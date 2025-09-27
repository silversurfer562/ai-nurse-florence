import time
import pytest

from src.utils.redis_cache import (
    cache_set_sync,
    cache_get_sync,
    cache_delete_sync,
    cached,
)


def test_cache_set_get_delete_sync():
    key = "test_sync_unit:1"
    # ensure clean state
    cache_delete_sync(key)

    assert cache_get_sync(key) is None

    cache_set_sync(key, {"v": 42}, ttl_seconds=2)
    got = cache_get_sync(key)
    assert isinstance(got, dict) and got.get("v") == 42

    cache_delete_sync(key)
    assert cache_get_sync(key) is None


def test_cached_decorator_sync_ttl():
    @cached(ttl_seconds=1, key_prefix="test_cached")
    def mul(a, b):
        return a * b

    v1 = mul(3, 7)
    v2 = mul(3, 7)
    assert v1 == 21 and v2 == 21

    # after ttl, value may be recomputed but still equal
    time.sleep(1.2)
    v3 = mul(3, 7)
    assert v3 == 21
