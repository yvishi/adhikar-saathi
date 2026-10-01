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


# ---- /api/ask `language` form field (was silently dropped before; the dropdown was a no-op)
def test_ask_language_field_reaches_pipeline(mock, monkeypatch):
    seen = {}
    real = pipeline.ask

    def spy(**kw):
        seen.update(kw)
        return real(**kw)
    monkeypatch.setattr(pipeline, "ask", spy)
    for code in ("pa-IN", "bn-IN", "mr-IN"):
        r = client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false", "language": code})
        assert r.status_code == 200 and seen["language"] == code
        assert r.json()["language"] == code
    client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"})
    assert seen["language"] is None
    client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false", "language": "  "})
    assert seen["language"] is None


def test_ask_language_omitted_keeps_hindi_shape(mock):
    j = client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"}).json()
    assert set(j) == ASK_KEYS


def test_ask_unknown_language_is_400(mock):
    r = client.post("/api/ask", data={"text": "minimum wage", "language": "xx-YY"})
    assert r.status_code == 400 and r.json()["error"]["code"] == "bad_request"


def test_ask_language_end_to_end_over_http(monkeypatch):
    """Non-mock path over HTTP with faked network: translate for retrieval, prompt names the
    language, TTS is asked for that language, response carries language + disclaimers."""
    import json as _json

    import requests

    from app.backend import llm, prompts
    from .conftest import FakeResp
    sink = []

    def post(url, **kw):
        sink.append((url, kw))
        if url.endswith("/translate"):
            return FakeResp(200, {"translated_text": "minimum wage", "source_language_code": "bn-IN"})
        if url.endswith("/text-to-speech"):
            return FakeResp(200, {"audios": ["AAAA"]})
        raise AssertionError(f"unexpected POST {url}")
    monkeypatch.setattr(requests, "post", post)
    msgs_seen = []

    def complete(messages, provider=None, max_tokens=500, temperature=0.2):
        msgs_seen.append(messages)
        return {"text": _json.dumps({"type": "answer", "answer_hi": "ন্যূনতম মজুরি আপনার অধিকার।",
                                     "answer_en": "Minimum wage is your right.", "used_ids": ["W-01"]},
                                    ensure_ascii=False),
                "usage": {"prompt_tokens": 10, "completion_tokens": 10}, "provider": "sarvam"}
    monkeypatch.setattr(llm, "complete", complete)
    j = client.post("/api/ask", data={"text": "আমার ন্যূনতম মজুরি", "retrieval": "all", "language": "bn-IN"}).json()
    assert j["language"] == "bn-IN" and j["answer_hi"].startswith("ন্যূনতম")
    assert "Bengali" in j["disclaimer_en"] and j["disclaimer_hi"] == prompts.LANG_DISCLAIMER_HI
    assert "Bengali" in msgs_seen[0][0]["content"]
    tts = [kw["json"] for url, kw in sink if url.endswith("/text-to-speech")]
    assert tts and tts[0]["language_code"] == "bn-IN"
    assert any(url.endswith("/translate") for url, _ in sink)
