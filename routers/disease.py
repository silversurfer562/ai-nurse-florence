from fastapi import APIRouter, Query
from models.schemas import DiseaseSummary
from services.disease_service import lookup
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["disease"])
example = {
    "banner": "Draft for clinician review — not medical advice. No PHI stored.",
    "query": "cancer",
    "name": "Cancer",
    "summary": "Cancer is a group of diseases with abnormal cell growth and potential spread.",
    "references": [],
}


@router.get(
    "/disease",
    response_model=DiseaseSummary,
    responses={200: {"content": {"application/json": {"example": example}}}},
)
def disease_lookup(q: str = Query(..., description="Disease term or ID")):
    data = lookup(q)
    return DiseaseSummary(
        banner=educational_banner(),
        query=q,
        name=data.get("name"),
        summary=data.get("summary"),
        references=data.get("references", []),
    )
