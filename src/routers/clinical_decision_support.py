"""
Clinical Decision Support Router - Core clinical endpoints
Following Service Layer Architecture
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Query, status

from src.services.clinical_decision_service import (
    ClinicalDecisionService,
    get_clinical_decision_service,
)
from src.services.risk_assessment_service import (
    RiskAssessmentService,
    get_risk_assessment_service,
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
):
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


@router.post("/risk-assessment/falls")
async def assess_falls_risk(
    patient_data: Dict[str, Any] = Body(
        ...,
        description="Patient data for Morse Falls Scale assessment",
        examples=[
            {
                "history_of_falling": "yes",
                "secondary_diagnosis": "yes",
                "ambulatory_aid": "crutches_cane_walker",
                "iv_heparin_lock": "no",
                "gait": "weak",
                "mental_status": "oriented",
                "assessment_date": "2025-10-07",
            }
        ],
    ),
    risk_service: RiskAssessmentService = Depends(get_risk_assessment_service),
):
    """
    Morse Falls Scale risk assessment

    Validated tool for falls risk. Scores range from 0-125.
    Based on peer-reviewed clinical research.
    """
    try:
        result = await risk_service.calculate_falls_risk(patient_data)
        return create_success_response(result)
    except Exception as e:
        return create_error_response(
            f"Falls risk assessment failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/risk-assessment/pressure-ulcer")
async def assess_pressure_ulcer_risk(
    patient_data: Dict[str, Any] = Body(
        ...,
        description="Patient data for Braden Scale assessment",
        examples=[
            {
                "sensory_perception": 3,
                "moisture": 2,
                "activity": 2,
                "mobility": 2,
                "nutrition": 3,
                "friction_shear": 2,
                "assessment_date": "2025-10-07",
            }
        ],
    ),
    risk_service: RiskAssessmentService = Depends(get_risk_assessment_service),
):
    """
    Braden Scale pressure ulcer/injury risk assessment

    Validated tool for pressure injury risk. Scores range from 6-23.
    Lower scores indicate higher risk.
    """
    try:
        result = await risk_service.calculate_pressure_ulcer_risk(patient_data)
        return create_success_response(result)
    except Exception as e:
        return create_error_response(
            f"Pressure ulcer risk assessment failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/risk-assessment/deterioration")
async def assess_deterioration_risk(
    vital_signs: Dict[str, Any] = Body(
        ...,
        description="Vital signs for MEWS calculation",
        examples=[
            {
                "systolic_bp": 110,
                "heart_rate": 95,
                "respiratory_rate": 18,
                "temperature": 37.2,
                "avpu": "alert",
                "assessment_time": "2025-10-07T08:30:00",
            }
        ],
    ),
    risk_service: RiskAssessmentService = Depends(get_risk_assessment_service),
):
    """
    Modified Early Warning Score (MEWS) for clinical deterioration

    Validated tool for detecting deterioration. Scores range from 0-14.
    Higher scores indicate increased risk.
    """
    try:
        result = await risk_service.calculate_deterioration_risk(vital_signs)
        return create_success_response(result)
    except Exception as e:
        return create_error_response(
            f"Deterioration risk assessment failed: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
