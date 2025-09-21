"""
Compatibility shim for task imports used in tests.

In production `services.tasks` may be a package with task-specific submodules
for celery. For local development we keep a lightweight single-file module.
Some tests expect to patch `services.tasks.summarize_service` by importing
that dotted name; Python's import machinery requires that name to exist in
`sys.modules`. To support that without restructuring into a package, we
import the real service modules and register them under the package-style
name so `unittest.mock` patching works.

This file intentionally does not start any background workers or require
Redis — it's a safe shim for tests and local runs.
"""

import importlib
import sys
from typing import Any

# List of service module names we want to expose under services.tasks.*
_SERVICE_MODULES = [
	"services.summarize_service",
	"services.disease_service",
	"services.pubmed_service",
	"services.trials_service",
]

for mod_name in _SERVICE_MODULES:
	try:
		mod = importlib.import_module(mod_name)
		# register as if it were a submodule of services.tasks
		alias = mod_name.replace("services.", "services.tasks.")
		sys.modules[alias] = mod
		# also set as attribute on this module for direct access
		setattr(sys.modules[__name__], alias.split(".")[-1], mod)
	except Exception:
		# If a service isn't present, leave a placeholder None so tests
		# can still patch the attribute (they will replace it anyway).
		setattr(sys.modules[__name__], mod_name.split(".")[-1], None)
