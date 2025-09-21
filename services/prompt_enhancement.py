"""
Prompt enhancement helpers.

This module provides deterministic, test-friendly prompt enhancements and
clarification suggestions for various service types (summarize, education,
and disease lookup).
"""
from typing import Tuple, Optional
from utils.logging import get_logger

logger = get_logger(__name__)

# Vague prompts that should trigger clarification questions
VAGUE_PROMPTS = {
    "help": "What specific medical topic would you like information about?",
    "tell me more": "Which medical condition or treatment would you like to learn about?",
    "information": "What specific medical information are you looking for?",
    "explain": "What medical concept would you like me to explain?",
    "summary": "Which medical condition or topic would you like summarized?",
}

COMMON_CONDITIONS = [
    "diabetes",
    "hypertension",
    "asthma",
    "cancer",
    "arthritis",
    "depression",
    "anxiety",
    "alzheimer",
    "parkinsons",
    "copd",
]


def enhance_prompt(prompt: str, service_type: str = "general") -> Tuple[str, bool, Optional[str]]:
    """Return (effective_prompt, needs_clarification, clarification_question)."""
    if not prompt or not prompt.strip():
        return prompt, True, "Please provide a medical question or topic to proceed."

    normalized = prompt.lower().strip()

    # Short-circuit long prompts (likely already well-formed)
    if len(normalized.split()) > 18:
        return prompt, False, None

    # Exact vague matches → request clarification
    if normalized in VAGUE_PROMPTS:
        return prompt, True, VAGUE_PROMPTS[normalized]

    # Service-specific enhancements
    if service_type == "summarize":
        enhanced, changed = enhance_summarize_prompt(normalized)
        if changed:
            return enhanced, False, None

    if service_type == "education":
        enhanced, changed = enhance_education_prompt(normalized)
        if changed:
            return enhanced, False, None

    if service_type == "disease":
        enhanced, changed = enhance_disease_prompt(normalized)
        if changed:
            return enhanced, False, None

    # Very short prompts without medical terms → clarification
    if len(normalized.split()) <= 2 and not any(c in normalized for c in COMMON_CONDITIONS):
        return prompt, True, "Could you provide more details about your medical question?"

    return prompt, False, None


def enhance_summarize_prompt(prompt: str) -> Tuple[str, bool]:
    """Return an enhanced prompt for summarize requests, if applicable."""
    if prompt.startswith("summarize"):
        topic = prompt.replace("summarize", "", 1).strip()
        if topic:
            # Tests expect the phrase 'clinical summary' in enhanced prompts
            return (
                f"Provide a clinical summary of {topic} including key symptoms, diagnostic criteria, and treatment approaches",
                True,
            )

    # For bare condition names with summarize service type
    for cond in COMMON_CONDITIONS:
        if cond in prompt and "summar" not in prompt:
            return (f"Provide a clinical summary of {cond} including key symptoms, diagnostic criteria, and treatment approaches", True)

    return prompt, False


def enhance_education_prompt(prompt: str) -> Tuple[str, bool]:
    for key in ("about", "explain", "what is", "info"):
        if key in prompt:
            parts = prompt.split(key, 1)
            if len(parts) > 1 and parts[1].strip():
                topic = parts[1].strip()
                return (
                    f"Provide patient education material about {topic} including symptoms, causes, treatments, and when to seek medical attention",
                    True,
                )
    
    # For bare condition names with education service type
    for cond in COMMON_CONDITIONS:
        if cond in prompt:
            return (f"Provide patient-friendly information about {cond} including symptoms, treatments, and self-care tips", True)
    
    return prompt, False


def enhance_disease_prompt(prompt: str) -> Tuple[str, bool]:
    for cond in COMMON_CONDITIONS:
        if cond in prompt:
            return (f"Provide clinical information about {cond} for healthcare professionals", True)
    return prompt, False
