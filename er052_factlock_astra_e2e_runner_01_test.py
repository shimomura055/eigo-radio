# -*- coding: utf-8 -*-
"""FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05: 2腕E2E runner の単体テスト(API 0。dry-runはstub)。
実行: .venv/Scripts/python.exe -X utf8 -m unittest er052_factlock_astra_e2e_runner_01_test -v
前半=純関数・G0・予算・env隔離の単体テスト(数秒)、後半=stub dry-run(子process起動、1シナリオ 20〜60秒)。"""
from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

import er052_factlock_astra_e2e_runner_01 as R

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.join(HERE, "er052_factlock_astra_e2e_runner_01.py")
FL = "er052_output/factlock_writer_trial_01"


def read_assigned_str(path: str, name: str) -> str:
    tree = ast.parse(open(os.path.join(HERE, path), encoding="utf-8").read())
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == name for t in n.targets):
            return ast.literal_eval(n.value)
    raise KeyError(name)


class VerbatimAndPureFunctionTest(unittest.TestCase):
    def test_astra_user_message_verbatim_with_matrix(self):
        for p in (f"{FL}/astra_revise_matrix_01/tools/run_matrix.py", f"{FL}/astra_revise_matrix_02/tools/run_matrix2.py"):
            self.assertEqual(R.USER_TMPL, read_assigned_str(p, "USER_TMPL"), p)

    def test_prompts_unchanged_against_recorded_manifest(self):
        import er019_family_x_ja_writer_o_r1_r2_01 as jaw
        import er052_factlock_writer_trial_01_run as fl
        man = json.load(open(os.path.join(HERE, f"{FL}/runs/hormuz/control/b2__factlock__r1/manifest.json"), encoding="utf-8"))["prompt_sha256"]
        self.assertEqual(R.sha_text(jaw.R0_PROMPT), man["R0_PROMPT"])
        self.assertEqual(R.sha_text(fl.build_r0_block(jaw.CONCRETENESS_CONTROL_AN3_BLOCK)), man["FACTLOCK_R0_BLOCK"])
        self.assertEqual(R.sha_text(fl.FACTLOCK_REVISION_BLOCK), man["FACTLOCK_REVISION_BLOCK"])
        self.assertNotIn("R0_PROMPT =", open(RUNNER, encoding="utf-8").read())      # runnerはPromptを再定義しない

    def test_post_processors_same_as_originals(self):
        import er052_step2_astra_r3_01_run as H
        raw = "# 見出し\n\n**強調**と——ダッシュ。\n---\n- 箇条\n\n\n\n本文……終わり。\n"
        self.assertEqual(R.strip_markdown(raw), H.strip_markdown(raw))
        self.assertEqual(R.dash_to_comma(raw), H.dash_to_comma(raw))

    def test_postprocess_ellipsis_dash_markdown(self):
        out = R.postprocess_ja("# 題名\n\n**太字**だ……そして続く——ここ。\n終わり……\n")
        self.assertNotIn("…", out)
        self.assertNotIn("——", out)
        self.assertNotIn("**", out)
        self.assertNotIn("#", out)
        self.assertIn("太字だ、そして続く、ここ。", out)

    def test_parse_brief_md_same_as_dev(self):
        import er052_open233_polysemy_nb_dev_01 as dev
        for t in ("meta", "hormuz", "space_weapons"):
            txt = open(os.path.join(HERE, f"{FL}/briefs/{t}/b2/selected_brief_factlock.md"), encoding="utf-8").read()
            self.assertEqual(R.parse_brief_md(txt), dev.parse_brief_md(txt))
            self.assertEqual(R.parse_brief_md(txt.replace("\n", "\r\n")), dev.parse_brief_md(txt))

    def test_tag_strip_single_path_and_leak_detection(self):
        dirty = "題名\n\n文です。【事実1】別の文。【事実 2】三つ目。【F3】四つ目。【中核数値】五つ目。【周辺数値】\n【速報】は残る。"
        clean = R.clean_ja_for_next(dirty)
        self.assertFalse(R.TAG_LEAK_RE.search(clean))
        self.assertIn("【速報】", clean)
        with self.assertRaises(R.TagLeak):
            R.assert_no_tag_leak("本文【事実3】が残った")

    def test_r0_echo_detection_on_known_case_and_clean(self):
        p = os.path.join(HERE, f"{FL}/runs/hormuz/control/b2__factlock__r1/ja_writer/original_with_tags.md")
        if os.path.exists(p):    # ホルムズ b2 r1 のR0は復唱が出る実例(DESIGN 4節(b))
            self.assertTrue(R.detect_r0_echo(R.rdt(p))["echo_anywhere"])
        self.assertFalse(R.detect_r0_echo("題名\n\nきょうの話です。普通に始まります。")["echo_anywhere"])
        self.assertTrue(R.detect_r0_echo("題名\n\nこれ、ちょっと面白くない？と思った。")["echo_in_head120"])

    def test_dynamic_fixture_keys_match_real_fixture_and_instance(self):
        import er050_gpt6_checker_comparison_trial_01 as g6
        p = os.path.join(HERE, "er019_output/family_x_refresh_e2e_01/meta/run_03/b1b/audit/deviation_checks/advanced_attempt1.json")
        if not os.path.exists(p):
            self.skipTest("real fixture source missing")
        real = g6.load_audit_fixture("x", p, "gold")
        fx = R.make_fixture("t", "L", "A", "J")
        self.assertEqual(set(fx), set(real))
        self.assertIsNone(fx["baseline_parsed"])
        self.assertTrue(fx["include_related_fact_id"] and not fx["hook_aware"])
        inst = R.make_instance(fx)
        import er052_open233_e2e_acceptance_01 as old
        ref = next(iter(old.prepare_instances().values()))
        self.assertLessEqual({"instance_id", "fixture", "stage1_mode", "stage1_source", "substitute_baseline_on_stage1_miss", "s1u_eligible"}, set(inst))
        self.assertEqual(inst["stage1_mode"], "fresh")
        self.assertFalse(inst["substitute_baseline_on_stage1_miss"] or inst["s1u_eligible"])
        self.assertLessEqual({"instance_id", "fixture", "stage1_mode", "stage1_source"}, set(ref))

    def test_stage_ok(self):
        d = tempfile.mkdtemp()
        try:
            for name, data, ok in (("a.md", b"x", True), ("b.md", b"", False), ("c.md", b"a\x00b", False), ("d.json", b"{bad", False), ("e.json", b"{}", True)):
                open(f"{d}/{name}", "wb").write(data)
                self.assertEqual(R.stage_ok(f"{d}/{name}"), ok, name)
            self.assertFalse(R.stage_ok(f"{d}/nope.md"))
        finally:
            shutil.rmtree(d)


class EnvIsolationTest(unittest.TestCase):
    def _ctx(self, stub=True):
        return types.SimpleNamespace(stub=stub)

    def test_old_env_has_no_flags_new_env_has_m1_m3_not_m2(self):
        saved = {k: os.environ.pop(k, None) for k in R.FLAG_KEYS}
        try:
            os.environ["OPEN243_M1"] = "1"      # 親の汚染: 子には持ち越さない
            eo, en = R.build_env(self._ctx(), "old", "x/old"), R.build_env(self._ctx(), "new", "x/new")
            for k in ("OPEN243_M1", "OPEN243_M2", "OPEN233_RECLASSIFY_PROTECT_FLAGS"):
                self.assertNotIn(k, eo)
            self.assertEqual((en["OPEN243_M1"], en["OPEN233_RECLASSIFY_PROTECT_FLAGS"]), ("1", "changed_actor"))
            self.assertNotIn("OPEN243_M2", en)
            self.assertNotEqual(eo["OPEN243_G3_TELEMETRY_PATH"], en["OPEN243_G3_TELEMETRY_PATH"])
        finally:
            for k, v in saved.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    def test_mismatch_is_provenance_violation(self):
        with self.assertRaises(R.ProvenanceViolation):
            R.assert_arm_env("old", {"OPEN243_M1": "1"})
        with self.assertRaises(R.ProvenanceViolation):
            R.assert_arm_env("new", {"OPEN243_M1": "1"})                      # M3欠落
        with self.assertRaises(R.ProvenanceViolation):
            R.assert_arm_env("new", {**R.ARM_FLAGS["new"], "OPEN243_M2": "1"})  # M2はOFF固定


class PricingAndBudgetTest(unittest.TestCase):
    def test_row_cost_matches_efam_and_astra_registered(self):
        import er012_e_family_entertainment_two_level_runner_01 as efam
        d = tempfile.mkdtemp()
        try:
            rows = [{"provider": "openai", "model_id": "gpt-6-luna", "input_tokens": 1000, "output_tokens": 500},
                    {"provider": "openai", "model_id": "gpt-6-astra-2026-10", "input_tokens": 700, "output_tokens": 1500},
                    {"provider": "openai", "model_id": "gpt-6-luna", "input_tokens": 10, "output_tokens": 10, "web_search_call_count": 3}]
            p = f"{d}/raw_usage_log.jsonl"
            for r in rows:
                R.append_jsonl(p, r)
            mine = sum(R.row_cost_usd(r) for r in rows) * 160
            rows_efam = [dict(r, model_id=("gpt-6-astra" if "astra" in r["model_id"] else r["model_id"])) for r in rows]
            for r in rows_efam:
                R.append_jsonl(f"{d}/e.jsonl", r)
            jpy, _ = efam.compute_cost_jpy_so_far(f"{d}/e.jsonl")
            self.assertAlmostEqual(mine, jpy, places=6)
            raw, guard = R.arm_cost(d, 1.5)
            self.assertAlmostEqual(raw, mine, places=6)
            self.assertGreater(guard, raw)                  # astra行だけ x1.5
        finally:
            shutil.rmtree(d)

    def test_unregistered_model_stops(self):
        with self.assertRaises(R.GlobalStop):
            R.row_cost_usd({"provider": "openai", "model_id": "gpt-99-mystery", "input_tokens": 1, "output_tokens": 1})

    def test_budget_guard_cross_worker_reservation_cap_and_alert(self):
        d = tempfile.mkdtemp()
        try:
            g1, g2 = R.BudgetGuard(d, 1, cap=100, alert=80), R.BudgetGuard(d, 2, cap=100, alert=80)
            r1 = g1.reserve("t", "new", "new_r1", 20.0, astra=True)              # 20 x 1.5 = 30
            self.assertAlmostEqual(g2.totals()["open_reserved_jpy"], 30.0)         # 他workerの予約が見える
            g2.reserve("t2", "old", "old_ja", 40.0)
            with self.assertRaises(R.GlobalStop):                                  # 30+40+31 > 100
                g1.reserve("t3", "new", "new_r2", 31.0)
            g1.settle(r1, "t", "new", "new_r1", 18.0, 27.0)
            t = g2.totals()
            self.assertAlmostEqual(t["settled_guard_jpy"], 27.0)
            self.assertAlmostEqual(t["total_jpy"], 67.0)
            self.assertFalse(g1.alert_reached())
            g1.reserve("t4", "old", "x", 20.0)
            self.assertTrue(g2.alert_reached())                                    # 87 >= 80
        finally:
            shutil.rmtree(d)


class StateAndForbiddenTest(unittest.TestCase):
    def test_arm_state_reset(self):
        d = tempfile.mkdtemp()
        try:
            st = R.ArmState(d)
            st.add("stage_done", stage="a")
            st.add("stage_stop", stage="b")
            self.assertEqual((st.status("a"), st.status("b"), st.status("c")), ("done", "stop", None))
            st.add("reset", stages=["a"])
            self.assertIsNone(st.status("a"))
            st.add("b1_recovery")
            self.assertEqual(st.count("b1_recovery"), 1)
        finally:
            shutil.rmtree(d)

    def test_provenance_records_flags_and_script_change_stops_resume(self):
        d = tempfile.mkdtemp()
        try:
            ctx = types.SimpleNamespace(stub=True, allow_script_change=False)
            env = R.build_env(ctx, "new", f"{d}/new")
            R.record_provenance(ctx, "new", f"{d}/new", "new_r0", env)
            R.record_provenance(ctx, "new", f"{d}/new", "new_r1", env)             # 同一スクリプトなら再開OK
            first = R.read_jsonl(f"{d}/new/provenance.jsonl")[0]
            self.assertEqual(first["flags"]["OPEN243_M1"], "1")
            self.assertIn("er052_factlock_astra_e2e_runner_01.py", first["scripts"])
            tampered = R.read_jsonl(f"{d}/new/provenance.jsonl")
            tampered[0]["scripts"]["er052_factlock_astra_e2e_runner_01.py"] = "0" * 64
            open(f"{d}/new/provenance.jsonl", "w", encoding="utf-8").write("".join(json.dumps(t) + chr(10) for t in tampered))
            with self.assertRaises(R.GlobalStop):
                R.record_provenance(ctx, "new", f"{d}/new", "new_r2", env)         # スクリプト変更はSTOP
            ctx.allow_script_change = True
            R.record_provenance(ctx, "new", f"{d}/new", "new_r2", env)
            self.assertEqual(R.ArmState(f"{d}/new").count("script_changed"), 1)
        finally:
            shutil.rmtree(d)

    def test_detect_forbidden_api(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(f"{d}/arm/old")
            self.assertEqual(R.detect_forbidden_api(f"{d}/arm/old"), [])
            R.append_jsonl(f"{d}/arm/old/raw_usage_log.jsonl", {"stage": "advanced", "web_search_call_count": 0})
            self.assertEqual(R.detect_forbidden_api(f"{d}/arm/old"), [])
            R.append_jsonl(f"{d}/arm/old/raw_usage_log.jsonl", {"stage": "research", "web_search_call_count": 0})
            R.append_jsonl(f"{d}/arm/old/raw_usage_log_x.jsonl", {"stage": "advanced", "web_search_call_count": 2})
            self.assertEqual(len(R.detect_forbidden_api(f"{d}/arm/old")), 2)
            R.wj(f"{d}/arm/old/storyline_b3/runtime_evidence.json", {})
            self.assertIn({"new_artifact": "storyline_b3/runtime_evidence.json"}, R.detect_forbidden_api(f"{d}/arm/old"))
        finally:
            shutil.rmtree(d)


class G0Test(unittest.TestCase):
    def _prep(self, tamper=None):
        d = tempfile.mkdtemp()
        ctx = types.SimpleNamespace(root=f"{d}/runs", inputs_dir=f"{d}/inputs", stage_r_dir=f"{d}/no_stage_r", allow_frozen=True,
                                    substitute_annotation=True, topics={})
        if tamper:
            tamper(f"{d}/inputs/meta")
        return d, ctx

    def test_g0_pass_on_frozen_meta(self):
        d, ctx = self._prep()
        try:
            g0 = R.prepare_theme(ctx, "meta")
            self.assertTrue(g0["pass"], g0)
            self.assertTrue(all(v["pass"] for v in g0["checks"].values()))
            self.assertTrue(g0["substitutions"])                      # 代用した旨が記録される
            self.assertTrue(os.path.exists(f"{ctx.root}/meta/old/storyline_b3/selected_brief.md"))
            self.assertEqual(R.rd(f"{ctx.root}/meta/new/storyline_b3/selected_brief.md"), R.rd(f"{ctx.root}/meta/shared/brief_annotated.md"))
        finally:
            shutil.rmtree(d)

    def test_g0_fails_on_tampered_ledger_and_on_strip_mismatch(self):
        def bad_ledger(dd):
            os.makedirs(dd, exist_ok=True)
            open(f"{dd}/ledger.txt", "w", encoding="utf-8").write("tampered ledger")
        d, ctx = self._prep(bad_ledger)
        try:
            with self.assertRaises(R.GlobalStop) as cm:
                R.prepare_theme(ctx, "meta")
            self.assertIn("ledger_equals_frozen", str(cm.exception))
        finally:
            shutil.rmtree(d)

        def bad_annot(dd):
            os.makedirs(dd, exist_ok=True)
            t = R.rd(os.path.join(HERE, R.FROZEN["meta"]["annotated"])).replace("人間", "人", 1)   # 注記が本文を書き換えた
            open(f"{dd}/selected_brief_annotated.md", "w", encoding="utf-8", newline="").write(t)
        d, ctx = self._prep(bad_annot)
        try:
            with self.assertRaises(R.GlobalStop) as cm:
                R.prepare_theme(ctx, "meta")
            self.assertIn("annotated_strip_equals_original", str(cm.exception))
        finally:
            shutil.rmtree(d)

    def test_missing_input_means_no_research_fallback(self):
        d = tempfile.mkdtemp()
        try:
            ctx = types.SimpleNamespace(root=f"{d}/r", inputs_dir=f"{d}/i", stage_r_dir=f"{d}/no_sr", allow_frozen=False, substitute_annotation=False,
                                        topics={})
            with self.assertRaises(R.GlobalStop) as cm:
                R.prepare_theme(ctx, "meta")
            self.assertIn("入力欠落", str(cm.exception))
        finally:
            shutil.rmtree(d)

    def test_stage_r_inputs_g0_pass_for_all_ten_themes_with_dryrun_annotation(self):
        """委任_06のStage R出力(読取のみ)10テーマが、凍結台帳一致・LF正規化sha(FROZEN_INPUTS_SHA256.json)・JSON/md一致のG0を通る。
        注記版はdry-run用の機械的な仮注記(許される挿入だけ)。"""
        sr = os.path.join(HERE, R.TRIAL_ROOT, "stage_r")
        themes = [t for t in ("meta", "hormuz", "space_weapons", "small_bag", "byd_recall", "central_bank_mortgage", "inbound_tourism",
                              "openai_copyright", "semiconductor_earnings", "streaming_price")
                  if os.path.exists(f"{sr}/{t}/storyline_b3/selected_brief.md")]
        if not themes:
            self.skipTest("stage_r missing")
        d = tempfile.mkdtemp()
        try:
            ctx = types.SimpleNamespace(root=f"{d}/runs", inputs_dir=f"{d}/inputs", stage_r_dir=sr, allow_frozen=False, substitute_annotation=True, topics={})
            for t in themes:
                g0 = R.prepare_theme(ctx, t)
                self.assertTrue(g0["pass"], t)
                self.assertIn("B3=Stage R出力(委任_06)から取得", g0["substitutions"])
                names = set(g0["checks"])
                self.assertIn("manifest_ledger_sha256_lf", names)
                if t in R.FROZEN:
                    self.assertIn("ledger_equals_frozen", names)
        finally:
            shutil.rmtree(d)

    def test_json_helpers_roundtrip(self):
        jo = json.load(open(os.path.join(HERE, R.FROZEN["meta"]["b3_dir"], "fact_selection_evidence.json"), encoding="utf-8"))
        md = R.rd(os.path.join(HERE, R.FROZEN["meta"]["b3_dir"], "selected_brief.md"))
        self.assertEqual(R.md_facts_of_json(jo), R.parse_brief_md(md)[1].strip("\n"))
        aj = R.annotated_json_from(jo, R.rd(os.path.join(HERE, R.FROZEN["meta"]["annotated"])))
        self.assertTrue(aj["selected_fact_brief_text"].startswith(jo["selected_storyline"]))
        self.assertIn("【事実1】", aj["selected_fact_brief_text"])


# ---------------------------------------------------------------- stub dry-run(子process)
def run_cli(root, themes="meta", arms="old,new", scenario=None, extra=()):
    env = dict(os.environ)
    env.pop("E2E_STUB_SCENARIO", None)
    if scenario:
        env["E2E_STUB_SCENARIO"] = json.dumps(scenario)
    cmd = [sys.executable, "-X", "utf8", RUNNER, "run", "--root", root, "--themes", themes, "--arms", arms, "--stub", "--allow-frozen-b3",
           "--substitute-annotation", "--no-mem-check", "--inputs-dir", os.path.join(root, "_no_inputs"),
           "--stage-r-dir", os.path.join(root, "_no_stage_r"), *extra]
    return subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")


def events(root, theme, arm):
    return R.ArmState(f"{root}/{theme}/{arm}").events()


class ShadowNoStandardArticleTest(unittest.TestCase):      # 委任_12: EN Standard STOP(a2/article.md無し)でもshadowが例外を出さない
    def test_shadow_skips_standard_when_article_missing(self):
        d = tempfile.mkdtemp()
        try:
            for sub in ("ja_writer", "b1b/audit/deviation_checks", "a2/audit/deviation_checks", "telemetry"):
                os.makedirs(f"{d}/{sub}")
            R.wt(f"{d}/ja_writer/revision2.md", "日本語")
            R.wt(f"{d}/b1b/article.md", "本文のみ(見出しなし)")
            R.wj(f"{d}/b1b/audit/deviation_checks/advanced_attempt1.json", {"parsed": {"deviations": []}})
            R.wj(f"{d}/a2/audit/deviation_checks/standard_attempt1.json", {"parsed": {"deviations": []}})
            fake = {}
            for n in ("er003_v1_en_direct_vfl_01_generate", "er003_v1_n3_01_advanced_adaptation_generate",
                      "er012_e_family_entertainment_two_level_runner_01", "er005_cost_logger"):
                m = types.ModuleType(n)
                m.get_client = lambda: object()
                fake[n] = m
            saved = {n: sys.modules.get(n) for n in fake}
            sys.modules.update(fake)
            try:
                rc = R.worker_shadow(types.SimpleNamespace(arm="old"), d, "ledger")
            finally:
                for n, v in saved.items():
                    if v is None:
                        sys.modules.pop(n, None)
                    else:
                        sys.modules[n] = v
            self.assertEqual(rc, 0)
            self.assertNotIn("standard_attempt1_major", R.rj(f"{d}/telemetry/shadow.json"))
        finally:
            shutil.rmtree(d)


class StubDryRunTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_full_two_arms_resume_and_arm_isolation(self):
        r = run_cli(self.root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for arm in ("old", "new"):
            st = R.ArmState(f"{self.root}/meta/{arm}")
            stages = R.OLD_STAGES if arm == "old" else R.NEW_STAGES
            self.assertEqual([s for s in stages if st.status(s) != "done"], [], arm)
            w = R.rj(f"{self.root}/meta/{arm}/writer_run_summary.json")
            m1 = {v.get("env_OPEN243_M1") for v in w.values() if isinstance(v, dict)}
            self.assertEqual(m1, {"1"} if arm == "new" else {None})            # EN段のM1はnew腕のみ
            c = R.rj(f"{self.root}/meta/{arm}/checker/advanced.json")
            self.assertEqual(c["env_protect_flags"], "changed_actor" if arm == "new" else "")   # M3はnew腕のみ
        new_ja = R.rd(f"{self.root}/meta/new/ja_writer/revision2.md")
        self.assertFalse(R.TAG_LEAK_RE.search(new_ja))                          # (c) EN段へ渡る本文にタグ無し
        r2 = R.rj(f"{self.root}/meta/new/new_writer/r2.response.json")
        self.assertTrue(r2["model"].startswith("gpt-6-astra") and r2["previous_response_id_used"] is False and r2["developer_message"] is None)
        # 新腕のEN段にLuna R1/R2が混ざらない(R1/R2のstage tagがraw_usage_logに無い)
        tags = {x.get("stage") for fn in os.listdir(f"{self.root}/meta/new") if fn.startswith("raw_usage_log") for x in R.read_jsonl(f"{self.root}/meta/new/{fn}")}
        self.assertFalse(tags & {"ja_r1", "ja_r2", "ja_r2_must_fix"})
        led = R.BudgetGuard(self.root, 1).entries()
        n0 = len(led)
        self.assertGreater(R.BudgetGuard(self.root, 1).totals()["settled_raw_jpy"], 0)
        r = run_cli(self.root)                                                  # 再開: 完了済みstageはAPI(=ledger)を再度動かさない
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(R.BudgetGuard(self.root, 1).entries()), n0)

    def test_split_arm_invocations_keep_summaries_and_m3_file(self):      # 委任_12: 上書き問題とm3_protected空ファイル
        r1 = run_cli(self.root, arms="new")
        self.assertEqual(r1.returncode, 0, r1.stdout + r1.stderr)
        r2 = run_cli(self.root, arms="old")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        ts = R.rj(f"{self.root}/meta/theme_summary.json")
        self.assertIn("new", ts)
        self.assertIn("old", ts)
        self.assertTrue(os.path.exists(f"{self.root}/run_summary_worker1_new.json"))
        self.assertTrue(os.path.exists(f"{self.root}/run_summary_worker1_old.json"))
        self.assertTrue(os.path.exists(f"{self.root}/meta/new/telemetry/m3_protected.jsonl"))

    def test_b1_recovery_once_then_denied_per_article(self):
        r = run_cli(self.root, arms="new", scenario={"ja_recheck": {"new": 2}}, extra=["--until", "new_en_std"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        evs = events(self.root, "meta", "new")
        self.assertEqual(sum(e["ev"] == "b1_recovery" for e in evs), 1)
        self.assertEqual(sum(e["ev"] == "b1_denied" for e in evs), 1)           # 回復後もMAJOR -> 2回目は1記事1回で拒否 -> STOP記録
        self.assertEqual(R.ArmState(f"{self.root}/meta/new").status("new_en_adv"), "stop")
        self.assertTrue(os.path.isdir(f"{self.root}/meta/new/new_writer_prev_b1"))     # 元の成果物は別名保存
        self.assertTrue(R.stage_ok(f"{self.root}/meta/new/recovery/must_fix.json"))
        self.assertEqual(len(R.read_jsonl(f"{self.root}/meta/new/telemetry/ja_recheck_events.jsonl")), 2)   # 初回(回復前)も記録

    def test_b1_trial_limit_zero_denies_and_records_stop(self):
        r = run_cli(self.root, arms="new", scenario={"ja_recheck": {"new": 1}}, extra=["--until", "new_en_std", "--b1-total-max", "0"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        denied = [e for e in events(self.root, "meta", "new") if e["ev"] == "b1_denied"]
        self.assertEqual(len(denied), 1)
        self.assertIn("trial_limit", denied[0]["reason"])

    def test_r2_fc_major_triggers_b1_and_shadow_stop_final_continues(self):
        r = run_cli(self.root, arms="new", scenario={"fc_major": {"new_r2_fc": 2}}, extra=["--until", "new_en_std"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        evs = events(self.root, "meta", "new")
        shadow = [e for e in evs if e["ev"] == "shadow_stop"]
        # R2後FC MAJORを検出するたびに final=False を記録: 1回目MAJOR -> B1回復 -> 再生成後もMAJOR(final=False) -> 回復枠なし -> 影STOP(final=True)
        self.assertEqual([e["final"] for e in shadow], [False, False, True])
        self.assertEqual(sum(e["ev"] == "b1_recovery" for e in evs), 1)
        self.assertEqual(R.ArmState(f"{self.root}/meta/new").status("new_en_std"), "done")   # 影STOPでも続行(分母に残す)
        self.assertTrue(R.rj(f"{self.root}/meta/new/new_writer/r2_fc.json")["shadow_stop"])

    def test_forbidden_research_call_stops_everything_and_no_checker(self):
        r = run_cli(self.root, arms="old", scenario={"force_research_call": True})
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        stop = R.rj(f"{self.root}/STOP.json")
        self.assertIn("研究/B3呼び出し", stop["reason"])
        self.assertTrue(R.stage_ok(f"{self.root}/meta/old/telemetry/forbidden_call.json"))
        self.assertFalse(os.path.exists(f"{self.root}/meta/old/checker"))

    def test_web_search_row_in_log_stops(self):
        r = run_cli(self.root, arms="old", scenario={"force_web_search_row": True})
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("研究/B3呼び出し", R.rj(f"{self.root}/STOP.json")["reason"])

    def test_budget_hard_stop(self):
        r = run_cli(self.root, arms="new", extra=["--cap-jpy", "20"])
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("BUDGET_HARD_STOP", R.rj(f"{self.root}/STOP.json")["reason"])

    def test_corrupted_output_is_rerun_not_trusted(self):
        r = run_cli(self.root, arms="old", extra=["--until", "old_adv"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        open(f"{self.root}/meta/old/b1b/article.md", "wb").write(b"\x00\x00")
        self.assertFalse(R.stage_ok(f"{self.root}/meta/old/b1b/article.md"))
        r = run_cli(self.root, arms="old", extra=["--until", "old_adv"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(R.stage_ok(f"{self.root}/meta/old/b1b/article.md"))
        self.assertGreaterEqual(sum(1 for e in R.BudgetGuard(self.root, 1).entries() if e["kind"] == "settle" and e["stage"] == "old_adv"), 2)

    def test_shadow_m1b_counterfactual_and_aggregate(self):
        r = run_cli(self.root, scenario={"en_attempt1_summary_major": True}, extra=["--until", "new_check_std"])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for arm, rule in (("new", "old_full_regen"), ("old", "m1_summary_only")):
            sh = R.rj(f"{self.root}/meta/{arm}/telemetry/shadow.json")
            self.assertTrue(sh["m1b"]["majors_only_in_summary"], arm)
            self.assertEqual(sh["m1b"]["counterfactual"]["rule"], rule)
            self.assertEqual(sh["m1a"]["alt_rule"], "old_input" if arm == "new" else "m1_input")
        import er052_factlock_astra_e2e_aggregate_01 as agg_mod
        agg = agg_mod.aggregate(self.root)
        self.assertEqual(agg["arms"]["new"]["planned_runs"], 2)
        self.assertEqual(agg["arms"]["old"]["checker_runs_done"], 2)
        self.assertTrue(agg["arms"]["new"]["stub_values"])
        md = agg_mod.to_markdown(agg)
        self.assertIn("| L 人手介入率(予定run分母) |", md)


if __name__ == "__main__":
    unittest.main()
