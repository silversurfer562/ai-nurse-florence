# Treatment Plan Wizard Documentation

## Overview

The Treatment Plan Wizard is a multi-step guided workflow that helps healthcare professionals create comprehensive, structured treatment plans. It follows evidence-based nursing practices and ensures all critical components are included in the care plan.

## Workflow Steps

### 1. Start Wizard
**Endpoint:** `POST /api/v1/wizards/treatment-plan/start`

Initializes a new treatment plan session and returns a unique wizard ID.

**Response:**
```json
{
  "status": "success",
  "data": {
    "wizard_id": "uuid-string",
    "message": "Treatment Plan wizard started...",
    "next_step": "assessment"
  }
}
```

### 2. Patient Assessment
**Endpoint:** `POST /api/v1/wizards/treatment-plan/assessment`

Captures comprehensive patient assessment including:
- Primary diagnosis and secondary conditions
- Current symptoms and severity
- Relevant medical/surgical history
- Functional status and limitations
- Psychosocial factors

**Request:**
```json
{
  "wizard_id": "uuid-string",
  "text": "65-year-old male with Type 2 diabetes, hypertension, and chronic kidney disease. Admitted with diabetic ketoacidosis..."
}
```

### 3. Treatment Goals
**Endpoint:** `POST /api/v1/wizards/treatment-plan/goals`

Defines measurable treatment objectives:
- Short-term goals (24-72 hours)
- Long-term goals (weeks to months)
- Patient-centered outcomes
- Expected timeframes

**Request:**
```json
{
  "wizard_id": "uuid-string",
  "text": "Short-term: Stabilize blood glucose <200 mg/dL in 24 hours, correct dehydration..."
}
```

### 4. Interventions
**Endpoint:** `POST /api/v1/wizards/treatment-plan/interventions`

Comprehensive intervention planning across three domains:

**Request:**
```json
{
  "wizard_id": "uuid-string",
  "nursing_interventions": "Continuous glucose monitoring, strict I&O, neuro checks q2h...",
  "medications": "Insulin drip per protocol, IV fluids 0.9% NS, potassium replacement...",
  "patient_education": "Diabetes self-management, glucose monitoring, medication compliance..."
}
```

### 5. Monitoring Plan
**Endpoint:** `POST /api/v1/wizards/treatment-plan/monitoring`

Establishes systematic monitoring protocols:
- Vital signs monitoring frequency
- Laboratory values to track
- Symptom assessment schedules
- Response to interventions
- Safety parameters and alerts

**Request:**
```json
{
  "wizard_id": "uuid-string",
  "text": "Vitals q4h, glucose checks q1h during insulin drip then q6h, daily labs..."
}
```

### 6. Generate Treatment Plan
**Endpoint:** `POST /api/v1/wizards/treatment-plan/generate`

Adds evaluation criteria and generates the complete treatment plan using AI.

**Request:**
```json
{
  "wizard_id": "uuid-string",
  "evaluation_criteria": "Success indicators: glucose <200 mg/dL, pH normalized..."
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "wizard_id": "uuid-string",
    "treatment_plan": "# COMPREHENSIVE TREATMENT PLAN\n\n## PATIENT ASSESSMENT...",
    "summary": {
      "primary_diagnosis": "Type 2 diabetes with diabetic ketoacidosis...",
      "key_goals": "Stabilize blood glucose, correct dehydration...",
      "main_interventions": "Continuous glucose monitoring, insulin drip...",
      "monitoring_focus": "Vital signs q4h, glucose monitoring..."
    }
  }
}
```

## Session Management

### Get Session Status
**Endpoint:** `GET /api/v1/wizards/treatment-plan/session/{wizard_id}`

Returns current session progress and next required step.

**Response:**
```json
{
  "status": "success",
  "data": {
    "wizard_id": "uuid-string",
    "completed_steps": ["assessment", "goals"],
    "next_step": "interventions",
    "progress": "2/7 steps completed"
  }
}
```

### Cancel Session
**Endpoint:** `DELETE /api/v1/wizards/treatment-plan/session/{wizard_id}`

Cancels and removes a treatment plan wizard session.

## Generated Treatment Plan Structure

The AI-generated treatment plan follows a standardized clinical format:

```markdown
# COMPREHENSIVE TREATMENT PLAN

## PATIENT ASSESSMENT
- Primary Diagnosis: [Primary condition]
- Secondary Conditions: [Comorbidities]
- Current Status: [Symptoms and vital parameters]

## TREATMENT GOALS
### Short-term Goals (24-48 hours)
- [Immediate objectives with timeframes]

### Long-term Goals (weeks to months)
- [Extended care objectives]

## NURSING INTERVENTIONS
- [Evidence-based nursing care activities]
- [Monitoring and assessment protocols]
- [Safety measures and precautions]

## MEDICATION MANAGEMENT
- [Prescribed medications and dosages]
- [Administration protocols]
- [Monitoring for effectiveness and side effects]

## PATIENT EDUCATION
- [Self-care education topics]
- [Family involvement strategies]
- [Resource provision]

## MONITORING PLAN
- [Vital signs frequency]
- [Laboratory monitoring schedule]
- [Symptom tracking protocols]

## EVALUATION CRITERIA
### Success Indicators
- [Measurable outcomes]
- [Target values and timeframes]

### Reassessment Timeline
- [Follow-up schedule]
- [Plan modification triggers]

### Discharge Criteria
- [Requirements for safe discharge]
```

## Clinical Use Cases

### Acute Care Settings
- **Diabetic Ketoacidosis:** Comprehensive metabolic management
- **Heart Failure Exacerbation:** Fluid management and monitoring
- **Post-Surgical Care:** Pain management and mobility restoration
- **Infection Management:** Antibiotic therapy and symptom monitoring

### Chronic Disease Management
- **Diabetes Management:** Long-term glycemic control
- **Hypertension Care:** Lifestyle and medication optimization
- **COPD Management:** Respiratory status and medication adherence
- **Kidney Disease:** Progression monitoring and complication prevention

### Specialty Care
- **Oncology:** Treatment tolerance and symptom management
- **Cardiac Care:** Post-procedure monitoring and rehabilitation
- **Wound Care:** Healing progression and infection prevention
- **Mental Health:** Therapeutic interventions and safety planning

## Best Practices

### Assessment Phase
- Include all relevant medical history
- Document current symptoms objectively
- Assess psychosocial factors affecting care
- Consider cultural and linguistic needs

### Goal Setting
- Use SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- Include both physiological and functional outcomes
- Align with patient preferences and values
- Consider realistic timeframes

### Intervention Planning
- Base interventions on current evidence
- Include both independent and collaborative nursing actions
- Address safety priorities first
- Plan for patient and family education

### Monitoring Strategy
- Establish clear parameters for assessment
- Define frequency based on patient acuity
- Include both objective measurements and subjective assessments
- Plan for early detection of complications

### Evaluation Criteria
- Define specific success indicators
- Establish timeline for reassessment
- Include criteria for plan modification
- Plan for care transitions

## Error Handling

### Common Error Scenarios
- **Invalid Wizard ID:** Returns 404 with clear error message
- **Missing Components:** Returns 400 with list of missing elements
- **AI Service Unavailable:** Returns 503 with fallback options
- **Session Timeout:** Automatic cleanup after inactivity

### Error Response Format
```json
{
  "status": "error",
  "error": {
    "message": "Human-readable error description",
    "code": "machine_readable_error_code"
  }
}
```

## Security and Privacy

### Data Protection
- No PHI (Personal Health Information) is stored permanently
- Session data is cleaned up after completion or timeout
- All data transmissions use HTTPS encryption
- Audit logging for clinical documentation

### Access Control
- API key authentication required
- Role-based access control for clinical features
- Rate limiting to prevent abuse
- Request correlation IDs for traceability

## Integration Examples

### JavaScript/TypeScript
```javascript
// Start treatment plan wizard
const startResponse = await fetch('/api/v1/wizards/treatment-plan/start', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  }
});

const { data } = await startResponse.json();
const wizardId = data.wizard_id;

// Add patient assessment
const assessmentResponse = await fetch('/api/v1/wizards/treatment-plan/assessment', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    wizard_id: wizardId,
    text: "Patient assessment details..."
  })
});
```

### Python
```python
import requests

# Start wizard
response = requests.post(
    'https://api.florence-ai.org/api/v1/wizards/treatment-plan/start',
    headers={'Authorization': 'Bearer your-api-key'}
)
wizard_id = response.json()['data']['wizard_id']

# Add assessment
assessment_data = {
    'wizard_id': wizard_id,
    'text': 'Comprehensive patient assessment...'
}
requests.post(
    'https://api.florence-ai.org/api/v1/wizards/treatment-plan/assessment',
    headers={'Authorization': 'Bearer your-api-key'},
    json=assessment_data
)
```

### cURL
```bash
# Start wizard
curl -X POST https://api.florence-ai.org/api/v1/wizards/treatment-plan/start \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json"

# Add interventions
curl -X POST https://api.florence-ai.org/api/v1/wizards/treatment-plan/interventions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "wizard_id": "uuid-here",
    "nursing_interventions": "Continuous monitoring...",
    "medications": "Insulin therapy...",
    "patient_education": "Diabetes management..."
  }'
```

## Compliance and Quality

### Clinical Standards
- Follows evidence-based nursing practice guidelines
- Incorporates Joint Commission safety requirements
- Aligns with nursing documentation standards
- Supports quality improvement initiatives

### Educational Disclaimers
All generated treatment plans include appropriate medical disclaimers:
- "Educational use only — not medical advice"
- "No PHI stored"
- "Consult qualified healthcare providers for medical decisions"
- "Review and customize for individual patient needs"

### Quality Assurance
- AI-generated content reviewed for clinical accuracy
- Regular updates based on current evidence
- User feedback integration for continuous improvement
- Monitoring for potential bias or errors

## Support and Troubleshooting

### Common Issues
1. **Session Timeout:** Sessions expire after inactivity - restart wizard
2. **Missing Steps:** Use session status endpoint to identify missing components
3. **AI Generation Failure:** Check API key and retry generation
4. **Validation Errors:** Ensure all required fields are provided

### Contact Information
- Technical Support: Review API documentation and logs
- Clinical Questions: Consult with healthcare professionals
- Feature Requests: Submit through appropriate channels
- Bug Reports: Include request correlation IDs for investigation
