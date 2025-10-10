# AI Nurse Florence - Comprehensive Wizard Implementation Plan

**Status**: Planning Phase
**Created**: 2025-10-10
**Owner**: Deep Study AI Development Team
**Epic Integration Dependency**: Epic Wizard serves as Microsoft-style UI template

---

## Executive Summary

### Vision
Transform all clinical wizards to follow the Microsoft-style wizard pattern established by the Epic Integration Wizard, creating a consistent, professional user experience across AI Nurse Florence.

### Current State Analysis

**✅ Existing Wizards (17 Backend Routers)**
1. admission_assessment_wizard.py
2. care_plan.py
3. clinical_assessment.py
4. discharge_planning.py
5. discharge_summary_wizard.py
6. dosage_calculation.py
7. incident_report_wizard.py
8. medication_reconciliation.py
9. nursing_assessment.py
10. patient_education.py
11. quality_improvement.py
12. sbar_report.py
13. sbar_wizard.py
14. shift_handoff_wizard.py
15. soap_note_wizard.py
16. treatment_plan.py
17. **epic_integration_wizard.py** (✅ Complete - Microsoft-style template)

**Frontend Templates**
- epic-wizard.html (✅ Complete - Microsoft-style with client-side navigation)
- sbar-wizard.html (🔄 Needs upgrade to Microsoft style)
- care-plan-wizard.html (🔄 Needs upgrade)
- patient-education-wizard.html (🔄 Needs upgrade)

---

## Architecture & Design Patterns

### 1. Microsoft-Style Wizard Template (Epic Wizard)

**Key Features to Replicate:**
```javascript
// Client-side navigation (no backend dependency for demo)
function navigateNext() {
    const stepData = collectCurrentStepData();
    Object.assign(wizardState.data, stepData);
    wizardState.current_step = Math.min(wizardState.current_step + 1, totalSteps);
    updateWizardUI({...});
    handleStepSpecificLogic({...});
}
```

**Design Elements:**
- ✅ Progress bar with percentage (0% → 100%)
- ✅ Step indicators (numbered circles: 1→2→3→4...)
- ✅ Card-style form fields with labels
- ✅ Copy-to-clipboard buttons for text fields
- ✅ Password visibility toggles
- ✅ Back/Next/Finish navigation buttons
- ✅ Silent error handling (no intrusive banners)
- ✅ Tailwind CSS styling
- ✅ FontAwesome icons
- ✅ Responsive design

### 2. Backend Architecture (LangChain/LangGraph)

**Epic Wizard Pattern:**
```python
# State machine with TypedDict
class WizardState(TypedDict):
    current_step: int
    completed_steps: List[int]
    messages: List[BaseMessage]
    errors: List[str]
    warnings: List[str]
    # Step-specific fields...

# Step-specific handlers
async def step_1_handler(state: WizardState) -> WizardState:
    # Perform step logic
    state["completed_steps"].append(1)
    return state

# LangGraph workflow
wizard_graph = StateGraph(WizardState)
wizard_graph.add_node("step_1", step_1_handler)
wizard_graph.add_edge("step_1", "step_2")
```

**FastAPI Router Pattern:**
```python
@router.post("/step/{step_number}")
async def submit_step(step_number: int, input_data: Dict):
    # Execute only specific step handler (not full graph)
    handler = step_handlers[step_number]
    result = await handler(state)
    return _build_state_response(result)
```

---

## Implementation Phases

### Phase 1: Foundation & Template (COMPLETE ✅)
**Epic Integration Wizard serves as the master template**

**Deliverables:**
- ✅ Microsoft-style wizard UI (epic-wizard.html)
- ✅ Client-side navigation framework
- ✅ LangChain/LangGraph backend pattern
- ✅ FastAPI step-by-step endpoint architecture
- ✅ Silent error handling for demos
- ✅ Deployed to Railway staging

---

### Phase 2: Priority Clinical Wizards (HIGH PRIORITY 🔥)

#### 2.1 SBAR Report Wizard
**Business Value**: Most commonly used clinical communication tool
**Current Status**: Backend complete, frontend needs upgrade

**Steps:**
1. Situation Assessment
2. Background Information
3. Assessment & Analysis
4. Recommendation & Actions
5. Review & Submit

**Implementation Tasks:**
- [ ] Copy epic-wizard.html as template
- [ ] Replace 7 steps with 5 SBAR-specific steps
- [ ] Design card-style forms for S-B-A-R data entry
- [ ] Add AI-powered suggestion buttons (OpenAI integration)
- [ ] Connect to existing sbar_wizard.py backend
- [ ] Test with sample patient scenarios
- [ ] Deploy to staging

**Data Model:**
```python
class SBARState(TypedDict):
    situation: str  # Chief complaint, vital signs
    background: str  # Medical history, medications
    assessment: str  # Nurse's clinical assessment
    recommendation: str  # Suggested interventions
    patient_mrn: Optional[str]  # Epic integration ready
```

#### 2.2 Medication Reconciliation Wizard
**Business Value**: Critical for patient safety, high error-reduction value

**Steps:**
1. Patient Identification
2. Home Medications Review
3. Hospital Medications Import (Epic)
4. Discrepancy Detection
5. Reconciliation & Approval
6. Final Documentation

**Implementation Tasks:**
- [ ] Epic FHIR MedicationRequest integration
- [ ] Drug interaction checking (FDA API)
- [ ] Visual diff display (added/removed/changed meds)
- [ ] Card-style medication cards with RxNorm codes
- [ ] Barcode scanning for medication verification
- [ ] Print-friendly reconciliation summary

#### 2.3 Discharge Summary Wizard
**Business Value**: Streamlines discharge process, reduces delays

**Steps:**
1. Discharge Readiness Check
2. Diagnosis & Treatment Summary
3. Medications & Instructions
4. Follow-up Care Plan
5. Patient Education Materials
6. Review & Sign

**Implementation Tasks:**
- [ ] Auto-populate from Epic encounter data
- [ ] Generate patient-friendly instructions
- [ ] Multi-language support (existing i18n)
- [ ] PDF generation for patient handout
- [ ] Epic DocumentReference write-back
- [ ] E-signature integration

---

### Phase 3: Assessment & Documentation Wizards (MEDIUM PRIORITY)

#### 3.1 Admission Assessment Wizard
**Steps:**
1. Patient Demographics (Epic auto-fill)
2. Chief Complaint & History
3. Physical Assessment (body systems)
4. Psychosocial Assessment
5. Risk Screening (falls, pressure ulcers)
6. Care Plan Initiation

#### 3.2 Shift Handoff Wizard (I-PASS Format)
**Steps:**
1. Illness Severity
2. Patient Summary
3. Action Items
4. Situational Awareness
5. Synthesis by Receiver

#### 3.3 SOAP Note Wizard
**Steps:**
1. Subjective Data
2. Objective Findings
3. Assessment & Diagnosis
4. Plan & Interventions
5. Documentation Review

#### 3.4 Incident Report Wizard
**Steps:**
1. Incident Details (time, location, type)
2. Patient/Staff Involved
3. Description of Event
4. Immediate Actions Taken
5. Root Cause Analysis
6. Prevention Recommendations

---

### Phase 4: Care Planning & Education (MEDIUM PRIORITY)

#### 4.1 Care Plan Wizard
**Steps:**
1. Problem Identification (NANDA diagnoses)
2. Goal Setting (SMART goals)
3. Intervention Planning
4. Evaluation Criteria
5. Multidisciplinary Coordination

#### 4.2 Patient Education Wizard
**Steps:**
1. Learning Needs Assessment
2. Topic Selection (condition-specific)
3. Material Generation (multi-language)
4. Teach-Back Verification
5. Documentation & Follow-up

#### 4.3 Clinical Assessment Wizard
**Generic assessment framework for specialty units**

---

### Phase 5: Specialized Calculators & Tools (LOW PRIORITY)

#### 5.1 Dosage Calculation Wizard
**Steps:**
1. Medication Selection
2. Patient Parameters (weight, age, renal function)
3. Calculation Method
4. Result Verification
5. Documentation

#### 5.2 Quality Improvement Wizard
**Steps:**
1. QI Project Selection
2. Baseline Data Collection
3. Intervention Planning
4. Implementation Tracking
5. Outcome Measurement
6. PDSA Cycle Documentation

---

## Technical Implementation Guide

### Step-by-Step Wizard Creation Workflow

#### 1. **Copy Template**
```bash
cp static/epic-wizard.html static/new-wizard.html
```

#### 2. **Configure Steps**
```javascript
// Update step configuration
const totalSteps = 5;  // Change from 7
const stepNames = [
    "Patient Info",
    "Assessment",
    "Diagnosis",
    "Plan",
    "Review"
];
```

#### 3. **Design Step Content**
```html
<!-- Step 1: Patient Info -->
<div id="step1Content" class="step-content active">
    <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <h3 class="font-bold text-gray-900 mb-4">Patient Information</h3>
        <div class="grid grid-cols-2 gap-4">
            <!-- Card-style input fields -->
        </div>
    </div>
</div>
```

#### 4. **Implement Data Collection**
```javascript
function collectCurrentStepData() {
    const stepData = {};
    switch (wizardState.current_step) {
        case 1:
            stepData.patient_mrn = document.getElementById('mrn').value;
            stepData.patient_name = document.getElementById('patientName').value;
            break;
        // ... other steps
    }
    return stepData;
}
```

#### 5. **Connect Backend (Optional)**
```python
# Create wizard router at src/routers/wizards/new_wizard.py
router = APIRouter(prefix="/wizard/new-wizard", tags=["New Wizard"])

@router.post("/step/{step_number}")
async def submit_step(step_number: int, data: Dict):
    # Process step with LangGraph
    result = await wizard_graph.ainvoke(data)
    return result
```

#### 6. **Epic Integration Points**
```python
# Add Epic FHIR data fetching
async def step_1_patient_lookup(state: WizardState):
    if config.integration_mode == IntegrationMode.EPIC_INTEGRATED:
        patient = await ehr_service.fetch_patient_by_mrn(state["mrn"])
        state["patient_data"] = patient.dict()
    return state
```

---

## UI/UX Design Standards

### Color Palette
```css
/* Primary Actions */
--primary: #6366f1;  /* Indigo */
--primary-hover: #4f46e5;

/* Success States */
--success: #10b981;  /* Green */

/* Warning/Caution */
--warning: #f59e0b;  /* Amber */

/* Error States */
--error: #ef4444;  /* Red */

/* Neutral/Background */
--gray-50: #f9fafb;
--gray-100: #f3f4f6;
--gray-700: #374151;
--gray-900: #111827;
```

### Typography
```css
/* Headings */
h1: text-3xl font-bold text-gray-900
h2: text-2xl font-bold text-gray-900
h3: text-xl font-semibold text-gray-800
h4: text-lg font-medium text-gray-700

/* Body */
p: text-base text-gray-700
small: text-sm text-gray-600
```

### Form Components
```html
<!-- Text Input Card -->
<div class="bg-white border border-gray-200 rounded-lg p-4">
    <label class="block text-sm font-medium text-gray-700 mb-2">
        Field Label
    </label>
    <div class="relative">
        <input type="text"
               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
               placeholder="Enter value">
        <button class="absolute right-2 top-2 text-gray-400 hover:text-gray-600">
            <i class="fas fa-copy"></i>
        </button>
    </div>
</div>

<!-- Checkbox Card -->
<div class="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
    <label class="flex items-center cursor-pointer">
        <input type="checkbox" class="w-5 h-5 text-indigo-600 rounded">
        <span class="ml-3 text-sm font-medium text-indigo-900">Option Label</span>
    </label>
</div>

<!-- Radio Card -->
<div class="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-indigo-400 cursor-pointer">
    <label class="flex items-center cursor-pointer">
        <input type="radio" name="group" class="w-5 h-5 text-indigo-600">
        <div class="ml-3">
            <div class="text-sm font-semibold text-gray-900">Option Title</div>
            <div class="text-xs text-gray-600">Option description</div>
        </div>
    </label>
</div>
```

---

## Epic Integration Strategy

### Phase A: Standalone Mode (Current)
- ✅ All wizards work without Epic
- ✅ Manual data entry
- ✅ Demo-ready for presentations

### Phase B: Epic Read-Only
**When Epic sandbox credentials available:**
- [ ] Patient lookup by MRN
- [ ] Auto-populate demographics
- [ ] Import active medications
- [ ] Import active diagnoses
- [ ] Import encounter context

**API Endpoints:**
```python
# Epic FHIR R4 endpoints
GET /Patient?identifier={mrn}
GET /MedicationRequest?patient={patient_id}&status=active
GET /Condition?patient={patient_id}&clinical-status=active
GET /Encounter?patient={patient_id}&status=in-progress
```

### Phase C: Epic Write-Back
**Requires Epic App Orchard approval:**
- [ ] Write discharge summaries → DocumentReference
- [ ] Write care plans → CarePlan
- [ ] Write assessments → Observation
- [ ] Write incident reports → DetectedIssue

---

## Testing Strategy

### 1. Unit Tests
```python
# Test each wizard step handler
@pytest.mark.asyncio
async def test_sbar_step_1_situation():
    state = create_initial_state()
    state["situation"] = "Patient with chest pain"

    result = await step_1_situation_handler(state)

    assert result["completed_steps"] == [1]
    assert result["current_step"] == 2
```

### 2. Integration Tests
```python
# Test full wizard flow
@pytest.mark.asyncio
async def test_sbar_full_workflow():
    wizard = SBARWizard()

    # Step 1
    result = await wizard.submit_step(1, {"situation": "..."})
    assert result["current_step"] == 2

    # ... continue through all steps
```

### 3. Epic Mock Server
```python
# Use mock_fhir_server.py for Epic simulation
@pytest.fixture
def mock_epic():
    server = MockFHIRServer()
    server.add_patient("12345678", {...})
    return server
```

### 4. Frontend E2E Tests
```javascript
// Playwright/Cypress tests
test('SBAR wizard completes successfully', async () => {
    await page.goto('/static/sbar-wizard.html');
    await page.fill('#situation', 'Test situation');
    await page.click('#nextBtn');
    // ... continue
});
```

---

## Deployment Plan

### Railway Staging Deployment
```yaml
# railway.toml
[deploy]
startCommand = "/app/start-railway.sh"

[environments.staging]
variables = {
    EPIC_MOCK_MODE = "true",
    ENABLE_ALL_WIZARDS = "true"
}
```

### Production Checklist
- [ ] All wizards pass integration tests
- [ ] Epic FHIR OAuth configured
- [ ] HIPAA compliance review complete
- [ ] User acceptance testing (UAT) with nurses
- [ ] Performance testing (100+ concurrent users)
- [ ] Documentation complete
- [ ] Training materials ready

---

## Success Metrics

### Developer Metrics
- ✅ Time to create new wizard: < 2 hours (using template)
- ✅ Code reuse: > 80% (shared components)
- ✅ Test coverage: > 90%

### User Metrics
- Time to complete wizard: < 3 minutes (vs 10-15 manual)
- Data entry reduction: 70-80%
- Error rate: < 1%
- User satisfaction: > 4.5/5

### Clinical Metrics
- Documentation time savings: 5-10 min/patient
- Transcription error reduction: > 90%
- Workflow interruptions: -50%

---

## Team Assignments & Timeline

### Immediate Next Steps (Week 1)
- [ ] **Epic Wizard**: Deploy latest fixes to Railway ✅
- [ ] **SBAR Wizard**: Upgrade to Microsoft style (2 days)
- [ ] **Medication Rec**: Start frontend design (3 days)

### Sprint 1 (Weeks 2-3)
- [ ] Complete SBAR, Medication Rec, Discharge Summary
- [ ] Create reusable wizard component library
- [ ] Document wizard creation process

### Sprint 2 (Weeks 4-5)
- [ ] Admission Assessment, Shift Handoff, SOAP Note
- [ ] Epic integration testing with sandbox
- [ ] Performance optimization

### Sprint 3 (Weeks 6-7)
- [ ] Incident Report, Care Plan, Patient Education
- [ ] Final QA and bug fixes
- [ ] Production deployment preparation

---

## Risk Management

### Technical Risks
| Risk | Mitigation |
|------|-----------|
| Epic credentials delay | Build all wizards in standalone mode first |
| OAuth complexity | Use proven libraries (Authlib, HTTPX) |
| Performance issues | Implement caching, async processing |
| Browser compatibility | Test on Chrome, Safari, Firefox, Edge |

### Clinical Risks
| Risk | Mitigation |
|------|-----------|
| Incorrect medical logic | Nurse review of all workflows |
| Incomplete assessments | Required field validation |
| Data loss | Auto-save every 30 seconds |

---

## Appendix

### A. Wizard Naming Conventions
```
File naming:
- Backend: {wizard_name}_wizard.py
- Frontend: {wizard-name}-wizard.html
- Tests: test_{wizard_name}_wizard.py

API Routes:
- /api/v1/wizard/{wizard-name}/start
- /api/v1/wizard/{wizard-name}/step/{number}
- /api/v1/wizard/{wizard-name}/complete
```

### B. Wizard State Schema
```typescript
interface WizardState {
    current_step: number;
    completed_steps: number[];
    total_steps: number;
    progress_percent: number;
    step_name: string;
    step_description: string;
    can_proceed: boolean;
    errors: string[];
    warnings: string[];
    messages: Message[];
    state_data: Record<string, any>;
}
```

### C. Epic FHIR Resources Reference
- **Patient**: Demographics, identifiers (MRN)
- **Encounter**: Visit type, location, attending
- **Condition**: Diagnoses (ICD-10, SNOMED)
- **MedicationRequest**: Active meds (RxNorm)
- **AllergyIntolerance**: Drug/food allergies
- **Observation**: Vital signs, lab results
- **DocumentReference**: Clinical notes, summaries
- **CarePlan**: Treatment plans, goals

---

## Conclusion

This comprehensive plan provides a roadmap for implementing all 17 clinical wizards using the Epic Integration Wizard as the gold standard template. By following the Microsoft-style design pattern and maintaining consistency across all wizards, AI Nurse Florence will deliver a professional, nurse-friendly experience that significantly reduces documentation burden and improves patient care quality.

**Next Action**: Begin SBAR Wizard upgrade to Microsoft style (est. 2 days).

---

**Document Version**: 1.0
**Last Updated**: 2025-10-10
**Review Date**: Weekly during implementation
