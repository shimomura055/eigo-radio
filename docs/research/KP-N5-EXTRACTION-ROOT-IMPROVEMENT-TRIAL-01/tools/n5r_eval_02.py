"""Trial専用(API 0)。TRIAL_PLAN_02 §4の基準をrep file/gen cacheから集計する。usage: python n5r_eval_02.py <out_prefix> <case[,case...]> """
import sys, os, json, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import n5r_lib_02 as L
n5 = L.n5
PREFIX, CASES = sys.argv[1], sys.argv[2].split(",")
MAIN = {"untidi_b1b", "untidi_a2"}
HR = ["turn into an interrogation", "hear it out"]
POOL_OF = {"A0": "A0", "A1": "E1", "A2": "E2", "A2d": "E2", "A4": "E2", "A4d": "E2", "A8": "E2", "A5": "E5", "A6p": "E6", "A7p": "E2", "A3ref": "E2"}
ARMS = list(POOL_OF)
SAME = ("SAME", "MODIFIER_DROPPED_OK")
fx = L.fixture()


def load(case):
    reps = sorted(int(f.split("_")[-1].split(".")[0]) for f in os.listdir(L.EV) if f.startswith(f"rep_{case}_") and f.endswith(".json"))
    R = {r: json.load(open(f"{L.EV}/rep_{case}_{r}.json", encoding="utf-8")) for r in reps}
    cf = f"{L.EV}/gen_cache_{case}.json"
    cache = json.load(open(cf, encoding="utf-8")) if os.path.exists(cf) else {}
    return R, cache


def pick_items(rep, arm):
    return rep["picks"][arm]


def final_items(rep, arm, cache, text):
    """CHK5通過後・API 0 QA(CMU/5語)通過後の最終。cache未実行のitemがあればNone。pick順を保つ。"""
    out = []
    for c in pick_items(rep, arm):
        g = cache.get(L.norm_key(c["span"]))
        if g is None:
            return None
        if g["outcome"] != "kept" or g.get("cmu") or not g.get("words_ok", True):
            continue
        out.append(dict(c, g=g))
    return out


def has(items, rx, use_g):
    for c in items:
        s = c["span"] + (" | " + c["g"]["display_form"] if (use_g and c.get("g")) else "")
        if rx.search(s):
            return True
    return False


def overlap(a, b):
    return L.norm_key(a) == L.norm_key(b) or n5._contains(a, b)


def in_list(span, lst):
    return any(overlap(span, x["span"]) for x in lst)


res = {"cases": CASES, "arms": {}, "per_rep": {}}
ctlsel = json.load(open(f"{L.EV}/ctl_sel_untidi_b1b.json", encoding="utf-8")) if os.path.exists(f"{L.EV}/ctl_sel_untidi_b1b.json") else None
base_agree = None
if ctlsel:
    vs = [v["agreement"]["clskeep"]["mean"] for v in ctlsel["pools"].values()]
    base_agree = {"clskeep_mean_of_pools": round(sum(vs) / len(vs), 4), "detail": {pn: v["agreement"] for pn, v in ctlsel["pools"].items()}}
res["n4_baseline"] = base_agree

rows = []   # (case, rep, arm) records
for case in CASES:
    R, cache = load(case)
    text = fx["cases"][case]["text"]
    for r, rep in R.items():
        a0f = final_items(rep, "A0", cache, text)
        for arm in ARMS:
            pk = pick_items(rep, arm)
            pool = rep["pools"][POOL_OF[arm]]["judged"]
            fin = final_items(rep, arm, cache, text)
            hp = L.hits([c["span"] for c in pk])
            hpool = L.hits([c["span"] for c in pool])
            rec = {"case": case, "rep": r, "arm": arm, "pool_hits": hpool, "pick_hits": hp, "pick_both": hp["put_away"] and hp["in_the_way"],
                   "pool_both": hpool["put_away"] and hpool["in_the_way"], "n_pick": len(pk), "pick": [c["span"] for c in pk],
                   "ext_fallback": (rep["ext"].get({"A0": "A0", "E1": "E1", "E2": "E2", "E5": "E5", "E6": "E2"}[POOL_OF[arm]], {}) or {}).get("fallback")}
            if fin is not None:
                hf = {k: False for k in ("put_away", "in_the_way", "leave_out", "in_sight")}
                s = L.hits([c["span"] + " | " + c["g"]["display_form"] for c in fin]); hf.update(s)
                rec.update(final=[{"span": c["span"], "form": c["g"]["display_form"], "gloss": c["g"]["gloss_ja"], "rel": c["g"]["relation"], "diff": c["difficulty"], "type": c["chunk_type"], "origin": c["n5_origin"], "reverted": c["g"]["reverted"]} for c in fin],
                           final_hits=hf, final_both=hf["put_away"] and hf["in_the_way"], n_final=len(fin))
                if arm != "A0" and a0f is not None:
                    ent = [c for c in fin if not in_list(c["span"], a0f)]
                    rec["entrants"] = [c["span"] for c in ent]
                    rec["n5_bad"] = [c["span"] for c in ent if c["g"]["relation"] not in SAME]
                    rec["displaced"] = [c["span"] for c in a0f if not in_list(c["span"], fin)]
                    rec["hr_survive"] = {h: in_list(h, fin) for h in HR if in_list(h, a0f)}
                if a0f is not None and arm == "A0":
                    rec["hr_survive"] = {h: in_list(h, fin) for h in HR if any(L.norm_key(h) == L.norm_key(c["span"]) for c in fin)}
                tl = text.lower()
                n2 = 0
                for c in fin:
                    br = L.body_recur_trial(c["span"], text)
                    if c["difficulty"] == "easy" and br < 3 and c["chunk_type"] in ("fixed_phrase", "collocation"):
                        n2 += 1
                rec["n2"] = n2
                rec["title_mix"] = sum(1 for c in fin if L.TITLE_PHRASES.search(c["span"]))
                rec["diff_dist"] = {d: sum(1 for c in fin if c["difficulty"] == d) for d in ("advanced", "upper_intermediate", "easy")}
                rec["n1_bad"] = [c["span"] for c in fin if not n5.span_in_text(c["span"], text)]
            # N4: A0プールとの共通候補のcls/keep一致率
            if arm not in ("A0",):
                a0p = {L.norm_key(c["span"]): c for c in rep["pools"]["A0"]["judged"]}
                ap = {L.norm_key(c["span"]): c for c in pool}
                com = [k for k in ap if k in a0p]
                if com:
                    rec["n4_common"] = len(com)
                    rec["n4_clskeep"] = sum(1 for k in com if ap[k]["cls"] == a0p[k]["cls"] and bool(ap[k]["keep"]) == bool(a0p[k]["keep"])) / len(com)
                    rec["n4_diff"] = sum(1 for k in com if ap[k]["difficulty"] == a0p[k]["difficulty"]) / len(com)
            # N6 cost/time (抽出+SEL+rerank)
            def c_of(x): return (x or {}).get("cost_jpy") or 0
            def s_of(x): return (x or {}).get("sec") or 0
            ex = {"A0": "A0", "A1": "E1", "A2": "E2", "A2d": "E2", "A4": "E2", "A4d": "E2", "A8": "E2", "A5": None, "A6p": "E2", "A7p": "E2", "A3ref": "E2"}[arm]
            cost = c_of(rep["ext"].get(ex)) + c_of(rep["pools"][POOL_OF[arm]]["info"]); sec = s_of(rep["ext"].get(ex)) + s_of(rep["pools"][POOL_OF[arm]]["info"])
            if arm in ("A7p", "A6p"):
                rr = rep["rr"]["E2" if arm == "A7p" else "E6"]; cost += c_of(rr); sec += s_of(rr)
            rec["cost"] = round(cost, 4); rec["sec"] = round(sec, 1)
            rows.append(rec)
    # N7
    metas = [m for rep in R.values() for m in rep["all_metas"]]
    gb = [json.load(open(f, encoding="utf-8")) for f in glob.glob(f"{L.EV}/gen_batches_{case}_*.json")]
    res.setdefault("n7", {})[case] = {"calls": len(metas), "truncated_or_retry": sum(1 for m in metas if m.get("json_ok") is False or (m.get("attempt") or 1) > 1),
                                       "truncated_stages": [m["label"] for m in metas if m.get("json_ok") is False]}


def agg_arm(arm, cases):
    rr = [r for r in rows if r["arm"] == arm and r["case"] in cases]
    if not rr: return None
    def cnt(f): return sum(1 for r in rr if f(r))
    a = {"n_reps": len(rr),
         "S1_put_away_pool": cnt(lambda r: r["pool_hits"]["put_away"]), "S1_in_the_way_pool": cnt(lambda r: r["pool_hits"]["in_the_way"]), "S1_both_pool": cnt(lambda r: r["pool_both"]),
         "pick_put_away": cnt(lambda r: r["pick_hits"]["put_away"]), "pick_in_the_way": cnt(lambda r: r["pick_hits"]["in_the_way"]), "S3pick_both": cnt(lambda r: r["pick_both"]),
         "fallback_reps": cnt(lambda r: r["ext_fallback"]),
         "mean_cost": round(sum(r["cost"] for r in rr) / len(rr), 3), "mean_sec": round(sum(r["sec"] for r in rr) / len(rr), 1)}
    fr = [r for r in rr if "final" in r]
    if fr:
        a.update(n_final_reps=len(fr), S3final_both=cnt(lambda r: r.get("final_both")), final_put_away=cnt(lambda r: r.get("final_hits", {}).get("put_away")),
                 final_in_the_way=cnt(lambda r: r.get("final_hits", {}).get("in_the_way")), final_leave_out=cnt(lambda r: r.get("final_hits", {}).get("leave_out")),
                 final_in_sight=cnt(lambda r: r.get("final_hits", {}).get("in_sight")),
                 mean_n2=round(sum(r["n2"] for r in fr) / len(fr), 2), mean_title_mix=round(sum(r["title_mix"] for r in fr) / len(fr), 2),
                 mean_displaced=round(sum(len(r.get("displaced", [])) for r in fr) / len(fr), 2) if arm != "A0" else None,
                 n5_bad=[x for r in fr for x in r.get("n5_bad", [])], n1_bad=[x for r in fr for x in r["n1_bad"]],
                 mean_diff_dist={d: round(sum(r["diff_dist"][d] for r in fr) / len(fr), 2) for d in ("advanced", "upper_intermediate", "easy")})
        hs = [(h, v) for r in fr for h, v in (r.get("hr_survive") or {}).items()]
        a["hr_survive"] = f"{sum(1 for _, v in hs if v)}/{len(hs)}" if hs else None
    n4 = [r["n4_clskeep"] for r in rr if "n4_clskeep" in r]
    if n4: a["n4_clskeep_mean"] = round(sum(n4) / len(n4), 4); a["n4_diff_mean"] = round(sum(r["n4_diff"] for r in rr if "n4_diff" in r) / len(n4), 4)
    return a


for grp, cs in (("main", [c for c in CASES if c in MAIN]), ("heldout", [c for c in CASES if c not in MAIN])):
    if not cs: continue
    res["arms"][grp] = {arm: agg_arm(arm, cs) for arm in ARMS}
res["rows"] = rows
json.dump(res, open(f"{L.EV}/{PREFIX}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({g: {a: {k: v for k, v in d.items() if not isinstance(v, list)} for a, d in arms.items() if d} for g, arms in res["arms"].items()}, ensure_ascii=False, indent=1))
print("n4_baseline", base_agree and base_agree["clskeep_mean_of_pools"], "n7", res.get("n7"))
