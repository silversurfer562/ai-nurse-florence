#!/usr/bin/env python3
"""
One-time script to populate disease aliases from cached data.
Run this to build the initial alias mappings.
"""

import asyncio
import logging
import os

# Force use of dev.db
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./dev.db"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Populate disease aliases from cached disease data."""
    try:
        from src.services.disease_alias_service import populate_disease_aliases

        logger.info("🚀 Starting disease alias population...")
        alias_count = await populate_disease_aliases()

        if alias_count > 0:
            logger.info(f"✅ Successfully created {alias_count} disease aliases!")
            logger.info("Disease lookup will now support:")
            logger.info("  - Abbreviations (T1DM, COPD, MI, CHF, CVA)")
            logger.info("  - Variations (Type 1 Diabetes, Diabetes Type 1)")
            logger.info("  - Common terms (heart attack, stroke)")
        else:
            logger.warning("⚠️ No aliases created. Check if disease cache has data.")

    except Exception as e:
        logger.error(f"❌ Failed to populate aliases: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
