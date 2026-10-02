"""Spending guard for a public deployment: per-IP rate limit and a daily rupee budget.

Both are off unless set in the environment (RATE_LIMIT_PER_10MIN, DAILY_BUDGET_INR).
State is in memory, so on serverless each warm instance keeps its own counters: a
best-effort brake on runaway Sarvam spend, not an exact accounting.
"""
import os
import threading
import time
from collections import defaultdict, deque

from .errors import AppError

_lock = threading.Lock()
_hits: dict[str, deque] = defaultdict(deque)
_spent = {"day": "", "inr": 0.0}
WINDOW_S = 600


def _num(name: str) -> float:
    try:
        return float(os.getenv(name, "0") or 0)
    except ValueError:
        return 0.0


def _today_ist(now: float) -> str:
    return time.strftime("%Y-%m-%d", time.gmtime(now + 5.5 * 3600))


def check(ip: str) -> None:
    limit, budget, now = int(_num("RATE_LIMIT_PER_10MIN")), _num("DAILY_BUDGET_INR"), time.time()
    with _lock:
        day = _today_ist(now)
        if _spent["day"] != day:
            _spent.update(day=day, inr=0.0)
        if budget and _spent["inr"] >= budget:
            raise AppError("rate_limited", "Today's demo budget is used up. Please try again tomorrow.",
                           "आज की सीमा पूरी हो गई है। कृपया कल फिर कोशिश करें।")
        if limit:
            q = _hits[ip]
            while q and now - q[0] > WINDOW_S:
                q.popleft()
            if len(q) >= limit:
                raise AppError("rate_limited")
            q.append(now)


def record(cost_inr) -> None:
    try:
        cost = float(cost_inr or 0)
    except (TypeError, ValueError):
        return
    with _lock:
        day = _today_ist(time.time())
        if _spent["day"] != day:
            _spent.update(day=day, inr=0.0)
        _spent["inr"] += cost


def client_ip(headers, fallback: str | None) -> str:
    fwd = headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() or headers.get("x-real-ip", "") or fallback or "unknown")
