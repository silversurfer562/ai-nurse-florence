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

from ..services.disease_service import lookup_disease_info
from ..utils.config import get_educational_banner

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
    banner: str = Field(default_factory=get_educational_banner)
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
                   examples=["hypertension", "diabetes mellitus", "pneumonia"])
):
    """
    Look up disease information following External Service Integration pattern.
    
    Provides evidence-based medical information for healthcare professionals.
    All responses include educational disclaimers per API Design Standards.
    """
    try:
        result = await lookup_disease_info(q)
        
        if result.get("needs_clarification"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query needs clarification",
                    "clarification_question": result.get("clarification_question"),
                    "banner": get_educational_banner()
                }
            )
        
        return DiseaseResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Disease lookup failed: {str(e)}"
        )

@router.get(
    "/disease-names",
    summary="Get disease names for autocomplete",
    description="Returns a list of disease names from MONDO ontology for autocomplete functionality",
    response_description="List of disease names"
)
async def get_disease_names(
    query: Optional[str] = Query(None, description="Search query to filter disease names"),
    limit: int = Query(50, description="Maximum number of results to return", ge=1, le=200)
):
    """
    Get disease names for autocomplete from MONDO ontology.

    Returns a curated list of diseases and conditions.
    Optionally filter by query string for autocomplete functionality.
    Uses smart caching for performance.
    """
    try:
        # Import smart cache
        from src.utils.smart_cache import SmartCacheManager
        cache_manager = SmartCacheManager()

        # Create cache key based on query
        cache_key = f"disease_names_{query or 'all'}_{limit}"

        # Try to get from cache first
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

        # Fetch from MONDO ontology API
        # MONDO provides disease names with MONDO IDs
        mondo_url = "https://www.ebi.ac.uk/ols/api/search"

        params = {
            "ontology": "mondo",
            "type": "class",
            "rows": limit,
            "start": 0
        }

        if query and len(query) >= 2:
            params["q"] = query

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(mondo_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract disease names from response
            disease_names = []
            for doc in data.get("response", {}).get("docs", []):
                label = doc.get("label")
                if label:
                    disease_names.append(label)

            # Remove duplicates and sort
            disease_names = sorted(list(set(disease_names)))[:limit]

            # Cache for 24 hours (disease names don't change often)
            await cache_manager.set(cache_key, disease_names, ttl=86400)

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
