"""
AI Nurse Florence Routers Registry
Following Router Organization pattern with Conditional Imports
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Router registry following Router Organization pattern
_router_registry = {}

def _load_routers():
    """Load available routers following Conditional Imports Pattern."""
    global _router_registry
    
    # Health router (unprotected)
    try:
        from .health import router as health_router
        _router_registry['health'] = health_router
        logger.info("Health router registered")
    except ImportError as e:
        logger.warning(f"Health router unavailable: {e}")
    
    # Auth router (unprotected) 
    try:
        from .auth import router as auth_router
        _router_registry['auth'] = auth_router
        logger.info("Auth router registered")
    except ImportError as e:
        logger.warning(f"Auth router unavailable: {e}")
    
    # Disease router (protected)
    try:
        from .disease import router as disease_router
        _router_registry['disease'] = disease_router
        logger.info("Disease router registered")
    except ImportError as e:
        logger.warning(f"Disease router unavailable: {e}")
    
    # Literature router (protected)
    try:
        from .literature import router as literature_router
        _router_registry['literature'] = literature_router
        logger.info("Literature router registered")
    except ImportError as e:
        logger.warning(f"Literature router unavailable: {e}")
    
    # Clinical trials router (protected)
    try:
        from .clinical_trials import router as clinical_trials_router
        _router_registry['clinical_trials'] = clinical_trials_router
        logger.info("Clinical trials router registered")
    except ImportError as e:
        logger.warning(f"Clinical trials router unavailable: {e}")
    
    # Wizard routers (protected) - following Wizard Pattern Implementation
    wizard_routers = [
        ('nursing_assessment', 'wizards.nursing_assessment'),
        ('sbar_report', 'wizards.sbar_report'),
        ('medication_reconciliation', 'wizards.medication_reconciliation'),
        ('care_plan', 'wizards.care_plan'),
        ('discharge_planning', 'wizards.discharge_planning')
    ]
    
    for wizard_name, wizard_module in wizard_routers:
        try:
            module = __import__(f'src.routers.{wizard_module}', fromlist=['router'])
            _router_registry[wizard_name] = module.router
            logger.info(f"Wizard router registered: {wizard_name}")
        except ImportError as e:
            logger.warning(f"Wizard router unavailable ({wizard_name}): {e}")

def get_available_routers() -> Dict[str, APIRouter]:
    """
    Get available routers following Conditional Imports Pattern.
    Returns only successfully loaded routers.
    """
    if not _router_registry:
        _load_routers()
    
    return _router_registry.copy()

def get_router_status() -> Dict[str, bool]:
    """Get status of all routers for health checks."""
    if not _router_registry:
        _load_routers()
    
    expected_routers = [
        'health', 'auth', 'disease', 'literature', 'clinical_trials',
        'nursing_assessment', 'sbar_report', 'medication_reconciliation',
        'care_plan', 'discharge_planning'
    ]
    
    return {
        router_name: router_name in _router_registry
        for router_name in expected_routers
    }

# Initialize routers on module import
_load_routers()

__all__ = [
    'get_available_routers',
    'get_router_status'
]
