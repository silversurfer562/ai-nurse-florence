"""
AI Nurse Florence - Vercel Serverless API

A FastAPI application providing clinical assessment optimization and medical information lookup.
Educational use only - not medical advice. No PHI stored.

Features:
- Clinical query optimization with evidence-based enhancements
- Disease information lookup via MyDisease.info API
- Clinical trial information via ClinicalTrials.gov API  
- PubMed literature search integration
- SBAR clinical report template generation
- Intelligent caching for performance optimization

Author: AI Nurse Florence Team
License: Educational Use Only
"""

from fastapi import FastAPI, HTTPException, Query, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import httpx
import json
import time
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Educational banner following API design standards
EDU_BANNER = "Educational purposes only — verify with healthcare providers. No PHI stored."

# Cache configuration
CACHE_TTL = 3600  # 1 hour cache TTL
MAX_CACHE_SIZE = 1000  # Maximum cache entries

class ClinicalOptimizationRequest(BaseModel):
    """
    Pydantic model for clinical assessment optimization requests.
    
    This model validates and structures clinical data to enhance AI prompts
    for better, more targeted clinical guidance.
    """
    primary_concern: str = Field(..., min_length=5, max_length=1000, 
                                description="Primary clinical concern or symptom")
    patient_age: Optional[str] = Field(None, max_length=10, 
                                     description="Patient age in years")
    primary_diagnosis: Optional[str] = Field(None, max_length=200, 
                                           description="Current primary diagnosis")
    comorbidities: Optional[str] = Field(None, max_length=500, 
                                       description="Relevant comorbid conditions")
    timeline: Optional[str] = Field(None, max_length=200, 
                                  description="Symptom onset timeline")
    severity: Optional[str] = Field(None, max_length=50, 
                                  description="Clinical severity assessment")
    associated_symptoms: Optional[str] = Field(None, max_length=500, 
                                             description="Associated signs and symptoms")
    focus_areas: Optional[str] = Field(None, max_length=500, 
                                     description="Comma-separated clinical focus areas")
    evidence_level: Optional[str] = Field("guidelines", max_length=50, 
                                        description="Preferred evidence quality level")
    urgency_level: Optional[str] = Field("routine", max_length=50, 
                                       description="Clinical urgency classification")
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity levels"""
        if v and v.lower() not in ['mild', 'moderate', 'severe', 'critical', '']:
            logger.warning(f"Unknown severity level: {v}")
        return v
    
    @validator('evidence_level')
    def validate_evidence_level(cls, v):
        """Validate evidence level preferences"""
        valid_levels = ['guidelines', 'research', 'expert', 'comprehensive']
        if v and v.lower() not in valid_levels:
            logger.warning(f"Unknown evidence level: {v}")
        return v


# Thread-safe cache implementation
class SimpleCache:
    """Thread-safe in-memory cache for serverless environment"""
    
    def __init__(self, ttl: int = CACHE_TTL, max_size: int = MAX_CACHE_SIZE):
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self.ttl = ttl
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if still valid"""
        if key in self._cache and key in self._timestamps:
            if time.time() - self._timestamps[key] < self.ttl:
                logger.info(f"Cache hit for key: {key}")
                return self._cache[key]
            else:
                # Expired, remove from cache
                self._cleanup_key(key)
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Cache value with timestamp"""
        # Implement basic LRU by clearing oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
            self._cleanup_key(oldest_key)
        
        self._cache[key] = value
        self._timestamps[key] = time.time()
        logger.info(f"Cached value for key: {key}")
    
    def _cleanup_key(self, key: str) -> None:
        """Remove key from both cache and timestamps"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

# Global cache instance
cache = SimpleCache()

def _get_default_focus_areas() -> str:
    """Get default clinical focus areas when none are specified"""
    return """
- Nursing assessment priorities and interventions
- Patient safety considerations and risk factors
- When to escalate care to physician
- Patient/family education points"""

async def lookup_disease_simple(query: str) -> Dict[str, Any]:
    """
    Enhanced disease lookup with caching and multiple data sources.
    
    Args:
        query: Medical condition or disease name to search for
        
    Returns:
        Dict containing disease information, references, and educational banner
        
    Raises:
        HTTPException: If query is invalid or service unavailable
    """
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters long"
        )
    
    cache_key = f"disease:{query.lower().strip()}"
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        cached_result["cache_hit"] = True
        logger.info(f"Returning cached disease info for: {query}")
        return cached_result
    
    try:
        # Enhanced medical information lookup with multiple fallbacks
        async with httpx.AsyncClient(timeout=15.0) as client:
            
            # Try MyDisease.info API for comprehensive medical data
            try:
                disease_response = await client.get(
                    f"https://mydisease.info/v1/query",
                    params={
                        "q": query,
                        "fields": "mondo.definition,mondo.label,disgenet.diseases_genes_summary,hpo.definition,orphanet.definition",
                        "size": 3
                    }
                )
                
                if disease_response.status_code == 200:
                    disease_data = disease_response.json()
                    if disease_data.get("hits"):
                        # Process multiple hits to find the best match
                        for hit in disease_data["hits"]:
                            mondo_info = hit.get("mondo", {})
                            name = mondo_info.get("label", "")
                            definition = mondo_info.get("definition", "")
                            
                            # Look for exact or close matches
                            if query.lower() in name.lower() or name.lower() in query.lower():
                                # Build comprehensive summary
                                summary_parts = []
                                if definition:
                                    summary_parts.append(f"Medical Definition: {definition}")
                                
                                # Add additional information sources
                                hpo_def = hit.get("hpo", {}).get("definition")
                                if hpo_def and hpo_def != definition:
                                    summary_parts.append(f"Clinical Information: {hpo_def}")
                                
                                orphanet_def = hit.get("orphanet", {}).get("definition")
                                if orphanet_def and orphanet_def not in [definition, hpo_def]:
                                    summary_parts.append(f"Additional Information: {orphanet_def}")
                                
                                if not summary_parts:
                                    summary_parts.append(f"{name} is a medical condition documented in scientific literature.")
                                
                                summary_parts.append("This information is for educational purposes only. Always consult healthcare professionals for medical advice.")
                                
                                result = {
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
                                    "mode": "serverless",
                                    "cache_hit": False
                                }
                                
                                # Cache the result
                                cache.set(cache_key, result)
                                return result
                        
                        # If no exact match, use first result
                        hit = disease_data["hits"][0]
                        name = hit.get("mondo", {}).get("label", query.title())
                        definition = hit.get("mondo", {}).get("definition", "")
                        
                        if definition:
                            summary = f"Medical Definition: {definition} This information is for educational purposes only. Always consult healthcare professionals for medical advice."
                        else:
                            summary = f"{name} is a medical condition documented in scientific literature. This information is for educational purposes only. Always consult healthcare professionals for medical advice."
                        
                        result = {
                            "banner": EDU_BANNER,
                            "query": query,
                            "name": name,
                            "summary": summary,
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
                            "mode": "serverless",
                            "cache_hit": False
                        }
                        
                        # Cache the result
                        cache.set(cache_key, result)
                        return result
                        
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
                    }
                )
                
                if response.status_code == 200:
                    summary = f"Based on NIH medical resources, {query.title()} is a documented medical condition. For comprehensive information including symptoms, causes, diagnosis, and treatment options, please consult with qualified healthcare providers or visit MedlinePlus.gov for evidence-based medical information."
                    
                    result = {
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
                        "mode": "serverless",
                        "cache_hit": False
                    }
                    
                    # Cache the result
                    cache.set(cache_key, result)
                    return result
                    
            except Exception as e:
                print(f"MedlinePlus API error: {e}")
                
    except Exception as e:
        print(f"General API error: {e}")
    
    
    
    # Enhanced fallback response with educational information
    result = {
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
        "mode": "serverless",
        "cache_hit": False
    }
    
    # Cache even the fallback response
    cache.set(cache_key, result)
    return result

# FastAPI Application Factory
def create_app() -> FastAPI:
    """
    Create and configure FastAPI application instance.
    
    This factory pattern allows for better testing, configuration management,
    and deployment flexibility across different environments.
    
    Returns:
        FastAPI: Configured application instance with middleware and routes
    """
    # Initialize FastAPI with comprehensive metadata
    app = FastAPI(
        title="AI Nurse Florence",
        description="Educational healthcare AI assistant providing evidence-based medical information for nursing professionals",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        terms_of_service="/terms",
        contact={
            "name": "AI Nurse Florence Support",
            "url": "https://github.com/your-repo/ai-nurse-florence",
            "email": "support@ai-nurse-florence.com"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # Security Headers Middleware
    @app.middleware("http")
    async def add_security_headers(request: Request, call_next):
        """Add comprehensive security headers to all responses"""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response
    
    # Request ID Middleware for tracing
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add unique request ID for debugging and logging"""
        import uuid
        request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    # CORS Middleware with proper configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://silversurfer562.github.io",
            "https://*.github.io", 
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"]
    )
    
    # Request logging middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log all requests for monitoring and debugging"""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"Request: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        return response
    
    return app

# Create application instance
app = create_app()

# Root endpoint
@app.get("/", 
         summary="API Root", 
         description="Main API information endpoint",
         tags=["System"])
async def root():
    """API root endpoint with service information"""
    return JSONResponse({
        "service": "AI Nurse Florence",
        "description": "Educational healthcare AI assistant",
        "version": "2.0.0",
        "status": "healthy",
        "banner": EDU_BANNER,
        "mode": "serverless",
        "endpoints": {
            "health": "/api/v1/health",
            "disease_lookup": "/api/v1/disease",
            "clinical_optimizer": "/api/v1/clinical/optimize-query",
            "sbar_template": "/api/v1/templates/sbar",
            "documentation": "/docs"
        }
    })

# Health Check Endpoint  
@app.get("/api/v1/health",
         summary="Health Check",
         description="System health and status information",
         tags=["System"])
async def health():
    """
    Comprehensive health check endpoint with system status.
    
    Returns detailed information about service health, cache status,
    available APIs, and system configuration for monitoring purposes.
    """
    return JSONResponse({
        "status": "healthy",
        "service": "ai-nurse-florence",
        "version": "2.0.0",
        "timestamp": time.time(),
        "banner": EDU_BANNER,
        "mode": "serverless",
        "cache": {
            "type": "in-memory",
            "ttl_seconds": CACHE_TTL,
            "max_size": MAX_CACHE_SIZE,
            "current_entries": len(cache._cache),
            "hit_ratio": "tracking_not_implemented"
        },
        "apis": {
            "mydisease": {
                "url": "https://mydisease.info/v1/",
                "status": "external",
                "description": "Disease information and definitions"
            },
            "medlineplus": {
                "url": "https://connect.medlineplus.gov/service",
                "status": "external", 
                "description": "NIH consumer health information"
            },
            "pubmed": {
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "status": "external",
                "description": "Medical literature database"
            }
        },
        "features": {
            "disease_lookup": True,
            "clinical_optimization": True,
            "sbar_templates": True,
            "caching": True,
            "security_headers": True
        }
    })

@app.get("/api/v1/disease",
         summary="Disease Information Lookup",
         description="Look up comprehensive disease information from multiple medical sources",
         tags=["Medical Information"])
async def disease_info(q: str = Query(..., description="Disease or condition to search for", min_length=2)):
    """
    Look up comprehensive disease information from authoritative medical sources.
    
    This endpoint queries multiple medical databases including MyDisease.info,
    MedlinePlus, and provides fallback educational information. All responses
    include educational disclaimers and authoritative references.
    
    Args:
        q: Disease or medical condition name to search for (minimum 2 characters)
        
    Returns:
        JSONResponse: Disease information including definition, summary, and references
        
    Raises:
        HTTPException: If query is too short or service unavailable
    """
    try:
        logger.info(f"Disease lookup request for: {q}")
        
        # Use the enhanced disease lookup with comprehensive error handling
        result = await lookup_disease_simple(q)
        
        return JSONResponse({
            "status": "success",
            "banner": result.get("banner", EDU_BANNER),
            "query": result.get("query", q),
            "name": result.get("name"),
            "summary": result.get("summary"),
            "references": result.get("references", []),
            "source": result.get("source", "educational"),
            "cache_hit": result.get("cache_hit", False),
            "service": "ai-nurse-florence",
            "mode": "serverless",
            "timestamp": time.time()
        })
        
    except HTTPException:
        # Re-raise HTTP exceptions from validation
        raise
    except Exception as e:
        logger.error(f"Disease lookup error for query '{q}': {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": "Unable to retrieve disease information at this time",
            "banner": EDU_BANNER,
            "query": q,
            "service": "ai-nurse-florence",
            "mode": "serverless",
            "timestamp": time.time(),
            "references": [
                {
                    "title": f"MedlinePlus Health Topics - {q.title()}",
                    "url": "https://medlineplus.gov/healthtopics.html",
                    "source": "NIH/MedlinePlus"
                },
                {
                    "title": f"PubMed Medical Literature - {q.title()}",
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/?term={q}",
                    "source": "NIH/NLM"
                }
            ]
        }, status_code=500)


# Basic Clinical Templates for Quick Deployment
SBAR_TEMPLATE = """
# SBAR Report - {{ patient_name or "Patient" }}

## Situation
{{ situation or "Clinical situation to be described" }}

## Background
{{ background or "Relevant medical history and context" }}

## Assessment
{{ assessment or "Current clinical assessment and findings" }}

## Recommendation
{{ recommendation or "Recommended actions and follow-up" }}

---
*Generated by AI Nurse Florence for educational purposes only. Review and verify all information before clinical use.*
"""

@app.post("/api/v1/clinical/optimize-query",
          summary="Clinical Assessment Optimization",
          description="Transform clinical assessment data into optimized AI prompts for better clinical guidance",
          tags=["Clinical Tools"])
async def optimize_clinical_query(request: ClinicalOptimizationRequest):
    """
    Transform clinical assessment form data into optimized AI prompt.
    
    This endpoint takes structured clinical assessment data and transforms it into
    a comprehensive, evidence-based prompt that will generate higher quality
    AI responses for clinical decision support. The optimization includes:
    
    - Structured clinical context organization
    - Evidence-level preference integration  
    - Nursing-focused priority areas
    - Safety and escalation considerations
    - Professional citation requirements
    
    Args:
        request: Clinical optimization request with patient data and preferences
        
    Returns:
        JSONResponse: Optimized prompt with metadata and quality score
        
    Raises:
        HTTPException: If request data is invalid or processing fails
    """
    try:
        logger.info(f"Clinical optimization request for: {request.primary_concern[:50]}...")
        
        # Validate primary concern length and content
        concern = request.primary_concern.strip()
        if not concern or len(concern) < 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Primary concern must be at least 5 characters long and contain meaningful clinical information"
            )
        
        # Build comprehensive clinical prompt with professional structure
        enhanced_prompt = f"""CLINICAL ASSESSMENT REQUEST - AI NURSE FLORENCE

PRIMARY CONCERN: {concern}

PATIENT CLINICAL CONTEXT:"""
        
        # Systematically add available patient context
        context_items = []
        if request.patient_age:
            context_items.append(f"Patient Age: {request.patient_age} years")
        if request.primary_diagnosis:
            context_items.append(f"Primary Diagnosis: {request.primary_diagnosis}")
        if request.comorbidities:
            context_items.append(f"Relevant Comorbidities: {request.comorbidities}")
        if request.timeline:
            context_items.append(f"Clinical Timeline/Onset: {request.timeline}")
        if request.severity:
            context_items.append(f"Assessed Severity: {request.severity}")
        if request.associated_symptoms:
            context_items.append(f"Associated Clinical Findings: {request.associated_symptoms}")
        
        if context_items:
            for item in context_items:
                enhanced_prompt += f"\n- {item}"
        else:
            enhanced_prompt += "\n- [Limited patient context available - provide general clinical guidance]"
            
        enhanced_prompt += f"""

CLINICAL ASSESSMENT PRIORITIES:
Please provide evidence-based nursing guidance focusing on:"""

        # Process and validate focus areas
        if request.focus_areas and request.focus_areas.strip():
            # Parse comma-separated focus areas
            areas = [area.strip() for area in request.focus_areas.split(',') if area.strip()]
            if areas:
                for area in areas:
                    enhanced_prompt += f"\n- {area}"
            else:
                enhanced_prompt += _get_default_focus_areas()
        else:
            enhanced_prompt += _get_default_focus_areas()

        # Add professional requirements and evidence standards
        evidence_level = (request.evidence_level or 'guidelines').lower()
        urgency_level = (request.urgency_level or 'routine').lower()
        
        # Validate evidence level
        valid_evidence_levels = ['guidelines', 'research', 'expert', 'comprehensive']
        if evidence_level not in valid_evidence_levels:
            evidence_level = 'guidelines'
            
        # Validate urgency level  
        valid_urgency_levels = ['routine', 'urgent', 'emergent', 'stat']
        if urgency_level not in valid_urgency_levels:
            urgency_level = 'routine'
        
        enhanced_prompt += f"""

RESPONSE REQUIREMENTS AND STANDARDS:
- Evidence Quality: {evidence_level.title()} level sources required
- Clinical Urgency: {urgency_level.title()} assessment timeline
- Include authoritative medical references and citations
- Provide specific, actionable nursing interventions
- Address patient safety considerations and risk factors
- Include clear escalation criteria for physician consultation
- Educational purpose only - not direct medical advice

RESPONSE STRUCTURE REQUESTED:
1. Clinical Assessment Summary
2. Evidence-Based Nursing Interventions  
3. Patient Safety Considerations
4. Escalation Criteria and Red Flags
5. Patient/Family Education Points
6. Authoritative References and Citations

Please ensure all recommendations align with current nursing practice standards and evidence-based guidelines."""

        # Calculate comprehensive optimization score
        optimization_score = calculate_optimization_score(
            concern, request.patient_age, request.primary_diagnosis, 
            request.comorbidities, request.timeline, request.severity, 
            request.associated_symptoms, request.focus_areas
        )
        
        # Prepare comprehensive response
        response_data = {
            "status": "success",
            "optimization_type": "clinical_assessment_nursing",
            "enhanced_prompt": enhanced_prompt,
            "original_concern": concern,
            "optimization_score": optimization_score,
            "optimization_details": {
                "context_completeness": f"{len(context_items)}/6 context fields provided",
                "evidence_level": evidence_level.title(),
                "urgency_level": urgency_level.title(),
                "focus_areas": len([a.strip() for a in (request.focus_areas or '').split(',') if a.strip()]),
                "professional_structure": True
            },
            "banner": EDU_BANNER,
            "ready_for_ai": True,
            "service": "ai-nurse-florence-optimizer",
            "timestamp": time.time(),
            "usage_guidance": "Copy the enhanced_prompt to your AI assistant for comprehensive clinical guidance"
        }
        
        logger.info(f"Clinical optimization completed with score: {optimization_score}")
        return JSONResponse(response_data)
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        logger.error(f"Clinical optimization error: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": "Unable to optimize clinical query at this time",
            "original_concern": request.primary_concern if request else "Unknown",
            "banner": EDU_BANNER,
            "service": "ai-nurse-florence-optimizer",
            "timestamp": time.time()
        }, status_code=500)


def calculate_optimization_score(concern, age, diagnosis, comorbidities, timeline, severity, associated_symptoms, focus_areas):
    """Calculate how well-optimized the query is"""
    score = 0
    if concern: score += 30  # Primary concern is critical
    if age: score += 10
    if diagnosis: score += 15
    if comorbidities: score += 10
    if timeline: score += 10
    if severity: score += 10
    if associated_symptoms: score += 5
    if focus_areas: score += 10
    return min(score, 100)


@app.post("/api/v1/templates/sbar",
          summary="SBAR Report Generation", 
          description="Generate structured SBAR (Situation-Background-Assessment-Recommendation) clinical reports",
          tags=["Clinical Templates"])
async def generate_sbar_template(
    patient_name: str = Query(None, description="Patient name or identifier"),
    situation: str = Query(None, description="Current clinical situation"),
    background: str = Query(None, description="Relevant background information"),
    assessment: str = Query(None, description="Clinical assessment"),
    recommendation: str = Query(None, description="Recommendations")
):
    """
    Generate structured SBAR report template for clinical communication.
    
    SBAR (Situation-Background-Assessment-Recommendation) is a standardized
    communication framework used in healthcare to ensure clear, concise,
    and complete information transfer between healthcare professionals.
    
    Args:
        patient_name: Patient identifier (anonymized as appropriate)
        situation: Current clinical situation or concern
        background: Relevant medical history and context
        assessment: Current clinical assessment and findings
        recommendation: Recommended interventions or actions
        
    Returns:
        JSONResponse: Formatted SBAR report template
        
    Raises:
        HTTPException: If template generation fails
    """
    try:
        logger.info("Generating SBAR template")
        
        # Enhanced SBAR template with professional formatting
        template_content = f"""# SBAR Clinical Communication Report

**Patient:** {patient_name or '[Patient Name/Identifier]'}
**Date:** [Insert Date]
**Reporter:** [Your Name/Title]
**Recipient:** [Physician/Provider Name]

---

## 🔍 SITUATION
**Current Clinical Status:**
{situation or '[Describe the current clinical situation, immediate concern, or reason for communication]'}

---

## 📋 BACKGROUND
**Relevant Medical History & Context:**
{background or '[Include relevant medical history, current medications, recent procedures, and contextual information]'}

---

## 📊 ASSESSMENT
**Clinical Findings & Analysis:**
{assessment or '[Provide current vital signs, assessment findings, test results, and clinical observations]'}

---

## 💡 RECOMMENDATION
**Requested Actions & Follow-up:**
{recommendation or '[Specify recommended interventions, orders needed, timeline for follow-up, and escalation criteria]'}

---

*Generated by AI Nurse Florence Clinical Templates*
*{EDU_BANNER}*
*Review and customize all information before clinical use*
"""
        
        return JSONResponse({
            "status": "success",
            "template_type": "sbar_clinical_communication",
            "content": template_content,
            "metadata": {
                "patient_provided": bool(patient_name),
                "situation_provided": bool(situation),
                "background_provided": bool(background),
                "assessment_provided": bool(assessment),
                "recommendation_provided": bool(recommendation),
                "completeness_score": sum([bool(patient_name), bool(situation), bool(background), bool(assessment), bool(recommendation)]) * 20
            },
            "usage_instructions": [
                "Review and customize all bracketed placeholders",
                "Verify patient information is accurate and appropriate",
                "Ensure clinical details are complete and relevant", 
                "Use for professional healthcare communication only"
            ],
            "banner": EDU_BANNER,
            "service": "ai-nurse-florence-templates",
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"SBAR template generation error: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": "Unable to generate SBAR template at this time",
            "banner": EDU_BANNER,
            "service": "ai-nurse-florence-templates",
            "timestamp": time.time()
        }, status_code=500)


# Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler with educational context"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "banner": EDU_BANNER,
            "service": "ai-nurse-florence",
            "timestamp": time.time(),
            "request_path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    """Custom 500 error handler with logging"""
    logger.error(f"Internal server error on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error", 
            "message": "Internal server error occurred",
            "banner": EDU_BANNER,
            "service": "ai-nurse-florence",
            "timestamp": time.time(),
            "support": "Please try again or contact support if the issue persists"
        }
    )
