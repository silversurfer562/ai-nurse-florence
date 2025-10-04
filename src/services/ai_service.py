"""
Unified AI Service - AI Nurse Florence

Smart AI service that automatically selects the best available AI provider:
1. Claude (Anthropic) - Primary choice for medical content
2. OpenAI (GPT-4) - Fallback option

Provides transparent failover and consistent API.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class UnifiedAIService:
    """
    Unified AI service with automatic provider selection and fallback.

    Priority order:
    1. Claude (better for medical, cheaper, longer context)
    2. OpenAI (fallback)
    """

    def __init__(self):
        self.claude = None
        self.openai = None
        self.primary_provider = None

        # Try to load Claude
        try:
            from src.services.claude_service import claude_service

            if claude_service.available:
                self.claude = claude_service
                self.primary_provider = "claude"
                logger.info("✓ Primary AI: Claude (Anthropic)")
        except Exception as e:
            logger.warning(f"Claude not available: {e}")

        # Try to load OpenAI as fallback
        try:
            from src.services import get_service

            openai_svc = get_service("openai")
            if openai_svc:
                self.openai = openai_svc
                if not self.primary_provider:
                    self.primary_provider = "openai"
                logger.info("✓ Fallback AI: OpenAI (GPT-4)")
        except Exception as e:
            logger.warning(f"OpenAI not available: {e}")

        if not self.primary_provider:
            logger.error("❌ No AI providers available!")

    async def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        prefer_provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response with automatic provider selection.

        Args:
            prompt: The main prompt
            context: Optional context
            prefer_provider: Force specific provider ("claude" or "openai")

        Returns:
            AI response with metadata
        """
        # Determine which provider to use
        providers_to_try = []

        if prefer_provider == "claude" and self.claude:
            providers_to_try = [("claude", self.claude)]
        elif prefer_provider == "openai" and self.openai:
            providers_to_try = [("openai", self.openai)]
        else:
            # Auto-select based on availability
            if self.claude:
                providers_to_try.append(("claude", self.claude))
            if self.openai:
                providers_to_try.append(("openai", self.openai))

        # Try each provider
        last_error = None
        for provider_name, provider in providers_to_try:
            try:
                logger.info(f"Trying AI provider: {provider_name}")

                if provider_name == "claude":
                    response = await provider.generate_response(prompt, context=context)
                else:  # openai
                    response = await provider.generate_response(prompt, context)

                # Success!
                if response.get("response"):
                    response["provider_used"] = provider_name
                    if len(providers_to_try) > 1:
                        response["has_fallback"] = True
                    return response

            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}")
                last_error = str(e)
                continue

        # All providers failed
        return {
            "response": "",
            "error": last_error or "No AI providers available",
            "service_note": "All AI providers unavailable. Please configure ANTHROPIC_API_KEY or OPENAI_API_KEY",
        }

    async def generate_patient_education(
        self,
        condition: str,
        patient_context: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Generate patient education material."""
        # Prefer Claude for medical content
        if self.claude:
            return await self.claude.generate_patient_education(
                condition, patient_context, language
            )
        elif self.openai:
            # Fallback to OpenAI with custom prompt
            prompt = f"Create patient education material for {condition} at 8th grade reading level."
            return await self.openai.generate_response(
                prompt, "Patient education material"
            )

        return {"response": "", "error": "No AI provider available"}

    async def generate_sbar_report(
        self,
        situation: str,
        background: str,
        assessment: str,
        recommendations: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate SBAR report."""
        if self.claude:
            return await self.claude.generate_sbar_report(
                situation, background, assessment, recommendations
            )
        elif self.openai:
            prompt = f"Create SBAR report:\nS: {situation}\nB: {background}\nA: {assessment}\nR: {recommendations}"
            return await self.openai.generate_response(prompt, "SBAR report generation")

        return {"response": "", "error": "No AI provider available"}

    async def generate_discharge_instructions(
        self,
        diagnosis: str,
        medications: list[str],
        follow_up: str,
        restrictions: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate discharge instructions."""
        if self.claude:
            return await self.claude.generate_discharge_instructions(
                diagnosis, medications, follow_up, restrictions
            )
        elif self.openai:
            meds = ", ".join(medications)
            prompt = f"Create discharge instructions for {diagnosis}. Meds: {meds}. Follow-up: {follow_up}."
            return await self.openai.generate_response(prompt, "Discharge instructions")

        return {"response": "", "error": "No AI provider available"}

    async def simplify_fda_label(
        self, fda_text: str, section: str = "general"
    ) -> Dict[str, Any]:
        """Simplify FDA label to plain language."""
        if self.claude:
            return await self.claude.simplify_fda_label(fda_text, section)
        elif self.openai:
            prompt = f"Simplify this FDA text to 8th grade reading level:\n\n{fda_text}"
            return await self.openai.generate_response(
                prompt, "FDA label simplification"
            )

        return {"response": "", "error": "No AI provider available"}

    def get_status(self) -> Dict[str, Any]:
        """Get AI service status."""
        return {
            "primary_provider": self.primary_provider,
            "claude_available": bool(self.claude and self.claude.available),
            "openai_available": bool(self.openai),
            "has_fallback": bool(self.claude and self.openai),
        }


# Global unified service
ai_service = UnifiedAIService()


# Service registration
async def register_ai_service():
    """Register unified AI service."""
    status = ai_service.get_status()
    logger.info(f"Unified AI Service: {status}")
    return ai_service
