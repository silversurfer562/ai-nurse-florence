from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse
from typing import Any, Dict

from services import summarize_service
# Try to import the Celery task. In Redis-free development or tests the
# tasks module may not expose a Celery task object; provide a local
# synchronous fallback that implements `.delay()` and returns a small
# task-like object with `id`, `status`, and `get()` so the endpoint can
# operate without a worker.
try:
    from services.tasks import summarize_text_task  # type: ignore
except Exception:
    from uuid import uuid4

    class _LocalTask:
        def __init__(self, result: dict):
            self.id = str(uuid4())
            # When running in a local, synchronous fallback we still return
            # an initial PENDING status so the API behaves like a queued
            # Celery task for callers (tests patch AsyncResult for GET).
            self.status = "PENDING"
            self._result = result

        def get(self, propagate: bool = True):
            return self._result

    class _LocalTaskWrapper:
        @staticmethod
        def delay(prompt: str, model: str = "gpt-4o-mini"):
            # call the summarization synchronously (tests may patch
            # `services.summarize_service.summarize_text` so this remains
            # test-friendly)
            result = summarize_service.summarize_text(prompt, model=model)
            return _LocalTask(result)

    summarize_text_task = _LocalTaskWrapper()
from celery.result import AsyncResult
from utils.exceptions import ExternalServiceException
from utils.logging import get_logger
from utils.api_responses import create_success_response, create_error_response

router = APIRouter(prefix="/summarize", tags=["summarize"])
logger = get_logger(__name__)


@router.post("/chat",
    summary="Summarize text",
    description="""
    Summarize medical text using AI.
    
    This endpoint uses an AI model to create concise summaries of medical text,
    which can include patient notes, research papers, or any medical content.
    
    Request body should include:
    - prompt: The text to summarize
    - model: (Optional) The AI model to use (default: gpt-4o-mini)
    
    Example request:
    ```json
    {
        "prompt": "The patient is a 45-year-old male with a history of hypertension...",
        "model": "gpt-4o-mini"
    }
    ```
    
    The response contains the summarized text.
    """
)
async def chat_endpoint(payload: Dict[str, Any], request: Request):
    """
    POST /summarize/chat
    Body example: {"prompt": "Summarize this...", "model": "gpt-4o-mini"}
    """
    request_id = getattr(request.state, "request_id", None)
    prompt = payload.get("prompt", "")
    model = payload.get("model", "gpt-4o-mini")
    
    if not prompt:
        logger.warning(
            "Missing prompt in request", 
            extra={"request_id": request_id}
        )
        return create_error_response(
            message="Missing 'prompt' in request body.",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_prompt"
        )
    
    try:
        logger.info(
            f"Processing summarization request with model {model}",
            extra={"request_id": request_id, "model": model}
        )
        
        result = summarize_service.summarize_text(prompt, model=model)
        
        # Check if clarification is needed
        if result.get("needs_clarification"):
            return create_error_response(
                message="The prompt is too vague. Please provide more details.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="clarification_needed",
                details={
                    "clarification_question": result["clarification_question"],
                    "original_prompt": result["original_prompt"]
                }
            )
        
        # Return the normal success response
        return create_success_response(result)
        
    except ExternalServiceException as exc:
        # This will be caught by our global exception handler
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error in summarize endpoint: {str(exc)}",
            extra={"request_id": request_id, "error": str(exc)},
            exc_info=True
        )
        # For unexpected errors, use the standardized error response
        return create_error_response(
            message="An unexpected error occurred while processing the summary.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error"
        )

@router.post("/chat/async",
    summary="Summarize text asynchronously",
    description="""
    Process text summarization asynchronously.
    
    This endpoint offloads the summarization task to a background worker and
    immediately returns a `task_id`. Use the `/tasks/{task_id}` endpoint
    to check the status and retrieve the result.
    
    The response contains a task_id and status information.
    """
)
async def chat_endpoint_async(
    payload: Dict[str, Any], 
    request: Request, 
):
    """
    POST /summarize/chat/async
    
    Dispatches a summarization task to the Celery worker.
    """
    request_id = getattr(request.state, "request_id", None)
    prompt = payload.get("prompt", "")
    model = payload.get("model", "gpt-4o-mini")
    
    if not prompt:
        logger.warning(
            "Missing prompt in request", 
            extra={"request_id": request_id}
        )
        return create_error_response(
            message="Missing 'prompt' in request body.",
            status_code=status.HTTP_400_BAD_REQUEST,
            code="missing_prompt"
        )
    
    logger.info(
        f"Dispatching summarization task for request {request_id}",
        extra={"request_id": request_id}
    )
    
    # Dispatch the task to Celery
    task = summarize_text_task.delay(prompt, model=model)
    
    task_info = {"task_id": task.id, "status": task.status}
    
    return create_success_response(
        data=task_info,
        links={"status": f"/api/v1/summarize/tasks/{task.id}"}
    )


@router.get("/tasks/{task_id}",
    summary="Get async task status",
    description="""
    Retrieve the status and result of an asynchronous summarization task.
    
    Possible statuses are: PENDING, STARTED, SUCCESS, FAILURE.
    
    For successful tasks, the response will include the summarization result.
    For failed tasks, the response will include the error message.
    """
)
async def get_task(task_id: str):
    """
    GET /summarize/tasks/{task_id}
    
    Checks the status of a Celery task.
    
    Returns:
        A dictionary with task status information
    """
    task_result = AsyncResult(task_id)
    
    if task_result.status == "SUCCESS":
        result = task_result.get()
        response_data = {"task_id": task_id, "status": task_result.status, "result": result}
    elif task_result.status == "FAILURE":
        result = task_result.get(propagate=False) # Get exception without raising it
        response_data = {
            "task_id": task_id,
            "status": task_result.status,
            "error": {"type": type(result).__name__, "message": str(result)}
        }
    else:
        # For PENDING, STARTED, etc.
        response_data = {"task_id": task_id, "status": task_result.status}

    if not task_result.ready() and task_result.status not in ('PENDING', 'STARTED'):
        # This condition handles cases where the task ID might not be in the backend.
        # The Celery result backend may be None in local/test environments, so
        # guard attribute access accordingly.
        backend = getattr(task_result, "backend", None)
        if backend is None or not getattr(backend, "get", lambda *_: False)(task_id):
            return create_error_response(
                f"Task {task_id} not found",
                status.HTTP_404_NOT_FOUND,
                "task_not_found"
            )

    return create_success_response(response_data)
