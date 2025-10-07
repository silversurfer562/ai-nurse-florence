"""
ICD-10 Autocomplete Service
Provides fast autocomplete for 74,000+ ICD-10 diagnosis codes
"""

import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

# Global cache for ICD-10 codes
_icd10_codes: List[Dict[str, str]] = []
_loaded = False


def load_icd10_codes() -> None:
    """Load ICD-10 codes from data file into memory (one-time load)."""
    global _icd10_codes, _loaded

    if _loaded:
        return

    try:
        # Path to ICD-10 data file
        # __file__ is /app/src/services/icd10_autocomplete.py in production
        # We need to go to /app/data, not /data
        service_dir = os.path.dirname(os.path.abspath(__file__))  # /app/src/services
        src_dir = os.path.dirname(service_dir)  # /app/src
        app_root = os.path.dirname(src_dir)  # /app
        data_path = os.path.join(
            app_root, "data", "icd10_raw", "icd10cm-codes-2025.txt"
        )

        if not os.path.exists(data_path):
            logger.error(
                f"ICD-10 data file not found at {data_path} - "
                f"Current directory: {os.getcwd()}, "
                f"__file__: {__file__}"
            )
            _loaded = True  # Mark as loaded to avoid repeated checks
            return

        logger.info(f"Loading ICD-10 codes from {data_path}...")

        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Split on whitespace (2+ spaces) - format is: "CODE    Description"
                parts = re.split(r"\s{2,}", line, maxsplit=1)
                if len(parts) == 2:
                    code, description = parts
                    _icd10_codes.append(
                        {"code": code.strip(), "description": description.strip()}
                    )

        _loaded = True
        logger.info(f"✅ Loaded {len(_icd10_codes)} ICD-10 codes for autocomplete")

    except Exception as e:
        logger.error(f"Failed to load ICD-10 codes: {e}", exc_info=True)
        _loaded = True  # Mark as loaded to avoid repeated checks


def search_icd10(query: str, limit: int = 10) -> List[Dict[str, str]]:
    """
    Search ICD-10 codes by description or code.

    Args:
        query: Search term (e.g., "diabetes", "E11")
        limit: Maximum results to return

    Returns:
        List of matching diagnoses with id, label, value, icd10_code
    """
    # Ensure codes are loaded
    if not _loaded:
        load_icd10_codes()

    if not _icd10_codes:
        return []

    query_lower = query.lower()
    results = []

    # Search through codes
    for item in _icd10_codes:
        if len(results) >= limit:
            break

        code = item["code"]
        description = item["description"]

        # Match by code or description
        if query_lower in code.lower() or query_lower in description.lower():
            results.append(
                {
                    "id": code,
                    "label": f"{description} ({code})",
                    "value": code,
                    "icd10_code": code,
                }
            )

    return results


# DON'T pre-load codes - lazy load on first request to avoid startup timeout
# load_icd10_codes()
