"""
API response utilities for AI Nurse Florence
Standardized response patterns with educational banners
"""

from typing import Any, Dict, Optional, List
from fastapi.responses import JSONResponse
from .config import get_educational_banner

def create_success_response(
    data: Any,
    message: str = "Success",
    educational_banner: Optional[str] = None,
    evidence_level: Optional[str] = None,
    clinical_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized success response with educational content
    Following AI Nurse Florence response pattern
    """
    
    response = {
        "success": True,
        "message": message,
        "data": data,
        "banner": educational_banner or get_educational_banner()
    }
    
    # Add clinical metadata if provided
    if evidence_level:
        response["evidence_level"] = evidence_level
    
    if clinical_context:
        response["clinical_context"] = clinical_context
    
    # Add timestamp for clinical documentation
    from datetime import datetime
    response["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    return response

def create_error_response(
    message: str,
    error_type: str = "service_error",
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 500
) -> JSONResponse:
    """
    Create standardized error response
    Following AI Nurse Florence error handling pattern
    """
    
    response_data = {
        "success": False,
        "error": True,
        "error_type": error_type,
        "message": message,
        "details": details or {},
        "banner": get_educational_banner(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_data
    )

def create_clinical_response(
    data: Any,
    nursing_interventions: Optional[str] = None,
    evidence_level: str = "Level IV - Expert Opinion",
    safety_considerations: Optional[List[str]] = None,
    educational_banner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create clinical decision support response
    Following AI Nurse Florence clinical pattern
    """
    
    from datetime import datetime
    
    response = {
        "success": True,
        "data": data,
        "nursing_interventions": nursing_interventions,
        "evidence_level": evidence_level,
        "banner": educational_banner or "🏥 CLINICAL GUIDANCE: Educational use only - not medical advice. Clinical judgment required.",
        "safety_considerations": safety_considerations or [
            "Verify patient allergies and contraindications",
            "Consider individual patient factors",
            "Follow institutional protocols",
            "Document all interventions appropriately"
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "clinical_disclaimer": "This information is for educational purposes only and should not replace clinical judgment or institutional protocols."
    }
    
    return response

def create_paginated_response(
    items: List[Any],
    total: int,
    page: int = 1,
    size: int = 10,
    educational_banner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create paginated response with clinical context
    Following AI Nurse Florence pagination pattern
    """
    
    response = {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "size": size,
                "pages": (total + size - 1) // size,  # Ceiling division
                "has_next": page * size < total,
                "has_prev": page > 1
            }
        },
        "banner": educational_banner or get_educational_banner(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return response

def create_wizard_response(
    step: str,
    data: Any,
    next_step: Optional[str] = None,
    progress: Optional[Dict[str, Any]] = None,
    educational_banner: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create wizard workflow response
    Following AI Nurse Florence wizard pattern
    """
    
    response = {
        "success": True,
        "wizard": {
            "current_step": step,
            "next_step": next_step,
            "progress": progress or {}
        },
        "data": data,
        "banner": educational_banner or get_educational_banner(),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    return response

# Conditional import for datetime if not available
try:
    from datetime import datetime
except ImportError:
    # Fallback for datetime
    import time
    
    class datetime:
        @staticmethod
        def utcnow():
            class MockDateTime:
                def isoformat(self):
                    return time.strftime("%Y-%m-%dT%H:%M:%S")
            return MockDateTime()
