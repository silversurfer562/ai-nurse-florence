from fastapi import APIRouter, Query
from typing import Optional
from models.schemas import ClinicalTrialsResponse, ClinicalTrial
from services.trials_service import search
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["clinicaltrials"])


@router.get("/clinicaltrials/search", response_model=ClinicalTrialsResponse)
def clinical_trials(
    condition: str = Query(...),
    status: Optional[str] = Query(None, pattern="^(recruiting|active|completed)$"),
    max_results: int = Query(10, ge=1, le=50),
):
    raw = search(condition=condition, status=status, max_results=max_results)
    results = [
        ClinicalTrial(
            nct_id=r.get("nct_id"),
            title=r.get("title"),
            status=r.get("status"),
            conditions=r.get("conditions") or [],
            locations=r.get("locations") or [],
            url=r.get("url"),
        )
        for r in raw.get("results", [])
    ]
    return ClinicalTrialsResponse(
        banner=educational_banner(), condition=condition, status=status, results=results
    )
