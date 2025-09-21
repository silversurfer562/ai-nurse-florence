from fastapi import APIRouter
from models.schemas import PatientEducationRequest, PatientEducation
from services.education_service import make_patient_education
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["education"])
example = {
    "banner": "Draft for clinician review — not medical advice. No PHI stored.",
    "topic": "Asthma",
    "level": 7,
    "lang": "en",
    "what_it_is": "Asthma is a condition that makes breathing passages swell and narrow.",
    "why_it_matters": "Knowing the basics helps you notice changes early.",
    "red_flags": [
        "Trouble speaking full sentences",
        "Chest tightness that is new or severe",
    ],
    "self_care": ["Avoid triggers when possible", "Track symptoms in a simple log"],
    "when_to_seek_help": ["Call emergency services for severe breathing problems"],
    "references": [],
}


@router.post(
    "/patient-education",
    response_model=PatientEducation,
    responses={200: {"content": {"application/json": {"example": example}}}},
)
def patient_education(payload: PatientEducationRequest):
    data = make_patient_education(payload.topic, level=payload.level, lang=payload.lang)
    return PatientEducation(banner=educational_banner(), **data)
