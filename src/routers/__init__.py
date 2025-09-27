"""
AI Nurse Florence Routers
Following Router Organization pattern from coding instructions
"""

# Router imports following Conditional Imports Pattern
try:
    from .disease import router as disease_router
    _has_disease_router = True
except ImportError:
    _has_disease_router = False
    disease_router = None

try:
    from .literature import router as literature_router
    _has_literature_router = True
except ImportError:
    _has_literature_router = False
    literature_router = None

try:
    from .clinical_trials import router as clinical_trials_router
    _has_clinical_trials_router = True
except ImportError:
    _has_clinical_trials_router = False
    clinical_trials_router = None

# Export available routers
__all__ = [
    'disease_router',
    'literature_router', 
    'clinical_trials_router'
]

def get_available_routers():
    """Get list of available routers following Service Layer Architecture."""
    available = {}
    if _has_disease_router:
        available['disease'] = disease_router
    if _has_literature_router:
        available['literature'] = literature_router
    if _has_clinical_trials_router:
        available['clinical_trials'] = clinical_trials_router
    
    return available
