from fastapi import APIRouter
from fastapi.responses import Response
import yaml

router = APIRouter()

@router.get("/openapi.yaml")
async def get_openapi_yaml():
    """Serve OpenAPI spec in YAML for GPT Store"""
    
    # Get the OpenAPI JSON from your app
    import requests
    try:
        # Fetch your existing OpenAPI spec
        response = requests.get("https://ai-nurse-florence-production.up.railway.app/openapi.json")
        openapi_json = response.json()
    except Exception:
        # Fallback minimal spec
        openapi_json = {
            "openapi": "3.0.0",
            "info": {
                "title": "AI Nurse Florence",
                "version": "2.0.1",
                "description": "Clinical documentation assistant for nurses"
            },
            "servers": [
                {"url": "https://ai-nurse-florence-production.up.railway.app"}
            ]
        }
    
    # Add GPT Store specific metadata
    openapi_json["info"]["x-openai-manifest"] = {
        "api": {
            "type": "openapi",
            "url": "https://ai-nurse-florence-production.up.railway.app/openapi.yaml"
        },
        "auth": {
            "type": "none"  # Change to "oauth" or "api_key" when ready
        },
        "name_for_model": "nurse_florence",
        "description_for_model": "Help nurses create clinical documentation including SBAR reports, patient education, and professional communications."
    }
    
    yaml_content = yaml.dump(openapi_json, sort_keys=False, default_flow_style=False)
    return Response(content=yaml_content, media_type="application/x-yaml")

