"""
Enhanced Swagger UI configuration for clinical decision support
Following Service Layer Architecture and Conditional Imports Pattern
"""

from typing import Any, Dict

from fastapi import Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.utils.config import get_settings

# Conditional ChatGPT Store integration following coding instructions pattern
try:
    # Import module only to detect availability; avoid importing unused symbols
    import importlib.util

    _has_chatgpt_integration = (
        importlib.util.find_spec("src.utils.chatgpt_store") is not None
    )
except Exception:
    _has_chatgpt_integration = False

settings = get_settings()


def get_enhanced_openapi_schema(app) -> Dict[str, Any]:
    """
    Enhanced OpenAPI schema for healthcare professional documentation
    Following Service Layer Architecture pattern from coding instructions
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Nurse Florence - Clinical Decision Support System",
        version="2.1.0",
        description="""
        **Professional clinical decision support for nursing professionals**
        
        🩺 **Evidence-based interventions** and risk assessment tools
        📝 **Clinical documentation** - SBAR reports, care plans, assessments  
        🧙‍♀️ **Multi-step care planning** wizards with evidence integration
        📚 **Literature integration** - PubMed, clinical guidelines, drug databases
        
        ---
        
        **🏥 Educational Use Only**
        
        Clinical decision support tool for nursing education and professional development. 
        Not for diagnostic purposes. Clinical judgment always required.
        
        **No PHI stored. Session isolation. Audit logging enabled.**
        """,
        routes=app.routes,
    )

    # ChatGPT Store specific schema enhancements (conditional)
    if _has_chatgpt_integration:
        openapi_schema = _enhance_schema_for_chatgpt_store(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_enhanced_swagger_ui_html(request: Request):
    """
    Enhanced Swagger UI with clinical workflow optimizations
    Following conditional loading pattern from coding instructions
    """

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="AI Nurse Florence - Clinical Decision Support",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="/static/css/clinical-swagger.css",  # Custom healthcare theme
        swagger_ui_parameters={
            # Clinical workflow optimizations
            "defaultModelsExpandDepth": 3,
            "filter": True,
            "tryItOutEnabled": True,
            "syntaxHighlight.theme": "agate",
        },
    )


def _enhance_schema_for_chatgpt_store(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add ChatGPT Store specific enhancements.

    Future enhancements planned:
    - Authentication schemes for ChatGPT Store
    - Professional validation endpoints
    - Institution-specific customization schemas

    See: src/routers/chatgpt_store.py for implementation details
    """
    return schema
