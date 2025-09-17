from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Any, Dict

from services import summarize_service
from utils.exceptions import ExternalServiceException
from utils.logging import get_logger
from utils.background_tasks import schedule_task, get_task_status

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
async def chat_endpoint(payload: Dict[str, Any], request: Request) -> Dict[str, Any]:
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
        raise HTTPException(status_code=400, detail="Missing 'prompt' in body")
    
    try:
        logger.info(
            f"Processing summarization request with model {model}",
            extra={"request_id": request_id, "model": model}
        )
        
        result = summarize_service.summarize_text(prompt, model=model)
        
        # Check if clarification is needed
        if result.get("needs_clarification"):
            return JSONResponse(
                status_code=422,  # Unprocessable Entity
                content={
                    "detail": {
                        "needs_clarification": True,
                        "clarification_question": result["clarification_question"],
                        "original_prompt": result["original_prompt"]
                    }
                }
            )
        
        # Return the normal response
        return result
        
    except ExternalServiceException as exc:
        # This will be caught by our exception handler and returned with proper formatting
        raise
    except Exception as exc:
        logger.error(
            f"Unexpected error in summarize endpoint: {str(exc)}",
            extra={"request_id": request_id, "error": str(exc)},
            exc_info=True
        )
        # For unexpected errors, still return a 500
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/chat/async",
    summary="Asynchronously summarize text",
    description="""
    Process text summarization asynchronously.
    
    This endpoint is ideal for longer texts or when you want to avoid waiting for the 
    processing to complete. It returns a task ID that can be used to check the status
    or result later.
    
    Request body should include:
    - prompt: The text to summarize
    - model: (Optional) The AI model to use (default: gpt-4o-mini)
    - callback_url: (Optional) URL to receive the result when processing completes
    
    Example request:
    ```json
    {
        "prompt": "The patient is a 45-year-old male with a history of hypertension...",
        "model": "gpt-4o-mini",
        "callback_url": "https://example.com/webhook"
    }
    ```
    
    The response contains a task_id and status information.
    """
)
async def chat_endpoint_async(
    payload: Dict[str, Any], 
    request: Request, 
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    POST /summarize/chat/async
    
    Asynchronously summarize text using ChatGPT.
    
    Body example: {
        "prompt": "Summarize this...", 
        "model": "gpt-4o-mini",
        "callback_url": "https://example.com/callback"  # Optional
    }
    
    Returns a task ID that can be used to check the status of the operation.
    
    Args:
        payload: The request payload
        request: The FastAPI request object
        background_tasks: FastAPI background tasks object
        
    Returns:
        A dictionary with task_id and status
    """
    request_id = getattr(request.state, "request_id", None)
    prompt = payload.get("prompt", "")
    model = payload.get("model", "gpt-4o-mini")
    callback_url = payload.get("callback_url")
    
    if not prompt:
        logger.warning(
            "Missing prompt in request", 
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=400, detail="Missing 'prompt' in body")
    
    logger.info(
        f"Scheduling async summarization with model {model}",
        extra={"request_id": request_id, "model": model}
    )
    
    return schedule_task(
        background_tasks,
        summarize_service.summarize_text,
        prompt,
        model=model,
        callback_url=callback_url
    )


@router.get("/tasks/{task_id}",
    summary="Get task status",
    description="""
    Check the status of an asynchronous summarization task.
    
    This endpoint returns the current status of a task and, if completed,
    the result of the summarization.
    
    Possible status values:
    - scheduled: Task has been queued
    - running: Task is currently being processed
    - completed: Task has finished successfully
    - failed: Task encountered an error
    
    For completed tasks, the response will include the result.
    For failed tasks, the response will include the error message.
    """
)
async def get_task(task_id: str) -> Dict[str, Any]:
    """
    GET /summarize/tasks/{task_id}
    
    Get the status of a background task.
    
    Args:
        task_id: The ID of the task
        
    Returns:
        A dictionary with task status information
    """
    result = get_task_status(task_id)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return result
