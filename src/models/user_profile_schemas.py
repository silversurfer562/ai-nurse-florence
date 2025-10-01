"""
User Profile Schemas for Personalization and Document Generation
Supports flexible patient-centered document generation based on work setting
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class NurseCredential(str, Enum):
    """Nursing credentials and certifications"""
    CNA = "CNA"  # Certified Nursing Assistant
    LPN = "LPN"  # Licensed Practical Nurse
    LVN = "LVN"  # Licensed Vocational Nurse
    RN = "RN"    # Registered Nurse
    BSN = "BSN"  # Bachelor of Science in Nursing
    MSN = "MSN"  # Master of Science in Nursing
    NP = "NP"    # Nurse Practitioner
    CNS = "CNS"  # Clinical Nurse Specialist
    CRNA = "CRNA"  # Certified Registered Nurse Anesthetist
    CNM = "CNM"  # Certified Nurse Midwife
    DNP = "DNP"  # Doctor of Nursing Practice
    PhD = "PhD"  # PhD in Nursing


class WorkSetting(str, Enum):
    """Healthcare work settings that influence default document preferences"""
    # Hospital Units
    EMERGENCY_DEPARTMENT = "emergency_department"
    INTENSIVE_CARE = "intensive_care"
    MED_SURG = "medical_surgical"
    PEDIATRICS = "pediatrics"
    NICU = "nicu"
    LABOR_DELIVERY = "labor_delivery"
    ONCOLOGY = "oncology"
    CARDIOLOGY = "cardiology"
    SURGERY = "surgery"
    REHABILITATION = "rehabilitation"
    MENTAL_HEALTH = "mental_health"

    # Outpatient Settings
    COMMUNITY_CLINIC = "community_clinic"
    PRIMARY_CARE = "primary_care"
    SPECIALTY_CLINIC = "specialty_clinic"
    URGENT_CARE = "urgent_care"

    # Long-term Care
    SKILLED_NURSING = "skilled_nursing_facility"
    ASSISTED_LIVING = "assisted_living"
    HOME_HEALTH = "home_health"
    HOSPICE = "hospice"

    # Academic/Research
    ACADEMIC_MEDICAL_CENTER = "academic_medical_center"
    RESEARCH_HOSPITAL = "research_hospital"

    # Rural/Underserved
    RURAL_HOSPITAL = "rural_hospital"
    FEDERALLY_QUALIFIED = "fqhc"  # Federally Qualified Health Center

    # Other
    SCHOOL_NURSING = "school_nursing"
    OCCUPATIONAL_HEALTH = "occupational_health"
    PUBLIC_HEALTH = "public_health"
    OTHER = "other"


class PatientPopulation(str, Enum):
    """Description of typical patient population"""
    LOW_HEALTH_LITERACY = "low_health_literacy"
    MIXED_LITERACY = "mixed_literacy"
    HIGH_HEALTH_LITERACY = "high_health_literacy"
    PEDIATRIC = "pediatric"
    GERIATRIC = "geriatric"
    NON_ENGLISH_PRIMARY = "non_english_primary"
    ACUTE_CRITICAL = "acute_critical"
    CHRONIC_CARE = "chronic_care"


class LanguageCode(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    SPANISH = "es"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    VIETNAMESE = "vi"
    TAGALOG = "tl"
    KOREAN = "ko"
    ARABIC = "ar"
    FRENCH = "fr"
    HAITIAN_CREOLE = "ht"


class ReadingLevel(str, Enum):
    """Patient reading level for documents"""
    BASIC = "basic"  # 4th-6th grade
    INTERMEDIATE = "intermediate"  # 7th-9th grade
    ADVANCED = "advanced"  # 10th+ grade


class DocumentPermissionLevel(str, Enum):
    """What documents a user can generate based on credentials"""
    BASIC = "basic"  # CNAs - basic care instructions
    STANDARD = "standard"  # LPN/LVN - most patient education
    FULL = "full"  # RN+ - all documents including legal
    ADVANCED = "advanced"  # NP/CNS/CRNA/CNM - provider-level documents


# ============================================================================
# User Profile Models
# ============================================================================

class UserProfileCreate(BaseModel):
    """Request model for creating user profile"""
    full_name: str = Field(..., min_length=2, max_length=200, description="Full name")
    credentials: List[NurseCredential] = Field(
        default=[NurseCredential.RN],
        description="Nursing credentials (can have multiple)"
    )
    primary_credential: NurseCredential = Field(
        default=NurseCredential.RN,
        description="Primary credential used for permissions"
    )

    # License Information
    license_number: Optional[str] = Field(None, max_length=50, description="Nursing license number")
    license_state: Optional[str] = Field(None, max_length=2, description="State of licensure (e.g., CA)")
    license_expiry: Optional[datetime] = Field(None, description="License expiration date")

    # Work Setting
    facility_name: str = Field(..., max_length=200, description="Hospital or facility name")
    work_setting: WorkSetting = Field(..., description="Primary work setting/unit")
    department: Optional[str] = Field(None, max_length=100, description="Specific department")
    patient_population: PatientPopulation = Field(
        default=PatientPopulation.MIXED_LITERACY,
        description="Typical patient population served"
    )

    # Contact Information
    work_phone: Optional[str] = Field(None, max_length=20, description="Work phone number")
    work_email: Optional[str] = Field(None, max_length=100, description="Work email address")

    # Document Preferences (Smart Defaults)
    default_patient_language: LanguageCode = Field(
        default=LanguageCode.ENGLISH,
        description="Default language for patient documents"
    )
    default_patient_reading_level: ReadingLevel = Field(
        default=ReadingLevel.INTERMEDIATE,
        description="Default reading level (auto-set based on work setting)"
    )
    secondary_languages: List[LanguageCode] = Field(
        default=[],
        description="Additional languages frequently needed"
    )


class UserProfileUpdate(BaseModel):
    """Request model for updating user profile"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    credentials: Optional[List[NurseCredential]] = None
    primary_credential: Optional[NurseCredential] = None
    license_number: Optional[str] = None
    license_state: Optional[str] = None
    license_expiry: Optional[datetime] = None
    facility_name: Optional[str] = None
    work_setting: Optional[WorkSetting] = None
    department: Optional[str] = None
    patient_population: Optional[PatientPopulation] = None
    work_phone: Optional[str] = None
    work_email: Optional[str] = None
    default_patient_language: Optional[LanguageCode] = None
    default_patient_reading_level: Optional[ReadingLevel] = None
    secondary_languages: Optional[List[LanguageCode]] = None


class SignatureUploadRequest(BaseModel):
    """Request model for uploading digital signature"""
    signature_data: str = Field(..., description="Base64-encoded signature image")
    format: str = Field(default="png", description="Image format (png, jpg)")


class UserProfileResponse(BaseModel):
    """Response model for user profile"""
    user_id: str
    full_name: str
    credentials: List[NurseCredential]
    primary_credential: NurseCredential
    permission_level: DocumentPermissionLevel

    license_number: Optional[str]
    license_state: Optional[str]
    license_expiry: Optional[datetime]
    license_status: str  # "active", "expired", "pending"

    facility_name: str
    work_setting: WorkSetting
    department: Optional[str]
    patient_population: PatientPopulation

    work_phone: Optional[str]
    work_email: Optional[str]

    # Document defaults
    default_patient_language: LanguageCode
    default_patient_reading_level: ReadingLevel
    secondary_languages: List[LanguageCode]

    # Signature
    has_signature: bool
    signature_url: Optional[str]

    # Stats
    documents_generated: int
    last_document_at: Optional[datetime]

    # Metadata
    created_at: datetime
    updated_at: datetime


class DocumentPreferences(BaseModel):
    """User's saved preferences for document generation"""
    # Last used settings (learn from user behavior)
    last_used_language: LanguageCode = LanguageCode.ENGLISH
    last_used_reading_level: ReadingLevel = ReadingLevel.INTERMEDIATE

    # Frequently used text snippets
    common_discharge_instructions: List[str] = Field(default=[], max_items=10)
    common_warning_signs: List[str] = Field(default=[], max_items=20)
    common_follow_up_instructions: List[str] = Field(default=[], max_items=10)

    # Template preferences
    include_facility_logo: bool = True
    include_qr_codes: bool = False
    default_copies: int = 1
    auto_print: bool = False


class DocumentPermissions(BaseModel):
    """What documents this user can generate based on credentials"""
    permission_level: DocumentPermissionLevel

    # Patient Education Documents
    can_generate_discharge_instructions: bool
    can_generate_medication_guides: bool
    can_generate_disease_education: bool

    # Legal Documents
    can_generate_incident_reports: bool
    can_generate_ama_documentation: bool
    can_generate_witness_statements: bool

    # Clinical Documents
    can_generate_sbar_reports: bool
    can_generate_care_plans: bool
    can_generate_assessment_notes: bool

    # Advanced Documents (NP/Provider level)
    can_generate_treatment_plans: bool
    can_generate_prescriptions: bool
    can_order_diagnostics: bool

    # Co-signature requirements
    requires_cosign: bool
    can_cosign_for_others: bool

    # Template management
    can_create_templates: bool
    can_modify_templates: bool


# ============================================================================
# Smart Defaults Configuration
# ============================================================================

class WorkSettingDefaults(BaseModel):
    """Smart defaults based on work setting"""
    work_setting: WorkSetting
    recommended_reading_level: ReadingLevel
    recommended_languages: List[LanguageCode]
    common_document_types: List[str]
    typical_patient_needs: str


# Predefined smart defaults
WORK_SETTING_DEFAULTS = {
    WorkSetting.EMERGENCY_DEPARTMENT: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "High stress, time pressure, diverse literacy",
        "recommended_languages": [LanguageCode.ENGLISH, LanguageCode.SPANISH],
        "common_documents": ["discharge_instructions", "ama_documentation", "incident_reports"]
    },

    WorkSetting.COMMUNITY_CLINIC: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "Underserved populations, lower health literacy average",
        "recommended_languages": [LanguageCode.ENGLISH, LanguageCode.SPANISH],
        "common_documents": ["disease_education", "medication_guides", "preventive_care"]
    },

    WorkSetting.RURAL_HOSPITAL: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "Lower average education levels, limited health resources",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["discharge_instructions", "medication_guides"]
    },

    WorkSetting.ACADEMIC_MEDICAL_CENTER: {
        "recommended_reading_level": ReadingLevel.INTERMEDIATE,
        "reason": "Educated patient population, complex conditions",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["disease_education", "research_information", "complex_treatment_plans"]
    },

    WorkSetting.RESEARCH_HOSPITAL: {
        "recommended_reading_level": ReadingLevel.ADVANCED,
        "reason": "Highly educated patients, complex medical information",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["clinical_trial_information", "complex_disease_education"]
    },

    WorkSetting.PEDIATRICS: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "For parents/caregivers, need simple clear instructions",
        "recommended_languages": [LanguageCode.ENGLISH, LanguageCode.SPANISH],
        "common_documents": ["parent_education", "growth_development", "immunization_info"]
    },

    WorkSetting.SKILLED_NURSING: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "Geriatric patients, vision issues, cognitive changes, need clarity",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["medication_guides", "fall_prevention", "chronic_disease_management"]
    },

    WorkSetting.INTENSIVE_CARE: {
        "recommended_reading_level": ReadingLevel.INTERMEDIATE,
        "reason": "Families under stress, need clear but thorough information",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["family_updates", "critical_care_education", "prognosis_discussions"]
    },

    WorkSetting.ONCOLOGY: {
        "recommended_reading_level": ReadingLevel.INTERMEDIATE,
        "reason": "Patients often research extensively, need detailed info",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["treatment_options", "side_effect_management", "survivorship_care"]
    },

    WorkSetting.HOME_HEALTH: {
        "recommended_reading_level": ReadingLevel.BASIC,
        "reason": "Patients/family managing care independently",
        "recommended_languages": [LanguageCode.ENGLISH, LanguageCode.SPANISH],
        "common_documents": ["home_care_instructions", "equipment_use", "emergency_contacts"]
    },

    WorkSetting.MENTAL_HEALTH: {
        "recommended_reading_level": ReadingLevel.INTERMEDIATE,
        "reason": "Need clear, non-stigmatizing language",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["crisis_plan", "medication_management", "therapy_resources"]
    }
}


def get_smart_defaults(work_setting: WorkSetting) -> Dict:
    """Get recommended defaults based on work setting"""
    return WORK_SETTING_DEFAULTS.get(work_setting, {
        "recommended_reading_level": ReadingLevel.INTERMEDIATE,
        "reason": "Safe default for mixed populations",
        "recommended_languages": [LanguageCode.ENGLISH],
        "common_documents": ["discharge_instructions", "medication_guides"]
    })


def get_permission_level(primary_credential: NurseCredential) -> DocumentPermissionLevel:
    """Determine permission level based on primary credential"""
    if primary_credential in [NurseCredential.CNA]:
        return DocumentPermissionLevel.BASIC
    elif primary_credential in [NurseCredential.LPN, NurseCredential.LVN]:
        return DocumentPermissionLevel.STANDARD
    elif primary_credential in [NurseCredential.RN, NurseCredential.BSN, NurseCredential.MSN]:
        return DocumentPermissionLevel.FULL
    elif primary_credential in [NurseCredential.NP, NurseCredential.CNS, NurseCredential.CRNA,
                                  NurseCredential.CNM, NurseCredential.DNP, NurseCredential.PhD]:
        return DocumentPermissionLevel.ADVANCED
    else:
        return DocumentPermissionLevel.FULL  # Default to RN level


def get_document_permissions(permission_level: DocumentPermissionLevel) -> DocumentPermissions:
    """Get document permissions based on permission level"""

    if permission_level == DocumentPermissionLevel.BASIC:
        return DocumentPermissions(
            permission_level=permission_level,
            can_generate_discharge_instructions=False,
            can_generate_medication_guides=False,
            can_generate_disease_education=True,
            can_generate_incident_reports=False,
            can_generate_ama_documentation=False,
            can_generate_witness_statements=True,
            can_generate_sbar_reports=False,
            can_generate_care_plans=False,
            can_generate_assessment_notes=False,
            can_generate_treatment_plans=False,
            can_generate_prescriptions=False,
            can_order_diagnostics=False,
            requires_cosign=True,
            can_cosign_for_others=False,
            can_create_templates=False,
            can_modify_templates=False
        )

    elif permission_level == DocumentPermissionLevel.STANDARD:
        return DocumentPermissions(
            permission_level=permission_level,
            can_generate_discharge_instructions=True,
            can_generate_medication_guides=True,
            can_generate_disease_education=True,
            can_generate_incident_reports=True,
            can_generate_ama_documentation=False,  # Usually requires RN
            can_generate_witness_statements=True,
            can_generate_sbar_reports=True,
            can_generate_care_plans=True,
            can_generate_assessment_notes=True,
            can_generate_treatment_plans=False,
            can_generate_prescriptions=False,
            can_order_diagnostics=False,
            requires_cosign=False,
            can_cosign_for_others=False,
            can_create_templates=False,
            can_modify_templates=False
        )

    elif permission_level == DocumentPermissionLevel.FULL:
        return DocumentPermissions(
            permission_level=permission_level,
            can_generate_discharge_instructions=True,
            can_generate_medication_guides=True,
            can_generate_disease_education=True,
            can_generate_incident_reports=True,
            can_generate_ama_documentation=True,
            can_generate_witness_statements=True,
            can_generate_sbar_reports=True,
            can_generate_care_plans=True,
            can_generate_assessment_notes=True,
            can_generate_treatment_plans=False,  # Provider level
            can_generate_prescriptions=False,
            can_order_diagnostics=False,
            requires_cosign=False,
            can_cosign_for_others=True,
            can_create_templates=True,
            can_modify_templates=True
        )

    else:  # ADVANCED (NP, CNS, etc.)
        return DocumentPermissions(
            permission_level=permission_level,
            can_generate_discharge_instructions=True,
            can_generate_medication_guides=True,
            can_generate_disease_education=True,
            can_generate_incident_reports=True,
            can_generate_ama_documentation=True,
            can_generate_witness_statements=True,
            can_generate_sbar_reports=True,
            can_generate_care_plans=True,
            can_generate_assessment_notes=True,
            can_generate_treatment_plans=True,
            can_generate_prescriptions=True,
            can_order_diagnostics=True,
            requires_cosign=False,
            can_cosign_for_others=True,
            can_create_templates=True,
            can_modify_templates=True
        )
