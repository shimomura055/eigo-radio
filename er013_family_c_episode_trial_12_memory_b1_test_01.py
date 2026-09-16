# ============================================================
# er013_family_c_episode_trial_12_memory_b1_test_01.py
# 管理ID: FAMILY-C-SEGMENT-COMMENT-TRIAL-12(委任1: Memory B1)
# ============================================================
# 決定的テスト(API呼び出しなし): 本文sha256固定・日本語タイトル不在・
# Comment英語・Support voice=Charon・兄voice=Algieba・150語以上segment
# なしの回帰確認。`er013_family_c_episode_trial_10_memory_test_01.py`の
# B1SpecTestsを本Trialスクリプト向けに複製・書き換えたもの。
from __future__ import annotations

import hashlib
import json
import os
import unittest

import er013_family_c_episode_trial_12_memory_b1_run as b1m


class ArticleFixedTests(unittest.TestCase):
    """Trial-10で独立生成済みのreader_facing_article_b1.txtを正本候補として
    固定し、本タスクでは再生成・書き換えを行わないことの決定的確認
    (sha256一致)。"""

    def test_article_sha256_matches_trial10_source(self):
        with open(b1m.ARTICLE_B1_PATH, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(actual_sha, b1m.EXPECTED_ARTICLE_SHA256)


class StorySegmentSplitTests(unittest.TestCase):
    def setUp(self):
        with open(b1m.ARTICLE_B1_PATH, encoding="utf-8") as f:
            self.article_text = f.read()
        self.paragraphs = b1m.a2m.split_into_paragraphs(self.article_text)
        self.segments, self.ambiguous = b1m.build_story_segments_trial12(self.paragraphs)

    def test_paragraph_count(self):
        self.assertEqual(len(self.paragraphs), 26)

    def test_reconstruction_matches_article_exactly(self):
        recon = b1m.reconstruct_article_from_story_segments(self.segments, self.paragraphs)
        self.assertEqual(recon, self.article_text)

    def test_device_quotes_are_split_into_device_voice(self):
        device_segs = [s for s in self.segments if s["voice"] == "device"]
        self.assertEqual(len(device_segs), 2)
        texts = sorted(s["raw_text"] for s in device_segs)
        self.assertIn("“Return date?”", texts)
        self.assertIn("“Are you sure?”", texts)

    def test_brother_quote_is_split_into_brother_voice(self):
        brother_segs = [s for s in self.segments if s["voice"] == "brother"]
        self.assertEqual(len(brother_segs), 1)
        self.assertEqual(brother_segs[0]["source_paragraph_indices"], [16])

    def test_lena_dialogue_stays_narrator(self):
        combined = " ".join(s["raw_text"] for s in self.segments if s["voice"] == "narrator")
        self.assertIn("But I cannot carry it now", combined)
        self.assertIn("I will come back to this", combined)

    def test_no_segment_reaches_150_words(self):
        """Trial安全ガイド(150-200語級を作らない)の決定的確認。"""
        for s in self.segments:
            word_count = len(s["tts_text"].split())
            self.assertLess(word_count, 150,
                             f"{s['id']}が{word_count}語(150語以上、安全ガイド違反)")

    def test_no_short_narrator_only_quote_split(self):
        """"No,"のような短い同一Voice(narrator)台詞が単独segment化されて
        いないことの確認(Trial-11方針の踏襲)。narrator segmentは複数の
        段落・chunkを統合しているため、単一引用符のみのnarrator segment
        (例: raw_text=="“No,”")は存在しないはず。"""
        for s in self.segments:
            if s["voice"] == "narrator":
                self.assertNotEqual(s["raw_text"].strip(), "“No,”")


class SegmentationCountTests(unittest.TestCase):
    def test_segment_count_is_10(self):
        with open(b1m.ARTICLE_B1_PATH, encoding="utf-8") as f:
            article_text = f.read()
        paragraphs = b1m.a2m.split_into_paragraphs(article_text)
        segments, _ = b1m.build_story_segments_trial12(paragraphs)
        self.assertEqual(len(segments), 10)


class NoJapaneseTitleTests(unittest.TestCase):
    def test_no_japanese_title_constant(self):
        self.assertFalse(hasattr(b1m, "JAPANESE_TITLE_TEXT_B1"))
        self.assertFalse(hasattr(b1m, "JAPANESE_TITLE_TEXT"))

    def test_no_japanese_title_file_after_run(self):
        if not os.path.isdir(f"{b1m.OUT_DIR}/audio"):
            self.skipTest("Trial-12 B1 run未実行(audio dir不在)")
        self.assertFalse(os.path.exists(f"{b1m.OUT_DIR}/audio/japanese_title.wav"),
                          "B1にjapanese_title.wavが生成されています(B1は日本語タイトルなしが正式仕様)")


class CommentEnglishAndUnchangedTests(unittest.TestCase):
    def test_comments_contain_no_japanese(self):
        path = f"{b1m.PREV_OUT_DIR}/comments_en.md"
        if not os.path.exists(path):
            self.skipTest("Trial-10 comments_en.md不在")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        has_japanese = any("぀" <= ch <= "ヿ" or "一" <= ch <= "鿿" for ch in text)
        self.assertFalse(has_japanese, "B1 Comment 1-3に日本語が含まれています")

    def test_comments_unchanged_vs_trial10(self):
        out_dir = b1m.OUT_DIR
        new_path = f"{out_dir}/comments_en.md"
        prev_path = f"{b1m.PREV_OUT_DIR}/comments_en.md"
        if not os.path.exists(new_path):
            self.skipTest("Trial-12 B1 run未実行(comments_en.md不在)")
        with open(new_path, encoding="utf-8") as f:
            new_text = f.read()
        with open(prev_path, encoding="utf-8") as f:
            prev_text = f.read()
        self.assertEqual(new_text, prev_text, "B1 CommentはTrial-10から内容変更なしのはず")


class SupportVoiceAndBrotherVoiceTests(unittest.TestCase):
    def test_brother_voice_is_algieba(self):
        self.assertEqual(b1m.BROTHER_VOICE_NAME, "Algieba")

    def test_speaker_map_records_algieba_and_charon(self):
        path = f"{b1m.OUT_DIR}/speaker_map.json"
        if not os.path.exists(path):
            self.skipTest("Trial-12 B1 run未実行(speaker_map.json不在)")
        with open(path, encoding="utf-8") as f:
            speaker_map = json.load(f)
        self.assertEqual(speaker_map["brother_voice"], "Algieba")
        self.assertEqual(speaker_map["device_voice"], "Charon")

    def test_support_voice_consistency_file_exists(self):
        consistency_path = f"{b1m.OUT_DIR}/player_display_audio_consistency.json"
        if not os.path.exists(consistency_path):
            self.skipTest("Trial-12 B1 run未実行")
        self.assertTrue(os.path.exists(consistency_path))


class Trial10And11UnchangedTests(unittest.TestCase):
    """Trial-10/Trial-11の既存成果物を無編集で保存していることの確認
    (git statusでの確認が正、本テストはファイル存在のみの補助確認)。"""

    def test_trial10_b1_article_still_exists(self):
        self.assertTrue(os.path.exists(
            "er013_output/family_c_episode_trial_10/memory_b1/reader_facing_article_b1.txt"))

    def test_trial11_memory_a2_dir_still_exists(self):
        self.assertTrue(os.path.isdir("er013_output/family_c_episode_trial_11/memory_a2"))


if __name__ == "__main__":
    unittest.main()
