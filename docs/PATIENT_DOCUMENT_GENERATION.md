# Patient Document Generation - PDF System

## Overview

AI Nurse Florence now supports generating professional, print-ready patient education materials as PDF documents. This feature enables healthcare providers to create customized discharge instructions, medication guides, and disease education materials.

## Features

✅ **Three Document Types:**
- Discharge Instructions
- Medication Guides
- Disease Education Materials

✅ **Professional Design:**
- Clean, print-ready layouts
- Color-coded warning boxes
- Easy-to-read formatting
- Medical disclaimer and generation date

✅ **Smart Auto-Population:**
- Integrates with MedlinePlus for disease information
- Can fetch FDA drug data (future enhancement)
- Reduces manual data entry

✅ **Multi-Language Support:**
- English (en)
- Spanish (es)
- Chinese Simplified (zh-CN)
- Chinese Traditional (zh-TW)

✅ **Reading Level Adaptation:**
- Basic (4th-6th grade)
- Intermediate (7th-9th grade)
- Advanced (10th+ grade)

✅ **Batch Generation:**
- Generate multiple documents at once
- Combine into single PDF packet
- Perfect for discharge packets

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/patient-documents
```

### Endpoints

1. **List Templates**: `GET /templates`
2. **Discharge Instructions**: `POST /discharge-instructions`
3. **Medication Guide**: `POST /medication-guide`
4. **Disease Education**: `POST /disease-education`
5. **Batch Generate**: `POST /batch-generate`

## Examples

### 1. Discharge Instructions

Generate comprehensive discharge instructions with medications, follow-up care, and warning signs.

```bash
curl -X POST "http://localhost:8000/api/v1/patient-documents/discharge-instructions" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Smith",
    "primary_diagnosis": "Pneumonia",
    "medications": [
      {
        "name": "Amoxicillin",
        "dosage": "500 mg",
        "frequency": "Three times daily",
        "instructions": "Take with food. Complete full course."
      },
      {
        "name": "Ibuprofen",
        "dosage": "400 mg",
        "frequency": "Every 6 hours as needed",
        "instructions": "For fever or pain"
      }
    ],
    "follow_up_appointments": [
      "See your primary care doctor in 7-10 days",
      "Return to ER if symptoms worsen"
    ],
    "activity_restrictions": [
      "Rest for 3-5 days",
      "Avoid strenuous activity for 2 weeks",
      "Stay hydrated"
    ],
    "warning_signs": [
      "Fever over 101°F that does not improve",
      "Difficulty breathing or shortness of breath",
      "Chest pain",
      "Coughing up blood"
    ],
    "emergency_criteria": [
      "Severe difficulty breathing",
      "Confusion or altered mental status",
      "Blue lips or fingernails"
    ],
    "language": "en",
    "reading_level": "intermediate"
  }' \
  --output discharge_instructions.pdf
```

**Response**: PDF file download

---

### 2. Medication Guide

Generate patient-friendly medication information.

```bash
curl -X POST "http://localhost:8000/api/v1/patient-documents/medication-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "medication_name": "Metformin",
    "dosage": "500 mg",
    "frequency": "Twice daily",
    "route": "oral",
    "purpose": "Controls blood sugar levels in type 2 diabetes",
    "how_it_works": "Metformin helps your body use insulin more effectively and reduces the amount of sugar your liver makes.",
    "special_instructions": [
      "Take with meals to reduce stomach upset",
      "Do not crush or chew extended-release tablets",
      "Swallow tablets whole"
    ],
    "common_side_effects": [
      "Nausea or upset stomach",
      "Diarrhea",
      "Gas or bloating",
      "Metallic taste in mouth"
    ],
    "serious_side_effects": [
      "Severe abdominal pain",
      "Unusual muscle pain or weakness",
      "Difficulty breathing",
      "Unusual tiredness"
    ],
    "food_interactions": [
      "Avoid excessive alcohol - increases risk of lactic acidosis"
    ],
    "storage_instructions": "Store at room temperature away from moisture and heat",
    "missed_dose_instructions": "Take as soon as you remember with food. If it is almost time for your next dose, skip the missed dose. Do not take two doses at once.",
    "auto_populate": true,
    "language": "en",
    "reading_level": "intermediate"
  }' \
  --output metformin_guide.pdf
```

**Response**: PDF file download

---

### 3. Disease Education Material

Generate comprehensive patient education about a disease or condition.

```bash
curl -X POST "http://localhost:8000/api/v1/patient-documents/disease-education" \
  -H "Content-Type: application/json" \
  -d '{
    "disease_name": "Type 2 Diabetes",
    "what_it_is": "Type 2 diabetes is a chronic condition that affects the way your body processes blood sugar (glucose). Your body either resists the effects of insulin or does not produce enough insulin to maintain normal glucose levels.",
    "causes": "Type 2 diabetes develops when the body becomes resistant to insulin or when the pancreas is unable to produce enough insulin. Risk factors include obesity, family history, age over 45, and physical inactivity.",
    "symptoms": [
      "Increased thirst and frequent urination",
      "Increased hunger",
      "Fatigue and weakness",
      "Blurred vision",
      "Slow-healing sores",
      "Frequent infections",
      "Darkened skin areas"
    ],
    "treatment_options": [
      "Blood sugar monitoring",
      "Medications (oral or insulin)",
      "Healthy eating plan",
      "Regular physical activity",
      "Weight management"
    ],
    "self_care_tips": [
      "Check blood sugar as directed by your doctor",
      "Take medications exactly as prescribed",
      "Keep a food and activity log",
      "Examine your feet daily for cuts or sores",
      "Schedule regular check-ups"
    ],
    "lifestyle_modifications": [
      "Lose weight if overweight (5-10% weight loss can make a big difference)",
      "Exercise at least 150 minutes per week",
      "Quit smoking",
      "Limit alcohol intake",
      "Manage stress"
    ],
    "diet_recommendations": "Focus on vegetables, whole grains, lean proteins, and healthy fats. Limit sugary foods and refined carbohydrates. Work with a dietitian to create a meal plan.",
    "exercise_recommendations": "Aim for 30 minutes of moderate aerobic activity most days. Include strength training 2-3 times per week. Check blood sugar before and after exercise.",
    "warning_signs": [
      "Blood sugar consistently over 180 mg/dL",
      "Blood sugar under 70 mg/dL",
      "Ketones in urine",
      "Persistent symptoms despite treatment"
    ],
    "emergency_symptoms": [
      "Blood sugar over 400 mg/dL",
      "Severe hypoglycemia with confusion",
      "Fruity-smelling breath",
      "Difficulty breathing",
      "Severe abdominal pain"
    ],
    "additional_resources": [
      "American Diabetes Association: diabetes.org",
      "CDC Diabetes resources: cdc.gov/diabetes"
    ],
    "questions_to_ask": [
      "What is my target blood sugar range?",
      "How often should I check my blood sugar?",
      "What medications do I need and when should I take them?",
      "What should I do if I miss a dose?",
      "When should I call you or go to the emergency room?"
    ],
    "auto_populate": true,
    "language": "en",
    "reading_level": "intermediate"
  }' \
  --output diabetes_education.pdf
```

**Response**: PDF file download

---

### 4. Batch Document Generation

Generate multiple documents at once (perfect for discharge packets).

```bash
curl -X POST "http://localhost:8000/api/v1/patient-documents/batch-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Jane Doe",
    "discharge_instructions": {
      "primary_diagnosis": "Heart Failure",
      "medications": [
        {
          "name": "Furosemide",
          "dosage": "40 mg",
          "frequency": "Once daily in morning",
          "instructions": "Take with food"
        }
      ],
      "warning_signs": [
        "Sudden weight gain (2-3 pounds in a day)",
        "Increased swelling in legs or abdomen",
        "Shortness of breath"
      ],
      "emergency_criteria": [
        "Severe difficulty breathing",
        "Chest pain"
      ]
    },
    "medication_guides": [
      {
        "medication_name": "Furosemide",
        "dosage": "40 mg",
        "frequency": "Once daily",
        "purpose": "Removes excess fluid from your body",
        "auto_populate": true
      },
      {
        "medication_name": "Carvedilol",
        "dosage": "25 mg",
        "frequency": "Twice daily",
        "purpose": "Helps your heart work more efficiently",
        "auto_populate": true
      }
    ],
    "disease_education": [
      {
        "disease_name": "Heart Failure",
        "auto_populate": true
      }
    ],
    "language": "en",
    "reading_level": "intermediate",
    "combine_into_packet": true
  }' \
  --output patient_discharge_packet.pdf
```

**Response**: Combined PDF packet with all documents

---

## Python Client Examples

### Using httpx (async)

```python
import httpx
import asyncio

async def generate_discharge_pdf():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/patient-documents/discharge-instructions",
            json={
                "primary_diagnosis": "Pneumonia",
                "medications": [
                    {
                        "name": "Amoxicillin",
                        "dosage": "500 mg",
                        "frequency": "Three times daily",
                        "instructions": "Take with food"
                    }
                ],
                "warning_signs": [
                    "Fever over 101°F",
                    "Difficulty breathing"
                ],
                "emergency_criteria": [
                    "Severe difficulty breathing"
                ]
            }
        )

        if response.status_code == 200:
            with open("discharge.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PDF generated successfully!")

asyncio.run(generate_discharge_pdf())
```

### Using requests (sync)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/patient-documents/medication-guide",
    json={
        "medication_name": "Metformin",
        "dosage": "500 mg",
        "frequency": "Twice daily",
        "purpose": "Controls blood sugar in type 2 diabetes",
        "auto_populate": True
    }
)

if response.status_code == 200:
    with open("metformin_guide.pdf", "wb") as f:
        f.write(response.content)
    print("✅ Medication guide created!")
```

---

## Document Format Features

### Discharge Instructions Include:
- Patient name (optional for privacy)
- Discharge date
- Primary diagnosis
- Medication table with dosages and instructions
- Follow-up appointment reminders
- Activity restrictions
- Diet instructions
- Wound care instructions (if applicable)
- Warning signs (color-coded amber box)
- Emergency criteria (color-coded red box)
- Home care services information
- Medical disclaimer footer

### Medication Guides Include:
- Medication name and dosing
- Purpose and how it works
- Special instructions
- Common side effects
- Serious side effects (color-coded warning)
- Food interactions
- Drug interactions (color-coded warning)
- Storage instructions
- Missed dose instructions
- Data sources
- Medical disclaimer footer

### Disease Education Materials Include:
- Disease explanation
- Causes and risk factors
- Symptoms checklist
- Treatment options
- Self-care tips
- Lifestyle modifications
- Diet and exercise recommendations
- Warning signs (color-coded)
- Emergency symptoms (color-coded)
- Support groups and resources
- Questions to ask healthcare provider
- Data sources
- Medical disclaimer footer

---

## Multi-Language Support

All documents support multiple languages:

```json
{
  "language": "es",  // Spanish
  "reading_level": "basic"
}
```

Available languages:
- `en` - English
- `es` - Spanish
- `zh-CN` - Chinese (Simplified)
- `zh-TW` - Chinese (Traditional)

---

## Reading Levels

Adapt content complexity:

- **basic**: 4th-6th grade reading level
- **intermediate**: 7th-9th grade reading level (default)
- **advanced**: 10th+ grade reading level

---

## Auto-Population

Enable automatic data fetching:

```json
{
  "auto_populate": true
}
```

**For Medication Guides:**
- Fetches FDA drug information (future enhancement)
- Populates side effects, interactions, storage

**For Disease Education:**
- Fetches MedlinePlus consumer health information
- Populates symptoms, treatment options, self-care tips

---

## Integration with Frontend

### React Example

```javascript
async function downloadDischargePDF(data) {
  const response = await fetch('/api/v1/patient-documents/discharge-instructions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'discharge_instructions.pdf';
    a.click();
  }
}
```

---

## Best Practices

1. **Always include warning signs and emergency criteria** for patient safety
2. **Use auto-populate when possible** to leverage authoritative medical databases
3. **Choose appropriate reading level** based on patient education and health literacy
4. **Generate batch packets for discharge** to provide complete information
5. **Include follow-up instructions** to ensure continuity of care
6. **Review generated PDFs** before giving to patients
7. **Keep patient name optional** for privacy when sharing examples

---

## Future Enhancements

🔮 **Planned Features:**
- QR codes linking to video instructions
- Medication images from FDA database
- Anatomical diagrams for disease education
- PDF merging for true batch packets
- HTML and plain text output formats
- Customizable branding (hospital logos, colors)
- E-signature fields for patient acknowledgment
- Translation API integration for better multi-language support
- Reading level analyzer to ensure appropriate complexity

---

## Technical Details

**PDF Generation Library**: ReportLab 4.0+
**Page Size**: US Letter (8.5" x 11")
**Margins**: 0.75 inches on all sides
**Fonts**: Helvetica (standard, widely compatible)
**Colors**:
- Primary: Blue (#2563EB)
- Warning: Red (#EF4444)
- Info: Amber (#F59E0B)
- Success: Green (#10B981)

---

## Troubleshooting

### PDF Not Downloading
- Check that ReportLab is installed: `pip install reportlab`
- Verify endpoint URL is correct
- Check response headers for errors

### Auto-Populate Not Working
- Ensure backend services are running
- Check MedlinePlus API connectivity
- Review server logs for errors

### Incorrect Language/Reading Level
- Verify language code is valid (en, es, zh-CN, zh-TW)
- Confirm reading_level is one of: basic, intermediate, advanced

---

## Support

For issues or questions:
- Review this documentation
- Check `/api/v1/patient-documents/templates` endpoint for available options
- Review FastAPI docs at `/docs` for interactive testing
- Submit issues on GitHub

---

**Generated by AI Nurse Florence - Supporting evidence-based nursing practice**
