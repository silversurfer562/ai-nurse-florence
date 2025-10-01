#!/usr/bin/env python3
"""
Sample PDF Generation Script
Demonstrates how to generate patient education PDFs using AI Nurse Florence
"""

import sys
sys.path.insert(0, '.')

from services.pdf_generation_service import (
    generate_discharge_instructions,
    generate_medication_guide,
    generate_disease_education
)


def generate_discharge_example():
    """Generate a sample discharge instructions PDF"""
    print("📄 Generating Discharge Instructions PDF...")

    data = {
        'patient_name': 'John Smith',
        'primary_diagnosis': 'Community-Acquired Pneumonia',
        'medications': [
            {
                'name': 'Amoxicillin',
                'dosage': '500 mg',
                'frequency': 'Three times daily',
                'instructions': 'Take with food. Complete full 10-day course even if feeling better.'
            },
            {
                'name': 'Ibuprofen',
                'dosage': '400 mg',
                'frequency': 'Every 6 hours as needed',
                'instructions': 'For fever or pain. Take with food.'
            }
        ],
        'follow_up_appointments': [
            'See your primary care doctor in 7-10 days',
            'Chest X-ray in 6 weeks if symptoms persist',
            'Return to emergency room if symptoms worsen'
        ],
        'activity_restrictions': [
            'Rest and avoid strenuous activity for 1-2 weeks',
            'Stay home from work for at least 3-5 days',
            'Avoid crowded places until fever-free for 24 hours',
            'Get plenty of sleep (8-10 hours per night)'
        ],
        'diet_instructions': 'Drink plenty of fluids (8-10 glasses of water per day). Eat nutritious meals to support recovery. Avoid alcohol while taking antibiotics.',
        'warning_signs': [
            'Fever over 101°F (38.3°C) that does not improve with medication',
            'Difficulty breathing or shortness of breath that worsens',
            'Chest pain that is severe or worsening',
            'Coughing up blood or rust-colored mucus',
            'Confusion or altered mental status',
            'Inability to keep fluids down'
        ],
        'emergency_criteria': [
            'Severe difficulty breathing or gasping for air',
            'Blue lips or fingernails',
            'Severe chest pain',
            'Confusion or inability to stay awake',
            'Coughing up large amounts of blood'
        ],
        'wound_care': None,
        'equipment_needs': ['Thermometer for monitoring temperature'],
        'home_care_services': None
    }

    pdf_buffer = generate_discharge_instructions(data)

    filename = 'sample_discharge_instructions.pdf'
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print(f"✅ Discharge Instructions PDF created: {filename}")
    return filename


def generate_medication_example():
    """Generate a sample medication guide PDF"""
    print("\n💊 Generating Medication Guide PDF...")

    data = {
        'medication_name': 'Metformin',
        'dosage': '500 mg',
        'frequency': 'Twice daily with meals',
        'route': 'Oral',
        'purpose': 'Metformin is used to control high blood sugar levels in people with type 2 diabetes. Controlling blood sugar helps prevent kidney damage, blindness, nerve problems, loss of limbs, and sexual function problems.',
        'how_it_works': 'Metformin works by helping restore your body\'s proper response to insulin. It decreases the amount of sugar your liver makes and your stomach/intestines absorb. This helps lower blood sugar levels.',
        'special_instructions': [
            'Take with meals to reduce stomach upset',
            'Do not crush or chew extended-release tablets',
            'Swallow tablets whole with a full glass of water',
            'Check blood sugar regularly as directed by your doctor'
        ],
        'common_side_effects': [
            'Nausea or upset stomach (usually improves after a few weeks)',
            'Diarrhea',
            'Gas or bloating',
            'Stomach pain',
            'Metallic taste in mouth',
            'Loss of appetite'
        ],
        'serious_side_effects': [
            'Lactic acidosis (rare but serious): muscle pain, weakness, trouble breathing, stomach pain, feeling cold, dizzy, tired, or weak',
            'Signs of low blood sugar: shakiness, sweating, fast heartbeat, dizziness',
            'Vitamin B12 deficiency: numbness or tingling in hands/feet, unusual tiredness',
            'Allergic reaction: rash, itching, swelling, severe dizziness, trouble breathing'
        ],
        'food_interactions': [
            'Avoid excessive alcohol consumption - increases risk of lactic acidosis and low blood sugar',
            'Limit foods high in simple sugars',
            'Maintain consistent carbohydrate intake'
        ],
        'drug_interactions': [
            'Contrast dye used in imaging tests - stop metformin before and after procedure',
            'Diuretics (water pills)',
            'Corticosteroids',
            'Other diabetes medications'
        ],
        'storage_instructions': 'Store at room temperature between 68-77°F (20-25°C) away from light and moisture. Do not store in the bathroom. Keep out of reach of children and pets.',
        'missed_dose_instructions': 'If you miss a dose, take it as soon as you remember with food. If it is almost time for your next dose (within 2-3 hours), skip the missed dose and continue with your regular schedule. Do not take two doses at once.',
        'data_sources': ['FDA Drug Information', 'User-provided information']
    }

    pdf_buffer = generate_medication_guide(data)

    filename = 'sample_medication_guide_metformin.pdf'
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print(f"✅ Medication Guide PDF created: {filename}")
    return filename


def generate_disease_education_example():
    """Generate a sample disease education PDF"""
    print("\n🏥 Generating Disease Education PDF...")

    data = {
        'disease_name': 'Type 2 Diabetes',
        'what_it_is': 'Type 2 diabetes is a chronic condition that affects the way your body processes blood sugar (glucose). With type 2 diabetes, your body either resists the effects of insulin — a hormone that regulates the movement of sugar into your cells — or doesn\'t produce enough insulin to maintain normal glucose levels.',
        'causes': 'Type 2 diabetes develops when the body becomes resistant to insulin or when the pancreas is unable to produce enough insulin. Excess weight and inactivity are important factors. Risk factors include family history, age over 45, high blood pressure, abnormal cholesterol levels, and history of gestational diabetes.',
        'symptoms': [
            'Increased thirst and frequent urination',
            'Increased hunger',
            'Unintended weight loss',
            'Fatigue and weakness',
            'Blurred vision',
            'Slow-healing sores or frequent infections',
            'Darkened skin areas (often in armpits and neck)',
            'Numbness or tingling in hands or feet'
        ],
        'treatment_options': [
            'Blood glucose monitoring',
            'Oral medications (like metformin)',
            'Insulin therapy if needed',
            'Healthy eating plan',
            'Regular physical activity',
            'Weight management',
            'Regular medical check-ups'
        ],
        'self_care_tips': [
            'Check your blood sugar as directed by your healthcare provider',
            'Take all medications exactly as prescribed',
            'Keep a log of your blood sugar readings, meals, and activities',
            'Examine your feet daily for cuts, blisters, or sores',
            'Attend all scheduled medical appointments',
            'Wear medical identification (bracelet or necklace)',
            'Carry glucose tablets or candy for low blood sugar episodes'
        ],
        'lifestyle_modifications': [
            'Lose weight if overweight (even 5-10% weight loss helps)',
            'Get at least 150 minutes of moderate aerobic activity per week',
            'Include strength training 2-3 times per week',
            'Quit smoking',
            'Limit alcohol intake',
            'Manage stress through relaxation techniques',
            'Get 7-9 hours of sleep per night'
        ],
        'diet_recommendations': 'Focus on vegetables, fruits, whole grains, lean proteins, and healthy fats. Limit foods high in saturated fat, trans fat, cholesterol, and sodium. Count carbohydrates and space them evenly throughout the day. Work with a registered dietitian to create a personalized meal plan. Use the plate method: fill half your plate with non-starchy vegetables, one quarter with lean protein, and one quarter with carbohydrates.',
        'exercise_recommendations': 'Aim for 30 minutes of moderate aerobic activity (like brisk walking) most days of the week, totaling at least 150 minutes weekly. Include strength training exercises at least twice a week. Always check your blood sugar before and after exercise. Carry a snack in case of low blood sugar during activity. Stay hydrated and wear proper footwear.',
        'warning_signs': [
            'Blood sugar consistently over 180 mg/dL after meals',
            'Blood sugar under 70 mg/dL (hypoglycemia)',
            'Ketones in urine',
            'Persistent symptoms despite medication',
            'New or worsening vision problems',
            'Foot sores that won\'t heal',
            'Frequent infections'
        ],
        'emergency_symptoms': [
            'Blood sugar over 400 mg/dL',
            'Severe hypoglycemia with confusion or unconsciousness',
            'Fruity-smelling breath',
            'Rapid breathing or difficulty breathing',
            'Severe abdominal pain',
            'Extreme weakness or fatigue',
            'Loss of consciousness'
        ],
        'support_groups': [
            'American Diabetes Association local chapters',
            'JDRF (Juvenile Diabetes Research Foundation) support groups',
            'Hospital-based diabetes education programs',
            'Online communities and forums'
        ],
        'additional_resources': [
            'American Diabetes Association: www.diabetes.org',
            'CDC Diabetes Resources: www.cdc.gov/diabetes',
            'National Institute of Diabetes: www.niddk.nih.gov',
            'Diabetes Self-Management magazine',
            'MySugr app for tracking blood sugar',
            'Glucose Buddy app'
        ],
        'questions_to_ask': [
            'What is my target blood sugar range?',
            'How often should I check my blood sugar?',
            'What medications do I need and when should I take them?',
            'What should I do if I miss a dose of medication?',
            'How do I recognize and treat low blood sugar?',
            'What lifestyle changes should I make?',
            'How often should I have eye exams and foot checks?',
            'When should I call you or go to the emergency room?',
            'Should I see a diabetes educator or dietitian?',
            'What are my A1C goals and when should it be checked?'
        ],
        'data_sources': ['MedlinePlus (NIH)', 'American Diabetes Association', 'User-provided information']
    }

    pdf_buffer = generate_disease_education(data)

    filename = 'sample_disease_education_diabetes.pdf'
    with open(filename, 'wb') as f:
        f.write(pdf_buffer.getvalue())

    print(f"✅ Disease Education PDF created: {filename}")
    return filename


def main():
    """Generate all sample PDFs"""
    print("=" * 60)
    print("AI Nurse Florence - Patient Document PDF Generator")
    print("=" * 60)
    print()
    print("This script generates sample patient education PDFs.")
    print()

    try:
        # Generate each type of document
        discharge_file = generate_discharge_example()
        medication_file = generate_medication_example()
        disease_file = generate_disease_education_example()

        print("\n" + "=" * 60)
        print("✅ ALL PDFs GENERATED SUCCESSFULLY!")
        print("=" * 60)
        print("\nGenerated files:")
        print(f"  1. {discharge_file}")
        print(f"  2. {medication_file}")
        print(f"  3. {disease_file}")
        print("\nYou can now:")
        print("  - Open these PDFs to review the formatting")
        print("  - Print them for patient education")
        print("  - Use them as templates for your own documents")
        print("\nTo generate custom PDFs:")
        print("  - Use the API endpoints (see docs/PATIENT_DOCUMENT_GENERATION.md)")
        print("  - Modify this script with your own data")
        print("  - Integrate with your frontend application")
        print()

    except Exception as e:
        print(f"\n❌ Error generating PDFs: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
