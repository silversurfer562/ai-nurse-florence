"""
Clinical helper router - provides lightweight endpoints used by the frontend optimizer

This file adds two minimal endpoints for local development and testing:
- POST /clinical/optimize-query -> returns an enhanced prompt (stub)
- POST /clinical/generate-response -> returns a generated response for a prompt (stub)

These are intentionally simple and deterministic stubs suitable for development.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.services.openai_client import create_openai_service
from src.utils.api_responses import create_error_response, create_success_response

router = APIRouter(prefix="/clinical", tags=["clinical"])


class OptimizeRequest(BaseModel):
    primary_concern: str = Field(...)
    patient_age: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    comorbidities: Optional[str] = None
    timeline: Optional[str] = None
    severity: Optional[str] = None
    associated_symptoms: Optional[str] = None
    focus_areas: Optional[str] = None
    evidence_level: Optional[str] = None
    urgency_level: Optional[str] = None


class OptimizeResponse(BaseModel):
    status: str
    optimization_score: int
    enhanced_prompt: str


@router.post("/optimize-query", response_model=OptimizeResponse)
async def optimize_query(body: OptimizeRequest) -> OptimizeResponse:
    """Return a simple enhanced prompt for the frontend optimizer (stub).

    This function does not call external services and is safe for local testing.
    """
    try:
        # Build a small enhanced prompt deterministically
        prompt_lines = ["Clinical Assessment Request:\n"]
        prompt_lines.append(f"Primary Concern: {body.primary_concern}\n")
        if body.patient_age:
            prompt_lines.append(f"- Age: {body.patient_age} years\n")
        if body.primary_diagnosis:
            prompt_lines.append(f"- Primary Diagnosis: {body.primary_diagnosis}\n")
        if body.comorbidities:
            prompt_lines.append(f"- Comorbidities: {body.comorbidities}\n")

        prompt_lines.append("\nPlease provide evidence-based nursing assessment priorities, safety considerations, when to escalate care, and documentation requirements.")

        enhanced = "".join(prompt_lines)

        # Simple heuristic score: percentage of fields present
        present = sum(bool(getattr(body, f)) for f in [
            "primary_concern",
            "patient_age",
            "primary_diagnosis",
            "comorbidities",
            "timeline",
            "severity",
            "associated_symptoms",
            "focus_areas",
        ])
        total = 8
        score = int((present / total) * 100)

        return OptimizeResponse(status="success", optimization_score=score, enhanced_prompt=enhanced)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


class GenerateRequest(BaseModel):
    prompt: str = Field(...)


class GenerateResponse(BaseModel):
    status: str
    answer: str


@router.post("/generate-response", response_model=GenerateResponse)
async def generate_response(body: GenerateRequest) -> GenerateResponse:
    """Generate an AI response using the project's OpenAI service.

    Returns a simple JSON object compatible with the frontend which expects an
    `answer` field (or similar). Falls back to an educational stub when the
    service is unavailable.
    """
    try:
        service = create_openai_service()

        if not service:
            # Service unavailable - return a clear educational stub
            stub = (
                "OpenAI service unavailable. Returning educational stub response for development purposes. "
                "In production, ensure OPENAI_API_KEY is configured."
            )
            return GenerateResponse(status="success", answer=stub)

        # Delegate generation to the OpenAI service
        result = await service.generate_response(body.prompt, context="clinical_generate")

        # service.generate_response returns a dict with key 'response' on success
        answer = ""
        if isinstance(result, dict):
            answer = result.get("response") or result.get("answer") or result.get("text") or ""

        if not answer:
            # No answer produced - return a helpful fallback
            fallback = result.get("error") if isinstance(result, dict) else "AI generation returned no content"
            return GenerateResponse(status="error", answer=str(fallback or "AI generation returned no content"))

        return GenerateResponse(status="success", answer=answer)

    except Exception as e:
        # Log and return a structured error response (keep the frontend contract)
        return GenerateResponse(status="error", answer=f"AI generation failed: {str(e)}")
