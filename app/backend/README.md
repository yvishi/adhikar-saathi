# Backend (FastAPI)

Run everything from the project root (`F:\College\SEM5\BFWAI Hackathon`).

```
pip install -r app/backend/requirements.txt
uvicorn app.backend.main:app --reload            # real Sarvam calls, needs SARVAM_API_KEY in .env
MOCK_MODE=1 uvicorn app.backend.main:app --reload   # no network, canned answers, silent WAV
```
PowerShell: `$env:MOCK_MODE=1; uvicorn app.backend.main:app --reload`.
Open http://127.0.0.1:8000/ (frontend, served only if `app/frontend/index.html` exists when the server starts) or http://127.0.0.1:8000/api/docs.

## Flags (env or `.env`)
| Flag | Default | Meaning |
|---|---|---|
| `MOCK_MODE` | 0 | 1 = no network. Answers are canned but driven by real card retrieval. In text, `mock:clarify` forces a clarify reply and `mock:refuse` a refusal; audio uploads always transcribe to one fixed wage question. |
| `LLM_PROVIDER` | sarvam | `sarvam`, `gemini` or `groq` (`GEMINI_API_KEY` / `GROQ_API_KEY`; model override `GEMINI_MODEL` / `GROQ_MODEL`). Only sarvam is tested live. |
| `RETRIEVAL_MODE` | topk | `all` sends every non-skipped card to the LLM. |
| `DEBUG_RESPONSES` | 0 | 1 adds the `debug` object to `/api/ask`. |
| `TTS_CACHE` | 0 | 1 caches TTS audio under `app/data/cache/tts/`. |
| `VERIFY` | 0 | 1 adds a second LLM pass that must confirm the answer is supported by the cited cards (costs one more call; fails closed to a refusal). |

## Tests and live check
```
python -m pytest app/backend/tests -q               # offline; any network call fails the test
python -m app.backend.live_check                    # 3 real text turns, about Rs 0.07 (add --tts for one 30-char TTS)
```
Cards come from `app/data/cards/cards.json`; until it exists the backend uses `tests/fixtures/cards_fixture.json`.
The LLM helper for other code: `from app.backend.llm import complete` (`complete(messages, provider=None, max_tokens=500, temperature=0.2)`).
