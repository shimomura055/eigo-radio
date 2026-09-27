# ============================================================
# er030_family_x_kp_db_hybrid_evidence_02_run.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01(修正1回目後の
# post-fix runtime evidence、Gate 3最終項目)
# ============================================================
# Guardrail ¥20(見積り約¥1〜2、Hormuz A2 1記事のみ)。修正1回目
# (commit bfd7090e、Opus L2所見BLOCKER 3件[B1 telemetry観測性/B2
# per-article traceability/B3 routing違反fallback吸収]反映後)の
# 実runtime evidenceを、既存evidence_01と同じ実Production共有入口
# er003_v1_n3_01_scaffold_generate.run_key_phrases(kp_backend=
# "db_hybrid")経由で取得する。
#
# 既存Production artifact(er019_output配下のkeywords_canonicalized.json
# 等、Stage 3fでAssembly済みのHormuz A2本番成果物含む)は一切上書きしない。
# 出力は本ファイル専用の
# er030_output/family_x_kp_db_hybrid_evidence_02/hormuz_a2/ 配下のみ。
#
# B3(routing契約違反→fallback不可でSTOP)は課金せずmock注入testで
# 既に再確認済み(er030_key_phrase_db_hybrid_family_x_production_
# wiring_01_test.pyの該当test、本スクリプトでは実行しない)。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_v1_n3_01_scaffold_generate as sc

OUTPUT_ROOT = os.path.join("er030_output", "family_x_kp_db_hybrid_evidence_02")

ARTICLE_KEY = "hormuz_a2"
ARTICLE_PATH = "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md"
LEVEL = "a2"
PROCESS = "A2_SUPPORT"


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    article_text = _load(ARTICLE_PATH)
    out_dir = os.path.join(OUTPUT_ROOT, ARTICLE_KEY, "key_phrases")
    article_id = f"FAMILY_X_KP_DB_HYBRID_EVIDENCE_02_{ARTICLE_KEY.upper()}"

    print(f"=== {ARTICLE_KEY} (post-fix evidence, kp_backend=db_hybrid) ===")
    t0 = time.time()
    kp = sc.run_key_phrases(article_text, out_dir, article_id, LEVEL, process=PROCESS,
                             kp_backend="db_hybrid")
    elapsed = time.time() - t0

    selection = kp["selection"]
    final_items = []
    if selection.get("original_items"):
        final_items = [{"rank": it.get("rank"), "display_phrase": it.get("display_phrase"),
                         "phrase_type": it.get("phrase_type"), "source_sentence": it.get("source_sentence")}
                        for it in selection["original_items"]]

    canon_items = None
    if kp.get("canonicalization") and kp["canonicalization"].get("merged"):
        canon_items = [{"rank": it.get("rank"), "used_form": it.get("used_form"),
                        "japanese_gloss": it.get("japanese_gloss")}
                       for it in kp["canonicalization"]["merged"]["items"]]

    result = {
        "article_key": ARTICLE_KEY, "article_id": article_id, "level": LEVEL,
        "kp_backend_used": selection.get("kp_backend_used"),
        "kp_backend_fallback_reason_code": selection.get("kp_backend_fallback_reason_code"),
        "selection_status": selection.get("status"),
        "selection_cost_jpy": selection.get("cost_jpy"),
        "selection_model_id": selection.get("model_id"),
        "shortlist_total_count": selection.get("shortlist_total_count"),
        "canonicalization_status": (kp.get("canonicalization") or {}).get("status"),
        "redundancy_qa_status": (kp.get("redundancy_qa") or {}).get("status"),
        "redundancy_retry_attempts": kp.get("redundancy_retry_attempts"),
        "final_selected_items_raw": final_items,
        "final_canonicalized_items": canon_items,
        "elapsed_sec": round(elapsed, 2),
    }
    os.makedirs(os.path.join(OUTPUT_ROOT, ARTICLE_KEY), exist_ok=True)
    with open(os.path.join(OUTPUT_ROOT, ARTICLE_KEY, "evidence_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  kp_backend_used={result['kp_backend_used']} status={result['selection_status']} "
          f"cost_jpy={result['selection_cost_jpy']} shortlist={result['shortlist_total_count']} "
          f"canon={result['canonicalization_status']} redundancy={result['redundancy_qa_status']}")
    print("Done.")
    return result


if __name__ == "__main__":
    main()
