"""
Disease Information Router - AI Nurse Florence
Following Router Organization pattern with comprehensive documentation
"""

from fastapi import APIRouter, Query, HTTPException, status
from typing import Optional
from pydantic import BaseModel, Field

from src.services import get_service
from src.models.schemas import BaseResponse

# Educational banner following coding instructions
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

router = APIRouter(
    prefix="/api/v1/disease",
    tags=["disease-information"],
    responses={
        404: {"description": "Disease not found"},
        500: {"description": "External service error"}
    }
)

class DiseaseResponse(BaseResponse):
    """Disease information response following API Design Standards."""
    banner: str = Field(default=EDU_BANNER, description="Educational disclaimer")
    query: str = Field(..., description="Original search query")
    disease_name: Optional[str] = Field(None, description="Disease name")
    description: Optional[str] = Field(None, description="Clinical description")
    symptoms: list[str] = Field(default_factory=list, description="Common symptoms")
    risk_factors: list[str] = Field(default_factory=list, description="Risk factors")
    references: list[str] = Field(default_factory=list, description="Medical references")

@router.get(
    "/lookup",
    response_model=DiseaseResponse,
    summary="Look up disease information",
    description="Get comprehensive disease information for clinical reference. Educational use only.",
    responses={
        200: {
            "description": "Disease information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": {
                            "banner": EDU_BANNER,
                            "query": "diabetes",
                            "disease_name": "Diabetes Mellitus",
                            "description": "Chronic metabolic disorder...",
                            "symptoms": ["Polyuria", "Polydipsia", "Weight loss"],
                            "risk_factors": ["Obesity", "Family history", "Age >45"]
                        }
                    }
                }
            }
        }
    }
)
async def lookup_disease(
    q: str = Query(
        ...,
        description="Disease name or medical term to search for",
        min_length=2,
        max_length=100,
        examples={
            "diabetes": {"summary": "Search for diabetes information"},
            "hypertension": {"summary": "Search for blood pressure disorders"},
            "pneumonia": {"summary": "Search for lung infection information"}
        }
    )
):
    """
    Look up comprehensive disease information.
    
    Following Service Layer Architecture pattern:
    - Uses service registry for dependency injection
    - Implements Conditional Imports Pattern for graceful degradation
    - Returns standardized responses with educational disclaimers
    """
    try:
        # Get service through registry (Conditional Imports Pattern)
        disease_service = get_service('disease')
        if not disease_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Disease information service temporarily unavailable"
            )
        
        # Call service layer
        result = await disease_service.lookup_disease(q)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No information found for: {q}"
            )
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving disease information: {str(e)}"
        )

@router.get(
    "/search",
    response_model=dict,
    summary="Search diseases by symptoms",
    description="Search for potential diseases based on symptom patterns. Educational use only."
)
async def search_by_symptoms(
    symptoms: str = Query(
        ...,
        description="Comma-separated list of symptoms",
        examples={
            "fever,cough,shortness of breath": {"summary": "Search by respiratory symptoms"},
            "fatigue,weight loss,excessive thirst": {"summary": "Search by metabolic symptoms"}
        }
    )
):
    """Search diseases by symptom patterns following Service Layer Architecture."""
    try:
        disease_service = get_service('disease')
        if not disease_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Disease search service temporarily unavailable"
            )
        
        # Parse symptoms
        symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
        
        result = await disease_service.search_by_symptoms(symptom_list)
        
        return {
            "success": True,
            "data": {
                "banner": EDU_BANNER,
                "symptoms_searched": symptom_list,
                "potential_diseases": result,
                "disclaimer": "Symptom matching is for educational reference only. Consult healthcare providers for diagnosis."
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching diseases: {str(e)}"
        )
