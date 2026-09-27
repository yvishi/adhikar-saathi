import base64
import io
import wave

import pytest
from fastapi.testclient import TestClient

from app.backend import config, pipeline
from app.backend.errors import AppError
from app.backend.main import app

client = TestClient(app)

ASK_KEYS = {"session_id", "transcript", "answer_hi", "answer_en", "type", "sources", "audio_b64", "audio_mime",
            "latency_ms", "cost_inr_est"}


@pytest.fixture
def mock(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "1")


def test_health(mock):
    j = client.get("/api/health").json()
    assert j["ok"] is True and j["mock"] is True and j["cards"] >= 1
    assert set(j["providers"]) == {"sarvam", "gemini", "groq"}


def test_mock_ask_contract_shape(mock):
    r = client.post("/api/ask", data={"text": "न्यूनतम मजदूरी क्या है"})
    assert r.status_code == 200
    j = r.json()
    assert set(j) == ASK_KEYS  # no debug unless DEBUG_RESPONSES=1
    assert j["type"] == "answer" and j["sources"] and set(j["sources"][0]) == {
        "card_id", "title", "source_name", "section", "url"}
    assert set(j["latency_ms"]) == {"stt", "retrieve", "llm", "tts", "total"}
    with wave.open(io.BytesIO(base64.b64decode(j["audio_b64"]))) as w:
        assert w.getnframes() > 0
    assert j["audio_mime"] == "audio/wav"


def test_mock_refuse_and_clarify_have_no_sources(mock):
    for text, typ in (("पड़ोसी से ज़मीन का झगड़ा", "refuse"), ("mock:clarify", "clarify")):
        j = client.post("/api/ask", data={"text": text, "want_audio": "false"}).json()
        assert j["type"] == typ and j["sources"] == [] and j["audio_b64"] is None


def test_debug_flag(mock, monkeypatch):
    monkeypatch.setenv("DEBUG_RESPONSES", "1")
    j = client.post("/api/ask", data={"text": "minimum wage"}).json()
    assert set(j["debug"]) == {"retrieved_ids", "used_ids", "provider", "rewritten_query", "retriever", "retrieval_scores"}
    assert set(j["debug"]["used_ids"]) <= set(j["debug"]["retrieved_ids"])


def test_mock_audio_turn(mock):
    j = client.post("/api/ask", files={"audio": ("q.webm", b"\x01" * 100, "audio/webm")},
                    data={"want_audio": "false"}).json()
    assert j["transcript"] and j["type"] in ("answer", "refuse", "clarify")


def test_session_id_roundtrip(mock):
    a = client.post("/api/ask", data={"text": "minimum wage"}).json()
    b = client.post("/api/ask", data={"text": "and pension", "session_id": a["session_id"]}).json()
    assert a["session_id"] == b["session_id"]


def test_errors_shape(mock):
    r = client.post("/api/ask", data={})
    assert r.status_code == 400
    e = r.json()["error"]
    assert e["code"] == "bad_request" and e["message_hi"] and e["message_en"]
    r = client.post("/api/ask", data={"text": "x", "provider": "nope"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "bad_request"


def test_audio_over_5mb_rejected(mock):
    big = b"\x00" * (config.MAX_AUDIO_BYTES + 10)
    r = client.post("/api/ask", files={"audio": ("q.wav", big, "audio/wav")})
    assert r.status_code == 400 and r.json()["error"]["code"] == "bad_request"


def test_unknown_api_path_uses_error_shape():
    assert "error" in client.get("/api/nope").json()


def test_schemes_and_complaint_501_when_module_missing(monkeypatch):
    import app.backend.main as m
    monkeypatch.setattr(m, "_optional_module", lambda name, fn: None)
    for path in ("/api/schemes", "/api/complaint-draft"):
        r = client.post(path, json={})
        assert r.status_code == 501 and r.json()["error"]["message_en"]


def test_schemes_delegates(monkeypatch):
    import app.backend.main as m
    monkeypatch.setattr(m, "_optional_module", lambda name, fn: (lambda p: {"echo": p, "fn": fn}))
    assert client.post("/api/schemes", json={"age": 30}).json() == {"echo": {"age": 30}, "fn": "match"}
    assert client.post("/api/complaint-draft", json={"a": 1}).json()["fn"] == "draft"


def test_pipeline_error_becomes_http(monkeypatch):
    def boom(*a, **k):
        raise AppError("rate_limited")
    monkeypatch.setattr(pipeline, "ask", boom)
    r = client.post("/api/ask", data={"text": "x"})
    assert r.status_code == 429 and r.json()["error"]["code"] == "rate_limited"
