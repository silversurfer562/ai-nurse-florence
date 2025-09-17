# services/summarize_service.py
from typing import Any, Optional, Callable, Dict
import json
import re

from services.openai_client import get_client

__all__ = ["call_chatgpt", "sbar_from_notes"]

class ChatGPTError(RuntimeError):
    pass

def _extract_text(resp: Any) -> str:
    """
    Handle multiple response shapes:
    - tests: dict with "output_text"
    - OpenAI Responses API: object with .output_text
    - legacy/chat: choices[0].message.content
    - last resort: str(resp)
    """
    # test double shape
    if isinstance(resp, dict) and "output_text" in resp:
        return str(resp["output_text"])

    # responses API (python sdk) shape
    text = getattr(resp, "output_text", None)
    if text:
        return str(text)

    # legacy/chat-like shape
    choices = getattr(resp, "choices", None)
    if choices:
        first = choices[0] if choices else None
        message = getattr(first, "message", None) if first else None
        content = getattr(message, "content", None) if message else None
        if content:
            return str(content)

    # fall back to string
    return str(resp)

def call_chatgpt(
    prompt: str,
    *,
    model: str = "gpt-5.1-mini",
    **kwargs: Any,
) -> str:
    """
    Thin wrapper around OpenAI Responses API.
    Tests monkeypatch services.openai_client.get_client() to return a fake client
    exposing client.responses.create(model=..., input=...).
    """
    client = get_client()
    if not client:
        raise ChatGPTError("OpenAI client is not configured")

    resp = client.responses.create(model=model, input=prompt, **kwargs)
    return _extract_text(resp)

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
    model: str = "gpt-5.1-mini",
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
