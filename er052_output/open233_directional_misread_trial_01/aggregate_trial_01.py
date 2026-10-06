"""委任_02 一次集計(¥0)。run_<config>/results_*.jsonl + testset_01.json -> trial_summary_01.{json,md}"""
import json
import os

D = os.path.dirname(os.path.abspath(__file__))
TS = json.load(open(os.path.join(D, "testset_01.json"), encoding="utf-8"))
POP = json.load(open(os.path.join(D, "population_01.json"), encoding="utf-8"))
REG = TS["fact_registry"]
CONFIGS = ["same_blind", "same_nonblind", "split_blind"]
NORMAL_ROLES = ("faithful_state", "same_fact_not_mentioned", "non_directional")
LEVELS = POP["cost_estimate"]["article_units_per_run"]
LEDGER_FACTS = POP["cost_estimate"]["ledger_facts_per_run"]
BASE_REWRITE = 0.67


def load(cfg):
    p = os.path.join(D, f"run_{cfg}", f"results_{cfg}.jsonl")
    if not os.path.exists(p):
        return None
    rows = [json.loads(x) for x in open(p, encoding="utf-8")]
    summ = json.load(open(os.path.join(D, f"run_{cfg}", f"summary_{cfg}.json"), encoding="utf-8"))
    cl = []
    cp = os.path.join(D, f"run_{cfg}", f"call_log_{cfg}.jsonl")
    if os.path.exists(cp):
        cl = [json.loads(x) for x in open(cp, encoding="utf-8")]
    return {"rows": rows, "summary": summ, "call_log": cl}


def split_costs(cfg, rows, cl, led_rep):
    """call_logを再生して Ledger側/記事側 に分類(処理順の決定性を利用)。"""
    seq, seen, i = [], set(), 0
    for r in rows:
        reps = len(r.get("repeat_events", [])) or 1
        if cfg == "same_nonblind":
            seq += ["nb"] * reps
            continue
        if r["fact_id"] + "|" + str(r["id"].split("-")[0]) not in seen and r["fact_id"] not in seen:
            seen.add(r["fact_id"])
            seq += ["L"] * led_rep
        for evs in r.get("repeat_events", []):
            seq += ["A"] * len(evs)
    # reuse時は記事側がcall_logに出ないため、記事側はcall_logに含まれない分を除外する
    kinds = {"L": [], "A": [], "nb": []}
    j = 0
    for k in seq:
        if k == "A" and cfg == "split_blind" and j >= len(cl):
            continue
        if j < len(cl):
            kinds[k].append(cl[j]["jpy"])
        j += 1
    return kinds


def analyze(cfg, d, led_rep):
    rows, s = d["rows"], d["summary"]
    A = {"config": cfg, "n_rows": len(rows), "calls": s.get("calls"), "cost_jpy": s.get("cost_jpy"),
         "stopped_by_budget": s.get("stopped_by_budget"), "n_failed_calls": s.get("n_failed_calls"),
         "models": s.get("models"), "reuse_hits": s.get("reuse_hits"), "reuse_miss": s.get("reuse_miss")}
    A["jpy_per_call"] = round(s["cost_jpy"] / s["calls"], 5) if s.get("calls") else None
    dist = {}
    for r in rows:
        dist[r["compare"]] = dist.get(r["compare"], 0) + 1
    A["compare_distribution"] = dist
    gold = [r for r in rows if r.get("role") == "gold_reversal"]
    A["gold"] = {"n": len(gold), "detected_rep0": sum(r["compare"] == "REVERSED" for r in gold),
                 "per_item": {r["id"]: r["repeat_compares"] for r in gold},
                 "detected_repeats": sum(c == "REVERSED" for r in gold for c in r["repeat_compares"]),
                 "total_repeats": sum(len(r["repeat_compares"]) for r in gold)}
    syn = [r for r in rows if r.get("role") == "synthetic_reversal"]
    strict = [r for r in syn if (r["expected"].get("acceptable_compare") or []) == ["REVERSED"]]
    tol = [r for r in syn if r not in strict]
    A["synthetic"] = {"n": len(syn), "strict_n": len(strict), "strict_detected": sum(r["compare"] == "REVERSED" for r in strict),
                      "tolerant_n": len(tol), "tolerant_detected": sum(r["compare"] == "REVERSED" for r in tol),
                      "tolerant_ok_by_acceptable": sum(r["compare"] in (r["expected"].get("acceptable_compare") or []) for r in tol),
                      "all_detected": sum(r["compare"] == "REVERSED" for r in syn),
                      "missed_ids": [r["id"] for r in syn if r["compare"] != "REVERSED"]}
    allrev = gold + syn
    A["reversal_total"] = {"n": len(allrev), "detected": sum(r["compare"] == "REVERSED" for r in allrev),
                           "missed": sum(r["compare"] != "REVERSED" for r in allrev)}
    nor = [r for r in rows if r.get("role") in NORMAL_ROLES]
    fr = [r["id"] for r in nor if r["compare"] == "REVERSED"]
    nor_rep = [(r["id"], c) for r in nor for c in r["repeat_compares"]]
    A["normal"] = {"n": len(nor), "false_reversal": len(fr), "false_reversal_ids": fr,
                   "rate": round(len(fr) / len(nor), 4) if nor else None,
                   "rate_all_repeats": round(sum(c == "REVERSED" for _, c in nor_rep) / len(nor_rep), 4) if nor_rep else None,
                   "unclear": sum(r["compare"] == "UNCLEAR" for r in nor)}
    A["unclear_total"] = dist.get("UNCLEAR", 0)
    amb = [r for r in rows if r.get("role") == "ambiguous"]
    A["ambiguous"] = {r["id"]: {"expected": r["expected"]["expected_compare"], "repeat_compares": r["repeat_compares"]} for r in amb}
    # Ledger側(fact単位)
    facts = {}
    for r in rows:
        facts.setdefault(r["fact_id"], r)
    L = {}
    hd_ok = st_ok = st_n = fluct = any_ok = 0
    for fid, r in facts.items():
        reg = REG.get(fid, {})
        led = r.get("ledger", {})
        rhd = led.get("repeat_has_direction") or [bool(evs) for evs in r["repeat_events"]]
        rst = led.get("repeat_states") or [[e["ledger_state"] for e in evs] for evs in r["repeat_events"]]
        exp_hd = bool(reg.get("has_direction", r["expected"].get("has_direction")))
        acc = reg.get("acceptable_ledger_states") or [reg.get("expected_ledger_state")]
        firsts = [(s[0] if s else None) for s in rst]
        L[fid] = {"expected_has_direction": exp_hd, "has_direction_repeats": rhd, "states_repeats": firsts,
                  "acceptable": acc}
        hd_ok += sum(h == exp_hd for h in rhd)
        if exp_hd:
            st_n += len(firsts)
            st_ok += sum(f in acc for f in firsts)
        any_ok += sum(any(x in acc for x in s) for s in rst) if exp_hd else 0
        fluct += (len(set(map(str, rhd))) > 1 or len(set(map(str, firsts))) > 1)
    nrep = sum(len(v["has_direction_repeats"]) for v in L.values())
    A["ledger_side"] = {"n_facts": len(L), "has_direction_accuracy": round(hd_ok / nrep, 4) if nrep else None,
                        "state_accuracy_directional": round(st_ok / st_n, 4) if st_n else None,
                        "state_accuracy_any_event": round(any_ok / st_n, 4) if st_n else None, "facts_with_repeat_fluctuation": fluct, "per_fact": L}
    if cfg != "same_nonblind":
        pass
    ar = [r for r in rows if r["events"] and r["expected"].get("expected_article_state")]
    A["article_state_accuracy"] = round(sum(r["events"][0]["article_state"] == r["expected"]["expected_article_state"] for r in ar) / len(ar), 4) if ar else None
    A["article_state_n"] = len(ar)
    kinds = split_costs(cfg, rows, d["call_log"], led_rep)
    avg = lambda v: round(sum(v) / len(v), 5) if v else None
    A["unit_cost"] = {"ledger_jpy_per_call": avg(kinds["L"]), "article_jpy_per_call": avg(kinds["A"]),
                      "nonblind_jpy_per_call": avg(kinds["nb"]), "n_ledger_calls": len(kinds["L"]),
                      "n_article_calls": len(kinds["A"]), "n_nb_calls": len(kinds["nb"])}
    return A


def per_run(A, art_cost_fallback):
    """1 runあたり追加処理件数/費用/不要Rewrite見込み(3水準)。"""
    u = A["unit_cost"]
    out = {}
    fr = A["normal"]["rate"] or 0.0
    for lvl, units in LEVELS.items():
        if A["config"] == "same_nonblind":
            cost = (u["nonblind_jpy_per_call"] or 0) * units
            calls = units
        else:
            art = u["article_jpy_per_call"] if u["article_jpy_per_call"] is not None else art_cost_fallback
            cost = (u["ledger_jpy_per_call"] or 0) * LEDGER_FACTS + (art or 0) * units
            calls = LEDGER_FACTS + units
        out[lvl] = {"units_per_run": units, "added_calls": round(calls, 2), "added_jpy": round(cost, 3),
                    "unneeded_rewrite_per_run": round(fr * units, 3),
                    "vs_baseline_rewrite_0.67": round(fr * units / BASE_REWRITE, 2)}
    return out


def main():
    data = {c: load(c) for c in CONFIGS}
    res = {}
    for c, d in data.items():
        if d:
            res[c] = analyze(c, d, 3 if c != "same_nonblind" else 1)
    fb = (res.get("same_blind") or {}).get("unit_cost", {}).get("article_jpy_per_call")
    for c, A in res.items():
        A["per_run"] = per_run(A, fb)
    cmp_ = {}
    if "same_blind" in res and "split_blind" in res:
        a, b = res["same_blind"]["ledger_side"]["per_fact"], res["split_blind"]["ledger_side"]["per_fact"]
        pairs = same = 0
        fact_agree = 0
        for fid in a:
            if fid not in b:
                continue
            fa, fb_ = a[fid], b[fid]
            n = min(len(fa["states_repeats"]), len(fb_["states_repeats"]))
            ag = [(fa["has_direction_repeats"][i], fa["states_repeats"][i]) == (fb_["has_direction_repeats"][i], fb_["states_repeats"][i]) for i in range(n)]
            pairs += n
            same += sum(ag)
            fact_agree += all(ag)
        cmp_["ledger_same_vs_split"] = {"pair_agreement": round(same / pairs, 4) if pairs else None, "pairs": pairs,
                                        "facts_fully_agree": fact_agree, "facts": len(a)}
    if "same_blind" in res and "same_nonblind" in res:
        cmp_["blind_vs_nonblind_gold"] = {c: {"rep0": res[c]["gold"]["detected_rep0"],
                                               "repeats": f"{res[c]['gold']['detected_repeats']}/{res[c]['gold']['total_repeats']}"}
                                           for c in ("same_blind", "same_nonblind")}
    out = {"configs": res, "comparison": cmp_, "baseline_rewrite_per_run": BASE_REWRITE,
           "total_cost_jpy": round(sum(A["cost_jpy"] or 0 for A in res.values()), 4)}
    json.dump(out, open(os.path.join(D, "trial_summary_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    md = ["# trial_summary_01(委任_02 一次集計、Status分類はFable)", "", f"累計実費: ¥{out['total_cost_jpy']}", "",
          "| 項目 | " + " | ".join(res) + " |", "|---|" + "---|" * len(res)]
    def row(label, f):
        md.append(f"| {label} | " + " | ".join(str(f(A)) for A in res.values()) + " |")
    row("model(ledger/article)", lambda A: f"{A['models']['ledger']}/{A['models']['article']}")
    row("calls/実費¥/¥per call", lambda A: f"{A['calls']}/{A['cost_jpy']}/{A['jpy_per_call']}")
    row("失敗call/予算停止", lambda A: f"{A['n_failed_calls']}/{A['stopped_by_budget']}")
    row("gold検出(rep0)/repeat計", lambda A: f"{A['gold']['detected_rep0']}/{A['gold']['n']}, {A['gold']['detected_repeats']}/{A['gold']['total_repeats']}")
    row("人工反転 厳密/許容 検出", lambda A: f"{A['synthetic']['strict_detected']}/{A['synthetic']['strict_n']}, {A['synthetic']['tolerant_detected']}/{A['synthetic']['tolerant_n']}")
    row("反転17件 検出/見逃し", lambda A: f"{A['reversal_total']['detected']}/{A['reversal_total']['missed']}")
    row("正常43 誤反転(rate)", lambda A: f"{A['normal']['false_reversal']} ({A['normal']['rate']}) 全repeat率{A['normal']['rate_all_repeats']}")
    row("判断不能(UNCLEAR)全体/正常内", lambda A: f"{A['unclear_total']}/{A['normal']['unclear']}")
    row("機械比較分布", lambda A: A["compare_distribution"])
    row("Ledger has_direction精度/state精度/揺れfact", lambda A: f"{A['ledger_side']['has_direction_accuracy']}/{A['ledger_side']['state_accuracy_directional']}(any{A['ledger_side']['state_accuracy_any_event']})/{A['ledger_side']['facts_with_repeat_fluctuation']}")
    row("記事側state精度(n)", lambda A: f"{A['article_state_accuracy']}({A['article_state_n']})")
    row("曖昧3件", lambda A: A["ambiguous"])
    md += ["", "## 比較", "", "```", json.dumps(cmp_, ensure_ascii=False, indent=1), "```", "",
           "## 1 runあたり追加処理・費用・不要Rewrite見込み(基準: 現行Rewrite 0.67件/run)", ""]
    for c, A in res.items():
        md.append(f"### {c}")
        for lvl, v in A["per_run"].items():
            md.append(f"- {lvl}(記事側{v['units_per_run']}単位+Ledger{LEDGER_FACTS}fact): 追加call {v['added_calls']}/run、追加¥{v['added_jpy']}/run、不要Rewrite見込み {v['unneeded_rewrite_per_run']}件/run(現行0.67の{v['vs_baseline_rewrite_0.67']}倍)")
    md += ["", "(注) 反転17件=gold3+人工14。誤反転はrep0基準、全repeat率併記。詳細はtrial_summary_01.json。"]
    open(os.path.join(D, "trial_summary_01.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
