"""
Health Check Router - AI Nurse Florence
Following Router Organization pattern for unprotected health endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any
import os

from src.utils.config import get_settings
from src.utils.config import get_base_url
from src.services import get_available_services

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Service healthy"},
        503: {"description": "Service degraded"}
    }
)

@router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Health check endpoint",
    description="Check application health and service availability following coding instructions."
)
async def health_check():
    """
    Health check endpoint following API Design Standards.
    Unprotected route for monitoring and service discovery.
    """
    settings = get_settings()
    
    # Get service status following Service Layer Architecture
    try:
        services = get_available_services()
    except Exception:
        services = {"error": "Service registry unavailable"}
    
    # Count available routes (if app context available)
    route_count = "unknown"
    try:
        # Route counting would be done at app level
        route_count = "available"
    except Exception:
        pass
    
    # Determine mesh index readiness
    try:
        from src.services.mesh_service import get_mesh_index  # type: ignore
        mesh_idx = get_mesh_index()
        mesh_ready = bool(mesh_idx)
    except Exception:
        mesh_ready = False

    health_data = {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "banner": settings.EDUCATIONAL_BANNER,
    "base_url": get_base_url(),
        "environment": "railway" if os.getenv("RAILWAY_ENVIRONMENT") else "development",
        "services": services,
        "configuration": {
            "live_services": settings.USE_LIVE_SERVICES,
            "openai_available": settings.has_openai(),
            "redis_available": settings.has_redis(),
            "rate_limiting": settings.RATE_LIMIT_ENABLED
        },
        "routes": route_count,
        "external_apis": {
            "mydisease": "https://mydisease.info/v1/",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/",
            "clinicaltrials": "https://clinicaltrials.gov/api/v2/"
        }
    }
    # include mesh readiness
    health_data["services"]["mesh_index"] = {"available": mesh_ready}
    
    return health_data

@router.get(
    "/ready",
    summary="Readiness probe",
    description="Kubernetes/Railway readiness probe endpoint."
)
async def readiness_check():
    """Readiness probe for container orchestration."""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@router.get(
    "/live",
    summary="Liveness probe", 
    description="Kubernetes/Railway liveness probe endpoint."
)
async def liveness_check():
    """Liveness probe for container orchestration."""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


# Production Monitoring Endpoints (Step 2 Implementation)
@router.get(
    "/monitoring-status",
    summary="Production monitoring status", 
    description="Get comprehensive monitoring status for production deployment."
)
async def monitoring_status():
    """Production monitoring status endpoint for Step 2 implementation."""
    try:
        # Import monitoring utilities
        from src.utils.monitoring import get_monitoring_data
        
        # Get comprehensive monitoring data
        monitoring_data = get_monitoring_data()
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "monitoring": monitoring_data,
            "step_2_status": "complete"
        }
    except Exception as e:
        return {
            "status": "monitoring_unavailable", 
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "step_2_status": "partial"
        }


@router.get(
    "/monitoring-performance",
    summary="Performance metrics",
    description="Get application performance metrics."
)
async def monitoring_performance():
    """Performance monitoring endpoint."""
    try:
        from src.utils.monitoring import performance_monitor
        
        metrics = performance_monitor.get_metrics()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "performance": metrics
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(), 
            "error": str(e)
        }


@router.get(
    "/monitoring-system",
    summary="System metrics",
    description="Get system resource metrics."
)
async def monitoring_system():
    """System monitoring endpoint."""
    try:
        from src.utils.monitoring import SystemMonitor
        
        metrics = SystemMonitor.get_system_metrics()
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "system": metrics
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@router.get(
    "/monitoring-alerts",
    summary="Alert status",
    description="Get current alert status and thresholds."
)
async def monitoring_alerts():
    """Alert monitoring endpoint."""
    try:
        from src.utils.monitoring import alert_manager, get_monitoring_data
        
        # Get current metrics for alert checking
        monitoring_data = get_monitoring_data()
        alerts = alert_manager.check_alerts(monitoring_data)
        
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "thresholds": alert_manager.alert_thresholds
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
