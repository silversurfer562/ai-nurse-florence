"""
Background task utilities for the application.

This module provides functionality for running tasks in the background
using FastAPI's background tasks feature.
"""
import uuid
from typing import Dict, Any, Optional, Callable
import asyncio
import time
from fastapi import BackgroundTasks

from utils.logging import get_logger

logger = get_logger(__name__)

# In-memory store for task results
# For production, use a persistent store like Redis
_task_results: Dict[str, Dict[str, Any]] = {}
_task_callbacks: Dict[str, Callable] = {}


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a background task.
    
    Args:
        task_id: The ID of the task
        
    Returns:
        A dictionary with task status information
    """
    if task_id not in _task_results:
        return {"task_id": task_id, "status": "not_found"}
    
    return _task_results[task_id]


def schedule_task(
    background_tasks: BackgroundTasks,
    task_func: Callable,
    *args: Any,
    callback_url: Optional[str] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Schedule a task to run in the background.
    
    Args:
        background_tasks: FastAPI BackgroundTasks instance
        task_func: The function to run in the background
        *args: Positional arguments to pass to the task function
        callback_url: Optional URL to call when the task completes
        **kwargs: Keyword arguments to pass to the task function
        
    Returns:
        A dictionary with task_id and status
    """
    task_id = str(uuid.uuid4())
    
    # Create initial task status
    _task_results[task_id] = {
        "task_id": task_id,
        "status": "scheduled",
        "created_at": time.time(),
    }
    
    # Store callback if provided
    if callback_url:
        _task_callbacks[task_id] = callback_url
    
    # Add the task to the background tasks
    background_tasks.add_task(
        _run_task_with_status_tracking,
        task_id,
        task_func,
        *args,
        **kwargs
    )
    
    return {"task_id": task_id, "status": "scheduled"}


async def _run_task_with_status_tracking(
    task_id: str,
    task_func: Callable,
    *args: Any,
    **kwargs: Any
) -> None:
    """
    Run a task and track its status.
    
    Args:
        task_id: The ID of the task
        task_func: The function to run
        *args: Positional arguments to pass to the task function
        **kwargs: Keyword arguments to pass to the task function
    """
    try:
        # Update status to running
        _task_results[task_id]["status"] = "running"
        _task_results[task_id]["started_at"] = time.time()
        
        # Run the task
        if asyncio.iscoroutinefunction(task_func):
            result = await task_func(*args, **kwargs)
        else:
            result = task_func(*args, **kwargs)
        
        # Update status to completed
        _task_results[task_id]["status"] = "completed"
        _task_results[task_id]["completed_at"] = time.time()
        _task_results[task_id]["result"] = result
        
        logger.info(f"Task completed: {task_id}")
        
        # Call callback if registered
        if task_id in _task_callbacks:
            await _call_callback(task_id, _task_callbacks[task_id], result)
            
    except Exception as e:
        # Update status to failed
        _task_results[task_id]["status"] = "failed"
        _task_results[task_id]["completed_at"] = time.time()
        _task_results[task_id]["error"] = str(e)
        
        logger.error(
            f"Task failed: {task_id}", 
            extra={"task_id": task_id, "error": str(e)},
            exc_info=True
        )
        
        # Call callback with error if registered
        if task_id in _task_callbacks:
            error_result = {"error": str(e)}
            await _call_callback(task_id, _task_callbacks[task_id], error_result)


async def _call_callback(task_id: str, callback_url: str, result: Any) -> None:
    """
    Call a callback URL with the task result.
    
    Args:
        task_id: The ID of the task
        callback_url: The URL to call
        result: The result to send
    """
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "task_id": task_id,
                "result": result
            }
            
            async with session.post(callback_url, json=payload) as response:
                if response.status >= 400:
                    logger.error(
                        f"Callback failed: {callback_url}",
                        extra={
                            "task_id": task_id,
                            "status_code": response.status
                        }
                    )
                else:
                    logger.info(
                        f"Callback succeeded: {callback_url}",
                        extra={"task_id": task_id}
                    )
    except Exception as e:
        logger.error(
            f"Error calling callback: {str(e)}",
            extra={"task_id": task_id, "callback_url": callback_url, "error": str(e)},
            exc_info=True
        )