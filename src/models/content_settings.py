"""
Content Settings Models
FHIR-ready database models for settings-based content reuse

Tables:
- FacilitySettings: Facility-wide settings shared by all nurses
- WorkSettingPreset: Pre-configured content for specific work environments
- PersonalContentLibrary: User's personal saved content and preferences
- DiagnosisContentMap: System-wide diagnosis library with FHIR codes
- MedlinePlusCache: Cached patient education content from MedlinePlus API
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List, Dict

Base = declarative_base()


class FacilitySettings(Base):
    """
    Facility-wide settings (shared by all nurses at facility)

    Stores non-PHI facility information that can be reused across all documents
    """
    __tablename__ = "facility_settings"

    facility_id = Column(String(50), primary_key=True)
    facility_name = Column(String(200), nullable=False)

    # Contact information
    main_phone = Column(String(20))
    after_hours_phone = Column(String(20))
    patient_portal_url = Column(String(200))
    address = Column(Text)

    # Standard content
    standard_follow_up_instructions = Column(JSON)  # List[str]
    standard_emergency_criteria = Column(JSON)  # List[str]
    hipaa_disclaimer = Column(Text)

    # Facility logo for documents (file path or URL)
    logo_path = Column(String(500))

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkSettingPreset(Base):
    """
    Pre-configured content for specific work settings

    Contains common content for ED, ICU, Community Clinic, etc.
    Helps nurses quickly populate documents based on their work environment
    """
    __tablename__ = "work_setting_presets"

    id = Column(String(50), primary_key=True)
    work_setting = Column(String(50), index=True, nullable=False)  # ED, ICU, etc.

    # Common content for this setting
    common_warning_signs = Column(JSON)  # List[str]
    common_medications = Column(JSON)  # List[Dict] with RxNorm codes
    common_diagnoses = Column(JSON)  # List[str] with ICD-10 codes
    common_activity_restrictions = Column(JSON)  # List[str]
    common_diet_instructions = Column(JSON)  # List[str]

    # Defaults
    default_follow_up_timeframe = Column(String(50))  # "7-10 days"
    default_reading_level = Column(String(20))  # "basic", "intermediate", "advanced"
    default_language = Column(String(10))  # "en", "es", "zh-CN"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PersonalContentLibrary(Base):
    """
    User's personal saved content and preferences

    Stores nurse's favorite phrases, templates, and usage patterns
    NO PATIENT DATA - only nurse preferences and reusable content
    """
    __tablename__ = "personal_content_library"

    # Foreign key to users table (relaxed for development, enforced in production via migration)
    user_id = Column(String(50), primary_key=True)

    # Favorite phrases (learned from usage)
    favorite_warning_signs = Column(JSON, default=list)  # List[str]
    favorite_medication_instructions = Column(JSON, default=list)  # List[str]
    favorite_follow_up_phrases = Column(JSON, default=list)  # List[str]
    favorite_activity_restrictions = Column(JSON, default=list)  # List[str]

    # Custom templates
    custom_discharge_templates = Column(JSON, default=list)  # List[Dict]
    custom_medication_templates = Column(JSON, default=list)  # List[Dict]

    # Usage tracking (for learning - NO PHI)
    most_used_diagnoses = Column(JSON, default=list)  # List[Dict] with frequency
    most_used_medications = Column(JSON, default=list)  # List[Dict] with frequency

    # ❌ NO PATIENT DATA EVER STORED HERE
    # Only reusable content and nurse preferences

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiagnosisContentMap(Base):
    """
    System-wide diagnosis library with FHIR codes

    Maps diagnoses to standard content with ICD-10 and SNOMED codes
    Epic/EHR Integration Ready: Uses FHIR-standard coding systems
    """
    __tablename__ = "diagnosis_content_map"

    id = Column(String(50), primary_key=True)

    # FHIR-aligned clinical codes
    icd10_code = Column(String(10), unique=True, index=True, nullable=False)  # "E11.9"
    snomed_code = Column(String(20), index=True)  # "44054006" (Epic primary coding)
    diagnosis_display = Column(String(200), index=True, nullable=False)  # "Type 2 Diabetes Mellitus"

    # Legacy field for backwards compatibility
    diagnosis_name = Column(String(200))  # Kept for existing code

    # Aliases for search (common variations)
    diagnosis_aliases = Column(JSON, default=list)  # List[str]: ["diabetes type 2", "T2DM", "DM2"]

    # Standard content
    standard_warning_signs = Column(JSON)  # List[str]
    standard_medications = Column(JSON)  # List[Dict] with RxNorm codes
    standard_activity_restrictions = Column(JSON)  # List[str]
    standard_diet_instructions = Column(Text)
    standard_follow_up_instructions = Column(Text)

    # Educational content for patients
    patient_education_key_points = Column(JSON)  # List[str]
    patient_education_urls = Column(JSON)  # List[str] - MedlinePlus, etc.
    patient_friendly_description = Column(Text)  # Grade 6-8 reading level explanation

    # Clinical metadata
    is_chronic_condition = Column(Boolean, default=False)
    requires_specialist_followup = Column(Boolean, default=False)
    typical_followup_days = Column(Integer)  # 7, 14, 30, etc.

    # Usage statistics (for popularity/recommendations)
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MedicationContentMap(Base):
    """
    System-wide medication library with RxNorm codes

    Standard medication instructions and safety information
    Epic/EHR Integration Ready: Uses RxNorm coding system
    """
    __tablename__ = "medication_content_map"

    id = Column(String(50), primary_key=True)

    # FHIR-aligned medication codes
    rxnorm_code = Column(String(20), unique=True, index=True)  # "860975" (Metformin)
    medication_display = Column(String(200), index=True, nullable=False)  # "Metformin"
    generic_name = Column(String(200), index=True)  # Generic name if brand
    brand_names = Column(JSON, default=list)  # List[str] of brand names

    # Standard instructions
    standard_instructions = Column(JSON)  # List[str]: ["Take with food", "Complete full course"]
    common_dosages = Column(JSON)  # List[Dict]: [{"value": "500", "unit": "mg"}]
    common_frequencies = Column(JSON)  # List[Dict]: [{"code": "BID", "display": "Twice daily"}]
    routes = Column(JSON)  # List[str]: ["oral", "IV", "topical"]

    # Safety information
    common_side_effects = Column(JSON)  # List[str]
    serious_warnings = Column(JSON)  # List[str]
    contraindications = Column(JSON)  # List[str]
    food_interactions = Column(JSON)  # List[str]
    drug_interactions = Column(JSON)  # List[str]

    # Patient instructions
    missed_dose_instructions = Column(Text)
    storage_instructions = Column(Text)

    # Educational resources
    patient_education_url = Column(String(500))  # Link to MedlinePlus or FDA

    # Usage statistics
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Helper functions for FHIR code lookups

def search_diagnosis_by_icd10(session, icd10_code: str) -> Optional[DiagnosisContentMap]:
    """Find diagnosis by ICD-10 code"""
    return session.query(DiagnosisContentMap).filter_by(icd10_code=icd10_code).first()


def search_diagnosis_by_snomed(session, snomed_code: str) -> Optional[DiagnosisContentMap]:
    """Find diagnosis by SNOMED code (Epic primary)"""
    return session.query(DiagnosisContentMap).filter_by(snomed_code=snomed_code).first()


def search_medication_by_rxnorm(session, rxnorm_code: str) -> Optional[MedicationContentMap]:
    """Find medication by RxNorm code"""
    return session.query(MedicationContentMap).filter_by(rxnorm_code=rxnorm_code).first()


def search_diagnosis_by_name(session, search_term: str) -> List[DiagnosisContentMap]:
    """Fuzzy search diagnosis by name or alias"""
    search_pattern = f"%{search_term.lower()}%"
    return session.query(DiagnosisContentMap).filter(
        DiagnosisContentMap.diagnosis_display.ilike(search_pattern)
    ).limit(20).all()


class MedlinePlusCache(Base):
    """
    Cache for MedlinePlus patient education content.

    Stores fetched content from MedlinePlus Connect API to reduce API calls
    and improve performance. Content refreshed every 24 hours.
    """
    __tablename__ = "medlineplus_cache"

    icd10_code = Column(String(10), primary_key=True)
    language = Column(String(10), primary_key=True, default="en")  # "en" or "es"

    # Content from MedlinePlus
    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    summary = Column(Text)

    # Metadata
    cached_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "icd10_code": self.icd10_code,
            "language": self.language,
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "cached_at": self.cached_at.isoformat() if self.cached_at else None
        }
