# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_15(Opus条件Aレビュー_C R-C1/R-C2/R-C4/R-C7): Family Z 共通Style配線のtest(課金0)。
 t1 drift: 共通roleのZ解決sha == Xの承認済み定数sha == X既定profile(fx_20261017)の該当roleのsha(X既定が変わればFAIL)
 t2 Z側にer019定数と同一文字列のコピー定数が残っていない
 t3 例外roleの明示列挙
 t4 roleのtext差替えで該当roleのreuse_keyのみ変化し、Dialogueのreuse_keyは不変
 t5 speaker -> Voice対応の不変
 t6 全Role記録の不一致STOP・記録なし+結果ファイル存在STOP
 t7 新run copy allowlist/除外
 t8 X既定profile(DEFAULT_NEW_RUN_PROFILE)を変えてもZの解決は変わらない(非従属)
実行: .venv/Scripts/python.exe -m unittest er063_family_z_common_style_wiring_01_test_01 -v"""
from __future__ import annotations

import ast
import json
import os
import shutil
import tempfile
import unittest
from unittest import mock

import er019_family_x_style_profile_01 as xprof
import er063_family_z_audio_01 as z
from er063_family_z_audio_01_test_01 import fake_generators, make_plan

EXPECTED_EXCEPTION_ROLES = {"ADV_EN_COMMENT", "TOPIC_INTRO_EN", "JAPANESE_TITLE", "DIALOGUE_ADV", "DIALOGUE_STD", "SHELL"}


def _all_plan_specs():
    return [s for lv in ("a2", "b1b") for s in make_plan(lv)[0]]


class T1DriftTest(unittest.TestCase):
    def test_map_covers_exactly_all_roles(self):
        self.assertEqual(set(z.CROSS_FAMILY_COMMON_STYLE_MAP), set(z.FAMILY_Z_ROLE_STYLE))

    def test_common_roles_resolve_to_x_constant_sha(self):
        x_default = xprof.get_profile(xprof.DEFAULT_NEW_RUN_PROFILE)["overrides"]       # テスト側だけがX既定を参照する(drift検知)
        checked = 0
        for role, row in z.CROSS_FAMILY_COMMON_STYLE_MAP.items():
            if row["X"] is None:
                self.assertTrue(row["Z"].startswith("EXCEPTION:"), role)
                continue
            x_text = getattr(xprof, row["X"])
            x_sha = xprof.sha256_text(x_text)
            spec = z.FAMILY_Z_ROLE_STYLE[role]
            self.assertEqual(spec["style_label"], row["Z"], role)
            self.assertEqual(z.role_style_sha256(role), x_sha, role)                    # Z解決sha == X定数sha
            self.assertEqual(spec["text"], x_text, role)
            self.assertEqual(z._STYLE_SHA256[row["Z"]], x_sha, role)                    # Z側literal固定shaとも一致
            xo = x_default.get(row["X_profile_role"])
            self.assertIsNotNone(xo, f"X既定profileに{row['X_profile_role']}のoverrideが無い(X既定が変わった: Z配線またはEXCEPTION登録が必要)")
            self.assertEqual(xo["sha256"], x_sha, f"{role}: X既定のshaが変わった。Z配線の再判断が必要")
            for lv in row["X_levels"]:
                self.assertIn(lv, xprof.ROLE_LEVELS[row["X_profile_role"]] if row["X_profile_role"] in xprof.ROLE_LEVELS else (lv,))
            checked += 1
        self.assertEqual(checked, 8)

    def test_x_default_override_roles_all_mapped(self):
        """X既定profileのoverride roleは、Zの対応表のX_profile_roleに全て現れる(新roleがXに追加されたらFAIL=Z配線かEXCEPTION登録を強制)。"""
        x_roles = set(xprof.get_profile(xprof.DEFAULT_NEW_RUN_PROFILE)["overrides"])
        z_roles = {row["X_profile_role"] for row in z.CROSS_FAMILY_COMMON_STYLE_MAP.values() if row["X"] is not None}
        self.assertEqual(x_roles, z_roles)


class T2NoCopyTest(unittest.TestCase):
    def test_no_literal_copy_of_x_constants_in_z_source(self):
        x_strings = {}
        for name, val in vars(xprof).items():
            if isinstance(val, str) and len(val) >= 30 and (name.endswith("_TEXT") or name == "SUPPORT_JA_STYLE_S3_20261017"):
                x_strings[val] = name
        self.assertGreaterEqual(len(x_strings), 8)
        with open("er063_family_z_audio_01.py", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        copies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in x_strings:
                copies.append((x_strings[node.value], node.lineno))
        self.assertEqual(copies, [])

    def test_z_values_are_the_x_objects(self):
        for label, name in (("PD06", "PD06_TEXT"), ("S3", "SUPPORT_JA_STYLE_S3_20261017"), ("E1", "E1_TEXT"),
                            ("K2", "K2_TEXT"), ("P7", "P7_TEXT"), ("P8_KP", "P8_KP_JA_TEXT")):
            self.assertIs(z._STYLE_TEXT[label], getattr(xprof, name), label)


class T3ExceptionRolesTest(unittest.TestCase):
    def test_exception_roles_are_explicit(self):
        exc = {r for r, row in z.CROSS_FAMILY_COMMON_STYLE_MAP.items() if row["Z"].startswith("EXCEPTION:")}
        self.assertEqual(exc, EXPECTED_EXCEPTION_ROLES)
        for r in EXPECTED_EXCEPTION_ROLES:
            spec = z.FAMILY_Z_ROLE_STYLE[r]
            self.assertEqual(spec["origin_kind"], "family_z_specific", r)
            self.assertTrue(spec["origin"].startswith("family_z_specific"), r)
        for r in set(z.FAMILY_Z_ROLE_STYLE) - EXPECTED_EXCEPTION_ROLES:
            self.assertEqual(z.FAMILY_Z_ROLE_STYLE[r]["origin_kind"], "x_common_constant", r)

    def test_style_label_is_recorded_per_role(self):
        for r, spec in z.FAMILY_Z_ROLE_STYLE.items():
            self.assertTrue(spec["style_label"], r)
            if spec["text"] is not None:
                self.assertIn(spec["style_label"], z._STYLE_SHA256, r)

    def test_role_style_version_not_bumped(self):
        self.assertEqual(z.FAMILY_Z_ROLE_STYLE_VERSION, "z_v2_pd8_r2_e1_e2up_k2_m2_kpx_20261012")


class T4ReuseKeyTest(unittest.TestCase):
    def test_changing_a_role_text_changes_only_that_roles_reuse_key(self):
        specs = _all_plan_specs()
        before = {(s.level, s.clip_id): z.build_reuse_key(s) for s in specs}
        patched = dict(z.FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_STD"], text="TAMPERED STYLE")
        with mock.patch.dict(z.FAMILY_Z_ROLE_STYLE, {"NARRATOR_FULL_STORY_STD": patched}):
            after = {(s.level, s.clip_id): z.build_reuse_key(s) for s in specs}
        changed = {k for k in before if before[k] != after[k]}
        expected = {(s.level, s.clip_id) for s in specs if s.role_key == "NARRATOR_FULL_STORY_STD"}
        self.assertTrue(expected)
        self.assertEqual(changed, expected)
        for s in specs:
            if s.kind == "dialogue":
                self.assertEqual(before[(s.level, s.clip_id)], after[(s.level, s.clip_id)], s.clip_id)

    def test_dialogue_reuse_key_independent_of_all_common_role_texts(self):
        specs = [s for s in _all_plan_specs() if s.kind == "dialogue"]
        self.assertTrue(specs)
        before = [z.build_reuse_key(s) for s in specs]
        tampered = {r: dict(spec, text="X" + (spec["text"] or "")) for r, spec in z.FAMILY_Z_ROLE_STYLE.items() if spec["text"] is not None}
        with mock.patch.dict(z.FAMILY_Z_ROLE_STYLE, tampered):
            after = [z.build_reuse_key(s) for s in specs]
        self.assertEqual(before, after)


class T5VoiceTest(unittest.TestCase):
    def test_speaker_to_voice_mapping_unchanged(self):
        self.assertEqual(z.FAMILY_Z_DIALOGUE_VOICE_TTS_NAMES,
                         {"narrator": "Aoede", "melos": "Algieba", "selinuntius": "Erinome", "dionysius": "Charon"})
        self.assertEqual(z.SPEAKER_ALIASES, {"king": "dionysius", "friend": "selinuntius", "melos": "melos", "narrator": "narrator",
                                             "dionysius": "dionysius", "selinuntius": "selinuntius"})
        for s in _all_plan_specs():
            if s.kind == "dialogue":
                self.assertEqual(s.voice, z.resolve_dialogue_voice(s.speaker), s.clip_id)
            if s.kind == "narrator":
                self.assertEqual(s.voice, "Aoede")


class T6RunStateStopTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.run = f"{self.tmp}/melos/run_01"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _no_gen(self):
        calls = []
        return calls, {k: (lambda s, p, k=k: calls.append(k)) for k in fake_generators()}

    def test_non_narrator_role_mismatch_in_record_stops_before_generation(self):
        plan, _, _ = make_plan("a2")
        z.run_tts_stage(self.run, "a2", plan, generators=fake_generators())
        rec_path = f"{self.run}/a2/{z.STYLE_RECORD_RELPATH}"
        with open(rec_path, encoding="utf-8") as f:
            rec = json.load(f)
        rec["roles"]["STD_JA_PREVIEW"]["style_prefix_sha256"] = "0" * 64      # 旧Style(R2等)で記録された状態を模擬
        rec["roles"]["STD_JA_PREVIEW"]["style_label"] = "R2"
        with open(rec_path, "w", encoding="utf-8") as f:
            json.dump(rec, f)
        calls, gens = self._no_gen()
        with self.assertRaises(z.FamilyZRunStyleMismatchStop) as cm:
            z.run_tts_stage(self.run, "a2", plan, generators=gens)
        self.assertIn("STD_JA_PREVIEW", str(cm.exception))
        self.assertEqual(calls, [])

    def test_missing_role_in_record_stops(self):
        plan, _, _ = make_plan("b1b")
        z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators())
        rec_path = f"{self.run}/b1b/{z.STYLE_RECORD_RELPATH}"
        with open(rec_path, encoding="utf-8") as f:
            rec = json.load(f)
        del rec["roles"]["KP_EXPL_EN"]
        with open(rec_path, "w", encoding="utf-8") as f:
            json.dump(rec, f)
        with self.assertRaises(z.FamilyZRunStyleMismatchStop):
            z.run_tts_stage(self.run, "b1b", plan, generators=fake_generators())

    def test_each_run_state_file_without_record_stops(self):
        for name in z.RUN_STATE_FILES:
            with self.subTest(name=name):
                lvl = f"{self.tmp}/m_{name}/run_01/a2"
                os.makedirs(f"{lvl}/audit")
                with open(f"{lvl}/audit/{name}", "w", encoding="utf-8") as f:
                    f.write("{}")
                plan, _, _ = make_plan("a2")
                calls, gens = self._no_gen()
                with self.assertRaises(z.FamilyZRunStyleMismatchStop):
                    z.run_tts_stage(f"{self.tmp}/m_{name}/run_01", "a2", plan, generators=gens)
                self.assertEqual(calls, [])
                self.assertFalse(os.path.exists(f"{lvl}/{z.STYLE_RECORD_RELPATH}"))

    def test_legacy_narrator_record_alone_is_not_a_record(self):
        lvl = f"{self.run}/a2"
        os.makedirs(f"{lvl}/audit")
        with open(f"{lvl}/{z.LEGACY_NARRATOR_STYLE_RECORD_RELPATH}", "w", encoding="utf-8") as f:
            json.dump({"style_label": "N01"}, f)
        with open(f"{lvl}/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
            f.write("{}")
        info = z.inspect_run_style_record(lvl, "a2")
        self.assertEqual(info["status"], "RUN_STATE_WITHOUT_RECORD")
        self.assertTrue(info["legacy_narrator_record_exists"])

    def test_existing_old_melos_runs_are_stopped_if_present(self):
        root = "er026_output/family_z_production_e2e_01/melos"
        found = 0
        for run in ("run_e2e_01", "run_e2e_02", "run_kgcpw_z_e2e_01"):
            for lv in ("a2", "b1b"):
                d = f"{root}/{run}/{lv}"
                if os.path.exists(f"{d}/audit/tts_generation_results.json"):
                    found += 1
                    self.assertEqual(z.inspect_run_style_record(d, lv)["status"], "RUN_STATE_WITHOUT_RECORD", d)
        if not found:
            self.skipTest("old run dirs absent")


class T7CopyAllowlistTest(unittest.TestCase):
    ALLOW = ["writer/r2.md", "writer/std.md", "writer/provenance.json", "segment_plan_a2.json", "segment_plan_b1b.json",
             "dialogue_attribution_a2.json", "speaker_table.md", "support/a2_support.json", "key_phrases/a2_result.json",
             "key_phrases/b1b/kp_explanations.json", "key_phrases/a2/keywords_canonicalized.json"]
    DENY = ["a2/audit/tts_generation_results.json", "a2/audit/review_lock_state.json", "b1b/audit/human_approved_segments.json",
            "a2/narration/full_story_part1_c1.wav", "b1b/narration/attempts/x.wav", "a2/assembly/timeline.json",
            "a2/key_phrases/keywords_canonicalized.json", "audit_stop_sentinel.jsonl", "cost_log.jsonl", "STOP", "STOP_ALL",
            "page_verify_local.json", "writer/x_pending_result.json", "a2/audit/x.consumed.json", "key_phrases/a2/keywords_snapshot.json",
            "writer/audit/anything.json", "unknown_new_file.json", "tts_generation_results.json"]

    def test_classify(self):
        for p in self.ALLOW:
            self.assertEqual(z.classify_reuse_path(p)[0], "ALLOW", p)
        for p in self.DENY:
            self.assertEqual(z.classify_reuse_path(p)[0], "DENY", p)

    def test_copy_copies_only_allowed_and_dry_run_is_default(self):
        tmp = tempfile.mkdtemp()
        try:
            src, dst = f"{tmp}/src", f"{tmp}/dst"
            for p in self.ALLOW + self.DENY:
                os.makedirs(os.path.dirname(f"{src}/{p}"), exist_ok=True)
                with open(f"{src}/{p}", "w", encoding="utf-8") as f:
                    f.write("x")
            r = z.copy_reusable_run_assets(src, dst)                      # 既定=dry-run
            self.assertTrue(r["dry_run"])
            self.assertFalse(os.path.exists(dst))
            self.assertEqual(r["would_copy"], len(self.ALLOW))
            r = z.copy_reusable_run_assets(src, dst, dry_run=False)
            self.assertEqual(r["copied"], len(self.ALLOW))
            got = sorted(os.path.relpath(os.path.join(rt, fn), dst).replace("\\", "/") for rt, _d, fs in os.walk(dst) for fn in fs)
            self.assertEqual(got, sorted(self.ALLOW))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_copy_refuses_dst_with_result_files_or_same_dir(self):
        tmp = tempfile.mkdtemp()
        try:
            os.makedirs(f"{tmp}/src")
            os.makedirs(f"{tmp}/dst/a2/audit")
            with open(f"{tmp}/dst/a2/audit/review_lock_state.json", "w", encoding="utf-8") as f:
                f.write("{}")
            with self.assertRaises(z.FamilyZRunStyleMismatchStop):
                z.copy_reusable_run_assets(f"{tmp}/src", f"{tmp}/dst", dry_run=False)
            with self.assertRaises(z.FamilyZRunStyleMismatchStop):
                z.copy_reusable_run_assets(f"{tmp}/src", f"{tmp}/src")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_allowlist_on_real_run_e2e_02_never_allows_audio_or_state(self):
        src = "er026_output/family_z_production_e2e_01/melos/run_e2e_02"
        if not os.path.isdir(src):
            self.skipTest("run_e2e_02 absent")
        plan = z.plan_reusable_run_assets(src)
        self.assertTrue(plan["allow"])
        for item in plan["allow"]:
            p = item["path"]
            self.assertFalse(p.endswith((".wav", ".mp3")), p)
            self.assertFalse(any(seg in ("audit", "narration", "assembly") for seg in p.split("/")), p)
            self.assertNotIn(os.path.basename(p), z.RUN_STATE_FILES)
            self.assertFalse(p.startswith(("a2/", "b1b/")), p)


class T8NonDependenceTest(unittest.TestCase):
    def test_changing_x_default_profile_does_not_change_z_resolution(self):
        specs = _all_plan_specs()
        before_keys = [z.build_reuse_key(s) for s in specs]
        before_styles = [z.style_text_for(s) for s in specs]
        before_record = z.expected_style_record("a2")
        x_default_before = xprof.get_profile(xprof.DEFAULT_NEW_RUN_PROFILE)
        with mock.patch.object(xprof, "DEFAULT_NEW_RUN_PROFILE", xprof.PROFILE_COFFEE_P8), \
                mock.patch.dict(xprof.STYLE_PROFILES, {xprof.PROFILE_FX_20261017: {"overrides": {"FULL_STORY": {
                    "text": "X DEFAULT CHANGED", "sha256": "f" * 64, "std_append_slower_instruction": False}}}}):
            self.assertNotEqual(xprof.get_profile(xprof.DEFAULT_NEW_RUN_PROFILE), x_default_before)
            self.assertEqual([z.build_reuse_key(s) for s in specs], before_keys)
            self.assertEqual([z.style_text_for(s) for s in specs], before_styles)
            self.assertEqual(z.expected_style_record("a2"), before_record)
            z.assert_style_table_integrity()

    def test_tampered_common_text_stops_integrity(self):
        with mock.patch.dict(z._STYLE_TEXT, {"PD06": "tampered"}):
            with self.assertRaises(z.FamilyZStyleIntegrityStop):
                z.assert_style_table_integrity()
        patched = dict(z.FAMILY_Z_ROLE_STYLE["KP_EXPL_EN"], text="tampered")
        with mock.patch.dict(z.FAMILY_Z_ROLE_STYLE, {"KP_EXPL_EN": patched}):
            with self.assertRaises(z.FamilyZStyleIntegrityStop):
                z.assert_style_table_integrity()


if __name__ == "__main__":
    unittest.main()
