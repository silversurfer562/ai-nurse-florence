"""
AI Nurse Florence - Healthcare AI Assistant
Following Service Layer Architecture from coding instructions
Build: 2025-10-04 11:05
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import APIRouter, FastAPI, Request
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
        APP_VERSION = "2.3.0"
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
    # Startup logging and OpenAPI population (moved from deprecated on_event)
    logger.info("=== AI NURSE FLORENCE STARTUP ===")
    logger.info(f"App: {getattr(settings, 'APP_NAME', 'AI Nurse Florence')}")
    logger.info(f"Version: {getattr(settings, 'APP_VERSION', '2.3.0')}")
    logger.info(
        f"Environment: {'Railway' if os.getenv('RAILWAY_ENVIRONMENT') else 'Development'}"
    )
    logger.info(f"Routers loaded: {len(ROUTERS_LOADED)}")
    logger.info(
        f"Educational banner: {getattr(settings, 'EDUCATIONAL_BANNER', 'Educational purposes only')[:50]}..."
    )
    logger.info("Healthcare AI assistant ready - Educational use only")

    # Initialize session cleanup service (Phase 3.4.4)
    try:
        from src.services.session_cleanup import start_session_cleanup

        await start_session_cleanup()
        logger.info("✅ Session cleanup service started")
    except Exception as e:
        logger.warning(f"⚠️ Session cleanup service not available: {e}")

    # Cache updater services disabled to prevent startup hang
    logger.info("⚠️ Cache updater services disabled - enable after fixing startup")

    # Initialize diagnosis content library (auto-seed if empty)
    # Temporarily disabled to fix Railway startup hang - database initialization moved to separate migration
    logger.info(
        "⚠️ Database initialization skipped - run migrations separately if needed"
    )

    # Log effective base URL for observability
    try:
        from src.utils.config import get_base_url

        effective_base = get_base_url()
        logger.info(f"Effective BASE_URL: {effective_base}")
    except Exception:
        logger.debug("Could not determine effective BASE_URL at startup")

    # OpenAPI schema population disabled to prevent startup hang
    logger.debug("OpenAPI schema will be generated on first /docs request")

    logger.info("🚀 Application startup complete")

    try:
        yield
    finally:
        # Shutdown
        # Stop session cleanup service (Phase 3.4.4)
        try:
            from src.services.session_cleanup import stop_session_cleanup

            await stop_session_cleanup()
            logger.info("✅ Session cleanup service stopped")
        except Exception as e:
            logger.warning(f"⚠️ Error stopping session cleanup service: {e}")

        # Stop drug cache updater service (Phase 4.2)
        try:
            from src.services.drug_cache_updater import get_drug_cache_updater

            drug_cache_updater = get_drug_cache_updater()
            await drug_cache_updater.stop()
            logger.info("✅ Drug cache updater service stopped")
        except Exception as e:
            logger.warning(f"⚠️ Error stopping drug cache updater service: {e}")

        # Stop disease cache updater service (Phase 4.2)
        try:
            from src.services.disease_cache_updater import get_disease_cache_updater

            disease_cache_updater = get_disease_cache_updater()
            await disease_cache_updater.stop()
            logger.info("✅ Disease cache updater service stopped")
        except Exception as e:
            logger.warning(f"⚠️ Error stopping disease cache updater service: {e}")

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
    openapi_url="/openapi.json",
)

# Create API router following Router Organization pattern
api_router = APIRouter(prefix="/api/v1")


# CORS Configuration following Security & Middleware Stack
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "ALLOWED_ORIGINS", ["http://localhost:3000"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware - conditionally loaded
try:
    from src.utils.rate_limit import RateLimiter

    if getattr(settings, "RATE_LIMIT_ENABLED", True):
        # Define paths that are exempt from rate limiting
        exempt_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/health",
            "/metrics",
        ]

        # Get rate limit value from settings
        rate_limit = getattr(settings, "RATE_LIMIT_REQUESTS", 60)

        # Add RateLimiter middleware
        app.add_middleware(
            RateLimiter, requests_per_minute=rate_limit, exempt_paths=exempt_paths
        )
        logger.info(f"Rate limiting enabled: {rate_limit} requests per minute")
except ImportError:
    logger.warning("Rate limiting middleware not available")

# Add admin router first (from local routers directory)
try:
    from routers.admin import router as admin_router

    api_router.include_router(admin_router)
    ROUTERS_LOADED["admin"] = True
    logger.info("Admin router registered successfully")
except Exception as e:
    logger.warning(f"Failed to register admin router: {e}")
    ROUTERS_LOADED["admin"] = False

# Add cache monitoring router (Phase 4.1 - Enhanced Redis Caching)
try:
    from src.routers.cache_monitoring import router as cache_monitoring_router

    api_router.include_router(cache_monitoring_router)
    ROUTERS_LOADED["cache_monitoring"] = True
    logger.info(
        "Cache monitoring router registered successfully - Phase 4.1 Enhanced Caching"
    )
except Exception as e:
    logger.warning(f"Failed to register cache monitoring router: {e}")
    ROUTERS_LOADED["cache_monitoring"] = False

# Add enhanced literature router (Phase 4.2 - Additional Medical Services)
try:
    from src.routers.enhanced_literature import router as enhanced_literature_router

    api_router.include_router(enhanced_literature_router)
    ROUTERS_LOADED["enhanced_literature"] = True
    logger.info(
        "Enhanced literature router registered successfully - Phase 4.2 Additional Medical Services"
    )
except Exception as e:
    logger.warning(f"Failed to register enhanced literature router: {e}")
    ROUTERS_LOADED["enhanced_literature"] = False

# Add drug interactions router (Phase 4.2 - Additional Medical Services)
try:
    from src.routers.drug_interactions import router as drug_interactions_router

    api_router.include_router(drug_interactions_router)
    ROUTERS_LOADED["drug_interactions"] = True
    logger.info(
        "Drug interactions router registered successfully - Phase 4.2 Additional Medical Services"
    )
except Exception as e:
    logger.warning(f"Failed to register drug interactions router: {e}")
    ROUTERS_LOADED["drug_interactions"] = False

# Add patient documents router (PDF generation for patient education)
try:
    from routers.patient_documents import router as patient_documents_router

    api_router.include_router(patient_documents_router)
    ROUTERS_LOADED["patient_documents"] = True
    logger.info(
        "Patient documents router registered successfully - PDF generation enabled"
    )
except Exception as e:
    logger.warning(f"Failed to register patient documents router: {e}")
    ROUTERS_LOADED["patient_documents"] = False

# Add user profile router (Personalization and work settings)
try:
    from routers.user_profile import router as user_profile_router

    api_router.include_router(user_profile_router)
    ROUTERS_LOADED["user_profile"] = True
    logger.info("User profile router registered successfully - Personalization enabled")
except Exception as e:
    logger.warning(f"Failed to register user profile router: {e}")
    ROUTERS_LOADED["user_profile"] = False

# Additional routers temporarily disabled to fix startup hang
logger.info(
    "⚠️ Additional routers (content_settings, genes, disease_glossary, webhooks) disabled during startup troubleshooting"
)


# Serve main healthcare interface at root
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_main_interface(request: Request):
    """Serve the React app."""
    try:
        # Try React build first
        if os.path.exists("frontend/dist/index.html"):
            with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        # Fallback to static HTML
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to template if static file doesn't exist
        return templates.TemplateResponse("index.html", {"request": request})


# API status endpoint
@app.get("/status")
async def api_status():
    """API status endpoint with application information."""
    return {
        "service": "ai-nurse-florence",
        "version": getattr(settings, "APP_VERSION", "2.1.0"),
        "description": "Healthcare AI assistant - Educational use only",
        "banner": getattr(settings, "EDUCATIONAL_BANNER", "Educational purposes only"),
        "docs": "/docs",
        "health": "/api/v1/health",
        "routers_loaded": len(ROUTERS_LOADED),
        "timestamp": datetime.now().isoformat(),
    }


# Simple health endpoint for Railway health checks
@app.get("/health")
async def root_health():
    """Simple health check for Railway."""
    return {"status": "healthy", "service": "ai-nurse-florence"}


# Enhanced health endpoint at root level
@app.get("/api/v1/health")
async def health_check():
    """Enhanced health check with router status."""

    # Count routes by category
    total_routes = len([r for r in app.routes if hasattr(r, "path")])

    # Categorize routes
    wizard_routes = len([r for r in app.routes if "wizard" in getattr(r, "path", "")])
    medical_routes = len(
        [
            r
            for r in app.routes
            if any(
                term in getattr(r, "path", "")
                for term in ["disease", "literature", "clinical"]
            )
        ]
    )

    # Service status
    try:
        from src.services import get_available_services

        services = get_available_services()
    except Exception:
        services = {"error": "Service registry unavailable"}

    health_data = {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": getattr(settings, "APP_VERSION", "2.1.0"),
        "banner": getattr(settings, "EDUCATIONAL_BANNER", "Educational purposes only"),
        "environment": "railway" if os.getenv("RAILWAY_ENVIRONMENT") else "development",
        "routes": {
            "total": total_routes,
            "wizards": wizard_routes,
            "medical": medical_routes,
            "routers_loaded": ROUTERS_LOADED,
        },
        "services": services,
        "configuration": {
            "live_services": getattr(settings, "USE_LIVE_SERVICES", False),
            "educational_mode": True,
        },
        "timestamp": datetime.now().isoformat(),
    }

    return health_data


if __name__ == "__main__":
    import os

    import uvicorn

    # Use Railway's PORT if available, otherwise default to 8080 (Railway default)
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True, log_level="info")

# NOTE: Router registration is handled above by including routers onto `api_router`.
# The previous duplicate registration block was removed to avoid double-including routers
# which caused duplicate OpenAPI operation IDs. If a fallback import path is needed,
# the registry in `src.routers` should be updated instead of registering routers twice here.

# Create directories if they don't exist
os.makedirs("static/css", exist_ok=True)
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


# Wizard-specific routes
@app.get("/wizards", response_class=HTMLResponse, include_in_schema=False)
async def serve_wizard_hub():
    """Serve the wizard hub interface."""
    try:
        with open("frontend/src/pages/wizard-hub.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
        <!DOCTYPE html>
        <html><head><title>Clinical Wizards</title></head>
        <body>
            <h1>Clinical Wizards</h1>
            <ul>
                <li><a href="/wizards/sbar">SBAR Report Generator</a></li>
                <li><a href="/wizards/treatment-plan">Treatment Plan Wizard</a></li>
                <li><a href="/wizards/patient-education">Patient Education</a></li>
            </ul>
        </body></html>
        """,
            status_code=200,
        )


@app.get("/wizards/{wizard_name}", response_class=HTMLResponse, include_in_schema=False)
async def serve_wizard_interface(wizard_name: str):
    """Serve individual wizard interfaces."""
    wizard_map = {
        "sbar": "sbar-wizard.html",
        "treatment-plan": "treatment-plan-wizard.html",
        "patient-education": "patient-education-wizard.html",
    }

    if wizard_name in wizard_map:
        try:
            with open(
                f"frontend/src/pages/{wizard_map[wizard_name]}", "r", encoding="utf-8"
            ) as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
        except FileNotFoundError:
            # Fallback to generic wizard template
            return HTMLResponse(
                content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{wizard_name.title()} Wizard</title>
                <link rel="stylesheet" href="/frontend/src/styles/wizard.css">
            </head>
            <body>
                <div id="wizard-app"></div>
                <script type="module">
                    import SbarWizard from '/frontend/src/components/wizards/SbarWizard.js';
                    new SbarWizard('wizard-app');
                </script>
            </body>
            </html>
            """
            )

    return HTMLResponse(content="<h1>Wizard not found</h1>", status_code=404)


# Additional static HTML routes
@app.get("/chat", response_class=HTMLResponse, include_in_schema=False)
async def serve_chat():
    """Serve the chat interface."""
    try:
        with open("static/chat.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Chat interface not found</h1>", status_code=404
        )


@app.get("/clinical-workspace", response_class=HTMLResponse, include_in_schema=False)
async def serve_clinical_workspace():
    """Serve the clinical workspace interface."""
    try:
        with open("static/clinical-workspace.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Clinical workspace not found</h1>", status_code=404
        )


@app.get("/clinical-assessment", response_class=HTMLResponse, include_in_schema=False)
async def serve_clinical_assessment():
    """Serve the clinical assessment optimizer."""
    try:
        with open(
            "static/clinical-assessment-optimizer.html", "r", encoding="utf-8"
        ) as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Clinical assessment not found</h1>", status_code=404
        )


# Health dashboard redirect
@app.get("/dashboard", include_in_schema=False)
async def dashboard_redirect():
    """Redirect to main interface."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/")


# Register API router with main app following Router Organization
app.include_router(api_router)


# Root route to serve simple HTML landing page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_root():
    """Serve static HTML landing page at root."""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Landing page not found</h1>", status_code=404)


# Serve drug-checker route (React app)
@app.get("/drug-checker", response_class=HTMLResponse, include_in_schema=False)
async def serve_drug_checker():
    """Serve React drug interaction app."""
    if os.path.exists("frontend/dist/index.html"):
        with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Drug checker not found</h1>", status_code=404)


# Catch-all route for React Router (SPA) - must be last
@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def serve_react_app(full_path: str, request: Request):
    """Catch-all route to serve React app for client-side routing."""
    # Skip if no path (root handled above)
    if not full_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # For file extensions, let them 404 naturally (don't serve React app)
    if "." in full_path.split("/")[-1]:
        # This looks like a file request (e.g., .json, .js, .css)
        # Don't serve React app for these
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Don't intercept API routes or docs
    if (
        full_path.startswith("api")
        or full_path.startswith("docs")
        or full_path.startswith("openapi")
    ):
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Serve React app for all other routes (SPA client-side routing)
    if os.path.exists("frontend/dist/index.html"):
        with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return HTMLResponse(content="<h1>Not Found</h1>", status_code=404)
