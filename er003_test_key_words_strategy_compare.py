# ============================================================
# er003_test_key_words_strategy_compare.py
# ER-003-P2E: Key Words選定軸3方式の同時比較のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_key_words_strategy_compare -v

import inspect
import json
import unittest

import er003_b2_key_words as p2d
import er003_key_words_strategy_compare as sc
import er003_ja_to_en_translation as er003

GOOD_ARTICLE = (
    "## Title\n\n"
    "Gordon met it, and England took the lead. This was a huge moment for the team.\n\n"
    "The plan was withdrawn the next day, surprising everyone.\n\n"
    "Ships passed through the strait without incident."
)


def make_item(order, display_phrase, source_form, source_sentence, ja_gloss,
              item_type="word", category="general_unknown_word", substitution=False, substitution_reason=""):
    return {
        "order": order, "display_phrase": display_phrase, "source_form": source_form,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "item_type": item_type,
        "selection_reason": "selection reason text", "listening_difficulty_reason": "difficulty reason text",
        "inference_transparency": "LOW", "topic_exposure_dependency": "MEDIUM",
        "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": category, "portfolio_substitution": substitution,
        "portfolio_substitution_reason": substitution_reason,
    }


def make_items_diverse_categories():
    return [
        make_item(1, "take the lead", "took the lead", "Gordon met it, and England took the lead.",
                  "リードを奪う", "collocation", "general_unknown_word"),
        make_item(2, "huge moment", "huge moment", "This was a huge moment for the team.",
                  "重要な瞬間", "collocation", "domain_expression"),
        make_item(3, "withdraw", "was withdrawn", "The plan was withdrawn the next day, surprising everyone.",
                  "撤回する", "word", "listening_chunk"),
        make_item(4, "surprise", "surprising", "The plan was withdrawn the next day, surprising everyone.",
                  "驚かせる", "phrasal_verb", "figurative_emotional"),
        make_item(5, "without incident", "without incident", "Ships passed through the strait without incident.",
                  "支障なく", "idiomatic_phrase", "causal_contrast"),
    ]


def make_selection(strategy_id, items=None):
    return {"strategy_id": strategy_id, "article_id": "A01", "items": items or make_items_diverse_categories()}


class InputIsolationTests(unittest.TestCase):
    """要求(共通入力): selector入力はA01のapproved概要+確定B2本文のみ。
    P2D選定結果・ユーザー具体例・日本語原稿等は一切参照しない。"""

    def test_b2_and_summary_paths_reused_from_p2d(self):
        self.assertIs(sc.B2_INPUT_PATHS, p2d.B2_INPUT_PATHS)
        self.assertIs(sc.APPROVED_SUMMARY_PATHS, p2d.APPROVED_SUMMARY_PATHS)

    def test_target_topic_is_a01(self):
        self.assertEqual(sc.TARGET_TOPIC_ID, "A01")

    def test_strategy_prompts_do_not_contain_user_reference_examples(self):
        for strategy_id in sc.STRATEGY_IDS:
            template = sc.load_strategy_prompt_template(strategy_id)
            for phrase in sc.USER_HELPFUL_REFERENCE + sc.USER_UNHELPFUL_REFERENCE:
                self.assertNotIn(phrase, template, msg=f"{strategy_id}: {phrase}")

    def test_strategy_prompts_do_not_reference_p2d_results(self):
        for strategy_id in sc.STRATEGY_IDS:
            template = sc.load_strategy_prompt_template(strategy_id).lower()
            self.assertNotIn("key_words_selection", template)
            self.assertNotIn("p2d", template)

    def test_module_does_not_reference_japanese_or_natural_source(self):
        src = inspect.getsource(sc)
        self.assertNotIn("load_approved_japanese_article", src)
        self.assertNotIn("NATURAL_SOURCE_PATHS", src)

    def test_selectors_have_no_web_search_tool(self):
        for strategy_id in sc.STRATEGY_IDS:
            fn = sc.make_strategy_selector_fn(strategy_id, "dummy", client=object())
            self.assertFalse(fn.uses_web_search_tool)

    def test_three_strategies_use_three_distinct_prompt_templates(self):
        templates = {sid: sc.load_strategy_prompt_template(sid) for sid in sc.STRATEGY_IDS}
        self.assertEqual(len(set(templates.values())), 3)

    def test_model_and_reasoning_effort_match_p2d(self):
        self.assertEqual(sc.SELECTOR_MODEL, p2d.SELECTOR_MODEL)
        self.assertEqual(sc.SELECTOR_REASONING_EFFORT, p2d.SELECTOR_REASONING_EFFORT)

    def test_no_batch_all_strategies_single_call_function(self):
        # 3方式は独立callであるべきで、1 callへまとめる関数を持たない
        self.assertFalse(hasattr(sc, "select_all_strategies_in_one_call"))

    def test_reference_sets_only_used_by_comparison_qa_builder(self):
        selector_src = "".join(inspect.getsource(sc.make_strategy_selector_fn))
        self.assertNotIn("USER_HELPFUL_REFERENCE", selector_src)
        self.assertNotIn("USER_UNHELPFUL_REFERENCE", selector_src)
        qa_src = inspect.getsource(sc.build_comparison_qa_prompt)
        self.assertIn("USER_HELPFUL_REFERENCE", qa_src)
        self.assertIn("USER_UNHELPFUL_REFERENCE", qa_src)


class SchemaValidatorTests(unittest.TestCase):
    """要求(共通validator): exactly 5・schema・本文対応・重複・禁止項目、
    方式Pのカテゴリ重複時のsubstitution必須ルール。"""

    def test_valid_selection_passes_for_each_strategy(self):
        for strategy_id in sc.STRATEGY_IDS:
            result = sc.validate_strategy_selection(make_selection(strategy_id), GOOD_ARTICLE, strategy_id)
            self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=(strategy_id, result))

    def test_strategy_id_mismatch_fails(self):
        result = sc.validate_strategy_selection(make_selection("L"), GOOD_ARTICLE, "P")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_four_items_fails(self):
        items = make_items_diverse_categories()[:4]
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_six_items_fails(self):
        items = make_items_diverse_categories() + [
            make_item(6, "extra", "incident", "Ships passed through the strait without incident.", "追加")]
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_order_duplicate_fails(self):
        items = make_items_diverse_categories()
        items[4] = dict(items[4])
        items[4]["order"] = 4
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_order_gap_fails(self):
        items = make_items_diverse_categories()
        items[4] = dict(items[4])
        items[4]["order"] = 9
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_item_type_enum_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["item_type"] = "not_real"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_tri_level_enum_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["comprehension_impact"] = "SUPER_HIGH"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_portfolio_category_enum_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["portfolio_category"] = "not_a_category"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_sentence_not_in_article_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["source_sentence"] = "This sentence does not exist anywhere."
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_form_not_in_source_sentence_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["source_form"] = "not present at all"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("source_form" in reason for reason in item0["reasons"]))

    def test_digits_only_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["source_form"] = "20"
        items[0]["display_phrase"] = "20"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("数字だけ" in reason for reason in item0["reasons"]))

    def test_date_only_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["source_form"] = "July 15"
        items[0]["display_phrase"] = "July 15"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("日付だけ" in reason for reason in item0["reasons"]))

    def test_duplicate_display_phrase_fails(self):
        items = make_items_diverse_categories()
        items[1] = dict(items[1])
        items[1]["display_phrase"] = items[0]["display_phrase"]
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_empty_ja_gloss_fails(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "   "
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_english_only_ja_gloss_detected(self):
        items = make_items_diverse_categories()
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "to take the lead"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("日本語" in reason for reason in item0["reasons"]))

    def test_strategy_p_category_duplicate_without_substitution_fails(self):
        items = make_items_diverse_categories()
        items[4] = dict(items[4])
        items[4]["portfolio_category"] = "general_unknown_word"  # duplicates item[0]
        items[4]["portfolio_substitution"] = False
        result = sc.validate_strategy_selection(make_selection("P", items), GOOD_ARTICLE, "P")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_strategy_p_category_duplicate_with_substitution_and_reason_passes(self):
        items = make_items_diverse_categories()
        items[4] = dict(items[4])
        items[4]["portfolio_category"] = "general_unknown_word"
        items[4]["portfolio_substitution"] = True
        items[4]["portfolio_substitution_reason"] = "価値ある候補が他カテゴリになかったため"
        items[0] = dict(items[0])
        items[0]["portfolio_substitution"] = True
        items[0]["portfolio_substitution_reason"] = "価値ある候補が他カテゴリになかったため"
        result = sc.validate_strategy_selection(make_selection("P", items), GOOD_ARTICLE, "P")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_strategy_l_category_duplicate_does_not_require_substitution(self):
        # substitutionルールは方式Pのみに適用される
        items = make_items_diverse_categories()
        items[4] = dict(items[4])
        items[4]["portfolio_category"] = "general_unknown_word"
        result = sc.validate_strategy_selection(make_selection("L", items), GOOD_ARTICLE, "L")
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_category_distribution_saved(self):
        result = sc.validate_strategy_selection(make_selection("P"), GOOD_ARTICLE, "P")
        self.assertIn("category_distribution", result)
        self.assertEqual(sum(result["category_distribution"].values()), 5)

    def test_schema_declares_exactly_5_items_for_each_strategy(self):
        for strategy_id in sc.STRATEGY_IDS:
            items_schema = sc.STRATEGY_JSON_SCHEMAS[strategy_id]["schema"]["properties"]["items"]
            self.assertEqual(items_schema["minItems"], 5)
            self.assertEqual(items_schema["maxItems"], 5)


class RetryAndSaveTests(unittest.TestCase):
    """要求(再試行): 方式ごとに技術・構造理由のみ最大1回再試行。
    内容品質理由で再生成しない。他方式の結果を参照しない。"""

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
        parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
            "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)

    def test_structure_invalid_retried_once_then_passes(self):
        bad_json = json.dumps(make_selection("L", make_items_diverse_categories()[:4]))
        good_json = json.dumps(make_selection("L"))
        make_factory, call_count = self._factory_returning([bad_json, good_json])
        parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
            "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_structure_invalid_twice_yields_final_invalid(self):
        bad_json = json.dumps(make_selection("L", make_items_diverse_categories()[:4]))
        make_factory, call_count = self._factory_returning(bad_json)
        parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
            "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], sc.MAX_STRATEGY_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        good_json = json.dumps(make_selection("U"))
        make_factory, call_count = self._factory_returning([None, good_json])
        parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
            "U", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_parse_failed_retried_once(self):
        good_json = json.dumps(make_selection("P"))
        make_factory, call_count = self._factory_returning(["not json{{{", good_json])
        parsed, status, attempts, model_id, response_id = sc.run_strategy_selection_gate(
            "P", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_never_calls_comparison_qa(self):
        src = inspect.getsource(sc.run_strategy_selection_gate)
        self.assertNotIn("make_comparison_qa_fn", src)
        self.assertNotIn("parse_and_validate_comparison_qa_output", src)

    def test_gate_does_not_change_prompt_between_attempts(self):
        src = inspect.getsource(sc.run_strategy_selection_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_strategy_user_message", src)

    def test_all_attempts_include_raw_text(self):
        bad_json = json.dumps(make_selection("L", make_items_diverse_categories()[:4]))
        good_json = json.dumps(make_selection("L"))
        make_factory, _ = self._factory_returning([bad_json, good_json])
        _, _, attempts, _, _ = sc.run_strategy_selection_gate("L", make_factory, GOOD_ARTICLE)
        for a in attempts:
            self.assertIn("raw_text", a)


class ComparisonQaTests(unittest.TestCase):
    """要求(比較QA): selectorとは別実行。3方式全てを評価する。
    QA結果で選定を書き換えない。"""

    def _valid_qa_output(self):
        def strategy_eval(sid):
            return {
                "strategy_id": sid, "unknown_word_capture": "HIGH", "domain_expression_capture": "MEDIUM",
                "listening_chunk_capture": "MEDIUM", "figurative_emotional_capture": "LOW",
                "transparent_easy_item_contamination": "LOW", "comprehension_contribution": "HIGH",
                "diversity": "HIGH", "overall_spoiler_risk": "LOW", "gloss_quality": "HIGH",
                "helpful_reference_matches": [], "unhelpful_reference_overlaps": [], "notes": "",
            }
        return {
            "strategies": [strategy_eval(sid) for sid in sc.STRATEGY_IDS],
            "cross_strategy_overlap": [], "unique_items_by_strategy": {sid: [] for sid in sc.STRATEGY_IDS},
            "provisional_best_fit": "L", "notes": "",
        }

    def test_valid_qa_output_parses(self):
        parsed = sc.parse_and_validate_comparison_qa_output(json.dumps(self._valid_qa_output()))
        self.assertEqual(parsed["provisional_best_fit"], "L")

    def test_qa_requires_all_three_strategies(self):
        output = self._valid_qa_output()
        output["strategies"] = output["strategies"][:2]
        with self.assertRaises(er003.QaSchemaError):
            sc.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_requires_unique_items_by_strategy_keys(self):
        output = self._valid_qa_output()
        del output["unique_items_by_strategy"]["U"]
        with self.assertRaises(er003.QaSchemaError):
            sc.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_invalid_provisional_best_fit_raises(self):
        output = self._valid_qa_output()
        output["provisional_best_fit"] = "Z"
        with self.assertRaises(er003.QaSchemaError):
            sc.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_missing_strategy_id_coverage_raises(self):
        output = self._valid_qa_output()
        output["strategies"][2]["strategy_id"] = "L"  # duplicate L, missing U
        with self.assertRaises(er003.QaSchemaError):
            sc.parse_and_validate_comparison_qa_output(json.dumps(output))

    def test_qa_does_not_rewrite_items(self):
        schema_fields = set(sc.COMPARISON_QA_JSON_SCHEMA["schema"]["properties"])
        self.assertNotIn("corrected_items", schema_fields)
        self.assertNotIn("display_phrase", schema_fields)

    def test_qa_has_no_web_search_tool(self):
        fn = sc.make_comparison_qa_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_qa_prompt_includes_reference_sets(self):
        prompt = sc.build_comparison_qa_prompt("SUM", "ART", "{}")
        for phrase in sc.USER_HELPFUL_REFERENCE:
            self.assertIn(phrase, prompt)
        for phrase in sc.USER_UNHELPFUL_REFERENCE:
            self.assertIn(phrase, prompt)

    def test_json_response_gate_reused_directly(self):
        self.assertIs(sc.run_json_response_gate, er003.run_json_response_gate)

    def test_qa_non_json_raises(self):
        with self.assertRaises(er003.QaSchemaError):
            sc.parse_and_validate_comparison_qa_output("not json")


class BlindMappingTests(unittest.TestCase):
    """要求(ブラインドレビュー): 固定seedで決定的にL/P/UをSet X/Y/Zへ割り当てる。"""

    def test_mapping_covers_all_three_strategies_bijectively(self):
        mapping = sc.build_blind_mapping()
        self.assertEqual(set(mapping.values()), set(sc.STRATEGY_IDS))
        self.assertEqual(len(mapping), 3)

    def test_mapping_deterministic_with_same_seed(self):
        m1 = sc.build_blind_mapping(seed=123)
        m2 = sc.build_blind_mapping(seed=123)
        self.assertEqual(m1, m2)

    def test_default_seed_is_fixed_constant(self):
        self.assertIsInstance(sc.BLIND_MAPPING_SEED, int)
        m1 = sc.build_blind_mapping()
        m2 = sc.build_blind_mapping(seed=sc.BLIND_MAPPING_SEED)
        self.assertEqual(m1, m2)

    def test_different_seed_may_produce_different_mapping(self):
        m_default = sc.build_blind_mapping(seed=1)
        m_other = sc.build_blind_mapping(seed=2)
        # 異なるseedで必ず異なるとは限らないが、少なくとも両方とも有効な
        # 全単射であることを確認する
        self.assertEqual(set(m_default.values()), set(sc.STRATEGY_IDS))
        self.assertEqual(set(m_other.values()), set(sc.STRATEGY_IDS))


class ReadingCopyAndMetricsTests(unittest.TestCase):
    """要求(読み上げ原稿): P2Dと同じ決定的ビルダーを再利用する。"""

    def test_reading_copy_builder_reused_directly_from_p2d(self):
        self.assertIs(sc.build_key_words_reading_copy, p2d.build_key_words_reading_copy)

    def test_reading_copy_generated_deterministically(self):
        items = make_items_diverse_categories()
        copy1 = sc.build_key_words_reading_copy(items)
        copy2 = sc.build_key_words_reading_copy(items)
        self.assertEqual(copy1, copy2)
        self.assertEqual(copy1.count("## Key Words"), 1)

    def test_metrics_computed_by_python(self):
        items = make_items_diverse_categories()
        reading_copy = sc.build_key_words_reading_copy(items)
        metrics = sc.compute_strategy_metrics(items, reading_copy)
        self.assertEqual(metrics["item_count"], 5)
        self.assertEqual(sum(metrics["portfolio_category_counts"].values()), 5)


class RegressionAndIsolationTests(unittest.TestCase):
    """要求(回帰・非対象範囲): TTS・外部辞書・A02/ADD03再選定・既存P2D
    成果物の上書きなし。"""

    def test_module_does_not_call_tts(self):
        src = inspect.getsource(sc)
        self.assertNotIn("elevenlabs", src.lower())
        self.assertNotIn("text_to_speech", src.lower())

    def test_module_does_not_reference_external_dictionary(self):
        src = inspect.getsource(sc)
        self.assertNotIn("wordnet", src.lower())
        self.assertNotIn("dictionary_api", src.lower())

    def test_module_has_no_a02_or_add03_reselection_function(self):
        self.assertFalse(hasattr(sc, "select_a02"))
        self.assertFalse(hasattr(sc, "select_add03"))

    def test_validator_never_returns_fixed_or_corrected_items(self):
        result = sc.validate_strategy_selection(make_selection("L"), GOOD_ARTICLE, "L")
        self.assertNotIn("fixed_items", result)
        self.assertNotIn("corrected_items", result)


if __name__ == "__main__":
    unittest.main()
