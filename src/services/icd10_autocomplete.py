"""
ICD-10 Autocomplete Service
Provides fast autocomplete for 74,000+ ICD-10 diagnosis codes
"""

import logging
import os
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


def simplify_diagnosis_name(description: str) -> str:
    """
    Simplify ICD-10 diagnosis names for patient education.

    Removes medical jargon and technical details:
    - "Type 1 diabetes mellitus without complications" → "Type 1 Diabetes"
    - "Essential (primary) hypertension" → "Essential Hypertension"
    - "Acute myocardial infarction" → "Acute Myocardial Infarction (Heart Attack)"
    """
    simplified = description

    # Remove common suffixes that add medical detail
    removals = [
        ", unspecified",
        " without complications",
        " with complications",
        " unspecified",
        ", unspecified type",
        ", diet controlled",
        ", insulin controlled",
        ", in childbirth",
        ", in pregnancy",
        ", in the puerperium",
        ", uncomplicated",
        " uncomplicated",
    ]

    for removal in removals:
        simplified = simplified.replace(removal, "")

    # Replace "mellitus" with nothing (diabetes mellitus → diabetes)
    simplified = simplified.replace(" mellitus", "")

    # Remove parenthetical details like "(primary)" unless it's a helpful synonym
    simplified = re.sub(r"\s*\([^)]*\)\s*", " ", simplified)

    # Clean up extra spaces
    simplified = re.sub(r"\s+", " ", simplified).strip()

    # Title case for better readability
    simplified = simplified.title()

    return simplified


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

    Prioritizes simpler, shorter descriptions for better UX.

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
    matches = []

    # Search through codes and collect all matches
    for item in _icd10_codes:
        code = item["code"]
        description = item["description"]

        # Match by code or description
        if query_lower in code.lower() or query_lower in description.lower():
            # Calculate a simplicity score (prefer shorter descriptions)
            desc_length = len(description)
            # Bonus for codes ending in 9 or 0 (usually more general)
            is_general = code.endswith("9") or code.endswith("0")
            # Penalty for words like "with", "due to" (usually more specific)
            is_specific = (
                " with " in description.lower() or " due to " in description.lower()
            )

            # Lower score = better (will sort ascending)
            score = desc_length
            if is_general:
                score -= 50  # Prioritize general codes
            if is_specific:
                score += 100  # Deprioritize specific complications

            matches.append({"code": code, "description": description, "score": score})

    # Sort by score (simpler/more general first)
    matches.sort(key=lambda x: x["score"])

    # Return top results with simplified names
    results = []
    for match in matches[:limit]:
        simplified_name = simplify_diagnosis_name(match["description"])
        results.append(
            {
                "id": match["code"],
                "label": f"{simplified_name} ({match['code']})",
                "value": match["code"],
                "icd10_code": match["code"],
            }
        )

    return results


# DON'T pre-load codes - lazy load on first request to avoid startup timeout
# load_icd10_codes()
