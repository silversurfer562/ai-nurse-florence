from typing import List, Dict, Any, Optional

try:
    import live_clinicaltrials as trials_live
except Exception:
    trials_live = None
try:
    import clinicaltrials as trials_mod
except Exception:
    trials_mod = None


def search_trials(
    condition: str, status: Optional[str] = None, max_results: int = 10
) -> List[Dict[str, Any]]:
    if trials_live and hasattr(trials_live, "search"):
        try:
            return trials_live.search(
                condition=condition, status=status, max_results=max_results
            )
        except Exception:
            pass
    if trials_mod and hasattr(trials_mod, "search"):
        try:
            return trials_mod.search(
                condition=condition, status=status, max_results=max_results
            )
        except Exception:
            pass
    return [
        {
            "nct_id": None,
            "title": f"Stub trial for '{condition}'",
            "status": status or "unknown",
            "conditions": [condition],
            "locations": [],
            "url": None,
        }
        for _ in range(min(max_results, 3))
    ]
