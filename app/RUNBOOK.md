# Runbook: Adhikar Saathi

All commands run from the project root (`F:\College\SEM5\BFWAI Hackathon`). Python 3.12.

## 1. Setup on a fresh machine
1. `pip install -r app/backend/requirements.txt` (fastapi, uvicorn, python-multipart, requests, python-dotenv, pytest, httpx, fastembed, onnxruntime, numpy).
2. Retrieval model (about 241 MB, one time, needs internet): it must exist in `app/backend/retrieval_data/models/`. Copy the folder from the working machine, or run `python -m app.backend.retrieval --download-model`. Without it the server still starts but falls back to BM25 only; the server log then shows `Embedding model unavailable` and `debug.retriever` says `retriever:bm25`.
3. Put `SARVAM_API_KEY=...` in a file named `.env` in the project root. Never commit, paste or print it.
4. Optional for the UI check scripts only: `pip install playwright` (uses the installed Edge, no download).

## 2. Start
- Real: `powershell -File scripts\run_demo.ps1` then open http://127.0.0.1:8000/ . (Same as `uvicorn app.backend.main:app --port 8000` with `TTS_CACHE=1 DEBUG_RESPONSES=1`.)
- Mock (no network, no cost): `powershell -File scripts\run_demo.ps1 -Mock`. Answers are canned but chosen from the real cards; typing `mock:clarify` or `mock:refuse` forces those replies; audio is silence.
- Frontend-only mock (no server at all): open `app/frontend/index.html?mock=1` (or `/?mock=1` from the server). `&state=answer|clarify|refuse|schemes|complaint|error` jumps to a screen.
- Tick "Judge view" (bottom of the page) to see latency, cost and retrieved/used card ids.

## 3. Tests (offline, free)
`python -m pytest app -q` (any network call fails a test). Card check: `python app/data/cards/validate_cards.py`.

## 4. Evaluation (paid, text only, about Rs 0.05 per turn)
1. Start the real server (step 2) with `DEBUG_RESPONSES=1`.
2. `python app/eval/run_eval.py --mode both --base-url http://127.0.0.1:8000 --max-inr 7` (full 60 questions, both modes, cost Rs 5.1 in the integration run (two halves of Rs 2.85 and Rs 2.27); --max-inr 7 leaves headroom; `--ids Q002,Q004` for a subset; `--mode system` skips the baseline). Results go to `app/eval/results/<time>/`.
3. Free self-check of the harness: `python app/eval/run_eval.py --selftest`.
The questions and regexes are a DRAFT until the owner has reviewed the Hindi (`app/data/hindi_review/INDEX.md`).

## 5. Demo prewarm (paid, live)
`python scripts/prewarm_demo.py --list`, then `--only refuse,wages,pmsym --max-inr 3`. It runs the real pipeline in-process with `TTS_CACHE=1`, saving the spoken answers in `app/data/cache/tts/` (Rs 0.35 per refusal, about Rs 1.2 per answer). Cache key is the exact answer text and the LLM varies slightly between runs, so an answer can still be re-spoken (and re-paid). Refusals always hit the cache. The "clarify" demo question is not reliable (2 of 3 real runs): for a guaranteed clarify show the mock (`mock:clarify`).

## 6. If Sarvam is down or credits run out
- TTS fails: the API still returns 200 with `audio_b64: null`; the page shows the text answer and source card, no player. Nothing to do.
- STT fails or credits gone (errors such as `stt_failed`, `llm_failed`, `rate_limited`): the UI shows the error card; type the question instead (text needs only the LLM, about Rs 0.05).
- Everything down: start with `-Mock`. The judges then see the real UI, real cards and real source links, but canned answers and silent audio; say so.
- Cached audio only helps for answers already prewarmed with the same text (section 5).
- Other LLMs: `LLM_PROVIDER=gemini|groq` with the key in `.env` exist in code but were never run live.

## 7. Test the microphone on a phone
Browsers only allow the microphone on HTTPS or on `localhost`. Options (none is set up here): (a) run the server on the laptop and open it on the laptop with Chrome's device emulation for layout only; (b) put the server behind an HTTPS tunnel or an HTTPS host and open that URL on the phone; (c) with Android USB debugging, `chrome://inspect` port forwarding makes the phone's `localhost:8000` reach the laptop, which counts as a secure origin. Then: tap the mic, allow the permission, speak, tap again. If recording is not possible the page says so and the typed box still works. Recording format differs by phone (webm on Android Chrome, mp4 on iPhone Safari); iPhone has never been tried.
