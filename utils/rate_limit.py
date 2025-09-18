import time
from typing import Dict, Tuple, List
from utils.config import get_settings

class RateLimiter:
    """
    Very small in-memory sliding-window limiter. Good enough for serverless dev.
    Resets per instance (fine for Vercel testing).
    """
    _hits: Dict[Tuple[str, str], List[float]] = {}
    window_sec = 60
    limit = 60  # 60 hits per minute per (key, id)

    def __init__(self):
        self.settings = get_settings()

    def allow(self, key: str, ident: str, limit: int = None, window_sec: int = None) -> bool:
        limit = limit or self.limit
        window = window_sec or self.window_sec
        now = time.time()
        bucket = self._hits.setdefault((key, ident), [])
        # drop old
        cutoff = now - window
        i = 0
        for t in bucket:
            if t >= cutoff:
                break
            i += 1
        if i:
            del bucket[:i]
        # check + record
        if len(bucket) >= limit:
            return False
        bucket.append(now)
        return True
