"""Trial専用(API 0)。委任_05 Phase1: 全cell(case)のE2プール・A10 cap10選定・既存GEN5/VER5/CHK5 cache・現行N5(fixture trial_items)の棚卸し。
usage: python n5r_inv_05.py -> stdout JSON(ev05/inventory_05.json)"""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
fx = L.fixture()
OUT = os.path.join(L.TD, "ev05"); os.makedirs(OUT, exist_ok=True)
reps = {}
for f in sorted(glob.glob(f"{L.EV}/rep_*.json")):
    d = json.load(open(f, encoding="utf-8")); reps.setdefault(d["case"], []).append(d)
caches = {}
for c in reps:
    fn = f"{L.EV}/gen_cache_{c}.json"
    caches[c] = json.load(open(fn, encoding="utf-8")) if os.path.exists(fn) else {}
inv = {}
for case, rl in reps.items():
    text = fx["cases"][case]["text"]
    cur = fx["cases"][case]["trial_items"]
    row = {"n_reps": len(rl), "cache_n": len(caches[case]), "reps": [], "current_n5_trial_items": [(x["source_span"], x["display_form"]) for x in cur]}
    union = {}
    for rep in rl:
        pk = L.pick_A10(rep["pools"]["E2"]["judged"], text, 10)
        spans = [c["span"] for c in pk]
        unc = [s for s in spans if L.norm_key(s) not in caches[case]]
        for s in spans: union[L.norm_key(s)] = s
        row["reps"].append({"rep": rep["rep"], "spans": spans, "uncached": unc, "n_keep": sum(1 for c in rep["pools"]["E2"]["judged"] if c["keep"])})
    row["union"] = len(union); row["union_uncached"] = [s for k, s in union.items() if k not in caches[case]]
    inv[case] = row
json.dump(inv, open(f"{OUT}/inventory_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for case, r in inv.items():
    print(case, "reps", r["n_reps"], "cache", r["cache_n"], "union_cap10", r["union"], "union_uncached", len(r["union_uncached"]))
    for x in r["reps"]: print("   rep", x["rep"], "keep", x["n_keep"], "n", len(x["spans"]), "uncached", len(x["uncached"]))

# ---- 追加: 既知(GEN5済)集合 = gen_cache + fixture trial_items、A0 cap7(現行B1方式の各rep)も対象に含めた場合の未処理数 ----
def known_keys(case):
    k = set(caches[case].keys())
    for x in fx["cases"][case]["trial_items"]:
        k.add(L.norm_key(x["source_span"]))
    return k
print("---- 未処理(GEN5新規)見積")
est = {}
for case, rl in reps.items():
    text = fx["cases"][case]["text"]; kn = known_keys(case)
    A = {}; B = {}
    for rep in rl:
        for c in L.pick_A10(rep["pools"]["E2"]["judged"], text, 10): A.setdefault(L.norm_key(c["span"]), c["span"])
        for c in rep["picks"]["A0"]: B.setdefault(L.norm_key(c["span"]), c["span"])
    a_new = [s for k, s in A.items() if k not in kn]
    b_new = [s for k, s in B.items() if k not in kn and k not in A]
    est[case] = {"A_union": len(A), "A_new": a_new, "A0_union": len(B), "A0_new": b_new, "n_text": len(text)}
    print(case, "A10cap10 union", len(A), "new", len(a_new), "| A0cap7 union", len(B), "new(not in A)", len(b_new), "| known", len(kn))
json.dump(est, open(f"{OUT}/gen_estimate_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
