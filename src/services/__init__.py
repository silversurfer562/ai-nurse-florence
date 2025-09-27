"""
AI Nurse Florence Services Registry
Following Service Layer Architecture with Conditional Imports Pattern
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .base_service import BaseService

logger = logging.getLogger(__name__)

# Service registry following Service Layer Architecture
_service_registry: Dict[str, 'BaseService'] = {}
_registry_initialized = False

def _initialize_services() -> None:
    """Initialize available services with graceful degradation."""
    global _registry_initialized, _service_registry
    
    if _registry_initialized:
        return
    
    # Disease service
    try:
        from .disease_service import create_disease_service
        disease_service = create_disease_service()
        if disease_service:
            _service_registry['disease'] = disease_service
            logger.info("Disease service registered successfully")
    except ImportError as e:
        logger.warning(f"Disease service unavailable: {e}")
    
    # PubMed service
    try:
        from .pubmed_service import create_pubmed_service
        pubmed_service = create_pubmed_service()
        if pubmed_service:
            _service_registry['pubmed'] = pubmed_service
            logger.info("PubMed service registered successfully")
    except ImportError as e:
        logger.warning(f"PubMed service unavailable: {e}")
    
    # Clinical trials service
    try:
        from .clinical_trials_service import create_clinical_trials_service
        trials_service = create_clinical_trials_service()
        if trials_service:
            _service_registry['clinical_trials'] = trials_service
            logger.info("Clinical trials service registered successfully")
    except ImportError as e:
        logger.warning(f"Clinical trials service unavailable: {e}")
    
    # SBAR service (ADD THIS SECTION)
    try:
        from .sbar_service import create_sbar_service
        sbar_service = create_sbar_service()
        if sbar_service:
            _service_registry['sbar'] = sbar_service
            logger.info("SBAR service registered successfully")
    except ImportError as e:
        logger.warning(f"SBAR service unavailable: {e}")
    
    # OpenAI service (conditional)
    try:
        from .openai_client import create_openai_service
        openai_service = create_openai_service()
        if openai_service and openai_service.is_available():
            _service_registry['openai'] = openai_service
            logger.info("OpenAI service registered successfully")
        else:
            logger.info("OpenAI service available but not configured (missing API key)")
    except ImportError as e:
        logger.warning(f"OpenAI service unavailable: {e}")
    
    _registry_initialized = True

def get_service(service_name: str) -> Optional['BaseService']:
    """
    Get service from registry following Service Layer Architecture.
    Returns None if service not available (Conditional Imports Pattern).
    """
    if not _registry_initialized:
        _initialize_services()
    
    return _service_registry.get(service_name)

def get_available_services() -> Dict[str, bool]:
    """Get status of all services for health checks."""
    if not _registry_initialized:
        _initialize_services()
    
    return {
        'disease': 'disease' in _service_registry,
        'pubmed': 'pubmed' in _service_registry,
        'clinical_trials': 'clinical_trials' in _service_registry,
        'sbar': 'sbar' in _service_registry,  # ADD THIS LINE
        'openai': 'openai' in _service_registry
    }

def register_service(name: str, service: 'BaseService') -> None:
    """Register a service in the registry."""
    global _service_registry
    _service_registry[name] = service
    logger.info(f"Service '{name}' registered successfully")

def clear_registry() -> None:
    """Clear service registry - primarily for testing."""
    global _service_registry, _registry_initialized
    _service_registry.clear()
    _registry_initialized = False

__all__ = [
    'get_service',
    'get_available_services', 
    'register_service',
    'clear_registry'
]
