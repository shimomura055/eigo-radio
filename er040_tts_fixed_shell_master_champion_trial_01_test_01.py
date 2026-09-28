# ============================================================
# er040_tts_fixed_shell_master_champion_trial_01_test_01.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-01(Trial)
# ============================================================
# 実API呼び出し無し。(1)Production Store未使用(path assert)、
# (2)棚卸し一覧の網羅(Family X runnerの固定shared narration全種)、
# (3)Master Audio Keyがstyle_instruction_id/version違いで別idになる
# こと、(4)候補は既定でA/B/Cの3種類に限定されている(無限大量生成に
# ならない)ことを検証する。
from __future__ import annotations

import os
import tempfile
import unittest
import wave

import numpy as np

import er002_common as common
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er040_tts_fixed_shell_master_champion_trial_01 as champ
import er040_tts_fixed_shell_master_champion_trial_01_page_01 as page


class ProductionStoreUntouchedTest(unittest.TestCase):
    def test_trial_master_audio_store_restores_production_globals_on_exit(self):
        orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        self.assertEqual(orig[0], "er006_output/master_audio_store_01")
        with champ.trial_master_audio_store("er040_output/tts_fixed_shell_master_champion_trial_01/master_store"):
            self.assertEqual(
                store.STORE_DIR,
                "er040_output/tts_fixed_shell_master_champion_trial_01/master_store")
            self.assertNotEqual(store.STORE_DIR, orig[0])
        self.assertEqual(
            (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH), orig)

    def test_trial_master_audio_store_restores_even_on_exception(self):
        orig = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        with self.assertRaises(ValueError):
            with champ.trial_master_audio_store("er040_output/tts_fixed_shell_master_champion_trial_01/master_store"):
                raise ValueError("boom")
        self.assertEqual(
            (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH), orig)

    def test_production_store_manifest_path_constant_unchanged(self):
        # Trial scriptがProduction manifestを読み取り専用で参照する
        # 定数自体が、正式Production Store定義(er006_master_audio_
        # store_01.STORE_DIR)と一致していることを確認する(パス誤りに
        # よる別store混入を防ぐ)。
        self.assertEqual(
            champ.PRODUCTION_STORE_MANIFEST_PATH,
            f"{store.STORE_DIR}/manifest.json")
        self.assertEqual(
            champ.PRODUCTION_STORE_AUDIO_DIR,
            f"{store.STORE_DIR}/audio")

    def test_japanese_style_override_restores_original_prefix(self):
        import er003_v1_sing01_voice01_generate as voice01
        original = voice01.p9a.JAPANESE_STYLE_PREFIX
        with champ.trial_japanese_style_override("簡潔に、はっきりと"):
            self.assertEqual(voice01.p9a.JAPANESE_STYLE_PREFIX, "簡潔に、はっきりと")
        self.assertEqual(voice01.p9a.JAPANESE_STYLE_PREFIX, original)

    def test_japanese_style_override_restores_even_on_exception(self):
        import er003_v1_sing01_voice01_generate as voice01
        original = voice01.p9a.JAPANESE_STYLE_PREFIX
        with self.assertRaises(ValueError):
            with champ.trial_japanese_style_override("dummy"):
                raise ValueError("boom")
        self.assertEqual(voice01.p9a.JAPANESE_STYLE_PREFIX, original)


class InventoryCoverageTest(unittest.TestCase):
    def test_fixed_phrase_inventory_matches_shared_narration_definitions(self):
        expected_en = {
            "welcome", "preview_intro", "key_phrases_intro", "full_story_intro",
            "num_one", "num_two", "num_three", "num_four", "num_five",
        }
        expected_ja = {"point_explanation"}
        self.assertEqual(set(champ.FIXED_PHRASE_NAMES_EN), expected_en)
        self.assertEqual(set(champ.FIXED_PHRASE_NAMES_JA), expected_ja)
        # 棚卸し対象がshared_narration.pyの実定義と完全一致すること
        # (別モジュールで定義が増減しても本Trialが追従漏れしないことの保証)。
        self.assertEqual(set(champ.FIXED_PHRASE_NAMES_EN), set(shared_narration.FIXED_ENGLISH_TEXTS.keys()))
        self.assertEqual(set(champ.FIXED_PHRASE_NAMES_JA),
                          set(shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.keys()))

    def test_role_style_en_covers_all_phrases_except_known_failure_num_two_three(self):
        # num_two/num_threeはdesign doc §1-5により意図的に対象外。
        # それ以外の7 phraseは全てRole styleが定義されていること。
        covered = set(champ.ROLE_STYLE_EN.keys())
        expected = set(champ.FIXED_PHRASE_NAMES_EN) - {"num_two", "num_three"}
        self.assertEqual(covered, expected)

    def test_known_failure_map_covers_exactly_num_two_and_num_three(self):
        self.assertEqual(set(champ.KNOWN_FAILURE_CANDIDATE_B_NUM_TWO_THREE.keys()),
                          {"num_two", "num_three"})
        for name, info in champ.KNOWN_FAILURE_CANDIDATE_B_NUM_TWO_THREE.items():
            self.assertEqual(info["status"], "SKIPPED_KNOWN_FAILURE")
            self.assertIn("OPEN-222", info["open_item"])


class MasterAudioKeyDistinguishesStyleVersionsTest(unittest.TestCase):
    def test_master_audio_key_distinguishes_style_versions(self):
        text = shared_narration.FIXED_ENGLISH_TEXTS["welcome"]
        # (a) Production既定(v1、structured_separation)
        key_v1 = shared_narration._make_english_key(text, tts_backend="structured_separation")
        # (b) Production Flash-Lite Baseline(v2_flash_lite_short_style)
        key_v2 = shared_narration._make_english_key(text, tts_backend="speech_metadata_flash_lite")
        # (c) 本TrialのCandidate B(Role style、trial_ch1_role_style_v1)
        key_trial_b = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
            canonical_text=text, level=None,
            style_instruction_id=champ.CANDIDATE_B_STYLE_ID,
            style_instruction_version=champ.CANDIDATE_B_STYLE_VERSION,
        )
        ids = {key_v1.master_audio_id(), key_v2.master_audio_id(), key_trial_b.master_audio_id()}
        self.assertEqual(len(ids), 3, "3つのkeyが全て別のmaster_audio_idを持つべき(誤reuse防止)")

    def test_level_independence_preserved_for_trial_candidate_b(self):
        # level=Noneであることを明示的に確認する(B1/A2共有、level依存に
        # なっていないことの回帰確認)。
        text = shared_narration.FIXED_ENGLISH_TEXTS["num_one"]
        key = store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
            canonical_text=text, level=None,
            style_instruction_id=champ.CANDIDATE_B_STYLE_ID,
            style_instruction_version=champ.CANDIDATE_B_STYLE_VERSION,
        )
        self.assertIsNone(key.level)


class CandidateScopeTest(unittest.TestCase):
    def test_default_candidates_limited_to_a_b_c(self):
        parser = champ.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "40"])
        candidates = [c.strip().upper() for c in args.candidates.split(",") if c.strip()]
        self.assertEqual(set(candidates), {"A", "B", "C"})
        self.assertEqual(len(candidates), 3, "候補は2〜3程度が基本(無意味な大量生成禁止)")

    def test_no_wpm_specification_in_any_role_style(self):
        # 既存の安全網(N-7是正と同じ)をRole style文言全件へ適用する。
        import er002_common as common
        for style in champ.ROLE_STYLE_EN.values():
            common.assert_no_wpm_specification(style)  # 例外が出なければPASS
        common.assert_no_wpm_specification(champ.ROLE_STYLE_JA_POINT_EXPLANATION)


class PageGenerationHelpersTest(unittest.TestCase):
    def _write_tone_wav(self, path: str, seconds: float = 0.2, freq: float = 440.0) -> None:
        sr = 24000
        t = np.linspace(0, seconds, int(sr * seconds), endpoint=False)
        samples = 0.2 * np.sin(2 * np.pi * freq * t)
        common.write_wav_float(path, samples, sr, 1)

    def test_wav_to_mp3_roundtrip_produces_nonempty_file(self):
        with tempfile.TemporaryDirectory() as td:
            wav_path = os.path.join(td, "a.wav")
            mp3_path = os.path.join(td, "a.mp3")
            self._write_tone_wav(wav_path)
            ok = page.wav_to_mp3(wav_path, mp3_path)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(mp3_path))
            self.assertGreater(os.path.getsize(mp3_path), 0)

    def test_concat_wavs_skips_missing_files_without_error(self):
        with tempfile.TemporaryDirectory() as td:
            wav1 = os.path.join(td, "one.wav")
            missing = os.path.join(td, "does_not_exist.wav")
            wav2 = os.path.join(td, "two.wav")
            out = os.path.join(td, "joined.wav")
            self._write_tone_wav(wav1)
            self._write_tone_wav(wav2)
            ok = page.concat_wavs([wav1, missing, wav2], out)
            self.assertTrue(ok)
            with wave.open(out, "rb") as w:
                total_frames = w.getnframes()
            with wave.open(wav1, "rb") as w:
                single_frames = w.getnframes()
            self.assertEqual(total_frames, single_frames * 2, "欠落ファイルはスキップされ、2件分のみ連結される")

    def test_concat_wavs_returns_false_when_all_missing(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "joined.wav")
            ok = page.concat_wavs([os.path.join(td, "nope1.wav"), os.path.join(td, "nope2.wav")], out)
            self.assertFalse(ok)
            self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
