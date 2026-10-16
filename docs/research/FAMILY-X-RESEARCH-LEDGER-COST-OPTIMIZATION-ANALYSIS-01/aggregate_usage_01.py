"""FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-ANALYSIS-01 read-only集計script。
ネットワーク・API呼出なし。raw_usage_log.jsonlのstage=research/ledger行を
pricing_snapshot.jsonの単価で再計算し、cost.jsonと突合する。
USD_JPYは er012 efam.USD_JPY=160.0 (コード値、er012_e_family_entertainment_two_level_runner_01.py:68)。
"""
import argparse, json, os, sys

USD_JPY = 160.0
WEB_SEARCH_MODEL = "N/A (tool, all models)"


def load_price(path):
    d = json.load(open(path, encoding="utf-8"))
    tbl = {}
    for p in d["prices"]:
        tbl[(p["model"], p["meter"])] = p["price"]
    return tbl


def breakdown(rec, tbl):
    m = rec["model_id"]
    ws = rec.get("web_search_call_count") or 0
    it, ot, ct = rec.get("input_tokens") or 0, rec.get("output_tokens") or 0, rec.get("cached_input_tokens") or 0
    # cost.jsonの実装(er019 compute_stage_cost_breakdown)はcachedを別計上せずinput全量に通常単価を適用
    # (cached=0のため差なし)。ここでは同実装に合わせる。
    usd_in = it * tbl[(m, "input_tokens")] / 1e6
    usd_out = ot * tbl[(m, "output_tokens")] / 1e6
    usd_ws = ws * tbl[(WEB_SEARCH_MODEL, "web_search_call")] / 1000
    return {
        "stage": rec["stage"], "model_id": m, "attempt_number": rec.get("attempt_number"),
        "success": rec.get("success"), "web_search_call_count": ws,
        "input_tokens": it, "output_tokens": ot, "cached_input_tokens": ct,
        "reasoning_tokens": rec.get("reasoning_tokens"),
        "jpy_input": usd_in * USD_JPY, "jpy_output": usd_out * USD_JPY, "jpy_web_search": usd_ws * USD_JPY,
        "jpy_total": (usd_in + usd_out + usd_ws) * USD_JPY,
    }


def per_run(log_path, tbl):
    rows = []
    for line in open(log_path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("stage") in ("research", "ledger"):
            rows.append(breakdown(r, tbl))
    return rows


def selection_info(run_dir):
    out = {}
    p = os.path.join(run_dir, "storyline_b3", "fact_selection_evidence.json")
    if os.path.exists(p):
        d = json.load(open(p, encoding="utf-8"))
        out["full_ledger_facts"] = len(d["full_ledger_fact_ids"])
        out["selected_facts"] = len(d["selected_fact_ids"])
        out["selected_ids"] = d["selected_fact_ids"]
    v = os.path.join(run_dir, "research_ledger", "verdict_counts.json")
    if os.path.exists(v):
        out["verdict_counts"] = json.load(open(v, encoding="utf-8"))
    for stage, fn in (("research", "researcher_full_record.json"), ("ledger", "verification_full_record.json")):
        a = os.path.join(run_dir, "research_ledger", "audit", fn)
        if os.path.exists(a):
            d = json.load(open(a, encoding="utf-8"))
            out[stage + "_n_queries_logged"] = len(d["search_usage"]["queries"])
            out[stage + "_prompt_chars"] = len(d["prompt"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usage-log", required=True)
    ap.add_argument("--cost-json", required=True)
    ap.add_argument("--pricing", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--compare-run", action="append", default=[], help="比較用run dir(read-only、複数可)")
    a = ap.parse_args()
    tbl = load_price(a.pricing)
    rows = per_run(a.usage_log, tbl)
    cost = json.load(open(a.cost_json, encoding="utf-8"))["by_stage_jpy"]
    summ = {}
    for st in ("research", "ledger"):
        rs = [r for r in rows if r["stage"] == st]
        s = {k: sum(r[k] for r in rs) for k in ("web_search_call_count", "input_tokens", "output_tokens",
                                                "cached_input_tokens", "reasoning_tokens",
                                                "jpy_input", "jpy_output", "jpy_web_search", "jpy_total")}
        s["n_api_calls"] = len(rs)
        s["models"] = sorted({r["model_id"] for r in rs})
        s["cost_json_jpy"] = cost.get(st)
        s["diff_vs_cost_json"] = round(s["jpy_total"] - cost.get(st, 0), 4)
        s["web_search_share"] = s["jpy_web_search"] / s["jpy_total"]
        s["token_share"] = (s["jpy_input"] + s["jpy_output"]) / s["jpy_total"]
        summ[st] = s
    tot = {k: summ["research"][k] + summ["ledger"][k] for k in ("jpy_total", "jpy_web_search", "jpy_input", "jpy_output", "web_search_call_count")}
    tot["web_search_share"] = tot["jpy_web_search"] / tot["jpy_total"]
    tot["unit_fee_per_call_jpy"] = tbl[(WEB_SEARCH_MODEL, "web_search_call")] / 1000 * USD_JPY
    res = {
        "assumptions": {"usd_jpy": USD_JPY, "prices_usd_per_1M": {
            "gpt-6-luna.input": tbl[("gpt-6-luna", "input_tokens")],
            "gpt-6-luna.cached": tbl[("gpt-6-luna", "cached_input_tokens")],
            "gpt-6-luna.output": tbl[("gpt-6-luna", "output_tokens")],
            "web_search_per_1000_calls": tbl[(WEB_SEARCH_MODEL, "web_search_call")]}},
        "rows": rows, "summary": summ, "total_research_plus_ledger": tot,
        "ledger_minus_research_jpy": summ["ledger"]["jpy_total"] - summ["research"]["jpy_total"],
        "this_run_selection": selection_info(os.path.dirname(a.usage_log)),
        "compare_runs": {},
    }
    d = res["ledger_minus_research_jpy"]
    res["ledger_minus_research_decomposition_jpy"] = {
        "web_search_fee": summ["ledger"]["jpy_web_search"] - summ["research"]["jpy_web_search"],
        "input_tokens": summ["ledger"]["jpy_input"] - summ["research"]["jpy_input"],
        "output_tokens": summ["ledger"]["jpy_output"] - summ["research"]["jpy_output"],
        "total": d}
    for rd in a.compare_run:
        lp = os.path.join(rd, "raw_usage_log.jsonl")
        rr = per_run(lp, tbl) if os.path.exists(lp) else []
        res["compare_runs"][rd] = {
            "rows": [{k: r[k] for k in ("stage", "model_id", "web_search_call_count", "input_tokens", "output_tokens", "jpy_web_search", "jpy_total")} for r in rr],
            "selection": selection_info(rd)}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({"summary": {k: {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()} for k, v in summ.items()},
                      "total": {k: round(v, 4) for k, v in tot.items()},
                      "ledger_minus_research": res["ledger_minus_research_decomposition_jpy"]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    sys.exit(main())
