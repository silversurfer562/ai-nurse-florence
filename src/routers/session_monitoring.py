"""
Session Monitoring Router - AI Nurse Florence
Phase 3.4.4: Session Cleanup

Admin interface for session monitoring and cleanup management.
Following Router Organization pattern and API Design Standards from coding instructions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Import utilities following conditional imports pattern
try:
    from src.utils.auth_dependencies import get_current_user
    from src.utils.api_responses import create_success_response, create_error_response
    from src.services.session_cleanup import (
        session_cleanup_service,
        cleanup_expired_sessions,
        get_session_statistics,
        start_session_cleanup,
        stop_session_cleanup,
        get_cleanup_service_status
    )
    _has_dependencies = True
except ImportError as e:
    _has_dependencies = False
    
    # Mock functions for testing
    async def get_current_user() -> Dict[str, Any]:
        return {"user_id": "mock_admin", "role": "admin"}
    
    def create_success_response(data: Any) -> Dict[str, Any]:
        return {"success": True, "data": data}
    
    def create_error_response(message: str, status_code: int = 500, details: Optional[Dict] = None) -> Dict[str, Any]:
        return {"success": False, "message": message, "details": details}
    
    # Mock session cleanup functions
    async def cleanup_expired_sessions():
        return {"expired_sessions_removed": 0, "cleanup_time": datetime.utcnow()}
    
    async def get_session_statistics():
        return {"total_sessions": 0, "active_sessions": 0}
    
    async def start_session_cleanup():
        pass
    
    async def stop_session_cleanup():
        pass
    
    def get_cleanup_service_status():
        return {"is_running": False, "database_available": False}

# Router setup following router organization patterns
router = APIRouter(
    prefix="/sessions",
    tags=["session-monitoring"],
    responses={
        401: {"description": "Authentication failed"},
        403: {"description": "Insufficient permissions - admin role required"},
        500: {"description": "Internal server error"}
    }
)

# Helper function to check admin permissions
def require_admin_role(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency to require admin role for session management."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator permissions required for session management"
        )
    return current_user

# Phase 3.4.4: Session monitoring and cleanup endpoints

@router.get(
    "/statistics",
    summary="Get session statistics",
    description="Get comprehensive session statistics including active, expired, and cleanup metrics"
)
async def get_session_stats(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get comprehensive session statistics.
    Requires admin role.
    Phase 3.4.4: Session monitoring and cleanup.
    """
    try:
        stats = await get_session_statistics()
        
        return create_success_response({
            "session_statistics": stats,
            "requested_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get session statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/cleanup",
    summary="Manual session cleanup",
    description="Manually trigger cleanup of expired sessions"
)
async def manual_session_cleanup(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Manually trigger cleanup of expired sessions.
    Requires admin role.
    """
    try:
        cleanup_stats = await cleanup_expired_sessions()
        
        # Convert cleanup stats to dict if it's a dataclass
        if hasattr(cleanup_stats, '__dict__'):
            stats_dict = {
                "cleanup_time": cleanup_stats.cleanup_time.isoformat(),
                "expired_sessions_removed": cleanup_stats.expired_sessions_removed,
                "total_sessions_before": cleanup_stats.total_sessions_before,
                "total_sessions_after": cleanup_stats.total_sessions_after,
                "cleanup_duration_seconds": cleanup_stats.cleanup_duration_seconds,
                "errors": cleanup_stats.errors,
                "success": len(cleanup_stats.errors) == 0
            }
        else:
            # Handle mock or dict response
            stats_dict = cleanup_stats
        
        return create_success_response({
            "cleanup_results": stats_dict,
            "triggered_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Manual session cleanup failed",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/cleanup/history",
    summary="Get cleanup history",
    description="Get history of session cleanup operations"
)
async def get_cleanup_history(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of entries to return"),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get history of session cleanup operations.
    Requires admin role.
    """
    try:
        if _has_dependencies:
            history = await session_cleanup_service.get_cleanup_history(limit=limit)
        else:
            # Mock history for testing
            history = [
                {
                    "cleanup_time": datetime.utcnow().isoformat(),
                    "expired_sessions_removed": 0,
                    "success": True,
                    "errors": []
                }
            ]
        
        return create_success_response({
            "cleanup_history": history,
            "total_entries": len(history),
            "limit": limit,
            "requested_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get cleanup history",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/cleanup/start",
    summary="Start background cleanup",
    description="Start the background session cleanup task"
)
async def start_background_cleanup(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Start the background session cleanup task.
    Requires admin role.
    """
    try:
        await start_session_cleanup()
        
        return create_success_response({
            "message": "Background session cleanup started",
            "started_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to start background cleanup",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.post(
    "/cleanup/stop",
    summary="Stop background cleanup",
    description="Stop the background session cleanup task"
)
async def stop_background_cleanup(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Stop the background session cleanup task.
    Requires admin role.
    """
    try:
        await stop_session_cleanup()
        
        return create_success_response({
            "message": "Background session cleanup stopped",
            "stopped_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to stop background cleanup",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/cleanup/status",
    summary="Get cleanup service status",
    description="Get current status of the session cleanup service"
)
async def get_cleanup_status(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get current status of the session cleanup service.
    Requires admin role.
    """
    try:
        status_info = get_cleanup_service_status()
        
        return create_success_response({
            "service_status": status_info,
            "requested_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get service status",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

@router.get(
    "/active",
    summary="Get active sessions",
    description="Get list of currently active sessions (admin view)"
)
async def get_active_sessions(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of sessions to return"),
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """
    Get list of currently active sessions.
    Requires admin role.
    Note: This provides aggregated statistics only, no personal information.
    """
    try:
        # Get session statistics
        stats = await get_session_statistics()
        
        # Extract active session info (no personal data)
        active_info = {
            "active_session_count": stats.get("database", {}).get("active_sessions", 0),
            "total_session_count": stats.get("database", {}).get("total_sessions", 0),
            "users_with_active_sessions": stats.get("database", {}).get("users_with_sessions", 0),
            "redis_session_count": stats.get("redis", {}).get("redis_sessions", 0),
            "last_cleanup": stats.get("cleanup", {}).get("last_cleanup"),
            "service_running": stats.get("service", {}).get("is_running", False)
        }
        
        return create_success_response({
            "active_session_summary": active_info,
            "note": "Aggregated statistics only - no personal information displayed",
            "limit": limit,
            "requested_by": current_user["user_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
        })
        
    except Exception as e:
        return create_error_response(
            message="Failed to get active session information",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error": str(e)}
        )

# Test endpoint for session monitoring functionality

@router.get(
    "/test",
    summary="Test session monitoring",
    description="Test endpoint to verify session monitoring system is working"
)
async def test_session_monitoring(
    current_user: Dict[str, Any] = Depends(require_admin_role)
):
    """Test session monitoring system functionality."""
    service_status = get_cleanup_service_status()
    
    return create_success_response({
        "message": "Session monitoring system operational",
        "admin_user": current_user["user_id"],
        "service_status": service_status,
        "dependencies_available": _has_dependencies,
        "timestamp": datetime.utcnow().isoformat(),
        "educational_notice": "For educational purposes only - not medical advice. No PHI stored."
    })
