"""
Vercel API handler entry point.

This file serves as the entry point for Vercel deployments.
It imports the FastAPI app from the main app.py file.
"""
from app import app

# Vercel expects this to be available as 'app'
handler = app