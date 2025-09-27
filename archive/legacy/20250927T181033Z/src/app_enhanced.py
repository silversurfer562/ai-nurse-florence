"""
Enhanced FastAPI application with ChatGPT Store integration
Following Service Layer Architecture and Conditional Imports Pattern
"""

import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path following conftest.py pattern
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Conditional imports following coding instructions pattern
try:
    from utils.chatgpt_store import ChatGPTStoreAuth
    from routers.chatgpt_store import router as chatgpt_store_router
    _has_chatgpt_integration = True
except ImportError:
    _has_chatgpt_integration = False

try:
    from utils.swagger_enhancements import get_enhanced_openapi_schema, get_enhanced_swagger_ui_html
    _has_enhanced_ui = True
except ImportError:
    _has_enhanced_ui = False

# Core imports
from utils.config import get_settings
from routers.api import api_router
from utils.middleware import SecurityHeadersMiddleware, RequestIdMiddleware, LoggingMiddleware

settings = get_settings()

def create_application() -> FastAPI:
    """
    Enhanced application factory function
    Following Service Layer Architecture from coding instructions
    """
    
    app = FastAPI(
        title="AI Nurse Florence - Clinical Decision Support System",
        version="2.1.0",
        description="Professional clinical decision support for nursing professionals",
        docs_url=None,  # Custom Swagger UI
        redoc_url=None
    )
    
    # Enhanced OpenAPI schema integration
    if _has_enhanced_ui:
        app.openapi = lambda: get_enhanced_openapi_schema(app)
        
        @app.get("/docs", include_in_schema=False)
        async def custom_swagger_ui_html(req):
            return get_enhanced_swagger_ui_html(req)
    
    # Static file serving for React components (conditional)
    try:
        static_path = Path("src/static")
        if static_path.exists():
            app.mount("/static", StaticFiles(directory="src/static"), name="static")
    except Exception:
        pass  # Graceful degradation if static files unavailable
    
    # Middleware stack following established order from coding instructions
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Router registration following router organization
    app.include_router(api_router)
    
    # ChatGPT Store integration (conditional)
    if _has_chatgpt_integration:
        app.include_router(chatgpt_store_router, prefix="/api/v1")
    
    # Enhanced UI routes (conditional)
    try:
        from routers.ui import router as ui_router
        app.include_router(ui_router)
    except ImportError:
        pass  # UI enhancement optional
    
    # Health check endpoint (unprotected)
    @app.get("/api/v1/health")
    async def health_check():
        """Health check endpoint following API design standards"""
        return {
            "status": "healthy",
            "version": "2.1.0",
            "features": {
                "chatgpt_store": _has_chatgpt_integration,
                "enhanced_ui": _has_enhanced_ui,
                "react_components": static_path.exists() if 'static_path' in locals() else False
            }
        }
    
    return app

# Application instance
app = create_application()

# TODO: Add startup/shutdown event handlers
# TODO: Implement background task initialization
# TODO: Add monitoring and metrics integration
# TODO: Database connection management
