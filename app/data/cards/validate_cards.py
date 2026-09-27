import json, re, html, subprocess, os, sys
ROOT = r"F:\College\SEM5\BFWAI Hackathon"
cards = json.load(open(os.path.join(ROOT, r"app\data\cards\cards.json"), encoding="utf-8"))
PLANNED = "W-01 W-02 W-03 W-04 W-05 W-06 W-07 S-01 S-02 S-03 S-04 S-05 M-01 H-01 X-01 X-02 D-01 D-02".split()
KEYS = ["id", "topic", "title_en", "text_en", "text_hi", "keywords_en", "keywords_hi", "source", "verified", "status", "notes"]
TOPICS = {"wages", "schemes", "maternity", "harassment", "helpline", "domestic", "meta"}
cache = {}


def text_of(rel):
    if rel in cache:
        return cache[rel]
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if p.endswith(".pdf"):
        t = subprocess.run(["pdftotext", "-enc", "UTF-8", p, "-"], capture_output=True).stdout.decode("utf-8", "ignore")
    elif p.endswith(".html"):
        s = open(p, encoding="utf-8", errors="ignore").read()
        s = re.sub(r"(?s)<!--.*?-->", "", s)
        s = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", "", s)
        s = re.sub(r"(?s)<[^>]+>", " ", s)
        t = html.unescape(s)
    else:
        t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"\s+", " ", t)
    cache[rel] = t
    return t


errs = []
ids = [c["id"] for c in cards]
if len(set(ids)) != len(ids):
    errs.append("duplicate ids")
for pid in PLANNED:
    if pid not in ids:
        errs.append("missing planned id " + pid)
for c in cards:
    i = c["id"]
    for k in KEYS:
        if k not in c:
            errs.append(f"{i}: missing key {k}")
    if not (i in PLANNED or i.startswith("X-")):
        errs.append(f"{i}: id not allowed")
    if c["topic"] not in TOPICS:
        errs.append(f"{i}: bad topic")
    if c["text_hi"] is not None or c["keywords_hi"] != []:
        errs.append(f"{i}: hi fields not empty")
    if c["status"] not in ("ready", "draft", "skipped"):
        errs.append(f"{i}: bad status")
    if c["status"] == "ready":
        if c["verified"] is not True:
            errs.append(f"{i}: ready but not verified")
        if not 4 <= len(c["keywords_en"]) <= 8:
            errs.append(f"{i}: keywords count {len(c['keywords_en'])}")
        for sk in ("name", "section", "url", "file"):
            if sk not in c["source"]:
                errs.append(f"{i}: source missing {sk}")
        ev = c.get("evidence")
        if not ev:
            errs.append(f"{i}: no evidence")
        else:
            f = c["source"]["file"]
            if not os.path.exists(os.path.join(ROOT, f.replace("/", os.sep))):
                errs.append(f"{i}: file missing {f}")
            elif re.sub(r"\s+", " ", ev).strip() not in text_of(f):
                errs.append(f"{i}: evidence NOT FOUND in {f}: {ev!r}")
        n_sent = len(re.findall(r"[.!?](?:\s|$)", c["text_en"]))
        print(f"{i}: sentences~{n_sent}, chars={len(c['text_en'])}, keywords={len(c['keywords_en'])}, evidence_ok={'yes' if not any(e.startswith(i+':') and 'evidence' in e for e in errs) else 'NO'}")
    else:
        if not c["notes"]:
            errs.append(f"{i}: skipped without notes")
print("cards:", len(cards), "ready:", sum(c["status"] == "ready" for c in cards), "skipped:", sum(c["status"] == "skipped" for c in cards))
print("ERRORS:", errs if errs else "none")
sys.exit(1 if errs else 0)
