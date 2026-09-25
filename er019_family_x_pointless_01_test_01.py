# ============================================================
# er019_family_x_pointless_01_test_01.py
# NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B unit tests
# ============================================================
# API呼び出しなし(fixtureテキスト・dummy音声配列のみ)。
# 実行方法: .venv/Scripts/python.exe -m unittest er019_family_x_pointless_01_test_01 -v

from __future__ import annotations

import re
import subprocess
import unittest

import numpy as np

import er003_b1_p9a_audio as p9a
import er019_family_x_pointless_assemble_01 as fx_asm
import er019_family_x_pointless_scaffold_01 as fx_sc

_POINT_WORD_RE = re.compile(r"\bpoint\s+(one|two|1|2)\b|第(一|二)に", flags=re.IGNORECASE)

_FIXTURE_ARTICLE = """# Test Headline For Family X Trial

This is the first paragraph of the main story. It introduces the topic with
several sentences so that the paragraph has a reasonable number of words to
count for the volume balance test we are running here today.

This is the second paragraph of the main story. It continues the narrative
with additional detail and context, again containing enough words for the
word-count based split logic to have something meaningful to balance.

This is the third paragraph of the main story, which is intentionally a bit
shorter than the others but still has a decent number of words in it so the
three-way split has real content to work with in every part.

This is the fourth paragraph of the main story. It wraps up the narrative
before the point sections begin, again with a moderate number of words so
that the overall distribution across three parts stays reasonably balanced.

### Point One heading text

Point One body text goes here, describing one angle of the story in detail
with several sentences of content that should never appear in Family X.

### Point Two heading text

Point Two body text goes here, describing a second angle of the story with
its own sentences of content that should also never appear in Family X.

## In one line

The whole story wraps up in one short concluding line.
"""


# ============================================================
# Family Aモジュール未変更チェック(git working treeに差分が無いこと)
# ============================================================
FAMILY_A_FILES_MUST_BE_UNCHANGED = (
    "er003_v1_n3_01_scaffold_generate.py",
    "er003_v1_n3_01_assemble.py",
    "er003_v1_n3_01_tts_generate.py",
    "er012_e_family_entertainment_two_level_runner_01.py",
    "er003_v1_b1_scaffold_01_generate.py",
    "er003_v1_iran01_a2_generate.py",
    "audio_review_player.py",
    "er006_audio_cost_pilot_02_shared_narration.py",
    "er003_v1_sing01_voice01_generate.py",
    "er003_v1_sing01_news_tail_fix.py",
    "er003_b1_p9a_audio.py",
    "er005_cost_logger.py",
)


class FamilyAUnchangedTest(unittest.TestCase):
    def test_family_a_files_have_no_working_tree_diff(self):
        for path in FAMILY_A_FILES_MUST_BE_UNCHANGED:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--", path],
                cwd="C:/Users/tensh/eigo-radio", capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), "",
                              f"Family Aファイル{path}に未コミットの差分があります(無変更である必要があります): "
                              f"{result.stdout!r}")


class SplitArticleText3WayTest(unittest.TestCase):
    def test_volume_balance_within_threshold(self):
        parts = fx_sc.split_article_text_3way(_FIXTURE_ARTICLE)
        counts = parts["split_word_counts"]
        c1, c2, c3 = counts["part1"], counts["part2"], counts["part3"]
        self.assertGreater(c1, 0)
        self.assertGreater(c2, 0)
        self.assertGreater(c3, 0)
        total = c1 + c2 + c3
        max_min_diff_ratio = (max(c1, c2, c3) - min(c1, c2, c3)) / total
        # 既存2分割(split_article_text)の実測差(Meta本文で68語/59語、差13.4%)
        # より緩いが十分厳しい閾値として35%を採用する(3分割は分割点の自由度が
        # 2分割より低いため、同じ厳しさを機械的に要求すると偽陰性になりうる)。
        self.assertLessEqual(max_min_diff_ratio, 0.35,
                              f"3分割の語数バランスが偏りすぎています: part1={c1} part2={c2} part3={c3}")

    def test_point_sections_are_discarded(self):
        parts = fx_sc.split_article_text_3way(_FIXTURE_ARTICLE)
        combined = parts["part1"] + parts["part2"] + parts["part3"] + parts["in_one_line"]
        self.assertNotIn("Point One body text", combined)
        self.assertNotIn("Point Two body text", combined)
        self.assertNotIn("Point One heading text", combined)
        self.assertNotIn("Point Two heading text", combined)

    def test_too_few_paragraphs_raises(self):
        text = "# T\n\nOnly one paragraph here with some words in it.\n\n## In one line\nDone.\n"
        with self.assertRaises(RuntimeError):
            fx_sc.split_article_text_3way(text)


class PointWordingAbsenceTest(unittest.TestCase):
    def test_comment_role_texts_have_no_point_wording(self):
        for role_text in (fx_sc.FAMILY_X_COMMENT_3_ROLE, fx_sc.FAMILY_X_COMMENT_4_ROLE):
            self.assertIsNone(_POINT_WORD_RE.search(role_text),
                               f"role文言にPoint語彙が残存しています: {role_text!r}")

    def test_regex_detects_point_wording_in_sample_text(self):
        # 検出器自体が機能していることの陽性対照(negative controlの逆)。
        self.assertIsNotNone(_POINT_WORD_RE.search("Let's move to Point One now."))
        self.assertIsNotNone(_POINT_WORD_RE.search("第一に、これが重要です。"))


class TimelineHasNoPointSegmentTest(unittest.TestCase):
    @staticmethod
    def _dummy_stereo(seconds: float = 0.05):
        return np.zeros((int(seconds * p9a.TARGET_SAMPLE_RATE), 2), dtype=np.float64)

    def _build_fixture_parts(self):
        dummy = self._dummy_stereo
        b1_segments = {name: dummy() for name in (
            "full_story_part1", "full_story_part2", "full_story_part3",
            "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line")}
        return {
            "intro": dummy(), "welcome": dummy(), "topic_intro": dummy(), "notification": dummy(),
            "preview_intro": dummy(), "full_story_intro": dummy(), "outro": dummy(),
            "b1_segments": b1_segments,
        }

    def test_no_point_substring_in_any_timeline_label(self):
        parts = self._build_fixture_parts()
        seq = fx_asm.build_family_x_b1_timeline(parts)
        labels = [name for name, _ in seq]
        for label in labels:
            self.assertNotIn("Point", label, f"timelineにPoint関連segmentが残っています: {label}")

    def test_full_story_part3_and_comment_4_present_after_comment_3(self):
        parts = self._build_fixture_parts()
        seq = fx_asm.build_family_x_b1_timeline(parts)
        labels = [name for name, _ in seq]
        idx_c3 = next(i for i, l in enumerate(labels) if l.startswith("Comment 3"))
        idx_p3 = next(i for i, l in enumerate(labels) if l.startswith("Full Story Part 3"))
        idx_c4 = next(i for i, l in enumerate(labels) if l.startswith("Comment 4"))
        idx_ool = next(i for i, l in enumerate(labels) if l.startswith("In One Line"))
        self.assertLess(idx_c3, idx_p3)
        self.assertLess(idx_p3, idx_c4)
        self.assertLess(idx_c4, idx_ool)

    def test_no_key_phrase_segment_in_timeline(self):
        parts = self._build_fixture_parts()
        seq = fx_asm.build_family_x_b1_timeline(parts)
        labels = [name for name, _ in seq]
        for label in labels:
            self.assertNotIn("Key Phrase", label)
            self.assertNotIn("key_phrase", label.lower())

    def test_assemble_with_timeline_runs_without_error(self):
        parts = self._build_fixture_parts()
        seq = fx_asm.build_family_x_b1_timeline(parts)
        result = fx_asm.asm.assemble_with_timeline(seq)
        self.assertGreater(result["total_duration_seconds"], 0)
        self.assertEqual(len(result["timeline"]), len(seq))


if __name__ == "__main__":
    unittest.main()
