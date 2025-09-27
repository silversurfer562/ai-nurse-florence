"""
Vercel serverless function wrapper for AI Nurse Florence
Provides a serverless entry point for the FastAPI application
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Vercel-specific environment variables
os.environ.setdefault('ENVIRONMENT', 'production')
os.environ.setdefault('LOG_LEVEL', 'INFO')
os.environ.setdefault('USE_LIVE', 'true')

try:
    # Import the FastAPI app
    from app import app
    
    # Export for Vercel (FastAPI apps work directly with Vercel)
    # No need for a custom handler - Vercel handles ASGI apps natively
    
except Exception:
    # Fallback minimal app if main app fails
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(
        title="AI Nurse Florence",
        description="Healthcare AI Assistant - Vercel Deployment",
        version="2.0.1"
    )
    
    @app.get("/")
    @app.get("/health")
    @app.get("/api/v1/health")
    async def health_check():
        return JSONResponse({
            "status": "error",
            "message": f"Deployment issue: {str(e)}",
            "platform": "vercel",
            "note": "Please check environment variables and dependencies"
        })
