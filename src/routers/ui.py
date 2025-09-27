"""
Enhanced UI Router - Progressive enhancement endpoints
Following Conditional Imports Pattern
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Conditional imports for enhanced UI features
try:
    templates = Jinja2Templates(directory="src/templates")
    _has_templates = True
except Exception:
    _has_templates = False

router = APIRouter(prefix="/ui", tags=["Enhanced UI"])

@router.get("/clinical-decision", response_class=HTMLResponse)
async def clinical_decision_interface(request: Request):
    """
    Enhanced clinical decision support interface
    Following progressive enhancement strategy
    """
    
    if not _has_templates:
        return HTMLResponse("""
            <html><body>
                <h1>Clinical Decision Support</h1>
                <p>Enhanced UI not available. Use <a href="/docs">API documentation</a> instead.</p>
            </body></html>
        """)
    
    # TODO: Implement template rendering with React components
    # TODO: Add clinical workflow context
    # TODO: Progressive enhancement fallbacks
    
    return templates.TemplateResponse("clinical_decision.html", {
        "request": request,
        "title": "Clinical Decision Support",
        "has_react": True
    })

@router.get("/sbar-wizard", response_class=HTMLResponse)
async def sbar_wizard_interface(request: Request):
    """SBAR report generation wizard interface"""
    
    if not _has_templates:
        return HTMLResponse("""
            <html><body>
                <h1>SBAR Wizard</h1>
                <p>Enhanced wizard not available. Use API endpoints instead.</p>
            </body></html>
        """)
    
    # TODO: Implement SBAR wizard template
    # TODO: Multi-step workflow interface
    # TODO: React component integration
    
    return templates.TemplateResponse("sbar_wizard.html", {
        "request": request,
        "title": "SBAR Report Wizard",
        "wizard_type": "sbar"
    })
