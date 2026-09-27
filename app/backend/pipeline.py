"""Turn orchestration: STT -> retrieval -> LLM -> post-checks -> TTS."""
import base64
import json
import logging
import os
import re
import threading
import time

from . import config, languages, llm, prompts, sarvam
from .errors import AppError
from .session import store

# Cost constants (INR), from CONTRACT section 4.
log = logging.getLogger("adhikar.pipeline")

STT_INR_PER_SEC = 30 / 3600
TTS_INR_PER_CHAR = 3 / 1000
SARVAM_LLM_IN_PER_TOKEN = 29.28 / 1e6
SARVAM_LLM_OUT_PER_TOKEN = 73.20 / 1e6
# Sarvam Translate (Mayura v1 / sarvam-translate v1), Rs 20 per 10,000 chars, verified 2026-09-27
# against https://docs.sarvam.ai/api/pricing (see app/backend/languages.py for the language facts).
TRANSLATE_INR_PER_CHAR = 20 / 10_000
# Rough keyword-overlap floor for the LANG_VERIFY=1 back-translation safety net (see
# _lang_verify_ok below): a HEURISTIC, not a guarantee, documented in this agent's final report.
LANG_VERIFY_OVERLAP_FLOOR = 0.25

MAX_TEXT_CHARS = 1000
LLM_MAX_TOKENS = 700  # Devanagari is token-hungry; JSON holds both Hindi and English
PROMPT_HISTORY_TURNS = 3
# Integration fix: when even the best card scores below this, the question is clearly off-topic:
# refuse without an LLM call (retrieval scores are 0-1). Chosen on the DEV half of the eval only;
# lowest in-scope top score there was 0.44, off-topic ones 0.00-0.01. Env MIN_RETRIEVAL_SCORE overrides.
MIN_RETRIEVAL_SCORE = 0.15

# ---------------------------------------------------------------- cards / retrieval

_cards_lock = threading.Lock()
_cache: dict = {"key": None, "cards": [], "retriever": None}


def _cards_path():
    return config.CARDS_PATH if config.CARDS_PATH.exists() else config.FIXTURE_CARDS_PATH


_STOP = set("the a an is are to of and for in on my me i do does what how can not no it be by with at or if you your "
            "have has had this that from as was will would should".split())
_HI_EXPAND = [  # Hindi hint -> English terms (only for the keyword fallback and MOCK mode)
    (("मजदूरी", "मज़दूरी", "वेतन", "पैसे", "तनख्वाह", "तनख़्वाह"), "wages unpaid wage"),
    (("न्यूनतम",), "minimum wage"),
    (("पेंशन",), "pension"),
    (("श्रम",), "e-shram registration"),
    (("बीमा",), "insurance accident"),
    (("घरेलू",), "domestic worker"),
    (("हेल्पलाइन", "14434"), "helpline"),
    (("गर्भ", "प्रसव", "मातृत्व"), "maternity"),
    (("उत्पीड़न", "छेड़"), "harassment"),
    (("ठेकेदार",), "contractor"),
]


def _tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[\s,.?!।\"'()\[\]:;/]+", text.lower()) if len(t) >= 3 and t not in _STOP]


def _expand(query: str) -> list[str]:
    extra = " ".join(en for hints, en in _HI_EXPAND if any(h in query for h in hints))
    return _tokens(query + " " + extra)


def _overlap(tokens: list[str], card: dict) -> int:
    kw = {w for k in card.get("keywords_en") or [] for w in _tokens(k)}
    title = set(_tokens(card.get("title_en", "")))
    text = set(_tokens(card.get("text_en", "")))
    score = 0
    for t in set(tokens):
        score += (2 if t in kw else 0) + (2 if t in title else 0) + (1 if t in text else 0)
    return score


def _keyword_retrieve(query: str, cards: list[dict], k: int) -> list[dict]:
    toks = _expand(query)
    scored = [(_overlap(toks, c), c) for c in cards]
    scored = [(s, c) for s, c in scored if s > 0]
    scored.sort(key=lambda x: -x[0])
    return [{**c, "score": float(s)} for s, c in scored[:k]]


def _load():
    """Returns (all non-skipped cards, retriever or None); reloads when the cards file changes."""
    path = _cards_path()
    key = (str(path), path.stat().st_mtime_ns)
    with _cards_lock:
        if _cache["key"] != key:
            raw = json.loads(path.read_text(encoding="utf-8"))
            cards = [c for c in raw if c.get("status") != "skipped"]
            retriever = None
            try:
                from app.backend.retrieval import Retriever  # owned by the retrieval agent
                retriever = Retriever(str(path))
            except Exception as e:  # integration fix: never fall back to keyword search silently
                log.warning("RETRIEVER UNAVAILABLE (%s: %s); using the weak keyword fallback", type(e).__name__, e)
                retriever = None
            _cache.update(key=key, cards=cards, retriever=retriever)
        return _cache["cards"], _cache["retriever"]


def card_count() -> int:
    try:
        return len(_load()[0])
    except Exception:
        return 0


def retrieve(query: str, mode: str, k: int = 4) -> list[dict]:
    cards, retriever = _load()
    if mode == "all":
        return list(cards)
    if retriever is not None:
        try:
            return list(retriever.retrieve(query, k=k))
        except Exception as e:
            log.warning("RETRIEVER FAILED at query time (%s: %s); using the weak keyword fallback", type(e).__name__, e)
    return [{**c, "_fallback": True} for c in _keyword_retrieve(query, cards, k)]


def retriever_label(mode: str, retrieved: list[dict]) -> str:
    """For debug output: which retrieval path actually produced the cards."""
    if mode == "all":
        return "all-cards"
    if any(c.get("_fallback") for c in retrieved):
        return "keyword-fallback"
    r = _cache.get("retriever")
    return f"retriever:{r.mode}" if r is not None else "keyword-fallback"


def _min_score() -> float:
    try:
        return float(os.getenv("MIN_RETRIEVAL_SCORE", MIN_RETRIEVAL_SCORE))
    except ValueError:
        return MIN_RETRIEVAL_SCORE


def build_query(history: list[dict], text: str) -> str:
    """Follow-ups retrieve on the last two user turns (previous + current)."""
    if history:
        return f"{history[-1]['user']} {text}"
    return text


# ---------------------------------------------------------------- LLM output handling

_TYPES = ("answer", "clarify", "refuse")
# Also removes a lead-in that only pointed at the id ("According to S-01," / "S-01 के अनुसार,").
_ID_RE = re.compile(r"\s*(?:(?i:according to)\s+)?[\[(]?\b[A-Z]{1,2}-\d{2}\b[\])]?(?:\s*के अनुसार)?\s*,?")


def parse_llm_json(text: str) -> dict | None:
    """Robustly parse the model's JSON; returns a normalised dict or None if unusable."""
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
    t = re.sub(r"\s*```$", "", t)
    obj = None
    for cand in (t, t[t.find("{"): t.rfind("}") + 1] if "{" in t and "}" in t else None):
        if not cand:
            continue
        try:
            obj = json.loads(cand)
            break
        except ValueError:
            continue
    if not isinstance(obj, dict):
        return None
    typ = str(obj.get("type", "")).strip().lower()
    if typ not in _TYPES:
        return None
    used = obj.get("used_ids") or []
    if isinstance(used, str):
        used = [used]
    if not isinstance(used, list):
        used = []
    return {
        "type": typ,
        "answer_hi": str(obj.get("answer_hi") or "").strip(),
        "answer_en": str(obj.get("answer_en") or "").strip(),
        "used_ids": [str(u).strip() for u in used],
    }


def _strip_ids(s: str) -> str:
    return _ID_RE.sub("", s).strip()


def postprocess(parsed: dict | None, retrieved_ids: list[str]) -> dict:
    """Enforce cite-or-refuse. Returns {type, answer_hi, answer_en, used_ids}."""
    refuse = {"type": "refuse", "answer_hi": prompts.REFUSE_HI, "answer_en": prompts.REFUSE_EN, "used_ids": []}
    if not parsed:
        return refuse
    hi, en = _strip_ids(parsed["answer_hi"]), _strip_ids(parsed["answer_en"])
    typ = parsed["type"]
    if not hi:
        return refuse
    if typ == "answer":
        allowed = set(retrieved_ids)
        used = []
        for u in parsed["used_ids"]:
            if u in allowed and u not in used:
                used.append(u)
        if not used:
            return refuse  # an answer without a valid citation is not allowed
        return {"type": "answer", "answer_hi": hi, "answer_en": en or "(English gloss unavailable)", "used_ids": used}
    return {"type": typ, "answer_hi": hi, "answer_en": en or "(English gloss unavailable)", "used_ids": []}


class _Usage:
    def __init__(self):
        self.prompt = 0
        self.completion = 0

    def add(self, r: dict):
        self.prompt += r["usage"]["prompt_tokens"]
        self.completion += r["usage"]["completion_tokens"]


def _generate(messages, provider, usage: _Usage) -> dict | None:
    """One LLM call, one retry on invalid JSON. Provider errors propagate as AppError."""
    r = llm.complete(messages, provider=provider, max_tokens=LLM_MAX_TOKENS)
    usage.add(r)
    parsed = parse_llm_json(r["text"])
    if parsed is None:
        retry = messages + [{"role": "assistant", "content": r["text"] or "(empty)"},
                            {"role": "user", "content": prompts.RETRY_NOTE}]
        r = llm.complete(retry, provider=provider, max_tokens=LLM_MAX_TOKENS)
        usage.add(r)
        parsed = parse_llm_json(r["text"])
    return parsed


def _verify_supported(answer_en: str, cards: list[dict], provider, usage: _Usage) -> bool:
    """Second LLM pass (VERIFY=1). Fail-closed: unparsable verdict counts as unsupported."""
    r = llm.complete(prompts.build_verify_messages(answer_en, cards), provider=provider, max_tokens=300)
    usage.add(r)
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", r["text"].strip(), flags=re.I)
    try:
        return json.loads(t[t.find("{"): t.rfind("}") + 1]).get("supported") is True
    except ValueError:
        return False


def _lang_verify_ok(answer_target: str, answer_en: str, lang_code: str) -> tuple[bool, int]:
    """LANG_VERIFY=1 safety net for languages nobody here can read (see this agent's final
    report). Back-translates `answer_target` to English via Sarvam Translate and does a rough
    keyword-overlap check against `answer_en` (the model's own English gloss). This is a
    HEURISTIC, not a guarantee: it catches wildly different text, not a subtly wrong fact.
    Returns (ok, characters_translated). Fail-closed: any translate error counts as not ok."""
    try:
        back = sarvam.translate(answer_target, source_language_code=lang_code, target_language_code="en-IN")
    except AppError:
        return False, 0
    back_toks, en_toks = set(_tokens(back["translated_text"])), set(_tokens(answer_en))
    if not en_toks:
        return False, len(answer_target)
    overlap = len(back_toks & en_toks) / len(en_toks)
    return overlap >= LANG_VERIFY_OVERLAP_FLOOR, len(answer_target)


# ---------------------------------------------------------------- mock mode

def _mock_answer(text: str, retrieved: list[dict]) -> dict:
    low = text.lower()
    if "mock:clarify" in low:
        return {"type": "clarify", "answer_hi": prompts.MOCK_CLARIFY_HI, "answer_en": prompts.MOCK_CLARIFY_EN,
                "used_ids": []}
    toks = _expand(text)
    best, best_score = None, 0
    if "mock:refuse" not in low:
        for c in retrieved:
            s = _overlap(toks, c)
            if s > best_score:
                best, best_score = c, s
    if best is None:
        return {"type": "refuse", "answer_hi": prompts.REFUSE_HI, "answer_en": prompts.REFUSE_EN, "used_ids": []}
    return {"type": "answer", "answer_hi": f"{prompts.MOCK_INTRO_HI} {best['title_en']}।",
            "answer_en": f"{prompts.MOCK_INTRO_EN} {best['text_en']}", "used_ids": [best["id"]]}


# ---------------------------------------------------------------- main entry

def _estimate_audio_seconds(data: bytes) -> float:
    return sarvam.wav_seconds(data) or max(1.0, len(data) / 6000.0)  # ~48 kbps opus/webm


def _source(card: dict) -> dict:
    src = card.get("source") or {}
    return {"card_id": card["id"], "title": card.get("title_en", ""), "source_name": src.get("name", ""),
            "section": src.get("section", ""), "url": src.get("url") or ""}


def ask(session_id: str | None = None, text: str | None = None, audio: tuple | None = None,
        want_audio: bool = True, provider: str | None = None, retrieval: str | None = None,
        language: str | None = None) -> dict:
    """`audio` is (bytes, filename, content_type). Text wins if both are given.
    `language`: an app/backend/languages.py code, default "hi-IN" (languages.DEFAULT_LANGUAGE).
    Omitting it reproduces the original Hindi-only behaviour exactly: no extra translate calls,
    no extra response keys ("language"/"disclaimer_en"/"disclaimer_hi" only appear for other
    languages), same prompt. The JSON contract keeps the field name "answer_hi" for every
    language (see app/backend/prompts.py) instead of adding a new field, to avoid breaking any
    existing frontend/eval code that reads answer_hi; for language != "hi-IN" that field holds
    the answer in the REQUESTED language, not literally Hindi."""
    t_start = time.perf_counter()
    lat = {"stt": 0, "retrieve": 0, "llm": 0, "tts": 0, "total": 0}
    mock = config.mock_mode()
    provider = (provider or config.llm_provider()).lower()
    mode = (retrieval or config.retrieval_mode()).lower()
    lang_code = (language or languages.DEFAULT_LANGUAGE).strip()
    lang = languages.get(lang_code)
    if provider not in llm.PROVIDERS:
        raise AppError("bad_request", f"Unknown provider '{provider}'.")
    if mode not in ("topk", "all"):
        raise AppError("bad_request", f"Unknown retrieval mode '{mode}'.")
    if lang is None:
        raise AppError("bad_request", f"Unknown language '{lang_code}'.")
    text = (text or "").strip()
    if not text and not audio:
        raise AppError("bad_request", "Send either text or audio.")
    if len(text) > MAX_TEXT_CHARS:
        raise AppError("bad_request", f"Text is longer than {MAX_TEXT_CHARS} characters.")
    if audio and len(audio[0]) > config.MAX_AUDIO_BYTES:
        raise AppError("bad_request", "Audio file is larger than 5 MB.")

    sid = store.get_or_create(session_id)
    history = store.history(sid)
    stt_secs = 0.0

    # 1. STT
    if text:
        transcript = text
    else:
        t0 = time.perf_counter()
        if mock:
            transcript = prompts.MOCK_TRANSCRIPT
        else:
            transcript = sarvam.stt(*audio)["transcript"]
            stt_secs = _estimate_audio_seconds(audio[0])
        lat["stt"] = int((time.perf_counter() - t0) * 1000)
        if not transcript:
            raise AppError("no_speech")

    # 2. retrieval (retrieval.py / the keyword fallback are English-only and untouched: for any
    # language whose queries they cannot already read via the Hindi/Hinglish glossary, translate
    # the query to English first via Sarvam Translate, but keep `transcript`/`query` in the
    # original language for display, history and the LLM prompt).
    t0 = time.perf_counter()
    query = build_query(history, transcript)
    translate_chars = 0
    retrieval_query, translated_query = query, None
    if not mock and languages.needs_translation_for_retrieval(lang_code):
        try:
            out = sarvam.translate(query, source_language_code="auto", target_language_code="en-IN")
            if out["translated_text"]:
                retrieval_query = translated_query = out["translated_text"]
                translate_chars += len(query)
        except AppError as e:
            log.warning("Query translation failed (%s); retrieving on the original-language query", e)
    retrieved = retrieve(retrieval_query, mode)
    lat["retrieve"] = int((time.perf_counter() - t0) * 1000)
    retrieved_ids = [c["id"] for c in retrieved]
    cards_by_id = {c["id"]: c for c in retrieved}

    # 3. LLM + post-checks
    t0 = time.perf_counter()
    usage = _Usage()
    if mock:
        parsed = _mock_answer(transcript, retrieved)
    elif not retrieved:
        parsed = None  # nothing to ground on: refuse without spending an LLM call
    elif mode == "topk" and max(c.get("score", 1.0) for c in retrieved) < _min_score():
        parsed = None  # clearly off-topic: same, no LLM call
    else:
        msgs = prompts.build_messages(transcript, retrieved, history[-PROMPT_HISTORY_TURNS:], language=lang)
        parsed = _generate(msgs, provider, usage)
    result = postprocess(parsed, retrieved_ids)
    if result["type"] == "answer" and config.verify() and not mock:
        used_cards = [cards_by_id[i] for i in result["used_ids"]]
        if not _verify_supported(result["answer_en"], used_cards, provider, usage):
            result = postprocess(None, retrieved_ids)
    # Whether `result["answer_hi"]` is actually model-generated text in the target language
    # (an "answer", a "clarify" question, or even a "refuse" the model itself worded) versus the
    # fixed, already-verified REFUSE_HI/REFUSE_EN fallback (used when no card was retrieved, the
    # score was too low, or JSON parsing failed -- see postprocess()). Only the former needs the
    # disclaimer and the LANG_VERIFY safety net; the fixed fallback is Hindi/English, verified,
    # and showing it as-is (even when a non-Hindi language was requested) is the honest choice.
    is_generated_text = result["answer_hi"] != prompts.REFUSE_HI
    # Safety net for languages nobody here can read (LANG_VERIFY=1): back-translate and check
    # for rough agreement with the model's own English gloss; fail closed. Heuristic, not a
    # guarantee -- see this agent's final report and _lang_verify_ok's docstring.
    if is_generated_text and languages.needs_disclaimer(lang_code) and config.lang_verify() and not mock:
        ok, chars = _lang_verify_ok(result["answer_hi"], result["answer_en"], lang_code)
        translate_chars += chars
        if not ok:
            is_generated_text = False  # the fallback text below is fixed Hindi/English again
            result = {"type": "refuse", "answer_hi": prompts.LANG_VERIFY_FAIL_HI,
                      "answer_en": prompts.LANG_VERIFY_FAIL_EN, "used_ids": []}
    lat["llm"] = int((time.perf_counter() - t0) * 1000)

    # 4. TTS (failure degrades to text-only instead of failing the turn)
    audio_b64, tts_chars = None, 0
    if want_audio:
        t0 = time.perf_counter()
        try:
            spoken = sarvam.trim_for_tts(result["answer_hi"])
            if mock:
                wav = sarvam.silent_wav()
            elif lang_code == languages.DEFAULT_LANGUAGE:
                wav = sarvam.tts(spoken)  # unchanged call shape for the default language
            else:
                wav = sarvam.tts(spoken, language_code=lang["code"], speaker=lang["tts_speaker"])
            audio_b64 = base64.b64encode(wav).decode("ascii")
            tts_chars = 0 if mock else len(spoken)
        except AppError:
            audio_b64 = None
        lat["tts"] = int((time.perf_counter() - t0) * 1000)

    store.add_turn(sid, transcript, result["answer_hi"])
    lat["total"] = int((time.perf_counter() - t_start) * 1000)

    cost = stt_secs * STT_INR_PER_SEC + tts_chars * TTS_INR_PER_CHAR + translate_chars * TRANSLATE_INR_PER_CHAR
    if provider == "sarvam":  # gemini/groq free-tier prices are not modelled
        cost += usage.prompt * SARVAM_LLM_IN_PER_TOKEN + usage.completion * SARVAM_LLM_OUT_PER_TOKEN

    resp = {
        "session_id": sid,
        "transcript": transcript,
        "answer_hi": result["answer_hi"],
        "answer_en": result["answer_en"],
        "type": result["type"],
        "sources": [_source(cards_by_id[i]) for i in result["used_ids"]],
        "audio_b64": audio_b64,
        "audio_mime": "audio/wav",
        "latency_ms": lat,
        "cost_inr_est": round(cost, 4),
    }
    # Extra keys only ever appear for a non-default language, so existing callers that omit
    # `language` (the whole test suite, the current frontend, the current eval harness) see
    # exactly the same response shape as before.
    if lang_code != languages.DEFAULT_LANGUAGE:
        resp["language"] = lang_code
        if is_generated_text:
            resp["disclaimer_en"] = prompts.lang_disclaimer_en(lang)
            resp["disclaimer_hi"] = prompts.LANG_DISCLAIMER_HI
    if config.debug_responses():
        resp["debug"] = {"retrieved_ids": retrieved_ids, "used_ids": result["used_ids"], "provider": provider,
                         "rewritten_query": query if query != transcript else None,
                         "retriever": retriever_label(mode, retrieved),
                         "retrieval_scores": {c["id"]: c.get("score") for c in retrieved}}
        if lang_code != languages.DEFAULT_LANGUAGE:
            resp["debug"]["translated_query"] = translated_query
            resp["debug"]["language"] = lang_code
    return resp
