from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import time
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Nurse Florence",
    description="Healthcare AI Assistant providing evidence-based medical information",
    version="2.0.1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files (HTML frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Educational banner
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Nurse Florence - Healthcare AI Assistant",
        "status": "operational",
        "version": "2.0.1",
        "banner": EDU_BANNER,
        "docs": "/docs",
        "health": "/health",
        "api_health": "/api/v1/health",
        "frontend": "/static/index.html"
    }

@app.get("/app")
async def frontend():
    """Serve the main frontend application"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": "2.0.1",
        "banner": EDU_BANNER,
        "mode": "railway",
        "apis": {
            "mydisease": "https://mydisease.info/v1/",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/",
            "clinicaltrials": "https://clinicaltrials.gov/api/v2/"
        }
    }

@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint"""
    return await health()

@app.get("/api/v1/disease/lookup")
async def disease_lookup(q: str = Query(..., description="Disease or condition to search for")):
    """Look up disease information using MyDisease.info API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Query MyDisease.info API
            url = "https://mydisease.info/v1/query"
            params = {
                "q": q,
                "size": 1,
                "fields": "mondo.definition,disgenet.diseases_related_to_gene,chembl.indication"
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("hits"):
                return {
                    "query": q,
                    "banner": EDU_BANNER,
                    "message": f"No disease information found for '{q}'",
                    "suggestions": "Try using medical terminology or check spelling"
                }
            
            hit = data["hits"][0]
            return {
                "query": q,
                "banner": EDU_BANNER,
                "disease_info": hit,
                "source": "MyDisease.info",
                "timestamp": time.time()
            }
            
    except Exception as e:
        logger.error(f"Disease lookup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error looking up disease information: {str(e)}"
        )

@app.get("/api/v1/literature/search")
async def literature_search(q: str = Query(..., description="Medical literature search query")):
    """Search medical literature using PubMed API"""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Search PubMed
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": q,
                "retmax": 5,
                "retmode": "json",
                "sort": "relevance"
            }
            
            search_response = await client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if not search_data.get("esearchresult", {}).get("idlist"):
                return {
                    "query": q,
                    "banner": EDU_BANNER,
                    "message": f"No literature found for '{q}'",
                    "articles": []
                }
            
            # Get article details
            ids = search_data["esearchresult"]["idlist"]
            summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            summary_params = {
                "db": "pubmed",
                "id": ",".join(ids),
                "retmode": "json"
            }
            
            summary_response = await client.get(summary_url, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            articles = []
            for uid in ids:
                if uid in summary_data.get("result", {}):
                    article = summary_data["result"][uid]
                    articles.append({
                        "pmid": uid,
                        "title": article.get("title", ""),
                        "authors": article.get("authors", []),
                        "source": article.get("source", ""),
                        "pubdate": article.get("pubdate", ""),
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                    })
            
            return {
                "query": q,
                "banner": EDU_BANNER,
                "articles": articles,
                "total_found": len(articles),
                "source": "PubMed",
                "timestamp": time.time()
            }
            
    except Exception as e:
        logger.error(f"Literature search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching literature: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AI Nurse Florence on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
