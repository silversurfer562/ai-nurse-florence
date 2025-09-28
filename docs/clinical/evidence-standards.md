# Evidence Standards Documentation
## Clinical evidence integration standards for AI Nurse Florence

## Overview

AI Nurse Florence integrates with multiple authoritative medical data sources to provide evidence-based clinical information. This document outlines the standards, protocols, and best practices for integrating and utilizing external medical evidence sources.

## External Service Integration Architecture

### Service Layer Pattern with Conditional Loading

```python
# Core pattern for all external service integrations
import os

USE_LIVE = os.getenv("USE_LIVE", "false").lower() == "true"

try:
    if USE_LIVE:
        from live_mydisease import lookup as disease_lookup
        from live_pubmed import search as pubmed_search
        from live_clinicaltrials import search as trials_search
    else:
        from stubs.mock_services import (
            disease_lookup, 
            pubmed_search, 
            trials_search
        )
except ImportError as e:
    # Graceful degradation to stub services
    from stubs.fallback_services import get_fallback_service
    disease_lookup = get_fallback_service("disease")
    pubmed_search = get_fallback_service("pubmed")
    trials_search = get_fallback_service("trials")
```

## Integrated Medical Data Sources

### 1. MyDisease.info Integration

**Purpose**: Comprehensive disease information aggregation  
**API Version**: v1  
**Base URL**: `https://mydisease.info/v1`

#### Integration Standards
```python
class MyDiseaseIntegration:
    """
    Standards for MyDisease.info integration
    """
    
    @staticmethod
    def lookup(term: str) -> dict:
        """
        Query disease information with cross-references
        
        Returns:
        {
            "name": "Disease name",
            "mondo": "MONDO:0000000",  # Mondo Disease Ontology ID
            "umls": "C0000000",         # UMLS Concept ID
            "mesh": "D000000",          # MeSH ID
            "description": "Clinical description",
            "synonyms": ["alternate names"],
            "xrefs": {                  # Cross-references
                "orphanet": "ORPHA:0000",
                "omim": "000000",
                "icd10": "X00.0"
            }
        }
        """
        response = requests.get(
            f"https://mydisease.info/v1/query",
            params={"q": term, "fields": "all"}
        )
        return standardize_disease_response(response.json())
```

#### Evidence Quality Indicators
- **Authoritative Source**: NIH/NCBI BioThings API
- **Update Frequency**: Weekly
- **Coverage**: 20,000+ diseases
- **Cross-References**: MONDO, UMLS, MeSH, ICD-10, OMIM

### 2. PubMed/NCBI Integration

**Purpose**: Medical literature and research evidence  
**API**: E-utilities API  
**Base URL**: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`

#### Integration Standards
```python
class PubMedIntegration:
    """
    Standards for PubMed/NCBI integration
    """
    
    # Rate limiting compliance
    DEFAULT_RATE_LIMIT = 3  # requests per second without API key
    AUTHENTICATED_RATE_LIMIT = 10  # with NCBI API key
    
    @staticmethod
    def search(query: str, max_results: int = 10) -> list:
        """
        Search PubMed for relevant literature
        
        Returns:
        [
            {
                "pmid": "00000000",
                "title": "Article title",
                "authors": ["Author1", "Author2"],
                "journal": "Journal Name",
                "year": 2025,
                "abstract": "Abstract text",
                "mesh_terms": ["Term1", "Term2"],
                "publication_type": ["Research", "Clinical Trial"],
                "evidence_level": "I",  # Classified by study type
                "doi": "10.1000/journal.0000"
            }
        ]
        """
        # Implement rate limiting
        time.sleep(1 / get_rate_limit())
        
        # Search with proper field tags
        search_results = esearch(query)
        pmids = extract_pmids(search_results)
        
        # Fetch detailed records
        articles = efetch(pmids)
        return classify_evidence_level(articles)
```

#### Evidence Classification
```python
def classify_evidence_level(article):
    """
    Classify evidence according to standard hierarchy
    """
    publication_types = article.get("publication_type", [])
    
    if "Systematic Review" in publication_types:
        return "Ia"  # Systematic review of RCTs
    elif "Randomized Controlled Trial" in publication_types:
        return "Ib"  # Individual RCT
    elif "Controlled Clinical Trial" in publication_types:
        return "IIa"  # Controlled trial without randomization
    elif "Cohort Study" in publication_types:
        return "IIb"  # Cohort study
    elif "Case-Control Study" in publication_types:
        return "III"  # Case-control study
    elif "Case Report" in publication_types:
        return "IV"  # Case series/report
    else:
        return "V"  # Expert opinion
```

### 3. ClinicalTrials.gov Integration

**Purpose**: Current and completed clinical studies  
**API Version**: v2  
**Base URL**: `https://clinicaltrials.gov/api/v2`

#### Integration Standards
```python
class ClinicalTrialsIntegration:
    """
    Standards for ClinicalTrials.gov integration
    """
    
    @staticmethod
    def search(condition: str, status: str = None) -> list:
        """
        Search for relevant clinical trials
        
        Returns:
        [
            {
                "nct_id": "NCT00000000",
                "title": "Study title",
                "status": "Recruiting",
                "phase": "Phase 3",
                "conditions": ["Condition1", "Condition2"],
                "interventions": ["Drug A", "Procedure B"],
                "sponsor": "Organization name",
                "enrollment": 500,
                "start_date": "2024-01-01",
                "completion_date": "2026-12-31",
                "locations": ["City, State, Country"],
                "eligibility": {
                    "min_age": "18 Years",
                    "max_age": "65 Years",
                    "gender": "All"
                }
            }
        ]
        """
        params = {
            "query.cond": condition,
            "pageSize": max_results
        }
        if status:
            params["filter.overallStatus"] = status
            
        response = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params=params
        )
        return standardize_trial_response(response.json())
```

### 4. MedlinePlus Integration

**Purpose**: Patient education materials  
**API**: MedlinePlus Connect  
**Base URL**: `https://connect.medlineplus.gov/service`

#### Integration Standards
```python
class MedlinePlusIntegration:
    """
    Standards for MedlinePlus patient education
    """
    
    @staticmethod
    def get_patient_education(code: str, code_system: str = "ICD10") -> dict:
        """
        Retrieve patient-friendly health information
        
        Returns:
        {
            "topic": "Condition name",
            "summary": "Plain language summary",
            "content_sections": [
                {
                    "title": "What is it?",
                    "content": "Description",
                    "reading_level": 8  # Grade level
                }
            ],
            "languages": ["English", "Spanish"],
            "last_reviewed": "2025-01-01",
            "images": ["url1", "url2"],
            "videos": ["url1", "url2"]
        }
        """
        response = requests.get(
            "https://connect.medlineplus.gov/service",
            params={
                "mainSearchCriteria.v.c": code,
                "mainSearchCriteria.v.cs": code_system,
                "informationRecipient.languageCode.c": "en"
            }
        )
        return process_education_materials(response.text)
```

## Evidence Quality Standards

### Source Reliability Hierarchy

1. **Level A - Highest Quality**
   - Cochrane Reviews
   - Clinical Practice Guidelines from major societies
   - FDA-approved prescribing information
   - WHO recommendations

2. **Level B - High Quality**
   - PubMed systematic reviews and meta-analyses
   - Randomized controlled trials
   - ClinicalTrials.gov registered studies

3. **Level C - Moderate Quality**
   - Observational studies
   - Case-control studies
   - Expert consensus statements

4. **Level D - Lower Quality**
   - Case reports
   - Expert opinion
   - Theoretical models

### Currency Requirements

```python
def assess_evidence_currency(publication_date):
    """
    Evaluate currency of evidence
    """
    years_old = (datetime.now() - publication_date).days / 365
    
    if years_old <= 2:
        return "CURRENT"
    elif years_old <= 5:
        return "RECENT"
    elif years_old <= 10:
        return "DATED"
    else:
        return "HISTORICAL"
```

### Evidence Synthesis Standards

```python
class EvidenceSynthesizer:
    """
    Standards for combining evidence from multiple sources
    """
    
    @staticmethod
    def synthesize(evidence_items: list) -> dict:
        """
        Combine and weight evidence appropriately
        """
        # Sort by evidence level
        sorted_evidence = sorted(
            evidence_items, 
            key=lambda x: x['evidence_level']
        )
        
        synthesis = {
            "primary_evidence": sorted_evidence[0:3],
            "supporting_evidence": sorted_evidence[3:10],
            "consensus_level": calculate_consensus(sorted_evidence),
            "recommendation_strength": determine_strength(sorted_evidence),
            "evidence_gaps": identify_gaps(sorted_evidence)
        }
        
        return synthesis
```

## Caching and Performance Standards

### Cache Strategy
```python
from utils.redis_cache import cached

# Disease information - cache for 24 hours
@cached(ttl_seconds=86400)
def get_disease_info(disease_name):
    return disease_lookup(disease_name)

# Literature search - cache for 1 hour
@cached(ttl_seconds=3600)
def search_literature(query):
    return pubmed_search(query)

# Clinical trials - cache for 6 hours
@cached(ttl_seconds=21600)
def find_trials(condition):
    return trials_search(condition)
```

### Rate Limiting Compliance
```python
class RateLimiter:
    """
    Ensure compliance with API rate limits
    """
    
    def __init__(self, service_name, max_per_second):
        self.service_name = service_name
        self.max_per_second = max_per_second
        self.last_request = 0
        
    def wait_if_needed(self):
        elapsed = time.time() - self.last_request
        min_interval = 1.0 / self.max_per_second
        
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        
        self.last_request = time.time()
```

## Error Handling Standards

### Graceful Degradation Pattern
```python
def get_medical_evidence(condition: str) -> dict:
    """
    Retrieve evidence with graceful degradation
    """
    evidence = {}
    
    # Try primary source
    try:
        evidence['disease'] = disease_lookup(condition)
    except ExternalServiceException:
        evidence['disease'] = get_cached_or_stub('disease', condition)
    
    # Try literature search
    try:
        evidence['literature'] = pubmed_search(condition)
    except ExternalServiceException:
        evidence['literature'] = get_cached_or_stub('literature', condition)
    
    # Always return something useful
    if not evidence:
        evidence = get_fallback_evidence(condition)
    
    return add_disclaimer(evidence)
```

### Service Health Monitoring
```python
class ServiceHealthMonitor:
    """
    Monitor external service availability
    """
    
    def __init__(self):
        self.service_status = {}
        
    async def check_health(self):
        """
        Periodic health checks
        """
        services = [
            ("mydisease", "https://mydisease.info/v1/metadata"),
            ("pubmed", "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=test"),
            ("trials", "https://clinicaltrials.gov/api/v2/stats")
        ]
        
        for name, url in services:
            try:
                response = await async_get(url, timeout=5)
                self.service_status[name] = "healthy" if response.ok else "degraded"
            except:
                self.service_status[name] = "unavailable"
```

## Data Standardization

### FHIR Compliance
```python
def convert_to_fhir(medical_data):
    """
    Convert to FHIR standard format
    """
    return {
        "resourceType": "Condition",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": medical_data.get('snomed_code'),
                    "display": medical_data.get('name')
                }
            ]
        },
        "severity": medical_data.get('severity'),
        "evidence": [
            {
                "code": {
                    "text": item['title']
                },
                "detail": [
                    {
                        "reference": f"PubMed/{item['pmid']}"
                    }
                ]
            }
            for item in medical_data.get('evidence', [])
        ]
    }
```

## Compliance and Legal Standards

### Medical Disclaimers
All evidence must include:
```python
STANDARD_DISCLAIMER = """
This information is for educational purposes only and is not intended as medical advice. 
It should not replace consultation with qualified healthcare professionals. 
No personal health information (PHI) is stored or retained.
Evidence levels and recommendations are based on published literature and may not 
apply to individual patient circumstances.
"""
```

### Attribution Requirements
```python
def format_citation(source):
    """
    Proper attribution for all evidence
    """
    if source['type'] == 'pubmed':
        return f"{source['authors']}. {source['title']}. {source['journal']}. {source['year']};{source['volume']}:{source['pages']}. PMID: {source['pmid']}"
    elif source['type'] == 'trial':
        return f"{source['title']}. ClinicalTrials.gov Identifier: {source['nct_id']}"
    elif source['type'] == 'disease':
        return f"{source['name']}. Source: MyDisease.info. MONDO: {source['mondo_id']}"
```

## Quality Assurance

### Evidence Validation
```python
def validate_evidence_quality(evidence):
    """
    Ensure evidence meets minimum standards
    """
    checks = {
        "has_source": bool(evidence.get('source')),
        "has_date": bool(evidence.get('publication_date')),
        "is_current": assess_evidence_currency(evidence.get('publication_date')) != "HISTORICAL",
        "has_citation": bool(evidence.get('citation')),
        "has_evidence_level": bool(evidence.get('evidence_level'))
    }
    
    quality_score = sum(checks.values()) / len(checks)
    
    if quality_score < 0.6:
        raise ValueError("Evidence does not meet minimum quality standards")
    
    return quality_score
```

### Continuous Improvement
- Monthly review of evidence sources
- Quarterly assessment of API performance
- Annual review of evidence standards
- User feedback integration

## API Keys and Authentication

### Configuration Standards
```python
# Environment variable configuration
NCBI_API_KEY = os.getenv('NCBI_API_KEY')  # Optional, improves rate limits
COCHRANE_API_KEY = os.getenv('COCHRANE_API_KEY')  # For systematic reviews
UPTODATE_API_KEY = os.getenv('UPTODATE_API_KEY')  # Clinical decision support

# API key rotation
def rotate_api_keys():
    """
    Periodic key rotation for security
    """
    # Implementation depends on key management system
    pass
```

## Documentation Requirements

All integrated evidence must include:
1. Source identification
2. Access timestamp
3. Evidence level classification
4. Currency assessment
5. Relevant disclaimers
6. Proper citations
7. Cross-references to related evidence

---

**Last Updated**: September 2025  
**Compliance**: HIPAA-aligned, no PHI storage  
**Standards**: Evidence-based medicine principles
