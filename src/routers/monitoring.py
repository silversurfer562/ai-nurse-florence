"""
Production Monitoring Router for AI Nurse Florence
Provides endpoints for monitoring application health and performance
"""

import logging
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from src.utils.monitoring import (
    get_monitoring_data,
    performance_monitor,
    alert_manager,
    SystemMonitor,
    HealthChecker
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/monitoring",
    tags=["monitoring"],
    responses={404: {"description": "Not found"}},
)


@router.get("/status")
async def get_monitoring_status():
    """Get comprehensive application monitoring status"""
    try:
        monitoring_data = get_monitoring_data()
        return JSONResponse(content=monitoring_data)
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve monitoring data")


@router.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        metrics = performance_monitor.get_metrics()
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "performance": metrics
        })
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")


@router.get("/system")
async def get_system_metrics():
    """Get system resource usage metrics"""
    try:
        metrics = SystemMonitor.get_system_metrics()
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "system": metrics
        })
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")


@router.get("/alerts")
async def get_current_alerts():
    """Get current system alerts based on thresholds"""
    try:
        monitoring_data = get_monitoring_data()
        alerts = monitoring_data.get("alerts", [])
        
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "alerts": alerts,
            "alert_count": len(alerts),
            "thresholds": alert_manager.alert_thresholds
        })
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")


@router.get("/health/detailed")
async def get_detailed_health():
    """Get comprehensive health check including all services"""
    try:
        health_checker = HealthChecker()
        health_data = await health_checker.comprehensive_health_check()
        
        return JSONResponse(content=health_data)
    except Exception as e:
        logger.error(f"Failed to get detailed health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve detailed health information")


@router.get("/health/external")
async def get_external_services_health():
    """Check health of external services only"""
    try:
        health_checker = HealthChecker()
        services = health_checker.check_external_services()
        
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "external_services": services
        })
    except Exception as e:
        logger.error(f"Failed to check external services: {e}")
        raise HTTPException(status_code=500, detail="Failed to check external services")


@router.post("/alerts/test")
async def test_alert_system():
    """Test the alert system by generating sample alerts"""
    try:
        # Create test metrics that would trigger alerts
        test_metrics = {
            "performance": {
                "error_rate_percent": 10.0,  # Above 5% threshold
                "average_response_time_ms": 3000,  # Above 2000ms threshold
            },
            "system": {
                "cpu_percent": 85,  # Above 80% threshold
                "memory_percent": 90,  # Above 85% threshold
                "disk_percent": 95  # Above 90% threshold
            }
        }
        
        alerts = alert_manager.check_alerts(test_metrics)
        
        return JSONResponse(content={
            "timestamp": datetime.now().isoformat(),
            "test_alerts": alerts,
            "test_metrics": test_metrics,
            "message": "Alert system test completed"
        })
    except Exception as e:
        logger.error(f"Failed to test alert system: {e}")
        raise HTTPException(status_code=500, detail="Failed to test alert system")


@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Get all monitoring data for dashboard display"""
    try:
        # Get comprehensive monitoring data
        monitoring_data = get_monitoring_data()
        
        # Get external services health
        health_checker = HealthChecker()
        external_services = health_checker.check_external_services()
        
        # Combine into dashboard format
        dashboard_data = {
            "timestamp": datetime.now().isoformat(),
            "overview": {
                "status": "healthy" if monitoring_data.get("alert_count", 0) == 0 else "alerts",
                "alert_count": monitoring_data.get("alert_count", 0),
                "uptime": monitoring_data.get("performance", {}).get("uptime_human", "Unknown")
            },
            "performance": monitoring_data.get("performance", {}),
            "system": monitoring_data.get("system", {}),
            "external_services": external_services,
            "alerts": monitoring_data.get("alerts", [])
        }
        
        return JSONResponse(content=dashboard_data)
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")
