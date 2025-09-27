"""
API Response Utilities - AI Nurse Florence
Following API Design Standards from copilot-instructions.md
"""

from typing import Dict, Any, Optional
from fastapi import status

def create_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = status.HTTP_200_OK
) -> Dict[str, Any]:
    """Create standardized success response."""
    response = {
        "success": True,
        "message": message,
        "status_code": status_code
    }
    
    if data is not None:
        response["data"] = data
    
    return response

def create_error_response(
    message: str,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized error response."""
    response = {
        "success": False,
        "error": message,
        "status_code": status_code
    }
    
    if details:
        response["details"] = details
    
    return response
