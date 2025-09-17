"""
Celery worker configuration.

This module sets up and configures the Celery application instance, which is
responsible for running background tasks asynchronously. It uses Redis as both
the message broker for queuing tasks and the result backend for storing task
outcomes.
"""
from celery import Celery
from utils.config import settings
import os

# Allow skipping Redis for testing
TESTING = os.getenv("TESTING", "false").lower() == "true"

# Ensure Redis URL is configured (unless in testing mode)
if not TESTING and not settings.REDIS_URL:
    raise RuntimeError("REDIS_URL must be configured in settings to use Celery.")

# Create the Celery application instance
if TESTING or not settings.REDIS_URL:
    # Use in-memory broker for testing
    celery_app = Celery(
        "worker",
        broker="memory://",
        backend="cache+memory://",
        include=["services.tasks"]
    )
else:
    celery_app = Celery(
        "worker",
        broker=settings.REDIS_URL,
        backend=settings.REDIS_URL,
        include=["services.tasks"]  # List of modules to import when the worker starts
    )

# Optional Celery configuration
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,  # Store results for 1 hour
    broker_connection_retry_on_startup=True,
)
