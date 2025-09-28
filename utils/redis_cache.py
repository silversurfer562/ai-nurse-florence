"""
Redis cache implementation for the application.

This module provides a Redis-backed caching system with TTL support
that can be used in production environments. It implements the same
interface as the in-memory cache for easy switching.
"""
import json
from typing import Any, Optional, TypeVar, Callable, Tuple, Union
import redis
from utils.logging import get_logger
from utils.config import settings
import os
import signal
import subprocess

# Conditional import for metrics
try:
    from src.utils.metrics import record_cache_hit, record_cache_miss
    _has_metrics = True
except ImportError:
    _has_metrics = False
    # Stub implementations if metrics module isn't available
    def record_cache_hit(cache_key: str) -> None:
        pass
    def record_cache_miss(cache_key: str) -> None:
        pass

logger = get_logger(__name__)

T = TypeVar('T')

class RedisCache:
    """
    Redis-backed cache with TTL support.
    
    This cache uses Redis for storage, making it suitable for distributed
    environments where multiple instances of the application are running.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the Redis cache.
        
        Args:
            redis_url: Redis connection URL (default: from REDIS_URL env var)
        """
        self._redis_url = redis_url or settings.REDIS_URL
        if not self._redis_url:
            raise ValueError("Redis URL not provided or configured in settings.")
        self._redis = redis.from_url(self._redis_url)
        logger.info(f"Connected to Redis at {self._redis_url}")
        
    def get(self, key: str) -> Tuple[Optional[Any], bool]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            A tuple of (value, hit) where hit is True if the key was found,
            False otherwise.
        """
        try:
            value = self._redis.get(key)
            if value is not None:
                logger.debug(f"Redis cache hit for key: {key}")
                if _has_metrics:
                    record_cache_hit(key)
                return json.loads(value), True
            
            logger.debug(f"Redis cache miss for key: {key}")
            if _has_metrics:
                record_cache_miss(key)
            return None, False
        except Exception as e:
            logger.error(
                f"Redis get error: {str(e)}", 
                extra={"key": key, "error": str(e)},
                exc_info=True
            )
            if _has_metrics:
                record_cache_miss(key)
            return None, False
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to store
            ttl_seconds: Time-to-live in seconds (default: 300)
        """
        try:
            serialized = json.dumps(value)
            self._redis.setex(key, ttl_seconds, serialized)
            logger.debug(f"Redis cached key: {key}, expires in {ttl_seconds}s")
        except Exception as e:
            logger.error(
                f"Redis set error: {str(e)}", 
                extra={"key": key, "error": str(e)},
                exc_info=True
            )
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        try:
            result = self._redis.delete(key)
            success = result > 0
            if success:
                logger.debug(f"Deleted Redis cache key: {key}")
            return success
        except Exception as e:
            logger.error(
                f"Redis delete error: {str(e)}", 
                extra={"key": key, "error": str(e)},
                exc_info=True
            )
            return False
    
    def clear(self) -> None:
        """Clear all cache entries with a specific prefix."""
        try:
            # In production, you'd typically use a key prefix
            # and only clear keys with that prefix
            logger.warning("Redis cache clear called - this is potentially dangerous in production")
            # This is a placeholder; in production you'd implement a safer approach
            # self._redis.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}", exc_info=True)


# Cache factory function
def get_cache() -> Union[RedisCache, 'CacheService']:
    """
    Get the appropriate cache implementation based on configuration.
    
    Returns:
        A cache instance (Redis-based if REDIS_URL is set, in-memory otherwise)
    """
    if settings.REDIS_URL:
        # Use Redis cache
        try:
            from redis import Redis
            return RedisCache(settings.REDIS_URL)
        except ImportError:
            logger.warning("Redis package not installed; falling back to in-memory cache")
    
    # Fall back to in-memory cache
    from utils.cache import CacheService
    return CacheService()


def cached(ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time-to-live in seconds (default: 300)
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Create a cache key from function name and arguments
            cache_key = (
                f"{func.__module__}.{func.__name__}:"
                f"{repr(args)}:{repr(sorted(kwargs.items()))}"
            )
            
            # Check if we have a valid cached result
            cache = get_cache()
            result, hit = cache.get(cache_key)
            
            if hit:
                return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            return result
            
        return wrapper
    return decorator

# --- Synchronous wrapper for Redis cache ---

def sync_wrapper(func: Callable[..., T]) -> Callable[..., T]:
    """
    Synchronous wrapper for Redis cache access.
    
    This is used to allow synchronous code to access the Redis cache
    in an asyncio-based application.
    """
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        cache_key = f"{func.__module__}.{func.__name__}:{repr(args)}:{repr(sorted(kwargs.items()))}"
        cache = get_cache()
        
        # Try to get the cached result
        cached_result, hit = cache.get(cache_key)
        
        if hit:
            return cached_result
        
        # If no cached result, call the function
        result = func(*args, **kwargs)
        
        # Cache the result asynchronously
        loop = kwargs.get('_loop')  # Expecting the event loop to be passed in kwargs
        ttl_seconds = kwargs.get('_ttl', 300)
        
        # Coroutine to set the cache
        async def cache_set(key, value, ttl):
            cache.set(key, value, ttl)
        
        # Coroutine to get the cache
        async def cache_get(key):
            return cache.get(key)
        
        # Use the provided loop if available
        try:
            (
                (lambda: (
                    (lambda future: (future.result(timeout=5) if True else None))(
                        asyncio.run_coroutine_threadsafe(cache_get(cache_key), loop)
                    )
                ) )() if (loop is not None and loop.is_running()) else asyncio.run(cache_get(cache_key))
            )
        except Exception:
            cached_result = None
        
        if cached_result is not None:
            return cached_result
        
        # Fallback: set the cache normally (non-async)
        cache.set(cache_key, result, ttl_seconds)
        return result
    
    return wrapper

import os, subprocess
env = os.environ.copy()
env.update({
    "AI_NURSE_DISABLE_REDIS": "1",
    "PYTHONASYNCIODEBUG": "1",
    "PYTHONFAULTHANDLER": "1",
})
subprocess.run([os.path.join(".venv","bin","python"), "-m", "pytest",
                "tests/unit/test_disease_clinical_fallback.py::test_disease_fallback_no_requests",
                "-vv", "-s", "--maxfail=1", "--showlocals"], env=env)