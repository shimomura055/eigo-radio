# -*- coding: utf-8 -*-
"""FAMILY-Y-STYLE-PROFILE-FIX-01 委任_02: OPEN-537(Y runnerが承認Style profileを供給せず"default"だった)是正と再発防止のtest。API 0・実client生成block(runner testと同じharness)。

検査: (1)承認profile=fx_20261017の固定(Xの既定と一致・6 roleのsha/長さを承認スナップショットと照合=drift) (2)静的配線(AST: resolve_run_profile/assert_profile_backend呼出・
"default"リテラル/旧STYLE_PROFILE/migrate_recordの不在・generate_y_*のstyle_profile既定値なし・課金前の解決順) (3)runnerのprofile解決(固定記録・M2 STOP・未解決stageはSTOP)
(4)Y Gateのfail-closed(記録欠落/不一致/承認外/引数不一致/role網羅の完全一致[Opus M-1]/日本語roleの実測[Opus M-4]/Adv・Std本文のStyle) (5)送信Styleの実測(PD06/E1/S3/K2/P7/P8-KP)
(6)横断登録表(R-7: Family runnerを列挙し未登録ならFAIL)。
"""
from __future__ import annotations

import ast
import glob
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from er121_family_y_runner_01_test_01 import setUpModule, tearDownModule, BLOCK, _ctx, _declare, _quiet  # noqa: E402,F401  (遮断harnessを共有)
import er019_family_x_style_profile_01 as xprof  # noqa: E402
import er121_family_y_audio_01 as ya  # noqa: E402
import er121_family_y_runner_01 as r  # noqa: E402

APPROVED = "fx_20261017"
SNAPSHOT = os.path.join(ROOT, "docs", "research", "FAMILY-Y-STYLE-PROFILE-FIX-01", "style_matrix_01.json")
# 承認済み6 roleのsha256先頭8桁/長さ/level(DESIGN_01[LAUNCH-01]:84・A19・STYLE_MATRIX_01。Xの承認profile fx_20261017と一致。変更=承認変更)
APPROVED_ROLES = {
    "FULL_STORY": ("3a680861", 177, ["a2", "b1b"]),
    "SUPPORT_JA": ("060c08fd", 199, ["a2"]),
    "PREVIEW": ("8862317f", 68, ["b1b"]),
    "KP_EN": ("9d905cfe", 332, ["a2", "b1b"]),
    "KP_JA_MEANING": ("b12c8721", 93, ["a2"]),
    "KP_EXPLANATION_EN": ("05180006", 136, ["b1b"]),
}


def _src(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return f.read()


class TestApprovedProfileDrift(unittest.TestCase):
    def test_y_approved_profile_is_literal_and_equals_x_default(self):
        self.assertEqual(ya.Y_APPROVED_STYLE_PROFILE, APPROVED)
        self.assertEqual(ya.Y_APPROVED_STYLE_PROFILE, xprof.DEFAULT_NEW_RUN_PROFILE)       # Xの既定が変わればYが落ち、Y側の承認判断を強制する(自動追従しない)

    def test_six_roles_match_approved_snapshot(self):
        ov = xprof.get_profile(APPROVED)["overrides"]
        self.assertEqual(sorted(ov), sorted(APPROVED_ROLES))
        for role, (pre, ln, levels) in APPROVED_ROLES.items():
            self.assertTrue(ov[role]["sha256"].startswith(pre), role)
            self.assertEqual(len(ov[role]["text"]), ln, role)
            self.assertEqual(list(xprof.ROLE_LEVELS[role]), levels, role)
        with open(SNAPSHOT, encoding="utf-8") as f:
            snap = json.load(f)["roles"]
        for role, (pre, ln, levels) in APPROVED_ROLES.items():
            self.assertEqual((snap[role]["sha256_prefix"], snap[role]["len"], snap[role]["levels"]), (pre, ln, levels), role)

    def test_y_role_coverage_equals_profile_roles_and_levels(self):
        self.assertEqual(sorted(ya.Y_ROLE_COVERAGE), sorted(xprof.overridden_roles(APPROVED)))
        for role, lv in ya.Y_ROLE_COVERAGE.items():
            self.assertEqual(sorted(lv), sorted(xprof.ROLE_LEVELS[role]), role)         # Yのlevelは承認profileのlevelと矛盾しない
        self.assertEqual(len(ya.y_expected_coverage("b1b")), 8 + 1 + 3 + 3)         # 本文8+Preview+KP英語3+KP解説3
        self.assertEqual(len(ya.y_expected_coverage("a2")), 8 + 4 + 3 + 3)          # 本文8+日本語補助4(preview+comment_1..3)+KP英語3+KP日本語意味3


class TestStaticWiring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = _src("er121_family_y_runner_01.py")
        cls.audio = _src("er121_family_y_audio_01.py")
        cls.mock_src = _src("er121_family_y_mock_01.py")

    def test_old_module_constant_style_profile_is_removed(self):
        tree = ast.parse(self.runner)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        self.assertNotIn("STYLE_PROFILE", names)
        self.assertFalse(hasattr(r, "STYLE_PROFILE"))

    def test_no_default_string_literal_in_runner_audio_mock(self):
        for label, src in (("runner", self.runner), ("audio", self.audio), ("mock", self.mock_src)):
            hits = [n.lineno for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Constant) and n.value == "default"]
            self.assertEqual(hits, [], f"{label}: style_profileへ'default'を渡す経路を作らない: lines {hits}")

    def test_runner_calls_resolve_and_backend_assert_and_never_migrates(self):
        called = {n.func.attr for n in ast.walk(ast.parse(self.runner)) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
        self.assertTrue({"resolve_run_profile", "assert_profile_backend", "read_record", "verify_record"} <= called, called)
        for label, src in (("runner", self.runner), ("audio", self.audio), ("mock", self.mock_src)):
            tree = ast.parse(src)
            used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
            self.assertNotIn("migrate_record", used, f"{label}: 同一dirのprofile移行はYでは使用禁止(日本語roleの照合が自己一致になる。Opus見落とし1)")

    def test_generate_functions_have_required_keyword_style_profile(self):
        for fn in (ya.generate_y_b1_segments, ya.generate_y_a2_segments, ya.assemble_level):
            p = inspect.signature(fn).parameters["style_profile"]
            self.assertIs(p.default, inspect.Parameter.empty, fn.__name__)
            self.assertEqual(p.kind, inspect.Parameter.KEYWORD_ONLY, fn.__name__)

    def test_profile_is_resolved_before_billing_side_effects(self):
        fn = next(n for n in ast.walk(ast.parse(self.runner)) if isinstance(n, ast.FunctionDef) and n.name == "build_real_context")
        calls = {}
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                nm = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else None)
                if nm:
                    calls.setdefault(nm, n.lineno)
        self.assertLess(calls["_launch_guard"], calls["resolve_style_profile"])
        for later in ("load_dotenv", "install", "get_client"):
            self.assertLess(calls["resolve_style_profile"], calls[later], later)

    def test_stages_use_resolved_profile_not_literals(self):
        tree = ast.parse(self.runner)
        for n in ast.walk(tree):
            if isinstance(n, ast.keyword) and n.arg == "style_profile":
                self.assertFalse(isinstance(n.value, ast.Constant), f"line {n.value.lineno}: style_profileに定数を直渡ししない")
        for fname in ("stage_tts", "stage_gate", "stage_assemble", "_tts_input_sha"):
            fn = next(x for x in ast.walk(tree) if isinstance(x, ast.FunctionDef) and x.name == fname)
            called = {c.func.id for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)}
            self.assertIn("_style_profile", called, f"{fname}はctxの解決済みprofile(固定記録で再検証)を使う")


class TestRunnerResolve(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="y_sp_resolve_")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_mock_context_resolves_and_writes_fixed_record(self):
        ctx = _ctx(self.root)
        self.assertEqual(ctx.style_profile, APPROVED)
        rec = xprof.read_record(ctx.out_dir)
        self.assertEqual(rec["profile_id"], APPROVED)
        self.assertEqual(xprof.verify_record(rec), APPROVED)
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/audit/style_profile.json"))

    def test_second_resolve_uses_record(self):
        ctx = _ctx(self.root)
        pid, src = (r.resolve_style_profile(ctx), ctx.style_profile_source)
        self.assertEqual((pid, src), (APPROVED, "record"))

    def test_existing_run_state_without_record_stops_before_billing(self):
        d = os.path.join(self.root, "slug", "run_old")
        os.makedirs(f"{d}/b1b/audit")
        with open(f"{d}/b1b/audit/tts_generation_results.json", "w", encoding="utf-8") as f:
            json.dump({"segments": {}}, f)
        ctx = r.YContext(slug="slug", run="run_old", mode="mock", run_root=self.root)
        with self.assertRaises(r.YE2EStop) as e:
            r.resolve_style_profile(ctx)
        self.assertIn("FAMILY_Y_STYLE_PROFILE_STOP", str(e.exception))
        self.assertIn("M2", str(e.exception))
        self.assertFalse(os.path.exists(f"{d}/audit/style_profile.json"))      # 記録は作らない(旧runへStyle混在を作らない)
        self.assertIsNone(ctx.style_profile)

    def test_record_with_other_profile_stops(self):
        ctx = _ctx(self.root)
        with open(f"{ctx.out_dir}/audit/style_profile.json", "w", encoding="utf-8") as f:
            json.dump(xprof.build_record("fx_20261016"), f)
        ctx2 = r.YContext(slug=ctx.slug, run=ctx.run, mode="mock", run_root=self.root)
        with self.assertRaises(r.YE2EStop):
            r.resolve_style_profile(ctx2)

    def test_stage_functions_stop_when_profile_unresolved(self):
        ctx = r.YContext(slug="s", run="r", mode="mock", run_root=self.root)
        for fn in (r.stage_gate, r.stage_assemble):
            with self.assertRaises(r.YE2EStop) as e:
                fn(ctx)
            self.assertTrue("FAMILY_Y_STYLE_PROFILE_NOT_RESOLVED" in str(e.exception) or "FAMILY_Y_STAGE_NOT_FRESH" in str(e.exception), str(e.exception)[:200])
        with self.assertRaises(r.YE2EStop) as e:
            r._style_profile(ctx)
        self.assertIn("FAMILY_Y_STYLE_PROFILE_NOT_RESOLVED", str(e.exception))

    def test_dry_run_plan_reports_profile_without_writing(self):
        ctx = r.YContext(slug="s", run="r_dry", mode="dry-run", run_root=self.root)
        self.assertEqual(r.resolve_style_profile(ctx, write=False), APPROVED)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/audit/style_profile.json"))


class Base(unittest.TestCase):
    """一度だけ全stage(gateまで)を通し、成果物を各testがcopyして破壊的に検査する。"""
    base_root = None
    base_ctx = None

    @classmethod
    def setUpClass(cls):
        cls.base_root = tempfile.mkdtemp(prefix="y_sp_base_")
        cls.base_ctx = _ctx(cls.base_root)
        with _quiet():
            r.run_stages(cls.base_ctx, ["seed_check", "text", "translate", "support"])
            _declare(cls.base_ctx)
            r.run_stages(cls.base_ctx, ["kp", "tts_b1b", "tts_a2", "gate"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base_root, ignore_errors=True)

    def setUp(self):
        self.work = tempfile.mkdtemp(prefix="y_sp_work_")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.out = os.path.join(self.work, "run")
        shutil.copytree(self.base_ctx.out_dir, self.out)

    @staticmethod
    def rj(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def wj(p, d):
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)

    def res_path(self, lv):
        return f"{self.out}/{lv}/audit/tts_generation_results.json"

    def mutate(self, lv, fn):
        d = self.rj(self.res_path(lv))
        fn(d)
        self.wj(self.res_path(lv), d)

    def gate(self, lv, profile=APPROVED):
        with _quiet():
            return ya.y_style_gate(self.out, lv, profile)

    def reasons(self, g):
        out = set()
        for key in ("y_body_blocked", "x_gate_blocked_after_filter", "y_profile_blocked"):
            for b in g.get(key) or []:
                out.update(b.get("violations") or [b.get("reason")])
        return out


class TestGatePassAndEvidence(Base):
    def test_both_levels_pass_with_full_coverage_and_all_match_table(self):
        for lv, n in (("b1b", 15), ("a2", 18)):
            g = self.gate(lv)
            self.assertEqual(g["status"], "PASS", self.reasons(g))
            self.assertEqual(g["coverage"]["expected_count"], n)
            self.assertEqual(g["coverage"]["evaluated_count"], n)
            self.assertEqual((g["coverage"]["missing"], g["coverage"]["unexpected"]), ([], []))
            tbl = self.rj(f"{self.out}/{lv}/audit/style_actual_vs_approved.json")
            self.assertTrue(tbl["all_match"])
            self.assertGreaterEqual(tbl["rows_count"], n)
            self.assertTrue(all(row["match"] is True for row in tbl["rows"]))

    def test_stage_gate_wrote_combined_actual_vs_approved_table(self):
        t = self.rj(f"{self.base_ctx.out_dir}/audit/style_actual_vs_approved.json")
        self.assertEqual(t["profile_id"], APPROVED)
        self.assertTrue(t["all_match"])
        self.assertEqual(sorted(t["levels"]), ["a2", "b1b"])
        gs = self.rj(f"{self.base_ctx.out_dir}/gate_summary.json")
        self.assertEqual({lv: v["status"] for lv, v in gs.items()}, {"b1b": "PASS", "a2": "PASS"})

    def test_sent_styles_are_the_approved_ones(self):
        ov = xprof.get_profile(APPROVED)["overrides"]
        b = self.rj(self.res_path("b1b"))
        a = self.rj(self.res_path("a2"))
        for sid in ("y_lead", "y_intro_1", "y_voice_1", "y_intro_2", "y_voice_2", "y_intro_3", "y_voice_3", "y_closing"):
            self.assertTrue(b["segments"][sid]["style_prefix"].startswith(ov["FULL_STORY"]["text"]), sid)      # Adv: Voice 1〜3本文を含めPD06
            self.assertEqual(a["segments"][sid]["style_prefix"], ov["FULL_STORY"]["text"], sid)              # Std: PD06逐語(減速は生成後6%)
            self.assertTrue(a["segments"][sid]["slowdown_applied"], sid)
        self.assertTrue(b["segments"]["preview"]["style_prefix"].startswith(ov["PREVIEW"]["text"]))
        for n in ("preview", "comment_1", "comment_2", "comment_3"):
            self.assertEqual(a["segments"][n]["style_prefix"], ov["SUPPORT_JA"]["text"], n)
        for rank in ("1", "2", "3"):
            self.assertEqual(b["key_phrases"][rank]["english"]["style_prefix"], ov["KP_EN"]["text"])
            self.assertEqual(b["key_phrases"][rank]["explanation"]["style_prefix"], ov["KP_EXPLANATION_EN"]["text"])
            self.assertEqual(a["key_phrases"][rank]["japanese_meaning"]["style_prefix"], ov["KP_JA_MEANING"]["text"])
        self.assertNotIn("comment_2", b["segments"])      # Adv Comment 2は削除維持


class TestGateFailClosed(Base):
    def test_record_missing_blocks_and_assembly_refuses(self):
        os.remove(f"{self.out}/audit/style_profile.json")
        g = self.gate("b1b")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("Y_STYLE_PROFILE_RECORD_MISSING", self.reasons(g))
        with _quiet():
            s = ya.assemble_level(self.out, "b1b", style_profile=APPROVED, slug="s", article_text="x")
        self.assertEqual(s["status"], "BLOCKED_STYLE_PROFILE_GATE")

    def test_record_sha_tampered_blocks(self):
        p = f"{self.out}/audit/style_profile.json"
        rec = self.rj(p)
        rec["roles"]["FULL_STORY"]["sha256"] = "0" * 64
        self.wj(p, rec)
        g = self.gate("a2")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("Y_STYLE_PROFILE_RECORD_MISMATCH", self.reasons(g))

    def test_unapproved_record_profile_blocks(self):
        self.wj(f"{self.out}/audit/style_profile.json", xprof.build_record("fx_20261016"))
        g = self.gate("b1b", "fx_20261016")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("Y_STYLE_PROFILE_NOT_APPROVED", self.reasons(g))

    def test_default_profile_argument_blocks_no_legacy_waiver(self):
        for lv in ("b1b", "a2"):
            g = self.gate(lv, "default")
            self.assertEqual(g["status"], "BLOCK")
            self.assertTrue({"Y_STYLE_PROFILE_NOT_APPROVED", "Y_STYLE_PROFILE_ARG_DISAGREES_WITH_RECORD"} <= self.reasons(g), self.reasons(g))
        self.assertFalse(os.path.exists(f"{self.out}/audit/style_profile_waiver.json"))

    def test_default_record_blocks_and_unreadable_record_blocks(self):
        self.wj(f"{self.out}/audit/style_profile.json", xprof.build_record("default"))      # 旧default記録(承認外)
        g0 = self.gate("b1b", "default")
        self.assertEqual(g0["status"], "BLOCK")
        self.assertIn("Y_STYLE_PROFILE_NOT_APPROVED", self.reasons(g0))
        with open(f"{self.out}/audit/style_profile.json", "w", encoding="utf-8") as f:
            f.write("{ broken")
        g = self.gate("b1b")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("Y_STYLE_PROFILE_RECORD_UNREADABLE", self.reasons(g))

    def test_opus_m1_empty_body_coverage_blocks_even_though_x_checked_is_nonempty(self):
        """Opus M-1の再現: Xのcheckedはfull_story_part*等のX名で埋まるため、Y本文が0件でも『checked>=1』は満たされる。Y期待集合との完全一致で必ずBLOCKする。"""
        self.mutate("b1b", lambda d: [d["segments"].pop(s) for s in list(ya.ys.Y_SEGMENT_IDS)])
        g = self.gate("b1b")
        self.assertTrue(g["x_gate"]["checked"])
        self.assertEqual(g["status"], "BLOCK")
        miss = {tuple(x) for x in g["coverage"]["missing"]}
        self.assertEqual({n for role, n in miss if role == "FULL_STORY"}, set(ya.ys.Y_SEGMENT_IDS))
        self.assertIn("Y_STYLE_COVERAGE_EMPTY", self.reasons(g))

    def test_missing_kp_entry_blocks_with_named_coverage(self):
        self.mutate("b1b", lambda d: d["key_phrases"]["1"].pop("english"))
        g = self.gate("b1b")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn(["KP_EN", "kp1_english"], g["coverage"]["missing"])

    def test_missing_one_body_segment_blocks(self):
        self.mutate("a2", lambda d: d["segments"].pop("y_voice_1"))
        g = self.gate("a2")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn(["FULL_STORY", "y_voice_1"], g["coverage"]["missing"])

    def test_role_table_drift_and_unexpected_coverage_block(self):
        cov = dict(ya.Y_ROLE_COVERAGE)
        cov.pop("KP_EN")
        with mock.patch.object(ya, "Y_ROLE_COVERAGE", cov):
            g = self.gate("b1b")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("Y_STYLE_ROLE_TABLE_DRIFT", self.reasons(g))
        cov2 = {**ya.Y_ROLE_COVERAGE, "KP_EN": {"b1b": ya.Y_ROLE_COVERAGE["KP_EN"]["b1b"]}}
        with mock.patch.object(ya, "Y_ROLE_COVERAGE", cov2):
            g2 = self.gate("a2")
        self.assertEqual(g2["status"], "BLOCK")
        self.assertIn("Y_STYLE_COVERAGE_UNEXPECTED", self.reasons(g2))

    def test_adv_body_with_old_default_style_blocks(self):
        self.mutate("b1b", lambda d: d["segments"]["y_voice_2"].update({"style_prefix": "calm, steady news narration, not dramatic."}))
        g = self.gate("b1b")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED", self.reasons(g))

    def test_std_body_with_other_style_blocks(self):
        self.mutate("a2", lambda d: d["segments"]["y_intro_1"].update({"style_prefix": "calm, steady news narration."}))
        g = self.gate("a2")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("FINAL_STYLE_SHA_MISMATCH_NO_HINT", self.reasons(g))

    def test_adv_minimal_fallback_and_std_fallback_block(self):
        self.mutate("b1b", lambda d: d["segments"]["y_lead"].update({"instruction_type": "minimal_fallback"}))
        self.assertIn("ADV_MINIMAL_FALLBACK", self.reasons(self.gate("b1b")))
        self.mutate("a2", lambda d: d["segments"]["y_lead"].update({"fallback_used": True}))
        self.assertIn("STD_FALLBACK_USED_OR_UNKNOWN", self.reasons(self.gate("a2")))

    def test_japanese_role_measured_from_sent_instruction_not_from_intended_sha(self):
        """Opus M-4/見落とし1: 再利用entryはstyle_profile記録(意図sha)が現行profileで上書きされ自己一致する。送信instruction(style_prefix)が旧Styleなら必ずBLOCK。"""
        self.mutate("a2", lambda d: d["segments"]["comment_1"].update({"style_prefix": "古い既定のStyle"}))
        g = self.gate("a2")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("JA_STYLE_ACTUAL_MISMATCH", self.reasons(g))
        row = next(x for x in self.rj(f"{self.out}/a2/audit/style_actual_vs_approved.json")["rows"] if x["segment"] == "comment_1")
        self.assertFalse(row["match"])
        self.assertEqual(row["measured_kind"], "style_prefix(送信instruction実測)")

    def test_japanese_role_without_measurement_is_not_treated_as_match(self):
        self.mutate("a2", lambda d: d["key_phrases"]["2"]["japanese_meaning"].pop("style_prefix"))
        g = self.gate("a2")
        self.assertEqual(g["status"], "BLOCK")
        self.assertIn("JA_STYLE_ACTUAL_UNMEASURED", self.reasons(g))
        tbl = self.rj(f"{self.out}/a2/audit/style_actual_vs_approved.json")
        row = next(x for x in tbl["rows"] if x["segment"] == "kp2_japanese_meaning")
        self.assertEqual((row["measured_kind"], row["match"], row["measured_sha256"]), ("意図sha(実測なし)", False, None))
        self.assertFalse(tbl["all_match"])

    def test_local_rewrite_recovery_still_blocks(self):
        self.mutate("b1b", lambda d: d["segments"]["y_voice_3"].update({"local_rewrite_recovery": {"mock": True}}))
        self.assertIn("LOCAL_REWRITE_RECOVERY", self.reasons(self.gate("b1b")))

    def test_assembly_refuses_when_gate_blocks(self):
        self.mutate("b1b", lambda d: d["segments"]["y_voice_2"].update({"style_prefix": "x"}))
        with _quiet():
            s = ya.assemble_level(self.out, "b1b", style_profile=APPROVED, slug="s", article_text="x")
        self.assertEqual(s["status"], "BLOCKED_STYLE_PROFILE_GATE")


class TestCrossFamilyRegistry(unittest.TestCase):
    """R-7(Opus): 横断の登録表。Family(X/Y/Z)のProduction runnerを列挙し、登録表に無い新runnerはFAIL=新Familyの未配線を機械検出する。
    登録のkind: 'audio_style'=Style承認値の供給/検査機構を持つ(markerがソースに存在すること) / 'exempt'=TTS音声のStyle供給を持たない(理由必須)。"""
    REGISTRY = {
        "er019_family_x_audio_production_runner_01.py": ("X", "audio_style", ["resolve_run_profile", "assert_profile_backend", "m3_assembly_gate"]),
        "er026_family_z_fiction_production_runner_01.py": ("Z", "audio_style", ["assert_style_table_integrity"]),
        "er121_family_y_runner_01.py": ("Y", "audio_style", ["resolve_style_profile", "resolve_run_profile", "y_style_gate", "Y_APPROVED_STYLE_PROFILE"]),
        "er019_family_x_entertainment_production_runner_01.py": ("X", "exempt", "Entertainment系統の調査/Writer工程(音声Style供給なし。音声はer019_family_x_audio_production_runner_01経由)"),
        "er019_family_x_pointless_runner_01.py": ("X", "exempt", "Trial専用runner(DEV/Trial path。Production正式経路ではない)"),
    }

    def test_every_family_xyz_runner_is_registered(self):
        found = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "er[0-9]*_family_[xyz]_*runner_01.py")) if "test" not in os.path.basename(p))
        unregistered = [f for f in found if f not in self.REGISTRY]
        self.assertEqual(unregistered, [], f"未登録のFamily runner: {unregistered}。登録表(Family/承認Style供給・検査のmarker or 免除理由)を追加し、Style配線を確認すること")

    def test_registered_audio_runners_still_contain_their_style_markers(self):
        for fname, (fam, kind, marker) in self.REGISTRY.items():
            self.assertTrue(os.path.exists(os.path.join(ROOT, fname)), fname)
            if kind == "audio_style":
                src = _src(fname)
                for m in marker:
                    self.assertIn(m, src, f"{fam}: {fname} から Style配線marker '{m}' が消えている")
            else:
                self.assertTrue(isinstance(marker, str) and marker.strip(), f"{fname}: 免除には理由が必要")

    def test_y_registered_coverage_table_is_the_gate_expected_set(self):
        self.assertTrue(ya.Y_ROLE_COVERAGE)
        self.assertEqual(sorted(ya.Y_ROLE_COVERAGE), sorted(xprof.overridden_roles(ya.Y_APPROVED_STYLE_PROFILE)))


if __name__ == "__main__":
    unittest.main()
