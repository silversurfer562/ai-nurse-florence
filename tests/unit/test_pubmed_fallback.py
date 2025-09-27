import pytest
from pytest import mark

from src.services import pubmed_service


@mark.asyncio
async def test_pubmed_fallback_no_requests_or_xml(monkeypatch):
    # Simulate environment without requests and XML
    monkeypatch.setattr(pubmed_service, "_has_requests", False)
    monkeypatch.setattr(pubmed_service, "_has_xml", False)
    monkeypatch.setattr(pubmed_service, "requests", None)
    monkeypatch.setattr(pubmed_service, "ET", None)

    service = pubmed_service.create_pubmed_service()
    assert service is not None

    result = await service.search_literature("nursing assessment", max_results=2)
    assert isinstance(result, dict)
    assert "data" in result
    data = result["data"]
    assert "articles" in data
    assert data["total_results"] == len(data["articles"]) 
    # Stub articles use pmid like 'stub_1'
    assert data["articles"][0]["pmid"].startswith("stub_")


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
