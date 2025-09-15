from fastapi import APIRouter, Query
from models.schemas import MedlinePlusSummary
from services.medlineplus_service import summary
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["medlineplus"])


@router.get("/medlineplus/summary", response_model=MedlinePlusSummary)
def medlineplus_summary(topic: str = Query(..., description="Topic term")):
    data = summary(topic)
    return MedlinePlusSummary(
        banner=educational_banner(),
        topic=topic,
        summary=data.get("summary"),
        references=data.get("references", []),
    )
