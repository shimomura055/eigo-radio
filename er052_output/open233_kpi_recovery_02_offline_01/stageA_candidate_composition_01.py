# -*- coding: utf-8 -*-
# stageA_candidate_composition_01.py  (OPEN-233-STAGE1-CHECKER-RECOVERY-AND-PM-RCA-01 委任_09、完全に¥0・APIなし)
# 段階A(er052_output/open233_stage1_stageA_01)の保存出力と rep30 の保存出力だけを読む。コード/Prompt/gold/fixtureは変更しない。
# 出力: stageA_candidate_composition_01.json / .md(同ディレクトリ)
import glob
import json
import os
import re
import statistics as st
from collections import Counter, defaultdict

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
import er052_open233_stage1_stageA_01 as sa

OUT = "er052_output/open233_kpi_recovery_02_offline_01"
RUNS = "er052_output/open233_stage1_stageA_01/runs"
REP30 = "er052_output/open233_self_recovery_flow_runner_01_rep30"
REP24_MEAN, REP30_MEAN_RECORDED = 0.4401, 0.5733  # rep30 summary_kpi_01.json の cost.rep24_mean_per_run / rep29_mean_per_run
FIT_A, FIT_B = 0.099, 0.073  # Stage 2費用 ≒ A + B x 候補数 (stage1_redesign_offline_eval_01.md、n=30、候補範囲[0,10])

GROUPS = {"SC": sa.SC_IDS, "B2watch": sa.WATCH_IDS, "NORMAL": sa.NORMAL_IDS, "holdout": sa.HOLDOUT_IDS}
GROUP_OF = {i: g for g, ids in GROUPS.items() for i in ids}

# ---- 作業2: NORMAL 6 instance(s1)の先頭5候補の目視相当ラベル(推測。gold変更ではない) ----
# R=本当に逸脱(Ledger範囲超え・範囲拡張、軽微含む) / N=自然な推論・言い換え(問題なし) / U=Checkerが迷って候補にしただけ(導入・修辞・見出し・評価語など、事実主張が薄い)
SAMPLE_LABELS = {
    "neg1_meta_b3prod_a2": {"T": "U", "S1.1": "U", "S1.2": "U", "S1.3": "R", "S1.4": "N"},
    "neg2_meta_refresh_a2": {"S1.1": "U", "S1.4": "N", "S2.4": "U", "S3.1": "N", "S3.2": "N"},
    "neg3_hormuz_prodrunner_b1b": {"T": "U", "S1.1": "U", "S2.1": "N", "S2.2": "U", "H2": "U"},
    "neg4_smallbag_div_a2": {"T": "U", "S1.2": "U", "S1.3": "U", "S2.1": "R", "S2.2": "R"},
    "neg6_smallbag_div_b1b": {"T": "U", "S1.1": "N", "S1.2": "U", "S1.3": "U", "S2.1": "R"},
    "neg7_meta_prodrunner_b1b": {"T": "U", "S1.4": "U", "S2.2": "U", "S2.3": "U", "H1": "U"},
}


def load_runs():
    out = []
    for p in sorted(glob.glob(f"{RUNS}/s*/*.json")):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def source_of(c):
    sr, rt = set(c["sub_reasons"]), set(c["routes"])
    if "unknown_unit_id" in sr:
        return "orphan(unknown_unit_id)"
    if "coverage_gap" in sr:
        return "coverage_gap"
    if "model" in sr:
        return "LLM_both(r3+r5)" if rt == {"r3", "r5"} else ("LLM_r3only" if rt == {"r3"} else "LLM_r5only")
    return "deterministic_only"


def classify_negation(unit, fact_line):
    """negation_polarity_mismatch 発火1件の分類(ルール化。70 unique件を目視で確認済み。推測を含む)。"""
    en = [m.group(0).lower() for m in cov.NEGATION_EN_RE.finditer(unit)]
    ja = [m for m in cov.NEGATION_MARKERS_JA if m in fact_line]
    if not en and ja:  # 単位は肯定、factのclaim行に日本語否定語
        if "ほどなく" in fact_line and set(ja) <= {"なく"}:
            return "FP:字面(「ほどなく」の『なく』)"
        if "ではなく" in fact_line:
            return "FP:対比構文(「AIではなく人間が」。単位は肯定側を述べており矛盾なし)"
        if "意図せず" in fact_line:
            return "FP:修飾語(「意図せず共有」の『せず』。極性反転なし)"
        if "示されなかった" in fact_line:
            return "FP:情報欠如の言い換え(単位はonly等で同義。極性反転なし)"
        if "好まない" in fact_line:
            return "FP:英語動詞(disliked)で否定を表現、否定語リストに無い"
        return "UNCLASSIFIED(単位肯定/fact否定語)"
    if en and not ja:  # 単位に英語否定語、factのclaim行に日本語否定語なし
        if "not only" in unit.lower():
            return "FP:慣用句(not only A but also B)は否定ではない"
        if "なしに" in fact_line:
            return "FP:マーカー欠落(日本語『なし(に)』が否定語リストに無い。withoutと整合)"
        if re.match(r"^\[VERIFIED\] [A-Za-z]\d+:", fact_line) or not re.search(r"[ぁ-ん]", fact_line[:60]):
            return "FP:言語不整合(factが英語Ledgerで日本語否定語しか検査しない構造)"
        if "cannot" in en or "did not" in en:
            return "PLAUSIBLE_TRUE(推測):単位の否定・留保がfactに無い。ただし極性反転ではなく『Ledgerに無い主張/留保』で、第1support factのみでの検査"
        return "UNCLASSIFIED(単位否定語/fact肯定)"
    return "UNCLASSIFIED(その他)"


def main():
    runs = load_runs()
    insts = {i["instance_id"]: i for i in runner.build_target_instances()}
    blocks = {iid: cov.ledger_fact_blocks(insts[iid]["fixture"]["ledger_text"]) for iid in {r["instance_id"] for r in runs}}
    R = {"n_runs": len(runs), "api_failure_runs": sum(1 for r in runs if r["api_failure"])}

    # ---- 作業1: 候補の発生源 ----
    per_group = defaultdict(lambda: defaultdict(list))
    per_inst = defaultdict(lambda: defaultdict(list))
    src_total = Counter()
    flag_cnt, flag_cnt_model = Counter(), Counter()
    issue_len, has_issue, has_rel, has_claim, n_model = [], 0, 0, 0, 0
    route_status = {"r3": Counter(), "r5": Counter()}
    det_reason = Counter()
    for r in runs:
        a = r["audit"]
        g, iid = GROUP_OF[r["instance_id"]], r["instance_id"]
        cs = a["union_candidates"]
        srcs = Counter(source_of(c) for c in cs)
        for k in ("LLM_both(r3+r5)", "LLM_r3only", "LLM_r5only", "deterministic_only", "orphan(unknown_unit_id)", "coverage_gap"):
            per_group[g][k].append(srcs.get(k, 0))
            per_inst[iid][k].append(srcs.get(k, 0))
        per_group[g]["union"].append(len(cs))
        per_group[g]["judged"].append(a["n_judged_units"])
        per_inst[iid]["union"].append(len(cs))
        per_inst[iid]["judged"].append(a["n_judged_units"])
        per_inst[iid]["r3"].append(len(a["per_route"]["r3"]["candidates"]))
        per_inst[iid]["r5"].append(len(a["per_route"]["r5"]["candidates"]))
        per_inst[iid]["cost"].append(r["total_cost_jpy"])
        src_total.update(srcs)
        for rt, pr in a["per_route"].items():
            for s in pr["unit_status"].values():
                route_status[rt][s.split("(")[0] if "(" in s and s.startswith("SUPPORTED->") else s] += 1
                if s.startswith("SUPPORTED->CANDIDATE("):
                    for x in s[s.find("(") + 1:-1].split(","):
                        det_reason[x] += 1
        for c in cs:
            if "model" in c["sub_reasons"]:
                n_model += 1
                for k, v in c["flags"].items():
                    if v:
                        flag_cnt_model[k] += 1
                iss = [x for x in c["issues"] if x and not x.startswith("決定論検査で戻した")]
                has_issue += bool(iss)
                issue_len.extend(len(x) for x in iss)
                has_rel += bool(c["related_fact_ids"])
                has_claim += bool(c["model_claims"])
            for k, v in c["flags"].items():
                if v:
                    flag_cnt[k] += 1
    def m(x):
        return round(sum(x) / len(x), 2) if x else 0
    R["by_group_mean_per_run"] = {g: {k: m(v) for k, v in d.items()} | {"n_runs": len(d["union"]),
                                  "union_over_judged": round(sum(d["union"]) / max(1, sum(d["judged"])), 3)} for g, d in per_group.items()}
    R["by_instance_mean_per_run"] = {i: {k: m(v) for k, v in d.items()} | {"n_runs": len(d["union"])} for i, d in per_inst.items()}
    R["source_total"] = dict(src_total)
    R["route_unit_status_total"] = {k: dict(v) for k, v in route_status.items()}
    tot_j3 = sum(route_status["r3"].values())
    R["r3_supported_share_after_det"] = round(route_status["r3"]["SUPPORTED"] / tot_j3, 3)
    R["r3_supported_share_before_det"] = round((route_status["r3"]["SUPPORTED"] + route_status["r3"]["SUPPORTED->CANDIDATE"]) / tot_j3, 3)
    tot_j5 = sum(route_status["r5"].values())
    R["r5_match_share"] = round(route_status["r5"]["MATCH"] / tot_j5, 3)
    R["r5_unmentioned_share"] = round(route_status["r5"]["UNMENTIONED"] / tot_j5, 3)
    R["det_return_by_reason"] = dict(det_reason)
    R["llm_candidates"] = {"n": n_model, "flag_distribution": dict(flag_cnt_model.most_common()),
                           "issue_present_rate": round(has_issue / n_model, 3), "issue_len_mean": m(issue_len),
                           "related_fact_id_present_rate": round(has_rel / n_model, 3), "claim_in_article_present_rate": round(has_claim / n_model, 3),
                           "only_generic_flags_rate(changed_fact/unsupported_new_claim/changed_scope以外が無い)": None}
    # 汎用フラグのみ(=「Ledgerに無い/範囲が広い」型)の割合
    generic = {"changed_fact", "unsupported_new_claim", "changed_scope"}
    n_gen = n_noflag = 0
    for r in runs:
        for c in r["audit"]["union_candidates"]:
            if "model" in c["sub_reasons"]:
                on = {k for k, v in c["flags"].items() if v}
                n_gen += bool(on) and on <= generic
                n_noflag += not on
    R["llm_candidates"]["only_generic_flags_rate(changed_fact/unsupported_new_claim/changed_scope以外が無い)"] = round(n_gen / n_model, 3)
    R["llm_candidates"]["no_flag_rate"] = round(n_noflag / n_model, 3)

    # ---- 作業2: NORMAL先頭5候補のサンプル(s1) ----
    sample_rows, lab_cnt = [], Counter()
    for iid, labs in SAMPLE_LABELS.items():
        d = json.load(open(f"{RUNS}/s1/{iid}.json", encoding="utf-8"))
        first5 = d["audit"]["union_candidates"][:5]
        assert [c["unit_ids"][0] for c in first5] == list(labs), iid
        for c in first5:
            u = c["unit_ids"][0]
            lab = labs[u]
            lab_cnt[lab] += 1
            sample_rows.append({"instance": iid, "unit": u, "label": lab, "claim": c["claim_text"][:120], "routes": c["routes"],
                                "sub_reasons": c["sub_reasons"], "flags": [k for k, v in c["flags"].items() if v]})
    n_s = sum(lab_cnt.values())
    R["normal_sample"] = {"n": n_s, "labels": dict(lab_cnt), "share": {k: round(v / n_s, 3) for k, v in lab_cnt.items()},
                          "note": "ラベルは推測(目視相当)。gold変更ではない。R=真の逸脱(軽微含む) N=自然な推論・言い換え U=迷って候補(事実主張が薄い導入・修辞・見出し・評価語)",
                          "rows": sample_rows}

    # ---- 作業3: negation_polarity_mismatch 全149件 ----
    neg_rows, neg_cls = [], Counter()
    uniq = {}
    for r in runs:
        iid = r["instance_id"]
        for c in r["audit"]["union_candidates"]:
            if "negation_polarity_mismatch" in c["sub_reasons"]:
                rf = c["related_fact_ids"][0] if c["related_fact_ids"] else ""
                fl = blocks[iid].get(rf, "").split("\n")[0]
                lab = classify_negation(c["claim_text"], fl)
                neg_cls[lab] += 1
                uniq.setdefault((iid, c["unit_ids"][0]), lab)
                neg_rows.append({"instance": iid, "unit": c["unit_ids"][0], "label": lab})
    ucls = Counter(uniq.values())
    n_fp = sum(v for k, v in neg_cls.items() if k.startswith("FP"))
    R["negation_polarity_mismatch"] = {"fired_total": len(neg_rows), "unique_instance_unit": len(uniq), "classification_total": dict(neg_cls.most_common()),
                                       "classification_unique": dict(ucls.most_common()),
                                       "false_positive_rate_total": round(n_fp / len(neg_rows), 3),
                                       "confirmed_true_polarity_mismatch": 0,
                                       "note": "確認=発火単位と第1support factの否定語(JA marker/EN regex)を実際に列挙し70 unique件を目視。極性反転の確定例は0。推測=PLAUSIBLE_TRUE 2種は極性反転ではなく『Ledgerに無い留保』。第1support factのみでの再現(全support factではない)"}

    # ---- 作業4: Stage 2負荷・費用の推定 ----
    rep30 = defaultdict(list)
    for p in glob.glob(f"{REP30}/instances_s*/*.json"):
        d = json.load(open(p, encoding="utf-8"))
        c1 = d["cycles"][0] if d["cycles"] else {}
        rep30[d["instance_id"]].append({"n2": len(c1.get("stage2_results", [])), "bl": c1.get("blocking_count", 0),
                                        "rw": sum(len(x.get("rewrite_records", [])) for x in d["cycles"]), "cycles": len(d["cycles"]),
                                        "cost": d.get("total_cost_jpy", 0.0), "final": d["final_state"]})
    allr = [x for v in rep30.values() for x in v]
    tot_n2, tot_bl = sum(x["n2"] for x in allr), sum(x["bl"] for x in allr)
    nr = [x for i, v in rep30.items() if GROUP_OF.get(i) == "NORMAL" for x in v]
    n2_nor, bl_nor = sum(x["n2"] for x in nr), sum(x["bl"] for x in nr)
    rate_all, rate_nor = tot_bl / tot_n2, (bl_nor / n2_nor if n2_nor else 0.0)
    rw_runs = [x for x in allr if x["rw"] > 0]
    fit = lambda n: 0.0 if n <= 0 else FIT_A + FIT_B * n
    cost_per_rewrite = st.mean([(x["cost"] - fit(x["n2"])) / x["rw"] for x in rw_runs])  # Stage 2を除いたRewrite+Recheck費用/Rewrite
    cmean = {i: m([x["cost"] for x in v]) for i, v in rep30.items()}
    n2mean = {i: m([x["n2"] for x in v]) for i, v in rep30.items()}
    s1_cost = [r["total_cost_jpy"] for r in runs]
    rows_est = []
    for r in runs:
        iid = r["instance_id"]
        c = r["audit"]["n_union_candidates"]
        base = cmean[iid] - fit(n2mean[iid])
        d_lin = fit(c) - fit(n2mean[iid])
        d_cap = fit(min(c, 10)) - fit(n2mean[iid])
        extra_bl = rate_nor * max(0, c - n2mean[iid]) if GROUP_OF[iid] == "NORMAL" else rate_all * max(0, c - n2mean[iid])
        rows_est.append({"iid": iid, "group": GROUP_OF[iid], "cand": c, "s1": r["total_cost_jpy"], "rep30_cost": cmean[iid], "rep30_n2": n2mean[iid],
                         "stage2_new_lin": fit(c), "stage2_new_cap10": fit(min(c, 10)), "d_lin": d_lin, "d_cap": d_cap, "extra_blocking_rate_based": extra_bl})

    def agg(rows, key):
        return round(sum(x[key] for x in rows) / len(rows), 3) if rows else 0
    est = {}
    for g in ["ALL", "NORMAL", "SC", "holdout"]:
        rows = rows_est if g == "ALL" else [x for x in rows_est if x["group"] == g]
        s1m = agg(rows, "s1")
        r30 = agg(rows, "rep30_cost")
        e = {"n_runs": len(rows), "mean_cand": agg(rows, "cand"), "stage1_fresh_cost_per_run": s1m, "rep30_cost_per_run_matched": r30,
             "stage2_new_cost_per_run_linear_fit": agg(rows, "stage2_new_lin"), "stage2_new_cost_per_run_fit_capped_at_10cand": agg(rows, "stage2_new_cap10"),
             "extra_blocking_per_run_rate_based": agg(rows, "extra_blocking_rate_based")}
        extra_rw_cost = e["extra_blocking_per_run_rate_based"] * cost_per_rewrite
        e["extra_rewrite_recheck_cost_per_run"] = round(extra_rw_cost, 3)
        for nm, k in (("linear", "d_lin"), ("capped10", "d_cap")):
            tot = r30 + s1m + agg(rows, k) + extra_rw_cost
            e[f"total_per_run_{nm}"] = round(tot, 3)
            e[f"add_vs_rep24_{nm}"] = round(tot - REP24_MEAN, 3)
            e[f"add_vs_rep30_{nm}"] = round(tot - r30, 3)
        # Stage 1のみ追加(Stage 2を現行のまま/BLOCKING増なしの下限)
        e["add_vs_rep24_floor_stage1_only(下限)"] = round(r30 + s1m - REP24_MEAN, 3)
        est[g] = e
    n24 = 24.0
    sc_ = {"candidates_per_article": n24, "stage2_cost_linear": round(fit(n24), 3), "stage2_cost_capped10": round(fit(10), 3),
           "rep30_blocking_rate_all": round(rate_all, 3), "rep30_blocking_rate_NORMAL": round(rate_nor, 3),
           "rep30_items_all": tot_n2, "rep30_blocking_all": tot_bl, "rep30_items_NORMAL": n2_nor, "rep30_blocking_NORMAL": bl_nor,
           "expected_blocking_conservative_NORMALrate": round(n24 * rate_nor, 2), "expected_blocking_conservative_allrate": round(n24 * rate_all, 2),
           "expected_blocking_if_only_R_label_share": round(n24 * lab_cnt["R"] / n_s, 2),
           "prob_zero_blocking_poisson_NORMALrate": round(2.718281828 ** (-(n24 * rate_nor)), 3),
           "prob_zero_blocking_poisson_Rshare": round(2.718281828 ** (-(n24 * lab_cnt["R"] / n_s)), 3),
           "rep30_normal_instance_rewrite": {i: [x["rw"] for x in v] for i, v in rep30.items() if GROUP_OF.get(i) == "NORMAL"},
           "rep30_cycles_ge2_runs": sum(1 for x in allr if x["cycles"] >= 2), "rep30_n_runs": len(allr),
           "rep30_runs_with_rewrite": len(rw_runs), "cost_per_rewrite_excl_stage2": round(cost_per_rewrite, 3),
           "fit_domain_note": "fitは候補範囲[0,10]、24への外挿。線形とcap10の2通りを併記"}
    R["stage2_estimate"] = {"scenario_24": sc_, "by_group": est}
    R["verdict"] = {"KPI_cost_plus2": "No(下限=Stage1新設だけで+" + str(est["ALL"]["add_vs_rep24_floor_stage1_only(下限)"]) + "円/run vs rep24。線形fit込み+"
                    + str(est["ALL"]["add_vs_rep24_linear"]) + "、cap10でも+" + str(est["ALL"]["add_vs_rep24_capped10"])
                    + "。同一instance照合のrep30比でも下限+" + str(est["ALL"]["stage1_fresh_cost_per_run"]) + "、線形+" + str(est["ALL"]["add_vs_rep30_linear"])
                    + "、cap10 +" + str(est["ALL"]["add_vs_rep30_capped10"]) + "。NORMAL群は線形+" + str(est["NORMAL"]["add_vs_rep30_linear"]) + ")。基準+2円/記事を下限でも超えるか僅差、"
                    "Stage 2・追加Rewriteを入れると超過。注意: hold-out 9本は判定単位が1文のみ(候補1/run)で記事規模の代表ではない",
                    "KPI_human_review_zero": "不明(BLOCKING・Rewrite・cycle増で上限到達リスクは上がる。実測は段階Bのみ)",
                    "KPI_safety_zero_miss": "見込みYes(Stage 1はSC 6/6・hold-out 9/9。ただしStage 2が候補過多でBLOCKING判定の質を保つかは不明)"}
    json.dump(R, open(f"{OUT}/stageA_candidate_composition_01.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    write_md(R)
    print(json.dumps({k: R[k] for k in ("by_group_mean_per_run", "source_total", "verdict")}, ensure_ascii=False, indent=1)[:3500])


def write_md(R):
    L = ["# 段階A候補の内訳とStage 2負荷見込み(委任_09、¥0)", "", "KPI provenance: 既存fresh出力(段階A 42 run、rep30)の再集計。E2Eではない。", ""]
    L += ["## 1. 候補の発生源(1 runあたり平均)", "", "| 群 | run | 判定単位 | 候補∪ | LLM両経路 | LLM r3のみ | LLM r5のみ | 決定論のみ | 候補/単位 |", "|---|---|---|---|---|---|---|---|---|"]
    for g, d in R["by_group_mean_per_run"].items():
        L.append(f"| {g} | {d['n_runs']} | {d['judged']} | {d['union']} | {d['LLM_both(r3+r5)']} | {d['LLM_r3only']} | {d['LLM_r5only']} | {d['deterministic_only']} | {d['union_over_judged']} |")
    L += ["", "instance別(平均/run、union・r3・r5・判定単位)", "", "| instance | n | 判定単位 | r3 | r5 | ∪ |", "|---|---|---|---|---|---|"]
    for i, d in R["by_instance_mean_per_run"].items():
        L.append(f"| {i} | {d['n_runs']} | {d['judged']} | {d['r3']} | {d['r5']} | {d['union']} |")
    lc = R["llm_candidates"]
    L += ["", f"全発生源(候補総数): {R['source_total']}", f"決定論で戻した理由(r3経路): {R['det_return_by_reason']}",
          f"SUPPORTED割合(r3、決定論後/前): {R['r3_supported_share_after_det']}/{R['r3_supported_share_before_det']}。r5: MATCH {R['r5_match_share']}、UNMENTIONED(対応factなし) {R['r5_unmentioned_share']}",
          f"LLM候補{lc['n']}件のフラグ分布: {lc['flag_distribution']}", f"issueあり率 {lc['issue_present_rate']}(平均{lc['issue_len_mean']}字)、related_fact_idあり {lc['related_fact_id_present_rate']}、claim_in_articleあり {lc['claim_in_article_present_rate']}",
          f"汎用フラグ(changed_fact/unsupported_new_claim/changed_scope)のみの候補: {lc['only_generic_flags_rate(changed_fact/unsupported_new_claim/changed_scope以外が無い)']}、フラグなし: {lc['no_flag_rate']}", ""]
    ns = R["normal_sample"]
    L += ["## 2. NORMAL 6 instance先頭5候補(30件、s1)のラベル(推測)", "", f"{ns['labels']}、割合{ns['share']}。{ns['note']}", "", "| instance | unit | ラベル | claim |", "|---|---|---|---|"]
    for x in ns["rows"]:
        L.append(f"| {x['instance'][:14]} | {x['unit']} | {x['label']} | {x['claim'][:70]} |")
    nm = R["negation_polarity_mismatch"]
    L += ["", "## 3. negation_polarity_mismatch", "", f"発火{nm['fired_total']}件(unique {nm['unique_instance_unit']})。誤発火率(FP分類)={nm['false_positive_rate_total']}、確定した真の極性不一致={nm['confirmed_true_polarity_mismatch']}", "", "| 分類 | 件数(全発火) |", "|---|---|"]
    for k, v in nm["classification_total"].items():
        L.append(f"| {k} | {v} |")
    L += ["", nm["note"], ""]
    e = R["stage2_estimate"]
    s = e["scenario_24"]
    L += ["## 4. Stage 2負荷・KPI見込み", "", f"候補24/記事: Stage 2費用 線形fit ¥{s['stage2_cost_linear']}/記事(cap10なら¥{s['stage2_cost_capped10']})。rep30のBLOCKING率 全体{s['rep30_blocking_rate_all']}({s['rep30_blocking_all']}/{s['rep30_items_all']})、NORMAL {s['rep30_blocking_rate_NORMAL']}({s['rep30_blocking_NORMAL']}/{s['rep30_items_NORMAL']})。",
          f"期待BLOCKING/記事: 保守(NORMAL率){s['expected_blocking_conservative_NORMALrate']}、保守(全体率){s['expected_blocking_conservative_allrate']}、サンプルのR割合のみBLOCKINGなら{s['expected_blocking_if_only_R_label_share']}。0件(Rewriteなし)になる確率(Poisson近似): {s['prob_zero_blocking_poisson_NORMALrate']}/{s['prob_zero_blocking_poisson_Rshare']}。",
          f"rep30: cycles>=2が{s['rep30_cycles_ge2_runs']}/{s['rep30_n_runs']} run、Rewriteあり{s['rep30_runs_with_rewrite']} run、NORMALのRewrite {s['rep30_normal_instance_rewrite']}。Rewrite+Recheck費用(Stage 2除く)≒¥{s['cost_per_rewrite_excl_stage2']}/Rewrite。{s['fit_domain_note']}", "",
          "| 群 | run | 平均候補 | Stage1 fresh | rep30費用(照合) | Stage2新(線形) | 追加BLOCKING | 合計/run(線形) | rep24比(線形) | rep24比(cap10) | rep24比(下限=Stage1のみ) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for g, d in e["by_group"].items():
        L.append(f"| {g} | {d['n_runs']} | {d['mean_cand']} | {d['stage1_fresh_cost_per_run']} | {d['rep30_cost_per_run_matched']} | {d['stage2_new_cost_per_run_linear_fit']} | {d['extra_blocking_per_run_rate_based']} | {d['total_per_run_linear']} | +{d['add_vs_rep24_linear']} | +{d['add_vs_rep24_capped10']} | +{d['add_vs_rep24_floor_stage1_only(下限)']} |")
    L += ["", "## 結論", ""] + [f"- {k}: {v}" for k, v in R["verdict"].items()]
    open(f"{OUT}/stageA_candidate_composition_01.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
