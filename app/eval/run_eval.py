"""Evaluation harness for Adhikar Saathi: our system (A) vs a no-corpus, no-guardrail baseline (B).

Usage (from the project root, Python 3.12, needs `requests`):
  python app/eval/run_eval.py --mode system   --base-url http://127.0.0.1:8000
  python app/eval/run_eval.py --mode baseline
  python app/eval/run_eval.py --mode both     --base-url http://127.0.0.1:8000
  python app/eval/run_eval.py --compare app/eval/results/A app/eval/results/B
  python app/eval/run_eval.py --selftest      (no network, no paid calls)

Metric definitions live in app/eval/README.md. This script makes NO LLM-judge calls unless --judge is given.
"""
import argparse
import datetime as dt
import importlib
import json
import math
import re
import sys
import tempfile
import threading
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # project root R
DEFAULT_QUESTIONS = HERE / "questions.jsonl"
DEFAULT_CARDS = ROOT / "app" / "data" / "cards" / "cards.json"

# Contract section 6 planned ids: used to validate citations when the real cards file does not exist yet.
PLANNED_IDS = {
    "W-01", "W-02", "W-03", "W-04", "W-05", "W-06", "W-07",
    "S-01", "S-02", "S-03", "S-04", "S-05", "M-01", "H-01", "X-01", "X-02", "D-01", "D-02",
}
# sarvam-105b prices (contract section 4), Rs per 1M tokens. Used for baseline cost from `usage`.
PRICE_IN, PRICE_OUT = 29.28, 73.20
BASELINE_SYSTEM_PROMPT = "You are a helpful assistant. Answer in simple Hindi."


# ------------------------------------------------------------------ loading
def load_questions(path: Path) -> list[dict]:
    qs = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                qs.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{i}: invalid JSON: {e}")
    return qs


def load_cards(path: Path):
    """Return (valid_ids, available_ids_or_None). valid = non-skipped ids in the file. None = file missing."""
    if not path.exists():
        return set(PLANNED_IDS), None
    cards = json.loads(path.read_text(encoding="utf-8"))
    avail = {c["id"] for c in cards if c.get("status", "ready") != "skipped"}
    return avail, avail


def effective_question(q: dict, available: set | None):
    """Adapt expectations to the cards actually available. Returns (q_eff, adapted: bool)."""
    if available is None or q["expected_behavior"] != "answer" or not q["expected_card_ids"]:
        return q, False
    keep = [c for c in q["expected_card_ids"] if c in available]
    if keep == q["expected_card_ids"]:
        return q, False
    e = dict(q)
    if keep:
        e["expected_card_ids"] = keep
    else:  # every expected card is skipped or missing: the correct behaviour is a refusal
        e.update(expected_behavior="refuse", expected_card_ids=[], required_any=[])
        e["also_acceptable"] = [b for b in q.get("also_acceptable", []) if b != "answer"]
    return e, True


# ------------------------------------------------------------------ calling
class Budget:
    def __init__(self, max_inr: float):
        self.max_inr, self.spent = max_inr, 0.0

    def add(self, x: float):
        self.spent += x or 0.0

    @property
    def exceeded(self) -> bool:
        return self.spent > self.max_inr


def ask_system(base_url, sid, text, provider, retrieval, timeout):
    form = {"session_id": (None, sid), "text": (None, text), "want_audio": (None, "false")}
    if provider:
        form["provider"] = (None, provider)
    if retrieval:
        form["retrieval"] = (None, retrieval)
    err = None
    for attempt in range(3):
        t0 = time.perf_counter()
        try:
            r = requests.post(base_url.rstrip("/") + "/api/ask", files=form, timeout=timeout)
        except requests.RequestException as e:
            return None, f"request failed: {type(e).__name__}", (time.perf_counter() - t0) * 1000
        wall = (time.perf_counter() - t0) * 1000
        if r.status_code == 200:
            try:
                return r.json(), None, wall
            except ValueError:
                return None, "non-JSON 200 response", wall
        try:
            code = r.json().get("error", {}).get("code", "")
        except ValueError:
            code = ""
        err = f"HTTP {r.status_code} {code}".strip()
        if r.status_code in (429, 502, 503) and attempt < 2:
            time.sleep(2 * (attempt + 1))
            continue
        break
    return None, err, wall


def run_one(q: dict, mode: str, ctx: dict) -> dict:
    """Run all turns of one question; the final turn is graded. Returns a row (without flags)."""
    sid = f"eval-{ctx['run_id']}-{q['id']}"
    history, turns_out, walls, cost = [], [], [], 0.0
    final = {"type": "error", "text_hi": "", "text_en": "", "source_ids": [], "error": None}
    for user in q["turns"]:
        if mode == "system":
            j, err, wall = ask_system(ctx["base_url"], sid, user, ctx["provider"], ctx["retrieval"], ctx["timeout"])
            walls.append(wall)
            if err or j is None:
                final = {"type": "error", "text_hi": "", "text_en": "", "source_ids": [], "error": err}
                turns_out.append({"user": user, "error": err})
                break
            cost += float(j.get("cost_inr_est") or 0.0)
            final = {"type": j.get("type", "answer"), "text_hi": j.get("answer_hi", ""), "text_en": j.get("answer_en", ""),
                     "source_ids": [s.get("card_id") for s in j.get("sources") or []], "error": None,
                     "server_turns": (j.get("debug") or {}).get("turns_in_session")}
        else:
            msgs = [{"role": "system", "content": BASELINE_SYSTEM_PROMPT}] + history + [{"role": "user", "content": user}]
            t0 = time.perf_counter()
            try:
                out = ctx["complete_fn"](msgs, provider=ctx["provider"], max_tokens=500, temperature=0.2)
            except Exception as e:  # provider errors, missing keys...
                walls.append((time.perf_counter() - t0) * 1000)
                err = f"{type(e).__name__}: {str(e)[:120]}"
                final = {"type": "error", "text_hi": "", "text_en": "", "source_ids": [], "error": err}
                turns_out.append({"user": user, "error": err})
                break
            walls.append((time.perf_counter() - t0) * 1000)
            u = out.get("usage") or {}
            cost += (u.get("prompt_tokens", 0) * PRICE_IN + u.get("completion_tokens", 0) * PRICE_OUT) / 1e6
            # By design the baseline "answers everything with no citation".
            final = {"type": "answer", "text_hi": out.get("text", ""), "text_en": "", "source_ids": [], "error": None}
            history += [{"role": "user", "content": user}, {"role": "assistant", "content": final["text_hi"]}]
        turns_out.append({"user": user, "type": final["type"], "answer_hi": final["text_hi"][:600]})
    ctx["budget"].add(cost)
    return {"id": q["id"], "category": q["category"], "mode": mode, "n_turns": len(q["turns"]), "type": final["type"],
            "source_ids": final["source_ids"], "server_turns": final.get("server_turns"), "answer_hi": final["text_hi"], "answer_en": final["text_en"],
            "error": final["error"], "wall_ms": walls, "cost_inr": cost, "turns": turns_out}


# ------------------------------------------------------------------ grading
def _match_any(patterns: list[str], text: str) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def grade(row: dict, qe: dict, adapted: bool, valid_ids: set, judge=None) -> dict:
    text = (row["answer_hi"] or "") + "\n" + (row["answer_en"] or "")
    exp, also = qe["expected_behavior"], qe.get("also_acceptable", [])
    typ, srcs = row["type"], row["source_ids"]
    f = {}
    f["behavior_ok"] = typ == exp or typ in also
    f["false_refusal"] = (typ == "refuse" and exp in ("answer", "clarify") and "refuse" not in also) if exp != "refuse" else None
    f["citation_valid"] = (bool(srcs) and all(s in valid_ids for s in srcs)) if typ == "answer" else None
    f["card_hit"] = (typ == "answer" and any(c in srcs for c in qe["expected_card_ids"])) if exp == "answer" and qe["expected_card_ids"] else None
    f["facts_hit"] = _match_any(qe["required_any"], text) if exp == "answer" and qe["required_any"] else None
    f["forbidden_hits"] = [p for p in qe["forbidden"] if re.search(p, text, re.I)]
    f["wrong_cite_refusal"] = typ in ("refuse", "clarify") and bool(srcs)
    f["judge"] = None
    if judge:
        f["judge"] = judge(qe, text, srcs)
    row.update(adapted=adapted, expected_behavior=exp, also_acceptable=also, expected_card_ids=qe["expected_card_ids"], flags=f)
    return row


# ------------------------------------------------------------------ metrics
def _frac(num, den):
    return {"num": num, "den": den, "value": (num / den) if den else None}


def _pct(vals, p):
    if not vals:
        return None
    s = sorted(vals)
    return s[max(0, math.ceil(p * len(s)) - 1)]


def compute_metrics(rows: list[dict]) -> dict:
    fl = lambda r: r["flags"]
    oos = [r for r in rows if r["category"] == "out_of_scope"]
    ans_or_clar = [r for r in rows if r["expected_behavior"] in ("answer", "clarify")]
    answers = [r for r in rows if r["type"] == "answer"]
    m = {
        "n_questions": len(rows),
        "behavior_accuracy": _frac(sum(fl(r)["behavior_ok"] for r in rows), len(rows)),
        "false_refusal_rate": _frac(sum(bool(fl(r)["false_refusal"]) for r in ans_or_clar), len(ans_or_clar)),
        "refusal_on_out_of_scope": _frac(sum(r["type"] == "refuse" for r in oos), len(oos)),
        "answered_out_of_scope": _frac(sum(r["type"] == "answer" for r in oos), len(oos)),
        "citation_validity": _frac(sum(bool(fl(r)["citation_valid"]) for r in answers), len(answers)),
        "expected_card_hit": _frac(sum(bool(fl(r)["card_hit"]) for r in rows if fl(r)["card_hit"] is not None),
                                   sum(fl(r)["card_hit"] is not None for r in rows)),
        "required_facts_hit": _frac(sum(bool(fl(r)["facts_hit"]) for r in rows if fl(r)["facts_hit"] is not None),
                                    sum(fl(r)["facts_hit"] is not None for r in rows)),
        "forbidden_violations": {"count": sum(len(fl(r)["forbidden_hits"]) > 0 for r in rows), "den": len(rows),
                                 "ids": [r["id"] for r in rows if fl(r)["forbidden_hits"]]},
        "wrong_citation_on_refusal": {"count": sum(bool(fl(r)["wrong_cite_refusal"]) for r in rows),
                                      "ids": [r["id"] for r in rows if fl(r)["wrong_cite_refusal"]]},
        "errors": {"count": sum(r["type"] == "error" for r in rows), "ids": [r["id"] for r in rows if r["type"] == "error"]},
    }
    walls = [w for r in rows for w in r["wall_ms"]]
    m["latency_ms_p50"], m["latency_ms_p95"] = _pct(walls, 0.5), _pct(walls, 0.95)
    m["total_cost_inr"] = sum(r["cost_inr"] for r in rows)
    m["cost_per_question_inr"] = m["total_cost_inr"] / len(rows) if rows else None
    js = [fl(r)["judge"] for r in rows if fl(r)["judge"] is not None]
    if js:
        m["judge_correct_rate"] = _frac(sum(bool(j.get("correct")) for j in js), len(js))
    return m


def _fmt(f, pct=True):
    if f is None or f.get("value") is None:
        return "n/a"
    return f"{f['num']}/{f['den']} ({f['value'] * 100:.1f}%)"


def _ms(x):
    return "n/a" if x is None else f"{x / 1000:.2f} s"


def table(sys_m: dict | None, base_m: dict | None) -> str:
    """Markdown side-by-side table. Baseline cells that are meaningless by design show 'n/a'."""
    def col(m, key, fn=_fmt):
        return fn(m[key]) if m and key in m else "not run"

    NA = "n/a (never refuses)"
    rows = [
        ("Behavior accuracy (answer/clarify/refuse as expected)", col(sys_m, "behavior_accuracy"), NA if base_m else "not run", "higher"),
        ("False-refusal rate", col(sys_m, "false_refusal_rate"), NA if base_m else "not run", "lower"),
        ("Refuses out-of-scope questions", col(sys_m, "refusal_on_out_of_scope"), col(base_m, "refusal_on_out_of_scope"), "higher"),
        ("Answers out-of-scope questions", col(sys_m, "answered_out_of_scope"), col(base_m, "answered_out_of_scope"), "lower"),
        ("Valid citation on answers", col(sys_m, "citation_validity"), col(base_m, "citation_validity") + " (0 by design)" if base_m else "not run", "higher"),
        ("Expected card cited", col(sys_m, "expected_card_hit"), col(base_m, "expected_card_hit"), "higher"),
        ("Required facts present", col(sys_m, "required_facts_hit"), col(base_m, "required_facts_hit"), "higher"),
        ("Forbidden-claim violations (questions)", col(sys_m, "forbidden_violations", lambda x: f"{x['count']}/{x['den']}"),
         col(base_m, "forbidden_violations", lambda x: f"{x['count']}/{x['den']}"), "lower"),
        ("Refuse/clarify with a source attached", col(sys_m, "wrong_citation_on_refusal", lambda x: str(x["count"])), NA if base_m else "not run", "lower"),
        ("Request errors", col(sys_m, "errors", lambda x: str(x["count"])), col(base_m, "errors", lambda x: str(x["count"])), "lower"),
        ("Latency p50", col(sys_m, "latency_ms_p50", _ms), col(base_m, "latency_ms_p50", _ms), "lower"),
        ("Latency p95", col(sys_m, "latency_ms_p95", _ms), col(base_m, "latency_ms_p95", _ms), "lower"),
        ("Total cost", col(sys_m, "total_cost_inr", lambda x: f"Rs {x:.2f}"), col(base_m, "total_cost_inr", lambda x: f"Rs {x:.2f}"), "lower"),
    ]
    if (sys_m and "judge_correct_rate" in sys_m) or (base_m and "judge_correct_rate" in base_m):
        rows.append(("LLM-judge correct (optional)", col(sys_m, "judge_correct_rate"), col(base_m, "judge_correct_rate"), "higher"))
    out = ["| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows]
    return "\n".join(out)


def write_outputs(out_dir: Path, rows: list[dict], mode: str, meta: dict):
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "results.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    m = compute_metrics(rows) if rows else {}
    (out_dir / "summary.json").write_text(json.dumps({"mode": mode, "meta": meta, "metrics": m}, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# Eval summary ({mode})", "", f"Run: {meta.get('run_id')}  |  questions evaluated: {len(rows)}  |  aborted: {meta.get('aborted')}", ""]
    if rows:
        md.append(table(m if mode == "system" else None, m if mode == "baseline" else None))
        md += ["", "Flagged forbidden claims: " + (", ".join(m["forbidden_violations"]["ids"]) or "none"),
               "Refuse/clarify with source: " + (", ".join(m["wrong_citation_on_refusal"]["ids"]) or "none"),
               "Request errors: " + (", ".join(m["errors"]["ids"]) or "none"),
               "Expectation adapted to available cards: " + (", ".join(meta.get("adapted_ids") or []) or "none")]
    (out_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return m


def write_side_by_side(out_dir: Path, sys_m, base_m, meta):
    md = ["# Eval: system vs baseline", "", f"Run: {meta.get('run_id')}", "", table(sys_m, base_m), "",
          "Baseline replies are treated as uncited answers by design (see README). Regex checks are heuristic: review flagged rows in results.jsonl."]
    (out_dir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ orchestration
def run_mode(mode, questions, args, ctx, valid_ids, available, out_dir, run_meta):
    rows, aborted, adapted_ids = [], False, []
    n = len(questions)
    for i, q in enumerate(questions, 1):
        qe, adapted = effective_question(q, available)
        if adapted:
            adapted_ids.append(q["id"])
        row = grade(run_one(q, mode, ctx), qe, adapted, valid_ids, ctx.get("judge"))
        rows.append(row)
        print(f"[{mode} {i}/{n}] {q['id']} exp={qe['expected_behavior']} got={row['type']} src={','.join(row['source_ids']) or '-'} "
              f"cost=Rs{row['cost_inr']:.3f} total=Rs{ctx['budget'].spent:.2f}" + (f" ERR={row['error']}" if row["error"] else ""), flush=True)
        if ctx["budget"].exceeded:
            aborted = True
            print(f"BUDGET EXCEEDED: Rs {ctx['budget'].spent:.2f} > --max-inr {ctx['budget'].max_inr}. Aborting.", flush=True)
            break
    meta = dict(run_meta, mode=mode, aborted=aborted, adapted_ids=adapted_ids, provider=ctx["provider"], retrieval=ctx["retrieval"])
    m = write_outputs(out_dir, rows, mode, meta)
    return rows, m, aborted


def load_judge(spec: str | None):
    """--judge pkg.module:function. The callable gets (question, answer_text, source_ids) and returns
    {"correct": bool, "reason": str}. It is the caller's job to keep its cost inside --max-inr; nothing runs unless this flag is given."""
    if not spec:
        return None
    mod, _, fn = spec.partition(":")
    return getattr(importlib.import_module(mod), fn)


def get_complete_fn():
    sys.path.insert(0, str(ROOT))
    from app.backend.llm import complete  # noqa: E402
    return complete


def build_ctx(args, budget, complete_fn=None, run_id=None):
    return {"base_url": args.base_url, "provider": args.provider, "retrieval": args.retrieval, "timeout": args.timeout,
            "budget": budget, "complete_fn": complete_fn, "judge": load_judge(args.judge),
            "run_id": run_id or dt.datetime.now().strftime("%Y%m%d-%H%M%S")}


def select(questions, args):
    if args.ids:
        want = [x.strip() for x in args.ids.split(",") if x.strip()]
        by = {q["id"]: q for q in questions}
        missing = [w for w in want if w not in by]
        if missing:
            raise SystemExit(f"unknown ids: {missing}")
        questions = [by[w] for w in want]
    return questions[: args.limit] if args.limit else questions


def compare(dirs):
    ms = []
    for d in dirs:
        rows = load_questions(Path(d) / "results.jsonl")
        ms.append(compute_metrics(rows))
    print(table(ms[0], ms[1]))


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--mode", choices=["system", "baseline", "both"], default="system")
    ap.add_argument("--provider", default=None, help="sarvam|gemini|groq (system: sent to /api/ask; baseline: passed to complete())")
    ap.add_argument("--retrieval", default=None, help="topk|all (system only)")
    ap.add_argument("--questions", default=str(DEFAULT_QUESTIONS))
    ap.add_argument("--cards", default=str(DEFAULT_CARDS))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="", help="comma-separated question ids")
    ap.add_argument("--max-inr", type=float, default=8.0, help="abort when cumulative estimated cost exceeds this")
    ap.add_argument("--out", default=None, help="output dir (default app/eval/results/<timestamp>)")
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--no-adapt", action="store_true", help="do not turn expectations into refusals when expected cards are skipped/missing")
    ap.add_argument("--judge", default=None, help="OFF by default. module:function judge hook, see README")
    ap.add_argument("--compare", nargs=2, metavar=("SYSTEM_DIR", "BASELINE_DIR"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.compare:
        return compare(args.compare)

    questions = select(load_questions(Path(args.questions)), args)
    valid_ids, available = load_cards(Path(args.cards))
    if available is None:
        print(f"note: {args.cards} not found; validating citations against the planned ids in CONTRACT section 6, no expectation adaptation.")
    if args.no_adapt:
        available = None
    out = Path(args.out) if args.out else HERE / "results" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    budget = Budget(args.max_inr)
    ctx = build_ctx(args, budget, complete_fn=get_complete_fn() if args.mode in ("baseline", "both") else None)
    meta = {"run_id": ctx["run_id"], "questions_file": args.questions, "cards_file": args.cards}

    sys_m = base_m = None
    aborted = False
    if args.mode in ("system", "both"):
        _, sys_m, aborted = run_mode("system", questions, args, ctx, valid_ids, available, out / "system" if args.mode == "both" else out, meta)
    if args.mode in ("baseline", "both") and not aborted:
        _, base_m, aborted = run_mode("baseline", questions, args, ctx, valid_ids, available, out / "baseline" if args.mode == "both" else out, meta)
    if args.mode == "both":
        out.mkdir(parents=True, exist_ok=True)
        write_side_by_side(out, sys_m, base_m, meta)
    print("\n" + table(sys_m, base_m))
    print(f"\nTotal spend: Rs {budget.spent:.2f}  |  results in {out}")
    return 1 if aborted else 0


# ------------------------------------------------------------------ selftest
def selftest() -> int:
    sys.path.insert(0, str(HERE))
    import fake_server

    def q(id, text, cat, exp, cards, req, forb=(), turns=None, also=()):
        d = {"id": id, "turns": turns or [text], "question_hi": text, "question_en": text, "category": cat,
             "expected_behavior": exp, "expected_card_ids": cards, "required_any": req, "forbidden": list(forb), "notes": ""}
        if also:
            d["also_acceptable"] = list(also)
        return d

    THREE, FREE_, MW = [r"three years"], [r"free"], [r"minimum wage"]
    qs = [
        q("s01", "wage claim time #fake=answer:W-03", "wages", "answer", ["W-03"], THREE),
        q("s02", "e-Shram fee #fake=answer:S-01", "schemes", "answer", ["S-01"], FREE_),
        q("s03", "e-Shram fee wrong card #fake=answer:W-01", "schemes", "answer", ["S-01"], FREE_),
        q("s04", "answer with no sources #fake=answer_nosrc", "wages", "answer", ["W-03"], THREE),
        q("s05", "answer with unknown id #fake=unknown_id", "wages", "answer", ["W-03"], THREE),
        q("s06", "should answer but refuses #fake=refuse", "wages", "answer", ["W-03"], THREE),
        q("s07", "cricket score #fake=refuse", "out_of_scope", "refuse", [], []),
        q("s08", "divorce #fake=refuse_src", "out_of_scope", "refuse", [], []),
        q("s09", "weather #fake=answer:W-01", "out_of_scope", "refuse", [], []),
        q("s10", "vague #fake=clarify", "wages", "clarify", ["W-03"], []),
        q("s11", "state minimum wage #fake=forbidden", "adversarial", "answer", ["W-01"], MW, forb=[r"Rs\.?\s?[0-9]+"]),
        q("s12", "unused first turn", "wages", "answer", ["W-03"], THREE, turns=["hello", "how long can I claim #fake=answer:W-03"]),
    ]
    cards = [{"id": i, "status": "ready"} for i in ("W-01", "W-03", "S-01", "X-01")]
    tmp = Path(tempfile.mkdtemp(prefix="eval_selftest_"))
    (tmp / "cards.json").write_text(json.dumps(cards), encoding="utf-8")
    valid_ids, available = load_cards(tmp / "cards.json")

    srv = fake_server.make_server(0, cost=0.05)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    ns = argparse.Namespace(base_url=f"http://127.0.0.1:{port}", provider=None, retrieval=None, timeout=10.0, judge=None)
    checks = []

    def check(name, got, want):
        ok = got == want
        checks.append(ok)
        print(f"  {'PASS' if ok else 'FAIL'}  {name}: got {got!r}, want {want!r}")

    print(f"fake server on port {port}")
    # A: system run
    ctx = build_ctx(ns, Budget(100.0), run_id="selftest")
    rows, m, aborted = run_mode("system", qs, ns, ctx, valid_ids, available, tmp / "sys", {"run_id": "selftest"})
    print("\nSystem metrics checks")
    check("evaluated", m["n_questions"], 12)
    check("behavior_accuracy", (m["behavior_accuracy"]["num"], m["behavior_accuracy"]["den"]), (10, 12))
    check("false_refusal", (m["false_refusal_rate"]["num"], m["false_refusal_rate"]["den"]), (1, 9))
    check("refusal_on_oos", (m["refusal_on_out_of_scope"]["num"], m["refusal_on_out_of_scope"]["den"]), (2, 3))
    check("answered_oos", (m["answered_out_of_scope"]["num"], m["answered_out_of_scope"]["den"]), (1, 3))
    check("citation_validity", (m["citation_validity"]["num"], m["citation_validity"]["den"]), (6, 8))
    check("expected_card_hit", (m["expected_card_hit"]["num"], m["expected_card_hit"]["den"]), (4, 8))
    check("required_facts_hit", (m["required_facts_hit"]["num"], m["required_facts_hit"]["den"]), (6, 8))
    check("forbidden_violations", m["forbidden_violations"]["ids"], ["s11"])
    check("wrong_citation_on_refusal (refuse-with-source)", m["wrong_citation_on_refusal"]["ids"], ["s08"])
    check("errors", m["errors"]["count"], 0)
    check("multi-turn reuses one session (server saw 2 turns)", rows[-1]["server_turns"], 2)
    check("system cost (13 requests x Rs 0.05)", round(m["total_cost_inr"], 4), 0.65)
    # B: baseline with a stub LLM (no network)
    stub = lambda msgs, provider=None, max_tokens=500, temperature=0.2: {
        "text": "You can claim within three years.", "usage": {"prompt_tokens": 100, "completion_tokens": 50}, "provider": "stub"}
    ctxb = build_ctx(ns, Budget(100.0), complete_fn=stub, run_id="selftest")
    _, bm, _ = run_mode("baseline", qs, ns, ctxb, valid_ids, available, tmp / "base", {"run_id": "selftest"})
    print("\nBaseline metrics checks")
    check("answered_oos", (bm["answered_out_of_scope"]["num"], bm["answered_out_of_scope"]["den"]), (3, 3))
    check("citation rate (0 by design)", bm["citation_validity"]["num"], 0)
    check("required_facts_hit", (bm["required_facts_hit"]["num"], bm["required_facts_hit"]["den"]), (5, 8))
    check("forbidden_violations", bm["forbidden_violations"]["count"], 0)
    check("baseline cost (13 calls)", round(bm["total_cost_inr"], 5), round(13 * (100 * PRICE_IN + 50 * PRICE_OUT) / 1e6, 5))
    # C: budget guard
    srv2 = fake_server.make_server(0, cost=0.05)
    threading.Thread(target=srv2.serve_forever, daemon=True).start()
    ns2 = argparse.Namespace(**{**vars(ns), "base_url": f"http://127.0.0.1:{srv2.server_address[1]}"})
    ctxc = build_ctx(ns2, Budget(0.12), run_id="selftest")
    rows_c, _, aborted_c = run_mode("system", qs, ns2, ctxc, valid_ids, available, tmp / "budget", {"run_id": "selftest"})
    print("\nBudget guard check")
    check("aborted after cost exceeds Rs 0.12 (3 x Rs 0.05)", (aborted_c, len(rows_c)), (True, 3))
    # D: adaptation to skipped cards
    print("\nAdaptation check")
    e, a = effective_question(qs[0], {"W-01"})
    check("expected card skipped -> refuse", (a, e["expected_behavior"], e["expected_card_ids"]), (True, "refuse", []))
    # E: table renders
    print("\n" + table(m, bm))
    print()
    srv.shutdown()
    srv2.shutdown()
    if all(checks):
        print(f"SELFTEST PASSED ({sum(checks)}/{len(checks)} checks)")
        return 0
    print(f"SELFTEST FAILED ({sum(checks)}/{len(checks)} checks passed)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
