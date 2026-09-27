# ============================================================
# er030_key_phrase_db_hybrid_source_reference_contract_01_evidence_run.py
# KEY-PHRASE-DB-HYBRID-SOURCE-REFERENCE-CONTRACT-PRODUCTION-WIRING-01
# ============================================================
# Guardrail ¥40(委任文)。実行前に既にtest修正時の事故(§REPORT参照、
# 旧mock対象を新しいsrc_ref_contract呼び出し先へ切り替え忘れたことに
# より、2件のunit testが実際にOpenAI APIを呼び出してしまい実測¥20.7826
# を消費した)があったため、本evidence runの実行前残予算は
# 40 - 20.7826 = 19.2174円である。この制約下で、実Production共有入口
# `sc.run_key_phrases(kp_backend="db_hybrid")`を用いて以下を実行する
# (規模を縮小、詳細はREPORT参照):
#   1. Hormuz A2(Family X、既存Production regression確認用)
#   2. twins A2(quote-heavy、既知失敗事例、x1)
#   3. Melos A2(Family Z由来テキスト、quote-heavy、既知失敗事例、x1、
#      同じ共有入口へテキストを直接渡すだけでFamily X runnerは使わない)
#   4. 強制SHORTLIST_TOO_SMALL注入によるfallback 1回(短い記事、
#      db_hybrid自体はAPI呼び出し前に失敗するため¥0、Strategy L
#      fallbackのみ課金)
#
# 各記事の実行後にcost_jpyを確認し、残予算に近づいた場合は後続の記事を
# 実行せず打ち切る(実測値のみを記録する、推測でPASS報告しない)。
#
# 既存Production artifact(er019_output配下)は一切上書きしない。出力は
# 本ファイル専用の
# er030_output/family_x_kp_source_reference_contract_evidence_01/ 配下のみ。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_v1_n3_01_scaffold_generate as sc

OUTPUT_ROOT = os.path.join("er030_output", "family_x_kp_source_reference_contract_evidence_01")

REMAINING_BUDGET_JPY = 19.2174

ARTICLES = [
    {
        "key": "hormuz_a2",
        "path": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
        "level": "a2", "process": "A2_SUPPORT",
    },
    {
        "key": "twins_a2",
        "path": "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt",
        "level": "a2", "process": "A2_SUPPORT",
    },
    {
        "key": "melos_a2",
        "path": "er026_output/family_z_production_e2e_01/melos/run_01/article.md",
        "level": "a2", "process": "A2_SUPPORT",
    },
]

FALLBACK_FORCED_TEXT = (
    "# Tiny Article\n\nCats sit. Dogs run. Birds fly away quickly today."
)


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _run_one(article_key: str, article_path: str, level: str, process: str, cumulative: list) -> dict:
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    article_text = _load(article_path)
    out_dir = os.path.join(OUTPUT_ROOT, article_key, "key_phrases")
    article_id = f"KP_SRC_REF_CONTRACT_EVIDENCE_01_{article_key.upper()}"

    print(f"=== {article_key} (source reference contract evidence, kp_backend=db_hybrid) ===")
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
            "source_sentence": it.get("source_sentence"), "source_span": it.get("source_span"),
        } for it in selection["original_items"]]

    canon_items = None
    if kp.get("canonicalization") and kp["canonicalization"].get("merged"):
        canon_items = [{
            "rank": it.get("rank"), "used_form": it.get("used_form"),
            "source_reference_contract": it.get("source_reference_contract"),
            "source_candidate_id": it.get("source_candidate_id"),
        } for it in kp["canonicalization"]["merged"]["items"]]

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
        "final_canonicalized_items": canon_items,
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


def _run_forced_fallback(cumulative: list) -> dict:
    """SHORTLIST_TOO_SMALLをAPI呼び出し前に発火させ(db_hybrid selector自体は
    ¥0)、Strategy L fallbackへ実際に切り替わることと、telemetry上で
    source_reference_contract="free_text_strategy_l"のタグが付くことを
    実測する。"""
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    out_dir = os.path.join(OUTPUT_ROOT, "forced_fallback", "key_phrases")
    article_id = "KP_SRC_REF_CONTRACT_EVIDENCE_01_FORCED_FALLBACK"
    print("=== forced_fallback (SHORTLIST_TOO_SMALL -> Strategy L fallback) ===")
    t0 = time.time()
    kp = sc.run_key_phrases(FALLBACK_FORCED_TEXT, out_dir, article_id, "a2", process="A2_SUPPORT",
                             kp_backend="db_hybrid")
    elapsed = time.time() - t0
    selection = kp["selection"]
    cost_jpy = selection.get("cost_jpy")
    if cost_jpy:
        cumulative.append(cost_jpy)
    result = {
        "kp_backend_used": selection.get("kp_backend_used"),
        "kp_backend_fallback_reason_code": selection.get("kp_backend_fallback_reason_code"),
        "selection_status": selection.get("status"),
        "selection_cost_jpy": cost_jpy,
        "elapsed_sec": round(elapsed, 2),
        "cumulative_measured_cost_jpy_so_far": round(sum(cumulative), 4),
    }
    os.makedirs(os.path.join(OUTPUT_ROOT, "forced_fallback"), exist_ok=True)
    with open(os.path.join(OUTPUT_ROOT, "forced_fallback", "evidence_summary.json"), "w",
              encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  kp_backend_used={result['kp_backend_used']} "
          f"fallback_reason_code={result['kp_backend_fallback_reason_code']} "
          f"cost_jpy={result['selection_cost_jpy']} cumulative={result['cumulative_measured_cost_jpy_so_far']}")
    return result


def main():
    cumulative = []
    results = {}
    for spec in ARTICLES:
        if sum(cumulative) > REMAINING_BUDGET_JPY - 2.0:
            print(f"[BUDGET STOP] 累積実測¥{sum(cumulative):.4f}が残予算¥{REMAINING_BUDGET_JPY}に接近したため、"
                  f"{spec['key']}以降は実行せず打ち切ります。")
            break
        results[spec["key"]] = _run_one(spec["key"], spec["path"], spec["level"], spec["process"], cumulative)

    if sum(cumulative) <= REMAINING_BUDGET_JPY - 0.5:
        results["forced_fallback"] = _run_forced_fallback(cumulative)
    else:
        print(f"[BUDGET STOP] forced_fallbackは残予算不足のため実行しませんでした"
              f"(累積実測¥{sum(cumulative):.4f})。")

    summary = {
        "results": results,
        "total_measured_selection_cost_jpy": round(sum(cumulative), 4),
        "remaining_budget_jpy_before_run": REMAINING_BUDGET_JPY,
    }
    with open(os.path.join(OUTPUT_ROOT, "all_articles_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Done. total_measured_selection_cost_jpy={summary['total_measured_selection_cost_jpy']}")
    return summary


if __name__ == "__main__":
    main()
