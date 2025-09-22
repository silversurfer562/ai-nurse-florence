def make_patient_education(topic: str, level: int = 7, lang: str = "en"):
    t = topic.strip().title()
    what = f"{t} is a health condition. This handout explains it in simple terms."
    why = f"Understanding {t} helps you notice changes early and talk with your care team."
    red = [
        "Trouble breathing or speaking full sentences",
        "New confusion, fainting, or chest pressure",
        "Sudden, severe, or unusual symptoms",
    ]
    care = [
        "Follow your care team's instructions and ask questions when unsure",
        "Keep a simple log of symptoms and any changes you notice",
        "Know your red-flag symptoms and when to seek help",
    ]
    seek = [
        "Call your local emergency number for severe or sudden symptoms",
        "Contact your clinic for non-urgent questions or if symptoms slowly worsen",
    ]
    return {
        "topic": t,
        "level": level,
        "lang": lang,
        "what_it_is": what,
        "why_it_matters": why,
        "red_flags": red,
        "self_care": care,
        "when_to_seek_help": seek,
        "references": [],
    }
