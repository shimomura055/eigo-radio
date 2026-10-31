import json, sys, collections
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
tab = collections.defaultdict(lambda: collections.Counter()); fr = collections.Counter(); n_pairs = collections.Counter(); cost = 0; perr = collections.Counter()
for r in rows:
    cost += r["cost_jpy"] or 0
    if r["parse_error"]:
        perr[r["cond"]] += 1; continue
    tab[(r["cond"], r["type"])]["n"] += 1; tab[(r["cond"], r["type"])]["caught"] += int(r["caught"])
    fr[r["cond"]] += len(r["false_rejects"]); n_pairs[r["cond"]] += r["n_pairs"] - 1
conds = ["noV", "CV", "DV", "EV"]; types = ["mixin", "inversion", "omission", "number"]
out = {"cost_jpy": round(cost, 4), "parse_errors": dict(perr), "false_rejects_of_clean_pairs": {c: f"{fr[c]}/{n_pairs[c]}" for c in conds}, "capture": {}}
for c in conds:
    tot = sum(tab[(c, t)]["caught"] for t in types); nn = sum(tab[(c, t)]["n"] for t in types)
    out["capture"][c] = {"total": f"{tot}/{nn}", **{t: f"{tab[(c, t)]['caught']}/{tab[(c, t)]['n']}" for t in types}}
print(json.dumps(out, ensure_ascii=False, indent=1))
elig = {}
for c in ("CV", "DV", "EV"):
    tv = sum(tab[(c, t)]["caught"] for t in types); tn = sum(tab[("noV", t)]["caught"] for t in types)
    mv = tab[(c, "mixin")]["caught"]; mn = tab[("noV", "mixin")]["caught"]
    elig[c] = {"overall_ok(V>=noV-2)": tv >= tn - 2, "mixin_ok(V>=noV-1)": mv >= mn - 1, "eligible": (tv >= tn - 2) and (mv >= mn - 1)}
print(json.dumps(elig, ensure_ascii=False))
