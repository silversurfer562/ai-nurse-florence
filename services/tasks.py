"""
Tasks for background processing.

This module defines tasks that can be executed asynchronously by Celery
or synchronously as fallback when Celery is not available.
"""
from celery_worker import celery_app
from services import summarize_service
from utils.logging import get_logger

logger = get_logger(__name__)

def summarize_text_sync(prompt: str, model: str = "gpt-4o-mini"):
    """
    Synchronous text summarization function.
    
    This is used as a fallback when Celery is not available.
    """
    try:
        logger.info(f"Starting synchronous summarization for prompt: '{prompt[:30]}...'")
        summary_result = summarize_service.summarize_text(prompt, model=model)
        logger.info("Completed synchronous summarization")
        return summary_result
    except Exception as e:
        logger.error(f"Synchronous summarization failed: {e}", exc_info=True)
        raise

# Only create Celery task if celery_app is available
if celery_app:
    @celery_app.task(bind=True)
    def summarize_text_task(self, prompt: str, model: str = "gpt-4o-mini"):
        """
        A Celery task to perform text summarization.
        
        The `bind=True` argument makes `self` available, which provides access
        to the task instance for things like updating state.
        """
        try:
            logger.info(f"Starting summarization task {self.request.id} for prompt: '{prompt[:30]}...'")
            summary_result = summarize_service.summarize_text(prompt, model=model)
            logger.info(f"Completed summarization task {self.request.id}")
            return summary_result
        except Exception as e:
            logger.error(f"Task {self.request.id} failed: {e}", exc_info=True)
            raise
else:
    # Create a mock task that runs synchronously
    class MockTask:
        def delay(self, *args, **kwargs):
            """Mock delay method that runs synchronously"""
            result = summarize_text_sync(*args, **kwargs)
            return MockAsyncResult(result)
        
        def apply_async(self, *args, **kwargs):
            """Mock apply_async method that runs synchronously"""
            result = summarize_text_sync(*args, **kwargs)
            return MockAsyncResult(result)
    
    class MockAsyncResult:
        def __init__(self, result):
            self.result = result
            self.id = "sync-task"
            self.state = "SUCCESS"
            
        def get(self, timeout=None):
            return self.result
            
        def ready(self):
            return True
            
        def successful(self):
            return True
    
    summarize_text_task = MockTask()