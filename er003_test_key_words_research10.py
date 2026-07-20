# ============================================================
# er003_test_key_words_research10.py
# ER-003-P2F: A02・ADD03におけるKey Words 3方式×10件の比較調査のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_key_words_research10 -v

import inspect
import json
import unittest

import er003_b2_key_words as p2d
import er003_key_words_strategy_compare as p2e
import er003_key_words_research10 as r10
import er003_ja_to_en_translation as er003

GOOD_ARTICLE = (
    "## Title\n\n"
    "Gordon met it, and England took the lead. This was a huge moment for the team.\n\n"
    "The plan was withdrawn the next day, surprising everyone.\n\n"
    "Ships passed through the strait without incident. The weather stayed calm all day.\n\n"
    "Fans cheered loudly as the final whistle blew. Analysts debated the tactics for hours.\n\n"
    "The coach praised the team spirit. Injuries had tested their depth all season.\n\n"
    "A new stadium will host the next match. Ticket sales broke every previous record."
)

GOOD_SENTENCES = [
    "Gordon met it, and England took the lead.",
    "This was a huge moment for the team.",
    "The plan was withdrawn the next day, surprising everyone.",
    "Ships passed through the strait without incident.",
    "The weather stayed calm all day.",
    "Fans cheered loudly as the final whistle blew.",
    "Analysts debated the tactics for hours.",
    "The coach praised the team spirit.",
    "Injuries had tested their depth all season.",
    "A new stadium will host the next match.",
]


def make_item(rank, display_phrase, source_form, source_sentence, ja_gloss,
              item_type="word", category="general_unknown_word", substitution=False, substitution_reason=""):
    band = "TOP_5" if 1 <= rank <= 5 else "RANK_6_TO_10"
    return {
        "rank": rank, "display_phrase": display_phrase, "source_form": source_form,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "item_type": item_type,
        "selection_reason": "selection reason text", "listening_difficulty_reason": "difficulty reason text",
        "inference_transparency": "LOW", "topic_exposure_dependency": "MEDIUM",
        "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": category, "portfolio_substitution": substitution,
        "portfolio_substitution_reason": substitution_reason, "research_band": band,
    }


def make_items_10(categories=None):
    categories = categories or (
        ["general_unknown_word"] * 2 + ["domain_expression"] * 2 + ["listening_chunk"] * 2
        + ["figurative_emotional"] * 2 + ["causal_contrast"] * 2
    )
    return [
        make_item(i + 1, f"phrase {i}", " ".join(GOOD_SENTENCES[i].split()[:2]), GOOD_SENTENCES[i], f"グロス{i}",
                  "word", categories[i])
        for i in range(10)
    ]


def make_selection(strategy_id, article_id="A02", items=None):
    return {
        "strategy_id": strategy_id, "article_id": article_id, "research_item_count": 10,
        "production_item_count_unchanged": 5, "items": items or make_items_10(),
    }


class InputIsolationTests(unittest.TestCase):
    """要求(共通入力・非対象範囲): A02/ADD03のみ対象。A01を再実行せず、
    P2D/P2E結果・ユーザー具体例をselectorへ渡さない。"""

    def test_article_ids_are_a02_and_add03_only(self):
        self.assertEqual(r10.ARTICLE_IDS, ("A02", "ADD03"))
        self.assertNotIn("A01", r10.ARTICLE_IDS)

    def test_b2_and_summary_paths_reused_from_p2d(self):
        self.assertIs(r10.B2_INPUT_PATHS, p2d.B2_INPUT_PATHS)
        self.assertIs(r10.APPROVED_SUMMARY_PATHS, p2d.APPROVED_SUMMARY_PATHS)

    def test_module_has_no_a01_reselection_function(self):
        self.assertFalse(hasattr(r10, "select_a01"))

    def test_module_does_not_reference_p2e_a01_results(self):
        src = inspect.getsource(r10)
        self.assertNotIn("p2e.USER_HELPFUL_REFERENCE", src)
        self.assertNotIn("p2e.USER_UNHELPFUL_REFERENCE", src)

    def test_strategy_prompts_do_not_contain_a01_user_reference_examples(self):
        a01_examples = list(p2e.USER_HELPFUL_REFERENCE) + list(p2e.USER_UNHELPFUL_REFERENCE)
        for strategy_id in r10.STRATEGY_IDS:
            template = r10.load_strategy_prompt_template(strategy_id)
            for phrase in a01_examples:
                self.assertNotIn(phrase, template, msg=f"{strategy_id}: {phrase}")

    def test_strategy_prompts_do_not_reference_p2d_or_p2e_results(self):
        for strategy_id in r10.STRATEGY_IDS:
            template = r10.load_strategy_prompt_template(strategy_id).lower()
            self.assertNotIn("key_words_selection", template)
            self.assertNotIn("p2d", template)
            self.assertNotIn("p2e", template)

    def test_module_does_not_reference_japanese_or_natural_source(self):
        src = inspect.getsource(r10)
        self.assertNotIn("load_approved_japanese_article", src)
        self.assertNotIn("NATURAL_SOURCE_PATHS", src)

    def test_selectors_have_no_web_search_tool(self):
        for strategy_id in r10.STRATEGY_IDS:
            fn = r10.make_strategy_selector_fn(strategy_id, "dummy", client=object())
            self.assertFalse(fn.uses_web_search_tool)

    def test_three_strategies_use_three_distinct_prompt_templates(self):
        templates = {sid: r10.load_strategy_prompt_template(sid) for sid in r10.STRATEGY_IDS}
        self.assertEqual(len(set(templates.values())), 3)

    def test_model_and_reasoning_effort_match_p2e(self):
        self.assertEqual(r10.SELECTOR_MODEL, p2e.SELECTOR_MODEL)
        self.assertEqual(r10.SELECTOR_REASONING_EFFORT, p2e.SELECTOR_REASONING_EFFORT)

    def test_no_single_call_batch_function(self):
        self.assertFalse(hasattr(r10, "select_all_strategies_in_one_call"))
        self.assertFalse(hasattr(r10, "select_all_articles_in_one_call"))

    def test_production_key_words_count_unchanged_constant(self):
        self.assertEqual(r10.PRODUCTION_ITEM_COUNT_UNCHANGED, 5)

    def test_research_item_count_constant(self):
        self.assertEqual(r10.RESEARCH_ITEM_COUNT, 10)


class SchemaValidatorTests(unittest.TestCase):
    """要求(schema/validator): exactly 10・rank 1-10・band整合・本文
    対応・重複・禁止項目・カウント固定値・方式Pの2件/カテゴリquota。"""

    def test_valid_selection_passes_for_each_strategy(self):
        for strategy_id in r10.STRATEGY_IDS:
            result = r10.validate_research10_selection(
                make_selection(strategy_id), GOOD_ARTICLE, strategy_id, "A02")
            self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=(strategy_id, result))

    def test_strategy_id_mismatch_fails(self):
        result = r10.validate_research10_selection(make_selection("L"), GOOD_ARTICLE, "P", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_article_id_mismatch_fails(self):
        result = r10.validate_research10_selection(make_selection("L", "A02"), GOOD_ARTICLE, "L", "ADD03")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_research_item_count_field_must_be_10(self):
        selection = make_selection("L")
        selection["research_item_count"] = 5
        result = r10.validate_research10_selection(selection, GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_production_item_count_unchanged_field_must_be_5(self):
        selection = make_selection("L")
        selection["production_item_count_unchanged"] = 10
        result = r10.validate_research10_selection(selection, GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_nine_items_fails(self):
        items = make_items_10()[:9]
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_eleven_items_fails(self):
        items = make_items_10() + [make_item(11, "extra", "stadium", GOOD_SENTENCES[9], "追加")]
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_rank_1_to_10_no_gap_no_duplicate_passes(self):
        ranks = [item["rank"] for item in make_items_10()]
        self.assertEqual(sorted(ranks), list(range(1, 11)))

    def test_rank_duplicate_fails(self):
        items = make_items_10()
        items[9] = dict(items[9])
        items[9]["rank"] = 9
        items[9]["research_band"] = "RANK_6_TO_10"
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_rank_gap_fails(self):
        items = make_items_10()
        items[9] = dict(items[9])
        items[9]["rank"] = 15
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_band_mismatch_for_top5_rank_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["research_band"] = "RANK_6_TO_10"  # rank=1本来はTOP_5
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("research_band" in reason for reason in item0["reasons"]))

    def test_band_mismatch_for_rank_6_10_fails(self):
        items = make_items_10()
        items[9] = dict(items[9])
        items[9]["research_band"] = "TOP_5"  # rank=10本来はRANK_6_TO_10
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        item9 = next(r for r in result["item_reasons"] if r["index"] == 9)
        self.assertTrue(any("research_band" in reason for reason in item9["reasons"]))

    def test_invalid_item_type_enum_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["item_type"] = "not_real"
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_sentence_not_in_article_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["source_sentence"] = "This sentence does not exist anywhere."
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_form_not_in_source_sentence_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["source_form"] = "not present at all"
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("source_form" in reason for reason in item0["reasons"]))

    def test_digits_only_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["source_form"] = "20"
        items[0]["display_phrase"] = "20"
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("数字だけ" in reason for reason in item0["reasons"]))

    def test_duplicate_display_phrase_fails(self):
        items = make_items_10()
        items[1] = dict(items[1])
        items[1]["display_phrase"] = items[0]["display_phrase"]
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_empty_ja_gloss_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "   "
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_english_only_ja_gloss_detected(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "an English only gloss"
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("日本語" in reason for reason in item0["reasons"]))

    def test_strategy_p_default_2_per_category_passes(self):
        result = r10.validate_research10_selection(make_selection("P"), GOOD_ARTICLE, "P", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_strategy_p_over_quota_category_without_substitution_fails(self):
        categories = (["general_unknown_word"] * 3 + ["domain_expression"] * 1 + ["listening_chunk"] * 2
                      + ["figurative_emotional"] * 2 + ["causal_contrast"] * 2)
        items = make_items_10(categories)
        result = r10.validate_research10_selection(make_selection("P", items=items), GOOD_ARTICLE, "P", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_strategy_p_over_quota_category_with_substitution_and_reason_passes(self):
        categories = (["general_unknown_word"] * 3 + ["domain_expression"] * 1 + ["listening_chunk"] * 2
                      + ["figurative_emotional"] * 2 + ["causal_contrast"] * 2)
        items = make_items_10(categories)
        for i in (0, 1, 2):
            items[i] = dict(items[i])
            items[i]["portfolio_substitution"] = True
            items[i]["portfolio_substitution_reason"] = "他カテゴリに価値ある候補がなかったため"
        result = r10.validate_research10_selection(make_selection("P", items=items), GOOD_ARTICLE, "P", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_strategy_l_over_quota_category_does_not_require_substitution(self):
        categories = ["general_unknown_word"] * 10
        items = make_items_10(categories)
        result = r10.validate_research10_selection(make_selection("L", items=items), GOOD_ARTICLE, "L", "A02")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_schema_declares_exactly_10_items_for_each_strategy(self):
        for strategy_id in r10.STRATEGY_IDS:
            items_schema = r10.RESEARCH10_JSON_SCHEMAS[strategy_id]["schema"]["properties"]["items"]
            self.assertEqual(items_schema["minItems"], 10)
            self.assertEqual(items_schema["maxItems"], 10)

    def test_schema_enforces_fixed_item_counts(self):
        for strategy_id in r10.STRATEGY_IDS:
            schema_props = r10.RESEARCH10_JSON_SCHEMAS[strategy_id]["schema"]["properties"]
            self.assertEqual(schema_props["research_item_count"]["enum"], [10])
            self.assertEqual(schema_props["production_item_count_unchanged"]["enum"], [5])


class RetryAndSaveTests(unittest.TestCase):
    """要求(再試行): call毎に技術・構造理由のみ最大1回再試行。内容品質
    理由で再生成しない。"""

    def _factory_returning(self, texts):
        texts = texts if isinstance(texts, list) else [texts]
        call_count = {"n": 0}

        def make_factory():
            call_count["n"] += 1
            idx = min(call_count["n"] - 1, len(texts) - 1)
            text = texts[idx]

            def selector_fn():
                if text is None:
                    raise RuntimeError("simulated network error")
                return text, "gpt-5.6-sol", "resp1"
            return selector_fn
        return make_factory, call_count

    def test_pass_on_first_attempt_no_retry(self):
        good_json = json.dumps(make_selection("L"))
        make_factory, call_count = self._factory_returning(good_json)
        parsed, status, attempts, model_id, response_id = r10.run_research10_selection_gate(
            "L", "A02", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)

    def test_structure_invalid_retried_once_then_passes(self):
        bad_json = json.dumps(make_selection("L", items=make_items_10()[:9]))
        good_json = json.dumps(make_selection("L"))
        make_factory, call_count = self._factory_returning([bad_json, good_json])
        parsed, status, attempts, model_id, response_id = r10.run_research10_selection_gate(
            "L", "A02", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_structure_invalid_twice_yields_final_invalid(self):
        bad_json = json.dumps(make_selection("L", items=make_items_10()[:9]))
        make_factory, call_count = self._factory_returning(bad_json)
        parsed, status, attempts, model_id, response_id = r10.run_research10_selection_gate(
            "L", "A02", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], r10.MAX_RESEARCH10_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        good_json = json.dumps(make_selection("U"))
        make_factory, call_count = self._factory_returning([None, good_json])
        parsed, status, attempts, model_id, response_id = r10.run_research10_selection_gate(
            "U", "A02", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_parse_failed_retried_once(self):
        good_json = json.dumps(make_selection("P"))
        make_factory, call_count = self._factory_returning(["not json{{{", good_json])
        parsed, status, attempts, model_id, response_id = r10.run_research10_selection_gate(
            "P", "A02", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_never_calls_comparison_qa(self):
        src = inspect.getsource(r10.run_research10_selection_gate)
        self.assertNotIn("make_comparison_qa_fn", src)
        self.assertNotIn("parse_and_validate_comparison_qa_output", src)

    def test_gate_does_not_change_prompt_between_attempts(self):
        src = inspect.getsource(r10.run_research10_selection_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_strategy_user_message", src)


class ComparisonQaTests(unittest.TestCase):
    """要求(比較QA): 記事別・selectorとは別実行。3方式評価。top5/6-10
    を分離評価。QA結果で選定を書き換えない。"""

    def _valid_qa_output(self, article_id="A02"):
        def strategy_eval(sid):
            return {
                "strategy_id": sid, "top5_unknown_word_capture": "HIGH", "top5_domain_expression_capture": "MEDIUM",
                "top5_listening_chunk_capture": "MEDIUM", "top5_figurative_emotional_capture": "LOW",
                "top5_transparent_easy_item_contamination": "LOW", "top5_low_value_items": [],
                "top5_spoiler_risk": "LOW", "top5_diversity": "HIGH", "rank_6_10_promotion_candidates": [],
                "rank_6_10_demotion_candidates_from_top5": [], "rank_6_10_low_value_increase": "LOW", "notes": "",
            }
        return {
            "article_id": article_id, "strategies": [strategy_eval(sid) for sid in r10.STRATEGY_IDS],
            "cross_strategy_overlap": [], "unique_items_by_strategy": {sid: [] for sid in r10.STRATEGY_IDS},
            "provisional_best_fit": "L", "notes": "",
        }

    def test_valid_qa_output_parses(self):
        parsed = r10.parse_and_validate_comparison_qa_output(json.dumps(self._valid_qa_output()))
        self.assertEqual(parsed["provisional_best_fit"], "L")

    def test_qa_requires_all_three_strategies(self):
        output = self._valid_qa_output()
        output["strategies"] = output["strategies"][:2]
        with self.assertRaises(er003.QaSchemaError):
            r10.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_requires_valid_article_id(self):
        output = self._valid_qa_output()
        output["article_id"] = "A01"
        with self.assertRaises(er003.QaSchemaError):
            r10.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_requires_unique_items_by_strategy_keys(self):
        output = self._valid_qa_output()
        del output["unique_items_by_strategy"]["U"]
        with self.assertRaises(er003.QaSchemaError):
            r10.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_invalid_provisional_best_fit_raises(self):
        output = self._valid_qa_output()
        output["provisional_best_fit"] = "Z"
        with self.assertRaises(er003.QaSchemaError):
            r10.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_top5_and_rank_6_10_fields_present_in_schema(self):
        props = r10.COMPARISON_QA_JSON_SCHEMA["schema"]["properties"]["strategies"]["items"]["properties"]
        self.assertIn("top5_low_value_items", props)
        self.assertIn("rank_6_10_promotion_candidates", props)
        self.assertIn("rank_6_10_demotion_candidates_from_top5", props)
        self.assertIn("rank_6_10_low_value_increase", props)

    def test_qa_does_not_rewrite_items(self):
        schema_fields = set(r10.COMPARISON_QA_JSON_SCHEMA["schema"]["properties"])
        self.assertNotIn("corrected_items", schema_fields)
        self.assertNotIn("display_phrase", schema_fields)

    def test_qa_has_no_web_search_tool(self):
        fn = r10.make_comparison_qa_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_json_response_gate_reused_directly(self):
        self.assertIs(r10.run_json_response_gate, er003.run_json_response_gate)

    def test_qa_non_json_raises(self):
        with self.assertRaises(er003.QaSchemaError):
            r10.parse_and_validate_comparison_qa_output("not json")


class BlindMappingTests(unittest.TestCase):
    """要求(ブラインドレビュー): 記事別に固定seedで決定的にL/P/UをSet
    X/Y/Zへ割り当てる。A02とADD03は別mappingでよい。"""

    def test_mapping_covers_all_three_strategies_bijectively(self):
        for article_id in r10.ARTICLE_IDS:
            mapping = r10.build_blind_mapping(article_id)
            self.assertEqual(set(mapping.values()), set(r10.STRATEGY_IDS))

    def test_mapping_deterministic_across_calls(self):
        m1 = r10.build_blind_mapping("A02")
        m2 = r10.build_blind_mapping("A02")
        self.assertEqual(m1, m2)

    def test_a02_and_add03_use_distinct_seeds(self):
        self.assertNotEqual(r10.BLIND_MAPPING_SEEDS["A02"], r10.BLIND_MAPPING_SEEDS["ADD03"])

    def test_a01_seed_not_reused(self):
        self.assertNotIn(p2e.BLIND_MAPPING_SEED, r10.BLIND_MAPPING_SEEDS.values())


class ReadingCopyAndMetricsTests(unittest.TestCase):
    """要求(読み上げ原稿・指標): P2Dのビルダーをrank->orderアダプタ経由
    で再利用し、決定的に構成する。RESEARCH_ONLYであることを前提とする
    設計(製品参照manifestは触らない)。"""

    def test_reading_copy_generated_deterministically(self):
        items = make_items_10()
        copy1 = r10.build_research_reading_copy(items)
        copy2 = r10.build_research_reading_copy(items)
        self.assertEqual(copy1, copy2)
        self.assertEqual(copy1.count("## Key Words"), 1)

    def test_reading_copy_uses_p2d_builder_via_adapter(self):
        src = inspect.getsource(r10.build_research_reading_copy)
        self.assertIn("p2d.build_key_words_reading_copy", src)

    def test_reading_copy_not_generated_by_llm(self):
        src = inspect.getsource(r10.build_research_reading_copy)
        self.assertNotIn("responses.create", src)

    def test_metrics_computed_by_python(self):
        items = make_items_10()
        metrics = r10.compute_research10_metrics(items)
        self.assertEqual(metrics["item_count"], 10)
        self.assertEqual(metrics["top5_count"], 5)
        self.assertEqual(metrics["rank_6_10_count"], 5)


class RegressionAndIsolationTests(unittest.TestCase):
    """要求(回帰・非対象範囲): TTS・外部辞書・P2D/P2E成果物の上書きなし。"""

    def test_module_does_not_call_tts(self):
        src = inspect.getsource(r10)
        self.assertNotIn("elevenlabs", src.lower())
        self.assertNotIn("text_to_speech", src.lower())

    def test_module_does_not_reference_external_dictionary(self):
        src = inspect.getsource(r10)
        self.assertNotIn("wordnet", src.lower())
        self.assertNotIn("dictionary_api", src.lower())

    def test_module_does_not_write_to_official_reference_manifest(self):
        src = inspect.getsource(r10)
        self.assertNotIn("ER-003-P2C_reference_manifest", src)

    def test_validator_never_returns_fixed_or_corrected_items(self):
        result = r10.validate_research10_selection(make_selection("L"), GOOD_ARTICLE, "L", "A02")
        self.assertNotIn("fixed_items", result)
        self.assertNotIn("corrected_items", result)


if __name__ == "__main__":
    unittest.main()
