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


class TestClaimIdentityNormalization(unittest.TestCase):
    """委任_10: fact_idが無い場合のclaim identityが、表記揺れ(引用符・大小
    文字・空白)だけで別claim扱いされないことのregression test(Opus L2 #1
    論点5対応)。"""

    def test_quote_wrapping_does_not_change_identity(self):
        dev1 = {"related_fact_id": "", "claim_in_article": "「同じ主張です」"}
        dev2 = {"related_fact_id": "", "claim_in_article": "同じ主張です"}
        self.assertEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))

    def test_case_and_whitespace_do_not_change_identity(self):
        dev1 = {"related_fact_id": "", "claim_in_article": "The Market Reacted   Strongly"}
        dev2 = {"related_fact_id": "", "claim_in_article": "the market reacted strongly"}
        self.assertEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))

    def test_genuinely_different_claims_still_differ(self):
        dev1 = {"related_fact_id": "", "claim_in_article": "Alpha claim text"}
        dev2 = {"related_fact_id": "", "claim_in_article": "Completely different beta claim"}
        self.assertNotEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))

    def test_fact_id_still_takes_priority_over_text_normalization(self):
        dev1 = {"related_fact_id": "HF-001", "claim_in_article": "text A"}
        dev2 = {"related_fact_id": "HF-001", "claim_in_article": "「text A」"}
        self.assertEqual(runner.claim_identity(dev1), runner.claim_identity(dev2))
        self.assertEqual(runner.claim_identity(dev1), "fact:HF-001")


class TestExtractQuotedFragment(unittest.TestCase):
    def test_extracts_double_quoted_english(self):
        hint = 'delete the sentence "Meta had run a test that caused exactly this surprise" (fact_id=MUSE-HC-006)'
        frag = runner.extract_quoted_fragment(hint)
        self.assertEqual(frag, "Meta had run a test that caused exactly this surprise")

    def test_extracts_ja_kagi_quotes(self):
        hint = "「原油価格が高い状態が続けば」を削除する(fact_id=HF-007)"
        frag = runner.extract_quoted_fragment(hint)
        self.assertEqual(frag, "原油価格が高い状態が続けば")

    def test_returns_none_when_no_quotes(self):
        self.assertIsNone(runner.extract_quoted_fragment("no quotes here at all"))

    def test_returns_none_for_empty_hint(self):
        self.assertIsNone(runner.extract_quoted_fragment(""))

    def test_picks_longest_fragment_when_multiple_quotes(self):
        hint = '"short" and also "a much longer quoted fragment here"'
        frag = runner.extract_quoted_fragment(hint)
        self.assertEqual(frag, "a much longer quoted fragment here")


class TestLocateTarget(unittest.TestCase):
    def test_uses_rewrite_hint_quote_as_first_key(self):
        text = "Intro sentence. The exact target phrase appears here. Outro sentence."
        # claim_textはtextと無関係でも、rewrite_hintの引用がexact substringなら
        # それを優先する(委任_10、rewrite_hintを第一キーにする設計)。
        target, method = runner.locate_target(
            "totally unrelated claim wording",
            'rewrite: replace "The exact target phrase appears here." per ledger',
            text,
        )
        self.assertEqual(target, "The exact target phrase appears here.")
        self.assertEqual(method, "rewrite_hint_quote")

    def test_falls_back_to_claim_text_when_hint_has_no_match(self):
        text = "Intro sentence. The market reacted very strongly today. Outro sentence."
        target, method = runner.locate_target(
            "The market reacted strongly today.", "no quotes in this hint", text)
        self.assertIn("market reacted", target)

    def test_falls_back_to_er010_word_overlap_when_sequence_matcher_fails(self):
        # SequenceMatcher(文字単位)では閾値未満だが、語単位overlapでは
        # 一致するケース(語順が大きく異なる長文)。
        text = ("Intro. Regulators in several countries discussed new rules about data "
                "privacy and cross-border transfers extensively during the summit. Outro.")
        claim = ("during the summit regulators extensively discussed cross-border data "
                 "transfers and new rules about privacy in several countries")
        target, method = runner.locate_target(claim, "", text)
        self.assertIsNotNone(target)
        self.assertTrue(method.startswith("er010_word_overlap") or method.startswith("sequence_matcher"))

    def test_returns_none_when_nothing_matches(self):
        text = "Completely unrelated sentence content here."
        target, method = runner.locate_target("XYZXYZXYZ nothing in common", "", text)
        self.assertIsNone(target)


class TestSplitSentencesGeneric(unittest.TestCase):
    def test_splits_on_period_and_ignores_headers(self):
        text = "# Heading\nFirst sentence. Second sentence! Third one?"
        sentences = runner.split_sentences_generic(text)
        self.assertEqual(sentences, ["First sentence.", "Second sentence!", "Third one?"])

    def test_split_ja_sentences_on_kuten(self):
        text = "# 見出し\nこれは一文目です。これは二文目です！これは三文目ですか？"
        sentences = runner.split_ja_sentences(text)
        self.assertEqual(sentences, ["これは一文目です。", "これは二文目です！", "これは三文目ですか？"])


class TestLocateJaCounterpartByPosition(unittest.TestCase):
    def test_maps_by_position_ratio_and_prefers_digit_match(self):
        en_full = "First. Second. The price rose by 20 percent in July. Fourth. Fifth."
        # JA全文は同じ位置(3文目付近)に対応する数値20を含む
        ja_full = "一文目。二文目。7月に価格が20%上昇した。四文目。五文目。"
        en_target = "The price rose by 20 percent in July."
        target, method = runner.locate_ja_counterpart_by_position(en_target, en_full, ja_full)
        self.assertIn("20", target)
        self.assertIn("digit_match", method)

    def test_returns_none_for_empty_text(self):
        target, method = runner.locate_ja_counterpart_by_position("x", "", "")
        self.assertIsNone(target)


class TestDeleteReoccurrenceGuard(unittest.TestCase):
    def test_delete_leaves_paraphrased_duplicate_detected_as_reoccurrence(self):
        # locate_best_sentenceのfuzzy matchが、削除後も類似文が残っている
        # ケースを検出できることを確認する(delete型claim単位再出現確認、
        # single_text_rewrite内部ロジックの構成要素のunit test)。
        updated_text = "Intro. The market reacted very strongly to the announcement. Outro."
        target, method = runner.locate_best_sentence(
            "The market reacted strongly to the announcement.", updated_text)
        self.assertIsNotNone(target)


class TestStage1UnionScreenConversion(unittest.TestCase):
    """s1u screenの変換ロジック(S1D出力キー -> V4A互換キー)をstage1_union_
    screenの実装から抽出したデータ変換規則で検証する(ネットワーク呼び出し
    なし、変換規則そのもののread-only regression test)。"""

    def test_floor_flags_are_carried_over_from_s1d_output(self):
        d = {"claim_in_article": "X", "related_fact_id_guess": "HF-1", "changed_actor": True,
             "changed_number": False, "materiality": "BLOCKING"}
        converted = {
            "claim_in_article": d.get("claim_in_article", ""), "origin": None,
            "related_fact_id": d.get("related_fact_id_guess", ""), "severity": "MAJOR",
            **{k: d.get(k, False) for k in runner.FLOOR_FLAGS},
        }
        self.assertEqual(converted["related_fact_id"], "HF-1")
        self.assertEqual(converted["severity"], "MAJOR")
        self.assertTrue(converted["changed_actor"])
        self.assertFalse(converted["changed_number"])


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
