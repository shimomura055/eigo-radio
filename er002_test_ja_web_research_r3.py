# ============================================================
# er002_test_ja_web_research_r3.py
# ER-002-v1.2M-R3: Web検索付きChatGPT自己取材・記事生成パイロットのテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_web_research_r3 -v

import inspect
import json
import os
import re
import unittest

import er002_ja_free_markdown_restore as restore
import er002_ja_web_research_r3 as r3

MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"


def make_fake_response(output_text, model="gpt-5.6-sol", response_id="resp_test",
                        search_call_count=1, queries=None, sources=None):
    queries = queries if queries is not None else ["テストクエリ"]
    sources = sources if sources is not None else [{"title": "テスト記事", "url": "https://example.com/a"}]

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

        def __init__(self, title, url):
            self.title = title
            self.url = url

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
            anns = [FakeAnnotation(s.get("title"), s.get("url")) for s in sources]
            items = []
            for _ in range(search_call_count):
                items.append(FakeWebSearchCall(queries))
            items.append(FakeMessage(anns))
            self.output = items

    return FakeResponse()


def make_two_point_markdown():
    return (
        "# タイトル\n\n本文段落。\n\n"
        "## 重要ポイント\n\n"
        "### 見出し1\n\n内容1。\n\n"
        "### 見出し2\n\n内容2。\n\n"
        "## 一言で表すなら\n\nまとめ。\n"
    )


class WriterInputCompositionTests(unittest.TestCase):
    """要求1〜4: writer入力がマスター・テーマ・自然文依頼だけで構成される。"""

    def test_writer_input_has_only_master_and_topic_placeholders(self):
        with open("er002_v1_2m_restore_briefs/writer_prompt_template_r3.txt", encoding="utf-8") as f:
            template = f.read()
        self.assertIn("{hanshin_master_full_text}", template)
        self.assertIn("{topic}", template)
        forbidden_placeholders = ["{concise_news_brief}", "{fact_registry}", "{fact_id_map}", "{brief}"]
        for p in forbidden_placeholders:
            self.assertNotIn(p, template)

    def test_no_concise_brief_in_writer_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        self.assertNotIn("concise_brief", msg.lower())

    def test_no_full_fact_registry_in_writer_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        for forbidden in ["source_url", "verification_status", "fact_registry"]:
            self.assertNotIn(forbidden, msg)

    def test_no_fact_id_in_writer_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        msg = r3.build_writer_user_message_r3(master, "テストテーマ")
        self.assertNotRegex(msg, r"\bF0[0-9]\b")


class ResponsesApiAndWebSearchTests(unittest.TestCase):
    """要求5〜7: Responses API使用、Web検索ツール有効、検索クエリ非固定。"""

    def test_writer_uses_responses_api(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return make_fake_response(make_two_point_markdown())

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        writer_fn()
        self.assertEqual(len(calls), 1)

    def test_writer_has_web_search_tool_enabled(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return make_fake_response(make_two_point_markdown())

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        writer_fn()
        self.assertIn("tools", calls[0])
        self.assertIn({"type": "web_search"}, calls[0]["tools"])

    def test_no_fixed_search_query_passed_to_api(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return make_fake_response(make_two_point_markdown())

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        writer_fn()
        tool_config = calls[0]["tools"][0]
        self.assertNotIn("query", tool_config)
        self.assertNotIn("queries", tool_config)


class WebSearchRequiredGateTests(unittest.TestCase):
    """要求8・9: Web検索未使用は不合格。再試行は最大1回。"""

    def test_zero_search_calls_marks_web_search_not_used(self):
        def make_writer_fn():
            def writer_fn():
                resp = make_fake_response(make_two_point_markdown(), search_call_count=0)
                usage = r3.extract_web_search_usage(resp)
                sources = r3.extract_sources(resp)
                return resp.output_text, resp.model, resp.id, usage, sources
            return writer_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = r3.run_writer_with_gates(
            make_writer_fn)
        self.assertEqual(status, "WRITER_WEB_SEARCH_NOT_USED")

    def test_web_search_not_used_retry_max_one(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1
            attempt = call_count["n"]

            def writer_fn():
                # 1回目は検索0件、2回目は検索1件+構造合格
                search_count = 0 if attempt == 1 else 1
                resp = make_fake_response(make_two_point_markdown(), search_call_count=search_count)
                usage = r3.extract_web_search_usage(resp)
                sources = r3.extract_sources(resp)
                return resp.output_text, resp.model, resp.id, usage, sources
            return writer_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = r3.run_writer_with_gates(
            make_writer_fn)
        self.assertEqual(status, "STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_never_exceeds_max_content_attempts(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1

            def writer_fn():
                resp = make_fake_response(make_two_point_markdown(), search_call_count=0)
                usage = r3.extract_web_search_usage(resp)
                sources = r3.extract_sources(resp)
                return resp.output_text, resp.model, resp.id, usage, sources
            return writer_fn

        r3.run_writer_with_gates(make_writer_fn)
        self.assertLessEqual(call_count["n"], r3.MAX_CONTENT_ATTEMPTS)


class SearchAndWritingSameCallTests(unittest.TestCase):
    """要求10・11: 検索と執筆が同一API実行内。別モデルによる検索結果要約工程がない。"""

    def test_search_usage_and_article_text_come_from_same_response(self):
        class FakeResponses:
            def create(self, **kwargs):
                return make_fake_response(make_two_point_markdown(), search_call_count=2)

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        text, model_id, response_id, search_usage, sources = writer_fn()
        self.assertEqual(search_usage["web_search_call_count"], 2)
        self.assertEqual(text, make_two_point_markdown())

    def test_no_separate_summarization_step_in_module(self):
        with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_only = "\n".join(l.split("#", 1)[0] for l in lines if not l.strip().startswith("#"))
        for forbidden in ["summarize", "summarise", "要約する関数"]:
            self.assertNotIn(forbidden, code_only.lower())


class WriterOutputFormatTests(unittest.TestCase):
    """要求12・13: writer出力が自由Markdown。Structured Outputがない。"""

    def test_writer_output_is_free_markdown_string(self):
        class FakeResponses:
            def create(self, **kwargs):
                return make_fake_response(make_two_point_markdown())

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        text, *_ = writer_fn()
        self.assertIsInstance(text, str)
        self.assertTrue(text.startswith("#"))

    def test_no_structured_output_for_writer_call(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return make_fake_response(make_two_point_markdown())

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        writer_fn = r3.make_writer_research_fn("user message", client=FakeClient())
        writer_fn()
        self.assertNotIn("text", calls[0])  # text.format(json_schema)はfact checker専用


class StructureGateReuseTests(unittest.TestCase):
    """要求14〜17: R2の構造ゲートを再利用。再試行は最大1回。内容不満で再生成しない。"""

    def test_two_h3_pass_via_r2_validator(self):
        import er002_ja_free_markdown_restore_r2 as restore_r2
        result = restore_r2.validate_point_structure(make_two_point_markdown())
        self.assertEqual(result.status, "STRUCTURE_PASS")

    def test_invalid_h3_counts_fail_via_r2_validator(self):
        import er002_ja_free_markdown_restore_r2 as restore_r2
        for md in [
            "# タイトル\n\n本文のみ。\n",
            "# タイトル\n\n### 一つだけ\n\n内容。\n",
            "# タイトル\n\n### A\n\n内容A\n\n### B\n\n内容B\n\n### C\n\n内容C\n",
        ]:
            result = restore_r2.validate_point_structure(md)
            self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")

    def test_structure_retry_max_one_in_gate(self):
        call_count = {"n": 0}

        def make_writer_fn():
            call_count["n"] += 1
            attempt = call_count["n"]

            def writer_fn():
                md = "# タイトル\n\n### 一つだけ\n\n内容。\n" if attempt == 1 else make_two_point_markdown()
                resp = make_fake_response(md, search_call_count=1)
                usage = r3.extract_web_search_usage(resp)
                sources = r3.extract_sources(resp)
                return resp.output_text, resp.model, resp.id, usage, sources
            return writer_fn

        raw_text, status, attempts, model_id, response_id, search_usage, sources = r3.run_writer_with_gates(
            make_writer_fn)
        self.assertEqual(status, "STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)

    def test_no_content_dissatisfaction_regeneration_by_design(self):
        # run_writer_with_gates(構造ゲート)はfact checkerのverdictを一切
        # 参照しない。再生成条件はWeb検索未使用/構造不適合の2つのみであり、
        # 内容(面白さ・事実確認結果)による再生成条件が実装されていないことを、
        # 関数のソースコードそのものから確認する。
        gate_source = inspect.getsource(r3.run_writer_with_gates)
        self.assertNotIn("verdict", gate_source.lower())
        self.assertNotIn("fact_check", gate_source.lower())
        self.assertNotIn("make_fact_checker_fn", gate_source)
        self.assertNotIn("regenerate_on_qa", gate_source.lower())
        params = list(inspect.signature(r3.run_writer_with_gates).parameters)
        self.assertNotIn("fact_check_result", params)


class FactCheckerIndependenceTests(unittest.TestCase):
    """要求18〜23: fact checkerが別API実行、Web検索有効、独立検索可能、
    面白さ非評価、記事非書き換え、QA結果で再生成しない。"""

    def test_fact_checker_is_separate_api_call_from_writer(self):
        writer_calls = []
        checker_calls = []

        class FakeResponses:
            def __init__(self, sink):
                self.sink = sink

            def create(self, **kwargs):
                self.sink.append(kwargs)
                if "text" in kwargs:
                    return make_fake_response(
                        json.dumps({"verdict": "PASS", "contradictions": [], "unsupported_specific_claims": [],
                                    "verified_claims_summary": [], "sources": [], "notes": "ok"}))
                return make_fake_response(make_two_point_markdown())

        class FakeWriterClient:
            def __init__(self):
                self.responses = FakeResponses(writer_calls)

        class FakeCheckerClient:
            def __init__(self):
                self.responses = FakeResponses(checker_calls)

        writer_fn = r3.make_writer_research_fn("writer message", client=FakeWriterClient())
        writer_fn()
        checker_fn = r3.make_fact_checker_fn("checker prompt", client=FakeCheckerClient())
        checker_fn()
        self.assertEqual(len(writer_calls), 1)
        self.assertEqual(len(checker_calls), 1)
        # 別クライアント(別実行)であり、writer呼び出し引数がchecker側に混入していない
        self.assertNotIn("text", writer_calls[0])
        self.assertIn("text", checker_calls[0])

    def test_fact_checker_has_web_search_tool(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                return make_fake_response(json.dumps(
                    {"verdict": "PASS", "contradictions": [], "unsupported_specific_claims": [],
                     "verified_claims_summary": [], "sources": [], "notes": "ok"}))

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        checker_fn = r3.make_fact_checker_fn("prompt", client=FakeClient())
        checker_fn()
        self.assertIn({"type": "web_search"}, calls[0]["tools"])

    def test_fact_checker_prompt_instructs_independent_search(self):
        prompt = r3.build_fact_check_prompt("テスト", "記事本文", [{"title": "t", "url": "http://x"}])
        self.assertIn("参照したソースだけを信用せず", prompt)

    def test_fact_checker_schema_excludes_interest_fields(self):
        props = set(r3.FACT_CHECK_JSON_SCHEMA["schema"]["properties"].keys())
        forbidden = {"interest", "narrative", "momentum", "angle", "tone_score", "listener_payoff"}
        self.assertEqual(props & forbidden, set())

    def test_fact_checker_prompt_forbids_rewriting(self):
        prompt = r3.build_fact_check_prompt("テスト", "記事本文", [])
        self.assertIn("書き直したり、修正したりしないでください", prompt)

    def test_no_regeneration_logic_tied_to_fact_check_result(self):
        with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
            src = f.read()
        # fact checkerのverdictを条件にwriterを再度呼ぶ分岐が存在しない
        self.assertNotIn("if verdict", src.lower())


class R2ArtifactsUnchangedTests(unittest.TestCase):
    """要求26: R2成果物が変更されない。"""

    def test_r2_review_markdown_still_present_and_valid(self):
        path = "er002_output/v1_2m_r2/ER-002-v1.2M-R2_user_review.md"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ADD03", content)

    def test_r2_status_record_exists(self):
        path = "er002_output/_experiment_config/ER-002-v1.2M-R2_status.json"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            status = json.load(f)
        self.assertEqual(status["two_point_structure_gate"], "PASS")
        self.assertEqual(status["user_quality_evaluation"], "BELOW_PRIOR_CHATGPT_OUTPUTS")


class SourceStorageTests(unittest.TestCase):
    """要求27・28: Webソースはタイトル・URLのみ保存。秘密情報を保存しない。"""

    def test_extract_sources_returns_only_title_and_url(self):
        resp = make_fake_response(make_two_point_markdown(), sources=[
            {"title": "記事タイトル", "url": "https://example.com/article"},
        ])
        sources = r3.extract_sources(resp)
        self.assertEqual(len(sources), 1)
        self.assertEqual(set(sources[0].keys()), {"title", "url"})

    def test_no_api_key_patterns_in_module_source(self):
        with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotRegex(src, r"sk-[a-zA-Z0-9]{10,}")
        self.assertNotRegex(src, r"AIza[a-zA-Z0-9_\-]{10,}")


class NoOtherApiCallsR3Tests(unittest.TestCase):
    """要求29・30: TTS・旧Editorial Brief工程が呼ばれない。"""

    def test_tts_not_referenced(self):
        with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("tts", src.lower())

    def test_old_editorial_pipeline_not_imported(self):
        with open("er002_ja_web_research_r3.py", encoding="utf-8") as f:
            import_lines = [l for l in f.readlines() if re.match(r"^\s*(import|from)\s", l)]
        forbidden = ["er002_editorial_common", "er002_editorial_angle_adapter", "er002_editorial_runner"]
        for line in import_lines:
            for fb in forbidden:
                self.assertNotIn(fb, line)


if __name__ == "__main__":
    unittest.main()
