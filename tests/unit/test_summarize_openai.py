# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/tests/unit/test_summarize_openai.py
import pytest


def test_call_chatgpt_returns_text(monkeypatch):
    # Fake client that mimics the actual OpenAI API structure
    class FakeChoice:
        def __init__(self):
            self.message = type('Message', (), {'content': 'Hello from fake'})()

    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            response = type('Response', (), {'choices': [FakeChoice()]})()
            return response

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()

    # patch get_client to return our fake
    monkeypatch.setattr("services.summarize_service.get_client", lambda: FakeClient())

    from services.summarize_service import call_chatgpt

    out = call_chatgpt("test prompt", model="gpt-4o-mini")
    assert "Hello from fake" in out


def test_call_chatgpt_raises_when_no_client(monkeypatch):
    # patch get_client to return None
    monkeypatch.setattr("services.summarize_service.get_client", lambda: None)

    from services.summarize_service import call_chatgpt

    with pytest.raises(RuntimeError):
        call_chatgpt("test")
