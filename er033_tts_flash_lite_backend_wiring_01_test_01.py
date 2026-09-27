# ============================================================
# er033_tts_flash_lite_backend_wiring_01_test_01.py
# TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 1
# ============================================================
# 実際のGemini API呼び出しは一切行わない(¥0)。既定backend
# (structured_separation)が既存呼び出しとbyte-identicalであること、
# SDK未対応時のfail-closed、speech_metadata backendのWAV/PCM防御・
# resample・routing contract統合をunit testで検証する。
from __future__ import annotations

import io
import unittest
import wave
from unittest import mock

import numpy as np

import er003_b1_p4c_audio as p4c
import er006_model_routing_contract_01 as routing_contract
import er033_tts_flash_lite_backend_wiring_01 as flw
import er033_tts_flash_lite_family_x_styles_01 as fl_styles


class DefaultBackendByteIdenticalTests(unittest.TestCase):
    """既定backend(structured_separation)は、既存の
    `batch_wiring.make_batch_tts_call_fn(...) + p4c.build_tts_prompt(...)`
    という2行パターンとbyte-identicalであることを確認する。"""

    def test_prompt_is_byte_identical_to_legacy_build_tts_prompt(self):
        text, style = "Hello world.", "Speak calmly and clearly."
        _, prompt = flw.resolve_tts_call_and_prompt(
            text, style, "gemini-2.5-pro-preview-tts", "Aoede", "out.wav",
            tts_backend="structured_separation")
        self.assertEqual(prompt, p4c.build_tts_prompt(text, style))

    def test_call_fn_is_produced_via_batch_wiring_for_default_backend(self):
        # tts_call_fnの型(callable)だけを確認する(実際のAPI呼び出しはしない)。
        call_fn, _ = flw.resolve_tts_call_and_prompt(
            "text", "style", "gemini-2.5-pro-preview-tts", "Aoede", "out.wav",
            tts_backend="structured_separation")
        self.assertTrue(callable(call_fn))

    def test_unknown_backend_raises_value_error(self):
        with self.assertRaises(ValueError):
            flw.resolve_tts_call_and_prompt("t", "s", "m", "v", "o.wav", tts_backend="bogus")


class SDKFailClosedGuardTests(unittest.TestCase):
    """Production `.venv`(google-genai 2.11.0)ではspeech_metadata_flash_lite
    backendがfail-closedで停止することを確認する(実際のSDKバージョンに
    依存しないよう、_parse_genai_versionをmockして両方向を検証する)。"""

    def test_below_minimum_version_raises(self):
        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 11, 0)):
            with self.assertRaises(flw.TTSBackendSDKUnsupportedError):
                flw.assert_sdk_supports_speech_metadata()

    def test_at_minimum_version_does_not_raise(self):
        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 25, 0)):
            flw.assert_sdk_supports_speech_metadata()  # raiseしないことを確認

    def test_above_minimum_version_does_not_raise(self):
        with mock.patch.object(flw, "_parse_genai_version", return_value=(3, 0, 0)):
            flw.assert_sdk_supports_speech_metadata()

    def test_resolve_tts_call_and_prompt_fails_closed_for_flash_lite_on_old_sdk(self):
        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 11, 0)):
            with self.assertRaises(flw.TTSBackendSDKUnsupportedError):
                flw.resolve_tts_call_and_prompt(
                    "text", "style", "gemini-2.5-pro-preview-tts", "Aoede", "out.wav",
                    tts_backend="speech_metadata_flash_lite")

    def test_make_speech_metadata_call_fn_fails_closed_on_old_sdk(self):
        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 11, 0)):
            with self.assertRaises(flw.TTSBackendSDKUnsupportedError):
                flw.make_speech_metadata_call_fn(
                    fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede")


class ResolveActualModelNameTests(unittest.TestCase):
    def test_structured_separation_keeps_legacy_model(self):
        self.assertEqual(
            flw.resolve_actual_model_name("gemini-2.5-pro-preview-tts", "structured_separation"),
            "gemini-2.5-pro-preview-tts")

    def test_flash_lite_backend_returns_flash_lite_model(self):
        self.assertEqual(
            flw.resolve_actual_model_name("gemini-2.5-pro-preview-tts", "speech_metadata_flash_lite"),
            fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)


class ModelRoutingContractIntegrationTests(unittest.TestCase):
    """設計書§(g): FAMILY_X_FLASH_LITE_TTS processがrouting contractへ
    登録済みで、require_modelがfail-closedに機能することを確認する
    (SDKチェックは通す前提で、routing contract側の検証のみを対象にする)。"""

    def test_process_registered_in_map(self):
        self.assertEqual(
            routing_contract.PROCESS_MODEL_MAP["FAMILY_X_FLASH_LITE_TTS"],
            "gemini-3.8-flash-lite-tts")

    def test_require_model_rejects_wrong_model_id(self):
        with self.assertRaises(routing_contract.ModelContractViolation):
            routing_contract.require_model("FAMILY_X_FLASH_LITE_TTS", "gemini-2.5-pro-preview-tts")

    def test_make_speech_metadata_call_fn_rejects_wrong_model_id_via_contract(self):
        # SDKチェックはpatchで通し、routing contract側のfail-closedのみを検証する。
        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 25, 0)):
            with self.assertRaises(routing_contract.ModelContractViolation):
                flw.make_speech_metadata_call_fn("gemini-2.5-pro-preview-tts", "Aoede")


def _make_wav_bytes(samples_int16: "np.ndarray", framerate: int, channels: int = 1) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(framerate)
        w.writeframes(samples_int16.tobytes())
    return buf.getvalue()


class WavPcmDefenseTests(unittest.TestCase):
    """設計書§(a-2)/委任文「WAV/PCM防御」: Gemini 3.8系のWAVヘッダ付き
    音声(Trial実測: 24000Hz/mono/16bit)を正しく生PCMへ変換すること、
    ヘッダ無し(生PCM)の場合はそのまま扱うことを確認する。"""

    def test_wav_header_24000hz_mono_decodes_to_matching_sample_count(self):
        samples = np.array([0, 1000, -1000, 32000, -32000], dtype=np.int16)
        raw = _make_wav_bytes(samples, 24000, channels=1)
        decoded, framerate = flw._decode_audio_defensive(raw)
        self.assertEqual(framerate, 24000)
        self.assertEqual(len(decoded), len(samples))

    def test_no_wav_header_treated_as_raw_pcm_at_common_rate(self):
        import er002_common as common
        samples = np.array([0, 500, -500], dtype=np.int16)
        raw = samples.tobytes()  # RIFFヘッダ無し
        decoded, framerate = flw._decode_audio_defensive(raw)
        self.assertEqual(framerate, common.SAMPLE_RATE)
        self.assertEqual(len(decoded), len(samples))

    def test_resample_noop_when_rate_matches_common_rate(self):
        import er002_common as common
        samples = np.array([0.1, 0.2, -0.1], dtype=np.float64)
        result = flw._resample_to_common_rate(samples, common.SAMPLE_RATE)
        self.assertTrue(np.array_equal(result, samples))

    def test_resample_changes_length_when_rate_differs(self):
        import er002_common as common
        samples = np.zeros(48000, dtype=np.float64)  # 48kHz、1秒分
        result = flw._resample_to_common_rate(samples, 48000)
        # 24000Hzへ変換されるため、概ね半分の長さになる(rational resampling)。
        self.assertNotEqual(len(result), len(samples))
        self.assertAlmostEqual(len(result) / common.SAMPLE_RATE, len(samples) / 48000, delta=0.01)

    def test_float_to_pcm16_bytes_round_trips_without_clipping(self):
        samples = np.array([0.0, 0.5, -0.5, 0.999], dtype=np.float64)
        raw = flw._float_to_pcm16_bytes(samples)
        roundtrip = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        self.assertTrue(np.allclose(roundtrip, samples, atol=1e-3))

    def test_float_to_pcm16_bytes_normalizes_peak_over_one(self):
        # 想定外にpeak>1.0のsamplesが来ても、write_wav_float側のassertを
        # 壊さないよう正規化してからint16化する(防御的実装の確認)。
        samples = np.array([2.0, -2.0, 1.0], dtype=np.float64)
        raw = flw._float_to_pcm16_bytes(samples)
        roundtrip = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
        self.assertTrue(np.max(np.abs(roundtrip)) <= 1.0 + 1e-6)


class _FakePart:
    """google.genai.types.Partの軽量代替(pydantic strict schemaに依存
    しない)。Production `.venv`(2.11.0)にはtypes.SpeechMetadataが未実装
    (2.25.0導入待ち、設計書§(f))のため、実型ではなくこのFakeで検証する
    (SDKバージョンに関係なく本モジュール自身の配線ロジックだけを見る)。"""

    def __init__(self, text=None, speech_metadata=None):
        self.text = text
        self.speech_metadata = speech_metadata


class _FakeSpeechMetadata:
    def __init__(self, style=None):
        self.style = style


class _FakeContent:
    def __init__(self, parts=None, role=None):
        self.parts = parts
        self.role = role


class _FakeSpeechConfig:
    def __init__(self, voice_config=None):
        self.voice_config = voice_config


class _FakeVoiceConfig:
    def __init__(self, prebuilt_voice_config=None):
        self.prebuilt_voice_config = prebuilt_voice_config


class _FakePrebuiltVoiceConfig:
    def __init__(self, voice_name=None):
        self.voice_name = voice_name


class _FakeGenerateContentConfig:
    def __init__(self, response_modalities=None, speech_config=None):
        self.response_modalities = response_modalities
        self.speech_config = speech_config


def _patch_genai_types():
    """google.genai.typesの該当クラスをFakeへ差し替える(installed SDK
    versionのpydantic schemaに依存しないため、mock.patch.objectで
    create=Trueにし、SpeechMetadataがまだ存在しないSDKでもpatch可能に
    する)。"""
    import google.genai.types as real_types
    return mock.patch.multiple(
        real_types,
        Part=_FakePart, Content=_FakeContent, SpeechMetadata=_FakeSpeechMetadata,
        GenerateContentConfig=_FakeGenerateContentConfig, SpeechConfig=_FakeSpeechConfig,
        VoiceConfig=_FakeVoiceConfig, PrebuiltVoiceConfig=_FakePrebuiltVoiceConfig,
        create=True)


class MakeSpeechMetadataCallFnShapeTests(unittest.TestCase):
    """speech_metadata backendのcall_fnがtuple payload(text, style)を
    受け取る形状であることをFake client+Fake typesで確認する(実API呼び出し
    無し、installed SDK versionのpydantic schemaにも依存しない)。"""

    def test_call_fn_sends_speech_metadata_style_and_returns_pcm(self):
        samples = np.array([100, -100, 200], dtype=np.int16)
        wav_bytes = _make_wav_bytes(samples, 24000)
        captured = {}

        class FakeModels:
            def generate_content(self, model, contents, config):
                captured["model"] = model
                captured["contents"] = contents
                part = mock.Mock(inline_data=mock.Mock(data=wav_bytes))
                return mock.Mock(candidates=[mock.Mock(content=mock.Mock(parts=[part]))])

        class FakeClient:
            def __init__(self):
                self.models = FakeModels()

        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 25, 0)), _patch_genai_types():
            call_fn = flw.make_speech_metadata_call_fn(
                fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede", client=FakeClient())
            pcm = call_fn(("Hello.", "calm, conversational"))

        self.assertEqual(captured["model"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)
        content = captured["contents"]
        self.assertEqual(len(content.parts), 1)
        self.assertEqual(content.parts[0].text, "Hello.")
        self.assertEqual(content.parts[0].speech_metadata.style, "calm, conversational")
        roundtrip = np.frombuffer(pcm, dtype=np.int16)
        self.assertEqual(len(roundtrip), len(samples))

    def test_call_fn_omits_speech_metadata_when_style_empty(self):
        samples = np.array([10, 20], dtype=np.int16)
        wav_bytes = _make_wav_bytes(samples, 24000)
        captured = {}

        class FakeModels:
            def generate_content(self, model, contents, config):
                captured["contents"] = contents
                part = mock.Mock(inline_data=mock.Mock(data=wav_bytes))
                return mock.Mock(candidates=[mock.Mock(content=mock.Mock(parts=[part]))])

        class FakeClient:
            def __init__(self):
                self.models = FakeModels()

        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 25, 0)), _patch_genai_types():
            call_fn = flw.make_speech_metadata_call_fn(
                fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede", client=FakeClient())
            call_fn(("Hello.", ""))

        content = captured["contents"]
        self.assertIsNone(content.parts[0].speech_metadata)

    def test_call_fn_raises_on_empty_audio_parts(self):
        class FakeModels:
            def generate_content(self, model, contents, config):
                return mock.Mock(candidates=[mock.Mock(content=mock.Mock(parts=[]))])

        class FakeClient:
            def __init__(self):
                self.models = FakeModels()

        with mock.patch.object(flw, "_parse_genai_version", return_value=(2, 25, 0)), _patch_genai_types():
            call_fn = flw.make_speech_metadata_call_fn(
                fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede", client=FakeClient())
            with self.assertRaises(RuntimeError):
                call_fn(("Hello.", "calm"))


class RealSDKSpeechMetadataIntegrationTests(unittest.TestCase):
    """TTS-GEMINI-3.8-FLASH-LITE-PRODUCTION-WIRING-FAMILY-X-01 Phase 2
    (2026-09-28): Production `.venv`へgoogle-genai 2.25.0を導入した後、
    Fake(_patch_genai_types、上記MakeSpeechMetadataCallFnShapeTests)ではなく
    実SDK型(google.genai.types.Part/Content/SpeechMetadata等)を一切
    patchせずそのまま使って同じ検証を行う(委任文「実SDK型に置き換え
    (またはSDKが提供する場合は実型を優先し、fakeはフォールバックに)」)。
    google-genai<2.25.0の環境(例: 一部の`.venv-ci`)ではtypes.SpeechMetadata
    が無くこのテストクラス自体が意味を持たないため、収集時に存在確認して
    無ければskip理由付きでスキップする(fail-closedガード自体は
    SDKFailClosedGuardTestsが別途担保)。"""

    @classmethod
    def setUpClass(cls):
        try:
            from google.genai import types as real_types
        except Exception as e:  # pragma: no cover
            raise unittest.SkipTest(f"google.genai import失敗: {e}")
        if not hasattr(real_types, "SpeechMetadata"):
            raise unittest.SkipTest(
                "installed google-genaiにtypes.SpeechMetadataが無い"
                "(2.25.0未満の環境、例: 一部の.venv-ci。Fakeベースの"
                "MakeSpeechMetadataCallFnShapeTestsが同等の配線検証を担保する)。")
        cls.real_types = real_types

    def test_real_speech_metadata_style_roundtrip(self):
        sm = self.real_types.SpeechMetadata(style="calm, conversational")
        self.assertEqual(sm.style, "calm, conversational")

    def test_call_fn_sends_real_speech_metadata_and_returns_pcm(self):
        samples = np.array([100, -100, 200], dtype=np.int16)
        wav_bytes = _make_wav_bytes(samples, 24000)
        captured = {}

        class FakeModels:
            def generate_content(self, model, contents, config):
                captured["model"] = model
                captured["contents"] = contents
                captured["config"] = config
                part = mock.Mock(inline_data=mock.Mock(data=wav_bytes))
                return mock.Mock(candidates=[mock.Mock(content=mock.Mock(parts=[part]))])

        class FakeClient:
            def __init__(self):
                self.models = FakeModels()

        # 実SDK型は一切patchしない(installed 2.25.0をそのまま使う)。
        # FakeClientのみ差し込み、実API呼び出し(ネットワーク)は発生しない。
        call_fn = flw.make_speech_metadata_call_fn(
            fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede", client=FakeClient())
        pcm = call_fn(("Hello.", "calm, conversational"))

        self.assertEqual(captured["model"], fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME)
        content = captured["contents"]
        self.assertIsInstance(content, self.real_types.Content)
        self.assertEqual(len(content.parts), 1)
        self.assertIsInstance(content.parts[0], self.real_types.Part)
        self.assertEqual(content.parts[0].text, "Hello.")
        self.assertIsInstance(content.parts[0].speech_metadata, self.real_types.SpeechMetadata)
        self.assertEqual(content.parts[0].speech_metadata.style, "calm, conversational")
        roundtrip = np.frombuffer(pcm, dtype=np.int16)
        self.assertEqual(len(roundtrip), len(samples))

    def test_call_fn_omits_speech_metadata_when_style_empty_real_types(self):
        samples = np.array([10, 20], dtype=np.int16)
        wav_bytes = _make_wav_bytes(samples, 24000)
        captured = {}

        class FakeModels:
            def generate_content(self, model, contents, config):
                captured["contents"] = contents
                part = mock.Mock(inline_data=mock.Mock(data=wav_bytes))
                return mock.Mock(candidates=[mock.Mock(content=mock.Mock(parts=[part]))])

        class FakeClient:
            def __init__(self):
                self.models = FakeModels()

        call_fn = flw.make_speech_metadata_call_fn(
            fl_styles.FAMILY_X_FLASH_LITE_MODEL_NAME, "Aoede", client=FakeClient())
        call_fn(("Hello.", ""))

        content = captured["contents"]
        self.assertIsNone(content.parts[0].speech_metadata)


def run():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for cls in (
        DefaultBackendByteIdenticalTests, SDKFailClosedGuardTests, ResolveActualModelNameTests,
        ModelRoutingContractIntegrationTests, WavPcmDefenseTests, MakeSpeechMetadataCallFnShapeTests,
        RealSDKSpeechMetadataIntegrationTests,
    ):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    run()
