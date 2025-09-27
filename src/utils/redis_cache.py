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

from src.utils.config import get_settings, get_redis_config

# Global cache instances
_redis_client: Optional[Any] = None
_memory_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.RLock()

async def get_redis_client():
    """Get Redis client with graceful fallback"""
    global _redis_client
    
    if not _redis_available:
        return None
    
    if _redis_client is None:
        redis_config = get_redis_config()
        if not redis_config:
            return None
        
        try:
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
            serialized_value = json.dumps(value, default=str)
            await redis_client.setex(key, ttl_seconds, serialized_value)
            return True
    except Exception as e:
        logging.warning(f"Redis cache set failed: {e}")
    
    # Fallback to memory cache
    _memory_cache_set(key, value, ttl_seconds)
    return True

async def cache_get(key: str) -> Optional[Any]:
    """Get cache value with Redis fallback to memory"""
    try:
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            cached_value = await redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
    except Exception as e:
        logging.warning(f"Redis cache get failed: {e}")
    
    # Fallback to memory cache
    return _memory_cache_get(key)

async def cache_delete(key: str) -> bool:
    """Delete cache value from both Redis and memory"""
    success = False
    
    try:
        # Try Redis first
        redis_client = await get_redis_client()
        if redis_client:
            await redis_client.delete(key)
            success = True
    except Exception as e:
        logging.warning(f"Redis cache delete failed: {e}")
    
    # Also delete from memory cache
    _memory_cache_delete(key)
    return success

def cached(ttl_seconds: int = 3600, key_prefix: str = "ai_nurse"):
    """
    Decorator for caching function results
    Following AI Nurse Florence caching strategy
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = await cache_get(cache_key)
            if cached_result is not None:
                logging.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Cache miss - call function
            logging.debug(f"Cache miss for {cache_key}")
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Store in cache
            await cache_set(cache_key, result, ttl_seconds)
            return result
        
        return wrapper
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
    """Get Redis client if available following Caching Strategy."""
    try:
        redis_config = get_redis_config()
        if redis_config["available"]:
            # Production would return Redis client
            return None
        return None
    except Exception:
        return None
