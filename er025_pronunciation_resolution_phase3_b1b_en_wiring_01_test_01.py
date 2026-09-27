# ============================================================
# er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01.py
# PRONUNCIATION-RESOLUTION-PHASE-3-B1B-EN-WIRING-AND-JA-VALIDATOR-PUNCT-01
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest \
#       er025_pronunciation_resolution_phase3_b1b_en_wiring_01_test_01 -v
#
# API呼び出し: 0(全てmock/cache-onlyのER-025 disable_web_lookup_for_test()
# コンテキストマネージャ使用、実TTS/ASR/LLM呼び出しなし)。
#
# 対象(OPEN-197是正): voice01.generate_charon_english()へ既存A2英語標準
# 経路(generate_narration_snippet_verified_strict)と同一のPronunciation
# Ledger hookを、opt-in引数enable_pronunciation_resolver(既定False)で追加。
# 対象(OPEN-198是正): repro01.generate_english_component_minimal_
# instruction()へ同じhookを同じopt-in引数で追加。news_tail_fix.
# generate_news_narration_wide_margin()はこの引数を技術的fallback
# (発話区間検出失敗時のみ)呼び出しへそのまま転送するだけ。
# Family X production runner(er019_family_x_audio_production_runner_01.py)
# のB1B生成関数のみが明示的にTrueを渡すこと、既存Family A/B/C legacy
# 呼び出し元は無変更のままであることを確認する。
#
# 対象(Stage 3d副次発見の是正): er003_v1_n3_01_tts_generate.
# generate_a2_japanese_with_fallback()に review_lock.guarded_generate("ja")
# を追加し、標準経路のみでrecord_outcome()が確定してしまいfallback成功が
# Lock storeへ反映されない既存ギャップを是正する(状態ファイルは書き
# 換えない、次回実行時から正しく記録されることを確認する)。
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as n3_tts
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er003_v1_sing01_voice01_generate as voice01
import er006_pronunciation_ledger_01 as ledger
import er011_human_review_lock_01 as review_lock
import er025_entity_pronunciation_resolver_core_01 as pron_resolver_core


def _use_temp_ledger(test_fn):
    orig_path = ledger.LEDGER_PATH
    tmp_path = "er006_output/_test_pronunciation_resolver_phase3_b1b_tmp/ledger.json"
    import os
    if os.path.exists(os.path.dirname(tmp_path)):
        shutil.rmtree(os.path.dirname(tmp_path))
    ledger.LEDGER_PATH = tmp_path
    pron_resolver_core.reset_run_caches()
    try:
        test_fn()
    finally:
        ledger.LEDGER_PATH = orig_path
        pron_resolver_core.reset_run_caches()
        if os.path.exists(os.path.dirname(tmp_path)):
            shutil.rmtree(os.path.dirname(tmp_path))


def _fail_if_web_lookup_called(*_a, **_kw):
    raise AssertionError("cache-onlyのはずのtestでweb lookupが呼ばれた(意図しないAPI支出)")


class GenerateCharonEnglishResolverWiringTests(unittest.TestCase):
    """OPEN-197是正: voice01.generate_charon_english()のopt-in resolver配線。
    実TTS/ASRはすべてmockし、resolver配線ロジック(style_prefixの augment)
    だけを単体で確認する。"""

    def _run(self, text: str, enable: bool, out_path: str = "dummy_out.wav"):
        """generate_charon_english.__wrapped__を、実TTS/ASR/trim/measureを
        すべてmockして1回のattempt(max_attempts=1)で即PASSさせる。呼び出し
        直後に実際にbuild_tts_promptへ渡されたstyle_prefixをキャプチャする。"""
        captured = {}

        def fake_build_tts_prompt(txt, style_prefix):
            captured["style_prefix"] = style_prefix
            return style_prefix + txt

        with mock.patch.object(voice01, "p4c") as fake_p4c, \
             mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
             mock.patch.object(voice01.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)), \
             mock.patch.object(voice01.common, "pcm_bytes_to_float_mono", return_value=[0.0]), \
             mock.patch.object(voice01.p3u, "trim_english_keyword_silence",
                                return_value=([0.0], {"raw_duration_seconds": 1.0})), \
             mock.patch.object(voice01.safety, "detect_duration_anomaly", return_value={"is_anomaly": False}), \
             mock.patch.object(voice01.common, "write_wav_float"), \
             mock.patch.object(voice01.routing, "transcribe", return_value=(text, None)), \
             mock.patch.object(voice01.secondary_asr, "evaluate_attempt_with_cascade") as fake_cascade, \
             mock.patch.object(voice01.dq18, "apply_disfluency_gate",
                                return_value={"verified": True, "disfluency_checked": False,
                                              "disfluency_evidence": None}), \
             mock.patch.object(voice01.common, "measure_metrics", return_value={"clipping_detected": False}), \
             mock.patch.object(voice01.review_lock, "save_tts_attempt_audio", return_value=None):
            fake_p4c.build_tts_prompt.side_effect = fake_build_tts_prompt
            fake_cls = mock.Mock()
            fake_cls.classification = "EXACT_MATCH"
            fake_cascade.return_value = (True, False, fake_cls)
            result = voice01.generate_charon_english.__wrapped__(
                text, out_path, max_attempts=1, enable_pronunciation_resolver=enable)
        return result, captured.get("style_prefix")

    def test_default_disabled_resolver_never_invoked_and_prompt_unchanged(self):
        def run():
            key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
            ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
            with mock.patch.object(pron_resolver_core, "resolve_and_augment_en_style_prefix",
                                    side_effect=AssertionError(
                                        "enable_pronunciation_resolver=False(既定)ではresolverを"
                                        "呼んではいけない")):
                result, style_prefix = self._run("We spoke with Ottoni about the plan.", enable=False)
            self.assertEqual(result["status"], "OK")
            self.assertIsNone(result.get("en_pronunciation_resolver_info"))
            self.assertNotIn("Ottoni", style_prefix or "")
        _use_temp_ledger(run)

    def test_enabled_with_cache_hit_augments_style_prefix(self):
        def run():
            with pron_resolver_core.disable_web_lookup_for_test():
                key = ledger.LedgerKey(surface="Ottoni", entity_type="person")
                ledger.upsert(key, {"pronunciation_hint": "oh-TOH-nee", "confidence": "high"})
                result, style_prefix = self._run("We spoke with Ottoni about the plan.", enable=True)
            self.assertEqual(result["status"], "OK")
            info = result.get("en_pronunciation_resolver_info")
            self.assertIsNotNone(info)
            self.assertTrue(info["hints_applied"])
            self.assertIn("Ottoni", style_prefix)
            self.assertIn("oh-TOH-nee", style_prefix)
        _use_temp_ledger(run)

    def test_enabled_no_matching_hint_leaves_prompt_unchanged(self):
        def run():
            with pron_resolver_core.disable_web_lookup_for_test():
                result, style_prefix = self._run("This text mentions nobody special.", enable=True)
            self.assertEqual(result["status"], "OK")
            info = result.get("en_pronunciation_resolver_info")
            self.assertIsNotNone(info)
            self.assertFalse(info["hints_applied"])
        _use_temp_ledger(run)


class GenerateEnglishComponentMinimalInstructionResolverWiringTests(unittest.TestCase):
    """OPEN-198是正: repro01.generate_english_component_minimal_instruction()
    のopt-in resolver配線。"""

    def _run(self, text: str, enable: bool, out_path: str = "dummy_min.wav"):
        captured = {}

        def fake_build_tts_prompt(txt, style_prefix):
            captured["style_prefix"] = style_prefix
            return style_prefix + txt

        with mock.patch.object(repro01, "p4c") as fake_p4c, \
             mock.patch.object(repro01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
             mock.patch.object(repro01.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)), \
             mock.patch.object(repro01.common, "pcm_bytes_to_float_mono", return_value=[0.0]), \
             mock.patch.object(repro01.p3u, "trim_english_keyword_silence",
                                return_value=([0.0], {"raw_duration_seconds": 1.0})), \
             mock.patch.object(repro01.safety, "detect_duration_anomaly", return_value={"is_anomaly": False}), \
             mock.patch.object(repro01.common, "write_wav_float"), \
             mock.patch.object(repro01.common, "measure_metrics", return_value={"clipping_detected": False}), \
             mock.patch.object(repro01.p8a, "sha256_file", return_value="deadbeef"):
            fake_p4c.build_tts_prompt.side_effect = fake_build_tts_prompt
            result = repro01.generate_english_component_minimal_instruction(
                text, out_path, enable_pronunciation_resolver=enable)
        return result, captured.get("style_prefix")

    def test_default_disabled_resolver_never_invoked_and_prompt_unchanged(self):
        def run():
            key = ledger.LedgerKey(surface="Toteme", entity_type="product")
            ledger.upsert(key, {"pronunciation_hint": "toh-TEHM", "confidence": "high"})
            with mock.patch.object(pron_resolver_core, "resolve_and_augment_en_style_prefix",
                                    side_effect=AssertionError(
                                        "enable_pronunciation_resolver=False(既定)ではresolverを"
                                        "呼んではいけない")):
                result, style_prefix = self._run("The brand Toteme was mentioned.", enable=False)
            self.assertEqual(result["status"], "OK")
            self.assertIsNone(result.get("en_pronunciation_resolver_info"))
            self.assertNotIn("Toteme", style_prefix or "")
        _use_temp_ledger(run)

    def test_enabled_with_cache_hit_augments_instruction(self):
        def run():
            with pron_resolver_core.disable_web_lookup_for_test():
                key = ledger.LedgerKey(surface="Toteme", entity_type="product")
                ledger.upsert(key, {"pronunciation_hint": "toh-TEHM", "confidence": "high"})
                result, style_prefix = self._run("The brand Toteme was mentioned.", enable=True)
            self.assertEqual(result["status"], "OK")
            info = result.get("en_pronunciation_resolver_info")
            self.assertIsNotNone(info)
            self.assertTrue(info["hints_applied"])
            self.assertIn("Toteme", style_prefix)
            self.assertIn("toh-TEHM", style_prefix)
        _use_temp_ledger(run)

    def test_enabled_no_matching_hint_leaves_prompt_unchanged(self):
        def run():
            with pron_resolver_core.disable_web_lookup_for_test():
                result, style_prefix = self._run("This text mentions nobody special.", enable=True)
            self.assertEqual(result["status"], "OK")
            info = result.get("en_pronunciation_resolver_info")
            self.assertIsNotNone(info)
            self.assertFalse(info["hints_applied"])
        _use_temp_ledger(run)


class GenerateNewsNarrationWideMarginResolverThreadingTests(unittest.TestCase):
    """OPEN-198是正: news_tail_fix.generate_news_narration_wide_margin()の
    enable_pronunciation_resolver引数が、技術的fallback(発話区間検出失敗
    時のみ)呼び出しへそのまま転送されること(この関数自身の標準
    ENGLISH_STYLE_PREFIX経路は無変更のまま)を確認する。"""

    def _run(self, enable: bool):
        with mock.patch.object(news_tail_fix.safety, "detect_prohibited_symbols", return_value=[]), \
             mock.patch.object(news_tail_fix.safety, "symbol_gate_requires_stop", return_value=False), \
             mock.patch.object(news_tail_fix.retry_primitive, "maybe_cooldown_before_attempt", return_value=None), \
             mock.patch.object(news_tail_fix.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
             mock.patch.object(news_tail_fix.p4c, "build_tts_prompt", return_value="prompt"), \
             mock.patch.object(news_tail_fix.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)), \
             mock.patch.object(news_tail_fix.common, "pcm_bytes_to_float_mono", return_value=[0.0]), \
             mock.patch.object(news_tail_fix.p3u, "trim_english_keyword_silence", return_value=(None, None)), \
             mock.patch.object(news_tail_fix, "repro01") as fake_repro01:
            fake_repro01.generate_english_component_minimal_instruction.return_value = {
                "status": "STOPPED", "reason": "fallbackもtestでは失敗させ、continueさせる"}
            news_tail_fix.generate_news_narration_wide_margin(
                "Some canonical text.", "dummy_wide.wav", max_attempts=1,
                enable_pronunciation_resolver=enable)
            return fake_repro01.generate_english_component_minimal_instruction

    def test_default_disabled_forwards_false(self):
        mock_fn = self._run(enable=False)
        mock_fn.assert_called_once()
        _, kwargs = mock_fn.call_args
        self.assertFalse(kwargs.get("enable_pronunciation_resolver"))

    def test_enabled_forwards_true(self):
        mock_fn = self._run(enable=True)
        mock_fn.assert_called_once()
        _, kwargs = mock_fn.call_args
        self.assertTrue(kwargs.get("enable_pronunciation_resolver"))


class FamilyXRunnerKwargWiringTests(unittest.TestCase):
    """Family X production runnerのB1B TTS生成が、generate_charon_english/
    generate_news_narration_wide_marginへ明示的にenable_pronunciation_
    resolver=Trueを渡すこと(Family A/B/C legacy呼び出し元は本管理IDでは
    一切編集していない=無変更のまま)を確認する。実TTS/ASR呼び出しは
    すべてmockする。"""

    def test_b1_segments_pass_enable_pronunciation_resolver_true(self):
        import os
        import shutil
        import tempfile

        import er019_family_x_audio_production_runner_01 as runner

        tmpdir = tempfile.mkdtemp(prefix="family_x_b1_resolver_wiring_")
        try:
            parts = {
                "title": "Sample Title", "part1": "Part one text.",
                "heading1": "Heading One.", "body2": "Body two text.",
                "heading2": "Heading Two.", "body3": "Body three text.",
                "in_one_line": "In one line text.",
            }
            support = {"preview": "Preview.", "comment_1": "C1.", "comment_2": "C2.",
                       "comment_3": "C3.", "comment_4": "C4."}
            b1b_dir = os.path.join(tmpdir, "b1b")
            os.makedirs(b1b_dir, exist_ok=True)
            with open(os.path.join(b1b_dir, "parts.json"), "w", encoding="utf-8") as f:
                runner.json.dump(parts, f)
            with open(os.path.join(b1b_dir, "b1_support_texts.json"), "w", encoding="utf-8") as f:
                runner.json.dump(support, f)

            def _ok(*_a, **_kw):
                return {"status": "OK", "canonical_text": "x"}

            with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_b1"), \
                 mock.patch.object(runner.voice01, "generate_charon_english", side_effect=_ok) as charon_mock, \
                 mock.patch.object(runner.news_tail_fix, "generate_news_narration_wide_margin",
                                    side_effect=_ok) as wide_margin_mock, \
                 mock.patch.object(runner.point_headings, "generate", side_effect=_ok):
                runner.generate_family_x_b1_segments(tmpdir)

            for call in charon_mock.call_args_list:
                self.assertTrue(call.kwargs.get("enable_pronunciation_resolver"),
                                 f"generate_charon_english call missing enable_pronunciation_resolver=True: {call}")
            for call in wide_margin_mock.call_args_list:
                self.assertTrue(call.kwargs.get("enable_pronunciation_resolver"),
                                 f"generate_news_narration_wide_margin call missing "
                                 f"enable_pronunciation_resolver=True: {call}")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class FamilyLegacyCallersUnaffectedTests(unittest.TestCase):
    """Family A(legacy)経路がgenerate_charon_english/generate_english_
    component_minimal_instruction/generate_news_narration_wide_marginを
    呼ぶ際、本管理IDのopt-in引数を一切渡していない(既定Falseのまま)ことを
    シグネチャ検査で確認する(既存呼び出し元コード自体は本管理IDで無編集)。"""

    def test_generate_charon_english_default_is_false(self):
        import inspect
        sig = inspect.signature(voice01.generate_charon_english)
        self.assertIs(sig.parameters["enable_pronunciation_resolver"].default, False)

    def test_generate_english_component_minimal_instruction_default_is_false(self):
        import inspect
        sig = inspect.signature(repro01.generate_english_component_minimal_instruction)
        self.assertIs(sig.parameters["enable_pronunciation_resolver"].default, False)

    def test_generate_news_narration_wide_margin_default_is_false(self):
        import inspect
        sig = inspect.signature(news_tail_fix.generate_news_narration_wide_margin)
        self.assertIs(sig.parameters["enable_pronunciation_resolver"].default, False)


class KeyPhraseJapaneseMeaningLockRecordingFixTests(unittest.TestCase):
    """Stage 3d副次発見(small_bag A2 meaning_5)の是正確認: er003_v1_n3_01_
    tts_generate.generate_a2_japanese_with_fallback()に review_lock.
    guarded_generate("ja")を追加したことで、標準経路が失敗した後に自前の
    fallback(minimal instruction)が実際に成功した場合、review_lock_
    state.jsonへ最終結果(RESOLVED)が正しく反映されることを、実際の
    narration layout(theme/level/narration/<segment>.wav)+実際のLock
    store読み書きで確認する(TTS/ASR自体はmock、Lock機構自体は本物)。"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="kp_ja_meaning_lock_fix_")
        self.out_path = os.path.join(self.tmpdir, "theme1", "a2", "narration", "meaning_5.wav")
        os.makedirs(os.path.dirname(self.out_path), exist_ok=True)
        self.attempt_history_path = os.path.join(self.tmpdir, "attempt_history.jsonl")
        self._orig_attempt_history_path = review_lock.ATTEMPT_HISTORY_PATH
        review_lock.ATTEMPT_HISTORY_PATH = self.attempt_history_path

    def tearDown(self):
        review_lock.ATTEMPT_HISTORY_PATH = self._orig_attempt_history_path
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _lock_store_path(self):
        level_out_dir = os.path.dirname(os.path.dirname(self.out_path))
        return os.path.join(level_out_dir, "audit", "review_lock_state.json")

    def test_fallback_success_after_standard_exhausted_is_recorded_as_resolved(self):
        realistic_standard_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        fake_cls = mock.Mock()
        fake_cls.classification = "PHONETIC_MATCH"
        with mock.patch.object(n3_tts.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_standard_attempts_log}), \
             mock.patch.object(n3_tts, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "目を引く",
                                              "path": self.out_path}), \
             mock.patch.object(n3_tts.routing, "transcribe", return_value=("目を引く", None)), \
             mock.patch.object(n3_tts.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(True, False, fake_cls)):
            result = n3_tts.generate_a2_japanese_with_fallback(
                "目を引く", self.out_path, "目を")

        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["fallback_used"])

        store_path = self._lock_store_path()
        self.assertTrue(os.path.exists(store_path), "Lock storeが書き込まれていません")
        with open(store_path, encoding="utf-8") as f:
            store = __import__("json").load(f)
        segment = store.get("meaning_5")
        self.assertIsNotNone(segment, "meaning_5のLock entryが見つかりません")
        self.assertEqual(segment["state"], "RESOLVED",
                          f"fallback成功後もLock stateがRESOLVEDになっていません(修正前バグの再現): {segment}")

    def test_both_standard_and_fallback_fail_is_recorded_as_human_review_required(self):
        """regression確認: 標準・fallbackとも不合格の既存挙動(HUMAN_REVIEW_
        REQUIREDへ正しく落ちること)は本修正で変わらない。"""
        realistic_standard_attempts_log = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        fake_cls = mock.Mock()
        fake_cls.classification = "TRUE_CONTENT_MISMATCH"
        with mock.patch.object(n3_tts.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic_standard_attempts_log}), \
             mock.patch.object(n3_tts, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": "目を引く",
                                              "path": self.out_path}), \
             mock.patch.object(n3_tts.routing, "transcribe", return_value=("違う文", None)), \
             mock.patch.object(n3_tts.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                return_value=(False, False, fake_cls)):
            result = n3_tts.generate_a2_japanese_with_fallback(
                "目を引く", self.out_path, "目を")

        self.assertEqual(result["status"], "STOPPED")

        store_path = self._lock_store_path()
        with open(store_path, encoding="utf-8") as f:
            store = __import__("json").load(f)
        segment = store.get("meaning_5")
        self.assertIsNotNone(segment)
        self.assertEqual(segment["state"], "HUMAN_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
