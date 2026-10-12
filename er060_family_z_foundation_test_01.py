"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_03 先行実装のtest(課金0、API呼出なし)。

対象: (a)routing key追加(M7)、(b)er020 resolve_narrative_role の `full_story_part[1-3]_c[0-9]+`
後方互換追加(M6/推奨)、(c)Production seed置き場へのsha付き複製。"""
import hashlib
import json
import unittest

import er006_model_routing_contract_01 as routing
import er020_tts_retry_local_rewrite_01 as er020

SEED_DIR = "er026_output/family_z_production_e2e_01/melos/seed"
TRIAL_DIR = ("er018_output/fiction_external_seed_selection_criteria_trial_02/"
             "stories/03_japanese_lit_2")


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class FamilyZRoutingKeyTest(unittest.TestCase):
    EXPECTED = {
        "FAMILY_Z_WRITER_ADV_R0": "gpt-6.1-sol",
        "FAMILY_Z_WRITER_ADV_R1": "gpt-6.1-sol",
        "FAMILY_Z_WRITER_ADV_R2": "gpt-6.1-sol",
        "FAMILY_Z_STD_ADJUST": "gpt-6.1-sol",
        "FAMILY_Z_SEMANTIC_JUDGE": "gpt-6-luna",
        "FAMILY_Z_STORY_SPLIT": "gpt-6-luna",
        "FAMILY_Z_DIALOGUE_ATTRIBUTION": "gpt-6-luna",
    }

    def test_keys_and_values(self):
        for k, v in self.EXPECTED.items():
            self.assertEqual(routing.PROCESS_MODEL_MAP.get(k), v, k)

    def test_judge_split_attribution_keys_are_separate(self):
        # M7: 判定用keyと共用しない(キー自体が別であること)
        ks = ["FAMILY_Z_SEMANTIC_JUDGE", "FAMILY_Z_STORY_SPLIT", "FAMILY_Z_DIALOGUE_ATTRIBUTION"]
        self.assertEqual(len(set(ks)), 3)
        for k in ks:
            self.assertIn(k, routing.PROCESS_MODEL_MAP)

    def test_existing_family_x_and_trial_keys_unchanged(self):
        m = routing.PROCESS_MODEL_MAP
        self.assertEqual(m["FAMILY_X_STORYLINE_B3"], "gpt-6.1-sol")
        self.assertEqual(m["FAMILY_X_FACTLOCK_R0"], "gpt-6.1-sol")
        self.assertEqual(m["FAMILY_X_FACTLOCK_REVISE"], "gpt-6.1-sol")
        self.assertEqual(m["FAMILY_X_RF_LUNA"], "gpt-6-luna")
        self.assertEqual(m["FAMILY_Z_TRIAL_STORY_QUALITY_EVAL"], "gpt-6-luna")
        self.assertEqual(m["FAMILY_Z_TRIAL_RIGHTS_INTERPRET"], "gpt-6-luna")


class ResolveNarrativeRoleFamilyZTest(unittest.TestCase):
    EXISTING = {
        "full_story_part1": "FULL_STORY", "full_story_part2": "FULL_STORY",
        "full_story_part3": "FULL_STORY", "point_one": "FULL_STORY", "point_two": "FULL_STORY",
        "comment_1": "COMMENT", "comment_2": "COMMENT", "comment_3": "COMMENT",
        "comment_4": "COMMENT", "preview": "PREVIEW", "topic_intro": "TOPIC_INTRO",
        "in_one_line": "IN_ONE_LINE", "point_one_heading": "HEADING_READOUT",
        "point_two_heading": "HEADING_READOUT", "kp1_en": "KEY_PHRASE", "kp3_ja": "KEY_PHRASE",
    }

    def test_existing_ids_unchanged(self):
        for sid, role in self.EXISTING.items():
            self.assertEqual(er020.resolve_narrative_role(sid), role, sid)
        self.assertIsNone(er020.resolve_narrative_role(None))
        self.assertIsNone(er020.resolve_narrative_role("story_004"))

    def test_positive_clip_ids(self):
        for sid in ("full_story_part1_c1", "full_story_part2_c3", "full_story_part3_c12"):
            self.assertEqual(er020.resolve_narrative_role(sid), "FULL_STORY", sid)
            self.assertTrue(er020.connected_speech_enabled_for(sid), sid)

    def test_negative_ids(self):
        for sid in (
            "full_story_part4_c1", "full_story_part0_c1", "foo_c1", "full_story_c1",
            "full_story_part1_c", "full_story_part1_cx", "full_story_part1_c1_original",
            "full_story_part1_c1_heading", "full_story_part1_original", "full_story_part1_heading",
            "full_story_part1_c1x", "xfull_story_part1_c1", "full_story_part12_c1",
            "full_story_part1_c1\n", "full_story_part1_c١",  # Unicode数字も不可
            "full_story_part1_c1_c2", "",
        ):
            self.assertIsNone(er020.resolve_narrative_role(sid), repr(sid))
            self.assertFalse(er020.connected_speech_enabled_for(sid), repr(sid))

    def test_connected_speech_frozenset_not_extended(self):
        # frozenset自体は(未参照のため)変更しない。_cN付きIDは含めない。
        self.assertNotIn("full_story_part1_c1", er020.CONNECTED_SPEECH_SEGMENT_IDS)
        self.assertEqual(len(er020.CONNECTED_SPEECH_SEGMENT_IDS), 12)


class ProductionSeedCopyTest(unittest.TestCase):
    def test_sha_matches_provenance_and_trial_source(self):
        with open(f"{SEED_DIR}/SEED_PROVENANCE.json", encoding="utf-8") as f:
            prov = json.load(f)
        for name, info in prov["files"].items():
            self.assertEqual(_sha(f"{SEED_DIR}/{name}"), info["sha256"], name)
            # Trial成果物(編集しない)とも一致
            self.assertEqual(_sha(f"{TRIAL_DIR}/{name}"), info["sha256"], name)

    def test_seed_loadable_with_expected_fields(self):
        with open(f"{SEED_DIR}/seed.json", encoding="utf-8") as f:
            seed = json.load(f)
        self.assertIn("original_summary", seed)
        self.assertTrue(len(seed["seed_elements"]) > 0)


if __name__ == "__main__":
    unittest.main()
