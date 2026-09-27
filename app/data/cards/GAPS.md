# Gaps, conflicts and manual downloads

No card is `skipped`. These are the things the owner should still know or fix, most important first.

## 1. Conflicts inside the sources

- **e-Shram PMSBY accident cover (S-03, S-01).** `eshram_intro.pdf` (item 8) says registered workers "will get an Accidental Insurance cover of 2 Lacs under PMSBY". The live FAQ (`eshram_faq.html`) Q42 says "Right now, only registration is being done through e-Shram", and every PMSBY question (Q21, Q40, Q51) sits inside an HTML comment, i.e. withdrawn. S-03 is therefore written as a hedge ("older material says..., current FAQ says..., confirm with 14434"). To remove the hedge, get written confirmation from the Ministry or helpdesk.
- **e-Shram helpdesk hours (X-01).** Live site: 9.00 AM to 6.00 PM, daily including Sundays. Brochure: Monday to Saturday, 8am to 8pm. Card uses the live wording.
- **e-Shram age band (S-01).** Live FAQ Q11: 16 years or above. Brochure: 16-59. Card says 16 or above.
- **Supreme Court report on POSH coverage (D-01 vs H-01).** `p_livelaw_sc.html` says the court noted domestic workers "stand excluded" from the 2013 sexual harassment Act. The Act text itself (s.2(a)(ii), 2(e), 2(g)(iv), 2(o)(vi), 11(1)) covers women employed in a dwelling place or house, and gives domestic workers a Local Committee/police route. H-01 follows the Act. D-01 does not repeat the news claim.

## 2. Things checked only in secondary or indirect form

- **Code on Wages commencement.** The gazette file (Aug 2019) does not say when the Code came into force, and the PIB explainer (23 Nov 2025) does not state a date. The Code on Social Security copy states its own commencement (21 Nov 2025, S.O. 5319(E)). A web search result said the Wages Code notification is S.O. 5322 of 21 Nov 2025 and that some sub-sections of the Wages Code and Social Security Code are still not notified; I could not fetch it. **Owner: download the Ministry of Labour notification bringing the Code on Wages into force (labour.gov.in "Gazette Notification" page, or the PIB release PRID=2192463 which blocks automated fetches) and save as `app/data/sources/wages_code_commencement_notification.pdf`; check that sections 3, 5, 14, 17, 18, 19, 45 and 59 are among the sections in force.** For the Code on Social Security every section cited by the cards (2, 7, 59-72, 100-113) is listed as in force in the footnote to s.1 of the saved copy.
- **D-01 rests on news reports** (Down To Earth 18 Jan 2026, LiveLaw 29 Jan 2025), not the judgment or the committee report. Owner should download: the Supreme Court judgment in Ajay Mallik v State of Uttarakhand, SLP(Crl) 8777/2022 (order of 29 Jan 2025, from the Supreme Court website; suggested name `sc_ajay_mallik_2025_domestic_workers.pdf`) and the expert committee report of July 2025 from the Ministry of Labour and Employment (suggested name `domestic_workers_committee_report_2025.pdf`). I do not have their URLs.
- **W-07** is from the PIB explainer only; the operative rule is s.5 (W-01, gazette).

## 3. Not covered (left out on purpose, no source)

- State-wise minimum wage rates. No card states any figure. Manual: each state Labour Department's current notification (URL differs per state).
- PM-SYM contribution chart (amounts by age) and PM-SYM exclusions (EPFO/ESIC/NPS members). Manual: the Contribution Chart and FAQs of PM-SYM pages on maandhan.in (save as `pmsym_contribution_chart.html`, `pmsym_faq.html`).
- BOCW benefit amounts (pension, accident, education, maternity assistance) and state welfare board schemes. The Code on Social Security only says benefits are "as may be prescribed"; amounts are in state schemes or central rules. Manual: your state Building and Other Construction Workers' Welfare Board scheme list.
- Whether the Building and Other Construction Workers (Regulation of Employment and Conditions of Service) Act 1996 was subsumed by the OSH Code from 21 Nov 2025 (the Cess Act repeal is verified in the Social Security Code; the 1996 regulation Act was not checked). Manual: the repeal section of the Occupational Safety, Health and Working Conditions Code, 2020 gazette (India Code), save as `osh_code_2020_indiacode.pdf`.
- Rules made under the Codes (for example the Code on Wages Rules; rules for maternity notice forms, wage slips). Cards use only the Acts.
- POSH: the Sexual Harassment of Women at Workplace Rules 2013 and any state helpline or the SHe-Box portal. Not in a saved file, so no phone number or portal is named. H-01 cites `s.11(1)`'s police route; that section still names section 509 IPC (now replaced by the Bharatiya Nyaya Sanhita), which the card avoids repeating.
- Maternity: medical bonus (Rs 3,500), adoption/commissioning mother (12 weeks), miscarriage leave (6 weeks) and creche (50 employees) are in Chapter VI of the Code but were left out of M-01 to keep it short. Add a separate `X-` card if wanted.

## 4. Card-specific cautions

- M-01: applicability is limited to factories, mines, plantations and shops/establishments with ten or more employees (plus others the government notifies). Many casual and domestic workers will not qualify; the card says so and points to unorganised-worker schemes (s.109(1)(ii)).
- S-05: the Code's definition of "building or other construction work" (s.2(6)) excludes some small works. The card tells the worker to ask the Welfare Board.
- D-02: "wage worker" in the Code carries a monthly wage limit "as may be notified"; the amount is not known.
- X-02 has no external source; its `evidence` line is from CONTRACT.md s.9.
