"""
Tests for the caching functionality.

This module tests the cache service and cached decorator.
"""
import pytest
import time
from unittest.mock import MagicMock, patch

from utils.cache import CacheService, cached, get_cache


def test_cache_service_get_set():
    """Test basic cache get and set operations."""
    cache = CacheService()
    
    # Test cache miss
    value, hit = cache.get("test_key")
    assert hit is False
    assert value is None
    
    # Test cache hit
    cache.set("test_key", "test_value", ttl_seconds=10)
    value, hit = cache.get("test_key")
    assert hit is True
    assert value == "test_value"


def test_cache_service_expiry():
    """Test cache entry expiration."""
    cache = CacheService()
    
    # Set with very short TTL
    cache.set("test_key", "test_value", ttl_seconds=0.1)
    
    # Should be a hit immediately
    value, hit = cache.get("test_key")
    assert hit is True
    assert value == "test_value"
    
    # Wait for expiration
    time.sleep(0.2)
    
    # Should be a miss after expiry
    value, hit = cache.get("test_key")
    assert hit is False
    assert value is None


def test_cache_service_delete():
    """Test cache delete operation."""
    cache = CacheService()
    
    # Set a value
    cache.set("test_key", "test_value")
    
    # Delete should return True for existing key
    assert cache.delete("test_key") is True
    
    # Should be a miss after delete
    value, hit = cache.get("test_key")
    assert hit is False
    
    # Delete should return False for non-existent key
    assert cache.delete("nonexistent_key") is False


def test_cache_service_clear():
    """Test cache clear operation."""
    cache = CacheService()
    
    # Set multiple values
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    # Clear all entries
    cache.clear()
    
    # All keys should be missing
    assert cache.get("key1")[1] is False
    assert cache.get("key2")[1] is False


def test_cache_decorator():
    """Test the cached decorator."""
    # Create a mock function to cache
    mock_func = MagicMock(return_value="test_result")
    
    # Apply the cached decorator
    cached_func = cached(ttl_seconds=10)(mock_func)
    
    # First call should invoke the function
    result1 = cached_func("arg1", kwarg1="value1")
    assert result1 == "test_result"
    mock_func.assert_called_once_with("arg1", kwarg1="value1")
    
    # Reset the mock to verify it's not called again
    mock_func.reset_mock()
    
    # Second call with same args should use cache
    result2 = cached_func("arg1", kwarg1="value1")
    assert result2 == "test_result"
    mock_func.assert_not_called()
    
    # Call with different args should invoke the function again
    result3 = cached_func("arg2", kwarg1="value1")
    assert result3 == "test_result"
    mock_func.assert_called_once_with("arg2", kwarg1="value1")