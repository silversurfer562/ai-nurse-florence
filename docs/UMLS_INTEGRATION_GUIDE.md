# UMLS Integration Guide

> **What:** Unified Medical Language System - comprehensive medical terminology integration
> **Provider:** National Library of Medicine (NLM)
> **Cost:** FREE (requires free account)
> **Purpose:** Map ICD-10 codes to SNOMED CT codes for Epic/EHR integration

---

## What is UMLS?

**UMLS (Unified Medical Language System)** is a comprehensive set of files and software that integrates multiple health and biomedical vocabularies to enable interoperability between computer systems.

Think of it as a **"Rosetta Stone" for medical terminology** - it maps and connects different medical coding systems.

### What UMLS Provides

**1. Metathesaurus**
- Terms and codes from 200+ biomedical vocabularies
- **Includes:** ICD-10, SNOMED CT, RxNorm, LOINC, MeSH, CPT, and more
- **Mappings:** Cross-references between different coding systems
- **Size:** 4+ million concepts, 15+ million terms

**2. Semantic Network**
- Broad categories for medical concepts (e.g., "Disease", "Medication")
- Relationships between categories (e.g., "treats", "causes")
- **Use:** Classification and reasoning

**3. SPECIALIST Lexicon**
- Linguistic tools for natural language processing
- Helps with medical text processing

---

## Why We Need UMLS

### Our Requirement: ICD-10 → SNOMED CT Mapping

**Problem:**
- We have 34 Tier 1 diagnoses with ICD-10 codes ✅
- Epic/EHRs primarily use SNOMED CT codes ❌
- Need both for FHIR R4 compliance

**Solution:**
- Use UMLS Metathesaurus to map ICD-10 → SNOMED CT
- Example: `E11.9` (ICD-10) → `44054006` (SNOMED CT) for Type 2 Diabetes

**FHIR CodeableConcept Format (What Epic Expects):**
```json
{
  "coding": [
    {
      "system": "http://hl7.org/fhir/sid/icd-10-cm",
      "code": "E11.9",
      "display": "Type 2 diabetes mellitus without complications"
    },
    {
      "system": "http://snomed.info/sct",
      "code": "44054006",
      "display": "Diabetes mellitus type 2"
    }
  ]
}
```

---

## How to Get Access (Step-by-Step)

### Step 1: Sign Up for UMLS Account

1. Go to: **https://uts.nlm.nih.gov/uts/signup-login**

2. Click **"Request a License"** or **"Sign Up"**

3. Fill out the form:
   - Name and contact information
   - Intended use: "Healthcare software development"
   - Accept UMLS Metathesaurus License Agreement

4. Verify your email address

5. **Approval Time:** Usually 1-2 business days (sometimes instant)

### Step 2: Get Your API Key

1. Log in to: **https://uts.nlm.nih.gov/uts/**

2. Go to **"My Profile"**

3. Click **"Generate API Key"** or **"Get Your API Key"**

4. Copy your API key (keep it secure!)

**API Key Format:**
```
XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
```

### Step 3: Test Your Access

Try this in your browser (replace `YOUR_API_KEY`):
```
https://uts-ws.nlm.nih.gov/rest/search/current?string=diabetes&apiKey=YOUR_API_KEY
```

If you see JSON results → ✅ You're ready!

---

## UMLS REST API

### Base URL
```
https://uts-ws.nlm.nih.gov/rest
```

### Authentication
All requests require your API key:
```
?apiKey=YOUR_API_KEY
```

---

## Common API Endpoints

### 1. Search for a Concept

**Endpoint:**
```
GET /search/current?string={search_term}&apiKey={key}
```

**Example: Search for "diabetes"**
```bash
curl "https://uts-ws.nlm.nih.gov/rest/search/current?string=diabetes&apiKey=YOUR_KEY"
```

**Response:**
```json
{
  "result": {
    "results": [
      {
        "ui": "C0011849",  // CUI (Concept Unique Identifier)
        "name": "Diabetes Mellitus",
        "uri": "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0011849"
      }
    ]
  }
}
```

**Key Field:** `ui` = CUI (Concept Unique Identifier) - this is the universal ID for this concept across all vocabularies

---

### 2. Get Concept Details (by CUI)

**Endpoint:**
```
GET /content/current/CUI/{cui}?apiKey={key}
```

**Example: Get diabetes details**
```bash
curl "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0011849?apiKey=YOUR_KEY"
```

**Response includes:**
- Concept name
- Definition
- Semantic types
- Relationships
- Atoms (terms from different vocabularies)

---

### 3. Crosswalk Between Vocabularies ⭐ MOST IMPORTANT

**Endpoint:**
```
GET /crosswalk/current/source/{source}/{id}?apiKey={key}
```

**Example: Map ICD-10 code to SNOMED CT**

Step 1: Get CUI from ICD-10 code
```bash
curl "https://uts-ws.nlm.nih.gov/rest/crosswalk/current/source/ICD10CM/E11.9?apiKey=YOUR_KEY"
```

Step 2: Response includes SNOMED CT codes
```json
{
  "result": [
    {
      "ui": "C0011860",
      "name": "Type 2 Diabetes Mellitus",
      "sourceId": "E11.9",
      "sourceName": "ICD10CM",
      "targetId": "44054006",  // SNOMED CT code!
      "targetName": "SNOMEDCT_US"
    }
  ]
}
```

**Perfect!** Now we have both codes:
- ICD-10: `E11.9`
- SNOMED CT: `44054006`

---

### 4. Get All Codes for a Concept (Alternative Approach)

**Endpoint:**
```
GET /content/current/CUI/{cui}/atoms?apiKey={key}&sabs=ICD10CM,SNOMEDCT_US
```

**Example: Get all ICD-10 and SNOMED codes for diabetes**
```bash
curl "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0011860/atoms?apiKey=YOUR_KEY&sabs=ICD10CM,SNOMEDCT_US"
```

**Response:**
```json
{
  "result": [
    {
      "code": "E11.9",
      "rootSource": "ICD10CM",
      "name": "Type 2 diabetes mellitus without complications"
    },
    {
      "code": "44054006",
      "rootSource": "SNOMEDCT_US",
      "name": "Diabetes mellitus type 2"
    }
  ]
}
```

---

## Python Integration Example

### Basic UMLS Client

```python
import requests
from typing import Optional, Dict

class UMLSClient:
    """Client for UMLS Terminology Services API"""

    BASE_URL = "https://uts-ws.nlm.nih.gov/rest"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()

    def search_concept(self, search_term: str) -> Optional[str]:
        """
        Search for a concept and return its CUI.

        Args:
            search_term: Term to search (e.g., "diabetes")

        Returns:
            CUI (Concept Unique Identifier) or None
        """
        url = f"{self.BASE_URL}/search/current"
        params = {
            "string": search_term,
            "apiKey": self.api_key
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("result", {}).get("results", [])

        if results:
            return results[0]["ui"]  # Return first CUI
        return None

    def icd10_to_snomed(self, icd10_code: str) -> Optional[str]:
        """
        Map ICD-10 code to SNOMED CT code.

        Args:
            icd10_code: ICD-10-CM code (e.g., "E11.9")

        Returns:
            SNOMED CT code or None
        """
        url = f"{self.BASE_URL}/crosswalk/current/source/ICD10CM/{icd10_code}"
        params = {"apiKey": self.api_key}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        results = data.get("result", [])

        # Find SNOMED CT mapping
        for result in results:
            if result.get("targetName") == "SNOMEDCT_US":
                return result.get("targetId")

        return None

    def get_concept_codes(self, cui: str) -> Dict[str, str]:
        """
        Get ICD-10 and SNOMED codes for a CUI.

        Args:
            cui: Concept Unique Identifier

        Returns:
            Dict with ICD-10 and SNOMED codes
        """
        url = f"{self.BASE_URL}/content/current/CUI/{cui}/atoms"
        params = {
            "apiKey": self.api_key,
            "sabs": "ICD10CM,SNOMEDCT_US"  # Only get these vocabularies
        }

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        atoms = data.get("result", [])

        codes = {}
        for atom in atoms:
            source = atom.get("rootSource")
            code = atom.get("code")

            if source == "ICD10CM":
                codes["icd10"] = code
            elif source == "SNOMEDCT_US":
                codes["snomed"] = code

        return codes


# Usage example
if __name__ == "__main__":
    # Initialize client
    client = UMLSClient(api_key="YOUR_API_KEY_HERE")

    # Example 1: Map ICD-10 to SNOMED
    icd10_code = "E11.9"
    snomed_code = client.icd10_to_snomed(icd10_code)
    print(f"{icd10_code} (ICD-10) → {snomed_code} (SNOMED CT)")

    # Example 2: Search for diabetes and get all codes
    cui = client.search_concept("type 2 diabetes")
    codes = client.get_concept_codes(cui)
    print(f"ICD-10: {codes.get('icd10')}")
    print(f"SNOMED: {codes.get('snomed')}")
```

---

## Batch Enrichment Script

### For Our 34 Tier 1 Diagnoses

```python
#!/usr/bin/env python3
"""
Enrich Tier 1 diagnoses with SNOMED CT codes from UMLS.

Usage:
    python scripts/enrich_snomed_codes.py --api-key YOUR_KEY
"""

import sys
import os
import argparse
from time import sleep

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.content_settings import DiagnosisContentMap
from umls_client import UMLSClient  # From above


def enrich_diagnoses(api_key: str, db_path: str = "ai_nurse_florence.db"):
    """Enrich all Tier 1 diagnoses with SNOMED codes"""

    # Setup database
    engine = create_engine(f'sqlite:///{db_path}')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create UMLS client
    umls = UMLSClient(api_key)

    # Get all diagnoses without SNOMED codes
    diagnoses = session.query(DiagnosisContentMap).filter(
        DiagnosisContentMap.snomed_code.is_(None)
    ).all()

    print(f"Found {len(diagnoses)} diagnoses without SNOMED codes")
    print()

    # Enrich each diagnosis
    success_count = 0
    fail_count = 0

    for diagnosis in diagnoses:
        print(f"Processing: {diagnosis.diagnosis_display}")
        print(f"  ICD-10: {diagnosis.icd10_code}")

        try:
            # Map ICD-10 to SNOMED
            snomed_code = umls.icd10_to_snomed(diagnosis.icd10_code)

            if snomed_code:
                diagnosis.snomed_code = snomed_code
                print(f"  ✅ SNOMED: {snomed_code}")
                success_count += 1
            else:
                print(f"  ⚠️  No SNOMED mapping found")
                fail_count += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            fail_count += 1

        print()

        # Rate limiting (be nice to API)
        sleep(0.5)

    # Commit changes
    session.commit()

    print("=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)
    print(f"✅ Success: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Enrich diagnoses with SNOMED codes")
    parser.add_argument("--api-key", required=True, help="UMLS API key")
    parser.add_argument("--db", default="ai_nurse_florence.db", help="Database path")

    args = parser.parse_args()

    enrich_diagnoses(args.api_key, args.db)


if __name__ == "__main__":
    main()
```

**Usage:**
```bash
# After getting UMLS API key:
python scripts/enrich_snomed_codes.py --api-key YOUR_API_KEY_HERE

# Expected output:
# Processing: Type 2 diabetes mellitus without complications
#   ICD-10: E11.9
#   ✅ SNOMED: 44054006
#
# ... (33 more diagnoses)
#
# ENRICHMENT COMPLETE
# ✅ Success: 34
# ❌ Failed: 0
```

---

## Important Vocabularies in UMLS

| Abbreviation | Full Name | Use Case |
|--------------|-----------|----------|
| **ICD10CM** | ICD-10 Clinical Modification | Diagnosis billing (what we have) |
| **SNOMEDCT_US** | SNOMED CT US Edition | Epic/EHR standard (what we need) |
| **RXNORM** | RxNorm | Medication codes |
| **LOINC** | Logical Observation Identifiers | Lab tests |
| **CPT** | Current Procedural Terminology | Procedures |
| **MESH** | Medical Subject Headings | PubMed indexing |

---

## Rate Limits & Best Practices

### Rate Limits
- **No official limit documented**
- Recommended: **~2-3 requests per second** (be respectful)
- For batch processing: Add `sleep(0.5)` between requests

### Best Practices
1. **Cache results** - Store SNOMED codes in your database
2. **Batch processing** - Process all 34 diagnoses in one script run
3. **Error handling** - Some ICD-10 codes may not have SNOMED mappings
4. **API key security** - Never commit API key to git (use environment variable)

---

## Common Issues & Solutions

### Issue 1: API Key Not Working
**Solution:**
- Make sure account is approved (check email)
- Verify API key is active in UTS profile
- Check for typos in API key

### Issue 2: No SNOMED Mapping Found
**Solution:**
- Not all ICD-10 codes have direct SNOMED equivalents
- Try searching by concept name instead
- May need manual mapping for some codes

### Issue 3: API Returns Empty Results
**Solution:**
- Check ICD-10 code format (include dot: "E11.9" not "E119")
- Verify using ICD10CM (not ICD10 or ICD10PCS)
- Try crosswalk endpoint instead of search

---

## Alternative: Manual SNOMED Mapping

If UMLS API unavailable or delayed, you can manually map the 34 codes:

**Resources:**
- SNOMED CT Browser: https://browser.ihtsdotools.org/
- ICD-10 to SNOMED Map: https://www.nlm.nih.gov/research/umls/mapping_projects/icd10cm_to_snomedct.html

**Estimated Time:** ~5-10 minutes per code = 3-6 hours for all 34

---

## Next Steps for Our Project

### Tomorrow (Oct 2) - SNOMED Enrichment

**Step 1:** Sign up for UMLS (5 minutes)
- Go to: https://uts.nlm.nih.gov/uts/signup-login
- Fill out form
- Verify email

**Step 2:** Get API key (instant)
- Log in to UTS
- Generate API key
- Store securely (environment variable)

**Step 3:** Create enrichment script (2-3 hours)
- Copy UMLS client code (from this doc)
- Create `scripts/enrich_snomed_codes.py`
- Add error handling and logging

**Step 4:** Run enrichment (30 minutes)
- Process all 34 Tier 1 diagnoses
- Verify SNOMED codes
- Commit to database

**Step 5:** Validate FHIR format (30 minutes)
- Update API responses to include SNOMED
- Test FHIR CodeableConcept format
- Validate with FHIR validator

**Total Time:** ~4 hours (including UMLS signup approval if instant)

---

## Cost

**FREE** ✅

- UMLS license: **$0**
- API access: **$0**
- No rate limit charges: **$0**

**Only requirement:** Free account registration

---

## Summary

**UMLS** = Unified Medical Language System (NLM)

**Purpose:** Map between medical coding systems

**Our Use:** ICD-10 → SNOMED CT for Epic integration

**Access:** Free account + API key

**API:** REST API with JSON responses

**Timeline:** Sign up today, enrich tomorrow (1 day total)

**Alternative:** Manual mapping if API delayed (3-6 hours)

---

**Ready to proceed tomorrow! 🚀**

---

*AI Nurse Florence - UMLS Integration Guide*
*Created: October 1, 2025*
*Next Step: Sign up for UMLS account (Oct 2)*
