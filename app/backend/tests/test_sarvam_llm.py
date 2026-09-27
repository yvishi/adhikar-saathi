import base64

import pytest
import requests

from app.backend import config, llm, sarvam
from app.backend.errors import AppError

from .conftest import FakeResp


def patch_post(monkeypatch, resp, sink=None):
    def post(url, **kw):
        if sink is not None:
            sink.append((url, kw))
        if isinstance(resp, Exception):
            raise resp
        return resp
    monkeypatch.setattr(requests, "post", post)


def test_stt_request_shape_and_result(monkeypatch):
    sink = []
    patch_post(monkeypatch, FakeResp(200, {"transcript": " नमस्ते ", "language_code": "hi-IN"}), sink)
    out = sarvam.stt(b"abc", "q.webm", "audio/webm;codecs=opus")
    assert out == {"transcript": "नमस्ते", "language_code": "hi-IN"}
    url, kw = sink[0]
    assert url.endswith("/speech-to-text") and kw["data"] == {"model": "saaras:v3", "mode": "transcribe"}
    assert kw["files"]["file"][2] == "audio/webm" and kw["headers"] == {"api-subscription-key": "test-key"}


@pytest.mark.parametrize("status,body,code", [
    (403, "", "stt_failed"), (401, "", "stt_failed"), (429, "", "rate_limited"),
    (400, "audio duration exceeds 30 seconds", "audio_too_long"), (400, "bad codec", "bad_request"),
    (500, "", "stt_failed"),
])
def test_stt_error_mapping(monkeypatch, status, body, code):
    patch_post(monkeypatch, FakeResp(status, text=body))
    with pytest.raises(AppError) as e:
        sarvam.stt(b"abc")
    assert e.value.code == code and e.value.message_hi and e.value.message_en
    assert "test-key" not in e.value.message_en


def test_stt_network_error(monkeypatch):
    patch_post(monkeypatch, requests.ConnectionError("x"))
    with pytest.raises(AppError) as e:
        sarvam.stt(b"abc")
    assert e.value.code == "stt_failed"


def test_stt_long_wav_rejected_locally():
    wav = sarvam.silent_wav(seconds=31, rate=8000)
    with pytest.raises(AppError) as e:
        sarvam.stt(wav, "a.wav", "audio/wav")
    assert e.value.code == "audio_too_long"


def test_tts_request_shape_cap_and_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "TTS_CACHE_DIR", tmp_path)
    monkeypatch.setenv("TTS_CACHE", "1")
    sink = []
    wav = sarvam.silent_wav(0.1)
    b64 = base64.b64encode(wav).decode()
    half = len(b64) // 2
    patch_post(monkeypatch, FakeResp(200, {"audios": [b64[:half], b64[half:]]}), sink)
    long_text = "यह वाक्य है। " * 100
    assert sarvam.tts(long_text) == wav
    body = sink[0][1]["json"]
    assert len(body["text"]) <= 400 and body["text"].endswith("।")
    assert (body["language_code"], body["model"], body["speaker"]) == ("hi-IN", "bulbul:v3", "shubh")
    assert sarvam.tts(long_text) == wav and len(sink) == 1  # second call served from disk


def test_tts_errors(monkeypatch):
    patch_post(monkeypatch, FakeResp(403))
    with pytest.raises(AppError) as e:
        sarvam.tts("नमस्ते")
    assert e.value.code == "tts_failed"
    patch_post(monkeypatch, FakeResp(429))
    with pytest.raises(AppError) as e:
        sarvam.tts("नमस्ते")
    assert e.value.code == "rate_limited"


def test_sarvam_chat_shape(monkeypatch):
    sink = []
    patch_post(monkeypatch, FakeResp(200, {"choices": [{"message": {"content": "<think>x</think>hello"}}],
                                           "usage": {"prompt_tokens": 7, "completion_tokens": 3}}), sink)
    r = llm.complete([{"role": "user", "content": "hi"}])
    assert r == {"text": "hello", "usage": {"prompt_tokens": 7, "completion_tokens": 3}, "provider": "sarvam"}
    url, kw = sink[0]
    assert url == "https://api.sarvam.ai/v1/chat/completions"
    assert kw["json"]["model"] == "sarvam-105b" and kw["json"]["reasoning_effort"] is None
    assert kw["headers"]["api-subscription-key"] == "test-key"


def test_other_providers_are_openai_compatible(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "g")
    monkeypatch.setenv("GEMINI_API_KEY", "m")
    sink = []
    patch_post(monkeypatch, FakeResp(200, {"choices": [{"message": {"content": "ok"}}]}), sink)
    assert llm.complete([], provider="groq")["provider"] == "groq"
    assert llm.complete([], provider="gemini")["usage"] == {"prompt_tokens": 0, "completion_tokens": 0}
    assert sink[0][0] == "https://api.groq.com/openai/v1/chat/completions"
    assert sink[0][1]["headers"]["Authorization"] == "Bearer g"
    assert sink[1][0] == "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    assert "reasoning_effort" not in sink[0][1]["json"]


def test_llm_missing_key_and_unknown_provider():
    with pytest.raises(AppError) as e:
        llm.complete([], provider="groq")
    assert e.value.code == "bad_request"
    with pytest.raises(AppError):
        llm.complete([], provider="nope")


def test_llm_error_mapping(monkeypatch):
    for status, code in ((403, "llm_failed"), (429, "rate_limited"), (500, "llm_failed")):
        patch_post(monkeypatch, FakeResp(status))
        with pytest.raises(AppError) as e:
            llm.complete([])
        assert e.value.code == code
    patch_post(monkeypatch, FakeResp(200, {"weird": 1}))
    with pytest.raises(AppError):
        llm.complete([])
