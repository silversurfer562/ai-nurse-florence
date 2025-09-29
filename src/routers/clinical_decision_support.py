"""
Clinical Decision Support Router - Core clinical endpoints
Following Service Layer Architecture
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from src.services.clinical_decision_service import (
    ClinicalDecisionService,
    get_clinical_decision_service,
)
from src.utils.api_responses import create_error_response, create_success_response

router = APIRouter(
    prefix="/clinical-decision-support", tags=["Clinical Decision Support"]
)


@router.post("/interventions", response_model=dict)
async def get_nursing_interventions(
    patient_condition: str = Query(
        ...,
        description="Patient condition or clinical presentation",
        examples=["acute heart failure", "COPD exacerbation", "post-operative care"],
    ),
    severity: str = Query(
        "moderate",
        description="Clinical severity level",
        enum=["mild", "moderate", "severe", "critical"],
    ),
    comorbidities: Optional[List[str]] = Query(
        None, description="Comorbid conditions", examples=["diabetes", "hypertension"]
    ),
    care_setting: str = Query(
        "med-surg",
        description="Care setting context",
        enum=["ICU", "med-surg", "ED", "community", "cardiac", "orthopedic"],
    ),
    clinical_service: ClinicalDecisionService = Depends(get_clinical_decision_service),
) -> Dict[str, Any]:
    """
    Evidence-based nursing interventions endpoint
    Following API design standards from coding instructions
    """

    try:
        result = await clinical_service.get_nursing_interventions(
            patient_condition=patient_condition,
            severity=severity,
            comorbidities=comorbidities or [],
        )

        # Return a standardized success wrapper (used across the API)
        return create_success_response(result)

    except Exception as e:
        return create_error_response(
            f"Clinical decision support failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get("/risk-assessment/{assessment_type}")
async def get_risk_assessment(
    assessment_type: str = Path(
        ...,
        description="Type of risk assessment",
        enum=["falls", "pressure_ulcer", "deterioration"],
    ),
) -> Dict[str, Any]:
    """Risk assessment tools endpoint"""

    # TODO: Integrate with risk assessment service
    # TODO: Implement assessment-specific logic
    # TODO: Return structured risk scores

    return create_success_response(
        {
            "assessment_type": assessment_type,
            "tools": f"TODO: Implement {assessment_type} risk assessment",
        }
    )
