"""Celery task package placeholder for environments without Celery/Redis.

This package exposes a module path `services.tasks.summarize_service` so tests
that patch `services.tasks.summarize_service.summarize_text` can import it.

In production this package can be replaced with real Celery tasks.
This module also exposes a small, test-friendly `summarize_text_task` stub
that mimics the minimal interface used by the API layer: `.delay()` returns
an object with `id` and `status` attributes. This prevents NameError in
environments where Celery/Redis are not configured.
"""

from . import summarize_service
import uuid
from types import SimpleNamespace


class _TaskStub:
	"""Minimal task-like object returned from `.delay()` in tests.

	`.delay()` returns an instance with an `id` and `status` (initially
	'PENDING'). This mirrors the small subset of behaviour the API expects
	for dispatching asynchronous jobs in tests.
	"""

	@staticmethod
	def delay(*args, **kwargs):
		task_id = str(uuid.uuid4())
		return SimpleNamespace(id=task_id, status="PENDING")


# Export a module-level task object that has a `.delay()` method. Tests and
# the router will call `summarize_text_task.delay(...)` and inspect `id`.
summarize_text_task = _TaskStub()

__all__ = ["summarize_service", "summarize_text_task"]
