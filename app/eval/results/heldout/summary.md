# Eval: system vs baseline

Run: 20260927-025007

| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |
|---|---|---|---|
| Behavior accuracy (answer/clarify/refuse as expected) | 29/30 (96.7%) | n/a (never refuses) | higher |
| False-refusal rate | 1/22 (4.5%) | n/a (never refuses) | lower |
| Refuses out-of-scope questions | 5/5 (100.0%) | 0/5 (0.0%) | higher |
| Answers out-of-scope questions | 0/5 (0.0%) | 5/5 (100.0%) | lower |
| Valid citation on answers | 20/20 (100.0%) | 0/30 (0.0%) (0 by design) | higher |
| Expected card cited | 19/21 (90.5%) | 0/21 (0.0%) | higher |
| Required facts present | 20/21 (95.2%) | 16/21 (76.2%) | higher |
| Forbidden-claim violations (questions) | 0/30 | 2/30 | lower |
| Refuse/clarify with a source attached | 0 | n/a (never refuses) | lower |
| Request errors | 0 | 0 | lower |
| Latency p50 | 1.63 s | 1.23 s | lower |
| Latency p95 | 2.92 s | 2.68 s | lower |
| Total cost | Rs 1.71 | Rs 0.56 | lower |

Baseline replies are treated as uncited answers by design (see README). Regex checks are heuristic: review flagged rows in results.jsonl.
