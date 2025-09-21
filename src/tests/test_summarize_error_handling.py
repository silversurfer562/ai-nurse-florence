"""
Tests for the summarize service with the new error handling.
"""
import pytest
from unittest.mock import MagicMock, patch
from services.summarize_service import call_chatgpt, ChatGPTError
from utils.exceptions import ExternalServiceException

# Test the new error handling in call_chatgpt
def test_call_chatgpt_client_not_configured():
    """Test that call_chatgpt raises ChatGPTError when client is not configured."""
    with patch('services.summarize_service.get_client', return_value=None):
        with pytest.raises(ChatGPTError) as excinfo:
            call_chatgpt("test prompt")
        assert "OpenAI client is not configured" in str(excinfo.value)
        assert isinstance(excinfo.value, ExternalServiceException)
        assert excinfo.value.service_name == "openai"
        assert excinfo.value.status_code == 503


def test_call_chatgpt_api_error():
    """Test that call_chatgpt handles API errors properly."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API error")
    
    with patch('services.summarize_service.get_client', return_value=mock_client):
        with pytest.raises(ChatGPTError) as excinfo:
            call_chatgpt("test prompt")
        assert "OpenAI API call failed" in str(excinfo.value)
        assert isinstance(excinfo.value, ExternalServiceException)
        assert excinfo.value.service_name == "openai"
        assert "API error" in str(excinfo.value)
        assert excinfo.value.status_code == 503