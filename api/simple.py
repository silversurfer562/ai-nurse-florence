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

# Simple handler to provide medical AI endpoints
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        path = self.path.split('?')[0]  # Remove query parameters
        
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
            response = {
                "banner": EDU_BANNER,
                "service": "disease-lookup",
                "message": "Disease information service - coming soon",
                "path": path,
                "status": "stub"
            }
        elif path == '/api/v1/pubmed':
            response = {
                "banner": EDU_BANNER,
                "service": "pubmed-search", 
                "message": "Medical literature search - coming soon",
                "path": path,
                "status": "stub"
            }
        elif path == '/api/v1/trials':
            response = {
                "banner": EDU_BANNER,
                "service": "clinical-trials",
                "message": "Clinical trials search - coming soon", 
                "path": path,
                "status": "stub"
            }
        else:
            response = {
                "status": "healthy",
                "service": "ai-nurse-florence",
                "version": "1.0.0",
                "message": "AI Nurse Florence - Healthcare AI Assistant",
                "available_endpoints": [
                    "/api/v1/health",
                    "/api/v1/disease",
                    "/api/v1/pubmed", 
                    "/api/v1/trials"
                ],
                "path": path,
                "banner": EDU_BANNER
            }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
