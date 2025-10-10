"""
Wizard AI API Router
Provides AI-powered assistance endpoints for clinical wizards using LangChain
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.services.wizard_ai_service import WizardAIService, get_wizard_ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/wizard-ai", tags=["Wizard AI"])


# Request/Response models
class PatientContext(BaseModel):
    """Patient context for AI suggestions"""

    patient_id: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    chief_complaint: Optional[str] = None
    medical_history: Optional[List[str]] = []
    medications: Optional[List[str]] = []
    allergies: Optional[List[str]] = []


class SepsisAssessmentRequest(BaseModel):
    """Request for sepsis assessment AI suggestions"""

    patient_context: PatientContext
    current_vitals: Optional[Dict[str, Any]] = {}
    recent_labs: Optional[Dict[str, Any]] = {}


class StrokeAssessmentRequest(BaseModel):
    """Request for stroke assessment AI suggestions"""

    patient_context: PatientContext
    symptom_onset_time: str
    current_symptoms: Dict[str, Any]


class CardiacAssessmentRequest(BaseModel):
    """Request for cardiac assessment AI suggestions"""

    patient_context: PatientContext
    chest_pain_characteristics: Dict[str, Any]
    vital_signs: Dict[str, Any]


class WizardFieldSuggestionRequest(BaseModel):
    """Request for single field suggestion"""

    wizard_type: str = Field(
        ..., description="Type of wizard (sepsis, stroke, cardiac, etc.)"
    )
    field_name: str = Field(..., description="Name of the field needing suggestion")
    patient_context: PatientContext
    current_wizard_data: Dict[str, Any] = Field(default_factory=dict)


@router.post("/sepsis/suggest")
async def suggest_sepsis_assessment(
    request: SepsisAssessmentRequest,
    service: WizardAIService = Depends(get_wizard_ai_service),
):
    """
    Get AI-powered suggestions for sepsis screening wizard

    Returns structured suggestions including:
    - Suspected infection source
    - Risk factors
    - qSOFA score predictions
    - Recommended interventions
    """
    try:
        result = await service.suggest_sepsis_assessment(
            patient_context=request.patient_context.dict(),
            current_vitals=request.current_vitals,
            recent_labs=request.recent_labs,
        )

        return {
            "success": True,
            "suggestions": result.dict(),
        }

    except Exception as e:
        logger.error(f"Error in sepsis assessment endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stroke/suggest")
async def suggest_stroke_assessment(
    request: StrokeAssessmentRequest,
    service: WizardAIService = Depends(get_wizard_ai_service),
):
    """
    Get AI-powered suggestions for stroke assessment wizard

    Returns structured suggestions including:
    - Cincinnati Stroke Scale findings
    - NIHSS predictions
    - tPA eligibility assessment
    - Time-critical actions
    """
    try:
        result = await service.suggest_stroke_assessment(
            patient_context=request.patient_context.dict(),
            symptom_onset_time=request.symptom_onset_time,
            current_symptoms=request.current_symptoms,
        )

        return {
            "success": True,
            "suggestions": result.dict(),
        }

    except Exception as e:
        logger.error(f"Error in stroke assessment endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cardiac/suggest")
async def suggest_cardiac_assessment(
    request: CardiacAssessmentRequest,
    service: WizardAIService = Depends(get_wizard_ai_service),
):
    """
    Get AI-powered suggestions for cardiac assessment wizard

    Returns structured suggestions including:
    - HEART score component predictions
    - ECG findings
    - STEMI alert
    - Recommended interventions
    - Disposition recommendation
    """
    try:
        result = await service.suggest_cardiac_assessment(
            patient_context=request.patient_context.dict(),
            chest_pain_characteristics=request.chest_pain_characteristics,
            vital_signs=request.vital_signs,
        )

        return {
            "success": True,
            "suggestions": result.dict(),
        }

    except Exception as e:
        logger.error(f"Error in cardiac assessment endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/field/suggest")
async def suggest_wizard_field(
    request: WizardFieldSuggestionRequest,
    service: WizardAIService = Depends(get_wizard_ai_service),
):
    """
    Get AI suggestion for a specific wizard field

    Returns:
    - suggested_value: The AI's suggested value for the field
    - reasoning: Brief clinical reasoning for the suggestion
    """
    try:
        result = await service.suggest_wizard_field(
            wizard_type=request.wizard_type,
            field_name=request.field_name,
            patient_context=request.patient_context.dict(),
            current_wizard_data=request.current_wizard_data,
        )

        return {
            "success": True,
            "suggestion": result,
        }

    except Exception as e:
        logger.error(f"Error in field suggestion endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint for wizard AI service"""
    return {
        "status": "healthy",
        "service": "Wizard AI",
        "langchain_enabled": True,
    }
