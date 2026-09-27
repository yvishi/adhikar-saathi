"""Deterministic wage-claim letter template (English + Hindi). No LLM, no network.

Legal basis (see app/data/schemes/rules.json, COW_* rules): Code on Wages, 2019,
s.43 (employer must pay), s.45(1) (authority appointed by the appropriate Government),
s.45(4) (employee may apply), s.45(6) (three years). Missing fields stay as
placeholders: nothing is invented. Hindi strings are listed in
app/data/hindi_review/schemes.md and are NEEDS-REVIEW.
"""
from __future__ import annotations

import math
import re
from datetime import date, datetime

PH = "[ ____ ]"
MAX_DETAILS = 1000
MAX_FIELD = 200
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")

_LABELS = {
    "worker_name": "worker name",
    "state": "state",
    "employer_name": "employer name",
    "work_type": "type of work",
    "wage_owed_inr": "amount of wages owed",
    "period_from": "start date of the period",
    "period_to": "end date of the period",
}


def _text(v, limit=MAX_FIELD):
    if v is None or isinstance(v, (bool, dict, list)):
        return ""
    s = _CTRL.sub("", str(v)).strip()
    return s[:limit]


def _amount(v):
    """Positive finite number -> display string like '12,500', else ''."""
    if isinstance(v, bool):
        return ""
    if isinstance(v, str):
        try:
            v = float(v.replace(",", "").strip())
        except ValueError:
            return ""
    if not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 < v < 1e10:
        return ""
    whole, frac = divmod(round(float(v), 2), 1)
    s = str(int(whole))
    if len(s) > 3:  # Indian digit grouping: 12,34,567
        head, tail = s[:-3], s[-3:]
        head = re.sub(r"(\d)(?=(\d\d)+$)", r"\1,", head)
        s = head + "," + tail
    if frac:
        s += f".{int(round(frac * 100)):02d}"
    return s


def _parse_date(s):
    for f in _DATE_FORMATS:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    return None


def draft(fields: dict, *, today: date | None = None) -> dict:
    f = fields if isinstance(fields, dict) else {}
    name = _text(f.get("worker_name"))
    state = _text(f.get("state"))
    employer = _text(f.get("employer_name"))
    work = _text(f.get("work_type"))
    amount = _amount(f.get("wage_owed_inr"))
    p_from = _text(f.get("period_from"))
    p_to = _text(f.get("period_to"))
    raw_details = _text(f.get("details"), limit=MAX_DETAILS + 1)
    details = raw_details[:MAX_DETAILS]

    n, st, em, wk = name or PH, state or PH, employer or PH, work or PH
    am = f"Rs {amount}" if amount else f"Rs {PH}"
    am_hi = f"₹{amount}" if amount else f"₹{PH}"
    pf, pt = p_from or PH, p_to or PH

    en = [
        "To,",
        "The Authority appointed under the Code on Wages, 2019",
        f"State: {st}",
        "",
        "Subject: Application for payment of unpaid wages (claim under section 45 of the Code on Wages, 2019)",
        "",
        "Respected Sir/Madam,",
        "",
        f"I, {n}, worked as {wk} for {em}, from {pf} to {pt}.",
        f"Wages of {am} for this period have not been paid to me.",
    ]
    if details:
        en.append(f"Details: {details}")
    en += [
        "",
        "I request that the authority direct my employer to pay the wages due to me, as required by the "
        "Code on Wages, 2019. I am ready to give any documents or information needed.",
        "",
        "Yours faithfully,",
        n,
        f"Date: {PH}",
        f"Address and phone number: {PH}",
    ]

    hi = [
        "सेवा में,",
        "प्राधिकारी (मजदूरी संहिता, 2019 के अंतर्गत नियुक्त)",
        f"राज्य: {st}",
        "",
        "विषय: बकाया मजदूरी के भुगतान के लिए आवेदन",
        "",
        "महोदय/महोदया,",
        "",
        f"मैं {n}, {em} के यहाँ {wk} का काम करता/करती थी। मैंने {pf} से {pt} तक काम किया।",
        f"इस अवधि की मेरी {am_hi} की मजदूरी मुझे अभी तक नहीं मिली है।",
    ]
    if details:
        hi.append(f"विवरण: {details}")
    hi += [
        "",
        "मेरा निवेदन है कि मेरे नियोक्ता से मेरी बकाया मजदूरी दिलवाई जाए। मैं ज़रूरी कागज़ात देने को तैयार हूँ।",
        "",
        "भवदीय,",
        n,
        f"तारीख: {PH}",
        f"पता और फ़ोन नंबर: {PH}",
    ]

    notes = [
        "This is a template and not legal advice. You must read, correct and approve it yourself; this app "
        "never sends or files anything.",
    ]
    empty = [label for key, label in _LABELS.items()
             if not {"wage_owed_inr": amount, "worker_name": name, "state": state, "employer_name": employer,
                     "work_type": work, "period_from": p_from, "period_to": p_to}[key]]
    if empty:
        notes.append("Fill every " + PH + " before use. Missing now: " + ", ".join(empty)
                     + ". Also add the date, your address and phone number.")
    else:
        notes.append("Add the date, your address and phone number where marked " + PH + ".")
    notes += [
        "Authority: under the Code on Wages, 2019 (section 45), claims are heard by an authority that your "
        "State or the Central Government appoints by notification (a Gazetted Officer or above). The Code "
        "names no office or address, so find the correct office for your state and area (for example "
        "through the district or state labour department) and write its name and address at the top.",
        "The Code text we checked does not fix a form for one worker's claim (it leaves forms and procedure "
        "details to rules), so ask the labour office whether your state requires a particular format.",
        "Time limit: the application may be filed within three years from the date the claim arises "
        "(section 45(6)); a later application can be accepted only if you show sufficient cause for the delay.",
        "Attach copies of what you have: attendance or muster record, payment slips or messages, bank or "
        "UPI records, any written agreement, ID proof, and notes of who owes what and since when.",
        "Check the amount and the dates yourself. Do not sign or send anything you are not sure is correct.",
        "Keep a copy of the letter and of everything you attach, and ask for a stamped acknowledgement or "
        "keep proof of how and when you submitted it.",
        "Once a claim is filed for non-payment or less payment, the Code (section 59) puts the burden of "
        "proving the dues were paid on the employer.",
        "The Hindi text (draft_hi) is NEEDS-REVIEW: it has not been checked by a Hindi reader; the "
        "English text is the reference.",
    ]
    if raw_details and len(raw_details) > MAX_DETAILS:
        notes.append(f"Your details were cut to {MAX_DETAILS} characters; check that nothing important is missing.")

    d_from, d_to = _parse_date(p_from), _parse_date(p_to)
    if (p_from and not d_from) or (p_to and not d_to):
        notes.append("A date could not be read (use DD/MM/YYYY or YYYY-MM-DD); check the period in the letter.")
    if d_from and d_to and d_from > d_to:
        notes.append("The start date is later than the end date; correct the period.")
    if d_to and (today or date.today()) > _plus_years(d_to, 3):
        notes.append("The end of your claim period is more than three years ago. The time limit runs from "
                     "when the claim arose, so it may still be in time, otherwise you must explain the "
                     "delay in the application; check with the labour office.")

    return {
        "draft_en": "\n".join(en),
        "draft_hi": "\n".join(hi),
        "notes_en": notes,
        "requires_human_review": True,
    }


def _plus_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + years, day=28)
