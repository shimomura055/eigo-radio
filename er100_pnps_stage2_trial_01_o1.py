# -*- coding: utf-8 -*-
"""O1(0円・HTTP GETのみ): 7語の発音表記を無料源から取得試行。読取専用(er097.default_fetch再利用: GETのみ/サイズ上限/タイムアウト/redirect毎検査)。
R0: Wiktionary / Wikipedia(lead) / Wikidata(P898,P443) / 既存調査履歴に出た出典URLの本文(出現確認V1')。"""
import json, os, re, sys, time, urllib.parse
sys.path.insert(0, os.getcwd())
from er100_pnps_stage2_trial_01_common import *
import er097_pronunciation_supply_stage1_01 as S1
from er006_m1_multi_candidate_01 import ipa_to_arpa

SKIP_HOST = ("youtube.com", "instagram.com", "reddit.com", "facebook.com", "linkedin.com", "groups.google.com")
WIKI = {"toteme": ["Toteme"], "khaite": ["Khaite"], "altuzarra": ["Altuzarra", "Joseph_Altuzarra"], "zabelina": ["Zabelina"],
        "canele": ["Canelé", "Canele"], "meink": ["Troy_Meink", "Meink"], "melos": ["Melos", "Run,_Melos!", "Melos_(disambiguation)"]}
WIKT = {"toteme": ["Toteme"], "khaite": ["Khaite"], "altuzarra": ["Altuzarra"], "zabelina": ["Zabelina"], "canele": ["canelé", "canele"],
        "meink": ["Meink"], "melos": ["melos", "Melos"]}
IPA_RE = re.compile(r"[/\[]([^/\[\]\n]{2,40})[/\]]")
IPA_CH = re.compile(r"[ˈˌːɑɒæɛəɜɪʊʌɔθðʃʒŋɹɡɝɚ͡]")
_log = []


def get(url):
    t0 = time.time()
    try:
        raw = S1.default_fetch(url, timeout=8, max_bytes=600_000)
    except Exception as ex:
        _log.append({"url": url, "ok": False, "error": type(ex).__name__})
        return None
    _log.append({"url": url, "ok": raw is not None, "bytes": len(raw) if raw else 0, "sec": round(time.time() - t0, 2)})
    time.sleep(0.4)
    return raw


def windows(text, name, w=260):
    low = text.lower(); out = []; i = 0
    n = name.lower().replace("é", "e")
    low2 = low.replace("é", "e")
    while True:
        j = low2.find(n, i)
        if j < 0 or len(out) >= 6:
            break
        out.append(text[max(0, j - 40): j + w]); i = j + len(n)
    return out


def ipa_candidates(snips):
    c = []
    for s in snips:
        for m in IPA_RE.finditer(s):
            body = m.group(1).strip()
            if IPA_CH.search(body):
                c.append({"ipa": body, "arpa": ipa_to_arpa(body)})
    return c


def analyze(word, url, raw, kind):
    if raw is None:
        return {"url": url, "kind": kind, "fetched": False}
    text = S1.html_to_text(raw)
    nm = S1._words(word)
    present = S1._has_phrase(S1._words(text), nm)
    sn = windows(text, word) if present else []
    pr = [s for s in sn if re.search(r"pronounc|IPA|pronunciation|\bsay\b", s, re.I)]
    return {"url": url, "kind": kind, "fetched": True, "text_len": len(text), "name_in_page": present,
            "pron_marker_snippets": [re.sub(r"\s+", " ", s)[:300] for s in pr[:3]],
            "ipa_candidates": ipa_candidates(sn)[:6]}


def wikidata(word):
    out = {"search": [], "entities": []}
    q = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbsearchentities", "search": word, "language": "en", "format": "json", "limit": 6})
    raw = get(q)
    if not raw:
        return out
    try:
        res = json.loads(raw).get("search", [])
    except Exception:
        return out
    out["search"] = [{"id": r["id"], "label": r.get("label"), "desc": r.get("description")} for r in res]
    ids = [r["id"] for r in res]
    if ids:
        raw2 = get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids), "props": "claims|labels", "format": "json"}))
        try:
            ent = json.loads(raw2).get("entities", {})
        except Exception:
            ent = {}
        for i, e in ent.items():
            cl = e.get("claims", {})
            ipa = [x["mainsnak"].get("datavalue", {}).get("value") for x in cl.get("P898", [])]
            aud = [x["mainsnak"].get("datavalue", {}).get("value") for x in cl.get("P443", [])]
            out["entities"].append({"id": i, "label": e.get("labels", {}).get("en", {}).get("value"), "P898_ipa": ipa, "P443_audio": aud})
    return out


results = {}
rows = load_rows()
for w in TARGETS:
    res = {"word": w, "pages": [], "wikidata": None}
    urls = []
    for t in WIKT[w]:
        urls.append((f"https://en.wiktionary.org/wiki/{urllib.parse.quote(t)}", "wiktionary"))
    for t in WIKI[w]:
        urls.append((f"https://en.wikipedia.org/wiki/{urllib.parse.quote(t)}", "wikipedia"))
    seen = set(u for u, _ in urls)
    for r in rows:
        lk = (r.get("pronunciation_lookups") or {}).get(w)
        for u in (lk or {}).get("sources", []) or []:
            if u in seen or any(h in u for h in SKIP_HOST):
                continue
            seen.add(u); urls.append((u, "prior_research_source"))
    for u, k in urls[:40]:
        res["pages"].append(analyze(w, u, get(u), k))
    res["wikidata"] = wikidata(w if w != "canele" else "canelé")
    results[w] = res
    print(w, len(res["pages"]), sum(1 for p in res["pages"] if p.get("fetched")), flush=True)
json.dump({"results": results, "http_log": _log}, open(f"{OUT}/o1_free_sources.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("http calls", len(_log), "ok", sum(x["ok"] for x in _log))
