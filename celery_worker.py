"""
Celery worker configuration.

This module sets up and configures the Celery application instance, which is
responsible for running background tasks asynchronously. It uses Redis as both
the message broker for queuing tasks and the result backend for storing task
outcomes.

Note: This module is optional and will only be available if Redis is configured.
"""
from celery import Celery
from utils.config import settings
from utils.logging import get_logger

logger = get_logger(__name__)

# Make Celery optional for serverless deployments
celery_app = None

if settings.REDIS_URL:
    logger.info("Redis URL configured, initializing Celery")
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
    logger.info("Celery initialized successfully")
else:
    logger.info("REDIS_URL not configured, Celery tasks will run synchronously")

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
