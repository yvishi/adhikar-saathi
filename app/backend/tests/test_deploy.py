"""Public-deployment behaviour: browser-held history after a restart, rate limit, daily budget."""
import json

import pytest
from fastapi.testclient import TestClient

from app.backend import guard, main, pipeline


@pytest.fixture(autouse=True)
def _fresh_guard(monkeypatch):
    monkeypatch.setenv("MOCK_MODE", "1")
    for name in ("RATE_LIMIT_PER_10MIN", "DAILY_BUDGET_INR"):
        monkeypatch.delenv(name, raising=False)
    guard._hits.clear()
    guard._spent.update(day="", inr=0.0)
    yield


client = TestClient(main.app)


def test_client_history_used_when_server_has_no_session(monkeypatch):
    seen = {}
    real = pipeline.build_query

    def spy(history, text):
        seen["history"] = history
        return real(history, text)

    monkeypatch.setattr(pipeline, "build_query", spy)
    turns = [{"user": "ठेकेदार ने मज़दूरी नहीं दी", "assistant": "आप दावा कर सकते हैं।"}]
    r = client.post("/api/ask", data={"session_id": "fresh-instance", "text": "और अगर वो मना करे?",
                                      "want_audio": "false", "history": json.dumps(turns)})
    assert r.status_code == 200
    assert seen["history"] == turns


def test_server_history_wins_over_client_history(monkeypatch):
    client.post("/api/ask", data={"session_id": "s1", "text": "minimum wage", "want_audio": "false"})
    seen = {}
    monkeypatch.setattr(pipeline, "build_query", lambda h, t: seen.setdefault("history", h) and t or t)
    client.post("/api/ask", data={"session_id": "s1", "text": "and then?", "want_audio": "false",
                                  "history": json.dumps([{"user": "fake", "assistant": "fake"}])})
    assert seen["history"][0]["user"] == "minimum wage"


@pytest.mark.parametrize("raw", [None, "not json", "{}", json.dumps([{"user": 1}]), "x" * 30000])
def test_bad_client_history_is_ignored(raw):
    data = {"text": "minimum wage", "want_audio": "false"}
    if raw is not None:
        data["history"] = raw
    assert client.post("/api/ask", data=data).status_code == 200


def test_clean_client_history_caps_turns_and_length():
    raw = [{"user": "u" * 5000, "assistant": "a" * 5000}] * 10
    out = pipeline.clean_client_history(raw)
    assert len(out) == 6
    assert len(out[0]["assistant"]) == 1500


def test_rate_limit_per_ip(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_10MIN", "2")
    codes = [client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"},
                         headers={"x-forwarded-for": "1.2.3.4"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    other = client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"},
                        headers={"x-forwarded-for": "5.6.7.8"})
    assert other.status_code == 200


def test_daily_budget_stops_requests(monkeypatch):
    monkeypatch.setenv("DAILY_BUDGET_INR", "1")
    guard.record(1.5)
    r = client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"})
    assert r.status_code == 429
    assert r.json()["error"]["code"] == "rate_limited"


def test_guard_off_by_default():
    for _ in range(30):
        assert client.post("/api/ask", data={"text": "minimum wage", "want_audio": "false"}).status_code == 200
