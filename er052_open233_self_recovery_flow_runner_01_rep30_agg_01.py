# -*- coding: utf-8 -*-
# rep30(委任_11作成・未実行、実行は委任_12以降)集計。API呼び出しなし(¥0)。
# 方針: rep29_agg_01(KPI判定・Safety-critical・費用・Tier 0/S1・N1′・AG1等の既存集計)を、出力先だけrep30へ差し替えて再利用し
# (`summary_01.*`/`summary_kpi_01.json`/`blocking_claims_01.md`/`release_log_01.md`。ファイル内の「rep29」表記はrep30のこと)、
# その上で、委任_11の新設計に固有の指標(許可リスト外STAGE4件数・G経路のS1通過率・未書換BLOCKINGによるPASS件数・スイッチ別発火・
# rep29/rep28/rep24/iter7との比較)を `summary_rep30_new_01.json` へ追加する。
from __future__ import annotations

import collections
import json
import os

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep29_agg_01 as agg29
import er052_open233_self_recovery_flow_runner_01_rep29_full_01 as full29
import er052_open233_self_recovery_flow_runner_01_rep30_full_01 as full


def _load(p):
    return agg29._load(p)


def _runs(dirpath, ids):
    return agg29._runs_in(dirpath, ids)


def _stage4_rows(runs):
    return [(s, i, d.get("stage4_reason")) for s, i, d in runs if d.get("final_state") == "STAGE4_ESCALATION"]


def _cost(runs):
    return [d.get("total_cost_jpy") or 0.0 for _s, _i, d in runs]


def _mean(xs):
    return round(sum(xs) / len(xs), 4) if xs else None


def new_design_metrics(runs) -> dict:
    """委任_11の新設計に固有の指標(instance JSONの`stage4_allowlist`、`cycles[*].judge_only_cycle`等から)。"""
    allowed = runner.STAGE4_ALLOWED_REASONS
    s4 = _stage4_rows(runs)
    outside = [(s, i, r) for s, i, r in s4 if r not in allowed]
    g_cycles, g_without_s1 = [], []
    fired = collections.Counter()
    legacy_rerouted = collections.Counter()
    pass_blocked = unrewritten_pass = t_used = 0
    pinned = []
    for s, iid, d in runs:
        sa = d.get("stage4_allowlist") or {}
        for k, v in (sa.get("switch_fired") or {}).items():
            fired[k] += v
        for e in sa.get("decisions") or []:
            if e.get("legacy_reason"):
                legacy_rerouted[e["legacy_reason"]] += 1
        pass_blocked += sa.get("pass_blocked_by_carry", 0)
        unrewritten_pass += sa.get("unrewritten_blocking_pass", 0)
        t_used += 1 if sa.get("t_used") else 0
        for c in d.get("cycles", []):
            if c.get("judge_only_cycle"):
                has_s1 = c.get("stage2_downgrade_confirm_log") is not None
                nonblk = [sr for sr in c.get("stage2_results", []) if sr.get("materiality") != "BLOCKING"]
                # 降格(非BLOCKING)が出たG cycleは全件S1(`second_opinion`)を通っていること。floor/pinned/carried/reusedは対象外
                bad = [sr for sr in nonblk if not sr.get("second_opinion") and not sr.get("floor_reason")
                       and not sr.get("reused_nonblocking_verdict") and sr.get("basis") != "precheck_floor"]
                g_cycles.append({"sample": s, "instance_id": iid, "cycle": c["cycle"], "s1_log_present": has_s1,
                                 "nonblocking": len(nonblk), "nonblocking_without_s1": len(bad)})
                if bad:
                    g_without_s1.append((s, iid, c["cycle"]))
            for sr in c.get("stage2_results", []):
                if sr.get("basis") == "materiality_pinned":
                    pinned.append({"sample": s, "instance_id": iid, "cycle": c["cycle"], "claim": (sr.get("claim_text") or "")[:80]})
    return {
        "n_runs": len(runs), "stage4_count": len(s4), "stage4_rows": s4,
        "stage4_outside_allowlist_count": len(outside), "stage4_outside_allowlist": outside,
        "stage4_allowed_reason_counts": dict(collections.Counter(r for _s, _i, r in s4 if r in allowed)),
        "legacy_exits_rerouted": dict(legacy_rerouted),
        "g_judge_only_cycles": g_cycles,
        "g_cycles_with_nonblocking_without_s1": g_without_s1,
        "g_s1_pass_rate": (None if not g_cycles else round(1 - len(g_without_s1) / len(g_cycles), 4)),
        "unrewritten_blocking_pass_count": unrewritten_pass,
        "pass_blocked_by_carry_events": pass_blocked,
        "t_used_runs": t_used, "switch_fired": dict(fired), "pinned_blocking_events": pinned}


def run_agg():
    # rep29_aggの既存集計をrep30の出力先で再利用する
    full29.OUT_DIR_REP29 = full.OUT_DIR_REP30
    agg29.run_agg()
    ids = full.ALL_IDS
    cur = _runs(full.OUT_DIR_REP30, ids)
    r29 = _runs(full.REP29_DIR, ids)
    r28 = _runs(full.REP28_DIR, ids)
    r24 = _runs(full.REP24_DIR, ids)
    it7 = agg29._iter7_runs(ids)
    NORMAL = runner.NORMAL_GROUP_INSTANCE_IDS

    def per_inst_mean(runs):
        m = collections.defaultdict(list)
        for _s, i, d in runs:
            m[i].append(d.get("total_cost_jpy") or 0.0)
        return {i: sum(v) / len(v) for i, v in m.items()}

    def adds(base):
        b = per_inst_mean(base)
        return [(s, iid, round((d.get("total_cost_jpy") or 0.0) - b[iid], 4)) for s, iid, d in cur if iid in b]

    def normal_rewrite(runs):
        n = [(s, i, d) for s, i, d in runs if i in NORMAL]
        return {"n_normal_runs": len(n), "with_rewrite": sum(1 for _s, _i, d in n if agg29._executed_rewrites_ladder(d))}

    out = {"new_design": new_design_metrics(cur), "n_runs": len(cur)}
    out["comparison"] = {}
    for tag, base in (("rep29", r29), ("rep28", r28), ("rep24", r24), ("iter7", it7)):
        a = adds(base)
        out["comparison"][tag] = {
            "stage4_count": len(_stage4_rows(base)), "stage4_rows": _stage4_rows(base),
            "cost_total": round(sum(_cost(base)), 4), "cost_mean_per_run": _mean(_cost(base)),
            "avg_add_matched_instance": _mean([x[2] for x in a]), "worst_add_matched_instance": (max(a, key=lambda x: x[2]) if a else None),
            "runs_over_cap_plus3": [x for x in a if x[2] > 3.0], "normal_group_rewrite": normal_rewrite(base)}
    out["rep30"] = {"cost_total": round(sum(_cost(cur)), 4), "cost_mean_per_run": _mean(_cost(cur)),
                    "worst_run": max(_cost(cur)) if cur else None, "normal_group_rewrite": normal_rewrite(cur),
                    "stage4_count": len(_stage4_rows(cur)), "stage4_rows": _stage4_rows(cur),
                    "cycles_ge3_runs": sum(1 for _s, _i, d in cur if len(d.get("cycles", [])) >= 3),
                    "cycles_ge4_runs(判定だけのcycle等)": sum(1 for _s, _i, d in cur if len(d.get("cycles", [])) >= 4)}
    # 事前基準(委任_11でFable追加): 許可リスト外STAGE4 0件 / G経路の降格は全件S1通過 / 未書換BLOCKINGによるPASS 0件
    nd = out["new_design"]
    out["pre_registered_criteria"] = {
        "stage4_outside_allowlist_is_zero": nd["stage4_outside_allowlist_count"] == 0,
        "g_route_downgrades_all_through_s1": not nd["g_cycles_with_nonblocking_without_s1"],
        "unrewritten_blocking_pass_is_zero": nd["unrewritten_blocking_pass_count"] == 0,
        "primary_human_review_zero": nd["stage4_count"] == 0,
        "note": "KPI本体(重大見逃し0・平均追加+¥2・Cap+¥3)は summary_kpi_01.json(rep29_agg再利用)の`kpi`を参照"}
    p = f"{full.OUT_DIR_REP30}/summary_rep30_new_01.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print("=== rep30 new-design summary ===")
    print(json.dumps(out, ensure_ascii=True, indent=1, default=str)[:9000])
    return out


if __name__ == "__main__":
    run_agg()
