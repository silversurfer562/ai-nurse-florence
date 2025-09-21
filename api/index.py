"""Vercel serverless function for AI Nurse Florence.
Minimal FastAPI app with educational disclaimers.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Educational banner following API design standards
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

# Create minimal FastAPI app
app = FastAPI(
    title="AI Nurse Florence",
    description="Educational healthcare AI assistant",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

@app.get("/")
@app.get("/api/v1/health")
async def health():
    """Health endpoint with educational disclaimers"""
    return JSONResponse({
        "status": "healthy",
        "service": "ai-nurse-florence", 
        "version": "1.0.0",
        "banner": EDU_BANNER,
        "mode": "serverless"
    })

@app.get("/api/v1/disease")
async def disease_info():
    """Disease endpoint with educational disclaimers"""
    return JSONResponse({
        "status": "ok",
        "message": "AI Nurse Florence Disease Information Service",
        "banner": EDU_BANNER,
        "query": "fallback",
        "service": "ai-nurse-florence",
        "mode": "serverless"
    })
