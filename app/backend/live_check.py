"""Live smoke check of the text pipeline against real Sarvam (costs about Rs 0.15 for 3 turns).

    python -m app.backend.live_check            # text only
    python -m app.backend.live_check --tts      # also ONE TTS of a fixed 30-character line (about Rs 0.1)

Run from the project root. Prints the answers, citations and measured spend. Never prints keys.
"""
import os
import sys

os.environ["DEBUG_RESPONSES"] = "1"
os.environ.pop("MOCK_MODE", None)

from app.backend import config, pipeline  # noqa: E402

QUESTIONS = [
    ("in-scope wage", "ठेकेदार ने मेरी मजदूरी नहीं दी, मैं क्या करूँ?"),
    ("out-of-scope", "मेरे पड़ोसी के साथ ज़मीन का झगड़ा है, मैं क्या करूँ?"),
    ("follow-up", "यह पैसा कितने समय तक मांग सकता हूँ?"),
]
BUDGET_INR = 3.0


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    with_tts = "--tts" in sys.argv
    cards = pipeline.card_count()
    print(f"cards loaded: {cards} (file: {pipeline._cards_path().name})\n")
    total = 0.0
    # follow-up runs in the same session as the wage question, out-of-scope in its own session
    sessions = {"in-scope wage": None, "out-of-scope": None, "follow-up": "reuse"}
    first_sid = None
    for i, (label, q) in enumerate(QUESTIONS):
        use_sid = first_sid if sessions[label] == "reuse" else None
        r = pipeline.ask(session_id=use_sid, text=q, want_audio=False, retrieval=None)
        if i == 0:
            first_sid = r["session_id"]
        total += r["cost_inr_est"]
        d = r["debug"]
        print(f"[{label}] Q: {q}")
        print(f"  type      : {r['type']}")
        print(f"  answer_hi : {r['answer_hi']}")
        print(f"  answer_en : {r['answer_en']}")
        print(f"  sources   : {[s['card_id'] for s in r['sources']]}  (used_ids={d['used_ids']}, retrieved={d['retrieved_ids']})")
        print(f"  query     : {d['rewritten_query']}")
        print(f"  latency   : {r['latency_ms']}  cost est Rs {r['cost_inr_est']}")
        print(f"  audio     : {'yes' if r['audio_b64'] else 'no'}\n")
        if total > BUDGET_INR:
            print("budget exceeded, stopping")
            break
    if with_tts:
        from app.backend import sarvam
        line = "नमस्ते, मैं अधिकार साथी हूँ।"
        sarvam.tts(line)
        total += len(line) * pipeline.TTS_INR_PER_CHAR
        print(f"TTS ok for {len(line)} chars")
    print(f"TOTAL estimated spend: Rs {total:.4f}  (cap Rs {BUDGET_INR})")


if __name__ == "__main__":
    _ = config  # (config import loads .env)
    main()
