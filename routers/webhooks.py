"""
GitHub webhook endpoints for Notion integration.

This module provides webhook endpoints that GitHub can call to send events
to Notion in real-time, enabling better tracking of repository changes.
"""
import hashlib
import hmac
import json
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from utils.config import get_settings
from utils.logging import get_logger
from services.notion_service import NotionService
from utils.exceptions import ExternalServiceException

logger = get_logger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify that the webhook payload came from GitHub.
    
    Args:
        payload: The raw request body
        signature: The X-Hub-Signature-256 header from GitHub
        secret: The webhook secret configured in GitHub
        
    Returns:
        True if the signature is valid, False otherwise
    """
    if not signature or not secret:
        return False
        
    # GitHub sends the signature as "sha256=<hash>"
    if not signature.startswith("sha256="):
        return False
        
    expected_signature = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def require_webhook_config():
    """Dependency to ensure webhook configuration is present."""
    settings = get_settings()
    if not settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=503,
            detail="GitHub webhook secret not configured"
        )
    if not settings.NOTION_TOKEN or not settings.NOTION_DATABASE_ID:
        raise HTTPException(
            status_code=503,
            detail="Notion integration not configured"
        )


@router.post("/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    _: None = Depends(require_webhook_config)
):
    """
    Handle GitHub webhook events and send them to Notion.
    
    This endpoint receives webhook events from GitHub and processes them
    in the background to create or update pages in Notion.
    """
    settings = get_settings()
    
    # Get headers
    signature = request.headers.get("X-Hub-Signature-256", "")
    event_type = request.headers.get("X-GitHub-Event", "")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")
    
    # Read the raw payload
    payload = await request.body()
    
    # Verify the signature
    if not verify_github_signature(payload, signature, settings.GITHUB_WEBHOOK_SECRET):
        logger.warning(
            "Invalid webhook signature",
            extra={"delivery_id": delivery_id, "event_type": event_type}
        )
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse the JSON payload
    try:
        data = json.loads(payload.decode())
    except json.JSONDecodeError:
        logger.error("Invalid JSON payload", extra={"delivery_id": delivery_id})
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # Log the received event
    logger.info(
        f"Received GitHub webhook: {event_type}",
        extra={
            "delivery_id": delivery_id,
            "event_type": event_type,
            "repository": data.get("repository", {}).get("full_name"),
            "action": data.get("action")
        }
    )
    
    # Process the event in the background
    background_tasks.add_task(
        process_github_event,
        event_type,
        data,
        delivery_id
    )
    
    return JSONResponse(
        status_code=200,
        content={"status": "received", "delivery_id": delivery_id}
    )


async def process_github_event(event_type: str, data: Dict[str, Any], delivery_id: str):
    """
    Process a GitHub webhook event and update Notion.
    
    Args:
        event_type: The type of GitHub event (push, pull_request, issues, etc.)
        data: The webhook payload data
        delivery_id: GitHub delivery ID for tracking
    """
    try:
        notion_service = NotionService()
        
        # Process different event types
        if event_type == "push":
            await notion_service.handle_push_event(data)
        elif event_type == "pull_request":
            await notion_service.handle_pull_request_event(data)
        elif event_type == "issues":
            await notion_service.handle_issue_event(data)
        elif event_type == "issue_comment":
            await notion_service.handle_issue_comment_event(data)
        elif event_type == "pull_request_review":
            await notion_service.handle_pr_review_event(data)
        else:
            logger.info(
                f"Unhandled event type: {event_type}",
                extra={"delivery_id": delivery_id}
            )
            return
            
        logger.info(
            f"Successfully processed {event_type} event",
            extra={"delivery_id": delivery_id}
        )
        
    except ExternalServiceException as e:
        logger.error(
            f"Failed to process {event_type} event: {e.message}",
            extra={
                "delivery_id": delivery_id,
                "error": str(e),
                "service": e.service_name
            },
            exc_info=True
        )
    except Exception as e:
        logger.error(
            f"Unexpected error processing {event_type} event: {str(e)}",
            extra={"delivery_id": delivery_id},
            exc_info=True
        )


@router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook service."""
    settings = get_settings()
    
    # Check if required configuration is present
    config_status = {
        "webhook_secret": bool(settings.GITHUB_WEBHOOK_SECRET),
        "notion_token": bool(settings.NOTION_TOKEN),
        "notion_database_id": bool(settings.NOTION_DATABASE_ID)
    }
    
    # Check Notion connectivity
    notion_status = "unknown"
    try:
        if all(config_status.values()):
            notion_service = NotionService()
            await notion_service.test_connection()
            notion_status = "connected"
    except Exception as e:
        notion_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if all(config_status.values()) else "configuration_incomplete",
        "configuration": config_status,
        "notion_connection": notion_status,
        "webhook_url": "/webhooks/github"
    }