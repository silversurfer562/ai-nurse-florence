from fastapi import APIRouter
from models.schemas import ReadabilityRequest, ReadabilityResponse
from services.readability_service import analyze_readability
from utils.guardrails import educational_banner

router = APIRouter(prefix="/readability", tags=["readability"])
example = {
    "banner": "Draft for clinician review — not medical advice. No PHI stored.",
    "flesch_reading_ease": 72.3,
    "flesch_kincaid_grade": 6.8,
    "sentences": 3,
    "words": 35,
    "syllables": 48,
    "suggestions": ["Shorten long sentences"],
}


@router.post(
    "/check",
    response_model=ReadabilityResponse,
    responses={200: {"content": {"application/json": {"example": example}}}},
)
def readability_check(payload: ReadabilityRequest):
    m = analyze_readability(payload.text or "")
    return ReadabilityResponse(banner=educational_banner(), **m)
