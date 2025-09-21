"""Minimal Vercel serverless function for AI Nurse Florence API"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Nurse Florence API",
    description="Educational healthcare AI assistant API",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware to allow GitHub Pages to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://silversurfer562.github.io",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"  # Allow all origins for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health():
    return JSONResponse(
        content={
            "status": "healthy", 
            "service": "ai-nurse-florence",
            "version": "1.0.0",
            "deployment": "vercel"
        },
        headers={"Content-Type": "application/json"}
    )

@app.get("/api/v1/disease")
async def disease_info():
    return JSONResponse(
        content={
            "status": "ok",
            "message": "AI Nurse Florence Disease Information Service",
            "service": "ai-nurse-florence"
        },
        headers={"Content-Type": "application/json"}
    )
