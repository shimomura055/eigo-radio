# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage2_downgrade_q_measure_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_68): 修正版S1(降格の2-of-2)導入時の「2回目だけBLOCKING」率qの限定測定。
# 測定専用(Production path・runner・Checker Prompt・Schema・Stage 2 rubric[V7b]は変更しない)。
#   対象: rep24で「Checker MAJOR→Stage 2の1回目が非BLOCKING(llm_direct)」となった68件(body 50/hook 18)から、
#         cycle 1由来とcycle 2以降由来を分けて抽出(cycle 2以降を優先して全件、残りをcycle 1へ。計上限=2*max_per_group)。
#   各claimに対し、記録済みと同一の本文・Ledger・rubric(runner既定=V7b/hook V4)で、対象claimのみのbatch(1 claim)を
#   runner.run_stage2で1回呼ぶ(=修正版S1の2回目に相当。比較基準は最終materiality)。hook経路はhook-aware Stage 2。
# 既存のrunner.run_stage2を呼ぶだけで、runnerファイルは変更しない(出力先・予算state・FLOOR_VERIFY_MODEのみ
# 本プロセス内でモジュール変数を差し替える)。
# ============================================================
from __future__ import annotations

import argparse
import json
import math
import os
import random

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_stage2_b3_misdowngrade_diag_01 as diag

OUT_DIR = "er052_output/open233_stage2_downgrade_q_measure_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233at_68.json"
SEED = 20261004
FIRST_DIR_SUFFIX = "rep24"


def _load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save(p, o):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1, default=str)


def _wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0, c - h), 3), round(min(1, c + h), 3)]


def _runner():
    import er052_open233_self_recovery_flow_runner_01 as runner
    runner.OUT_DIR = OUT_DIR
    runner.BUDGET_STATE_PATH = BUDGET_STATE_PATH
    return runner


def _claim_text_context(runner, inst_cache, instance_id, cycle, d, c_idx_rec):
    """cycle開始時点の本文(en)でStage 2が見たlocal_contextを再現できるかを確認し、作業fixtureを返す。"""
    if instance_id not in inst_cache:
        inst_cache[instance_id] = next((i for i in runner.build_target_instances() if i["instance_id"] == instance_id), None)
    inst = inst_cache[instance_id]
    if inst is None:
        return None, "instance_not_in_build_target_instances"
    fx = dict(inst["fixture"])
    if cycle == 1:
        art = fx["article_text"]
    else:
        prev = d["cycles"][cycle - 2]
        art = prev.get("en_text_after_rewrite")
        if not art:
            return None, "prev_cycle_text_missing"
    fx["article_text"] = art
    lc, _ = runner.s2p.build_local_context(art, c_idx_rec["claim_text"])
    if lc != c_idx_rec.get("local_context"):
        return None, "local_context_mismatch"
    return fx, None


def select_targets(runner, max_per_group):
    rows, _, _, _, _ = diag.collect_downgrades()
    rows = [r for r in rows if r["via"] == "llm_direct" and r["dir"].endswith(FIRST_DIR_SUFFIX)]
    inst_cache, ok, skipped = {}, [], []
    for r in rows:
        d = _load(r["file"])
        rec = d["cycles"][r["cycle"] - 1]["stage2_results"][r["result_index"]]
        fx, why = _claim_text_context(runner, inst_cache, r["instance_id"], r["cycle"], d, rec)
        if fx is None:
            skipped.append({"instance_id": r["instance_id"], "cycle": r["cycle"], "why": why})
            continue
        ok.append({**r, "claim_text": rec["claim_text"], "related_fact_id": rec.get("related_fact_id"),
                   "first_route": rec.get("stage2_route"), "first_basis": rec.get("basis"),
                   "first_llm": rec.get("llm_materiality"), "first_final": rec["materiality"],
                   "first_floor_reason": rec.get("floor_reason")})
    rng = random.Random(SEED)
    c2 = [r for r in ok if r["cycle"] > 1]
    c1 = [r for r in ok if r["cycle"] == 1]
    rng.shuffle(c2)
    rng.shuffle(c1)
    cap_total = 2 * max_per_group
    c2_sel = c2[:max_per_group]
    c1_sel = c1[:cap_total - len(c2_sel)]
    sel = c1_sel + c2_sel
    for i, r in enumerate(sel):
        r["sel_id"] = f"t{i:02d}"
    return sel, {"candidates_llm_direct_rep24": len(rows), "usable": len(ok), "skipped": skipped,
                 "cycle1_candidates": len(c1), "cycle2plus_candidates": len(c2),
                 "cycle1_selected": len(c1_sel), "cycle2plus_selected": len(c2_sel), "seed": SEED}


def run_one(runner, client, state, ce, t, inst_cache):
    path = f"{OUT_DIR}/raw/{t['sel_id']}.json"
    if os.path.exists(path):
        return _load(path)
    d = _load(t["file"])
    rec = d["cycles"][t["cycle"] - 1]["stage2_results"][t["result_index"]]
    fx, why = _claim_text_context(runner, inst_cache, t["instance_id"], t["cycle"], d, rec)
    claim = {"claim_text": rec["claim_text"], "origin": rec.get("origin"), "related_fact_id": rec.get("related_fact_id"),
             "dev": rec["dev"], "detected_by": rec.get("detected_by", "stage1_llm")}
    raw_calls, call_log = [], []
    s2c, s2h = runner.s2c, runner.s2h
    orig_c, orig_h = s2c.run_stage2_batch_variant, s2h.run_stage2_hook_batch

    def wrap(fn, kind):
        def _w(*a, **k):
            r = fn(*a, **k)
            raw_calls.append({"kind": kind, "result": r})
            return r
        return _w
    s2c.run_stage2_batch_variant, s2h.run_stage2_hook_batch = wrap(orig_c, "body"), wrap(orig_h, "hook")
    try:
        out = runner.run_stage2(client, state, ce, call_log, t["sel_id"], fx, [claim])
    finally:
        s2c.run_stage2_batch_variant, s2h.run_stage2_hook_batch = orig_c, orig_h
    r2 = out[0]
    res = {"sel_id": t["sel_id"], "instance_id": t["instance_id"], "cycle": t["cycle"], "route_first": t["first_route"],
           "first": {"llm": t["first_llm"], "final": t["first_final"], "basis": t["first_basis"],
                     "floor_reason": t["first_floor_reason"]},
           "second": {"llm": r2["llm_materiality"], "final": r2["materiality"], "basis": r2["basis"],
                      "rewrite_kind": r2["rewrite_kind"], "rewrite_hint": r2["rewrite_hint"],
                      "floor_reason": r2["floor_reason"], "route": r2["stage2_route"]},
           "claim_text": t["claim_text"], "issue": (rec["dev"] or {}).get("issue"),
           "local_context": rec.get("local_context"),
           "cost_jpy": round(sum(c.get("cost_jpy", 0.0) for c in call_log), 4), "call_log": call_log, "raw": raw_calls}
    _save(path, res)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["probe", "main", "agg"], required=True)
    ap.add_argument("--max-per-group", type=int, default=20)
    ap.add_argument("--budget-jpy", type=float, default=6.0)
    a = ap.parse_args()
    if a.stage == "agg":
        return agg()
    runner = _runner()
    runner.TOTAL_BUDGET_JPY = a.budget_jpy
    runner.FLOOR_VERIFY_MODE = runner.validate_floor_verify_mode("time_only")   # rep24と同じ構成
    sel_path = f"{OUT_DIR}/selection_{a.max_per_group}.json"
    if os.path.exists(sel_path):
        sel = _load(sel_path)["targets"]
    else:
        sel, info = select_targets(runner, a.max_per_group)
        _save(sel_path, {"info": info, "targets": sel})
        print(json.dumps(info, ensure_ascii=False))
    client = vfl01.get_client()
    state = runner.load_budget_state()
    ce = [0]
    inst_cache = {}
    stopped, reason = False, None
    todo = sel[:1] if a.stage == "probe" else sel
    try:
        for t in todo:
            r = run_one(runner, client, state, ce, t, inst_cache)
            print(t["sel_id"], r["first"]["final"], "->", r["second"]["final"], r["second"]["basis"], r["cost_jpy"], flush=True)
    except runner.TrialAbort as e:
        stopped, reason = True, str(e)
    info = {"stage": a.stage, "stopped": stopped, "stop_reason": reason, "cumulative_jpy": round(state["cumulative_jpy"], 4),
            "cumulative_calls": state["cumulative_calls"], "cumulative_errors": state["cumulative_errors"]}
    _save(f"{OUT_DIR}/stage_{a.stage}_info.json", info)
    print(json.dumps(info, ensure_ascii=False))


def _results():
    out = []
    d = f"{OUT_DIR}/raw"
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            out.append(_load(f"{d}/{fn}"))
    return out


def _grp(rs):
    n = len(rs)
    fc = [r for r in rs if "failclosed" in (r["second"]["route"] or "")]
    valid = [r for r in rs if r not in fc]
    nb = sum(1 for r in valid if r["second"]["final"] == "BLOCKING")
    return {"n": n, "api_failure_or_schema": len(fc), "n_valid": len(valid), "blocking": nb,
            "q": round(nb / len(valid), 3) if valid else None, "q_wilson95": _wilson(nb, len(valid))}


def agg():
    rs = _results()
    state = _load(BUDGET_STATE_PATH)
    labels_path = f"{OUT_DIR}/provisional_labels_01.json"
    labels = _load(labels_path) if os.path.exists(labels_path) else {}
    out = {"cost_jpy_total": round(state["cumulative_jpy"], 4), "calls": state["cumulative_calls"],
           "errors": state["cumulative_errors"], "n_results": len(rs), "overall": _grp(rs)}
    out["by_cycle"] = {"cycle1": _grp([r for r in rs if r["cycle"] == 1]), "cycle2plus": _grp([r for r in rs if r["cycle"] > 1])}
    out["by_route"] = {k: _grp([r for r in rs if r["route_first"] == k]) for k in ("body", "hook")}
    out["by_first_final"] = {k: _grp([r for r in rs if r["first"]["final"] == k]) for k in ("ACCEPTABLE", "QUALITY")}
    out["by_cycle_route"] = {f"{c}/{k}": _grp([r for r in rs if (r["cycle"] == 1) == (c == "cycle1") and r["route_first"] == k])
                             for c in ("cycle1", "cycle2plus") for k in ("body", "hook")}
    out["route_mismatch"] = [r["sel_id"] for r in rs if r["second"]["route"] != r["route_first"]]
    out["second_floor_reason_anomaly"] = [{"sel_id": r["sel_id"], "floor_reason": r["second"]["floor_reason"],
                                           "second_llm": r["second"]["llm"], "second_final": r["second"]["final"]}
                                          for r in rs if r["second"]["floor_reason"] and "failclosed" not in r["second"]["floor_reason"]]
    out["second_blocking_only_via_llm_vs_final"] = {
        "llm_blocking": sum(1 for r in rs if r["second"]["llm"] == "BLOCKING"),
        "final_blocking": sum(1 for r in rs if r["second"]["final"] == "BLOCKING")}
    bl = [r for r in rs if r["second"]["final"] == "BLOCKING"]
    out["blocking_cases"] = [{"sel_id": r["sel_id"], "instance_id": r["instance_id"], "cycle": r["cycle"], "route": r["route_first"],
                              "first": r["first"], "second_basis": r["second"]["basis"], "second_kind": r["second"]["rewrite_kind"],
                              "second_hint": r["second"]["rewrite_hint"], "claim_text": r["claim_text"], "issue": r["issue"],
                              "provisional_label": (labels.get(r["sel_id"]) or {}).get("label"),
                              "provisional_reason": (labels.get(r["sel_id"]) or {}).get("reason")} for r in bl]
    lab = {}
    for c in out["blocking_cases"]:
        lab[c["provisional_label"]] = lab.get(c["provisional_label"], 0) + 1
    out["blocking_provisional_label_counts"] = lab
    out["stop_threshold"] = {"cycle1_limit": 0.30, "cycle2plus_limit": 0.20,
                             "cycle1_exceeds": (out["by_cycle"]["cycle1"]["q"] or 0) > 0.30,
                             "cycle2plus_exceeds": (out["by_cycle"]["cycle2plus"]["q"] or 0) > 0.20}
    # S1追加費用の試算(rep24 38 instance-run、29記事)。target件数はrep24のllm_direct(cycle別)。
    rows, _, _, _, _ = diag.collect_downgrades()
    r24 = [r for r in rows if r["via"] == "llm_direct" and r["dir"].endswith(FIRST_DIR_SUFFIX)]
    n1, n2 = sum(1 for r in r24 if r["cycle"] == 1), sum(1 for r in r24 if r["cycle"] > 1)
    q1, q2 = out["by_cycle"]["cycle1"]["q"] or 0, out["by_cycle"]["cycle2plus"]["q"] or 0
    extra_rw = n1 * q1 + n2 * q2
    calls = len({(r["file"], r["cycle"], r["route"]) for r in r24})
    unit = (sum(r["cost_jpy"] for r in rs) / len(rs)) if rs else 0.14
    est = {"rep24_targets": {"cycle1": n1, "cycle2plus": n2}, "rep24_s2_second_calls_batched": calls,
           "unit_cost_per_call_measured_single_claim": round(unit, 4),
           "extra_rewrites_total_rep24": round(extra_rw, 2), "extra_rewrites_per_instance_run(38)": round(extra_rw / 38, 3),
           "stage2_second_cost_per_instance_run(batched)": round(calls * unit / 38, 3),
           "stage2_second_cost_per_article(29)": round(calls * unit / 29, 3)}
    est["rewrite_cost_per_instance_run_range"] = [round(extra_rw / 38 * 0.5, 3), round(extra_rw / 38 * 0.8, 3)]
    est["total_extra_per_instance_run_range"] = [round(est["stage2_second_cost_per_instance_run(batched)"] + est["rewrite_cost_per_instance_run_range"][0], 3),
                                                 round(est["stage2_second_cost_per_instance_run(batched)"] + est["rewrite_cost_per_instance_run_range"][1], 3)]
    est["note"] = "推定。Rewriteの再帰(Recheckで新MAJOR等)・STAGE4への移行は含まない。+2円枠はfloor_verify/L6/Recheck等の合計に対する上限(Opus#10)。"
    out["s1_cost_estimate"] = est
    _save(f"{OUT_DIR}/results_01.json", out)
    md = ["# results_01.md (委任_68 q測定: 修正版S1の2回目だけBLOCKINGになる率)\n",
          f"cost_jpy_total={out['cost_jpy_total']} calls={out['calls']} errors={out['errors']} n={out['n_results']}\n",
          "## q(2回目の最終materiality=BLOCKING率)\n", "| 区分 | n | API失敗等 | 有効n | BLOCKING | q | Wilson95 |", "|---|---|---|---|---|---|---|"]

    def row(nm, g):
        md.append(f"| {nm} | {g['n']} | {g['api_failure_or_schema']} | {g['n_valid']} | {g['blocking']} | {g['q']} | {g['q_wilson95']} |")
    row("全体", out["overall"])
    for k, g in out["by_cycle"].items():
        row(k, g)
    for k, g in out["by_route"].items():
        row(f"route={k}", g)
    for k, g in out["by_first_final"].items():
        row(f"1回目={k}", g)
    for k, g in out["by_cycle_route"].items():
        row(k, g)
    md.append(f"\nSTOP閾値(cycle1>30% / cycle2+>20%): {out['stop_threshold']}")
    md.append(f"route不一致: {out['route_mismatch']} / 2回目floor_reason異常: {out['second_floor_reason_anomaly']}")
    md.append(f"2回目のllm_materiality=BLOCKING {out['second_blocking_only_via_llm_vs_final']['llm_blocking']}件 / 最終BLOCKING {out['second_blocking_only_via_llm_vs_final']['final_blocking']}件\n")
    md.append("## 2回目BLOCKINGの件(仮ラベル=実行層[Sonnet]の読み、正式確定ではない)\n")
    md.append(f"仮ラベル集計: {out['blocking_provisional_label_counts']}\n")
    for c in out["blocking_cases"]:
        md.append(f"- {c['sel_id']} {c['instance_id']} c{c['cycle']} {c['route']}: 1回目={c['first']['final']}({c['first']['basis']}) -> 2回目 BLOCKING basis={c['second_basis']} kind={c['second_kind']}"
                  f" / 仮ラベル={c['provisional_label']} 理由={c['provisional_reason']}\n  claim: {c['claim_text']}\n  Checker issue: {c['issue']}\n  hint: {c['second_hint']}")
    md.append("\n## S1追加費用の試算\n")
    for k, v in est.items():
        md.append(f"- {k}: {v}")
    with open(f"{OUT_DIR}/results_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({k: out[k] for k in ("cost_jpy_total", "calls", "errors", "overall", "by_cycle", "by_route", "by_first_final", "stop_threshold", "blocking_provisional_label_counts")}, ensure_ascii=True))


if __name__ == "__main__":
    main()
