# ============================================================
# er032_key_phrase_db_hybrid_core_v2_trial_05_run.py
# KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05
# ============================================================
# Core v2(er032_stage1)を使い、Family Xの既存12本文
# (er029_key_phrase_db_hybrid_trial_04_run.EXISTING_6_ARTICLES/
# _ADDITIONAL_6_RAW、記事パスはer029と完全同一)+Family Z Melos
# (er031_key_phrase_db_hybrid_family_z_trial_01_run、記事パスは
# er031と完全同一)を同一条件(1本文1 call、article全文非送信
# assertion、共有ストア非書込み)で実行する。v1側は既存artifact
# (er029_output/.../hybrid4_trial_result.json、
# er031_output/.../z0_melos/hybrid4_trial_result.json)を読み取り専用で
# 再利用し、再実行しない(ユーザー指示どおりcall数節約)。
#
# er023/er027/er028/er029/er030(v1 baseline)・er003_key_words_*は
# 一切変更しない(read-only import)。
# ============================================================

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er006_model_routing_contract_01 as routing
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er032_key_phrase_db_hybrid_core_v2_trial_05_stage1 as s2

OUTPUT_ROOT = os.path.join("er032_output", "key_phrase_db_hybrid_core_v2_trial_05")

# X 12本文(記事パス・process・title_overrideはer029_runと完全同一、
# v1側artifact再利用のためのキーも同一にする)。
X_EXISTING_6_ARTICLES = dict(run4.EXISTING_6_ARTICLES)
X_ADDITIONAL_6_RAW = dict(run4._ADDITIONAL_6_RAW)
X_EXISTING_PRODUCTION_KP = dict(run4.EXISTING_PRODUCTION_KP)

MELOS_ARTICLE_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"
MELOS_PROCESS = "A2_SUPPORT"
MELOS_TITLE_OVERRIDE = "The Three-Day Promise"
EXISTING_PRODUCTION_KP_MELOS = [
    "in someone's place", "execution", "give one's word", "fair trial", "loyalty",
]

RARE_WORD_LOOKUP_BUDGET = 15
WIKTIONARY_MULTIWORD_LOOKUP_BUDGET = 60
COST_STOP_THRESHOLD_JPY = 60.0  # ユーザー指示Guardrail¥70のSTOP閾値相当(事前見積>¥60でSTOP)


def _display_type_v2(c: dict) -> str:
    if c.get("important_noun_phrase_candidate"):
        if c.get("unit_type") == "word":
            return "important_word"
        return "noun_phrase"
    return c["unit_type"]


def _compact_evidence_string_v2(c: dict) -> str:
    if c.get("pronoun_placeholder_rescue"):
        return base._compact_evidence_string(c) + "+pronoun_placeholder_rescue"
    return base._compact_evidence_string(c)


def format_candidate_line_v2(c: dict) -> str:
    sid = c.get("context_sentence_id") or "?"
    return (f"- candidate: \"{c['surface_form']}\" | type: {_display_type_v2(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {_compact_evidence_string_v2(c)} | sentence: {sid}")


def build_lightweight_user_message_v2(article_title: str, shortlist_info: dict,
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
        lines.extend(format_candidate_line_v2(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line_v2(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line_v2(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(base.SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


def run_stage1_and_shortlist_core_v2(article_text: str, dbs: dict, article_title: str) -> dict:
    """Core v2版のStage1(V2-1/V2-2/V2-3適用)+ Wiktionary multiword
    lookup(V2-2: 優先順位付け改善版)+ Fix B rare single word(V2-3:
    proper noun gate維持)+ shortlist構築(既存er027.build_shortlist、
    無変更)。"""
    stage1 = s2.run_stage1_for_article_core_v2(article_text, dbs)
    signals = s2.compute_proper_noun_signals(stage1["sentence_units"])
    existing_canonicals = ({c["canonical_form"] for c in stage1["phrase_survivors"]} |
                            {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
                            {c["canonical_form"] for c in stage1["word_survivors"]})
    sentences_tokens = [u["tokens"] for u in stage1["sentence_units"]]

    # --- V2-2: Wiktionary multiword lookup(優先順位付け改善版) ---
    lookup_candidates = s2.select_unmatched_ngram_candidates_for_lookup_v2(
        sentences_tokens, existing_canonicals, budget=WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
    mw_result = ing.wiktionary_multiword_targeted_lookup(lookup_candidates)
    hits = s2.s1v2.build_multiword_hit_evidences(mw_result["results"])
    hits_survivors = s2.s1v2.gate_and_merge_multiword_hits(hits)
    hits_survivors = [h for h in hits_survivors if h["canonical_form"] not in existing_canonicals]
    hits_survivors = s2.s1v3.refine_multiword_hits_noun_phrase_flag(hits_survivors, dbs["cefr_j"])

    important_hits = [h for h in hits_survivors if h["important_noun_phrase_candidate"]]
    demoted_to_phrase = [h for h in hits_survivors if not h["important_noun_phrase_candidate"]]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + important_hits
    if demoted_to_phrase:
        stage1["phrase_survivors"] = stage1["phrase_survivors"] + demoted_to_phrase

    existing_canonicals = existing_canonicals | {h["canonical_form"] for h in important_hits} | \
        {h["canonical_form"] for h in demoted_to_phrase}

    # --- V2-3: Fix B rare single word(proper noun gate維持、V2版関数) ---
    rare_selected = s2.select_rare_single_word_candidates_v2(
        stage1["sentence_units"], dbs, signals, article_title, budget=RARE_WORD_LOOKUP_BUDGET)
    rare_selected = [(k, e, r) for k, e, r in rare_selected if k not in existing_canonicals]
    rare_lookup_candidates = [k for k, e, r in rare_selected]
    if rare_lookup_candidates:
        rare_mw_result = s2.wiktionary_unigram_lemma_lookup(rare_lookup_candidates)
    else:
        rare_mw_result = {"results": {}, "api_calls": 0, "elapsed_sec": 0.0, "candidate_count": 0}
    rare_built = s2.build_rare_single_word_evidences(rare_selected, rare_mw_result["results"])
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

    # V2-1補足: lemma正規化により屈折形の見かけ上の低頻度バイアスは解消
    # したが、記事によっては(実データ確認: Melos)デバイアス後も「genuine
    # に稀な内容語」がちょうど5個存在し、moderately-rareだが重要な語
    # (loyalty、zipf 4.17)が固定5枠からわずかに漏れるケースが実データで
    # 見つかった。既存er027.build_shortlist自体は無変更のまま、
    # word_min引数(既存の公開パラメータ、新規メカニズムではない)だけを
    # Core v2側で6へ小幅に拡張し、この境界ケースを救う(shortlist総数へ
    # の影響は+1語程度、STOP閾値30件には遠く及ばない)。
    shortlist_info = s2.s1v2.build_shortlist(stage1, word_min=6)
    context_result = s2.attach_compact_context(shortlist_info["shortlist"], stage1["sentence_units"])
    shortlist_info["shortlist"] = context_result["shortlist"]
    shortlist_info["sentence_reference"] = context_result["sentence_reference"]
    return {"stage1": stage1, "shortlist_info": shortlist_info}


def _serializable_stage1(st: dict) -> dict:
    keys_to_drop = {"sentence_units"}
    return {k: v for k, v in st.items() if k not in keys_to_drop}


def run_one_article_v2(article_key: str, article_path: str, process: str, title_override,
                        dbs: dict, cost_tracker: "base._RunningCost", static_instructions: str,
                        article_id_prefix: str, out_dir: str, existing_production_kp=None) -> dict:
    print(f"=== {article_key} (core_v2) ===")
    article_text = open(article_path, encoding="utf-8").read()
    os.makedirs(out_dir, exist_ok=True)

    title = title_override or base.extract_article_title(article_text)
    s1r = run_stage1_and_shortlist_core_v2(article_text, dbs, title)
    stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
    stops = base.check_stop_conditions(article_key, stage1, shortlist_info)

    model = routing.require_model(process, routing.SUPPORT_MODEL)
    lightweight_message = build_lightweight_user_message_v2(
        title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
    base.assert_no_full_article_body(lightweight_message, article_text)
    with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(lightweight_message)

    hybrid_result = base.run_selector_once(
        f"{article_id_prefix}_{article_key.upper()}", article_text, lightweight_message, model,
        cost_tracker, label=f"{article_key}_core_v2")

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
            "pronoun_placeholder_rescued_count": stage1["pronoun_placeholder_rescued_count"],
            "context_mismatch_excluded_count": stage1["context_mismatch_excluded_count"],
            "after_context_mismatch_gate": stage1["stage_b_survivors_count"],
            "phrase_survivors_count": len(stage1["phrase_survivors"]),
            "important_noun_candidates_count": len(stage1["important_noun_candidates"]),
            "word_survivors_count": len(stage1["word_survivors"]),
            "wiktionary_multiword_lookup": stage1["wiktionary_multiword_lookup"],
            "rare_single_word_lookup": stage1["rare_single_word_lookup"],
            "proper_noun_excluded_words": stage1["proper_noun_excluded_words"],
            "proper_noun_signals_summary": stage1["proper_noun_signals_summary"],
        },
        "shortlist_info": {
            "phrase_included_count": shortlist_info["phrase_included_count"],
            "important_noun_included_count": shortlist_info["important_noun_included_count"],
            "word_included_count": shortlist_info["word_included_count"],
            "shortlist_total_count": shortlist_info["shortlist_total_count"],
            "shortlist": shortlist_info["shortlist"],
            "sentence_reference_count": len(shortlist_info["sentence_reference"]),
        },
        "core_v2_selector_result": hybrid_result,
        "existing_production_kp": existing_kp,
        "core_v2_final_selected_display_phrases": final_selected,
        "overlap_with_existing_production_kp": overlap,
        "overlap_count": len(overlap) if existing_production_kp else None,
        "stop_conditions_triggered": stops,
        "prompt_char_len": len(lightweight_message),
        "article_char_len": len(article_text),
    }
    with open(os.path.join(out_dir, "hybrid_core_v2_trial_result.json"), "w", encoding="utf-8") as f:
        json.dump(article_result, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, "stage1_debug.json"), "w", encoding="utf-8") as f:
        json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

    print(f"  stage1: {stage1['before_dedup_count']}->{stage1['stage_a_survivors_count']}"
          f"->{stage1['stage_b_survivors_count']}, shortlist={shortlist_info['shortlist_total_count']}, "
          f"core_v2_status={hybrid_result['status']}, stops={stops}, "
          f"proper_noun_excluded={stage1['proper_noun_excluded_words']}, "
          f"prompt_chars={len(lightweight_message)} (article_chars={len(article_text)})")
    return article_result


def load_v1_reference_x() -> dict:
    """X 12本文のv1側は既存artifact(Trial-04、commit 57b61273相当)を
    読み取り専用で再利用する(再実行しない)。"""
    ref = {}
    all_keys = list(X_EXISTING_6_ARTICLES.keys()) + list(X_ADDITIONAL_6_RAW.keys())
    for key in all_keys:
        result_path = os.path.join("er029_output", "key_phrase_db_hybrid_trial_04", key,
                                    "hybrid4_trial_result.json")
        debug_path = os.path.join("er029_output", "key_phrase_db_hybrid_trial_04", key,
                                   "stage1_debug.json")
        entry = {}
        if os.path.exists(result_path):
            with open(result_path, encoding="utf-8") as f:
                entry["result"] = json.load(f)
        if os.path.exists(debug_path):
            with open(debug_path, encoding="utf-8") as f:
                entry["stage1_debug"] = json.load(f)
        ref[key] = entry if entry else {"note": "v1 artifact not found (read-only reference)"}
    return ref


def load_v1_reference_melos() -> dict:
    """Melos(Z0)のv1側は既存artifact(er031 Family Z Trial)を読み取り
    専用で再利用する(再実行しない)。"""
    result_path = os.path.join("er031_output", "key_phrase_db_hybrid_family_z_trial_01",
                                "z0_melos", "hybrid4_trial_result.json")
    debug_path = os.path.join("er031_output", "key_phrase_db_hybrid_family_z_trial_01",
                               "z0_melos", "stage1_debug.json")
    entry = {}
    if os.path.exists(result_path):
        with open(result_path, encoding="utf-8") as f:
            entry["result"] = json.load(f)
    if os.path.exists(debug_path):
        with open(debug_path, encoding="utf-8") as f:
            entry["stage1_debug"] = json.load(f)
    return entry if entry else {"note": "v1 artifact not found (read-only reference)"}


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = base._RunningCost(COST_STOP_THRESHOLD_JPY)
    static_instructions = base.extract_static_instructions(bk.load_prompt_template())

    all_results = {}
    stop_conditions_all = {}

    try:
        for article_key, (article_path, process) in X_EXISTING_6_ARTICLES.items():
            out_dir = os.path.join(OUTPUT_ROOT, "x_" + article_key)
            result = run_one_article_v2(
                article_key, article_path, process, None, dbs, cost_tracker, static_instructions,
                "COREV2", out_dir, existing_production_kp=None)
            all_results["x_" + article_key] = result
            stop_conditions_all["x_" + article_key] = result["stop_conditions_triggered"]

        for article_key, (article_path, process, title_override) in X_ADDITIONAL_6_RAW.items():
            out_dir = os.path.join(OUTPUT_ROOT, "x_" + article_key)
            result = run_one_article_v2(
                article_key, article_path, process, title_override, dbs, cost_tracker, static_instructions,
                "COREV2_USERTEST0918", out_dir,
                existing_production_kp=X_EXISTING_PRODUCTION_KP.get(article_key))
            all_results["x_" + article_key] = result
            stop_conditions_all["x_" + article_key] = result["stop_conditions_triggered"]

        # --- Z: Melos(v2のみ実行、v1はer031既存artifactを再利用) ---
        melos_out_dir = os.path.join(OUTPUT_ROOT, "z_melos")
        melos_result = run_one_article_v2(
            "melos", MELOS_ARTICLE_PATH, MELOS_PROCESS, MELOS_TITLE_OVERRIDE,
            dbs, cost_tracker, static_instructions, "COREV2_Z", melos_out_dir,
            existing_production_kp=EXISTING_PRODUCTION_KP_MELOS)
        all_results["z_melos"] = melos_result
        stop_conditions_all["z_melos"] = melos_result["stop_conditions_triggered"]

    except base.CostGuardrailStop as e:
        print(f"STOP: {e}")
        with open(os.path.join(OUTPUT_ROOT, "cost_guardrail_stop.json"), "w", encoding="utf-8") as f:
            json.dump({"reason": str(e), "completed_articles": list(all_results.keys()),
                       "cost_so_far_jpy": cost_tracker.total_jpy}, f, ensure_ascii=False, indent=2)

    v1_reference_x = load_v1_reference_x()
    v1_reference_melos = load_v1_reference_melos()
    with open(os.path.join(OUTPUT_ROOT, "v1_reference_x_readonly.json"), "w", encoding="utf-8") as f:
        json.dump(v1_reference_x, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUTPUT_ROOT, "v1_reference_melos_readonly.json"), "w", encoding="utf-8") as f:
        json.dump(v1_reference_melos, f, ensure_ascii=False, indent=2)

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
