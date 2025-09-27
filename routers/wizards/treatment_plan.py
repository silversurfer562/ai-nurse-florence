"""
A wizard for generating comprehensive treatment plans for healthcare professionals.

This multi-step wizard guides users through creating structured treatment plans
that include assessment, goals, interventions, monitoring, and evaluation components.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import Dict, Optional

from utils.api_responses import create_success_response, create_error_response
from services import openai_client
from utils.logging import get_logger

router = APIRouter(prefix="/wizards/treatment-plan", tags=["wizards"])
logger = get_logger(__name__)

# In-memory storage for wizard state. In production, use Redis or a database.
treatment_wizard_sessions: Dict[str, Dict[str, str]] = {}

# --- Pydantic Models for Wizard Steps ---

class StartTreatmentResponse(BaseModel):
    wizard_id: str
    message: str
    next_step: str

class TreatmentStepInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    text: str = Field(..., description="The text content for the current step.")

class TreatmentStepResponse(BaseModel):
    wizard_id: str
    next_step: str
    message: str

class InterventionsInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    nursing_interventions: str = Field(..., description="Planned nursing interventions.")
    medications: str = Field(..., description="Medication management plan.")
    patient_education: str = Field(..., description="Patient and family education plan.")

class InterventionsResponse(BaseModel):
    wizard_id: str
    next_step: str
    message: str

class GenerateTreatmentInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    evaluation_criteria: str = Field(..., description="Evaluation criteria and timeline.")

class GenerateTreatmentResponse(BaseModel):
    wizard_id: str
    treatment_plan: str
    summary: Dict[str, str]

# --- Wizard Endpoints ---

@router.post("/start", response_model=StartTreatmentResponse, summary="Step 1: Start the Treatment Plan wizard")
async def start_treatment_wizard():
    """
    Initializes a new Treatment Plan wizard session and returns a unique `wizard_id`.
    
    The treatment plan wizard follows a structured approach:
    1. Patient Assessment
    2. Treatment Goals
    3. Interventions (Nursing, Medications, Education)
    4. Monitoring Plan
    5. Evaluation Criteria
    
    Each step builds upon the previous to create a comprehensive care plan.
    """
    import uuid
    wizard_id = str(uuid.uuid4())
    treatment_wizard_sessions[wizard_id] = {}
    logger.info(f"Started Treatment Plan wizard session: {wizard_id}")
    
    return create_success_response({
        "wizard_id": wizard_id,
        "message": "Treatment Plan wizard started. Please provide the patient assessment including primary diagnosis, symptoms, and relevant history.",
        "next_step": "assessment"
    })

def _update_treatment_step(wizard_id: str, step_name: str, text: str, next_step_name: str, custom_message: Optional[str] = None):
    """Helper function to update a step in the treatment wizard session."""
    if wizard_id not in treatment_wizard_sessions:
        return create_error_response("Treatment wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")
    
    treatment_wizard_sessions[wizard_id][step_name] = text
    logger.info(f"Updated Treatment Plan session {wizard_id} with step: {step_name}")
    
    default_message = f"'{step_name.replace('_', ' ').title()}' received. Please proceed to add the '{next_step_name.replace('_', ' ').title()}'."
    
    return create_success_response({
        "wizard_id": wizard_id,
        "message": custom_message or default_message,
        "next_step": next_step_name
    })

@router.post("/assessment", response_model=TreatmentStepResponse, summary="Step 2: Add Patient Assessment")
async def add_patient_assessment(step_input: TreatmentStepInput):
    """
    Adds the **Patient Assessment** component to the treatment plan.
    
    Include:
    - Primary diagnosis and secondary conditions
    - Current symptoms and severity
    - Relevant medical/surgical history
    - Functional status and limitations
    - Psychosocial factors
    """
    return _update_treatment_step(
        step_input.wizard_id, 
        "assessment", 
        step_input.text, 
        "goals",
        "Patient assessment received. Please define the treatment goals including both short-term and long-term objectives."
    )

@router.post("/goals", response_model=TreatmentStepResponse, summary="Step 3: Add Treatment Goals")
async def add_treatment_goals(step_input: TreatmentStepInput):
    """
    Adds the **Treatment Goals** component to the treatment plan.
    
    Include:
    - Short-term goals (24-72 hours)
    - Long-term goals (weeks to months)
    - Patient-centered outcomes
    - Measurable objectives
    - Expected timeframes
    """
    return _update_treatment_step(
        step_input.wizard_id, 
        "goals", 
        step_input.text, 
        "interventions",
        "Treatment goals received. Please provide the planned interventions including nursing care, medications, and patient education."
    )

@router.post("/interventions", response_model=InterventionsResponse, summary="Step 4: Add Interventions")
async def add_interventions(interventions_input: InterventionsInput):
    """
    Adds the **Interventions** components to the treatment plan.
    
    This step captures three key intervention categories:
    - Nursing interventions and care activities
    - Medication management and administration
    - Patient and family education plans
    """
    wizard_id = interventions_input.wizard_id
    if wizard_id not in treatment_wizard_sessions:
        return create_error_response("Treatment wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")
    
    session_data = treatment_wizard_sessions[wizard_id]
    session_data["nursing_interventions"] = interventions_input.nursing_interventions
    session_data["medications"] = interventions_input.medications
    session_data["patient_education"] = interventions_input.patient_education
    
    logger.info(f"Updated Treatment Plan session {wizard_id} with interventions")
    
    return create_success_response({
        "wizard_id": wizard_id,
        "message": "Interventions received. Please provide the monitoring plan including vital signs, lab values, and symptom tracking.",
        "next_step": "monitoring"
    })

@router.post("/monitoring", response_model=TreatmentStepResponse, summary="Step 5: Add Monitoring Plan")
async def add_monitoring_plan(step_input: TreatmentStepInput):
    """
    Adds the **Monitoring Plan** component to the treatment plan.
    
    Include:
    - Vital signs monitoring frequency
    - Laboratory values to track
    - Symptom assessment schedules
    - Response to interventions
    - Safety parameters and alerts
    """
    return _update_treatment_step(
        step_input.wizard_id, 
        "monitoring", 
        step_input.text, 
        "evaluation",
        "Monitoring plan received. Please provide the evaluation criteria including success indicators and timeline for reassessment."
    )

@router.post("/generate", response_model=GenerateTreatmentResponse, summary="Step 6: Add Evaluation Criteria and Generate Plan")
async def generate_treatment_plan(step_input: GenerateTreatmentInput):
    """
    Adds the final **Evaluation Criteria** component and generates the complete,
    formatted treatment plan using an AI model.
    
    The generated plan will include:
    - Structured treatment plan document
    - Summary of key components
    - Professional formatting suitable for clinical use
    """
    wizard_id = step_input.wizard_id
    if wizard_id not in treatment_wizard_sessions:
        return create_error_response("Treatment wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")

    session_data = treatment_wizard_sessions[wizard_id]
    session_data["evaluation_criteria"] = step_input.evaluation_criteria

    # Verify all parts are present
    required_parts = ["assessment", "goals", "nursing_interventions", "medications", "patient_education", "monitoring", "evaluation_criteria"]
    if not all(part in session_data for part in required_parts):
        missing = [part.replace('_', ' ').title() for part in required_parts if part not in session_data]
        return create_error_response(
            f"Cannot generate treatment plan. Missing components: {', '.join(missing)}",
            status.HTTP_400_BAD_REQUEST,
            "missing_treatment_components"
        )

    prompt = (
        "Format the following clinical information into a comprehensive, professional treatment plan.\n"
        "Use clear headings and bullet points for readability. Ensure the plan is evidence-based and suitable for clinical implementation.\n\n"
        f"**PATIENT ASSESSMENT:**\n{session_data['assessment']}\n\n"
        f"**TREATMENT GOALS:**\n{session_data['goals']}\n\n"
        f"**NURSING INTERVENTIONS:**\n{session_data['nursing_interventions']}\n\n"
        f"**MEDICATION MANAGEMENT:**\n{session_data['medications']}\n\n"
        f"**PATIENT EDUCATION:**\n{session_data['patient_education']}\n\n"
        f"**MONITORING PLAN:**\n{session_data['monitoring']}\n\n"
        f"**EVALUATION CRITERIA:**\n{session_data['evaluation_criteria']}\n\n"
        "Please format this as a comprehensive treatment plan with:\n"
        "1. Clear section headers\n2. Organized bullet points\n3. Professional medical language\n4. Implementation timeline where appropriate\n5. Safety considerations highlighted\n"
    )

    try:
        client = openai_client.get_client()
        if not client:
            return create_error_response(
                "AI service unavailable. Treatment plan cannot be generated.",
                status.HTTP_503_SERVICE_UNAVAILABLE,
                "ai_service_unavailable",
            )

        # Call the AI client; tests will mock `openai_client.get_client()`
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert clinical nurse specialist with extensive experience in developing comprehensive treatment plans. "
                        "Format treatment plans with clear structure, evidence-based interventions, and professional clinical language. "
                        "Always include safety considerations and measurable outcomes."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )

        # Support different client response shapes safely
        treatment_plan = None
        try:
            treatment_plan = response.choices[0].message.content
        except Exception:
            try:
                treatment_plan = response.choices[0].text
            except Exception:
                treatment_plan = str(response)

        logger.info(f"Successfully generated treatment plan for session {wizard_id}")

        summary = {
            "primary_diagnosis": (session_data.get('assessment') or '')[:100] + "...",
            "key_goals": (session_data.get('goals') or '')[:100] + "...",
            "main_interventions": (session_data.get('nursing_interventions') or '')[:100] + "...",
            "monitoring_focus": (session_data.get('monitoring') or '')[:100] + "...",
        }

        # Clean up session
        treatment_wizard_sessions.pop(wizard_id, None)

        return create_success_response({
            "wizard_id": wizard_id,
            "treatment_plan": treatment_plan,
            "summary": summary,
        })

    except Exception as e:
        logger.error(f"Treatment plan generation failed for session {wizard_id}: {e}", exc_info=True)
        return create_error_response(
            "Failed to generate treatment plan from AI model.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "generation_failed",
        )

@router.get("/session/{wizard_id}", summary="Get Current Session Status")
async def get_session_status(wizard_id: str):
    """
    Retrieves the current status of a treatment plan wizard session.
    
    Returns the completed steps and what step is needed next.
    Useful for resuming interrupted sessions or checking progress.
    """
    if wizard_id not in treatment_wizard_sessions:
        return create_error_response("Treatment wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")
    
    session_data = treatment_wizard_sessions[wizard_id]
    completed_steps = list(session_data.keys())
    
    # Determine next step based on what's completed
    step_order = ["assessment", "goals", "nursing_interventions", "medications", "patient_education", "monitoring", "evaluation_criteria"]
    next_step = None
    
    if "assessment" not in completed_steps:
        next_step = "assessment"
    elif "goals" not in completed_steps:
        next_step = "goals"
    elif not all(key in completed_steps for key in ["nursing_interventions", "medications", "patient_education"]):
        next_step = "interventions"
    elif "monitoring" not in completed_steps:
        next_step = "monitoring"
    elif "evaluation_criteria" not in completed_steps:
        next_step = "evaluation"
    else:
        next_step = "generate"
    
    return create_success_response({
        "wizard_id": wizard_id,
        "completed_steps": completed_steps,
        "next_step": next_step,
        "progress": f"{len(completed_steps)}/{len(step_order)} steps completed"
    })

@router.delete("/session/{wizard_id}", summary="Cancel Treatment Plan Session")
async def cancel_session(wizard_id: str):
    """
    Cancels and removes a treatment plan wizard session.
    
    Use this endpoint to clean up sessions that are no longer needed
    or to start over with a fresh session.
    """
    if wizard_id not in treatment_wizard_sessions:
        return create_error_response("Treatment wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")
    
    del treatment_wizard_sessions[wizard_id]
    logger.info(f"Cancelled treatment plan wizard session: {wizard_id}")
    
    return create_success_response({
        "message": f"Treatment plan wizard session {wizard_id} has been cancelled.",
        "wizard_id": wizard_id
    })
