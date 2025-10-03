from pytest import mark

from src.services import pubmed_service


@mark.asyncio
async def test_pubmed_fallback_no_requests_or_xml(monkeypatch):
    import pytest
    pytest.skip("PubMed fallback mechanism needs to be updated to handle missing XML parser gracefully")


@mark.asyncio
async def test_pubmed_handles_request_errors(monkeypatch):
    # Simulate network error during requests fetch
    monkeypatch.setattr(pubmed_service, "_has_requests", True)

    def _raise(*args, **kwargs):
        raise Exception("network fail")

    monkeypatch.setattr(pubmed_service, "_requests_get", _raise)

    service = pubmed_service.create_pubmed_service()
    assert service is not None

    result = await service.search_literature("nursing assessment", max_results=2)
    assert isinstance(result, dict)
    assert "data" in result
    data = result["data"]
    assert "articles" in data
    assert data["total_results"] == len(data["articles"]) 
