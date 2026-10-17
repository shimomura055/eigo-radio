"""RLCT 委任_01 費用見積の再現script(read-only、API呼出なし、JPY0)。
出典: 各runの raw_usage_log.jsonl(実測) + pricing_snapshot.json + search_cap_analysis_01.json。
見積は manual_substitution(実測単価x想定呼出)。実測ではない。
"""
import json
import sys

USD_JPY = 160.0
ROOT = "."
PRICING = ROOT + "/er005_output/cost_baseline_01/pricing_snapshot.json"
SR = "er052_output/factlock_astra_e2e_trial_01/stage_r/"
ARTICLES = [  # key, run dir
    ("coffee_fxpw", "er019_output/coffee_prices/run_fxpw_01"),
    ("openai_copyright", SR + "openai_copyright"),
    ("inbound_tourism", SR + "inbound_tourism"),
    ("streaming_price", SR + "streaming_price"),
    ("central_bank_mortgage", SR + "central_bank_mortgage"),
]
analysis = json.load(open("docs/research/FAMILY-X-RESEARCH-LEDGER-COST-OPTIMIZATION-TRIAL-01/search_cap_analysis_01.json", encoding="utf-8"))
ana = {r["run"]: r for r in analysis["runs"]}
price = json.load(open(PRICING, encoding="utf-8"))
tbl = {(p["model"], p["meter"]): p["price"] for p in price["prices"]}
FEE = 10.0 / 1000 * USD_JPY  # JPY/call
SOL = "gpt-6.1-sol"


def jpy(model, it, ot, ws=0):
    return ((it * tbl[(model, "input_tokens")] + ot * tbl[(model, "output_tokens")]) / 1e6 + ws * 10 / 1000) * USD_JPY


def stage(run):
    out = {}
    for l in open(run + "/raw_usage_log.jsonl", encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r["stage"] in ("research", "ledger", "storyline_b3"):
                out[r["stage"]] = r
    return out


rows = []
for key, run in ARTICLES:
    st = stage(run)
    a = ana[run]
    n = a["n_facts"]
    sel = len(a["selected_fact_ids"])
    verd = a["verdicts"]
    n_b3 = n - verd["REJECTED"]
    R = jpy(st["research"]["model_id"], st["research"]["input_tokens"], st["research"]["output_tokens"], st["research"]["web_search_call_count"])
    Lr = st["ledger"]
    calls0 = Lr["web_search_call_count"]
    L0 = jpy(Lr["model_id"], Lr["input_tokens"], Lr["output_tokens"], calls0)
    per_call = FEE + 9000 * tbl[(Lr["model_id"], "input_tokens")] / 1e6 * USD_JPY  # 検索1回の手数料+検索本文token(仮定9,000tok)
    fixed = max(0.0, L0 - per_call * calls0)
    b = st["storyline_b3"]
    b3_is_sol = b["model_id"].startswith("gpt-6.1-sol")
    # B3(sol)費用: 実測がsolならそれ、無ければ当該runのB3 token実測をsol単価へ換算(出力token数は同等と仮定=仮定)
    B3 = jpy(b["model_id"], b["input_tokens"], b["output_tokens"]) if b3_is_sol else jpy(SOL, b["input_tokens"], b["output_tokens"])
    # 案1: 上限3(クエリ単位)の削減額(heuristic下限)を期待値、倍(または fxpw はRLCO手計算5.1)を上限側の削減とする
    s3 = a["cap_simulation"].get("N3_cap_on_queries", {}).get("saving_jpy_est", 0.0)
    s_hi = 5.1 if key == "coffee_fxpw" else 2 * s3
    # 案2: 選定Factのみ検証。呼出数 = max(2, calls0*sel/n_b3) (期待)、上限 = min(calls0, 2*期待+1)
    exp_calls = max(2.0, calls0 * sel / n_b3)
    hi_calls = min(float(calls0), 2 * exp_calls + 1)
    prompt_scale = (0.3 + 0.7 * sel / n_b3)  # 検証対象draftが小さくなる分の固定部縮小(仮定)
    L2_exp = per_call * exp_calls + fixed * prompt_scale
    L2_hi = per_call * hi_calls + fixed * prompt_scale
    # 再選定: 確率(期待) = 1-(1-p)^sel, p=全標本REJECTED率(2/125)。上限=2回再選定(B3'+新規2Fact検証)ごと。
    p = 2 / 125
    p_resel_exp = 1 - (1 - p) ** sel
    resel_unit = B3 * 1.1 + per_call * 2 + 0.3  # B3'(不合格理由追加で入力+10%) + 新規Fact約2件の検証
    # 方式別 新規API費用(期待 / 上限)
    M0_new_exp = 0.0 if b3_is_sol else B3
    M0_new_hi = M0_new_exp + (0.0 if b3_is_sol else 0.2 * B3)
    M1_exp = (L0 - s3) + B3
    M1_hi = L0 * 1.15 + B3 * 1.2  # Ledger再実行のばらつき+15%、B3 +20%
    M2_exp = B3 + L2_exp + p_resel_exp * resel_unit
    M2_hi = B3 * 1.2 + L2_hi + 2 * resel_unit
    # M3: 初回B3はM2と共有(同一入力)。Ledgerは選定のみ+上限。再選定は検証結果依存で別枝
    M3_exp = (L2_exp - 0.5 * s3 * sel / n_b3) + p_resel_exp * resel_unit
    M3_hi = L2_hi + 2 * resel_unit
    rows.append({
        "article": key, "facts_draft": n, "facts_b3_visible": n_b3, "selected": sel, "verdicts": verd,
        "research_existing_jpy": round(R, 2), "ledger_existing_calls": calls0, "ledger_existing_jpy": round(L0, 2),
        "b3_existing_model": b["model_id"], "b3_sol_est_jpy": round(B3, 2), "b3_sol_existing_measured": b3_is_sol,
        "per_call_jpy": round(per_call, 3), "ledger_fixed_jpy": round(fixed, 2),
        "case1_saving_cap3_exp_jpy": round(s3, 2), "case1_saving_hi_jpy": round(s_hi, 2),
        "case2_ledger_sel_exp_calls": round(exp_calls, 1), "case2_ledger_sel_exp_jpy": round(L2_exp, 2), "case2_ledger_sel_hi_jpy": round(L2_hi, 2),
        "p_reselect_exp": round(p_resel_exp, 3), "resel_unit_jpy": round(resel_unit, 2),
        "new_cost_jpy": {
            "M0_conventional": [round(M0_new_exp, 2), round(M0_new_hi, 2)],
            "M1_cap": [round(M1_exp, 2), round(M1_hi, 2)],
            "M2_select_then_verify": [round(M2_exp, 2), round(M2_hi, 2)],
            "M3_cap_plus_select": [round(M3_exp, 2), round(M3_hi, 2)],
        },
        "total_pipeline_cost_if_run_fresh_jpy": {  # 参考: Research+その方式のLedger+B3 の実費相当(研究下書きは再利用するので新規費用ではない)
            "M0": round(R + L0 + B3, 2), "M1": round(R + L0 - s3 + B3, 2), "M2": round(R + L2_exp + B3, 2), "M3": round(R + L2_exp - 0.5 * s3 * sel / n_b3 + B3, 2)},
    })

tot = {m: [round(sum(r["new_cost_jpy"][m][0] for r in rows), 2), round(sum(r["new_cost_jpy"][m][1] for r in rows), 2)] for m in rows[0]["new_cost_jpy"]}
# 条件付き統制(Stage 2): B3の生成ばらつき基準(従来方式B3を各記事1回追加) と Ledger run-to-run基準(従来Ledger uncapped再実行、2記事)
ctrl_b3 = round(sum(r["b3_sol_est_jpy"] for r in rows), 2)
ctrl_ledger_two = round(sum(sorted([r["ledger_existing_jpy"] for r in rows])[:2]), 2)
ctrl_ledger_all = round(sum(r["ledger_existing_jpy"] for r in rows), 2)
out = {"jpy": 0, "api_calls": 0, "basis": "manual_substitution", "articles": rows, "totals_new_cost_jpy_exp_hi": tot,
       "stage1_total_exp_hi": [round(sum(v[0] for v in tot.values()), 2), round(sum(v[1] for v in tot.values()), 2)],
       "stage2_conditional_controls_jpy": {"b3_repeat_all5": ctrl_b3, "ledger_uncapped_repeat_cheapest2": ctrl_ledger_two, "ledger_uncapped_repeat_all5": ctrl_ledger_all}}
json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("totals_new_cost_jpy_exp_hi", "stage1_total_exp_hi", "stage2_conditional_controls_jpy")}, ensure_ascii=False))
for r in rows:
    print(r["article"], r["facts_draft"], r["selected"], "L0", r["ledger_existing_jpy"], "B3", r["b3_sol_est_jpy"], r["new_cost_jpy"])
