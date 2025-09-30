"""
Medication Database Seed Script
Populates the medications table with comprehensive list of common medications
"""

import asyncio
import sys
import os
from uuid import uuid4
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import init_database, get_db_session, Medication
from sqlalchemy import select
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Comprehensive medication list with categorization
MEDICATIONS_DATA = [
    # Pain & Anti-inflammatory
    {"name": "Acetaminophen", "generic": "Acetaminophen", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Analgesic"},
    {"name": "Tylenol", "generic": "Acetaminophen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Analgesic"},
    {"name": "Paracetamol", "generic": "Acetaminophen", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Analgesic"},
    {"name": "Ibuprofen", "generic": "Ibuprofen", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Advil", "generic": "Ibuprofen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Motrin", "generic": "Ibuprofen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Naproxen", "generic": "Naproxen", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Aleve", "generic": "Naproxen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Naprosyn", "generic": "Naproxen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Aspirin", "generic": "Aspirin", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Bayer", "generic": "Aspirin", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "NSAID"},
    {"name": "Excedrin", "generic": "Aspirin/Acetaminophen/Caffeine", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Analgesic Combination"},
    {"name": "Tramadol", "generic": "Tramadol", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Ultram", "generic": "Tramadol", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Hydrocodone", "generic": "Hydrocodone", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Vicodin", "generic": "Hydrocodone/Acetaminophen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Norco", "generic": "Hydrocodone/Acetaminophen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Oxycodone", "generic": "Oxycodone", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "OxyContin", "generic": "Oxycodone", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Percocet", "generic": "Oxycodone/Acetaminophen", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Roxicodone", "generic": "Oxycodone", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "OxyIR", "generic": "Oxycodone", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Morphine", "generic": "Morphine", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "MS Contin", "generic": "Morphine", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Fentanyl", "generic": "Fentanyl", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Duragesic", "generic": "Fentanyl", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Codeine", "generic": "Codeine", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "Opioid"},
    {"name": "Celecoxib", "generic": "Celecoxib", "is_brand": False, "category": "Pain & Anti-inflammatory", "drug_class": "COX-2 Inhibitor"},
    {"name": "Celebrex", "generic": "Celecoxib", "is_brand": True, "category": "Pain & Anti-inflammatory", "drug_class": "COX-2 Inhibitor"},

    # Antibiotics
    {"name": "Amoxicillin", "generic": "Amoxicillin", "is_brand": False, "category": "Antibiotics", "drug_class": "Penicillin"},
    {"name": "Amoxil", "generic": "Amoxicillin", "is_brand": True, "category": "Antibiotics", "drug_class": "Penicillin"},
    {"name": "Augmentin", "generic": "Amoxicillin/Clavulanate", "is_brand": True, "category": "Antibiotics", "drug_class": "Penicillin Combination"},
    {"name": "Azithromycin", "generic": "Azithromycin", "is_brand": False, "category": "Antibiotics", "drug_class": "Macrolide"},
    {"name": "Zithromax", "generic": "Azithromycin", "is_brand": True, "category": "Antibiotics", "drug_class": "Macrolide"},
    {"name": "Z-Pak", "generic": "Azithromycin", "is_brand": True, "category": "Antibiotics", "drug_class": "Macrolide"},
    {"name": "Ciprofloxacin", "generic": "Ciprofloxacin", "is_brand": False, "category": "Antibiotics", "drug_class": "Fluoroquinolone"},
    {"name": "Cipro", "generic": "Ciprofloxacin", "is_brand": True, "category": "Antibiotics", "drug_class": "Fluoroquinolone"},
    {"name": "Levofloxacin", "generic": "Levofloxacin", "is_brand": False, "category": "Antibiotics", "drug_class": "Fluoroquinolone"},
    {"name": "Levaquin", "generic": "Levofloxacin", "is_brand": True, "category": "Antibiotics", "drug_class": "Fluoroquinolone"},
    {"name": "Doxycycline", "generic": "Doxycycline", "is_brand": False, "category": "Antibiotics", "drug_class": "Tetracycline"},
    {"name": "Vibramycin", "generic": "Doxycycline", "is_brand": True, "category": "Antibiotics", "drug_class": "Tetracycline"},
    {"name": "Cephalexin", "generic": "Cephalexin", "is_brand": False, "category": "Antibiotics", "drug_class": "Cephalosporin"},
    {"name": "Keflex", "generic": "Cephalexin", "is_brand": True, "category": "Antibiotics", "drug_class": "Cephalosporin"},
    {"name": "Clindamycin", "generic": "Clindamycin", "is_brand": False, "category": "Antibiotics", "drug_class": "Lincosamide"},
    {"name": "Cleocin", "generic": "Clindamycin", "is_brand": True, "category": "Antibiotics", "drug_class": "Lincosamide"},
    {"name": "Metronidazole", "generic": "Metronidazole", "is_brand": False, "category": "Antibiotics", "drug_class": "Nitroimidazole"},
    {"name": "Flagyl", "generic": "Metronidazole", "is_brand": True, "category": "Antibiotics", "drug_class": "Nitroimidazole"},
    {"name": "Trimethoprim-Sulfamethoxazole", "generic": "Trimethoprim-Sulfamethoxazole", "is_brand": False, "category": "Antibiotics", "drug_class": "Sulfonamide"},
    {"name": "Bactrim", "generic": "Trimethoprim-Sulfamethoxazole", "is_brand": True, "category": "Antibiotics", "drug_class": "Sulfonamide"},
    {"name": "Septra", "generic": "Trimethoprim-Sulfamethoxazole", "is_brand": True, "category": "Antibiotics", "drug_class": "Sulfonamide"},
    {"name": "Penicillin", "generic": "Penicillin", "is_brand": False, "category": "Antibiotics", "drug_class": "Penicillin"},
    {"name": "Pen VK", "generic": "Penicillin VK", "is_brand": True, "category": "Antibiotics", "drug_class": "Penicillin"},

    # Cardiovascular
    {"name": "Atorvastatin", "generic": "Atorvastatin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Lipitor", "generic": "Atorvastatin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Simvastatin", "generic": "Simvastatin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Zocor", "generic": "Simvastatin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Rosuvastatin", "generic": "Rosuvastatin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Crestor", "generic": "Rosuvastatin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Pravastatin", "generic": "Pravastatin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Pravachol", "generic": "Pravastatin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Statin"},
    {"name": "Lisinopril", "generic": "Lisinopril", "is_brand": False, "category": "Cardiovascular", "drug_class": "ACE Inhibitor"},
    {"name": "Prinivil", "generic": "Lisinopril", "is_brand": True, "category": "Cardiovascular", "drug_class": "ACE Inhibitor"},
    {"name": "Zestril", "generic": "Lisinopril", "is_brand": True, "category": "Cardiovascular", "drug_class": "ACE Inhibitor"},
    {"name": "Losartan", "generic": "Losartan", "is_brand": False, "category": "Cardiovascular", "drug_class": "ARB"},
    {"name": "Cozaar", "generic": "Losartan", "is_brand": True, "category": "Cardiovascular", "drug_class": "ARB"},
    {"name": "Valsartan", "generic": "Valsartan", "is_brand": False, "category": "Cardiovascular", "drug_class": "ARB"},
    {"name": "Diovan", "generic": "Valsartan", "is_brand": True, "category": "Cardiovascular", "drug_class": "ARB"},
    {"name": "Amlodipine", "generic": "Amlodipine", "is_brand": False, "category": "Cardiovascular", "drug_class": "Calcium Channel Blocker"},
    {"name": "Norvasc", "generic": "Amlodipine", "is_brand": True, "category": "Cardiovascular", "drug_class": "Calcium Channel Blocker"},
    {"name": "Metoprolol", "generic": "Metoprolol", "is_brand": False, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Lopressor", "generic": "Metoprolol", "is_brand": True, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Toprol-XL", "generic": "Metoprolol", "is_brand": True, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Atenolol", "generic": "Atenolol", "is_brand": False, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Tenormin", "generic": "Atenolol", "is_brand": True, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Carvedilol", "generic": "Carvedilol", "is_brand": False, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Coreg", "generic": "Carvedilol", "is_brand": True, "category": "Cardiovascular", "drug_class": "Beta Blocker"},
    {"name": "Furosemide", "generic": "Furosemide", "is_brand": False, "category": "Cardiovascular", "drug_class": "Loop Diuretic"},
    {"name": "Lasix", "generic": "Furosemide", "is_brand": True, "category": "Cardiovascular", "drug_class": "Loop Diuretic"},
    {"name": "Hydrochlorothiazide", "generic": "Hydrochlorothiazide", "is_brand": False, "category": "Cardiovascular", "drug_class": "Thiazide Diuretic"},
    {"name": "HCTZ", "generic": "Hydrochlorothiazide", "is_brand": False, "category": "Cardiovascular", "drug_class": "Thiazide Diuretic"},
    {"name": "Spironolactone", "generic": "Spironolactone", "is_brand": False, "category": "Cardiovascular", "drug_class": "Potassium-Sparing Diuretic"},
    {"name": "Aldactone", "generic": "Spironolactone", "is_brand": True, "category": "Cardiovascular", "drug_class": "Potassium-Sparing Diuretic"},
    {"name": "Warfarin", "generic": "Warfarin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Coumadin", "generic": "Warfarin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Apixaban", "generic": "Apixaban", "is_brand": False, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Eliquis", "generic": "Apixaban", "is_brand": True, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Rivaroxaban", "generic": "Rivaroxaban", "is_brand": False, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Xarelto", "generic": "Rivaroxaban", "is_brand": True, "category": "Cardiovascular", "drug_class": "Anticoagulant"},
    {"name": "Clopidogrel", "generic": "Clopidogrel", "is_brand": False, "category": "Cardiovascular", "drug_class": "Antiplatelet"},
    {"name": "Plavix", "generic": "Clopidogrel", "is_brand": True, "category": "Cardiovascular", "drug_class": "Antiplatelet"},
    {"name": "Digoxin", "generic": "Digoxin", "is_brand": False, "category": "Cardiovascular", "drug_class": "Cardiac Glycoside"},
    {"name": "Lanoxin", "generic": "Digoxin", "is_brand": True, "category": "Cardiovascular", "drug_class": "Cardiac Glycoside"},

    # Diabetes
    {"name": "Metformin", "generic": "Metformin", "is_brand": False, "category": "Diabetes", "drug_class": "Biguanide"},
    {"name": "Glucophage", "generic": "Metformin", "is_brand": True, "category": "Diabetes", "drug_class": "Biguanide"},
    {"name": "Insulin", "generic": "Insulin", "is_brand": False, "category": "Diabetes", "drug_class": "Insulin"},
    {"name": "Humalog", "generic": "Insulin Lispro", "is_brand": True, "category": "Diabetes", "drug_class": "Rapid-Acting Insulin"},
    {"name": "NovoLog", "generic": "Insulin Aspart", "is_brand": True, "category": "Diabetes", "drug_class": "Rapid-Acting Insulin"},
    {"name": "Lantus", "generic": "Insulin Glargine", "is_brand": True, "category": "Diabetes", "drug_class": "Long-Acting Insulin"},
    {"name": "Levemir", "generic": "Insulin Detemir", "is_brand": True, "category": "Diabetes", "drug_class": "Long-Acting Insulin"},
    {"name": "Glipizide", "generic": "Glipizide", "is_brand": False, "category": "Diabetes", "drug_class": "Sulfonylurea"},
    {"name": "Glucotrol", "generic": "Glipizide", "is_brand": True, "category": "Diabetes", "drug_class": "Sulfonylurea"},
    {"name": "Glyburide", "generic": "Glyburide", "is_brand": False, "category": "Diabetes", "drug_class": "Sulfonylurea"},
    {"name": "Diabeta", "generic": "Glyburide", "is_brand": True, "category": "Diabetes", "drug_class": "Sulfonylurea"},
    {"name": "Sitagliptin", "generic": "Sitagliptin", "is_brand": False, "category": "Diabetes", "drug_class": "DPP-4 Inhibitor"},
    {"name": "Januvia", "generic": "Sitagliptin", "is_brand": True, "category": "Diabetes", "drug_class": "DPP-4 Inhibitor"},
    {"name": "Empagliflozin", "generic": "Empagliflozin", "is_brand": False, "category": "Diabetes", "drug_class": "SGLT2 Inhibitor"},
    {"name": "Jardiance", "generic": "Empagliflozin", "is_brand": True, "category": "Diabetes", "drug_class": "SGLT2 Inhibitor"},
    {"name": "Semaglutide", "generic": "Semaglutide", "is_brand": False, "category": "Diabetes", "drug_class": "GLP-1 Agonist"},
    {"name": "Ozempic", "generic": "Semaglutide", "is_brand": True, "category": "Diabetes", "drug_class": "GLP-1 Agonist"},
    {"name": "Wegovy", "generic": "Semaglutide", "is_brand": True, "category": "Diabetes", "drug_class": "GLP-1 Agonist"},
    {"name": "Liraglutide", "generic": "Liraglutide", "is_brand": False, "category": "Diabetes", "drug_class": "GLP-1 Agonist"},
    {"name": "Victoza", "generic": "Liraglutide", "is_brand": True, "category": "Diabetes", "drug_class": "GLP-1 Agonist"},

    # Gastrointestinal / Acid Reducers
    {"name": "Omeprazole", "generic": "Omeprazole", "is_brand": False, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Prilosec", "generic": "Omeprazole", "is_brand": True, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Esomeprazole", "generic": "Esomeprazole", "is_brand": False, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Nexium", "generic": "Esomeprazole", "is_brand": True, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Pantoprazole", "generic": "Pantoprazole", "is_brand": False, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Protonix", "generic": "Pantoprazole", "is_brand": True, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Lansoprazole", "generic": "Lansoprazole", "is_brand": False, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Prevacid", "generic": "Lansoprazole", "is_brand": True, "category": "Gastrointestinal", "drug_class": "PPI"},
    {"name": "Ranitidine", "generic": "Ranitidine", "is_brand": False, "category": "Gastrointestinal", "drug_class": "H2 Blocker"},
    {"name": "Zantac", "generic": "Ranitidine", "is_brand": True, "category": "Gastrointestinal", "drug_class": "H2 Blocker"},
    {"name": "Famotidine", "generic": "Famotidine", "is_brand": False, "category": "Gastrointestinal", "drug_class": "H2 Blocker"},
    {"name": "Pepcid", "generic": "Famotidine", "is_brand": True, "category": "Gastrointestinal", "drug_class": "H2 Blocker"},
    {"name": "Ondansetron", "generic": "Ondansetron", "is_brand": False, "category": "Gastrointestinal", "drug_class": "Antiemetic"},
    {"name": "Zofran", "generic": "Ondansetron", "is_brand": True, "category": "Gastrointestinal", "drug_class": "Antiemetic"},
    {"name": "Metoclopramide", "generic": "Metoclopramide", "is_brand": False, "category": "Gastrointestinal", "drug_class": "Antiemetic"},
    {"name": "Reglan", "generic": "Metoclopramide", "is_brand": True, "category": "Gastrointestinal", "drug_class": "Antiemetic"},
    {"name": "Docusate", "generic": "Docusate", "is_brand": False, "category": "Gastrointestinal", "drug_class": "Stool Softener"},
    {"name": "Colace", "generic": "Docusate", "is_brand": True, "category": "Gastrointestinal", "drug_class": "Stool Softener"},
    {"name": "Polyethylene Glycol", "generic": "Polyethylene Glycol", "is_brand": False, "category": "Gastrointestinal", "drug_class": "Laxative"},
    {"name": "MiraLAX", "generic": "Polyethylene Glycol", "is_brand": True, "category": "Gastrointestinal", "drug_class": "Laxative"},

    # Respiratory
    {"name": "Albuterol", "generic": "Albuterol", "is_brand": False, "category": "Respiratory", "drug_class": "Bronchodilator"},
    {"name": "ProAir", "generic": "Albuterol", "is_brand": True, "category": "Respiratory", "drug_class": "Bronchodilator"},
    {"name": "Ventolin", "generic": "Albuterol", "is_brand": True, "category": "Respiratory", "drug_class": "Bronchodilator"},
    {"name": "Montelukast", "generic": "Montelukast", "is_brand": False, "category": "Respiratory", "drug_class": "Leukotriene Inhibitor"},
    {"name": "Singulair", "generic": "Montelukast", "is_brand": True, "category": "Respiratory", "drug_class": "Leukotriene Inhibitor"},
    {"name": "Prednisone", "generic": "Prednisone", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Deltasone", "generic": "Prednisone", "is_brand": True, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Prednisolone", "generic": "Prednisolone", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Budesonide", "generic": "Budesonide", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Pulmicort", "generic": "Budesonide", "is_brand": True, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Fluticasone", "generic": "Fluticasone", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Flovent", "generic": "Fluticasone", "is_brand": True, "category": "Respiratory", "drug_class": "Corticosteroid"},
    {"name": "Fluticasone-Salmeterol", "generic": "Fluticasone-Salmeterol", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid/Bronchodilator"},
    {"name": "Advair", "generic": "Fluticasone-Salmeterol", "is_brand": True, "category": "Respiratory", "drug_class": "Corticosteroid/Bronchodilator"},
    {"name": "Budesonide-Formoterol", "generic": "Budesonide-Formoterol", "is_brand": False, "category": "Respiratory", "drug_class": "Corticosteroid/Bronchodilator"},
    {"name": "Symbicort", "generic": "Budesonide-Formoterol", "is_brand": True, "category": "Respiratory", "drug_class": "Corticosteroid/Bronchodilator"},
    {"name": "Tiotropium", "generic": "Tiotropium", "is_brand": False, "category": "Respiratory", "drug_class": "Anticholinergic"},
    {"name": "Spiriva", "generic": "Tiotropium", "is_brand": True, "category": "Respiratory", "drug_class": "Anticholinergic"},

    # Psychiatric / Neurological
    {"name": "Sertraline", "generic": "Sertraline", "is_brand": False, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Zoloft", "generic": "Sertraline", "is_brand": True, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Escitalopram", "generic": "Escitalopram", "is_brand": False, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Lexapro", "generic": "Escitalopram", "is_brand": True, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Fluoxetine", "generic": "Fluoxetine", "is_brand": False, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Prozac", "generic": "Fluoxetine", "is_brand": True, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Citalopram", "generic": "Citalopram", "is_brand": False, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Celexa", "generic": "Citalopram", "is_brand": True, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Paroxetine", "generic": "Paroxetine", "is_brand": False, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Paxil", "generic": "Paroxetine", "is_brand": True, "category": "Psychiatric", "drug_class": "SSRI"},
    {"name": "Venlafaxine", "generic": "Venlafaxine", "is_brand": False, "category": "Psychiatric", "drug_class": "SNRI"},
    {"name": "Effexor", "generic": "Venlafaxine", "is_brand": True, "category": "Psychiatric", "drug_class": "SNRI"},
    {"name": "Duloxetine", "generic": "Duloxetine", "is_brand": False, "category": "Psychiatric", "drug_class": "SNRI"},
    {"name": "Cymbalta", "generic": "Duloxetine", "is_brand": True, "category": "Psychiatric", "drug_class": "SNRI"},
    {"name": "Bupropion", "generic": "Bupropion", "is_brand": False, "category": "Psychiatric", "drug_class": "NDRI"},
    {"name": "Wellbutrin", "generic": "Bupropion", "is_brand": True, "category": "Psychiatric", "drug_class": "NDRI"},
    {"name": "Zyban", "generic": "Bupropion", "is_brand": True, "category": "Psychiatric", "drug_class": "NDRI"},
    {"name": "Trazodone", "generic": "Trazodone", "is_brand": False, "category": "Psychiatric", "drug_class": "SARI"},
    {"name": "Desyrel", "generic": "Trazodone", "is_brand": True, "category": "Psychiatric", "drug_class": "SARI"},
    {"name": "Mirtazapine", "generic": "Mirtazapine", "is_brand": False, "category": "Psychiatric", "drug_class": "Atypical Antidepressant"},
    {"name": "Remeron", "generic": "Mirtazapine", "is_brand": True, "category": "Psychiatric", "drug_class": "Atypical Antidepressant"},
    {"name": "Alprazolam", "generic": "Alprazolam", "is_brand": False, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Xanax", "generic": "Alprazolam", "is_brand": True, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Lorazepam", "generic": "Lorazepam", "is_brand": False, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Ativan", "generic": "Lorazepam", "is_brand": True, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Clonazepam", "generic": "Clonazepam", "is_brand": False, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Klonopin", "generic": "Clonazepam", "is_brand": True, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Diazepam", "generic": "Diazepam", "is_brand": False, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Valium", "generic": "Diazepam", "is_brand": True, "category": "Psychiatric", "drug_class": "Benzodiazepine"},
    {"name": "Zolpidem", "generic": "Zolpidem", "is_brand": False, "category": "Psychiatric", "drug_class": "Sedative-Hypnotic"},
    {"name": "Ambien", "generic": "Zolpidem", "is_brand": True, "category": "Psychiatric", "drug_class": "Sedative-Hypnotic"},
    {"name": "Gabapentin", "generic": "Gabapentin", "is_brand": False, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Neurontin", "generic": "Gabapentin", "is_brand": True, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Pregabalin", "generic": "Pregabalin", "is_brand": False, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Lyrica", "generic": "Pregabalin", "is_brand": True, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Levetiracetam", "generic": "Levetiracetam", "is_brand": False, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Keppra", "generic": "Levetiracetam", "is_brand": True, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Topiramate", "generic": "Topiramate", "is_brand": False, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Topamax", "generic": "Topiramate", "is_brand": True, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Lamotrigine", "generic": "Lamotrigine", "is_brand": False, "category": "Neurological", "drug_class": "Anticonvulsant"},
    {"name": "Lamictal", "generic": "Lamotrigine", "is_brand": True, "category": "Neurological", "drug_class": "Anticonvulsant"},

    # Thyroid & Hormones
    {"name": "Levothyroxine", "generic": "Levothyroxine", "is_brand": False, "category": "Endocrine", "drug_class": "Thyroid Hormone"},
    {"name": "Synthroid", "generic": "Levothyroxine", "is_brand": True, "category": "Endocrine", "drug_class": "Thyroid Hormone"},
    {"name": "Levoxyl", "generic": "Levothyroxine", "is_brand": True, "category": "Endocrine", "drug_class": "Thyroid Hormone"},
    {"name": "Liothyronine", "generic": "Liothyronine", "is_brand": False, "category": "Endocrine", "drug_class": "Thyroid Hormone"},
    {"name": "Cytomel", "generic": "Liothyronine", "is_brand": True, "category": "Endocrine", "drug_class": "Thyroid Hormone"},

    # Allergy & Antihistamines
    {"name": "Cetirizine", "generic": "Cetirizine", "is_brand": False, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Zyrtec", "generic": "Cetirizine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Loratadine", "generic": "Loratadine", "is_brand": False, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Claritin", "generic": "Loratadine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Fexofenadine", "generic": "Fexofenadine", "is_brand": False, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Allegra", "generic": "Fexofenadine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Diphenhydramine", "generic": "Diphenhydramine", "is_brand": False, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Benadryl", "generic": "Diphenhydramine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Hydroxyzine", "generic": "Hydroxyzine", "is_brand": False, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Atarax", "generic": "Hydroxyzine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},
    {"name": "Vistaril", "generic": "Hydroxyzine", "is_brand": True, "category": "Allergy", "drug_class": "Antihistamine"},

    # Urological
    {"name": "Tamsulosin", "generic": "Tamsulosin", "is_brand": False, "category": "Urological", "drug_class": "Alpha Blocker"},
    {"name": "Flomax", "generic": "Tamsulosin", "is_brand": True, "category": "Urological", "drug_class": "Alpha Blocker"},
    {"name": "Finasteride", "generic": "Finasteride", "is_brand": False, "category": "Urological", "drug_class": "5-Alpha Reductase Inhibitor"},
    {"name": "Proscar", "generic": "Finasteride", "is_brand": True, "category": "Urological", "drug_class": "5-Alpha Reductase Inhibitor"},
    {"name": "Propecia", "generic": "Finasteride", "is_brand": True, "category": "Urological", "drug_class": "5-Alpha Reductase Inhibitor"},

    # Dermatology
    {"name": "Hydrocortisone", "generic": "Hydrocortisone", "is_brand": False, "category": "Dermatology", "drug_class": "Topical Corticosteroid"},
    {"name": "Triamcinolone", "generic": "Triamcinolone", "is_brand": False, "category": "Dermatology", "drug_class": "Topical Corticosteroid"},
    {"name": "Clobetasol", "generic": "Clobetasol", "is_brand": False, "category": "Dermatology", "drug_class": "Topical Corticosteroid"},
    {"name": "Temovate", "generic": "Clobetasol", "is_brand": True, "category": "Dermatology", "drug_class": "Topical Corticosteroid"},
    {"name": "Mupirocin", "generic": "Mupirocin", "is_brand": False, "category": "Dermatology", "drug_class": "Topical Antibiotic"},
    {"name": "Bactroban", "generic": "Mupirocin", "is_brand": True, "category": "Dermatology", "drug_class": "Topical Antibiotic"},
    {"name": "Isotretinoin", "generic": "Isotretinoin", "is_brand": False, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Accutane", "generic": "Isotretinoin", "is_brand": True, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Claravis", "generic": "Isotretinoin", "is_brand": True, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Absorica", "generic": "Isotretinoin", "is_brand": True, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Tretinoin", "generic": "Tretinoin", "is_brand": False, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Retin-A", "generic": "Tretinoin", "is_brand": True, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Renova", "generic": "Tretinoin", "is_brand": True, "category": "Dermatology", "drug_class": "Retinoid"},
    {"name": "Benzoyl Peroxide", "generic": "Benzoyl Peroxide", "is_brand": False, "category": "Dermatology", "drug_class": "Topical Acne Treatment"},
    {"name": "PanOxyl", "generic": "Benzoyl Peroxide", "is_brand": True, "category": "Dermatology", "drug_class": "Topical Acne Treatment"},
]

async def seed_medications():
    """Seed medication database with comprehensive medication list."""
    logger.info("🌱 Starting medication database seeding...")

    # Initialize database
    await init_database()

    async for session in get_db_session():
        try:
            # Check if medications already exist
            result = await session.execute(select(Medication))
            existing = result.scalars().all()

            if len(existing) > 0:
                logger.info(f"⚠️ Database already contains {len(existing)} medications.")
                logger.info("Clearing and re-seeding...")

                # Clear existing
                from sqlalchemy import delete
                await session.execute(delete(Medication))
                await session.commit()
                logger.info("✅ Cleared existing medications")

            # Insert medications
            medications_created = 0
            for med_data in MEDICATIONS_DATA:
                medication = Medication(
                    id=str(uuid4()),
                    name=med_data["name"],
                    generic_name=med_data["generic"],
                    is_brand=med_data["is_brand"],
                    category=med_data["category"],
                    drug_class=med_data["drug_class"],
                    source="curated",
                    is_active=True
                )
                session.add(medication)
                medications_created += 1

            await session.commit()
            logger.info(f"✅ Successfully seeded {medications_created} medications")

            # Display summary by category
            result = await session.execute(select(Medication))
            all_meds = result.scalars().all()

            categories = {}
            for med in all_meds:
                if med.category not in categories:
                    categories[med.category] = 0
                categories[med.category] += 1

            logger.info("\n📊 Medication Summary by Category:")
            for category, count in sorted(categories.items()):
                logger.info(f"   {category}: {count} medications")

            logger.info(f"\n🎉 Total medications in database: {len(all_meds)}")

        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Seeding failed: {e}")
            raise e

if __name__ == "__main__":
    asyncio.run(seed_medications())
