"""Benchmark the retriever variants on the fixture. Run from the project root:
    python app/backend/retrieval_data/benchmark.py            (prints a table)
    python app/backend/retrieval_data/benchmark.py --write    (also writes BENCHMARK.md)
"""
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from app.backend import retrieval as R  # noqa: E402

FX = ROOT / "app/backend/tests/fixtures"
Q = json.loads((FX / "queries_fixture.json").read_text(encoding="utf-8"))["queries"]


def rrf(*score_lists, k=60):
    n = len(score_lists[0])
    out = [0.0] * n
    for sc in score_lists:
        for rank, i in enumerate(sorted(range(n), key=lambda i: -sc[i])):
            out[i] += 1 / (k + rank + 1)
    return out


def main():
    write = "--write" in sys.argv
    t0 = time.time()
    r = R.Retriever(str(FX / "retrieval_cards_fixture.json"), mode="hybrid", cache_dir=tempfile.mkdtemp())
    init_s = time.time() - t0
    ids = [c["id"] for c in r._cards]
    cache = {}
    for q in Q:
        R.EMBED_WITH_EXPANSION = False
        e_plain = r._embed_scores(q["q"])
        R.EMBED_WITH_EXPANSION = True
        b, e = r._bm25_scores(q["q"]), r._embed_scores(q["q"])
        cache[q["q"]] = {
            "bm25": b,
            "embed (plain query)": e_plain,
            "embed (+glossary terms)": e,
            "hybrid (score fusion, default)": [R.HYBRID_W_BM25 * x + (1 - R.HYBRID_W_BM25) * y for x, y in zip(b, e)],
            "hybrid RRF (rank only)": rrf(b, e),
        }
    variants = list(next(iter(cache.values())).keys())
    lines = []
    for split in ("tuned", "heldout", "heldout2", "all"):
        qs = [q for q in Q if split == "all" or q.get("split") == split]
        ins = [q for q in qs if not q.get("oos")]
        oos = [q for q in qs if q.get("oos")]
        lines.append(f"\n### {split}: {len(ins)} in-scope + {len(oos)} out-of-scope queries\n")
        lines.append("| method | recall@1 | recall@3 | recall@4 | min top score (in-scope) | max top score (out-of-scope) |")
        lines.append("|---|---|---|---|---|---|")
        for v in variants:
            hit = {1: 0, 3: 0, 4: 0}
            tops_in, tops_oos = [], []
            for q in ins:
                sc = cache[q["q"]][v]
                order = sorted(range(len(sc)), key=lambda i: -sc[i])
                for k in hit:
                    hit[k] += bool({ids[i] for i in order[:k]} & set(q["expected"]))
                tops_in.append(sc[order[0]])
            for q in oos:
                tops_oos.append(max(cache[q["q"]][v]))
            n = len(ins)
            rrf_note = v.startswith("hybrid RRF")
            lo = "n/a" if rrf_note else f"{min(tops_in):.2f} (p10 {sorted(tops_in)[len(tops_in)//10]:.2f})"
            hi = "n/a" if rrf_note else f"{max(tops_oos):.2f}"
            lines.append(f"| {v} | {hit[1]/n:.3f} | {hit[3]/n:.3f} | {hit[4]/n:.3f} | {lo} | {hi} |")
    # per-language r@1 for default
    v = "hybrid (score fusion, default)"
    lang = {}
    for q in Q:
        if q.get("oos"):
            continue
        sc = cache[q["q"]][v]
        top = ids[max(range(len(sc)), key=lambda i: sc[i])]
        d = lang.setdefault(q["lang"], [0, 0])
        d[0] += top in q["expected"]
        d[1] += 1
    lines.append("\nDefault (hybrid) recall@1 by language, all in-scope queries: " + ", ".join(f"{k} {a}/{b}" for k, (a, b) in lang.items()))
    lines.append(f"\nStartup (index + model load, cached vectors absent): {init_s:.1f} s.")
    real = ROOT / "app/data/cards/cards.json"
    if real.exists():
        lines.append("\n### Snapshot on the REAL cards file (same queries; expected ids come from the planned card ids)\n")
        lines.append("| method | recall@1 | recall@4 | max top score (out-of-scope) |")
        lines.append("|---|---|---|---|")
        ins = [q for q in Q if not q.get("oos")]
        oos = [q for q in Q if q.get("oos")]
        for mode in ("bm25", "hybrid"):
            rr = R.Retriever(str(real), mode=mode, cache_dir=tempfile.mkdtemp())
            top = [[c["id"] for c in rr.retrieve(q["q"], 4)] for q in ins]
            r1 = sum(t[0] in q["expected"] for t, q in zip(top, ins)) / len(ins)
            r4 = sum(bool(set(t) & set(q["expected"])) for t, q in zip(top, ins)) / len(ins)
            mx = max(rr.retrieve(q["q"], 1)[0]["score"] for q in oos)
            lines.append(f"| {mode} | {r1:.3f} | {r4:.3f} | {mx:.2f} |")
    text = "\n".join(lines)
    print(text)
    if write:
        head = (
            "# Retrieval benchmark (fixture cards, NOT the real corpus)\n\n"
            "Regenerate: `python app/backend/retrieval_data/benchmark.py --write`. Hit = any expected id within top-k.\n"
            "Scores are the 0-1 values returned by `Retriever.retrieve` (RRF has no absolute scale).\n"
            f"Default constants: BM25_SCALE={R.BM25_SCALE}, HYBRID_W_BM25={R.HYBRID_W_BM25}, cosine range "
            f"{R.COS_LOW}-{R.COS_HIGH}, glossary terms appended for the embedder={R.EMBED_WITH_EXPANSION}.\n"
            "`tuned` queries were written together with the glossary and the constants were chosen on them, so they are optimistic;\n"
            "`heldout` was written after the glossary was first frozen (then the glossary was extended from its misses, so it is no longer blind);\n"
            "`heldout2` was written after that and is the least biased. Expect lower numbers on real cards and real speech.\n"
        )
        (Path(__file__).parent / "BENCHMARK.md").write_text(head + text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
