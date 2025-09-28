"""
Redis caching with in-memory fallback
Following AI Nurse Florence Conditional Imports Pattern
"""

import json
import asyncio
import logging
from typing import Any, Optional, Dict, Callable
from functools import wraps
import threading
from datetime import datetime, timedelta

# Conditional Redis import - graceful degradation
try:
    import redis.asyncio as redis
    _redis_available = True
except ImportError:
    _redis_available = False
    redis = None

import os
from src.utils.config import get_redis_config

# Optional metrics - record cache hits/misses when available
try:
    from src.utils.metrics import record_cache_hit, record_cache_miss
    _has_metrics = True
except Exception:
    _has_metrics = False
    def record_cache_hit(cache_key: str, cache_type: str = "redis"):
        return
    def record_cache_miss(cache_key: str, cache_type: str = "redis"):
        return

# Global cache instances
_redis_client: Optional[Any] = None
_memory_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.RLock()

async def get_redis_client():
    """Get Redis client with graceful fallback"""
    global _redis_client
    
    # Allow tests or environments to force in-memory-only mode by setting
    # AI_NURSE_DISABLE_REDIS=1 in the environment. This prevents background
    # Redis connection attempts that can leave pending tasks during test runs.
    if os.environ.get("AI_NURSE_DISABLE_REDIS", "0") in ("1", "true", "True"):
        return None

    if not _redis_available:
        return None
    
    if _redis_client is None:
        redis_config = get_redis_config()
        if not redis_config:
            return None
        
        try:
            # redis is imported conditionally; ensure the name is not None for static checkers
            assert redis is not None
            _redis_client = redis.from_url(
                redis_config["url"],
                decode_responses=redis_config.get("decode_responses", True),
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            await _redis_client.ping()
            logging.info("Redis connection established")
        except Exception as e:
            logging.warning(f"Redis connection failed: {e}, using in-memory cache")
            _redis_client = None
    
    return _redis_client

def _memory_cache_set(key: str, value: Any, ttl_seconds: int = 3600):
    """Set value in memory cache with TTL"""
    with _cache_lock:
        expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        _memory_cache[key] = {
            "value": value,
            "expiry": expiry
        }

def _memory_cache_get(key: str) -> Optional[Any]:
    """Get value from memory cache"""
    with _cache_lock:
        if key not in _memory_cache:
            return None
        
        cache_entry = _memory_cache[key]
        if datetime.utcnow() > cache_entry["expiry"]:
            del _memory_cache[key]
            return None
        
        return cache_entry["value"]

def _memory_cache_delete(key: str):
    """Delete value from memory cache"""
    with _cache_lock:
        _memory_cache.pop(key, None)

async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
    """Set cache value with Redis fallback to memory"""
    try:
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                serialized_value = json.dumps(value, default=str)
                await redis_client.setex(key, ttl_seconds, serialized_value)
                if _has_metrics:
                    record_cache_miss(key, cache_type="redis")
                return True
            except Exception as e:
                logging.warning(f"Redis cache set serialization/storing failed: {e}")
    except Exception as e:
        logging.warning(f"Redis cache set failed: {e}")
    
    # Fallback to memory cache
    try:
        _memory_cache_set(key, value, ttl_seconds)
        if _has_metrics:
            record_cache_miss(key, cache_type="memory")
    except Exception as e:
        logging.warning(f"Memory cache set failed: {e}")
    return True

async def cache_get(key: str) -> Optional[Any]:
    """Get cache value with Redis fallback to memory"""
    try:
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                cached_value = await redis_client.get(key)
                if cached_value:
                    if _has_metrics:
                        record_cache_hit(key, cache_type="redis")
                    return json.loads(cached_value)
            except Exception as e:
                logging.warning(f"Redis cache get/deserialize failed: {e}")
    except Exception as e:
        logging.warning(f"Redis cache get failed: {e}")
    
    # Fallback to memory cache
    try:
        val = _memory_cache_get(key)
        if val is not None and _has_metrics:
            record_cache_hit(key, cache_type="memory")
        return val
    except Exception as e:
        logging.warning(f"Memory cache get failed: {e}")
        return None

async def cache_delete(key: str) -> bool:
    """Delete cache value from both Redis and memory"""
    success = False
    
    try:
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            try:
                await redis_client.delete(key)
                success = True
            except Exception as e:
                logging.warning(f"Redis cache delete failed for key {key}: {e}")
    except Exception as e:
        logging.warning(f"Redis cache delete failed: {e}")
    
    # Also delete from memory cache
    try:
        _memory_cache_delete(key)
    except Exception as e:
        logging.warning(f"Memory cache delete failed for key {key}: {e}")
    return success


def _run_sync(coro):
    """Run an async coroutine from sync code, handling running event loops."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Running inside an event loop (e.g., in async framework); schedule and wait
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    else:
        return asyncio.run(coro)


def cache_set_sync(key: str, value: Any, ttl_seconds: int = 3600) -> bool:
    """Synchronous wrapper for `cache_set`.

    Prefer storing in the in-memory cache first for deterministic behavior in
    sync contexts, then attempt to update Redis asynchronously. Any Redis
    errors are swallowed since memory is the fallback.
    """
    try:
        _memory_cache_set(key, value, ttl_seconds)
        if _has_metrics:
            record_cache_miss(key, cache_type="memory")
    except Exception as e:
        logging.warning(f"Memory cache set failed in sync wrapper: {e}")

    # Attempt to update Redis as best-effort, ignore errors
    try:
        _run_sync(cache_set(key, value, ttl_seconds))
    except Exception:
        pass

    return True


def cache_get_sync(key: str) -> Optional[Any]:
    """Synchronous wrapper for `cache_get`.

    Check the in-memory cache first for deterministic sync behaviour. If
    not found, fall back to attempting an async Redis read.
    """
    try:
        val = _memory_cache_get(key)
        if val is not None:
            if _has_metrics:
                record_cache_hit(key, cache_type="memory")
            return val
    except Exception:
        logging.debug("Memory cache get failed in sync wrapper")

    # If not in memory, try Redis (best-effort)
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None

    cached_result = None
    try:
        # If we have a running loop in the current thread, avoid submitting
        # coroutines into it from sync code (this can deadlock in pytest's
        # asyncio runner). Prefer the deterministic in-memory cache in that
        # case and skip attempting a Redis read from sync contexts.
        if loop is not None and loop.is_running():
            cached_result = None
        else:
            # No running loop available — run the coroutine synchronously (safe fallback)
            try:
                cached_result = asyncio.run(cache_get(key))
            except Exception:
                cached_result = None
    except Exception:
        cached_result = None

    if cached_result is not None:
        logging.debug(f"Cache hit for {key}")
        return cached_result

    return None


def cache_delete_sync(key: str) -> bool:
    """Synchronous wrapper for `cache_delete`.

    Delete from in-memory cache first (deterministic), then attempt an
    async Redis delete as best-effort.
    """
    try:
        _memory_cache_delete(key)
    except Exception:
        logging.debug("Memory cache delete failed in sync wrapper")

    try:
        return _run_sync(cache_delete(key))
    except Exception:
        return False

def cached(ttl_seconds: int = 3600, key_prefix: str = "ai_nurse"):
    """
    Decorator for caching function results
    Supports async and sync functions. Uses Redis with in-memory fallback.
    """
    def decorator(func: Callable):
        is_coro = asyncio.iscoroutinefunction(func)

        def _make_key(args, kwargs):
            try:
                key_body = json.dumps({"args": args, "kwargs": kwargs}, default=str, sort_keys=True)
            except Exception:
                key_body = str((args, tuple(sorted(kwargs.items()))))
            # Keep key length reasonable
            suffix = str(abs(hash(key_body)))
            return f"{key_prefix}:{func.__name__}:{suffix}"

        if is_coro:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                cache_key = _make_key(args, kwargs)
                cached_result = await cache_get(cache_key)
                if cached_result is not None:
                    logging.debug(f"Cache hit for {cache_key}")
                    return cached_result

                logging.debug(f"Cache miss for {cache_key}")
                result = await func(*args, **kwargs)
                await cache_set(cache_key, result, ttl_seconds)
                return result

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = _make_key(args, kwargs)
                # run async cache_get in event loop if available
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = None

                cached_result = None
                try:
                    # If we have a running loop, use run_coroutine_threadsafe with a short timeout.
                    if loop is not None and loop.is_running():
                        future = asyncio.run_coroutine_threadsafe(cache_get(cache_key), loop)
                        try:
                            cached_result = future.result(timeout=5)
                        except Exception:
                            cached_result = None
                    else:
                        # No running loop available — run the coroutine synchronously (safe fallback)
                        try:
                            cached_result = asyncio.run(cache_get(cache_key))
                        except Exception:
                            cached_result = None
                except Exception:
                    cached_result = None

                if cached_result is not None:
                    logging.debug(f"Cache hit for {cache_key}")
                    return cached_result

                logging.debug(f"Cache miss for {cache_key}")
                result = func(*args, **kwargs)

                # store result: prefer in-memory (already set by wrapper); if
                # no event loop is running we can update Redis synchronously.
                try:
                    if loop is not None and loop.is_running():
                        # Skip Redis update when running inside an event loop
                        # in the same thread to avoid blocking/deadlocks.
                        pass
                    else:
                        asyncio.run(cache_set(cache_key, result, ttl_seconds))
                except Exception:
                    # Best-effort: ignore cache update failures
                    pass

                return result

            return sync_wrapper

    return decorator

# Cache status helper for monitoring
async def get_cache_status() -> Dict[str, Any]:
    """Get cache system status"""
    redis_status = "unavailable"
    redis_info = {}
    
    try:
        redis_client = await get_redis_client()
        if redis_client:
            redis_info = await redis_client.info()
            redis_status = "connected"
    except Exception:
        redis_status = "error"
    
    memory_entries = len(_memory_cache)
    
    return {
        "redis": {
            "status": redis_status,
            "info": redis_info
        },
        "memory": {
            "entries": memory_entries,
            "status": "active"
        },
        "fallback_mode": redis_status != "connected"
    }

# Cleanup function for graceful shutdown
async def cleanup_cache():
    """Cleanup cache connections"""
    global _redis_client, _memory_cache
    
    if _redis_client:
        try:
            await _redis_client.close()
        except Exception:
            pass
        _redis_client = None
    
    with _cache_lock:
        _memory_cache.clear()
    
    logging.info("Cache cleanup completed")

def get_cache_client():
    """Return cache client status information.

    Returns a dict: {"available": bool, "url": Optional[str]}
    This is a safe, synchronous helper that does not create async connections.
    """
    try:
        cfg = get_redis_config() or {}
        url = cfg.get("url")
        # Consider Redis available if URL present and the redis library is installed
        available = bool(url) and _redis_available
        return {"available": available, "url": url}
    except Exception:
        return {"available": False, "url": None}
