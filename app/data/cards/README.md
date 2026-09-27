# Rights cards: provenance

`cards.json` holds 18 cards, all `status: "ready"`, `verified: true`. Every ready card has an `evidence` key: a short verbatim English quote from the source file, checked by script (whitespace-normalised substring match against the text of the file; PDFs via `pdftotext -enc UTF-8`, HTML with comments/scripts/tags removed). `text_hi` is null and `keywords_hi` empty on every card (owner fills these). Read `GAPS.md` before relying on S-03, D-01, or on any Wages Code card.

## Cards

| id | status | source file (in `app/data/sources/`) | evidence (verbatim) |
|---|---|---|---|
| W-01 | ready | wages_code_labourgov.pdf (s.5) | No employer shall pay to any employee wages less than the minimum rate of wages |
| W-02 | ready | wages_code_labourgov.pdf (s.17) | daily basis, at the end of the shift |
| W-03 | ready | wages_code_labourgov.pdf (s.45, s.59) | may be filed within a period of three years |
| W-04 | ready | wages_code_labourgov.pdf (s.18, s.19(4)) | there shall be no deductions from the wages of the employee |
| W-05 | ready | wages_code_labourgov.pdf (s.3, s.4) | employees on the ground of gender in matters relating to wages by the same employer |
| W-06 | ready | wages_code_labourgov.pdf (s.14) | shall not be less than twice the normal rate of wages |
| W-07 | ready | labour_codes_pib.pdf | establishes a statutory right to minimum wages for all employees, extending its coverage to every sector, both organised and unorganised |
| S-01 | ready | eshram_faq.html | Registration on e-Shram portal is free. |
| S-02 | ready | pmsym.html | Entry Age between 18 to 40 years |
| S-03 | ready (hedged) | eshram_intro.pdf | Accidental Insurance cover of 2 Lacs |
| S-04 | ready | labour_gov_doc.pdf | provides for social security to all unorganized workers including domestic workers |
| S-05 | ready | social_security_code_indiacode.pdf (ss.106-108, 7(6)) | has been engaged in any building or other construction work for not less than ninety days during the preceding twelve months |
| M-01 | ready | social_security_code_indiacode.pdf (Ch. VI, ss.59-72) | shall be twentysix weeks of which not more than eight weeks shall precede the expected date of her delivery |
| H-01 | ready | posh_act_2013_english_delhipolice.pdf (ss.2, 6, 9, 11) | has not been constituted due to having less than ten workers or if the complaint is against the employer himself |
| X-01 | ready | eshram_faq.html | Helpdesk Number is 14434/18008896811 (9.00 AM to 6.00 PM - Daily including Sundays) |
| X-02 | ready | app/CONTRACT.md s.9 (meta card, no legal claim) | This is information, not legal advice. |
| D-01 | ready | p_dte.html (news report; p_livelaw_sc.html for the 29 Jan 2025 order) | domestic workers do not require a separate law |
| D-02 | ready | social_security_code_indiacode.pdf (s.2(90), ss.109, 113) | workers employed by households including domestic workers |

## Changes against CONTRACT.md section 5 (owner should know)

1. **Section numbers (Code on Wages), read from the gazette:** minimum wage s.5 (as contract); time of payment s.17 (as contract, plus s.17(2) two working days on exit); deductions s.18 (fine cap s.19(4)); equal pay s.3; overtime s.14; claims and the three-year limit s.45(6); burden of proof on employer s.59. No disagreement with the contract or PIB where they gave numbers.
2. **Maternity (M-01) follows the Code on Social Security, not the Maternity Benefit Act 1961.** `wb_maternity.pdf` is the pre-2017 text (12 weeks) and s.164(1) item 5 of the Code repeals that Act; the Code copy says items 1, 2 and 4 to 9 of s.164(1) came into force on 21 Nov 2025 (footnote to s.1). Chapter VI gives 26 weeks (8 before delivery), 12 weeks for two or more surviving children, 80 days worked, ten or more employees.
3. **S-05 (construction) follows Chapter VIII of the Code on Social Security** (the 1996 Cess Act is repealed by item 8), not the BOCW Act 1996. No benefit amounts appear in the Code, so none are stated.
4. **H-01** uses an English copy of the POSH Act found on a government host (Delhi Police), so it is no longer unverified. It shows domestic workers are covered and how the Local Committee route works.
5. **S-03 is hedged** (older brochure says Rs 2 lakh PMSBY cover; live FAQ says only registration is being done and its PMSBY questions are commented out). **S-01** does not present insurance as a current benefit. **X-01** uses the live-site hours (9 am to 6 pm daily incl. Sundays) and flags the brochure's Mon-Sat 8-8 in `notes`.
6. e-Shram age: live FAQ says 16 or above; brochure says 16-59. Card S-01 says "16 or above".

## Sources added by the corpus agent (retrieved 2026-09-27)

| file in `app/data/sources/` | URL | retrieved | note |
|---|---|---|---|
| social_security_code_indiacode.pdf | https://www.indiacode.nic.in/bitstream/123456789/16823/1/aA2020-36.pdf | 2026-09-27 | India Code copy, "Act 36 of 2020 [As on the 21th November, 2025]"; commencement footnote to s.1. The direct bitstream link worked with a browser User-Agent. |
| posh_act_2013_english_delhipolice.pdf | https://delhipolice.gov.in/doc/POSH/POSH_ActRulesSO.pdf | 2026-09-27 | English Act plus Rules, "Last updated 31-8-2021". Also seen on a second government CDN copy (cdnbbsr.s3waas.gov.in/s3ec055ee0070c40a7c781507b38c59c3e/uploads/2024/09/2024092018.pdf) which was checked but not saved. |

Fetched but NOT kept or used: a DGFASLI copy of the BOCW Act 1996 (https://www.dgfasli.gov.in/public/Admin/Cms/AllPdf//65a1324d47cfa9.78419508.pdf), because Chapter VIII of the Code on Social Security is the current provision. Blocked or failed: wcd.nic.in (DNS), doe.gov.in (TLS), wblc.gov.in (timeout), vvgnli.gov.in (404), indiacode.nic.in BOCW bitstream (504).

Not used as evidence: `wages_code_prs.pdf` (bill as introduced), `posh_ilo_hindi.pdf` (legacy Hindi font, unreadable), `wb_maternity.pdf` (superseded), `prs_socsec.html` (background only).

## Re-running the check

`python app/data/cards/validate_cards.py` (needs `pdftotext` on PATH). Rule: for each ready card, `evidence` (whitespace-normalised) must be a substring of the normalised text of `source.file`. The script has the project root hard-coded at the top (`ROOT`).
