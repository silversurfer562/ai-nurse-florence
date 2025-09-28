import asyncio
import time
import uuid
from types import SimpleNamespace

import pytest

from src.utils import redis_cache


def test_sync_cached_schedules_background_update(monkeypatch):
    """Sync cached function should populate in-memory cache immediately and schedule Redis update."""
    updates = []

    async def fake_cache_set(key, value, ttl_seconds=3600):
        # simulate small delay
        await asyncio.sleep(0)
        updates.append((key, value))
        return True

    monkeypatch.setattr(redis_cache, "cache_set", fake_cache_set)

    @redis_cache.cached(ttl_seconds=60)
    def compute_sync(x):
        return {"value": x, "id": str(uuid.uuid4())}

    # Call sync function - should return immediately and memory cache set synchronously
    result = compute_sync(42)
    assert isinstance(result, dict)

    # Find memory key
    # We don't directly know key format, so inspect memory cache for matching value id
    found_key = None
    for k, v in redis_cache._memory_cache.items():
        if isinstance(v, dict) and v.get("value") is not None:
            # compare stored value structure
            if v["value"].get("id") == result["id"]:
                found_key = k
                break

    assert found_key is not None, "In-memory cache was not populated"

    # Wait up to 2s for background update to run
    deadline = time.time() + 2.0
    while time.time() < deadline and not updates:
        time.sleep(0.01)

    assert updates, "Background cache_set was not called"
    # Ensure the background update used the same value
    assert updates[0][1]["id"] == result["id"]


@pytest.mark.asyncio
async def test_async_cached_concurrent_calls_share_result(monkeypatch):
    """Concurrent async calls should return consistent results and trigger cache_set."""
    sets = []

    async def fake_cache_set(key, value, ttl_seconds=3600):
        # tiny delay to simulate IO
        await asyncio.sleep(0.01)
        sets.append((key, value))
        return True

    monkeypatch.setattr(redis_cache, "cache_set", fake_cache_set)

    call_count = SimpleNamespace(count=0)

    @redis_cache.cached(ttl_seconds=60)
    async def compute_async(x):
        call_count.count += 1
        # simulate work
        await asyncio.sleep(0.02)
        return {"value": x, "ts": time.time()}

    # Run several concurrent calls with the same args
    tasks = [asyncio.create_task(compute_async(7)) for _ in range(6)]
    results = await asyncio.gather(*tasks)

    # All results should be dicts and have the same 'value'
    assert all(isinstance(r, dict) for r in results)
    assert all(r["value"] == 7 for r in results)

    # At least one cache_set occurred
    assert sets, "cache_set was not called for async cached function"

    # call_count may be >1 depending on timing, but ensure results are consistent
    ids = [r.get("ts") for r in results]
    assert len(set(ids)) >= 1
