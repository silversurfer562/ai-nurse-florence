"""Minimal Vercel serverless function test"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def root():
    return JSONResponse(
        content={"message": "Hello from AI Nurse Florence", "status": "ok"},
        headers={"Content-Type": "application/json"}
    )

@app.get("/api/v1/health")
async def health():
    return JSONResponse(
        content={"status": "healthy", "service": "ai-nurse-florence"},
        headers={"Content-Type": "application/json"}
    )
