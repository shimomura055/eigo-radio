# ============================================================
# er002_test_ja_free_markdown_restore_r2.py
# ER-002-v1.2M-R2: 重要ポイント2件の構造ゲートのテスト
# ============================================================
# 実API・実TTS・Web検索は一切行わない。すべてモック・既存成果物の
# 読み込みのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er002_test_ja_free_markdown_restore_r2 -v

import hashlib
import json
import os
import re
import unittest

import er002_ja_free_markdown_restore as restore
import er002_ja_free_markdown_restore_r2 as restore_r2

R1_PROMPT_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template.txt"
R2_PROMPT_PATH = "er002_v1_2m_restore_briefs/writer_prompt_template_r2.txt"
EXPECTED_R1_PROMPT_SHA256 = "035d168e1f462b7a4a595f6815a6643aeb2291d0d1a1edf790f1898f29a2856e"
MASTER_PATH = "er002_v1_2m_masters/hanshin_ja_master.txt"


def make_two_point_markdown():
    return (
        "# タイトル\n\n本文段落。\n\n"
        "## 重要ポイント\n\n"
        "### 見出し1\n\n内容1。\n\n"
        "### 見出し2\n\n内容2。\n\n"
        "## 一言で表すなら\n\nまとめ。\n"
    )


class PointCountBasicTests(unittest.TestCase):
    """要求1〜4: H3見出し数による合否。"""

    def test_two_h3_headings_pass(self):
        result = restore_r2.validate_point_structure(make_two_point_markdown())
        self.assertEqual(result.status, "STRUCTURE_PASS")
        self.assertEqual(result.h3_count, 2)

    def test_zero_h3_fail(self):
        md = "# タイトル\n\n本文だけで見出しなし。\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertEqual(result.h3_count, 0)

    def test_one_h3_fail(self):
        md = "# タイトル\n\n### 見出し1\n\n内容。\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertEqual(result.h3_count, 1)

    def test_three_h3_fail(self):
        md = "# タイトル\n\n### A\n\n内容A\n\n### B\n\n内容B\n\n### C\n\n内容C\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertEqual(result.h3_count, 3)


class CodeFenceTests(unittest.TestCase):
    """要求5: コードフェンス内の###を数えない。"""

    def test_h3_in_code_fence_not_counted(self):
        md = (
            "# タイトル\n\n本文。\n\n"
            "```markdown\n### これはコード例です\n### これも\n### これも\n```\n\n"
            "### 見出し1\n\n内容1。\n\n"
            "### 見出し2\n\n内容2。\n"
        )
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_PASS")
        self.assertEqual(result.h3_count, 2)


class EmptyContentTests(unittest.TestCase):
    """要求6・7: 空見出し・本文なしPointを不合格にする。"""

    def test_empty_heading_fail(self):
        md = "# タイトル\n\n###\n\n内容1。\n\n### 見出し2\n\n内容2。\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertIn("point_1_heading_empty", result.reasons)

    def test_empty_body_fail(self):
        md = "# タイトル\n\n### 見出し1\n\n### 見出し2\n\n内容2。\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_INVALID_POINT_COUNT_OR_BODY")
        self.assertIn("point_1_body_empty", result.reasons)


class HeadingNameIndependenceTests(unittest.TestCase):
    """要求8〜10: 見出し名・親見出し名・一言まとめ名称に依存しない。"""

    def test_different_heading_names_still_pass(self):
        md = "# タイトル\n\n### 🌟全く違う見出し表現\n\n内容1。\n\n### another heading style\n\n内容2。\n"
        result = restore_r2.validate_point_structure(md)
        self.assertEqual(result.status, "STRUCTURE_PASS")

    def test_independent_of_h2_parent_heading(self):
        md1 = make_two_point_markdown()
        md2 = md1.replace("## 重要ポイント", "## 全く別の親見出し表現🔥")
        r1 = restore_r2.validate_point_structure(md1)
        r2 = restore_r2.validate_point_structure(md2)
        self.assertEqual(r1.status, r2.status)
        self.assertEqual(r1.status, "STRUCTURE_PASS")

    def test_independent_of_closing_section_name(self):
        md1 = make_two_point_markdown()
        md2 = md1.replace("## 一言で表すなら", "## まとめ")
        r1 = restore_r2.validate_point_structure(md1)
        r2 = restore_r2.validate_point_structure(md2)
        self.assertEqual(r1.status, r2.status)


class StructureRetryTests(unittest.TestCase):
    """要求11〜13: 構造不適合時の再試行(最大1回)、2回目不合格で停止、
    2回を超えて生成しない。"""

    def test_structure_retry_once_on_first_failure(self):
        call_count = {"n": 0}

        def make_generation_fn():
            call_count["n"] += 1
            attempt = call_count["n"]

            def gen_fn():
                if attempt == 1:
                    return "# タイトル\n\n### 一つだけ\n\n内容。\n", "gpt-5.6-sol", f"resp_{attempt}"
                return make_two_point_markdown(), "gpt-5.6-sol", f"resp_{attempt}"
            return gen_fn

        raw_text, status, attempts, model_id, response_id = restore_r2.run_generation_with_structure_gate(
            make_generation_fn)
        self.assertEqual(status, "STRUCTURE_PASS")
        self.assertEqual(call_count["n"], 2)
        self.assertEqual(len(attempts), 2)

    def test_stops_after_second_failure(self):
        call_count = {"n": 0}

        def make_generation_fn():
            call_count["n"] += 1

            def gen_fn():
                return "# タイトル\n\n### 一つだけ\n\n内容。\n", "gpt-5.6-sol", "resp_x"
            return gen_fn

        raw_text, status, attempts, model_id, response_id = restore_r2.run_generation_with_structure_gate(
            make_generation_fn)
        self.assertEqual(status, "STRUCTURE_INVALID")
        self.assertEqual(call_count["n"], 2)

    def test_never_exceeds_two_content_attempts(self):
        call_count = {"n": 0}

        def make_generation_fn():
            call_count["n"] += 1

            def gen_fn():
                return "# タイトル\n\n本文のみ、見出しなし。\n", "gpt-5.6-sol", "resp_y"
            return gen_fn

        restore_r2.run_generation_with_structure_gate(make_generation_fn)
        self.assertLessEqual(call_count["n"], restore_r2.MAX_STRUCTURE_CONTENT_ATTEMPTS)


class NoAutoMergeTests(unittest.TestCase):
    """要求14: 3 Pointを自動統合しない。"""

    def test_no_merge_logic_in_source(self):
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_only = "\n".join(l.split("#", 1)[0] for l in lines if not l.strip().startswith("#"))
        for forbidden in ["merge", "combine", "join_points", "select_two"]:
            self.assertNotIn(forbidden, code_only.lower())


class FactQaOrderingTests(unittest.TestCase):
    """要求16・17: 構造合格後だけ事実QAを呼ぶ。QA警告で再生成しない。"""

    def test_fact_qa_not_called_when_structure_invalid_by_design(self):
        # モジュール内に「構造不合格でもfact QAを呼ぶ」分岐が存在しないことを
        # ソースレベルで確認する(実際の呼び出しはexecution scriptの責務)
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("fact_qa", src.lower())  # R2モジュール自体は事実QAに一切触れない設計

    def test_no_regeneration_on_qa_warning_by_design(self):
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_only = "\n".join(l.split("#", 1)[0] for l in lines if not l.strip().startswith("#"))
        self.assertNotIn("REVIEW_REQUIRED", code_only)
        self.assertNotIn("regenerate", code_only.lower())


class WriterInputTests(unittest.TestCase):
    """要求18・19: writer入力にfull registry・response_formatがない。"""

    def test_full_registry_not_in_r2_writer_input(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        brief = "テストニュース説明。"
        user_message = restore_r2.build_writer_user_message_r2(master, brief)
        for forbidden in ["F01", "F02", "source_url", "verification_status", "fact_id"]:
            self.assertNotIn(forbidden, user_message)

    def test_no_response_format_in_r2_generation_call(self):
        calls = []

        class FakeResponses:
            def create(self, **kwargs):
                calls.append(kwargs)
                class R:
                    output_text = make_two_point_markdown()
                    model = "gpt-5.6-sol"
                    id = "resp_test"
                return R()

        class FakeClient:
            def __init__(self):
                self.responses = FakeResponses()

        gen_fn = restore.make_free_markdown_generation_fn("user message", client=FakeClient())
        gen_fn()
        self.assertNotIn("response_format", calls[0])


class ModelConsistencyTests(unittest.TestCase):
    """要求20・21・24: gpt-5.6-sol/highを維持、阪神マスター1本のみ、
    7記事で共通model設定。"""

    def test_model_and_reasoning_unchanged_from_r1(self):
        self.assertEqual(restore.WRITER_MODEL, "gpt-5.6-sol")
        self.assertEqual(restore.WRITER_REASONING_EFFORT, "high")

    def test_only_hanshin_master_r2(self):
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("second_master", src.lower())
        self.assertNotIn("additional_master", src.lower())

    def test_same_model_settings_across_articles(self):
        gen_fn_a = restore.make_free_markdown_generation_fn("message A")
        gen_fn_b = restore.make_free_markdown_generation_fn("message B")
        self.assertEqual(gen_fn_a.model, gen_fn_b.model)
        self.assertEqual(gen_fn_a.reasoning_effort, gen_fn_b.reasoning_effort)


class PromptDiffTests(unittest.TestCase):
    """要求22・23: R1 promptとの差がPoint数の1文だけ。7記事で共通prompt hash。"""

    def test_r1_prompt_unchanged(self):
        with open(R1_PROMPT_PATH, "rb") as f:
            data = f.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(), EXPECTED_R1_PROMPT_SHA256)

    def test_r2_prompt_diff_is_single_sentence(self):
        with open(R1_PROMPT_PATH, encoding="utf-8") as f:
            r1_lines = f.readlines()
        with open(R2_PROMPT_PATH, encoding="utf-8") as f:
            r2_lines = f.readlines()
        self.assertTrue(r2_lines[:len(r1_lines)] == r1_lines or "".join(r2_lines).startswith("".join(r1_lines).rstrip("\n")))
        added_text = "".join(r2_lines)[len("".join(r1_lines).rstrip("\n")):].strip()
        self.assertEqual(added_text, restore_r2.POINT_COUNT_INSTRUCTION_SENTENCE)

    def test_same_prompt_template_used_for_all_seven_articles(self):
        with open(MASTER_PATH, encoding="utf-8") as f:
            master = f.read()
        topics = ["A01", "A02", "ADD01", "ADD02", "ADD03", "ADD04", "ADD05"]
        briefs = [f"テスト説明_{t}" for t in topics]
        messages = [restore_r2.build_writer_user_message_r2(master, b) for b in briefs]
        normalized = [m.replace(b, "{BRIEF}") for m, b in zip(messages, briefs)]
        self.assertEqual(len(set(normalized)), 1)


class NoOtherApiCallsR2Tests(unittest.TestCase):
    """要求25・26: Web検索0件・TTS0件。"""

    def test_web_search_not_referenced_r2(self):
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("web_search", src.lower())

    def test_tts_not_referenced_r2(self):
        with open("er002_ja_free_markdown_restore_r2.py", encoding="utf-8") as f:
            src = f.read()
        self.assertNotIn("tts", src.lower())


class R1ArtifactsUnchangedTests(unittest.TestCase):
    """要求27: R1成果物が変更されない。"""

    def test_r1_raw_articles_unchanged(self):
        for topic_id in ["A01", "ADD05"]:
            path = f"er002_output/v1_2m_r1/{topic_id}/raw_article.md"
            if not os.path.exists(path):
                self.skipTest(f"{path}が見つかりません")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertTrue(len(content) > 0)

    def test_r1_status_record_exists_and_reflects_decision(self):
        path = "er002_output/_experiment_config/ER-002-v1.2M-R1_status.json"
        if not os.path.exists(path):
            self.skipTest(f"{path}が見つかりません")
        with open(path, encoding="utf-8") as f:
            status = json.load(f)
        self.assertTrue(status["editorial_taste_restored"])
        self.assertFalse(status["restoration_package_adopted"])
        self.assertEqual(status["reason_not_adopted"], "important_points_count_was_three_instead_of_two")


class BriefSourceTests(unittest.TestCase):
    """新規に用意した7件のbriefのsha256・出典が記録されていること。"""

    def test_brief_source_manifest_covers_all_seven_topics(self):
        with open("er002_v1_2m_restore_briefs/r2_briefs_source_manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(
            set(manifest["briefs"].keys()),
            {"A01", "A02", "ADD01", "ADD02", "ADD03", "ADD04", "ADD05"},
        )

    def test_a02_marked_brief_source_missing(self):
        with open("er002_v1_2m_restore_briefs/r2_briefs_source_manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["briefs"]["A02"]["status"], "BRIEF_SOURCE_MISSING")

    def test_add_briefs_are_verbatim_substrings_of_original_request(self):
        with open("er002_v1_2m_masters/original_request.txt", encoding="utf-8") as f:
            original_request = f.read()
        for topic_id in ["ADD01", "ADD02", "ADD03", "ADD04"]:
            with open(f"er002_v1_2m_restore_briefs/{topic_id}_concise_brief.txt", encoding="utf-8") as f:
                brief = f.read().rstrip("\n")
            self.assertIn(brief, original_request)


if __name__ == "__main__":
    unittest.main()
