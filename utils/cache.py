"""
Caching service for the application.

This module provides a simple in-memory caching system with TTL support.
For production use, consider using Redis or another distributed cache.
"""
import time
import functools
from typing import Any, Dict, Optional, TypeVar, Callable, Tuple
import threading
from utils.logging import get_logger

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

class CacheService:
    """
    Simple in-memory cache with TTL support.
    
    This cache is thread-safe and supports time-based expiration.
    """
    
    def __init__(self):
        """Initialize the cache."""
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = threading.RLock()
        
    def get(self, key: str) -> Tuple[Optional[Any], bool]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            A tuple of (value, hit) where hit is True if the key was found
            and not expired, False otherwise.
        """
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                # Check if the value is still valid
                if time.time() < timestamp:
                    logger.debug(f"Cache hit for key: {key}")
                    if _has_metrics:
                        record_cache_hit(key)
                    return value, True
                else:
                    # Remove expired value
                    logger.debug(f"Cache expired for key: {key}")
                    del self._cache[key]
            
            logger.debug(f"Cache miss for key: {key}")
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
        with self._lock:
            expiry = time.time() + ttl_seconds
            self._cache[key] = (value, expiry)
            logger.debug(f"Cached key: {key}, expires in {ttl_seconds}s")
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache key: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            logger.debug("Cache cleared")
    
    def cleanup(self) -> int:
        """
        Remove all expired cache entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            now = time.time()
            expired_keys = [k for k, (_, exp) in self._cache.items() if exp <= now]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)


# Global cache instance
_cache = CacheService()

def get_cache() -> CacheService:
    """
    Get the global cache instance.
    
    Returns:
        The global CacheService instance
    """
    return _cache


def cached(ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time-to-live in seconds (default: 300)
        
    Returns:
        A decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
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