"""
Patient Document Schemas for PDF Generation
Supports discharge instructions, medication guides, and disease education materials

FHIR Integration Ready:
- Uses HL7 FHIR R4 naming conventions for Epic/EHR integration
- Supports both standalone (manual entry) and Epic-integrated modes
- All patient data fields aligned with FHIR resources (Patient, Condition, MedicationRequest, Encounter)
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported languages for patient documents"""
    ENGLISH = "en"
    SPANISH = "es"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"


class ReadingLevel(str, Enum):
    """Patient reading level for content adaptation"""
    BASIC = "basic"  # 4th-6th grade
    INTERMEDIATE = "intermediate"  # 7th-9th grade
    ADVANCED = "advanced"  # 10th+ grade


class DocumentFormat(str, Enum):
    """Output format for generated documents"""
    PDF = "pdf"
    HTML = "html"
    TEXT = "text"
    DOCX = "docx"  # Microsoft Word


# ============================================================================
# FHIR-Aligned Models (Epic Integration Ready)
# ============================================================================

class FHIRPatientIdentifier(BaseModel):
    """
    FHIR-aligned patient identification
    Maps to FHIR Resource: Patient
    """
    patient_fhir_id: Optional[str] = Field(None, description="Epic Patient FHIR ID (future)")
    patient_mrn: Optional[str] = Field(None, description="Medical Record Number")
    patient_given_name: Optional[str] = Field(None, description="First name (FHIR: Patient.name.given)")
    patient_family_name: Optional[str] = Field(None, description="Last name (FHIR: Patient.name.family)")

    @property
    def full_name(self) -> Optional[str]:
        """Convenience property for display"""
        if self.patient_given_name and self.patient_family_name:
            return f"{self.patient_given_name} {self.patient_family_name}"
        return None

    class Config:
        json_schema_extra = {
            "example": {
                "patient_mrn": "12345678",
                "patient_given_name": "John",
                "patient_family_name": "Smith"
            }
        }


class FHIRCondition(BaseModel):
    """
    FHIR-aligned diagnosis/condition
    Maps to FHIR Resource: Condition
    """
    condition_fhir_id: Optional[str] = Field(None, description="Epic Condition FHIR ID (future)")
    condition_code_icd10: str = Field(..., description="ICD-10 code (e.g., E11.9)")
    condition_code_snomed: Optional[str] = Field(None, description="SNOMED CT code (Epic primary)")
    condition_display: str = Field(..., description="Human-readable diagnosis")
    condition_clinical_status: str = Field(default="active", description="active | resolved | inactive")

    class Config:
        json_schema_extra = {
            "example": {
                "condition_code_icd10": "E11.9",
                "condition_code_snomed": "44054006",
                "condition_display": "Type 2 Diabetes Mellitus",
                "condition_clinical_status": "active"
            }
        }


class FHIRMedicationRequest(BaseModel):
    """
    FHIR-aligned medication order
    Maps to FHIR Resource: MedicationRequest
    """
    medication_fhir_id: Optional[str] = Field(None, description="Epic MedicationRequest FHIR ID (future)")
    medication_code_rxnorm: Optional[str] = Field(None, description="RxNorm code")
    medication_display: str = Field(..., description="Medication name")
    dosage_value: str = Field(..., description="Dose amount (e.g., '500')")
    dosage_unit: str = Field(..., description="Dose unit (e.g., 'mg')")
    frequency_code: str = Field(..., description="Timing code (e.g., 'BID', 'QID')")
    frequency_display: str = Field(..., description="Human-readable frequency")
    route: Optional[str] = Field(default="oral", description="Route of administration")
    instructions: Optional[str] = Field(None, description="Patient instructions")
    prescriber_npi: Optional[str] = Field(None, description="Prescriber NPI (future)")

    class Config:
        json_schema_extra = {
            "example": {
                "medication_code_rxnorm": "860975",
                "medication_display": "Metformin",
                "dosage_value": "500",
                "dosage_unit": "mg",
                "frequency_code": "BID",
                "frequency_display": "Twice daily",
                "route": "oral",
                "instructions": "Take with food"
            }
        }


class FHIREncounter(BaseModel):
    """
    FHIR-aligned encounter context
    Maps to FHIR Resource: Encounter
    """
    encounter_fhir_id: Optional[str] = Field(None, description="Epic Encounter FHIR ID (future)")
    encounter_type_code: Optional[str] = Field(None, description="Encounter type code")
    encounter_type_display: Optional[str] = Field(None, description="ED | Inpatient | Outpatient")
    encounter_start: Optional[datetime] = Field(None, description="Encounter start time")
    encounter_end: Optional[datetime] = Field(None, description="Encounter end time")

    class Config:
        json_schema_extra = {
            "example": {
                "encounter_type_code": "EMER",
                "encounter_type_display": "Emergency",
                "encounter_start": "2024-01-15T08:30:00Z",
                "encounter_end": "2024-01-15T12:45:00Z"
            }
        }


# ============================================================================
# Discharge Instructions (FHIR-Enhanced)
# ============================================================================

class DischargeInstructionsFHIR(BaseModel):
    """
    FHIR-aligned discharge instructions request

    Use this model when Epic integration is enabled or for future compatibility.
    Falls back gracefully to manual entry in standalone mode.
    """
    # Patient identification (FHIR-aligned)
    patient: FHIRPatientIdentifier

    # Clinical context (FHIR-aligned)
    primary_diagnosis: FHIRCondition
    secondary_diagnoses: List[FHIRCondition] = Field(default=[], description="Additional diagnoses")
    medications: List[FHIRMedicationRequest] = Field(default=[], description="Prescribed medications")
    encounter: Optional[FHIREncounter] = Field(None, description="Encounter context (ED visit, etc.)")

    # Discharge-specific content
    warning_signs: List[str] = Field(..., description="Warning signs to watch for")
    emergency_criteria: List[str] = Field(..., description="When to call 911")
    activity_restrictions: List[str] = Field(default=[], description="Activity limitations")
    diet_instructions: Optional[str] = Field(None, description="Dietary guidance")
    follow_up_instructions: str = Field(..., description="Follow-up care instructions")
    wound_care: Optional[str] = Field(None, description="Wound care if applicable")
    equipment_needs: List[str] = Field(default=[], description="DME or supplies needed")

    # Localization
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Document language")
    reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")
    format: DocumentFormat = Field(default=DocumentFormat.PDF, description="Output format")

    class Config:
        json_schema_extra = {
            "example": {
                "patient": {
                    "patient_mrn": "12345678",
                    "patient_given_name": "John",
                    "patient_family_name": "Smith"
                },
                "primary_diagnosis": {
                    "condition_code_icd10": "E11.9",
                    "condition_display": "Type 2 Diabetes Mellitus"
                },
                "medications": [
                    {
                        "medication_display": "Metformin",
                        "dosage_value": "500",
                        "dosage_unit": "mg",
                        "frequency_code": "BID",
                        "frequency_display": "Twice daily",
                        "instructions": "Take with food"
                    }
                ],
                "warning_signs": ["Blood sugar over 300", "Severe confusion"],
                "emergency_criteria": ["Loss of consciousness", "Chest pain"],
                "follow_up_instructions": "See your primary care doctor in 1 week"
            }
        }


# ============================================================================
# Legacy Discharge Instructions (Backward Compatibility)
# ============================================================================

class DischargeInstructionsRequest(BaseModel):
    """Request model for discharge instructions"""
    patient_name: Optional[str] = Field(None, description="Patient name (optional for privacy)")
    discharge_date: Optional[datetime] = Field(default_factory=datetime.now, description="Date of discharge")
    primary_diagnosis: str = Field(..., description="Primary diagnosis or reason for visit")

    # Medications
    medications: List[Dict[str, str]] = Field(
        default=[],
        description="List of medications with name, dosage, frequency, and instructions"
    )

    # Follow-up care
    follow_up_appointments: List[str] = Field(
        default=[],
        description="Follow-up appointments (e.g., 'See your primary care doctor in 7-10 days')"
    )

    # Activity restrictions
    activity_restrictions: List[str] = Field(
        default=[],
        description="Activity restrictions (e.g., 'No heavy lifting for 2 weeks')"
    )

    # Diet instructions
    diet_instructions: Optional[str] = Field(None, description="Special diet instructions")

    # Warning signs
    warning_signs: List[str] = Field(
        ...,
        description="Warning signs to watch for that require immediate medical attention"
    )

    # Emergency contact criteria
    emergency_criteria: List[str] = Field(
        ...,
        description="When to call 911 or go to emergency room"
    )

    # Additional instructions
    wound_care: Optional[str] = Field(None, description="Wound care instructions if applicable")
    equipment_needs: List[str] = Field(default=[], description="Medical equipment needed at home")
    home_care_services: Optional[str] = Field(None, description="Home health or other services arranged")

    # Document settings
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Language for document")
    reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")
    include_diagrams: bool = Field(default=False, description="Include visual diagrams if available")
    format: DocumentFormat = Field(default=DocumentFormat.PDF, description="Output format")


class DischargeInstructionsResponse(BaseModel):
    """Response model for discharge instructions"""
    success: bool
    document_type: str = "discharge_instructions"
    file_path: Optional[str] = None
    file_content: Optional[bytes] = None
    content_type: str = "application/pdf"
    filename: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ============================================================================
# Medication Guide
# ============================================================================

class MedicationGuideRequest(BaseModel):
    """Request model for medication guide"""
    medication_name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Prescribed dosage (e.g., '10 mg')")
    frequency: str = Field(..., description="How often to take (e.g., 'twice daily')")
    route: str = Field(default="oral", description="Route of administration")

    # Instructions
    special_instructions: List[str] = Field(
        default=[],
        description="Special instructions (e.g., 'Take with food', 'Take on empty stomach')"
    )

    # What to expect
    purpose: Optional[str] = Field(None, description="Why patient is taking this medication")
    how_it_works: Optional[str] = Field(None, description="Simple explanation of how medication works")

    # Side effects
    common_side_effects: List[str] = Field(default=[], description="Common side effects")
    serious_side_effects: List[str] = Field(default=[], description="Serious side effects requiring medical attention")

    # Interactions
    food_interactions: List[str] = Field(default=[], description="Foods to avoid")
    drug_interactions: List[str] = Field(default=[], description="Other medications that may interact")

    # Storage and handling
    storage_instructions: Optional[str] = Field(
        default="Store at room temperature away from moisture and heat",
        description="How to store medication"
    )

    # Missed dose
    missed_dose_instructions: Optional[str] = Field(
        default="Take as soon as you remember. If it's almost time for the next dose, skip the missed dose.",
        description="What to do if a dose is missed"
    )

    # Document settings
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Language for document")
    reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")
    include_images: bool = Field(default=False, description="Include medication images if available")
    auto_populate: bool = Field(
        default=True,
        description="Auto-populate information from FDA database if available"
    )
    format: DocumentFormat = Field(default=DocumentFormat.PDF, description="Output format")


class MedicationGuideResponse(BaseModel):
    """Response model for medication guide"""
    success: bool
    document_type: str = "medication_guide"
    file_path: Optional[str] = None
    file_content: Optional[bytes] = None
    content_type: str = "application/pdf"
    filename: str
    data_sources: List[str] = Field(
        default=[],
        description="Sources used to generate guide (FDA, OpenFDA, etc.)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ============================================================================
# Disease Education Material
# ============================================================================

class DiseaseEducationRequest(BaseModel):
    """Request model for disease education material"""
    disease_name: str = Field(..., description="Disease or condition name")

    # Core content
    what_it_is: Optional[str] = Field(None, description="Simple explanation of the disease")
    causes: Optional[str] = Field(None, description="What causes this condition")
    symptoms: List[str] = Field(default=[], description="Common symptoms to watch for")

    # Management
    treatment_options: List[str] = Field(default=[], description="Available treatment options")
    self_care_tips: List[str] = Field(default=[], description="Self-care and lifestyle modifications")
    medications_overview: Optional[str] = Field(None, description="Overview of typical medications used")

    # Living with condition
    lifestyle_modifications: List[str] = Field(default=[], description="Lifestyle changes that can help")
    diet_recommendations: Optional[str] = Field(None, description="Dietary recommendations")
    exercise_recommendations: Optional[str] = Field(None, description="Exercise and activity recommendations")

    # When to seek help
    warning_signs: List[str] = Field(default=[], description="Warning signs requiring medical attention")
    emergency_symptoms: List[str] = Field(default=[], description="Emergency symptoms requiring immediate care")

    # Support and resources
    support_groups: List[str] = Field(default=[], description="Support groups or resources")
    additional_resources: List[str] = Field(default=[], description="Websites, apps, or other resources")

    # Questions for doctor
    questions_to_ask: List[str] = Field(
        default=[],
        description="Suggested questions patients should ask their healthcare provider"
    )

    # Document settings
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Language for document")
    reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level")
    include_diagrams: bool = Field(default=True, description="Include anatomical diagrams if available")
    auto_populate: bool = Field(
        default=True,
        description="Auto-populate from MedlinePlus and disease databases"
    )
    format: DocumentFormat = Field(default=DocumentFormat.PDF, description="Output format")


class DiseaseEducationResponse(BaseModel):
    """Response model for disease education material"""
    success: bool
    document_type: str = "disease_education"
    file_path: Optional[str] = None
    file_content: Optional[bytes] = None
    content_type: str = "application/pdf"
    filename: str
    data_sources: List[str] = Field(
        default=[],
        description="Sources used (MedlinePlus, MONDO, PubMed, etc.)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ============================================================================
# Pre-Visit Questionnaire
# ============================================================================

class PreVisitQuestionnaireRequest(BaseModel):
    """Request model for pre-visit questionnaire"""
    visit_type: str = Field(..., description="Type of visit (annual checkup, specialty, follow-up)")
    specialty: Optional[str] = Field(None, description="Medical specialty if applicable")

    # Sections to include
    include_medical_history: bool = Field(default=True, description="Include medical history section")
    include_medications: bool = Field(default=True, description="Include current medications section")
    include_allergies: bool = Field(default=True, description="Include allergies section")
    include_family_history: bool = Field(default=True, description="Include family history section")
    include_social_history: bool = Field(default=True, description="Include social history section")
    include_symptoms: bool = Field(default=True, description="Include current symptoms section")
    include_pain_scale: bool = Field(default=False, description="Include pain assessment")
    include_functional_status: bool = Field(default=False, description="Include activities of daily living")

    # Custom questions
    custom_questions: List[str] = Field(default=[], description="Additional custom questions")

    # Document settings
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Language for document")
    reading_level: ReadingLevel = Field(default=ReadingLevel.BASIC, description="Target reading level")
    format: DocumentFormat = Field(default=DocumentFormat.PDF, description="Output format")


class PreVisitQuestionnaireResponse(BaseModel):
    """Response model for pre-visit questionnaire"""
    success: bool
    document_type: str = "pre_visit_questionnaire"
    file_path: Optional[str] = None
    file_content: Optional[bytes] = None
    content_type: str = "application/pdf"
    filename: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


# ============================================================================
# Batch Document Generation
# ============================================================================

class BatchDocumentRequest(BaseModel):
    """Request model for generating multiple documents at once"""
    patient_name: Optional[str] = Field(None, description="Patient name")

    # Document types to generate
    discharge_instructions: Optional[DischargeInstructionsRequest] = None
    medication_guides: List[MedicationGuideRequest] = Field(default=[], description="Multiple medication guides")
    disease_education: List[DiseaseEducationRequest] = Field(default=[], description="Multiple disease education materials")

    # Settings
    language: LanguageCode = Field(default=LanguageCode.ENGLISH, description="Language for all documents")
    reading_level: ReadingLevel = Field(default=ReadingLevel.INTERMEDIATE, description="Target reading level for all")
    combine_into_packet: bool = Field(
        default=True,
        description="Combine all documents into a single PDF packet"
    )


class BatchDocumentResponse(BaseModel):
    """Response model for batch document generation"""
    success: bool
    documents_generated: int
    file_path: Optional[str] = None  # Path to combined packet if combine_into_packet=True
    individual_documents: List[Dict[str, Any]] = Field(
        default=[],
        description="List of individual document responses if combine_into_packet=False"
    )
    file_content: Optional[bytes] = None
    content_type: str = "application/pdf"
    filename: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default=[], description="Any errors encountered")
