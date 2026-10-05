# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_recheck_coverage_test_01.py
# OPEN-233 E2E-ACCEPTANCE-01 委任_18: Rewrite後Recheckの新Stage 1仕様(`RECHECK_MODE=coverage_union`)の単体テスト。
# ネットワーク呼び出しなし(¥0、偽LLM/mockのみ)。既定(legacy_v4a)で挙動が変わらないことも確認する。
# ============================================================
from __future__ import annotations

import re
import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov

ZERO = {k: False for k in cov.FLAG_KEYS}
LEDGER = """[VERIFIED] HF-001: 20％の償還料が7月13日に提案された。
  scope: ホルムズ海峡

[VERIFIED] HF-002: 徴収方法は示されなかった。
  scope: 償還料案
"""
BEFORE = """# Title Here

The plan was posted on July 13. It said 20% would be charged.

The post did not say how to collect it. So the plan left the stage.

Other paragraph has a plain sentence. And another plain sentence follows here.
"""
AFTER = BEFORE.replace("It said 20% would be charged.", "It said a fee would be charged.")
# 関係単位(因果語起点)を含まない版: 偽LLMのSUPPORTEDが決定論検査(causal_not_in_fact)で戻されないようにする
BEFORE_NR = BEFORE.replace("So the plan left the stage.", "The plan left the stage.").replace("did not say", "described")
AFTER_NR = AFTER.replace("So the plan left the stage.", "The plan left the stage.").replace("did not say", "described")


def _seg():
    return dict(segment_fn=runner.vs_sentence_segments_l6, initial_extra=runner.CAUSAL_SENTENCE_INITIAL_EN)


class FakeLLM:
    def __init__(self, fail=(), cands=()):
        self.fail, self.cands, self.calls = set(fail), set(cands), []

    def __call__(self, label, developer, prompt, schema):
        self.calls.append((label, prompt))
        if label in self.fail:
            return None, {"cost_jpy": 0.0, "error": "fake"}
        meta = {"cost_jpy": 0.5, "usage": {}}
        if schema is cov.R3_JSON_SCHEMA:
            ids = re.search(r"【判定必須の単位ID\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
            return {"unit_verdicts": [
                {"unit_id": i, "verdict": "CANDIDATE" if i in self.cands else "SUPPORTED", "support_fact_ids": ["HF-001"],
                 "ledger_quotes": ["20％の償還料が7月13日に提案された"], "issue": "x" if i in self.cands else "",
                 "claim_in_article": "", "related_fact_id": "HF-001" if i in self.cands else "", "flags": dict(ZERO)}
                for i in ids]}, meta
        fids = re.search(r"【factID一覧\(全\d+件\)】\n(.*)\n", prompt).group(1).split(", ")
        return {"facts": [{"fact_id": f, "matches": []} for f in fids]}, meta


class TestChangedScope(unittest.TestCase):
    def test_single_sentence_change_gives_changed_plus_neighbors(self):
        r = cov.coverage_changed_scope(BEFORE, AFTER, **_seg())
        self.assertEqual(r["changed_ids"], ["S1.2"])
        self.assertTrue({"S1.1", "S1.2", "S2.1"} <= set(r["scope_ids"]))  # 前後1単位(次の段落の先頭文も隣)
        self.assertNotIn("S3.2", r["scope_ids"])  # 離れた単位は対象外

    def test_unchanged_text_with_prior_claim_still_in_scope(self):
        r = cov.coverage_changed_scope(BEFORE, BEFORE, prior_claims=["It said 20% would be charged."], **_seg())
        self.assertEqual(r["changed_ids"], ["S1.2"])  # Rewriteが効かず不変でも指摘箇所は範囲外にしない
        self.assertIn("S1.2", r["scope_ids"])
        self.assertEqual(r["n_prior_claim_hits"], 1)

    def test_pure_deletion_marks_neighbors(self):
        after = BEFORE.replace(" It said 20% would be charged.", "")
        r = cov.coverage_changed_scope(BEFORE, after, **_seg())
        self.assertIn("S1.1", r["scope_ids"])
        self.assertTrue(r["scope_ids"])

    def test_relation_unit_included_when_member_in_scope(self):
        r = cov.coverage_changed_scope(BEFORE, AFTER, **_seg())
        self.assertIn("R:S2.1+S2.2", r["split"]["relation_ids"])
        self.assertIn("R:S2.1+S2.2", r["scope_ids"])  # S2.1(変更S1.2の次の単位)を含む関係単位


class TestRecheckScopeRun(unittest.TestCase):
    PRIOR = [{"fact_id": "HF-001", "claim_in_article": "It said 20% would be charged.", "issue": "i", "explanation": "e"}]

    def _fx(self, art):
        return {"ledger_text": LEDGER, "article_text": art}

    def test_r3_required_ids_and_r5_targets_are_limited_to_scope(self):
        llm = FakeLLM()
        res = cov.run_recheck_scope(self._fx(AFTER), llm, BEFORE, self.PRIOR, **_seg())
        sc = res["audit"]["scope_ids"]
        r3p = [p for (l, p) in llm.calls if l == "r3"][0]
        self.assertIn("(全%d件)" % len(sc), r3p)  # 必須IDは全単位ではなくscope件数
        self.assertLess(len(sc), res["audit"]["n_judged_units"])
        r5p = [p for (l, p) in llm.calls if l == "r5v"][0]
        self.assertNotIn("[S3.2]", r5p.split("【factID一覧")[0].split("【検証対象の単位")[-1])
        self.assertEqual([l for (l, p) in llm.calls], ["r3", "r5v"])

    def test_candidate_in_scope_marks_prior_issue_unresolved(self):
        res = cov.run_recheck_scope(self._fx(AFTER), FakeLLM(cands={"S1.2"}), BEFORE, self.PRIOR, **_seg())
        self.assertFalse(res["prior_issues_resolved"][0]["resolved"])
        self.assertTrue(res["candidates"])

    def test_no_candidate_resolves_prior_issue(self):
        res = cov.run_recheck_scope(self._fx(AFTER_NR), FakeLLM(), BEFORE_NR, self.PRIOR, **_seg())
        self.assertTrue(res["prior_issues_resolved"][0]["resolved"])
        self.assertEqual(res["candidates"], [])
        self.assertFalse(res["api_failure"])

    def test_same_fact_other_unit_is_conservatively_unresolved(self):
        res = cov.run_recheck_scope(self._fx(AFTER), FakeLLM(cands={"S2.1"}), BEFORE, self.PRIOR, **_seg())
        self.assertFalse(res["prior_issues_resolved"][0]["resolved"])  # 同fact_idの候補=fail-closed

    def test_exit_full_r3_requires_all_judged_units(self):
        llm = FakeLLM()
        r = cov.run_exit_full_r3(self._fx(AFTER), llm, **_seg())
        self.assertEqual(r["audit"]["kind"], "exit_full_r3")
        n = r["audit"]["n_judged_units"]
        self.assertIn("(全%d件)" % n, llm.calls[0][1])
        self.assertEqual([l for (l, p) in llm.calls], ["r3"])  # 5-liteは呼ばない(3'-R全文1回)


class TestRunnerWiring(unittest.TestCase):
    def test_defaults_are_legacy(self):
        self.assertEqual(runner.RECHECK_MODE, runner.RECHECK_MODE_LEGACY)
        self.assertIsNone(runner.RUN_CALL_HOOK)

    def test_recheck_coverage_api_failure_is_fail_closed(self):
        fail = FakeLLM(fail={"r3", "r3_retry"})
        with mock.patch.object(runner, "make_stage1_call_fn", lambda *a, **k: fail):
            out = runner.run_recheck_coverage(None, {}, [0], [], "x", {"ledger_text": LEDGER}, AFTER, TestRecheckScopeRun.PRIOR, BEFORE)
        self.assertEqual(out["overall_status"], "LEDGER_DEVIATION")
        self.assertFalse(out["all_prior_issues_resolved"])
        self.assertTrue(out["_recheck_api_failure"])

    def test_recheck_coverage_returns_run_recheck_shape(self):
        with mock.patch.object(runner, "make_stage1_call_fn", lambda *a, **k: FakeLLM()):
            out = runner.run_recheck_coverage(None, {}, [0], [], "x", {"ledger_text": LEDGER}, AFTER_NR,
                                              TestRecheckScopeRun.PRIOR, BEFORE_NR)
        self.assertEqual(out["overall_status"], "LEDGER_COMPLIANT")
        self.assertTrue(out["all_prior_issues_resolved"])
        self.assertEqual(out["prior_issues_resolved_by_index"], {"0": True})

    def test_check_budget_hook_is_called_only_when_set(self):
        seen = []
        st = {"cumulative_jpy": 0.0}
        runner.check_budget(st)
        with mock.patch.object(runner, "RUN_CALL_HOOK", lambda s: seen.append(1)):
            runner.check_budget(st)
        self.assertEqual(seen, [1])


# ---- run_instanceの出口3'-R(Rewrite発生記事のみ・1回)。既存テストのharness(偽Stage 1/2/3/局所QA)を再利用する
import er052_open233_self_recovery_flow_runner_01_test_01 as rt


class TestExitGate(unittest.TestCase):
    def _run(self, exit_fn, mode=runner.RECHECK_MODE_COVERAGE_UNION):
        calls = []

        def fake_exit(*a, **k):
            calls.append(a[4])
            return exit_fn(len(calls))
        def fake_rc(client, state, ce, call_log, label, fixture, article_text, prior_issues, before_text):
            return {"overall_status": "LEDGER_COMPLIANT", "deviations": [], "all_prior_issues_resolved": True,
                    "prior_issues_resolved": [{"index": i, "resolved": True, "explanation": ""} for i, _ in enumerate(prior_issues)],
                    "recheck_coverage_audit": {}}
        with mock.patch.object(runner, "RECHECK_MODE", mode), mock.patch.object(runner, "run_exit_check_coverage", fake_exit),                 mock.patch.object(runner, "run_recheck_coverage", fake_rc):
            res, seen = rt._run_instance49([rt._dev49(rt.META_TARGET)])
        return res, seen, calls

    @staticmethod
    def _ok(n):
        return {"api_failure": False, "deviations": [], "audit": {"n_calls": 1, "n_judged_units": 9, "total_cost_jpy": 0.4,
                                                                  "missing_after_rerun": []}}

    def test_exit_check_runs_once_after_rewrite_and_passes_when_no_candidates(self):
        res, seen, calls = self._run(self._ok)
        self.assertEqual(len(calls), 1)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertTrue(res["recheck_exit_check"]["done"])
        self.assertEqual(res["switches"]["RECHECK_MODE"], "coverage_union")

    def test_exit_candidates_reenter_stage2_once_and_exit_check_is_not_repeated(self):
        def fn(n):
            return {"api_failure": False, "deviations": [rt._dev49("Calls happened.")] if n == 1 else [],
                    "audit": {"n_calls": 1, "n_judged_units": 9, "total_cost_jpy": 0.4, "missing_after_rerun": []}}
        res, seen, calls = self._run(fn)
        self.assertEqual(len(calls), 1)  # 1記事1回(再入後は再度行わない)
        self.assertEqual(len(res["cycles"]), 2)  # 新規CANDIDATEは次cycleのStage 2へ合流
        self.assertEqual(res["recheck_exit_check"]["log"][0]["n_candidates"], 1)

    def test_exit_api_failure_is_fail_closed_to_allowlisted_stage4(self):
        res, seen, calls = self._run(lambda n: {"api_failure": True, "deviations": [], "audit": {}})
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "api_failure")

    def test_legacy_mode_has_no_exit_check_and_no_new_keys(self):
        res, seen, calls = self._run(self._ok, mode=runner.RECHECK_MODE_LEGACY)
        self.assertEqual(calls, [])
        self.assertNotIn("recheck_exit_check", res)
        self.assertNotIn("RECHECK_MODE", res["switches"])


if __name__ == "__main__":
    unittest.main()
