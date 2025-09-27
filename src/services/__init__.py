"""
Service layer initialization following Service Layer Architecture
Conditional imports pattern from copilot-instructions.md
"""

from typing import Dict, Any, Optional
import logging

# Conditional imports following copilot-instructions.md pattern
try:
    from .disease_service import DiseaseService
    _has_disease_service = True
except ImportError as e:
    _has_disease_service = False
    logging.warning(f"Disease service unavailable: {e}")

try:
    from .pubmed_service import PubMedService
    _has_pubmed_service = True
except ImportError as e:
    _has_pubmed_service = False
    logging.warning(f"PubMed service unavailable: {e}")

try:
    from .clinical_trials_service import ClinicalTrialsService
    _has_clinical_trials_service = True
except ImportError as e:
    _has_clinical_trials_service = False
    logging.warning(f"Clinical trials service unavailable: {e}")

# Service registry for dependency injection
_service_registry: Dict[str, Any] = {}

def get_service(service_name: str) -> Optional[Any]:
    """
    Get service instance following Service Layer Architecture
    Returns None if service unavailable (Conditional Imports Pattern)
    """
    if service_name not in _service_registry:
        try:
            if service_name == "disease" and _has_disease_service:
                _service_registry[service_name] = DiseaseService()
            elif service_name == "pubmed" and _has_pubmed_service:
                _service_registry[service_name] = PubMedService()
            elif service_name == "clinical_trials" and _has_clinical_trials_service:
                _service_registry[service_name] = ClinicalTrialsService()
            else:
                return None
        except Exception as e:
            logging.error(f"Failed to initialize {service_name} service: {e}")
            return None
    
    return _service_registry.get(service_name)

def get_available_services() -> Dict[str, bool]:
    """Get status of all services for health checks"""
    return {
        "disease": _has_disease_service,
        "pubmed": _has_pubmed_service,
        "clinical_trials": _has_clinical_trials_service
    }

__all__ = ["get_service", "get_available_services"]
