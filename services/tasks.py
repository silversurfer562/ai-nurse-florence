"""
Celery tasks for background processing.

This module defines the asynchronous tasks that can be executed by the Celery
worker. By defining logic here, we offload long-running operations from the
main API process, preventing them from blocking requests.
"""
from utils.config import settings
from services import summarize_service
from utils.logging import get_logger

logger = get_logger(__name__)

# Conditionally import and create celery app only if Redis is available
celery_app = None
if settings.REDIS_URL:
    try:
        from celery_worker import celery_app as _celery_app
        celery_app = _celery_app
    except (ImportError, RuntimeError) as e:
        logger.warning(f"Celery not available: {e}")

def summarize_text_task(prompt: str, model: str = "gpt-4o-mini"):
    """
    A function to perform text summarization.
    
    If Celery is available, this can be executed as a background task.
    Otherwise, it runs synchronously.
    """
    try:
        logger.info(f"Starting summarization for prompt: '{prompt[:30]}...'")
        # Call the core summarization logic
        summary_result = summarize_service.summarize_text(prompt, model=model)
        
        logger.info("Completed summarization task")
        return summary_result
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        raise

# If Celery is available, create the async task
if celery_app:
    summarize_text_task = celery_app.task(bind=True)(lambda self, *args, **kwargs: summarize_text_task(*args, **kwargs))