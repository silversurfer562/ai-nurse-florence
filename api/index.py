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

# Start with minimal FastAPI app to avoid function invocation failures
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI assistant providing evidence-based medical information for nurses",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

@app.get("/")
@app.get("/api/v1/health")
async def health():
    """Health endpoint following API design standards"""
    return {
        "status": "healthy",
        "service": "ai-nurse-florence", 
        "version": "1.0.0",
        "banner": EDU_BANNER,
        "deployment": "vercel_minimal",
        "python_version": sys.version.split()[0]
    }

@app.get("/api/v1/disease")
async def disease_info(q: str = "example"):
    """Disease endpoint with educational disclaimers"""
    return {
        "status": "ok",
        "message": "AI Nurse Florence Disease Information Service",
        "banner": EDU_BANNER,
        "query": q,
        "service": "ai-nurse-florence",
        "note": "Educational use only - not medical advice"
    }

# Export for Vercel
handler = app
