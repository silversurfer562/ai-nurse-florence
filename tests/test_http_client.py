from __future__ import annotations

import types
import pytest
from src.utils.http_client import safe_get_json_sync, safe_get_json


class DummyResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data

    def raise_for_status(self):
        return None


def test_safe_get_json_sync_monkeypatch(monkeypatch):
    dummy = DummyResponse({"ok": True})

    class Req:
        @staticmethod
        def get(url, params=None, timeout=None):
            return dummy

    # Patch the requests symbol in the http_client module
    monkeypatch.setattr("src.utils.http_client.requests", Req, raising=False)
    monkeypatch.setattr("src.utils.http_client._has_requests", True, raising=False)

    res = safe_get_json_sync("http://example", params={"q": "x"})
    assert res == {"ok": True}


@pytest.mark.asyncio
async def test_safe_get_json_async_fallback(monkeypatch):
    # Simulate httpx missing and use requests in thread
    monkeypatch.setattr("src.utils.http_client.httpx", None, raising=False)
    monkeypatch.setattr("src.utils.http_client._has_httpx", False, raising=False)
    monkeypatch.setattr(
        "src.utils.http_client.requests",
        type("R", (), {"get": staticmethod(lambda *a, **k: DummyResponse({"ok": True}))}),
        raising=False,
    )
    monkeypatch.setattr("src.utils.http_client._has_requests", True, raising=False)

    res = await safe_get_json("http://example", params={"q": "x"})
    assert res == {"ok": True}
