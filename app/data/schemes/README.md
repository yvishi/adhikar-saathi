# Scheme rules and evidence

`rules.json` is the single source of truth for `app/backend/schemes.py` (eligibility) and the legal facts in `app/backend/complaint.py`. Each rule has an id, a plain statement, `source_file`, and a verbatim `quote`. `kind`:

- `encoded`: used as a hard rule (thresholds are read from `value` in code).
- `note`: used only in wording.
- `not_encoded`: seen in a source but deliberately not used, with the reason.

`live: false` means the text is inside an HTML comment on the source page (not shown to visitors).

`app/backend/tests/test_schemes.py::test_rule_quotes_exist_in_sources` re-checks every quote against the files in `app/data/sources/` (PDFs need `pdftotext` on PATH, otherwise those cases skip).

## Design choices

- No LLM, no network: plain code. Unknown or unusable input (missing, wrong type, out of range, non-bool flags) gives `"unknown"` with `missing_info`, never a silent true.
- A definite `false` is returned only where a verified rule fails, even if other fields are missing.
- `PMSBY` is always `"unknown"`: the 2021 brochure says e-Shram registration gives Rs 2 lakh cover, but the current FAQ says only registration is being done and has all PMSBY questions commented out.
- `Maternity Benefit` is never `true`: the profile has no establishment size/type or days-worked fields. The West Bengal copy is an older text; duration and amounts are not stated.
- `occupation` is not used in any rule (no verified rule depends on it; it only adds one sentence for `daily_wage` in the maternity wording).
- `missing_info` entries are plain English phrases for display, not field names.

## Refresh procedure

If a source is updated, edit the rule and its quote in `rules.json`, then run the tests: a stale quote fails.
