# Simple wrapper that tries to import the main app
import sys
import os

# Add the application directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'ai-nurse-florence-working', 'ai-nurse-florence')
sys.path.insert(0, app_dir)

try:
    # Change to the app directory so relative imports work
    original_cwd = os.getcwd()
    os.chdir(app_dir)
    
    # Import the main app
    from app import app
    
    # Restore original working directory
    os.chdir(original_cwd)
    
except Exception as e:
    # Fallback FastAPI app if main app fails to import
    from fastapi import FastAPI
    
    app = FastAPI(
        title="AI Nurse Florence", 
        description="Healthcare AI Assistant API",
        version="1.0.0"
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "AI Nurse Florence API", 
            "status": "running with fallback mode",
            "error": str(e)
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "fallback"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)