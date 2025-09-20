"""
Tests for the prompt enhancement service.
"""
import pytest
from services.prompt_enhancement import (
    enhance_prompt,
    enhance_summarize_prompt,
    enhance_education_prompt,
    enhance_disease_prompt
)

class TestPromptEnhancement:
    """Test prompt enhancement functionality."""
    
    def test_empty_prompt(self):
        """Test that empty prompts trigger a clarification request."""
        prompt = ""
        enhanced, needs_clarification, question = enhance_prompt(prompt)
        assert needs_clarification is True
        assert question is not None
        assert "provide" in question.lower()
    
    def test_vague_prompt(self):
        """Test that vague prompts trigger a clarification request."""
        prompt = "help"
        enhanced, needs_clarification, question = enhance_prompt(prompt)
        assert needs_clarification is True
        assert question is not None
    
    def test_long_prompt_unchanged(self):
        """Test that longer, well-formed prompts are not changed."""
        prompt = "What are the most effective treatments for type 2 diabetes in patients who also have hypertension and are over 65 years old?"
        enhanced, needs_clarification, _ = enhance_prompt(prompt)
        assert needs_clarification is False
        assert enhanced == prompt
    
    def test_enhance_summarize_prompt(self):
        """Test summarize prompt enhancement."""
        prompt = "summarize diabetes"
        enhanced, needs_clarification, _ = enhance_prompt(prompt, "summarize")
        assert needs_clarification is False
        assert "clinical summary" in enhanced
        assert "diabetes" in enhanced
        assert enhanced != prompt
    
    def test_enhance_education_prompt(self):
        """Test education prompt enhancement."""
        prompt = "about asthma"
        enhanced, needs_clarification, _ = enhance_prompt(prompt, "education")
        assert needs_clarification is False
        assert "patient education" in enhanced
        assert "asthma" in enhanced
        assert enhanced != prompt
    
    def test_enhance_disease_prompt(self):
        """Test disease prompt enhancement."""
        prompt = "hypertension"
        enhanced, needs_clarification, _ = enhance_prompt(prompt, "disease")
        assert needs_clarification is False
        assert "clinical information" in enhanced
        assert "hypertension" in enhanced
        assert enhanced != prompt
    
    def test_bare_condition_detection(self):
        """Test that bare condition names are enhanced appropriately."""
        for service_type, expected_phrase in [
            ("summarize", "clinical summary"),
            ("education", "patient-friendly"),
            ("disease", "clinical information")
        ]:
            prompt = "diabetes"
            enhanced, needs_clarification, _ = enhance_prompt(prompt, service_type)
            assert needs_clarification is False
            assert expected_phrase in enhanced
            assert "diabetes" in enhanced
    
    def test_short_nonmedical_prompt(self):
        """Test that short prompts without medical terms ask for clarification."""
        prompt = "hi there"
        enhanced, needs_clarification, question = enhance_prompt(prompt)
        assert needs_clarification is True
        assert question is not None