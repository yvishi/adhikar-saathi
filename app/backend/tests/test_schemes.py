"""Offline, table-driven tests for the rules engine (app/backend/schemes.py)."""
import html
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from app.backend import schemes

ROOT = Path(__file__).resolve().parents[3]
SCHEMES = ["e-Shram", "PM-SYM", "PMSBY", "Maternity Benefit"]


def by_scheme(profile):
    res = schemes.match(profile)["matches"]
    assert [m["scheme"] for m in res] == SCHEMES
    return {m["scheme"]: m for m in res}


# A profile that satisfies every checkable rule, used as a base.
BASE = {"age": 30, "monthly_income_inr": 10000, "occupation": "daily_wage",
        "is_epfo_esic_member": False, "is_income_tax_payer": False,
        "gender": "female", "is_pregnant": False}


def prof(**kw):
    return {**BASE, **kw}


# ------------------------------------------------------------ contract shape
def test_shape_and_types():
    for m in schemes.match(BASE)["matches"]:
        assert set(m) == {"scheme", "eligible", "why_en", "why_hi", "card_id", "missing_info"}
        assert m["eligible"] in (True, False, "unknown")
        assert m["why_hi"] is None
        assert isinstance(m["why_en"], str) and m["why_en"].strip()
        assert isinstance(m["missing_info"], list)
        assert m["card_id"] in {"S-01", "S-02", "S-03", "M-01"}


# ------------------------------------------------------------ PM-SYM ages
@pytest.mark.parametrize("age,expected", [
    (17, False), (18, True), (40, True), (41, False), (0, False), (60, False),
])
def test_pmsym_age_boundaries(age, expected):
    assert by_scheme(prof(age=age))["PM-SYM"]["eligible"] is expected


@pytest.mark.parametrize("income,expected", [
    (0, True), (14999, True), (15000, True), (15000.0, True), (15001, False), (15000.5, False), (90000, False),
])
def test_pmsym_income_boundaries(income, expected):
    assert by_scheme(prof(monthly_income_inr=income))["PM-SYM"]["eligible"] is expected


# ------------------------------------------------------------ e-Shram ages
@pytest.mark.parametrize("age,expected", [
    (15, False), (16, True), (17, True), (40, True), (59, True), (60, "unknown"), (75, "unknown"),
])
def test_eshram_age_boundaries(age, expected):
    assert by_scheme(prof(age=age))["e-Shram"]["eligible"] == expected


def test_eshram_age_60_plus_flags_source_conflict():
    m = by_scheme(prof(age=65))["e-Shram"]
    assert m["eligible"] == "unknown"
    assert any("upper age limit" in x for x in m["missing_info"])


@pytest.mark.parametrize("kw,expected", [
    ({"is_epfo_esic_member": True}, False),
    ({"is_income_tax_payer": True}, False),
    ({"is_epfo_esic_member": True, "is_income_tax_payer": True}, False),
    ({"monthly_income_inr": 500000}, True),  # no income criterion for e-Shram
])
def test_eshram_exclusions(kw, expected):
    assert by_scheme(prof(**kw))["e-Shram"]["eligible"] is expected


def test_eshram_true_always_lists_govt_employee_check():
    m = by_scheme(BASE)["e-Shram"]
    assert m["eligible"] is True
    assert any("government employee" in x for x in m["missing_info"])


# ------------------------------------------------------------ PM-SYM EPFO handling
def test_pmsym_epfo_member_is_unknown_not_false():
    m = by_scheme(prof(is_epfo_esic_member=True))["PM-SYM"]
    assert m["eligible"] == "unknown"  # exclusion list is not on the PM-SYM page


def test_pmsym_epfo_member_but_too_old_is_false():
    assert by_scheme(prof(age=45, is_epfo_esic_member=True))["PM-SYM"]["eligible"] is False


def test_pmsym_true_needs_explicit_not_epfo():
    p = dict(BASE)
    del p["is_epfo_esic_member"]
    m = by_scheme(p)["PM-SYM"]
    assert m["eligible"] == "unknown" and "whether you are an EPFO or ESIC member" in m["missing_info"]


def test_pmsym_true_carries_unverified_exclusion_caveat():
    m = by_scheme(BASE)["PM-SYM"]
    assert m["eligible"] is True and m["missing_info"]


# ------------------------------------------------------------ missing / invalid fields
@pytest.mark.parametrize("payload", [{}, None, [], "x", 5, {"age": None}])
def test_empty_or_bad_payload_is_all_unknown_except_nothing_true(payload):
    res = schemes.match(payload)["matches"]
    assert len(res) == 4
    assert all(m["eligible"] == "unknown" for m in res)
    assert all(m["missing_info"] for m in res)


def test_missing_income_unknown_but_definite_no_still_false():
    assert by_scheme({"age": 50})["PM-SYM"]["eligible"] is False
    assert by_scheme({"age": 30})["PM-SYM"]["eligible"] == "unknown"
    assert by_scheme({"monthly_income_inr": 20000})["PM-SYM"]["eligible"] is False


@pytest.mark.parametrize("bad_age", [True, "abc", -3, 121, 30.5, float("nan"), float("inf"), [], {}, "३०", "1e2"])
def test_invalid_age_treated_as_missing(bad_age):
    res = by_scheme(prof(age=bad_age))
    assert res["e-Shram"]["eligible"] == "unknown"
    assert res["PM-SYM"]["eligible"] == "unknown"
    assert "your age in whole years" in res["PM-SYM"]["missing_info"]


@pytest.mark.parametrize("age", [34, 34.0, "34", " 34 "])
def test_age_accepted_forms(age):
    assert by_scheme(prof(age=age))["PM-SYM"]["eligible"] is True


@pytest.mark.parametrize("bad_income", [True, "lots", -1, float("nan"), float("inf"), [], None])
def test_invalid_income_treated_as_missing(bad_income):
    assert by_scheme(prof(monthly_income_inr=bad_income))["PM-SYM"]["eligible"] == "unknown"


@pytest.mark.parametrize("bad_flag", ["true", "false", 1, 0, "yes", None])
def test_non_bool_flags_are_not_trusted(bad_flag):
    # A truthy/falsy non-bool must never produce a definite answer.
    res = by_scheme(prof(is_epfo_esic_member=bad_flag, is_income_tax_payer=bad_flag))
    assert res["e-Shram"]["eligible"] == "unknown"
    assert res["PM-SYM"]["eligible"] == "unknown"


def test_unknown_extra_fields_and_occupation_do_not_change_results():
    a = schemes.match(BASE)
    b = schemes.match({**BASE, "occupation": "nonsense", "surprise": {"x": 1}, "name": "राम"})
    for x, y in zip(a["matches"], b["matches"]):
        assert x["eligible"] == y["eligible"]


# ------------------------------------------------------------ contradictions
def test_male_and_pregnant_is_unknown_with_conflict_message():
    m = by_scheme(prof(gender="male", is_pregnant=True))["Maternity Benefit"]
    assert m["eligible"] == "unknown" and "conflict" in m["why_en"]


def test_multiple_exclusions_all_named():
    m = by_scheme(prof(age=12, is_epfo_esic_member=True, is_income_tax_payer=True))["e-Shram"]
    assert m["eligible"] is False
    assert "12" in m["why_en"] and "EPFO" in m["why_en"] and "income tax" in m["why_en"]


def test_false_beats_unknown():
    # Income tax payer is a definite no even though age and EPFO are missing.
    assert by_scheme({"is_income_tax_payer": True})["e-Shram"]["eligible"] is False


# ------------------------------------------------------------ PMSBY
@pytest.mark.parametrize("profile", [
    BASE, {}, prof(age=10), prof(is_epfo_esic_member=True), prof(age=70), prof(is_income_tax_payer=True)])
def test_pmsby_never_definite(profile):
    m = by_scheme(profile)["PMSBY"]
    assert m["eligible"] == "unknown"
    assert "14434" in m["why_en"]


def test_pmsby_when_not_eshram_eligible_does_not_say_false():
    m = by_scheme(prof(is_income_tax_payer=True))["PMSBY"]
    assert m["eligible"] == "unknown" and "do not qualify for e-Shram" in m["why_en"]


# ------------------------------------------------------------ Maternity
@pytest.mark.parametrize("kw,expected", [
    ({"gender": "female", "is_pregnant": True}, "unknown"),   # never true: establishment rules unverifiable
    ({"gender": "female", "is_pregnant": False}, False),
    ({"gender": "male"}, False),
    ({"gender": "male", "is_pregnant": False}, False),
    ({"gender": "other", "is_pregnant": True}, "unknown"),
    ({"gender": "female"}, "unknown"),
])
def test_maternity(kw, expected):
    base = {k: v for k, v in BASE.items() if k not in ("gender", "is_pregnant")}
    assert by_scheme({**base, **kw})["Maternity Benefit"]["eligible"] == expected


def test_maternity_never_true_for_any_input():
    for g in ("female", "male", "other", None):
        for pr in (True, False, None):
            for ep in (True, False, None):
                m = by_scheme({"gender": g, "is_pregnant": pr, "is_epfo_esic_member": ep})["Maternity Benefit"]
                assert m["eligible"] is not True


def test_maternity_lists_establishment_and_80_day_checks():
    m = by_scheme(prof(gender="female", is_pregnant=True))["Maternity Benefit"]
    joined = " ".join(m["missing_info"])
    assert "10 or more persons" in joined and "80 days" in joined
    assert "12 weeks" not in m["why_en"]  # duration not verified against the 2017 amendment


def test_maternity_esi_warning_when_epfo_esic_member():
    m = by_scheme(prof(gender="female", is_pregnant=True, is_epfo_esic_member=True))["Maternity Benefit"]
    assert "ESI Act" in m["why_en"]


# ------------------------------------------------------------ unicode / hostile input
def test_unicode_and_extra_keys_are_harmless():
    res = schemes.match({"age": 34, "worker_name": "रामू 👷", "occupation": "निर्माण", "gender": "महिला"})
    assert len(res["matches"]) == 4


# ------------------------------------------------------------ rules.json evidence
def test_rule_values_match_verified_facts():
    assert (schemes.PMSYM_MIN_AGE, schemes.PMSYM_MAX_AGE, schemes.PMSYM_MAX_INCOME) == (18, 40, 15000)
    assert schemes.ESHRAM_MIN_AGE == 16 and schemes.ESHRAM_BROCHURE_MAX_AGE == 59


def _norm(s):
    return re.sub(r"\s+", "", s)


def _source_text(path, live):
    p = ROOT / path
    if p.suffix == ".pdf":
        if not shutil.which("pdftotext"):
            pytest.skip("pdftotext not installed")
        out = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(p), "-"],
                             capture_output=True, check=True).stdout.decode("utf-8")
        return _norm(out)
    t = p.read_text(encoding="utf-8", errors="ignore")
    if live:  # text inside HTML comments is not shown to site visitors
        t = re.sub(r"(?s)<!--.*?-->", "", t)
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
    return _norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))


@pytest.mark.parametrize("rule", list(schemes.RULES.values()), ids=lambda r: r["id"])
def test_rule_quotes_exist_in_sources(rule):
    text = _source_text(rule["source_file"], rule["live"])
    for fragment in rule["quote"].split(" ... "):
        assert _norm(fragment) in text, f"{rule['id']}: quote not found in {rule['source_file']}"
