"""
A wizard for searching clinical trials.

This multi-step wizard helps users find relevant clinical trials by guiding
them through specifying search criteria.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from utils.api_responses import create_success_response, create_error_response
from utils.logging import get_logger

router = APIRouter(prefix="/wizards/clinical-trials", tags=["wizards"])
logger = get_logger(__name__)

# In-memory storage for wizard state. In production, use Redis or a database.
wizard_sessions: Dict[str, Dict[str, Any]] = {}

# --- Pydantic Models for Wizard Steps ---

class StartWizardResponse(BaseModel):
    wizard_id: str
    message: str

class Step1Input(BaseModel):
    wizard_id: str
    condition: str = Field(..., description="The medical condition to search trials for.", example="Non-small cell lung cancer")

class Step2Input(BaseModel):
    wizard_id: str
    intervention: Optional[str] = Field(None, description="Specific drug, device, or treatment.", example="Osimertinib")
    location: Optional[str] = Field(None, description="Geographic location (e.g., city, state, country).", example="California, USA")

class SearchResponse(BaseModel):
    search_summary: str
    results: List[Dict[str, Any]]

# --- Wizard Endpoints ---

@router.post("/start", response_model=StartWizardResponse, summary="Step 1: Start the clinical trial search wizard")
async def start_wizard():
    """Initializes a new search wizard session."""
    import uuid
    wizard_id = str(uuid.uuid4())
    wizard_sessions[wizard_id] = {}
    logger.info(f"Started clinical trial search wizard session: {wizard_id}")
    
    return create_success_response({
        "wizard_id": wizard_id,
        "message": "Wizard started. Please provide the medical condition."
    })

@router.post("/step2-condition", summary="Step 2: Specify the condition")
async def add_condition(step1_input: Step1Input):
    """Adds the primary medical condition to the search criteria."""
    wizard_id = step1_input.wizard_id
    if wizard_id not in wizard_sessions:
        return create_error_response("Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")
    
    wizard_sessions[wizard_id]["condition"] = step1_input.condition
    logger.info(f"Updated trial search session {wizard_id} with condition: {step1_input.condition}")
    
    return create_success_response({
        "wizard_id": wizard_id,
        "message": "Condition received. You can now add optional filters or execute the search."
    })

@router.post("/search", response_model=SearchResponse, summary="Step 3: Add optional filters and search")
async def search_trials(step2_input: Step2Input):
    """
    Adds optional filters (intervention, location) and executes the search
    against a clinical trials database.
    """
    wizard_id = step2_input.wizard_id
    if wizard_id not in wizard_sessions:
        return create_error_response("Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found")

    session = wizard_sessions[wizard_id]
    session.update(step2_input.dict(exclude_unset=True))

    # In a real application, you would call a service like ClinicalTrials.gov API
    # Here, we'll simulate the call and response.
    
    search_summary = f"Simulated search for condition '{session['condition']}'"
    if session.get('intervention'):
        search_summary += f" with intervention '{session['intervention']}'"
    if session.get('location'):
        search_summary += f" in location '{session['location']}'"
    
    logger.info(f"Executing trial search for session {wizard_id}: {search_summary}")

    # Mocked results
    mock_results = [
        {
            "trial_id": "NCT123456",
            "title": f"A Study of {session.get('intervention', 'NewDrug')} for {session['condition']}",
            "status": "Recruiting",
            "locations": [session.get('location', 'USA')]
        },
        {
            "trial_id": "NCT789012",
            "title": f"Efficacy and Safety of Placebo in {session['condition']}",
            "status": "Completed",
            "locations": ["Global"]
        }
    ]
    
    # Clean up the session
    del wizard_sessions[wizard_id]
    
    return create_success_response({
        "search_summary": search_summary,
        "results": mock_results
    })