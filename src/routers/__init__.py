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

        _router_registry["health"] = router
        router_status["health"] = True
        logger.info("✅ Health router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Health router unavailable: {e}")
        router_status["health"] = False

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

        _router_registry["auth"] = router
        router_status["auth"] = True
        logger.info("✅ Enhanced Auth router loaded successfully")
        logger.info(f"Auth router endpoints: {len(router.routes)}")
    except (ImportError, AttributeError) as e:
        logger.error(f"❌ Enhanced Auth router import failed: {e}")
        router_status["auth"] = False
        # Import traceback for detailed error logging
        import traceback

        logger.error(f"Enhanced Auth router traceback: {traceback.format_exc()}")

    # Session monitoring router (Phase 3.4.4)
    try:
        from .session_monitoring import router

        _router_registry["session_monitoring"] = router
        router_status["session_monitoring"] = True
        logger.info("✅ Session monitoring router loaded successfully")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Session monitoring router unavailable: {e}")
        router_status["session_monitoring"] = False

    # Epic Integration Wizard router (LangChain-powered)
    try:
        from .epic_wizard import router

        _router_registry["epic_wizard"] = router
        router_status["epic_wizard"] = True
        logger.info("✅ Epic Integration Wizard router loaded successfully")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Epic Integration Wizard router unavailable: {e}")
        logger.warning("   Requires: langchain, langgraph dependencies")
        router_status["epic_wizard"] = False


def _load_medical_routers():
    """Load medical information routers following External Service Integration."""

    # Disease router
    try:
        from .disease import router

        _router_registry["disease"] = router
        router_status["disease"] = True
        logger.info("✅ Disease router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Disease router unavailable: {e}")
        router_status["disease"] = False

    # Literature router
    try:
        from .literature import router

        _router_registry["literature"] = router
        router_status["literature"] = True
        logger.info("✅ Literature router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Literature router unavailable: {e}")
        router_status["literature"] = False

    # Clinical trials router
    try:
        from .clinical_trials import router

        _router_registry["clinical_trials"] = router
        router_status["clinical_trials"] = True
        logger.info("✅ Clinical trials router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Clinical trials router unavailable: {e}")
        router_status["clinical_trials"] = False

    # Clinical decision support router
    try:
        from .clinical_decision_support import router

        _router_registry["clinical_decision_support"] = router
        router_status["clinical_decision_support"] = True
        logger.info("✅ Clinical Decision Support router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Clinical Decision Support router unavailable: {e}")
        router_status["clinical_decision_support"] = False

    # Chat router
    try:
        from .chat import router

        _router_registry["chat"] = router
        router_status["chat"] = True
        logger.info("✅ Chat router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Chat router unavailable: {e}")
        router_status["chat"] = False


def _load_wizard_routers():
    """Load wizard routers following Wizard Pattern Implementation with Conditional Imports."""

    # Wizard routers are optional and loaded dynamically
    wizard_modules = [
        "clinical_assessment",
        "care_plan",
        "medication_reconciliation",
        "sbar_report",
        "shift_handoff_wizard",
        "soap_note_wizard",
        "admission_assessment_wizard",
        "discharge_summary_wizard",
        "incident_report_wizard",
        "patient_education",
        "quality_improvement",
        "dosage_calculation",
    ]

    for wizard_name in wizard_modules:
        try:
            import importlib

            wizard_module = importlib.import_module(
                f".wizards.{wizard_name}", package=__package__
            )
            if hasattr(wizard_module, "router"):
                _router_registry[f"wizard_{wizard_name}"] = wizard_module.router
                router_status[f"wizard_{wizard_name}"] = True
                logger.info(f"✅ Wizard router loaded: {wizard_name}")
            else:
                logger.warning(f"⚠️ Wizard module {wizard_name} has no router attribute")
                router_status[f"wizard_{wizard_name}"] = False
        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠️ Wizard router unavailable: {wizard_name} - {e}")
            router_status[f"wizard_{wizard_name}"] = False


def _load_optional_routers():
    """Load optional service routers following External Service Integration."""

    # NOTE: conversation, users, med_check, and educational routers
    # are not yet implemented - removed from loader to reduce log noise
    # TODO: Implement these routers when needed:
    #   - conversation.py: Chat/conversation history
    #   - users.py: User management
    #   - med_check.py: Medication checking
    #   - educational.py: Educational content management

    pass  # No optional routers currently implemented


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

    logger.info(
        f"✅ Router loading complete: {loaded_count}/{total_attempted} routers loaded"
    )

    if loaded_count == 0:
        logger.error(
            "❌ No routers loaded! Check dependencies and router implementations."
        )
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
    return {
        name: router
        for name, router in _router_registry.items()
        if router_status.get(name, False)
    }


def get_router_status():
    """Get status of all attempted router loads."""
    return router_status.copy()


def load_routers():
    """Load and combine all routers into a single APIRouter for app.py."""
    main_router = APIRouter(prefix="/api/v1")

    # Include all successfully loaded routers
    for name, router in _router_registry.items():
        if router_status.get(name, False):
            main_router.include_router(router)
            logger.debug(f"Including router: {name}")

    # Attach status for app.py to access
    load_routers.routers_loaded = router_status

    return main_router


# Export for app.py to register with main FastAPI app
available_routers = get_available_routers()
