"""
FDA OpenFDA Drug Information Service
Integrates with FDA OpenFDA API for drug information and interactions
Following Service Layer Architecture
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from src.utils.config import get_settings
from src.utils.redis_cache import cached

logger = logging.getLogger(__name__)


class FDADrugService:
    """
    FDA OpenFDA API integration for drug information
    Following Service Layer Architecture from coding instructions
    """

    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.fda.gov/drug"
        self.timeout = 10.0  # 10 second timeout
        self.edu_banner = "Educational use only — not medical advice. No PHI stored."

    @cached(ttl_seconds=86400)  # 24 hour cache for drug label data
    async def get_drug_label(
        self, drug_name: str, limit: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch drug label information from FDA OpenFDA API

        Args:
            drug_name: Brand or generic drug name
            limit: Maximum number of results to return

        Returns:
            Dict with drug label information or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Search drug labels by name
                url = f"{self.base_url}/label.json"
                params = {
                    "search": f'openfda.brand_name:"{drug_name}" openfda.generic_name:"{drug_name}"',
                    "limit": limit,
                }

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "results" in data and len(data["results"]) > 0:
                    return data["results"][0]

                logger.info(f"No FDA label data found for drug: {drug_name}")
                return None

        except httpx.HTTPError as e:
            logger.error(f"FDA API HTTP error for {drug_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"FDA API error for {drug_name}: {e}")
            return None

    @cached(ttl_seconds=86400)  # 24 hour cache
    async def get_drug_interactions(self, drug_name: str) -> Optional[List[str]]:
        """
        Extract drug interaction information from FDA label

        Args:
            drug_name: Brand or generic drug name

        Returns:
            List of drug interaction warnings or None
        """
        try:
            label_data = await self.get_drug_label(drug_name)

            if not label_data:
                return None

            # Extract drug interactions from various possible fields
            interactions = []

            # Check drug_interactions field
            if "drug_interactions" in label_data:
                drug_int = label_data["drug_interactions"]
                if isinstance(drug_int, list):
                    interactions.extend(drug_int)
                elif isinstance(drug_int, str):
                    interactions.append(drug_int)

            # Check precautions field
            if "precautions" in label_data:
                precautions = label_data["precautions"]
                if isinstance(precautions, list):
                    interactions.extend(precautions)
                elif isinstance(precautions, str):
                    interactions.append(precautions)

            return interactions if interactions else None

        except Exception as e:
            logger.error(f"Error extracting interactions for {drug_name}: {e}")
            return None

    @cached(ttl_seconds=86400)  # 24 hour cache
    async def get_drug_adverse_events(
        self, drug_name: str, limit: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch adverse event reports from FDA FAERS database

        Args:
            drug_name: Drug name to query
            limit: Maximum number of results

        Returns:
            Dict with adverse event statistics or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/event.json"
                params = {
                    "search": f'patient.drug.openfda.brand_name:"{drug_name}" patient.drug.openfda.generic_name:"{drug_name}"',
                    "count": "patient.reaction.reactionmeddrapt.exact",
                    "limit": limit,
                }

                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                if "results" in data:
                    return {
                        "drug_name": drug_name,
                        "total_reports": len(data["results"]),
                        "top_reactions": data["results"],
                    }

                return None

        except httpx.HTTPError as e:
            logger.error(f"FDA adverse events HTTP error for {drug_name}: {e}")
            return None
        except Exception as e:
            logger.error(f"FDA adverse events error for {drug_name}: {e}")
            return None

    async def get_medication_guide_data(self, drug_name: str) -> Dict[str, Any]:
        """
        Comprehensive drug information for medication guides

        Args:
            drug_name: Drug name

        Returns:
            Dict with structured drug information
        """
        label_data = await self.get_drug_label(drug_name)
        interactions = await self.get_drug_interactions(drug_name)

        if not label_data:
            return {
                "banner": self.edu_banner,
                "drug_name": drug_name,
                "data_available": False,
                "message": f"No FDA data available for {drug_name}",
            }

        # Extract key information from label
        purpose = None
        if "purpose" in label_data:
            purpose = (
                label_data["purpose"][0]
                if isinstance(label_data["purpose"], list)
                else label_data["purpose"]
            )
        elif "indications_and_usage" in label_data:
            purpose = (
                label_data["indications_and_usage"][0]
                if isinstance(label_data["indications_and_usage"], list)
                else label_data["indications_and_usage"]
            )

        warnings = None
        if "warnings" in label_data:
            warnings = (
                label_data["warnings"]
                if isinstance(label_data["warnings"], list)
                else [label_data["warnings"]]
            )

        dosage = None
        if "dosage_and_administration" in label_data:
            dosage = (
                label_data["dosage_and_administration"][0]
                if isinstance(label_data["dosage_and_administration"], list)
                else label_data["dosage_and_administration"]
            )

        side_effects = None
        if "adverse_reactions" in label_data:
            side_effects = (
                label_data["adverse_reactions"]
                if isinstance(label_data["adverse_reactions"], list)
                else [label_data["adverse_reactions"]]
            )

        storage = None
        if "storage_and_handling" in label_data:
            storage = (
                label_data["storage_and_handling"][0]
                if isinstance(label_data["storage_and_handling"], list)
                else label_data["storage_and_handling"]
            )

        return {
            "banner": self.edu_banner,
            "drug_name": drug_name,
            "data_available": True,
            "purpose": purpose,
            "warnings": warnings,
            "dosage_information": dosage,
            "side_effects": side_effects,
            "drug_interactions": interactions,
            "storage_instructions": storage,
            "data_source": "FDA OpenFDA API",
            "openfda_data": label_data.get("openfda", {}),
        }


def get_fda_drug_service() -> FDADrugService:
    """Dependency injection for FDA drug service"""
    return FDADrugService()
