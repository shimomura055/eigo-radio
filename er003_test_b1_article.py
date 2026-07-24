# ============================================================
# er003_test_b1_article.py
# ER-003-B1-P1: A01 B1本文の初回プロトタイプ生成のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_article -v

import shutil
import tempfile
import unittest
from pathlib import Path

import er002_ja_article_generation as article_gen
import er003_b1_article as b1
import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b

GOOD_B1_TEXT = (
    "# Title\n\n"
    "This is the introduction. It sets up the story in short sentences.\n\n"
    "## Today's Match Points\n\n"
    "### Point One: A Simple Angle\n\n"
    "This is the body of point one. It has more than one sentence here.\n\n"
    "### Point Two: Another Angle\n\n"
    "This is the body of point two. It also has more than one sentence.\n\n"
    "## In One Line\n\n"
    "This is the short closing line that wraps up the story."
)


class MasterExportTests(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_ja_and_en_master_paths_reuse_existing_approved_sources(self):
        self.assertEqual(b1.JAPANESE_MASTER_PATH, er003.APPROVED_ARTICLE_SOURCE_PATHS["A01"])
        self.assertEqual(b1.NATURAL_ENGLISH_SOURCE_PATH, "er003_output/p1b/A01/natural_source_approved.md")

    def test_export_writes_byte_for_byte_identical_copies(self):
        ja_text = "日本語マスター本文\n\nテスト用。"
        en_text = "# Title\n\nNatural English Source body.\n"
        result = b1.export_master_files(self.tmp_dir, japanese_master=ja_text, natural_english_source=en_text)

        with open(result["japanese_master"]["output_path"], encoding="utf-8") as f:
            self.assertEqual(f.read(), ja_text)
        with open(result["natural_english_source"]["output_path"], encoding="utf-8") as f:
            self.assertEqual(f.read(), en_text)

    def test_export_records_source_path_and_sha256(self):
        ja_text = "テスト日本語"
        en_text = "Test English"
        result = b1.export_master_files(self.tmp_dir, japanese_master=ja_text, natural_english_source=en_text)

        self.assertEqual(result["japanese_master"]["source_path"], b1.JAPANESE_MASTER_PATH)
        self.assertEqual(result["japanese_master"]["sha256"], b1.sha256_text(ja_text))
        self.assertEqual(result["natural_english_source"]["source_path"], b1.NATURAL_ENGLISH_SOURCE_PATH)
        self.assertEqual(result["natural_english_source"]["sha256"], b1.sha256_text(en_text))

    def test_real_approved_sources_load_without_error(self):
        ja = b1.load_japanese_master()
        en = b1.load_natural_english_source()
        self.assertTrue(ja.strip())
        self.assertTrue(en.strip())
        self.assertIn("Argentina", en)


class PromptBuilderTests(unittest.TestCase):

    def test_template_loads_and_contains_required_instructions(self):
        template = b1.load_b1_prompt_template()
        self.assertIn("B1-level", template)
        self.assertIn("15 words", template)
        self.assertIn("24 words", template)
        self.assertIn("In One Line", template)
        self.assertIn("{approved_natural_english_source}", template)

    def test_prompt_never_mentions_b2_or_japanese_source(self):
        """B2本文・日本語原稿をprompt生成入力へ含めないことの直接検証。
        プレースホルダーがNatural English Source専用の1つしかない。"""
        import re
        template = b1.load_b1_prompt_template()
        self.assertNotIn("{approved_japanese_article}", template)
        self.assertNotIn("{approved_b2", template)
        placeholders = set(re.findall(r"\{approved_[a-z_]+\}", template))
        self.assertEqual(placeholders, {"{approved_natural_english_source}"})

    def test_build_user_message_substitutes_source_only(self):
        msg = b1.build_b1_user_message("SOURCE_TEXT_MARKER")
        self.assertIn("SOURCE_TEXT_MARKER", msg)
        self.assertNotIn("{approved_natural_english_source}", msg)

    def test_build_user_message_does_not_leak_between_calls(self):
        msg1 = b1.build_b1_user_message("FIRST_ARTICLE")
        msg2 = b1.build_b1_user_message("SECOND_ARTICLE")
        self.assertIn("FIRST_ARTICLE", msg1)
        self.assertNotIn("SECOND_ARTICLE", msg1)
        self.assertIn("SECOND_ARTICLE", msg2)
        self.assertNotIn("FIRST_ARTICLE", msg2)


class GeneratorFunctionTests(unittest.TestCase):

    def test_reuses_p1_translator_model_and_reasoning_effort(self):
        self.assertEqual(b1.B1_MODEL, er003.TRANSLATOR_MODEL)
        self.assertEqual(b1.B1_REASONING_EFFORT, er003.TRANSLATOR_REASONING_EFFORT)

    def test_developer_message_is_b1_specific_and_short(self):
        self.assertEqual(b1.B1_DEVELOPER_MESSAGE,
                         "Write a natural English news article for B1-level learners.")

    def test_generator_fn_has_no_web_search_and_no_structured_output(self):
        fn = b1.make_b1_generator_fn("dummy user message", client=object())
        self.assertFalse(fn.uses_web_search_tool)
        self.assertFalse(fn.response_format_used)
        self.assertEqual(fn.model, b1.B1_MODEL)
        self.assertEqual(fn.reasoning_effort, b1.B1_REASONING_EFFORT)
        self.assertEqual(fn.developer_message, b1.B1_DEVELOPER_MESSAGE)

    def test_module_has_no_retry_gate_function(self):
        """自動再生成しない(section 5)ことの構造的な保証: モジュール内に
        gate/retry相当の関数が存在しない。"""
        for name in dir(b1):
            self.assertNotIn("gate", name.lower(), msg=name)
            self.assertNotIn("retry", name.lower(), msg=name)

    def test_fake_client_success_path(self):
        class FakeResponse:
            model = b1.B1_MODEL
            output_text = GOOD_B1_TEXT
            id = "resp_fake_1"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        fn = b1.make_b1_generator_fn("dummy", client=FakeClient())
        text, model_id, response_id, search_usage, sources = fn()
        self.assertEqual(text, GOOD_B1_TEXT)
        self.assertEqual(model_id, b1.B1_MODEL)
        self.assertEqual(response_id, "resp_fake_1")
        self.assertEqual(search_usage["web_search_call_count"], 0)
        self.assertEqual(sources, [])

    def test_fake_client_empty_response_raises(self):
        class FakeResponse:
            model = b1.B1_MODEL
            output_text = ""
            id = "resp_fake_2"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        fn = b1.make_b1_generator_fn("dummy", client=FakeClient())
        with self.assertRaises(er003.restore.GenerationEmptyOrBrokenError):
            fn()

    def test_fake_client_model_mismatch_raises(self):
        class FakeResponse:
            model = "some-other-model"
            output_text = GOOD_B1_TEXT
            id = "resp_fake_3"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    return FakeResponse()

        fn = b1.make_b1_generator_fn("dummy", client=FakeClient())
        with self.assertRaises(er003.TranslatorModelMismatchError):
            fn()


class StructureCheckReuseTests(unittest.TestCase):

    def test_check_b1_structure_is_p1b_validator(self):
        self.assertIs(b1.check_b1_structure, p1b.validate_p1b_structure)

    def test_good_text_passes_structure_check(self):
        result = b1.check_b1_structure(GOOD_B1_TEXT)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_PASS")
        self.assertTrue(result["in_one_line_present"])

    def test_missing_point_two_fails_structure_check(self):
        broken = GOOD_B1_TEXT.replace("### Point Two: Another Angle\n\n"
                                      "This is the body of point two. It also has more than one sentence.\n\n", "")
        result = b1.check_b1_structure(broken)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_INVALID")
        self.assertTrue(any("Point Two" in r for r in result["reasons"]))


class SentenceMetricsTests(unittest.TestCase):

    def test_strip_heading_lines_reused_from_b2_adapter(self):
        self.assertIs(b1.strip_heading_lines, b2.strip_heading_lines)

    def test_metrics_on_good_text_produce_reasonable_values(self):
        metrics = b1.compute_b1_sentence_metrics(GOOD_B1_TEXT)
        self.assertGreater(metrics["total_word_count_including_headings"], 0)
        self.assertGreater(metrics["total_sentence_count"], 0)
        self.assertEqual(metrics["max_sentence_word_count_ceiling"], 24)
        self.assertEqual(metrics["avg_words_per_sentence_target"], 15.0)
        self.assertIsInstance(metrics["avg_words_per_sentence_within_target"], bool)

    def test_no_hard_total_word_count_limit_field(self):
        """section 4: 総語数のhard limitは設けない。metrics内にhard
        limit相当の合否フィールドが無いことを確認する。"""
        metrics = b1.compute_b1_sentence_metrics(GOOD_B1_TEXT)
        for key in metrics:
            self.assertNotIn("total_word_count_status", key)
            self.assertNotIn("total_word_count_limit", key)

    def test_sentence_over_24_words_detected(self):
        long_sentence = " ".join(["word"] * 30) + "."
        text = f"# Title\n\nIntro.\n\n## Today's Test Points\n\n### Point One: A\n\n{long_sentence}\n\n" \
              f"### Point Two: B\n\nShort body.\n\n## In One Line\n\nShort closer."
        metrics = b1.compute_b1_sentence_metrics(text)
        self.assertGreaterEqual(metrics["sentences_over_24_word_count"], 1)
        self.assertTrue(any(item["word_count"] > 24 for item in metrics["sentences_over_24"]))

    def test_short_sentences_produce_zero_over_24(self):
        metrics = b1.compute_b1_sentence_metrics(GOOD_B1_TEXT)
        self.assertEqual(metrics["sentences_over_24_word_count"], 0)

    def test_estimated_reading_time_reused(self):
        metrics = b1.compute_b1_sentence_metrics(GOOD_B1_TEXT)
        self.assertIn("estimated_reading_time_minutes", metrics)
        self.assertIsInstance(metrics["estimated_reading_time_minutes"], dict)


class MachineChecksTests(unittest.TestCase):

    def _structure_and_metrics(self, text):
        return b1.check_b1_structure(text), b1.compute_b1_sentence_metrics(text)

    def test_good_text_passes_all_checks(self):
        structure, metrics = self._structure_and_metrics(GOOD_B1_TEXT)
        result = b1.run_machine_checks(GOOD_B1_TEXT, structure, metrics, uses_web_search_tool=False)
        self.assertEqual(result["status"], "ALL_CHECKS_PASS")
        self.assertTrue(all(result["checks"].values()))

    def test_empty_text_fails_multiple_checks(self):
        structure, metrics = self._structure_and_metrics("")
        result = b1.run_machine_checks("", structure, metrics, uses_web_search_tool=False)
        self.assertEqual(result["status"], "SOME_CHECKS_FAILED")
        self.assertFalse(result["checks"]["api_response_not_empty"])
        self.assertFalse(result["checks"]["markdown_structure_present"])

    def test_web_search_used_fails_check(self):
        structure, metrics = self._structure_and_metrics(GOOD_B1_TEXT)
        result = b1.run_machine_checks(GOOD_B1_TEXT, structure, metrics, uses_web_search_tool=True)
        self.assertFalse(result["checks"]["web_search_not_used"])
        self.assertEqual(result["status"], "SOME_CHECKS_FAILED")

    def test_missing_in_one_line_fails_check(self):
        broken = GOOD_B1_TEXT.replace("## In One Line\n\nThis is the short closing line that wraps up the story.", "")
        structure, metrics = self._structure_and_metrics(broken)
        result = b1.run_machine_checks(broken, structure, metrics, uses_web_search_tool=False)
        self.assertFalse(result["checks"]["in_one_line_present"])

    def test_b2_body_not_used_flag_is_structural_constant(self):
        structure, metrics = self._structure_and_metrics(GOOD_B1_TEXT)
        result = b1.run_machine_checks(GOOD_B1_TEXT, structure, metrics, uses_web_search_tool=False)
        self.assertTrue(result["checks"]["b2_body_not_used_as_input"])

    def test_metrics_failure_does_not_indicate_check_failure(self):
        """平均15語超・最大24語超であっても機械チェック自体はfailしない
        (section 8: 再生成しない、記録するだけ)。"""
        long_sentence = " ".join(["word"] * 30) + "."
        text = f"# Title\n\nIntro.\n\n## Today's Test Points\n\n### Point One: A\n\n{long_sentence}\n\n" \
              f"### Point Two: B\n\nShort body.\n\n## In One Line\n\nShort closer."
        structure, metrics = self._structure_and_metrics(text)
        result = b1.run_machine_checks(text, structure, metrics, uses_web_search_tool=False)
        # sentence_length_measurableはTrueのまま(文長が測れている、という
        # 意味のチェックであり、閾値超過そのものはチェック対象ではない)
        self.assertTrue(result["checks"]["sentence_length_measurable"])


class InputIsolationTests(unittest.TestCase):
    """B2本文をB1生成へ一切渡さないことの構造的な保証。"""

    def test_module_has_no_reference_to_b2_body_paths(self):
        import inspect
        source = inspect.getsource(b1)
        self.assertNotIn("b2_version_raw", source)
        self.assertNotIn("B2_INPUT_PATHS", source)

    def test_only_one_topic_id_defined(self):
        self.assertEqual(b1.TOPIC_ID, "A01")


if __name__ == "__main__":
    unittest.main()
