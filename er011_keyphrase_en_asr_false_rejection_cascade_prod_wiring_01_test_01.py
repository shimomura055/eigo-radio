# ============================================================
# er011_keyphrase_en_asr_false_rejection_cascade_prod_wiring_01_test_01.py
# KEYPHRASE-EN-ASR-FALSE-REJECTION-CASCADE-PROD-WIRING-01: 受入テスト
# ============================================================
# 対象: er003_v1_repro01_main_generate.py の
#   - generate_narration_snippet_verified_strict()(asr_prompt/
#     enable_non_latin_cascade引数の既定None/False・KP経路限定確認)
#   - generate_key_phrase_component_verified()(Primary/Fallbackの両方が
#     KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT/enable_non_latin_cascade=True
#     を実際に下流へ渡していることの配線確認)
#
# TTS/ASRの外部呼び出しはすべてモックし、実APIは一切呼ばない(単体テスト
# の原則を踏襲、既存er011_tts_attempt_audio_retention_wiring_01_test.py
# と同じ方針)。

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from unittest import mock

import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01


class _FakeClassification:
    def __init__(self, classification: str):
        self.classification = classification
        self.connected_speech_info = None
        self.reading_resolver_info = None


def _fake_generate_narration_snippet(content: bytes = b"AUDIO"):
    def fake(text, language, out_path, tts_call_fn=None, safety_margin_seconds=None,
             style_prefix_override=None):
        with open(out_path, "wb") as f:
            f.write(content)
        return {"status": "OK", "text": text, "language": language, "path": out_path,
                "model": "fake-en-model", "voice": "Aoede", "duration_seconds": 1.0}
    return fake


# ============================================================
# (A) generate_narration_snippet_verified_strict(): 適用範囲限定の確認
# ============================================================
class NarrationSnippetVerifiedStrictScopeTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_kp_asr_prod_wiring_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "wiring_theme", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "kp_1_probe.wav").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_default_call_passes_prompt_none_and_cascade_disabled(self):
        # asr_prompt/enable_non_latin_cascadeを渡さない既存の全呼び出し元
        # (本文segment等)は、routing.transcribe()へprompt=Noneのまま渡り、
        # Cascade側もenable_non_latin_cascade=Falseのまま呼ばれること。
        captured = {}
        orig_transcribe = repro01.routing.transcribe
        orig_cascade = repro01.secondary_asr.evaluate_attempt_with_cascade

        def fake_transcribe(wav_path, language=None, timeout_seconds=90.0, prompt=None):
            captured["transcribe_prompt"] = prompt
            return "test phrase", None

        def fake_cascade(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                          cascade_enabled=None, force_secondary=False,
                          enable_non_latin_cascade=False, detail_out=None):
            captured["enable_non_latin_cascade"] = enable_non_latin_cascade
            if detail_out is not None:
                detail_out.update({"cascade_invoked": False, "non_latin_cascade_invoked": False, "steps": []})
            return True, False, _FakeClassification("exact")

        repro01.routing.transcribe = fake_transcribe
        repro01.secondary_asr.evaluate_attempt_with_cascade = fake_cascade
        with mock.patch.object(p9a, "generate_narration_snippet",
                                         side_effect=_fake_generate_narration_snippet()):
            try:
                core = repro01.generate_narration_snippet_verified_strict.__wrapped__
                result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=1)
            finally:
                repro01.routing.transcribe = orig_transcribe
                repro01.secondary_asr.evaluate_attempt_with_cascade = orig_cascade

        self.assertEqual(result["status"], "OK")
        self.assertIsNone(captured["transcribe_prompt"])
        self.assertFalse(captured["enable_non_latin_cascade"])

    def test_explicit_call_forwards_prompt_and_cascade_flag(self):
        # 呼び出し元が明示的にasr_prompt/enable_non_latin_cascade=Trueを
        # 渡した場合(generate_key_phrase_component_verified相当)のみ、
        # それらがそのままrouting.transcribe()/Cascadeへ転送されること。
        captured = {}
        orig_transcribe = repro01.routing.transcribe
        orig_cascade = repro01.secondary_asr.evaluate_attempt_with_cascade

        def fake_transcribe(wav_path, language=None, timeout_seconds=90.0, prompt=None):
            captured["transcribe_prompt"] = prompt
            return "test phrase", None

        def fake_cascade(text, asr_text, history, out_path, language=None, ledger_phrases=None,
                          cascade_enabled=None, force_secondary=False,
                          enable_non_latin_cascade=False, detail_out=None):
            captured["enable_non_latin_cascade"] = enable_non_latin_cascade
            if detail_out is not None:
                detail_out.update({"cascade_invoked": True, "non_latin_cascade_invoked": True, "steps": []})
            return True, False, _FakeClassification("exact")

        repro01.routing.transcribe = fake_transcribe
        repro01.secondary_asr.evaluate_attempt_with_cascade = fake_cascade
        with mock.patch.object(p9a, "generate_narration_snippet",
                                         side_effect=_fake_generate_narration_snippet()):
            try:
                core = repro01.generate_narration_snippet_verified_strict.__wrapped__
                result = core("test phrase", "en", self.out_path, "test phrase", max_attempts=1,
                              asr_prompt=repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT,
                              enable_non_latin_cascade=True)
            finally:
                repro01.routing.transcribe = orig_transcribe
                repro01.secondary_asr.evaluate_attempt_with_cascade = orig_cascade

        self.assertEqual(result["status"], "OK")
        self.assertEqual(captured["transcribe_prompt"], repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
        self.assertTrue(captured["enable_non_latin_cascade"])
        # attempts_logへ監査フィールドが記録されていること(review_lock/
        # attempt保存への記録要件)。
        self.assertTrue(result["attempts_log"][0]["asr_prompt_applied"])
        self.assertTrue(result["attempts_log"][0]["non_latin_cascade_enabled"])

    def test_japanese_branch_never_receives_prompt_even_if_caller_passes_it(self):
        # language=="ja"の場合、routing.transcribeはasr_prompt引数に
        # 関わらずprompt=Noneで呼ばれること(適用範囲は英語のみ、日本語
        # 分岐は別のASR Validator[ja_secondary]を使うため無関係)。
        captured = {}
        orig_transcribe = repro01.routing.transcribe

        def fake_transcribe(wav_path, language=None, timeout_seconds=90.0, prompt=None):
            captured["transcribe_prompt"] = prompt
            return "テストフレーズ", None

        repro01.routing.transcribe = fake_transcribe
        ja_out_path = os.path.join(self.narration_dir, "meaning_1.wav").replace("\\", "/")
        with mock.patch.object(p9a, "generate_narration_snippet",
                                         side_effect=_fake_generate_narration_snippet()):
            try:
                core = repro01.generate_narration_snippet_verified_strict.__wrapped__
                core("テストフレーズ", "ja", ja_out_path, "テストフレーズ", max_attempts=1,
                     asr_prompt="THIS SHOULD NEVER BE FORWARDED FOR JAPANESE")
            finally:
                repro01.routing.transcribe = orig_transcribe

        self.assertIsNone(captured["transcribe_prompt"])


# ============================================================
# (B) generate_key_phrase_component_verified(): Primary/Fallback両段が
# prompt/enable_non_latin_cascadeを実際に下流へ渡していることの配線確認
# ============================================================
class KeyPhraseComponentVerifiedWiringTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="er011_kp_asr_prod_wiring_kp_test_")
        self.narration_dir = os.path.join(self.tmp_dir, "wiring_theme", "a2", "narration")
        os.makedirs(self.narration_dir, exist_ok=True)
        self.out_path = os.path.join(self.narration_dir, "kp_1_probe.wav").replace("\\", "/")

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_primary_call_receives_prompt_and_cascade_flag(self):
        call_log = []
        orig = repro01.generate_narration_snippet_verified_strict

        def fake(text, language, out_path_, expected_substring, **kwargs):
            call_log.append(kwargs)
            return {"status": "OK", "model": "MOCK", "voice": "MOCK", "asr_text": text,
                    "attempts_log": [{"attempt": 1, "asr_text": text}]}

        repro01.generate_narration_snippet_verified_strict = fake
        try:
            result = repro01.generate_key_phrase_component_verified("probe phrase", self.out_path)
        finally:
            repro01.generate_narration_snippet_verified_strict = orig

        self.assertEqual(result["status"], "OK")
        self.assertEqual(len(call_log), 1, "Primaryが1回でPASSしたのでFallbackは呼ばれないはず")
        self.assertEqual(call_log[0]["asr_prompt"], repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
        self.assertTrue(call_log[0]["enable_non_latin_cascade"])
        self.assertEqual(call_log[0]["style_prefix_override"], repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)

    def test_fallback_call_also_receives_prompt_and_cascade_flag(self):
        call_log = []
        orig = repro01.generate_narration_snippet_verified_strict

        def fake(text, language, out_path_, expected_substring, **kwargs):
            stage = ("MINIMAL" if kwargs.get("style_prefix_override") == repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX
                     else "ENGLISH_LOCK")
            call_log.append({"stage": stage, **kwargs})
            if stage == "MINIMAL":
                return {"status": "STOPPED", "reason": "強制失敗(テスト用)",
                        "attempts_log": [{"attempt": 1, "asr_text": "wrong"},
                                          {"attempt": 2, "asr_text": "wrong"}]}
            return {"status": "OK", "model": "MOCK", "voice": "MOCK", "asr_text": text,
                    "attempts_log": [{"attempt": 1, "asr_text": text}]}

        repro01.generate_narration_snippet_verified_strict = fake
        try:
            result = repro01.generate_key_phrase_component_verified("probe phrase 2", self.out_path)
        finally:
            repro01.generate_narration_snippet_verified_strict = orig

        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["fallback_used"])
        self.assertEqual(len(call_log), 2, "Minimal(NG)+English Lock(OK)の2回呼ばれるはず")
        for call in call_log:
            self.assertEqual(call["asr_prompt"], repro01.KEY_PHRASE_EN_ASR_NO_TRANSLATE_PROMPT)
            self.assertTrue(call["enable_non_latin_cascade"])


if __name__ == "__main__":
    unittest.main()
