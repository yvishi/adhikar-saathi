# Hindi review index: read in this order

"Strings" = lines carrying Devanagari text (approximate: a table row or list item is one string; some rows hold two).

| Priority | File | What it is | Strings (approx.) | Why this order |
|---|---|---|---|---|
| 1 | (not a file) the Hindi ANSWERS from a real run: `answer_hi` in `app/eval/results/*/results.jsonl` (`dev2`, `heldout/system`) | What users actually hear and read | about 60 answers | These are the product. Check meaning, correctness against the card, and tone. |
| 2 | `eval.md` | The 60 eval questions and the Hindi words inside the grading regexes | 142 | Questions decide whether the metrics mean anything; a wrong regex causes false misses/violations. |
| 3 | `backend-core.md` | Error messages, the fixed refusal text (`REFUSE_HI`), mock texts | 15 | `REFUSE_HI` is spoken on every refusal; error messages appear on failures. |
| 4 | `frontend.md` | Every UI label, error and notice | 126 | Every user reads these; includes the legal and privacy notices. |
| 5 | `schemes.md` | The Hindi wage-claim letter template (`draft_hi`) | 13 | A user may print and hand this over; must be checked before it is used. |
| 6 | `integration.md` | One changed UI label plus script/test strings | 6 items | Small; the label change is in the schemes flow. |
| 7 | `retrieval.md` | Glossary that maps Hindi/Hinglish words to English search terms | 327 | Never shown to users; an error only causes a wrong card to be retrieved. |
| - | `corpus.md` | Says the cards have no Hindi | 0 | Nothing to review. |
