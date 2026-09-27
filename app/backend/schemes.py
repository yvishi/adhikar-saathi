"""Deterministic scheme eligibility checker (no LLM, no network).

Every threshold comes from app/data/schemes/rules.json, where each rule keeps its
source file and a verbatim quote. Rule ids used below are the ids in that file.
Anything the sources do not settle returns eligible="unknown", never a silent true.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

_RULES_PATH = Path(__file__).resolve().parents[1] / "data" / "schemes" / "rules.json"
RULES = {r["id"]: r for r in json.loads(_RULES_PATH.read_text(encoding="utf-8"))["rules"]}

ESHRAM_MIN_AGE = RULES["ESHRAM_AGE_MIN"]["value"]                # 16
ESHRAM_BROCHURE_MAX_AGE = RULES["ESHRAM_AGE_BAND_BROCHURE"]["value"]["max"]  # 59
PMSYM_MIN_AGE = RULES["PMSYM_AGE"]["value"]["min"]               # 18
PMSYM_MAX_AGE = RULES["PMSYM_AGE"]["value"]["max"]               # 40
PMSYM_MAX_INCOME = RULES["PMSYM_INCOME"]["value"]                # 15000

HELPLINE = "helpline 14434"

# Human-readable labels used in missing_info.
M_AGE = "your age in whole years"
M_INCOME = "your monthly income in rupees"
M_EPFO = "whether you are an EPFO or ESIC member"
M_TAX = "whether you pay income tax"
M_GENDER = "your gender"
M_PREG = "whether you are pregnant"


# ---------------------------------------------------------------- input cleaning
def _age(v):
    """Whole years 0-120 -> int, else None (missing or not understood)."""
    if isinstance(v, bool):
        return None
    if isinstance(v, str):
        v = v.strip()
        if not v.isascii() or not v.isdigit():
            return None
        v = int(v)
    if isinstance(v, float):
        if not math.isfinite(v) or v != int(v):
            return None
        v = int(v)
    if isinstance(v, int) and 0 <= v <= 120:
        return v
    return None


def _income(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, str):
        try:
            v = float(v.strip())
        except ValueError:
            return None
    if isinstance(v, (int, float)) and math.isfinite(v) and v >= 0:
        return v
    return None


def _flag(v):
    return v if isinstance(v, bool) else None


def _gender(v):
    v = v.strip().lower() if isinstance(v, str) else None
    return v if v in ("female", "male", "other") else None


def _clean(profile):
    p = profile if isinstance(profile, dict) else {}
    occ = p.get("occupation")
    return {
        "age": _age(p.get("age")),
        "income": _income(p.get("monthly_income_inr")),
        "epfo": _flag(p.get("is_epfo_esic_member")),
        "tax": _flag(p.get("is_income_tax_payer")),
        "gender": _gender(p.get("gender")),
        "pregnant": _flag(p.get("is_pregnant")),
        "occupation": occ if occ in ("daily_wage", "construction", "domestic", "other") else None,
    }


def _yn(b):
    return "yes" if b else "no"


def _rupees(x):
    return f"Rs {int(x)}" if float(x).is_integer() else f"Rs {x}"


def _out(scheme, eligible, why, card_id, missing=()):
    return {"scheme": scheme, "eligible": eligible, "why_en": why, "why_hi": None,
            "card_id": card_id, "missing_info": list(missing)}


# ---------------------------------------------------------------- e-Shram
def _eshram(p):
    age, epfo, tax = p["age"], p["epfo"], p["tax"]
    no = []
    if age is not None and age < ESHRAM_MIN_AGE:
        no.append(f"you are {age}, below the minimum registration age of {ESHRAM_MIN_AGE}")
    if epfo is True:
        no.append("you are an EPFO/ESIC member, and e-Shram is for unorganised workers who are not")
    if tax is True:
        no.append("you pay income tax, and e-Shram says the worker should not be an income tax payee")
    if no:
        return _out("e-Shram", False, "Not eligible for e-Shram registration because "
                    + " and ".join(no) + ".", "S-01")

    missing = []
    if age is None:
        missing.append(M_AGE)
    if epfo is None:
        missing.append(M_EPFO)
    if tax is None:
        missing.append(M_TAX)
    age_conflict = age is not None and age > ESHRAM_BROCHURE_MAX_AGE
    if age_conflict:
        missing.append(f"the upper age limit: the e-Shram brochure says 16-{ESHRAM_BROCHURE_MAX_AGE} but the "
                       f"current FAQ says 16 or above, so ask the {HELPLINE}")
    if missing:
        why = ("e-Shram needs age 16-59 (brochure), not an EPFO/ESIC member and not an income tax payer, "
               "so we cannot say yet")
        if age_conflict:
            why += f"; at age {age} the two e-Shram documents disagree on the upper age limit"
        return _out("e-Shram", "unknown", why + ".", "S-01", missing)

    return _out("e-Shram", True,
                f"You appear to meet the e-Shram conditions (age 16-59, not an EPFO/ESIC member, not an "
                f"income tax payer) from your answers: age {age}, EPFO/ESIC member {_yn(epfo)}, "
                f"income tax payer {_yn(tax)}.", "S-01",
                ["confirm you are not a government employee (not asked here)"])


# ---------------------------------------------------------------- PM-SYM
def _pmsym(p):
    age, inc, epfo = p["age"], p["income"], p["epfo"]
    no = []
    if age is not None and age < PMSYM_MIN_AGE:
        no.append(f"your age {age} is below the entry age of {PMSYM_MIN_AGE}")
    if age is not None and age > PMSYM_MAX_AGE:
        no.append(f"your age {age} is above the entry age limit of {PMSYM_MAX_AGE}")
    if inc is not None and inc > PMSYM_MAX_INCOME:
        no.append(f"your monthly income {_rupees(inc)} is above the limit of Rs {PMSYM_MAX_INCOME}")
    if no:
        return _out("PM-SYM", False, "Not eligible for PM-SYM because " + " and ".join(no)
                    + " (entry age 18-40, monthly income up to Rs 15000).", "S-02")

    missing = []
    if age is None:
        missing.append(M_AGE)
    if inc is None:
        missing.append(M_INCOME)
    if epfo is None:
        missing.append(M_EPFO)
    if missing:
        return _out("PM-SYM", "unknown",
                    "PM-SYM needs entry age 18-40, monthly income up to Rs 15000 and an unorganised "
                    "worker, so we cannot say yet.", "S-02", missing)
    if epfo is True:
        return _out("PM-SYM", "unknown",
                    "Your age and income fit PM-SYM (18-40, up to Rs 15000), but it is for unorganised "
                    "workers and you said you are an EPFO/ESIC member, and the PM-SYM page does not state "
                    f"whether that rules you out, so ask the {HELPLINE} or a Common Service Centre.",
                    "S-02", ["whether an EPFO/ESIC member can join PM-SYM"])
    return _out("PM-SYM", True,
                f"You meet the PM-SYM conditions listed on the scheme page (entry age 18-40, monthly income "
                f"up to Rs 15000) from your answers: age {age}, income {_rupees(inc)}, EPFO/ESIC member "
                f"{_yn(epfo)}.", "S-02",
                ["the PM-SYM page we have lists no other exclusions (for example other pension "
                 f"schemes): confirm at a Common Service Centre or the {HELPLINE} when enrolling"])


# ---------------------------------------------------------------- PMSBY
def _pmsby(p, eshram):
    # Always unknown: see PMSBY_LIVE_FAQ_ONLY_REGISTRATION in rules.json.
    conflict = ("The e-Shram brochure says registration gives Rs 2 lakh accident cover under PMSBY, but the "
                "current e-Shram FAQ says only registration is being done and no longer mentions PMSBY")
    if eshram["eligible"] is False:
        why = (conflict + f"; you do not qualify for e-Shram, and this source gives no other route, "
               f"so ask the {HELPLINE} how to get accident cover.")
        missing = []
    else:
        why = conflict + f", so confirm with the {HELPLINE} that the cover applies to you now."
        missing = [m for m in eshram["missing_info"] if not m.startswith(("confirm", "the upper age"))]
        missing.append("whether e-Shram registration currently gives PMSBY cover")
        if eshram["eligible"] == "unknown":
            why = "First check e-Shram eligibility. " + why
    return _out("PMSBY", "unknown", why, "S-03", missing)


# ---------------------------------------------------------------- Maternity Benefit
def _maternity(p):
    g, preg, epfo, occ = p["gender"], p["pregnant"], p["epfo"], p["occupation"]
    if g == "male" and preg is True:
        return _out("Maternity Benefit", "unknown",
                    "Your answers conflict (male and pregnant), so no check was done; please correct them.",
                    "M-01", ["your gender", "whether you are pregnant"])
    if preg is False:
        return _out("Maternity Benefit", False,
                    "This indicative check is only for a current pregnancy and you said you are not pregnant; "
                    f"if you delivered or miscarried recently, ask the {HELPLINE} or your labour office.",
                    "M-01")
    if g == "male":
        return _out("Maternity Benefit", False,
                    "The Maternity Benefit Act regulates the employment of women around childbirth, "
                    "and you gave your gender as male.", "M-01")

    missing = []
    if g is None:
        missing.append(M_GENDER)
    if preg is None:
        missing.append(M_PREG)
    missing += [
        "whether your workplace is a factory, mine, plantation, circus or a shop/establishment with 10 "
        "or more persons",
        "whether you actually worked at least 80 days with this employer in the 12 months before the "
        "expected delivery",
    ]
    why = ("Indicative only: the Maternity Benefit Act covers certain establishments and needs at least "
           "80 days actually worked in the 12 months before delivery, which we cannot check from your answers.")
    if occ == "daily_wage":
        why += " Being a casual or daily-wage worker is not by itself a bar, per a Supreme Court quote in the Act's FAQ."
    if epfo is True:
        why += (" The Act does not apply to establishments covered by the ESI Act, and you said you are an "
                f"EPFO/ESIC member, so ask ESIC or the {HELPLINE} which maternity rules apply to you.")
        missing.append("whether your workplace is covered by the ESI Act")
    return _out("Maternity Benefit", "unknown", why, "M-01", missing)


# ---------------------------------------------------------------- public API
def match(profile: dict) -> dict:
    p = _clean(profile)
    eshram = _eshram(p)
    return {"matches": [eshram, _pmsym(p), _pmsby(p, eshram), _maternity(p)]}
