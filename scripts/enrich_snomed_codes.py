#!/usr/bin/env python3
"""
Enrich Diagnosis Library with SNOMED CT Codes via UMLS API

Maps ICD-10-CM codes to SNOMED CT codes for Epic/EHR integration.
SNOMED CT is the primary coding system used by Epic and most modern EHRs.

Prerequisites:
- UMLS account with API key (https://uts.nlm.nih.gov/)
- Approval time: 1-2 business days

Usage:
    python scripts/enrich_snomed_codes.py --api-key YOUR_UMLS_KEY [--dry-run]
"""

import sys
import os
import argparse
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.content_settings import DiagnosisContentMap
from src.integrations.umls_client import UMLSClient, VALIDATION_TEST_CASES


class SNOMEDEnricher:
    """Enriches diagnosis library with SNOMED CT codes from UMLS"""

    def __init__(self, api_key: str, db_path: str = "ai_nurse_florence.db", dry_run: bool = False):
        self.api_key = api_key
        self.db_path = db_path
        self.dry_run = dry_run

        # Initialize UMLS client
        self.umls_client = UMLSClient(api_key=api_key, cache_enabled=True)

        # Setup database (only if not dry run)
        if not dry_run:
            self.engine = create_engine(f'sqlite:///{db_path}')
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = None

        # Statistics
        self.stats = {
            'total': 0,
            'enriched': 0,
            'already_had_snomed': 0,
            'not_found': 0,
            'errors': 0
        }

    def validate_api_key(self) -> bool:
        """Validate UMLS API key with known test cases"""
        print("=" * 70)
        print("VALIDATING UMLS API KEY")
        print("=" * 70)
        print()

        # Test with a single known mapping
        test_icd10 = "E11.9"
        expected_snomed = "44054006"

        snomed = self.umls_client.map_icd10_to_snomed(test_icd10)

        if snomed == expected_snomed:
            print(f"✅ API key validated successfully")
            print(f"   Test: {test_icd10} → {snomed}")
            print()
            return True
        else:
            print(f"❌ API key validation failed")
            print(f"   Expected: {test_icd10} → {expected_snomed}")
            print(f"   Got: {test_icd10} → {snomed}")
            print()
            print("   Possible issues:")
            print("   - Invalid API key")
            print("   - Network connectivity problems")
            print("   - UMLS API endpoint changed")
            print()
            return False

    def enrich_all_diagnoses(self):
        """Enrich all diagnoses in library with SNOMED CT codes"""
        print("=" * 70)
        print("SNOMED CT ENRICHMENT")
        if self.dry_run:
            print("🧪 DRY RUN MODE - No database changes")
        print("=" * 70)
        print()

        # Get all diagnoses that need SNOMED codes
        if self.dry_run:
            # For dry run, use in-memory test data
            diagnoses = self._get_sample_diagnoses()
        else:
            diagnoses = self.session.query(DiagnosisContentMap).all()

        self.stats['total'] = len(diagnoses)
        print(f"📊 Processing {self.stats['total']} diagnoses...")
        print()

        # Process each diagnosis
        for i, diagnosis in enumerate(diagnoses, 1):
            icd10_code = diagnosis.icd10_code

            # Skip if already has SNOMED code
            if diagnosis.snomed_code:
                self.stats['already_had_snomed'] += 1
                print(f"  ⏭️  [{i}/{self.stats['total']}] {icd10_code} - Already has SNOMED: {diagnosis.snomed_code}")
                continue

            # Map ICD-10 to SNOMED via UMLS
            print(f"  🔍 [{i}/{self.stats['total']}] {icd10_code} - Looking up SNOMED code...")

            snomed_code = self.umls_client.map_icd10_to_snomed(icd10_code)

            if snomed_code:
                print(f"      ✅ Found: {snomed_code}")

                if not self.dry_run:
                    # Update database
                    try:
                        diagnosis.snomed_code = snomed_code
                        self.session.commit()
                        self.stats['enriched'] += 1
                    except Exception as e:
                        print(f"      ❌ Database error: {e}")
                        self.session.rollback()
                        self.stats['errors'] += 1
                else:
                    self.stats['enriched'] += 1

            else:
                print(f"      ⚠️  Not found in UMLS")
                self.stats['not_found'] += 1

            # Add small delay to be nice to UMLS API (100ms)
            import time
            time.sleep(0.1)

        # Print summary
        print()
        print("=" * 70)
        print("ENRICHMENT COMPLETE")
        print("=" * 70)
        print(f"  Total diagnoses: {self.stats['total']}")
        print(f"  ✅ Newly enriched: {self.stats['enriched']}")
        print(f"  ⏭️  Already had SNOMED: {self.stats['already_had_snomed']}")
        print(f"  ⚠️  Not found in UMLS: {self.stats['not_found']}")
        print(f"  ❌ Errors: {self.stats['errors']}")
        print()

        # Cache stats
        cache_stats = self.umls_client.get_cache_stats()
        print(f"  📦 API calls cached: {cache_stats['cache_size']}")
        print()

        if self.dry_run:
            print("🧪 DRY RUN COMPLETE - Run without --dry-run to update database")
        else:
            print("✅ DATABASE UPDATED - SNOMED CT codes enriched")

        # Epic integration readiness
        self._print_epic_readiness_status()

    def _get_sample_diagnoses(self):
        """Get sample diagnoses for dry run testing"""
        from collections import namedtuple

        Diagnosis = namedtuple('Diagnosis', ['icd10_code', 'snomed_code', 'diagnosis_display'])

        return [
            Diagnosis("E11.9", None, "Type 2 Diabetes Mellitus"),
            Diagnosis("I10", None, "Essential Hypertension"),
            Diagnosis("J45.909", None, "Asthma, Unspecified"),
        ]

    def _print_epic_readiness_status(self):
        """Print Epic/EHR integration readiness status"""
        if self.dry_run:
            return

        total = self.stats['total']
        with_snomed = self.stats['enriched'] + self.stats['already_had_snomed']
        readiness_pct = (with_snomed / total * 100) if total > 0 else 0

        print()
        print("=" * 70)
        print("EPIC/EHR INTEGRATION READINESS")
        print("=" * 70)
        print(f"  Diagnoses with SNOMED CT codes: {with_snomed}/{total} ({readiness_pct:.1f}%)")
        print()

        if readiness_pct >= 100:
            print("  🎉 100% EPIC READY!")
            print("     All diagnoses have SNOMED CT codes")
        elif readiness_pct >= 80:
            print("  ✅ MOSTLY READY for Epic integration")
            print("     Most diagnoses have SNOMED CT codes")
        elif readiness_pct >= 50:
            print("  ⚠️  PARTIALLY READY for Epic integration")
            print("     About half of diagnoses have SNOMED CT codes")
        else:
            print("  ❌ NOT READY for Epic integration")
            print("     Most diagnoses missing SNOMED CT codes")

        print()
        print("  Next steps:")
        print("  1. For diagnoses without SNOMED codes:")
        print("     - Manually look up in SNOMED CT browser: https://browser.ihtsdotools.org/")
        print("     - Or use alternative ICD-10 code with better mapping")
        print("  2. Test FHIR Condition resources with Epic sandbox")
        print("  3. Verify CodeableConcept structure with Epic team")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Enrich diagnosis library with SNOMED CT codes via UMLS API"
    )
    parser.add_argument(
        "--api-key",
        required=True,
        help="UMLS API key (get from https://uts.nlm.nih.gov/)"
    )
    parser.add_argument(
        "--db",
        default="ai_nurse_florence.db",
        help="Database path (default: ai_nurse_florence.db)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without updating database"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate API key, don't enrich"
    )

    args = parser.parse_args()

    # Create enricher
    enricher = SNOMEDEnricher(
        api_key=args.api_key,
        db_path=args.db,
        dry_run=args.dry_run
    )

    # Validate API key first
    if not enricher.validate_api_key():
        print("❌ API key validation failed. Aborting.")
        sys.exit(1)

    if args.validate_only:
        print("✅ API key validated successfully!")
        sys.exit(0)

    # Enrich diagnoses
    enricher.enrich_all_diagnoses()


if __name__ == "__main__":
    main()
