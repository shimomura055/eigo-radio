# -*- coding: utf-8 -*-
# er052_open233_e2e_acceptance_01_test_01.py: E2Eスクリプトの純粋部分(計画・Waste検知・provenance照合・集計)の単体テスト。API呼び出しなし(¥0)。
from __future__ import annotations

import unittest

import er052_open233_e2e_acceptance_01 as e2e


def _state(jpy=0.0, calls=0, errs=0, hist=None):
    return {"cumulative_jpy": jpy, "cumulative_calls": calls, "cumulative_errors": errs, "history": hist or []}


class TestPlan(unittest.TestCase):
    def test_plan_is_20_runs_with_std_adv_pairs(self):
        p = e2e.plan()
        self.assertEqual(len(p), 20)
        self.assertEqual(len(set(p)), 20)
        ids = [i for s, i in p if s == 1]
        for pair in e2e.PAIR_SETS.values():
            self.assertIn(pair["advanced"], ids)
            self.assertIn(pair["standard"], ids)
        self.assertEqual(sum(1 for s, i in p if i in e2e.SC_IDS), 12)  # SC 6 x n=2

    def test_instances_disable_substitution_and_reuse(self):
        insts = e2e.prepare_instances()
        for i in insts.values():
            self.assertFalse(i["substitute_baseline_on_stage1_miss"])
            self.assertEqual(i["stage1_mode"], "fresh")
        self.assertIn("bgroup_B3", insts)  # 従来baseline代替が効いていたinstanceも対象に含まれ、代替は無効


class TestWasteAndProvenance(unittest.TestCase):
    def test_guard_raises_on_cost_calls_errors_and_cycle(self):
        g = e2e.RunGuard(_state())
        g(_state(1.0, 5, 0))  # 正常
        for st, flag in ((_state(7.0), "per_run_cost"), (_state(1, 81), "calls_gt"), (_state(1, 5, 4), "api_errors"),
                         (_state(1, 5, 0, [{"label": "x_c6_recheck"}]), "cycle_gt")):
            with self.assertRaises(e2e.RunWaste) as cm:
                g(st)
            self.assertIn(flag, cm.exception.flag)

    def test_post_run_flags(self):
        r = {"cycles": [{"rewrite_records": [{"claim_identity": "a"}]}] * 4, "total_calls": 10, "total_cost_jpy": 1.0}
        self.assertIn("same_candidate_rewrite_gt_3", e2e.post_run_waste_flags(r))
        self.assertEqual(e2e.post_run_waste_flags({"cycles": [], "total_calls": 5, "total_cost_jpy": 1.0}), [])
        self.assertIn("exit_check_repeated", e2e.post_run_waste_flags(
            {"cycles": [], "recheck_exit_check": {"log": [1, 2]}, "total_calls": 1, "total_cost_jpy": 0}))

    def test_provenance_violations_detect_frozen_substitution_and_missing_audit(self):
        pv = {"stage1_source": "fresh", "frozen": False, "reuse": False, "substitution": False,
              "switches": {"STAGE1_MODE": "coverage_union", "RECHECK_MODE": "coverage_union"}}
        ok = {"stage1_call_used": True, "stage1_coverage": {"module_version": e2e.cov.MODULE_VERSION}, "provenance": pv}
        self.assertEqual(e2e.provenance_violations(ok), [])
        self.assertTrue(e2e.provenance_violations({**ok, "stage1_call_used": False}))  # frozen/reuse疑い
        self.assertTrue(e2e.provenance_violations({**ok, "stage1_recall_miss_substituted": True}))
        self.assertTrue(e2e.provenance_violations({**ok, "stage1_coverage": {}}))
        self.assertTrue(e2e.provenance_violations({**ok, "provenance": {**pv, "frozen": True}}))


class TestAggregate(unittest.TestCase):
    def _run(self, iid, sample, cost, final="RESOLVED_REWRITE", rewrite=True, s4=None):
        return {"instance_id": iid, "sample": sample, "final_state": final, "stage4_reason": s4, "total_cost_jpy": cost,
                "stage1_call_used": True, "elapsed_seconds": 1.0, "residual_at_pass": {"defs": []},
                "stage1_coverage": {"module_version": e2e.cov.MODULE_VERSION, "union_candidates": []},
                "cycles": [{"stage2_results": [], "blocking_count": 0, "rewrite_records": [{"claim_identity": "x"}] if rewrite else []}],
                "call_log": [{"recovery_stage": "stage1_initial", "cost_jpy": cost}], "provenance_violations": [], "waste_flags": []}

    def test_set_measured_pair_vs_estimate_columns_are_separate(self):
        runs = [self._run("hormuz_run03_advanced", 1, 3.0), self._run("hormuz_run03_standard", 1, 4.0),
                self._run("bgroup_B3", 1, 5.0)]
        c = e2e.aggregate(runs)["cost"]
        m = c["per_set"]["measured_pairs"]
        self.assertEqual(len(m), 1)
        self.assertEqual(m[0]["set_total_jpy"], 7.0)
        self.assertAlmostEqual(m[0]["net_increase_jpy"], 7.0 - 0.76)
        self.assertAlmostEqual(c["per_set"]["estimated_set_jpy(1記事平均x2、全run)"], 8.0)  # 平均4.0x2(実測対とは別列)

    def test_stage4_exit_counts_as_human_review_fail_and_residual_is_critical_miss(self):
        r1 = self._run("safety_A4", 1, 1.0, final="STAGE4_ESCALATION", s4="blocking_structural_after_ladder")
        agg = e2e.aggregate([r1])
        self.assertEqual(agg["human_review"]["n"], 1)
        self.assertFalse(agg["kpi_summary"]["human_review_pass"])
        d = e2e.runner._safety_critical_defs("safety_A4")[0]
        r2 = self._run("safety_A4", 2, 1.0)
        r2["residual_at_pass"] = {"defs": [{"sub_id": d["sub_id"], "remains_in_final_en_pattern": True, "ever_blocking_flagged": False}]}
        agg2 = e2e.aggregate([r2])
        self.assertEqual(agg2["safety"]["critical_miss_at_exit"][0]["sub_id"], d["sub_id"])
        self.assertFalse(agg2["kpi_summary"]["safety_pass"])


if __name__ == "__main__":
    unittest.main()
