# ============================================================
# er002_test_ja_web_research_r4.py
# ER-002-v1.2M-R4: 記事長制約と複数記事同時生成の比較検証のテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_web_research_r4 -v

import inspect
import json
import math
import os
import unittest

import er002_ja_web_research_r3 as r3
import er002_ja_web_research_r4 as r4

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"


def make_fake_response(output_text, model="gpt-5.6-sol", response_id="resp_test",
                        search_call_count=1, queries=None, annotations=None):
    """r4.extract_citation_annotationsが読めるstart_index/end_index付きの
    annotationを持つfakeレスポンスを作る。"""
    queries = queries if queries is not None else ["テストクエリ"]
    annotations = annotations if annotations is not None else []

    class FakeAction:
        def __init__(self, qs):
            self.queries = qs
            self.query = qs[0] if qs else None

    class FakeWebSearchCall:
        type = "web_search_call"

        def __init__(self, qs):
            self.action = FakeAction(qs)

    class FakeAnnotation:
        type = "url_citation"

        def __init__(self, a):
            self.start_index = a["start_index"]
            self.end_index = a["end_index"]
            self.title = a.get("title")
            self.url = a.get("url")

    class FakeContent:
        def __init__(self, anns):
            self.annotations = anns

    class FakeMessage:
        type = "message"

        def __init__(self, anns):
            self.content = [FakeContent(anns)]

    class FakeResponse:
        def __init__(self):
            self.model = model
            self.id = response_id
            self.output_text = output_text
            anns = [FakeAnnotation(a) for a in annotations]
            items = [FakeWebSearchCall(queries) for _ in range(search_call_count)]
            items.append(FakeMessage(anns))
            self.output = items

    return FakeResponse()


def make_response_without_message():
    class FakeResponse:
        output = []
        output_text = ""
    return FakeResponse()


TWO_POINT_MARKDOWN = (
    "# タイトル\n\n本文段落。\n\n"
    "## セクション\n\n"
    "### 見出し1\n\n内容1。\n\n"
    "### 見出し2\n\n内容2。\n\n"
)


class CitationAnnotationExtractionTests(unittest.TestCase):
    def test_extract_annotations_returns_list_with_indices(self):
        resp = make_fake_response(
            "本文(引用)です。",
            annotations=[{"start_index": 2, "end_index": 6, "title": "t", "url": "u"}],
        )
        anns = r4.extract_citation_annotations(resp)
        self.assertEqual(anns, [{"start_index": 2, "end_index": 6, "title": "t", "url": "u"}])

    def test_extract_annotations_none_when_no_message_item(self):
        resp = make_response_without_message()
        self.assertIsNone(r4.extract_citation_annotations(resp))

    def test_extract_annotations_empty_list_when_message_has_zero_citations(self):
        resp = make_fake_response("本文です。", annotations=[])
        self.assertEqual(r4.extract_citation_annotations(resp), [])


class CitationSpanRemovalTests(unittest.TestCase):
    def test_remove_single_span(self):
        text = "前(citation)後"
        anns = [{"start_index": 1, "end_index": 11, "title": "t", "url": "u"}]
        self.assertEqual(r4.remove_citation_spans(text, anns), "前後")

    def test_remove_multiple_spans_descending_order_keeps_indices_valid(self):
        text = "AA(one)BB(two)CC"
        anns = [
            {"start_index": 2, "end_index": 7, "title": "1", "url": "1"},
            {"start_index": 9, "end_index": 14, "title": "2", "url": "2"},
        ]
        self.assertEqual(r4.remove_citation_spans(text, anns), "AABBCC")

    def test_real_r3_annotation_span_matches_citation_markup(self):
        # R3で実際に保存されたraw_response.jsonのannotation構造(start_index/
        # end_indexがoutput_text中の"([domain](url))"形式の引用表示を正確に
        # 指すこと)を、簡略化した同型データで再現して検証する。
        text = "本文([fifa.com](https://example.com/x))続き"
        start = text.index("([fifa.com]")
        end = text.index("続き")
        anns = [{"start_index": start, "end_index": end, "title": "fifa.com", "url": "https://example.com/x"}]
        self.assertEqual(r4.remove_citation_spans(text, anns), "本文続き")


class MarkdownSymbolStripTests(unittest.TestCase):
    def test_strips_heading_markers(self):
        self.assertNotIn("#", r4.strip_markdown_symbols("## 見出し"))

    def test_strips_bold_and_italic_markers(self):
        stripped = r4.strip_markdown_symbols("**太字**と*斜体*")
        self.assertNotIn("*", stripped)
        self.assertIn("太字", stripped)
        self.assertIn("斜体", stripped)

    def test_strips_code_fence_and_inline_code(self):
        stripped = r4.strip_markdown_symbols("```code block```と`inline`")
        self.assertNotIn("`", stripped)

    def test_strips_urls(self):
        stripped = r4.strip_markdown_symbols("見てくださいhttps://example.com/path 以上")
        self.assertNotIn("https://", stripped)

    def test_does_not_blanket_delete_arbitrary_parentheses(self):
        # 6.3: 任意の括弧書きを一律削除しないこと
        stripped = r4.strip_markdown_symbols("これは(重要な補足)です。")
        self.assertIn("重要な補足", stripped)

    def test_heading_text_content_preserved(self):
        stripped = r4.strip_markdown_symbols("### ⭐ 見出しの中身")
        self.assertIn("見出しの中身", stripped)


class NormalizeForCharCountTests(unittest.TestCase):
    def test_nfkc_normalizes_fullwidth_ascii(self):
        # 全角英数はNFKCで半角へ正規化される(文字数自体は変わらない場合が多いが
        # 正規化ロジックが実際に動作していることを確認する)
        normalized = r4.normalize_for_char_count("Ａ")
        self.assertEqual(normalized, "A")

    def test_removes_all_whitespace_and_newlines_and_tabs(self):
        normalized = r4.normalize_for_char_count("あ い\tう\nえ　お")
        self.assertEqual(normalized, "あいうえお")

    def test_punctuation_is_counted(self):
        normalized = r4.normalize_for_char_count("「これは、句読点。」")
        self.assertEqual(len(normalized), len("「これは、句読点。」"))


class ComputeSpokenTextCharCountTests(unittest.TestCase):
    def test_uncertain_status_when_annotations_none(self):
        result = r4.compute_spoken_text_char_count("本文", None)
        self.assertEqual(result["status"], "COUNT_EXTRACTION_UNCERTAIN")
        self.assertIsNone(result["spoken_text_char_count"])

    def test_ok_status_when_annotations_empty_list(self):
        result = r4.compute_spoken_text_char_count("本文です", [])
        self.assertEqual(result["status"], "COUNT_OK")
        self.assertEqual(result["spoken_text_char_count"], len("本文です"))

    def test_ok_status_removes_citation_before_counting(self):
        text = "本文([site.com](https://example.com))です"
        start = text.index("([site.com]")
        end = text.index("です")
        anns = [{"start_index": start, "end_index": end, "title": "site.com", "url": "https://example.com"}]
        result = r4.compute_spoken_text_char_count(text, anns)
        self.assertEqual(result["spoken_text_char_count"], len("本文です"))


class MasterRemeasurementTests(unittest.TestCase):
    def test_master_char_count_result_is_ok(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master_text = f.read()
        result = r4.compute_master_char_count_result(master_text)
        self.assertEqual(result["status"], "COUNT_OK")
        self.assertIsInstance(result["spoken_text_char_count"], int)
        self.assertGreater(result["spoken_text_char_count"], 0)

    def test_lower_bound_is_floor_of_085(self):
        lower, upper = r4.compute_length_bounds(1000)
        self.assertEqual(lower, math.floor(1000 * 0.85))

    def test_upper_bound_is_ceil_of_115(self):
        lower, upper = r4.compute_length_bounds(1000)
        self.assertEqual(upper, math.ceil(1000 * 1.15))

    def test_bounds_use_floor_ceil_not_round(self):
        # 997は端数が出る値。四捨五入ではなくfloor/ceilであることを確認する
        lower, upper = r4.compute_length_bounds(997)
        self.assertEqual(lower, math.floor(997 * 0.85))
        self.assertEqual(upper, math.ceil(997 * 1.15))


class LengthGateTests(unittest.TestCase):
    def test_length_pass_within_bounds(self):
        count_result = {"status": "COUNT_OK", "spoken_text_char_count": 700}
        self.assertEqual(r4.validate_length(count_result, 600, 800), "LENGTH_PASS")

    def test_length_fail_below_lower_bound(self):
        count_result = {"status": "COUNT_OK", "spoken_text_char_count": 500}
        self.assertEqual(r4.validate_length(count_result, 600, 800), "LENGTH_FAIL")

    def test_length_fail_above_upper_bound(self):
        count_result = {"status": "COUNT_OK", "spoken_text_char_count": 900}
        self.assertEqual(r4.validate_length(count_result, 600, 800), "LENGTH_FAIL")

    def test_length_uncertain_propagates(self):
        count_result = {"status": "COUNT_EXTRACTION_UNCERTAIN", "spoken_text_char_count": None}
        self.assertEqual(r4.validate_length(count_result, 600, 800), "COUNT_EXTRACTION_UNCERTAIN")


class ConditionLPromptTests(unittest.TestCase):
    def test_l_message_starts_with_r3_message(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        r3_msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        l_msg = r4.build_writer_user_message_r4_l(master, "テストテーマ", 700, 595, 805)
        self.assertTrue(l_msg.startswith(r3_msg))

    def test_l_message_diff_is_exactly_length_suffix(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        r3_msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        l_msg = r4.build_writer_user_message_r4_l(master, "テストテーマ", 700, 595, 805)
        suffix = r4.build_length_instruction_suffix(700, 595, 805)
        self.assertEqual(l_msg, r3_msg + "\n\n" + suffix)

    def test_length_suffix_contains_bounds(self):
        suffix = r4.build_length_instruction_suffix(700, 595, 805)
        self.assertIn("700", suffix)
        self.assertIn("595", suffix)
        self.assertIn("805", suffix)

    def test_length_suffix_forbids_nothing_extra(self):
        # 第7節で追加禁止とされた項目(段落数指定・自己採点等)の文言が
        # 混入していないことを確認する
        suffix = r4.build_length_instruction_suffix(700, 595, 805)
        forbidden_terms = ["段落数", "自己採点", "複数案", "出力トークン上限"]
        for term in forbidden_terms:
            self.assertNotIn(term, suffix)


class ConditionLBPromptTests(unittest.TestCase):
    def test_lb_message_contains_three_topics(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        lb_msg = r4.build_writer_user_message_r4_lb(master, 700, 595, 805)
        for topic_fragment in ["イングランド対アルゼンチン", "夜間SNS設定", "ホルムズ海峡"]:
            self.assertIn(topic_fragment, lb_msg)

    def test_lb_message_contains_id_headings_in_order(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        lb_msg = r4.build_writer_user_message_r4_lb(master, 700, 595, 805)
        pos_a01 = lb_msg.index("## A01")
        pos_a02 = lb_msg.index("## A02")
        pos_add03 = lb_msg.index("## ADD03")
        self.assertLess(pos_a01, pos_a02)
        self.assertLess(pos_a02, pos_add03)

    def test_lb_message_contains_bounds(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        lb_msg = r4.build_writer_user_message_r4_lb(master, 700, 595, 805)
        self.assertIn("595", lb_msg)
        self.assertIn("805", lb_msg)

    def test_lb_single_writer_call_per_batch(self):
        # LBはwriter API呼び出しが1回であることを構造的に保証する:
        # run_writer_technical_gateへ渡すmake_writer_fnはバッチ全体で
        # ただ1つのuser_messageから作られる(個別テーマごとに複数回
        # 呼び出す実装になっていないことをソースコードから確認する)
        src = inspect.getsource(r4)
        self.assertNotIn("for topic in R4_LB_TOPIC_ORDER", src)


class BatchParsingTests(unittest.TestCase):
    def _make_batch(self, ids=("A01", "A02", "ADD03")):
        parts = []
        for i in ids:
            parts.append(f"## {i}\n記事{i}本文です。\n\n### 見出し1\n\n内容1\n\n### 見出し2\n\n内容2\n")
        return "\n".join(parts)

    def test_valid_batch_splits_into_three(self):
        result = r4.parse_batch_articles(self._make_batch())
        self.assertEqual(result["status"], "BATCH_PARSE_OK")
        self.assertEqual(set(result["articles"].keys()), {"A01", "A02", "ADD03"})

    def test_id_heading_excluded_from_article_raw_text(self):
        result = r4.parse_batch_articles(self._make_batch())
        for topic_id, info in result["articles"].items():
            self.assertNotIn(f"## {topic_id}", info["raw_text"])

    def test_missing_id_is_invalid(self):
        batch = "## A01\nx\n## A02\ny\n"
        result = r4.parse_batch_articles(batch)
        self.assertEqual(result["status"], "BATCH_PARSE_INVALID")

    def test_duplicate_id_is_invalid(self):
        batch = "## A01\nx\n## A01\ny\n## A02\nz\n## ADD03\nw\n"
        result = r4.parse_batch_articles(batch)
        self.assertEqual(result["status"], "BATCH_PARSE_INVALID")

    def test_wrong_order_is_invalid(self):
        batch = "## A02\nx\n## A01\ny\n## ADD03\nz\n"
        result = r4.parse_batch_articles(batch)
        self.assertEqual(result["status"], "BATCH_PARSE_INVALID")

    def test_unknown_id_is_invalid(self):
        batch = "## A01\nx\n## A02\ny\n## ADD99\nz\n"
        result = r4.parse_batch_articles(batch)
        self.assertEqual(result["status"], "BATCH_PARSE_INVALID")

    def test_does_not_guess_split_on_invalid_batch(self):
        batch = "## A01\nx\n## A02\ny\n"
        result = r4.parse_batch_articles(batch)
        self.assertIsNone(result["articles"])


class CitationAttributionTests(unittest.TestCase):
    def test_annotation_attributed_to_correct_article(self):
        batch = "## A01\n記事1本文です。\n## A02\n記事2本文です。\n## ADD03\n記事3本文です。\n"
        result = r4.parse_batch_articles(batch)
        articles = result["articles"]
        target_start = batch.index("記事2")
        anns = [{"start_index": target_start, "end_index": target_start + 2, "title": "t", "url": "u"}]
        attributed = r4.attribute_annotations_to_batch_articles(articles, anns)
        self.assertEqual(len(attributed["A02"]["citation_annotations"]), 1)
        self.assertEqual(len(attributed["A01"]["citation_annotations"]), 0)
        self.assertEqual(len(attributed["ADD03"]["citation_annotations"]), 0)

    def test_none_annotations_propagate_as_none_per_article(self):
        batch = "## A01\nx\n## A02\ny\n## ADD03\nz\n"
        articles = r4.parse_batch_articles(batch)["articles"]
        attributed = r4.attribute_annotations_to_batch_articles(articles, None)
        for info in attributed.values():
            self.assertIsNone(info["citation_annotations"])

    def test_topic_evidence_confirmed_when_citations_present(self):
        self.assertEqual(r4.classify_batch_topic_evidence([{"start_index": 0, "end_index": 1}]), "TOPIC_RESEARCH_CONFIRMED")

    def test_topic_evidence_not_confirmed_when_empty(self):
        self.assertEqual(r4.classify_batch_topic_evidence([]), "BATCH_TOPIC_RESEARCH_NOT_CONFIRMED")

    def test_topic_evidence_not_confirmed_when_none(self):
        self.assertEqual(r4.classify_batch_topic_evidence(None), "BATCH_TOPIC_RESEARCH_NOT_CONFIRMED")


class StructureGateReuseTests(unittest.TestCase):
    def test_two_h3_pass(self):
        diag = r4.classify_writer_diagnostics(
            TWO_POINT_MARKDOWN, {"web_search_call_count": 1}, {"status": "COUNT_OK", "spoken_text_char_count": 700},
            600, 800,
        )
        self.assertEqual(diag["structure_status"], "STRUCTURE_PASS")

    def test_zero_h3_fail(self):
        diag = r4.classify_writer_diagnostics(
            "# タイトル\n\n本文のみ\n", {"web_search_call_count": 1}, {"status": "COUNT_OK", "spoken_text_char_count": 700},
            600, 800,
        )
        self.assertEqual(diag["structure_status"], "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")

    def test_three_h3_fail(self):
        md = "# T\n\n### A\n\naa\n\n### B\n\nbb\n\n### C\n\ncc\n"
        diag = r4.classify_writer_diagnostics(
            md, {"web_search_call_count": 1}, {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertEqual(diag["structure_status"], "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")


class NoRetryOnContentOrLengthOrStructureTests(unittest.TestCase):
    """要求: 文字数・構造・内容不満では再試行しない。技術的失敗のみ最大1回。"""

    def test_technical_gate_source_never_checks_structure_or_length(self):
        src = inspect.getsource(r4.run_writer_technical_gate)
        self.assertNotIn("validate_point_structure", src)
        self.assertNotIn("validate_length", src)
        self.assertNotIn("web_search_call_count", src)

    def test_succeeded_call_returns_immediately_without_retry(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1

            def writer_fn():
                return "# T\n\nzero point structure\n", "gpt-5.6-sol", "resp1", {"web_search_call_count": 0}, []
            return writer_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = r4.run_writer_technical_gate(
            make_writer_fn)
        self.assertEqual(status, "WRITER_CALL_SUCCEEDED")
        self.assertEqual(call_count["n"], 1)  # 検索未使用でも再試行されない

    def test_technical_failure_retried_once(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1
            attempt = call_count["n"]

            def writer_fn():
                if attempt == 1:
                    raise RuntimeError("simulated network error")
                return "# T\n\n### A\n\na\n\n### B\n\nb\n", "gpt-5.6-sol", "resp2", {"web_search_call_count": 1}, []
            return writer_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = r4.run_writer_technical_gate(
            make_writer_fn)
        self.assertEqual(status, "WRITER_CALL_SUCCEEDED")
        self.assertEqual(call_count["n"], 2)

    def test_never_exceeds_max_technical_attempts(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1

            def writer_fn():
                raise RuntimeError("always fails")
            return writer_fn

        r4.run_writer_technical_gate(make_writer_fn)
        self.assertLessEqual(call_count["n"], r4.MAX_TECHNICAL_RETRY_ATTEMPTS)

    def test_structure_invalid_not_retried_and_recorded(self):
        diag = r4.classify_writer_diagnostics(
            "# T\n\nno points\n", {"web_search_call_count": 1},
            {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertEqual(diag["structure_status"], "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertFalse(diag["eligible_for_fact_check"])

    def test_length_fail_does_not_block_fact_check_eligibility_alone(self):
        # 文字数逸脱は事実確認への回付を妨げない(文字数は独立した評価軸)
        diag = r4.classify_writer_diagnostics(
            TWO_POINT_MARKDOWN, {"web_search_call_count": 1},
            {"status": "COUNT_OK", "spoken_text_char_count": 9999}, 600, 800)
        self.assertEqual(diag["length_status"], "LENGTH_FAIL")
        self.assertTrue(diag["eligible_for_fact_check"])


class WriterDiagnosticsWebSearchTests(unittest.TestCase):
    def test_web_search_used_status(self):
        diag = r4.classify_writer_diagnostics(
            TWO_POINT_MARKDOWN, {"web_search_call_count": 3},
            {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertEqual(diag["web_search_status"], "WEB_SEARCH_USED")

    def test_web_search_not_used_excludes_from_fact_check(self):
        diag = r4.classify_writer_diagnostics(
            TWO_POINT_MARKDOWN, {"web_search_call_count": 0},
            {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertEqual(diag["web_search_status"], "WRITER_WEB_SEARCH_NOT_USED")
        self.assertFalse(diag["eligible_for_fact_check"])

    def test_batch_article_eligibility_requires_topic_evidence(self):
        diag = r4.classify_batch_article_diagnostics(
            TWO_POINT_MARKDOWN, "WEB_SEARCH_USED", [],
            {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertEqual(diag["topic_evidence_status"], "BATCH_TOPIC_RESEARCH_NOT_CONFIRMED")
        self.assertFalse(diag["eligible_for_fact_check"])

    def test_batch_article_eligible_when_all_three_axes_pass(self):
        diag = r4.classify_batch_article_diagnostics(
            TWO_POINT_MARKDOWN, "WEB_SEARCH_USED", [{"start_index": 0, "end_index": 1}],
            {"status": "COUNT_OK", "spoken_text_char_count": 700}, 600, 800)
        self.assertTrue(diag["eligible_for_fact_check"])


class FactCheckerUnchangedTests(unittest.TestCase):
    """R3のfact checkerロジックが完全に不変のまま再利用されていることを確認する。"""

    def test_r4_does_not_redefine_fact_checker_functions(self):
        with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
            src_lines = f.readlines()
        for line in src_lines:
            self.assertNotRegex(line, r"^def make_fact_checker_fn")
            self.assertNotRegex(line, r"^def run_fact_checker_with_gates")
            self.assertNotRegex(line, r"^def parse_and_validate_fact_check_output")
            self.assertNotRegex(line, r"^FACT_CHECK_JSON_SCHEMA\s*=")

    def test_r4_reuses_r3_fact_checker_directly(self):
        self.assertIs(r4.r3.run_fact_checker_with_gates, r3.run_fact_checker_with_gates)
        self.assertIs(r4.r3.make_fact_checker_fn, r3.make_fact_checker_fn)
        self.assertIs(r4.r3.FACT_CHECK_JSON_SCHEMA, r3.FACT_CHECK_JSON_SCHEMA)

    def test_fact_checker_model_and_effort_unchanged(self):
        self.assertEqual(r3.FACT_CHECKER_MODEL, "gpt-5.6-sol")
        self.assertEqual(r3.FACT_CHECKER_REASONING_EFFORT, "high")


class WriterConditionsUnchangedFromR3Tests(unittest.TestCase):
    def test_writer_model_reasoning_developer_message_unchanged(self):
        self.assertEqual(r4.WRITER_MODEL, "gpt-5.6-sol")
        self.assertEqual(r4.WRITER_REASONING_EFFORT, "high")
        self.assertEqual(r4.NEUTRAL_DEVELOPER_MESSAGE, "日本語の記事を作成してください。")

    def test_r4_reuses_r3_writer_call_function_directly(self):
        self.assertIs(r4.r3.make_writer_research_fn, r3.make_writer_research_fn)

    def test_writer_still_has_web_search_tool(self):
        writer_src = inspect.getsource(r3.make_writer_research_fn)
        self.assertIn('{"type": "web_search"}', writer_src)

    def test_app_does_not_fix_search_query(self):
        writer_src = inspect.getsource(r3.make_writer_research_fn)
        self.assertNotIn('"query":', writer_src)
        self.assertNotIn('"queries":', writer_src)


class R3ArtifactsUnchangedTests(unittest.TestCase):
    def test_r3_review_markdown_still_present(self):
        path = "er002_output/v1_2m_r3/ER-002-v1.2M-R3_user_review.md"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("A01", content)

    def test_r3_status_record_exists(self):
        path = "er002_output/_experiment_config/ER-002-v1.2M-R3_status.json"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            status = json.load(f)
        self.assertEqual(status["process_acceptance"], "ACCEPTED")


class NoOtherApiCallsR4Tests(unittest.TestCase):
    def test_tts_not_referenced(self):
        with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
            src = f.read().lower()
        self.assertNotIn("tts", src)

    def test_no_post_generation_compression_step(self):
        with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_only = "\n".join(l.split("#", 1)[0] for l in lines if not l.strip().startswith("#"))
        for forbidden in ["summarize", "summarise", "compress_article"]:
            self.assertNotIn(forbidden, code_only.lower())

    def test_old_editorial_pipeline_not_imported(self):
        with open("er002_ja_web_research_r4.py", encoding="utf-8") as f:
            import_lines = [l for l in f.readlines() if l.strip().startswith(("import", "from"))]
        forbidden = ["er002_editorial_common", "er002_editorial_angle_adapter", "er002_editorial_runner"]
        for line in import_lines:
            for fb in forbidden:
                self.assertNotIn(fb, line)

    def test_no_structured_output_used_for_writer_body(self):
        writer_src = inspect.getsource(r3.make_writer_research_fn)
        self.assertNotIn('"text":', writer_src)
        self.assertNotIn("text={", writer_src)


if __name__ == "__main__":
    unittest.main()
