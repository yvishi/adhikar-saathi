import json

import pytest
import requests

from app.backend import config, languages, llm, pipeline, prompts, sarvam
from app.backend.errors import AppError

from .conftest import FakeResp


def patch_post(monkeypatch, resp_by_path, sink=None):
    """resp_by_path: {"/translate": FakeResp(...), "/text-to-speech": FakeResp(...)}."""
    def post(url, **kw):
        if sink is not None:
            sink.append((url, kw))
        for suffix, resp in resp_by_path.items():
            if url.endswith(suffix):
                if isinstance(resp, Exception):
                    raise resp
                return resp
        raise AssertionError(f"unexpected POST {url}")
    monkeypatch.setattr(requests, "post", post)


def fake_llm(monkeypatch, *texts, usage=(100, 50)):
    calls = []
    it = iter(texts)

    def complete(messages, provider=None, max_tokens=500, temperature=0.2):
        calls.append(messages)
        return {"text": next(it), "usage": {"prompt_tokens": usage[0], "completion_tokens": usage[1]},
                "provider": provider or "sarvam"}
    monkeypatch.setattr(llm, "complete", complete)
    return calls


def js(**kw):
    d = {"type": "answer", "answer_hi": "ਪੰਜਾਬੀ ਜਵਾਬ", "answer_en": "minimum wage answer", "used_ids": ["W-01"]}
    d.update(kw)
    return json.dumps(d, ensure_ascii=False)


# ---- registry
def test_registry_shape_and_hindi_is_verified():
    hi = languages.get("hi-IN")
    assert hi["verified_by_owner"] is True
    assert languages.DEFAULT_LANGUAGE == "hi-IN"
    others = [l for l in languages.LANGUAGES if l["code"] != "hi-IN"]
    assert 2 <= len(others) <= 4
    for l in others:
        assert l["verified_by_owner"] is False
        assert l["tts_speaker"]
    assert languages.is_supported("pa-IN") and not languages.is_supported("zz-ZZ")


def test_needs_translation_and_disclaimer_flags():
    assert not languages.needs_translation_for_retrieval("hi-IN")
    assert not languages.needs_translation_for_retrieval("en-IN")
    assert languages.needs_translation_for_retrieval("pa-IN")
    assert not languages.needs_disclaimer("hi-IN")
    assert languages.needs_disclaimer("pa-IN")


# ---- prompts
def test_build_messages_default_language_matches_original_system_prompt():
    msgs = prompts.build_messages("q", [], [])
    assert msgs[0]["content"] == prompts.SYSTEM_PROMPT
    msgs_hi = prompts.build_messages("q", [], [], language=languages.get("hi-IN"))
    assert msgs_hi[0]["content"] == prompts.SYSTEM_PROMPT


def test_build_messages_other_language_names_it_in_the_prompt():
    pa = languages.get("pa-IN")
    msgs = prompts.build_messages("q", [], [], language=pa)
    assert "Punjabi" in msgs[0]["content"] and "Gurmukhi" in msgs[0]["content"]
    assert msgs[0]["content"] != prompts.SYSTEM_PROMPT


# ---- pipeline: language validation
def test_ask_unknown_language_is_bad_request():
    with pytest.raises(AppError) as e:
        pipeline.ask(text="q", language="zz-ZZ")
    assert e.value.code == "bad_request"


def test_ask_default_language_response_unchanged_shape(monkeypatch):
    fake_llm(monkeypatch, js(answer_hi="जवाब", answer_en="answer"))
    r = pipeline.ask(text="minimum wage", want_audio=False, retrieval="all")
    assert "language" not in r and "disclaimer_en" not in r and "disclaimer_hi" not in r


# ---- pipeline: a non-Hindi language end to end (mocked network)
def test_ask_other_language_translates_query_and_adds_disclaimer(monkeypatch):
    sink = []
    patch_post(monkeypatch, {
        "/translate": FakeResp(200, {"translated_text": "minimum wage claim", "source_language_code": "pa-IN"}),
    }, sink)
    fake_llm(monkeypatch, js())
    r = pipeline.ask(text="ਮੈਨੂੰ ਤਨਖਾਹ ਨਹੀਂ ਮਿਲੀ", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "answer"
    assert r["language"] == "pa-IN"
    assert "Punjabi" in r["disclaimer_en"]
    assert r["disclaimer_hi"] == prompts.LANG_DISCLAIMER_HI
    # the retriever/keyword-fallback never sees Punjabi text directly: it was translated first
    assert any(url.endswith("/translate") for url, kw in sink)
    body = sink[0][1]["json"]
    assert body["source_language_code"] == "auto" and body["target_language_code"] == "en-IN"
    assert body["model"] == "mayura:v1"
    # translate cost is included
    assert r["cost_inr_est"] > 0


def test_ask_other_language_tts_uses_registry_speaker(monkeypatch):
    patch_post(monkeypatch, {
        "/translate": FakeResp(200, {"translated_text": "minimum wage", "source_language_code": "pa-IN"}),
        "/text-to-speech": FakeResp(200, {"audios": ["AAAA"]}),
    })
    fake_llm(monkeypatch, js())
    r = pipeline.ask(text="q", want_audio=True, retrieval="all", language="pa-IN")
    assert r["audio_b64"] is not None


def test_ask_other_language_translate_failure_falls_back_to_original_query(monkeypatch, caplog):
    patch_post(monkeypatch, {"/translate": FakeResp(500, text="boom")})
    fake_llm(monkeypatch, js())
    with caplog.at_level("WARNING", logger="adhikar.pipeline"):
        r = pipeline.ask(text="q", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "answer"  # still answers using the untranslated query
    assert "Query translation failed" in caplog.text


def test_ask_default_language_never_calls_translate(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("translate should not be called for hi-IN")
    monkeypatch.setattr(sarvam, "translate", boom)
    fake_llm(monkeypatch, js(answer_hi="जवाब", answer_en="answer"))
    r = pipeline.ask(text="minimum wage", want_audio=False, retrieval="all")
    assert r["type"] == "answer"


def test_mock_mode_ignores_language_and_never_calls_translate(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "1")
    r = pipeline.ask(text="minimum wage", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] in ("answer", "refuse", "clarify")


def test_ask_other_language_model_refusal_still_gets_disclaimer(monkeypatch):
    """A refusal the MODEL worded in the target language (e.g. an adversarial question that
    reached the LLM) is just as unverified as an answer, so it still needs the disclaimer -
    unlike the fixed REFUSE_HI/REFUSE_EN fallback used when the LLM was never called."""
    patch_post(monkeypatch, {"/translate": FakeResp(200, {"translated_text": "state minimum wage", "source_language_code": "pa-IN"})})
    fake_llm(monkeypatch, js(type="refuse", answer_hi="ਮੇਰੇ ਕੋਲ ਇਹ ਜਾਣਕਾਰੀ ਨਹੀਂ ਹੈ", answer_en="I do not have this information", used_ids=[]))
    r = pipeline.ask(text="q", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "refuse"
    assert r["answer_hi"] != prompts.REFUSE_HI
    assert r["disclaimer_en"] and r["disclaimer_hi"] == prompts.LANG_DISCLAIMER_HI


def test_ask_other_language_fixed_fallback_refusal_has_no_disclaimer(monkeypatch):
    """When no card is retrieved at all the LLM is never called and the fixed, already-verified
    REFUSE_HI/REFUSE_EN text is returned as-is (in Hindi/English) -- no disclaimer needed."""
    patch_post(monkeypatch, {"/translate": FakeResp(200, {"translated_text": "q", "source_language_code": "pa-IN"})})
    calls = fake_llm(monkeypatch)
    monkeypatch.setattr(pipeline, "retrieve", lambda q, m, k=4: [])
    r = pipeline.ask(text="q", want_audio=False, language="pa-IN")
    assert r["type"] == "refuse" and calls == []
    assert r["answer_hi"] == prompts.REFUSE_HI
    assert r["language"] == "pa-IN"  # the language was still recorded...
    assert "disclaimer_en" not in r and "disclaimer_hi" not in r  # ...but no false disclaimer


# ---- LANG_VERIFY safety net
def test_lang_verify_downgrades_on_low_overlap(monkeypatch):
    monkeypatch.setenv("LANG_VERIFY", "1")
    patch_post(monkeypatch, {
        "/translate": FakeResp(200, {"translated_text": "completely unrelated text about weather", "source_language_code": "pa-IN"}),
    })
    fake_llm(monkeypatch, js(answer_en="you have the right to minimum wage under the wages code"))
    r = pipeline.ask(text="q", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "refuse"
    assert r["answer_en"] == prompts.LANG_VERIFY_FAIL_EN


def test_lang_verify_passes_on_good_overlap(monkeypatch):
    monkeypatch.setenv("LANG_VERIFY", "1")
    calls = {"n": 0}

    def post(url, **kw):
        calls["n"] += 1
        if url.endswith("/translate"):
            # first call: query -> English; second call: back-translation for verification
            if calls["n"] == 1:
                return FakeResp(200, {"translated_text": "minimum wage question", "source_language_code": "pa-IN"})
            return FakeResp(200, {"translated_text": "you have the right to minimum wage", "source_language_code": "pa-IN"})
        raise AssertionError(url)
    monkeypatch.setattr(requests, "post", post)
    fake_llm(monkeypatch, js(answer_en="you have the right to minimum wage"))
    r = pipeline.ask(text="q", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "answer"


def test_lang_verify_translate_failure_fails_closed(monkeypatch):
    monkeypatch.setenv("LANG_VERIFY", "1")
    calls = {"n": 0}

    def post(url, **kw):
        calls["n"] += 1
        if url.endswith("/translate"):
            if calls["n"] == 1:
                return FakeResp(200, {"translated_text": "minimum wage question", "source_language_code": "pa-IN"})
            return FakeResp(500, text="boom")
        raise AssertionError(url)
    monkeypatch.setattr(requests, "post", post)
    fake_llm(monkeypatch, js(answer_en="you have the right to minimum wage"))
    r = pipeline.ask(text="q", want_audio=False, retrieval="all", language="pa-IN")
    assert r["type"] == "refuse"


# ---- sarvam.translate request shape
def test_translate_request_shape(monkeypatch):
    sink = []
    patch_post(monkeypatch, {"/translate": FakeResp(200, {"translated_text": "hello", "source_language_code": "pa-IN"})}, sink)
    out = sarvam.translate("ਸਤ ਸ੍ਰੀ ਅਕਾਲ", source_language_code="auto", target_language_code="en-IN")
    assert out == {"translated_text": "hello", "source_language_code": "pa-IN"}
    url, kw = sink[0]
    assert url.endswith("/translate")
    assert kw["json"]["model"] == "mayura:v1"
    assert kw["json"]["source_language_code"] == "auto"
    assert kw["headers"]["api-subscription-key"] == "test-key"


def test_translate_error_mapping(monkeypatch):
    patch_post(monkeypatch, {"/translate": FakeResp(429)})
    with pytest.raises(AppError) as e:
        sarvam.translate("x")
    assert e.value.code == "rate_limited"
    patch_post(monkeypatch, {"/translate": FakeResp(500)})
    with pytest.raises(AppError) as e:
        sarvam.translate("x")
    assert e.value.code == "llm_failed"


def test_translate_empty_text_short_circuits(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("should not call the network for empty text")
    monkeypatch.setattr(requests, "post", boom)
    assert sarvam.translate("   ") == {"translated_text": "", "source_language_code": "auto"}


# ---- tts backward compatibility with new params
def test_tts_other_language_request_shape(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "TTS_CACHE_DIR", tmp_path)
    sink = []
    import base64
    wav = sarvam.silent_wav(0.1)
    b64 = base64.b64encode(wav).decode()
    patch_post(monkeypatch, {"/text-to-speech": FakeResp(200, {"audios": [b64]})}, sink)
    out = sarvam.tts("ਸਤ ਸ੍ਰੀ ਅਕਾਲ", language_code="pa-IN", speaker="shubh")
    assert out == wav
    body = sink[0][1]["json"]
    assert (body["language_code"], body["speaker"]) == ("pa-IN", "shubh")
