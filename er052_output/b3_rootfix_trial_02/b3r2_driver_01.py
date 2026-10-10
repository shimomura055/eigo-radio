# -*- coding: utf-8 -*-
"""B3-FACT-INSTRUCTION-SEPARATION-ROOTFIX-TRIAL-02 driver (DEV/Trial only; not Production).
Phase 1 では --dry-run / selftest / estimate のみ実装。有料API呼び出しコードは Phase 2 で追加する(本ファイルには含めない)。
  python b3r2_driver_01.py dry-run     payload生成(API呼び出しなし)+入力sha+token見積
  python b3r2_driver_01.py selftest    決定論部分(表記抽出/規則導出/検証/タグ挿入)の自己検査
"""
import sys, os, json, glob, argparse, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
T1 = os.path.join(REPO, "er052_output", "b3_fact_instruction_separation_trial_01")
sys.path.insert(0, HERE); sys.path.insert(0, T1); sys.path.insert(0, REPO)
from b3sep_common_01 import THEMES, PROBLEM5, theme_inputs, sha, wj, wt, rj, rd
import b3r2_rank_01 as RK
import b3r2_sepcall_01 as SEP

MODEL = "gpt-6-luna"
EFFORT = "high"            # vfl01.REASONING_EFFORT(Production B3と同一)。Phase 2で assert する
PRICE = {"gpt-6-luna": (0.10, 0.50), "gpt-6.1-sol": (2.00, 10.00)}   # USD/1M tokens (er006_model_routing_pricing_coverage_test_01 の登録値)
JPY = 160.0


def calib():
    """ROOTFIX-01 の C1 実測: テーマ別 prompt文字数と input_tokens を昇順対応させた chars->token 比(各テーマ2反復=同一値)。"""
    import er019_family_x_storyline_b3_fact_selection_01 as prod
    chars = sorted(len(prod.DEVELOPER_MESSAGE) + len(prod.build_user_prompt(theme_inputs(t)["topic"], theme_inputs(t)["ledger"])) for t in THEMES)
    toks = []
    for f in glob.glob(f"{T1}/runs/_raw_usage/C1_*.jsonl"):
        for l in open(f, encoding="utf-8"):
            toks.append(json.loads(l)["input_tokens"])
    toks = sorted(toks)[::2]          # 18 -> 9 (2反復は同一値)
    ratios = [t / c for t, c in zip(toks, chars)]
    return {"chars": chars, "tokens": toks, "ratio_mean": sum(ratios) / len(ratios), "ratio_min": min(ratios), "ratio_max": max(ratios)}


def cost_jpy(model, tin, tout):
    pi, po = PRICE[model]
    return (tin * pi + tout * po) / 1e6 * JPY


def dry_run():
    import b3r2_b3_dplus_01 as DP
    import er019_family_x_storyline_b3_fact_selection_01 as prod
    out = {"model": MODEL, "effort": EFFORT, "themes": {}}
    c = calib(); out["calibration"] = c; r = c["ratio_mean"]
    # 手順6文言の同一性(D-plusとSeparate-callの比較条件)。A6: 実装としてassertする
    import b3r2_b3_roleonly_01 as RO
    assert SEP.STEP6_RULES in DP.USER_PROMPT_TEMPLATE, "D-plusのPromptにSTEP6_RULESが逐語で含まれない"
    assert SEP.STEP6_RULES in SEP.USER_TEMPLATE, "Separate-callのPromptにSTEP6_RULESが逐語で含まれない"
    assert "number_ranks" not in RO.USER_PROMPT_TEMPLATE and "number_ranks" not in json.dumps(RO.STORYLINE_B3_JSON_SCHEMA), "役割宣言のみ腕にnumber_ranksが混入"
    assert "Fact選択の慎重さの参考" not in DP.USER_PROMPT_TEMPLATE and "Fact選択の慎重さの参考" not in RO.USER_PROMPT_TEMPLATE, "U1: 保守化誘導文が残っている"
    out["step6_rules_sha"] = sha(SEP.STEP6_RULES)
    out["step6_identical_in_dplus_and_sepcall"] = True
    rows = []
    for th in THEMES:
        ti = theme_inputs(th); ev = ti["ev"]
        ids = ev["selected_fact_ids"]
        pay_dp = {"model": MODEL, "reasoning": {"effort": EFFORT},
                  "text": {"format": {"type": "json_schema", **DP.STORYLINE_B3_JSON_SCHEMA}},
                  "input": [{"role": "developer", "content": DP.DEVELOPER_MESSAGE}, {"role": "user", "content": DP.build_user_prompt(ti["topic"], ti["ledger"])}]}
        base_chars = len(prod.DEVELOPER_MESSAGE) + len(prod.build_user_prompt(ti["topic"], ti["ledger"]))
        dp_chars = len(DP.DEVELOPER_MESSAGE) + len(pay_dp["input"][1]["content"])
        pay_sep = SEP.build_payload(ti["topic"], ev["selected_storyline"], ti["ledger"], ids, MODEL, EFFORT)
        sep_chars = len(SEP.DEVELOPER_MESSAGE) + len(pay_sep["input"][1]["content"])
        wj(f"{HERE}/dry_run/dplus/{th}.json", pay_dp)
        wj(f"{HERE}/dry_run/sepcall/{th}_c0ids.json", pay_sep)
        # ledger IDの抽出がshape後でも(元台帳で)一致すること
        id_ok = DP.extract_fact_ids_from_ledger(ti["ledger"]) == prod.extract_fact_ids_from_ledger(DP.shape_ledger_for_b3(ti["ledger"]))
        rows.append({"theme": th, "problem": th in PROBLEM5, "base_prompt_chars": base_chars, "dplus_prompt_chars": dp_chars, "dplus_added_chars": dp_chars - base_chars,
                     "base_in_tokens_est": round(base_chars * r), "dplus_in_tokens_est": round(dp_chars * r),
                     "sep_prompt_chars": sep_chars, "sep_in_tokens_est": round(sep_chars * r), "n_selected_c0": len(ids),
                     "id_extraction_ok_after_shape": id_ok, "ledger_sha256": sha(ti["ledger"]), "topic_sha256": sha(ti["topic"]),
                     "dplus_user_prompt_sha256": sha(pay_dp["input"][1]["content"]), "sep_user_prompt_sha256": sha(pay_sep["input"][1]["content"])})
    out["themes"] = rows
    out["all_id_extraction_ok"] = all(x["id_extraction_ok_after_shape"] for x in rows)
    wj(f"{HERE}/dry_run/dry_run_summary_01.json", out)
    print(json.dumps({k: out[k] for k in ("model", "effort", "all_id_extraction_ok")}, ensure_ascii=False))
    for x in rows:
        print(x["theme"], "base", x["base_prompt_chars"], "dplus", x["dplus_prompt_chars"], "(+%d)" % x["dplus_added_chars"], "sep", x["sep_prompt_chars"], "tok_est dplus/sep", x["dplus_in_tokens_est"], x["sep_in_tokens_est"])
    print("calibration ratio mean/min/max", round(c["ratio_mean"], 3), round(c["ratio_min"], 3), round(c["ratio_max"], 3))


def estimate():
    """推測値(=見積)。入力tokenは dry-run の実prompt長×実測比、出力tokenは仮定(low/mid/high)。単価は登録値。"""
    s = rj(f"{HERE}/dry_run/dry_run_summary_01.json")
    th = s["themes"]
    avg_dp_in = sum(x["dplus_in_tokens_est"] for x in th) / len(th)
    avg_sep_in = sum(x["sep_in_tokens_est"] for x in th) / len(th)
    avg_base_in = sum(x["base_in_tokens_est"] for x in th) / len(th)
    # ROOTFIX-01 実測: C1 平均 in 3642 / out 4955 (reasoning 3295)、A' out 5058。¥0.455/call
    base_out = 4955
    scen = {"low": dict(dp_extra_out=400, sep_out=800), "mid": dict(dp_extra_out=1500, sep_out=2000), "high": dict(dp_extra_out=3000, sep_out=4500)}
    est = {"basis": {"price_usd_per_M": PRICE, "usd_jpy": JPY, "measured_C1_b3_jpy_mean": 0.455, "measured_Aprime_b3_jpy_mean": 0.464,
                     "avg_dplus_in_tokens_est": round(avg_dp_in), "avg_sep_in_tokens_est": round(avg_sep_in), "avg_base_in_tokens_est": round(avg_base_in),
                     "assumptions": "出力tokenは仮定(low/mid/high)。D-plusの追加出力=number_ranks JSON(約45tok/数値x7-15個)+規則適用の追加reasoning。Separate-callはFact抜粋のみ入力・reasoning少なめ想定。いずれも見積であり実測ではない"}, "scenarios": {}}
    for k, v in scen.items():
        dp = cost_jpy(MODEL, avg_dp_in, base_out + v["dp_extra_out"])
        sep_l = cost_jpy("gpt-6-luna", avg_sep_in, v["sep_out"])
        sep_s = cost_jpy("gpt-6.1-sol", avg_sep_in, v["sep_out"])
        est["scenarios"][k] = {"dplus_b3_per_call_jpy": round(dp, 3), "dplus_18_calls_jpy": round(dp * 18, 2),
                               "sepcall_luna_per_article_jpy": round(sep_l, 3), "sepcall_luna_18_calls_jpy": round(sep_l * 18, 2),
                               "sepcall_sol_per_article_jpy": round(sep_s, 2), "sepcall_sol_6_calls_jpy": round(sep_s * 6, 2),
                               "sepcall_sol_18_calls_jpy": round(sep_s * 18, 2)}
    r0_meas, r0_hi = 0.45, 1.24
    est["r0_e9"] = {"measured_ROOTFIX01_R0_luna_per_call_jpy": r0_meas, "conservative_per_call_jpy": r0_hi, "calls_6_themes_x1": 6, "calls_6_themes_x2arms": 12,
                    "6_calls_jpy": [round(6 * r0_meas, 2), round(6 * r0_hi, 2)], "12_calls_jpy": [round(12 * r0_meas, 2), round(12 * r0_hi, 2)]}
    lo = est["scenarios"]["low"]; mid = est["scenarios"]["mid"]; hi = est["scenarios"]["high"]
    est["totals_jpy_default_plan"] = {
        "plan": "D-plus 18 call + Separate-call(Luna) 18 call + E9 R0 12 call(D-plus 6 + 対照6)",
        "low": round(lo["dplus_18_calls_jpy"] + lo["sepcall_luna_18_calls_jpy"] + 12 * r0_meas, 1),
        "mid": round(mid["dplus_18_calls_jpy"] + mid["sepcall_luna_18_calls_jpy"] + 12 * 0.8, 1),
        "high": round(hi["dplus_18_calls_jpy"] + hi["sepcall_luna_18_calls_jpy"] + 12 * r0_hi, 1)}
    est["totals_jpy_with_optional"] = {
        "optional": "D-plus-min 18 call + Separate-call Sol 6 call(Luna不成立時のみ)",
        "low": round(est["totals_jpy_default_plan"]["low"] + lo["dplus_18_calls_jpy"] + lo["sepcall_sol_6_calls_jpy"], 1),
        "mid": round(est["totals_jpy_default_plan"]["mid"] + mid["dplus_18_calls_jpy"] + mid["sepcall_sol_6_calls_jpy"], 1),
        "high": round(est["totals_jpy_default_plan"]["high"] + hi["dplus_18_calls_jpy"] + hi["sepcall_sol_6_calls_jpy"], 1)}
    wj(f"{HERE}/ESTIMATE_01.json", est)
    print(json.dumps(est, ensure_ascii=False, indent=1))


def selftest():
    res = {}
    # 1) 表記抽出の基本
    cases = {"20％の償還": ["20%"], "7月13日午前10時16分に": ["7月13日午前10時16分"], "約3.4％上昇、2,300件超": ["約3.4%", "2,300件超"],
             "3.75～4.00％": ["3.75~4.00%"], "第137回理事会": ["第137回"], "2026年9月": ["2026年9月"], "約200万バレル": ["約200万バレル"]}
    ok = {k: RK.extract_surfaces(k) for k in cases}
    res["extract"] = {k: {"got": ok[k], "want": v, "pass": ok[k] == v} for k, v in cases.items()}
    # 2) 規則導出: 全9テーマで例外なく動く+Storyline優先/上限
    der_summary = {}
    for th in THEMES:
        ti = theme_inputs(th); ev = ti["ev"]
        d = RK.derive_ranks(ti["ledger"], ev["selected_fact_ids"], ev["selected_storyline"])
        der_summary[th] = {"concepts": d["n_concepts"], "cap": d["cap"], "core": sum(i["role"] == "core" for i in d["items"]), "items": len(d["items"])}
    res["derive_9themes"] = der_summary
    # 3) validate_number_ranks: 合成ケース(hormuz C0 ids)
    ti = theme_inputs("hormuz"); ev = ti["ev"]; ids = ev["selected_fact_ids"]; st = ev["selected_storyline"]
    d = RK.derive_ranks(ti["ledger"], ids, st)
    good = [{"fact_id": i["fact_id"], "surface": i["surface"], "kind": i["kind"], "role": i["role"]} for i in d["items"]]
    t = {}
    t["good"] = RK.validate_number_ranks(good, ti["ledger"], ids, st)
    t["unknown_fact"] = RK.validate_number_ranks(good + [{"fact_id": "ZZ-9", "surface": "1%", "kind": "magnitude", "role": "core"}], ti["ledger"], ids, st)
    t["not_selected"] = RK.validate_number_ranks(good + [{"fact_id": "HF-001", "surface": "第137回", "kind": "ordinal", "role": "peripheral"}], ti["ledger"], ids, st)
    t["invented_number"] = RK.validate_number_ranks(good + [{"fact_id": ids[0], "surface": "99.9％", "kind": "magnitude", "role": "core"}], ti["ledger"], ids, st)
    t["swapped_fact"] = RK.validate_number_ranks([dict(good[0], fact_id=ids[-1])] + good[1:], ti["ledger"], ids, st)
    t["missing_one"] = RK.validate_number_ranks(good[1:], ti["ledger"], ids, st)
    t["role_flip"] = RK.validate_number_ranks([dict(good[0], role=("peripheral" if good[0]["role"] == "core" else "core"))] + good[1:], ti["ledger"], ids, st)
    t["dup"] = RK.validate_number_ranks(good + [good[0]], ti["ledger"], ids, st)
    t["no_core"] = RK.validate_number_ranks([dict(g, role="peripheral") for g in good], ti["ledger"], ids, st)
    res["validate"] = {k: {"errors": len(v["errors"]), "flags": [f[:70] for f in v["flags"]], "err_head": [e[:60] for e in v["errors"][:2]]} for k, v in t.items()}
    expect = {"good": (0, False), "unknown_fact": (1, None), "not_selected": (1, None), "invented_number": (1, None), "swapped_fact": (None, None), "missing_one": (0, None), "role_flip": (0, None), "dup": (1, None), "no_core": (0, None)}
    chk = {"good_no_errors": t["good"]["errors"] == [], "unknown_detected": any("UNKNOWN_FACT_ID" in e for e in t["unknown_fact"]["errors"]),
           "not_selected_detected": any("FACT_NOT_SELECTED" in e for e in t["not_selected"]["errors"]),
           "invented_detected": any("SURFACE_NOT_IN_FACT" in e for e in t["invented_number"]["errors"]),
           "swapped_detected_as_error_or_missing": bool(t["swapped_fact"]["errors"]) or any("MISSING" in f for f in t["swapped_fact"]["flags"]),
           "missing_flagged": any("MISSING_SURFACES" in f for f in t["missing_one"]["flags"]),
           "role_flip_flagged": any("ROLE_DISAGREES" in f for f in t["role_flip"]["flags"]),
           "dup_detected": any("DUPLICATE" in e for e in t["dup"]["errors"]),
           "no_core_flagged": any(f == "NO_CORE" for f in t["no_core"]["flags"])}
    res["validate_checks"] = chk
    # 4) タグ挿入: 本文非改変 + 二重付与なし + 元に戻る
    ins = {}
    for th in THEMES:
        ti = theme_inputs(th); ev = ti["ev"]
        import b3sep_build_01 as B1
        d = RK.derive_ranks(ti["ledger"], ev["selected_fact_ids"], ev["selected_storyline"])
        a = B1.assemble_D(ti["ledger"], ev["selected_fact_ids"], ev["selected_storyline"], "Dmin")
        marked = []
        for n, fid in enumerate(a["ordered_ids"], 1):
            line = a["facts_text"].split("\n")[n - 1]
            marked.append(RK.insert_marks(line, [i for i in d["items"] if i["fact_id"] == fid]))
        mt = "\n".join(marked)
        ins[th] = {"roundtrip_equal": RK.strip_marks(mt) == "\n".join(a["facts_text"].split("\n")[:len(marked)]), "marks_core": mt.count(RK.MARK["core"]), "marks_periph": mt.count(RK.MARK["peripheral"]),
                   "double_marks": len(re.findall(r"】【", mt))}
    res["insert_marks"] = ins
    # 5) 委任_02 是正 A1/A2/A3 の検査
    A = {}
    mk = lambda t, sf, role="core": RK.insert_marks(t, [{"surface": sf, "role": role}])
    A["A1_pos_1.5%と5%"] = (mk("1.5%と5%", "5%"), "1.5%と5%【中核数値】")
    A["A1_pos_13日と3日"] = (mk("13日と3日", "3日"), "13日と3日【中核数値】")
    A["A1_pos_19月と9月"] = (mk("19月と9月", "9月"), "19月と9月【中核数値】")
    A["A1_pos_2,300件と300"] = (mk("2,300件と300", "300"), "2,300件と300【中核数値】")
    A["A1_pos_5.5と5"] = (mk("5.5と5", "5"), "5.5と5【中核数値】")
    A["A1_pos_全角NFKC"] = (mk("売上は１２％増", "12%"), "売上は１２％【中核数値】増")
    A["A1_contains_1.5%に5%は無い"] = (RK.contains("1.5%", "5%"), False)
    A["A1_contains_13日に3日は無い"] = (RK.contains("13日", "3日"), False)
    A["A1_contains_正常"] = (RK.contains("3.4%上昇", "3.4%"), True)
    ext = {"9月に": ["9月"], "第2四半期の売上": ["第2四半期"], "2026年第3四半期": ["2026年第3四半期"], "午前10時16分に": ["午前10時16分"], "1万5000円": ["1万5000円"],
           "三千人と数百件": [], "翌14日の": ["14日"], "3日間": ["3日間"], "3時間": ["3時間"], "1日あたり200万バレル": ["200万バレル"], "$78.00": ["$78.00"], "7月13日": ["7月13日"], "2億5,000万ドル": ["2億5,000万ドル"], "2026-10-08に": ["2026-10-08"], "事件番号は1:26-cv-08892": ["1:26-cv-08892"]}
    for k, v in ext.items():
        A["A2_extract_" + k] = (RK.extract_surfaces(k), v)
    A["A2_compound_main"] = (RK.main_numbers("1万5000円", "magnitude"), ("M", "15000"))
    A["A2_compound_main_oku"] = (RK.main_numbers("2億5,000万ドル", "magnitude"), ("M", "250000000"))
    A["A2_iso_kind"] = (RK.surface_kind("2026-10-08"), "date_time")
    A["A2_docket_kind"] = (RK.surface_kind("1:26-cv-08892"), "name_embedded")
    led_nonv = ("[VERIFIED] T-1: 売上は約3.4％増の120億円だった。" + chr(10) + "  scope: 全社" + chr(10) +
                "[VERIFIED] T-2: 利益は20％減った。" + chr(10) + "  scope: 全社" + chr(10))
    d1 = RK.derive_ranks(led_nonv, ["T-1", "T-2"], "")
    A["A3_alt_numeric_all_eligible"] = (sorted({i["surface"]: i["eligible"] for i in d1["items"]}.items()), sorted({"約3.4%": True, "120億円": True, "20%": True}.items()))
    led_mix = ("[VERIFIED] T-1: 売上は約3.4％増の120億円だった。" + chr(10) + "  numeric_value: 120億円" + chr(10) +
               "[VERIFIED] T-2: 利益は20％減った。" + chr(10) + "  scope: 全社" + chr(10))
    d2 = RK.derive_ranks(led_mix, ["T-1", "T-2"], "")
    A["A3_no_alt_when_field_exists_elsewhere"] = ({i["surface"]: i["eligible"] for i in d2["items"]}, {"約3.4%": False, "120億円": True, "20%": False})
    led_same = ("[VERIFIED] T-1: 利益は20％減った。" + chr(10) + "  numeric_value: 20％" + chr(10) +
                "[VERIFIED] T-2: 税率は20％だった。" + chr(10) + "  numeric_value: 20％" + chr(10))
    d3 = RK.derive_ranks(led_same, ["T-1", "T-2"], "")
    A["A3_item_key_has_fact_id"] = (len({i["ikey"] for i in d3["items"]}), 2)
    A["A3_same_surface_merged_concept"] = (len({i["concept"] for i in d3["items"]}), 1)
    led_unit = ("[VERIFIED] T-1: 20％の人が20件を見た。" + chr(10) + "  numeric_value: 20％、20件" + chr(10))
    d5 = RK.derive_ranks(led_unit, ["T-1"], "")
    A["A3_unit_splits_concepts"] = (len({i["concept"] for i in d5["items"]}), 2)
    led_date = ("[VERIFIED] T-1: 7月13日に発表され、9月には開始する。" + chr(10) + "  date_or_period: 2026-07-13" + chr(10))
    d4 = RK.derive_ranks(led_date, ["T-1"], "")
    A["A3_date_eligibility"] = ({i["surface"]: i["eligible"] for i in d4["items"]}, {"7月13日": True, "9月": False})
    res["A_checks"] = {k: {"got": str(v[0]), "want": str(v[1]), "pass": v[0] == v[1]} for k, v in A.items()}
    allA = all(v["pass"] for v in res["A_checks"].values())
    allpass = allA and all(v["pass"] for v in res["extract"].values()) and all(chk.values()) and all(v["roundtrip_equal"] and v["double_marks"] == 0 for v in ins.values())
    res["ALL_PASS"] = allpass
    wj(f"{HERE}/selftest_result_01.json", res)
    print(json.dumps({"extract_pass": {k: v["pass"] for k, v in res["extract"].items()}, "validate_checks": chk, "insert_marks_ok": {k: (v["roundtrip_equal"], v["double_marks"]) for k, v in ins.items()}, "ALL_PASS": allpass}, ensure_ascii=False, indent=1))


# ======================================================================
# 委任_02 Phase 2a: 有料サブコマンド (b3-dplus / b3-roleonly / sep) と frozen。技術retryのみ(結果を見た再実行禁止)。
# 台帳・topic・C0採用IDはROOTFIX-01と同一の凍結入力(shaを検証)。Production B3はimportのみ(不変)。
# ======================================================================
import time, hashlib, importlib
CAP = 60.0                       # 本線(D-plus 18 + Sep 18 + 役割宣言のみ 18)累計JPY。Sol条件付きは別途累計JPY100内
CAP_SOL_TOTAL = 100.0
LEDGER_COST = f"{HERE}/cost_ledger_b3r2_01.jsonl"
FROZEN = f"{HERE}/frozen_b3r2_02.json"
EST_PER_CALL = {"b3-dplus": 0.8, "b3-roleonly": 0.7, "sep": 0.5, "sep-sol": 8.0}   # guard用の1回上限見積(JPY、高位)
RETRY_NOTE = ("\n\n【前回出力の修正指示】前回の出力は技術的に無効でした(JSON不正、またはFactに存在しないfact_id・表記を含んでいました)。"
              "採用Factに実在するfact_idと表記のみを使い、指定のJSON schemaに厳密に従って再出力してください。")


class Stop(RuntimeError):
    pass


def spent():
    if not os.path.exists(LEDGER_COST):
        return 0.0, 0.0
    tot = sol = 0.0
    for l in open(LEDGER_COST, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            tot += r["jpy"]
            if "sol" in r.get("model", ""):
                sol += r["jpy"]
    return tot, sol


def guard(est, sol=False):
    tot, solspent = spent()
    cap = CAP_SOL_TOTAL if sol else CAP
    if tot + est > cap:
        raise Stop(f"[STOP] cap: spent={tot:.2f} + est={est} > {cap}")
    return tot


def _module_shas():
    import er019_family_x_storyline_b3_fact_selection_01 as prod
    out = {"prod_b3": sha(open(prod.__file__, encoding="utf-8", newline="").read().replace("\r\n", "\n"))}
    for f in ("b3r2_b3_dplus_01.py", "b3r2_b3_roleonly_01.py", "b3r2_sepcall_01.py", "b3r2_rank_01.py"):
        out[f] = sha(open(f"{HERE}/{f}", encoding="utf-8", newline="").read().replace("\r\n", "\n"))
    out["step6_rules"] = sha(SEP.STEP6_RULES)
    return out


def _prereg_sha():
    return sha(open(f"{HERE}/PREREGISTRATION_02.md", encoding="utf-8", newline="").read().replace("\r\n", "\n"))


def cmd_frozen(a=None):
    """事前登録(PREREGISTRATION_02.md)確定後に1回だけ実行。入力・module・事前登録のshaを記録(以後の変更検知)。"""
    out = {"_prereg_sha256": _prereg_sha(), "_modules": _module_shas(), "themes": {}}
    for th in THEMES:
        ti = theme_inputs(th)
        out["themes"][th] = {"ledger_sha256": sha(ti["ledger"]), "topic_sha256": sha(ti["topic"]), "c0_selected_fact_ids": ti["ev"]["selected_fact_ids"],
                             "c0_storyline_sha256": sha(ti["ev"]["selected_storyline"])}
    wj(FROZEN, out)
    print("frozen written", out["_prereg_sha256"][:12], json.dumps(out["_modules"], ensure_ascii=False)[:200])


def _verify_frozen(theme):
    fz = rj(FROZEN)
    cur = _module_shas()
    for k, v in fz["_modules"].items():
        if cur[k] != v:
            raise Stop(f"[STOP] frozen module changed: {k}")
    if _prereg_sha() != fz["_prereg_sha256"]:
        raise Stop("[STOP] PREREGISTRATION_02 changed after freeze")
    ti = theme_inputs(theme)
    if sha(ti["ledger"]) != fz["themes"][theme]["ledger_sha256"] or sha(ti["topic"]) != fz["themes"][theme]["topic_sha256"]:
        raise Stop(f"[STOP] frozen input sha mismatch {theme}")
    return fz, ti


def _row_cost_jpy(rec):
    if rec.get("provider") != "openai":
        return 0.0
    m = rec.get("model_id") or rec.get("model") or ""
    key = "gpt-6.1-sol" if m.startswith("gpt-6.1-sol") else ("gpt-6-luna" if m.startswith("gpt-6-luna") else None)
    if key is None:
        raise Stop(f"[STOP] 単価未登録model: {m}")
    return cost_jpy(key, rec.get("input_tokens") or 0, rec.get("output_tokens") or 0)


def _cost_since(path, start):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()][start:]
    return sum(_row_cost_jpy(r) for r in rows), rows, start + len(rows)


def _append_cost(rec):
    with open(LEDGER_COST, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + chr(10))


def _client_setup(tag):
    import er003_v1_en_direct_vfl_01_generate as vfl01
    import er005_cost_logger as cl
    assert vfl01.MODEL == MODEL, vfl01.MODEL
    assert vfl01.REASONING_EFFORT == EFFORT, vfl01.REASONING_EFFORT
    rawp = f"{HERE}/runs/_raw_usage/{tag}_{os.getpid()}.jsonl"
    os.makedirs(os.path.dirname(rawp), exist_ok=True)
    cl.install(rawp)
    return vfl01, cl, rawp, vfl01.get_client()


def _usage(rows):
    return [{k: r.get(k) for k in ("input_tokens", "output_tokens", "reasoning_tokens", "elapsed_seconds", "attempt_number")} for r in rows]


def cmd_b3(a):
    """D-plus-single-call / 役割宣言のみ腕。Trialコピーの run_storyline_b3_selection(Productionのretry機構そのまま)を使う。"""
    arm = "D-plus" if a.cmd == "b3-dplus" else "RoleOnly"
    mod = importlib.import_module("b3r2_b3_dplus_01" if a.cmd == "b3-dplus" else "b3r2_b3_roleonly_01")
    vfl01, cl, rawp, client = _client_setup(arm)
    cur = 0
    for th in a.themes.split(","):
        fz, ti = _verify_frozen(th)
        for rep in [int(x) for x in a.reps.split(",")]:
            od = f"{HERE}/runs/{arm}/{th}/rep{rep}"
            if os.path.exists(f"{od}/selection.json") or os.path.exists(f"{od}/selection_failed.json"):
                print("skip(existing)", od)
                continue
            s0 = guard(EST_PER_CALL[a.cmd])
            t0 = time.time()
            try:
                sel = mod.run_storyline_b3_selection(client, ti["topic"], ti["ledger"], model=vfl01.MODEL, effort=vfl01.REASONING_EFFORT)
            except RuntimeError as ex:
                jpy, rows, cur = _cost_since(rawp, cur)
                wj(f"{od}/selection_failed.json", {"arm": arm, "theme": th, "rep": rep, "error": str(ex)[:600], "attempts_log": getattr(ex, "attempts_log", None),
                                                   "latency_seconds": round(time.time() - t0, 1), "usage_rows": _usage(rows)})
                _append_cost({"arm": arm, "theme": th, "rep": rep, "kind": "b3_stop", "jpy": round(jpy, 4), "n_api_rows": len(rows), "model": MODEL,
                              "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
                print("STOP-recorded", arm, th, rep, flush=True)
                continue
            jpy, rows, cur = _cost_since(rawp, cur)
            if not str(sel["model"]).startswith(MODEL):
                raise Stop(f"[STOP] model mismatch {sel['model']}")
            wj(f"{od}/selection.json", {"arm": arm, "theme": th, "rep": rep, "parsed": sel["parsed"], "model": sel["model"], "response_id": sel["response_id"],
                                        "latency_seconds": sel["latency_seconds"], "attempts": sel["attempts"], "retried": sel["retried"],
                                        "soft_warnings": sel["soft_warnings"], "prompt_shas": sel["prompt_shas"], "ledger_sha256": sha(ti["ledger"]),
                                        "attempts_log": sel["attempts_log"], "usage_rows": _usage(rows)})
            wt(f"{od}/selected_brief_raw.md", mod.build_selected_brief_markdown(sel))
            rec = {"arm": arm, "theme": th, "rep": rep, "kind": "b3", "jpy": round(jpy, 4), "n_api_rows": len(rows), "attempts": sel["attempts"],
                   "latency_seconds": round(sel["latency_seconds"], 1), "model": sel["model"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            _append_cost(rec)
            print("done", arm, th, rep, rec["jpy"], "attempts", sel["attempts"], "lat", rec["latency_seconds"], flush=True)


def cmd_sep(a):
    """Separate-call: C0の採用ID+C0 Storylineを入力に数値ランクだけを別callで出す。同一入力でrep1/rep2=純粋な再現性。"""
    model = a.model
    assert model in PRICE, model
    sol = model == "gpt-6.1-sol"
    arm = "Sep" if not sol else "SepSol"
    vfl01, cl, rawp, client = _client_setup(arm)
    cur = 0
    for th in a.themes.split(","):
        fz, ti = _verify_frozen(th)
        ev = ti["ev"]
        ids = ev["selected_fact_ids"]
        story = ev["selected_storyline"]
        for rep in [int(x) for x in a.reps.split(",")]:
            od = f"{HERE}/runs/{arm}/{th}/rep{rep}"
            if os.path.exists(f"{od}/selection.json") or os.path.exists(f"{od}/selection_failed.json"):
                print("skip(existing)", od)
                continue
            s0 = guard(EST_PER_CALL["sep-sol" if sol else "sep"], sol=sol)
            attempts_log, result, payload = [], None, None
            t0 = time.time()
            for attempt in (1, 2):
                payload = SEP.build_payload(ti["topic"], story, ti["ledger"], ids, model, EFFORT)
                if attempt == 2:
                    payload["input"][1]["content"] += RETRY_NOTE
                t1 = time.time()
                try:
                    with cl.logging_context("B3R2_SEP_TRIAL_02", "number_ranks"):
                        resp = client.responses.create(**payload)
                    parsed = json.loads(resp.output_text)
                except Exception as exc:   # noqa: BLE001
                    attempts_log.append({"attempt": attempt, "error": str(exc)[:400]})
                    continue
                v = SEP.validate(parsed, ti["ledger"], ids, story)
                attempts_log.append({"attempt": attempt, "validation_errors": v["errors"], "flags": v["flags"], "latency_seconds": round(time.time() - t1, 1), "model": resp.model})
                if not str(resp.model).startswith(model):
                    raise Stop(f"[STOP] model mismatch {resp.model}")
                if not v["errors"]:
                    result = {"parsed": parsed, "model": resp.model, "response_id": resp.id, "attempts": attempt, "flags": v["flags"]}
                    break
            lat = time.time() - t0
            jpy, rows, cur = _cost_since(rawp, cur)
            if result is None:
                wj(f"{od}/selection_failed.json", {"arm": arm, "theme": th, "rep": rep, "attempts_log": attempts_log, "latency_seconds": round(lat, 1), "usage_rows": _usage(rows)})
                _append_cost({"arm": arm, "theme": th, "rep": rep, "kind": "sep_stop", "jpy": round(jpy, 4), "n_api_rows": len(rows), "model": model, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
                print("STOP-recorded", arm, th, rep, flush=True)
                continue
            wj(f"{od}/selection.json", {"arm": arm, "theme": th, "rep": rep, "input_c0_ids": ids, "parsed": result["parsed"], "model": result["model"], "response_id": result["response_id"],
                                        "attempts": result["attempts"], "flags": result["flags"], "latency_seconds": round(lat, 1), "attempts_log": attempts_log,
                                        "payload_sha256": sha(json.dumps(payload, ensure_ascii=False, sort_keys=True)), "usage_rows": _usage(rows)})
            rec = {"arm": arm, "theme": th, "rep": rep, "kind": "sep", "jpy": round(jpy, 4), "n_api_rows": len(rows), "attempts": result["attempts"],
                   "latency_seconds": round(lat, 1), "model": result["model"], "ts": time.strftime("%Y-%m-%dT%H:%M:%S")}
            _append_cost(rec)
            print("done", arm, th, rep, rec["jpy"], "attempts", result["attempts"], "lat", rec["latency_seconds"], flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd")
    for c in ("dry-run", "estimate", "selftest", "frozen"):
        sp.add_parser(c)
    for c in ("b3-dplus", "b3-roleonly"):
        b = sp.add_parser(c)
        b.add_argument("--themes", required=True)
        b.add_argument("--reps", default="1,2")
    b = sp.add_parser("sep")
    b.add_argument("--themes", required=True)
    b.add_argument("--reps", default="1,2")
    b.add_argument("--model", default="gpt-6-luna")
    a = ap.parse_args()
    try:
        {"dry-run": lambda a: dry_run(), "estimate": lambda a: estimate(), "selftest": lambda a: selftest(), "frozen": cmd_frozen,
         "b3-dplus": cmd_b3, "b3-roleonly": cmd_b3, "sep": cmd_sep}[a.cmd](a)
    except Stop as ex:
        print(ex)
        sys.exit(46)
