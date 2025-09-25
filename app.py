from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException
from routers import openapi_gpt
from fastapi.responses import JSONResponse, Response, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import sys
import logging

# Core imports
from utils.middleware import RequestIdMiddleware, LoggingMiddleware
from utils.logging import get_logger
from utils.config import settings, get_settings
from utils.security import SecurityHeadersMiddleware

# Configure logging for Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set up logger
logger = get_logger(__name__)

# Define exempt paths for rate limiting
EXEMPT_PATHS = {
    "/docs",
    "/redoc", 
    "/openapi.json",
    "/metrics",
    "/health",
    "/api/v1/health",
    "/",
    "/app",
    "/static"
}

# --- Import Routers (with explicit error handling) ---
routers_loaded = []
routers_failed = []

try:
    from routers.summarize import router as summarize_router
    routers_loaded.append("summarize")
except Exception as e:
    logger.error(f"Failed to import summarize router: {e}")
    routers_failed.append(f"summarize: {e}")
    summarize_router = None

try:
    from routers.disease import router as disease_router
    routers_loaded.append("disease")
except Exception as e:
    logger.error(f"Failed to import disease router: {e}")
    routers_failed.append(f"disease: {e}")
    disease_router = None

try:
    from routers.pubmed import router as pubmed_router
    routers_loaded.append("pubmed")
except Exception as e:
    logger.error(f"Failed to import pubmed router: {e}")
    routers_failed.append(f"pubmed: {e}")
    pubmed_router = None

try:
    from routers.trials import router as trials_router
    routers_loaded.append("trials")
except Exception as e:
    logger.error(f"Failed to import trials router: {e}")
    routers_failed.append(f"trials: {e}")
    trials_router = None

try:
    from routers.patient_education import router as patient_education_router
    routers_loaded.append("patient_education")
except Exception as e:
    logger.error(f"Failed to import patient_education router: {e}")
    routers_failed.append(f"patient_education: {e}")
    patient_education_router = None

try:
    from routers.readability import router as readability_router
    routers_loaded.append("readability")
except Exception as e:
    logger.error(f"Failed to import readability router: {e}")
    routers_failed.append(f"readability: {e}")
    readability_router = None

try:
    from routers.education import router as education_router
    routers_loaded.append("education")
except Exception as e:
    logger.error(f"Failed to import education router: {e}")
    routers_failed.append(f"education: {e}")
    education_router = None

try:
    from routers.medlineplus import router as medlineplus_router
    routers_loaded.append("medlineplus")
except Exception as e:
    logger.error(f"Failed to import medlineplus router: {e}")
    routers_failed.append(f"medlineplus: {e}")
    medlineplus_router = None

try:
    from routers.clinical_documents import router as clinical_documents_router
    routers_loaded.append("clinical_documents")
except Exception as e:
    logger.error(f"Failed to import clinical_documents router: {e}")
    routers_failed.append(f"clinical_documents: {e}")
    clinical_documents_router = None

try:
    from routers.healthcheck import router as healthcheck_router
    routers_loaded.append("healthcheck")
except Exception as e:
    logger.error(f"Failed to import healthcheck router: {e}")
    routers_failed.append(f"healthcheck: {e}")
    healthcheck_router = None

logger.info(f"Routers loaded: {routers_loaded}")
logger.info(f"Routers failed: {routers_failed}")

# Import auth if it exists
try:
    from routers.auth import router as auth_router
    AUTH_AVAILABLE = True
except ImportError:
    logger.warning("Auth router not available")
    AUTH_AVAILABLE = False
    auth_router = None

# Import wizards if they exist
try:
    from routers.wizards.patient_education import router as patient_education_wizard_router
    from routers.wizards.sbar_report import router as sbar_report_wizard_router
    from routers.wizards.treatment_plan import router as treatment_plan_wizard_router
    from routers.wizards.clinical_trials import router as clinical_trials_wizard_router
    from routers.wizards.disease_search import router as disease_search_wizard_router
    WIZARDS_AVAILABLE = True
except ImportError:
    logger.warning("Wizard routers not available")
    WIZARDS_AVAILABLE = False
    patient_education_wizard_router = None
    sbar_report_wizard_router = None
    treatment_plan_wizard_router = None
    clinical_trials_wizard_router = None
    disease_search_wizard_router = None

# Create FastAPI instance
app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI Assistant providing evidence-based medical information",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Log startup diagnostics
print(f"=== AI NURSE FLORENCE FULL APPLICATION STARTING ===")
print(f"THIS IS THE COMPLETE APP.PY WITH ALL MEDICAL FEATURES")
print(f"Deployment ID: {os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local')}")
print(f"Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
print(f"Port: {os.environ.get('PORT', '8000')}")
print(f"Git commit: 1558a38")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Loaded routers: {routers_loaded}")
print(f"Failed routers: {routers_failed}")
print(f"Wizards available: {WIZARDS_AVAILABLE}")
print(f"Auth available: {AUTH_AVAILABLE}")
print(f"Expected ~35 routes in full app")
print("===========================================================")

# Ensure health endpoint is available immediately
print(f"Total app routes defined: {len(app.routes)}")
print("Health endpoint will be available at /health")

# Mount static files (HTML frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Frontend route
@app.get("/app", response_class=HTMLResponse)
async def frontend():
    """Serve the main frontend application"""
    return FileResponse("static/index.html")

# Root endpoint  
@app.get("/")
async def root():
    """Serve the main frontend application"""
    return FileResponse("static/index.html")

@app.get("/info")
async def info():
    """Service information endpoint"""
    return {
        "message": "AI Nurse Florence - Healthcare AI Assistant",
        "status": "operational", 
        "version": "2.1.0",
        "banner": "Educational purposes only — verify with healthcare providers. No PHI stored.",
        "docs": "/docs",
        "health": "/health", 
        "api_health": "/api/v1/health",
        "frontend": "/app"
    }

# Health endpoint for Railway healthcheck
@app.get("/health")
async def health():
    """Health check endpoint optimized for Railway deployment"""
    # Log that health check was called
    logger.info("Health check endpoint called")
    
    return {
        "status": "healthy", 
        "timestamp": "2025-09-25-000902",
        "service": "ai-nurse-florence",
        "version": "2.1.0",
        "routers_count": len(routers_loaded)
    }

# Diagnostic endpoint to see what loaded
@app.get("/debug/status")
async def debug_status():
    """Debug endpoint to see what components loaded"""
    return {
        "routers_loaded": routers_loaded,
        "routers_failed": routers_failed,
        "wizards_available": WIZARDS_AVAILABLE,
        "auth_available": AUTH_AVAILABLE,
        "version": "2.1.0"
    }

# --- API Versioning Router ---
api_router = APIRouter(prefix="/api/v1")
unprotected_router = APIRouter(prefix="/api/v1") 

# --- Middleware Configuration ---
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)

# Setup metrics if available
try:
    from utils.metrics import setup_metrics
    setup_metrics(app)
except ImportError:
    logger.warning("Metrics not available")

# Setup rate limiting if available  
try:
    from utils.rate_limit import RateLimiter
    app.add_middleware(
        RateLimiter,
        requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
        exempt_paths=EXEMPT_PATHS
    )
except ImportError:
    logger.warning("Rate limiting not available")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers (only if they loaded successfully) ---
if summarize_router:
    api_router.include_router(summarize_router)
if disease_router:
    api_router.include_router(disease_router)
if pubmed_router:
    api_router.include_router(pubmed_router)
if trials_router:
    api_router.include_router(trials_router)
if patient_education_router:
    api_router.include_router(patient_education_router)
if readability_router:
    api_router.include_router(readability_router)
if education_router:
    api_router.include_router(education_router)
if medlineplus_router:
    api_router.include_router(medlineplus_router)
if clinical_documents_router:
    api_router.include_router(clinical_documents_router)

# Add wizards if available
if WIZARDS_AVAILABLE and patient_education_wizard_router:
    api_router.include_router(patient_education_wizard_router)
if WIZARDS_AVAILABLE and sbar_report_wizard_router:
    api_router.include_router(sbar_report_wizard_router)
if WIZARDS_AVAILABLE and treatment_plan_wizard_router:
    api_router.include_router(treatment_plan_wizard_router)
if WIZARDS_AVAILABLE and clinical_trials_wizard_router:
    api_router.include_router(clinical_trials_wizard_router)
if WIZARDS_AVAILABLE and disease_search_wizard_router:
    api_router.include_router(disease_search_wizard_router)

# Unprotected routes
if healthcheck_router:
    unprotected_router.include_router(healthcheck_router)
if AUTH_AVAILABLE and auth_router:
    unprotected_router.include_router(auth_router)

# Include routers in app
app.include_router(api_router)
app.include_router(unprotected_router)
app.include_router(openapi_gpt.router)

# Register exception handlers if available
try:
    from utils.error_handlers import register_exception_handlers
    register_exception_handlers(app)
except ImportError:
    logger.warning("Exception handlers not available")

@app.on_event("startup")
async def startup_event() -> None:
    logger.info("AI Nurse Florence API starting up")
    
    # Initialize database if needed
    try:
        if "sqlite" in settings.DATABASE_URL:
            logger.info("Using SQLite database - tables will be created as needed")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")

    # Initialize OpenAI client if available
    if settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI as OpenAIClient
            global client
            client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client configured")
        except Exception as e:
            logger.warning(f"OpenAI client setup failed: {e}")

@app.on_event("shutdown") 
async def shutdown_event() -> None:
    logger.info("AI Nurse Florence API shutting down")
