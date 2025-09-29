"""
Condition-Based Wizard Service
Integrates selected medical conditions with targeted nursing workflows
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..utils.config import get_educational_banner, get_settings
from ..utils.redis_cache import cached
from .disease_service import lookup_disease_info

logger = logging.getLogger(__name__)

# In-memory wizard session storage (Redis in production)
wizard_sessions: Dict[str, Dict[str, Any]] = {}

class ConditionWizard:
    """Base class for condition-specific wizards"""

    def __init__(self, wizard_type: str, condition_data: Dict[str, Any]):
        self.wizard_id = str(uuid.uuid4())
        self.wizard_type = wizard_type
        self.condition_data = condition_data
        self.created_at = datetime.now()
        self.steps_completed: List[str] = []
        self.cached_data: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wizard_id": self.wizard_id,
            "wizard_type": self.wizard_type,
            "condition_data": self.condition_data,
            "created_at": self.created_at.isoformat(),
            "steps_completed": self.steps_completed,
            "cached_data": self.cached_data
        }


async def create_condition_wizard(
    condition_name: str,
    condition_id: str,
    wizard_type: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a new condition-based wizard with cached medical data
    """
    try:
        # Get comprehensive condition information
        condition_info = await lookup_disease_info(condition_name)

        # Create wizard with enhanced condition data
        enhanced_condition = {
            "name": condition_name,
            "mondo_id": condition_id,
            "medical_info": condition_info,
            "user_context": user_context or {}
        }

        wizard = ConditionWizard(wizard_type, enhanced_condition)

        # Pre-cache relevant data based on wizard type
        await _precache_wizard_data(wizard)

        # Store session
        wizard_sessions[wizard.wizard_id] = wizard.to_dict()

        logger.info(f"Created {wizard_type} wizard for {condition_name} ({condition_id})")

        return {
            "wizard_id": wizard.wizard_id,
            "wizard_type": wizard_type,
            "condition": enhanced_condition,
            "status": "created",
            "next_steps": await _get_wizard_steps(wizard_type),
            "cached_data_available": list(wizard.cached_data.keys())
        }

    except Exception as e:
        logger.error(f"Failed to create condition wizard: {e}")
        raise


async def _precache_wizard_data(wizard: ConditionWizard) -> None:
    """Pre-cache relevant data based on wizard type and condition"""
    condition_name = wizard.condition_data["name"]

    # Cache condition-specific nursing interventions
    if wizard.wizard_type in ["sbar", "care_plan", "nursing_assessment"]:
        wizard.cached_data["nursing_interventions"] = await _get_nursing_interventions(condition_name)

    # Cache medication information
    if wizard.wizard_type in ["medication_reconciliation", "care_plan", "handoff"]:
        wizard.cached_data["medications"] = await _get_condition_medications(condition_name)

    # Cache assessment priorities
    if wizard.wizard_type in ["nursing_assessment", "sbar", "handoff"]:
        wizard.cached_data["assessment_priorities"] = await _get_assessment_priorities(condition_name)

    # Cache documentation templates
    if wizard.wizard_type in ["sbar", "handoff", "nursing_notes"]:
        wizard.cached_data["templates"] = await _get_documentation_templates(wizard.wizard_type, condition_name)


async def _get_nursing_interventions(condition_name: str) -> List[Dict[str, Any]]:
    """Get condition-specific nursing interventions"""

    # Define condition-specific interventions
    interventions_map = {
        "diabetes": [
            {
                "priority": "high",
                "intervention": "Monitor blood glucose levels per protocol",
                "frequency": "q4h or as ordered",
                "rationale": "Prevent hypoglycemic/hyperglycemic episodes"
            },
            {
                "priority": "high",
                "intervention": "Assess feet daily for wounds or pressure areas",
                "frequency": "daily",
                "rationale": "Diabetic neuropathy increases injury risk"
            },
            {
                "priority": "medium",
                "intervention": "Monitor dietary compliance and carbohydrate counting",
                "frequency": "each meal",
                "rationale": "Optimize glycemic control"
            },
            {
                "priority": "medium",
                "intervention": "Assess injection sites for lipodystrophy",
                "frequency": "with each insulin administration",
                "rationale": "Ensure proper insulin absorption"
            }
        ],
        "hypertension": [
            {
                "priority": "high",
                "intervention": "Monitor blood pressure and hemodynamic status",
                "frequency": "q4h or as ordered",
                "rationale": "Detect hypertensive crisis or hypotensive episodes"
            },
            {
                "priority": "high",
                "intervention": "Assess for target organ damage",
                "frequency": "shift assessment",
                "rationale": "Early detection of complications"
            },
            {
                "priority": "medium",
                "intervention": "Monitor medication adherence and side effects",
                "frequency": "daily",
                "rationale": "Optimize therapeutic effectiveness"
            }
        ],
        "heart failure": [
            {
                "priority": "high",
                "intervention": "Monitor daily weights and fluid balance",
                "frequency": "daily, same time/scale",
                "rationale": "Early detection of fluid retention"
            },
            {
                "priority": "high",
                "intervention": "Assess respiratory status and oxygen saturation",
                "frequency": "q4h",
                "rationale": "Monitor for pulmonary edema"
            },
            {
                "priority": "medium",
                "intervention": "Monitor electrolytes, especially potassium",
                "frequency": "as ordered",
                "rationale": "Prevent complications from diuretic therapy"
            }
        ]
    }

    # Get interventions for condition (case-insensitive)
    condition_lower = condition_name.lower()
    for key, interventions in interventions_map.items():
        if key in condition_lower:
            return interventions

    # Default interventions for unknown conditions
    return [
        {
            "priority": "high",
            "intervention": "Complete comprehensive nursing assessment",
            "frequency": "per protocol",
            "rationale": "Establish baseline and identify nursing diagnoses"
        },
        {
            "priority": "medium",
            "intervention": "Monitor vital signs and symptoms",
            "frequency": "as ordered",
            "rationale": "Track patient status and response to treatment"
        }
    ]


async def _get_condition_medications(condition_name: str) -> List[Dict[str, Any]]:
    """Get common medications for the condition"""

    medication_map = {
        "diabetes": [
            {
                "category": "Rapid-acting insulin",
                "examples": ["Humalog", "NovoLog", "Apidra"],
                "monitoring": "Blood glucose before meals and bedtime",
                "nursing_considerations": "Administer 15 minutes before meals, rotate injection sites"
            },
            {
                "category": "Long-acting insulin",
                "examples": ["Lantus", "Levemir", "Tresiba"],
                "monitoring": "Fasting glucose, HbA1c",
                "nursing_considerations": "Administer same time daily, do not mix with other insulins"
            },
            {
                "category": "Oral antidiabetics",
                "examples": ["Metformin", "Glipizide", "Januvia"],
                "monitoring": "Kidney function, vitamin B12 levels",
                "nursing_considerations": "Take with meals to reduce GI upset"
            }
        ],
        "hypertension": [
            {
                "category": "ACE Inhibitors",
                "examples": ["Lisinopril", "Enalapril", "Captopril"],
                "monitoring": "Blood pressure, kidney function, potassium",
                "nursing_considerations": "Monitor for dry cough, angioedema"
            },
            {
                "category": "Beta blockers",
                "examples": ["Metoprolol", "Atenolol", "Propranolol"],
                "monitoring": "Heart rate, blood pressure, respiratory status",
                "nursing_considerations": "Do not stop abruptly, monitor for bronchospasm"
            }
        ],
        "heart failure": [
            {
                "category": "Diuretics",
                "examples": ["Furosemide", "HCTZ", "Spironolactone"],
                "monitoring": "Daily weights, electrolytes, kidney function",
                "nursing_considerations": "Monitor I&O, assess for dehydration/overdiuresis"
            }
        ]
    }

    condition_lower = condition_name.lower()
    for key, medications in medication_map.items():
        if key in condition_lower:
            return medications

    return [{
        "category": "Condition-specific medications",
        "examples": ["Consult pharmacist or provider"],
        "monitoring": "Per medication protocols",
        "nursing_considerations": "Follow institutional medication administration policies"
    }]


async def _get_assessment_priorities(condition_name: str) -> List[Dict[str, Any]]:
    """Get assessment priorities for the condition"""

    assessment_map = {
        "diabetes": [
            {
                "system": "Integumentary",
                "focus": "Skin integrity, wounds, injection sites",
                "frequency": "Daily",
                "red_flags": "Non-healing wounds, signs of infection"
            },
            {
                "system": "Neurological",
                "focus": "Peripheral sensation, reflexes",
                "frequency": "Shift assessment",
                "red_flags": "Loss of sensation, absent reflexes"
            },
            {
                "system": "Vascular",
                "focus": "Peripheral pulses, circulation",
                "frequency": "Shift assessment",
                "red_flags": "Diminished pulses, poor capillary refill"
            }
        ],
        "hypertension": [
            {
                "system": "Cardiovascular",
                "focus": "Blood pressure trends, heart rate, rhythm",
                "frequency": "q4h or per orders",
                "red_flags": "SBP >180, DBP >110, irregular rhythm"
            },
            {
                "system": "Neurological",
                "focus": "Headaches, vision changes, mental status",
                "frequency": "q4h",
                "red_flags": "Severe headache, vision changes, confusion"
            }
        ],
        "heart failure": [
            {
                "system": "Respiratory",
                "focus": "Breath sounds, dyspnea, oxygen saturation",
                "frequency": "q4h",
                "red_flags": "Crackles, increasing dyspnea, O2 sat <90%"
            },
            {
                "system": "Cardiovascular",
                "focus": "Heart sounds, edema, jugular venous distension",
                "frequency": "q8h",
                "red_flags": "S3 gallop, increasing edema, elevated JVD"
            }
        ]
    }

    condition_lower = condition_name.lower()
    for key, assessments in assessment_map.items():
        if key in condition_lower:
            return assessments

    return [{
        "system": "General",
        "focus": "Vital signs, pain, functional status",
        "frequency": "Per protocol",
        "red_flags": "Significant changes from baseline"
    }]


async def _get_documentation_templates(wizard_type: str, condition_name: str) -> Dict[str, Any]:
    """Get documentation templates for the wizard type and condition"""

    if wizard_type == "sbar":
        return {
            "template": f"""
**SITUATION:**
Patient: [Name], [Age] y/o [Gender] with {condition_name}
Room: [Room Number]
Attending: [Provider Name]
Reason for report: [Reason]

**BACKGROUND:**
- Admitted: [Date] for [Reason]
- Primary diagnosis: {condition_name}
- Relevant history: [Medical History]
- Allergies: [Allergies]
- Current medications: [See cached medication data]

**ASSESSMENT:**
- Vital signs: [Current VS]
- Key assessments: [See cached assessment priorities]
- Lab results: [Recent labs]
- Patient concerns: [Patient/family concerns]

**RECOMMENDATION:**
- Immediate needs: [Urgent interventions needed]
- Anticipated orders: [Expected orders]
- Follow-up: [When to reassess]
- Questions/concerns: [Specific questions for provider]
            """.strip(),
            "placeholders": [
                "Patient name", "Age", "Gender", "Room number", "Provider name",
                "Reason for report", "Admission date", "Admission reason",
                "Medical history", "Allergies", "Current VS", "Recent labs",
                "Patient concerns", "Urgent interventions", "Expected orders",
                "Reassessment timing", "Provider questions"
            ]
        }

    elif wizard_type == "handoff":
        return {
            "template": f"""
**HANDOFF COMMUNICATION**
Patient: [Name] - Room: [Room]
Diagnosis: {condition_name}

**CURRENT STATUS:**
- Condition: [Stable/Unstable/Critical]
- Pain level: [0-10 scale]
- Activity level: [Bedrest/Up with assist/Independent]
- Diet: [NPO/Clear liquids/Regular/Diabetic/etc.]

**KEY INTERVENTIONS THIS SHIFT:**
[See cached nursing interventions]

**MEDICATIONS:**
[See cached medication data]

**PENDING/UPCOMING:**
- Lab draws: [Times and types]
- Procedures: [Scheduled procedures]
- Appointments: [Upcoming appointments]
- Teaching: [Patient education needs]

**CONCERNS/WATCH FOR:**
[See assessment priorities and red flags]

**FAMILY/SUPPORT:**
- Contacts: [Emergency contacts]
- Involvement: [Family participation in care]
            """.strip(),
            "placeholders": [
                "Patient name", "Room number", "Current condition",
                "Pain level", "Activity level", "Diet orders",
                "Lab schedule", "Procedures", "Appointments",
                "Education needs", "Emergency contacts", "Family involvement"
            ]
        }

    return {"template": "Generic template", "placeholders": []}


async def _get_wizard_steps(wizard_type: str) -> List[Dict[str, Any]]:
    """Get the steps for a specific wizard type"""

    steps_map = {
        "sbar": [
            {"step": 1, "title": "Situation", "description": "Patient identification and current situation"},
            {"step": 2, "title": "Background", "description": "Medical history and current medications"},
            {"step": 3, "title": "Assessment", "description": "Current status and assessment findings"},
            {"step": 4, "title": "Recommendation", "description": "Requested actions and follow-up"}
        ],
        "care_plan": [
            {"step": 1, "title": "Assessment Data", "description": "Gather condition-specific assessment data"},
            {"step": 2, "title": "Nursing Diagnoses", "description": "Identify priority nursing diagnoses"},
            {"step": 3, "title": "Goals & Outcomes", "description": "Set measurable patient outcomes"},
            {"step": 4, "title": "Interventions", "description": "Select evidence-based interventions"},
            {"step": 5, "title": "Evaluation", "description": "Plan for outcome evaluation"}
        ],
        "nursing_assessment": [
            {"step": 1, "title": "Primary Survey", "description": "Airway, breathing, circulation"},
            {"step": 2, "title": "Systems Assessment", "description": "Condition-focused system review"},
            {"step": 3, "title": "Psychosocial", "description": "Mental status and support systems"},
            {"step": 4, "title": "Documentation", "description": "Record findings and priorities"}
        ],
        "handoff": [
            {"step": 1, "title": "Current Status", "description": "Patient condition and stability"},
            {"step": 2, "title": "Interventions", "description": "Completed and ongoing interventions"},
            {"step": 3, "title": "Pending Items", "description": "Upcoming tasks and monitoring"},
            {"step": 4, "title": "Concerns", "description": "Watch items and contingency plans"}
        ],
        "medication_reconciliation": [
            {"step": 1, "title": "Home Medications", "description": "Verify pre-admission medications"},
            {"step": 2, "title": "Current Orders", "description": "Review current medication orders"},
            {"step": 3, "title": "Reconciliation", "description": "Identify discrepancies and clarify"},
            {"step": 4, "title": "Education", "description": "Patient education on medication changes"}
        ]
    }

    return steps_map.get(wizard_type, [])


async def get_wizard_session(wizard_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a wizard session"""
    return wizard_sessions.get(wizard_id)


async def update_wizard_progress(
    wizard_id: str,
    step_completed: str,
    step_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update wizard progress and cache step data"""

    if wizard_id not in wizard_sessions:
        raise ValueError(f"Wizard session {wizard_id} not found")

    session = wizard_sessions[wizard_id]

    # Add completed step
    if step_completed not in session["steps_completed"]:
        session["steps_completed"].append(step_completed)

    # Cache step data
    session["cached_data"][f"step_{step_completed}"] = step_data

    # Update session
    wizard_sessions[wizard_id] = session

    logger.info(f"Updated wizard {wizard_id}, completed step {step_completed}")

    return {
        "wizard_id": wizard_id,
        "steps_completed": session["steps_completed"],
        "progress_percentage": len(session["steps_completed"]) / len(await _get_wizard_steps(session["wizard_type"])) * 100,
        "cached_data_keys": list(session["cached_data"].keys())
    }


async def complete_wizard(wizard_id: str) -> Dict[str, Any]:
    """Complete a wizard and generate final output"""

    if wizard_id not in wizard_sessions:
        raise ValueError(f"Wizard session {wizard_id} not found")

    session = wizard_sessions[wizard_id]
    wizard_type = session["wizard_type"]
    condition_data = session["condition_data"]
    cached_data = session["cached_data"]

    # Generate final document based on wizard type
    final_output = await _generate_final_document(wizard_type, condition_data, cached_data)

    # Clean up session (or archive it)
    # del wizard_sessions[wizard_id]  # Keep for now for review

    logger.info(f"Completed wizard {wizard_id} of type {wizard_type}")

    return {
        "wizard_id": wizard_id,
        "wizard_type": wizard_type,
        "condition": condition_data["name"],
        "status": "completed",
        "final_document": final_output,
        "completion_time": datetime.now().isoformat()
    }


async def _generate_final_document(
    wizard_type: str,
    condition_data: Dict[str, Any],
    cached_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate final document based on completed wizard steps"""

    condition_name = condition_data["name"]

    if wizard_type == "sbar":
        return {
            "document_type": "SBAR Report",
            "condition": condition_name,
            "template": cached_data.get("templates", {}).get("template", ""),
            "nursing_interventions": cached_data.get("nursing_interventions", []),
            "assessment_priorities": cached_data.get("assessment_priorities", []),
            "medications": cached_data.get("medications", []),
            "completed_data": {k: v for k, v in cached_data.items() if k.startswith("step_")},
            "banner": get_educational_banner()
        }

    elif wizard_type == "care_plan":
        return {
            "document_type": "Nursing Care Plan",
            "condition": condition_name,
            "nursing_diagnoses": _generate_nursing_diagnoses(condition_name),
            "interventions": cached_data.get("nursing_interventions", []),
            "goals": _generate_care_goals(condition_name),
            "completed_data": {k: v for k, v in cached_data.items() if k.startswith("step_")},
            "banner": get_educational_banner()
        }

    # Add other wizard types as needed
    return {
        "document_type": wizard_type.replace("_", " ").title(),
        "condition": condition_name,
        "cached_data": cached_data,
        "banner": get_educational_banner()
    }


def _generate_nursing_diagnoses(condition_name: str) -> List[str]:
    """Generate common nursing diagnoses for the condition"""

    diagnoses_map = {
        "diabetes": [
            "Risk for unstable blood glucose level",
            "Ineffective self-health management",
            "Risk for impaired skin integrity",
            "Deficient knowledge regarding diabetes management"
        ],
        "hypertension": [
            "Risk for decreased cardiac output",
            "Ineffective self-health management",
            "Risk for acute confusion",
            "Deficient knowledge regarding hypertension management"
        ],
        "heart failure": [
            "Decreased cardiac output",
            "Excess fluid volume",
            "Activity intolerance",
            "Anxiety related to dyspnea"
        ]
    }

    condition_lower = condition_name.lower()
    for key, diagnoses in diagnoses_map.items():
        if key in condition_lower:
            return diagnoses

    return ["Risk for complications related to medical condition"]


def _generate_care_goals(condition_name: str) -> List[Dict[str, str]]:
    """Generate SMART care goals for the condition"""

    goals_map = {
        "diabetes": [
            {
                "goal": "Patient will maintain blood glucose levels between 80-180 mg/dL",
                "timeframe": "Throughout hospitalization",
                "measurable": "Blood glucose readings q6h"
            },
            {
                "goal": "Patient will demonstrate proper insulin injection technique",
                "timeframe": "Prior to discharge",
                "measurable": "Return demonstration with 100% accuracy"
            }
        ],
        "hypertension": [
            {
                "goal": "Patient will maintain blood pressure <140/90 mmHg",
                "timeframe": "Within 24 hours of medication adjustment",
                "measurable": "BP readings q4h"
            }
        ],
        "heart failure": [
            {
                "goal": "Patient will maintain fluid balance",
                "timeframe": "Daily",
                "measurable": "Daily weight stable within 2 lbs of baseline"
            }
        ]
    }

    condition_lower = condition_name.lower()
    for key, goals in goals_map.items():
        if key in condition_lower:
            return goals

    return [{
        "goal": "Patient will demonstrate improved condition management",
        "timeframe": "Prior to discharge",
        "measurable": "Patient verbalization and demonstration"
    }]
