# tests/unit/test_summarize_openai.py
"""
Tests for OpenAI integration in summarize service.
Updated to use proper OpenAI chat completions API structure.
"""
import pytest
from unittest.mock import MagicMock

from services.summarize_service import ChatGPTError


def test_call_chatgpt_returns_text(monkeypatch):
    """Test that call_chatgpt returns text from chat completions API."""
    # Create mock for chat completions API
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello from fake chat completion"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    # Patch get_client to return our fake
    monkeypatch.setattr("services.openai_client.get_client", lambda: mock_client)

    from services.summarize_service import call_chatgpt

    result = call_chatgpt("test prompt", model="gpt-4o-mini")
    assert result == "Hello from fake chat completion"
    
    # Verify the API call was made correctly
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4o-mini"
    assert len(call_args[1]["messages"]) == 2
    assert call_args[1]["messages"][0]["role"] == "system"
    assert call_args[1]["messages"][1]["role"] == "user"
    assert call_args[1]["messages"][1]["content"] == "test prompt"


def test_call_chatgpt_raises_when_no_client(monkeypatch):
    """Test that call_chatgpt raises ChatGPTError when client is not configured."""
    # Patch get_client to return None
    monkeypatch.setattr("services.openai_client.get_client", lambda: None)

    from services.summarize_service import call_chatgpt

    with pytest.raises(ChatGPTError) as exc_info:
        call_chatgpt("test")
    
    assert "OpenAI client is not configured" in str(exc_info.value)


def test_call_chatgpt_handles_api_error(monkeypatch):
    """Test that call_chatgpt properly handles API errors."""
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")

    # Patch get_client to return our fake
    monkeypatch.setattr("services.openai_client.get_client", lambda: mock_client)

    from services.summarize_service import call_chatgpt

    with pytest.raises(ChatGPTError) as exc_info:
        call_chatgpt("test prompt")
    
    assert "OpenAI API call failed" in str(exc_info.value)
    assert "API Error" in str(exc_info.value)


def test_call_chatgpt_with_custom_system_message(monkeypatch):
    """Test that call_chatgpt accepts custom system messages."""
    mock_choice = MagicMock()
    mock_choice.message.content = "Custom response"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr("services.openai_client.get_client", lambda: mock_client)

    from services.summarize_service import call_chatgpt

    custom_system = "You are a specialized medical assistant."
    result = call_chatgpt("test prompt", system_message=custom_system)
    
    assert result == "Custom response"
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["messages"][0]["content"] == custom_system


def test_summarize_text(monkeypatch):
    """Test the summarize_text function with the new API."""
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a summary from chat completion"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    monkeypatch.setattr("services.openai_client.get_client", lambda: mock_client)

    from services.summarize_service import summarize_text

    result = summarize_text("test prompt for summarization", model="gpt-4o-mini")
    assert result["text"] == "This is a summary from chat completion"


def test_summarize_text_raises_when_no_client(monkeypatch):
    """Test that summarize_text raises ChatGPTError when client is not configured."""
    monkeypatch.setattr("services.openai_client.get_client", lambda: None)

    from services.summarize_service import summarize_text

    with pytest.raises(ChatGPTError) as exc_info:
        summarize_text("test prompt for summarization")
    
    assert "OpenAI client is not configured" in str(exc_info.value)
