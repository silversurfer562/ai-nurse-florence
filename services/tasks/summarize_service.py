"""Proxy module for services.tasks.summarize_service used in tests.

This forwards calls to the main services.summarize_service module so unit and
integration tests that patch this import path continue to work even when
Celery tasks are disabled.
"""
from services import summarize_service as _main

# Re-export the key functions used by tests
summarize_text = _main.summarize_text
sbar_from_notes = _main.sbar_from_notes
call_chatgpt = _main.call_chatgpt

__all__ = ["summarize_text", "sbar_from_notes", "call_chatgpt"]
