"""
AI Nurse Florence - Vercel Serverless Handler

Imports the main FastAPI application for serverless deployment.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
app_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(app_dir))
os.environ.setdefault('PYTHONPATH', str(app_dir))

def create_app():
    """Create and configure the FastAPI app"""
    try:
        # Change to app directory for relative imports
        original_cwd = os.getcwd()
        os.chdir(str(app_dir))
        
        # Import the main application
        from app import app
        
        # Restore directory
        os.chdir(original_cwd)
        
        return app
        
    except Exception as e:
        # Fallback app if main import fails
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        fallback_app = FastAPI(
            title="AI Nurse Florence",
            description="Healthcare AI Assistant API - Fallback Mode",
            version="1.0.0"
        )
        
        # Add CORS middleware
        fallback_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @fallback_app.get("/")
        async def root():
            return {
                "message": "AI Nurse Florence API",
                "status": "running",
                "mode": "fallback",
                "error": str(e),
                "app_dir": str(app_dir),
                "cwd": os.getcwd()
            }
        
        @fallback_app.get("/health")
        async def health():
            return {
                "status": "healthy", 
                "mode": "fallback",
                "app_directory_exists": app_dir.exists(),
                "main_app_file_exists": (app_dir / "app.py").exists()
            }
            
        @fallback_app.get("/api/v1/health")
        async def api_health():
            return await health()
            
        return fallback_app

# Create the app instance
app = create_app()

# Vercel handler
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # If mangum is not available, create a simple handler
    def handler(event, context):
        return app
