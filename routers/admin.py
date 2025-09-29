"""
Admin Router - AI Nurse Florence
Phase 3.4.3: Admin Endpoints

Administrator interface for user management with role-based access control.
Following Router Organization pattern and API Design Standards from coding instructions.

This is the root-level router that imports from src.routers.admin
"""

try:
    from src.routers.admin import router
    logger = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Admin router imported successfully from src.routers.admin")
    except:
        pass
except ImportError as e:
    # Fallback router if src router not available
    from fastapi import APIRouter, HTTPException, status
    from datetime import datetime
    
    router = APIRouter(
        prefix="/admin",
        tags=["admin"],
        responses={
            501: {"description": "Admin functionality not implemented"},
        }
    )
    
    @router.get("/test")
    async def admin_not_implemented():
        return {
            "message": "Admin functionality not yet implemented",
            "timestamp": datetime.utcnow().isoformat(),
            "status": "fallback_router"
        }
    
    logger = None
    try:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Using fallback admin router - src.routers.admin not available")
    except:
        pass
