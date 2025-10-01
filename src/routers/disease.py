"""
Disease Information Router - AI Nurse Florence
Following External Service Integration and API Design Standards from coding instructions
"""

from fastapi import APIRouter, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import httpx
import logging
import re
import xml.etree.ElementTree as ET

from ..services.disease_service import lookup_disease_info

# Conditional translation import
try:
    from src.services.translation_service import translate_text
    _has_translation = True
except ImportError:
    _has_translation = False
    async def translate_text(text: str, target_language: str, source_language: str = "en", context: str = "medical"):
        return {"translated_text": text, "success": False}

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/disease",
    tags=["medical-information", "disease"],
    responses={
        200: {"description": "Disease information retrieved successfully"},
        422: {"description": "Query needs clarification"},
        500: {"description": "External service error"}
    }
)

class RelatedArticle(BaseModel):
    pmid: str
    title: str
    authors: str
    journal: str
    pub_date: str
    summary: str
    url: str

class DiseaseResponse(BaseModel):
    query: str
    summary: Optional[str] = None
    description: Optional[str] = None
    symptoms: Optional[List[str]] = None
    disease_name: Optional[str] = None
    synonyms: Optional[List[str]] = None
    mondo_id: Optional[str] = None
    sources: Optional[List[str]] = None
    related_articles: Optional[List[RelatedArticle]] = []
    needs_clarification: Optional[bool] = False

@router.get("/lookup", response_model=DiseaseResponse)
async def lookup_disease(
    q: str = Query(...,
                   description="Disease name or condition to look up",
                   examples=["hypertension", "diabetes mellitus", "pneumonia", "t1dm", "heart attack"]),
    language: str = Query("en", description="Response language code (en, es, fr, de, it, pt, zh-CN)")
):
    """
    Look up disease information using alias mapping for reliable results.

    Supports common abbreviations (T1DM, COPD, MI) and variations.
    Provides evidence-based medical information for healthcare professionals.
    """
    try:
        # Try alias lookup first for more reliable MONDO ID matching
        from src.services.disease_alias_service import lookup_disease_by_alias

        alias_result = await lookup_disease_by_alias(q)

        # If we found an alias, use the canonical name for lookup
        lookup_query = q
        if alias_result:
            lookup_query = alias_result.get("canonical_name", q)
            logger.info(f"Alias match: '{q}' -> '{lookup_query}' (MONDO: {alias_result.get('mondo_id')})")

        result = await lookup_disease_info(lookup_query)

        if result.get("needs_clarification"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query needs clarification",
                    "clarification_question": result.get("clarification_question")
                }
            )

        # Translate description and summary if needed
        if language and language.lower() != "en" and _has_translation:
            if result.get("description"):
                trans_result = await translate_text(
                    result["description"],
                    target_language=language,
                    source_language="en",
                    context="medical"
                )
                if trans_result.get("success"):
                    result["description"] = trans_result.get("translated_text")
                    logger.info(f"Translated description to {language}")

            if result.get("summary"):
                trans_result = await translate_text(
                    result["summary"],
                    target_language=language,
                    source_language="en",
                    context="medical"
                )
                if trans_result.get("success"):
                    result["summary"] = trans_result.get("translated_text")

            # Translate symptoms if available
            if result.get("symptoms") and isinstance(result["symptoms"], list):
                translated_symptoms = []
                for symptom in result["symptoms"]:
                    trans_result = await translate_text(
                        symptom,
                        target_language=language,
                        source_language="en",
                        context="medical"
                    )
                    if trans_result.get("success"):
                        translated_symptoms.append(trans_result.get("translated_text"))
                    else:
                        translated_symptoms.append(symptom)
                result["symptoms"] = translated_symptoms

        return DiseaseResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease lookup failed for '{q}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease lookup failed: {str(e)}"
        )

@router.get(
    "/disease-names",
    summary="Get disease names for autocomplete",
    description="Returns a list of disease names with alias support for better matching",
    response_description="List of disease names"
)
async def get_disease_names(
    query: Optional[str] = Query(None, description="Search query to filter disease names"),
    limit: int = Query(50, description="Maximum number of results to return", ge=1, le=200)
):
    """
    Get disease names for autocomplete with intelligent alias matching.

    Supports abbreviations (T1DM, COPD) and variations.
    Returns canonical disease names for consistent display.
    """
    try:
        # Try alias-based autocomplete first for better results
        from src.services.disease_alias_service import get_disease_autocomplete

        if query and len(query) >= 2:
            alias_suggestions = await get_disease_autocomplete(query, limit)

            if alias_suggestions:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": f"Retrieved {len(alias_suggestions)} disease names (alias-based)",
                        "status_code": 200,
                        "data": {
                            "diseases": alias_suggestions,
                            "count": len(alias_suggestions),
                            "source": "alias_database"
                        }
                    }
                )

        # Fallback to original API-based lookup if no query or no alias results
        # Import smart cache
        from src.utils.smart_cache import SmartCacheManager
        cache_manager = SmartCacheManager()

        # Only use cache for full disease list, not for autocomplete queries
        # This ensures live API data for user searches
        cache_key = f"disease_names_{query or 'all'}_{limit}"
        use_cache = not query  # Only cache when no query (full list)

        if use_cache:
            cached_data = await cache_manager.get(cache_key)
            if cached_data:
                return JSONResponse(
                    content={
                        "success": True,
                        "message": f"Retrieved {len(cached_data)} disease names (cached)",
                        "status_code": 200,
                        "data": {
                            "diseases": cached_data,
                            "count": len(cached_data),
                            "cache_hit": True
                        }
                    }
                )

        # Fetch from BOTH MyDisease.info and MedlinePlus for comprehensive coverage
        # MyDisease.info: technical terms and synonyms
        # MedlinePlus: consumer-friendly disease names

        animal_keywords = ["chicken", "dog", "horse", "pig", "cat", "mouse",
                         "rat", "cattle", "sheep", "goat", "rabbit", "koala",
                         "quail", "guinea pig", "chinchilla", "non-human animal"]

        # Track diseases with their source for better ranking
        disease_results = {}  # {name: source} where source is "medlineplus" or "mydisease"

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # Use ONLY MedlinePlus for consumer-friendly disease names
            try:
                if query and len(query) >= 3:
                    medlineplus_url = "https://wsearch.nlm.nih.gov/ws/query"
                    params = {
                        "db": "healthTopics",
                        "term": query,
                        "retmax": limit  # Get all results from MedlinePlus only
                    }
                    response = await client.get(medlineplus_url, params=params)
                    response.raise_for_status()

                    # Parse XML response
                    root = ET.fromstring(response.text)

                    # Extract disease names from title and altTitle fields
                    for document in root.findall('.//document'):
                        # Get main title
                        title_elem = document.find('.//content[@name="title"]')
                        if title_elem is not None and title_elem.text:
                            # Remove HTML tags like <span class="qt0">
                            title = re.sub(r'<[^>]+>', '', title_elem.text)
                            if title and not any(keyword in title.lower() for keyword in animal_keywords):
                                disease_results[title] = "medlineplus"

                        # Get alternative titles
                        for alt_title in document.findall('.//content[@name="altTitle"]'):
                            if alt_title.text:
                                alt = re.sub(r'<[^>]+>', '', alt_title.text)
                                if alt and not any(keyword in alt.lower() for keyword in animal_keywords):
                                    disease_results[alt] = "medlineplus"
            except Exception as e:
                logger.warning(f"MedlinePlus fetch failed: {e}")

            # Filter out non-disease terms (treatments, tests, procedures, body parts, procedures)
            non_disease_terms = [
                "insulin", "a1c", "hba1c", "hemoglobin a1c", "glycohemoglobin",
                "blood glucose", "blood sugar", "glucose", "test", "tests",
                "medicines", "drugs", "medication", "treatment", "therapy",
                "surgery", "rehabilitation", "care", "screening", "prevention",
                "eye care", "eye health", "eye safety", "nutrition", "diet",
                "exercise", "lifestyle", "management", "monitoring",
                "diaper rash", "dialysis", "dual diagnosis"  # Non-disease conditions/procedures
            ]

            filtered_results = {}
            for name, source in disease_results.items():
                name_lower = name.lower()
                # Exclude if it's a non-disease term
                if not any(term in name_lower for term in non_disease_terms):
                    filtered_results[name] = source

            # If no results from MedlinePlus, fallback to database
            if len(filtered_results) == 0 and query:
                try:
                    from src.services.disease_cache_updater import get_disease_cache_updater
                    disease_updater = get_disease_cache_updater()
                    db_diseases = await disease_updater.get_disease_list_from_db()

                    if db_diseases:
                        # Filter database results - only match diseases that START with query
                        # This prevents false matches like "cardiac" when searching "dia"
                        for disease in db_diseases:
                            disease_lower = disease.lower()
                            query_lower = query.lower()
                            # Match if disease starts with query OR any word in disease starts with query
                            words = disease_lower.split()
                            if disease_lower.startswith(query_lower) or any(word.startswith(query_lower) for word in words):
                                # Filter out non-disease terms from database too
                                if not any(term in disease_lower for term in non_disease_terms):
                                    filtered_results[disease] = "database"
                                    if len(filtered_results) >= limit:
                                        break
                except Exception as db_error:
                    logger.warning(f"Database fallback failed: {db_error}")

            # Remove duplicates with reversed word order (e.g., "Type 1 Diabetes" vs "Diabetes Type 1")
            # and number variations (e.g., "Type 2" vs "Type II")
            # Always prefer MedlinePlus names over database names
            def normalize_for_dedup(name):
                """Normalize disease name for duplicate detection by sorting words and normalizing numbers"""
                # Convert to lowercase and split into words
                words = name.lower().split()

                # Normalize roman numerals and numbers to a standard form
                number_map = {
                    'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
                    'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5'
                }

                normalized_words = []
                for word in words:
                    # Check if word is a roman numeral or number word
                    if word in number_map:
                        normalized_words.append(number_map[word])
                    else:
                        normalized_words.append(word)

                # Sort words to detect reversed duplicates
                return " ".join(sorted(normalized_words))

            deduped_results = {}
            seen_normalized = {}

            for name, source in filtered_results.items():
                normalized = normalize_for_dedup(name)

                if normalized not in seen_normalized:
                    # First occurrence - keep it
                    seen_normalized[normalized] = name
                    deduped_results[name] = source
                else:
                    # Duplicate detected - prefer MedlinePlus name over database name
                    existing_name = seen_normalized[normalized]
                    existing_source = deduped_results[existing_name]

                    # If new entry is from MedlinePlus and existing is not, replace
                    if source == "medlineplus" and existing_source != "medlineplus":
                        del deduped_results[existing_name]
                        deduped_results[name] = source
                        seen_normalized[normalized] = name
                    # If both are from same source, keep shorter name
                    elif source == existing_source and len(name) < len(existing_name):
                        del deduped_results[existing_name]
                        deduped_results[name] = source
                        seen_normalized[normalized] = name

            # Sort results with smart ranking:
            # 1. MedlinePlus results first (consumer-friendly)
            # 2. Database results second
            # 3. Shorter names (simpler, more likely to be main diseases)
            # 4. Alphabetically within each group
            def rank_disease(name):
                source = deduped_results.get(name, "database")
                source_priority = 0 if source == "medlineplus" else (1 if source == "database" else 2)
                length_score = len(name)  # Shorter is better
                return (source_priority, length_score, name.lower())

            disease_names = sorted(deduped_results.keys(), key=rank_disease)[:limit]

            # Only cache full disease list, not autocomplete queries
            if use_cache:
                await cache_manager.set(cache_key, disease_names, ttl_seconds=86400)

            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Retrieved {len(disease_names)} disease names",
                    "status_code": 200,
                    "data": {
                        "diseases": disease_names,
                        "count": len(disease_names),
                        "cache_hit": False
                    }
                }
            )

    except Exception as e:
        logger.error(f"Failed to fetch disease names: {e}")

        # Try to get status from disease cache updater service
        network_warning = None
        fallback_source = "hardcoded"
        try:
            from src.services.disease_cache_updater import get_disease_cache_updater
            disease_updater = get_disease_cache_updater()
            status = disease_updater.get_status()
            fallback_source = status.get("last_fetch_source", "hardcoded")
            if status.get("network_warning"):
                if fallback_source == "database":
                    network_warning = "⚠️ Network connectivity issues - using cached data from last successful update"
                else:
                    network_warning = "⚠️ Network connectivity issues - disease list may be incomplete. Please verify condition names carefully."
        except Exception as updater_error:
            logger.error(f"Could not get disease cache updater status: {updater_error}")

        # COMPREHENSIVE disease list covering all major medical specialties
        common_diseases = [
            # ===== ENDOCRINE & METABOLIC =====
            # Diabetes
            "Diabetes Mellitus", "Type 1 Diabetes", "Type 2 Diabetes",
            "Gestational Diabetes", "Prediabetes", "Diabetic Ketoacidosis",
            "Hyperosmolar Hyperglycemic State", "Diabetic Neuropathy",
            "Diabetic Retinopathy", "Diabetic Nephropathy", "Diabetic Foot",
            "Maturity Onset Diabetes of the Young", "Neonatal Diabetes",

            # Thyroid
            "Hypothyroidism", "Hyperthyroidism", "Thyroid Nodule",
            "Hashimoto Thyroiditis", "Graves Disease", "Thyroid Cancer",
            "Thyroiditis", "Goiter", "Thyrotoxicosis", "Myxedema",

            # Other Endocrine
            "Cushing Syndrome", "Addison Disease", "Pheochromocytoma",
            "Acromegaly", "Hypopituitarism", "Prolactinoma",
            "Primary Hyperparathyroidism", "Hypoparathyroidism",
            "Polycystic Ovary Syndrome", "Metabolic Syndrome",
            "Lipodystrophy", "Gaucher Disease", "Fabry Disease",

            # Metabolic
            "Hyperlipidemia", "Hypercholesterolemia", "Hypertriglyceridemia",
            "Obesity", "Malnutrition", "Vitamin D Deficiency",
            "Vitamin B12 Deficiency", "Iron Deficiency", "Folate Deficiency",
            "Scurvy", "Rickets", "Osteomalacia", "Kwashiorkor", "Marasmus",
            "Electrolyte Imbalance", "Hyperkalemia", "Hypokalemia",
            "Hypernatremia", "Hyponatremia", "Hypercalcemia", "Hypocalcemia",
            "Hypermagnesemia", "Hypomagnesemia", "Metabolic Acidosis",
            "Metabolic Alkalosis", "Dehydration", "Gout", "Pseudogout",
            "Hemochromatosis", "Wilson Disease", "Porphyria",

            # ===== CARDIOVASCULAR =====
            "Hypertension", "Hypertensive Crisis", "Resistant Hypertension",
            "Heart Failure", "Congestive Heart Failure", "Acute Heart Failure",
            "Systolic Heart Failure", "Diastolic Heart Failure",
            "Coronary Artery Disease", "Acute Coronary Syndrome",
            "Acute Myocardial Infarction", "STEMI", "NSTEMI",
            "Unstable Angina", "Angina Pectoris", "Stable Angina",
            "Atrial Fibrillation", "Atrial Flutter", "Ventricular Fibrillation",
            "Ventricular Tachycardia", "Supraventricular Tachycardia",
            "Bradycardia", "Sick Sinus Syndrome", "Heart Block",
            "Cardiomyopathy", "Dilated Cardiomyopathy", "Hypertrophic Cardiomyopathy",
            "Restrictive Cardiomyopathy", "Takotsubo Cardiomyopathy",
            "Myocarditis", "Pericarditis", "Endocarditis", "Pericardial Effusion",
            "Cardiac Tamponade", "Valvular Heart Disease", "Aortic Stenosis",
            "Aortic Regurgitation", "Mitral Stenosis", "Mitral Regurgitation",
            "Mitral Valve Prolapse", "Tricuspid Regurgitation",
            "Rheumatic Heart Disease", "Congenital Heart Disease",
            "Peripheral Artery Disease", "Deep Vein Thrombosis",
            "Pulmonary Embolism", "Aortic Aneurysm", "Aortic Dissection",
            "Carotid Artery Stenosis", "Raynaud Phenomenon", "Vasculitis",
            "Thromboangiitis Obliterans", "Lymphedema",

            # ===== RESPIRATORY =====
            "Asthma", "Exercise-Induced Asthma", "Allergic Asthma",
            "Chronic Obstructive Pulmonary Disease", "Emphysema", "Chronic Bronchitis",
            "Pneumonia", "Community-Acquired Pneumonia", "Hospital-Acquired Pneumonia",
            "Aspiration Pneumonia", "Pneumocystis Pneumonia",
            "Acute Bronchitis", "Bronchiectasis", "Bronchiolitis",
            "Tuberculosis", "Latent Tuberculosis", "Active Tuberculosis",
            "Pulmonary Fibrosis", "Idiopathic Pulmonary Fibrosis",
            "Interstitial Lung Disease", "Sarcoidosis",
            "Acute Respiratory Distress Syndrome", "Respiratory Failure",
            "Sleep Apnea", "Obstructive Sleep Apnea", "Central Sleep Apnea",
            "Pleural Effusion", "Pneumothorax", "Hemothorax", "Empyema",
            "Lung Abscess", "Pulmonary Hypertension", "Cor Pulmonale",
            "Cystic Fibrosis", "Alpha-1 Antitrypsin Deficiency",
            "COVID-19", "Influenza", "Respiratory Syncytial Virus",
            "Whooping Cough", "Legionnaires Disease",
            "Chronic Cough", "Hemoptysis", "Hypoxemia",

            # ===== GASTROINTESTINAL =====
            "Gastroesophageal Reflux Disease", "Barrett Esophagus",
            "Esophagitis", "Esophageal Varices", "Achalasia",
            "Peptic Ulcer Disease", "Gastric Ulcer", "Duodenal Ulcer",
            "Gastritis", "Helicobacter Pylori Infection",
            "Gastroparesis", "Gastric Cancer", "Esophageal Cancer",
            "Inflammatory Bowel Disease", "Crohn Disease", "Ulcerative Colitis",
            "Irritable Bowel Syndrome", "Celiac Disease", "Diverticulosis",
            "Diverticulitis", "Appendicitis", "Bowel Obstruction",
            "Ileus", "Intussusception", "Volvulus", "Ischemic Colitis",
            "Colonic Polyps", "Colorectal Cancer", "Colon Cancer", "Rectal Cancer",
            "Hemorrhoids", "Anal Fissure", "Perianal Abscess", "Fistula",
            "Constipation", "Diarrhea", "Clostridium Difficile Infection",
            "Malabsorption", "Lactose Intolerance", "Small Intestinal Bacterial Overgrowth",
            "Hepatitis", "Hepatitis A", "Hepatitis B", "Hepatitis C",
            "Autoimmune Hepatitis", "Alcoholic Hepatitis",
            "Cirrhosis", "Liver Failure", "Acute Liver Failure",
            "Non-Alcoholic Fatty Liver Disease", "Non-Alcoholic Steatohepatitis",
            "Primary Biliary Cholangitis", "Primary Sclerosing Cholangitis",
            "Hepatocellular Carcinoma", "Liver Cancer",
            "Pancreatitis", "Acute Pancreatitis", "Chronic Pancreatitis",
            "Pancreatic Cancer", "Cholelithiasis", "Cholecystitis",
            "Cholangitis", "Biliary Colic", "Choledocholithiasis",

            # ===== RENAL & UROLOGIC =====
            "Chronic Kidney Disease", "Acute Kidney Injury", "End-Stage Renal Disease",
            "Nephrotic Syndrome", "Nephritic Syndrome", "Glomerulonephritis",
            "IgA Nephropathy", "Focal Segmental Glomerulosclerosis",
            "Membranous Nephropathy", "Minimal Change Disease",
            "Diabetic Nephropathy", "Hypertensive Nephropathy",
            "Polycystic Kidney Disease", "Kidney Stones", "Nephrolithiasis",
            "Hydronephrosis", "Renal Artery Stenosis", "Renal Cell Carcinoma",
            "Bladder Cancer", "Urinary Tract Infection", "Cystitis", "Pyelonephritis",
            "Urinary Incontinence", "Overactive Bladder", "Urinary Retention",
            "Benign Prostatic Hyperplasia", "Prostatitis", "Prostate Cancer",
            "Testicular Cancer", "Erectile Dysfunction", "Hematuria", "Proteinuria",

            # ===== HEMATOLOGIC =====
            "Anemia", "Iron Deficiency Anemia", "Pernicious Anemia",
            "Aplastic Anemia", "Hemolytic Anemia", "Sickle Cell Disease",
            "Thalassemia", "Glucose-6-Phosphate Dehydrogenase Deficiency",
            "Polycythemia Vera", "Thrombocytopenia", "Immune Thrombocytopenia",
            "Thrombotic Thrombocytopenic Purpura", "Hemophilia",
            "Von Willebrand Disease", "Disseminated Intravascular Coagulation",
            "Leukemia", "Acute Lymphoblastic Leukemia", "Acute Myeloid Leukemia",
            "Chronic Lymphocytic Leukemia", "Chronic Myeloid Leukemia",
            "Lymphoma", "Hodgkin Lymphoma", "Non-Hodgkin Lymphoma",
            "Multiple Myeloma", "Myelodysplastic Syndrome",
            "Myeloproliferative Neoplasm", "Essential Thrombocythemia",
            "Primary Myelofibrosis", "Agranulocytosis", "Neutropenia",
            "Pancytopenia", "Hypercoagulable State", "Antiphospholipid Syndrome",

            # ===== INFECTIOUS DISEASES =====
            "Sepsis", "Severe Sepsis", "Septic Shock", "Bacteremia",
            "Cellulitis", "Abscess", "Necrotizing Fasciitis", "Erysipelas",
            "Meningitis", "Bacterial Meningitis", "Viral Meningitis",
            "Encephalitis", "Brain Abscess", "Endocarditis",
            "Osteomyelitis", "Septic Arthritis", "HIV/AIDS",
            "Mononucleosis", "Cytomegalovirus", "Epstein-Barr Virus",
            "Herpes Simplex Virus", "Herpes Zoster", "Shingles", "Chickenpox",
            "Measles", "Mumps", "Rubella", "Tetanus", "Diphtheria",
            "Malaria", "Dengue Fever", "Lyme Disease", "Rocky Mountain Spotted Fever",
            "Toxic Shock Syndrome", "Scarlet Fever", "Streptococcal Pharyngitis",
            "Pertussis", "Candidiasis", "Aspergillosis", "Histoplasmosis",

            # ===== NEUROLOGICAL =====
            "Stroke", "Ischemic Stroke", "Hemorrhagic Stroke",
            "Transient Ischemic Attack", "Subarachnoid Hemorrhage",
            "Intracerebral Hemorrhage", "Subdural Hematoma", "Epidural Hematoma",
            "Alzheimer Disease", "Vascular Dementia", "Dementia",
            "Lewy Body Dementia", "Frontotemporal Dementia",
            "Parkinson Disease", "Multiple System Atrophy", "Progressive Supranuclear Palsy",
            "Huntington Disease", "Amyotrophic Lateral Sclerosis",
            "Multiple Sclerosis", "Myasthenia Gravis", "Guillain-Barre Syndrome",
            "Epilepsy", "Seizure Disorder", "Status Epilepticus",
            "Migraine", "Tension Headache", "Cluster Headache",
            "Trigeminal Neuralgia", "Bell Palsy", "Peripheral Neuropathy",
            "Diabetic Neuropathy", "Charcot-Marie-Tooth Disease",
            "Restless Legs Syndrome", "Narcolepsy", "Essential Tremor",
            "Cerebral Palsy", "Hydrocephalus", "Normal Pressure Hydrocephalus",
            "Brain Tumor", "Glioblastoma", "Meningioma",
            "Spinal Cord Injury", "Cauda Equina Syndrome",
            "Cervical Spondylosis", "Spinal Stenosis",

            # ===== MUSCULOSKELETAL =====
            "Osteoarthritis", "Rheumatoid Arthritis", "Psoriatic Arthritis",
            "Ankylosing Spondylitis", "Spondyloarthritis", "Reactive Arthritis",
            "Gout", "Pseudogout", "Systemic Lupus Erythematosus",
            "Sjogren Syndrome", "Scleroderma", "Polymyositis", "Dermatomyositis",
            "Mixed Connective Tissue Disease", "Polymyalgia Rheumatica",
            "Giant Cell Arteritis", "Fibromyalgia", "Osteoporosis",
            "Osteopenia", "Paget Disease of Bone", "Osteomyelitis",
            "Fracture", "Hip Fracture", "Vertebral Compression Fracture",
            "Rotator Cuff Tear", "Adhesive Capsulitis", "Tennis Elbow",
            "Carpal Tunnel Syndrome", "De Quervain Tenosynovitis",
            "Plantar Fasciitis", "Achilles Tendinitis", "Bursitis",
            "Herniated Disc", "Degenerative Disc Disease", "Sciatica",
            "Low Back Pain", "Neck Pain", "Spinal Stenosis",
            "Muscular Dystrophy", "Rhabdomyolysis", "Compartment Syndrome",
            "Osteosarcoma", "Bone Metastases",

            # ===== DERMATOLOGIC =====
            "Acne Vulgaris", "Rosacea", "Eczema", "Atopic Dermatitis",
            "Contact Dermatitis", "Seborrheic Dermatitis", "Psoriasis",
            "Vitiligo", "Alopecia Areata", "Urticaria", "Angioedema",
            "Stevens-Johnson Syndrome", "Toxic Epidermal Necrolysis",
            "Cellulitis", "Impetigo", "Folliculitis", "Abscess",
            "Hidradenitis Suppurativa", "Pressure Ulcer", "Diabetic Foot Ulcer",
            "Venous Stasis Ulcer", "Melanoma", "Basal Cell Carcinoma",
            "Squamous Cell Carcinoma", "Cutaneous T-Cell Lymphoma",
            "Pemphigus", "Bullous Pemphigoid", "Erythema Multiforme",
            "Erythema Nodosum", "Scleroderma", "Dermatomyositis",

            # ===== PSYCHIATRIC & BEHAVIORAL =====
            "Depression", "Major Depressive Disorder", "Persistent Depressive Disorder",
            "Anxiety Disorder", "Generalized Anxiety Disorder", "Panic Disorder",
            "Social Anxiety Disorder", "Specific Phobia", "Agoraphobia",
            "Obsessive-Compulsive Disorder", "Post-Traumatic Stress Disorder",
            "Acute Stress Disorder", "Adjustment Disorder",
            "Bipolar Disorder", "Bipolar I Disorder", "Bipolar II Disorder",
            "Cyclothymic Disorder", "Schizophrenia", "Schizoaffective Disorder",
            "Delusional Disorder", "Brief Psychotic Disorder",
            "Attention-Deficit/Hyperactivity Disorder", "Autism Spectrum Disorder",
            "Anorexia Nervosa", "Bulimia Nervosa", "Binge Eating Disorder",
            "Alcohol Use Disorder", "Opioid Use Disorder", "Substance Use Disorder",
            "Insomnia", "Hypersomnia", "Personality Disorder",
            "Borderline Personality Disorder", "Antisocial Personality Disorder",

            # ===== ONCOLOGY =====
            "Breast Cancer", "Lung Cancer", "Small Cell Lung Cancer",
            "Non-Small Cell Lung Cancer", "Colorectal Cancer", "Colon Cancer",
            "Rectal Cancer", "Prostate Cancer", "Pancreatic Cancer",
            "Liver Cancer", "Hepatocellular Carcinoma", "Gastric Cancer",
            "Esophageal Cancer", "Ovarian Cancer", "Endometrial Cancer",
            "Cervical Cancer", "Bladder Cancer", "Kidney Cancer",
            "Renal Cell Carcinoma", "Thyroid Cancer", "Head and Neck Cancer",
            "Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma",
            "Brain Tumor", "Glioblastoma", "Meningioma",
            "Lymphoma", "Hodgkin Lymphoma", "Non-Hodgkin Lymphoma",
            "Leukemia", "Multiple Myeloma", "Myelodysplastic Syndrome",
            "Bone Cancer", "Osteosarcoma", "Soft Tissue Sarcoma",

            # ===== OPHTHALMOLOGIC =====
            "Cataracts", "Glaucoma", "Macular Degeneration", "Diabetic Retinopathy",
            "Retinal Detachment", "Uveitis", "Conjunctivitis", "Keratitis",
            "Corneal Ulcer", "Blepharitis", "Stye", "Chalazion",
            "Dry Eye Syndrome", "Optic Neuritis", "Retinitis Pigmentosa",

            # ===== ENT (EAR, NOSE, THROAT) =====
            "Otitis Media", "Otitis Externa", "Hearing Loss", "Tinnitus",
            "Meniere Disease", "Vertigo", "Benign Paroxysmal Positional Vertigo",
            "Sinusitis", "Rhinitis", "Allergic Rhinitis", "Nasal Polyps",
            "Pharyngitis", "Tonsillitis", "Laryngitis", "Epiglottitis",
            "Obstructive Sleep Apnea", "Vocal Cord Paralysis",

            # ===== REPRODUCTIVE & OBSTETRIC =====
            "Polycystic Ovary Syndrome", "Endometriosis", "Uterine Fibroids",
            "Ovarian Cyst", "Pelvic Inflammatory Disease", "Menopause",
            "Premature Ovarian Insufficiency", "Amenorrhea", "Dysmenorrhea",
            "Premenstrual Syndrome", "Premenstrual Dysphoric Disorder",
            "Preeclampsia", "Eclampsia", "Gestational Diabetes",
            "Placenta Previa", "Placental Abruption", "Ectopic Pregnancy",
            "Miscarriage", "Preterm Labor", "Postpartum Depression",

            # ===== ALLERGIC & IMMUNOLOGIC =====
            "Allergic Rhinitis", "Asthma", "Anaphylaxis", "Food Allergy",
            "Drug Allergy", "Urticaria", "Angioedema", "Atopic Dermatitis",
            "Systemic Lupus Erythematosus", "Rheumatoid Arthritis",
            "Sjogren Syndrome", "Scleroderma", "Vasculitis",
            "Common Variable Immunodeficiency", "Selective IgA Deficiency",
            "Chronic Granulomatous Disease",

            # ===== CRITICAL CARE & EMERGENCY =====
            "Shock", "Hypovolemic Shock", "Cardiogenic Shock", "Distributive Shock",
            "Septic Shock", "Anaphylactic Shock", "Cardiac Arrest",
            "Respiratory Arrest", "Multi-Organ Failure",
            "Acute Respiratory Distress Syndrome", "Disseminated Intravascular Coagulation",
            "Rhabdomyolysis", "Acute Liver Failure", "Fulminant Hepatic Failure",
            "Adrenal Crisis", "Myxedema Coma", "Thyroid Storm",
            "Hyperosmolar Hyperglycemic State", "Diabetic Ketoacidosis",

            # ===== TOXICOLOGY =====
            "Acetaminophen Overdose", "Salicylate Toxicity", "Opioid Overdose",
            "Benzodiazepine Overdose", "Carbon Monoxide Poisoning",
            "Alcohol Intoxication", "Alcohol Withdrawal", "Delirium Tremens",
            "Serotonin Syndrome", "Neuroleptic Malignant Syndrome",

            # ===== PEDIATRIC (Common) =====
            "Bronchiolitis", "Croup", "Kawasaki Disease", "Febrile Seizure",
            "Intussusception", "Pyloric Stenosis", "Neonatal Jaundice",
            "Respiratory Distress Syndrome", "Congenital Heart Disease",

            # ===== OTHER IMPORTANT CONDITIONS =====
            "Chronic Fatigue Syndrome", "Chronic Pain Syndrome",
            "Complex Regional Pain Syndrome", "Sarcoidosis",
            "Amyloidosis", "Behcet Disease", "Still Disease",
            "Mastocytosis", "Eosinophilic Esophagitis",
        ]

        # Smart filtering with related disease grouping
        if query and len(query) >= 2:
            query_lower = query.lower()

            # Define disease groups for smart suggestions
            disease_groups = {
                "diabetes": ["Diabetes Mellitus", "Type 1 Diabetes", "Type 2 Diabetes",
                             "Gestational Diabetes", "Prediabetes", "Diabetic Neuropathy",
                             "Diabetic Retinopathy", "Diabetic Nephropathy"],
                "heart": ["Heart Failure", "Congestive Heart Failure", "Coronary Artery Disease",
                          "Acute Myocardial Infarction", "Angina Pectoris", "Cardiomyopathy",
                          "Atrial Fibrillation"],
                "cardiac": ["Heart Failure", "Congestive Heart Failure", "Coronary Artery Disease",
                            "Acute Myocardial Infarction", "Angina Pectoris", "Cardiomyopathy",
                            "Atrial Fibrillation"],
                "kidney": ["Chronic Kidney Disease", "Acute Kidney Injury", "Kidney Stones",
                           "Nephrotic Syndrome", "Glomerulonephritis", "Diabetic Nephropathy"],
                "renal": ["Chronic Kidney Disease", "Acute Kidney Injury", "Kidney Stones",
                          "Nephrotic Syndrome", "Glomerulonephritis", "Diabetic Nephropathy"],
                "cancer": ["Breast Cancer", "Lung Cancer", "Colon Cancer", "Prostate Cancer",
                           "Pancreatic Cancer", "Melanoma", "Bladder Cancer", "Leukemia", "Lymphoma"],
                "arthritis": ["Osteoarthritis", "Rheumatoid Arthritis", "Spondyloarthritis", "Gout"],
                "thyroid": ["Hypothyroidism", "Hyperthyroidism", "Thyroid Nodule", "Hashimoto Thyroiditis"],
                "lung": ["Asthma", "Pneumonia", "Chronic Obstructive Pulmonary Disease",
                         "Bronchitis", "Emphysema", "Pulmonary Fibrosis", "Lung Cancer",
                         "Pulmonary Embolism", "Sleep Apnea", "Tuberculosis"],
                "copd": ["Chronic Obstructive Pulmonary Disease", "Emphysema", "Bronchitis"],
                "stroke": ["Stroke", "Transient Ischemic Attack"],
                "dementia": ["Dementia", "Alzheimer Disease"],
                "anemia": ["Anemia", "Iron Deficiency Anemia", "Sickle Cell Disease"],
                "hepatitis": ["Hepatitis", "Cirrhosis"],
                "bowel": ["Inflammatory Bowel Disease", "Crohn Disease", "Ulcerative Colitis",
                          "Diverticulitis"],
                "mental": ["Depression", "Anxiety Disorder", "Bipolar Disorder", "Schizophrenia",
                           "Post-Traumatic Stress Disorder"],
                "infection": ["Urinary Tract Infection", "Sepsis", "Cellulitis", "Meningitis",
                              "Endocarditis", "Osteomyelitis", "Pneumonia", "Tuberculosis"],
            }

            # Check if query matches a disease group keyword
            matched_group = None
            for keyword, group_diseases in disease_groups.items():
                if keyword in query_lower:
                    matched_group = group_diseases
                    break

            # If matched a group, prioritize those diseases
            if matched_group:
                # First add all diseases from the matched group
                filtered = [d for d in matched_group if d in common_diseases]
                # Then add other matching diseases not in the group
                other_matches = [d for d in common_diseases if query_lower in d.lower() and d not in filtered]
                common_diseases = filtered + other_matches
            else:
                # Standard substring filtering
                common_diseases = [d for d in common_diseases if query_lower in d.lower()]

        response_data = {
            "diseases": common_diseases[:limit],
            "count": len(common_diseases[:limit]),
            "cache_hit": False,
            "fallback_source": fallback_source
        }

        if network_warning:
            response_data["network_warning"] = network_warning

        return JSONResponse(
            content={
                "success": True,
                "message": f"Retrieved {len(common_diseases[:limit])} disease names (fallback list)",
                "status_code": 200,
                "data": response_data
            }
        )
