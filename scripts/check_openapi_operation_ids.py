"""Small script to fail CI if there are duplicate operationIds in generated OpenAPI JSON.

It expects the FastAPI app to be importable as `app` from `app` module and will
write the OpenAPI schema to a temporary file and scan for duplicate operationId values.
"""
from collections import Counter
import json
import sys

try:
    from app import app  # app: FastAPI
except Exception as e:
    print(f"Could not import FastAPI app: {e}")
    sys.exit(1)

openapi = app.openapi()
operation_ids = []
for path, methods in openapi.get("paths", {}).items():
    for method, spec in methods.items():
        op_id = spec.get("operationId")
        if op_id:
            operation_ids.append(op_id)

counts = Counter(operation_ids)
dups = [op for op, c in counts.items() if c > 1]
if dups:
    print("Duplicate operationIds found:")
    for op in dups:
        print(f"  {op} (count={counts[op]})")
    sys.exit(2)

print("No duplicate operationIds detected.")
sys.exit(0)
