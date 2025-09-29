"""
Condition-Based Wizard Router
Provides endpoints for guided nursing documentation workflows
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ..models.schemas import BaseResponse
from ..services.condition_wizard_service import (
    complete_wizard,
    create_condition_wizard,
    get_wizard_session,
    update_wizard_progress,
)
from ..utils.api_responses import create_error_response, create_success_response
from ..utils.config import get_educational_banner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wizards", tags=["condition-wizards"])

# Pydantic models for request/response validation
class CreateWizardRequest(BaseModel):
    condition_name: str = Field(..., description="Name of the medical condition")
    condition_id: str = Field(..., description="MONDO ID or condition identifier")
    wizard_type: str = Field(..., description="Type of wizard to create")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="Additional user context")

class UpdateWizardRequest(BaseModel):
    step_completed: str = Field(..., description="Step that was completed")
    step_data: Dict[str, Any] = Field(..., description="Data from the completed step")

class WizardResponse(BaseModel):
    banner: str = Field(default=get_educational_banner())
    wizard_id: str
    wizard_type: str
    condition: Dict[str, Any]
    status: str
    data: Dict[str, Any]

class WizardProgressResponse(BaseModel):
    banner: str = Field(default=get_educational_banner())
    wizard_id: str
    progress_percentage: float
    steps_completed: List[str]
    cached_data_keys: List[str]

class WizardCompletionResponse(BaseModel):
    banner: str = Field(default=get_educational_banner())
    wizard_id: str
    wizard_type: str
    condition: str
    status: str
    final_document: Dict[str, Any]
    completion_time: str


@router.get("/types")
async def get_wizard_types() -> Dict[str, Any]:
    """
    Get available wizard types for nursing documentation

    Returns list of available wizard types with descriptions
    """
    wizard_types = {
        "sbar": {
            "name": "SBAR Report",
            "description": "Situation-Background-Assessment-Recommendation structured communication",
            "use_case": "Provider communication, shift report, urgent situations",
            "estimated_time": "5-10 minutes"
        },
        "care_plan": {
            "name": "Nursing Care Plan",
            "description": "Comprehensive care planning with diagnoses, goals, and interventions",
            "use_case": "Care planning, documentation, quality improvement",
            "estimated_time": "15-20 minutes"
        },
        "nursing_assessment": {
            "name": "Focused Assessment",
            "description": "Condition-specific nursing assessment with priority focus areas",
            "use_case": "Admission assessment, change in condition, comprehensive evaluation",
            "estimated_time": "10-15 minutes"
        },
        "handoff": {
            "name": "Handoff Communication",
            "description": "Structured shift-to-shift or unit-to-unit communication",
            "use_case": "Change of shift, transfers, assignment updates",
            "estimated_time": "3-5 minutes"
        },
        "medication_reconciliation": {
            "name": "Medication Reconciliation",
            "description": "Systematic review and reconciliation of medications",
            "use_case": "Admission, transfer, discharge, medication changes",
            "estimated_time": "8-12 minutes"
        }
    }

    return create_success_response({
        "wizard_types": wizard_types,
        "total_available": len(wizard_types),
        "educational_note": "These wizards provide structured templates based on evidence-based nursing practices"
    })


@router.post("/create", response_model=WizardResponse)
async def create_wizard(request: CreateWizardRequest) -> WizardResponse:
    """
    Create a new condition-based wizard

    Creates a guided workflow for nursing documentation based on selected condition
    """
    try:
        # Validate wizard type
        valid_types = ["sbar", "care_plan", "nursing_assessment", "handoff", "medication_reconciliation"]
        if request.wizard_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid wizard type. Must be one of: {', '.join(valid_types)}"
            )

        # Create the wizard
        wizard_data = await create_condition_wizard(
            condition_name=request.condition_name,
            condition_id=request.condition_id,
            wizard_type=request.wizard_type,
            user_context=request.user_context
        )

        return WizardResponse(
            wizard_id=wizard_data["wizard_id"],
            wizard_type=wizard_data["wizard_type"],
            condition=wizard_data["condition"],
            status=wizard_data["status"],
            data={
                "next_steps": wizard_data["next_steps"],
                "cached_data_available": wizard_data["cached_data_available"]
            }
        )

    except Exception as e:
        logger.error(f"Failed to create wizard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wizard: {str(e)}"
        )


@router.get("/{wizard_id}")
async def get_wizard(wizard_id: str) -> Dict[str, Any]:
    """
    Get wizard session details and cached data

    Retrieves current wizard state including progress and cached medical data
    """
    try:
        session = await get_wizard_session(wizard_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found"
            )

        return create_success_response({
            "wizard_session": session,
            "educational_note": "Review cached medical data and continue with guided workflow"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get wizard {wizard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve wizard: {str(e)}"
        )


@router.post("/{wizard_id}/progress", response_model=WizardProgressResponse)
async def update_wizard(wizard_id: str, request: UpdateWizardRequest) -> WizardProgressResponse:
    """
    Update wizard progress with completed step data

    Records completion of a wizard step and caches the step data for final document generation
    """
    try:
        progress_data = await update_wizard_progress(
            wizard_id=wizard_id,
            step_completed=request.step_completed,
            step_data=request.step_data
        )

        return WizardProgressResponse(
            wizard_id=progress_data["wizard_id"],
            progress_percentage=progress_data["progress_percentage"],
            steps_completed=progress_data["steps_completed"],
            cached_data_keys=progress_data["cached_data_keys"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to update wizard {wizard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update wizard: {str(e)}"
        )


@router.post("/{wizard_id}/complete", response_model=WizardCompletionResponse)
async def complete_wizard_endpoint(wizard_id: str) -> WizardCompletionResponse:
    """
    Complete wizard and generate final nursing documentation

    Generates structured nursing documentation based on completed wizard steps and cached medical data
    """
    try:
        completion_data = await complete_wizard(wizard_id)

        return WizardCompletionResponse(
            wizard_id=completion_data["wizard_id"],
            wizard_type=completion_data["wizard_type"],
            condition=completion_data["condition"],
            status=completion_data["status"],
            final_document=completion_data["final_document"],
            completion_time=completion_data["completion_time"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to complete wizard {wizard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete wizard: {str(e)}"
        )


@router.get("/{wizard_id}/template")
async def get_wizard_template(
    wizard_id: str,
    step: Optional[str] = Query(None, description="Specific step to get template for")
) -> Dict[str, Any]:
    """
    Get template and guidance for current wizard step

    Provides structured templates with condition-specific guidance for nursing documentation
    """
    try:
        session = await get_wizard_session(wizard_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found"
            )

        # Get cached templates and guidance
        cached_data = session.get("cached_data", {})
        templates = cached_data.get("templates", {})

        # Get step-specific guidance
        step_guidance = {}
        if step:
            step_guidance = _get_step_guidance(session["wizard_type"], step, cached_data)

        return create_success_response({
            "wizard_id": wizard_id,
            "wizard_type": session["wizard_type"],
            "condition": session["condition_data"]["name"],
            "templates": templates,
            "step_guidance": step_guidance,
            "cached_interventions": cached_data.get("nursing_interventions", []),
            "cached_assessments": cached_data.get("assessment_priorities", []),
            "cached_medications": cached_data.get("medications", []),
            "educational_note": "Templates are pre-populated with condition-specific guidance"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get template for wizard {wizard_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )


def _get_step_guidance(wizard_type: str, step: str, cached_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get step-specific guidance and prompts"""

    guidance_map: Dict[str, Dict[str, Dict[str, Any]]] = {
        "sbar": {
            "situation": {
                "prompts": [
                    "What is the patient's current condition?",
                    "What prompted this communication?",
                    "What is the urgency level?"
                ],
                "tips": [
                    "Be concise but complete",
                    "State the most critical information first",
                    "Include patient identifiers"
                ]
            },
            "background": {
                "prompts": [
                    "What is the relevant medical history?",
                    "What treatments have been tried?",
                    "What are the current medications?"
                ],
                "tips": [
                    "Focus on relevant history only",
                    "Include allergies and current orders",
                    "Mention recent changes"
                ]
            },
            "assessment": {
                "prompts": [
                    "What are the current vital signs?",
                    "What are your nursing assessments?",
                    "What is your clinical concern?"
                ],
                "tips": [
                    "Include objective data",
                    "State your nursing judgment",
                    "Highlight abnormal findings"
                ]
            },
            "recommendation": {
                "prompts": [
                    "What do you need from the provider?",
                    "What is the timeframe for response?",
                    "What are you requesting?"
                ],
                "tips": [
                    "Be specific about requests",
                    "Suggest timeframes",
                    "Offer alternatives if appropriate"
                ]
            }
        }
    }

    wizard_guidance = guidance_map.get(wizard_type, {})
    step_guidance: Dict[str, Any] = wizard_guidance.get(step.lower(), {}).copy()

    # Add condition-specific guidance
    if cached_data.get("assessment_priorities"):
        step_guidance["condition_specific"] = {
            "assessment_priorities": cached_data["assessment_priorities"],
            "red_flags": [item.get("red_flags", "") for item in cached_data["assessment_priorities"]]
        }

    return step_guidance
