# Language review index

Adhikar Saathi now writes answers in one of four languages (`app/backend/languages.py`).
This file says exactly what is verified and what is not, so nobody mistakes one for the other.

## What IS verified

- **Hindi (`hi-IN`)** — the owner (fluent in Hindi) has reviewed the fixed Hindi strings
  (`app/data/hindi_review/*.md`) and the model's Hindi answers on the eval set
  (`app/data/hindi_review/INDEX.md`). This is the only language whose output a human on this
  team has actually read and approved.
- **English (`answer_en`, always produced alongside every answer)** — English is not a separate
  selectable answer language, but the `answer_en` gloss that ships with every response in every
  language is meant to be checked by the owner/judges as a proxy for correctness, since it is in
  a language they read.

## What is NOT verified (Punjabi, Bengali, Marathi)

Nobody on this build team reads Punjabi, Bengali or Marathi. For these three:
- The model (sarvam-105b) generates the answer text directly in that language from the same
  English cards, under the same cite-or-refuse rules, in the same call that also produces
  `answer_en`. Nobody has read a native speaker's judgement on any of this output.
- The fixed strings this agent DID write in these languages: none. The only new strings are two
  Hindi lines and one Hindi UI label (`app/data/hindi_review/multilingual.md`) plus English text
  naming the language (`app/backend/prompts.py` `LANG_DISCLAIMER_EN_TMPL`) — English is safe to
  write because it is itself a verified language.
- Every answer in these languages carries a disclaimer (English, primary; Hindi, secondary) and,
  optionally, an automatic heuristic safety net (`LANG_VERIFY=1`, see
  `app/backend/pipeline.py _lang_verify_ok`) that can downgrade a suspicious answer to a refusal.
  Neither of these is a substitute for a native speaker's review.

### What a native speaker of each language would need to check

For **Punjabi (pa-IN)**, **Bengali (bn-IN)** and **Marathi (mr-IN)**, in order of priority:
1. **Meaning matches the English gloss.** Read `answer_hi` (which for these languages actually
   holds the answer in that language, not Hindi — see `app/backend/pipeline.py` docstring on
   `ask()`) side by side with `answer_en` from the same response and confirm they say the same
   thing, especially numbers, ages, amounts, deadlines and phone numbers (14434) which must
   match the card exactly.
2. **No invented facts.** The cite-or-refuse rule is enforced on `answer_en` (English) by the
   model and, when `VERIFY=1`, by a second English LLM pass — but nothing directly checks the
   target-language text for smuggled-in facts. A subtle mistranslation that adds a fact would
   not be caught mechanically.
3. **Register and clarity.** Is it actually simple spoken language a daily-wage worker would
   understand, or stiff/formal machine-translation-sounding text?
4. **Script and encoding.** Confirm the text renders in the correct script (Gurmukhi for
   Punjabi, Bengali script for Bengali, Devanagari for Marathi) and isn't mixed with stray
   Hindi/English fragments.
5. **TTS quality.** Listen to a `want_audio=true` response and confirm the Bulbul v3 "shubh"
   voice is intelligible and correctly pronounced in that language (only 1-2 samples were
   listen-tested by this agent, who cannot judge pronunciation quality in these languages).
6. **The two disclaimer lines and the refusal fallback** (`app/backend/prompts.py`
   `LANG_DISCLAIMER_HI`, `LANG_VERIFY_FAIL_HI`) are in HINDI, not the target language, on
   purpose (see `app/data/hindi_review/multilingual.md`) — nothing to check here in the target
   language itself, but confirm this doesn't read as confusing to a Punjabi/Bengali/Marathi
   speaker who does not read Hindi.

## Architecture note (why adding a language needed no new glossary)

Retrieval (`app/backend/retrieval.py`) is English-only and untouched. For Punjabi/Bengali/
Marathi queries, `app/backend/pipeline.py` calls Sarvam Translate (`mayura:v1`,
`source_language_code="auto"`) once to get an English version of the query, and retrieves on
that. The original-language transcript is kept for display and for the LLM prompt. This means
the existing Hindi/Hinglish keyword glossary in `retrieval.py` was never touched or duplicated.

## Honest residual risk

A confidently wrong answer in Punjabi, Bengali or Marathi could reach a real worker and nobody
on this team would notice, because nobody here can read the output. The `LANG_VERIFY=1` back-
translation check is a heuristic (rough keyword overlap against `answer_en`) that catches wildly
off-topic drift, not a subtly wrong number or a mistranslated condition. Treat every non-Hindi,
non-English answer as unverified until a real speaker of that language has checked it against
this list.
