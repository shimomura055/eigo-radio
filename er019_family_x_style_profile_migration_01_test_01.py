# -*- coding: utf-8 -*-
"""FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_03: E1配線(新profile coffee_n01_r2_p3_e1)・記録移行CLI・
Preview M4/Gate・既存profile不変のtest。API呼出なし(tmp dir)。"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

import er019_family_x_style_profile_01 as sp
import er057_tone_trial_tts_gen_01 as tone

NEW = sp.PROFILE_COFFEE_N01_R2_P3_E1
OLD = sp.PROFILE_COFFEE_N01_R2_P3
MID = "TEST-MANAGED-ID"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _old_dir(profile=OLD):
    d = tempfile.mkdtemp()
    os.makedirs(f"{d}/audit")
    with open(sp.record_path(d), "w", encoding="utf-8") as f:
        json.dump(sp.build_record(profile), f, ensure_ascii=False)
    return d


class E1ConstantTests(unittest.TestCase):
    def test_e1_matches_origin_and_approved_sha(self):
        origin = tone.SPECS["E"]["items"]["E1"][2]
        self.assertEqual(sp.E1_TEXT, origin)
        self.assertEqual(_sha(sp.E1_TEXT), sp.E1_SHA256)
        self.assertTrue(sp.E1_SHA256.startswith("8862317ff766"))
        self.assertEqual(len(sp.E1_TEXT), sp.E1_LENGTH)

    def test_new_profile_roles_and_levels(self):
        self.assertEqual(sp.overridden_roles(NEW), sorted(["FULL_STORY", "SUPPORT_JA", "KP_EXPLANATION_EN", "PREVIEW"]))
        self.assertEqual(sp.ROLE_LEVELS["PREVIEW"], ("b1b",))
        self.assertEqual(sp.ROLE_SEGMENTS["PREVIEW"], ("preview",))
        self.assertEqual(sp.resolve_role_style(NEW, "PREVIEW", "b1b", lambda r: "BASE"), sp.E1_TEXT)
        self.assertEqual(sp.resolve_role_style(NEW, "COMMENT", "b1b", lambda r: "BASE"), "BASE")

    def test_a2_behaviour_unchanged_by_preview_role(self):
        self.assertEqual(sp.resolve_role_style(NEW, "PREVIEW", "a2", lambda r: "BASE"), "BASE")
        self.assertEqual(sp.overridden_segment_names(NEW, "a2"), sp.overridden_segment_names(OLD, "a2"))
        self.assertEqual(sp.overridden_segment_names(NEW, "b1b"), sp.overridden_segment_names(OLD, "b1b") + ["preview"])
        self.assertEqual([t[0] for t in sp._gate_targets(NEW, "a2", {})], [t[0] for t in sp._gate_targets(OLD, "a2", {})])

    def test_existing_profiles_unchanged(self):
        for pid in (sp.PROFILE_DEFAULT, sp.PROFILE_COFFEE_P8, sp.PROFILE_COFFEE_FINAL_V5, sp.PROFILE_N01, OLD):
            self.assertNotIn("PREVIEW", sp.get_profile(pid)["overrides"])
        self.assertEqual(sp.overridden_roles(OLD), ["FULL_STORY", "KP_EXPLANATION_EN", "SUPPORT_JA"])

    def test_segment_profile_record_for_preview(self):
        e = sp.attach_segment_profile_record({}, NEW, "PREVIEW", sp.E1_TEXT)
        self.assertEqual(e["style_profile"]["expected_base_sha256"], sp.E1_SHA256)
        self.assertEqual(e["style_profile"]["style_base_sha256"], sp.E1_SHA256)
        self.assertEqual(sp.attach_segment_profile_record({}, OLD, "PREVIEW", sp.E1_TEXT), {})


class PreviewGateTests(unittest.TestCase):
    def _results(self, prefix, itype="english_style_prefix", base=sp.E1_SHA256):
        def seg(role_sha, st):
            return {"status": "OK", "style_prefix": st, "instruction_type": "english_style_prefix_wide_margin",
                    "fallback_used": False,
                    "style_profile": {"style_base_sha256": role_sha, "expected_base_sha256": role_sha}}
        segs = {
            "preview": {"status": "OK", "style_prefix": prefix, "instruction_type": itype,
                        "style_profile": {"style_base_sha256": base, "expected_base_sha256": sp.E1_SHA256}},
        }
        for n in ("full_story_part1", "full_story_part2", "full_story_part3"):
            segs[n] = seg(sp.N01_SHA256, sp.N01_TEXT)
        return {"segments": segs, "key_phrases": {}}

    def test_pass_when_e1_applied(self):
        g = sp.m3_assembly_gate(NEW, "b1b", self._results(sp.E1_TEXT))
        self.assertEqual([b for b in g["blocked"] if b["segment"] == "preview"], [])

    def test_block_when_minimal_fallback_or_missing_record(self):
        g = sp.m3_assembly_gate(NEW, "b1b", self._results("minimal", itype="minimal_fallback"))
        v = [b["violations"] for b in g["blocked"] if b["segment"] == "preview"][0]
        self.assertIn("PREVIEW_MINIMAL_FALLBACK", v)
        self.assertIn("PREVIEW_STYLE_PREFIX_NOT_E1_PREFIXED", v)
        r = self._results(sp.E1_TEXT)
        del r["segments"]["preview"]["style_profile"]
        g2 = sp.m3_assembly_gate(NEW, "b1b", r)
        self.assertTrue(any(b["segment"] == "preview" for b in g2["blocked"]))


class MigrationTests(unittest.TestCase):
    def test_migrate_ok_and_verify_after(self):
        d = _old_dir()
        old_bytes = open(sp.record_path(d), "rb").read()
        rec = sp.migrate_record(d, OLD, NEW, "reason X", MID, now="2026-10-13T00:00:00")
        m = rec["migration"]
        self.assertEqual((m["from"], m["to"], m["reason"], m["managed_id"], m["timestamp"]),
                         (OLD, NEW, "reason X", MID, "2026-10-13T00:00:00"))
        self.assertEqual(m["old_sha"], hashlib.sha256(old_bytes).hexdigest())
        self.assertEqual(m["added_roles"], ["PREVIEW"])
        self.assertTrue(m["new_sha"])
        self.assertEqual(open(f"{d}/audit/style_profile_migrated_from_01.json", "rb").read(), old_bytes)
        loaded = sp.read_record(d)
        self.assertEqual(sp.verify_record(loaded), NEW)
        self.assertEqual(sp.resolve_run_profile(d, NEW, write=False), (NEW, "record"))
        self.assertEqual(sp.resolve_run_profile(d, None, write=False), (NEW, "record"))

    def test_hand_edited_profile_id_fails_verify(self):
        d = _old_dir()
        r = sp.read_record(d)
        r["profile_id"] = NEW
        with self.assertRaises(sp.StyleProfileStop):
            sp.verify_record(r)

    def test_reject_not_superset(self):
        d = _old_dir(sp.PROFILE_COFFEE_FINAL_V5)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, sp.PROFILE_COFFEE_FINAL_V5, NEW, "r", MID)
        d2 = _old_dir(NEW)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d2, NEW, OLD, "r", MID)

    def test_reject_same_mismatch_missing_and_empty_reason(self):
        d = _old_dir()
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, OLD, OLD, "r", MID)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, sp.PROFILE_N01, NEW, "r", MID)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, OLD, NEW, "  ", MID)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(tempfile.mkdtemp(), OLD, NEW, "r", MID)
        self.assertFalse(os.path.exists(f"{d}/audit/style_profile_migrated_from_01.json"))

    def test_reject_text_sha_mismatch_in_record(self):
        d = _old_dir()
        r = sp.read_record(d)
        r["roles"]["SUPPORT_JA"]["sha256"] = "0" * 64
        json.dump(r, open(sp.record_path(d), "w", encoding="utf-8"))
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, OLD, NEW, "r", MID)
        self.assertEqual(sp.read_record(d)["roles"]["SUPPORT_JA"]["sha256"], "0" * 64)

    def test_second_migration_rejected(self):
        d = _old_dir()
        sp.migrate_record(d, OLD, NEW, "r", MID)
        with self.assertRaises(sp.StyleProfileStop):
            sp.migrate_record(d, OLD, NEW, "r", MID)

    def test_m2_still_blocks_new_record_with_run_state(self):
        d = tempfile.mkdtemp()
        os.makedirs(f"{d}/a2/audit")
        open(f"{d}/a2/audit/tts_generation_results.json", "w").write("{}")
        with self.assertRaises(sp.StyleProfileStop):
            sp.resolve_run_profile(d, NEW, write=True)

    def test_cli_migration(self):
        d = _old_dir()
        r = subprocess.run([sys.executable, "er019_family_x_audio_production_runner_01.py", "--out-dir", d,
                            "--migrate-style-profile-record", "--from", OLD, "--to", NEW, "--reason", "cli test"],
                           capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertIn("MIGRATED", r.stdout)
        self.assertEqual(sp.verify_record(sp.read_record(d)), NEW)
        self.assertEqual(sp.read_record(d)["migration"]["managed_id"], "FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01")


if __name__ == "__main__":
    unittest.main()
