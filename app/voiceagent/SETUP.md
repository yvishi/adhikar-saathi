# Adhikar Saathi -- Tier 1 voice agent (Sarvam Voice Agents / Samvaad)

Tier 1 = a real-time SPOKEN conversation with our own backend's cards,
citations and guardrails, reachable through a browser (Sarvam's dashboard
"test agent" mic, or the "Web" widget). **This is NOT a phone number** --
no telephony, no KYC, no number rental, no per-minute call spend was set up
or attempted here.

This folder (`app/voiceagent/`) does not touch `app/backend`, `app/frontend`
or `app/data`; the existing text/mic web app keeps working unchanged.

## What requires the owner to click inside indus.sarvam.ai (no way around this)
Sarvam's REST API (`docs.sarvam.ai/conversations/api/*`) only covers
**deployments** (turning an *already-built* agent into a live telephony
number/campaign), campaigns, instant-outbound (real phone calls),
analytics, boards and tests. There is no API to create or edit the agent
itself. So the following steps are manual, one-time, done in the dashboard:

1. Log into `indus.sarvam.ai`, open **Voice Agents**.
2. **Settings -> API Key**: generate a Voice-Agents API key. This looks like
   a *separate* key from the `SARVAM_API_KEY` already in `.env` (the intro
   docs show a different `X-API-Key` header on a different host,
   `apps.sarvam.ai/api/app-authoring`, vs. the core `api-subscription-key`
   on `api.sarvam.ai`) -- verify this live; do not assume the existing key
   works, and never paste either key into a file in this repo.
3. **Build -> Agents -> Create from Scratch** (skip Genie's auto-build so
   the prompt matches ours exactly).
4. On the **Canvas -> Instructions tab**: paste the **Greeting** from
   `app/voiceagent/greeting.txt` and the **Instructions** from
   `app/voiceagent/instructions.md`.
5. **Settings -> Speaking**: set starting language to Hindi (hi-IN).
6. **Tools -> Add Tool -> HTTPS Tool**: configure exactly as written in
   `app/voiceagent/tool_config.md` (name `ask_adhikar_saathi`, `POST
   {BASE_URL}/api/ask`, JSON body with `text`/`want_audio`/`session_id`,
   response template `{{answer_hi}}`). `{BASE_URL}` is the tunnel URL from
   step below -- **it changes every time the tunnel restarts, so you must
   re-paste it into this tool's URL field each session** (no way found
   around this without a paid/persistent tunnel or a fixed public host).
7. Commit the agent version.
8. **Test agent** (dashboard mic button) -- speak a question, e.g. "मेरी
   मजदूरी नहीं मिली, मैं क्या करूँ?" and confirm it answers using our
   card text and cites correctly, and that an off-topic question gets the
   safe refusal.

Steps 2-7 cannot be scripted or API'd around -- see the Findings section
below for exact citations.

## What the script does for you: the tunnel
Sarvam's cloud cannot reach `127.0.0.1:8000`. `scripts/tunnel.ps1` opens a
free Cloudflare "quick tunnel" (`cloudflared`) to the backend and prints
the public HTTPS URL to paste into step 6 above.

- `cloudflared` is **not on PATH by default** in this sandbox, but IS
  installable without admin rights: `winget install --id
  Cloudflare.cloudflared -e` (verified: this worked here, no elevation
  prompt, installed to `C:\Program Files (x86)\cloudflared\cloudflared.exe`
  and printed "Successfully installed"). The script auto-detects
  `cloudflared` on PATH first, then falls back to that known install path.
- Run `powershell -File scripts\tunnel.ps1` from the project root **after**
  the backend is already running (`scripts\run_demo.ps1`, per RUNBOOK). It
  does not start the backend itself.
- The free quick tunnel has no login and no uptime guarantee (Cloudflare's
  own warning banner says so) and gets a **new random URL every restart**
  (e.g. `https://incorporated-doubt-calculator-beginning.trycloudflare.com`
  in the live test below) -- update the HTTPS tool's URL in the dashboard
  each time you restart the tunnel.

## What was actually verified live (real, not simulated)
1. Installed `cloudflared` via `winget` (no admin needed) -- confirmed with
   `cloudflared --version` -> `2026.9.3`.
2. Found the real backend already running on `127.0.0.1:8000` (per
   RUNBOOK's "already running" assumption) -- did not start or stop it.
3. Ran `cloudflared tunnel --url http://127.0.0.1:8000`, got public URL
   `https://incorporated-doubt-calculator-beginning.trycloudflare.com`.
4. `curl https://.../api/health` through the tunnel -> `200 {"ok":true,...}`,
   proving external reachability.
5. `curl -X POST https://.../api/ask -F text="..." -F want_audio=false` twice
   through the tunnel:
   - A Hindi question sent from Git-Bash got mangled by shell encoding
     (`curl -F` on this shell does not preserve UTF-8 in a here-typed
     Devanagari argument) and scored 0 on retrieval, so it correctly
     **refused with zero cost** (`cost_inr_est: 0.0` -- the pipeline skips
     the LLM call below its retrieval-score floor).
   - An English question ("what is minimum wage") got a real `type:
     "answer"` with `sources: [{"card_id":"W-01", ...}]` and
     `cost_inr_est: 0.0586`.
   - Total live spend for this whole task: **Rs 0.0586**, well under the
     Rs 5 cap. Both calls used the tunnel URL end-to-end, proving the
     contract survives the tunnel unchanged.
6. Killed the `cloudflared` process afterward and confirmed the tunnel URL
   now 502s. Left the pre-existing backend on port 8000 untouched (it was
   not started by this task).

**Not done, and correctly not done**: no agent, deployment, session or test
call was created inside Sarvam's Voice Agents product itself, since its
per-minute/per-session pricing is not published anywhere in the docs
fetched (see Findings) and creating a live agent might not be free-tier.
Steps 1-8 above are therefore left for the owner.

## Findings: what is API-only vs. dashboard-only in Sarvam Voice Agents
(Read 2026-09-27 via `docs.sarvam.ai`; each point cites the exact page.)

**(a) Can an agent be created/configured purely via REST? No.** The full
page index (`conversations/llms.txt`) shows a REST layer
(`conversations/api/*`) covering only deployments, campaigns,
instant-outbound, analytics, boards, tests and BYOK -- there is no
create/update endpoint for the agent itself (no `api/apps` or
`api/agents`). `conversations/api/deployments/create.md`'s `POST
.../deployments` takes an existing `app_id` + `app_version`; it deploys an
already-built agent, it doesn't build one. `conversations/build/system-prompt.md`
says the greeting/instructions are "authored on the Canvas" (dashboard).
`conversations/build/tools/https-tool.md` says the HTTPS tool is configured
"through a dashboard UI form" (curl-paste auto-fills fields, but it's still
a dashboard action). `conversations/build/voice-language.md` says starting
language has "no API endpoint or programmatic equivalent."

**(b) Can a session be driven via API/SDK without the dashboard's test-agent
UI? Yes, but only after (a) is done once by hand.**
`conversations/deploy/deploy-with-code.md` documents `sarvam-conv-ai-sdk`
for Python (`AsyncSamvaadAgent`), Web/TS (`ConversationAgent` +
`BrowserAudioInterface`), React Native and Flutter -- all needing
`org_id`/`workspace_id`/`app_id` from a dashboard-created, committed agent,
plus a Voice-Agents API key from Settings -> API Key
(`conversations/settings/api-key.md`), which the intro API doc shows using
a different `X-API-Key` header on `apps.sarvam.ai` -- likely **not** the
same key/header as the core `api-subscription-key` already used for
STT/TTS/Chat. `conversations/deploy/overview.md` also documents a **Web**
channel: an embeddable call-or-chat widget needing "no phone number,"
matching this Tier-1 goal exactly.

**(c) What needs a human click in indus.sarvam.ai:** account/workspace
login and API-key generation; creating the agent (Canvas, no REST
equivalent); writing the Greeting/Instructions/HTTPS tool/starting
language (all dashboard forms); committing the agent version before the
SDK can drive it; the free "test agent" mic (fastest way to actually talk
to it); Monitor -> Agent Analytics.

**Telephony endpoints intentionally avoided:**
`conversations/api/instant-outbound/create.md` places a real outbound phone
call (`agent_phone_number` + `user_phone_number` required) -- out of scope
per the brief, not touched, not tested.

**Biggest open unknown:** no page fetched (introduction, overview,
quickstart, deploy/overview, settings/api-key) states a price, free-tier
limit, or per-minute rate for Voice Agents/Samvaad itself (as opposed to
the already-known STT/TTS/Chat per-unit prices in `CONTRACT.md` section 4,
which are unrelated products). Whether creating an agent, committing a
version, or a single test-agent conversation is free is unverified --
treat as "needs the owner to test, cost unknown" and check the dashboard's
credit balance before and after the first real test conversation.

## Known limitations of this Tier-1 setup
- Free quick-tunnel URL changes every restart -- re-paste into the
  dashboard tool config each session (no fixed hostname found without a
  paid Cloudflare tunnel or another always-on host).
- This only gives a **browser-based spoken conversation** via the
  dashboard's test-agent mic or the embeddable Web widget -- it is not a
  phone number and has no telephony, IVR, KYC or number-rental step
  anywhere in it.
- The exact "pass the caller's live utterance" variable name in the HTTPS
  tool's `@`-variable picker was not confirmed from the fetched docs (only
  User Identifier / Call Transcript / Interaction ID / Call Length were
  listed) -- see `tool_config.md`'s "Known gap" section for what to check
  live and the fallback if only "Call Transcript" is available.
- Whether the HTTPS tool can send `multipart/form-data` or
  `x-www-form-urlencoded` (which our `/api/ask` already accepts as-is) or
  only raw JSON (which needs the small backend addition specced in
  `backend_json_variant_spec.md`) was not confirmed from the fetched docs
  either -- try form-encoded first, it needs zero backend changes.

## Files in this folder
- `greeting.txt`, `instructions.md` -- paste-ready text for the dashboard.
- `tool_config.md` -- exact `ask_adhikar_saathi` HTTPS tool config + the two
  open questions to check live before it will really work.
- `backend_json_variant_spec.md` -- spec only (not implemented) for
  backend-core, needed only if the tool truly cannot send form-encoded data.
- `SETUP.md` -- this file.
Hindi strings introduced here are recorded in
`app/data/hindi_review/voiceagent.md` per the contract.
