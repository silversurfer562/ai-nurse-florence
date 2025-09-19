# app.py — FastAPI entrypoint for Vercel (ASGI), safe config checks, rate limiting
import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse, Response

from utils.config import get_settings
from utils.rate_limit import RateLimiter

app = FastAPI(
    title="AI Nurse Florence",
    version="1.0.0",
    docs_url="/docs",           # keep or disable in prod
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ---------- Helpers (no import-time crashes) ----------

def _missing_envs() -> list[str]:
    s = get_settings()  # lazy; reads envs at first use
    missing = []
    if not s.OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not s.API_BEARER:
        missing.append("API_BEARER")
    return missing

def require_config():
    missing = _missing_envs()
    if missing:
        # Friendly 500 rather than a stack trace
        raise HTTPException(
            status_code=500,
            detail={
                "status": "misconfigured",
                "missing": missing,
                "how_to_fix": (
                    "Vercel → Project → Settings → Environment Variables (Production) → "
                    "add values → Redeploy."
                ),
            },
        )

def rate_limit(request: Request, key: str = "global", per_minute: int = 60):
    ip = request.client.host if request.client else "unknown"
    limiter = RateLimiter()
    if not limiter.allow(key, ip, limit=per_minute, window_sec=60):
        raise HTTPException(status_code=429, detail="Too many requests")

# ---------- Minimal system routes ----------

@app.get("/favicon.ico")
async def favicon() -> Response:
    # Prevent browsers from turning favicon fetches into noisy 500s
    return Response(status_code=204)

@app.get("/api/health")
async def health() -> Dict[str, Any]:
    return {"ok": True, "ts": int(time.time())}

@app.get("/", tags=["system"])
async def root(request: Request, _=Depends(require_config)):
    rate_limit(request, key="root", per_minute=30)
    return {
        "status": "ok",
        "name": "AI Nurse Florence",
        "message": "Server is live and configuration looks good.",
    }

# ---------- Your domain routes (plug back in here) ----------

# Include webhook router for Notion-GitHub integration
from routers.webhooks import router as webhook_router
app.include_router(webhook_router)

# If you have existing routers, include them here, e.g.:
#
# from api.v1.disease import router as disease_router
# app.include_router(disease_router, prefix="/v1", tags=["disease"])
#
# Or if you defined endpoints directly in this file previously,
# paste them below. To protect a route with the same checks, add:
#
#   async def some_route(request: Request, _=Depends(require_config)):
#       rate_limit(request, key="some_route", per_minute=60)
#       ... your logic ...
#

# ---------- Local dev entry (ignored by Vercel) ----------

if __name__ == "__main__":
    # For local testing: uvicorn app:app --reload --port 8088
    try:
        import uvicorn  # type: ignore
        uvicorn.run("app:app", host="0.0.0.0", port=8088, reload=True)
    except Exception:
        # uvicorn not required on Vercel; safe to ignore locally if missing
        pass

# Checks for api-bearer enviroment variable in vercel deployment
def require_bearer(request: Request):
    expected = (get_settings().API_BEARER or "").strip()
    auth = request.headers.get("authorization", "")
    token = auth.split(" ", 1)[1] if auth.startswith("Bearer ") else ""
    if not expected or token != expected:
        raise HTTPException(401, "Unauthorized")

@app.get("/admin/stats")
async def admin_stats(
    request: Request,
    _=Depends(lambda: require_config(require_bearer=True)),
    __=Depends(require_bearer),
):
    return {"ok": True}
