"""
Quality Improvement Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
Quality metrics tracking and improvement initiative workflows
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime

from ...utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/quality-improvement",
    tags=["wizards", "quality-improvement"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"}
    }
)

# Wizard session storage (Redis in production)
_wizard_sessions: Dict[str, Dict[str, Any]] = {}

class QualityImprovementStepData(BaseModel):
    """Data model for quality improvement step submission."""
    step_data: Dict[str, Any]
    metrics: Optional[List[Dict[str, Any]]] = None

@router.post("/start")
async def start_quality_improvement(
    initiative_type: str = "general",
    department: Optional[str] = None
):
    """Start quality improvement wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "quality_improvement",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 5,
        "completed_steps": [],
        "data": {
            "initiative_type": initiative_type,
            "department": department,
            "problem_identification": {},
            "baseline_metrics": {},
            "improvement_plan": {},
            "implementation": {},
            "evaluation": {}
        }
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "quality_improvement",
        "current_step": 1,
        "total_steps": 5,
        "step_title": "Problem Identification",
        "step_description": "Define the quality issue or opportunity for improvement",
        "fields": [
            {"name": "problem_statement", "type": "textarea", "required": True},
            {"name": "affected_population", "type": "text", "label": "Patient/staff population affected", "required": True},
            {"name": "scope", "type": "select", "options": ["Unit-level", "Department-level", "Hospital-wide", "System-wide"], "required": True},
            {"name": "current_impact", "type": "textarea", "label": "Current impact on care/outcomes", "required": True},
            {"name": "root_causes", "type": "textarea", "label": "Suspected root causes", "required": True},
            {"name": "stakeholders", "type": "textarea", "required": True}
        ],
        "educational_note": "Use SMART criteria when defining the problem. Consider using root cause analysis tools like fishbone diagrams."
    }

@router.get("/{wizard_id}/status")
async def get_quality_improvement_status(wizard_id: str):
    """Get quality improvement wizard status following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": session["wizard_type"],
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "completed_steps": session["completed_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "data": session["data"]
    }

@router.post("/{wizard_id}/step/{step_number}")
async def submit_quality_improvement_step(
    wizard_id: str,
    step_number: int,
    step_data: QualityImprovementStepData
):
    """Submit quality improvement step data following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number != session["current_step"]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid step. Expected step {session['current_step']}, got step {step_number}"
        )

    # Store step data based on step number
    step_mapping = {
        1: "problem_identification",
        2: "baseline_metrics",
        3: "improvement_plan",
        4: "implementation",
        5: "evaluation"
    }

    if step_number in step_mapping:
        session["data"][step_mapping[step_number]] = step_data.step_data

    # Track metrics if provided
    if step_data.metrics:
        if "tracked_metrics" not in session["data"]:
            session["data"]["tracked_metrics"] = []
        session["data"]["tracked_metrics"].extend(step_data.metrics)

    # Mark step as completed
    if step_number not in session["completed_steps"]:
        session["completed_steps"].append(step_number)

    # Move to next step
    if step_number < session["total_steps"]:
        session["current_step"] = step_number + 1
        next_step_info = _get_step_info(step_number + 1)
    else:
        next_step_info = None

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_completed": step_number,
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "next_step": next_step_info
    }

@router.get("/{wizard_id}/step/{step_number}")
async def get_quality_improvement_step(wizard_id: str, step_number: int):
    """Get quality improvement step information."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number < 1 or step_number > session["total_steps"]:
        raise HTTPException(status_code=422, detail="Invalid step number")

    step_info = _get_step_info(step_number)

    # Get previously entered data if exists
    step_mapping = {
        1: "problem_identification",
        2: "baseline_metrics",
        3: "improvement_plan",
        4: "implementation",
        5: "evaluation"
    }

    existing_data = session["data"].get(step_mapping.get(step_number, ""), {})

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_number": step_number,
        "existing_data": existing_data,
        **step_info
    }

@router.get("/{wizard_id}/metrics")
async def get_quality_metrics(wizard_id: str):
    """Get tracked quality metrics for the initiative."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]
    metrics = session["data"].get("tracked_metrics", [])

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "metrics": metrics,
        "baseline_data": session["data"].get("baseline_metrics", {}),
        "evaluation_data": session["data"].get("evaluation", {})
    }

@router.delete("/{wizard_id}")
async def cancel_quality_improvement(wizard_id: str):
    """Cancel and delete quality improvement wizard session."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    del _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "message": "Quality improvement wizard session cancelled",
        "wizard_id": wizard_id
    }

def _get_step_info(step_number: int) -> Dict[str, Any]:
    """Get step configuration information."""

    steps = {
        1: {
            "step_title": "Problem Identification",
            "step_description": "Define the quality issue or opportunity for improvement",
            "fields": [
                {"name": "problem_statement", "type": "textarea", "required": True},
                {"name": "affected_population", "type": "text", "label": "Patient/staff population affected", "required": True},
                {"name": "scope", "type": "select", "options": ["Unit-level", "Department-level", "Hospital-wide", "System-wide"], "required": True},
                {"name": "current_impact", "type": "textarea", "label": "Current impact on care/outcomes", "required": True},
                {"name": "root_causes", "type": "textarea", "label": "Suspected root causes", "required": True},
                {"name": "stakeholders", "type": "textarea", "required": True}
            ],
            "educational_note": "Use SMART criteria when defining the problem. Consider using root cause analysis tools like fishbone diagrams."
        },
        2: {
            "step_title": "Baseline Metrics",
            "step_description": "Establish current performance and measurement criteria",
            "fields": [
                {"name": "primary_metric", "type": "text", "required": True},
                {"name": "primary_metric_value", "type": "number", "label": "Current value", "required": True},
                {"name": "secondary_metrics", "type": "textarea", "required": False},
                {"name": "data_source", "type": "text", "label": "How metrics are collected", "required": True},
                {"name": "measurement_frequency", "type": "select", "options": ["Daily", "Weekly", "Monthly", "Quarterly"], "required": True},
                {"name": "target_value", "type": "number", "required": True},
                {"name": "target_timeline", "type": "text", "label": "Timeline to reach target", "required": True}
            ],
            "educational_note": "Ensure metrics are measurable, relevant, and align with organizational quality goals."
        },
        3: {
            "step_title": "Improvement Plan",
            "step_description": "Develop PDSA (Plan-Do-Study-Act) improvement strategy",
            "fields": [
                {"name": "aim_statement", "type": "textarea", "label": "SMART aim statement", "required": True},
                {"name": "interventions", "type": "textarea", "label": "Planned interventions/changes", "required": True},
                {"name": "evidence_base", "type": "textarea", "label": "Evidence supporting interventions", "required": True},
                {"name": "resources_needed", "type": "textarea", "required": True},
                {"name": "team_members", "type": "textarea", "label": "QI team members and roles", "required": True},
                {"name": "timeline", "type": "textarea", "label": "Implementation timeline", "required": True},
                {"name": "barriers_anticipated", "type": "textarea", "required": True},
                {"name": "mitigation_strategies", "type": "textarea", "required": True}
            ],
            "educational_note": "Use evidence-based practices. Plan for small tests of change (PDSA cycles) before full implementation."
        },
        4: {
            "step_title": "Implementation",
            "step_description": "Document implementation progress and adjustments",
            "fields": [
                {"name": "start_date", "type": "date", "required": True},
                {"name": "interventions_completed", "type": "textarea", "required": True},
                {"name": "staff_training_completed", "type": "boolean", "required": True},
                {"name": "process_changes_made", "type": "textarea", "required": True},
                {"name": "challenges_encountered", "type": "textarea", "required": True},
                {"name": "adjustments_made", "type": "textarea", "label": "PDSA adjustments", "required": True},
                {"name": "stakeholder_feedback", "type": "textarea", "required": False},
                {"name": "current_adoption_rate", "type": "number", "unit": "%", "required": True}
            ],
            "educational_note": "Document all PDSA cycles. Be prepared to adapt the plan based on real-world feedback."
        },
        5: {
            "step_title": "Evaluation & Sustainability",
            "step_description": "Assess outcomes and plan for sustained improvement",
            "fields": [
                {"name": "end_date", "type": "date", "required": True},
                {"name": "final_metric_value", "type": "number", "label": "Final primary metric value", "required": True},
                {"name": "target_achieved", "type": "boolean", "required": True},
                {"name": "outcome_summary", "type": "textarea", "required": True},
                {"name": "lessons_learned", "type": "textarea", "required": True},
                {"name": "sustainability_plan", "type": "textarea", "label": "How improvements will be sustained", "required": True},
                {"name": "monitoring_frequency", "type": "select", "label": "Ongoing monitoring plan", "options": ["Daily", "Weekly", "Monthly", "Quarterly"], "required": True},
                {"name": "spread_potential", "type": "textarea", "label": "Potential to spread to other units", "required": False},
                {"name": "next_steps", "type": "textarea", "required": True}
            ],
            "educational_note": "Celebrate successes! Share results with stakeholders. Plan for ongoing monitoring to prevent backsliding."
        }
    }

    return steps.get(step_number, {})

@router.get("/templates")
async def get_quality_improvement_templates():
    """Get common quality improvement initiative templates."""

    return {
        "banner": get_educational_banner(),
        "templates": [
            {
                "name": "Fall Prevention",
                "description": "Reduce patient falls and fall-related injuries",
                "common_metrics": ["Falls per 1000 patient days", "Fall-related injury rate", "Post-fall huddle completion rate"],
                "evidence_based_interventions": [
                    "Hourly rounding",
                    "Fall risk assessment on admission",
                    "Yellow socks/wristbands for high-risk patients",
                    "Bed alarms for appropriate patients",
                    "Environmental safety checks"
                ]
            },
            {
                "name": "Pressure Injury Prevention",
                "description": "Prevent hospital-acquired pressure injuries",
                "common_metrics": ["Hospital-acquired pressure injury rate", "Skin assessment completion rate", "Turn compliance rate"],
                "evidence_based_interventions": [
                    "Braden scale assessment on admission",
                    "Turn schedule implementation",
                    "Specialty mattress utilization",
                    "Nutritional support",
                    "Heel offloading protocols"
                ]
            },
            {
                "name": "CAUTI Prevention",
                "description": "Reduce catheter-associated urinary tract infections",
                "common_metrics": ["CAUTI rate per 1000 catheter days", "Catheter utilization ratio", "Appropriate indication documentation"],
                "evidence_based_interventions": [
                    "Daily catheter necessity assessment",
                    "Aseptic insertion technique",
                    "Proper catheter maintenance",
                    "Early removal protocols",
                    "Nurse-driven removal protocols"
                ]
            },
            {
                "name": "Medication Safety",
                "description": "Reduce medication errors and adverse drug events",
                "common_metrics": ["Medication error rate", "Adverse drug event rate", "High-alert medication compliance"],
                "evidence_based_interventions": [
                    "Double-check protocols for high-alert meds",
                    "Barcode scanning compliance",
                    "Medication reconciliation",
                    "Smart pump utilization",
                    "Pharmacist involvement in rounds"
                ]
            },
            {
                "name": "Hand Hygiene Compliance",
                "description": "Improve hand hygiene compliance rates",
                "common_metrics": ["Hand hygiene compliance rate", "Healthcare-associated infection rates", "Audit completion rate"],
                "evidence_based_interventions": [
                    "Alcohol-based hand sanitizer placement",
                    "Visual reminders at point of care",
                    "Direct observation audits",
                    "Peer accountability",
                    "Leadership rounding with feedback"
                ]
            },
            {
                "name": "Patient Satisfaction",
                "description": "Improve patient experience and satisfaction scores",
                "common_metrics": ["HCAHPS scores", "Response rate to call lights", "Hourly rounding completion"],
                "evidence_based_interventions": [
                    "Bedside shift report",
                    "Hourly rounding with 4 Ps (Pain, Potty, Position, Possessions)",
                    "Leader rounding",
                    "Discharge phone calls",
                    "White board communication"
                ]
            }
        ]
    }