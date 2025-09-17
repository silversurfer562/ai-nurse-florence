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

# Check if we're running on Vercel (serverless environment)
is_vercel = os.environ.get('VERCEL') == '1'

# For Vercel or when Redis is not available, create a minimal celery instance
if is_vercel or not settings.REDIS_URL:
    # Create a minimal Celery app that won't actually work but allows imports
    celery_app = Celery("worker")
    celery_app.conf.update(task_always_eager=True)  # Execute tasks synchronously
else:
    # Create the normal Celery application instance
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
