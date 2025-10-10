"""
Epic Integration Wizard API Router

Provides REST endpoints for the Epic FHIR integration setup wizard.
Uses LangChain/LangGraph agent for multi-step configuration workflow.

Copyright 2025 Deep Study AI, LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Lazy import of wizard agent
WIZARD_AVAILABLE = None


def get_wizard_imports():
    """Lazy import of Epic wizard agent"""
    global WIZARD_AVAILABLE
    if WIZARD_AVAILABLE is None:
        try:
            from agents.epic_integration_wizard import (
                WizardState,
                create_initial_state,
                epic_wizard_graph,
            )

            WIZARD_AVAILABLE = True
            return epic_wizard_graph, create_initial_state, WizardState
        except Exception as e:
            logger.warning(f"Epic wizard agent not available: {e}")
            WIZARD_AVAILABLE = False
            return None, None, None
    elif WIZARD_AVAILABLE:
        from agents.epic_integration_wizard import (
            WizardState,
            create_initial_state,
            epic_wizard_graph,
        )

        return epic_wizard_graph, create_initial_state, WizardState
    else:
        return None, None, None


# Create router
router = APIRouter(
    prefix="/wizard",
    tags=["Epic Integration Wizard"],
    responses={404: {"description": "Not found"}},
)


# =============================================================================
# Request/Response Models
# =============================================================================


class WizardStartRequest(BaseModel):
    """Request to start new wizard session"""

    reset_existing: bool = Field(
        default=False, description="Reset existing wizard session if one exists"
    )


class WizardStepInput(BaseModel):
    """Input for advancing wizard to next step"""

    step: int = Field(..., description="Current step number (1-7)")
    data: Dict[str, Any] = Field(..., description="Step-specific input data")


class WizardStateResponse(BaseModel):
    """Current wizard state response"""

    current_step: int
    completed_steps: list[int]
    total_steps: int = 7
    progress_percent: int
    step_name: str
    step_description: str
    can_proceed: bool
    errors: list[str]
    warnings: list[str]
    messages: list[Dict[str, str]]
    state_data: Dict[str, Any]


class WizardNavigationRequest(BaseModel):
    """Request to navigate wizard (back/next/jump)"""

    action: str = Field(..., description="Navigation action: next, back, jump")
    target_step: Optional[int] = Field(None, description="Target step for jump action")


# =============================================================================
# In-Memory Session Storage (Replace with Redis/Database in production)
# =============================================================================

wizard_sessions: Dict[str, Dict[str, Any]] = {}


def get_or_create_session(session_id: str = "default") -> Dict[str, Any]:
    """Get existing wizard session or create new one"""
    epic_wizard_graph, create_initial_state, WizardState = get_wizard_imports()

    if not epic_wizard_graph:
        raise HTTPException(
            status_code=503,
            detail="Epic wizard agent not available. LangChain dependencies may be missing.",
        )

    if session_id not in wizard_sessions:
        wizard_sessions[session_id] = {
            "state": create_initial_state(),
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
        }

    return wizard_sessions[session_id]


# =============================================================================
# API Endpoints
# =============================================================================


@router.post("/start", response_model=WizardStateResponse)
async def start_wizard(request: WizardStartRequest):
    """
    Start new Epic Integration wizard session

    Creates a new wizard session and returns initial state.
    If reset_existing=True, clears any existing session.
    """
    session_id = "default"  # In production, use user-specific session ID

    if request.reset_existing and session_id in wizard_sessions:
        del wizard_sessions[session_id]

    session = get_or_create_session(session_id)
    state = session["state"]

    # Run step 1 (prerequisites check) automatically
    epic_wizard_graph, create_initial_state, WizardState = get_wizard_imports()

    try:
        result = await epic_wizard_graph.ainvoke(state)
        session["state"] = result
        session["last_updated"] = datetime.utcnow().isoformat()

        return _build_state_response(result)

    except Exception as e:
        logger.error(f"Wizard start failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Wizard initialization failed: {str(e)}"
        )


@router.get("/state", response_model=WizardStateResponse)
async def get_wizard_state():
    """
    Get current wizard state

    Returns current progress, completed steps, and next actions.
    """
    session = get_or_create_session()
    state = session["state"]

    return _build_state_response(state)


@router.post("/step/{step_number}", response_model=WizardStateResponse)
async def submit_wizard_step(step_number: int, input_data: Dict[str, Any]):
    """
    Submit data for specific wizard step

    Validates input, updates state, and advances to next step if validation passes.

    **Step-specific inputs:**
    - Step 2 (Credentials): epic_client_id, epic_client_secret, epic_fhir_base_url, epic_oauth_token_url
    - Step 4 (Resources): selected_resources (list)
    - Step 5 (Test Lookup): test_mrn (string)
    - Step 6 (Confirm): configuration_confirmed (boolean)
    """
    session = get_or_create_session()
    state = session["state"]

    # Update state with input data
    state.update(input_data)

    # Import step functions
    from agents.epic_integration_wizard import (
        step_1_prerequisites,
        step_2_credentials,
        step_3_connection_test,
        step_4_resource_permissions,
        step_5_test_patient_lookup,
        step_6_review_confirm,
        step_7_complete,
    )

    # Map step numbers to their handler functions
    step_handlers = {
        1: step_1_prerequisites,
        2: step_2_credentials,
        3: step_3_connection_test,
        4: step_4_resource_permissions,
        5: step_5_test_patient_lookup,
        6: step_6_review_confirm,
        7: step_7_complete,
    }

    try:
        # Execute only the current step's handler (don't run full graph)
        if step_number in step_handlers:
            handler = step_handlers[step_number]
            result = await handler(state)

            # Advance to next step if current step was completed successfully
            if step_number in result.get("completed_steps", []):
                result["current_step"] = min(step_number + 1, 7)

            session["state"] = result
            session["last_updated"] = datetime.utcnow().isoformat()

            return _build_state_response(result)
        else:
            raise HTTPException(
                status_code=400, detail=f"Invalid step number: {step_number}"
            )

    except Exception as e:
        logger.error(f"Step {step_number} processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Step processing failed: {str(e)}")


@router.post("/navigate", response_model=WizardStateResponse)
async def navigate_wizard(request: WizardNavigationRequest):
    """
    Navigate wizard (next, back, jump to step)

    Microsoft wizard pattern: Back button, Next button, or jump to completed step.
    """
    session = get_or_create_session()
    state = session["state"]

    current_step = state.get("current_step", 1)
    completed_steps = state.get("completed_steps", [])

    if request.action == "next":
        # Advance to next step (if current step is completed)
        if current_step in completed_steps:
            state["current_step"] = min(current_step + 1, 7)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot advance: Step {current_step} not completed",
            )

    elif request.action == "back":
        # Go back to previous step
        state["current_step"] = max(current_step - 1, 1)

    elif request.action == "jump":
        # Jump to specific completed step
        if request.target_step is None:
            raise HTTPException(
                status_code=400, detail="target_step required for jump action"
            )

        if (
            request.target_step in completed_steps
            or request.target_step <= current_step
        ):
            state["current_step"] = request.target_step
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot jump to step {request.target_step}: not yet completed",
            )

    session["last_updated"] = datetime.utcnow().isoformat()

    return _build_state_response(state)


@router.post("/reset")
async def reset_wizard():
    """
    Reset wizard to initial state

    Clears all progress and starts over.
    """
    session_id = "default"
    if session_id in wizard_sessions:
        del wizard_sessions[session_id]

    session = get_or_create_session(session_id)
    return {
        "message": "Wizard reset successfully",
        "state": _build_state_response(session["state"]),
    }


@router.get("/progress")
async def get_wizard_progress():
    """
    Get wizard progress summary

    Returns progress percentage, completed steps, and estimated time remaining.
    """
    session = get_or_create_session()
    state = session["state"]

    completed = len(state.get("completed_steps", []))
    total = 7
    progress_percent = int((completed / total) * 100)

    return {
        "current_step": state.get("current_step", 1),
        "completed_steps": completed,
        "total_steps": total,
        "progress_percent": progress_percent,
        "integration_activated": state.get("integration_activated", False),
    }


# =============================================================================
# Helper Functions
# =============================================================================


def _build_state_response(state: Dict[str, Any]) -> WizardStateResponse:
    """Build standardized wizard state response"""

    current_step = state.get("current_step", 1)
    completed_steps = state.get("completed_steps", [])
    total_steps = 7
    progress_percent = int((len(completed_steps) / total_steps) * 100)

    # Step metadata
    step_info = {
        1: ("Prerequisites Check", "Validating system requirements"),
        2: ("Epic Credentials", "Enter Epic FHIR credentials"),
        3: ("Connection Test", "Testing Epic FHIR connection"),
        4: ("Resource Permissions", "Select FHIR resources to enable"),
        5: ("Test Patient Lookup", "Verify patient data retrieval"),
        6: ("Review & Confirm", "Review configuration before activation"),
        7: ("Complete", "Integration setup complete"),
    }

    step_name, step_description = step_info.get(current_step, ("Unknown", ""))

    # Determine if user can proceed
    can_proceed = current_step in completed_steps

    # Format messages
    messages = [
        {
            "role": "ai" if hasattr(msg, "content") else "human",
            "content": msg.content if hasattr(msg, "content") else str(msg),
        }
        for msg in state.get("messages", [])
    ]

    # State data (filtered to remove internal fields)
    state_data = {
        k: v
        for k, v in state.items()
        if k
        not in ["messages", "errors", "warnings", "current_step", "completed_steps"]
    }

    return WizardStateResponse(
        current_step=current_step,
        completed_steps=completed_steps,
        total_steps=total_steps,
        progress_percent=progress_percent,
        step_name=step_name,
        step_description=step_description,
        can_proceed=can_proceed,
        errors=state.get("errors", []),
        warnings=state.get("warnings", []),
        messages=messages,
        state_data=state_data,
    )
