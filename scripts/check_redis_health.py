"""Check that code gracefully degrades when Redis is disabled.

This script sets AI_NURSE_DISABLE_REDIS=1 and ensures that
`src.utils.redis_cache.get_redis_client()` returns quickly and does not
hang or return an active client. Exit code is non-zero on failure so
CI will fail loudly when a change makes Redis required.
"""
import os
import sys
import asyncio

# Force the tests/CI path to disable Redis for the check
os.environ.setdefault("AI_NURSE_DISABLE_REDIS", "1")

try:
    from src.utils.redis_cache import get_redis_client
except Exception as e:
    print("ERROR: failed to import src.utils.redis_cache:", e)
    sys.exit(2)


async def _check():
    try:
        # run with a short timeout; if get_redis_client blocks, fail
        client = await asyncio.wait_for(get_redis_client(), timeout=3)
        if client:
            print("ERROR: get_redis_client() returned a client while AI_NURSE_DISABLE_REDIS=1")
            return 3
        print("OK: get_redis_client() returned falsy while Redis disabled")
        return 0
    except asyncio.TimeoutError:
        print("ERROR: get_redis_client() timed out — Redis appears to be required or the call hung")
        return 4
    except Exception as e:
        # Accept exceptions as a sign of graceful degradation if they are expected
        print("ERROR: get_redis_client() raised an exception:", e)
        return 5


if __name__ == "__main__":
    code = asyncio.run(_check())
    sys.exit(code)
