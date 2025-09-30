"""
Clinical Trials Service - AI Nurse Florence  
Following Service Layer Architecture with ClinicalTrials.gov integration
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from src.utils.config import get_settings, get_educational_banner
from src.utils.redis_cache import cached

logger = logging.getLogger(__name__)

# Conditional imports following Conditional Imports Pattern
try:
    from src.services.prompt_enhancement import enhance_prompt
    _has_prompt_enhancement = True
except Exception:
    _has_prompt_enhancement = False
    # Provide a lightweight fallback to satisfy static analysis and runtime when missing
    def enhance_prompt(prompt: str, purpose: str):
        return prompt, False, None

try:
    import requests
    _has_requests = True
except Exception:
    _has_requests = False
    # Fallback helper to raise a clear error if live API is attempted without requests
    class _RequestsStub:
        @staticmethod
        def get(*args, **kwargs):
            raise RuntimeError("requests package not available in this environment")

    requests = _RequestsStub()

# Backwards compatibility: prefer httpx when available for async calls
try:
    import httpx
    _has_httpx = True
except Exception:
    _has_httpx = False
    httpx = None

class ClinicalTrialsService:
    """
    Clinical trials service following Service Layer Architecture.
    Implements Conditional Imports Pattern for graceful degradation.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.use_live = self.settings.effective_use_live_services
        self.banner = get_educational_banner()
        
        # Try to initialize live service connection
        self._client = None
        if self.use_live:
            try:
                # In production, would initialize ClinicalTrials.gov API client
                logger.info("Clinical trials service: Using live ClinicalTrials.gov data")
            except Exception as e:
                logger.warning(f"Clinical trials service: Failed to connect to live service: {e}")
                self.use_live = False
    
    @cached(ttl_seconds=3600)
    async def search_trials(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search clinical trials by condition or intervention using live ClinicalTrials.gov API v2.

        Following Service Layer Architecture:
        - Business logic separation from routing
        - Educational disclaimers included
        - Live data only (no stubs)
        """
        try:
            return await self._search_live_trials(query, limit)
        except Exception as e:
            logger.error(f"Clinical trials search error: {e}")
            return self._create_error_response(query, str(e))
    
    async def get_trial_details(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed trial information by NCT ID using live API."""
        try:
            return await self._get_live_trial_details(nct_id)
        except Exception as e:
            logger.error(f"Trial details error for {nct_id}: {e}")
            return None
    
    async def _search_live_trials(self, query: str, limit: int) -> Dict[str, Any]:
        """Search live ClinicalTrials.gov API v2."""
        try:
            # ClinicalTrials.gov API v2 endpoint
            base_url = "https://clinicaltrials.gov/api/v2/studies"

            params = {
                "query.cond": query,
                "pageSize": min(limit, 100),  # Max 100 per page
                "format": "json"
            }

            if _has_httpx:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(base_url, params=params)
                    response.raise_for_status()
                    data = response.json()
            elif _has_requests:
                # Fallback to synchronous requests
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                raise RuntimeError("No HTTP client available (httpx or requests required)")

            # Parse the response
            studies = data.get("studies", [])
            trials = []

            for study in studies[:limit]:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})
                conditions_module = protocol.get("conditionsModule", {})

                trial = {
                    "nct_id": identification.get("nctId", "Unknown"),
                    "title": identification.get("briefTitle", "No title available"),
                    "phase": design_module.get("phases", ["N/A"])[0] if design_module.get("phases") else "N/A",
                    "status": status_module.get("overallStatus", "Unknown"),
                    "study_type": design_module.get("studyType", "Unknown"),
                    "condition": ", ".join(conditions_module.get("conditions", [query])),
                    "brief_summary": protocol.get("descriptionModule", {}).get("briefSummary", ""),
                    "locations": self._extract_locations(protocol.get("contactsLocationsModule", {}))
                }
                trials.append(trial)

            return {
                "banner": self.banner,
                "query": query,
                "condition": query,
                "total_studies": data.get("totalCount", len(trials)),
                "studies_summary": f"Found {len(trials)} clinical trials for '{query}' from ClinicalTrials.gov",
                "trials": trials,
                "sources": ["ClinicalTrials.gov API v2"],
                "needs_clarification": False
            }

        except Exception as e:
            logger.error(f"Live ClinicalTrials.gov API error: {e}")
            raise
    
    def _extract_locations(self, contacts_locations: Dict[str, Any]) -> list:
        """Extract location information from trial data."""
        locations = []
        for location in contacts_locations.get("locations", [])[:5]:  # Limit to 5 locations
            loc_info = {
                "facility": location.get("facility", "Unknown"),
                "city": location.get("city", ""),
                "state": location.get("state", ""),
                "country": location.get("country", "")
            }
            locations.append(loc_info)
        return locations

    async def _get_live_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """Get live trial details from ClinicalTrials.gov API v2."""
        try:
            base_url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}"

            if _has_httpx:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(base_url)
                    response.raise_for_status()
                    data = response.json()
            elif _has_requests:
                response = requests.get(base_url, timeout=30)
                response.raise_for_status()
                data = response.json()
            else:
                raise RuntimeError("No HTTP client available")

            # Parse study details
            protocol = data.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status_module = protocol.get("statusModule", {})
            description_module = protocol.get("descriptionModule", {})
            conditions_module = protocol.get("conditionsModule", {})
            design_module = protocol.get("designModule", {})
            arms_module = protocol.get("armsInterventionsModule", {})

            return {
                "banner": self.banner,
                "nct_id": nct_id,
                "title": identification.get("briefTitle", ""),
                "official_title": identification.get("officialTitle", ""),
                "brief_summary": description_module.get("briefSummary", ""),
                "detailed_description": description_module.get("detailedDescription", ""),
                "conditions": conditions_module.get("conditions", []),
                "phase": design_module.get("phases", ["N/A"])[0] if design_module.get("phases") else "N/A",
                "status": status_module.get("overallStatus", "Unknown"),
                "study_type": design_module.get("studyType", "Unknown"),
                "enrollment": status_module.get("enrollmentInfo", {}).get("count", "Unknown"),
                "interventions": [i.get("name", "") for i in arms_module.get("interventions", [])],
                "locations": self._extract_locations(protocol.get("contactsLocationsModule", {})),
                "source": "ClinicalTrials.gov API v2"
            }

        except Exception as e:
            logger.error(f"Live trial details error for {nct_id}: {e}")
            raise
    
    def _create_stub_trials_response(self, query: str, limit: int) -> Dict[str, Any]:
        """Create educational stub response following API Design Standards."""
        
        # Educational stub trials based on common conditions
        stub_trials = []
        
        if any(term in query.lower() for term in ['diabetes', 'glucose', 'insulin']):
            stub_trials = [
                {
                    "nct_id": "NCT12345678",
                    "title": f"Educational Example: Diabetes Management Study - Query: {query}",
                    "brief_summary": "Educational stub: This represents a typical diabetes intervention study design for learning purposes.",
                    "phase": "Phase 3",
                    "status": "Recruiting",
                    "conditions": ["Diabetes Mellitus, Type 2"],
                    "interventions": ["Lifestyle intervention", "Medication management"],
                    "primary_outcomes": ["HbA1c reduction", "Quality of life improvement"],
                    "enrollment": 500,
                    "sponsor": "Educational Medical Center"
                }
            ]
        
        elif any(term in query.lower() for term in ['hypertension', 'blood pressure', 'bp']):
            stub_trials = [
                {
                    "nct_id": "NCT87654321", 
                    "title": f"Educational Example: Hypertension Treatment Study - Query: {query}",
                    "brief_summary": "Educational stub: This represents a typical hypertension intervention study for learning purposes.",
                    "phase": "Phase 2/3",
                    "status": "Active",
                    "conditions": ["Hypertension", "Cardiovascular Disease"],
                    "interventions": ["Antihypertensive therapy", "Lifestyle counseling"],
                    "primary_outcomes": ["Blood pressure reduction", "Cardiovascular events"],
                    "enrollment": 750,
                    "sponsor": "Educational Cardiovascular Institute"
                }
            ]
        
        else:
            # Generic educational stub
            stub_trials = [
                {
                    "nct_id": "NCT11111111",
                    "title": f"Educational Example: Clinical Study for {query}",
                    "brief_summary": f"Educational stub: This represents a typical clinical study design for {query} research purposes.",
                    "phase": "Phase 2",
                    "status": "Not yet recruiting", 
                    "conditions": [query.title()],
                    "interventions": ["Investigational intervention", "Standard care comparison"],
                    "primary_outcomes": ["Primary endpoint measurement", "Safety assessment"],
                    "enrollment": 300,
                    "sponsor": "Educational Research Center"
                }
            ]
        
        return {
            "banner": self.banner,
            "query": query,
            "trials": stub_trials[:limit],
            "total_results": len(stub_trials),
            "service_note": "Educational stub data - not actual clinical trials. For real trial information, consult ClinicalTrials.gov directly.",
            "disclaimer": "This is educational content for learning clinical research concepts. Always verify trial information through official sources."
        }
    
    def _create_stub_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """Create detailed stub trial information."""
        
        return {
            "banner": self.banner,
            "nct_id": nct_id,
            "title": f"Educational Example: Detailed Trial Information for {nct_id}",
            "brief_summary": "Educational stub: This provides an example of detailed clinical trial information structure.",
            "detailed_description": "This is educational content showing the typical structure and information found in clinical trial records.",
            "phase": "Phase 2/3",
            "status": "Educational Example",
            "conditions": ["Educational Condition Example"],
            "interventions": [
                "Educational intervention A: Represents experimental treatment",
                "Educational intervention B: Represents control or comparison treatment"
            ],
            "primary_outcomes": [
                "Primary efficacy endpoint (educational example)",
                "Safety and tolerability assessment"
            ],
            "secondary_outcomes": [
                "Quality of life measures",
                "Long-term follow-up assessments"
            ],
            "enrollment": 400,
            "eligibility_criteria": "Educational example: Age 18-65, diagnosed condition, informed consent",
            "sponsor": "Educational Medical Research Institute",
            "location": "Educational Medical Centers (Multiple locations)",
            "contact_information": "For educational purposes only - contact real trials through ClinicalTrials.gov",
            "educational_note": "This is stub data for learning purposes. Real clinical trial information is available at ClinicalTrials.gov"
        }
    
    def _create_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "banner": self.banner,
            "query": query,
            "trials": [],
            "total_results": 0,
            "error": f"Clinical trials service temporarily unavailable: {error}",
            "fallback_note": "Service experiencing issues. Please try again later or visit ClinicalTrials.gov directly."
        }

# Service factory function following Conditional Imports Pattern
def create_clinical_trials_service() -> Optional[ClinicalTrialsService]:
    """
    Create clinical trials service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return ClinicalTrialsService()
    except Exception as e:
        logger.warning(f"Clinical trials service unavailable: {e}")
        return None

async def search_clinical_trials(condition: str, max_studies: int = 10) -> Dict[str, Any]:
    """
    Search clinical trials following External Service Integration pattern.
    
    Args:
        condition: Medical condition for clinical trials search
        max_studies: Maximum number of studies to return
        
    Returns:
        Dict containing clinical trials search results with educational banner
    """
    settings = get_settings()
    banner = get_educational_banner()
    
    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_condition, needs_clarification, clarification_question = enhance_prompt(condition, "clinical_trials")
            
            if needs_clarification:
                return {
                    "banner": banner,
                    "query": condition,
                    "condition": condition,
                    "needs_clarification": True,
                    "clarification_question": clarification_question
                }
        else:
            effective_condition = condition
        
        # Use live ClinicalTrials.gov API v2
        result = await _search_trials_live(effective_condition, max_studies)
        result["banner"] = banner
        result["query"] = condition
        result["condition"] = condition
        return result

    except Exception as e:
        logger.error(f"Clinical trials search failed: {e}")
        raise ExternalServiceException(f"ClinicalTrials.gov API error: {str(e)}", "clinical_trials")

async def _search_trials_live(condition: str, max_studies: int) -> Dict[str, Any]:
    """Search ClinicalTrials.gov using live API v2 following External Service Integration."""

    # ClinicalTrials.gov API v2 endpoint
    base_url = "https://clinicaltrials.gov/api/v2/studies"

    params = {
        "query.cond": condition,
        "pageSize": min(max_studies, 100),
        "format": "json"
    }

    if _has_httpx:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
    else:
        # Synchronous fallback for environments without httpx
        # Use asyncio.to_thread to avoid blocking the event loop
        response = await asyncio.to_thread(requests.get, base_url, {
            "params": params,
            "timeout": 15
        })
        # If the requests stub raises, it will surface here
        response.raise_for_status()
        data = response.json()
    
    # Parse API v2 response
    studies = data.get("studies", [])
    total_studies = data.get("totalCount", len(studies))

    trials = []
    for study in studies[:max_studies]:
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        conditions_module = protocol.get("conditionsModule", {})

        trials.append({
            "nct_id": identification.get("nctId", "Unknown"),
            "title": identification.get("briefTitle", "No title available"),
            "phase": design_module.get("phases", ["N/A"])[0] if design_module.get("phases") else "N/A",
            "status": status_module.get("overallStatus", "Unknown"),
            "study_type": design_module.get("studyType", "Unknown"),
            "condition": ", ".join(conditions_module.get("conditions", [condition]))
        })

    return {
        "total_studies": total_studies,
        "studies_summary": f"Found {len(trials)} clinical trials related to '{condition}' from ClinicalTrials.gov API v2",
        "trials": trials,
        "sources": ["ClinicalTrials.gov API v2"]
    }

def _create_trials_stub_response(condition: str, banner: str, max_studies: int) -> Dict[str, Any]:
    """Create stub response for clinical trials search following Conditional Imports Pattern."""
    
    return {
        "banner": banner,
        "query": condition,
        "condition": condition,
        "total_studies": 15,  # Stub data
        "studies_summary": f"Clinical trials search completed for '{condition}'. This is educational stub data - use live services for actual trial information.",
        "trials": [
            {
                "nct_id": "NCT12345678",
                "title": f"Phase III Study of {condition} Treatment",
                "phase": "Phase 3",
                "status": "Recruiting",
                "study_type": "Interventional",
                "condition": condition
            },
            {
                "nct_id": "NCT87654321",
                "title": f"Observational Study of {condition} Outcomes",
                "phase": "N/A",
                "status": "Active, not recruiting",
                "study_type": "Observational",
                "condition": condition
            }
        ],
        "sources": ["ClinicalTrials.gov (Educational stub data)"],
        "needs_clarification": False
    }
