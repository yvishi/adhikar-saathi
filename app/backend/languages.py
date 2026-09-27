"""Registry of answer languages beyond Hindi.

Hindi is the only language the owner (fluent in Hindi) has reviewed and approved
(see app/data/hindi_review/). Every other language here is a genuine but UNVERIFIED
capability: the model writes the answer directly in that language and Sarvam TTS
speaks it, but nobody on this team can check the output text itself. See
app/data/language_review/INDEX.md for exactly what is/isn't verified.

Why these languages: PLFS 2025 shows Punjab has the highest share of informal
workers of any Indian state (82%), so Punjabi is the first non-Hindi language.
Bengali and Marathi are added next: both are large migrant/unorganised-worker
languages (construction and domestic work) and both are fully supported end to
end (STT, Translate, TTS) so the same architecture covers them for free.

Verified against Sarvam's docs on 2026-09-27 (see CONTRACT.md section 4 for the
already-verified STT/TTS/chat facts; these are the language-coverage facts this
agent verified for this task):
  - https://docs.sarvam.ai/api/getting-started/models/bulbul.md
    Bulbul v3 TTS supports 11 language_codes (10 Indian + English): hi-IN, bn-IN,
    ta-IN, te-IN, gu-IN, kn-IN, ml-IN, mr-IN, pa-IN, od-IN, en-IN. "shubh" is
    documented as the default speaker, available across languages.
  - https://docs.sarvam.ai/api/getting-started/models/saaras.md
    Saaras STT (saaras:v3/v4) supports 23 languages including all of the above,
    so every Bulbul TTS language here also has STT coverage.
  - https://docs.sarvam.ai/api-reference/text/translate-text
    Sarvam Translate (model "mayura:v1") supports source_language_code:"auto"
    plus target_language_code for 23 languages, a superset of Bulbul's list.
    (The newer "sarvam-translate:v1" model does NOT support "auto" - only
    mayura:v1 does - so mayura:v1 is what this module uses for auto-detected
    query translation.)

Only languages Bulbul v3 actually speaks (real language_code + a real speaker)
are listed here; this list is deliberately short.
"""

DEFAULT_LANGUAGE = "hi-IN"

# TRANSLATE_MODEL is the model that supports source_language_code="auto" (see docstring above).
TRANSLATE_MODEL = "mayura:v1"

LANGUAGES = [
    {
        "code": "hi-IN",
        "name_en": "Hindi",
        "name_native": "हिन्दी",
        "script_en": "Devanagari",
        "tts_speaker": "shubh",
        "verified_by_owner": True,
    },
    {
        "code": "pa-IN",
        "name_en": "Punjabi",
        "name_native": "ਪੰਜਾਬੀ",
        "script_en": "Gurmukhi",
        "tts_speaker": "shubh",
        "verified_by_owner": False,
    },
    {
        "code": "bn-IN",
        "name_en": "Bengali",
        "name_native": "বাংলা",
        "script_en": "Bengali",
        "tts_speaker": "shubh",
        "verified_by_owner": False,
    },
    {
        "code": "mr-IN",
        "name_en": "Marathi",
        "name_native": "मराठी",
        "script_en": "Devanagari",
        "tts_speaker": "shubh",
        "verified_by_owner": False,
    },
]

BY_CODE = {lang["code"]: lang for lang in LANGUAGES}


def get(code: str | None) -> dict | None:
    """Registry entry for `code`, or None if not a supported answer language."""
    return BY_CODE.get((code or "").strip())


def is_supported(code: str | None) -> bool:
    return get(code) is not None


def needs_translation_for_retrieval(code: str | None) -> bool:
    """True for any answer language whose queries our English-glossary retriever
    cannot already handle (everything except Hindi/Hinglish and English)."""
    return (code or "").strip() not in ("hi-IN", "en-IN")


def needs_disclaimer(code: str | None) -> bool:
    """True for any answer language other than the two the owner has verified."""
    c = (code or "").strip()
    return c not in ("hi-IN", "en-IN")
