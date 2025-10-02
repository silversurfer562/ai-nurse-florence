#!/usr/bin/env python3
"""
MONDO Disease Reference Database Importer

This script imports 20,000+ diseases from MONDO Disease Ontology into the
lightweight reference database for lookup purposes.

Data imported:
- Disease name + synonyms
- ICD-10 and SNOMED codes
- Short description
- External resource links (MedlinePlus, PubMed, MONDO)

This is TIER 2 data - lightweight reference only, NO full clinical content.

Usage:
    python scripts/import_mondo_reference.py [--limit 1000] [--test]
"""

import sys
import os
import requests
import time
from datetime import datetime
import argparse
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.disease_reference import Base, DiseaseReference


# MONDO API endpoints
MONDO_SEARCH_API = "https://api.monarchinitiative.org/api/search/entity"
MONDO_DISEASE_API = "https://api.monarchinitiative.org/api/bioentity/disease"


class MondoImporter:
    """Imports disease reference data from MONDO Disease Ontology"""

    def __init__(self, db_path="ai_nurse_florence.db", limit=None, test_mode=False):
        self.db_path = db_path
        self.limit = limit
        self.test_mode = test_mode

        # Setup database
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Stats
        self.stats = {
            "total_processed": 0,
            "imported": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0
        }

    def get_disease_categories(self):
        """
        Define disease categories to import.

        Instead of importing ALL 20,000 diseases, we categorize and prioritize
        based on clinical relevance and common search patterns.
        """
        return {
            # High priority: Common diseases (will be in full library too)
            "cardiovascular": ["heart disease", "hypertension", "stroke", "arrhythmia"],
            "respiratory": ["asthma", "COPD", "pneumonia", "bronchitis"],
            "infectious": ["infection", "sepsis", "influenza", "COVID"],
            "metabolic": ["diabetes", "thyroid", "metabolic syndrome"],
            "neurological": ["seizure", "migraine", "dementia", "neuropathy"],
            "gastrointestinal": ["gastritis", "colitis", "hepatitis", "pancreatitis"],
            "renal": ["kidney disease", "renal failure", "nephropathy"],

            # Medium priority: Specialty conditions
            "autoimmune": ["lupus", "rheumatoid arthritis", "scleroderma"],
            "oncological": ["cancer", "carcinoma", "lymphoma", "leukemia"],
            "hematological": ["anemia", "thrombocytopenia", "coagulopathy"],
            "endocrine": ["adrenal", "pituitary", "hormone"],

            # Rare diseases: For reference lookup only
            "genetic": ["syndrome", "hereditary", "congenital"],
            "rare_metabolic": ["lysosomal storage", "mitochondrial", "peroxisomal"]
        }

    def search_mondo_diseases(self, query, category="disease", limit=100):
        """
        Search MONDO API for diseases matching query.

        Returns list of MONDO IDs and basic info.
        """
        try:
            params = {
                "q": query,
                "category": category,
                "rows": limit
            }

            response = requests.get(MONDO_SEARCH_API, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "docs" in data:
                return data["docs"]
            else:
                return []

        except Exception as e:
            print(f"❌ Error searching MONDO for '{query}': {e}")
            return []

    def get_disease_details(self, mondo_id):
        """
        Get detailed information for a specific MONDO disease.

        Returns dict with all disease metadata.
        """
        try:
            url = f"{MONDO_DISEASE_API}/{mondo_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"❌ Error fetching details for {mondo_id}: {e}")
            return None

    def extract_disease_data(self, disease_doc):
        """
        Extract relevant fields from MONDO disease document.

        MONDO returns complex nested JSON - this extracts what we need.
        """
        # Get MONDO ID
        mondo_id = disease_doc.get("id", "")
        if not mondo_id.startswith("MONDO:"):
            mondo_id = f"MONDO:{mondo_id}"

        # Get disease name
        disease_name = disease_doc.get("label", disease_doc.get("name", "Unknown"))

        # Get synonyms
        synonyms = []
        if "synonym" in disease_doc:
            for syn in disease_doc.get("synonym", []):
                if isinstance(syn, str):
                    synonyms.append(syn)
                elif isinstance(syn, dict) and "val" in syn:
                    synonyms.append(syn["val"])

        # Get ICD-10 codes
        icd10_codes = []
        snomed_code = None
        umls_code = None

        if "xrefs" in disease_doc:
            for xref in disease_doc["xrefs"]:
                xref_val = xref if isinstance(xref, str) else xref.get("val", "")

                if xref_val.startswith("ICD10:") or xref_val.startswith("ICD10CM:"):
                    code = xref_val.split(":")[-1]
                    if code not in icd10_codes:
                        icd10_codes.append(code)
                elif xref_val.startswith("SNOMEDCT:") or xref_val.startswith("SNOMED:"):
                    snomed_code = xref_val.split(":")[-1]
                elif xref_val.startswith("UMLS:"):
                    umls_code = xref_val.split(":")[-1]

        # Get description (first sentence only)
        description = disease_doc.get("description", "")
        if isinstance(description, list) and len(description) > 0:
            description = description[0]

        # Truncate to first 2 sentences max
        if description:
            sentences = description.split(". ")
            description = ". ".join(sentences[:2])
            if not description.endswith("."):
                description += "."

        # Determine if rare disease
        is_rare = False
        if "rare" in disease_name.lower() or "syndrome" in disease_name.lower():
            is_rare = True

        # Get category
        category = disease_doc.get("category", ["Unknown"])[0] if "category" in disease_doc else "Unknown"

        # Generate external URLs
        medlineplus_search = f"https://medlineplus.gov/search/?query={disease_name.replace(' ', '+')}"
        pubmed_search = f"https://pubmed.ncbi.nlm.nih.gov/?term={disease_name.replace(' ', '+')}"
        mondo_url = f"https://monarchinitiative.org/disease/{mondo_id}"

        return {
            "mondo_id": mondo_id,
            "disease_name": disease_name,
            "disease_synonyms": synonyms,
            "icd10_codes": icd10_codes,
            "snomed_code": snomed_code,
            "umls_code": umls_code,
            "short_description": description or None,
            "disease_category": category,
            "is_rare_disease": is_rare,
            "medlineplus_url": medlineplus_search,
            "pubmed_search_url": pubmed_search,
            "mondo_url": mondo_url,
            "data_source": "MONDO"
        }

    def import_disease(self, disease_data):
        """
        Import or update a disease in the reference database.
        """
        try:
            # Check if already exists
            existing = self.session.query(DiseaseReference).filter_by(
                mondo_id=disease_data["mondo_id"]
            ).first()

            if existing:
                # Update existing
                for key, value in disease_data.items():
                    setattr(existing, key, value)
                existing.last_updated_at = datetime.utcnow()
                self.stats["updated"] += 1
            else:
                # Create new
                disease = DiseaseReference(**disease_data)
                self.session.add(disease)
                self.stats["imported"] += 1

            self.session.commit()
            return True

        except Exception as e:
            print(f"❌ Error importing {disease_data.get('disease_name', 'Unknown')}: {e}")
            self.session.rollback()
            self.stats["errors"] += 1
            return False

    def run_import(self):
        """
        Main import process.

        Searches MONDO for each category and imports diseases.
        """
        print("=" * 70)
        print("MONDO DISEASE REFERENCE IMPORT")
        print("=" * 70)
        print()

        if self.test_mode:
            print("🧪 TEST MODE: Importing limited sample")
            print()

        categories = self.get_disease_categories()

        for category_name, search_terms in categories.items():
            print(f"\n📁 Category: {category_name.upper()}")
            print("-" * 70)

            for search_term in search_terms:
                if self.limit and self.stats["total_processed"] >= self.limit:
                    print(f"\n⏹️  Reached limit of {self.limit} diseases")
                    break

                print(f"  Searching: '{search_term}'...", end=" ")

                # Search MONDO
                diseases = self.search_mondo_diseases(
                    query=search_term,
                    limit=20 if self.test_mode else 100
                )

                print(f"Found {len(diseases)} results")

                # Process each disease
                for disease_doc in diseases:
                    if self.limit and self.stats["total_processed"] >= self.limit:
                        break

                    self.stats["total_processed"] += 1

                    # Extract data
                    disease_data = self.extract_disease_data(disease_doc)

                    # Skip if no ICD-10 code (probably not clinically relevant)
                    if not disease_data["icd10_codes"]:
                        self.stats["skipped"] += 1
                        continue

                    # Import
                    if self.import_disease(disease_data):
                        print(f"    ✅ {disease_data['disease_name'][:60]}")

                # Rate limiting
                time.sleep(0.5)

            if self.limit and self.stats["total_processed"] >= self.limit:
                break

        # Print summary
        print("\n" + "=" * 70)
        print("IMPORT COMPLETE")
        print("=" * 70)
        print(f"  Total processed: {self.stats['total_processed']}")
        print(f"  ✅ Imported: {self.stats['imported']}")
        print(f"  🔄 Updated: {self.stats['updated']}")
        print(f"  ⏭️  Skipped (no ICD-10): {self.stats['skipped']}")
        print(f"  ❌ Errors: {self.stats['errors']}")
        print()

        # Show database stats
        total_count = self.session.query(DiseaseReference).count()
        rare_count = self.session.query(DiseaseReference).filter_by(is_rare_disease=True).count()

        print(f"📊 Database Statistics:")
        print(f"  Total diseases in reference DB: {total_count}")
        print(f"  Rare diseases: {rare_count}")
        print(f"  Common diseases: {total_count - rare_count}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Import MONDO disease reference data")
    parser.add_argument("--limit", type=int, help="Limit number of diseases to import (for testing)")
    parser.add_argument("--test", action="store_true", help="Test mode (import small sample)")
    parser.add_argument("--db", type=str, default="ai_nurse_florence.db", help="Database path")

    args = parser.parse_args()

    # Set limit for test mode
    if args.test and not args.limit:
        args.limit = 50

    # Run import
    importer = MondoImporter(
        db_path=args.db,
        limit=args.limit,
        test_mode=args.test
    )

    importer.run_import()


if __name__ == "__main__":
    main()
