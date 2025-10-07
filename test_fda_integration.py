"""
Test script for FDA OpenFDA API integration
Tests the FDADrugService with real drug queries
"""

import asyncio
import logging

from src.services.fda_drug_service import FDADrugService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_common_drugs():
    """Test FDA API with common medications"""
    service = FDADrugService()

    test_drugs = [
        "aspirin",
        "ibuprofen",
        "metformin",
        "lisinopril",
        "atorvastatin",
    ]

    logger.info("=" * 80)
    logger.info("Testing FDA API with common drugs")
    logger.info("=" * 80)

    for drug_name in test_drugs:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing: {drug_name}")
        logger.info(f"{'=' * 80}")

        try:
            # Test get_drug_label
            label_data = await service.get_drug_label(drug_name)
            if label_data:
                logger.info(f"✓ Found label data for {drug_name}")
                logger.info(
                    f"  Brand names: {label_data.get('openfda', {}).get('brand_name', [])[:3]}"
                )
                logger.info(
                    f"  Generic names: {label_data.get('openfda', {}).get('generic_name', [])[:3]}"
                )
            else:
                logger.warning(f"✗ No label data found for {drug_name}")

            # Test get_drug_interactions
            interactions = await service.get_drug_interactions(drug_name)
            if interactions:
                logger.info(
                    f"✓ Found {len(interactions)} interaction warnings for {drug_name}"
                )
                logger.info(f"  First warning: {interactions[0][:100]}...")
            else:
                logger.warning(f"✗ No interaction data found for {drug_name}")

            # Test get_medication_guide_data
            guide_data = await service.get_medication_guide_data(drug_name)
            logger.info(f"✓ Medication guide data retrieved for {drug_name}")
            logger.info(f"  Data available: {guide_data.get('data_available', False)}")
            if guide_data.get("data_available"):
                logger.info(
                    f"  Purpose: {str(guide_data.get('purpose', 'N/A'))[:100]}..."
                )
                warnings = guide_data.get("warnings") or []
                interactions = guide_data.get("drug_interactions") or []
                logger.info(f"  Warnings: {len(warnings)} found")
                logger.info(f"  Drug interactions: {len(interactions)} found")

        except Exception as e:
            logger.error(f"✗ Error testing {drug_name}: {e}", exc_info=True)

        await asyncio.sleep(0.5)  # Rate limiting - be nice to FDA API


async def test_brand_name_drugs():
    """Test FDA API with brand name medications"""
    service = FDADrugService()

    brand_drugs = [
        "Tylenol",
        "Advil",
        "Lipitor",
        "Glucophage",
    ]

    logger.info("\n" + "=" * 80)
    logger.info("Testing FDA API with brand name drugs")
    logger.info("=" * 80)

    for drug_name in brand_drugs:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing: {drug_name}")
        logger.info(f"{'=' * 80}")

        try:
            guide_data = await service.get_medication_guide_data(drug_name)
            logger.info(f"✓ Retrieved data for {drug_name}")
            logger.info(f"  Data available: {guide_data.get('data_available', False)}")
            logger.info(f"  Drug name: {guide_data.get('drug_name')}")

            if guide_data.get("data_available"):
                logger.info("  ✓ FDA data successfully retrieved")
            else:
                logger.warning(
                    f"  ✗ No FDA data for {drug_name}: {guide_data.get('message')}"
                )

        except Exception as e:
            logger.error(f"✗ Error testing {drug_name}: {e}")

        await asyncio.sleep(0.5)


async def test_rare_drug():
    """Test FDA API fallback with less common drug"""
    service = FDADrugService()

    rare_drugs = ["Vemlidy", "Eliquis", "Xarelto"]

    logger.info("\n" + "=" * 80)
    logger.info("Testing FDA API with less common drugs")
    logger.info("=" * 80)

    for drug_name in rare_drugs:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing: {drug_name}")
        logger.info(f"{'=' * 80}")

        try:
            guide_data = await service.get_medication_guide_data(drug_name)
            logger.info(f"✓ Retrieved data for {drug_name}")
            logger.info(f"  Data available: {guide_data.get('data_available', False)}")

            if guide_data.get("data_available"):
                logger.info("  ✓ FDA data successfully retrieved")
                logger.info(f"  Data source: {guide_data.get('data_source')}")
            else:
                logger.warning(f"  ✗ No FDA data for {drug_name}")

        except Exception as e:
            logger.error(f"✗ Error testing {drug_name}: {e}")

        await asyncio.sleep(0.5)


async def test_adverse_events():
    """Test adverse event reporting"""
    service = FDADrugService()

    logger.info("\n" + "=" * 80)
    logger.info("Testing FDA adverse event reports")
    logger.info("=" * 80)

    test_drug = "aspirin"
    logger.info(f"\nTesting adverse events for: {test_drug}")

    try:
        events = await service.get_drug_adverse_events(test_drug, limit=5)
        if events:
            logger.info(f"✓ Found adverse event data for {test_drug}")
            logger.info(f"  Total reports: {events.get('total_reports', 0)}")
            logger.info(f"  Top reactions: {events.get('top_reactions', [])[:3]}")
        else:
            logger.warning(f"✗ No adverse event data found for {test_drug}")

    except Exception as e:
        logger.error(f"✗ Error testing adverse events: {e}")


async def main():
    """Run all tests"""
    logger.info("\n" + "=" * 80)
    logger.info("FDA OpenFDA API Integration Test Suite")
    logger.info("=" * 80)

    try:
        await test_common_drugs()
        await test_brand_name_drugs()
        await test_rare_drug()
        await test_adverse_events()

        logger.info("\n" + "=" * 80)
        logger.info("✓ Test suite completed successfully!")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\n✗ Test suite interrupted by user")
    except Exception as e:
        logger.error(f"\n✗ Test suite failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
