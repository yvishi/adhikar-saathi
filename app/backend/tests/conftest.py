import pytest
import requests

from app.backend import config, pipeline
from app.backend.session import SessionStore


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    """No test may touch the network or the real cards file; tests opt in to mocks explicitly."""
    def boom(*a, **k):
        raise AssertionError("network call attempted in a test")
    monkeypatch.setattr(requests, "post", boom)
    monkeypatch.setattr(config, "CARDS_PATH", config.FIXTURE_CARDS_PATH)
    monkeypatch.setattr(config, "TTS_CACHE_DIR", config.ROOT / "app" / "data" / "cache" / "tts_test")
    for name in ("MOCK_MODE", "LLM_PROVIDER", "RETRIEVAL_MODE", "DEBUG_RESPONSES", "TTS_CACHE", "VERIFY",
                 "GEMINI_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("SARVAM_API_KEY", "test-key")
    pipeline._cache.update(key=None, cards=[], retriever=None)
    monkeypatch.setattr(pipeline, "store", SessionStore())
    yield


class FakeResp:
    def __init__(self, status=200, json_data=None, text=""):
        self.status_code = status
        self._json = json_data
        self.text = text

    def json(self):
        return self._json
