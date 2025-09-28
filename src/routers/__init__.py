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

    # Auth router
    try:
        from .auth import router

        _router_registry["auth"] = router
        router_status["auth"] = True
        logger.info("✅ Auth router loaded")
    except (ImportError, AttributeError) as e:
        logger.warning(f"⚠️ Auth router unavailable: {e}")
        router_status["auth"] = False


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


def _load_wizard_routers():
    """Load wizard routers following Wizard Pattern Implementation with Conditional Imports."""

    wizard_routers = {
        "nursing_assessment": "src.routers.wizards.nursing_assessment",
        "treatment_plan": "src.routers.wizards.treatment_plan",
        "sbar_report": "src.routers.wizards.sbar_report",
        "medication_reconciliation": "src.routers.wizards.medication_reconciliation",
        "care_plan": "src.routers.wizards.care_plan",
        "discharge_planning": "src.routers.wizards.discharge_planning",
    }

    for wizard_name, module_path in wizard_routers.items():
        try:
            import importlib

            module = importlib.import_module(module_path)

            if hasattr(module, "router"):
                _router_registry[wizard_name] = module.router
                router_status[wizard_name] = True
                logger.info(f"✅ Wizard router loaded: {wizard_name}")
            else:
                logger.warning(
                    f"⚠️ Wizard module {wizard_name} missing 'router' attribute"
                )
                router_status[wizard_name] = False

        except (ImportError, AttributeError) as e:
            logger.warning(f"⚠️ Wizard router unavailable: {wizard_name} - {e}")
            router_status[wizard_name] = False


def _load_routers():
    """
    Load all routers with graceful degradation following Conditional Imports Pattern.
    Critical pattern: Services fail gracefully when optional dependencies missing.
    """
    logger.info("Loading routers following Router Organization pattern...")

    try:
        _load_core_routers()
        _load_medical_routers()
        _load_wizard_routers()

        loaded_count = sum(router_status.values())
        total_count = len(router_status)

        logger.info(
            f"Router loading complete: {loaded_count}/{total_count} routers available"
        )

    except Exception as e:
        logger.error(f"Router loading failed with unexpected error: {e}")
        # Ensure router_status is always populated even on failure
        if not router_status:
            router_status.update(
                {
                    "health": False,
                    "auth": False,
                    "disease": False,
                    "literature": False,
                    "clinical_trials": False,
                    "clinical_decision_support": False,
                    "nursing_assessment": False,
                    "sbar_report": False,
                    "medication_reconciliation": False,
                    "care_plan": False,
                    "discharge_planning": False,
                }
            )


def get_available_routers() -> Dict[str, APIRouter]:
    """Get dictionary of available routers following Conditional Imports Pattern."""
    # Return a canonical mapping of router name -> APIRouter with duplicates removed.
    # Some modules may expose the same APIRouter object under multiple keys; callers
    # expect a single canonical router object per logical route collection. We prefer
    # the first-seen name when duplicates are detected and log a warning.
    canonical: Dict[str, APIRouter] = {}
    seen_router_ids: Dict[int, str] = {}

    for name, router in _router_registry.items():
        if router is None:
            continue
        rid = id(router)
        if rid in seen_router_ids:
            prev_name = seen_router_ids[rid]
            logger.warning(
                f"Duplicate router object detected: '{name}' is the same router as '{prev_name}'; skipping alias '{name}'."
            )
            # skip alias to avoid duplicate registration
            continue
        canonical[name] = router
        seen_router_ids[rid] = name

    return canonical


def get_router_status() -> Dict[str, bool]:
    """Get router availability status following Router Organization pattern."""
    return router_status.copy()


def reload_routers():
    """Reload all routers (useful for testing) following Service Layer Architecture."""
    global _router_registry, router_status
    _router_registry.clear()
    router_status.clear()
    _load_routers()


# Initialize routers on module import with graceful degradation
try:
    _load_routers()
except Exception as e:
    logger.error(f"Initial router loading failed: {e}")
    # Ensure basic structure exists even on complete failure
    router_status = {
        "health": False,
        "auth": False,
        "disease": False,
        "literature": False,
        "clinical_trials": False,
        "clinical_decision_support": False,
        "nursing_assessment": False,
        "sbar_report": False,
        "medication_reconciliation": False,
        "care_plan": False,
        "discharge_planning": False,
    }

# Export a canonical mapping at import time, but prefer callers to call get_available_routers()
available_routers = get_available_routers()
__all__ = [
    "available_routers",
    "router_status",
    "get_available_routers",
    "get_router_status",
    "reload_routers",
]
