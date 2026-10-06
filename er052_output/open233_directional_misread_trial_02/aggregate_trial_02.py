"""TRIAL-02 集計(委任_03, 費用0円/LLM呼出なし)。基準充足の事実のみ出力し、Status判定はしない(Fable)。
usage: aggregate_trial_02.py --results R.jsonl --ledger-cache L.json --truth T.json --testset S.json
       --population P.json --prev trial_summary_01.json --out DIR [--summary summary.json]"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE, HALF = 0.67, 0.335
GOLD = {"G-01": "HC-012", "G-02": "A5-0", "G-03": "D61"}
PREV_FALSE = ["F-09", "F-10", "F-19"]


def jl(p):
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def jd(p):
    return json.load(open(p, encoding="utf-8"))


def cmps(r):
    return [x["compare"] for x in r.get("repeats", [])]


def rep0(r):
    return r.get("final_compare_rep0") or (cmps(r) or [None])[0]


def cls(r):
    return {"真の反転": "gold", "人工反転": "synthetic", "曖昧": "ambiguous", "忠実": "normal"}.get(r.get("label", ""), "other")


def keys_of(ev):
    return [k for k in [ev.get("event_key", "")] + list(ev.get("aliases", [])) if k]


def match(subj, ev):
    return bool(subj) and any(k in subj or subj in k for k in keys_of(ev))


def rate(a, b):
    return round(a / b, 4) if b else None


def gold_part(rows):
    out = {}
    for gid, nm in GOLD.items():
        r = next((x for x in rows if x["id"] == gid), None)
        if r:
            c = cmps(r)
            out[gid] = {"name": nm, "rep0": rep0(r), "rep0_detected": rep0(r) == "REVERSED", "compares": c,
                        "k": sum(x == "REVERSED" for x in c), "n": len(c)}
    return out


def item_part(rows):
    nor = [r for r in rows if cls(r) == "normal"]
    fr = [r["id"] for r in nor if rep0(r) == "REVERSED"]
    allc = [c for r in nor for c in cmps(r)]
    dist = {}
    for r in rows:
        dist[rep0(r)] = dist.get(rep0(r), 0) + 1
    pf = {}
    for i in PREV_FALSE:
        r = next((x for x in rows if x["id"] == i), None)
        if r:
            c = cmps(r)
            pf[i] = {"rep0": rep0(r), "compares": c, "resolved": all(x != "REVERSED" for x in c) and rep0(r) != "REVERSED"}
        else:
            pf[i] = {"rep0": None, "compares": [], "resolved": None}
    syn = [r for r in rows if cls(r) == "synthetic"]
    strict = [r for r in syn if r.get("acceptable_compare") == ["REVERSED"]]
    tol = [r for r in syn if r not in strict]
    amb = [r for r in rows if cls(r) == "ambiguous"]
    multi = [r for r in rows if len(cmps(r)) >= 3]
    return {"n_items": len(rows), "rep0_distribution": dist,
            "normal": {"n": len(nor), "false_reversal": len(fr), "false_reversal_ids": fr, "rate_rep0": rate(len(fr), len(nor)),
                       "rate_all_repeats": rate(sum(c == "REVERSED" for c in allc), len(allc)),
                       "unclear": sum(rep0(r) == "UNCLEAR" for r in nor), "not_mentioned": sum(rep0(r) == "NOT_MENTIONED" for r in nor)},
            "unclear_total": dist.get("UNCLEAR", 0), "not_mentioned_total": dist.get("NOT_MENTIONED", 0),
            "gold": gold_part(rows), "prev_false_alarms": pf,
            "synthetic": {"n": len(syn), "strict_n": len(strict), "strict_detected": sum(rep0(r) == "REVERSED" for r in strict),
                          "tolerant_n": len(tol), "tolerant_detected": sum(rep0(r) == "REVERSED" for r in tol),
                          "tolerant_ok_by_acceptable": sum(rep0(r) in (r.get("acceptable_compare") or []) for r in tol),
                          "detected": sum(rep0(r) == "REVERSED" for r in syn), "missed_ids": [r["id"] for r in syn if rep0(r) != "REVERSED"]},
            "ambiguous": {r["id"]: {"rep0": rep0(r), "compares": cmps(r), "any_reversed": "REVERSED" in cmps(r) or rep0(r) == "REVERSED"} for r in amb},
            "fluctuation": {"n_multi_repeat_items": len(multi), "all_agree": sum(len(set(cmps(r))) == 1 for r in multi),
                            "agree_rate": rate(sum(len(set(cmps(r))) == 1 for r in multi), len(multi)),
                            "disagree_ids": [r["id"] for r in multi if len(set(cmps(r))) > 1]}}


def ledger_part(cache, truth):
    hd_ok = hd_n = ev_n = ev_match = st_ok = extra = reps_n = 0
    stable = stable_n = 0
    for fid, t in truth.items():
        reps = cache.get(fid, {})
        sigs = []
        for rk, evs in reps.items():
            reps_n += 1
            hd_n += 1
            hd_ok += (len(evs) > 0) == bool(t.get("has_direction"))
            used, sig = set(), []
            for te in t.get("events", []):
                ev_n += 1
                m = next((i for i, e in enumerate(evs) if i not in used and match(e.get("subject_x", ""), te)), None)
                if m is not None:
                    used.add(m)
                    ev_match += 1
                    acc = te.get("acceptable_states") or [te.get("result_state")]
                    st_ok += evs[m].get("result_state") in acc
                    sig.append((te.get("event_key"), evs[m].get("result_state")))
            extra += len(evs) - len(used)
            sigs.append(sorted(map(str, sig)) + [len(evs)])
        if len(sigs) >= 2:
            stable_n += 1
            stable += all(s == sigs[0] for s in sigs)
    return {"n_facts": len(truth), "n_ledger_reps": reps_n, "has_direction_accuracy": rate(hd_ok, hd_n),
            "event_match_rate": rate(ev_match, ev_n), "state_accuracy_given_match": rate(st_ok, ev_match),
            "state_accuracy_all_truth_events": rate(st_ok, ev_n), "extra_events_per_rep": round(extra / reps_n, 3) if reps_n else None,
            "repeat_agreement_facts": f"{stable}/{stable_n}", "repeat_agreement_rate": rate(stable, stable_n)}


def article_part(rows, truth):
    sel_ok = sel_n = st_ok = st_n = 0
    for r in rows:
        exp = r.get("expected_event_subject")
        if exp:
            tev = [e for e in truth.get(r["fact_id"], {}).get("events", []) if match(exp, e)]
            for x in r.get("repeats", []):
                sel_n += 1
                s = x.get("selected_subject") or ""
                sel_ok += bool(s) and (exp in s or s in exp or any(match(s, e) for e in tev))
        ea = r.get("expected_article_state")
        if ea:
            for x in r.get("repeats", []):
                st_n += 1
                st_ok += x.get("article_state") == ea
    return {"selected_event_n": sel_n, "selected_event_accuracy": rate(sel_ok, sel_n), "article_state_n": st_n,
            "article_state_accuracy": rate(st_ok, st_n)}


def per_run(it, pop, cost, calls, args):
    ce = pop["cost_estimate"]
    jpc = cost / calls if calls else 0.0
    out = {}
    for lvl, units in ce["article_units_per_run"].items():
        n = ce["ledger_facts_per_run"] * args.prod_ledger_calls_per_fact + units * args.prod_article_calls_per_unit
        un = round((it["normal"]["rate_rep0"] or 0) * units, 3)
        out[lvl] = {"units_per_run": units, "added_calls": round(n, 2), "added_jpy": round(jpc * n, 3),
                    "unneeded_rewrite_per_run": un, "vs_baseline_rewrite_0.67": round(un / BASE, 2), "le_half_baseline_0.335": un <= HALF}
    return {"jpy_per_call": round(jpc, 5), "levels": out}


def criteria(it, pr, prev_cfg):
    g, c = it["gold"], []
    def gc(gid):
        x = g.get(gid)
        return ("判定不能", "未評価") if not x else (("充足" if x["n"] >= 3 and x["k"] == x["n"] else "未達"), f"{x['k']}/{x['n']} rep0={x['rep0']}")
    c.append(("1 HC-012 3/3検出",) + gc("G-01"))
    c.append(("2 A5-0 3/3検出",) + gc("G-02"))
    r = it["normal"]["rate_rep0"]
    c.append(("3 正常文の誤重大判定2%以下", "判定不能" if r is None else ("充足" if r <= 0.02 else "未達"),
              f"{it['normal']['false_reversal']}/{it['normal']['n']}={r} ids={it['normal']['false_reversal_ids']}"))
    lv = pr["levels"]
    c.append(("4 不要Rewrite見込み0.335以下(全3水準)", "充足" if all(v["le_half_baseline_0.335"] for v in lv.values()) else "未達",
              {k: v["unneeded_rewrite_per_run"] for k, v in lv.items()}))
    pf = it["prev_false_alarms"]
    st = "判定不能" if any(v["resolved"] is None for v in pf.values()) else ("充足" if all(v["resolved"] for v in pf.values()) else "未達")
    c.append(("5 前回誤爆3件解消(3反復ともREVERSEDでない)", st, {k: v["compares"] for k, v in pf.items()}))
    pg = (prev_cfg.get("gold", {}) or {}).get("per_item", {})
    prev_det = [i for i, v in pg.items() if v and v[0] == "REVERSED"]
    prev_syn = [i for i in (it.get("_syn_ids") or []) if i not in prev_cfg.get("synthetic", {}).get("missed_ids", [])]
    cur_miss = [i for i in prev_det if i in g and not g[i]["rep0_detected"]] + [i for i in prev_syn if i in it["synthetic"]["missed_ids"]]
    c.append(("6 新しい重大見逃しなし(前回検出gold/人工反転の今回見逃し)", "充足" if not cur_miss else "未達", {"new_misses": cur_miss}))
    return [{"criterion": a, "result": b, "evidence": e} for a, b, e in c]


def main():
    ap = argparse.ArgumentParser()
    for k in ("results", "ledger-cache", "truth", "testset", "population", "prev", "out"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--summary")
    ap.add_argument("--prev-config", default="same_blind")
    ap.add_argument("--prod-ledger-calls-per-fact", type=float, default=1.0)
    ap.add_argument("--prod-article-calls-per-unit", type=float, default=1.0)
    a = ap.parse_args()
    rows, cache, truth = jl(a.results), jd(a.ledger_cache), jd(a.truth)
    truth = truth.get("facts", truth)
    pop, prev = jd(a.population), jd(a.prev)["configs"][a.prev_config]
    it = item_part(rows)
    it["_syn_ids"] = [r["id"] for r in rows if cls(r) == "synthetic"]
    S = jd(a.summary) if a.summary else {}
    cost = S.get("cost_jpy", round(sum(r.get("cost_jpy", 0) for r in rows), 6))
    nrep = sum(len(v) for v in cache.values())
    calls = S.get("n_calls") or S.get("calls") or (nrep + sum(len(r.get("repeats", [])) for r in rows))
    pr = per_run(it, pop, cost, calls, a)
    crit = criteria(it, pr, prev)
    it.pop("_syn_ids")
    import regression_vs_trial01 as rg
    out = {"cost_jpy": cost, "n_calls": calls, "items": it, "ledger_side": ledger_part(cache, truth),
           "article_side": article_part(rows, truth), "per_run": pr, "criteria": crit}
    out["regression"] = rg.compare({**it, "per_run": pr}, prev)
    out.update({"gold": it["gold"], "normal": it["normal"], "unclear_total": it["unclear_total"], "synthetic": it["synthetic"]})
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "trial_summary_02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# trial_summary_02(事実のみ、Status判定はFable)", "", f"実費 {cost}円 / calls {calls} / items {it['n_items']}", "",
          "## 合格基準チェック", "", "| 基準 | 結果 | 根拠 |", "|---|---|---|"]
    md += [f"| {c['criterion']} | {c['result']} | {c['evidence']} |" for c in crit]
    md += ["", "## 前回比", ""] + rg.to_md(out["regression"])
    for k in ("gold", "normal", "prev_false_alarms", "synthetic", "ambiguous", "fluctuation"):
        md += ["", f"## {k}", "```", json.dumps(it[k], ensure_ascii=False, indent=1), "```"]
    for k in ("ledger_side", "article_side", "per_run"):
        md += ["", f"## {k}", "```", json.dumps(out[k], ensure_ascii=False, indent=1), "```"]
    open(os.path.join(a.out, "trial_summary_02.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("OK", os.path.join(a.out, "trial_summary_02.json"))


if __name__ == "__main__":
    main()
