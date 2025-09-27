"""
Clinical Trials Router - AI Nurse Florence
Following Router Organization pattern with ClinicalTrials.gov integration
"""

from fastapi import APIRouter, Query, Path, HTTPException, status
from typing import Optional, List
from pydantic import BaseModel, Field

from src.services import get_service
from src.models.schemas import BaseResponse

# Educational banner following coding instructions
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

router = APIRouter(
    prefix="/api/v1/clinical-trials",
    tags=["clinical-trials"],
    responses={
        404: {"description": "No trials found"},
        503: {"description": "Clinical trials service unavailable"}
    }
)

class ClinicalTrialsResponse(BaseResponse):
    """Clinical trials response following API Design Standards."""
    banner: str = Field(default=EDU_BANNER)
    query: str = Field(..., description="Search query")
    trials: List[dict] = Field(default_factory=list, description="Clinical trials")
    total_results: int = Field(default=0, description="Total trials available")

@router.get(
    "/search",
    response_model=ClinicalTrialsResponse,
    summary="Search clinical trials",
    description="Search ClinicalTrials.gov for relevant studies. Educational use only.",
    responses={
        200: {
            "description": "Clinical trials search completed successfully"
        },
        503: {
            "description": "Clinical trials service temporarily unavailable"
        }
    }
)
async def search_clinical_trials(
    q: str = Query(
        ...,
        description="Medical condition or intervention to search for",
        min_length=2,
        max_length=200,
        examples={
            "diabetes": {"summary": "Search diabetes-related trials"},
            "hypertension": {"summary": "Search blood pressure trials"},
            "nursing intervention": {"summary": "Search nursing care studies"}
        }
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of trials to return"
    )
):
    """
    Search clinical trials through ClinicalTrials.gov.
    
    Following Service Layer Architecture with Conditional Imports Pattern:
    - Service may be unavailable (graceful degradation)
    - Educational disclaimers included
    - Standardized error responses
    """
    try:
        # Get service through registry (Conditional Imports Pattern)
        trials_service = get_service('clinical_trials')
        if not trials_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Clinical trials service temporarily unavailable. This service requires additional dependencies."
            )
        
        # Call service layer
        result = await trials_service.search_trials(q, limit=limit)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching clinical trials: {str(e)}"
        )

@router.get(
    "/trial/{nct_id}",
    response_model=dict,
    summary="Get trial details",
    description="Retrieve detailed information for a specific clinical trial."
)
async def get_trial_details(
    nct_id: str = Path(
        ...,
        description="NCT ID of the clinical trial (e.g., NCT12345678)",
        pattern="^NCT[0-9]{8}$",
        examples=["NCT12345678", "NCT87654321"]
    )
):
    """Get detailed trial information by NCT ID following API Design Standards."""
    try:
        trials_service = get_service('clinical_trials')
        if not trials_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Clinical trials service temporarily unavailable"
            )
        
        result = await trials_service.get_trial_details(nct_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trial not found: {nct_id}"
            )
        
        return {
            "success": True,
            "data": {
                "banner": EDU_BANNER,
                **result
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving trial details: {str(e)}"
        )
