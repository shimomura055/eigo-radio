# census_01.py -- ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01 §1(d)。保存済みASR記録の読取専用集計(API 0・Production無変更)。
# 母集団=er109_stored_census_01.rows_from_results と同一(全 *tts_generation_results*.json の本文segment+KP英語 attempts_log)。
# CMU未登録語(OOV)を含むsegmentと含まないsegmentで、Primary NG率/再試行率/Azure呼出率/最終STOP率を比較し、
# 「Primary NGの全差分spanがOOV語を含む」型(gacha->gotcha型)を機械抽出する。
import collections, glob, json, os, re, sys
sys.path.insert(0, ".")
import er109_stored_census_01 as C
import er008_asr_variant_hardening_15_homophone_en as hp

TOK = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")
def norm(t):
    return TOK.findall((t or "").lower().replace("’", "'"))

_cache = {}
def has_cmu(tok):
    if tok in _cache: return _cache[tok]
    cands = [tok]
    if tok.endswith("'s"): cands.append(tok[:-2])
    if tok.endswith("s"): cands.append(tok[:-1])
    if tok.endswith("'"): cands.append(tok[:-1])
    ok = any(hp._phone_variants(c) for c in cands)
    _cache[tok] = ok
    return ok

def is_oov(tok):
    return tok.isalpha() and len(tok) >= 3 and not has_cmu(tok)

import difflib
def spans(c, a):
    sm = difflib.SequenceMatcher(None, c, a, autojunk=False)
    return [(op, c[i1:i2], a[j1:j2]) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]

def main():
    files = sorted(glob.glob("**/*tts_generation_results*.json", recursive=True))
    files = [f for f in files if ".venv" not in f and "node_modules" not in f]
    rows = []
    for f in files:
        rows += C.rows_from_results(f)
    # attempt-levelのprimary pass
    for r in rows:
        r["primary_pass"] = (r["stored_cls"] in C.PASS_LABELS) if r["stored_cls"] else None
        r["canon_toks"] = norm(r["canonical"])
        r["oov"] = sorted({t for t in r["canon_toks"] if is_oov(t)})
    print("files", len(files), "rows", len(rows))
    seg = collections.defaultdict(list)
    for r in rows: seg[(r["src"], r["seg"])].append(r)
    def stats(label, groups):
        n_seg = len(groups); n_att = sum(len(g) for g in groups)
        ng_att = sum(1 for g in groups for r in g if r["primary_pass"] is False)
        known = sum(1 for g in groups for r in g if r["primary_pass"] is not None)
        retried = sum(1 for g in groups if len(g) > 1)
        azure = sum(1 for g in groups for r in g if r.get("azure"))
        stopped = sum(1 for g in groups if g[0]["final_status"] not in ("OK", None))
        print(f"{label}: segments={n_seg} attempts={n_att} primaryNG_attempts={ng_att}/{known} ({100*ng_att/max(1,known):.1f}%) segments_with_retry={retried} ({100*retried/max(1,n_seg):.1f}%) azure_text_rows={azure} final_not_OK={stopped} ({100*stopped/max(1,n_seg):.1f}%)")
        return dict(segments=n_seg, attempts=n_att, primary_ng_attempts=ng_att, known=known, segments_with_retry=retried, azure_rows=azure, final_not_ok=stopped)
    with_oov = [g for g in seg.values() if any(r["oov"] for r in g[:1])]
    without = [g for g in seg.values() if not any(r["oov"] for r in g[:1])]
    out = {"files": len(files), "rows": len(rows), "segments": len(seg)}
    out["with_oov"] = stats("CMU-OOV語を含むsegment", with_oov)
    out["without_oov"] = stats("OOV語なしsegment", without)
    # 1 OOV tokenごとの出現頻度
    cnt = collections.Counter()
    for g in seg.values():
        for t in g[0]["oov"]: cnt[t] += 1
    out["oov_top"] = cnt.most_common(80)
    # OOV-only diff 型の抽出
    oov_only = []; oov_involved = 0; ng_rows = 0
    for r in rows:
        if r["primary_pass"] is not False or not r["asr"]: continue
        ng_rows += 1
        sp = spans(r["canon_toks"], norm(r["asr"]))
        if not sp: continue
        inv = [s for s in sp if any(t in r["oov"] for t in s[1])]
        if inv: oov_involved += 1
        if inv and len(inv) == len(sp):
            oov_only.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "spans": [(s[0], " ".join(s[1]), " ".join(s[2])) for s in sp], "final_status": r["final_status"], "azure": bool(r.get("azure")), "kp": r["kp"]})
    out["ng_rows"] = ng_rows; out["ng_rows_with_oov_span"] = oov_involved; out["oov_only_ng_rows"] = len(oov_only)
    out["oov_only_examples"] = oov_only
    print("primary NG rows", ng_rows, "うちOOV語がdiff spanに関与", oov_involved, "うちOOV-only(全spanがOOV関与)", len(oov_only))
    json.dump(out, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/census_01_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
main()

# ---- 追補: 固有名詞(大文字始まり)を除いた「一般語型OOV」(借用語・造語・新語・サービス名の小文字表記)に限定した集計 ----
def common_oov(canon_text):
    caps = set(); lows = set()
    for m in re.finditer(r"[A-Za-z][A-Za-z']*", canon_text):
        w = m.group(0)
        (lows if w[0].islower() else caps).add(w.lower().strip("'"))
    return {t for t in lows if is_oov(t) and len(t) >= 4}

def main2():
    files = [f for f in sorted(glob.glob("**/*tts_generation_results*.json", recursive=True)) if ".venv" not in f]
    rows = []
    for f in files: rows += C.rows_from_results(f)
    for r in rows:
        r["primary_pass"] = (r["stored_cls"] in C.PASS_LABELS) if r["stored_cls"] else None
        r["ct"] = norm(r["canonical"]); r["coov"] = common_oov(r["canonical"])
    seg = collections.defaultdict(list)
    for r in rows: seg[(r["src"], r["seg"])].append(r)
    cnt = collections.Counter(t for g in seg.values() for t in g[0]["coov"])
    print("一般語型OOV(小文字出現)上位:", cnt.most_common(40))
    gs = [g for g in seg.values() if g[0]["coov"]]
    ng = sum(1 for g in gs for r in g if r["primary_pass"] is False); kn = sum(1 for g in gs for r in g if r["primary_pass"] is not None)
    rt = sum(1 for g in gs if len(g) > 1)
    print(f"一般語型OOVを含むsegment={len(gs)} NG attempts={ng}/{kn} ({100*ng/max(1,kn):.1f}%) retry segments={rt} ({100*rt/max(1,len(gs)):.1f}%)")
    hits = []
    for r in rows:
        if r["primary_pass"] is not False or not r["coov"] or not r["asr"]: continue
        sp = spans(r["ct"], norm(r["asr"]))
        inv = [s for s in sp if any(t in r["coov"] for t in s[1])]
        if inv:
            hits.append({"src": r["src"], "seg": r["seg"], "attempt": r["attempt"], "all_spans_oov": len(inv) == len(sp), "spans": [(s[0], " ".join(s[1]), " ".join(s[2])) for s in sp], "final_status": r["final_status"], "azure": bool(r.get("azure"))})
    print("一般語型OOVがdiff spanに関与したPrimary NG rows:", len(hits), "うち全span OOV:", sum(h["all_spans_oov"] for h in hits))
    by = collections.Counter()
    for h in hits:
        for s in h["spans"]:
            by[(s[1], s[2])] += 1
    print(by.most_common(40))
    json.dump({"common_oov_top": cnt.most_common(100), "n_segments": len(gs), "ng": ng, "known": kn, "retry_segments": rt, "hits": hits}, open("docs/research/ASR-OOV-HOMOPHONE-ROOT-CAUSE-01/census_02_common_oov.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
main2()
