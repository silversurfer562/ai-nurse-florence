from fastapi import FastAPI
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

# Create FastAPI app
app = FastAPI(title="AI Nurse Florence", version="1.0.0")

@app.get("/")
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": "1.0.0",
        "message": "AI Nurse Florence - Healthcare AI Assistant",
        "features": ["health-check", "disease-lookup", "pubmed-search", "clinical-trials"],
        "environment": "production"
    }

# Educational banner for all medical responses
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

# Simple medical knowledge for common conditions
DISEASE_DB = {
    "hypertension": {
        "name": "Hypertension (High Blood Pressure)",
        "summary": "A condition where blood pressure in arteries is persistently elevated. Normal BP is <120/80 mmHg. Hypertension is ≥130/80 mmHg. Often called 'silent killer' as it may have no symptoms.",
        "references": [
            {"title": "AHA Blood Pressure Guidelines", "url": "https://www.heart.org/en/health-topics/high-blood-pressure", "source": "American Heart Association"}
        ]
    },
    "diabetes": {
        "name": "Diabetes Mellitus",
        "summary": "A group of metabolic disorders characterized by high blood sugar levels. Type 1: autoimmune destruction of insulin-producing cells. Type 2: insulin resistance and relative insulin deficiency.",
        "references": [
            {"title": "ADA Diabetes Standards", "url": "https://diabetescare.diabetesjournals.org/", "source": "American Diabetes Association"}
        ]
    },
    "pneumonia": {
        "name": "Pneumonia",
        "summary": "Infection that inflames air sacs in lungs, which may fill with fluid. Symptoms include cough with phlegm, fever, chills, difficulty breathing. Can be caused by bacteria, viruses, or fungi.",
        "references": [
            {"title": "CDC Pneumonia Information", "url": "https://www.cdc.gov/pneumonia/", "source": "CDC"}
        ]
    },
    "asthma": {
        "name": "Asthma",
        "summary": "Chronic respiratory condition where airways narrow, swell, and produce extra mucus. Symptoms include wheezing, shortness of breath, chest tightness, and coughing.",
        "references": [
            {"title": "NHLBI Asthma Guidelines", "url": "https://www.nhlbi.nih.gov/health/asthma", "source": "NHLBI"}
        ]
    }
}

def lookup_disease(term):
    """Simple disease lookup function"""
    term_lower = term.lower().strip()
    
    # Direct match
    if term_lower in DISEASE_DB:
        disease_info = DISEASE_DB[term_lower]
        return {
            "banner": EDU_BANNER,
            "query": term,
            "name": disease_info["name"],
            "summary": disease_info["summary"],
            "references": disease_info["references"],
            "status": "found"
        }
    
    # Partial matches
    for key, disease_info in DISEASE_DB.items():
        if term_lower in key or key in term_lower:
            return {
                "banner": EDU_BANNER,
                "query": term,
                "name": disease_info["name"],
                "summary": disease_info["summary"],
                "references": disease_info["references"],
                "status": "partial_match"
            }
    
    # No match found
    return {
        "banner": EDU_BANNER,
        "query": term,
        "name": None,
        "summary": f"No information found for '{term}'. Try searching for common conditions like 'hypertension', 'diabetes', 'pneumonia', or 'asthma'.",
        "references": [],
        "status": "not_found",
        "available_conditions": list(DISEASE_DB.keys())
    }

# Simple handler to provide medical AI endpoints
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route handling
        if path == '/api/v1/health':
            response = {
                "status": "healthy",
                "service": "ai-nurse-florence",
                "version": "1.0.0",
                "message": "AI Nurse Florence - Healthcare AI Assistant",
                "features": ["health-check", "disease-lookup", "pubmed-search", "clinical-trials"],
                "environment": "production",
                "banner": EDU_BANNER
            }
        elif path == '/api/v1/disease':
            # Get query parameter
            q = query_params.get('q', [''])[0]
            if q:
                response = lookup_disease(q)
            else:
                response = {
                    "banner": EDU_BANNER,
                    "service": "disease-lookup",
                    "message": "Please provide a disease or condition name using ?q=condition_name",
                    "example": "/api/v1/disease?q=hypertension",
                    "available_conditions": list(DISEASE_DB.keys()),
                    "status": "missing_query"
                }
        elif path == '/api/v1/pubmed':
            q = query_params.get('q', [''])[0]
            response = {
                "banner": EDU_BANNER,
                "service": "pubmed-search", 
                "query": q if q else None,
                "message": "Medical literature search - basic implementation",
                "results": [
                    {
                        "title": "Sample PubMed Article About " + (q if q else "Medical Research"),
                        "authors": ["Smith J", "Doe A"],
                        "journal": "Sample Medical Journal",
                        "year": "2024",
                        "pmid": "12345678",
                        "abstract": f"This is a sample abstract for research on {q if q else 'medical topics'}. In production, this would be real PubMed data."
                    }
                ] if q else [],
                "status": "stub" if q else "missing_query"
            }
        elif path == '/api/v1/trials':
            q = query_params.get('q', [''])[0]
            response = {
                "banner": EDU_BANNER,
                "service": "clinical-trials",
                "query": q if q else None,
                "message": "Clinical trials search - basic implementation", 
                "trials": [
                    {
                        "title": f"Clinical Trial for {q if q else 'Medical Condition'}",
                        "nct_id": "NCT12345678",
                        "phase": "Phase 3",
                        "status": "Recruiting",
                        "condition": q if q else "Sample Condition",
                        "location": "Multiple Centers"
                    }
                ] if q else [],
                "status": "stub" if q else "missing_query"
            }
        else:
            response = {
                "status": "healthy",
                "service": "ai-nurse-florence",
                "version": "1.0.0",
                "message": "AI Nurse Florence - Healthcare AI Assistant",
                "available_endpoints": [
                    "/api/v1/health",
                    "/api/v1/disease?q=condition_name",
                    "/api/v1/pubmed?q=search_term", 
                    "/api/v1/trials?q=condition"
                ],
                "path": path,
                "banner": EDU_BANNER
            }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
