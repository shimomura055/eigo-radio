# ============================================================
# er029_key_phrase_db_hybrid_trial_04_run.py
# KEY-PHRASE-DB-HYBRID-TRIAL-04
# ============================================================
# KEY-PHRASE-DB-HYBRID-TRIAL-03の確定版(er028_key_phrase_db_hybrid_
# trial_03_run.py)を無変更のままimportし、以下だけを新規に追加する。
#   - Stage 1をer029_stage1のv4(Fix A: sentence segmentation、
#     Fix B: rare single word候補)へ差し替えたorchestration
#     (run_stage1_and_shortlist_v4)。
#   - 12本文(Trial-03既存6本文+user_test追加6本文)を同一条件
#     (1本文1 call、article全文非送信assertion、共有ストア非書込み)で
#     まとめて実行する単一エントリポイント。
#
# er027/er028/er023(Trial-01〜03資産)は一切変更しない。Production
# module(er003_key_words_*等)もimport/読み取りのみ。
# ============================================================

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er006_model_routing_contract_01 as routing
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_run as base
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er029_key_phrase_db_hybrid_trial_04_stage1 as s1v4

OUTPUT_ROOT = os.path.join("er029_output", "key_phrase_db_hybrid_trial_04")

# Trial-03既存6本文(er028_key_phrase_db_hybrid_trial_03_run.ARTICLESと
# 同一パス、本文再生成なしの回帰比較用)。
EXISTING_6_ARTICLES = dict(base.ARTICLES)

# user_test追加6本文(er028_key_phrase_db_hybrid_trial_03_run_02_user_
# test_0918.ARTICLESと同一パス。Family C[twins]はarticle.mdが無いため
# title_overrideを使う)。
_ADDITIONAL_6_RAW = {
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

EXISTING_PRODUCTION_KP = {
    "wake_a2": ["grogginess", "self-awakening", "count as success", "slow build-up", "inner timekeeper"],
    "wake_b1b": ["self-awakening", "keep time", "read the clock", "body clock", "learned expectation"],
    "aihiring_a2": ["opt-out", "screen a résumé", "be reduced to a score", "answer for", "make the final call"],
    "aihiring_b1": ["opt-out", "screen a résumé", "be reduced to a score", "answer for", "make the final call"],
    "twins_a2": ["take over", "digital twin", "audition", "pretend to want", "application"],
    "twins_b1": ["digital twin", "audition", "take over", "bring out", "hold one's breath"],
}

RARE_WORD_LOOKUP_BUDGET = 15
COST_STOP_THRESHOLD_JPY = 50.0  # ユーザー指示のGuardrail(合計目安¥60、¥50到達で中止)


def _display_type_v4(c: dict) -> str:
    """er028_run._display_typeと同じ役割だが、fix Bの1-token重要候補を
    "noun_phrase"ではなく"important_word"として区別表示する(表示の
    正確性のみの改善、選定ロジック・bucket分けは無変更)。"""
    if c.get("important_noun_phrase_candidate"):
        if c.get("unit_type") == "word":
            return "important_word"
        return "noun_phrase"
    return c["unit_type"]


def format_candidate_line_v4(c: dict) -> str:
    sid = c.get("context_sentence_id") or "?"
    return (f"- candidate: \"{c['surface_form']}\" | type: {_display_type_v4(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {base._compact_evidence_string(c)} | sentence: {sid}")


def build_lightweight_user_message_v4(article_title: str, shortlist_info: dict,
                                       sentence_reference: dict, static_instructions: str) -> str:
    important = [c for c in shortlist_info["shortlist"] if c.get("important_noun_phrase_candidate")]
    phrase = [c for c in shortlist_info["shortlist"]
              if not c.get("important_noun_phrase_candidate") and c["unit_type"] != "word"]
    word = [c for c in shortlist_info["shortlist"]
            if not c.get("important_noun_phrase_candidate") and c["unit_type"] == "word"]

    lines = [static_instructions.rstrip(), ""]
    lines.append(f"【Topic】title: {article_title}")
    lines.append("")
    lines.append("【重要な単語・単語群候補】")
    if important:
        lines.extend(format_candidate_line_v4(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line_v4(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line_v4(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(base.SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


def run_stage1_and_shortlist_v4(article_text: str, dbs: dict, article_title: str) -> dict:
    """er028.run_stage1_and_shortlist_v3と同じ手順(Stage1->Wiktionary
    multiword lookup[bug A/B/C適用]->shortlist->compact context)に、
    Fix A(sentence segmentation v4)とFix B(rare single word候補)を
    追加する。"""
    stage1 = s1v4.run_stage1_for_article_v4(article_text, dbs)
    existing_canonicals = ({c["canonical_form"] for c in stage1["phrase_survivors"]} |
                            {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
                            {c["canonical_form"] for c in stage1["word_survivors"]})
    sentences_tokens = [u["tokens"] for u in stage1["sentence_units"]]

    # --- 既存Wiktionary multiword lookup(2〜3-gram、bug A/B/C適用済み、無変更) ---
    lookup_candidates = s1v2.select_unmatched_ngram_candidates_for_lookup(
        sentences_tokens, existing_canonicals, budget=base.WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
    mw_result = ing.wiktionary_multiword_targeted_lookup(lookup_candidates)
    hits = s1v2.build_multiword_hit_evidences(mw_result["results"])
    hits_survivors = s1v2.gate_and_merge_multiword_hits(hits)
    hits_survivors = [h for h in hits_survivors if h["canonical_form"] not in existing_canonicals]
    hits_survivors = s1v3.refine_multiword_hits_noun_phrase_flag(hits_survivors, dbs["cefr_j"])

    important_hits = [h for h in hits_survivors if h["important_noun_phrase_candidate"]]
    demoted_to_phrase = [h for h in hits_survivors if not h["important_noun_phrase_candidate"]]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + important_hits
    if demoted_to_phrase:
        stage1["phrase_survivors"] = stage1["phrase_survivors"] + demoted_to_phrase

    existing_canonicals = existing_canonicals | {h["canonical_form"] for h in important_hits} | \
        {h["canonical_form"] for h in demoted_to_phrase}

    # --- Fix B: rare single word候補(1-gram、新規) ---
    rare_selected = s1v4.select_rare_single_word_candidates(
        stage1["sentence_units"], dbs, article_title, budget=RARE_WORD_LOOKUP_BUDGET)
    rare_selected = [(k, e, r) for k, e, r in rare_selected if k not in existing_canonicals]
    rare_lookup_candidates = [k for k, e, r in rare_selected]
    if rare_lookup_candidates:
        rare_mw_result = s1v4.wiktionary_unigram_lemma_lookup(rare_lookup_candidates)
    else:
        rare_mw_result = {"results": {}, "api_calls": 0, "elapsed_sec": 0.0, "candidate_count": 0}
    rare_built = s1v4.build_rare_single_word_evidences(rare_selected, rare_mw_result["results"])
    rare_evidences = rare_built["evidences"]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + rare_evidences

    stage1["wiktionary_multiword_lookup"] = {
        "candidates_checked": mw_result["candidate_count"],
        "api_calls": mw_result["api_calls"], "elapsed_sec": mw_result["elapsed_sec"],
        "hits": len(hits), "hits_surviving_gate_and_dedup": len(hits_survivors),
        "hits_important_after_pos_refine": len(important_hits),
        "hits_demoted_to_phrase_after_pos_refine": [h["canonical_form"] for h in demoted_to_phrase],
    }
    stage1["rare_single_word_lookup"] = {
        "candidates_checked": rare_mw_result["candidate_count"],
        "api_calls": rare_mw_result["api_calls"], "elapsed_sec": rare_mw_result["elapsed_sec"],
        "selected_with_reason": [(k, r) for k, e, r in rare_selected],
        "wiktionary_lemma_confirmed": rare_mw_result["results"],
        "final_included": [ev["canonical_form"] for ev in rare_evidences],
        "dropped_unconfirmed_frequency_unknown": rare_built["dropped_unconfirmed_frequency_unknown"],
    }

    shortlist_info = s1v2.build_shortlist(stage1)
    context_result = s1v4.attach_compact_context(shortlist_info["shortlist"], stage1["sentence_units"])
    shortlist_info["shortlist"] = context_result["shortlist"]
    shortlist_info["sentence_reference"] = context_result["sentence_reference"]
    return {"stage1": stage1, "shortlist_info": shortlist_info}


def _serializable_stage1(st: dict) -> dict:
    keys_to_drop = {"sentence_units"}
    return {k: v for k, v in st.items() if k not in keys_to_drop}


def run_one_article(article_key: str, article_path: str, process: str, title_override,
                     dbs: dict, cost_tracker: "base._RunningCost", static_instructions: str,
                     article_id_prefix: str, out_dir: str, existing_production_kp=None) -> dict:
    print(f"=== {article_key} ===")
    article_text = open(article_path, encoding="utf-8").read()
    os.makedirs(out_dir, exist_ok=True)

    title = title_override or base.extract_article_title(article_text)
    s1r = run_stage1_and_shortlist_v4(article_text, dbs, title)
    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    stops = base.check_stop_conditions(article_key, stage1, shortlist_info)

    model = routing.require_model(process, routing.SUPPORT_MODEL)
    lightweight_message = build_lightweight_user_message_v4(
        title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
    base.assert_no_full_article_body(lightweight_message, article_text)
    with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(lightweight_message)

    hybrid_result = base.run_selector_once(
        f"{article_id_prefix}_{article_key.upper()}", article_text, lightweight_message, model,
        cost_tracker, label=f"{article_key}_hybrid4")

    final_selected = []
    if hybrid_result["parsed"]:
        final_selected = [it.get("display_phrase") for it in hybrid_result["parsed"].get("items", [])]
    existing_kp = existing_production_kp or []
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
            "rare_single_word_lookup": stage1["rare_single_word_lookup"],
        },
        "shortlist_info": {
            "phrase_included_count": shortlist_info["phrase_included_count"],
            "important_noun_included_count": shortlist_info["important_noun_included_count"],
            "word_included_count": shortlist_info["word_included_count"],
            "shortlist_total_count": shortlist_info["shortlist_total_count"],
            "shortlist": shortlist_info["shortlist"],
            "sentence_reference_count": len(shortlist_info["sentence_reference"]),
        },
        "hybrid4_selector_result": hybrid_result,
        "existing_production_kp": existing_kp,
        "trial04_final_selected_display_phrases": final_selected,
        "overlap_with_existing_production_kp": overlap,
        "overlap_count": len(overlap) if existing_production_kp else None,
        "stop_conditions_triggered": stops,
        "prompt_char_len": len(lightweight_message),
        "article_char_len": len(article_text),
    }
    with open(os.path.join(out_dir, "hybrid4_trial_result.json"), "w", encoding="utf-8") as f:
        json.dump(article_result, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "stage1_debug.json"), "w", encoding="utf-8") as f:
        json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

    print(f"  stage1: {stage1['before_dedup_count']}->{stage1['stage_a_survivors_count']}"
          f"->{stage1['stage_b_survivors_count']}, shortlist={shortlist_info['shortlist_total_count']}, "
          f"hybrid4_status={hybrid_result['status']}, stops={stops}, "
          f"rare_word_final={stage1['rare_single_word_lookup']['final_included']}, "
          f"prompt_chars={len(lightweight_message)} (article_chars={len(article_text)})")
    return article_result


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = base._RunningCost(COST_STOP_THRESHOLD_JPY)
    static_instructions = base.extract_static_instructions(bk.load_prompt_template())

    all_results = {}
    stop_conditions_all = {}

    try:
        for article_key, (article_path, process) in EXISTING_6_ARTICLES.items():
            out_dir = os.path.join(OUTPUT_ROOT, article_key)
            result = run_one_article(
                article_key, article_path, process, None, dbs, cost_tracker, static_instructions,
                "HYBRID4", out_dir, existing_production_kp=None)
            all_results[article_key] = result
            stop_conditions_all[article_key] = result["stop_conditions_triggered"]

        for article_key, (article_path, process, title_override) in _ADDITIONAL_6_RAW.items():
            out_dir = os.path.join(OUTPUT_ROOT, article_key)
            result = run_one_article(
                article_key, article_path, process, title_override, dbs, cost_tracker, static_instructions,
                "HYBRID4_USERTEST0918", out_dir,
                existing_production_kp=EXISTING_PRODUCTION_KP.get(article_key))
            all_results[article_key] = result
            stop_conditions_all[article_key] = result["stop_conditions_triggered"]

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
