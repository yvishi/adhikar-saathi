"""Send the known-good demo questions through the real pipeline with TTS_CACHE=1, so the spoken
answers are saved in app/data/cache/tts/ (keyed by the answer text). LIVE and PAID: about Rs 1.2 per
answer question, Rs 0.35 for a refusal. Run from the project root:

    python scripts/prewarm_demo.py --list
    python scripts/prewarm_demo.py --limit 3            # first 3 in the order below
    python scripts/prewarm_demo.py --only refuse,pmsym  # or pick by name
    python scripts/prewarm_demo.py --max-inr 5          # stops before spending more than this

Caveat: the cache key is the exact answer text and the LLM is not perfectly deterministic (temperature
0.2), so a re-asked question can miss the cache and be spoken (and paid) again. Refusals are fixed text,
so those always hit. Choice of questions: refuse, wages, pmsym and salary7 behaved as expected in every real run of the
integration eval. "clarify" is NOT reliable: it clarified in 2 of 3 real runs and answered in the third
(live prewarm proof run, see app/RUNBOOK.md); for a guaranteed clarify use MOCK_MODE with text "mock:clarify"."""
import argparse
import os
import sys
from pathlib import Path

os.environ["TTS_CACHE"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from app.backend import config, pipeline  # noqa: E402

# name -> (expected type, [turns]); only the last turn is spoken
DEMO = {
    "refuse": ("refuse", ["आज क्रिकेट मैच का स्कोर क्या है?"]),       # off-topic: gated, no LLM call
    "clarify": ("clarify", ["काम पर एक आदमी मुझे परेशान करता है।", "वो मेरा सुपरवाइज़र है। शिकायत कहाँ करूँ?"]),
    "wages": ("answer", ["मेरे ठेकेदार ने तीन महीने से मजदूरी नहीं दी, मैं क्या करूँ?"]),
    "pmsym": ("answer", ["I am 45, can I join PM-SYM?"]),
    "salary7": ("answer", ["Mera malik mahine ki salary 7 tarikh ke baad bhi nahi deta, kya ye sahi hai?"]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=len(DEMO))
    ap.add_argument("--max-inr", type=float, default=5.0)
    a = ap.parse_args()
    if a.list:
        for k, (t, turns) in DEMO.items():
            print(f"{k:8s} expect={t:8s} {turns}")
        return 0
    names = [n for n in (a.only.split(",") if a.only else DEMO) if n][: a.limit]
    spent = 0.0
    for n in names:
        exp, turns = DEMO[n]
        sid = f"prewarm-{n}"
        for i, t in enumerate(turns):
            last = i == len(turns) - 1
            if spent >= a.max_inr:
                print(f"budget reached (Rs {spent:.2f}); stopping")
                return 1
            r = pipeline.ask(session_id=sid, text=t, want_audio=last)
            spent += r["cost_inr_est"]
            if last:
                cached = "yes" if r["audio_b64"] else "NO AUDIO"
                flag = "" if r["type"] == exp else f"   <-- expected {exp}"
                print(f"{n:8s} type={r['type']:8s} audio={cached} cost=Rs{r['cost_inr_est']:.3f} "
                      f"sources={[s['card_id'] for s in r['sources']]}{flag}")
    n_files = len(list(config.TTS_CACHE_DIR.glob("*.wav"))) if config.TTS_CACHE_DIR.exists() else 0
    print(f"total cost Rs {spent:.2f}; {n_files} wav files in {config.TTS_CACHE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
