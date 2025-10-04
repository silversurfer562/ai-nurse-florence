"""
Claude AI Service - AI Nurse Florence

Provides AI-powered features using Anthropic's Claude API.
Claude excels at medical/clinical content generation with better instruction following
and longer context windows (200K tokens) compared to other models.
"""

import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic

    _has_anthropic = True
except ImportError:
    _has_anthropic = False
    Anthropic = None  # type: ignore


class ClaudeService:
    """
    Claude AI service for medical content generation.

    Features:
    - Patient education materials
    - Clinical documentation
    - Drug interaction analysis
    - SBAR report generation
    - Discharge instructions
    - 200K token context window
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.available = False

        if not _has_anthropic:
            logger.warning(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
            return

        if not self.api_key:
            logger.warning(
                "ANTHROPIC_API_KEY not set. Claude features will be unavailable."
            )
            return

        try:
            self.client = Anthropic(api_key=self.api_key)
            self.available = True
            logger.info("✓ Claude AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate AI response using Claude.

        Args:
            prompt: The main prompt/question
            context: Optional context to prepend
            model: Claude model to use (default: claude-3-5-sonnet)
            max_tokens: Maximum response tokens
            temperature: Randomness (0-1)

        Returns:
            Dict with response and metadata
        """
        if not self.available:
            return {
                "response": "",
                "error": "Claude AI service not available. Check API key.",
                "service_note": "ANTHROPIC_API_KEY not configured",
            }

        try:
            # Build messages
            system_message = "You are a highly knowledgeable medical AI assistant helping nurses and healthcare providers. Provide accurate, evidence-based information. Be clear, professional, and concise."

            if context:
                system_message += f"\n\nContext: {context}"

            # Call Claude API
            message = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=[{"role": "user", "content": prompt}],
            )

            # Extract response
            response_text = message.content[0].text if message.content else ""

            return {
                "response": response_text,
                "model": model,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                },
                "service": "claude",
                "service_note": f"Powered by Claude ({model})",
            }

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {
                "response": "",
                "error": str(e),
                "service_note": "Claude API request failed",
            }

    async def generate_patient_education(
        self,
        condition: str,
        patient_context: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate patient education material.

        Args:
            condition: Medical condition or topic
            patient_context: Patient demographics, reading level, etc.
            language: Output language code

        Returns:
            Patient education content
        """
        context = f"Generate patient education material for: {condition}"

        if patient_context:
            age = patient_context.get("age", "adult")
            reading_level = patient_context.get("reading_level", "8th grade")
            context += f"\nPatient: {age}, reading level: {reading_level}"

        prompt = f"""Create patient education material about {condition}.

Requirements:
- Use simple, clear language (8th grade reading level)
- Include: What it is, symptoms, treatment, when to seek help
- Be empathetic and encouraging
- Use bullet points for key information
- Include practical daily living tips

Format as markdown with clear sections."""

        return await self.generate_response(prompt, context=context)

    async def generate_sbar_report(
        self,
        situation: str,
        background: str,
        assessment: str,
        recommendations: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate or enhance SBAR report.

        Args:
            situation: Current situation
            background: Patient background
            assessment: Clinical assessment
            recommendations: Recommended actions

        Returns:
            Enhanced SBAR report
        """
        prompt = f"""Create a professional SBAR report based on this information:

**Situation:** {situation}

**Background:** {background}

**Assessment:** {assessment}

**Recommendation:** {recommendations or "Please provide recommendations"}

Format as a clear, professional SBAR report suitable for handoff communication.
Include all critical information and use medical terminology appropriately."""

        context = (
            "You are helping a nurse create a handoff report using the SBAR format."
        )

        return await self.generate_response(prompt, context=context, temperature=0.3)

    async def generate_discharge_instructions(
        self,
        diagnosis: str,
        medications: list[str],
        follow_up: str,
        restrictions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate patient discharge instructions.

        Args:
            diagnosis: Primary diagnosis
            medications: List of medications
            follow_up: Follow-up care plan
            restrictions: Activity restrictions

        Returns:
            Discharge instructions
        """
        meds_list = "\n".join([f"- {med}" for med in medications])

        prompt = f"""Create discharge instructions for a patient:

**Diagnosis:** {diagnosis}

**Medications:**
{meds_list}

**Follow-up:** {follow_up}

**Restrictions:** {restrictions or "None specified"}

Create clear, patient-friendly discharge instructions including:
1. What to do at home
2. How to take medications
3. Warning signs to watch for
4. When to seek emergency care
5. Follow-up appointments

Use simple language and bullet points."""

        context = "Creating discharge instructions for patient and family education."

        return await self.generate_response(prompt, context=context)

    async def simplify_fda_label(
        self, fda_text: str, section: str = "general"
    ) -> Dict[str, Any]:
        """
        Convert FDA drug label to plain language.

        Args:
            fda_text: Original FDA label text
            section: Which section (indications, warnings, etc.)

        Returns:
            Plain language version
        """
        prompt = f"""Convert this FDA drug label text into simple, patient-friendly language:

{fda_text}

Requirements:
- 8th grade reading level
- Remove medical jargon or explain it
- Use short sentences
- Keep all important safety information
- Make it easy to understand

Output the simplified version:"""

        context = f"Converting FDA {section} information to patient-friendly language."

        return await self.generate_response(prompt, context=context)


# Global service instance
claude_service = ClaudeService()


# Service registration
async def register_claude_service():
    """Register Claude service for dependency injection."""
    logger.info("Claude AI service registered")
    return claude_service
