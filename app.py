from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Routers (import existing project routers)
from routers import (
    healthcheck,
    disease,
    pubmed,
    trials,
    medlineplus,
    summarize,
    patient_education,
    readability,
)

load_dotenv()

API_BEARER = os.getenv("API_BEARER", "").strip()
CORS_ORIGINS = [o for o in os.getenv("CORS_ORIGINS", "").split(",") if o]

# Read OpenAI key from env (do NOT hardcode secrets)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Do NOT import OpenAI at module import time; make it optional / lazy
client = None

app = FastAPI(title="Nurses API", docs_url="/docs", redoc_url="/redoc")

# CORS
if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount routers
app.include_router(healthcheck.router)
app.include_router(disease.router)
app.include_router(pubmed.router)
app.include_router(trials.router)
app.include_router(medlineplus.router)
app.include_router(summarize.router)
app.include_router(patient_education.router)
app.include_router(readability.router)

EXEMPT_PATHS = {"/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", "/health"}


@app.middleware("http")
async def bearer_middleware(request: Request, call_next):
    path = str(request.url.path)
    if request.method == "OPTIONS" or path in EXEMPT_PATHS or path.startswith("/static"):
        return await call_next(request)

    if not API_BEARER:
        return await call_next(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    token = auth.split(" ", 1)[1].strip()
    if token != API_BEARER:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


@app.on_event("startup")
async def startup_event():
    global client
    print("Nurses API starting up")
    if OPENAI_API_KEY:
        try:
            # lazy import so app can run without openai installed
            from openai import OpenAI as OpenAIClient

            client = OpenAIClient(api_key=OPENAI_API_KEY)
            print("OpenAI client configured")
        except Exception:
            client = None
            print(
                "OpenAI package not installed; set OPENAI_API_KEY and install 'openai' to enable client."
            )
    else:
        print("WARNING: OPENAI_API_KEY not set; OpenAI calls will fail if used.")

