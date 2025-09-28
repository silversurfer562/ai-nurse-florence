# routers/education.py
from fastapi import APIRouter
from models.schemas import PatientEducationRequest, PatientEducation
from services.openai_client import chat
from services.model_selector import TaskType
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["education"])


@router.post("/patient-education", response_model=PatientEducation)
def patient_education(payload: PatientEducationRequest):
    # Heuristic: nurse => high complexity; allied/public => medium by default
    complexity = "high" if payload.level == "nurse" else "medium"

    system = (
        "You are a clinical education assistant for nurses and allied professionals. "
        "Draft-only output. Not medical advice. "
        "Use clear structure and define clinical terms briefly on first use."
    )

    # “Concise but complete” for nurses prevents premature truncation
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

    # Optional: include model for QA/observability
    return PatientEducation(banner=educational_banner(), model=model_used, text=text)
