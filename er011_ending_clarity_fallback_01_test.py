# ============================================================
# er011_ending_clarity_fallback_01_test.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03: 受入テスト(10項目)
# ============================================================
from __future__ import annotations

import os
import shutil
import tempfile
import unittest

import er003_b1_p9a_audio as p9a
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er011_ending_clarity_fallback_01 as ending_clarity
import er011_human_review_lock_01 as review_lock

CANONICAL_ENDING_LOSS_TEXT = "Your phone does not have to be opened to become part of the task."
ASR_ENDING_LOSS_TEXT = "Your phone does not have to be open to become part of the task."
ASR_UNRELATED_MISMATCH_TEXT = "Your phone does not have to be closed to become part of the task."


class DetectEndingLossTests(unittest.TestCase):
    def test_detects_generic_suffix_drop_not_just_opened(self):
        # item 9: "opened"へのhardcodeが無く、他の語(walked/walk、
        # results/result)でも同じ仕組みで検出できることを確認する。
        self.assertTrue(ending_clarity.detect_ending_loss_diffs(
            "She walked to the station.", "She walk to the station."))
        self.assertTrue(ending_clarity.detect_ending_loss_diffs(
            "She kept checking her phone.", "She kept check her phone."))

    def test_detects_opened_case(self):
        findings = ending_clarity.detect_ending_loss_diffs(CANONICAL_ENDING_LOSS_TEXT, ASR_ENDING_LOSS_TEXT)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["canonical_word"], "opened")
        self.assertEqual(findings[0]["asr_word"], "open")
        self.assertEqual(findings[0]["dropped_suffix"], "ed")

    def test_no_hardcoded_opened_string_in_suffix_or_module_logic(self):
        # item 9(強化): instruction文言自体にも"opened"という語が含まれない。
        self.assertNotIn("opened", ending_clarity.ENDING_CLARITY_SUFFIX.lower())

    def test_unrelated_content_mismatch_is_not_ending_loss(self):
        # "closed"は"opened"と語尾ではなく語幹自体が違うため、prefix関係が無く
        # 検出されない(単なるASR表記揺れ・内容誤りまでfallback対象にしない)。
        findings = ending_clarity.detect_ending_loss_diffs(CANONICAL_ENDING_LOSS_TEXT, ASR_UNRELATED_MISMATCH_TEXT)
        self.assertEqual(findings, [])

    # ------------------------------------------------------------
    # ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04: comment_2実データ
    # ("studies"->"study")の回帰テスト。
    # ------------------------------------------------------------
    def test_detects_irregular_y_plural_suffix_drop_studies_case(self):
        findings = ending_clarity.detect_ending_loss_diffs(
            "The studies suggest that a phone can affect attention.",
            "The study suggests that a phone can affect attention.")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["canonical_word"], "studies")
        self.assertEqual(findings[0]["asr_word"], "study")
        self.assertEqual(findings[0]["dropped_suffix"], "ies")

    def test_irregular_y_plural_generalizes_beyond_studies(self):
        # "studies"へのhardcodeでは無いことを、別の子音+y複数形(city/cities)で
        # 確認する。
        findings = ending_clarity.detect_ending_loss_diffs(
            "Several cities reported the same pattern.",
            "Several city reported the same pattern.")
        self.assertTrue(findings)
        self.assertEqual(findings[0]["canonical_word"], "cities")
        self.assertEqual(findings[0]["asr_word"], "city")

    def test_added_ending_survey_to_surveys_is_not_ending_loss(self):
        # comment_3実データ回帰: "survey"->"surveys"は語尾が"脱落"したのでは
        # なく、存在しない語尾が"追加"されたケース(語尾脱落fallbackの対象外)。
        findings = ending_clarity.detect_ending_loss_diffs(
            "The studies and the survey suggest that a phone can affect people.",
            "The studies and the surveys suggest that a phone can affect people.")
        self.assertEqual(findings, [])


class EndingClarityFallbackWiringTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_ec_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "b1b", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "in_one_line.wav").replace("\\", "/")
        self.other_out_path = os.path.join(self.narration_dir, "full_story_part1.wav").replace("\\", "/")
        self.original_core = news_tail_fix.generate_news_narration_wide_margin.__wrapped__
        self.original_prefix = p9a.ENGLISH_STYLE_PREFIX

    def tearDown(self):
        news_tail_fix.generate_news_narration_wide_margin.__wrapped__ = self.original_core
        p9a.ENGLISH_STYLE_PREFIX = self.original_prefix
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _install_fake_core(self, fn):
        news_tail_fix.generate_news_narration_wide_margin.__wrapped__ = fn

    # ------------------------------------------------------------
    # item 1: normal PASS -> fallback発火しない
    # ------------------------------------------------------------
    def test_1_normal_pass_does_not_trigger_fallback(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            calls.append({"text": text, "out_path": out_path, "prefix_at_call": p9a.ENGLISH_STYLE_PREFIX})
            return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)
        self.assertEqual(len(calls), 1, "通常PASS時はcoreは1回しか呼ばれてはならない")
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["ending_clarity_fallback_used"])

    # ------------------------------------------------------------
    # item 2: normal NG -> retry PASS -> fallback発火しない
    # (retryはcore内部の既存ロジックのため、wrapperから見ればcoreが
    #  最終的にOKを返すケースと区別できない。同じ検証で足りる。)
    # ------------------------------------------------------------
    def test_2_core_internal_retry_pass_does_not_trigger_fallback(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            calls.append(1)
            # coreが内部で複数回試行した後に最終的にPASSしたことを模擬する
            # (attempts_logに複数attemptを含める)。
            return {"status": "OK", "asr_text": text,
                    "attempts_log": [{"attempt": 1, "asr_text": "wrong"}, {"attempt": 2, "asr_text": text}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["ending_clarity_fallback_used"])

    # ------------------------------------------------------------
    # item 3: normal NG -> retry NG(語尾脱落) -> Ending-Clarity発火
    # item 4: fallback PASS -> segment差し替え
    # ------------------------------------------------------------
    def test_3_and_4_ending_loss_ng_triggers_fallback_and_replaces_segment(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            prefix_now = p9a.ENGLISH_STYLE_PREFIX
            calls.append({"prefix": prefix_now, "max_attempts": max_attempts})
            if ending_clarity.ENDING_CLARITY_SUFFIX in prefix_now:
                # fallback呼び出し(Ending-Clarity instruction適用中)はPASS。
                return {"status": "OK", "asr_text": text,
                        "attempts_log": [{"attempt": 1, "asr_text": text}]}
            # 通常呼び出しはNG(語尾脱落ASR)。
            return {"status": "STOPPED", "reason": "3回試行しても不合格",
                    "attempts_log": [{"attempt": 1, "asr_text": ASR_ENDING_LOSS_TEXT},
                                      {"attempt": 2, "asr_text": ASR_ENDING_LOSS_TEXT},
                                      {"attempt": 3, "asr_text": ASR_ENDING_LOSS_TEXT}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)

        self.assertEqual(len(calls), 2, "通常呼び出し1回+fallback呼び出し1回のはず")
        self.assertNotIn(ending_clarity.ENDING_CLARITY_SUFFIX, calls[0]["prefix"], "通常呼び出しに常時適用されていない")
        self.assertIn(ending_clarity.ENDING_CLARITY_SUFFIX, calls[1]["prefix"], "fallback呼び出しにAND追加されている")
        self.assertTrue(calls[1]["prefix"].startswith(p9a.ENGLISH_STYLE_PREFIX),
                         "既存instructionを置換せずAND方式で追加している")
        self.assertEqual(calls[1]["max_attempts"], ending_clarity.FALLBACK_MAX_ATTEMPTS)

        self.assertEqual(result["status"], "OK", "fallback PASSがそのままsegmentの採用結果になる")
        self.assertTrue(result["ending_clarity_fallback_used"])
        self.assertEqual(result["instruction_type"], "ending_clarity_fallback")
        self.assertEqual(len(result["standard_attempts_log"]), 3)
        self.assertEqual(len(result["fallback_attempts_log"]), 1)
        # 恒久変更が残っていないこと。
        self.assertEqual(p9a.ENGLISH_STYLE_PREFIX, self.original_prefix)

    # ------------------------------------------------------------
    # item 5: fallback NG -> 既存STOP/NG処理へ
    # ------------------------------------------------------------
    def test_5_fallback_also_ng_falls_back_to_existing_stop(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            calls.append(p9a.ENGLISH_STYLE_PREFIX)
            return {"status": "STOPPED", "reason": "不合格",
                    "attempts_log": [{"attempt": i, "asr_text": ASR_ENDING_LOSS_TEXT}
                                      for i in range(1, max_attempts + 1)]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)

        self.assertEqual(len(calls), 2)
        self.assertNotEqual(result["status"], "OK")
        self.assertEqual(result["status"], "STOPPED", "元の(通常経路の)失敗statusをそのまま返す")
        self.assertTrue(result["ending_clarity_fallback_used"])
        self.assertTrue(result["ending_clarity_fallback_failed"])
        self.assertEqual(p9a.ENGLISH_STYLE_PREFIX, self.original_prefix, "失敗時も恒久変更は残らない")

    # ------------------------------------------------------------
    # item 6: 正常segmentは保持(このsegmentの処理が別segmentへ波及しない)
    # ------------------------------------------------------------
    def test_6_other_segment_untouched(self):
        calls = {"target": 0, "other": 0}

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            if out_path == self.out_path:
                calls["target"] += 1
                return {"status": "STOPPED", "reason": "NG",
                        "attempts_log": [{"attempt": 1, "asr_text": ASR_ENDING_LOSS_TEXT}]}
            calls["other"] += 1
            raise AssertionError("別segmentのcoreが呼ばれてはならない")

        self._install_fake_core(fake_core)
        ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)
        self.assertGreaterEqual(calls["target"], 1)
        self.assertEqual(calls["other"], 0)

    # ------------------------------------------------------------
    # item 7: attempt count正確(review_lockの累積カウントに正しく反映)
    # ------------------------------------------------------------
    def test_7_attempt_count_recorded_accurately_in_review_lock(self):
        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            if ending_clarity.ENDING_CLARITY_SUFFIX in p9a.ENGLISH_STYLE_PREFIX:
                return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}
            return {"status": "STOPPED", "reason": "NG",
                    "attempts_log": [{"attempt": 1, "asr_text": ASR_ENDING_LOSS_TEXT},
                                      {"attempt": 2, "asr_text": ASR_ENDING_LOSS_TEXT}]}

        self._install_fake_core(fake_core)
        ending_clarity.generate_news_narration_with_ending_clarity_fallback(CANONICAL_ENDING_LOSS_TEXT, self.out_path)

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        entry = review_lock._load_store(level_out_dir)["in_one_line"]
        # 通常2回 + fallback 1回 = 合計3回が正しく記録されること(二重会計なし)。
        self.assertEqual(entry["cumulative_tts_attempts"], 3)
        self.assertEqual(entry["state"], "RESOLVED")

    # ------------------------------------------------------------
    # item 8: assembly対象asset正確(fallback採用時も同一out_pathを使い続ける)
    # ------------------------------------------------------------
    def test_8_fallback_writes_to_same_out_path_used_by_assembly(self):
        seen_paths = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            seen_paths.append(out_path)
            if ending_clarity.ENDING_CLARITY_SUFFIX in p9a.ENGLISH_STYLE_PREFIX:
                return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}
            return {"status": "STOPPED", "reason": "NG",
                    "attempts_log": [{"attempt": 1, "asr_text": ASR_ENDING_LOSS_TEXT}]}

        self._install_fake_core(fake_core)
        ending_clarity.generate_news_narration_with_ending_clarity_fallback(CANONICAL_ENDING_LOSS_TEXT, self.out_path)
        self.assertTrue(all(p == self.out_path for p in seen_paths))

    # ------------------------------------------------------------
    # item 9: `opened` hardcodeなし(モジュール全体に対する確認)
    # ------------------------------------------------------------
    def test_9_no_opened_hardcode_in_executable_logic(self):
        # コメント上での説明的な言及("opened"を例として挙げる)は許容するが、
        # 実行されるコード行(比較・分岐条件)に"opened"という特定語への
        # hardcodeが無いことを確認する(コメント行・docstring行は除外)。
        import inspect
        source = inspect.getsource(ending_clarity)
        in_docstring = False
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.count('"""') % 2 == 1:
                in_docstring = not in_docstring
                continue
            if in_docstring or stripped.startswith("#") or not stripped:
                continue
            self.assertNotIn("opened", stripped.lower(),
                              f"実行コード行に'opened'のhardcodeが見つかりました: {line!r}")

    # ------------------------------------------------------------
    # item 10: fallback instruction常時適用なし(語尾脱落以外のNGでは発火しない)
    # ------------------------------------------------------------
    def test_10_fallback_not_applied_for_non_ending_loss_ng(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, max_extra_chars=15, disfluency_qa=False):
            calls.append(p9a.ENGLISH_STYLE_PREFIX)
            return {"status": "STOPPED", "reason": "内容誤り(語尾脱落ではない)",
                    "attempts_log": [{"attempt": 1, "asr_text": ASR_UNRELATED_MISMATCH_TEXT}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_news_narration_with_ending_clarity_fallback(
            CANONICAL_ENDING_LOSS_TEXT, self.out_path)
        self.assertEqual(len(calls), 1, "語尾脱落パターンが無い場合、fallbackは一切呼ばれてはならない")
        self.assertFalse(result["ending_clarity_fallback_used"])
        self.assertEqual(result["status"], "STOPPED")


CANONICAL_COMMENT2_TEXT = ("The studies suggest that a phone can affect attention even when you do not "
                            "check it. How does this pull appear in everyday life, especially for teenagers?")
ASR_COMMENT2_ENDING_LOSS_TEXT = ("The study suggests that a phone can affect attention even when you do not "
                                 "check it. How does this pull appear in everyday life, especially for teenagers?")


class CharonEndingClarityFallbackWiringTests(unittest.TestCase):
    """ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04: B1 Comment segment
    (voice01.generate_charon_english経路)向けfallback配線の受入テスト。
    News本文版と同じ設計方針を、style_prefix_override直接引数版で確認する
    (p9a.ENGLISH_STYLE_PREFIXのmonkeypatchは不要な設計)。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_ec_charon_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "b1b", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "comment_2.wav").replace("\\", "/")
        self.style_prefix_override = "CALM_PREVIEW_STYLE_PREFIX_FOR_TEST"
        self.original_core = voice01.generate_charon_english.__wrapped__

    def tearDown(self):
        voice01.generate_charon_english.__wrapped__ = self.original_core
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _install_fake_core(self, fn):
        voice01.generate_charon_english.__wrapped__ = fn

    def test_normal_pass_does_not_trigger_fallback(self):
        calls = []

        def fake_core(text, out_path, max_attempts=3, style_prefix_override=None, disfluency_qa=False):
            calls.append({"style_prefix_override": style_prefix_override})
            return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_charon_english_with_ending_clarity_fallback(
            CANONICAL_COMMENT2_TEXT, self.out_path, style_prefix_override=self.style_prefix_override)
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["ending_clarity_fallback_used"])

    def test_ending_loss_ng_triggers_fallback_and_appends_to_existing_style_prefix(self):
        # comment_2実データ相当: "studies"->"study"(複数マーカー脱落)で通常
        # 経路が3回ともNG -> Ending-Clarity fallbackが発火し、既存の
        # style_prefix_override(calm/clear/unhurried)を置換せずAND追加する
        # ことを確認する。
        calls = []

        def fake_core(text, out_path, max_attempts=3, style_prefix_override=None, disfluency_qa=False):
            calls.append({"style_prefix_override": style_prefix_override, "max_attempts": max_attempts})
            if style_prefix_override and ending_clarity.ENDING_CLARITY_SUFFIX in style_prefix_override:
                return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}
            return {"status": "STOPPED", "reason": "3回試行しても不合格",
                    "attempts_log": [{"attempt": i, "asr_text": ASR_COMMENT2_ENDING_LOSS_TEXT}
                                      for i in range(1, 4)]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_charon_english_with_ending_clarity_fallback(
            CANONICAL_COMMENT2_TEXT, self.out_path, style_prefix_override=self.style_prefix_override)

        self.assertEqual(len(calls), 2, "通常呼び出し1回+fallback呼び出し1回のはず")
        self.assertEqual(calls[0]["style_prefix_override"], self.style_prefix_override)
        self.assertIn(ending_clarity.ENDING_CLARITY_SUFFIX, calls[1]["style_prefix_override"])
        self.assertTrue(calls[1]["style_prefix_override"].startswith(self.style_prefix_override),
                         "既存のcalm/clear/unhurried instructionを置換せずAND方式で追加している")
        self.assertEqual(calls[1]["max_attempts"], ending_clarity.FALLBACK_MAX_ATTEMPTS)

        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["ending_clarity_fallback_used"])
        self.assertEqual(result["instruction_type"], "ending_clarity_fallback")

    def test_non_ending_loss_ng_does_not_trigger_fallback(self):
        # comment_3実データ相当("survey"->"surveys"、追加であり脱落ではない)
        # ではfallbackを発火させない回帰確認。
        calls = []

        def fake_core(text, out_path, max_attempts=3, style_prefix_override=None, disfluency_qa=False):
            calls.append(1)
            return {"status": "ASR_VALIDATION_UNCERTAIN", "asr_text": text,
                    "attempts_log": [{"attempt": 1, "asr_text": text.replace("survey", "surveys")}]}

        self._install_fake_core(fake_core)
        result = ending_clarity.generate_charon_english_with_ending_clarity_fallback(
            "The studies and the survey suggest that a phone can affect people.",
            self.out_path, style_prefix_override=self.style_prefix_override)
        self.assertEqual(len(calls), 1, "語尾脱落パターンが無い場合、fallbackは一切呼ばれてはならない")
        self.assertFalse(result["ending_clarity_fallback_used"])

    def test_attempt_count_recorded_accurately_in_review_lock(self):
        def fake_core(text, out_path, max_attempts=3, style_prefix_override=None, disfluency_qa=False):
            if style_prefix_override and ending_clarity.ENDING_CLARITY_SUFFIX in style_prefix_override:
                return {"status": "OK", "asr_text": text, "attempts_log": [{"attempt": 1, "asr_text": text}]}
            return {"status": "STOPPED", "reason": "NG",
                    "attempts_log": [{"attempt": 1, "asr_text": ASR_COMMENT2_ENDING_LOSS_TEXT},
                                      {"attempt": 2, "asr_text": ASR_COMMENT2_ENDING_LOSS_TEXT}]}

        self._install_fake_core(fake_core)
        ending_clarity.generate_charon_english_with_ending_clarity_fallback(
            CANONICAL_COMMENT2_TEXT, self.out_path, style_prefix_override=self.style_prefix_override)

        level_out_dir = review_lock._level_out_dir_from_out_path(self.out_path)
        entry = review_lock._load_store(level_out_dir)["comment_2"]
        self.assertEqual(entry["cumulative_tts_attempts"], 3)
        self.assertEqual(entry["state"], "RESOLVED")


if __name__ == "__main__":
    unittest.main()
