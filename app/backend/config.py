"""Settings. Reads R/.env quietly; nothing here ever prints a secret."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")  # does not override variables already in the environment

CARDS_PATH = ROOT / "app" / "data" / "cards" / "cards.json"
FIXTURE_CARDS_PATH = ROOT / "app" / "backend" / "tests" / "fixtures" / "cards_fixture.json"
FRONTEND_DIR = ROOT / "app" / "frontend"
TTS_CACHE_DIR = ROOT / "app" / "data" / "cache" / "tts"

SARVAM_BASE = "https://api.sarvam.ai"
MAX_AUDIO_BYTES = 5 * 1024 * 1024
MAX_AUDIO_SECONDS = 30
TTS_MAX_CHARS = 400

# Flags are read at call time so tests can monkeypatch the environment.


def _flag(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def mock_mode() -> bool:
    return _flag("MOCK_MODE")


def debug_responses() -> bool:
    return _flag("DEBUG_RESPONSES")


def tts_cache() -> bool:
    return _flag("TTS_CACHE")


def verify() -> bool:
    return _flag("VERIFY")


def lang_verify() -> bool:
    """LANG_VERIFY=1: back-translate non-Hindi/non-English answers and keyword-check them
    against answer_en before trusting them (see app/backend/pipeline.py _lang_verify_ok)."""
    return _flag("LANG_VERIFY")


def llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "sarvam").strip().lower() or "sarvam"


def retrieval_mode() -> str:
    m = os.getenv("RETRIEVAL_MODE", "topk").strip().lower()
    return m if m in ("topk", "all") else "topk"


def api_key(env_name: str) -> str | None:
    v = os.getenv(env_name, "").strip().strip('"').strip("'")
    return v or None
