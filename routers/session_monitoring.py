"""
Session Monitoring Router - AI Nurse Florence
Phase 3.4.4: Session Cleanup

This is the root-level router that imports from src.routers.session_monitoring
"""

try:
    from src.routers.session_monitoring import router
    logger = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Session monitoring router imported successfully from src.routers.session_monitoring")
    except:
        pass
except ImportError as e:
    # Fallback router if src router not available
    from fastapi import APIRouter
    from datetime import datetime
    
    router = APIRouter(
        prefix="/sessions",
        tags=["session-monitoring"],
        responses={
            501: {"description": "Session monitoring functionality not implemented"},
        }
    )
    
    @router.get("/test")
    async def session_monitoring_not_implemented():
        return {
            "message": "Session monitoring functionality not yet implemented",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "fallback_router"
        }
    
    logger = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Using fallback session monitoring router - src.routers.session_monitoring not available")
    except:
        pass
