from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os
import traceback

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
    # Export the FastAPI app for Vercel
    handler = app
except Exception as e:
    # Create a fallback app if main app fails to import
    handler = FastAPI(title="AI Nurse Florence - Error", version="1.0.0")
    
    @handler.get("/")
    @handler.get("/api/v1/health")
    async def error_handler():
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Application failed to initialize: {str(e)}",
                "traceback": traceback.format_exc(),
                "pythonpath": sys.path
            }
        )
