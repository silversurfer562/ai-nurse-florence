"""Consolidated metrics module for ai-nurse-florence.

Lightweight Prometheus integration when available; otherwise a memory-backed
metrics store. Exposes compatibility functions used throughout the codebase.
"""

import logging
from typing import Any, Dict, Optional
import threading

logger = logging.getLogger(__name__)

# Read settings flag (best-effort)
try:
    from src.utils.config import get_settings
    settings = get_settings()
    _METRICS_ENABLED = bool(getattr(settings, "ENABLE_METRICS", False))
except Exception:
    _METRICS_ENABLED = False

# Prometheus optional imports
_PROM_AVAILABLE = False
Counter = None
Histogram = None
Gauge = None
Info = None
try:
    import prometheus_client as _prom  # type: ignore
    from prometheus_client import Counter as Counter, Histogram as Histogram, Gauge as Gauge, Info as Info  # type: ignore
    _PROM_AVAILABLE = True
except Exception:
    logger.debug("prometheus_client not available; falling back to memory metrics")

# In-memory store used as fallback
_metrics_lock = threading.RLock()
_metrics_store: Dict[str, Dict[str, Any]] = {}


def _memory_metrics_update(name: str, value: Any = 1, labels: Optional[Dict[str, str]] = None) -> None:
    with _metrics_lock:
        if name not in _metrics_store:
            _metrics_store[name] = {"total": 0, "values": [], "by_label": {}}
        _metrics_store[name]["total"] += value
        _metrics_store[name]["values"].append(value)
        if labels:
            key = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
            if key not in _metrics_store[name]["by_label"]:
                _metrics_store[name]["by_label"][key] = {"total": 0, "values": []}
            _metrics_store[name]["by_label"][key]["total"] += value
            _metrics_store[name]["by_label"][key]["values"].append(value)


def record_cache_hit(cache_key: str, cache_type: str = "redis") -> None:
    if not _METRICS_ENABLED:
        return
    try:
        key_prefix = cache_key.split(":", 1)[0] if cache_key else "unknown"
        if _PROM_AVAILABLE and Counter is not None:
            if "_CACHE_HITS" not in globals():
                globals()['_CACHE_HITS'] = Counter("ai_nurse_cache_hits_total", "Cache hit count", ["cache_type", "key_prefix"])  # type: ignore
            globals()['_CACHE_HITS'].labels(cache_type=cache_type, key_prefix=key_prefix).inc()
        else:
            _memory_metrics_update("cache_hits", labels={"cache_type": cache_type, "key_prefix": key_prefix})
    except Exception as e:
        logger.debug("record_cache_hit failed: %s", e)


def record_cache_miss(cache_key: str, cache_type: str = "redis") -> None:
    if not _METRICS_ENABLED:
        return
    try:
        key_prefix = cache_key.split(":", 1)[0] if cache_key else "unknown"
        if _PROM_AVAILABLE and Counter is not None:
            if "_CACHE_MISSES" not in globals():
                globals()['_CACHE_MISSES'] = Counter("ai_nurse_cache_misses_total", "Cache miss count", ["cache_type", "key_prefix"])  # type: ignore
            globals()['_CACHE_MISSES'].labels(cache_type=cache_type, key_prefix=key_prefix).inc()
        else:
            _memory_metrics_update("cache_misses", labels={"cache_type": cache_type, "key_prefix": key_prefix})
    except Exception as e:
        logger.debug("record_cache_miss failed: %s", e)


def record_external_request(service: str, operation: Optional[str] = None) -> None:
    if not _METRICS_ENABLED:
        return
    try:
        if _PROM_AVAILABLE and Counter is not None:
            if "_EXT_REQUESTS" not in globals():
                globals()['_EXT_REQUESTS'] = Counter("ai_nurse_external_requests_total", "External API request count", ["service"])  # type: ignore
            globals()['_EXT_REQUESTS'].labels(service=service).inc()
        else:
            labels = {"service": service}
            if operation:
                labels["operation"] = operation
            _memory_metrics_update("external_requests", labels=labels)
    except Exception as e:
        logger.debug("record_external_request failed: %s", e)


def record_external_error(service: str, operation: Optional[str] = None, error_type: str = "general") -> None:
    if not _METRICS_ENABLED:
        return
    try:
        if _PROM_AVAILABLE and Counter is not None:
            if "_EXT_ERRORS" not in globals():
                globals()['_EXT_ERRORS'] = Counter("ai_nurse_external_errors_total", "External API error count", ["service", "error_type"])  # type: ignore
            globals()['_EXT_ERRORS'].labels(service=service, error_type=error_type).inc()
        else:
            labels = {"service": service, "error_type": error_type}
            if operation:
                labels["operation"] = operation
            _memory_metrics_update("external_errors", labels=labels)
    except Exception as e:
        logger.debug("record_external_error failed: %s", e)


def record_service_call(service_name: str, success: bool = True) -> None:
    if not _METRICS_ENABLED:
        return
    try:
        _memory_metrics_update("service_calls", labels={"service": service_name, "success": str(bool(success))})
    except Exception as e:
        logger.debug("record_service_call failed: %s", e)


def record_gpt_usage(*args, **kwargs) -> None:
    if not _METRICS_ENABLED:
        return
    try:
        if len(args) == 1 and isinstance(args[0], str) and not kwargs:
            _memory_metrics_update("openai_usage", labels={"usage_type": args[0]})
            return

        tokens = kwargs.get("tokens") if "tokens" in kwargs else (args[0] if len(args) > 0 else None)
        model = kwargs.get("model") if "model" in kwargs else (args[1] if len(args) > 1 else None)
        token_type = kwargs.get("token_type", "total")

        if tokens is None or model is None:
            _memory_metrics_update("openai_usage_unknown")
            return

        tokens = int(tokens)
        if _PROM_AVAILABLE and Counter is not None:
            if "_OPENAI_TOKENS" not in globals():
                globals()['_OPENAI_TOKENS'] = Counter("ai_nurse_openai_tokens_total", "OpenAI tokens used", ["model", "type"])  # type: ignore
            globals()['_OPENAI_TOKENS'].labels(model=model, type=token_type).inc(tokens)
        else:
            _memory_metrics_update("openai_tokens", value=tokens, labels={"model": model, "type": token_type})
    except Exception as e:
        logger.debug("record_gpt_usage failed: %s", e)


def timing_metric(name: str, labels_func=None):
    import time
    from functools import wraps
    import inspect

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs):
                if not _METRICS_ENABLED:
                    return await func(*args, **kwargs)
                labels = {} if not labels_func else (labels_func(*args, **kwargs) or {})
                start = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start
                    _memory_metrics_update(name, value=duration, labels=labels)
                    return result
                except Exception:
                    duration = time.time() - start
                    _memory_metrics_update(name, value=duration, labels=labels)
                    raise

            return wraps(func)(async_wrapper)
        else:
            def sync_wrapper(*args, **kwargs):
                if not _METRICS_ENABLED:
                    return func(*args, **kwargs)
                labels = {} if not labels_func else (labels_func(*args, **kwargs) or {})
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start
                    _memory_metrics_update(name, value=duration, labels=labels)
                    return result
                except Exception:
                    duration = time.time() - start
                    _memory_metrics_update(name, value=duration, labels=labels)
                    raise

            return wraps(func)(sync_wrapper)

    return decorator


def get_metrics_summary() -> Dict[str, Any]:
    if not _METRICS_ENABLED:
        return {"status": "disabled"}
    if _PROM_AVAILABLE:
        return {"status": "prometheus_enabled", "endpoint": "/metrics"}
    with _metrics_lock:
        return {
            "status": "memory_only",
            "metrics": {k: {"total": v["total"], "count": len(v["values"]), "labels": len(v["by_label"])} for k, v in _metrics_store.items()}
        }


def setup_metrics(app, metrics_route: str = "/metrics") -> None:
    if not _METRICS_ENABLED:
        logger.debug("Metrics disabled; setup_metrics no-op")
        return
    if not _PROM_AVAILABLE:
        logger.info("Prometheus client not available; using memory metrics")
        return
    try:
        from prometheus_client import make_asgi_app
        metrics_app = make_asgi_app()
        app.mount(metrics_route, metrics_app)
        logger.info("Prometheus metrics mounted at %s", metrics_route)
    except Exception as e:
        logger.warning("Failed to mount prometheus ASGI app: %s", e)



    def get_metrics_summary() -> Dict[str, Any]:
        if not _METRICS_ENABLED:
            return {"status": "disabled"}
        if _PROM_AVAILABLE:
            return {"status": "prometheus_enabled", "endpoint": "/metrics"}
        with _metrics_lock:
            return {"status": "memory_only", "metrics": {k: {"total": v["total"], "count": len(v["values"]), "labels": len(v["by_label"])} for k, v in _metrics_store.items()}}


    def setup_metrics(app, metrics_route: str = "/metrics") -> None:
        if not _METRICS_ENABLED:
            logger.debug("Metrics disabled; setup_metrics no-op")
            return
        if not _PROM_AVAILABLE:
            logger.info("Prometheus client not available; using memory metrics")
            return
        try:
            from prometheus_client import make_asgi_app
            metrics_app = make_asgi_app()
            app.mount(metrics_route, metrics_app)
            logger.info("Prometheus metrics mounted at %s", metrics_route)
        except Exception as e:
            logger.warning("Failed to mount prometheus ASGI app: %s", e)
