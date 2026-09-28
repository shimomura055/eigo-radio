# ============================================================
# er047_tts_fixed_shell_number_three_five_retrial_01_test_01.py
# TTS-FIXED-SHELL-NUMBER-THREE-FIVE-RETRIAL-01(Trial)
# ============================================================
# 実API呼び出し無し。(1)style文言が採用済みOne/Two/Fourと完全一致
# (import元が同一定数であること)、(2)model/voiceが無変更、(3)takeごとに
# Master Audio Keyが別id(4 take独立生成の保証)、(4)style B/Cは別id、
# (5)Trial Storeの隔離・復元(Production Store非書込)、(6)対象phrase外を
# 指定した場合にValueError、(7)WPM数値指定なし(既存constより継承済みの
# はずだが本scriptでも再importしていることを確認)、(8)引数既定値。
from __future__ import annotations

import unittest

import er002_common as common
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er043_tts_fixed_shell_master_champion_trial_02 as champ2
import er047_tts_fixed_shell_number_three_five_retrial_01 as retrial


class StyleTextIdentityTest(unittest.TestCase):
    def test_style_b_matches_champ2_constant_verbatim(self):
        # num_two(採用candidate)が使ったB系統style文言と完全一致
        # (再定義・改変していないこと)。
        self.assertIs(retrial.STYLE_TEXT_BY_CANDIDATE["B"], champ2.STYLE_TEXT_GROUP3_B)

    def test_style_c_matches_champ2_constant_verbatim(self):
        # num_one/num_four(採用candidate)が使ったC系統style文言と完全一致。
        self.assertIs(retrial.STYLE_TEXT_BY_CANDIDATE["C"], champ2.STYLE_TEXT_GROUP3_C)

    def test_no_wpm_specification(self):
        for style in retrial.STYLE_TEXT_BY_CANDIDATE.values():
            common.assert_no_wpm_specification(style)  # 例外なければPASS


class TargetPhraseScopeTest(unittest.TestCase):
    def test_target_phrases_are_exactly_num_three_and_num_five(self):
        self.assertEqual(set(retrial.TARGET_PHRASE_NAMES), {"num_three", "num_five"})

    def test_target_phrases_are_a_subset_of_group3_num_set(self):
        self.assertTrue(set(retrial.TARGET_PHRASE_NAMES).issubset(set(champ2.GROUP3_NUM_SET)))


class AdoptedMappingDocumentationTest(unittest.TestCase):
    def test_adopted_style_system_mapping_matches_champion_trial_02_decision(self):
        # design docの列位置確定結果(num_one=C、num_two=B、num_four=C)を
        # コード上でも記録していること(参考表示用データの一致確認)。
        self.assertEqual(retrial.ADOPTED_STYLE_SYSTEM_BY_ADOPTED_PHRASE,
                          {"num_one": "C", "num_two": "B", "num_four": "C"})


class MasterAudioKeyTakeIndependenceTest(unittest.TestCase):
    def _key_for(self, name: str, candidate: str, take: int) -> store.MasterAudioKey:
        text = shared_narration.FIXED_ENGLISH_TEXTS[name]
        style_id = retrial.STYLE_INSTRUCTION_ID_BY_CANDIDATE[candidate]
        return store.MasterAudioKey(
            language="en", speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
            canonical_text=text, level=retrial._take_level(take),
            style_instruction_id=style_id, style_instruction_version=retrial.STYLE_INSTRUCTION_VERSION,
        )

    def test_four_takes_get_four_distinct_master_audio_ids(self):
        ids = {self._key_for("num_three", "B", take).master_audio_id() for take in range(1, 5)}
        self.assertEqual(len(ids), 4, "4takeとも別id(独立生成、誤cache reuse防止)")

    def test_style_b_and_c_get_distinct_master_audio_ids_for_same_take(self):
        key_b = self._key_for("num_three", "B", 1)
        key_c = self._key_for("num_three", "C", 1)
        self.assertNotEqual(key_b.master_audio_id(), key_c.master_audio_id())

    def test_num_three_and_num_five_get_distinct_master_audio_ids(self):
        key_three = self._key_for("num_three", "B", 1)
        key_five = self._key_for("num_five", "B", 1)
        self.assertNotEqual(key_three.master_audio_id(), key_five.master_audio_id())

    def test_take_key_matches_model_voice_of_adopted_candidates(self):
        key = self._key_for("num_three", "B", 1)
        self.assertEqual(key.tts_model_id, shared_narration.TTS_MODEL_FLASH_LITE)
        self.assertEqual(key.speaker_voice, "Charon")

    def test_take_key_uses_same_style_instruction_id_lineage_as_champ2(self):
        # style_instruction_idは採用candidateと同一の系統id文字列を使う
        # (出自を保つ、design doc §4)。
        self.assertEqual(retrial.STYLE_INSTRUCTION_ID_BY_CANDIDATE["B"], "trial_ch2_num_set_style_b")
        self.assertEqual(retrial.STYLE_INSTRUCTION_ID_BY_CANDIDATE["C"], "trial_ch2_num_set_style_c")


class TrialStoreIsolationTest(unittest.TestCase):
    def test_trial_master_audio_store_restores_production_paths_after_use(self):
        import er040_tts_fixed_shell_master_champion_trial_01 as champ1
        original = (store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH)
        with champ1.trial_master_audio_store("er047_output/tts_fixed_shell_number_three_five_retrial_01/master_store"):
            self.assertEqual(store.STORE_DIR,
                              "er047_output/tts_fixed_shell_number_three_five_retrial_01/master_store")
            self.assertNotEqual(store.STORE_DIR, "er006_output/master_audio_store_01")
        self.assertEqual((store.STORE_DIR, store.AUDIO_DIR, store.MANIFEST_PATH, store.TELEMETRY_PATH), original)

    def test_production_store_dir_constant_unchanged_reference(self):
        self.assertEqual(store.STORE_DIR, "er006_output/master_audio_store_01")


class EnsureTakeArgumentValidationTest(unittest.TestCase):
    def test_ensure_take_raises_on_unknown_phrase(self):
        with self.assertRaises(ValueError):
            retrial.ensure_take("not_a_real_phrase", "B", 1, "dummy_out")

    def test_ensure_take_raises_on_unknown_style(self):
        with self.assertRaises(ValueError):
            retrial.ensure_take("num_three", "Z", 1, "dummy_out")


class ArgParsingTest(unittest.TestCase):
    def test_default_phrases_are_num_three_and_num_five(self):
        parser = retrial.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "20"])
        phrases = [p.strip() for p in args.phrases.split(",") if p.strip()]
        self.assertEqual(set(phrases), {"num_three", "num_five"})

    def test_default_styles_are_b_and_c(self):
        parser = retrial.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "20"])
        styles = [c.strip().upper() for c in args.styles.split(",") if c.strip()]
        self.assertEqual(set(styles), {"B", "C"})

    def test_default_takes_is_four(self):
        parser = retrial.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "20"])
        self.assertEqual(args.takes, 4)

    def test_main_rejects_out_of_scope_phrase(self):
        import sys
        old_argv = sys.argv
        sys.argv = ["er047_tts_fixed_shell_number_three_five_retrial_01.py",
                    "--phrases", "num_one", "--out-dir", "dummy_out",
                    "--trial-store", "dummy_store", "--budget-jpy", "20"]
        try:
            with self.assertRaises(ValueError):
                retrial.main()
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    unittest.main()
