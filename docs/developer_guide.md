# AI Nurse Florence: Developer Guide

This guide provides technical documentation for developers working with the AI Nurse Florence API and codebase.

## Architecture Overview

AI Nurse Florence is a FastAPI-based application that provides healthcare information through various live medical data services:

```
┌───────────────┐     ┌─────────────┐     ┌─────────────────┐
│  API Gateway  │────▶│  FastAPI    │────▶│  Core Services  │
└───────────────┘     └─────────────┘     └─────────────────┘
				    │                      │
				    ▼                      ▼
			    ┌─────────────┐     ┌─────────────────┐
			    │  Middleware │     │ Live Medical    │
			    └─────────────┘     │ APIs Integration│
				    │             └─────────────────┘
				    ▼                      │
			    ┌─────────────┐              ▼
			    │   Caching   │     ┌─────────────────┐
			    └─────────────┘     │ LLM Integration │
							└─────────────────┘
```

### Key Components

- **API Routers**: Endpoint definitions in the `/routers` directory
- **Services**: Core business logic in the `/services` directory with live API integration
- **Live Medical APIs**: Real-time data from `live_mydisease.py`, `live_pubmed.py`, `live_clinicaltrials.py`
- **Middleware**: Request processing, rate limiting, and logging in `/utils/middleware.py`
- **Exception Handling**: Custom exceptions with external service handling in `/utils/exceptions.py`
- **Caching**: Redis-based caching with in-memory fallback in `/utils/cache.py`
- **Monitoring**: Prometheus metrics and health checks in `/utils/metrics.py`

## Live Medical Data Integration

### External APIs

#### MyDisease.info
- **Purpose**: Comprehensive disease information and cross-references
- **File**: `live_mydisease.py`
- **Function**: `lookup(term: str)`
- **Rate Limits**: No authentication required, reasonable use expected
- **Data Fields**: Disease names, definitions, MONDO ontology, HPO phenotypes, SNOMED CT codes

#### MedlinePlus Connect (NIH) ⭐ NEW
- **Purpose**: Consumer-friendly symptom information from NIH MedlinePlus
- **Service**: `src/services/disease_service.py` (lines 393-462)
- **Function**: `_fetch_medlineplus_symptoms(disease_name, snomed_code)`
- **Rate Limits**: No published limit, conservative use recommended
- **Query Methods**:
  - SNOMED CT codes (primary): `mainSearchCriteria.v.c=<code>&mainSearchCriteria.v.cs=2.16.840.1.113883.6.96`
  - Disease name (fallback): `mainSearchCriteria.v.c=<name>`
- **Response Format**: JSON with HTML summary field
- **Data Extraction**: HTML parsing with regex for symptom lists

**Example Usage**:
```python
# Query with SNOMED code
symptoms = await _fetch_medlineplus_symptoms("diabetes", snomed_code="44054006")
# Returns: ["Increased thirst and urination", "Increased hunger", ...]

# Query with disease name (automatic fallback)
symptoms = await _fetch_medlineplus_symptoms("heart failure")
# Returns: ["Feeling short of breath...", "Fatigue or weakness...", ...]
```

**Multi-Tier Symptom Fetching Strategy**:
1. **MedlinePlus** (primary): Consumer-friendly symptoms from NIH
2. **HPO** (secondary): Clinical phenotype data from Human Phenotype Ontology
3. **Professional fallback** (tertiary): Clinical guidance when data unavailable

#### PubMed/NCBI eUtils
- **Purpose**: Medical literature search from 35+ million citations
- **File**: `live_pubmed.py`
- **Functions**: `search(query, max_results)`, `get_total_count(query)`
- **Rate Limits**: 3/sec (10/sec with API key)
- **API Key**: Set `NCBI_API_KEY` for enhanced rate limits

#### ClinicalTrials.gov
- **Purpose**: Current and completed clinical studies
- **File**: `live_clinicaltrials.py`
- **Function**: `search(condition, status, max_results)`
- **API Version**: v2 (current stable)
- **Rate Limits**: No authentication required

#### FDA API
- **Purpose**: Drug name lists for autocomplete and interaction checking
- **Service**: `src/services/drug_cache_updater.py`
- **Update Frequency**: Hourly background updates
- **Database Backup**: CachedDrugList table (~660 drugs)
- **Rate Limits**: No authentication required, reasonable use expected

## Getting Started

### Prerequisites

- Python 3.9+
- Redis (for production deployments - optional for development)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key (required for AI features)
- NCBI API key (optional but recommended for enhanced PubMed rate limits)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ai-nurse-florence.git
cd ai-nurse-florence

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -m src.models.database

# Run development server
uvicorn app:app --reload --port 8000
```

## Background Cache Update Services ⭐ NEW

AI Nurse Florence includes automatic background services that keep drug and disease caches fresh without manual intervention.

### Drug Cache Updater

**File**: `src/services/drug_cache_updater.py`

**Features**:
- Automatic hourly updates from FDA API
- Fetches ~1000 drugs and saves to SQL database
- Three-tier fallback: FDA API → Database → Hardcoded list (150 drugs)
- Preserves last known good data during API failures

**Configuration**:
```python
# In app.py - starts automatically on application startup
@app.on_event("startup")
async def startup_event():
    drug_cache_updater = get_drug_cache_updater()
    await drug_cache_updater.start()  # Runs in background
```

**Database Table**:
```sql
CREATE TABLE cached_drug_list (
    id VARCHAR PRIMARY KEY,
    drug_names JSON NOT NULL,           -- Array of ~660 drug names
    source VARCHAR NOT NULL,             -- 'fda_api', 'database', 'hardcoded'
    count INTEGER NOT NULL,              -- Number of drugs
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**Usage in Code**:
```python
from src.services.drug_cache_updater import get_drug_cache_updater

# Get status
updater = get_drug_cache_updater()
status = updater.get_status()
# Returns: {'is_running': True, 'last_update': '2025-09-30T10:00:00', ...}
```

### Disease Cache Updater

**File**: `src/services/disease_cache_updater.py`

**Features**:
- Automatic hourly updates from MONDO API (EBI OLS)
- Fetches ~1000 diseases and saves to SQL database
- Three-tier fallback: MONDO API → Database → Hardcoded list (600+ diseases)
- Preserves last known good data during API failures

**Configuration**:
```python
# In app.py - starts automatically on application startup
@app.on_event("startup")
async def startup_event():
    disease_cache_updater = get_disease_cache_updater()
    await disease_cache_updater.start()  # Runs in background
```

**Database Table**:
```sql
CREATE TABLE cached_disease_list (
    id VARCHAR PRIMARY KEY,
    disease_names JSON NOT NULL,        -- Array of 600-1200 disease names
    source VARCHAR NOT NULL,             -- 'mondo_api', 'database', 'hardcoded'
    count INTEGER NOT NULL,              -- Number of diseases
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**Usage in Code**:
```python
from src.services.disease_cache_updater import get_disease_cache_updater

# Get status
updater = get_disease_cache_updater()
status = updater.get_status()
# Returns: {'is_running': True, 'last_update': '2025-09-30T10:00:00',
#           'last_fetch_source': 'api', 'network_warning': False}
```

**Key Design Principles**:
1. **No Manual Intervention**: Services start automatically with FastAPI app
2. **Database Preservation**: Only updates DB on successful API fetch
3. **Graceful Degradation**: Falls back to database during network issues
4. **Network Warnings**: Frontend components detect fallback mode and notify users

## SNOMED CT Code Integration ⭐ NEW

SNOMED CT codes enable precise lookups in MedlinePlus and other clinical systems.

### Extracting SNOMED Codes from MONDO

**File**: `src/services/disease_service.py` (lines 642-683)

```python
# Extract SNOMED CT Identifier (sctid) from MONDO xrefs
xrefs = mondo.get("xrefs", {})

if isinstance(xrefs, dict):
    # Try multiple SNOMED reference fields
    # sctid = SNOMED CT Identifier (the correct field!)
    snomed_code = (
        xrefs.get("sctid") or  # Primary: SNOMED CT ID
        xrefs.get("snomedct_us") or
        xrefs.get("snomedct") or
        xrefs.get("SNOMEDCT_US_2023_03_01") or
        xrefs.get("SNOMEDCT_US_2022_12_01") or
        []
    )

    if snomed_code:
        # sctid can be single value or list
        if isinstance(snomed_code, list):
            snomed_code = snomed_code[0]
        logger.info(f"✅ Found SNOMED code: {snomed_code}")
```

**Key Discovery**: MONDO uses `sctid` field, not `snomedct_us` or `snomedct`

### Disease Name Simplification

**Problem**: Specific disease variants (e.g., "type 2 diabetes", "resistant hypertension") may not match MedlinePlus entries

**Solution**: Strip qualifiers to create simplified variants

```python
# Build list of disease name variations to try
disease_name_variations = []

# Add official MONDO label first
if mondo.get("label"):
    disease_name_variations.append(mondo["label"])

    # Create simplified version by removing qualifiers
    qualifiers = [
        "resistant", "refractory", "monogenic", "thunderstorm triggered",
        "drug-induced", "drug induced", "acute", "chronic", "severe",
        "mild", "moderate", "familial", "hereditary", "congenital",
        "acquired", "primary", "secondary", "type 1", "type 2",
        "juvenile", "adult", "early onset", "late onset"
    ]

    label_lower = mondo["label"].lower()

    for qualifier in qualifiers:
        if qualifier in label_lower:
            # Remove qualifier and clean up spacing
            simplified = mondo["label"].lower().replace(qualifier, "").strip()
            simplified = " ".join(simplified.split())  # Remove extra spaces
            if simplified and simplified not in [v.lower() for v in disease_name_variations]:
                disease_name_variations.append(simplified)
                logger.info(f"📝 Created simplified disease name: '{simplified}'")
                break

# Try all variations with MedlinePlus
for name_variant in disease_name_variations:
    symptoms = await _fetch_medlineplus_symptoms(name_variant, snomed_code)
    if symptoms:
        break
```

**Examples**:
- "type 2 diabetes mellitus" → "diabetes mellitus"
- "resistant hypertension" → "hypertension"
- "thunderstorm triggered asthma" → "asthma"

## Symptom Fetching Flow

### Complete Data Flow

```
User Query: "type 2 diabetes"
        ↓
MyDisease.info API (disease ontology)
        ↓
Extract MONDO data + xrefs.sctid → "44054006"
        ↓
Create disease name variations:
  1. "type 2 diabetes mellitus" (official)
  2. "diabetes mellitus" (simplified)
        ↓
Try MedlinePlus API with SNOMED code 44054006
        ↓
Parse HTML → Extract symptom list
        ↓
SUCCESS: Return consumer-friendly symptoms ✅

If MedlinePlus fails for all variants ↓
Try HPO phenotypes (clinical terminology)
        ↓
Extract from disease_data.hpo.phenotype_related_to_disease
        ↓
Return clinical phenotypes ✅

If both MedlinePlus and HPO fail ↓
Professional fallback text:
  - "Detailed symptom information is not available..."
  - "Clinical manifestations may vary..."
  - "Consult medical literature..."
        ↓
Return professional guidance ✅
```

### Code Implementation

**File**: `src/services/disease_service.py` (lines 642-731)

```python
# 1. Try MedlinePlus FIRST (primary source)
logger.info(f"🔍 Attempting to fetch symptoms from MedlinePlus for: {disease_name}")

# Extract SNOMED code and create name variations
snomed_code = extract_snomed_code(mondo)
disease_name_variations = create_name_variations(mondo)

# Fetch from MedlinePlus
medlineplus_symptoms = []
for name_variant in disease_name_variations:
    medlineplus_symptoms = await _fetch_medlineplus_symptoms(name_variant, snomed_code)
    if medlineplus_symptoms:
        logger.info(f"✅ Using MedlinePlus symptoms for: '{name_variant}'")
        break

if medlineplus_symptoms:
    symptoms = ["The following are some of the symptoms that may vary between individuals:"] + medlineplus_symptoms

# 2. If MedlinePlus didn't provide symptoms, try HPO (fallback)
if not symptoms:
    logger.info(f"⚠️ MedlinePlus returned no symptoms, trying HPO fallback")
    if hpo and isinstance(hpo, dict):
        phenotypes = hpo.get("phenotype_related_to_disease", [])
        for phenotype in phenotypes[:10]:
            if isinstance(phenotype, dict):
                symptom_name = phenotype.get("hpo_name") or phenotype.get("phenotype_name")
                if symptom_name:
                    symptoms.append(symptom_name)

        if symptoms:
            logger.info(f"✅ Using HPO symptoms ({len(symptoms)} found)")

# 3. Final fallback: professional guidance
if not symptoms:
    logger.warning(f"⚠️ No symptoms found from any source, using fallback text")
    symptoms = [
        "Detailed symptom information is not available in the database",
        "Clinical manifestations may vary between individuals",
        "Consult medical literature and clinical practice guidelines"
    ]
```

## Troubleshooting

### MedlinePlus Integration

**Issue**: MedlinePlus returns 0 entries for all diseases

**Solution**: Check SNOMED code extraction
```python
# Add debug logging
xrefs = mondo.get("xrefs", {})
logger.info(f"Available xrefs: {list(xrefs.keys())}")
# Should see: ['sctid', 'icd10cm', 'mesh', ...]
```

**Issue**: Disease-specific variants not matching

**Solution**: Review disease name simplification
```python
# Check created variations
logger.info(f"Disease name variations: {disease_name_variations}")
# Should see: ["type 2 diabetes mellitus", "diabetes mellitus"]
```

**Issue**: HTML parsing fails for symptom extraction

**Solution**: Check MedlinePlus response format
```python
# Log raw response
logger.debug(f"MedlinePlus response: {response.text}")
# Verify <ul><li> structure exists in summary._value
```

### Background Cache Services

**Issue**: Background services not starting

**Check**:
```bash
# View application logs
grep "Starting background.*updates" logs/app.log
# Should see: "Starting background drug cache updates with 1.0h interval"
```

**Issue**: Database backups not being created

**Check**:
```bash
# Query database
sqlite3 florence.db "SELECT * FROM cached_drug_list ORDER BY updated_at DESC LIMIT 1;"
# Should return recent entry
```

**Issue**: Frontend showing network warnings constantly

**Solution**: Check cache updater status
```python
# In API endpoint
updater = get_drug_cache_updater()
status = updater.get_status()
print(status['last_fetch_source'])  # Should be 'api' if working
```

## API Development

### Creating New Endpoints

(Previous content continues...)
