# ============================================================
# er010_open141_diff_qa_production_wiring_test_01.py
# 管理ID: OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01
# ============================================================
# ユーザー正式判断(2026-09-13、PM-CLOSEOUT-CONSOLIDATION-105)で承認された
# Production配線(target-sentence-matching既定ON + 差分QA案I)を検証する。
# 実LLM呼び出しは一切行わない(すべてmock、¥0)。
#
# 対象:
#   - er010_ledger_local_rewrite_09.run_diff_qa_for_accepted_rewrite()の
#     verdict分岐(FAIL/REVIEW_REQUIRED/PASS × LEDGER_DEVIATION/COMPLIANT)。
#   - er010_ledger_local_rewrite_09.apply_diff_qa_to_resolved_rewrite()の
#     resolved=False早期return、blocks_acceptance時のresolved反転。
#   - DIFF_QA_CALLS_PER_ITEM(既存MAX_REWRITE_CYCLES/MAX_REWRITE_ATTEMPTSとは
#     独立の別軸カウンタ)。
#   - A-Family(er003_v1_n3_01_articles_generate.run_one_pattern)からの配線
#     (use_target_sentence_matching=True・apply_diff_qa_to_resolved_rewrite
#     呼び出し)。
#   - B-Family(er012_b_family_voices_writer_generic_01.
#     run_ledger_deviation_and_local_rewrite)からの配線(topic_ja有無での
#     分岐を含む)。
#
# 実LLM呼び出しによるruntime evidence(Production正式経路でLocal Rewrite/
# 差分QAが実際に発火した記録)は本ファイルの対象外
# (OPEN-141-TARGET-SENTENCE-DIFF-QA-PRODUCTION-WIRING-01_REPORT.md参照)。

import shutil
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_articles_generate as gen
import er010_ledger_local_rewrite_09 as local_rewrite
import er010_n9_production_integration_09_test_01 as base_test
import er012_b_family_voices_writer_generic_01 as wg


def _fake_fc_gates(verdict):
    return ({"verdict": verdict}, "PASS", [], "fake-fc-model", "fake-resp-id",
            {"web_search_call_count": 2}, [])


def _ledger_check_result(status, target_sentence="Target sentence."):
    if status == "LEDGER_COMPLIANT":
        return {"parsed": {"overall_status": status, "deviations": []}}
    # evaluate_target_sentence_status()は対象文に対応付けられた実際の
    # deviationがある場合のみLEDGER_DEVIATIONとするため(空deviations配列
    # は常にLEDGER_COMPLIANT扱い)、target_sentence自身をclaim_in_articleに
    # 持つMAJOR deviationを1件含める。
    return {"parsed": {"overall_status": status, "deviations": [
        {"claim_in_article": target_sentence, "issue": "test issue", "explanation": "test explanation",
         "severity": "MAJOR", "changed_certainty": True, "changed_fact": False, "changed_scope": False,
         "changed_causality": False, "changed_number": False, "changed_actor": False,
         "changed_negation": False, "changed_comparison": False, "changed_time": False,
         "unsupported_new_claim": False, "treated_as_hook": False, "auto_downgraded": False},
    ]}}


class DiffQaCallsPerItemConstantTests(unittest.TestCase):
    def test_diff_qa_calls_per_item_is_one(self):
        # 既存MAX_REWRITE_CYCLES/MAX_REWRITE_ATTEMPTS(いずれも3)と混同しない
        # 独立カウンタであることを明示する回帰テスト。
        self.assertEqual(local_rewrite.DIFF_QA_CALLS_PER_ITEM, 1)
        self.assertNotEqual(local_rewrite.DIFF_QA_CALLS_PER_ITEM, local_rewrite.MAX_REWRITE_CYCLES)
        self.assertNotEqual(local_rewrite.DIFF_QA_CALLS_PER_ITEM, local_rewrite.MAX_REWRITE_ATTEMPTS)


class RunDiffQaForAcceptedRewriteVerdictTests(unittest.TestCase):
    """FAIL/REVIEW_REQUIRED/PASS各verdict × Ledger再評価(LEDGER_DEVIATION/
    LEDGER_COMPLIANT)でのblocks_acceptance分岐(LLMはmock、¥0)。"""

    def _run(self, fc_verdict, ledger_status):
        with mock.patch.object(local_rewrite.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(local_rewrite.r3, "run_fact_checker_with_gates",
                                return_value=_fake_fc_gates(fc_verdict)), \
             mock.patch.object(local_rewrite.vfl01, "run_deviation_check",
                                return_value=_ledger_check_result(ledger_status)):
            return local_rewrite.run_diff_qa_for_accepted_rewrite(
                client=object(), topic_ja="tip screens", target_sentence="Target sentence.",
                before_ctx="Before context.", after_ctx="After context.",
                verified_ledger_text="FACT-01: some ledger fact",
                ledger_model="fake-ledger-model", fact_checker_model="fake-fc-model")

    def test_pass_and_compliant_does_not_block(self):
        result = self._run("PASS", "LEDGER_COMPLIANT")
        self.assertFalse(result["blocks_acceptance"])

    def test_review_required_and_compliant_does_not_block(self):
        # ユーザー承認2026-09-13: REVIEW_REQUIREDは既存Fact Checker A'の
        # non-blocking advisory運用と同じ扱い(記録のみ・通過)。
        result = self._run("REVIEW_REQUIRED", "LEDGER_COMPLIANT")
        self.assertFalse(result["blocks_acceptance"])
        self.assertEqual(result["fact_check_verdict"], "REVIEW_REQUIRED")

    def test_fail_blocks_even_if_ledger_compliant(self):
        result = self._run("FAIL", "LEDGER_COMPLIANT")
        self.assertTrue(result["blocks_acceptance"])

    def test_ledger_deviation_blocks_even_if_fact_check_pass(self):
        result = self._run("PASS", "LEDGER_DEVIATION")
        self.assertTrue(result["blocks_acceptance"])

    def test_review_required_and_ledger_deviation_blocks_via_ledger(self):
        result = self._run("REVIEW_REQUIRED", "LEDGER_DEVIATION")
        self.assertTrue(result["blocks_acceptance"])

    def test_window_text_construction_and_calls_field(self):
        result = self._run("PASS", "LEDGER_COMPLIANT")
        self.assertEqual(result["window_text"], "Before context. Target sentence. After context.")
        self.assertEqual(result["diff_qa_calls"], local_rewrite.DIFF_QA_CALLS_PER_ITEM)
        self.assertEqual(result["fact_check_model"], "fake-fc-model")


class ApplyDiffQaToResolvedRewriteTests(unittest.TestCase):
    def _base_kwargs(self):
        return dict(client=object(), topic_ja="tip screens", before_ctx="Before.", after_ctx="After.",
                    verified_ledger_text="FACT-01: x", ledger_model="fake-model",
                    fact_checker_model="fake-fc-model")

    def test_skip_when_not_resolved_makes_no_diff_qa_call(self):
        diff_qa_mock = mock.Mock()
        with mock.patch.object(local_rewrite, "run_diff_qa_for_accepted_rewrite", diff_qa_mock):
            r = {"resolved": False, "human_review_required": True, "final_text": "still bad"}
            result = local_rewrite.apply_diff_qa_to_resolved_rewrite(r, **self._base_kwargs())
        diff_qa_mock.assert_not_called()
        self.assertEqual(result["diff_qa"], {"applied": False, "reason": "not_resolved_skip"})
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])

    def test_fail_verdict_flips_resolved_to_false_and_sets_human_review(self):
        with mock.patch.object(local_rewrite, "run_diff_qa_for_accepted_rewrite",
                                return_value={"blocks_acceptance": True, "fact_check_verdict": "FAIL"}):
            r = {"resolved": True, "human_review_required": False,
                 "final_text": "In this study, the tip rate rose after screens appeared."}
            result = local_rewrite.apply_diff_qa_to_resolved_rewrite(r, **self._base_kwargs())
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])
        self.assertTrue(result["diff_qa"]["applied"])
        self.assertTrue(result["diff_qa"]["blocks_acceptance"])

    def test_ledger_deviation_verdict_flips_resolved_to_false(self):
        with mock.patch.object(local_rewrite, "run_diff_qa_for_accepted_rewrite",
                                return_value={"blocks_acceptance": True,
                                               "ledger_check_target_eval": {"overall_status": "LEDGER_DEVIATION"}}):
            r = {"resolved": True, "human_review_required": False, "final_text": "x"}
            result = local_rewrite.apply_diff_qa_to_resolved_rewrite(r, **self._base_kwargs())
        self.assertFalse(result["resolved"])
        self.assertTrue(result["human_review_required"])

    def test_review_required_keeps_resolved_true_non_blocking(self):
        with mock.patch.object(local_rewrite, "run_diff_qa_for_accepted_rewrite",
                                return_value={"blocks_acceptance": False,
                                               "fact_check_verdict": "REVIEW_REQUIRED"}):
            r = {"resolved": True, "human_review_required": False, "final_text": "x"}
            result = local_rewrite.apply_diff_qa_to_resolved_rewrite(r, **self._base_kwargs())
        self.assertTrue(result["resolved"])
        self.assertFalse(result["human_review_required"])
        self.assertTrue(result["diff_qa"]["applied"])


class AFamilyDefaultOnWiringTests(unittest.TestCase):
    """A-Family(run_one_pattern)経路で、target-sentence-matchingが既定ONで
    rewrite_ng_item()へ渡され、Local Rewrite受理直後に差分QAが実際に呼ばれる
    ことを、LLM呼び出しをすべてmockして検証する(¥0)。"""

    def setUp(self):
        self.out_dir = tempfile.mkdtemp(prefix="er010_open141_a_family_wiring_test_")
        self.addCleanup(shutil.rmtree, self.out_dir, ignore_errors=True)

    def test_rewrite_ng_item_and_diff_qa_wired_with_target_sentence_matching_enabled(self):
        writer_mock = mock.Mock(return_value=base_test._fake_writer_result(base_test.ARTICLE_WITH_MAJOR))
        deviation_mock = mock.Mock(side_effect=[base_test._major_deviation_result(),
                                                 base_test._compliant_deviation_result()])
        rewrite_mock = mock.Mock(return_value={
            "original_ng_sentence": "The tip rate always rises after screens appear.",
            "issue": "certainty強化", "explanation": "x", "flags": ["changed_certainty"],
            "attempts": [{"attempt": 1, "text": "In this study, the tip rate rose after screens appeared.",
                          "ledger_status": "LEDGER_COMPLIANT"}],
            "final_text": "In this study, the tip rate rose after screens appeared.",
            "resolved": True, "human_review_required": False,
        })
        diff_qa_mock = mock.Mock(side_effect=lambda r, *a, **k: r)
        with mock.patch.object(gen.vfl01, "run_writer_with_technical_retry", writer_mock), \
             mock.patch.object(gen, "run_point_overlap_qa_and_regenerate",
                                side_effect=base_test._fake_point_overlap_no_flag), \
             mock.patch.object(gen.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(gen.r3, "run_fact_checker_with_gates",
                                return_value=base_test._fake_fact_checker_gates()), \
             mock.patch.object(gen.vfl01, "run_deviation_check", deviation_mock), \
             mock.patch.object(gen.point_planning, "run_point_role_planning",
                                side_effect=base_test._fake_role_planning_result), \
             mock.patch.object(gen.point_planning, "run_point_value_qa",
                                side_effect=base_test._fake_value_qa_pass), \
             mock.patch.object(gen.local_rewrite, "rewrite_ng_item", rewrite_mock), \
             mock.patch.object(gen.local_rewrite, "apply_diff_qa_to_resolved_rewrite", diff_qa_mock):
            result = gen.run_one_pattern(
                client=object(), theme_id="t1", label="A2",
                prompt="fake prompt", verified_ledger_text="FACT-01: some ledger fact",
                topic="tip screens", out_dir=self.out_dir,
                apply_evidence_compression=False, apply_directional_fact_precheck=False)

        self.assertEqual(result["status"], "OK")
        rewrite_mock.assert_called_once()
        _, rewrite_kwargs = rewrite_mock.call_args
        self.assertTrue(rewrite_kwargs.get("use_target_sentence_matching"))
        diff_qa_mock.assert_called_once()
        diff_qa_args, _ = diff_qa_mock.call_args
        # apply_diff_qa_to_resolved_rewrite(r, client, topic_ja, before_ctx, ...)
        self.assertEqual(diff_qa_args[2], "tip screens")
        self.assertEqual(len(result["local_rewrite_results"]), 1)
        self.assertIn("diff_qa_point_overlap", result["local_rewrite_results"][0])


class BFamilyDiffQaWiringTests(unittest.TestCase):
    """B-Family(run_ledger_deviation_and_local_rewrite)経路のtopic_ja有無に
    よる差分QA発火/非発火分岐を、LLM呼び出しをすべてmockして検証する(¥0)。
    3V Fact Safety gate(OPEN-120)とは無関係な検証のため明示的にOFF固定。"""

    ARTICLE = "Intro line stays the same.\n\nThe result always happens after the change.\n\nClosing line."
    TARGET = "The result always happens after the change."

    def _major_result(self):
        flags = {k: False for k in
                  ["changed_fact", "changed_scope", "changed_causality", "changed_number",
                   "changed_actor", "changed_negation", "changed_comparison", "changed_time",
                   "unsupported_new_claim", "treated_as_hook", "auto_downgraded"]}
        flags["changed_certainty"] = True
        return {"parsed": {"overall_status": "LEDGER_DEVIATION", "deviations": [
            {"claim_in_article": self.TARGET, "issue": "certainty強化", "explanation": "x",
             "severity": "MAJOR", **flags}]}}

    def _compliant_result(self):
        return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []}}

    def _run(self, topic_ja, rewrite_mock, diff_qa_mock, deviation_mock):
        with tempfile.TemporaryDirectory() as tmp:
            import os
            os.makedirs(f"{tmp}/audit", exist_ok=True)
            with mock.patch.object(wg.registry, "is_voice_fact_safety_gate_mode_enabled", return_value=False), \
                 mock.patch.object(wg.vfl01, "run_deviation_check", deviation_mock), \
                 mock.patch.object(wg.local_rewrite, "locate_target_sentence",
                                    return_value=(self.TARGET, "exact_substring")), \
                 mock.patch.object(wg.local_rewrite, "rewrite_ng_item", rewrite_mock), \
                 mock.patch.object(wg.local_rewrite, "apply_diff_qa_to_resolved_rewrite", diff_qa_mock):
                kwargs = dict(client=object(), theme_id="t", label="B1B", article_text=self.ARTICLE,
                              verified_ledger_text="dummy ledger", out_dir=tmp, ledger_model="dummy-model")
                if topic_ja is not None:
                    kwargs["topic_ja"] = topic_ja
                return wg.run_ledger_deviation_and_local_rewrite(**kwargs)

    def test_topic_ja_not_provided_skips_diff_qa_but_still_uses_target_sentence_matching(self):
        rewrite_mock = mock.Mock(return_value={
            "original_ng_sentence": self.TARGET, "issue": "x", "explanation": "y", "flags": [],
            "attempts": [{"attempt": 1, "text": "In this case, the result happens after the change.",
                          "ledger_status": "LEDGER_COMPLIANT"}],
            "final_text": "In this case, the result happens after the change.",
            "resolved": True, "human_review_required": False,
        })
        diff_qa_mock = mock.Mock(side_effect=lambda r, *a, **k: r)
        deviation_mock = mock.Mock(side_effect=[self._major_result(), self._compliant_result()])
        result = self._run(None, rewrite_mock, diff_qa_mock, deviation_mock)

        rewrite_mock.assert_called_once()
        _, rewrite_kwargs = rewrite_mock.call_args
        self.assertTrue(rewrite_kwargs.get("use_target_sentence_matching"))
        diff_qa_mock.assert_not_called()
        self.assertEqual(result["local_rewrite_results"][0]["diff_qa"],
                          {"applied": False, "reason": "topic_ja_not_provided"})

    def test_topic_ja_provided_invokes_diff_qa(self):
        rewrite_mock = mock.Mock(return_value={
            "original_ng_sentence": self.TARGET, "issue": "x", "explanation": "y", "flags": [],
            "attempts": [{"attempt": 1, "text": "In this case, the result happens after the change.",
                          "ledger_status": "LEDGER_COMPLIANT"}],
            "final_text": "In this case, the result happens after the change.",
            "resolved": True, "human_review_required": False,
        })
        diff_qa_mock = mock.Mock(side_effect=lambda r, *a, **k: r)
        deviation_mock = mock.Mock(side_effect=[self._major_result(), self._compliant_result()])
        result = self._run("theme X", rewrite_mock, diff_qa_mock, deviation_mock)

        diff_qa_mock.assert_called_once()
        diff_qa_args, _ = diff_qa_mock.call_args
        self.assertEqual(diff_qa_args[2], "theme X")
        self.assertEqual(len(result["local_rewrite_results"]), 1)
        self.assertIn("diff_qa_point_overlap", result["local_rewrite_results"][0])

    def test_diff_qa_fail_verdict_propagates_to_ng_review_required(self):
        # apply_diff_qa_to_resolved_rewriteの実装(mockしない)を使い、FAIL
        # 相当のverdictがresolved反転→human_review_required→cycle継続
        # →最終的にNG_REVIEW_REQUIRED相当(remaining_major/human_review)へ
        # 合流することを実装レベルで確認する。
        # apply_diff_qa_to_resolved_rewrite()はrewrite_result dictをin-place
        # で変更するため、cycleごとに新しいdictを返すfactoryを使う(mockの
        # return_valueに固定dictを渡すと、同一オブジェクトがcycleをまたいで
        # 使い回され、前cycleでの変更[resolved=False等]が次cycleの
        # rewrite_ng_item呼び出し結果へ誤って持ち越されてしまうため)。
        rewrite_mock = mock.Mock(side_effect=lambda *a, **k: {
            "original_ng_sentence": self.TARGET, "issue": "x", "explanation": "y", "flags": [],
            "attempts": [{"attempt": 1, "text": "In this case, the result happens after the change.",
                          "ledger_status": "LEDGER_COMPLIANT"}],
            "final_text": "In this case, the result happens after the change.",
            "resolved": True, "human_review_required": False,
        })
        # cycle上限まで毎回MAJORが検出される(rewrite_ng_item自体は
        # LEDGER_COMPLIANTとして受理するが、差分QAが毎回FAILし続けるため
        # 最終的にhuman_review_required=Trueのまま cycle上限に達する)。
        # vfl01.run_deviation_check()は本cycleループ内の全体再判定と、
        # 差分QA内のLedger再確認の両方から呼ばれる(同一module属性への
        # patchのため)ので、呼び出し回数に依存しないreturn_valueを使う。
        deviation_mock = mock.Mock(return_value=self._major_result())
        with mock.patch.object(local_rewrite.r3, "build_fact_check_prompt", return_value="fake-prompt"), \
             mock.patch.object(local_rewrite.r3, "run_fact_checker_with_gates",
                                return_value=_fake_fc_gates("FAIL")):
            result = self._run("theme X", rewrite_mock, wg.local_rewrite.apply_diff_qa_to_resolved_rewrite,
                                deviation_mock)
        self.assertTrue(result["any_human_review_required"])
        last_item = result["local_rewrite_results"][-1]
        self.assertFalse(last_item["resolved"])
        self.assertTrue(last_item["human_review_required"])
        self.assertTrue(last_item["diff_qa"]["applied"])
        self.assertTrue(last_item["diff_qa"]["blocks_acceptance"])


if __name__ == "__main__":
    unittest.main()
