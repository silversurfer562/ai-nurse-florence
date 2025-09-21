"""
Security-related utilities and middleware.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    A middleware to add security-related HTTP headers to every response.

    These headers help protect the application against common web vulnerabilities.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Instructs browsers to always use HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevents MIME-sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevents the page from being displayed in a frame (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"
        
        # A basic Content Security Policy (CSP) to restrict resource loading
        # This is a restrictive policy; it may need to be adjusted if you add a front-end
        # that loads resources from other domains (e.g., fonts, scripts).
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'"
        
        return response
