# -*- coding: utf-8 -*-
"""FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01: Family Y Voice候補表(男性5/女性5)・Voice 1=Puck の配線test(API 0・TTS 0)。

ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-26): Y男性=Puck/Schedar/Fenrir/Orus/Iapetus、女性=Zephyr/Kore/Leda/Sulafat/Erinome、Algieba除外、Voice 1=Puck。
Family Zは変更しない(Z男性1=Algieba、Z男性5=Puck)。Y/Z候補差分はユーザーが明示許容した承認済みFamily固有仕様。
既存の完成音声(run_01 / 公開ページ)は差し替えない(今後の制作に適用)。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er121_family_y_voice_table_test_01.py -q
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er062_family_z_structure_01 as z  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402

APPROVED_Y = {
    "male": ("Puck", "Schedar", "Fenrir", "Orus", "Iapetus"),
    "female": ("Zephyr", "Kore", "Leda", "Sulafat", "Erinome"),
}
APPROVED_Z = {
    "male": ("Algieba", "Schedar", "Fenrir", "Orus", "Puck"),
    "female": ("Zephyr", "Kore", "Leda", "Sulafat", "Erinome"),
}
INTENT = "Y/Z候補差分(Y男性1=Puck・男性5=Iapetus / Z男性1=Algieba・男性5=Puck)はユーザーが2026-10-26に明示許容した承認済みFamily固有仕様。共通仕様統一を理由に変更しない"


class YVoiceTable(unittest.TestCase):
    def test_pool_exact_match_approved_table(self):
        self.assertEqual(ys.Y_DIALOGUE_VOICE_POOL, APPROVED_Y)
        self.assertEqual(len(ys.Y_DIALOGUE_VOICE_POOL["male"]), 5)
        self.assertEqual(len(ys.Y_DIALOGUE_VOICE_POOL["female"]), 5)

    def test_algieba_excluded_from_y(self):
        for g, names in ys.Y_DIALOGUE_VOICE_POOL.items():
            self.assertNotIn("Algieba", names, g)
        self.assertNotIn("Algieba", ys.FIXED_VOICE_SLOTS.values())

    def test_voice_1_is_puck_and_2_3_unchanged(self):
        self.assertEqual(ys.FIXED_VOICE_SLOTS, {"voice_1": "Puck", "voice_2": "Zephyr", "voice_3": "Schedar"})

    def test_fixed_slots_match_pool_rule(self):
        rec = ys.verify_voice_assignment()
        self.assertTrue(rec["match"])
        self.assertEqual(rec["y_fixed_slots"], {"voice_1": "Puck", "voice_2": "Zephyr", "voice_3": "Schedar"})

    def test_segment_voices(self):
        self.assertEqual(ys.voice_of_segment("y_voice_1", "Aoede"), "Puck")
        self.assertEqual(ys.voice_of_segment("y_voice_2", "Aoede"), "Zephyr")
        self.assertEqual(ys.voice_of_segment("y_voice_3", "Aoede"), "Schedar")
        self.assertEqual(ys.voice_of_segment("y_lead", "Aoede"), "Aoede")

    def test_z_table_unchanged_and_intentional_difference(self):
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL, APPROVED_Z, INTENT)
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["male"][0], "Algieba", INTENT)
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["male"][4], "Puck", INTENT)
        self.assertEqual(z.FAMILY_Z_NARRATOR_VOICE, "Aoede")
        self.assertNotEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["male"], ys.Y_DIALOGUE_VOICE_POOL["male"], INTENT)
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_POOL["female"], ys.Y_DIALOGUE_VOICE_POOL["female"], INTENT)

    def test_z_melos_pin_algieba_untouched(self):
        self.assertEqual(z.STORY_VOICE_PINS["melos"]["melos"], "Algieba", INTENT)

    def test_y_modules_do_not_hardcode_algieba_in_code(self):
        # 正式Y経路(er121_family_y_*.py。testを除く)のコード行にAlgiebaが残らない(コメント・履歴注記は可)
        for p in glob.glob(os.path.join(ROOT, "er121_family_y_*.py")):
            if p.endswith("_test_01.py"):
                continue
            for i, line in enumerate(open(p, encoding="utf-8").read().splitlines(), 1):
                code = line.split("#", 1)[0]
                self.assertNotIn("Algieba", code, f"{os.path.basename(p)}:{i}")

    def test_existing_run_01_and_public_pages_not_modified(self):
        """既存の完成音声・公開ページを無断で差し替えない: run_01 / 公開dirのtracked fileに変更・削除がない(git status。改行変換の影響を受けない)。"""
        try:
            out = subprocess.run(["git", "status", "--porcelain", "--", "er121_output/family_y_production_01/redelivery_fee/run_01",
                                  "er121_output/family_y_production_01/sns_age_limit/run_01", "user_test"],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.splitlines()
        except Exception as e:  # pragma: no cover
            self.skipTest(f"git unavailable: {e}")
        changed = [ln for ln in out if not ln.startswith("??")]
        self.assertEqual(changed, [], "既存run_01/公開ページのtracked fileが変更されています(今後の制作にのみ適用する)")
        self.assertTrue(subprocess.run(["git", "ls-files", "--error-unmatch", "er121_output/family_y_production_01/redelivery_fee/run_01/final_manifest.json"],
                                       cwd=ROOT, capture_output=True, timeout=30).returncode == 0)


if __name__ == "__main__":
    unittest.main()
