"""
Celery worker configuration.

This module sets up and configures the Celery application instance, which is
responsible for running background tasks asynchronously. It uses Redis as both
the message broker for queuing tasks and the result backend for storing task
outcomes.

If Redis is not configured, Celery operations will be disabled.
"""
from celery import Celery
from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

# Initialize celery_app as None by default
celery_app = None

# Only configure Celery if Redis URL is provided
if settings.REDIS_URL:
    # Create the Celery application instance
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
    
    logger.info("Celery configured with Redis backend")
else:
    logger.warning("REDIS_URL not configured - Celery background tasks will be disabled")
