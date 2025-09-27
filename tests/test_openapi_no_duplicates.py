
from app import app


def test_no_duplicate_operation_ids():
    """Fail if OpenAPI operationIds contain duplicates (prevents ambiguous API docs)."""
    schema = app.openapi()
    ops = []
    for path, methods in schema.get('paths', {}).items():
        for method, info in methods.items():
            op_id = info.get('operationId')
            if op_id:
                ops.append(op_id)

    dupes = set([x for x in ops if ops.count(x) > 1])
    assert not dupes, f"Duplicate operationIds found in OpenAPI schema: {dupes}"
