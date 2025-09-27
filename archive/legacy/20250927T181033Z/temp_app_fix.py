# Add this near the top of app.py after the FastAPI app creation
from fastapi import APIRouter

# Create API router following Router Organization pattern
api_router = APIRouter(prefix="/api/v1")

# Register API router with main app
app.include_router(api_router)
