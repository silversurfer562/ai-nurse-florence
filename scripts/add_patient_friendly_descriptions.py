#!/usr/bin/env python3
"""
Add Patient-Friendly Descriptions to Diagnosis Library

Converts technical medical terminology into Grade 6-8 reading level descriptions
that patients can easily understand.

Grade 6-8 Guidelines:
- Simple, everyday words
- Short sentences (15-20 words max)
- Active voice
- Concrete examples
- Avoid medical jargon

Usage:
    python scripts/add_patient_friendly_descriptions.py [--dry-run]
"""

import sys
import os
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, Column, Text, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from src.models.content_settings import DiagnosisContentMap, Base

# Top 10 most common diagnoses with patient-friendly descriptions
PATIENT_FRIENDLY_DESCRIPTIONS = {
    "diabetes_type2": {
        "technical": "Type 2 Diabetes Mellitus",
        "patient_friendly": "Type 2 diabetes is when your body can't use sugar properly. Your blood sugar stays too high, which can damage your body over time. This happens when your body doesn't make enough insulin or can't use it well. You can manage it with healthy eating, exercise, and sometimes medicine.",
        "reading_level": "Grade 6-7"
    },

    "hypertension": {
        "technical": "Essential (Primary) Hypertension",
        "patient_friendly": "High blood pressure means your blood pushes too hard against your blood vessel walls. Over time, this can damage your heart, brain, and kidneys. Most people feel fine with high blood pressure, so regular check-ups are important. You can control it with healthy habits and medicine.",
        "reading_level": "Grade 6-7"
    },

    "asthma_exacerbation": {
        "technical": "Asthma Exacerbation, Unspecified",
        "patient_friendly": "An asthma attack happens when your airways swell and tighten, making it hard to breathe. You might wheeze, cough, or feel like you can't get enough air. Quick-relief medicine can help open your airways. Avoid triggers like smoke, dust, or cold air.",
        "reading_level": "Grade 6-7"
    },

    "pneumonia": {
        "technical": "Pneumonia, Unspecified Organism",
        "patient_friendly": "Pneumonia is an infection in your lungs that makes tiny air sacs fill with fluid or pus. You might have fever, cough, and trouble breathing. Your body needs rest and plenty of fluids. Antibiotics can help if bacteria caused it. It usually takes a few weeks to fully recover.",
        "reading_level": "Grade 7-8"
    },

    "uti": {
        "technical": "Urinary Tract Infection, Site Not Specified",
        "patient_friendly": "A urinary tract infection (UTI) is when bacteria get into your bladder or urinary system. You might feel burning when you pee, need to go often, or have cloudy urine. Antibiotics can clear it up in a few days. Drinking lots of water helps flush out bacteria.",
        "reading_level": "Grade 6-7"
    },

    "copd": {
        "technical": "Chronic Obstructive Pulmonary Disease, Unspecified",
        "patient_friendly": "COPD is long-term lung damage that makes breathing hard. Your airways are blocked or damaged, so less air gets through. You might feel short of breath or cough a lot. Smoking is the main cause. Medicine, oxygen, and quitting smoking can help you breathe better.",
        "reading_level": "Grade 7-8"
    },

    "chf": {
        "technical": "Heart Failure, Unspecified",
        "patient_friendly": "Heart failure means your heart can't pump blood as well as it should. Your body doesn't get enough oxygen and blood. You might feel tired, short of breath, or notice swelling in your legs. Medicine, diet changes, and limiting salt can help your heart work better.",
        "reading_level": "Grade 7-8"
    },

    "chest_pain": {
        "technical": "Chest Pain, Unspecified",
        "patient_friendly": "Chest pain can have many causes - from heartburn to heart problems. It might feel like pressure, burning, or sharp pain. If pain spreads to your arm, jaw, or back, or if you have trouble breathing, call 911 right away. These could be signs of a heart attack.",
        "reading_level": "Grade 6-7"
    },

    "abdominal_pain": {
        "technical": "Abdominal Pain, Unspecified",
        "patient_friendly": "Belly pain can come from many things - gas, food problems, or infections. The pain might be sharp, dull, or cramping. Where it hurts and how bad it feels helps doctors find the cause. Severe pain, fever, or vomiting means you should see a doctor soon.",
        "reading_level": "Grade 6-7"
    },

    "headache": {
        "technical": "Headache, Unspecified",
        "patient_friendly": "Headaches cause pain in your head or face. They can be dull, throbbing, or sharp. Common causes include stress, not drinking enough water, or muscle tension. Rest, water, and pain medicine often help. Severe headaches with vision changes or confusion need immediate care.",
        "reading_level": "Grade 6-7"
    }
}


class PatientFriendlyDescriptionAdder:
    """Adds patient-friendly descriptions to diagnosis library"""

    def __init__(self, db_path="ai_nurse_florence.db", dry_run=False):
        self.db_path = db_path
        self.dry_run = dry_run

        # Setup database
        if not dry_run:
            self.engine = create_engine(f'sqlite:///{db_path}')
            self._add_column_if_needed()
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
        else:
            self.session = None

        self.stats = {
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }

    def _add_column_if_needed(self):
        """Add patient_friendly_description column if not exists"""
        inspector = inspect(self.engine)
        columns = [col['name'] for col in inspector.get_columns('diagnosis_content_map')]

        with self.engine.connect() as conn:
            if 'patient_friendly_description' not in columns:
                print("Adding 'patient_friendly_description' column...")
                conn.execute(text(
                    'ALTER TABLE diagnosis_content_map ADD COLUMN patient_friendly_description TEXT'
                ))
                conn.commit()

    def add_descriptions(self):
        """Add patient-friendly descriptions to diagnoses"""
        print("=" * 70)
        print("PATIENT-FRIENDLY DESCRIPTIONS")
        if self.dry_run:
            print("🧪 DRY RUN MODE - No database changes")
        print("=" * 70)
        print()

        # Process each diagnosis with a patient-friendly description
        for diagnosis_id, content in PATIENT_FRIENDLY_DESCRIPTIONS.items():
            print(f"\n📋 {diagnosis_id.upper()}")
            print(f"   Technical: {content['technical']}")
            print(f"   Reading Level: {content['reading_level']}")
            print()
            print(f"   Patient-Friendly:")
            print(f"   {content['patient_friendly']}")
            print()

            if not self.dry_run:
                # Update database
                try:
                    diagnosis = self.session.query(DiagnosisContentMap).filter_by(
                        id=diagnosis_id
                    ).first()

                    if diagnosis:
                        diagnosis.patient_friendly_description = content['patient_friendly']
                        self.session.commit()
                        self.stats['updated'] += 1
                        print(f"   ✅ Updated in database")
                    else:
                        print(f"   ⚠️  Diagnosis '{diagnosis_id}' not found in database")
                        self.stats['skipped'] += 1

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    self.stats['errors'] += 1
                    self.session.rollback()

        # Print summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"  ✅ Updated: {self.stats['updated']}")
        print(f"  ⚠️  Skipped: {self.stats['skipped']}")
        print(f"  ❌ Errors: {self.stats['errors']}")
        print()

        if self.dry_run:
            print("🧪 DRY RUN COMPLETE - Run without --dry-run to update database")
        else:
            print("✅ DATABASE UPDATED - Patient-friendly descriptions added")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Add patient-friendly descriptions to diagnosis library"
    )
    parser.add_argument("--db", default="ai_nurse_florence.db", help="Database path")
    parser.add_argument("--dry-run", action="store_true", help="Preview without updating")

    args = parser.parse_args()

    adder = PatientFriendlyDescriptionAdder(db_path=args.db, dry_run=args.dry_run)
    adder.add_descriptions()


if __name__ == "__main__":
    main()
