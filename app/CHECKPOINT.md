# Checkpoint — 2026-09-27

Work paused here by request, to resume after hackathon idea-deck selection. This is the single source of truth for "where things stand" — read this before doing anything else.

## What's done and verified
- **Idea deck submitted:** `Mythos_AdhikarSaathi_v3.pptx` (project root) — the one that was submitted. v1/v2 are superseded (v1 had an incorrect PMSBY claim; v2 fixed that but predates multilingual/voice-conversation wording).
- **Backend, frontend, corpus, retrieval, schemes/complaint, eval harness:** all built, wired together, and tested. `python -m pytest app -q` → **244 passed**, verified independently (not just trusting agent reports).
- **Corpus:** 18 English rights cards in `app/data/cards/cards.json`, each with a cited evidence quote, validated by `python app/data/cards/validate_cards.py`.
- **Real evaluation numbers exist** (small sample, 30 questions/half — see `app/eval/results/`): system beats a no-corpus baseline on citation validity (39/39 vs 0), out-of-scope refusal (10/10 vs 0/10), and required-fact accuracy, at ~Rs 0.05/turn.
- **GitHub:** pushed to **https://github.com/yvishi/adhikar-saathi** (private). `.env`, the 241MB retrieval model, and the TTS cache are gitignored — verified not leaked.
- **Multilingual (just added, untested by a human):** Hindi (owner-verified) plus Punjabi, Bengali, Marathi via translate-for-retrieval + same cards. See `app/data/language_review/INDEX.md`.
- **Voice-agent (Tier 1, scoped but not activated):** paste-ready config in `app/voiceagent/` for Sarvam's Voice Agents dashboard; a working tunnel script (`scripts/tunnel.ps1`) was live-verified once for Rs 0.06.

## NOT done — do these before demoing further
1. **Wire the language selector.** `app/backend/main.py`'s `/api/ask` handler needs `language: str | None = Form(None)` added and passed to `pipeline.ask(...)`, mirroring the existing `retrieval` field. Until then, the frontend's language dropdown is a harmless no-op (always answers in Hindi). ~2 lines, per the multilingual agent's report.
2. **Review the Hindi you haven't yet:** `app/data/hindi_review/multilingual.md` and `voiceagent.md` are new since your last pass. Check `INDEX.md` for the full list and priority order.
3. **No human has checked Punjabi, Bengali or Marathi output.** Don't present these as verified in a demo — say "architecture supports it, pending native-speaker review," per `app/data/language_review/INDEX.md`.
4. **The Sarvam Voice Agents dashboard setup was never actually done** — only scoped and the reachability tunnel tested. Files are ready in `app/voiceagent/`; the dashboard steps (create agent, paste instructions/greeting/tool config) still need you, logged in.
5. **Voice-Agent-specific pricing is unverified.** Check your Sarvam credit balance before/after your first test conversation there.
6. **Real phone microphone never tested** on an actual device (only headless-browser scripted checks).
7. **HTTPS hosting for the mic to work on a phone** is not set up (needs a tunnel or a real host).
8. One evaluation finding still open: an answer that cited real cards but stated something the cards don't support (Q016, PM-SYM/accident insurance) wasn't caught by the citation check. `VERIFY=1` (a second LLM pass) exists in the pipeline but was never turned on and tested for this.

## How to pick this back up
Read `app/RUNBOOK.md` for exact run commands (`scripts\run_demo.ps1`, mock mode, tests, eval, prewarm). Read `app/CONTRACT.md` for the full architecture and data provenance. Everything is committed to the GitHub repo above, so a fresh machine only needs the repo, `.env` with `SARVAM_API_KEY`, and the retrieval model (`python -m app.backend.retrieval --download-model`).
