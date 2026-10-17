# -*- coding: utf-8 -*-
# ============================================================
# er019_family_x_s3_wiring_01_test_01.py
# FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01 委任_03 (Phase B、2026-10-17、ユーザー正式承認 APPROVED_FOR_PRODUCTION)
# ============================================================
# 目的: Family X Standard日本語Preview/Comment1〜4(role SUPPORT_JA)の正式StyleがR2→S3(sha 060c08fd…, 199字)へ
# Production既定として配線されたこと、他role/Advanced/旧profileが不変であること、注意点③(S3非適用の無警告通過が無いこと)を固定する。
# 実行: .venv/Scripts/python.exe -m pytest er019_family_x_s3_wiring_01_test_01.py -q
# ============================================================
import hashlib
import json
import os
import re
import tempfile
import unittest
from unittest import mock

import er019_family_x_audio_production_runner_01 as runner
import er019_family_x_style_profile_01 as sp

NEW = sp.PROFILE_FX_20261017
OLD = sp.PROFILE_FX_20261016
FL = "speech_metadata_flash_lite"
S3_SHA = "060c08fde003cf7c2d15c654da96d3f857b8e7a9bd79eac31814ceaf7c923f33"
S3_MD = "er057_output/ja_support_calm_style_trial_04/PROMPTS_01.md"
SEGS = ("preview", "comment_1", "comment_2", "comment_3", "comment_4")


def _sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def _ok(*_a, **_kw):
    return {"status": "OK", "canonical_text": "x", "fallback_used": False}


class S3ConstantTests(unittest.TestCase):
    def test_s3_constant_sha_len(self):
        self.assertEqual(len(sp.SUPPORT_JA_STYLE_S3_20261017), 199)
        self.assertEqual(sp.SUPPORT_JA_STYLE_S3_LENGTH, 199)
        self.assertEqual(_sha(sp.SUPPORT_JA_STYLE_S3_20261017), S3_SHA)
        self.assertEqual(sp.SUPPORT_JA_STYLE_S3_SHA256, S3_SHA)

    def test_s3_verbatim_vs_trial_source(self):
        md = open(S3_MD, encoding="utf-8").read()
        i = md.index("## S3 ")
        blk = re.search(r"```\n(.*?)\n```", md[i:], re.S).group(1)
        self.assertEqual(sp.SUPPORT_JA_STYLE_S3_20261017, blk)

    def test_s3_differs_from_r2_and_has_no_wpm(self):
        import er002_common
        self.assertNotEqual(sp.SUPPORT_JA_STYLE_S3_20261017, sp.R2_TEXT)
        er002_common.assert_no_wpm_specification(sp.SUPPORT_JA_STYLE_S3_20261017)

    def test_verify_constants_detects_tampering(self):
        with mock.patch.object(sp, "SUPPORT_JA_STYLE_S3_20261017", sp.SUPPORT_JA_STYLE_S3_20261017 + "。"):
            with self.assertRaises(sp.StyleProfileStop):
                sp._verify_constants()

    def test_old_constants_unchanged(self):
        self.assertEqual(sp.R2_SHA256, "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f")
        self.assertEqual(sp.PD06_SHA256, "3a680861e4d9d1bc46ddba4dc1fc91f26c68f9f9c5e5e450a85fcba7fda43c2d")
        self.assertEqual(sp.K2_SHA256, "9d905cfe6c040cd001c4e7877327044f540a72bd315776f2c297e0f58f7aea42")


class ProfileDiffTests(unittest.TestCase):
    def test_default_is_fx_20261017(self):
        self.assertEqual(sp.DEFAULT_NEW_RUN_PROFILE, "fx_20261017")

    def test_only_support_ja_differs_from_old_default(self):
        a, b = sp.STYLE_PROFILES[OLD]["overrides"], sp.STYLE_PROFILES[NEW]["overrides"]
        self.assertEqual(set(a), set(b))
        self.assertEqual([r for r in a if a[r] != b[r]], ["SUPPORT_JA"])
        self.assertEqual(b["SUPPORT_JA"]["sha256"], S3_SHA)
        self.assertEqual(a["SUPPORT_JA"]["sha256"], sp.R2_SHA256)

    def test_resolve_per_role_level_s3_std_only_adv_unchanged(self):
        base = lambda r: f"BASE:{r}"
        self.assertEqual(sp.resolve_role_style(NEW, "SUPPORT_JA", "a2", base), sp.SUPPORT_JA_STYLE_S3_20261017)
        self.assertEqual(sp.resolve_role_style(NEW, "SUPPORT_JA", "b1b", base), "BASE:SUPPORT_JA")  # Adv影響なし
        for role, level in (("FULL_STORY", "a2"), ("FULL_STORY", "b1b"), ("PREVIEW", "b1b"), ("PREVIEW", "a2"),
                            ("KP_EXPLANATION_EN", "b1b"), ("KP_EN", "a2"), ("KP_EN", "b1b"),
                            ("KP_JA_MEANING", "a2"), ("KP_JA_MEANING", "b1b"),
                            ("IN_ONE_LINE", "a2"), ("TOPIC_INTRO", "a2")):
            self.assertEqual(sp.resolve_role_style(NEW, role, level, base), sp.resolve_role_style(OLD, role, level, base),
                             (role, level))

    def test_r2_only_in_legacy_profiles_dangling_check(self):
        users = sorted(pid for pid, p in sp.STYLE_PROFILES.items()
                       if p["overrides"].get("SUPPORT_JA", {}).get("sha256") == sp.R2_SHA256)
        self.assertEqual(users, sorted(["coffee_final_v5", "coffee_n01_r2_p3", "coffee_n01_r2_p3_e1", OLD]))
        self.assertNotIn(NEW, users)

    def test_record_roundtrip_and_levels(self):
        rec = sp.build_record(NEW)
        self.assertEqual(rec["profile_id"], NEW)
        self.assertEqual(rec["roles"]["SUPPORT_JA"]["sha256"], S3_SHA)
        self.assertEqual(rec["roles"]["SUPPORT_JA"]["length"], 199)
        self.assertEqual(rec["roles"]["SUPPORT_JA"]["levels"], ["a2"])
        self.assertEqual(sp.verify_record(rec), NEW)
        rec["roles"]["SUPPORT_JA"]["sha256"] = sp.R2_SHA256   # R2へ差し替えた記録は不一致でSTOP
        with self.assertRaises(sp.StyleProfileStop):
            sp.verify_record(rec)

    def test_cli_choices_contain_both(self):
        ch = runner.build_arg_parser()._option_string_actions["--style-profile"].choices
        self.assertIn(NEW, ch)
        self.assertIn(OLD, ch)


class ResolutionTests(unittest.TestCase):
    def test_no_cli_new_dir_selects_new_default_and_writes_record(self):
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/o"
            self.assertEqual(sp.resolve_run_profile(out, None, tts_backend=FL), (NEW, "default_new_run_fx_20261017"))
            self.assertEqual(sp.read_record(out)["roles"]["SUPPORT_JA"]["sha256"], S3_SHA)

    def test_resume_old_default_record_keeps_r2_and_warns(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/audit")
            json.dump(sp.build_record(OLD), open(sp.record_path(d), "w", encoding="utf-8"))
            pid, src = sp.resolve_run_profile(d, None, tts_backend=FL)
            self.assertEqual((pid, src), (OLD, "record"))       # 黙ってS3へ切替わらない(記録が正)
            self.assertIn("旧profileでresume中", sp.profile_resolution_warning(pid, src))
            self.assertEqual(sp.read_record(d)["profile_id"], OLD)  # 記録不変
            with self.assertRaises(sp.StyleProfileStop):        # CLIで新profileを明示しても途中変更不可
                sp.resolve_run_profile(d, NEW, tts_backend=FL)

    def test_migration_old_to_new_is_rejected_style_differs(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/audit")
            json.dump(sp.build_record(OLD), open(sp.record_path(d), "w", encoding="utf-8"))
            with self.assertRaises(sp.StyleProfileStop):
                sp.migrate_record(d, OLD, NEW, "reason", "MID")

    def test_existing_run_artifacts_without_record_stops(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(f"{d}/a2/audit")
            open(f"{d}/a2/audit/tts_generation_results.json", "w").write("{}")
            with self.assertRaises(sp.StyleProfileStop):        # 既存R2 runへ途中でS3を混ぜない
                sp.resolve_run_profile(d, None, write=False, tts_backend=FL)

    def test_legacy_backend_cannot_apply_new_profile(self):
        with self.assertRaises(sp.StyleProfileStop):
            sp.assert_profile_backend(NEW, "structured_separation")


class RunnerS3ApplicationTests(unittest.TestCase):
    def _run_a2(self, profile, d):
        out = f"{d}/a2"
        os.makedirs(out)
        parts = {"title": "T", "part1": "P1 text.", "part2": "P2 text.", "part3": "P3 text.", "in_one_line": "IOL text."}
        support = {n: f"テキスト{n}" for n in SEGS}
        json.dump(parts, open(f"{out}/parts.json", "w", encoding="utf-8"))
        json.dump(support, open(f"{out}/a2_support_texts.json", "w", encoding="utf-8"))
        with mock.patch.object(runner.shared_narration, "ensure_all_shared_narration_a2", return_value={}), \
             mock.patch.object(runner.crosslevel_common, "generate_english_segment_with_fallback", side_effect=_ok), \
             mock.patch.object(runner.n3_tts, "generate_a2_japanese_with_reading_safety", side_effect=_ok) as ja, \
             mock.patch.object(runner.n3_tts, "generate_a2_segment_with_slowdown", side_effect=_ok) as slow:
            runner.generate_family_x_a2_segments(d, japanese_title="題", tts_backend=FL, style_profile=profile)
        with open(f"{out}/audit/tts_generation_results.json", encoding="utf-8") as f:
            return ja, slow, json.load(f)

    def test_five_support_segments_get_s3_and_record_sha(self):
        with tempfile.TemporaryDirectory() as d:
            ja, slow, res = self._run_a2(NEW, d)
            by = {os.path.basename(c.args[1]): c.kwargs["style_prefix_override"] for c in ja.call_args_list}
            for n in SEGS:
                self.assertEqual(by[f"{n}.wav"], sp.SUPPORT_JA_STYLE_S3_20261017, n)
                self.assertEqual(res["segments"][n]["style_profile"]["style_base_sha256"], S3_SHA, n)
                self.assertEqual(res["segments"][n]["style_profile"]["profile_id"], NEW)
            # japanese_titleはSUPPORT_JA対象外(従来J3のまま、S3ではない)
            self.assertNotEqual(by["japanese_title.wav"], sp.SUPPORT_JA_STYLE_S3_20261017)
            # Full Story=PD06逐語(S3/R2変更の影響なし)
            sby = {os.path.basename(c.args[1]): c.kwargs["style_prefix_override"] for c in slow.call_args_list}
            for n in ("full_story_part1", "full_story_part2", "full_story_part3"):
                self.assertEqual(sby[f"{n}.wav"], sp.PD06_TEXT)

    def test_old_profile_still_applies_r2_for_resume(self):
        with tempfile.TemporaryDirectory() as d:
            ja, _slow, res = self._run_a2(OLD, d)
            by = {os.path.basename(c.args[1]): c.kwargs["style_prefix_override"] for c in ja.call_args_list}
            for n in SEGS:
                self.assertEqual(by[f"{n}.wav"], sp.R2_TEXT)
                self.assertEqual(res["segments"][n]["style_profile"]["style_base_sha256"], sp.R2_SHA256)

    def test_other_segments_identical_between_old_and_new(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            ja1, s1, _ = self._run_a2(OLD, d1)
            ja2, s2, _ = self._run_a2(NEW, d2)
            key = lambda m: {os.path.basename(c.args[1]): c.kwargs.get("style_prefix_override") for c in m.call_args_list}
            self.assertEqual(key(s1), key(s2))
            a, b = key(ja1), key(ja2)
            self.assertEqual({k: v for k, v in a.items() if k[:-4] not in SEGS},
                             {k: v for k, v in b.items() if k[:-4] not in SEGS})


def _entry(base_sha=S3_SHA, fallback=False, lr=False, text="t"):
    e = {"status": "OK", "canonical_text": text, "fallback_used": fallback,
         "style_profile": {"profile_id": NEW, "role": "SUPPORT_JA", "expected_base_sha256": S3_SHA,
                           "style_base_sha256": base_sha}}
    if lr:
        e["local_rewrite_recovery"] = {"x": 1}
    return e


class FallbackGuaranteeTests(unittest.TestCase):
    """注意点③: S3非適用(minimal fallback / R2 / local rewrite)をS3正常適用としてPASSさせない
    (既存M3 BLOCKで検知。新fallback仕様は追加していない)。"""

    def _gate(self, **per):
        segs = {n: _entry() for n in SEGS}
        for n, e in per.items():
            segs[n] = e
        g = sp.m3_assembly_gate(NEW, "a2", {"segments": segs, "key_phrases": {}})
        return {b["segment"]: b["violations"] for b in g["blocked"] if b["segment"] in SEGS}

    def test_all_s3_ok_no_ja_block(self):
        self.assertEqual(self._gate(), {})

    def test_minimal_fallback_blocks(self):
        self.assertIn("JA_FALLBACK_USED_OR_UNKNOWN", self._gate(comment_2=_entry(fallback=True))["comment_2"])

    def test_unknown_fallback_flag_blocks(self):
        e = _entry()
        del e["fallback_used"]
        self.assertIn("JA_FALLBACK_USED_OR_UNKNOWN", self._gate(preview=e)["preview"])

    def test_r2_style_audio_under_s3_profile_blocks(self):
        self.assertIn("STYLE_BASE_SHA_MISMATCH_OR_MISSING",
                      self._gate(comment_1=_entry(base_sha=sp.R2_SHA256))["comment_1"])

    def test_local_rewrite_blocks(self):
        self.assertIn("LOCAL_REWRITE_RECOVERY", self._gate(comment_3=_entry(lr=True))["comment_3"])

    def test_missing_segment_blocks(self):
        segs = {n: _entry() for n in SEGS if n != "comment_4"}
        g = sp.m3_assembly_gate(NEW, "a2", {"segments": segs, "key_phrases": {}})
        blocked = {b["segment"]: b["violations"] for b in g["blocked"]}
        self.assertIn("NO_SEGMENT_RECORD", blocked["comment_4"])

    def test_assemble_stage_invokes_style_gate_for_a2(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertIn('_style_profile_gate_blocked_summary(theme_out_dir, out_dir, "a2")', src)


class IsolationTests(unittest.TestCase):
    def test_family_a_shared_modules_do_not_reference_s3(self):
        for p in ("er006_audio_cost_pilot_02_shared_narration.py", "er006_master_audio_store_01.py"):
            text = open(p, encoding="utf-8").read()
            self.assertNotIn("060c08fd", text, p)
            self.assertNotIn("fx_20261017", text, p)

    def test_runner_has_no_hardcoded_r2_for_support_ja(self):
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        self.assertNotIn("625826c1", src)
        self.assertNotIn("R2_TEXT", src)


if __name__ == "__main__":
    unittest.main()
