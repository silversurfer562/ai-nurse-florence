from fastapi import APIRouter, Query
from typing import Optional
import services.trials_service as trials_service
from utils.guardrails import educational_banner
from utils.api_responses import create_success_response

# No version prefix here; app.py will expose under /v1 for legacy routes
router = APIRouter(prefix="", tags=["clinicaltrials"])


@router.get("/clinicaltrials/search")
def clinical_trials(
    condition: str = Query(...),
    status: Optional[str] = Query(None, pattern="^(recruiting|active|completed)$"),
    max_results: int = Query(10, ge=1, le=50),
) -> dict:
    raw = trials_service.search_trials(condition=condition, status=status, max_results=max_results)
    # tolerate both list and dict return shapes
    items = raw if isinstance(raw, list) else raw.get("results", [])
    # Convert to simple dicts for the response
    results = [
        {
            "nct_id": r.get("nct_id"),
            "title": r.get("title"),
            "status": r.get("status"),
            "conditions": r.get("conditions") or [],
            "locations": r.get("locations") or [],
            "url": r.get("url"),
        }
        for r in items
    ]
    # Return a flat success response so callers get top-level keys expected by
    # legacy integrations/tests.
    from utils.api_responses import create_success_response_flat
    return create_success_response_flat({
        "banner": educational_banner(),
        "condition": condition,
        "status": status,
        "results": results,
    })
