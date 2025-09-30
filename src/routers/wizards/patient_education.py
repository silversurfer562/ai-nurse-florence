"""
Patient Education Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
Educational content delivery system with learning pathways
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime

from ...utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/patient-education",
    tags=["wizards", "patient-education"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"}
    }
)

# Wizard session storage (Redis in production)
_wizard_sessions: Dict[str, Dict[str, Any]] = {}

class EducationStepData(BaseModel):
    """Data model for education step submission."""
    step_data: Dict[str, Any]
    comprehension_score: Optional[int] = None
    questions: Optional[List[str]] = None

@router.post("/start")
async def start_patient_education(
    topic: str = "general",
    patient_literacy_level: str = "standard"
):
    """Start patient education wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "patient_education",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 4,
        "completed_steps": [],
        "data": {
            "topic": topic,
            "literacy_level": patient_literacy_level,
            "learning_objectives": [],
            "content_delivered": [],
            "comprehension_checks": [],
            "follow_up_materials": []
        }
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "patient_education",
        "current_step": 1,
        "total_steps": 4,
        "step_title": "Learning Assessment",
        "step_description": "Assess patient's current knowledge and learning preferences",
        "fields": [
            {"name": "current_knowledge_level", "type": "select", "options": ["No knowledge", "Some knowledge", "Moderate knowledge", "Good knowledge"], "required": True},
            {"name": "preferred_learning_style", "type": "select", "options": ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"], "required": True},
            {"name": "language_preference", "type": "text", "required": True},
            {"name": "barriers_to_learning", "type": "textarea", "required": False},
            {"name": "support_system", "type": "textarea", "label": "Family/caregiver involvement", "required": False}
        ],
        "educational_note": "Tailor education to patient's literacy level, learning style, and cultural background."
    }

@router.get("/{wizard_id}/status")
async def get_patient_education_status(wizard_id: str):
    """Get patient education wizard status following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": session["wizard_type"],
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "completed_steps": session["completed_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "data": session["data"]
    }

@router.post("/{wizard_id}/step/{step_number}")
async def submit_patient_education_step(
    wizard_id: str,
    step_number: int,
    step_data: EducationStepData
):
    """Submit patient education step data following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number != session["current_step"]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid step. Expected step {session['current_step']}, got step {step_number}"
        )

    # Store step data based on step number
    step_mapping = {
        1: "learning_assessment",
        2: "content_delivery",
        3: "comprehension_check",
        4: "follow_up_plan"
    }

    if step_number in step_mapping:
        session["data"][step_mapping[step_number]] = step_data.step_data

    # Track comprehension scores if provided
    if step_data.comprehension_score is not None:
        session["data"]["comprehension_checks"].append({
            "step": step_number,
            "score": step_data.comprehension_score,
            "timestamp": datetime.now().isoformat()
        })

    # Track questions if provided
    if step_data.questions:
        if "patient_questions" not in session["data"]:
            session["data"]["patient_questions"] = []
        session["data"]["patient_questions"].extend(step_data.questions)

    # Mark step as completed
    if step_number not in session["completed_steps"]:
        session["completed_steps"].append(step_number)

    # Move to next step
    if step_number < session["total_steps"]:
        session["current_step"] = step_number + 1
        next_step_info = _get_step_info(step_number + 1, session["data"]["topic"])
    else:
        next_step_info = None

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_completed": step_number,
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "next_step": next_step_info
    }

@router.get("/{wizard_id}/step/{step_number}")
async def get_patient_education_step(wizard_id: str, step_number: int):
    """Get patient education step information."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number < 1 or step_number > session["total_steps"]:
        raise HTTPException(status_code=422, detail="Invalid step number")

    step_info = _get_step_info(step_number, session["data"]["topic"])

    # Get previously entered data if exists
    step_mapping = {
        1: "learning_assessment",
        2: "content_delivery",
        3: "comprehension_check",
        4: "follow_up_plan"
    }

    existing_data = session["data"].get(step_mapping.get(step_number, ""), {})

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_number": step_number,
        "existing_data": existing_data,
        **step_info
    }

@router.get("/{wizard_id}/materials")
async def get_education_materials(wizard_id: str):
    """Get recommended educational materials based on topic and learning style."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]
    topic = session["data"].get("topic", "general")
    learning_style = session["data"].get("learning_assessment", {}).get("preferred_learning_style", "Mixed")

    # Generate material recommendations based on topic and learning style
    materials = _generate_educational_materials(topic, learning_style)

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "topic": topic,
        "learning_style": learning_style,
        "materials": materials
    }

@router.delete("/{wizard_id}")
async def cancel_patient_education(wizard_id: str):
    """Cancel and delete patient education wizard session."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    del _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "message": "Patient education wizard session cancelled",
        "wizard_id": wizard_id
    }

def _get_step_info(step_number: int, topic: str = "general") -> Dict[str, Any]:
    """Get step configuration information."""

    steps = {
        1: {
            "step_title": "Learning Assessment",
            "step_description": "Assess patient's current knowledge and learning preferences",
            "fields": [
                {"name": "current_knowledge_level", "type": "select", "options": ["No knowledge", "Some knowledge", "Moderate knowledge", "Good knowledge"], "required": True},
                {"name": "preferred_learning_style", "type": "select", "options": ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"], "required": True},
                {"name": "language_preference", "type": "text", "required": True},
                {"name": "barriers_to_learning", "type": "textarea", "required": False},
                {"name": "support_system", "type": "textarea", "label": "Family/caregiver involvement", "required": False}
            ],
            "educational_note": "Tailor education to patient's literacy level, learning style, and cultural background."
        },
        2: {
            "step_title": "Content Delivery",
            "step_description": f"Deliver educational content about {topic}",
            "fields": [
                {"name": "key_concepts_covered", "type": "textarea", "required": True},
                {"name": "demonstrations_provided", "type": "textarea", "required": False},
                {"name": "materials_given", "type": "textarea", "label": "Written materials provided", "required": True},
                {"name": "visual_aids_used", "type": "textarea", "required": False},
                {"name": "patient_engagement", "type": "select", "options": ["Excellent", "Good", "Fair", "Poor"], "required": True},
                {"name": "time_spent", "type": "number", "unit": "minutes", "required": True}
            ],
            "educational_note": "Use teach-back method to ensure comprehension. Provide materials at appropriate literacy level."
        },
        3: {
            "step_title": "Comprehension Check",
            "step_description": "Verify patient understanding using teach-back method",
            "fields": [
                {"name": "teach_back_response", "type": "textarea", "label": "Patient's explanation in own words", "required": True},
                {"name": "comprehension_score", "type": "number", "min": 0, "max": 100, "unit": "%", "required": True},
                {"name": "areas_of_confusion", "type": "textarea", "required": False},
                {"name": "additional_questions", "type": "textarea", "required": False},
                {"name": "demonstration_accuracy", "type": "select", "label": "Return demonstration accuracy", "options": ["Accurate", "Mostly accurate", "Needs improvement", "Unable to demonstrate"], "required": False}
            ],
            "educational_note": "Use teach-back method: 'To make sure I explained clearly, can you tell me in your own words...'"
        },
        4: {
            "step_title": "Follow-up Plan",
            "step_description": "Establish follow-up education and support plan",
            "fields": [
                {"name": "reinforcement_needed", "type": "select", "options": ["None", "Minimal", "Moderate", "Extensive"], "required": True},
                {"name": "follow_up_date", "type": "date", "required": True},
                {"name": "topics_to_review", "type": "textarea", "required": False},
                {"name": "support_resources", "type": "textarea", "label": "Community resources provided", "required": True},
                {"name": "contact_information", "type": "textarea", "label": "Contact info for questions", "required": True},
                {"name": "documentation_completed", "type": "boolean", "required": True}
            ],
            "educational_note": "Provide written discharge instructions and emergency contact information."
        }
    }

    return steps.get(step_number, {})

def _generate_educational_materials(topic: str, learning_style: str) -> List[Dict[str, Any]]:
    """Generate recommended educational materials based on topic and learning style."""

    # Base materials available for all topics
    materials = []

    if learning_style in ["Visual", "Mixed"]:
        materials.append({
            "type": "video",
            "title": f"Understanding {topic.title()}",
            "description": "Visual guide with animations and graphics",
            "duration": "5-10 minutes",
            "language": "English with subtitles available"
        })
        materials.append({
            "type": "infographic",
            "title": f"{topic.title()} Quick Reference",
            "description": "One-page visual summary with key information",
            "format": "PDF, printable"
        })

    if learning_style in ["Reading/Writing", "Mixed"]:
        materials.append({
            "type": "handout",
            "title": f"Patient Guide to {topic.title()}",
            "description": "Comprehensive written guide at 6th grade reading level",
            "format": "PDF, available in multiple languages"
        })
        materials.append({
            "type": "worksheet",
            "title": f"My {topic.title()} Action Plan",
            "description": "Fill-in worksheet for personal care planning",
            "format": "Printable PDF"
        })

    if learning_style in ["Auditory", "Mixed"]:
        materials.append({
            "type": "audio",
            "title": f"{topic.title()} Audio Guide",
            "description": "Narrated guide covering key concepts",
            "duration": "10-15 minutes",
            "format": "MP3, downloadable"
        })

    if learning_style in ["Kinesthetic", "Mixed"]:
        materials.append({
            "type": "demonstration",
            "title": f"{topic.title()} Skills Practice",
            "description": "Hands-on practice session with return demonstration",
            "duration": "15-20 minutes",
            "supplies_needed": "Provided by nursing staff"
        })

    # Add web resources for all
    materials.append({
        "type": "website",
        "title": "MedlinePlus Patient Education",
        "url": "https://medlineplus.gov",
        "description": "Reliable health information from NIH",
        "note": "Search for your specific condition"
    })

    return materials