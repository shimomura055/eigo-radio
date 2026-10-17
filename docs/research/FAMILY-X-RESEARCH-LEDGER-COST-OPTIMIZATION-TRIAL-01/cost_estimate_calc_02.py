"""RLCT 委任_03 費用見積v2の再現script(read-only、API呼出なし、JPY0)。
cost_estimate_01.json(実測単価x想定呼出=manual_substitution)を基に、Opus条件Aレビュー(OF-RLCT-R-04/05/08/12/13/14)を反映。
使い方: python cost_estimate_calc_02.py --pricing <pricing_snapshot.json> --base <cost_estimate_01.json> --out <cost_estimate_02.json>
出力: out(json) と、同名 *_tables.md(表のmarkdown)。実測ではない。
"""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("--pricing"); ap.add_argument("--base"); ap.add_argument("--out")
a = ap.parse_args()
USD_JPY = 160.0
price = json.load(open(a.pricing, encoding="utf-8"))
tbl = {(p["model"], p["meter"]): p["price"] for p in price["prices"]}
base = json.load(open(a.base, encoding="utf-8"))
A = {r["article"]: r for r in base["articles"]}
ORDER = ["coffee_fxpw", "inbound_tourism", "streaming_price", "openai_copyright", "central_bank_mortgage"]
STAGE_1A = ["coffee_fxpw", "inbound_tourism"]
STAGE_1B = ["streaming_price", "openai_copyright", "central_bank_mortgage"]
M0P_STAGE1 = {"coffee_fxpw", "inbound_tourism", "streaming_price"}  # R-04
P_FORCE = {"inbound_tourism": 1.0}  # R-13(b) inbound再選定はほぼ確実(p=1)
# 本日使用済み: 41.6(SJS4 TTS実測31.33+ASR推定10.3) + S3W Phase A 約3(未確定の見込み)
USED_TODAY = 41.6 + 3.0
DAILY_CAP = 1000.0


def jpy(model, it, ot):
    return (it * tbl[(model, "input_tokens")] + ot * tbl[(model, "output_tokens")]) / 1e6 * USD_JPY


def r2(x):
    return round(x, 2)


rows = {}
for k in ORDER:
    r = A[k]
    B3 = r["b3_sol_est_jpy"]; L0 = r["ledger_existing_jpy"]; R = r["research_existing_jpy"]
    sel = r["selected"]; nb = r["facts_b3_visible"]; s3 = r["case1_saving_cap3_exp_jpy"]
    L2e = r["case2_ledger_sel_exp_jpy"]; L2h = r["case2_ledger_sel_hi_jpy"]; resel = r["resel_unit_jpy"]
    p = P_FORCE.get(k, r["p_reselect_exp"])
    m3_led = L2e - 0.5 * s3 * sel / nb
    new = {}
    new["M0"] = [r["new_cost_jpy"]["M0_conventional"][0], r["new_cost_jpy"]["M0_conventional"][1]]
    new["M0b"] = [B3, 1.2 * B3]
    new["M0p"] = [L0, 1.15 * L0]  # 同日・上限なしLedger再検証(Stage 1はM0P_STAGE1の記事のみ。他はStage 2条件付き)
    new["M1"] = list(r["new_cost_jpy"]["M1_cap"])
    new["M2"] = [B3 + L2e + p * resel, r["new_cost_jpy"]["M2_select_then_verify"][1]]
    new["M3"] = [m3_led + p * resel, r["new_cost_jpy"]["M3_cap_plus_select"][1]]
    # 技術retry余裕(R-13a): 期待=50%x(B3 1回+選定Verifier 1回)、上限=100%x(B3 1回+全Fact Ledger Verifier 1回)
    retry = [0.5 * (B3 + L2e), B3 + L0]
    per_call = r["per_call_jpy"]; fixed = r["ledger_fixed_jpy"]
    probe = [2 * (per_call * 3 + fixed * 0.4), 2 * (per_call * 5 + fixed * 0.6)]  # 改変Fact3件x(上限なし/上限付き)の2検証
    m2b3 = [B3, 1.2 * B3]  # M2初回B3の追加1回(R-12)
    prod = {  # 本番換算(R-05): Research実測+Ledger+B3+再選定。共有/再利用分も帰属
        "M0": [R + L0 + B3, R + L0 + B3],
        "M1": [R + L0 - s3 + B3, R + 1.15 * L0 + 1.2 * B3],
        "M2": [R + L2e + B3 + p * resel, R + L2h + 1.2 * B3 + 2 * resel],
        "M3": [R + m3_led + B3 + p * resel, R + L2h + 1.2 * B3 + 2 * resel],
    }
    rows[k] = {"R": R, "L0": L0, "B3": B3, "p_resel_used": p, "resel_unit": resel, "s3": s3, "sel": sel, "n_b3": nb,
               "new": new, "retry": retry, "probe": probe, "m2b3": m2b3, "prod": prod}


def stage_total(arts):
    e = h = 0.0
    for k in arts:
        n = rows[k]["new"]
        for m in ("M0", "M0b", "M1", "M2", "M3"):
            e += n[m][0]; h += n[m][1]
        if k in M0P_STAGE1:
            e += n["M0p"][0]; h += n["M0p"][1]
        e += rows[k]["retry"][0]; h += rows[k]["retry"][1]
    return [e, h]


s1a = stage_total(STAGE_1A); s1b = stage_total(STAGE_1B); s1 = [s1a[0] + s1b[0], s1a[1] + s1b[1]]
s2 = [sum(rows[k]["new"]["M0p"][0] for k in ("openai_copyright", "central_bank_mortgage")),
      sum(rows[k]["new"]["M0p"][1] for k in ("openai_copyright", "central_bank_mortgage"))]
P3 = ("coffee_fxpw", "inbound_tourism", "streaming_price")
probe3 = [sum(rows[k]["probe"][0] for k in P3), sum(rows[k]["probe"][1] for k in P3)]
probe5 = [sum(rows[k]["probe"][0] for k in ORDER), sum(rows[k]["probe"][1] for k in ORDER)]
m2b3_ci = [sum(rows[k]["m2b3"][0] for k in STAGE_1A), sum(rows[k]["m2b3"][1] for k in STAGE_1A)]
# Stage 3 RF比較: Coffee run_fxpw_01 の risk_flag.*.a2 実測token(A3+A4, luna+gemini lite)。2記事x(全台帳+縮小台帳)=4 RF実行。W-1なし
rf_one = (jpy("gpt-6-luna", 6752, 1062) + jpy("gpt-6-luna", 6902, 1352)
          + jpy("gemini-3.5-flash-lite", 6360, 84) + jpy("gemini-3.5-flash-lite", 6480, 4))
rf = [4 * rf_one, 4 * rf_one * 1.5]
opt_all_e = probe3[0] + m2b3_ci[0] + rf[0]
opt_all_h = probe3[1] + m2b3_ci[1] + rf[1]


def day(total_hi):
    return {"used_today": USED_TODAY, "used_plus_total_hi": r2(USED_TODAY + total_hi), "remaining_after": r2(DAILY_CAP - USED_TODAY - total_hi),
            "within_daily_1000": USED_TODAY + total_hi <= DAILY_CAP}


full_e = s1[0] + s2[0] + opt_all_e
full_h = s1[1] + s2[1] + opt_all_h
out = {"jpy": 0, "api_calls": 0, "basis": "manual_substitution(実測単価x想定呼出、cost_estimate_01.jsonを基に改訂)",
       "assumptions_v2": {
           "p_reselect_inbound": 1.0,
           "retry_margin": "期待=50%x(B3 1回+選定Verifier 1回)、上限=100%x(B3 1回+全Fact Ledger Verifier 1回)/記事",
           "M0prime_stage1_articles": sorted(M0P_STAGE1),
           "smoke": "Coffee M2初回(1a冒頭)は本番のM2 runそのもの=追加費用0、失敗時の再実行は技術retry余裕に含む",
           "probe": "改変Fact3件x(上限なし+上限付き)の2検証。検索3回/件(期待)・5回/件(上限)。推奨=Coffee/inbound/streaming 3記事",
           "m2_b3_extra": "Coffee/inboundでM2初回B3を追加1回(sol B3実費換算、上限+20%)",
           "stage3_rf": "Coffee run_fxpw_01 risk_flag.*.a2のtoken実測(A3+A4 luna+gemini flash-lite)x4実行。W-1なし。inboundに既存W-1記事が無ければ約JPY14追加(未計上)",
           "used_today": "41.6(SJS4: TTS実測31.33+ASR推定10.3)+S3W Phase A 約3(未確定の見込み)",
           "proportional_shrink": "選定Factだけ検証した時の呼出数比例縮小は未検証の仮定(R-13c)",
           "gate_1a_to_1b": "上限遵守率の記録が取れている/再選定loopが仕様どおり動作/実測費用÷見積<=1.3/Production・再利用成果物sha不変"},
       "table1_trial_additional_spend": {
           "per_article_per_method_exp_hi": {k: {m: [r2(v[0]), r2(v[1])] for m, v in rows[k]["new"].items()} for k in ORDER},
           "retry_margin_per_article_exp_hi": {k: [r2(rows[k]["retry"][0]), r2(rows[k]["retry"][1])] for k in ORDER},
           "stage1a_coffee_inbound": [r2(s1a[0]), r2(s1a[1])], "stage1b_streaming_openai_central": [r2(s1b[0]), r2(s1b[1])],
           "stage1_required_total": [r2(s1[0]), r2(s1[1])],
           "stage2_conditional_M0prime_openai_central": [r2(s2[0]), r2(s2[1])],
           "optional_fault_injection_probe_3articles": [r2(probe3[0]), r2(probe3[1])],
           "optional_fault_injection_probe_5articles": [r2(probe5[0]), r2(probe5[1])],
           "optional_M2_initial_B3_extra_coffee_inbound": [r2(m2b3_ci[0]), r2(m2b3_ci[1])],
           "optional_stage3_RF_compare_coffee_inbound": [r2(rf[0]), r2(rf[1])], "rf_one_run_jpy": r2(rf_one),
           "optional_total_recommended": [r2(opt_all_e), r2(opt_all_h)],
           "all_in_total_with_stage2_and_optional": [r2(full_e), r2(full_h)]},
       "daily_check": {"stage1_only": day(s1[1]), "stage1_plus_stage2_plus_optional": day(full_h)},
       "rule_7_7": "期待・上限ともJPY100超 -> ユーザー費用承認(#104)なしで有料実行不可",
       "table2_production_equivalent_exp_hi": {k: {m: [r2(v[0]), r2(v[1])] for m, v in rows[k]["prod"].items()} for k in ORDER},
       "saving_formula": "削減率=(M0本番換算-Mx本番換算)/M0本番換算。M0本番換算=Research実測+Ledger実測+B3(sol換算)。共有/再利用分も帰属"}
sv = {}
for k in ORDER:
    pm = rows[k]["prod"]
    sv[k] = {m: round((pm["M0"][0] - pm[m][0]) / pm["M0"][0] * 100, 1) for m in ("M1", "M2", "M3")}
out["table2_saving_pct_exp"] = sv
tot = {m: sum(rows[k]["prod"][m][0] for k in ORDER) for m in ("M0", "M1", "M2", "M3")}
out["table2_totals_exp"] = {m: r2(v) for m, v in tot.items()}
out["table2_totals_saving_pct_exp"] = {m: round((tot["M0"] - tot[m]) / tot["M0"] * 100, 1) for m in ("M1", "M2", "M3")}
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

NM = {"coffee_fxpw": "Coffee fxpw_01", "inbound_tourism": "inbound_tourism", "streaming_price": "streaming_price", "openai_copyright": "openai_copyright", "central_bank_mortgage": "central_bank_mortgage"}
L = ["### 表1a 記事x方式 Trial追加支出(JPY、期待/上限、Stage 1必須分。M0'はCoffee/inbound/streamingのみStage 1)", "",
     "| 記事 | M0(従来B3新規) | M0b | M0' | 案1(M1) | 案2(M2) | 案1+案2(M3) | 技術retry余裕 | 記事計 |", "|---|---|---|---|---|---|---|---|---|"]
for k in ORDER:
    n = rows[k]["new"]
    cells = []
    e = h = 0
    for m in ("M0", "M0b", "M0p", "M1", "M2", "M3"):
        if m == "M0p" and k not in M0P_STAGE1:
            cells.append("(Stage 2条件付き)"); continue
        cells.append("%.1f/%.1f" % (n[m][0], n[m][1])); e += n[m][0]; h += n[m][1]
    e += rows[k]["retry"][0]; h += rows[k]["retry"][1]
    L.append("| %s | %s | %.1f/%.1f | **%.1f/%.1f** |" % (NM[k], " | ".join(cells), rows[k]["retry"][0], rows[k]["retry"][1], e, h))
L += ["", "### 表1b 段階・任意行の合計(JPY、期待/上限)", "", "| 区分 | 期待 | 上限 |", "|---|---|---|",
      "| 1a: Coffee+inbound(Coffee M2 smokeを冒頭に含む) | %.1f | %.1f |" % tuple(s1a),
      "| 1b: streaming→openai→central | %.1f | %.1f |" % tuple(s1b),
      "| **Stage 1 必須合計(1a+1b)** | **%.1f** | **%.1f** |" % tuple(s1),
      "| Stage 2条件付き: openai/central M0'(M1の呼出ログで上限が拘束した場合のみ) | %.1f | %.1f |" % tuple(s2),
      "| 任意A: 故障注入プローブ(Coffee/inbound/streaming 3記事) | %.1f | %.1f |" % tuple(probe3),
      "| (参考)任意A 5記事版 | %.1f | %.1f |" % tuple(probe5),
      "| 任意B: M2初回B3の追加1回(Coffee/inbound) | %.1f | %.1f |" % tuple(m2b3_ci),
      "| 任意C: Stage 3 RF比較(Coffee/inbound x 全台帳/縮小台帳、W-1なし) | %.1f | %.1f |" % tuple(rf),
      "| 任意A+B+C(3記事プローブ) | %.1f | %.1f |" % (opt_all_e, opt_all_h),
      "| 全部入り(必須+Stage 2+任意A+B+C) | %.1f | %.1f |" % (full_e, full_h)]
L += ["", "### 表2 本番換算費用(JPY/記事、期待。Research実測+Ledger+B3+再選定、共有/再利用分も帰属)と削減率", "",
      "| 記事 | 従来M0 | 案1 | 案2 | 案1+案2 | 削減率 案1 | 案2 | 案1+案2 |", "|---|---|---|---|---|---|---|---|"]
for k in ORDER:
    pm = rows[k]["prod"]
    L.append("| %s | %.1f | %.1f | %.1f | %.1f | %.1f%% | %.1f%% | %.1f%% |" % (NM[k], pm["M0"][0], pm["M1"][0], pm["M2"][0], pm["M3"][0], sv[k]["M1"], sv[k]["M2"], sv[k]["M3"]))
L.append("| **5記事合計** | %.1f | %.1f | %.1f | %.1f | %.1f%% | %.1f%% | %.1f%% |" % (tot["M0"], tot["M1"], tot["M2"], tot["M3"], out["table2_totals_saving_pct_exp"]["M1"], out["table2_totals_saving_pct_exp"]["M2"], out["table2_totals_saving_pct_exp"]["M3"]))
open(a.out.replace(".json", "_tables.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
print(json.dumps({"daily_check": out["daily_check"], "rf_one": rf_one}, ensure_ascii=False))
