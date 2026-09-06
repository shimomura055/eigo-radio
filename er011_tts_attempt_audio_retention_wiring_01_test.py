# ============================================================
# er011_tts_attempt_audio_retention_wiring_01_test.py
# ER-011-TTS-ATTEMPT-AUDIO-RETENTION-PRODUCTION-WIRING-01: 受入テスト
# ============================================================
# TTS attemptごとの音声・ASR結果を上書きせず個別保存する仕様の受入
# テスト。(A) review_lock.save_tts_attempt_audio()単体のふるまい、
# (B) 実Production経路(generate_narration_snippet_verified_strict)へ
# 実際に配線されていること、の2層で検証する。TTS/ASRの外部呼び出しは
# すべてモックし、実APIは一切呼ばない(単体テストの原則を踏襲)。
from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er011_human_review_lock_01 as review_lock


def _sha256_bytes(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class _FakeClassification:
    def __init__(self, classification: str):
        self.classification = classification
        self.connected_speech_info = None
        self.reading_resolver_info = None


# ============================================================
# (A) save_tts_attempt_audio()単体テスト
# ============================================================
class SaveTtsAttemptAudioUnitTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_attempt_audio_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "pool_test_theme", "b1b", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "full_story_part1.wav").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_out_path(self, content: bytes):
        with open(self.out_path, "wb") as f:
            f.write(content)

    def test_multiple_attempts_produce_individual_non_overwritten_files(self):
        self._write_out_path(b"AUDIO_ATTEMPT_1")
        path1 = review_lock.save_tts_attempt_audio(self.out_path, "standard", {"asr_text": "one"})
        self._write_out_path(b"AUDIO_ATTEMPT_2_DIFFERENT_CONTENT")
        path2 = review_lock.save_tts_attempt_audio(self.out_path, "standard", {"asr_text": "two"})

        self.assertIsNotNone(path1)
        self.assertIsNotNone(path2)
        self.assertNotEqual(path1, path2, "attempt同士が同じファイルへ上書きしてはならない")
        self.assertTrue(os.path.exists(path1), "attempt1の音声が消失していない")
        self.assertTrue(os.path.exists(path2))

        with open(path1, "rb") as f:
            self.assertEqual(f.read(), b"AUDIO_ATTEMPT_1", "attempt1の内容が後続attemptで上書きされていない")
        with open(path2, "rb") as f:
            self.assertEqual(f.read(), b"AUDIO_ATTEMPT_2_DIFFERENT_CONTENT")

        # out_path自体(最終成果物)は一切変更されない(読み取り専用アクセス)。
        with open(self.out_path, "rb") as f:
            self.assertEqual(f.read(), b"AUDIO_ATTEMPT_2_DIFFERENT_CONTENT")

    def test_attempt_numbers_are_globally_monotonic_per_segment(self):
        self._write_out_path(b"A1")
        review_lock.save_tts_attempt_audio(self.out_path, "standard", {})
        self._write_out_path(b"A2")
        review_lock.save_tts_attempt_audio(self.out_path, "minimal_fallback", {})
        self._write_out_path(b"A3")
        path3 = review_lock.save_tts_attempt_audio(self.out_path, "standard", {})
        self.assertIn("_attempt3_", os.path.basename(path3))

    def test_single_attempt_case(self):
        self._write_out_path(b"ONLY_ATTEMPT")
        path = review_lock.save_tts_attempt_audio(self.out_path, "standard", {})
        self.assertIn("_attempt1_", os.path.basename(path))
        attempts_dir = os.path.join(self.narration_dir, "attempts")
        wav_files = [f for f in os.listdir(attempts_dir) if f.endswith(".wav")]
        self.assertEqual(len(wav_files), 1)

    def test_json_sidecar_records_metadata_and_matches_sha256(self):
        self._write_out_path(b"SOME_AUDIO_BYTES")
        path = review_lock.save_tts_attempt_audio(self.out_path, "custom_abcd1234", {
            "asr_text": "hello world", "audio_classification": "A", "model": "fake-model",
            "voice": "Aoede", "tts_execution_mode": "STANDARD", "verified": True,
        })
        import json
        json_path = path[:-4] + ".json"
        self.assertTrue(os.path.exists(json_path))
        with open(json_path, encoding="utf-8") as f:
            record = json.load(f)
        self.assertEqual(record["route"], "custom_abcd1234")
        self.assertEqual(record["attempt_number"], 1)
        self.assertEqual(record["segment_id"], "full_story_part1")
        self.assertEqual(record["theme_id"], "pool_test_theme")
        self.assertEqual(record["level"], "b1b")
        self.assertEqual(record["asr_text"], "hello world")
        self.assertEqual(record["model"], "fake-model")
        self.assertEqual(record["tts_execution_mode"], "STANDARD")
        self.assertEqual(record["sha256"], _sha256_bytes(path))
        self.assertEqual(record["sha256"], hashlib.sha256(b"SOME_AUDIO_BYTES").hexdigest())

    def test_bypassed_for_non_standard_out_path_layout(self):
        dummy_out = os.path.join(self.tmp_dir, "dummy_out.wav").replace("\\", "/")
        with open(dummy_out, "wb") as f:
            f.write(b"x")
        result = review_lock.save_tts_attempt_audio(dummy_out, "standard", {})
        self.assertIsNone(result)
        self.assertFalse(os.path.exists(os.path.join(self.tmp_dir, "attempts")))

    def test_returns_none_and_no_op_when_out_path_missing(self):
        # out_pathがまだ書き込まれていない(例: TTS技術的失敗で早期return
        # した場合)にsave_tts_attempt_audio()が誤って呼ばれても安全に
        # no-opであること。
        result = review_lock.save_tts_attempt_audio(self.out_path, "standard", {})
        self.assertIsNone(result)


# ============================================================
# (B) 実Production経路(generate_narration_snippet_verified_strict)への
# 配線確認。TTS/ASRはモックするが、attempt保存呼び出しは実コードパス
# (review_lock.save_tts_attempt_audio)をそのまま通す。
# ============================================================
class ProductionWiringIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_attempt_audio_wiring_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "wiring_theme", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "kp_1_test_phrase.wav").replace("\\", "/")
        self.attempts_dir = os.path.join(self.narration_dir, "attempts")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _fake_generate_narration_snippet_factory(self, contents_by_call):
        state = {"n": 0}

        def fake(text, language, out_path, tts_call_fn=None, safety_margin_seconds=None,
                 style_prefix_override=None):
            idx = state["n"]
            state["n"] += 1
            with open(out_path, "wb") as f:
                f.write(contents_by_call[idx])
            return {"status": "OK", "text": text, "language": language, "path": out_path,
                    "model": "fake-en-model", "voice": "Aoede", "duration_seconds": 1.23,
                    "sha256": _sha256_bytes(out_path)}
        return fake

    def test_ng_then_ok_creates_two_attempt_files_and_final_matches_last(self):
        # attempt1: ASR不一致(NG)。attempt2: ASR一致(OK)。
        fake_snippet = self._fake_generate_narration_snippet_factory([b"WRONG_AUDIO", b"CORRECT_AUDIO"])
        cls_sequence = [_FakeClassification("mismatch"), _FakeClassification("exact")]

        def fake_evaluate(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                           cascade_enabled=None, force_secondary=False,
                           enable_non_latin_cascade=False, detail_out=None):
            cls = cls_sequence.pop(0)
            verified = (cls.classification == "exact")
            return verified, False, cls

        with mock.patch.object(p9a, "generate_narration_snippet", side_effect=fake_snippet), \
             mock.patch.object(repro01.routing, "transcribe", side_effect=[("wrong text", None), ("test phrase", None)]), \
             mock.patch.object(repro01.secondary_asr, "evaluate_attempt_with_cascade", side_effect=fake_evaluate):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=3)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(len(result["attempts_log"]), 2)

        wav_files = sorted(f for f in os.listdir(self.attempts_dir) if f.endswith(".wav"))
        self.assertEqual(len(wav_files), 2, "NG 1回+OK 1回=2つのattempt音声が個別保存されるべき")

        attempt1_path = os.path.join(self.attempts_dir, [f for f in wav_files if "_attempt1_" in f][0])
        attempt2_path = os.path.join(self.attempts_dir, [f for f in wav_files if "_attempt2_" in f][0])
        with open(attempt1_path, "rb") as f:
            self.assertEqual(f.read(), b"WRONG_AUDIO", "NGだったattempt1の音声も上書きされず残っている")
        with open(attempt2_path, "rb") as f:
            self.assertEqual(f.read(), b"CORRECT_AUDIO")

        # 最終成果物(out_path)は、採用されたattempt2と完全に一致する(sha256)。
        final_sha256 = _sha256_bytes(self.out_path)
        self.assertEqual(final_sha256, _sha256_bytes(attempt2_path))
        self.assertNotEqual(final_sha256, _sha256_bytes(attempt1_path))

        # attempts_logにも保存パスが記録されている(review_lock台帳へ引き継がれる経路)。
        self.assertEqual(result["attempts_log"][0]["attempt_audio_path"], attempt1_path.replace("\\", "/"))
        self.assertEqual(result["attempts_log"][1]["attempt_audio_path"], attempt2_path.replace("\\", "/"))

    def test_single_attempt_success_creates_exactly_one_file(self):
        fake_snippet = self._fake_generate_narration_snippet_factory([b"ONLY_TAKE"])

        def fake_evaluate(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                           cascade_enabled=None, force_secondary=False,
                           enable_non_latin_cascade=False, detail_out=None):
            return True, False, _FakeClassification("exact")

        with mock.patch.object(p9a, "generate_narration_snippet", side_effect=fake_snippet), \
             mock.patch.object(repro01.routing, "transcribe", return_value=("test phrase", None)), \
             mock.patch.object(repro01.secondary_asr, "evaluate_attempt_with_cascade", side_effect=fake_evaluate):
            core = repro01.generate_narration_snippet_verified_strict.__wrapped__
            result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=3)

        self.assertEqual(result["status"], "OK")
        wav_files = [f for f in os.listdir(self.attempts_dir) if f.endswith(".wav")]
        self.assertEqual(len(wav_files), 1)
        self.assertEqual(_sha256_bytes(self.out_path), _sha256_bytes(os.path.join(self.attempts_dir, wav_files[0])))

    def test_regenerate_approved_continues_attempt_numbering_without_overwrite(self):
        # 1回目の呼び出し(review_lock guard込み、REGENERATE_APPROVEDでの
        # 再生成を含む)で attempt1 が保存され、承認後の2回目呼び出しで
        # attempt2 が作られる(attempt1は上書きされず残る)ことを確認する。
        fake_snippet = self._fake_generate_narration_snippet_factory([b"FIRST_RUN_AUDIO", b"SECOND_RUN_AUDIO"])

        def fake_evaluate(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                           cascade_enabled=None, force_secondary=False,
                           enable_non_latin_cascade=False, detail_out=None):
            return True, False, _FakeClassification("exact")

        with mock.patch.object(p9a, "generate_narration_snippet", side_effect=fake_snippet), \
             mock.patch.object(repro01.routing, "transcribe", return_value=("test phrase", None)), \
             mock.patch.object(repro01.secondary_asr, "evaluate_attempt_with_cascade", side_effect=fake_evaluate):
            result1 = repro01.generate_narration_snippet_verified_strict(
                "test phrase", "en", self.out_path, "test phrase", max_attempts=3)
            self.assertEqual(result1["status"], "OK")

            review_lock.approve_regenerate(self.out_path, "test phrase", approved_by="test_user")

            result2 = repro01.generate_narration_snippet_verified_strict(
                "test phrase", "en", self.out_path, "test phrase", max_attempts=3)
            self.assertEqual(result2["status"], "OK")

        wav_files = sorted(f for f in os.listdir(self.attempts_dir) if f.endswith(".wav"))
        self.assertEqual(len(wav_files), 2, "1回目のattempt1・REGENERATE後のattempt2が両方残っているべき")
        self.assertTrue(any("_attempt1_" in f for f in wav_files))
        self.assertTrue(any("_attempt2_" in f for f in wav_files))
        attempt1_file = [f for f in wav_files if "_attempt1_" in f][0]
        with open(os.path.join(self.attempts_dir, attempt1_file), "rb") as f:
            self.assertEqual(f.read(), b"FIRST_RUN_AUDIO", "REGENERATE後もattempt1の音声が上書きされていない")


if __name__ == "__main__":
    unittest.main()
