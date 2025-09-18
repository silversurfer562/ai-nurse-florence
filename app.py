"""
Main FastAPI application for the AI Nurse Florence project.

This module sets up the FastAPI application, configures middleware,
includes all routers, and defines startup/shutdown events.
"""
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
from utils.auth import get_current_user
from database import Base, engine

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
from routers.auth import router as auth_router

# Do NOT import OpenAI at module import time; make it optional / lazy
client = None

app = FastAPI(
    title="AI Nurse Florence",
    description="A REST API for Florence, an AI healthcare assistant that helps nurses with patient education and clinical information needs.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "disease",
            "description": "Operations for looking up disease information."
        },
        {
            "name": "summarize",
            "description": "Operations for summarizing text."
        }
    ]
)

# --- Middleware Configuration ---

# Define paths exempt from authentication and rate limiting
# Health and metrics are still public, and auth endpoints should also be exempt.
PUBLIC_PATHS: set[str] = {
    "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", 
    "/health", "/metrics", "/api/v1/auth/"
}

# Add security headers middleware (should be one of the first)
app.add_middleware(SecurityHeadersMiddleware)

# Add request ID and logging middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)

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

# --- API Versioning Router ---
# All API routes will be nested under this single router.
# For now, make OAuth2 authentication optional to ensure backward compatibility
api_router = APIRouter(
    prefix="/api/v1",
    # dependencies=[Depends(get_current_user)]  # Temporarily disabled for backward compatibility
)

# A separate, unprotected router for authentication
unprotected_router = APIRouter(prefix="/api/v1")

# --- Include Routers into the Versioned API Router ---
api_router.include_router(summarize_router)
api_router.include_router(disease_router)
api_router.include_router(patient_education_wizard_router)
api_router.include_router(sbar_report_wizard_router)
api_router.include_router(clinical_trials_wizard_router)
api_router.include_router(disease_search_wizard_router)
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
    if (request.method == "OPTIONS" or 
        path in PUBLIC_PATHS or 
        path.startswith("/static") or 
        path.startswith("/api/v1/auth/")):
        return await call_next(request)
    
    # Check for bearer token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header with Bearer token is required"},
        )
    
    token = auth_header.split(" ")[1]
    
    # If API_BEARER is configured, accept it for backward compatibility
    if settings.API_BEARER and token == settings.API_BEARER:
        return await call_next(request)
    
    # For JWT tokens, we need to validate them properly
    # Rather than doing full JWT validation here (which would duplicate the get_current_user logic),
    # we'll allow JWT-looking tokens to pass through and let the endpoint dependencies handle validation
    try:
        # Simple check if it looks like a JWT (has 3 parts separated by dots)
        parts = token.split('.')
        if len(parts) == 3:
            # Looks like a JWT, let the endpoint handle validation
            return await call_next(request)
    except:
        pass
    
    # If we get here, the token doesn't look like a JWT and doesn't match API_BEARER
    return JSONResponse(status_code=403, content={"detail": "Invalid API token"})

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

    # Initialize OpenAI client if key is available
    if settings.OPENAI_API_KEY:
        try:
            # lazy import so app can run without openai installed
            from openai import OpenAI as OpenAIClient

            client = OpenAIClient(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client configured successfully")
        except Exception as e:
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
            logger.warning("Redis package not installed; install 'redis' to enable redis support.")
        except Exception as e:
            logger.error(
                f"Failed to connect to Redis: {str(e)}",
                extra={"redis_url": settings.REDIS_URL, "error": str(e)},
                exc_info=True
            )

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Clean up resources on application shutdown.
    """
    logger.info("Nurses API shutting down")

# Health check endpoint
@app.get("/health", tags=["health"])
async def health():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}

