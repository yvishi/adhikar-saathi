"""Tiny stdlib stand-in for the real backend, used to test the eval harness end to end.

Implements GET /api/health and POST /api/ask (multipart or urlencoded) from CONTRACT.md section 8.
It makes no network calls. Behaviour per request:

1. If the LAST user text of the session contains a directive `#fake=<name>` it is obeyed. Directives:
     answer:W-03[,S-01]  correct-shaped answer citing those ids
     answer_nosrc        type=answer but sources=[]              (citation-validity failure)
     unknown_id          type=answer citing card id Z-99         (citation-validity failure)
     refuse              type=refuse, sources=[]                 (correct refusal shape)
     refuse_src          type=refuse but WITH a source           (wrong-citation-on-refusal)
     clarify             type=clarify, sources=[]
     forbidden           answer citing W-01 whose text states "Rs 500"  (forbidden-claim bait)
     error               HTTP 500 with the contract error body
2. Otherwise a crude keyword heuristic picks a card or refuses, so the server is also usable to
   smoke-test the harness on the real questions.jsonl (results are of course meaningless).

All text it emits is English placeholder text (no Hindi authored here).

Run standalone:  python app/eval/fake_server.py --port 8000
"""
import argparse
import json
import re
import threading
import time
from email.parser import BytesParser
from email.policy import HTTP
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

CARDS = {
    "W-01": ("Minimum wage is a legal right", "Code on Wages, 2019", "s.5", "Every worker has the right to minimum wage."),
    "W-03": ("Claim unpaid wages within 3 years", "Code on Wages, 2019", "", "You can file a wage claim within three years."),
    "S-01": ("e-Shram registration and benefits", "e-Shram", "", "e-Shram registration is free."),
    "X-01": ("Helpline 14434", "e-Shram", "", "14434 is the e-Shram helpdesk only."),
}
# keyword -> card id for the heuristic mode (English and a few Devanagari/Latin tokens)
KEYWORDS = [
    (r"three years|3 years|unpaid|claim|मजदूरी|mazdoori", "W-03"),
    (r"minimum wage|न्यूनतम", "W-01"),
    (r"e-?shram|ई-?श्रम|pension|पेंशन", "S-01"),
    (r"14434", "X-01"),
]


def _source(cid: str) -> dict:
    title, name, section, _ = CARDS.get(cid, ("Unknown card", "?", "", ""))
    return {"card_id": cid, "title": title, "source_name": name, "section": section, "url": "https://example.invalid/" + cid}


def _facts(ids: list[str]) -> str:
    return " ".join(CARDS[i][3] for i in ids if i in CARDS) or "Placeholder answer."


def decide(text: str) -> dict:
    """Return {'type', 'ids', 'text', 'status'} for a user text."""
    m = re.search(r"#fake=([a-z_]+)(?::([A-Z0-9,\-]+))?", text)
    if m:
        name, arg = m.group(1), m.group(2)
        ids = arg.split(",") if arg else []
        if name == "answer":
            return {"type": "answer", "ids": ids, "text": _facts(ids)}
        if name == "answer_nosrc":
            return {"type": "answer", "ids": [], "text": _facts(["W-03"])}
        if name == "unknown_id":
            return {"type": "answer", "ids": ["Z-99"], "text": _facts(["W-03"])}
        if name == "refuse":
            return {"type": "refuse", "ids": [], "text": "I can only help with workers' rights and schemes."}
        if name == "refuse_src":
            return {"type": "refuse", "ids": ["W-01"], "text": "I can only help with workers' rights and schemes."}
        if name == "clarify":
            return {"type": "clarify", "ids": [], "text": "Which state do you work in?"}
        if name == "forbidden":
            return {"type": "answer", "ids": ["W-01"], "text": _facts(["W-01"]) + " The rate is Rs 500 per day."}
        if name == "error":
            return {"status": 500}
    for rx, cid in KEYWORDS:
        if re.search(rx, text, re.I):
            return {"type": "answer", "ids": [cid], "text": _facts([cid])}
    return {"type": "refuse", "ids": [], "text": "I can only help with workers' rights and schemes."}


def _parse_form(ctype: str, body: bytes) -> dict:
    if ctype.startswith("multipart/form-data"):
        raw = b"Content-Type: " + ctype.encode() + b"\r\nMIME-Version: 1.0\r\n\r\n" + body
        msg = BytesParser(policy=HTTP).parsebytes(raw)
        out = {}
        for part in msg.iter_parts():
            name = part.get_param("name", header="content-disposition")
            if name and part.get_filename() is None:
                out[name] = (part.get_payload(decode=True) or b"").decode("utf-8", "replace")
        return out
    return {k: v[0] for k, v in parse_qs(body.decode("utf-8", "replace")).items()}


def make_server(port: int = 0, cost: float = 0.05) -> ThreadingHTTPServer:
    sessions: dict[str, list[str]] = {}
    lock = threading.Lock()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):  # keep test output clean
            pass

        def _send(self, status: int, obj: dict):
            data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/api/health":
                return self._send(200, {"ok": True, "providers": {"sarvam": True, "gemini": False, "groq": False},
                                        "cards": len(CARDS), "mock": True})
            self._send(404, {"error": {"code": "bad_request", "message_hi": "", "message_en": "not found"}})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(n)
            if self.path != "/api/ask":
                return self._send(404, {"error": {"code": "bad_request", "message_hi": "", "message_en": "not found"}})
            f = _parse_form(self.headers.get("Content-Type", ""), body)
            text = f.get("text", "")
            if not text:
                return self._send(400, {"error": {"code": "bad_request", "message_hi": "", "message_en": "text required in fake server"}})
            sid = f.get("session_id") or f"fake{int(time.time() * 1000)}"
            with lock:
                sessions.setdefault(sid, []).append(text)
                turns = len(sessions[sid])
            d = decide(text)
            if d.get("status"):
                return self._send(d["status"], {"error": {"code": "llm_failed", "message_hi": "", "message_en": "fake failure"}})
            resp = {
                "session_id": sid,
                "transcript": text,
                "answer_hi": f"[fake hi] {d['text']}",
                "answer_en": d["text"],
                "type": d["type"],
                "sources": [_source(i) for i in d["ids"]],
                "audio_b64": None,
                "audio_mime": "audio/wav",
                "latency_ms": {"stt": 0, "retrieve": 1, "llm": 2, "tts": 0, "total": 3},
                "cost_inr_est": cost,
                "debug": {"retrieved_ids": d["ids"], "used_ids": d["ids"], "provider": "fake", "rewritten_query": None, "turns_in_session": turns},
            }
            self._send(200, resp)

    return ThreadingHTTPServer(("127.0.0.1", port), H)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--cost", type=float, default=0.05, help="cost_inr_est returned per request")
    a = ap.parse_args()
    srv = make_server(a.port, a.cost)
    print(f"fake server on http://127.0.0.1:{srv.server_address[1]}")
    srv.serve_forever()
