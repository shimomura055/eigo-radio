# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_06 C-2: 中核数値丸めの配線(W1〜W6)・Opus条件(P-01〜P-08)の統合test。
API 0・費用0円(client/judge/Writer応答はstub。producer/契約/W-1/runner helper/cost.jsonは実コード)。
実行: .venv/Scripts/python.exe -m unittest er095_b3_core_number_rounding_01_wiring_test_01
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import er019_family_x_entertainment_production_runner_01 as runner
import er053_b3_annotation_contract_01 as contract
import er053_b3_deterministic_producer_01 as prod
import er053_dev_b3_fixture_adapter_01 as adapter
import er053_family_x_factlock_ja_writer_01 as w1
import er095_b3_core_number_rounding_01 as m

HERE = os.path.dirname(os.path.abspath(__file__))
V8_FIXTURE = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02", "evidence", "v8_regression_90.json")
DATASET = os.path.join(HERE, "er090_output", "b3_core_number_rounding_trial_02", "dataset")


def judge_json_for(sidecar, approx_map):
    """approx_map: {surface: approx_surface}。含まれるsurfaceを持つconceptだけAPPROXIMATE_OK、他はEXACT_REQUIRED。"""
    decisions = []
    for c in m.core_concepts(sidecar):
        if all(s in approx_map for s in c["surfaces"]):
            decisions.append({"concept": c["concept"], "decision": m.DECISION_APPROX,
                              "surfaces": [{"surface": s, "approx_surface": approx_map[s]} for s in c["surfaces"]],
                              "reason": "r", "basis_fact_ids": list(c["ledger_ids"]), "approved_condition": "c"})
        else:
            decisions.append({"concept": c["concept"], "decision": m.DECISION_EXACT,
                              "surfaces": [{"surface": s, "approx_surface": None} for s in c["surfaces"]],
                              "reason": "r", "basis_fact_ids": list(c["ledger_ids"]), "approved_condition": "c"})
    return {"decisions": decisions}


def judge_stub(approx_map, model="gpt-6-luna-2026-10-01"):
    def _j(client, prompt, tag):
        ann = _j.annotated
        return {"parsed": judge_json_for(ann.sidecar, approx_map), "model_requested": "gpt-6-luna", "model_returned": model,
                "response_id": "resp_stub", "sec": 0.1, "effort": "low", "usage": {"input_tokens": 1, "output_tokens": 1, "reasoning_tokens": 0}}
    return _j


class WriterClient:
    """W-1のR0(Sol)/R1/R2 stub。呼出promptを記録する。"""

    def __init__(self, r0_text="メタの話\n車が回収されました。【事実1】\nこれは面白いですね。\n"):
        self.responses = self
        self.prompts, self.n = [], 0
        self.scripts = [r0_text, "# タイトル\n\n本文その1です。続きの文です。", "# 新タイトル\n\n本文その2です。続きの文です。"]

    def create(self, **kw):
        self.prompts.append(kw["input"][-1]["content"])
        text = self.scripts[self.n]
        self.n += 1
        return SimpleNamespace(output_text=text, model="gpt-6.1-sol", id="resp_%d" % self.n,
                               usage=SimpleNamespace(input_tokens=10, output_tokens=10))


def _args(regenerate=None, budget=150.0):
    return SimpleNamespace(regenerate_stage=regenerate, budget_jpy=budget)


class Base(unittest.TestCase):
    THEME = "byd_recall"
    APPROX = {"142,895台": "約14万3千台", "183,211台": "約18万3千台"}

    def setUp(self):
        self.out = tempfile.mkdtemp(prefix="b3rd_wire_")
        adapter.build_fixture(self.THEME, self.out)
        self.ledger = open(os.path.join(self.out, "research_ledger", "verified_fact_ledger.txt"), encoding="utf-8").read()
        patches = [mock.patch.object(runner.efam, "assert_budget_ok", return_value=0.0), mock.patch.object(w1.time, "sleep", lambda s: None)]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def ann(self):
        return contract.validate_annotated_b3(self.out)

    def make_overlay(self, approx=None, judge_model="gpt-6-luna-2026-10-01"):
        a = self.ann()
        j = judge_stub(self.APPROX if approx is None else approx, judge_model)
        j.annotated = a
        return m.run_core_number_rounding(None, self.out, a, w1.parse_brief_md, self.ledger, judge=j)


class TestRunnerHelperW1(Base):
    def run_helper(self, stage="all", regenerate=None, judge=None, **kw):
        j = judge or judge_stub(self.APPROX)
        j.annotated = self.ann()
        with mock.patch.object(m, "judge_call", j):
            return runner.run_core_number_rounding(None, self.out, self.ledger, _args(regenerate), stage)

    def test_first_run_judges_once_and_persists_overlay_with_luna_low_provenance(self):
        r = self.run_helper()
        self.assertEqual((r["status"], r["api_calls"], r["n_approximate_ok"]), ("OK", 1, 2))
        ov = json.load(open(m.overlay_path(self.out), encoding="utf-8"))
        self.assertTrue(ov["judge"]["model_returned"].startswith("gpt-6-luna"))
        self.assertEqual((ov["judge"]["effort"], ov["role_key"], ov["status"]), ("low", "FAMILY_X_B3_CORE_NUMBER_ROUNDING", "OK"))

    def test_second_run_reuses_without_api_even_for_writer_resume(self):
        self.run_helper()
        calls = []
        j = judge_stub(self.APPROX)
        j.annotated = self.ann()
        with mock.patch.object(m, "judge_call", lambda *a, **k: calls.append(1) or j(*a)):
            r = runner.run_core_number_rounding(None, self.out, self.ledger, _args(), "writer")     # --stage writer（既存revision2なし）
        self.assertEqual((r["reused"], r["api_calls"], calls), (True, 0, []))

    def test_regenerate_writer_rejudges_P01(self):
        self.run_helper()
        calls = []
        j = judge_stub(self.APPROX)
        j.annotated = self.ann()
        with mock.patch.object(m, "judge_call", lambda *a, **k: calls.append(1) or j(*a)):
            r = runner.run_core_number_rounding(None, self.out, self.ledger, _args("writer"), "all")
        self.assertEqual((r["reused"], r["api_calls"]), (False, 1))

    def test_ja_reuse_path_does_not_judge_P02(self):
        os.makedirs(os.path.join(self.out, "ja_writer"))
        open(os.path.join(self.out, "ja_writer", "revision2.md"), "w", encoding="utf-8").write("既存JA")
        calls = []
        with mock.patch.object(m, "judge_call", lambda *a, **k: calls.append(1)):
            r = runner.run_core_number_rounding(None, self.out, self.ledger, _args(), "standard")       # --stage standard: JA再利用経路
        self.assertEqual((r["status"], r["api_calls"], calls), ("NOT_JUDGED_REUSE_PATH", 0, []))
        self.assertFalse(os.path.exists(m.overlay_path(self.out)))

    def test_warn_printed_and_status_recorded_on_judge_failure_P03(self):
        def down(*a, **k):
            raise OSError("api down")
        import io
        import contextlib
        buf = io.StringIO()
        with mock.patch.object(m, "judge_call", down), contextlib.redirect_stdout(buf):
            r = runner.run_core_number_rounding(None, self.out, self.ledger, _args(), "all")
        self.assertEqual(r["status"], m.STATUS_API_ERROR)
        self.assertIn("[WARN][core_number_rounding]", buf.getvalue())
        runner._write_cost_json(self.out)
        cj = json.load(open(os.path.join(self.out, "cost.json"), encoding="utf-8"))
        self.assertEqual((cj["b3_core_number_rounding"]["status"], cj["b3_core_number_rounding"]["warn"]), (m.STATUS_API_ERROR, True))

    def test_cost_json_records_ok_status_and_model(self):
        self.run_helper()
        runner._write_cost_json(self.out)
        cj = json.load(open(os.path.join(self.out, "cost.json"), encoding="utf-8"))["b3_core_number_rounding"]
        self.assertEqual((cj["status"], cj["n_approximate_ok"], cj["effort"], cj["warn"]), ("OK", 2, "low", False))
        self.assertTrue(cj["model_returned"].startswith("gpt-6-luna"))


class TestWriterW2W3W4W6(Base):
    def test_no_overlay_news_field_and_prompt_byte_identical_P07(self):
        a = self.ann()
        client = WriterClient()
        w1.run_w1_writer(self.out, client=client)
        self.assertIn(a.news_field_text, client.prompts[0])
        self.assertEqual(client.prompts[0], w1.build_r0_prompt(*w1.parse_brief_md(a.annotated_md_text)[:1], a.news_field_text))
        ev = json.load(open(os.path.join(self.out, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
        self.assertEqual(ev["rounding"]["reason"], "overlay_absent")
        self.assertFalse(ev["rounding"]["applied"])
        self.assertEqual(ev["rounding"]["news_field_sha256_before"], ev["rounding"]["news_field_sha256_after"])
        self.assertEqual(ev["news_field_sha256"], ev["rounding"]["news_field_sha256_after"])

    def test_zero_approx_overlay_is_byte_identical_P07(self):
        self.make_overlay(approx={})                      # 全EXACT
        a = self.ann()
        ov, rev = m.load_overlay_for_writer(self.out, a.annotated_md_sha256)
        self.assertEqual(rev["reason"], "no_approximate_ok")
        client = WriterClient()
        w1.run_w1_writer(self.out, client=client)
        self.assertEqual(client.prompts[0], w1.build_r0_prompt(w1.parse_brief_md(a.annotated_md_text)[0], a.news_field_text))
        self.assertNotIn("【概数表記】", client.prompts[0])
        self.assertNotIn(m.RULE8_TEXT, client.prompts[0])

    def test_overlay_adds_constraint_lines_and_rule8_and_provenance_P11(self):
        r = self.make_overlay()
        self.assertEqual(r["n_approximate_ok"], 2)
        a = self.ann()
        client = WriterClient()
        w1.run_w1_writer(self.out, client=client)
        p0 = client.prompts[0]
        self.assertEqual(p0.count("【概数表記】「142,895台」は「約14万3千台」"), 1)
        self.assertEqual(p0.count("【概数表記】「183,211台」は「約18万3千台」"), 1)
        self.assertTrue(p0.endswith(m.RULE8_TEXT))
        self.assertNotEqual(p0, w1.build_r0_prompt(w1.parse_brief_md(a.annotated_md_text)[0], a.news_field_text))   # 追加分のみ差がある
        base = w1.build_r0_prompt(w1.parse_brief_md(a.annotated_md_text)[0], a.news_field_text)
        self.assertEqual(len(p0) - len(base), len(m.RULE8_TEXT) + len("\n".join(m.constraint_lines(m.load_overlay_for_writer(self.out, a.annotated_md_sha256)[0])) + "\n"))
        ev = json.load(open(os.path.join(self.out, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
        rd = ev["rounding"]
        self.assertTrue(rd["applied"] and rd["rule8_in_prompt"] and rd["enabled"])
        self.assertEqual((rd["overlay_status"], rd["judge_effort"], rd["n_approximate_ok"]), ("OK", "low", 2))
        self.assertTrue(rd["judge_model_returned"].startswith("gpt-6-luna"))
        self.assertNotEqual(rd["news_field_sha256_before"], rd["news_field_sha256_after"])
        self.assertEqual(ev["news_field_sha256"], rd["news_field_sha256_after"])
        r0 = json.load(open(os.path.join(self.out, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))
        self.assertEqual(r0["r0_prompt_sha256"], rd["r0_prompt_sha256"])

    def test_symbol_regen_prompt_also_has_rule8(self):
        self.make_overlay()
        a = self.ann()
        ov, _ = m.load_overlay_for_writer(self.out, a.annotated_md_sha256)
        story = w1.parse_brief_md(a.annotated_md_text)[0]
        p2 = w1.build_r0_symbol_regen_prompt(story, "NEWS", [], ov)
        self.assertIn(m.RULE8_TEXT, p2)
        self.assertEqual(w1.build_r0_symbol_regen_prompt(story, "NEWS", []),
                         w1.build_r0_prompt(story, "NEWS") + "\n\n" + w1.safety.build_symbol_violation_prompt_note([]))

    def test_flag_off_is_byte_identical_and_no_judge(self):
        self.make_overlay()
        m.B3_CORE_NUMBER_ROUNDING_ENABLED = False
        try:
            a = self.ann()
            client = WriterClient()
            w1.run_w1_writer(self.out, client=client)
            self.assertEqual(client.prompts[0], w1.build_r0_prompt(w1.parse_brief_md(a.annotated_md_text)[0], a.news_field_text))
            ev = json.load(open(os.path.join(self.out, "ja_writer", "runtime_evidence.json"), encoding="utf-8"))
            self.assertEqual((ev["rounding"]["enabled"], ev["rounding"]["reason"]), (False, "flag_off"))
        finally:
            m.B3_CORE_NUMBER_ROUNDING_ENABLED = True

    def test_approx_mark_echo_is_stripped_counted_and_warned_S5_P08(self):
        self.make_overlay()
        import io
        import contextlib
        client = WriterClient(r0_text="メタ\n【概数表記】車が約14万3千台回収されました。【事実1】\n【 概数表記 】これは面白いですね。\n【中核数値】\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = w1.run_w1_writer(self.out, client=client)                  # TagLeakにならない
        r0m = json.load(open(os.path.join(self.out, "ja_writer", "factlock", "r0_meta.json"), encoding="utf-8"))
        self.assertEqual((r0m["approx_marks_echoed"], r0m["marks_echoed"]), (2, 1))
        self.assertIn("[WARN][W1][r0]", buf.getvalue())
        r0 = open(os.path.join(self.out, "ja_writer", "factlock", "r0.md"), encoding="utf-8").read()
        self.assertNotIn("概数表記", r0)
        self.assertNotIn("概数表記", res["ja_text"])

    def test_s5_tag_leak_detects_other_variants(self):
        with self.assertRaises(w1.TagLeak):
            w1.assert_no_tag_leak("本文【概数表記：約14万】")        # 正確な形でない変形はTagLeak(除去されない)
        self.assertEqual(w1.strip_tags("a【概数表記】b【 概数表記 】c"), "abc")


class TestResumeW5(Base):
    def seed_ja(self, rounding_rec):
        d = os.path.join(self.out, "ja_writer")
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "revision2.md"), "w", encoding="utf-8").write("W-1の日本語記事")
        ev = {"chain_method": "W-1", "annotated_md_sha256": self.ann().annotated_md_sha256}
        if rounding_rec is not None:
            ev["rounding"] = rounding_rec
        json.dump(ev, open(os.path.join(d, "runtime_evidence.json"), "w", encoding="utf-8"))

    def test_resume_api_zero_and_provenance_match_P11_3(self):
        self.make_overlay()
        client = WriterClient()
        w1.run_w1_writer(self.out, client=client)                           # 実Writer経由でevidence["rounding"]を記録
        n = client.n
        self.assertEqual(runner.load_reused_ja_text(self.out), open(os.path.join(self.out, "ja_writer", "revision2.md"), encoding="utf-8").read())
        self.assertEqual(client.n, n)                                        # resume: API 0

    def test_legacy_article_without_rounding_key_is_reused(self):
        self.seed_ja(None)
        self.assertEqual(runner.load_reused_ja_text(self.out), "W-1の日本語記事")

    def test_overlay_replaced_after_ja_stops_P01(self):
        self.make_overlay()
        self.seed_ja({"enabled": True, "overlay_sha256": m.current_overlay_sha(self.out)})
        self.assertEqual(runner.load_reused_ja_text(self.out), "W-1の日本語記事")
        os.remove(m.overlay_path(self.out))
        self.make_overlay(approx={})                                         # 同一B3版で別内容のoverlay(手動差替え想定)
        with self.assertRaises(runner.LegacyWriterProvenanceStop) as cm:
            runner.load_reused_ja_text(self.out)
        self.assertIn("PROVENANCE_MISMATCH", str(cm.exception))

    def test_status_not_ok_overlay_is_checked_too(self):
        def down(*a, **k):
            raise OSError("x")
        m.run_core_number_rounding(None, self.out, self.ann(), w1.parse_brief_md, self.ledger, judge=down)
        self.seed_ja({"enabled": True, "overlay_sha256": m.current_overlay_sha(self.out)})
        self.assertEqual(runner.load_reused_ja_text(self.out), "W-1の日本語記事")
        self.seed_ja({"enabled": True, "overlay_sha256": "other"})
        with self.assertRaises(runner.LegacyWriterProvenanceStop):
            runner.load_reused_ja_text(self.out)

    def test_flag_switch_does_not_stop(self):
        self.make_overlay()
        self.seed_ja({"enabled": True, "overlay_sha256": "stale-but-flag-off-now"})
        m.B3_CORE_NUMBER_ROUNDING_ENABLED = False
        try:
            self.assertEqual(runner.load_reused_ja_text(self.out), "W-1の日本語記事")
        finally:
            m.B3_CORE_NUMBER_ROUNDING_ENABLED = True


class TestV9DateTime(unittest.TestCase):
    def test_date_time_core_number_stays_exact_even_if_judge_says_approx(self):
        import er053_dev_b3_fixture_adapter_01 as ad
        d = tempfile.mkdtemp()
        try:
            ad.build_fixture("small_bag", d)
            a = contract.validate_annotated_b3(d)
            kinds = {c["concept"]: c["kind"] for c in m.core_concepts(a.sidecar)}
            self.assertIn("date_time", kinds.values())
            approx = {s: "約2026年" for c in m.core_concepts(a.sidecar) for s in c["surfaces"]}
            ov = m.build_overlay(a.sidecar, judge_json_for(a.sidecar, approx))
            for e in ov["entries"]:
                if e["kind"] == "date_time":
                    self.assertEqual(e["final_decision"], m.DECISION_EXACT)
                    self.assertTrue(any(x.startswith("V9_") for x in e["downgrade_reasons"]), e)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_v9_changes_nothing_in_v8_fixture_90_P05(self):
        """影響0件: 保存済みLuna判断90件のcore conceptはすべて kind=magnitude(date_timeを含まない)。V9で拒否されるラベルAは0。"""
        fx = json.load(open(V8_FIXTURE, encoding="utf-8"))
        n_dt = 0
        for it in fx["items"]:
            sc = json.load(open(os.path.join(DATASET, it["article"], "storyline_b3", "annotation.json"), encoding="utf-8"))
            kinds = {n["kind"] for n in sc["numbers"] if n["concept"] == it["concept"] and n["class"] == "core"}
            self.assertEqual(len(kinds), 1, it)
            n_dt += sum(1 for k in kinds if k in m.EXACT_ALWAYS_KINDS)
        self.assertEqual(n_dt, 0)


class TestRoutingAndFamilyZ(unittest.TestCase):
    def test_family_z_and_other_runners_do_not_import_module(self):
        import glob
        for p in glob.glob(os.path.join(HERE, "er0*.py")):
            b = os.path.basename(p)
            if b.endswith("_test_01.py") or b.startswith(("er090_", "er095_")) or b in (
                    "er019_family_x_entertainment_production_runner_01.py", "er053_family_x_factlock_ja_writer_01.py"):
                continue
            self.assertNotIn("er095_b3_core_number_rounding_01", open(p, encoding="utf-8", errors="replace").read(), b)

    def test_judge_uses_registered_role_through_routing(self):
        import er006_model_routing_contract_01 as routing
        self.assertIn(m.ROLE_KEY, routing.PROCESS_MODEL_MAP)
        self.assertEqual(routing.PROCESS_MODEL_MAP[m.ROLE_KEY], m.JUDGE_MODEL)


if __name__ == "__main__":
    unittest.main()
