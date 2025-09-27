"""
Router Registry - AI Nurse Florence
Following Router Organization and Conditional Imports Pattern from coding instructions
"""

import logging
from typing import Dict, Optional
from fastapi import APIRouter

logger = logging.getLogger(__name__)

# Router registry with conditional imports following Conditional Imports Pattern
_router_registry: Dict[str, APIRouter] = {}
router_status: Dict[str, bool] = {}

def _load_core_routers():
    """Load core routers following Conditional Imports Pattern."""
    
    # Health router
    try:
        from .health import router
        _router_registry['health'] = router
        router_status['health'] = True
        logger.info("✅ Health router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Health router unavailable: {e}")
        router_status['health'] = False

    # Auth router  
    try:
        from .auth import router
        _router_registry['auth'] = router
        router_status['auth'] = True
        logger.info("✅ Auth router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Auth router unavailable: {e}")
        router_status['auth'] = False

def _load_wizard_routers():
    """Load wizard routers following Wizard Pattern Implementation with Conditional Imports."""
    
    wizard_routers = {
        'nursing_assessment': 'src.routers.wizards.nursing_assessment',
        'sbar_report': 'src.routers.wizards.sbar_report', 
        'medication_reconciliation': 'src.routers.wizards.medication_reconciliation',
        'care_plan': 'src.routers.wizards.care_plan',
        'discharge_planning': 'src.routers.wizards.discharge_planning'
    }
    
    for wizard_name, module_path in wizard_routers.items():
        try:
            import importlib
            module = importlib.import_module(module_path)
            
            if hasattr(module, 'router'):
                _router_registry[wizard_name] = module.router
                router_status[wizard_name] = True
                logger.info(f"✅ Wizard router loaded: {wizard_name}")
            else:
                logger.warning(f"⚠️ Wizard module {wizard_name} missing 'router' attribute")
                router_status[wizard_name] = False
                
        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠️ Wizard router unavailable: {wizard_name} - {e}")
            router_status[wizard_name] = False

# Initialize routers on module import with graceful degradation
try:
    _load_core_routers()
    _load_wizard_routers()
except Exception as e:
    logger.error(f"Initial router loading failed: {e}")

# Export following Router Organization pattern
available_routers = _router_registry
__all__ = ['available_routers', 'router_status']

def get_available_routers() -> Dict[str, APIRouter]:
    """Get dictionary of available routers following Conditional Imports Pattern."""
    return _router_registry.copy()

def get_router_status() -> Dict[str, bool]:
    """Get router availability status following Router Organization pattern."""
    return router_status.copy()

def reload_routers():
    """Reload all routers (useful for testing) following Service Layer Architecture."""
    global _router_registry, router_status
    _router_registry.clear()
    router_status.clear()
    _load_routers()
