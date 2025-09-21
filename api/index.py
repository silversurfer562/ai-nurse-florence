"""Vercel serverless function for AI Nurse Florence FastAPI app.
Following conditional imports pattern from coding instructions.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path following conftest.py pattern
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Educational banner following your API design standards
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

# Conditional imports pattern - graceful degradation
_has_main_app = False
_import_error = "Not attempted"

try:
    from app import app
    # Test if main app has routes and middleware stack
    if hasattr(app, 'routes') and len(app.routes) > 2:
        _has_main_app = True
        handler = app
    else:
        _has_main_app = False
        _import_error = "Main app has no routes"
        raise ImportError("Main app has no routes")
except Exception as e:
    _has_main_app = False
    _import_error = str(e)
    
    # Fallback app following service layer architecture
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    fallback_app = FastAPI(
        title="AI Nurse Florence",
        description="Educational healthcare AI assistant",
        version="1.0.0",
        docs_url="/docs",
        openapi_url="/openapi.json"
    )
    
    @fallback_app.get("/")
    @fallback_app.get("/api/v1/health")
    async def health():
        """Health endpoint following API design standards"""
        return JSONResponse(
            content={
                "status": "healthy",
                "service": "ai-nurse-florence", 
                "version": "1.0.0",
                "banner": EDU_BANNER,
                "fallback_mode": True,
                "main_app_available": _has_main_app,
                "error": _import_error
            },
            headers={"Content-Type": "application/json"}
        )
    
    @fallback_app.get("/api/v1/disease")
    async def disease_info():
        """Disease endpoint with educational disclaimers"""
        return JSONResponse(
            content={
                "status": "ok",
                "message": "AI Nurse Florence Disease Information Service",
                "banner": EDU_BANNER,
                "query": "minimal",
                "service": "ai-nurse-florence",
                "fallback_mode": True
            },
            headers={"Content-Type": "application/json"}
        )
    
    handler = fallback_app

# Export for Vercel
app = handler
