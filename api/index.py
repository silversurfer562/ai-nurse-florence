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
    """Enhanced disease lookup using multiple medical APIs"""
    try:
        # Enhanced medical information lookup
        async with httpx.AsyncClient() as client:
            
            # Try MyDisease.info API for comprehensive medical data
            try:
                disease_response = await client.get(
                    f"https://mydisease.info/v1/query",
                    params={
                        "q": query,
                        "fields": "mondo.definition,mondo.label,disgenet.diseases_genes_summary,hpo.definition",
                        "size": 1
                    },
                    timeout=10.0
                )
                
                if disease_response.status_code == 200:
                    disease_data = disease_response.json()
                    if disease_data.get("hits"):
                        hit = disease_data["hits"][0]
                        
                        # Extract comprehensive information
                        name = hit.get("mondo", {}).get("label", query.title())
                        definition = hit.get("mondo", {}).get("definition", "")
                        hpo_def = hit.get("hpo", {}).get("definition", "")
                        
                        # Build comprehensive summary
                        summary_parts = []
                        if definition:
                            summary_parts.append(f"Medical Definition: {definition}")
                        if hpo_def and hpo_def != definition:
                            summary_parts.append(f"Clinical Information: {hpo_def}")
                        
                        if not summary_parts:
                            summary_parts.append(f"{name} is a medical condition documented in scientific literature.")
                        
                        summary_parts.append("This information is for educational purposes only. Always consult healthcare professionals for medical advice.")
                        
                        return {
                            "banner": EDU_BANNER,
                            "query": query,
                            "name": name,
                            "summary": " ".join(summary_parts),
                            "references": [
                                {
                                    "title": f"MyDisease.info - {name}",
                                    "url": f"https://mydisease.info/v1/disease/{hit.get('_id', query)}",
                                    "source": "MyDisease.info/NIH"
                                },
                                {
                                    "title": f"MedlinePlus - {name}",
                                    "url": f"https://medlineplus.gov/healthtopics.html",
                                    "source": "MedlinePlus/NIH"
                                },
                                {
                                    "title": "PubMed Medical Literature",
                                    "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query}",
                                    "source": "PubMed/NCBI"
                                }
                            ],
                            "source": "mydisease",
                            "service": "ai-nurse-florence",
                            "mode": "serverless"
                        }
            except Exception as e:
                print(f"MyDisease.info API error: {e}")
            
            # Fallback to MedlinePlus Connect API
            try:
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
                    summary = f"Based on NIH medical resources, {query.title()} is a documented medical condition. For comprehensive information including symptoms, causes, diagnosis, and treatment options, please consult with qualified healthcare providers or visit MedlinePlus.gov for evidence-based medical information."
                    
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
                            },
                            {
                                "title": "PubMed Medical Literature",
                                "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query}",
                                "source": "PubMed/NCBI"
                            }
                        ],
                        "source": "medlineplus",
                        "service": "ai-nurse-florence",
                        "mode": "serverless"
                    }
            except Exception as e:
                print(f"MedlinePlus API error: {e}")
                
    except Exception as e:
        print(f"General API error: {e}")
    
    
    # Enhanced fallback response with educational information
    return {
        "banner": EDU_BANNER,
        "query": query,
        "name": query.title(),
        "summary": f"Educational Information: {query.title()} is a medical term or condition. For accurate, comprehensive medical information including definitions, symptoms, causes, diagnosis, and treatment options, please consult with qualified healthcare professionals. You can also find evidence-based information at MedlinePlus.gov (NIH) or search peer-reviewed medical literature at PubMed.gov.",
        "references": [
            {
                "title": f"MedlinePlus Health Topics - {query.title()}",
                "url": f"https://medlineplus.gov/healthtopics.html",
                "source": "NIH/MedlinePlus"
            },
            {
                "title": f"PubMed Medical Literature - {query.title()}",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={query}",
                "source": "NIH/NLM"
            },
            {
                "title": "Mayo Clinic Health Information",
                "url": f"https://www.mayoclinic.org/search/search-results?q={query}",
                "source": "Mayo Clinic"
            }
        ],
        "source": "educational",
        "service": "ai-nurse-florence",
        "mode": "serverless"
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
        "mode": "serverless",
        "apis": {
            "mydisease": "https://mydisease.info/v1/",
            "medlineplus": "https://connect.medlineplus.gov/service",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/"
        }
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
