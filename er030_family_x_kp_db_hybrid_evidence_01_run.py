# ============================================================
# er030_family_x_kp_db_hybrid_evidence_01_run.py
# KEY-PHRASE-DB-HYBRID-FAMILY-X-PRODUCTION-WIRING-01
# ============================================================
# Guardrail ¥40。Family X既存記事(Meta A2/B1B、Hormuz A2/B1B)に対し、
# 実Production共有入口 er003_v1_n3_01_scaffold_generate.run_key_phrases()
# を kp_backend="db_hybrid" で実行する(選定→canonicalization→
# Key Phrase Set Redundancy QAの全工程、既存Gate無変更)。
#
# 既存Production artifact(er019_output配下のkeywords_canonicalized.json
# 等)は一切上書きしない。出力は本ファイル専用の
# er030_output/family_x_kp_db_hybrid_evidence_01/<article_key>/ 配下。
#
# 追加で、1本文(hormuz_a2)だけcost guardを一時的に極小値へ
# monkeypatchし、DB Hybrid selectorがCOST_GUARD_EXCEEDEDで実際に失敗し
# Strategy L全文方式へ実fallbackすることを実測する(強制failure注入、
# 実際に2回分のLLM呼び出し[db_hybrid選定+fallback選定]+
# canonicalization+redundancy QAが発生するため¥1程度追加でかかる)。
# ============================================================

from __future__ import annotations

import json
import os
import time
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er030_key_phrase_db_hybrid_selector_01 as db_hybrid

OUTPUT_ROOT = os.path.join("er030_output", "family_x_kp_db_hybrid_evidence_01")

ARTICLES = {
    "meta_a2": ("er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md", "a2", "A2_SUPPORT"),
    "meta_b1b": ("er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md", "b1b", "B1_SUPPORT"),
    "hormuz_a2": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md", "a2", "A2_SUPPORT"),
    "hormuz_b1b": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md", "b1b", "B1_SUPPORT"),
}

FORCED_FALLBACK_ARTICLE_KEY = "hormuz_a2"


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def run_one(article_key: str, article_path: str, level: str, process: str, force_fallback: bool = False) -> dict:
    print(f"=== {article_key} (force_fallback={force_fallback}) ===")
    article_text = _load(article_path)
    suffix = "_forced_fallback" if force_fallback else ""
    out_dir = os.path.join(OUTPUT_ROOT, article_key + suffix, "key_phrases")
    article_id = f"FAMILY_X_KP_DB_HYBRID_EVIDENCE_{article_key.upper()}{suffix.upper()}"

    t0 = time.time()
    if force_fallback:
        with mock.patch.object(db_hybrid, "DEFAULT_COST_GUARD_JPY", 0.0001):
            kp = sc.run_key_phrases(article_text, out_dir, article_id, level, process=process,
                                     kp_backend="db_hybrid")
    else:
        kp = sc.run_key_phrases(article_text, out_dir, article_id, level, process=process,
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
        "article_key": article_key, "article_id": article_id, "level": level,
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
    os.makedirs(os.path.join(OUTPUT_ROOT, article_key + suffix), exist_ok=True)
    with open(os.path.join(OUTPUT_ROOT, article_key + suffix, "evidence_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  kp_backend_used={result['kp_backend_used']} status={result['selection_status']} "
          f"cost_jpy={result['selection_cost_jpy']} shortlist={result['shortlist_total_count']} "
          f"canon={result['canonicalization_status']} redundancy={result['redundancy_qa_status']}")
    return result


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    all_results = {}
    for article_key, (path, level, process) in ARTICLES.items():
        all_results[article_key] = run_one(article_key, path, level, process, force_fallback=False)

    forced_path, forced_level, forced_process = ARTICLES[FORCED_FALLBACK_ARTICLE_KEY]
    all_results[FORCED_FALLBACK_ARTICLE_KEY + "_forced_fallback"] = run_one(
        FORCED_FALLBACK_ARTICLE_KEY, forced_path, forced_level, forced_process, force_fallback=True)

    with open(os.path.join(OUTPUT_ROOT, "all_evidence_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("Done.")
    return all_results


if __name__ == "__main__":
    main()
