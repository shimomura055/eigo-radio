# ============================================================
# er003_test_b1_p3r_audio.py
# ER-003-B1-P3R: A01 Preview+B1本文 通し音声プロトタイプのテスト
# ============================================================
# 実API・実TTSは一切行わない。すべてモック・既存成果物の読み込みのみ。
# 共有コード(er002_common/er002_gemini_client)は変更していないため、
# 本ファイルは新規追加分(source読み込み・markdown→script変換・
# TTS instruction再利用の確認)だけに絞る(大規模なテスト追加はしない)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_b1_p3r_audio -v

import json
import tempfile
import unittest

import er002_common as common
import er003_b1_p3r_audio as p3r

GOOD_B1_MARKDOWN = (
    "# Five Minutes from the Final—Then the Champions Struck\n\n"
    "On July 15, 2026, England and Argentina met in Atlanta.\n\n"
    "Neither team had a shot on target before the break.\n\n"
    "**England 1–2 Argentina**\n\n"
    "## Today's Match-Turning Points\n\n"
    "### Point One: Messi Created the Goals Instead of Scoring\n\n"
    "At 39, the Argentina captain made two assists.\n\n"
    "He did not take either of the final shots.\n\n"
    "### Point Two: England Defended, While Argentina Attacked\n\n"
    "England took off players including Rice.\n\n"
    "Lautaro later scored the winning goal.\n\n"
    "## In One Line\n\n"
    "\"England tried to close the door to the final.\"\n\n"
    "Argentina will now face Spain."
)


class PatternALoaderTests(unittest.TestCase):

    def _write_preview_json(self, patterns):
        f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
        json.dump({"patterns": patterns}, f, ensure_ascii=False)
        f.close()
        return f.name

    def test_extracts_pattern_a_text_only(self):
        path = self._write_preview_json([
            {"pattern_id": "A", "text": "PATTERN_A_TEXT", "used_forms": []},
            {"pattern_id": "B", "text": "PATTERN_B_TEXT", "used_forms": []},
            {"pattern_id": "C", "text": "PATTERN_C_TEXT", "used_forms": []},
        ])
        text = p3r.load_pattern_a_text(path)
        self.assertEqual(text, "PATTERN_A_TEXT")

    def test_raises_if_pattern_a_missing(self):
        path = self._write_preview_json([
            {"pattern_id": "B", "text": "PATTERN_B_TEXT", "used_forms": []},
            {"pattern_id": "C", "text": "PATTERN_C_TEXT", "used_forms": []},
        ])
        with self.assertRaises(ValueError):
            p3r.load_pattern_a_text(path)

    def test_real_pattern_a_source_loads(self):
        text = p3r.load_pattern_a_text()
        self.assertTrue(text.strip())
        self.assertIn("shot on target", text)


class B1ArticleLoaderTests(unittest.TestCase):

    def test_real_b1_article_loads(self):
        text = p3r.load_b1_article_text()
        self.assertTrue(text.strip())
        self.assertIn("Point One:", text)
        self.assertIn("Point Two:", text)
        self.assertIn("In One Line", text)


class MarkdownToScriptParserTests(unittest.TestCase):

    def test_parses_title_and_body(self):
        script = p3r.parse_b1_markdown_to_script(GOOD_B1_MARKDOWN)
        self.assertEqual(script["title"], "Five Minutes from the Final—Then the Champions Struck")
        body_paragraphs = script["sections"][0]["paragraphs"]
        self.assertIn("On July 15, 2026, England and Argentina met in Atlanta.", body_paragraphs)
        # ** markers are removed, but the literal score text is preserved (no deletion of content)
        self.assertIn("England 1–2 Argentina", body_paragraphs)
        self.assertNotIn("**England 1–2 Argentina**", body_paragraphs)

    def test_parses_points_section_and_subsections(self):
        script = p3r.parse_b1_markdown_to_script(GOOD_B1_MARKDOWN)
        points = script["sections"][1]
        self.assertEqual(points["heading"], "Today's Match-Turning Points")
        self.assertEqual(len(points["subsections"]), 2)
        self.assertEqual(points["subsections"][0]["heading"], "Messi Created the Goals Instead of Scoring")
        self.assertEqual(points["subsections"][1]["heading"], "England Defended, While Argentina Attacked")
        self.assertIn("At 39, the Argentina captain made two assists.", points["subsections"][0]["paragraphs"])
        self.assertIn("Lautaro later scored the winning goal.", points["subsections"][1]["paragraphs"])

    def test_parses_in_one_line_section(self):
        script = p3r.parse_b1_markdown_to_script(GOOD_B1_MARKDOWN)
        final = script["sections"][2]
        self.assertEqual(final["heading"], "In One Line")
        self.assertTrue(any("close the door to the final" in p for p in final["paragraphs"]))

    def test_output_is_valid_for_build_narration_plan(self):
        """er002_common.build_narration_plan(既存実装)がそのまま受理
        できることの直接検証(新しい台本schemaを作っていない)。"""
        script = p3r.parse_b1_markdown_to_script(GOOD_B1_MARKDOWN)
        plan = common.build_narration_plan(script)
        self.assertEqual(len(plan.chunks), 3)
        self.assertEqual(plan.chunks[0][0], "body")
        self.assertEqual(plan.chunks[1][0], "Today's Match-Turning Points")
        self.assertEqual(plan.chunks[2][0], "In One Line")

    def test_no_content_added_or_removed_beyond_markdown_symbols(self):
        """すべての本文段落が、Markdown記号を除いて元のtextに含まれる
        ことを確認する(要約・追加をしていない)。"""
        script = p3r.parse_b1_markdown_to_script(GOOD_B1_MARKDOWN)
        all_paragraphs = (
            script["sections"][0]["paragraphs"]
            + script["sections"][1]["subsections"][0]["paragraphs"]
            + script["sections"][1]["subsections"][1]["paragraphs"]
            + script["sections"][2]["paragraphs"]
        )
        for para in all_paragraphs:
            self.assertIn(para.replace("\"", "").strip('"'), GOOD_B1_MARKDOWN.replace("**", ""))

    def test_missing_point_two_raises(self):
        broken = GOOD_B1_MARKDOWN.replace(
            "### Point Two: England Defended, While Argentina Attacked\n\n"
            "England took off players including Rice.\n\n"
            "Lautaro later scored the winning goal.\n\n", "")
        with self.assertRaises(ValueError):
            p3r.parse_b1_markdown_to_script(broken)

    def test_real_b1_article_parses_successfully(self):
        text = p3r.load_b1_article_text()
        script = p3r.parse_b1_markdown_to_script(text)
        self.assertTrue(script["title"])
        self.assertEqual(len(script["sections"]), 3)
        self.assertEqual(len(script["sections"][1]["subsections"]), 2)
        plan = common.build_narration_plan(script)
        self.assertEqual(len(plan.chunks), 3)


class StyleReuseTests(unittest.TestCase):

    def test_style_prefix_is_common_module_output(self):
        self.assertEqual(p3r.build_style_prefix(), common.build_style_prefix())

    def test_style_prefix_has_no_wpm_or_genre_leakage(self):
        """採用済みinstructionをそのまま使っており、新しい指示を追加
        していないことの間接検証(既存assertがそのまま通ることを確認)。"""
        prefix = p3r.build_style_prefix()
        common.assert_no_wpm_specification(prefix)
        common.assert_no_genre_leakage(prefix)

    def test_build_tts_prompt_prepends_style_prefix(self):
        prompt = p3r.build_tts_prompt("BODY_TEXT_MARKER", style_prefix="PREFIX_")
        self.assertEqual(prompt, "PREFIX_BODY_TEXT_MARKER")

    def test_build_tts_prompt_defaults_to_common_style_prefix(self):
        prompt = p3r.build_tts_prompt("BODY_TEXT_MARKER")
        self.assertTrue(prompt.startswith(common.build_style_prefix()))

    def test_voice_name_is_aoede(self):
        self.assertEqual(p3r.VOICE_NAME, "Aoede")

    def test_no_new_retry_gate_beyond_technical_retry_constant(self):
        """品質評価を理由とした自動再生成の仕組み(QA関連関数)を、この
        モジュールが新規に持たないことを確認する。"""
        for name in ("evaluate_qa_for_audio", "run_tts_content_attempts", "call_qa_with_retry"):
            self.assertFalse(hasattr(p3r, name), msg=name)

    def test_max_technical_retry_is_1(self):
        self.assertEqual(p3r.MAX_TTS_TECHNICAL_RETRY, 1)


if __name__ == "__main__":
    unittest.main()
