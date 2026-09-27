# Eval summary (system)

Run: 20260927-024837  |  questions evaluated: 30  |  aborted: False

| Metric | System (rights cards + guardrails) | Baseline (same LLM, no corpus) | Better |
|---|---|---|---|
| Behavior accuracy (answer/clarify/refuse as expected) | 29/30 (96.7%) | not run | higher |
| False-refusal rate | 0/21 (0.0%) | not run | lower |
| Refuses out-of-scope questions | 5/5 (100.0%) | not run | higher |
| Answers out-of-scope questions | 0/5 (0.0%) | not run | lower |
| Valid citation on answers | 19/19 (100.0%) | not run | higher |
| Expected card cited | 14/18 (77.8%) | not run | higher |
| Required facts present | 17/18 (94.4%) | not run | higher |
| Forbidden-claim violations (questions) | 1/30 | not run | lower |
| Refuse/clarify with a source attached | 0 | not run | lower |
| Request errors | 0 | not run | lower |
| Latency p50 | 1.60 s | not run | lower |
| Latency p95 | 3.11 s | not run | lower |
| Total cost | Rs 2.06 | not run | lower |

Flagged forbidden claims: Q046
Refuse/clarify with source: none
Request errors: none
Expectation adapted to available cards: none
