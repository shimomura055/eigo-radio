# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: Family Z narrator N01配線のmock test(課金0・生成なし、TEST_PLAN_01 Z-1m/Z-2m、Opus必須7)。
Family Zの記事再生成・音声化はSTOP中のため、実TTS/ASRは一切呼ばない(generatorsは差替え)。
実行: .venv/Scripts/python.exe -m unittest er063_family_z_audio_01_n01_test_01 -v"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import tempfile
import unittest

import er019_family_x_style_profile_01 as xprof
import er063_family_z_audio_01 as z
from er063_family_z_audio_01_test_01 import fake_generators, make_plan, _write_tone

N01_SHA = "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477"
PD8_SHA = "329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226"
PD8_A2SLOW_SHA = "74b456cacf74af0ad08636776dc32fc35e041f869ecc7d60ecab190cf99a1f91"


def _sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


class ZStyleTableN01Test(unittest.TestCase):
    def test_n01_constant_equals_family_x_n01_and_pinned_sha(self):
        self.assertEqual(z._N01, xprof.N01_TEXT)
        self.assertEqual(hashlib.sha256(z._N01.encode("utf-8")).hexdigest(), N01_SHA)
        rep = z.assert_style_table_integrity()
        self.assertEqual(rep["N01"], N01_SHA)

    def test_narrator_roles_are_n01_verbatim_std_and_adv(self):
        for role in ("NARRATOR_FULL_STORY_ADV", "NARRATOR_FULL_STORY_STD"):
            spec = z.FAMILY_Z_ROLE_STYLE[role]
            self.assertEqual(spec["style_label"], "N01")
            self.assertEqual(spec["text"], z._N01)
            self.assertEqual(z.role_style_sha256(role), N01_SHA)
        self.assertNotIn("Speak at a slightly slower", z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"])

    def test_old_pd8_constants_kept_but_not_used_by_any_role(self):
        self.assertEqual(z._STYLE_SHA256["PD8"], PD8_SHA)
        self.assertEqual(z._STYLE_SHA256["PD8_A2SLOW"], PD8_A2SLOW_SHA)
        for role, spec in z.FAMILY_Z_ROLE_STYLE.items():
            self.assertNotIn(spec["style_label"], ("PD8", "PD8+A2_SLOWDOWN_INSTRUCTION"), role)

    def test_style_text_for_each_kind(self):
        for level in ("a2", "b1b"):
            plan, _, _ = make_plan(level)
            for s in plan:
                st = z.style_text_for(s)
                if s.kind == "narrator":
                    self.assertEqual(st, z._N01, s.clip_id)
                elif s.kind == "dialogue":
                    self.assertTrue(st is None or z._N01 not in st, s.clip_id)  # Dialogue voicesはN01の対象外
                else:
                    self.assertTrue(st is None or z._N01 not in st, s.clip_id)

    def test_non_narrator_roles_unchanged(self):
        pins = {"STD_JA_PREVIEW": "R2", "STD_JA_COMMENT": "R2", "ADV_EN_PREVIEW": "E1", "ADV_EN_COMMENT": "E2_UPBEAT",
                "KP_EN": "K2", "KP_JA": "M2"}
        for role, label in pins.items():
            self.assertEqual(z.FAMILY_Z_ROLE_STYLE[role]["style_label"], label)
            self.assertEqual(z.role_style_sha256(role), z._STYLE_SHA256[label])
        for role in ("DIALOGUE_ADV", "DIALOGUE_STD", "SHELL"):
            self.assertIsNone(z.FAMILY_Z_ROLE_STYLE[role]["text"])

    def test_z_does_not_use_x_profile_mechanism(self):
        """Z-2m: Z narratorはtext定数経由。runner `--style-profile`/resolve_run_profileを参照しない。"""
        tree = ast.parse(open("er063_family_z_audio_01.py", encoding="utf-8").read())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            for n in names:
                self.assertNotIn("style_profile", n)
        src = open("er063_family_z_audio_01.py", encoding="utf-8").read()
        self.assertNotIn("resolve_run_profile", src)


class ZRunStyleLabelRecordTest(unittest.TestCase):
    """Opus必須7: run単位でnarrator style labelを記録し、不一致ならSTOP。新規Z runでなければN01にならない。"""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _legacy_results(self, level, label, sha):
        os.makedirs(f"{self.run}/{level}/audit", exist_ok=True)
        doc = {"segments": {"full_story_part1_c1": {
            "status": "OK", "clip_kind": "narrator", "role_style_key": "NARRATOR_FULL_STORY_STD" if level == "a2" else "NARRATOR_FULL_STORY_ADV",
            "style": {"instruction_label": label, "style_prefix_sha256": sha}}}, "key_phrases": {}}
        p = f"{self.run}/{level}/audit/tts_generation_results.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(doc, f)
        return p

    def test_new_run_gets_n01_record_and_resumes(self):
        for level in ("a2", "b1b"):
            plan, _, _ = make_plan(level)
            z.run_tts_stage(self.run, level, plan, generators=fake_generators())
            rec = json.load(open(f"{self.run}/{level}/{z.NARRATOR_STYLE_RECORD_RELPATH}", encoding="utf-8"))
            self.assertEqual(rec["style_label"], "N01")
            self.assertEqual(rec["style_prefix_sha256"], N01_SHA)
            # resume(同一run、記録一致)は通る
            z.run_tts_stage(self.run, level, plan, generators=fake_generators())
            results = json.load(open(f"{self.run}/{level}/audit/tts_generation_results.json", encoding="utf-8"))
            nar = [e for e in results["segments"].values() if e.get("clip_kind") == "narrator"]
            self.assertTrue(nar)
            for e in nar:
                self.assertEqual(e["style"]["instruction_label"], "N01")
                self.assertEqual(e["style"]["style_prefix_sha256"], N01_SHA)

    def test_existing_pd8_run_stops_before_any_generation(self):
        for level, sha in (("a2", PD8_A2SLOW_SHA), ("b1b", PD8_SHA)):
            p = self._legacy_results(level, "PD8", sha)
            before = _sha_file(p)
            plan, _, _ = make_plan(level)
            calls = []
            gens = {k: (lambda s, pth, k=k: calls.append(k)) for k in fake_generators()}
            with self.assertRaises(z.FamilyZNarratorStyleMismatchStop) as cm:
                z.run_tts_stage(self.run, level, plan, generators=gens)
            self.assertIn("PD8", str(cm.exception))
            self.assertEqual(calls, [], level)                                   # 生成(課金)に到達しない
            self.assertEqual(_sha_file(p), before, level)                        # 既存結果は変更しない
            self.assertFalse(os.path.exists(f"{self.run}/{level}/{z.NARRATOR_STYLE_RECORD_RELPATH}"))

    def test_record_mismatch_stops(self):
        os.makedirs(f"{self.run}/b1b/audit")
        with open(f"{self.run}/b1b/{z.NARRATOR_STYLE_RECORD_RELPATH}", "w", encoding="utf-8") as f:
            json.dump({"style_label": "PD8", "style_prefix_sha256": PD8_SHA}, f)
        plan, _, _ = make_plan("b1b")
        with self.assertRaises(z.FamilyZNarratorStyleMismatchStop):
            z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators())

    def test_dry_run_reports_without_raising_or_writing(self):
        p = self._legacy_results("b1b", "PD8", PD8_SHA)
        before = _sha_file(p)
        plan, _, _ = make_plan("b1b")
        out = z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators(), dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["narrator_style_record"]["status"], "LEGACY_NARRATOR_ENTRIES_MISMATCH")
        self.assertEqual(_sha_file(p), before)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/{z.NARRATOR_STYLE_RECORD_RELPATH}"))

    def test_dry_run_new_run_is_new_run_status(self):
        plan, _, _ = make_plan("a2")
        out = z.run_tts_stage(self.run, "a2", plan, generators=fake_generators(), dry_run=True)
        self.assertEqual(out["narrator_style_record"]["status"], "NEW_RUN")
        self.assertFalse(os.path.exists(self.run))

    def test_dialogue_only_cached_run_is_not_mismatch(self):
        os.makedirs(f"{self.run}/b1b/audit")
        doc = {"segments": {"full_story_part1_c2": {"status": "OK", "clip_kind": "dialogue", "role_style_key": "DIALOGUE_ADV",
                                                     "style": {"instruction_label": "existing_dialogue_style(ENGLISH_STYLE_PREFIX)",
                                                               "style_prefix_sha256": None}}}, "key_phrases": {}}
        json.dump(doc, open(f"{self.run}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8"))
        info = z.inspect_run_narrator_style(f"{self.run}/b1b", "b1b", doc)
        self.assertEqual(info["status"], "NEW_RUN")


if __name__ == "__main__":
    unittest.main()
