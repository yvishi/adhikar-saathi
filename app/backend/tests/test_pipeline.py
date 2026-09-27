import json

import pytest

from app.backend import llm, pipeline, sarvam
from app.backend.errors import AppError
from app.backend.pipeline import parse_llm_json, postprocess


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
    d = {"type": "answer", "answer_hi": "हिंदी", "answer_en": "English", "used_ids": ["W-01"]}
    d.update(kw)
    return json.dumps(d, ensure_ascii=False)


# ---- JSON repair
def test_parse_plain_and_fenced_and_wrapped():
    assert parse_llm_json(js())["type"] == "answer"
    assert parse_llm_json("```json\n" + js() + "\n```")["used_ids"] == ["W-01"]
    assert parse_llm_json("Here you go: " + js() + " Hope this helps")["answer_en"] == "English"


def test_parse_invalid():
    assert parse_llm_json("not json") is None
    assert parse_llm_json("") is None
    assert parse_llm_json('{"type": "maybe", "answer_hi": "x"}') is None
    assert parse_llm_json("[1,2]") is None


def test_parse_string_used_ids_normalised():
    assert parse_llm_json(js(used_ids="W-01"))["used_ids"] == ["W-01"]


# ---- post-check rules
def test_postprocess_answer_ok_and_ids_stripped():
    r = postprocess(parse_llm_json(js(answer_hi="जवाब [W-01]", used_ids=["W-01", "W-01", "Z-99"])), ["W-01", "W-02"])
    assert r["type"] == "answer" and r["used_ids"] == ["W-01"] and "W-01" not in r["answer_hi"]


def test_postprocess_answer_without_valid_id_becomes_refuse():
    r = postprocess(parse_llm_json(js(used_ids=["Z-99"])), ["W-01"])
    assert r["type"] == "refuse" and r["used_ids"] == []
    r = postprocess(parse_llm_json(js(used_ids=[])), ["W-01"])
    assert r["type"] == "refuse"


def test_postprocess_refuse_and_clarify_have_no_ids():
    for t in ("refuse", "clarify"):
        r = postprocess(parse_llm_json(js(type=t, used_ids=["W-01"])), ["W-01"])
        assert r["type"] == t and r["used_ids"] == []


def test_postprocess_none_is_refuse():
    assert postprocess(None, ["W-01"])["type"] == "refuse"


# ---- full turns with mocked LLM
def test_ask_answer_sources_and_cost(monkeypatch):
    fake_llm(monkeypatch, js(used_ids=["W-01", "W-03"]))
    r = pipeline.ask(text="minimum wage", want_audio=False, retrieval="all")
    assert r["type"] == "answer"
    assert [s["card_id"] for s in r["sources"]] == ["W-01", "W-03"]
    assert set(r["sources"][0]) == {"card_id", "title", "source_name", "section", "url"}
    assert r["audio_b64"] is None
    assert r["cost_inr_est"] == pytest.approx(100 * 29.28e-6 + 50 * 73.20e-6, abs=1e-4)
    assert "debug" not in r


def test_ask_refuse_has_no_sources(monkeypatch):
    fake_llm(monkeypatch, js(type="refuse", used_ids=["W-01"]))
    r = pipeline.ask(text="land dispute", want_audio=False, retrieval="all")
    assert r["type"] == "refuse" and r["sources"] == []


def test_ask_invalid_used_ids_subset_and_refusal(monkeypatch):
    monkeypatch.setenv("DEBUG_RESPONSES", "1")
    fake_llm(monkeypatch, js(used_ids=["W-01", "NOPE-1"]))
    r = pipeline.ask(text="q", want_audio=False, retrieval="all")
    assert set(r["debug"]["used_ids"]) <= set(r["debug"]["retrieved_ids"]) and r["debug"]["used_ids"] == ["W-01"]
    fake_llm(monkeypatch, js(used_ids=["NOPE-1"]))
    assert pipeline.ask(text="q", want_audio=False, retrieval="all")["type"] == "refuse"


def test_ask_invalid_json_retries_once_then_ok(monkeypatch):
    calls = fake_llm(monkeypatch, "garbage", js())
    r = pipeline.ask(text="q", want_audio=False, retrieval="all")
    assert r["type"] == "answer" and len(calls) == 2


def test_ask_invalid_json_twice_falls_back_to_refuse(monkeypatch):
    calls = fake_llm(monkeypatch, "garbage", "still garbage")
    r = pipeline.ask(text="q", want_audio=False, retrieval="all")
    assert r["type"] == "refuse" and r["sources"] == [] and len(calls) == 2


def test_ask_verify_downgrades(monkeypatch):
    monkeypatch.setenv("VERIFY", "1")
    fake_llm(monkeypatch, js(), '{"supported": false, "unsupported": ["x"]}')
    assert pipeline.ask(text="q", want_audio=False, retrieval="all")["type"] == "refuse"
    fake_llm(monkeypatch, js(), '{"supported": true, "unsupported": []}')
    assert pipeline.ask(text="q", want_audio=False, retrieval="all")["type"] == "answer"


def test_ask_no_retrieved_cards_skips_llm(monkeypatch):
    calls = fake_llm(monkeypatch)
    monkeypatch.setattr(pipeline, "retrieve", lambda q, m, k=4: [])
    assert pipeline.ask(text="q", want_audio=False)["type"] == "refuse" and calls == []


def test_ask_tts_failure_degrades_to_text(monkeypatch):
    fake_llm(monkeypatch, js())

    def bad_tts(text):
        raise AppError("tts_failed")
    monkeypatch.setattr(sarvam, "tts", bad_tts)
    r = pipeline.ask(text="q", retrieval="all")
    assert r["type"] == "answer" and r["audio_b64"] is None


def test_ask_bad_input():
    with pytest.raises(AppError) as e:
        pipeline.ask()
    assert e.value.code == "bad_request"
    with pytest.raises(AppError):
        pipeline.ask(text="q", provider="nope")


def test_stt_no_speech(monkeypatch):
    monkeypatch.setattr(sarvam, "stt", lambda *a, **k: {"transcript": "", "language_code": None})
    with pytest.raises(AppError) as e:
        pipeline.ask(audio=(b"x" * 10, "a.wav", "audio/wav"))
    assert e.value.code == "no_speech"


# ---- session memory
def test_session_memory_used_in_followup(monkeypatch):
    monkeypatch.setenv("DEBUG_RESPONSES", "1")
    seen = []
    monkeypatch.setattr(pipeline, "retrieve", lambda q, m, k=4: seen.append(q) or pipeline._load()[0][:2])
    calls = fake_llm(monkeypatch, js(), js())
    r1 = pipeline.ask(text="first question", want_audio=False)
    r2 = pipeline.ask(session_id=r1["session_id"], text="second", want_audio=False)
    assert seen == ["first question", "first question second"]
    assert r2["debug"]["rewritten_query"] == "first question second"
    assert "first question" in calls[1][1]["content"]
    assert r1["session_id"] == r2["session_id"]


# ---- integration fixes
def test_low_score_query_refuses_without_llm_call(monkeypatch):
    calls = fake_llm(monkeypatch, js())
    monkeypatch.setattr(pipeline, "retrieve", lambda q, m, k=4: [
        dict(pipeline._load()[0][0], score=0.01), dict(pipeline._load()[0][1], score=0.0)])
    r = pipeline.ask(text="what is the score of the cricket match", want_audio=False)
    assert r["type"] == "refuse" and r["sources"] == [] and calls == []


def test_score_at_or_above_floor_still_reaches_llm(monkeypatch):
    calls = fake_llm(monkeypatch, js())
    monkeypatch.setattr(pipeline, "retrieve", lambda q, m, k=4: [dict(pipeline._load()[0][0], score=0.5)])
    pipeline.ask(text="minimum wage", want_audio=False)
    assert len(calls) == 1


def test_retriever_failure_is_loud_and_labelled(monkeypatch, caplog):
    class Boom:
        mode = "hybrid"

        def retrieve(self, q, k=4):
            raise RuntimeError("index broken")
    pipeline._load()
    monkeypatch.setitem(pipeline._cache, "retriever", Boom())
    with caplog.at_level("WARNING", logger="adhikar.pipeline"):
        got = pipeline.retrieve("minimum wage", "topk")
    assert "RETRIEVER FAILED" in caplog.text
    assert pipeline.retriever_label("topk", got) == "keyword-fallback"


def test_source_url_is_never_null(monkeypatch):
    card = dict(pipeline._load()[0][0])
    card["source"] = dict(card["source"], url=None)
    assert pipeline._source(card)["url"] == ""


def test_strip_ids_removes_dangling_lead_in():
    assert pipeline._strip_ids("हाँ, आप रजिस्टर कर सकते हैं। S-01 के अनुसार, 16 साल या उससे अधिक उम्र वाले जुड़ सकते हैं।") == \
        "हाँ, आप रजिस्टर कर सकते हैं। 16 साल या उससे अधिक उम्र वाले जुड़ सकते हैं।"
    assert pipeline._strip_ids("According to S-01, workers can join. Free [W-01].") == "workers can join. Free."
