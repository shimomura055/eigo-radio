"""Trial専用(API 0)。委任_05: 比較の定量補助集計(難易度構成・同一rep内A0(cap7)/A10(cap10)の入替・GEN5以降の脱落・重複・relation分布)。usage: python n5r_stats_05.py -> ev05/stats_05.json"""
import sys, os, json, glob, itertools, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
import n5r_cmp_05 as C
n5 = L.n5
EV2 = os.path.join(L.TD, "ev02"); EV5 = os.path.join(L.TD, "ev05")
fx = L.fixture()
st = {}
for case, _ in C.CASES:
    text = fx["cases"][case]["text"]
    reps = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(f"{EV2}/rep_{case}_*.json"))]
    row = collections.OrderedDict()
    easy10 = []; easy0 = []; n10 = []; n0 = []; only_a = []; only_0 = []; both = []; dup_reps = 0; usable_n = []; dropped_n = []
    rel = collections.Counter(); drops = collections.Counter(); union_a = {}
    for r in reps:
        a10 = L.pick_A10(r["pools"]["E2"]["judged"], text, 10)
        a0 = r["picks"]["A0"]
        easy10.append(sum(1 for c in a10 if c["difficulty"] == "easy")); easy0.append(sum(1 for c in a0 if c["difficulty"] == "easy"))
        n10.append(len(a10)); n0.append(len(a0))
        i10 = [C.ident(case, c["span"]) for c in a10]; i0 = [C.ident(case, c["span"]) for c in a0]
        both.append(len(set(i10) & set(i0))); only_a.append(len(set(i10) - set(i0))); only_0.append(len(set(i0) - set(i10)))
        gs = [C.gen_of(case, c["span"]) for c in a10]
        usable_n.append(sum(1 for g in gs if C.usable(g))); dropped_n.append(sum(1 for g in gs if not C.usable(g)))
        dfs = [g["display_form"].lower() for g in gs if C.usable(g)]
        if len(dfs) != len(set(dfs)):
            dup_reps += 1
        for c in a10:
            union_a.setdefault(L.norm_key(c["span"]), c)
    for k, c in union_a.items():
        g = C.gen_of(case, c["span"])
        if g is None:
            drops["GEN未処理"] += 1
        elif g["outcome"] == "dropped":
            drops[f"{g.get('drop_stage')}"] += 1
        else:
            rel[str(g.get("relation"))] += 1
            if not C.usable(g):
                drops["CMU/5語"] += 1
    m = lambda x: round(sum(x) / len(x), 2)
    cur = fx["cases"][case]["trial_items"]
    rt10 = collections.Counter(); rt0 = collections.Counter()
    for r in reps:
        for c in L.pick_A10(r["pools"]["E2"]["judged"], text, 10):
            g = C.gen_of(case, c["span"]); rt10[C.rate(g["display_form"]) if C.usable(g) else "脱落"] += 1
        for c in r["picks"]["A0"]:
            g = C.gen_of(case, c["span"]); rt0[C.rate(g["display_form"]) if g and g["outcome"] == "kept" else "脱落"] += 1
    row["rating_mean_per_rep_A10"] = {k: round(v / len(reps), 2) for k, v in rt10.items()}
    row["rating_mean_per_rep_A0"] = {k: round(v / len(reps), 2) for k, v in rt0.items()}
    row.update(n_reps=len(reps), cur_n=len(cur), cur_easy=sum(1 for x in cur if x.get("difficulty") == "easy"),
               A10_n_mean=m(n10), A10_easy_mean=m(easy10), A0_n_mean=m(n0), A0_easy_mean=m(easy0),
               A10_usable_mean=m(usable_n), A10_gen_dropped_mean=m(dropped_n), same_rep_shared_mean=m(both), same_rep_A10only_mean=m(only_a), same_rep_A0only_mean=m(only_0),
               reps_with_duplicate_display_form=dup_reps, union_A10_n=len(union_a), union_relation=dict(rel), union_drops=dict(drops))
    st[case] = row
json.dump(st, open(f"{EV5}/stats_05.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c, r in st.items():
    print(c, json.dumps(r, ensure_ascii=False))
