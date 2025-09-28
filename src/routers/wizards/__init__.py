"""
Clinical Wizards Router Registry
Following Router Organization pattern from copilot-instructions.md
"""

# Wizard router imports following Conditional Imports Pattern
try:
    from .sbar_wizard import router as sbar_wizard_router

    _has_sbar_wizard = True
except ImportError:
    _has_sbar_wizard = False
    sbar_wizard_router = None

try:
    from .treatment_plan_wizard import router as treatment_plan_router

    _has_treatment_plan = True
except ImportError:
    _has_treatment_plan = False
    treatment_plan_router = None

# Export available wizards
__all__ = ["sbar_wizard_router", "treatment_plan_router"]


def get_available_wizards():
    """Get list of available wizard routers."""
    available = {}
    if _has_sbar_wizard and sbar_wizard_router:
        available["sbar"] = sbar_wizard_router
    if _has_treatment_plan and treatment_plan_router:
        available["treatment_plan"] = treatment_plan_router

    return available
