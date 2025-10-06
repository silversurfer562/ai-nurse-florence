"""
Logging utilities for AI Nurse Florence.

Provides standardized logging configuration across the application.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__ from calling module)
        level: Optional logging level (defaults to INFO)

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)

    # Set level if not already configured
    if level is not None:
        logger.setLevel(level)
    elif not logger.level:
        logger.setLevel(logging.INFO)

    # Add console handler if no handlers exist
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        # Format: timestamp - name - level - message
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def configure_root_logger(level: int = logging.INFO) -> None:
    """
    Configure the root logger for the application.

    Args:
        level: Logging level (default: INFO)

    Example:
        >>> from src.utils.logging import configure_root_logger
        >>> import logging
        >>> configure_root_logger(logging.DEBUG)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
