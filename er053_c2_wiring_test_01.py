# -*- coding: utf-8 -*-
"""RISK-FLAGGER-PRODUCTION-WIRING-01 Phase 2 C2(2026-10-10)。Production正式入口 main() の配線test(API呼び出し0、費用0円)。

er019_family_x_entertainment_production_runner_01.main() を、外部呼出(Research/B3/W-1/英訳/RF)をstub化して駆動し、
  (5) RF配線順序: Writer -> Advanced英訳 -> Advanced RF -> Standard生成 -> Standard RF(->Queue保存)、
      Flagあり/RF_UNAVAILABLEでも次工程へ進む、RFは cl.logging_context ブロックの外、記事sha不変
  (3) 契約fail-closed: 注記なし -> 課金前STOP(stub client未呼出、英訳もRFも呼ばれない)
  U-1: 来歴なし旧Writer記事の再利用 -> STOP(英訳・RF未呼出)
  再利用/再生成/--stop-after の各経路で旧Checkerが呼ばれないこと(vfl01.run_deviation_check を spy、呼ばれたら失敗)
を確認する。

実行: .venv/Scripts/python.exe -m pytest er053_c2_wiring_test_01.py -q
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er005_cost_logger as cl
import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_dev_b3_fixture_adapter_01 as adapter

HERE = os.path.dirname(os.path.abspath(__file__))


def _boom(*a, **k):
    raise AssertionError("旧Checker(vfl01.run_deviation_check)が呼ばれた")


class Rec:
    """main() の外部呼出を記録するstub群。"""

    def __init__(self, out_dir, rf_status="OK", ctx_probe=True):
        self.events = []
        self.out = out_dir
        self.rf_status = rf_status
        self.ctx = []

    def research(self, client, topic, ledger_dir):
        self.events.append("research_ledger")
        return {"ledger_text": "LEDGER"}

    def storyline(self, client, topic, ledger_text, out_dir):
        self.events.append("storyline_b3")
        return {"selected_storyline": "S", "selected_fact_brief_text": "B"}

    def writer(self, client, out_dir, budget_jpy):
        self.events.append("writer")
        return {"ja_text": "JA", "title": "T", "runtime_evidence": {}}

    def writer_stage(self, client, theme, ja_text, ledger_text, budget_jpy, only=None, **kw):
        assert not kw, f"legacy kwargs passed: {kw}"
        self.events.append(only)
        self.ctx.append((only, cl._CONTEXT.get("stage")))
        lv = "b1b" if only == "advanced" else "a2"
        os.makedirs(f"{self.out}/{lv}", exist_ok=True)
        with open(f"{self.out}/{lv}/article.md", "w", encoding="utf-8") as f:
            f.write(f"# {only}\n\nSentence one. Sentence two.\n")
        return {}

    def risk_flag(self, out_dir, level, budget_jpy, run_label=None):
        self.events.append(f"rf:{level}")
        self.ctx.append((f"rf:{level}", cl._CONTEXT.get("stage")))
        return {"status": self.rf_status, "queue": {"saved": True}}


def run_main(out_dir, argv_extra, rec, pre=None):
    argv = ["runner", "--theme", "THEME", "--slug", "s", "--out-dir", out_dir, *argv_extra]
    patches = [
        mock.patch.object(sys, "argv", argv),
        mock.patch.object(runner.cl, "install"),
        mock.patch.object(runner.vfl01, "get_client", return_value=object()),
        mock.patch.object(runner, "run_research_and_ledger", side_effect=rec.research),
        mock.patch.object(runner, "run_storyline_b3", side_effect=rec.storyline),
        mock.patch.object(runner, "run_ja_writer", side_effect=rec.writer),
        mock.patch.object(runner.efam, "run_writer_stage", side_effect=rec.writer_stage),
        mock.patch.object(runner, "run_post_en_risk_flag", side_effect=rec.risk_flag),
        mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0),
        mock.patch.object(runner.vfl01, "run_deviation_check", side_effect=_boom),
    ]
    for p in patches:
        p.start()
    try:
        runner.main()
    finally:
        for p in reversed(patches):
            p.stop()


def make_fixture_out(with_w1_ja=True, chain="W-1", slug="meta"):
    d = tempfile.mkdtemp(prefix="c2_main_")
    adapter.build_fixture(slug, d)
    if with_w1_ja:
        jd = os.path.join(d, "ja_writer")
        os.makedirs(jd)
        with open(os.path.join(jd, "revision2.md"), "w", encoding="utf-8") as f:
            f.write("W-1の日本語記事")
        with open(os.path.join(jd, "runtime_evidence.json"), "w", encoding="utf-8") as f:
            json.dump({"chain_method": chain,
                       "annotated_md_sha256": contract.validate_annotated_b3(d).annotated_md_sha256}, f)
    return d


class MainOrderTests(unittest.TestCase):
    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="c2_main_new_")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_initial_full_run_order_advanced_rf_standard_rf(self):
        rec = Rec(self.out)
        run_main(self.out, [], rec)       # --stage all(既定)、初回(storyline/writerとも新規)
        self.assertEqual(rec.events, ["research_ledger", "storyline_b3", "writer", "advanced", "rf:b1b", "standard", "rf:a2"])

    def test_rf_is_outside_logging_context_and_writer_stages_inside(self):
        rec = Rec(self.out)
        run_main(self.out, [], rec)
        d = dict(rec.ctx)
        self.assertEqual(d["advanced"], "advanced")
        self.assertEqual(d["standard"], "standard")
        self.assertIsNone(d["rf:b1b"])        # RFは cl.logging_context ブロックの外
        self.assertIsNone(d["rf:a2"])

    def test_standard_generation_starts_after_advanced_rf(self):
        rec = Rec(self.out)
        run_main(self.out, [], rec)
        e = rec.events
        self.assertLess(e.index("rf:b1b"), e.index("standard"))
        self.assertLess(e.index("standard"), e.index("rf:a2"))

    def test_stop_after_advanced_runs_advanced_rf_then_stops(self):
        rec = Rec(self.out)
        run_main(self.out, ["--stop-after", "advanced"], rec)
        self.assertEqual(rec.events[-2:], ["advanced", "rf:b1b"])
        self.assertNotIn("standard", rec.events)
        self.assertNotIn("rf:a2", rec.events)

    def test_flagged_and_rf_unavailable_still_proceed_to_standard_and_end(self):
        for st in ("OK", "PARTIAL", "RF_UNAVAILABLE"):
            out = tempfile.mkdtemp(prefix="c2_main_st_")
            try:
                rec = Rec(out, rf_status=st)
                run_main(out, [], rec)       # 例外なく完走(=次工程へ進む)
                self.assertEqual(rec.events[-3:], ["rf:b1b", "standard", "rf:a2"], st)
                self.assertTrue(os.path.exists(os.path.join(out, "cost.json")))
            finally:
                shutil.rmtree(out, ignore_errors=True)

    def test_no_tts_scaffold_assemble_stage_exists(self):
        for name in ("run_scaffold_stage", "run_tts_stage", "run_assemble_stage", "build_player_html"):
            self.assertFalse(hasattr(runner, name), name)

    def test_run_label_is_record_only_and_passed_to_rf(self):
        rec = Rec(self.out)
        labels = []
        orig = rec.risk_flag

        def spy(out_dir, level, budget_jpy, run_label=None):
            labels.append(run_label)
            return orig(out_dir, level, budget_jpy, run_label=run_label)

        rec.risk_flag = spy
        run_main(self.out, ["--run-label", "W1_DOWNSTREAM_DEV_CONFIRM"], rec)
        self.assertEqual(labels, ["W1_DOWNSTREAM_DEV_CONFIRM"] * 2)
        ep = json.load(open(os.path.join(self.out, "entry_point.json"), encoding="utf-8"))
        self.assertEqual(ep["args"]["run_label"], "W1_DOWNSTREAM_DEV_CONFIRM")
        self.assertIn("risk_flagger_module_sha256", ep)
        self.assertIn("annotation_contract_module_sha256", ep)


class ResumeAndRegenerationPathTests(unittest.TestCase):
    """再利用(resume)/再生成(regeneration)経路。旧Checker(vfl01.run_deviation_check)が呼ばれたら失敗。"""

    def test_resume_standard_only_reuses_w1_ja_after_provenance_check(self):
        out = make_fixture_out()
        try:
            rec = Rec(out)
            run_main(out, ["--stage", "standard"], rec)
            self.assertEqual(rec.events, ["research_ledger", "standard", "rf:a2"])    # Writer再実行なし
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_resume_advanced_reuses_w1_ja(self):
        out = make_fixture_out()
        try:
            rec = Rec(out)
            run_main(out, ["--stage", "advanced", "--stop-after", "advanced"], rec)
            self.assertEqual(rec.events, ["research_ledger", "advanced", "rf:b1b"])
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_u1_legacy_ja_without_provenance_stops_before_translation_and_rf(self):
        out = make_fixture_out(with_w1_ja=False)
        try:
            jd = os.path.join(out, "ja_writer")
            os.makedirs(jd)
            with open(os.path.join(jd, "revision2.md"), "w", encoding="utf-8") as f:
                f.write("旧Writer(Luna連鎖)の記事")
            rec = Rec(out)
            with self.assertRaises(runner.LegacyWriterProvenanceStop):
                run_main(out, ["--stage", "standard"], rec)
            self.assertEqual(rec.events, ["research_ledger"])           # 英訳・RFへ進まない
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_u1_old_chain_method_stops(self):
        out = make_fixture_out(chain="previous_response_id")
        try:
            rec = Rec(out)
            with self.assertRaises(runner.LegacyWriterProvenanceStop):
                run_main(out, ["--stage", "all"], rec)
            self.assertNotIn("advanced", rec.events)
            self.assertNotIn("writer", rec.events)       # 再利用分岐でSTOP(旧記事を黙って再生成もしない)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_regenerate_writer_calls_w1_not_reuse(self):
        out = make_fixture_out(with_w1_ja=True)
        try:
            rec = Rec(out)
            run_main(out, ["--regenerate-stage", "writer"], rec)
            self.assertIn("writer", rec.events)
            self.assertEqual(rec.events[-4:], ["advanced", "rf:b1b", "standard", "rf:a2"])
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_regenerate_advanced_then_standard_follow_with_rf_each(self):
        out = make_fixture_out()
        try:
            rec = Rec(out)
            run_main(out, ["--regenerate-stage", "advanced"], rec)    # stage既定all -> Advanced+Standard再生成
            self.assertEqual(rec.events[-4:], ["advanced", "rf:b1b", "standard", "rf:a2"])
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_regenerate_storyline_reruns_b3_then_writer_validates_contract(self):
        out = make_fixture_out()
        try:
            rec = Rec(out)
            run_main(out, ["--regenerate-stage", "storyline_b3", "--stop-after", "storyline_b3"], rec)
            self.assertEqual(rec.events, ["research_ledger", "storyline_b3"])
        finally:
            shutil.rmtree(out, ignore_errors=True)


class MainContractFailClosedTests(unittest.TestCase):
    def test_no_annotation_stops_at_writer_before_translation_rf_and_api(self):
        """実 run_ja_writer(契約検証)を通す。注記なし -> AnnotatedB3ContractViolation、英訳・RFは呼ばれない。"""
        out = tempfile.mkdtemp(prefix="c2_main_noann_")
        try:
            os.makedirs(os.path.join(out, "storyline_b3"))
            with open(os.path.join(out, "storyline_b3", "selected_brief.md"), "w", encoding="utf-8") as f:
                f.write("# Selected Fact Brief\n\n## Storyline\nS\n\n## Selected Facts\n- f\n")
            rec = Rec(out)
            argv = ["runner", "--theme", "T", "--slug", "s", "--out-dir", out]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(runner.cl, "install"), \
                    mock.patch.object(runner.vfl01, "get_client", return_value=object()), \
                    mock.patch.object(runner, "run_research_and_ledger", side_effect=rec.research), \
                    mock.patch.object(runner.efam, "run_writer_stage", side_effect=rec.writer_stage), \
                    mock.patch.object(runner, "run_post_en_risk_flag", side_effect=rec.risk_flag), \
                    mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0), \
                    mock.patch.object(runner.w1, "call_astra", side_effect=_boom), \
                    mock.patch.object(runner.w1, "call_luna_r0", side_effect=_boom):
                with self.assertRaises(contract.AnnotatedB3ContractViolation):
                    runner.main()
            self.assertEqual(rec.events, ["research_ledger"])
        finally:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
