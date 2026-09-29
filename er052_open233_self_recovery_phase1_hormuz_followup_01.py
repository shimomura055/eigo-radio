# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_phase1_hormuz_followup_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ②、委任_06)
# ============================================================
# 目的: trial_03_stability_n20(前Phase実測)でV4-Aがhormuz_run03_standard
# (HF-009 changed_scope)を非検出だった3 attempt(deviations=[])を特定し、
# (a) deterministic pre-check(¥0)を適用して拾えるか、
# (b) Stage 2 Second Judge(診断目的、Stage 1出力なしで独立適用、有料)を
#     適用して拾えるか、を実測する。
#
# Guardrail: 本スクリプト単体¥10(委任文既定)。超過見込みでSTOP。
from __future__ import annotations

import glob
import json
import os

import er003_v1_en_direct_vfl_01_generate as vfl01
import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_precheck_01 as pc
import er052_open233_self_recovery_stage2_01 as stage2

OUT_DIR = "er052_output/open233_self_recovery_phase1_hormuz_followup_01"
GUARDRAIL_JPY = 10.0
N_STAGE2_CALLS = 3  # 3 missed attemptsそれぞれに1 call(入力は同一article_text)


def find_missed_attempts() -> list[dict]:
    base = "er051_output/open233_checker_trial_01/trial_03_stability_n20/hormuz_run03_standard/V4A"
    out = []
    for path in sorted(glob.glob(f"{base}/run_*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        p = d.get("parsed", {})
        if p.get("overall_status") == "LEDGER_COMPLIANT" and p.get("deviations") == []:
            out.append({
                "path": path,
                "attempt": d.get("attempt"),
                "prompt_sha256": d.get("prompt_sha256"),
                "response_id": d.get("response_id"),
            })
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    missed = find_missed_attempts()
    result: dict = {"missed_attempts": missed, "n_missed": len(missed)}
    print(json.dumps({"missed_attempts_found": [m["attempt"] for m in missed]}, ensure_ascii=False))

    fx = {f["id"]: f for f in g6.step3_fixtures()}
    fixture = fx["hormuz_run03_standard"]

    # (a) deterministic pre-check(¥0)
    precheck_findings = pc.run_precheck(fixture["ledger_text"], fixture["article_text"])
    result["precheck_findings"] = precheck_findings
    result["precheck_detected"] = len(precheck_findings) > 0
    print(json.dumps({"precheck_detected": result["precheck_detected"],
                       "n_precheck_findings": len(precheck_findings)}, ensure_ascii=False))

    # (b) Stage 2 diagnostic(有料、Guardrail¥10)
    client = vfl01.get_client()
    stage2_runs = []
    cumulative_jpy = 0.0
    for i in range(1, N_STAGE2_CALLS + 1):
        if cumulative_jpy >= GUARDRAIL_JPY:
            stage2_runs.append({"call": i, "skipped": f"cumulative_jpy={cumulative_jpy:.4f} reached guardrail"})
            continue
        try:
            r = stage2.run_stage2_diagnostic(
                client, fixture["ledger_text"], fixture["article_text"],
                source_article_text=fixture.get("source_article_text"),
            )
        except Exception as e:  # noqa: BLE001
            stage2_runs.append({"call": i, "error": f"{type(e).__name__}: {e}"})
            continue
        cumulative_jpy += r["cost_jpy"]
        detected_blocking = any(
            d["materiality"] == "BLOCKING" for d in r["parsed"].get("candidate_deviations", [])
        )
        stage2_runs.append({
            "call": i,
            "prompt_sha256": r["prompt_sha256"],
            "model": r["model"],
            "response_id": r["response_id"],
            "usage": r["usage"],
            "cost_jpy": r["cost_jpy"],
            "elapsed_seconds": r["elapsed_seconds"],
            "candidate_deviations": r["parsed"].get("candidate_deviations", []),
            "detected_blocking": detected_blocking,
        })
        with open(f"{OUT_DIR}/stage2_call_{i}.json", "w", encoding="utf-8") as f:
            json.dump(stage2_runs[-1], f, ensure_ascii=False, indent=2)

    result["stage2_runs"] = stage2_runs
    result["stage2_cumulative_jpy"] = round(cumulative_jpy, 4)
    result["stage2_n_detected_blocking"] = sum(1 for r in stage2_runs if r.get("detected_blocking"))

    with open(f"{OUT_DIR}/summary.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "stage2_cumulative_jpy": result["stage2_cumulative_jpy"],
        "stage2_n_detected_blocking": result["stage2_n_detected_blocking"],
        "n_stage2_calls_executed": sum(1 for r in stage2_runs if "cost_jpy" in r),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
