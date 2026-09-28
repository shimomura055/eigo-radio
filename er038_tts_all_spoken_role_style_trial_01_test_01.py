# ============================================================
# er038_tts_all_spoken_role_style_trial_01_test_01.py
# TTS-ALL-SPOKEN-ROLE-STYLE-TRIAL-01: 単体test(費用ゼロ、API呼び出しは
# 全てmock)。プロジェクト規約に合わせunittest.TestCase形式で実装する
# (run_project_regression.py はunittest.TestLoader().discover()を使う)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er002_common as common
import er003_v1_n3_01_tts_generate as n3_tts
import er006_master_audio_store_01 as store
import er033_tts_flash_lite_family_x_styles_01 as fl_styles
import er038_tts_all_spoken_role_style_trial_01 as trial

BASELINE_B1B = ("er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
                "hormuz__run_06_flashlite_full_kp/b1b/audit/tts_generation_results.json")
BASELINE_A2 = ("er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
               "hormuz__run_06_flashlite_full_kp/a2/audit/tts_generation_results.json")


def _baseline_segment_ids(path: str) -> set:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ids = set(data["segments"].keys())
    ids |= set(data["shared_narration"].keys())
    return ids


def _baseline_kp_sub_keys(path: str) -> set:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    sub_keys = set()
    for kp in data["key_phrases"].values():
        sub_keys |= set(kp.keys())
    return sub_keys


class RoleCoverageTest(unittest.TestCase):
    """Role漏れ0の検証(design doc §2)。"""

    def test_role_coverage_no_gap_b1b(self):
        baseline_ids = _baseline_segment_ids(BASELINE_B1B)
        mapped_ids = set(trial.SEGMENT_ROLE_MAP_B1B.keys()) - {"kp_english", "kp_japanese"}
        missing = baseline_ids - mapped_ids
        self.assertFalse(missing, f"B1B: Role未割当のsegmentがあります: {missing}")
        kp_sub_keys = _baseline_kp_sub_keys(BASELINE_B1B)
        self.assertEqual(kp_sub_keys, {"english", "japanese"})
        self.assertIn("kp_english", trial.SEGMENT_ROLE_MAP_B1B)
        self.assertIn("kp_japanese", trial.SEGMENT_ROLE_MAP_B1B)

    def test_role_coverage_no_gap_a2(self):
        baseline_ids = _baseline_segment_ids(BASELINE_A2)
        mapped_ids = set(trial.SEGMENT_ROLE_MAP_A2.keys()) - {"kp_english", "kp_japanese_meaning"}
        missing = baseline_ids - mapped_ids
        self.assertFalse(missing, f"A2: Role未割当のsegmentがあります: {missing}")
        kp_sub_keys = _baseline_kp_sub_keys(BASELINE_A2)
        self.assertEqual(kp_sub_keys, {"english", "japanese_meaning"})
        self.assertIn("kp_english", trial.SEGMENT_ROLE_MAP_A2)
        self.assertIn("kp_japanese_meaning", trial.SEGMENT_ROLE_MAP_A2)

    def test_role_map_every_segment_has_known_role(self):
        known_roles = set(trial.TRIAL_ROLE_STYLE_EN.keys()) | set(trial.TRIAL_ROLE_STYLE_JA.keys())
        for name, role in trial.SEGMENT_ROLE_MAP_B1B.items():
            self.assertIn(role, known_roles, f"{name} -> 未定義role {role}")
        for name, role in trial.SEGMENT_ROLE_MAP_A2.items():
            self.assertIn(role, known_roles, f"{name} -> 未定義role {role}")


class StandardSlowInstructionRemovedTest(unittest.TestCase):
    """Standard slow instruction除去 / Advancedにslowdown無し。"""

    def test_standard_style_excludes_slow_instruction_text(self):
        slow_fragment = "slightly slower"
        for role, style in trial.TRIAL_ROLE_STYLE_EN.items():
            self.assertNotIn(slow_fragment, style, f"{role} styleにStandard専用slow instructionが混入しています")
        # 既存Production文言自体は変更されていないことの確認(比較対象として存在するだけ)。
        self.assertIn(slow_fragment, n3_tts.A2_SLOWER_PACE_INSTRUCTION)

    def test_generate_a2_main_segments_does_not_concatenate_slower_instruction(self):
        captured = {}

        def fake_slowdown(tts_input, out_path, expected_substring, style_prefix_override=None, **kwargs):
            captured.setdefault("style_prefix_override", []).append(style_prefix_override)
            return {"status": "OK", "path": out_path, "slowdown_applied": True}

        tmp_dir = tempfile.mkdtemp(prefix="er038_test_")
        try:
            a2_dir = f"{tmp_dir}/a2"
            os.makedirs(a2_dir, exist_ok=True)
            parts = {"title": "T", "part1": "Part one text.", "heading1": "Heading one.",
                     "body2": "Body two text.", "heading2": "Heading two.", "body3": "Body three text.",
                     "in_one_line": "One line summary."}
            support = {"preview": "プレビュー。", "comment_1": "コメント1。", "comment_2": "コメント2。",
                       "comment_3": "コメント3。", "comment_4": "コメント4。"}
            with open(f"{a2_dir}/parts.json", "w", encoding="utf-8") as f:
                json.dump(parts, f)
            with open(f"{a2_dir}/a2_support_texts.json", "w", encoding="utf-8") as f:
                json.dump(support, f)

            with mock.patch.object(trial.n3_tts, "generate_a2_segment_with_slowdown", side_effect=fake_slowdown), \
                 mock.patch.object(trial.crosslevel_common, "generate_english_segment_with_fallback",
                                    return_value={"status": "OK", "path": "x"}), \
                 mock.patch.object(trial, "generate_ja_role_style", return_value={"status": "OK", "path": "x"}):
                trial.generate_a2_main_segments(tmp_dir, "日本語タイトル", "structured_separation")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        for style in captured["style_prefix_override"]:
            self.assertNotIn("slightly slower", style)
            self.assertIn(style, trial.TRIAL_ROLE_STYLE_EN.values())


class ProductionConstantsUnchangedTest(unittest.TestCase):
    """Production style定数の不変性の確認。"""

    def test_production_6role_style_constants_unchanged(self):
        # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
        # ユーザー正式決定(E2、TTS-VARIABLE-SPOKEN-ROLE-STYLE-TRIAL-02)を
        # TOPIC_INTRO/FULL_STORY/IN_ONE_LINEへ反映したため期待値を更新
        # (E0→E2、逐語)。PREVIEW/COMMENT/HEADING_READOUTはE2未検証のため
        # 不変(E0のまま)。
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN, {
            "TOPIC_INTRO": "brief, clear, engaging news topic introduction with natural emphasis on the topic; "
                           "not dramatic.",
            "PREVIEW": "calm, conversational",
            "COMMENT": "calm, conversational",
            "FULL_STORY": "calm, steady news narration with natural emphasis at key points and turns; "
                          "not dramatic.",
            "HEADING_READOUT": "brief and clear",
            "IN_ONE_LINE": "concise, clear, landing naturally as a settled conclusion; not flat, not dramatic.",
        })
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK, ["natural, clear, conversational", "clear"])
        payload = json.dumps(fl_styles.FAMILY_X_ROLE_STYLE_EN, sort_keys=True, ensure_ascii=False)
        actual_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(len(actual_hash), 64)

    def test_trial_role_style_reuses_existing_6role_values_unchanged(self):
        # TTS-VARIABLE-ROLE-STYLE-PRODUCTION-WIRING-01(Phase B、2026-09-28):
        # trial.TRIAL_ROLE_STYLE_EN(このTrialスクリプト自身、無変更・E0の
        # まま)と、Production側fl_styles.FAMILY_X_ROLE_STYLE_EN(E2へ更新
        # 済み)は、TOPIC_INTRO/FULL_STORY/IN_ONE_LINEの3roleではもはや
        # 一致しない(意図的な差分、E0→E2)。PREVIEW/COMMENT/HEADING_READOUT
        # の3roleはE2未検証のためProduction側も不変で、引き続き一致する。
        self.assertEqual(trial.TRIAL_ROLE_STYLE_EN["PREVIEW"], fl_styles.FAMILY_X_ROLE_STYLE_EN["PREVIEW"])
        self.assertEqual(trial.TRIAL_ROLE_STYLE_EN["COMMENT"], fl_styles.FAMILY_X_ROLE_STYLE_EN["COMMENT"])
        self.assertEqual(trial.TRIAL_ROLE_STYLE_EN["HEADING"], fl_styles.FAMILY_X_ROLE_STYLE_EN["HEADING_READOUT"])
        self.assertNotEqual(trial.TRIAL_ROLE_STYLE_EN["TOPIC_INTRO"], fl_styles.FAMILY_X_ROLE_STYLE_EN["TOPIC_INTRO"])
        self.assertNotEqual(trial.TRIAL_ROLE_STYLE_EN["FULL_STORY"], fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"])
        self.assertNotEqual(trial.TRIAL_ROLE_STYLE_EN["IN_ONE_LINE"], fl_styles.FAMILY_X_ROLE_STYLE_EN["IN_ONE_LINE"])


class NoWpmGuardTest(unittest.TestCase):
    def test_all_trial_styles_pass_no_wpm_guard(self):
        for style in list(trial.TRIAL_ROLE_STYLE_EN.values()) + list(trial.TRIAL_ROLE_STYLE_JA.values()):
            common.assert_no_wpm_specification(style)  # raiseしなければPASS


class ProductionMasterReuseTest(unittest.TestCase):
    """修正1回目(ユーザー指示反映): num_two/num_threeのProduction Master
    reuse経路が、Production Master Audio Store(er006_output/
    master_audio_store_01/)へ一切書き込まないことを確認する。"""

    PRODUCTION_MANIFEST = "er006_output/master_audio_store_01/manifest.json"

    def test_reuse_constants_canonical_text_hash_matches_production_manifest_entries(self):
        for name, entry in trial.PRODUCTION_MASTER_REUSE_SHELL_SEGMENTS.items():
            expected_hash = hashlib.sha256(entry["canonical_text"].encode("utf-8")).hexdigest()[:16]
            with open(self.PRODUCTION_MANIFEST, encoding="utf-8") as f:
                manifest = json.load(f)
            self.assertIn(entry["master_audio_id"], manifest, f"{name}: master_audio_idがProduction Storeに無い")
            key = manifest[entry["master_audio_id"]]["key"]
            self.assertEqual(key["canonical_text_hash"], expected_hash)
            self.assertEqual(key["tts_model_id"], entry["tts_model_id"])
            self.assertEqual(key["style_instruction_version"], entry["style_instruction_version"])

    def test_reuse_production_master_segment_copies_without_touching_production_store(self):
        before_mtime = os.path.getmtime(self.PRODUCTION_MANIFEST)
        with open(self.PRODUCTION_MANIFEST, "rb") as f:
            before_bytes = f.read()

        tmp_dir = tempfile.mkdtemp(prefix="er038_test_")
        try:
            src = os.path.join(tmp_dir, "fake_master.wav")
            with open(src, "wb") as f:
                f.write(b"\x00\x00" * 10)
            out_path = os.path.join(tmp_dir, "num_two_charon.wav")
            fake_entry = {
                "master_audio_id": "fakeid123", "audio_path": src, "canonical_text": "Two.",
                "style_instruction_id": "charon_english_fixed_shell",
                "style_instruction_version": "v2_flash_lite_short_style",
                "tts_model_id": "gemini-3.8-flash-lite-tts", "asr_text_evidence": "2",
                "asr_evidence_source": "dummy",
            }
            result = trial._reuse_production_master_segment(fake_entry, out_path)
            self.assertEqual(result["status"], "OK")
            self.assertTrue(result["reused_from_production_master"])
            self.assertEqual(result["master_audio_id"], "fakeid123")
            self.assertEqual(result["asr_text"], "2")
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "rb") as f:
                self.assertEqual(f.read(), b"\x00\x00" * 10)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.assertEqual(os.path.getmtime(self.PRODUCTION_MANIFEST), before_mtime)
        with open(self.PRODUCTION_MANIFEST, "rb") as f:
            after_bytes = f.read()
        self.assertEqual(before_bytes, after_bytes, "Production Master Storeが変更されています")

    def test_generate_shell_segments_skips_store_get_or_generate_for_reused_names(self):
        tmp_dir = tempfile.mkdtemp(prefix="er038_test_")
        try:
            narration_dir = os.path.join(tmp_dir, "narration")
            calls = []

            def fake_get_or_generate(key, out_path, gen_fn):
                calls.append(key.canonical_text)
                with open(out_path, "wb") as f:
                    f.write(b"\x00\x00" * 5)
                return {"status": "OK", "reused": False, "master_audio_id": "x", "attempts_log": []}

            def fake_reuse(reuse_entry, out_path):
                with open(out_path, "wb") as f:
                    f.write(b"\x00\x00" * 5)
                return {"status": "OK", "reused": True, "reused_from_production_master": True,
                        "master_audio_id": reuse_entry["master_audio_id"], "attempts_log": [],
                        "asr_text": reuse_entry["asr_text_evidence"]}

            with mock.patch.object(trial.store, "get_or_generate", side_effect=fake_get_or_generate), \
                 mock.patch.object(trial, "_reuse_production_master_segment", side_effect=fake_reuse):
                results = trial.generate_shell_segments(
                    narration_dir, "b1b", "speech_metadata_flash_lite",
                    reuse_production_master=frozenset({"num_two", "num_three"}))
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.assertEqual(results["num_two"]["status"], "OK")
        self.assertTrue(results["num_two"]["reused_from_production_master"])
        self.assertEqual(results["num_three"]["status"], "OK")
        self.assertTrue(results["num_three"]["reused_from_production_master"])
        self.assertNotIn("Two.", calls)
        self.assertNotIn("Three.", calls)
        self.assertIn("Welcome to English Your Way.", calls)  # 非reuse segmentは従来通りStore経由


class MasterAudioStoreIsolationTest(unittest.TestCase):
    def test_trial_master_audio_store_redirects_and_restores(self):
        orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        self.assertEqual(store.STORE_DIR, "er006_output/master_audio_store_01")
        with trial.trial_master_audio_store("er038_output/tts_all_spoken_role_style_trial_01/dummy_store"):
            self.assertEqual(store.STORE_DIR, "er038_output/tts_all_spoken_role_style_trial_01/dummy_store")
            self.assertTrue(store.AUDIO_DIR.startswith("er038_output/"))
            self.assertTrue(store.MANIFEST_PATH.startswith("er038_output/"))
            self.assertTrue(store.TELEMETRY_PATH.startswith("er038_output/"))
        self.assertEqual((store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH), orig)


class JaRoleStyleGeneratorTest(unittest.TestCase):
    """JA role-style生成: style_prefixが最下層のresolve_tts_call_and_
    promptへ実際に渡ることをmockで確認する(実TTS/ASR呼び出しは行わない)。"""

    def test_generate_ja_role_style_passes_style_prefix_to_lowest_layer(self):
        tmp_dir = tempfile.mkdtemp(prefix="er038_test_")
        out_path = os.path.join(tmp_dir, "seg.wav")
        captured = {}

        def fake_resolve(text, style_prefix, model_name, voice_name, out_path_arg, tts_backend=None, **kwargs):
            captured["style_prefix"] = style_prefix
            captured["voice_name"] = voice_name
            return (lambda prompt: b"\x00\x00" * 100), (text, style_prefix)

        fake_cls = mock.Mock(classification="NORMALIZED_MATCH")

        try:
            with mock.patch.object(trial.flw, "resolve_tts_call_and_prompt", side_effect=fake_resolve), \
                 mock.patch.object(trial.common, "_call_tts_with_retry",
                                    return_value=(b"\x00\x00" * 100, 0, True, None)), \
                 mock.patch.object(trial.common, "pcm_bytes_to_float_mono", return_value=[0.0] * 24000), \
                 mock.patch.object(trial.p3u, "trim_english_keyword_silence",
                                    return_value=([0.0] * 24000, {"raw_duration_seconds": 1.0})), \
                 mock.patch.object(trial.safety, "detect_duration_anomaly",
                                    return_value={"is_anomaly": False}), \
                 mock.patch.object(trial.common, "write_wav_float", return_value=None), \
                 mock.patch.object(trial.routing, "transcribe", return_value=("テストです", None)), \
                 mock.patch.object(trial.ja_secondary, "evaluate_attempt_ja_with_cascade",
                                    return_value=(True, False, fake_cls)), \
                 mock.patch.object(trial.common, "measure_metrics", return_value={"clipping_detected": False}), \
                 mock.patch("builtins.open", mock.mock_open(read_data=b"dummy")):
                result = trial.generate_ja_role_style(
                    "テストです", out_path, "はっきりと、落ち着いて", "Charon",
                    lambda *a, **k: {"status": "STOPPED"}, "structured_separation")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(captured["style_prefix"], "はっきりと、落ち着いて")
        self.assertEqual(captured["voice_name"], "Charon")
        self.assertEqual(result["style_prefix_used"], "はっきりと、落ち着いて")

    def test_generate_ja_role_style_falls_back_to_unmodified_production_minimal_fn(self):
        tmp_dir = tempfile.mkdtemp(prefix="er038_test_")
        out_path = os.path.join(tmp_dir, "seg.wav")
        fallback_calls = []

        def fake_minimal_fallback(text, out_path_arg, tts_backend=None):
            fallback_calls.append((text, tts_backend))
            return {"status": "STOPPED", "reason": "mock fallback also fails"}

        try:
            with mock.patch.object(trial.flw, "resolve_tts_call_and_prompt",
                                    return_value=(lambda p: b"\x00\x00" * 10, ("t", "s"))), \
                 mock.patch.object(trial.common, "_call_tts_with_retry",
                                    return_value=(b"", 0, False, "technical failure")):
                result = trial.generate_ja_role_style(
                    "テストです", out_path, "スタイル", "Aoede", fake_minimal_fallback, "structured_separation")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        self.assertEqual(result["status"], "STOPPED")
        self.assertGreaterEqual(len(fallback_calls), 1)
        self.assertEqual(fallback_calls[0][0], "テストです")  # reading-safety適用後のtts_input


class KeyPhraseExplanationRoleTest(unittest.TestCase):
    """Advancedの英語解説をStandardの日本語意味として扱わないことの確認
    (design doc §1-3: KEY_PHRASE_EXPLANATION_ENは定義のみ・本Trialでは
    音声生成しない)。"""

    def test_key_phrase_explanation_role_is_defined_but_not_generated(self):
        self.assertIn("KEY_PHRASE_EXPLANATION_EN", trial.TRIAL_ROLE_STYLE_EN)
        for name, role in trial.SEGMENT_ROLE_MAP_B1B.items():
            self.assertNotEqual(role, "KEY_PHRASE_EXPLANATION_EN")
        for name, role in trial.SEGMENT_ROLE_MAP_A2.items():
            self.assertNotEqual(role, "KEY_PHRASE_EXPLANATION_EN")

    def test_kp_ja_role_used_for_both_levels_same_style(self):
        # Standard/AdvancedのKey Phrase JA(意味読み上げ)は同一style(design
        # doc §1-3: Advanced固有の英語解説artifactが無いため、現状は両者とも
        # 同じ内容[EN句+JA意味]のまま、styleのみ比較する)。
        self.assertEqual(trial.SEGMENT_ROLE_MAP_B1B["kp_japanese"], "KEY_PHRASE_JA")
        self.assertEqual(trial.SEGMENT_ROLE_MAP_A2["kp_japanese_meaning"], "KEY_PHRASE_JA")


if __name__ == "__main__":
    unittest.main()
