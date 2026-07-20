# ============================================================
# er003_test_b2_summary.py
# ER-003-P2B: 「Before You Listen」概要パイロットのテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてモック・既存成果物の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b2_summary -v

import hashlib
import inspect
import json
import os
import unittest

import er003_b2_summary as s
import er003_ja_to_en_translation as er003


def make_body(sentence_word_counts, word="word"):
    """各要素をそのままの語数を持つ1文とし、段落(空行区切り)として
    連結する(section 8のBefore You Listen固定構造と同じ配置)。ER-003-
    P2Cの第一文開始要件を満たすため、先頭文は'We'll look at'(3語)で
    始め、残りをpadding語で埋めて指定語数ちょうどにする。"""
    sentences = []
    for i, n in enumerate(sentence_word_counts):
        if i == 0:
            pad = n - 3
            sentences.append("We'll look at " + " ".join([word] * pad) + "." if pad > 0 else "We'll look at.")
        else:
            sentences.append(" ".join([word] * n) + ".")
    return "## Before You Listen\n\n" + "\n\n".join(sentences)


GOOD_SUMMARY = make_body([13, 12])  # 25語、2文(境界値ちょうど)
GOOD_SUMMARY_3_SENTENCES = make_body([10, 10, 10])  # 30語、3文


class InputIsolationTests(unittest.TestCase):
    """要求6-19: 入力は確定済みB2 reading copyのみ。日本語原稿・Natural
    English Source・P1/P1B・Web検索・fact registry・Key Words・TTSは
    一切参照しない。"""

    def test_input_paths_point_only_to_p2_b2_reading_copy(self):
        for topic_id, path in s.B2_INPUT_PATHS.items():
            self.assertIn("er003_output/p2/", path)
            self.assertTrue(path.endswith("b2_version_raw.md"))

    def test_module_does_not_reference_japanese_source(self):
        src = inspect.getsource(s)
        self.assertNotIn("APPROVED_ARTICLE_SOURCE_PATHS", src)
        self.assertNotIn("load_approved_japanese_article", src)

    def test_module_does_not_reference_natural_source(self):
        src = inspect.getsource(s)
        self.assertNotIn("NATURAL_SOURCE_PATHS", src)
        self.assertNotIn("natural_english_source", src.lower())

    def test_module_does_not_import_p1b(self):
        self.assertNotIn("er003_ja_to_en_translation_p1b", s.__dict__)
        src = inspect.getsource(s)
        self.assertNotIn("import er003_ja_to_en_translation_p1b", src)

    def test_generator_has_no_web_search_tool(self):
        fn = s.make_summary_generator_fn("dummy user message", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_module_does_not_reference_fact_registry(self):
        src = inspect.getsource(s)
        self.assertNotIn("fact_registry", src.lower())

    def test_module_does_not_reference_key_words(self):
        src = inspect.getsource(s)
        self.assertNotIn("key_word", src.lower())

    def test_same_prompt_template_used_for_all_topics(self):
        template = s.load_summary_prompt_template()
        for topic_id in s.ARTICLE_TOPICS:
            msg = s.build_summary_user_message(f"ARTICLE_{topic_id}", template=template)
            self.assertIn(f"ARTICLE_{topic_id}", msg)
            self.assertNotIn("{approved_b2_article}", msg)

    def test_prompt_template_sha256_is_deterministic(self):
        t1 = s.load_summary_prompt_template()
        t2 = s.load_summary_prompt_template()
        self.assertEqual(hashlib.sha256(t1.encode("utf-8")).hexdigest(),
                          hashlib.sha256(t2.encode("utf-8")).hexdigest())

    def test_no_batch_generation_function_exists(self):
        self.assertFalse(hasattr(s, "generate_summaries_batch"))
        self.assertFalse(hasattr(s, "make_summary_generator_batch_fn"))

    def test_model_and_reasoning_effort_match_translator(self):
        self.assertEqual(s.SUMMARY_MODEL, er003.TRANSLATOR_MODEL)
        self.assertEqual(s.SUMMARY_REASONING_EFFORT, er003.TRANSLATOR_REASONING_EFFORT)

    def test_generator_uses_free_markdown_not_structured_output(self):
        fn = s.make_summary_generator_fn("dummy user message", client=object())
        self.assertFalse(fn.response_format_used)

    def test_generator_reuses_translator_fn_directly(self):
        # make_translator_fnをそのまま呼び出すだけの薄いラッパーであることを
        # ソースから確認する(独自のAPI呼び出しロジックを再実装していない)。
        src = inspect.getsource(s.make_summary_generator_fn)
        self.assertIn("er003.make_translator_fn", src)


class StructureLengthGateTests(unittest.TestCase):
    """要求20-37: 固定見出し・語数(25-35)・文数(2-3)を検証する。"""

    def test_valid_structure_passes(self):
        result = s.validate_summary_structure(GOOD_SUMMARY)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS")
        self.assertEqual(result["reasons"], [])

    def test_heading_detected_exactly_once(self):
        result = s.validate_summary_structure(GOOD_SUMMARY)
        self.assertTrue(result["heading_present"])

    def test_heading_wording_must_match_exactly(self):
        for bad_heading in ("## Before Listening", "## Before We Listen", "## Before the Story",
                             "## Quick Preview", "## Summary", "## before you listen"):
            text = GOOD_SUMMARY.replace("## Before You Listen", bad_heading)
            result = s.validate_summary_structure(text)
            self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID", msg=bad_heading)

    def test_other_heading_present_fails(self):
        text = GOOD_SUMMARY + "\n\n## Extra Heading\n\nMore text."
        result = s.validate_summary_structure(text)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_empty_body_fails(self):
        result = s.validate_summary_structure("## Before You Listen\n\n")
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")
        self.assertIn("概要本文が空", result["reasons"])

    def test_24_words_fails(self):
        result = s.validate_summary_structure(make_body([12, 12]))
        self.assertEqual(result["word_count"], 24)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_25_words_passes(self):
        result = s.validate_summary_structure(make_body([13, 12]))
        self.assertEqual(result["word_count"], 25)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS")

    def test_35_words_passes(self):
        result = s.validate_summary_structure(make_body([18, 17]))
        self.assertEqual(result["word_count"], 35)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS")

    def test_36_words_fails(self):
        result = s.validate_summary_structure(make_body([18, 18]))
        self.assertEqual(result["word_count"], 36)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_1_sentence_fails(self):
        result = s.validate_summary_structure(make_body([30]))
        self.assertEqual(result["sentence_count"], 1)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_2_sentences_passes(self):
        result = s.validate_summary_structure(make_body([13, 12]))
        self.assertEqual(result["sentence_count"], 2)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS")

    def test_3_sentences_passes(self):
        result = s.validate_summary_structure(make_body([10, 10, 10]))
        self.assertEqual(result["sentence_count"], 3)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_PASS")

    def test_4_sentences_fails(self):
        result = s.validate_summary_structure(make_body([7, 7, 7, 7]))
        self.assertEqual(result["sentence_count"], 4)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_non_english_text_mixed_in_detected(self):
        text = "## Before You Listen\n\nThis is about a match. これは日本語です。"
        result = s.validate_summary_structure(text)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")
        self.assertTrue(any("日本語" in r for r in result["reasons"]))

    def test_code_fence_fails(self):
        text = "## Before You Listen\n\n```\ncode\n```"
        result = s.validate_summary_structure(text)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_bullet_list_fails(self):
        text = "## Before You Listen\n\n- Point one.\n- Point two."
        result = s.validate_summary_structure(text)
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_uses_p2a_sentence_splitter(self):
        # カーリークォート付きの引用が誤って前後の段落と連結されないことを
        # 確認する(ER-003-P2Aで修正済みのsplit_sentencesが使われている証拠)。
        text = ('## Before You Listen\n\n'
                + " ".join(["word"] * 10) + '.\n\n'
                + "“" + " ".join(["word"] * 10) + '.”\n\n'
                + " ".join(["word"] * 5) + ".")
        result = s.validate_summary_structure(text)
        self.assertEqual(result["sentence_count"], 3)

    def test_heading_excluded_from_body_word_count(self):
        result = s.validate_summary_structure(GOOD_SUMMARY)
        # "Before You Listen"自体の3語が本文語数(25語)に含まれていない
        self.assertEqual(result["word_count"], 25)

    def test_metrics_saves_word_count_including_heading_separately(self):
        metrics = s.compute_summary_metrics(GOOD_SUMMARY)
        self.assertGreater(metrics["total_word_count_including_heading"], metrics["word_count"])


class OpeningSentenceRequirementTests(unittest.TestCase):
    """要求4-13(ER-003-P2C): 第一文は'We'll look at ...'で始まる
    Podcast調の語り口を必須とし、'This episode ...'的な教材紹介の
    開始表現は不合格とする。"""

    def _body(self, opening, rest_words=20):
        return "## Before You Listen\n\n" + opening + " " + " ".join(["word"] * rest_words) + "."

    def test_heading_detected_exactly_once(self):
        result = s.validate_summary_structure(GOOD_SUMMARY)
        self.assertTrue(result["heading_present"])

    def test_ascii_apostrophe_we_ll_look_at_passes_opening_check(self):
        text = self._body("We'll look at a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertTrue(result["opening_ok"])

    def test_typographic_apostrophe_we_ll_look_at_passes_opening_check(self):
        text = self._body("We’ll look at a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertTrue(result["opening_ok"])

    def test_this_episode_opening_fails(self):
        text = self._body("This episode covers a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])
        self.assertEqual(result["status"], "B2_SUMMARY_STRUCTURE_INVALID")

    def test_this_lesson_opening_fails(self):
        text = self._body("This lesson covers a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])

    def test_this_story_opening_fails(self):
        text = self._body("This story covers a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])

    def test_in_this_episode_opening_fails(self):
        text = self._body("In this episode we cover a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])

    def test_the_episode_opening_fails(self):
        text = self._body("The episode covers a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])

    def test_we_will_discuss_does_not_match_required_pattern(self):
        # "We"で始まっていても、固定パターン"We'll look at"と一致しなければ不合格
        text = self._body("We will discuss a topic,", rest_words=20)
        result = s.validate_summary_structure(text)
        self.assertFalse(result["opening_ok"])

    def test_second_sentence_not_fixed_still_passes_if_other_conditions_met(self):
        # 第二文は固定文言でなくてよい(Listen for.../Pay attention to...等)
        for second in ("Listen for how it ends.", "Pay attention to the key moment.",
                       "As you listen, notice the outcome."):
            text = ("## Before You Listen\n\nWe'll look at " + " ".join(["word"] * 10)
                    + ". " + second)
            result = s.validate_summary_structure(text)
            self.assertTrue(result["opening_ok"], msg=second)

    def test_forbidden_opening_prefixes_constant_matches_spec(self):
        self.assertEqual(
            s.FORBIDDEN_OPENING_PREFIXES,
            ("This episode", "This lesson", "This story", "In this episode", "The episode"),
        )


class RetryAndSaveTests(unittest.TestCase):
    """要求38-45: 構造・語数・文数理由のみ最大1回再試行。内容品質理由で
    再生成しない。全attemptを保存する。"""

    def test_pass_on_first_attempt_no_retry(self):
        call_count = {"n": 0}

        def make_factory():
            call_count["n"] += 1

            def generator_fn():
                return GOOD_SUMMARY, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return generator_fn

        raw_text, status, attempts, model_id, response_id = s.run_summary_structure_gate(make_factory)
        self.assertEqual(status, "B2_SUMMARY_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 1)
        self.assertEqual(len(attempts), 1)

    def test_structure_invalid_retried_once_then_passes(self):
        call_count = {"n": 0}
        bad_text = make_body([12, 12])  # 24語(範囲外)

        def make_factory():
            call_count["n"] += 1
            attempt = call_count["n"]

            def generator_fn():
                text = bad_text if attempt == 1 else GOOD_SUMMARY
                return text, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return generator_fn

        raw_text, status, attempts, model_id, response_id = s.run_summary_structure_gate(make_factory)
        self.assertEqual(status, "B2_SUMMARY_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)
        self.assertEqual(len(attempts), 2)

    def test_structure_invalid_twice_yields_final_invalid_no_third_attempt(self):
        call_count = {"n": 0}
        bad_text = make_body([12, 12])

        def make_factory():
            call_count["n"] += 1

            def generator_fn():
                return bad_text, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return generator_fn

        raw_text, status, attempts, model_id, response_id = s.run_summary_structure_gate(make_factory)
        self.assertEqual(status, "B2_SUMMARY_STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], s.MAX_STRUCTURE_RETRY_ATTEMPTS)

    def test_technical_failure_retried_once(self):
        call_count = {"n": 0}

        def make_factory():
            call_count["n"] += 1
            attempt = call_count["n"]

            def generator_fn():
                if attempt == 1:
                    raise RuntimeError("simulated network error")
                return GOOD_SUMMARY, "gpt-5.6-sol", "resp2", {"web_search_call_count": 0}, []
            return generator_fn

        raw_text, status, attempts, model_id, response_id = s.run_summary_structure_gate(make_factory)
        self.assertEqual(status, "B2_SUMMARY_STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_gate_does_not_change_prompt_between_attempts(self):
        src = inspect.getsource(s.run_summary_structure_gate)
        self.assertNotIn("user_message", src)
        self.assertNotIn("build_summary_user_message", src)

    def test_all_attempts_include_raw_text_and_structure_reasons(self):
        call_count = {"n": 0}
        bad_text = make_body([12, 12])

        def make_factory():
            call_count["n"] += 1
            attempt = call_count["n"]

            def generator_fn():
                text = bad_text if attempt == 1 else GOOD_SUMMARY
                return text, "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return generator_fn

        _, _, attempts, _, _ = s.run_summary_structure_gate(make_factory)
        for a in attempts:
            self.assertIn("raw_text", a)
            self.assertIn("structure_reasons", a)

    def test_validator_never_returns_fixed_or_corrected_text(self):
        result = s.validate_summary_structure(GOOD_SUMMARY)
        self.assertNotIn("fixed_text", result)
        self.assertNotIn("corrected_text", result)


class SummaryQaTests(unittest.TestCase):
    """要求46-59: 概要QAはgeneratorと別実行。B2本文と概要のみを入力とし、
    Web検索なし。新事実追加・矛盾・ネタバレ・above-B1候補等を検出する。"""

    def test_qa_is_separate_function_from_generator(self):
        self.assertIsNot(s.make_summary_qa_fn, s.make_summary_generator_fn)

    def test_qa_prompt_takes_only_b2_article_and_summary(self):
        sig = inspect.signature(s.build_summary_qa_prompt)
        params = list(sig.parameters)
        self.assertIn("b2_article", params)
        self.assertIn("summary", params)
        self.assertNotIn("japanese_article", params)
        self.assertNotIn("natural_english_source", params)

    def test_qa_has_no_web_search_tool(self):
        fn = s.make_summary_qa_fn("dummy prompt", client=object())
        self.assertFalse(fn.uses_web_search_tool)

    def test_qa_schema_has_required_leakage_and_addition_fields(self):
        props = s.SUMMARY_QA_JSON_SCHEMA["schema"]["properties"]
        for field in ("unsupported_additions", "contradictions", "spoilers",
                      "point_answer_leakage", "in_one_line_leakage", "above_b1_candidates",
                      "unexplained_technical_terms", "standalone_comprehension_notes",
                      "information_overload_notes", "information_gap_notes"):
            self.assertIn(field, props)

    def test_valid_qa_output_parses(self):
        raw = json.dumps({
            "verdict": "PASS", "unsupported_additions": [], "contradictions": [], "spoilers": [],
            "point_answer_leakage": [], "in_one_line_leakage": [], "above_b1_candidates": [],
            "unexplained_technical_terms": [], "standalone_comprehension_notes": [],
            "information_overload_notes": [], "information_gap_notes": [], "notes": "",
        })
        parsed = s.parse_and_validate_summary_qa_output(raw)
        self.assertEqual(parsed["verdict"], "PASS")

    def test_qa_missing_field_raises(self):
        raw = json.dumps({"verdict": "PASS"})
        with self.assertRaises(er003.QaSchemaError):
            s.parse_and_validate_summary_qa_output(raw)

    def test_qa_invalid_verdict_raises(self):
        raw = json.dumps({
            "verdict": "MAYBE", "unsupported_additions": [], "contradictions": [], "spoilers": [],
            "point_answer_leakage": [], "in_one_line_leakage": [], "above_b1_candidates": [],
            "unexplained_technical_terms": [], "standalone_comprehension_notes": [],
            "information_overload_notes": [], "information_gap_notes": [], "notes": "",
        })
        with self.assertRaises(er003.QaSchemaError):
            s.parse_and_validate_summary_qa_output(raw)

    def test_qa_non_json_raises(self):
        with self.assertRaises(er003.QaSchemaError):
            s.parse_and_validate_summary_qa_output("not json")

    def test_gate_does_not_invoke_qa_on_regenerate(self):
        src = inspect.getsource(s.run_summary_structure_gate)
        self.assertNotIn("make_summary_qa_fn", src)
        self.assertNotIn("parse_and_validate_summary_qa_output", src)

    def test_qa_output_does_not_rewrite_summary(self):
        parsed_fields = set(s.SUMMARY_QA_JSON_SCHEMA["schema"]["properties"])
        self.assertNotIn("summary", parsed_fields)
        self.assertNotIn("corrected_summary", parsed_fields)
        self.assertNotIn("body", parsed_fields)

    def test_json_response_gate_reused_directly(self):
        self.assertIs(s.run_json_response_gate, er003.run_json_response_gate)


class DeterministicMetricsTests(unittest.TestCase):
    """要求60-65: 語数・文数・各文語数・推定読み上げ時間をPythonで計測
    する。TTS・Key Wordsは生成しない。B2本文は変更しない。"""

    def test_word_count_computed_by_python_not_llm(self):
        metrics = s.compute_summary_metrics(GOOD_SUMMARY)
        self.assertEqual(metrics["word_count"], 25)

    def test_sentence_count_and_per_sentence_word_counts(self):
        metrics = s.compute_summary_metrics(GOOD_SUMMARY)
        self.assertEqual(metrics["sentence_count"], 2)
        self.assertEqual(sum(metrics["sentence_word_counts"]), 25)

    def test_three_wpm_estimates_present(self):
        metrics = s.compute_summary_metrics(GOOD_SUMMARY)
        times = metrics["estimated_reading_time_minutes"]
        for wpm in (130, 145, 160):
            self.assertIn(f"{wpm}_wpm_minutes", times)

    def test_module_does_not_reference_tts_generation(self):
        src = inspect.getsource(s)
        self.assertNotIn("elevenlabs", src.lower())
        self.assertNotIn("text_to_speech", src.lower())

    def test_module_has_no_key_words_generation_function(self):
        self.assertFalse(hasattr(s, "generate_key_words"))
        self.assertFalse(hasattr(s, "make_key_words_fn"))

    def test_load_approved_b2_article_is_read_only(self):
        src = inspect.getsource(s.load_approved_b2_article)
        self.assertNotIn('"w"', src)
        self.assertNotIn("'w'", src)


class P2AOfficialRecordTests(unittest.TestCase):
    """要求1-5: P2Bの前提として、ER-003-P2Aの再計測結果がA01/A02/ADD03
    すべての正式記録としてPASSに訂正されていることを確認する。"""

    def _run_summary(self, topic_id):
        with open(f"er003_output/p2/{topic_id}_run_summary.json", encoding="utf-8") as f:
            return json.load(f)

    def test_all_three_articles_official_metrics_pass(self):
        for topic_id in ("A01", "A02", "ADD03"):
            with open(f"er003_output/p2/{topic_id}/sentence_metrics_recalculated.json", encoding="utf-8") as f:
                recalculated = json.load(f)
            self.assertEqual(recalculated["overall_status"], "B2_SENTENCE_METRICS_PASS", msg=topic_id)

    def test_supersession_manifest_records_old_verdicts(self):
        with open("er003_output/p2/P2A_metrics_supersession_manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        by_topic = {r["topic_id"]: r for r in manifest["per_article_verdict_change"]}
        self.assertEqual(by_topic["A02"]["pre_p2a_overall_status"], "B2_SENTENCE_METRICS_FAIL")
        self.assertEqual(by_topic["A02"]["official_overall_status"], "B2_SENTENCE_METRICS_PASS")
        self.assertEqual(by_topic["ADD03"]["pre_p2a_overall_status"], "B2_SENTENCE_METRICS_FAIL")
        self.assertEqual(by_topic["ADD03"]["official_overall_status"], "B2_SENTENCE_METRICS_PASS")

    def test_run_summary_sentence_metrics_reflects_recalculated_values(self):
        for topic_id in ("A01", "A02", "ADD03"):
            run_summary = self._run_summary(topic_id)
            self.assertEqual(run_summary["sentence_metrics"]["overall_status"], "B2_SENTENCE_METRICS_PASS")
            self.assertIn("sentence_metrics_pre_p2a_superseded", run_summary)

    def test_b2_body_text_untouched_by_p2a(self):
        for topic_id, path in s.B2_INPUT_PATHS.items():
            with open(path, encoding="utf-8") as f:
                text = f.read()
            with open(f"er003_output/p2/{topic_id}/sentence_segments.json", encoding="utf-8") as f:
                segments = json.load(f)
            self.assertEqual(er003.sha256_text(text), segments["source_sha256"])

    def test_p2a_finalize_script_does_not_touch_natural_source(self):
        with open("er003_v1_p2a_finalize.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("natural_source_approved", src)


if __name__ == "__main__":
    unittest.main()
