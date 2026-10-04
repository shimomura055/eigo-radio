# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_rep25_affected_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_66: L6完結文復元を有効にした影響instanceの再実行 rep25、n=2固定)
# ============================================================
# rep24_full_01を複製し、instance集合をrep24でHuman Review(STAGE4 violation_span_unverified)になった2 instance
# (`safety_A2A3`・`bgroup_B3`、n=2 = 4 instance-run)に絞り、`VS_SENTENCE_RESTORE=True`を追加した。他のスイッチはrep24と同一
# (HANDOFF_MODE=violation_span / VS_MATCH_EXT / VS_EXPLAIN_SPLIT / JA_MODE=english_only / FLOOR_VERIFY_MODE=time_only /
# Stage 2 rubric V7b、MAX_CYCLES=2・HARD_MAX_CYCLES=3)。runner本体のロジックは変更しない(スイッチ設定とOUT_DIR・予算状態の切替のみ)。
# Production codeは変更しない。出力はOUT_DIR_REP25のみ。TTSなし。再実行・部分再実行・n増しはしない(既存jsonがあればskipするのみ)。
# 即時STOP: 日本語変更・重大解放(floor_verify released)・Safety-critical残存(pass_with_residual_unflagged)・例外・TrialAbort。
# 集計(--stage agg)は本ファイル内(API呼び出しなし、記録済みinstance JSONのみ)。
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

OUT_DIR_REP25 = "er052_output/open233_self_recovery_flow_runner_01_rep25"
BUDGET_STATE_REP25 = f"{OUT_DIR_REP25}/budget_state_c233aq_66_rep25.json"
REP24_DIR = "er052_output/open233_self_recovery_flow_runner_01_rep24"
INSTANCE_IDS = ["safety_A2A3", "bgroup_B3"]
SAFETY_CRITICAL_IDS = {"bgroup_B3": "B3", "safety_A2A3": "A2A3-0"}


def apply_switches(budget_jpy: float) -> None:
    runner.OUT_DIR = OUT_DIR_REP25
    runner.BUDGET_STATE_PATH = BUDGET_STATE_REP25
    runner.TOTAL_BUDGET_JPY = budget_jpy
    runner.HANDOFF_MODE = runner.HANDOFF_MODE_VIOLATION_SPAN
    runner.VS_MATCH_EXT = True
    runner.VS_EXPLAIN_SPLIT = True
    runner.VS_SENTENCE_RESTORE = True  # 委任_66(rep24との唯一の追加)
    runner.JA_MODE = runner.JA_MODE_ENGLISH_ONLY
    runner.FLOOR_VERIFY_MODE = runner.validate_floor_verify_mode(runner.FLOOR_VERIFY_MODE_TIME_ONLY)
    assert runner.MAX_CYCLES == 2 and runner.HARD_MAX_CYCLES == 3
    assert runner.BODY_RUBRIC_DEFAULT is runner.s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B


def run_main(n, budget_jpy):
    apply_switches(budget_jpy)
    os.makedirs(OUT_DIR_REP25, exist_ok=True)
    client = vfl01.get_client()
    state = runner.load_budget_state()
    consecutive_errors = [0]
    all_inst = {i["instance_id"]: i for i in runner.build_target_instances()}
    stage1_cache: dict = {}
    log = {"stopped": False, "stop_reason": None, "runs": [], "exceptions": []}
    for sample_idx in range(1, n + 1):
        subdir = f"instances_s{sample_idx}"
        for iid in INSTANCE_IDS:
            path = f"{OUT_DIR_REP25}/{subdir}/{iid}.json"
            if os.path.exists(path):
                print(f"[skip existing] {subdir}/{iid}")
                continue
            try:
                r = runner.run_instance(client, state, consecutive_errors, all_inst[iid], enable_s1u=False,
                                        stage1_cache=stage1_cache, instances_subdir=subdir)
            except runner.TrialAbort as e:
                log.update(stopped=True, stop_reason=f"TrialAbort: {e}")
                break
            except Exception as e:  # 例外は即STOP(再実行しない)
                log["exceptions"].append({"sample": sample_idx, "instance_id": iid, "error": repr(e),
                                          "tb": traceback.format_exc()[-1500:]})
                log.update(stopped=True, stop_reason=f"exception: {e!r}")
                print(f"[EXCEPTION] {subdir}/{iid}: {e!r}")
                break
            reasons = rep23.immediate_stop_check(r)
            print(f"[done] {subdir}/{iid} final={r['final_state']} s4={r.get('stage4_reason')} "
                  f"cost=JPY{r['total_cost_jpy']} cum=JPY{state['cumulative_jpy']:.3f} stop_check={reasons}", flush=True)
            log["runs"].append({"sample": sample_idx, "instance_id": iid, "final_state": r["final_state"],
                                "stage4_reason": r.get("stage4_reason"), "cost": r["total_cost_jpy"],
                                "stop_check": reasons})
            if reasons:
                log.update(stopped=True, stop_reason=f"immediate stop condition: {reasons}")
                break
        if log["stopped"]:
            break
    log["cumulative_jpy"] = round(state["cumulative_jpy"], 4)
    runner.save_json(f"{OUT_DIR_REP25}/run_log_main.json", log)
    print(json.dumps(log, ensure_ascii=True, indent=2)[:6000])


# ---------------------------------------------------------------- 集計(API呼び出しなし)
def _load(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _iter_records(d):
    for c in d.get("cycles", []):
        for rr in c.get("rewrite_records", []) or []:
            yield c, rr


def _l6_detail(d, article_before_by_cycle):
    """run内のL6復元(`level=L6:sentence_restore`)ごとに、復元文の逐語性・issueとの対応・Rewrite前後・焦点内かを集める。"""
    out = []
    for c, rr in _iter_records(d):
        h = rr.get("handoff") or {}
        res = h.get("resolution") or {}
        sr = res.get("sentence_restore") or h.get("sentence_restore")
        if not sr:
            continue
        en = article_before_by_cycle.get(c.get("cycle"))
        row = {"cycle": c.get("cycle"), "status": sr.get("status"), "reason": sr.get("reason"),
               "restore_reason": sr.get("restore_reason"), "n_sentences": sr.get("n_sentences"),
               "original_claim": sr.get("original_claim"), "restored_sentence": sr.get("restored_sentence"),
               "anchors": sr.get("anchors"), "residual_check": sr.get("residual_check"),
               "issue_focus_check": h.get("issue_focus_check"), "issue_focus_absent": bool(h.get("issue_focus_absent")),
               "focus_guard_fired": bool(h.get("focus_guard_fired")), "method": rr.get("method"),
               "ladder_level_used": rr.get("ladder_level_used"), "level_attempts": h.get("level_attempts")}
        if en and sr.get("restored_sentence"):
            row["restored_is_verbatim_unique_in_cycle_start_article"] = (en.count(sr["restored_sentence"]) == 1)
        # 最小Rewrite: 成功した水準のbefore/afterについて、変更域が焦点文の内側か
        diffs = []
        for att in h.get("level_attempts", []) or []:
            if att.get("result") == "success":
                for ba in att.get("before_after", []) or []:
                    b, a = ba.get("before") or "", ba.get("after") or ""
                    p = 0
                    mx = min(len(b), len(a))
                    while p < mx and b[p] == a[p]:
                        p += 1
                    s = 0
                    while s < mx - p and b[len(b) - 1 - s] == a[len(a) - 1 - s]:
                        s += 1
                    diffs.append({"level": att.get("level"), "before": b, "after": a,
                                  "changed_before": b[p:len(b) - s], "changed_after": a[p:len(a) - s],
                                  "n_changed_chars_before": len(b) - s - p, "n_changed_chars_after": len(a) - s - p,
                                  "sentence_len": len(b)})
                if row.get("restored_is_verbatim_unique_in_cycle_start_article") and sr.get("span") and sr.get("focus_spans") and en:
                    try:
                        g = runner.vs_l6_focus_guard({"span": tuple(sr["span"]), "focus_spans": [tuple(x) for x in sr["focus_spans"]]},
                                                     sr["restored_sentence"], diffs[-1]["after"] if diffs else sr["restored_sentence"], en)
                        row["changed_region_inside_focus_sentences"] = g["ok"]
                    except Exception as e:  # noqa: BLE001
                        row["changed_region_inside_focus_sentences"] = f"check_error:{e!r}"
        row["rewrite_diffs"] = diffs
        out.append(row)
    return out


def run_agg():
    runs = []
    for s in (1, 2):
        for iid in INSTANCE_IDS:
            d = _load(f"{OUT_DIR_REP25}/instances_s{s}/{iid}.json")
            if d:
                runs.append((s, iid, d))
    S = {"n_runs": len(runs), "instances": INSTANCE_IDS, "per_run": [], "rep24_same_instances": []}
    for s, iid, d in runs:
        cyc_start_en = {}
        cycles = d.get("cycles", [])
        for ci, c in enumerate(cycles):
            cyc_start_en[c.get("cycle")] = (cycles[ci - 1].get("en_text_after_rewrite") or cycles[ci - 1].get("en_text_before_rewrite")) if ci else c.get("en_text_before_rewrite")
        rap = d.get("residual_at_pass") or {}
        blocking = [(c["cycle"], sr) for c in cycles for sr in c.get("stage2_results", []) if sr.get("materiality") == "BLOCKING"]
        ja_changed = any("ja_text_after_rewrite" in c for c in cycles)
        ja_calls = [cl.get("label") for cl in d.get("call_log", []) if "ja_" in str(cl.get("label", ""))]
        S["per_run"].append({
            "sample": s, "instance_id": iid, "final_state": d.get("final_state"), "stage4_reason": d.get("stage4_reason"),
            "is_stage4": d.get("final_state") == "STAGE4_ESCALATION", "cost_jpy": d.get("total_cost_jpy"),
            "n_cycles": len(cycles), "n_blocking_claims": len(blocking),
            "blocking_claims": [f"c{cy}:{(sr.get('claim_text') or '')[:160]}" for cy, sr in blocking],
            "residual_at_pass": {"final_state_is_pass_family": rap.get("final_state_is_pass_family"),
                                 "defs": rap.get("defs")},
            "pass_with_residual_unflagged": [x.get("sub_id") for x in rap.get("defs", []) if x.get("pass_with_residual_unflagged")],
            "ja_changed": ja_changed, "ja_labelled_calls": ja_calls,
            "paired": [rr.get("mechanism") for _c, rr in _iter_records(d) if str(rr.get("mechanism", "")).startswith("paired")],
            "switches": d.get("switches"), "full_recheck_reasons": [c.get("full_recheck_required_reasons") for c in cycles],
            "l6": _l6_detail(d, cyc_start_en),
            "unresolved_reasons": [(rr.get("handoff") or {}).get("span_unverified_reason") for _c, rr in _iter_records(d)
                                   if (rr.get("handoff") or {}).get("span_unverified")],
        })
    done_pairs = {(s_, i_) for s_, i_, _d in runs}  # rep25で実行した(sample, instance)と同じ組だけをrep24と比較する
    for s in (1, 2):
        for iid in INSTANCE_IDS:
            d = _load(f"{REP24_DIR}/instances_s{s}/{iid}.json")
            if d and (s, iid) in done_pairs:
                S["rep24_same_instances"].append({"sample": s, "instance_id": iid, "final_state": d.get("final_state"),
                                                  "stage4_reason": d.get("stage4_reason"), "cost_jpy": d.get("total_cost_jpy")})
    # 記録(handoff)にL6の試行が残らない経路(同一cycleの先行Rewriteで書き換え済みになったcarry-forward。この記録は
    # 実行後に追加したため、本rep25のinstance JSONには無い)を補うため、記録済みclaimと本文を決定論replay(¥0)する。
    runner.VS_MATCH_EXT, runner.VS_EXPLAIN_SPLIT, runner.VS_SENTENCE_RESTORE = True, True, True
    S["offline_l6_replay_of_recorded_claims"] = []
    for s, iid, d in runs:
        for ci, c in enumerate(d.get("cycles", [])):
            en_start = (d["cycles"][ci - 1].get("en_text_after_rewrite") or d["cycles"][ci - 1].get("en_text_before_rewrite")) if ci else c.get("en_text_before_rewrite")
            en_after = c.get("en_text_after_rewrite")
            for sr in c.get("stage2_results", []):
                if sr.get("materiality") != "BLOCKING" or not en_start:
                    continue
                r0 = runner._resolve_claim_string(sr.get("claim_text") or "", en_start, None)
                r1 = runner._resolve_claim_string(sr.get("claim_text") or "", en_after, None) if en_after else None
                S["offline_l6_replay_of_recorded_claims"].append({
                    "sample": s, "instance_id": iid, "cycle": c.get("cycle"), "claim": sr.get("claim_text"),
                    "at_cycle_start": {"status": r0["status"], "level": r0.get("level"),
                                       "restored": ((r0.get("sentence_restore") or {}).get("restored_sentence")
                                                    if r0.get("level") == runner.VS_L6_LEVEL else None)},
                    "after_rewrite_text": ({"status": r1["status"], "level": r1.get("level")} if r1 else None)})
    inst_runs = [d for _s, _i, d in runs]
    S["sentence_restore_summary"] = runner.sentence_restore_summarize(inst_runs)
    S["stage4_count"] = sum(1 for m in S["per_run"] if m["is_stage4"])
    S["stage4_by_reason"] = dict(collections.Counter(m["stage4_reason"] for m in S["per_run"] if m["is_stage4"]))
    S["cost_total_jpy"] = round(sum(m["cost_jpy"] or 0 for m in S["per_run"]), 4)
    S["cost_rep24_same_runs_jpy"] = round(sum(m["cost_jpy"] or 0 for m in S["rep24_same_instances"]), 4)
    S["cost_diff_per_article_jpy"] = (round((S["cost_total_jpy"] - S["cost_rep24_same_runs_jpy"]) / max(1, len(runs)), 4)
                                      if runs else None)
    S["pass_with_residual_unflagged_total"] = sum(len(m["pass_with_residual_unflagged"]) for m in S["per_run"])
    S["ja_changed_total"] = sum(1 for m in S["per_run"] if m["ja_changed"])
    S["safety_critical"] = runner.detect_safety_critical_misdowngrades(inst_runs)
    S["safety_critical_defs_by_run"] = [{"sample": m["sample"], "instance_id": m["instance_id"], "final_state": m["final_state"],
                                         "defs": [{k: x.get(k) for k in ("sub_id", "remains_in_final_en", "ever_blocking_flagged",
                                                                         "pass_with_residual_unflagged")}
                                                  for x in (m["residual_at_pass"].get("defs") or [])]} for m in S["per_run"]]
    os.makedirs(OUT_DIR_REP25, exist_ok=True)
    with open(f"{OUT_DIR_REP25}/summary_01.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    md = ["# summary_01.md (rep25、委任_66)", "",
          f"n instance-run={S['n_runs']} cost=JPY{S['cost_total_jpy']} (rep24同instance同run数: JPY{S['cost_rep24_same_runs_jpy']}, "
          f"1記事あたり差 JPY{S['cost_diff_per_article_jpy']})",
          f"STAGE4={S['stage4_count']} {S['stage4_by_reason']} / pass_with_residual_unflagged={S['pass_with_residual_unflagged_total']} / "
          f"ja_changed={S['ja_changed_total']}",
          f"L6集計: {json.dumps(S['sentence_restore_summary'], ensure_ascii=False)}", "", "## per run", ""]
    for m in S["per_run"]:
        md.append(f"- s{m['sample']} {m['instance_id']}: {m['final_state']} s4={m['stage4_reason']} JPY{m['cost_jpy']} cycles={m['n_cycles']} "
                  f"blocking={m['n_blocking_claims']} unresolved={m['unresolved_reasons']}")
        for l in m["l6"]:
            md.append(f"  - L6 c{l['cycle']} {l['status']} reason={l['reason']} restore={l['restore_reason']} n_sent={l['n_sentences']} "
                      f"focus_absent={l['issue_focus_absent']} level_used={l['ladder_level_used']} method={l['method']}")
            md.append(f"    claim: {l['original_claim']}")
            md.append(f"    restored: {l['restored_sentence']}")
            for df in l["rewrite_diffs"]:
                md.append(f"    rewrite[{df['level']}] changed: {df['changed_before']!r} -> {df['changed_after']!r} "
                          f"(sentence {df['sentence_len']} chars, inside_focus={l.get('changed_region_inside_focus_sentences')})")
    with open(f"{OUT_DIR_REP25}/summary_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({k: S[k] for k in ("n_runs", "stage4_count", "stage4_by_reason", "cost_total_jpy", "cost_rep24_same_runs_jpy",
                                         "cost_diff_per_article_jpy", "pass_with_residual_unflagged_total", "ja_changed_total",
                                         "sentence_restore_summary")}, ensure_ascii=True, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["main", "agg"])
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--budget-jpy", type=float, default=8.0)
    args = ap.parse_args()
    if args.stage == "agg":
        run_agg()
        return
    if args.n != 2:
        raise SystemExit("n=2固定(委任_66)")
    run_main(args.n, args.budget_jpy)


if __name__ == "__main__":
    main()
