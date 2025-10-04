"""
Disease Cache Updater Service - AI Nurse Florence
Phase 4.2: Disease Information Enhancement

Automatic pre-fetching and caching of MONDO disease names list.
Runs hourly to keep disease list fresh and ready for users.
"""

import asyncio
import logging
import re
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

import httpx

from src.utils.redis_cache import cache_set

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

            self.db_available = True
            logger.info(
                "Disease cache updater: Database available for fallback storage"
            )
        except Exception as e:
            logger.warning(f"Disease cache updater: Database not available: {e}")

    async def save_disease_list_to_db(
        self, disease_list: List[str], source: str = "mondo_api"
    ):
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
            from sqlalchemy import delete

            from src.models.database import CachedDiseaseList, get_db_session

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
                        updated_at=datetime.utcnow(),
                    )

                    session.add(cached_list)
                    await session.commit()
                    logger.info(
                        f"✅ Saved {len(disease_list)} diseases to database backup (source: {source})"
                    )

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
            from sqlalchemy import select

            from src.models.database import CachedDiseaseList, get_db_session

            async for session in get_db_session():
                try:
                    result = await session.execute(
                        select(CachedDiseaseList)
                        .order_by(CachedDiseaseList.updated_at.desc())
                        .limit(1)
                    )
                    cached_list = result.scalar_one_or_none()

                    if cached_list:
                        logger.info(
                            f"Retrieved {cached_list.count} diseases from database (source: {cached_list.source})"
                        )
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
        Fetch comprehensive disease list from BOTH MyDisease.info and MedlinePlus.

        Dual-source strategy:
        1. MyDisease.info: Technical terms and MONDO synonyms
        2. MedlinePlus: Consumer-friendly disease names

        Fallback strategy:
        1. Try both APIs (primary sources)
        2. If APIs fail, use last successful data from database
        3. If no database backup, use comprehensive hardcoded list

        Database backup is ONLY updated on successful API fetch,
        preserving the last known good data during network issues.

        Returns:
            List of disease names and synonyms from both sources
        """
        try:
            # Updated animal keywords to catch more variations
            animal_keywords = [
                "chicken",
                "dog",
                "horse",
                "pig",
                "cat",
                "mouse",
                "rat",
                "cattle",
                "sheep",
                "goat",
                "rabbit",
                "koala",
                "quail",
                "guinea pig",
                "chinchilla",
                "non-human animal",
            ]

            disease_names = set()

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # SOURCE 1: MyDisease.info for comprehensive disease data with synonyms
                mydisease_url = "https://mydisease.info/v1/query"
                params = {
                    "q": "disease",
                    "size": 1000,  # Fetch large sample for comprehensive list
                    "fields": "mondo.label,mondo.synonym",
                }

                response = await client.get(mydisease_url, params=params)
                response.raise_for_status()
                data = response.json()
                for hit in data.get("hits", []):
                    mondo = hit.get("mondo", {})

                    # Add primary label
                    label = mondo.get("label")
                    if label and not any(
                        keyword in label.lower() for keyword in animal_keywords
                    ):
                        disease_names.add(label)

                    # Add all synonyms (they're nested in exact and related fields)
                    synonyms_obj = mondo.get("synonym", {})
                    all_synonyms = []

                    if isinstance(synonyms_obj, dict):
                        # Get exact synonyms
                        exact = synonyms_obj.get("exact", [])
                        if isinstance(exact, list):
                            all_synonyms.extend(exact)
                        # Get related synonyms
                        related = synonyms_obj.get("related", [])
                        if isinstance(related, list):
                            all_synonyms.extend(related)
                    elif isinstance(synonyms_obj, list):
                        all_synonyms = synonyms_obj
                    elif isinstance(synonyms_obj, str):
                        all_synonyms = [synonyms_obj]

                    for synonym in all_synonyms:
                        if synonym and not any(
                            keyword in synonym.lower() for keyword in animal_keywords
                        ):
                            # Filter out technical identifiers that aren't useful for clinical search
                            # Skip: IDDM6, NIDDM5, MODY2, etc. (gene variants with numbers)
                            # Keep: IDDM, NIDDM, T1DM, T2DM (common abbreviations)
                            synonym_upper = synonym.upper()
                            is_gene_variant = (
                                bool(
                                    re.search(
                                        r"(IDDM|NIDDM|MODY|T\dDM)\d+$", synonym_upper
                                    )
                                )
                                or bool(  # Gene variants with trailing numbers
                                    re.search(r"^[A-Z]+\d+[A-Z]*\d*$", synonym)
                                )
                                or synonym.startswith(  # Codes like HLA-DQ2, FMO3, etc.
                                    "rs"
                                )
                                or "susceptibility"  # SNP identifiers
                                in synonym.lower()
                                or "protection against" in synonym.lower()
                            )
                            if not is_gene_variant:
                                disease_names.add(synonym)

                logger.info(
                    f"✅ Fetched {len(disease_names)} diseases from MyDisease.info"
                )

                # SOURCE 2: MedlinePlus for consumer-friendly disease names
                # Fetch common disease categories
                common_searches = [
                    "diabetes",
                    "cancer",
                    "heart",
                    "asthma",
                    "arthritis",
                    "hypertension",
                    "infection",
                    "mental",
                    "kidney",
                    "liver",
                    "lung",
                    "brain",
                    "blood",
                    "skin",
                    "eye",
                    "bone",
                    "pregnancy",
                    "child",
                    "elderly",
                ]

                for search_term in common_searches:
                    try:
                        medlineplus_url = "https://wsearch.nlm.nih.gov/ws/query"
                        params = {
                            "db": "healthTopics",
                            "term": search_term,
                            "retmax": 50,  # Get top 50 results per category
                        }
                        response = await client.get(medlineplus_url, params=params)
                        response.raise_for_status()

                        # Parse XML response
                        root = ET.fromstring(response.text)

                        # Extract disease names from title and altTitle fields
                        for document in root.findall(".//document"):
                            # Get main title
                            title_elem = document.find('.//content[@name="title"]')
                            if title_elem is not None and title_elem.text:
                                title = re.sub(r"<[^>]+>", "", title_elem.text)
                                if title and not any(
                                    keyword in title.lower()
                                    for keyword in animal_keywords
                                ):
                                    disease_names.add(title)

                            # Get alternative titles
                            for alt_title in document.findall(
                                './/content[@name="altTitle"]'
                            ):
                                if alt_title.text:
                                    alt = re.sub(r"<[^>]+>", "", alt_title.text)
                                    if alt and not any(
                                        keyword in alt.lower()
                                        for keyword in animal_keywords
                                    ):
                                        disease_names.add(alt)

                    except Exception as e:
                        logger.debug(
                            f"MedlinePlus fetch for '{search_term}' failed: {e}"
                        )
                        continue

                logger.info(
                    f"✅ Fetched total {len(disease_names)} diseases from both sources"
                )

                # Remove duplicates and sort
                disease_names_list = sorted(list(disease_names))

                # ONLY save to database on successful fetch
                # This preserves the last known good data during API failures
                await self.save_disease_list_to_db(
                    disease_names_list, source="dual_source_api"
                )
                self.last_fetch_source = "api"

                return disease_names_list

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
            "Hypertension",
            "Coronary Artery Disease",
            "Heart Failure",
            "Atrial Fibrillation",
            "Acute Myocardial Infarction",
            "Angina Pectoris",
            "Stroke",
            "Deep Vein Thrombosis",
            "Pulmonary Embolism",
            "Peripheral Artery Disease",
            "Cardiomyopathy",
            "Valvular Heart Disease",
            "Endocarditis",
            "Pericarditis",
            "Aortic Aneurysm",
            # Respiratory diseases
            "Asthma",
            "Chronic Obstructive Pulmonary Disease",
            "Pneumonia",
            "Bronchitis",
            "Pulmonary Fibrosis",
            "Tuberculosis",
            "Lung Cancer",
            "Pleural Effusion",
            "Respiratory Failure",
            "Pulmonary Hypertension",
            "Sleep Apnea",
            # Endocrine diseases
            "Diabetes Mellitus",
            "Hypothyroidism",
            "Hyperthyroidism",
            "Cushing Syndrome",
            "Addison Disease",
            "Metabolic Syndrome",
            "Obesity",
            "Hyperlipidemia",
            "Thyroid Cancer",
            "Pituitary Adenoma",
            "Diabetes Insipidus",
            # Renal diseases
            "Chronic Kidney Disease",
            "Acute Kidney Injury",
            "Nephrotic Syndrome",
            "Glomerulonephritis",
            "Polycystic Kidney Disease",
            "Renal Cell Carcinoma",
            "Urinary Tract Infection",
            "Pyelonephritis",
            "Kidney Stones",
            # Gastrointestinal diseases
            "Gastroesophageal Reflux Disease",
            "Peptic Ulcer Disease",
            "Inflammatory Bowel Disease",
            "Crohn Disease",
            "Ulcerative Colitis",
            "Irritable Bowel Syndrome",
            "Cirrhosis",
            "Hepatitis",
            "Pancreatitis",
            "Cholecystitis",
            "Colorectal Cancer",
            "Gastric Cancer",
            "Diverticulitis",
            "Appendicitis",
            # Neurological diseases
            "Alzheimer Disease",
            "Parkinson Disease",
            "Multiple Sclerosis",
            "Epilepsy",
            "Migraine",
            "Stroke",
            "Transient Ischemic Attack",
            "Meningitis",
            "Encephalitis",
            "Peripheral Neuropathy",
            "Myasthenia Gravis",
            "Guillain-Barre Syndrome",
            "Brain Tumor",
            "Dementia",
            # Psychiatric diseases
            "Depression",
            "Anxiety Disorder",
            "Bipolar Disorder",
            "Schizophrenia",
            "Post-Traumatic Stress Disorder",
            "Obsessive-Compulsive Disorder",
            "Attention Deficit Hyperactivity Disorder",
            "Substance Use Disorder",
            # Rheumatological diseases
            "Rheumatoid Arthritis",
            "Osteoarthritis",
            "Systemic Lupus Erythematosus",
            "Scleroderma",
            "Sjogren Syndrome",
            "Polymyalgia Rheumatica",
            "Gout",
            "Osteoporosis",
            "Fibromyalgia",
            "Ankylosing Spondylitis",
            # Hematological diseases
            "Anemia",
            "Iron Deficiency Anemia",
            "Sickle Cell Disease",
            "Thalassemia",
            "Leukemia",
            "Lymphoma",
            "Multiple Myeloma",
            "Thrombocytopenia",
            "Hemophilia",
            "Von Willebrand Disease",
            "Polycythemia Vera",
            # Infectious diseases
            "Sepsis",
            "Pneumonia",
            "Urinary Tract Infection",
            "Cellulitis",
            "Tuberculosis",
            "HIV/AIDS",
            "Hepatitis",
            "Influenza",
            "COVID-19",
            "Meningitis",
            "Endocarditis",
            "Osteomyelitis",
            # Cancer
            "Breast Cancer",
            "Lung Cancer",
            "Colorectal Cancer",
            "Prostate Cancer",
            "Pancreatic Cancer",
            "Liver Cancer",
            "Gastric Cancer",
            "Ovarian Cancer",
            "Bladder Cancer",
            "Melanoma",
            "Lymphoma",
            "Leukemia",
            # Dermatological diseases
            "Psoriasis",
            "Eczema",
            "Dermatitis",
            "Acne",
            "Cellulitis",
            "Skin Cancer",
            "Urticaria",
            "Rosacea",
            # Other common conditions
            "Pregnancy",
            "Acute Coronary Syndrome",
            "Syncope",
            "Dehydration",
            "Electrolyte Imbalance",
            "Malnutrition",
            "Pressure Ulcer",
            "Falls",
            "Confusion",
            "Chest Pain",
            "Abdominal Pain",
        ]

    async def update_disease_cache(self):
        """
        Update the disease cache with fresh MONDO data and populate aliases.
        """
        # Temporarily disabled to prevent blocking Railway startup
        logger.info(
            "Disease cache update skipped - disabled during startup troubleshooting"
        )
        return

        try:
            if not self.cache_manager:
                logger.warning(
                    "Cache manager not available, skipping disease cache update"
                )
                return

            logger.info("Starting disease cache update...")

            # Fetch fresh disease list from MONDO
            disease_list = await self.fetch_mondo_disease_list()

            # Cache the full disease list (no query filter)
            cache_key = "disease_names_all_1000"
            await cache_set(cache_key, disease_list, ttl_seconds=7200)  # 2 hours TTL

            self.last_update = datetime.now()
            logger.info(
                f"Disease cache updated successfully with {len(disease_list)} diseases at {self.last_update}"
            )

            # Populate disease aliases from the cached data
            try:
                from src.services.disease_alias_service import populate_disease_aliases

                alias_count = await populate_disease_aliases()
                logger.info(
                    f"✅ Populated {alias_count} disease aliases for improved search"
                )
            except Exception as alias_error:
                logger.warning(f"Failed to populate disease aliases: {alias_error}")
                # Don't fail the entire update if alias population fails

        except Exception as e:
            logger.error(f"Error updating disease cache: {e}")

    async def run_background_updates(self):
        """
        Background task that updates disease cache hourly.
        """
        logger.info(
            f"Starting background disease cache updates with {self.update_interval_seconds/3600}h interval"
        )

        # Skip initial update to prevent blocking startup - will update on first interval
        logger.info("Skipping initial disease cache update - will run on schedule")

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
            "network_warning": self.last_fetch_source in ["database", "hardcoded"],
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
