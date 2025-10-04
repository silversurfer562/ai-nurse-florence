"""
Drug Database Service - AI Nurse Florence

Provides fast drug lookups from local SQLite database built from FDA data.
Falls back to FDA API if drug not found in local database.
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
    """Service for looking up drug information from local database."""

    def __init__(self):
        self.db_path = DATABASE_PATH
        self.db_available = self.db_path.exists()

        if self.db_available:
            logger.info(f"✓ Drug database loaded from {self.db_path}")
            self._log_database_stats()
        else:
            logger.warning(
                f"⚠️ Drug database not found at {self.db_path}. Run scripts/build_drug_database.py to build it."
            )

    def _log_database_stats(self):
        """Log database statistics."""
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
        Search for drugs by name (generic or brand).

        Args:
            drug_name: Drug name to search for
            limit: Maximum number of results

        Returns:
            List of matching drug records
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
        Get comprehensive drug information.
        First checks local database, then falls back to FDA API.

        Args:
            drug_name: Drug name (generic or brand)

        Returns:
            Drug information dict or None if not found
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
        Get drug-drug interaction information from database.
        Currently returns None - interaction checking is handled by
        the drug_interaction_service.

        Future enhancement: Store known interactions in database.

        Args:
            drug1: First drug name
            drug2: Second drug name

        Returns:
            Interaction description or None
        """
        # TODO: Implement interaction lookup from database
        # For now, interactions are handled by drug_interaction_service.py
        return None

    def close(self):
        """Cleanup resources (nothing to cleanup for SQLite)."""
        pass


# Global service instance
drug_db_service = DrugDatabaseService()


# Service registration function
async def register_drug_database_service():
    """Register drug database service for dependency injection."""
    logger.info("Drug database service registered successfully")
    return drug_db_service
