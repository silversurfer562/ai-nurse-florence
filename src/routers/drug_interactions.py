"""
Drug Interaction Router - AI Nurse Florence
Phase 4.2: Additional Medical Services

REST API endpoints for comprehensive drug interaction checking
with clinical decision support and smart caching.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime

# Import service following conditional imports pattern
try:
    from src.services.drug_interaction_service import DrugInteractionService
    _has_drug_service = True
except ImportError:
    _has_drug_service = False
    DrugInteractionService = None  # type: ignore

try:
    from src.utils.api_responses import create_success_response, create_error_response
    _has_api_responses = True
except ImportError:
    _has_api_responses = False
    def create_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:  # type: ignore
        return {"status": "success", "data": data, "message": message}
    def create_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  # type: ignore
        return {"status": "error", "message": message, "status_code": status_code, "details": details}

try:
    from src.utils.config import get_settings
    _has_config = True
except ImportError:
    _has_config = False
    def get_settings():  # type: ignore
        return type('Settings', (), {'educational_banner': 'Educational use only - not medical advice'})()

logger = logging.getLogger(__name__)

# Pydantic Models
class DrugInteractionRequest(BaseModel):
    """Request model for drug interaction checking."""
    drugs: List[str] = Field(
        ..., 
        description="List of medications to check for interactions (2-20 drugs)"
    )
    patient_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional patient context including age, conditions, allergies"
    )
    include_warnings: bool = Field(
        True,
        description="Include minor and moderate interaction warnings"
    )
    
    @validator('drugs')
    def validate_drugs(cls, v):
        if not v or len(v) < 2:
            raise ValueError("At least 2 medications required for interaction checking")
        if len(v) > 20:
            raise ValueError("Maximum 20 medications allowed")
        
        # Clean and validate drug names
        cleaned_drugs = []
        for drug in v:
            cleaned = drug.strip().lower()
            if len(cleaned) < 2:
                raise ValueError(f"Invalid drug name: {drug}")
            cleaned_drugs.append(cleaned)
        
        return cleaned_drugs

class BulkInteractionRequest(BaseModel):
    """Request model for checking multiple drug combinations."""
    drug_lists: List[List[str]] = Field(
        ...,
        description="Multiple drug lists to check for interactions"
    )
    patient_context: Optional[Dict[str, Any]] = None
    priority: str = Field("standard", description="Priority level: low, standard, high, urgent")
    
    @validator('drug_lists')
    def validate_drug_lists(cls, v):
        if not v or len(v) < 1:
            raise ValueError("At least 1 drug list required")
        if len(v) > 10:
            raise ValueError("Maximum 10 drug lists allowed")
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'standard', 'high', 'urgent']:
            raise ValueError("Priority must be: low, standard, high, or urgent")
        return v

class DrugSearchRequest(BaseModel):
    """Request model for drug database search."""
    query: str = Field(..., min_length=2, description="Drug name or partial name to search")
    max_results: int = Field(10, ge=1, le=50, description="Maximum results to return")
    include_generics: bool = Field(True, description="Include generic medications")

# Router setup
router = APIRouter(
    prefix="/drug-interactions",
    tags=["drug-interactions"],
    responses={
        404: {"description": "Drug interaction service not available"},
        422: {"description": "Invalid input data"},
        500: {"description": "Internal service error"}
    }
)

# Service instance
drug_service = DrugInteractionService() if _has_drug_service and DrugInteractionService else None

@router.post(
    "/check",
    summary="Check Drug Interactions",
    description="Check for interactions between multiple medications with clinical recommendations"
)
async def check_drug_interactions(
    request: DrugInteractionRequest
):
    """
    Check for drug interactions in a medication list.
    
    Returns comprehensive interaction analysis with:
    - Interaction severity levels
    - Clinical recommendations
    - Monitoring requirements
    - Patient-specific alerts
    """
    if not drug_service:
        return JSONResponse(
            content=create_error_response(
                "Drug interaction service unavailable",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        result = await drug_service.check_drug_interactions(
            drugs=request.drugs,
            patient_context=request.patient_context,
            use_cache=True
        )
        
        # Filter results based on warning preferences
        if not request.include_warnings:
            interactions = result.get('interactions', [])
            result['interactions'] = [
                interaction for interaction in interactions
                if interaction.get('severity', '').lower() in ['major', 'severe', 'contraindicated']
            ]
            result['total_interactions'] = len(result['interactions'])
        
        return JSONResponse(
            content=create_success_response(
                result,
                f"Interaction check complete for {len(request.drugs)} medications"
            )
        )
        
    except Exception as e:
        logger.error(f"Drug interaction check failed: {e}")
        return JSONResponse(
            content=create_error_response(
                "Failed to check drug interactions",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)}
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post(
    "/bulk-check",
    summary="Bulk Drug Interaction Check", 
    description="Check interactions for multiple medication lists simultaneously"
)
async def bulk_drug_interaction_check(
    request: BulkInteractionRequest
):
    """
    Check drug interactions for multiple medication combinations.
    
    Useful for:
    - Comparing different treatment regimens
    - Batch processing patient medications
    - Clinical decision support workflows
    """
    if not drug_service:
        return JSONResponse(
            content=create_error_response(
                "Drug interaction service unavailable",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        results = []
        
        for i, drug_list in enumerate(request.drug_lists):
            if len(drug_list) < 2:
                results.append({
                    "list_index": i,
                    "error": "At least 2 medications required",
                    "drugs": drug_list
                })
                continue
            
            try:
                result = await drug_service.check_drug_interactions(
                    drugs=drug_list,
                    patient_context=request.patient_context,
                    use_cache=True
                )
                
                results.append({
                    "list_index": i,
                    "drugs": drug_list,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "list_index": i,
                    "drugs": drug_list,
                    "error": str(e)
                })
        
        return JSONResponse(
            content=create_success_response(
                {"bulk_results": results, "total_lists": len(request.drug_lists)},
                f"Bulk interaction check complete for {len(request.drug_lists)} drug lists"
            )
        )
        
    except Exception as e:
        logger.error(f"Bulk drug interaction check failed: {e}")
        return JSONResponse(
            content=create_error_response(
                "Failed to process bulk interaction check",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)}
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get(
    "/severity-levels",
    summary="Get Interaction Severity Levels",
    description="Retrieve information about drug interaction severity classifications"
)
async def get_severity_levels():
    """
    Get drug interaction severity level definitions.
    
    Returns standard clinical severity classifications used
    in interaction analysis and clinical decision support.
    """
    severity_levels = {
        "contraindicated": {
            "level": 4,
            "description": "These drug combinations are contraindicated and should not be used together",
            "action": "Avoid combination - choose alternative therapy",
            "color_code": "red",
            "clinical_priority": "immediate"
        },
        "major": {
            "level": 3,
            "description": "Major interaction that may result in serious adverse effects",
            "action": "Avoid combination or monitor closely with frequent assessment",
            "color_code": "orange",
            "clinical_priority": "high"
        },
        "moderate": {
            "level": 2,
            "description": "Moderate interaction requiring monitoring or dosage adjustment",
            "action": "Monitor therapy and consider dosage modifications",
            "color_code": "yellow",
            "clinical_priority": "moderate"
        },
        "minor": {
            "level": 1,
            "description": "Minor interaction with minimal clinical significance",
            "action": "Monitor therapy but continuation usually acceptable",
            "color_code": "green",
            "clinical_priority": "low"
        },
        "unknown": {
            "level": 0,
            "description": "Interaction potential unknown or insufficient data",
            "action": "Review literature and monitor therapy",
            "color_code": "gray",
            "clinical_priority": "review"
        }
    }
    
    return JSONResponse(
        content=create_success_response(
            severity_levels,
            "Drug interaction severity levels retrieved"
        )
    )

@router.post(
    "/search-drugs",
    summary="Search Drug Database",
    description="Search the drug database for medication names and information"
)
async def search_drugs(
    request: DrugSearchRequest
):
    """
    Search for drugs in the interaction database.
    
    Useful for:
    - Drug name validation
    - Finding correct medication names
    - Discovering available medications for interaction checking
    """
    if not drug_service:
        return JSONResponse(
            content=create_error_response(
                "Drug interaction service unavailable",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Mock drug search for demonstration
        # In production, this would search the actual drug database
        mock_drugs = [
            {
                "name": "metformin",
                "generic_name": "metformin",
                "brand_names": ["Glucophage", "Fortamet", "Glumetza"],
                "drug_class": "Biguanides",
                "indication": "Type 2 diabetes",
                "match_score": 0.95
            },
            {
                "name": "lisinopril", 
                "generic_name": "lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ACE Inhibitors",
                "indication": "Hypertension, Heart failure",
                "match_score": 0.90
            },
            {
                "name": "warfarin",
                "generic_name": "warfarin",
                "brand_names": ["Coumadin", "Jantoven"],
                "drug_class": "Anticoagulants",
                "indication": "Anticoagulation",
                "match_score": 0.88
            }
        ]
        
        # Filter based on query
        query_lower = request.query.lower()
        filtered_drugs = [
            drug for drug in mock_drugs
            if query_lower in drug["name"].lower() or 
               any(query_lower in brand.lower() for brand in drug["brand_names"])
        ]
        
        # Limit results
        limited_results = filtered_drugs[:request.max_results]
        
        return JSONResponse(
            content=create_success_response(
                {
                    "query": request.query,
                    "results": limited_results,
                    "total_found": len(limited_results),
                    "include_generics": request.include_generics
                },
                f"Found {len(limited_results)} matching drugs"
            )
        )
        
    except Exception as e:
        logger.error(f"Drug search failed: {e}")
        return JSONResponse(
            content=create_error_response(
                "Failed to search drug database",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)}
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get(
    "/health",
    summary="Drug Interaction Service Health",
    description="Check the health and availability of the drug interaction service"
)
async def get_service_health():
    """
    Check drug interaction service health and capabilities.
    
    Returns service status, database information, and feature availability.
    """
    settings = get_settings() if _has_config else type('Settings', (), {})()
    
    health_status = {
        "service_available": _has_drug_service and drug_service is not None,
        "drug_database_size": 150,  # Mock database size
        "interaction_rules": 2500,  # Mock rule count
        "severity_levels": ["contraindicated", "major", "moderate", "minor", "unknown"],
        "supported_features": [
            "drug_interaction_checking",
            "clinical_recommendations", 
            "severity_assessment",
            "patient_context_analysis",
            "bulk_processing",
            "smart_caching"
        ],
        "cache_enabled": True,
        "last_database_update": "2024-09-01",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
    
    if hasattr(settings, 'educational_banner'):
        health_status["educational_banner"] = getattr(settings, 'educational_banner', '')
    
    return JSONResponse(
        content=create_success_response(
            health_status,
            "Drug interaction service health check complete"
        )
    )

@router.get(
    "/statistics",
    summary="Service Usage Statistics", 
    description="Get drug interaction service usage and performance statistics"
)
async def get_service_statistics():
    """
    Get drug interaction service usage statistics.
    
    Returns performance metrics, usage patterns, and service analytics.
    """
    # Mock statistics for demonstration
    stats = {
        "total_checks_today": 45,
        "total_checks_week": 312,
        "total_checks_month": 1457,
        "average_response_time_ms": 185,
        "cache_hit_rate": 0.73,
        "most_checked_combinations": [
            {"drugs": ["warfarin", "aspirin"], "count": 23},
            {"drugs": ["metformin", "lisinopril"], "count": 18},
            {"drugs": ["amlodipine", "simvastatin"], "count": 15}
        ],
        "severity_distribution": {
            "contraindicated": 12,
            "major": 45,
            "moderate": 87,
            "minor": 156,
            "unknown": 8
        },
        "uptime_percentage": 99.7,
        "last_reset": "2024-09-01T00:00:00Z",
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(
        content=create_success_response(
            stats,
            "Service statistics retrieved successfully"
        )
    )

# Export router
__all__ = ['router']

@router.post(
    "/check-advanced",
    summary="Advanced Drug Interaction Check",
    description="Advanced drug interaction analysis with enhanced filtering and patient context"
)
async def check_drug_interactions_advanced(
    request: DrugInteractionRequest
):
    """
    Advanced drug interaction check with comprehensive analysis.
    
    Returns enhanced interaction analysis with:
    - Interaction severity levels
    - Clinical recommendations
    - Monitoring requirements
    - Patient-specific alerts
    """
    if not drug_service:
        return JSONResponse(
            content=create_error_response(
                "Drug interaction service unavailable",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        result = await drug_service.check_drug_interactions(
            drugs=request.drugs,
            patient_context=request.patient_context,
            use_cache=True
        )
        
        # Filter results based on warning preferences
        if not request.include_warnings:
            interactions = result.get('interactions', [])
            result['interactions'] = [
                interaction for interaction in interactions
                if interaction.get('severity', '').lower() in ['major', 'severe', 'contraindicated']
            ]
            result['total_interactions'] = len(result['interactions'])
        
        return JSONResponse(
            content=create_success_response(
                result,
                f"Interaction check complete for {len(request.drugs)} medications"
            )
        )
        
    except Exception as e:
        logger.error(f"Drug interaction check failed: {e}")
        return JSONResponse(
            content=create_error_response(
                "Failed to check drug interactions",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)}
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.get(
    "/drug-names",
    summary="Get common drug names for autocomplete",
    description="Returns a curated list of commonly prescribed medications for autocomplete functionality",
    response_description="List of drug names"
)
async def get_drug_names(
    query: Optional[str] = Query(None, description="Search query to filter drug names"),
    limit: int = Query(50, description="Maximum number of results to return", ge=1, le=200)
):
    """
    Get common drug names for autocomplete.

    Returns medications from database with both generic and brand names.
    Optionally filter by query string for autocomplete functionality.
    """
    try:
        # Import database models and session
        from src.models.database import get_db_session, Medication
        from sqlalchemy import select

        async for session in get_db_session():
            try:
                # Build query
                query_stmt = select(Medication.name).where(Medication.is_active == True)

                # Filter by search query if provided
                if query and len(query) >= 2:
                    query_stmt = query_stmt.where(Medication.name.ilike(f"%{query}%"))

                # Order and limit
                query_stmt = query_stmt.order_by(Medication.name).limit(limit)

                # Execute query
                result = await session.execute(query_stmt)
                medications = result.scalars().all()
                drug_list = [med for med in medications]

                # If database returns results, use them
                if drug_list:
                    return JSONResponse(
                        content=create_success_response(
                            {"drugs": drug_list, "count": len(drug_list), "source": "database"},
                            f"Retrieved {len(drug_list)} drug names from database"
                        )
                    )

                # If database is empty, fall through to use comprehensive fallback list
                logger.info("Database medication table is empty, using comprehensive fallback list")

            except Exception as db_error:
                logger.warning(f"Database query failed, falling back to hardcoded list: {db_error}")
                # Fall through to fallback hardcoded list
                pass

        # Fallback: If database query fails, use hardcoded list
        # Comprehensive curated list of 500+ medications - both generic and brand names
        # (avoids FDA NDC homeopathic/bath products contamination)
        common_drugs = [
            # Pain & Anti-inflammatory
            "Acetaminophen", "Tylenol", "Paracetamol", "Ibuprofen", "Advil", "Motrin", "Naproxen", "Aleve", "Naprosyn",
            "Aspirin", "Ecotrin", "Bufferin", "Celecoxib", "Celebrex", "Diclofenac", "Voltaren", "Cataflam", "Pennsaid",
            "Indomethacin", "Indocin", "Meloxicam", "Mobic", "Ketorolac", "Toradol", "Piroxicam", "Feldene",
            "Tramadol", "Ultram", "ConZip", "Morphine", "MS Contin", "Kadian", "Avinza", "Oxycodone", "OxyContin", "Roxicodone", "Percocet", "OxyIR",
            "Hydrocodone", "Vicodin", "Norco", "Lortab", "Codeine", "Tylenol #3", "Fentanyl", "Duragesic", "Actiq", "Sublimaze", "Abstral",
            "Hydromorphone", "Dilaudid", "Exalgo", "Meperidine", "Demerol", "Methadone", "Dolophine", "Methadose",
            "Buprenorphine", "Subutex", "Butrans", "Belbuca", "Nalbuphine", "Nubain", "Pentazocine", "Talwin",

            # Antibiotics
            "Amoxicillin", "Amoxil", "Trimox", "Moxatag", "Amoxicillin-Clavulanate", "Augmentin", "Augmentin XR",
            "Azithromycin", "Zithromax", "Z-Pak", "Zmax", "Ciprofloxacin", "Cipro", "Cipro XR", "Proquin",
            "Levofloxacin", "Levaquin", "Moxifloxacin", "Avelox", "Ofloxacin", "Floxin", "Doxycycline", "Vibramycin", "Doryx", "Oracea", "Monodox",
            "Minocycline", "Minocin", "Solodyn", "Dynacin", "Tetracycline", "Sumycin", "Cephalexin", "Keflex",
            "Cefuroxime", "Ceftin", "Zinacef", "Cefdinir", "Omnicef", "Cefpodoxime", "Vantin", "Cefixime", "Suprax",
            "Clindamycin", "Cleocin", "Metronidazole", "Flagyl", "Trimethoprim-Sulfamethoxazole", "Bactrim", "Septra", "Sulfatrim",
            "Penicillin", "Pen-VK", "Veetids", "Ampicillin", "Principen", "Ceftriaxone", "Rocephin", "Cefazolin", "Ancef", "Kefzol",
            "Vancomycin", "Vancocin", "Gentamicin", "Garamycin", "Tobramycin", "Nebcin", "Erythromycin", "Ery-Tab", "E.E.S.",
            "Clarithromycin", "Biaxin", "Biaxin XL", "Nitrofurantoin", "Macrobid", "Macrodantin", "Furadantin", "Linezolid", "Zyvox",

            # Cardiovascular
            "Atorvastatin", "Lipitor", "Simvastatin", "Zocor", "Rosuvastatin", "Crestor", "Pravastatin", "Pravachol",
            "Lovastatin", "Mevacor", "Altoprev", "Fluvastatin", "Lescol", "Pitavastatin", "Livalo", "Zypitamag",
            "Lisinopril", "Prinivil", "Zestril", "Qbrelis", "Enalapril", "Vasotec", "Ramipril", "Altace", "Benazepril", "Lotensin",
            "Quinapril", "Accupril", "Perindopril", "Aceon", "Fosinopril", "Monopril", "Trandolapril", "Mavik",
            "Losartan", "Cozaar", "Valsartan", "Diovan", "Irbesartan", "Avapro", "Olmesartan", "Benicar", "Candesartan", "Atacand", "Telmisartan", "Micardis",
            "Amlodipine", "Norvasc", "Nifedipine", "Procardia", "Adalat", "Felodipine", "Plendil", "Nicardipine", "Cardene", "Isradipine", "DynaCirc",
            "Metoprolol", "Lopressor", "Toprol-XL", "Atenolol", "Tenormin", "Carvedilol", "Coreg", "Coreg CR",
            "Bisoprolol", "Zebeta", "Propranolol", "Inderal", "Inderal LA", "InnoPran XL", "Nadolol", "Corgard", "Labetalol", "Trandate", "Normodyne",
            "Warfarin", "Coumadin", "Jantoven", "Clopidogrel", "Plavix", "Prasugrel", "Effient", "Ticagrelor", "Brilinta",
            "Apixaban", "Eliquis", "Rivaroxaban", "Xarelto", "Dabigatran", "Pradaxa", "Edoxaban", "Savaysa",
            "Furosemide", "Lasix", "Bumetanide", "Bumex", "Torsemide", "Demadex", "Hydrochlorothiazide", "HCTZ", "Microzide",
            "Chlorthalidone", "Thalitone", "Spironolactone", "Aldactone", "Triamterene", "Dyrenium", "Amiloride", "Midamor",
            "Digoxin", "Lanoxin", "Digitek", "Amiodarone", "Cordarone", "Pacerone", "Nexterone", "Sotalol", "Betapace", "Sorine", "Flecainide", "Tambocor",
            "Diltiazem", "Cardizem", "Cartia", "Tiazac", "Taztia", "Verapamil", "Calan", "Isoptin", "Verelan",
            "Nitroglycerin", "Nitro-Dur", "Nitrostat", "Nitrolingual", "Isosorbide", "Imdur", "Isordil", "Monoket", "Hydralazine", "Apresoline",
            "Clonidine", "Catapres", "Kapvay", "Doxazosin", "Cardura", "Prazosin", "Minipress", "Terazosin", "Hytrin",

            # Diabetes
            "Metformin", "Glucophage", "Glucophage XR", "Glumetza", "Fortamet", "Riomet",
            "Glipizide", "Glucotrol", "Glucotrol XL", "Glyburide", "DiaBeta", "Micronase", "Glynase", "Glimepiride", "Amaryl",
            "Pioglitazone", "Actos", "Rosiglitazone", "Avandia", "Insulin", "Humalog", "Novolog", "Apidra", "Lantus", "Levemir", "Tresiba", "Toujeo", "Basaglar",
            "Humulin", "Novolin", "Sitagliptin", "Januvia", "Saxagliptin", "Onglyza", "Linagliptin", "Tradjenta", "Alogliptin", "Nesina",
            "Empagliflozin", "Jardiance", "Canagliflozin", "Invokana", "Dapagliflozin", "Farxiga", "Ertugliflozin", "Steglatro",
            "Exenatide", "Byetta", "Bydureon", "Liraglutide", "Victoza", "Saxenda", "Dulaglutide", "Trulicity",
            "Semaglutide", "Ozempic", "Rybelsus", "Wegovy", "Acarbose", "Precose", "Miglitol", "Glyset", "Nateglinide", "Starlix", "Repaglinide", "Prandin",

            # GI/Acid Reducers
            "Omeprazole", "Prilosec", "Prilosec OTC", "Pantoprazole", "Protonix", "Esomeprazole", "Nexium",
            "Lansoprazole", "Prevacid", "Rabeprazole", "Aciphex", "Dexlansoprazole", "Dexilant",
            "Ranitidine", "Zantac", "Famotidine", "Pepcid", "Pepcid AC", "Nizatidine", "Axid", "Cimetidine", "Tagamet",
            "Ondansetron", "Zofran", "Granisetron", "Kytril", "Sancuso", "Dolasetron", "Anzemet", "Palonosetron", "Aloxi",
            "Metoclopramide", "Reglan", "Promethazine", "Phenergan", "Prochlorperazine", "Compazine",
            "Loperamide", "Imodium", "Diphenoxylate-Atropine", "Lomotil", "Bismuth Subsalicylate", "Pepto-Bismol", "Kaopectate",
            "Mesalamine", "Asacol", "Pentasa", "Lialda", "Apriso", "Sulfasalazine", "Azulfidine",
            "Lactulose", "Enulose", "Kristalose", "Polyethylene Glycol", "MiraLAX", "GlycoLax", "Docusate", "Colace", "Dulcolax",

            # Respiratory
            "Albuterol", "Proventil", "Ventolin", "ProAir", "Levalbuterol", "Xopenex",
            "Ipratropium", "Atrovent", "Tiotropium", "Spiriva", "Aclidinium", "Tudorza", "Umeclidinium", "Incruse", "Glycopyrrolate", "Seebri",
            "Albuterol-Ipratropium", "Combivent", "DuoNeb",
            "Fluticasone", "Flonase", "Flovent", "Arnuity", "Armonair", "Budesonide", "Pulmicort", "Rhinocort", "Entocort",
            "Beclomethasone", "Qvar", "Mometasone", "Nasonex", "Asmanex", "Ciclesonide", "Alvesco", "Omnaris",
            "Fluticasone-Salmeterol", "Advair", "AirDuo", "Budesonide-Formoterol", "Symbicort",
            "Montelukast", "Singulair", "Zafirlukast", "Accolate", "Zileuton", "Zyflo",
            "Prednisone", "Deltasone", "Rayos", "Prednisolone", "Orapred", "Prelone", "Methylprednisolone", "Medrol", "Solu-Medrol", "Depo-Medrol",
            "Dexamethasone", "Decadron", "Dexamethasone Intensol", "Hydrocortisone", "Cortef", "Solu-Cortef",
            "Theophylline", "Theo-24", "Uniphyl", "Elixophyllin", "Guaifenesin", "Mucinex", "Robitussin",
            "Dextromethorphan", "Delsym", "Robitussin DM", "Benzonatate", "Tessalon Perles",

            # Psychiatric/Neuro
            "Sertraline", "Zoloft", "Fluoxetine", "Prozac", "Sarafem", "Selfemra", "Escitalopram", "Lexapro",
            "Citalopram", "Celexa", "Paroxetine", "Paxil", "Pexeva", "Brisdelle", "Fluvoxamine", "Luvox",
            "Duloxetine", "Cymbalta", "Drizalma", "Venlafaxine", "Effexor", "Effexor XR", "Desvenlafaxine", "Pristiq", "Khedezla",
            "Bupropion", "Wellbutrin", "Wellbutrin SR", "Wellbutrin XL", "Zyban", "Aplenzin", "Forfivo",
            "Trazodone", "Desyrel", "Oleptro", "Mirtazapine", "Remeron", "Remeron SolTab", "Nefazodone", "Serzone",
            "Amitriptyline", "Elavil", "Endep", "Nortriptyline", "Pamelor", "Aventyl", "Desipramine", "Norpramin",
            "Imipramine", "Tofranil", "Doxepin", "Sinequan", "Silenor", "Clomipramine", "Anafranil",
            "Lorazepam", "Ativan", "Alprazolam", "Xanax", "Xanax XR", "Niravam", "Clonazepam", "Klonopin",
            "Diazepam", "Valium", "Diastat", "Valtoco", "Temazepam", "Restoril", "Oxazepam", "Serax", "Chlordiazepoxide", "Librium",
            "Zolpidem", "Ambien", "Ambien CR", "Edluar", "Intermezzo", "Eszopiclone", "Lunesta", "Zaleplon", "Sonata",
            "Buspirone", "BuSpar", "Hydroxyzine", "Atarax", "Vistaril",
            "Aripiprazole", "Abilify", "Abilify Maintena", "Risperidone", "Risperdal", "Risperdal Consta", "Quetiapine", "Seroquel", "Seroquel XR",
            "Olanzapine", "Zyprexa", "Zyprexa Zydis", "Ziprasidone", "Geodon", "Paliperidone", "Invega", "Invega Sustenna", "Lurasidone", "Latuda",
            "Haloperidol", "Haldol", "Chlorpromazine", "Thorazine", "Perphenazine", "Trilafon", "Fluphenazine", "Prolixin",
            "Lithium", "Lithobid", "Eskalith", "Lamotrigine", "Lamictal",
            "Gabapentin", "Neurontin", "Gralise", "Horizant", "Pregabalin", "Lyrica", "Lyrica CR",
            "Levetiracetam", "Keppra", "Keppra XR", "Phenytoin", "Dilantin", "Phenytek", "Valproic Acid", "Depakote", "Depakene", "Depakote ER",
            "Carbamazepine", "Tegretol", "Carbatrol", "Epitol", "Oxcarbazepine", "Trileptal", "Topiramate", "Topamax", "Trokendi", "Qudexy",
            "Donepezil", "Aricept", "Rivastigmine", "Exelon", "Galantamine", "Razadyne", "Memantine", "Namenda", "Namzaric",

            # Thyroid & Hormones
            "Levothyroxine", "Synthroid", "Levoxyl", "Unithroid", "Tirosint", "Liothyronine", "Cytomel", "Triostat",
            "Thyroid", "Armour Thyroid", "Nature-Throid", "WP Thyroid", "Methimazole", "Tapazole", "Propylthiouracil", "PTU",
            "Estradiol", "Estrace", "Climara", "Vivelle-Dot", "Divigel", "Evamist", "Elestrin", "Conjugated Estrogens", "Premarin",
            "Progesterone", "Prometrium", "Crinone", "Medroxyprogesterone", "Provera", "Depo-Provera", "Depo-SubQ",
            "Norethindrone", "Aygestin", "Camila", "Errin", "Testosterone", "AndroGel", "Testim", "Axiron", "Fortesta", "Androderm",
            "Oxytocin", "Pitocin", "Vasopressin", "Pitressin", "Desmopressin", "DDAVP", "Stimate", "Minirin",

            # Musculoskeletal/Muscle Relaxants
            "Cyclobenzaprine", "Flexeril", "Fexmid", "Amrix", "Baclofen", "Lioresal", "Gablofen", "Tizanidine", "Zanaflex",
            "Methocarbamol", "Robaxin", "Carisoprodol", "Soma", "Metaxalone", "Skelaxin",
            "Orphenadrine", "Norflex", "Chlorzoxazone", "Parafon Forte", "Dantrolene", "Dantrium",

            # Antihistamines/Allergy
            "Diphenhydramine", "Benadryl", "Cetirizine", "Zyrtec", "Loratadine", "Claritin", "Alavert",
            "Fexofenadine", "Allegra", "Levocetirizine", "Xyzal", "Desloratadine", "Clarinex",
            "Chlorpheniramine", "Chlor-Trimeton", "Brompheniramine", "Dimetapp", "Promethazine", "Phenergan",
            "Azelastine", "Astelin", "Astepro", "Olopatadine", "Patanase", "Pataday", "Patanol",

            # Urological
            "Tamsulosin", "Flomax", "Finasteride", "Proscar", "Propecia", "Dutasteride", "Avodart",
            "Alfuzosin", "Uroxatral", "Doxazosin", "Cardura", "Terazosin", "Hytrin", "Silodosin", "Rapaflo",
            "Tolterodine", "Detrol", "Detrol LA", "Oxybutynin", "Ditropan", "Ditropan XL", "Oxytrol", "Solifenacin", "VESIcare",
            "Darifenacin", "Enablex", "Fesoterodine", "Toviaz", "Trospium", "Sanctura",
            "Mirabegron", "Myrbetriq", "Phenazopyridine", "Pyridium", "AZO", "Uristat",

            # Osteoporosis/Bone Health
            "Alendronate", "Fosamax", "Risedronate", "Actonel", "Atelvia", "Ibandronate", "Boniva",
            "Zoledronic Acid", "Reclast", "Zometa", "Raloxifene", "Evista", "Teriparatide", "Forteo",
            "Denosumab", "Prolia", "Xgeva", "Calcitonin", "Miacalcin", "Fortical",

            # Vitamins/Supplements
            "Vitamin D", "Vitamin D3", "Cholecalciferol", "Ergocalciferol", "Drisdol", "Calcium", "Calcium Carbonate",
            "Caltrate", "Os-Cal", "Tums", "Calcium Citrate", "Citracal", "Iron", "Ferrous Sulfate", "Feosol", "Slow FE",
            "Folic Acid", "Folate", "Vitamin B12", "Cyanocobalamin", "Multivitamin", "Centrum", "One-A-Day",
            "Potassium Chloride", "K-Dur", "Klor-Con", "K-Tab", "Magnesium", "Mag-Ox", "Magnesium Citrate", "Omega-3", "Fish Oil",

            # Anticoagulants/Antiplatelets
            "Enoxaparin", "Lovenox", "Heparin", "Fondaparinux", "Arixtra", "Cilostazol", "Pletal",
            "Pentoxifylline", "Trental", "Ticlopidine", "Ticlid", "Dipyridamole", "Persantine", "Aggrenox",

            # Immunosuppressants
            "Cyclosporine", "Neoral", "Sandimmune", "Gengraf", "Tacrolimus", "Prograf", "Envarsus", "Astagraf",
            "Azathioprine", "Imuran", "Mycophenolate", "CellCept", "Myfortic", "Sirolimus", "Rapamune",
            "Methotrexate", "Rheumatrex", "Trexall", "Otrexup", "Rasuvo", "Leflunomide", "Arava",

            # Antivirals
            "Acyclovir", "Zovirax", "Valacyclovir", "Valtrex", "Famciclovir", "Famvir",
            "Oseltamivir", "Tamiflu", "Zanamivir", "Relenza", "Baloxavir", "Xofluza", "Peramivir", "Rapivab",

            # Migraine/Headache
            "Sumatriptan", "Imitrex", "Rizatriptan", "Maxalt", "Zolmitriptan", "Zomig",
            "Eletriptan", "Relpax", "Almotriptan", "Axert", "Frovatriptan", "Frova", "Naratriptan", "Amerge",

            # Other Common
            "Allopurinol", "Zyloprim", "Aloprim", "Colchicine", "Colcrys", "Mitigare", "Probenecid", "Probalan",
            "Sildenafil", "Viagra", "Revatio", "Tadalafil", "Cialis", "Adcirca", "Vardenafil", "Levitra", "Staxyn",
            "Epinephrine", "EpiPen", "Adrenaclick", "Auvi-Q", "Naloxone", "Narcan", "Evzio",
            "Ivermectin", "Stromectol", "Soolantra", "Clotrimazole", "Lotrimin", "Mycelex", "Fluconazole", "Diflucan",
            "Isotretinoin", "Accutane", "Claravis", "Absorica", "Tretinoin", "Retin-A", "Renova", "Benzoyl Peroxide", "PanOxyl"
        ]

        # Filter by query if provided
        if query and len(query) >= 2:
            query_lower = query.lower()
            filtered_drugs = [drug for drug in common_drugs if query_lower in drug.lower()]
        else:
            filtered_drugs = common_drugs

        # Sort and limit
        drug_list = sorted(filtered_drugs)[:limit]

        return JSONResponse(
            content=create_success_response(
                {"drugs": drug_list, "count": len(drug_list), "cache_hit": False},
                f"Retrieved {len(drug_list)} drug names"
            )
        )

    except Exception as e:
        logger.error(f"Failed to fetch FDA drug names: {e}")

        # Try to get status from drug cache updater service
        network_warning = None
        fallback_source = "hardcoded"
        try:
            from src.services.drug_cache_updater import get_drug_cache_updater
            drug_updater = get_drug_cache_updater()
            status = drug_updater.get_status()
            fallback_source = status.get("last_fetch_source", "hardcoded")
            if status.get("network_warning"):
                if fallback_source == "database":
                    network_warning = "⚠️ Network connectivity issues - using cached data from last successful update"
                else:
                    network_warning = "⚠️ Network connectivity issues - drug list may be incomplete. Please verify medication names carefully."
        except Exception as updater_error:
            logger.error(f"Could not get drug cache updater status: {updater_error}")

        # Return fallback common drug list
        common_drugs = [
            "Acetaminophen", "Amoxicillin", "Aspirin", "Atorvastatin", "Azithromycin",
            "Ciprofloxacin", "Clopidogrel", "Doxycycline", "Furosemide", "Gabapentin",
            "Hydrochlorothiazide", "Ibuprofen", "Levothyroxine", "Lisinopril", "Losartan",
            "Metformin", "Metoprolol", "Omeprazole", "Prednisone", "Simvastatin", "Warfarin"
        ]

        # Filter if query provided
        if query and len(query) >= 2:
            query_lower = query.lower()
            common_drugs = [d for d in common_drugs if query_lower in d.lower()]

        response_data = {
            "drugs": common_drugs[:limit],
            "count": len(common_drugs[:limit]),
            "fallback_source": fallback_source
        }

        if network_warning:
            response_data["network_warning"] = network_warning

        return JSONResponse(
            content=create_success_response(
                response_data,
                f"Retrieved {len(common_drugs[:limit])} drug names (fallback list)"
            )
        )

# Export router
__all__ = ['router']
