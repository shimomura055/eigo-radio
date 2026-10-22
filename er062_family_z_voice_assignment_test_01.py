# -*- coding: utf-8 -*-
"""FAMILY-Z-VOICE-PRODUCTION-WIRING-01 委任_01: Family Z 登場人物Voice 正式表・決定的割当規則のtest(課金0)。"""
import json
import os
import tempfile
import unittest

import er062_family_z_structure_01 as st
import er026_family_z_fiction_production_runner_01 as r26

MALE = ["Algieba", "Schedar", "Fenrir", "Orus", "Puck"]
FEMALE = ["Zephyr", "Kore", "Leda", "Sulafat", "Erinome"]


def _roster(genders):
    return [{"speaker": f"s{i}", "gender": g, "order": i + 1} for i, g in enumerate(genders)]


class AssignmentRuleTest(unittest.TestCase):
    def test_pool_is_user_decision(self):
        self.assertEqual(list(st.FAMILY_Z_DIALOGUE_VOICE_POOL["male"]), MALE)
        self.assertEqual(list(st.FAMILY_Z_DIALOGUE_VOICE_POOL["female"]), FEMALE)

    def test_rank_order_and_cycle_independent_by_gender(self):
        r = _roster(["male"] * 7 + ["female"] * 7)
        out = st.assign_dialogue_voices(r)
        self.assertEqual([out[f"s{i}"] for i in range(7)], MALE + MALE[:2])
        self.assertEqual([out[f"s{i}"] for i in range(7, 14)], FEMALE + FEMALE[:2])

    def test_order_not_list_position(self):
        r = [{"speaker": "b", "gender": "female", "order": 2}, {"speaker": "a", "gender": "female", "order": 1}]
        out = st.assign_dialogue_voices(r)
        self.assertEqual((out["a"], out["b"]), ("Zephyr", "Kore"))

    def test_mixed_gender_independent_ranks(self):
        out = st.assign_dialogue_voices(_roster(["male", "female", "female", "male"]))
        self.assertEqual((out["s0"], out["s3"]), ("Algieba", "Schedar"))
        self.assertEqual((out["s1"], out["s2"]), ("Zephyr", "Kore"))

    def test_narrator_and_charon_never_in_pool(self):
        allv = set(MALE + FEMALE)
        self.assertNotIn(st.FAMILY_Z_NARRATOR_VOICE, allv)
        self.assertNotIn(st.FAMILY_Z_ADVANCED_AUX_VOICE, allv)
        out = st.assign_dialogue_voices(_roster(["male"] * 12 + ["female"] * 12))
        self.assertFalse(set(out.values()) & {"Aoede", "Charon"})

    def test_deterministic(self):
        r = _roster(["male", "female"] * 4)
        self.assertEqual(st.assign_dialogue_voices(r), st.assign_dialogue_voices(list(reversed(r))))
        for k in st.STORY_VOICE_ROSTER:
            self.assertEqual(st.derive_voice_assignment(k), st.derive_voice_assignment(k))

    def test_gender_must_be_explicit(self):
        with self.assertRaises(ValueError):
            st.assign_dialogue_voices([{"speaker": "x", "gender": None, "order": 1}])
        with self.assertRaises(ValueError):
            st.assign_dialogue_voices([{"speaker": "x", "gender": "male", "order": 1}, {"speaker": "y", "gender": "male", "order": 1}])


class OpenWindowTest(unittest.TestCase):
    def test_expected_assignment(self):
        n = st.STORY_SPEAKER_CONFIG["the_open_window"]["dialogue_voice_tts_names"]
        self.assertEqual(n, {"narrator": "Aoede", "vera": "Zephyr", "framton": "Algieba", "mrs_sappleton": "Kore", "men": "Schedar"})
        self.assertNotIn(None, n.values())
        self.assertNotIn("Charon", n.values())
        a = st.derive_voice_assignment("the_open_window")
        self.assertFalse(any(row["pinned"] for row in a["speakers"]))
        self.assertTrue(all(row["voice"] == row["rule_voice"] for row in a["speakers"]))

    def test_roster_covers_speakers(self):
        c = st.STORY_SPEAKER_CONFIG["the_open_window"]
        sp = {r["speaker"] for r in st.STORY_VOICE_ROSTER["the_open_window"]}
        self.assertEqual(sp, set(c["speakers"]) - {"other", "narrator"})
        self.assertEqual(sp, set(c["dialogue_voice_tts_names"]) - {"narrator"})

    def test_plan_matches_config(self):
        self.assertEqual(r26.STORY_REGISTRY["the_open_window"]["voice_tts_names_plan"],
                         st.STORY_SPEAKER_CONFIG["the_open_window"]["dialogue_voice_tts_names"])


class MelosPinTest(unittest.TestCase):
    def test_melos_voices_pinned_to_accepted_values(self):
        self.assertEqual(st.STORY_SPEAKER_CONFIG["melos"]["dialogue_voice_tts_names"],
                         {"narrator": "Aoede", "melos": "Algieba", "selinuntius": "Erinome", "dionysius": "Charon"})

    def test_melos_rule_values_recorded_but_not_applied(self):
        rows = {r["speaker"]: r for r in st.derive_voice_assignment("melos")["speakers"]}
        self.assertEqual(rows["melos"]["rule_voice"], "Algieba")
        self.assertEqual(rows["dionysius"]["rule_voice"], "Schedar")
        self.assertEqual(rows["selinuntius"]["rule_voice"], "Fenrir")
        self.assertTrue(all(r["pinned"] for r in rows.values()))
        self.assertTrue(st.STORY_VOICE_PIN_REASON["melos"])


class VoiceAssignmentFileTest(unittest.TestCase):
    def test_written_and_idempotent_and_stale_moved(self):
        with tempfile.TemporaryDirectory() as d:
            rec = r26.write_voice_assignment(d, "the_open_window")
            p = os.path.join(d, "voice_assignment.json")
            self.assertEqual(json.load(open(p, encoding="utf-8")), rec)
            r26.write_voice_assignment(d, "the_open_window")           # 再計算=同一: 退避なし
            self.assertEqual([f for f in os.listdir(d) if "STALE" in f], [])
            old = dict(rec); old["speakers"] = [dict(x) for x in rec["speakers"]]; old["speakers"][0]["voice"] = "Erinome"
            json.dump(old, open(p, "w", encoding="utf-8"))
            r26.write_voice_assignment(d, "the_open_window")           # 差分: 旧を退避(削除しない)
            self.assertEqual(len([f for f in os.listdir(d) if "STALE" in f]), 1)
            self.assertEqual(json.load(open(p, encoding="utf-8")), rec)


class StoreKeyTest(unittest.TestCase):
    def test_store_key_includes_voice(self):
        import er006_master_audio_store_01 as ms
        self.assertIn("speaker_voice", ms.EQUALITY_FIELDS)


if __name__ == "__main__":
    unittest.main()
