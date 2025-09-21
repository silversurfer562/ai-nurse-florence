from fastapi import FastAPI
from mangum import Mangum

# Create FastAPI app
app = FastAPI(title="AI Nurse Florence", version="1.0.0")

@app.get("/")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": "1.0.0",
        "message": "FastAPI working on Vercel!"
    }

# Use Mangum to wrap FastAPI for serverless
handler = Mangum(app)
