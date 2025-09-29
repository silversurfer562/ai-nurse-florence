"""
Router Registry - AI Nurse Florence
Following Router Organization and Conditional Imports Pattern from coding instructions
"""

import logging
from typing import Dict
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

    # Monitoring router
    try:
        from .monitoring import router
        _router_registry["monitoring"] = router
        router_status["monitoring"] = True
        logger.info("✅ Monitoring router loaded successfully")
    except (ImportError, AttributeError) as e:
        logger.error(f"❌ Monitoring router import failed: {e}")
        router_status["monitoring"] = False
        # Import traceback for detailed error logging
        import traceback
        logger.error(f"Monitoring router traceback: {traceback.format_exc()}")

    # Auth router  
    try:
        from .auth import router
        _router_registry['auth'] = router
        router_status['auth'] = True
        logger.info("✅ Auth router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Auth router unavailable: {e}")
        router_status['auth'] = False

def _load_medical_routers():
    """Load medical information routers following External Service Integration."""
    
    # Disease router
    try:
        from .disease import router
        _router_registry['disease'] = router
        router_status['disease'] = True
        logger.info("✅ Disease router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Disease router unavailable: {e}")
        router_status['disease'] = False

    # Literature router
    try:
        from .literature import router
        _router_registry['literature'] = router
        router_status['literature'] = True
        logger.info("✅ Literature router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Literature router unavailable: {e}")
        router_status['literature'] = False

    # Clinical trials router
    try:
        from .clinical_trials import router
        _router_registry['clinical_trials'] = router
        router_status['clinical_trials'] = True
        logger.info("✅ Clinical trials router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Clinical trials router unavailable: {e}")
        router_status['clinical_trials'] = False

    # Clinical decision support router
    try:
        from .clinical_decision_support import router
        _router_registry['clinical_decision_support'] = router
        router_status['clinical_decision_support'] = True
        logger.info("✅ Clinical Decision Support router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Clinical Decision Support router unavailable: {e}")
        router_status['clinical_decision_support'] = False

def _load_wizard_routers():
    """Load wizard routers following Wizard Pattern Implementation with Conditional Imports."""
    
    # Wizard routers are optional and loaded dynamically
    wizard_modules = [
        'clinical_assessment',
        'care_plan', 
        'medication_reconciliation',
        'sbar_report',
        'patient_education',
        'quality_improvement'
    ]
    
    for wizard_name in wizard_modules:
        try:
            import importlib
            wizard_module = importlib.import_module(f".wizards.{wizard_name}", package=__package__)
            if hasattr(wizard_module, 'router'):
                _router_registry[f'wizard_{wizard_name}'] = wizard_module.router
                router_status[f'wizard_{wizard_name}'] = True
                logger.info(f"✅ Wizard router loaded: {wizard_name}")
            else:
                logger.warning(f"⚠️ Wizard module {wizard_name} has no router attribute")
                router_status[f'wizard_{wizard_name}'] = False
        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠️ Wizard router unavailable: {wizard_name} - {e}")
            router_status[f'wizard_{wizard_name}'] = False

def _load_optional_routers():
    """Load optional service routers following External Service Integration."""
    
    # Chat/conversation router
    try:
        from .conversation import router
        _router_registry['conversation'] = router
        router_status['conversation'] = True
        logger.info("✅ Conversation router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Conversation router unavailable: {e}")
        router_status['conversation'] = False

    # User management router
    try:
        from .users import router
        _router_registry['users'] = router
        router_status['users'] = True
        logger.info("✅ Users router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Users router unavailable: {e}")
        router_status['users'] = False

    # Med check router
    try:
        from .med_check import router
        _router_registry['med_check'] = router
        router_status['med_check'] = True
        logger.info("✅ Med check router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Med check router unavailable: {e}")
        router_status['med_check'] = False

    # Educational router
    try:
        from .educational import router
        _router_registry['educational'] = router
        router_status['educational'] = True
        logger.info("✅ Educational router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Educational router unavailable: {e}")
        router_status['educational'] = False

def _load_routers():
    """Load all routers following Service Layer Architecture patterns."""
    logger.info("🔄 Loading routers with conditional imports...")
    
    # Load in order: core -> medical -> wizards -> optional
    _load_core_routers()
    _load_medical_routers()
    _load_wizard_routers()
    _load_optional_routers()
    
    loaded_count = sum(1 for status in router_status.values() if status)
    total_attempted = len(router_status)
    
    logger.info(f"✅ Router loading complete: {loaded_count}/{total_attempted} routers loaded")
    
    if loaded_count == 0:
        logger.error("❌ No routers loaded! Check dependencies and router implementations.")
    elif loaded_count < total_attempted:
        failed_routers = [name for name, status in router_status.items() if not status]
        logger.warning(f"⚠️ Some routers failed to load: {failed_routers}")

# Initialize router loading
try:
    _load_routers()
except Exception as e:
    logger.error(f"Initial router loading failed: {e}")
    # Continue execution with whatever routers loaded

def get_router(name: str) -> APIRouter:
    """Get a router by name from the registry."""
    if name not in _router_registry:
        logger.warning(f"Router '{name}' not found in registry")
        # Return empty router to prevent crashes
        return APIRouter()
    return _router_registry[name]

def get_available_routers():
    """Get list of successfully loaded routers."""
    return {name: router for name, router in _router_registry.items() 
            if router_status.get(name, False)}

def get_router_status():
    """Get status of all attempted router loads."""
    return router_status.copy()

# Export for app.py to register with main FastAPI app
available_routers = get_available_routers()
