"""
Custom exceptions for the API.

This module defines a hierarchy of exceptions that can be raised by services
and handled consistently throughout the application.
"""
from typing import Optional, Dict, Any


class ServiceException(Exception):
    """Base exception for all service errors."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str, 
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.service_name = service_name
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ExternalServiceException(ServiceException):
    """Exception for when external service calls fail."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str, 
        status_code: int = 503,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, service_name, status_code, details)


class ValidationException(ServiceException):
    """Exception for data validation errors."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, service_name, status_code=400, details=details)


class AuthenticationException(ServiceException):
    """Exception for authentication errors."""
    
    def __init__(
        self, 
        message: str = "Authentication failed",
        service_name: str = "auth",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, service_name, status_code=401, details=details)


class NotFoundException(ServiceException):
    """Exception for when a resource is not found."""
    
    def __init__(
        self, 
        message: str, 
        service_name: str,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        if details is None:
            details = {}
        details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        super().__init__(message, service_name, status_code=404, details=details)