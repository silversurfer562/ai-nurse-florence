from services.summarize_service import summarize_text

def test_sbar_from_empty_notes_returns_expected_keys():
    sbar = summarize_text("")
    assert isinstance(sbar, dict)
    for key in ("situation", "background", "assessment", "recommendation"):
        assert key in sbar

def test_sbar_from_sample_note_contains_content():
    note = "Pt is a 65yo M with chest pain. Hx HTN. Vitals stable. Recommend ECG and cardiology consult."
    sbar = summarize_text(note)
    assert isinstance(sbar, dict)
    assert any(bool(sbar.get(k)) for k in ("situation", "background", "assessment", "recommendation"))