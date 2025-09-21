from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging

logger = logging.getLogger("nurses_api")
logging.basicConfig(level=logging.INFO)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        resp = await call_next(request)
        elapsed = (time.time() - start) * 1000
        logger.info(
            f"{request.method} {request.url.path} -> {resp.status_code} [{elapsed:.1f}ms]"
        )
        return resp
