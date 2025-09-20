import sys
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
app_dir = project_root / 'ai-nurse-florence-working' / 'ai-nurse-florence'

# Add to Python path
sys.path.insert(0, str(app_dir))
sys.path.insert(0, str(project_root))

# Set environment for the app
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
        
        app = FastAPI(
            title="AI Nurse Florence",
            description="Healthcare AI Assistant API - Fallback Mode",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/")
        async def root():
            return {
                "message": "AI Nurse Florence API",
                "status": "running",
                "mode": "fallback",
                "error": str(e),
                "app_dir": str(app_dir),
                "cwd": os.getcwd(),
                "python_path": sys.path[:3]
            }
        
        @app.get("/health")
        async def health():
            return {
                "status": "healthy", 
                "mode": "fallback",
                "app_directory_exists": app_dir.exists(),
                "main_app_file_exists": (app_dir / "app.py").exists()
            }
            
        @app.get("/api/health")
        async def api_health():
            return await health()
        
        return app

# Create the app instance
app = create_app()

# Vercel handler
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # If mangum is not available, create a simple handler
    def handler(event, context):
        return {"statusCode": 500, "body": "Mangum not available"}

# For testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)