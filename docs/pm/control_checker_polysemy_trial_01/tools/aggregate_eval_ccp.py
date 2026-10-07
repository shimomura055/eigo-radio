# -*- coding: utf-8 -*-
"""OPEN-233-CONTROL-CHECKER-POLYSEMY-PRODUCTION-PATH-TRIAL-01 委任_03: 盲検評価の集計(決定論・API無し・評価JSON読取専用)。
出力: eval/aggregate_ccp.json (SUMMARY_CCP.md は build_summary_ccp.py が生成)。MAP(eval/_private/MAP_ccp.json)を読む(全員分出揃い後)。"""
import glob, json, math, os, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
os.chdir(ROOT)
B = "er052_output/open233_control_checker_polysemy_trial_01"
EV = B + "/eval"


def jl(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def cp_upper(k, n, alpha=0.05):
    """Clopper-Pearson 片側上限(1-alpha)。"""
    if k >= n:
        return 1.0

    def cdf(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if cdf(mid) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


ORDER = {"correct": 0, "ambiguous": 1, "misread": 2}


def worse(labels):
    ls = [l for l in labels if l in ORDER]
    return max(ls, key=lambda x: ORDER[x]) if ls else "not_selected"


def main():
    opened = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mp = jl(EV + "/_private/MAP_ccp.json")["articles"]
    bal = jl(EV + "/_private/assignment_balance_ccp.json")
    rf = jl(EV + "/_private/run_facts.json")["run_facts"]
    cost = jl(B + "/runs/cost_summary.json")
    ev_of = {}
    for ev, lst in bal["assign"].items():
        for k in lst:
            ev_of[k] = ev
    arts, errs = [], []
    for p in sorted(glob.glob(EV + "/articles/*.json")):
        a = jl(p)
        key = "%s/%s" % (a["slug"], a["code"])
        if key not in mp:
            errs.append("MAP解決不能 " + key)
            continue
        a["_key"] = key
        a["_map"] = mp[key]
        a["_eval"] = ev_of.get(key)
        arts.append(a)
    chk = {"articles": len(arts), "map_missing": errs}
    bad = []
    for a in arts:
        for sk, st in (("s0", "s0_r0"), ("s1", "s1_ja"), ("s2", "s2_en")):
            c_min = sum(1 for x in a["ng_items"] if x["severity"] == "minor" and x["stage"].get(sk))
            c_maj = sum(1 for x in a["ng_items"] if x["severity"] == "major" and x["stage"].get(sk))
            if c_min != a["stages"][st]["minor"] or c_maj != a["stages"][st]["major"]:
                bad.append("%s %s ng_items=%d/%d stages=%d/%d" % (a["_key"], st, c_maj, c_min, a["stages"][st]["major"], a["stages"][st]["minor"]))
    chk["ng_items_vs_stages_mismatch"] = bad
    meta = [a for a in arts if a["slug"] == "meta"]
    xs = {os.path.basename(p)[:-5]: jl(p) for p in glob.glob(EV + "/rollback_x/*.json")}
    chk["rollback_x_n"] = len(xs)
    rb = []
    for a in meta:
        x = xs["meta_" + a["code"]]
        row = {"code": a["code"], "rep": a["_map"]["rep"], "eval": a["_eval"]}
        for st in ("ja_r2", "en_pre_checker", "en_final"):
            row[st] = a["rollback_labels"][st]["label"]
            row[st + "_X"] = x["rollback_labels"][st]["label"]
        row["worse_eval"] = worse([row[s] for s in ("ja_r2", "en_pre_checker", "en_final")])
        row["worse_X"] = worse([row[s + "_X"] for s in ("ja_r2", "en_pre_checker", "en_final")])
        rb.append(row)

    def cnt(st, who=""):
        c = {"correct": 0, "ambiguous": 0, "misread": 0, "not_selected": 0}
        for r in rb:
            c[r[st + who]] += 1
        return c
    rbk = {st: {"eval": cnt(st), "X": cnt(st, "_X")} for st in ("ja_r2", "en_pre_checker", "en_final")}
    rbk["worse_of_3"] = {"eval": {k: sum(1 for r in rb if r["worse_eval"] == k) for k in ORDER},
                         "X": {k: sum(1 for r in rb if r["worse_X"] == k) for k in ORDER}}
    disagree = [{"code": r["code"], "stage": st, "eval": r[st], "X": r[st + "_X"]} for r in rb
                for st in ("ja_r2", "en_pre_checker", "en_final") if r[st] != r[st + "_X"]]
    past = {"correct": 3, "ambiguous": 9, "misread": 0, "n": 12, "src": "REPORT §91(N=5: 正1/曖4/誤0)+§92(N=7: 正2/曖5/誤0)"}
    new_ja = rbk["ja_r2"]["eval"]
    n_sel = sum(new_ja.values()) - new_ja["not_selected"]
    cum = {k: past[k] + new_ja[k] for k in ("correct", "ambiguous", "misread")}
    cum_n = past["n"] + n_sel
    rbk["ja_r2_new_n"] = n_sel
    rbk["cumulative"] = dict(n=cum_n, misread_upper95=cp_upper(cum["misread"], cum_n), **cum)
    rbk["new_misread_upper95"] = cp_upper(new_ja["misread"], n_sel)
    maj_arts = [a["_key"] for a in arts if any(x["severity"] == "major" for x in a["ng_items"])
                or a["stages"]["s1_ja"]["major"] or a["stages"]["s2_en"]["major"]]
    pend_major = [(a["_key"], p["id"]) for a in arts for p in a["pending"]
                  if "major" in str(p.get("leaning", "")).lower() or "重大寄り" in str(p.get("leaning", ""))]
    drv = jl(B + "/runs/driver_result.json")
    gate_first = drv["state"].get("gate_stops_first")
    rws = [(a["_key"], r) for a in arts for r in a["checker_rewrites"]]
    n_rec = sum(v["n_rewrite_records"] for v in rf.values())
    bw = {"true": 0, "false": 0, "unclear": 0}
    for _, r in rws:
        bw[str(r["before_was_ng"]).lower()] += 1
    arts_rw = {}
    for k, r in rws:
        arts_rw.setdefault(k, []).append(str(r["before_was_ng"]).lower())
    art_all_unneeded = [k for k, v in arts_rw.items() if all(x != "true" for x in v)]
    art_all_false = [k for k, v in arts_rw.items() if all(x == "false" for x in v)]
    new_ng = {"major": 0, "minor": 0, "items": []}
    for k, r in rws:
        v = str(r["after_new_ng"]).lower()
        if v in ("major", "minor"):
            new_ng[v] += 1
            new_ng["items"].append((k, v, r["before"][:80], r["after"][:80]))
    s2_only = [(a["_key"], x["id"], x["severity"], x["kind"]) for a in arts for x in a["ng_items"]
               if x["stage"].get("s2") and not x["stage"].get("s1") and not x["stage"].get("s0")]
    ja_only = [(a["_key"], x["id"], x["severity"], x["kind"]) for a in arts for x in a["ng_items"]
               if x["stage"].get("s1") and not x["stage"].get("s2")]

    def is_rb(x):
        return x["fact_id"] == "MUSE-HC-012" and x["kind"] == "scope"

    def final_present(x):
        return bool(x["stage"].get("s1") or x["stage"].get("s2"))

    def stat(group):
        g = {"n": len(group), "major_all": 0, "minor_all": 0, "minor_rb": 0, "minor_final": 0, "minor_final_rb": 0,
             "pending": 0, "reg_minor": 0, "reg_major": 0}
        for a in group:
            g["pending"] += len(a["pending"])
            g["reg_minor"] += a["regressions"]["minor"]
            g["reg_major"] += a["regressions"]["major"]
            for x in a["ng_items"]:
                if x["severity"] == "major":
                    g["major_all"] += 1
                else:
                    g["minor_all"] += 1
                    g["minor_rb"] += is_rb(x)
                    if final_present(x):
                        g["minor_final"] += 1
                        g["minor_final_rb"] += is_rb(x)
        g["minor_excl"] = g["minor_all"] - g["minor_rb"]
        g["minor_final_excl"] = g["minor_final"] - g["minor_final_rb"]
        return g
    allg = stat(arts)
    themes = {t: stat([a for a in arts if a["slug"] == t]) for t in ("meta", "hormuz", "space_weapons", "sewer", "ai_control")}
    evals = {e: stat([a for a in arts if a["_eval"] == e]) for e in ("A", "B", "C")}
    nonmeta = stat([a for a in arts if a["slug"] != "meta"])
    excl_jb = stat([a for a in arts if a["_key"] != "ai_control/jb9k"])
    r1 = "PASS" if rbk["ja_r2"]["eval"]["misread"] == 0 and rbk["ja_r2"]["X"]["misread"] == 0 else "FAIL(要人間確認)"
    r2 = "PASS" if len(maj_arts) == 0 else ("CONDITIONAL" if len(maj_arts) == 1 else "FAIL")
    r3 = "懸念なし" if gate_first <= 2 else ("要注意" if gate_first <= 4 else "FAIL")
    strict = bw["false"] / max(1, len(rws))
    incl = (bw["false"] + bw["unclear"]) / max(1, len(rws))
    r5 = "PASS" if new_ng["major"] == 0 else "FAIL"
    avg, mx, tot_disk = cost["avg_jpy"], cost["max_jpy"], cost["disk_total_jpy_incl_failed"]
    r6 = "PASS" if (avg <= 13.0 and mx <= 25 and tot_disk <= 500) else "FAIL"
    if "FAIL" in r1 or r2 == "FAIL" or r3 == "FAIL" or r5 == "FAIL" or r6 == "FAIL":
        overall = "FAIL"
    elif r2 == "CONDITIONAL" or r3 == "要注意" or strict > 0.5:
        overall = "CONDITIONAL"
    else:
        overall = "PASS"
    overall_alt = "CONDITIONAL" if (overall == "PASS" and incl > 0.5) else overall
    out = {"opened_at": opened, "check": chk, "rollback_rows": rb, "rollback": rbk, "rollback_disagree": disagree, "past_rollback": past,
           "major_articles": maj_arts, "pending_leaning_major": pend_major, "gate_stop_first": gate_first,
           "rewrite_records_run_facts": n_rec, "rewrite_evaluated": len(rws), "before_was_ng": bw,
           "unneeded_rate_strict_false_only": strict, "unneeded_rate_false_or_unclear": incl, "rewrite_articles": arts_rw,
           "rewrite_articles_all_unneeded_incl_unclear": art_all_unneeded, "rewrite_articles_all_false": art_all_false,
           "new_ng_from_rewrite": new_ng, "s2_only_items": s2_only, "ja_only_items": ja_only, "overall_stats": allg, "themes": themes,
           "evaluators": evals, "nonmeta": nonmeta, "excl_jb9k": excl_jb,
           "cost": {"avg": avg, "max": mx, "completed_total": cost["total_jpy_completed"], "disk_total_incl_failed": tot_disk},
           "judgement": {"1_rollback": r1, "2_major": r2, "3_gate": r3, "5_new_major": r5, "6_cost": r6,
                         "overall_prereg_text": overall, "overall_if_unclear_counted": overall_alt}}
    json.dump(out, open(EV + "/aggregate_ccp.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return out


if __name__ == "__main__":
    o = main()
    print(json.dumps({k: o[k] for k in ("check", "rollback", "rollback_disagree", "major_articles", "gate_stop_first",
                                        "rewrite_records_run_facts", "rewrite_evaluated", "before_was_ng", "new_ng_from_rewrite",
                                        "s2_only_items", "ja_only_items", "overall_stats", "judgement")}, ensure_ascii=False, indent=1))
    for k in ("themes", "evaluators", "nonmeta", "excl_jb9k"):
        print(k, json.dumps(o[k], ensure_ascii=False))
