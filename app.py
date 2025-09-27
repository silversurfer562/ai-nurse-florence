"""
AI Nurse Florence - FastAPI Healthcare AI Assistant
Following copilot-instructions.md Architecture Patterns
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Core utilities following Conditional Imports Pattern
try:
    from src.utils.config import get_settings, is_feature_enabled
    from src.utils.middleware import (
        SecurityHeadersMiddleware,
        RequestIdMiddleware, 
        LoggingMiddleware
    )
    from src.utils.exceptions import ServiceException, ExternalServiceException
    _has_core_utils = True
except ImportError as e:
    logging.error(f"Core utilities unavailable: {e}")
    _has_core_utils = False
    raise

# Optional middleware following Conditional Imports Pattern
try:
    from src.utils.rate_limit import RateLimiter
    _has_rate_limiting = True
except ImportError:
    _has_rate_limiting = False
    logging.warning("Rate limiting unavailable - continuing without")

try:
    from prometheus_fastapi_instrumentator import Instrumentator
    _has_metrics = True
except ImportError:
    _has_metrics = False
    logging.warning("Prometheus metrics unavailable - continuing without")

# Router imports following Router Organization pattern
AVAILABLE_ROUTERS = {}

# Core routers (always available)
try:
    from src.routers.health import router as health_router
    AVAILABLE_ROUTERS['health'] = health_router
except ImportError:
    logging.warning("Health router unavailable")

try:
    from src.routers.auth import router as auth_router
    AVAILABLE_ROUTERS['auth'] = auth_router
except ImportError:
    logging.warning("Auth router unavailable")

# Medical Information routers (Conditional Imports Pattern)
try:
    from src.routers.disease import router as disease_router
    from src.routers.literature import router as literature_router
    from src.routers.clinical_trials import router as clinical_trials_router
    
    AVAILABLE_ROUTERS.update({
        'disease': disease_router,
        'literature': literature_router,
        'clinical_trials': clinical_trials_router
    })
    logging.info("Medical Information API: Available")
except ImportError as e:
    logging.warning(f"Medical Information API unavailable: {e}")

# Wizard routers (Conditional Imports Pattern) 
try:
    from src.routers.wizards.sbar_wizard import router as sbar_wizard_router
    from src.routers.wizards.treatment_plan_wizard import router as treatment_plan_router
    
    AVAILABLE_ROUTERS.update({
        'sbar_wizard': sbar_wizard_router,
        'treatment_plan': treatment_plan_router
    })
    logging.info("Clinical Wizards: Available")
except ImportError as e:
    logging.warning(f"Clinical Wizards unavailable: {e}")

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management following copilot-instructions.md patterns."""
    
    # Startup
    logging.info("AI Nurse Florence starting up...")
    
    # Initialize services following Service Layer Architecture
    try:
        from src.services import get_available_services
        services = get_available_services()
        logging.info(f"Services initialized: {services}")
    except ImportError:
        logging.warning("Service registry unavailable - continuing with limited functionality")
    
    # Log available routers
    logging.info(f"Available routers: {list(AVAILABLE_ROUTERS.keys())}")
    
    # Initialize metrics if available
    if _has_metrics:
        instrumentator = Instrumentator()
        instrumentator.instrument(app).expose(app)
        logging.info("Prometheus metrics enabled")
    
    yield
    
    # Shutdown
    logging.info("AI Nurse Florence shutting down...")

# Initialize FastAPI app following API Design Standards
def create_app() -> FastAPI:
    """Create FastAPI application following copilot-instructions.md patterns."""
    
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Healthcare AI assistant providing evidence-based medical information for nurses and healthcare professionals. Educational use only - not medical advice. No PHI stored.",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
        openapi_tags=[
            {"name": "health", "description": "Health check and system status"},
            {"name": "auth", "description": "Authentication and authorization"},
            {"name": "disease-information", "description": "Disease lookup and medical information"},
            {"name": "medical-literature", "description": "PubMed literature search"},
            {"name": "clinical-trials", "description": "Clinical trials discovery"},
            {"name": "clinical-wizards", "description": "Multi-step clinical workflows"},
        ]
    )
    
    # Security & Middleware Stack following critical order from copilot-instructions.md
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    # Rate limiting (conditional)
    if _has_rate_limiting and settings.ENABLE_RATE_LIMITING:
        rate_limiter = RateLimiter(
            requests_per_minute=60,
            exempt_paths=["/docs", "/redoc", "/openapi.json", "/api/v1/health"]
        )
        app.add_middleware(rate_limiter)
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Mount static files
    try:
        app.mount("/static", StaticFiles(directory="src/static"), name="static")
    except Exception as e:
        logging.warning(f"Static files unavailable: {e}")
    
    # Register available routers following Router Organization pattern
    for router_name, router in AVAILABLE_ROUTERS.items():
        try:
            app.include_router(router)
            logging.info(f"Router registered: {router_name}")
        except Exception as e:
            logging.error(f"Failed to register router {router_name}: {e}")
    
    # Global exception handlers following Error Handling pattern
    @app.exception_handler(ServiceException)
    async def service_exception_handler(request: Request, exc: ServiceException):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": f"Service error: {exc.message}",
                "service": exc.service_name,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    @app.exception_handler(ExternalServiceException)
    async def external_service_exception_handler(request: Request, exc: ExternalServiceException):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": f"External service unavailable: {exc.message}",
                "service": exc.service_name,
                "fallback_available": exc.fallback_available,
                "request_id": getattr(request.state, 'request_id', None)
            }
        )
    
    return app

# Create application instance
app = create_app()

# Health check endpoint (always available)
@app.get("/api/v1/health", tags=["health"])
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check following copilot-instructions.md patterns.
    
    Returns:
        - System status and version
        - Available services and routers
        - Configuration status
        - Dependency health
    """
    settings = get_settings()
    
    # Check service availability
    try:
        from src.services import get_available_services
        services = get_available_services()
    except ImportError:
        services = {"error": "Service registry unavailable"}
    
    health_data = {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "services": services,
        "routers": list(AVAILABLE_ROUTERS.keys()),
        "features": {
            "rate_limiting": _has_rate_limiting and settings.ENABLE_RATE_LIMITING,
            "metrics": _has_metrics,
            "live_services": settings.USE_LIVE_SERVICES,
            "openai": is_feature_enabled("openai"),
            "redis": is_feature_enabled("redis")
        },
        "banner": settings.EDUCATIONAL_BANNER
    }
    
    return health_data

if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
