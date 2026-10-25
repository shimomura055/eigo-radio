# OPEN-517是正案 v4 API 0再評価(事前登録=OPEN517_PREREGISTERED_02.md)。保存済み転写のみ・LLM/ASR/TTS呼出0(socket guard)。Production file無変更。
# 対象: 既存771件(open517_api0_eval_03.out.json rows)+未知データ(unknown_pool_02.json、collect_unknown_pool_02.py)
# 比較: 現行(Productionそのまま) / v3(proto_value_gate_fix_03.apply_in_process) / v4(proto_value_gate_fix_04.apply_in_process)
# 出力: open517_api0_eval_04.out.json / 標準出力。再現: リポジトリrootで PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_open517_api0_04.py
import collections, difflib, hashlib, json, sys
sys.path.insert(0, "."); sys.path.insert(0, "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01")
import eval_common_02 as E
import proto_value_gate_fix_03 as F3
import proto_value_gate_fix_04 as F4
import er078_asr_value_guard_01 as vg

D = "docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/"
READ = ("PHONETIC_MATCH", "READING_RESOLVED_MATCH")
KNOWN_NEG = {"N1-er066a-028", "N1-er066b-020", "N1-er066b-022", "N1-prodbug-006", "N1-prodbug-007", "N1-new-042", "N1-new-044", "N1-new-057", "N3-02"}
corpus = json.load(open(D + "open517_api0_eval_03.out.json", encoding="utf8"))["rows"]
unknown = json.load(open(D + "unknown_pool_02.json", encoding="utf8"))
items = [(r["src"], r["id"], r["canon"], r["asr"]) for r in corpus]
items += [("U:" + u["family"], u["sources"][0], u["canon"], u["asr"]) for u in unknown]
PASSING = E.uj.PASSING_STATES
E.api0_guard_on()
rows = []
for src, ident, canon, asr in items:
    b = E.primary_stage(canon, asr, False)
    with F3.apply_in_process():
        f3 = E.primary_stage(canon, asr, False)
    log = []
    with F4.apply_in_process(log=log):
        f4 = E.primary_stage(canon, asr, False)
    fired = []
    for c, t, info in log:
        fired.append({"replaced": [list(x) for x in info.replaced], "canon2": info.canon2, "text2": info.text2})
    fb = []
    with F4.apply_in_process(log=None):
        pass
    # monotonic guardのfallback件数(READING_MATCH PASSの最終ゲートで発動しなかった理由): 純関数で再現
    if b["primary_pass"] and b["label"] in READ:
        _, info = F4.value_guard_fixed_detail(canon, asr)
        fb = info.fallback
    else:
        fb = None
    rows.append({"src": src, "id": ident, "canon": canon, "asr": asr,
                 "base_state": b["state"], "base_reason": b["reason"], "base_label": b["label"], "base_warn": sorted(b["warnings"]),
                 "v3_state": f3["state"], "v3_reason": f3["reason"], "v3_warn": sorted(f3["warnings"]),
                 "fix_state": f4["state"], "fix_reason": f4["reason"], "fix_label": f4["label"], "fix_warn": sorted(f4["warnings"]),
                 "f2_fired": fired, "f2_fallback": fb, "known_neg": ident in KNOWN_NEG})
E.api0_guard_off()


def passing(s): return s in PASSING
def _rs(x): return "primary_pass" if str(x).startswith("primary_pass") else x
def sig(r, p): return (r[p + "_state"], _rs(r[p + "_reason"]))


def chg(rs, p="fix"):
    return [r for r in rs if (r["base_state"], _rs(r["base_reason"]), r["base_label"]) != (r[p + "_state"], _rs(r[p + "_reason"]), r.get("fix_label") if p == "fix" else r["base_label"])]


known_rows = [r for r in rows if not r["src"].startswith("U:")]
unk_rows = [r for r in rows if r["src"].startswith("U:")]
print(f"items: {len(rows)} = corpus {len(known_rows)} + unknown {len(unk_rows)}; unknown by family {dict(collections.Counter(r['src'] for r in unk_rows))}")
base_read_pass = [r for r in rows if passing(r["base_state"]) and r["base_label"] in READ]
print(f"base READING_MATCH PASS: {len(base_read_pass)} (corpus {sum(1 for r in base_read_pass if not r['src'].startswith('U:'))} / unknown {sum(1 for r in base_read_pass if r['src'].startswith('U:'))})")


def show(rs, tag):
    for r in rs:
        print(f" {tag} {r['src']} {r['id'][-70:]} | {r['canon'][:30]} | {r['asr'][:30]} | {r['base_state']}/{r['base_reason']}/{r['base_label']} -> v4 {r['fix_state']}/{r['fix_reason']} (v3 {r['v3_state']}) warn {r['base_warn']}->{r['fix_warn']}")


changed = [r for r in rows if (r["base_state"], _rs(r["base_reason"])) != (r["fix_state"], _rs(r["fix_reason"])) or r["base_warn"] != r["fix_warn"]]
print(f"== 判定/警告が変わった全件(現行 -> v4): {len(changed)} (corpus {sum(1 for r in changed if not r['src'].startswith('U:'))} / unknown {sum(1 for r in changed if r['src'].startswith('U:'))}) ==")
show(changed, "CHG")
# 基準1: 正常attempt
normal = [r for r in base_read_pass if r["src"] in ("P4", "POS")]
ng_normal = [r for r in normal if not passing(r["fix_state"])]
print(f"[K1] 正常attempt(P4+正例対照のREADING_MATCH PASS {len(normal)}件)のNG化/降格: {len(ng_normal)}")
show(ng_normal, "K1")
kn = [r for r in rows if r["known_neg"]]
k2_ok = len(kn) == 9 and all(passing(r["base_state"]) and not passing(r["fix_state"]) for r in kn)
print("[K2] 既知負例(現行READING_MATCH PASS)9件が全てPASS以外へ:", k2_ok)
for r in kn: print("    ", r["id"], r["canon"][:20], "|", r["asr"][:20], "->", r["fix_state"], r["fix_reason"])
ich = [r for r in rows if "いちばん低い" in r["canon"] + r["asr"] or "一番低い" in r["canon"] + r["asr"]]
print("[K1b] いちばん/一番の件:", [(r["id"][-40:], r["base_state"], r["fix_state"]) for r in ich])
# 基準3
f1_chg = [r for r in changed if passing(r["base_state"]) and r["base_label"] in READ and not passing(r["fix_state"])]
warn_add = [r for r in changed if passing(r["base_state"]) and passing(r["fix_state"]) and set(r["base_warn"]) < set(r["fix_warn"]) and (r["base_state"], _rs(r["base_reason"])) != None]
other = [r for r in changed if r not in f1_chg and r not in warn_add]
nonread_pass_changed = [r for r in rows if passing(r["base_state"]) and r["base_label"] not in READ and (r["base_state"], _rs(r["base_reason"])) != (r["fix_state"], _rs(r["fix_reason"]))]
ng_to_pass = [r for r in rows if (not passing(r["base_state"])) and passing(r["fix_state"])]
lost_warn = [r for r in rows if passing(r["base_state"]) and passing(r["fix_state"]) and not set(r["base_warn"]) <= set(r["fix_warn"])]
print(f"[K3] 変化の分類: F1(READING_MATCH PASS->not PASS)={len(f1_chg)} / PASS->PASS(警告追加)={len(warn_add)} / other={len(other)}")
show(other, "OTHER")
print(f"[K3] 非READING_MATCH PASSの変化: {len(nonread_pass_changed)} / NG->PASS: {len(ng_to_pass)} / 警告の喪失: {len(lost_warn)}")
show(lost_warn, "LOSTWARN")
# 未知データ(基準8)
u_changed = [r for r in changed if r["src"].startswith("U:")]
print(f"[K8] 未知データ {len(unk_rows)}件(現行READING_MATCH PASS {sum(1 for r in unk_rows if passing(r['base_state']) and r['base_label'] in READ)}件)の判定変化: {len(u_changed)}")
show(u_changed, "K8")
# v3 vs v4 差分表(既存771+未知)
dv = [r for r in rows if (r["v3_state"], _rs(r["v3_reason"]), r["v3_warn"]) != (r["fix_state"], _rs(r["fix_reason"]), r["fix_warn"])]
print(f"[v3->v4 差分] {len(dv)}件")
for r in dv:
    print(f"   {r['src']} {r['id'][-60:]} | {r['canon'][:28]} | {r['asr'][:28]} | base {r['base_state']} v3 {r['v3_state']}/{r['v3_reason']} v4 {r['fix_state']}/{r['fix_reason']}")
# 基準9: F2発動全件
fired_rows = [r for r in rows if r["f2_fired"]]
print(f"[K9] F2発動(fired=True) {len(fired_rows)}件 (corpus {sum(1 for r in fired_rows if not r['src'].startswith('U:'))} / unknown {sum(1 for r in fired_rows if r['src'].startswith('U:'))}); うち正常143件中: {sum(1 for r in normal if r['f2_fired'])} / 正常attempt全体(P4+POS READING_MATCH PASS {len(normal)})")
fallbacks = [r for r in rows if r["f2_fallback"] == "monotonic_guard"]
print(f"[K9] monotonic guardによるF2前結果への巻戻し(fallback): {len(fallbacks)}件")
for r in fallbacks: print("    fallback:", r["src"], r["id"][-50:], r["canon"][:30], "|", r["asr"][:30])
chk_fail = []
for r in fired_rows:
    f = r["f2_fired"][0]
    c2, t2 = f["canon2"], f["text2"]
    gpost = vg.value_guard(c2, t2, "ja")
    for side, surf in f["replaced"]:
        orig_text, new_text = (r["canon"], c2) if side == "src" else (r["asr"], t2)
        import unicodedata
        o = unicodedata.normalize("NFKC", orig_text)
        # partner atom
        pa = [a for a in vg.extract_atoms_ja(unicodedata.normalize("NFKC", r["asr"] if side == "src" else r["canon"])) if a.surface == surf]
        sm = difflib.SequenceMatcher(None, o, new_text, autojunk=False)
        read = None
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op == "replace" and new_text[j1:j2] == surf:
                read = o[i1:i2]
        okb = bool(pa) and read is not None and F4._rev(pa[0].unit).get(read) == {int(pa[0].value)}
        okc = all(p.verdict == vg.EQUAL for p in gpost.pairs if surf in (p.src, p.hyp))
        okc2 = bool(pa) and any(a.surface == surf for a in vg.extract_atoms_ja(new_text))
        r.setdefault("f2_checks", []).append({"side": side, "partner": surf, "read": read, "b_unique_read_maps_to_value": okb, "c_pair_equal_after": okc, "a_partner_surface_present": okc2})
        if not (okb and okc and okc2): chk_fail.append(r)
    print(f"   F2 {r['src']} {r['id'][-50:]} | {r['canon'][:34]} | {r['asr'][:34]} | replaced {[(c['side'], c['partner'], c['read']) for c in r['f2_checks']]} | {r['base_state']}->{r['fix_state']}")
print("[K9] 機械確認(a表層一致・b読みが当該値にのみ対応・cF2後pair EQUAL)の失敗:", len(chk_fail))
remain = [r for r in base_read_pass if passing(r["fix_state"])]
print(f"[K6] 是正後もPASSのREADING_MATCH PASS: {len(remain)}")
summary = {"items": len(rows), "corpus": len(known_rows), "unknown": len(unk_rows), "base_read_pass": len(base_read_pass), "normal_ng": len(ng_normal), "known_neg_ok": k2_ok,
           "changed": len(changed), "f1": len(f1_chg), "warn_add": len(warn_add), "other_changed": len(other), "nonread_pass_changed": len(nonread_pass_changed), "ng_to_pass": len(ng_to_pass),
           "lost_warnings": len(lost_warn), "unknown_changed": len(u_changed), "f2_fired": len(fired_rows), "f2_fallback": len(fallbacks), "f2_checks_failed": len(chk_fail), "v3_v4_diff": len(dv), "remain_pass": len(remain)}
print("summary:", json.dumps(summary, ensure_ascii=False))
json.dump({"rows": rows, "summary": summary}, open(D + "open517_api0_eval_04.out.json", "w", encoding="utf8"), ensure_ascii=False, indent=1, default=str)
print("out sha256:", hashlib.sha256(open(D + "open517_api0_eval_04.out.json", "rb").read()).hexdigest())
