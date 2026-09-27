"""Offline retrieval of English rights cards for Hindi / Hinglish / English queries.

Three methods, switchable with env RETRIEVER_MODE (or the `mode` argument):
  bm25    BM25 over English card text plus a hand-built Hindi/Hinglish -> English
          labour glossary (query expansion). Pure Python, starts instantly.
  embed   Cosine similarity with a local multilingual sentence model
          (fastembed + paraphrase-multilingual-MiniLM-L12-v2, ONNX, CPU).
  hybrid  Weighted fusion of the two normalised scores.
  auto    (default) hybrid if the model loads, otherwise bm25.
No network calls happen at query time. See retrieval_data/BENCHMARK.md for numbers.

CLI:  python -m app.backend.retrieval "query" --k 4 [--mode bm25]
      python -m app.backend.retrieval --download-model   (one-off, needs internet)
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import logging
import math
import os
import re
import sys
import unicodedata
from pathlib import Path

log = logging.getLogger("retrieval")

DATA_DIR = Path(__file__).resolve().parent / "retrieval_data"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
MODEL_DIR = DATA_DIR / "models"
DEFAULT_CARDS = "app/data/cards/cards.json"
INDEX_VERSION = "v1"  # bump when the text fed to the embedder changes

# Scores are in 0-1. Suggested "nothing relevant" floor: on the fixture benchmark a top
# score below it kept 83/84 in-scope queries and flagged 9/12 out-of-scope ones. It is a
# soft signal (hard cases like "cook biryani" score ~0.5), so keep the LLM's cite-or-refuse.
RELEVANCE_THRESHOLD = 0.20

# BM25 -> 0-1 squashing constant and hybrid weights (tuned on the fixture benchmark).
BM25_SCALE = 16.0
HYBRID_W_BM25 = 0.5
COS_LOW, COS_HIGH = 0.20, 0.60  # cosine range mapped to 0-1
EMBED_WITH_EXPANSION = True  # append glossary English terms to the text sent to the embedder


# --------------------------------------------------------------------------- text
_NUKTA = "़"


def normalize(text: str) -> str:
    """Lowercase, NFC, drop nukta, unify chandrabindu, join e-Shram / PM-SYM spellings."""
    t = unicodedata.normalize("NFC", text or "").lower()
    t = t.replace(_NUKTA, "").replace("ँ", "ं")
    t = unicodedata.normalize("NFC", t.replace("।", " ").replace("॥", " "))
    t = re.sub(r"\be\s*[-‐-―]?\s*shram\b", "eshram", t)
    t = re.sub(r"\bई\s*[-‐-―]?\s*श्रम\b", "eshram", t)
    t = re.sub(r"\bpm\s*[-‐-―]?\s*sym\b", "pmsym", t)
    t = re.sub(r"\bpm\s*[-‐-―]?\s*sbdy\b", "pmsbdy", t)
    return t


_TOKEN_RE = re.compile(r"[ऀ-ॿ]+|[a-z0-9]+")
_DEVANAGARI_RE = re.compile(r"[ऀ-ॿ]")


def tokens_of(text: str) -> list[str]:
    return _TOKEN_RE.findall(normalize(text))


def _is_dev(tok: str) -> bool:
    return bool(_DEVANAGARI_RE.match(tok))


_EN_STOP = set(
    """a an the and or but of to in on at for from by with without as is are was were be been being am
    do does did have has had i me my mine we our you your he she it its they them their this that these
    those there here what which who whom when where why how can could should would will shall may might
    must not no if then than so such also any all each every some more most other into over under about
    up out off very just get got""".split()
)


def stem(w: str) -> str:
    """Very light English stemmer: enough to match plural / -ing / -ed forms."""
    if len(w) <= 3 or not w.isalpha():
        return w
    for suf, rep in (("ies", "y"), ("ing", ""), ("ed", ""), ("es", ""), ("s", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3 and not w.endswith("ss"):
            base = w[: -len(suf)] + rep
            if suf in ("ing", "ed") and len(base) > 2 and base[-1] == base[-2] and base[-1] not in "ls":
                base = base[:-1]
            return base
    return w


def en_terms(text: str) -> list[str]:
    """English/latin terms only (used for documents and for expanded queries)."""
    return [stem(t) for t in tokens_of(text) if not _is_dev(t) and t not in _EN_STOP]


# ----------------------------------------------------------------------- glossary
# (keys, english expansion). Keys: Hindi (Devanagari) and Hinglish (Latin) spellings,
# single words or short phrases. Every Hindi key is listed in
# app/data/hindi_review/retrieval.md for the owner to verify. The expansion is what the
# BM25 side sees, so it is written in the vocabulary the cards use.
_GLOSSARY_RAW: list[tuple[list[str], str]] = [
    # wages
    (["मजदूरी", "मज़दूरी", "मजदुरी", "majdoori", "majdori", "mazdoori", "mazdori", "majduri", "mazduri"], "wages wage pay"),
    (["वेतन", "तनख्वाह", "तनखा", "तनखाह", "पगार", "सैलरी", "salary", "tankhwah", "tankha", "tankhah", "pagar", "vetan", "selary"], "salary wages pay"),
    (["दिहाड़ी", "दिहाडी", "दिहाड़ी", "dihadi", "dihaadi", "dehadi", "dihari"], "daily wage daily wager"),
    (["न्यूनतम", "न्यूनतम", "nyuntam", "minimam", "kam se kam", "कम से कम"], "minimum"),
    (["पैसे", "पैसा", "पैसो", "रुपये", "रुपए", "paisa", "paise", "paisey", "rupay", "rupaye", "rupee"], "pay wages money"),
    (["ठेकेदार", "ठेकदार", "ठेकेदारी", "thekedar", "thekedaar", "thekadar", "thekedari", "contractor", "ठेका", "theka"], "contractor contract worker"),
    (["मालिक", "मालकिन", "सेठ", "नियोक्ता", "malik", "maalik", "seth", "sethji", "niyokta", "boss", "मालिको"], "employer"),
    (["मजदूर", "मज़दूर", "मजदुर", "कामगार", "श्रमिक", "majdoor", "mazdoor", "mazdur", "majdur", "kaamgar", "kamgar", "shramik", "मजदूरो"], "worker labour unorganised"),
    (["काटता", "काट", "कटौती", "kaat", "kaatna", "kaat leta", "katauti", "katta", "kata"], "deduction cut fine"),
    (["जुर्माना", "jurmana", "jurmaana", "fine", "fined", "penalty"], "fine deduction"),
    (["एडवांस", "advance", "पेशगी", "peshgi"], "advance deduction"),
    (["ओवरटाइम", "ओवर टाइम", "overtime", "over time", "extra ghante", "अतिरिक्त घंटे", "ज्यादा घंटे", "ज्यादा घण्टे", "zyada ghante"], "overtime extra hours"),
    (["बोनस", "bonus"], "bonus"),
    (["छुट्टी", "chutti", "chhutti", "छुट्टियां", "अवकाश"], "leave paid leave holiday"),
    (["साप्ताहिक", "हफ्ते", "haftawar", "hafte", "saptahik"], "weekly"),
    (["देरी", "देर", "late", "deri", "der se"], "late delay"),
    (["समय पर", "कब तक", "कब मिल", "kab tak", "samay par", "time par", "kab milna"], "payment date when paid"),
    (["महीने", "महिना", "महीना", "mahine", "mahina", "mahinay"], "monthly month"),
    (["मजदूरी नहीं", "पैसे नहीं", "पैसा नहीं", "वेतन नहीं", "तनख्वाह नहीं", "नहीं दी", "नहीं दिया", "नहीं मिली", "नहीं मिला", "नहीं मिले", "नहीं मिलता", "नहीं मिलती",
      "majdoori nahi", "mazdoori nahi", "paisa nahi", "paise nahi", "salary nahi", "pagar nahi", "tankhwah nahi", "nahi di", "nahi diya", "nahi mila", "nahi mili", "nahi milta", "nahi milti"],
     "unpaid wages withheld not paid dues"),
    (["बकाया", "बाकी पैसे", "bakaya", "baki paise", "बाकी"], "unpaid dues wages"),
    (["शिकायत", "shikayat", "shikayath", "complaint", "शिकायत करूं", "फरियाद"], "complaint claim authority"),
    (["दावा", "dava", "daava", "claim"], "claim application authority"),
    (["तीन साल", "3 साल", "teen saal"], "three years time limit"),
    (["बराबर", "बराबरी", "barabar", "same"], "equal same"),
    (["औरत", "औरतों", "महिला", "महिलाओं", "लड़की", "स्त्री", "aurat", "auraton", "mahila", "mahilaon", "ladki", "stri", "women", "female", "woman"], "woman women gender"),
    (["आदमी", "आदमियों", "पुरुष", "मर्द", "aadmi", "admi", "purush", "mard", "male"], "man men gender"),
    (["भेदभाव", "bhedbhav", "bhed bhav", "भेद भाव"], "discrimination"),
    # schemes
    (["पेंशन", "पेन्शन", "pension", "pention"], "pension"),
    (["बुढ़ापे", "बुढ़ापा", "बुढापे", "बुज़ुर्ग", "वृद्धावस्था", "बूढ़े", "budhapa", "budhape", "buddhe", "retire", "बुजुर्ग", "60 साल"], "old age retirement age pension"),
    (["बीमा", "बिमा", "bima", "beema", "insurance", "insurence"], "insurance accident cover"),
    (["दुर्घटना", "हादसा", "durghatna", "hadsa", "haadsa", "accident", "एक्सीडेंट", "axident", "chot", "चोट", "घायल", "ghayal"], "accident injury insurance cover disability"),
    (["मौत", "मृत्यु", "मर जाए", "maut", "mrityu", "death"], "death accidental cover"),
    (["विकलांगता", "अपंग", "viklangta", "apang", "disability"], "disability cover"),
    (["ईश्रम", "eshram", "e shram", "eshramcard", "ई श्रम", "shram card", "श्रम कार्ड"], "eshram registration portal card"),
    (["रजिस्ट्रेशन", "पंजीकरण", "रजिस्टर", "पंजीयन", "registration", "registeration", "registration", "register", "panjikaran", "panjikaran", "रजिस्ट्रेशन"], "registration register"),
    (["कार्ड", "card", "kaard"], "card"),
    (["लेबर कार्ड", "श्रमिक कार्ड", "लेबर", "labour card", "labor card", "labor", "लेबर कार्ड"], "labour card labour welfare board registration"),
    (["निर्माण", "मिस्त्री", "मिस्री", "राजमिस्त्री", "बिल्डिंग", "nirman", "mistri", "mistry", "raajmistri", "rajmistri", "construction", "building", "मकान बनाने", "इमारत"], "construction building worker BOCW welfare board"),
    (["योजना", "स्कीम", "योजनाएं", "योजनाओं", "yojana", "yojna", "scheme", "skeem", "लाभ", "labh", "फायदा", "fayda", "फ़ायदा", "sarkari", "सरकारी"], "scheme benefits government"),
    (["श्रम योगी", "मानधन", "mandhan", "maandhan", "pmsym", "shram yogi", "पीएम एसवाईएम", "pm sym"], "PM-SYM pension Shram Yogi Maan-dhan"),
    (["असंगठित", "unorganised", "unorganized", "asangathit", "asangathith", "informal", "इनफॉर्मल"], "unorganised informal"),
    (["सामाजिक सुरक्षा", "samajik suraksha", "social security"], "social security"),
    (["फ्री", "मुफ्त", "मुफ़्त", "निःशुल्क", "free", "muft", "muphat", "नि:शुल्क"], "free"),
    (["पैसे लगते", "paise lagte", "paise lagenge", "पैसे लगेंगे", "paise dena", "पैसे देने", "रिश्वत", "rishwat", "bribe"], "free registration fee pay"),
    (["फीस", "fees", "fee", "शुल्क", "shulk"], "fee pay charge"),
    # maternity
    (["मातृत्व", "matritva", "matritv", "maternity"], "maternity maternity leave benefit"),
    (["प्रसूति", "prasuti", "prasooti", "प्रसव", "prasav", "डिलीवरी", "delivery", "delivary"], "maternity delivery childbirth"),
    (["गर्भवती", "गर्भ", "गर्भावस्था", "प्रेग्नेंट", "प्रेग्नेंसी", "garbhvati", "garbhwati", "garbh", "pregnant", "pregnancy", "pregnent", "pregnency", "pet se", "पेट से"], "pregnant pregnancy maternity"),
    (["बच्चा", "बच्चे", "बच्चा होने", "bachcha", "bachha", "bacha", "bachche"], "child delivery maternity"),
    (["निकाल", "निकाला", "निकालना", "नौकरी से", "nikal", "nikala", "nikaal", "naukri se", "fire", "fired", "dismiss"], "dismissed dismissal termination"),
    # harassment
    (["यौन", "yaun", "sexual", "sexuel"], "sexual"),
    (["उत्पीड़न", "उत्पीडन", "utpidan", "utpeedan", "shoshan", "शोषण", "harassment", "harrasment", "harasment", "परेशान", "pareshan"], "harassment complaint"),
    (["छेड़छाड़", "छेड़खानी", "छेड़ा", "छेड़", "chhedchhad", "chhedkhani", "chheda", "chhed", "छेडछाड", "छेडखानी"], "sexual harassment molestation complaint"),
    (["छूता", "छुआ", "गंदी नजर", "छू", "chhua", "chhuta", "gandi nazar", "chhoo", "छुआ"], "touching sexual harassment"),
    (["बलात्कार", "रेप", "balatkar", "rape"], "sexual harassment complaint police"),
    (["काम की जगह", "कार्यस्थल", "दफ्तर", "ऑफिस", "ऑफ़िस", "आफिस", "कारखाना", "फैक्ट्री", "karyasthal", "daftar", "office", "factory", "kaam ki jagah", "work place", "workplace"], "workplace"),
    (["समिति", "कमेटी", "committee", "samiti"], "committee internal local"),
    # domestic
    (["घरेलू", "gharelu", "gharelu kamgar", "घर में काम", "घरों में", "ghar mein kaam", "ghar me kaam", "ghar ka kaam", "ghar ke kaam"], "domestic worker household"),
    (["बाई", "नौकरानी", "कामवाली", "कामवाली", "नौकर", "झाड़ू", "झाडू", "पोछा", "पोंछा", "बर्तन", "खाना बनाने", "bai", "naukrani", "kaamwali", "kamwali", "naukar", "jhadu", "pocha", "bartan", "maid", "cook", "cleaner", "servant"], "domestic worker maid house help household"),
    # withholding, injury, help, timing (added after looking at held-out misses)
    (["रोक", "रोके", "रोका", "रोककर", "दबा", "दबाकर", "दबाए", "rok", "roka", "roke", "rokh", "daba", "dabakar", "hold back", "holding back", "holds back", "withhold", "withholding", "keeps back"], "withheld unpaid wages dues"),
    (["टूट", "टूटा", "टूट गया", "फ्रैक्चर", "toot", "tut", "tuta", "toota", "fracture", "injured", "hurt", "गिर गया", "gir gaya", "जख्मी", "zakhmi"], "injury accident insurance cover"),
    (["मदद", "सहायता", "मदद मिलेगी", "madad", "sahayata", "sahayta", "help", "aid", "सहयोग"], "help benefits scheme"),
    (["कब मिलनी", "कब मिलेगी", "कब मिलेगा", "कब मिलता", "कब देना", "कब देते", "kab milni", "kab milegi", "kab milega", "kab milta", "kab dena", "kab deta"], "payment date when paid wages"),
    (["रोज", "रोज़", "रोजाना", "हर दिन", "roz", "rojana", "roj", "har din", "daily"], "daily wage"),
    (["देर तक", "ज्यादा देर", "ज्यादा घंटे", "der tak", "zyada der", "jyada der", "bahut der", "बहुत देर", "extra kaam", "एक्स्ट्रा", "extra", "अलग से पैसे"], "overtime extra hours"),
    (["boss", "manager", "supervisor", "sahab", "साहब", "मैनेजर", "सुपरवाइजर", "मुनीम", "munim"], "employer"),
    (["terminate", "terminated", "laid off", "hata diya", "हटा दिया", "हटाया", "hataya", "काम से हटा"], "dismissed dismissal termination"),
    (["expecting", "expectant", "उम्मीद से", "ummeed se"], "pregnant pregnancy maternity"),
    (["harassed", "harass", "abused", "abuse", "गलत तरीके", "galat tarike", "galat tarah", "गलत नजर"], "harassment complaint"),
    (["सरकारी", "सरकार", "sarkar", "sarkari", "government", "govt"], "government scheme benefits"),
    # helpline / meta
    (["हेल्पलाइन", "हेल्प लाइन", "हेल्पडेस्क", "नंबर", "टोल फ्री", "helpline", "helpdesk", "number", "nambar", "nambr", "toll free"], "helpline helpdesk phone number contact"),
    (["14434"], "14434 helpline helpdesk eshram"),
    (["कानून", "क़ानून", "kanoon", "kanun", "law", "कानूनी"], "law legal"),
    (["वकील", "कानूनी सलाह", "अदालत", "कोर्ट", "मुकदमा", "केस", "vakil", "kanooni salah", "court", "adalat", "mukadma", "mukadama", "case", "lawyer"], "legal advice lawyer court case"),
    (["श्रम विभाग", "लेबर ऑफिस", "लेबर विभाग", "shram vibhag", "labour office", "labor office", "labour department"], "labour office authority department"),
    (["अधिकार", "हक", "हक़", "adhikar", "hak", "haq", "rights", "right"], "right entitled"),
    (["कैसे", "kaise", "kese", "kaisay"], "how"),
    (["कहाँ", "कहां", "kahan", "kaha", "kahaan", "kidhar"], "where"),
    (["क्या", "kya", "kyaa"], ""),
]

# Words that carry no information in Hindi / Hinglish queries.
_HI_STOP = set(
    """का की के को से में पर है हैं था थी थे हो हूँ हूं हु होता होती होते ही भी तो या और कि जो यह वह ये वो इस उस मैं मुझे मुझको मेरा मेरी मेरे
    हम हमें हमारा आप आपका तुम क्या कौन कौनसा कौन सा कोई कुछ बहुत नहीं ना न कर करना करें करूं करूँ करो कराना दे दी दिया देता देती दें
    लिए लिये साथ तक अगर तो जी लेकिन एक दो तीन ने रहा रही रहे गया गई गए जाता जाती जाते सकता सकती सकते चाहिए चाहता चाहती होना
    ka ki ke ko se mein me main par hai hain tha thi the ho hu hun hoon hota hoti hote hi bhi to ya aur ki jo yeh ye woh wo is us mai mujhe mujhko
    mera meri mere hum hume hamara aap aapka tum kya kaun koi kuch bahut nahi na kar karna karen karu karun karo dena de di diya deta deti den
    liye liya sath tak agar toh ji lekin ek do teen ne raha rahi rahe gaya gayi gaye jata jati jate sakta sakti sakte chahiye chahta chahti
    hona kitni kitna kitne hoga hogi honge milta milti mila mili milega milegi mil""".split()
)


def _build_glossary():
    phrases: dict[str, str] = {}
    words: dict[str, str] = {}
    dev_words: dict[str, str] = {}
    for keys, exp in _GLOSSARY_RAW:
        for k in keys:
            nk = " ".join(tokens_of(k))
            if not nk:
                continue
            if " " in nk:
                phrases[nk] = (phrases.get(nk, "") + " " + exp).strip()
            elif _is_dev(nk):
                dev_words[nk] = (dev_words.get(nk, "") + " " + exp).strip()
            else:
                words[nk] = (words.get(nk, "") + " " + exp).strip()
    return phrases, words, dev_words


_PHRASES, _WORDS, _DEV_WORDS = _build_glossary()
_LATIN_KEYS = sorted(w for w in _WORDS if len(w) >= 5)
_HI_STOP_N = {normalize(w) for w in _HI_STOP}


def expand_query(query: str) -> str:
    """Return extra English terms suggested by Hindi / Hinglish words in the query."""
    toks = tokens_of(query)
    padded = " " + " ".join(toks) + " "
    extra: list[str] = []
    for ph, exp in _PHRASES.items():
        if f" {ph} " in padded:
            extra.append(exp)
    for t in toks:
        if t in _HI_STOP_N and t not in _WORDS and t not in _DEV_WORDS:
            continue
        if _is_dev(t):
            if t in _DEV_WORDS:
                extra.append(_DEV_WORDS[t])
                continue
            best = ""
            for k in _DEV_WORDS:
                if len(k) >= 4 and t.startswith(k) and len(k) > len(best):
                    best = k
            if best:
                extra.append(_DEV_WORDS[best])
        else:
            if t in _WORDS:
                extra.append(_WORDS[t])
            elif len(t) >= 5 and t not in _EN_STOP:
                m = difflib.get_close_matches(t, _LATIN_KEYS, n=1, cutoff=0.84)
                if m:
                    extra.append(_WORDS[m[0]])
    seen: list[str] = []
    for w in " ".join(extra).split():
        if w not in seen:
            seen.append(w)
    return " ".join(seen)


# --------------------------------------------------------------------------- BM25
class _BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = docs
        self.tf = []
        df: dict[str, int] = {}
        for d in docs:
            f: dict[str, int] = {}
            for w in d:
                f[w] = f.get(w, 0) + 1
            self.tf.append(f)
            for w in f:
                df[w] = df.get(w, 0) + 1
        n = len(docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}
        self.avgdl = (sum(len(d) for d in docs) / n) if n else 1.0

    def scores(self, q_terms: list[str]) -> list[float]:
        out = []
        for f, d in zip(self.tf, self.docs):
            s = 0.0
            dl = len(d)
            for w in q_terms:
                tf = f.get(w)
                if not tf:
                    continue
                s += self.idf[w] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            out.append(s)
        return out


# ------------------------------------------------------------------------ Retriever
def _load_cards(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Cards file not found: {path}")
    raw = path.read_bytes()
    if not raw.strip():
        raise ValueError(f"Cards file is empty: {path}")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Cards file is not valid JSON: {path} ({e})") from e
    if isinstance(data, dict):  # fixture style {"notes":..., "cards":[...]}
        data = data.get("cards", [])
    if not isinstance(data, list):
        raise ValueError(f"Cards file must contain a JSON array of cards: {path}")
    cards = [c for c in data if isinstance(c, dict) and c.get("id") and c.get("status") != "skipped"]
    if not cards:
        raise ValueError(f"Cards file has no usable (non-skipped) cards: {path}")
    return cards


def _doc_text(c: dict) -> str:
    kws = ", ".join(c.get("keywords_en") or [])
    return f"{c.get('title_en', '')}. {c.get('text_en', '')} {kws}".strip()


class Retriever:
    def __init__(self, cards_path: str = DEFAULT_CARDS, mode: str | None = None, cache_dir: str | Path | None = None):
        self.cards_path = Path(cards_path)
        if not self.cards_path.is_absolute() and not self.cards_path.exists():
            alt = PROJECT_ROOT / self.cards_path  # allow running from another cwd
            if alt.exists():
                self.cards_path = alt
        self.cache_dir = Path(cache_dir) if cache_dir else DATA_DIR
        self.requested_mode = (mode or os.environ.get("RETRIEVER_MODE") or "auto").strip().lower()
        if self.requested_mode not in ("bm25", "embed", "hybrid", "auto"):
            raise ValueError("RETRIEVER_MODE must be bm25, embed, hybrid or auto")
        self.mode = "bm25"
        self._model = None
        self._model_tried = False
        self._sig = None
        self._cards: list[dict] = []
        self._load()

    # -- indexing --------------------------------------------------------------
    def _file_sig(self):
        st = self.cards_path.stat()
        return (st.st_mtime_ns, st.st_size)

    def _load(self):
        self._cards = _load_cards(self.cards_path)
        self._sig = self._file_sig()
        docs = []
        for c in self._cards:
            title = en_terms(c.get("title_en", ""))
            kws = en_terms(" ".join(c.get("keywords_en") or []))
            body = en_terms(c.get("text_en", ""))
            hi = [t for t in tokens_of(" ".join((c.get("keywords_hi") or []) + [c.get("text_hi") or ""])) if _is_dev(t)]
            docs.append(title * 2 + kws * 2 + body + hi)
        self._bm25 = _BM25(docs)
        self._emb = None
        self._resolve_mode()

    def _resolve_mode(self):
        want = self.requested_mode
        if want == "bm25":
            self.mode = "bm25"
            return
        if not self._ensure_model():
            self.mode = "bm25"
            return
        try:
            self._emb = self._load_or_build_embeddings()
            self.mode = "hybrid" if want == "auto" else want
        except Exception as e:  # pragma: no cover - depends on environment
            log.warning("Embedding index failed (%s); falling back to BM25", e)
            self.mode = "bm25"

    def _ensure_model(self) -> bool:
        if self._model is not None:
            return True
        if self._model_tried:
            return False
        self._model_tried = True
        try:
            from fastembed import TextEmbedding

            kw = {} if os.environ.get("RETRIEVER_DOWNLOAD") == "1" else {"local_files_only": True}
            self._model = TextEmbedding(MODEL_NAME, cache_dir=str(MODEL_DIR), **kw)
            return True
        except Exception as e:
            log.warning("Embedding model unavailable (%s); using BM25 only. "
                        "Run `python -m app.backend.retrieval --download-model` once with internet.", e)
            return False

    def _cards_hash(self) -> str:
        h = hashlib.sha256()
        h.update(self.cards_path.read_bytes())
        h.update(f"|{MODEL_NAME}|{INDEX_VERSION}".encode())
        return h.hexdigest()[:16]

    def _load_or_build_embeddings(self):
        import numpy as np

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        key = self._cards_hash()
        f = self.cache_dir / f"emb_{key}.npz"
        ids = [c["id"] for c in self._cards]
        if f.exists():
            try:
                z = np.load(f, allow_pickle=False)
                if list(z["ids"]) == ids:
                    return z["vecs"]
            except Exception:
                pass
        vecs = np.array(list(self._model.embed([_doc_text(c) for c in self._cards])), dtype="float32")
        vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
        for old in self.cache_dir.glob("emb_*.npz"):
            try:
                old.unlink()
            except OSError:
                pass
        np.savez(f, ids=np.array(ids), vecs=vecs)
        return vecs

    def _refresh_if_changed(self):
        try:
            sig = self._file_sig()
        except FileNotFoundError:
            return  # keep serving the last good index
        if sig != self._sig:
            log.info("cards file changed, re-indexing")
            self._load()

    # -- scoring ---------------------------------------------------------------
    def _bm25_scores(self, query: str) -> list[float]:
        terms = en_terms(query) + en_terms(expand_query(query))
        raw = self._bm25.scores([t for t in terms if t in self._bm25.idf])
        return [1 - math.exp(-s / BM25_SCALE) for s in raw]

    def _embed_scores(self, query: str) -> list[float]:
        import numpy as np

        text = " ".join(tokens_of(query)) or query
        if EMBED_WITH_EXPANSION:
            text += " " + expand_query(query)
        q = np.array(list(self._model.embed([text])), dtype="float32")[0]
        q /= np.linalg.norm(q) + 1e-9
        cos = self._emb @ q
        return [float(min(1.0, max(0.0, (c - COS_LOW) / (COS_HIGH - COS_LOW)))) for c in cos]

    def _scores(self, query: str, mode: str) -> list[float]:
        if mode == "bm25":
            return self._bm25_scores(query)
        if mode == "embed":
            return self._embed_scores(query)
        b, e = self._bm25_scores(query), self._embed_scores(query)
        return [HYBRID_W_BM25 * x + (1 - HYBRID_W_BM25) * y for x, y in zip(b, e)]

    # -- public API ------------------------------------------------------------
    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        """Up to k non-skipped cards, best first, each a copy with 'score' in 0-1."""
        self._refresh_if_changed()
        if not (query or "").strip() or k <= 0:
            return []
        scores = self._scores(query, self.mode)
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))[:k]
        return [dict(self._cards[i], score=round(scores[i], 4)) for i in order]

    def retrieve_all(self) -> list[dict]:
        self._refresh_if_changed()
        return [dict(c) for c in self._cards]


# --------------------------------------------------------------------------- CLI
def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Query the rights-card retriever")
    ap.add_argument("query", nargs="?", help="query in Hindi, Hinglish or English")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--cards", default=DEFAULT_CARDS)
    ap.add_argument("--mode", choices=["bm25", "embed", "hybrid", "auto"], default=None)
    ap.add_argument("--download-model", action="store_true", help="fetch the embedding model once (needs internet)")
    a = ap.parse_args(argv)
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if a.download_model:
        os.environ["RETRIEVER_DOWNLOAD"] = "1"
        from fastembed import TextEmbedding

        TextEmbedding(MODEL_NAME, cache_dir=str(MODEL_DIR))
        print("model ready in", MODEL_DIR)
        return 0
    if not a.query:
        ap.error("query is required")
    try:
        r = Retriever(a.cards, mode=a.mode)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"mode={r.mode}  expansion={expand_query(a.query)!r}")
    for c in r.retrieve(a.query, a.k):
        print(f"{c['score']:.3f}  {c['id']:6s} {c['title_en']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
