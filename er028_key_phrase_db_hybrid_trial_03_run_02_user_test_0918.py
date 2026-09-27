# ============================================================
# er028_key_phrase_db_hybrid_trial_03_run_02_user_test_0918.py
# KEY-PHRASE-DB-HYBRID-TRIAL-03 追加評価run(ユーザー指定 2026-09-27)
# ============================================================
# 目的: 新規記事生成ではなく、既存user_test公開ページ
# (user_test/articles_2026_0918.html)に掲載中の3記事×A2/B1=6本文へ、
# er028の確定版Trial-03方式(Stage1 screening+compact shortlist
# +Topic見出し再利用->Strategy L 1回)を適用する。
#
# er028_key_phrase_db_hybrid_trial_03_run.py / _stage1.py は
# **無変更のままimportし再利用する**(確定版ルールそのものは一切
# 変更しない、というユーザー指示)。本ファイルは新規orchestration
# (対象記事リストの差し替えと出力先の変更)のみを追加する。
#
# 記事側artifact(article.md/article_normalized.txt等)は一切書き
# 換えない(read-onlyで読むだけ)。共有ストア(pronunciation ledger/
# master audio store/human_review_queue/telemetry)へは書き込まない
# (run_stage1_and_shortlist_v3・run_selector_once はいずれもTrial-02/03
# 由来のin-memory処理のみで、これらの共有ストアへの書き込みコードパスを
# 含まない。Production module[er003_key_words_production.
# run_production_selection_gate]はvalidatorとしてのみ呼ばれ、
# 呼び出しはTrial側のarticle_id[HYBRID3_USERTEST0918_*]をkeyとした
# in-memory結果のみを返す。ledger等への書き込みAPIは別途呼び出して
# いないため、共有ストアへの書き込みは発生しない)。
# ============================================================

from __future__ import annotations

import json
import os

import er028_key_phrase_db_hybrid_trial_03_run as base
import er023_key_phrase_db_ingest as ing
import er006_model_routing_contract_01 as routing

OUTPUT_ROOT = os.path.join("er028_output", "key_phrase_db_hybrid_trial_03", "run_02_user_test_0918")

# パス特定根拠: user_test/articles_2026_0918.html内のbtn-std/btn-adv
# hrefのsrcクエリパラメータ(URLデコード後)が指すディレクトリの
# article.md(Family A/B)/article_normalized.txt(Family C、H1見出し
# なし)。twins(Digital Twins)はarticle.mdが存在しないため、同じ
# user_test html自身が持つ公開英語タイトル(en=Digital+Twins、
# player.htmlのh1表記とも整合)を、新しいLLM callでの再抽出ではなく
# 既存の公開artifactとしてTopicへ再利用する(Family A/B のarticle.md
# H1見出し再利用と同じ「既存artifactの再利用」という設計方針を、
# Family CにH1が存在しないという制約下で適用したもの。詳細はREPORT
# §15に明記)。
ARTICLES = {
    "wake_a2": (
        "er011_output/discovery_generalization_wake_before_alarm_trial_12/a2/article.md",
        "A2_SUPPORT", None,
    ),
    "wake_b1b": (
        "er011_output/discovery_generalization_wake_before_alarm_trial_12/b1b/article.md",
        "B1_SUPPORT", None,
    ),
    "aihiring_a2": (
        "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md",
        "A2_SUPPORT", None,
    ),
    "aihiring_b1": (
        "er012_output/editorial_b_voices_3v_audio_trial_01/b1b/article.md",
        "B1_SUPPORT", None,
    ),
    "twins_a2": (
        "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt",
        "A2_SUPPORT", "Digital Twins",
    ),
    "twins_b1": (
        "er013_output/family_c_episode_trial_12/twins_b1/article_normalized.txt",
        "B1_SUPPORT", "Digital Twins",
    ),
}

# 既存Production公開Key Phrase(最終5件、keywords_canonicalized.jsonから
# 抽出、read-onlyで比較用に埋め込む。記事側artifactは変更していない)
EXISTING_PRODUCTION_KP = {
    "wake_a2": [
        "grogginess", "self-awakening", "count as success", "slow build-up", "inner timekeeper",
    ],
    "wake_b1b": [
        "self-awakening", "keep time", "read the clock", "body clock", "learned expectation",
    ],
    "aihiring_a2": [
        "opt-out", "screen a résumé", "be reduced to a score", "answer for", "make the final call",
    ],
    "aihiring_b1": [
        "opt-out", "screen a résumé", "be reduced to a score", "answer for", "make the final call",
    ],
    "twins_a2": [
        "take over", "digital twin", "audition", "pretend to want", "application",
    ],
    "twins_b1": [
        "digital twin", "audition", "take over", "bring out", "hold one's breath",
    ],
}

COST_STOP_THRESHOLD_JPY = 50.0  # ユーザー指示のSTOP閾値(Guardrail合計目安¥60)


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = base._RunningCost(COST_STOP_THRESHOLD_JPY)

    all_results = {}
    stop_conditions_all = {}
    static_instructions = base.extract_static_instructions(base.bk.load_prompt_template())

    try:
        for article_key, (article_path, process, title_override) in ARTICLES.items():
            print(f"=== {article_key} ===")
            article_text = open(article_path, encoding="utf-8").read()
            out_dir = os.path.join(OUTPUT_ROOT, article_key)
            os.makedirs(out_dir, exist_ok=True)

            s1r = base.run_stage1_and_shortlist_v3(article_text, dbs)
            stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
            stops = base.check_stop_conditions(article_key, stage1, shortlist_info)
            stop_conditions_all[article_key] = stops

            model = routing.require_model(process, routing.SUPPORT_MODEL)
            title = title_override or base.extract_article_title(article_text)
            lightweight_message = base.build_lightweight_user_message(
                title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
            base.assert_no_full_article_body(lightweight_message, article_text)
            with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
                f.write(lightweight_message)

            hybrid_result = base.run_selector_once(
                "HYBRID3_USERTEST0918_" + article_key.upper(), article_text, lightweight_message, model,
                cost_tracker, label=f"{article_key}_hybrid3")

            def _serializable_stage1(st):
                keys_to_drop = {"sentence_units"}
                return {k: v for k, v in st.items() if k not in keys_to_drop}

            final_selected = []
            if hybrid_result["parsed"]:
                final_selected = [it.get("display_phrase") for it in hybrid_result["parsed"].get("items", [])]
            existing_kp = EXISTING_PRODUCTION_KP.get(article_key, [])
            overlap = sorted(set(x.lower() for x in final_selected) & set(x.lower() for x in existing_kp))

            article_result = {
                "article_key": article_key,
                "article_path": article_path,
                "article_title": title,
                "article_word_count_approx": len(article_text.split()),
                "stage1_step_reduction": {
                    "raw_ngrams_before_dedup": stage1["before_dedup_count"],
                    "after_dedup": stage1["after_dedup_count"],
                    "after_existing_gate": stage1["stage_a_survivors_count"],
                    "irregular_verb_rescued_count": stage1["irregular_verb_rescued_count"],
                    "context_mismatch_excluded_count": stage1["context_mismatch_excluded_count"],
                    "after_context_mismatch_gate": stage1["stage_b_survivors_count"],
                    "phrase_survivors_count": len(stage1["phrase_survivors"]),
                    "important_noun_candidates_count": len(stage1["important_noun_candidates"]),
                    "word_survivors_count": len(stage1["word_survivors"]),
                    "wiktionary_multiword_lookup": stage1["wiktionary_multiword_lookup"],
                },
                "shortlist_info": {
                    "phrase_included_count": shortlist_info["phrase_included_count"],
                    "important_noun_included_count": shortlist_info["important_noun_included_count"],
                    "word_included_count": shortlist_info["word_included_count"],
                    "shortlist_total_count": shortlist_info["shortlist_total_count"],
                    "shortlist": shortlist_info["shortlist"],
                    "sentence_reference_count": len(shortlist_info["sentence_reference"]),
                },
                "hybrid3_selector_result": hybrid_result,
                "existing_production_kp": existing_kp,
                "trial03_final_selected_display_phrases": final_selected,
                "overlap_with_existing_production_kp": overlap,
                "overlap_count": len(overlap),
                "stop_conditions_triggered": stops,
                "prompt_char_len": len(lightweight_message),
                "article_char_len": len(article_text),
            }
            with open(os.path.join(out_dir, "hybrid3_trial_result.json"), "w", encoding="utf-8") as f:
                json.dump(article_result, f, ensure_ascii=False, indent=2)
            with open(os.path.join(out_dir, "stage1_debug.json"), "w", encoding="utf-8") as f:
                json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

            all_results[article_key] = article_result
            print(f"  stage1: {stage1['before_dedup_count']}->{stage1['stage_a_survivors_count']}"
                  f"->{stage1['stage_b_survivors_count']}, shortlist={shortlist_info['shortlist_total_count']}, "
                  f"hybrid3_status={hybrid_result['status']}, stops={stops}, "
                  f"overlap={len(overlap)}/5, "
                  f"prompt_chars={len(lightweight_message)} (article_chars={len(article_text)})")

    except base.CostGuardrailStop as e:
        print(f"STOP: {e}")
        with open(os.path.join(OUTPUT_ROOT, "cost_guardrail_stop.json"), "w", encoding="utf-8") as f:
            json.dump({"reason": str(e), "completed_articles": list(all_results.keys()),
                       "cost_so_far_jpy": cost_tracker.total_jpy}, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUTPUT_ROOT, "raw_usage_log.jsonl"), "w", encoding="utf-8") as f:
        for call in cost_tracker.calls:
            f.write(json.dumps(call, ensure_ascii=False) + "\n")
    with open(os.path.join(OUTPUT_ROOT, "cost.json"), "w", encoding="utf-8") as f:
        json.dump({"total_jpy": round(cost_tracker.total_jpy, 4), "calls": cost_tracker.calls},
                   f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_ROOT, "all_articles_stop_conditions.json"), "w", encoding="utf-8") as f:
        json.dump(stop_conditions_all, f, ensure_ascii=False, indent=2)

    print("Done. Total cost JPY:", round(cost_tracker.total_jpy, 4))
    return all_results


if __name__ == "__main__":
    main()
