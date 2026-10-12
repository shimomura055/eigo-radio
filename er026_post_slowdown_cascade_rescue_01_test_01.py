"""FAMILY-Z-MELOS-PROPER-NOUN-ASR-ROOT-CAUSE-01 委任_01 是正A のtest。
減速後再検証(apply_a2_slowdown_postprocess)へ、減速前と同じ共有Cascade
(Tier3 corroboration等、既承認)を配線したことの確認。有料API・ネットワーク
は使わない(Azure/OpenAI ASR/Ledger research/telemetry書込は全てmock)。"""
import hashlib
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_tts_generate as tg
import er006_secondary_asr_01 as sec


class PostSlowdownCascadeRescueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="er026_pscr_test_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.name = "full_story_part1_c1"
        self.out = f"{self.tmp}/{self.name}.wav"
        with open(self.out, "wb") as f:
            f.write(b"PRE")

    def _fake_stretch(self, src, dst):
        with open(dst, "wb") as f:
            f.write(b"POST_STRETCHED")
        return {"src_duration_seconds": 2.0, "dst_duration_seconds": 2.12}

    def _run(self, canonical, primary_asr, azure_text, *, azure_err=None):
        """実classify_asr_match+実共有Cascadeを使い、ASR/Azure/Ledger research/telemetryだけをmockする。"""
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        azure_calls = []

        def fake_azure(wav, language="en-US", phrases=None, timeout_seconds=90.0):
            azure_calls.append(phrases)
            return azure_text, azure_err

        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch), \
             mock.patch.object(tg.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec.routing, "transcribe", return_value=(primary_asr, None)), \
             mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", side_effect=fake_azure), \
             mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None), \
             mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"):
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, canonical, result)
        return out, azure_calls

    # --- 救済される正例(Melosの実事例と同型) ---
    def test_entity_only_uncertain_rescued_when_secondary_spells_canonical(self):
        out, calls = self._run("Melos called across the hall,", "Mellos called across the hall.",
                               "Melos called across the hall.")
        self.assertEqual(out["status"], "OK")
        self.assertTrue(out["post_slowdown_cascade_accepted"])
        self.assertEqual(out["post_slowdown_classification"], "ASR_VALIDATION_UNCERTAIN")
        self.assertTrue(out["post_slowdown_cascade"]["verified"])
        self.assertEqual(out["post_slowdown_cascade"]["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")
        self.assertTrue(calls)  # Azureが呼ばれた
        # sha256はNone許容(既存契約)のまま、asr_verified/asr_textは更新される
        self.assertTrue(out["asr_verified"])

    # --- 反例: 誤PASSしてはならない ---
    def test_no_rescue_when_secondary_also_misspells(self):
        # 実事例 b1b part1_c5: Azureも"Mellow"と聞く -> 救済しない(従来どおりSTOPPED)
        out, _ = self._run("Melos said.", "Mello said.", "Mellow said.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertFalse(out.get("post_slowdown_cascade_accepted", False))
        self.assertFalse(out["asr_verified"])

    def test_no_rescue_when_secondary_fails(self):
        out, _ = self._run("Melos called across the hall,", "Mellos called across the hall.", None,
                           azure_err="boom")
        self.assertEqual(out["status"], "STOPPED")

    def test_no_rescue_for_artificially_replaced_different_name(self):
        # 人工置換: 別の実在固有名詞に置換された音声(Primary/Secondaryとも"Marcus")
        out, _ = self._run("Melos called across the hall,", "Marcus called across the hall.",
                           "Marcus called across the hall.")
        self.assertEqual(out["status"], "STOPPED")

    def test_no_rescue_for_content_word_error(self):
        # 非固有名詞の内容語誤り(TRUE_CONTENT_MISMATCH)はCascade対象外 -> Azureを呼ばない
        out, calls = self._run("He drank water slowly.", "He dropped water slowly.", "He drank water slowly.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(calls, [])
        self.assertNotIn("post_slowdown_cascade", out)

    def test_no_rescue_for_number_error(self):
        out, calls = self._run("Melos waited three days.", "Melos waited five days.", "Melos waited three days.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(calls, [])

    def test_exception_in_cascade_is_fail_closed(self):
        result = {"status": "OK", "sha256": None, "duration_seconds": 2.0}
        with mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=self._fake_stretch), \
             mock.patch.object(tg.routing, "transcribe", return_value=("Mello said.", None)), \
             mock.patch.object(sec, "evaluate_attempt_with_cascade_detail", side_effect=RuntimeError("x")):
            out = tg.apply_a2_slowdown_postprocess(self.name, self.tmp, "Melos said.", result)
        self.assertEqual(out["status"], "STOPPED")
        self.assertIn("error", out["post_slowdown_cascade"])

    # --- 既存挙動の維持 ---
    def test_primary_pass_does_not_invoke_cascade(self):
        out, calls = self._run("Melos called across the hall,", "Melos called across the hall.", None)
        self.assertEqual(out["status"], "OK")
        self.assertEqual(calls, [])
        self.assertNotIn("post_slowdown_cascade", out)

    def test_cascade_disabled_flag_keeps_old_behavior(self):
        with mock.patch.object(sec, "FEATURE_FLAG_SECONDARY_ASR_ENABLED", False):
            out, calls = self._run("Melos called across the hall,", "Mellos called across the hall.",
                                   "Melos called across the hall.")
        self.assertEqual(out["status"], "STOPPED")
        self.assertEqual(calls, [])


class OuterLoopIntegrationTests(unittest.TestCase):
    """generate_a2_segment_with_slowdown全体: 救済されれば1回のTTS生成で完了し、取り直しが発生しない。"""

    def _run(self, name, canonical, primary, azure, dur):
        tmp = tempfile.mkdtemp(prefix="er026_pscr_outer_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        out = f"{tmp}/{name}.wav"
        with open(out, "wb") as f:
            f.write(b"PRE")
        calls = {"tts": 0}

        def fake_inner(*a, **k):
            calls["tts"] += 1
            return {"status": "OK", "sha256": None, "duration_seconds": dur, "standard_attempts_log": [{}]}

        def fake_stretch(src, dst):
            with open(dst, "wb") as f:
                f.write(b"POST")
            return {"src_duration_seconds": dur, "dst_duration_seconds": dur * 1.06}

        with mock.patch.object(tg.c, "generate_english_segment_with_fallback", side_effect=fake_inner),              mock.patch.object(tg.a2_slowdown, "apply_a2_slowdown", side_effect=fake_stretch),              mock.patch.object(tg.routing, "transcribe", return_value=(primary, None)),              mock.patch.object(sec.routing, "transcribe", return_value=(primary, None)),              mock.patch.object(sec, "get_full_text_via_azure_stt_with_phrase_list", return_value=(azure, None)),              mock.patch.object(sec, "_resolve_unresolved_entity_for_review", return_value=None),              mock.patch.object(sec.semantic_equivalence, "append_telemetry_log"),              mock.patch.object(tg.review_lock, "append_attempt_history_event") as hist:
            r = tg.generate_a2_segment_with_slowdown(canonical, out, canonical.split()[0])
        return r, calls, hist

    def test_rescue_prevents_regeneration_and_logs_cascade(self):
        r, calls, hist = self._run("full_story_part1_c1", "Melos called across the hall,",
                                   "Mellos called across the hall.", "Melos called across the hall.", 2.0)
        self.assertEqual(r["status"], "OK")
        self.assertEqual(calls["tts"], 1)
        self.assertEqual(r["tts_generations_used"], 1)
        ev = hist.call_args[0][2]
        self.assertEqual(ev["post_slowdown_cascade"]["final_status"], "SECONDARY_ASR_CORROBORATED_MATCH")

    def test_no_rescue_consumes_budget_as_before(self):
        r, calls, _ = self._run("full_story_part1_c5", "Melos said.", "Mello said.", "Mellow said.", 1.5)
        self.assertEqual(r["status"], "STOPPED")
        self.assertEqual(calls["tts"], 3)            # 既存の通算3回上限(OPEN-270是正)は不変
        self.assertTrue(r["tts_generation_cap_reached"])


if __name__ == "__main__":
    unittest.main()
