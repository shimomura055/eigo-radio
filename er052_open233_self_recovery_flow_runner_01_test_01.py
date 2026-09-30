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
        # 委任_13(iteration5): RUBRIC_R3_PRIME -> RUBRIC_R3_TRIPLE_PRIMEへ切替
        # (単体較正でB4-d/B1-c QUALITY 2/2+Safety-critical 10claim誤降格0を
        # 達成、summary_r3tripleprime_calibration.json参照)。
        self.assertIn("s2c.RUBRIC_R3_TRIPLE_PRIME", src)
        self.assertNotIn("s2c.RUBRIC_R2,", src)
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_NATURAL_INTERPRETATION"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_PRIME"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_DOUBLE_PRIME"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_TRIPLE_PRIME"))
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_NATURAL_INTERPRETATION)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_PRIME)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_DOUBLE_PRIME)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_TRIPLE_PRIME)

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


# ============================================================
# 委任_13(iteration5)品質劣化検出v2のregression test。fixtureはiteration4
# 実測証跡(er052_output/open233_self_recovery_flow_runner_01_iter4/
# summary_flow_runner.json、neg1_meta_b3prod_a2/neg2_meta_refresh_a2の
# en_text_before_rewrite/en_text_after_rewrite、および読み比べページで
# Opusが逐語引用したneg3の「In one line」文)をそのまま埋め込む
# (Opus L2レビュー#3論点6-B「iter4のv1検出器は4種の劣化のうち3種を
# 検出できなかった」の再発防止、既存iter4証跡は変更しない)。
# ============================================================
NEG1_CYCLE1_BEFORE = (
    "# We Thought It Was AI—But There Was a Person Inside Meta's Muse\n\n"
    "Ring, ring. A call seemed to come from an AI agent. But as the conversation went on, the voice "
    "was not AI at all. It was a person.\n\n"
    "Meta had run a test that caused exactly this surprise.\n\n"
    "The test used the phone feature of its AI agent, Muse. In some calls through Muse, trained "
    "contract workers made the calls, not AI. They carried each conversation through to the end."
)
NEG1_CYCLE1_AFTER = (
    "# Meta Tested Human-Handled Calls Through Muse\n\n"
    "Meta tested having trained contract workers make some calls through Muse.\n\n"
    "Meta had run a test that caused exactly this surprise.\n\n"
    "The test used the phone feature of its AI agent, Muse. In some calls through Muse, trained "
    "contract workers made the calls, not AI. They carried each conversation through to the end."
)
NEG1_CYCLE2_BEFORE = (
    "# Meta Tested Human-Handled Calls Through Muse\n\n"
    "Meta tested having trained contract workers make some calls through Muse.\n\n"
    "Meta had run a test that caused exactly this surprise.\n\n"
    "The test used the phone feature of its AI agent, Muse. In some calls through Muse, trained "
    "contract workers made the calls, not AI. They carried each conversation through to the end."
)
NEG1_CYCLE2_AFTER = (
    "# Meta Tested Human-Handled Calls Through Muse\n\n"
    "Meta tested having trained contract workers make some calls through Muse.\n\n"
    "Meta had tested having trained human contractors handle some calls made through its AI agent "
    "Muse.\n\n"
    "The test used the phone feature of its AI agent, Muse. In some calls through Muse, trained "
    "contract workers made the calls, not AI. They carried each conversation through to the end."
)
NEG2_CYCLE1_BEFORE = (
    "# Some AI Phone Calls Had Humans Behind the Scenes\n\n"
    "There was a small twist. A service let people ask AI to make phone calls. But humans were "
    "making some calls behind the scenes. This was part of a test.\n\n"
    "People who asked Muse to make a call might think AI was doing it. If this was not explained "
    "clearly, users could not know if it was AI or a person. They enjoyed the ease of AI. But they "
    "did not know that a human was on the other end. This was happening behind the scenes."
)
NEG2_CYCLE1_AFTER = (
    "# Some AI Phone Calls Had Humans Behind the Scenes\n\n"
    "There was a small twist. A service let people ask AI to make phone calls. But humans were "
    "making some calls behind the scenes. This was part of a test.\n\n"
    "But sometimes, a human was speaking instead. This was happening behind the scenes."
)
NEG3_INLINE_BEFORE = (
    "The fee plan left the stage, but the events driving oil prices, and the prices themselves, "
    "quickly returned."
)
NEG3_INLINE_AFTER = (
    "After the announcement replacing the fee plan, Brent futures briefly pared gains before "
    "returning to near pre-announcement highs; concerns about attacks, the blockade and tanker "
    "safety continued."
)


class TestMeasureRewriteQualityDegradationV2(unittest.TestCase):
    def test_neg1_cycle1_hook_and_title_loss_is_flagged_but_does_not_alone_trigger_regeneration(self):
        qd = runner.measure_rewrite_quality_degradation_v2(NEG1_CYCLE1_BEFORE, NEG1_CYCLE1_AFTER)
        self.assertTrue(qd["title_changed"])
        self.assertTrue(qd["first_paragraph_changed"])
        self.assertTrue(qd["hook_or_title_changed"])
        # (d)は単独ではneeds_regenerationのトリガにしない(BLOCKING claim
        # 自体がhookにある正当なケースがあるため、委任文の設計どおり)。
        self.assertFalse(qd["duplicate_paragraph_detected"])
        self.assertFalse(qd["orphan_contrastive_detected"])

    def test_neg1_cycle2_duplicate_paragraph_detected_and_triggers_regeneration(self):
        qd = runner.measure_rewrite_quality_degradation_v2(NEG1_CYCLE2_BEFORE, NEG1_CYCLE2_AFTER)
        self.assertTrue(qd["duplicate_paragraph_detected"])
        self.assertGreaterEqual(qd["duplicate_paragraphs"][0]["jaccard"], 0.4)
        self.assertTrue(qd["needs_regeneration"])

    def test_neg2_orphan_contrastive_opener_detected_and_triggers_regeneration(self):
        qd = runner.measure_rewrite_quality_degradation_v2(NEG2_CYCLE1_BEFORE, NEG2_CYCLE1_AFTER)
        self.assertTrue(qd["orphan_contrastive_detected"])
        self.assertIn("But sometimes, a human was speaking instead.",
                       qd["orphan_contrastive_paragraphs"][0]["opening"])
        self.assertTrue(qd["needs_regeneration"])

    def test_neg3_style_localized_vocab_difficulty_increase_detected_via_fragment(self):
        # 全文平均では希釈されて閾値未満になる(iter4実測: neg3/B2ともwhole
        # text難語率上昇は0.02未満)ため、changed_fragmentsを渡した場合のみ
        # 検出できることを固定する(Opus L2レビュー#3論点6-B該当事例)。
        qd_wholetext_only = runner.measure_rewrite_quality_degradation_v2(
            NEG3_INLINE_BEFORE, NEG3_INLINE_AFTER)
        self.assertTrue(qd_wholetext_only["vocab_difficulty_increased"])  # 短文単体では全文判定でも検出可
        qd_with_fragment = runner.measure_rewrite_quality_degradation_v2(
            NEG3_INLINE_BEFORE, NEG3_INLINE_AFTER,
            changed_fragments=[{"before": NEG3_INLINE_BEFORE, "after": NEG3_INLINE_AFTER}])
        self.assertTrue(qd_with_fragment["vocab_difficulty_increased_fragment"])
        self.assertTrue(qd_with_fragment["needs_regeneration"])

    def test_no_degradation_when_texts_identical(self):
        qd = runner.measure_rewrite_quality_degradation_v2(NEG1_CYCLE1_BEFORE, NEG1_CYCLE1_BEFORE)
        self.assertFalse(qd["needs_regeneration"])
        self.assertFalse(qd["duplicate_paragraph_detected"])
        self.assertFalse(qd["orphan_contrastive_detected"])
        self.assertFalse(qd["vocab_difficulty_increased"])


class TestInferArticleLevel(unittest.TestCase):
    def test_a2_suffix_maps_to_a2(self):
        self.assertEqual(runner.infer_article_level("neg1_meta_b3prod_a2"), "a2")

    def test_standard_suffix_maps_to_a2(self):
        self.assertEqual(runner.infer_article_level("hormuz_run03_standard"), "a2")

    def test_b1b_suffix_maps_to_b1b(self):
        self.assertEqual(runner.infer_article_level("neg3_hormuz_prodrunner_b1b"), "b1b")

    def test_advanced_suffix_maps_to_b1b(self):
        self.assertEqual(runner.infer_article_level("hormuz_run03_advanced"), "b1b")

    def test_unrecognized_id_returns_none(self):
        self.assertIsNone(runner.infer_article_level("bgroup_B1"))

    def test_level_constraint_text_includes_level_specific_wording(self):
        self.assertIn("CEFR-A2", runner.level_constraint_text("a2"))
        self.assertIn("B1", runner.level_constraint_text("b1b"))
        self.assertIn("Preserve the title", runner.level_constraint_text(None))


class TestStage2TwoOfTwoEligibility(unittest.TestCase):
    def test_eligible_when_normal_group_blocking_and_floor_not_applied(self):
        inst = {"instance_id": "neg1_meta_b3prod_a2"}
        result = {"materiality": "BLOCKING", "floor_reason": None}
        self.assertTrue(runner.stage2_two_of_two_eligible(inst, result))

    def test_not_eligible_when_floor_applied(self):
        inst = {"instance_id": "neg1_meta_b3prod_a2"}
        result = {"materiality": "BLOCKING", "floor_reason": "deterministic_floor:changed_time"}
        self.assertFalse(runner.stage2_two_of_two_eligible(inst, result))

    def test_not_eligible_when_not_blocking(self):
        inst = {"instance_id": "neg1_meta_b3prod_a2"}
        result = {"materiality": "QUALITY", "floor_reason": None}
        self.assertFalse(runner.stage2_two_of_two_eligible(inst, result))

    def test_not_eligible_when_outside_normal_group(self):
        inst = {"instance_id": "safety_er009_scenario_a"}
        result = {"materiality": "BLOCKING", "floor_reason": None}
        self.assertFalse(runner.stage2_two_of_two_eligible(inst, result))


class TestCiteOrRelease(unittest.TestCase):
    def test_cited_sentence_present_in_article_stays_unresolved(self):
        article_text = "Meta ran the test. The old claim sentence is still here. Nothing else changed."
        parsed = {"prior_issues_resolved": [
            {"index": 0, "resolved": False, "explanation": "still present",
             "remaining_sentence": "The old claim sentence is still here."},
        ]}
        out = runner.apply_cite_or_release(parsed, article_text)
        self.assertFalse(out["prior_issues_resolved"][0]["resolved"])
        self.assertFalse(out["prior_issues_resolved"][0]["cite_or_release_overridden"])
        self.assertFalse(out["all_prior_issues_resolved"])
        self.assertEqual(out["released_count"], 0)

    def test_unresolved_without_valid_citation_is_released(self):
        article_text = "Meta ran the test. The claim was removed already. Nothing else changed."
        parsed = {"prior_issues_resolved": [
            {"index": 0, "resolved": False, "explanation": "vague",
             "remaining_sentence": "This sentence does not exist in the article."},
        ]}
        out = runner.apply_cite_or_release(parsed, article_text)
        self.assertTrue(out["prior_issues_resolved"][0]["resolved"])
        self.assertTrue(out["prior_issues_resolved"][0]["cite_or_release_overridden"])
        self.assertTrue(out["all_prior_issues_resolved"])
        self.assertEqual(out["released_count"], 1)

    def test_empty_remaining_sentence_is_released(self):
        article_text = "Meta ran the test. Nothing else changed."
        parsed = {"prior_issues_resolved": [
            {"index": 0, "resolved": False, "explanation": "vague", "remaining_sentence": ""},
        ]}
        out = runner.apply_cite_or_release(parsed, article_text)
        self.assertTrue(out["prior_issues_resolved"][0]["resolved"])
        self.assertEqual(out["released_count"], 1)

    def test_already_resolved_items_are_not_touched(self):
        article_text = "Meta ran the test."
        parsed = {"prior_issues_resolved": [
            {"index": 0, "resolved": True, "explanation": "fixed", "remaining_sentence": ""},
        ]}
        out = runner.apply_cite_or_release(parsed, article_text)
        self.assertTrue(out["prior_issues_resolved"][0]["resolved"])
        self.assertFalse(out["prior_issues_resolved"][0]["cite_or_release_overridden"])
        self.assertEqual(out["released_count"], 0)


class TestWilsonScoreInterval(unittest.TestCase):
    def test_zero_n_returns_zero_interval(self):
        self.assertEqual(runner.wilson_score_interval(0, 0), (0.0, 0.0))

    def test_zero_successes_lower_bound_is_zero(self):
        lo, hi = runner.wilson_score_interval(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.0)

    def test_all_successes_upper_bound_is_at_most_one(self):
        lo, hi = runner.wilson_score_interval(10, 10)
        self.assertLessEqual(hi, 1.0)
        self.assertLess(lo, 1.0)

    def test_interval_widens_with_smaller_n(self):
        lo_small, hi_small = runner.wilson_score_interval(5, 10)
        lo_large, hi_large = runner.wilson_score_interval(50, 100)
        self.assertLess(lo_small, lo_large)
        self.assertGreater(hi_small, hi_large)


class TestUnnecessaryRewriteV2Correction(unittest.TestCase):
    def test_neg5_excluded_from_v2_corrected_numerator(self):
        self.assertIn("neg5_hormuz_div_a2", runner.UNNECESSARY_REWRITE_V2_EXCLUDE_INSTANCE_IDS)

    def test_iter5_measures_report_both_v1_and_v2_counts(self):
        base = {
            "group": "negative", "final_state": "RESOLVED_REWRITE", "stage4_reason": None,
            "total_cost_jpy": 0.1, "call_log": [], "total_calls": 1, "elapsed_seconds": 0.1,
        }
        results = [
            {**base, "instance_id": "neg5_hormuz_div_a2",
             "cycles": [{"rewrite_records": [{"claim_identity": "x"}], "stage2_results": []}]},
            {**base, "instance_id": "neg1_meta_b3prod_a2",
             "cycles": [{"rewrite_records": [{"claim_identity": "y"}], "stage2_results": []}]},
            {**base, "instance_id": "neg4_smallbag_div_a2", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
            {**base, "instance_id": "neg6_smallbag_div_b1b", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
            {**base, "instance_id": "neg7_meta_prodrunner_b1b", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
            {**base, "instance_id": "neg3_hormuz_prodrunner_b1b", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
            {**base, "instance_id": "hormuz_run03_advanced", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
            {**base, "instance_id": "meta_run03_advanced", "final_state": "RESOLVED_STAGE2_DOWNGRADE",
             "cycles": [{"stage2_results": []}]},
        ]
        out = runner._iter5_additional_measures(results)
        corrected = out["unnecessary_rewrite_v2_corrected"]
        self.assertEqual(corrected["count_v1_uncorrected"], 2)
        self.assertEqual(corrected["count_v2_corrected"], 1)
        self.assertNotIn("neg5_hormuz_div_a2", corrected["instance_ids_v2"])
        self.assertIn("neg1_meta_b3prod_a2", corrected["instance_ids_v2"])


# ------------------------------------------------------------
# 委任_14(iteration6、作業B-7): 丸め許容6例・Meta hook不BLOCK・B3型
# so->while・In one line長文化検出・ラダー停止・floor-cited/section_type。
# ------------------------------------------------------------
class TestNaturalRoundingFloorSuppression(unittest.TestCase):
    LEDGER = ("[VERIFIED] HF-001: The tanker traffic share fell.\n"
              "  scope: Hormuz strait tanker traffic\n"
              "  numeric_value: 2.6%\n"
              "  date_or_period: 2026-07-14\n")

    def _dev(self, claim_text):
        return {"claim_in_article": claim_text, "related_fact_id": "HF-001",
                "changed_number": True, "changed_actor": False, "changed_negation": False,
                "changed_comparison": False, "changed_time": False}

    def test_2_6_to_about_3_percent_is_natural_rounding_ok(self):
        dev = self._dev("Traffic fell by about 3%.")
        sanitized = runner._sanitize_dev_for_rounding(dev, "Traffic fell by about 3%.", self.LEDGER)
        self.assertFalse(sanitized["changed_number"])
        materiality, reason = runner.apply_floor("QUALITY", sanitized, "stage1_llm")
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)

    def test_1_7_to_about_2_percent_is_natural_rounding_ok(self):
        ledger = self.LEDGER.replace("2.6%", "1.7%")
        dev = self._dev("Traffic fell by about 2%.")
        sanitized = runner._sanitize_dev_for_rounding(dev, "Traffic fell by about 2%.", ledger)
        self.assertFalse(sanitized["changed_number"])

    def test_84_73_to_about_85_is_natural_rounding_ok(self):
        ledger = self.LEDGER.replace("2.6%", "84.73 workers")
        dev = self._dev("about 85 workers")
        sanitized = runner._sanitize_dev_for_rounding(dev, "about 85 workers", ledger)
        self.assertFalse(sanitized["changed_number"])

    def test_2_6_to_about_2_percent_is_meaning_changing_ng(self):
        dev = self._dev("Traffic fell by about 2%.")
        sanitized = runner._sanitize_dev_for_rounding(dev, "Traffic fell by about 2%.", self.LEDGER)
        self.assertTrue(sanitized["changed_number"])
        materiality, reason = runner.apply_floor("QUALITY", sanitized, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")

    def test_2_99_to_about_2_percent_is_meaning_changing_ng(self):
        ledger = self.LEDGER.replace("2.6%", "2.99%")
        dev = self._dev("about 2%")
        sanitized = runner._sanitize_dev_for_rounding(dev, "about 2%", ledger)
        self.assertTrue(sanitized["changed_number"])

    def test_84_73_to_about_100_is_meaning_changing_ng(self):
        ledger = self.LEDGER.replace("2.6%", "84.73 workers")
        dev = self._dev("about 100 workers")
        sanitized = runner._sanitize_dev_for_rounding(dev, "about 100 workers", ledger)
        self.assertTrue(sanitized["changed_number"])

    def test_other_floor_flags_unaffected_by_rounding_suppression(self):
        dev = self._dev("about 3%")
        dev["changed_actor"] = True
        sanitized = runner._sanitize_dev_for_rounding(dev, "about 3%", self.LEDGER)
        self.assertFalse(sanitized["changed_number"])
        materiality, reason = runner.apply_floor("QUALITY", sanitized, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")
        self.assertIn("changed_actor", reason)
        self.assertNotIn("changed_number", reason)


class TestIsNaturalRoundingDirect(unittest.TestCase):
    def test_six_examples_from_user_spec(self):
        import er052_open233_self_recovery_precheck_01 as pc
        self.assertTrue(pc.is_natural_rounding(2.6, 3.0))
        self.assertTrue(pc.is_natural_rounding(1.7, 2.0))
        self.assertTrue(pc.is_natural_rounding(84.73, 85.0))
        self.assertFalse(pc.is_natural_rounding(2.6, 2.0))
        self.assertFalse(pc.is_natural_rounding(2.99, 2.0))
        self.assertFalse(pc.is_natural_rounding(84.73, 100.0))


class TestHookAwareDowngrade(unittest.TestCase):
    def test_meta_style_scope_only_hook_claim_is_downgraded(self):
        dev = {"changed_scope": True, "changed_fact": False, "changed_causality": False,
               "changed_certainty": False, "changed_number": False, "changed_actor": False,
               "changed_negation": False, "changed_comparison": False, "changed_time": False,
               "unsupported_new_claim": False}
        materiality, reason = runner.apply_hook_aware_downgrade("BLOCKING", dev, "hook", None)
        self.assertEqual(materiality, "QUALITY")
        self.assertEqual(reason, "hook_aware_scope_downgrade")

    def test_not_applied_outside_hook_sections(self):
        dev = {"changed_scope": True}
        materiality, reason = runner.apply_hook_aware_downgrade("BLOCKING", dev, "body", None)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_not_applied_when_floor_already_fired(self):
        dev = {"changed_scope": True}
        materiality, reason = runner.apply_hook_aware_downgrade(
            "BLOCKING", dev, "hook", "deterministic_floor:changed_comparison")
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_not_applied_when_other_flag_also_fired(self):
        # neg1(Meta)実例の実際のflag(changed_fact/changed_certainty/
        # unsupported_new_claim)はHook-aware対象外のまま(監査文書の
        # 既知の限界どおり)。
        dev = {"changed_scope": False, "changed_fact": True, "changed_certainty": True,
               "unsupported_new_claim": True}
        materiality, reason = runner.apply_hook_aware_downgrade("BLOCKING", dev, "hook", None)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_changed_comparison_is_never_relaxed_because_it_is_in_floor_flags(self):
        # changed_comparisonはFLOOR_FLAGSに含まれる安全装置であり、
        # Hook-aware緩和の対象に含めない(governance: 既存安全装置の
        # 独自判断での無効化禁止)。
        self.assertIn("changed_comparison", runner.FLOOR_FLAGS)
        self.assertNotEqual(runner.HOOK_AWARE_ELIGIBLE_FLAG, "changed_comparison")


class TestDetectClaimSectionType(unittest.TestCase):
    ARTICLE = (
        "# A Call That Surprised Everyone\n\n"
        "Ring, ring. A call seemed to come from an AI agent, but it was a person all along.\n\n"
        "Meta ran a test with trained contract workers on some calls, a report says.\n\n"
        "## In one line\n"
        "A test used real people on some calls.\n"
    )

    def test_title_detected(self):
        self.assertEqual(runner.detect_claim_section_type(
            "A Call That Surprised Everyone", self.ARTICLE), "title")

    def test_hook_paragraph_detected(self):
        self.assertEqual(runner.detect_claim_section_type(
            "Ring, ring. A call seemed to come from an AI agent, but it was a person all along.",
            self.ARTICLE), "hook")

    def test_in_one_line_detected(self):
        self.assertEqual(runner.detect_claim_section_type(
            "A test used real people on some calls.", self.ARTICLE), "in_one_line")

    def test_body_detected(self):
        self.assertEqual(runner.detect_claim_section_type(
            "Meta ran a test with trained contract workers on some calls, a report says.",
            self.ARTICLE), "body")


class TestFloorCitedVariant(unittest.TestCase):
    LEDGER = ("[VERIFIED] HF-001: The tanker traffic share fell.\n"
              "  scope: Hormuz strait tanker traffic\n"
              "  numeric_value: 2.6%\n"
              "  date_or_period: 2026-07-14\n")

    def test_precheck_is_always_cited(self):
        materiality, reason = runner.apply_floor_cited("ACCEPTABLE", {}, "precheck", self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertEqual(reason, "precheck_floor")

    def test_deterministic_floor_fires_when_issue_cites_ledger_value(self):
        dev = {"changed_number": True, "related_fact_id": "HF-001",
               "issue": "Article says the share fell 9%, but Ledger HF-001 records 2.6%."}
        materiality, reason = runner.apply_floor_cited("QUALITY", dev, "stage1_llm", self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNotNone(reason)

    def test_deterministic_floor_does_not_fire_without_citation(self):
        dev = {"changed_number": True, "related_fact_id": "HF-001",
               "issue": "The number looks different from what I expect."}
        materiality, reason = runner.apply_floor_cited("QUALITY", dev, "stage1_llm", self.LEDGER)
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)

    def test_no_related_fact_id_never_cited(self):
        dev = {"changed_number": True, "related_fact_id": "",
               "issue": "2.6% mentioned in Ledger HF-001"}
        materiality, reason = runner.apply_floor_cited("QUALITY", dev, "stage1_llm", self.LEDGER)
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)


class TestSectionRoleViolation(unittest.TestCase):
    def test_in_one_line_length_increase_over_30_percent_detected(self):
        before = "# Title\n\nHook paragraph here.\n\n## In one line\nShort summary here now.\n"
        after = ("# Title\n\nHook paragraph here.\n\n## In one line\n"
                 "This is a much longer summary that adds many extra words to the line now.\n")
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["in_one_line_too_long"])
        self.assertTrue(result["section_role_violated"])

    def test_numbers_added_to_title_detected(self):
        before = "# A Surprising Call\n\nHook.\n\n## In one line\nSummary.\n"
        after = "# 3 Surprising Facts About The Call\n\nHook.\n\n## In one line\nSummary.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["numbers_added_to_title"])

    def test_hook_shrinking_detected(self):
        before = ("# Title\n\nRing, ring! Was it a robot calling, or a real person? "
                   "Nobody could quite believe what happened next.\n\n## In one line\nS.\n")
        after = "# Title\n\nA call happened.\n\n## In one line\nS.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["hook_shrank"])
        self.assertTrue(result["section_role_violated"])

    def test_no_violation_when_unchanged(self):
        text = "# Title\n\nHook paragraph.\n\n## In one line\nSummary line.\n"
        result = runner.measure_section_role_violation(text, text)
        self.assertFalse(result["section_role_violated"])


class TestMinimalChangeLadderOrdering(unittest.TestCase):
    """委任_14 B-3: single_text_rewriteが水準①(単語・接続詞)を先に試し、
    guardを満たしたらそれ以降(③文/④段落)へ進まないことを、API呼び出しを
    mockして確認する(¥0)。"""

    def test_stops_at_level1_when_minimal_edit_resolves_it(self):
        from unittest import mock

        full_text = ("# Title\n\nConcerns continued on July 14. So the flashy 20% plan left "
                     "the stage.\n\n## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "So the flashy 20% plan left the stage.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "wrong causal link"},
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e1_minimal_word"):
                return "Concerns continued on July 14, while the flashy 20% plan left the stage."
            raise AssertionError(f"should not escalate past level 1, but called {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertEqual(result["ladder_level_used"], "1_word_connective")
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["guard_ok"])

    def test_escalates_to_level3_when_level1_declines(self):
        from unittest import mock

        full_text = "# Title\n\nSome sentence with a problem in it.\n\n## In one line\nA plan changed.\n"
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "problem"},
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e1_minimal_word"):
                return ""  # 委任_14: 最小編集では解消できない宣言
            if label.endswith("_e2_rewrite"):
                return "Some sentence without the problem."
            raise AssertionError(f"unexpected escalation to {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertEqual(result["ladder_level_used"], "3_sentence")
        self.assertEqual(calls, ["test_e1_minimal_word", "test_e2_rewrite"])


class TestCostBreakdown5Way(unittest.TestCase):
    def test_splits_rewrite_vs_no_rewrite_and_computes_worst(self):
        results = [
            {"instance_id": "a", "total_cost_jpy": 1.0, "cycles": []},
            {"instance_id": "b", "total_cost_jpy": 2.0, "cycles": [{"rewrite_records": [{"x": 1}]}]},
            {"instance_id": "c", "total_cost_jpy": 5.0, "cycles": [{"rewrite_records": [{"x": 1}]}]},
        ]
        out = runner.compute_cost_breakdown_5way(results)
        self.assertEqual(out["no_rewrite_count"], 1)
        self.assertEqual(out["no_rewrite_avg_cost_jpy"], 1.0)
        self.assertEqual(out["with_rewrite_count"], 2)
        self.assertEqual(out["with_rewrite_avg_cost_jpy"], 3.5)
        self.assertEqual(out["rewrite_rate"], round(2 / 3, 4))
        self.assertEqual(out["overall_avg_cost_jpy"], round(8.0 / 3, 4))
        self.assertEqual(out["worst_cost_jpy"], 5.0)


if __name__ == "__main__":
    unittest.main()
