"""
Disease Alias Service - Maps user-friendly terms to canonical MONDO IDs
Enables reliable disease lookups regardless of how users phrase the name.
"""

import logging
import uuid
from typing import List, Optional, Dict, cast
from datetime import datetime
import hashlib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import DiseaseAlias, get_db_session

logger = logging.getLogger(__name__)


class DiseaseAliasService:
    """Service for managing disease name aliases and canonical MONDO ID mappings."""

    @staticmethod
    async def populate_aliases_from_cache():
        """
        Extract aliases from cached disease data and populate the disease_aliases table.
        Reads from CachedDiseaseList and creates mappings for autocomplete and lookup.
        """
        try:
            from src.models.database import CachedDiseaseList

            async for session in get_db_session():
                # Get the latest cached disease list
                result = await session.execute(
                    select(CachedDiseaseList)
                    .order_by(CachedDiseaseList.updated_at.desc())
                    .limit(1)
                )
                cached_list = result.scalars().first()

                if not cached_list:
                    logger.warning("No cached disease list found")
                    return 0

                diseases = cast(List[str], cached_list.disease_names or [])
                alias_count = 0
                skipped_count = 0

                logger.info(f"Processing {len(diseases)} diseases to extract aliases...")

                for disease_name in diseases:
                    # Skip technical/genetic disease names
                    if DiseaseAliasService._should_skip_disease(disease_name):
                        skipped_count += 1
                        continue

                    # Create a stable, short placeholder mondo_id that fits VARCHAR(100)
                    placeholder_mondo_id = DiseaseAliasService._make_placeholder_mondo_id(disease_name)

                    # Create primary alias (the disease name itself)
                    await DiseaseAliasService._create_alias(
                        session=session,
                        alias=disease_name,
                        mondo_id=placeholder_mondo_id,  # Temporary until we link to real MONDO IDs
                        canonical_name=disease_name,
                        alias_type="primary",
                        is_preferred=True,
                        search_weight=10
                    )
                    alias_count += 1

                    # Create variations (lowercase, without spaces, etc.)
                    variations = DiseaseAliasService._generate_variations(disease_name)
                    for variation in variations:
                        if variation != disease_name.lower():
                            await DiseaseAliasService._create_alias(
                                session=session,
                                alias=variation,
                                mondo_id=placeholder_mondo_id,
                                canonical_name=disease_name,
                                alias_type="variation",
                                is_preferred=False,
                                search_weight=5
                            )
                            alias_count += 1

                await session.commit()
                logger.info(
                    f"✅ Created {alias_count} disease aliases (skipped {skipped_count} technical entries)"
                )
                return alias_count

        except Exception as e:
            logger.error(f"Failed to populate disease aliases: {e}")
            return 0

    @staticmethod
    async def _create_alias(
        session: AsyncSession,
        alias: str,
        mondo_id: str,
        canonical_name: str,
        alias_type: str,
        is_preferred: bool,
        search_weight: int
    ):
        """Create a single disease alias entry."""
        alias_normalized = alias.lower().strip()

        # Ensure mondo_id length fits DB constraint (VARCHAR(100))
        if len(mondo_id) > 100:
            mondo_id = mondo_id[:100]

        # Check if alias already exists
        result = await session.execute(
            select(DiseaseAlias).where(
                DiseaseAlias.alias == alias_normalized,
                DiseaseAlias.mondo_id == mondo_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return  # Skip duplicates

        new_alias = DiseaseAlias(
            id=str(uuid.uuid4()),
            alias=alias_normalized,
            alias_display=alias,
            mondo_id=mondo_id,
            canonical_name=canonical_name,
            alias_type=alias_type,
            search_weight=search_weight,
            is_preferred=is_preferred,
            source="disease_cache",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(new_alias)

    @staticmethod
    def _should_skip_disease(disease_name: str) -> bool:
        """Determine if a disease name should be skipped (technical/genetic entries)."""
        name_lower = disease_name.lower()

        # Skip if contains gene mutation patterns
        if any(pattern in name_lower for pattern in [
            ' gene ', ' mutation', ' variant', ' polymorphism',
            'autosomal dominant', 'autosomal recessive', 'x-linked',
            'chromosome ', ' locus', ' allele', '-related', '-associated',
            'caused disease or disorder', 'infectious disease'
        ]):
            return True

        # Skip if starts with gene names (all caps 3-6 letters followed by numbers or other genes)
        import re
        if re.match(r'^[A-Z]{2,6}\d+', disease_name):
            return True
        if re.match(r'^[A-Z]{3,10}\s+[a-z]', disease_name):  # e.g., "ADAM10 Alzheimer", "ATG16L1 inflammatory"
            return True

        # Skip if disease name is just an abbreviation (2-6 caps) - whitelist common ones
        if re.match(r'^[A-Z]{2,6}$', disease_name) and disease_name not in [
            'AIDS', 'COPD', 'ADHD', 'GERD', 'PTSD', 'OCD', 'ALS', 'MS', 'AD', 'AFib'
        ]:
            return True

        # Skip overly technical names with numbers
        if re.search(r'[A-Z]+\d+', disease_name) and not any(keep in name_lower for keep in [
            'type 1', 'type 2', 'covid-19', 'h1n1', 'h5n1'
        ]):
            return True

        return False

    @staticmethod
    def _generate_variations(disease_name: str) -> List[str]:
        """Generate common variations of a disease name for matching."""
        variations = set()
        name_lower = disease_name.lower()

        # Original lowercase
        variations.add(name_lower)

        # Without "disease" or "disorder"
        for suffix in [' disease', ' disorder', ' syndrome', ' condition']:
            if name_lower.endswith(suffix):
                variations.add(name_lower.replace(suffix, '').strip())

        # Common abbreviations
        # Type 1 Diabetes -> T1D, Type 2 -> T2D
        if 'type 1' in name_lower and 'diabetes' in name_lower:
            variations.add('t1d')
            variations.add('t1dm')
            variations.add('type 1 diabetes')
            variations.add('diabetes type 1')

        if 'type 2' in name_lower and 'diabetes' in name_lower:
            variations.add('t2d')
            variations.add('t2dm')
            variations.add('type 2 diabetes')
            variations.add('diabetes type 2')

        # COPD
        if 'chronic obstructive pulmonary disease' in name_lower:
            variations.add('copd')

        # CHF
        if 'congestive heart failure' in name_lower or 'chronic heart failure' in name_lower:
            variations.add('chf')

        # MI
        if 'myocardial infarction' in name_lower:
            variations.add('mi')
            variations.add('heart attack')

        # CVA
        if 'cerebrovascular accident' in name_lower or 'stroke' in name_lower:
            variations.add('cva')
            variations.add('stroke')

        return list(variations)

    @staticmethod
    def _make_placeholder_mondo_id(disease_name: str) -> str:
        """Create a deterministic, short placeholder mondo_id for a disease name.

        We cannot exceed VARCHAR(100) for the mondo_id column. Use a stable hash
        so repeated runs generate the same ID until a real MONDO ID is linked.
        Format example: "SEARCH:sha1:<40-hex>" (max length 48).
        """
        name = disease_name.strip().lower()
        digest = hashlib.sha1(name.encode("utf-8")).hexdigest()
        return f"SEARCH:sha1:{digest}"

    @staticmethod
    async def lookup_mondo_id(query: str) -> Optional[Dict]:
        """
        Look up a disease query and return the canonical MONDO ID and name.
        Returns: {"mondo_id": "MONDO:xxx", "canonical_name": "Disease Name"}
        """
        query_normalized = query.lower().strip()

        try:
            async for session in get_db_session():
                # Search for exact match first
                result = await session.execute(
                    select(DiseaseAlias)
                    .where(DiseaseAlias.alias == query_normalized)
                    .order_by(DiseaseAlias.search_weight.desc())
                    .limit(1)
                )
                alias = result.scalar_one_or_none()

                if alias:
                    return {
                        "mondo_id": alias.mondo_id,
                        "canonical_name": alias.canonical_name,
                        "matched_alias": alias.alias_display
                    }

                # Try partial match if exact fails
                result = await session.execute(
                    select(DiseaseAlias)
                    .where(DiseaseAlias.alias.like(f"%{query_normalized}%"))
                    .order_by(DiseaseAlias.search_weight.desc())
                    .limit(1)
                )
                alias = result.scalar_one_or_none()

                if alias:
                    return {
                        "mondo_id": alias.mondo_id,
                        "canonical_name": alias.canonical_name,
                        "matched_alias": alias.alias_display
                    }

                return None

        except Exception as e:
            logger.error(f"Alias lookup failed for '{query}': {e}")
            return None

        # Default: no alias found
        return None

    @staticmethod
    async def autocomplete(query: str, limit: int = 20) -> List[str]:
        """
        Get autocomplete suggestions for a disease query.
        Returns list of display names (not MONDO IDs).
        """
        query_normalized = query.lower().strip()

        if len(query_normalized) < 2:
            return []

        try:
            async for session in get_db_session():
                result = await session.execute(
                    select(DiseaseAlias.alias_display, DiseaseAlias.canonical_name)
                    .where(DiseaseAlias.alias.like(f"{query_normalized}%"))
                    .order_by(
                        DiseaseAlias.search_weight.desc(),
                        DiseaseAlias.is_preferred.desc()
                    )
                    .limit(limit)
                )

                suggestions: List[str] = []
                seen = set()

                for alias_display, canonical_name in result:
                    # Prefer canonical names for display
                    display_name = canonical_name if canonical_name else alias_display
                    if display_name not in seen:
                        suggestions.append(display_name)
                        seen.add(display_name)

                return suggestions

        except Exception as e:
            logger.error(f"Autocomplete failed for '{query}': {e}")
            return []

        # Default empty suggestions if no session yielded results
        return []


# Singleton instance
_alias_service = DiseaseAliasService()


async def populate_disease_aliases():
    """Convenience function to populate aliases from cache."""
    return await _alias_service.populate_aliases_from_cache()


async def lookup_disease_by_alias(query: str) -> Optional[Dict]:
    """Convenience function to lookup MONDO ID by alias."""
    return await _alias_service.lookup_mondo_id(query)


async def get_disease_autocomplete(query: str, limit: int = 20) -> List[str]:
    """Convenience function to get autocomplete suggestions."""
    return await _alias_service.autocomplete(query, limit)
