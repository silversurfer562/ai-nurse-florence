"""
Disease Cache Updater Service - AI Nurse Florence
Phase 4.2: Disease Information Enhancement

Automatic pre-fetching and caching of MONDO disease names list.
Runs hourly to keep disease list fresh and ready for users.
"""

import asyncio
import logging
import httpx
import uuid
from datetime import datetime
from typing import List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class DiseaseCacheUpdaterService:
    """
    Service for automatic MONDO disease list caching.

    Features:
    - Hourly background updates of MONDO disease list
    - Smart caching for instant autocomplete
    - Fallback to comprehensive common disease list if MONDO API fails
    """

    def __init__(self):
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.update_interval_seconds = 3600  # 1 hour
        self.last_update: Optional[datetime] = None
        self.cache_manager = None
        self.db_available = False
        self.last_fetch_source = None  # Track: "api", "database", "hardcoded"

        # Initialize cache manager
        try:
            from src.utils.smart_cache import SmartCacheManager
            self.cache_manager = SmartCacheManager()
            logger.info("Disease cache updater initialized with smart cache")
        except Exception as e:
            logger.warning(f"Could not initialize smart cache: {e}")

        # Check database availability
        try:
            from src.models.database import init_database
            self.db_available = True
            logger.info("Disease cache updater: Database available for fallback storage")
        except Exception as e:
            logger.warning(f"Disease cache updater: Database not available: {e}")

    async def save_disease_list_to_db(self, disease_list: List[str], source: str = "mondo_api"):
        """
        Save successful disease list fetch to database as backup.
        Only replaces existing data on successful fetch - preserves backup on failure.

        Args:
            disease_list: List of disease names to save
            source: Source of the data (mondo_api, etc.)
        """
        if not self.db_available:
            return

        try:
            from src.models.database import get_db_session, CachedDiseaseList
            from sqlalchemy import delete

            async for session in get_db_session():
                try:
                    # Only delete old data AFTER we have new successful data
                    # This ensures we always have a backup until replaced
                    await session.execute(delete(CachedDiseaseList))

                    # Create new cached list
                    cached_list = CachedDiseaseList(
                        id=str(uuid.uuid4()),
                        disease_names=disease_list,
                        source=source,
                        count=len(disease_list),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )

                    session.add(cached_list)
                    await session.commit()
                    logger.info(f"✅ Saved {len(disease_list)} diseases to database backup (source: {source})")

                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to save disease list to database: {e}")

        except Exception as e:
            logger.error(f"Database operation failed: {e}")

    async def get_disease_list_from_db(self) -> Optional[List[str]]:
        """
        Get last successful disease list from database.

        Returns:
            List of disease names from database, or None if not available
        """
        if not self.db_available:
            return None

        try:
            from src.models.database import get_db_session, CachedDiseaseList
            from sqlalchemy import select

            async for session in get_db_session():
                try:
                    result = await session.execute(
                        select(CachedDiseaseList)
                        .order_by(CachedDiseaseList.updated_at.desc())
                        .limit(1)
                    )
                    cached_list = result.scalar_one_or_none()

                    if cached_list:
                        logger.info(f"Retrieved {cached_list.count} diseases from database (source: {cached_list.source})")
                        return cached_list.disease_names

                    return None

                except Exception as e:
                    logger.error(f"Failed to retrieve disease list from database: {e}")
                    return None

        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return None

    async def fetch_mondo_disease_list(self) -> List[str]:
        """
        Fetch comprehensive disease list from MONDO ontology via EBI OLS API.

        Fallback strategy:
        1. Try MONDO API (primary source)
        2. If API fails, use last successful data from database
        3. If no database backup, use comprehensive hardcoded list

        Database backup is ONLY updated on successful API fetch,
        preserving the last known good data during network issues.

        Returns:
            List of disease names from MONDO
        """
        try:
            mondo_url = "https://www.ebi.ac.uk/ols/api/search"
            params = {
                "ontology": "mondo",
                "type": "class",
                "rows": 1000,  # Fetch large sample for comprehensive list
                "start": 0
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
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
                disease_names = sorted(list(set(disease_names)))
                logger.info(f"✅ Fetched {len(disease_names)} disease names from MONDO API")

                # ONLY save to database on successful fetch
                # This preserves the last known good data during API failures
                await self.save_disease_list_to_db(disease_names, source="mondo_api")
                self.last_fetch_source = "api"

                return disease_names

        except Exception as e:
            logger.error(f"❌ Failed to fetch MONDO disease list: {e}")
            # Try database fallback first (last successful fetch)
            # Database is NOT modified here - preserves backup
            db_diseases = await self.get_disease_list_from_db()
            if db_diseases:
                logger.info(f"✅ Using database fallback ({len(db_diseases)} diseases)")
                self.last_fetch_source = "database"
                return db_diseases

            # Final fallback to hardcoded list (worst case)
            logger.warning("⚠️ Using hardcoded fallback disease list")
            self.last_fetch_source = "hardcoded"
            return self.get_fallback_disease_list()

    def get_fallback_disease_list(self) -> List[str]:
        """
        Get comprehensive fallback list of common diseases when MONDO API is unavailable.

        Returns:
            List of common disease names
        """
        return [
            # Cardiovascular diseases
            "Hypertension", "Coronary Artery Disease", "Heart Failure", "Atrial Fibrillation",
            "Acute Myocardial Infarction", "Angina Pectoris", "Stroke", "Deep Vein Thrombosis",
            "Pulmonary Embolism", "Peripheral Artery Disease", "Cardiomyopathy",
            "Valvular Heart Disease", "Endocarditis", "Pericarditis", "Aortic Aneurysm",

            # Respiratory diseases
            "Asthma", "Chronic Obstructive Pulmonary Disease", "Pneumonia", "Bronchitis",
            "Pulmonary Fibrosis", "Tuberculosis", "Lung Cancer", "Pleural Effusion",
            "Respiratory Failure", "Pulmonary Hypertension", "Sleep Apnea",

            # Endocrine diseases
            "Diabetes Mellitus", "Hypothyroidism", "Hyperthyroidism", "Cushing Syndrome",
            "Addison Disease", "Metabolic Syndrome", "Obesity", "Hyperlipidemia",
            "Thyroid Cancer", "Pituitary Adenoma", "Diabetes Insipidus",

            # Renal diseases
            "Chronic Kidney Disease", "Acute Kidney Injury", "Nephrotic Syndrome",
            "Glomerulonephritis", "Polycystic Kidney Disease", "Renal Cell Carcinoma",
            "Urinary Tract Infection", "Pyelonephritis", "Kidney Stones",

            # Gastrointestinal diseases
            "Gastroesophageal Reflux Disease", "Peptic Ulcer Disease", "Inflammatory Bowel Disease",
            "Crohn Disease", "Ulcerative Colitis", "Irritable Bowel Syndrome",
            "Cirrhosis", "Hepatitis", "Pancreatitis", "Cholecystitis",
            "Colorectal Cancer", "Gastric Cancer", "Diverticulitis", "Appendicitis",

            # Neurological diseases
            "Alzheimer Disease", "Parkinson Disease", "Multiple Sclerosis", "Epilepsy",
            "Migraine", "Stroke", "Transient Ischemic Attack", "Meningitis",
            "Encephalitis", "Peripheral Neuropathy", "Myasthenia Gravis",
            "Guillain-Barre Syndrome", "Brain Tumor", "Dementia",

            # Psychiatric diseases
            "Depression", "Anxiety Disorder", "Bipolar Disorder", "Schizophrenia",
            "Post-Traumatic Stress Disorder", "Obsessive-Compulsive Disorder",
            "Attention Deficit Hyperactivity Disorder", "Substance Use Disorder",

            # Rheumatological diseases
            "Rheumatoid Arthritis", "Osteoarthritis", "Systemic Lupus Erythematosus",
            "Scleroderma", "Sjogren Syndrome", "Polymyalgia Rheumatica",
            "Gout", "Osteoporosis", "Fibromyalgia", "Ankylosing Spondylitis",

            # Hematological diseases
            "Anemia", "Iron Deficiency Anemia", "Sickle Cell Disease", "Thalassemia",
            "Leukemia", "Lymphoma", "Multiple Myeloma", "Thrombocytopenia",
            "Hemophilia", "Von Willebrand Disease", "Polycythemia Vera",

            # Infectious diseases
            "Sepsis", "Pneumonia", "Urinary Tract Infection", "Cellulitis",
            "Tuberculosis", "HIV/AIDS", "Hepatitis", "Influenza",
            "COVID-19", "Meningitis", "Endocarditis", "Osteomyelitis",

            # Cancer
            "Breast Cancer", "Lung Cancer", "Colorectal Cancer", "Prostate Cancer",
            "Pancreatic Cancer", "Liver Cancer", "Gastric Cancer", "Ovarian Cancer",
            "Bladder Cancer", "Melanoma", "Lymphoma", "Leukemia",

            # Dermatological diseases
            "Psoriasis", "Eczema", "Dermatitis", "Acne", "Cellulitis",
            "Skin Cancer", "Urticaria", "Rosacea",

            # Other common conditions
            "Pregnancy", "Acute Coronary Syndrome", "Syncope", "Dehydration",
            "Electrolyte Imbalance", "Malnutrition", "Pressure Ulcer",
            "Falls", "Confusion", "Chest Pain", "Abdominal Pain"
        ]

    async def update_disease_cache(self):
        """
        Update the disease cache with fresh MONDO data.
        """
        try:
            if not self.cache_manager:
                logger.warning("Cache manager not available, skipping disease cache update")
                return

            logger.info("Starting disease cache update...")

            # Fetch fresh disease list from MONDO
            disease_list = await self.fetch_mondo_disease_list()

            # Cache the full disease list (no query filter)
            cache_key = "disease_names_all_1000"
            await self.cache_manager.set(cache_key, disease_list, ttl=7200)  # 2 hours TTL

            self.last_update = datetime.now()
            logger.info(f"Disease cache updated successfully with {len(disease_list)} diseases at {self.last_update}")

        except Exception as e:
            logger.error(f"Error updating disease cache: {e}")

    async def run_background_updates(self):
        """
        Background task that updates disease cache hourly.
        """
        logger.info(f"Starting background disease cache updates with {self.update_interval_seconds/3600}h interval")

        # Do initial update immediately
        await self.update_disease_cache()

        while self.is_running:
            try:
                # Wait for next update interval
                await asyncio.sleep(self.update_interval_seconds)

                # Update the cache
                await self.update_disease_cache()

            except asyncio.CancelledError:
                logger.info("Background disease cache update task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background disease cache update: {e}")
                # Continue running even if one update fails
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def start(self):
        """
        Start the background disease cache updater service.
        """
        if self.is_running:
            logger.warning("Disease cache updater is already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self.run_background_updates())
        logger.info("Disease cache updater started")

    async def stop(self):
        """
        Stop the background disease cache updater service.
        """
        if not self.is_running:
            return

        self.is_running = False

        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        logger.info("Disease cache updater stopped")

    def get_status(self) -> dict:
        """
        Get current status of the disease cache updater.

        Returns:
            Dictionary with status information
        """
        return {
            "is_running": self.is_running,
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "update_interval_hours": self.update_interval_seconds / 3600,
            "cache_available": self.cache_manager is not None,
            "last_fetch_source": self.last_fetch_source,
            "network_warning": self.last_fetch_source in ["database", "hardcoded"]
        }

# Global instance
_disease_cache_updater: Optional[DiseaseCacheUpdaterService] = None

def get_disease_cache_updater() -> DiseaseCacheUpdaterService:
    """
    Get the global disease cache updater instance.

    Returns:
        DiseaseCacheUpdaterService instance
    """
    global _disease_cache_updater
    if _disease_cache_updater is None:
        _disease_cache_updater = DiseaseCacheUpdaterService()
    return _disease_cache_updater