"""
Exception handlers for the FastAPI application.

This module provides exception handlers that can be registered with a FastAPI app
to handle custom exceptions in a standardized way.
"""
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

from utils.exceptions import ServiceException, ValidationException, ExternalServiceException, NotFoundException
from utils.logging import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register exception handlers with a FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException) -> JSONResponse:
        """Handle all service exceptions."""
        # Log the exception
        logger.error(
            f"Service exception: {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "service": exc.service_name,
                "status_code": exc.status_code,
                "details": exc.details
            },
            exc_info=True
        )
        
        # Return a standardized response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "service": exc.service_name,
                    "type": exc.__class__.__name__,
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    **(exc.details if exc.details else {})
                }
            }
        )
    
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
        """Handle validation exceptions specifically."""
        # Log the exception
        logger.warning(
            f"Validation exception: {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "service": exc.service_name,
                "details": exc.details
            }
        )
        
        # Return a standardized response
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "message": exc.message,
                    "service": exc.service_name,
                    "type": "ValidationError",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    **(exc.details if exc.details else {})
                }
            }
        )
    
    @app.exception_handler(ExternalServiceException)
    async def external_service_exception_handler(request: Request, exc: ExternalServiceException) -> JSONResponse:
        """Handle external service exceptions specifically."""
        # Log the exception
        logger.error(
            f"External service exception: {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "service": exc.service_name,
                "details": exc.details
            },
            exc_info=True
        )
        
        # Return a standardized response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "service": exc.service_name,
                    "type": "ExternalServiceError",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    **(exc.details if exc.details else {})
                }
            }
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
        """Handle not found exceptions specifically."""
        # Log the exception
        logger.info(
            f"Resource not found: {exc.message}",
            extra={
                "request_id": getattr(request.state, "request_id", "unknown"),
                "service": exc.service_name,
                "resource_type": exc.details.get("resource_type"),
                "resource_id": exc.details.get("resource_id")
            }
        )
        
        # Return a standardized response
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "message": exc.message,
                    "service": exc.service_name,
                    "type": "NotFoundError",
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    **(exc.details if exc.details else {})
                }
            }
        )