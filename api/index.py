from fastapi import FastAPI
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import sys
import os

# Add the parent directory to the path so we can import from utils and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Educational banner for all medical responses
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

try:
    # Try to import the main app with all its features
    from app import app as main_app
    
    # If successful, create a simple test handler
    class handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Main app import succeeded! Full app integration working.",
                "service": "ai-nurse-florence",
                "banner": EDU_BANNER,
                "version": "1.0.0"
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
except Exception as e:
    # If main app import fails, provide detailed error info and fallback
    print(f"Main app import failed: {e}")
    
    # Fallback to our working simple implementation
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
            
            # Route handling with fallback functionality
            if path == '/api/v1/health':
                response = {
                    "status": "healthy",
                    "service": "ai-nurse-florence",
                    "version": "1.0.0",
                    "message": "AI Nurse Florence - Healthcare AI Assistant (Fallback Mode)",
                    "features": ["health-check", "disease-lookup", "pubmed-search", "clinical-trials"],
                    "environment": "production",
                    "banner": EDU_BANNER,
                    "import_error": str(e)
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
            else:
                response = {
                    "status": "healthy",
                    "service": "ai-nurse-florence",
                    "version": "1.0.0", 
                    "message": "AI Nurse Florence - Healthcare AI Assistant (Fallback Mode)",
                    "available_endpoints": [
                        "/api/v1/health",
                        "/api/v1/disease?q=condition_name"
                    ],
                    "path": path,
                    "banner": EDU_BANNER,
                    "import_error": str(e)
                }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
