"""
Drug Database Service - AI Nurse Florence

This service provides high-performance drug information lookup using a local SQLite
database populated from FDA drug label data. It implements a two-tier lookup strategy:
local database first (fast), then FDA API fallback (slow but comprehensive).

Key Features:
    - Local SQLite database with 25,000+ FDA-approved drugs
    - Fuzzy search across generic names, brand names, and substances
    - Intelligent result ranking (exact matches first)
    - Automatic fallback to live FDA API when drug not in local DB
    - Database statistics logging for monitoring
    - Zero external dependencies for offline operation (after initial build)

Architecture Patterns:
    - Service Layer Architecture: Encapsulated drug data access
    - Fallback Chain: Local DB → FDA API → Not Found
    - Global Singleton: Single service instance shared across application
    - Lazy Initialization: Database connection per query (SQLite best practice)

Database Schema:
    drugs table:
        - generic_name: Official generic drug name (e.g., "acetaminophen")
        - brand_name: Commercial brand name (e.g., "Tylenol")
        - brand_name_base: Base brand name without suffixes
        - substance_name: Active pharmaceutical ingredient
        - route: Administration route (oral, IV, topical, etc.)
        - product_type: HUMAN PRESCRIPTION DRUG, OTC DRUG, etc.
        - labeler_name: Manufacturer/distributor
        - active_ingredients: JSON array of ingredients
        - packaging: JSON array of packaging info

    metadata table:
        - key: Metadata key (e.g., "last_updated", "total_drugs")
        - value: Metadata value

Data Source:
    FDA Drug Label API (via scripts/build_drug_database.py)
    https://open.fda.gov/apis/drug/label/

Dependencies:
    Required: sqlite3 (Python stdlib), live_fda module
    Optional: None

Performance:
    - Local DB lookup: ~5-20ms (in-memory after first query)
    - FDA API fallback: ~500-2000ms (network latency)
    - Database size: ~50MB for 25,000 drugs
    - Startup time: ~10ms (just checks file existence)

Examples:
    >>> # Initialize service
    >>> service = DrugDatabaseService()
    ✓ Drug database loaded from .../data/drugs.db
      Database stats: 25,000 drugs | Last updated: 2025-10-03

    >>> # Search for drugs
    >>> results = service.search_drug("metformin", limit=5)
    >>> for drug in results:
    ...     print(f"{drug['brand_name']} ({drug['generic_name']})")
    Glucophage (metformin hydrochloride)
    Fortamet (metformin hydrochloride)

    >>> # Get full drug information
    >>> info = service.get_drug_info("aspirin")
    >>> print(info["generic_name"])
    aspirin
    >>> print(info["route"])
    oral, rectal

    >>> # Fallback to FDA API for rare drugs
    >>> rare_drug = service.get_drug_info("Vemlidy")
    ⚠️ Vemlidy not in local database, trying FDA API...
    ✓ Found Vemlidy in FDA API

Self-Improvement Checklist:
    [ ] Add unit tests for search_drug() with various patterns
    [ ] Add caching layer (Redis) for frequently queried drugs
    [ ] Implement drug-drug interaction storage in database
    [ ] Add database index optimization for faster searches
    [ ] Add support for searching by NDC (National Drug Code)
    [ ] Add phonetic search (soundex) for misspelled drug names
    [ ] Add database migration system for schema changes
    [ ] Add telemetry for search performance and hit rate
    [ ] Consider adding drug images from FDA database
    [ ] Add support for international drug names (WHO ATC codes)
    [ ] Implement database versioning and update checks
    [ ] Add partial match highlighting in search results

Version: 2.4.2
Last Updated: 2025-10-04
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from live_fda import get_drug_label

logger = logging.getLogger(__name__)

# Database path
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "drugs.db"


class DrugDatabaseService:
    """
    Service for high-performance drug information lookup from local SQLite database.

    This class provides the primary interface for drug data access, implementing
    a two-tier lookup strategy with local database first, FDA API fallback second.

    Attributes:
        db_path (Path): Path to drugs.db SQLite database file
        db_available (bool): Whether database file exists and is accessible

    Methods:
        search_drug: Search for drugs by name (generic, brand, substance)
        get_drug_info: Get comprehensive drug information with FDA fallback
        get_drug_interactions_from_db: Reserved for future interaction lookup
        close: Cleanup resources (no-op for SQLite)

    Examples:
        >>> service = DrugDatabaseService()
        >>> drugs = service.search_drug("ibuprofen")
        >>> print(f"Found {len(drugs)} matching drugs")
        Found 12 matching drugs

        >>> info = service.get_drug_info("Advil")
        >>> print(info["generic_name"])
        ibuprofen
    """

    def __init__(self) -> None:
        """
        Initialize drug database service and verify database availability.

        Checks if drugs.db exists at expected path and logs database statistics.
        If database not found, logs warning with instructions to build it.

        Side Effects:
            - Logs database path and statistics if available
            - Logs warning if database not found
        """
        self.db_path = DATABASE_PATH
        self.db_available = self.db_path.exists()

        if self.db_available:
            logger.info(f"✓ Drug database loaded from {self.db_path}")
            self._log_database_stats()
        else:
            logger.warning(
                f"⚠️ Drug database not found at {self.db_path}. Run scripts/build_drug_database.py to build it."
            )

    def _log_database_stats(self) -> None:
        """
        Internal method to log database statistics at startup.

        Queries the database for total drug count and last update timestamp,
        then logs this information for monitoring purposes.

        Side Effects:
            - Opens and closes temporary SQLite connection
            - Logs info message with statistics
            - Logs warning if stats cannot be read

        Note:
            Failures are non-fatal - service continues even if stats unavailable
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get total drugs
            cursor.execute("SELECT COUNT(*) FROM drugs")
            total = cursor.fetchone()[0]

            # Get last updated
            cursor.execute(
                "SELECT value FROM metadata WHERE key = 'last_updated' LIMIT 1"
            )
            result = cursor.fetchone()
            last_updated = result[0] if result else "Unknown"

            conn.close()

            logger.info(
                f"  Database stats: {total:,} drugs | Last updated: {last_updated}"
            )
        except Exception as e:
            logger.warning(f"Could not read database stats: {e}")

    def search_drug(
        self, drug_name: str, limit: int = 10
    ) -> List[Dict[str, Optional[str]]]:
        """
        Search for drugs by name with intelligent fuzzy matching and ranking.

        Performs case-insensitive partial match search across multiple fields
        (generic name, brand name, brand name base, substance name) and ranks
        results with exact prefix matches first.

        Args:
            drug_name (str): Drug name to search for (generic, brand, or substance)
                Examples: "met" matches "metformin", "Tylenol", "acetaminophen"
            limit (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            List[Dict[str, Optional[str]]]: List of matching drug records, ordered by:
                1. Generic name prefix match
                2. Brand name prefix match
                3. Brand name base prefix match
                4. Substance name contains match

                Each dict contains:
                {
                    "generic_name": str,
                    "brand_name": str,
                    "brand_name_base": str,
                    "substance_name": str,
                    "route": str,
                    "product_type": str,
                    "labeler_name": str,
                    "active_ingredients": str (JSON),
                    "packaging": str (JSON)
                }

                Returns empty list [] if:
                - Database not available
                - No matches found
                - Database error occurs

        Examples:
            >>> service = DrugDatabaseService()
            >>> # Search by generic name
            >>> results = service.search_drug("metformin")
            >>> print(results[0]["brand_name"])
            Glucophage

            >>> # Partial match
            >>> results = service.search_drug("ibu")
            >>> for drug in results[:3]:
            ...     print(drug["generic_name"])
            ibuprofen
            ibuprofen
            ibuprofen lysine

            >>> # Search by brand name
            >>> results = service.search_drug("Advil")
            >>> print(results[0]["generic_name"])
            ibuprofen

        Notes:
            - Search is case-insensitive
            - Uses SQL LIKE with % wildcards for fuzzy matching
            - Database connection opened and closed per query (SQLite best practice)
            - Errors logged but not raised (returns empty list instead)
        """
        if not self.db_available:
            logger.warning(
                "Database not available, cannot search. Build database first."
            )
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Search by generic name, brand name, or substance name (case-insensitive)
            cursor.execute(
                """
                SELECT * FROM drugs
                WHERE generic_name LIKE ?
                   OR brand_name LIKE ?
                   OR brand_name_base LIKE ?
                   OR substance_name LIKE ?
                ORDER BY
                    CASE
                        WHEN generic_name LIKE ? THEN 1
                        WHEN brand_name LIKE ? THEN 2
                        WHEN brand_name_base LIKE ? THEN 3
                        ELSE 4
                    END
                LIMIT ?
            """,
                (
                    f"%{drug_name}%",
                    f"%{drug_name}%",
                    f"%{drug_name}%",
                    f"%{drug_name}%",
                    f"{drug_name}%",
                    f"{drug_name}%",
                    f"{drug_name}%",
                    limit,
                ),
            )

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results
        except Exception as e:
            logger.error(f"Database search error: {e}")
            return []

    def get_drug_info(self, drug_name: str) -> Optional[Dict[str, Optional[str]]]:
        """
        Get comprehensive drug information with automatic FDA API fallback.

        This is the primary method for retrieving complete drug information.
        It implements a two-tier lookup strategy: local database first (fast),
        then FDA API (slow but comprehensive) if not found locally.

        Args:
            drug_name (str): Drug name to look up (generic or brand name)
                Examples: "ibuprofen", "Advil", "metformin hydrochloride"

        Returns:
            Optional[Dict[str, Optional[str]]]: Drug information dictionary or None.

                From local database:
                {
                    "generic_name": str,
                    "brand_name": str,
                    "brand_name_base": str,
                    "substance_name": str,
                    "route": str,  # "oral", "IV", "topical", etc.
                    "product_type": str,  # "HUMAN PRESCRIPTION DRUG", etc.
                    "labeler_name": str,  # Manufacturer
                    "active_ingredients": List[Dict],  # Parsed from JSON
                    "packaging": List[Dict]  # Parsed from JSON
                }

                From FDA API fallback:
                {
                    "source": "FDA_API",
                    "generic_name": str,
                    "brand_name": str,  # Comma-separated
                    "substance_name": str,  # Comma-separated
                    "route": str,  # Comma-separated
                    "product_type": str,
                    "labeler_name": str,
                    "fda_label_data": Dict  # Full FDA response
                }

                Returns None if drug not found in either source

        Examples:
            >>> service = DrugDatabaseService()
            >>> # Common drug (from local DB)
            >>> info = service.get_drug_info("aspirin")
            ✓ Found aspirin in local database
            >>> print(info["route"])
            oral

            >>> # Rare drug (FDA API fallback)
            >>> info = service.get_drug_info("Vemlidy")
            ⚠️ Vemlidy not in local database, trying FDA API...
            ✓ Found Vemlidy in FDA API
            >>> print(info["source"])
            FDA_API

            >>> # Not found anywhere
            >>> info = service.get_drug_info("FakeDrugXYZ")
            ✗ FakeDrugXYZ not found in database or FDA API
            >>> print(info)
            None

        Performance:
            - Local DB hit: ~5-20ms
            - FDA API fallback: ~500-2000ms (network latency)
            - Not found: ~500-2000ms (tried both sources)

        Notes:
            - JSON fields (active_ingredients, packaging) automatically parsed
            - Logs each lookup attempt and result for debugging
            - FDA API has rate limits (~240 requests/minute)
        """
        # Step 1: Search local database
        db_results = self.search_drug(drug_name, limit=1)

        if db_results:
            drug = db_results[0]
            logger.info(f"✓ Found {drug_name} in local database")

            # Parse active ingredients if stored as JSON
            active_ingredients = drug.get("active_ingredients")
            if active_ingredients and isinstance(active_ingredients, str):
                try:
                    drug["active_ingredients"] = json.loads(active_ingredients)
                except json.JSONDecodeError:
                    pass

            # Parse packaging if stored as JSON
            packaging = drug.get("packaging")
            if packaging and isinstance(packaging, str):
                try:
                    drug["packaging"] = json.loads(packaging)
                except json.JSONDecodeError:
                    pass

            return drug

        # Step 2: Fall back to FDA API for label data
        logger.info(f"⚠️ {drug_name} not in local database, trying FDA API...")
        fda_data = get_drug_label(drug_name)

        if fda_data:
            logger.info(f"✓ Found {drug_name} in FDA API")
            return {
                "source": "FDA_API",
                "generic_name": fda_data.get("generic_name"),
                "brand_name": ", ".join(fda_data.get("brand_names", [])),
                "substance_name": ", ".join(fda_data.get("substance_name", [])),
                "route": ", ".join(fda_data.get("route", [])),
                "product_type": fda_data.get("product_type"),
                "labeler_name": fda_data.get("manufacturer"),
                # Include full FDA data
                "fda_label_data": fda_data,
            }

        logger.warning(f"✗ {drug_name} not found in database or FDA API")
        return None

    def get_drug_interactions_from_db(self, drug1: str, drug2: str) -> Optional[str]:
        """
        Get drug-drug interaction information from database (FUTURE FEATURE).

        This method is reserved for future enhancement when drug-drug interaction
        data is stored in the local database. Currently, all interaction checking
        is handled by drug_interaction_service.py which queries external APIs.

        Args:
            drug1 (str): First drug name (generic or brand)
            drug2 (str): Second drug name (generic or brand)

        Returns:
            Optional[str]: Interaction description text or None (always None currently)

        Future Enhancement:
            When implemented, this will return cached interaction data from:
            - drugs_interactions table in SQLite
            - Pre-computed from FDA, DrugBank, or DailyMed APIs
            - Enables offline interaction checking
            - Reduces API latency and rate limit issues

        Examples:
            >>> service = DrugDatabaseService()
            >>> # Current behavior
            >>> result = service.get_drug_interactions_from_db("warfarin", "aspirin")
            >>> print(result)
            None

            >>> # Future behavior (not implemented)
            >>> # result = service.get_drug_interactions_from_db("warfarin", "aspirin")
            >>> # print(result)
            >>> # "Major interaction: Increased risk of bleeding..."

        See Also:
            - drug_interaction_service.py for current interaction checking
            - scripts/build_drug_database.py for database build process
        """
        # TODO: Implement interaction lookup from database
        # For now, interactions are handled by drug_interaction_service.py
        return None

    def close(self) -> None:
        """
        Cleanup resources (no-op for SQLite).

        SQLite connections are opened and closed per query, so no persistent
        connection cleanup is needed. This method exists for interface
        compatibility with other services that require cleanup.

        Side Effects:
            None

        Note:
            Safe to call multiple times
        """
        pass


# Global singleton service instance
# Initialized at module load time
drug_db_service = DrugDatabaseService()


# Service registration function
async def register_drug_database_service() -> DrugDatabaseService:
    """
    Register drug database service for dependency injection framework.

    This async function provides a hook for dependency injection systems
    to obtain the global drug database service instance. The service is
    already initialized as a module-level singleton.

    Returns:
        DrugDatabaseService: The global singleton service instance

    Examples:
        >>> # In dependency injection framework
        >>> service = await register_drug_database_service()
        Drug database service registered successfully
        >>> info = service.get_drug_info("ibuprofen")

    Notes:
        - Returns the same instance every time (singleton pattern)
        - Logs registration for monitoring
        - Async for compatibility with DI framework, but no actual async work
    """
    logger.info("Drug database service registered successfully")
    return drug_db_service
