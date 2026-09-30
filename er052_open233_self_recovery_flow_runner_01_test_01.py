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

    def test_certainty_flag_is_not_in_floor_set(self):
        # 委任_12(iteration4、§4-3改訂): changed_certaintyはfloor対象外化
        # された(B4-dがQUALITYへ再ラベルされたため、§7-0改訂)。floorに
        # 残っているとStage2 rubric(R3)のQUALITY判定と矛盾するため、
        # floor単独ではBLOCKINGへ強制せずLLM判定(rubric R3)に委ねる。
        self.assertNotIn("changed_certainty", runner.FLOOR_FLAGS)
        dev = {"changed_certainty": True}
        materiality, reason = runner.apply_floor("QUALITY", dev, "stage1_llm")
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)

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


class TestLocateParagraphBlock(unittest.TestCase):
    """委任_11 作業B-4(§5段落単位Rewriteへの拡張)のregression test。"""

    def test_finds_paragraph_containing_target_sentence(self):
        text = ("Intro paragraph sentence one. Intro paragraph sentence two.\n\n"
                "The market reacted very strongly to the news today. Another sentence in same block.\n\n"
                "Outro paragraph.")
        block, idx = runner.locate_paragraph_block(
            "The market reacted very strongly to the news today.", text)
        self.assertIn("Another sentence in same block.", block)
        self.assertEqual(idx, (1, 1))

    def test_includes_preceding_heading_only_block(self):
        text = ("# Meta had run a test that produced exactly this kind of surprise\n\n"
                "The body text explains further details about the surprise.\n\n"
                "Outro paragraph.")
        block, idx = runner.locate_paragraph_block(
            "The body text explains further details about the surprise.", text)
        self.assertIn("# Meta had run a test", block)
        self.assertIn("The body text explains", block)
        self.assertEqual(idx, (0, 1))

    def test_returns_none_when_not_found(self):
        block, idx = runner.locate_paragraph_block("nothing matches here", "Some unrelated text.")
        self.assertIsNone(block)
        self.assertIsNone(idx)

    def test_returns_none_for_empty_target(self):
        block, idx = runner.locate_paragraph_block(None, "Some text.\n\nMore text.")
        self.assertIsNone(block)
        self.assertIsNone(idx)


class TestFindMatchingPriorRecord(unittest.TestCase):
    """委任_11 作業B-3(§3-3停止判定の是正)のregression test。"""

    def test_same_fact_id_and_similar_claim_text_matches(self):
        dev = {"related_fact_id": "MUSE-HC-006",
               "claim_in_article": "Meta had run a test that caused exactly this surprise."}
        prior = [{"identity": "fact:MUSE-HC-006", "fact_id": "MUSE-HC-006",
                  "claim_text_norm": runner.normalize_claim_text(
                      "Meta had run a test that produced exactly this kind of surprise.")}]
        match = runner.find_matching_prior_record(dev, prior)
        self.assertIsNotNone(match)

    def test_same_fact_id_but_different_sentence_does_not_match(self):
        # bgroup_B4型の兄弟文カスケード: 同一fact_idでも別文(hook文/タイトル)
        # は「同一claim再発」として扱わない(is正後の挙動)。
        dev = {"related_fact_id": "MUSE-HC-006",
               "claim_in_article": "We Thought It Was AI, But There Was a Person All Along"}
        prior = [{"identity": "fact:MUSE-HC-006", "fact_id": "MUSE-HC-006",
                  "claim_text_norm": runner.normalize_claim_text(
                      "Meta had run a test that produced exactly this kind of surprise.")}]
        match = runner.find_matching_prior_record(dev, prior)
        self.assertIsNone(match)

    def test_different_fact_id_does_not_match(self):
        dev = {"related_fact_id": "HF-002", "claim_in_article": "Some claim text"}
        prior = [{"identity": "fact:HF-001", "fact_id": "HF-001", "claim_text_norm": "some claim text"}]
        self.assertIsNone(runner.find_matching_prior_record(dev, prior))

    def test_no_fact_id_requires_exact_hash_identity_match(self):
        dev1 = {"related_fact_id": "", "claim_in_article": "Alpha claim text"}
        prior = [{"identity": runner.claim_identity(dev1), "fact_id": "",
                  "claim_text_norm": runner.normalize_claim_text("Alpha claim text")}]
        self.assertIsNotNone(runner.find_matching_prior_record(dev1, prior))
        dev2 = {"related_fact_id": "", "claim_in_article": "Completely different beta claim"}
        self.assertIsNone(runner.find_matching_prior_record(dev2, prior))


class TestDetectRewriteNewPrecheckFindings(unittest.TestCase):
    """委任_11 作業B-6(§4 Rewrite由来新規逸脱検出)のregression test。"""

    LEDGER = ("[VERIFIED] F001: Alice announced a plan.\n"
              "  numeric_value: 20%\n")

    def test_new_finding_not_in_baseline_is_detected(self):
        baseline = []  # 元記事にはprecheck findingが無かったとする
        updated_text = "Bob announced a plan. The article mentions 45% instead."
        new_findings = runner.detect_rewrite_new_precheck_findings(self.LEDGER, baseline, updated_text)
        self.assertTrue(len(new_findings) >= 1)

    def test_finding_already_in_baseline_is_not_reported_again(self):
        updated_text = "Bob announced a plan. The article mentions 45% instead."
        baseline = runner.precheck.run_precheck(self.LEDGER, updated_text)
        new_findings = runner.detect_rewrite_new_precheck_findings(self.LEDGER, baseline, updated_text)
        self.assertEqual(new_findings, [])


class TestAggregateMeasurementsResolvedStatesAndGroups(unittest.TestCase):
    """委任_11 作業B-5是正(§8測定是正、Opus L2 #2論点5/6/7)のregression test。"""

    def _instance(self, instance_id, group, final_state, cycles=None, cost=0.1, stage4_reason=None):
        return {
            "instance_id": instance_id, "group": group, "expected_group_label": "x",
            "final_state": final_state, "stage4_reason": stage4_reason,
            "cycles": cycles or [], "stage1_call_used": False,
            "total_cost_jpy": cost, "total_calls": 1, "elapsed_seconds": 1.0,
        }

    def test_resolved_rewrite_then_downgrade_counts_toward_breakdown(self):
        results = [
            self._instance("x1", "test", "RESOLVED_REWRITE_THEN_DOWNGRADE",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}],
                                     "recheck_all_prior_issues_resolved": True,
                                     "stage2_results": []},
                                    {"stage2_results": []}]),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["escalation_zero_breakdown"]["true_resolved_all_prior_issues_resolved_true"], 1)

    def test_resolved_rewrite_then_downgrade_without_confirmation_is_unconfirmed(self):
        results = [
            self._instance("x2", "test", "RESOLVED_REWRITE_THEN_DOWNGRADE",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}],
                                     "recheck_all_prior_issues_resolved": False,
                                     "stage2_results": []},
                                    {"stage2_results": []}]),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["escalation_zero_breakdown"]["all_prior_issues_resolved_unconfirmed"], 1)

    def test_group_escalation_rates_separate_groups(self):
        results = [
            self._instance("s1", "safety", "STAGE4_ESCALATION", stage4_reason="x"),
            self._instance("s2", "safety", "RESOLVED_REWRITE"),
            self._instance("n1", "negative", "RESOLVED_REWRITE"),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["group_escalation_rates"]["safety"]["n"], 2)
        self.assertEqual(agg["group_escalation_rates"]["safety"]["escalated"], 1)
        self.assertEqual(agg["group_escalation_rates"]["negative"]["escalated"], 0)

    def test_real_run_escalation_only_counts_real_run_ids(self):
        results = [
            self._instance("hormuz_run02_advanced", "hormuz", "STAGE4_ESCALATION", stage4_reason="x"),
            self._instance("bgroup_B1", "b_group", "STAGE4_ESCALATION", stage4_reason="x"),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["real_run"]["n"], 1)
        self.assertEqual(agg["real_run"]["escalated"], 1)

    def test_article_level_aggregates_sum_cost_across_variants(self):
        results = [
            self._instance("meta_run03_standard", "meta", "RESOLVED_REWRITE", cost=1.0),
            self._instance("meta_run03_advanced", "meta", "RESOLVED_REWRITE", cost=1.5),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["article_level"]["aggregates"]["meta_run03"]["total_cost_jpy"], 2.5)
        self.assertFalse(agg["article_level"]["aggregates"]["meta_run03"]["escalated"])
        self.assertEqual(agg["article_level"]["worst_cost_jpy"], 2.5)

    def test_s1u_variant_key_renamed_and_labeled(self):
        results = [
            self._instance("hormuz_run02_advanced", "hormuz", "RESOLVED_REWRITE"),
        ]
        results[0]["s1u_screen_used"] = True
        results[0]["s1u_additional_block"] = True
        results[0]["s1u_additional_block_label"] = "true_positive"
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["s1u_variant"]["additional_block_count"], 1)
        self.assertEqual(agg["s1u_variant"]["additional_block_true_positive_count"], 1)
        self.assertEqual(agg["s1u_variant"]["additional_block_false_positive_count"], 0)

    def test_unconfirmed_after_reverify_counted(self):
        results = [
            self._instance("x3", "test", "STAGE4_ESCALATION", stage4_reason="unconfirmed_after_reverify"),
        ]
        agg = runner.aggregate_measurements(results)
        self.assertEqual(agg["rewrite_deviation_qa"]["unconfirmed_after_reverify_count"], 1)


class TestJ1BugFixesSourceInspection(unittest.TestCase):
    """委任_11 作業B-1/B-2(バグ修正2件、Opus L2 #2論点1推奨1/2)の
    read-only regression test。ネットワーク呼び出しを伴う完全なpaired_
    rewrite()実行はできないため(API課金が必要)、ソーステキスト検査で
    「j1_pair_not_locatedの早期returnが無い」「EN側フォールバック編集の
    分岐が実装されている」ことを機械確認する。"""

    def test_no_early_return_on_pair_not_located(self):
        import inspect
        src = inspect.getsource(runner.paired_rewrite)
        self.assertNotIn('"method": "j1_pair_not_located"', src)

    def test_en_side_is_edited_after_ja_fulltext_fallback(self):
        import inspect
        src = inspect.getsource(runner.paired_rewrite)
        self.assertIn("en_local_edit", src)
        self.assertIn("en_fulltext_fallback", src)
        # 旧バグ(EN側を無条件でen_fullのまま残す一行)が復活していないことを確認
        self.assertNotIn('updated_en = en_full  # EN側はcycle 2のEN Recheckで再評価に委ねる', src)


class TestRubricR3Wiring(unittest.TestCase):
    """委任_12(iteration4)regression: Stage2がR2ではなくR3(自然な解釈
    基準)を使うこと、materialityがBLOCKINGのclaimのみがStage3へ渡ること
    (QUALITYはRewriteされず通過)をソース検査+ロジックで確認する。"""

    def test_run_stage2_uses_r3_prime_not_r2(self):
        import inspect
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        src = inspect.getsource(runner.run_stage2)
        self.assertIn("s2c.RUBRIC_R3_PRIME", src)
        self.assertNotIn("s2c.RUBRIC_R2,", src)
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_NATURAL_INTERPRETATION"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_PRIME"))
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_NATURAL_INTERPRETATION)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_PRIME)

    def test_only_blocking_claims_dispatched_to_stage3(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('blocking_claims = [c for c in stage2_results if c["materiality"] == "BLOCKING"]', src)
        # QUALITY/ACCEPTABLEはrewrite_recordsを生成する経路(run_stage3_for_claim)
        # の入力(blocking_claims)に含まれないことをロジックで確認する。
        stage2_results = [
            {"materiality": "QUALITY", "dev": {}, "rewrite_kind": "delete"},
            {"materiality": "ACCEPTABLE", "dev": {}, "rewrite_kind": "delete"},
            {"materiality": "BLOCKING", "dev": {}, "rewrite_kind": "delete"},
        ]
        blocking_claims = [c for c in stage2_results if c["materiality"] == "BLOCKING"]
        self.assertEqual(len(blocking_claims), 1)


class TestMeasureRewriteQualityDegradation(unittest.TestCase):
    """委任_12(iteration4、§8追加測定)regression。"""

    def test_no_change_is_not_a_candidate(self):
        text = "Title line.\n\nParagraph one. It has two sentences.\n\nParagraph two."
        result = runner.measure_rewrite_quality_degradation(text, text)
        self.assertFalse(result["degradation_candidate"])
        self.assertEqual(result["sentence_drop_rate"], 0.0)

    def test_sentence_drop_and_hedge_increase_flag_candidate(self):
        before = "Title.\n\nOne. Two. Three. Four. Five."
        after = "Title.\n\nIt may possibly have seemed to be one thing."
        result = runner.measure_rewrite_quality_degradation(before, after)
        self.assertTrue(result["degradation_candidate"])
        self.assertGreater(result["hedge_word_increase"], 0)

    def test_paragraph_count_decrease_flags_candidate(self):
        before = "Title.\n\nPara one.\n\nPara two."
        after = "Title.\n\nPara one merged with para two."
        result = runner.measure_rewrite_quality_degradation(before, after)
        self.assertTrue(result["paragraph_delta"] < 0)
        self.assertTrue(result["degradation_candidate"])


class TestIter4AdditionalMeasures(unittest.TestCase):
    """委任_12(iteration4、§8追加測定7項目)regression。"""

    def _instance(self, instance_id, group, final_state, cycles=None):
        return {
            "instance_id": instance_id, "group": group, "expected_group_label": "x",
            "final_state": final_state, "stage4_reason": None, "cycles": cycles or [],
            "stage1_call_used": False, "total_cost_jpy": 0.1, "total_calls": 1, "elapsed_seconds": 1.0,
        }

    def test_normal_group_ids_include_all_7_negatives_and_2_normals(self):
        self.assertEqual(len(runner.NORMAL_GROUP_INSTANCE_IDS), 9)
        self.assertIn("neg1_meta_b3prod_a2", runner.NORMAL_GROUP_INSTANCE_IDS)
        self.assertIn("hormuz_run03_advanced", runner.NORMAL_GROUP_INSTANCE_IDS)
        self.assertIn("meta_run03_advanced", runner.NORMAL_GROUP_INSTANCE_IDS)

    def test_unnecessary_rewrite_counted_for_normal_group_only(self):
        results = [
            self._instance("neg1_meta_b3prod_a2", "negative", "RESOLVED_REWRITE",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}], "stage2_results": []}]),
            self._instance("bgroup_B1", "b_group", "RESOLVED_REWRITE",
                            cycles=[{"rewrite_records": [{"mechanism": "x"}], "stage2_results": []}]),
        ]
        agg = runner._iter4_additional_measures(results)
        self.assertEqual(agg["unnecessary_rewrite"]["count"], 1)
        self.assertEqual(agg["unnecessary_rewrite"]["instance_ids"], ["neg1_meta_b3prod_a2"])

    def test_stage1_false_block_counted_for_normal_group(self):
        results = [
            self._instance("neg2_meta_refresh_a2", "negative", "STAGE4_ESCALATION"),
        ]
        agg = runner._iter4_additional_measures(results)
        self.assertEqual(agg["natural_interpretation_blocked"]["stage1_false_block_count"], 1)

    def test_stage2_false_block_claim_counted_for_normal_group(self):
        results = [
            self._instance("neg3_hormuz_prodrunner_b1b", "negative", "RESOLVED_REWRITE",
                            cycles=[{"stage2_results": [{"materiality": "BLOCKING"},
                                                          {"materiality": "QUALITY"}]}]),
        ]
        agg = runner._iter4_additional_measures(results)
        self.assertEqual(agg["natural_interpretation_blocked"]["stage2_false_block_claim_count"], 1)

    def test_stage4_reason_breakdown(self):
        results = [
            self._instance("x1", "test", "STAGE4_ESCALATION"),
            self._instance("x2", "test", "STAGE4_ESCALATION"),
        ]
        results[0]["stage4_reason"] = "cycle_limit_exhausted"
        results[1]["stage4_reason"] = "same_claim_fact_id_reblocked"
        agg = runner._iter4_additional_measures(results)
        self.assertEqual(agg["stage4_reason_breakdown"]["cycle_limit_exhausted"], 1)
        self.assertEqual(agg["stage4_reason_breakdown"]["same_claim_fact_id_reblocked"], 1)


class TestS1UCounterfactual(unittest.TestCase):
    """委任_12(iteration4、§2項目6)regression: S1-Uが付加したclaimを除外
    した反実仮想が0 callで(=instance_resultsの再解析のみで)算出できること。"""

    def _instance(self, instance_id, group, final_state, s1u_additional_block=False, cost=1.0):
        return {
            "instance_id": instance_id, "group": group, "expected_group_label": "x",
            "final_state": final_state, "stage4_reason": "x" if final_state == "STAGE4_ESCALATION" else None,
            "cycles": [{"stage2_results": []}] if final_state != "ACCEPTABLE_STAGE1" else [],
            "stage1_call_used": False, "s1u_screen_used": s1u_additional_block,
            "s1u_additional_blocking_count": 1 if s1u_additional_block else 0,
            "s1u_additional_block": s1u_additional_block,
            "s1u_additional_block_label": "true_positive" if s1u_additional_block else None,
            "call_log": [], "total_cost_jpy": cost, "total_calls": 1, "elapsed_seconds": 1.0,
        }

    def test_s1u_contributed_escalation_removed_in_counterfactual(self):
        results = [
            self._instance("hormuz_run02_advanced", "hormuz", "STAGE4_ESCALATION",
                            s1u_additional_block=True, cost=5.0),
        ]
        cf = runner.compute_s1u_counterfactual(results)
        self.assertEqual(cf["with_s1u"]["final_stop_count"], 1)
        self.assertEqual(cf["without_s1u_counterfactual"]["final_stop_count"], 0)
        self.assertEqual(cf["without_s1u_counterfactual"]["total_cost_jpy"], 0.0)
        self.assertIn("hormuz_run02_advanced", cf["known_recall_miss_instances_among_removed"])

    def test_instance_without_s1u_block_is_unchanged(self):
        results = [
            self._instance("neg1_meta_b3prod_a2", "negative", "RESOLVED_STAGE2_DOWNGRADE",
                            s1u_additional_block=False, cost=0.5),
        ]
        cf = runner.compute_s1u_counterfactual(results)
        self.assertEqual(cf["with_s1u"]["total_cost_jpy"], cf["without_s1u_counterfactual"]["total_cost_jpy"])
        self.assertEqual(cf["instances_removed_by_counterfactual"], [])


if __name__ == "__main__":
    unittest.main()
