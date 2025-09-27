"""
A wizard for generating a custom clinical report on a disease.

This multi-step wizard guides users through building a detailed, context-aware
report on a specific medical condition, acting as an "Advanced Search" feature.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import json

from utils.api_responses import create_success_response, create_error_response
from services.openai_client import get_client
from utils.logging import get_logger

router = APIRouter(prefix="/wizards/disease-search", tags=["wizards"])
logger = get_logger(__name__)

# In-memory storage for wizard state. In production, use Redis or a database.
wizard_sessions: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models for Wizard Steps ---

class StartWizardInput(BaseModel):
    topic: str = Field(..., description="The medical condition or topic for the report.", example="Type 2 Diabetes")

class StartWizardResponse(BaseModel):
    wizard_id: str
    topic: str
    suggested_sections: List[str]
    pre_selected_sections: List[str]
    related_topics: List[str]

class GenerateReportInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    selected_sections: List[str] = Field(..., description="Sections to include in the report.")
    age_group: Optional[str] = Field(None, description="Patient age group (e.g., 'Pediatric', 'Adult', 'Geriatric').", example="Geriatric")
    comorbidities: Optional[List[str]] = Field(None, description="List of relevant patient comorbidities.", example=["Hypertension", "Chronic Kidney Disease"])

class NextStep(BaseModel):
    title: str
    prompt: str
    type: str

class GenerateReportResponse(BaseModel):
    wizard_id: str
    report: str
    topic: str
    suggested_next_steps: List[NextStep]

# --- Wizard Endpoints ---

@router.post("/start", response_model=StartWizardResponse, summary="Step 1: Start the Disease Report Wizard")
async def start_wizard(step_input: StartWizardInput):
    """
    Initializes a new disease report wizard. Provide a topic to get a
    unique `wizard_id` and a list of suggested sections for your report.
    """
    import uuid
    wizard_id = str(uuid.uuid4())
    topic = step_input.topic
    
    prompt = f"""
    For the medical topic "{topic}", generate a JSON object with three keys:
    1. "suggested_sections": A list of 7-10 relevant section titles for a clinical report.
    2. "pre_selected_sections": A list of the 3-4 most essential sections from the list above that should be selected by default.
    3. "related_topics": A list of 3 related medical topics for further exploration.
    """
    
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that helps structure clinical reports. Respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        suggestions = json.loads(response.choices[0].message.content)
        
        wizard_sessions[wizard_id] = {"topic": topic}
        logger.info(f"Started disease report wizard session: {wizard_id} for topic: {topic}")
        
        return create_success_response({
            "wizard_id": wizard_id,
            "topic": topic,
            "suggested_sections": suggestions.get("suggested_sections", []),
            "pre_selected_sections": suggestions.get("pre_selected_sections", []),
            "related_topics": suggestions.get("related_topics", [])
        })
    except Exception as e:
        logger.error(f"Failed to get dynamic suggestions for topic '{topic}': {e}", exc_info=True)
        return create_error_response(
            "Failed to generate dynamic suggestions for the topic.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "suggestion_generation_failed"
        )


@router.post("/generate", response_model=GenerateReportResponse, summary="Step 2: Generate the Custom Report")
async def generate_report(step_input: GenerateReportInput):
    """
    Generates the custom clinical report based on the selected sections and
    optional patient context (age group, comorbidities).
    """
    wizard_id = step_input.wizard_id
    if wizard_id not in wizard_sessions:
        return create_error_response("Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")

    session_data = wizard_sessions[wizard_id]
    topic = session_data["topic"]
    
    # Build the prompt for the LLM
    prompt_parts = [
        f"Generate a detailed clinical report on '{topic}' for a healthcare professional."
    ]
    
    if step_input.age_group:
        prompt_parts.append(f"Tailor the information for a '{step_input.age_group}' patient.")
    
    if step_input.comorbidities:
        comorbidities_str = ", ".join(step_input.comorbidities)
        prompt_parts.append(f"Pay special attention to interactions and considerations related to these comorbidities: {comorbidities_str}.")
        
    prompt_parts.append("\nThe report must include the following sections, clearly marked with headings:")
    for section in step_input.selected_sections:
        prompt_parts.append(f"- {section}")
        
    prompt_parts.append("\nProvide concise, evidence-based information in a professional tone.")
    
    prompt = "\n".join(prompt_parts)
    
    try:
        client = get_client()
        report_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a clinical information specialist AI, creating detailed reports for healthcare professionals."},
                {"role": "user", "content": prompt}
            ]
        )
        report_text = report_response.choices[0].message.content
        logger.info(f"Successfully generated disease report for session {wizard_id}")

        # Now, generate suggested next steps
        next_steps_prompt = f"""
        Based on the following clinical report on '{topic}', generate a JSON object containing a list of 3-4 suggested next steps for a healthcare professional.
        Each item in the list should be an object with three keys: "title" (a short, user-facing button label), "prompt" (a full prompt for another AI query), and "type" (e.g., "patient_education", "literature_search", "comparison").

        Report Context:
        - Age Group: {step_input.age_group or 'Not specified'}
        - Comorbidities: {', '.join(step_input.comorbidities) if step_input.comorbidities else 'None'}
        - Sections Covered: {', '.join(step_input.selected_sections)}
        
        Example response format:
        {{
            "suggested_next_steps": [
                {{
                    "title": "Create Patient Handout",
                    "prompt": "Generate a patient-friendly handout about {topic} focusing on lifestyle changes and medication adherence.",
                    "type": "patient_education"
                }}
            ]
        }}
        """
        
        next_steps_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that suggests relevant follow-up actions. Respond in JSON format."},
                {"role": "user", "content": next_steps_prompt}
            ],
            response_format={"type": "json_object"}
        )
        next_steps_data = json.loads(next_steps_response.choices[0].message.content)
        
        # Clean up the session
        del wizard_sessions[wizard_id]
        
        return create_success_response({
            "wizard_id": wizard_id,
            "topic": topic,
            "report": report_text,
            "suggested_next_steps": next_steps_data.get("suggested_next_steps", [])
        })
    except Exception as e:
        logger.error(f"Disease report generation failed for session {wizard_id}: {e}", exc_info=True)
        return create_error_response(
            "Failed to generate report from AI model.",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "generation_failed"
        )