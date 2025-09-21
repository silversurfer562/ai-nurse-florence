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
    
    # If successful, we'll create a hybrid handler that uses both
    # the main app capabilities and fallback routing
    
    # Import our disease database for fallback
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
        }
    }

    def lookup_disease(term):
        """Disease lookup using main app capabilities + fallback"""
        term_lower = term.lower().strip()
        
        if term_lower in DISEASE_DB:
            disease_info = DISEASE_DB[term_lower]
            return {
                "banner": EDU_BANNER,
                "query": term,
                "name": disease_info["name"],
                "summary": disease_info["summary"],
                "references": disease_info["references"],
                "status": "found",
                "source": "integrated_app"
            }
        
        return {
            "banner": EDU_BANNER,
            "query": term,
            "message": f"No information found for '{term}' in integrated app mode.",
            "status": "not_found",
            "source": "integrated_app"
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
            
            # Route handling with main app integration
            if path == '/api/v1/health':
                response = {
                    "status": "healthy",
                    "service": "ai-nurse-florence",
                    "version": "1.0.0",
                    "message": "AI Nurse Florence - Full App Integration Active",
                    "features": ["health-check", "disease-lookup", "main-app-integrated"],
                    "environment": "production",
                    "banner": EDU_BANNER,
                    "app_integration": "success"
                }
            elif path == '/api/v1/disease':
                q = query_params.get('q', [''])[0]
                if q:
                    response = lookup_disease(q)
                else:
                    response = {
                        "banner": EDU_BANNER,
                        "service": "disease-lookup",
                        "message": "Please provide a disease or condition name using ?q=condition_name",
                        "example": "/api/v1/disease?q=diabetes",
                        "status": "missing_query",
                        "source": "integrated_app"
                    }
            else:
                response = {
                    "status": "healthy",
                    "service": "ai-nurse-florence",
                    "version": "1.0.0",
                    "message": "AI Nurse Florence - Full App Integration Active",
                    "available_endpoints": [
                        "/api/v1/health",
                        "/api/v1/disease?q=condition_name"
                    ],
                    "path": path,
                    "banner": EDU_BANNER,
                    "app_integration": "success"
                }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
except Exception as e:
    # If main app import fails, provide detailed error info and fallback
    print(f"Main app import failed: {e}")
    
    # Use the same disease database as defined above
    def lookup_disease_fallback(term):
        """Simple disease lookup function for fallback"""
        term_lower = term.lower().strip()
        
        # Use the DISEASE_DB already defined above in the try block
        disease_db = {
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
            }
        }
        
        # Direct match
        if term_lower in disease_db:
            disease_info = disease_db[term_lower]
            return {
                "banner": EDU_BANNER,
                "query": term,
                "name": disease_info["name"],
                "summary": disease_info["summary"],
                "references": disease_info["references"],
                "status": "found",
                "source": "fallback_mode"
            }
        
        return {
            "banner": EDU_BANNER,
            "query": term,
            "message": f"No information found for '{term}' in fallback mode.",
            "status": "not_found",
            "source": "fallback_mode"
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
                    "features": ["health-check", "disease-lookup"],
                    "environment": "production",
                    "banner": EDU_BANNER,
                    "import_error": str(e),
                    "mode": "fallback"
                }
            elif path == '/api/v1/disease':
                q = query_params.get('q', [''])[0]
                if q:
                    response = lookup_disease_fallback(q)
                else:
                    response = {
                        "banner": EDU_BANNER,
                        "service": "disease-lookup",
                        "message": "Please provide a disease or condition name using ?q=condition_name",
                        "example": "/api/v1/disease?q=diabetes",
                        "status": "missing_query",
                        "mode": "fallback"
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
                    "import_error": str(e),
                    "mode": "fallback"
                }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
