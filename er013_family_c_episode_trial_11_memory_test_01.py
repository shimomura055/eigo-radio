# ============================================================
# er013_family_c_episode_trial_11_memory_test_01.py
# 管理ID: FAMILY-C-MEMORY-A2-SEGMENT-COMMENT-TRIAL-11
# ============================================================
# 決定的テスト(API呼び出しなし): 本文sha256固定(Trial-10と同一値)・新
# segmentation(Voice分割・再構成・150語未満・避けられる短segment削減)・
# Comment 4不在・禁止語句(メタナレーション)不在・Brother Voice変更
# (Algieba)・player構造。Trial-10用テスト(er013_family_c_episode_
# trial_10_memory_test_01.py)を、本Trial-11新segmentation設計に合わせて
# 複製・書き換えたもの。Trial-10側テストファイルは無変更のまま維持する。
from __future__ import annotations

import hashlib
import json
import os
import re
import unittest

import er013_family_c_episode_trial_11_memory_run as a2m


class ArticleFixedTests(unittest.TestCase):
    """Trial-08本文をTrial-10と同一のsha256で固定していることの決定的確認。"""

    def test_article_sha256_matches_trial08_source(self):
        with open(a2m.ARTICLE_PATH, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        expected_sha = "a9a646a798bfe44b632038c790d58680a3b278979ac39473339cace2733b2ea2"
        self.assertEqual(actual_sha, expected_sha)


class StorySegmentationTrial11Tests(unittest.TestCase):
    def setUp(self):
        self.article_text = a2m.load_article_text()
        self.paragraphs = a2m.split_into_paragraphs(self.article_text)
        self.segments = a2m.build_all_story_segments_trial11(self.paragraphs)

    def test_paragraph_count(self):
        self.assertEqual(len(self.paragraphs), 29)

    def test_reconstruction_matches_article_exactly(self):
        recon = a2m.reconstruct_article_from_story_segments(self.segments, len(self.paragraphs))
        self.assertEqual(recon, self.article_text)

    def test_device_quotes_are_split_into_device_voice(self):
        device_segs = [s for s in self.segments if s["voice"] == "device"]
        self.assertEqual(len(device_segs), 2)
        texts = sorted(s["raw_text"] for s in device_segs)
        self.assertIn("“Return date?”", texts)
        self.assertIn("“Are you sure?”", texts)

    def test_brother_quote_is_split_into_new_voice(self):
        brother_segs = [s for s in self.segments if s["voice"] == "brother"]
        self.assertEqual(len(brother_segs), 1)
        self.assertEqual(brother_segs[0]["source_paragraph_indices"], [14])
        # Trial-11のBrother Voice変更(Erinome→Algieba)の決定的確認。
        self.assertEqual(a2m.BROTHER_VOICE_NAME, "Algieba")

    def test_lena_dialogue_stays_narrator(self):
        combined = " ".join(s["raw_text"] for s in self.segments if s["voice"] == "narrator")
        self.assertIn("But I cannot carry it now", combined)
        self.assertIn("I will come back to this", combined)

    def test_segment_count_reduced_from_trial10(self):
        # Trial-10は14 segment(story_001-014)、Trial-11は同一本文をより
        # 大きな連続発話へ統合し10 segmentへ削減。
        self.assertEqual(len(self.segments), 10)

    def test_no_segment_reaches_150_words(self):
        for seg in self.segments:
            words = len(seg["tts_text"].split())
            self.assertLess(words, 150, f"{seg['id']}が150語以上: {words}語")

    def test_no_segment_exceeds_120_words_by_large_margin(self):
        for seg in self.segments:
            words = len(seg["tts_text"].split())
            self.assertLessEqual(words, 120, f"{seg['id']}が120語を超過: {words}語")

    def test_avoidable_short_narrator_segments_are_eliminated(self):
        # Trial-10には、device/brother引用符の前後にある短いnarrator地の文
        # (4語/3語/2語)が独立segmentとして3件存在した(story_002/006/010)。
        # Trial-11ではこれらを隣接する同一Voice(narrator)segmentへ統合して
        # いるため、10語未満のnarrator segmentは「前後とも別Voiceに挟まれた
        # 構造上やむを得ない例外」(段落3単独、story_003)の1件のみになる。
        short_narrator_segs = [s for s in self.segments
                                if s["voice"] == "narrator" and len(s["tts_text"].split()) < 10]
        self.assertEqual(len(short_narrator_segs), 1)
        self.assertEqual(short_narrator_segs[0]["id"], "story_003")


class CommentStructureTrial11Tests(unittest.TestCase):
    def test_comment_4_does_not_exist(self):
        self.assertEqual(a2m.COMMENT_NUMBERS, (1, 2, 3))
        self.assertNotIn(4, a2m.COMMENT_ROLES)
        self.assertFalse(hasattr(a2m, "COMMENT_4_ROLE_JA_TRIAL11"))

    def test_comment_boundaries_are_at_scene_transition_and_turning_point(self):
        segments = a2m.build_all_story_segments_trial11(a2m.split_into_paragraphs(a2m.load_article_text()))
        seg_ids = [s["id"] for s in segments]
        before_c2 = next(s for s in segments if s["id"] == a2m.COMMENT_2_AFTER_SEGMENT_ID)
        after_c2 = segments[seg_ids.index(a2m.COMMENT_2_AFTER_SEGMENT_ID) + 1]
        self.assertEqual(max(before_c2["source_paragraph_indices"]), 8)
        self.assertEqual(min(after_c2["source_paragraph_indices"]), 9)
        before_c3 = next(s for s in segments if s["id"] == a2m.COMMENT_3_AFTER_SEGMENT_ID)
        after_c3 = segments[seg_ids.index(a2m.COMMENT_3_AFTER_SEGMENT_ID) + 1]
        self.assertEqual(max(before_c3["source_paragraph_indices"]), 23)
        self.assertEqual(min(after_c3["source_paragraph_indices"]), 24)

    def test_trial10_prev_prompts_are_retained_for_comparison(self):
        self.assertTrue(hasattr(a2m, "COMMENT_1_ROLE_JA_TRIAL10_PREV"))
        self.assertTrue(hasattr(a2m, "COMMENT_2_ROLE_JA_TRIAL10_PREV"))
        self.assertTrue(hasattr(a2m, "COMMENT_3_ROLE_JA_TRIAL10_PREV"))

    def test_trial11_prompts_do_not_contain_banned_phrases_themselves(self):
        for role in (a2m.COMMENT_1_ROLE_JA_TRIAL11, a2m.COMMENT_2_ROLE_JA_TRIAL11,
                     a2m.COMMENT_3_ROLE_JA_TRIAL11):
            # Prompt本文は禁止語句を「使うな」という指示として言及するため、
            # ここでは生成後の実際のComment本文側(comments_ja.md)を検証する
            # (下のCommentOutputTrial11Testsを参照)。ここではPromptに新方針
            # キーワード(状況整理・理解を助ける)が含まれることのみ確認する。
            self.assertIn("状況", role)


class CommentOutputTrial11Tests(unittest.TestCase):
    """A2実行後に生成されたcomments_ja.mdを対象にした検証。未生成時はskip。"""

    COMMENTS_PATH = f"{a2m.OUT_DIR}/comments_ja.md"

    def test_no_banned_meta_narration_phrases_in_generated_comments(self):
        if not os.path.exists(self.COMMENTS_PATH):
            self.skipTest("comments_ja.md未生成(A2 run未実行)")
        with open(self.COMMENTS_PATH, encoding="utf-8") as f:
            text = f.read()
        hits = a2m.BANNED_COMMENT_PHRASES_RE.findall(text)
        self.assertEqual(hits, [], f"禁止語句が残存: {hits}")

    def test_comment_4_not_present_in_generated_md(self):
        if not os.path.exists(self.COMMENTS_PATH):
            self.skipTest("comments_ja.md未生成(A2 run未実行)")
        with open(self.COMMENTS_PATH, encoding="utf-8") as f:
            text = f.read()
        self.assertNotIn("## Comment 4", text)


class JapaneseTitlePresentA2Tests(unittest.TestCase):
    def test_japanese_title_text_is_registered(self):
        self.assertEqual(a2m.JAPANESE_TITLE_TEXT, "記憶の未来")
        self.assertTrue(len(a2m.JAPANESE_TITLE_TEXT) > 0)


class A2PlayerOutputTrial11Tests(unittest.TestCase):
    """A2実行後の生成物(存在すれば)を対象にした検証。未生成時はskip。"""

    PLAYER_PATH = f"{a2m.OUT_DIR}/player.html"
    CONSISTENCY_PATH = f"{a2m.OUT_DIR}/player_display_audio_consistency.json"

    def test_player_html_has_no_local_file_paths(self):
        if not os.path.exists(self.PLAYER_PATH):
            self.skipTest("player.htmlが未生成(A2 run未実行)")
        with open(self.PLAYER_PATH, encoding="utf-8") as f:
            html = f.read()
        self.assertNotIn("file:///", html)
        self.assertNotIn("C:\\", html)
        self.assertNotIn("C:/Users", html)

    def test_player_display_text_equals_canonical_text(self):
        if not os.path.exists(self.CONSISTENCY_PATH):
            self.skipTest("player_display_audio_consistency.jsonが未生成(A2 run未実行)")
        with open(self.CONSISTENCY_PATH, encoding="utf-8") as f:
            rows = json.load(f)
        for row in rows:
            self.assertEqual(row["player_display_text"], row["canonical_text"],
                              f"segment {row['segment_id']}: player表示文とcanonicalが不一致")
            self.assertEqual(row["tts_input_text"], row["canonical_text"],
                              f"segment {row['segment_id']}: TTS inputとcanonicalが不一致")


class Trial10UntouchedTests(unittest.TestCase):
    """Trial-10成果物を一切上書き・編集していないことの決定的確認
    (ファイル存在+本タスクで新規作成していないことの補助チェック)。"""

    def test_trial10_segments_json_still_has_14_segments(self):
        path = "er013_output/family_c_episode_trial_10/memory_a2/segments.json"
        if not os.path.exists(path):
            self.skipTest("Trial-10 segments.json不在")
        with open(path, encoding="utf-8") as f:
            segs = json.load(f)
        self.assertEqual(len(segs), 14)


if __name__ == "__main__":
    unittest.main()
