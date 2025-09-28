from __future__ import annotations

from typing import Any, Optional
from types import ModuleType
import importlib
import asyncio

httpx: Optional[ModuleType] = None
requests: Optional[ModuleType] = None
_has_httpx = False
_has_requests = False
try:
    _httpx_mod = importlib.import_module("httpx")
    httpx = _httpx_mod
    _has_httpx = True
except Exception:
    _has_httpx = False

try:
    _requests_mod = importlib.import_module("requests")
    requests = _requests_mod
    _has_requests = True
except Exception:
    _has_requests = False

from .exceptions import ExternalServiceException


async def safe_get_json(
    url: str, params: Optional[dict[str, Any]] = None, timeout: float = 15.0
) -> Any:
    """Typed helper to GET JSON from a URL using httpx async when available,
    falling back to requests executed in a thread. Raises ExternalServiceException
    on failure.
    """
    if _has_httpx and httpx is not None:
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            raise ExternalServiceException("http_client", str(e), e)

    # fallback to requests in a thread
    if not _has_requests or requests is None:
        raise ExternalServiceException("http_client", "No HTTP client available")

    def _sync_get(u: str, p: Optional[dict[str, Any]], t: float) -> Any:
        if not _has_requests or requests is None:
            raise ExternalServiceException("http_client", "requests not available")
        r = requests.get(u, params=p, timeout=t)
        r.raise_for_status()
        return r.json()

    try:
        return await asyncio.to_thread(_sync_get, url, params, timeout)
    except Exception as e:
        raise ExternalServiceException("http_client", str(e), e)


# Synchronous wrapper useful for testing or sync callers
def safe_get_json_sync(
    url: str, params: Optional[dict[str, Any]] = None, timeout: float = 15.0
) -> Any:
    if _has_requests and requests is not None:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    raise ExternalServiceException("http_client", "No sync HTTP client available")
