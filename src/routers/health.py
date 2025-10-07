"""
Health Check Router - AI Nurse Florence
Following Router Organization pattern for unprotected health endpoints
"""

import os
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter

from src.services import get_available_services
from src.utils.config import get_base_url, get_settings

router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Service healthy"},
        503: {"description": "Service degraded"},
    },
)


@router.get(
    "/",
    response_model=Dict[str, Any],
    summary="Health check endpoint",
    description="Check application health and service availability following coding instructions.",
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
            "anthropic_available": settings.has_anthropic(),
            "redis_available": settings.has_redis(),
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "ai_provider": settings.AI_PROVIDER,
            "ai_fallback_enabled": settings.AI_FALLBACK_ENABLED,
        },
        "routes": route_count,
        "external_apis": {
            "mydisease": "https://mydisease.info/v1/",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/",
            "clinicaltrials": "https://clinicaltrials.gov/api/v2/",
        },
    }
    # include mesh readiness
    health_data["services"]["mesh_index"] = {"available": mesh_ready}

    # Add Step 2 Production Monitoring Data
    try:
        # Simple monitoring data that doesn't require complex imports
        import psutil  # type: ignore

        # Basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        health_data["monitoring"] = {
            "step_2_status": "complete",
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
            },
            "application": {
                "uptime_started": "application_started",
                "environment": os.getenv("RAILWAY_ENVIRONMENT", "development"),
                "port": os.getenv("PORT", "8000"),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        health_data["monitoring"] = {
            "step_2_status": "partial",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

    return health_data


@router.get(
    "/ready",
    summary="Readiness probe",
    description="Kubernetes/Railway readiness probe endpoint.",
)
async def readiness_check():
    """Readiness probe for container orchestration."""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}


@router.get(
    "/live",
    summary="Liveness probe",
    description="Kubernetes/Railway liveness probe endpoint.",
)
async def liveness_check():
    """Liveness probe for container orchestration."""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}


# Production Monitoring Endpoints (Step 2 Implementation)
@router.get(
    "/monitoring-status",
    summary="Production monitoring status",
    description="Get comprehensive monitoring status for production deployment.",
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
            "step_2_status": "complete",
        }
    except Exception as e:
        return {
            "status": "monitoring_unavailable",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "step_2_status": "partial",
        }


@router.get(
    "/monitoring-performance",
    summary="Performance metrics",
    description="Get application performance metrics.",
)
async def monitoring_performance():
    """Performance monitoring endpoint."""
    try:
        from src.utils.monitoring import performance_monitor

        metrics = performance_monitor.get_metrics()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "performance": metrics,
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get(
    "/monitoring-system",
    summary="System metrics",
    description="Get system resource metrics.",
)
async def monitoring_system():
    """System monitoring endpoint."""
    try:
        from src.utils.monitoring import SystemMonitor

        metrics = SystemMonitor.get_system_metrics()

        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "system": metrics,
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get(
    "/monitoring-alerts",
    summary="Alert status",
    description="Get current alert status and thresholds.",
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
            "thresholds": alert_manager.alert_thresholds,
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@router.get(
    "/ai",
    summary="AI provider health status",
    description="Get AI provider fallback system health and circuit breaker status.",
)
async def ai_health_check():
    """
    AI provider health check with fallback status.
    Shows circuit breaker states and provider availability.
    """
    try:
        from src.services.ai_provider_fallback import get_ai_service

        ai_service = get_ai_service()
        health_status = ai_service.get_health_status()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "ai_system": health_status,
        }
    except ValueError:
        # No API keys configured - return graceful response without error
        return {
            "status": "not_configured",
            "timestamp": datetime.now().isoformat(),
            "ai_system": {
                "primary_provider": None,
                "fallback_provider": None,
                "providers_available": {
                    "openai": False,
                    "anthropic": False,
                },
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "message": "AI fallback service unavailable",
        }
