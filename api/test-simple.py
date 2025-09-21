from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "working",
            "message": "Simple test handler is working",
            "timestamp": "2025-01-21"
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
