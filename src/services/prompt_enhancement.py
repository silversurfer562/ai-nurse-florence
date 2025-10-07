"""
Prompt Enhancement Service - AI Nurse Florence
Medical query clarification and terminology normalization
Following OpenAI Integration from coding instructions
"""

import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class PromptEnhancementService:
    """
    Service for enhancing and clarifying medical queries
    Following Service Layer Architecture from coding instructions
    """

    # Medical abbreviations and their expansions
    MEDICAL_ABBREVIATIONS = {
        # Vital signs
        "bp": "blood pressure",
        "hr": "heart rate",
        "rr": "respiratory rate",
        "temp": "temperature",
        "o2": "oxygen",
        "spo2": "oxygen saturation",
        # Common medical terms
        "mi": "myocardial infarction",
        "copd": "chronic obstructive pulmonary disease",
        "chf": "congestive heart failure",
        "cad": "coronary artery disease",
        "dm": "diabetes mellitus",
        "htn": "hypertension",
        "sob": "shortness of breath",
        "n/v": "nausea and vomiting",
        "loc": "loss of consciousness",
        "gi": "gastrointestinal",
        "uti": "urinary tract infection",
        "dvt": "deep vein thrombosis",
        "pe": "pulmonary embolism",
        "cvd": "cardiovascular disease",
        "cva": "cerebrovascular accident",
        "tia": "transient ischemic attack",
        "stemi": "ST-elevation myocardial infarction",
        "nstemi": "non-ST-elevation myocardial infarction",
        # Lab values
        "wbc": "white blood cell count",
        "rbc": "red blood cell count",
        "hgb": "hemoglobin",
        "hct": "hematocrit",
        "plt": "platelet count",
        "bun": "blood urea nitrogen",
        "cr": "creatinine",
        "na": "sodium",
        "k": "potassium",
        "cl": "chloride",
        "hco3": "bicarbonate",
        "gfr": "glomerular filtration rate",
        # Procedures
        "cpr": "cardiopulmonary resuscitation",
        "ekg": "electrocardiogram",
        "ecg": "electrocardiogram",
        "ct": "computed tomography",
        "mri": "magnetic resonance imaging",
        "cxr": "chest x-ray",
        # Routes
        "po": "by mouth",
        "iv": "intravenous",
        "im": "intramuscular",
        "sq": "subcutaneous",
        "sc": "subcutaneous",
        "prn": "as needed",
        "bid": "twice daily",
        "tid": "three times daily",
        "qid": "four times daily",
        "qd": "once daily",
        "hs": "at bedtime",
    }

    # Vague query indicators
    VAGUE_PATTERNS = [
        r"\b(what about|tell me about|explain|how about)\b",
        r"\b(general|basic|simple|quick)\s+(info|information)\b",
        r"^\s*\w{1,10}\s*$",  # Single word or very short query
    ]

    # Medical context keywords that indicate specific queries
    SPECIFIC_CONTEXT = [
        "dose",
        "dosage",
        "side effects",
        "contraindication",
        "interaction",
        "adverse event",
        "administration",
        "mechanism",
        "indication",
        "treatment",
        "diagnosis",
        "symptom",
        "monitoring",
        "protocol",
    ]

    def __init__(self):
        self.edu_banner = "Educational use only — not medical advice. No PHI stored."

    def enhance_prompt(self, query: str) -> Dict[str, any]:
        """
        Enhance and clarify a medical query

        Args:
            query: Original user query

        Returns:
            Dict with enhanced query and metadata
        """
        enhanced = query.strip()
        modifications = []

        # Step 1: Normalize medical terminology (expand abbreviations)
        normalized, norm_changes = self.normalize_medical_terminology(enhanced)
        if norm_changes:
            enhanced = normalized
            modifications.extend(norm_changes)

        # Step 2: Detect vague queries
        is_vague = self.is_vague_query(enhanced)

        # Step 3: Generate clarification questions if needed
        clarifications = None
        if is_vague:
            clarifications = self.generate_clarification_questions(enhanced)

        # Step 4: Add context hints
        context_hints = self.extract_context_hints(enhanced)

        return {
            "banner": self.edu_banner,
            "original_query": query,
            "enhanced_query": enhanced,
            "is_vague": is_vague,
            "modifications": modifications if modifications else None,
            "clarifications": clarifications,
            "context_hints": context_hints,
        }

    def normalize_medical_terminology(self, query: str) -> tuple[str, List[str]]:
        """
        Normalize medical abbreviations and terminology

        Args:
            query: Input query string

        Returns:
            Tuple of (normalized_query, list_of_changes)
        """
        normalized = query
        changes = []

        # Expand medical abbreviations (case-insensitive word boundary matching)
        for abbrev, expansion in self.MEDICAL_ABBREVIATIONS.items():
            pattern = re.compile(r"\b" + re.escape(abbrev) + r"\b", re.IGNORECASE)
            if pattern.search(normalized):
                normalized = pattern.sub(expansion, normalized)
                changes.append(f'Expanded "{abbrev}" to "{expansion}"')

        return normalized, changes

    def is_vague_query(self, query: str) -> bool:
        """
        Detect if a query is too vague or needs clarification

        Args:
            query: Query string to analyze

        Returns:
            True if query is vague, False otherwise
        """
        query_lower = query.lower()

        # Check for vague patterns
        for pattern in self.VAGUE_PATTERNS:
            if re.search(pattern, query_lower):
                return True

        # Check if query has specific medical context
        has_context = any(keyword in query_lower for keyword in self.SPECIFIC_CONTEXT)

        # Very short queries without specific context are likely vague
        word_count = len(query.split())
        if word_count <= 3 and not has_context:
            return True

        return False

    def generate_clarification_questions(self, query: str) -> List[str]:
        """
        Generate clarification questions for vague queries

        Args:
            query: Original query

        Returns:
            List of clarification questions
        """
        questions = []
        query_lower = query.lower()

        # Drug-related queries
        if any(
            word in query_lower for word in ["drug", "medication", "med", "medicine"]
        ):
            questions.append(
                "Are you asking about dosing, side effects, or interactions?"
            )
            questions.append(
                "Do you need information for a specific patient population (pediatric, geriatric, pregnancy)?"
            )

        # Disease/condition queries
        elif any(word in query_lower for word in ["disease", "condition", "diagnosis"]):
            questions.append(
                "Are you looking for symptoms, causes, treatment, or prevention?"
            )
            questions.append(
                "Do you need patient education materials or clinical guidelines?"
            )

        # Procedure queries
        elif any(
            word in query_lower
            for word in ["procedure", "surgery", "operation", "intervention"]
        ):
            questions.append(
                "Are you asking about indications, contraindications, or post-operative care?"
            )
            questions.append("Do you need procedural steps or patient education?")

        # Generic vague query
        else:
            questions.append("What specific aspect are you interested in?")
            questions.append(
                "Is this for patient education, clinical decision support, or research?"
            )

        # Always ask for urgency/priority
        questions.append("Is this for immediate clinical use or general learning?")

        return questions

    def extract_context_hints(self, query: str) -> Dict[str, bool]:
        """
        Extract context hints from the query to guide response

        Args:
            query: Query string

        Returns:
            Dict of boolean flags for different contexts
        """
        query_lower = query.lower()

        return {
            "patient_education": any(
                word in query_lower
                for word in ["patient", "explain to", "discharge", "teaching"]
            ),
            "clinical_decision": any(
                word in query_lower
                for word in [
                    "treatment",
                    "diagnosis",
                    "management",
                    "protocol",
                    "guideline",
                ]
            ),
            "drug_information": any(
                word in query_lower
                for word in ["drug", "medication", "dose", "interaction", "side effect"]
            ),
            "emergency": any(
                word in query_lower
                for word in ["emergency", "urgent", "stat", "code", "critical"]
            ),
            "research": any(
                word in query_lower
                for word in ["research", "study", "evidence", "literature", "pubmed"]
            ),
        }

    def add_clinical_context(self, query: str, care_setting: str = None) -> str:
        """
        Add clinical context tags to improve AI response relevance

        Args:
            query: Original query
            care_setting: Clinical setting (ICU, ED, med-surg, etc.)

        Returns:
            Query with added context
        """
        context_tags = []

        if care_setting:
            context_tags.append(f"[Care Setting: {care_setting}]")

        # Add professional context
        context_tags.append("[Audience: Registered Nurse]")

        # Add evidence-based tag
        context_tags.append("[Require: Evidence-based clinical information]")

        if context_tags:
            return f"{' '.join(context_tags)} {query}"

        return query


def get_prompt_enhancement_service() -> PromptEnhancementService:
    """Dependency injection for prompt enhancement service"""
    return PromptEnhancementService()
