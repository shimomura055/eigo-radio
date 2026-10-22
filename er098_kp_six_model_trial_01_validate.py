# -*- coding: utf-8 -*-
"""FAMILY-X-KP-SELECTION-SIX-MODEL-COMPARISON-TRIAL-01 委任_01: 機械検証(API 0)。Trial専用。
規則(TRIAL_DESIGN_01.md 5節):
 語数=スペース区切り個数 / 5語以内 / 本文一致: (a)連続部分列(大小文字・末尾句読点・引用符種別のみ正規化)
 (b)一般化(placeholderを可変長wildcard)で一意に原文spanを特定=確認済み、複数=要確認、なし=NG。無条件PASSは作らない。
 自己申告語数との不一致は違反とせず「不一致」として別記録。既存Production KPも同じ規則で検証する(比較基準)。"""
import json, re, sys
from pathlib import Path
import er098_kp_six_model_trial_01_common as C

PLACEHOLDERS_CS = {"A", "B", "X", "Y", "A's", "B's", "A/B", "B/A", "sb", "sth", "sb's"}          # 大文字小文字区別
PLACEHOLDERS_CI = {"someone", "something", "somebody", "someone's", "somebody's", "something's", "one's", "oneself", "someone/something", "something/someone"}
BSL = chr(92)
WILD = r"(\S+(?:\s+\S+){0,7}?)"
WILD_ONES = r"(\S+(?:\s+\S+){0,1}?)"

def norm(s):
    tbl = {"’": "'", "‘": "'", "ʼ": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "}
    o = []
    for ch in s:
        ch = tbl.get(ch, ch); l = ch.lower()
        o.append(l if len(l) == 1 else ch)
    r = "".join(o); assert len(r) == len(s); return r

def norm_keep(s):
    tbl = {"’": "'", "‘": "'", "ʼ": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "}
    return "".join(tbl.get(ch, ch) for ch in s)

def clean_cand_raw(c):
    c = norm_keep(c).strip().strip("\"'` ")
    c = re.sub(r"[.,;:!?)\]]+$", "", c).strip()
    return re.sub(r"^[(\[]+", "", c).strip()

def clean_cand(c):
    c = norm(c).strip()
    c = c.strip("\"'` ")
    c = re.sub(r"[.,;:!?)\]]+$", "", c).strip()
    c = re.sub(r"^[(\[]+", "", c).strip()
    return c

def is_ph(tok):
    t = tok.strip(".,;:!?\"'")
    return ("~" in tok) or tok in PLACEHOLDERS_CS or t in PLACEHOLDERS_CS or tok.lower() in PLACEHOLDERS_CI or t.lower() in PLACEHOLDERS_CI


IRREG = {"took": "take", "taken": "take", "gave": "give", "given": "give", "went": "go", "gone": "go", "came": "come", "got": "get", "gotten": "get", "made": "make", "ran": "run",
         "said": "say", "saw": "see", "seen": "see", "held": "hold", "brought": "bring", "thought": "think", "fell": "fall", "fallen": "fall", "rose": "rise", "risen": "rise",
         "kept": "keep", "left": "leave", "told": "tell", "found": "find", "set": "set", "put": "put", "cut": "cut", "was": "be", "were": "be", "is": "be", "are": "be", "been": "be",
         "became": "become", "begun": "begin", "began": "begin", "chose": "choose", "chosen": "choose", "drew": "draw", "drawn": "draw", "grew": "grow", "grown": "grow", "knew": "know", "known": "know", "showed": "show", "shown": "show", "threw": "throw", "thrown": "throw", "wrote": "write", "written": "write", "stood": "stand", "led": "lead", "paid": "pay", "sold": "sell", "sent": "send", "spent": "spend", "broke": "break", "broken": "break", "lost": "lose", "won": "win", "built": "build", "meant": "mean", "met": "meet", "heard": "hear", "felt": "feel", "slid": "slide", "hid": "hide",
         "his": "<p>", "her": "<p>", "their": "<p>", "its": "<p>", "my": "<p>", "your": "<p>", "our": "<p>", "one's": "<p>"}
def stem(w):
    w = w.lower().strip(".,;:!?\"'()[]“”‘’—–-")
    if w.endswith("'s"): w = w[:-2]
    if w in IRREG: w = IRREG[w]
    else:
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) > len(suf) + 2 and not (suf == "s" and w.endswith("ss")):
                w = w[:-len(suf)]; break
    if w.endswith("e") and len(w) > 3: w = w[:-1]
    if len(w) > 3 and w[-1] == w[-2] and w[-1] not in "ls": w = w[:-1]
    return w

def loose_find(ctoks, ph, art):
    """活用形・所有格代名詞の差のみ許す参考検索(厳密規則ではNG。区別して記録するための分類)。"""
    atoks = [(m.group(0), m.start(), m.end()) for m in re.finditer(r"\S+", art)]
    ast = [stem(t[0]) for t in atoks]
    cst = [stem(t) for t in ctoks]
    def rec(ci, ai):
        if ci == len(ctoks): return ai
        if ph[ci]:
            for n in range(1, 9):
                if ai + n > len(atoks): break
                r = rec(ci + 1, ai + n)
                if r is not None: return r
            return None
        if ai < len(atoks) and ast[ai] == cst[ci]:
            if cst[ci] == "<p>" or True: return rec(ci + 1, ai + 1)
        return None
    for st in range(len(atoks)):
        if ph[0] and st > 0 and False: continue
        e = rec(0, st)
        if e is not None:
            return atoks[st][1], atoks[e - 1][2]
    return None

def validate_phrase(phrase, art, art_n):
    r = dict(phrase=phrase)
    toks = phrase.split()
    r["words_actual"] = len(toks)
    r["within_5"] = len(toks) <= 5 and len(toks) >= 1
    cn = clean_cand(phrase)
    if not cn:
        r.update(match_type="NG_EMPTY", span_text=None); return r
    ctoks_raw = clean_cand_raw(phrase).split()
    ctoks = [t.lower() for t in ctoks_raw]
    B = r"(?<![A-Za-z0-9])"; E = r"(?![A-Za-z0-9])"
    # (a) 厳密(大小文字・引用符・末尾句読点のみ正規化)
    pat = B + r"\s+".join(re.escape(t) for t in ctoks) + E
    m = re.search(pat, art_n)
    if m:
        r.update(match_type="A_EXACT", span_text=art[m.start():m.end()], span_start=m.start(), span_end=m.end(), generalization=[]); return r
    # (b) 一般化: placeholderをwildcard化(原文の大文字小文字区別せず)
    ph = [is_ph(t) for t in ctoks_raw]
    if not any(ph):
        lf = loose_find(ctoks, ph, art)
        if lf:
            r.update(match_type="NG_INFLECTION_ONLY", span_text=art[lf[0]:lf[1]], span_start=lf[0], span_end=lf[1], note="本文と活用形・所有格代名詞のみ相違(厳密規則では変更=NG、創作ではない)")
        else:
            r.update(match_type="NG_NO_MATCH", span_text=None, note="placeholderなし・連続部分列として本文に存在しない(言い換え/創作)")
        return r
    if all(ph):
        r.update(match_type="NG_ONLY_PLACEHOLDER", span_text=None); return r
    parts = []
    for t, p in zip(ctoks, ph):
        if p:
            w = WILD_ONES if t.lower() in ("one's", "oneself") else WILD
            if t.lower().rstrip("'s") in ("someone", "something", "somebody") and t.endswith("'s"):
                w = WILD
            if "~" in t and len(t) > 1:     # 語内に埋め込まれた~(例: ~-led, $~)は1語内wildcard
                w = ("(" + BSL + "S+?)").join(re.escape(x) for x in t.split("~"))
            parts.append(w)
        else:
            parts.append(re.escape(t))
    pat = B + r"\s+".join(parts) + E
    rx = re.compile(pat)
    spans = []; pos = 0
    while True:
        m = rx.search(art_n, pos)
        if not m: break
        spans.append((m.start(), m.end(), [g for g in m.groups()]))
        pos = m.start() + 1
    # 重複span除去
    seen = set(); uniq = []
    for s, e, g in spans:
        if (s, e) not in seen: seen.add((s, e)); uniq.append((s, e, g))
    if not uniq:
        lf = loose_find(ctoks, ph, art)
        if lf:
            r.update(match_type="NG_INFLECTION_ONLY", span_text=art[lf[0]:lf[1]], span_start=lf[0], span_end=lf[1], note="一般化後も活用形のみ相違")
        else:
            r.update(match_type="NG_NO_MATCH", span_text=None, note="一般化後wildcard照合でも本文に存在しない")
        return r
    s, e, g = uniq[0]
    phs = [t for t, p in zip(ctoks_raw, ph) if p]
    gen = [dict(placeholder=t, original=art[a:b] if False else None) for t in phs]
    # wildcard捕捉語を原文から復元(正規化後と同一長なのでオフセットで取り出せる)
    m = rx.search(art_n, s)
    gen = []
    for i, t in enumerate(phs):
        gs, ge = m.span(i + 1)
        gen.append(dict(placeholder=t, original=art[gs:ge].rstrip(".,;:!?)\"”’")))
    e = s + len(art[s:e].rstrip(".,;:!?)\"”’"))
    r.update(match_type="B_GEN_UNIQUE" if len({art[a:b].lower() for a, b, _ in uniq}) == 1 else "B_GEN_AMBIGUOUS", span_text=art[s:e], span_start=s, span_end=e, generalization=gen, n_matches=len(uniq), n_distinct_texts=len({art[a:b].lower() for a, b, _ in uniq}),
             all_spans=[art[a:b] for a, b, _ in uniq[:5]])
    return r

CONFIRMED = {"A_EXACT", "B_GEN_UNIQUE"}
# 抽出(パース)の手動指定(モデル出力は無改変。同一出力内の『選定表』と『各表現の意味』説明リストが併存する場合、選定表=グループ0を採用)。TRIAL_RESULT_01.md に記載
PARSE_OVERRIDES = {"m6_claude-sonnet-5-5/D_Advanced": 0, "m6_claude-sonnet-5-5/E_Advanced": 0}

def validate_set(cands, art):
    art_n = norm(art)
    out = []; seen = {}
    for i, c in enumerate(cands):
        v = validate_phrase(c["phrase"], art, art_n)
        v["rank"] = i + 1; v["self_count"] = c.get("self_count")
        v["self_count_mismatch"] = (c.get("self_count") is not None and c["self_count"] != v["words_actual"])
        k = clean_cand(c["phrase"])
        v["duplicate_of"] = seen.get(k); seen.setdefault(k, i + 1)
        v["strict_pass"] = bool(v["within_5"] and v["match_type"] in CONFIRMED and v["duplicate_of"] is None)
        out.append(v)
    return out

def main():
    out = C.OUT; man = json.loads((out / "inputs" / "manifest.json").read_text(encoding="utf8"))
    units = {u["unit_id"]: u for u in man["units"] if u.get("copy_path")}
    res = {"generated_by": "er098_kp_six_model_trial_01_validate.py", "rules": "TRIAL_DESIGN_01.md 5節", "sets": []}
    # モデル出力
    for rp in sorted((out / "runs").glob("*/*.json")):
        d = json.loads(rp.read_text(encoding="utf8"))
        u = units[d["unit_id"]]
        art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        if not d.get("ok"):
            res["sets"].append(dict(source=d["model_key"], unit_id=d["unit_id"], status="TECH_FAIL", candidates=[])); continue
        pinfo = {}
        fg = PARSE_OVERRIDES.get("%s/%s" % (d["model_key"], d["unit_id"]))
        cands = C.parse_candidates(d["response_text"], pinfo, force_group=fg)
        if fg is not None: pinfo["override_group"] = fg
        vs = validate_set(cands, art)
        res["sets"].append(dict(source=d["model_key"], unit_id=d["unit_id"], status="OK", n_parsed=len(cands), n_over5=len(cands) > 5, finish=d.get("finish"), parse_info=pinfo, candidates=vs))
    # 既存Production KP(比較基準・同規則で検証)
    for uid, u in units.items():
        art = (C.ROOT / u["copy_path"]).read_text(encoding="utf8")
        cands = [dict(phrase=k["key_phrase"], self_count=None) for k in u.get("production_kp", [])]
        res["sets"].append(dict(source="production", unit_id=uid, status="OK", n_parsed=len(cands), n_over5=False, candidates=validate_set(cands, art)))
    (out / "validation.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf8")
    # 集計表示
    agg = {}
    for s in res["sets"]:
        a = agg.setdefault(s["source"], dict(n=0, w5=0, confirmed=0, ambiguous=0, ng=0, mismatch=0, dup=0, sets=0, sets_ok=0))
        a["sets"] += 1
        if s["status"] != "OK": continue
        a["sets_ok"] += 1
        for v in s["candidates"]:
            a["n"] += 1; a["w5"] += v["within_5"]; a["confirmed"] += v["match_type"] in CONFIRMED
            a["ambiguous"] += v["match_type"] == "B_GEN_AMBIGUOUS"; a["ng"] += v["match_type"].startswith("NG"); a["infl"] = a.get("infl", 0) + (v["match_type"] == "NG_INFLECTION_ONLY"); a["mismatch"] += v["self_count_mismatch"]; a["dup"] += v["duplicate_of"] is not None
    print(json.dumps(agg, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    sys.exit(main())
