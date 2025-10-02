"""
Webhook Notification Service
Sends deployment notifications to external services (Discord, Slack, Email, etc.)
"""

import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NotificationConfig(BaseModel):
    """Configuration for notification services."""

    discord_webhook_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    email_enabled: bool = False
    email_recipients: list[str] = []


class DeploymentNotification(BaseModel):
    """Structured deployment notification."""

    status: str
    event_type: str
    timestamp: datetime
    deployment_id: str
    environment: str = "production"
    project_name: str = "AI Nurse Florence"
    deployment_url: Optional[str] = None
    commit_message: Optional[str] = None
    duration: Optional[str] = None
    error_message: Optional[str] = None


class EmailConfig(BaseModel):
    """Email server configuration."""

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None


def get_notification_config() -> NotificationConfig:
    """
    Load notification configuration from environment variables.

    Returns:
        NotificationConfig: Configuration for notification services
    """
    email_recipients_str = os.getenv("NOTIFICATION_EMAIL_RECIPIENTS", "")
    email_recipients = [r.strip() for r in email_recipients_str.split(",") if r.strip()]

    return NotificationConfig(
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        email_enabled=os.getenv("NOTIFICATION_EMAIL_ENABLED", "false").lower() == "true",
        email_recipients=email_recipients
    )


def get_email_config() -> EmailConfig:
    """
    Load email configuration from environment variables.

    Returns:
        EmailConfig: Email server configuration
    """
    return EmailConfig(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        from_email=os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME"))
    )


def get_status_emoji(status: str) -> str:
    """Get emoji for deployment status."""
    status_emojis = {
        "SUCCESS": "✅",
        "FAILED": "❌",
        "CRASHED": "💥",
        "BUILDING": "🔨",
        "DEPLOYING": "🚀",
        "QUEUED": "⏳",
        "SKIPPED": "⏭️",
        "WAITING": "⏸️",
    }
    return status_emojis.get(status.upper(), "📦")


def get_status_color(status: str) -> int:
    """Get color code for deployment status (Discord embeds)."""
    status_colors = {
        "SUCCESS": 0x00ff00,  # Green
        "FAILED": 0xff0000,   # Red
        "CRASHED": 0xff0000,  # Red
        "BUILDING": 0xffaa00, # Orange
        "DEPLOYING": 0x00aaff, # Blue
        "QUEUED": 0xaaaaaa,   # Gray
    }
    return status_colors.get(status.upper(), 0x888888)


async def send_discord_notification(notification: DeploymentNotification, webhook_url: str):
    """
    Send deployment notification to Discord.

    Args:
        notification: The deployment notification to send
        webhook_url: Discord webhook URL
    """
    try:
        emoji = get_status_emoji(notification.status)
        color = get_status_color(notification.status)

        # Build embed fields
        fields = [
            {
                "name": "Status",
                "value": f"{emoji} {notification.status}",
                "inline": True
            },
            {
                "name": "Environment",
                "value": notification.environment,
                "inline": True
            },
            {
                "name": "Deployment ID",
                "value": f"`{notification.deployment_id[:12]}...`",
                "inline": True
            }
        ]

        if notification.deployment_url:
            fields.append({
                "name": "Deployment URL",
                "value": f"[View Deployment]({notification.deployment_url})",
                "inline": False
            })

        if notification.commit_message:
            fields.append({
                "name": "Commit",
                "value": notification.commit_message[:100],
                "inline": False
            })

        if notification.duration:
            fields.append({
                "name": "Duration",
                "value": notification.duration,
                "inline": True
            })

        if notification.error_message:
            fields.append({
                "name": "Error",
                "value": f"```{notification.error_message[:500]}```",
                "inline": False
            })

        # Create Discord embed
        embed = {
            "title": f"{emoji} Deployment {notification.status}",
            "description": f"**{notification.project_name}** deployment update",
            "color": color,
            "fields": fields,
            "timestamp": notification.timestamp.isoformat(),
            "footer": {
                "text": "Railway Deployment Webhook"
            }
        }

        payload = {
            "embeds": [embed],
            "username": "Railway Bot",
            "avatar_url": "https://railway.app/brand/logo-light.png"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"✅ Discord notification sent for {notification.status} deployment")

    except Exception as e:
        logger.error(f"❌ Failed to send Discord notification: {str(e)}")


async def send_slack_notification(notification: DeploymentNotification, webhook_url: str):
    """
    Send deployment notification to Slack.

    Args:
        notification: The deployment notification to send
        webhook_url: Slack webhook URL
    """
    try:
        emoji = get_status_emoji(notification.status)

        # Slack block kit message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Deployment {notification.status}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:*\n{notification.project_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Environment:*\n{notification.status}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{notification.status}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time:*\n{notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    }
                ]
            }
        ]

        if notification.deployment_url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{notification.deployment_url}|View Deployment>"
                }
            })

        if notification.error_message:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:*\n```{notification.error_message[:500]}```"
                }
            })

        payload = {
            "blocks": blocks,
            "text": f"{emoji} {notification.project_name} deployment {notification.status}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"✅ Slack notification sent for {notification.status} deployment")

    except Exception as e:
        logger.error(f"❌ Failed to send Slack notification: {str(e)}")


async def send_email_notification(notification: DeploymentNotification, recipients: list[str]):
    """
    Send deployment notification via email.

    Args:
        notification: The deployment notification to send
        recipients: List of email addresses to send to
    """
    try:
        email_config = get_email_config()

        if not email_config.smtp_username or not email_config.smtp_password:
            logger.error("❌ Email notifications configured but SMTP credentials missing")
            logger.error("   Set SMTP_USERNAME and SMTP_PASSWORD environment variables")
            return

        emoji = get_status_emoji(notification.status)

        # Create HTML email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: {'#4CAF50' if notification.status == 'SUCCESS' else '#f44336'};
                           color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .detail {{ margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #4CAF50; }}
                .detail strong {{ display: inline-block; width: 150px; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .error {{ background-color: #ffebee; border-left-color: #f44336; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{emoji} Deployment {notification.status}</h1>
                <p>{notification.project_name}</p>
            </div>
            <div class="content">
                <div class="detail">
                    <strong>Environment:</strong> {notification.environment}
                </div>
                <div class="detail">
                    <strong>Status:</strong> {notification.status}
                </div>
                <div class="detail">
                    <strong>Deployment ID:</strong> {notification.deployment_id[:12]}...
                </div>
                <div class="detail">
                    <strong>Timestamp:</strong> {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
                {f'<div class="detail"><strong>Deployment URL:</strong> <a href="{notification.deployment_url}">{notification.deployment_url}</a></div>' if notification.deployment_url else ''}
                {f'<div class="detail"><strong>Commit:</strong> {notification.commit_message[:100]}</div>' if notification.commit_message else ''}
                {f'<div class="detail"><strong>Duration:</strong> {notification.duration}</div>' if notification.duration else ''}
                {f'<div class="error"><strong>Error:</strong><br><pre>{notification.error_message[:500]}</pre></div>' if notification.error_message else ''}
            </div>
            <div class="footer">
                <p>Railway Deployment Webhook Notification</p>
                <p>AI Nurse Florence - Healthcare AI Assistant</p>
            </div>
        </body>
        </html>
        """

        # Create plain text version
        text_body = f"""
{emoji} Deployment {notification.status}
{notification.project_name}

Environment: {notification.environment}
Status: {notification.status}
Deployment ID: {notification.deployment_id}
Timestamp: {notification.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
        if notification.deployment_url:
            text_body += f"\nDeployment URL: {notification.deployment_url}"
        if notification.commit_message:
            text_body += f"\nCommit: {notification.commit_message}"
        if notification.error_message:
            text_body += f"\n\nError:\n{notification.error_message[:500]}"

        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{emoji} {notification.project_name} Deployment {notification.status}"
        msg['From'] = email_config.from_email or email_config.smtp_username
        msg['To'] = ", ".join(recipients)

        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port) as server:
            server.starttls()
            server.login(email_config.smtp_username, email_config.smtp_password)
            server.send_message(msg)

        logger.info(f"✅ Email notification sent to {len(recipients)} recipient(s)")

    except Exception as e:
        logger.error(f"❌ Failed to send email notification: {str(e)}")


async def send_deployment_notification(event):
    """
    Send deployment notification to all configured services.

    Args:
        event: WebhookEvent object containing deployment information
    """
    config = get_notification_config()

    # Extract deployment details from event metadata
    metadata = event.metadata
    deployment_info = metadata.get("deployment", {})

    notification = DeploymentNotification(
        status=event.status,
        event_type=event.event_type,
        timestamp=event.timestamp,
        deployment_id=event.id,
        environment=metadata.get("environment", {}).get("name", "production"),
        project_name=metadata.get("project", {}).get("name", "AI Nurse Florence"),
        deployment_url=deployment_info.get("url"),
        commit_message=deployment_info.get("meta", {}).get("commitMessage"),
    )

    # Send to all configured services
    if config.discord_webhook_url:
        logger.info("📢 Sending Discord notification...")
        await send_discord_notification(notification, config.discord_webhook_url)
    else:
        logger.debug("Discord webhook not configured (set DISCORD_WEBHOOK_URL)")

    if config.slack_webhook_url:
        logger.info("📢 Sending Slack notification...")
        await send_slack_notification(notification, config.slack_webhook_url)
    else:
        logger.debug("Slack webhook not configured (set SLACK_WEBHOOK_URL)")

    if config.email_enabled and config.email_recipients:
        logger.info(f"📧 Sending email notifications to {len(config.email_recipients)} recipients...")
        await send_email_notification(notification, config.email_recipients)
    else:
        logger.debug("Email notifications not configured (set NOTIFICATION_EMAIL_ENABLED=true and NOTIFICATION_EMAIL_RECIPIENTS)")

    if not (config.discord_webhook_url or config.slack_webhook_url or (config.email_enabled and config.email_recipients)):
        logger.warning("⚠️ No notification services configured. Set DISCORD_WEBHOOK_URL, SLACK_WEBHOOK_URL, or email settings")
