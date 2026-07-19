# ============================================================
# er002_test_ja_article_generation.py
# ER-002-v1.2M-R4-FINALIZE: 正式採用された記事生成パイプラインのテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物
# (ER-002-v1.2M-R4の条件Lで実際に保存されたraw_response.json/
# raw_article.md)の読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_article_generation -v

import inspect
import json
import types
import unittest

import er002_ja_article_generation as article_gen
import er002_ja_web_research_r3 as r3

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"
CONDITION_L_DIR = "er002_output/v1_2m_r4/condition_l"


def dict_to_ns(d):
    if isinstance(d, dict):
        ns = types.SimpleNamespace()
        for k, v in d.items():
            setattr(ns, k, dict_to_ns(v))
        return ns
    if isinstance(d, list):
        return [dict_to_ns(x) for x in d]
    return d


class LengthSpecFrozenValueTests(unittest.TestCase):
    """基準値・許容範囲が単一のJSONから読み込まれ、マジックナンバーとして
    コード中に分散していないことを確認する。"""

    def test_master_spoken_text_char_count_is_697(self):
        self.assertEqual(article_gen.MASTER_SPOKEN_TEXT_CHAR_COUNT, 697)

    def test_lower_bound_is_592(self):
        self.assertEqual(article_gen.LENGTH_LOWER_BOUND, 592)

    def test_upper_bound_is_802(self):
        self.assertEqual(article_gen.LENGTH_UPPER_BOUND, 802)

    def test_recompute_from_master_matches_frozen_spec(self):
        recomputed = article_gen.recompute_length_spec_from_master()
        self.assertEqual(recomputed["master_spoken_text_char_count"], article_gen.MASTER_SPOKEN_TEXT_CHAR_COUNT)
        self.assertEqual(recomputed["lower_bound"], article_gen.LENGTH_LOWER_BOUND)
        self.assertEqual(recomputed["upper_bound"], article_gen.LENGTH_UPPER_BOUND)

    def test_bounds_are_computed_not_hardcoded_in_source(self):
        # モジュールのコード行(コメントを除く)中に592/802/697が直接
        # 埋め込まれておらず、load_length_spec()経由でJSONから読み込まれて
        # いることを確認する(コメントでの説明的な言及は許容する)
        with open("er002_ja_article_generation.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_only = "\n".join(l.split("#", 1)[0] for l in lines if not l.strip().startswith("#"))
        self.assertNotIn("592", code_only)
        self.assertNotIn("802", code_only)
        self.assertNotIn("697", code_only)
        self.assertIn("load_length_spec", code_only)

    def test_length_spec_file_has_tolerance_ratios(self):
        with open("er002_v1_2m_length_spec.json", encoding="utf-8") as f:
            spec = json.load(f)
        self.assertEqual(spec["tolerance_lower_ratio"], 0.85)
        self.assertEqual(spec["tolerance_upper_ratio"], 1.15)


class LengthBoundaryTests(unittest.TestCase):
    """受入条件: 境界値592字と802字は合格。591字と803字は不合格。"""

    def test_lower_boundary_592_passes(self):
        result = {"status": "COUNT_OK", "spoken_text_char_count": 592}
        self.assertEqual(article_gen.validate_length(result), "LENGTH_PASS")

    def test_upper_boundary_802_passes(self):
        result = {"status": "COUNT_OK", "spoken_text_char_count": 802}
        self.assertEqual(article_gen.validate_length(result), "LENGTH_PASS")

    def test_just_below_lower_boundary_591_fails(self):
        result = {"status": "COUNT_OK", "spoken_text_char_count": 591}
        self.assertEqual(article_gen.validate_length(result), "LENGTH_FAIL")

    def test_just_above_upper_boundary_803_fails(self):
        result = {"status": "COUNT_OK", "spoken_text_char_count": 803}
        self.assertEqual(article_gen.validate_length(result), "LENGTH_FAIL")

    def test_uncertain_status_propagates(self):
        result = {"status": "COUNT_EXTRACTION_UNCERTAIN", "spoken_text_char_count": None}
        self.assertEqual(article_gen.validate_length(result), "COUNT_EXTRACTION_UNCERTAIN")


class CitationAnnotationRemovalTests(unittest.TestCase):
    """citation annotationの文字位置情報を使った引用表示除去のテスト。"""

    def test_single_citation_removed(self):
        text = "本文([site.com](https://example.com))続き"
        start = text.index("([site.com]")
        end = text.index("続き")
        anns = [{"start_index": start, "end_index": end, "title": "site.com", "url": "https://example.com"}]
        self.assertEqual(article_gen.remove_citation_spans(text, anns), "本文続き")

    def test_multiple_citations_removed_correctly(self):
        text = "AA(one)BB(two)CC"
        anns = [
            {"start_index": 2, "end_index": 7, "title": "1", "url": "1"},
            {"start_index": 9, "end_index": 14, "title": "2", "url": "2"},
        ]
        self.assertEqual(article_gen.remove_citation_spans(text, anns), "AABBCC")

    def test_no_citations_leaves_text_unchanged(self):
        text = "引用のない本文です。"
        self.assertEqual(article_gen.remove_citation_spans(text, []), text)

    def test_boundary_span_at_text_start(self):
        text = "(citation)本文"
        anns = [{"start_index": 0, "end_index": 10, "title": "t", "url": "u"}]
        self.assertEqual(article_gen.remove_citation_spans(text, anns), "本文")

    def test_boundary_span_at_text_end(self):
        text = "本文(citation)"
        anns = [{"start_index": 2, "end_index": 12, "title": "t", "url": "u"}]
        self.assertEqual(article_gen.remove_citation_spans(text, anns), "本文")

    def test_extract_annotations_none_when_no_message(self):
        class FakeResponse:
            output = []
        self.assertIsNone(article_gen.extract_citation_annotations(FakeResponse()))

    def test_compute_uncertain_when_annotations_none(self):
        result = article_gen.compute_spoken_text_char_count("本文", None)
        self.assertEqual(result["status"], "COUNT_EXTRACTION_UNCERTAIN")

    def test_compute_ok_when_annotations_empty(self):
        result = article_gen.compute_spoken_text_char_count("本文です", [])
        self.assertEqual(result["status"], "COUNT_OK")
        self.assertEqual(result["spoken_text_char_count"], len("本文です"))


class MarkdownWhitespaceNfkcNormalizationTests(unittest.TestCase):
    def test_strips_heading_bold_code_markers(self):
        stripped = article_gen.strip_markdown_symbols("## **見出し** と `code`")
        for ch in ["#", "*", "`"]:
            self.assertNotIn(ch, stripped)

    def test_removes_whitespace_newlines_tabs(self):
        normalized = article_gen.normalize_for_char_count("あ い\tう\nえ　お")
        self.assertEqual(normalized, "あいうえお")

    def test_nfkc_normalizes_fullwidth_and_halfwidth_mix(self):
        normalized = article_gen.normalize_for_char_count("Ａｂｃ123")
        self.assertEqual(normalized, "Abc123")

    def test_does_not_blanket_delete_parentheses(self):
        stripped = article_gen.strip_markdown_symbols("これは(補足)です")
        self.assertIn("補足", stripped)


class WriterExecutionModelTests(unittest.TestCase):
    """受入条件: 1記事1writer実行になっている。条件LBが正式経路から除外。"""

    def test_writer_executions_per_article_is_one(self):
        self.assertEqual(article_gen.WRITER_EXECUTIONS_PER_ARTICLE, 1)

    def test_official_module_has_no_batch_functions(self):
        forbidden_names = [
            "parse_batch_articles", "attribute_annotations_to_batch_articles",
            "classify_batch_topic_evidence", "classify_batch_article_diagnostics",
            "build_writer_user_message_r4_lb",
        ]
        for name in forbidden_names:
            self.assertFalse(hasattr(article_gen, name), f"{name}が正式モジュールに存在してはならない")

    def test_build_writer_user_message_takes_single_topic(self):
        params = list(inspect.signature(article_gen.build_writer_user_message).parameters)
        self.assertIn("topic", params)
        self.assertNotIn("topics", params)

    def test_no_retry_on_structure_or_length_in_technical_gate(self):
        src = inspect.getsource(article_gen.run_writer_technical_gate)
        self.assertNotIn("validate_point_structure", src)
        self.assertNotIn("validate_length", src)
        self.assertNotIn("web_search_call_count", src)


class ConditionLPromptReuseTests(unittest.TestCase):
    def test_message_starts_with_r3_message(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        r3_msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        official_msg = article_gen.build_writer_user_message(master, "テストテーマ")
        self.assertTrue(official_msg.startswith(r3_msg))

    def test_diff_from_r3_is_exactly_length_suffix(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        r3_msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        official_msg = article_gen.build_writer_user_message(master, "テストテーマ")
        suffix = article_gen.build_length_instruction_suffix()
        self.assertEqual(official_msg, r3_msg + "\n\n" + suffix)


class FactCheckerUnchangedFromR3Tests(unittest.TestCase):
    def test_official_module_does_not_redefine_fact_checker(self):
        with open("er002_ja_article_generation.py", encoding="utf-8") as f:
            src_lines = f.readlines()
        for line in src_lines:
            self.assertNotRegex(line, r"^def make_fact_checker_fn")
            self.assertNotRegex(line, r"^def run_fact_checker_with_gates")
            self.assertNotRegex(line, r"^def parse_and_validate_fact_check_output")

    def test_official_module_reuses_r3_fact_checker_directly(self):
        # 公式モジュールはr3を直接importして使うだけで、fact checkerの
        # 実体を再定義していない
        with open("er002_ja_article_generation.py", encoding="utf-8") as f:
            src = f.read()
        self.assertIn("import er002_ja_web_research_r3 as r3", src)

    def test_fact_check_include_verdicts_excludes_fail(self):
        self.assertEqual(set(article_gen.FACT_CHECK_INCLUDE_VERDICTS), {"PASS", "REVIEW_REQUIRED"})
        self.assertNotIn("FAIL", article_gen.FACT_CHECK_INCLUDE_VERDICTS)

    def test_fact_checker_model_and_effort_unchanged(self):
        self.assertEqual(r3.FACT_CHECKER_MODEL, "gpt-5.6-sol")
        self.assertEqual(r3.FACT_CHECKER_REASONING_EFFORT, "high")

    def test_review_required_not_auto_promoted_to_pass(self):
        with open("er002_v1_2m_generate_article.py", encoding="utf-8") as f:
            src = f.read()
        # REVIEW_REQUIREDをPASSへ書き換えるロジックが存在しない
        self.assertNotIn('"REVIEW_REQUIRED"] = "PASS"', src)
        self.assertNotIn("verdict == 'REVIEW_REQUIRED'", src.replace('"', "'"))


class ConditionLReproducibilityTests(unittest.TestCase):
    """受入条件: 条件Lの既存3記事(A01=674字, A02=722字, ADD03=698字)の
    計測結果が、保存済みの実API成果物から再現できる。実APIは呼ばない。"""

    EXPECTED_COUNTS = {"A01": 674, "A02": 722, "ADD03": 698}

    def _measure(self, topic_id):
        with open(f"{CONDITION_L_DIR}/{topic_id}/raw_response.json", encoding="utf-8") as f:
            raw = json.load(f)
        response = dict_to_ns(raw)
        annotations = article_gen.extract_citation_annotations(response)
        with open(f"{CONDITION_L_DIR}/{topic_id}/raw_article.md", encoding="utf-8") as f:
            raw_article = f.read()
        return article_gen.compute_spoken_text_char_count(raw_article, annotations)

    def test_a01_reproduces_674(self):
        result = self._measure("A01")
        self.assertEqual(result["spoken_text_char_count"], self.EXPECTED_COUNTS["A01"])

    def test_a02_reproduces_722(self):
        result = self._measure("A02")
        self.assertEqual(result["spoken_text_char_count"], self.EXPECTED_COUNTS["A02"])

    def test_add03_reproduces_698(self):
        result = self._measure("ADD03")
        self.assertEqual(result["spoken_text_char_count"], self.EXPECTED_COUNTS["ADD03"])

    def test_all_three_pass_length_gate(self):
        for topic_id in self.EXPECTED_COUNTS:
            result = self._measure(topic_id)
            self.assertEqual(article_gen.validate_length(result), "LENGTH_PASS")


class OfficialGenerationScriptTests(unittest.TestCase):
    def test_generate_article_script_has_no_lb_argument(self):
        with open("er002_v1_2m_generate_article.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn('"lb"', src)
        self.assertNotIn("condition_lb", src)

    def test_generate_article_takes_single_topic_id_and_topic(self):
        import er002_v1_2m_generate_article as gen
        params = list(inspect.signature(gen.generate_article).parameters)
        self.assertEqual(params[:2], ["topic_id", "topic"])


if __name__ == "__main__":
    unittest.main()
