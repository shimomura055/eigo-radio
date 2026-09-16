# ============================================================
# er013_family_c_episode_trial_12_twins_test_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins A2+B1)
# ============================================================
# 決定的テスト(API呼び出しなし)。A2部分: 本文sha256固定・新segmentationが
# Trial-10と完全一致すること・再構成一致・Comment 4不在・禁止語句不在・
# Echo voice=Erinome不変・150語以上segmentなし。B1テストは
# er013_family_c_episode_trial_12_twins_b1_run.py完成後に追記する。
from __future__ import annotations

import json
import os
import unittest

import er013_family_c_episode_trial_12_twins_run as a2t


class ArticleFixedA2Tests(unittest.TestCase):
    def test_article_sha256_matches_trial08_source(self):
        actual_sha = a2t.sha256_text_file(a2t.ARTICLE_PATH)
        expected_sha = "b22e5f8e5f6951df302a31f7e83d1a6c9bef0d871dcfee65be480298d38a00b3"
        self.assertEqual(actual_sha, expected_sha)


class StorySegmentationA2Tests(unittest.TestCase):
    def setUp(self):
        self.article_text = a2t.load_article_text()
        self.paragraphs = a2t.split_into_paragraphs(self.article_text)
        self.segments = a2t.build_all_story_segments_trial12_twins(self.paragraphs)

    def test_paragraph_count(self):
        self.assertEqual(len(self.paragraphs), 33)

    def test_reconstruction_matches_article_exactly(self):
        recon = a2t.reconstruct_article_from_story_segments(self.segments, len(self.paragraphs))
        self.assertEqual(recon, self.article_text)

    def test_segment_count_identical_to_trial10(self):
        # 本タスクの分析結果: Trial-10 Twins A2のSTORY_SEGMENT_PLANは既に
        # Trial-11原則(Voice変化点/Comment挿入位置/scene boundaryのみで分割)
        # に沿って手作業設計されていたため、新旧segmentationは完全一致する。
        self.assertEqual(len(self.segments), 22)
        with open(f"{a2t.PREV_OUT_DIR}/segments.json", encoding="utf-8") as f:
            prev_segments = json.load(f)
        new_key = [(s["voice"], s["tts_text"]) for s in self.segments]
        prev_key = [(s["voice"], s["tts_text"]) for s in prev_segments]
        self.assertEqual(new_key, prev_key)

    def test_no_segment_reaches_150_words(self):
        for seg in self.segments:
            words = len(seg["tts_text"].split())
            self.assertLess(words, 150, f"{seg['id']}が150語以上: {words}語")

    def test_twin_voice_paragraphs_unchanged(self):
        twin_segs = [s for s in self.segments if s["voice"] == "twin"]
        self.assertEqual(len(twin_segs), 10)


class VoiceUnchangedA2Tests(unittest.TestCase):
    def test_twin_voice_is_erinome(self):
        self.assertEqual(a2t.TWIN_VOICE_NAME, "Erinome")


class CommentStructureA2Tests(unittest.TestCase):
    def test_comment_4_does_not_exist(self):
        self.assertEqual(a2t.COMMENT_NUMBERS, (1, 2, 3))
        self.assertNotIn(4, a2t.COMMENT_ROLES)
        self.assertFalse(hasattr(a2t, "COMMENT_4_ROLE_JA_TRIAL12_TWINS"))

    def test_comment_boundaries_at_expected_segments(self):
        segments = a2t.build_all_story_segments_trial12_twins(
            a2t.split_into_paragraphs(a2t.load_article_text()))
        seg_ids = [s["id"] for s in segments]
        self.assertIn(a2t.COMMENT_2_AFTER_SEGMENT_ID, seg_ids)
        self.assertIn(a2t.COMMENT_3_AFTER_SEGMENT_ID, seg_ids)
        self.assertEqual(a2t.COMMENT_2_AFTER_SEGMENT_ID, "story_010")
        self.assertEqual(a2t.COMMENT_3_AFTER_SEGMENT_ID, "story_019")


class CommentOutputA2Tests(unittest.TestCase):
    """A2実行後に生成されたcomments_ja.mdを対象にした検証。未生成時はskip。"""

    COMMENTS_PATH = f"{a2t.OUT_DIR}/comments_ja.md"

    def test_no_banned_meta_narration_phrases_in_generated_comments(self):
        if not os.path.exists(self.COMMENTS_PATH):
            self.skipTest("comments_ja.md未生成(A2 run未実行)")
        with open(self.COMMENTS_PATH, encoding="utf-8") as f:
            text = f.read()
        hits = a2t.BANNED_COMMENT_PHRASES_RE.findall(text)
        self.assertEqual(hits, [], f"禁止語句が残存: {hits}")

    def test_comment_4_not_present_in_generated_md(self):
        if not os.path.exists(self.COMMENTS_PATH):
            self.skipTest("comments_ja.md未生成(A2 run未実行)")
        with open(self.COMMENTS_PATH, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("## Comment 4", text)


class Trial10UntouchedA2Tests(unittest.TestCase):
    def test_trial10_twins_a2_segments_json_still_has_22_segments(self):
        path = "er013_output/family_c_episode_trial_10/twins_a2/segments.json"
        if not os.path.exists(path):
            self.skipTest("Trial-10 segments.json不在")
        with open(path, encoding="utf-8") as f:
            segs = json.load(f)
        self.assertEqual(len(segs), 22)


if __name__ == "__main__":
    unittest.main()
