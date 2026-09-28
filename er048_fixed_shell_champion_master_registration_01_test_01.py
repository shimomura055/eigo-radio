# ============================================================
# er048_fixed_shell_champion_master_registration_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W2、2026-09-29)
# ============================================================
# 実行方法:
#   .venv\Scripts\python.exe -m unittest er048_fixed_shell_champion_master_registration_01_test_01 -v
#
# API呼び出し: 0(実TTS/ASR呼び出しは全てmock、または「呼ばれたらFAIL」の
# センチネルで検証する)。¥0。
from __future__ import annotations

import json
import os
import shutil
import unittest

import er003_v1_sing01_voice01_generate as voice01
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er048_fixed_shell_champion_master_registration_01 as reg


class SourceJsonVerbatimMatchTests(unittest.TestCase):
    """CHAMPION_REGISTRATIONSの逐語転記が、由来Trial JSON(er043/er047)
    原本と一致することを検証する(手作業転記ミスの検出)。"""

    def test_er043_style_prefix_used_matches_source_json(self):
        with open(f"{reg.ER043_DIR}/champion_trial_results.json", encoding="utf-8") as f:
            champion = json.load(f)
        for entry in reg.CHAMPION_REGISTRATIONS:
            if entry["trial_management_id"] != reg.ER043_TRIAL_MANAGEMENT_ID:
                continue
            src = champion["candidates"][entry["candidate"]][entry["name"]]
            with self.subTest(name=entry["name"]):
                self.assertEqual(src["style_prefix_used"], entry["style_prefix_used"])
                self.assertEqual(src["canonical_text"], entry["canonical_text"])
                self.assertTrue(src["asr_verified"])

    def test_er047_style_prefix_used_matches_source_json(self):
        with open(f"{reg.ER047_DIR}/retrial_results.json", encoding="utf-8") as f:
            retrial = json.load(f)
        for entry in reg.CHAMPION_REGISTRATIONS:
            if entry["trial_management_id"] != reg.ER047_TRIAL_MANAGEMENT_ID:
                continue
            src = retrial["phrases"][entry["name"]][entry["candidate"]][str(entry["take"])]
            with self.subTest(name=entry["name"]):
                self.assertEqual(src["style_prefix_used"], entry["style_prefix_used"])
                self.assertEqual(src["canonical_text"], entry["canonical_text"])
                self.assertTrue(src["asr_verified"])
                self.assertEqual(src["candidate_style_system"], entry["candidate"])


class RegistrationsMatchSharedNarrationTests(unittest.TestCase):
    def test_no_stop_problems(self):
        problems = reg.assert_registrations_match_source_json()
        self.assertEqual(problems, [], f"STOP該当あり: {problems}")

    def test_welcome_is_not_in_registration_list(self):
        names = {e["name"] for e in reg.CHAMPION_REGISTRATIONS}
        self.assertNotIn("welcome", names)
        self.assertEqual(len(reg.CHAMPION_REGISTRATIONS), 9)

    def test_model_and_voice_unchanged_for_all_entries(self):
        for entry in reg.CHAMPION_REGISTRATIONS:
            key = reg.build_key(entry)
            with self.subTest(name=entry["name"]):
                self.assertEqual(key.tts_model_id, shared_narration.TTS_MODEL_FLASH_LITE)
                self.assertEqual(key.speaker_voice, "Charon")

    def test_old_version_master_not_hit_by_new_version_lookup(self):
        for entry in reg.CHAMPION_REGISTRATIONS:
            if entry["language"] != "en":
                continue
            new_key = reg.build_key(entry)
            old_key = shared_narration._make_english_key(
                entry["name"], entry["canonical_text"], "structured_separation")
            with self.subTest(name=entry["name"]):
                self.assertNotEqual(new_key.master_audio_id(), old_key.master_audio_id())
                self.assertEqual(new_key.style_instruction_version, shared_narration.SHELL_CHAMPION_STYLE_INSTRUCTION_VERSION)


class ApplyRegistrationTempStoreTests(unittest.TestCase):
    """一時Store(実Production manifestとは別ディレクトリ)へ実際に登録を
    行い、additive-onlyであること・reuse時TTS呼び出しが0回であることを
    検証する。"""

    def setUp(self):
        self.tmp_dir = "er048_output/_test_champion_registration_tmp"
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        self.orig_store_dir, self.orig_audio_dir = store.STORE_DIR, store.AUDIO_DIR
        self.orig_manifest, self.orig_telemetry = store.MANIFEST_PATH, store.TELEMETRY_PATH
        store.STORE_DIR = f"{self.tmp_dir}/store"
        store.AUDIO_DIR = f"{self.tmp_dir}/store/audio"
        store.MANIFEST_PATH = f"{self.tmp_dir}/store/manifest.json"
        store.TELEMETRY_PATH = f"{self.tmp_dir}/store/reuse_telemetry.jsonl"
        self.orig_out_dir = reg.OUT_DIR
        reg.OUT_DIR = f"{self.tmp_dir}/report"

    def tearDown(self):
        store.STORE_DIR, store.AUDIO_DIR = self.orig_store_dir, self.orig_audio_dir
        store.MANIFEST_PATH, store.TELEMETRY_PATH = self.orig_manifest, self.orig_telemetry
        reg.OUT_DIR = self.orig_out_dir
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_dry_run_does_not_write_manifest(self):
        report = reg.run("dry_run")
        self.assertFalse(os.path.exists(store.MANIFEST_PATH))
        self.assertEqual(report["manifest_before"]["entry_count"], 0)
        self.assertEqual(report["manifest_after"]["entry_count"], 0)
        self.assertEqual(len(report["entries"]), 9)
        for item in report["entries"]:
            self.assertFalse(item["already_registered"])

    def test_apply_registers_9_entries_additive_only_and_is_idempotent(self):
        report1 = reg.run("apply")
        self.assertEqual(report1["manifest_before"]["entry_count"], 0)
        self.assertEqual(report1["manifest_after"]["entry_count"], 9)
        master_ids = {item["master_audio_id"] for item in report1["entries"]}
        self.assertEqual(len(master_ids), 9, "9件それぞれ別のmaster_audio_idであるはず")
        for item in report1["entries"]:
            self.assertEqual(item["apply_result"]["status"], "REGISTERED")

        # 2回目実行(idempotent): 既存entryは書き換えずSKIPPED、manifestは
        # 完全不変(sha256一致)。
        sha_after_first = report1["manifest_after"]["sha256"]
        report2 = reg.run("apply")
        self.assertEqual(report2["manifest_before"]["entry_count"], 9)
        self.assertEqual(report2["manifest_after"]["entry_count"], 9)
        self.assertEqual(report2["manifest_after"]["sha256"], sha_after_first,
                          "2回目実行でmanifestが変化してはならない(additive-only・上書き禁止)")
        for item in report2["entries"]:
            self.assertEqual(item["apply_result"]["status"], "SKIPPED_ALREADY_EXISTS")

    def test_manifest_qa_evidence_records_asr_verified_and_source(self):
        reg.run("apply")
        with open(store.MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(len(manifest), 9)
        for master_id, entry in manifest.items():
            self.assertTrue(entry["qa_evidence"]["asr_verified"])
            self.assertIn(entry["qa_evidence"]["source_trial_management_id"],
                          (reg.ER043_TRIAL_MANAGEMENT_ID, reg.ER047_TRIAL_MANAGEMENT_ID))
            self.assertIn(entry["qa_evidence"]["source_commit"], (reg.ER043_SOURCE_COMMIT, reg.ER047_SOURCE_COMMIT))
            self.assertTrue(os.path.exists(entry["audio_path"]))

    def test_reuse_after_registration_makes_zero_tts_calls(self):
        """登録後、shared_narration.ensure_fixed_english_segment/
        ensure_fixed_japanese_segmentが実TTS関数を一切呼ばずreuseする
        ことを確認する(呼ばれたらAssertionErrorになるセンチネルを使う、
        mockのside_effectでraiseする形)。"""
        reg.run("apply")

        def _must_not_be_called(*_a, **_kw):
            raise AssertionError("TTSが呼ばれた(reuseされていない)")

        orig_en, orig_ja = voice01.generate_charon_english, voice01.generate_charon_japanese
        voice01.generate_charon_english = _must_not_be_called
        voice01.generate_charon_japanese = _must_not_be_called
        try:
            narration_dir = f"{self.tmp_dir}/narration"
            for entry in reg.CHAMPION_REGISTRATIONS:
                if entry["language"] != "en":
                    continue
                result = shared_narration.ensure_fixed_english_segment(
                    entry["name"], narration_dir, tts_backend="speech_metadata_flash_lite")
                with self.subTest(name=entry["name"]):
                    self.assertTrue(result["reused"], f"{entry['name']}はreuseされるはず: {result}")
                    self.assertEqual(result["master_audio_id"], reg.build_key(entry).master_audio_id())

            ja_entry = next(e for e in reg.CHAMPION_REGISTRATIONS if e["language"] == "ja")
            result_ja = shared_narration.ensure_fixed_japanese_segment(
                ja_entry["name"], narration_dir, tts_backend="speech_metadata_flash_lite")
            self.assertTrue(result_ja["reused"])
            self.assertEqual(result_ja["master_audio_id"], reg.build_key(ja_entry).master_audio_id())
        finally:
            voice01.generate_charon_english = orig_en
            voice01.generate_charon_japanese = orig_ja

    def test_welcome_still_resolves_to_existing_production_master_key_unaffected(self):
        """welcomeは本登録スクリプトの対象外であり、_make_english_keyの
        version("v2_flash_lite_short_style")も不変であることを、一時Store
        内でも再確認する(登録9件の実施がwelcomeのkey計算に影響しない
        ことのregression guard)。"""
        reg.run("apply")
        welcome_key = shared_narration._make_english_key(
            "welcome", shared_narration.FIXED_ENGLISH_TEXTS["welcome"], "speech_metadata_flash_lite")
        self.assertEqual(welcome_key.style_instruction_version,
                          shared_narration.SHELL_ENGLISH_FLASH_LITE_STYLE_INSTRUCTION_VERSION)
        with open(store.MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertNotIn(welcome_key.master_audio_id(), manifest,
                          "welcomeは本タスクで新規登録しない(現行Production Master継続)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
