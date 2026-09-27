# ============================================================
# er027_key_phrase_db_hybrid_trial_02_run.py
# KEY-PHRASE-DB-HYBRID-TRIAL-02
# ============================================================
# Stage 1(機械screening、er027_key_phrase_db_hybrid_trial_02_stage1.py)
# の出力を使い、Stage 2として既存Production Strategy L
# (er003_key_words_production.py)を「変更せず」候補根拠つきprompt
# (in-memoryコピー)で1回だけ呼び出すオーケストレーション。
#
# Production module(er003_key_words_production.py・er003_b1_p2_keywords.py)
# は一切変更しない。Strategy L呼び出し自体は、実際に使われているモデル/
# reasoning effort/developer message/schemaをそのまま踏襲しつつ、token
# 使用量(usage)を計測するためにTrial側で独立にAPI呼び出しラッパーを
# 実装する(prod.make_production_selector_fnの内部ロジックを、usage
# 収集のためだけに複製している。Production側のファイルには一切触れない)。
#
# 比較用: small_bagはexisting keywords_canonicalized.jsonが存在しない
# ため、本Trial内で現行Production Strategy L(候補根拠なし、通常の
# production prompt template)を1回実行し、比較対象を作る(ユーザー
# 指示#8、費用計上)。
# ============================================================

from __future__ import annotations

import json
import os
import time

import er003_b1_p2_keywords as bk
import er003_key_words_production as prod
import er006_model_routing_contract_01 as routing
import er009_n1_routing_governance_10_actual_model_cost as pricing
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1

OUTPUT_ROOT = os.path.join("er027_output", "key_phrase_db_hybrid_trial_02")

ARTICLES = {
    "meta_a2": ("er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md", "A2_SUPPORT"),
    "meta_b1b": ("er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md", "B1_SUPPORT"),
    "hormuz_a2": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md", "A2_SUPPORT"),
    "hormuz_b1b": ("er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md", "B1_SUPPORT"),
    "small_bag_a2": ("er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md", "A2_SUPPORT"),
    "small_bag_b1b": ("er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md", "B1_SUPPORT"),
}

EXISTING_PRODUCTION_KEY_PHRASES = {
    "meta_a2": "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/a2/key_phrases/keywords_canonicalized.json",
    "meta_b1b": "er019_output/family_x_audio_production_wiring_01/family_x_b3_production_wiring_01__run_01/b1b/key_phrases/keywords_canonicalized.json",
    "hormuz_a2": "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/a2/key_phrases/keywords_canonicalized.json",
    "hormuz_b1b": "er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/hormuz__run_02/b1b/key_phrases/keywords_canonicalized.json",
    "small_bag_a2": None,
    "small_bag_b1b": None,
}

WIKTIONARY_MULTIWORD_LOOKUP_BUDGET = 60
COST_STOP_THRESHOLD_JPY = 80.0

USER_EXAMPLE_TERMS = {
    "meta_a2": ["contract worker"], "meta_b1b": ["contract worker"],
    "hormuz_a2": ["brent crude", "sea blockade"], "hormuz_b1b": ["brent crude", "sea blockade"],
    "small_bag_a2": [], "small_bag_b1b": [],
}


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
    """prod.make_production_selector_fnと同じAPI contract(model/reasoning_
    effort/developer_message/schema)を使うが、response.usage/latencyを
    usage_sinkへ記録する(Production module自体は変更しない、Trial側の
    独立ラッパー)。"""

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


def _format_candidate_for_prompt(c: dict) -> str:
    db_note = "/".join(c.get("matched_dbs") or []) or "repeated_compound_noun/wiktionary_multiword"
    cats = "/".join(c.get("db_categories") or [])
    rep = c.get("repetition_count_in_article")
    rep_note = f"、本文中{rep}回出現" if rep else ""
    try:
        import wordfreq
        zf = round(wordfreq.zipf_frequency(c["canonical_form"], "en"), 2)
    except Exception:
        zf = None
    important_tag = "【重要な単語・単語群候補】" if c.get("important_noun_phrase_candidate") else ""
    return (f"- {important_tag}\"{c['surface_form']}\"(種別: {c['unit_type']}、"
            f"DB根拠: {db_note}[{cats}]、頻度zipf={zf}{rep_note})")


def build_hybrid_user_message(article_text: str, shortlist: list, template: str) -> str:
    base_message = bk.build_user_message(article_text, template=template)
    candidate_lines = "\n".join(_format_candidate_for_prompt(c) for c in shortlist)
    addition = f"""

【DB照合済み候補リスト(参考情報、KEY-PHRASE-DB-HYBRID-TRIAL-02専用)】
以下は、複数の語彙・イディオムデータベース(CEFR-J、NGSL/NAWL/BSL、
Wiktionary idioms/phrasal verbs/multiword terms)と機械的な文脈チェックに
より事前スクリーニングされた候補です。採用は任意です。これらを必ず使う
必要はありませんが、選定の参考にしてください。

選定にあたっては以下の方針を重視してください:
- 5個のうち少なくとも1個は、記事理解・再利用価値の高い重要な単語または
  単語群(名詞句など、例: "contract worker"、"brent crude"、
  "sea blockade" のようなもの、候補リスト中【重要な単語・単語群候補】と
  記載されたもの)を含めてください。
- 残りは、phrase/idiom/phrasal verbのような複数語表現を優先してください。
  良い候補が不足する場合のみ、単語で補ってください。
- CEFR難易度・語彙レベルを主要な判断軸にしないでください(本文の語彙
  難度は記事生成段階で既に制御済みです)。

候補一覧:
{candidate_lines}
"""
    return base_message + addition


def run_stage1_and_shortlist(article_text: str, dbs: dict) -> dict:
    stage1 = s1.run_stage1_for_article(article_text, dbs)
    existing_canonicals = ({c["canonical_form"] for c in stage1["phrase_survivors"]} |
                            {c["canonical_form"] for c in stage1["important_noun_candidates"]} |
                            {c["canonical_form"] for c in stage1["word_survivors"]})
    lookup_candidates = s1.select_unmatched_ngram_candidates_for_lookup(
        stage1["sentences"], existing_canonicals, budget=WIKTIONARY_MULTIWORD_LOOKUP_BUDGET)
    mw_result = ing.wiktionary_multiword_targeted_lookup(lookup_candidates)
    hits = s1.build_multiword_hit_evidences(mw_result["results"])
    hits_survivors = s1.gate_and_merge_multiword_hits(hits)
    hits_survivors = [h for h in hits_survivors if h["canonical_form"] not in existing_canonicals]

    stage1["important_noun_candidates"] = stage1["important_noun_candidates"] + hits_survivors
    stage1["wiktionary_multiword_lookup"] = {
        "candidates_checked": mw_result["candidate_count"],
        "api_calls": mw_result["api_calls"], "elapsed_sec": mw_result["elapsed_sec"],
        "hits": len(hits), "hits_surviving_gate_and_dedup": len(hits_survivors),
        "hit_terms": [h["canonical_form"] for h in hits_survivors],
    }

    shortlist_info = s1.build_shortlist(stage1)
    return {"stage1": stage1, "shortlist_info": shortlist_info}


def _load_existing_production_key_phrases(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
    elif isinstance(data, list):
        items = data
    else:
        items = []
    result = []
    for item in items:
        if isinstance(item, dict):
            kp = item.get("key_phrase") or item.get("used_form") or item.get("display_phrase")
            if kp:
                result.append(kp)
    return result


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

    try:
        for article_key, (article_path, process) in ARTICLES.items():
            print(f"=== {article_key} ===")
            article_text = open(article_path, encoding="utf-8").read()
            out_dir = os.path.join(OUTPUT_ROOT, article_key)
            os.makedirs(out_dir, exist_ok=True)

            s1r = run_stage1_and_shortlist(article_text, dbs)
            stage1, shortlist_info = s1r["stage1"], s1r["shortlist_info"]
            stops = check_stop_conditions(article_key, stage1, shortlist_info)
            stop_conditions_all[article_key] = stops

            model = routing.require_model(process, routing.SUPPORT_MODEL)
            template = bk.load_prompt_template()
            hybrid_message = build_hybrid_user_message(article_text, shortlist_info["shortlist"], template)
            with open(os.path.join(out_dir, "hybrid_selector_prompt.txt"), "w", encoding="utf-8") as f:
                f.write(hybrid_message)

            hybrid_result = run_selector_once(
                "HYBRID_" + article_key.upper(), article_text, hybrid_message, model,
                cost_tracker, label=f"{article_key}_hybrid")

            existing_path = EXISTING_PRODUCTION_KEY_PHRASES.get(article_key)
            existing_kp = _load_existing_production_key_phrases(existing_path)

            baseline_result = None
            if existing_kp is None:
                baseline_message = bk.build_user_message(article_text, template=template)
                baseline_result = run_selector_once(
                    "BASELINE_" + article_key.upper(), article_text, baseline_message, model,
                    cost_tracker, label=f"{article_key}_baseline_current_production")

            def _serializable_stage1(st):
                keys_to_drop = {"sentences"}
                out = {}
                for k, v in st.items():
                    if k in keys_to_drop:
                        continue
                    out[k] = v
                return out

            article_result = {
                "article_key": article_key,
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
                },
                "hybrid_selector_result": hybrid_result,
                "baseline_current_production_result": baseline_result,
                "existing_production_key_phrases": existing_kp,
                "stop_conditions_triggered": stops,
            }
            with open(os.path.join(out_dir, "hybrid_trial_result.json"), "w", encoding="utf-8") as f:
                json.dump(article_result, f, ensure_ascii=False, indent=2)
            with open(os.path.join(out_dir, "stage1_debug.json"), "w", encoding="utf-8") as f:
                json.dump(_serializable_stage1(stage1), f, ensure_ascii=False, indent=2)

            all_results[article_key] = article_result
            print(f"  stage1: {stage1['before_dedup_count']}->{stage1['stage_a_survivors_count']}"
                  f"->{stage1['stage_b_survivors_count']}, shortlist={shortlist_info['shortlist_total_count']}, "
                  f"hybrid_status={hybrid_result['status']}, stops={stops}")

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
