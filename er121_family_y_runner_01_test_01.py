# -*- coding: utf-8 -*-
"""FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02B: Y Production runner の mock test(API 0・実client生成block・network遮断)。

遮断harness(KP HR案件でmock漏れにより実LLM到達事故があったため、新入口のtestは最初に遮断を張る):
  - socket.connect / create_connection / getaddrinfo を例外化、
  - vfl01.get_client / openai.OpenAI / google.genai.Client の生成を例外化(生成試行を数える)。
  testの終了時に『実client生成試行 0・network接続試行 0』を確認する。
"""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import er121_family_y_runner_01 as r  # noqa: E402
import er121_family_y_structure_01 as ys  # noqa: E402

BLOCK = {"net": 0, "client": 0}
_PATCHERS = []


def setUpModule():
    def net(*a, **k):
        BLOCK["net"] += 1
        raise RuntimeError("NETWORK_BLOCKED_BY_TEST")

    def client(*a, **k):
        BLOCK["client"] += 1
        raise RuntimeError("REAL_CLIENT_CREATION_BLOCKED_BY_TEST")

    targets = [(socket.socket, "connect", net), (socket, "create_connection", net), (socket, "getaddrinfo", net)]
    import er003_v1_en_direct_vfl_01_generate as vfl01
    targets.append((vfl01, "get_client", client))
    for modname, attr in (("openai", "OpenAI"), ("google.genai", "Client")):
        try:
            m = __import__(modname, fromlist=[attr])
            targets.append((m, attr, client))
        except Exception:  # noqa: BLE001  (未installなら生成されようがない)
            pass
    for obj, name, fn in targets:
        p = mock.patch.object(obj, name, fn)
        p.start()
        _PATCHERS.append(p)


def tearDownModule():
    for p in _PATCHERS:
        p.stop()


def _theme(root):
    os.makedirs(root, exist_ok=True)
    p = os.path.join(root, "theme.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump({"theme": "mock"}, f)
    return p


def _declare(ctx):
    import er119_kp_wiring_01 as kw
    kw.declare_from_runner_args(ctx.out_dir, by="test", reason="mock test", user_ref="mock")


@contextlib.contextmanager
def _quiet():
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        yield


def _ctx(root, run="run_t", **kw):
    ctx = r.build_mock_context(root, run=run, slug="mock_slug", theme_package_path=_theme(root), **kw)
    return ctx


def _res(title, body, actual, requested):
    import types
    return types.SimpleNamespace(text="# " + title + "\n\n" + body, title=title, body=body, model_id_actual=actual, model_id_requested=requested, response_id="x",
                                 usage={}, cost_usd=0.0, cost_jpy=0.0, attempts=1, retried=False, fallback_detected=actual != requested, elapsed_seconds=0.0)


def _calls(ctx):
    return ctx.mock_api.n


class FullMockRun(unittest.TestCase):
    """一度だけ全stageを通し、成果物を複数のtestで検査する。"""

    @classmethod
    def setUpClass(cls):
        cls.root = tempfile.mkdtemp(prefix="y_runner_")
        cls.ctx = _ctx(cls.root)
        with _quiet():
            r.run_stages(cls.ctx, ["seed_check", "text", "translate", "support"])
            _declare(cls.ctx)
            r.run_stages(cls.ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        cls.out = cls.ctx.out_dir
        cls.calls_after_first = _calls(cls.ctx)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_all_stages_completed_and_manifest(self):
        man = json.load(open(f"{self.out}/final_manifest.json", encoding="utf-8"))
        self.assertEqual(man["entry_status"], "FAMILY_Y_PRODUCTION")
        self.assertEqual(man["chunk_tts"], "not_applicable_Y")
        self.assertEqual(man["core_numeric_v4_j2"], "not_applicable_Y")
        self.assertTrue(man["closing_record"]["routing_key"])           # closing_record(実model/routing/prompt sha)が最終成果物に残る
        self.assertTrue(man["closing_record"]["prompt_sha256"])
        for lv in ("b1b", "a2"):
            self.assertTrue(man["assembled"][lv] and os.path.exists(man["assembled"][lv]))
        self.assertTrue(os.path.exists(f"{self.out}/pages/index.html"))
        self.assertTrue(json.load(open(f"{self.out}/page_verify_local.json", encoding="utf-8"))["ok"])

    def test_translate_entries_record_actual_model_and_routing(self):
        prov = json.load(open(f"{self.out}/provenance.json", encoding="utf-8"))
        for unit, key in (("translate_b1b", "FAMILY_Y_TRANSLATE_ADV"), ("translate_a2", "FAMILY_Y_TRANSLATE_STD")):
            e = prov["downstream_stages"][unit]
            self.assertEqual(e["routing_key"], key)
            self.assertTrue(e["actual_model_id"].startswith(e["requested_model"]))
            self.assertTrue(e["response_id"])

    def test_api_boundary_only_mock_kinds_and_no_real_client(self):
        kinds = {json.loads(l)["kind"] for l in open(f"{self.out}/mock_api_calls.jsonl", encoding="utf-8")}
        self.assertTrue(kinds <= {"llm", "text_core", "kp", "kp_expl", "tts", "tts_shared", "tts_kp"}, kinds)
        self.assertEqual(BLOCK["client"], 0)
        self.assertEqual(BLOCK["net"], 0)

    def test_resume_is_api0_and_reuses(self):
        before = _calls(self.ctx)
        with _quiet():
            res = r.run_stages(self.ctx, ["text", "translate", "support", "kp", "tts_b1b", "tts_a2"])
        self.assertEqual(_calls(self.ctx), before, "resumeでAPI境界を通った(再利用が効いていない)")
        self.assertEqual(res["text"]["status"], "reused")
        self.assertEqual(res["tts_b1b"]["status"], "reused")
        self.assertEqual(res["translate"], {"b1b": "reused", "a2": "reused"})

    def test_timeline_has_all_y_segments_in_play_order(self):
        want = [ys.PAGE_LABEL[s] for s in ys.Y_SEGMENT_IDS]
        for lv in ("b1b", "a2"):
            tl = json.load(open(f"{self.out}/{lv}/audit/timeline.json", encoding="utf-8"))
            parts = [e["part"] for e in tl if not e["part"].startswith("pause")]
            got = [p for p in parts if p in want]
            self.assertEqual(got, want, lv)
            i = parts.index
            self.assertEqual(parts[i("Full story intro"):i("Full story intro") + 3], ["Full story intro", "Comment 1", want[0]])
            self.assertLess(i("Comment 2"), i(want[1]))
            self.assertEqual(parts[i(want[6]) + 1:i(want[6]) + 3], ["Comment 3", want[7]])      # Voice3 → Comment 3 → Closing
            self.assertEqual(parts[-1], "Outro")
            self.assertNotIn("Comment 4", parts)
            self.assertFalse([p for p in parts if "one line" in p.lower()])

    def test_tts_results_cover_segment_ids_with_voices(self):
        import er121_family_y_audio_01 as ya
        vm = ya.segment_voice_map()
        self.assertEqual(vm["y_voice_1"], "Algieba")
        self.assertEqual(vm["y_voice_2"], "Zephyr")
        self.assertEqual(vm["y_voice_3"], "Schedar")
        narrator = ya.narrator_voice()
        for sid in ys.Y_NARRATOR_IDS:
            self.assertEqual(vm[sid], narrator, sid)
        for lv in ("b1b", "a2"):
            res = json.load(open(f"{self.out}/{lv}/audit/tts_generation_results.json", encoding="utf-8"))
            for sid in ys.Y_SEGMENT_IDS:
                e = res["segments"][sid]
                self.assertEqual(e["status"], "OK")
                self.assertEqual(e["y_tts_voice_requested"], vm[sid])
            self.assertFalse({"full_story_part1", "comment_4", "in_one_line"} & set(res["segments"]))
            dec = json.load(open(f"{self.out}/{lv}/audit/chunk_tts_decision.json", encoding="utf-8"))
            self.assertIs(dec.get("chunk_tts_applicable"), True)      # 委任_04: USER_02 ①でX方式Chunkを正式採用(APPROVED_FOR_PRODUCTION)
            self.assertEqual((dec.get("method"), dec.get("approval"), dec.get("z_b_r1_adopted")), ("X_paragraph_0.2s", "APPROVED_FOR_PRODUCTION", False))

    def test_std_slowdown_for_all_y_body_segments(self):
        res = json.load(open(f"{self.out}/a2/audit/tts_generation_results.json", encoding="utf-8"))
        for sid in ys.Y_SEGMENT_IDS:
            self.assertIs(res["segments"][sid].get("slowdown_applied"), True, sid)

    def test_page_rows_labels_and_notice_outside_body(self):
        html = open(f"{self.out}/pages/index.html", encoding="utf-8").read()
        for sid in ys.Y_SEGMENT_IDS:
            self.assertIn(ys.PAGE_LABEL[sid], html)
        for sid in ys.Y_SEGMENT_IDS:                                    # 内部IDを画面に出さない
            self.assertNotIn(sid, html)
        chk = ys.check_y_page_notice(html)
        self.assertTrue(chk["ok"], chk)
        self.assertEqual(html.count(ys.PAGE_NOTICE_CLASS), 1)
        self.assertLess(html.index(ys.PAGE_NOTICE_CLASS), html.index("<table"))
        self.assertIn('name="robots" content="noindex', html)
        self.assertNotIn("In one line", html)

    def test_y_provider_collects_scripts(self):
        import er121_family_y_audio_01 as ya
        segs, extra = ya.YProvider(self.out).collect()
        ids = {s.segment_id for s in segs}
        for lv in ("b1b", "a2"):
            for sid in ys.Y_SEGMENT_IDS:
                self.assertIn(f"{lv}:{sid}", ids)
        self.assertEqual(extra, [])

    def test_study_text_slots_recorded_as_unconnected(self):
        d = json.load(open(f"{self.out}/study_text_slots.json", encoding="utf-8"))
        self.assertIn("未接続", d["part2_grammar"])
        self.assertIn("未接続", d["part1_vocabulary_expressions"])


class StageFramework(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="y_runner_")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _through_support(self, ctx):
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])

    def test_regenerate_marks_descendants_stale_and_stops_without_explicit_regenerate(self):
        ctx = _ctx(self.root)
        self._through_support(ctx)
        ctx.regenerate_stage = "translate_b1b"
        w62 = r._m().w62
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):      # b1bは明示再生成される。同一起動内のa2はstaleのため自動再生成せずSTOP
            with _quiet():
                r.stage_translate(ctx)
        prov = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        self.assertIn("translate_a2", prov["downstream_stale"])
        self.assertIn("support_b1b", prov["downstream_stale"])
        # 明示 --regenerate-stage の無い次のstageは自動再生成せずSTOP
        ctx.regenerate_stage = None
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):
            with _quiet():
                r.stage_translate(ctx)
        with self.assertRaises(w62.FamilyZProvenanceMismatchStop):
            with _quiet():
                r.stage_support(ctx)

    def test_text_change_makes_downstream_input_sha_mismatch_stop(self):
        ctx = _ctx(self.root)
        self._through_support(ctx)
        ctx.regenerate_stage = "text"
        with _quiet():
            r.stage_text(ctx)
        ctx.regenerate_stage = None
        prov = json.load(open(f"{ctx.out_dir}/provenance.json", encoding="utf-8"))
        self.assertIn("translate_b1b", prov["downstream_stale"])

    def test_unknown_regenerate_unit_rejected_by_parser(self):
        with self.assertRaises(SystemExit):
            with _quiet():
                r.build_parser().parse_args(["--regenerate-stage", "no_such_unit"])

    def test_stop_sentinel_stops_before_any_api(self):
        ctx = _ctx(self.root)
        os.makedirs(ctx.out_dir, exist_ok=True)
        open(f"{ctx.out_dir}/STOP", "w").write("{}")
        st = r._m().st
        with self.assertRaises(st.FamilyZStopSentinel):
            with _quiet():
                r.run_stages(ctx, ["text"])
        self.assertEqual(_calls(ctx), 0)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))

    def test_stop_sentinel_via_main_returns_rc3_and_no_api(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            run_dir = f"{self.root}/mock_slug/run_x_mock"
            os.makedirs(run_dir, exist_ok=True)
            open(f"{run_dir}/STOP", "w").write("{}")
            with _quiet():
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_x", "--stage", "text", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 3)
        self.assertFalse(os.path.exists(f"{run_dir}/mock_api_calls.jsonl"))

    def test_run_lock_refuses_double_launch_rc4(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            run_dir = f"{self.root}/mock_slug/run_l_mock"
            os.makedirs(run_dir, exist_ok=True)
            holder = os.getppid()                                         # 別の生存process(PIDが生きている)
            json.dump({"pid": holder, "started_ts": 0, "argv": []}, open(f"{run_dir}/RUN_LOCK.json", "w"))
            with mock.patch.object(r._m().st, "pid_alive", lambda pid: True):
                with _quiet():
                    rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_l", "--stage", "text", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, r._m().st.LOCK_EXIT_CODE)
        self.assertFalse(os.path.exists(f"{run_dir}/mock_api_calls.jsonl"))

    def test_restart_storm_stops_with_rc3_and_creates_stop(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            rcs = []
            for _ in range(3):
                with _quiet():
                    rcs.append(r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_s", "--stage", "seed_check", "--theme-package", _theme(self.root)]))
        self.assertEqual(rcs[:2], [0, 0])
        self.assertEqual(rcs[2], r._m().st.STOP_EXIT_CODE)
        self.assertTrue(os.path.exists(f"{self.root}/mock_slug/run_s_mock/STOP"))

    def test_kp_pending_returns_rc4_with_marker_and_stops_before_paid_stages(self):
        out = io.StringIO()
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_k", "--stages", "text,translate,support,kp,tts_b1b,tts_a2",
                             "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 4)
        self.assertIn("[KP_REVIEW_PENDING]", out.getvalue())
        run_dir = f"{self.root}/mock_slug/run_k_mock"
        self.assertTrue(os.path.exists(f"{run_dir}/kp_review_pending.json"))
        self.assertFalse(os.path.exists(f"{run_dir}/b1b/audit/tts_generation_results.json"), "KP待機中にTTSへ進んだ")
        kinds = [json.loads(l)["kind"] for l in open(f"{run_dir}/mock_api_calls.jsonl", encoding="utf-8")]
        self.assertFalse([k for k in kinds if k.startswith("tts")])

    def test_kp_auto_requires_by_and_reason(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = r.main(["--mode", "mock", "--slug", "mock_slug", "--run", "run_a", "--stage", "seed_check", "--kp-review", "auto",
                             "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 2)

    def test_dry_run_has_zero_side_effects(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            before = sorted(os.listdir(self.root))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = r.main(["--mode", "dry-run", "--slug", "mock_slug", "--run", "run_d"])
        self.assertEqual(rc, 0)
        self.assertEqual(sorted(os.listdir(self.root)), before)
        plan = json.loads(out.getvalue())
        self.assertEqual(plan["api_calls"], 0)
        self.assertEqual(plan["side_effects"], 0)
        self.assertEqual([s["stage"] for s in plan["stages"]], list(r.STAGES))

    def test_default_mode_is_dry_run_and_real_needs_budget_before_any_client(self):
        self.assertEqual(r.build_parser().parse_args([]).mode, "dry-run")
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with _quiet():
                rc = r.main(["--mode", "real", "--slug", "mock_slug", "--run", "run_r", "--stage", "seed_check", "--theme-package", _theme(self.root)])
        self.assertEqual(rc, 2)                                         # 予算未承認 → clientもcost_logもdirも作らずSTOP
        self.assertEqual(BLOCK["client"], 0)
        self.assertFalse(os.path.exists(f"{self.root}/mock_slug/run_r"))

    def test_budget_cap_and_guard(self):
        with self.assertRaises(r.YBudgetStop):
            r.E2EBudget(r.APPROVED_BUDGET_MAX_JPY + 1)
        with self.assertRaises(r.YBudgetStop):
            r.E2EBudget(0)
        ctx = _ctx(self.root)
        ctx.budget = r.E2EBudget(10, 5, spent_fn=lambda: 4.9)            # 警告閾値5円: 4.9+見積(text 45)は超過
        with self.assertRaises(r.YBudgetStop):
            with _quiet():
                r.run_stages(ctx, ["text"])
        self.assertEqual(_calls(ctx), 0, "予算超過見込みなのに新規API境界を通った")

    def test_text_core_not_connected_stops_without_artifact(self):
        ctx = _ctx(self.root, hooks={"text_core": object()})
        with self.assertRaises(r.YTextCoreNotConnected):
            with _quiet():
                r.stage_text(ctx)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))
        self.assertEqual(_calls(ctx), 0)

    def test_text_core_without_closing_record_stops(self):
        class TC:
            def produce_article(self, client, **kw):
                return {"title": "t", "lead": "l", "intros": {}, "voices": {}, "closing": "c"}
        ctx = _ctx(self.root, hooks={"text_core": TC()})
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_text(ctx)
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/text/article_ja.md"))

    def test_text_requires_theme_package(self):
        ctx = r.build_mock_context(self.root, run="run_np", slug="mock_slug", theme_package_path=None)
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_text(ctx)

    def test_ja_ai_announce_in_text_stops(self):
        class TC:
            def produce_article(self, client, **kw):
                return {"title": "t", "lead": "実在する人々の声を組み立てました。", "intros": {"voice_1": "a", "voice_2": "b", "voice_3": "c"},
                        "voices": {"voice_1": "私は", "voice_2": "私は", "voice_3": "私は"}, "closing": "終わり", "closing_record": {"source": "x"}}
        ctx = _ctx(self.root, hooks={"text_core": TC()})
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_text(ctx)
        self.assertIn("AI_ANNOUNCE", str(cm.exception))

    def _bad_adv_fn(self, calls):
        def fn(ja, *, client=None, model=None, must_fix=None, **kw):
            calls.append(must_fix)
            body = "p1\n\np2\n\np3"
            return _res("T", body, model, model)
        return fn

    def test_translate_structure_violation_retries_once_then_stops(self):
        calls = []
        try:
            fn = self._bad_adv_fn(calls)
        except TypeError:
            self.skipTest("result dataclass fields changed")
        ctx = _ctx(self.root, hooks={"translate_adv_fn": fn})
        with _quiet():
            r.run_stages(ctx, ["text"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_translate(ctx)
        self.assertIn("FAMILY_Y_EN_CONTRACT_VIOLATION", str(cm.exception))
        self.assertEqual(len(calls), 2, "再試行は構造違反につき1回だけ(初回+再試行1)")
        self.assertFalse(os.path.exists(r._level_text_path(ctx, "b1b")), "契約違反の英訳を成果物として残した")

    def test_translate_model_drift_stops(self):
        import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
        def fn(ja, *, client=None, model=None, must_fix=None, **kw):
            import er121_family_y_mock_01 as mk
            body = mk.EN_ADV.split("\n\n", 1)[1]
            return _res(mk.SAMPLE_TITLE_EN, body, "other-model", model)
        ctx = _ctx(self.root, hooks={"translate_adv_fn": fn})
        with _quiet():
            r.run_stages(ctx, ["text"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_translate(ctx)
        self.assertIn("MODEL_DRIFT", str(cm.exception))

    def test_tts_without_mock_patch_stops_before_any_tts(self):
        ctx = _ctx(self.root)
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])
            _declare(ctx)
            r.run_stages(ctx, ["kp"])
        ctx.hooks.pop("tts_patch")
        n = _calls(ctx)
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_tts(ctx, "b1b")
        self.assertIn("NO_MOCK_TTS", str(cm.exception))
        self.assertEqual(_calls(ctx), n)

    def test_gate_and_assemble_refuse_stale_or_missing_tts(self):
        ctx = _ctx(self.root)
        with _quiet():
            r.run_stages(ctx, ["text", "translate", "support"])
        with self.assertRaises(r.YE2EStop) as cm:
            with _quiet():
                r.stage_gate(ctx)
        self.assertIn("NOT_FRESH", str(cm.exception))
        with self.assertRaises(r.YE2EStop):
            with _quiet():
                r.stage_assemble(ctx)

    def test_seed_check_fail_closed_on_unregistered_key(self):
        import er006_model_routing_contract_01 as routing
        ctx = _ctx(self.root)
        saved = routing.PROCESS_MODEL_MAP.pop("FAMILY_Y_LEAD_GENERATE")
        try:
            with self.assertRaises(r.YE2EStop):
                r.stage_seed_check(ctx)
        finally:
            routing.PROCESS_MODEL_MAP["FAMILY_Y_LEAD_GENERATE"] = saved
        self.assertEqual(r.stage_seed_check(ctx)["voice_assignment"]["y_fixed_slots"]["voice_1"], "Algieba")

    def test_clear_stop_requires_reason(self):
        with mock.patch.object(r, "RUN_ROOT", self.root):
            with _quiet():
                self.assertEqual(r.main(["--clear-stop", "--slug", "mock_slug", "--run", "run_c"]), 2)



class SelfConsistency(unittest.TestCase):
    def test_dependents_only_reference_known_units(self):
        for k, v in r.DEPENDENTS.items():
            self.assertIn(k, r.UNIT_NAMES)
            for x in v:
                self.assertIn(x, r.UNIT_NAMES)

    def test_no_er110_import_and_no_chunk_or_core_numeric_import(self):
        banned_prefix = ("er110_", "er095_", "er118_")      # 委任_04: er117(X方式Chunk共通module)はUSER_02 ①で採用。importしてよいのはaudit moduleのみ(下で固定)
        for fn in ("er121_family_y_runner_01.py", "er121_family_y_audio_01.py", "er121_family_y_structure_01.py", "er121_family_y_mock_01.py"):
            tree = ast.parse(open(os.path.join(ROOT, fn), encoding="utf-8").read())
            for n in ast.walk(tree):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] if isinstance(n, ast.ImportFrom) and n.module else [])
                for m in mods:
                    self.assertFalse(m.startswith(banned_prefix), f"{fn} が {m} をimportしている(DEV Trial/Chunk/中核数値の混入禁止)")

    def test_stage_names_include_kp_review_and_no_part_stage(self):
        self.assertIn("kp", r.STAGES)
        self.assertFalse([s for s in r.STAGES if "part2" in s or "in_one_line" in s])


if __name__ == "__main__":
    unittest.main()
