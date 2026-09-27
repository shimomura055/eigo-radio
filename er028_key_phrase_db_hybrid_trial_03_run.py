# ============================================================
# er028_key_phrase_db_hybrid_trial_03_run.py
# KEY-PHRASE-DB-HYBRID-TRIAL-03
# ============================================================
# KEY-PHRASE-DB-HYBRID-TRIAL-02(er027_*)のHybrid設計(DB+機械screening
# ->Strategy L 1回)を踏襲しつつ、ユーザー指示のLLM input軽量化(article
# 全文を再送しない)を実装する。Production module
# (er003_key_words_production.py/er003_b1_p2_keywords.py)は無変更、
# 読み取り・定数再利用のみ(usage計測のためのAPI呼び出しラッパーは
# er027と同様にTrial側で独立実装する)。
#
# 送信するprompt = 静的instructions(既存production template由来、
# article placeholderを除いた部分、無変更)+ Topic(記事タイトルのみ、
# 既存artifact[article.mdのH1見出し]を再利用、新しいLLM callでの
# Topic抽出は行わない)+ compact shortlist(候補・種別・記事内出現回数・
# 参照sentence ID)+ sentence reference table(候補が参照する文のみ、
# 重複なし)+ 選定方針。article全文は一切含まない。
# ============================================================

from __future__ import annotations

import json
import os
import re
import time

import er003_b1_p2_keywords as bk
import er003_key_words_production as prod
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2

OUTPUT_ROOT = os.path.join("er028_output", "key_phrase_db_hybrid_trial_03")

ARTICLES = {
    "meta_a2": ("er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md", "A2_SUPPORT"),
    "meta_b1b": ("er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md", "B1_SUPPORT"),
    "hormuz_a2": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md", "A2_SUPPORT"),
    "hormuz_b1b": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md", "B1_SUPPORT"),
    "small_bag_a2": ("er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md", "A2_SUPPORT"),
    "small_bag_b1b": ("er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md", "B1_SUPPORT"),
}

WIKTIONARY_MULTIWORD_LOOKUP_BUDGET = 60
COST_STOP_THRESHOLD_JPY = 50.0  # 本Trialのユーザー指示のGuardrail(合計目安¥60、¥50到達で中止)

USER_EXAMPLE_TERMS = {
    "meta_a2": ["contract worker"], "meta_b1b": ["contract worker"],
    "hormuz_a2": ["brent crude", "sea blockade"], "hormuz_b1b": ["brent crude", "sea blockade"],
    "small_bag_a2": [], "small_bag_b1b": [],
}

_ARTICLE_PLACEHOLDER_MARKERS = ("{approved_b1_article}", "{approved_b2_article}")


def extract_static_instructions(template: str) -> str:
    """production prompt templateから、article本文placeholder以降(本文
    ラベル行含む)を取り除いた静的instructions部分だけを返す(instructions
    自体の文言は一切変更しない、article差し込み部分だけを取り除く)。"""
    text = template
    for marker in _ARTICLE_PLACEHOLDER_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    # placeholder直前のラベル行(例:【B1 Article】)を取り除く
    lines = text.rstrip().splitlines()
    while lines and (lines[-1].strip().startswith("【") or not lines[-1].strip()):
        lines.pop()
    return "\n".join(lines).rstrip() + "\n"


def extract_article_title(article_text: str) -> str:
    """article.mdの最初のH1見出し行のみを再利用する(新しいLLM callでの
    Topic抽出は行わない、既存Writer成果物の一部を読み取るだけ)。"""
    for line in article_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return ""


def _compact_evidence_string(c: dict) -> str:
    if c.get("important_noun_phrase_candidate") and "repeated_compound_noun_heuristic" in (c.get("matched_dbs") or []):
        return "repeated_compound_noun"
    if c.get("important_noun_phrase_candidate") and c.get("matched_dbs") == ["wiktionary"] and \
            c.get("db_categories") == ["multiword_term"]:
        return "wiktionary_multiword"
    parts = list(c.get("matched_dbs") or [])
    cats = list(c.get("db_categories") or [])
    s = "+".join(parts) if parts else "heuristic"
    if cats:
        s += f"[{','.join(cats)}]"
    if c.get("irregular_verb_rescue"):
        s += "+irregular_rescue"
    if c.get("possessive_noise_stripped"):
        s += "+possessive_stripped"
    return s


def _display_type(c: dict) -> str:
    if c.get("important_noun_phrase_candidate"):
        return "noun_phrase"
    return c["unit_type"]


def format_candidate_line(c: dict) -> str:
    sid = c.get("context_sentence_id") or "?"
    return (f"- candidate: \"{c['surface_form']}\" | type: {_display_type(c)} | "
            f"occ: {c.get('occurrence_count_in_article', '?')} | "
            f"evidence: {_compact_evidence_string(c)} | sentence: {sid}")


SELECTION_GUIDANCE = """
【選定方針】
- 最終的に選ぶ5件は、必ず下記の候補一覧の中から選んでください。候補に
  無い新しい表現を作らないでください。
- 5個のうち少なくとも1個は、[重要な単語・単語群候補]区分から選んで
  ください(記事理解・再利用価値の高い重要な名詞・専門用語・複合語)。
- 残りは、[phrase / idiom / phrasal verb候補]区分を優先してください。
  良い候補が不足する場合のみ[word候補]区分で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください。
- 各itemのsource_sentenceは、必ず【SENTENCE REFERENCE】に列挙されている
  文をそのまま(一字一句、改変せず)使用してください。新しい文を作らない
  でください。source_spanは、そのsource_sentence内に実際に現れる形
  (元の活用形・大文字小文字を含む)の一部分にしてください。
"""


def build_lightweight_user_message(article_title: str, shortlist_info: dict,
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
        lines.extend(format_candidate_line(c) for c in important)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【phrase / idiom / phrasal verb候補】")
    if phrase:
        lines.extend(format_candidate_line(c) for c in phrase)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【word候補】")
    if word:
        lines.extend(format_candidate_line(c) for c in word)
    else:
        lines.append("(なし)")
    lines.append("")
    lines.append("【SENTENCE REFERENCE】")
    for sid in sorted(sentence_reference, key=lambda s: int(s[1:])):
        lines.append(f'{sid}: "{sentence_reference[sid]}"')
    lines.append(SELECTION_GUIDANCE.rstrip())
    return "\n".join(lines) + "\n"


def assert_no_full_article_body(user_message: str, article_text: str) -> None:
    """article全文がLLM inputへ混入していないことの構造的チェック(連続
    100語一致が無いこと)。regressionテストでも同内容を検証する。"""
    article_words = re.findall(r"[A-Za-z']+", article_text)
    if len(article_words) < 100:
        return
    for i in range(0, len(article_words) - 100, 20):
        window = " ".join(article_words[i:i + 100]).lower()
        if window in re.sub(r"\s+", " ", user_message.lower()):
            raise AssertionError("article全文相当の連続100語がuser_messageに含まれています")


class CostGuardrailStop(Exception):
    pass


class _RunningCost:
    def __init__(self, threshold: float):
        self.total_jpy = 0.0
        self.threshold = threshold
        self.calls = []

    def add(self, label, model, usage):
        cost = pricing.cost_jpy_for_call(
            "openai", model,
            usage.get("input_tokens"), usage.get("cached_input_tokens"), usage.get("output_tokens"))
        self.total_jpy += cost
        self.calls.append({"label": label, "model": model, "usage": usage, "cost_jpy": cost})
        if self.total_jpy >= self.threshold:
            raise CostGuardrailStop(
                f"累計費用が¥{self.threshold}に到達しました(¥{self.total_jpy:.4f})。"
                "STOP条件(実装上の指示)に従い残りの呼び出しを中止します。")


def _usage_dict(usage) -> dict:
    if usage is None:
        return {}
    d = {"input_tokens": getattr(usage, "input_tokens", None),
         "output_tokens": getattr(usage, "output_tokens", None),
         "total_tokens": getattr(usage, "total_tokens", None)}
    in_details = getattr(usage, "input_tokens_details", None)
    if in_details is not None:
        d["cached_input_tokens"] = getattr(in_details, "cached_tokens", None)
    out_details = getattr(usage, "output_tokens_details", None)
    if out_details is not None:
        d["reasoning_tokens"] = getattr(out_details, "reasoning_tokens", None)
    return d


def make_instrumented_selector_factory(user_message: str, model: str, usage_sink: list, client=None):
    def factory():
        nonlocal client
        if client is None:
            from dotenv import load_dotenv
            load_dotenv()
            from openai import OpenAI
            client = OpenAI()

        def fn():
            t0 = time.time()
            response = client.responses.create(
                model=model,
                reasoning={"effort": prod.SELECTOR_REASONING_EFFORT},
                text={"format": {"type": "json_schema", **prod.SELECTOR_JSON_SCHEMA}},
                input=[
                    {"role": "developer", "content": prod.SELECTOR_DEVELOPER_MESSAGE},
                    {"role": "user", "content": user_message},
                ],
            )
            elapsed = time.time() - t0
            if response.model != model:
                raise prod.SelectorModelMismatchError(
                    f"応答モデルが不一致です(期待: {model}, 実際: {response.model})")
            text = getattr(response, "output_text", None)
            usage_sink.append({
                "response_id": response.id, "model": response.model,
                "usage": _usage_dict(getattr(response, "usage", None)),
                "elapsed_sec": round(elapsed, 3),
            })
            if not text or not text.strip():
                import er003_ja_to_en_translation as er003
                raise er003.restore.GenerationEmptyOrBrokenError("selector応答が空です")
            return text, response.model, response.id

        fn.model = model
        fn.reasoning_effort = prod.SELECTOR_REASONING_EFFORT
        fn.uses_web_search_tool = False
        fn.uses_structured_output = True
        return fn

    return factory


def run_stage1_and_shortlist_v3(article_text: str, dbs: dict) -> dict:
    stage1 = s1v3.run_stage1_for_article_v3(article_text, dbs)
    existing_canonicals = ({c["canonical_form"] for c in stage1["phrase_survivors"]} |
                            {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
                            {c["canonical_form"] for c in stage1["word_survivors"]})
    sentences_tokens = [u["tokens"] for u in stage1["sentence_units"]]
    lookup_candidates = s1v2.select_unmatched_ngram_candidates_for_lookup(
        sentences_tokens, existing_canonicals, budget=WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
    mw_result = ing.wiktionary_multiword_targeted_lookup(lookup_candidates)
    hits = s1v2.build_multiword_hit_evidences(mw_result["results"])
    hits_survivors = s1v2.gate_and_merge_multiword_hits(hits)
    hits_survivors = [h for h in hits_survivors if h["canonical_form"] not in existing_canonicals]
    # bug B修正: important_noun_phrase_candidateを品詞妥当性で再判定する
    hits_survivors = s1v3.refine_multiword_hits_noun_phrase_flag(hits_survivors, dbs["cefr_j"])

    important_hits = [h for h in hits_survivors if h["important_noun_phrase_candidate"]]
    demoted_to_phrase = [h for h in hits_survivors if not h["important_noun_phrase_candidate"]]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + important_hits
    # important判定から外れたWiktionary multiword hitは、一般phraseとして
    # phrase_survivorsへ合流させる(捨てない、ユーザー指示どおり)。
    if demoted_to_phrase:
        stage1["phrase_survivors"] = stage1["phrase_survivors"] + demoted_to_phrase

    stage1["wiktionary_multiword_lookup"] = {
        "candidates_checked": mw_result["candidate_count"],
        "api_calls": mw_result["api_calls"], "elapsed_sec": mw_result["elapsed_sec"],
        "hits": len(hits), "hits_surviving_gate_and_dedup": len(hits_survivors),
        "hits_important_after_pos_refine": len(important_hits),
        "hits_demoted_to_phrase_after_pos_refine": [h["canonical_form"] for h in demoted_to_phrase],
    }

    shortlist_info = s1v2.build_shortlist(stage1)
    context_result = s1v3.attach_compact_context(shortlist_info["shortlist"], stage1["sentence_units"])
    shortlist_info["shortlist"] = context_result["shortlist"]
    shortlist_info["sentence_reference"] = context_result["sentence_reference"]
    return {"stage1": stage1, "shortlist_info": shortlist_info}


def run_selector_once(article_id: str, article_text: str, user_message: str, model: str,
                       cost_tracker: _RunningCost, label: str):
    usage_sink = []
    factory = make_instrumented_selector_factory(user_message, model, usage_sink)
    parsed, status, attempts, model_id, response_id = prod.run_production_selection_gate(
        article_id, factory, article_text, strategy_id=prod.STANDARD_STRATEGY_ID, max_attempts=1,
    )
    usage_entry = usage_sink[0] if usage_sink else {"usage": {}}
    cost_tracker.add(label, model_id or model, usage_entry.get("usage", {}))
    return {
        "status": status, "parsed": parsed, "model_id": model_id, "response_id": response_id,
        "usage": usage_entry.get("usage", {}), "elapsed_sec": usage_entry.get("elapsed_sec"),
        "attempts_detail": [{k: v for k, v in a.items() if k != "raw_text"} for a in attempts],
    }


def check_stop_conditions(article_key: str, stage1: dict, shortlist_info: dict) -> list:
    stops = []
    survivors_canonical = {c["canonical_form"] for c in stage1["phrase_survivors"]} | \
        {c["canonical_form"] for c in stage1["important_noun_candidates"]}
    for term in USER_EXAMPLE_TERMS.get(article_key, []):
        term_key = term.lower()
        if not any(term_key in c or c in term_key for c in survivors_canonical):
            stops.append(f"ユーザー例示語'{term}'が機械スクリーニング後に残っていません")
    if shortlist_info["shortlist_total_count"] > 30:
        stops.append("shortlistが20件前後の目安を大幅に超過しました"
                      f"({shortlist_info['shortlist_total_count']}件)")
    return stops


def main():
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    print("Loading group1 DBs...")
    dbs = ing.load_all_group1_dbs()
    cost_tracker = _RunningCost(COST_STOP_THRESHOLD_JPY)

    all_results = {}
    stop_conditions_all = {}
    static_instructions = extract_static_instructions(bk.load_prompt_template())

    try:
        for article_key, (article_path, process) in ARTICLES.items():
            print(f"=== {article_key} ===")
            article_text = open(article_path, encoding="utf-8").read()
            out_dir = os.path.join(OUTPUT_ROOT, article_key)
            os.makedirs(out_dir, exist_ok=True)

            s1r = run_stage1_and_shortlist_v3(article_text, dbs)
            stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
            stops = check_stop_conditions(article_key, stage1, shortlist_info)
            stop_conditions_all[article_key] = stops

            model = routing.require_model(process, routing.SUPPORT_MODEL)
            title = extract_article_title(article_text)
            lightweight_message = build_lightweight_user_message(
                title, shortlist_info, shortlist_info["sentence_reference"], static_instructions)
            assert_no_full_article_body(lightweight_message, article_text)
            with open(os.path.join(out_dir, "lightweight_selector_prompt.txt"), "w", encoding="utf-8") as f:
                f.write(lightweight_message)

            hybrid_result = run_selector_once(
                "HYBRID3_" + article_key.upper(), article_text, lightweight_message, model,
                cost_tracker, label=f"{article_key}_hybrid3")

            def _serializable_stage1(st):
                keys_to_drop = {"sentence_units"}
                return {k: v for k, v in st.items() if k not in keys_to_drop}

            article_result = {
                "article_key": article_key,
                "article_title": title,
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
                  f"prompt_chars={len(lightweight_message)} (article_chars={len(article_text)})")

    except CostGuardrailStop as e:
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
