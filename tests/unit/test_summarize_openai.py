# filepath: /Users/patrickroebuck/Documents/pycharm-projects/nurses_api/tests/unit/test_summarize_openai.py
import pytest


def test_call_chatgpt_returns_text(monkeypatch):
    # Import the module first
    from services.summarize_service import call_chatgpt
    
    # Fake client that mimics client.chat.completions.create structure
    class FakeChoice:
        def __init__(self, content):
            self.message = type('Message', (), {'content': content})()
    
    class FakeCompletion:
        def __init__(self, content):
            self.choices = [FakeChoice(content)]
    
    class FakeCompletions:
        def create(self, model, messages, **kwargs):
            return FakeCompletion("Hello from fake")
    
    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeClient:
        def __init__(self):
            self.chat = FakeChat()

    # patch get_client to return our fake
    monkeypatch.setattr("services.summarize_service.get_client", lambda: FakeClient())

    out = call_chatgpt("test prompt", model="gpt-4o-mini")
    assert "Hello from fake" in out


def test_call_chatgpt_raises_when_no_client(monkeypatch):
    # Import the module first
    from services.summarize_service import call_chatgpt
    
    # patch get_client to return None
    monkeypatch.setattr("services.summarize_service.get_client", lambda: None)

    with pytest.raises(RuntimeError):
        call_chatgpt("test")
