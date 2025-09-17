from fastapi import FastAPI, Request, APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import Callable

# New imports
from utils.middleware import RequestIdMiddleware, LoggingMiddleware
from utils.error_handlers import register_exception_handlers
from utils.logging import get_logger
from utils.metrics import setup_metrics
from utils.rate_limit import RateLimiter
from utils.config import settings
from utils.security import SecurityHeadersMiddleware
from utils.auth import get_current_user # Import the new dependency
from database import Base, engine # Import database components

# Load environment variables
# This is still useful for local development, Pydantic will override with actual env vars if they exist
load_dotenv()

# Set up logger
logger = get_logger(__name__)

# --- Routers ---
from routers.summarize import router as summarize_router
from routers.disease import router as disease_router
from routers.wizards.patient_education import router as patient_education_wizard_router
from routers.wizards.sbar_report import router as sbar_report_wizard_router
from routers.wizards.clinical_trials import router as clinical_trials_wizard_router
from routers.wizards.disease_search import router as disease_search_wizard_router
from routers.pubmed import router as pubmed_router
from routers.auth import router as auth_router # Import the new auth router
from routers.healthcheck import router as healthcheck_router

# Do NOT import OpenAI at module import time; make it optional / lazy
client = None

app = FastAPI(
    title="Nurses API",
    description="""
    AI-powered healthcare information API for nurses and healthcare professionals.
    
    This API provides access to medical information, research papers, clinical trials,
    and AI-assisted summarization of medical text. It's designed to help healthcare
    professionals access reliable information quickly.
    
    ## Features
    
    * Disease and condition information lookups
    * PubMed article search
    * Clinical trials search
    * MedlinePlus health topic summaries
    * Text summarization and SBAR generation
    * Readability analysis
    * Patient education materials
    
    ## Authentication
    
    Most endpoints require API key authentication using a Bearer token.
    Include the token in the Authorization header: `Authorization: Bearer your-api-key`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "disease",
            "description": "Operations related to diseases and medical conditions"
        },
        {
            "name": "pubmed",
            "description": "Search for medical research articles in PubMed"
        },
        {
            "name": "clinicaltrials",
            "description": "Search for clinical trials"
        },
        {
            "name": "medlineplus",
            "description": "Access health information from MedlinePlus"
        },
        {
            "name": "summarize",
            "description": "AI-powered text summarization services"
        },
        {
            "name": "readability",
            "description": "Analyze readability of medical texts"
        }
    ]
)

# --- API Versioning Router ---
# All API routes will be nested under this single router.
api_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)] # Protect all v1 routes
)

# A separate, unprotected router for authentication
unprotected_router = APIRouter(prefix="/api/v1")

# --- Middleware Configuration ---

# Add security headers middleware (should be one of the first)
app.add_middleware(SecurityHeadersMiddleware)

# Add request ID and logging middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)

# Set up metrics
setup_metrics(app)

# Define paths that should be exempt from rate limiting
EXEMPT_PATHS = {
    "/health",
    "/metrics", 
    "/docs",
    "/redoc",
    "/openapi.json"
}

# Add rate limiting
app.add_middleware(
    RateLimiter,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    exempt_paths=EXEMPT_PATHS
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers into the Versioned API Router ---
api_router.include_router(summarize_router)
api_router.include_router(disease_router)
api_router.include_router(patient_education_wizard_router)
api_router.include_router(sbar_report_wizard_router)
api_router.include_router(clinical_trials_wizard_router)
api_router.include_router(pubmed_router)

# The auth router is unprotected and handles the login flow
unprotected_router.include_router(auth_router)
unprotected_router.include_router(healthcheck_router)

# Include the main versioned router into the app
app.include_router(api_router)
app.include_router(unprotected_router)

# Add a simple root health endpoint for serverless health checks
@app.get("/health")
async def root_health():
    """Simple health check endpoint at the root level."""
    return {"status": "ok"}

# --- Event Handlers ---

@app.on_event("startup")
async def startup_event() -> None:
    """
    FastAPI startup event handler that initializes the OpenAI client if credentials are available.
    
    This function:
    1. Checks for the OPENAI_API_KEY environment variable
    2. Attempts to initialize the OpenAI client if the key is available
    3. Logs the status of the OpenAI client configuration
    
    The OpenAI client is initialized lazily, allowing the app to run without OpenAI installed
    if those features aren't being used.
    """
    global client
    logger.info("Nurses API starting up")
    
    # Create database tables if they don't exist (for SQLite)
    # For PostgreSQL, we use Alembic migrations.
    # Skip database initialization in serverless environments if it fails
    if "sqlite" in settings.DATABASE_URL:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created for SQLite.")
        except Exception as e:
            logger.warning(f"Could not initialize database: {e}. This is normal in serverless environments.")

    # Initialize OpenAI client if key is available
    if settings.OPENAI_API_KEY:
        try:
            # lazy import so app can run without openai installed
            from openai import OpenAI as OpenAIClient

            client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client configured successfully")
        except Exception as e:
            client = None
            logger.warning(
                "OpenAI package not installed; set OPENAI_API_KEY and install 'openai' to enable client.",
                extra={"error": str(e)}
            )
    else:
        logger.warning("OPENAI_API_KEY not set; OpenAI calls will fail if used.")
    
    # Check Redis connection if REDIS_URL is set
    if settings.REDIS_URL:
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            logger.info(f"Redis connection successful: {settings.REDIS_URL}")
        except ImportError:
            logger.warning("Redis package not installed; install 'redis' to enable Redis caching")
        except Exception as e:
            logger.error(
                f"Failed to connect to Redis: {str(e)}",
                extra={"redis_url": settings.REDIS_URL, "error": str(e)},
                exc_info=True
            )

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    FastAPI shutdown event handler that performs cleanup actions when the application stops.
    
    This function currently includes:
    - Closing the Redis connection pool, if it was created.
    
    More actions can be added here in the future as needed.
    """
    logger.info("Nurses API shutting down")
    # Add any cleanup actions here

