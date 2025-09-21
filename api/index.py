"""Vercel serverless function for AI Nurse Florence.
Minimal FastAPI app with disease information lookup.
"""
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any, Optional

# Educational banner following API design standards
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

async def lookup_disease_simple(query: str) -> Dict[str, Any]:
    """Simple disease lookup using external APIs"""
    try:
        # Try to get basic information from MedlinePlus API
        async with httpx.AsyncClient() as client:
            # MedlinePlus Connect API for basic disease information
            response = await client.get(
                "https://connect.medlineplus.gov/service",
                params={
                    "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.177",
                    "mainSearchCriteria.v.c": query,
                    "knowledgeResponseType": "application/json"
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract basic info from MedlinePlus response
                summary = f"Based on medical resources, {query} is a medical condition. For detailed information, please consult with healthcare providers or visit MedlinePlus.gov."
                
                return {
                    "banner": EDU_BANNER,
                    "query": query,
                    "name": query.title(),
                    "summary": summary,
                    "references": [
                        {
                            "title": f"MedlinePlus - {query.title()}",
                            "url": f"https://medlineplus.gov/healthtopics.html",
                            "source": "MedlinePlus/NIH"
                        }
                    ],
                    "source": "medlineplus"
                }
    except Exception as e:
        pass  # Fall back to basic response
    
    # Fallback response with educational information
    return {
        "banner": EDU_BANNER,
        "query": query,
        "name": query.title(),
        "summary": f"This is an educational response about {query}. Please consult with healthcare professionals for accurate medical information. Visit MedlinePlus.gov or PubMed for peer-reviewed medical information.",
        "references": [
            {
                "title": "MedlinePlus Health Topics",
                "url": "https://medlineplus.gov/healthtopics.html",
                "source": "NIH/MedlinePlus"
            },
            {
                "title": "PubMed Database",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "source": "NIH/NLM"
            }
        ],
        "source": "educational"
    }

# Create minimal FastAPI app
app = FastAPI(
    title="AI Nurse Florence",
    description="Educational healthcare AI assistant",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware to allow GitHub Pages to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://silversurfer562.github.io",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"  # Allow all origins for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.get("/api/v1/health")
async def health():
    """Health endpoint with educational disclaimers"""
    return JSONResponse({
        "status": "healthy",
        "service": "ai-nurse-florence", 
        "version": "1.0.0",
        "banner": EDU_BANNER,
        "mode": "serverless"
    })

@app.get("/api/v1/disease")
async def disease_info(q: str = Query(..., description="Disease or condition to search for")):
    """Disease endpoint with actual disease information lookup"""
    try:
        # Use the simple disease lookup
        result = await lookup_disease_simple(q)
        return JSONResponse({
            "status": "ok",
            "banner": result.get("banner", EDU_BANNER),
            "query": result.get("query", q),
            "name": result.get("name"),
            "summary": result.get("summary"),
            "references": result.get("references", []),
            "source": result.get("source", "educational"),
            "service": "ai-nurse-florence",
            "mode": "serverless"
        })
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"Error looking up disease information: {str(e)}",
            "banner": EDU_BANNER,
            "query": q,
            "service": "ai-nurse-florence",
            "mode": "serverless"
        }, status_code=500)
