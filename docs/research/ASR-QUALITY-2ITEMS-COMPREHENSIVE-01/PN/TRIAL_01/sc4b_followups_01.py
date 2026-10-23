# -*- coding: utf-8 -*-
"""SC-4 追補: (1)既受理45(A類)の維持=退行0 (2)Ledger leave-one-out (3)ユニーク(text,名前)単位 (4)D1新規受理の全件adjudication表(OF-PN2-07)。API 0(保存表・保存結果の再評価)。"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_01 import *
tabs = {k: ret.EntityTable.from_dict(v) for k, v in json.load(open(os.path.join(HERE, "entity_tables_hr_01.json"), encoding="utf-8")).items()}
rows = [(i, r) for i, r, c in load_hr_rows() if not c]
grp = {}
for i, r in rows:
    k, segs, how = group_key_and_segments(r)
    grp[i] = k
full = ledger_tokens(False)
none = ledger_tokens(True)
L = json.load(open(LEDGER_JSON, encoding="utf-8"))
res = {}
# (1) 退行: 現行Ledgerで原本accept -> RET accept
reg = []
new_acc = []
data = {}
for i, r in rows:
    kw = inputs_for(r)
    if kw is None:
        continue
    tb = tabs[grp[i]]
    for lm, led in (("cur", full), ("excl", none)):
        o = run_orig(kw, led); t = run_trial(kw, led, tb)
        data[(i, lm)] = (kw, o, t)
        if o.accept and not t.accept:
            reg.append({"i": i, "lm": lm, "reason": t.reason, "detail": t.detail})
        if (not o.accept) and t.accept and lm == "excl":
            ents = t.detail.get("entity_table", {})
            new_acc.append({"i": i, "canon": kw["canonical_text"][:150], "primary": kw["primary_text"][:150], "secondary": (kw["secondary_text"] or "")[:150],
                            "diffs": [(x.canonical, x.asr_primary, x.asr_secondary, x.evidence, x.similarity_primary) for x in t.diffs],
                            "orig_reason": o.reason, "ret3": bool(ents.get("ret3")), "entries": [(e["surface"], e["category"], e["grade"]) for e in ents.get("entries_used", [])],
                            "labels": t.detail.get("alarm_labels")})
res["regressions"] = reg
res["n_new_accept_excl"] = len(new_acc)
# (2) LOO: Ledger各entry(surface token)を外して原本が reject に変わる行 = その語に依存する受理
by_entry = {}
for key, e in L.items():
    if e.get("ledger_disabled") or e.get("entity_type") == "ja_reading_katakana":
        continue
    toks = {t.strip("'") for t in pol._fold(e["surface"]).split()}
    by_entry[key] = toks
dep_total = dep_kept = 0
loo_rows = []
for key, toks in by_entry.items():
    led = frozenset(full - toks)
    for i, r in rows:
        kw, o_full, _ = data.get((i, "cur"), (None, None, None))
        if kw is None or not o_full.accept:
            continue
        o_loo = run_orig(kw, led)
        if o_loo.accept:
            continue
        dep_total += 1
        t_loo = run_trial(kw, led, tabs[grp[i]])
        dep_kept += t_loo.accept
        loo_rows.append({"entry": key, "i": i, "kept": t_loo.accept, "reason": t_loo.reason})
res["loo"] = {"ledger_entries": len(by_entry), "dependent_acceptances": dep_total, "kept_by_table": dep_kept, "rate": (dep_kept / dep_total if dep_total else None)}
res["loo_not_kept"] = [x for x in loo_rows if not x["kept"]]
# (3) ユニーク(text,名前)
def unit(i, d):
    kw = data[(i, "excl")][0]
    return (kw["canonical_text"], tuple(sorted(x.canonical for x in d.diffs)) if d.diffs else ("-",))
u_orig = {unit(i, data[(i, "excl")][1]) for i, r in rows if (i, "excl") in data and data[(i, "excl")][1].accept}
u_new = {unit(i, data[(i, "excl")][2]) for i, r in rows if (i, "excl") in data and data[(i, "excl")][2].accept}
res["unique_units"] = {"orig_accept_units": len(u_orig), "ret_accept_units": len(u_new)}
# 事象数（rowごと）
c = collections.Counter()
for lm in ("cur", "excl"):
    for variant, idx in (("orig", 1), ("ret", 2)):
        c[(lm, variant)] = sum(1 for (i, l), v in data.items() if l == lm and v[idx].accept)
res["accept_counts"] = {"%s/%s" % k: v for k, v in c.items()}
json.dump(res, open(os.path.join(HERE, "sc4b_followups_01_result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
json.dump(new_acc, open(os.path.join(HERE, "sc4_new_accepts_adjudication_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in res.items() if k != "loo_not_kept"}, ensure_ascii=False, indent=1))
print("LOO not kept:", res["loo_not_kept"])
print("new accepts (excl):", len(new_acc))
