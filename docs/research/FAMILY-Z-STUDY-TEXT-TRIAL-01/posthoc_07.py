# Trial-07 事後分析(API 0。合否に使わない。事前登録外の反事実集計。追加Trialの設計ではない)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_07 as t7, analyze_07 as an
def sel_variant(F, classes):
    el = sorted([f for f in F if t7.eligible7(f) and t7._cls(f) in classes], key=t7._order_key)
    return el[:1]
res = {}
for name, cls in {"main(事前登録)": set(t7.PRIORITY), "強クラスのみ(INV/CLEFT/CMP)": set(t7.STRONG)}.items():
    r = {}
    for w in t7.WORKS7:
        S = an.load(w); has_core = bool(an.CORE[w]); ok = True; zero = 0; outside = 0
        for j in S:
            sel = [t7.sel_record(f) for f in sel_variant(j["features"], cls)]
            ks = [an.kind_of(w, m) for m in sel]
            if "outside" in ks: ok = False; outside += 1
            if has_core and not sel: ok = False; zero += 1
            if w == "melos" and sel: ok = False
        r[w] = dict(pass_=ok, samples_with_outside=outside, zero_samples=zero)
    res[name] = r
json.dump(res, open(os.path.join(an.BASE, "posthoc_07.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items(): print(k, {w: ("PASS" if x["pass_"] else f"FAIL(out={x['samples_with_outside']},zero={x['zero_samples']})") for w, x in v.items()})
