# -*- coding: utf-8 -*-
# rep23(委任_62)集計。API呼び出しなし(¥0)。記録済みinstance JSONの読み取りと、説明文混入・照合の
# 決定論replay(runner.vs_explain_split_resolve/_resolve_claim_string、¥0)のみ。runner本体は変更しない。
from __future__ import annotations

import collections
import json
import os

import er052_open233_self_recovery_flow_runner_01 as runner

NORMAL_IDS = runner.NORMAL_GROUP_INSTANCE_IDS
SAFETY_IDS = {"safety_A4", "safety_A2A3", "safety_er009_changed_number"}


def _load(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _executed_rewrites(r):
    return [rr for c in r.get("cycles", []) for rr in c.get("rewrite_records", [])
            if rr.get("ladder_level_used") or str(rr.get("method", "")).startswith(("e1_", "e2_", "e3_", "delete"))]


def _all_rewrite_records(r):
    return [(c["cycle"], rr) for c in r.get("cycles", []) for rr in c.get("rewrite_records", [])]


def run_metrics(r):
    s2 = [(c["cycle"], sr) for c in r.get("cycles", []) for sr in c.get("stage2_results", [])]
    blocking = [(cy, sr) for cy, sr in s2 if sr.get("materiality") == "BLOCKING"]
    floor_only = [(cy, sr) for cy, sr in blocking if sr.get("llm_materiality") != "BLOCKING"]
    fl_flag = collections.Counter(str(sr.get("floor_reason")) for _cy, sr in floor_only)
    floor_applied_any = [(cy, sr) for cy, sr in s2 if str(sr.get("floor_reason") or "").startswith(("deterministic_floor", "precheck_floor"))]
    recs = _all_rewrite_records(r)
    executed = [rr for _cy, rr in recs if rr.get("ladder_level_used")]
    return {
        "final_state": r.get("final_state"), "stage4_reason": r.get("stage4_reason"),
        "n_cycles": len(r.get("cycles", [])), "cost_jpy": r.get("total_cost_jpy"),
        "n_stage2_claims": len(s2), "n_stage2_blocking": len(blocking),
        "n_floor_only_blocking": len(floor_only), "floor_only_by_flag": dict(fl_flag),
        "n_floor_applied_claims": len(floor_applied_any),
        "n_rewrite_executed": len(executed), "has_rewrite": bool(executed),
        "n_rewrite_records_total": len(recs),
        "is_stage4": r.get("final_state") == "STAGE4_ESCALATION",
    }


def _en_text_for_cycle(r, fixture_en, idx):
    cycles = r.get("cycles", [])
    if idx == 0:
        return fixture_en
    prev = cycles[idx - 1]
    return prev.get("en_text_after_rewrite") or prev.get("en_text_before_rewrite") or fixture_en


def explain_split_replay(r, fixture_en):
    """各cycleのBLOCKING claimの照合を、記録された本文(cycle1=fixture、以降=前cycleのRewrite後)に対して決定論replay。
    記録されたhandoffの結果(status/level)との一致も確認する。"""
    rows = []
    for ci, c in enumerate(r.get("cycles", [])):
        en = _en_text_for_cycle(r, fixture_en, ci)
        for sr in c.get("stage2_results", []):
            if sr.get("materiality") != "BLOCKING":
                continue
            claim = sr.get("claim_text") or ""
            base = runner._resolve_claim_string_base(claim, en, None)
            full = runner._resolve_claim_string(claim, en, None)
            es = full.get("explain_split")
            row = {"cycle": c["cycle"], "claim_text": claim, "base_status": base["status"], "base_reason": base.get("reason"),
                   "base_level": base.get("level"), "final_status": full["status"], "final_level": full.get("level"),
                   "final_reason": full.get("reason"), "ranges": full.get("ranges")}
            if es is not None:
                row["explain_split"] = {"attempted": es.get("attempted"), "status": es.get("status"), "reason": es.get("reason"),
                                        "fragments": es.get("fragments"), "dropped_remainders": es.get("dropped_remainders")}
            rows.append(row)
    return rows


def run_agg(out_dir, instance_ids, baselines):
    runner.VS_MATCH_EXT = True      # replay(¥0)で実flowと同じ照合設定にする
    runner.VS_EXPLAIN_SPLIT = True
    fixtures = {i["instance_id"]: i["fixture"]["article_text"] for i in runner.build_target_instances()}
    runs = []
    for s in (1, 2):
        for iid in instance_ids:
            d = _load(f"{out_dir}/instances_s{s}/{iid}.json")
            if d:
                runs.append((s, iid, d))
    base_runs = []
    base_src = {}
    for iid in instance_ids:
        tag, paths = baselines[iid]
        base_src[iid] = {"tag": tag, "paths": paths}
        for p in paths:
            d = _load(p)
            if d:
                base_runs.append((tag, iid, d))

    S = {"n_runs": len(runs), "baseline_sources": base_src, "per_run": [], "per_run_baseline": []}
    for s, iid, d in runs:
        m = run_metrics(d)
        m.update({"sample": s, "instance_id": iid})
        S["per_run"].append(m)
    for tag, iid, d in base_runs:
        m = run_metrics(d)
        m.update({"baseline": tag, "instance_id": iid})
        S["per_run_baseline"].append(m)

    def tot(rows):
        n = len(rows)
        normal = [m for m in rows if m["instance_id"] in NORMAL_IDS]
        return {
            "n_runs": n,
            "stage2_blocking": sum(m["n_stage2_blocking"] for m in rows),
            "floor_only_blocking": sum(m["n_floor_only_blocking"] for m in rows),
            "floor_only_by_flag": dict(sum((collections.Counter(m["floor_only_by_flag"]) for m in rows), collections.Counter())),
            "rewrite_executed": sum(m["n_rewrite_executed"] for m in rows),
            "runs_with_rewrite": sum(1 for m in rows if m["has_rewrite"]),
            "unnecessary_rewrite_def_normal_group": {
                "definition": "NORMAL_GROUP_INSTANCE_IDS(正常記事)のinstance-runのうちRewriteが1件以上実行されたrunの割合(既存runner定義)",
                "n_normal_runs": len(normal), "n_with_rewrite": sum(1 for m in normal if m["has_rewrite"]),
                "rate": round(sum(1 for m in normal if m["has_rewrite"]) / len(normal), 4) if normal else None},
            "runs_with_rewrite_nonsafety": {"n": len([m for m in rows if m["instance_id"] not in SAFETY_IDS]),
                                             "with_rewrite": sum(1 for m in rows if m["instance_id"] not in SAFETY_IDS and m["has_rewrite"])},
            "stage4_count": sum(1 for m in rows if m["is_stage4"]),
            "stage4_reasons": dict(collections.Counter(m["stage4_reason"] for m in rows if m["is_stage4"])),
            "cycles_ge2_runs": sum(1 for m in rows if m["n_cycles"] >= 2),
            "cycles_ge3_runs": sum(1 for m in rows if m["n_cycles"] >= 3),
            "cost_jpy_total": round(sum(m["cost_jpy"] or 0 for m in rows), 4),
            "cost_jpy_worst": max((m["cost_jpy"] or 0) for m in rows) if rows else None,
        }
    S["totals_rep23"] = tot(S["per_run"])
    S["totals_baseline"] = tot(S["per_run_baseline"])
    S["totals_by_instance"] = {iid: {"rep23": tot([m for m in S["per_run"] if m["instance_id"] == iid]),
                                     "baseline": tot([m for m in S["per_run_baseline"] if m["instance_id"] == iid]),
                                     "baseline_tag": baselines[iid][0]} for iid in instance_ids}

    # 1. Safety-critical / residual_at_pass
    item1 = []
    for s, iid, d in runs:
        rap = d.get("residual_at_pass") or {}
        for df in rap.get("defs", []):
            item1.append({"sample": s, "instance_id": iid, "final_state": d.get("final_state"), "sub_id": df["sub_id"],
                          "remains_in_final_en": df["remains_in_final_en"], "ever_blocking_flagged": df["ever_blocking_flagged"],
                          "ever_blocking_flagged_same_fact_id": df["ever_blocking_flagged_same_fact_id"],
                          "pass_with_residual_unflagged": df["pass_with_residual_unflagged"],
                          "final_state_is_pass_family": rap.get("final_state_is_pass_family")})
    S["item1_safety_critical_defs"] = item1
    S["item1_pass_with_residual_unflagged_count"] = sum(1 for x in item1 if x["pass_with_residual_unflagged"])
    S["item1_safety_critical_misdowngrades"] = runner.detect_safety_critical_misdowngrades([d for _s, _i, d in runs])

    # 2. floor_verify
    fv_rows = []
    for s, iid, d in runs:
        for c in d.get("cycles", []):
            for sr in c.get("stage2_results", []):
                fv = sr.get("floor_verify")
                if fv:
                    fv_rows.append({"sample": s, "instance_id": iid, "cycle": c["cycle"], "claim_text": sr.get("claim_text"),
                                    "floor_reason": sr.get("floor_reason"), "materiality_final": sr.get("materiality"), **fv})
    S["item2_floor_verify_summary"] = runner.floor_verify_summarize(
        sr for _s, _i, d in runs for c in d.get("cycles", []) for sr in c.get("stage2_results", []))
    S["item2_floor_verify_records"] = fv_rows
    S["item2_released"] = [x for x in fv_rows if x.get("released")]

    # 6/7. 照合
    replay_all = []
    levels = collections.Counter()
    reasons = collections.Counter()
    for s, iid, d in runs:
        for c in d.get("cycles", []):
            for rr in c.get("rewrite_records", []):
                res = (rr.get("handoff") or {}).get("resolution") or {}
                levels[str(res.get("level"))] += 1
                if res.get("status") != "resolved":
                    reasons[f"{res.get('status')}:{res.get('reason')}"] += 1
        for row in explain_split_replay(d, fixtures[iid]):
            row.update({"sample": s, "instance_id": iid})
            replay_all.append(row)
    S["item67_recorded_resolution_levels"] = dict(levels)
    S["item67_recorded_unresolved_reasons"] = dict(reasons)
    S["item6_replay_rows"] = replay_all
    S["item6_p_fired_in_replay"] = [x for x in replay_all if str(x.get("final_level") or "").startswith("P:")]
    S["item6_explain_split_attempted_in_replay"] = [x for x in replay_all if x.get("explain_split")]
    S["item7_l5_resolved_in_replay"] = [x for x in replay_all if x.get("base_level") == "L5_edge_punct" or x.get("final_level") == "L5_edge_punct"]
    S["item7_label_only_in_replay"] = [x for x in replay_all if x.get("base_reason") == "label_only"]
    S["item7_recorded_l5_in_handoffs"] = levels.get("L5_edge_punct", 0)

    # 8. JA
    item8 = []
    for s, iid, d in runs:
        ja_changed = any("ja_text_after_rewrite" in c for c in d.get("cycles", []))
        ja_calls = [cl.get("label") for cl in d.get("call_log", []) if "ja_" in str(cl.get("label", ""))]
        paired = [rr.get("mechanism") for _cy, rr in _all_rewrite_records(d) if str(rr.get("mechanism", "")).startswith("paired")]
        per_cycle = []
        for c in d.get("cycles", []):
            reasons_c = c.get("full_recheck_required_reasons")
            fired = bool(reasons_c) and "english_only_ja_source_requires_full_recheck" in reasons_c
            did_recheck = c.get("recheck_overall_status") is not None
            ja_src_blk = any(sr.get("materiality") == "BLOCKING" and sr.get("origin") == "ja_source" for sr in c.get("stage2_results", []))
            reached_recheck_decision = c.get("full_recheck_required_reasons") is not None
            per_cycle.append({"cycle": c["cycle"], "fired": fired, "recheck_performed": did_recheck,
                              "ja_source_blocking_in_cycle": ja_src_blk, "reached_recheck_decision": reached_recheck_decision,
                              "has_rewrite_executed": any(rr.get("ladder_level_used") for rr in c.get("rewrite_records", []))})
        item8.append({"sample": s, "instance_id": iid, "switches": d.get("switches"), "ja_changed": ja_changed,
                      "ja_labelled_calls": ja_calls, "paired_mechanisms": paired,
                      "en_title_rewritten": d.get("en_title_rewritten"), "en_title_changes": d.get("en_title_changes"),
                      "per_cycle": per_cycle})
    S["item8"] = item8

    # 9. retry/recheck
    item9 = []
    for s, iid, d in runs:
        cf_cmp = 0
        cf_cov = 0
        modes = collections.Counter()
        for _cy, rr in _all_rewrite_records(d):
            h = rr.get("handoff") or {}
            modes[h.get("mode")] += 1
            if h.get("carry_forward_comparison"):
                cf_cmp += 1
            if h.get("carry_forward_covered"):
                cf_cov += 1
        cyc_info = []
        for c in d.get("cycles", []):
            floor_claims = [sr for sr in c.get("stage2_results", []) if str(sr.get("floor_reason") or "").startswith("deterministic_floor")]
            cyc_info.append({"cycle": c["cycle"], "n_stage2": len(c.get("stage2_results", [])),
                             "n_floor_claims": len(floor_claims),
                             "n_floor_claims_with_floor_verify_record": sum(1 for sr in floor_claims if sr.get("floor_verify")),
                             "recheck_status": c.get("recheck_overall_status"), "recheck_all_resolved": c.get("recheck_all_prior_issues_resolved"),
                             "full_recheck_required_reasons": c.get("full_recheck_required_reasons")})
        item9.append({"sample": s, "instance_id": iid, "n_cycles": len(d.get("cycles", [])),
                      "severity_wobble_n": len(d.get("severity_wobble") or []), "severity_wobble": d.get("severity_wobble"),
                      "carry_forward_comparison_n": cf_cmp, "carry_forward_covered_n": cf_cov,
                      "handoff_modes": dict(modes), "cycles": cyc_info})
    S["item9"] = item9

    S["cost_total_jpy"] = S["totals_rep23"]["cost_jpy_total"]
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/summary_01.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)

    # release_log_01.md
    lines = ["# release_log_01.md (rep23、委任_62)", "",
             f"floor_verify(FLOOR_VERIFY_MODE=time_only)記録: {len(fv_rows)}件(deterministic floorが発火したclaim)。",
             f"集計: {json.dumps(S['item2_floor_verify_summary'], ensure_ascii=False)}", "",
             f"解放件数: **{len(S['item2_released'])}**", ""]
    for x in fv_rows:
        lines.append(f"- s{x['sample']} {x['instance_id']} c{x['cycle']} target={x['target']} target_reason={x['target_reason']} "
                     f"triggered_flags={x.get('triggered_flags')} llm_materiality={x['llm_materiality']} n_calls={x['n_calls']} "
                     f"released={x['released']} final={x['materiality_final']} fixed_reason={x['blocking_fixed_reason']}  \n  claim: {x['claim_text']}")
    for x in S["item2_released"]:
        lines.append(f"\n## 解放 s{x['sample']} {x['instance_id']} c{x['cycle']}\n{json.dumps(x, ensure_ascii=False, indent=1)}")
    with open(f"{out_dir}/release_log_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(json.dumps({k: S[k] for k in ("totals_rep23", "totals_baseline", "item1_pass_with_residual_unflagged_count",
                                         "item2_floor_verify_summary", "item67_recorded_resolution_levels",
                                         "item67_recorded_unresolved_reasons", "cost_total_jpy")}, ensure_ascii=True, indent=1))
