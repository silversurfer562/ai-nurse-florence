"""Vercel serverless function wrapper for AI Nurse Florence FastAPI app."""
import sys
import os
from pathlib import Path

# Add project root to Python path following conftest.py pattern
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import main FastAPI app with service layer architecture
    from app import app
    
    # Vercel handler - export the FastAPI app directly
    # This maintains the full middleware stack and router configuration
    handler = app
    
except ImportError as e:
    # Conditional loading pattern - graceful degradation
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import traceback
    
    # Create minimal fallback app for debugging
    fallback_app = FastAPI(
        title="AI Nurse Florence - Debug Mode",
        description="Fallback app for debugging import issues"
    )
    
    @fallback_app.get("/api/v1/health")
    @fallback_app.get("/")
    async def debug_health():
        return JSONResponse({
            "status": "error",
            "message": f"Main app import failed: {str(e)}",
            "traceback": traceback.format_exc(),
            "python_path": sys.path,
            "working_directory": os.getcwd(),
            "project_root": str(project_root)
        })
    
    handler = fallback_app

# Export for Vercel
app = handler
