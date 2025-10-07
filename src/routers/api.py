"""
Enhanced API Router - Main API endpoints
Following Router Organization patterns
"""

from fastapi import APIRouter

from src.routers import clinical_decision_support
from src.routers.wizards import sbar_report, sbar_wizard_router, treatment_plan

# Conditional imports for enhanced features
try:
    from src.routers import chatgpt_store

    _has_gpt_store = True
except ImportError:
    _has_gpt_store = False

# Create main API router following router organization pattern
api_router = APIRouter(prefix="/api/v1")

# Include core clinical routers
api_router.include_router(clinical_decision_support.router)

# Include wizard workflows following wizard pattern implementation
api_router.include_router(treatment_plan.router)
api_router.include_router(sbar_report.router)
api_router.include_router(sbar_wizard_router)

# Conditional ChatGPT Store integration
if _has_gpt_store:
    api_router.include_router(chatgpt_store.router)

# TODO: Add additional router inclusions
# TODO: Implement rate limiting configuration
# TODO: Add middleware for clinical workflows
