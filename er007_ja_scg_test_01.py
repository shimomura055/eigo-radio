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
        self.azure = mock.patch.object(ja_secondary, "_azure_stt_strict")
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
         mock.patch.object(ja_secondary, "_azure_stt_strict",
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
             mock.patch.object(ja_secondary, "_azure_stt_strict", return_value=azure_ret) as mock_azure, \
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
             mock.patch.object(ja_secondary, "_azure_stt_strict",
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
             mock.patch.object(ja_secondary, "_azure_stt_strict") as mock_azure, \
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
        self.assertIn("_azure_stt_strict", seg)
        self.assertNotIn("with_phrase_list", seg)


# ============================================================
# Opus独立レビュー是正(必須1/2、推奨5/6/7)
# ============================================================
class OpusReviewFixTests(_Base):
    def test_c1_entity_like_diff_in_mixed_diffs_not_executed(self):
        # 「ガス」->「カス」(カタカナ同士=entity_like)を含む混在差分(漢字差も同時にある)
        canon, primary = "熟すと出るガス", "じくすと出るカス。"
        self.mock_azure.return_value = (canon, None)
        d = self.detail(canon, primary)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertEqual(d["scg_result"], "NOT_APPLIED")
        self.assertIn("entity_like_diff", d["scg_info"]["exclusion_reason"])
        self.assertFalse(d["verified"])
        self.assertFalse(d["stop_retrying"])

    def test_c1_dictionary_reading_mismatch_not_executed(self):
        # 原稿「Meta」、Primary「メタン」、expected_readings(meta=メタ)。Azureが「Meta」と返しても不実行
        canon, primary = "Metaが新しい発表をしました", "メタンが新しい発表をしました"
        self.mock_azure.return_value = (canon, None)
        d = self.detail(canon, primary, expected_readings={"meta": "メタ"})
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertEqual(d["scg_result"], "NOT_APPLIED")
        reason = d["scg_info"]["exclusion_reason"]
        self.assertTrue(reason.startswith(("reading_dictionary_mismatch", "entity_like_diff", "latin_in_canonical_diff")), reason)

    def test_c1_latin_in_canonical_diff_excluded_unit(self):
        # 実入力ではentity_like経路(UNCERTAIN)に入ることが多いため、除外関数を直接検証する
        def fake_cls(diffs):
            prot = types.SimpleNamespace(number_mismatches=[], negation_mismatches=[], content_diffs=diffs)
            return types.SimpleNamespace(classification="TRUE_CONTENT_MISMATCH", protected=prot, similarity_ratio=0.9)
        r = ja_secondary._scg_exclusion_reason(fake_cls([
            {"canonical": "出演", "asr": "出現", "entity_like": False},
            {"canonical": "Meta", "asr": "メタン", "entity_like": False}]))
        self.assertTrue(r.startswith("latin_in_canonical_diff"), r)
        r = ja_secondary._scg_exclusion_reason(fake_cls([{"canonical": "出演", "asr": "出現", "entity_like": False}]))
        self.assertIsNone(r)
        r = ja_secondary._scg_exclusion_reason(fake_cls([
            {"canonical": "x", "asr": "y", "entity_like": False, "reading_dictionary_mismatch": True,
             "reading_dictionary_token": "meta"}]))
        self.assertTrue(r.startswith("reading_dictionary_mismatch"), r)

    def test_c1_pure_kanji_diff_still_executes(self):
        self.mock_azure.return_value = (CANON, None)
        d = self.detail(CANON, PRIMARY_NG)
        self.assertEqual(self.mock_azure.call_count, 1)
        self.assertEqual(d["scg_result"], "PASS")

    def test_rec6_length_not_ok_skips_scg(self):
        self.mock_azure.return_value = (CANON, None)
        d = self.detail(CANON, PRIMARY_NG, length_ok=False)
        self.assertEqual(self.mock_azure.call_count, 0)
        self.assertEqual(d["scg_result"], "NOT_APPLIED")
        self.assertIn("length_not_ok", d["scg_info"]["exclusion_reason"])
        self.assertFalse(d["verified"])
        # wrapper(drop-in)にもlength_okが通る
        v, stop, cls = ja_secondary.evaluate_attempt_ja_with_cascade(CANON, PRIMARY_NG, "dummy.wav", length_ok=False)
        self.assertFalse(v)
        self.assertEqual(self.mock_azure.call_count, 0)

    def test_rec6_callers_pass_length_ok(self):
        for mod in (n3, repro01, voice01):
            src = open(mod.__file__, encoding="utf-8").read()
            self.assertEqual(src.count("cls = ja_secondary.evaluate_attempt_ja_with_cascade("),
                             src.count("expected_readings=expected_readings, length_ok=length_ok)"), mod.__name__)

    def test_rec5_secondary_does_not_call_reading_resolver(self):
        import er011_a2_reading_resolver_01 as rr
        calls = {"n": 0}

        def fake_resolve(c, a):
            calls["n"] += 1
            return {"resolved_match": False, "resolver_calls": 0}

        self.mock_azure.return_value = (AZURE_STILL_NG, None)
        with mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", True), \
             mock.patch.object(rr, "resolve_reading_diff", side_effect=fake_resolve):
            d = self.detail(CANON, PRIMARY_NG)
            n_with_scg = calls["n"]
            calls["n"] = 0
            javal.classify_ja_asr_match(CANON, PRIMARY_NG)
            n_primary_only = calls["n"]
        self.assertEqual(d["scg_result"], "NG")
        self.assertEqual(n_with_scg, n_primary_only, "SCG(Secondary)判定はResolverを追加で呼ばない")

    def test_rec5_allow_reading_resolver_default_true_is_backward_compatible(self):
        import inspect
        sig = inspect.signature(javal.classify_ja_asr_match)
        self.assertIs(sig.parameters["allow_reading_resolver"].default, True)


class _FakeEvent:
    def __init__(self):
        self.cbs = []

    def connect(self, cb):
        self.cbs.append(cb)

    def fire(self, evt):
        for cb in self.cbs:
            cb(evt)


def _make_fake_speechsdk(script):
    """script(recognizer, sdk)がstart時に呼ばれ、イベントをfireする。"""
    sdk = types.SimpleNamespace()
    sdk.ResultReason = types.SimpleNamespace(RecognizedSpeech="RS")
    sdk.CancellationReason = types.SimpleNamespace(Error="ERR", EndOfStream="EOS")
    sdk.SpeechConfig = lambda **k: types.SimpleNamespace()
    sdk.audio = types.SimpleNamespace(AudioConfig=lambda **k: None)

    class Rec:
        def __init__(self, **k):
            self.recognized, self.session_stopped, self.canceled = _FakeEvent(), _FakeEvent(), _FakeEvent()

        def start_continuous_recognition(self):
            script(self, sdk)

        def stop_continuous_recognition(self):
            pass

    sdk.SpeechRecognizer = Rec
    return sdk


class AzureStrictCancelTests(unittest.TestCase):
    def _run(self, script):
        import sys
        import tempfile
        sdk = _make_fake_speechsdk(script)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav = f.name
        try:
            fake_pkg = types.ModuleType("azure.cognitiveservices.speech")
            fake_pkg.__dict__.update(sdk.__dict__)
            import azure.cognitiveservices as _acs
            with mock.patch.dict(sys.modules, {"azure.cognitiveservices.speech": fake_pkg}), \
                 mock.patch.object(_acs, "speech", fake_pkg), \
                 mock.patch.dict(os.environ, {"SPEECH_KEY": "k", "SPEECH_REGION": "r"}):
                return ja_secondary._azure_stt_strict(wav, timeout_seconds=3)
        finally:
            os.unlink(wav)

    @staticmethod
    def _rec_evt(text):
        return types.SimpleNamespace(result=types.SimpleNamespace(reason="RS", text=text))

    def test_error_cancel_after_partial_transcript_is_unavailable(self):
        def script(rec, sdk):
            rec.recognized.fire(self._rec_evt("AIの電話に人間が"))
            rec.canceled.fire(types.SimpleNamespace(cancellation_details=types.SimpleNamespace(
                reason="ERR", error_details="network down")))
        text, err = self._run(script)
        self.assertIsNone(text)
        self.assertIn("network down", err)

    def test_end_of_stream_cancel_is_normal(self):
        def script(rec, sdk):
            rec.recognized.fire(self._rec_evt("全文"))
            rec.canceled.fire(types.SimpleNamespace(cancellation_details=types.SimpleNamespace(
                reason="EOS", error_details=None)))
        text, err = self._run(script)
        self.assertEqual(text, "全文")
        self.assertIsNone(err)

    def test_cancel_details_unreadable_is_conservative_error(self):
        def script(rec, sdk):
            rec.recognized.fire(self._rec_evt("途中"))
            rec.canceled.fire(types.SimpleNamespace())  # cancellation_detailsなし
        text, err = self._run(script)
        self.assertIsNone(text)
        self.assertIsNotNone(err)

    def test_session_stopped_normal_returns_text(self):
        def script(rec, sdk):
            rec.recognized.fire(self._rec_evt("あ"))
            rec.recognized.fire(self._rec_evt("い"))
            rec.session_stopped.fire(types.SimpleNamespace())
        self.assertEqual(self._run(script), ("あい", None))

    def test_scg_treats_strict_error_as_unavailable_via_production_path(self):
        with mock.patch.object(ja_secondary, "_azure_stt_strict", return_value=(None, "CancellationReason.Error: x")), \
             mock.patch.object(javal, "FEATURE_FLAG_A2_READING_RESOLVER_ENABLED", False):
            d = ja_secondary.evaluate_attempt_ja_with_cascade_detail(CANON, PRIMARY_NG, "dummy.wav", cascade_enabled=True)
        self.assertEqual(d["scg_result"], "UNAVAILABLE")
        self.assertFalse(d["verified"])
        self.assertFalse(d["stop_retrying"])

    def test_shared_p4_function_signature_unchanged(self):
        # 他testのmock漏れの影響を受けないよう、実体ではなくソースのASTで署名を確認する
        src = open(p4.__file__, encoding="utf-8").read()
        fn = [n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "get_full_text_via_azure_stt_continuous"][0]
        self.assertEqual([a.arg for a in fn.args.args], ["wav_path", "language", "timeout_seconds"])


class MasterStoreScgFieldsTests(unittest.TestCase):
    def test_manifest_records_audio_classification_and_scg_result(self):
        import json
        import tempfile
        import er006_master_audio_store_01 as store
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(store, "STORE_DIR", tmp), mock.patch.object(store, "AUDIO_DIR", f"{tmp}/audio"), \
                 mock.patch.object(store, "MANIFEST_PATH", f"{tmp}/manifest.json"), \
                 mock.patch.object(store, "TELEMETRY_PATH", f"{tmp}/t.jsonl"):
                key = store.MasterAudioKey(language="ja", speaker_voice="Charon", tts_model_id="m", canonical_text=CANON)

                def gen(out):
                    with open(out, "wb") as f:
                        f.write(b"x")
                    return {"status": "OK", "audio_classification": "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG",
                            "scg_info": {"scg_result": "PASS"}}
                store.get_or_generate(key, f"{tmp}/o.wav", gen)
                ent = json.load(open(f"{tmp}/manifest.json", encoding="utf-8"))[key.master_audio_id()]
        self.assertEqual(ent["audio_classification"], "SECONDARY_CONFIRMED_PRIMARY_FALSE_NG")
        self.assertEqual(ent["scg_result"], "PASS")
        for k in ("audio_path", "key", "created_at", "qa_evidence"):
            self.assertIn(k, ent)


if __name__ == "__main__":
    unittest.main()
