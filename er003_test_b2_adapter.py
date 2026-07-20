# ============================================================
# er003_test_b2_adapter.py
# ER-003-P2 Part B: B2本文調整パイロットのテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b2_adapter -v

import inspect
import json
import os
import unittest

import er003_b2_adapter as b2
import er003_ja_to_en_translation as er003
import er003_ja_to_en_translation_p1b as p1b

GOOD_B2_TEXT = (
    "# Title\n\nIntro text.\n\n"
    "## Today's Turning Points\n\n"
    "### Point One: First angle\n\nShort body one.\n\n"
    "### Point Two: Second angle\n\nShort body two.\n\n"
    "## In One Line\n\nA short closing line.\n"
)


class AdapterInputTests(unittest.TestCase):
    """要求11-16: 入力はNatural English Sourceのみ。日本語原稿・P1/P1B
    raw response・英語マスター・Web検索・fact registryなし。"""

    def test_natural_source_paths_point_to_p1b_approved(self):
        for topic_id, path in b2.NATURAL_SOURCE_PATHS.items():
            self.assertIn("p1b", path)
            self.assertTrue(path.endswith("natural_source_approved.md"))

    def test_build_message_only_takes_natural_source(self):
        params = list(inspect.signature(b2.build_b2_adapter_user_message).parameters)
        self.assertEqual(params[0], "approved_natural_english_source")
        self.assertNotIn("japanese_article", params)
        self.assertNotIn("p1_raw_response", params)
        self.assertNotIn("english_master", params)

    def test_adapter_reuses_translator_fn_directly(self):
        # make_b2_adapter_fnはer003.make_translator_fnの薄いラッパーであり
        # Web検索・Structured Outputに関する実体を再実装していない
        src = inspect.getsource(b2.make_b2_adapter_fn)
        self.assertIn("er003.make_translator_fn", src)

    def test_adapter_has_no_web_search_tool(self):
        src = inspect.getsource(er003.make_translator_fn)
        self.assertNotIn('"type": "web_search"', src)
        self.assertNotIn("tools=", src)

    def test_template_contains_no_word_count_or_keywords_or_tts(self):
        template = b2.load_b2_adapter_prompt_template().lower()
        for term in ["word count limit", "key words", "tts", "summary", "理解問題", "発音"]:
            self.assertNotIn(term, template)


class SingleExecutionTests(unittest.TestCase):
    """要求17-24: 1記事1adapter実行。同一prompt template。model/reasoning
    一致。自由Markdown。Structured Outputなし。固定構造維持。"""

    def test_no_batch_function(self):
        for name in dir(b2):
            self.assertNotIn("batch", name.lower())

    def test_model_and_reasoning_match_translator(self):
        self.assertEqual(b2.B2_ADAPTER_MODEL, er003.TRANSLATOR_MODEL)
        self.assertEqual(b2.B2_ADAPTER_REASONING_EFFORT, er003.TRANSLATOR_REASONING_EFFORT)
        self.assertEqual(b2.B2_ADAPTER_MODEL, "gpt-5.6-sol")
        self.assertEqual(b2.B2_ADAPTER_REASONING_EFFORT, "high")

    def test_developer_message_is_b2_specific(self):
        self.assertIn("B2", b2.B2_ADAPTER_DEVELOPER_MESSAGE)
        self.assertNotEqual(b2.B2_ADAPTER_DEVELOPER_MESSAGE, er003.TRANSLATOR_DEVELOPER_MESSAGE)

    def test_no_structured_output_for_adapter_call(self):
        src = inspect.getsource(er003.make_translator_fn)
        self.assertNotIn("text={", src)

    def test_template_has_fixed_structure_markers(self):
        template = b2.load_b2_adapter_prompt_template()
        self.assertIn("Today's", template)
        self.assertIn("Point One:", template)
        self.assertIn("Point Two:", template)
        self.assertIn("In One Line", template)


class StructureDetectionReuseTests(unittest.TestCase):
    """要求25-31: 固定構造検出(P1Bのvalidatorをそのまま再利用)。
    構造再試行は最大1回。内容・CEFR・文長理由で再生成しない。"""

    def test_validate_b2_structure_is_p1b_validator(self):
        self.assertIs(b2.validate_b2_structure, p1b.validate_p1b_structure)

    def test_run_gate_is_p1b_gate(self):
        self.assertIs(b2.run_b2_adapter_structure_gate, p1b.run_translator_structure_gate)

    def test_good_structure_passes(self):
        result = b2.validate_b2_structure(GOOD_B2_TEXT)
        self.assertEqual(result["status"], "TRANSLATION_STRUCTURE_PASS")

    def test_point_one_and_two_detected(self):
        result = b2.validate_b2_structure(GOOD_B2_TEXT)
        self.assertEqual(result["point_one_heading"], "Point One: First angle")
        self.assertEqual(result["point_two_heading"], "Point Two: Second angle")

    def test_in_one_line_detected(self):
        result = b2.validate_b2_structure(GOOD_B2_TEXT)
        self.assertTrue(result["in_one_line_present"])

    def test_gate_max_attempts_is_two(self):
        self.assertEqual(p1b.MAX_STRUCTURE_RETRY_ATTEMPTS, 2)

    def test_gate_source_does_not_reference_cefr_or_sentence_length(self):
        src = inspect.getsource(p1b.run_translator_structure_gate)
        self.assertNotIn("cefr", src.lower())
        self.assertNotIn("sentence", src.lower())
        self.assertNotIn("fidelity", src.lower())


class DeterministicMetricsTests(unittest.TestCase):
    """要求32-40: Markdown見出しを文長計測から除外。境界値。32語超文数。
    総語数を本文込み・見出し込みで保存。3速度推定。LLMに数えさせない。"""

    def test_headings_excluded_from_avg_calc(self):
        text = "## A Very Long Heading With Many Extra Words In It Today\n\nShort sentence here.\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        # 見出し内の語は平均文長計算(本文のみの文分割)には影響しない
        self.assertEqual(metrics["total_sentence_count"], 1)

    def test_avg_exactly_19_passes(self):
        # 19語ちょうどの文を1つ作る
        sentence = " ".join(["word"] * 19) + "."
        text = f"# T\n\n{sentence}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertEqual(metrics["avg_words_per_sentence"], 19.0)
        self.assertEqual(metrics["avg_words_per_sentence_status"], "PASS")

    def test_avg_19_01_fails(self):
        # 2文で平均19.01語相当を作る(38語/2文=19.0にならないよう調整)
        s1 = " ".join(["word"] * 20) + "."
        s2 = " ".join(["word"] * 19) + "."
        text = f"# T\n\n{s1} {s2}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertGreater(metrics["avg_words_per_sentence"], 19.00)
        self.assertEqual(metrics["avg_words_per_sentence_status"], "FAIL")

    def test_longest_32_passes(self):
        sentence = " ".join(["word"] * 32) + "."
        text = f"# T\n\n{sentence}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertEqual(metrics["longest_sentence_word_count"], 32)
        self.assertEqual(metrics["longest_sentence_status"], "PASS")

    def test_longest_33_fails(self):
        sentence = " ".join(["word"] * 33) + "."
        text = f"# T\n\n{sentence}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertEqual(metrics["longest_sentence_word_count"], 33)
        self.assertEqual(metrics["longest_sentence_status"], "FAIL")

    def test_sentences_over_32_counted(self):
        long_sentence = " ".join(["word"] * 40) + "."
        short_sentence = "Short one here."
        text = f"# T\n\n{long_sentence} {short_sentence}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertEqual(metrics["sentences_over_32_word_count"], 1)

    def test_word_count_with_and_without_headings_both_saved(self):
        metrics = b2.compute_b2_sentence_metrics(GOOD_B2_TEXT)
        self.assertIn("total_word_count_including_headings", metrics)
        self.assertIn("total_word_count_body_only", metrics)
        self.assertGreaterEqual(
            metrics["total_word_count_including_headings"], metrics["total_word_count_body_only"])

    def test_reading_times_three_speeds(self):
        metrics = b2.compute_b2_sentence_metrics(GOOD_B2_TEXT)
        self.assertEqual(
            set(metrics["estimated_reading_time_minutes"].keys()),
            {"130_wpm_minutes", "145_wpm_minutes", "160_wpm_minutes"})

    def test_metrics_use_er003_deterministic_functions(self):
        src = inspect.getsource(b2.compute_b2_sentence_metrics)
        self.assertIn("er003.compute_word_count", src)
        self.assertIn("er003.split_sentences", src)

    def test_overall_status_fail_when_either_metric_fails(self):
        sentence = " ".join(["word"] * 40) + "."
        text = f"# T\n\n{sentence}\n"
        metrics = b2.compute_b2_sentence_metrics(text)
        self.assertEqual(metrics["overall_status"], "B2_SENTENCE_METRICS_FAIL")


class B2FidelityQaTests(unittest.TestCase):
    """要求41-46: 整合性QAはadapterと別実行。日本語・Natural Source・
    B2版を渡す。Web検索なし。因果関係変化・重要脱落・追加を検出。
    QA結果で再生成しない。"""

    def test_fidelity_qa_separate_from_adapter(self):
        self.assertIsNot(b2.make_b2_fidelity_qa_fn, b2.make_b2_adapter_fn)

    def test_fidelity_prompt_takes_three_inputs(self):
        params = list(inspect.signature(b2.build_b2_fidelity_qa_prompt).parameters)
        self.assertIn("japanese_article", params)
        self.assertIn("natural_english_source", params)
        self.assertIn("b2_version", params)

    def test_fidelity_qa_has_no_web_search(self):
        src = inspect.getsource(b2.make_b2_fidelity_qa_fn)
        self.assertNotIn('"type": "web_search"', src)

    def test_fidelity_schema_has_causality_and_angle_fields(self):
        props = b2.B2_FIDELITY_QA_JSON_SCHEMA["schema"]["properties"]
        self.assertIn("causality_changes", props)
        self.assertIn("angle_preservation_notes", props)
        self.assertIn("in_one_line_preservation_notes", props)

    def test_valid_fidelity_json_parses(self):
        payload = json.dumps({
            "verdict": "PASS", "meaning_changes": [], "important_omissions": [], "unsupported_additions": [],
            "number_name_negation_issues": [], "causality_changes": [], "angle_preservation_notes": [],
            "in_one_line_preservation_notes": [], "notes": "ok",
        })
        parsed = b2.parse_and_validate_b2_fidelity_qa_output(payload)
        self.assertEqual(parsed["verdict"], "PASS")

    def test_invalid_fidelity_verdict_raises(self):
        payload = json.dumps({
            "verdict": "MAYBE", "meaning_changes": [], "important_omissions": [], "unsupported_additions": [],
            "number_name_negation_issues": [], "causality_changes": [], "angle_preservation_notes": [],
            "in_one_line_preservation_notes": [], "notes": "",
        })
        with self.assertRaises(er003.QaSchemaError):
            b2.parse_and_validate_b2_fidelity_qa_output(payload)

    def test_gate_never_calls_adapter_again(self):
        src = inspect.getsource(b2.run_json_response_gate)
        self.assertNotIn("make_b2_adapter_fn", src)
        self.assertNotIn("adapter", src.lower())


class B2DifficultyQaTests(unittest.TestCase):
    """要求47-51: 難易度QAは別実行。above-B2候補保存。必要専門語区別。
    過度な単純化記録。CEFRは確定値として扱わない。"""

    def test_difficulty_qa_separate_execution(self):
        self.assertIsNot(b2.make_b2_difficulty_qa_fn, b2.make_b2_adapter_fn)
        self.assertIsNot(b2.make_b2_difficulty_qa_fn, b2.make_b2_fidelity_qa_fn)

    def test_difficulty_schema_has_required_fields(self):
        props = b2.B2_DIFFICULTY_JSON_SCHEMA["schema"]["properties"]
        for field in ["above_b2_candidates", "essential_technical_terms", "over_simplification_notes",
                      "information_density_notes", "estimated_cefr"]:
            self.assertIn(field, props)

    def test_valid_difficulty_json_parses(self):
        payload = json.dumps({
            "verdict": "PASS", "estimated_cefr": "B2", "above_b2_candidates": [], "essential_technical_terms": [],
            "complex_sentence_notes": [], "information_density_notes": [], "over_simplification_notes": [], "notes": "ok",
        })
        parsed = b2.parse_and_validate_b2_difficulty_output(payload)
        self.assertEqual(parsed["estimated_cefr"], "B2")

    def test_invalid_cefr_raises(self):
        payload = json.dumps({
            "verdict": "PASS", "estimated_cefr": "Z9", "above_b2_candidates": [], "essential_technical_terms": [],
            "complex_sentence_notes": [], "information_density_notes": [], "over_simplification_notes": [], "notes": "",
        })
        with self.assertRaises(er003.QaSchemaError):
            b2.parse_and_validate_b2_difficulty_output(payload)

    def test_cefr_levels_match_er003(self):
        self.assertEqual(set(b2.B2_DIFFICULTY_CEFR_LEVELS), set(er003.DIFFICULTY_CEFR_LEVELS))


class RegressionAndArtifactProtectionTests(unittest.TestCase):
    """要求52-56: P1・P1B成果物を変更しない。TTS/Key Words/概要なし。"""

    def test_tts_not_referenced(self):
        with open("er003_b2_adapter.py", encoding="utf-8") as f:
            src = f.read().lower()
        self.assertNotIn("tts", src)

    def test_no_key_words_or_summary_generation(self):
        with open("er003_b2_adapter.py", encoding="utf-8") as f:
            src = f.read()
        for forbidden in ["key_words", "KeyWords", "日本語概要", "英語概要"]:
            self.assertNotIn(forbidden, src)

    def test_p1b_review_untouched(self):
        path = "er003_output/p1b/ER-003-P1B_user_review.md"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("A01", content)


if __name__ == "__main__":
    unittest.main()
