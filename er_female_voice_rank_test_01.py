# -*- coding: utf-8 -*-
"""FY-FZ-FEMALE-VOICE-RANK-01(2026-10-29ユーザー正式決定 APPROVED_FOR_PRODUCTION、OPEN-606): Y/Z女性Voice候補順位 Leda/Erinome/Sulafat/Kore/Zephyr のtest(API 0・TTS 0)。
確認: 新順位(Y/Z)・男性不変・新規制作の既定割当・既存run(記録値)不変・resume/regen整合・Zの制作済み作品pin・level別記録(記事固有採用)。"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er062_family_z_structure_01 as z  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402

FEMALE = ("Leda", "Erinome", "Sulafat", "Kore", "Zephyr")
Y_MALE = ("Puck", "Schedar", "Fenrir", "Orus", "Iapetus")
Z_MALE = ("Algieba", "Schedar", "Fenrir", "Orus", "Puck")
OLD = {"voice_1": "Puck", "voice_2": "Zephyr", "voice_3": "Schedar"}


def _w(d, rec):
    with open(os.path.join(d, "voice_assignment.json"), "w", encoding="utf-8") as f:
        json.dump(rec, f)


class FemaleRank(unittest.TestCase):
    def test_pools(self):
        self.assertEqual(ys.Y_DIALOGUE_VOICE_POOL["female"], FEMALE)
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["female"], FEMALE)
        self.assertEqual(ys.Y_DIALOGUE_VOICE_POOL["male"], Y_MALE)        # 男性不変・Y/Z差異維持
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["male"], Z_MALE)

    def test_y_default_new_production(self):
        self.assertEqual(ys.FIXED_VOICE_SLOTS, {"voice_1": "Puck", "voice_2": "Leda", "voice_3": "Schedar"})
        self.assertTrue(ys.verify_voice_assignment()["match"])
        self.assertEqual(ys.resolve_voice_slots(None), ys.FIXED_VOICE_SLOTS)
        with tempfile.TemporaryDirectory() as d:   # 記録なしの新規run=新順位
            self.assertEqual(ya.segment_voice_map(d, "a2")["y_voice_2"], "Leda")
            rec = ys.voice_assignment_record(d)
            self.assertEqual(rec["y_fixed_slots"]["voice_2"], "Leda")

    def test_y_existing_run_record_not_reassigned(self):
        with tempfile.TemporaryDirectory() as d:
            old = {"z_rule_assignment": dict(OLD), "y_fixed_slots": dict(OLD), "match": True}
            _w(d, old)
            for lv in ("a2", "b1b", None):
                self.assertEqual(ya.segment_voice_map(d, lv)["y_voice_2"], "Zephyr")
                self.assertEqual(ya.segment_voice_map(d, lv)["y_voice_1"], "Puck")
            self.assertEqual(ys.voice_assignment_record(d), old)   # runner再起動(resume/regen)でも記録を上書きしない

    def test_y_level_specific_record_article_pin(self):
        """記事固有採用(Std=Leda / Adv=Zephyr維持)を記録で表現できる。共通順位変更とは別。"""
        with tempfile.TemporaryDirectory() as d:
            _w(d, {"y_fixed_slots": dict(OLD), "y_fixed_slots_by_level": {"a2": {**OLD, "voice_2": "Leda"}, "b1b": dict(OLD)}})
            self.assertEqual(ya.segment_voice_map(d, "a2")["y_voice_2"], "Leda")
            self.assertEqual(ya.segment_voice_map(d, "b1b")["y_voice_2"], "Zephyr")
            self.assertEqual(ya.segment_voice_map(d, "a2")["y_voice_3"], "Schedar")

    def test_y_level_dir_path_resolves_run_record(self):
        """audio moduleは level dir(<run>/b1b|a2)を渡して呼ぶ。記録(run dir)がlevel dir経由でも解決される(OPEN-606 level dir経路不具合の回帰)。"""
        with tempfile.TemporaryDirectory() as d:
            for lv in ("a2", "b1b"):
                os.makedirs(os.path.join(d, lv))
            for lv in ("a2", "b1b"):   # 記録なし新規run: 既定Leda、男性不変
                m = ya.segment_voice_map(os.path.join(d, lv), lv)
                self.assertEqual((m["y_voice_1"], m["y_voice_2"], m["y_voice_3"]), ("Puck", "Leda", "Schedar"))
            _w(d, {"y_fixed_slots": dict(OLD), "y_fixed_slots_by_level": {"a2": {**OLD, "voice_2": "Leda"}, "b1b": dict(OLD)}})
            self.assertEqual(ya.segment_voice_map(os.path.join(d, "b1b"), "b1b")["y_voice_2"], "Zephyr")
            self.assertEqual(ya.segment_voice_map(os.path.join(d, "a2"), "a2")["y_voice_2"], "Leda")
            self.assertEqual(ya.segment_voice_map(os.path.join(d, "b1b"), "b1b")["y_voice_1"], "Puck")
            cached = {"segments": {"y_voice_2": {"y_tts_voice_requested": "Zephyr"}}}
            self.assertIn("y_voice_2", ya.voice_guard_cached(cached, os.path.join(d, "b1b"), "b1b")["segments"])

    def test_y_invalid_record_stops_and_male_slots_ignore_record(self):
        with tempfile.TemporaryDirectory() as d:
            _w(d, {"y_fixed_slots": {"voice_1": "Puck", "voice_2": "Nope", "voice_3": "Schedar"}})
            with self.assertRaises(ys.FamilyYStop):
                ya.segment_voice_map(d, "a2")
            # 旧記録(voice_1=Algieba)でも男性slotは現行既定(Puck)へ解決=男性は不変・女性だけ記録値(Zephyr)
            _w(d, {"y_fixed_slots": {"voice_1": "Algieba", "voice_2": "Zephyr", "voice_3": "Schedar"}})
            vm = ya.segment_voice_map(d, "a2")
            self.assertEqual((vm["y_voice_1"], vm["y_voice_2"], vm["y_voice_3"]), ("Puck", "Zephyr", "Schedar"))

    def test_y_voice_guard_cached(self):
        """resume: 既存run(Zephyr記録)のcachedは要求Voice一致で再利用、記録なし(新規既定Leda)ではZephyr entryを破棄=Voice混在なし。"""
        cached = {"segments": {"y_voice_2": {"y_tts_voice_requested": "Zephyr"}}}
        with tempfile.TemporaryDirectory() as d:
            _w(d, {"y_fixed_slots": dict(OLD)})
            out = ya.voice_guard_cached(json.loads(json.dumps(cached)), d, "a2")
            self.assertIn("y_voice_2", out["segments"])
        out2 = ya.voice_guard_cached(json.loads(json.dumps(cached)), None, "a2")
        self.assertNotIn("y_voice_2", out2["segments"])

    def test_z_new_story_gets_new_rank_and_males_unchanged(self):
        r = [{"speaker": f"f{i}", "gender": "female", "order": i + 1} for i in range(6)] + [{"speaker": f"m{i}", "gender": "male", "order": i + 101} for i in range(5)]
        out = z.assign_dialogue_voices(r)
        self.assertEqual([out[f"f{i}"] for i in range(6)], list(FEMALE) + ["Leda"])
        self.assertEqual([out[f"m{i}"] for i in range(5)], list(Z_MALE))

    def test_z_existing_stories_female_pinned_to_prior_voices(self):
        exp = {"the_open_window": {"vera": "Zephyr", "mrs_sappleton": "Kore"}, "the_gift_of_the_magi": {"della": "Zephyr", "madame": "Kore"},
               "the_monkeys_paw": {"mrs_white": "Zephyr"}, "in_a_grove": {"old_woman": "Zephyr", "masago": "Kore"}}
        for story, females in exp.items():
            names = z.derive_dialogue_voice_tts_names(story)
            for sp, v in females.items():
                self.assertEqual(names[sp], v, (story, sp))
            rec = z.derive_voice_assignment(story)
            self.assertTrue(rec["pin_reason"])
            for row in rec["speakers"]:                     # 男性はrule値(旧と同一)
                if row["gender"] == "male":
                    self.assertFalse(row["pinned"], (story, row["speaker"]))
        self.assertEqual(z.derive_dialogue_voice_tts_names("in_a_grove")["woodcutter"], "Algieba")
        self.assertEqual(z.derive_dialogue_voice_tts_names("melos")["dionysius"], "Charon")

    def test_every_female_roster_speaker_in_registered_story_is_pinned(self):
        """新順位が適用されてよいのはpinの無い(=新規)作品のみ。現registryの女性話者は全員pin済み(制作済み作品の差替え防止)。"""
        for story, roster in z.STORY_VOICE_ROSTER.items():
            for r in roster:
                if r["gender"] == "female":
                    self.assertIn(r["speaker"], z.STORY_VOICE_PINS.get(story, {}), (story, r["speaker"]))


if __name__ == "__main__":
    unittest.main()
