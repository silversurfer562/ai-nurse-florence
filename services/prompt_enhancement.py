"""
Prompt enhancement service to improve user prompts.

This module provides functions to analyze and enhance user prompts,
or generate clarification questions when prompts are unclear.
"""
from typing import Tuple, Optional
from utils.logging import get_logger

logger = get_logger(__name__)

# Common vague prompts and their clarification questions
VAGUE_PROMPTS = {
    "help": "What specific medical topic would you like information about?",
    "tell me more": "Which medical condition or treatment would you like to learn about?",
    "information": "What specific medical information are you looking for?",
    "explain": "What medical concept would you like me to explain?",
    "summary": "Which medical condition or topic would you like summarized?",
    "i need info": "What medical information are you looking for?",
    "can you help": "What medical assistance do you need?",
}

# Medical conditions for pattern matching
COMMON_CONDITIONS = [
    "diabetes", "hypertension", "asthma", "cancer", "arthritis", 
    "depression", "anxiety", "alzheimer", "parkinsons", "copd",
    "heart disease", "stroke", "obesity", "migraine", "epilepsy"
]

def enhance_prompt(prompt: str, service_type: str = "general") -> Tuple[str, bool, Optional[str]]:
    """
    Analyzes a user prompt and enhances it or provides a clarification question.
    
    Args:
        prompt: The user's original prompt
        service_type: Type of service (summarize, education, etc.)
        
    Returns:
        Tuple of (effective_prompt, needs_clarification, clarification_question)
        - effective_prompt: Original or enhanced prompt
        - needs_clarification: Boolean indicating if clarification is needed
        - clarification_question: Question to ask the user if clarification needed
    """
    if not prompt or not prompt.strip():
        return prompt, True, "Please provide a medical question or topic to proceed."
    
    original_prompt = prompt
    normalized_prompt = prompt.lower().strip()
    
    # Skip enhancement for longer, likely well-formed prompts
    if len(normalized_prompt.split()) > 15:
        logger.debug(f"Skipping enhancement for longer prompt: '{prompt}'")
        return prompt, False, None
    
    # Check for exact matches in common vague prompts
    if normalized_prompt in VAGUE_PROMPTS:
        logger.info(f"Clarification needed for vague prompt: '{prompt}'")
        return prompt, True, VAGUE_PROMPTS[normalized_prompt]
    
    # Service-specific enhancements
    if service_type == "summarize":
        enhanced, modified = enhance_summarize_prompt(normalized_prompt)
        if modified:
            logger.info(f"Enhanced summarize prompt: '{prompt}' → '{enhanced}'")
            return enhanced, False, None
    
    elif service_type == "education":
        enhanced, modified = enhance_education_prompt(normalized_prompt)
        if modified:
            logger.info(f"Enhanced education prompt: '{prompt}' → '{enhanced}'")
            return enhanced, False, None
    
    elif service_type == "disease":
        enhanced, modified = enhance_disease_prompt(normalized_prompt)
        if modified:
            logger.info(f"Enhanced disease prompt: '{prompt}' → '{enhanced}'")
            return enhanced, False, None
    
    # Check if prompt is very short with no clear medical terms
    if len(normalized_prompt.split()) <= 2:
        # Check if contains at least one medical term
        if not any(condition in normalized_prompt for condition in COMMON_CONDITIONS):
            logger.info(f"Clarification needed for short prompt: '{prompt}'")
            return prompt, True, "Could you provide more details about your medical question?"
    
    # If we can't enhance, just return the original
    return prompt, False, None

def enhance_summarize_prompt(prompt: str) -> Tuple[str, bool]:
    """
    Enhance prompts for the summarize service.
    
    Args:
        prompt: The normalized prompt
        
    Returns:
        Tuple of (enhanced_prompt, was_modified)
    """
    # Simple enhancement for "summarize X" pattern
    if prompt.startswith("summarize"):
        topic = prompt.replace("summarize", "", 1).strip()
        if topic:
            return f"Provide a clinical summary of {topic} including key symptoms, diagnostic criteria, and treatment approaches", True
    
    # Look for topic without clear instruction
    for condition in COMMON_CONDITIONS:
        if condition in prompt and "summar" not in prompt:
            return f"Summarize key clinical information about {condition} for healthcare professionals", True
    
    return prompt, False

def enhance_education_prompt(prompt: str) -> Tuple[str, bool]:
    """
    Enhance prompts for the patient education service.
    
    Args:
        prompt: The normalized prompt
        
    Returns:
        Tuple of (enhanced_prompt, was_modified)
    """
    # Check for words like "about", "info", "explain" + condition
    info_words = ["about", "info", "explain", "tell me about", "what is"]
    
    for info_word in info_words:
        if info_word in prompt:
            # Extract the topic after the info word
            parts = prompt.split(info_word, 1)
            if len(parts) > 1 and parts[1].strip():
                topic = parts[1].strip()
                return f"Provide patient education material about {topic} including symptoms, causes, treatments, and when to seek medical attention", True
    
    # Check if prompt is just a medical condition
    for condition in COMMON_CONDITIONS:
        if prompt == condition or prompt == f"{condition}?":
            return f"Provide patient-friendly information about {condition} including symptoms, treatments, and self-care tips", True
    
    return prompt, False

def enhance_disease_prompt(prompt: str) -> Tuple[str, bool]:
    """
    Enhance prompts for the disease lookup service.
    
    Args:
        prompt: The normalized prompt
        
    Returns:
        Tuple of (enhanced_prompt, was_modified)
    """
    # For disease lookups, ensure we have a clear condition name
    if len(prompt.split()) <= 2:
        for condition in COMMON_CONDITIONS:
            if condition in prompt:
                return f"Provide clinical information about {condition} for healthcare professionals", True
    
    return prompt, False