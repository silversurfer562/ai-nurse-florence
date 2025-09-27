"""
A wizard for generating patient education materials.

This module provides a multi-step guided workflow (wizard) to help users
create customized patient education handouts.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from utils.api_responses import create_success_response, create_error_response
from services.openai_client import get_client
from utils.logging import get_logger

router = APIRouter(prefix="/wizards/patient-education", tags=["wizards"])
logger = get_logger(__name__)

# --- Pydantic Models for Wizard Steps ---

class Step1Input(BaseModel):
    topic: str = Field(..., description="The medical condition or topic for the handout.", example="Type 2 Diabetes")

class Step1Response(BaseModel):
    wizard_id: str
    topic: str
    suggested_sections: List[str]

class Step2Input(BaseModel):
    wizard_id: str
    selected_sections: List[str] = Field(..., description="Sections to include in the handout.")
    custom_sections: Optional[List[str]] = Field(None, description="User-defined custom sections.")
    target_audience: str = Field("patient", description="Audience (e.g., 'patient', 'caregiver', 'child').")
    reading_level: str = Field("8th grade", description="Desired reading level (e.g., '5th grade', '8th grade', 'high school').")

class Step2Response(BaseModel):
    wizard_id: str
    generation_task_id: str
    message: str

class GenerationResult(BaseModel):
    status: str
    handout_text: Optional[str] = None
    error: Optional[str] = None

# In-memory storage for wizard state and results.
# In a production system, this would be replaced with a database or Redis.
wizard_sessions: Dict[str, Any] = {}
generation_results: Dict[str, GenerationResult] = {}

# --- Wizard Endpoints ---

@router.post("/step1-topic", response_model=Step1Response, summary="Start the patient education wizard")
async def start_wizard(step1_input: Step1Input):
    """
    **Step 1: Define the Topic**

    Start the wizard by providing a medical topic. The system will return a
    unique wizard ID and suggest sections to include in the handout.
    """
    import uuid
    wizard_id = str(uuid.uuid4())
    
    # In a real implementation, you might use an LLM to get better suggestions.
    suggested_sections = [
        "What is it?",
        "Symptoms",
        "Causes and Risk Factors",
        "Diagnosis",
        "Treatment Options",
        "Lifestyle and Home Remedies",
        "When to see a doctor"
    ]
    
    wizard_sessions[wizard_id] = {
        "topic": step1_input.topic,
        "suggested_sections": suggested_sections
    }
    
    return create_success_response({
        "wizard_id": wizard_id,
        "topic": step1_input.topic,
        "suggested_sections": suggested_sections
    })

@router.post("/step2-generate", response_model=Step2Response, summary="Generate the handout")
async def generate_handout(step2_input: Step2Input):
    """
    **Step 2: Customize and Generate**

    Provide the wizard ID, select sections, and specify audience details.
    This will start the asynchronous generation of the handout.
    """
    wizard_id = step2_input.wizard_id
    if wizard_id not in wizard_sessions:
        return create_error_response("Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")

    import uuid
    task_id = str(uuid.uuid4())
    
    # Store generation parameters
    wizard_sessions[wizard_id].update(step2_input.dict())
    generation_results[task_id] = GenerationResult(status="pending")

    # In a real app, this would be a background task
    # For simplicity, we'll run it synchronously here.
    try:
        await _generate_handout_content(wizard_id, task_id)
    except Exception as e:
        logger.error(f"Handout generation failed for task {task_id}: {e}", exc_info=True)
        generation_results[task_id] = GenerationResult(status="failed", error=str(e))

    return create_success_response({
        "wizard_id": wizard_id,
        "generation_task_id": task_id,
        "message": "Handout generation started. Check the status endpoint for results."
    })

@router.get("/result/{task_id}", response_model=GenerationResult, summary="Get the generated handout")
async def get_generation_result(task_id: str):
    """
    **Step 3: Retrieve the Result**

    Check the status of the generation task and get the final handout text
    once it's complete.
    """
    result = generation_results.get(task_id)
    if not result:
        return create_error_response("Generation task not found.", status.HTTP_404_NOT_FOUND, "task_not_found")
    
    return create_success_response(result)

# --- Helper Function ---

async def _generate_handout_content(wizard_id: str, task_id: str):
    """Helper to generate the handout content using an LLM."""
    session_data = wizard_sessions[wizard_id]
    topic = session_data["topic"]
    sections = session_data["selected_sections"] + (session_data.get("custom_sections") or [])
    
    prompt = f"""
    Generate a patient education handout about "{topic}".
    The handout should be written at a {session_data['reading_level']} reading level
    for a {session_data['target_audience']}.
    
    Include the following sections, clearly marked with headings:
    - {', '.join(sections)}
    
    For each section, provide clear, concise, and easy-to-understand information.
    Start with a brief, one-paragraph overview of the topic.
    End with a disclaimer: "This information is for educational purposes only and does not replace professional medical advice."
    """
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in creating patient-friendly medical education materials."},
                {"role": "user", "content": prompt}
            ]
        )
        handout_text = response.choices[0].message.content
        generation_results[task_id] = GenerationResult(status="completed", handout_text=handout_text)
        logger.info(f"Successfully generated handout for task {task_id}")
    except Exception as e:
        logger.error(f"LLM call failed for task {task_id}: {e}", exc_info=True)
        generation_results[task_id] = GenerationResult(status="failed", error="Failed to generate content from AI model.")
        raise