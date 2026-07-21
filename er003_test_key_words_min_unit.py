# ============================================================
# er003_test_key_words_min_unit.py
# ER-003-P2G: Key Words最小単位化＋3記事×3方式ブラインド再比較のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_key_words_min_unit -v

import inspect
import json
import unittest

import er003_b2_key_words as p2d
import er003_key_words_strategy_compare as p2e
import er003_key_words_min_unit as mu
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


def make_item(rank, display_phrase, source_span, source_sentence, ja_gloss,
              phrase_type="word", normalization_type="none", category="general_unknown_word",
              substitution=False, substitution_reason=""):
    return {
        "rank": rank, "display_phrase": display_phrase, "source_span": source_span,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "phrase_type": phrase_type,
        "normalization_type": normalization_type, "normalization_note": "note",
        "selection_reason": "selection reason text", "listening_difficulty_reason": "difficulty reason text",
        "inference_transparency": "LOW", "topic_exposure_dependency": "MEDIUM",
        "comprehension_impact": "HIGH", "figurative_or_emotional_value": "LOW", "spoiler_risk": "LOW",
        "portfolio_category": category, "portfolio_substitution": substitution,
        "portfolio_substitution_reason": substitution_reason,
    }


def make_items_10(categories=None):
    categories = categories or (
        ["general_unknown_word"] * 2 + ["domain_expression"] * 2 + ["compact_listening_pattern"] * 2
        + ["figurative_emotional"] * 2 + ["causal_contrast"] * 2
    )
    return [
        make_item(i + 1, f"phrase {i}", " ".join(GOOD_SENTENCES[i].split()[:2]), GOOD_SENTENCES[i], f"グロス{i}",
                  "word", "none", categories[i])
        for i in range(10)
    ]


def with_metadata(items, article_id="A02", strategy_id="L"):
    return mu.attach_runtime_metadata({"items": items}, article_id, strategy_id)


class InputIsolationTests(unittest.TestCase):
    """要求(共通入力): 3記事のみ対象。旧成果物・ユーザー具体例・
    他記事/他方式の結果をselectorへ渡さない。"""

    def test_article_ids_are_a01_a02_add03(self):
        self.assertEqual(mu.ARTICLE_IDS, ("A01", "A02", "ADD03"))

    def test_b2_and_summary_paths_reused_from_p2d(self):
        self.assertIs(mu.B2_INPUT_PATHS, p2d.B2_INPUT_PATHS)
        self.assertIs(mu.APPROVED_SUMMARY_PATHS, p2d.APPROVED_SUMMARY_PATHS)

    def test_strategy_prompts_do_not_contain_a01_user_reference_examples(self):
        a01_examples = list(p2e.USER_HELPFUL_REFERENCE) + list(p2e.USER_UNHELPFUL_REFERENCE)
        for strategy_id in mu.STRATEGY_IDS:
            template = mu.load_strategy_prompt_template(strategy_id)
            for phrase in a01_examples:
                self.assertNotIn(phrase, template, msg=f"{strategy_id}: {phrase}")

    def test_strategy_prompts_do_not_contain_forbidden_spec_examples(self):
        forbidden = ["shook global energy supply routes", "the bigger question was whether"]
        for strategy_id in mu.STRATEGY_IDS:
            template = mu.load_strategy_prompt_template(strategy_id)
            for phrase in forbidden:
                self.assertNotIn(phrase, template, msg=f"{strategy_id}: {phrase}")

    def test_strategy_prompts_do_not_reference_prior_stage_results(self):
        for strategy_id in mu.STRATEGY_IDS:
            template = mu.load_strategy_prompt_template(strategy_id).lower()
            self.assertNotIn("p2d", template)
            self.assertNotIn("p2e", template)
            self.assertNotIn("p2f", template)

    def test_selectors_have_no_web_search_tool(self):
        fn = mu.make_strategy_selector_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_three_strategies_use_three_distinct_prompt_templates(self):
        templates = {sid: mu.load_strategy_prompt_template(sid) for sid in mu.STRATEGY_IDS}
        self.assertEqual(len(set(templates.values())), 3)

    def test_model_and_reasoning_effort_match_p2e(self):
        self.assertEqual(mu.SELECTOR_MODEL, p2e.SELECTOR_MODEL)
        self.assertEqual(mu.SELECTOR_REASONING_EFFORT, p2e.SELECTOR_REASONING_EFFORT)

    def test_no_batch_function(self):
        self.assertFalse(hasattr(mu, "select_all_in_one_call"))

    def test_production_and_research_counts(self):
        self.assertEqual(mu.RESEARCH_ITEM_COUNT, 10)
        self.assertEqual(mu.PRODUCTION_ITEM_COUNT_UNCHANGED, 5)


class RuntimeMetadataTests(unittest.TestCase):
    """要求(section 8): article_id/strategy_id/counts はmodel schemaに
    含まれず、runtimeが決定的に付与する。model自己申告に依存しない。"""

    def test_model_schema_has_no_article_id_field(self):
        schema_props = mu.SELECTOR_JSON_SCHEMA["schema"]["properties"]
        self.assertNotIn("article_id", schema_props)

    def test_model_schema_has_no_strategy_id_field(self):
        schema_props = mu.SELECTOR_JSON_SCHEMA["schema"]["properties"]
        self.assertNotIn("strategy_id", schema_props)

    def test_model_schema_has_no_count_fields(self):
        schema_props = mu.SELECTOR_JSON_SCHEMA["schema"]["properties"]
        self.assertNotIn("research_item_count", schema_props)
        self.assertNotIn("production_item_count_unchanged", schema_props)

    def test_item_schema_has_no_research_band_field(self):
        item_props = mu.SELECTOR_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"]
        self.assertNotIn("research_band", item_props)

    def test_attach_runtime_metadata_sets_article_and_strategy(self):
        result = mu.attach_runtime_metadata({"items": make_items_10()}, "ADD03", "P")
        self.assertEqual(result["article_id"], "ADD03")
        self.assertEqual(result["strategy_id"], "P")
        self.assertEqual(result["research_item_count"], 10)
        self.assertEqual(result["production_item_count_unchanged"], 5)

    def test_attach_runtime_metadata_assigns_research_band_from_rank(self):
        result = mu.attach_runtime_metadata({"items": make_items_10()}, "A02", "L")
        for item in result["items"]:
            expected = "TOP_5" if item["rank"] <= 5 else "RANK_6_TO_10"
            self.assertEqual(item["research_band"], expected)

    def test_p2f_style_wrong_article_id_in_model_output_does_not_matter(self):
        # モデルが誤ったIDを自己申告するフィールド自体が存在しないため、
        # P2Fのarticle_id誤記問題は構造的に発生しない。
        fake_model_output = {"items": make_items_10()}
        self.assertNotIn("article_id", fake_model_output)
        result = mu.attach_runtime_metadata(fake_model_output, "A02", "L")
        self.assertEqual(result["article_id"], "A02")


class DisplayPhraseFormTests(unittest.TestCase):
    """要求(section 7.2-7.4、24番): 1〜5語hard gate、完全文・節排除、
    有限助動詞排除、正規化の受入例。"""

    def test_one_word_passes(self):
        self.assertTrue(mu.validate_display_phrase_form("rivalry")["ok"])

    def test_five_words_passes(self):
        self.assertTrue(mu.validate_display_phrase_form("take the lead in style")["ok"])

    def test_six_words_fails(self):
        result = mu.validate_display_phrase_form("take the lead in the match")
        self.assertFalse(result["ok"])
        self.assertTrue(any("語でない" in r for r in result["reasons"]))

    def test_hyphenated_word_counts_as_one(self):
        result = mu.validate_display_phrase_form("well-known fact")
        self.assertEqual(result["word_count"], 2)
        self.assertTrue(result["ok"])

    def test_contraction_counts_as_one(self):
        result = mu.validate_display_phrase_form("don't worry")
        self.assertEqual(result["word_count"], 2)
        self.assertTrue(result["ok"])

    def test_full_sentence_fails(self):
        result = mu.validate_display_phrase_form("The plan was still in place.")
        self.assertFalse(result["ok"])

    def test_subject_plus_finite_verb_clause_fails(self):
        result = mu.validate_display_phrase_form("the bigger question was whether")
        self.assertFalse(result["ok"])

    def test_question_fails(self):
        result = mu.validate_display_phrase_form("why did it happen?")
        self.assertFalse(result["ok"])

    def test_ellipsis_fails(self):
        result = mu.validate_display_phrase_form("take the lead...")
        self.assertFalse(result["ok"])

    def test_terminal_punctuation_fails(self):
        result = mu.validate_display_phrase_form("take the lead.")
        self.assertFalse(result["ok"])

    def test_past_tense_auxiliary_residue_fails(self):
        result = mu.validate_display_phrase_form("had taken a different form")
        self.assertFalse(result["ok"])

    def test_perfect_auxiliary_residue_fails(self):
        result = mu.validate_display_phrase_form("has been withdrawn")
        self.assertFalse(result["ok"])

    def test_base_verb_phrase_passes(self):
        result = mu.validate_display_phrase_form("take a different form")
        self.assertTrue(result["ok"], msg=result["reasons"])

    def test_passive_base_with_bare_be_passes(self):
        result = mu.validate_display_phrase_form("be withdrawn")
        self.assertTrue(result["ok"], msg=result["reasons"])

    def test_synthetic_long_source_normalizes_to_accepted_base_form(self):
        # section 7.4の正規化例: "had taken a completely different form" ->
        # "take a different form"
        long_source = "had taken a completely different form"
        normalized = "take a different form"
        self.assertFalse(mu.validate_display_phrase_form(long_source)["ok"])
        self.assertTrue(mu.validate_display_phrase_form(normalized)["ok"])

    def test_quote_wrapper_fails(self):
        result = mu.validate_display_phrase_form('"take the lead"')
        self.assertFalse(result["ok"])

    def test_pronoun_initial_is_warning_not_failure(self):
        result = mu.validate_display_phrase_form("it worked")
        self.assertTrue(result["ok"])
        self.assertTrue(any("pronoun" in w.lower() for w in result["warnings"]))

    def test_digits_only_word_count_still_evaluated(self):
        result = mu.validate_display_phrase_form("20")
        self.assertEqual(result["word_count"], 1)


class SchemaValidatorTests(unittest.TestCase):
    """要求(section 12): exactly 10・rank・本文対応・重複検証。"""

    def test_valid_selection_passes(self):
        result = mu.validate_min_unit_selection(with_metadata(make_items_10()), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_nine_items_fails(self):
        items = make_items_10()[:9]
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_rank_duplicate_fails(self):
        items = make_items_10()
        items[9] = dict(items[9])
        items[9]["rank"] = 9
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_display_phrase_too_long_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["display_phrase"] = "one two three four five six"
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("語でない" in reason for reason in item0["reasons"]))

    def test_full_sentence_display_phrase_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["display_phrase"] = "The plan was still in place."
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_sentence_not_in_article_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["source_sentence"] = "This sentence does not exist anywhere."
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_span_not_in_source_sentence_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["source_span"] = "not present at all"
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        item0 = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("source_span" in reason for reason in item0["reasons"]))

    def test_duplicate_display_phrase_fails(self):
        items = make_items_10()
        items[1] = dict(items[1])
        items[1]["display_phrase"] = items[0]["display_phrase"]
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_phrase_type_enum_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["phrase_type"] = "not_real"
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_normalization_type_enum_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["normalization_type"] = "not_real"
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_empty_ja_gloss_fails(self):
        items = make_items_10()
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "   "
        result = mu.validate_min_unit_selection(with_metadata(items), GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")


class RetryAndSaveTests(unittest.TestCase):
    """要求(section 14): job毎にhard requirement理由のみ最大1回再試行。
    内容品質理由で再生成しない。"""

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
        good_json = json.dumps({"items": make_items_10()})
        make_factory, call_count = self._factory_returning(good_json)
        parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
            "A02", "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)
        self.assertEqual(parsed["article_id"], "A02")
        self.assertEqual(parsed["strategy_id"], "L")

    def test_hard_form_violation_retried_once_then_passes(self):
        bad_items = make_items_10()
        bad_items[0] = dict(bad_items[0])
        bad_items[0]["display_phrase"] = "one two three four five six"
        bad_json = json.dumps({"items": bad_items})
        good_json = json.dumps({"items": make_items_10()})
        make_factory, call_count = self._factory_returning([bad_json, good_json])
        parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
            "A02", "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_hard_form_violation_twice_yields_final_invalid(self):
        bad_items = make_items_10()
        bad_items[0] = dict(bad_items[0])
        bad_items[0]["display_phrase"] = "one two three four five six"
        bad_json = json.dumps({"items": bad_items})
        make_factory, call_count = self._factory_returning(bad_json)
        parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
            "A02", "L", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], mu.MAX_MIN_UNIT_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        good_json = json.dumps({"items": make_items_10()})
        make_factory, call_count = self._factory_returning([None, good_json])
        parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
            "A02", "U", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_parse_failed_retried_once(self):
        good_json = json.dumps({"items": make_items_10()})
        make_factory, call_count = self._factory_returning(["not json{{{", good_json])
        parsed, status, attempts, model_id, response_id = mu.run_min_unit_selection_gate(
            "A02", "P", make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_never_calls_form_qa(self):
        src = inspect.getsource(mu.run_min_unit_selection_gate)
        self.assertNotIn("make_form_qa_fn", src)
        self.assertNotIn("parse_and_validate_form_qa_output", src)

    def test_gate_does_not_change_prompt_between_attempts(self):
        src = inspect.getsource(mu.run_min_unit_selection_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_strategy_user_message", src)

    def test_all_attempts_include_raw_text(self):
        bad_items = make_items_10()
        bad_items[0] = dict(bad_items[0])
        bad_items[0]["display_phrase"] = "one two three four five six"
        bad_json = json.dumps({"items": bad_items})
        good_json = json.dumps({"items": make_items_10()})
        make_factory, _ = self._factory_returning([bad_json, good_json])
        _, _, attempts, _, _ = mu.run_min_unit_selection_gate("A02", "L", make_factory, GOOD_ARTICLE)
        for a in attempts:
            self.assertIn("raw_text", a)


class FormQaTests(unittest.TestCase):
    """要求(section 13): 記事ごとに3方式・30項目まとめて形式QA。方式
    比較・best fitは行わない。項目を書き換えない。"""

    def _valid_qa_output(self):
        def item_eval(rank):
            return {"rank": rank, "form_verdict": "PASS", "minimal_unit": "PASS", "not_a_clause": "PASS",
                    "canonical_form": "PASS", "source_fidelity": "PASS", "gloss_match": "PASS", "notes": ""}
        return {"sets": [{"runtime_strategy_id": sid, "items": [item_eval(i + 1) for i in range(10)]}
                          for sid in ("L", "P", "U")]}

    def test_valid_form_qa_output_parses(self):
        parsed = mu.parse_and_validate_form_qa_output(json.dumps(self._valid_qa_output()))
        self.assertEqual(len(parsed["sets"]), 3)

    def test_form_qa_requires_all_three_strategies(self):
        output = self._valid_qa_output()
        output["sets"] = output["sets"][:2]
        with self.assertRaises(er003.QaSchemaError):
            mu.parse_and_validate_form_qa_output(json.dumps(output))

    def test_form_qa_requires_10_items_per_set(self):
        output = self._valid_qa_output()
        output["sets"][0]["items"] = output["sets"][0]["items"][:9]
        with self.assertRaises(er003.QaSchemaError):
            mu.parse_and_validate_form_qa_output(json.dumps(output))

    def test_form_qa_schema_has_no_comparison_or_best_fit_field(self):
        top_props = mu.FORM_QA_JSON_SCHEMA["schema"]["properties"]
        self.assertNotIn("provisional_best_fit", top_props)
        self.assertNotIn("cross_strategy_overlap", top_props)

    def test_form_qa_does_not_rewrite_items(self):
        item_props = set(mu.FORM_QA_ITEM_SCHEMA_PROPERTIES)
        self.assertNotIn("display_phrase", item_props)
        self.assertNotIn("corrected_display_phrase", item_props)

    def test_form_qa_has_no_web_search_tool(self):
        fn = mu.make_form_qa_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_json_response_gate_reused_directly(self):
        self.assertIs(mu.run_json_response_gate, er003.run_json_response_gate)

    def test_form_qa_non_json_raises(self):
        with self.assertRaises(er003.QaSchemaError):
            mu.parse_and_validate_form_qa_output("not json")


class BlindMappingTests(unittest.TestCase):
    """要求(section 15): 記事別固定seedでL/P/UをSet A/B/Cへ割り当てる。
    P2E/P2Fのseedとは異なる。"""

    def test_mapping_covers_all_three_strategies_bijectively(self):
        for article_id in mu.ARTICLE_IDS:
            mapping = mu.build_blind_mapping(article_id)
            self.assertEqual(set(mapping.values()), set(mu.STRATEGY_IDS))

    def test_mapping_deterministic_across_calls(self):
        m1 = mu.build_blind_mapping("A01")
        m2 = mu.build_blind_mapping("A01")
        self.assertEqual(m1, m2)

    def test_three_articles_use_three_distinct_seeds(self):
        seeds = list(mu.BLIND_MAPPING_SEEDS.values())
        self.assertEqual(len(seeds), len(set(seeds)))

    def test_seeds_distinct_from_p2e_and_p2f(self):
        import er003_key_words_research10 as r10
        all_prior_seeds = {p2e.BLIND_MAPPING_SEED} | set(r10.BLIND_MAPPING_SEEDS.values())
        for seed in mu.BLIND_MAPPING_SEEDS.values():
            self.assertNotIn(seed, all_prior_seeds)

    def test_set_labels_are_a_b_c_not_x_y_z(self):
        mapping = mu.build_blind_mapping("A01")
        self.assertEqual(set(mapping.keys()), {"Set A", "Set B", "Set C"})


class ReadingCopyAndMetricsTests(unittest.TestCase):
    """要求(section 18): TOP_5のみ決定的にreading copy生成。研究専用
    metadata。製品参照manifestは変更しない。"""

    def test_reading_copy_generated_deterministically(self):
        items = mu.attach_runtime_metadata({"items": make_items_10()}, "A02", "L")["items"]
        copy1 = mu.build_research_reading_copy(items)
        copy2 = mu.build_research_reading_copy(items)
        self.assertEqual(copy1, copy2)
        self.assertEqual(copy1.count("## Key Words"), 1)

    def test_reading_copy_research_only_metadata_constants(self):
        self.assertEqual(mu.READING_COPY_METADATA["research_only"], "RESEARCH_ONLY_10_ITEMS")
        self.assertEqual(mu.READING_COPY_METADATA["production_spec"], "PRODUCTION_SPEC_REMAINS_5")

    def test_metrics_computed_by_python(self):
        items = mu.attach_runtime_metadata({"items": make_items_10()}, "A02", "L")["items"]
        metrics = mu.compute_min_unit_metrics(items)
        self.assertEqual(metrics["item_count"], 10)
        self.assertEqual(metrics["top5_count"], 5)
        self.assertEqual(metrics["rank_6_10_count"], 5)
        self.assertEqual(sum(metrics["word_count_distribution"].values()), 10)

    def test_module_does_not_write_to_official_reference_manifest(self):
        src = inspect.getsource(mu)
        self.assertNotIn("ER-003-P2C_reference_manifest", src)


class RegressionAndBlindnessGuaranteeTests(unittest.TestCase):
    """要求(section 15-16, 25): モジュール自体がstrategy比較・best fit
    ロジックを持たないことを構造的に確認する(blind性の担保)。"""

    def test_module_has_no_strategy_analysis_function(self):
        # strategy比較・分析用の関数はこのモジュールには存在しない
        # (別スクリプトでユーザー評価後にのみ扱う設計)。
        self.assertFalse(hasattr(mu, "build_strategy_analysis"))
        self.assertFalse(hasattr(mu, "compute_provisional_best_fit"))

    def test_module_does_not_call_tts(self):
        src = inspect.getsource(mu)
        self.assertNotIn("elevenlabs", src.lower())
        self.assertNotIn("text_to_speech", src.lower())

    def test_module_does_not_reference_external_dictionary(self):
        src = inspect.getsource(mu)
        self.assertNotIn("wordnet", src.lower())
        self.assertNotIn("dictionary_api", src.lower())

    def test_validator_never_returns_fixed_or_corrected_items(self):
        result = mu.validate_min_unit_selection(with_metadata(make_items_10()), GOOD_ARTICLE)
        self.assertNotIn("fixed_items", result)
        self.assertNotIn("corrected_items", result)


if __name__ == "__main__":
    unittest.main()
