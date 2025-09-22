"""
Minimal FastAPI app for Railway healthcheck testing
"""
from fastapi import FastAPI
import os

# Create minimal app
app = FastAPI(title="AI Nurse Florence - Minimal", version="2.0.1-minimal")

@app.get("/")
async def root():
    return {
        "message": "AI Nurse Florence - Minimal Mode",
        "status": "operational",
        "port": os.environ.get("PORT", "8000"),
        "version": "2.0.1-minimal"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "minimal": True}

@app.get("/test")
async def test():
    return {"test": "working", "port": os.environ.get("PORT")}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
