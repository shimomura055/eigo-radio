# ============================================================
# er013_family_c_episode_trial_12_twins_test_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任2: Digital Twins A2+B1)
# ============================================================
# 決定的テスト(API呼び出しなし)。A2部分: 本文sha256固定・新segmentationが
# Trial-10と完全一致すること・再構成一致・Comment 4不在・禁止語句不在・
# Echo voice=Erinome不変・150語以上segmentなし。B1部分: 本文sha256固定・
# 新segmentation(旧53→新24)・再構成一致・Comment英語不変(Trial-10と
# byte-identical)・Support voice=Charon・150語以上segmentなし。
from __future__ import annotations

import json
import os
import unittest

import er013_family_c_episode_trial_12_twins_run as a2t
import er013_family_c_episode_trial_12_twins_b1_run as b1t


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


class ArticleFixedB1Tests(unittest.TestCase):
    def test_article_sha256_matches_trial10_source(self):
        actual_sha = a2t.sha256_text_file(b1t.ARTICLE_B1_PATH)
        self.assertEqual(actual_sha, b1t.EXPECTED_ARTICLE_SHA256)


class StorySegmentationB1Tests(unittest.TestCase):
    def setUp(self):
        with open(b1t.ARTICLE_B1_PATH, encoding="utf-8") as f:
            self.article_text = f.read()
        self.paragraphs = a2t.split_into_paragraphs(self.article_text)
        self.segments, self.ambiguous = b1t.build_story_segments_trial12_twins_b1(self.paragraphs)

    def test_paragraph_count(self):
        self.assertEqual(len(self.paragraphs), 34)

    def test_reconstruction_matches_article_exactly(self):
        recon = b1t.reconstruct_article_from_story_segments(self.segments, self.paragraphs)
        self.assertEqual(recon, self.article_text)

    def test_segment_count_reduced_from_trial10(self):
        # Trial-10 twins_b1は53 segment(段落ごとの機械的split)。Trial-12は
        # Voice変化点+scene boundary force splitのみで24 segmentへ削減。
        self.assertEqual(len(self.segments), 24)

    def test_no_segment_reaches_150_words(self):
        for s in self.segments:
            words = len(s["tts_text"].split())
            self.assertLess(words, 150, f"{s['id']}が150語以上: {words}語")

    def test_no_segment_exceeds_120_words(self):
        for s in self.segments:
            words = len(s["tts_text"].split())
            self.assertLessEqual(words, 120, f"{s['id']}が120語を超過: {words}語")

    def test_twin_quotes_classified_via_echo_twin_keywords(self):
        twin_segs = [s for s in self.segments if s["voice"] == "twin"]
        self.assertEqual(len(twin_segs), 11)

    def test_mara_own_quotes_stay_narrator(self):
        combined = " ".join(s["raw_text"] for s in self.segments if s["voice"] == "narrator")
        self.assertIn("begin with the first note", combined)
        self.assertIn("Echo?", combined)


class CommentUnchangedB1Tests(unittest.TestCase):
    def test_comments_unchanged_vs_trial10(self):
        new_path = f"{b1t.OUT_DIR}/comments_en.md"
        prev_path = f"{b1t.PREV_OUT_DIR}/comments_en.md"
        if not os.path.exists(new_path):
            self.skipTest("Trial-12 Twins B1 run未実行(comments_en.md不在)")
        with open(new_path, encoding="utf-8") as f:
            new_text = f.read()
        with open(prev_path, encoding="utf-8") as f:
            prev_text = f.read()
        self.assertEqual(new_text, prev_text, "Twins B1 CommentはTrial-10から内容変更なしのはず")

    def test_preview_unchanged_vs_trial10(self):
        new_path = f"{b1t.OUT_DIR}/preview_en.txt"
        prev_path = f"{b1t.PREV_OUT_DIR}/preview_en.txt"
        if not os.path.exists(new_path):
            self.skipTest("Trial-12 Twins B1 run未実行(preview_en.txt不在)")
        with open(new_path, encoding="utf-8") as f:
            new_text = f.read()
        with open(prev_path, encoding="utf-8") as f:
            prev_text = f.read()
        self.assertEqual(new_text, prev_text)


class SupportVoiceB1Tests(unittest.TestCase):
    def test_twin_voice_is_erinome(self):
        self.assertEqual(b1t.TWIN_VOICE_NAME, "Erinome")

    def test_speaker_map_records_erinome(self):
        path = f"{b1t.OUT_DIR}/speaker_map.json"
        if not os.path.exists(path):
            self.skipTest("Trial-12 Twins B1 run未実行(speaker_map.json不在)")
        with open(path, encoding="utf-8") as f:
            speaker_map = json.load(f)
        self.assertEqual(speaker_map["twin_voice"], "Erinome")


class Trial10TwinsB1UntouchedTests(unittest.TestCase):
    def test_trial10_twins_b1_segments_json_still_has_53_segments(self):
        path = "er013_output/family_c_episode_trial_10/twins_b1/segments.json"
        if not os.path.exists(path):
            self.skipTest("Trial-10 segments.json不在")
        with open(path, encoding="utf-8") as f:
            segs = json.load(f)
        self.assertEqual(len(segs), 53)


if __name__ == "__main__":
    unittest.main()
