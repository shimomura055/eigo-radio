# ============================================================
# er031_key_phrase_db_hybrid_family_z_trial_01_run.py
# KEY-PHRASE-DB-HYBRID-FAMILY-Z-CORE-APPLICABILITY-TRIAL-01
# ============================================================
# 目的: Family X向けCommon DB Hybrid Core(er029_key_phrase_db_hybrid_
# trial_04、baseline=commit 57b61273)が、Fiction/Story系のFamily Zでも
# 有効かを確認する。er029/er028/er027/er003_key_words_*は一切変更しない
# (import/read-onlyのみ)。新しいDB追加・Core側候補生成ロジックの変更は
# 行わない。
#
# Z0: er029 Coreをそのまま(Family Z固有ルールなし)実行する条件。
#     run4.run_one_article(=er029の本番run関数、無変更)をそのまま呼ぶ。
# Z1: 同じCore Stage1/shortlist(run4.run_stage1_and_shortlist_v4、無変更)
#     を使うが、最終選定LLMへ渡すprompt文言だけをFamily Z固有guidance
#     (er031_..._rules.build_lightweight_user_message_z1)へ差し替える
#     条件。
#
# 素材: er026_output/family_z_production_e2e_01/melos/run_01/article.md
# (Family Z実データ、Public Domain文学リライト、既存Production記事)。
# 新規記事生成・新規Writer/Preview/Comment LLM callは一切行わない
# (既存artifactの読み取りのみ)。実LLM callはZ0/Z1のKey Phrase最終選定
# selectorのみ、本文1件につき1 call(max_attempts=1、既存run_selector_
# onceを無変更のまま再利用)。
#
# 参考(twins_a2/twins_b1、dialogue-heavy): 新規実行しない。
# er029_output/key_phrase_db_hybrid_trial_04/{twins_a2,twins_b1}/
# の既存artifact(Trial-04で既に生成済み)を読み取り専用で参照する。
# ============================================================

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er006_model_routing_contract_01 as routing
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er031_key_phrase_db_hybrid_family_z_trial_01_rules as z_rules

OUTPUT_ROOT = os.path.join("er031_output", "key_phrase_db_hybrid_family_z_trial_01")

MELOS_ARTICLE_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"
MELOS_PROCESS = "A2_SUPPORT"  # article_config.json source_level="A2"相当(既存Family Z Production記録を参照)

# 既存Family Z Production公開Key Phrase(参考比較用、er026 melos run_01
# keywords_canonicalized.json由来、変更しない)。
EXISTING_PRODUCTION_KP_MELOS = [
    "in someone's place", "execution", "give one's word", "fair trial", "loyalty",
]

# 参考(twins、既存artifact読み取りのみ、新規実行なし)
TWINS_REFERENCE_DIRS = {
    "twins_a2": os.path.join("er029_output", "key_phrase_db_hybrid_trial_04", "twins_a2"),
    "twins_b1": os.path.join("er029_output", "key_phrase_db_hybrid_trial_04", "twins_b1"),
}

COST_STOP_THRESHOLD_JPY = 25.0  # ユーザー指示Guardrail¥30のSTOP閾値¥25


def run_one_article_z1(article_key: str, article_path: str, process: str,
                        dbs: dict, cost_tracker: "base._RunningCost", static_instructions: str,
                        out_dir: str, existing_production_kp=None) -> dict:
    """Z1条件: Core Stage1/shortlist(run4、無変更)は共通のまま、最終選定
    promptだけをFamily Z固有guidanceへ差し替えて実行する。"""
    print(f"=== {article_key} (Z1) ===")
    article_text = open(article_path, encoding="utf-8").read()
    os.makedirs(out_dir, exist_ok=True)

    title = base.extract_article_title(article_text)
    s1r = run4.run_stage1_and_shortlist_v4(article_text, dbs, title)
    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    stops = base.check_stop_conditions(article_key, stage1, shortlist_info)

    model = routing.require_model(process, routing.SUPPORT_MODEL)
    lightweight_message = z_rules.build_lightweight_user_message_z1(
        title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
    base.assert_no_full_article_body(lightweight_message, article_text)
    with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(lightweight_message)

    hybrid_result = base.run_selector_once(
        f"HYBRIDZ1_{article_key.upper()}", article_text, lightweight_message, model,
        cost_tracker, label=f"{article_key}_z1")

    final_selected = []
    if hybrid_result["parsed"]:
        final_selected = [it.get("display_phrase") for it in hybrid_result["parsed"].get("items", [])]
    existing_kp = existing_production_kp or []
    overlap = sorted(set(x.lower() for x in final_selected) & set(x.lower() for x in existing_kp))

    article_result = {
        "condition": "Z1_family_z_selection_rule",
        "article_key": article_key,
        "article_path": article_path,
        "article_title": title,
        "article_word_count_approx": len(article_text.split()),
        "shortlist_info": {
            "phrase_included_count": shortlist_info["phrase_included_count"],
            "important_noun_included_count": shortlist_info["important_noun_included_count"],
            "word_included_count": shortlist_info["word_included_count"],
            "shortlist_total_count": shortlist_info["shortlist_total_count"],
            "shortlist": shortlist_info["shortlist"],
            "sentence_reference_count": len(shortlist_info["sentence_reference"]),
        },
        "z1_selector_result": hybrid_result,
        "existing_production_kp": existing_kp,
        "z1_final_selected_display_phrases": final_selected,
        "overlap_with_existing_production_kp": overlap,
        "overlap_count": len(overlap) if existing_production_kp else None,
        "stop_conditions_triggered": stops,
        "prompt_char_len": len(lightweight_message),
        "article_char_len": len(article_text),
    }
    with open(os.path.join(out_dir, "hybridz1_trial_result.json"), "w", encoding="utf-8") as f:
        json.dump(article_result, f, ensure_ascii=False, indent=2)

    def _serializable_stage1(st):
        return {k: v for k, v in st.items() if k != "sentence_units"}

    with open(os.path.join(out_dir, "stage1_debug.json"), "w", encoding="utf-8") as f:
        json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

    print(f"  shortlist={shortlist_info['shortlist_total_count']}, "
          f"z1_status={hybrid_result['status']}, stops={stops}, "
          f"prompt_chars={len(lightweight_message)} (article_chars={len(article_text)})")
    return article_result


def load_twins_reference() -> dict:
    """参考(twins_a2/twins_b1)の既存artifact(Trial-04で既に生成済み)を
    読み取り専用で参照する。新規実行・新規API callは一切行わない。"""
    ref = {}
    for key, out_dir in TWINS_REFERENCE_DIRS.items():
        path = os.path.join(out_dir, "hybrid4_trial_result.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            ref[key] = {
                "final_selected": d.get("trial04_final_selected_display_phrases"),
                "existing_production_kp": d.get("existing_production_kp"),
                "overlap": d.get("overlap_with_existing_production_kp"),
                "shortlist_total_count": d.get("shortlist_info", {}).get("shortlist_total_count"),
            }
        else:
            ref[key] = {"note": "artifact not found (read-only reference, not re-run)"}
    return ref


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = base._RunningCost(COST_STOP_THRESHOLD_JPY)
    static_instructions = base.extract_static_instructions(bk.load_prompt_template())

    all_results = {}

    try:
        # --- Z0: er029 Coreをそのまま実行(Family Z固有ルールなし) ---
        z0_out_dir = os.path.join(OUTPUT_ROOT, "z0_melos")
        z0_result = run4.run_one_article(
            "melos", MELOS_ARTICLE_PATH, MELOS_PROCESS, "The Three-Day Promise",
            dbs, cost_tracker, static_instructions, "HYBRIDZ0", z0_out_dir,
            existing_production_kp=EXISTING_PRODUCTION_KP_MELOS)
        all_results["z0_melos"] = z0_result

        # --- Z1: 同じCore shortlistにFamily Z固有選定ruleを適用 ---
        z1_out_dir = os.path.join(OUTPUT_ROOT, "z1_melos")
        z1_result = run_one_article_z1(
            "melos", MELOS_ARTICLE_PATH, MELOS_PROCESS,
            dbs, cost_tracker, static_instructions, z1_out_dir,
            existing_production_kp=EXISTING_PRODUCTION_KP_MELOS)
        all_results["z1_melos"] = z1_result

    except base.CostGuardrailStop as e:
        print(f"STOP: {e}")
        with open(os.path.join(OUTPUT_ROOT, "cost_guardrail_stop.json"), "w", encoding="utf-8") as f:
            json.dump({"reason": str(e), "completed_conditions": list(all_results.keys()),
                       "cost_so_far_jpy": cost_tracker.total_jpy}, f, ensure_ascii=False, indent=2)

    twins_reference = load_twins_reference()
    with open(os.path.join(OUTPUT_ROOT, "twins_reference_readonly.json"), "w", encoding="utf-8") as f:
        json.dump(twins_reference, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUTPUT_ROOT, "raw_usage_log.jsonl"), "w", encoding="utf-8") as f:
        for call in cost_tracker.calls:
            f.write(json.dumps(call, ensure_ascii=False) + "\n")
    with open(os.path.join(OUTPUT_ROOT, "cost.json"), "w", encoding="utf-8") as f:
        json.dump({"total_jpy": round(cost_tracker.total_jpy, 4), "calls": cost_tracker.calls},
                   f, ensure_ascii=False, indent=2)

    print("Done. Total cost JPY:", round(cost_tracker.total_jpy, 4))
    return all_results


if __name__ == "__main__":
    main()
