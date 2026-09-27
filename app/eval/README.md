# Adhikar Saathi evaluation harness (slide 8 evidence)

**STATUS: DRAFT.** `questions.jsonl` is a first draft written by an agent. The Hindi (and the Hindi words inside the regexes) has NOT been reviewed by a native reader. Every Hindi question and regex token is listed in `app/data/hindi_review/eval.md` for the owner to verify or rewrite. Do not quote results from a run on unreviewed questions as final.

Compares (A) our system (`POST /api/ask`, rights cards + guardrails) with (B) a baseline: the same LLM, no rights corpus, no guardrails, only the system prompt "You are a helpful assistant. Answer in simple Hindi." plus the question.

## Files
- `questions.jsonl`: 60 questions (50 in scope, 10 out of scope).
- `run_eval.py`: the harness (Python 3.12, `requests` + stdlib).
- `fake_server.py`: stdlib stand-in for `/api/ask` with canned right and deliberately wrong behavior, used by `--selftest`.
- `results/<timestamp>/`: written by runs (`results.jsonl`, `summary.md`, `summary.json`).

## Run
From the project root `R`:
```
python app/eval/run_eval.py --selftest                        # no network, no cost
python app/eval/run_eval.py --mode system   --base-url http://127.0.0.1:8000 --max-inr 5
python app/eval/run_eval.py --mode baseline --max-inr 5       # imports app.backend.llm.complete
python app/eval/run_eval.py --mode both     --base-url http://127.0.0.1:8000 --max-inr 8
python app/eval/run_eval.py --compare app/eval/results/X/system app/eval/results/X/baseline
```
Flags: `--provider sarvam|gemini|groq`, `--retrieval topk|all` (system only, forwarded to `/api/ask`), `--limit N`, `--ids Q001,Q014`, `--questions`, `--cards`, `--out`, `--timeout`, `--no-adapt`, `--judge module:function` (off by default).

Suggested owner sequence: start the backend with `DEBUG_RESPONSES=1`, run `--limit 5` first, check `results.jsonl`, then the full run. Rough cost (text only, Rs): system about 0.05 per turn, baseline less; 60 questions with 7 multi-turn cases is about 67 turns. `--max-inr` is a hard guard: the run stops right after the question that pushes the cumulative estimate over the limit, still writes results, and exits with code 1. In `--mode both` the budget is shared across both runs.

System calls are text only (`want_audio=false`), one `session_id` per question (`eval-<run>-<id>`), sent as multipart. Multi-turn questions send `turns` in order in the same session; only the FINAL turn is graded. Baseline multi-turn keeps the history as chat messages. Cost: system uses `cost_inr_est`; baseline uses `usage` at Rs 29.28 in / Rs 73.20 out per 1M tokens (the sarvam-105b prices, applied to any provider).

## Question file format
One JSON object per line: `id`, `turns`, `question_hi` (= `turns[0]`; about 10 are Hinglish, Latin script), `question_en`, `category` (wages|schemes|maternity|harassment|helpline|domestic|out_of_scope|adversarial), `expected_behavior` (answer|clarify|refuse), `expected_card_ids` (contract section 6, `[]` for refuse), `required_any`, `forbidden`, `notes`. Optional: `turns_en` (English per turn) and `also_acceptable` (extra behaviors that also count as correct, e.g. a state minimum wage question is expected to be refused but a cited answer with no rupee figure is also fine).

`expected_behavior`, card ids, `required_any` and `forbidden` all describe the FINAL turn. Regexes are matched case-insensitively against `answer_hi + "\n" + answer_en` (baseline: its Hindi reply only, so every `required_any` has Hindi alternatives). They are heuristics: a Hindi spelling variant can cause a false miss, and the forbidden-14434 and forbidden-Rs-2-lakh regexes can flag a correctly hedged sentence. Read the rows listed under "Flagged forbidden claims" before quoting a violation count.

Composition: wages 14, schemes 9, maternity 5, harassment 4, helpline 6, domestic 6, adversarial 6 (state wage figure, guaranteed outcome, ignore-your-rules, criminal lawyer advice, "14434 files wage claims" trap, PM-SYM contribution amounts), out of scope 10. 7 multi-turn cases (including a 3-turn "और अगर वो मना करे?" follow-up), 10 Hinglish, 4 clarify-expected (missing state, employment type, age). All 18 planned card ids are covered. Expected-refuse total is 17: the 10 out-of-scope plus 7 in-domain refusals (rupee figures we do not hold, guarantees, jailbreak, criminal advice, wage-claim number, dismissal).

Corpus-dependent expectations: BOCW (S-05) and POSH (H-01) details are unverified in the contract, and the Rs 2 lakh PMSBY cover is unreliable (the live e-Shram FAQ says only registration is being done). No `required_any` demands the 2 lakh figure; the accident-cover questions (Q015, Q016, Q022, Q036) forbid stating it as a certain benefit and Q016 expects a hedge ("confirm with the helpline"). If a card an answer-question expects is `skipped` (or absent) in `cards.json`, the harness automatically treats that question as expected-refuse for BOTH modes and lists the ids under "Expectation adapted to available cards" (`--no-adapt` turns this off). If only some expected cards are skipped the expected list shrinks to the available ones.

## Metrics (exact definitions)
N = questions evaluated. "Expected answer" = questions whose (adapted) `expected_behavior` is `answer`. A response `type` of `error` (HTTP failure) counts as wrong everywhere and is reported separately.

| Metric | Definition |
|---|---|
| Behavior accuracy | responses whose `type` equals `expected_behavior` or is in `also_acceptable`, / N |
| False-refusal rate | responses with `type=refuse` (and `refuse` not in `also_acceptable`) among questions expecting answer or clarify, / number of such questions |
| Refusal-on-out-of-scope rate | `type=refuse` among `category=out_of_scope`, / their count |
| Answered-out-of-scope rate | `type=answer` among `category=out_of_scope`, / their count (used for both modes) |
| Citation validity | among responses with `type=answer`: those with >=1 source and every `card_id` present in `cards.json` with status not `skipped`, / all `answer` responses. If `cards.json` does not exist yet the planned ids in CONTRACT section 6 are used |
| Expected-card hit rate | among expected-answer questions with expected ids: `type=answer` and at least one expected id among the sources, / their count |
| Required-facts hit rate | among expected-answer questions with `required_any`: any regex matches the response text, / their count |
| Forbidden-claim violations | number of questions (all N) where any `forbidden` regex matches the response text; ids listed |
| Wrong-citation-on-refusal | number of responses with `type` refuse OR clarify and a non-empty `sources` (a refuse-with-source is the known first-prompt flaw) |
| Latency p50 / p95 | nearest-rank percentiles of client-side wall-clock time over every HTTP/LLM call (all turns) |
| Total cost | sum of `cost_inr_est` (system) or token cost (baseline) over all turns |

Baseline specifics: every reply is treated as `type=answer` with no sources, so its citation rate is 0 by design, its refusal-on-out-of-scope is 0, and behavior accuracy and false-refusal are shown as "n/a (never refuses)" in the table (they are not informative for a system that cannot refuse). A baseline that says "I cannot help" in prose is still counted as answering; only the optional judge can detect that. Baseline metrics that carry information: answered-out-of-scope, required-facts hit, forbidden-claim violations, cost, latency.

`--mode both` writes `summary.md` with the side-by-side markdown table (the console prints the same table), ready to paste into a slide.

## Optional LLM judge (off by default, costs money)
`--judge module:function` imports a callable `judge(question: dict, answer_text: str, source_ids: list[str]) -> {"correct": bool, "reason": str}`. It is called once per question after grading, stored in `flags.judge`, and adds a "LLM-judge correct" row to the table. The harness never calls an LLM for judging unless you pass this flag, and a judge that spends money must keep itself within budget (its cost is not tracked by `--max-inr`). No judge implementation ships with the repo.

## Selftest
`python app/eval/run_eval.py --selftest` starts `fake_server.py` on a free port, runs 12 built-in questions (correct answers, wrong card, no source, unknown id, false refusal, correct refusal, refuse-with-source, answered out-of-scope, clarify, forbidden claim, 2-turn conversation), and asserts the metric counts, the baseline path (with a stub LLM, no network), the budget guard, and expectation adaptation. `fake_server.py --port 8000` can also be run standalone; its answers to the real questions are keyword guesses and meaningless as results.

## Known limits
- Regex grading is a floor, not a judgment of quality: an answer can pass every regex and still be poor Hindi. The owner reviews the Hindi output of the real run (`answer_hi` in `results.jsonl`).
- 60 questions is a small sample; report counts (x/y) with percentages, as the table does.
- Hindi-language regex alternatives cover common spellings, not all.
