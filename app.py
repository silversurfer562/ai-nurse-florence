"""
AI Nurse Florence - Healthcare AI Assistant
Following Service Layer Architecture from coding instructions
Build: 2025-10-04 11:05
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging following coding instructions
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        APP_VERSION = "2.4.0"
        ALLOWED_ORIGINS = ["http://localhost:3000"]
        EDUCATIONAL_BANNER = "Educational purposes only"

    settings = FallbackSettings()

# Load and register routers following Router Organization pattern
ROUTERS_LOADED = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan following coding instructions startup patterns."""
    # Startup
    logger.info(f"🏥 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Healthcare AI assistant - Educational use only, no PHI stored")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI app following coding instructions
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - Following security pattern from coding instructions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
try:
    from src.utils.rate_limit import RateLimitMiddleware

    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting enabled: 60 requests per minute")
except Exception as e:
    logger.warning(f"Rate limiting unavailable: {e}")

# Load routers following Router Organization pattern
try:
    from src.routers import load_routers

    logger.info("🔄 Loading routers with conditional imports...")
    api_router = load_routers()
    ROUTERS_LOADED = getattr(load_routers, "routers_loaded", {})
except Exception as e:
    logger.error(f"Failed to load routers: {e}")
    api_router = APIRouter()

# Phase 3: Enhanced Auth Routes (2024-12-26)
try:
    from src.routers.enhanced_auth import router as enhanced_auth_router

    api_router.include_router(enhanced_auth_router)
    ROUTERS_LOADED["enhanced_auth"] = True
except Exception as e:
    logger.warning(f"Enhanced auth router unavailable: {e}")
    ROUTERS_LOADED["enhanced_auth"] = False

# Phase 3.1: Session Monitoring Routes (2024-12-27)
try:
    from src.routers.session_monitoring import router as session_monitoring_router

    api_router.include_router(session_monitoring_router)
    ROUTERS_LOADED["session_monitoring"] = True
except Exception as e:
    logger.warning(f"Session monitoring router unavailable: {e}")
    ROUTERS_LOADED["session_monitoring"] = False

# Phase 4.1: Cache Monitoring Routes (2025-01-06)
try:
    from src.routers.cache_monitoring import router as cache_monitoring_router

    api_router.include_router(cache_monitoring_router)
    logger.info(
        "Cache monitoring router registered successfully - Phase 4.1 Enhanced Caching"
    )
    ROUTERS_LOADED["cache_monitoring"] = True
except Exception as e:
    logger.warning(f"Cache monitoring router unavailable: {e}")
    ROUTERS_LOADED["cache_monitoring"] = False

# Phase 4.2: Enhanced Literature Service Routes (2025-01-10)
try:
    from src.routers.enhanced_literature import router as enhanced_literature_router

    api_router.include_router(enhanced_literature_router)
    logger.info(
        "Enhanced literature router registered successfully - Phase 4.2 Additional Medical Services"
    )
    ROUTERS_LOADED["enhanced_literature"] = True
except Exception as e:
    logger.warning(f"Enhanced literature router unavailable: {e}")
    ROUTERS_LOADED["enhanced_literature"] = False

# Phase 4.2: Drug Interactions Routes (2025-01-10)
try:
    from src.routers.drug_interactions import router as drug_interactions_router

    api_router.include_router(drug_interactions_router)
    logger.info(
        "Drug interactions router registered successfully - Phase 4.2 Additional Medical Services"
    )
    ROUTERS_LOADED["drug_interactions"] = True
except Exception as e:
    logger.warning(f"Drug interactions router unavailable: {e}")
    ROUTERS_LOADED["drug_interactions"] = False

# Wizard AI Routes with LangChain (2025-10-10)
try:
    from src.routers.wizard_ai import router as wizard_ai_router

    api_router.include_router(wizard_ai_router)
    logger.info(
        "Wizard AI router registered successfully - LangChain-powered clinical wizards"
    )
    ROUTERS_LOADED["wizard_ai"] = True
except Exception as e:
    logger.warning(f"Wizard AI router unavailable: {e}")
    ROUTERS_LOADED["wizard_ai"] = False

# Patient documents router (PDF generation)
try:
    from routers.patient_education_documents import router as patient_docs_router

    api_router.include_router(patient_docs_router)
    logger.info(
        "Patient documents router registered successfully - PDF generation enabled"
    )
    ROUTERS_LOADED["patient_docs"] = True
except Exception as e:
    logger.warning(f"Patient documents router unavailable: {e}")
    ROUTERS_LOADED["patient_docs"] = False

# User profile router
try:
    from routers.user_profile import router as user_profile_router

    api_router.include_router(user_profile_router)
    logger.info("User profile router registered successfully - Personalization enabled")
    ROUTERS_LOADED["user_profile"] = True
except Exception as e:
    logger.warning(f"User profile router unavailable: {e}")
    ROUTERS_LOADED["user_profile"] = False

# Admin router - protected routes for admin functions
try:
    from routers.admin import router as admin_router

    api_router.include_router(admin_router)
    logger.info("Admin router registered successfully")
    ROUTERS_LOADED["admin"] = True
except Exception as e:
    logger.warning(f"Admin router unavailable: {e}")
    ROUTERS_LOADED["admin"] = False

# Webhooks router - Railway deployment notifications
try:
    from routers.webhooks import router as webhooks_router

    app.include_router(webhooks_router)
    logger.info(
        "✅ Webhooks router registered successfully - Railway deployment notifications enabled"
    )
    ROUTERS_LOADED["webhooks"] = True
except Exception as e:
    logger.warning(f"Failed to register webhooks router: {e}")
    ROUTERS_LOADED["webhooks"] = False

# Content Settings Router - Diagnosis autocomplete and content management
try:
    from routers.content_settings import router as content_settings_router

    api_router.include_router(content_settings_router)
    logger.info("✅ Content settings router registered successfully")
    ROUTERS_LOADED["content_settings"] = True
except Exception as e:
    logger.warning(f"Failed to register content settings router: {e}")
    ROUTERS_LOADED["content_settings"] = False

# Epic EHR Integration Router - FHIR patient lookup
try:
    from src.routers.epic_ehr import router as epic_ehr_router

    api_router.include_router(epic_ehr_router)
    logger.info("✅ Epic EHR integration router registered successfully")
    ROUTERS_LOADED["epic_ehr"] = True
except Exception as e:
    logger.warning(f"Failed to register Epic EHR router: {e}")
    ROUTERS_LOADED["epic_ehr"] = False


# Education router (now using v1/patient-education)
try:
    from routers.education import router as education_router

    app.include_router(education_router, prefix="/api")
    logger.info("✅ Education router loaded successfully")
    ROUTERS_LOADED["education"] = True
except Exception as e:
    logger.warning(f"⚠️ Education router unavailable: {e}")
    ROUTERS_LOADED["education"] = False

# Include the main API router
app.include_router(api_router)

# Mount static files and frontend
os.makedirs("static", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Mount React app build
if os.path.exists("frontend/dist"):
    logger.info("✅ frontend/dist exists, mounting assets")
    app.mount(
        "/assets", StaticFiles(directory="frontend/dist/assets"), name="react-assets"
    )
    # Mount translation files
    if os.path.exists("frontend/dist/locales"):
        logger.info("✅ frontend/dist/locales exists, mounting /locales route")
        # List locales to verify
        locales_dirs = os.listdir("frontend/dist/locales")
        logger.info(f"📁 Available locales: {locales_dirs}")
        app.mount(
            "/locales", StaticFiles(directory="frontend/dist/locales"), name="locales"
        )
    else:
        logger.warning("⚠️ frontend/dist/locales NOT FOUND - translation files will 404")
else:
    logger.warning("⚠️ frontend/dist NOT FOUND - React app not available")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("=== AI NURSE FLORENCE STARTUP ===")
    logger.info(f"App: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Environment: Railway" if os.getenv("RAILWAY_ENVIRONMENT") else "Local")
    logger.info(f"Routers loaded: {len([k for k, v in ROUTERS_LOADED.items() if v])}")
    logger.info(f"Educational banner: {settings.EDUCATIONAL_BANNER[:50]}...")
    logger.info("Healthcare AI assistant ready - Educational use only")

    # Session cleanup service
    try:
        from src.services.session_cleanup import start_cleanup_service

        await start_cleanup_service()
        logger.info("✅ Session cleanup service started")
    except Exception as e:
        logger.warning(f"Session cleanup service unavailable: {e}")

    # Cache updater services - Disabled temporarily
    logger.info("⚠️ Cache updater services disabled - enable after fixing startup")

    # Database initialization - Skip for now
    logger.info(
        "⚠️ Database initialization skipped - run migrations separately if needed"
    )

    # Log effective BASE_URL
    base_url = os.getenv("BASE_URL", "http://0.0.0.0:8080")
    logger.info(f"Effective BASE_URL: {base_url}")

    logger.info("🚀 Application startup complete")


# Root route - serve React app
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_root():
    """Serve React app index.html at root."""
    index_path = "frontend/dist/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return HTMLResponse(
        content="<h1>AI Nurse Florence</h1><p>React frontend not built. Run: cd frontend && npm run build</p>",
        status_code=503,
    )


# Redirect /app to Clinical Wizards Dashboard
@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
async def redirect_to_dashboard():
    """Redirect /app to the Clinical Wizards Dashboard."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/static/dashboard.html", status_code=302)


# Catchall route for React Router (SPA client-side routing)
@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def catch_all(full_path: str):
    """
    Catchall route for React Router client-side routing.
    Serves index.html for all non-API, non-static routes.
    """
    # For file extensions, let them 404 naturally (don't serve React app)
    if "." in full_path.split("/")[-1]:
        # This looks like a file request (e.g., .json, .js, .css)
        # Don't serve React app for these
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Don't intercept API routes, docs, or health endpoints
    if (
        full_path.startswith("api")
        or full_path.startswith("docs")
        or full_path.startswith("openapi")
        or full_path == "health"
        or full_path == "status"
    ):
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Serve React app for all other routes (SPA client-side routing)
    if os.path.exists("frontend/dist/index.html"):
        with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return HTMLResponse(content="<h1>Not Found</h1>", status_code=404)
