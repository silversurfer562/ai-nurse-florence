"""
AI Nurse Florence - Healthcare AI Assistant
Following Service Layer Architecture from coding instructions
Build: 2025-10-04 11:05
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging following coding instructions
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import configuration following Configuration Management pattern
try:
    from src.utils.config import get_settings

    settings = get_settings()
    logger.info(f"Configuration loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
except Exception as e:
    logger.error(f"Configuration failed: {e}")

    # Fallback configuration
    class FallbackSettings:
        APP_NAME = "AI Nurse Florence"
        APP_VERSION = "2.4.0"
        ALLOWED_ORIGINS = ["http://localhost:3000"]
        EDUCATIONAL_BANNER = "Educational purposes only"

    settings = FallbackSettings()

# Load and register routers following Router Organization pattern
ROUTERS_LOADED = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan following coding instructions startup patterns."""
    # Startup
    logger.info(f"🏥 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Healthcare AI assistant - Educational use only, no PHI stored")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI app following coding instructions
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - Following security pattern from coding instructions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
try:
    from src.utils.rate_limit import RateLimitMiddleware

    app.add_middleware(RateLimitMiddleware)
    logger.info("Rate limiting enabled: 60 requests per minute")
except Exception as e:
    logger.warning(f"Rate limiting unavailable: {e}")

# Load routers following Router Organization pattern
try:
    from src.routers import load_routers

    logger.info("🔄 Loading routers with conditional imports...")
    api_router = load_routers()
    ROUTERS_LOADED = getattr(load_routers, "routers_loaded", {})
except Exception as e:
    logger.error(f"Failed to load routers: {e}")
    api_router = APIRouter()

# Phase 3: Enhanced Auth Routes (2024-12-26)
try:
    from src.routers.enhanced_auth import router as enhanced_auth_router

    api_router.include_router(enhanced_auth_router)
    ROUTERS_LOADED["enhanced_auth"] = True
except Exception as e:
    logger.warning(f"Enhanced auth router unavailable: {e}")
    ROUTERS_LOADED["enhanced_auth"] = False

# Phase 3.1: Session Monitoring Routes (2024-12-27)
try:
    from src.routers.session_monitoring import router as session_monitoring_router

    api_router.include_router(session_monitoring_router)
    ROUTERS_LOADED["session_monitoring"] = True
except Exception as e:
    logger.warning(f"Session monitoring router unavailable: {e}")
    ROUTERS_LOADED["session_monitoring"] = False

# Phase 4.1: Cache Monitoring Routes (2025-01-06)
try:
    from src.routers.cache_monitoring import router as cache_monitoring_router

    api_router.include_router(cache_monitoring_router)
    logger.info(
        "Cache monitoring router registered successfully - Phase 4.1 Enhanced Caching"
    )
    ROUTERS_LOADED["cache_monitoring"] = True
except Exception as e:
    logger.warning(f"Cache monitoring router unavailable: {e}")
    ROUTERS_LOADED["cache_monitoring"] = False

# Phase 4.2: Enhanced Literature Service Routes (2025-01-10)
try:
    from src.routers.enhanced_literature import router as enhanced_literature_router

    api_router.include_router(enhanced_literature_router)
    logger.info(
        "Enhanced literature router registered successfully - Phase 4.2 Additional Medical Services"
    )
    ROUTERS_LOADED["enhanced_literature"] = True
except Exception as e:
    logger.warning(f"Enhanced literature router unavailable: {e}")
    ROUTERS_LOADED["enhanced_literature"] = False

# Phase 4.2: Drug Interactions Routes (2025-01-10)
try:
    from src.routers.drug_interactions import router as drug_interactions_router

    api_router.include_router(drug_interactions_router)
    logger.info(
        "Drug interactions router registered successfully - Phase 4.2 Additional Medical Services"
    )
    ROUTERS_LOADED["drug_interactions"] = True
except Exception as e:
    logger.warning(f"Drug interactions router unavailable: {e}")
    ROUTERS_LOADED["drug_interactions"] = False

# Patient documents router (PDF generation)
try:
    from routers.patient_education_documents import router as patient_docs_router

    api_router.include_router(patient_docs_router)
    logger.info(
        "Patient documents router registered successfully - PDF generation enabled"
    )
    ROUTERS_LOADED["patient_docs"] = True
except Exception as e:
    logger.warning(f"Patient documents router unavailable: {e}")
    ROUTERS_LOADED["patient_docs"] = False

# User profile router
try:
    from routers.user_profile import router as user_profile_router

    api_router.include_router(user_profile_router)
    logger.info("User profile router registered successfully - Personalization enabled")
    ROUTERS_LOADED["user_profile"] = True
except Exception as e:
    logger.warning(f"User profile router unavailable: {e}")
    ROUTERS_LOADED["user_profile"] = False

# Admin router - protected routes for admin functions
try:
    from routers.admin import router as admin_router

    api_router.include_router(admin_router)
    logger.info("Admin router registered successfully")
    ROUTERS_LOADED["admin"] = True
except Exception as e:
    logger.warning(f"Admin router unavailable: {e}")
    ROUTERS_LOADED["admin"] = False

# Webhooks router - Railway deployment notifications
try:
    from routers.webhooks import router as webhooks_router

    app.include_router(webhooks_router)
    logger.info(
        "✅ Webhooks router registered successfully - Railway deployment notifications enabled"
    )
    ROUTERS_LOADED["webhooks"] = True
except Exception as e:
    logger.warning(f"Failed to register webhooks router: {e}")
    ROUTERS_LOADED["webhooks"] = False

# Content Settings Router - Diagnosis autocomplete and content management
try:
    from routers.content_settings import router as content_settings_router

    api_router.include_router(content_settings_router)
    logger.info("✅ Content settings router registered successfully")
    ROUTERS_LOADED["content_settings"] = True
except Exception as e:
    logger.warning(f"Failed to register content settings router: {e}")
    ROUTERS_LOADED["content_settings"] = False


# Diagnosis Search Endpoint - Disease name suggestions from database (FALLBACK)
# This is a fallback if content_settings router fails to load
@app.get("/api/v1/content-settings/diagnosis/search")
async def search_diagnoses_proxy(q: str, limit: int = 20):
    """
    Search for disease/diagnosis names from disease_aliases database.
    Used by clinical trials page autocomplete.
    """
    # Query disease_aliases database for matching diseases
    try:
        from sqlalchemy import create_engine, text

        from src.models.database import DATABASE_URL

        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            # Search for diseases where alias contains the query (case-insensitive)
            query_text = text(
                """
                SELECT DISTINCT
                    mondo_id as disease_id,
                    canonical_name as disease_name,
                    'FDA/MONDO' as category
                FROM disease_aliases
                WHERE LOWER(alias) LIKE LOWER(:search_term)
                   OR LOWER(canonical_name) LIKE LOWER(:search_term)
                ORDER BY
                    CASE
                        WHEN LOWER(alias) = LOWER(:exact_match) THEN 1
                        WHEN LOWER(canonical_name) = LOWER(:exact_match) THEN 2
                        WHEN LOWER(alias) LIKE LOWER(:search_term_start) THEN 3
                        WHEN LOWER(canonical_name) LIKE LOWER(:search_term_start) THEN 4
                        ELSE 5
                    END,
                    canonical_name
                LIMIT :result_limit
            """
            )

            result = conn.execute(
                query_text,
                {
                    "search_term": f"%{q}%",
                    "exact_match": q,
                    "search_term_start": f"{q}%",
                    "result_limit": limit,
                },
            )

            diseases = [
                {"disease_id": row[0], "disease_name": row[1], "category": row[2]}
                for row in result
            ]

            if diseases:
                logger.debug(
                    f"Found {len(diseases)} diseases matching '{q}' in database"
                )
                return diseases

    except Exception as e:
        logger.warning(f"Disease database unavailable: {e}")

    # Comprehensive disease database with common variants and synonyms
    common_diseases = {
        "dia": [
            "Diabetes Mellitus Type 1",
            "Diabetes Mellitus Type 2",
            "Diabetes Mellitus",
            "Diabetes Insipidus",
            "Diabetic Ketoacidosis",
            "Diabetic Neuropathy",
            "Diabetic Retinopathy",
            "Diabetic Nephropathy",
            "Diabetic Foot",
            "Diarrhea",
            "Diverticulitis",
            "Diverticulosis",
        ],
        "hyper": [
            "Hypertension",
            "Hypertensive Crisis",
            "Hypertensive Heart Disease",
            "Hyperthyroidism",
            "Hyperlipidemia",
            "Hyperglycemia",
            "Hyperkalemia",
            "Hypernatremia",
            "Hypercalcemia",
            "Hypertrophic Cardiomyopathy",
        ],
        "hypo": [
            "Hypotension",
            "Hypothyroidism",
            "Hypoglycemia",
            "Hypokalemia",
            "Hyponatremia",
            "Hypocalcemia",
            "Hypovolemia",
        ],
        "asth": ["Asthma", "Asthenia", "Astigmatism"],
        "canc": [
            "Cancer",
            "Lung Cancer",
            "Breast Cancer",
            "Colon Cancer",
            "Prostate Cancer",
            "Pancreatic Cancer",
            "Skin Cancer",
            "Melanoma",
            "Leukemia",
            "Lymphoma",
        ],
        "heart": [
            "Heart Disease",
            "Heart Failure",
            "Congestive Heart Failure",
            "Heart Attack",
            "Myocardial Infarction",
            "Coronary Artery Disease",
            "Atrial Fibrillation",
            "Arrhythmia",
        ],
        "stroke": [
            "Stroke",
            "Ischemic Stroke",
            "Hemorrhagic Stroke",
            "Transient Ischemic Attack",
            "TIA",
        ],
        "arthri": [
            "Arthritis",
            "Rheumatoid Arthritis",
            "Osteoarthritis",
            "Psoriatic Arthritis",
            "Gout",
            "Gouty Arthritis",
        ],
        "depress": [
            "Depression",
            "Major Depressive Disorder",
            "Bipolar Disorder",
            "Dysthymia",
            "Seasonal Affective Disorder",
        ],
        "anxi": [
            "Anxiety",
            "Anxiety Disorder",
            "Generalized Anxiety Disorder",
            "Panic Disorder",
            "Panic Attack",
            "Social Anxiety Disorder",
        ],
        "copd": [
            "COPD",
            "Chronic Obstructive Pulmonary Disease",
            "Emphysema",
            "Chronic Bronchitis",
        ],
        "pneum": ["Pneumonia", "Pneumonitis", "Pneumothorax"],
        "renal": [
            "Renal Failure",
            "Chronic Kidney Disease",
            "Acute Kidney Injury",
            "Kidney Stones",
            "Nephrolithiasis",
        ],
        "hepat": [
            "Hepatitis A",
            "Hepatitis B",
            "Hepatitis C",
            "Hepatic Cirrhosis",
            "Liver Cirrhosis",
            "Fatty Liver Disease",
        ],
        "sep": ["Sepsis", "Septic Shock", "Septicemia"],
        "alzh": ["Alzheimer's Disease", "Dementia", "Vascular Dementia"],
        "park": ["Parkinson's Disease", "Parkinsonism"],
        "epi": ["Epilepsy", "Seizure Disorder", "Status Epilepticus"],
        "schiz": ["Schizophrenia", "Schizoaffective Disorder"],
        "ost": ["Osteoporosis", "Osteopenia"],
        "anemia": [
            "Anemia",
            "Iron Deficiency Anemia",
            "Pernicious Anemia",
            "Sickle Cell Anemia",
        ],
        "celiac": ["Celiac Disease", "Gluten Sensitivity"],
        "crohn": [
            "Crohn's Disease",
            "Ulcerative Colitis",
            "Inflammatory Bowel Disease",
        ],
        "psori": ["Psoriasis", "Psoriatic Arthritis"],
        "lupus": ["Lupus", "Systemic Lupus Erythematosus", "SLE"],
        "ms": ["Multiple Sclerosis", "MS"],
        "hiv": ["HIV", "AIDS", "HIV/AIDS"],
        "tb": ["Tuberculosis", "TB", "Latent Tuberculosis"],
    }

    q_lower = q.lower()
    suggestions = []

    # Find matching suggestions
    for prefix, diseases in common_diseases.items():
        if q_lower.startswith(prefix):
            suggestions = [d for d in diseases if q_lower in d.lower()]
            break

    # If no prefix match, search all diseases containing the query
    if not suggestions:
        for diseases in common_diseases.values():
            for disease in diseases:
                if q_lower in disease.lower() and disease not in suggestions:
                    suggestions.append(disease)

    # Return suggestions or echo query
    if suggestions:
        return [
            {"disease_id": idx, "disease_name": name, "category": "Common"}
            for idx, name in enumerate(suggestions[:limit])
        ]

    return [{"disease_id": 0, "disease_name": q, "category": "General"}]


# Additional routers temporarily disabled (genes, disease_glossary)
logger.info("ℹ️ Using simplified diagnosis search (proxy to disease service)")


# Serve main healthcare interface at root
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_main_interface(request: Request):
    """Serve the React app."""
    try:
        # Try React build first
        if os.path.exists("frontend/dist/index.html"):
            with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        # Fallback to static HTML
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        # Fallback to template if static file doesn't exist
        return templates.TemplateResponse("index.html", {"request": request})


# API status endpoint
@app.get("/status", response_class=JSONResponse, include_in_schema=False)
async def status():
    """Status endpoint for monitoring."""
    return {
        "status": "operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "routers_loaded": len([k for k, v in ROUTERS_LOADED.items() if v]),
        "total_routers": len(ROUTERS_LOADED),
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy", "service": "ai-nurse-florence"}


# Wizards hub
@app.get("/wizards", response_class=HTMLResponse, include_in_schema=False)
async def serve_wizard_hub():
    """Serve the wizard hub interface."""
    try:
        with open("frontend/src/pages/wizard-hub.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="""
        <!DOCTYPE html>
        <html><head><title>Clinical Wizards</title></head>
        <body>
            <h1>Clinical Wizards</h1>
            <ul>
                <li><a href="/wizards/sbar">SBAR Report Generator</a></li>
                <li><a href="/wizards/treatment-plan">Treatment Plan Wizard</a></li>
                <li><a href="/wizards/patient-education">Patient Education</a></li>
            </ul>
        </body></html>
        """
        )


# Education router (now using v1/patient-education)
try:
    from routers.education import router as education_router

    app.include_router(education_router, prefix="/api")
    logger.info("✅ Education router loaded successfully")
    ROUTERS_LOADED["education"] = True
except Exception as e:
    logger.warning(f"⚠️ Education router unavailable: {e}")
    ROUTERS_LOADED["education"] = False

# Include the main API router
app.include_router(api_router)

# Mount static files and frontend
os.makedirs("static", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Mount React app build
if os.path.exists("frontend/dist"):
    logger.info("✅ frontend/dist exists, mounting assets")
    app.mount(
        "/assets", StaticFiles(directory="frontend/dist/assets"), name="react-assets"
    )
    # Mount translation files
    if os.path.exists("frontend/dist/locales"):
        logger.info("✅ frontend/dist/locales exists, mounting /locales route")
        # List locales to verify
        locales_dirs = os.listdir("frontend/dist/locales")
        logger.info(f"📁 Available locales: {locales_dirs}")
        app.mount(
            "/locales", StaticFiles(directory="frontend/dist/locales"), name="locales"
        )
    else:
        logger.warning("⚠️ frontend/dist/locales NOT FOUND - translation files will 404")
else:
    logger.warning("⚠️ frontend/dist NOT FOUND - React app not available")

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("=== AI NURSE FLORENCE STARTUP ===")
    logger.info(f"App: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info("Environment: Railway" if os.getenv("RAILWAY_ENVIRONMENT") else "Local")
    logger.info(f"Routers loaded: {len([k for k, v in ROUTERS_LOADED.items() if v])}")
    logger.info(f"Educational banner: {settings.EDUCATIONAL_BANNER[:50]}...")
    logger.info("Healthcare AI assistant ready - Educational use only")

    # Session cleanup service
    try:
        from src.services.session_cleanup import start_cleanup_service

        await start_cleanup_service()
        logger.info("✅ Session cleanup service started")
    except Exception as e:
        logger.warning(f"Session cleanup service unavailable: {e}")

    # Cache updater services - Disabled temporarily
    logger.info("⚠️ Cache updater services disabled - enable after fixing startup")

    # Database initialization - Skip for now
    logger.info(
        "⚠️ Database initialization skipped - run migrations separately if needed"
    )

    # Log effective BASE_URL
    base_url = os.getenv("BASE_URL", "http://0.0.0.0:8080")
    logger.info(f"Effective BASE_URL: {base_url}")

    logger.info("🚀 Application startup complete")


# Catchall route for React Router (SPA client-side routing)
@app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
async def catch_all(full_path: str):
    """
    Catchall route for React Router client-side routing.
    Serves index.html for all non-API, non-static routes.
    """
    # Skip if no path (root handled above)
    if not full_path:
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # For file extensions, let them 404 naturally (don't serve React app)
    if "." in full_path.split("/")[-1]:
        # This looks like a file request (e.g., .json, .js, .css)
        # Don't serve React app for these
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Don't intercept API routes, docs, or health endpoints
    if (
        full_path.startswith("api")
        or full_path.startswith("docs")
        or full_path.startswith("openapi")
        or full_path == "health"
        or full_path == "status"
    ):
        from fastapi import HTTPException

        raise HTTPException(status_code=404)

    # Serve React app for all other routes (SPA client-side routing)
    if os.path.exists("frontend/dist/index.html"):
        with open("frontend/dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return HTMLResponse(content="<h1>Not Found</h1>", status_code=404)
