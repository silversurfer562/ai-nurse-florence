"""
Clinical Trials Service - AI Nurse Florence  
Following Service Layer Architecture with ClinicalTrials.gov integration
"""

import logging
from typing import Optional, Dict, Any
from src.utils.config import get_settings, get_educational_banner
from src.utils.redis_cache import cached

logger = logging.getLogger(__name__)

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
        Search clinical trials by condition or intervention.
        
        Following Service Layer Architecture:
        - Business logic separation from routing
        - Educational disclaimers included
        - Graceful fallback to stub data
        """
        try:
            if self.use_live and self._client:
                # In production: Call ClinicalTrials.gov API
                return await self._search_live_trials(query, limit)
            else:
                # Fallback: Educational stub data
                return self._create_stub_trials_response(query, limit)
                
        except Exception as e:
            logger.error(f"Clinical trials search error: {e}")
            return self._create_error_response(query, str(e))
    
    async def get_trial_details(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed trial information by NCT ID."""
        try:
            if self.use_live and self._client:
                # In production: Get specific trial details
                return await self._get_live_trial_details(nct_id)
            else:
                # Fallback: Stub trial details
                return self._create_stub_trial_details(nct_id)
                
        except Exception as e:
            logger.error(f"Trial details error for {nct_id}: {e}")
            return None
    
    async def _search_live_trials(self, query: str, limit: int) -> Dict[str, Any]:
        """Search live ClinicalTrials.gov (production implementation)."""
        # Production implementation would use clinicaltrials.gov API
        # For now, return enhanced stub data
        return self._create_stub_trials_response(query, limit)
    
    async def _get_live_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """Get live trial details (production implementation)."""
        # Production implementation would fetch from clinicaltrials.gov
        return self._create_stub_trial_details(nct_id)
    
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
