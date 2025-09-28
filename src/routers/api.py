"""
Enhanced API Router - Main API endpoints
Following Router Organization patterns
"""

from fastapi import APIRouter
import importlib
from types import ModuleType
from typing import Optional

# Load routers using importlib to make optional modules explicit to static checkers
try:
    clinical_decision_support: Optional[ModuleType] = importlib.import_module(
        "routers.clinical_decision_support"
    )
except Exception:
    clinical_decision_support = None

try:
    wizards_module: Optional[ModuleType] = importlib.import_module("routers.wizards")
    treatment_plan = getattr(wizards_module, "treatment_plan", None) if wizards_module else None
    sbar_report = getattr(wizards_module, "sbar_report", None) if wizards_module else None
except Exception:
    treatment_plan = None
    sbar_report = None

# Conditional imports for enhanced features
try:
    chatgpt_store: Optional[ModuleType] = importlib.import_module("routers.chatgpt_store")
    _has_gpt_store = True if chatgpt_store is not None else False
except Exception:
    chatgpt_store = None
    _has_gpt_store = False

# Create main API router following router organization pattern
api_router = APIRouter(prefix="/api/v1")

# Include core clinical routers
if clinical_decision_support is not None and hasattr(clinical_decision_support, "router"):
    api_router.include_router(clinical_decision_support.router)

# Include wizard workflows following wizard pattern implementation
if treatment_plan is not None and hasattr(treatment_plan, "router"):
    api_router.include_router(treatment_plan.router)

if sbar_report is not None and hasattr(sbar_report, "router"):
    api_router.include_router(sbar_report.router)

# Conditional ChatGPT Store integration
if _has_gpt_store and chatgpt_store is not None and hasattr(chatgpt_store, "router"):
    api_router.include_router(chatgpt_store.router)

# TODO: Add additional router inclusions
# TODO: Implement rate limiting configuration
# TODO: Add middleware for clinical workflows
