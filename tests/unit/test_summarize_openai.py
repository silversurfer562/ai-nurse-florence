# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/tests/unit/test_summarize_openai.py
import pytest


def test_call_chatgpt_returns_text(monkeypatch):
    # Fake client that mimics client.responses.create returning output_text
    class FakeResponses:
        def create(self, model, input, **kwargs):
            return {"output_text": "Hello from fake"}

    class FakeClient:
        def __init__(self):
            self.responses = FakeResponses()

    # patch get_client to return our fake
    monkeypatch.setattr("services.openai_client.get_client", lambda: FakeClient())
    
    # Force reload of the module to pick up the patch
    import sys
    if 'services.summarize_service' in sys.modules:
        del sys.modules['services.summarize_service']

    from services.summarize_service import call_chatgpt

    out = call_chatgpt("test prompt", model="gpt-4o-mini")
    assert "Hello from fake" in out


def test_call_chatgpt_raises_when_no_client(monkeypatch):
    # patch get_client to return None
    monkeypatch.setattr("services.openai_client.get_client", lambda: None)
    
    # Force reload of the module to pick up the patch
    import sys
    if 'services.summarize_service' in sys.modules:
        del sys.modules['services.summarize_service']

    from services.summarize_service import call_chatgpt

    with pytest.raises(RuntimeError):
        call_chatgpt("test")
