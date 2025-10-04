"""
FDA OpenFDA API connector for drug label and interaction information.

API Documentation: https://open.fda.gov/apis/drug/label/
"""

import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.fda.gov/drug"


def get_drug_label(drug_name: str) -> Optional[Dict[str, Any]]:
    """
    Get FDA drug label information for a specific drug.

    Args:
        drug_name: Drug name (generic or brand name)

    Returns:
        Dict containing FDA drug label fields
    """
    try:
        # Search for drug by brand or generic name
        response = requests.get(
            f"{BASE_URL}/label.json",
            params={
                "search": f'openfda.brand_name:"{drug_name}" openfda.generic_name:"{drug_name}"',
                "limit": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            logger.info(f"No FDA label found for drug: {drug_name}")
            return None

        result = data["results"][0]
        openfda = result.get("openfda", {})

        # Extract key FDA label sections
        label_data = {
            "drug_name": drug_name,
            "generic_name": openfda.get("generic_name", [None])[0],
            "brand_names": openfda.get("brand_name", []),
            "manufacturer": openfda.get("manufacturer_name", [None])[0],
            "product_type": openfda.get("product_type", [None])[0],
            "route": openfda.get("route", []),
            "substance_name": openfda.get("substance_name", []),
            # Clinical information from label
            "indications_and_usage": result.get("indications_and_usage", [None])[0],
            "dosage_and_administration": result.get(
                "dosage_and_administration", [None]
            )[0],
            "contraindications": result.get("contraindications", [None])[0],
            "warnings_and_cautions": result.get("warnings_and_cautions", [None])[0],
            "boxed_warning": result.get("boxed_warning", [None])[0],
            "adverse_reactions": result.get("adverse_reactions", [None])[0],
            "drug_interactions": result.get("drug_interactions", [None])[0],
            # Additional clinical sections
            "use_in_specific_populations": result.get(
                "use_in_specific_populations", [None]
            )[0],
            "pregnancy": result.get("pregnancy", [None])[0],
            "nursing_mothers": result.get("nursing_mothers", [None])[0],
            "pediatric_use": result.get("pediatric_use", [None])[0],
            "geriatric_use": result.get("geriatric_use", [None])[0],
            # Pharmacology
            "clinical_pharmacology": result.get("clinical_pharmacology", [None])[0],
            "mechanism_of_action": result.get("mechanism_of_action", [None])[0],
            "pharmacokinetics": result.get("pharmacokinetics", [None])[0],
            # Storage and handling
            "storage_and_handling": result.get("storage_and_handling", [None])[0],
            # Metadata
            "effective_time": result.get("effective_time"),
            "spl_id": result.get("spl_id"),
        }

        return label_data

    except requests.exceptions.RequestException as e:
        logger.error(f"FDA API request error for {drug_name}: {e}")
        return None
    except Exception as e:
        logger.error(f"FDA API error for {drug_name}: {e}")
        return None


def search_drug_interactions(drug_name: str) -> List[str]:
    """
    Extract drug interactions from FDA label data.

    Args:
        drug_name: Drug name to search for

    Returns:
        List of drug interaction warnings
    """
    label_data = get_drug_label(drug_name)
    if not label_data:
        return []

    interactions_text = label_data.get("drug_interactions")
    if not interactions_text:
        return []

    # Simple extraction - in production would use NLP to parse structured data
    # For now, return the full text split by common delimiters
    interactions = []
    for line in interactions_text.split("\n"):
        line = line.strip()
        if line and len(line) > 10:  # Filter out very short lines
            interactions.append(line)

    return interactions[:10]  # Return top 10 interactions


def get_nursing_considerations(drug_name: str) -> Dict[str, Any]:
    """
    Extract nursing-relevant information from FDA label.

    Args:
        drug_name: Drug name

    Returns:
        Dict with nursing considerations
    """
    label_data = get_drug_label(drug_name)
    if not label_data:
        return {}

    return {
        "drug_name": drug_name,
        "administration": label_data.get("dosage_and_administration"),
        "contraindications": label_data.get("contraindications"),
        "warnings": label_data.get("warnings_and_cautions"),
        "boxed_warning": label_data.get("boxed_warning"),
        "adverse_reactions": label_data.get("adverse_reactions"),
        "special_populations": {
            "pregnancy": label_data.get("pregnancy"),
            "nursing_mothers": label_data.get("nursing_mothers"),
            "pediatric": label_data.get("pediatric_use"),
            "geriatric": label_data.get("geriatric_use"),
        },
        "storage": label_data.get("storage_and_handling"),
    }


def get_boxed_warnings(drug_name: str) -> Optional[str]:
    """
    Get FDA black box warning (most serious warning) for a drug.

    Args:
        drug_name: Drug name

    Returns:
        Black box warning text if present
    """
    label_data = get_drug_label(drug_name)
    if not label_data:
        return None

    return label_data.get("boxed_warning")
