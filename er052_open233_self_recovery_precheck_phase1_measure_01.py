# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_precheck_phase1_measure_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ①、委任_06)
# ============================================================
# 目的: design_open233_self_recovery_flow_01.md §9-1①(precheck FP率実測、
# ¥0、最優先)を実行する。
# (a) 既存LEDGER_COMPLIANT(deviations=[])記事28件へprecheckを適用し、
#     FP率(記事単位・finding単位)と型別内訳を測定する。
# (b) Safety群(er009 9種+A2A3/A4/A5、既存er050_gpt6_checker_comparison_
#     trial_01.step1_fixtures())へprecheckを適用し、precheck単独の
#     検出率(型別)を測定する。
# API呼び出しなし(¥0)。Production非接続。
from __future__ import annotations

import glob
import json

import er050_gpt6_checker_comparison_trial_01 as g6
import er052_open233_self_recovery_precheck_01 as pc

OUT_DIR = "er052_output/open233_self_recovery_precheck_01"


def find_ledger_compliant_articles() -> list[str]:
    files = glob.glob("er019_output/**/deviation_checks/*.json", recursive=True)
    out = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except Exception:
            continue
        p = d.get("parsed", d)
        if p.get("overall_status") == "LEDGER_COMPLIANT" and p.get("deviations") == []:
            out.append(f)
    return sorted(out)


def measure_fp_rate() -> dict:
    files = find_ledger_compliant_articles()
    per_article = []
    kind_counts: dict[str, int] = {}
    articles_with_finding = 0
    total_findings = 0
    for path in files:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        prompt = d.get("prompt")
        if not prompt:
            per_article.append({"path": path, "skipped": "no prompt key"})
            continue
        try:
            extracted = g6.extract_inputs_from_prompt(prompt)
            assert g6.verify_reconstruction(prompt, extracted)
        except Exception as e:  # noqa: BLE001
            per_article.append({"path": path, "skipped": f"reconstruction failed: {e}"})
            continue
        findings = pc.run_precheck(extracted["ledger_text"], extracted["article_text"])
        if findings:
            articles_with_finding += 1
            total_findings += len(findings)
            for f in findings:
                kind_counts[f["kind"]] = kind_counts.get(f["kind"], 0) + 1
        per_article.append({
            "path": path,
            "n_findings": len(findings),
            "findings": findings,
        })
    n_articles_evaluated = sum(1 for r in per_article if "skipped" not in r)
    return {
        "n_articles_total": len(files),
        "n_articles_evaluated": n_articles_evaluated,
        "n_articles_with_false_positive_finding": articles_with_finding,
        "article_level_fp_rate": round(articles_with_finding / n_articles_evaluated, 4) if n_articles_evaluated else None,
        "total_findings": total_findings,
        "finding_kind_counts": kind_counts,
        "per_article": per_article,
    }


def measure_safety_group_detection_rate() -> dict:
    fixtures = g6.step1_fixtures()
    per_fixture = []
    kind_counts: dict[str, int] = {}
    n_detected = 0
    for fx in fixtures:
        findings = pc.run_precheck(fx["ledger_text"], fx["article_text"])
        detected = len(findings) > 0
        if detected:
            n_detected += 1
            for f in findings:
                kind_counts[f["kind"]] = kind_counts.get(f["kind"], 0) + 1
        per_fixture.append({
            "id": fx["id"],
            "gold_note": fx.get("gold_note"),
            "expected_flag": fx.get("expected_flag"),
            "precheck_detected": detected,
            "findings": findings,
        })
    return {
        "n_fixtures": len(fixtures),
        "n_detected_by_precheck_alone": n_detected,
        "precheck_detection_rate": round(n_detected / len(fixtures), 4),
        "finding_kind_counts": kind_counts,
        "per_fixture": per_fixture,
    }


def main():
    import os
    os.makedirs(OUT_DIR, exist_ok=True)

    fp_result = measure_fp_rate()
    with open(f"{OUT_DIR}/phase1_step1_fp_rate.json", "w", encoding="utf-8") as f:
        json.dump(fp_result, f, ensure_ascii=False, indent=2)
    print(json.dumps({
        "n_articles_total": fp_result["n_articles_total"],
        "n_articles_evaluated": fp_result["n_articles_evaluated"],
        "n_articles_with_false_positive_finding": fp_result["n_articles_with_false_positive_finding"],
        "article_level_fp_rate": fp_result["article_level_fp_rate"],
        "total_findings": fp_result["total_findings"],
        "finding_kind_counts": fp_result["finding_kind_counts"],
    }, ensure_ascii=False, indent=2))

    safety_result = measure_safety_group_detection_rate()
    with open(f"{OUT_DIR}/phase1_step1_safety_group_detection.json", "w", encoding="utf-8") as f:
        json.dump(safety_result, f, ensure_ascii=False, indent=2)
    print(json.dumps({
        "n_fixtures": safety_result["n_fixtures"],
        "n_detected_by_precheck_alone": safety_result["n_detected_by_precheck_alone"],
        "precheck_detection_rate": safety_result["precheck_detection_rate"],
        "finding_kind_counts": safety_result["finding_kind_counts"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
