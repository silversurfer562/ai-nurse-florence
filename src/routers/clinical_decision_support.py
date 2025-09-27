"""
Clinical Decision Support Router - Core clinical endpoints
Following Service Layer Architecture
"""

from fastapi import APIRouter, Query, Depends, status, Path
from typing import List, Optional
from src.models.schemas import ClinicalDecisionRequest, ClinicalDecisionResponse
from src.services.clinical_decision_service import get_clinical_decision_service, ClinicalDecisionService
from src.utils.api_responses import create_success_response, create_error_response

router = APIRouter(
    prefix="/clinical-decision-support", 
    tags=["Clinical Decision Support"]
)

@router.post("/interventions", response_model=ClinicalDecisionResponse)
async def get_nursing_interventions(
    patient_condition: str = Query(..., 
        description="Patient condition or clinical presentation",
        examples=["acute heart failure", "COPD exacerbation", "post-operative care"]
    ),
    severity: str = Query("moderate", 
        description="Clinical severity level",
        enum=["mild", "moderate", "severe", "critical"]
    ),
    comorbidities: Optional[List[str]] = Query(None,
        description="Comorbid conditions",
        examples=["diabetes", "hypertension"]
    ),
    care_setting: str = Query("med-surg",
        description="Care setting context",
        enum=["ICU", "med-surg", "ED", "community", "cardiac", "orthopedic"]
    ),
    clinical_service: ClinicalDecisionService = Depends(get_clinical_decision_service)
):
    """
    Evidence-based nursing interventions endpoint
    Following API design standards from coding instructions
    """
    
    try:
        result = await clinical_service.get_nursing_interventions(
            patient_condition=patient_condition,
            severity=severity,
            comorbidities=comorbidities or []
        )
        
        return create_success_response(result)
        
    except Exception as e:
        return create_error_response(
            f"Clinical decision support failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get("/risk-assessment/{assessment_type}")
async def get_risk_assessment(
    assessment_type: str = Path(..., 
        description="Type of risk assessment",
        enum=["falls", "pressure_ulcer", "deterioration"]
    )
):
    """Risk assessment tools endpoint"""
    
    # TODO: Integrate with risk assessment service
    # TODO: Implement assessment-specific logic
    # TODO: Return structured risk scores
    
    return create_success_response({
        "assessment_type": assessment_type,
        "tools": f"TODO: Implement {assessment_type} risk assessment"
    })
