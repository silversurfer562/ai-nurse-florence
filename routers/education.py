# routers/education.py
import logging

from fastapi import APIRouter

from models.schemas import PatientEducation, PatientEducationRequest
from utils.guardrails import educational_banner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["education"])


@router.post("/patient-education", response_model=PatientEducation)
async def patient_education(payload: PatientEducationRequest):
    """
    Generate patient education material using Claude AI (with OpenAI fallback).

    Uses unified AI service that tries Claude first (better for medical content),
    then falls back to OpenAI if Claude is unavailable.
    """
    # Import unified AI service
    try:
        from src.services.ai_service import ai_service

        # Call unified AI service (Claude with OpenAI fallback)
        response = await ai_service.generate_patient_education(
            condition=payload.topic,
            patient_context={
                "reading_level": (
                    "8th grade" if payload.level != "nurse" else "professional"
                ),
                "audience": payload.level,
            },
            language=payload.lang,
        )

        text = response.get("response", "")
        model_used = response.get("provider_used", "unknown")

        # Add note about AI provider if available
        note = ""
        if response.get("provider_used") == "claude":
            note = " (Powered by Claude AI)"
        elif response.get("provider_used") == "openai":
            note = " (Powered by OpenAI)"

        return PatientEducation(
            banner=educational_banner(), model=model_used + note, text=text
        )

    except ImportError:
        # Fallback to old OpenAI service if unified service not available
        logger.warning(
            "Unified AI service not available, falling back to OpenAI client"
        )
        from services.model_selector import TaskType
        from services.openai_client import chat

        complexity = "high" if payload.level == "nurse" else "medium"
        system = (
            "You are a clinical education assistant for nurses and allied professionals. "
            "Draft-only output. Not medical advice. "
            "Use clear structure and define clinical terms briefly on first use."
        )
        style_hint = (
            "Audience: {level}. Be concise but complete; include clinically relevant details "
            "appropriate for nursing students or practicing nurses."
            if payload.level == "nurse"
            else "Audience: {level}. Keep it clear and accessible; avoid unnecessary jargon."
        )
        messages = [
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": (
                    f"Topic: {payload.topic}\n"
                    f"Level: {payload.level}\n"
                    f"Language: {payload.lang}\n"
                    f"{style_hint.format(level=payload.level)}\n"
                    "Organize with short headings and bullet points where it aids readability.\n"
                ),
            },
        ]
        text, model_used = chat(
            messages,
            task=TaskType.EDUCATION,
            level=payload.level,
            complexity=complexity,
        )
        return PatientEducation(
            banner=educational_banner(), model=model_used, text=text
        )

    except Exception as e:
        # If unified AI service fails, return error
        logger.error(f"AI service failed: {e}")
        return PatientEducation(
            banner=educational_banner(),
            model="error",
            text=f"Unable to generate education material at this time. Please try again later. Error: {str(e)}",
        )
