# ============================================================
# er003_test_ja_to_en_translation.py
# ER-003-P1: 制約なし自然英訳ベースライン検証のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_ja_to_en_translation -v

import inspect
import json
import os
import unittest

import er002_ja_article_generation as article_gen
import er003_ja_to_en_translation as er003

FORBIDDEN_INPUT_TERMS = [
    "cefr", "b2", "vocabulary list", "word count limit", "sentence length",
    "key words", "単語解説", "日本語概要", "英語概要", "理解問題", "発音",
]


class ApprovedSourceSelectionTests(unittest.TestCase):
    """要求1-4: 翻訳対象は条件Lの承認済み3記事。sha256記録。改変なし。
    citation/URL/QA注記が翻訳元に含まれない。"""

    def test_source_paths_point_to_condition_l_reading_copy(self):
        for topic_id, path in er003.APPROVED_ARTICLE_SOURCE_PATHS.items():
            self.assertIn("condition_l", path)
            self.assertTrue(path.endswith("reading_copy.md"))

    def test_exactly_three_topics(self):
        self.assertEqual(set(er003.APPROVED_ARTICLE_SOURCE_PATHS.keys()), {"A01", "A02", "ADD03"})

    def test_sha256_is_deterministic(self):
        text = "テスト本文"
        self.assertEqual(er003.sha256_text(text), er003.sha256_text(text))
        self.assertEqual(len(er003.sha256_text(text)), 64)

    def test_load_approved_article_matches_file_exactly(self):
        for topic_id, path in er003.APPROVED_ARTICLE_SOURCE_PATHS.items():
            if not os.path.exists(path):
                self.skipTest(f"{path}が見つかりません")
            with open(path, encoding="utf-8") as f:
                expected = f.read()
            self.assertEqual(er003.load_approved_japanese_article(topic_id), expected)

    def test_source_articles_contain_no_url_citation_markers(self):
        for topic_id, path in er003.APPROVED_ARTICLE_SOURCE_PATHS.items():
            if not os.path.exists(path):
                self.skipTest(f"{path}が見つかりません")
            text = er003.load_approved_japanese_article(topic_id)
            self.assertNotIn("https://", text)
            self.assertNotIn("http://", text)


class TranslatorPromptTests(unittest.TestCase):
    """要求5-6, 10-16: promptが凍結文面と一致。3記事で同じテンプレート。
    英語マスター・阪神マスター・fact registry・CEFR・語彙・文長・語数
    制約が一切含まれない。"""

    def test_template_has_only_approved_japanese_article_placeholder(self):
        template = er003.load_translator_prompt_template()
        self.assertIn("{approved_japanese_article}", template)

    def test_build_message_uses_same_template_for_all_topics(self):
        ja_text = "テスト記事本文です。"
        msg1 = er003.build_translator_user_message(ja_text)
        msg2 = er003.build_translator_user_message(ja_text)
        self.assertEqual(msg1, msg2)

    def test_message_signature_takes_only_article_text(self):
        params = list(inspect.signature(er003.build_translator_user_message).parameters)
        self.assertEqual(params[0], "approved_japanese_article")
        self.assertNotIn("english_master", params)
        self.assertNotIn("hanshin_master", params)
        self.assertNotIn("fact_registry", params)

    def test_template_contains_no_forbidden_constraint_terms(self):
        template = er003.load_translator_prompt_template().lower()
        for term in FORBIDDEN_INPUT_TERMS:
            self.assertNotIn(term, template)

    def test_developer_message_is_short_neutral_instruction(self):
        self.assertEqual(er003.TRANSLATOR_DEVELOPER_MESSAGE, "日本語の記事を自然な英語に翻訳してください。")


class TranslatorCallTests(unittest.TestCase):
    """要求7-9, 17-18: 1記事1API実行。複数記事同時翻訳なし。Web検索
    ツールなし。自由Markdown出力。Structured Outputなし。"""

    def test_translator_has_no_web_search_tool(self):
        src = inspect.getsource(er003.make_translator_fn)
        self.assertNotIn('"type": "web_search"', src)
        self.assertNotIn("tools=", src)

    def test_translator_has_no_structured_output(self):
        src = inspect.getsource(er003.make_translator_fn)
        self.assertNotIn('"text":', src)
        self.assertNotIn("text={", src)

    def test_module_has_no_batch_translation_function(self):
        for name in dir(er003):
            self.assertNotIn("batch", name.lower())

    def test_single_translator_call_returns_expected_shape(self):
        calls = []

        class FakeResponse:
            model = er003.TRANSLATOR_MODEL
            id = "resp_test"
            output_text = "# Title\n\nBody."

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return FakeResponse()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        translator_fn = er003.make_translator_fn("user message", client=FakeClient())
        text, model_id, response_id, search_usage, sources = translator_fn()
        self.assertEqual(len(calls), 1)
        self.assertEqual(text, "# Title\n\nBody.")
        self.assertEqual(search_usage["web_search_call_count"], 0)
        self.assertEqual(sources, [])

    def test_model_mismatch_raises_technical_error(self):
        class FakeResponse:
            model = "some-other-model"
            id = "resp_test"
            output_text = "text"

        class FakeResponses:
            def create(self, **kwargs):
                return FakeResponse()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        translator_fn = er003.make_translator_fn("user message", client=FakeClient())
        with self.assertRaises(er003.TranslatorModelMismatchError):
            translator_fn()

    def test_empty_response_raises_technical_error(self):
        class FakeResponse:
            model = er003.TRANSLATOR_MODEL
            id = "resp_test"
            output_text = ""

        class FakeResponses:
            def create(self, **kwargs):
                return FakeResponse()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        translator_fn = er003.make_translator_fn("user message", client=FakeClient())
        with self.assertRaises(Exception):
            translator_fn()


class TechnicalRetryReuseTests(unittest.TestCase):
    """要求19-20: 技術再試行は最大1回。内容品質で再生成しない
    (article_generationの汎用ゲートをそのまま再利用する)。"""

    def test_reuses_article_generation_technical_gate_directly(self):
        self.assertIs(er003.run_translator_technical_gate, article_gen.run_writer_technical_gate)

    def test_technical_gate_never_checks_structure_or_content_quality(self):
        src = inspect.getsource(er003.run_translator_technical_gate)
        self.assertNotIn("validate_point_structure", src)
        self.assertNotIn("fidelity", src.lower())

    def test_max_technical_retry_is_two_attempts_total(self):
        self.assertEqual(article_gen.MAX_TECHNICAL_RETRY_ATTEMPTS, 2)


class EnglishStructureCheckTests(unittest.TestCase):
    """要求21-24: H3見出し数を記録。Point本文の空チェック。一言まとめ
    相当の存在を記録。構造不適合でも自動修正しない。"""

    TWO_POINT_EN = (
        "# A Hook Title\n\nIntro paragraph.\n\n"
        "### First Point\n\nBody of first point.\n\n"
        "### Second Point\n\nBody of second point.\n\n"
        "In one line: this is the closing summary.\n"
    )

    def test_records_h3_heading_count(self):
        result = er003.check_english_structure(self.TWO_POINT_EN)
        self.assertEqual(result["h3_heading_count"], 2)
        self.assertEqual(result["structure_status"], "STRUCTURE_PASS")

    def test_zero_headings_recorded_as_invalid_not_fixed(self):
        result = er003.check_english_structure("# Title\n\nJust a body, no points.\n")
        self.assertEqual(result["structure_status"], "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")

    def test_closing_summary_heuristic_true_when_extra_paragraph_present(self):
        result = er003.check_english_structure(self.TWO_POINT_EN)
        self.assertTrue(result["closing_summary_present_heuristic"])

    def test_closing_summary_heuristic_false_when_no_extra_paragraph(self):
        text = "# T\n\n### P1\n\nBody1.\n\n### P2\n\nBody2."
        result = er003.check_english_structure(text)
        self.assertFalse(result["closing_summary_present_heuristic"])

    def test_check_does_not_mutate_or_return_modified_text(self):
        result = er003.check_english_structure(self.TWO_POINT_EN)
        self.assertNotIn("fixed_text", result)
        self.assertNotIn("corrected_text", result)


class FidelityQaTests(unittest.TestCase):
    """要求25-33: QAはtranslatorと別実行。Web検索なし。意味整合性のみ
    確認。英文を書き換えない。再生成トリガーにならない。スキーマ検証。
    数字/固有名詞/否定・unsupported addition・important omissionを記録。"""

    def test_fidelity_qa_is_separate_function_from_translator(self):
        self.assertIsNot(er003.make_fidelity_qa_fn, er003.make_translator_fn)

    def test_fidelity_qa_has_no_web_search_tool(self):
        src = inspect.getsource(er003.make_fidelity_qa_fn)
        self.assertNotIn('"type": "web_search"', src)
        self.assertNotIn("tools=", src)

    def test_fidelity_qa_prompt_forbids_interest_and_rewriting(self):
        prompt = er003.build_fidelity_qa_prompt("日本語本文", "English text")
        self.assertIn("書き直したり", prompt)
        self.assertIn("一切評価しない", prompt)

    def test_fidelity_qa_uses_structured_output(self):
        src = inspect.getsource(er003.make_fidelity_qa_fn)
        self.assertIn("text={", src)

    def test_valid_json_parses(self):
        payload = json.dumps({
            "verdict": "PASS", "meaning_changes": [], "important_omissions": [],
            "unsupported_additions": [], "number_name_negation_issues": [], "notes": "ok",
        })
        parsed = er003.parse_and_validate_fidelity_qa_output(payload)
        self.assertEqual(parsed["verdict"], "PASS")

    def test_invalid_verdict_raises_schema_error(self):
        payload = json.dumps({
            "verdict": "MAYBE", "meaning_changes": [], "important_omissions": [],
            "unsupported_additions": [], "number_name_negation_issues": [], "notes": "",
        })
        with self.assertRaises(er003.QaSchemaError):
            er003.parse_and_validate_fidelity_qa_output(payload)

    def test_missing_field_raises_schema_error(self):
        payload = json.dumps({"verdict": "PASS", "meaning_changes": []})
        with self.assertRaises(er003.QaSchemaError):
            er003.parse_and_validate_fidelity_qa_output(payload)

    def test_schema_has_number_name_negation_field(self):
        props = er003.FIDELITY_QA_JSON_SCHEMA["schema"]["properties"]
        self.assertIn("number_name_negation_issues", props)

    def test_schema_has_unsupported_additions_field(self):
        props = er003.FIDELITY_QA_JSON_SCHEMA["schema"]["properties"]
        self.assertIn("unsupported_additions", props)

    def test_schema_has_important_omissions_field(self):
        props = er003.FIDELITY_QA_JSON_SCHEMA["schema"]["properties"]
        self.assertIn("important_omissions", props)

    def test_json_response_gate_never_calls_translator(self):
        src = inspect.getsource(er003.run_json_response_gate)
        self.assertNotIn("make_translator_fn", src)
        self.assertNotIn("translator", src.lower())

    def test_json_response_gate_completes_on_first_success(self):
        call_count = {"n": 0}

        def make_fn():
            call_count["n"] += 1

            def fn():
                return json.dumps({
                    "verdict": "PASS", "meaning_changes": [], "important_omissions": [],
                    "unsupported_additions": [], "number_name_negation_issues": [], "notes": "",
                }), "gpt-5.6-sol", "resp1"
            return fn

        parsed, status, attempts, model_id, response_id = er003.run_json_response_gate(
            make_fn, er003.parse_and_validate_fidelity_qa_output)
        self.assertEqual(status, "COMPLETED")
        self.assertEqual(call_count["n"], 1)

    def test_json_response_gate_retries_once_on_parse_failure(self):
        call_count = {"n": 0}

        def make_fn():
            call_count["n"] += 1
            attempt = call_count["n"]

            def fn():
                if attempt == 1:
                    return "broken json{", "gpt-5.6-sol", "resp1"
                return json.dumps({
                    "verdict": "PASS", "meaning_changes": [], "important_omissions": [],
                    "unsupported_additions": [], "number_name_negation_issues": [], "notes": "",
                }), "gpt-5.6-sol", "resp2"
            return fn

        parsed, status, attempts, model_id, response_id = er003.run_json_response_gate(
            make_fn, er003.parse_and_validate_fidelity_qa_output)
        self.assertEqual(status, "COMPLETED")
        self.assertEqual(call_count["n"], 2)

    def test_json_response_gate_never_exceeds_max_attempts(self):
        call_count = {"n": 0}

        def make_fn():
            call_count["n"] += 1

            def fn():
                raise RuntimeError("always fails")
            return fn

        er003.run_json_response_gate(make_fn, er003.parse_and_validate_fidelity_qa_output)
        self.assertLessEqual(call_count["n"], er003.MAX_JSON_RESPONSE_ATTEMPTS)


class DifficultyMetricsTests(unittest.TestCase):
    """要求34-38: 英単語数、文数、平均文長、最長文、推定CEFR、
    推定読み上げ時間(3速度)を計測・保存する。"""

    def test_word_count_basic(self):
        self.assertEqual(er003.compute_word_count("This is a test."), 4)

    def test_word_count_ignores_markdown_symbols_after_strip(self):
        plain = article_gen.strip_markdown_symbols("## **Bold** heading")
        self.assertEqual(er003.compute_word_count(plain), 2)

    def test_sentence_count_and_avg_length(self):
        text = "This is sentence one. This is sentence two, with more words in it."
        metrics = er003.compute_sentence_metrics(text)
        self.assertEqual(metrics["total_sentence_count"], 2)
        self.assertGreater(metrics["avg_words_per_sentence"], 0)

    def test_longest_sentence_word_count(self):
        text = "Short one. This is a much longer sentence with many more words in it."
        metrics = er003.compute_sentence_metrics(text)
        self.assertGreater(metrics["longest_sentence_word_count"], 2)

    def test_reading_times_computed_for_three_speeds(self):
        times = er003.compute_estimated_reading_times(650)
        self.assertEqual(set(times.keys()), {"130_wpm_minutes", "145_wpm_minutes", "160_wpm_minutes"})
        self.assertAlmostEqual(times["130_wpm_minutes"], 5.0, places=1)

    def test_difficulty_schema_has_cefr_field(self):
        props = er003.DIFFICULTY_JSON_SCHEMA["schema"]["properties"]
        self.assertIn("estimated_cefr", props)
        self.assertEqual(set(er003.DIFFICULTY_CEFR_LEVELS), {"A2", "B1", "B1-B2", "B2", "B2-C1", "C1"})

    def test_difficulty_assessment_has_no_web_search_and_does_not_rewrite(self):
        src = inspect.getsource(er003.make_difficulty_assessment_fn)
        self.assertNotIn('"type": "web_search"', src)
        self.assertNotIn("tools=", src)
        prompt = er003.build_difficulty_prompt("Some English text.")
        self.assertIn("書き直したり", prompt)

    def test_valid_difficulty_json_parses(self):
        payload = json.dumps({
            "estimated_cefr": "B2", "cefr_reasoning": "ok",
            "b2_exceeding_expressions": [], "unavoidable_proper_nouns_or_technical_terms": [],
            "complex_clause_examples": [],
        })
        parsed = er003.parse_and_validate_difficulty_output(payload)
        self.assertEqual(parsed["estimated_cefr"], "B2")

    def test_invalid_cefr_value_raises_schema_error(self):
        payload = json.dumps({
            "estimated_cefr": "D5", "cefr_reasoning": "", "b2_exceeding_expressions": [],
            "unavoidable_proper_nouns_or_technical_terms": [], "complex_clause_examples": [],
        })
        with self.assertRaises(er003.QaSchemaError):
            er003.parse_and_validate_difficulty_output(payload)


class SentenceSplitterParagraphAwareTests(unittest.TestCase):
    """ER-003-P2A: 文分割の根本原因修正の回帰テスト。段落境界を保持し、
    カーリークォート・略語・小数点を正しく扱う。"""

    def test_does_not_merge_across_blank_line_paragraphs(self):
        text = "First paragraph with no ending punctuation\n\nSecond paragraph starts here."
        sentences = er003.split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], "First paragraph with no ending punctuation")

    def test_punctuationless_paragraph_is_its_own_unit(self):
        text = "England 1–2 Argentina\n\nAt 39, the captain provided two assists that night."
        sentences = er003.split_sentences(text)
        self.assertEqual(sentences[0], "England 1–2 Argentina")
        self.assertEqual(sentences[1], "At 39, the captain provided two assists that night.")

    def test_splits_after_period_before_closing_curly_quote(self):
        text = 'He said, “This is a test.” Then he left the room.'
        sentences = er003.split_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0].endswith('”'))
        self.assertEqual(sentences[1], "Then he left the room.")

    def test_curly_quote_paragraph_does_not_merge_with_neighbors(self):
        text = (
            "But the results suggest defaults can guide people’s choices.\n\n"
            "“What the UK is trying to switch off is not the glow of the smartphone, "
            "but the endless current of scrolling that carries teenagers right up to bedtime.”\n\n"
            "This midnight speed bump sits somewhere between a strict ban and a complete hands-off approach."
        )
        sentences = er003.split_sentences(text)
        self.assertEqual(len(sentences), 3)
        for s in sentences:
            self.assertLessEqual(er003.compute_word_count(s), 32)

    def test_am_abbreviation_not_split(self):
        sentences = er003.split_sentences("It would run from midnight to 6 a.m. That is late.")
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0].endswith("a.m."))

    def test_pm_abbreviation_not_split(self):
        sentences = er003.split_sentences("Restrictions ran from 9 p.m. to 7 a.m. daily.")
        self.assertEqual(len(sentences), 1)

    def test_us_abbreviation_not_split(self):
        sentences = er003.split_sentences("On July 13, U.S. President Trump made an announcement.")
        self.assertEqual(len(sentences), 1)

    def test_decimal_not_split(self):
        sentences = er003.split_sentences("That is roughly 4.9 billion yen. It matters.")
        self.assertEqual(len(sentences), 2)
        self.assertTrue(sentences[0].endswith("4.9 billion yen."))

    def test_currency_amount_not_split(self):
        sentences = er003.split_sentences("Brent closed at 84 dollars and 73 cents. It rose overnight.")
        self.assertEqual(len(sentences), 2)

    def test_colon_introduced_quote_paragraphs_not_merged(self):
        text = (
            "The message changed overnight from:\n\n"
            "“If you want to pass through, pay 20 percent,”\n\n"
            "to:\n\n"
            "“Invest in the United States instead.”\n\n"
            "Within just 24 hours, everything changed."
        )
        sentences = er003.split_sentences(text)
        self.assertEqual(len(sentences), 5)

    def test_question_mark_splits(self):
        sentences = er003.split_sentences("Did the markets breathe a sigh of relief? Only partly.")
        self.assertEqual(len(sentences), 2)

    def test_exclamation_mark_splits(self):
        sentences = er003.split_sentences("What a game! Nobody expected this.")
        self.assertEqual(len(sentences), 2)

    def test_closing_bracket_after_terminal_mark_recognized(self):
        sentences = er003.split_sentences("This happened (in July). Then this happened.")
        self.assertEqual(len(sentences), 2)

    def test_hyphenated_word_count_unchanged(self):
        self.assertEqual(er003.compute_word_count("digital switch-off period"), 3)

    def test_contraction_word_count_unchanged(self):
        self.assertEqual(er003.compute_word_count("wouldn't couldn't didn't"), 3)

    def test_avg_exactly_19_is_pass_boundary(self):
        sentence = " ".join(["word"] * 19) + "."
        metrics = er003.compute_sentence_metrics(sentence)
        self.assertEqual(metrics["avg_words_per_sentence"], 19.0)

    def test_avg_19_01_is_fail_boundary(self):
        s1 = " ".join(["word"] * 20) + "."
        s2 = " ".join(["word"] * 19) + "."
        metrics = er003.compute_sentence_metrics(f"{s1} {s2}")
        self.assertGreater(metrics["avg_words_per_sentence"], 19.00)

    def test_longest_32_is_pass_boundary(self):
        sentence = " ".join(["word"] * 32) + "."
        metrics = er003.compute_sentence_metrics(sentence)
        self.assertEqual(metrics["longest_sentence_word_count"], 32)

    def test_longest_33_is_fail_boundary(self):
        sentence = " ".join(["word"] * 33) + "."
        metrics = er003.compute_sentence_metrics(sentence)
        self.assertEqual(metrics["longest_sentence_word_count"], 33)


class SavedB2ArticleRecomputeRegressionTests(unittest.TestCase):
    """ER-003-P2A: 保存済みB2版3記事(P2で実際に生成された本文)を、
    修正後のsplit_sentencesで再計測しても、32語超の文が残らないことを
    確認する回帰テスト。APIは一切呼ばない。"""

    def _recompute(self, topic_id):
        import er003_b2_adapter as b2
        path = f"er003_output/p2/{topic_id}/b2_version_raw.md"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        return b2.compute_b2_sentence_metrics(raw)

    def test_a01_recompute_has_no_sentence_over_32(self):
        metrics = self._recompute("A01")
        self.assertEqual(metrics["sentences_over_32_word_count"], 0)

    def test_a02_recompute_has_no_sentence_over_32(self):
        metrics = self._recompute("A02")
        self.assertEqual(metrics["sentences_over_32_word_count"], 0)

    def test_add03_recompute_has_no_sentence_over_32(self):
        metrics = self._recompute("ADD03")
        self.assertEqual(metrics["sentences_over_32_word_count"], 0)

    def test_a01_recompute_passes_both_metrics(self):
        metrics = self._recompute("A01")
        self.assertEqual(metrics["overall_status"], "B2_SENTENCE_METRICS_PASS")

    def test_a02_recompute_passes_both_metrics(self):
        metrics = self._recompute("A02")
        self.assertEqual(metrics["overall_status"], "B2_SENTENCE_METRICS_PASS")

    def test_add03_recompute_passes_both_metrics(self):
        metrics = self._recompute("ADD03")
        self.assertEqual(metrics["overall_status"], "B2_SENTENCE_METRICS_PASS")


class NoOtherApiCallsTests(unittest.TestCase):
    """要求39-40: TTSを呼ばない。Key Words・概要生成をしない。"""

    def test_tts_not_referenced(self):
        with open("er003_ja_to_en_translation.py", encoding="utf-8") as f:
            src = f.read().lower()
        self.assertNotIn("tts", src)

    def test_no_key_words_or_summary_generation(self):
        with open("er003_ja_to_en_translation.py", encoding="utf-8") as f:
            src = f.read()
        forbidden = ["key_words", "KeyWords", "日本語概要", "英語概要", "理解問題"]
        for term in forbidden:
            self.assertNotIn(term, src)


if __name__ == "__main__":
    unittest.main()
