"""
Populate Work Setting Presets
Creates pre-configured content for different work environments
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.content_settings import Base, WorkSettingPreset
from datetime import datetime

# Database setup
DATABASE_URL = "sqlite:///./ai_nurse_florence.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


WORK_SETTING_PRESETS = [
    {
        "id": "emergency_department",
        "work_setting": "emergency_department",
        "common_warning_signs": [
            "Fever over 101°F (38.3°C)",
            "Difficulty breathing or shortness of breath",
            "Severe pain (8-10 on pain scale)",
            "Chest pain",
            "Confusion or altered mental status",
            "Uncontrolled bleeding",
            "Signs of infection (redness, swelling, warmth)"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "5640",
                "medication_display": "Ibuprofen",
                "dosage_value": "400-600",
                "dosage_unit": "mg",
                "frequency_code": "Q6H",
                "frequency_display": "Every 6 hours as needed",
                "instructions": "Take with food"
            },
            {
                "medication_code_rxnorm": "161",
                "medication_display": "Acetaminophen",
                "dosage_value": "500-1000",
                "dosage_unit": "mg",
                "frequency_code": "Q6H",
                "frequency_display": "Every 6 hours as needed",
                "instructions": "Do not exceed 3000mg in 24 hours"
            }
        ],
        "common_diagnoses": [
            "Minor injuries and lacerations",
            "Acute pain",
            "Infections (URI, UTI)",
            "Dehydration",
            "Allergic reactions"
        ],
        "common_activity_restrictions": [
            "Rest for 24-48 hours",
            "Avoid strenuous activity until follow-up",
            "Return to ED if symptoms worsen",
            "Keep wound clean and dry"
        ],
        "common_diet_instructions": [
            "Stay well hydrated",
            "Resume normal diet as tolerated",
            "Avoid alcohol while taking medications"
        ],
        "default_follow_up_timeframe": "Follow up with your primary care doctor in 3-5 days",
        "default_reading_level": "basic",
        "default_language": "en"
    },
    {
        "id": "icu",
        "work_setting": "icu",
        "common_warning_signs": [
            "Any difficulty breathing",
            "Chest pain or pressure",
            "Confusion or difficulty waking",
            "Fever over 101°F",
            "Rapid heart rate (over 120 bpm)",
            "Low blood pressure (systolic under 90)",
            "Decreased urine output"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "20610",
                "medication_display": "Furosemide",
                "dosage_value": "20-40",
                "dosage_unit": "mg",
                "frequency_code": "QD-BID",
                "frequency_display": "Once or twice daily",
                "instructions": "Take in morning to avoid nighttime urination"
            }
        ],
        "common_diagnoses": [
            "Respiratory failure",
            "Sepsis",
            "Heart failure",
            "Multi-organ dysfunction",
            "Post-operative recovery"
        ],
        "common_activity_restrictions": [
            "Bed rest with gradual mobilization",
            "No heavy lifting for 4-6 weeks",
            "Physical therapy as prescribed",
            "Monitor vital signs closely"
        ],
        "common_diet_instructions": [
            "Restricted sodium diet (under 2000mg/day)",
            "Fluid restriction as prescribed",
            "Small, frequent meals"
        ],
        "default_follow_up_timeframe": "Follow up with specialist within 1 week of discharge",
        "default_reading_level": "intermediate",
        "default_language": "en"
    },
    {
        "id": "community_clinic",
        "work_setting": "community_clinic",
        "common_warning_signs": [
            "Symptoms that worsen or don't improve in 3-5 days",
            "Fever over 101°F that persists",
            "New or worsening pain",
            "Signs of infection",
            "Medication side effects"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "197361",
                "medication_display": "Lisinopril",
                "dosage_value": "10-20",
                "dosage_unit": "mg",
                "frequency_code": "QD",
                "frequency_display": "Once daily",
                "instructions": "Take at the same time each day"
            },
            {
                "medication_code_rxnorm": "860975",
                "medication_display": "Metformin",
                "dosage_value": "500-1000",
                "dosage_unit": "mg",
                "frequency_code": "BID",
                "frequency_display": "Twice daily",
                "instructions": "Take with meals"
            }
        ],
        "common_diagnoses": [
            "Hypertension",
            "Type 2 Diabetes",
            "Upper respiratory infections",
            "Minor injuries",
            "Chronic disease management"
        ],
        "common_activity_restrictions": [
            "Regular exercise (30 minutes most days)",
            "Maintain healthy weight",
            "Avoid smoking and limit alcohol"
        ],
        "common_diet_instructions": [
            "Heart-healthy diet (low sodium, low saturated fat)",
            "Diabetic diet if applicable",
            "Increase fruits and vegetables"
        ],
        "default_follow_up_timeframe": "Return for follow-up in 2-4 weeks",
        "default_reading_level": "basic",
        "default_language": "en"
    },
    {
        "id": "skilled_nursing",
        "work_setting": "skilled_nursing",
        "common_warning_signs": [
            "Change in mental status or confusion",
            "Difficulty swallowing",
            "Falls or dizziness",
            "Skin breakdown or pressure ulcers",
            "Signs of dehydration",
            "Medication adverse effects"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "432",
                "medication_display": "Aspirin",
                "dosage_value": "81",
                "dosage_unit": "mg",
                "frequency_code": "QD",
                "frequency_display": "Once daily",
                "instructions": "Take with food"
            }
        ],
        "common_diagnoses": [
            "Dementia/Alzheimer's",
            "Heart failure",
            "COPD",
            "Stroke recovery",
            "Post-surgical rehabilitation"
        ],
        "common_activity_restrictions": [
            "Use walker or assistive device as prescribed",
            "Physical therapy exercises daily",
            "Fall precautions (non-slip socks, call bell within reach)",
            "Supervised ambulation"
        ],
        "common_diet_instructions": [
            "Soft or pureed diet if swallowing difficulty",
            "Ensure adequate hydration (8 glasses daily)",
            "Nutritional supplements as ordered"
        ],
        "default_follow_up_timeframe": "Physician rounds weekly, call for concerns",
        "default_reading_level": "basic",
        "default_language": "en"
    },
    {
        "id": "outpatient_surgery",
        "work_setting": "outpatient_surgery",
        "common_warning_signs": [
            "Fever over 101°F",
            "Increased pain not controlled by medication",
            "Redness, swelling, or drainage from incision",
            "Nausea and vomiting preventing fluid intake",
            "Difficulty urinating",
            "Excessive bleeding or bruising"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "7052",
                "medication_display": "Hydrocodone-Acetaminophen",
                "dosage_value": "5-325",
                "dosage_unit": "mg",
                "frequency_code": "Q4-6H",
                "frequency_display": "Every 4-6 hours as needed",
                "instructions": "Take with food. May cause drowsiness. Do not drive."
            },
            {
                "medication_code_rxnorm": "309364",
                "medication_display": "Ondansetron (Zofran)",
                "dosage_value": "4-8",
                "dosage_unit": "mg",
                "frequency_code": "Q8H",
                "frequency_display": "Every 8 hours as needed for nausea",
                "instructions": "Dissolve under tongue"
            }
        ],
        "common_diagnoses": [
            "Post-operative status",
            "Minor surgical procedures",
            "Diagnostic procedures",
            "Pain management"
        ],
        "common_activity_restrictions": [
            "No driving for 24 hours after anesthesia",
            "No heavy lifting (over 10 lbs) for 1 week",
            "Keep surgical site clean and dry",
            "No swimming or soaking in tub until cleared by surgeon"
        ],
        "common_diet_instructions": [
            "Start with clear liquids, advance as tolerated",
            "Avoid alcohol for 24 hours",
            "Stay well hydrated"
        ],
        "default_follow_up_timeframe": "Follow up with surgeon in 7-10 days",
        "default_reading_level": "intermediate",
        "default_language": "en"
    },
    {
        "id": "pediatrics",
        "work_setting": "pediatrics",
        "common_warning_signs": [
            "Fever over 100.4°F in infants under 3 months",
            "Fever over 102°F in older children",
            "Difficulty breathing or rapid breathing",
            "Persistent vomiting or diarrhea",
            "Signs of dehydration (dry mouth, no tears, decreased urination)",
            "Lethargy or difficulty waking child",
            "Rash with fever"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "161",
                "medication_display": "Acetaminophen (Tylenol)",
                "dosage_value": "10-15",
                "dosage_unit": "mg/kg",
                "frequency_code": "Q4-6H",
                "frequency_display": "Every 4-6 hours as needed",
                "instructions": "Dose based on weight. Do not exceed 5 doses in 24 hours."
            },
            {
                "medication_code_rxnorm": "5640",
                "medication_display": "Ibuprofen (Advil/Motrin)",
                "dosage_value": "5-10",
                "dosage_unit": "mg/kg",
                "frequency_code": "Q6-8H",
                "frequency_display": "Every 6-8 hours as needed",
                "instructions": "For children over 6 months. Give with food."
            }
        ],
        "common_diagnoses": [
            "Upper respiratory infections",
            "Ear infections (otitis media)",
            "Gastroenteritis",
            "Minor injuries",
            "Well-child checks"
        ],
        "common_activity_restrictions": [
            "Rest until fever-free for 24 hours",
            "May return to school/daycare when symptoms improve",
            "Avoid contact sports until cleared by doctor (if injured)"
        ],
        "common_diet_instructions": [
            "Encourage fluid intake to prevent dehydration",
            "BRAT diet for upset stomach (Bananas, Rice, Applesauce, Toast)",
            "Resume normal diet as tolerated"
        ],
        "default_follow_up_timeframe": "Follow up with pediatrician in 3-5 days or sooner if worsening",
        "default_reading_level": "basic",
        "default_language": "en"
    },
    {
        "id": "home_health",
        "work_setting": "home_health",
        "common_warning_signs": [
            "New or worsening shortness of breath",
            "Chest pain",
            "Change in mental status",
            "Falls",
            "Uncontrolled pain",
            "Signs of infection (fever, redness, swelling)",
            "Medication problems or adverse effects"
        ],
        "common_medications": [
            {
                "medication_code_rxnorm": "855332",
                "medication_display": "Warfarin",
                "dosage_value": "Variable",
                "dosage_unit": "mg",
                "frequency_code": "QD",
                "frequency_display": "Once daily",
                "instructions": "Take at same time daily. INR monitoring required."
            }
        ],
        "common_diagnoses": [
            "Heart failure",
            "COPD",
            "Diabetes",
            "Wound care",
            "Post-hospitalization recovery"
        ],
        "common_activity_restrictions": [
            "Home safety assessment completed",
            "Use assistive devices as prescribed",
            "Energy conservation techniques",
            "Call nurse before making activity changes"
        ],
        "common_diet_instructions": [
            "Follow prescribed diet (diabetic, cardiac, renal, etc.)",
            "Meal preparation assistance if needed",
            "Monitor weight daily if heart failure"
        ],
        "default_follow_up_timeframe": "Nurse will visit as scheduled. Call for concerns between visits.",
        "default_reading_level": "basic",
        "default_language": "en"
    }
]


def populate_work_presets():
    """Populate work setting presets"""
    session = Session()

    try:
        for preset_data in WORK_SETTING_PRESETS:
            # Check if already exists
            existing = session.query(WorkSettingPreset).filter_by(
                id=preset_data["id"]
            ).first()

            if existing:
                print(f"✓ Work preset already exists: {preset_data['work_setting']}")
                continue

            # Create new preset
            preset = WorkSettingPreset(
                **preset_data,
                created_at=datetime.utcnow()
            )

            session.add(preset)
            print(f"✓ Added: {preset_data['work_setting']}")

        session.commit()
        print(f"\n✅ Successfully populated {len(WORK_SETTING_PRESETS)} work setting presets")

        # Print summary
        print("\n" + "="*60)
        print("WORK SETTING PRESETS SUMMARY")
        print("="*60)
        total = session.query(WorkSettingPreset).count()
        print(f"Total presets: {total}")
        print("\nAvailable work settings:")
        for preset in session.query(WorkSettingPreset).all():
            print(f"  • {preset.work_setting} (reading level: {preset.default_reading_level})")

    except Exception as e:
        session.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Populating work setting presets...\n")
    populate_work_presets()
