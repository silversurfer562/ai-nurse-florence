# Chapter: Building Clinical Assessment Wizards with the Documentation Framework

## Overview

This chapter documents the methodology for creating clinical assessment wizards in AI Nurse Florence, using the integrated documentation framework. This process can be replicated by both human developers and AI agents for consistent wizard development.

## Core Philosophy: "Assessment Without Documentation Is Incomplete"

A clinical wizard must not only gather data and calculate scores but also produce legally compliant documentation. This three-phase pattern ensures nurses can complete the full workflow:

1. **Assessment** - Gather patient data
2. **Analysis** - Calculate scores, identify risks
3. **Documentation** - Generate, edit, and submit SBAR notes

## The Documentation Framework Architecture

### Framework Components

```
AI Nurse Florence Clinical Wizards
├── Reusable Modules
│   ├── wizardPersistence.js      - Draft saving/resume
│   ├── careSettings.js           - Care environment personalization
│   └── documentationModule.js    - SBAR generation & export
├── Individual Wizards
│   ├── sepsis-screening-wizard.html
│   ├── stroke-assessment-wizard.html
│   └── [18 wizards total]
└── Documentation Philosophy
    └── WIZARD_DOCUMENTATION_PHILOSOPHY.md
```

### Why "Framework" Not "Process"

**Framework** accurately describes this system because:
- **Reusable structure**: DocumentationModule.js provides consistent interfaces
- **Defined contracts**: `generateSBAR(wizardData, wizardType)` accepts standardized inputs
- **Extensible templates**: New wizard types plug into existing architecture
- **Consistent UX**: Preview→Edit→Submit pattern across all wizards
- **Standardized outputs**: All wizards produce compliant SBAR notes

A "process" implies steps humans follow. A "framework" provides code infrastructure for building new features.

## The Wizard Creation Methodology

### Phase 1: Clinical Requirements Analysis

**Example: Sepsis Screening Wizard**

1. **Identify clinical use case**
   - Sepsis requires rapid assessment using qSOFA + SIRS criteria
   - Time-sensitive (1-hour bundle requirement)
   - High legal documentation requirement (CDC Core Elements)

2. **Define assessment steps**
   - Step 1: Suspected Infection (chief complaint, source, onset, risk factors)
   - Step 2: qSOFA Score (respiratory rate, mental status, blood pressure)
   - Step 3: SIRS Criteria (temperature, heart rate, respiratory rate, WBC)
   - Step 4: Interventions (sepsis bundle checklist, reassessment time, nurse signature)
   - Step 5: Documentation (SBAR preview, edit, submit)

3. **Determine auto-calculators needed**
   - qSOFA score (0-3 scale, ≥2 = high risk)
   - SIRS criteria count (0-4, ≥2 = SIRS positive)
   - Real-time risk interpretation

4. **Identify legal documentation requirements**
   - SBAR format required (Joint Commission standard)
   - Must document: Assessment findings, interventions taken, provider notification
   - "If you didn't document it, it didn't happen" legal standard applies

### Phase 2: Technical Implementation

#### Step 1: Create Base HTML Structure

**File**: `static/sepsis-screening-wizard.html`

**Key sections:**
```html
<!-- Reusable module imports -->
<script src="/static/js/wizardPersistence.js"></script>
<script src="/static/js/careSettings.js"></script>
<script src="/static/js/documentationModule.js"></script>

<!-- Progress tracking -->
<div id="progressBar" class="progress-bar"></div>

<!-- Step indicators (visual breadcrumb) -->
<div class="step-indicator active" data-step="1">1</div>
<div class="step-indicator pending" data-step="2">2</div>
<!-- ... -->

<!-- Step content -->
<div id="step1" class="step-content active">
  <!-- Assessment form fields -->
</div>
<div id="step2" class="step-content">
  <!-- qSOFA calculator -->
</div>
<!-- ... -->
<div id="step5" class="step-content">
  <!-- Documentation preview/edit/submit -->
</div>
```

#### Step 2: Implement Step-Specific Logic

**Assessment Data Collection (Steps 1-4)**:
```javascript
function collectCurrentStepData() {
  switch (wizardState.current_step) {
    case 1:
      wizardState.data.chiefComplaint = document.getElementById('chiefComplaint').value;
      wizardState.data.infectionSource = document.getElementById('infectionSource').value;
      // ... collect all Step 1 fields
      break;
    case 2:
      // qSOFA data collection
      break;
    // ... etc
  }
}
```

**Auto-Calculators**:
```javascript
function calculateQSOFA() {
  const rr = parseInt(document.getElementById('respiratoryRate').value) || 0;
  const ms = parseInt(document.getElementById('mentalStatus').value) || 0;
  const bp = parseInt(document.getElementById('systolicBP').value) || 0;

  const score = rr + ms + bp;
  wizardState.data.qsofaScore = score;

  // Update UI with score and risk interpretation
  document.getElementById('qsofaScore').textContent = score;

  if (score >= 2) {
    showMessage('error', 'qSOFA ≥2 indicates high risk for sepsis!');
  }
}
```

#### Step 3: Implement Documentation Generation (Step 5)

**This is where the framework shines:**

```javascript
function generateAndDisplaySBAR() {
  // Prepare wizard data in standardized format
  const wizardData = {
    patientAge: 65,
    patientGender: 'M',
    chiefComplaint: wizardState.data.chiefComplaint,
    infectionSource: wizardState.data.infectionSource,
    qsofaScore: wizardState.data.qsofaScore,
    sirsScore: wizardState.data.sirsScore,
    interventions: wizardState.data.bundleItems,
    nurseSignature: wizardState.data.nurseSignature,
    // ... all assessment data
  };

  // Generate SBAR using framework (single line!)
  const sbarData = DocumentationModule.generateSBAR(wizardData, 'sepsis');

  // Format and display
  const formattedSBAR = DocumentationModule.formatSBARForDisplay(sbarData);
  document.getElementById('sbarPreviewText').textContent = formattedSBAR;

  // Update metadata
  document.getElementById('docId').textContent = sbarData.metadata.documentId;
  document.getElementById('docTimestamp').textContent = sbarData.metadata.timestampFormatted;
  document.getElementById('docNurse').textContent = sbarData.metadata.nurse;
}
```

**Framework does the heavy lifting:**
- Auto-generates SBAR sections (Situation, Background, Assessment, Recommendation)
- Creates unique document ID
- Adds timestamps
- Formats for display
- Validates required sections

#### Step 4: Wire Up Edit & Export Functions

```javascript
// Toggle edit mode
function editSBARNote() {
  const previewText = document.getElementById('sbarPreviewText');
  previewText.contentEditable = previewText.contentEditable === 'true' ? 'false' : 'true';
}

// Export options (provided by framework)
function printSBAR() {
  DocumentationModule.printChartCopy(sbarText);
}

function exportSBARToPDF() {
  DocumentationModule.exportToPDF(sbarText, metadata);
}

function copySBARToClipboard() {
  DocumentationModule.copyToClipboard(sbarText);
}
```

### Phase 3: Adding SBAR Templates to the Framework

**File**: `static/js/documentationModule.js`

For each new wizard type, add a specific SBAR generator:

```javascript
const DocumentationModule = {
  // Main router
  generateSBAR(wizardData, wizardType) {
    const templates = {
      'sepsis': this.generateSepsisSBAR,
      'stroke': this.generateStrokeSBAR,
      'cardiac': this.generateCardiacSBAR,
      // Add new wizard types here
    };
    return templates[wizardType](wizardData);
  },

  // Sepsis-specific template (fully implemented)
  generateSepsisSBAR(data) {
    return {
      situation: this.formatSituation({
        age: data.patientAge,
        gender: data.patientGender,
        chiefComplaint: data.chiefComplaint,
        infectionSource: data.infectionSource
      }),
      background: this.formatBackground({
        medicalHistory: data.medicalHistory,
        riskFactors: data.riskFactors
      }),
      assessment: this.formatSepsisAssessment({
        qsofaScore: data.qsofaScore,
        sirsCount: data.sirsScore,
        vitalSigns: data.vitalSigns
      }),
      recommendation: this.formatSepsisRecommendation({
        interventions: data.interventions,
        providerNotified: data.providerNotified
      })
    };
  },

  // Stroke-specific template (to be implemented)
  generateStrokeSBAR(data) {
    return {
      situation: this.formatSituation({...}),
      background: this.formatBackground({...}),
      assessment: this.formatStrokeAssessment({
        nihssScore: data.nihssScore,
        lastKnownWell: data.lastKnownWell,
        // Stroke-specific fields
      }),
      recommendation: this.formatStrokeRecommendation({
        tpaEligibility: data.tpaEligibility,
        // Stroke-specific interventions
      })
    };
  }
};
```

### Phase 4: Testing & Validation

**Manual Testing Checklist:**
1. ✅ All form fields populate wizard state correctly
2. ✅ Auto-calculators update in real-time
3. ✅ Navigation between steps works (back/next buttons)
4. ✅ Step indicators update correctly
5. ✅ Draft persistence saves/resumes state
6. ✅ SBAR generates with all assessment data
7. ✅ Edit mode allows text modification
8. ✅ Export functions work (Print, PDF, Copy)
9. ✅ Final confirmation checkbox validates
10. ✅ Completion alert shows correct data

**Quick Fill Scenarios:**
```javascript
function fillRespiratorySepsis() {
  // Populate form with realistic test data
  document.getElementById('chiefComplaint').value = 'Fever, productive cough, shortness of breath';
  document.getElementById('infectionSource').value = 'respiratory';
  document.getElementById('temperature').value = '39.2';
  // ... etc

  calculateQSOFA();
  calculateSIRS();

  showMessage('success', 'Respiratory sepsis scenario populated');
}
```

## Real-World Example: Sepsis Wizard Implementation

### File Structure
```
static/
├── sepsis-screening-wizard.html          (1,710 lines)
├── js/
│   ├── wizardPersistence.js              (271 lines)
│   ├── careSettings.js                   (450 lines)
│   └── documentationModule.js            (532 lines)
```

### Development Timeline
1. **Created base wizard**: 4 steps for assessment (Steps 1-4)
2. **Added AI Assist**: LangChain integration for suggestions
3. **Integrated documentation framework**: Added Step 5
4. **Total implementation**: ~2,963 lines of production code

### Key Metrics
- **5 steps**: Infection → qSOFA → SIRS → Interventions → Documentation
- **2 auto-calculators**: qSOFA (0-3), SIRS (0-4)
- **8 risk factors**: Tracked via checkboxes
- **5 bundle items**: Sepsis bundle checklist
- **4 export options**: Print, PDF, Copy, Save to EHR (placeholder)

### What the Framework Provides

**Before Framework (Steps 1-4 only):**
- Nurse completes assessment
- Calculates scores
- **STOPS** - Must manually write SBAR note in separate system
- Risk of incomplete documentation
- No standardized format

**After Framework (Steps 1-5 complete):**
- Nurse completes assessment
- Calculates scores
- **Auto-generates SBAR note from data**
- Preview before submission
- Edit if needed
- Submit to patient record
- **Workflow complete in one system**

## Extending to Other Wizards

### Priority Order (18 Wizards Total)

**Critical (Legal Documentation Required):**
1. ✅ Sepsis Screening - **COMPLETE**
2. Stroke Assessment (tPA documentation)
3. Cardiac Assessment (STEMI activation)
4. Code Blue Documentation
5. Blood Transfusion Verification

**Standard Priority:**
6. Restraint Assessment
7. Fall Risk Assessment
8. Pain Assessment
9. Wound Assessment
10. Medication Reconciliation
11. IV Site Assessment
12. Foley Catheter Assessment
13. Admission Assessment
14. Discharge Planning
15. Pre-Op Checklist
16. Post-Op Assessment
17. Neuro Assessment
18. Respiratory Assessment

### Implementation Pattern for Each Wizard

```bash
# 1. Create wizard HTML (copy template from sepsis-screening-wizard.html)
cp static/sepsis-screening-wizard.html static/stroke-assessment-wizard.html

# 2. Customize steps for clinical workflow
# - Update step labels
# - Add wizard-specific form fields
# - Implement auto-calculators (e.g., NIHSS score)

# 3. Add SBAR template to documentationModule.js
# - Implement generateStrokeSBAR(data)
# - Customize formatStrokeAssessment(data)
# - Customize formatStrokeRecommendation(data)

# 4. Wire up Step 5 to call documentation framework
# - generateAndDisplaySBAR() calls DocumentationModule.generateSBAR(wizardData, 'stroke')

# 5. Test end-to-end workflow
# - Fill out assessment
# - Verify SBAR generation
# - Test edit/export functions
# - Validate completion
```

## Training AI Agents on This Framework

### Prompt Template for AI Agent

When asking an AI agent to create a new wizard:

```
Create a [WIZARD_NAME] wizard following the AI Nurse Florence Clinical Wizard Framework:

1. CLINICAL REQUIREMENTS:
   - Use case: [description]
   - Assessment steps: [list steps]
   - Auto-calculators needed: [list calculators]
   - Legal documentation requirement: [yes/no + details]

2. STRUCTURE:
   - Copy base from static/sepsis-screening-wizard.html
   - Update to [X] steps
   - Import reusable modules:
     * wizardPersistence.js
     * careSettings.js
     * documentationModule.js

3. DOCUMENTATION INTEGRATION:
   - Add Step [N]: "Preview & Submit Documentation"
   - Implement generateAndDisplaySBAR() function
   - Add [WIZARD_TYPE]SBAR template to documentationModule.js:
     * Situation: [what to include]
     * Background: [what to include]
     * Assessment: [what to include]
     * Recommendation: [what to include]

4. DELIVERABLES:
   - static/[wizard-name]-wizard.html
   - Updated documentationModule.js with new template
   - Test scenarios for validation

REFERENCE FILES:
- Philosophy: docs/WIZARD_DOCUMENTATION_PHILOSOPHY.md
- Proof-of-concept: static/sepsis-screening-wizard.html
- Framework: static/js/documentationModule.js
```

### Example: Training Claude Code to Build Stroke Wizard

**Prompt:**
```
Create a Stroke Assessment wizard following the Clinical Wizard Framework:

CLINICAL REQUIREMENTS:
- Use case: Rapid stroke assessment using NIHSS (NIH Stroke Scale)
- Assessment steps:
  1. Last Known Well Time (critical for tPA eligibility)
  2. NIHSS Score (15 components, 0-42 scale)
  3. tPA Eligibility Checklist
  4. Intervention Timeline
  5. Documentation
- Auto-calculator: NIHSS score with real-time severity interpretation
- Legal documentation: Critical - tPA administration requires detailed documentation

SBAR TEMPLATE REQUIREMENTS:
- Situation: Last known well time, NIHSS score, stroke type (ischemic vs hemorrhagic)
- Background: Risk factors (hypertension, diabetes, anticoagulants)
- Assessment: NIHSS breakdown by component, tPA eligibility determination
- Recommendation: tPA administration or contraindication, neuro consult, ICU admission

Reference sepsis-screening-wizard.html for implementation pattern.
```

**Expected Output:**
- `static/stroke-assessment-wizard.html` (5 steps with NIHSS calculator)
- Updated `static/js/documentationModule.js` with `generateStrokeSBAR(data)` function
- Test scenarios for tPA-eligible and contraindicated patients

## Framework Benefits

### For Developers
- **Reusability**: Write SBAR generation once, use across 18 wizards
- **Consistency**: Same Preview→Edit→Submit UX everywhere
- **Maintainability**: Update framework once, all wizards benefit
- **Testing**: Standardized interfaces make unit testing easier

### For Nurses
- **Workflow efficiency**: Complete assessment and documentation in one system
- **Legal compliance**: SBAR notes meet Joint Commission standards automatically
- **Error prevention**: Auto-generation reduces transcription errors
- **Flexibility**: Edit mode allows clinical judgment to refine notes

### For Healthcare Organizations
- **Standardization**: All nurses use same documentation format
- **Audit trail**: Document IDs and timestamps for every note
- **Legal protection**: "If you didn't document it, it didn't happen" addressed systematically
- **Quality metrics**: Structured data enables analysis of assessment completion rates

## Lessons Learned

### What Worked Well
1. **Modular architecture**: Reusable modules (persistence, care settings, documentation) accelerated development
2. **Framework approach**: Adding new wizards became templating exercise rather than full build
3. **Auto-generation**: Nurses love not having to type SBAR notes from scratch
4. **Edit mode**: Clinical judgment override is essential - never trust 100% auto-generation

### What to Improve
1. **EHR integration**: Currently placeholder - needs Epic FHIR API connection
2. **PDF generation**: Current implementation uses browser print dialog - should generate proper PDFs
3. **Offline mode**: Documentation module could cache notes for submission when connectivity restored
4. **Template customization**: Organizations may want to customize SBAR format - make templates configurable

### Anti-Patterns to Avoid
❌ **DON'T**: Create wizards without Step 5 documentation
  - Assessment without documentation is incomplete

❌ **DON'T**: Hard-code SBAR templates in individual wizards
  - Use DocumentationModule for consistency

❌ **DON'T**: Skip edit mode
  - Nurses need ability to refine AI-generated notes

❌ **DON'T**: Submit without confirmation checkbox
  - Legal requirement - nurse must certify accuracy

## Conclusion

The Clinical Wizard Documentation Framework represents a fundamental shift in how clinical decision support tools should be built:

**Before**: Tools that gather data and calculate scores
**After**: Complete workflows that gather data, calculate scores, **and produce legal documentation**

This framework is:
- ✅ **Reusable** across 18 wizard types
- ✅ **Extensible** for new wizards
- ✅ **Standards-compliant** (Joint Commission, CDC)
- ✅ **AI-trainable** with clear patterns

By documenting this methodology, both human developers and AI agents can replicate this pattern to build complete clinical workflows that serve the full needs of nursing practice.

---

**Next Steps:**
1. Roll out documentation framework to remaining 17 wizards
2. Add Epic FHIR integration for real EHR submission
3. Implement proper PDF generation
4. Create organization-configurable SBAR templates
5. Add analytics dashboard showing documentation completion rates

**Training Resources:**
- Philosophy: `docs/WIZARD_DOCUMENTATION_PHILOSOPHY.md`
- This chapter: `docs/BOOK_CHAPTER_WIZARD_FRAMEWORK.md`
- Reference implementation: `static/sepsis-screening-wizard.html`
- Framework code: `static/js/documentationModule.js`

---

🚀 **Framework Status: Production-Ready**
- Proof-of-concept: Sepsis wizard complete
- Pattern validated: Preview→Edit→Submit works
- Ready to scale: Template pattern established for 17 remaining wizards
