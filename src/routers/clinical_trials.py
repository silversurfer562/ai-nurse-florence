"""
Clinical Trials Router - AI Nurse Florence
Following External Service Integration and API Design Standards from coding instructions
"""

from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from ..services.clinical_trials_service import search_clinical_trials
from ..utils.config import get_educational_banner

router = APIRouter(
    prefix="/clinical-trials",
    tags=["medical-information", "clinical-trials"],
    responses={
        200: {"description": "Clinical trials search completed successfully"},
        422: {"description": "Query needs clarification"},
        500: {"description": "External service error"}
    }
)

class ClinicalTrialsResponse(BaseModel):
    banner: str = Field(default_factory=get_educational_banner)
    query: str
    condition: Optional[str] = None
    total_studies: Optional[int] = None
    studies_summary: Optional[str] = None
    trials: Optional[List[Dict[str, Any]]] = None
    sources: Optional[List[str]] = None
    needs_clarification: Optional[bool] = False

@router.get("/search", response_model=ClinicalTrialsResponse)
async def search_trials(
    condition: Optional[str] = Query(None,
                          description="Medical condition for clinical trials search",
                          examples=["diabetes", "hypertension", "cancer treatment"]),
    q: Optional[str] = Query(None, description="Alias for condition"),
    status_filter: Optional[str] = Query(None, alias="status", description="Trial status filter (RECRUITING, ACTIVE_NOT_RECRUITING, COMPLETED, etc.)"),
    max_studies: int = Query(10, ge=1, le=50, description="Maximum number of studies to return")
):
    # Support 'q' query param as an alias for condition for backward compatibility
    if not condition and q:
        condition = q
    if not condition:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Missing required query parameter 'condition' or 'q'")
    """
    Search clinical trials following External Service Integration pattern.

    Searches ClinicalTrials.gov for ongoing and completed clinical studies.
    All responses include educational disclaimers per API Design Standards.
    """
    try:
        result = await search_clinical_trials(condition, max_studies=max_studies, status=status_filter)
        
        if result.get("needs_clarification"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query needs clarification",
                    "clarification_question": result.get("clarification_question"),
                    "banner": get_educational_banner()
                }
            )
        
        return ClinicalTrialsResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical trials search failed: {str(e)}"
        )
