import os
from typing import Dict, Any

LIVE = str(os.getenv("USE_LIVE", "0")).lower() in {"1", "true", "yes", "on"}

mydisease_live = None
if LIVE:
    try:
        import live_mydisease as mydisease_live
    except Exception:
        mydisease_live = None

def lookup(term: str) -> Dict[str, Any]:
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    if LIVE and mydisease_live and hasattr(mydisease_live, "lookup"):
        try:
            data: Dict[str, Any] = mydisease_live.lookup(term)
            data.setdefault("banner", banner)
            data.setdefault("query", term)
            data.setdefault("references", [])
            if "name" not in data:
                data["name"] = term.title() if term else None
            return data
        except Exception:
            pass
    return {
        "banner": banner,
        "query": term,
        "name": term.title() if term else None,
        "summary": f"No live connector found. Placeholder for '{term}'.",
        "references": [],
    }
