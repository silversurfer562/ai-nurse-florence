"""
Health Checks Module for AI Nurse Florence

This module provides comprehensive health monitoring for all system components,
including database, cache, external services, and system resources.
"""

import asyncio
import time
import logging
import psutil  # type: ignore
from typing import Dict, Any, Optional
from datetime import datetime

# Conditional imports following AI Nurse Florence pattern
try:
    from src.utils.redis_cache import get_redis_client
    _has_redis = True
except ImportError:
    _has_redis = False
    get_redis_client = None  # type: ignore

try:
    from src.models.database import engine
    from sqlalchemy import text
    _has_database = True
except ImportError:
    _has_database = False
    engine = None
    text = lambda x: x  # type: ignore

try:
    import httpx
    _has_httpx = True
except ImportError:
    _has_httpx = False
    httpx = None  # type: ignore

logger = logging.getLogger(__name__)


async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    if not _has_database or engine is None:
        return {
            "status": "disabled",
            "message": "Database module not available",
            "latency_ms": None
        }
    
    start_time = time.time()
    
    try:
        # Test database connectivity with a simple query
        async with engine.begin() as connection:
            if text is not None:
                result = await connection.execute(text("SELECT 1"))
                row = result.fetchone()
            else:
                row = [1]  # Fallback
        
        latency_ms = (time.time() - start_time) * 1000
        
        if row:
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "message": "Database connection successful"
            }
        else:
            return {
                "status": "unhealthy",
                "latency_ms": round(latency_ms, 2),
                "error": "Database query returned no result"
            }
            
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.warning(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "latency_ms": round(latency_ms, 2),
            "error": str(e)
        }


async def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and performance."""
    if not _has_redis or get_redis_client is None:
        return {
            "status": "unavailable",
            "message": "Redis not configured"
        }
    
    start_time = time.time()
    
    try:
        redis_client = await get_redis_client()
        if redis_client is None:
            return {
                "status": "unavailable",
                "message": "Redis client not available"
            }
        
        # Test basic connectivity
        if hasattr(redis_client, 'ping'):
            await redis_client.ping()
        else:
            # Fallback for Redis clients without ping
            await redis_client.set("health_check", "ok", ex=1)
            await redis_client.delete("health_check")
        
        # Test cache operations
        test_key = "health_test_key"
        test_value = "health_test_value"
        
        # Set and get test
        await redis_client.set(test_key, test_value, ex=10)
        retrieved_value = await redis_client.get(test_key)
        await redis_client.delete(test_key)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if retrieved_value == test_value:
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "cache_operations": "working"
            }
        else:
            return {
                "status": "unhealthy",
                "error": "Cache operations not working correctly",
                "response_time_ms": response_time
            }
            
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": response_time
        }


async def check_external_service(service_name: str, url: str, timeout: int = 5) -> Dict[str, Any]:
    """Check health of an external service."""
    if not _has_httpx or httpx is None:
        return {
            "status": "disabled",
            "message": "HTTP client not available",
            "response_time_ms": None
        }
    
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            
        response_time_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            return {
                "status": "healthy",
                "response_time_ms": round(response_time_ms, 2),
                "status_code": response.status_code
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": round(response_time_ms, 2),
                "status_code": response.status_code,
                "error": f"HTTP {response.status_code}"
            }
            
    except asyncio.TimeoutError:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy",
            "response_time_ms": round(response_time_ms, 2),
            "error": "Request timeout"
        }
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy", 
            "response_time_ms": round(response_time_ms, 2),
            "error": str(e)
        }


async def check_external_services_health() -> Dict[str, Any]:
    """Check health of external medical services."""
    services = {
        "mydisease": "https://mydisease.info/v1/metadata",
        "pubmed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi",
        "clinicaltrials": "https://clinicaltrials.gov/api/info",
        # Add MedlinePlus when available
        # "medlineplus": "https://wsearch.nlm.nih.gov/ws/query"
    }
    
    results: Dict[str, Any] = {}
    
    # Check services concurrently for better performance
    tasks = []
    service_names = []
    
    for service_name, url in services.items():
        task = check_external_service(service_name, url)
        tasks.append(task)
        service_names.append(service_name)
    
    try:
        service_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(service_results):
            service_name = service_names[i]
            if isinstance(result, Exception):
                results[service_name] = {
                    "status": "unhealthy",
                    "error": str(result),
                    "response_time_ms": None
                }
            else:
                results[service_name] = result
                
    except Exception as e:
        logger.error(f"Error checking external services: {e}")
        results["error"] = str(e)
    
    return results


async def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage."""
    try:
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # CPU usage (average over 1 second)
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        return {
            "memory_usage": round(memory_percent, 2),
            "cpu_usage": round(cpu_percent, 2),
            "disk_usage": round(disk_percent, 2),
            "status": "healthy" if all(x < 90 for x in [memory_percent, cpu_percent, disk_percent]) else "warning"
        }
        
    except Exception as e:
        logger.warning(f"System resource check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "memory_usage": None,
            "cpu_usage": None,
            "disk_usage": None
        }


async def get_comprehensive_health_status() -> Dict[str, Any]:
    """Get comprehensive health status for all system components."""
    start_time = time.time()
    
    # Run all health checks concurrently
    tasks = [
        check_database_health(),
        check_redis_health(),
        check_external_services_health(),
        check_system_resources()
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        db_health, redis_health, external_health, system_health = results
        
        # Handle exceptions in results
        if isinstance(db_health, Exception):
            db_health = {"status": "error", "error": str(db_health)}
        if isinstance(redis_health, Exception):
            redis_health = {"status": "error", "error": str(redis_health)}
        if isinstance(external_health, Exception):
            external_health = {"status": "error", "error": str(external_health)}
        if isinstance(system_health, Exception):
            system_health = {"status": "error", "error": str(system_health)}
        
        # Determine overall health status
        overall_status = "healthy"
        
        # Check critical services
        if isinstance(db_health, dict) and db_health.get("status") == "unhealthy":
            overall_status = "unhealthy"
        elif isinstance(db_health, dict) and db_health.get("status") in ["error", "degraded"]:
            overall_status = "degraded"
        
        # Redis is not critical (graceful degradation)
        if isinstance(redis_health, dict) and redis_health.get("status") == "unhealthy" and overall_status == "healthy":
            overall_status = "degraded"
        
        # System resources
        if isinstance(system_health, dict):
            if system_health.get("status") == "warning" and overall_status == "healthy":
                overall_status = "degraded"
            elif system_health.get("status") == "error":
                overall_status = "degraded"
        
        # Check external services (not critical but affects functionality)
        external_unhealthy = 0
        external_total = 0
        if isinstance(external_health, dict):
            for service_name, service_status in external_health.items():
                if service_name != "error" and isinstance(service_status, dict):
                    external_total += 1
                    if service_status.get("status") == "unhealthy":
                        external_unhealthy += 1
        
        # If more than half of external services are down
        if external_total > 0 and external_unhealthy / external_total > 0.5:
            if overall_status == "healthy":
                overall_status = "degraded"
        
        health_status = {
            "status": overall_status,
            "timestamp": time.time(),
            "check_duration_ms": round((time.time() - start_time) * 1000, 2),
            "services": {
                "database": db_health,
                "cache": redis_health,
                "system": system_health
            },
            "external_services": external_health
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {e}")
        return {
            "status": "error",
            "timestamp": time.time(),
            "error": str(e),
            "services": {},
            "external_services": {}
        }


# Convenience function for simple health check
async def is_system_healthy() -> bool:
    """Simple boolean health check."""
    try:
        health = await get_comprehensive_health_status()
        return health["status"] in ["healthy", "degraded"]
    except Exception:
        return False