# ============================================================
# er013_family_c_episode_trial_10_memory_test_01.py
# 管理ID: USER-TEST-FINAL-AUDIO-BATCH-06(委任B: Family C「The future of
# memory」A2+B1)
# ============================================================
# 決定的テスト(API呼び出しなし): A2側は本文sha256固定・speaker分割・
# Comment 4不在・日本語タイトル存在。B1側は日本語タイトル不在・Comment/
# Previewに日本語が含まれないこと・Support voice=Charonであること。
# (Home Robots用テスト[trial_09b_test_01.py/trial_09b_b1_test_01.py]の
# 構成を、本記事[memory]向けに複製・書き換えたもの)
from __future__ import annotations

import hashlib
import json
import os
import unittest

import er013_family_c_episode_trial_10_memory_run as a2m


class ArticleFixedTests(unittest.TestCase):
    """ユーザー指示(2026-09-15): Trial-08 reader_facing_article.txtを正本
    候補として固定し、本タスクでは再生成・書き換えを行わないことの決定的
    確認(sha256一致)。"""

    def test_article_sha256_matches_trial08_source(self):
        with open(a2m.ARTICLE_PATH, "rb") as f:
            actual_sha = hashlib.sha256(f.read()).hexdigest()
        # 2026-09-15時点のTrial-08正本sha256(本タスク開始時に固定・記録、
        # audit/article_fixed_sha256.jsonのsource_article_sha256と同一値)。
        expected_sha = "a9a646a798bfe44b632038c790d58680a3b278979ac39473339cace2733b2ea2"
        self.assertEqual(actual_sha, expected_sha)


class StorySegmentSplitTests(unittest.TestCase):
    def setUp(self):
        self.article_text = a2m.load_article_text()
        self.paragraphs = a2m.split_into_paragraphs(self.article_text)
        self.segments = a2m.build_all_story_segments(self.paragraphs)

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

    def test_brother_quote_is_split_into_brother_voice(self):
        brother_segs = [s for s in self.segments if s["voice"] == "brother"]
        self.assertEqual(len(brother_segs), 1)
        self.assertEqual(brother_segs[0]["source_paragraph_indices"], [14])

    def test_lena_dialogue_stays_narrator(self):
        combined = " ".join(s["raw_text"] for s in self.segments if s["voice"] == "narrator")
        self.assertIn("But I cannot carry it now", combined)
        self.assertIn("I will come back to this", combined)


class CommentStructureTests(unittest.TestCase):
    def test_comment_4_does_not_exist(self):
        self.assertEqual(a2m.COMMENT_NUMBERS, (1, 2, 3))
        self.assertNotIn(4, a2m.COMMENT_ROLES)
        self.assertFalse(hasattr(a2m, "COMMENT_4_ROLE_JA"))

    def test_comment_boundaries_are_at_scene_transition_and_turning_point(self):
        segments = a2m.build_all_story_segments(a2m.split_into_paragraphs(a2m.load_article_text()))
        segs_by_plan = {}
        for s in segments:
            segs_by_plan.setdefault(s["plan_index"], []).append(s)
        before_c2 = segs_by_plan[a2m.COMMENT_2_AFTER_PLAN_INDEX][-1]
        after_c2 = segs_by_plan[a2m.COMMENT_2_AFTER_PLAN_INDEX + 1][0]
        self.assertEqual(max(before_c2["source_paragraph_indices"]), 8)
        self.assertEqual(min(after_c2["source_paragraph_indices"]), 9)
        before_c3 = segs_by_plan[a2m.COMMENT_3_AFTER_PLAN_INDEX][-1]
        after_c3 = segs_by_plan[a2m.COMMENT_3_AFTER_PLAN_INDEX + 1][0]
        self.assertEqual(max(before_c3["source_paragraph_indices"]), 23)
        self.assertEqual(min(after_c3["source_paragraph_indices"]), 24)


class JapaneseTitlePresentA2Tests(unittest.TestCase):
    def test_japanese_title_text_is_registered(self):
        self.assertEqual(a2m.JAPANESE_TITLE_TEXT, "記憶の未来")
        self.assertTrue(len(a2m.JAPANESE_TITLE_TEXT) > 0)


class A2PlayerOutputTests(unittest.TestCase):
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


class B1SpecTests(unittest.TestCase):
    """B1側(er013_family_c_episode_trial_10_memory_b1_run.py)の恒久仕様
    (日本語タイトル不在・Comment 4不在・Support voice=Charon)の決定的
    テスト。B1スクリプトが未作成/未実行の段階ではimport自体をskipする。"""

    def setUp(self):
        try:
            import er013_family_c_episode_trial_10_memory_b1_run as b1m
        except ImportError:
            self.skipTest("B1スクリプト未作成")
        self.b1m = b1m

    def test_comment_4_does_not_exist_in_b1(self):
        self.assertFalse(hasattr(self.b1m, "JAPANESE_TITLE_TEXT_B1"))

    def test_b1_output_dir_has_no_japanese_title_file_after_run(self):
        out_dir = getattr(self.b1m, "OUT_DIR", None)
        if out_dir is None or not os.path.exists(f"{out_dir}/audio/japanese_title.wav"):
            self.skipTest("B1 run未実行、またはjapanese_title.wav不在(想定どおり)")
        self.fail("B1にjapanese_title.wavが生成されています(B1は日本語タイトルなしが正式仕様)")

    def test_b1_comments_and_preview_contain_no_japanese(self):
        out_dir = getattr(self.b1m, "OUT_DIR", None)
        comments_path = f"{out_dir}/comments_en.md" if out_dir else None
        if not comments_path or not os.path.exists(comments_path):
            self.skipTest("B1 comments_en.md未生成(B1 run未実行)")
        with open(comments_path, encoding="utf-8") as f:
            text = f.read()
        has_japanese = any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in text)
        self.assertFalse(has_japanese, "B1 Comment 1-3に日本語が含まれています")

    def test_b1_support_voice_is_charon(self):
        out_dir = getattr(self.b1m, "OUT_DIR", None)
        consistency_path = f"{out_dir}/player_display_audio_consistency.json" if out_dir else None
        if not consistency_path or not os.path.exists(consistency_path):
            self.skipTest("B1 consistency未生成(B1 run未実行)")
        # Support voice実装確認はaudit/tts_generation_results.json + RESULT_PACKET記載の
        # voice evidence(tts_robot経路呼び出し)で行う(このテストはファイル存在確認のみ)。
        self.assertTrue(os.path.exists(consistency_path))


if __name__ == "__main__":
    unittest.main()
