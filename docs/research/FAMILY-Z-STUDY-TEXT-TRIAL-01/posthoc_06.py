# Trial-06 事後分析(API 0。合否に使わない。事前登録外の反事実集計。4回目の設計ではない)
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_trial_06 as t6, analyze_06 as an
def sel_variant(F, excl):
    out = []; uc = set(); up = set()
    for f in sorted([f for f in F if t6.eligible_main(f) and t6._cls(f) not in excl], key=t6._order_key):
        if t6._cls(f) in uc or f["para"] in up: continue
        out.append(f); uc.add(t6._cls(f)); up.add(f["para"])
        if len(out) >= 2: break
    return out
res = {}
for name, excl in {"main(事前登録)": set(), "FRONT除外": {"FRONT"}, "FRONT+ELL除外": {"FRONT", "ELL"}, "強クラスのみ": set(t6.MID)}.items():
    r = {}
    for w in t6.WORKS6:
        S = an.load(w); has_core = bool(an.CORE[w]); ok = True; zero = 0; outside = 0
        for j in S:
            sel = [t6.sel_record(f) for f in sel_variant(j["features"], excl)]
            ks = [an.kind_of(w, m) for m in sel]
            if "outside" in ks: ok = False; outside += 1
            if has_core and not sel: ok = False; zero += 1
        r[w] = dict(pass_=ok, samples_with_outside=outside, zero_samples=zero)
    res[name] = r
json.dump(res, open(os.path.join(an.BASE, "posthoc_06.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in res.items(): print(k, {w: ("PASS" if x["pass_"] else f"FAIL(out={x['samples_with_outside']},zero={x['zero_samples']})") for w, x in v.items()})
