"""
SBAR Report Wizard - AI Nurse Florence
Following Wizard Pattern Implementation for clinical documentation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from src.utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/sbar-report",
    tags=["wizards", "sbar-report"],
    responses={
        404: {"description": "SBAR wizard session not found"},
        422: {"description": "Invalid SBAR data"},
    },
)

# Session storage following session state pattern
_sbar_sessions: Dict[str, Dict[str, Any]] = {}


class SBARStep(BaseModel):
    """SBAR step data following API Design Standards."""

    situation: Optional[str] = Field(None, description="Current patient situation")
    background: Optional[str] = Field(None, description="Relevant patient background")
    assessment: Optional[str] = Field(None, description="Clinical assessment")
    recommendation: Optional[str] = Field(
        None, description="Recommendations and requests"
    )


@router.post("/start")
async def start_sbar_report():
    """Start SBAR report wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    _sbar_sessions[wizard_id] = {
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 4,
        "completed": False,
        "sbar_data": {},
        "sections": ["Situation", "Background", "Assessment", "Recommendation"],
    }

    return {
        "wizard_id": wizard_id,
        "current_step": 1,
        "section": "Situation",
        "prompt": "Describe the current patient situation and reason for communication",
        "banner": get_educational_banner(),
    }


@router.post("/{wizard_id}/step")
async def submit_sbar_step(wizard_id: str, step_data: SBARStep):
    """Submit SBAR step following clinical documentation standards."""
    if wizard_id not in _sbar_sessions:
        raise HTTPException(status_code=404, detail="SBAR session not found")

    session = _sbar_sessions[wizard_id]
    current_step = session["current_step"]

    # Store current step data
    step_fields = ["situation", "background", "assessment", "recommendation"]
    field_name = step_fields[current_step - 1]
    field_value = getattr(step_data, field_name)

    if field_value:
        session["sbar_data"][field_name] = field_value

    # Advance or complete
    next_step = current_step + 1
    if next_step > 4:
        session["completed"] = True
        return {
            "wizard_id": wizard_id,
            "completed": True,
            "sbar_report": session["sbar_data"],
            "banner": get_educational_banner(),
        }

    session["current_step"] = next_step
    prompts = [
        "Provide relevant patient background and medical history",
        "Share your clinical assessment and current findings",
        "State your recommendations and what you need",
    ]

    return {
        "wizard_id": wizard_id,
        "current_step": next_step,
        "section": session["sections"][next_step - 1],
        "prompt": prompts[next_step - 2],
        "banner": get_educational_banner(),
    }
