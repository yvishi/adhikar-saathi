"""Offline tests for app/backend/retrieval.py (fixture cards, no network)."""
import json
import shutil
from pathlib import Path

import pytest

from app.backend import retrieval as R

FX = Path(__file__).parent / "fixtures"
CARDS = FX / "retrieval_cards_fixture.json"
QUERIES = json.loads((FX / "queries_fixture.json").read_text(encoding="utf-8"))["queries"]


@pytest.fixture(scope="module")
def ret(tmp_path_factory):
    return R.Retriever(str(CARDS), cache_dir=tmp_path_factory.mktemp("cache"))


def top_id(r, q):
    return r.retrieve(q, 1)[0]["id"]


def test_hindi_queries(ret):
    assert top_id(ret, "मेरे ठेकेदार ने तीन महीने से मजदूरी नहीं दी") == "W-03"
    assert top_id(ret, "ई-श्रम कार्ड कैसे बनवाएं") == "S-01"
    assert top_id(ret, "बुढ़ापे में पेंशन कैसे मिलेगी") == "S-02"
    assert top_id(ret, "गर्भवती महिला को छुट्टी और पैसे मिलते हैं क्या") == "M-01"


def test_hinglish_queries(ret):
    assert top_id(ret, "thekedar ne majdoori nahi di kya karu") == "W-03"
    assert top_id(ret, "accident ho jaye to bima milega kya") == "S-03"
    assert top_id(ret, "office mein mere sath yaun utpidan hua complaint kaha kare") == "H-01"


def test_english_queries(ret):
    assert top_id(ret, "How do I register on e-Shram") == "S-01"
    assert top_id(ret, "Can my employer cut my salary as a fine") == "W-04"
    assert top_id(ret, "Is there a law for maids and domestic workers") in ("D-01", "D-02")


def test_out_of_scope_scores_low(ret):
    for q in ["What is the weather in Delhi today", "Who won the cricket match yesterday", "aaj ka mausam kaisa rahega",
              "gold ka bhav aaj kya hai"]:
        assert ret.retrieve(q, 1)[0]["score"] < R.RELEVANCE_THRESHOLD, q
    assert ret.retrieve("What is the minimum wage", 1)[0]["score"] > R.RELEVANCE_THRESHOLD


def test_result_shape(ret):
    res = ret.retrieve("minimum wage", k=4)
    assert 1 <= len(res) <= 4
    scores = [c["score"] for c in res]
    assert scores == sorted(scores, reverse=True)
    assert all(0.0 <= s <= 1.0 for s in scores)
    assert {"id", "title_en", "text_en", "source", "score"} <= set(res[0])
    assert len(ret.retrieve("minimum wage", k=2)) == 2
    assert ret.retrieve("   ") == []


def test_skipped_cards_excluded(ret):
    assert all(c["status"] != "skipped" for c in ret.retrieve_all())
    assert "X-03" not in [c["id"] for c in ret.retrieve_all()]
    assert "X-03" not in [c["id"] for c in ret.retrieve("minimum wage pension maternity", 20)]
    assert len(ret.retrieve_all()) == 18


def test_retrieve_returns_copies(ret):
    ret.retrieve("pension", 1)[0]["title_en"] = "changed"
    assert ret.retrieve("pension", 1)[0]["title_en"] != "changed"


def test_recall_on_fixture_queries(ret):
    ins = [q for q in QUERIES if not q.get("oos")]
    r1 = sum(top_id(ret, q["q"]) in q["expected"] for q in ins) / len(ins)
    r4 = sum(bool({c["id"] for c in ret.retrieve(q["q"], 4)} & set(q["expected"])) for q in ins) / len(ins)
    assert r1 >= 0.85, r1
    assert r4 >= 0.95, r4


def test_bm25_mode_works(tmp_path):
    r = R.Retriever(str(CARDS), mode="bm25", cache_dir=tmp_path)
    assert r.mode == "bm25"
    assert r.retrieve("ओवरटाइम का पैसा", 1)[0]["id"] == "W-06"
    assert r.retrieve("majdoori kitni honi chahiye minimum", 1)[0]["id"] in ("W-01", "W-07")


def test_env_mode_and_invalid(monkeypatch, tmp_path):
    monkeypatch.setenv("RETRIEVER_MODE", "bm25")
    assert R.Retriever(str(CARDS), cache_dir=tmp_path).mode == "bm25"
    monkeypatch.setenv("RETRIEVER_MODE", "nonsense")
    with pytest.raises(ValueError):
        R.Retriever(str(CARDS), cache_dir=tmp_path)


def test_falls_back_to_bm25_when_model_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(R.Retriever, "_ensure_model", lambda self: False)
    r = R.Retriever(str(CARDS), mode="hybrid", cache_dir=tmp_path)
    assert r.mode == "bm25"
    assert r.retrieve("pension", 1)[0]["id"] == "S-02"


def test_reindex_on_file_change(tmp_path):
    cards = tmp_path / "cards.json"
    shutil.copy(CARDS, cards)
    cache = tmp_path / "cache"
    r = R.Retriever(str(cards), cache_dir=cache)
    assert top_id(r, "safety helmet on scaffolding") != "Z-99"
    data = json.loads(cards.read_text(encoding="utf-8"))
    data["cards"].append({
        "id": "Z-99", "topic": "meta", "title_en": "Safety helmet on scaffolding",
        "text_en": "Workers on scaffolding must be given a safety helmet and a safety belt.",
        "keywords_en": ["helmet", "scaffolding", "safety"], "keywords_hi": [], "source": {}, "verified": False,
        "status": "ready", "notes": "",
    })
    cards.write_text(json.dumps(data), encoding="utf-8")
    assert top_id(r, "safety helmet on scaffolding") == "Z-99"
    assert len(r.retrieve_all()) == 19
    if r.mode != "bm25":  # vectors are re-cached under a new hash, old file removed
        assert len(list(cache.glob("emb_*.npz"))) == 1


def test_embedding_cache_reused(tmp_path):
    r1 = R.Retriever(str(CARDS), mode="embed", cache_dir=tmp_path)
    if r1.mode != "embed":
        pytest.skip("embedding model not available locally")
    files = list(tmp_path.glob("emb_*.npz"))
    assert len(files) == 1
    mtime = files[0].stat().st_mtime_ns
    r2 = R.Retriever(str(CARDS), mode="embed", cache_dir=tmp_path)
    assert files[0].stat().st_mtime_ns == mtime
    assert r2.retrieve("pension for old age", 1)[0]["id"] == "S-02"


def test_accepts_plain_array_file(tmp_path):
    cards = json.loads(CARDS.read_text(encoding="utf-8"))["cards"]
    f = tmp_path / "cards.json"
    f.write_text(json.dumps(cards), encoding="utf-8")
    assert R.Retriever(str(f), mode="bm25", cache_dir=tmp_path).retrieve("pension", 1)[0]["id"] == "S-02"


def test_missing_and_bad_files(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        R.Retriever(str(tmp_path / "nope.json"), cache_dir=tmp_path)
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        R.Retriever(str(empty), cache_dir=tmp_path)
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="not valid JSON"):
        R.Retriever(str(bad), cache_dir=tmp_path)
    none = tmp_path / "none.json"
    none.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="no usable"):
        R.Retriever(str(none), cache_dir=tmp_path)


def test_cli_prints_utf8(capsys):
    rc = R._main(["ई-श्रम कार्ड कैसे बनवाएं", "--k", "2", "--cards", str(CARDS), "--mode", "bm25"])
    out = capsys.readouterr().out
    assert rc == 0 and "S-01" in out
    assert R._main(["x", "--cards", "does_not_exist.json"]) == 2


def test_glossary_normalisation():
    assert "wage" in R.expand_query("मज़दूरी")  # nukta variant
    assert "wage" in R.expand_query("मजदूरों की मजदूरी")
    assert "contractor" in R.expand_query("thekedaar")  # spelling variant
    assert "eshram" in R.expand_query("e-Shram card")
    assert R.expand_query("what is the weather") == ""
