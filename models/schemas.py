from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."


class Reference(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None


class DiseaseSummary(BaseModel):
    banner: str
    query: str
    summary: str
    references: List[Reference]


class PubMedArticle(BaseModel):
    pmid: Optional[str] = None
    title: Optional[str] = None
    abstract: Optional[str] = None
    url: Optional[str] = None


class PubMedSearchResponse(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    query: str
    results: List[PubMedArticle] = []


class ClinicalTrial(BaseModel):
    nct_id: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None
    conditions: List[str] = []
    locations: List[str] = []
    url: Optional[str] = None


class ClinicalTrialsResponse(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    condition: str
    status: Optional[str] = None
    results: List[ClinicalTrial] = []


class MedlinePlusSummary(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    topic: str
    summary: Optional[str] = None
    references: List[Reference] = []


class SBARRequest(BaseModel):
    notes: str = Field(..., description="De-identified clinical or shift notes")


class SBAR(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    situation: str
    background: str
    assessment: str
    recommendation: str
    references: List[Reference] = []


class PatientEducationRequest(BaseModel):
    topic: str = Field(..., description="Education topic")
    level: int = Field(7, ge=5, le=10)
    lang: str = Field("en")


class PatientEducation(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    topic: str
    level: int
    lang: str = "en"
    what_it_is: str
    why_it_matters: str
    red_flags: List[str] = []
    self_care: List[str] = []
    when_to_seek_help: List[str] = []
    references: List[Reference] = []


class ReadabilityRequest(BaseModel):
    text: str


class ReadabilityResponse(BaseModel):
    banner: str = Field(default=EDU_BANNER)
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    sentences: int
    words: int
    syllables: int
    suggestions: List[str] = []


# --- Schemas for User and Token Handling ---

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    provider_user_id: str | None = None


class User(BaseModel):
    id: uuid.UUID
    provider: str
    provider_user_id: str

    # pydantic v2: replace legacy Config.orm_mode with model_config.from_attributes
    model_config = {
        "from_attributes": True
    }

# Backwards-compatible re-exports: some parts of the app import these from `models.schemas`
# but the canonical implementations live under `src.models.schemas` for the richer clinical schemas.
try:
    # prefer the full definitions from `src.models.schemas`
    from src.models.schemas import ClinicalDecisionRequest, ClinicalDecisionResponse  # type: ignore
except Exception:
    # Fallback minimal stubs so imports don't fail in constrained environments
    class ClinicalDecisionRequest(BaseModel):
        patient_condition: str = Field(..., description="Primary patient condition")

    class ClinicalDecisionResponse(BaseModel):
        nursing_interventions: str = Field(..., description="Evidence-based nursing interventions")
