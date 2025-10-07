# Future Enhancement Ideas

This document tracks features and improvements identified during development that could be valuable in future iterations.

---

## Comprehensive Discharge Summary Wizard

**Status:** Concept identified from prototype
**Priority:** Medium
**Related:** Current DischargeInstructions wizard provides patient-facing discharge instructions. This would add a provider-focused comprehensive discharge summary.

### Purpose
Create detailed hospital discharge summaries for provider-to-provider communication (vs. patient education). Useful for:
- Transitions of care documentation
- Hospital discharge summaries for medical records
- Provider handoff documentation
- Meeting regulatory documentation requirements

### Additional Fields Beyond Current DischargeInstructions

#### Patient & Admission Information
- `patient_name` - Full patient identification
- `admission_date` - Date of hospital admission
- `discharge_date` - Date of discharge
- `length_of_stay` - Duration of hospitalization
- `attending_physician` - Primary physician
- `discharge_disposition` - Where patient is going (home, SNF, rehab, etc.)

#### Hospital Course (New Section)
- `admission_diagnosis` - Reason for admission
- `hospital_course` - Narrative of hospitalization events
- `procedures_performed` - All procedures during stay
- `complications` - Any complications encountered
- `consults_obtained` - Specialist consultations
- `significant_events` - Key events during hospitalization

#### Discharge Status & Findings (New Section)
- `discharge_diagnosis` - Final diagnoses at discharge
- `discharge_condition` - Clinical condition at discharge
- `discharge_vital_signs` - Final vital signs
- `pending_results` - Tests still pending
- `discharge_labs` - Final lab values
- `functional_status` - ADLs, mobility, cognitive status

#### Medications & Care (Enhanced)
- `discharge_medications` - Complete med list with doses
- `medication_changes` - Changes from admission meds
- `diet_instructions` - Dietary recommendations
- `activity_restrictions` - Physical activity limitations
- `wound_care` - Wound care instructions
- `equipment_needs` - DME requirements (walker, oxygen, etc.)

#### Follow-up & Education (Enhanced)
- `follow_up_appointments` - Scheduled appointments
- `warning_signs` - Red flags to watch for
- `patient_education_provided` - Education topics covered
- `discharge_instructions_given` - Instructions provided
- `patient_understanding` - Patient comprehension assessment
- `caregiver_education` - Education for caregivers

### Technical Features to Include
- **AI Enhancement** - LLM-powered enhancement of narrative sections
- **5-step wizard** - Patient Info, Hospital Course, Discharge Status, Medications/Care, Follow-up
- **Template generation** - Auto-generate structured summary
- **Export formats** - PDF, DOCX, TXT
- **Integration with EHR** - FHIR compatibility for Epic/Cerner

### Implementation Notes
- Must follow restrictive navigation pattern (forward-only)
- Should include confirmation dialogs
- Requires comprehensive review step
- May need provider authentication/signature
- Consider templates for different specialties (medical, surgical, psychiatric, etc.)

### Relationship to Current Features
- **DischargeInstructions** = Patient/family education document
- **DischargeSummary** (future) = Provider-to-provider medical record
- Both could share some fields (medications, follow-up, warning signs)
- Could potentially generate both from single data entry

### Estimated Effort
- Frontend wizard: 2-3 days
- Backend API: 1-2 days
- AI enhancement feature: 2-3 days
- Testing & refinement: 2-3 days
- **Total: ~1-2 weeks**

### References
- Source prototype: `frontend-react/src/widgets/DischargeSummaryWizard/` (deleted 2025-01-07)
- Related documentation: CMS discharge planning requirements
- Standards: Joint Commission discharge summary requirements

---

## Other Future Enhancements

### Epic FHIR Integration
- **Status:** Identified, on hold
- **Purpose:** Direct integration with Epic EHR systems
- **Priority:** High (for hospital adoption)
- See Epic integration planning docs

### Auto-save Drafts
- **Status:** Concept
- **Purpose:** Save wizard progress to localStorage/backend
- **Priority:** Medium
- Allow users to resume interrupted wizards

### Multi-language Support
- **Status:** Partial (i18n framework exists)
- **Purpose:** Discharge instructions in patient's language
- **Priority:** Medium-High
- Currently only English supported

### Voice-to-Text Improvements
- **Status:** Basic implementation exists
- **Purpose:** Better clinical voice dictation
- **Priority:** Low-Medium
- Consider specialized medical vocabulary

---

**Last Updated:** 2025-01-07
