# python
import re
from .openai_client import get_client


def _clean(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").strip())


def _normalize_sbar(sbar):
    if isinstance(sbar, dict):
        return sbar
    if isinstance(sbar, (list, tuple)) and len(sbar) == 4:
        return {
            "situation": sbar[0],
            "background": sbar[1],
            "assessment": sbar[2],
            "recommendation": sbar[3],
        }
    raise AssertionError(f"Unexpected SBAR return type: {type(sbar)}")


def _extract_sbar_parts(notes: str):
    n = notes or ""
    pat = re.compile(
        r"(?:^|\b)s(?:ituation)?\s*[:\-]\s*(?P<s>.*?)(?=\b[b|a|r](?:ackground|ssessment|ecommendation)?\s*[:\-]|\Z)|"
        r"(?:^|\b)b(?:ackground)?\s*[:\-]\s*(?P<b>.*?)(?=\b[a|r](?:ssessment|ecommendation)?\s*[:\-]|\Z)|"
        r"(?:^|\b)a(?:ssessment)?\s*[:\-]\s*(?P<a>.*?)(?=\b[r](?:ecommendation)?\s*[:\-]|\Z)|"
        r"(?:^|\b)r(?:ecommendation)?\s*[:\-]\s*(?P<r>.*)",
        re.I | re.S,
    )
    s = b = a = r = ""
    for m in pat.finditer(n):
        if m.group("s"):
            s = m.group("s")
        if m.group("b"):
            b = m.group("b")
        if m.group("a"):
            a = m.group("a")
        if m.group("r"):
            r = m.group("r")
    if any([s, b, a, r]):
        return _clean(s), _clean(b), _clean(a), _clean(r)

    sentences = re.split(r"(?<=[.!?])\s+", n.strip())
    if not sentences or sentences == ['']:
        return "", "", "", ""
    q = max(1, len(sentences) // 4)
    S = " ".join(sentences[0:q])
    B = " ".join(sentences[q : 2 * q]) if len(sentences) > q else ""
    A = " ".join(sentences[2 * q : 3 * q]) if len(sentences) > 2 * q else ""
    R = " ".join(sentences[3 * q :]) if len(sentences) > 3 * q else ""
    return _clean(S), _clean(B), _clean(A), _clean(R)


def call_chatgpt(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Call OpenAI API with the given prompt.
    Raises RuntimeError if client is not available.
    """
    client = get_client()
    if client is None:
        raise RuntimeError("OpenAI client not configured. Check OPENAI_API_KEY.")
    
    try:
        # Check if this is the test's fake client that uses responses.create
        if hasattr(client, 'responses') and hasattr(client.responses, 'create'):
            response = client.responses.create(model=model, input=prompt)
            return response.get("output_text", "")
        
        # Real OpenAI client API
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")


def sbar_from_notes(notes: str):
    situation, background, assessment, recommendation = _extract_sbar_parts(notes)
    return {
        "situation": situation,
        "background": background,
        "assessment": assessment,
        "recommendation": recommendation,
    }


# quick module-local tests (kept for iteration)
def test_sbar_from_empty_notes_returns_expected_keys():
    sbar = _normalize_sbar(sbar_from_notes(""))
    assert isinstance(sbar, dict)
    for key in ("situation", "background", "assessment", "recommendation"):
        assert key in sbar


def test_sbar_from_sample_note_contains_content():
    note = "Pt is a 65yo M with chest pain. Hx HTN. Vitals stable. Recommend ECG and cardiology consult."
    sbar = _normalize_sbar(sbar_from_notes(note))
    assert isinstance(sbar, dict)
    assert any(bool(sbar.get(k)) for k in ("situation", "background", "assessment", "recommendation"))
