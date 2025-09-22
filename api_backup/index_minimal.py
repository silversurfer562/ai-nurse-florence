"""Minimal Vercel test wrapper"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def root():
    return HTMLResponse("<h1>Minimal Test</h1>")

@app.get("/test")
def test():
    return {"message": "test"}

# Vercel handler
handler = app
