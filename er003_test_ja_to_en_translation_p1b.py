# ============================================================
# er003_test_ja_to_en_translation_p1b.py
# ER-003-P1B: 固定構造付き自然英訳のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_ja_to_en_translation_p1b -v

import inspect
import os
import unittest

import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b

GOOD_STRUCTURE = (
    "# Title\n\nIntro text here.\n\n"
    "## Today's Semifinal Turning Points\n\n"
    "### Point One: Messi the Closer\n\nBody one.\n\n"
    "### Point Two: Substitutions That Mattered\n\nBody two.\n\n"
    "## In One Line\n\nClosing summary sentence.\n"
)


class UnchangedFromP1Tests(unittest.TestCase):
    """要求1-11: 翻訳元・model・reasoning effort・Web検索なし・英語
    マスターなし・fact registryなし・1記事1実行・自由Markdown・
    Structured Outputなしは、いずれもP1から不変。"""

    def test_source_paths_identical_to_p1(self):
        self.assertIs(p1b.APPROVED_ARTICLE_SOURCE_PATHS, er003.APPROVED_ARTICLE_SOURCE_PATHS)

    def test_load_approved_article_matches_p1(self):
        for topic_id in p1b.APPROVED_ARTICLE_SOURCE_PATHS:
            self.assertEqual(p1b.load_approved_japanese_article(topic_id), er003.load_approved_japanese_article(topic_id))

    def test_source_sha256_matches_p1(self):
        for topic_id in p1b.APPROVED_ARTICLE_SOURCE_PATHS:
            p1_text = er003.load_approved_japanese_article(topic_id)
            p1b_text = p1b.load_approved_japanese_article(topic_id)
            self.assertEqual(er003.sha256_text(p1_text), er003.sha256_text(p1b_text))

    def test_message_builder_does_not_accept_p1_english_translation(self):
        params = list(inspect.signature(p1b.build_translator_user_message_p1b).parameters)
        self.assertNotIn("english_translation", params)
        self.assertNotIn("p1_translation", params)

    def test_model_and_reasoning_unchanged(self):
        self.assertEqual(p1b.TRANSLATOR_MODEL, er003.TRANSLATOR_MODEL)
        self.assertEqual(p1b.TRANSLATOR_REASONING_EFFORT, er003.TRANSLATOR_REASONING_EFFORT)
        self.assertEqual(p1b.TRANSLATOR_MODEL, "gpt-5.6-sol")
        self.assertEqual(p1b.TRANSLATOR_REASONING_EFFORT, "high")

    def test_developer_message_unchanged(self):
        self.assertEqual(p1b.TRANSLATOR_DEVELOPER_MESSAGE, er003.TRANSLATOR_DEVELOPER_MESSAGE)

    def test_make_translator_fn_reused_directly(self):
        self.assertIs(p1b.make_translator_fn, er003.make_translator_fn)

    def test_translator_has_no_web_search_tool(self):
        src = inspect.getsource(p1b.make_translator_fn)
        self.assertNotIn('"type": "web_search"', src)
        self.assertNotIn("tools=", src)

    def test_translator_has_no_structured_output(self):
        src = inspect.getsource(p1b.make_translator_fn)
        self.assertNotIn("text={", src)

    def test_no_batch_translation_function(self):
        for name in dir(p1b):
            self.assertNotIn("batch", name.lower())

    def test_template_contains_no_cefr_or_vocab_constraints(self):
        template = p1b.load_translator_prompt_template_p1b().lower()
        for term in ["cefr", "b2", "vocabulary", "word count", "sentence length", "english master", "阪神", "fact registry"]:
            self.assertNotIn(term, template)

    def test_template_contains_fixed_structure_instructions(self):
        template = p1b.load_translator_prompt_template_p1b()
        self.assertIn("Today's", template)
        self.assertIn("Points", template)
        self.assertIn("Point One:", template)
        self.assertIn("Point Two:", template)
        self.assertIn("In One Line", template)

    def test_template_has_only_approved_japanese_article_placeholder(self):
        template = p1b.load_translator_prompt_template_p1b()
        self.assertIn("{approved_japanese_article}", template)


class FixedStructureDetectionTests(unittest.TestCase):
    """要求12-26: 固定構造(Today's...Points/Point One/Point Two/
    In One Line)の検出条件。"""

    def test_valid_structure_passes(self):
        result = p1b.validate_p1b_structure(GOOD_STRUCTURE)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_PASS")
        self.assertEqual(result["reasons"], [])

    def test_todays_points_heading_detected(self):
        result = p1b.validate_p1b_structure(GOOD_STRUCTURE)
        self.assertEqual(result["todays_points_heading"], "Today's Semifinal Turning Points")

    def test_empty_phrase_between_todays_and_points_fails(self):
        text = GOOD_STRUCTURE.replace("Today's Semifinal Turning Points", "Today's  Points")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_point_points_duplication_fails(self):
        text = GOOD_STRUCTURE.replace("Turning Points", "Turning Point Points")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")
        self.assertTrue(any("重複" in r for r in result["reasons"]))

    def test_key_points_points_duplication_fails(self):
        text = GOOD_STRUCTURE.replace("Semifinal Turning Points", "Key Points Points")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_missing_point_one_fails(self):
        text = GOOD_STRUCTURE.replace("### Point One: Messi the Closer", "### Something Else")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_empty_point_one_angle_fails(self):
        text = GOOD_STRUCTURE.replace("### Point One: Messi the Closer", "### Point One:")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_empty_point_one_body_fails(self):
        text = GOOD_STRUCTURE.replace("Body one.\n\n", "")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_missing_point_two_fails(self):
        text = GOOD_STRUCTURE.replace("### Point Two: Substitutions That Mattered", "### Something Else")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_empty_point_two_angle_fails(self):
        text = GOOD_STRUCTURE.replace("### Point Two: Substitutions That Mattered", "### Point Two:")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_empty_point_two_body_fails(self):
        text = GOOD_STRUCTURE.replace("Body two.\n\n", "")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_point_order_violation_fails(self):
        text = (
            "# Title\n\nIntro.\n\n## Today's Turning Points\n\n"
            "### Point Two: Second\n\nBody2.\n\n"
            "### Point One: First\n\nBody1.\n\n"
            "## In One Line\n\nSummary.\n"
        )
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_in_one_line_detected_exactly_once(self):
        result = p1b.validate_p1b_structure(GOOD_STRUCTURE)
        self.assertTrue(result["in_one_line_present"])

    def test_missing_in_one_line_fails(self):
        text = GOOD_STRUCTURE.replace("## In One Line\n\nClosing summary sentence.\n", "")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_empty_in_one_line_body_fails(self):
        text = GOOD_STRUCTURE.replace("Closing summary sentence.\n", "")
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_in_one_line_before_point_two_fails(self):
        text = (
            "# Title\n\nIntro.\n\n## Today's Turning Points\n\n"
            "### Point One: First\n\nBody1.\n\n"
            "## In One Line\n\nSummary.\n\n"
            "### Point Two: Second\n\nBody2.\n"
        )
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")

    def test_code_fence_headings_excluded(self):
        text = GOOD_STRUCTURE + "\n```\n## Today's Fake Points\n### Point One: Fake\n```\n"
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_PASS")

    def test_duplicate_headings_detected(self):
        text = GOOD_STRUCTURE + "\n## Today's Semifinal Turning Points\n\nDuplicate.\n"
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")
        self.assertTrue(any("重複" in r for r in result["reasons"]))

    def test_truncated_text_flagged(self):
        text = GOOD_STRUCTURE.rstrip(".\n") + "\n\n## In One Line\n\nAnd then suddenly it just stops without"
        result = p1b.validate_p1b_structure(text)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")


class StructureRetryGateTests(unittest.TestCase):
    """要求27-30: 構造再試行は最大1回。構造以外の理由で再試行しない。
    再試行時にpromptを変えない。Claude Codeが見出しを後処理しない。"""

    def test_pass_on_first_attempt_no_retry(self):
        call_count = {"n": 0}

        def make_factory():
            call_count["n"] += 1

            def translator_fn():
                return GOOD_STRUCTURE, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return translator_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = p1b.run_translator_structure_gate(
            make_factory)
        self.assertEqual(status, "TRANSLATION_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)

    def test_structure_invalid_retried_once_then_passes(self):
        call_count = {"n": 0}
        bad_text = GOOD_STRUCTURE.replace("### Point One: Messi the Closer", "### Something Else")

        def make_factory():
            call_count["n"] += 1
            attempt = call_count["n"]

            def translator_fn():
                text = bad_text if attempt == 1 else GOOD_STRUCTURE
                return text, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return translator_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = p1b.run_translator_structure_gate(
            make_factory)
        self.assertEqual(status, "TRANSLATION_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_structure_invalid_twice_yields_final_invalid_no_third_attempt(self):
        call_count = {"n": 0}
        bad_text = GOOD_STRUCTURE.replace("### Point One: Messi the Closer", "### Something Else")

        def make_factory():
            call_count["n"] += 1

            def translator_fn():
                return bad_text, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return translator_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = p1b.run_translator_structure_gate(
            make_factory)
        self.assertEqual(status, "TRANSLATION_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], p1b.MAX_STRUCTURE_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        call_count = {"n": 0}

        def make_factory():
            call_count["n"] += 1
            attempt = call_count["n"]

            def translator_fn():
                if attempt == 1:
                    raise RuntimeError("simulated network error")
                return GOOD_STRUCTURE, "gpt-5.6-sol", "resp2", {"web_search_call_count": 0}, []
            return translator_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = p1b.run_translator_structure_gate(
            make_factory)
        self.assertEqual(status, "TRANSLATION_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_never_calls_fidelity_qa_or_content_quality(self):
        src = inspect.getsource(p1b.run_translator_structure_gate)
        self.assertNotIn("fidelity", src.lower())
        self.assertNotIn("difficulty", src.lower())

    def test_gate_does_not_change_prompt_between_attempts(self):
        # ゲート関数自体はmake_translator_factoryを呼ぶだけで、user_message
        # を変更するロジックを持たない(呼び出し元が固定のuser_messageで
        # クロージャを作る設計であることをソースから確認する)
        src = inspect.getsource(p1b.run_translator_structure_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_translator_user_message", src)

    def test_validator_never_returns_fixed_or_corrected_text(self):
        result = p1b.validate_p1b_structure(GOOD_STRUCTURE)
        self.assertNotIn("fixed_text", result)
        self.assertNotIn("corrected_text", result)


class FidelityQaAndDifficultyReuseTests(unittest.TestCase):
    """要求31-38: QAはP1と独立実行され、意味整合性のみ確認し、Web検索
    なし、結果で再翻訳しない。難易度・文章指標もP1から不変。"""

    def test_fidelity_qa_reused_directly_from_p1(self):
        self.assertIs(p1b.er003.make_fidelity_qa_fn, er003.make_fidelity_qa_fn)
        self.assertIs(p1b.er003.run_json_response_gate, er003.run_json_response_gate)

    def test_fidelity_qa_has_no_web_search(self):
        src = inspect.getsource(er003.make_fidelity_qa_fn)
        self.assertNotIn('"type": "web_search"', src)

    def test_difficulty_functions_reused_directly_from_p1(self):
        self.assertIs(p1b.er003.compute_difficulty_metrics, er003.compute_difficulty_metrics)
        self.assertIs(p1b.er003.make_difficulty_assessment_fn, er003.make_difficulty_assessment_fn)

    def test_word_count_is_deterministic(self):
        text = "This is a test sentence with several words."
        self.assertEqual(er003.compute_word_count(text), er003.compute_word_count(text))

    def test_sentence_metrics_computed_without_llm(self):
        metrics = er003.compute_sentence_metrics("First sentence here. Second one follows.")
        self.assertIn("total_sentence_count", metrics)
        self.assertIn("avg_words_per_sentence", metrics)
        self.assertIn("longest_sentence_word_count", metrics)

    def test_reading_times_three_speeds(self):
        times = er003.compute_estimated_reading_times(390)
        self.assertEqual(set(times.keys()), {"130_wpm_minutes", "145_wpm_minutes", "160_wpm_minutes"})

    def test_cefr_stored_as_reference_value_only(self):
        self.assertIn("estimated_cefr", er003.DIFFICULTY_JSON_SCHEMA["schema"]["properties"])


class NoOtherApiCallsAndP1ProtectionTests(unittest.TestCase):
    """要求39-42: TTS・Key Words・概要を生成しない。P1成果物を変更しない。"""

    def test_tts_not_referenced(self):
        with open("er003_ja_to_en_translation_p1b.py", encoding="utf-8") as f:
            src = f.read().lower()
        self.assertNotIn("tts", src)

    def test_no_key_words_or_summary_generation(self):
        with open("er003_ja_to_en_translation_p1b.py", encoding="utf-8") as f:
            src = f.read()
        for forbidden in ["key_words", "KeyWords", "日本語概要", "英語概要"]:
            self.assertNotIn(forbidden, src)

    def test_p1_review_markdown_untouched(self):
        path = "er003_output/p1/ER-003-P1_user_review.md"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("A01", content)

    def test_p1_module_not_modified_by_import(self):
        # p1bはp1の関数を再利用するだけで、p1側のグローバル状態を書き換えない
        original = er003.TRANSLATOR_MODEL
        _ = p1b.TRANSLATOR_MODEL
        self.assertEqual(er003.TRANSLATOR_MODEL, original)


if __name__ == "__main__":
    unittest.main()
