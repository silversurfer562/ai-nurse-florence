"""
SBAR Report Wizard - AI Nurse Florence
Following Wizard Pattern Implementation for clinical documentation
Enhanced with AI assistance for time-saving and quality improvement
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime
import logging
import re

from src.utils.config import get_educational_banner
from src.services.openai_client import OpenAIService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wizard/sbar-report",
    tags=["wizards", "sbar-report"],
    responses={
        404: {"description": "SBAR wizard session not found"},
        422: {"description": "Invalid SBAR data"}
    }
)

# Session storage following session state pattern
_sbar_sessions: Dict[str, Dict[str, Any]] = {}

# Initialize AI service
_ai_service = OpenAIService()

class SBARStep(BaseModel):
    """SBAR step data following API Design Standards."""
    situation: Optional[str] = Field(None, description="Current patient situation")
    background: Optional[str] = Field(None, description="Relevant patient background")
    assessment: Optional[str] = Field(None, description="Clinical assessment")
    recommendation: Optional[str] = Field(None, description="Recommendations and requests")

class SBAREnhanceRequest(BaseModel):
    """Request to enhance SBAR text with AI."""
    text: str = Field(..., description="Text to enhance")
    section: str = Field(..., description="SBAR section (situation/background/assessment/recommendation)")

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
        "sections": ["Situation", "Background", "Assessment", "Recommendation"]
    }
    
    return {
        "wizard_id": wizard_id,
        "current_step": 1,
        "section": "Situation",
        "prompt": "Describe the current patient situation and reason for communication",
        "banner": get_educational_banner()
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
            "banner": get_educational_banner()
        }
    
    session["current_step"] = next_step
    prompts = [
        "Provide relevant patient background and medical history",
        "Share your clinical assessment and current findings", 
        "State your recommendations and what you need"
    ]
    
    return {
        "wizard_id": wizard_id,
        "current_step": next_step,
        "section": session["sections"][next_step - 1],
        "prompt": prompts[next_step - 2],
        "banner": get_educational_banner()
    }

@router.post("/ai/enhance")
async def enhance_sbar_text(request: SBAREnhanceRequest):
    """
    AI-powered text enhancement for SBAR sections.
    Converts informal notes to professional clinical language.
    """
    try:
        section_guidance = {
            "situation": "Convert this to clear, concise SBAR Situation statement. Include patient ID, location, and reason for communication.",
            "background": "Convert this to professional SBAR Background. Include admission date, diagnosis, relevant history, and current medications.",
            "assessment": "Convert this to structured SBAR Assessment. Include vital signs, physical findings, and current status.",
            "recommendation": "Convert this to clear SBAR Recommendation. State specific actions needed and priority level."
        }

        guidance = section_guidance.get(request.section.lower(), "Convert to professional clinical language")

        prompt = f"""{guidance}

Informal notes: {request.text}

Convert to professional clinical language. Keep it concise and focused. Use standard medical terminology."""

        context = "You are a clinical documentation assistant helping nurses write professional SBAR reports. Be concise and use proper medical terminology."

        ai_response = await _ai_service.generate_response(prompt, context)

        return {
            "original": request.text,
            "enhanced": ai_response.get("response", request.text),
            "section": request.section
        }

    except Exception as e:
        logger.error(f"SBAR enhancement error: {e}")
        return {
            "original": request.text,
            "enhanced": request.text,
            "section": request.section,
            "error": "AI enhancement temporarily unavailable"
        }

@router.post("/ai/check-completeness")
async def check_sbar_completeness(sbar_data: Dict[str, Any]):
    """
    AI-powered completeness check for SBAR report.
    Identifies missing critical information.
    """
    try:
        prompt = f"""Review this SBAR report and identify any critical missing information.

Situation: {sbar_data.get('situation', 'Not provided')}
Background: {sbar_data.get('background', 'Not provided')}
Assessment: {sbar_data.get('assessment', 'Not provided')}
Recommendation: {sbar_data.get('recommendation', 'Not provided')}

List specific missing elements in each section. Be concise. Focus on:
- Situation: Patient ID, location, reason for call
- Background: Admission date, diagnosis, allergies, medications
- Assessment: Vital signs, physical findings, mental status
- Recommendation: Specific actions needed, priority level

Format as bullet points by section."""

        context = "You are a clinical documentation quality checker helping ensure complete SBAR reports."

        ai_response = await _ai_service.generate_response(prompt, context)

        return {
            "completeness_check": ai_response.get("response", "Unable to assess completeness"),
            "banner": get_educational_banner()
        }

    except Exception as e:
        logger.error(f"SBAR completeness check error: {e}")
        return {
            "completeness_check": "Completeness check temporarily unavailable",
            "error": str(e),
            "banner": get_educational_banner()
        }

@router.post("/ai/suggest-priority")
async def suggest_priority_level(assessment_data: Dict[str, Any]):
    """
    AI-powered priority suggestion based on assessment findings.
    Helps nurses quickly identify urgency level.
    """
    try:
        prompt = f"""Based on this patient assessment, suggest the appropriate priority level for communication.

Vital Signs: {assessment_data.get('vital_signs', 'Not provided')}
Physical Assessment: {assessment_data.get('physical_assessment', 'Not provided')}
Mental Status: {assessment_data.get('mental_status', 'Not provided')}
Clinical Concerns: {assessment_data.get('clinical_concerns', 'Not provided')}

Suggest priority level:
- STAT (immediate life-threatening)
- URGENT (requires attention within 1 hour)
- ROUTINE (can wait for regular rounds)

Provide brief reasoning (1-2 sentences)."""

        context = "You are a clinical triage assistant helping nurses assess communication priority. Be conservative - err on side of higher priority if uncertain."

        ai_response = await _ai_service.generate_response(prompt, context)

        # Extract priority level from response
        response_text = ai_response.get("response", "")
        priority = "routine"  # default

        if "STAT" in response_text.upper():
            priority = "stat"
        elif "URGENT" in response_text.upper():
            priority = "urgent"

        return {
            "suggested_priority": priority,
            "reasoning": response_text
        }

    except Exception as e:
        logger.error(f"Priority suggestion error: {e}")
        return {
            "suggested_priority": "routine",
            "reasoning": "Priority suggestion temporarily unavailable",
            "error": str(e)
        }

@router.post("/ai/check-medications")
async def check_medication_interactions(medication_text: Dict[str, str]):
    """
    Check for drug interactions from SBAR Background section.
    Integrates with drug interaction checker for patient safety.
    """
    try:
        from src.services.drug_interaction_service import DrugInteractionService

        med_text = medication_text.get("medications", "")

        if not med_text or len(med_text.strip()) < 3:
            return {
                "has_interactions": False,
                "message": "No medications provided to check"
            }

        # Parse medication names from text using AI
        prompt = f"""Extract medication names from this text. Return ONLY a comma-separated list of medication names, nothing else.

Text: {med_text}

Examples:
- "metformin 500mg BID, lisinopril 10mg daily" → metformin, lisinopril
- "Patient on warfarin and aspirin" → warfarin, aspirin
- "Current meds: Tylenol PRN, Lasix 40mg" → Tylenol, Lasix"""

        context = "You are a medication parser. Extract only drug names, no dosages or frequencies."

        ai_response = await _ai_service.generate_response(prompt, context)

        # Parse medication names
        med_list_text = ai_response.get("response", "")
        medications = [med.strip() for med in med_list_text.split(",") if med.strip()]

        if len(medications) < 2:
            return {
                "has_interactions": False,
                "medications_found": medications,
                "message": "Need at least 2 medications to check interactions"
            }

        # Check interactions using existing drug interaction service
        drug_service = DrugInteractionService()

        # Use the drug interaction service
        interaction_result = await drug_service.check_drug_interactions(
            drugs=medications,
            patient_context={"source": "sbar_wizard"}
        )

        # Parse interaction results
        interactions = interaction_result.get("interactions", [])
        total_interactions = interaction_result.get("total_interactions", 0)

        has_major_interactions = any(
            inter.get("severity", "").lower() in ["major", "severe", "critical"]
            for inter in interactions
        )

        return {
            "has_interactions": total_interactions > 0,
            "medications_found": medications,
            "total_interactions": total_interactions,
            "has_major_interactions": has_major_interactions,
            "interactions": interactions[:3],  # Return top 3 most important
            "full_report_available": total_interactions > 3
        }

    except Exception as e:
        logger.error(f"Medication interaction check error: {e}")
        return {
            "has_interactions": False,
            "error": "Medication check temporarily unavailable",
            "error_detail": str(e)
        }
