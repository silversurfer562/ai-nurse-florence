from fastapi import APIRouter, Query
from models.schemas import MedlinePlusSummary
from services.medlineplus_service import get_medlineplus_summary
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["medlineplus"])


@router.get("/medlineplus/summary", response_model=MedlinePlusSummary)
def medlineplus_summary(topic: str = Query(..., description="Topic term")) -> MedlinePlusSummary:
    """
    Retrieve a summary from MedlinePlus for a given health topic.
    
    Args:
        topic: The health topic to search for
        
    Returns:
        A MedlinePlusSummary object containing the topic summary and references
        
    Examples:
        /v1/medlineplus/summary?topic=diabetes
        /v1/medlineplus/summary?topic=hypertension
    """
    data = get_medlineplus_summary(topic)
    return MedlinePlusSummary(
        banner=educational_banner(),
        topic=topic,
        summary=data.get("summary"),
        references=data.get("references", []),
    )
