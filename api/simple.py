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
        "message": "FastAPI working on Vercel!"
    }

# Simple handler to test FastAPI response
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Simple health check response
        response = {
            "status": "healthy",
            "service": "ai-nurse-florence",
            "version": "1.0.0",
            "message": "FastAPI-style response working on Vercel!",
            "path": self.path
        }
        
        self.wfile.write(json.dumps(response).encode())
