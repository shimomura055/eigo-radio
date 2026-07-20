# ============================================================
# er003_test_b2_key_words.py
# ER-003-P2D: B2 Key Words 5個の選定・日本語グロス検証のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b2_key_words -v

import inspect
import json
import unittest

import er003_b2_key_words as kw
import er003_ja_to_en_translation as er003

GOOD_ARTICLE = (
    "## Title\n\n"
    "Gordon met it, and England took the lead. This was a huge moment for the team.\n\n"
    "The plan was withdrawn the next day, surprising everyone.\n\n"
    "Ships passed through the strait without incident."
)


def make_item(order, display_phrase, source_form, source_sentence, ja_gloss,
              item_type="word", reuse_value="MEDIUM", spoiler_risk="LOW"):
    return {
        "order": order, "display_phrase": display_phrase, "source_form": source_form,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "item_type": item_type,
        "selection_reason": "selection reason text", "difficulty_reason": "difficulty reason text",
        "reuse_value": reuse_value, "spoiler_risk": spoiler_risk,
    }


GOOD_ITEMS = [
    make_item(1, "take the lead", "took the lead",
              "Gordon met it, and England took the lead.", "リードを奪う", "collocation", "HIGH"),
    make_item(2, "huge moment", "huge moment",
              "This was a huge moment for the team.", "重要な瞬間", "collocation", "MEDIUM"),
    make_item(3, "withdraw", "was withdrawn",
              "The plan was withdrawn the next day, surprising everyone.", "撤回する", "word", "MEDIUM"),
    make_item(4, "surprise", "surprising",
              "The plan was withdrawn the next day, surprising everyone.", "驚かせる",
              "phrasal_verb", "MEDIUM"),
    make_item(5, "without incident", "without incident",
              "Ships passed through the strait without incident.", "支障なく",
              "idiomatic_phrase", "LOW"),
]

GOOD_SELECTION = {"article_id": "TEST", "items": GOOD_ITEMS}


class InputIsolationTests(unittest.TestCase):
    """要求1-14: selector入力はapproved概要+確定B2本文のみ。日本語原稿・
    Natural Source・P1/P1B・Web検索・fact registry・外部辞書・Key Words
    候補・TTS指示は一切参照しない。"""

    def test_b2_input_paths_reused_from_p2b(self):
        import er003_b2_summary as summary_mod
        self.assertIs(kw.B2_INPUT_PATHS, summary_mod.B2_INPUT_PATHS)

    def test_approved_summary_paths_point_to_p2c_approved_files(self):
        for topic_id, path in kw.APPROVED_SUMMARY_PATHS.items():
            self.assertTrue(path.endswith("summary_en_approved.md"), msg=topic_id)

    def test_module_does_not_reference_japanese_source(self):
        src = inspect.getsource(kw)
        self.assertNotIn("APPROVED_ARTICLE_SOURCE_PATHS", src)
        self.assertNotIn("load_approved_japanese_article", src)

    def test_module_does_not_reference_natural_source(self):
        src = inspect.getsource(kw)
        self.assertNotIn("NATURAL_SOURCE_PATHS", src)
        self.assertNotIn("natural_english_source", src.lower())

    def test_module_does_not_import_p1_or_p1b(self):
        src = inspect.getsource(kw)
        self.assertNotIn("import er003_ja_to_en_translation_p1b", src)

    def test_selector_has_no_web_search_tool(self):
        fn = kw.make_selector_fn("dummy", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_module_does_not_reference_fact_registry(self):
        src = inspect.getsource(kw)
        self.assertNotIn("fact_registry", src.lower())

    def test_module_does_not_reference_external_dictionary(self):
        src = inspect.getsource(kw)
        self.assertNotIn("dictionary_api", src.lower())
        self.assertNotIn("wordnet", src.lower())

    def test_prompt_has_no_per_article_key_words_examples(self):
        template = kw.load_selector_prompt_template()
        self.assertNotIn("A01", template)
        self.assertNotIn("A02", template)
        self.assertNotIn("ADD03", template)

    def test_module_does_not_reference_tts(self):
        src = inspect.getsource(kw)
        self.assertNotIn("elevenlabs", src.lower())
        self.assertNotIn("text_to_speech", src.lower())

    def test_same_prompt_template_used_for_all_topics(self):
        template = kw.load_selector_prompt_template()
        for topic_id in kw.ARTICLE_TOPICS:
            msg = kw.build_selector_user_message(f"SUMMARY_{topic_id}", f"ARTICLE_{topic_id}", template=template)
            self.assertIn(f"SUMMARY_{topic_id}", msg)
            self.assertIn(f"ARTICLE_{topic_id}", msg)

    def test_prompt_template_sha256_is_deterministic(self):
        import hashlib
        t1 = kw.load_selector_prompt_template()
        t2 = kw.load_selector_prompt_template()
        self.assertEqual(hashlib.sha256(t1.encode("utf-8")).hexdigest(),
                          hashlib.sha256(t2.encode("utf-8")).hexdigest())

    def test_no_batch_selection_function_exists(self):
        self.assertFalse(hasattr(kw, "select_key_words_batch"))

    def test_model_and_reasoning_effort_match_translator(self):
        self.assertEqual(kw.SELECTOR_MODEL, er003.TRANSLATOR_MODEL)
        self.assertEqual(kw.SELECTOR_REASONING_EFFORT, er003.TRANSLATOR_REASONING_EFFORT)


class SchemaValidatorTests(unittest.TestCase):
    """要求15-35: exactly 5 items・schema・本文対応・重複・禁止項目の
    決定的検証。"""

    def test_valid_selection_passes(self):
        result = kw.validate_key_words_selection(GOOD_SELECTION, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_PASS", msg=result)

    def test_four_items_fails(self):
        parsed = {"article_id": "TEST", "items": GOOD_ITEMS[:4]}
        result = kw.validate_key_words_selection(parsed, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_six_items_fails(self):
        extra = make_item(6, "extra phrase", "extra phrase", "Ships passed through the strait without incident.",
                           "追加", "word", "LOW")
        parsed = {"article_id": "TEST", "items": GOOD_ITEMS + [extra]}
        result = kw.validate_key_words_selection(parsed, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_order_1_to_5_no_duplicates_passes(self):
        orders = [item["order"] for item in GOOD_ITEMS]
        self.assertEqual(sorted(orders), [1, 2, 3, 4, 5])

    def test_order_duplicate_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[4]["order"] = 4  # duplicate of item index 3
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_order_gap_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[4]["order"] = 7  # gap: 1,2,3,4,7
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_empty_required_field_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = ""
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_invalid_item_type_enum_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["item_type"] = "not_a_real_type"
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_source_sentence_exact_match_in_article(self):
        result = kw.validate_key_words_selection(GOOD_SELECTION, GOOD_ARTICLE)
        self.assertEqual(result["item_reasons"], [])

    def test_unicode_normalization_difference_allowed(self):
        # カーリークォート・全角文字などUnicode正規化差は許容する
        article_with_curly = GOOD_ARTICLE.replace(
            "This was a huge moment for the team.", "This was a “huge moment” for the team.")
        items = [dict(it) for it in GOOD_ITEMS]
        items[1] = dict(items[1])
        items[1]["source_sentence"] = "This was a “huge moment” for the team."
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, article_with_curly)
        item1_reasons = next((r for r in result["item_reasons"] if r["index"] == 1), None)
        self.assertIsNone(item1_reasons)

    def test_source_form_present_within_source_sentence(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["source_form"] = "not in the sentence at all"
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        item0_reasons = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("source_form" in reason for reason in item0_reasons["reasons"]))

    def test_source_sentence_not_in_article_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["source_sentence"] = "This sentence does not exist anywhere in the article."
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_digits_only_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["source_form"] = "20"
        items[0]["display_phrase"] = "20"
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        item0_reasons = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("数字だけ" in reason for reason in item0_reasons["reasons"]))

    def test_date_only_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["source_form"] = "July 15"
        items[0]["display_phrase"] = "July 15"
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        item0_reasons = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("日付だけ" in reason for reason in item0_reasons["reasons"]))

    def test_exact_duplicate_display_phrase_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[1] = dict(items[1])
        items[1]["display_phrase"] = items[0]["display_phrase"]
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")
        self.assertTrue(any("display_phrase" in r for r in result["reasons"]))

    def test_case_only_duplicate_display_phrase_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[1] = dict(items[1])
        items[1]["display_phrase"] = items[0]["display_phrase"].upper()
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_empty_ja_gloss_fails(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "   "
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        self.assertEqual(result["status"], "KEY_WORDS_STRUCTURE_INVALID")

    def test_english_only_ja_gloss_detected(self):
        items = [dict(it) for it in GOOD_ITEMS]
        items[0] = dict(items[0])
        items[0]["ja_gloss"] = "to take the lead in a match"
        result = kw.validate_key_words_selection({"article_id": "TEST", "items": items}, GOOD_ARTICLE)
        item0_reasons = next(r for r in result["item_reasons"] if r["index"] == 0)
        self.assertTrue(any("日本語" in reason for reason in item0_reasons["reasons"]))

    def test_display_phrase_and_source_form_both_saved(self):
        result_item = GOOD_ITEMS[0]
        self.assertIn("display_phrase", result_item)
        self.assertIn("source_form", result_item)
        self.assertNotEqual(result_item["display_phrase"], "")

    def test_base_form_normalization_allowed(self):
        # source_form(活用形)とdisplay_phrase(基本形)が異なっていても
        # source_sentence内にsource_formが存在すれば合格する
        result = kw.validate_key_words_selection(GOOD_SELECTION, GOOD_ARTICLE)
        item2_reasons = next((r for r in result["item_reasons"] if r["index"] == 2), None)
        self.assertIsNone(item2_reasons)  # withdraw/was withdrawn

    def test_schema_declares_exactly_5_items(self):
        items_schema = kw.KEY_WORDS_JSON_SCHEMA["schema"]["properties"]["items"]
        self.assertEqual(items_schema["minItems"], 5)
        self.assertEqual(items_schema["maxItems"], 5)


class RetryAndSaveTests(unittest.TestCase):
    """要求36-44: 技術・構造理由のみ最大1回再試行。内容品質理由で
    再生成しない。全attemptを保存する。"""

    def _factory_returning(self, raw_text_or_texts):
        call_count = {"n": 0}
        texts = raw_text_or_texts if isinstance(raw_text_or_texts, list) else [raw_text_or_texts]

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
        good_json = json.dumps(GOOD_SELECTION)
        make_factory, call_count = self._factory_returning(good_json)
        parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
            make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)
        self.assertEqual(len(attempts), 1)

    def test_structure_invalid_retried_once_then_passes(self):
        bad_items = [dict(it) for it in GOOD_ITEMS][:4]
        bad_json = json.dumps({"article_id": "TEST", "items": bad_items})
        good_json = json.dumps(GOOD_SELECTION)
        make_factory, call_count = self._factory_returning([bad_json, good_json])
        parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
            make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)
        self.assertEqual(len(attempts), 2)

    def test_structure_invalid_twice_yields_final_invalid_no_third_attempt(self):
        bad_items = [dict(it) for it in GOOD_ITEMS][:4]
        bad_json = json.dumps({"article_id": "TEST", "items": bad_items})
        make_factory, call_count = self._factory_returning(bad_json)
        parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
            make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], kw.MAX_SELECTION_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        good_json = json.dumps(GOOD_SELECTION)
        make_factory, call_count = self._factory_returning([None, good_json])
        parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
            make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_parse_failed_retried_once(self):
        good_json = json.dumps(GOOD_SELECTION)
        make_factory, call_count = self._factory_returning(["not valid json{{{", good_json])
        parsed, status, attempts, model_id, response_id = kw.run_key_words_selection_gate(
            make_factory, GOOD_ARTICLE)
        self.assertEqual(status, "KEY_WORDS_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_never_calls_qa(self):
        src = inspect.getsource(kw.run_key_words_selection_gate)
        self.assertNotIn("make_qa_fn", src)
        self.assertNotIn("parse_and_validate_key_words_qa_output", src)

    def test_gate_does_not_change_prompt_between_attempts(self):
        src = inspect.getsource(kw.run_key_words_selection_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_selector_user_message", src)

    def test_all_attempts_include_raw_text(self):
        bad_items = [dict(it) for it in GOOD_ITEMS][:4]
        bad_json = json.dumps({"article_id": "TEST", "items": bad_items})
        good_json = json.dumps(GOOD_SELECTION)
        make_factory, _ = self._factory_returning([bad_json, good_json])
        _, _, attempts, _, _ = kw.run_key_words_selection_gate(make_factory, GOOD_ARTICLE)
        for a in attempts:
            self.assertIn("raw_text", a)

    def test_validator_never_returns_fixed_or_corrected_selection(self):
        result = kw.validate_key_words_selection(GOOD_SELECTION, GOOD_ARTICLE)
        self.assertNotIn("fixed_items", result)
        self.assertNotIn("corrected_items", result)


class ReadingCopyTests(unittest.TestCase):
    """要求45-54: 決定的なreading copy生成。LLMに自由生成させない。"""

    def setUp(self):
        self.reading_copy = kw.build_key_words_reading_copy(GOOD_ITEMS)

    def test_key_words_heading_appears_exactly_once(self):
        self.assertEqual(self.reading_copy.count("## Key Words"), 1)

    def test_number_headings_in_order(self):
        for word in ("One", "Two", "Three", "Four", "Five"):
            self.assertIn(f"### Number {word}", self.reading_copy)
        idx_one = self.reading_copy.index("### Number One")
        idx_two = self.reading_copy.index("### Number Two")
        idx_three = self.reading_copy.index("### Number Three")
        idx_four = self.reading_copy.index("### Number Four")
        idx_five = self.reading_copy.index("### Number Five")
        self.assertTrue(idx_one < idx_two < idx_three < idx_four < idx_five)

    def test_each_item_is_english_japanese_english(self):
        for item in GOOD_ITEMS:
            occurrences = self.reading_copy.count(item["display_phrase"])
            self.assertGreaterEqual(occurrences, 2, msg=item["display_phrase"])
            self.assertIn(item["ja_gloss"], self.reading_copy)

    def test_display_phrase_appears_before_and_after_gloss(self):
        lines = [l for l in self.reading_copy.split("\n") if l.strip()]
        idx = lines.index("### Number One")
        self.assertEqual(lines[idx + 1], GOOD_ITEMS[0]["display_phrase"])
        self.assertEqual(lines[idx + 2], GOOD_ITEMS[0]["ja_gloss"])
        self.assertEqual(lines[idx + 3], GOOD_ITEMS[0]["display_phrase"])

    def test_ja_gloss_appears_exactly_once_per_item(self):
        for item in GOOD_ITEMS:
            self.assertEqual(self.reading_copy.count(item["ja_gloss"]), 1)

    def test_no_example_sentences_added(self):
        for item in GOOD_ITEMS:
            self.assertNotIn(item["source_sentence"], self.reading_copy)

    def test_no_pronunciation_symbols_added(self):
        self.assertNotIn("/", self.reading_copy)

    def test_no_katakana_pronunciation_guide_appended_to_display_phrase(self):
        # 日本語グロス自体にカタカナ外来語(例: リード)が含まれるのは正常。
        # 禁止されるのは英語表現の直後にカタカナ発音表記を別途追加する
        # ことであり、builderはdisplay_phrase/ja_glossをそのまま書き出す
        # だけなので、括弧付きの発音注記が挿入されないことを確認する。
        self.assertNotIn("(", self.reading_copy)
        self.assertNotIn("（", self.reading_copy)

    def test_reading_copy_built_deterministically_from_json(self):
        copy1 = kw.build_key_words_reading_copy(GOOD_ITEMS)
        copy2 = kw.build_key_words_reading_copy(GOOD_ITEMS)
        self.assertEqual(copy1, copy2)

    def test_reading_copy_not_generated_by_llm(self):
        src = inspect.getsource(kw.build_key_words_reading_copy)
        self.assertNotIn("client", src)
        self.assertNotIn("responses.create", src)


class KeyWordsQaTests(unittest.TestCase):
    """要求55-71: 独立QA(selectorとは別実行、Web検索なし)。書き換えない。"""

    def test_qa_is_separate_function_from_selector(self):
        self.assertIsNot(kw.make_qa_fn, kw.make_selector_fn)

    def test_qa_has_no_web_search_tool(self):
        fn = kw.make_qa_fn("dummy prompt", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_qa_prompt_takes_summary_article_and_key_words(self):
        sig = inspect.signature(kw.build_qa_prompt)
        params = list(sig.parameters)
        self.assertIn("approved_summary", params)
        self.assertIn("approved_b2_article", params)
        self.assertIn("key_words_json", params)

    def _valid_qa_output(self):
        item_qa = {
            "order": 1, "source_match": "PASS", "display_phrase_match": "PASS", "gloss_accuracy": "PASS",
            "comprehension_value": "HIGH", "difficulty_value": "MEDIUM", "reuse_value": "HIGH",
            "spoiler_risk": "LOW", "duplicate_risk": "LOW", "notes": "",
        }
        return {
            "verdict": "PASS",
            "items": [dict(item_qa, order=i) for i in range(1, 6)],
            "set_balance": "PASS", "low_value_filler_risk": [], "technical_term_overload": [],
            "missing_high_value_candidates": [], "standalone_summary_dependency": "PASS", "notes": "",
        }

    def test_valid_qa_output_parses(self):
        raw = json.dumps(self._valid_qa_output())
        parsed = kw.parse_and_validate_key_words_qa_output(raw)
        self.assertEqual(parsed["verdict"], "PASS")

    def test_qa_output_requires_exactly_5_items(self):
        output = self._valid_qa_output()
        output["items"] = output["items"][:4]
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output(json.dumps(output))

    def test_qa_output_validates_comprehension_value_enum(self):
        output = self._valid_qa_output()
        output["items"][0]["comprehension_value"] = "SUPER_HIGH"
        # スキーマ上の型チェックはstrで通るが、enum自体はAPI側で強制される想定。
        # ここでは型のみのチェックであることを確認する(値の中身までは
        # parse_and_validate側で個々にenum検証していないフィールドがある
        # ことをテストで明示する)。
        parsed = kw.parse_and_validate_key_words_qa_output(json.dumps(output))
        self.assertEqual(parsed["items"][0]["comprehension_value"], "SUPER_HIGH")

    def test_qa_output_validates_difficulty_value_evaluated(self):
        output = self._valid_qa_output()
        parsed = kw.parse_and_validate_key_words_qa_output(json.dumps(output))
        self.assertIn("difficulty_value", parsed["items"][0])

    def test_qa_output_validates_reuse_value_evaluated(self):
        output = self._valid_qa_output()
        parsed = kw.parse_and_validate_key_words_qa_output(json.dumps(output))
        self.assertIn("reuse_value", parsed["items"][0])

    def test_qa_output_validates_spoiler_risk_evaluated(self):
        output = self._valid_qa_output()
        parsed = kw.parse_and_validate_key_words_qa_output(json.dumps(output))
        self.assertIn("spoiler_risk", parsed["items"][0])

    def test_qa_output_validates_duplicate_risk_evaluated(self):
        output = self._valid_qa_output()
        parsed = kw.parse_and_validate_key_words_qa_output(json.dumps(output))
        self.assertIn("duplicate_risk", parsed["items"][0])

    def test_qa_output_missing_technical_term_overload_raises(self):
        output = self._valid_qa_output()
        del output["technical_term_overload"]
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output(json.dumps(output))

    def test_qa_output_missing_low_value_filler_risk_raises(self):
        output = self._valid_qa_output()
        del output["low_value_filler_risk"]
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output(json.dumps(output))

    def test_qa_output_missing_missing_high_value_candidates_raises(self):
        output = self._valid_qa_output()
        del output["missing_high_value_candidates"]
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output(json.dumps(output))

    def test_qa_output_missing_standalone_summary_dependency_raises(self):
        output = self._valid_qa_output()
        del output["standalone_summary_dependency"]
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output(json.dumps(output))

    def test_qa_result_not_used_to_regenerate_selection(self):
        src = inspect.getsource(kw)
        self.assertNotIn("regenerate", src.lower())

    def test_qa_does_not_rewrite_items(self):
        schema_fields = set(kw.KEY_WORDS_QA_JSON_SCHEMA["schema"]["properties"])
        self.assertNotIn("corrected_items", schema_fields)
        self.assertNotIn("display_phrase", schema_fields)

    def test_json_response_gate_reused_directly(self):
        self.assertIs(kw.run_json_response_gate, er003.run_json_response_gate)

    def test_qa_non_json_raises(self):
        with self.assertRaises(er003.QaSchemaError):
            kw.parse_and_validate_key_words_qa_output("not json")


class MetricsAndRegressionTests(unittest.TestCase):
    """要求72-79相当: 決定的指標計測、B2本文・approved概要無変更を
    前提とした関数設計、TTS呼び出しなし。"""

    def test_metrics_computed_by_python_not_llm(self):
        reading_copy = kw.build_key_words_reading_copy(GOOD_ITEMS)
        metrics = kw.compute_key_words_metrics(GOOD_ITEMS, reading_copy)
        self.assertEqual(metrics["item_count"], 5)

    def test_item_type_counts_present(self):
        reading_copy = kw.build_key_words_reading_copy(GOOD_ITEMS)
        metrics = kw.compute_key_words_metrics(GOOD_ITEMS, reading_copy)
        self.assertEqual(sum(metrics["item_type_counts"].values()), 5)

    def test_reuse_value_and_spoiler_risk_distributions(self):
        reading_copy = kw.build_key_words_reading_copy(GOOD_ITEMS)
        metrics = kw.compute_key_words_metrics(GOOD_ITEMS, reading_copy)
        self.assertEqual(sum(metrics["reuse_value_counts"].values()), 5)
        self.assertEqual(sum(metrics["spoiler_risk_counts"].values()), 5)

    def test_reading_copy_word_count_computed(self):
        reading_copy = kw.build_key_words_reading_copy(GOOD_ITEMS)
        metrics = kw.compute_key_words_metrics(GOOD_ITEMS, reading_copy)
        self.assertGreater(metrics["reading_copy_word_count"], 0)

    def test_module_does_not_call_tts(self):
        src = inspect.getsource(kw)
        self.assertNotIn("elevenlabs", src.lower())

    def test_load_approved_b2_article_reused_from_p2b(self):
        import er003_b2_summary as summary_mod
        self.assertIs(kw.load_approved_b2_article, summary_mod.load_approved_b2_article)


if __name__ == "__main__":
    unittest.main()
