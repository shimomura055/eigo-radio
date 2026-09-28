# ============================================================
# er019_family_x_variable_role_style_wiring_01_test_01.py
# TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er019_family_x_variable_role_style_wiring_01_test_01 -v
#
# API呼び出し: 0(実TTS/ASR呼び出しは全てmock)。¥0。
#
# 対象: ユーザー正式決定(JA=J3、EN=E2、APPROVED_FOR_PRODUCTION、
# TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02)を、既存のPRODUCTION_WIRED
# 済み6-role style機構(speech_metadata_flash_lite backend限定)へ配線
# したことを確認する。
#   (a) FAMILY_X_ROLE_STYLE_JA / E2 3roleがer044のJ3/E2と逐語一致
#   (b) 既定backendではJA style overrideがNone(従来PREFIX)、Flash-Lite
#       明示時のみJ3
#   (c) generate_a2_japanese_with_reading_safetyの既定呼び出しが従来と
#       同一のprefix(None=JAPANESE_STYLE_PREFIX)を転送する
#   (d) shell固定phraseのstyle解決関数が本変更の影響を受けない(逐語不変)
#   (e) Key Phrase系Roleが無変更
#   (f) fallback経路がoverrideの影響を受けない(既存テキスト流用のまま)
from __future__ import annotations

import json
import os
import shutil
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_sing01_news_tail_fix as news_tail_fix_mod
import er003_v1_sing01_point_headings_aoede as point_headings_mod
import er003_v1_sing01_voice01_generate as voice01_mod
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er019_family_x_audio_production_runner_01 as runner
import er033_tts_flash_lite_backend_wiring_01 as flw
import er033_tts_flash_lite_family_x_styles_01 as fl_styles
import er044_tts_variable_spoken_role_style_trial_02 as trial02


def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x"}


class J3E2VerbatimMatchTests(unittest.TestCase):
    """(a) Production定数がTrial-02実測・ユーザー承認値と逐語一致すること。"""

    def test_family_x_role_style_ja_matches_trial02_j3_verbatim(self):
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_JA, trial02.J_PATTERN_STYLES["J3"])

    def test_family_x_role_style_en_e2_roles_match_trial02_verbatim(self):
        for role in ("TOPIC_INTRO", "FULL_STORY", "IN_ONE_LINE"):
            with self.subTest(role=role):
                self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN[role], trial02.E_PATTERN_STYLES[role]["E2"])

    def test_unaffected_en_roles_unchanged(self):
        # PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため対象外(不変)。
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["PREVIEW"], "calm, conversational")
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["COMMENT"], "calm, conversational")
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"], "brief and clear")


class P9aJapaneseBranchSymmetryTests(unittest.TestCase):
    """p9a.generate_narration_snippet()のja分岐がen分岐と対称化されたこと
    (style_prefix_override or JAPANESE_STYLE_PREFIX)。"""

    def test_ja_default_override_none_uses_japanese_style_prefix(self):
        captured = {}

        def fake_call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None):
            captured["prompt"] = prompt
            return None, 0, False, "forced_stop_for_test"

        with mock.patch.object(p9a.common, "_call_tts_with_retry", side_effect=fake_call_tts_with_retry):
            p9a.generate_narration_snippet("こんにちは。", "ja", "dummy_out.wav")
        self.assertEqual(captured["prompt"], p9a.p4c.build_tts_prompt("こんにちは。", p9a.JAPANESE_STYLE_PREFIX))

    def test_ja_explicit_override_replaces_japanese_style_prefix(self):
        captured = {}

        def fake_call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None):
            captured["prompt"] = prompt
            return None, 0, False, "forced_stop_for_test"

        with mock.patch.object(p9a.common, "_call_tts_with_retry", side_effect=fake_call_tts_with_retry):
            p9a.generate_narration_snippet(
                "こんにちは。", "ja", "dummy_out.wav",
                style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        self.assertEqual(
            captured["prompt"], p9a.p4c.build_tts_prompt("こんにちは。", fl_styles.FAMILY_X_ROLE_STYLE_JA))
        # 置換方式であること(長文PREFIXとの併記ではない、Trial-02と同一)。
        self.assertNotIn(p9a.JAPANESE_STYLE_PREFIX, captured["prompt"].replace(
            p9a.p4c.build_tts_prompt("こんにちは。", fl_styles.FAMILY_X_ROLE_STYLE_JA), ""))


class RunnerBackendGateTests(unittest.TestCase):
    """(b) Family Xランナーの_role_style_ja()相当の挙動: 既定backendでは
    Noneを転送(従来PREFIX維持)、Flash-Lite明示時のみJ3を転送する。"""

    def _make_a2_dir(self, tmpdir):
        parts = {
            "title": "Sample Title", "title_tts": "Sample Title",
            "part1": "Part one text.", "heading1": "Heading One.", "body2": "Body two text.",
            "heading2": "Heading Two.", "body3": "Body three text.", "in_one_line": "In one line text.",
        }
        support = {"preview": "プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。",
                   "comment_3": "コメント3。", "comment_4": "コメント4。"}
        a2_dir = os.path.join(tmpdir, "a2")
        os.makedirs(a2_dir, exist_ok=True)
        with open(os.path.join(a2_dir, "parts.json"), "w", encoding="utf-8") as f:
            json.dump(parts, f)
        with open(os.path.join(a2_dir, "a2_support_texts.json"), "w", encoding="utf-8") as f:
            json.dump(support, f)
        return a2_dir

    def test_flash_lite_backend_passes_j3_to_title_preview_and_comments(self):
        # FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、Opus L2所見MAJOR-1
        # 是正・ユーザー正式決定): japanese_titleもpreview/comment_1-4と
        # 同一のJ3を受け取るよう統一した(従来はjapanese_titleだけ対象外
        # だったが、これを撤回)。
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_ja_role_style_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok) as ja_mock, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok):
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル",
                                                      tts_backend="speech_metadata_flash_lite")

            # japanese_title(1回目の呼び出し)を含む全6回がJ3を受け取る。
            for call in ja_mock.call_args_list:
                self.assertEqual(call.kwargs.get("style_prefix_override"), fl_styles.FAMILY_X_ROLE_STYLE_JA)
            self.assertEqual(len(ja_mock.call_args_list), 6)  # japanese_title + preview + comment_1-4
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_default_backend_does_not_pass_j3_to_preview_and_comments(self):
        tmpdir = tempfile.mkdtemp(prefix="family_x_a2_ja_role_style_default_")
        try:
            self._make_a2_dir(tmpdir)
            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2"), \
                 mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback",
                                    side_effect=_ok), \
                 mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                    side_effect=_ok) as ja_mock, \
                 mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok):
                runner.generate_family_x_a2_segments(tmpdir, "日本語タイトル")  # 既定backend

            for call in ja_mock.call_args_list:
                self.assertIsNone(call.kwargs.get("style_prefix_override"))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class ReadingSafetyDefaultForwardingTests(unittest.TestCase):
    """(c) generate_a2_japanese_with_reading_safetyの既定呼び出しが従来と
    同一のprefix(override=None)をgenerate_a2_japanese_with_fallbackへ
    転送すること(モック)。"""

    def test_default_call_forwards_style_prefix_override_none(self):
        with mock.patch.object(n3_tts, "generate_a2_japanese_with_fallback",
                                side_effect=_ok) as fallback_mock:
            n3_tts.generate_a2_japanese_with_reading_safety("テスト文", "dummy.wav", "テス")
        self.assertIn("style_prefix_override", fallback_mock.call_args.kwargs)
        self.assertIsNone(fallback_mock.call_args.kwargs["style_prefix_override"])

    def test_explicit_override_forwarded_unchanged(self):
        with mock.patch.object(n3_tts, "generate_a2_japanese_with_fallback",
                                side_effect=_ok) as fallback_mock:
            n3_tts.generate_a2_japanese_with_reading_safety(
                "テスト文", "dummy.wav", "テス", style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        self.assertEqual(fallback_mock.call_args.kwargs["style_prefix_override"], fl_styles.FAMILY_X_ROLE_STYLE_JA)


class ShellFixedPhraseUnaffectedTests(unittest.TestCase):
    """(d) 固定Master phrase(shell)のstyle解決関数が本タスク
    (TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01)の影響を受けない
    (逐語不変)ことを確認する。

    FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29)により
    _resolve_shell_english_style_prefix_overrideの引数にname(phrase名)が
    追加され、welcome以外の8 English phraseはChampion style map
    (SHELL_CHAMPION_STYLE_BY_PHRASE_EN)経由の文言へ切り替わった
    (この置き換え自体が本Championタスクの目的であり、意図した破壊的変更)。
    本テストの目的である「welcomeの解決結果が不変」の検証は維持し、
    旧シグネチャ呼び出し・旧一律style期待だけを更新する。"""

    def test_shell_english_style_resolution_literal_unchanged(self):
        self.assertIsNone(
            shared_narration._resolve_shell_english_style_prefix_override("welcome", "structured_separation"))
        self.assertEqual(
            shared_narration._resolve_shell_english_style_prefix_override("welcome", "speech_metadata_flash_lite"),
            "natural, clear, conversational")
        # FAMILY_X_ROLE_STYLE_EN_FALLBACK自体もJ3/E2配線の対象外(不変)。
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK, ["natural, clear, conversational", "clear"])

    def test_shell_version_constant_unchanged(self):
        self.assertEqual(shared_narration.SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION,
                          "v2_flash_lite_short_style")


class KeyPhraseRoleUnchangedTests(unittest.TestCase):
    """(e) Key Phrase系(A2/B1双方)は本変更の対象外であり、
    generate_a2_japanese_with_reading_safety呼び出しにstyle_prefix_override
    を渡さない(=既存JAPANESE_STYLE_PREFIXのまま)ことを確認する。"""

    def test_a2_key_phrase_segments_do_not_receive_style_prefix_override(self):
        kp = {"items": [{"rank": 1, "used_form": "opt out", "japanese_gloss": "見送る"}]}
        with mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=_ok), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety",
                                side_effect=_ok) as ja_mock, \
             mock.patch.object(runner.n3_tts, "resolve_key_phrase_ja_gloss_tts",
                                return_value=("みおくる", False)):
            runner._generate_key_phrase_segments_a2(kp, "dummy_dir", tts_backend="speech_metadata_flash_lite")
        self.assertNotIn("style_prefix_override", ja_mock.call_args_list[0].kwargs)


class FallbackPathUnaffectedTests(unittest.TestCase):
    """(f) fallback(minimal instruction)経路はstyle_prefix_overrideの
    影響を受けない(FAMILY-X-02 D-1の方針どおり、既存テキスト流用のまま)。"""

    def test_fallback_minimal_instruction_ignores_style_prefix_override(self):
        standard_stopped = {"status": "STOPPED", "reason": "forced", "attempts_log": []}
        with mock.patch.object(n3_tts.c, "generate_narration_snippet_verified_strict",
                                return_value=standard_stopped) as standard_mock, \
             mock.patch.object(n3_tts, "_generate_a2_japanese_minimal_instruction",
                                side_effect=_ok) as minimal_mock:
            n3_tts.generate_a2_japanese_with_fallback(
                "テスト文", "dummy.wav", "テス", style_prefix_override=fl_styles.FAMILY_X_ROLE_STYLE_JA)
        # 標準経路へはoverrideが転送される。
        self.assertEqual(standard_mock.call_args.kwargs.get("style_prefix_override"),
                          fl_styles.FAMILY_X_ROLE_STYLE_JA)
        # fallback(minimal instruction)経路はstyle_prefix_overrideを一切
        # 受け取らない(既存テキスト_A2_JA_MINIMAL_INSTRUCTION_PREFIX流用のまま)。
        self.assertNotIn("style_prefix_override", minimal_mock.call_args.kwargs)


# ============================================================
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、2026-09-29)
# Opus L2所見MAJOR-3是正: 可変segment reuse判定のcache version guard。
# ============================================================
class CacheVersionGuardTests(unittest.TestCase):
    """_generate_or_reuse()がcachedのトップレベル"style_version"を見て、
    現行FAMILY_X_VARIABLE_ROLE_STYLE_VERSIONと不一致・欠落の場合は可変
    segmentのreuseを一切行わないこと(shell/Key Phrase側の_generate_or_
    reuse_kpは対象外で無変更のまま)を確認する。"""

    def test_reuse_skipped_when_style_version_mismatches(self):
        cached = {"style_version": "old_version_before_this_fix",
                  "segments": {"seg": {"status": "OK", "canonical_text": "x"}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK", "canonical_text": "x"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse(cached, "seg", "dummy.wav", gen, expected_text="x")
        self.assertEqual(calls["n"], 1)
        self.assertNotIn("reused_from_previous_run", result)

    def test_reuse_skipped_when_style_version_missing(self):
        # 本是正以前に保存されたcache(style_versionキー自体が無い)。
        cached = {"segments": {"seg": {"status": "OK", "canonical_text": "x"}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK", "canonical_text": "x"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse(cached, "seg", "dummy.wav", gen, expected_text="x")
        self.assertEqual(calls["n"], 1)
        self.assertNotIn("reused_from_previous_run", result)

    def test_reuse_allowed_when_style_version_matches(self):
        cached = {"style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
                  "segments": {"seg": {"status": "OK", "canonical_text": "x"}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK", "canonical_text": "x"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse(cached, "seg", "dummy.wav", gen, expected_text="x")
        self.assertEqual(calls["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))

    def test_reuse_still_allowed_when_cached_is_none(self):
        # cache自体が存在しない(新規out-dir初回run)場合は従来どおり
        # generate_fn()を呼ぶ(version guardの新設で新規runへの影響なし)。
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK", "canonical_text": "x"}

        result = runner._generate_or_reuse(None, "seg", "dummy_nonexistent.wav", gen, expected_text="x")
        self.assertEqual(calls["n"], 1)
        self.assertNotIn("reused_from_previous_run", result)

    def test_key_phrase_reuse_unaffected_by_style_version_guard(self):
        # (e)と対称: shell固定phrase・Key Phraseのreuse判定
        # (_generate_or_reuse_kp)はstyle_versionを一切参照しない(不変)。
        cached = {"style_version": "old_version_before_this_fix",
                  "key_phrases": {"1": {"english": {"status": "OK"}}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse_kp(cached, 1, "english", "dummy.wav", gen)
        self.assertEqual(calls["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))


# ============================================================
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W3、2026-09-29)
# Opus L2所見MAJOR-2/MINOR-A是正: Advanced(B1B)英語経路
# (er003_v1_sing01_voice01_generate.py/news_tail_fix.py/
# point_headings_aoede.py)の戻り値へruntime evidence(style_prefix/
# tts_model_id/voice)が追加されたことを確認する。
#
# 設計上の注記(MINOR-B): 本テストは各関数単体をmockで固めた単体テスト
# であり、「runner配線」(japanese_title/preview等がどのstyleを選ぶか)の
# 検証はRunnerBackendGateTests側が担う。実際にFlash-Lite backendで生成
# した音声にstyleが正しく反映されていることのruntime実測(E2E)は、本W3
# の範囲外(後続のE2Eで取得)。
# ============================================================
_FAKE_CLS_EXACT_MATCH = types.SimpleNamespace(classification="EXACT_MATCH")


class RuntimeEvidenceKeysTests(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.mkdtemp(prefix="family_x_runtime_evidence_")
        self._out_path = os.path.join(self._tmpdir, "dummy_out.wav")

    def tearDown(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_voice01_generate_charon_english_returns_evidence_keys(self):
        samples = (np.sin(np.linspace(0, 6.28, 2400)) * 0.05).astype(np.float64)
        with mock.patch.object(flw, "resolve_tts_call_and_prompt",
                                return_value=(lambda prompt: b"\x00\x00" * 100, "dummy prompt")), \
             mock.patch.object(voice01_mod.common, "_call_tts_with_retry",
                                return_value=(b"\x00\x00" * 100, 0, True, None)), \
             mock.patch.object(voice01_mod.p3u, "trim_english_keyword_silence",
                                return_value=(samples, {"raw_duration_seconds": 1.0})), \
             mock.patch.object(voice01_mod.routing, "transcribe", return_value=("hello there.", None)), \
             mock.patch.object(voice01_mod.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(True, False, _FAKE_CLS_EXACT_MATCH)):
            # override指定時: 実値がstyle_prefixへ記録される。
            result_override = voice01_mod.generate_charon_english.__wrapped__(
                "hello there.", self._out_path, style_prefix_override="calm, conversational")
            self.assertEqual(result_override["status"], "OK")
            self.assertEqual(result_override["voice"], voice01_mod.CHARON)
            self.assertIn("tts_model_id", result_override)
            self.assertEqual(result_override["style_prefix"], "calm, conversational")

            # 既定(override無し)時: 長文prefixの実値ではなくラベルを記録する
            # (Opus L2所見MINOR-A是正)。
            result_default = voice01_mod.generate_charon_english.__wrapped__(
                "hello there.", self._out_path)
            self.assertEqual(result_default["status"], "OK")
            self.assertEqual(result_default["style_prefix"], "<default:ENGLISH_STYLE_PREFIX>")

    def test_news_tail_fix_generate_news_narration_returns_evidence_keys(self):
        samples = (np.sin(np.linspace(0, 6.28, 2400)) * 0.05).astype(np.float64)
        with mock.patch.object(flw, "resolve_tts_call_and_prompt",
                                return_value=(lambda prompt: b"\x00\x00" * 100, "dummy prompt")), \
             mock.patch.object(news_tail_fix_mod.common, "_call_tts_with_retry",
                                return_value=(b"\x00\x00" * 100, 0, True, None)), \
             mock.patch.object(news_tail_fix_mod.p3u, "trim_english_keyword_silence",
                                return_value=(samples, {"raw_duration_seconds": 1.0})), \
             mock.patch.object(news_tail_fix_mod.routing, "transcribe", return_value=("hello there.", None)), \
             mock.patch.object(news_tail_fix_mod.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(True, False, _FAKE_CLS_EXACT_MATCH)):
            result_override = news_tail_fix_mod.generate_news_narration_wide_margin.__wrapped__(
                "hello there.", self._out_path, style_prefix_override="clear")
            self.assertEqual(result_override["status"], "OK")
            self.assertEqual(result_override["voice"], news_tail_fix_mod.p9a.VOICE_NAME)
            self.assertIn("tts_model_id", result_override)
            self.assertEqual(result_override["style_prefix"], "clear")

            result_default = news_tail_fix_mod.generate_news_narration_wide_margin.__wrapped__(
                "hello there.", self._out_path)
            self.assertEqual(result_default["status"], "OK")
            self.assertEqual(result_default["style_prefix"], "<default:ENGLISH_STYLE_PREFIX>")

    def test_point_headings_aoede_generate_returns_evidence_keys(self):
        samples = (np.sin(np.linspace(0, 6.28, 2400)) * 0.05).astype(np.float64)
        with mock.patch.object(flw, "resolve_tts_call_and_prompt",
                                return_value=(lambda prompt: b"\x00\x00" * 100, "dummy prompt")), \
             mock.patch.object(point_headings_mod.common, "_call_tts_with_retry",
                                return_value=(b"\x00\x00" * 100, 0, True, None)), \
             mock.patch.object(point_headings_mod.p3u, "trim_english_keyword_silence",
                                return_value=(samples, {"raw_duration_seconds": 1.0})), \
             mock.patch.object(point_headings_mod.routing, "transcribe", return_value=("First point.", None)), \
             mock.patch.object(point_headings_mod.secondary_asr, "evaluate_attempt_with_cascade",
                                return_value=(True, False, _FAKE_CLS_EXACT_MATCH)):
            result_override = point_headings_mod.generate.__wrapped__(
                "First point.", self._out_path, disfluency_qa=False, style_prefix_override="brief and clear")
            self.assertEqual(result_override["status"], "OK")
            self.assertEqual(result_override["voice"], point_headings_mod.AOEDE)
            self.assertIn("tts_model_id", result_override)
            self.assertEqual(result_override["style_prefix"], "brief and clear")

            result_default = point_headings_mod.generate.__wrapped__(
                "First point.", self._out_path, disfluency_qa=False)
            self.assertEqual(result_default["status"], "OK")
            self.assertEqual(result_default["style_prefix"], "<default:ENGLISH_STYLE_PREFIX>")


class P9aDefaultLabelTests(unittest.TestCase):
    """(MINOR-A是正) p9a.generate_narration_snippet()のstyle_prefixが、
    override指定時は実値、既定時は短いラベルになること。"""

    def test_override_records_actual_value_en(self):
        samples = (np.sin(np.linspace(0, 6.28, 2400)) * 0.05).astype(np.float64)
        tmpdir = tempfile.mkdtemp(prefix="p9a_default_label_")
        try:
            out_path = os.path.join(tmpdir, "dummy_out.wav")
            with mock.patch.object(p9a.common, "_call_tts_with_retry",
                                    return_value=(b"\x00\x00" * 100, 0, True, None)), \
                 mock.patch.object(p9a, "p3u") as p3u_mock:
                p3u_mock.trim_english_keyword_silence.return_value = (samples, {"raw_duration_seconds": 1.0})
                p3u_mock.EN_TRIM_SAFETY_MARGIN_SECONDS = 0.08
                result_override = p9a.generate_narration_snippet(
                    "hello", "en", out_path, style_prefix_override="calm, conversational")
                result_default = p9a.generate_narration_snippet("hello", "en", out_path)
            self.assertEqual(result_override["style_prefix"], "calm, conversational")
            self.assertEqual(result_default["style_prefix"], "<default:ENGLISH_STYLE_PREFIX>")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        J3E2VerbatimMatchTests, P9aJapaneseBranchSymmetryTests, RunnerBackendGateTests,
        ReadingSafetyDefaultForwardingTests, ShellFixedPhraseUnaffectedTests,
        KeyPhraseRoleUnchangedTests, FallbackPathUnaffectedTests,
        CacheVersionGuardTests, RuntimeEvidenceKeysTests, P9aDefaultLabelTests,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner_ = unittest.TextTestRunner(verbosity=2)
    result = runner_.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
