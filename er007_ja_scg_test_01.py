# ============================================================
# er007_ja_scg_test_01.py
# OPEN-258-JA-SECONDARY-ASR-PRODUCTION-WIRING-01: SCG(Secondary Confirm Gate)
# の単体・統合test(課金0、Azure/OpenAI/TTSはすべてmock)。
#   (a) Primary TCM -> Secondary EXACT -> PASS
#   (b) NORMALIZED -> PASS
#   (c) PHONETIC_MATCH -> NG(再生成)
#   (d) 数字/否定差 -> SCG不実行
#   (e) 類似度0.4未満 -> 不実行
#   (f) Azure例外/空/None -> 従来動作
#   (g) attempt上限(標準2+fallback1=3)・Human Review Lock不変
#   (h) 英語経路に影響なし
# ============================================================
from __future__ import annotations

import ast
import os
import types
import unittest
from unittest import mock

import numpy as np

import er003_b1_p4_audio as p4
import er003_v1_n3_01_tts_generate as n3
import er003_v1_repro01_main_generate as repro01
import er003_v1_sing01_voice01_generate as voice01
import er007_ja_asr_validator_01 as javal
import er007_ja_secondary_asr_01 as ja_secondary
import er011_human_review_lock_01 as review_lock

CANON = "AIの電話に人間が出演。問題は「キャスト変更」のお知らせでした"
PRIMARY_NG = "AIの電話に人間が出現。問題は、キャスト変更のお知らせでした。"
AZURE_NORMALIZED = "AIの電話に人間が出演。問題はキャスト変更のお知らせでした。"
AZURE_STILL_NG = "AIの電話に人間が出現。問題はキャスト変更のお知らせでした。"
_DUMMY_TRIM_INFO = {"raw_duration_seconds": 1.0, "trimmed_duration_seconds": 1.0}


class _Base(unittest.TestCase):
    def setUp(self):
        # Reading Resolver(LLM)はOFF(課金0)。SCGは既定ON(モジュール既定を確認する別testあり)
        p = mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False)
        p.start()
        self.addCleanup(p.stop)
        self.azure = mock.patch.object(p4, "get_full_text_via_azure_stt_continuous")
        self.mock_azure = self.azure.start()
        self.addCleanup(self.azure.stop)

    def detail(self, canon, primary, **kw):
        return ja_secondary.evaluate_attempt_ja_with_cascade_detail(
            canon, primary, "dummy.wav", cascade_enabled=kw.pop("cascade_enabled", True), **kw)


class ScgJudgementTests(_Base):
    def test_default_flag_is_on(self):
        self.assertIs(ja_secondary.FEATURE_FLAG_JA_SCG_ENABLED, True)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("JA_SCG_ENABLED", None)
            self.assertTrue(ja_secondary._scg_enabled())

    def test_a_secondary_exact_match_passes(self):
        self.mock_azure.return_value = (CANON, None)
        d = self.detail(CANON, PRIMARY_NG)
        self.assertTrue(d["verified"])
        self.assertFalse(d["stop_retrying"])
        self.assertEqual(d["final_status"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(d["classification"].classification, "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertTrue(d["classification"].should_pass)
        self.assertEqual(d["scg_info"]["secondary_classification"], "EXACT_MATCH")
        self.assertEqual(self.mock_azure.call_count, 1)
        self.assertFalse(d["human_review_required"])
        self.assertIs(d["scg_applied"], True)
        self.assertEqual(d["scg_result"], "PASS")

    def test_b_secondary_normalized_match_passes(self):
        self.mock_azure.return_value = (AZURE_NORMALIZED, None)
        d = self.detail(CANON, PRIMARY_NG)
        self.assertTrue(d["verified"])
        self.assertEqual(d["scg_info"]["secondary_classification"], "NORMALIZED_MATCH")
        self.assertEqual(d["scg_info"]["secondary_transcript"], AZURE_NORMALIZED)
        self.assertEqual(self.mock_azure.call_count, 1)
        # Phrase Listなし版の既存関数を使う(Phrase List版は呼ばない)
        args, kwargs = self.mock_azure.call_args
        self.assertEqual(kwargs.get("language"), "ja-JP")

    def test_c_phonetic_match_is_not_auto_pass(self):
        # 同読み別表記(PHONETIC_MATCH): Primaryが「匂い」、原稿が「においを出す」型
        canon = "熟すと出るガスのにおいを出す"
        primary = "熟すと出るガスのを出す"
        self.mock_azure.return_value = ("熟すと出るガスの匂いを出す", None)
        d = self.detail(canon, primary)
        self.assertEqual(d["scg_info"]["secondary_classification"], "PHONETIC_MATCH")
        self.assertFalse(d["verified"])
        self.assertEqual(d["scg_result"], "NG")
        self.assertEqual(d["classification"].classification, "TRUE_CONTENT_MISMATCH")
        self.assertFalse(d["stop_retrying"])  # 従来どおり再生成へ

    def test_secondary_same_error_as_primary_is_ng(self):
        self.mock_azure.return_value = (AZURE_STILL_NG, None)
        d = self.detail(CANON, PRIMARY_NG)
        self.assertFalse(d["verified"])
        self.assertEqual(d["scg_result"], "NG")
        self.assertFalse(d["stop_retrying"])
        self.assertEqual(d["final_status"], "TRUE_CONTENT_MISMATCH")

    def test_d_number_mismatch_not_executed(self):
        self.mock_azure.return_value = ("150人の女性を対象とした調査", None)
        d = self.detail("150人の女性を対象とした調査", "140人の女性を対象とした調査")
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(d["verified"])
        self.assertEqual(d["scg_result"], "NOT_APPLIED")
        self.assertIn("number_mismatch", d["scg_info"]["exclusion_reason"])

    def test_d_negation_mismatch_not_executed(self):
        self.mock_azure.return_value = ("この薬は眠くならない仕組みです", None)
        d = self.detail("この薬は眠くならない仕組みです", "この薬は眠くなる仕組みです")
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(d["verified"])
        self.assertIn("negation_mismatch", d["scg_info"]["exclusion_reason"])

    def test_e_similarity_below_0_4_not_executed(self):
        self.mock_azure.return_value = ("湿度", None)
        d = self.detail("湿度", "死図塔")
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(d["verified"])
        self.assertIn("similarity_lt_0.4", d["scg_info"]["exclusion_reason"])

    def test_f_azure_exception_falls_back_to_legacy(self):
        self.mock_azure.side_effect = RuntimeError("boom")
        d = self.detail(CANON, PRIMARY_NG)
        self.assertFalse(d["verified"])
        self.assertFalse(d["stop_retrying"])
        self.assertEqual(d["scg_result"], "UNAVAILABLE")
        self.assertEqual(d["final_status"], "TRUE_CONTENT_MISMATCH")
        self.assertFalse(d["human_review_required"])
        self.assertIn("boom", d["scg_info"]["error"])

    def test_f_azure_none_and_empty_fall_back_to_legacy(self):
        for ret in [(None, "timeout"), ("", None), ("   ", None)]:
            self.mock_azure.return_value = ret
            d = self.detail(CANON, PRIMARY_NG)
            self.assertFalse(d["verified"], ret)
            self.assertEqual(d["scg_result"], "UNAVAILABLE", ret)
            self.assertFalse(d["stop_retrying"], ret)

    def test_flag_off_is_identical_to_legacy(self):
        self.mock_azure.return_value = (CANON, None)
        with mock.patch.object(ja_secondary, "FEATURE_FLAG_JA_SCG_ENABLED", False):
            d = self.detail(CANON, PRIMARY_NG)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(d["verified"])
        self.assertFalse(d["stop_retrying"])
        self.assertFalse(d["scg_applied"])
        self.assertEqual(d["final_status"], "TRUE_CONTENT_MISMATCH")

    def test_env_kill_switch(self):
        self.mock_azure.return_value = (CANON, None)
        with mock.patch.dict(os.environ, {"JA_SCG_ENABLED": "0"}):
            d = self.detail(CANON, PRIMARY_NG)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertFalse(d["verified"])

    def test_cascade_disabled_skips_scg(self):
        self.mock_azure.return_value = (CANON, None)
        d = self.detail(CANON, PRIMARY_NG, cascade_enabled=False)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertNotIn("scg_info", d)
        self.assertFalse(d["verified"])

    def test_primary_pass_never_calls_azure(self):
        d = self.detail(CANON, CANON)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertTrue(d["verified"])
        self.assertNotIn("scg_info", d)

    def test_uncertain_entity_path_unchanged_no_scg(self):
        """ASR_VALIDATION_UNCERTAIN(entity_like)は従来Cascadeのまま(SCG分岐に入らない)。"""
        import er006_asr_provider_routing_01 as routing
        canon = "解約を難しくする壁は、「スラッジ」と考えられます。"
        asr = "解約を難しくする壁は、「スラッシ」と考えられます。"
        with mock.patch.object(routing, "_transcribe_openai_mini", return_value=(canon, None)):
            d = self.detail(canon, asr)
        self.assertTrue(d["verified"])
        self.assertNotEqual(d["final_status"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertNotIn("scg_info", d)
        self.assertEqual(self.mock_azure.call_count, 0)

    def test_wrapper_returns_dropin_tuple_and_scg_info_on_cls(self):
        self.mock_azure.return_value = (AZURE_NORMALIZED, None)
        v, stop, cls = ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav")
        self.assertTrue(v)
        self.assertFalse(stop)
        self.assertEqual(cls.scg_info["scg_result"], "PASS")
        self.mock_azure.return_value = (AZURE_STILL_NG, None)
        v, stop, cls = ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav")
        self.assertFalse(v)
        self.assertFalse(stop)
        self.assertEqual(cls.classification, "TRUE_CONTENT_MISMATCH")
        self.assertEqual(cls.scg_info["scg_result"], "NG")


# ---- 統合(呼び出し元経路ごと): attempt上限・fallback・Human Review Lock不変 ----

def _run_voice01(primary_texts, azure_texts):
    """voice01.generate_charon_japanese(標準2+fallback1)。Primary/Azureの転写をattempt順に返す。
    TTS/ASR(Primary)/Azureはmock、ja_secondary.evaluate_attempt_ja_with_cascadeは実物。"""
    with mock.patch.object(voice01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
         mock.patch.object(voice01.p4c, "build_tts_prompt", return_value="dummy prompt"), \
         mock.patch.object(voice01.common, "_call_tts_with_retry", return_value=(b"pcm", 0, True, None)) as mock_tts, \
         mock.patch.object(voice01.common, "pcm_bytes_to_float_mono", return_value=np.zeros(100, dtype=np.float32)), \
         mock.patch.object(voice01.p3u, "trim_english_keyword_silence",
                            return_value=(np.zeros(100, dtype=np.float32), dict(_DUMMY_TRIM_INFO))), \
         mock.patch.object(voice01.safety, "detect_duration_anomaly", return_value={"is_anomaly": False}), \
         mock.patch.object(voice01.common, "write_wav_float", return_value=None), \
         mock.patch.object(voice01.common, "measure_metrics", return_value={"clipping_detected": False}), \
         mock.patch.object(voice01.routing, "transcribe", side_effect=[(t, None) for t in primary_texts]), \
         mock.patch.object(p4, "get_full_text_via_azure_stt_continuous",
                            side_effect=[(t, None) for t in azure_texts]) as mock_azure, \
         mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False), \
         mock.patch.object(review_lock, "save_tts_attempt_audio", return_value="saved.wav"):
        result = voice01.generate_charon_japanese(CANON, "dummy_out.wav", "出演")
    return mock_tts, mock_azure, result


class VoiceCharonJapaneseScgTests(unittest.TestCase):
    def test_scg_pass_on_first_attempt_consumes_one_tts(self):
        mock_tts, mock_azure, result = _run_voice01([PRIMARY_NG], [AZURE_NORMALIZED])
        self.assertEqual(mock_tts.call_count, 1)
        self.assertEqual(mock_azure.call_count, 1)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["asr_verified"])
        self.assertFalse(result["fallback_used"])
        self.assertEqual(result["attempts_log"][0]["audio_classification"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(result["attempts_log"][0]["scg_info"]["secondary_transcript"], AZURE_NORMALIZED)

    def test_scg_ng_every_attempt_keeps_total_three_and_stops(self):
        mock_tts, mock_azure, result = _run_voice01([PRIMARY_NG] * 3, [AZURE_STILL_NG] * 3)
        self.assertEqual(mock_tts.call_count, review_lock.PRODUCTION_MAX_TTS_ATTEMPTS)
        self.assertEqual(mock_azure.call_count, 3, "SCGは1 attemptにつきAzure 1回(TTS attemptを消費しない)")
        self.assertEqual(result["status"], "STOPPED")
        for a in result["standard_attempts_log"] + result["fallback_attempts_log"]:
            self.assertEqual(a["scg_info"]["scg_result"], "NG")

    def test_scg_azure_unavailable_every_attempt_is_legacy_stopped(self):
        mock_tts, mock_azure, result = _run_voice01([PRIMARY_NG] * 3, [""] * 3)
        self.assertEqual(mock_tts.call_count, 3)
        self.assertEqual(result["status"], "STOPPED")

    def test_scg_pass_on_fallback_attempt(self):
        mock_tts, mock_azure, result = _run_voice01(
            [PRIMARY_NG] * 3, [AZURE_STILL_NG, AZURE_STILL_NG, AZURE_NORMALIZED])
        self.assertEqual(mock_tts.call_count, 3)
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["fallback_attempts_log"][0]["audio_classification"],
                          "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(result["fallback_attempts_log"][0]["scg_info"]["scg_result"], "PASS")


class N3FallbackScgTests(unittest.TestCase):
    """n3.generate_a2_japanese_with_fallback の fallback(minimal instruction)attemptでもSCGが動く。"""

    def _run(self, azure_ret):
        realistic = [{"attempt": 1, "status": "OK"}, {"attempt": 2, "status": "OK"}]
        with mock.patch.object(n3.c, "generate_narration_snippet_verified_strict",
                                return_value={"status": "STOPPED", "attempts_log": realistic}), \
             mock.patch.object(n3, "_generate_a2_japanese_minimal_instruction",
                                return_value={"status": "OK", "text": CANON, "path": "dummy.wav"}) as mock_min, \
             mock.patch.object(n3.routing, "transcribe", return_value=(PRIMARY_NG, None)), \
             mock.patch.object(p4, "get_full_text_via_azure_stt_continuous", return_value=azure_ret) as mock_azure, \
             mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False), \
             mock.patch.object(review_lock, "save_tts_attempt_audio", return_value="saved.wav"):
            result = n3.generate_a2_japanese_with_fallback(CANON, "dummy.wav", "出演")
        return mock_min, mock_azure, result

    def test_fallback_scg_pass(self):
        mock_min, mock_azure, result = self._run((AZURE_NORMALIZED, None))
        self.assertEqual(mock_min.call_count, 1)
        self.assertEqual(mock_azure.call_count, 1)
        self.assertTrue(result["asr_verified"])
        self.assertTrue(result["fallback_used"])
        self.assertEqual(result["audio_classification"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(result["scg_info"]["scg_result"], "PASS")

    def test_fallback_scg_ng_is_stopped_with_total_three(self):
        mock_min, mock_azure, result = self._run((AZURE_STILL_NG, None))
        self.assertEqual(mock_min.call_count, 1)
        self.assertEqual(result["status"], "STOPPED")
        self.assertEqual(result["fallback_attempts_log"][0]["scg_info"]["scg_result"], "NG")


class Repro01ScgTests(unittest.TestCase):
    """repro01.generate_narration_snippet_verified_strict(language=ja): 初回・retry・STOP。"""

    def _run(self, language, primary_texts, azure_texts, max_attempts=3):
        gen = mock.Mock(return_value={"status": "OK", "duration_seconds": 2.0, "path": "dummy.wav"})
        with mock.patch.object(repro01.p9a, "generate_narration_snippet", gen), \
             mock.patch.object(repro01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
             mock.patch.object(repro01.routing, "transcribe", side_effect=[(t, None) for t in primary_texts]), \
             mock.patch.object(p4, "get_full_text_via_azure_stt_continuous",
                                side_effect=[(t, None) for t in azure_texts]) as mock_azure, \
             mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False), \
             mock.patch.object(review_lock, "save_tts_attempt_audio", return_value="saved.wav"):
            result = repro01.generate_narration_snippet_verified_strict(
                CANON, language, "dummy_out.wav", "出演", max_attempts=max_attempts, max_extra_chars=40)
        return gen, mock_azure, result

    def test_first_attempt_scg_pass(self):
        gen, mock_azure, result = self._run("ja", [PRIMARY_NG], [AZURE_NORMALIZED])
        self.assertEqual(gen.call_count, 1)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["audio_classification"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(result["scg_info"]["scg_result"], "PASS")
        self.assertEqual(result["attempts_log"][0]["scg_info"]["secondary_transcript"], AZURE_NORMALIZED)

    def test_retry_then_scg_pass_on_second_attempt(self):
        gen, mock_azure, result = self._run("ja", [PRIMARY_NG] * 2, [AZURE_STILL_NG, AZURE_NORMALIZED])
        self.assertEqual(gen.call_count, 2)
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["attempts_log"][0]["scg_info"]["scg_result"], "NG")
        self.assertFalse(result["attempts_log"][0]["verified"])
        self.assertEqual(result["attempts_log"][1]["scg_info"]["scg_result"], "PASS")

    def test_all_ng_hits_attempt_cap_and_stops(self):
        gen, mock_azure, result = self._run("ja", [PRIMARY_NG] * 3, [AZURE_STILL_NG] * 3)
        self.assertEqual(gen.call_count, 3)
        self.assertEqual(mock_azure.call_count, 3)
        self.assertEqual(result["status"], "STOPPED")

    def test_default_max_attempts_is_unchanged_three(self):
        import inspect
        sig = inspect.signature(repro01.generate_narration_snippet_verified_strict)
        self.assertEqual(sig.parameters["max_attempts"].default, 3)
        self.assertEqual(review_lock.PRODUCTION_MAX_TTS_ATTEMPTS, 3)
        self.assertEqual(review_lock.PRODUCTION_STANDARD_TTS_ATTEMPTS, 2)
        self.assertEqual(review_lock.PRODUCTION_MINIMAL_FALLBACK_TTS_ATTEMPTS, 1)

    def test_h_english_path_never_touches_scg(self):
        en_text = "The quick brown fox jumps over the lazy dog."
        with mock.patch.object(repro01.p9a, "generate_narration_snippet",
                                return_value={"status": "OK", "duration_seconds": 2.0, "path": "dummy.wav"}), \
             mock.patch.object(repro01.batch_wiring, "make_batch_tts_call_fn", return_value=lambda *a, **k: None), \
             mock.patch.object(repro01.routing, "transcribe", return_value=(en_text, None)), \
             mock.patch.object(repro01.ja_secondary, "evaluate_attempt_ja_with_cascade") as mock_ja, \
             mock.patch.object(p4, "get_full_text_via_azure_stt_continuous") as mock_azure, \
             mock.patch.object(review_lock, "save_tts_attempt_audio", return_value="saved.wav"):
            result = repro01.generate_narration_snippet_verified_strict(en_text, "en", "dummy_out.wav", "quick")
        self.assertEqual(mock_ja.call_count, 0)
        self.assertEqual(mock_azure.call_count, 0)
        self.assertNotIn("SECONDARY_CONFIRMED_PRIMARY_FALSE_NG", str(result.get("audio_classification")))

    def test_h_english_asr_modules_do_not_reference_scg(self):
        here = os.path.dirname(os.path.abspath(__file__))
        for fn in ("er006_secondary_asr_01.py", "er006_asr_provider_routing_01.py", "er021_en_asr_semantic_equivalence_01.py"):
            path = os.path.join(here, fn)
            if not os.path.exists(path):
                continue
            src = open(path, encoding="utf-8").read()
            self.assertNotIn("SECONDARY_CONFIRMED_PRIMARY_FALSE_NG", src, fn)
            self.assertNotIn("JA_SCG_ENABLED", src, fn)


class HumanReviewLockUnchangedTests(_Base):
    def test_scg_paths_never_write_human_review_queue(self):
        with mock.patch.object(ja_secondary, "_log_human_review") as mock_log:
            self.mock_azure.return_value = (AZURE_NORMALIZED, None)
            ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav")
            self.mock_azure.return_value = (AZURE_STILL_NG, None)
            ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav")
            self.mock_azure.side_effect = RuntimeError("x")
            ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav")
        self.assertEqual(mock_log.call_count, 0, "SCGは新規Human Review投入を行わない")


class ScgSafetyConstantsTests(unittest.TestCase):
    def test_only_exact_and_normalized_pass(self):
        self.assertEqual(ja_secondary.SCG_PASS_CLASSIFICATIONS, ("EXACT_MATCH", "NORMALIZED_MATCH"))
        self.assertEqual(ja_secondary.SCG_MIN_SIMILARITY, 0.4)

    def test_no_phrase_list_call_in_scg_code(self):
        src = open(ja_secondary.__file__, encoding="utf-8").read()
        tree = ast.parse(src)
        fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_run_scg_secondary_confirm"][0]
        seg = ast.get_source_segment(src, fn)
        self.assertNotIn("phrase_list", seg.replace('"phrase_list": False', "").replace("phrase_list=False", ""))
        self.assertIn("get_full_text_via_azure_stt_continuous", seg)
        self.assertNotIn("with_phrase_list", seg)


if __name__ == "__main__":
    unittest.main()
