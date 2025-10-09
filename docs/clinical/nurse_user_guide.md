# AI Nurse Florence: User Guide for Healthcare Professionals

**Who This Is For**: Registered nurses (RN), nurse practitioners (NP), physician assistants (PA), and other healthcare professionals providing direct patient care. This guide helps you use Florence to access evidence-based medical information, generate clinical documentation, and support patient education.

**Prerequisites**:
- Active clinical practice or healthcare education role
- Basic computer literacy and web browser access
- Understanding of clinical terminology and workflows
- No technical/programming knowledge required

**Time**: 15-20 minutes to read; 5 minutes to start using Florence for basic tasks.

---

## Table of Contents

- [Getting Started](#getting-started)
- [Accessing Florence](#accessing-florence)
- [Key Features](#key-features)
  - [Disease Lookup](#disease-lookup)
  - [Medical Literature Search](#medical-literature-search)
  - [Clinical Text Summarization](#clinical-text-summarization)
  - [Patient Education Materials](#patient-education-materials)
- [Tips for Effective Use](#tips-for-effective-use)
- [Important Reminders](#important-reminders)
- [Getting Help](#getting-help)
- [Related Resources](#related-resources)

---

## Getting Started

Florence is designed to help you access reliable medical information quickly. You can use Florence to:

- Look up diseases and medical conditions
- Search for relevant medical literature
- Summarize clinical text
- Generate patient education materials
- Find clinical trials
- Analyze the readability of health content

## Accessing Florence

Florence is available through:

1. **Web Interface**: Visit [nurse.florence-ai.org](https://nurse.florence-ai.org) and log in with your credentials
2. **Mobile App**: Download the Florence app from the App Store or Google Play
3. **Integration with EMR**: Access through the "Florence" tab in your EMR system (if enabled by your organization)

## Key Features

### Disease Lookup

Get reliable information about medical conditions including symptoms, causes, treatments, and evidence-based references.

**How to use:**
- Type a disease or condition name in the search box
- View the structured information and references
- Use the "Save to Notes" feature to include in patient documentation

**Example queries:**
- Type 2 diabetes management
- Heart failure with preserved ejection fraction
- Asthma exacerbation guidelines

### Medical Literature Search

Search PubMed and other medical databases for relevant literature.

**How to use:**
- Enter your clinical question
- Filter results by publication date, study type, or specialty
- Save references or export citations

**Example queries:**
- Effectiveness of SGLT2 inhibitors in heart failure
- Nursing interventions to prevent pressure ulcers
- Latest guidelines for post-operative pain management

### Clinical Text Summarization

Generate concise summaries of clinical notes, research papers, or other medical text.

**How to use:**
- Paste or upload the text you want to summarize
- Select the desired length and focus (e.g., "treatment focused")
- Review and edit the generated summary

**Tip:** If your request is unclear, Florence might ask for clarification to provide a better summary.

### Patient Education Materials

Create easy-to-understand patient education materials for various conditions.

**How to use:**
- Enter the condition and specific aspects to cover
- Select reading level and language
- Add custom notes if needed

**Example uses:**
- Create a handout on insulin administration for newly diagnosed diabetes patients
- Generate diet recommendations for patients with GERD
- Prepare post-discharge care instructions for heart failure patients

## Tips for Effective Use

1. **Be specific in your queries** - The more specific your question, the better Florence can help.

2. **Refine when prompted** - If Florence asks for clarification, providing more details will improve results.

3. **Review all information** - Always use your clinical judgment and verify information before using it in patient care.

4. **Save frequently used queries** - Bookmark searches or summaries you use often for quick access.

5. **Provide feedback** - Use the feedback button to help improve Florence's responses.

## Important Reminders

- Florence provides information to support clinical decision-making but is not a substitute for professional judgment.
- All information should be verified against current clinical practice guidelines.
- No patient health information (PHI) is stored when using Florence.
- Always follow your organization's policies regarding the use of AI tools in clinical practice.

## Getting Help

If you need assistance with Florence:

- Click the "Help" icon in the application
- Email support at help@florence-ai.org
- Contact your organization's Florence administrator

## Training Resources

To build your skills with Florence:

- Watch tutorial videos in the Learning Center
- Join monthly webinars (schedule available in the app)
- Complete the online training modules for continuing education credits

---

## Common Troubleshooting

### Epic Connection Issues

**Problem**: Cannot connect to Epic EHR
**Solution**:
1. Verify Epic integration is enabled in Settings
2. Check OAuth token is valid (Settings > Epic Integration > Connection Status)
3. Ensure you're on hospital network or approved VPN
4. Contact IT if "Authentication Failed" appears
5. Verify your Epic credentials in Settings

**Problem**: Patient data not loading from Epic
**Solution**:
1. Verify correct MRN format (7-10 digits, no spaces or dashes)
2. Check patient exists in Epic system
3. Confirm you have appropriate Epic permissions for patient data access
4. Try refreshing the page
5. If issue persists, contact clinical informatics team

### Medication Lookup Issues

**Problem**: Medication not found in database
**Solution**:
1. Try generic name instead of brand name (e.g., "metformin" not "Glucophage")
2. Check spelling (use autocomplete when available)
3. Search by RxNorm code if available
4. Use "Drug Information" tab for broader search
5. Contact pharmacy if medication should be in formulary

**Problem**: Drug interaction warning appears
**Solution**:
1. **DO NOT IGNORE** - interaction warnings indicate potential patient safety risk
2. Document the interaction warning
3. Notify prescribing physician before administering
4. If medications already ordered, verify with pharmacy
5. Document physician's response in patient chart

### Discharge Planning Issues

**Problem**: Generated discharge instructions don't match physician orders
**Solution**:
1. **NEVER use conflicting instructions** - patient safety risk
2. Manually edit discharge instructions to match physician orders
3. When in doubt, consult physician for clarification
4. Document any discrepancies in nursing notes
5. Always verify medications against Epic MAR

**Problem**: Patient has complex medication regimen - discharge instructions too long
**Solution**:
1. Prioritize essential medications in main document
2. Use "Medication List" section for complete list
3. Create separate handout for complex instructions (e.g., insulin sliding scale)
4. Schedule medication reconciliation with pharmacist
5. Provide pharmacy phone number for patient questions

### Patient Education Material Issues

**Problem**: Reading level too high for patient
**Solution**:
1. Use "Reading Level" slider in Patient Education wizard
2. Select "5th-6th grade" for most patients
3. Use "Simple Language" option
4. Add pictures/diagrams when available
5. Provide verbal explanation alongside written materials

**Problem**: Patient speaks language other than English
**Solution**:
1. Use Florence's multi-language support (Settings > Language)
2. Current languages: English, Spanish (more coming soon)
3. For other languages, use hospital interpreter services
4. Provide translated materials from MedlinePlus (available in 45+ languages)
5. Document language barrier and interpreter use

### SBAR Report Issues

**Problem**: Generated SBAR missing critical information
**Solution**:
1. SBAR is a **starting template**, not complete report
2. Always add patient-specific details:
   - Exact vital signs
   - Recent lab values
   - Medication changes
   - Patient-specific concerns
3. Review with supervising RN before calling physician
4. Use as communication guide, not word-for-word script

### Technical Issues

**Problem**: Page won't load / Slow performance
**Solution**:
1. Check internet connection
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try different browser (Chrome, Firefox, Safari, Edge)
4. Disable browser extensions temporarily
5. Contact IT Help Desk: [your hospital IT number]

**Problem**: Lost unsaved work
**Solution**:
1. Florence auto-saves every 60 seconds for wizards
2. Check "Recent Sessions" to recover
3. For long documentation, copy to clipboard periodically
4. Use Epic for official documentation (Florence is for drafting)

**Problem**: Can't print discharge instructions
**Solution**:
1. Use browser print function (Ctrl+P / Cmd+P)
2. Select "Save as PDF" to create digital copy
3. Copy text into Epic and print from there
4. Adjust print layout in Settings if formatting issues
5. Contact IT if printer not available

---

## Clinical Workflow Examples

### Example 1: Emergency Department Discharge

**Scenario**: 67-year-old patient treated for pneumonia, ready for discharge

**Florence Workflow**:

1. **Open Discharge Wizard**
   - Navigate to Wizards > Discharge Planning
   - Select "Emergency Department Discharge"

2. **Enter Patient Information** (NO PHI)
   - Age: 67
   - Diagnosis: Community-acquired pneumonia (J18.9)
   - Treatment: IV antibiotics, fluids

3. **Medications Section**
   - Add: Amoxicillin-clavulanate 875mg PO BID x 7 days
   - Add: Guaifenesin 400mg PO Q4H PRN cough
   - Florence auto-populates administration instructions

4. **Warning Signs Section**
   - Florence generates standard pneumonia warning signs:
     - Difficulty breathing
     - High fever >102°F
     - Chest pain
     - Confusion
   - **Nurse adds**: "Call 911 if lips/fingernails turn blue"

5. **Follow-up Instructions**
   - Florence suggests: "Follow up with primary care in 3-5 days"
   - **Nurse customizes**: "Dr. Johnson at ABC Clinic, appointment scheduled for [DATE]"

6. **Review & Print**
   - Review entire document for accuracy
   - Verify medications match Epic MAR
   - Print 2 copies (one for patient, one for chart)
   - Provide verbal education to patient

**Time Saved**: 10-15 minutes compared to manual documentation

---

### Example 2: Medical-Surgical Unit Handoff

**Scenario**: End of shift, handing off 5 patients to night shift RN

**Florence Workflow**:

1. **Open Shift Handoff Wizard**
   - Wizards > Shift Handoff Report
   - Select "Med-Surg Unit"

2. **Patient 1: Post-op Day 2 Hip Replacement**
   - Situation: Stable, ambulating with PT
   - Assessment: Pain 4/10 controlled with Norco
   - Tasks for Next Shift:
     - Give Coumadin at 1800 (already prepared)
     - Check INR results when available
     - Continue DVT prophylaxis
   - Watch For: Increased pain, signs of DVT

3. **Patient 2: CHF Exacerbation**
   - Situation: Improving, O2 sat 95% on 2L
   - Assessment: Weight down 3kg from admission
   - Tasks for Next Shift:
     - I&O monitoring (restrict fluids to 1500mL/day)
     - Daily weight at 0600
     - Furosemide 40mg IV at 0600
   - Watch For: Respiratory distress, declining O2 sat

4. **Generate Report**
   - Florence creates structured handoff document
   - Print for receiving RN
   - Walk rounds together using report as guide

**Time Saved**: 5-7 minutes per patient (25-35 minutes total)
**Safety Benefit**: Standardized format reduces communication errors

---

### Example 3: Patient Education for New Diagnosis

**Scenario**: Patient newly diagnosed with Type 2 Diabetes, needs education on insulin

**Florence Workflow**:

1. **Open Patient Education Wizard**
   - Wizards > Patient Education
   - Topic: Diabetes Management

2. **Customize Content**
   - Select subtopics:
     - What is Type 2 Diabetes?
     - Blood sugar monitoring
     - Insulin injection technique
     - Hypoglycemia warning signs
     - Diet recommendations
   - Reading level: 6th grade
   - Include: Pictures of injection sites

3. **Generate Materials**
   - Florence creates patient-friendly handout
   - Uses plain language ("high blood sugar" instead of "hyperglycemia")
   - Includes visual aids

4. **Nurse Customization**
   - Add patient's specific insulin regimen:
     - "Lantus 20 units at bedtime"
     - "Humalog 8 units before meals"
   - Add prescriber contact: "Dr. Smith, Endocrinology, (555) 123-4567"
   - Add demonstration notes: "Return demonstration completed successfully"

5. **Education Session**
   - Review handout with patient
   - Demonstrate insulin injection
   - Patient performs return demonstration
   - Assess understanding with teach-back method
   - Document education in Epic

**Patient Outcome**: Written reinforcement of verbal teaching improves compliance

---

## Quick Reference Card

**Copy this page for your badge/pocket reference**

---

### Florence Quick Actions

| Task | Navigation | Keyboard Shortcut |
|------|------------|-------------------|
| New SBAR Report | Wizards > SBAR | Alt+S |
| Discharge Planning | Wizards > Discharge | Alt+D |
| Drug Lookup | Tools > Medication Info | Alt+M |
| Patient Education | Wizards > Education | Alt+E |
| Disease Lookup | Tools > Disease Info | Alt+I |
| Search PubMed | Research > PubMed | Alt+P |

### Common Diagnoses - ICD-10 Codes

| Diagnosis | ICD-10 Code |
|-----------|-------------|
| Pneumonia | J18.9 |
| CHF | I50.9 |
| COPD exacerbation | J44.1 |
| Type 2 Diabetes | E11.9 |
| UTI | N39.0 |
| Cellulitis | L03.90 |
| Chest pain | R07.9 |
| Abdominal pain | R10.9 |

### Medication Frequency Abbreviations

| Abbreviation | Meaning | Example Schedule |
|--------------|---------|------------------|
| QD / Daily | Once daily | 0800 |
| BID | Twice daily | 0800, 2000 |
| TID | Three times daily | 0800, 1400, 2000 |
| QID | Four times daily | 0800, 1200, 1600, 2000 |
| Q4H | Every 4 hours | Round-the-clock |
| Q6H | Every 6 hours | 0000, 0600, 1200, 1800 |
| AC | Before meals | 30 min before eating |
| PC | After meals | With/after food |
| HS | At bedtime | 2100 |
| PRN | As needed | Only when necessary |

### Emergency Contact Numbers

| Issue | Contact |
|-------|---------|
| Epic Login Issues | IT Help Desk: [NUMBER] |
| Florence Technical Issues | Clinical Informatics: [NUMBER] |
| Medication Questions | Pharmacy: [NUMBER] |
| Patient Safety Concern | Supervisor / Charge Nurse |
| HIPAA Violation | Privacy Officer: [NUMBER] |

### Safety Reminders

**Before Using Florence:**
- [ ] No patient names or MRNs
- [ ] Verify on secure network
- [ ] For education/templates only (not emergencies)

**Before Giving to Patient:**
- [ ] Reviewed all content for accuracy
- [ ] Verified against physician orders
- [ ] Checked patient allergies
- [ ] Customized for patient's needs
- [ ] Provided verbal education

### When to Call Physician (SBAR)

**Situation**: State problem clearly
**Background**: Relevant patient history
**Assessment**: Your clinical interpretation
**Recommendation**: What you think should be done

**Critical Values Requiring Notification:**
- HR <50 or >110
- BP <90/60 or >180/120
- RR <10 or >24
- O2 sat <90%
- Temperature <35°C or >39.5°C
- Glucose <60 or >400
- New chest pain, SOB, altered mental status

---

## Related Resources

**For Clinical Use:**
- [Clinical Glossary](./CLINICAL_GLOSSARY.md) - Medical terminology and abbreviations reference
- [Safety Best Practices](./SAFETY_BEST_PRACTICES.md) - Concrete safety protocols with code examples
- [Clinical Workflows](./clinical-workflows.md) - Common clinical use cases and workflows
- [Evidence Standards](./evidence-standards.md) - How Florence sources and validates medical information
- [Safety Guidelines](./safety-guidelines.md) - Patient safety protocols and best practices

**For Technical Information:**
- [API Documentation](../technical/api-documentation.md) - If integrating Florence with your EMR/EHR
- [Quick Start Guide](../getting-started/quick-start.md) - For IT staff setting up Florence

**For Learning More:**
- [Development Philosophy](../DEVELOPMENT_PHILOSOPHY.md) - Our public benefit mission

---

## Feedback & Support

**Have Questions?**
- Email: clinical-support@florence-ai.org
- Internal Help Desk: Contact your organization's Florence administrator
- Training Resources: Access video tutorials in the Learning Center

**Report an Issue:**
- Technical problems: IT Help Desk
- Clinical content errors: clinical-safety@florence-ai.org
- Feature requests: feedback@florence-ai.org

---

Thank you for using AI Nurse Florence to support your evidence-based practice!

*Florence is a clinical decision support tool designed to assist healthcare professionals. All content must be reviewed and validated by licensed clinicians before use in patient care.*
