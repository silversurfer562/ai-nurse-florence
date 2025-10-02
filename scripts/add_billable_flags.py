#!/usr/bin/env python3
"""
Add Billable Code Flags to Disease Reference Database

Determines which ICD-10 codes are billable according to CMS guidelines:
- 3-character codes: NOT billable (too vague, need more specificity)
- 4-character codes: May be billable (verify with payer)
- 5+ character codes: Usually billable

This helps users understand which codes require additional specificity for billing.

Usage:
    python scripts/add_billable_flags.py [--dry-run]
"""

import sys
import os
import argparse
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Boolean, String
from sqlalchemy.orm import sessionmaker
from src.models.disease_reference import Base, DiseaseReference


class BillableCodeAnalyzer:
    """Analyzes ICD-10 codes to determine billable status"""

    def __init__(self, db_path="ai_nurse_florence.db", dry_run=False):
        self.db_path = db_path
        self.dry_run = dry_run

        # Setup database
        if not dry_run:
            self.engine = create_engine(f'sqlite:///{db_path}')

            # Add columns if they don't exist
            self._add_columns_if_needed()

            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = None

        # Stats
        self.stats = defaultdict(int)

    def _add_columns_if_needed(self):
        """Add billable columns to disease_reference table if not exists"""
        from sqlalchemy import inspect, text

        inspector = inspect(self.engine)
        columns = [col['name'] for col in inspector.get_columns('disease_reference')]

        with self.engine.connect() as conn:
            if 'is_billable' not in columns:
                print("Adding 'is_billable' column...")
                conn.execute(text('ALTER TABLE disease_reference ADD COLUMN is_billable BOOLEAN DEFAULT TRUE'))
                conn.commit()

            if 'billable_note' not in columns:
                print("Adding 'billable_note' column...")
                conn.execute(text('ALTER TABLE disease_reference ADD COLUMN billable_note VARCHAR(200)'))
                conn.commit()

    def analyze_billability(self, icd10_code: str) -> tuple[bool, str]:
        """
        Determine if ICD-10 code is billable.

        CMS Rules:
        - 3-character codes: NOT billable (header codes)
        - 4-character codes: Sometimes billable (depends on category)
        - 5+ character codes: Usually billable

        Args:
            icd10_code: ICD-10 code with or without dot (e.g., "E11.9" or "E119")

        Returns:
            Tuple of (is_billable: bool, note: str)
        """
        # Remove dot for length calculation
        code_without_dot = icd10_code.replace(".", "")
        code_length = len(code_without_dot)

        # Determine billable status
        if code_length <= 3:
            # 3-character codes are category headers, not billable
            return (
                False,
                "⚠️ Not billable - code requires additional specificity for billing. This is a category header."
            )

        elif code_length == 4:
            # 4-character codes may or may not be billable
            # Check if there are more specific child codes
            return (
                True,
                "⚠️ Verify billability - code may require more specificity. Check with payer."
            )

        elif code_length >= 5:
            # 5+ character codes are usually billable
            return (
                True,
                None  # No warning needed
            )

        else:
            # Fallback (shouldn't happen)
            return (True, None)

    def process_all_diseases(self):
        """Process all diseases in database"""
        print("=" * 70)
        print("BILLABLE CODE FLAG ANALYSIS")
        if self.dry_run:
            print("🧪 DRY RUN MODE - No database changes")
        print("=" * 70)
        print()

        # Get all diseases
        if self.dry_run:
            # For dry run, just show sample
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            engine = create_engine(f'sqlite:///{self.db_path}')
            Session = sessionmaker(bind=engine)
            session = Session()
            diseases = session.query(DiseaseReference).limit(20).all()
        else:
            diseases = self.session.query(DiseaseReference).all()

        total = len(diseases)
        print(f"Analyzing {total} diseases...")
        print()

        # Process each disease
        for i, disease in enumerate(diseases, 1):
            # Get first ICD-10 code (diseases may have multiple)
            icd10_codes = disease.icd10_codes if isinstance(disease.icd10_codes, list) else [disease.icd10_codes]
            if not icd10_codes or not icd10_codes[0]:
                self.stats['no_icd10'] += 1
                continue

            icd10_code = icd10_codes[0]

            # Analyze billability
            is_billable, note = self.analyze_billability(icd10_code)

            # Update stats
            if is_billable:
                self.stats['billable'] += 1
                if note:
                    self.stats['billable_with_warning'] += 1
                else:
                    self.stats['fully_billable'] += 1
            else:
                self.stats['not_billable'] += 1

            # Update database
            if not self.dry_run:
                disease.is_billable = is_billable
                disease.billable_note = note

                # Commit in batches
                if i % 100 == 0:
                    self.session.commit()
                    print(f"  ✅ Processed {i}/{total} diseases...")

            # Show sample in dry run
            elif self.dry_run and i <= 10:
                status = "✅ Billable" if is_billable else "❌ Not Billable"
                print(f"{icd10_code:10} | {status:20} | {disease.disease_name[:40]}")
                if note:
                    print(f"           | Note: {note}")
                print()

        # Final commit
        if not self.dry_run:
            self.session.commit()

        # Print summary
        print()
        print("=" * 70)
        print("ANALYSIS COMPLETE")
        print("=" * 70)
        print(f"  Total diseases analyzed: {total}")
        print(f"  ✅ Fully billable (no warnings): {self.stats['fully_billable']}")
        print(f"  ⚠️  Billable with warnings: {self.stats['billable_with_warning']}")
        print(f"  ❌ Not billable: {self.stats['not_billable']}")
        print(f"  🔍 No ICD-10 code: {self.stats['no_icd10']}")
        print()

        # Breakdown by code length
        print("📊 Billability by Code Length:")
        print(f"  3 characters: Category headers (NOT billable)")
        print(f"  4 characters: May be billable (verify with payer)")
        print(f"  5+ characters: Usually billable")
        print()

        if not self.dry_run:
            # Show some examples
            print("📋 Example Non-Billable Codes (3-character):")
            non_billable = self.session.query(DiseaseReference).filter_by(is_billable=False).limit(5).all()
            for disease in non_billable:
                icd10 = disease.icd10_codes[0] if disease.icd10_codes else "N/A"
                print(f"  • {icd10:10} {disease.disease_name}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Add billable code flags")
    parser.add_argument("--db", default="ai_nurse_florence.db", help="Database path")
    parser.add_argument("--dry-run", action="store_true", help="Test without updating database")

    args = parser.parse_args()

    analyzer = BillableCodeAnalyzer(db_path=args.db, dry_run=args.dry_run)
    analyzer.process_all_diseases()

    if args.dry_run:
        print("🧪 DRY RUN COMPLETE - Run without --dry-run to update database")
    else:
        print("✅ DATABASE UPDATED - Billable flags added to all diseases")


if __name__ == "__main__":
    main()
