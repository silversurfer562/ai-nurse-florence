"""
Clinical Wizards Router Registry
Following Router Organization pattern from copilot-instructions.md
"""

from typing import Optional, Dict, Any
from fastapi import APIRouter

# Wizard router imports following Conditional Imports Pattern
# Pre-declare variables so mypy knows they exist and can be Optional
sbar_wizard_router: Optional[APIRouter] = None
treatment_plan_router: Optional[APIRouter] = None

try:
    from .sbar_wizard import router as _sbar_router

    sbar_wizard_router = _sbar_router
    _has_sbar_wizard = True
except ImportError:
    _has_sbar_wizard = False

try:
    from .treatment_plan_wizard import router as _treatment_router

    treatment_plan_router = _treatment_router
    _has_treatment_plan = True
except ImportError:
    _has_treatment_plan = False

# Export available wizards
__all__ = ["sbar_wizard_router", "treatment_plan_router"]


def get_available_wizards() -> Dict[str, Any]:
    """Get list of available wizard routers."""
    available = {}
    if _has_sbar_wizard and sbar_wizard_router:
        available["sbar"] = sbar_wizard_router
    if _has_treatment_plan and treatment_plan_router:
        available["treatment_plan"] = treatment_plan_router

    return available
