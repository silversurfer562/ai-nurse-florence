"""AI Nurse Florence - Practical Clinical Assistant
Focused on real nursing workflows and daily clinical needs.
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI(
    title="AI Nurse Florence - Clinical Assistant",
    description="Practical tools for nurses and healthcare professionals",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Educational disclaimer
CLINICAL_BANNER = "🏥 Clinical reference tool - Always follow facility protocols and consult providers for patient care decisions"

# Practical nursing data
COMMON_MEDICATIONS = {
    "tylenol": {
        "generic": "acetaminophen",
        "max_daily": "4000mg",
        "pediatric_dose": "10-15 mg/kg every 4-6 hours",
        "interactions": ["warfarin - monitor INR", "alcohol - hepatotoxicity risk"],
        "contraindications": ["severe liver disease", "allergy to acetaminophen"],
        "nursing_considerations": ["Monitor liver function", "Check temp 1hr after dose", "Max 5 days continuous use"]
    },
    "ibuprofen": {
        "generic": "ibuprofen",
        "max_daily": "3200mg (prescription) / 1200mg (OTC)",
        "pediatric_dose": "5-10 mg/kg every 6-8 hours",
        "interactions": ["warfarin - bleeding risk", "ACE inhibitors - reduced effect", "aspirin - GI bleeding"],
        "contraindications": ["kidney disease", "heart failure", "active GI bleeding", "3rd trimester pregnancy"],
        "nursing_considerations": ["Take with food", "Monitor BP", "Watch for GI bleeding", "Check kidney function"]
    },
    "metformin": {
        "generic": "metformin",
        "starting_dose": "500mg BID with meals",
        "max_daily": "2550mg",
        "interactions": ["contrast dye - hold 48hrs", "alcohol - lactic acidosis risk"],
        "contraindications": ["kidney disease (eGFR <30)", "liver disease", "heart failure"],
        "nursing_considerations": ["Monitor blood glucose", "Check kidney function", "Watch for lactic acidosis symptoms"]
    }
}

VITAL_SIGN_RANGES = {
    "adult": {
        "hr": {"normal": "60-100 bpm", "bradycardia": "<60", "tachycardia": ">100"},
        "bp": {"normal": "<120/80", "elevated": "120-129/<80", "stage1": "130-139/80-89", "stage2": "≥140/90"},
        "rr": {"normal": "12-20/min", "low": "<12", "high": ">20"},
        "temp": {"normal": "97.8-99.1°F (36.5-37.3°C)", "fever": ">100.4°F (38°C)", "hypothermia": "<95°F (35°C)"},
        "o2sat": {"normal": "≥95%", "concern": "90-94%", "critical": "<90%"}
    },
    "pediatric": {
        "hr": {"infant": "100-160", "toddler": "90-150", "preschool": "80-140", "school": "70-120"},
        "bp": {"varies": "Age-specific - use pediatric charts"},
        "rr": {"infant": "30-60", "toddler": "24-40", "preschool": "22-34", "school": "18-30"},
        "temp": {"same": "Same as adult ranges"},
        "o2sat": {"normal": "≥95%", "concern": "90-94%", "critical": "<90%"}
    }
}

@app.get("/")
async def home():
    return HTMLResponse("""
    <html>
        <head><title>AI Nurse Florence - Clinical Assistant</title></head>
        <body style="font-family: Arial; margin: 40px; line-height: 1.6;">
            <h1>🏥 AI Nurse Florence - Clinical Assistant</h1>
            <p><strong>Quick Clinical Tools for Nurses</strong></p>
            
            <h3>Available Tools:</h3>
            <ul>
                <li><a href="/docs">/docs</a> - Interactive API documentation</li>
                <li><a href="/medication/tylenol">/medication/{drug}</a> - Drug information & interactions</li>
                <li><a href="/vitals/adult">/vitals/{population}</a> - Normal vital sign ranges</li>
                <li><a href="/dosage-calc?weight=70&drug=tylenol">/dosage-calc</a> - Calculate medication doses</li>
                <li><a href="/assessment/chest-pain">/assessment/{symptom}</a> - Symptom assessment guides</li>
            </ul>
            
            <p><em>""" + CLINICAL_BANNER + """</em></p>
        </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ai-nurse-florence-clinical",
        "version": "2.0.0",
        "tools": ["medication lookup", "vital signs", "dosage calculator", "assessments"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/medication/{drug_name}")
async def medication_info(drug_name: str):
    """Get practical medication information for clinical use"""
    drug = drug_name.lower().replace(" ", "").replace("-", "")
    
    if drug in COMMON_MEDICATIONS:
        med_info = COMMON_MEDICATIONS[drug].copy()
        med_info["banner"] = CLINICAL_BANNER
        med_info["drug_searched"] = drug_name
        med_info["timestamp"] = datetime.now().isoformat()
        return med_info
    
    # Basic response for unknown medications
    return {
        "banner": CLINICAL_BANNER,
        "drug_searched": drug_name,
        "message": "Medication not in quick reference database",
        "recommendation": "Consult facility drug reference or pharmacist",
        "common_considerations": [
            "Check allergies and contraindications",
            "Verify dose and route",
            "Review drug interactions",
            "Monitor for side effects",
            "Document administration"
        ]
    }

@app.get("/vitals/{population}")
async def vital_signs(population: str):
    """Get normal vital sign ranges for clinical assessment"""
    pop = population.lower()
    
    if pop in VITAL_SIGN_RANGES:
        ranges = VITAL_SIGN_RANGES[pop].copy()
        return {
            "banner": CLINICAL_BANNER,
            "population": population,
            "timestamp": datetime.now().isoformat(),
            "vital_signs": ranges
        }
    
    return {
        "banner": CLINICAL_BANNER,
        "available_populations": list(VITAL_SIGN_RANGES.keys()),
        "message": f"Population '{population}' not found"
    }

@app.get("/dosage-calc")
async def dosage_calculator(
    weight: float = Query(..., description="Patient weight in kg"),
    drug: str = Query(..., description="Medication name"),
    age_group: str = Query("adult", description="adult or pediatric")
):
    """Calculate medication dosages based on weight"""
    
    drug_key = drug.lower().replace(" ", "").replace("-", "")
    
    if drug_key in COMMON_MEDICATIONS and age_group == "pediatric":
        med_info = COMMON_MEDICATIONS[drug_key]
        if "pediatric_dose" in med_info:
            # Parse pediatric dose (simplified for demo)
            if "mg/kg" in med_info["pediatric_dose"]:
                dose_range = med_info["pediatric_dose"].split()[0]  # Get "10-15"
                if "-" in dose_range:
                    min_dose, max_dose = map(float, dose_range.split("-"))
                    min_total = min_dose * weight
                    max_total = max_dose * weight
                    
                    return {
                        "banner": CLINICAL_BANNER,
                        "drug": drug,
                        "weight": f"{weight} kg",
                        "age_group": age_group,
                        "dose_range": f"{min_total:.1f} - {max_total:.1f} mg",
                        "frequency": med_info["pediatric_dose"].split("every")[-1].strip() if "every" in med_info["pediatric_dose"] else "as prescribed",
                        "max_daily": med_info.get("max_daily", "See prescribing information"),
                        "reminder": "Always verify calculations and follow facility protocols"
                    }
    
    return {
        "banner": CLINICAL_BANNER,
        "message": "Dosage calculation not available for this medication/age group",
        "recommendation": "Consult facility drug reference, pharmacist, or prescribing information",
        "safety_reminder": "Always double-check calculations with another nurse or pharmacist"
    }

@app.get("/assessment/{symptom}")
async def symptom_assessment(symptom: str):
    """Quick assessment guides for common symptoms"""
    
    assessments = {
        "chest-pain": {
            "immediate_actions": [
                "Assess airway, breathing, circulation",
                "Obtain vital signs",
                "Apply oxygen if SpO2 <94%",
                "Get 12-lead EKG within 10 minutes",
                "Establish IV access"
            ],
            "red_flags": [
                "Crushing chest pain",
                "Radiation to arm, jaw, back",
                "Shortness of breath",
                "Diaphoresis",
                "Nausea/vomiting with chest pain"
            ],
            "assessment_questions": [
                "When did pain start?",
                "Rate pain 1-10",
                "What makes it better/worse?",
                "Any previous cardiac history?",
                "Current medications?"
            ]
        },
        "shortness-of-breath": {
            "immediate_actions": [
                "Position upright/semi-Fowler's",
                "Check oxygen saturation",
                "Apply oxygen if needed",
                "Assess respiratory rate and effort",
                "Listen to lung sounds"
            ],
            "red_flags": [
                "SpO2 <90%",
                "Use of accessory muscles",
                "Cyanosis",
                "Unable to speak in full sentences",
                "Altered mental status"
            ],
            "assessment_questions": [
                "When did SOB start?",
                "At rest or with exertion?",
                "Any chest pain?",
                "History of COPD, asthma, CHF?",
                "Recent travel or surgery?"
            ]
        }
    }
    
    symptom_key = symptom.lower().replace(" ", "-")
    
    if symptom_key in assessments:
        result = assessments[symptom_key].copy()
        return {
            "banner": CLINICAL_BANNER,
            "symptom": symptom,
            "timestamp": datetime.now().isoformat(),
            "assessment": result
        }
    
    return {
        "banner": CLINICAL_BANNER,
        "message": f"Assessment guide for '{symptom}' not available",
        "available_assessments": list(assessments.keys()),
        "general_advice": "Follow facility protocols and contact provider for patient concerns"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
