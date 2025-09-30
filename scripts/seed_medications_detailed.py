"""
Seed medications database with comprehensive clinical information.
This provides OpenAI-level detail without requiring API calls.
"""

import asyncio
import json
import logging
import sys
import os
from uuid import uuid4

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import get_db_session, Medication, init_database
from sqlalchemy import select, delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive medication data with clinical details
DETAILED_MEDICATIONS = [
    {
        "name": "Aspirin",
        "generic": "Aspirin",
        "is_brand": False,
        "brand_names": ["Bayer", "Bufferin", "Ecotrin"],
        "drug_class": "Nonsteroidal Anti-Inflammatory Drug (NSAID) / Antiplatelet",
        "category": "Pain & Anti-inflammatory",
        "indication": "Pain relief, fever reduction, anti-inflammatory, and prevention of cardiovascular events through antiplatelet effects",
        "nursing_considerations": [
            "Monitor for signs of bleeding (bruising, petechiae, GI bleeding)",
            "Administer with food or milk to reduce GI upset",
            "Assess for history of peptic ulcer disease or bleeding disorders",
            "Monitor renal function in long-term use",
            "Check for aspirin allergy or sensitivity"
        ],
        "common_side_effects": [
            "Gastrointestinal upset, nausea",
            "Increased bleeding risk",
            "Tinnitus (ringing in ears) at high doses",
            "Heartburn and dyspepsia"
        ],
        "warnings": [
            "Contraindicated in active peptic ulcer disease",
            "Use caution with anticoagulants (increased bleeding risk)",
            "Avoid in children with viral infections (Reye's syndrome risk)",
            "May worsen asthma in aspirin-sensitive patients"
        ]
    },
    {
        "name": "Warfarin",
        "generic": "Warfarin",
        "is_brand": False,
        "brand_names": ["Coumadin", "Jantoven"],
        "drug_class": "Anticoagulant (Vitamin K antagonist)",
        "category": "Cardiovascular",
        "indication": "Prevention and treatment of thromboembolic disorders including deep vein thrombosis, pulmonary embolism, and stroke prevention in atrial fibrillation",
        "nursing_considerations": [
            "Monitor INR regularly (target usually 2.0-3.0)",
            "Assess for signs of bleeding (hematuria, melena, bruising)",
            "Educate patient on dietary vitamin K consistency",
            "Monitor for drug-drug interactions",
            "Ensure patient has purple top bracelet/alert card"
        ],
        "common_side_effects": [
            "Increased bleeding and bruising",
            "Nausea and vomiting",
            "Abdominal pain",
            "Skin necrosis (rare)"
        ],
        "warnings": [
            "Major bleeding risk - requires careful monitoring",
            "Numerous drug and food interactions",
            "Contraindicated in pregnancy (teratogenic)",
            "Avoid with active bleeding or high fall risk"
        ]
    },
    {
        "name": "Metformin",
        "generic": "Metformin",
        "is_brand": False,
        "brand_names": ["Glucophage", "Fortamet", "Glumetza"],
        "drug_class": "Biguanide (Antidiabetic)",
        "category": "Diabetes",
        "indication": "Type 2 diabetes mellitus management - first-line therapy to improve glycemic control",
        "nursing_considerations": [
            "Monitor blood glucose levels regularly",
            "Assess renal function before initiating and periodically (eGFR)",
            "Administer with meals to reduce GI side effects",
            "Hold before procedures with contrast dye",
            "Monitor for signs of lactic acidosis (rare but serious)"
        ],
        "common_side_effects": [
            "Gastrointestinal upset (diarrhea, nausea, abdominal discomfort)",
            "Metallic taste",
            "Vitamin B12 deficiency with long-term use",
            "Decreased appetite"
        ],
        "warnings": [
            "Contraindicated in severe renal impairment (eGFR <30)",
            "Risk of lactic acidosis (rare but fatal)",
            "Hold 48 hours before and after iodinated contrast procedures",
            "Use caution in heart failure and hepatic impairment"
        ]
    },
    {
        "name": "Lisinopril",
        "generic": "Lisinopril",
        "is_brand": False,
        "brand_names": ["Prinivil", "Zestril"],
        "drug_class": "ACE Inhibitor (Angiotensin-Converting Enzyme Inhibitor)",
        "category": "Cardiovascular",
        "indication": "Hypertension, heart failure, and post-myocardial infarction to improve survival",
        "nursing_considerations": [
            "Monitor blood pressure and heart rate",
            "Assess for dry persistent cough (common side effect)",
            "Check renal function and potassium levels periodically",
            "Take at same time daily, can be without food",
            "Monitor for angioedema (facial/tongue swelling)"
        ],
        "common_side_effects": [
            "Dry persistent cough",
            "Dizziness and hypotension",
            "Headache",
            "Fatigue",
            "Hyperkalemia"
        ],
        "warnings": [
            "Contraindicated in pregnancy (teratogenic)",
            "Risk of angioedema (life-threatening)",
            "Can cause hyperkalemia - avoid potassium supplements",
            "May worsen renal function in bilateral renal artery stenosis"
        ]
    },
    {
        "name": "Atorvastatin",
        "generic": "Atorvastatin",
        "is_brand": False,
        "brand_names": ["Lipitor"],
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "category": "Cardiovascular",
        "indication": "Hyperlipidemia and prevention of cardiovascular disease by lowering LDL cholesterol",
        "nursing_considerations": [
            "Monitor lipid panel (LDL, HDL, triglycerides)",
            "Assess liver function tests before and during therapy",
            "Check for muscle pain or weakness (myopathy)",
            "Administer in evening (cholesterol synthesis peaks at night)",
            "Avoid grapefruit juice (increases drug levels)"
        ],
        "common_side_effects": [
            "Muscle aches and pain (myalgia)",
            "Headache",
            "Nausea and abdominal pain",
            "Elevated liver enzymes",
            "Constipation or diarrhea"
        ],
        "warnings": [
            "Risk of rhabdomyolysis (rare but serious muscle breakdown)",
            "Monitor for muscle pain, weakness, dark urine",
            "Contraindicated in active liver disease",
            "Use caution with other myopathic drugs"
        ]
    },
    {
        "name": "Levothyroxine",
        "generic": "Levothyroxine",
        "is_brand": False,
        "brand_names": ["Synthroid", "Levoxyl", "Unithroid"],
        "drug_class": "Thyroid Hormone Replacement",
        "category": "Endocrine",
        "indication": "Hypothyroidism and thyroid hormone replacement therapy",
        "nursing_considerations": [
            "Monitor TSH levels to assess therapeutic effectiveness",
            "Administer on empty stomach, 30-60 minutes before breakfast",
            "Maintain consistent brand (bioavailability varies)",
            "Monitor for signs of hyperthyroidism (overdose)",
            "Space from calcium, iron, antacids by 4 hours"
        ],
        "common_side_effects": [
            "Hair loss (temporary, at initiation)",
            "Weight changes",
            "Headache",
            "Most side effects indicate overdose"
        ],
        "warnings": [
            "Do not use for weight loss (dangerous)",
            "Can precipitate cardiac ischemia in CAD patients",
            "Increases effects of warfarin (monitor INR)",
            "Many drug interactions affecting absorption"
        ]
    },
    {
        "name": "Omeprazole",
        "generic": "Omeprazole",
        "is_brand": False,
        "brand_names": ["Prilosec"],
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "category": "Gastrointestinal",
        "indication": "Gastroesophageal reflux disease (GERD), peptic ulcer disease, and erosive esophagitis",
        "nursing_considerations": [
            "Administer 30-60 minutes before meals",
            "Swallow capsules whole (do not crush)",
            "Monitor for Clostridium difficile infection risk",
            "Assess bone density with long-term use",
            "May take 1-4 days for full effect"
        ],
        "common_side_effects": [
            "Headache",
            "Abdominal pain and nausea",
            "Diarrhea or constipation",
            "Dizziness"
        ],
        "warnings": [
            "Long-term use increases fracture risk (hip, wrist, spine)",
            "May mask symptoms of gastric cancer",
            "Decreased magnesium with prolonged use",
            "Increases risk of C. difficile infection"
        ]
    },
    {
        "name": "Amlodipine",
        "generic": "Amlodipine",
        "is_brand": False,
        "brand_names": ["Norvasc"],
        "drug_class": "Calcium Channel Blocker (Dihydropyridine)",
        "category": "Cardiovascular",
        "indication": "Hypertension and chronic stable angina",
        "nursing_considerations": [
            "Monitor blood pressure and heart rate",
            "Assess for peripheral edema (especially ankles)",
            "Can be taken without regard to meals",
            "May take 2 weeks for full antihypertensive effect",
            "Monitor liver function in hepatic impairment"
        ],
        "common_side_effects": [
            "Peripheral edema (swelling of ankles/feet)",
            "Headache and dizziness",
            "Flushing",
            "Fatigue",
            "Palpitations"
        ],
        "warnings": [
            "Use caution in severe aortic stenosis",
            "May worsen heart failure in some patients",
            "Dose adjustment needed in hepatic impairment",
            "Grapefruit juice may increase drug levels"
        ]
    },
    {
        "name": "Metoprolol",
        "generic": "Metoprolol",
        "is_brand": False,
        "brand_names": ["Lopressor", "Toprol-XL"],
        "drug_class": "Beta-Blocker (Selective Beta-1)",
        "category": "Cardiovascular",
        "indication": "Hypertension, angina, heart failure, and post-myocardial infarction",
        "nursing_considerations": [
            "Monitor blood pressure and heart rate (hold if HR <60)",
            "Do not stop abruptly (risk of rebound hypertension)",
            "Assess for signs of heart failure exacerbation",
            "Take with or immediately after meals",
            "Monitor blood glucose in diabetics (may mask hypoglycemia)"
        ],
        "common_side_effects": [
            "Bradycardia (slow heart rate)",
            "Fatigue and dizziness",
            "Depression",
            "Cold extremities",
            "Shortness of breath"
        ],
        "warnings": [
            "Contraindicated in severe bradycardia, heart block",
            "Use caution in asthma/COPD (can cause bronchospasm)",
            "Masks symptoms of hypoglycemia in diabetes",
            "Taper gradually when discontinuing"
        ]
    },
    {
        "name": "Albuterol",
        "generic": "Albuterol",
        "is_brand": False,
        "brand_names": ["Proventil", "Ventolin", "ProAir"],
        "drug_class": "Short-Acting Beta-2 Agonist (SABA) Bronchodilator",
        "category": "Respiratory",
        "indication": "Acute bronchospasm in asthma and COPD, exercise-induced bronchospasm prevention",
        "nursing_considerations": [
            "Teach proper inhaler technique",
            "Monitor respiratory rate and breath sounds",
            "Assess for tremors and tachycardia",
            "Rinse mouth after use (reduces thrush risk)",
            "Monitor for overuse (>2 times/week indicates poor control)"
        ],
        "common_side_effects": [
            "Tremors (especially hands)",
            "Tachycardia and palpitations",
            "Nervousness and anxiety",
            "Headache",
            "Hypokalemia at high doses"
        ],
        "warnings": [
            "Overuse indicates worsening asthma (seek medical care)",
            "Use caution in cardiovascular disease",
            "May cause paradoxical bronchospasm (rare)",
            "Monitor potassium in high-dose or nebulizer use"
        ]
    },
    {
        "name": "Furosemide",
        "generic": "Furosemide",
        "is_brand": False,
        "brand_names": ["Lasix"],
        "drug_class": "Loop Diuretic",
        "category": "Cardiovascular",
        "indication": "Edema associated with heart failure, hepatic cirrhosis, and renal disease; hypertension",
        "nursing_considerations": [
            "Monitor fluid balance (intake/output, daily weights)",
            "Assess electrolytes especially potassium and magnesium",
            "Monitor blood pressure (orthostatic hypotension risk)",
            "Administer in morning to avoid nocturia",
            "Assess hearing (ototoxicity risk with rapid IV administration)"
        ],
        "common_side_effects": [
            "Hypokalemia and other electrolyte imbalances",
            "Dehydration and hypotension",
            "Dizziness",
            "Increased urination",
            "Hyperglycemia and hyperuricemia"
        ],
        "warnings": [
            "Monitor potassium levels - supplement as needed",
            "Risk of ototoxicity especially with rapid IV push",
            "Use caution with other nephrotoxic drugs",
            "May worsen gout or diabetes"
        ]
    },
    {
        "name": "Gabapentin",
        "generic": "Gabapentin",
        "is_brand": False,
        "brand_names": ["Neurontin", "Gralise"],
        "drug_class": "Anticonvulsant / Neuropathic Pain Agent",
        "category": "Neurological",
        "indication": "Neuropathic pain, postherpetic neuralgia, and adjunctive therapy for partial seizures",
        "nursing_considerations": [
            "Taper gradually when discontinuing (seizure risk)",
            "Monitor for sedation and dizziness",
            "Assess renal function (dose adjustment needed)",
            "May take with or without food",
            "Monitor for mood changes and suicidal ideation"
        ],
        "common_side_effects": [
            "Dizziness and somnolence",
            "Peripheral edema",
            "Fatigue and ataxia",
            "Weight gain",
            "Blurred vision"
        ],
        "warnings": [
            "Increased risk of suicidal thoughts/behavior",
            "Do not stop abruptly - taper to prevent seizures",
            "Dose adjustment required in renal impairment",
            "May cause severe skin reactions (rare)"
        ]
    },
    {
        "name": "Prednisone",
        "generic": "Prednisone",
        "is_brand": False,
        "brand_names": ["Deltasone", "Rayos"],
        "drug_class": "Corticosteroid",
        "category": "Endocrine",
        "indication": "Anti-inflammatory and immunosuppressant for various conditions including asthma, arthritis, allergic reactions",
        "nursing_considerations": [
            "Administer with food to reduce GI upset",
            "Monitor blood glucose (hyperglycemia risk)",
            "Assess for signs of infection (immunosuppression)",
            "Monitor blood pressure and weight",
            "Taper dose gradually - never stop abruptly"
        ],
        "common_side_effects": [
            "Increased appetite and weight gain",
            "Hyperglycemia",
            "Insomnia and mood changes",
            "Fluid retention and edema",
            "Increased infection risk"
        ],
        "warnings": [
            "Long-term use: osteoporosis, cataracts, adrenal suppression",
            "Never stop abruptly - must taper to prevent adrenal crisis",
            "Avoid live vaccines while on therapy",
            "Masks signs of infection"
        ]
    },
    {
        "name": "Losartan",
        "generic": "Losartan",
        "is_brand": False,
        "brand_names": ["Cozaar"],
        "drug_class": "Angiotensin II Receptor Blocker (ARB)",
        "category": "Cardiovascular",
        "indication": "Hypertension, diabetic nephropathy, and stroke risk reduction in hypertensive patients with left ventricular hypertrophy",
        "nursing_considerations": [
            "Monitor blood pressure and heart rate",
            "Check renal function and potassium levels",
            "Can be taken without regard to meals",
            "Monitor for signs of angioedema (rare)",
            "Assess for dizziness especially with first dose"
        ],
        "common_side_effects": [
            "Dizziness and hypotension",
            "Hyperkalemia",
            "Fatigue",
            "Upper respiratory infection",
            "Back pain"
        ],
        "warnings": [
            "Contraindicated in pregnancy (teratogenic)",
            "Risk of hyperkalemia - avoid potassium supplements",
            "May worsen renal function in bilateral renal artery stenosis",
            "Use caution in volume-depleted patients"
        ]
    },
    {
        "name": "Hydrochlorothiazide",
        "generic": "Hydrochlorothiazide",
        "is_brand": False,
        "brand_names": ["Microzide", "HCTZ"],
        "drug_class": "Thiazide Diuretic",
        "category": "Cardiovascular",
        "indication": "Hypertension and edema",
        "nursing_considerations": [
            "Monitor electrolytes especially potassium",
            "Assess fluid balance and daily weights",
            "Administer in morning to avoid nocturia",
            "Monitor blood glucose and uric acid levels",
            "Check blood pressure regularly"
        ],
        "common_side_effects": [
            "Hypokalemia",
            "Hypotension and dizziness",
            "Increased urination",
            "Hyperglycemia",
            "Photosensitivity"
        ],
        "warnings": [
            "Monitor and replace potassium as needed",
            "May worsen gout or diabetes",
            "Use sunscreen (photosensitivity)",
            "Can cause severe electrolyte imbalances"
        ]
    },
    {
        "name": "Sertraline",
        "generic": "Sertraline",
        "is_brand": False,
        "brand_names": ["Zoloft"],
        "drug_class": "Selective Serotonin Reuptake Inhibitor (SSRI)",
        "category": "Psychiatric",
        "indication": "Depression, anxiety disorders, OCD, PTSD, panic disorder, and PMDD",
        "nursing_considerations": [
            "Monitor for suicidal ideation especially in young adults",
            "Take with food to reduce nausea",
            "May take 4-6 weeks for full therapeutic effect",
            "Assess for serotonin syndrome",
            "Monitor for activation/mania in bipolar disorder"
        ],
        "common_side_effects": [
            "Nausea and diarrhea",
            "Sexual dysfunction",
            "Insomnia or drowsiness",
            "Dry mouth",
            "Increased sweating"
        ],
        "warnings": [
            "Black box warning: increased suicide risk in young adults",
            "Taper gradually to avoid discontinuation syndrome",
            "Risk of serotonin syndrome with other serotonergic drugs",
            "May increase bleeding risk especially with NSAIDs/anticoagulants"
        ]
    },
    {
        "name": "Insulin Glargine",
        "generic": "Insulin Glargine",
        "is_brand": False,
        "brand_names": ["Lantus", "Basaglar", "Toujeo"],
        "drug_class": "Long-Acting Insulin",
        "category": "Diabetes",
        "indication": "Type 1 and type 2 diabetes mellitus for glycemic control",
        "nursing_considerations": [
            "Monitor blood glucose before and after administration",
            "Administer subcutaneously at same time daily",
            "Do not mix with other insulins",
            "Rotate injection sites to prevent lipodystrophy",
            "Assess for signs of hypoglycemia"
        ],
        "common_side_effects": [
            "Hypoglycemia",
            "Weight gain",
            "Injection site reactions",
            "Lipodystrophy",
            "Peripheral edema"
        ],
        "warnings": [
            "Never administer IV (SC only)",
            "Do not mix with other insulins in same syringe",
            "Monitor closely during illness or stress",
            "Educate on hypoglycemia recognition and treatment"
        ]
    },
    {
        "name": "Clopidogrel",
        "generic": "Clopidogrel",
        "is_brand": False,
        "brand_names": ["Plavix"],
        "drug_class": "Antiplatelet Agent (P2Y12 Inhibitor)",
        "category": "Cardiovascular",
        "indication": "Prevention of atherothrombotic events in patients with recent MI, stroke, or peripheral arterial disease; acute coronary syndrome",
        "nursing_considerations": [
            "Monitor for signs of bleeding",
            "Can be taken without regard to meals",
            "Assess platelet function if bleeding occurs",
            "Hold 5-7 days before elective surgery",
            "Monitor for signs of thrombotic thrombocytopenic purpura (rare)"
        ],
        "common_side_effects": [
            "Increased bleeding risk",
            "Bruising",
            "Nosebleeds",
            "Gastrointestinal bleeding",
            "Headache"
        ],
        "warnings": [
            "Major bleeding risk - use caution with other anticoagulants",
            "Reduced effectiveness in poor CYP2C19 metabolizers",
            "Avoid concurrent use with omeprazole (reduces efficacy)",
            "Risk of thrombotic thrombocytopenic purpura (rare but serious)"
        ]
    },
    {
        "name": "Tramadol",
        "generic": "Tramadol",
        "is_brand": False,
        "brand_names": ["Ultram", "ConZip"],
        "drug_class": "Opioid Analgesic (Centrally Acting)",
        "category": "Pain & Anti-inflammatory",
        "indication": "Moderate to moderately severe pain",
        "nursing_considerations": [
            "Assess pain intensity and characteristics",
            "Monitor for respiratory depression",
            "Can be taken with or without food",
            "Assess for substance abuse history",
            "Monitor for serotonin syndrome with SSRIs"
        ],
        "common_side_effects": [
            "Nausea and vomiting",
            "Dizziness and drowsiness",
            "Constipation",
            "Headache",
            "Dry mouth"
        ],
        "warnings": [
            "Seizure risk especially at high doses",
            "Serotonin syndrome risk with SSRIs/SNRIs",
            "Abuse and addiction potential (Schedule IV)",
            "Respiratory depression risk"
        ]
    },
    {
        "name": "Amoxicillin",
        "generic": "Amoxicillin",
        "is_brand": False,
        "brand_names": ["Amoxil", "Moxatag"],
        "drug_class": "Aminopenicillin Antibiotic",
        "category": "Antibiotics",
        "indication": "Bacterial infections including respiratory tract, ear, nose, throat, skin, and urinary tract infections",
        "nursing_considerations": [
            "Assess for penicillin allergy before administration",
            "Take full course even if feeling better",
            "Can be taken with or without food",
            "Monitor for signs of allergic reaction",
            "Assess for diarrhea (C. difficile risk)"
        ],
        "common_side_effects": [
            "Diarrhea and nausea",
            "Rash (not always allergic)",
            "Yeast infections",
            "Vomiting",
            "Headache"
        ],
        "warnings": [
            "Cross-reactivity with penicillin allergy",
            "May reduce effectiveness of oral contraceptives",
            "Risk of C. difficile-associated diarrhea",
            "Serious skin reactions possible (rare)"
        ]
    },
    {
        "name": "Pantoprazole",
        "generic": "Pantoprazole",
        "is_brand": False,
        "brand_names": ["Protonix"],
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "category": "Gastrointestinal",
        "indication": "GERD, erosive esophagitis, and pathological hypersecretory conditions",
        "nursing_considerations": [
            "Administer 30 minutes before meals",
            "Swallow tablets whole (do not crush)",
            "Monitor for C. difficile infection",
            "Assess bone density with long-term use",
            "Check magnesium with prolonged therapy"
        ],
        "common_side_effects": [
            "Headache",
            "Diarrhea",
            "Nausea",
            "Abdominal pain",
            "Dizziness"
        ],
        "warnings": [
            "Long-term use increases fracture risk",
            "May mask gastric cancer symptoms",
            "Hypomagnesemia with prolonged use",
            "Increased C. difficile infection risk"
        ]
    },
    {
        "name": "Duloxetine",
        "generic": "Duloxetine",
        "is_brand": False,
        "brand_names": ["Cymbalta"],
        "drug_class": "Serotonin-Norepinephrine Reuptake Inhibitor (SNRI)",
        "category": "Psychiatric",
        "indication": "Depression, generalized anxiety disorder, diabetic neuropathy, fibromyalgia, chronic musculoskeletal pain",
        "nursing_considerations": [
            "Monitor for suicidal ideation",
            "Swallow capsules whole",
            "May take 4-6 weeks for full effect",
            "Monitor blood pressure (may increase)",
            "Assess liver function (hepatotoxicity risk)"
        ],
        "common_side_effects": [
            "Nausea",
            "Dry mouth",
            "Drowsiness or insomnia",
            "Constipation",
            "Decreased appetite"
        ],
        "warnings": [
            "Black box warning: suicide risk in young adults",
            "Contraindicated in uncontrolled narrow-angle glaucoma",
            "Hepatotoxicity - monitor liver function",
            "Taper gradually to avoid discontinuation syndrome"
        ]
    },
    {
        "name": "Montelukast",
        "generic": "Montelukast",
        "is_brand": False,
        "brand_names": ["Singulair"],
        "drug_class": "Leukotriene Receptor Antagonist",
        "category": "Respiratory",
        "indication": "Asthma prophylaxis and treatment of allergic rhinitis",
        "nursing_considerations": [
            "Take once daily in evening",
            "Not for acute asthma attacks",
            "Monitor for neuropsychiatric events",
            "Can be taken with or without food",
            "Continue even when asymptomatic"
        ],
        "common_side_effects": [
            "Headache",
            "Upper respiratory infection",
            "Abdominal pain",
            "Diarrhea",
            "Fatigue"
        ],
        "warnings": [
            "Neuropsychiatric events: agitation, depression, suicidal thoughts",
            "Not a rescue inhaler - do not use for acute symptoms",
            "Rare: eosinophilic conditions and vasculitis",
            "Monitor for mood/behavior changes"
        ]
    },
    {
        "name": "Escitalopram",
        "generic": "Escitalopram",
        "is_brand": False,
        "brand_names": ["Lexapro"],
        "drug_class": "Selective Serotonin Reuptake Inhibitor (SSRI)",
        "category": "Psychiatric",
        "indication": "Major depressive disorder and generalized anxiety disorder",
        "nursing_considerations": [
            "Monitor for suicidal ideation especially initially",
            "Can be taken with or without food",
            "Full effect may take 4-6 weeks",
            "Monitor for serotonin syndrome",
            "Check QTc interval (can prolong)"
        ],
        "common_side_effects": [
            "Nausea",
            "Insomnia or drowsiness",
            "Sexual dysfunction",
            "Dry mouth",
            "Increased sweating"
        ],
        "warnings": [
            "Black box warning: suicide risk in young adults",
            "QTc prolongation - use caution with other QT-prolonging drugs",
            "Serotonin syndrome risk",
            "Taper gradually when discontinuing"
        ]
    },
    {
        "name": "Azithromycin",
        "generic": "Azithromycin",
        "is_brand": False,
        "brand_names": ["Zithromax", "Z-Pak"],
        "drug_class": "Macrolide Antibiotic",
        "category": "Antibiotics",
        "indication": "Respiratory tract infections, skin infections, sexually transmitted infections",
        "nursing_considerations": [
            "Can be taken with or without food",
            "Usually 5-day course (Z-Pak)",
            "Monitor for QT prolongation",
            "Assess for macrolide allergy",
            "Complete full course of therapy"
        ],
        "common_side_effects": [
            "Diarrhea and nausea",
            "Abdominal pain",
            "Vomiting",
            "Headache",
            "Dizziness"
        ],
        "warnings": [
            "QT prolongation - avoid in patients with risk factors",
            "May worsen myasthenia gravis",
            "C. difficile-associated diarrhea risk",
            "Hepatotoxicity (rare)"
        ]
    },
    {
        "name": "Rosuvastatin",
        "generic": "Rosuvastatin",
        "is_brand": False,
        "brand_names": ["Crestor"],
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "category": "Cardiovascular",
        "indication": "Hyperlipidemia and prevention of cardiovascular disease",
        "nursing_considerations": [
            "Monitor lipid panel periodically",
            "Assess for muscle pain or weakness",
            "Check liver function tests",
            "Can be taken any time of day",
            "Avoid grapefruit juice"
        ],
        "common_side_effects": [
            "Myalgia (muscle pain)",
            "Headache",
            "Abdominal pain",
            "Nausea",
            "Constipation"
        ],
        "warnings": [
            "Rhabdomyolysis risk (rare but serious)",
            "Monitor for muscle pain, weakness, dark urine",
            "Contraindicated in active liver disease",
            "Dose adjustment needed in Asian patients"
        ]
    },
    {
        "name": "Carvedilol",
        "generic": "Carvedilol",
        "is_brand": False,
        "brand_names": ["Coreg", "Coreg CR"],
        "drug_class": "Non-selective Beta-Blocker with Alpha-Blocking Activity",
        "category": "Cardiovascular",
        "indication": "Heart failure, hypertension, and post-myocardial infarction left ventricular dysfunction",
        "nursing_considerations": [
            "Monitor heart rate and blood pressure",
            "Take with food to slow absorption",
            "Start low and titrate slowly",
            "Do not stop abruptly",
            "Monitor for signs of heart failure worsening"
        ],
        "common_side_effects": [
            "Dizziness and hypotension",
            "Bradycardia",
            "Fatigue",
            "Diarrhea",
            "Weight gain"
        ],
        "warnings": [
            "Contraindicated in decompensated heart failure",
            "Use caution in asthma/COPD",
            "May mask hypoglycemia symptoms",
            "Taper gradually when discontinuing"
        ]
    },
    {
        "name": "Trazodone",
        "generic": "Trazodone",
        "is_brand": False,
        "brand_names": ["Desyrel"],
        "drug_class": "Serotonin Antagonist and Reuptake Inhibitor (Antidepressant)",
        "category": "Psychiatric",
        "indication": "Depression and off-label for insomnia",
        "nursing_considerations": [
            "Take with food to enhance absorption",
            "Commonly used at low doses for sleep",
            "Monitor for orthostatic hypotension",
            "Assess for suicidal ideation",
            "Usually taken at bedtime for sedation"
        ],
        "common_side_effects": [
            "Drowsiness and sedation",
            "Dizziness and orthostatic hypotension",
            "Dry mouth",
            "Blurred vision",
            "Headache"
        ],
        "warnings": [
            "Priapism (rare but requires immediate medical attention)",
            "Serotonin syndrome risk with other serotonergic drugs",
            "QT prolongation possible",
            "May increase suicide risk in young adults"
        ]
    },
    {
        "name": "Spironolactone",
        "generic": "Spironolactone",
        "is_brand": False,
        "brand_names": ["Aldactone"],
        "drug_class": "Potassium-Sparing Diuretic / Aldosterone Antagonist",
        "category": "Cardiovascular",
        "indication": "Heart failure, hypertension, edema, primary hyperaldosteronism",
        "nursing_considerations": [
            "Monitor potassium levels closely",
            "Assess renal function regularly",
            "Monitor blood pressure",
            "May take 2 weeks for full antihypertensive effect",
            "Take with food to enhance absorption"
        ],
        "common_side_effects": [
            "Hyperkalemia",
            "Gynecomastia in males",
            "Menstrual irregularities",
            "Dizziness",
            "Headache"
        ],
        "warnings": [
            "Hyperkalemia risk - avoid potassium supplements",
            "Contraindicated in renal failure and hyperkalemia",
            "May cause feminization effects (anti-androgenic)",
            "Monitor potassium especially with ACE inhibitors/ARBs"
        ]
    },
    {
        "name": "Ciprofloxacin",
        "generic": "Ciprofloxacin",
        "is_brand": False,
        "brand_names": ["Cipro"],
        "drug_class": "Fluoroquinolone Antibiotic",
        "category": "Antibiotics",
        "indication": "Bacterial infections including UTIs, respiratory infections, skin infections, bone/joint infections",
        "nursing_considerations": [
            "Take 2 hours before or 6 hours after antacids/supplements",
            "Encourage fluid intake",
            "Monitor for tendon pain or swelling",
            "Avoid excessive sun exposure",
            "Complete full course of therapy"
        ],
        "common_side_effects": [
            "Nausea and diarrhea",
            "Headache",
            "Dizziness",
            "Abdominal pain",
            "Photosensitivity"
        ],
        "warnings": [
            "Black box warning: tendon rupture, peripheral neuropathy, CNS effects",
            "May worsen myasthenia gravis",
            "QT prolongation risk",
            "Avoid in pregnancy and children (cartilage damage)"
        ]
    },
    {
        "name": "Ranitidine",
        "generic": "Ranitidine",
        "is_brand": False,
        "brand_names": ["Zantac"],
        "drug_class": "H2 Receptor Antagonist",
        "category": "Gastrointestinal",
        "indication": "GERD, peptic ulcer disease, erosive esophagitis (NOTE: Withdrawn from market in 2020 due to NDMA contamination)",
        "nursing_considerations": [
            "ALERT: Product recalled in 2020 - included for reference only",
            "Can be taken with or without food",
            "Less effective than PPIs for GERD",
            "Monitor for drug interactions",
            "Dose adjustment in renal impairment"
        ],
        "common_side_effects": [
            "Headache",
            "Constipation or diarrhea",
            "Nausea",
            "Dizziness",
            "Fatigue"
        ],
        "warnings": [
            "RECALLED from market due to NDMA contamination",
            "Historical information only - not currently available",
            "May mask gastric cancer symptoms",
            "Elderly: increased risk of confusion"
        ]
    }
]

async def seed_detailed_medications():
    """Seed database with detailed medication information."""
    logger.info("🔄 Starting detailed medication database seeding...")

    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")

        async for session in get_db_session():
            try:
                # Check existing medications
                result = await session.execute(select(Medication))
                existing = result.scalars().all()

                if len(existing) > 0:
                    logger.info(f"⚠️ Database already contains {len(existing)} medications.")
                    logger.info("Clearing and re-seeding with detailed data...")
                    await session.execute(delete(Medication))
                    await session.commit()
                    logger.info("✅ Cleared existing medications")

                # Insert detailed medications
                medications_created = 0
                for med_data in DETAILED_MEDICATIONS:
                    medication = Medication(
                        id=str(uuid4()),
                        name=med_data["name"],
                        generic_name=med_data["generic"],
                        is_brand=med_data["is_brand"],
                        brand_names=json.dumps(med_data["brand_names"]),
                        drug_class=med_data["drug_class"],
                        category=med_data["category"],
                        indication=med_data["indication"],
                        nursing_considerations=json.dumps(med_data["nursing_considerations"]),
                        common_side_effects=json.dumps(med_data["common_side_effects"]),
                        warnings=json.dumps(med_data["warnings"]),
                        source="curated_detailed",
                        is_active=True
                    )
                    session.add(medication)
                    medications_created += 1
                    logger.info(f"  ➕ Added: {med_data['name']} ({med_data['category']})")

                await session.commit()

                logger.info(f"\n✅ Successfully seeded {medications_created} detailed medications!")
                logger.info("These medications now include:")
                logger.info("  - Brand names")
                logger.info("  - Drug class and category")
                logger.info("  - Clinical indications")
                logger.info("  - Nursing considerations")
                logger.info("  - Common side effects")
                logger.info("  - Warnings and contraindications")

            except Exception as e:
                await session.rollback()
                logger.error(f"❌ Database error: {e}")
                raise

    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(seed_detailed_medications())
