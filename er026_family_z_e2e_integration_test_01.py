# -*- coding: utf-8 -*-
"""FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_05: er026 E2E統合のtest(課金0・実API呼出なし)。

- stage順 / --stage all / STOP条件(話者不一致、other、budget、STOPセンチネル)。2026-10-12ユーザー決定により原作保持Validator(er061)は経路から撤廃(validate stageなし)、Std段落不一致はWARN+独自分割
- resume(provenance sha)・dry-run副作用ゼロ・mock全stage通し(writer->...->assemble->pages->page_verify --local)
- mock時は全LLM/TTS/ASR/KP fnを内蔵ダミーに固定し、実client生成/ログ初期化が呼ばれたら即AssertionError
実行: .venv/Scripts/python.exe -m unittest er026_family_z_e2e_integration_test_01 -v
(page_verifyは約2分。ER026_SKIP_PAGE_VERIFY=1 でその1件だけ省略できる)"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from unittest import mock

import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st62
import er063_family_z_audio_01 as a63

MONITORED_FILES = [
    "er006_output/master_audio_store_01/manifest.json",
    "er006_output/master_audio_store_01/reuse_telemetry.jsonl",
    "er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl",
    "er006_output/pronunciation_ledger_01/ledger.json",
    "er011_output/attempt_history.jsonl",
    "er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl",
    "er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl",
    "er030_output/kp_backend_telemetry_01/telemetry.jsonl",
    "er005_output/cost_baseline_01/cost_summary.json",
]
MONITORED_DIRS = ["er026_output/family_z_production_e2e_01", "er011_output/local_rewrite_recovery",
                  "user_test/family_z_melos_01", "user_test/family_z_melos_02"]
PRE_STAGES = ["seed_check", "writer", "std_adjust", "plan", "support", "kp"]


def _file_sha(p):
    if not os.path.exists(p):
        return None
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def snapshot() -> dict:
    snap = {"files": {p: _file_sha(p) for p in MONITORED_FILES}, "dirs": {}}
    for d in MONITORED_DIRS:
        rows = []
        if os.path.isdir(d):
            for root, _dirs, files in os.walk(d):
                for fn in files:
                    fp = os.path.join(root, fn)
                    rows.append((fp, os.path.getsize(fp), os.stat(fp).st_mtime_ns))
        snap["dirs"][d] = (os.path.isdir(d), sorted(rows))
    return snap


def forbid_real_apis() -> contextlib.ExitStack:
    """mock時に実client生成・ログ初期化・実Support/KP/TTS入口が呼ばれたら即AssertionError(04B事故再発防止)。"""
    stack = contextlib.ExitStack()
    for target in ("er003_v1_en_direct_vfl_01_generate.get_client",
                   "er003_v1_b1_scaffold_01_generate.get_client",
                   "er003_v1_b1_scaffold_01_generate.run_support_text",
                   "er003_v1_iran01_a2_generate.run_support_text",
                   "er003_v1_n3_01_scaffold_generate.run_key_phrases",
                   "er005_cost_logger.install",
                   "er063_family_z_audio_01.real_generators"):
        stack.enter_context(mock.patch(target, side_effect=AssertionError(f"REAL API PATH CALLED: {target}")))
    return stack


def run_stages_quiet(ctx, stages):
    with contextlib.redirect_stdout(io.StringIO()):
        return r.run_stages(ctx, stages)


class TmpMixin:
    def new_tmp(self):
        t = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, t, True)
        return t


# ============================================================
# 1. mock全stage通し(1回だけ実行して各観点を検証)
# ============================================================
class MockFullPipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = snapshot()
        cls.tmp = tempfile.mkdtemp()
        cls._forbid = forbid_real_apis()
        cls._forbid.__enter__()
        cls.ctx = r.build_mock_context(cls.tmp)
        cls.stages = [s for s in r.E2E_STAGES if s != "page_verify"]
        cls.results = run_stages_quiet(cls.ctx, cls.stages)
        cls.out = cls.ctx.out_dir

    @classmethod
    def tearDownClass(cls):
        cls._forbid.__exit__(None, None, None)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _j(self, rel):
        with open(f"{self.out}/{rel}", encoding="utf-8") as f:
            return json.load(f)

    def test_stage_order_is_fixed_and_all_ran(self):
        self.assertEqual(list(r.E2E_STAGES), ["seed_check", "writer", "std_adjust", "plan",
                                              "support", "kp", "tts_b1b", "tts_a2", "provision_shell", "gate",
                                              "assemble", "pages", "page_verify"])
        self.assertEqual(list(self.results), self.stages)

    def test_stage_log_written_per_stage(self):
        with open(f"{self.out}/e2e_stage_log.jsonl", encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
        self.assertEqual([x["stage"] for x in rows][: len(self.stages)], self.stages)
        self.assertTrue(all(x["mode"] == "mock" for x in rows))

    def test_word_count_and_ratio_guardrails_are_warn_only_and_never_regenerate(self):
        # 2026-10-12ユーザー決定: Adv/Stdとも400±70=330-470語(2026-10-19更新、WARNのみ)。Adv/Std語数比Guardrailは撤回。自動再生成しない。
        g_adv = self.results["writer"]["stages"]["r2"]["guardrails"]
        self.assertEqual(g_adv["failures"], [])
        self.assertFalse(any("RATIO" in w for w in g_adv["warnings"]))
        g_std = self.results["std_adjust"]["guardrails"]
        self.assertFalse(any("RATIO" in w for w in g_std["warnings"]))
        self.assertFalse(self.results["std_adjust"]["auto_regenerated"])
        self.assertEqual(g_std["failures"], [])

    def test_seed_check_reports_approved_melos_voice(self):
        res = self.results["seed_check"]
        self.assertEqual(res["melos_voice_status"], "APPROVED_FOR_PRODUCTION")
        self.assertEqual(res["dialogue_voices"]["narrator"], "Aoede")
        self.assertEqual(res["dialogue_voices"]["selinuntius"], "Erinome")
        self.assertEqual(res["dialogue_voices"]["dionysius"], "Charon")
        self.assertTrue(res["er020_full_story_clip_pattern"])

    def test_no_validator_stage_and_er061_not_loaded_by_runner(self):
        # 2026-10-12ユーザー決定: 原作保持Validator(er061)は撤廃。経路にstage・成果物・importがない
        self.assertFalse(os.path.exists(f"{self.out}/validator"))
        self.assertNotIn("validate_b1b", self.results)
        self.assertNotIn("validate_a2", self.results)
        self.assertFalse(hasattr(r._m(), "v61"))
        self.assertFalse(hasattr(self.ctx, "judge_client"))

    def test_provenance_chain_and_no_stale(self):
        prov = self._j("writer/provenance.json")
        self.assertEqual([e["stage"] for e in prov["chain"]], ["r0", "r1", "r2", "std_adjust"])
        for name in ("plan_b1b", "plan_a2", "support_b1b", "support_a2", "kp_b1b", "kp_a2", "kp_expl_b1b"):
            self.assertIn(name, prov["downstream_stages"])
        self.assertEqual(prov["downstream_stale"], [])
        # sha chain: 親outputshaが子のinputshaになる
        self.assertEqual(prov["chain"][1]["input_sha256"], prov["chain"][0]["output_sha256"])
        self.assertEqual(prov["chain"][3]["input_sha256"], prov["chain"][2]["output_sha256"])

    def test_plan_aligned_and_speaker_table(self):
        pb, pa = self._j("segment_plan_b1b.json"), self._j("segment_plan_a2.json")
        self.assertEqual(pa["split_origin"], "mapped_from_advanced")
        self.assertEqual(pa["boundaries"], pb["boundaries"])
        self.assertTrue(pa["std_adv_paragraph_count_match"])
        with open(f"{self.out}/speaker_table.md", encoding="utf-8") as f:
            table = f.read()
        att = self._j("dialogue_attribution_b1b.json")
        for row in att["rows"]:
            self.assertIn(row["quote_id"], table)       # 全引用が人間確認用の表に載る
        self.assertNotIn("is_recollection", table)
        self.assertNotIn("is_recollection", json.dumps(att))

    def test_kp_assets_copied_and_adv_third_segment_is_english_explanation(self):
        for lv in ("b1b", "a2"):
            self.assertTrue(os.path.exists(f"{self.out}/{lv}/key_phrases/keywords_canonicalized.json"))
        self.assertTrue(os.path.exists(f"{self.out}/b1b/narration/kp1_explanation_en.wav"))
        self.assertFalse(os.path.exists(f"{self.out}/b1b/narration/kp1_ja.wav"))
        self.assertTrue(os.path.exists(f"{self.out}/a2/narration/kp1_ja.wav"))
        self.assertFalse(os.path.exists(f"{self.out}/a2/narration/kp1_explanation_en.wav"))
        adv = self._j("b1b/audit/tts_generation_results.json")
        self.assertEqual(adv["key_phrases"]["1"]["explanation"]["role_style_key"], "KP_EXPL_EN")
        self.assertNotIn("japanese_meaning", adv["key_phrases"]["1"])
        std = self._j("a2/audit/tts_generation_results.json")
        self.assertIn("japanese_meaning", std["key_phrases"]["1"])

    def test_tts_entries_voice_role_and_slowdown(self):
        adv = self._j("b1b/audit/tts_generation_results.json")["segments"]
        std = self._j("a2/audit/tts_generation_results.json")["segments"]
        clip_ids = [k for k in adv if re.fullmatch(r"full_story_part[1-3]_c[0-9]+", k)]
        self.assertTrue(clip_ids)
        self.assertEqual({adv[k]["role"] for k in clip_ids}, {"FULL_STORY"})
        voices = {adv[k]["voice"] for k in clip_ids}
        self.assertIn("Aoede", voices)                    # narrator
        self.assertTrue(voices & {"Charon", "Erinome", "Algieba"})   # dialogue clipは別Voice
        self.assertTrue(all(std[k]["slowdown_applied"] is True for k in std if re.fullmatch(r"full_story_part[1-3]_c[0-9]+", k)))

    def test_gate_and_assembly(self):
        for lv in ("b1b", "a2"):
            g = self._j(f"{lv}/audit/gate_result_04C.json")
            self.assertEqual(g["shared_gate"], "PASS")
            tl = self._j(f"{lv}/assembly/timeline.json")
            self.assertNotIn("In One Line", tl["sequence_order"])
            self.assertEqual(tl["sequence_order"][-1], "Outro")
            self.assertTrue(os.path.exists(tl["wav"]))
        self.assertEqual(self.results["gate"]["b1b"]["audio_text_deviation_clips"], [])

    def test_pages_built_without_level_labels_or_file_scheme(self):
        pages = self.results["pages"]
        for label in ("Standard", "Advanced"):
            self.assertEqual(pages[label]["lint"], {"file_scheme": False, "level_label_leak": False, "kp_label_leak": False})
        self.assertTrue(os.path.exists(f"{self.ctx.pages_dir}/index.html"))
        self.assertFalse(os.path.abspath(self.ctx.pages_dir).startswith(os.path.abspath(r.E2E_PAGES_DIR)))  # mockは公開用ディレクトリに書かない

    def test_shared_state_files_unchanged_by_mock_run(self):
        after = snapshot()
        self.assertEqual(after["files"], self.before["files"])
        self.assertEqual(after["dirs"]["er011_output/local_rewrite_recovery"], self.before["dirs"]["er011_output/local_rewrite_recovery"])
        self.assertEqual(after["dirs"]["user_test/family_z_melos_01"], self.before["dirs"]["user_test/family_z_melos_01"])
        self.assertEqual(after["dirs"]["user_test/family_z_melos_02"], self.before["dirs"]["user_test/family_z_melos_02"])
        self.assertEqual(after["dirs"]["er026_output/family_z_production_e2e_01"],
                         self.before["dirs"]["er026_output/family_z_production_e2e_01"])

    def test_resume_reuses_without_new_api_calls(self):
        llm_before = len(self.ctx.llm_client.responses.calls)
        res = run_stages_quiet(self.ctx, ["writer", "std_adjust", "plan", "support", "kp", "tts_b1b"])
        self.assertEqual(len(self.ctx.llm_client.responses.calls), llm_before)
        self.assertTrue(all(v["status"] == "reused" for v in res["writer"]["stages"].values()))
        adv = self._j("b1b/audit/tts_generation_results.json")["segments"]
        self.assertTrue(all(e.get("reused_from_previous_run") for k, e in adv.items()
                            if re.fullmatch(r"full_story_part[1-3]_c[0-9]+", k)))

    def test_zz_page_verify_local_playwright(self):
        if os.environ.get("ER026_SKIP_PAGE_VERIFY") == "1":
            self.skipTest("ER026_SKIP_PAGE_VERIFY=1")
        res = r.stage_page_verify(self.ctx)       # 約2分。問題があれば FamilyZE2EStop
        self.assertEqual(res["pages"], ["advanced.html", "index.html", "standard.html"])
        ev = self._j("page_verify_local.json")
        self.assertEqual(ev["pages"]["standard.html"]["plays_failed"], [])
        self.assertEqual(ev["pages"]["advanced.html"]["plays_failed"], [])
        self.assertTrue(ev["internal_only_local"])


class PageVerifyEvaluationTest(unittest.TestCase):
    GOOD = {"http_status": 200, "plays_failed": [], "console_errors": [], "http_ge400": [], "(m)_no_file_scheme": True,
            "(i)_no_A2_B1_label": True, "(n)_no_kp_label": True, "(a)_full_episode_audio": True, "(b)_preview_row": True,
            "(f)_intro_outro_noted": True, "(k)_tts_mode_stated": True, "(c)_comment_rows": 3, "(d)_story_rows": 30,
            "(e)_kp_rows": 5, "seek_ok_all": False}

    def test_good_passes_and_seek_false_is_ignored(self):
        self.assertEqual(r.evaluate_page_verify({"pages": {"standard.html": dict(self.GOOD)}}), [])

    def test_failures_are_detected(self):
        bad = dict(self.GOOD, plays_failed=["x.mp3"], http_status=404, **{"(i)_no_A2_B1_label": False})
        problems = r.evaluate_page_verify({"pages": {"advanced.html": bad}})
        self.assertTrue(any("plays_failed" in p for p in problems))
        self.assertTrue(any("http_status=404" in p for p in problems))
        self.assertTrue(any("(i)_no_A2_B1_label" in p for p in problems))


# ============================================================
# 2. dry-run 副作用ゼロ / CLI
# ============================================================
class DryRunAndCliTest(unittest.TestCase):
    def _main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = r.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_dry_run_all_stages_zero_side_effects(self):
        before = snapshot()
        run = "t_dry_run_zero"
        out_dir = r.E2EContext(run=run).out_dir
        with forbid_real_apis(), mock.patch("os.makedirs", side_effect=AssertionError("dry-runでmakedirs")):
            code, out, _ = self._main(["--mode", "dry-run", "--stage", "all", "--run", run])
        self.assertEqual(code, 0)
        plan = json.loads(out)
        self.assertEqual([s["stage"] for s in plan["stages"]], list(r.E2E_STAGES))
        self.assertTrue(plan["dry_run"])
        self.assertEqual(plan["preflight"]["melos_voice_status"], "APPROVED_FOR_PRODUCTION")
        self.assertNotIn("validate_b1b", [s["stage"] for s in plan["stages"]])
        self.assertEqual(plan["stop_sentinel"]["exit_code_on_hit"], 3)
        self.assertFalse(os.path.exists(out_dir))
        self.assertEqual(snapshot(), before)               # Master Store/telemetry/queue/attempt_history/ledger 不変

    def test_dry_run_each_single_stage(self):
        before = snapshot()
        for s in r.E2E_STAGES:
            with forbid_real_apis():
                code, out, _ = self._main(["--mode", "dry-run", "--stage", s, "--run", "t_dry_single"])
            self.assertEqual(code, 0, s)
            self.assertEqual([x["stage"] for x in json.loads(out)["stages"]], [s])
        self.assertEqual(snapshot(), before)

    def test_legacy_dry_run_flag_maps_to_dry_run(self):
        before = snapshot()
        with forbid_real_apis():
            code, out, _ = self._main(["--dry-run", "--stage", "writer", "--run", "t_dry_legacy"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["dry_run"])
        self.assertEqual(snapshot(), before)

    def test_stop_after_limits_stages(self):
        with forbid_real_apis():
            code, out, _ = self._main(["--mode", "dry-run", "--stop-after", "plan"])
        self.assertEqual([x["stage"] for x in json.loads(out)["stages"]], list(r.E2E_STAGES[:r.E2E_STAGES.index("plan") + 1]))

    def test_real_mode_without_budget_stops_before_any_client_or_dir(self):
        run = "t_real_unapproved"
        out_dir = r.E2EContext(run=run).out_dir
        with forbid_real_apis():
            code, _out, err = self._main(["--mode", "real", "--stage", "writer", "--run", run])
        self.assertEqual(code, 2)
        self.assertIn("FamilyZBudgetStop", err)
        self.assertIn("NOT_APPROVED", err)
        self.assertFalse(os.path.exists(out_dir))

    def test_real_mode_above_approved_max_stops(self):
        with forbid_real_apis():
            code, _out, err = self._main(["--mode", "real", "--stage", "writer", "--run", "t_real_over",
                                          "--approved-budget-jpy", "301"])
        self.assertEqual(code, 2)
        self.assertIn("ABOVE_APPROVED_MAX", err)
        self.assertFalse(os.path.exists(r.E2EContext(run="t_real_over").out_dir))

    def test_parser_defaults_are_safe(self):
        a = r.build_parser().parse_args([])
        self.assertEqual((a.mode, a.stage, a.tts_execution_mode), ("dry-run", "all", "STANDARD"))
        self.assertFalse(a.ack_warn_threshold)
        self.assertEqual(a.warn_threshold_jpy, 200.0)


class StageOrderTest(unittest.TestCase):
    def test_run_stages_executes_in_given_order_and_stops_on_error(self):
        seen = []

        def fake(ctx, name):
            seen.append(name)
            if name == "plan":
                raise r.FamilyZE2EStop("boom")
            return {}
        ctx = r.E2EContext(mode="mock", run_root=tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, ctx.run_root, True)
        with mock.patch.object(r, "run_stage", side_effect=fake), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(r.FamilyZE2EStop):
                r.run_stages(ctx, r.E2E_STAGES)
        self.assertEqual(seen, list(r.E2E_STAGES[: r.E2E_STAGES.index("plan") + 1]))


# ============================================================
# 3. STOP条件
# ============================================================
class StopConditionsTest(TmpMixin, unittest.TestCase):
    def setUp(self):
        self._forbid = forbid_real_apis()
        self._forbid.__enter__()
        self.addCleanup(self._forbid.__exit__, None, None, None)

    def _std_extra_paragraph(self, n, adv):
        return r._mock_std_text(adv, n) + "\nExtra paragraph really.\n"

    def test_std_identical_to_adv_stops_in_std_adjust(self):
        ctx = r.build_mock_context(self.new_tmp(), writer_hook=r.mock_writer_hook(std_override=lambda n, adv: adv))
        with self.assertRaises(st62.FamilyZStop):
            run_stages_quiet(ctx, ["seed_check", "writer", "std_adjust"])

    # --- Std段落数 ---
    def _std_calls(self, ctx):
        return sum(1 for c in ctx.llm_client.responses.calls if "Rewrite this entire story for CEFR A2" in c["input"][-1]["content"])

    def test_std_paragraph_mismatch_warns_and_falls_back_without_regeneration_or_stop(self):
        # 2026-10-12ユーザー決定: 段落不一致はWARN+04B独自分割。再生成・STOPしない。
        ctx = r.build_mock_context(self.new_tmp(), writer_hook=r.mock_writer_hook(std_override=self._std_extra_paragraph))
        res = run_stages_quiet(ctx, ["seed_check", "writer", "std_adjust", "plan"])
        self.assertEqual(self._std_calls(ctx), 1)                              # 再生成なし(1回のみ)
        self.assertFalse(res["std_adjust"]["auto_regenerated"])
        self.assertIsNotNone(res["std_adjust"]["paragraph_mismatch_warn"])
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/writer/std_paragraph_mismatch_warn.json"))
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/writer/std_auto_realign.json"))
        self.assertNotEqual(res["plan"]["a2"]["split_origin"], "mapped_from_advanced")   # 独自分割にフォールバック
        run_stages_quiet(ctx, ["std_adjust"])                                  # 再実行も追加callなし
        self.assertEqual(self._std_calls(ctx), 1)

    def test_word_count_out_of_range_is_warn_only(self):
        nl = chr(10) * 2
        ctx = r.build_mock_context(
            self.new_tmp(), writer_hook=r.mock_writer_hook(std_override=lambda n, adv: "# T" + nl + nl.join(["Short here."] * n)))
        res = run_stages_quiet(ctx, ["seed_check", "writer", "std_adjust"])
        g = res["std_adjust"]["guardrails"]
        self.assertTrue(any(w.startswith("STD_WORDS_OUT_OF_RANGE") for w in g["warnings"]))
        self.assertEqual(g["failures"], [])
        self.assertFalse(res["std_adjust"]["auto_regenerated"])

    # --- STOPセンチネル(委任_11) ---
    def test_stop_sentinel_run_stops_before_any_api_call_and_records_audit(self):
        ctx = r.build_mock_context(self.new_tmp())
        os.makedirs(ctx.out_dir, exist_ok=True)
        with open(f"{ctx.out_dir}/STOP", "w", encoding="utf-8") as f:
            f.write("stop")
        with self.assertRaises(st62.FamilyZStopSentinel):
            run_stages_quiet(ctx, ["seed_check", "writer"])
        self.assertEqual(len(ctx.llm_client.responses.calls), 0)               # 新規API呼出なし
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/audit_stop_sentinel.jsonl"))
        st62.set_stop_run_dir(None)

    def test_stop_sentinel_stop_all_stops_and_main_returns_rc3(self):
        ctx = r.build_mock_context(self.new_tmp())
        stop_all = os.path.join(self.new_tmp(), "STOP_ALL")
        with open(stop_all, "w", encoding="utf-8") as f:
            f.write("stop")
        with mock.patch.object(st62, "STOP_ALL_PATH", stop_all):
            with self.assertRaises(st62.FamilyZStopSentinel):
                run_stages_quiet(ctx, ["writer"])
            self.assertEqual(len(ctx.llm_client.responses.calls), 0)
            with mock.patch.object(r, "build_mock_context", return_value=ctx):
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    code = r.main(["--mode", "mock", "--stage", "writer", "--run", "t_sentinel"])
        self.assertEqual(code, 3)
        st62.set_stop_run_dir(None)

    def test_stop_sentinel_blocks_each_tts_clip_call(self):
        calls = []
        gens = {"narrator": lambda spec, out: calls.append(spec.clip_id) or {"status": "OK"}}
        d = self.new_tmp()
        with open(f"{d}/STOP", "w", encoding="utf-8") as f:
            f.write("stop")
        wrapped = r.wrap_generators_with_budget(gens, None, sentinel_dir=d)
        spec = type("S", (), {"clip_id": "full_story_part1_c1"})()
        with self.assertRaises(st62.FamilyZStopSentinel):
            wrapped["narrator"](spec, "x.wav")
        self.assertEqual(calls, [])

    # --- 話者 ---
    def _flip_attribution(self, quote_id, speaker):
        base = r.mock_writer_hook()

        def hook(kw):
            out = base(kw)
            if (kw.get("text") or {}).get("format", {}).get("name") == "z_dialogue_attribution":
                obj = json.loads(out)
                for a in obj["attributions"]:
                    if a["quote_id"] == quote_id:
                        a["speaker"] = speaker
                return json.dumps(obj)
            return out
        return hook

    def test_speaker_mismatch_stops_and_records_override(self):
        # q9_1 は決定論=friend。LLMがkingと食い違うとSTOP(自動採用しない)
        ctx = r.build_mock_context(self.new_tmp(), writer_hook=self._flip_attribution("q9_1", "king"))
        with self.assertRaises(st62.FamilyZDialogueMismatchStop):
            run_stages_quiet(ctx, PRE_STAGES[:4])
        self.assertTrue(os.path.exists(f"{ctx.out_dir}/dialogue_override.json"))
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/segment_plan_b1b.json"))

    def test_speaker_other_stops(self):
        # q1_1 は決定論=判定不能(llm_only)。LLMが other を返すと採用はされるがSTOP(04C)
        ctx = r.build_mock_context(self.new_tmp(), writer_hook=self._flip_attribution("q1_1", "other"))
        with self.assertRaises(r.FamilyZDialogueOtherStop) as cm:
            run_stages_quiet(ctx, PRE_STAGES[:4])
        self.assertIn("other", str(cm.exception))

    def test_llm_only_speaker_is_adopted_without_stop(self):
        ctx = r.build_mock_context(self.new_tmp())
        res = run_stages_quiet(ctx, PRE_STAGES[:4])
        self.assertGreater(res["plan"]["b1b"]["dialogue_summary"]["llm_only"], 0)

    # --- provenance ---
    def test_provenance_sha_mismatch_stops_on_resume(self):
        ctx = r.build_mock_context(self.new_tmp())
        run_stages_quiet(ctx, ["seed_check", "writer"])
        with open(f"{ctx.out_dir}/writer/r2.md", "a", encoding="utf-8") as f:
            f.write("\nTampered paragraph.\n")
        with self.assertRaises(st62.FamilyZProvenanceMismatchStop):
            run_stages_quiet(ctx, ["writer"])

    # --- budget ---
    def test_budget_unit_rules(self):
        with self.assertRaises(r.FamilyZBudgetStop):
            r.E2EBudget(0)
        with self.assertRaises(r.FamilyZBudgetStop):
            r.E2EBudget(300.01)
        b = r.E2EBudget(300, 200, spent_fn=lambda: 195.0)
        b.guard("ok", 5.0)                                   # 200ちょうどはOK
        with self.assertRaises(r.FamilyZBudgetStop) as cm:
            b.guard("over", 5.01)
        self.assertIn("WARN_THRESHOLD", str(cm.exception))
        b2 = r.E2EBudget(300, 200, spent_fn=lambda: 250.0, ack_warn=True)
        b2.guard("ack-ok", 50.0)
        with self.assertRaises(r.FamilyZBudgetStop) as cm:
            b2.guard("ack-over", 50.01)
        self.assertIn("APPROVED_CAP", str(cm.exception))
        self.assertEqual(r.E2EBudget(300, 200, spent_fn=lambda: (12.5, {})).spent(), 12.5)     # tuple戻り値(compute_cost_jpy_so_far形)

    def test_budget_stop_before_any_new_api_call(self):
        ctx = r.build_mock_context(self.new_tmp())
        ctx.budget = r.E2EBudget(300, 200, spent_fn=lambda: 199.0)
        with self.assertRaises(r.FamilyZBudgetStop):
            run_stages_quiet(ctx, ["seed_check", "writer"])
        self.assertEqual(len(ctx.llm_client.responses.calls), 0)             # 新規API呼出前に停止
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/writer/r0.md"))

    def test_budget_stop_mid_tts_keeps_audit_records_and_raises(self):
        ctx = r.build_mock_context(self.new_tmp())
        run_stages_quiet(ctx, PRE_STAGES)
        counter = {"n": 0}
        base_gens = r.mock_tts_generators()

        def counting(fn):
            def w(spec, out_path):
                counter["n"] += 1
                return fn(spec, out_path)
            return w
        ctx.hooks["tts_generators"] = {k: counting(v) for k, v in base_gens.items()}
        ctx.budget = r.E2EBudget(300, 200, spent_fn=lambda: 195.0 + 0.6 * counter["n"])
        with self.assertRaises(r.FamilyZBudgetStop):
            run_stages_quiet(ctx, ["tts_b1b"])
        data = json.load(open(f"{ctx.out_dir}/b1b/audit/tts_generation_results.json", encoding="utf-8"))
        statuses = [e["status"] for e in data["segments"].values()]
        self.assertIn("OK", statuses)                # 停止前に生成済みのclipは監査記録に残る
        self.assertIn("STOPPED", statuses)
        self.assertLess(counter["n"], 20)            # 以降のclipは新規生成されない

    def test_tts_clip_failure_stops_with_listing(self):
        ctx = r.build_mock_context(self.new_tmp())
        run_stages_quiet(ctx, PRE_STAGES)
        base = r.mock_tts_generators()

        def failing_narrator(spec, out_path):
            if spec.clip_id == "full_story_part1_c1":
                return {"status": "STOPPED", "reason": "asr mismatch"}
            return base["narrator"](spec, out_path)
        ctx.hooks["tts_generators"] = dict(base, narrator=failing_narrator)
        with self.assertRaises(r.FamilyZTtsClipFailedStop) as cm:
            run_stages_quiet(ctx, ["tts_b1b"])
        self.assertIn("full_story_part1_c1", str(cm.exception))


# ============================================================
# 4. 個別helper
# ============================================================
class KpInstallTest(TmpMixin, unittest.TestCase):
    def test_install_kp_assets_copies_to_level_dir_and_fails_closed_when_missing(self):
        ctx = r.E2EContext(mode="mock", run_root=self.new_tmp(), run="t_kp")
        with self.assertRaises(r.FamilyZE2EStop):
            r.install_kp_assets(ctx, "b1b")
        os.makedirs(f"{ctx.out_dir}/key_phrases/b1b")
        with open(f"{ctx.out_dir}/key_phrases/b1b/keywords_canonicalized.json", "w", encoding="utf-8") as f:
            json.dump({"items": []}, f)
        dst = r.install_kp_assets(ctx, "b1b")
        self.assertEqual(dst, f"{ctx.out_dir}/b1b/key_phrases/keywords_canonicalized.json")
        self.assertTrue(os.path.exists(dst))


class Er063KpExplanationExtensionTest(unittest.TestCase):
    def test_kp_explanation_style_is_x_p7_reference_and_x_unchanged(self):
        # 2026-10-17 委任_15: 期待値を意図的に更新(旧: 旧KEY_PHRASE_EXPLANATION_EN逐語コピー。ユーザー承認§2B: Adv KP英語解説=P7=X共通定数参照)。
        import er019_family_x_style_profile_01 as xs
        import er033_tts_flash_lite_family_x_styles_01 as fl
        self.assertIs(a63._STYLE_TEXT["P7"], xs.P7_TEXT)
        self.assertEqual(a63.FAMILY_Z_ROLE_STYLE["KP_EXPL_EN"]["text"], xs.P7_TEXT)
        self.assertEqual(a63.FAMILY_Z_ROLE_STYLE["KP_EXPL_EN"]["style_label"], "P7")
        self.assertNotEqual(xs.P7_TEXT, fl.KEY_PHRASE_EXPLANATION_EN)   # 旧P0(KEY_PHRASE_EXPLANATION_EN)はX側で不変のまま、Zは使わない
        self.assertTrue(a63.assert_style_table_integrity())

    def test_plan_requires_explanation_text_for_adv_and_uses_explanation_ids(self):
        story = [{"id": "full_story_part1_c1", "speaker": "narrator", "text": "Melos ran."}]
        kp = [{"rank": 1, "used_form": "ran on", "japanese_gloss": "走り続ける"}]
        comments = {1: "c", 2: "c", 3: "c"}
        with self.assertRaises(a63.FamilyZAudioStop):
            a63.build_level_plan("b1b", story, "p", comments, kp, "T", kp_explanations={})
        plan = a63.build_level_plan("b1b", story, "p", comments, kp, "T", kp_explanations={1: "to keep going"})
        ids = [s.clip_id for s in plan]
        self.assertIn("kp1_explanation_en", ids)
        self.assertNotIn("kp1_ja", ids)
        spec = next(s for s in plan if s.clip_id == "kp1_explanation_en")
        self.assertEqual((spec.kind, spec.voice, spec.role_key), ("kp_expl_en", "Aoede", "KP_EXPL_EN"))
        self.assertIsNotNone(a63._lookup_entry({"key_phrases": {"1": {"explanation": {"status": "OK"}}}}, "kp1_explanation_en"))

    def test_default_plan_without_explanations_is_unchanged(self):
        story = [{"id": "full_story_part1_c1", "speaker": "narrator", "text": "Melos ran."}]
        kp = [{"rank": 1, "used_form": "ran on", "japanese_gloss": "走り続ける"}]
        plan = a63.build_level_plan("b1b", story, "p", {1: "c", 2: "c", 3: "c"}, kp, "T")
        self.assertIn("kp1_ja", [s.clip_id for s in plan])


if __name__ == "__main__":
    unittest.main()
