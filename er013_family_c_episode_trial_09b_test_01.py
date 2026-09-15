# ============================================================
# er013_family_c_episode_trial_09b_test_01.py
# 管理ID: USER-TEST-AUDIO-HUMAN-REVIEW-FIX-02-FAMILYC
# ============================================================
# 決定的テスト(API呼び出しなし): speaker分割、Comment位置、
# player表示=canonical、file:///不在。
from __future__ import annotations

import json
import os
import unittest

import er013_family_c_episode_trial_09b_run as m


class StorySegmentSplitTests(unittest.TestCase):
    def setUp(self):
        self.article_text = m.load_article_text()
        self.paragraphs = m.split_into_paragraphs(self.article_text)
        self.segments = m.build_all_story_segments(self.paragraphs)

    def test_paragraph_count(self):
        self.assertEqual(len(self.paragraphs), 34)

    def test_reconstruction_matches_article_exactly(self):
        recon = m.reconstruct_article_from_story_segments(self.segments, len(self.paragraphs))
        self.assertEqual(recon, self.article_text)

    def test_mother_quotes_are_split_into_mother_voice(self):
        mother_segs = [s for s in self.segments if s["voice"] == "mother"]
        self.assertEqual(len(mother_segs), 3)
        texts = sorted(s["raw_text"] for s in mother_segs)
        self.assertIn("“My doctor says I cannot live alone now,”", texts)
        self.assertIn(
            "“I can move into a care house, or I can live here with you. What do you think?”",
            texts)
        self.assertIn("“What do you want, Maya?”", texts)

    def test_mother_quotes_come_only_from_paragraphs_11_and_24(self):
        for s in self.segments:
            if s["voice"] == "mother":
                self.assertEqual(s["source_paragraph_indices"], [11] if 11 in s["source_paragraph_indices"]
                                  else [24])
                self.assertIn(s["source_paragraph_indices"][0], m.MOTHER_QUOTE_PARAGRAPH_INDICES)

    def test_robot_quotes_unchanged_from_v1_paragraph_set(self):
        robot_para_indices = {idx for s in self.segments if s["voice"] == "robot"
                               for idx in s["source_paragraph_indices"]}
        self.assertEqual(robot_para_indices, m.ROBOT_QUOTE_PARAGRAPH_INDICES | {m.UI_PARAGRAPH_INDEX})

    def test_maya_dialogue_stays_narrator(self):
        # "Turn everything off," she said. と "Mother," she said, "come in." は
        # Mayaの台詞であり、narrator(Aoede)のまま分離しない(speaker_map.jsonの
        # 明示的な設計判断どおり)。
        combined = " ".join(s["raw_text"] for s in self.segments if s["voice"] == "narrator")
        self.assertIn("Turn everything off", combined)
        self.assertIn("come in", combined)

    def test_no_new_words_introduced_by_normalization(self):
        for s in self.segments:
            raw_words = m.normalize_for_tts(s["raw_text"]).split()
            tts_words_without_time_fix = raw_words  # tts_safe_time_reading_enは"7:00"のみ対象
            # tts_textの語数は正規化+時刻読み修正のみが差分(語の追加・削除がないこと)
            self.assertGreaterEqual(len(s["tts_text"].split()), len(raw_words) - 1)
            self.assertLessEqual(len(s["tts_text"].split()), len(raw_words) + 1)


class PlanStructureTests(unittest.TestCase):
    def setUp(self):
        self.article_text = m.load_article_text()
        self.paragraphs = m.split_into_paragraphs(self.article_text)
        self.segments = m.build_all_story_segments(self.paragraphs)
        self.segs_by_plan = {}
        for s in self.segments:
            self.segs_by_plan.setdefault(s["plan_index"], []).append(s)

    def test_comment_2_boundary_matches_v1_story_009_010(self):
        # v1のstory_009/010境界(段落9/10境界)と同一段落境界にC2を置くこと。
        before = self.segs_by_plan[m.COMMENT_2_AFTER_PLAN_INDEX][-1]
        after = self.segs_by_plan[m.COMMENT_2_AFTER_PLAN_INDEX + 1][0]
        self.assertEqual(max(before["source_paragraph_indices"]), 9)
        self.assertEqual(min(after["source_paragraph_indices"]), 10)

    def test_comment_3_boundary_matches_v1_story_017_018(self):
        # v1のstory_017/018境界(段落22/23境界)と同一段落境界にC3を置くこと。
        before = self.segs_by_plan[m.COMMENT_3_AFTER_PLAN_INDEX][-1]
        after = self.segs_by_plan[m.COMMENT_3_AFTER_PLAN_INDEX + 1][0]
        self.assertEqual(max(before["source_paragraph_indices"]), 22)
        self.assertEqual(min(after["source_paragraph_indices"]), 23)

    def test_v1_reusable_plan_indices_have_matching_segment_counts(self):
        for pi in m.V1_REUSABLE_PLAN_INDICES:
            expected_ids = m.V1_SEGMENT_IDS_BY_PLAN_INDEX[pi]
            actual = self.segs_by_plan[pi]
            self.assertEqual(len(expected_ids), len(actual),
                              f"plan_index={pi}: v1 segment数不一致")

    def test_reusable_and_new_plan_indices_partition_all_indices(self):
        all_indices = set(range(len(m.STORY_SEGMENT_PLAN)))
        new_indices = all_indices - m.V1_REUSABLE_PLAN_INDICES
        # 母親発話を含む段落(11,24)由来のplan_indexは新規生成対象であること。
        self.assertEqual(new_indices, {5, 6, 7, 14, 15, 16})


class NormalizeLooseTests(unittest.TestCase):
    def test_case_and_punctuation_insensitive(self):
        self.assertEqual(m._normalize_loose("Preference."), m._normalize_loose("preference"))

    def test_none_becomes_empty(self):
        self.assertEqual(m._normalize_loose(None), "")


class PlayerOutputTests(unittest.TestCase):
    """v2の生成物(実行後)を対象にした検証。生成物が無い場合はskipする
    (このテストファイル単体をAPI呼び出しなしで実行できるようにするため、
    実行結果への依存はここに限定する)。"""

    PLAYER_PATH = f"{m.OUT_DIR}/player.html"
    SEGMENTS_PATH = f"{m.OUT_DIR}/segments.json"
    CONSISTENCY_PATH = f"{m.OUT_DIR}/player_display_audio_consistency.json"

    def test_player_html_has_no_local_file_paths(self):
        if not os.path.exists(self.PLAYER_PATH):
            self.skipTest("player.htmlが未生成(run未実行)")
        with open(self.PLAYER_PATH, encoding="utf-8") as f:
            html = f.read()
        self.assertNotIn("file:///", html)
        self.assertNotIn("C:\\", html)
        self.assertNotIn("C:/Users", html)

    def test_segments_json_ids_are_sequential(self):
        if not os.path.exists(self.SEGMENTS_PATH):
            self.skipTest("segments.jsonが未生成(run未実行)")
        with open(self.SEGMENTS_PATH, encoding="utf-8") as f:
            segs = json.load(f)
        ids = [s["id"] for s in segs]
        self.assertEqual(ids, sorted(ids))

    def test_player_display_text_equals_canonical_text(self):
        if not os.path.exists(self.CONSISTENCY_PATH):
            self.skipTest("player_display_audio_consistency.jsonが未生成(run未実行)")
        with open(self.CONSISTENCY_PATH, encoding="utf-8") as f:
            rows = json.load(f)
        for row in rows:
            self.assertEqual(row["player_display_text"], row["canonical_text"],
                              f"segment {row['segment_id']}: player表示文とcanonicalが不一致")
            self.assertEqual(row["tts_input_text"], row["canonical_text"],
                              f"segment {row['segment_id']}: TTS inputとcanonicalが不一致")


if __name__ == "__main__":
    unittest.main()
