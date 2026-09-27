# `ask_adhikar_saathi` HTTPS tool config (paste into Canvas -> Tools -> Add Tool -> HTTPS Tool)

Reference: https://docs.sarvam.ai/conversations/build/tools/https-tool.md

## Basic fields
- **Name**: `ask_adhikar_saathi`
- **Description** (shown to the agent so it knows when to call it): "Looks up
  a verified answer about Indian labour rights, wages, welfare schemes,
  maternity benefits or workplace harassment from our own backend. Always
  call this before answering any factual question in those areas."
- **Method**: `POST`
- **URL**: `{BASE_URL}/api/ask` where `{BASE_URL}` is the current public
  tunnel URL from `scripts/tunnel.ps1` (changes every restart -- see SETUP.md
  step about updating this).
- **Authentication**: None (our backend has no auth of its own; do not put
  the Sarvam API key here, it is irrelevant to our backend).

## Body (JSON)
The https-tool docs describe a generic "Body" payload editor with `@`
variable insertion and support for pasting a cURL command to auto-fill
method/URL/headers/body; the fetched docs did not show a raw content-type
selector, so treat the body editor as a **JSON** editor (send
`Content-Type: application/json`) unless the live UI shows an explicit
"form-data" option -- see "Known gap" below.

```json
{
  "text": "@<user utterance variable -- see Known gap>",
  "want_audio": "false",
  "session_id": "@Interaction ID"
}
```

## Response template
Docs say response fields are referenced with `{{fieldname}}` to map the
tool's JSON response back into things the agent can speak. Our `/api/ask`
response has `answer_hi` at the top level, so:

```
{{answer_hi}}
```

The agent should be told (in Instructions, already written in
`instructions.md`) to speak this verbatim, and separately to also make
`{{type}}` available so the "TOOL FAILURE" branch in the instructions can
check whether the call itself failed (non-200) vs. returned a normal
`refuse`/`clarify` (both of which already have a safe `answer_hi`).

## Known gap -- verify these two things live before relying on this
1. **Which call-context variable holds "what the caller just said".** The
   https-tool docs (as fetched) list four call-context variables: **User
   Identifier** (caller phone number), **Call Transcript** (full transcript
   so far), **Interaction ID**, and **Call Length**. No variable named
   "last user message" / "current utterance" was shown in what I could
   fetch (the docs page may have more that a text-extraction pass dropped).
   Before wiring this for real, open the tool's Body editor in the
   dashboard and check the `@` autocomplete list:
   - If a **last-user-message-style variable exists**, use it for `text`.
   - If only **Call Transcript** exists, use `@Call Transcript` for `text`
     instead. This sends the whole conversation so far rather than just the
     latest question; our backend's LLM step can usually still extract the
     live question from it, but this is a real behaviour change from a
     single-turn API call and should be tested with a multi-turn
     conversation before demoing.
2. **Whether the Body editor truly only sends JSON**, or has a
   form-urlencoded/multipart option. If it can send
   `application/x-www-form-urlencoded` with a `text` field, our existing
   `/api/ask` (which reads `Form(...)` fields) will accept it AS-IS with no
   backend change -- try this first since it needs zero backend-core work.
   Only fall back to the JSON-variant endpoint spec
   (`backend_json_variant_spec.md`) if the tool truly cannot send anything
   but a raw JSON body.

## Why not multipart directly
Our contract (`app/CONTRACT.md` section 8) has `/api/ask` read
`multipart/form-data` fields via FastAPI `Form(...)`/`File(...)`. A generic
webhook-style tool builder (curl-paste, JSON body editor) is unlikely to
build a real multipart body, and we are not sending an audio file from this
tool anyway (text-only), so JSON is the natural fit -- hence the
`backend_json_variant_spec.md` fallback.
