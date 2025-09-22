"""
Simple test handler to debug Vercel deployment
"""

from fastapi import FastAPI

app = FastAPI(title="Test API")

@app.get("/")
def root():
    return {"message": "Test successful", "status": "working"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "test": "basic"}

# Vercel handler
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    def handler(event, context):
        return app
