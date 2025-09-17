"""
Celery tasks for background processing.

This module defines the asynchronous tasks that can be executed by the Celery
worker. By defining logic here, we offload long-running operations from the
main API process, preventing them from blocking requests.
"""
from celery_worker import celery_app
from services import summarize_service
from utils.logging import get_logger

logger = get_logger(__name__)

# Only define tasks if Celery is available
if celery_app is not None:
    @celery_app.task(bind=True)
    def summarize_text_task(self, prompt: str, model: str = "gpt-4o-mini"):
        """
        A Celery task to perform text summarization.
        
        The `bind=True` argument makes `self` available, which provides access
        to the task instance for things like updating state.
        """
        try:
            logger.info(f"Starting summarization task {self.request.id} for prompt: '{prompt[:30]}...'")
            # We call the core summarization logic, which is now separate from the task definition.
            # Note: The original summarize_text function returns a dictionary.
            # We might want to refactor it to return just the text or handle the dict here.
            # For now, we'll assume it returns the full dictionary.
            summary_result = summarize_service.summarize_text(prompt, model=model)
            
            logger.info(f"Completed summarization task {self.request.id}")
            return summary_result
            
        except Exception as e:
            logger.error(f"Task {self.request.id} failed: {e}", exc_info=True)
            # Reraise the exception to mark the task as failed in Celery
            raise
else:
    # Define a fallback function when Celery is not available
    def summarize_text_task(prompt: str, model: str = "gpt-4o-mini"):
        """
        Fallback synchronous function when Celery is not available.
        """
        logger.warning("Celery not available, running synchronously")
        return summarize_service.summarize_text(prompt, model=model)