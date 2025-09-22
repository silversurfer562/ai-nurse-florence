from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

# Core imports
from utils.middleware import RequestIdMiddleware, LoggingMiddleware
from utils.logging import get_logger
from utils.config import settings, get_settings
from utils.security import SecurityHeadersMiddleware

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

# --- Import Routers (only the ones that exist) ---
from routers.summarize import router as summarize_router
from routers.disease import router as disease_router  
from routers.pubmed import router as pubmed_router
from routers.trials import router as trials_router
from routers.patient_education import router as patient_education_router
from routers.readability import router as readability_router
from routers.healthcheck import router as healthcheck_router

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
    WIZARDS_AVAILABLE = True
except ImportError:
    logger.warning("Wizard routers not available")
    WIZARDS_AVAILABLE = False
    patient_education_wizard_router = None
    sbar_report_wizard_router = None
    treatment_plan_wizard_router = None

app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI Assistant providing evidence-based medical information",
    version="2.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

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
    """Root endpoint with service information"""
    return {
        "message": "AI Nurse Florence - Healthcare AI Assistant",
        "status": "operational", 
        "version": "2.0.1",
        "banner": "Educational purposes only — verify with healthcare providers. No PHI stored.",
        "docs": "/docs",
        "health": "/health", 
        "api_health": "/api/v1/health",
        "frontend": "/app"
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


# Checks for api-bearer environment variable in vercel deployment
def require_bearer(request: Request):
    expected = (get_settings().API_BEARER or "").strip()
    auth = request.headers.get("authorization", "")
    token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""
    if not expected or token != expected:
        raise HTTPException(401, "Unauthorized")

@app.get("/admin/stats")
async def admin_stats(
    request: Request,
    __=Depends(require_bearer),
):
    return {"ok": True}

# --- Include Routers ---
api_router.include_router(summarize_router)
api_router.include_router(disease_router)
api_router.include_router(pubmed_router)
api_router.include_router(trials_router)
api_router.include_router(patient_education_router)
api_router.include_router(readability_router)

# Add wizards if available
if WIZARDS_AVAILABLE and patient_education_wizard_router:
    api_router.include_router(patient_education_wizard_router)
if WIZARDS_AVAILABLE and sbar_report_wizard_router:
    api_router.include_router(sbar_report_wizard_router)
if WIZARDS_AVAILABLE and treatment_plan_wizard_router:
    api_router.include_router(treatment_plan_wizard_router)

# Unprotected routes
unprotected_router.include_router(healthcheck_router)
if AUTH_AVAILABLE and auth_router:
    unprotected_router.include_router(auth_router)

# Include routers in app
app.include_router(api_router)
app.include_router(unprotected_router)

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
