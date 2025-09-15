import pytest
from services.readability_service import analyze

def test_analyze_returns_dict_for_empty_text():
    out = analyze("")
    assert isinstance(out, dict)

def test_analyze_handles_simple_text():
    out = analyze("This is a short sentence.")
    assert isinstance(out, dict)
    # if implementation exposes a numeric score, ensure a numeric type
    if "score" in out:
        assert isinstance(out["score"], (int, float))

@pytest.mark.parametrize(
    "text",
    [
        "Short.",
        "This is a longer sentence with clauses and punctuation to affect readability metrics."
    ],
)
def test_analyze_varied_texts(text):
    out = analyze(text)
    assert isinstance(out, dict)