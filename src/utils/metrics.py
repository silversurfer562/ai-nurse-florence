"""
Metrics collection for AI Nurse Florence
Includes cache metrics, API response times, and optional Prometheus integration
"""

import time
import logging
import os
import asyncio
from typing import Dict, Any, Optional, Callable, Union, List
from functools import wraps
import threading
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration
try:
    from src.utils.config import get_settings
    settings = get_settings()
    _metrics_enabled = getattr(settings, 'ENABLE_METRICS', False)
except Exception:
    _metrics_enabled = False

# Thread-safe metrics store for memory-based metrics
_metrics_store: Dict[str, Dict[str, Any]] = {}
_metrics_lock = threading.RLock()

# Prometheus client (optional)
_prometheus_available = False
_prometheus_metrics = {}

# Try to import prometheus client
try:
    import prometheus_client
    _prometheus_available = True
    
    # Initialize prometheus metrics if available
    def _init_prometheus_metrics():
        global _prometheus_metrics
        if not _prometheus_metrics:
            _prometheus_metrics = {
                # Cache metrics
                "cache_hits": prometheus_client.Counter(
                    'ai_nurse_cache_hits_total', 
                    'Cache hit count', 
                    ['cache_type', 'key_prefix']
                ),
                "cache_misses": prometheus_client.Counter(
                    'ai_nurse_cache_misses_total', 
                    'Cache miss count', 
                    ['cache_type', 'key_prefix']
                ),
                # API metrics
                "api_requests": prometheus_client.Counter(
                    'ai_nurse_api_requests_total', 
                    'API request count', 
                    ['endpoint', 'method', 'status']
                ),
                "api_latency": prometheus_client.Histogram(
                    'ai_nurse_api_latency_seconds', 
                    'API latency in seconds', 
                    ['endpoint'], 
                    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30]
                ),
                # External service metrics
                "external_requests": prometheus_client.Counter(
                    'ai_nurse_external_requests_total', 
                    'External API request count', 
                    ['service']
                ),
                "external_errors": prometheus_client.Counter(
                    'ai_nurse_external_errors_total', 
                    'External API error count', 
                    ['service', 'error_type']
                ),
                # System info
                "system_info": prometheus_client.Info(
                    'ai_nurse_system', 
                    'System information'
                )
            }
            
            # Set system info
            _prometheus_metrics["system_info"].info({
                "version": getattr(settings, 'APP_VERSION', 'unknown'),
                "environment": "railway" if os.environ.get("RAILWAY_ENVIRONMENT") else "development"
            })
except ImportError:
    logger.info("Prometheus client not available, using memory metrics")

# Import configuration
try:
    from src.utils.config import get_settings
    settings = get_settings()
    _metrics_enabled = settings.ENABLE_METRICS
except Exception:
    _metrics_enabled = False

# Configure logging
logger = logging.getLogger(__name__)

# Thread-safe metrics store for memory-based metrics
_metrics_store: Dict[str, Dict[str, Any]] = {}
_metrics_lock = threading.RLock()

# Prometheus metrics
if _prometheus_available and _metrics_enabled:
    # Cache metrics
    CACHE_HITS = Counter('ai_nurse_cache_hits_total', 'Cache hit count', ['cache_type', 'key_prefix'])
    CACHE_MISSES = Counter('ai_nurse_cache_misses_total', 'Cache miss count', ['cache_type', 'key_prefix'])
    CACHE_ERRORS = Counter('ai_nurse_cache_errors_total', 'Cache error count', ['cache_type'])
    
    # API metrics
    API_REQUESTS = Counter('ai_nurse_api_requests_total', 'API request count', ['endpoint', 'method', 'status'])
    API_LATENCY = Histogram('ai_nurse_api_latency_seconds', 'API latency in seconds', 
                           ['endpoint'], buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10, 30])
    
    # External service metrics
    EXTERNAL_REQUESTS = Counter('ai_nurse_external_requests_total', 'External API request count', ['service'])
    EXTERNAL_ERRORS = Counter('ai_nurse_external_errors_total', 'External API error count', ['service', 'error_type'])
    EXTERNAL_LATENCY = Histogram('ai_nurse_external_latency_seconds', 'External API latency in seconds', 
                                ['service'], buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60])
    
    # OpenAI metrics
    OPENAI_TOKENS = Counter('ai_nurse_openai_tokens_total', 'OpenAI tokens used', ['model', 'type'])
    OPENAI_COSTS = Counter('ai_nurse_openai_costs_total', 'OpenAI costs in USD', ['model'])
    
    # System metrics
    SYSTEM_INFO = Info('ai_nurse_system', 'System information')
    ACTIVE_CONNECTIONS = Gauge('ai_nurse_active_connections', 'Number of active connections')

def _memory_metrics_update(metric_name: str, value: Any = 1, labels: Optional[Dict[str, str]] = None):
    """Update memory-based metrics when Prometheus is not available"""
    with _metrics_lock:
        if metric_name not in _metrics_store:
            _metrics_store[metric_name] = {"total": 0, "values": [], "by_label": {}}
        
        _metrics_store[metric_name]["total"] += value
        _metrics_store[metric_name]["values"].append(value)
        
        # Limit stored values to prevent memory growth
        if len(_metrics_store[metric_name]["values"]) > 1000:
            _metrics_store[metric_name]["values"] = _metrics_store[metric_name]["values"][-1000:]
        
        if labels:
            label_key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            if label_key not in _metrics_store[metric_name]["by_label"]:
                _metrics_store[metric_name]["by_label"][label_key] = {"total": 0, "values": []}
            
            _metrics_store[metric_name]["by_label"][label_key]["total"] += value
            _metrics_store[metric_name]["by_label"][label_key]["values"].append(value)
            
            # Limit stored values for labels too
            if len(_metrics_store[metric_name]["by_label"][label_key]["values"]) > 100:
                _metrics_store[metric_name]["by_label"][label_key]["values"] = _metrics_store[metric_name]["by_label"][label_key]["values"][-100:]

def record_cache_hit(cache_key: str, cache_type: str = "redis"):
    """Record a cache hit"""
    if not _metrics_enabled:
        return
    
    try:
        # Extract key prefix (everything before the first colon)
        key_parts = cache_key.split(":", 1)
        key_prefix = key_parts[0] if len(key_parts) > 0 else "unknown"
        
        if _prometheus_available:
            CACHE_HITS.labels(cache_type=cache_type, key_prefix=key_prefix).inc()
        else:
            _memory_metrics_update("cache_hits", labels={"cache_type": cache_type, "key_prefix": key_prefix})
            
        logger.debug(f"Cache hit recorded: {cache_key}")
    except Exception as e:
        logger.debug(f"Failed to record cache hit: {e}")

def record_cache_miss(cache_key: str, cache_type: str = "redis"):
    """Record a cache miss"""
    if not _metrics_enabled:
        return
    
    try:
        # Extract key prefix (everything before the first colon)
        key_parts = cache_key.split(":", 1)
        key_prefix = key_parts[0] if len(key_parts) > 0 else "unknown"
        
        if _prometheus_available:
            CACHE_MISSES.labels(cache_type=cache_type, key_prefix=key_prefix).inc()
        else:
            _memory_metrics_update("cache_misses", labels={"cache_type": cache_type, "key_prefix": key_prefix})
            
        logger.debug(f"Cache miss recorded: {cache_key}")
    except Exception as e:
        logger.debug(f"Failed to record cache miss: {e}")

def record_external_request(service: str):
    """Record an external API request"""
    if not _metrics_enabled:
        return
    
    try:
        if _prometheus_available:
            EXTERNAL_REQUESTS.labels(service=service).inc()
        else:
            _memory_metrics_update("external_requests", labels={"service": service})
    except Exception as e:
        logger.debug(f"Failed to record external request: {e}")

def record_external_error(service: str, error_type: str = "general"):
    """Record an external API error"""
    if not _metrics_enabled:
        return
    
    try:
        if _prometheus_available:
            EXTERNAL_ERRORS.labels(service=service, error_type=error_type).inc()
        else:
            _memory_metrics_update("external_errors", labels={"service": service, "error_type": error_type})
    except Exception as e:
        logger.debug(f"Failed to record external error: {e}")

def record_api_request(endpoint: str, method: str, status: Union[int, str]):
    """Record an API request"""
    if not _metrics_enabled:
        return
    
    try:
        if _prometheus_available:
            API_REQUESTS.labels(endpoint=endpoint, method=method, status=str(status)).inc()
        else:
            _memory_metrics_update("api_requests", labels={"endpoint": endpoint, "method": method, "status": str(status)})
    except Exception as e:
        logger.debug(f"Failed to record API request: {e}")

def record_gpt_usage(tokens: int, model: str, token_type: str = "total"):
    """Record OpenAI GPT token usage"""
    if not _metrics_enabled:
        return
    
    try:
        if _prometheus_available:
            OPENAI_TOKENS.labels(model=model, type=token_type).inc(tokens)
            
            # Calculate approximate cost
            cost_per_1k = {
                "gpt-3.5-turbo": 0.002,
                "gpt-4": 0.03,
                "gpt-4-turbo": 0.01,
                "gpt-4-32k": 0.06
            }.get(model, 0.005)
            
            cost = tokens * cost_per_1k / 1000
            if cost > 0:
                OPENAI_COSTS.labels(model=model).inc(cost)
        else:
            _memory_metrics_update("openai_tokens", value=tokens, labels={"model": model, "type": token_type})
    except Exception as e:
        logger.debug(f"Failed to record GPT usage: {e}")

def timing_metric(name: str, labels_func=None):
    """Decorator to measure execution time of functions"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _metrics_enabled:
                return await func(*args, **kwargs)
            
            labels = {}
            if labels_func:
                try:
                    labels = labels_func(*args, **kwargs) or {}
                except Exception:
                    pass
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                if _prometheus_available:
                    if name == "api_latency":
                        API_LATENCY.labels(**labels).observe(duration)
                    elif name == "external_latency":
                        EXTERNAL_LATENCY.labels(**labels).observe(duration)
                else:
                    _memory_metrics_update(name, value=duration, labels=labels)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                if _prometheus_available:
                    if name == "api_latency":
                        API_LATENCY.labels(**labels).observe(duration)
                    elif name == "external_latency":
                        EXTERNAL_LATENCY.labels(**labels).observe(duration)
                else:
                    _memory_metrics_update(name, value=duration, labels=labels)
                
                raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not _metrics_enabled:
                return func(*args, **kwargs)
            
            labels = {}
            if labels_func:
                try:
                    labels = labels_func(*args, **kwargs) or {}
                except Exception:
                    pass
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if _prometheus_available:
                    if name == "api_latency":
                        API_LATENCY.labels(**labels).observe(duration)
                    elif name == "external_latency":
                        EXTERNAL_LATENCY.labels(**labels).observe(duration)
                else:
                    _memory_metrics_update(name, value=duration, labels=labels)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                if _prometheus_available:
                    if name == "api_latency":
                        API_LATENCY.labels(**labels).observe(duration)
                    elif name == "external_latency":
                        EXTERNAL_LATENCY.labels(**labels).observe(duration)
                else:
                    _memory_metrics_update(name, value=duration, labels=labels)
                
                raise e
        
        if hasattr(func, "__awaitable__"):
            return async_wrapper
        return sync_wrapper
    
    return decorator

def get_metrics_summary() -> Dict[str, Any]:
    """Get a summary of collected metrics for health check endpoint"""
    if not _metrics_enabled:
        return {"status": "disabled"}
    
    if _prometheus_available:
        return {
            "status": "prometheus_enabled",
            "endpoint": "/metrics"
        }
    
    # Return memory-based metrics summary
    with _metrics_lock:
        return {
            "status": "memory_only",
            "metrics": {
                key: {
                    "total": value["total"],
                    "count": len(value["values"]),
                    "labels": len(value["by_label"])
                }
                for key, value in _metrics_store.items()
            }
        }

def setup_metrics(app):
    """Setup Prometheus metrics for FastAPI app"""
    if not _metrics_enabled:
        logger.info("Metrics collection disabled")
        return
    
    if not _prometheus_available:
        logger.info("Prometheus client not available, using memory metrics")
        return
    
    try:
        from prometheus_client import make_asgi_app
        
        # Add version info
        SYSTEM_INFO.info({
            "version": settings.APP_VERSION,
            "environment": "railway" if settings.RAILWAY_ENVIRONMENT else "development"
        })
        
        # Add prometheus endpoint
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        logger.info("Prometheus metrics enabled at /metrics")
    except Exception as e:
        logger.warning(f"Failed to setup Prometheus metrics: {e}")
