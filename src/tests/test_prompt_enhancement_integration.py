"""
Integration tests for the prompt enhancement functionality.

These tests verify that the prompt enhancement is correctly integrated
with the summarize service and endpoint.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

@pytest.mark.integration
class TestPromptEnhancementIntegration:
    """Integration tests for prompt enhancement."""
    
    @patch('services.prompt_enhancement.enhance_prompt')
    @patch('services.summarize_service.call_chatgpt')
    def test_summarize_with_enhanced_prompt(self, mock_call_chatgpt, mock_enhance_prompt):
        """Test that summarization endpoint uses enhanced prompts."""
        # Setup mocks
        mock_enhance_prompt.return_value = ("Enhanced prompt", False, None)
        mock_call_chatgpt.return_value = "Test summary"
        
        # Make request
        response = client.post(
            "/summarize/chat",
            json={"prompt": "summarize diabetes", "model": "gpt-4o-mini"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test summary"
        assert data["prompt_enhanced"] is True
        assert data["original_prompt"] == "summarize diabetes"
        assert data["enhanced_prompt"] == "Enhanced prompt"
        
        # Verify mocks were called correctly
        mock_enhance_prompt.assert_called_once_with("summarize diabetes", "summarize")
        mock_call_chatgpt.assert_called_once_with("Enhanced prompt", model="gpt-4o-mini")
    
    @patch('services.prompt_enhancement.enhance_prompt')
    def test_summarize_needs_clarification(self, mock_enhance_prompt):
        """Test that the endpoint returns clarification questions when needed."""
        # Setup mock
        mock_enhance_prompt.return_value = (
            "Original prompt", 
            True, 
            "What specific aspect of diabetes would you like summarized?"
        )
        
        # Make request
        response = client.post(
            "/summarize/chat",
            json={"prompt": "diabetes"}
        )
        
        # Check response
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert data["detail"]["needs_clarification"] is True
        assert "clarification_question" in data["detail"]
        assert "What specific aspect" in data["detail"]["clarification_question"]
        
        # Verify mock was called correctly
        mock_enhance_prompt.assert_called_once_with("diabetes", "summarize")
    
    @patch('services.prompt_enhancement.enhance_prompt')
    @patch('services.summarize_service.call_chatgpt')
    def test_summarize_without_enhancement(self, mock_call_chatgpt, mock_enhance_prompt):
        """Test that good prompts are processed without enhancement."""
        # Setup mocks
        mock_enhance_prompt.return_value = (
            "Original good prompt", 
            False, 
            None
        )
        mock_call_chatgpt.return_value = "Test summary"
        
        # Make request
        response = client.post(
            "/summarize/chat",
            json={"prompt": "Original good prompt"}
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test summary"
        assert "prompt_enhanced" not in data
        
        # Verify mocks were called correctly
        mock_enhance_prompt.assert_called_once()
        mock_call_chatgpt.assert_called_once_with("Original good prompt", model="gpt-4o-mini")