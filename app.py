"""
AI Nurse Florence - Healthcare AI Assistant FastAPI Application
Educational use only - not medical advice. No PHI stored.
Following Service Layer Architecture with Conditional Imports Pattern
"""

from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
import logging
from pathlib import Path
import uuid
from datetime import datetime

from src.utils.middleware import setup_middleware
from src.routers.disease import router as disease_router
from src.routers.literature import router as literature_router  
from src.routers.clinical_trials import router as clinical_trials_router

# Configure logging for Railway deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Educational disclaimer banner
EDU_BANNER = "Draft for clinician review — not medical advice. No PHI stored."

# Application metadata following Configuration Management
app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI assistant providing evidence-based medical information for nurses and healthcare professionals. Educational use only - not medical advice.",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup Security & Middleware Stack following critical order from copilot-instructions.md
setup_middleware(app)

# Request ID middleware following Security & Middleware Stack
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Logging middleware following Middleware Stack Order
@app.middleware("http") 
async def logging_middleware(request: Request, call_next):
    """Structured request/response logging"""
    start_time = datetime.utcnow()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path} - ID: {getattr(request.state, 'request_id', 'unknown')}")
    
    response = await call_next(request)
    
    # Log response
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Response: {response.status_code} - Duration: {duration:.3f}s")
    
    return response

# Health check endpoints (unprotected routes)
@app.get("/health", tags=["health"])
def health_check():
    """Railway health check endpoint - unprotected route"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "AI Nurse Florence API operational"
    }

@app.get("/api/v1/health", tags=["health"])
def api_health_check():
    """API health check with dependency status"""
    # Check service availability
    services_status = {}
    
    # Test database connection (conditional)
    try:
        from utils.database import test_connection
        services_status["database"] = "healthy" if test_connection() else "unhealthy"
    except ImportError:
        services_status["database"] = "not configured"
    
    # Test Redis cache (conditional)
    try:
        from utils.redis_cache import test_redis
        services_status["redis"] = "healthy" if test_redis() else "unhealthy"
    except ImportError:
        services_status["redis"] = "not configured"
    
    return {
        "status": "healthy",
        "version": "2.1.0",
        "services": services_status,
        "banner": EDU_BANNER
    }

# Root endpoints for frontend serving
@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve frontend application"""
    try:
        static_path = Path("static/index.html")
        if static_path.exists():
            return FileResponse("static/index.html")
        else:
            # Fallback HTML if static files not available
            return HTMLResponse("""
            <!DOCTYPE html>
            <html>
            <head><title>AI Nurse Florence</title></head>
            <body>
                <h1>AI Nurse Florence</h1>
                <p>Healthcare AI Assistant API</p>
                <p><a href="/docs">API Documentation</a></p>
                <p><em>Educational use only - not medical advice</em></p>
            </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        return HTMLResponse("<h1>AI Nurse Florence API</h1><p>Visit <a href='/docs'>/docs</a> for API documentation</p>")

@app.get("/app", response_class=HTMLResponse)
def read_app():
    """Alternative frontend endpoint"""
    return read_root()

# Mount static files (conditional)
try:
    if Path("static").exists():
        app.mount("/static", StaticFiles(directory="static"), name="static")
        logger.info("✅ Static files mounted")
except Exception as e:
    logger.warning(f"⚠️ Static files not mounted: {e}")

# Debug endpoints for Railway troubleshooting
@app.get("/debug/status", tags=["debug"])
def debug_status():
    """Debug endpoint showing loaded routers and system status"""
    return {
        "version": "2.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "port": os.getenv("PORT", "8000"),
        "routers_loaded": [route.tags[0] if route.tags else "untagged" for route in app.routes if hasattr(route, 'tags')],
        "files_exist": {
            "requirements.txt": Path("requirements.txt").exists(),
            "routers_init": Path("routers/__init__.py").exists(),
            "wizards_init": Path("routers/wizards/__init__.py").exists()
        },
        "environment_vars": {
            "PORT": os.getenv("PORT", "Not set"),
            "DATABASE_URL": "Set" if os.getenv("DATABASE_URL") else "Not set",
            "REDIS_URL": "Set" if os.getenv("REDIS_URL") else "Not set",
            "OPENAI_API_KEY": "Set" if os.getenv("OPENAI_API_KEY") else "Not set"
        }
    }

@app.get("/info", tags=["info"])
def app_info():
    """Application information endpoint"""
    return {
        "name": "AI Nurse Florence",
        "version": "2.1.0",
        "description": "Healthcare AI assistant for nurses and healthcare professionals",
        "banner": EDU_BANNER,
        "message": "Educational use only - not medical advice. No PHI stored."
    }

# API Router for protected routes following Router Organization
api_router = APIRouter(prefix="/api/v1", tags=["api"])

# Core medical services with Conditional Imports Pattern
logger.info("=== AI NURSE FLORENCE STARTUP ===")
logger.info("Loading routers with Conditional Imports Pattern...")

routers_loaded = []
routers_failed = []

# Disease information service
try:
    api_router.include_router(disease_router, prefix="/disease", tags=["disease"])
    routers_loaded.append("disease")
    logger.info("✅ Disease router loaded")
except ImportError as e:
    routers_failed.append(f"disease: {e}")
    logger.warning(f"⚠️ Disease router failed: {e}")

# Literature search service  
try:
    api_router.include_router(literature_router, prefix="/literature", tags=["literature"])
    routers_loaded.append("literature")
    logger.info("✅ Literature router loaded")
except ImportError as e:
    routers_failed.append(f"literature: {e}")
    logger.warning(f"⚠️ Literature router failed: {e}")

# Clinical trials service
try:
    api_router.include_router(clinical_trials_router, prefix="/trials", tags=["trials"]) 
    routers_loaded.append("trials")
    logger.info("✅ Clinical trials router loaded")
except ImportError as e:
    routers_failed.append(f"trials: {e}")
    logger.warning(f"⚠️ Clinical trials router failed: {e}")

# Patient education service
try:
    from routers.patient_education import router as education_router
    api_router.include_router(education_router, prefix="/patient-education", tags=["education"])
    routers_loaded.append("education")  
    logger.info("✅ Patient education router loaded")
except ImportError as e:
    routers_failed.append(f"education: {e}")
    logger.warning(f"⚠️ Patient education router failed: {e}")

# Text summarization service
try:
    from routers.summarize import router as summarize_router
    api_router.include_router(summarize_router, prefix="/summarize", tags=["summarize"])
    routers_loaded.append("summarize")
    logger.info("✅ Summarize router loaded")
except ImportError as e:
    routers_failed.append(f"summarize: {e}")
    logger.warning(f"⚠️ Summarize router failed: {e}")

# Wizard Pattern Implementation - Multi-step workflows
WIZARDS_AVAILABLE = False
wizard_routers_loaded = []

logger.info("Loading wizard routers following Wizard Pattern Implementation...")

# Treatment plan wizard (your original target endpoint)
try:
    from routers.wizards.treatment_plan import router as treatment_plan_wizard_router
    api_router.include_router(treatment_plan_wizard_router, prefix="/wizards/treatment-plan", tags=["wizards", "treatment-plan"])
    wizard_routers_loaded.append("treatment-plan")
    WIZARDS_AVAILABLE = True
    logger.info("✅ Treatment plan wizard loaded - YOUR ORIGINAL ENDPOINT AVAILABLE!")
except ImportError as e:
    routers_failed.append(f"treatment-plan-wizard: {e}")
    logger.warning(f"⚠️ Treatment plan wizard failed: {e}")

# SBAR report wizard  
try:
    from routers.wizards.sbar_report import router as sbar_wizard_router
    api_router.include_router(sbar_wizard_router, prefix="/wizards/sbar", tags=["wizards", "sbar"])
    wizard_routers_loaded.append("sbar")
    WIZARDS_AVAILABLE = True
    logger.info("✅ SBAR wizard loaded")
except ImportError as e:
    routers_failed.append(f"sbar-wizard: {e}")
    logger.warning(f"⚠️ SBAR wizard failed: {e}")

# Patient education wizard
try:
    from routers.wizards.patient_education import router as patient_education_wizard_router
    api_router.include_router(patient_education_wizard_router, prefix="/wizards/patient-education", tags=["wizards", "patient-education"])
    wizard_routers_loaded.append("patient-education")
    WIZARDS_AVAILABLE = True
    logger.info("✅ Patient education wizard loaded")
except ImportError as e:
    routers_failed.append(f"patient-education-wizard: {e}")
    logger.warning(f"⚠️ Patient education wizard failed: {e}")

# Clinical trials wizard
try:
    from routers.wizards.clinical_trials import router as clinical_trials_wizard_router
    api_router.include_router(clinical_trials_wizard_router, prefix="/wizards/clinical-trials", tags=["wizards", "clinical-trials"])
    wizard_routers_loaded.append("clinical-trials")
    WIZARDS_AVAILABLE = True
    logger.info("✅ Clinical trials wizard loaded")
except ImportError as e:
    routers_failed.append(f"clinical-trials-wizard: {e}")
    logger.warning(f"⚠️ Clinical trials wizard failed: {e}")

# Disease search wizard
try:
    from routers.wizards.disease_search import router as disease_search_wizard_router
    api_router.include_router(disease_search_wizard_router, prefix="/wizards/disease-search", tags=["wizards", "disease-search"])
    wizard_routers_loaded.append("disease-search")
    WIZARDS_AVAILABLE = True
    logger.info("✅ Disease search wizard loaded")
except ImportError as e:
    routers_failed.append(f"disease-search-wizard: {e}")
    logger.warning(f"⚠️ Disease search wizard failed: {e}")

# Include main API router with all loaded endpoints
app.include_router(api_router)

# Medical Information Routers
api_router.include_router(disease_router)
api_router.include_router(literature_router)
api_router.include_router(clinical_trials_router)

# Startup summary following Service Layer Architecture
logger.info("=== STARTUP SUMMARY ===")
logger.info(f"Core routers loaded: {routers_loaded}")
logger.info(f"Wizard routers loaded: {wizard_routers_loaded}")  
logger.info(f"Wizards available: {WIZARDS_AVAILABLE}")
logger.info(f"Failed imports: {len(routers_failed)}")

if routers_failed:
    logger.warning("Failed router imports (graceful degradation):")
    for failure in routers_failed:
        logger.warning(f"  - {failure}")

total_expected_routes = len(routers_loaded) * 3 + len(wizard_routers_loaded) * 8  # Estimated
logger.info(f"Expected routes: ~{total_expected_routes}")

if WIZARDS_AVAILABLE:
    logger.info("🎯 TREATMENT PLAN WIZARD ENDPOINTS AVAILABLE:")
    logger.info("  - POST /api/v1/wizards/treatment-plan/start")
    logger.info("  - POST /api/v1/wizards/treatment-plan/interventions (YOUR ORIGINAL TARGET)")
    logger.info("  - POST /api/v1/wizards/treatment-plan/generate")

# OpenAI client initialization (conditional)
try:
    from services.openai_client import get_openai_client
    openai_client = get_openai_client()
    if openai_client:
        logger.info("✅ OpenAI client configured")
    else:
        logger.info("⚠️ OpenAI client not configured (API key missing)")
except ImportError:
    logger.warning("⚠️ OpenAI service not available")

# Cache initialization (conditional) following Caching Strategy
try:
    from utils.redis_cache import test_redis
    if test_redis():
        logger.info("✅ Redis cache available")
    else:
        logger.info("⚠️ Redis cache not available - using in-memory fallback")
except ImportError:
    logger.info("⚠️ Cache service not configured")

logger.info("=== AI NURSE FLORENCE READY ===")
logger.info(f"Version: 2.1.0")
logger.info(f"Educational disclaimer: {EDU_BANNER}")
logger.info("Health endpoint: /health")
logger.info("API documentation: /docs")

# Error handlers following Error Handling patterns
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Standardized HTTP exception handling"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code,
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handling with logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"Unhandled exception - Request ID: {request_id} - {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )

# Development server configuration
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"Starting development server on {host}:{port}")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
