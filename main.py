"""
AI Nurse Florence - Railway Entry Point

This file serves as the main entry point for Railway deployment.
It imports and exposes the complete FastAPI application with all medical features.
"""

import os
import sys
from pathlib import Path

# Ensure we're in the correct directory
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

print("=== RAILWAY MAIN.PY ENTRY POINT ===")
print(f"Project root: {project_root}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path[0]}")

# Import the complete FastAPI application
try:
    from app import app
    print("✅ Successfully imported complete AI Nurse Florence application")
    print("✅ All medical APIs, wizards, and advanced features should be available")
    
    # Count routes to verify complete app loaded
    route_count = len([r for r in app.routes if hasattr(r, 'path')])
    print(f"✅ Total routes loaded: {route_count}")
    
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    import traceback
    traceback.print_exc()
    
    # Create fallback app
    from fastapi import FastAPI
    app = FastAPI(
        title="AI Nurse Florence - Import Error", 
        description=f"Failed to import main app: {e}"
    )
    
    @app.get("/")
    def root():
        return {"error": f"Failed to import main app: {e}", "status": "fallback"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
