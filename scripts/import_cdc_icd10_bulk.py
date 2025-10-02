#!/usr/bin/env python3
"""
Bulk Import CDC ICD-10-CM Codes

Imports clinically relevant diseases from official CDC ICD-10-CM 2025 dataset.
Smart filtering to import 1,500-2,500 most relevant codes (not all 74,000).

Filtering Strategy:
1. Include all chapter codes (high-level diseases)
2. Include 3-character category codes (common diseases)
3. Include 4-character subcategory codes for major conditions
4. Include select 5-7 character codes for frequently encountered specifics
5. Exclude highly specific administrative/billing codes

This gives comprehensive coverage while maintaining database performance.

Usage:
    python scripts/import_cdc_icd10_bulk.py [--limit 2000] [--dry-run]
"""

import sys
import os
import re
from datetime import datetime
import argparse
from urllib.parse import quote
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.disease_reference import Base, DiseaseReference


class CDCBulkImporter:
    """Imports CDC ICD-10-CM codes with smart filtering"""

    def __init__(self, db_path="ai_nurse_florence.db", limit=None, dry_run=False):
        self.db_path = db_path
        self.limit = limit
        self.dry_run = dry_run

        # Setup database
        if not dry_run:
            self.engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(self.engine)
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = None

        # Stats
        self.stats = {
            "total_in_file": 0,
            "passed_filter": 0,
            "imported": 0,
            "updated": 0,
            "skipped": 0,
            "by_chapter": defaultdict(int),
            "by_code_length": defaultdict(int)
        }

        # Category mappings
        self.chapter_names = self._get_chapter_names()

    def _get_chapter_names(self):
        """Map ICD-10 letter prefixes to chapter names"""
        return {
            'A': 'Infectious and Parasitic Diseases',
            'B': 'Infectious and Parasitic Diseases',
            'C': 'Neoplasms',
            'D0': 'Neoplasms',
            'D1': 'Neoplasms',
            'D2': 'Neoplasms',
            'D3': 'Neoplasms',
            'D4': 'Neoplasms',
            'D5': 'Blood and Immune Disorders',
            'D6': 'Blood and Immune Disorders',
            'D7': 'Blood and Immune Disorders',
            'D8': 'Blood and Immune Disorders',
            'E': 'Endocrine, Nutritional and Metabolic Diseases',
            'F': 'Mental and Behavioral Disorders',
            'G': 'Nervous System Diseases',
            'H0': 'Eye and Adnexa Diseases',
            'H1': 'Eye and Adnexa Diseases',
            'H2': 'Eye and Adnexa Diseases',
            'H3': 'Eye and Adnexa Diseases',
            'H4': 'Eye and Adnexa Diseases',
            'H5': 'Eye and Adnexa Diseases',
            'H6': 'Ear and Mastoid Diseases',
            'H7': 'Ear and Mastoid Diseases',
            'H8': 'Ear and Mastoid Diseases',
            'H9': 'Ear and Mastoid Diseases',
            'I': 'Circulatory System Diseases',
            'J': 'Respiratory System Diseases',
            'K': 'Digestive System Diseases',
            'L': 'Skin and Subcutaneous Tissue Diseases',
            'M': 'Musculoskeletal System Diseases',
            'N': 'Genitourinary System Diseases',
            'O': 'Pregnancy, Childbirth and Puerperium',
            'P': 'Perinatal Period Conditions',
            'Q': 'Congenital Malformations',
            'R': 'Symptoms, Signs and Abnormal Findings',
            'S': 'Injury, Poisoning and External Causes',
            'T': 'Injury, Poisoning and External Causes',
            'U': 'Special Purpose Codes',
            'V': 'External Causes of Morbidity',
            'W': 'External Causes of Morbidity',
            'X': 'External Causes of Morbidity',
            'Y': 'External Causes of Morbidity',
            'Z': 'Factors Influencing Health Status'
        }

    def get_category_name(self, code):
        """Get chapter name from ICD-10 code"""
        if len(code) >= 2:
            prefix = code[:2]
            if prefix in self.chapter_names:
                return self.chapter_names[prefix]

        prefix = code[0]
        return self.chapter_names.get(prefix, 'Other')

    def should_include_code(self, code):
        """
        Smart filtering logic to determine if code should be included.

        Inclusion criteria:
        - 3-character codes (e.g., A00) - category level, always include
        - 4-character codes (e.g., A000) - subcategory, usually include
        - 5-character codes - include for major conditions
        - 6-7 character codes - only include for very common conditions

        Exclusion criteria:
        - Purely administrative codes (Z codes beyond certain level)
        - Highly specific injury codes (S,T codes with 6-7 characters)
        - Very rare genetic syndromes (unless historically significant)
        """

        code_length = len(code)

        # Always include 3-4 character codes (category and subcategory)
        if code_length <= 4:
            return True

        # 5-character codes: Include selectively
        if code_length == 5:
            # Include all major disease categories
            if code[0] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R']:
                return True

            # Exclude most specific injury codes (S, T)
            if code[0] in ['S', 'T']:
                return False

            # Exclude most specific external causes (V, W, X, Y)
            if code[0] in ['V', 'W', 'X', 'Y']:
                return False

            # Include important Z codes
            if code[0] == 'Z':
                # Include cancer screening, immunization, high-risk history
                if code.startswith(('Z11', 'Z12', 'Z13', 'Z23', 'Z85', 'Z86', 'Z87')):
                    return True
                return False

            # Include special codes (U)
            if code[0] == 'U':
                return True

        # 6-7 character codes: Only include for very common/important conditions
        if code_length >= 6:
            # Include critical infectious diseases
            if code.startswith(('A00', 'A01', 'A02', 'A15', 'A16', 'A39', 'A40', 'A41', 'B00', 'B01', 'B02', 'B15', 'B16', 'B17', 'B18', 'B19', 'B20')):
                return True

            # Include major cancers
            if code.startswith(('C18', 'C19', 'C20', 'C34', 'C50', 'C61', 'C64', 'C71', 'C91', 'C92')):
                return True

            # Include diabetes subtypes
            if code.startswith(('E10', 'E11')):
                return True

            # Include mental health conditions
            if code.startswith(('F10', 'F17', 'F32', 'F33', 'F41', 'F43')):
                return True

            # Include common cardiac conditions
            if code.startswith(('I10', 'I20', 'I21', 'I25', 'I48', 'I50', 'I63', 'I64')):
                return True

            # Include common respiratory
            if code.startswith(('J18', 'J44', 'J45')):
                return True

            # Include COVID-19 and vaping
            if code.startswith(('U07', 'U09')):
                return True

            # Most other 6-7 character codes are too specific
            return False

        return True

    def parse_icd10_file(self, filepath):
        """Parse CDC ICD-10-CM codes file"""
        print(f"📂 Reading file: {filepath}")
        print()

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                self.stats["total_in_file"] += 1

                # Parse format: "CODE    Description"
                line = line.strip()
                if not line:
                    continue

                # Split on whitespace (tab or multiple spaces)
                parts = re.split(r'\s{2,}', line, maxsplit=1)
                if len(parts) != 2:
                    continue

                code, description = parts
                code = code.strip()
                description = description.strip()

                # Apply smart filter
                if not self.should_include_code(code):
                    self.stats["skipped"] += 1
                    continue

                self.stats["passed_filter"] += 1
                self.stats["by_code_length"][len(code)] += 1

                # Get category
                category = self.get_category_name(code)
                self.stats["by_chapter"][category] += 1

                # Yield for processing
                yield code, description, category

                # Check limit
                if self.limit and self.stats["passed_filter"] >= self.limit:
                    break

    def build_disease_entry(self, icd10_code, disease_name, category):
        """Build disease reference entry"""
        mondo_id = f"ICD10:{icd10_code}"

        description = f"{disease_name}"
        is_rare = any(keyword in disease_name.lower() for keyword in [
            'rare', 'syndrome', 'congenital', 'hereditary', 'genetic'
        ])

        disease_search = quote(disease_name)
        medlineplus_url = f"https://medlineplus.gov/search/?query={disease_search}"
        pubmed_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={disease_search}"
        icd10_url = f"https://www.icd10data.com/ICD10CM/Codes/{icd10_code.replace('.', '')}"

        return {
            "mondo_id": mondo_id,
            "disease_name": disease_name,
            "disease_synonyms": [],
            "icd10_codes": [icd10_code],
            "snomed_code": None,
            "umls_code": None,
            "short_description": description,
            "disease_category": category,
            "is_rare_disease": is_rare,
            "medlineplus_url": medlineplus_url,
            "pubmed_search_url": pubmed_url,
            "mondo_url": icd10_url,
            "data_source": "CDC-ICD10-CM-2025"
        }

    def import_disease(self, disease_data):
        """Import or update disease"""
        if self.dry_run:
            return True

        try:
            existing = self.session.query(DiseaseReference).filter_by(
                mondo_id=disease_data["mondo_id"]
            ).first()

            if existing:
                for key, value in disease_data.items():
                    setattr(existing, key, value)
                self.stats["updated"] += 1
            else:
                disease = DiseaseReference(**disease_data)
                self.session.add(disease)
                self.stats["imported"] += 1

            # Batch commit every 100
            if (self.stats["imported"] + self.stats["updated"]) % 100 == 0:
                self.session.commit()

            return True

        except Exception as e:
            print(f"❌ Error importing {disease_data.get('disease_name', 'Unknown')}: {e}")
            self.session.rollback()
            return False

    def run_import(self, filepath):
        """Main import process"""
        print("=" * 70)
        print("CDC ICD-10-CM BULK IMPORT")
        if self.dry_run:
            print("🧪 DRY RUN MODE - No database changes")
        print("=" * 70)
        print()

        for code, description, category in self.parse_icd10_file(filepath):
            disease_data = self.build_disease_entry(code, description, category)

            if not self.dry_run:
                self.import_disease(disease_data)

            # Progress update every 500
            if self.stats["passed_filter"] % 500 == 0:
                print(f"  ✅ Progress: {self.stats['passed_filter']} diseases processed")

        # Final commit
        if not self.dry_run and self.session:
            self.session.commit()

        # Summary
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"  Total codes in CDC file: {self.stats['total_in_file']}")
        print(f"  ✅ Passed filter: {self.stats['passed_filter']}")
        print(f"  ⏭️  Skipped (too specific): {self.stats['skipped']}")

        if not self.dry_run:
            print(f"  📥 Imported: {self.stats['imported']}")
            print(f"  🔄 Updated: {self.stats['updated']}")
        print()

        print("📊 By Code Length:")
        for length in sorted(self.stats["by_code_length"].keys()):
            count = self.stats["by_code_length"][length]
            print(f"  • {length} characters: {count}")
        print()

        print("📊 By Chapter:")
        for chapter in sorted(self.stats["by_chapter"].keys()):
            count = self.stats["by_chapter"][chapter]
            print(f"  • {chapter}: {count}")
        print()

        if not self.dry_run:
            total_count = self.session.query(DiseaseReference).count()
            print(f"📊 Total diseases in reference DB: {total_count}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Bulk import CDC ICD-10-CM codes")
    parser.add_argument("--file", default="data/icd10_raw/icd10cm-codes-2025.txt",
                        help="Path to CDC codes file")
    parser.add_argument("--db", default="ai_nurse_florence.db", help="Database path")
    parser.add_argument("--limit", type=int, help="Limit number to import")
    parser.add_argument("--dry-run", action="store_true", help="Test without importing")

    args = parser.parse_args()

    importer = CDCBulkImporter(
        db_path=args.db,
        limit=args.limit,
        dry_run=args.dry_run
    )

    importer.run_import(args.file)


if __name__ == "__main__":
    main()
