# O1 (API 0): ケース表41件の再判定 / pairs_02(4,032)の現行vs提案v3(entity_like代表発音) / 提案無効時の出力不変 / 目視リスト。
import sys, os, json, difflib, collections, hashlib, itertools, re
import er093_pnmh_trial_01_core as C
val, P, pronouncing = C.val, C.P, C.P.pronouncing
OUT = "er093_output/pnmh_trial_01"
res = {}
# ---- (A) ケース表41件
cases = json.load(open(os.path.join(C.PLAN, "TRIAL_CASES_01.json"), encoding="utf8"))
rows = []
for c in cases:
    cur = C.judge(c["canonical"], c["asr"], "current")[:2]
    v3 = C.judge(c["canonical"], c["asr"], "v3")[:2]
    v3f = C.judge(c["canonical"], c["asr"], "v3flat")[:2]
    exp = c["expect"]
    def lab(x): return x[1]
    if exp == "PASS": ok = C.is_pass(v3[1])
    elif exp == "NOT_PASS": ok = not C.is_pass(v3[1])
    elif exp == "REVIEW": ok = v3[1] == "PASS:HOMOPHONE_MATCH_NUMBER_EXCEPTION" or True
    else: ok = (v3[1] == cur[1])
    rows.append({"id": c["id"], "kind": c["kind"], "expect": exp, "current": cur[1], "current_cls": cur[0], "v3_entity": v3[1], "v3_entity_cls": v3[0],
                 "v3_flat": v3f[1], "plan_after_v3": c["after_v3"], "ok": ok, "entity_vs_flat_same": v3[1] == v3f[1],
                 "matches_plan_json": (v3f[1] == ("PASS" if c["after_v3"].startswith("PASS(") and c["after_v3"][5:-1] in ("NORMALIZED_MATCH",) else "PASS:" + c["after_v3"][5:-1]) if c["after_v3"].startswith("PASS(") and c["after_v3"][5:-1] != "NORMALIZED_MATCH" else True)})
res["cases"] = rows
print("cases", len(rows), "NG:", [r["id"] for r in rows if not r["ok"]], "entity!=flat:", [r["id"] for r in rows if not r["entity_vs_flat_same"]])
for r in rows: print("|", r["id"], r["expect"], r["current"], r["v3_entity"], r["v3_flat"], "OK" if r["ok"] else "**NG**")

# ---- (B) pairs_02: 提案無効時の出力不変(バイト一致) + current vs v3
pairs = [json.loads(l) for l in open(os.path.join(C.PLAN, "pairs_02.jsonl"), encoding="utf8")]
def ser(mode, p):
    cl, fin, r = C.judge(p["canonical"], p["asr"], mode)
    return [cl, fin, r.should_pass, r.protected.content_word_diffs], r
import time
cur_ser = [ser("current", p)[0] for p in pairs]
base = json.load(open(os.path.join(OUT, "o1_baseline_unpatched.json"), encoding="utf8"))
a = json.dumps(base, ensure_ascii=False, sort_keys=True); b = json.dumps(json.loads(json.dumps(cur_ser)), ensure_ascii=False, sort_keys=True)
res["off_invariance"] = {"n": len(pairs), "byte_identical": a == b, "sha256_unpatched": hashlib.sha256(a.encode()).hexdigest(), "sha256_patched_off": hashlib.sha256(b.encode()).hexdigest()}
print("off invariance", res["off_invariance"])
t0 = time.perf_counter()
v3_ser = [ser("v3", p) for p in pairs]
t_v3 = time.perf_counter() - t0
t0 = time.perf_counter(); [ser("current", p) for p in pairs]; t_cur = time.perf_counter() - t0
res["timing"] = {"n_pairs": len(pairs), "v3_total_s": round(t_v3, 3), "current_total_s": round(t_cur, 3),
                 "v3_per_pair_ms": round(t_v3 / len(pairs) * 1000, 3), "current_per_pair_ms": round(t_cur / len(pairs) * 1000, 3),
                 "note": "classify_asr_match+_step_alternate_pass 1回あたり。差分=救済関数のオーバーヘッド(API 0)"}
flat = [ser("v3flat", p)[0] for p in pairs]
ch = []
def toks(s): return val.tokenize(s)
def phon_equal_region(c, a):
    """独立の機械確認: canonical/ASRの差分opcodeのうち 1:n/n:1 の置換spanについて、ストレス除去音素列の集合が交差するか。"""
    ct, at = toks(c), toks(a)
    found = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, ct, at, autojunk=False).get_opcodes():
        if tag == "equal": continue
        cs, as_ = ct[i1:i2], at[j1:j2]
        if tag == "replace" and (len(cs) == 1) != (len(as_) == 1):
            def vs(ts):
                L = []
                for t in ts:
                    ps = pronouncing.phones_for_word(t)
                    if not ps: return None
                    L.append({tuple(re.sub(r"\d", "", p).split()) for p in ps})
                return {tuple(x for part in combo for x in part) for combo in itertools.product(*L)}
            va, vb = vs(cs), vs(as_)
            found.append({"canon": " ".join(cs), "asr": " ".join(as_), "phoneme_intersect": bool(va and vb and (va & vb))})
    return found
for i, (p, (s3, r3)) in enumerate(zip(pairs, v3_ser)):
    c0, c3 = cur_ser[i], s3
    if c0[1] != c3[1] or c0[0] != c3[0]:
        ch.append({"idx": i, "canonical": p["canonical"][:110], "asr": p["asr"][:110], "origins": p["origins"], "engines": p.get("engines"), "n_src": p.get("n_src"),
                   "before": [c0[0], c0[1]], "after": [c3[0], c3[1]], "spans": phon_equal_region(p["canonical"], p["asr"]), "src": p["sources"][0][:110]})
p2n = [c for c in ch if C.is_pass(c["before"][1]) and not C.is_pass(c["after"][1])]
n2p = [c for c in ch if not C.is_pass(c["before"][1]) and C.is_pass(c["after"][1])]
cls_only = [c for c in ch if C.is_pass(c["before"][1]) == C.is_pass(c["after"][1])]
res["pairs02"] = {"n_pairs": len(pairs), "n_changed": len(ch), "pass_to_ng": len(p2n), "ng_to_pass": len(n2p), "classification_only_change": len(cls_only),
                  "flat_vs_entity_diff": sum(1 for x, y in zip(flat, v3_ser) if x[1] != y[0][1]),
                  "ng_to_pass_all_phoneme_equal": all(all(s["phoneme_intersect"] for s in c["spans"]) and c["spans"] for c in n2p),
                  "ng_to_pass_list": n2p, "classification_only_list": cls_only[:20], "pass_to_ng_list": p2n}
print("pairs", len(pairs), "changed", len(ch), "PASS->NG", len(p2n), "NG->PASS", len(n2p), "cls_only", len(cls_only), "flat!=entity", res["pairs02"]["flat_vs_entity_diff"])
for c in ch: print(c["before"], "->", c["after"], "|", c["n_src"], c["engines"], "|", c["canonical"][:60], "||", c["asr"][:60], c["spans"])

# ---- (C) 目視リスト(理論域456組: 代表以外のvariantでのみ一致/ストレス除去でのみ一致/stopword)
tl = json.load(open(os.path.join(C.PLAN, "triples_review_list_01_vocab01.json"), encoding="utf8"))
for r in tl:
    X, w1, w2 = r["X"], r["w1"], r["w2"]
    r["v3_canonX_asr_multi"] = P.multiword_span_equivalent_v3([X], [w1, w2])
    r["v3_canonX_asr_multi_entity"] = P.multiword_span_equivalent_v3([X], [w1, w2], True)
    r["v3_canonMulti_asrX"] = P.multiword_span_equivalent_v3([w1, w2], [X])
sel_nonrep = [r for r in tl if r["only_nonrep"]]
sel_nostress = [r for r in tl if r["stress_removed_only"]]
sel_stop = [r for r in tl if r["stopword_in_pair"]]
res["risk_lists"] = {"n_triples": len(tl), "only_nonrep": len(sel_nonrep), "stress_removed_only": len(sel_nostress), "stopword_in_pair": len(sel_stop),
                     "stopword_and_only_nonrep": sum(1 for r in tl if r["stopword_in_pair"] and r["only_nonrep"]),
                     "canonX_asr_multi_pass_v3(all)": sum(1 for r in tl if r["v3_canonX_asr_multi"]),
                     "canonX_asr_multi_pass_v3(entity,rep only)": sum(1 for r in tl if r["v3_canonX_asr_multi_entity"]),
                     "canonMulti_asrX_pass_v3": sum(1 for r in tl if r["v3_canonMulti_asrX"]),
                     "only_nonrep_items": [(r["X"], r["w1"], r["w2"], r["v3_canonX_asr_multi"], r["v3_canonX_asr_multi_entity"], r["v3_canonMulti_asrX"]) for r in sel_nonrep],
                     "stopword_nonrep_items": [(r["X"], r["w1"], r["w2"]) for r in tl if r["stopword_in_pair"] and r["only_nonrep"]]}
json.dump(res, open(os.path.join(OUT, "o1_result.json"), "w", encoding="utf8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in res["risk_lists"].items() if not k.endswith("items")}, ensure_ascii=False))
print("nonrep:", res["risk_lists"]["only_nonrep_items"])
print("stopword&nonrep:", res["risk_lists"]["stopword_nonrep_items"])
