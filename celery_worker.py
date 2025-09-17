"""
Celery worker configuration.

This module sets up and configures the Celery application instance, which is
responsible for running background tasks asynchronously. It uses Redis as both
the message broker for queuing tasks and the result backend for storing task
outcomes.
"""
from celery import Celery
from utils.config import settings

# Ensure Redis URL is configured
if not settings.REDIS_URL:
    import warnings
    warnings.warn("REDIS_URL not configured - Celery tasks will run synchronously", UserWarning)
    # Don't create celery app, let the importing modules handle it gracefully
    celery_app = None
else:
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
