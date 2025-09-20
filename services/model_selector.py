# services/model_selector.py
from enum import Enum


class TaskType(str, Enum):
    TRIAGE = "triage"
    READABILITY = "readability"
    EDUCATION = "education"
    SUMMARIZE = "summarize"


def choose_model(task: TaskType, level: str | None = None, complexity: str | None = None) -> str:
    """
    Centralized policy for model selection.

    Args:
        task: high-level task category.
        level: audience level, e.g., "public" | "allied" | "nurse".
        complexity: "low" | "medium" | "high" (heuristic for depth/nuance).

    Policy:
      - Triage / Readability -> gpt-4o-mini (fast, cheap)
      - Education:
          - nurse -> gpt-5.1 (nuance, layered terminology)
          - public/allied:
              - complexity high -> gpt-5.1
              - else            -> gpt-4o
      - Summarize:
          - complexity high -> gpt-5.1
          - else            -> gpt-4o-mini
    """
    # Fast default
    model = "gpt-4o-mini"

    if task == TaskType.EDUCATION:
        if level == "nurse":
            return "gpt-5.1"
        # public/allied
        if (complexity or "").lower() == "high":
            return "gpt-5.1"
        return "gpt-4o"

    if task == TaskType.SUMMARIZE:
        return "gpt-5.1" if (complexity or "").lower() == "high" else "gpt-4o-mini"

    # TRIAGE / READABILITY fall back to mini
    return model
