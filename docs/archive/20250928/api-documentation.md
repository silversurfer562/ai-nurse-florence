# API Documentation
## Comprehensive endpoint documentation for AI Nurse Florence

## Base URL
```
Production: https://api.ainurseflorence.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

### API Key Authentication
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.ainurseflorence.com/api/v1/health
```

### OAuth2 JWT Authentication
```python
# Token request
response = requests.post(
    "https://api.ainurseflorence.com/api/v1/auth/token",
    data={
        "username": "your-username",
        "password": "your-password",
        "grant_type": "password"
    }
)
token = response.json()["access_token"]

# Authenticated request
headers = {"Authorization": f"Bearer {token}"}
```

## Core Endpoints

### Health Check

#### `GET /health`
Check system health and dependencies status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-28T10:00:00Z",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "external_apis": {
      "mydisease": "healthy",
      "pubmed": "healthy",
      "clinicaltrials": "healthy"
    }
  },
  "version": "1.0.0"
}
```

### Disease Information

#### `GET /disease`
Lookup comprehensive disease information from MyDisease.info.

**Parameters:**
- `q` (required): Disease name or condition to search
- `fields` (optional): Specific fields to return (default: all)

**Example:**
```bash
curl "https://api.ainurseflorence.com/api/v1/disease?q=diabetes"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "disease": {
      "name": "Diabetes Mellitus, Type 2",
      "mondo_id": "MONDO:0005148",
      "umls_id": "C0011860",
      "mesh_id": "D003924",
      "description": "A metabolic disorder characterized by hyperglycemia...",
      "synonyms": ["Type 2 diabetes", "T2DM", "Adult-onset diabetes"],
      "symptoms": ["Polyuria", "Polydipsia", "Polyphagia"],
      "xrefs": {
        "icd10": "E11",
        "omim": "125853",
        "orphanet": "ORPHA:769"
      }
    },
    "banner": "Educational use only — not medical advice. No PHI stored."
  }
}
```

### Medical Literature Search

#### `GET /pubmed`
Search PubMed/NCBI for medical literature.

**Parameters:**
- `q` (required): Search query
- `max_results` (optional): Maximum results to return (default: 10, max: 100)
- `sort` (optional): Sort order (relevance, date)
- `publication_types` (optional): Filter by publication type

**Example:**
```bash
curl "https://api.ainurseflorence.com/api/v1/pubmed?q=hypertension%20treatment&max_results=5"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "total_count": 158432,
    "articles": [
      {
        "pmid": "38234567",
        "title": "2025 Guidelines for Hypertension Management",
        "authors": ["Smith J", "Jones M"],
        "journal": "New England Journal of Medicine",
        "year": 2025,
        "abstract": "...",
        "doi": "10.1056/NEJMoa2025",
        "evidence_level": "Ia",
        "mesh_terms": ["Hypertension", "Antihypertensive Agents"]
      }
    ],
    "banner": "Educational use only — not medical advice."
  }
}
```

### Clinical Trials Search

#### `GET /trials`
Search ClinicalTrials.gov for active and completed studies.

**Parameters:**
- `condition` (required): Medical condition
- `status` (optional): Trial status (recruiting, active, completed)
- `phase` (optional): Trial phase (1, 2, 3, 4)
- `max_results` (optional): Maximum results (default: 10)

**Example:**
```bash
curl "https://api.ainurseflorence.com/api/v1/trials?condition=heart%20failure&status=recruiting"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "trials": [
      {
        "nct_id": "NCT05123456",
        "title": "SGLT2 Inhibitors in Heart Failure",
        "status": "Recruiting",
        "phase": "Phase 3",
        "enrollment": 500,
        "sponsor": "National Heart Institute",
        "locations": ["Boston, MA", "New York, NY"],
        "eligibility": {
          "min_age": "18 Years",
          "max_age": "85 Years",
          "gender": "All"
        }
      }
    ]
  }
}
```

## Clinical Wizard Endpoints

### Treatment Plan Wizard

#### `POST /wizards/treatment-plan/start`
Initialize a new treatment plan wizard session.

**Response:**
```json
{
  "status": "success",
  "data": {
    "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Treatment plan wizard started",
    "next_step": "assessment"
  }
}
```

#### `POST /wizards/treatment-plan/assessment`
Submit patient assessment information.

**Request Body:**
```json
{
  "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "65-year-old male with Type 2 diabetes, hypertension..."
}
```

#### `POST /wizards/treatment-plan/goals`
Define treatment goals.

**Request Body:**
```json
{
  "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Short-term: Achieve glucose control <180 mg/dL..."
}
```

#### `POST /wizards/treatment-plan/interventions`
Plan nursing and medical interventions.

**Request Body:**
```json
{
  "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
  "nursing_interventions": "Monitor blood glucose q6h...",
  "medications": "Metformin 1000mg PO BID...",
  "patient_education": "Diabetes self-management education..."
}
```

#### `POST /wizards/treatment-plan/monitoring`
Establish monitoring plan.

**Request Body:**
```json
{
  "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
  "text": "Vital signs q4h, glucose checks before meals..."
}
```

#### `POST /wizards/treatment-plan/generate`
Generate the complete treatment plan.

**Request Body:**
```json
{
  "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
  "evaluation_criteria": "Target HbA1c <7%, no hypoglycemic episodes..."
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
    "treatment_plan": "# COMPREHENSIVE TREATMENT PLAN\n\n## PATIENT ASSESSMENT...",
    "summary": {
      "primary_diagnosis": "Type 2 Diabetes Mellitus",
      "key_goals": "Glycemic control, prevent complications",
      "main_interventions": "Medication optimization, lifestyle modification"
    }
  }
}
```

### SBAR Report Wizard

#### `POST /wizards/sbar-report/start`
Start SBAR report generation.

#### `POST /wizards/sbar-report/generate`
Generate complete SBAR report.

**Request Body:**
```json
{
  "wizard_id": "wizard-id-here",
  "situation": "Mr. Jones, 72yo, post-op day 2...",
  "background": "CABG x3 on 9/26...",
  "assessment": "Decreasing urine output, elevated creatinine...",
  "recommendation": "Nephrology consult, fluid challenge..."
}
```

## Clinical Decision Support Endpoints

### Evidence-Based Interventions

#### `POST /clinical-decision-support/interventions`
Get evidence-based nursing interventions for a condition.

**Request Body:**
```json
{
  "patient_condition": "acute heart failure",
  "severity": "moderate",
  "comorbidities": ["diabetes", "hypertension"],
  "care_setting": "telemetry"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "nursing_interventions": [
      {
        "intervention": "Monitor daily weights",
        "rationale": "Detect fluid retention early",
        "frequency": "Daily at 0600",
        "evidence_level": "Ia"
      },
      {
        "intervention": "Assess lung sounds",
        "rationale": "Identify pulmonary congestion",
        "frequency": "Q4H",
        "evidence_level": "Ib"
      }
    ],
    "monitoring_parameters": [...],
    "patient_education": [...],
    "banner": "Educational use only — not medical advice."
  }
}
```

### Risk Assessment

#### `GET /clinical-decision-support/risk-assessment/{type}`
Calculate clinical risk scores.

**Supported Types:**
- `morse-falls`: Morse Falls Scale
- `braden`: Braden Scale for pressure injuries
- `mews`: Modified Early Warning Score

**Example:**
```bash
curl -X POST "https://api.ainurseflorence.com/api/v1/clinical-decision-support/risk-assessment/morse-falls" \
  -H "Content-Type: application/json" \
  -d '{
    "history_of_falling": true,
    "secondary_diagnosis": true,
    "ambulatory_aid": "walker",
    "iv_therapy": true,
    "gait": "weak",
    "mental_status": "oriented"
  }'
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "assessment_type": "Morse Falls Scale",
    "score": 65,
    "risk_level": "High",
    "interpretation": "High risk for falls",
    "recommendations": [
      "Implement fall prevention protocol",
      "Bed alarm activation",
      "Hourly rounding",
      "Non-slip footwear"
    ],
    "evidence_source": "Morse JM, et al. 1989"
  }
}
```

## Text Processing Endpoints

### Medical Text Summarization

#### `POST /summarize/chat`
Summarize medical text or clinical notes.

**Request Body:**
```json
{
  "prompt": "Summarize this discharge summary...",
  "max_length": 500,
  "focus": "medications"
}
```

### Readability Analysis

#### `POST /readability/check`
Analyze text readability for patient education.

**Request Body:**
```json
{
  "text": "Your medication helps control blood pressure..."
}
```

**Response:**
```json
{
  "flesch_reading_ease": 65.2,
  "grade_level": 8.3,
  "interpretation": "Fairly easy to read",
  "suggestions": [
    "Consider simplifying medical terms",
    "Break long sentences into shorter ones"
  ]
}
```

## Patient Education Endpoints

#### `POST /patient-education`
Generate patient education materials.

**Request Body:**
```json
{
  "condition": "diabetes",
  "topics": ["diet", "medication", "monitoring"],
  "reading_level": "8th grade",
  "language": "English"
}
```

## Rate Limiting

All endpoints are rate-limited to ensure fair usage:

- **Default**: 60 requests per minute per IP
- **Authenticated**: 100 requests per minute per API key
- **Bulk operations**: 10 requests per minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1632835200
```

## Error Responses

### Standard Error Format
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested disease information was not found",
    "details": {
      "query": "unknown_disease",
      "suggestion": "Try a different search term"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request or missing parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `EXTERNAL_SERVICE_ERROR` | 503 | External API unavailable |
| `INTERNAL_ERROR` | 500 | Server error |

## Webhook Support

### Webhook Registration

#### `POST /webhooks/register`
Register a webhook for async notifications.

**Request Body:**
```json
{
  "url": "https://your-server.com/webhook",
  "events": ["wizard.completed", "report.generated"],
  "secret": "your-webhook-secret"
}
```

### Webhook Payload Format
```json
{
  "event": "wizard.completed",
  "timestamp": "2025-09-28T10:00:00Z",
  "data": {
    "wizard_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "treatment_plan",
    "result_url": "https://api.ainurseflorence.com/api/v1/results/..."
  },
  "signature": "sha256=..."
}
```

## Pagination

Endpoints returning multiple results support pagination:

**Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 10, max: 100)

**Response Headers:**
```
X-Total-Count: 245
X-Page: 1
X-Per-Page: 10
Link: <.../api/v1/pubmed?page=2>; rel="next"
```

## API Versioning

The API uses URL versioning:
- Current version: `/api/v1/`
- Legacy support: `/api/v0/` (deprecated)

**Version Header:**
```
X-API-Version: 1.0.0
```

## SDK Examples

### Python SDK
```python
from ainurse import Client

client = Client(api_key="your-api-key")

# Disease lookup
disease = client.diseases.get("diabetes")

# Literature search
articles = client.pubmed.search("hypertension", max_results=5)

# Start treatment plan wizard
wizard = client.wizards.treatment_plan.start()
wizard.add_assessment("Patient assessment...")
wizard.add_goals("Treatment goals...")
plan = wizard.generate()
```

### JavaScript/TypeScript SDK
```typescript
import { AINurseClient } from '@ainurse/client';

const client = new AINurseClient({ apiKey: 'your-api-key' });

// Disease lookup
const disease = await client.diseases.get('diabetes');

// Start SBAR wizard
const wizard = await client.wizards.sbar.start();
await wizard.addSituation('Patient situation...');
const report = await wizard.generate();
```

### cURL Examples
```bash
# Disease lookup
curl -X GET "https://api.ainurseflorence.com/api/v1/disease?q=diabetes" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Start treatment plan wizard
curl -X POST "https://api.ainurseflorence.com/api/v1/wizards/treatment-plan/start" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Search clinical trials
curl -X GET "https://api.ainurseflorence.com/api/v1/trials?condition=cancer&status=recruiting" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## OpenAPI Specification

The complete OpenAPI 3.0 specification is available at:
- JSON: `https://api.ainurseflorence.com/openapi.json`
- YAML: `https://api.ainurseflorence.com/openapi.yaml`
- Interactive Docs: `https://api.ainurseflorence.com/docs`
- ReDoc: `https://api.ainurseflorence.com/redoc`

## Testing Endpoints

### Sandbox Environment
Test endpoints without affecting production:
```
https://sandbox.ainurseflorence.com/api/v1/
```

### Mock Data Endpoints
For development and testing:
```
GET /api/v1/mock/disease?q=diabetes
GET /api/v1/mock/pubmed?q=test
```

## Compliance and Security

- **HIPAA**: No PHI storage, audit logging enabled
- **TLS**: All connections require TLS 1.2+
- **Authentication**: OAuth2 or API key required
- **Rate Limiting**: Prevents abuse
- **Input Validation**: All inputs sanitized
- **CORS**: Configurable origin restrictions

## Support

- **Status Page**: https://status.ainurseflorence.com
- **API Support**: api-support@ainurseflorence.com
- **Documentation**: https://docs.ainurseflorence.com
- **GitHub**: https://github.com/silversurfer562/ai-nurse-florence

---

**API Version**: 1.0.0  
**Last Updated**: September 2025  
**Compliance**: HIPAA-aligned, no PHI storage
