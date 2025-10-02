# Two-Tier Diagnosis System Architecture

> **Document Type:** Technical Guide - Chapter 3
> **Audience:** Users, Programmers, System Administrators
> **Last Updated:** 2025-10-01

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Tier 1: Full Clinical Library](#tier-1-full-clinical-library)
4. [Tier 2: Reference Database](#tier-2-reference-database)
5. [User Experience Workflows](#user-experience-workflows)
6. [API Reference](#api-reference)
7. [Database Schema](#database-schema)
8. [Promotion Workflow](#promotion-workflow)
9. [Maintenance & Updates](#maintenance--updates)
10. [For Programmers: Implementation Guide](#for-programmers-implementation-guide)
11. [For System Administrators: Deployment](#for-system-administrators-deployment)

---

## Overview

AI Nurse Florence uses a **two-tier diagnosis system** to balance comprehensive coverage with clinical quality:

- **Tier 1:** Curated library of 500-1,000 common diagnoses with full clinical content
- **Tier 2:** Lightweight reference database of 1,000-5,000+ diseases with external links

This architecture ensures:
- ✅ Fast, high-quality documentation for 90% of clinical encounters (Tier 1)
- ✅ Comprehensive lookup capability for rare/uncommon conditions (Tier 2)
- ✅ Manageable maintenance burden (curate quality where it matters)
- ✅ Scalability (reference database can grow without quality concerns)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER SEARCH QUERY                        │
│                    "patient diagnosis"                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │   Search Tier 1: Full Library       │
         │   (DiagnosisContentMap table)       │
         └──────────┬────────────────┬──────────┘
                    │                │
              FOUND │                │ NOT FOUND
                    │                │
                    ▼                ▼
         ┌──────────────────┐  ┌────────────────────────┐
         │  SHOW FULL INFO  │  │ Search Tier 2:         │
         │                  │  │ Reference Database     │
         │ • Medications    │  │ (DiseaseReference)     │
         │ • Warnings       │  └────────┬───────────────┘
         │ • Instructions   │           │
         │ • Generate Docs  │     FOUND │  NOT FOUND
         └──────────────────┘           │        │
                                        ▼        ▼
                             ┌─────────────────────────┐
                             │ SHOW REFERENCE INFO     │
                             │                         │
                             │ • Disease name + ICD-10│
                             │ • Short description    │
                             │ • External links:      │
                             │   - MedlinePlus        │
                             │   - PubMed research    │
                             │   - ICD-10 database    │
                             │ • "Promote to Library" │
                             └─────────────────────────┘
```

---

## Tier 1: Full Clinical Library

### Purpose
Provide **complete clinical content** for common diagnoses to enable automatic document generation.

### Coverage
**500-1,000 curated diagnoses** including:
- Top 100 ED diagnoses
- Top 100 primary care diagnoses
- Top 100 hospital medicine diagnoses
- Common specialty conditions (50-100 per specialty)

### Data Included

For each diagnosis in Tier 1:

| Field | Description | Example |
|-------|-------------|---------|
| **ICD-10 Code** | Primary diagnostic code | E11.9 |
| **SNOMED Code** | Epic/EHR standard code | 44054006 |
| **Diagnosis Display** | Clinical name | Type 2 diabetes mellitus without complications |
| **Warning Signs** | 5-7 red flags | Blood sugar >400 mg/dL, Confusion, Vomiting |
| **Medications** | 1-5 standard meds with RxNorm | Metformin (RxCUI: 860975), Insulin (RxCUI: 253182) |
| **Instructions** | Activity, diet, follow-up | Low carb diet, Daily glucose monitoring, Follow up in 1-2 weeks |
| **Clinical Flags** | Chronic condition, specialist referral | is_chronic: true, requires_specialist: true |

### Use Cases

✅ **Automated Document Generation**
- Discharge instructions
- Medication guides
- Patient education materials
- After-visit summaries

✅ **Smart Defaults**
- Pre-populate warning signs
- Suggest medications
- Auto-fill follow-up recommendations

✅ **Quality Assurance**
- All content clinically reviewed
- FHIR-compliant coding
- Epic integration ready

---

## Tier 2: Reference Database

### Purpose
Provide **lightweight lookup** for rare/uncommon diseases with links to external authoritative resources.

### Coverage
**1,000-5,000+ diseases** including:
- All ICD-10 codes for common categories
- Rare genetic disorders
- Specialized oncological conditions
- Uncommon infectious diseases

### Data Included

For each disease in Tier 2:

| Field | Description | Example |
|-------|-------------|---------|
| **MONDO ID** | Reference ID | ICD10:E75.21 |
| **Disease Name** | Official name | Fabry disease |
| **ICD-10 Codes** | Diagnostic codes | E75.21 |
| **SNOMED Code** | (if available) | 16652001 |
| **Short Description** | 1-2 sentences | A rare X-linked lysosomal storage disorder caused by alpha-galactosidase deficiency. |
| **Category** | Disease type | Rare Metabolic Diseases |
| **External Links** | Authoritative resources | MedlinePlus, PubMed, ICD-10 database |

### What's NOT Included

❌ **No clinical content:**
- No medication recommendations
- No warning signs
- No treatment protocols
- No discharge instructions

**Why?** Rare diseases require specialist knowledge. Instead of attempting to provide potentially outdated or incorrect guidance, we direct users to authoritative external resources.

### Use Cases

✅ **Quick ICD-10 Lookup**
```
User searches: "E75.21"
Result: Fabry disease + external links
```

✅ **Rare Disease Information**
```
User searches: "Fabry disease"
Result: Short description + MedlinePlus article + PubMed research
```

✅ **Discovery & Research**
```
User: "What's the ICD-10 for lysosomal storage disorder?"
System: Shows all matching diseases in Tier 2
User clicks: Gets external resources for specialist consultation
```

---

## User Experience Workflows

### Workflow 1: Common Diagnosis (Tier 1 Hit)

```
1. User searches: "diabetes type 2"
2. System finds in Tier 1 library
3. Display full diagnosis card:
   ┌─────────────────────────────────────────┐
   │ Type 2 Diabetes Mellitus                │
   │ ICD-10: E11.9 | SNOMED: 44054006       │
   ├─────────────────────────────────────────┤
   │ WARNING SIGNS (5):                      │
   │ • Blood sugar >400 mg/dL                │
   │ • Confusion or altered mental status    │
   │ • ...                                   │
   ├─────────────────────────────────────────┤
   │ MEDICATIONS (3):                        │
   │ • Metformin 500mg twice daily           │
   │ • ...                                   │
   ├─────────────────────────────────────────┤
   │ [Generate Discharge Instructions]       │
   │ [Generate Medication Guide]             │
   │ [Add to Patient Education]              │
   └─────────────────────────────────────────┘
4. User clicks "Generate Discharge Instructions"
5. Document auto-generated with all content
```

### Workflow 2: Rare Diagnosis (Tier 2 Hit)

```
1. User searches: "Fabry disease"
2. NOT found in Tier 1
3. Found in Tier 2 reference database
4. Display reference card:
   ┌─────────────────────────────────────────┐
   │ 📚 REFERENCE DATABASE MATCH             │
   ├─────────────────────────────────────────┤
   │ Fabry Disease                           │
   │ ICD-10: E75.21                          │
   │                                          │
   │ A rare X-linked lysosomal storage       │
   │ disorder caused by alpha-galactosidase  │
   │ deficiency.                             │
   ├─────────────────────────────────────────┤
   │ EXTERNAL RESOURCES:                     │
   │ 📄 [MedlinePlus Article]                │
   │ 🔬 [PubMed Research]                    │
   │ 🌐 [ICD-10 Database]                    │
   ├─────────────────────────────────────────┤
   │ ℹ️  This disease is not in our full     │
   │    clinical library. Please consult     │
   │    specialist resources.                │
   │                                          │
   │ 👤 [Request Add to Library] (admin)     │
   └─────────────────────────────────────────┘
5. User clicks MedlinePlus link
6. Opens authoritative patient education resource
```

### Workflow 3: Not Found (Neither Tier)

```
1. User searches: "extremely rare condition XYZ"
2. NOT found in Tier 1
3. NOT found in Tier 2
4. Display search help:
   ┌─────────────────────────────────────────┐
   │ ❌ NO MATCH FOUND                       │
   ├─────────────────────────────────────────┤
   │ We couldn't find a diagnosis matching:  │
   │ "extremely rare condition XYZ"          │
   │                                          │
   │ SUGGESTIONS:                            │
   │ • Try searching by ICD-10 code          │
   │ • Check spelling of disease name        │
   │ • Search external databases:            │
   │   - [MONDO Disease Ontology]            │
   │   - [WHO ICD-10 Browser]                │
   │   - [PubMed]                            │
   │                                          │
   │ 📧 [Report Missing Diagnosis]           │
   └─────────────────────────────────────────┘
```

---

## API Reference

### Tier 1 API (Full Library)

**Endpoint:** `/api/v1/content-settings/diagnoses/search`

```bash
GET /api/v1/content-settings/diagnoses/search?query=diabetes

Response:
{
  "results": [
    {
      "id": "dm_type2",
      "icd10_code": "E11.9",
      "snomed_code": "44054006",
      "diagnosis_display": "Type 2 diabetes mellitus without complications",
      "standard_warning_signs": [...],
      "standard_medications": [...],
      "is_chronic_condition": true
    }
  ]
}
```

### Tier 2 API (Reference Database)

**Endpoint:** `/api/v1/disease-reference/search`

```bash
GET /api/v1/disease-reference/search?q=fabry

Response:
{
  "query": "fabry",
  "total_results": 1,
  "results": [
    {
      "mondo_id": "ICD10:E75.21",
      "disease_name": "Fabry disease",
      "icd10_codes": ["E75.21"],
      "short_description": "A rare X-linked lysosomal storage disorder...",
      "external_resources": {
        "medlineplus": "https://medlineplus.gov/...",
        "pubmed": "https://pubmed.ncbi.nlm.nih.gov/...",
        "mondo": "https://www.icd10data.com/..."
      },
      "promoted_to_full_library": false
    }
  ],
  "search_time_ms": 45.2
}
```

**Additional Endpoints:**

- `GET /api/v1/disease-reference/by-icd10/{code}` - Lookup by exact ICD-10
- `GET /api/v1/disease-reference/categories` - List all categories
- `GET /api/v1/disease-reference/stats` - Database statistics
- `POST /api/v1/disease-reference/promote` - Request promotion to Tier 1

---

## Database Schema

### Tier 1: `diagnosis_content_map` Table

```sql
CREATE TABLE diagnosis_content_map (
    id VARCHAR(50) PRIMARY KEY,
    icd10_code VARCHAR(10) UNIQUE NOT NULL,
    snomed_code VARCHAR(20),
    diagnosis_display VARCHAR(200) NOT NULL,
    diagnosis_aliases JSON,
    standard_warning_signs JSON,
    standard_medications JSON,
    standard_activity_restrictions JSON,
    standard_diet_instructions JSON,
    standard_followup_instructions JSON,
    is_chronic_condition BOOLEAN DEFAULT FALSE,
    requires_specialist_followup BOOLEAN DEFAULT FALSE,
    typical_followup_days INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Tier 2: `disease_reference` Table

```sql
CREATE TABLE disease_reference (
    mondo_id VARCHAR(50) PRIMARY KEY,
    disease_name VARCHAR(300) NOT NULL,
    disease_synonyms JSON,
    icd10_codes JSON,
    snomed_code VARCHAR(20),
    umls_code VARCHAR(20),
    short_description TEXT,
    disease_category VARCHAR(100),
    is_rare_disease BOOLEAN DEFAULT FALSE,
    medlineplus_url VARCHAR(500),
    pubmed_search_url VARCHAR(500),
    mondo_url VARCHAR(500),
    search_count JSON,
    last_searched_at TIMESTAMP,
    promoted_to_full_library BOOLEAN DEFAULT FALSE,
    promotion_date TIMESTAMP,
    data_source VARCHAR(50),
    imported_at TIMESTAMP,
    last_updated_at TIMESTAMP
);
```

### Promotion Queue: `diagnosis_promotion_queue` Table

```sql
CREATE TABLE diagnosis_promotion_queue (
    id VARCHAR(50) PRIMARY KEY,
    mondo_id VARCHAR(50) NOT NULL,
    disease_name VARCHAR(300) NOT NULL,
    requested_by VARCHAR(100),
    request_reason TEXT,
    search_frequency JSON,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_to VARCHAR(100),
    review_notes TEXT,
    requested_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## Promotion Workflow

Frequently searched diseases in Tier 2 can be **promoted** to Tier 1 for full clinical content.

### Automatic Triggers

The system tracks search counts for each disease in Tier 2. Automatic promotion requests are created when:

- ✅ Disease searched 50+ times in last month
- ✅ Disease searched 100+ times total
- ✅ Multiple users request information about same disease

### Manual Promotion Request

Users/admins can manually request promotion:

```bash
POST /api/v1/disease-reference/promote
{
  "mondo_id": "ICD10:E75.21",
  "reason": "Multiple specialist referrals this quarter",
  "requested_by": "dr.smith@hospital.org"
}
```

### Promotion Process

```
1. Request Created
   ↓
2. Clinical Review
   • Verify clinical relevance
   • Research standard treatments
   • Gather medication recommendations
   ↓
3. Content Development
   • Add warning signs (5-7)
   • Add standard medications (1-5)
   • Add instructions (activity, diet, follow-up)
   • Medical review
   ↓
4. Promotion to Tier 1
   • Insert into diagnosis_content_map
   • Mark as promoted in disease_reference
   • Update promotion queue status
   ↓
5. Now Available for Document Generation!
```

---

## Maintenance & Updates

### Weekly Automated Updates (Tier 2)

```bash
# Run weekly (Sunday 2 AM)
python scripts/import_icd10_reference.py --update-mode
```

Updates:
- ✅ New ICD-10 codes from WHO
- ✅ Updated external links
- ✅ New disease descriptions from MedlinePlus

**Safety:** Updates go to staging table first, then manual review.

### Monthly Manual Review (Tier 1)

```
Review promotion queue:
- Approve/reject promotion requests
- Add full clinical content for approved diseases
- Update existing diagnoses based on new clinical guidelines
```

### Quarterly Audit

```
- FHIR compliance check
- Epic integration testing
- Usage analytics review
- Prune unused diagnoses from Tier 1
```

---

## For Programmers: Implementation Guide

### Adding a New Diagnosis to Tier 1

```python
from sqlalchemy.orm import Session
from src.models.content_settings import DiagnosisContentMap

def add_diagnosis_to_library(db: Session):
    diagnosis = DiagnosisContentMap(
        id="new_diagnosis_id",
        icd10_code="X00.0",
        snomed_code="12345678",
        diagnosis_display="New Diagnosis Name",
        diagnosis_aliases=["alias1", "alias2"],
        standard_warning_signs=[
            "Warning sign 1",
            "Warning sign 2",
            "Warning sign 3"
        ],
        standard_medications=[
            {
                "medication_code_rxnorm": "123456",
                "medication_display": "Medication Name",
                "dosage_value": "100",
                "dosage_unit": "mg",
                "frequency_code": "BID",
                "frequency_display": "Twice daily"
            }
        ],
        is_chronic_condition=False,
        requires_specialist_followup=True,
        typical_followup_days=7
    )

    db.add(diagnosis)
    db.commit()
```

### Searching Both Tiers Programmatically

```python
async def search_all_diagnoses(query: str, db: Session):
    # Search Tier 1 first
    tier1_results = db.query(DiagnosisContentMap).filter(
        DiagnosisContentMap.diagnosis_display.ilike(f"%{query}%")
    ).all()

    if tier1_results:
        return {
            "tier": 1,
            "type": "full_library",
            "results": tier1_results
        }

    # If not found, search Tier 2
    tier2_results = db.query(DiseaseReference).filter(
        DiseaseReference.disease_name.ilike(f"%{query}%")
    ).all()

    return {
        "tier": 2,
        "type": "reference",
        "results": tier2_results
    }
```

### Extending Reference Database with New Sources

```python
def import_from_new_source(source_url: str, db: Session):
    """
    Template for adding new data sources to Tier 2
    """
    # Fetch data from external source
    response = requests.get(source_url)
    data = response.json()

    for disease in data["diseases"]:
        ref = DiseaseReference(
            mondo_id=f"NEWSOURCE:{disease['id']}",
            disease_name=disease["name"],
            icd10_codes=disease.get("icd10_codes", []),
            short_description=disease.get("description"),
            disease_category=disease.get("category"),
            data_source="NEW_SOURCE"
        )

        db.add(ref)

    db.commit()
```

---

## For System Administrators: Deployment

### Initial Setup

```bash
# 1. Create database tables
python src/models/disease_reference.py

# 2. Import Tier 2 reference database (100 diseases)
python scripts/import_icd10_reference.py --limit 100

# 3. Import Tier 1 clinical library (30 diagnoses)
python scripts/expand_diagnosis_library.py

# 4. Verify import
curl http://localhost:8000/api/v1/disease-reference/stats
```

### Production Deployment

```bash
# Environment variables
export DATABASE_URL="postgresql://user:pass@localhost/ai_nurse_florence"
export ENABLE_TIER2_SEARCH=true
export PROMOTION_QUEUE_EMAIL="clinical.team@hospital.org"

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Monitoring

```bash
# Health check
curl http://localhost:8000/api/v1/disease-reference/health

# Database stats
curl http://localhost:8000/api/v1/disease-reference/stats

# Promotion queue (requires admin auth)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/v1/disease-reference/promotion-queue
```

### Backup Strategy

```bash
# Daily backup of Tier 1 (critical clinical content)
pg_dump -t diagnosis_content_map ai_nurse_florence > tier1_backup.sql

# Weekly backup of Tier 2 (can be regenerated)
pg_dump -t disease_reference ai_nurse_florence > tier2_backup.sql

# Backup promotion queue (workflow state)
pg_dump -t diagnosis_promotion_queue ai_nurse_florence > promotion_backup.sql
```

---

## Performance Benchmarks

| Operation | Tier 1 | Tier 2 | Notes |
|-----------|--------|--------|-------|
| **Search by name** | 15-30ms | 20-40ms | Indexed |
| **Search by ICD-10** | 5-10ms | 10-15ms | Unique index |
| **Get full diagnosis** | 10-20ms | N/A | Includes all JSON fields |
| **Get reference info** | N/A | 5-10ms | Lightweight data |
| **Database size** | ~50MB (1,000 diagnoses) | ~10MB (5,000 diseases) | With indexes |

---

## Future Enhancements

### Phase 2 (Q2 2025)
- [ ] Auto-promotion based on search frequency
- [ ] SNOMED code enrichment via UMLS API
- [ ] Multi-language support for disease names
- [ ] Synonym expansion from MONDO/UMLS

### Phase 3 (Q3 2025)
- [ ] Integration with UpToDate API (paid)
- [ ] FDA drug recall alerts tied to diagnoses
- [ ] Clinical guidelines linking
- [ ] ICD-11 preparation (WHO 2027 transition)

---

## Conclusion

The two-tier diagnosis system provides the best of both worlds:

✅ **Quality where it matters:** Full clinical content for common diagnoses
✅ **Comprehensive coverage:** Reference lookup for rare conditions
✅ **Scalable maintenance:** Focus curation efforts on high-value content
✅ **User experience:** Fast results + external resources for everything else

This architecture supports both immediate clinical needs and long-term scalability as the system grows.

---

**Next Chapter:** [Document Generation System](./DOCUMENT_SYSTEM_COMPLETE.md)
**Previous Chapter:** [Medical Data Sources](./MEDICAL_DATA_SOURCES.md)

---

*AI Nurse Florence - Healthcare Documentation Automation*
*© 2025 - Open Source Project*
