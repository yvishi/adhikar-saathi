"""Offline tests for the wage-claim letter template (app/backend/complaint.py)."""
from datetime import date

import pytest

from app.backend import complaint

PH = "[ ____ ]"
FULL = {"worker_name": "Ramesh Kumar", "state": "Bihar", "employer_name": "Shree Builders",
        "work_type": "mason", "wage_owed_inr": 12500, "period_from": "2025-01-01",
        "period_to": "2025-03-31", "details": "Employer said he would pay next week."}
TODAY = date(2026, 9, 27)


def d(fields, **kw):
    return complaint.draft(fields, today=TODAY, **kw)


def test_shape():
    r = d(FULL)
    assert set(r) == {"draft_en", "draft_hi", "notes_en", "requires_human_review"}
    assert r["requires_human_review"] is True
    assert isinstance(r["notes_en"], list) and all(isinstance(x, str) for x in r["notes_en"])


def test_full_fields_appear_and_no_placeholder_except_date_and_contact():
    r = d(FULL)
    for s in ("Ramesh Kumar", "Bihar", "Shree Builders", "mason", "Rs 12,500", "2025-01-01",
              "2025-03-31", "Employer said he would pay next week."):
        assert s in r["draft_en"]
    assert r["draft_en"].count(PH) == 2  # date, address/phone
    assert "Authority appointed under the Code on Wages, 2019" in r["draft_en"]
    assert r["draft_en"].rstrip().splitlines()[-3] == "Ramesh Kumar"  # sign-off name


def test_hindi_has_same_data():
    r = d(FULL)
    for s in ("Ramesh Kumar", "Bihar", "Shree Builders", "mason", "₹12,500", "2025-01-01", "2025-03-31"):
        assert s in r["draft_hi"]
    assert "मजदूरी संहिता, 2019" in r["draft_hi"]


@pytest.mark.parametrize("payload", [{}, None, [], "text", 7])
def test_empty_payload_is_all_placeholders_never_invented(payload):
    r = d(payload)
    assert r["requires_human_review"] is True
    assert r["draft_en"].count(PH) >= 8
    assert "Rs [ ____ ]" in r["draft_en"] and "₹[ ____ ]" in r["draft_hi"]
    assert "worker name" in " ".join(r["notes_en"])


@pytest.mark.parametrize("amount", [0, -5, None, "", "abc", True, float("nan"), float("inf"), [], 1e12])
def test_bad_amount_becomes_placeholder(amount):
    r = d({**FULL, "wage_owed_inr": amount})
    assert "Rs [ ____ ]" in r["draft_en"]
    assert "Rs 12,500" not in r["draft_en"]


@pytest.mark.parametrize("amount,shown", [
    (500, "Rs 500"), (1000, "Rs 1,000"), (123456, "Rs 1,23,456"), (1234567, "Rs 12,34,567"),
    (2500.5, "Rs 2,500.50"), ("8000", "Rs 8,000"), ("8,000", "Rs 8,000"),
])
def test_amount_formatting(amount, shown):
    assert shown in d({**FULL, "wage_owed_inr": amount})["draft_en"]


def test_each_missing_field_gets_a_placeholder_and_a_note():
    for key, label in [("worker_name", "worker name"), ("state", "state"), ("employer_name", "employer name"),
                       ("work_type", "type of work"), ("period_from", "start date"),
                       ("period_to", "end date"), ("wage_owed_inr", "amount")]:
        f = dict(FULL)
        f[key] = ""
        r = d(f)
        assert r["draft_en"].count(PH) >= 3, key
        assert label in " ".join(r["notes_en"]), key


def test_whitespace_only_treated_as_missing():
    r = d({**FULL, "worker_name": "   \n\t "})
    assert "I, [ ____ ]," in r["draft_en"]


def test_unicode_names_preserved():
    f = {**FULL, "worker_name": "रामू यादव", "employer_name": "श्री बिल्डर्स 🏗️", "state": "उत्तर प्रदेश"}
    r = d(f)
    for text in (r["draft_en"], r["draft_hi"]):
        assert "रामू यादव" in text and "श्री बिल्डर्स 🏗️" in text and "उत्तर प्रदेश" in text


def test_control_chars_stripped_and_details_omitted_when_empty():
    r = d({**FULL, "worker_name": "Ra\x00mesh\x07", "details": ""})
    assert "\x00" not in r["draft_en"] and "\x07" not in r["draft_en"]
    assert "Details:" not in r["draft_en"] and "विवरण:" not in r["draft_hi"]


def test_long_details_truncated_with_note():
    r = d({**FULL, "details": "x" * 5000})
    assert "x" * 1001 not in r["draft_en"] and "x" * 1000 in r["draft_en"]
    assert any("cut to" in n for n in r["notes_en"])


def test_non_string_fields_do_not_crash():
    r = d({"worker_name": 123, "state": ["a"], "employer_name": {"x": 1}, "work_type": True,
           "period_from": 20250101, "details": None})
    assert "I, 123," in r["draft_en"]


def test_notes_checklist_content():
    n = " ".join(d(FULL)["notes_en"])
    for s in ("not legal advice", "three years", "section 45(6)", "sufficient cause", "Keep a copy",
              "attendance", "your state", "NEEDS-REVIEW"):
        assert s in n, s


def test_no_invented_office_or_wrong_helpline():
    r = d(FULL)
    blob = r["draft_en"] + r["draft_hi"] + " ".join(r["notes_en"])
    assert "14434" not in blob  # e-Shram helpdesk only, not for wage claims


def test_old_claim_gets_time_limit_warning():
    r = d({**FULL, "period_from": "2021-01-01", "period_to": "2021-03-31"})
    assert any("more than three years" in n for n in r["notes_en"])
    assert not any("more than three years" in n for n in d(FULL)["notes_en"])


@pytest.mark.parametrize("p_to,expect_warn", [("2023-09-27", False), ("2023-09-26", True),
                                              ("26/09/2023", True), ("27-09-2023", False)])
def test_three_year_boundary(p_to, expect_warn):
    r = d({**FULL, "period_from": "2023-01-01", "period_to": p_to})
    assert any("more than three years" in n for n in r["notes_en"]) is expect_warn


def test_date_order_and_unreadable_date_notes():
    assert any("later than" in n for n in d({**FULL, "period_from": "2025-05-01", "period_to": "2025-01-01"})["notes_en"])
    assert any("could not be read" in n for n in d({**FULL, "period_from": "last winter"})["notes_en"])


def test_deterministic():
    assert d(FULL) == d(FULL)
