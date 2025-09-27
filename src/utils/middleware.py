"""
Middleware components for AI Nurse Florence
Following middleware stack order from coding instructions
"""

import uuid
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware following coding instructions.
    First in middleware stack - CSP, HSTS headers.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers for healthcare applications
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS for production
        if request.url.hostname not in ["localhost", "127.0.0.1"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP for healthcare application
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Request ID middleware following coding instructions.
    Second in middleware stack - UUID generation for tracing.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate UUID for request tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Structured logging middleware following coding instructions.
    Third in middleware stack - request/response logging.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get request ID from previous middleware
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 4),
                    "path": request.url.path
                }
            )
            
            # Add process time header
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": round(process_time, 4),
                    "path": request.url.path
                },
                exc_info=True
            )
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "message": "An error occurred processing your request"
                }
            )

# Export middleware classes following coding instructions
__all__ = [
    'SecurityHeadersMiddleware',
    'RequestIdMiddleware', 
    'LoggingMiddleware'
    # RateLimiter is exported from rate_limit.py
]
