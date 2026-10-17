# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15: Family Z Narrator=PD06 配線と run単位Style記録のmock test(課金0・生成なし)。
旧 er063_family_z_audio_01_n01_test_01.py(FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02、Narrator=N01)を、ユーザー承認(2026-10-17 §2B:
Narrator=PD06)に合わせて改名・更新したもの(期待値の意図的更新: N01->PD06、narrator記録->全Role Style記録)。
実TTS/ASRは一切呼ばない(generatorsは差替え)。
実行: .venv/Scripts/python.exe -m unittest er063_family_z_audio_01_pd06_run_style_test_01 -v"""
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
from er063_family_z_audio_01_test_01 import fake_generators, make_plan

PD06_SHA = "3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d"
OLD_N01_SHA = "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477"
OLD_PD8_SHA = "329ff46a5ec3877f7dc23375e14ee8a806efeff7cfe27963492a3cf95d182226"


def _sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class ZStyleTablePd06Test(unittest.TestCase):
    def test_pd06_constant_is_x_reference_and_pinned_sha(self):
        self.assertIs(z._STYLE_TEXT["PD06"], xprof.PD06_TEXT)          # コピーでなく定数参照
        self.assertEqual(hashlib.sha256(z._STYLE_TEXT["PD06"].encode("utf-8")).hexdigest(), PD06_SHA)
        self.assertEqual(z.assert_style_table_integrity()["PD06"], PD06_SHA)

    def test_narrator_roles_are_pd06_verbatim_std_and_adv(self):
        for role in ("NARRATOR_FULL_STORY_ADV", "NARRATOR_FULL_STORY_STD"):
            spec = z.FAMILY_Z_ROLE_STYLE[role]
            self.assertEqual(spec["style_label"], "PD06")
            self.assertEqual(spec["text"], xprof.PD06_TEXT)
            self.assertEqual(z.role_style_sha256(role), PD06_SHA)
            self.assertEqual(spec["origin_kind"], "x_common_constant")
        self.assertNotIn("Speak at a slightly slower", z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"]["text"])

    def test_retired_style_constants_are_removed(self):
        """旧Style(N01/PD8/PD8_A2SLOW/R2/M2)の定数・shaは撤去済み(どのroleからも参照されない)。"""
        for name in ("_N01", "_PD8", "_R2", "_M2", "_E1", "_K2", "_A2_SLOW_INSTRUCTION", "_X_KP_EXPLANATION_EN"):
            self.assertFalse(hasattr(z, name), name)
        for label in ("N01", "PD8", "PD8_A2SLOW", "R2", "M2"):
            self.assertNotIn(label, z._STYLE_SHA256)
            self.assertNotIn(label, z._STYLE_TEXT)
        for role, spec in z.FAMILY_Z_ROLE_STYLE.items():
            self.assertNotIn(spec["style_label"], ("N01", "PD8", "PD8_A2SLOW", "R2", "M2"), role)

    def test_style_text_for_each_kind(self):
        for level in ("a2", "b1b"):
            plan, _, _ = make_plan(level)
            for s in plan:
                st = z.style_text_for(s)
                if s.kind == "narrator":
                    self.assertEqual(st, xprof.PD06_TEXT, s.clip_id)
                else:
                    self.assertTrue(st is None or xprof.PD06_TEXT not in st, s.clip_id)   # Narrator以外(Dialogue含む)はPD06の対象外

    def test_non_narrator_roles_pins(self):
        pins = {"STD_JA_PREVIEW": "S3", "STD_JA_COMMENT": "S3", "ADV_EN_PREVIEW": "E1", "ADV_EN_COMMENT": "E2_UPBEAT",
                "KP_EN": "K2", "KP_JA": "P8_KP", "KP_EXPL_EN": "P7"}
        for role, label in pins.items():
            self.assertEqual(z.FAMILY_Z_ROLE_STYLE[role]["style_label"], label)
            self.assertEqual(z.role_style_sha256(role), z._STYLE_SHA256[label])
        for role in ("DIALOGUE_ADV", "DIALOGUE_STD", "SHELL"):
            self.assertIsNone(z.FAMILY_Z_ROLE_STYLE[role]["text"])

    def test_z_does_not_depend_on_x_default_profile_or_resolver(self):
        """Opus R-C1: ZはXの承認済み定数のみ参照し、DEFAULT_NEW_RUN_PROFILE・profile解決関数・STYLE_PROFILESには従属しない。"""
        with open("er063_family_z_audio_01.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        forbidden = {"DEFAULT_NEW_RUN_PROFILE", "resolve_run_profile", "get_profile", "resolve_role_style", "STYLE_PROFILES",
                     "PROFILE_FX_20261017", "PROFILE_FX_20261016", "has_role_override"}
        hits = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in forbidden:
                hits.append(node.attr)
            elif isinstance(node, ast.Name) and node.id in forbidden:
                hits.append(node.id)
            elif isinstance(node, ast.ImportFrom) and any(a.name in forbidden for a in node.names):
                hits.append("ImportFrom")
        self.assertEqual(hits, [])


class ZRunStyleRecordTest(unittest.TestCase):
    """Opus R-C4: run単位で全Role Styleを記録し、不一致/記録なし+結果ファイル有りは課金前にSTOP。"""

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

    def test_new_run_gets_full_record_and_resumes(self):
        for level in ("a2", "b1b"):
            plan, _, _ = make_plan(level)
            z.run_tts_stage(self.run, level, plan, generators=fake_generators())
            with open(f"{self.run}/{level}/{z.STYLE_RECORD_RELPATH}", encoding="utf-8") as f:
                rec = json.load(f)
            self.assertEqual(rec["roles"]["NARRATOR_FULL_STORY_STD"]["style_label"], "PD06")
            self.assertEqual(rec["roles"]["NARRATOR_FULL_STORY_STD"]["style_prefix_sha256"], PD06_SHA)
            self.assertEqual(set(rec["roles"]), set(z.FAMILY_Z_ROLE_STYLE))    # 全Role(Dialogue/SHELL含む)
            # resume(同一run、記録一致)は通る
            z.run_tts_stage(self.run, level, plan, generators=fake_generators())
            with open(f"{self.run}/{level}/audit/tts_generation_results.json", encoding="utf-8") as f:
                results = json.load(f)
            nar = [e for e in results["segments"].values() if e.get("clip_kind") == "narrator"]
            self.assertTrue(nar)
            for e in nar:
                self.assertEqual(e["style"]["instruction_label"], "PD06")
                self.assertEqual(e["style"]["style_prefix_sha256"], PD06_SHA)

    def test_existing_legacy_run_without_record_stops_before_any_generation(self):
        for level, label, sha in (("a2", "N01", OLD_N01_SHA), ("b1b", "PD8", OLD_PD8_SHA)):
            p = self._legacy_results(level, label, sha)
            before = _sha_file(p)
            plan, _, _ = make_plan(level)
            calls = []
            gens = {k: (lambda s, pth, k=k: calls.append(k)) for k in fake_generators()}
            with self.assertRaises(z.FamilyZRunStyleMismatchStop) as cm:
                z.run_tts_stage(self.run, level, plan, generators=gens)
            self.assertIn("Style記録", str(cm.exception))
            self.assertEqual(calls, [], level)                                   # 生成(課金)に到達しない
            self.assertEqual(_sha_file(p), before, level)                        # 既存結果は変更しない
            self.assertFalse(os.path.exists(f"{self.run}/{level}/{z.STYLE_RECORD_RELPATH}"))

    def test_old_exception_alias_still_catches(self):
        self.assertIs(z.FamilyZNarratorStyleMismatchStop, z.FamilyZRunStyleMismatchStop)

    def test_dry_run_reports_without_raising_or_writing(self):
        p = self._legacy_results("b1b", "PD8", OLD_PD8_SHA)
        before = _sha_file(p)
        plan, _, _ = make_plan("b1b")
        out = z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators(), dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["style_record"]["status"], "RUN_STATE_WITHOUT_RECORD")
        self.assertEqual(_sha_file(p), before)
        self.assertFalse(os.path.exists(f"{self.run}/b1b/{z.STYLE_RECORD_RELPATH}"))

    def test_dry_run_new_run_is_new_run_status(self):
        plan, _, _ = make_plan("a2")
        out = z.run_tts_stage(self.run, "a2", plan, generators=fake_generators(), dry_run=True)
        self.assertEqual(out["style_record"]["status"], "NEW_RUN")
        self.assertFalse(os.path.exists(self.run))


if __name__ == "__main__":
    unittest.main()
