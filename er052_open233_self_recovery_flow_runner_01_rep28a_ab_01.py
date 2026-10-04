# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep28a_ab_01.py
# OPEN-233-KPI-RECOVERY-REDESIGN-02 (委任_06 作業4: neg3/neg2の限定A/B。N3′[Recheckへ書き換え前後の対]の採否判定)
# ============================================================
# instance=neg3_hormuz_prodrunner_b1b, neg2_meta_refresh_a2、n=2、構成A=KPI構成+N1′(`RECHECK_BEFORE_AFTER_PAIRS`=False)、
# 構成B=A+N3′(`RECHECK_BEFORE_AFTER_PAIRS`=True)。計8 run。Stage 1はsha256一致でcache共有(A/B・sample間で同一入力)。
# 即時STOP(委任_06): JA変更・例外2 instance以上・1 instance-run費用>JPY7・TrialAbort。見逃し/STAGE4は止めずに完走。
# Production codeは変更しない。出力はOUT_DIRのみ。再実行・n増しはしない(既存jsonがあればskipするのみ)。TTSなし。
# 採否基準(事前設定、事後変更しない): 設計書§13-6。集計は`--stage agg`(API呼び出しなし)。
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import traceback

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01_rep23_limited_01 as rep23

OUT_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep28a"
BUDGET_STATE = f"{OUT_DIR}/budget_state_c233av_06_rep28a.json"
IDS = ["neg3_hormuz_prodrunner_b1b", "neg2_meta_refresh_a2"]
CONFIGS = {"A": False, "B": True}   # 構成 -> RECHECK_BEFORE_AFTER_PAIRS


def apply_switches(budget_jpy: float, n3: bool) -> dict:
    runner.OUT_DIR = OUT_DIR
    runner.BUDGET_STATE_PATH = BUDGET_STATE
    runner.TOTAL_BUDGET_JPY = budget_jpy
    applied = runner.apply_kpi_trial_switches()
    runner.RECHECK_BEFORE_AFTER_PAIRS = n3
    assert runner.RECHECK_MERGE_UNRESOLVED is True and runner.STAGE2_DOWNGRADE_VERIFY is False
    assert runner.CAUSAL_FLOOR is True and runner.STAGE2_SECOND_OPINION is True and runner.VS_SENTENCE_RESTORE is True
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B
    return applied


def stop_reasons(r: dict) -> list:
    out = [x for x in rep23.immediate_stop_check(r) if x.startswith("a:")]
    if (r.get("total_cost_jpy") or 0) > 7.0:
        out.append(f"cost>7: {r.get('total_cost_jpy')}")
    return out


def run_main(budget_jpy: float, n: int):
    os.makedirs(OUT_DIR, exist_ok=True)
    client = vfl01.get_client()
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    state = None
    consecutive_errors = [0]
    plan = [(cfg, s, iid) for cfg in CONFIGS for s in range(1, n + 1) for iid in IDS]
    for cfg, s, iid in plan:
        applied = apply_switches(budget_jpy, CONFIGS[cfg])
        if state is None:
            state = runner.load_budget_state()
        log["switches_" + cfg] = {**applied, "RECHECK_BEFORE_AFTER_PAIRS": CONFIGS[cfg]}
        subdir = f"instances_{cfg}_s{s}"
        path = f"{OUT_DIR}/{subdir}/{iid}.json"
        if os.path.exists(path):
            print(f"[skip existing] {subdir}/{iid}")
            continue
        try:
            r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                    stage1_cache=stage1_cache, instances_subdir=subdir)
        except runner.TrialAbort as e:
            log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
            break
        except Exception as e:  # 例外は記録(再実行しない)。2 instance以上でSTOP
            log["exceptions"].append({"config": cfg, "sample": s, "instance_id": iid, "error": repr(e),
                                      "tb": traceback.format_exc()[-1500:]})
            print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
            if len({(x['instance_id'], x['config'], x['sample']) for x in log["exceptions"]}) >= 2:
                log.update(stopped=True, stop_reason="exceptions in >=2 instance-runs")
                break
            continue
        reasons = stop_reasons(r)
        print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
              f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
        log["runs"].append({"config": cfg, "sample": s, "instance_id": iid, "final_state": r["final_state"],
                            "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"], "stop_check": reasons})
        if reasons:
            log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4) if state else None
    runner.save_json(f"{OUT_DIR}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:5000])


# ---------------------------------------------------------------- 集計(API呼び出しなし)
def _load(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[“”\"‘’]", "", t or "")).strip().lower()


def run_summary(d: dict) -> dict:
    cyc = d.get("cycles", [])
    rechecks = [c for c in cyc if c.get("recheck_overall_status") is not None]
    selfc = [c for c in rechecks if c.get("recheck_overall_status") == "LEDGER_COMPLIANT"
             and c.get("recheck_all_prior_issues_resolved") is False]
    confirms = [c for c in cyc if c.get("recheck_confirm_overall_status") is not None]
    unresolved_reasons = []
    formal = []   # 形だけの解消: resolved=trueだが、そのclaimの元の文が書き換え後の本文に逐語で残っている
    for c in rechecks:
        blk = [s for s in c.get("stage2_results", []) if s.get("materiality") == "BLOCKING"]
        after = _norm(c.get("en_text_after_rewrite") or "")
        for it in (c.get("recheck_prior_issues_resolved") or []):
            idx = it.get("index")
            if not it.get("resolved"):
                unresolved_reasons.append({"cycle": c["cycle"], "index": idx, "explanation": it.get("explanation")})
            elif isinstance(idx, int) and idx < len(blk):
                orig = _norm(blk[idx].get("claim_span_text") or blk[idx].get("claim_text"))
                if orig and orig in after:
                    formal.append({"cycle": c["cycle"], "index": idx, "orig": orig[:120], "explanation": it.get("explanation")})
    merges = [{"cycle": c["cycle"], **(c.get("recheck_merge") or {})} for c in cyc if c.get("recheck_merge")]
    # N1′合流claimの次cycleStage 2結果
    merged_stage2 = []
    for i, c in enumerate(cyc):
        m = c.get("recheck_merge")
        if m and m.get("n_merged") and i + 1 < len(cyc):
            merged_stage2.append({"from_cycle": c["cycle"], "n_merged": m["n_merged"],
                                  "next_stage2": [(s.get("related_fact_id") or (s.get("dev") or {}).get("related_fact_id"),
                                                   s.get("materiality"), (s.get("claim_text") or "")[:90])
                                                  for s in cyc[i + 1].get("stage2_results", [])]})
    executed = sum(1 for c in cyc for rr in c.get("rewrite_records", []) if rr.get("ladder_level_used"))
    return {
        "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"), "n_cycles": len(cyc),
        "n_rechecks": len(rechecks), "n_self_contradiction": len(selfc), "n_reverify_calls": len(confirms),
        "reverify_deviations": [{"cycle": c["cycle"], "status": c.get("recheck_confirm_overall_status"),
                                 "all_prior": c.get("recheck_confirm_all_prior_issues_resolved"),
                                 "deviations": c.get("recheck_confirm_deviations"),
                                 "prior_issues_resolved": c.get("recheck_confirm_prior_issues_resolved")} for c in confirms],
        "recheck_unresolved_reasons": unresolved_reasons, "formal_resolution_items": formal,
        "n_merges": len(merges), "merges": merges, "merged_stage2": merged_stage2,
        "reverify_deviation_without_major": any(c.get("reverify_deviation_without_major") for c in cyc),
        "rewrite_executed": executed, "cost_jpy": d.get("total_cost_jpy"),
        "before_after_pairs_n": [c.get("recheck_before_after_pairs_n") for c in rechecks],
        "recheck_call_prompt": [{"label": cl.get("label"), "ba_len": cl.get("before_after_block_len"),
                                 "sha": (cl.get("prompt_sha256") or "")[:12]}
                                for cl in d.get("call_log", []) if cl.get("recovery_stage") == "stage1_recheck"],
        "residual_unflagged": [x.get("sub_id") for x in (d.get("residual_at_pass") or {}).get("defs", [])
                               if x.get("pass_with_residual_unflagged")],
    }


def run_agg():
    n = 2
    os.makedirs(OUT_DIR, exist_ok=True)
    per = []
    for cfg in CONFIGS:
        for s in range(1, n + 1):
            for iid in IDS:
                d = _load(f"{OUT_DIR}/instances_{cfg}_s{s}/{iid}.json")
                if d is None:
                    per.append({"config": cfg, "sample": s, "instance_id": iid, "missing": True})
                    continue
                per.append({"config": cfg, "sample": s, "instance_id": iid, **run_summary(d)})
    tot = {}
    for cfg in CONFIGS:
        rows = [r for r in per if r["config"] == cfg and not r.get("missing")]
        nr = sum(r["n_rechecks"] for r in rows)
        sc = sum(r["n_self_contradiction"] for r in rows)
        tot[cfg] = {
            "n_runs": len(rows), "missing_runs(例外相当)": sum(1 for r in per if r["config"] == cfg and r.get("missing")),
            "n_rechecks": nr, "n_self_contradiction": sc, "self_contradiction_rate": round(sc / nr, 4) if nr else None,
            "reverify_calls": sum(r["n_reverify_calls"] for r in rows),
            "formal_resolution_items": sum(len(r["formal_resolution_items"]) for r in rows),
            "stage4_unified": sum(1 for r in rows if r["final_state"] == "STAGE4_ESCALATION")
                              + sum(1 for r in per if r["config"] == cfg and r.get("missing")),
            "stage4_reasons": dict(collections.Counter(r["stage4_reason"] for r in rows if r["final_state"] == "STAGE4_ESCALATION")),
            "unnecessary_rewrite_runs(NORMAL群)": sum(1 for r in rows if r["rewrite_executed"]),
            "n_merges": sum(r["n_merges"] for r in rows), "cycles_ge2": sum(1 for r in rows if r["n_cycles"] >= 2),
            "cost_total": round(sum(r["cost_jpy"] or 0 for r in rows), 4),
            "cost_worst": max((r["cost_jpy"] or 0 for r in rows), default=None),
            "residual_unflagged": sum(len(r["residual_unflagged"]) for r in rows),
        }
    A, B = tot["A"], tot["B"]
    criteria = {
        "lower_self_contradiction": (A["self_contradiction_rate"] is not None and B["self_contradiction_rate"] is not None
                                     and B["self_contradiction_rate"] < A["self_contradiction_rate"]),
        "a_formal_resolution_zero_in_B": B["formal_resolution_items"] == 0,
        "b_stage4_not_increased": B["stage4_unified"] <= A["stage4_unified"],
        "b_miss_not_increased": B["residual_unflagged"] <= A["residual_unflagged"],
        "complete_8_runs": A["n_runs"] == 4 and B["n_runs"] == 4,
    }
    criteria["N3_adopt"] = all(criteria.values())
    S = {"per_run": per, "totals": tot, "criteria": criteria}
    with open(f"{OUT_DIR}/summary_ab_01.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    lines = ["# summary_ab_01.md (rep28a、委任_06 A/B)", "", f"totals={json.dumps(tot, ensure_ascii=False)}",
             f"criteria={json.dumps(criteria)}", ""]
    for r in per:
        if r.get("missing"):
            lines.append(f"- {r['config']} s{r['sample']} {r['instance_id']}: MISSING")
            continue
        lines.append(f"- {r['config']} s{r['sample']} {r['instance_id']}: {r['final_state']} s4={r['stage4_reason']} cycles={r['n_cycles']} "
                     f"recheck={r['n_rechecks']} selfcontra={r['n_self_contradiction']} reverify={r['n_reverify_calls']} "
                     f"merges={r['n_merges']} rewrite={r['rewrite_executed']} JPY{r['cost_jpy']}")
        for u in r["recheck_unresolved_reasons"]:
            lines.append(f"    unresolved(c{u['cycle']} idx{u['index']}): {u['explanation']}")
        for fo in r["formal_resolution_items"]:
            lines.append(f"    FORMAL(c{fo['cycle']} idx{fo['index']}): orig still in text: {fo['orig']}")
        for rv in r["reverify_deviations"]:
            lines.append(f"    reverify(c{rv['cycle']}) status={rv['status']} all_prior={rv['all_prior']} deviations={json.dumps(rv['deviations'], ensure_ascii=False)}")
        for m in r["merges"]:
            lines.append(f"    merge(c{m['cycle']}): {json.dumps({k: m.get(k) for k in ('decision','source','merged_from','n_merged','n_dedup_dropped','reverify_deviation_without_major')}, ensure_ascii=False)}")
        for ms in r["merged_stage2"]:
            lines.append(f"    merged->stage2(next): {json.dumps(ms, ensure_ascii=False)}")
    with open(f"{OUT_DIR}/summary_ab_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({"totals": tot, "criteria": criteria}, ensure_ascii=True, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=10.0)
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg()
        return
    run_main(args.budget_jpy, args.n)


if __name__ == "__main__":
    main()
