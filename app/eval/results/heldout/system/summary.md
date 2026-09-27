# Eval summary (system)

Run: 20260927-025007  |  questions evaluated: 30  |  aborted: False

| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |
|---|---|---|---|
| Behavior accuracy (answer/clarify/refuse as expected) | 29/30 (96.7%) | not run | higher |
| False-refusal rate | 1/22 (4.5%) | not run | lower |
| Refuses out-of-scope questions | 5/5 (100.0%) | not run | higher |
| Answers out-of-scope questions | 0/5 (0.0%) | not run | lower |
| Valid citation on answers | 20/20 (100.0%) | not run | higher |
| Expected card cited | 19/21 (90.5%) | not run | higher |
| Required facts present | 20/21 (95.2%) | not run | higher |
| Forbidden-claim violations (questions) | 0/30 | not run | lower |
| Refuse/clarify with a source attached | 0 | not run | lower |
| Request errors | 0 | not run | lower |
| Latency p50 | 1.63 s | not run | lower |
| Latency p95 | 2.92 s | not run | lower |
| Total cost | Rs 1.71 | not run | lower |

Flagged forbidden claims: none
Refuse/clarify with source: none
Request errors: none
Expectation adapted to available cards: none
