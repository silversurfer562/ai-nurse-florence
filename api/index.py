"""
Vercel serverless function entry point for the AI Nurse Florence API.

This module serves as the main entry point for the FastAPI application 
when deployed on Vercel's serverless platform.
"""
import os
import sys

# Add the parent directory to the Python path so we can import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variable to indicate we're running on Vercel
os.environ['VERCEL'] = '1'

from app import app

# This is the handler that Vercel will call
def handler(request, response):
    """Vercel serverless function handler."""
    return app(request, response)

# For ASGI compatibility
app = app