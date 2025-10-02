# Parallel Work Plan - While Waiting for UMLS

> **Situation:** UMLS account applied for, approval pending (1-2 days)
> **Strategy:** Work on parallel tracks - don't wait idle
> **Goal:** Stay on track for end-of-October launch

---

## The Plan: Don't Wait - Execute in Parallel

Instead of blocking on UMLS approval, we'll work on **3 parallel tracks**:

```
┌─────────────────────────────────────────────────────┐
│             PARALLEL EXECUTION STRATEGY              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Track A: SNOMED Prep (ready when UMLS approved)   │
│  Track B: Quick Wins (billable flags, etc.)        │
│  Track C: Week 2 Work (PostgreSQL, hierarchy)      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Track A: SNOMED Preparation (Ready to Execute)

**Status:** Prepare everything NOW, run when UMLS approved

### Tasks (Complete Today)

**1. Create UMLS Client Module** [1 hour]
```python
# src/integrations/umls_client.py
# Complete implementation from UMLS_INTEGRATION_GUIDE.md
# Ready to use when API key arrives
```

**2. Create Enrichment Script** [1 hour]
```python
# scripts/enrich_snomed_codes.py
# Batch process all 34 Tier 1 diagnoses
# Just needs API key as parameter
```

**3. Add SNOMED Column to Database** [15 minutes]
```python
# Already exists in DiagnosisContentMap model
# Verify it's ready to receive data
```

**4. Prepare Test Cases** [30 minutes]
```python
# Known mappings for validation:
test_cases = {
    "E11.9": "44054006",  # Type 2 Diabetes
    "I10": "38341003",     # Hypertension
    "J45.909": "195967001" # Asthma
}
```

**When UMLS Approved:**
- Run: `python scripts/enrich_snomed_codes.py --api-key YOUR_KEY`
- Time: 30 minutes
- Result: All 34 diagnoses enriched ✅

---

## Track B: Quick Wins (Complete While Waiting)

**Status:** No blockers - can do today

### 1. Billable Code Flags [2 hours]

**Implementation:**

```python
# Add to disease_reference.py model
class DiseaseReference(Base):
    is_billable = Column(Boolean, default=True)  # NEW
    billable_note = Column(String(200))          # NEW

# Business logic:
def determine_billable_status(icd10_code):
    """
    CMS billable code rules:
    - 3-character codes: NOT billable (too vague)
    - 4-character codes: Sometimes billable
    - 5+ character codes: Usually billable
    """
    code_without_dot = icd10_code.replace(".", "")

    if len(code_without_dot) <= 3:
        return False, "Code requires additional specificity for billing"
    elif len(code_without_dot) == 4:
        return True, "Verify with payer - may require more specificity"
    else:
        return True, None
```

**Script to Update Database:**
```bash
python scripts/add_billable_flags.py
```

**Tasks:**
- [ ] Add `is_billable` and `billable_note` columns
- [ ] Create update script
- [ ] Process all 12,252 diseases
- [ ] Add UI warning for non-billable codes
- [ ] Test with sample searches

**Time:** 2 hours
**Blocker:** None ✅

---

### 2. Patient-Friendly Descriptions [Start Today, 2-3 hours]

**Approach:** Start with easiest/most common diagnoses first

**Top 10 to Start:**
1. Type 2 Diabetes (E11.9)
2. Hypertension (I10)
3. Asthma (J45.909)
4. Pneumonia (J18.9)
5. UTI (N39.0)
6. COPD (J44.1)
7. Heart Failure (I50.9)
8. Chest Pain (R07.9)
9. Abdominal Pain (R10.9)
10. Headache (R51)

**Format:**
```python
# Technical (CDC):
"Type 2 diabetes mellitus without complications"

# Patient-Friendly (Grade 6-8):
"Type 2 diabetes is when your body can't use sugar properly. Your blood sugar stays too high, which can damage your body over time."
```

**Tasks:**
- [ ] Add `patient_friendly_description` column
- [ ] Write descriptions for top 10 (15 min each)
- [ ] Run Flesch-Kincaid readability test
- [ ] Add UI toggle (technical vs friendly)

**Time:** 2-3 hours for 10 descriptions
**Blocker:** None ✅

---

### 3. Update API Documentation [1 hour]

**Tasks:**
- [ ] Generate OpenAPI/Swagger docs
- [ ] Add MedlinePlus endpoints
- [ ] Document disease reference endpoints
- [ ] Add examples and response schemas

**Tool:** FastAPI auto-generates most of this!

```python
# Just add better descriptions to endpoints
@router.get("/by-icd10/{icd10_code}",
    summary="Get patient education by ICD-10 code",
    description="""
    Fetches patient education content from MedlinePlus for a given ICD-10 code.

    - Caches results for 24 hours
    - Supports English and Spanish
    - Returns external resource links if API unavailable
    """,
    responses={
        200: {"description": "Education content found"},
        404: {"description": "No content available for this code"}
    }
)
```

**Time:** 1 hour
**Blocker:** None ✅

---

## Track C: Week 2 Work (Get a Head Start)

**Status:** Start now, finish in Week 2

### 1. PostgreSQL Setup [Start Today, 2-3 hours]

**Tasks:**

**Day 1 (Today):**
- [ ] Install PostgreSQL 15+ via Docker
  ```bash
  docker run --name ai-nurse-postgres \
    -e POSTGRES_PASSWORD=yourpassword \
    -e POSTGRES_DB=ai_nurse_florence \
    -p 5432:5432 \
    -d postgres:15
  ```
- [ ] Install Python PostgreSQL adapter
  ```bash
  pip install psycopg2-binary
  ```
- [ ] Create database connection config
  ```python
  # config/database.py
  DATABASES = {
      "development": "sqlite:///ai_nurse_florence.db",
      "production": "postgresql://user:pass@localhost/ai_nurse_florence"
  }
  ```
- [ ] Test connection

**Day 2 (Tomorrow or next):**
- [ ] Install Alembic (migration tool)
- [ ] Create initial migration
- [ ] Test migration with sample data

**Time:** 2-3 hours to get started
**Blocker:** None ✅

---

### 2. Code Hierarchy from Order File [Start Today, 3-4 hours]

**File:** `data/icd10_raw/icd10cm-order-2025.txt`

**This file contains:**
```
A00-B99    Certain infectious and parasitic diseases
  A00-A09    Intestinal infectious diseases
    A00      Cholera
      A000     Cholera due to Vibrio cholerae 01, biovar cholerae
      A001     Cholera due to Vibrio cholerae 01, biovar eltor
      A009     Cholera, unspecified
```

**What we need to extract:**
- Chapter ranges (A00-B99)
- Category ranges (A00-A09)
- Parent-child relationships (A00 → A000, A001, A009)

**Implementation:**

```python
# scripts/parse_icd10_hierarchy.py

import re

def parse_order_file(filepath):
    """Parse ICD-10 order file to extract hierarchy"""

    hierarchy = []
    current_chapter = None
    current_category = None

    with open(filepath, 'r') as f:
        for line in f:
            # Detect indentation level
            indent = len(line) - len(line.lstrip())
            code_line = line.strip()

            # Extract code and description
            match = re.match(r'^([A-Z0-9.-]+)\s+(.+)$', code_line)
            if match:
                code, description = match.groups()

                hierarchy.append({
                    "code": code,
                    "description": description,
                    "level": indent // 2,
                    "parent": get_parent(code, indent)
                })

    return hierarchy

def get_parent(code, indent):
    """Determine parent code based on indentation"""
    # Logic to find parent from previous entries
    pass
```

**Tasks:**
- [ ] Parse order file
- [ ] Extract hierarchy
- [ ] Add `parent_code` column to database
- [ ] Update all 12,252 diseases with parent references
- [ ] Create API endpoint for breadcrumb navigation

**Time:** 3-4 hours
**Blocker:** None ✅

---

## Today's Execution Plan (Oct 2)

**Morning (3-4 hours):**
1. ☕ Coffee
2. Create UMLS client module (ready for API key)
3. Create SNOMED enrichment script (ready to run)
4. Add billable code flags to database

**Afternoon (3-4 hours):**
5. Write patient-friendly descriptions (top 10)
6. Start PostgreSQL Docker setup
7. Begin parsing ICD-10 order file for hierarchy

**By EOD:**
- ✅ SNOMED scripts ready (waiting for API key only)
- ✅ Billable flags implemented
- ✅ 10 patient-friendly descriptions written
- ✅ PostgreSQL development environment running
- ✅ Hierarchy parsing started

**Progress:** Week 1 goes from 80% → 95% (without UMLS!)

---

## Tomorrow (Oct 3) - If UMLS Not Yet Approved

**Continue parallel tracks:**

**Option A: If UMLS approved overnight**
- ✅ Run SNOMED enrichment (30 min)
- ✅ Week 1 complete (100%)!
- 🚀 Move to Week 2 tasks

**Option B: If UMLS still pending**
- Continue Week 2 tasks:
  - Complete PostgreSQL migration
  - Finish hierarchy parsing
  - Write more patient-friendly descriptions (11-20)
  - Set up Epic sandbox (if available)

**Either way:** We're making progress!

---

## Backup Plan: Manual SNOMED Mapping

**If UMLS takes longer than expected (>3 days):**

We can manually map the 34 codes using public resources:

**Resources:**
- SNOMED CT Browser: https://browser.ihtsdotools.org/
- NIH Value Sets: https://vsac.nlm.nih.gov/
- ICD-10 to SNOMED Map: https://www.nlm.nih.gov/research/umls/mapping_projects/icd10cm_to_snomedct.html

**Process:**
1. Look up each ICD-10 code (e.g., E11.9)
2. Find SNOMED CT equivalent in browser
3. Manually enter in database

**Time:** ~10 minutes per code = 5-6 hours for all 34

**When to use:** If UMLS approval takes >5 days

---

## Week 1 Revised Schedule

**Original Plan:**
- Day 1: Disease library + MedlinePlus ✅ DONE
- Day 2-3: SNOMED enrichment ⏸️ WAITING
- Day 4-7: Nothing planned ❌

**New Plan:**
- Day 1: Disease library + MedlinePlus ✅ DONE
- Day 2: SNOMED prep + billable flags + descriptions ⏳ TODAY
- Day 3: PostgreSQL + hierarchy + more descriptions ⏳ TOMORROW
- Day 4-5: Complete Week 2 tasks early! ⏳ GETTING AHEAD
- Day 6-7: SNOMED enrichment when approved ⏳ FINISH WEEK 1

**Result:** Week 1 still completes on time, even with UMLS delay!

---

## Benefits of Parallel Execution

**Without parallel execution:**
```
Day 1: Work ✅
Day 2: Wait for UMLS ⏸️
Day 3: Wait for UMLS ⏸️
Day 4: UMLS approved, do SNOMED ✅
Day 5: Start Week 2 work
```
**Result:** Lost 2-3 days waiting

**With parallel execution:**
```
Day 1: Work ✅
Day 2: SNOMED prep + other tasks ✅
Day 3: Week 2 tasks + more prep ✅
Day 4: UMLS approved, quick SNOMED run ✅
Day 5: Continue Week 2 (already started!)
```
**Result:** Zero days lost, actually ahead of schedule!

---

## Risk Mitigation

| Scenario | Probability | Plan |
|----------|-------------|------|
| **UMLS approved tomorrow** | Medium | Run enrichment, Week 1 done early ✅ |
| **UMLS approved in 2-3 days** | High | Parallel work keeps us on track ✅ |
| **UMLS takes 5+ days** | Low | Manual mapping or defer to Week 2 |
| **UMLS rejected** | Very Low | Manual mapping (6 hours) |

**In all scenarios:** We stay on track for end-of-October launch!

---

## Key Insight

**The UMLS delay is actually a GIFT** 🎁

**Why?**
- Forces us to work in parallel (more efficient)
- Gets Week 2 work started early
- Proves we're not blocked by dependencies
- Demonstrates true agile execution

**Lesson:** Never wait idle when you can work on parallel tracks

---

## Updated Sprint Status

**Week 1 Status:**
- Day 1: 80% complete ✅
- Day 2 (today): Target 95% ⏳
- Day 3-7: Can complete Week 2 tasks early!

**Confidence:** Still HIGH 🎯

**Launch Date:** Still October 24-28 ✅

---

## Your Action Items Today

**Pick any 2-3 (based on energy/time):**

**Quick wins (2 hours each):**
- [ ] Billable code flags
- [ ] Patient-friendly descriptions (top 10)
- [ ] API documentation update

**Medium tasks (3-4 hours each):**
- [ ] PostgreSQL Docker setup
- [ ] ICD-10 hierarchy parsing
- [ ] SNOMED script preparation

**Recommended for today:**
1. ✅ Billable flags (2 hours) - Easy win
2. ✅ Patient descriptions (2 hours) - User value
3. ✅ PostgreSQL setup (2 hours) - Get ahead on Week 2

**Total:** 6 hours of productive work while waiting for UMLS

---

**Bottom line:** We don't wait. We execute in parallel. We stay on track. 🚀

---

*AI Nurse Florence - Parallel Work Plan*
*Created: October 1, 2025*
*Strategy: Execute while waiting*
