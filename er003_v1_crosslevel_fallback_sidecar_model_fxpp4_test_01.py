# FAMILY-X-PAYCHECK-PERSONALITY-PRODUCTION-E2E-01 委任_04: fallback sidecarの
# model/tts_backend記録是正のtest(無課金)。既定backendは従来とバイト同一。
import json
import unittest

import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as clac
import er033_tts_flash_lite_backend_wiring_01 as flw


class FallbackSidecarModelFieldsTests(unittest.TestCase):
    def test_default_backend_byte_identical_to_legacy(self):
        legacy = {"model": p9a.ENGLISH_MODEL_NAME, "voice": p9a.VOICE_NAME}
        new = {**clac._fallback_sidecar_model_fields("structured_separation"), "voice": p9a.VOICE_NAME}
        self.assertEqual(json.dumps(legacy, ensure_ascii=False), json.dumps(new, ensure_ascii=False))
        self.assertNotIn("tts_backend", clac._fallback_sidecar_model_fields(flw.DEFAULT_TTS_BACKEND))

    def test_flash_lite_backend_records_actual_model_and_backend(self):
        f = clac._fallback_sidecar_model_fields(flw.BACKEND_SPEECH_METADATA_FLASH_LITE)
        self.assertEqual(f["model"], "gemini-3.8-flash-lite-tts")
        self.assertNotEqual(f["model"], p9a.ENGLISH_MODEL_NAME)
        self.assertEqual(f["tts_backend"], "speech_metadata_flash_lite")


if __name__ == "__main__":
    unittest.main()
