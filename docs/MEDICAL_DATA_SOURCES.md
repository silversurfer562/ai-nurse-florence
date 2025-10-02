# Medical Data Sources for AI Nurse Florence

## Public Databases for Diagnosis & Medication Data

---

## 🏥 Diagnosis & Disease Information

### **1. MONDO Disease Ontology** ⭐ RECOMMENDED
- **What:** Comprehensive disease ontology with ICD-10 and SNOMED mappings
- **Access:** Free, public API
- **URL:** https://monarchinitiative.org/mondo
- **Coverage:** 20,000+ diseases with cross-references
- **Best For:** Getting standardized disease names with ICD-10 and SNOMED codes
- **API:** https://api.monarchinitiative.org/api/

**Example Use:**
```python
# Get disease by ICD-10 code
GET https://api.monarchinitiative.org/api/search/entity/E11.9
# Returns: Diabetes Type 2 with MONDO, ICD-10, SNOMED, UMLS codes
```

### **2. ICD-10 API (WHO)**
- **What:** Official WHO ICD-10 classification
- **Access:** Free API (registration required)
- **URL:** https://icd.who.int/icdapi
- **Coverage:** Complete ICD-10 catalog
- **Best For:** Official ICD-10 codes and descriptions
- **API Docs:** https://icd.who.int/icdapi/docs2/

**Example Use:**
```python
# Search for diabetes
GET https://id.who.int/icd/release/10/2019/E11
# Returns: Complete ICD-10 hierarchy and descriptions
```

### **3. SNOMED CT (UMLS)**
- **What:** Comprehensive clinical terminology
- **Access:** Free via UMLS (account required)
- **URL:** https://www.nlm.nih.gov/research/umls/
- **Coverage:** 350,000+ clinical concepts
- **Best For:** SNOMED CT codes (Epic's primary coding system)
- **API:** https://uts-ws.nlm.nih.gov/rest

**Note:** Requires free UMLS account: https://uts.nlm.nih.gov/uts/signup-login

### **4. MedlinePlus Connect**
- **What:** Patient-friendly health information
- **Access:** Free, public API (no key required)
- **URL:** https://medlineplus.gov/connect/
- **Coverage:** 1,000+ health topics
- **Best For:** Patient education content, warning signs, self-care tips
- **API:** https://connect.medlineplus.gov/service

**Example Use:**
```python
# Get diabetes patient education
GET https://connect.medlineplus.gov/service?mainSearchCriteria.v.c=E11.9&mainSearchCriteria.v.cs=2.16.840.1.113883.6.90&informationRecipient.languageCode.c=en
# Returns: Patient education materials, symptoms, treatment
```

---

## 💊 Medication Information

### **1. RxNorm (NLM)** ⭐ RECOMMENDED
- **What:** Standardized medication nomenclature
- **Access:** Free, public API (no key required)
- **URL:** https://rxnav.nlm.nih.gov/
- **Coverage:** 100,000+ medication names
- **Best For:** RxNorm codes (Epic/FHIR standard), medication relationships
- **API:** https://rxnav.nlm.nih.gov/REST.html

**Example Use:**
```python
# Get RxNorm code for Metformin
GET https://rxnav.nlm.nih.gov/REST/rxcui.json?name=metformin
# Returns: RxNorm CUI (860975)

# Get medication details
GET https://rxnav.nlm.nih.gov/REST/rxcui/860975/allProperties.json
# Returns: Brand names, ingredients, dosage forms
```

### **2. OpenFDA Drug API** ⭐ RECOMMENDED
- **What:** FDA drug labels and adverse events
- **Access:** Free, public API (no key required, but rate limited)
- **URL:** https://open.fda.gov/apis/drug/
- **Coverage:** All FDA-approved drugs
- **Best For:** Drug labels, side effects, warnings, interactions
- **API Docs:** https://open.fda.gov/apis/drug/label/

**Example Use:**
```python
# Get Metformin drug label
GET https://api.fda.gov/drug/label.json?search=openfda.generic_name:metformin
# Returns: Complete FDA label with warnings, side effects, interactions
```

### **3. DailyMed**
- **What:** FDA published medication information
- **Access:** Free, public API
- **URL:** https://dailymed.nlm.nih.gov/
- **Coverage:** All FDA-approved drugs
- **Best For:** Current drug labels, package inserts
- **API:** https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm

### **4. DrugBank** (Limited Free)
- **What:** Comprehensive drug database
- **Access:** Free for non-commercial (academic license)
- **URL:** https://go.drugbank.com/
- **Coverage:** 14,000+ drugs
- **Best For:** Drug interactions, mechanisms of action
- **API:** Requires academic/commercial license

---

## 🔄 Integration Strategy

### **Immediate: Expand Diagnosis Library**

Use **MONDO + MedlinePlus** for quick expansion:

```python
# 1. Get disease list from MONDO
diseases = get_mondo_diseases(category="common")

# 2. For each disease, get:
#    - ICD-10 code (from MONDO)
#    - SNOMED code (from MONDO)
#    - Patient education (from MedlinePlus)
#    - Standard content (AI-generated or curated)

# 3. Populate diagnosis_content_map table
```

### **Ongoing Maintenance**

**Weekly Updates:**
- Check OpenFDA for drug label updates
- Sync RxNorm for new medications
- Update patient education from MedlinePlus

**Monthly Updates:**
- MONDO database refresh
- ICD-10 code updates (WHO releases)
- New disease additions

---

## 📊 Recommended Expansion Plan

### **Phase 1: Top 50 ED/Clinic Diagnoses** (Week 1)

**Cardiovascular (10):**
- Chest Pain (R07.9)
- Atrial Fibrillation (I48.91)
- Myocardial Infarction (I21.9)
- Deep Vein Thrombosis (I82.40)
- Pulmonary Embolism (I26.99)
- Syncope (R55)
- Hypertensive Crisis (I16.9)
- Heart Failure Exacerbation (I50.9) ✅ Already added
- Peripheral Vascular Disease (I73.9)
- Stroke/TIA (I63.9, G45.9)

**Respiratory (8):**
- Asthma Exacerbation (J45.901)
- COPD Exacerbation (J44.1) ✅ Already added
- Pneumonia (J18.9) ✅ Already added
- Bronchitis (J20.9)
- Pleural Effusion (J90)
- Pulmonary Edema (J81.0)
- Upper Respiratory Infection (J06.9)
- COVID-19 (U07.1)

**Gastrointestinal (8):**
- Abdominal Pain (R10.9)
- Nausea/Vomiting (R11.2)
- Gastroenteritis (K52.9)
- GI Bleeding (K92.2)
- Constipation (K59.00)
- Diarrhea (K59.1)
- Diverticulitis (K57.92)
- Appendicitis (K37)

**Infectious Disease (6):**
- Sepsis (A41.9)
- UTI (N39.0) ✅ Already added
- Cellulitis (L03.90)
- Influenza (J11.1)
- C. diff Infection (A04.7)
- Meningitis (G03.9)

**Endocrine/Metabolic (5):**
- Diabetes Type 2 (E11.9) ✅ Already added
- Diabetes Type 1 (E10.9)
- Hyperglycemia (R73.9)
- Hypoglycemia (E16.2)
- Hypothyroidism (E03.9)

**Neurological (5):**
- Seizure Disorder (G40.909)
- Headache (R51)
- Migraine (G43.909)
- Altered Mental Status (R41.82)
- Vertigo (R42)

**Renal/GU (4):**
- Acute Kidney Injury (N17.9)
- Chronic Kidney Disease (N18.9)
- Renal Colic (N23)
- Hematuria (R31.9)

**Trauma/Injury (4):**
- Fracture (S42.90) - example
- Laceration (S01.01) - example
- Contusion (S00.83) - example
- Sprain/Strain (S93.40) - example

### **Phase 2: Specialty Conditions** (Week 2)

**Pediatrics:**
- Croup
- RSV
- Febrile Seizure
- Otitis Media
- Gastroenteritis (pediatric dosing)

**OB/GYN:**
- Preeclampsia
- Gestational Diabetes
- Hyperemesis Gravidarum
- Ectopic Pregnancy

**Psychiatric:**
- Major Depression
- Anxiety Disorder
- Bipolar Disorder
- Suicidal Ideation

### **Phase 3: Chronic Conditions** (Week 3)

- Rheumatoid Arthritis
- Lupus
- Multiple Sclerosis
- Parkinson's Disease
- Alzheimer's/Dementia
- Chronic Pain Syndrome

---

## 🛠️ Implementation Tools

### **Python Libraries**

```python
# Install these for database access
pip install requests
pip install umls-python-client  # For UMLS/SNOMED
pip install fhir.resources      # For FHIR validation
```

### **Sample Integration Code**

```python
import requests
import json

# 1. Get disease info from MONDO
def get_disease_from_mondo(icd10_code):
    url = f"https://api.monarchinitiative.org/api/search/entity/{icd10_code}"
    response = requests.get(url)
    return response.json()

# 2. Get patient education from MedlinePlus
def get_patient_education(icd10_code):
    url = f"https://connect.medlineplus.gov/service"
    params = {
        "mainSearchCriteria.v.c": icd10_code,
        "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.90",
        "informationRecipient.languageCode.c": "en"
    }
    response = requests.get(url, params=params)
    return response.json()

# 3. Get medication info from RxNorm
def get_medication_from_rxnorm(med_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={med_name}"
    response = requests.get(url)
    data = response.json()

    if data.get('idGroup', {}).get('rxnormId'):
        rxcui = data['idGroup']['rxnormId'][0]

        # Get full properties
        prop_url = f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}/allProperties.json"
        prop_response = requests.get(prop_url)
        return prop_response.json()

    return None

# 4. Get drug label from OpenFDA
def get_drug_label(generic_name):
    url = f"https://api.fda.gov/drug/label.json"
    params = {
        "search": f"openfda.generic_name:{generic_name}",
        "limit": 1
    }
    response = requests.get(url, params=params)
    return response.json()
```

---

## 📋 Data Quality Standards

### **Required Fields for Each Diagnosis**

✅ **Minimum Requirements:**
- ICD-10 code (primary)
- SNOMED code (Epic compatibility)
- Diagnosis display name
- 3-5 warning signs
- 3-5 standard medications (with RxNorm)
- 2-3 activity restrictions
- Diet instructions
- Follow-up recommendations

✅ **Enhanced Quality:**
- Aliases/common names
- Patient education links
- Typical follow-up timeframe
- Chronic vs acute classification
- Specialist referral flag

### **Required Fields for Each Medication**

✅ **Minimum Requirements:**
- RxNorm code
- Generic name
- 2-3 brand names
- Common dosages
- Common frequencies
- 3-5 common side effects
- 2-3 serious warnings
- Storage instructions

✅ **Enhanced Quality:**
- Food interactions
- Drug interactions
- Contraindications
- Missed dose instructions
- FDA label link

---

## 🔐 API Access & Rate Limits

| Database | API Key Required | Rate Limit | Cost |
|----------|------------------|------------|------|
| **MONDO** | No | Unlimited | Free |
| **MedlinePlus** | No | Unlimited | Free |
| **RxNorm** | No | Unlimited | Free |
| **OpenFDA** | No (recommended) | 240/min (1000/min with key) | Free |
| **ICD-10 (WHO)** | Yes (free) | 500/day | Free |
| **UMLS/SNOMED** | Yes (free account) | Varies | Free (non-commercial) |

**Recommendation:** Get free API keys for OpenFDA and WHO ICD-10 to avoid rate limits.

---

## 🚀 Next Steps

1. **Create expansion script** using MONDO + MedlinePlus
2. **Populate 50 common diagnoses** (Phase 1)
3. **Add 100 common medications** using RxNorm + OpenFDA
4. **Set up weekly update job** to sync with public databases
5. **Create validation system** to ensure data quality

---

## 📚 Additional Resources

- **FHIR Terminology Services:** https://terminology.hl7.org/
- **LOINC (Lab codes):** https://loinc.org/
- **CPT Codes:** https://www.ama-assn.org/practice-management/cpt
- **Clinical Guidelines:** https://www.guidelines.gov/
- **UpToDate (paid):** https://www.uptodate.com/ (best clinical content, requires subscription)

---

**Bottom Line:** We can build a comprehensive, automatically-maintained medical database using 100% free public APIs! 🎉
