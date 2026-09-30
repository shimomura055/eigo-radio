# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_test_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ⑥、委任_09)
# ============================================================
# ネットワーク呼び出しなし(¥0)。claim identity/floor適用/文特定/precheck
# floor dedup/測定集計ロジックのread-only regression testのみ。
from __future__ import annotations

import unittest

import er052_open233_self_recovery_flow_runner_01 as runner


class TestClaimIdentity(unittest.TestCase):
    def test_uses_fact_id_when_present(self):
        dev = {"related_fact_id": "HF-009", "claim_in_article": "some claim text"}
        self.assertEqual(runner.claim_identity(dev), "fact:HF-009")

    def test_same_fact_id_gives_same_identity_regardless_of_claim_text(self):
        dev1 = {"related_fact_id": "HF-009", "claim_in_article": "text A"}
        dev2 = {"related_fact_id": "HF-009", "claim_in_article": "text B (different wording)"}
        self.assertEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))

    def test_falls_back_to_claim_hash_when_no_fact_id(self):
        dev1 = {"related_fact_id": "", "claim_in_article": "alpha"}
        dev2 = {"related_fact_id": "", "claim_in_article": "beta"}
        self.assertNotEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))
        self.assertTrue(runner.claim_identity(dev1).startswith("claim:"))


class TestApplyFloor(unittest.TestCase):
    def test_precheck_detected_by_forces_blocking(self):
        dev = {}
        materiality, reason = runner.apply_floor("ACCEPTABLE", dev, "precheck")
        self.assertEqual(materiality, "BLOCKING")
        self.assertEqual(reason, "precheck_floor")

    def test_floor_flag_true_forces_blocking_even_if_llm_says_quality(self):
        dev = {"changed_actor": True}
        materiality, reason = runner.apply_floor("QUALITY", dev, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")
        self.assertIn("changed_actor", reason)

    def test_no_floor_passes_through_llm_judgment(self):
        dev = {"changed_actor": False, "changed_number": False}
        materiality, reason = runner.apply_floor("QUALITY", dev, "stage1_llm")
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)

    def test_certainty_flag_is_in_floor_set(self):
        self.assertIn("changed_certainty", runner.FLOOR_FLAGS)
        dev = {"changed_certainty": True}
        materiality, reason = runner.apply_floor("ACCEPTABLE", dev, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")

    def test_causality_not_in_floor_set(self):
        self.assertNotIn("changed_causality", runner.FLOOR_FLAGS)
        dev = {"changed_causality": True}
        materiality, reason = runner.apply_floor("QUALITY", dev, "stage1_llm")
        # floor対象外なのでLLM判定(QUALITY)がそのまま通る
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)


class TestLocateBestSentence(unittest.TestCase):
    def test_exact_substring(self):
        text = "Sentence one. TARGET sentence here. Sentence three."
        target, method = runner.locate_best_sentence("TARGET sentence here.", text)
        self.assertEqual(target, "TARGET sentence here.")
        self.assertEqual(method, "exact_substring")

    def test_fuzzy_fallback_when_not_exact(self):
        text = "Sentence one. The market reacted very strongly to the news today. Sentence three."
        target, method = runner.locate_best_sentence(
            "The market reacted strongly to the news today.", text)
        self.assertIn("market reacted", target)
        self.assertTrue(method.startswith("sequence_matcher"))

    def test_not_found_returns_none(self):
        text = "Completely unrelated sentence content here."
        target, method = runner.locate_best_sentence("XYZXYZXYZ totally different content", text)
        self.assertIsNone(target)
        self.assertEqual(method, "not_found")

    def test_japanese_exact_substring(self):
        text = "これは一文目です。これがターゲットの文です。これは三文目です。"
        target, method = runner.locate_best_sentence("これがターゲットの文です。", text)
        self.assertEqual(target, "これがターゲットの文です。")
        self.assertEqual(method, "exact_substring")


class TestPrecheckFloorClaimsDedup(unittest.TestCase):
    LEDGER = ("[VERIFIED] F001: Alice announced a plan.\n"
              "  numeric_value: 20%\n")
    ARTICLE_MISMATCH = "Bob announced a plan. The article mentions 45% instead."

    def test_new_finding_not_in_existing_ids_is_included(self):
        claims = runner.build_precheck_floor_claims(
            {"ledger_text": self.LEDGER, "article_text": self.ARTICLE_MISMATCH}, existing_fact_ids=set())
        self.assertTrue(any(c["related_fact_id"] == "F001" for c in claims))
        for c in claims:
            self.assertEqual(c["detected_by"], "precheck")

    def test_finding_already_covered_by_stage1_is_excluded(self):
        claims = runner.build_precheck_floor_claims(
            {"ledger_text": self.LEDGER, "article_text": self.ARTICLE_MISMATCH}, existing_fact_ids={"F001"})
        self.assertEqual(claims, [])


class TestAggregateMeasurements(unittest.TestCase):
    def _instance(self, instance_id, final_state, cycles=None, elapsed=1.0, calls=1, cost=0.1):
        return {
            "instance_id": instance_id, "group": "test", "expected_group_label": "x",
            "final_state": final_state, "stage4_reason": None if final_state != "STAGE4_ESCALATION" else "x",
            "cycles": cycles or [], "stage1_call_used": False,
            "total_cost_jpy": cost, "total_calls": calls, "elapsed_seconds": elapsed,
        }

    def test_basic_counts(self):
        results = [
            self._instance("a1", "ACCEPTABLE_STAGE1"),
            self._instance("a2", "RESOLVED_STAGE2_DOWNGRADE",
                            cycles=[{"stage2_results": [{"materiality": "QUALITY", "claim_text": "q1"}]}]),
            self._instance("a3", "RESOLVED_REWRITE",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}],
                                     "recheck_all_prior_issues_resolved": True}]),
            self._instance("a4", "STAGE4_ESCALATION",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}]},
                                    {"rewrite_records": [{"mechanism": "x"}]}]),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["n_instances"], 4)
        self.assertEqual(agg["self_recovery_6"]["initial_block_count"], 3)
        self.assertEqual(agg["self_recovery_6"]["rescreening_auto_resolved_count"], 1)
        self.assertEqual(agg["self_recovery_6"]["final_stop_count"], 1)
        self.assertEqual(agg["escalation_zero_breakdown"]["true_resolved_all_prior_issues_resolved_true"], 1)
        self.assertEqual(agg["escalation_zero_breakdown"]["quality_pass"], 1)
        self.assertEqual(len(agg["quality_claims"]), 1)
        self.assertEqual(agg["qcd"]["completion_rate"], 0.75)


class TestNoCrossModuleBudgetStateContamination(unittest.TestCase):
    """委任_09で実際に検出したbug(`s3rt.simple_llm_call`をそのまま呼ぶと
    `s3rt`モジュール自身の`save_budget_state`が既存委任_08の証跡ファイル
    [`er052_output/open233_self_recovery_stage3_rewrite_trial_01/
    budget_state_c233l_b.json`]を上書きする)の再発防止regression test。
    本runnerが`s3rt.simple_llm_call`(save_budget_state/record_callを
    内部で呼ぶ関数)を直接呼んでいないことをソーステキストで機械確認する。"""

    def test_runner_does_not_call_s3rt_simple_llm_call(self):
        import inspect
        src = inspect.getsource(runner)
        self.assertNotIn("s3rt.simple_llm_call(", src)

    def test_runner_has_own_simple_llm_call_using_own_budget_path(self):
        self.assertTrue(callable(runner.simple_llm_call))
        import inspect
        src = inspect.getsource(runner.simple_llm_call)
        self.assertIn("record_call(state", src)
        self.assertNotIn("s3rt.record_call", src)
        self.assertNotIn("s3rt.save_budget_state", src)


if __name__ == "__main__":
    unittest.main()
