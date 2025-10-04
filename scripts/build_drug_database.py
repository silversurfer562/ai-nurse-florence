#!/usr/bin/env python3
"""
Build comprehensive drug database from FDA OpenFDA data.

This script downloads the latest FDA NDC (National Drug Code) database
and builds a local SQLite database for fast drug lookups.

Data source: FDA OpenFDA NDC API
License: Public domain (U.S. Government data)
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FDA OpenFDA NDC API
FDA_NDC_API = "https://api.fda.gov/drug/ndc.json"
DATABASE_PATH = Path(__file__).parent.parent / "data" / "drugs.db"


def fetch_fda_drugs(limit: int = 1000, skip: int = 0) -> Dict:
    """
    Fetch drug data from FDA OpenFDA NDC API.

    Args:
        limit: Number of records to fetch (max 1000 per request)
        skip: Number of records to skip (for pagination)

    Returns:
        Dict with FDA response data
    """
    try:
        response = requests.get(
            FDA_NDC_API,
            params={"limit": limit, "skip": skip},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch FDA data: {e}")
        raise


def create_database():
    """Create SQLite database schema for drugs."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Drop existing table if exists
    cursor.execute("DROP TABLE IF EXISTS drugs")

    # Create drugs table
    cursor.execute(
        """
        CREATE TABLE drugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_ndc TEXT UNIQUE NOT NULL,
            generic_name TEXT,
            brand_name TEXT,
            brand_name_base TEXT,
            dosage_form TEXT,
            route TEXT,
            product_type TEXT,
            labeler_name TEXT,
            substance_name TEXT,
            active_ingredients TEXT,
            pharm_class TEXT,
            dea_schedule TEXT,
            marketing_category TEXT,
            application_number TEXT,
            packaging TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create indexes for fast lookups
    cursor.execute(
        "CREATE INDEX idx_generic_name ON drugs(generic_name COLLATE NOCASE)"
    )
    cursor.execute("CREATE INDEX idx_brand_name ON drugs(brand_name COLLATE NOCASE)")
    cursor.execute(
        "CREATE INDEX idx_substance_name ON drugs(substance_name COLLATE NOCASE)"
    )

    # Create metadata table
    cursor.execute(
        """
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()
    logger.info(f"✓ Database created at {DATABASE_PATH}")


def insert_drug(cursor, drug_data: Dict) -> bool:
    """
    Insert drug record into database.

    Args:
        cursor: SQLite cursor
        drug_data: FDA drug data dict

    Returns:
        True if inserted, False if skipped
    """
    try:
        # Extract key fields
        product_ndc = drug_data.get("product_ndc")
        if not product_ndc:
            return False

        # Get openfda data if available
        openfda = drug_data.get("openfda", {})

        # Extract active ingredients
        active_ingredients = drug_data.get("active_ingredients", [])
        active_ingredients_str = (
            json.dumps(active_ingredients) if active_ingredients else None
        )

        # Extract packaging
        packaging = drug_data.get("packaging", [])
        packaging_str = json.dumps(packaging) if packaging else None

        cursor.execute(
            """
            INSERT OR REPLACE INTO drugs (
                product_ndc, generic_name, brand_name, brand_name_base,
                dosage_form, route, product_type, labeler_name,
                substance_name, active_ingredients, pharm_class,
                dea_schedule, marketing_category, application_number,
                packaging, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                product_ndc,
                drug_data.get("generic_name"),
                drug_data.get("brand_name"),
                drug_data.get("brand_name_base"),
                drug_data.get("dosage_form"),
                ",".join(drug_data.get("route", [])),
                drug_data.get("product_type"),
                drug_data.get("labeler_name"),
                ",".join(openfda.get("substance_name", [])),
                active_ingredients_str,
                ",".join(openfda.get("pharm_class", [])),
                drug_data.get("dea_schedule"),
                drug_data.get("marketing_category"),
                drug_data.get("application_number"),
                packaging_str,
                datetime.now().isoformat(),
            ),
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to insert drug {drug_data.get('product_ndc')}: {e}")
        return False


def build_database(max_records: Optional[int] = None):
    """
    Build drug database from FDA OpenFDA data.

    Args:
        max_records: Maximum number of records to fetch (None = all)
    """
    logger.info("Building drug database from FDA OpenFDA...")

    create_database()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    total_inserted = 0
    total_fetched = 0
    skip = 0
    batch_size = 1000

    try:
        while True:
            logger.info(f"Fetching records {skip} to {skip + batch_size}...")

            response = fetch_fda_drugs(limit=batch_size, skip=skip)
            results = response.get("results", [])

            if not results:
                logger.info("No more records to fetch")
                break

            # Insert drugs
            for drug in results:
                if insert_drug(cursor, drug):
                    total_inserted += 1
                total_fetched += 1

            conn.commit()
            logger.info(f"✓ Inserted {total_inserted}/{total_fetched} drugs")

            skip += batch_size

            # Check if we've reached max records
            if max_records and total_fetched >= max_records:
                logger.info(f"Reached max records limit: {max_records}")
                break

            # Check if we've fetched all available records
            meta = response.get("meta", {})
            total_available = meta.get("results", {}).get("total", 0)
            if total_fetched >= total_available:
                logger.info(f"Fetched all {total_available} available records")
                break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error building database: {e}")
        raise
    finally:
        # Update metadata
        cursor.execute(
            """
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            ("total_drugs", str(total_inserted), datetime.now().isoformat()),
        )
        cursor.execute(
            """
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            ("last_updated", datetime.now().isoformat(), datetime.now().isoformat()),
        )
        cursor.execute(
            """
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            ("source", "FDA OpenFDA NDC API", datetime.now().isoformat()),
        )

        conn.commit()
        conn.close()

        logger.info(
            f"✅ Database build complete: {total_inserted} drugs inserted at {DATABASE_PATH}"
        )


def search_drug(drug_name: str) -> List[Dict]:
    """
    Search for drugs by name (generic or brand).

    Args:
        drug_name: Drug name to search for

    Returns:
        List of matching drug records
    """
    if not DATABASE_PATH.exists():
        logger.error("Drug database not found. Run build_database() first.")
        return []

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search by generic name or brand name (case-insensitive)
    cursor.execute(
        """
        SELECT * FROM drugs
        WHERE generic_name LIKE ? OR brand_name LIKE ?
        LIMIT 10
    """,
        (f"%{drug_name}%", f"%{drug_name}%"),
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Build FDA drug database")
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to fetch (default: all)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: fetch only 100 records",
    )

    args = parser.parse_args()

    max_records = 100 if args.test else args.max_records

    build_database(max_records=max_records)

    # Test search
    logger.info("\n--- Testing database search ---")
    test_drugs = ["aspirin", "warfarin", "metformin"]
    for drug in test_drugs:
        results = search_drug(drug)
        logger.info(f"Search '{drug}': {len(results)} results")
        if results:
            logger.info(
                f"  First result: {results[0].get('brand_name')} ({results[0].get('generic_name')})"
            )
