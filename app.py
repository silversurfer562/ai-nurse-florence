from fastapi import FastAPI, Request
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

# Routers (import existing project routers)
from routers import (
    healthcheck,
    disease,
    pubmed,
    trials,
    medlineplus,
    summarize,
    patient_education,
    readability,
)

load_dotenv()

# Set up logger
logger = get_logger(__name__)

API_BEARER = os.getenv("API_BEARER", "").strip()
CORS_ORIGINS = [o for o in os.getenv("CORS_ORIGINS", "").split(",") if o]

# Read OpenAI key from env (do NOT hardcode secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

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

# Add middleware
app.add_middleware(RequestIdMiddleware)
app.add_middleware(LoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Set up metrics
setup_metrics(app)

# Add rate limiting
app.add_middleware(
    RateLimiter,
    requests_per_minute=RATE_LIMIT_PER_MINUTE,
    exempt_paths=EXEMPT_PATHS
)

# CORS
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount routers
app.include_router(healthcheck.router)
app.include_router(disease.router)
app.include_router(pubmed.router)
app.include_router(trials.router)
app.include_router(medlineplus.router)
app.include_router(summarize.router)
app.include_router(patient_education.router)
app.include_router(readability.router)

# Paths exempt from bearer token authentication
load_dotenv()

# Set up logger
logger = get_logger(__name__)

API_BEARER = os.getenv("API_BEARER", "").strip()
CORS_ORIGINS = [o for o in os.getenv("CORS_ORIGINS", "").split(",") if o]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Load rate limit configuration from environment
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Paths exempt from bearer token authentication
EXEMPT_PATHS: set[str] = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", "/health", "/metrics"}


@app.middleware("http")
async def bearer_middleware(request: Request, call_next: Callable[[Request], Response]) -> JSONResponse | Response:
    """
    Middleware to enforce bearer token authentication for all non-exempt paths.
    
    Args:
        request: The incoming request
        call_next: The next middleware or endpoint handler
        
    Returns:
        The response from the next handler if authentication passes, 
        or a 401 Unauthorized response if it fails
    """
    path = str(request.url.path)
    if request.method == "OPTIONS" or path in EXEMPT_PATHS or path.startswith("/static"):
        return await call_next(request)

    if not API_BEARER:
        return await call_next(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    token = auth.split(" ", 1)[1].strip()
    if token != API_BEARER:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


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
    
    # Initialize OpenAI client if key is available
    if OPENAI_API_KEY:
        try:
            # lazy import so app can run without openai installed
            from openai import OpenAI as OpenAIClient

            client = OpenAIClient(api_key=OPENAI_API_KEY)
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
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            logger.info(f"Redis connection successful: {redis_url}")
        except ImportError:
            logger.warning("Redis package not installed; install 'redis' to enable Redis caching")
        except Exception as e:
            logger.error(
                f"Failed to connect to Redis: {str(e)}",
                extra={"redis_url": redis_url, "error": str(e)},
                exc_info=True
            )

