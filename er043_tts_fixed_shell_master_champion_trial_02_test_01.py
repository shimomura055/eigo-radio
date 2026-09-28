# ============================================================
# er043_tts_fixed_shell_master_champion_trial_02_test_01.py
# TTS-FIXED-SHELL-MASTER-CHAMPION-TRIAL-02(Trial)
# ============================================================
# 実API呼び出し無し。(1)Production Store未使用(path assert、champ1の
# 既存定数をそのまま使っていることの確認)、(2)phrase棚卸しの網羅、
# (3)Master Audio Keyがgroup/candidateごとに別idになること(誤reuse
# 防止)、(4)group1/group2でB/Cのstyle文言が同一でもversionが違うため
# 別id(cache hitではなく2回とも新規生成される設計になっていること)、
# (5)group3/group4はB/Cで異なるstyle文言を使うこと、(6)WPM数値指定が
# 含まれないこと、(7)候補・phraseの引数検証。
from __future__ import annotations

import unittest

import er002_common as common
import er006_audio_cost_pilot_02_shared_narration as shared_narration
import er006_master_audio_store_01 as store
import er040_tts_fixed_shell_master_champion_trial_01 as champ1
import er043_tts_fixed_shell_master_champion_trial_02 as champ2


class ProductionStoreReferenceTest(unittest.TestCase):
    def test_production_store_manifest_path_matches_champ1(self):
        # champ1(TRIAL-01)の既存定数をそのまま使っていること(独自の
        # 別定義によるpath誤り・別store混入を防ぐ)。
        self.assertEqual(champ2.PRODUCTION_STORE_MANIFEST_PATH, champ1.PRODUCTION_STORE_MANIFEST_PATH)
        self.assertEqual(champ2.PRODUCTION_STORE_MANIFEST_PATH, f"{store.STORE_DIR}/manifest.json")


class PhraseInventoryTest(unittest.TestCase):
    def test_all_phrase_names_matches_shared_narration_definitions(self):
        expected_en = set(shared_narration.FIXED_ENGLISH_TEXTS.keys())
        expected_ja = set(shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.keys())
        self.assertEqual(set(champ2.ALL_PHRASE_NAMES), expected_en | expected_ja)
        self.assertEqual(len(champ2.ALL_PHRASE_NAMES), 10)

    def test_groups_partition_all_phrases_without_overlap_or_gap(self):
        groups = [champ2.GROUP1_NO_COMPLAINT, champ2.GROUP2_FULL_STORY_INTRO,
                  champ2.GROUP3_NUM_SET, champ2.GROUP4_JA_POINT_EXPLANATION]
        flat = [name for g in groups for name in g]
        self.assertEqual(sorted(flat), sorted(champ2.ALL_PHRASE_NAMES))
        self.assertEqual(len(flat), len(set(flat)), "重複なし(各phraseは1グループのみに属する)")

    def test_num_four_is_included_in_group3_num_set(self):
        # design doc §2-1: delegation内表記の矛盾をユーザー原文優先で解消し、
        # num_fourも5個set styleの対象に含める実装判断とした。
        self.assertIn("num_four", champ2.GROUP3_NUM_SET)
        self.assertEqual(len(champ2.GROUP3_NUM_SET), 5)


class StyleTextTest(unittest.TestCase):
    def test_no_wpm_specification_in_any_style_text(self):
        for style in (champ2.STYLE_TEXT_GROUP1, champ2.STYLE_TEXT_GROUP2_PACE,
                      champ2.STYLE_TEXT_GROUP3_B, champ2.STYLE_TEXT_GROUP3_C,
                      champ2.STYLE_TEXT_GROUP4_B_JA, champ2.STYLE_TEXT_GROUP4_C_JA):
            common.assert_no_wpm_specification(style)  # 例外が出なければPASS

    def test_group3_b_and_c_style_texts_differ(self):
        self.assertNotEqual(champ2.STYLE_TEXT_GROUP3_B, champ2.STYLE_TEXT_GROUP3_C)

    def test_group3_style_texts_do_not_reuse_known_failure_wording(self):
        # TRIAL-01の既知失敗文言("brief, clear, neutral")をそのまま
        # 使っていないこと(OPEN-222)。
        known_failure_text = "brief, clear, neutral"
        self.assertNotEqual(champ2.STYLE_TEXT_GROUP3_B, known_failure_text)
        self.assertNotEqual(champ2.STYLE_TEXT_GROUP3_C, known_failure_text)

    def test_group4_ja_style_texts_differ(self):
        self.assertNotEqual(champ2.STYLE_TEXT_GROUP4_B_JA, champ2.STYLE_TEXT_GROUP4_C_JA)

    def test_group1_style_text_matches_current_production_fallback(self):
        # group1(指摘なし)は仕様(style文言)をProduction Aと同一のまま使う。
        import er033_tts_flash_lite_family_x_styles_01 as fl_styles
        self.assertEqual(champ2.STYLE_TEXT_GROUP1, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK[0])


class MasterAudioKeyDistinguishesGroupsAndCandidatesTest(unittest.TestCase):
    def _key_for(self, name: str, candidate: str) -> store.MasterAudioKey:
        style_text, style_id, style_version = champ2._style_for(name, candidate)
        text = shared_narration.FIXED_ENGLISH_TEXTS.get(name) or \
            shared_narration.FIXED_JAPANESE_TEXTS_A2_ONLY.get(name)
        language = "ja" if name == "point_explanation" else "en"
        return store.MasterAudioKey(
            language=language, speaker_voice="Charon", tts_model_id=shared_narration.TTS_MODEL_FLASH_LITE,
            canonical_text=text, level=None,
            style_instruction_id=style_id, style_instruction_version=style_version,
        )

    def test_group1_b_and_c_get_distinct_master_audio_ids_despite_same_style_text(self):
        # 同じstyle文言でも、versionが違うため別のmaster_audio_idになる
        # (B/Cが誤って同じ1回分のみの生成をcache reuseしないための設計)。
        key_b = self._key_for("welcome", "B")
        key_c = self._key_for("welcome", "C")
        self.assertNotEqual(key_b.master_audio_id(), key_c.master_audio_id())

    def test_group3_b_and_c_get_distinct_master_audio_ids(self):
        key_b = self._key_for("num_one", "B")
        key_c = self._key_for("num_one", "C")
        self.assertNotEqual(key_b.master_audio_id(), key_c.master_audio_id())

    def test_new_candidate_keys_differ_from_production_key(self):
        text = shared_narration.FIXED_ENGLISH_TEXTS["welcome"]
        production_key = shared_narration._make_english_key(text, tts_backend="speech_metadata_flash_lite")
        trial_key = self._key_for("welcome", "B")
        self.assertNotEqual(production_key.master_audio_id(), trial_key.master_audio_id())

    def test_num_one_through_five_share_same_key_scheme_within_candidate(self):
        # group3内では5 word全てに同一style_instruction_id/versionを使う
        # (setとしての統一性を狙う設計、design doc §2-6)。
        for candidate in ("B", "C"):
            ids = set()
            for name in champ2.GROUP3_NUM_SET:
                _, style_id, style_version = champ2._style_for(name, candidate)
                ids.add((style_id, style_version))
            self.assertEqual(len(ids), 1, f"candidate={candidate}: 5 word全てに同一style key")


class ArgParsingTest(unittest.TestCase):
    def test_default_candidates_are_a_b_c(self):
        parser = champ2.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "40"])
        candidates = [c.strip().upper() for c in args.candidates.split(",") if c.strip()]
        self.assertEqual(set(candidates), {"A", "B", "C"})

    def test_default_phrases_is_all(self):
        parser = champ2.build_arg_parser()
        args = parser.parse_args(["--out-dir", "dummy_out", "--trial-store", "dummy_store",
                                   "--budget-jpy", "40"])
        self.assertEqual(args.phrases, "all")


class GroupOfHelperTest(unittest.TestCase):
    def test_group_of_raises_on_unknown_name(self):
        with self.assertRaises(ValueError):
            champ2._group_of("not_a_real_phrase")

    def test_group_of_covers_all_known_phrases(self):
        for name in champ2.ALL_PHRASE_NAMES:
            self.assertIn(champ2._group_of(name),
                           {"group1_no_complaint", "group2_full_story_intro_pace",
                            "group3_num_set", "group4_ja_point_explanation"})


if __name__ == "__main__":
    unittest.main()
