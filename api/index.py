"""Vercel serverless function for AI Nurse Florence FastAPI app."""
import sys
import os
from pathlib import Path

# Add project root to Python path (conftest.py pattern)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Conditional imports pattern - graceful degradation
try:
    from app import app as fastapi_app
    _has_main_app = True
except ImportError as e:
    _has_main_app = False
    _import_error = str(e)

if _has_main_app:
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
            "files_in_root": os.listdir(project_root) if project_root.exists() else []
        })
    
    @app.get("/api/v1/disease")
    async def debug_disease():
        return JSONResponse({
            "status": "debug_mode", 
            "message": "Main app not available - using fallback",
            "banner": "Educational purposes only — verify with healthcare providers. No PHI stored.",
            "query": "debug"
        })
