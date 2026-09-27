# Eval: system vs baseline

Run: 20260927-024155

| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |
|---|---|---|---|
| Behavior accuracy (answer/clarify/refuse as expected) | 29/30 (96.7%) | n/a (never refuses) | higher |
| False-refusal rate | 0/21 (0.0%) | n/a (never refuses) | lower |
| Refuses out-of-scope questions | 5/5 (100.0%) | 0/5 (0.0%) | higher |
| Answers out-of-scope questions | 0/5 (0.0%) | 5/5 (100.0%) | lower |
| Valid citation on answers | 18/18 (100.0%) | 0/30 (0.0%) (0 by design) | higher |
| Expected card cited | 14/18 (77.8%) | 0/18 (0.0%) | higher |
| Required facts present | 17/18 (94.4%) | 14/18 (77.8%) | higher |
| Forbidden-claim violations (questions) | 1/30 | 4/30 | lower |
| Refuse/clarify with a source attached | 0 | n/a (never refuses) | lower |
| Request errors | 0 | 0 | lower |
| Latency p50 | 1.56 s | 1.72 s | lower |
| Latency p95 | 3.13 s | 2.38 s | lower |
| Total cost | Rs 2.13 | Rs 0.72 | lower |

Baseline replies are treated as uncited answers by design (see README). Regex checks are heuristic: review flagged rows in results.jsonl.
