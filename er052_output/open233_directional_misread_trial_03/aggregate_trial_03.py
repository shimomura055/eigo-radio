"""TRIAL-03 集計(費用0円/LLM呼出なし)。基準充足の事実のみ出力、Status判定はFable。
usage: aggregate_trial_03.py --results-x X.jsonl --results-y Y.jsonl --ledger-cache L.json --truth T.json
  --testset S.json --population P.json --prev-summary trial_summary_02.json --prev-results R02.jsonl --out DIR
  [--summary-x/--summary-y summary.json] [--ledger-cache-y L2.json]"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regression_vs_trial02 as rg

GOLD = {"G-01": "HC-012", "G-02": "A5-0", "G-03": "D61"}
PREV_FALSE = ["F-09", "F-10", "F-19"]
LBL = {"真の反転": "gold", "人工反転": "synthetic", "曖昧": "ambiguous", "忠実": "normal"}


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def jd(p):
    return json.load(open(p, encoding="utf-8"))


def cmps(r):
    return [x.get("compare") for x in r.get("repeats", [])]


def rep0(r):
    return rg.rep0(r)


def rate(a, b):
    return round(a / b, 4) if b else None


def is_held(r):
    return bool(r.get("heldout")) or str(r.get("id", "")).startswith("H-")


def kind(r):
    c = LBL.get(r.get("label", ""), "other")
    if is_held(r):
        if c == "other" and not r.get("label"):  # held-outはlabel欄なし → expected_compareで判別
            return "held_gold" if r.get("expected_compare") == "REVERSED" else "held_normal"
        return "held_normal" if c == "normal" else ("held_gold" if c in ("gold", "synthetic") else "held_other")
    return c


def kn(r):
    c = cmps(r)
    return {"rep0": rep0(r), "compares": c, "k": sum(x == "REVERSED" for x in c), "n": len(c)}


def fb_part(rows):
    used = [r for r in rows if any(x.get("fallback_used") for x in r.get("repeats", []))]
    reps = [x for r in rows for x in r.get("repeats", [])]
    nu = sum(bool(x.get("fallback_used")) for x in reps)
    return {"items_with_fallback": len(used), "repeats_with_fallback": nu, "repeat_fallback_rate": rate(nu, len(reps)),
            "fallback_calls": sum(x.get("fallback_calls", 0) or 0 for x in reps),
            "fallback_ids": [{"id": r["id"], "compares": cmps(r), "details": [x.get("fallback_details") for x in r["repeats"] if x.get("fallback_used")]} for r in used]}


def phase_part(rows):
    reps = [(r, x) for r in rows for x in r.get("repeats", [])]
    dist = {}
    for _, x in reps:
        p = x.get("article_phase")
        dist[str(p)] = dist.get(str(p), 0) + 1
    ex = [(r, x) for r, x in reps if r.get("expected_phase")]
    ok = sum(x.get("article_phase") == r["expected_phase"] for r, x in ex)
    multi = [r for r in rows if len(r.get("repeats", [])) >= 3 and any(x.get("article_phase") for x in r["repeats"])]
    agree = sum(len({x.get("article_phase") for x in r["repeats"]}) == 1 for r in multi)
    return {"article_phase_distribution": dist, "expected_phase_n": len(ex), "expected_phase_match": rate(ok, len(ex)),
            "phase_repeat_items": len(multi), "phase_repeat_agree_rate": rate(agree, len(multi))}


def analyze(rows, prev_rows):
    by = {r["id"]: r for r in rows}
    nor = [r for r in rows if kind(r) in ("normal", "held_normal")]
    fr = [r["id"] for r in nor if rep0(r) == "REVERSED"]
    allc = [c for r in nor for c in cmps(r)]
    gold = {g: dict(name=n, **kn(by[g])) for g, n in GOLD.items() if g in by}
    hg = {r["id"]: kn(r) for r in rows if kind(r) == "held_gold"}
    hks = [v["k"] / v["n"] for v in hg.values() if v["n"]]
    pf = {i: ({**kn(by[i]), "recurred": "REVERSED" in cmps(by[i]) or rep0(by[i]) == "REVERSED"} if i in by else None) for i in PREV_FALSE}
    prev_det = [r["id"] for r in prev_rows if LBL.get(r.get("label", "")) in ("gold", "synthetic") and rep0(r) == "REVERSED"]
    miss = [i for i in prev_det if i in by and rep0(by[i]) != "REVERSED"]
    outs = [i for i in miss if by[i].get("outside_event_list")]
    multi = [r for r in rows if len(cmps(r)) >= 3]
    ag = [r["id"] for r in multi if len(set(cmps(r))) > 1]
    dist = {}
    for r in rows:
        dist[str(rep0(r))] = dist.get(str(rep0(r)), 0) + 1
    return {"n_items": len(rows), "rep0_distribution": dist, "gold": gold,
            "held_gold": {"items": hg, "mean_k_rate": round(sum(hks) / len(hks), 4) if hks else None,
                          "min_k_rate": round(min(hks), 4) if hks else None},
            "normal_pool": {"n": len(nor), "n_held_normal": sum(kind(r) == "held_normal" for r in rows), "false_reversal": len(fr),
                            "false_reversal_ids": fr, "rate_rep0": rate(len(fr), len(nor)),
                            "rate_all_repeats": rate(sum(c == "REVERSED" for c in allc), len(allc)),
                            "false_reversal_any_repeat_ids": [r["id"] for r in nor if "REVERSED" in cmps(r)]},
            "prev_false_alarms": pf, "new_misses": [i for i in miss if i not in outs], "new_misses_outside_event_list_ref": outs,
            "fluctuation": {"n_multi": len(multi), "all_agree": len(multi) - len(ag), "agree_rate": rate(len(multi) - len(ag), len(multi)),
                            "disagree_ids": ag},
            "fallback": fb_part(rows), "phase": phase_part(rows)}


def ledger_part(cache, truth):
    n = hd = ev = em = pn = pok = sn = sok = 0
    for fid, t in truth.items():
        for rk, evs in cache.get(fid, {}).items():
            n += 1
            hd += (len(evs) > 0) == bool(t.get("has_direction"))
            used = set()
            for te in t.get("events", []):
                ev += 1
                ks = [k for k in [te.get("event_key", "")] + list(te.get("aliases", [])) if k]
                m = next((i for i, e in enumerate(evs) if i not in used and e.get("subject_x") and any(k in e["subject_x"] or e["subject_x"] in k for k in ks)), None)
                if m is None:
                    continue
                used.add(m)
                em += 1
                sn += 1
                sok += evs[m].get("result_state") in (te.get("acceptable_states") or [te.get("result_state")])
                if te.get("phase"):
                    pn += 1
                    pok += evs[m].get("phase") == te["phase"]
    return {"n_ledger_reps": n, "has_direction_accuracy": rate(hd, n), "event_match_rate": rate(em, ev),
            "state_accuracy_given_match": rate(sok, sn), "ledger_phase_n": pn, "ledger_phase_accuracy": rate(pok, pn)}


def per_run(a_, cost, calls, pop, args):
    ce = pop["cost_estimate"]
    jpc = cost / calls if calls else 0.0
    nrep = a_["_n_repeats"]
    fbc = (a_["fallback"]["fallback_calls"] / nrep) if nrep else 0.0
    out = {}
    for lvl, units in ce["article_units_per_run"].items():
        n = ce["ledger_facts_per_run"] * args.prod_ledger_calls_per_fact + units * args.prod_article_calls_per_unit * (1 + fbc)
        un = round((a_["normal_pool"]["rate_rep0"] or 0) * units, 3)
        out[lvl] = {"units_per_run": units, "added_calls": round(n, 2), "added_jpy": round(jpc * n, 3), "unneeded_rewrite_per_run": un}
    return {"jpy_per_call": round(jpc, 5), "fallback_calls_per_repeat": round(fbc, 4), "levels": out}


def criteria(a_, pr):
    g, h, n, c = a_["gold"], a_["held_gold"], a_["normal_pool"], []

    def gc(gid, need):
        x = g.get(gid)
        if not x:
            return "判定不能", "未評価"
        return ("充足" if x["n"] >= 3 and x["k"] >= need else "未達"), f"{x['k']}/{x['n']} rep0={x['rep0']}"
    c.append(("1 HC-012 3/3維持",) + gc("G-01", 3))
    c.append(("2 A5-0 3/3維持",) + gc("G-02", 3))
    c.append(("3 D61 2/3以上",) + gc("G-03", 2))
    if h["items"]:
        ok = h["mean_k_rate"] >= 2 / 3 - 1e-9 and all(v["k"] >= 1 for v in h["items"].values())
        c.append(("4 held-out重大例 平均2/3以上かつ全例1/3以上", "充足" if ok else "未達",
                  {"mean": h["mean_k_rate"], "min": h["min_k_rate"], "per_item": {k: f"{v['k']}/{v['n']}" for k, v in h["items"].items()}}))
    else:
        c.append(("4 held-out重大例 平均2/3以上かつ全例1/3以上", "判定不能", "held-out重大例なし"))
    c.append(("5 正常文+held-out正常例 不要な重大判定0", "充足" if n["false_reversal"] == 0 else "未達",
              f"{n['false_reversal']}/{n['n']} ids={n['false_reversal_ids']} (全repeat{n['false_reversal_any_repeat_ids']})"))
    un = {k: v["unneeded_rewrite_per_run"] for k, v in pr["levels"].items()}
    c.append(("6 不要Rewrite見込み0件/run", "充足" if all(v == 0 for v in un.values()) else "未達", un))
    c.append(("7 新たな重大見逃し0(前回REVERSED→今回非REVERSED)", "充足" if not a_["new_misses"] else "未達",
              {"new_misses": a_["new_misses"], "outside_event_list_ref": a_["new_misses_outside_event_list_ref"]}))
    pf = a_["prev_false_alarms"]
    st = "判定不能" if any(v is None for v in pf.values()) else ("未達" if any(v["recurred"] for v in pf.values()) else "充足")
    c.append(("8 前回誤爆3件(F-09/F-10/F-19)再発なし", st, {k: (v["compares"] if v else None) for k, v in pf.items()}))
    return [{"criterion": x, "result": y, "evidence": z} for x, y, z in c]


def run_cfg(name, rows, cache, truth, prev_rows, prev_sum, pop, summ, args):
    a_ = analyze(rows, prev_rows)
    a_["_n_repeats"] = sum(len(r.get("repeats", [])) for r in rows)
    lp = ledger_part(cache, truth)
    cost = summ.get("cost_jpy", round(sum(r.get("cost_jpy", 0) or 0 for r in rows), 6))
    nl = sum(len(v) for v in cache.values())
    calls = summ.get("n_calls") or (nl + a_["_n_repeats"] + a_["fallback"]["fallback_calls"])
    pr = per_run(a_, cost, calls, pop, args)
    crit = criteria(a_, pr)
    n_rep = a_.pop("_n_repeats")
    fbc = summ.get("fallback_cost_jpy")
    a_["fallback"].update({"summary_fallback_calls": summ.get("fallback_calls"), "fallback_cost_jpy": fbc})
    return {"name": name, "cost_jpy": cost, "n_calls": calls, "n_article_repeats": n_rep, "items": a_, "ledger_side": lp,
            "per_run": pr, "criteria": crit, "regression_vs_trial02": rg.compare(rows, a_, cost, prev_rows, prev_sum)}


def main():
    ap = argparse.ArgumentParser()
    for k in ("results-x", "results-y", "ledger-cache", "truth", "testset", "population", "prev-summary", "prev-results", "out"):
        ap.add_argument("--" + k, required=True)
    for k in ("summary-x", "summary-y", "ledger-cache-y"):
        ap.add_argument("--" + k)
    ap.add_argument("--prod-ledger-calls-per-fact", type=float, default=1.0)
    ap.add_argument("--prod-article-calls-per-unit", type=float, default=1.0)
    a = ap.parse_args()
    truth = jd(a.truth)
    truth = truth.get("facts", truth)
    pop, ps, prows = jd(a.population), jd(a.prev_summary), jl(a.prev_results)
    cx = jd(a.ledger_cache)
    cy = jd(a.ledger_cache_y) if a.ledger_cache_y else cx
    R = {}
    for nm, rp, sp, ca in (("X", a.results_x, a.summary_x, cx), ("Y", a.results_y, a.summary_y, cy)):
        R[nm] = run_cfg(nm, jl(rp), ca, truth, prows, ps, pop, jd(sp) if sp else {}, a)
    out = {"configs": R, "prev_cost_jpy": ps.get("cost_jpy")}
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "trial_summary_03.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# trial_summary_03(事実のみ、Status判定はFable)", ""]
    md += ["## 合格基準チェック(8行)", "", "| 基準 | X | X根拠 | Y | Y根拠 |", "|---|---|---|---|---|"]
    for cx_, cy_ in zip(R["X"]["criteria"], R["Y"]["criteria"]):
        md.append(f"| {cx_['criterion']} | {cx_['result']} | {cx_['evidence']} | {cy_['result']} | {cy_['evidence']} |")
    for nm, c in R.items():
        i = c["items"]
        md += ["", f"## 構成{nm}: 実費{c['cost_jpy']}円 / calls {c['n_calls']} / items {i['n_items']}", ""]
        for k in ("gold", "held_gold", "normal_pool", "prev_false_alarms", "fluctuation", "fallback", "phase", "rep0_distribution"):
            md += [f"### {k}", "```", json.dumps(i[k], ensure_ascii=False, indent=1), "```"]
        md += ["### ledger_side / per_run", "```", json.dumps({"ledger": c["ledger_side"], "per_run": c["per_run"]}, ensure_ascii=False, indent=1), "```",
               "### 前回比(TRIAL-02)", ""] + rg.to_md(c["regression_vs_trial02"])
    open(os.path.join(a.out, "trial_summary_03.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("OK", os.path.join(a.out, "trial_summary_03.json"))


if __name__ == "__main__":
    main()
