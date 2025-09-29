"""Minimal Celery application for AI Nurse Florence.

This module exposes a top-level `celery_app` name which is referenced by
the docker-compose and Procfile worker commands as
`celery -A celery_worker.celery_app worker`.

The configuration is intentionally small: it reads the broker/result backend
from the `REDIS_URL` environment variable (defaulting to the compose service
name), uses JSON serialization, and autodiscovers tasks from common locations.

This file should be importable by the worker runtime inside the container.
"""
from __future__ import annotations

import os

from celery import Celery

# Broker and backend (Redis expected in docker-compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


def make_celery(app_name: str = "florence") -> Celery:
    """Create and return a configured Celery application."""
    celery = Celery(app_name, broker=REDIS_URL, backend=REDIS_URL)

    celery.conf.update(
        accept_content=["json"],
        result_serializer="json",
        task_serializer="json",
        enable_utc=True,
        timezone="UTC",
    )

    # Autodiscover tasks in common locations. Only pass packages that are
    # actually importable to avoid crashing the worker when optional
    # background-task packages are not present in development images.
    candidate_packages = ["services", "services.tasks", "tasks"]
    import importlib.util

    available = [p for p in candidate_packages if importlib.util.find_spec(p) is not None]
    if available:
        celery.autodiscover_tasks(available)

    return celery


# Expose the application as `celery_app` so Celery's -A flag can reference it.
celery_app = make_celery()
