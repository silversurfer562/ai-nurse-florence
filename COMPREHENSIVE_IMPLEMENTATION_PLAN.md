# Comprehensive Implementation Plan
## Settings-First Document Generation + Professional Templates

---

## 🎯 Project Goals

1. **Settings-based content reuse** - Save 80% of repetitive content
2. **Quick Create** - 2-3 clicks for routine documents
3. **Wizard for complex cases** - Step-by-step for unusual scenarios
4. **Professional Word templates** - Attractive, easy-to-edit documents
5. **In-app editing** - Edit before export (similar to SBAR)
6. **Multiple export formats** - PDF, Word (.docx), Plain text
7. **Zero patient data storage** - HIPAA-safe, session-only patient info
8. **Legal documentation** - Incident reports, AMA forms with signatures
9. **🏥 Epic/EHR Integration Ready** - FHIR-aligned architecture for future institutional deployment

---

## 🚨 CRITICAL: HIPAA & Data Privacy Rules

### **NEVER Store Patient Data**

```python
# ✅ ALLOWED TO SAVE (Non-PHI)
class UserSettings:
    nurse_name: str
    facility_name: str
    work_setting: str
    common_medications: List[str]
    common_warning_signs: List[str]
    favorite_phrases: List[str]
    custom_templates: List[Dict]

# ❌ NEVER SAVE (PHI - Protected Health Information)
class PatientData:
    patient_name: str  # ❌ Session only
    patient_id: str  # ❌ Session only
    diagnosis: str  # ❌ Session only
    medications_prescribed: List  # ❌ Session only
    any_clinical_information: Any  # ❌ Session only
```

### **Implementation Requirements**

```python
# 1. Session-only storage
session_data = {
    "patient_name": "John Smith",  # Deleted when session ends
    "expires_at": now + 2_hours,
    "auto_delete": True
}

# 2. Explicit clearing
@app.on_event("shutdown")
async def clear_patient_data():
    """Delete all patient data on server shutdown"""
    await session_store.clear_all_patient_data()

# 3. Frontend clearing
// Clear patient data on:
// - Document generation complete
// - User navigates away
// - Browser close
// - 2 hour timeout
window.addEventListener('beforeunload', clearPatientData);

# 4. Database constraints
CREATE TABLE user_settings (
    -- NO patient data columns allowed
    -- Only nurse/facility/template data
);

# 5. Audit logging (log access, not data)
audit_log = {
    "user_id": "nurse_123",
    "action": "generated_discharge_instructions",
    "timestamp": now,
    "patient_identifier": None  # ❌ DO NOT LOG
}
```

---

## 🏥 EPIC/EHR INTEGRATION STRATEGY

### **Future-Ready Architecture**

The system is designed for **TWO operational modes**:

**Mode 1: Standalone** (Current Implementation)
- Manual data entry by nurses
- Session-only patient data storage
- No EHR connection required
- Perfect for: Community clinics, small practices, ChatGPT enterprise deployment

**Mode 2: Epic-Integrated** (Future Version)
- Real-time patient data from Epic FHIR API
- Scan patient wristband → Auto-populate form
- Write discharge instructions back to Epic chart
- Perfect for: Hospital systems, large health networks

### **FHIR Alignment Benefits**

All data models use **HL7 FHIR** (Fast Healthcare Interoperability Resources) naming conventions:

```python
# FHIR Resources We'll Integrate With (Future):
- Patient (demographics, MRN)
- Encounter (visit type, location)
- Condition (diagnoses with ICD-10/SNOMED codes)
- MedicationRequest (prescriptions with RxNorm codes)
- DocumentReference (write discharge notes to Epic chart)
```

**Key Principle:** FHIR-aligned naming NOW = Zero schema changes when Epic integration activates

### **Integration Workflow (Future)**

```
Standalone Mode (Current):          Epic-Integrated Mode (Future):
┌─────────────────────┐             ┌─────────────────────┐
│ Nurse enters data   │             │ Scan patient MRN    │
│ manually in forms   │             │ barcode             │
└──────────┬──────────┘             └──────────┬──────────┘
           │                                   │
           ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│ Generate document   │             │ Fetch from Epic     │
│ (session only)      │             │ FHIR API            │
└──────────┬──────────┘             └──────────┬──────────┘
           │                                   │
           ▼                                   ▼
┌─────────────────────┐             ┌─────────────────────┐
│ Export PDF/Word     │             │ Pre-populate form   │
│                     │             │ (name, meds, dx)    │
└─────────────────────┘             └──────────┬──────────┘
                                              │
                                              ▼
                                    ┌─────────────────────┐
                                    │ Nurse reviews/edits │
                                    │                     │
                                    └──────────┬──────────┘
                                              │
                                              ▼
                                    ┌─────────────────────┐
                                    │ Generate & Export   │
                                    │                     │
                                    └──────────┬──────────┘
                                              │
                                              ▼
                                    ┌─────────────────────┐
                                    │ Write to Epic chart │
                                    │ as DocumentReference│
                                    └─────────────────────┘
```

**Privacy Note:** Even with Epic integration, patient data remains session-only in our app. We just READ from Epic, process in memory, and WRITE back to Epic. Nothing persisted in our database.

---

## 📅 PHASED IMPLEMENTATION PLAN

---

## **PHASE 0: Epic/FHIR Readiness** (Days 1-2)

### **Sprint 0.1: FHIR-Aligned Data Models**

**Goal:** Update all schemas to use FHIR-compatible field naming and add integration configuration.

#### **0.1.1 Integration Mode Configuration**
```python
# src/config.py (NEW FILE)

from enum import Enum
from pydantic_settings import BaseSettings
from typing import Optional

class IntegrationMode(Enum):
    """EHR Integration Modes"""
    STANDALONE = "standalone"  # Current: No EHR connection
    EPIC_INTEGRATED = "epic_integrated"  # Future: Real-time Epic FHIR

class Settings(BaseSettings):
    """Application settings with Epic integration support"""

    # Integration mode
    integration_mode: IntegrationMode = IntegrationMode.STANDALONE

    # Epic FHIR Configuration (future use)
    epic_fhir_base_url: Optional[str] = None
    epic_client_id: Optional[str] = None
    epic_client_secret: Optional[str] = None
    epic_oauth_enabled: bool = False

    # Epic sandbox for testing (future)
    epic_sandbox_mode: bool = False
    epic_sandbox_url: str = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"

    class Config:
        env_file = ".env"

settings = Settings()
```

#### **0.1.2 FHIR-Aligned Patient Document Schemas**

Update `src/models/patient_document_schemas.py` with FHIR naming:

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FHIRPatientIdentifier(BaseModel):
    """FHIR-aligned patient identification"""
    patient_fhir_id: Optional[str] = Field(None, description="Epic Patient FHIR ID")
    patient_mrn: Optional[str] = Field(None, description="Medical Record Number")
    patient_given_name: Optional[str] = Field(None, description="First name (FHIR: Patient.name.given)")
    patient_family_name: Optional[str] = Field(None, description="Last name (FHIR: Patient.name.family)")

    # Convenience property for display
    @property
    def full_name(self) -> Optional[str]:
        if self.patient_given_name and self.patient_family_name:
            return f"{self.patient_given_name} {self.patient_family_name}"
        return None

class FHIRCondition(BaseModel):
    """FHIR-aligned diagnosis/condition"""
    condition_fhir_id: Optional[str] = Field(None, description="Epic Condition FHIR ID")
    condition_code_icd10: str = Field(..., description="ICD-10 code (e.g., E11.9)")
    condition_code_snomed: Optional[str] = Field(None, description="SNOMED CT code (Epic primary)")
    condition_display: str = Field(..., description="Human-readable diagnosis")
    condition_clinical_status: str = Field(default="active", description="active | resolved | inactive")

class FHIRMedicationRequest(BaseModel):
    """FHIR-aligned medication order"""
    medication_fhir_id: Optional[str] = Field(None, description="Epic MedicationRequest FHIR ID")
    medication_code_rxnorm: Optional[str] = Field(None, description="RxNorm code")
    medication_display: str = Field(..., description="Medication name")
    dosage_value: str = Field(..., description="Dose amount (e.g., '500')")
    dosage_unit: str = Field(..., description="Dose unit (e.g., 'mg')")
    frequency_code: str = Field(..., description="Timing code (e.g., 'BID', 'QID')")
    frequency_display: str = Field(..., description="Human-readable frequency")
    route: Optional[str] = Field(None, description="Route of administration (e.g., 'oral', 'IV')")
    instructions: Optional[str] = Field(None, description="Patient instructions")
    prescriber_npi: Optional[str] = Field(None, description="Prescriber NPI (future)")

class FHIREncounter(BaseModel):
    """FHIR-aligned encounter context"""
    encounter_fhir_id: Optional[str] = Field(None, description="Epic Encounter FHIR ID")
    encounter_type_code: Optional[str] = Field(None, description="Encounter type code")
    encounter_type_display: Optional[str] = Field(None, description="ED | Inpatient | Outpatient")
    encounter_start: Optional[datetime] = Field(None, description="Encounter start time")
    encounter_end: Optional[datetime] = Field(None, description="Encounter end time")

class DischargeInstructionsRequest(BaseModel):
    """Discharge instructions with FHIR alignment"""

    # Patient identification (FHIR-aligned)
    patient: FHIRPatientIdentifier

    # Clinical context (FHIR-aligned)
    primary_diagnosis: FHIRCondition
    secondary_diagnoses: List[FHIRCondition] = []
    medications: List[FHIRMedicationRequest] = []
    encounter: Optional[FHIREncounter] = None

    # Discharge-specific content
    warning_signs: List[str]
    emergency_criteria: List[str]
    activity_restrictions: List[str] = []
    diet_instructions: Optional[str] = None
    follow_up_instructions: str

    # Localization
    language: LanguageCode = LanguageCode.ENGLISH
    reading_level: ReadingLevel = ReadingLevel.INTERMEDIATE
```

#### **0.1.3 FHIR-Ready Diagnosis Library**

Update diagnosis content map with standardized codes:

```python
# src/models/content_settings.py

class DiagnosisContentMap(Base):
    """FHIR-ready diagnosis library with standard codes"""
    __tablename__ = "diagnosis_content_map"

    id = Column(String, primary_key=True)

    # Clinical codes (FHIR-aligned)
    icd10_code = Column(String(10), unique=True, index=True)  # "E11.9"
    snomed_code = Column(String(20), unique=True, index=True)  # "44054006" (Epic primary)
    diagnosis_display = Column(String(200), index=True)  # "Type 2 Diabetes Mellitus"

    # Legacy field for backwards compatibility
    diagnosis_name = Column(String(200))  # Kept for existing code

    # Standard content
    standard_warning_signs = Column(JSON)
    standard_medications = Column(JSON)  # Now includes RxNorm codes
    standard_activity_restrictions = Column(JSON)
    standard_diet_instructions = Column(Text)
    standard_follow_up_instructions = Column(Text)

    # Educational content
    patient_education_key_points = Column(JSON)

    # Usage stats
    times_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### **0.1.4 EHR Integration Service Stub**

Create placeholder for future Epic integration:

```python
# services/ehr_integration_service.py (NEW FILE)

from typing import Optional, List
from src.config import settings, IntegrationMode
from src.models.patient_document_schemas import (
    FHIRPatientIdentifier,
    FHIRCondition,
    FHIRMedicationRequest,
    FHIREncounter
)

class EHRIntegrationService:
    """
    EHR Integration Service

    Current: Stub/placeholder for future Epic FHIR integration
    Future: Real-time data exchange with Epic via HL7 FHIR R4 API

    Epic FHIR Resources:
    - Patient: Demographics, MRN
    - Encounter: Visit context, location, time
    - Condition: Diagnoses (ICD-10, SNOMED)
    - MedicationRequest: Active medications (RxNorm)
    - DocumentReference: Write discharge notes to chart

    Authentication: OAuth 2.0 (Epic on FHIR)
    Base URL: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
    """

    def __init__(self):
        self.mode = settings.integration_mode
        self.epic_client = None  # Future: EpicFHIRClient()

    async def fetch_patient_by_mrn(self, mrn: str) -> Optional[FHIRPatientIdentifier]:
        """
        Fetch patient demographics from Epic

        Standalone mode: Returns None (manual entry required)
        Epic mode: GET /Patient?identifier=mrn|{mrn}

        Args:
            mrn: Medical Record Number

        Returns:
            FHIRPatientIdentifier or None
        """
        if self.mode == IntegrationMode.STANDALONE:
            return None

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            # Future implementation:
            # response = await self.epic_client.get(f"/Patient?identifier=mrn|{mrn}")
            # return self._parse_patient_resource(response)
            raise NotImplementedError("Epic integration coming in future version")

    async def fetch_active_medications(
        self,
        patient_fhir_id: str
    ) -> List[FHIRMedicationRequest]:
        """
        Fetch active medications from Epic

        Epic mode: GET /MedicationRequest?patient={patient_id}&status=active

        Returns:
            List of active medication orders with RxNorm codes
        """
        if self.mode == IntegrationMode.STANDALONE:
            return []

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            # Future: return await self.epic_client.get_medications(patient_fhir_id)
            raise NotImplementedError("Epic integration coming in future version")

    async def fetch_active_conditions(
        self,
        patient_fhir_id: str
    ) -> List[FHIRCondition]:
        """
        Fetch active diagnoses from Epic

        Epic mode: GET /Condition?patient={patient_id}&clinical-status=active

        Returns:
            List of active conditions with ICD-10 and SNOMED codes
        """
        if self.mode == IntegrationMode.STANDALONE:
            return []

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            raise NotImplementedError("Epic integration coming in future version")

    async def fetch_encounter_context(
        self,
        encounter_fhir_id: str
    ) -> Optional[FHIREncounter]:
        """
        Fetch encounter details from Epic

        Epic mode: GET /Encounter/{encounter_id}
        """
        if self.mode == IntegrationMode.STANDALONE:
            return None

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            raise NotImplementedError("Epic integration coming in future version")

    async def write_discharge_note(
        self,
        encounter_fhir_id: str,
        document_content: str,
        document_type: str = "discharge_instructions"
    ) -> bool:
        """
        Write discharge instructions to Epic chart

        Epic mode: POST /DocumentReference
        Creates clinical note attached to encounter

        Args:
            encounter_fhir_id: Epic encounter ID
            document_content: Generated discharge instructions (text or PDF base64)
            document_type: Document category

        Returns:
            True if successful
        """
        if self.mode == IntegrationMode.STANDALONE:
            return True  # Document generated, nothing to write

        elif self.mode == IntegrationMode.EPIC_INTEGRATED:
            # Future: Create DocumentReference resource in Epic
            raise NotImplementedError("Epic integration coming in future version")

    def is_epic_enabled(self) -> bool:
        """Check if Epic integration is active"""
        return self.mode == IntegrationMode.EPIC_INTEGRATED

# Global instance
ehr_service = EHRIntegrationService()
```

---

## **PHASE 1: Foundation & Settings System** (Week 1-2)

### **Sprint 1.1: Core Settings Infrastructure** (Days 1-3)

**Goal:** Build the foundation for content reuse and settings management.

#### **1.1.1 Settings Database Models**
```python
# src/models/content_settings.py

class FacilitySettings(Base):
    """Facility-wide settings (shared by all nurses at facility)"""
    __tablename__ = "facility_settings"

    facility_id = Column(String, primary_key=True)
    facility_name = Column(String(200))

    # Contact info
    main_phone = Column(String(20))
    after_hours_phone = Column(String(20))
    patient_portal_url = Column(String(200))
    address = Column(Text)

    # Standard content
    standard_follow_up_instructions = Column(JSON)  # List of strings
    standard_emergency_criteria = Column(JSON)
    hipaa_disclaimer = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class WorkSettingPreset(Base):
    """Pre-configured content for specific work settings"""
    __tablename__ = "work_setting_presets"

    id = Column(String, primary_key=True)
    work_setting = Column(String(50), index=True)  # ED, ICU, etc.

    # Common content for this setting
    common_warning_signs = Column(JSON)  # List of pre-written signs
    common_medications = Column(JSON)  # List of {name, dosage, frequency}
    common_diagnoses = Column(JSON)  # List of strings
    common_activity_restrictions = Column(JSON)  # List of strings
    common_diet_instructions = Column(JSON)  # List of strings

    # Defaults
    default_follow_up_timeframe = Column(String(50))  # "7-10 days"

    created_at = Column(DateTime, default=datetime.utcnow)


class PersonalContentLibrary(Base):
    """User's personal saved content and preferences"""
    __tablename__ = "personal_content_library"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)

    # Favorite phrases (learned from usage)
    favorite_warning_signs = Column(JSON, default=[])
    favorite_medication_instructions = Column(JSON, default=[])
    favorite_follow_up_phrases = Column(JSON, default=[])
    favorite_activity_restrictions = Column(JSON, default=[])

    # Custom templates
    custom_discharge_templates = Column(JSON, default=[])
    custom_medication_templates = Column(JSON, default=[])

    # Usage tracking (for learning)
    most_used_diagnoses = Column(JSON, default=[])  # Track frequency
    most_used_medications = Column(JSON, default=[])

    # ❌ NO PATIENT DATA EVER

    updated_at = Column(DateTime, onupdate=datetime.utcnow)


class DiagnosisContentMap(Base):
    """Mapping of diagnoses to standard content (system-wide)"""
    __tablename__ = "diagnosis_content_map"

    diagnosis_id = Column(String, primary_key=True)
    diagnosis_name = Column(String(200), index=True)

    # Standard content for this diagnosis
    standard_warning_signs = Column(JSON)
    standard_medications = Column(JSON)
    standard_activity_restrictions = Column(JSON)
    standard_diet_instructions = Column(Text)
    standard_follow_up_instructions = Column(Text)

    # Educational content
    patient_education_key_points = Column(JSON)

    # Usage stats
    times_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
```

#### **1.1.2 Content Libraries (Pre-populated)**
```python
# scripts/populate_content_libraries.py

# Pre-populate 100+ diagnoses with standard content
DIAGNOSIS_LIBRARY = {
    "pneumonia": {
        "warning_signs": [
            "Fever over 101°F (38.3°C) that doesn't improve",
            "Difficulty breathing or shortness of breath",
            "Chest pain that is severe or worsening",
            "Coughing up blood or rust-colored mucus",
            "Confusion or altered mental status",
            "Inability to keep fluids down"
        ],
        "medications": [
            {"name": "Amoxicillin", "dosage": "500 mg", "frequency": "Three times daily"},
            {"name": "Ibuprofen", "dosage": "400 mg", "frequency": "Every 6 hours as needed"}
        ],
        "activity_restrictions": [
            "Rest for 3-5 days",
            "Avoid strenuous activity for 1-2 weeks",
            "Stay home from work for at least 3-5 days",
            "Avoid crowded places until fever-free for 24 hours"
        ],
        "diet_instructions": "Drink plenty of fluids (8-10 glasses of water per day). Eat nutritious meals to support recovery.",
        "follow_up": "See your primary care doctor in 7-10 days"
    },

    "urinary_tract_infection": {
        "warning_signs": [
            "Fever over 101°F",
            "Severe back or flank pain",
            "Blood in urine",
            "Nausea and vomiting",
            "Symptoms not improving after 2 days of antibiotics"
        ],
        "medications": [
            {"name": "Bactrim DS", "dosage": "1 tablet", "frequency": "Twice daily"}
        ],
        "activity_restrictions": [
            "Rest as needed",
            "Stay well hydrated"
        ],
        "diet_instructions": "Drink plenty of water (8-10 glasses daily). Cranberry juice may help prevent recurrence.",
        "follow_up": "Call doctor if symptoms don't improve in 48 hours"
    },

    # ... 100+ more diagnoses
}

# Pre-populate medication library (integrate with existing 700+ meds)
MEDICATION_INSTRUCTIONS_LIBRARY = {
    "amoxicillin": {
        "standard_instructions": [
            "Take with food to reduce stomach upset",
            "Complete the full course even if feeling better",
            "Space doses evenly throughout the day"
        ],
        "common_side_effects": ["Nausea", "Diarrhea", "Stomach upset"],
        "serious_warnings": ["Severe diarrhea", "Allergic reaction (rash, itching)"],
        "missed_dose": "Take as soon as you remember. If almost time for next dose, skip missed dose."
    },
    # ... 700+ more medications
}
```

---

### **Sprint 1.2: Settings API Endpoints** (Days 4-5)

#### **API Endpoints**
```
Settings Management:
├── GET    /api/v1/content-settings/facility
├── PUT    /api/v1/content-settings/facility
├── GET    /api/v1/content-settings/work-preset/{work_setting}
├── GET    /api/v1/content-settings/personal
├── PUT    /api/v1/content-settings/personal
├── POST   /api/v1/content-settings/personal/favorite
├── DELETE /api/v1/content-settings/personal/favorite/{id}
│
Diagnosis Content:
├── GET    /api/v1/diagnosis-content/{diagnosis}
├── GET    /api/v1/diagnosis-content/search?q={query}
├── GET    /api/v1/diagnosis-content/autocomplete?q={query}
│
Medication Content:
├── GET    /api/v1/medication-content/{medication}
└── GET    /api/v1/medication-content/autocomplete?q={query}
```

---

### **Sprint 1.3: Frontend Settings UI** (Days 6-7)

#### **Settings Page Mockup**
```jsx
// Settings.jsx

<SettingsPage>
  <Tabs>
    {/* Tab 1: Work Setting Presets */}
    <Tab label="My Work Setting">
      <Select
        value={workSetting}
        onChange={handleWorkSettingChange}
      >
        <option value="emergency_department">Emergency Department</option>
        <option value="icu">ICU</option>
        {/* ... more */}
      </Select>

      <PresetPreview>
        <h3>Default Content for Emergency Department:</h3>
        <CheckboxList
          items={presets.common_warning_signs}
          editable
          onEdit={handleEditPreset}
        />
      </PresetPreview>
    </Tab>

    {/* Tab 2: Personal Library */}
    <Tab label="My Favorites">
      <Section title="My Favorite Warning Signs">
        <EditableList
          items={personalLibrary.favorite_warning_signs}
          onAdd={handleAddFavorite}
          onRemove={handleRemoveFavorite}
        />
      </Section>

      <Section title="My Common Medications">
        <MedicationList
          items={personalLibrary.favorite_medications}
        />
      </Section>
    </Tab>

    {/* Tab 3: Facility Settings */}
    <Tab label="Facility Info">
      <Input label="Main Phone" value={facility.main_phone} />
      <Input label="Patient Portal" value={facility.patient_portal_url} />
      {/* ... more facility info */}
    </Tab>
  </Tabs>
</SettingsPage>
```

---

## **PHASE 2: Quick Create System** (Week 3)

### **Sprint 2.1: Quick Create API** (Days 8-9)

#### **Quick Create Endpoint**
```python
# routers/quick_create.py

@router.post("/quick-create/discharge-instructions")
async def quick_create_discharge(
    patient_name: str,
    diagnosis: str,
    reading_level: Optional[ReadingLevel] = None,
    language: Optional[LanguageCode] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Quick create discharge instructions

    - Auto-loads user settings
    - Auto-loads diagnosis content
    - Auto-populates document
    - Returns editable document

    **Patient data NOT saved - session only!**
    """

    # Get user settings
    user_profile = await get_user_profile(current_user.id)
    personal_library = await get_personal_library(current_user.id)
    facility_settings = await get_facility_settings(user_profile.facility_id)

    # Get diagnosis content
    diagnosis_content = await get_diagnosis_content(diagnosis)

    # Build document (NO PATIENT DATA SAVED)
    document_data = {
        # Nurse info (from saved settings)
        "nurse_name": user_profile.full_name,
        "nurse_credentials": user_profile.credentials,
        "facility_name": facility_settings.facility_name,
        "facility_phone": facility_settings.main_phone,

        # Patient info (SESSION ONLY - NOT SAVED)
        "patient_name": patient_name,  # ❌ NOT SAVED TO DB

        # Diagnosis (NOT PHI - can save to usage stats)
        "diagnosis": diagnosis,

        # Auto-populated content (from settings)
        "medications": diagnosis_content.standard_medications,
        "warning_signs": diagnosis_content.standard_warning_signs,
        "activity_restrictions": diagnosis_content.standard_activity_restrictions,
        "follow_up_instructions": diagnosis_content.standard_follow_up_instructions,

        # Defaults
        "reading_level": reading_level or user_profile.default_patient_reading_level,
        "language": language or user_profile.default_patient_language
    }

    # Track usage (NO PHI)
    await track_diagnosis_usage(current_user.id, diagnosis)  # ✅ OK to track

    # Return editable document (in-app editing next)
    return {
        "document_data": document_data,
        "session_id": generate_session_id(),  # For in-app editing
        "expires_at": now() + timedelta(hours=2)
    }
```

---

### **Sprint 2.2: In-App Document Editor** (Days 10-12)

#### **SBAR-style Rich Text Editor**

Reuse concepts from SBAR wizard with enhancements:

```jsx
// DocumentEditor.jsx

<DocumentEditor document={documentData}>
  <EditorToolbar>
    <FormatButton icon="bold" />
    <FormatButton icon="italic" />
    <FormatButton icon="list" />
    <Separator />
    <InsertButton icon="table" label="Insert Table" />
    <InsertButton icon="checkbox" label="Insert Checklist" />
    <Separator />
    <SaveDraftButton />
    <PreviewButton />
  </EditorToolbar>

  <EditableSections>
    {/* Each section editable */}
    <Section title="Basic Information" locked>
      <Field label="Nurse" value={nurse_name} readOnly />
      <Field label="Facility" value={facility} readOnly />
      <Field label="Patient" value={patient_name} editable />
    </Section>

    <Section title="Diagnosis">
      <RichTextField
        value={diagnosis}
        onChange={handleDiagnosisChange}
      />
    </Section>

    <Section title="Medications">
      <MedicationList
        items={medications}
        onAdd={handleAddMedication}
        onRemove={handleRemoveMedication}
        onEdit={handleEditMedication}
      />
      <AddFromLibraryButton onClick={() => openMedicationLibrary()} />
    </Section>

    <Section title="Instructions">
      <CheckboxList
        items={activity_restrictions}
        editable
        onToggle={handleToggleRestriction}
        onAdd={handleAddRestriction}
      />
    </Section>

    <Section title="Warning Signs">
      <CheckboxList
        items={warning_signs}
        editable
        highlight="warning"
      />
      <QuickAddButtons>
        <Button onClick={() => addWarningSign("Fever over 101°F")}>
          + Fever >101°F
        </Button>
        <Button onClick={() => addWarningSign("Difficulty breathing")}>
          + Difficulty Breathing
        </Button>
        {/* Common ones as quick buttons */}
      </QuickAddButtons>
    </Section>
  </EditableSections>

  <EditorFooter>
    <Button variant="secondary" onClick={saveDraft}>
      Save Draft (Session Only)
    </Button>
    <Button variant="primary" onClick={openExportModal}>
      Export Document
    </Button>
  </EditorFooter>
</DocumentEditor>
```

#### **Smart Features**
```jsx
// Smart content suggestions
<SmartSuggestions>
  {/* Based on diagnosis */}
  <SuggestionChip
    text="Did you forget: Take with food?"
    onClick={addToInstructions}
  />

  {/* Based on user's history */}
  <SuggestionChip
    text="You usually add: Complete full course"
    onClick={addToInstructions}
  />

  {/* Based on facility requirements */}
  <SuggestionChip
    text="Required: Follow-up appointment"
    onClick={addFollowUp}
    required
  />
</SmartSuggestions>
```

---

## **PHASE 3: Professional Export Formats** (Week 4)

### **Sprint 3.1: Word Document Generation** (Days 13-15)

#### **Professional Word Templates**

Use `python-docx` library for Microsoft Word generation.

```python
# services/word_generation_service.py

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

class ProfessionalWordTemplate:
    """Generate professional Word documents with styles"""

    def __init__(self, template_name="modern_medical"):
        self.doc = Document()
        self.template = template_name
        self._setup_styles()
        self._setup_page()

    def _setup_styles(self):
        """Create professional styles"""
        styles = self.doc.styles

        # Title style
        title_style = styles.add_style('CustomTitle', WD_STYLE_TYPE.PARAGRAPH)
        title_font = title_style.font
        title_font.name = 'Calibri'
        title_font.size = Pt(24)
        title_font.bold = True
        title_font.color.rgb = RGBColor(0, 51, 102)  # Navy blue

        # Section Header style
        header_style = styles.add_style('SectionHeader', WD_STYLE_TYPE.PARAGRAPH)
        header_font = header_style.font
        header_font.name = 'Calibri'
        header_font.size = Pt(14)
        header_font.bold = True
        header_font.color.rgb = RGBColor(0, 112, 192)  # Blue
        header_style.paragraph_format.space_before = Pt(12)
        header_style.paragraph_format.space_after = Pt(6)

        # Body text style
        body_style = styles.add_style('CustomBody', WD_STYLE_TYPE.PARAGRAPH)
        body_font = body_style.font
        body_font.name = 'Calibri'
        body_font.size = Pt(11)
        body_style.paragraph_format.line_spacing = 1.15

        # Warning box style
        warning_style = styles.add_style('WarningBox', WD_STYLE_TYPE.PARAGRAPH)
        warning_font = warning_style.font
        warning_font.name = 'Calibri'
        warning_font.size = Pt(11)
        warning_font.bold = True
        warning_font.color.rgb = RGBColor(192, 0, 0)  # Red
        warning_style.paragraph_format.left_indent = Inches(0.25)
        warning_style.paragraph_format.space_before = Pt(6)

    def _setup_page(self):
        """Setup page margins and size"""
        sections = self.doc.sections
        for section in sections:
            section.page_height = Inches(11)
            section.page_width = Inches(8.5)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)

    def add_header(self, facility_name, logo_path=None):
        """Add professional header with optional logo"""
        header = self.doc.sections[0].header
        header_para = header.paragraphs[0]

        if logo_path:
            run = header_para.add_run()
            run.add_picture(logo_path, width=Inches(1.5))

        header_para.add_run(f"  {facility_name}").bold = True
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_title(self, title, subtitle=None):
        """Add document title"""
        title_para = self.doc.add_paragraph(title, style='CustomTitle')
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if subtitle:
            subtitle_para = self.doc.add_paragraph(subtitle)
            subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_section(self, title, content):
        """Add section with header and content"""
        self.doc.add_paragraph(title, style='SectionHeader')
        self.doc.add_paragraph(content, style='CustomBody')

    def add_bulleted_list(self, title, items):
        """Add bulleted list"""
        self.doc.add_paragraph(title, style='SectionHeader')
        for item in items:
            para = self.doc.add_paragraph(item, style='List Bullet')
            para.paragraph_format.left_indent = Inches(0.25)

    def add_medication_table(self, medications):
        """Add professional medication table"""
        self.doc.add_paragraph("Your Medications", style='SectionHeader')

        table = self.doc.add_table(rows=1, cols=4)
        table.style = 'Light Grid Accent 1'

        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Medication'
        header_cells[1].text = 'Dosage'
        header_cells[2].text = 'Frequency'
        header_cells[3].text = 'Instructions'

        # Make header bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True

        # Add medication rows
        for med in medications:
            row_cells = table.add_row().cells
            row_cells[0].text = med.get('name', '')
            row_cells[1].text = med.get('dosage', '')
            row_cells[2].text = med.get('frequency', '')
            row_cells[3].text = med.get('instructions', '')

    def add_warning_box(self, title, items):
        """Add warning box with red border"""
        # Add table for border effect
        table = self.doc.add_table(rows=1, cols=1)
        table.style = 'Table Grid'
        cell = table.rows[0].cells[0]

        # Add warning title
        title_para = cell.add_paragraph()
        title_run = title_para.add_run(f"⚠️ {title}")
        title_run.bold = True
        title_run.font.color.rgb = RGBColor(192, 0, 0)
        title_run.font.size = Pt(12)

        # Add warning items
        for item in items:
            item_para = cell.add_paragraph()
            item_para.add_run(f"• {item}")
            item_para.paragraph_format.left_indent = Inches(0.25)

        # Style table border (red)
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        tbl = table._element
        tblPr = tbl.tblPr
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '12')  # Border size
            border.set(qn('w:color'), 'C00000')  # Red color
            tblBorders.append(border)
        tblPr.append(tblBorders)

    def add_footer(self, text):
        """Add footer"""
        footer = self.doc.sections[0].footer
        footer_para = footer.paragraphs[0]
        footer_para.text = text
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Style footer
        for run in footer_para.runs:
            run.font.size = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(128, 128, 128)

    def save(self, filename):
        """Save document"""
        self.doc.save(filename)
        return filename


# Example usage
def generate_discharge_instructions_word(data):
    """Generate professional Word document"""
    doc = ProfessionalWordTemplate("modern_medical")

    # Add header with logo
    if data.get('facility_logo'):
        doc.add_header(data['facility_name'], data['facility_logo'])
    else:
        doc.add_header(data['facility_name'])

    # Add title
    doc.add_title("Discharge Instructions", f"For: {data.get('patient_name', 'Patient')}")

    # Add diagnosis
    doc.add_section("Reason for Visit / Diagnosis", data['diagnosis'])

    # Add medications table
    if data.get('medications'):
        doc.add_medication_table(data['medications'])

    # Add instructions
    if data.get('activity_restrictions'):
        doc.add_bulleted_list("Activity Restrictions", data['activity_restrictions'])

    if data.get('diet_instructions'):
        doc.add_section("Diet Instructions", data['diet_instructions'])

    # Add warning signs
    if data.get('warning_signs'):
        doc.add_warning_box("Warning Signs - Contact Your Doctor If:", data['warning_signs'])

    if data.get('emergency_criteria'):
        doc.add_warning_box("Call 911 or Go to Emergency Room If:", data['emergency_criteria'])

    # Add footer
    doc.add_footer(f"Generated by AI Nurse Florence on {datetime.now().strftime('%B %d, %Y')}")

    # Save
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
```

#### **Template Styles**

Create 3 professional templates:

1. **Modern Medical** (Default)
   - Clean, professional
   - Navy blue headers
   - Calibri font
   - Table-based warnings

2. **Classic Healthcare**
   - Traditional look
   - Times New Roman
   - Conservative styling
   - Formal tone

3. **Patient-Friendly**
   - Larger fonts
   - More white space
   - Simplified layout
   - Icons and visual cues

---

### **Sprint 3.2: Plain Text Export** (Day 16)

```python
# services/text_generation_service.py

def generate_plain_text(data):
    """Generate plain text version (for copying/pasting)"""

    text = []
    text.append("=" * 70)
    text.append("DISCHARGE INSTRUCTIONS")
    text.append("=" * 70)
    text.append("")

    if data.get('patient_name'):
        text.append(f"Patient: {data['patient_name']}")
    text.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")
    text.append("")

    text.append("DIAGNOSIS")
    text.append("-" * 70)
    text.append(data['diagnosis'])
    text.append("")

    if data.get('medications'):
        text.append("YOUR MEDICATIONS")
        text.append("-" * 70)
        for med in data['medications']:
            text.append(f"• {med['name']} - {med['dosage']} {med['frequency']}")
            if med.get('instructions'):
                text.append(f"  Instructions: {med['instructions']}")
        text.append("")

    if data.get('warning_signs'):
        text.append("⚠️  WARNING SIGNS - CONTACT YOUR DOCTOR IF:")
        text.append("-" * 70)
        for sign in data['warning_signs']:
            text.append(f"• {sign}")
        text.append("")

    text.append("=" * 70)
    text.append(f"Generated by AI Nurse Florence")
    text.append("This document is for educational purposes only.")
    text.append("=" * 70)

    return "\n".join(text)
```

---

### **Sprint 3.3: Export Modal UI** (Day 17)

```jsx
// ExportModal.jsx

<ExportModal isOpen={showExport} onClose={closeExport}>
  <ModalHeader>
    <h2>Export Document</h2>
    <p>Choose your preferred format</p>
  </ModalHeader>

  <ExportOptions>
    <ExportOption
      icon={<PdfIcon />}
      title="PDF"
      description="Print-ready, professional format"
      onClick={() => exportAs('pdf')}
      recommended
    />

    <ExportOption
      icon={<WordIcon />}
      title="Microsoft Word"
      description="Editable .docx format with professional styles"
      onClick={() => exportAs('docx')}
    />

    <ExportOption
      icon={<TextIcon />}
      title="Plain Text"
      description="Simple text format for copying"
      onClick={() => exportAs('txt')}
    />
  </ExportOptions>

  <TemplateSelector>
    <label>Word Template Style:</label>
    <Select value={templateStyle} onChange={setTemplateStyle}>
      <option value="modern_medical">Modern Medical (Recommended)</option>
      <option value="classic_healthcare">Classic Healthcare</option>
      <option value="patient_friendly">Patient-Friendly</option>
    </Select>
  </TemplateSelector>

  <PrivacyNotice>
    <InfoIcon />
    <span>
      Patient information is NOT saved to our servers.
      This document will be generated and downloaded directly to your device.
    </span>
  </PrivacyNotice>

  <ModalFooter>
    <Button variant="secondary" onClick={closeExport}>
      Cancel
    </Button>
    <Button variant="primary" onClick={handleExport}>
      Download Document
    </Button>
  </ModalFooter>
</ExportModal>
```

---

## **PHASE 4: Wizard for Complex Cases** (Week 5)

### **Sprint 4.1: Wizard Infrastructure** (Days 18-20)

```jsx
// ComplexDocumentWizard.jsx

<Wizard
  steps={[
    "Basic Info",
    "Diagnosis & Conditions",
    "Medications",
    "Instructions",
    "Warning Signs",
    "Review"
  ]}
  currentStep={currentStep}
>
  {/* Step 1: Basic Info */}
  <WizardStep step={1}>
    <AutoFilledSection>
      <Field label="Nurse" value={nurse_name} locked />
      <Field label="Facility" value={facility} locked />
    </AutoFilledSection>

    <EditableSection>
      <Input
        label="Patient Name"
        value={patientName}
        onChange={setPatientName}
        warning="Not saved - session only"
      />
      <Select
        label="Reading Level"
        value={readingLevel}
        options={["basic", "intermediate", "advanced"]}
      />
    </EditableSection>
  </WizardStep>

  {/* Step 2: Diagnosis */}
  <WizardStep step={2}>
    <DiagnosisSelector
      onSelect={handleDiagnosisSelect}
      onContentLoad={loadDiagnosisContent}
    />

    {diagnosisSelected && (
      <ContentPreview>
        <Alert type="success">
          ✅ Loaded standard content for {diagnosis}
        </Alert>
        <ul>
          <li>{medications.length} common medications</li>
          <li>{warningContinue Signs.length} warning signs</li>
          <li>Standard activity restrictions</li>
        </ul>
      </ContentPreview>
    )}
  </WizardStep>

  {/* Step 3: Medications */}
  <WizardStep step={3}>
    <MedicationWizardStep
      preloadedMeds={diagnosisContent.medications}
      personalLibrary={personalLibrary.medications}
    />
  </WizardStep>

  {/* ... more steps */}

  {/* Step 6: Review */}
  <WizardStep step={6}>
    <DocumentPreview document={compiledDocument} />
    <WizardActions>
      <Button onClick={goBack}>Back to Edit</Button>
      <Button onClick={openExportModal} primary>
        Export Document
      </Button>
    </WizardActions>
  </WizardStep>
</Wizard>
```

---

## **PHASE 5: Legal Documentation** (Week 6-7)

### **Sprint 5.1: Incident Report System** (Days 21-24)

```python
# src/models/legal_documents.py

class IncidentReport(Base):
    """Legal incident report - immutable after signing"""
    __tablename__ = "incident_reports"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))

    # Incident details (NO PATIENT NAMES)
    incident_type = Column(String(50))  # fall, med_error, injury, etc.
    incident_date_time = Column(DateTime)
    location = Column(String(200))

    # Description (factual only)
    factual_description = Column(Text)
    immediate_actions_taken = Column(Text)
    notifications_made = Column(JSON)  # List of who was notified

    # Witnesses (NO PHI)
    witness_names = Column(JSON)  # Staff names only

    # Signatures
    nurse_signature_hash = Column(String(64))
    supervisor_signature_hash = Column(String(64))
    signed_at = Column(DateTime)

    # Immutability
    is_locked = Column(Boolean, default=False)
    content_hash = Column(String(64))  # SHA-256 of content

    # Audit trail
    audit_log = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
```

---

### **Sprint 5.2: AMA Documentation** (Days 25-27)

```python
class AMADocumentation(Base):
    """Against Medical Advice documentation"""
    __tablename__ = "ama_documentation"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))

    # NO PATIENT IDENTIFIERS
    # (PHI removed for legal protection while maintaining documentation)

    incident_date_time = Column(DateTime)

    # What was explained
    risks_explained = Column(JSON)  # List of risks
    consequences_explained = Column(Text)
    alternative_offered = Column(Text)

    # Patient response
    patient_understanding_verified = Column(Boolean)
    patient_verbatim_statement = Column(Text)

    # Notifications
    physician_notified = Column(Boolean)
    physician_name = Column(String(200))
    supervisor_notified = Column(Boolean)

    # Witnesses
    witnesses = Column(JSON)

    # Signatures
    nurse_signature_hash = Column(String(64))
    patient_refused_to_sign = Column(Boolean)

    # Immutability
    is_locked = Column(Boolean, default=False)
    content_hash = Column(String(64))

    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## **PHASE 6: Data Privacy & Security** (Week 8)

### **Sprint 6.1: Patient Data Protection** (Days 28-30)

#### **Session Management**
```python
# src/utils/session_management.py

class SecureSessionManager:
    """Manage patient data in memory only"""

    def __init__(self):
        self._sessions = {}  # In-memory only
        self._cleanup_task = None

    async def create_session(self, user_id: str, ttl_seconds: int = 7200):
        """Create new session (2 hour default)"""
        session_id = secrets.token_urlsafe(32)

        self._sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(seconds=ttl_seconds),
            "patient_data": {},  # PHI stored here temporarily
            "auto_delete": True
        }

        return session_id

    async def store_patient_data(self, session_id: str, key: str, value: Any):
        """Store patient data in session (temporary)"""
        if session_id not in self._sessions:
            raise ValueError("Invalid session")

        if self._is_expired(session_id):
            await self.delete_session(session_id)
            raise ValueError("Session expired")

        # Log access (NO PHI in logs)
        logger.info(f"Storing data for session {session_id[:8]}... (key: {key})")

        self._sessions[session_id]["patient_data"][key] = value

    async def delete_session(self, session_id: str):
        """Securely delete session and all patient data"""
        if session_id in self._sessions:
            # Overwrite sensitive data before deletion
            for key in self._sessions[session_id]["patient_data"]:
                self._sessions[session_id]["patient_data"][key] = None

            del self._sessions[session_id]
            logger.info(f"Session {session_id[:8]}... deleted")

    async def cleanup_expired_sessions(self):
        """Automatically cleanup expired sessions"""
        now = datetime.now()
        expired = [
            sid for sid, data in self._sessions.items()
            if data["expires_at"] < now
        ]

        for session_id in expired:
            await self.delete_session(session_id)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

    def _is_expired(self, session_id: str) -> bool:
        """Check if session is expired"""
        return self._sessions[session_id]["expires_at"] < datetime.now()


# Automatic cleanup
@app.on_event("startup")
async def start_session_cleanup():
    """Start background task to cleanup expired sessions"""
    session_manager = SecureSessionManager()

    async def cleanup_loop():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            await session_manager.cleanup_expired_sessions()

    asyncio.create_task(cleanup_loop())


@app.on_event("shutdown")
async def clear_all_sessions():
    """Clear all patient data on shutdown"""
    session_manager = SecureSessionManager()
    for session_id in list(session_manager._sessions.keys()):
        await session_manager.delete_session(session_id)

    logger.info("All patient data cleared on shutdown")
```

#### **Frontend Session Management**
```javascript
// utils/sessionManager.js

class PatientDataSession {
  constructor() {
    this.sessionId = null;
    this.expiresAt = null;
    this.autoCleanup = true;

    // Clear on page unload
    window.addEventListener('beforeunload', () => this.destroy());

    // Clear on timeout
    this.setupAutoExpiry();
  }

  async create() {
    const response = await fetch('/api/v1/session/create', {
      method: 'POST'
    });
    const data = await response.json();

    this.sessionId = data.session_id;
    this.expiresAt = new Date(data.expires_at);

    // Store in sessionStorage (NOT localStorage - clears on tab close)
    sessionStorage.setItem('patient_session_id', this.sessionId);

    return this.sessionId;
  }

  async storePatientData(key, value) {
    if (!this.sessionId) {
      await this.create();
    }

    // Send to server (temporary storage)
    await fetch(`/api/v1/session/${this.sessionId}/store`, {
      method: 'POST',
      body: JSON.stringify({ key, value })
    });

    // Also store in memory (NOT persisted)
    this.tempData = this.tempData || {};
    this.tempData[key] = value;
  }

  async destroy() {
    if (this.sessionId) {
      // Tell server to delete
      await fetch(`/api/v1/session/${this.sessionId}`, {
        method: 'DELETE'
      });

      // Clear local
      this.tempData = {};
      sessionStorage.removeItem('patient_session_id');
      this.sessionId = null;
    }
  }

  setupAutoExpiry() {
    // Auto-destroy after 2 hours
    setInterval(() => {
      if (this.expiresAt && new Date() > this.expiresAt) {
        this.destroy();
      }
    }, 60000); // Check every minute
  }
}

// Usage
const patientSession = new PatientDataSession();

// Store patient name (temporary)
await patientSession.storePatientData('patient_name', 'John Smith');

// After document generated
await patientSession.destroy(); // ← Immediately clear PHI
```

---

### **Sprint 6.2: Audit Logging (NO PHI)** (Day 31)

```python
# src/models/audit_log.py

class AuditLog(Base):
    """Audit log - NO PHI, only actions"""
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)

    # Who & When
    user_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String(100), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # What (NO PHI)
    document_type = Column(String(50))
    diagnosis_used = Column(String(200))  # ✅ OK - not PHI
    export_format = Column(String(20))

    # Context (NO PHI)
    work_setting = Column(String(50))
    session_id = Column(String(64))

    # ❌ NEVER LOG:
    # - patient_name
    # - patient_id
    # - any clinical details
    # - any identifiable information

    ip_address = Column(String(45))  # For security
    user_agent = Column(String(500))


# Usage
async def log_document_generation(user_id, document_type, diagnosis):
    """Log document generation (NO PHI)"""
    await AuditLog.create(
        user_id=user_id,
        action="generated_document",
        document_type=document_type,
        diagnosis_used=diagnosis,  # ✅ Not PHI
        # ❌ NO patient name
        # ❌ NO patient ID
        # ❌ NO clinical details
    )
```

---

## **PHASE 7: Integration & Testing** (Week 9)

### **Integration Points**
- Connect Quick Create to existing PDF generation
- Connect Wizard to Quick Create
- Connect Settings to all document generation
- Connect In-app Editor to Export system

### **Testing**
- Unit tests for each component
- Integration tests for full workflow
- Privacy tests (ensure NO PHI saved)
- Load tests (session management performance)
- User acceptance testing

---

## 📊 **IMPLEMENTATION SUMMARY**

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| **Phase 1** | Week 1-2 | Settings system, content libraries, APIs |
| **Phase 2** | Week 3 | Quick Create, In-app editor |
| **Phase 3** | Week 4 | Word/PDF/Text export, professional templates |
| **Phase 4** | Week 5 | Complex case wizard |
| **Phase 5** | Week 6-7 | Legal documentation (incident, AMA) |
| **Phase 6** | Week 8 | Data privacy, session management |
| **Phase 7** | Week 9 | Integration, testing |

**Total Timeline: 9 weeks**

---

## 🎯 **SUCCESS METRICS**

### Time Savings
- Routine discharge: **5 min → 30 sec** (90% reduction)
- Complex discharge: **10 min → 3 min** (70% reduction)
- Incident report: **15 min → 5 min** (67% reduction)

### Quality
- 100% consistent facility information
- 0% PHI leakage (nothing saved)
- Professional formatting in all exports
- Complete audit trail for legal documents

### User Experience
- Settings setup: 10 minutes (one-time)
- Quick Create: 2-3 clicks
- Wizard: 5 steps for complex cases
- Export: 1 click, 3 formats

---

## 🔐 **PRIVACY GUARANTEES**

✅ **What We Save:**
- Nurse profile
- Facility settings
- Content libraries
- Usage statistics (diagnosis frequency)
- Audit logs (actions, not data)

❌ **What We NEVER Save:**
- Patient names
- Patient IDs
- Clinical details
- Any PHI (Protected Health Information)

**All patient data:**
- Stored in memory only
- Session-based (2 hour expiry)
- Auto-deleted on browser close
- Cleared on document generation
- Wiped on server shutdown

---

This plan gives you professional, HIPAA-compliant document generation with massive time savings and zero patient data storage risk!

---

## 📝 **PENDING TODOS**

### **High Priority**
- [ ] **Briefing on Future App Deployment Plans**
  - Topic: App deployment beyond ChatGPT enterprise store
  - Details: Institutional network installation & data system integration
  - Status: Awaiting user briefing
  - Notes: User plans to install app on institutional networks with integration to existing data systems (EHR, patient management, etc.)

### **Implementation TODOs** (After Phase Planning Complete)
- [ ] Begin Phase 1 implementation (Settings infrastructure)
- [ ] Evaluate institutional integration requirements
- [ ] Plan EHR/EMR integration strategy
- [ ] Design on-premises deployment architecture

---

**Ready to proceed with Phase 1?**
