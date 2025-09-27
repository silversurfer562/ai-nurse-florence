"""
Pydantic schemas for AI Nurse Florence
Input/output validation with clinical context
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime

class SeverityLevel(str, Enum):
    """Clinical severity levels"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class CareSetting(str, Enum):
    """Healthcare settings"""
    ICU = "icu"
    MED_SURG = "med-surg"
    ED = "emergency"
    OUTPATIENT = "outpatient"
    HOME_HEALTH = "home-health"
    SKILLED_NURSING = "skilled-nursing"

class EvidenceLevel(str, Enum):
    """Evidence-based practice levels"""
    LEVEL_I = "Level I - Systematic Review/Meta-analysis"
    LEVEL_II = "Level II - RCT"
    LEVEL_III = "Level III - Controlled Trial"
    LEVEL_IV = "Level IV - Case-Control/Cohort"
    LEVEL_V = "Level V - Systematic Review of Descriptive"
    LEVEL_VI = "Level VI - Single Descriptive Study"
    LEVEL_VII = "Level VII - Expert Opinion"

# Base Response Schema
class BaseResponse(BaseModel):
    """Base response with educational banner"""
    success: bool = True
    message: str = "Success"
    banner: str = Field(default="Draft for clinician review — not medical advice. No PHI stored.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Clinical Decision Support Schemas
class ClinicalDecisionRequest(BaseModel):
    """Clinical decision support input"""
    patient_condition: str = Field(..., description="Primary patient condition or diagnosis")
    severity: SeverityLevel = Field(default=SeverityLevel.MODERATE)
    comorbidities: List[str] = Field(default=[], description="Relevant comorbidities")
    care_setting: CareSetting = Field(default=CareSetting.MED_SURG)
    additional_context: Optional[str] = Field(None, description="Additional clinical context")
    
    @validator('patient_condition')
    def validate_condition(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Patient condition must be at least 3 characters')
        return v.strip()

class ClinicalDecisionResponse(BaseResponse):
    """Clinical decision support output"""
    nursing_interventions: str = Field(..., description="Evidence-based nursing interventions")
    evidence_level: EvidenceLevel = Field(default=EvidenceLevel.LEVEL_VII)
    safety_considerations: List[str] = Field(default=[])
    clinical_context: Optional[Dict[str, Any]] = None

# Risk Assessment Schemas
class RiskAssessmentRequest(BaseModel):
    """Risk assessment input"""
    assessment_type: str = Field(..., description="Type of risk assessment (morse, braden, mews)")
    patient_data: Dict[str, Any] = Field(..., description="Patient assessment data")
    care_setting: CareSetting = Field(default=CareSetting.MED_SURG)

class RiskAssessmentResponse(BaseResponse):
    """Risk assessment output"""
    risk_score: int = Field(..., description="Calculated risk score")
    risk_level: str = Field(..., description="Risk level interpretation")
    interventions: List[str] = Field(..., description="Recommended interventions")
    reassessment_interval: str = Field(..., description="When to reassess")

# SBAR Documentation Schemas
class SBARRequest(BaseModel):
    """SBAR report input"""
    situation: str = Field(..., description="Current patient situation")
    background: str = Field(..., description="Relevant background information")
    assessment: str = Field(..., description="Clinical assessment findings")
    recommendation: str = Field(..., description="Recommendations for care")
    
    @validator('situation', 'background', 'assessment', 'recommendation')
    def validate_sbar_fields(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('SBAR fields must be at least 10 characters')
        return v.strip()

class SBARResponse(BaseResponse):
    """SBAR report output"""
    formatted_report: str = Field(..., description="Formatted SBAR report")
    clinical_priorities: List[str] = Field(default=[])
    follow_up_actions: List[str] = Field(default=[])

# Literature Search Schemas
class LiteratureSearchRequest(BaseModel):
    """Literature search input"""
    query: str = Field(..., min_length=3, description="Search query")
    max_results: int = Field(default=10, ge=1, le=50)
    filter_years: Optional[int] = Field(None, ge=1990, le=2025)
    study_types: List[str] = Field(default=[], description="Preferred study types")

class LiteratureItem(BaseModel):
    """Individual literature item"""
    title: str
    authors: List[str]
    journal: str
    year: int
    abstract: str
    url: Optional[str] = None
    evidence_level: Optional[EvidenceLevel] = None

class LiteratureSearchResponse(BaseResponse):
    """Literature search output"""
    articles: List[LiteratureItem]
    total_found: int
    search_strategy: str
    evidence_summary: Optional[str] = None

# Patient Education Schemas
class PatientEducationRequest(BaseModel):
    """Patient education material input"""
    topic: str = Field(..., description="Education topic")
    reading_level: str = Field(default="6th grade", description="Target reading level")
    language: str = Field(default="en", description="Language code")
    format_type: str = Field(default="general", description="Format type")

class PatientEducationResponse(BaseResponse):
    """Patient education material output"""
    content: str = Field(..., description="Educational content")
    reading_level_score: Optional[float] = None
    key_points: List[str] = Field(default=[])
    additional_resources: List[str] = Field(default=[])

# Wizard Workflow Schemas
class WizardStepRequest(BaseModel):
    """Wizard workflow step input"""
    wizard_type: str = Field(..., description="Type of wizard workflow")
    step_data: Dict[str, Any] = Field(..., description="Data for current step")
    session_id: Optional[str] = None

class WizardStepResponse(BaseResponse):
    """Wizard workflow step output"""
    current_step: str
    next_step: Optional[str] = None
    step_data: Dict[str, Any]
    progress_percentage: int = Field(ge=0, le=100)
    is_complete: bool = False

# Pagination Schema
class PaginationRequest(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)

class PaginatedResponse(BaseResponse):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

# Error Response Schema
class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = False
    error: bool = True
    error_type: str
    message: str
    details: Dict[str, Any] = Field(default={})
    banner: str = Field(default="Draft for clinician review — not medical advice. No PHI stored.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health Check Schema
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    environment: str
    features: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Export commonly used schemas
__all__ = [
    "SeverityLevel",
    "CareSetting", 
    "EvidenceLevel",
    "BaseResponse",
    "ClinicalDecisionRequest",
    "ClinicalDecisionResponse",
    "RiskAssessmentRequest",
    "RiskAssessmentResponse",
    "SBARRequest",
    "SBARResponse",
    "LiteratureSearchRequest",
    "LiteratureSearchResponse",
    "PatientEducationRequest",
    "PatientEducationResponse",
    "WizardStepRequest",
    "WizardStepResponse",
    "PaginationRequest",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthCheckResponse"
]
