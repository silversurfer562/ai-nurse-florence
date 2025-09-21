"""
Standardized API response formatters.

This module provides helper functions to create consistent success and error
responses across the application, making the API more predictable for clients.
"""
from fastapi.responses import JSONResponse
from fastapi import status
from typing import Any, Dict, Optional

def create_success_response(
    data: Any, 
    status_code: int = status.HTTP_200_OK,
    links: Optional[Dict[str, str]] = None
) -> JSONResponse:
    """
    Creates a standardized success response.
    
    Args:
        data: The payload to include in the response.
        status_code: The HTTP status code.
        links: Optional dictionary of links related to the resource.
        
    Returns:
        A JSONResponse with a standardized success format.
    """
    content = {
        "status": "success",
        "data": data
    }
    if links:
        content["_links"] = links

    return JSONResponse(
        status_code=status_code,
        content=content
    )

def create_error_response(
    message: str,
    status_code: int,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Creates a standardized error response.
    
    Args:
        message: The error message.
        status_code: The HTTP status code.
        code: An optional application-specific error code.
        details: Optional dictionary with more error details.
        
    Returns:
        A JSONResponse with a standardized error format.
    """
    error_content = {
        "message": message
    }
    if code:
        error_content["code"] = code
    if details:
        error_content["details"] = details
        
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": error_content
        }
    )