"""
Railway Webhook Handler Router
Handles deployment notifications from Railway and triggers automated actions.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class RailwayWebhookPayload(BaseModel):
    """Railway webhook payload structure based on Railway documentation."""

    type: str = Field(..., description="Event type (e.g., DEPLOY)")
    status: str = Field(
        ..., description="Deployment status: SUCCESS, FAILED, BUILDING, etc."
    )
    timestamp: Optional[str] = Field(None, description="Event timestamp")
    project: Optional[dict] = Field(None, description="Project information")
    environment: Optional[dict] = Field(None, description="Environment information")
    deployment: Optional[dict] = Field(None, description="Deployment information")
    service: Optional[dict] = Field(None, description="Service information")


class WebhookEvent(BaseModel):
    """Internal webhook event model for tracking."""

    id: str
    event_type: str
    status: str
    timestamp: datetime
    source: str = "railway"
    metadata: dict = {}


# In-memory event storage (replace with database in production)
webhook_events: list[WebhookEvent] = []


async def trigger_health_checks(deployment_info: dict):
    """
    Trigger automated health checks after successful deployment.

    Args:
        deployment_info: Information about the deployment that triggered checks
    """
    from services.webhook_health_check import run_post_deployment_health_checks

    logger.info(
        f"🔍 Triggering health checks for deployment: {deployment_info.get('id', 'unknown')}"
    )

    try:
        results = await run_post_deployment_health_checks()
        logger.info(f"✅ Health checks completed: {results}")
        return results
    except Exception as e:
        logger.error(f"❌ Health checks failed: {str(e)}")
        return {"status": "error", "message": str(e)}


async def send_notifications(event: WebhookEvent):
    """
    Send notifications to configured services (Discord, Slack, etc.).

    Args:
        event: The webhook event to notify about
    """
    from services.webhook_notifications import send_deployment_notification

    logger.info(
        f"📢 Sending notifications for event: {event.event_type} - {event.status}"
    )

    try:
        await send_deployment_notification(event)
    except Exception as e:
        logger.error(f"❌ Failed to send notifications: {str(e)}")


@router.post("/railway")
async def railway_webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks,
    x_webhook_signature: Optional[str] = Header(None),
):
    """
    Handle incoming webhooks from Railway.

    Railway sends webhooks for deployment events (Building, Success, Failed, etc.)
    This endpoint processes the event and triggers appropriate actions.

    Args:
        request: The incoming webhook request
        background_tasks: FastAPI background tasks for async processing
        x_webhook_signature: Railway webhook signature for verification (optional)

    Returns:
        dict: Acknowledgment of webhook receipt

    Example Railway Webhook Payload:
        {
            "type": "DEPLOY",
            "status": "SUCCESS",
            "timestamp": "2025-10-02T12:00:00Z",
            "project": {"id": "...", "name": "ai-nurse-florence"},
            "deployment": {"id": "...", "url": "https://..."}
        }
    """
    try:
        # Parse webhook payload
        payload = await request.json()
        logger.info(f"📥 Received Railway webhook: {payload.get('status', 'UNKNOWN')}")

        # Create event record
        event = WebhookEvent(
            id=payload.get("deployment", {}).get("id", "unknown"),
            event_type=payload.get("type", "UNKNOWN"),
            status=payload.get("status", "UNKNOWN"),
            timestamp=datetime.utcnow(),
            metadata=payload,
        )

        # Store event (in production, save to database)
        webhook_events.append(event)

        # Trigger background actions based on status
        status = event.status.upper()

        if status == "SUCCESS":
            logger.info("✅ Deployment succeeded - triggering health checks")
            background_tasks.add_task(
                trigger_health_checks, payload.get("deployment", {})
            )
            background_tasks.add_task(send_notifications, event)

        elif status in ["FAILED", "CRASHED"]:
            logger.error(
                f"❌ Deployment {status.lower()} - sending failure notifications"
            )
            background_tasks.add_task(send_notifications, event)

        elif status == "BUILDING":
            logger.info("🔨 Deployment building...")

        elif status == "DEPLOYING":
            logger.info("🚀 Deployment in progress...")

        return {
            "status": "received",
            "event_id": event.id,
            "event_type": event.event_type,
            "timestamp": event.timestamp.isoformat(),
            "message": f"Webhook processed: {status}",
        }

    except Exception as e:
        logger.error(f"❌ Error processing Railway webhook: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/events")
async def get_webhook_events(limit: int = 50):
    """
    Get recent webhook events.

    Args:
        limit: Maximum number of events to return

    Returns:
        dict: List of recent webhook events
    """
    recent_events = webhook_events[-limit:] if webhook_events else []

    return {
        "total": len(webhook_events),
        "events": [
            {
                "id": event.id,
                "type": event.event_type,
                "status": event.status,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
            }
            for event in reversed(recent_events)
        ],
    }


@router.get("/events/{event_id}")
async def get_webhook_event_details(event_id: str):
    """
    Get details for a specific webhook event.

    Args:
        event_id: The event ID to retrieve

    Returns:
        dict: Complete event details including metadata
    """
    event = next((e for e in webhook_events if e.id == event_id), None)

    if not event:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")

    return {
        "id": event.id,
        "type": event.event_type,
        "status": event.status,
        "timestamp": event.timestamp.isoformat(),
        "source": event.source,
        "metadata": event.metadata,
    }


@router.post("/test")
async def test_webhook_endpoint(background_tasks: BackgroundTasks):
    """
    Test webhook endpoint with a simulated Railway success event.

    Returns:
        dict: Test webhook response
    """
    test_payload = {
        "type": "DEPLOY",
        "status": "SUCCESS",
        "timestamp": datetime.utcnow().isoformat(),
        "project": {"id": "test", "name": "ai-nurse-florence"},
        "deployment": {"id": "test-deployment", "url": "http://localhost:8000"},
    }

    logger.info("🧪 Testing webhook with simulated Railway event")

    # Create mock request
    class MockRequest:
        async def json(self):
            return test_payload

    return await railway_webhook_handler(
        request=MockRequest(),
        background_tasks=background_tasks,
        x_webhook_signature=None,
    )
