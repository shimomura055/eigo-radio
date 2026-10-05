# -*- coding: utf-8 -*-
"""OPEN-233 E2E-ACCEPTANCE-01 委任_20: E2E停止の費用内訳・rep30比較・20 run再予測(API呼出なし、既存jsonの再集計のみ、¥0)。"""
import json, glob, os, sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E2E = os.path.join(ROOT, "er052_output", "open233_e2e_acceptance_01")
REP30 = os.path.join(ROOT, "er052_output", "open233_self_recovery_flow_runner_01_rep30")
OUT = os.path.dirname(os.path.abspath(__file__))
REMAIN_BUDGET = 98.29 - 10.76


def jl(p):
    return json.load(open(p, encoding="utf-8"))


def cat(label):
    if "_stage1_r3" in label: return "S1_r3初回"
    if "_stage1_r5" in label: return "S1_r5初回"
    if "recheck_r3" in label: return "Recheck_r3"
    if "recheck_r5v" in label: return "Recheck_r5v"
    if re.search(r"recheck$", label): return "Recheck(旧1call)"
    if "exit_r3" in label: return "出口3'-R_r3"
    if "floorverify" in label: return "floor_verify"
    if "_s1_stage2_" in label: return "Stage2_s1(2nd opinion)"
    if "stage2_stage2_" in label: return "Stage2_1st"
    if "fact:" in label or "_e1_" in label or "_e2_" in label: return "Rewrite"
    return "その他"


def breakdown(hist):
    agg = {}
    for h in hist:
        c = cat(h["label"]); u = h["usage"]
        a = agg.setdefault(c, {"n": 0, "jpy": 0.0, "in": 0, "out": 0, "reason": 0})
        a["n"] += 1; a["jpy"] += h["cost_jpy"]; a["in"] += u["input_tokens"]; a["out"] += u["output_tokens"]; a["reason"] += u["reasoning_tokens"]
    for a in agg.values(): a["jpy"] = round(a["jpy"], 4)
    return agg


b = jl(os.path.join(E2E, "budget_state_e2e_acceptance_01.json"))
H = b["history"]
hB3 = [h for h in H if h["label"].startswith("bgroup_B3")]
hA = [h for h in H if h["label"].startswith("safety_A2A3")]
res = {"e2e_B3": breakdown(hB3), "e2e_A2A3_partial": breakdown(hA),
       "e2e_B3_total": round(sum(h["cost_jpy"] for h in hB3), 4), "e2e_A2A3_total_at_abort": round(sum(h["cost_jpy"] for h in hA), 4),
       "cumulative": b["cumulative_jpy"], "cumulative_calls": b["cumulative_calls"]}

# HF別Rewrite call(A2A3, B3)
def hf_calls(hist):
    out = {}
    for h in hist:
        m = re.search(r"_c(\d)_fact:(HF-\d+)_(\w+)", h["label"])
        if m: out.setdefault(f"c{m.group(1)}:{m.group(2)}", []).append(m.group(3) + f"({h['cost_jpy']})")
    return out
res["rewrite_calls_by_cycle_HF"] = {"B3": hf_calls(hB3), "A2A3": hf_calls(hA)}

# rep30(Stage 1凍結)の後段
est = jl(os.path.join(E2E, "estimate.json"))
s1est = {}
for r in est["stage1_rows"]:
    s1est.setdefault(r["instance_id"], r["jpy_low_mid_high"][1])
rep = {}
for p in glob.glob(os.path.join(REP30, "instances_s1", "*.json")):
    d = jl(p)
    cl = d["call_log"]
    tot = lambda f: round(sum(c["cost_jpy"] for c in cl if f(c["label"])), 4)
    rep[d["instance_id"]] = {
        "final": d["final_state"], "cycles": len(d["cycles"]), "calls": d["total_calls"], "total": d["total_cost_jpy"],
        "s2": tot(lambda l: "stage2_" in l), "rw": tot(lambda l: ("fact:" in l or "_e1_" in l or "_e2_" in l)),
        "rc": tot(lambda l: l.endswith("recheck")), "n_rc": sum(1 for c in cl if c["label"].endswith("recheck")),
        "n_rw_rec": sum(len(c.get("rewrite_records", [])) for c in d["cycles"])}
res["rep30_B3"] = rep["bgroup_B3"]; res["rep30_A2A3"] = rep["safety_A2A3"]; res["rep30_A4"] = rep["safety_A4"]
ds = [v["s2"] for v in rep.values() if v["final"] == "RESOLVED_STAGE2_DOWNGRADE"]
S2_DOWN_MEAN = round(sum(ds) / len(ds), 4)
res["rep30_s2_downgrade_only_mean"] = S2_DOWN_MEAN

# 実測のrep30比(E2E c1, 同一instance)
def s(h, key): return round(sum(x["cost_jpy"] for x in h if cat(x["label"]) in key), 4)
res["ratio_vs_rep30"] = {
    "B3": {"s2_c1": [s([x for x in hB3 if "_c1_" in x["label"]], ["Stage2_1st", "Stage2_s1(2nd opinion)"]), rep["bgroup_B3"]["s2"]],
           "rewrite": [s(hB3, ["Rewrite"]), rep["bgroup_B3"]["rw"]], "recheck": [s(hB3, ["Recheck_r3", "Recheck_r5v"]), rep["bgroup_B3"]["rc"]]},
    "A2A3": {"s2_c1": [s([x for x in hA if "_c1_" in x["label"]], ["Stage2_1st", "Stage2_s1(2nd opinion)"]), rep["safety_A2A3"]["s2"]],
             "rewrite": [s(hA, ["Rewrite"]), rep["safety_A2A3"]["rw"]], "recheck": [s(hA, ["Recheck_r3", "Recheck_r5v"]), rep["safety_A2A3"]["rc"]]}}

# 再予測(low/mid/high)
F_S1 = (1.0, 1.22, 1.36)     # Stage1実測/見積mid: B3 1.495/1.379=1.08, A2A3 1.771/1.303=1.36、midは2点平均
K_S2 = (1.0, 1.45, 1.7)      # Stage 2(c1)実測/rep30: B3 1.45, A2A3 1.48
K_RW = (1.5, 3.7, 4.0)       # Rewrite call費: 実測/rep30 B3 4.0, A2A3 3.7
R_RC = (0.47, 0.8, 0.93)     # 新Recheck(r3+r5v)1回: B3 0.93, A2A3 c1 0.92/c2 0.47
EX = (0.5, 0.62, 0.75)       # 出口3'-R(B3実測0.6175、A2A3は未到達)
FV_SC = (0.1, 0.45, 0.8)     # floor_verify: B3 0.13, A2A3 0.78
FV_NSC = (0.05, 0.15, 0.4)   # 推測
XC_SC = (0.0, 0.75, 1.5)     # SCの追加cycle(rep30が1 cycleの場合のみ): B3 c2 0.22、A2A3 c2 1.55
SC = {"bgroup_B3", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B4", "neg5_hormuz_div_a2"}
NON = ["hormuz_run03_advanced", "hormuz_run03_standard", "meta_run03_advanced", "meta_run03_standard",
       "neg1_meta_b3prod_a2", "neg2_meta_refresh_a2", "neg3_hormuz_prodrunner_b1b", "neg7_meta_prodrunner_b1b"]


def model(iid):
    r = rep[iid]; out = []
    for i in range(3):
        s1 = s1est[iid] * F_S1[i]
        base_s2 = r["s2"] if r["s2"] > 0.05 else S2_DOWN_MEAN
        s2 = base_s2 * K_S2[i]
        fv = (FV_SC if iid in SC else FV_NSC)[i]
        rw = r["rw"] * K_RW[i]
        rc = r["n_rc"] * R_RC[i]
        ex = EX[i] if r["n_rw_rec"] > 0 else 0.0
        xc = XC_SC[i] if (iid in SC and r["cycles"] <= 1 and r["n_rw_rec"] > 0) else 0.0
        out.append(round(s1 + s2 + fv + rw + rc + ex + xc, 3))
    return out

per = {i: model(i) for i in list(SC) + NON}
res["model_per_instance_low_mid_high"] = per
def tot(ids):
    return [round(sum(per[i][k] for i in ids), 2) for k in range(3)]
sc_ids = ["bgroup_B3", "safety_A2A3", "safety_A4", "safety_A5", "bgroup_B4", "neg5_hormuz_div_a2"]
all20 = sc_ids * 2 + NON
res["total_20"] = tot(all20)
res["total_14_sc_n1"] = tot(sc_ids + NON)
res["total_8_nonsc"] = tot(NON)
# 残(B3 s1完了済みを除く)
b3 = per["bgroup_B3"]
res["remaining_19"] = [round(res["total_20"][k] - b3[k] if False else res["total_20"][k] - res["e2e_B3_total"], 2) for k in range(3)]
res["remaining_13_sc_n1"] = [round(res["total_14_sc_n1"][k] - res["e2e_B3_total"], 2) for k in range(3)]
res["remaining_budget"] = round(REMAIN_BUDGET, 2)
res["gap_vs_remaining_budget"] = {"19run": [round(REMAIN_BUDGET - v, 2) for v in res["remaining_19"]],
                                  "13run": [round(REMAIN_BUDGET - v, 2) for v in res["remaining_13_sc_n1"]],
                                  "8run": [round(REMAIN_BUDGET - v, 2) for v in res["total_8_nonsc"]]}
res["model_check"] = {"B3_model": per["bgroup_B3"], "B3_actual": res["e2e_B3_total"], "A2A3_model": per["safety_A2A3"], "A2A3_actual_at_abort": res["e2e_A2A3_total_at_abort"]}
# 閾値
res["runs_gt_6_by_model"] = {k: [i for i in per if per[i][j] > 6] for j, k in enumerate(["low", "mid", "high"])}
res["runs_gt_10_by_model"] = {k: [i for i in per if per[i][j] > 10] for j, k in enumerate(["low", "mid", "high"])}
# 純増(参考)
SUB = 0.83
nonsc_mean = [round(sum(per[i][k] for i in NON) / len(NON), 2) for k in range(3)]
res["net_increase_reference"] = {"B3_actual_article": res["e2e_B3_total"], "set_if_both_B3": round(2 * res["e2e_B3_total"] - SUB, 2),
                                  "nonsc_mean_per_article_low_mid_high": nonsc_mean,
                                  "set_nonsc_low_mid_high": [round(2 * v - SUB, 2) for v in nonsc_mean],
                                  "expected_set_mid": 5.4, "expected_set_high": 6.7}
json.dump(res, open(os.path.join(OUT, "e2e_stop_analysis_01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
