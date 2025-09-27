"""
Service Layer Architecture - AI Nurse Florence
Following coding instructions for service registry with Conditional Imports Pattern
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Service registry following Service Layer Architecture
_service_registry = {}
_service_status = {}

def _load_services():
    """Load all services following Conditional Imports Pattern."""
    
    # Disease service
    try:
        from .disease_service import create_disease_service
        service = create_disease_service()
        _service_registry['disease'] = service
        _service_status['disease'] = service is not None
        logger.info("Disease service registered")
    except ImportError as e:
        logger.warning(f"Disease service unavailable: {e}")
        _service_status['disease'] = False
    
    # PubMed service
    try:
        from .pubmed_service import create_pubmed_service
        service = create_pubmed_service()
        _service_registry['pubmed'] = service
        _service_status['pubmed'] = service is not None
        logger.info("PubMed service registered")
    except ImportError as e:
        logger.warning(f"PubMed service unavailable: {e}")
        _service_status['pubmed'] = False
    
    # Clinical trials service
    try:
        from .clinical_trials_service import create_clinical_trials_service
        service = create_clinical_trials_service()
        _service_registry['clinical_trials'] = service
        _service_status['clinical_trials'] = service is not None
        logger.info("Clinical trials service registered")
    except ImportError as e:
        logger.warning(f"Clinical trials service unavailable: {e}")
        _service_status['clinical_trials'] = False
    
    # SBAR service
    try:
        from .sbar_service import create_sbar_service
        service = create_sbar_service()
        _service_registry['sbar'] = service
        _service_status['sbar'] = service is not None
        logger.info("SBAR service registered")
    except ImportError as e:
        logger.warning(f"SBAR service unavailable: {e}")
        _service_status['sbar'] = False
    
    # OpenAI service
    try:
        from .openai_client import create_openai_service
        service = create_openai_service()
        _service_registry['openai'] = service
        _service_status['openai'] = service is not None
        logger.info("OpenAI service registered")
    except ImportError as e:
        logger.warning(f"OpenAI service unavailable: {e}")
        _service_status['openai'] = False

def get_service(service_name: str) -> Optional[Any]:
    """Get service instance following Service Layer Architecture."""
    if not _service_registry:
        _load_services()
    return _service_registry.get(service_name)

def get_available_services() -> Dict[str, bool]:
    """Get status of all services."""
    if not _service_registry:
        _load_services()
    return _service_status.copy()

# Initialize services
_load_services()

__all__ = ['get_service', 'get_available_services']

def reload_services():
    """Reload all services (useful for testing) following Service Layer Architecture."""
    global _service_registry, _service_status
    _service_registry = {}
    _service_status = {}
    _load_services()
