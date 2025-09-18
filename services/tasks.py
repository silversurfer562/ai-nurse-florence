"""
Celery tasks for background processing.

This module defines the asynchronous tasks that can be executed by the Celery
worker. By defining logic here, we offload long-running operations from the
main API process, preventing them from blocking requests.

If Celery is not configured, tasks will execute synchronously.
"""
from celery_worker import celery_app
from services import summarize_service
from utils.logging import get_logger

logger = get_logger(__name__)

def summarize_text_task(prompt: str, model: str = "gpt-4o-mini"):
    """
    A function to perform text summarization.
    
    If Celery is available, this will be decorated as a Celery task.
    Otherwise, it will execute synchronously.
    """
    try:
        task_id = getattr(summarize_text_task, 'request', {}).get('id', 'sync')
        logger.info(f"Starting summarization task {task_id} for prompt: '{prompt[:30]}...'")
        
        # Call the core summarization logic
        summary_result = summarize_service.summarize_text(prompt, model=model)
        
        logger.info(f"Completed summarization task {task_id}")
        return summary_result
        
    except Exception as e:
        logger.error(f"Summarization task failed: {e}", exc_info=True)
        # Reraise the exception to mark the task as failed
        raise

# Only decorate with Celery task if celery_app is available
if celery_app is not None:
    summarize_text_task = celery_app.task(bind=True)(summarize_text_task)
    logger.info("Summarization task registered with Celery")
else:
    logger.warning("Celery not available - summarization tasks will run synchronously")