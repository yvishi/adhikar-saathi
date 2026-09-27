# Adhikar Saathi: build contract (read fully before you write any code)

Project root `R` = `F:\College\SEM5\BFWAI Hackathon`. Everything below is relative to `R`. Python 3.12 on Windows. Use the Bash tool (POSIX syntax) or PowerShell. Solo builder (Yash); you are one of several agents working IN PARALLEL on separate folders.

## 1. What we are building
**Adhikar Saathi** is a turn-based Hindi voice assistant (mobile-first website) that tells daily-wage, construction and domestic workers in India their legal rights and which welfare schemes they qualify for. Flow per turn: mic audio -> Sarvam speech-to-text -> retrieve verified "rights cards" -> LLM writes a short spoken-Hindi answer using ONLY those cards and must cite them, or refuses -> Sarvam text-to-speech -> user hears the answer and sees the source card plus an English transcript (so non-Hindi judges can verify).
Hackathon: BFWAI "AI Build Challenge 2026", PS-06 (AI for Bharat in Indian Languages). Final submission 1 Oct 2026 11:59 PM IST. No model training: pretrained models + our own corpus, retrieval, guardrails, rules engine and evaluation. No telephony/IVR in this scope (a separate person is exploring the phone-call idea).

## 2. Ground rules (non-negotiable)
1. **Secrets.** `R\.env` holds `SARVAM_API_KEY` (and later maybe `GEMINI_API_KEY`, `GROQ_API_KEY`). NEVER open, read, print, log, echo or paste `.env` or any key. Code may load it (python-dotenv or manual parse) but must never print it, put it in URLs, tests, fixtures, docs or error messages. Do not use the Read tool on `.env`.
2. **Money.** Sarvam has about Rs 99 of free credit left; Rs 3 per 1,000 TTS characters is the main cost (one full voice turn is about Rs 0.75-1.0; text-only chat about Rs 0.05). Unless your brief says otherwise you make ZERO live paid calls: use mocks/fixtures. Anyone allowed live calls has a hard cap stated in their brief, must count spend, and must default dev/test paths to text-only.
3. **Hindi.** The owner reads Hindi, you might not write it reliably. Keep any Hindi you author minimal and simple, and record EVERY Hindi string you write in `app/data/hindi_review/<your-agent-name>.md` (one line each: where it is used + the string) so the owner can verify it. Never present unreviewed Hindi as final.
3b. **Honesty.** Only state legal/scheme facts that appear in section 5 (verified) or that you verify yourself in `app/data/sources/`. If you cannot verify something, leave it out and list it as a gap. Never invent section numbers, amounts, ages or URLs.
4. **Ownership.** Only write inside the folders/files your brief assigns you. Read anything. If you need a change in someone else's area, do not edit it: describe it in your final report.
5. **Simplicity.** No speculative features, no frameworks beyond what the brief names, short comments only where the WHY is non-obvious. No git operations (this is not a git repo).
6. **Final report** (your last message, under 300 words): files created, how to run/test, test results (paste the real pass/fail line), deviations from this contract, open issues, extra pip packages needed. Do not claim something works unless you ran it.

## 3. Layout and owners
```
app/CONTRACT.md                     (this file, read-only for everyone)
app/backend/                        backend-core agent, except the files listed next
app/backend/retrieval.py            retrieval agent (also app/backend/tests/test_retrieval.py, app/backend/retrieval_data/)
app/backend/schemes.py, complaint.py, tests/test_schemes.py, tests/test_complaint.py   schemes agent
app/frontend/                       frontend agent (index.html, style.css, app.js, assets)
app/data/cards/cards.json           corpus agent (also app/data/cards/README.md, GAPS.md)
app/data/sources/                   verified source documents (read-only, already copied)
app/data/hindi_review/<agent>.md    each agent's own Hindi-to-verify list
app/eval/                           eval agent (questions.jsonl, run_eval.py, README.md)
scripts/smoke_test.py               reference implementation of the Sarvam calls (read-only)
```
`app/backend/requirements.txt` is owned by backend-core; everyone else reports their extra packages in their final report.

## 4. Sarvam facts (verified against docs.sarvam.ai on 2026-09-27; smoke test passed)
Base `https://api.sarvam.ai`. Auth header `api-subscription-key: <key>`. Auth failures are HTTP 403 (not 401); 429 = rate limit.
- **STT**: `POST /speech-to-text` multipart: `file`, `model=saaras:v3`, `mode=transcribe` (`codemix` also exists). Response JSON has `transcript`, `language_code`. REST max 30 s audio. Accepts wav, mp3, aac, ogg/opus, flac, mp4/m4a, webm, amr. Docs mention `saaras:v4` in one place but v3 is what the overview recommends and what worked.
- **TTS**: `POST /text-to-speech` JSON `{text, language_code:"hi-IN", model:"bulbul:v3", speaker:"shubh"}`; response `{audios:[base64...]}`; join the list, base64-decode -> WAV. Max 2,500 chars per request; we cap answers at about 400 chars.
- **Chat**: `POST /v1/chat/completions` JSON OpenAI-style, `model:"sarvam-105b"`. Thinking is ON by default: pass `"reasoning_effort": null` (reasoning tokens are billed as output). Use `temperature` about 0.2, `max_tokens` about 500. ~0.7 s latency in the smoke test. Response `choices[0].message.content`, `usage.prompt_tokens/completion_tokens`.
- **Prices**: STT Rs 30/hour; TTS Rs 3/1,000 chars; sarvam-105b Rs 29.28 in / Rs 73.20 out per 1M tokens.
- Read `scripts/smoke_test.py` for working code. Known flaws of the first prompt (fix them): it cited an irrelevant card on a refusal; it tied helpline 14434 to filing wage claims (14434 is the e-Shram helpdesk only); it cited only one card although it used two.

## 5. Verified facts you may use (with where they came from)
- **Code on Wages, 2019** (Act 29 of 2019) is in force from 21 Nov 2025 and replaces the Minimum Wages Act 1948, Payment of Wages Act 1936, Payment of Bonus Act 1965 and Equal Remuneration Act 1976. Sources: `wages_code_labourgov.pdf` (official gazette, English body; the page headers are in a legacy Hindi font that extracts as gibberish, ignore that), `labour_codes_pib.pdf` (PIB explainer 23 Nov 2025). `wages_code_prs.pdf` is the bill AS INTRODUCED (section numbers may differ from the enacted Act): use only for reference, cite the gazette.
  - Section 5: no employer shall pay any employee less than the minimum rate of wages notified by the appropriate Government. PIB: applies to every employee in organised and unorganised sectors.
  - Section 17: wages paid on daily basis at the end of the shift; weekly on the last working day before the weekly holiday; fortnightly before the end of the second day after the fortnight; monthly before the seventh day of the following month (READ the gazette to confirm exact text before you use it).
  - A claim application to the authority may be filed within three years from the date the claim arises; the authority may accept a later one on sufficient cause (gazette text; find the section number yourself).
  - Section 9 read with Rule 11: floor wage (PIB).
- **Code on Social Security, 2020** provides social security to all unorganised workers including domestic workers (PIB note 20 Mar 2023, `labour_gov_doc.pdf`). `prs_socsec.html` is a PRS summary.
- **e-Shram** (`eshram_intro.pdf`, `eshram_faq.html`): registration is free; workers pay no one; CORRECTED 2026-09-27: the "Rs 2 lakh accident cover under PMSBY" claim is NOT reliable (only the older eshram_intro.pdf says it; the live FAQ Q42 says "Right now, only registration is being done through e-Shram" and its PMSBY answers are commented out of the page): never state it as a current benefit, say "confirm with the helpline"; helpdesk 14434 / 1800-8896811 with Hindi, English, Tamil, Bengali, Kannada, Malayalam, Marathi, Odia, Telugu, Assamese support; grievance portal `www.gms.eshram.gov.in`. CONFLICT: the PDF says helpdesk hours Mon-Sat 8am-8pm while the live site header says 9am-6pm daily including Sundays; use the live-site wording and flag the conflict. 30.58 crore registered (Tribune, Feb 2025) is for the deck, not for cards.
- **PM-SYM** (`pmsym.html`): unorganised workers, entry age 18-40, monthly income up to Rs 15,000, assured pension Rs 3,000/month at age 60, voluntary and contributory, government matches the contribution. Contribution chart amounts are NOT verified: do not state them.
- **Maternity Benefit Act 1961** (`wb_maternity.pdf`, a West Bengal government copy): read it yourself; the 2017 amendment and applicability (establishments with 10+ persons; 80 days worked in the 12 months before delivery) are NOT yet verified against this file. Coverage for unorganised workers is limited.
- **Domestic workers**: no dedicated central law. Supreme Court order of 29 Jan 2025 asked the Union to consider a law and set up an expert committee (`p_livelaw_sc.html`); the committee's July 2025 report said a separate law is not needed (`p_dte.html`). Domestic workers are covered only through general codes and state policies.
- **POSH Act 2013**: the only local copy is `posh_ilo_hindi.pdf` and its Hindi text is in a legacy font (unreadable). The English text could not be fetched (nabard.org returned 403, cltri.gov.in refused). Treat POSH details as UNVERIFIED unless you can fetch a reliable English official source yourself.
- **UNVERIFIED / GAPS**: BOCW Act 1996 benefits and registration (no primary source downloaded), state-wise minimum wage rates (notified separately, revised twice a year; no official file obtained), e-Shram age band 16-59 and exclusion rules (only seen in a search snippet, verify in `eshram_faq.html`), Maternity amendment details, POSH details, any "Rs 1,500 BOCW pension"-type numbers.

## 6. Card schema (`app/data/cards/cards.json` = JSON array of these)
```json
{
  "id": "W-01",
  "topic": "wages|schemes|maternity|harassment|helpline|domestic|meta",
  "title_en": "Minimum wage is a legal right",
  "text_en": "Two to four plain sentences a worker can act on. Facts only from verified sources.",
  "text_hi": null,
  "keywords_en": ["minimum wage", "daily wage"],
  "keywords_hi": [],
  "source": {"name": "Code on Wages, 2019", "section": "s.5", "url": "https://...", "file": "app/data/sources/wages_code_labourgov.pdf"},
  "verified": true,
  "status": "ready|draft|skipped",
  "notes": "why skipped / what to double-check"
}
```
`text_hi` and `keywords_hi` stay null/empty unless the owner fills them (English cards are the source of truth; the LLM writes the Hindi answer from English cards; the owner reviews the Hindi output on the eval set).
**Planned card ids** (corpus agent may mark any `skipped` with a reason, and may add ids only with prefix `X-`): W-01 minimum wage right (s.5) · W-02 when wages must be paid (s.17) · W-03 claim unpaid wages within 3 years · W-04 deductions from wages · W-05 no gender discrimination in pay · W-06 overtime · W-07 minimum wage covers daily wagers/unorganised (PIB) · S-01 e-Shram registration and benefits · S-02 PM-SYM pension · S-03 PMSBY accident cover via e-Shram · S-04 Code on Social Security covers unorganised and domestic workers · S-05 BOCW registration and benefits · M-01 Maternity Benefit Act basics · H-01 sexual harassment at work: how to complain · X-01 helpline 14434 (e-Shram helpdesk only: what it is and is not) · X-02 what this assistant cannot do (not legal advice; refer out) · D-01 domestic workers: no dedicated central law, what applies · D-02 domestic workers: coverage under the Code on Social Security.

## 7. Retriever interface (retrieval agent implements, backend-core consumes)
```python
# app/backend/retrieval.py
class Retriever:
    def __init__(self, cards_path: str = "app/data/cards/cards.json"): ...
    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        """Return up to k cards (full card dicts, only status != 'skipped'), best first, each with an added float key 'score'. Query may be Hindi, Hinglish or English; cards are English. Must not make paid API calls at query time unless explicitly a documented option."""
```
Also `retrieve_all()` returning every non-skipped card (the backend can send all cards when there are only about 20).

## 8. HTTP API contract (backend-core implements; frontend and eval consume)
Server: FastAPI (`uvicorn app.backend.main:app` run from `R`). Serves the frontend folder at `/` (static, `index.html`). All paths under `/api`.
- `GET /api/health` -> `{"ok": true, "providers": {"sarvam": true, "gemini": false, "groq": false}, "cards": 18, "mock": false}`
- `POST /api/ask` multipart/form-data. Fields (all optional except one of text/audio): `session_id` (str), `text` (str), `audio` (file: webm/ogg/mp4/wav/mp3, <=30 s), `want_audio` ("true"/"false", default "true"), `provider` ("sarvam"|"gemini"|"groq", default from env `LLM_PROVIDER`, default sarvam), `retrieval` ("topk"|"all", default from env `RETRIEVAL_MODE`, default topk).
  Success 200:
  ```json
  {
    "session_id": "abc123",
    "transcript": "what the user said (STT result, or echo of text)",
    "answer_hi": "short spoken-Hindi answer, no citation ids inside the text",
    "answer_en": "English gloss of the answer for verification",
    "type": "answer|clarify|refuse",
    "sources": [{"card_id": "W-01", "title": "Minimum wage is a legal right", "source_name": "Code on Wages, 2019", "section": "s.5", "url": "https://..."}],
    "audio_b64": "base64 WAV or null",
    "audio_mime": "audio/wav",
    "latency_ms": {"stt": 0, "retrieve": 0, "llm": 0, "tts": 0, "total": 0},
    "cost_inr_est": 0.0,
    "debug": {"retrieved_ids": ["W-01"], "used_ids": ["W-01"], "provider": "sarvam", "rewritten_query": null}
  }
  ```
  Rules: `type=refuse` and `type=clarify` have `sources: []`. `used_ids` must be a subset of `retrieved_ids`. `debug` present only when env `DEBUG_RESPONSES=1`.
  Errors: non-200 with `{"error": {"code": "stt_failed|llm_failed|tts_failed|bad_request|rate_limited|audio_too_long|no_speech", "message_hi": "...", "message_en": "..."}}`.
- `POST /api/schemes` JSON `{"age": 34, "monthly_income_inr": 12000, "occupation": "daily_wage|construction|domestic|other", "is_epfo_esic_member": false, "is_income_tax_payer": false, "gender": "female|male|other", "is_pregnant": false}` (every field optional) -> `{"matches": [{"scheme": "e-Shram", "eligible": true, "why_en": "...", "why_hi": null, "card_id": "S-01", "missing_info": []}]}` where `eligible` is `true|false|"unknown"`.
- `POST /api/complaint-draft` JSON `{"worker_name": "", "state": "", "employer_name": "", "work_type": "", "wage_owed_inr": 0, "period_from": "", "period_to": "", "details": ""}` -> `{"draft_en": "...", "draft_hi": "...", "notes_en": ["what the worker must check and fill before using"], "requires_human_review": true}`. A worker must review and approve; the API never sends or files anything.
- `GET /api/sample-audio` is NOT part of the contract.
Environment flags read by the backend: `MOCK_MODE=1` (no network: canned deterministic answers, fake WAV), `LLM_PROVIDER`, `RETRIEVAL_MODE`, `DEBUG_RESPONSES`, `TTS_CACHE=1` (cache TTS audio by text hash in `app/data/cache/tts/`).

## 9. Product rules the whole app follows
Cite-or-refuse: answers use only retrieved cards; no card supports it -> refuse in simple Hindi and point to helpline 14434 (the e-Shram helpdesk) for anything it can help with, never claiming 14434 handles wage claims. Ask ONE short clarifying question when a needed fact is missing. Never ask for or store names, Aadhaar or phone numbers in normal Q&A. Always show: "This is information, not legal advice." Privacy notice: questions are processed by Sarvam AI (and any other configured provider). Short spoken-style Hindi, at most 4 sentences.
