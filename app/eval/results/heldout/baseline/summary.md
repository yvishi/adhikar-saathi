# Eval summary (baseline)

Run: 20260927-025007  |  questions evaluated: 30  |  aborted: False

| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |
|---|---|---|---|
| Behavior accuracy (answer/clarify/refuse as expected) | not run | n/a (never refuses) | higher |
| False-refusal rate | not run | n/a (never refuses) | lower |
| Refuses out-of-scope questions | not run | 0/5 (0.0%) | higher |
| Answers out-of-scope questions | not run | 5/5 (100.0%) | lower |
| Valid citation on answers | not run | 0/30 (0.0%) (0 by design) | higher |
| Expected card cited | not run | 0/21 (0.0%) | higher |
| Required facts present | not run | 16/21 (76.2%) | higher |
| Forbidden-claim violations (questions) | not run | 2/30 | lower |
| Refuse/clarify with a source attached | not run | n/a (never refuses) | lower |
| Request errors | not run | 0 | lower |
| Latency p50 | not run | 1.23 s | lower |
| Latency p95 | not run | 2.68 s | lower |
| Total cost | not run | Rs 0.56 | lower |

Flagged forbidden claims: Q009, Q045
Refuse/clarify with source: none
Request errors: none
Expectation adapted to available cards: none
