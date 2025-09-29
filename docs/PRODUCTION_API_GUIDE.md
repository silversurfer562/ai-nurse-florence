# 🏥 AI Nurse Florence - Production API Guide

**Live medical data API for healthcare professionals**

Base URL: `https://your-app.railway.app`

## 🚀 Quick Start

### 1. Test Health Status
```bash
curl https://your-app.railway.app/health
```

### 2. Get Disease Information
```bash
curl "https://your-app.railway.app/api/v1/disease/lookup?q=diabetes"
```

### 3. Search Medical Literature
```bash
curl "https://your-app.railway.app/api/v1/pubmed/search?q=hypertension&limit=5"
```

## 📚 Core API Endpoints

### Health & Status

#### `GET /health`
Application health check with service status
```json
{
  "status": "healthy",
  "service": "ai-nurse-florence",
  "timestamp": "2024-01-15T10:30:00Z",
  "configuration": {
    "live_services": true,
    "openai_available": true,
    "redis_available": true
  },
  "external_apis": {
    "mydisease": "https://mydisease.info/v1/",
    "pubmed": "https://pubmed.ncbi.nlm.nih.gov/",
    "clinicaltrials": "https://clinicaltrials.gov/api/v2/"
  }
}
```

### Disease Information

#### `GET /api/v1/disease/lookup`
Look up disease information from authoritative medical databases

**Parameters:**
- `q` (required): Disease or condition name
- `limit` (optional): Number of results (default: 10)

**Example:**
```bash
curl "https://your-app.railway.app/api/v1/disease/lookup?q=diabetes"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "diabetes",
    "summary": "Diabetes mellitus is a group of metabolic disorders...",
    "sources": [
      {
        "name": "MyDisease.info",
        "data": {
          "mondo": {
            "definition": "A metabolic disorder characterized by...",
            "synonyms": ["diabetes mellitus", "DM"]
          }
        }
      }
    ],
    "banner": "Draft for clinician review — not medical advice"
  }
}
```

### Medical Literature Search

#### `GET /api/v1/pubmed/search`
Search PubMed database for medical literature

**Parameters:**
- `q` (required): Search query
- `limit` (optional): Number of results (default: 10, max: 50)
- `sort` (optional): Sort order ('date', 'relevance')

**Example:**
```bash
curl "https://your-app.railway.app/api/v1/pubmed/search?q=heart+disease+treatment&limit=5"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "heart disease treatment",
    "total_results": 245678,
    "articles": [
      {
        "pmid": "12345678",
        "title": "Novel Approaches to Cardiovascular Disease Treatment",
        "authors": ["Smith J", "Johnson A"],
        "journal": "New England Journal of Medicine",
        "pub_date": "2024-01-10",
        "abstract": "Background: Cardiovascular disease remains...",
        "doi": "10.1056/NEJMoa1234567",
        "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
      }
    ]
  }
}
```

### Clinical Trials

#### `GET /api/v1/trials/search`
Search for active clinical trials

**Parameters:**
- `condition` (required): Medical condition
- `location` (optional): Geographic location
- `status` (optional): Trial status ('recruiting', 'active', 'completed')
- `limit` (optional): Number of results (default: 10)

**Example:**
```bash
curl "https://your-app.railway.app/api/v1/trials/search?condition=cancer&location=New+York&status=recruiting"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "query": "cancer",
    "location": "New York",
    "trials": [
      {
        "nct_id": "NCT12345678",
        "title": "Phase II Study of Novel Cancer Treatment",
        "status": "Recruiting",
        "conditions": ["Lung Cancer", "Non-Small Cell Lung Cancer"],
        "locations": [
          {
            "facility": "Memorial Sloan Kettering Cancer Center",
            "city": "New York",
            "state": "NY"
          }
        ],
        "sponsor": "National Cancer Institute",
        "phase": "Phase 2",
        "enrollment": 150,
        "start_date": "2024-02-01",
        "completion_date": "2025-12-31",
        "url": "https://clinicaltrials.gov/ct2/show/NCT12345678"
      }
    ]
  }
}
```

### Patient Education

#### `GET /api/v1/medlineplus/summary`
Get patient-friendly health information

**Parameters:**
- `topic` (required): Health topic
- `language` (optional): Language code (default: 'en')

**Example:**
```bash
curl "https://your-app.railway.app/api/v1/medlineplus/summary?topic=diabetes"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "topic": "diabetes",
    "title": "Diabetes",
    "summary": "Diabetes is a disease that occurs when your blood glucose...",
    "key_points": [
      "Type 1 diabetes is usually diagnosed in children and young adults",
      "Type 2 diabetes is the most common form of diabetes",
      "Gestational diabetes develops during pregnancy"
    ],
    "source": "MedlinePlus",
    "last_updated": "2024-01-10",
    "url": "https://medlineplus.gov/diabetes.html"
  }
}
```

## 🤖 AI-Powered Endpoints

*Note: Requires OpenAI API key configuration*

### Patient Education Generation

#### `POST /api/v1/education/generate`
Generate AI-powered patient education materials

**Request Body:**
```json
{
  "topic": "diabetes management",
  "reading_level": "elementary",
  "language": "en",
  "format": "text"
}
```

**Example:**
```bash
curl -X POST "https://your-app.railway.app/api/v1/education/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "diabetes management",
    "reading_level": "elementary"
  }'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "topic": "diabetes management",
    "content": "Understanding Diabetes Management\n\nDiabetes is when your body...",
    "reading_level": "elementary",
    "word_count": 245,
    "estimated_reading_time": "2 minutes",
    "generated_at": "2024-01-15T10:30:00Z",
    "banner": "Draft for clinician review — not medical advice"
  }
}
```

### Clinical Decision Support

#### `POST /api/v1/clinical/analyze`
AI analysis of clinical scenarios

**Request Body:**
```json
{
  "patient_data": {
    "age": 65,
    "gender": "male",
    "chief_complaint": "chest pain",
    "vital_signs": {
      "bp": "140/90",
      "hr": 88,
      "temp": 98.6
    },
    "symptoms": ["chest pain", "shortness of breath"]
  },
  "question": "What are the differential diagnoses?"
}
```

## 📊 Response Format

All API responses follow this standard format:

### Success Response
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "response_time_ms": 245,
    "version": "1.0.0"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "The 'q' parameter is required",
    "details": {
      "parameter": "q",
      "provided": null,
      "expected": "string"
    }
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

## 🔧 Testing Your Deployment

### Automated Testing
```bash
# Test all endpoints
python scripts/test_production_endpoints.py https://your-app.railway.app

# Continuous monitoring
python scripts/railway_monitor.py https://your-app.railway.app --continuous
```

### Manual Testing
```bash
# Health check
curl https://your-app.railway.app/health

# Disease lookup
curl "https://your-app.railway.app/api/v1/disease/lookup?q=hypertension"

# Literature search
curl "https://your-app.railway.app/api/v1/pubmed/search?q=covid-19&limit=3"

# Clinical trials
curl "https://your-app.railway.app/api/v1/trials/search?condition=diabetes&limit=2"
```

## 🚀 Performance & Reliability

### Caching
- **Redis caching** for all external API calls (30-minute TTL)
- **Response compression** for large datasets
- **Connection pooling** for database operations

### Rate Limiting
- **120 requests per minute** per IP address
- **Burst allowance** of 200 requests
- **Graceful degradation** during high load

### Error Handling
- **Automatic retries** for transient failures
- **Fallback responses** when external APIs are down
- **Comprehensive logging** for debugging

### Monitoring
- **Health checks** every 30 seconds
- **Response time monitoring** (target: <2 seconds)
- **External API status** tracking
- **Automated alerts** for issues

## 🔗 Data Sources

Your deployment connects to these live medical databases:

| Source | Purpose | Update Frequency |
|--------|---------|------------------|
| **PubMed/NCBI** | Medical literature & research | Daily |
| **MyDisease.info** | Disease information & genetics | Weekly |
| **MedlinePlus** | Patient education materials | Weekly |
| **ClinicalTrials.gov** | Active clinical trials | Daily |
| **OpenAI GPT-4** | AI analysis & generation | Real-time |

## 🛡️ Security & Compliance

### Data Protection
- **No PHI storage** - all requests are stateless
- **HTTPS encryption** for all communications
- **Input validation** and sanitization
- **Rate limiting** to prevent abuse

### Compliance Notes
- **Educational use only** - not for direct patient care
- **Clinician review required** for all generated content
- **Source attribution** for all medical information
- **Audit logging** for all API requests

## 🔧 Troubleshooting

### Common Issues

#### 503 Service Unavailable
```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Check Railway logs
railway logs
```

#### Slow Response Times
```bash
# Monitor performance
python scripts/railway_monitor.py https://your-app.railway.app
```

#### External API Errors
- **PubMed**: Check NCBI service status
- **MyDisease**: Check mydisease.info status
- **OpenAI**: Verify API key and quota

### Support Resources
- **Health Dashboard**: `/health`
- **API Documentation**: `/docs`
- **Monitoring Script**: `scripts/railway_monitor.py`
- **Test Suite**: `scripts/test_production_endpoints.py`

---

✅ **Your AI Nurse Florence deployment is ready for production use with live medical data!**

For the most up-to-date API documentation, visit: `https://your-app.railway.app/docs`