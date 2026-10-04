# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_stage2_b3_misdowngrade_diag_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (委任_67): rep25 bgroup_B3 s1のStage 2誤降格(Safety-critical見逃し)の原因診断。
# 診断専用(Production path・runner・Checker Prompt・Schema・V7b/V7原則文は一切変更しない)。
#   (a) rep25 B3 s1の保存済みStage 2入力(本文・claim・local_context・batch構成[claim 1件])を再現し、
#       V7b n=10 / V7 n=10。
#   (b) batch構成はrep25の時点で1claim(単独と同一)のため、(a)と同一入力。別途の測定は行わない
#       (--n-b > 0 の場合のみ、(a)と同じ入力のV7bを追加実行する。既定0)。
#   (c) Safety-critical残り4件(B4-a/A2A3-0/A4-0/A5-0=委任_61 Part Aと同じgroup batch)+K16/K20
#       (委任_61 Part E CUSTOM_GROUPS E1_neg3/E2_a4)をV7b n=5ずつ。
# 既存のs2c.run_stage2_batch_variant/sc02.guarded_batch_callを再利用し、出力先だけ本スクリプト専用へ差し替える。
# ============================================================
from __future__ import annotations

import argparse
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er052_open233_element_trial_safety_control_02 as sc02
import er052_open233_element_trial_safety_control_06 as sc06
import er052_open233_self_recovery_stage2_calibration_01 as s2c

OUT_DIR = "er052_output/open233_stage2_b3_misdowngrade_diag_01"
BUDGET_STATE_PATH = f"{OUT_DIR}/budget_state_c233as_67.json"
REP25_B3 = "er052_output/open233_self_recovery_flow_runner_01_rep25/instances_s1/bgroup_B3.json"
REP25_B3_STAGE2_SHA = "85f6b9852656e40cdcb162ecad45e8b5cf7e92c907c08784e62d672f2d1a3f97"
RUBRICS = {"V7b": s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B,
           "V7": s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7}
C_GROUPS = ["B4", "A2A3", "A4", "A5"]       # 委任_61 Part Aと同じgroup batch(safety-critical sub_idを含む)
C_CUSTOM = ["E1_neg3", "E2_a4"]             # K16 / K20
C_TARGET_SUBS = {"B4": "B4-a", "A2A3": "A2A3-0", "A4": "A4-0", "A5": "A5-0"}


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_b3_input():
    d = _load(REP25_B3)
    sr = d["cycles"][0]["stage2_results"][0]
    import er052_open233_self_recovery_flow_runner_01 as runner
    fx = next(i for i in runner.build_target_instances() if i["instance_id"] == "bgroup_B3")["fixture"]
    claim = {"claim_text": sr["claim_text"], "origin": sr["origin"], "related_fact_id": sr["related_fact_id"],
             "local_context": sr["local_context"]}
    return fx, [claim], d["cycles"][0]["stage2_results"]


def call_once(client, state, ce, label, save_path, fixture, claims, rubric):
    """保存済みなら再利用(probeの結果をmainのnへ算入、二重課金回避)。"""
    if os.path.exists(save_path):
        r = _load(save_path)
        if "error" not in r:
            return r
    return sc02.guarded_batch_call(state, ce, label, save_path, client=client,
                                   verified_ledger_text=fixture["ledger_text"],
                                   source_article_text=fixture.get("source_article_text"),
                                   claims=claims, rubric_text=rubric)


def judg(res, idx):
    if res is None or "error" in res:
        return None
    m = next((j for j in res["parsed"].get("judgments", []) if j.get("claim_index") == idx), None)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["probe", "main", "agg"], required=True)
    ap.add_argument("--n-a", type=int, default=10)
    ap.add_argument("--n-b", type=int, default=0)
    ap.add_argument("--n-c", type=int, default=5)
    ap.add_argument("--budget-jpy", type=float, default=12.0)
    a = ap.parse_args()
    sc02.OUT_DIR, sc02.BUDGET_STATE_PATH = OUT_DIR, BUDGET_STATE_PATH
    sc02.TOTAL_BUDGET_JPY = a.budget_jpy
    if a.stage == "agg":
        return agg()
    client = vfl01.get_client()
    state = sc02.load_budget_state()
    ce = [0]
    fx, claims, _ = build_b3_input()
    stopped, reason = False, None
    try:
        if a.stage == "probe":
            r = call_once(client, state, ce, "a_V7b_run1", f"{OUT_DIR}/a_V7b/run_1.json", fx, claims, RUBRICS["V7b"])
            j = judg(r, 0)
            print(json.dumps({"prompt_sha256": r["prompt_sha256"], "sha_matches_rep25": r["prompt_sha256"] == REP25_B3_STAGE2_SHA,
                              "cost_jpy": r["cost_jpy"], "usage": r["usage"], "judgment": j}, ensure_ascii=False, indent=1))
        else:
            for tag in ("V7b", "V7"):
                for i in range(1, a.n_a + 1):
                    call_once(client, state, ce, f"a_{tag}_run{i}", f"{OUT_DIR}/a_{tag}/run_{i}.json", fx, claims, RUBRICS[tag])
            for i in range(1, a.n_b + 1):
                call_once(client, state, ce, f"b_V7b_run{i}", f"{OUT_DIR}/b_V7b/run_{i}.json", fx, claims, RUBRICS["V7b"])
            groups = {g["group_id"]: g for g in sc02.safety_critical_groups()}
            for gid in C_GROUPS:
                g = groups[gid]
                cl = s2c.build_claim_records_for_group(g)
                for i in range(1, a.n_c + 1):
                    call_once(client, state, ce, f"c_V7b_{gid}_run{i}", f"{OUT_DIR}/c_V7b/{gid}/run_{i}.json",
                              g["fixture"], cl, RUBRICS["V7b"])
            inputs = sc06.build_custom_inputs()
            for key in C_CUSTOM:
                g = inputs[key]
                for i in range(1, a.n_c + 1):
                    call_once(client, state, ce, f"c_V7b_{key}_run{i}", f"{OUT_DIR}/c_V7b/{key}/run_{i}.json",
                              g["fixture"], g["claims"], RUBRICS["V7b"])
    except sc02.TrialAbort as e:
        stopped, reason = True, str(e)
    info = {"stage": a.stage, "stopped": stopped, "stop_reason": reason,
            "cumulative_jpy": round(state["cumulative_jpy"], 4), "cumulative_calls": state["cumulative_calls"],
            "cumulative_errors": state["cumulative_errors"]}
    sc02.save_json(f"{OUT_DIR}/stage_{a.stage}_info.json", info)
    print(json.dumps(info, ensure_ascii=False, indent=1))


def _runs(dirpath):
    out = []
    if not os.path.isdir(dirpath):
        return out
    for fn in sorted(os.listdir(dirpath), key=lambda s: int(s.split("_")[1].split(".")[0]) if s.startswith("run_") else 0):
        if fn.startswith("run_"):
            out.append(_load(f"{dirpath}/{fn}"))
    return out


def _rate(labels):
    n = len(labels)
    nb = sum(1 for m in labels if m != "BLOCKING")
    return {"n": n, "blocking": n - nb, "non_blocking": nb,
            "non_blocking_rate": round(nb / n, 3) if n else None,
            "dist": {k: labels.count(k) for k in sorted(set(labels))}}


def agg():
    state = _load(BUDGET_STATE_PATH)
    out = {"cost_jpy_total": round(state["cumulative_jpy"], 4), "calls": state["cumulative_calls"],
           "errors": state["cumulative_errors"]}
    # (a)(b)
    for key in ("a_V7b", "a_V7", "b_V7b"):
        rs = _runs(f"{OUT_DIR}/{key}")
        if not rs:
            continue
        js = [judg(r, 0) for r in rs]
        labels = [j["materiality"] for j in js if j]
        out[key] = {**_rate(labels),
                    "per_run": [{"materiality": j["materiality"], "basis": j.get("basis"),
                                 "rewrite_kind": j.get("rewrite_kind"), "rewrite_hint": j.get("rewrite_hint")}
                                for j in js if j],
                    "prompt_sha256": sorted({r["prompt_sha256"] for r in rs}),
                    "sha_matches_rep25": all(r["prompt_sha256"] == REP25_B3_STAGE2_SHA for r in rs)}
    # (c)
    groups = {g["group_id"]: g for g in sc02.safety_critical_groups()}
    c_rows = []
    for gid in C_GROUPS:
        rs = _runs(f"{OUT_DIR}/c_V7b/{gid}")
        cl = s2c.build_claim_records_for_group(groups[gid])
        for idx, c in enumerate(cl):
            labels, per = [], []
            for r in rs:
                j = judg(r, idx)
                if j:
                    labels.append(j["materiality"])
                    per.append({"materiality": j["materiality"], "basis": j.get("basis"),
                                "rewrite_hint": j.get("rewrite_hint")})
            c_rows.append({"group": gid, "sub_id": c["sub_id"], "correct_label": c["correct_label"],
                           "target": C_TARGET_SUBS.get(gid) == c["sub_id"], "claim_text": c["claim_text"],
                           **_rate(labels), "per_run": per})
    inputs = sc06.build_custom_inputs()
    for key in C_CUSTOM:
        rs = _runs(f"{OUT_DIR}/c_V7b/{key}")
        for idx, c in enumerate(inputs[key]["claims"]):
            labels, per = [], []
            for r in rs:
                j = judg(r, idx)
                if j:
                    labels.append(j["materiality"])
                    per.append({"materiality": j["materiality"], "basis": j.get("basis"),
                                "rewrite_hint": j.get("rewrite_hint")})
            c_rows.append({"group": key, "sub_id": c["sub_id"], "correct_label": c["expected"],
                           "target": c["sub_id"].startswith("e-"), "claim_text": c["claim_text"],
                           **_rate(labels), "per_run": per})
    out["c_rows"] = c_rows
    sc02.save_json(f"{OUT_DIR}/results_01.json", out)
    md = ["# results_01.md (委任_67 B3誤降格診断)\n",
          f"cost_jpy_total={out['cost_jpy_total']} calls={out['calls']} errors={out['errors']}\n",
          "## (a) rep25 B3 s1同一入力\n"]
    for key in ("a_V7b", "a_V7", "b_V7b"):
        if key in out:
            o = out[key]
            md.append(f"- {key}: n={o['n']} BLOCKING={o['blocking']} 非BLOCKING={o['non_blocking']} "
                      f"率={o['non_blocking_rate']} dist={o['dist']} sha一致(rep25)={o['sha_matches_rep25']}")
    md.append("\n## (a) basis逐語(非BLOCKING回)\n")
    for key in ("a_V7b", "a_V7"):
        if key in out:
            for i, p in enumerate(out[key]["per_run"], 1):
                if p["materiality"] != "BLOCKING":
                    md.append(f"- {key} run{i}: {p['materiality']} basis={p['basis']} hint={p['rewrite_hint']!r}")
    md.append("\n## (a) basis逐語(BLOCKING回の代表、各版先頭1件)\n")
    for key in ("a_V7b", "a_V7"):
        if key in out:
            for i, p in enumerate(out[key]["per_run"], 1):
                if p["materiality"] == "BLOCKING":
                    md.append(f"- {key} run{i}: BLOCKING basis={p['basis']} kind={p['rewrite_kind']} hint={p['rewrite_hint']!r}")
                    break
    md.append("\n## (c) Safety-critical残り+K16/K20 (V7b)\n")
    md.append("| group | sub_id | target | 期待 | n | BLOCKING | 非BLOCKING | 分布 |\n|---|---|---|---|---|---|---|---|")
    for r in c_rows:
        md.append(f"| {r['group']} | {r['sub_id']} | {'*' if r['target'] else ''} | {r['correct_label']} | {r['n']} | "
                  f"{r['blocking']} | {r['non_blocking']} | {r['dist']} |")
    md.append("\n## (c) 非BLOCKING回のbasis逐語(target行のみ)\n")
    for r in c_rows:
        if r["target"]:
            for i, p in enumerate(r["per_run"], 1):
                if p["materiality"] != "BLOCKING":
                    md.append(f"- {r['sub_id']} run{i}: {p['materiality']} basis={p['basis']} hint={p['rewrite_hint']!r}")
    with open(f"{OUT_DIR}/results_01.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
