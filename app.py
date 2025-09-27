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
    # Startup logging and OpenAPI population (moved from deprecated on_event)
    logger.info("=== AI NURSE FLORENCE STARTUP ===")
    logger.info(f"App: {getattr(settings, 'APP_NAME', 'AI Nurse Florence')}")
    logger.info(f"Version: {getattr(settings, 'APP_VERSION', '2.1.0')}")
    logger.info(f"Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}")
    logger.info(f"Routers loaded: {len(ROUTERS_LOADED)}")
    logger.info(f"Educational banner: {getattr(settings, 'EDUCATIONAL_BANNER', 'Educational purposes only')[:50]}...")
    logger.info("Healthcare AI assistant ready - Educational use only")

    # Log effective base URL for observability and populate OpenAPI servers
    effective_base = None
    try:
        from src.utils.config import get_base_url
        effective_base = get_base_url()
        logger.info(f"Effective BASE_URL: {effective_base}")
    except Exception:
        logger.debug("Could not determine effective BASE_URL at startup")

    try:
        if hasattr(app, 'openapi_schema') and app.openapi_schema is not None:
            if effective_base:
                app.openapi_schema.setdefault('servers', [])
                app.openapi_schema['servers'].append({"url": effective_base})
        else:
            # Force generation of openapi schema then set servers
            schema = app.openapi()
            if effective_base:
                schema.setdefault('servers', [])
                schema['servers'].append({"url": effective_base})
            app.openapi_schema = schema
    except Exception:
        logger.debug('Failed to populate OpenAPI servers with BASE_URL')

    try:
        yield
    finally:
        # Shutdown
        logger.info("Application shutdown complete")

# Create FastAPI app following coding instructions
app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI assistant providing evidence-based medical information for nurses and healthcare professionals. **Educational use only - not medical advice. No PHI stored.**",
    version="2.1.0",
    lifespan=lifespan,
    # servers list will be populated at startup with the effective base URL
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Create API router following Router Organization pattern
from fastapi import APIRouter
api_router = APIRouter(prefix="/api/v1")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# ROUTER REGISTRATION - Following Router Organization Pattern
try:
    from src.routers import available_routers, router_status
    
    logger.info("Registering routers following Router Organization pattern...")
    
    # Register each available router with proper error handling
    registered_count = 0
    for router_name, router in available_routers.items():
        try:
            if router_status.get(router_name, False) and router:
                # Include router in the API router
                api_router.include_router(router)
                logger.info(f"✅ Registered router: {router_name}")
                registered_count += 1
            else:
                logger.warning(f"⚠️ Skipped unavailable router: {router_name}")
        except Exception as e:
            logger.error(f"❌ Failed to register router {router_name}: {e}")
    
    logger.info(f"Router registration complete: {registered_count}/{len(available_routers)} routers registered")
    
except ImportError as e:
    logger.error(f"Router loading failed: {e}")
    logger.info("Attempting individual router registration with Conditional Imports Pattern...")
    
    # Individual router registration with graceful degradation
    routers_to_load = [
        ('src.routers.health', 'health'),
        ('src.routers.auth', 'auth'),
        ('src.routers.wizards.nursing_assessment', 'nursing_assessment'),
        ('src.routers.wizards.sbar_report', 'sbar_report'),
        ('src.routers.wizards.medication_reconciliation', 'medication_reconciliation'),
        ('src.routers.wizards.care_plan', 'care_plan'),
        ('src.routers.wizards.discharge_planning', 'discharge_planning')
    ]
    
    for module_path, router_name in routers_to_load:
        try:
            import importlib
            module = importlib.import_module(module_path)
            if hasattr(module, 'router'):
                api_router.include_router(module.router)
                logger.info(f"✅ Fallback: {router_name} router registered")
            else:
                logger.warning(f"⚠️ {router_name} module missing 'router' attribute")
        except ImportError as e:
            logger.warning(f"⚠️ {router_name} router unavailable: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to register {router_name}: {e}")

# STATIC FILE SERVING - Following API Design Standards
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import HTMLResponse

# Create directories if they don't exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Serve main healthcare interface
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_frontend(request: Request):
    """Serve the main AI Nurse Florence healthcare interface."""
    return templates.TemplateResponse("index.html", {"request": request})

# Health dashboard redirect
@app.get("/dashboard", include_in_schema=False) 
async def dashboard_redirect():
    """Redirect to main interface."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")

# Register API router with main app following Router Organization
app.include_router(api_router)