"""Sarvam speech-to-text and text-to-speech (request shapes from CONTRACT section 4)."""
import base64
import hashlib
import io
import wave

import requests

from . import config
from .errors import AppError, AUDIO_UNREADABLE_EN, AUDIO_UNREADABLE_HI

_LONG_HINTS = ("duration", "too long", "30 sec", "exceed", "maximum")


def _headers() -> dict:
    key = config.api_key("SARVAM_API_KEY")
    if not key:
        raise AppError("bad_request", "SARVAM_API_KEY is not configured on the server.")
    return {"api-subscription-key": key}


def raise_for_status(resp, stage: str) -> None:
    """Map an HTTP error to an AppError. Never puts the response body in the message."""
    code = resp.status_code
    if code == 200:
        return
    # "translate" reuses llm_failed: there is no dedicated error code for it (errors.py is
    # not owned by this agent) and a failed translation is, like a failed LLM call, "the
    # answer service failed" from the user's point of view.
    failed = {"stt": "stt_failed", "llm": "llm_failed", "tts": "tts_failed", "translate": "llm_failed"}[stage]
    if code == 429:
        raise AppError("rate_limited")
    if code in (401, 403):
        raise AppError(failed, f"{stage.upper()} rejected the server's credentials (HTTP {code}).")
    if code == 400 and stage == "stt":
        body = (resp.text or "").lower()
        if any(h in body for h in _LONG_HINTS):
            raise AppError("audio_too_long")
        raise AppError("bad_request", AUDIO_UNREADABLE_EN, AUDIO_UNREADABLE_HI)
    raise AppError(failed, f"{stage.upper()} request failed (HTTP {code}).")


def wav_seconds(data: bytes) -> float | None:
    """Duration if `data` is a readable WAV, else None."""
    try:
        with wave.open(io.BytesIO(data)) as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def stt(audio_bytes: bytes, filename: str = "audio.webm", content_type: str = "audio/webm") -> dict:
    """Returns {"transcript": str, "language_code": str|None}."""
    secs = wav_seconds(audio_bytes)
    if secs is not None and secs > config.MAX_AUDIO_SECONDS:
        raise AppError("audio_too_long")
    ctype = (content_type or "audio/webm").split(";")[0].strip() or "audio/webm"
    try:
        r = requests.post(
            f"{config.SARVAM_BASE}/speech-to-text",
            headers=_headers(),
            files={"file": (filename or "audio.webm", audio_bytes, ctype)},
            data={"model": "saaras:v3", "mode": "transcribe"},
            timeout=60,
        )
    except requests.RequestException:
        raise AppError("stt_failed", "Could not reach the speech service.")
    raise_for_status(r, "stt")
    j = r.json()
    return {"transcript": (j.get("transcript") or "").strip(), "language_code": j.get("language_code")}


def trim_for_tts(text: str, limit: int = config.TTS_MAX_CHARS) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    m = max(cut.rfind("।"), cut.rfind("."), cut.rfind("?"), cut.rfind("!"))
    return cut[: m + 1] if m >= limit // 2 else cut


def tts(text: str, language_code: str = "hi-IN", speaker: str = "shubh") -> bytes:
    """Returns WAV bytes. Caches on disk by sha256 when TTS_CACHE=1.
    `language_code`/`speaker` default to the original Hindi voice, so existing
    callers are unaffected; other languages pass their app/backend/languages.py entry."""
    text = trim_for_tts(text)
    if not text:
        raise AppError("tts_failed", "Nothing to speak.")
    path = None
    if config.tts_cache():
        digest = hashlib.sha256(f"bulbul:v3|{speaker}|{language_code}|{text}".encode("utf-8")).hexdigest()
        path = config.TTS_CACHE_DIR / f"{digest}.wav"
        if path.exists():
            return path.read_bytes()
    try:
        r = requests.post(
            f"{config.SARVAM_BASE}/text-to-speech",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"text": text, "language_code": language_code, "model": "bulbul:v3", "speaker": speaker},
            timeout=60,
        )
    except requests.RequestException:
        raise AppError("tts_failed", "Could not reach the speech service.")
    raise_for_status(r, "tts")
    try:
        audio = base64.b64decode("".join(r.json()["audios"]))
    except Exception:
        raise AppError("tts_failed", "Unexpected TTS response.")
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(audio)
    return audio


def translate(text: str, source_language_code: str = "auto", target_language_code: str = "en-IN") -> dict:
    """POST /translate (Mayura). Returns {"translated_text": str, "source_language_code": str}.
    Only "mayura:v1" supports source_language_code="auto" (verified 2026-09-27, see languages.py).
    Max 1000 input characters for mayura:v1; callers keep queries/answers well under that."""
    text = (text or "").strip()
    if not text:
        return {"translated_text": "", "source_language_code": source_language_code}
    try:
        r = requests.post(
            f"{config.SARVAM_BASE}/translate",
            headers={**_headers(), "Content-Type": "application/json"},
            json={
                "input": text[:1000],
                "source_language_code": source_language_code,
                "target_language_code": target_language_code,
                "model": "mayura:v1",
            },
            timeout=30,
        )
    except requests.RequestException:
        raise AppError("llm_failed", "Could not reach the translation service.")
    raise_for_status(r, "translate")
    try:
        j = r.json()
        return {"translated_text": (j.get("translated_text") or "").strip(),
                "source_language_code": j.get("source_language_code") or source_language_code}
    except Exception:
        raise AppError("llm_failed", "Unexpected response from the translation service.")


def silent_wav(seconds: float = 1.0, rate: int = 16000) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00\x00" * int(rate * seconds))
    return buf.getvalue()

