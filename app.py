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
# For now, make OAuth2 authentication optional to ensure backward compatibility
# dependencies=[Depends(get_current_user)] is commented out until OAuth is fully configured
api_router = APIRouter(
    prefix="/api/v1",
    # dependencies=[Depends(get_current_user)]  # Temporarily disabled for backward compatibility
)

# A separate, unprotected router for authentication
unprotected_router = APIRouter(prefix="/api/v1")

# --- Middleware Configuration ---

# Define paths exempt from authentication and rate limiting
# Health and metrics are still public.
PUBLIC_PATHS: set[str] = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", "/health", "/metrics"}

# Add security headers middleware (should be one of the first)
app.add_middleware(SecurityHeadersMiddleware)

# Add request ID and logging middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware, logger=logger)

# Set up metrics
setup_metrics(app)

# Add rate limiting
app.add_middleware(
    RateLimiter,
    requests_per_minute=settings.RATE_LIMIT_PER_MINUTE,
    exempt_paths=PUBLIC_PATHS
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

# Include the main versioned router into the app
app.include_router(api_router)
app.include_router(unprotected_router)

# --- Authentication Middleware (FALLBACK) ---
# Add back a simplified version of the old bearer token middleware
# for backward compatibility during the transition to OAuth2
@app.middleware("http")
async def authentication_middleware(request: Request, call_next: Callable) -> Response:
    path = request.url.path
    
    # Let exempt paths and OPTIONS requests pass through
    if request.method == "OPTIONS" or path in PUBLIC_PATHS or path.startswith("/static"):
        return await call_next(request)
    
    # Check for bearer token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header with Bearer token is required"},
        )
    
    token = auth_header.split(" ")[1]
    # Check against the default API key (now that API_BEARER is optional)
    if settings.API_BEARER and token != settings.API_BEARER:
        return JSONResponse(status_code=403, content={"detail": "Invalid API token"})
    
    return await call_next(request)

# --- Event Handlers ---

@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize services on application startup.
    """
    global client
    logger.info("Nurses API starting up")
    
    # Create database tables if they don't exist (for SQLite)
    # For PostgreSQL, we use Alembic migrations.
    if "sqlite" in settings.DATABASE_URL:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created for SQLite.")
        except Exception as e:
            logger.error(f"Failed to create database tables: {str(e)}", exc_info=True)
            # Don't crash the app if DB init fails - we can still function without database

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

