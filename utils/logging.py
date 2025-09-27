"""
Logging setup and utilities for the application.

This module provides a standardized way to create loggers and structured logs
throughout the application.
"""
import logging
import json
import sys
import os
from typing import Optional

# Configure default logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create a JSON formatter for structured logging
class JsonFormatter(logging.Formatter):
    """Format log records as JSON strings."""
    
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
            
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)
            
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: The name of the logger, typically the module name
        
    Returns:
        A logger instance
    """
    logger = logging.getLogger(name)
    
    # Add JSON handler if not already present
    if not any(isinstance(h.formatter, JsonFormatter) for h in logger.handlers):
        json_handler = logging.StreamHandler()
        json_handler.setFormatter(JsonFormatter())
        logger.addHandler(json_handler)
        
    return logger


def log_with_context(
    logger: logging.Logger, 
    level: int, 
    msg: str, 
    request_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log a message with additional context.
    
    Args:
        logger: The logger to use
        level: The log level (e.g., logging.INFO)
        msg: The log message
        request_id: Optional request ID for tracing
        **kwargs: Additional key-value pairs to include in the log
    """
    extra = {"extra": kwargs}
    if request_id:
        extra["request_id"] = request_id
        
    logger.log(level, msg, extra=extra)