"""
Risk Assessment Service - Clinical risk scoring
Following caching strategy patterns

Implements evidence-based clinical risk assessment tools:
- Morse Falls Scale: Falls risk assessment (validated tool)
- Braden Scale: Pressure ulcer/injury risk assessment (validated tool)
- Modified Early Warning Score (MEWS): Clinical deterioration detection

All algorithms based on peer-reviewed clinical literature and
standard healthcare practice.
"""

from typing import Any, Dict, List

from src.utils.redis_cache import cached


class RiskAssessmentService:
    """
    Clinical risk assessment and early warning systems
    Following Service Layer Architecture from coding instructions
    """

    def __init__(self):
        self.edu_banner = "Educational use only — not medical advice. No PHI stored."

    @cached(ttl_seconds=300)  # 5-minute cache for risk calculations
    async def calculate_falls_risk(
        self, patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Morse Falls Scale assessment

        Validated tool for falls risk assessment. Scores range from 0-125.
        Based on Morse JM, Morse RM, Tylko SJ. Development of a scale to
        identify the fall-prone patient. Can J Aging. 1989;8(4):366-77.

        Args:
            patient_data: Dict with keys:
                - history_of_falling (str): "yes" or "no"
                - secondary_diagnosis (str): "yes" or "no"
                - ambulatory_aid (str): "none", "crutches_cane_walker", "furniture"
                - iv_heparin_lock (str): "yes" or "no"
                - gait (str): "normal", "weak", "impaired"
                - mental_status (str): "oriented", "forgets_limitations"

        Returns:
            Dict with score, risk_level, and interventions
        """
        score = 0
        factors = []

        # History of falling (25 points)
        if patient_data.get("history_of_falling", "").lower() == "yes":
            score += 25
            factors.append("History of falling")

        # Secondary diagnosis (15 points)
        if patient_data.get("secondary_diagnosis", "").lower() == "yes":
            score += 15
            factors.append("Multiple diagnoses")

        # Ambulatory aid (0-30 points)
        amb_aid = patient_data.get("ambulatory_aid", "").lower()
        if amb_aid in ["crutches", "cane", "walker", "crutches_cane_walker"]:
            score += 15
            factors.append("Uses assistive device")
        elif amb_aid == "furniture":
            score += 30
            factors.append("Furniture walking")

        # IV/Heparin lock (20 points)
        if patient_data.get("iv_heparin_lock", "").lower() == "yes":
            score += 20
            factors.append("IV therapy")

        # Gait (0-20 points)
        gait = patient_data.get("gait", "").lower()
        if gait == "weak":
            score += 10
            factors.append("Weak gait")
        elif gait == "impaired":
            score += 20
            factors.append("Impaired gait")

        # Mental status (0-15 points)
        mental = patient_data.get("mental_status", "").lower()
        if mental in ["forgets_limitations", "forgets"]:
            score += 15
            factors.append("Forgets limitations")

        # Determine risk level
        if score >= 51:
            risk_level = "high"
            risk_category = "High Risk"
        elif score >= 25:
            risk_level = "moderate"
            risk_category = "Moderate Risk"
        else:
            risk_level = "low"
            risk_category = "Low Risk"

        # Generate interventions
        interventions = self._generate_falls_interventions(score, factors)

        return {
            "banner": self.edu_banner,
            "assessment_type": "falls_risk",
            "scale": "Morse Falls Scale",
            "score": score,
            "max_score": 125,
            "risk_level": risk_level,
            "risk_category": risk_category,
            "risk_factors": factors,
            "interventions": interventions,
            "assessment_date": patient_data.get("assessment_date", ""),
        }

    def _generate_falls_interventions(
        self, score: int, factors: List[str]
    ) -> List[str]:
        """Generate evidence-based falls prevention interventions"""
        interventions = []

        # Universal interventions
        interventions.append("Orient patient to environment")
        interventions.append("Keep call bell within reach")
        interventions.append("Keep bed in lowest position")

        if score >= 25:  # Moderate risk
            interventions.append("Perform hourly rounding")
            interventions.append("Place falls risk sign on door/chart")
            interventions.append("Consider bed/chair alarm")
            interventions.append("Ensure adequate lighting")
            interventions.append("Keep frequently used items within reach")

        if score >= 51:  # High risk
            interventions.append("1:1 observation if appropriate")
            interventions.append("Non-skid footwear required")
            interventions.append("Consider moving closer to nurse station")
            interventions.append("PT/OT consultation for gait assessment")
            interventions.append("Medication review for fall-risk drugs")
            interventions.append("Consider hip protectors if applicable")

        # Factor-specific interventions
        if "Impaired gait" in factors or "Weak gait" in factors:
            interventions.append("Ambulate with assistance only")
            interventions.append("Assess need for assistive device")

        if "Forgets limitations" in factors:
            interventions.append("Frequent reorientation to limitations")
            interventions.append("Consider cognitive assessment")

        if "IV therapy" in factors:
            interventions.append("Ensure IV pole is stable and accessible")
            interventions.append("Assist with ambulation when IV attached")

        return interventions

    async def calculate_pressure_ulcer_risk(
        self, patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Braden Scale pressure ulcer/injury risk assessment

        Validated tool for pressure injury risk. Scores range from 6-23.
        Lower scores indicate higher risk.
        Based on Bergstrom N, Braden BJ, Laguzza A, Holman V. The Braden
        Scale for Predicting Pressure Sore Risk. Nurs Res. 1987;36(4):205-10.

        Args:
            patient_data: Dict with keys (each scored 1-4, except friction 1-3):
                - sensory_perception (int): 1-4 (1=completely limited, 4=no impairment)
                - moisture (int): 1-4 (1=constantly moist, 4=rarely moist)
                - activity (int): 1-4 (1=bedfast, 4=walks frequently)
                - mobility (int): 1-4 (1=completely immobile, 4=no limitation)
                - nutrition (int): 1-4 (1=very poor, 4=excellent)
                - friction_shear (int): 1-3 (1=problem, 3=no apparent problem)

        Returns:
            Dict with score, risk_level, and prevention strategies
        """
        # Get scores with defaults (mid-range = moderate risk)
        sensory = patient_data.get("sensory_perception", 3)
        moisture = patient_data.get("moisture", 3)
        activity = patient_data.get("activity", 3)
        mobility = patient_data.get("mobility", 3)
        nutrition = patient_data.get("nutrition", 3)
        friction = patient_data.get("friction_shear", 2)

        # Calculate total score (range: 6-23)
        total_score = sensory + moisture + activity + mobility + nutrition + friction

        # Identify risk factors (scores of 1-2 are concerning)
        risk_factors = []
        if sensory <= 2:
            risk_factors.append("Impaired sensory perception")
        if moisture <= 2:
            risk_factors.append("Excessive moisture exposure")
        if activity <= 2:
            risk_factors.append("Limited activity")
        if mobility <= 2:
            risk_factors.append("Limited mobility")
        if nutrition <= 2:
            risk_factors.append("Poor nutritional status")
        if friction <= 1:
            risk_factors.append("Friction and shear issues")

        # Determine risk level (standard Braden cutoffs)
        if total_score <= 9:
            risk_level = "severe"
            risk_category = "Severe Risk (Very High Risk)"
        elif total_score <= 12:
            risk_level = "high"
            risk_category = "High Risk"
        elif total_score <= 14:
            risk_level = "moderate"
            risk_category = "Moderate Risk"
        elif total_score <= 18:
            risk_level = "mild"
            risk_category = "Mild Risk (At Risk)"
        else:
            risk_level = "low"
            risk_category = "Low Risk (No Risk)"

        # Generate prevention strategies
        interventions = self._generate_pressure_injury_interventions(
            total_score, risk_factors, patient_data
        )

        return {
            "banner": self.edu_banner,
            "assessment_type": "pressure_ulcer_risk",
            "scale": "Braden Scale",
            "score": total_score,
            "max_score": 23,
            "min_score": 6,
            "risk_level": risk_level,
            "risk_category": risk_category,
            "risk_factors": risk_factors,
            "subscores": {
                "sensory_perception": sensory,
                "moisture": moisture,
                "activity": activity,
                "mobility": mobility,
                "nutrition": nutrition,
                "friction_shear": friction,
            },
            "interventions": interventions,
            "assessment_date": patient_data.get("assessment_date", ""),
        }

    def _generate_pressure_injury_interventions(
        self, score: int, factors: List[str], patient_data: Dict[str, Any]
    ) -> List[str]:
        """Generate evidence-based pressure injury prevention strategies"""
        interventions = []

        # Universal interventions
        interventions.append("Assess skin daily for pressure areas")
        interventions.append("Keep skin clean and dry")
        interventions.append("Avoid massaging bony prominences")

        if score <= 18:  # At risk or higher
            interventions.append("Reposition every 2 hours minimum")
            interventions.append("Use pressure-relieving devices")
            interventions.append("Protect heels with pillows or devices")
            interventions.append("Elevate head of bed ≤30° when possible")
            interventions.append("Use draw sheet for repositioning")

        if score <= 14:  # Moderate risk or higher
            interventions.append("Consider specialty mattress/overlay")
            interventions.append("Nutritional consultation for protein supplementation")
            interventions.append("Document skin assessment every shift")
            interventions.append("Use barrier cream for moisture protection")
            interventions.append("Float heels off bed surface")

        if score <= 12:  # High risk
            interventions.append(
                "Consider low-air-loss or alternating pressure mattress"
            )
            interventions.append("Reposition every 1-2 hours")
            interventions.append("Wound care nurse consultation")
            interventions.append("Optimize nutrition (protein 1.2-1.5g/kg/day)")
            interventions.append(
                "Consider prophylactic foam dressings for bony prominences"
            )

        if score <= 9:  # Severe risk
            interventions.append("IMMEDIATE wound care specialist consult")
            interventions.append("Advanced pressure-relieving surface required")
            interventions.append("Consider continuous repositioning schedule")
            interventions.append("Aggressive nutritional support")
            interventions.append("Consider prealbumin/albumin levels")

        # Factor-specific interventions
        if "Excessive moisture exposure" in factors:
            interventions.append("Implement moisture management protocol")
            interventions.append("Use moisture-wicking underpads")
            interventions.append("Check for incontinence q2h minimum")

        if "Poor nutritional status" in factors:
            interventions.append("Dietary consult for high-protein diet")
            interventions.append("Consider nutritional supplements")
            interventions.append("Monitor intake and output")

        if "Friction and shear issues" in factors:
            interventions.append("Use lift devices for all transfers")
            interventions.append("Apply skin protectant to areas at risk")
            interventions.append("Ensure proper positioning with pillows")

        return interventions

    async def calculate_deterioration_risk(
        self, vital_signs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modified Early Warning Score (MEWS) calculation

        Validated tool for detecting clinical deterioration. Scores range from 0-14.
        Higher scores indicate increased risk of adverse outcomes.
        Based on Subbe CP, Kruger M, Rutherford P, Gemmel L. Validation of a
        modified Early Warning Score in medical admissions. QJM. 2001;94(10):521-6.

        Args:
            vital_signs: Dict with keys:
                - systolic_bp (int): Systolic blood pressure in mmHg
                - heart_rate (int): Heart rate in bpm
                - respiratory_rate (int): Respiratory rate per minute
                - temperature (float): Temperature in Celsius
                - avpu (str): Alert/Voice/Pain/Unresponsive

        Returns:
            Dict with MEWS score, risk_level, and monitoring recommendations
        """
        score = 0
        alerts = []

        # Systolic BP scoring (3 points max)
        sbp = vital_signs.get("systolic_bp", 120)
        if sbp <= 70:
            score += 3
            alerts.append("Critical hypotension")
        elif sbp <= 80:
            score += 2
            alerts.append("Severe hypotension")
        elif sbp <= 100:
            score += 1
            alerts.append("Hypotension")
        elif sbp >= 200:
            score += 2
            alerts.append("Severe hypertension")

        # Heart Rate scoring (3 points max)
        hr = vital_signs.get("heart_rate", 80)
        if hr < 40:
            score += 2
            alerts.append("Severe bradycardia")
        elif hr < 50:
            score += 1
            alerts.append("Bradycardia")
        elif hr >= 130:
            score += 3
            alerts.append("Severe tachycardia")
        elif hr >= 110:
            score += 2
            alerts.append("Tachycardia")
        elif hr >= 100:
            score += 1
            alerts.append("Mild tachycardia")

        # Respiratory Rate scoring (3 points max)
        rr = vital_signs.get("respiratory_rate", 16)
        if rr < 9:
            score += 2
            alerts.append("Severe bradypnea")
        elif rr >= 30:
            score += 3
            alerts.append("Severe tachypnea")
        elif rr >= 25:
            score += 2
            alerts.append("Tachypnea")
        elif rr >= 21:
            score += 1
            alerts.append("Mild tachypnea")

        # Temperature scoring (2 points max)
        temp = vital_signs.get("temperature", 37.0)
        if temp < 35.0:
            score += 2
            alerts.append("Hypothermia")
        elif temp >= 38.5:
            score += 2
            alerts.append("High fever")

        # AVPU (3 points max)
        avpu = vital_signs.get("avpu", "alert").lower()
        if avpu == "unresponsive" or avpu == "u":
            score += 3
            alerts.append("Unresponsive")
        elif avpu == "pain" or avpu == "p":
            score += 2
            alerts.append("Responds to pain only")
        elif avpu == "voice" or avpu == "v":
            score += 1
            alerts.append("Responds to voice only")

        # Determine risk level and monitoring frequency
        if score >= 5:
            risk_level = "critical"
            risk_category = "Critical - Immediate Intervention"
            monitoring_freq = "Continuous monitoring"
        elif score >= 3:
            risk_level = "high"
            risk_category = "High Risk - Urgent Review"
            monitoring_freq = "Monitor q15-30min"
        elif score >= 1:
            risk_level = "moderate"
            risk_category = "Moderate Risk - Increased Monitoring"
            monitoring_freq = "Monitor q1-2h"
        else:
            risk_level = "low"
            risk_category = "Low Risk - Routine Monitoring"
            monitoring_freq = "Monitor q4h"

        # Generate escalation recommendations
        interventions = self._generate_mews_interventions(score, alerts, vital_signs)

        return {
            "banner": self.edu_banner,
            "assessment_type": "clinical_deterioration",
            "scale": "Modified Early Warning Score (MEWS)",
            "mews_score": score,
            "max_score": 14,
            "risk_level": risk_level,
            "risk_category": risk_category,
            "alerts": alerts,
            "vital_signs": {
                "systolic_bp": sbp,
                "heart_rate": hr,
                "respiratory_rate": rr,
                "temperature": temp,
                "avpu": avpu,
            },
            "monitoring_frequency": monitoring_freq,
            "interventions": interventions,
            "assessment_time": vital_signs.get("assessment_time", ""),
        }

    def _generate_mews_interventions(
        self, score: int, alerts: List[str], vital_signs: Dict[str, Any]
    ) -> List[str]:
        """Generate evidence-based escalation and intervention recommendations"""
        interventions = []

        if score == 0:
            # Low risk - routine care
            interventions.append("Continue routine monitoring q4h")
            interventions.append("Document vital signs per protocol")
            return interventions

        if score >= 1:  # Moderate risk
            interventions.append("Increase monitoring frequency to q1-2h")
            interventions.append("Notify charge nurse of MEWS score")
            interventions.append("Review patient chart for contributing factors")
            interventions.append("Ensure IV access if not present")

        if score >= 3:  # High risk
            interventions.append("NOTIFY PROVIDER IMMEDIATELY")
            interventions.append("Continuous vital sign monitoring")
            interventions.append("Obtain full set of vital signs including O2 sat")
            interventions.append("Consider rapid response team activation")
            interventions.append("Prepare for potential transfer to higher acuity")
            interventions.append("Review medications for contributing factors")

        if score >= 5:  # Critical
            interventions.append("ACTIVATE RAPID RESPONSE TEAM NOW")
            interventions.append("Initiate continuous monitoring")
            interventions.append("Establish/verify patent IV access")
            interventions.append("Prepare emergency equipment at bedside")
            interventions.append("Consider ICU-level care")
            interventions.append("Notify attending physician stat")

        # Alert-specific interventions
        if "Critical hypotension" in alerts or "Severe hypotension" in alerts:
            interventions.append("Consider fluid bolus per protocol")
            interventions.append("Assess for signs of shock")
            interventions.append("Review recent medications (antihypertensives)")

        if "Severe tachycardia" in alerts or "Tachycardia" in alerts:
            interventions.append("Obtain 12-lead EKG")
            interventions.append("Assess for pain, anxiety, fever")
            interventions.append("Check cardiac history")

        if "Severe tachypnea" in alerts or "Tachypnea" in alerts:
            interventions.append("Apply pulse oximetry")
            interventions.append("Assess lung sounds")
            interventions.append("Consider supplemental oxygen")
            interventions.append("Check for respiratory distress")

        if "High fever" in alerts:
            interventions.append("Obtain temperature via reliable route")
            interventions.append("Consider blood cultures if febrile")
            interventions.append("Review for infection sources")
            interventions.append("Implement cooling measures as ordered")

        if "Hypothermia" in alerts:
            interventions.append("Implement warming measures")
            interventions.append("Assess for sepsis")
            interventions.append("Check core temperature")

        if "Unresponsive" in alerts or "Responds to pain only" in alerts:
            interventions.append("IMMEDIATE provider notification")
            interventions.append("Assess airway, breathing, circulation")
            interventions.append("Check blood glucose")
            interventions.append("Review recent medications (sedatives, narcotics)")
            interventions.append("Consider stroke protocol if appropriate")

        return interventions


def get_risk_assessment_service() -> RiskAssessmentService:
    """Dependency injection for risk assessment service"""
    return RiskAssessmentService()
