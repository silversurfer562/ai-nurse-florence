"""
Custom exceptions for AI Nurse Florence
Standardized error handling following Service Layer Architecture
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException
from enum import Enum

class ErrorType(str, Enum):
    """Standard error types for clinical application"""
    VALIDATION_ERROR = "validation_error"
    SERVICE_ERROR = "service_error"
    EXTERNAL_API_ERROR = "external_api_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    CLINICAL_SAFETY_ERROR = "clinical_safety_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    CONFIGURATION_ERROR = "configuration_error"

class ServiceException(Exception):
    """
    Base exception for all service layer errors
    Follows standardized error response pattern
    """
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType = ErrorType.SERVICE_ERROR,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to standardized response format"""
        return {
            "error": True,
            "error_type": self.error_type.value,
            "message": self.message,
            "details": self.details,
            "educational_banner": self._get_educational_banner()
        }
    
    def _get_educational_banner(self) -> str:
        """Get educational banner for clinical safety"""
        if self.error_type == ErrorType.CLINICAL_SAFETY_ERROR:
            return "🏥 CLINICAL SAFETY: This system provides educational guidance only - not medical advice. Clinical judgment required."
        return "🏥 EDUCATIONAL: Draft for clinician review — not medical advice. No PHI stored."

class ExternalServiceException(ServiceException):
    """Exception for external API failures with fallback handling"""
    
    def __init__(self, service_name: str, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=f"{service_name} service error: {message}",
            error_type=ErrorType.EXTERNAL_API_ERROR,
            details={
                "service": service_name,
                "original_error": str(original_error) if original_error else None,
                "fallback_available": True
            },
            status_code=503
        )

class ValidationException(ServiceException):
    """Exception for input validation errors"""
    
    def __init__(self, field: str, value: Any, reason: str):
        super().__init__(
            message=f"Validation error for {field}: {reason}",
            error_type=ErrorType.VALIDATION_ERROR,
            details={
                "field": field,
                "value": str(value),
                "reason": reason
            },
            status_code=422
        )

class ClinicalSafetyException(ServiceException):
    """Exception for clinical safety violations"""
    
    def __init__(self, message: str, safety_rule: str):
        super().__init__(
            message=f"Clinical safety violation: {message}",
            error_type=ErrorType.CLINICAL_SAFETY_ERROR,
            details={
                "safety_rule": safety_rule,
                "recommendation": "Review clinical protocols and consult healthcare professional"
            },
            status_code=400
        )

# Global exception handler helper
def create_error_response(exception: ServiceException) -> Dict[str, Any]:
    """Create standardized error response from ServiceException"""
    return {
        "success": False,
        "data": None,
        **exception.to_dict()
    }

# HTTP Exception helpers for FastAPI
def raise_validation_error(field: str, value: Any, reason: str):
    """Raise HTTP validation error"""
    exc = ValidationException(field, value, reason)
    raise HTTPException(status_code=exc.status_code, detail=exc.to_dict())

def raise_service_error(message: str, status_code: int = 500):
    """Raise HTTP service error"""
    exc = ServiceException(message, status_code=status_code)
    raise HTTPException(status_code=exc.status_code, detail=exc.to_dict())

def raise_external_service_error(service_name: str, message: str):
    """Raise HTTP external service error"""
    exc = ExternalServiceException(service_name, message)
    raise HTTPException(status_code=exc.status_code, detail=exc.to_dict())
