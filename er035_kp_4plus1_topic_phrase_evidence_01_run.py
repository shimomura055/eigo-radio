# ============================================================
# er035_kp_4plus1_topic_phrase_evidence_01_run.py
# KEY-PHRASE-4PLUS1-TOPIC-PHRASE-PRODUCTION-01: Phase B検証evidence
# ============================================================
# 既存evidence runnerの雛形(er030_key_phrase_db_hybrid_source_reference_
# contract_01_evidence_run_02.py)を流用し、Production経路run_key_phrases
# 相当をDB Hybrid(Family X本文)/Strategy L(Family Z・legacy Family B/C
# 本文、およびDB Hybrid fallback強制1件)で呼ぶ。read-only既存article本文
# のみを入力とし、新規テーマ生成・既存Production記事ディレクトリの
# keywords*.json上書きは一切行わない(出力先はer035_output/配下のみ)。
#
# 実行方法:
#   .venv/Scripts/python.exe er035_kp_4plus1_topic_phrase_evidence_01_run.py
#     --out-dir er035_output/kp_4plus1_evidence_01 --budget-jpy 80
# ============================================================

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter

import er003_v1_n3_01_scaffold_generate as sc

# Family X News(DB Hybrid、既存evidence[KEY-PHRASE-DB-HYBRID-SOURCE-
# REFERENCE-CONTRACT-PRODUCTION-WIRING-01]と同一本文を再利用)。
DB_HYBRID_RUNS = [
    {"key": "meta_a2", "path": "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md",
     "level": "a2", "process": "A2_SUPPORT", "family": "Family X News (Meta)"},
    {"key": "meta_b1b", "path": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md",
     "level": "b1b", "process": "B1_SUPPORT", "family": "Family X News (Meta)"},
    {"key": "hormuz_a2", "path": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
     "level": "a2", "process": "A2_SUPPORT", "family": "Family X News (Hormuz)"},
    {"key": "hormuz_b1b", "path": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
     "level": "b1b", "process": "B1_SUPPORT", "family": "Family X News (Hormuz)"},
]

# Family Z Fiction / legacy Family B(Voices)・Family C(twins)。DB Hybridは
# Family X Primaryのみ配線済みのため、これらはStrategy L全文方式で読む
# (Fable判断: Family固有ruleは追加せず、共通Production経路の既定分岐
# [kp_backend既定"strategy_l"]をそのまま使うだけ)。
STRATEGY_L_RUNS = [
    {"key": "melos_a2", "path": "er026_output/family_z_production_e2e_01/melos/run_01/article.md",
     "level": "a2", "process": "A2_SUPPORT", "family": "Family Z Fiction (Melos)"},
    {"key": "twins_a2",
     "path": "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt",
     "level": "a2", "process": "A2_SUPPORT", "family": "legacy Family C Fiction (twins)"},
    {"key": "twins_b1",
     "path": "er013_output/family_c_episode_trial_12/twins_b1/article_normalized.txt",
     "level": "b1", "process": "B1_SUPPORT", "family": "legacy Family C Fiction (twins)"},
    {"key": "ai_hiring_a2",
     "path": "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md",
     "level": "a2", "process": "A2_SUPPORT", "family": "legacy Family B (Voices, ai_hiring)"},
]

# 既存の確立済み手法(er030_key_phrase_db_hybrid_source_reference_
# contract_01_evidence_run.py::_run_forced_fallback)を踏襲: 短い記事で
# SHORTLIST_TOO_SMALLを自然発火させ、Strategy Lへ実際にfallbackさせる。
FALLBACK_FORCED_TEXT = "# Tiny Article\n\nCats sit. Dogs run. Birds fly away quickly today."


def _load(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _role_counts(items):
    if not items:
        return None
    return dict(Counter(it.get("key_phrase_role") for it in items if isinstance(it, dict)))


def _topic_item(items):
    if not items:
        return None
    for it in items:
        if isinstance(it, dict) and it.get("key_phrase_role") == "topic":
            return it
    return None


def _stage1_topic_presence(out_dir: str, topic_item: dict):
    """観点7(DB Hybridのみ): topic役割item(既にschema enum制約により
    Stage1 shortlistの候補一覧に必ず存在する)が、shortlist内でどの候補
    区分(important_noun_phrase_candidate等)に由来したかを機械的に記録
    する(存在の有無そのものはschema上構造的に保証されるため、質的な
    由来区分の記録が目的)。"""
    debug_path = os.path.join(out_dir, "key_phrases_db_hybrid", "db_hybrid_stage1_debug.json")
    if not topic_item or not os.path.exists(debug_path):
        return {"available": False}
    try:
        with open(debug_path, encoding="utf-8") as f:
            stage1 = json.load(f)
    except Exception as e:  # pragma: no cover (診断目的、evidence欠損時も処理継続)
        return {"available": False, "error": str(e)}
    target_span = (topic_item.get("source_span") or "").strip().lower()
    target_display = (topic_item.get("display_phrase") or "").strip().lower()
    matches = []
    for bucket_name, bucket in stage1.items():
        if not isinstance(bucket, list):
            continue
        for c in bucket:
            if not isinstance(c, dict):
                continue
            surface = (c.get("surface_form") or "").strip().lower()
            canonical = (c.get("canonical_form") or "").strip().lower()
            if surface in (target_span, target_display) or canonical in (target_span, target_display):
                matches.append({"bucket": bucket_name, "candidate": c})
    return {"available": True, "matches": matches, "match_count": len(matches)}


def _run_one(article_key: str, article_path_or_text: str, level: str, process: str, family: str,
             kp_backend: str, cumulative: list, out_root: str, is_raw_text: bool = False) -> dict:
    os.makedirs(out_root, exist_ok=True)
    article_text = article_path_or_text if is_raw_text else _load(article_path_or_text)
    out_dir = os.path.join(out_root, article_key)
    kp_dir = os.path.join(out_dir, "key_phrases")
    article_id = f"KP_4PLUS1_EVIDENCE_01_{article_key.upper()}"

    print(f"=== {article_key} (family={family}, kp_backend={kp_backend}) ===")
    t0 = time.time()
    kp = sc.run_key_phrases(article_text, kp_dir, article_id, level, process=process, kp_backend=kp_backend)
    elapsed = time.time() - t0

    selection = kp["selection"]
    cost_jpy = selection.get("cost_jpy")
    if cost_jpy:
        cumulative.append(cost_jpy)

    canon = kp.get("canonicalization") or {}
    merged_items = (canon.get("merged") or {}).get("items") if canon else None
    redundancy = kp.get("redundancy_qa") or {}
    original_items = selection.get("original_items") or []
    original_by_rank = {it.get("rank"): it for it in original_items if isinstance(it, dict)}

    # canonicalization工程はmerge_canonicalization_result()のwhitelistで
    # 再構成されるため、selection_reason/phrase_type等の選定時点フィールド
    # はmerged itemには残らない(仕様どおり)。観点2(選定理由をそのまま
    # 転記)のため、rank一致でoriginal_items(選定直後、canonicalization前)
    # から補完する。
    display_items = []
    for it in (merged_items or original_items):
        orig = original_by_rank.get(it.get("rank"), {})
        display_items.append({
            "rank": it.get("rank"), "key_phrase_role": it.get("key_phrase_role"),
            "display_phrase": it.get("display_phrase"), "key_phrase": it.get("key_phrase"),
            "japanese_gloss": it.get("japanese_gloss") or it.get("ja_gloss"),
            "selection_reason": orig.get("selection_reason"),
            "phrase_type": orig.get("phrase_type"),
        })

    topic_display = _topic_item(display_items)
    topic = _topic_item(merged_items) if merged_items else _topic_item(original_items)
    stage1_presence = (_stage1_topic_presence(kp_dir, topic)
                        if kp_backend == "db_hybrid" and selection.get("status") == "KEY_WORDS_STRUCTURE_PASS"
                        else {"available": False, "reason": "not_db_hybrid_or_not_pass"})

    result = {
        "article_key": article_key, "article_id": article_id, "family": family, "level": level,
        "kp_backend_requested": kp_backend, "kp_backend_used": selection.get("kp_backend_used"),
        "kp_backend_fallback_reason_code": selection.get("kp_backend_fallback_reason_code"),
        "selection_status": selection.get("status"),
        "selection_cost_jpy": cost_jpy,
        "selection_model_id": selection.get("model_id"),
        "shortlist_total_count": selection.get("shortlist_total_count"),
        "source_reference_contract": selection.get("source_reference_contract"),
        "selection_contract": selection.get("selection_contract"),
        "role_counts": _role_counts(selection.get("original_items")),
        "canonicalization_status": canon.get("status"),
        "redundancy_qa_status": redundancy.get("status"),
        "redundancy_retry_attempts": kp.get("redundancy_retry_attempts"),
        "final_5_items": display_items,
        "topic_item_raw": topic,
        "topic_item_selection_reason": (topic_display or {}).get("selection_reason"),
        "stage1_topic_presence": stage1_presence,
        "elapsed_sec": round(elapsed, 2),
        "cumulative_measured_selection_cost_jpy_so_far": round(sum(cumulative), 4),
    }
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "evidence_summary.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  kp_backend_used={result['kp_backend_used']} status={result['selection_status']} "
          f"role_counts={result['role_counts']} cost_jpy={result['selection_cost_jpy']} "
          f"canon={result['canonicalization_status']} redundancy={result['redundancy_qa_status']} "
          f"cumulative={result['cumulative_measured_selection_cost_jpy_so_far']}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=os.path.join("er035_output", "kp_4plus1_evidence_01"))
    parser.add_argument("--budget-jpy", type=float, default=80.0)
    args = parser.parse_args()

    # canonicalization/Redundancy QA自体は既存Productionが元々cost計測して
    # いないため(OPEN-206既知の限界)、measured selection cost合計が
    # budget-jpyの半分に達したら以降のrunを打ち切る(安全マージン)。
    stop_threshold = args.budget_jpy / 2.0

    cumulative = []
    results = {}

    for spec in DB_HYBRID_RUNS:
        if sum(cumulative) > stop_threshold:
            print(f"[BUDGET STOP] 累積実測¥{sum(cumulative):.4f}が上限¥{stop_threshold}を"
                  f"超えたため、{spec['key']}以降は実行せず打ち切ります。")
            break
        results[spec["key"]] = _run_one(
            spec["key"], spec["path"], spec["level"], spec["process"], spec["family"],
            "db_hybrid", cumulative, args.out_dir)

    for spec in STRATEGY_L_RUNS:
        if sum(cumulative) > stop_threshold:
            print(f"[BUDGET STOP] 累積実測¥{sum(cumulative):.4f}が上限¥{stop_threshold}を"
                  f"超えたため、{spec['key']}以降は実行せず打ち切ります。")
            break
        results[spec["key"]] = _run_one(
            spec["key"], spec["path"], spec["level"], spec["process"], spec["family"],
            "strategy_l", cumulative, args.out_dir)

    if sum(cumulative) <= stop_threshold:
        results["forced_fallback"] = _run_one(
            "forced_fallback", FALLBACK_FORCED_TEXT, "a2", "A2_SUPPORT",
            "N/A (forced SHORTLIST_TOO_SMALL -> Strategy L fallback)",
            "db_hybrid", cumulative, args.out_dir, is_raw_text=True)
    else:
        print(f"[BUDGET STOP] forced_fallbackは残予算不足のため実行しませんでした"
              f"(累積実測¥{sum(cumulative):.4f})。")

    summary = {
        "results": results,
        "total_measured_selection_cost_jpy": round(sum(cumulative), 4),
        "budget_jpy": args.budget_jpy,
        "stop_threshold_jpy": stop_threshold,
        "run_count": len(results),
    }
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Done. run_count={len(results)} total_measured_selection_cost_jpy={round(sum(cumulative), 4)}")


if __name__ == "__main__":
    main()
