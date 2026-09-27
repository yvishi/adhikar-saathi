"""Sarvam pipeline smoke test: TTS -> STT -> grounded chat -> TTS. Costs roughly Rs 1-2."""
import base64
import difflib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "smoke_out"
OUT.mkdir(exist_ok=True)
BASE = "https://api.sarvam.ai"


def load_key():
    env = ROOT / ".env"
    if not env.exists():
        sys.exit(f"No .env found at {env}")
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("SARVAM_API_KEY"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("SARVAM_API_KEY not found in .env")


KEY = load_key()
H = {"api-subscription-key": KEY}
spent = {"stt_s": 0.0, "tts_chars": 0, "in_tok": 0, "out_tok": 0}


def tts(text, name):
    r = requests.post(f"{BASE}/text-to-speech", headers={**H, "Content-Type": "application/json"},
                      json={"text": text, "language_code": "hi-IN", "model": "bulbul:v3", "speaker": "shubh"}, timeout=60)
    if r.status_code != 200:
        sys.exit(f"TTS failed {r.status_code}: {r.text[:300]}")
    audio = base64.b64decode("".join(r.json()["audios"]))
    (OUT / name).write_bytes(audio)
    spent["tts_chars"] += len(text)
    return audio


def stt(audio, secs_estimate):
    files = {"file": ("q.wav", audio, "audio/wav")}
    data = {"model": "saaras:v3", "mode": "transcribe"}
    r = requests.post(f"{BASE}/speech-to-text", headers=H, files=files, data=data, timeout=60)
    if r.status_code != 200:
        sys.exit(f"STT failed {r.status_code}: {r.text[:300]}")
    spent["stt_s"] += secs_estimate
    return r.json()


SYSTEM = """You are Adhikar Saathi, a voice assistant that explains labour rights to daily-wage workers in India.
Rules:
1. Answer ONLY from the CARDS below. Never use outside knowledge about law.
2. Reply in simple spoken Hindi (Devanagari), at most 4 short sentences, no legal jargon.
3. End every answer with the card id you used, like [C1].
4. If no card answers the question, say in Hindi that you do not know and tell the person to call helpline 14434. Do not guess.
5. If you need a fact from the user first (for example how many days wages are unpaid), ask ONE short question instead of answering."""

CARDS = """CARDS
[C1] Code on Wages, 2019, section 5: No employer may pay any employee less than the minimum rate of wages notified by the government. This applies to organised and unorganised workers alike.
[C2] Code on Wages, 2019, section 17: Wages must be paid at the end of the shift for daily-wage work, on the last working day of the week for weekly work, and within the time set for fortnightly or monthly work.
[C3] Code on Wages, 2019: A worker can apply to the wage-claims authority for unpaid or under-paid wages within three years from the date the claim arises; later applications are allowed only with sufficient cause.
[C4] e-Shram: registration is free of cost. Registered unorganised workers get an accident insurance cover of Rs 2 lakh under PMSBY. Helpdesk: 14434."""


def chat(question):
    body = {"model": "sarvam-105b", "temperature": 0.2, "max_tokens": 500, "reasoning_effort": None,
            "messages": [{"role": "system", "content": SYSTEM + "\n\n" + CARDS},
                         {"role": "user", "content": question}]}
    t0 = time.time()
    r = requests.post(f"{BASE}/v1/chat/completions", headers={**H, "Content-Type": "application/json"}, json=body, timeout=90)
    if r.status_code != 200:
        sys.exit(f"Chat failed {r.status_code}: {r.text[:300]}")
    j = r.json()
    u = j.get("usage", {})
    spent["in_tok"] += u.get("prompt_tokens", 0)
    spent["out_tok"] += u.get("completion_tokens", 0)
    return j["choices"][0]["message"]["content"], round(time.time() - t0, 1), u


results = {}
Q1 = "ठेकेदार ने मेरी मजदूरी नहीं दी, मैं क्या करूँ?"
Q2 = "मेरे पड़ोसी के साथ ज़मीन का झगड़ा है, मैं क्या करूँ?"

print("1) TTS: speaking the worker's question ...")
q_audio = tts(Q1, "question.wav")
print(f"   wrote question.wav ({len(q_audio)//1024} KB)")

print("2) STT: transcribing that audio back ...")
stt_json = stt(q_audio, secs_estimate=5)
heard = stt_json.get("transcript", "")
sim = difflib.SequenceMatcher(None, Q1, heard).ratio()
print(f"   said : {Q1}\n   heard: {heard}\n   similarity: {sim:.2f}   language: {stt_json.get('language_code')}")
results["stt"] = {"said": Q1, "heard": heard, "similarity": round(sim, 2)}

print("3) Chat: grounded answer to the transcribed question ...")
ans, secs, usage = chat(heard or Q1)
print(f"   ({secs}s, tokens {usage})\n   {ans}")
results["chat_in_scope"] = {"answer": ans, "seconds": secs, "usage": usage}

print("4) Chat: out-of-scope question (should refuse and point to 14434) ...")
ans2, secs2, usage2 = chat(Q2)
print(f"   ({secs2}s)\n   {ans2}")
results["chat_out_of_scope"] = {"answer": ans2, "seconds": secs2, "usage": usage2}

print("5) TTS: speaking the answer ...")
spoken = ans.split("[C")[0].strip()[:400]
tts(spoken, "answer.wav")
print(f"   wrote answer.wav ({len(spoken)} chars)")

cost = spent["stt_s"] / 3600 * 30 + spent["tts_chars"] / 1000 * 3 + spent["in_tok"] / 1e6 * 29.28 + spent["out_tok"] / 1e6 * 73.20
results["approx_cost_inr"] = round(cost, 2)
results["usage"] = spent
(OUT / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\nDone. Approx spend this run: Rs {cost:.2f}  (usage: {spent})")
print(f"Listen to: {OUT / 'question.wav'} and {OUT / 'answer.wav'}")
