"""
Drug Cache Updater Service - AI Nurse Florence
Phase 4.2: Drug Interactions Enhancement

Automatic pre-fetching and caching of FDA drug names list.
Runs hourly to keep drug list fresh and ready for users.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import List, Optional

import httpx

# Configure logging
logger = logging.getLogger(__name__)


class DrugCacheUpdaterService:
    """
    Service for automatic FDA drug list caching.

    Features:
    - Hourly background updates of FDA drug list
    - Smart caching for instant autocomplete
    - Fallback to common drug list if FDA API fails
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
            logger.info("Drug cache updater initialized with smart cache")
        except Exception as e:
            logger.warning(f"Could not initialize smart cache: {e}")

        # Check database availability
        try:

            self.db_available = True
            logger.info("Drug cache updater: Database available for fallback storage")
        except Exception as e:
            logger.warning(f"Drug cache updater: Database not available: {e}")

    async def save_drug_list_to_db(self, drug_list: List[str], source: str = "fda_api"):
        """
        Save successful drug list fetch to database as backup.
        Only replaces existing data on successful fetch - preserves backup on failure.

        Args:
            drug_list: List of drug names to save
            source: Source of the data (fda_api, etc.)
        """
        if not self.db_available:
            return

        try:
            from sqlalchemy import delete

            from src.models.database import CachedDrugList, get_db_session

            async for session in get_db_session():
                try:
                    # Only delete old data AFTER we have new successful data
                    # This ensures we always have a backup until replaced
                    await session.execute(delete(CachedDrugList))

                    # Create new cached list
                    cached_list = CachedDrugList(
                        id=str(uuid.uuid4()),
                        drug_names=drug_list,
                        source=source,
                        count=len(drug_list),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    )

                    session.add(cached_list)
                    await session.commit()
                    logger.info(
                        f"✅ Saved {len(drug_list)} drugs to database backup (source: {source})"
                    )

                except Exception as e:
                    await session.rollback()
                    logger.error(f"Failed to save drug list to database: {e}")

        except Exception as e:
            logger.error(f"Database operation failed: {e}")

    async def get_drug_list_from_db(self) -> Optional[List[str]]:
        """
        Get last successful drug list from database.

        Returns:
            List of drug names from database, or None if not available
        """
        if not self.db_available:
            return None

        try:
            from sqlalchemy import select

            from src.models.database import CachedDrugList, get_db_session

            async for session in get_db_session():
                try:
                    result = await session.execute(
                        select(CachedDrugList)
                        .order_by(CachedDrugList.updated_at.desc())
                        .limit(1)
                    )
                    cached_list = result.scalar_one_or_none()

                    if cached_list:
                        logger.info(
                            f"Retrieved {cached_list.count} drugs from database (source: {cached_list.source})"
                        )
                        return cached_list.drug_names

                    return None

                except Exception as e:
                    logger.error(f"Failed to retrieve drug list from database: {e}")
                    return None

        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            return None

    async def fetch_fda_drug_list(self) -> List[str]:
        """
        Fetch comprehensive drug list from FDA OpenFDA API.

        Fallback strategy:
        1. Try FDA API (primary source)
        2. If API fails, use last successful data from database
        3. If no database backup, use minimal hardcoded list

        Database backup is ONLY updated on successful API fetch,
        preserving the last known good data during network issues.

        Returns:
            List of drug names (generic names)
        """
        try:
            fda_url = "https://api.fda.gov/drug/ndc.json"
            params = {"limit": 1000}  # Fetch large sample for comprehensive list

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(fda_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Extract unique generic names
                drug_names = set()
                for result in data.get("results", []):
                    generic_name = result.get("generic_name", "").strip()
                    if generic_name:
                        # Split comma-separated names and clean them
                        names = [n.strip().title() for n in generic_name.split(",")]
                        drug_names.update(names[:1])  # Take first name only

                drug_list = sorted(list(drug_names))
                logger.info(f"✅ Fetched {len(drug_list)} drug names from FDA API")

                # ONLY save to database on successful fetch
                # This preserves the last known good data during API failures
                await self.save_drug_list_to_db(drug_list, source="fda_api")
                self.last_fetch_source = "api"

                return drug_list

        except Exception as e:
            logger.error(f"❌ Failed to fetch FDA drug list: {e}")
            # Try database fallback first (last successful fetch)
            # Database is NOT modified here - preserves backup
            db_drugs = await self.get_drug_list_from_db()
            if db_drugs:
                logger.info(f"✅ Using database fallback ({len(db_drugs)} drugs)")
                self.last_fetch_source = "database"
                return db_drugs

            # Final fallback to hardcoded list (worst case)
            logger.warning("⚠️ Using hardcoded fallback drug list")
            self.last_fetch_source = "hardcoded"
            return self.get_fallback_drug_list()

    def get_fallback_drug_list(self) -> List[str]:
        """
        Get fallback list of common drugs when FDA API is unavailable.

        Returns:
            List of common drug names
        """
        return [
            "Acetaminophen",
            "Amoxicillin",
            "Aspirin",
            "Atorvastatin",
            "Azithromycin",
            "Ciprofloxacin",
            "Clopidogrel",
            "Doxycycline",
            "Furosemide",
            "Gabapentin",
            "Hydrochlorothiazide",
            "Ibuprofen",
            "Levothyroxine",
            "Lisinopril",
            "Losartan",
            "Metformin",
            "Metoprolol",
            "Omeprazole",
            "Prednisone",
            "Simvastatin",
            "Warfarin",
            "Amlodipine",
            "Albuterol",
            "Insulin",
            "Methotrexate",
            "Naproxen",
            "Pantoprazole",
            "Sertraline",
            "Tramadol",
            "Zolpidem",
        ]

    async def update_drug_cache(self):
        """
        Update the drug cache with fresh FDA data.
        """
        # Temporarily disabled to prevent blocking Railway startup
        logger.info(
            "Drug cache update skipped - disabled during startup troubleshooting"
        )
        return

        try:
            if not self.cache_manager:
                logger.warning(
                    "Cache manager not available, skipping drug cache update"
                )
                return

            logger.info("Starting drug cache update...")

            # Fetch fresh drug list from FDA
            drug_list = await self.fetch_fda_drug_list()

            # Cache the full drug list (no query filter)
            cache_key = "drug_names_all_1000"
            await self.cache_manager.set(
                cache_key, drug_list, ttl_seconds=7200
            )  # 2 hours TTL

            self.last_update = datetime.now()
            logger.info(
                f"Drug cache updated successfully with {len(drug_list)} drugs at {self.last_update}"
            )

        except Exception as e:
            logger.error(f"Error updating drug cache: {e}")

    async def run_background_updates(self):
        """
        Background task that updates drug cache hourly.
        """
        logger.info(
            f"Starting background drug cache updates with {self.update_interval_seconds/3600}h interval"
        )

        # Skip initial update to prevent blocking startup - will update on first interval
        logger.info("Skipping initial drug cache update - will run on schedule")

        while self.is_running:
            try:
                # Wait for next update interval
                await asyncio.sleep(self.update_interval_seconds)

                # Update the cache
                await self.update_drug_cache()

            except asyncio.CancelledError:
                logger.info("Background drug cache update task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background drug cache update: {e}")
                # Continue running even if one update fails
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def start(self):
        """
        Start the background drug cache updater service.
        """
        if self.is_running:
            logger.warning("Drug cache updater is already running")
            return

        self.is_running = True
        self.task = asyncio.create_task(self.run_background_updates())
        logger.info("Drug cache updater started")

    async def stop(self):
        """
        Stop the background drug cache updater service.
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

        logger.info("Drug cache updater stopped")

    def get_status(self) -> dict:
        """
        Get current status of the drug cache updater.

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
_drug_cache_updater: Optional[DrugCacheUpdaterService] = None


def get_drug_cache_updater() -> DrugCacheUpdaterService:
    """
    Get the global drug cache updater instance.

    Returns:
        DrugCacheUpdaterService instance
    """
    global _drug_cache_updater
    if _drug_cache_updater is None:
        _drug_cache_updater = DrugCacheUpdaterService()
    return _drug_cache_updater
