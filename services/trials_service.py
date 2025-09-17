import os
from typing import Dict, Any, List, Optional

LIVE = str(os.getenv("USE_LIVE", "0")).lower() in {"1", "true", "yes", "on"}

trials_live = None
if LIVE:
    try:
        import live_clinicaltrials as trials_live
    except Exception:
        trials_live = None

def search_trials(condition: str, status: Optional[str] = None, max_results: int = 10) -> Dict[str, Any]:
    banner = "Draft for clinician review — not medical advice. No PHI stored."
    if LIVE and trials_live and hasattr(trials_live, "search"):
        try:
            results: List[Dict[str, Any]] = trials_live.search(condition=condition, status=status, max_results=max_results)
            return {"banner": banner, "condition": condition, "status": status, "results": results}
        except Exception:
            pass
    return {
        "banner": banner,
        "condition": condition,
        "status": status,
        "results": [
            {
                "nct_id": None,
                "title": f"Stub trial for '{condition}'",
                "status": status,
                "conditions": [condition],
                "locations": [],
                "url": None,
            }
            for _ in range(max_results)
        ],
    }
