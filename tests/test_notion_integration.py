"""
Tests for the Notion-GitHub integration.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from routers.webhooks import verify_github_signature, process_github_event
from services.notion_service import NotionService
from utils.config import Settings


class TestWebhookSecurity:
    """Test webhook security features."""
    
    def test_verify_github_signature_valid(self):
        """Test that valid signatures are accepted."""
        payload = b'{"test": "payload"}'
        secret = "my_secret"
        # Generate the expected signature
        import hmac
        import hashlib
        expected_sig = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        
        assert verify_github_signature(payload, expected_sig, secret) is True
    
    def test_verify_github_signature_invalid(self):
        """Test that invalid signatures are rejected."""
        payload = b'{"test": "payload"}'
        secret = "my_secret"
        invalid_sig = "sha256=invalid_signature"
        
        assert verify_github_signature(payload, invalid_sig, secret) is False
    
    def test_verify_github_signature_missing_secret(self):
        """Test that missing secret is rejected."""
        payload = b'{"test": "payload"}'
        
        assert verify_github_signature(payload, "sha256=anything", "") is False
        assert verify_github_signature(payload, "", "secret") is False


class TestNotionService:
    """Test Notion service functionality."""
    
    @pytest.fixture
    def notion_service(self):
        """Create a NotionService instance with mocked settings."""
        with patch('services.notion_service.get_settings') as mock_settings:
            mock_settings.return_value = Settings(
                NOTION_TOKEN="test_token",
                NOTION_DATABASE_ID="test_db_id"
            )
            return NotionService()
    
    def test_create_rich_text(self, notion_service):
        """Test rich text creation."""
        result = notion_service._create_rich_text("test text")
        expected = [{"type": "text", "text": {"content": "test text"}}]
        assert result == expected
    
    def test_create_text_block(self, notion_service):
        """Test text block creation."""
        result = notion_service._create_text_block("test content")
        expected = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": "test content"}}]
            }
        }
        assert result == expected
    
    @pytest.mark.asyncio
    async def test_handle_push_event(self, notion_service):
        """Test handling of push events."""
        test_data = {
            "repository": {
                "name": "test-repo",
                "full_name": "user/test-repo",
                "html_url": "https://github.com/user/test-repo"
            },
            "commits": [
                {
                    "message": "Test commit",
                    "author": {"name": "Test User"}
                }
            ],
            "pusher": {"name": "Test User"},
            "ref": "refs/heads/main",
            "compare": "https://github.com/user/test-repo/compare/abc123..def456"
        }
        
        with patch.object(notion_service, 'create_page', new=AsyncMock()) as mock_create:
            await notion_service.handle_push_event(test_data)
            
            # Verify create_page was called
            mock_create.assert_called_once()
            
            # Check the properties passed to create_page
            args, kwargs = mock_create.call_args
            properties = args[0]
            
            assert "Title" in properties
            assert "Type" in properties
            assert properties["Type"]["select"]["name"] == "Push"
            assert properties["Repository"]["rich_text"][0]["text"]["content"] == "user/test-repo"


class TestWebhookIntegration:
    """Test webhook integration functionality."""
    
    @pytest.mark.asyncio
    async def test_process_github_event_push(self):
        """Test processing of push events."""
        test_data = {
            "repository": {"name": "test", "full_name": "user/test"},
            "commits": [],
            "pusher": {"name": "user"},
            "ref": "refs/heads/main"
        }
        
        with patch('routers.webhooks.NotionService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            await process_github_event("push", test_data, "test-delivery-id")
            
            mock_service.handle_push_event.assert_called_once_with(test_data)
    
    @pytest.mark.asyncio
    async def test_process_github_event_unhandled(self):
        """Test processing of unhandled event types."""
        test_data = {"test": "data"}
        
        with patch('routers.webhooks.NotionService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            await process_github_event("unknown_event", test_data, "test-delivery-id")
            
            # No handler methods should be called for unknown events
            assert not mock_service.handle_push_event.called
            assert not mock_service.handle_pull_request_event.called
            assert not mock_service.handle_issue_event.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])