"""Vercel serverless function wrapper for AI Nurse Florence FastAPI app."""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import the main FastAPI app with all routers
    from app import app
    
except Exception as e:
    # Fallback for debugging
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse, HTMLResponse
    import traceback
    
    app = FastAPI(title="AI Nurse Florence - Fallback")
    
    @app.get("/")
    async def fallback_root():
        return HTMLResponse(f"""
        <h1>AI Nurse Florence - Import Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <details>
            <summary>Debug Info</summary>
            <pre>{traceback.format_exc()}</pre>
            <p><strong>Python Path:</strong> {sys.path}</p>
            <p><strong>Working Directory:</strong> {os.getcwd()}</p>
            <p><strong>Project Root:</strong> {str(project_root)}</p>
        </details>
        """)
    
    @app.get("/api/v1/health")
    async def fallback_health():
        return JSONResponse({
            "status": "fallback", 
            "error": str(e)
        })
