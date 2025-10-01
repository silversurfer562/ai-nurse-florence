"""
Populate Diagnosis Content Library with FHIR Codes

Creates initial diagnosis library with:
- ICD-10 codes (International Classification of Diseases)
- SNOMED CT codes (Epic's primary coding system)
- Standard content for common diagnoses
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.content_settings import Base, DiagnosisContentMap
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///./ai_nurse_florence.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Common diagnoses with FHIR codes
DIAGNOSIS_LIBRARY = [
    {
        "id": "diabetes_type2",
        "icd10_code": "E11.9",
        "snomed_code": "44054006",
        "diagnosis_display": "Type 2 Diabetes Mellitus",
        "diagnosis_name": "Type 2 Diabetes",  # Legacy
        "diagnosis_aliases": ["diabetes type 2", "T2DM", "DM2", "diabetes mellitus type 2"],
        "standard_warning_signs": [
            "Blood sugar over 300 mg/dL",
            "Blood sugar under 70 mg/dL",
            "Severe confusion or disorientation",
            "Fruity-smelling breath",
            "Extreme thirst despite drinking fluids",
            "Blurred vision that persists"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "860975",
                "medication_display": "Metformin",
                "dosage_value": "500",
                "dosage_unit": "mg",
                "frequency_code": "BID",
                "frequency_display": "Twice daily",
                "instructions": "Take with food to reduce stomach upset"
            }
        ],
        "standard_activity_restrictions": [
            "Monitor blood sugar before and after exercise",
            "Avoid strenuous exercise if blood sugar is over 250 mg/dL",
            "Carry glucose tablets during exercise"
        ],
        "standard_diet_instructions": "Follow diabetic diet plan. Limit simple sugars and refined carbohydrates. Eat regular meals at consistent times.",
        "standard_follow_up_instructions": "Follow up with your primary care doctor or endocrinologist in 1-2 weeks. Bring your blood sugar log.",
        "patient_education_key_points": [
            "Check blood sugar as prescribed",
            "Take medications as directed",
            "Follow meal plan",
            "Exercise regularly",
            "Check feet daily for sores"
        ],
        "is_chronic_condition": True,
        "requires_specialist_followup": True,
        "typical_followup_days": 14
    },
    {
        "id": "hypertension",
        "icd10_code": "I10",
        "snomed_code": "38341003",
        "diagnosis_display": "Essential (Primary) Hypertension",
        "diagnosis_name": "High Blood Pressure",
        "diagnosis_aliases": ["hypertension", "HTN", "high blood pressure", "elevated blood pressure"],
        "standard_warning_signs": [
            "Severe headache",
            "Chest pain",
            "Difficulty breathing",
            "Blood pressure over 180/120",
            "Vision changes",
            "Severe anxiety or confusion"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "197361",
                "medication_display": "Lisinopril",
                "dosage_value": "10",
                "dosage_unit": "mg",
                "frequency_code": "QD",
                "frequency_display": "Once daily",
                "instructions": "Take at the same time each day"
            }
        ],
        "standard_activity_restrictions": [
            "Regular exercise (30 minutes most days)",
            "Avoid heavy lifting until blood pressure controlled"
        ],
        "standard_diet_instructions": "Low sodium diet (less than 2000mg per day). Limit caffeine and alcohol. Follow DASH diet principles.",
        "standard_follow_up_instructions": "Follow up with your doctor in 7-10 days to recheck blood pressure.",
        "patient_education_key_points": [
            "Check blood pressure at home regularly",
            "Reduce salt intake",
            "Maintain healthy weight",
            "Limit alcohol",
            "Manage stress"
        ],
        "is_chronic_condition": True,
        "requires_specialist_followup": False,
        "typical_followup_days": 7
    },
    {
        "id": "pneumonia",
        "icd10_code": "J18.9",
        "snomed_code": "233604007",
        "diagnosis_display": "Pneumonia, Unspecified Organism",
        "diagnosis_name": "Pneumonia",
        "diagnosis_aliases": ["pneumonia", "lung infection"],
        "standard_warning_signs": [
            "Fever over 101°F (38.3°C) that doesn't improve",
            "Difficulty breathing or shortness of breath",
            "Chest pain that is severe or worsening",
            "Coughing up blood or rust-colored mucus",
            "Confusion or altered mental status",
            "Inability to keep fluids down"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "723",
                "medication_display": "Amoxicillin",
                "dosage_value": "500",
                "dosage_unit": "mg",
                "frequency_code": "TID",
                "frequency_display": "Three times daily",
                "instructions": "Complete the full course even if feeling better"
            }
        ],
        "standard_activity_restrictions": [
            "Rest for 3-5 days",
            "Avoid strenuous activity for 1-2 weeks",
            "Stay home from work for at least 3-5 days",
            "Avoid crowded places until fever-free for 24 hours"
        ],
        "standard_diet_instructions": "Drink plenty of fluids (8-10 glasses of water per day). Eat nutritious meals to support recovery.",
        "standard_follow_up_instructions": "See your primary care doctor in 7-10 days for follow-up chest X-ray.",
        "patient_education_key_points": [
            "Complete all antibiotics",
            "Stay hydrated",
            "Use humidifier",
            "Get plenty of rest",
            "Cover coughs and sneezes"
        ],
        "is_chronic_condition": False,
        "requires_specialist_followup": False,
        "typical_followup_days": 7
    },
    {
        "id": "uti",
        "icd10_code": "N39.0",
        "snomed_code": "68566005",
        "diagnosis_display": "Urinary Tract Infection, Site Not Specified",
        "diagnosis_name": "Urinary Tract Infection",
        "diagnosis_aliases": ["UTI", "bladder infection", "urinary tract infection"],
        "standard_warning_signs": [
            "Fever over 101°F",
            "Severe back or flank pain",
            "Blood in urine",
            "Nausea and vomiting",
            "Symptoms not improving after 2 days of antibiotics"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "205426",
                "medication_display": "Trimethoprim-Sulfamethoxazole (Bactrim DS)",
                "dosage_value": "1",
                "dosage_unit": "tablet",
                "frequency_code": "BID",
                "frequency_display": "Twice daily",
                "instructions": "Take with full glass of water"
            }
        ],
        "standard_activity_restrictions": [
            "Rest as needed",
            "Stay well hydrated",
            "Avoid sexual activity until infection clears"
        ],
        "standard_diet_instructions": "Drink plenty of water (8-10 glasses daily). Cranberry juice may help prevent recurrence. Avoid caffeine and alcohol.",
        "standard_follow_up_instructions": "Call doctor if symptoms don't improve in 48 hours. Follow up in 1-2 weeks if recurrent infections.",
        "patient_education_key_points": [
            "Drink plenty of water",
            "Urinate frequently",
            "Wipe front to back",
            "Complete all antibiotics",
            "Avoid irritating products"
        ],
        "is_chronic_condition": False,
        "requires_specialist_followup": False,
        "typical_followup_days": 14
    },
    {
        "id": "copd",
        "icd10_code": "J44.9",
        "snomed_code": "13645005",
        "diagnosis_display": "Chronic Obstructive Pulmonary Disease, Unspecified",
        "diagnosis_name": "COPD",
        "diagnosis_aliases": ["COPD", "chronic obstructive pulmonary disease", "emphysema", "chronic bronchitis"],
        "standard_warning_signs": [
            "Increased shortness of breath",
            "Change in color or amount of sputum",
            "Fever",
            "Confusion or drowsiness",
            "Chest pain",
            "Lips or fingernails turning blue"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "746763",
                "medication_display": "Albuterol Inhaler",
                "dosage_value": "2",
                "dosage_unit": "puffs",
                "frequency_code": "Q4H",
                "frequency_display": "Every 4 hours as needed",
                "instructions": "Rinse mouth after use"
            }
        ],
        "standard_activity_restrictions": [
            "Pace activities with rest periods",
            "Avoid cold air and air pollution",
            "Use oxygen as prescribed"
        ],
        "standard_diet_instructions": "Eat small, frequent meals. Avoid gas-producing foods. Stay well hydrated unless fluid restricted.",
        "standard_follow_up_instructions": "Follow up with pulmonologist in 1-2 weeks. Bring medication list.",
        "patient_education_key_points": [
            "Quit smoking",
            "Use medications as prescribed",
            "Practice breathing exercises",
            "Get flu and pneumonia vaccines",
            "Recognize early warning signs"
        ],
        "is_chronic_condition": True,
        "requires_specialist_followup": True,
        "typical_followup_days": 14
    },
    {
        "id": "chf",
        "icd10_code": "I50.9",
        "snomed_code": "42343007",
        "diagnosis_display": "Heart Failure, Unspecified",
        "diagnosis_name": "Congestive Heart Failure",
        "diagnosis_aliases": ["CHF", "heart failure", "congestive heart failure", "cardiac failure"],
        "standard_warning_signs": [
            "Sudden weight gain (2-3 pounds in a day)",
            "Increased swelling in legs or feet",
            "Severe shortness of breath",
            "Shortness of breath lying flat",
            "New or worsening cough",
            "Extreme fatigue"
        ],
        "standard_medications": [
            {
                "medication_code_rxnorm": "18631",
                "medication_display": "Furosemide (Lasix)",
                "dosage_value": "20",
                "dosage_unit": "mg",
                "frequency_code": "QD",
                "frequency_display": "Once daily",
                "instructions": "Take in morning to avoid nighttime urination"
            }
        ],
        "standard_activity_restrictions": [
            "Elevate legs when sitting",
            "Avoid heavy lifting",
            "Moderate exercise as tolerated",
            "Weigh yourself daily at same time"
        ],
        "standard_diet_instructions": "Low sodium diet (less than 2000mg per day). Fluid restriction as prescribed. Monitor daily weights.",
        "standard_follow_up_instructions": "Follow up with cardiologist in 1 week. Call sooner if weight increases or symptoms worsen.",
        "patient_education_key_points": [
            "Weigh daily",
            "Limit salt and fluids",
            "Take medications as prescribed",
            "Elevate legs",
            "Report weight gain immediately"
        ],
        "is_chronic_condition": True,
        "requires_specialist_followup": True,
        "typical_followup_days": 7
    }
]


def populate_diagnoses():
    """Populate diagnosis library with FHIR codes"""
    session = Session()

    try:
        for diagnosis_data in DIAGNOSIS_LIBRARY:
            # Check if already exists
            existing = session.query(DiagnosisContentMap).filter_by(
                icd10_code=diagnosis_data["icd10_code"]
            ).first()

            if existing:
                print(f"✓ Diagnosis already exists: {diagnosis_data['diagnosis_display']}")
                continue

            # Create new diagnosis
            diagnosis = DiagnosisContentMap(
                id=diagnosis_data["id"],
                icd10_code=diagnosis_data["icd10_code"],
                snomed_code=diagnosis_data["snomed_code"],
                diagnosis_display=diagnosis_data["diagnosis_display"],
                diagnosis_name=diagnosis_data["diagnosis_name"],
                diagnosis_aliases=diagnosis_data["diagnosis_aliases"],
                standard_warning_signs=diagnosis_data["standard_warning_signs"],
                standard_medications=diagnosis_data["standard_medications"],
                standard_activity_restrictions=diagnosis_data["standard_activity_restrictions"],
                standard_diet_instructions=diagnosis_data["standard_diet_instructions"],
                standard_follow_up_instructions=diagnosis_data["standard_follow_up_instructions"],
                patient_education_key_points=diagnosis_data["patient_education_key_points"],
                is_chronic_condition=diagnosis_data["is_chronic_condition"],
                requires_specialist_followup=diagnosis_data["requires_specialist_followup"],
                typical_followup_days=diagnosis_data["typical_followup_days"],
                times_used=0,
                created_at=datetime.utcnow()
            )

            session.add(diagnosis)
            print(f"✓ Added: {diagnosis_data['diagnosis_display']} (ICD-10: {diagnosis_data['icd10_code']})")

        session.commit()
        print(f"\n✅ Successfully populated {len(DIAGNOSIS_LIBRARY)} diagnoses with FHIR codes")

        # Print summary
        print("\n" + "="*60)
        print("DIAGNOSIS LIBRARY SUMMARY")
        print("="*60)
        total = session.query(DiagnosisContentMap).count()
        print(f"Total diagnoses in library: {total}")
        print("\nSample diagnoses:")
        for diag in session.query(DiagnosisContentMap).limit(5).all():
            print(f"  • {diag.diagnosis_display} (ICD-10: {diag.icd10_code}, SNOMED: {diag.snomed_code})")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Populating diagnosis library with FHIR codes...\n")
    populate_diagnoses()
