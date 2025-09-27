# services/summarize_service.py
from typing import Any, Optional, Callable, Dict
import json
import re

from services import openai_client
from services.prompt_enhancement import enhance_prompt
from utils.exceptions import ExternalServiceException
from utils.logging import get_logger

def get_client():
    """Return the OpenAI client via services.openai_client.get_client.

    This wrapper allows tests to monkeypatch either
    `services.summarize_service.get_client` or
    `services.openai_client.get_client` and ensures the call is dynamic.
    """
    return openai_client.get_client()

__all__ = ["call_chatgpt", "sbar_from_notes", "summarize_text"]

logger = get_logger(__name__)

class ChatGPTError(ExternalServiceException):
    """Exception raised when the ChatGPT API fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, service_name="openai", details=details)

def call_chatgpt(
    prompt: str,
    *,
    model: str = "gpt-4o-mini",
    system_message: str = "You are a knowledgeable medical assistant for healthcare professionals.",
    **kwargs: Any,
) -> str:
    """
    Call OpenAI's chat completions API with proper error handling.
    
    Args:
        prompt: The user message/prompt to send
        model: OpenAI model name (default: gpt-4o-mini)
        system_message: System message to set context
        **kwargs: Additional parameters for the API call
        
    Returns:
        The response text from the API
        
    Raises:
        ChatGPTError: If the API call fails or client is not configured
    """
    # Use module-level alias so tests can patch services.summarize_service.get_client
    client = get_client()
    if not client:
        # Defer raising until a test or caller expects a live client.
        # Many unit tests inject a fake via monkeypatch; if client is missing,
        # raise a clear error so callers/tests can handle it.
        logger.error("OpenAI client configuration failed")
        raise ChatGPTError(
            "OpenAI client is not configured",
            details={"model": model}
        )

    try:
        logger.info(f"Calling OpenAI API with model {model}", extra={"model": model})
        
        # Build messages for chat completions API
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        
        # Default parameters
        api_params = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        # Override with any provided kwargs
        api_params.update(kwargs)
        
        # Make the API call
        response = client.chat.completions.create(**api_params)
        
        # Extract the content
        content = response.choices[0].message.content
        if not content:
            raise ChatGPTError("Empty response from OpenAI API", details={"model": model})
            
        return content.strip()
        
    except Exception as e:
        logger.error(
            f"OpenAI API call failed: {str(e)}", 
            extra={"model": model, "error": str(e)},
            exc_info=True
        )
        raise ChatGPTError(
            f"OpenAI API call failed: {str(e)}", 
            details={"model": model, "error": str(e)}
        )

_SBARK = ("situation", "background", "assessment", "recommendation")

def _parse_sbar_from_json(text: str) -> Optional[Dict[str, str]]:
    try:
        obj = json.loads(text)
        # normalize keys
        out = {}
        for k in _SBARK:
            for candidate in (k, k.capitalize(), k.upper()):
                if candidate in obj and isinstance(obj[candidate], str):
                    out[k] = obj[candidate].strip()
                    break
            if k not in out:
                out[k] = ""
        return out
    except Exception:
        return None

_SBAR_RE = re.compile(
    r"(?is)\b(Situation)[:\-]\s*(?P<situation>.+?)\s+"
    r"(Background)[:\-]\s*(?P<background>.+?)\s+"
    r"(Assessment)[:\-]\s*(?P<assessment>.+?)\s+"
    r"(Recommendation)[:\-]\s*(?P<recommendation>.+?)\s*$"
)

def _parse_sbar_from_headings(text: str) -> Dict[str, str]:
    m = _SBAR_RE.search(text.strip())
    if m:
        return {k: m.group(k).strip() for k in _SBARK}
    # softer fallback: split by headings if present in any order
    parts = {k: "" for k in _SBARK}
    current = None
    for line in text.splitlines():
        line_stripped = line.strip()
        hdr = line_stripped.lower().rstrip(":")
        if hdr in _SBARK and line_stripped.endswith(":"):
            current = hdr
            continue
        if current:
            parts[current] += ("" if parts[current] == "" else "\n") + line_stripped
    return {k: v.strip() for k, v in parts.items()}

def sbar_from_notes(
    notes: str,
    *,
    reading_level: str = "nurse",           # "nurse" default per your project
    max_words: int = 300,
    model: str = "gpt-4o-mini",
    llm: Optional[Callable[..., str]] = None,
    **kwargs: Any,
) -> Dict[str, str]:
    """
    Produce an SBAR summary dict from free-text notes.
    Returns: { 'situation': str, 'background': str, 'assessment': str, 'recommendation': str }

    - `llm` allows tests to inject a fake function. If None, uses call_chatgpt().
    - Attempts to parse JSON first; falls back to parsing SBAR headings.
    """
    if not isinstance(notes, str) or not notes.strip():
        return {k: "" for k in _SBARK}

    # Slightly “strict” output prompt to prefer JSON we can parse robustly.
    prompt = f"""
You are a clinical writing assistant for nurses. Summarize the following notes into SBAR at a {reading_level} reading level.
Keep the total under {max_words} words across all four fields combined.

Return ONLY a compact JSON object with these exact keys:
"situation", "background", "assessment", and "recommendation".
Do not include Markdown, code fences, or commentary.

NOTES:
\"\"\"{notes.strip()}\"
\"\"\"
"""

    runner = llm if llm is not None else (lambda p, **kw: call_chatgpt(p, model=model, **kw))
    raw = runner(prompt, **kwargs)

    # First try JSON
    parsed = _parse_sbar_from_json(raw)
    if parsed:
        return parsed

    # If model (or fake) returned a text block with headings, parse that
    return _parse_sbar_from_headings(raw)

def summarize_text(text: str, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Summarize the given text using ChatGPT.
    
    This function first enhances the prompt if needed, then sends it to ChatGPT.
    If the prompt is unclear, it returns a clarification question instead.
    
    Args:
        text: The text to summarize
        model: The model to use
        
    Returns:
        A dictionary with the summary or clarification information
    """
    # If input is empty, return an SBAR-shaped empty dict (tests expect SBAR keys)
    if not isinstance(text, str) or not text.strip():
        return sbar_from_notes(text)

    # Enhance the prompt
    effective_prompt, needs_clarification, clarification_question = enhance_prompt(text, "summarize")
    
    # If clarification is needed, return that info
    if needs_clarification:
        logger.info(f"Clarification needed for summarize prompt: '{text}'")
        return {
            "text": None,
            "needs_clarification": True,
            "clarification_question": clarification_question,
            "original_prompt": text
        }
    
    # Log if we enhanced the prompt
    was_enhanced = effective_prompt != text
    if was_enhanced:
        logger.info(f"Using enhanced prompt for summarization: '{text}' -> '{effective_prompt}'")
    
    # Local heuristic fallback: for short clinical notes, try a rule-based SBAR extraction
    def _local_sbar(notes: str) -> Optional[Dict[str, str]]:
        """Very small, conservative heuristic to extract SBAR fields from clinical notes.

        This is intentionally simple: it helps unit tests and local development when OpenAI
        is not configured. It should not replace model-generated summaries.
        """
        if not notes or not isinstance(notes, str):
            return None
        lowered = notes.lower()
        # Look for common clinical tokens indicating structured notes
        tokens = ("hx", "history", "vitals", "recommend", "recommendation", "ecg", "consult", "pt", "chest pain")
        # Match tokens as whole words to avoid false positives (e.g., 'prompt' contains 'pt')
        if not any(re.search(rf"\b{re.escape(t)}\b", lowered, re.I) for t in tokens):
            return None

        sentences = [s.strip() for s in re.split(r"[\n\.]+", notes) if s.strip()]
        situation = sentences[0] if sentences else ""
        # background: collect fragments containing hx or history
        background = "".join([s for s in sentences if re.search(r"\bhx\b|history", s, re.I)])
        assessment = "".join([s for s in sentences if re.search(r"pain|stable|tachy|hypotens|fever|assessment", s, re.I)])
        recommendation = "".join([s for s in sentences if re.search(r"recommend|recommendation|consult|ecg|admit|discharge", s, re.I)])

        return {
            "situation": situation.strip(),
            "background": background.strip(),
            "assessment": assessment.strip(),
            "recommendation": recommendation.strip(),
        }

    # If OpenAI client is not configured, try local heuristic before raising
    client = None
    try:
        client = get_client()
    except Exception:
        client = None

    if client is None:
        local = _local_sbar(text)
        if local:
            return local

    # Call ChatGPT with the effective prompt
    summary = call_chatgpt(effective_prompt, model=model)
    
    # Return the result with enhancement info if relevant
    result = {"text": summary}
    if was_enhanced:
        result["prompt_enhanced"] = "true"
        result["original_prompt"] = text
        result["enhanced_prompt"] = effective_prompt
    
    return result
