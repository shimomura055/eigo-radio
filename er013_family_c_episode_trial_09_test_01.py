# ============================================================
# er013_family_c_episode_trial_09_test_01.py
# 管理ID: EDITORIAL-FUTURE-FAMILY-C-HOME-ROBOTS-EPISODE-SPEC-TRIAL-09
# ============================================================
# 決定的テスト(API不要、¥0)。er013_family_c_episode_trial_09_run.pyの
# normalization/segment分割/UI表示文変換が、本文の語・語順を一切変えず、
# 再結合で元の本文へ完全一致復元できることを検証する。
# run_project_regression.py(unittest.TestLoader().discover()、
# pattern="er0*_test_*.py")から自動収集される想定のため、unittest.TestCase
# を使う(pytest未インストールのプロジェクト規約に合わせる)。
from __future__ import annotations

import re
import unittest

import er013_family_c_episode_trial_09_run as run_mod


ARTICLE_TEXT = run_mod.load_article_text()
PARAGRAPHS = run_mod.split_into_paragraphs(ARTICLE_TEXT)


def _word_tokens(text: str) -> list:
    """語(word)集合・順序比較用。記号・空白の正規化差(curly quote vs
    straight quote、Markdown太字記号、連続空白)を無視し、英数字/日本語
    トークンの並びだけを比較する。"""
    cleaned = text.replace("“", '"').replace("”", '"')
    cleaned = cleaned.replace("‘", "'").replace("’", "'")
    cleaned = cleaned.replace("**", "")
    return re.findall(r"[A-Za-z']+|[0-9]+|[^\sA-Za-z0-9'\"]", cleaned)


class TestArticleStructure(unittest.TestCase):
    def test_paragraph_count(self):
        self.assertEqual(len(PARAGRAPHS), 34)

    def test_paragraph_reconstruction(self):
        self.assertEqual("\n\n".join(PARAGRAPHS), ARTICLE_TEXT)


class TestNormalizeForTts(unittest.TestCase):
    def test_normalization_does_not_change_word_tokens(self):
        for para in PARAGRAPHS:
            normalized = run_mod.normalize_for_tts(para)
            self.assertEqual(_word_tokens(normalized), _word_tokens(para),
                              f"normalize_for_tts changed word tokens for: {para!r}")

    def test_normalization_collapses_whitespace_and_removes_markup(self):
        ui_para = PARAGRAPHS[run_mod.UI_PARAGRAPH_INDEX]
        normalized = run_mod.normalize_for_tts(ui_para)
        self.assertNotIn("**", normalized)
        self.assertNotIn("\n", normalized)
        self.assertNotIn("  ", normalized)
        self.assertEqual(normalized,
                          "CARE HOUSE: more sleep for Maya. HOME: more time with her mother.")

    def test_normalization_converts_curly_quotes_to_straight(self):
        para = PARAGRAPHS[3]
        normalized = run_mod.normalize_for_tts(para)
        self.assertNotIn("“", normalized)
        self.assertNotIn("”", normalized)
        self.assertIn('"', normalized)


class TestQuoteSplitting(unittest.TestCase):
    def test_split_reconstructs_paragraph_exactly(self):
        for idx in run_mod.ROBOT_QUOTE_PARAGRAPH_INDICES:
            para = PARAGRAPHS[idx]
            chunks = run_mod.split_paragraph_by_quotes(para)
            self.assertEqual("".join(text for _, text in chunks), para)

    def test_robot_paragraphs_contain_exactly_expected_robot_quote_count(self):
        expected_robot_chunk_counts = {3: 2, 6: 2, 16: 1, 18: 1}
        for idx, expected_count in expected_robot_chunk_counts.items():
            chunks = run_mod.split_paragraph_by_quotes(PARAGRAPHS[idx])
            robot_chunks = [c for v, c in chunks if v == "robot"]
            self.assertEqual(len(robot_chunks), expected_count,
                              f"paragraph {idx}: expected {expected_count} robot chunks, "
                              f"got {len(robot_chunks)}: {robot_chunks!r}")

    def test_non_robot_paragraphs_are_untouched_by_split_logic(self):
        # human dialogue (Maya/mother)を含む段落は、本Trialのvoice設計上
        # split対象ではない(ROBOT_QUOTE_PARAGRAPH_INDICES外)ことを確認する。
        human_dialogue_paragraph_indices = [11, 15, 22, 24, 27, 31]  # mother/Maya's quoted lines
        for idx in human_dialogue_paragraph_indices:
            self.assertNotIn(idx, run_mod.ROBOT_QUOTE_PARAGRAPH_INDICES)
            self.assertIn("“", PARAGRAPHS[idx])  # 引用符自体は含むが分割対象外


class TestStorySegmentPlanCoverage(unittest.TestCase):
    def test_plan_covers_all_paragraphs_exactly_once(self):
        covered = []
        for kind, arg in run_mod.STORY_SEGMENT_PLAN:
            if kind == "merge":
                covered.extend(arg)
            else:
                covered.append(arg)
        self.assertEqual(sorted(covered), list(range(34)))
        self.assertEqual(len(covered), len(set(covered)), "duplicate paragraph index in plan")

    def test_plan_ranges_are_contiguous_for_merge_entries(self):
        for kind, arg in run_mod.STORY_SEGMENT_PLAN:
            if kind == "merge" and len(arg) > 1:
                self.assertEqual(arg, list(range(arg[0], arg[-1] + 1)),
                                  f"non-contiguous merge group: {arg}")


class TestBuildAllStorySegments(unittest.TestCase):
    def setUp(self):
        self.segments = run_mod.build_all_story_segments(PARAGRAPHS)

    def test_reconstruction_matches_original_article_exactly(self):
        reconstructed = run_mod.reconstruct_article_from_story_segments(self.segments, len(PARAGRAPHS))
        self.assertEqual(reconstructed, ARTICLE_TEXT)

    def test_all_segments_have_non_empty_tts_text(self):
        for seg in self.segments:
            self.assertNotEqual(seg["tts_text"].strip(), "", f"segment {seg['id']} has empty tts_text")

    def test_segment_ids_are_unique_and_sequential(self):
        ids = [seg["id"] for seg in self.segments]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))

    def test_ui_paragraph_segment_is_robot_voice(self):
        ui_segments = [s for s in self.segments
                       if s["source_paragraph_indices"] == [run_mod.UI_PARAGRAPH_INDEX]]
        self.assertEqual(len(ui_segments), 1)
        self.assertEqual(ui_segments[0]["voice"], "robot")
        self.assertEqual(ui_segments[0]["tts_text"],
                          "CARE HOUSE: more sleep for Maya. HOME: more time with her mother.")

    def test_robot_voice_segment_count_matches_manual_story_read(self):
        # 本文を通読して特定したロボット直接発話は6箇所(7行目に2箇所、
        # 13行目に2箇所、34行目に1箇所、38行目に1箇所)+ UI表示文1箇所
        # (壁に表示される2行、システム/ロボットvoiceとして読む方式を採用)。
        robot_segments = [s for s in self.segments if s["voice"] == "robot"]
        self.assertEqual(len(robot_segments), 7)

    def test_narrator_voice_used_for_human_dialogue(self):
        # Maya/motherの発話を含む段落は、narrator voiceのsegmentへ含まれた
        # ままであること(2-voice設計、robot以外は全てnarrator)。
        mother_line_segment = [s for s in self.segments
                                if any(idx == 11 for idx in s["source_paragraph_indices"])]
        self.assertEqual(len(mother_line_segment), 1)
        self.assertEqual(mother_line_segment[0]["voice"], "narrator")
        self.assertIn("My doctor says I cannot live alone now", mother_line_segment[0]["raw_text"])

    def test_word_tokens_preserved_end_to_end(self):
        # segment化(merge/split)全体を通しても、記事全体の語トークン集合・
        # 順序が変わらないこと(意味を変えるsegment化になっていないことの
        # 決定的確認)。tts_safe_time_reading_en()による"7:00"→"seven"の
        # 意図的な安全変換(TestTtsSafeTimeReadingで別途検証)のみ、記事
        # 側にも同じ変換を適用したうえで比較する(それ以外の差分が無い
        # ことを確認する目的の比較であり、時刻の読み替えは対象外とする)。
        all_tts_text = " ".join(seg["tts_text"] for seg in self.segments)
        expected = run_mod.tts_safe_time_reading_en(ARTICLE_TEXT)
        self.assertEqual(_word_tokens(all_tts_text), _word_tokens(expected))


class TestTtsSafeTimeReading(unittest.TestCase):
    def test_converts_hhmm_zero_minutes_to_spoken_hour_word(self):
        self.assertEqual(run_mod.tts_safe_time_reading_en("At 7:00, Maya woke up."),
                          "At seven, Maya woke up.")

    def test_does_not_affect_text_without_time_expressions(self):
        for para in PARAGRAPHS:
            if "7:00" not in para:
                self.assertEqual(run_mod.tts_safe_time_reading_en(para), para)

    def test_article_contains_exactly_one_digit_expression(self):
        # 本文中で唯一の数字表記であることを再確認する(この安全変換が
        # 本文の他の箇所へ意図せず波及しないことの裏付け)。
        digit_matches = re.findall(r"\d+[:\d]*", ARTICLE_TEXT)
        self.assertEqual(digit_matches, ["7:00"])


class TestSupportMarkerInsertion(unittest.TestCase):
    def test_support_markers_present_and_positioned_correctly(self):
        segments = run_mod.build_story_segments_with_support_markers(PARAGRAPHS)
        marker_ids = [s["id"] for s in segments if s.get("marker")]
        self.assertEqual(marker_ids, ["__support_1__", "__support_2__"])
        self.assertEqual(segments[-1]["id"], "__support_2__")

        support_1_pos = [i for i, s in enumerate(segments) if s["id"] == "__support_1__"][0]
        preceding = segments[support_1_pos - 1]
        # support_1の直前segmentは、転換点(mother来訪)より前の最後の
        # narrator merge segment(paragraphs 7,8,9)であること。
        self.assertEqual(preceding["source_paragraph_indices"], [7, 8, 9])
        following = segments[support_1_pos + 1]
        self.assertEqual(following["source_paragraph_indices"], [10, 11, 12, 13])


if __name__ == "__main__":
    unittest.main()
