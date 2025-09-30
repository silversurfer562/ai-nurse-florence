#!/usr/bin/env python3
"""
Seed Medications Database - Autocomplete Only
AI Nurse Florence

Populates the medications table with 500+ medication names for autocomplete functionality.
This database is ONLY used for medication name search - NOT for drug details.
All drug interaction analysis and clinical information comes from OpenAI.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.models.database import Medication, Base
from src.utils.config import Settings

# Comprehensive list of 500+ commonly prescribed medications (generic and brand names)
COMMON_MEDICATIONS = [
    # Cardiovascular Medications
    "Lisinopril", "Amlodipine", "Metoprolol", "Atorvastatin", "Simvastatin",
    "Losartan", "Carvedilol", "Furosemide", "Hydrochlorothiazide", "Warfarin",
    "Clopidogrel", "Aspirin", "Ramipril", "Valsartan", "Diltiazem",
    "Enalapril", "Propranolol", "Spironolactone", "Digoxin", "Isosorbide",
    "Nifedipine", "Verapamil", "Quinapril", "Benazepril", "Fosinopril",
    "Telmisartan", "Irbesartan", "Candesartan", "Olmesartan", "Eplerenone",
    "Rosuvastatin", "Pravastatin", "Lovastatin", "Fluvastatin", "Pitavastatin",
    "Fenofibrate", "Gemfibrozil", "Ezetimibe", "Nitroglycerin", "Hydralazine",
    "Clonidine", "Doxazosin", "Prazosin", "Terazosin", "Labetalol",
    "Atenolol", "Nadolol", "Bisoprolol", "Nebivolol", "Acebutolol",

    # Brand names for cardiovascular
    "Lipitor", "Zocor", "Crestor", "Pravachol", "Mevacor",
    "Norvasc", "Cardizem", "Toprol", "Lopressor", "Coreg",
    "Lasix", "Coumadin", "Plavix", "Diovan", "Cozaar",
    "Prinivil", "Zestril", "Vasotec", "Altace", "Accupril",

    # Diabetes Medications
    "Metformin", "Glipizide", "Glyburide", "Insulin", "Sitagliptin",
    "Pioglitazone", "Rosiglitazone", "Glimepiride", "Acarbose", "Repaglinide",
    "Nateglinide", "Exenatide", "Liraglutide", "Dulaglutide", "Semaglutide",
    "Canagliflozin", "Dapagliflozin", "Empagliflozin", "Ertugliflozin", "Saxagliptin",
    "Linagliptin", "Alogliptin", "Pramlintide", "Insulin Glargine", "Insulin Aspart",
    "Insulin Lispro", "Insulin Detemir", "Insulin Degludec", "NPH Insulin", "Regular Insulin",

    # Brand names for diabetes
    "Glucophage", "Januvia", "Actos", "Avandia", "Amaryl",
    "Victoza", "Ozempic", "Trulicity", "Byetta", "Invokana",
    "Farxiga", "Jardiance", "Lantus", "Humalog", "Novolog",
    "Levemir", "Tresiba", "Toujeo", "Basaglar", "Apidra",

    # Antibiotics
    "Amoxicillin", "Azithromycin", "Ciprofloxacin", "Levofloxacin", "Doxycycline",
    "Cephalexin", "Clindamycin", "Metronidazole", "Trimethoprim", "Sulfamethoxazole",
    "Penicillin", "Ampicillin", "Cefuroxime", "Ceftriaxone", "Cefdinir",
    "Nitrofurantoin", "Vancomycin", "Gentamicin", "Tobramycin", "Moxifloxacin",
    "Clarithromycin", "Erythromycin", "Tetracycline", "Minocycline", "Linezolid",
    "Cefazolin", "Cefepime", "Ceftazidime", "Meropenem", "Imipenem",
    "Ertapenem", "Piperacillin", "Tazobactam", "Amoxicillin-Clavulanate", "Sulfadiazine",

    # Brand names for antibiotics
    "Augmentin", "Zithromax", "Z-Pak", "Cipro", "Levaquin",
    "Keflex", "Cleocin", "Flagyl", "Bactrim", "Septra",
    "Avelox", "Biaxin", "Macrobid", "Rocephin", "Omnicef",

    # Pain Medications & NSAIDs
    "Ibuprofen", "Naproxen", "Acetaminophen", "Tramadol", "Celecoxib",
    "Meloxicam", "Diclofenac", "Indomethacin", "Ketorolac", "Piroxicam",
    "Hydrocodone", "Oxycodone", "Morphine", "Fentanyl", "Codeine",
    "Hydromorphone", "Oxymorphone", "Buprenorphine", "Naloxone", "Gabapentin",
    "Pregabalin", "Duloxetine", "Amitriptyline", "Nortriptyline", "Cyclobenzaprine",

    # Brand names for pain
    "Advil", "Motrin", "Aleve", "Tylenol", "Ultram",
    "Celebrex", "Mobic", "Voltaren", "Toradol", "Vicodin",
    "Percocet", "OxyContin", "Dilaudid", "Duragesic", "Suboxone",
    "Neurontin", "Lyrica", "Cymbalta", "Elavil", "Pamelor",
    "Flexeril", "Soma", "Robaxin", "Skelaxin", "Zanaflex",

    # Gastrointestinal Medications
    "Omeprazole", "Pantoprazole", "Esomeprazole", "Lansoprazole", "Rabeprazole",
    "Famotidine", "Ranitidine", "Ondansetron", "Metoclopramide", "Bismuth",
    "Loperamide", "Docusate", "Senna", "Polyethylene Glycol", "Lactulose",
    "Psyllium", "Sucralfate", "Misoprostol", "Mesalamine", "Sulfasalazine",
    "Dicyclomine", "Hyoscyamine", "Lubiprostone", "Linaclotide", "Eluxadoline",

    # Brand names for GI
    "Prilosec", "Protonix", "Nexium", "Prevacid", "AcipHex",
    "Pepcid", "Zantac", "Zofran", "Reglan", "Pepto-Bismol",
    "Imodium", "Colace", "Senokot", "MiraLAX", "Metamucil",
    "Carafate", "Cytotec", "Asacol", "Azulfidine", "Bentyl",

    # Respiratory Medications
    "Albuterol", "Fluticasone", "Budesonide", "Montelukast", "Ipratropium",
    "Tiotropium", "Salmeterol", "Formoterol", "Prednisone", "Methylprednisolone",
    "Dexamethasone", "Guaifenesin", "Dextromethorphan", "Benzonatate", "Codeine",
    "Cetirizine", "Loratadine", "Fexofenadine", "Diphenhydramine", "Pseudoephedrine",
    "Phenylephrine", "Oxymetazoline", "Cromolyn", "Zafirlukast", "Roflumilast",

    # Brand names for respiratory
    "Proventil", "Ventolin", "ProAir", "Flovent", "Pulmicort",
    "Singulair", "Atrovent", "Spiriva", "Advair", "Symbicort",
    "Breo", "Anoro", "Dulera", "Mucinex", "Robitussin",
    "Tessalon", "Zyrtec", "Claritin", "Allegra", "Benadryl",
    "Sudafed", "Afrin", "Nasacort", "Flonase", "Rhinocort",

    # Psychiatric Medications
    "Sertraline", "Fluoxetine", "Escitalopram", "Citalopram", "Paroxetine",
    "Venlafaxine", "Desvenlafaxine", "Duloxetine", "Bupropion", "Mirtazapine",
    "Trazodone", "Buspirone", "Alprazolam", "Lorazepam", "Clonazepam",
    "Diazepam", "Temazepam", "Zolpidem", "Eszopiclone", "Ramelteon",
    "Quetiapine", "Olanzapine", "Risperidone", "Aripiprazole", "Ziprasidone",
    "Lithium", "Valproic Acid", "Lamotrigine", "Carbamazepine", "Oxcarbazepine",
    "Atomoxetine", "Methylphenidate", "Amphetamine", "Lisdexamfetamine", "Dextroamphetamine",
    "Modafinil", "Armodafinil", "Memantine", "Donepezil", "Rivastigmine",
    "Galantamine", "Varenicline", "Bupropion", "Naltrexone", "Disulfiram",

    # Brand names for psychiatric
    "Zoloft", "Prozac", "Lexapro", "Celexa", "Paxil",
    "Effexor", "Pristiq", "Cymbalta", "Wellbutrin", "Remeron",
    "Desyrel", "BuSpar", "Xanax", "Ativan", "Klonopin",
    "Valium", "Restoril", "Ambien", "Lunesta", "Rozerem",
    "Seroquel", "Zyprexa", "Risperdal", "Abilify", "Geodon",
    "Eskalith", "Depakote", "Lamictal", "Tegretol", "Trileptal",
    "Strattera", "Ritalin", "Concerta", "Adderall", "Vyvanse",
    "Provigil", "Nuvigil", "Namenda", "Aricept", "Exelon",
    "Razadyne", "Chantix", "Zyban", "Antabuse", "Campral",

    # Thyroid & Endocrine
    "Levothyroxine", "Liothyronine", "Methimazole", "Propylthiouracil", "Testosterone",
    "Estradiol", "Progesterone", "Medroxyprogesterone", "Norethindrone", "Ethinyl Estradiol",
    "Levonorgestrel", "Desogestrel", "Drospirenone", "Tamoxifen", "Raloxifene",
    "Alendronate", "Risedronate", "Ibandronate", "Zoledronic Acid", "Calcitonin",
    "Teriparatide", "Denosumab", "Vitamin D", "Calcium", "Calcitriol",

    # Brand names for endocrine
    "Synthroid", "Levoxyl", "Cytomel", "Tapazole", "PTU",
    "AndroGel", "Testim", "Estrace", "Premarin", "Provera",
    "Depo-Provera", "Ortho-Novum", "Yasmin", "Yaz", "NuvaRing",
    "Plan B", "Nolvadex", "Evista", "Fosamax", "Actonel",
    "Boniva", "Reclast", "Miacalcin", "Forteo", "Prolia",

    # Anticoagulants & Antiplatelet
    "Warfarin", "Heparin", "Enoxaparin", "Rivaroxaban", "Apixaban",
    "Dabigatran", "Edoxaban", "Clopidogrel", "Prasugrel", "Ticagrelor",
    "Aspirin", "Dipyridamole", "Cilostazol", "Fondaparinux", "Argatroban",

    # Brand names for anticoagulants
    "Coumadin", "Lovenox", "Xarelto", "Eliquis", "Pradaxa",
    "Savaysa", "Plavix", "Effient", "Brilinta", "Aggrenox",
    "Pletal", "Arixtra", "Fragmin", "Innohep", "Angiomax",

    # Neurological Medications
    "Levodopa", "Carbidopa", "Pramipexole", "Ropinirole", "Amantadine",
    "Phenytoin", "Levetiracetam", "Topiramate", "Valproic Acid", "Lacosamide",
    "Sumatriptan", "Rizatriptan", "Eletriptan", "Zolmitriptan", "Propranolol",
    "Amitriptyline", "Verapamil", "Baclofen", "Tizanidine", "Dantrolene",

    # Brand names for neurological
    "Sinemet", "Mirapex", "Requip", "Symmetrel", "Dilantin",
    "Keppra", "Topamax", "Depakote", "Vimpat", "Imitrex",
    "Maxalt", "Relpax", "Zomig", "Inderal", "Lioresal",
    "Zanaflex", "Dantrium", "Namenda", "Aricept", "Exelon",

    # Immunosuppressants & Biologics
    "Prednisone", "Methylprednisolone", "Hydrocortisone", "Dexamethasone", "Azathioprine",
    "Cyclosporine", "Tacrolimus", "Mycophenolate", "Methotrexate", "Hydroxychloroquine",
    "Sulfasalazine", "Leflunomide", "Adalimumab", "Etanercept", "Infliximab",
    "Rituximab", "Tocilizumab", "Ustekinumab", "Secukinumab", "Ixekizumab",

    # Brand names for immunosuppressants
    "Deltasone", "Medrol", "Cortef", "Decadron", "Imuran",
    "Neoral", "Sandimmune", "Prograf", "CellCept", "Rheumatrex",
    "Plaquenil", "Azulfidine", "Arava", "Humira", "Enbrel",
    "Remicade", "Rituxan", "Actemra", "Stelara", "Cosentyx",
    "Taltz", "Simponi", "Cimzia", "Orencia", "Kineret",

    # Urological Medications
    "Tamsulosin", "Finasteride", "Dutasteride", "Alfuzosin", "Doxazosin",
    "Terazosin", "Sildenafil", "Tadalafil", "Vardenafil", "Oxybutynin",
    "Tolterodine", "Solifenacin", "Darifenacin", "Fesoterodine", "Mirabegron",

    # Brand names for urological
    "Flomax", "Proscar", "Propecia", "Avodart", "Uroxatral",
    "Cardura", "Hytrin", "Viagra", "Cialis", "Levitra",
    "Ditropan", "Detrol", "VESIcare", "Enablex", "Toviaz",
    "Myrbetriq", "Rapaflo", "Jalyn", "Combigan", "Betoptic",

    # Ophthalmic Medications
    "Latanoprost", "Timolol", "Brimonidine", "Dorzolamide", "Brinzolamide",
    "Travoprost", "Bimatoprost", "Tafluprost", "Prednisolone", "Dexamethasone",
    "Cyclosporine", "Loteprednol", "Ketorolac", "Nepafenac", "Bromfenac",

    # Brand names for ophthalmic
    "Xalatan", "Timoptic", "Alphagan", "Trusopt", "Azopt",
    "Travatan", "Lumigan", "Zioptan", "Pred Forte", "Restasis",
    "Lotemax", "Acular", "Nevanac", "Prolensa", "Ilevro",

    # Dermatological Medications
    "Tretinoin", "Isotretinoin", "Adapalene", "Benzoyl Peroxide", "Clindamycin",
    "Erythromycin", "Doxycycline", "Minocycline", "Hydrocortisone", "Triamcinolone",
    "Betamethasone", "Clobetasol", "Fluocinonide", "Tacrolimus", "Pimecrolimus",

    # Brand names for dermatological
    "Retin-A", "Accutane", "Differin", "Benzac", "Cleocin T",
    "Ery-Tab", "Doryx", "Solodyn", "Cortaid", "Kenalog",
    "Diprolene", "Temovate", "Lidex", "Protopic", "Elidel",

    # Antivirals
    "Acyclovir", "Valacyclovir", "Famciclovir", "Oseltamivir", "Zanamivir",
    "Amantadine", "Rimantadine", "Ribavirin", "Sofosbuvir", "Ledipasvir",
    "Daclatasvir", "Simeprevir", "Ombitasvir", "Paritaprevir", "Dasabuvir",
    "Tenofovir", "Emtricitabine", "Lamivudine", "Efavirenz", "Dolutegravir",
    "Raltegravir", "Elvitegravir", "Atazanavir", "Darunavir", "Lopinavir",
    "Ritonavir", "Abacavir", "Zidovudine", "Stavudine", "Didanosine",

    # Brand names for antivirals
    "Zovirax", "Valtrex", "Famvir", "Tamiflu", "Relenza",
    "Symmetrel", "Flumadine", "Rebetol", "Sovaldi", "Harvoni",
    "Daklinza", "Olysio", "Viekira Pak", "Viread", "Truvada",
    "Epivir", "Sustiva", "Tivicay", "Isentress", "Vitekta",
    "Reyataz", "Prezista", "Kaletra", "Ziagen", "Retrovir",

    # Additional Common Medications
    "Allopurinol", "Colchicine", "Probenecid", "Febuxostat", "Rasburicase",
    "Cholestyramine", "Colesevelam", "Niacin", "Fish Oil", "Omega-3",
    "Vitamin B12", "Folic Acid", "Iron", "Ferrous Sulfate", "Multivitamin",
    "Potassium", "Magnesium", "Zinc", "Biotin", "Vitamin C",
]

async def seed_medications():
    """Seed the medications database with common medication names for autocomplete."""
    settings = Settings()

    # Handle both SQLite and PostgreSQL
    db_url = settings.DATABASE_URL
    if 'postgresql://' in db_url:
        db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    elif 'sqlite' not in db_url:
        # Default to SQLite if no database configured
        db_url = 'sqlite+aiosqlite:///./dev.db'

    print(f"Connecting to database: {db_url.split('@')[0]}...")  # Hide credentials

    # Create async engine
    engine = create_async_engine(db_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Clear existing medications
        from sqlalchemy import text
        await session.execute(text("DELETE FROM medications"))
        await session.commit()

        print(f"Adding {len(COMMON_MEDICATIONS)} medications to database...")

        # Add medications (use executemany for better performance and avoid duplicates)
        medications_added = 0
        for med_name in COMMON_MEDICATIONS:
            # Check if medication already exists (case-insensitive)
            from sqlalchemy import select, func
            result = await session.execute(
                select(Medication).where(func.lower(Medication.name) == func.lower(med_name))
            )
            existing = result.scalar_one_or_none()

            if not existing:
                medication = Medication(
                    id=str(uuid.uuid4()),
                    name=med_name,
                    source="curated_autocomplete",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(medication)
                medications_added += 1

                if medications_added % 50 == 0:
                    print(f"  Added {medications_added} medications...")
                    await session.commit()  # Commit in batches

        await session.commit()  # Final commit
        print(f"\n✅ Successfully added {medications_added} medications to database")
        print("Database is now ready for autocomplete functionality")

    await engine.dispose()

if __name__ == "__main__":
    print("=" * 70)
    print("AI Nurse Florence - Medication Autocomplete Database Seeding")
    print("=" * 70)
    print("\nThis script populates the medications table with 500+ medication names")
    print("for autocomplete functionality ONLY.")
    print("\nNote: Drug interaction analysis and clinical details come from OpenAI,")
    print("      NOT from this database.")
    print("=" * 70)
    print()

    asyncio.run(seed_medications())
