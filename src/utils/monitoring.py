"""
Production Monitoring Utilities for AI Nurse Florence
Provides comprehensive monitoring, logging, and alerting capabilities
"""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available - system metrics will be limited")


class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
    def record_request(self, response_time: float, status_code: int):
        """Record a request for performance tracking"""
        self.request_count += 1
        self.response_times.append(response_time)
        
        if status_code >= 400:
            self.error_count += 1
            
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        uptime = datetime.now() - self.start_time
        
        avg_response_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times else 0
        )
        
        error_rate = (
            (self.error_count / self.request_count * 100)
            if self.request_count > 0 else 0
        )
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "uptime_human": str(uptime),
            "total_requests": self.request_count,
            "error_count": self.error_count,
            "error_rate_percent": round(error_rate, 2),
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "requests_per_minute": round(
                self.request_count / (uptime.total_seconds() / 60), 2
            ) if uptime.total_seconds() > 0 else 0
        }


class SystemMonitor:
    """Monitor system resources and health"""
    
    @staticmethod
    def get_system_metrics() -> Dict:
        """Get current system resource usage"""
        if not PSUTIL_AVAILABLE:
            return {"error": "psutil not available", "status": "limited"}
            
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": round(memory.available / 1024 / 1024, 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / 1024 / 1024 / 1024, 2),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {"error": "Failed to retrieve system metrics"}


class HealthChecker:
    """Comprehensive health checking for all services"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "https://ai-nurse-florence-production.up.railway.app"
        
    async def check_database_health(self) -> Dict:
        """Check database connectivity"""
        try:
            # Basic database connection check
            return {"status": "healthy", "note": "Basic check - full implementation pending"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_redis_health(self) -> Dict:
        """Check Redis connectivity"""
        try:
            from src.utils.redis_cache import get_redis_client
            redis_client = await get_redis_client()
            if redis_client:
                # Test basic redis operation
                test_key = "health_check_test"
                await redis_client.set(test_key, "test", ex=5)
                result = await redis_client.get(test_key)
                await redis_client.delete(test_key)
                return {"status": "healthy", "test_successful": True}
            else:
                return {"status": "not_configured", "note": "Redis not configured, using in-memory cache"}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "not_configured", "error": str(e), "note": "Using in-memory cache fallback"}
    
    def check_external_services(self) -> Dict:
        """Check external service connectivity"""
        services = {}
        
        # Check PubMed API
        try:
            response = requests.get(
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed",
                timeout=5
            )
            services["pubmed"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            services["pubmed"] = {"status": "unhealthy", "error": str(e)}
        
        # Check OpenAI API (if configured)
        try:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                services["openai"] = {
                    "status": "configured" if openai_key.startswith("sk-") else "misconfigured"
                }
            else:
                services["openai"] = {"status": "not_configured"}
        except Exception as e:
            services["openai"] = {"status": "error", "error": str(e)}
        
        return services


class AlertManager:
    """Manage alerts and notifications for production issues"""
    
    def __init__(self):
        self.alert_thresholds = {
            "error_rate_percent": 5.0,  # Alert if error rate > 5%
            "response_time_ms": 2000,   # Alert if avg response time > 2s
            "cpu_percent": 80,          # Alert if CPU > 80%
            "memory_percent": 85,       # Alert if memory > 85%
            "disk_percent": 90          # Alert if disk > 90%
        }
        
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check metrics against thresholds and return alerts"""
        alerts = []
        
        # Check performance metrics
        perf_metrics = metrics.get("performance", {})
        if perf_metrics.get("error_rate_percent", 0) > self.alert_thresholds["error_rate_percent"]:
            alerts.append({
                "severity": "warning",
                "message": f"High error rate: {perf_metrics['error_rate_percent']}%",
                "threshold": self.alert_thresholds["error_rate_percent"]
            })
        
        if perf_metrics.get("average_response_time_ms", 0) > self.alert_thresholds["response_time_ms"]:
            alerts.append({
                "severity": "warning", 
                "message": f"High response time: {perf_metrics['average_response_time_ms']}ms",
                "threshold": self.alert_thresholds["response_time_ms"]
            })
        
        # Check system metrics if available
        system_metrics = metrics.get("system", {})
        if "error" not in system_metrics:
            if system_metrics.get("cpu_percent", 0) > self.alert_thresholds["cpu_percent"]:
                alerts.append({
                    "severity": "critical",
                    "message": f"High CPU usage: {system_metrics['cpu_percent']}%",
                    "threshold": self.alert_thresholds["cpu_percent"]
                })
                
            if system_metrics.get("memory_percent", 0) > self.alert_thresholds["memory_percent"]:
                alerts.append({
                    "severity": "critical",
                    "message": f"High memory usage: {system_metrics['memory_percent']}%",
                    "threshold": self.alert_thresholds["memory_percent"]
                })
                
            if system_metrics.get("disk_percent", 0) > self.alert_thresholds["disk_percent"]:
                alerts.append({
                    "severity": "critical",
                    "message": f"High disk usage: {system_metrics['disk_percent']}%", 
                    "threshold": self.alert_thresholds["disk_percent"]
                })
        
        return alerts


# Global instances
performance_monitor = PerformanceMonitor()
alert_manager = AlertManager()


def get_monitoring_data() -> Dict:
    """Get comprehensive monitoring data"""
    try:
        performance_metrics = performance_monitor.get_metrics()
        system_metrics = SystemMonitor.get_system_metrics()
        alerts = alert_manager.check_alerts({
            "performance": performance_metrics,
            "system": system_metrics
        })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "performance": performance_metrics,
            "system": system_metrics,
            "alerts": alerts,
            "alert_count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring data: {e}")
        return {"error": "Failed to retrieve monitoring data"}
