# ============================================================
# er013_family_c_episode_trial_09b_b1_test_01.py
# 管理ID: USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1
# ============================================================
# 決定的テスト(API呼び出しなし): speaker分割(汎用アルゴリズム)、Comment
# placement選定アルゴリズム、Comment 4不在、player相対参照・file:///不在。
from __future__ import annotations

import json
import os
import re
import unittest

import er013_family_c_episode_trial_09b_b1_run as m


SAMPLE_PARAGRAPHS = [
    "Maya woke early. The room was quiet.",
    "\u201cGood morning,\u201d said the robot. \u201cYour day is ready.\u201d",
    "She ate breakfast and thought about nothing in particular.",
    "\u201cI cannot live alone anymore,\u201d her mother said. \u201cWhat do you think?\u201d",
    "Maya looked at the two plans on the wall.",
    "\u201cI need your preference,\u201d the robot said quietly.",
    "\u201cWhat do you want, Maya?\u201d her mother asked, touching her hand.",
    "\u201cTurn everything off,\u201d Maya said, and the house went dark.",
    "In the dark, she took a slow breath and felt afraid, but awake.",
]
SAMPLE_ARTICLE_TEXT = "\n\n".join(SAMPLE_PARAGRAPHS)


class QuoteSpanDetectionTests(unittest.TestCase):
    def test_finds_all_quote_spans_curly(self):
        spans = m.find_quote_spans(SAMPLE_PARAGRAPHS[1])
        self.assertEqual(len(spans), 2)

    def test_no_quotes_returns_empty(self):
        spans = m.find_quote_spans(SAMPLE_PARAGRAPHS[0])
        self.assertEqual(spans, [])

    def test_classifies_robot_quote_by_nearby_keyword(self):
        spans = m.find_quote_spans(SAMPLE_PARAGRAPHS[1])
        start, end, _ = spans[0]
        self.assertEqual(m.classify_quote_voice(SAMPLE_PARAGRAPHS[1], start, end), "robot")

    def test_classifies_mother_quote_by_nearby_keyword(self):
        spans = m.find_quote_spans(SAMPLE_PARAGRAPHS[3])
        start, end, _ = spans[0]
        self.assertEqual(m.classify_quote_voice(SAMPLE_PARAGRAPHS[3], start, end), "mother")

    def test_ambiguous_quote_falls_back_to_narrator(self):
        # "robot"/"mother"どちらのキーワードも近傍にない引用符はnarratorへfallbackする。
        text = "\u201cHello there,\u201d she said with a smile."
        spans = m.find_quote_spans(text)
        start, end, _ = spans[0]
        self.assertEqual(m.classify_quote_voice(text, start, end), "narrator")


class BuildStorySegmentsB1Tests(unittest.TestCase):
    def setUp(self):
        self.paragraphs = m.v2run.split_into_paragraphs(SAMPLE_ARTICLE_TEXT)
        self.segments, self.ambiguous = m.build_all_story_segments_b1(self.paragraphs)

    def test_reconstruction_matches_article_exactly(self):
        recon = m.reconstruct_article_from_story_segments(self.segments, self.paragraphs)
        self.assertEqual(recon, SAMPLE_ARTICLE_TEXT)

    def test_only_maya_own_dialogue_is_ambiguous(self):
        # "Turn everything off," Maya said はrobot/mother両方に該当しないため
        # ambiguous_quotesへ記録されつつnarratorへfallbackする(意図した挙動、
        # v2のMaya分離しない設計判断と整合)。他の引用符(robot/mother発話)は
        # すべて機械的に判定できること。
        self.assertEqual(len(self.ambiguous), 1)
        self.assertIn("Turn everything off", self.ambiguous[0]["quote_text"])

    def test_no_quote_paragraphs_are_merge_kind(self):
        no_quote_para_indices = {0, 2, 4, 8}
        for seg in self.segments:
            if seg["source_paragraph_indices"][0] in no_quote_para_indices:
                self.assertEqual(seg["kind"], "merge")

    def test_dialogue_paragraphs_are_split_kind(self):
        dialogue_para_indices = {1, 3, 5, 6, 7}
        for seg in self.segments:
            if seg["source_paragraph_indices"][0] in dialogue_para_indices:
                self.assertEqual(seg["kind"], "split")

    def test_robot_and_mother_voices_detected(self):
        voices = {seg["voice"] for seg in self.segments}
        self.assertIn("robot", voices)
        self.assertIn("mother", voices)

    def test_maya_dialogue_stays_narrator(self):
        # "Turn everything off," Maya said は、Mayaの台詞でありnarrator(Aoede)のまま
        # 分離しない(v2のspeaker_map.json設計判断を踏襲)。前後80文字圏内に
        # "robot"/"mother"という語がないため、汎用アルゴリズム上もnarratorへ
        # 分類される(意図した挙動)。
        maya_line = next(seg for seg in self.segments if "Turn everything off" in seg["raw_text"])
        self.assertEqual(maya_line["voice"], "narrator")

    def test_segment_ids_are_sequential(self):
        ids = [seg["id"] for seg in self.segments]
        self.assertEqual(ids, sorted(ids))


class ChooseCommentBoundariesTests(unittest.TestCase):
    def test_c2_before_c3_and_both_are_merge_kind(self):
        paragraphs = m.v2run.split_into_paragraphs(SAMPLE_ARTICLE_TEXT)
        segments, _ = m.build_all_story_segments_b1(paragraphs)
        c2_idx, c3_idx, total_words, cum_words = m.choose_comment_boundaries(segments)
        self.assertLess(c2_idx, c3_idx)
        self.assertEqual(segments[c2_idx]["kind"], "merge")
        self.assertEqual(segments[c3_idx]["kind"], "merge")
        self.assertGreater(total_words, 0)

    def test_raises_when_no_merge_segment_exists(self):
        all_dialogue = "\u201cRobot said this,\u201d said the robot."
        paragraphs = m.v2run.split_into_paragraphs(all_dialogue)
        segments, _ = m.build_all_story_segments_b1(paragraphs)
        with self.assertRaises(RuntimeError):
            m.choose_comment_boundaries(segments)


class CommentStructureTests(unittest.TestCase):
    """Family C仕様: Comment 4を恒久的に使用しないこと(ユーザー正式決定)の
    決定的テスト(API呼び出しなし)。"""

    def test_comment_4_does_not_exist(self):
        self.assertEqual(set(m.COMMENT_ROLES.keys()), {1, 2, 3})
        self.assertNotIn(4, m.COMMENT_ROLES)
        self.assertFalse(hasattr(m, "COMMENT_4_ROLE_JA"))

    def test_comment_roles_are_nonempty_strings(self):
        for n in (1, 2, 3):
            self.assertIsInstance(m.COMMENT_ROLES[n], str)
            self.assertGreater(len(m.COMMENT_ROLES[n]), 20)

    def test_comment3_fixed_text_override_states_explicit_subjects(self):
        # USER-TEST-FOLLOWUP-AND-SPEC-TRACEABILITY-03-FAMILYC-B1(継続CONT1):
        # 「誰が問いかけ誰が答えたか」が曖昧だったComment 3の修正確認。
        # 修正後文は「ロボットが」(問いかけの主語)と「マヤは」(答えの主語)を
        # 明示的に含み、旧文(主語なしの「答えても」)のような曖昧さがない。
        text = m.COMMENT_3_FIXED_TEXT_OVERRIDE
        self.assertIn("ロボットが", text)
        self.assertIn("マヤは", text)
        old_ambiguous_text = ("お金や仕事、睡眠、安全について答えても、今回はロボットの"
                               "いつものやり方だけでは答えが見つからないようです。")
        self.assertNotEqual(text, old_ambiguous_text)


class FinalFixFourTests(unittest.TestCase):
    """FAMILY-C-HOME-ROBOTS-A2-B1-FINAL-FIX-04: 日本語タイトル不在・Comment
    1〜3のeasy English化・Robot選択肢二人称化の決定的テスト(生成物が無い
    場合はskip、APIコールなし)。"""

    OUT_DIR = m.OUT_DIR

    def test_japanese_title_segment_is_absent(self):
        path = f"{self.OUT_DIR}/player.html"
        segments_path = f"{self.OUT_DIR}/segments.json"
        if not (os.path.exists(path) and os.path.exists(segments_path)):
            self.skipTest("player.html/segments.json not generated yet")
        with open(path, encoding="utf-8") as f:
            html = f.read()
        self.assertNotIn("japanese_title", html)
        self.assertNotIn(m.JAPANESE_TITLE_TEXT, html)
        with open(segments_path, encoding="utf-8") as f:
            segs = json.load(f)
        self.assertNotIn(m.JAPANESE_TITLE_TEXT, [s.get("tts_text") for s in segs])

    def test_comments_1_to_3_contain_no_japanese_characters(self):
        path = f"{self.OUT_DIR}/audit/tts_generation_results.json"
        if not os.path.exists(path):
            self.skipTest("tts_generation_results.json not generated yet")
        with open(path, encoding="utf-8") as f:
            results = json.load(f)
        segs = results.get("segments", results)
        ja_re = re.compile(r"[぀-ヿ一-鿿]")
        for n in (1, 2, 3):
            key = f"comment_{n}_ja"
            self.assertIn(key, segs)
            text = segs[key].get("canonical_text", "")
            self.assertFalse(ja_re.search(text), f"{key} contains Japanese characters: {text!r}")

    def test_robot_choice_segment_matches_second_person_fixed_text(self):
        expected = "CARE HOUSE — more sleep and privacy for you HOME — more time with your mother"
        self.assertEqual(m.ROBOT_CHOICE_FIXED_TEXT_OVERRIDE_B1, expected)
        self.assertNotIn("Maya", expected)
        self.assertNotIn("her mother", expected)
        path = f"{self.OUT_DIR}/segments.json"
        if not os.path.exists(path):
            self.skipTest("segments.json not generated yet")
        with open(path, encoding="utf-8") as f:
            segs = json.load(f)
        texts = [s["tts_text"] for s in segs]
        self.assertNotIn(m.ROBOT_CHOICE_OLD_TEXT_B1, texts)
        self.assertIn(m.ROBOT_CHOICE_FIXED_TEXT_OVERRIDE_B1, texts)
        matching = [s for s in segs if s["tts_text"] == m.ROBOT_CHOICE_FIXED_TEXT_OVERRIDE_B1]
        self.assertEqual(matching[0]["voice"], "robot")


class WriterB1ContractTests(unittest.TestCase):
    """writer_08(A2)のhard rule定数を継承していること、B1固有の追加制約
    (Story core維持)が存在することの決定的テスト。"""

    def test_max_characters_matches_writer_08(self):
        self.assertEqual(m.writer_b1.MAX_CHARACTERS, m.writer_b1.writer08.MAX_CHARACTERS)

    def test_constraint_count_includes_story_core_preservation(self):
        joined = " ".join(m.writer_b1.CONSTRAINT_LIST)
        self.assertIn("Story core", joined)

    def test_word_target_is_documented_as_trial_approximation(self):
        self.assertIn("Trial", " ".join(m.writer_b1.CONSTRAINT_LIST))


class PlayerOutputTests(unittest.TestCase):
    """B1 runの生成物(実行後)を対象にした検証。生成物が無い場合はskipする
    (このテストファイル単体をAPI呼び出しなしで実行できるようにするため)。"""

    PLAYER_PATH = f"{m.OUT_DIR}/player.html"
    SEGMENTS_PATH = f"{m.OUT_DIR}/segments.json"
    CONSISTENCY_PATH = f"{m.OUT_DIR}/player_display_audio_consistency.json"
    COMMENT_PLACEMENT_PATH = f"{m.OUT_DIR}/comment_placement.json"

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

    def test_comment_placement_has_exactly_three_comments_no_four(self):
        if not os.path.exists(self.COMMENT_PLACEMENT_PATH):
            self.skipTest("comment_placement.jsonが未生成(run未実行)")
        with open(self.COMMENT_PLACEMENT_PATH, encoding="utf-8") as f:
            placement = json.load(f)
        comment_numbers = sorted(p["comment"] for p in placement)
        self.assertEqual(comment_numbers, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
