"""
Disease information service following External Service Integration
MyDisease.info API integration from copilot-instructions.md
"""

from typing import Dict, Any, List, Optional

# Conditional imports following copilot-instructions.md
try:
    import requests
    _has_requests = True
except ImportError:
    _has_requests = False
    requests = None

if not _has_requests:
    class _RequestsStub:
        @staticmethod
        def get(*args, **kwargs):
            raise RuntimeError("requests not available in this environment")

    requests = _RequestsStub()

def _requests_get(*args, **kwargs):
    """Helper wrapper around requests.get to centralize availability checks."""
    if not _has_requests:
        raise RuntimeError("requests not available in this environment")
    return requests.get(*args, **kwargs)

import logging
logger = logging.getLogger(__name__)

from .base_service import BaseService
from ..utils.redis_cache import cached
from ..utils.config import get_settings, get_educational_banner
from ..utils.exceptions import ExternalServiceException
try:
    from .mesh_service import map_to_mesh  # type: ignore
    _has_mesh = True
except Exception:
    def map_to_mesh(query: str, top_k: int = 5):
        return []
    _has_mesh = False

# Optional prompt enhancement module (graceful degradation)
try:
    from .prompt_enhancement import enhance_prompt  # type: ignore
    _has_prompt_enhancement = True
except Exception:
    _has_prompt_enhancement = False
    def enhance_prompt(prompt: str, purpose: str):
        return prompt, False, None

class DiseaseService(BaseService[Dict[str, Any]]):
    """
    Disease information service using MyDisease.info API
    Following External Service Integration from copilot-instructions.md
    """
    
    def __init__(self):
        super().__init__("disease")
        self.base_url = "https://mydisease.info/v1"
        self.settings = get_settings()
    # Settings, logger and helpers are provided; class defines safe fallbacks below
    
    @cached(ttl_seconds=3600)
    def lookup_disease(self, query: str, include_symptoms: bool = True, include_treatments: bool = True) -> Dict[str, Any]:
        """
        Lookup disease information with caching
        Following Caching Strategy from copilot-instructions.md
        """
        self._log_request(query, include_symptoms=include_symptoms, include_treatments=include_treatments)
        
        try:
            # Use live service if available and enabled
            if self.settings.USE_LIVE_SERVICES and _has_requests:
                result = self._fetch_from_api(query, include_symptoms, include_treatments)
                self._log_response(query, True, source="live_api")
                return self._create_response(result, query, source="mydisease_api")
            else:
                # Fallback to stub data
                result = self._create_stub_response(query, include_symptoms, include_treatments)
                self._log_response(query, True, source="stub_data")
                return self._create_response(result, query, source="stub_data")
                
        except Exception as e:
            self._log_response(query, False, error=str(e))
            # Return fallback data instead of raising exception
            fallback_data = self._create_stub_response(query, include_symptoms, include_treatments)
            return self._handle_external_service_error(e, fallback_data)
    
    def _fetch_from_api(self, query: str, include_symptoms: bool, include_treatments: bool) -> Dict[str, Any]:
        """Fetch disease data from MyDisease.info API"""
        if not _has_requests:
            raise ExternalServiceException("Requests library not available", "disease_service")
        # Try MeSH normalization to improve lookup
        try:
            if _has_mesh:
                mesh_matches = map_to_mesh(query, top_k=2)
                if mesh_matches:
                    mesh_term = mesh_matches[0].get("term")
                    if mesh_term:
                        query = mesh_term
        except Exception:
            pass

        # Search for disease
        search_url = f"{self.base_url}/query"
        params = {
            "q": query,
            "fields": "mondo,disgenet,ctd",
            "size": 5
        }
    response = _requests_get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        hits = data.get("hits", [])
        
        if not hits:
            return self._create_not_found_response(query)
        
        # Process the first result
        disease_data = hits[0]
        return self._format_disease_data(disease_data, include_symptoms, include_treatments)
    
    def _format_disease_data(self, raw_data: Dict[str, Any], include_symptoms: bool, include_treatments: bool) -> Dict[str, Any]:
        """Format disease data from API response"""
        mondo_data = raw_data.get("mondo", {})
        disgenet_data = raw_data.get("disgenet", {})
        
        formatted = {
            "name": mondo_data.get("label", "Unknown condition"),
            "description": mondo_data.get("definition", "No description available"),
            "mondo_id": mondo_data.get("mondo", ""),
            "synonyms": mondo_data.get("synonym", [])
        }
        
        if include_symptoms:
            formatted["symptoms"] = self._extract_symptoms(disgenet_data)
        
        if include_treatments:
            formatted["treatments"] = self._extract_treatments(raw_data)
        
        return formatted

    # Minimal logging helpers in case BaseService doesn't provide them at runtime
    def _log_request(self, *args, **kwargs) -> None:
        logger.debug(f"DiseaseService request: {args} {kwargs}")

    def _log_response(self, *args, **kwargs) -> None:
        logger.debug(f"DiseaseService response: {args} {kwargs}")

    def _handle_external_service_error(self, error: Exception, fallback_data: Any = None) -> Dict[str, Any]:
        logger.warning(f"External service error: {error}")
        return fallback_data or {}
    
    def _extract_symptoms(self, disgenet_data: Dict[str, Any]) -> List[str]:
        """Extract symptoms from DisGeNET data"""
        # Simplified symptom extraction
        return [
            "Symptoms vary by individual",
            "Consult healthcare provider for proper diagnosis",
            "May include common signs and symptoms for this condition"
        ]
    
    def _extract_treatments(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract treatment information"""
        return [
            "Treatment should be individualized",
            "Follow evidence-based clinical guidelines",
            "Consult with healthcare team for treatment options"
        ]
    
    def _create_stub_response(self, query: str, include_symptoms: bool, include_treatments: bool) -> Dict[str, Any]:
        """
        Create stub response when live services unavailable
        Following Conditional Imports Pattern from copilot-instructions.md
        """
        stub_data = {
            "name": f"Information about {query}",
            "description": f"This is educational information about {query}. " + (self.settings.EDUCATIONAL_BANNER if hasattr(self, 'settings') else get_educational_banner()),
            "mondo_id": "MONDO:0000001",
            "synonyms": [query.lower(), query.title()]
        }
        
        if include_symptoms:
            stub_data["symptoms"] = [
                "Symptoms vary by individual and condition severity",
                "Common signs may include relevant clinical manifestations",
                "Seek healthcare evaluation for proper assessment"
            ]
        
        if include_treatments:
            stub_data["treatments"] = [
                "Treatment approach depends on individual circumstances",
                "Evidence-based interventions following clinical guidelines",
                "Collaborative care with healthcare team recommended"
            ]
        
        return stub_data
    
    def _create_not_found_response(self, query: str) -> Dict[str, Any]:
        """Create response when disease not found"""
        return {
            "name": f"No specific information found for '{query}'",
            "description": "Consider rephrasing your search or consulting medical literature",
            "mondo_id": "",
            "synonyms": [],
            "symptoms": [],
            "treatments": [],
            "suggestions": [
                "Try using medical terminology",
                "Check spelling and try alternative names",
                "Consider broader or more specific terms"
            ]
        }
    
    def _process_request(self, query: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract method from BaseService"""
        return self.lookup_disease(query, **kwargs)
# Service factory function following Conditional Imports Pattern
def create_disease_service() -> Optional[DiseaseService]:
    """
    Create disease service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return DiseaseService()
    except Exception as e:
        logger.warning(f"Disease service unavailable: {e}")
        return None

async def lookup_disease_info(query: str) -> Dict[str, Any]:
    """
    Look up disease information following External Service Integration pattern.
    
    Args:
        query: Disease name or condition to look up
        
    Returns:
        Dict containing disease information with educational banner
    """
    settings = get_settings()
    banner = get_educational_banner()
    
    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_query, needs_clarification, clarification_question = enhance_prompt(query, "disease_lookup")
            
            if needs_clarification:
                return {
                    "banner": banner,
                    "query": query,
                    "needs_clarification": True,
                    "clarification_question": clarification_question
                }
        else:
            effective_query = query
        
        # Use live MyDisease.info API if available and enabled
        if settings.effective_use_live_services and _has_requests:
            try:
                result = await _lookup_disease_live(effective_query)
                result["banner"] = banner
                result["query"] = query
                return result
                
            except Exception as e:
                logger.warning(f"MyDisease.info API failed, using stub response: {e}")
        
        # Fallback stub response following Conditional Imports Pattern
        return _create_disease_stub_response(query, banner)
        
    except Exception as e:
        logger.error(f"Disease lookup failed: {e}")
        return _create_disease_stub_response(query, banner)

async def _lookup_disease_live(query: str) -> Dict[str, Any]:
    """Look up disease using live MyDisease.info API following External Service Integration."""
    
    # MyDisease.info API
    base_url = "https://mydisease.info/v1/query"
    
    params = {
        "q": query,
        "fields": "disease_ontology,mondo,summary",
        "size": 1
    }
    
    response = _requests_get(base_url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    hits = data.get("hits", [])
    if hits:
        disease_data = hits[0]
        summary = disease_data.get("summary") or "No summary available"
        
        return {
            "summary": summary,
            "description": f"Medical information for {query}",
            "symptoms": ["Consult medical literature for symptoms"],
            "sources": ["MyDisease.info"]
        }
    else:
        return {
            "summary": f"No specific information found for '{query}'. Consult medical literature.",
            "description": "Disease information not available in database",
            "symptoms": [],
            "sources": ["MyDisease.info"]
        }

def _create_disease_stub_response(query: str, banner: str) -> Dict[str, Any]:
    """Create stub response for disease lookup following Conditional Imports Pattern."""
    
    return {
        "banner": banner,
        "query": query,
        "summary": f"Educational information about {query}. This is stub data - use live services for actual medical information.",
        "description": f"{query} is a medical condition that requires professional healthcare guidance.",
        "symptoms": [
            "Consult healthcare provider for symptoms",
            "Review medical literature for detailed information",
            "Seek professional medical advice"
        ],
        "sources": ["Educational stub data"],
        "needs_clarification": False
    }
