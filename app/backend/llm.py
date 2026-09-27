"""LLM provider registry. Stable public API (the eval harness imports it):

    complete(messages, provider=None, max_tokens=500, temperature=0.2)
        -> {"text": str, "usage": {"prompt_tokens": int, "completion_tokens": int}, "provider": str}

Only `sarvam` has been tested live. `gemini` and `groq` use their OpenAI-compatible endpoints
(base URLs from the providers' docs, 2026-09-27) and are UNTESTED live (no keys yet).
Model ids can be overridden with GEMINI_MODEL / GROQ_MODEL / SARVAM_MODEL.
"""
import os
import re

import requests

from . import config
from .errors import AppError
from .sarvam import raise_for_status

PROVIDERS = {
    "sarvam": {
        "url": f"{config.SARVAM_BASE}/v1/chat/completions",
        "model": "sarvam-105b",
        "model_env": "SARVAM_MODEL",
        "key_env": "SARVAM_API_KEY",
        "auth": "api-subscription-key",
        "extra": {"reasoning_effort": None},  # thinking is ON by default and billed as output
    },
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "model": "gemini-3.6-flash",
        "model_env": "GEMINI_MODEL",
        "key_env": "GEMINI_API_KEY",
        "auth": "bearer",
        "extra": {},
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "model_env": "GROQ_MODEL",
        "key_env": "GROQ_API_KEY",
        "auth": "bearer",
        "extra": {},
    },
}


def available_providers() -> dict:
    mock = config.mock_mode()
    return {name: bool(mock or config.api_key(p["key_env"])) for name, p in PROVIDERS.items()}


def _clean(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()


def complete(messages: list[dict], provider: str | None = None, max_tokens: int = 500,
             temperature: float = 0.2) -> dict:
    name = (provider or config.llm_provider()).lower()
    if name not in PROVIDERS:
        raise AppError("bad_request", f"Unknown provider '{name}'. Use one of: {', '.join(PROVIDERS)}.")
    if config.mock_mode():
        return {"text": "[mock llm]", "usage": {"prompt_tokens": 0, "completion_tokens": 0}, "provider": name}
    p = PROVIDERS[name]
    key = config.api_key(p["key_env"])
    if not key:
        raise AppError("bad_request", f"Provider '{name}' is not configured (missing {p['key_env']}).")
    headers = {"Content-Type": "application/json"}
    if p["auth"] == "bearer":
        headers["Authorization"] = f"Bearer {key}"
    else:
        headers[p["auth"]] = key
    body = {
        "model": os.getenv(p["model_env"], "").strip() or p["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **p["extra"],
    }
    try:
        r = requests.post(p["url"], headers=headers, json=body, timeout=90)
    except requests.RequestException:
        raise AppError("llm_failed", f"Could not reach the {name} answer service.")
    raise_for_status(r, "llm")
    try:
        j = r.json()
        text = _clean(j["choices"][0]["message"].get("content") or "")
    except Exception:
        raise AppError("llm_failed", f"Unexpected response from {name}.")
    u = j.get("usage") or {}
    return {
        "text": text,
        "usage": {"prompt_tokens": int(u.get("prompt_tokens") or 0),
                  "completion_tokens": int(u.get("completion_tokens") or 0)},
        "provider": name,
    }
