"""
Tests for OpenAI client API key validation.

This module tests that the OpenAI client properly validates API keys
and rejects common placeholder or invalid keys.
"""
import pytest
import os
from unittest.mock import patch
from services.openai_client import get_client, _is_valid_api_key


class TestOpenAIClientValidation:
    """Test OpenAI client API key validation functionality."""
    
    def test_placeholder_key_validation(self):
        """Test that placeholder keys are rejected."""
        placeholder_keys = [
            "sk-NEW_Y********HERE",  # The specific key from the error
            "your-api-key-here",
            "your-openai-key-here", 
            "sk-placeholder",
            "sk-example",
            "sk-test-key",
            "sk-dummy",
            "sk-fake",
            "sk-***************",
        ]
        
        for key in placeholder_keys:
            assert not _is_valid_api_key(key), f"Key '{key}' should be invalid"
    
    def test_invalid_format_keys(self):
        """Test that keys with invalid format are rejected."""
        invalid_keys = [
            "",  # Empty
            "api-key-without-sk-prefix", 
            "sk-short",  # Too short
            "sk-",  # Just prefix
            "not-a-key-at-all",
        ]
        
        for key in invalid_keys:
            assert not _is_valid_api_key(key), f"Key '{key}' should be invalid"
    
    def test_valid_format_keys(self):
        """Test that keys with valid format are accepted."""
        valid_keys = [
            "sk-1234567890abcdef1234567890abcdef1234567890abcdef",  # 51 chars
            "sk-abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJK",   # Mixed case
            "sk-" + "x" * 48,  # Minimum reasonable length
        ]
        
        for key in valid_keys:
            assert _is_valid_api_key(key), f"Key '{key}' should be valid"
    
    def test_get_client_with_placeholder_key(self):
        """Test that get_client returns None for placeholder keys."""
        # Clear the cached client and mock the module-level API key
        from services import openai_client
        openai_client._client = None
        original_key = openai_client.OPENAI_API_KEY
        
        try:
            openai_client.OPENAI_API_KEY = "sk-NEW_Y********HERE"
            client = get_client()
            assert client is None, "Client should be None for placeholder key"
        finally:
            openai_client.OPENAI_API_KEY = original_key
    
    def test_get_client_with_empty_key(self):
        """Test that get_client returns None for empty key."""
        # Clear the cached client and mock the module-level API key
        from services import openai_client
        openai_client._client = None
        original_key = openai_client.OPENAI_API_KEY
        
        try:
            openai_client.OPENAI_API_KEY = ""
            client = get_client()
            assert client is None, "Client should be None for empty key"
        finally:
            openai_client.OPENAI_API_KEY = original_key
    
    def test_get_client_with_valid_key(self):
        """Test that get_client returns a client for valid format keys."""
        # Clear the cached client and mock the module-level API key
        from services import openai_client
        openai_client._client = None
        original_key = openai_client.OPENAI_API_KEY
        
        try:
            valid_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
            openai_client.OPENAI_API_KEY = valid_key
            client = get_client()
            assert client is not None, "Client should not be None for valid format key"
        finally:
            openai_client.OPENAI_API_KEY = original_key