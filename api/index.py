"""Vercel serverless function for AI Nurse Florence FastAPI app."""
import sys
import os
from pathlib import Path

# Add project root to Python path (conftest.py pattern)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize variables before try block
_has_main_app = False
_import_error = "Not attempted"
fastapi_app = None

# Conditional imports pattern - graceful degradation
try:
    from app import app as fastapi_app
    
    # Test that the app actually has routes by checking the router
    if hasattr(fastapi_app, 'routes') and len(fastapi_app.routes) > 2:
        # Main app loaded successfully with routes
        _has_main_app = True
        _import_error = None
    else:
        # App imported but no routes - something is wrong
        _has_main_app = False
        _import_error = "App imported but routes not found"
        fastapi_app = None
        
except Exception as e:
    _has_main_app = False
    _import_error = str(e)
    fastapi_app = None

if _has_main_app and fastapi_app:
    # Export the main FastAPI app with full middleware stack
    app = fastapi_app
else:
    # Fallback app with debug information following service layer architecture
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(
        title="AI Nurse Florence - Debug Mode",
        description="Fallback app for debugging import issues"
    )
    
    @app.get("/api/v1/health")
    @app.get("/health")
    @app.get("/")
    async def debug_health():
        return JSONResponse({
            "status": "debug_mode",
            "service": "ai-nurse-florence",
            "error": _import_error,
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "python_path": sys.path[:3],
            "project_root": str(project_root),
            "files_in_root": os.listdir(project_root) if project_root.exists() else [],
            "main_app_available": _has_main_app,
            "routes_count": len(fastapi_app.routes) if fastapi_app else 0
        })
    
    @app.get("/api/v1/disease")
    async def debug_disease():
        return JSONResponse({
            "status": "debug_mode", 
            "message": "Main app not available - using fallback",
            "banner": "Educational purposes only — verify with healthcare providers. No PHI stored.",
            "query": "debug",
            "error": _import_error
        })
