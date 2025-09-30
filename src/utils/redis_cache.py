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
_redis_connection_logged = False  # Track if we've already logged Redis failure

async def get_redis_client():
    """Get Redis client with graceful fallback"""
    global _redis_client, _redis_connection_logged

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
            logging.info("✅ Redis connection established")
            _redis_connection_logged = True
        except Exception as e:
            # Only log the warning once to avoid flooding logs
            if not _redis_connection_logged:
                logging.warning(f"⚠️ Redis unavailable ({e}), using in-memory cache fallback")
                _redis_connection_logged = True
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

                # Try Redis/memory via async path
                try:
                    cached_result = await cache_get(cache_key)
                except Exception:
                    cached_result = None

                if cached_result is not None:
                    logging.debug(f"Cache hit for {cache_key}")
                    return cached_result

                logging.debug(f"Cache miss for {cache_key}")
                result = await func(*args, **kwargs)

                # Best-effort store; allow cache_set errors to bubble silently
                try:
                    await cache_set(cache_key, result, ttl_seconds)
                except Exception:
                    logging.debug(f"Async cache_set failed for {cache_key}")

                return result

            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = _make_key(args, kwargs)

                # Prefer deterministic in-memory cache first
                try:
                    mem_val = _memory_cache_get(cache_key)
                    if mem_val is not None:
                        if _has_metrics:
                            record_cache_hit(cache_key, cache_type="memory")
                        logging.debug(f"Memory cache hit for {cache_key}")
                        return mem_val
                except Exception:
                    logging.debug("Memory cache access failed in sync wrapper")

                # Cache miss: call the sync function
                result = func(*args, **kwargs)

                # Store in memory immediately for deterministic sync behavior
                try:
                    _memory_cache_set(cache_key, result, ttl_seconds)
                    if _has_metrics:
                        record_cache_miss(cache_key, cache_type="memory")
                except Exception:
                    logging.debug("Memory cache set failed in sync wrapper")

                # Schedule Redis update in background without blocking.
                try:
                    try:
                        running_loop = asyncio.get_running_loop()
                    except RuntimeError:
                        running_loop = None

                    if running_loop is not None:
                        # We're in an async context but called a sync function; schedule
                        # an async cache update task without awaiting it.
                        def _schedule_update():
                            try:
                                asyncio.create_task(cache_set(cache_key, result, ttl_seconds))
                            except Exception:
                                pass

                        running_loop.call_soon_threadsafe(_schedule_update)
                    else:
                        # No loop running: run cache_set in a background thread to
                        # avoid blocking the caller thread.
                        threading.Thread(
                            target=lambda: asyncio.run(cache_set(cache_key, result, ttl_seconds)),
                            daemon=True,
                        ).start()
                except Exception:
                    logging.debug("Background cache update scheduling failed")

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
