# ============================================================
# er030_key_phrase_db_hybrid_source_reference_contract_01_evidence_run_02.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
# ============================================================
# evidence_run(1回目)が想定より安価だった(measured selection cost合計
# ¥3.2178、記事4件[hormuz_a2/twins_a2/melos_a2/forced_fallback])ため、
# 残予算内で追加evidenceを取得する(委任文の完全な規模[Meta A2/B1B・
# Hormuz A2/B1B・twins A2×3・Melos A2×3]には遠く及ばないが、量産規模の
# 反復安定性[twins A2/Melos A2の2サンプル追加、計×3]とMeta A2[Family X
# 2本目]を追加する)。
#
# 残予算の考え方: Guardrail¥40 - 事故的実測¥20.7826(test修正時、REPORT
# 参照)- 1回目evidence measured selection ¥3.2178 = 残り約¥15.9996
# (canonicalization/Redundancy QAの未計測分[OPEN-206既知の限界]を考慮し、
# 本スクリプトのmeasured selection cost合計が¥8を超えたら打ち切る)。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_v1_n3_01_scaffold_generate as sc

OUTPUT_ROOT = os.path.join("er030_output", "family_x_kp_source_reference_contract_evidence_01")

SELECTION_COST_STOP_JPY = 8.0

RUNS = [
    {"key": "meta_a2", "path": "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md",
     "level": "a2", "process": "A2_SUPPORT"},
    {"key": "twins_a2_s2",
     "path": "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt",
     "level": "a2", "process": "A2_SUPPORT"},
    {"key": "twins_a2_s3",
     "path": "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt",
     "level": "a2", "process": "A2_SUPPORT"},
    {"key": "melos_a2_s2", "path": "er026_output/family_z_production_e2e_01/melos/run_01/article.md",
     "level": "a2", "process": "A2_SUPPORT"},
    {"key": "melos_a2_s3", "path": "er026_output/family_z_production_e2e_01/melos/run_01/article.md",
     "level": "a2", "process": "A2_SUPPORT"},
]


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _run_one(article_key: str, article_path: str, level: str, process: str, cumulative: list) -> dict:
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    article_text = _load(article_path)
    out_dir = os.path.join(OUTPUT_ROOT, article_key, "key_phrases")
    article_id = f"KP_SRC_REF_CONTRACT_EVIDENCE_01_{article_key.upper()}"

    print(f"=== {article_key} (source reference contract evidence 02, kp_backend=db_hybrid) ===")
    t0 = time.time()
    kp = sc.run_key_phrases(article_text, out_dir, article_id, level, process=process,
                             kp_backend="db_hybrid")
    elapsed = time.time() - t0

    selection = kp["selection"]
    cost_jpy = selection.get("cost_jpy")
    if cost_jpy:
        cumulative.append(cost_jpy)

    final_items = []
    if selection.get("original_items"):
        final_items = [{
            "rank": it.get("rank"), "display_phrase": it.get("display_phrase"),
            "source_candidate_id": it.get("source_candidate_id"),
            "surface_echo": it.get("surface_echo"),
            "source_reference_contract": it.get("source_reference_contract"),
            "candidate_mismatch_suspected": it.get("candidate_mismatch_suspected"),
        } for it in selection["original_items"]]

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
        "final_selected_items_raw": final_items,
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

    summary_path = os.path.join(OUTPUT_ROOT, "all_articles_summary_02.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({"results": results, "total_measured_selection_cost_jpy": round(sum(cumulative), 4)},
                   f, ensure_ascii=False, indent=2)
    print(f"Done. total_measured_selection_cost_jpy={round(sum(cumulative), 4)}")


if __name__ == "__main__":
    main()
