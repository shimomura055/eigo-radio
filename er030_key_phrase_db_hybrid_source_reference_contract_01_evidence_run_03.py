# ============================================================
# er030_key_phrase_db_hybrid_source_reference_contract_01_evidence_run_03.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
# ============================================================
# run_01/run_02の実測が想定より安価だった(measured selection cost合計
# ¥7.5445)ため、残予算内で委任文が指定した規模(Meta A2/B1B・Hormuz
# A2/B1B)を完遂するため、Meta B1B・Hormuz B1Bを追加実行する。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_v1_n3_01_scaffold_generate as sc

OUTPUT_ROOT = os.path.join("er030_output", "family_x_kp_source_reference_contract_evidence_01")

SELECTION_COST_STOP_JPY = 6.0

RUNS = [
    {"key": "meta_b1b", "path": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md",
     "level": "b1b", "process": "B1_SUPPORT"},
    {"key": "hormuz_b1b", "path": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
     "level": "b1b", "process": "B1_SUPPORT"},
]


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _run_one(article_key: str, article_path: str, level: str, process: str, cumulative: list) -> dict:
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    article_text = _load(article_path)
    out_dir = os.path.join(OUTPUT_ROOT, article_key, "key_phrases")
    article_id = f"KP_SRC_REF_CONTRACT_EVIDENCE_01_{article_key.upper()}"

    print(f"=== {article_key} (source reference contract evidence 03, kp_backend=db_hybrid) ===")
    t0 = time.time()
    kp = sc.run_key_phrases(article_text, out_dir, article_id, level, process=process,
                             kp_backend="db_hybrid")
    elapsed = time.time() - t0

    selection = kp["selection"]
    cost_jpy = selection.get("cost_jpy")
    if cost_jpy:
        cumulative.append(cost_jpy)

    result = {
        "article_key": article_key, "article_id": article_id, "level": level,
        "kp_backend_used": selection.get("kp_backend_used"),
        "kp_backend_fallback_reason_code": selection.get("kp_backend_fallback_reason_code"),
        "selection_status": selection.get("status"),
        "selection_cost_jpy": cost_jpy,
        "selection_model_id": selection.get("model_id"),
        "shortlist_total_count": selection.get("shortlist_total_count"),
        "source_reference_contract": selection.get("source_reference_contract"),
        "candidate_mismatch_suspected_count": selection.get("candidate_mismatch_suspected_count"),
        "canonicalization_status": (kp.get("canonicalization") or {}).get("status"),
        "redundancy_qa_status": (kp.get("redundancy_qa") or {}).get("status"),
        "redundancy_retry_attempts": kp.get("redundancy_retry_attempts"),
        "elapsed_sec": round(elapsed, 2),
        "cumulative_measured_cost_jpy_so_far": round(sum(cumulative), 4),
    }
    os.makedirs(os.path.join(OUTPUT_ROOT, article_key), exist_ok=True)
    with open(os.path.join(OUTPUT_ROOT, article_key, "evidence_summary.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  kp_backend_used={result['kp_backend_used']} status={result['selection_status']} "
          f"cost_jpy={result['selection_cost_jpy']} shortlist={result['shortlist_total_count']} "
          f"contract={result['source_reference_contract']} mismatch_count="
          f"{result['candidate_mismatch_suspected_count']} canon={result['canonicalization_status']} "
          f"redundancy={result['redundancy_qa_status']} "
          f"cumulative={result['cumulative_measured_cost_jpy_so_far']}")
    return result


def main():
    cumulative = []
    results = {}
    for spec in RUNS:
        if sum(cumulative) > SELECTION_COST_STOP_JPY:
            print(f"[BUDGET STOP] 累積実測¥{sum(cumulative):.4f}が上限¥{SELECTION_COST_STOP_JPY}を"
                  f"超えたため、{spec['key']}以降は実行せず打ち切ります。")
            break
        results[spec["key"]] = _run_one(spec["key"], spec["path"], spec["level"], spec["process"], cumulative)

    summary_path = os.path.join(OUTPUT_ROOT, "all_articles_summary_03.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "total_measured_selection_cost_jpy": round(sum(cumulative), 4)},
                   f, ensure_ascii=False, indent=2)
    print(f"Done. total_measured_selection_cost_jpy={round(sum(cumulative), 4)}")


if __name__ == "__main__":
    main()
