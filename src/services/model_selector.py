# services/model_selector.py
"""
Centralized model selection policy for different AI tasks.
Maps task types and complexity levels to appropriate OpenAI models.
"""
from enum import Enum


class TaskType(str, Enum):
    """Enumeration of supported AI task types."""
    TRIAGE = "triage"
    READABILITY = "readability"
    EDUCATION = "education"
    SUMMARIZE = "summarize"
    CHAT = "chat"
    ANALYSIS = "analysis"


def choose_model(task: TaskType, level: str | None = None, complexity: str | None = None) -> str:
    """
    Centralized policy for OpenAI model selection.

    Args:
        task: High-level task category from TaskType enum
        level: Audience level - "public", "allied", "nurse", "physician"
        complexity: Task complexity - "low", "medium", "high"

    Returns:
        OpenAI model name string

    Model Selection Policy:
        - Fast/Simple tasks: gpt-4o-mini (cost-effective, fast)
        - Standard tasks: gpt-4o (balanced performance/cost)
        - Complex/Nuanced tasks: gpt-4 (highest quality reasoning)
        
    Task-specific policies:
        - Triage/Readability: Always use gpt-4o-mini (speed prioritized)
        - Education:
            - Nurse/Physician level: gpt-4 (clinical accuracy crucial)
            - High complexity: gpt-4 (detailed explanations needed)
            - Standard: gpt-4o (good balance)
        - Summarize:
            - High complexity: gpt-4 (nuanced understanding)
            - Standard: gpt-4o-mini (sufficient for most summaries)
        - Chat/Analysis: gpt-4o (good interactive performance)
    """
    # Default to fast, cost-effective model
    model = "gpt-4o-mini"

    # Education tasks require higher quality for clinical accuracy
    if task == TaskType.EDUCATION:
        if level in ["nurse", "physician"]:
            return "gpt-4"  # Clinical accuracy crucial
        if (complexity or "").lower() == "high":
            return "gpt-4"  # Complex educational content
        return "gpt-4o"  # Standard educational content

    # Summarization complexity determines model choice
    if task == TaskType.SUMMARIZE:
        if (complexity or "").lower() == "high":
            return "gpt-4"  # Complex medical summaries
        return "gpt-4o-mini"  # Standard summaries

    # Chat and analysis benefit from balanced model
    if task in [TaskType.CHAT, TaskType.ANALYSIS]:
        return "gpt-4o"

    # Triage and readability prioritize speed
    if task in [TaskType.TRIAGE, TaskType.READABILITY]:
        return "gpt-4o-mini"

    return model


def get_available_models() -> list[str]:
    """
    Get list of available OpenAI models used by this application.
    
    Returns:
        List of model names that may be selected by choose_model()
    """
    return [
        "gpt-4o-mini",  # Fast, cost-effective
        "gpt-4o",       # Balanced performance
        "gpt-4",        # Highest quality
    ]


def get_model_info(model: str) -> dict[str, str]:
    """
    Get information about a specific model.
    
    Args:
        model: OpenAI model name
        
    Returns:
        Dictionary with model information
    """
    model_info = {
        "gpt-4o-mini": {
            "description": "Fast and cost-effective model for simple tasks",
            "use_case": "Triage, readability, simple summaries",
            "cost": "Low",
            "speed": "Fast"
        },
        "gpt-4o": {
            "description": "Balanced performance and cost for standard tasks",
            "use_case": "Education, chat, standard analysis",
            "cost": "Medium",
            "speed": "Medium"
        },
        "gpt-4": {
            "description": "Highest quality reasoning for complex tasks",
            "use_case": "Clinical education, complex summaries, detailed analysis",
            "cost": "High",
            "speed": "Slower"
        }
    }
    
    return model_info.get(model, {
        "description": "Unknown model",
        "use_case": "Not specified",
        "cost": "Unknown",
        "speed": "Unknown"
    })
