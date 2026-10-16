# ============================================================
# er019_family_x_style_profile_01_n01_test_01.py
# FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_02: N01 profile(Family X)のtest(TEST_PLAN_01 N-1〜N-8)。
# API呼出なし(全てローカル純関数/tmp dir)。
# ============================================================
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest

import er019_family_x_style_profile_01 as sp
import er033_tts_flash_lite_family_x_styles_01 as fl_styles

N01_SHA = "d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477"
P8_SHA = "3eadf4f6f788b822c90f17ba56d893bccb5fab840358cf48845472cd4f4e5595"
PROMPTS_R5 = "er057_output/coffee_tts_style_h_speed_04/round5/prompts_r5.json"


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class N01ConstantTests(unittest.TestCase):
    def test_n01_sha_length_and_origin(self):  # N-1
        self.assertEqual(sp.N01_SHA256, N01_SHA)
        self.assertEqual(_sha(sp.N01_TEXT), N01_SHA)
        self.assertEqual(len(sp.N01_TEXT), 202)
        self.assertEqual(sp.N01_LENGTH, 202)
        with open(PROMPTS_R5, encoding="utf-8") as f:
            origin = json.load(f)
        cand = origin["candidates"]["N01"]["style"]
        self.assertEqual(sp.N01_TEXT, cand)  # byte一致(逐語)
        self.assertEqual(_sha(cand), N01_SHA)

    def test_n01_has_no_numeric_wpm_or_speed(self):
        import er002_common as common
        common.assert_no_wpm_specification(sp.N01_TEXT)
        low = sp.N01_TEXT.lower()
        for w in ("unhurried", "slowly", "wpm"):
            self.assertNotIn(w, low)

    def test_p8_r2_p3_constants_unchanged(self):  # N-5 後方互換
        self.assertEqual(sp.P8_SHA256, P8_SHA)
        self.assertEqual(_sha(sp.P8_TEXT), P8_SHA)
        self.assertEqual(sp.R2_SHA256, "625826c1187b6381fe36ff444f1f568fc1f68d639d6a6a8931e728463692252f")
        self.assertEqual(sp.P3_SHA256, "a8aaec591ef6d9acb42532cc0c84b6edfb2f75991e713d413c565b7e27677acc")
        self.assertIn("coffee_p8", sp.STYLE_PROFILES)
        self.assertIn("coffee_final_v5", sp.STYLE_PROFILES)

    def test_base_constant_not_rewritten_B_prime(self):
        """必須5(B'): FAMILY_X_ROLE_STYLE_EN定数(17ファイル参照)は書き換えない。"""
        self.assertEqual(fl_styles.FAMILY_X_ROLE_STYLE_EN["FULL_STORY"],
                         "calm, steady news narration with natural emphasis at key points and turns; not dramatic.")
        self.assertNotIn("sharing a true story", " ".join(fl_styles.FAMILY_X_ROLE_STYLE_EN.values()))
        self.assertNotIn(sp.N01_TEXT, fl_styles.FAMILY_X_ROLE_STYLE_EN_FALLBACK)  # N-8 fallback takeはN01ではない


class N01ProfileDefinitionTests(unittest.TestCase):
    def test_profile_n01_overrides_only_full_story(self):  # N-2
        prof = sp.get_profile(sp.PROFILE_N01)
        self.assertEqual(sorted(prof["overrides"]), ["FULL_STORY"])
        o = prof["overrides"]["FULL_STORY"]
        self.assertEqual(o["sha256"], N01_SHA)
        self.assertIs(o["std_append_slower_instruction"], False)

    def test_other_roles_pass_through(self):
        for role in ("TOPIC_INTRO", "PREVIEW", "COMMENT", "IN_ONE_LINE", "KEY_PHRASE_EXPLANATION_EN", sp.ROLE_SUPPORT_JA,
                     sp.ROLE_KP_EXPLANATION_EN):
            for level in ("a2", "b1b"):
                self.assertEqual(sp.resolve_role_style(sp.PROFILE_N01, role, level, lambda r: f"BASE:{r}"), f"BASE:{role}")

    def test_full_story_is_n01_verbatim_for_std_and_adv_no_slow_instruction(self):  # N-3
        import er003_v1_n3_01_tts_generate as n3_tts
        for level in ("a2", "b1b"):
            got = sp.resolve_role_style(sp.PROFILE_N01, "FULL_STORY", level, lambda r: "BASE")
            self.assertEqual(got, sp.N01_TEXT)
            self.assertNotIn(n3_tts.A2_SLOWER_PACE_INSTRUCTION.strip(), got)

    def test_combined_profile_n01_r2_p3(self):  # 必須6
        prof = sp.get_profile(sp.PROFILE_COFFEE_N01_R2_P3)
        ov = prof["overrides"]
        self.assertEqual(sorted(ov), sorted(["FULL_STORY", sp.ROLE_SUPPORT_JA, sp.ROLE_KP_EXPLANATION_EN]))
        self.assertEqual(ov["FULL_STORY"]["sha256"], N01_SHA)
        self.assertEqual(ov[sp.ROLE_SUPPORT_JA]["sha256"], sp.R2_SHA256)
        self.assertEqual(ov[sp.ROLE_KP_EXPLANATION_EN]["sha256"], sp.P3_SHA256)
        self.assertEqual(sp.resolve_role_style(sp.PROFILE_COFFEE_N01_R2_P3, sp.ROLE_SUPPORT_JA, "a2", lambda r: "B"), sp.R2_TEXT)
        self.assertEqual(sp.resolve_role_style(sp.PROFILE_COFFEE_N01_R2_P3, sp.ROLE_SUPPORT_JA, "b1b", lambda r: "B"), "B")
        self.assertEqual(sp.resolve_role_style(sp.PROFILE_COFFEE_N01_R2_P3, sp.ROLE_KP_EXPLANATION_EN, "b1b", lambda r: "B"), sp.P3_TEXT)
        self.assertEqual(sp.resolve_role_style(sp.PROFILE_COFFEE_N01_R2_P3, "FULL_STORY", "a2", lambda r: "B"), sp.N01_TEXT)

    def test_record_roundtrip_and_verify(self):
        for pid in (sp.PROFILE_N01, sp.PROFILE_COFFEE_N01_R2_P3, sp.PROFILE_COFFEE_P8, sp.PROFILE_COFFEE_FINAL_V5):
            rec = sp.build_record(pid)
            self.assertEqual(sp.verify_record(json.loads(json.dumps(rec))), pid)

    def test_m3_gate_n01_blocks_fallback_and_passes_normal(self):
        # FULL_STORY N01: Std fallbackはBLOCK、通常attemptはPASS(fallback合格partはN01 evidenceにしない、必須8)
        def entry(level, fallback):
            e = {"status": "OK", "fallback_used": fallback,
                 "style_profile": {"profile_id": sp.PROFILE_N01, "role": "FULL_STORY", "expected_base_sha256": N01_SHA,
                                   "style_base_sha256": N01_SHA}}
            if level == "b1b":
                e["style_prefix"] = sp.N01_TEXT
                e["instruction_type"] = "minimal_fallback" if fallback else "standard"
            else:
                e["attempts_log"] = [{"style_prefix": {"sha256": N01_SHA, "head200": sp.N01_TEXT[:200], "len": len(sp.N01_TEXT)}}]
            return e
        for level in ("a2", "b1b"):
            ok = {"segments": {f"full_story_part{i}": entry(level, False) for i in (1, 2, 3)}}
            self.assertEqual(sp.m3_assembly_gate(sp.PROFILE_N01, level, ok)["status"], "PASS", level)
            bad = {"segments": {**ok["segments"], "full_story_part2": entry(level, True)}}
            g = sp.m3_assembly_gate(sp.PROFILE_N01, level, bad)
            self.assertEqual(g["status"], "BLOCK", level)


class ResolveRunProfileTests(unittest.TestCase):
    FL = "speech_metadata_flash_lite"

    def test_new_out_dir_resolves_to_default_new_run_profile_and_records(self):
        # N-4(期待値を意図的に更新): 2026-10-16 委任_02Aで新規out_dirの既定はN01からfx_20261016へ。N01自体は
        # 明示指定[--style-profile n01]・既存記録のresumeで引き続き使える(下のtestで確認)。
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/new_run"
            pid, src = sp.resolve_run_profile(out, None, write=False, tts_backend=self.FL)
            self.assertEqual((pid, src), (sp.PROFILE_FX_20261016, "default_new_run_fx_20261016"))
            self.assertFalse(os.path.exists(sp.record_path(out)))  # write=Falseでは書かない
            pid, src = sp.resolve_run_profile(out, None, write=True, tts_backend=self.FL)
            self.assertEqual(pid, sp.PROFILE_FX_20261016)
            rec = sp.read_record(out)
            self.assertEqual(rec["profile_id"], sp.PROFILE_FX_20261016)
            self.assertEqual(rec["roles"]["FULL_STORY"]["sha256"], sp.PD06_SHA256)
            # 2回目(resume)は記録を採用
            self.assertEqual(sp.resolve_run_profile(out, None, tts_backend=self.FL), (sp.PROFILE_FX_20261016, "record"))
            # N01は明示指定で従来どおり新規作成できる(旧profileは残置)
            out2 = f"{d}/n01_run"
            pid2, src2 = sp.resolve_run_profile(out2, sp.PROFILE_N01, write=True, tts_backend=self.FL)
            self.assertEqual((pid2, src2), (sp.PROFILE_N01, "cli_new_record"))
            self.assertEqual(sp.read_record(out2)["roles"]["FULL_STORY"]["sha256"], N01_SHA)

    def test_legacy_backend_new_dir_stays_default_no_record(self):
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/legacy"
            self.assertEqual(sp.resolve_run_profile(out, None, tts_backend="structured_separation"),
                             (sp.PROFILE_DEFAULT, "default_no_record_legacy_backend"))
            self.assertFalse(os.path.exists(sp.record_path(out)))

    def test_explicit_default_is_default_no_record(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(sp.resolve_run_profile(f"{d}/x", sp.PROFILE_DEFAULT, tts_backend=self.FL),
                             (sp.PROFILE_DEFAULT, "default_no_record"))
            self.assertFalse(os.path.exists(sp.record_path(f"{d}/x")))

    def test_existing_run_state_without_record_stops_unless_explicit_default(self):  # 必須5: 課金前STOP
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/old"
            os.makedirs(f"{out}/a2/audit")
            with open(f"{out}/a2/audit/tts_generation_results.json", "w") as f:
                f.write("{}")
            with self.assertRaises(sp.StyleProfileStop) as cm:
                sp.resolve_run_profile(out, None, tts_backend=self.FL)
            self.assertIn("--style-profile default", str(cm.exception))
            self.assertFalse(os.path.exists(sp.record_path(out)))
            self.assertEqual(sp.resolve_run_profile(out, sp.PROFILE_DEFAULT, tts_backend=self.FL),
                             (sp.PROFILE_DEFAULT, "default_no_record"))

    def test_explicit_profile_existing_state_stops_m2(self):  # N-6
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/old"
            os.makedirs(f"{out}/audit")
            with open(f"{out}/audit/review_lock_state.json", "w") as f:
                f.write("{}")
            with self.assertRaises(sp.StyleProfileStop):
                sp.resolve_run_profile(out, sp.PROFILE_N01, tts_backend=self.FL)
            self.assertFalse(os.path.exists(sp.record_path(out)))

    def test_cli_conflicting_with_record_stops(self):
        with tempfile.TemporaryDirectory() as d:
            out = f"{d}/r"
            sp.resolve_run_profile(out, sp.PROFILE_COFFEE_N01_R2_P3, tts_backend=self.FL)
            with self.assertRaises(sp.StyleProfileStop):
                sp.resolve_run_profile(out, sp.PROFILE_N01, tts_backend=self.FL)
            with self.assertRaises(sp.StyleProfileStop):
                sp.resolve_run_profile(out, sp.PROFILE_DEFAULT, tts_backend=self.FL)

    def test_m5_legacy_backend_with_n01_stops(self):
        with self.assertRaises(sp.StyleProfileStop):
            sp.assert_profile_backend(sp.PROFILE_N01, "structured_separation")
        sp.assert_profile_backend(sp.PROFILE_N01, self.FL)  # 例外なし


class RunnerWiringTests(unittest.TestCase):
    def test_runner_passes_tts_backend_to_resolve_run_profile(self):
        import re
        src = open("er019_family_x_audio_production_runner_01.py", encoding="utf-8").read()
        calls = re.findall(r"resolve_run_profile\(\s*out_dir, args\.style_profile, write=(True|False), tts_backend=args\.tts_backend\)", src)
        self.assertEqual(sorted(calls), ["False", "True"])  # main()の2呼出(判定用write=False / 記録用write=True)の両方がbackendを渡す
        self.assertEqual(len(re.findall(r"resolve_run_profile\(", src)), 2)

    def test_plan_stage_records_profile_full_story_sha(self):
        import er019_family_x_audio_production_runner_01 as runner
        with tempfile.TemporaryDirectory() as d:
            src_dir = "er019_output/coffee_prices/run_v5_ms_01"
            if not os.path.exists(f"{src_dir}/a2/article.md"):
                self.fail("fixture missing")
            res = runner.run_plan_stage(src_dir, f"{d}/o", ["a2"], style_profile=sp.PROFILE_N01)
            plan = res["a2"]["style_profile_plan"]
            self.assertEqual(plan["full_story_style_sha256"], N01_SHA)
            self.assertEqual(plan["full_story_style_length"], 202)
            for part in plan["ledger_hits_web_lookup_disabled"].values():
                self.assertTrue(part["augmented_startswith_p8"])  # 互換key名(中身は適用中profileのFull Story style)

    def test_scaffold_only_kp_cli_exists(self):
        import er019_family_x_audio_production_runner_01 as runner
        p = runner.build_arg_parser()
        ns = p.parse_args(["--slug", "s", "--run", "r", "--stage", "scaffold", "--scaffold-only", "kp"])
        self.assertEqual(ns.scaffold_only, "kp")
        self.assertIsNone(p.parse_args(["--slug", "s", "--run", "r"]).scaffold_only)
        with self.assertRaises(SystemExit):
            p.parse_args(["--slug", "s", "--run", "r", "--scaffold-only", "support"])


if __name__ == "__main__":
    unittest.main()
