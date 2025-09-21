"""Test OpenAI integration with proper mocking according to project patterns."""
import pytest
from unittest.mock import MagicMock, patch
from services.summarize_service import ChatGPTError, summarize_text, call_chatgpt


def test_call_chatgpt_returns_text():
    """Test the call_chatgpt function with proper mocking."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Test response from OpenAI"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    # Mock at the service level where the client is used
    with patch('services.summarize_service.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = call_chatgpt("test prompt")
        
        assert result == "Test response from OpenAI"
        mock_client.chat.completions.create.assert_called_once()


def test_call_chatgpt_raises_when_no_client():
    """Test that call_chatgpt raises ChatGPTError when client is not configured."""
    with patch('services.summarize_service.get_client') as mock_get_client:
        mock_get_client.return_value = None
        
        with pytest.raises(ChatGPTError) as exc_info:
            call_chatgpt("test prompt")
        
        assert "OpenAI client is not configured" in str(exc_info.value)


def test_summarize_text():
    """Test the summarize_text function with proper mocking following AI Nurse Florence patterns."""
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a summary from chat completion"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch('services.summarize_service.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = summarize_text("test prompt for summarization", model="gpt-4o-mini")
        
        # Check the actual structure based on AI Nurse Florence service patterns
        assert isinstance(result, dict)
        assert "banner" in result
        assert "Draft for clinician review — not medical advice. No PHI stored." in result["banner"]
        
        # The summarized content should be in the response
        # Check if it's in 'content', 'text', or direct string response
        content_found = False
        for key in ['summary', 'content', 'text', 'result']:
            if key in result and "This is a summary from chat completion" in str(result[key]):
                content_found = True
                break
        
        # If not in a nested key, check if the whole response contains the content
        if not content_found:
            assert "This is a summary from chat completion" in str(result)
        
        mock_client.chat.completions.create.assert_called_once()


def test_summarize_text_with_debug():
    """Debug test to see actual response structure."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Debug summary content"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    with patch('services.summarize_service.get_client') as mock_get_client:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        result = summarize_text("debug test", model="gpt-4o-mini")
        
        # Print the actual structure for debugging
        print(f"Actual result structure: {result}")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Basic validation that we get a response
        assert result is not None
