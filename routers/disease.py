from fastapi import APIRouter, Query, status
from models.schemas import DiseaseSummary
from services.disease_service import lookup_disease
from utils.guardrails import educational_banner
from utils.api_responses import create_success_response, create_error_response

router = APIRouter(prefix="/disease", tags=["disease"])
example = {
    "banner": "Draft for clinician review — not medical advice. No PHI stored.",
    "query": "cancer",
    "name": "Cancer",
    "summary": "Cancer is a group of diseases with abnormal cell growth and potential spread.",
    "references": [],
}

@router.get(
    "/",
    response_model=DiseaseSummary,
    responses={200: {"content": {"application/json": {"example": example}}}},
    summary="Get disease information",
    description="""
    Retrieve information about a disease or medical condition.
    
    This endpoint provides a summary of a specified disease or condition,
    including key information and references where available.
    
    The response includes:
    - The original query term
    - The disease name (may be normalized or corrected)
    - A detailed summary of the disease
    - References to medical literature (when available)
    
    Example queries:
    - diabetes
    - hypertension
    - multiple sclerosis
    - alzheimer's disease
    """
)
def disease_lookup(
    q: str = Query(
        ..., 
        description="Disease term or ID",
        examples={
            "diabetes": {"summary": "Search for information about diabetes"},
            "alzheimer": {"summary": "Search for information about Alzheimer's disease"},
            "copd": {"summary": "Search for information about COPD"}
        }
    )
):
    """
    Lookup information about a disease or medical condition.
    
    Args:
        q: The disease term or identifier to search for
        
    Returns:
        A DiseaseSummary object containing name, summary, and references
        
    Examples:
        /api/v1/disease?q=diabetes
        /api/v1/disease?q=asthma
    """
    result = lookup_disease(q)
    
    # If clarification is needed, return a standardized error response
    if result.get("needs_clarification"):
        return create_error_response(
            message="The search query is too vague. Please provide more details.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="clarification_needed",
            details={
                "clarification_question": result["clarification_question"],
                "original_query": result["query"]
            }
        )
    
    # Add educational banner if missing
    if not result.get("banner"):
        result["banner"] = educational_banner
        
    # Add HATEOAS link to the advanced search wizard
    links = {
        "advanced_search": f"/api/v1/wizards/disease-search/start?topic={q}"
    }
    
    return create_success_response(result, links=links)
