# Spec for backend-core: optional JSON body support on `/api/ask` (NOT implemented by voiceagent)

Only needed if `tool_config.md`'s "Known gap" #2 confirms Sarvam's HTTPS
tool cannot send `multipart/form-data` or
`application/x-www-form-urlencoded`, and can only send a raw JSON body.

This is a spec, not a diff I applied -- `app/backend/main.py` is
backend-core's file and I have not touched it.

## Minimal option (preferred): accept JSON on the *same* route
FastAPI can distinguish by `Content-Type` at the top of the existing
`ask()` handler in `app/backend/main.py`. Sketch:

```python
from fastapi import Request

@app.post("/api/ask")
async def ask(request: Request, session_id: str | None = Form(None), ...):
    if request.headers.get("content-type", "").startswith("application/json"):
        body = await request.json()
        return pipeline.ask(
            session_id=body.get("session_id"),
            text=body.get("text"),
            audio=None,
            want_audio=str(body.get("want_audio", "false")).strip().lower() not in ("false", "0", "no", "off"),
            provider=body.get("provider"),
            retrieval=body.get("retrieval"),
        )
    # ... existing multipart/form Form(...)/File(...) path unchanged below
```
The tricky part: FastAPI does not let a single function signature mix
`Form(...)` params with also reading a raw JSON body cleanly, so the real
implementation would likely need to split into two thin route functions
(one `@app.post("/api/ask")` for multipart as today, kept byte-for-byte
identical, and either (a) a second explicit route such as
`@app.post("/api/ask/json")` that both call a shared internal
`_ask_common(...)` helper, or (b) a single route typed to take
`Request` and branch on `content-type` as sketched above, calling
`pipeline.ask()` either way). Both are additive and do not change the
existing multipart contract at all -- existing frontend/eval callers are
unaffected.

## Fields
Same as the existing multipart contract (CONTRACT.md section 8), JSON body:
```json
{
  "session_id": "abc123",
  "text": "...",
  "want_audio": false,
  "provider": null,
  "retrieval": null
}
```
No `audio` field in the JSON variant (voice-agent audio never needs to go
through this path -- Sarvam's own STT/TTS handles the caller's actual
speech; only the text of what was said/decided needs to reach us).

## Response
Unchanged -- identical JSON shape as today's `/api/ask` success/error
responses.

## Decision needed from backend-core / owner
Whether to add this at all depends entirely on the "Known gap" #2 test in
`tool_config.md`. If the tool can already send `application/x-www-form-urlencoded`
with a `text` field, none of this is needed.
