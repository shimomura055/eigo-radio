# FAMILY-X-COFFEE-NEW-TONE-PRODUCTION-E2E-01(2026-10-11): J2/E2_UPBEAT/F1.5の3仕様(APPROVED_FOR_PRODUCTION)の
# Production配線test(課金0、API呼出なし)。(a)逐語固定 (b)Role->Style対応(適用/非適用) (c)version guard
# (d)Dangling(旧style文字列・旧参照が定数/runnerに残っていない) (e)Trialの値との一致。
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er033_tts_flash_lite_family_x_styles_01 as fl
import er019_family_x_audio_production_runner_01 as runner

J2 = ("明るく、温かみのある親しみやすい話し方で。聞き手に楽しく語りかけるように、自然な抑揚と軽やかなリズムをつけてください。"
      "ニュース番組としての明瞭さを保ち、演技がかった話し方は避けてください。")
E2 = "warm, upbeat and engaging; friendly conversational delivery with lively but natural intonation."
F15 = ("warm, gently upbeat and engaging; natural, friendly delivery with a light sense of energy, "
       "while maintaining clear and credible news narration.")
OLD = ("落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。",
       "calm, conversational",
       "calm, steady news narration with natural emphasis at key points and turns; not dramatic.")
BASE = os.path.dirname(os.path.abspath(__file__))


class VerbatimTests(unittest.TestCase):
    def test_named_constants_verbatim(self):
        self.assertEqual(fl.JA_J2_BRIGHT, J2)
        self.assertEqual(fl.EN_COMMENT_E2_UPBEAT, E2)
        self.assertEqual(fl.EN_FULLSTORY_F1_5, F15)

    def test_role_mapping_applied(self):
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_JA, J2)
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN["PREVIEW"], E2)
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN["COMMENT"], E2)
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"], F15)

    def test_role_mapping_not_applied_unchanged(self):
        en = fl.FAMILY_X_ROLE_STYLE_EN
        self.assertEqual(en["TOPIC_INTRO"], "brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.")
        self.assertEqual(en["HEADING_READOUT"], "brief and clear")
        self.assertEqual(en["IN_ONE_LINE"], "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.")
        self.assertEqual(fl.FAMILY_X_ROLE_STYLE_EN_FALLBACK, ["natural, clear, conversational", "clear"])
        self.assertEqual(fl.KEY_PHRASE_EXPLANATION_EN, "clear, precise, at a measured pace, without dragging")

    def test_matches_trial_definitions(self):
        for rel, want in (("er053_output/tts_voice_tone_brightness_trial_01/tone_trial_01.py", J2),
                          ("er053_output/tts_voice_tone_brightness_trial_01/tone_trial_01.py", E2),
                          ("er053_output/tts_full_story_tone_trial_01/full_story_tone_trial_01.py", F15)):
            src = open(os.path.join(BASE, rel), encoding="utf-8").read()
            self.assertIn(want, src, rel)


class VersionGuardTests(unittest.TestCase):
    OLDV = "v3_j3_kp_meaning_and_explanation_guard"

    def test_version_bumped(self):
        self.assertEqual(runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, "v4_j2_e2upbeat_f15_tone_refresh")
        self.assertNotEqual(runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION, self.OLDV)

    def test_old_cache_not_reused(self):
        called = []
        cached = {"style_version": self.OLDV, "segments": {"preview": {"status": "OK", "canonical_text": "x"}}}
        runner._generate_or_reuse(cached, "preview", __file__, lambda: called.append(1) or {"status": "OK"}, expected_text="x")
        self.assertEqual(called, [1])
        called.clear()
        cached = {"style_version": self.OLDV,
                  "key_phrases": {"1": {"japanese_meaning": {"status": "OK", "canonical_text": "x"}}}}
        runner._generate_or_reuse_kp(cached, 1, "japanese_meaning", __file__, lambda: called.append(1) or {"status": "OK"},
                                     expected_text="x", require_style_version=True)
        self.assertEqual(called, [1])

    def test_current_version_cache_reused(self):
        cached = {"style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
                  "segments": {"preview": {"status": "OK", "canonical_text": "x"}}}
        r = runner._generate_or_reuse(cached, "preview", __file__, lambda: {"status": "REGEN"}, expected_text="x")
        self.assertTrue(r.get("reused_from_previous_run"))


class DanglingTests(unittest.TestCase):
    def test_no_old_style_literal_in_production_code(self):
        for f in ("er033_tts_flash_lite_family_x_styles_01.py", "er019_family_x_audio_production_runner_01.py"):
            src = open(os.path.join(BASE, f), encoding="utf-8").read()
            code = "\n".join(ln for ln in src.splitlines() if not ln.lstrip().startswith("#"))
            for old in OLD:
                self.assertNotIn('"' + old[:20], code, f"{f}: old style literal remains: {old[:30]}")

    def test_runner_reads_styles_only_via_fl_styles(self):
        src = open(os.path.join(BASE, "er019_family_x_audio_production_runner_01.py"), encoding="utf-8").read()
        self.assertIn("fl_styles.FAMILY_X_ROLE_STYLE_JA", src)
        self.assertIn("fl_styles.FAMILY_X_ROLE_STYLE_EN.get(role)", src)


if __name__ == "__main__":
    unittest.main()
