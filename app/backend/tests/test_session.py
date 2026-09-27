from app.backend.session import SessionStore


def test_keeps_last_six_turns():
    s = SessionStore()
    sid = s.get_or_create(None)
    for i in range(9):
        s.add_turn(sid, f"u{i}", f"a{i}")
    h = s.history(sid)
    assert len(h) == 6 and h[0]["user"] == "u3" and h[-1]["user"] == "u8"


def test_ttl_expiry():
    now = [0.0]
    s = SessionStore(ttl=100, clock=lambda: now[0])
    sid = s.get_or_create("abc")
    s.add_turn(sid, "u", "a")
    now[0] = 50
    assert s.history("abc")
    now[0] = 200
    s.get_or_create("other")  # triggers purge
    assert s.history("abc") == []


def test_unknown_id_is_created_with_that_id():
    assert SessionStore().get_or_create("mine") == "mine"
