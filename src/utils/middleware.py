"""
Middleware stack for AI Nurse Florence
Security, logging, and clinical safety middleware
"""

import time
import logging
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import uuid

from .config import get_settings
from .exceptions import ServiceException, create_error_response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers for healthcare compliance"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers for healthcare applications
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy for clinical applications
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # HSTS for production
        settings = get_settings()
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Add unique request ID for tracking"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    """Request/response logging with clinical context"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        # Log request
        logging.info(
            f"Request started: {request.method} {request.url.path} "
            f"[{request_id}] from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful response
            logging.info(
                f"Request completed: {request.method} {request.url.path} "
                f"[{request_id}] {response.status_code} in {duration:.3f}s"
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Log error
            logging.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[{request_id}] {str(e)} in {duration:.3f}s"
            )
            
            # Return structured error response
            if isinstance(e, ServiceException):
                return JSONResponse(
                    status_code=e.status_code,
                    content=create_error_response(e)
                )
            else:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": True,
                        "error_type": "internal_server_error", 
                        "message": "Internal server error",
                        "banner": "Draft for clinician review — not medical advice. No PHI stored.",
                        "request_id": request_id
                    }
                )

class ClinicalSafetyMiddleware(BaseHTTPMiddleware):
    """Add clinical safety headers and validation"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add clinical context to request
        request.state.clinical_context = {
            "is_clinical_endpoint": self._is_clinical_endpoint(request.url.path),
            "requires_disclaimer": True,
            "educational_use_only": True
        }
        
        response = await call_next(request)
        
        # Add clinical safety headers
        response.headers["X-Clinical-Disclaimer"] = "Educational use only - not medical advice"
        response.headers["X-PHI-Policy"] = "No PHI stored or processed"
        
        # Add educational banner to clinical responses
        if hasattr(response, 'body') and response.headers.get("content-type", "").startswith("application/json"):
            try:
                # This is a simplified approach - in practice you'd want more sophisticated JSON manipulation
                pass
            except Exception:
                # Don't break the response if JSON manipulation fails
                pass
        
        return response
    
    def _is_clinical_endpoint(self, path: str) -> bool:
        """Check if endpoint provides clinical information"""
        clinical_patterns = [
            "/clinical-decision",
            "/risk-assessment", 
            "/sbar",
            "/literature",
            "/patient-education",
            "/disease",
            "/medication"
        ]
        return any(pattern in path for pattern in clinical_patterns)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings = get_settings()
        
        # Skip rate limiting if disabled
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_requests(current_time)
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": True,
                    "error_type": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
                    "banner": "Draft for clinician review — not medical advice. No PHI stored."
                }
            )
        
        # Record request
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove requests older than 1 minute"""
        cutoff_time = current_time - 60
        for ip in list(self.request_history.keys()):
            self.request_history[ip] = [
                req_time for req_time in self.request_history[ip]
                if req_time > cutoff_time
            ]
            if not self.request_history[ip]:
                del self.request_history[ip]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit"""
        if client_ip not in self.request_history:
            return False
        
        recent_requests = len(self.request_history[client_ip])
        return recent_requests >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """Record a request from client"""
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        self.request_history[client_ip].append(current_time)

# CORS middleware configuration helper
def get_cors_middleware_config():
    """Get CORS configuration for FastAPI"""
    settings = get_settings()
    
    return {
        "allow_origins": settings.get_cors_origins_list(),
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Authorization",
            "Content-Type", 
            "X-Requested-With",
            "X-Request-ID",
            "Accept",
            "Origin",
            "User-Agent"
        ],
        "expose_headers": [
            "X-Request-ID",
            "X-Clinical-Disclaimer",
            "X-PHI-Policy"
        ]
    }

# Export middleware classes
__all__ = [
    "SecurityHeadersMiddleware",
    "RequestIdMiddleware", 
    "LoggingMiddleware",
    "ClinicalSafetyMiddleware",
    "RateLimitMiddleware",
    "get_cors_middleware_config"
]
