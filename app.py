"""
AI Nurse Florence - Healthcare AI Assistant
Following Service Layer Architecture from coding instructions
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Configure logging following coding instructions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration following Configuration Management pattern
try:
    from src.utils.config import get_settings
    settings = get_settings()
    logger.info(f"Configuration loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
except Exception as e:
    logger.error(f"Configuration failed: {e}")
    # Fallback configuration
    class FallbackSettings:
        APP_NAME = "AI Nurse Florence"
        APP_VERSION = "2.1.0"
        ALLOWED_ORIGINS = ["http://localhost:3000"]
        EDUCATIONAL_BANNER = "Educational purposes only"
    settings = FallbackSettings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan following coding instructions startup patterns."""
    # Startup
    logger.info(f"🏥 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Healthcare AI assistant - Educational use only, no PHI stored")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown complete")

# Create FastAPI app following coding instructions
app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI assistant providing evidence-based medical information for nurses and healthcare professionals. **Educational use only - not medical advice. No PHI stored.**",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration following Security & Middleware Stack
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, 'ALLOWED_ORIGINS', ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load and register routers following Router Organization pattern
ROUTERS_LOADED = {}
try:
    from src.routers import get_available_routers, get_router_status
    
    # Get available routers following Conditional Imports Pattern
    available_routers = get_available_routers()
    router_status = get_router_status()
    
    # Include routers with proper prefix following Router Organization
    for router_name, router in available_routers.items():
        try:
            if router_name in ['health', 'auth']:
                # Unprotected routes
                app.include_router(router, prefix="/api/v1")
            else:
                # Protected routes  
                app.include_router(router, prefix="/api/v1")
            
            ROUTERS_LOADED[router_name] = True
            logger.info(f"Router registered: {router_name}")
        except Exception as e:
            logger.warning(f"Failed to register router {router_name}: {e}")
            ROUTERS_LOADED[router_name] = False
    
    logger.info(f"Routers loaded: {sum(ROUTERS_LOADED.values())}/{len(router_status)}")
    
except Exception as e:
    logger.warning(f"Router loading failed: {e}")
    ROUTERS_LOADED = {}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "service": "ai-nurse-florence",
        "version": getattr(settings, 'APP_VERSION', '2.1.0'),
        "description": "Healthcare AI assistant - Educational use only",
        "banner": getattr(settings, 'EDUCATIONAL_BANNER', 'Educational purposes only'),
        "docs": "/docs",
        "health": "/api/v1/health",
        "routers_loaded": len(ROUTERS_LOADED),
        "timestamp": datetime.now().isoformat()
    }

# Enhanced health endpoint at root level
@app.get("/api/v1/health")
async def health_check():
    """Enhanced health check with router status."""
    
    # Count routes by category
    total_routes = len([r for r in app.routes if hasattr(r, 'path')])
    
    # Categorize routes
    wizard_routes = len([r for r in app.routes if hasattr(r, 'path') and 'wizard' in r.path])
    medical_routes = len([r for r in app.routes if hasattr(r, 'path') and 
                         any(term in r.path for term in ['disease', 'literature', 'clinical'])])
    
    # Service status
    try:
        from src.services import get_available_services
        services = get_available_services()
    except Exception:
        services = {"error": "Service registry unavailable"}
    
    health_data = {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": getattr(settings, 'APP_VERSION', '2.1.0'),
        "banner": getattr(settings, 'EDUCATIONAL_BANNER', 'Educational purposes only'),
        "environment": "railway" if os.getenv("RAILWAY_ENVIRONMENT") else "development",
        "routes": {
            "total": total_routes,
            "wizards": wizard_routes,
            "medical": medical_routes,
            "routers_loaded": ROUTERS_LOADED
        },
        "services": services,
        "configuration": {
            "live_services": getattr(settings, 'USE_LIVE_SERVICES', False),
            "educational_mode": True
        },
        "timestamp": datetime.now().isoformat()
    }
    
    return health_data

# Application startup logging
@app.on_event("startup")
async def startup_event():
    """Startup logging following coding instructions."""
    logger.info("=== AI NURSE FLORENCE STARTUP ===")
    logger.info(f"App: {getattr(settings, 'APP_NAME', 'AI Nurse Florence')}")
    logger.info(f"Version: {getattr(settings, 'APP_VERSION', '2.1.0')}")
    logger.info(f"Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}")
    logger.info(f"Routers loaded: {len(ROUTERS_LOADED)}")
    logger.info(f"Educational banner: {getattr(settings, 'EDUCATIONAL_BANNER', 'Educational purposes only')[:50]}...")
    logger.info("Healthcare AI assistant ready - Educational use only")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
