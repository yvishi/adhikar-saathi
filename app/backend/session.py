"""In-memory sessions: last 6 turns, 2 hour TTL. Lost on restart by design (nothing personal is stored on disk)."""
import threading
import time
import uuid

MAX_TURNS = 6
TTL_SECONDS = 2 * 60 * 60


class SessionStore:
    def __init__(self, max_turns: int = MAX_TURNS, ttl: float = TTL_SECONDS, clock=time.time):
        self.max_turns = max_turns
        self.ttl = ttl
        self.clock = clock
        self._data: dict[str, dict] = {}
        self._lock = threading.Lock()

    def _purge(self) -> None:
        now = self.clock()
        for sid in [s for s, v in self._data.items() if now - v["touched"] > self.ttl]:
            del self._data[sid]

    def get_or_create(self, session_id: str | None) -> str:
        with self._lock:
            self._purge()
            if not session_id or session_id not in self._data:
                session_id = session_id or uuid.uuid4().hex[:12]
                self._data[session_id] = {"turns": [], "touched": self.clock()}
            self._data[session_id]["touched"] = self.clock()
            return session_id

    def history(self, session_id: str) -> list[dict]:
        """[{"user": str, "assistant": str}, ...] oldest first."""
        with self._lock:
            s = self._data.get(session_id)
            return list(s["turns"]) if s else []

    def add_turn(self, session_id: str, user: str, assistant: str) -> None:
        with self._lock:
            s = self._data.setdefault(session_id, {"turns": [], "touched": self.clock()})
            s["turns"].append({"user": user, "assistant": assistant})
            del s["turns"][: -self.max_turns]
            s["touched"] = self.clock()


store = SessionStore()
