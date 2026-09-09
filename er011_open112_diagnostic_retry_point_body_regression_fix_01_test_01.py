#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPEN-112-DIAGNOSTIC-RETRY-POINT-BODY-REGRESSION-FIX-01

回帰テスト: `er009_diagnostic_full_retry_modules_12.py::build_diagnostic_
section()` が、ハードコードされたプレースホルダー文字列
"(Point One body from previous attempt)" / "(Point Two body from previous
attempt)" ではなく、実際の前回Point One/Two本文を診断promptへ埋め込む
ことを固定する(FAMILY-A-POINT-OVERLAP-GAP-FIX-TRIAL-05のReconciliation
Checkが発見した実装漏れへの回帰修正)。

対象:
1. `build_diagnostic_section()` 単体 -- 実本文がsectionに含まれ、
   プレースホルダー文字列が一切残らないこと。
2. `build_diagnostic_section()` -- Point本文が空文字列のケースでも
   例外を投げず、空のまま埋め込まれること(既存プレースホルダーへの
   フォールバックを行わないことの確認)。
3. `er003_v1_n3_01_articles_generate.py::build_diagnostic_retry_prompt()`
   (Production呼び出し元) -- `split_common_sections_for_point_qa()`が
   抽出した実際のPoint One/Two本文が、最終的なretry promptへ実際に
   含まれること(呼び出し元の配線漏れ自体の回帰防止)。

API呼び出し無し(すべてtext処理のみ)。
"""

from __future__ import annotations

import unittest

import er003_v1_n3_01_articles_generate as gen
import er008_point_overlap_qa_18 as overlap_qa
import er009_diagnostic_full_retry_modules_12 as diagnostic_mod

OLD_PLACEHOLDER_P1 = "(Point One body from previous attempt)"
OLD_PLACEHOLDER_P2 = "(Point Two body from previous attempt)"


class TestBuildDiagnosticSectionEmbedsRealPointBody(unittest.TestCase):
    """build_diagnostic_section()が実際のPoint本文を埋め込み、旧
    プレースホルダー文字列が出力に残らないことを確認する。"""

    def setUp(self):
        self.full_story = (
            "Research shows that tipping screens increase customer tip amounts. A study found "
            "that higher default suggestions led to more tipping."
        )
        self.point_one_text = "UNIQUE_MARKER_POINT_ONE_BODY_TEXT_ABC123"
        self.point_two_text = "UNIQUE_MARKER_POINT_TWO_BODY_TEXT_XYZ789"
        self.o1 = overlap_qa.flag_possible_paraphrase(self.point_one_text, self.full_story)
        self.o2 = overlap_qa.flag_possible_paraphrase(self.point_two_text, self.full_story)

    def test_real_point_body_text_is_embedded(self):
        section, diag_dict = diagnostic_mod.build_diagnostic_section(
            self.full_story, self.o1, self.o2, self.point_one_text, self.point_two_text,
        )
        self.assertIn(self.point_one_text, section)
        self.assertIn(self.point_two_text, section)
        self.assertIn("diagnosis_one", diag_dict)
        self.assertIn("diagnosis_two", diag_dict)

    def test_old_placeholder_strings_do_not_appear(self):
        section, _ = diagnostic_mod.build_diagnostic_section(
            self.full_story, self.o1, self.o2, self.point_one_text, self.point_two_text,
        )
        self.assertNotIn(OLD_PLACEHOLDER_P1, section)
        self.assertNotIn(OLD_PLACEHOLDER_P2, section)

    def test_missing_required_arguments_raises_type_error(self):
        # 旧3引数呼び出し(previous_point_one_text/previous_point_two_text省略)は
        # 既定値へフォールバックせず、明示的にTypeErrorとなること(=暗黙の
        # プレースホルダー復活を防ぐ)。
        with self.assertRaises(TypeError):
            diagnostic_mod.build_diagnostic_section(self.full_story, self.o1, self.o2)

    def test_empty_point_body_text_does_not_crash(self):
        # 本文抽出に失敗した場合等、空文字列が渡されるケースでも例外を
        # 投げず、空のまま埋め込まれること(placeholderへのフォールバックは
        # しない、という仕様通りの挙動)。
        section, _ = diagnostic_mod.build_diagnostic_section(
            self.full_story, self.o1, self.o2, "", "",
        )
        self.assertNotIn(OLD_PLACEHOLDER_P1, section)
        self.assertNotIn(OLD_PLACEHOLDER_P2, section)
        self.assertIn("Previous Point One", section)
        self.assertIn("Previous Point Two", section)


class TestBuildDiagnosticRetryPromptWiring(unittest.TestCase):
    """Production呼び出し元 build_diagnostic_retry_prompt() が、
    split_common_sections_for_point_qa()で抽出済みのPoint One/Two本文を
    実際にbuild_diagnostic_section()へ渡していることを確認する
    (抽出はしているのに使っていない、という配線漏れの回帰防止)。"""

    def test_retry_prompt_contains_actual_point_bodies(self):
        original_prompt = "Write an article about tipping screens.\n[Instructions]"
        article_text = (
            "# Article\n\n"
            "Research shows tipping screens increase tips. Studies demonstrate this effect.\n\n"
            "### Point One\n\n"
            "UNIQUE_MARKER_PRODUCTION_POINT_ONE_TEXT_QWERTY\n\n"
            "### Point Two\n\n"
            "UNIQUE_MARKER_PRODUCTION_POINT_TWO_TEXT_ASDFGH\n\n"
            "## In one line\n\n"
            "Screens influence consumer tipping choices.\n"
        )
        point_overlap = {
            "point_one": {"overlap_ratio": 0.55, "flagged": True,
                          "shared_words": ["screens", "tip", "increase", "tips"]},
            "point_two": {"overlap_ratio": 0.20, "flagged": False,
                          "shared_words": ["screens", "pressure"]},
        }

        retry_prompt = gen.build_diagnostic_retry_prompt(original_prompt, article_text, point_overlap)

        self.assertIn("UNIQUE_MARKER_PRODUCTION_POINT_ONE_TEXT_QWERTY", retry_prompt)
        self.assertIn("UNIQUE_MARKER_PRODUCTION_POINT_TWO_TEXT_ASDFGH", retry_prompt)
        self.assertNotIn(OLD_PLACEHOLDER_P1, retry_prompt)
        self.assertNotIn(OLD_PLACEHOLDER_P2, retry_prompt)

    def test_unparseable_article_structure_falls_back_to_original_prompt(self):
        # split_common_sections_for_point_qa()がNoneを返す(想定構造でない)
        # 場合は、従来通りoriginal_promptをそのまま返す(既存挙動を維持、
        # 新しいhard failureを追加しない)。
        original_prompt = "Write an article.\n[Instructions]"
        article_text = "No structured headings here at all."
        point_overlap = {
            "point_one": {"overlap_ratio": 0.55, "flagged": True, "shared_words": []},
            "point_two": {"overlap_ratio": 0.20, "flagged": False, "shared_words": []},
        }
        retry_prompt = gen.build_diagnostic_retry_prompt(original_prompt, article_text, point_overlap)
        self.assertEqual(retry_prompt, original_prompt)


if __name__ == "__main__":
    unittest.main()
