# AI Nurse Florence - Technical Specification
## Clinical Decision Support System & Document Authoring Platform

**Version**: 2.1.0
**Last Updated**: September 30, 2025
**Deployment Strategy**: Hybrid Progressive Enhancement with ChatGPT Store Integration

> **🏥 Educational Use Only**: Clinical decision support for nursing professionals. Not diagnostic. No PHI stored.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Services](#core-services)
4. [Disease Information Service](#disease-information-service)
5. [Drug Interaction Service](#drug-interaction-service)
6. [Literature Search Service](#literature-search-service)
7. [Data Management](#data-management)
8. [Caching Strategy](#caching-strategy)
9. [API Endpoints](#api-endpoints)
10. [Security & Compliance](#security--compliance)

---

## System Overview

AI Nurse Florence is a comprehensive clinical decision support system providing real-time access to medical information through integration with authoritative medical databases and APIs.

### Key Capabilities

- **Disease Information**: Comprehensive disease data from MONDO, MyDisease.info, and MedlinePlus
- **Symptom Data**: Consumer-friendly symptom information from NIH MedlinePlus (primary) with HPO fallback
- **Drug Interactions**: Multi-drug interaction checking with severity assessment and clinical recommendations
- **Literature Search**: Evidence-based medical literature from PubMed with intelligent ranking
- **Clinical Trials**: Active trial information from ClinicalTrials.gov
- **Smart Caching**: Intelligent caching with hourly background updates to SQL database

### Technology Stack

- **Backend**: FastAPI 0.115.14 (Python 3.10+)
- **Frontend**: React 18+ with TypeScript
- **Database**: SQLAlchemy with PostgreSQL/SQLite support
- **Caching**: Redis (production) / In-memory (development)
- **APIs**: MyDisease.info, MedlinePlus, PubMed, ClinicalTrials.gov, FDA

---

## Architecture

### Service Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│  API Routers Layer                                           │
│  ├── disease.py          (Disease information endpoints)     │
│  ├── drug_interactions.py (Drug interaction checking)        │
│  ├── enhanced_literature.py (Literature search)             │
│  ├── clinical_trials.py  (Clinical trial search)            │
│  └── cache_monitoring.py (Cache management)                 │
├─────────────────────────────────────────────────────────────┤
│  Service Layer                                               │
│  ├── disease_service.py         (Disease data integration)  │
│  ├── drug_interaction_service.py (Drug safety analysis)     │
│  ├── enhanced_literature_service.py (Evidence search)       │
│  ├── clinical_trials_service.py (Trial data)                │
│  ├── drug_cache_updater.py     (Background drug updates)    │
│  └── disease_cache_updater.py  (Background disease updates) │
├─────────────────────────────────────────────────────────────┤
│  Data Integration Layer                                      │
│  ├── MyDisease.info API    (Disease ontology, MONDO, HPO)   │
│  ├── MedlinePlus API       (Consumer health information)     │
│  ├── PubMed E-utilities    (Medical literature)             │
│  ├── ClinicalTrials.gov    (Clinical studies)               │
│  └── FDA API               (Drug information)                │
├─────────────────────────────────────────────────────────────┤
│  Caching & Persistence Layer                                 │
│  ├── SmartCacheManager     (Intelligent caching strategies)  │
│  ├── Redis Cache           (Production caching)              │
│  ├── Database (PostgreSQL) (Backup and persistence)          │
│  └── Background Updaters   (Hourly data refresh)             │
└─────────────────────────────────────────────────────────────┘
```

### Conditional Imports Pattern

Services use graceful degradation with conditional imports:

```python
try:
    import httpx
    _has_httpx = True
except ImportError:
    _has_httpx = False
    # Fallback to requests or stub responses
```

---

## Core Services

### Disease Information Service

**File**: `src/services/disease_service.py`
**Primary APIs**: MyDisease.info, MedlinePlus, PubMed

#### Features

1. **Comprehensive Disease Lookup**
   - Queries MyDisease.info for disease ontology data
   - Extracts MONDO classifications, synonyms, and cross-references
   - Fetches related PubMed articles with abstracts

2. **MedlinePlus Symptom Integration** ⭐ NEW
   - **Primary Source**: NIH MedlinePlus (consumer-friendly symptoms)
   - **SNOMED CT Integration**: Uses `sctid` codes from MONDO for precise lookups
   - **Disease Name Simplification**: Strips qualifiers ("type 2", "resistant", etc.)
   - **Multi-Tier Fallback**: MedlinePlus → HPO → Professional fallback text
   - **Consumer Language**: Clear, accessible symptom descriptions

3. **Autocomplete & Search**
   - 600+ disease database with smart grouping
   - Keyword-based disease suggestions
   - Medical specialty organization

#### Technical Implementation

**Symptom Fetching Flow:**
```python
# 1. Extract SNOMED code from MONDO xrefs
sctid = mondo.get("xrefs", {}).get("sctid")

# 2. Query MedlinePlus with SNOMED code
url = f"https://connect.medlineplus.gov/service?mainSearchCriteria.v.c={sctid}&mainSearchCriteria.v.cs=2.16.840.1.113883.6.96"

# 3. Parse symptom list from HTML response
symptoms = parse_medlineplus_html(response)

# 4. Fallback to HPO if MedlinePlus returns no data
if not symptoms:
    symptoms = extract_hpo_phenotypes(disease_data)

# 5. Professional fallback if all sources fail
if not symptoms:
    symptoms = ["Detailed symptom information is not available...",
                "Clinical manifestations may vary...",
                "Consult medical literature..."]
```

**SNOMED Code Extraction:**
```python
# MONDO uses 'sctid' (SNOMED CT Identifier) not 'snomedct_us'
xrefs = mondo.get("xrefs", {})
snomed_code = (
    xrefs.get("sctid") or           # Primary field
    xrefs.get("snomedct_us") or
    xrefs.get("snomedct") or
    []
)
```

**Disease Name Simplification:**
```python
# Remove qualifiers for better MedlinePlus matching
qualifiers = ["resistant", "refractory", "monogenic", "thunderstorm triggered",
              "type 1", "type 2", "acute", "chronic", "familial", ...]

# "resistant hypertension" → "hypertension"
# "type 2 diabetes mellitus" → "diabetes mellitus"
```

#### Data Models

```python
class DiseaseResponse(BaseModel):
    summary: str
    description: str
    symptoms: List[str]
    disease_name: str
    synonyms: List[str]
    mondo_id: str
    sources: List[str]
    related_articles: List[RelatedArticle]
    needs_clarification: bool

class RelatedArticle(BaseModel):
    pmid: str
    title: str
    authors: str
    journal: str
    pub_date: str
    summary: str  # Max 125 words
    url: str
```

#### Example Response

```json
{
  "disease_name": "type 2 diabetes mellitus",
  "symptoms": [
    "The following are some of the symptoms that may vary between individuals:",
    "Increased thirst and urination",
    "Increased hunger",
    "Feeling tired",
    "Blurred vision",
    "Numbness or tingling in the feet or hands",
    "Sores that do not heal",
    "Unexplained weight loss"
  ],
  "sources": ["MyDisease.info", "MONDO", "MedlinePlus", "HPO"],
  "mondo_id": "MONDO:0005148",
  "related_articles": [...]
}
```

---

### Drug Interaction Service

**File**: `src/services/drug_interaction_service.py`
**Primary APIs**: FDA, OpenAI (clinical analysis)

#### Features

1. **Multi-Drug Interaction Analysis**
   - Checks 2-20 medications simultaneously
   - 4-level severity classification
   - Clinical recommendations and monitoring requirements

2. **Drug Autocomplete**
   - FDA drug database integration
   - Real-time drug name suggestions
   - Database backup with hourly updates

3. **Smart Caching**
   - Drug combinations cached for instant responses
   - Background cache updates every hour
   - SQL database backup for offline operation

#### Severity Levels

```python
class InteractionSeverity(Enum):
    CONTRAINDICATED = "contraindicated"  # Do not use together
    MAJOR = "major"                      # Serious interaction, requires monitoring
    MODERATE = "moderate"                # May require dose adjustment
    MINOR = "minor"                      # Minimal clinical significance
    UNKNOWN = "unknown"                  # Insufficient data
```

#### Background Cache Updates

**File**: `src/services/drug_cache_updater.py`

- **Update Interval**: Every 1 hour
- **Source**: FDA API (1000 drugs)
- **Backup**: SQL database (`CachedDrugList` table)
- **Fallback Strategy**:
  1. Try FDA API
  2. Use database backup (last successful fetch)
  3. Use hardcoded fallback list (150 common drugs)

```python
# Automatic startup in app.py
@app.on_event("startup")
async def startup_event():
    drug_cache_updater = get_drug_cache_updater()
    await drug_cache_updater.start()  # Runs in background
```

---

### Literature Search Service

**File**: `src/services/enhanced_literature_service.py`
**Primary API**: PubMed E-utilities

#### Features

1. **Evidence-Based Search**
   - PubMed integration with 35M+ citations
   - Intelligent query enhancement
   - Quality-based ranking

2. **Medical Specialty Filtering**
   - Context-aware search optimization
   - Specialty-specific result prioritization

3. **Smart Caching**
   - Literature queries cached with TTL
   - Medical term normalization for cache keys

---

## Data Management

### Database Schema

#### CachedDrugList Table
```sql
CREATE TABLE cached_drug_list (
    id VARCHAR PRIMARY KEY,
    drug_names JSON NOT NULL,           -- Array of drug names
    source VARCHAR NOT NULL,             -- 'fda_api', 'database', 'hardcoded'
    count INTEGER NOT NULL,              -- Number of drugs
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

#### CachedDiseaseList Table
```sql
CREATE TABLE cached_disease_list (
    id VARCHAR PRIMARY KEY,
    disease_names JSON NOT NULL,        -- Array of disease names
    source VARCHAR NOT NULL,             -- 'mondo_api', 'database', 'hardcoded'
    count INTEGER NOT NULL,              -- Number of diseases
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

### Background Update Services

Both drug and disease cache updaters run as background async tasks:

**Characteristics:**
- **Startup**: Immediate initial fetch on app startup
- **Schedule**: Hourly updates (3600 seconds)
- **Strategy**: Only replace database on successful API fetch
- **Fallback**: Preserves last known good data during API failures
- **Logging**: Comprehensive logging for monitoring and debugging

**Example Log Output:**
```
✅ Saved 659 drugs to database (source: fda_api)
✅ Saved 1247 diseases to database (source: mondo_api)
```

---

## Caching Strategy

### Smart Cache Manager

**File**: `src/utils/smart_cache.py`

#### Cache Strategies

```python
class CacheStrategy(Enum):
    MEDICAL_REFERENCE = "medical_reference"    # Long TTL (24h)
    LITERATURE_SEARCH = "literature_search"    # Medium TTL (6h)
    CLINICAL_TRIALS = "clinical_trials"        # Short TTL (1h)
    DRUG_INTERACTIONS = "drug_interactions"    # Long TTL (24h)
    DISEASE_INFO = "disease_info"              # Long TTL (24h)
```

#### Implementation

- **Production**: Redis with automatic connection management
- **Development**: In-memory dictionary fallback
- **Automatic Fallback**: Gracefully degrades when Redis unavailable

---

## API Endpoints

### Disease Information

```
GET    /api/v1/disease/lookup?q={disease_name}
GET    /api/v1/disease/disease-names?query={term}&limit={n}
```

### Drug Interactions

```
POST   /api/v1/drug-interactions/check
GET    /api/v1/drug-interactions/drug-names?query={term}&limit={n}
GET    /api/v1/drug-interactions/statistics
```

### Literature Search

```
POST   /api/v1/enhanced-literature/search
GET    /api/v1/enhanced-literature/recent
GET    /api/v1/enhanced-literature/cache-stats
```

### Cache Monitoring

```
GET    /api/v1/cache/stats
GET    /api/v1/cache/health
POST   /api/v1/cache/clear
```

---

## Security & Compliance

### Educational Use Disclaimer

All API responses include:
```json
{
  "banner": "Draft for clinician review — not medical advice. No PHI stored."
}
```

### Data Privacy

- **No PHI Storage**: No patient health information stored
- **No Authentication Required**: Public educational resource
- **Rate Limiting**: SlowAPI integration for abuse prevention
- **CORS**: Configured for frontend access

### API Rate Limits

- **MyDisease.info**: Reasonable use (no hard limit)
- **PubMed**: 3 req/sec (10 req/sec with API key)
- **MedlinePlus**: No published limit (conservative use)
- **FDA**: Reasonable use (no hard limit)
- **ClinicalTrials.gov**: No published limit

---

## Configuration

### Environment Variables

```bash
# OpenAI API (required for AI features)
OPENAI_API_KEY=sk-...

# NCBI/PubMed (optional, enhances rate limits)
NCBI_API_KEY=...

# Redis (optional for production)
REDIS_URL=redis://localhost:6379

# Database
DATABASE_URL=postgresql://user:pass@localhost/florence
# or sqlite:///./florence.db for development
```

### Feature Flags

```python
# In src/config.py
USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "false").lower() == "true"
ENABLE_OPENAI = os.getenv("OPENAI_API_KEY") is not None
ENABLE_DRUG_INTERACTIONS = True  # Always enabled with fallback
```

---

## Performance Characteristics

### Response Times

- **Disease Lookup**: 150-300ms (with cache hits)
- **Drug Interactions**: 100-200ms (cached) / 500-1000ms (OpenAI analysis)
- **Literature Search**: 200-400ms (PubMed API)
- **Autocomplete**: <50ms (from cache/database)

### Cache Hit Rates

- **Disease Information**: ~80% hit rate
- **Drug Interactions**: ~73% hit rate
- **Literature Searches**: ~65% hit rate

### Database Sizes

- **Drug Cache**: ~660 drugs, updated hourly
- **Disease Cache**: ~600-1200 diseases, updated hourly
- **Total Storage**: <10MB for all caches

---

## Deployment Architecture

### Development Mode

```bash
# Backend
python -m uvicorn app:app --reload --port 8000

# Frontend
cd frontend && npm run dev
```

### Production Mode

```bash
# Docker Compose (recommended)
docker-compose up -d

# Manual (with Redis and PostgreSQL)
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Monitoring & Observability

### Health Checks

```
GET /api/v1/health         # Application health
GET /api/v1/cache/health   # Cache system health
```

### Metrics

- Request counts per endpoint
- Cache hit/miss ratios
- Background updater status
- API response times
- External API failure rates

### Logging

- Structured JSON logging
- Service-level logging for each component
- Debug logging for SNOMED/MedlinePlus integration
- Error tracking with stack traces

---

## Future Enhancements

### Phase 4.3 (Planned)
- Medical image processing (DICOM)
- Radiology report generation
- Image-based clinical decision support

### Phase 5 (Roadmap)
- Real-time clinical alerts
- Care plan generation
- Multi-language support
- Mobile application

---

**Last Updated**: September 30, 2025
**Version**: 2.1.0
**Status**: Production Ready