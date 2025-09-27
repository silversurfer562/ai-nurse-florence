"""
Pydantic schemas for AI Nurse Florence
Input/output validation with clinical context
"""

from pydantic import BaseModel, Field, field_validator
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
    
    @field_validator('patient_condition')
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
    
    @field_validator('situation', 'background', 'assessment', 'recommendation')
    def validate_sbar_fields(cls, v, info):
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

# SBAR Wizard Schemas
class SBARStep(BaseModel):
    """SBAR wizard step configuration."""
    step_number: int = Field(..., ge=1, le=4, description="Step number (1-4)")
    step_name: str = Field(..., description="SBAR step name (Situation, Background, Assessment, Recommendation)")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description")
    prompts: List[str] = Field(default_factory=list, description="Guiding questions")
    fields: List[Dict[str, Any]] = Field(default_factory=list, description="Form fields for this step")

class SBARWizardRequest(BaseModel):
    """SBAR wizard step submission."""
    step_number: int = Field(..., ge=1, le=4, description="Current step number")
    data: Dict[str, Any] = Field(..., description="Step data collected from user")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "step_number": 1,
                "data": {
                    "patient_condition": "Patient experiencing chest pain and shortness of breath",
                    "immediate_concerns": "Possible cardiac event, patient appears distressed",
                    "vital_signs": "BP: 180/95, HR: 110, RR: 22, O2 Sat: 92%"
                }
            }
        }
    }

class WizardSession(BaseModel):
    """Wizard session state."""
    wizard_id: str = Field(..., description="Unique wizard session ID")
    wizard_type: str = Field(..., description="Type of wizard (sbar, treatment_plan, etc.)")
    current_step: Union[int, str] = Field(..., description="Current step number or 'complete'")
    total_steps: int = Field(..., description="Total number of steps")
    collected_data: Dict[str, Any] = Field(default_factory=dict, description="Collected step data")
    created_at: str = Field(..., description="Session creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    completed_at: Optional[str] = Field(None, description="Completion timestamp")
    final_report: Optional[Dict[str, Any]] = Field(None, description="Final generated report")

class SBARWizardResponse(BaseResponse):
    """SBAR wizard response."""
    wizard_session: WizardSession = Field(..., description="Current wizard session state")
    current_step: Optional[SBARStep] = Field(None, description="Current step data")
    progress: Dict[str, Any] = Field(default_factory=dict, description="Progress information")
    sbar_report: Optional[Dict[str, Any]] = Field(None, description="Completed SBAR report")

class SBARReport(BaseModel):
    """Complete SBAR report."""
    report_type: str = Field(default="SBAR", description="Report type")
    generated_at: str = Field(..., description="Generation timestamp")
    banner: str = Field(..., description="Educational disclaimer")
    
    # SBAR Sections
    sections: Dict[str, Any] = Field(default_factory=dict, description="SBAR section data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Report metadata")
    
    # Generated content
    summary: Optional[str] = Field(None, description="Executive summary")
    enhanced_content: Optional[Dict[str, Any]] = Field(None, description="AI-enhanced content")

# Update model resolution for forward references
SBARWizardResponse.model_rebuild()

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
    "HealthCheckResponse",
    "SBARStep",
    "SBARWizardRequest",
    "SBARWizardResponse",
    "WizardSession",
    "SBARReport"
]
