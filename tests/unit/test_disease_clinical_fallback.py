import inspect
from pytest import mark

from src.services import disease_service, clinical_trials_service


@mark.asyncio
async def test_disease_fallback_no_requests(monkeypatch):
    # Force no requests available
    monkeypatch.setattr(disease_service, "_has_requests", False)
    monkeypatch.setattr(disease_service, "requests", None)

    service = disease_service.create_disease_service()
    assert service is not None

    maybe = service.lookup_disease("hypertension", include_symptoms=False, include_treatments=False)
    if inspect.isawaitable(maybe):
        result = await maybe
    else:
        result = maybe

    assert isinstance(result, dict)
    # BaseService wraps response as {'data': ...}
    assert "data" in result
    data = result["data"]
    assert "name" in data or isinstance(data, dict)


@mark.asyncio
async def test_clinical_trials_fallback_stub(monkeypatch):
    # Force clinical trials to use stub (disable live)
    monkeypatch.setattr(clinical_trials_service, "_has_requests", False)

    service = clinical_trials_service.create_clinical_trials_service()
    assert service is not None

    result = await service.search_trials("diabetes", limit=2)
    assert isinstance(result, dict)
    # Stub response includes 'trials' and 'total_results'
    assert "trials" in result
    assert "total_results" in result or "total_studies" in result
    assert isinstance(result["trials"], list)
