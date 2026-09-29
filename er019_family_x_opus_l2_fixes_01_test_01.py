# ============================================================
# er019_family_x_opus_l2_fixes_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01 (W5)
# ============================================================
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_family_x_opus_l2_fixes_01_test_01 -v
#
# API呼び出し: 0(実LLM/TTS呼び出しは全てmock)。費用¥0。
#
# 対象: REPORT行459-548のOpus L2所見(BLOCKER-1、MAJOR-1〜4、N-4、N-7)
# の是正+Standard KP日本語意味へのJ3配線(正式決定)の追加テスト。既存
# 個別テストファイル(er019_family_x_kp_structure_wiring_01_test_01.py、
# er019_family_x_variable_role_style_wiring_01_test_01.py、
# er012_e_family_entertainment_two_level_runner_test_01.py)で既に更新・
# 追加した観点は重複させず、ここでは以下に絞る:
#   A. BLOCKER-1: KP英語解説のfail-closed(text-gate status!="OK"はTTSを
#      呼ばずSTOPPED)
#   B. MAJOR-1: _generate_or_reuse_kpのexpected_text/require_style_version
#      guard(単体)
#   C. MAJOR-2: split_family_x_article_text_v2()の新NGステータス
#      (NG_MISSING_TITLE/NG_MISSING_IN_ONE_LINE/NG_HEADING_IN_BODY)+
#      generate_family_x_standard_a2_no_headingの`^#\s+`必須Gate
#   D. MAJOR-3: assert_production_tts_backend()のfail-fast
#   G. N-7(schema件数)・N-4(Master Store reuse返り値へのkey追加)
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er003_v1_n3_01_standard_a2_generate as std_gen
import er006_master_audio_store_01 as store
import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_kp_explanation_01 as kp_explanation_gen


# ============================================================
# A. BLOCKER-1: KP英語解説のfail-closed
# ============================================================
class KpExplanationFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.kp = {"items": [
            {"rank": 1, "used_form": "raise privacy concerns", "japanese_gloss": "懸念",
             "display_phrase": "raise privacy concerns", "source_sentence": "The plan may raise privacy concerns."},
        ]}

    def _run(self, explanation_bundle):
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations",
                                return_value=explanation_bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: {
                                    "status": "OK", "path": "narration/kp1_en.wav", "sha256": "sha_en_1"}), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified") as expl_mock:
            kp_results, _ = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        return kp_results, expl_mock

    def test_ng_status_does_not_call_tts_and_records_stopped(self):
        bundle = {"items": {1: {"english_explanation": "over 15 words " * 3, "qa": {"passed": False,
                                                                                     "new_fact_tokens": []},
                                 "status": "NG"}},
                   "audit": {}}
        kp_results, expl_mock = self._run(bundle)
        expl_mock.assert_not_called()
        self.assertEqual(kp_results[1]["explanation"]["status"], "STOPPED")
        self.assertIn("NG", kp_results[1]["explanation"]["reason"])

    def test_ng_phrase_mismatch_does_not_call_tts(self):
        bundle = {"items": {1: {"english_explanation": None, "qa": None, "status": "NG_PHRASE_MISMATCH"}},
                   "audit": {}}
        kp_results, expl_mock = self._run(bundle)
        expl_mock.assert_not_called()
        self.assertEqual(kp_results[1]["explanation"]["status"], "STOPPED")

    def test_missing_status_key_is_treated_as_not_ok(self):
        """parse失敗等でstatusキー自体が欠落しているケースもfail-closed。"""
        bundle = {"items": {1: {"english_explanation": None, "qa": None}}, "audit": {}}
        kp_results, expl_mock = self._run(bundle)
        expl_mock.assert_not_called()
        self.assertEqual(kp_results[1]["explanation"]["status"], "STOPPED")

    def test_ok_status_calls_tts_normally(self):
        bundle = {"items": {1: {"english_explanation": "to make people worried", "qa": {"passed": True},
                                 "status": "OK"}}, "audit": {}}
        with mock.patch.object(runner.kp_explanation_gen, "generate_kp_explanations", return_value=bundle), \
             mock.patch.object(runner.shared_narration, "ensure_key_phrase_english_component",
                                side_effect=lambda *_a, **_kw: {
                                    "status": "OK", "path": "narration/kp1_en.wav", "sha256": "sha_en_1"}), \
             mock.patch.object(runner, "generate_key_phrase_explanation_en_verified",
                                return_value={"status": "OK", "path": "x", "sha256": "y"}) as expl_mock:
            kp_results, _ = runner._generate_key_phrase_segments_b1(self.kp, "narration")
        expl_mock.assert_called_once()
        self.assertEqual(kp_results[1]["explanation"]["status"], "OK")

    def test_stopped_explanation_blocks_audio_validation_gate(self):
        """既存verify_episode_audio_validation_gateがkp{rank}_explanation=
        STOPPEDでassemblyをblockすることを確認する(BLOCKER-1是正の効果を
        既存Gateで実地検証)。"""
        import er003_v1_n3_01_assemble as asm
        tmpdir = tempfile.mkdtemp(prefix="family_x_kp_explanation_gate_")
        try:
            out_dir = tmpdir
            os.makedirs(f"{out_dir}/narration", exist_ok=True)
            data = {
                "segments": {},
                "key_phrases": {
                    "1": {
                        "english": {"status": "OK", "path": f"{out_dir}/narration/kp1_en.wav",
                                    "sha256": "a", "disfluency_checked": True},
                        "explanation": {"status": "STOPPED", "reason": "text-gate NG"},
                        "phrase_repeat": {"status": "OK", "path": f"{out_dir}/narration/kp1_en.wav",
                                          "sha256": "a"},
                    }
                },
                "style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION,
            }
            os.makedirs(f"{out_dir}/audit", exist_ok=True)
            with open(f"{out_dir}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
                json.dump(data, f)
            with self.assertRaises(RuntimeError) as ctx:
                asm.verify_episode_audio_validation_gate(out_dir, "B1")
            self.assertIn("kp1_explanation", str(ctx.exception))
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_ng_accepted_after_retry_status_removed_from_module(self):
        """NG_ACCEPTED_AFTER_RETRYという「採用」ステータスの廃止(BLOCKER-1)。"""
        def call_fn(user_message):
            too_long = " ".join(["word"] * (kp_explanation_gen.MAX_WORDS + 5))
            parsed = {"explanations": [{"phrase": "raise privacy concerns", "english_explanation": too_long}]}
            return parsed, kp_explanation_gen.MODEL, {"input_tokens": 1, "output_tokens": 1}, "resp"

        items = [{"rank": 1, "display_phrase": "raise privacy concerns",
                  "source_sentence": "The plan may raise privacy concerns.", "japanese_gloss": "懸念"}]
        result = kp_explanation_gen.generate_kp_explanations(items, call_fn=call_fn)
        self.assertEqual(result["items"][1]["status"], "NG")
        self.assertNotEqual(result["items"][1]["status"], "NG_ACCEPTED_AFTER_RETRY")


# ============================================================
# B. MAJOR-1: _generate_or_reuse_kp text/style_version guard(単体)
# ============================================================
class GenerateOrReuseKpGuardTests(unittest.TestCase):
    def test_expected_text_mismatch_forces_regeneration(self):
        cached = {"key_phrases": {"1": {"explanation": {
            "status": "OK", "path": "kp1_explanation_en.wav", "canonical_text": "old text"}}}}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            runner._generate_or_reuse_kp(cached, 1, "explanation", "kp1_explanation_en.wav", gen,
                                          expected_text="new text")
        self.assertEqual(calls["n"], 1, "textが変わっていればreuseせず再生成するはず")

    def test_expected_text_match_reuses(self):
        cached = {"key_phrases": {"1": {"explanation": {
            "status": "OK", "path": "kp1_explanation_en.wav", "canonical_text": "same text",
            "style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION}}},
            "style_version": runner.FAMILY_X_VARIABLE_ROLE_STYLE_VERSION}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse_kp(cached, 1, "explanation", "kp1_explanation_en.wav", gen,
                                                    expected_text="same text", require_style_version=True)
        self.assertEqual(calls["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))

    def test_style_version_mismatch_forces_regeneration_even_when_text_matches(self):
        cached = {"key_phrases": {"1": {"explanation": {
            "status": "OK", "path": "kp1_explanation_en.wav", "canonical_text": "same text"}}},
            "style_version": "old_version"}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            runner._generate_or_reuse_kp(cached, 1, "explanation", "kp1_explanation_en.wav", gen,
                                          expected_text="same text", require_style_version=True)
        self.assertEqual(calls["n"], 1)

    def test_style_version_guard_not_applied_when_require_style_version_false(self):
        """role="english"等、require_style_version=False(既定)の呼び出し元は
        style_versionを見ない(既存挙動を維持)。"""
        cached = {"key_phrases": {"1": {"english": {
            "status": "OK", "path": "kp1_en.wav", "canonical_text": "phrase"}}},
            "style_version": "old_version"}
        calls = {"n": 0}

        def gen():
            calls["n"] += 1
            return {"status": "OK"}

        with mock.patch.object(runner.os.path, "exists", return_value=True):
            result = runner._generate_or_reuse_kp(cached, 1, "english", "kp1_en.wav", gen,
                                                    expected_text="phrase")
        self.assertEqual(calls["n"], 0)
        self.assertTrue(result.get("reused_from_previous_run"))


# ============================================================
# C. MAJOR-2: split_family_x_article_text_v2()構造Gate対称化
# ============================================================
class SplitV2StructureGateTests(unittest.TestCase):
    _BODY = ("P1 has enough words here today please read.\n\n"
             "P2 has enough words here today please read.\n\n"
             "P3 has enough words here today please read.")

    def test_missing_title_returns_ng_status_not_ok(self):
        text = f"{self._BODY}\n\n## In one line\nS."
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "NG_MISSING_TITLE")
        self.assertNotEqual(result["status"], "OK")

    def test_missing_in_one_line_returns_ng_status_not_runtimeerror(self):
        """旧実装はRuntimeErrorを直接送出しretryされなかった(MAJOR-2)。
        新実装はstatusで返し、呼び出し側の共通retryヘルパーに載る。"""
        text = f"# T\n\n{self._BODY}\n"
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "NG_MISSING_IN_ONE_LINE")

    def test_heading_in_body_detected(self):
        text = f"# T\n\nP1 has enough words here today please.\n\n### Sneaky Heading\n\n{self._BODY}\n\n## In one line\nS."
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "NG_HEADING_IN_BODY")

    def test_valid_structure_still_returns_ok(self):
        text = f"# T\n\n{self._BODY}\n\n## In one line\nS."
        result = sc.split_family_x_article_text_v2(text)
        self.assertEqual(result["status"], "OK")

    def test_non_ok_status_is_caught_by_existing_retry_helper(self):
        """`_family_x_ensure_split_or_paragraph_retry()`は既にstatus!="OK"を
        汎用的に1回retryする設計であり、新NGステータスも同じ経路でretry
        される(呼び出し側の変更不要であることの確認)。"""
        import er012_e_family_entertainment_two_level_runner_01 as e_runner
        missing_title_text = f"{self._BODY}\n\n## In one line\nS."
        fixed_text = f"# T\n\n{self._BODY}\n\n## In one line\nS."
        calls = {"n": 0}

        def regen():
            calls["n"] += 1
            return fixed_text

        outcome = e_runner._family_x_ensure_split_or_paragraph_retry(missing_title_text, regen, "Test")
        self.assertTrue(outcome["paragraph_retried"])
        self.assertEqual(calls["n"], 1)
        self.assertEqual(outcome["split"]["status"], "OK")


class StandardA2TitleGateSymmetryTests(unittest.TestCase):
    """generate_family_x_standard_a2_no_heading()のparse gateをAdvanced
    (_FAMILY_X_TITLE_BODY_RE、`^#\\s+`必須)と対称化した(MAJOR-2)。"""

    def _mock_result(self, raw_text, model="m", response_id="r"):
        return {"raw_text": raw_text, "model": model, "response_id": response_id,
                "usage": {"input_tokens": 1, "output_tokens": 1}}

    def test_title_without_hash_prefix_is_rejected_then_retried(self):
        bad = "Title Without Hash\n\nBody text here."
        good = "# Title With Hash\n\nBody text here."
        calls = {"n": 0}

        def fake_run_writer_no_search(client, prompt, model=None, developer=None):
            calls["n"] += 1
            return self._mock_result(bad if calls["n"] == 1 else good)

        with mock.patch.object(std_gen.vfl01, "run_writer_no_search", side_effect=fake_run_writer_no_search), \
             mock.patch.object(std_gen.vfl01, "get_client", return_value=object()), \
             mock.patch.object(std_gen.routing, "require_model", return_value="m"), \
             mock.patch.object(std_gen, "_load_pricing", return_value=lambda *_a, **_kw: 0.0):
            result = std_gen.generate_family_x_standard_a2_no_heading("advanced text", max_attempts=2)
        self.assertEqual(calls["n"], 2, "1行目に`# `が無い場合はretryされるはず")
        self.assertEqual(result.text, good)

    def test_title_with_hash_prefix_passes_on_first_attempt(self):
        good = "# Title With Hash\n\nBody text here."
        calls = {"n": 0}

        def fake_run_writer_no_search(client, prompt, model=None, developer=None):
            calls["n"] += 1
            return self._mock_result(good)

        with mock.patch.object(std_gen.vfl01, "run_writer_no_search", side_effect=fake_run_writer_no_search), \
             mock.patch.object(std_gen.vfl01, "get_client", return_value=object()), \
             mock.patch.object(std_gen.routing, "require_model", return_value="m"), \
             mock.patch.object(std_gen, "_load_pricing", return_value=lambda *_a, **_kw: 0.0):
            std_gen.generate_family_x_standard_a2_no_heading("advanced text", max_attempts=2)
        self.assertEqual(calls["n"], 1)


# ============================================================
# D. MAJOR-3: TTS backend fail-fast
# ============================================================
class ProductionBackendGateTests(unittest.TestCase):
    def test_approved_backend_passes(self):
        runner.assert_production_tts_backend("speech_metadata_flash_lite", allow_legacy_backend=False)

    def test_legacy_backend_without_flag_raises(self):
        with self.assertRaises(RuntimeError):
            runner.assert_production_tts_backend("structured_separation", allow_legacy_backend=False)

    def test_legacy_backend_with_explicit_flag_passes(self):
        runner.assert_production_tts_backend("structured_separation", allow_legacy_backend=True)

    def test_main_cli_has_allow_legacy_backend_flag(self):
        parser = runner.build_arg_parser()
        args = parser.parse_args(["--slug", "s", "--run", "r"])
        self.assertFalse(args.allow_legacy_backend)
        args2 = parser.parse_args(["--slug", "s", "--run", "r", "--allow-legacy-backend"])
        self.assertTrue(args2.allow_legacy_backend)


# ============================================================
# G. MINOR: N-7(schema件数)・N-4(Master Store reuse返り値へのkey追加)
# ============================================================
class ExplanationSchemaItemCountTests(unittest.TestCase):
    def test_schema_min_max_items_derived_from_actual_item_count(self):
        schema = kp_explanation_gen._build_explanation_json_schema(3)
        props = schema["schema"]["properties"]["explanations"]
        self.assertEqual(props["minItems"], 3)
        self.assertEqual(props["maxItems"], 3)
        # 元のEXPLANATION_JSON_SCHEMA(5固定、sha256算出基準)は不変。
        self.assertEqual(kp_explanation_gen.EXPLANATION_JSON_SCHEMA["schema"]["properties"]
                          ["explanations"]["minItems"], 5)

    def test_generate_kp_explanations_with_non_five_items_does_not_hard_fail_on_count_mismatch(self):
        items = [
            {"rank": 1, "display_phrase": "p1", "source_sentence": "s1", "japanese_gloss": "g1"},
            {"rank": 2, "display_phrase": "p2", "source_sentence": "s2", "japanese_gloss": "g2"},
            {"rank": 3, "display_phrase": "p3", "source_sentence": "s3", "japanese_gloss": "g3"},
        ]
        captured_schema = {}

        def call_fn(user_message):
            return ({"explanations": [{"phrase": it["display_phrase"], "english_explanation": "ok"}
                                        for it in items]},
                    kp_explanation_gen.MODEL, {"input_tokens": 1, "output_tokens": 1}, "resp")

        result = kp_explanation_gen.generate_kp_explanations(items, call_fn=call_fn)
        self.assertEqual(len(result["items"]), 3)
        for row in result["items"].values():
            self.assertEqual(row["status"], "OK")


class MasterStoreReuseKeyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.orig_store_dir = store.STORE_DIR
        self.orig_audio_dir = store.AUDIO_DIR
        self.orig_manifest = store.MANIFEST_PATH
        self.orig_telemetry = store.TELEMETRY_PATH
        self.tmp_dir = tempfile.mkdtemp(prefix="master_store_n4_")
        store.STORE_DIR = self.tmp_dir
        store.AUDIO_DIR = f"{self.tmp_dir}/audio"
        store.MANIFEST_PATH = f"{self.tmp_dir}/manifest.json"
        store.TELEMETRY_PATH = f"{self.tmp_dir}/reuse_telemetry.jsonl"

    def tearDown(self):
        store.STORE_DIR = self.orig_store_dir
        store.AUDIO_DIR = self.orig_audio_dir
        store.MANIFEST_PATH = self.orig_manifest
        store.TELEMETRY_PATH = self.orig_telemetry
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_dummy_wav(self, path):
        import wave
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(b"\x00\x00" * 2400)

    def test_reused_and_generated_results_both_include_master_audio_key(self):
        def fake_generate(out_path):
            self._write_dummy_wav(out_path)
            return {"status": "OK"}

        key = store.MasterAudioKey(language="en", speaker_voice="Charon",
                                    tts_model_id="gemini-2.5-pro-preview-tts",
                                    canonical_text="Welcome to English Your Way.")
        r1 = store.get_or_generate(key, f"{self.tmp_dir}/out1.wav", fake_generate)
        self.assertIn("master_audio_key", r1)
        self.assertEqual(r1["master_audio_key"], key.as_dict())

        r2 = store.get_or_generate(key, f"{self.tmp_dir}/out2.wav", fake_generate)
        self.assertTrue(r2["reused"])
        self.assertIn("master_audio_key", r2)
        self.assertEqual(r2["master_audio_key"], key.as_dict())


if __name__ == "__main__":
    unittest.main()
