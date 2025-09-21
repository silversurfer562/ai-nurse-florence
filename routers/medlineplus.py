from fastapi import APIRouter, Query
import services.medlineplus_service as medlineplus_service
from utils.guardrails import educational_banner
from utils.api_responses import create_success_response_flat

# Use no version prefix here; app.py exposes this router under /v1 as needed.
router = APIRouter(prefix="", tags=["medlineplus"])


@router.get("/medlineplus/summary")
def medlineplus_summary(topic: str = Query(..., description="Topic term")):
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
    data = medlineplus_service.get_medlineplus_summary(topic)
    return create_success_response_flat({
        "banner": educational_banner(),
        "topic": topic,
        "summary": data.get("summary"),
        "references": data.get("references", []),
    })
