# -*- coding: utf-8 -*-
# rep28(委任_04)集計。API呼び出しなし(¥0)。記録済みinstance JSONの読み取りと、説明文混入・照合の
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


def _iter7_paths(iid):
    d = "er052_output/open233_self_recovery_flow_runner_01_iter7"
    ps = [f"{d}/instances_s{i}/{iid}.json" for i in (1, 2)] + [f"{d}/instances/{iid}.json"]
    return [p for p in ps if os.path.exists(p)]


def _rep23_paths(iid):
    d = "er052_output/open233_self_recovery_flow_runner_01_rep23"
    return [p for p in [f"{d}/instances_s{i}/{iid}.json" for i in (1, 2)] if os.path.exists(p)]


def run_agg_base():
    import er052_open233_self_recovery_flow_runner_01_rep28_full_01 as full
    out_dir = full.OUT_DIR_REP28
    instance_ids = full.ALL_IDS
    baselines = {iid: ("iter7", _iter7_paths(iid)) for iid in instance_ids}
    rep23_b = {iid: ("rep23", _rep23_paths(iid)) for iid in instance_ids if _rep23_paths(iid)}
    runner.VS_MATCH_EXT = True
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
    r23_runs = []
    for iid, (tag, paths) in rep23_b.items():
        for p in paths:
            d = _load(p)
            if d:
                r23_runs.append((tag, iid, d))

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
    S["totals_rep28"] = tot(S["per_run"])
    S["totals_baseline"] = tot(S["per_run_baseline"])
    S["per_run_rep23"] = []
    for tag, iid, d in r23_runs:
        m = run_metrics(d)
        m.update({"baseline": tag, "instance_id": iid})
        S["per_run_rep23"].append(m)
    S["totals_rep23_ref"] = tot(S["per_run_rep23"])
    S["totals_by_instance"] = {iid: {"rep28": tot([m for m in S["per_run"] if m["instance_id"] == iid]),
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

    # --- 追加(委任_63) ---
    S["per_run_cost"] = [{"sample": m["sample"], "instance_id": m["instance_id"], "cost_jpy": m["cost_jpy"],
                          "final_state": m["final_state"], "stage4_reason": m["stage4_reason"]} for m in S["per_run"]]
    # 5. STAGE4 instance別 (rep24 vs iter7)
    S["stage4_by_instance"] = {iid: {"rep28": [m["stage4_reason"] or m["final_state"] for m in S["per_run"] if m["instance_id"] == iid],
                                     "iter7": [m["stage4_reason"] or m["final_state"] for m in S["per_run_baseline"] if m["instance_id"] == iid]}
                               for iid in instance_ids}
    # 1. Safety-critical 5
    sc = {}
    for s_, iid, d in runs:
        if iid in full.SAFETY_CRITICAL_5:
            blk = [(c["cycle"], sr.get("claim_text")) for c in d.get("cycles", []) for sr in c.get("stage2_results", []) if sr.get("materiality") == "BLOCKING"]
            sc.setdefault(iid, []).append({"sample": s_, "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
                                           "n_blocking_claims": len(blk), "blocking_claims": [f"c{cy}:{(t or '')[:100]}" for cy, t in blk]})
    S["item1_safety_critical5_runs"] = sc
    # residual_at_pass 全件 (全def・全run) と残存あり
    S["item1_residual_remaining"] = [x for x in item1 if x["remains_in_final_en"]]
    # 6. P採用 全件
    p_rows = []
    for s_, iid, d in runs:
        for c in d.get("cycles", []):
            for rr in c.get("rewrite_records", []):
                res = (rr.get("handoff") or {}).get("resolution") or {}
                es = res.get("explain_split")
                if es is not None or str(res.get("level") or "").startswith("P:"):
                    p_rows.append({"sample": s_, "instance_id": iid, "cycle": c["cycle"], "status": res.get("status"), "level": res.get("level"),
                                   "explain_split": es, "ranges": res.get("ranges"), "claim": (rr.get("claim_text") or rr.get("claim") or "")})
    S["item6_recorded_explain_split_rows"] = p_rows
    # 8. JA/title
    S["item8_summary"] = {"n_runs": len(item8), "ja_changed": sum(1 for x in item8 if x["ja_changed"]),
                          "ja_labelled_calls": sum(len(x["ja_labelled_calls"]) for x in item8),
                          "paired": sum(len(x["paired_mechanisms"]) for x in item8),
                          "en_title_rewritten": sum(1 for x in item8 if x.get("en_title_rewritten")),
                          "fired_cycles": sum(1 for x in item8 for pc in x["per_cycle"] if pc["fired"]),
                          "fired_and_recheck": sum(1 for x in item8 for pc in x["per_cycle"] if pc["fired"] and pc["recheck_performed"]),
                          "switches_distinct": [json.dumps(x["switches"], sort_keys=True, default=str) for x in item8][:1]}
    # 9
    S["item9_summary"] = {"cycles_ge2": sum(1 for x in item9 if x["n_cycles"] >= 2), "cycles_ge3": sum(1 for x in item9 if x["n_cycles"] >= 3),
                          "severity_wobble": sum(x["severity_wobble_n"] for x in item9),
                          "carry_forward_comparison": sum(x["carry_forward_comparison_n"] for x in item9),
                          "carry_forward_covered": sum(x["carry_forward_covered_n"] for x in item9)}
    # BLOCKING claim 全件 (blocking_claims_01.md)
    bl = ["# blocking_claims_01.md (rep28、委任_04)", "", "全BLOCKING claim(cycle別)。仮ラベルはFable照合用にREPORTへ別記。", ""]
    for s_, iid, d in runs:
        for c in d.get("cycles", []):
            for sr in c.get("stage2_results", []):
                if sr.get("materiality") == "BLOCKING":
                    bl.append(f"- s{s_} {iid} c{c['cycle']} llm={sr.get('llm_materiality')} floor={sr.get('floor_reason')} origin={sr.get('origin')} "
                              f"issue={str(sr.get('issue') or '')[:160]!r}  " + chr(10) + f"  claim: {sr.get('claim_text')}")
    with open(f"{out_dir}/blocking_claims_01.md", "w", encoding="utf-8") as f:
        f.write(chr(10).join(bl) + chr(10))
    # summary_01.md
    t = S["totals_rep28"]
    md = ["# summary_01.md (rep28、委任_04)", "", f"n instance-run={t['n_runs']} cost=JPY{t['cost_jpy_total']} worst=JPY{t['cost_jpy_worst']}",
          f"stage2_blocking={t['stage2_blocking']} floor_only_blocking={t['floor_only_blocking']} by_flag={t['floor_only_by_flag']}",
          f"unnecessary_rewrite(normal group)={t['unnecessary_rewrite_def_normal_group']}",
          f"runs_with_rewrite_nonsafety={t['runs_with_rewrite_nonsafety']} rewrite_executed={t['rewrite_executed']}",
          f"stage4={t['stage4_count']} reasons={t['stage4_reasons']}", f"floor_verify={S['item2_floor_verify_summary']}",
          f"item8={S['item8_summary']}", f"item9={S['item9_summary']}",
          f"iter7 totals={json.dumps(S['totals_baseline'], ensure_ascii=False)}", f"rep23 totals={json.dumps(S['totals_rep23_ref'], ensure_ascii=False)}", "",
          "## per run", ""]
    for x in S["per_run_cost"]:
        md.append(f"- s{x['sample']} {x['instance_id']}: {x['final_state']} s4={x['stage4_reason']} JPY{x['cost_jpy']}")
    with open(f"{out_dir}/summary_01.md", "w", encoding="utf-8") as f:
        f.write(chr(10).join(md) + chr(10))

    S["cost_total_jpy"] = S["totals_rep28"]["cost_jpy_total"]
    os.makedirs(out_dir, exist_ok=True)
    with open(f"{out_dir}/summary_01.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)

    # release_log_01.md
    lines = ["# release_log_01.md (rep28、委任_04)", "",
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
    print(json.dumps({k: S[k] for k in ("totals_rep28", "totals_baseline", "item1_pass_with_residual_unflagged_count",
                                         "item2_floor_verify_summary", "item67_recorded_resolution_levels",
                                         "item67_recorded_unresolved_reasons", "cost_total_jpy")}, ensure_ascii=True, indent=1))


# ---------------------------------------------------------------- 委任_04: KPI判定用の追加集計(API呼び出しなし)
def _runs_in(dirpath, ids):
    out = []
    for s in (1, 2):
        for iid in ids:
            d = _load(f"{dirpath}/instances_s{s}/{iid}.json")
            if d:
                out.append((s, iid, d))
    return out


def _iter7_runs(ids):
    out = []
    for iid in ids:
        for p in _iter7_paths(iid):
            d = _load(p)
            if d:
                out.append((p, iid, d))
    return out


def _executed_rewrites_ladder(d):
    return sum(1 for c in d.get("cycles", []) for rr in c.get("rewrite_records", []) if rr.get("ladder_level_used"))


def _rewrite_stats(runs):
    n_exec = 0
    runs_with = 0
    for _s, _iid, d in runs:
        e = _executed_rewrites_ladder(d)
        n_exec += e
        runs_with += 1 if e else 0
    return {"n_runs": len(runs), "rewrite_executed_total": n_exec, "runs_with_rewrite": runs_with}


def run_agg():
    import er052_open233_self_recovery_flow_runner_01_rep28_full_01 as full
    run_agg_base()
    ids = full.ALL_IDS
    cur = _runs_in(full.OUT_DIR_REP28, ids)
    r24 = _runs_in(full.REP24_DIR, ids)
    it7 = _iter7_runs(ids)
    inst = [d for _s, _i, d in cur]
    K = {"n_runs": len(cur)}
    # --- Human Review / 見逃し
    s4 = [(s, iid, d.get("stage4_reason")) for s, iid, d in cur if d.get("final_state") == "STAGE4_ESCALATION"]
    K["stage4"] = {"count": len(s4), "rows": s4,
                   "rep24_count": sum(1 for _s, _i, d in r24 if d.get("final_state") == "STAGE4_ESCALATION"),
                   "iter7_count": sum(1 for _s, _i, d in it7 if d.get("final_state") == "STAGE4_ESCALATION")}
    K["safety_critical_dual"] = runner.safety_critical_dual_summary(inst)
    K["safety_critical_registered_rows"] = runner.detect_safety_critical_misdowngrades(inst)
    K["pass_with_residual_unflagged"] = [(s, iid, x.get("sub_id")) for s, iid, d in cur
                                         for x in (d.get("residual_at_pass") or {}).get("defs", []) if x.get("pass_with_residual_unflagged")]
    # --- Safety-critical 6件
    sc6 = {}
    for s, iid, d in cur:
        if iid in full.SAFETY_CRITICAL_6:
            blk = []
            t0 = []
            for c in d.get("cycles", []):
                for sr in c.get("stage2_results", []):
                    if sr.get("materiality") == "BLOCKING":
                        blk.append({"cycle": c["cycle"], "llm": sr.get("llm_materiality"), "floor": sr.get("floor_reason"),
                                    "claim": (sr.get("claim_text") or "")[:100]})
                    t = sr.get("tier0") or {}
                    if t.get("blocked"):
                        t0.append({"cycle": c["cycle"], "reason": t.get("reason"), "claim": (sr.get("claim_text") or "")[:80]})
            rap = d.get("residual_at_pass") or {}
            sc6.setdefault(iid, []).append({
                "sample": s, "sub_id": full.SAFETY_CRITICAL_6[iid], "final_state": d.get("final_state"),
                "stage1_call_used": d.get("stage1_call_used"), "stage1_recall_miss_substituted": d.get("stage1_recall_miss_substituted"),
                "n_blocking": len(blk), "blocking": blk, "tier0_blocked": t0,
                "residual_defs": [(x.get("sub_id"), x.get("remains_in_final_en"), x.get("ever_blocking_flagged"),
                                   x.get("pass_with_residual_unflagged")) for x in rap.get("defs", [])]})
    K["safety_critical6"] = sc6
    # --- Tier 0 / S1
    K["tier0"] = runner.tier0_summarize(inst)
    K["s1"] = runner.s1_summarize(inst)
    # --- 不要Rewrite
    K["rewrite"] = {"rep28": _rewrite_stats(cur), "rep24": _rewrite_stats(r24), "iter7": _rewrite_stats(it7)}

    def nm(runs):
        return {"n_normal": sum(1 for _s, i, _d in runs if i in NORMAL_IDS),
                "normal_with_rewrite": sum(1 for _s, i, d in runs if i in NORMAL_IDS and _executed_rewrites_ladder(d))}
    K["unnecessary_rewrite_normal_group"] = {"rep28": nm(cur), "rep24": nm(r24), "iter7": nm(it7)}

    # --- 過剰Major(Stage 2 BLOCKING)
    def blk(runs):
        tot_b = floor_b = 0
        for _s, _i, d in runs:
            for c in d.get("cycles", []):
                for sr in c.get("stage2_results", []):
                    if sr.get("materiality") == "BLOCKING":
                        tot_b += 1
                        floor_b += 1 if sr.get("llm_materiality") != "BLOCKING" else 0
        return {"stage2_blocking": tot_b, "floor_only_blocking": floor_b}
    K["blocking"] = {"rep28": blk(cur), "rep24": blk(r24), "iter7": blk(it7)}
    # --- L6/P/Q・prior_issues・partial overlap・cycles
    K["l6"] = runner.sentence_restore_summarize(inst)
    es = []
    po = []
    pi_cur = 0
    pi_total = 0
    for s, iid, d in cur:
        for c in d.get("cycles", []):
            for src in c.get("prior_issue_text_sources") or []:
                pi_total += 1
                pi_cur += 1 if src == runner.PRIOR_ISSUE_TEXT_SOURCE_CURRENT else 0
            for rr in c.get("rewrite_records", []):
                h = rr.get("handoff") or {}
                res = h.get("resolution") or {}
                if res.get("explain_split") is not None or str(res.get("level") or "").startswith("P:"):
                    es.append({"sample": s, "iid": iid, "cycle": c["cycle"], "level": res.get("level"), "status": res.get("status")})
                if any(x.get("partial_overlap") for x in (h.get("carry_forward_covered") or [])):
                    po.append({"sample": s, "iid": iid, "cycle": c["cycle"], "claim": rr.get("claim_identity")})
    K["explain_split_P_rows"] = es
    K["partial_overlap_carry_forward"] = po
    K["prior_issues"] = {"records": pi_total, "current_text": pi_cur}
    K["cycles"] = {"ge2": sum(1 for _s, _i, d in cur if len(d.get("cycles", [])) >= 2),
                   "ge3": sum(1 for _s, _i, d in cur if len(d.get("cycles", [])) >= 3)}
    K["ja_changed"] = sum(1 for _s, _i, d in cur if any("ja_text_after_rewrite" in c for c in d.get("cycles", [])))

    # --- 費用
    def cost(runs):
        return [d.get("total_cost_jpy") or 0.0 for _s, _i, d in runs]
    c27, c24, c7 = cost(cur), cost(r24), cost(it7)

    def mean(xs):
        return round(sum(xs) / len(xs), 4) if xs else None

    def per_inst_mean(runs):
        m = collections.defaultdict(list)
        for _s, i, d in runs:
            m[i].append(d.get("total_cost_jpy") or 0.0)
        return {i: sum(v) / len(v) for i, v in m.items()}
    b24, b7 = per_inst_mean(r24), per_inst_mean(it7)
    adds24 = [(s, iid, round((d.get("total_cost_jpy") or 0.0) - b24[iid], 4)) for s, iid, d in cur if iid in b24]
    adds7 = [(s, iid, round((d.get("total_cost_jpy") or 0.0) - b7[iid], 4)) for s, iid, d in cur if iid in b7]
    K["cost"] = {
        "rep28_total": round(sum(c27), 4), "rep28_mean_per_run": mean(c27), "rep28_worst_run": max(c27) if c27 else None,
        "rep24_total": round(sum(c24), 4), "rep24_mean_per_run": mean(c24), "iter7_total": round(sum(c7), 4), "iter7_mean_per_run": mean(c7),
        "avg_add_per_article_vs_rep24_mean": round(mean(c27) - mean(c24), 4) if c24 else None,
        "avg_add_per_article_vs_iter7_mean": round(mean(c27) - mean(c7), 4) if c7 else None,
        "avg_add_matched_instance_vs_rep24": mean([a for _s, _i, a in adds24]),
        "avg_add_matched_instance_vs_iter7": mean([a for _s, _i, a in adds7]),
        "worst_add_vs_rep24_instance_mean": max(adds24, key=lambda x: x[2]) if adds24 else None,
        "worst_add_vs_iter7_instance_mean": max(adds7, key=lambda x: x[2]) if adds7 else None,
        "runs_over_cap_plus3_vs_rep24": [x for x in adds24 if x[2] > 3.0],
        "runs_over_cap_plus3_vs_iter7": [x for x in adds7 if x[2] > 3.0]}
    K["switches"] = (cur[0][2].get("switches") if cur else None)
    K["models"] = {"rubric": "V7b (RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B)",
                   "call_models": sorted({str(cl.get("model")) for _s, _i, d in cur for cl in d.get("call_log", []) if cl.get("model")})}
    K["models"]["runner_MODEL(Checker/Stage 2/Rewrite等の既定モデルID、runner定数)"] = runner.MODEL
    # --- 委任_06: 統一Human Review定義(`stage4_reason`全種+例外終了=instance JSONが残らないrun) ---
    expected_runs = len(full.N2_IDS) * 2 + len(full.N1_IDS)
    run_log = _load(f"{full.OUT_DIR_REP28}/run_log_main.json") or {}
    exc = run_log.get("exceptions") or []
    missing = expected_runs - len(cur)
    K["human_review_unified"] = {"stage4": len(s4), "stage4_by_reason": dict(collections.Counter(r for _s, _i, r in s4)),
                                 "exception_runs(run_log exceptions)": len(exc), "missing_runs(expected-found)": missing,
                                 "stopped": run_log.get("stopped"), "stop_reason": run_log.get("stop_reason"),
                                 "total": len(s4) + max(len(exc), missing)}
    # --- 委任_06: rep27比・移動監視・N1′/N3′の発火 ---
    r27 = _runs_in(full.REP27_DIR, ids)
    K["vs_rep27"] = {"stage4_rep27": [(s, i, d.get("stage4_reason")) for s, i, d in r27 if d.get("final_state") == "STAGE4_ESCALATION"],
                     "cost_rep27_total": round(sum(cost(r27)), 4)}
    watch = ("same_claim_fact_id_reblocked", "cycle_limit_exhausted", "cycle_limit_exhausted_after_recheck",
             "unconfirmed_after_reverify", "ladder_exhausted_without_full_rewrite", "violation_span_unverified")
    K["stage4_move_watch"] = {w: sum(1 for _s, _i, r in s4 if r == w) for w in watch}
    merges, rv_calls, selfc, rechecks, rv_nomajor, ba_used = [], 0, 0, 0, [], 0
    formal = []
    for s, iid, d in cur:
        cy = d.get("cycles", [])
        for i, c in enumerate(cy):
            if c.get("recheck_overall_status") is not None:
                rechecks += 1
                if c.get("recheck_overall_status") == "LEDGER_COMPLIANT" and c.get("recheck_all_prior_issues_resolved") is False:
                    selfc += 1
            if c.get("recheck_confirm_overall_status") is not None:
                rv_calls += 1
            if c.get("recheck_merge") and c["recheck_merge"].get("n_merged"):
                nxt = [(sr.get("materiality"), (sr.get("claim_text") or "")[:80]) for sr in (cy[i + 1].get("stage2_results", []) if i + 1 < len(cy) else [])]
                merges.append({"sample": s, "instance_id": iid, "cycle": c["cycle"], "merged_from": c["recheck_merge"].get("merged_from"),
                               "next_cycle_stage2": nxt, "final_state": d.get("final_state")})
            if c.get("reverify_deviation_without_major"):
                rv_nomajor.append((s, iid, c["cycle"], d.get("final_state")))
            if c.get("recheck_before_after_pairs_n"):
                ba_used += 1
    K["n1_prime"] = {"rechecks": rechecks, "self_contradictions": selfc, "reverify_calls": rv_calls,
                     "merge_events": len(merges), "merges": merges, "reverify_deviation_without_major": rv_nomajor,
                     "n3_prime_recheck_with_pairs": ba_used}
    unified_zero = K["human_review_unified"]["total"] == 0
    kpi = {"primary_human_review_zero": unified_zero,
           "safety_zero_old": K["safety_critical_dual"].get("old_definition_rows", 0) == 0 and not K["pass_with_residual_unflagged"],
           "safety_zero_new": K["safety_critical_dual"].get("new_definition_rows", 0) == 0,
           "cost_avg_add_le_2_vs_rep24": (K["cost"]["avg_add_per_article_vs_rep24_mean"] is not None
                                          and K["cost"]["avg_add_per_article_vs_rep24_mean"] <= 2.0),
           "cost_avg_add_le_2_vs_iter7": (K["cost"]["avg_add_per_article_vs_iter7_mean"] is not None
                                          and K["cost"]["avg_add_per_article_vs_iter7_mean"] <= 2.0),
           "cap_worst_add_le_3_vs_rep24": not K["cost"]["runs_over_cap_plus3_vs_rep24"],
           "cap_worst_add_le_3_vs_iter7": not K["cost"]["runs_over_cap_plus3_vs_iter7"]}
    K["kpi"] = kpi
    out_dir = full.OUT_DIR_REP28
    with open(f"{out_dir}/summary_kpi_01.json", "w", encoding="utf-8") as f:
        json.dump(K, f, ensure_ascii=False, indent=2, default=str)
    print("=== KPI summary ===")
    print(json.dumps(K, ensure_ascii=True, indent=1, default=str)[:14000])
