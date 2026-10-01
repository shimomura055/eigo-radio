# -*- coding: utf-8 -*-
# ============================================================
# er052_open233_self_recovery_flow_runner_01_test_01.py
# OPEN-233-SELF-RECOVERY-TRIAL-01 (Self-Recovery Flow, Phase 1 ⑥、委任_09)
# ============================================================
# ネットワーク呼び出しなし(¥0)。claim identity/floor適用/文特定/precheck
# floor dedup/測定集計ロジックのread-only regression testのみ。
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_r3dprime_calibration_01 as r3d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er051_open233_checker_trial_variant_01 as trial


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


class TestExtractAllQuotedFragments(unittest.TestCase):
    # 委任_36(§6-18): extract_quoted_fragment(最長1件のみ)の複数版。
    def test_extracts_multiple_fragments_in_order(self):
        text = "“first fragment here” and “second fragment here”"
        frags = runner.extract_all_quoted_fragments(text)
        self.assertEqual(frags, ["first fragment here", "second fragment here"])

    def test_single_fragment_returns_one_item(self):
        text = "“only one fragment present”"
        self.assertEqual(runner.extract_all_quoted_fragments(text), ["only one fragment present"])

    def test_no_fragment_returns_empty_list(self):
        self.assertEqual(runner.extract_all_quoted_fragments("no quotes here"), [])

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(runner.extract_all_quoted_fragments(""), [])

    def test_deduplicates_identical_fragments(self):
        text = "“same phrase” appears twice: “same phrase”"
        self.assertEqual(runner.extract_all_quoted_fragments(text), ["same phrase"])


class TestLocateMultiQuoteSpan(unittest.TestCase):
    # 委任_36(§6-18、rep20 sample2 cycle2根本原因是正): claim_textが2文以上の
    # bracket-quote断片を結合した合成claimの場合の包含スパン特定。
    def test_spans_both_fragments_when_both_present_same_paragraph(self):
        full_text = (
            "Intro sentence. They could not tell if it was AI or a person. "
            "They enjoyed the convenience, but a human was on the other end. "
            "They did not realize it. Outro sentence."
        )
        claim_text = (
            "“They could not tell if it was AI or a person” and "
            "“They did not realize it.”"
        )
        span, method = runner.locate_multi_quote_span(claim_text, full_text)
        self.assertEqual(method, "multi_quote_span")
        self.assertIn("They could not tell if it was AI or a person", span)
        self.assertIn("They did not realize it.", span)

    def test_single_fragment_claim_returns_not_multi_quote(self):
        full_text = "Intro. The only quoted sentence is here. Outro."
        claim_text = "“The only quoted sentence is here.”"
        span, method = runner.locate_multi_quote_span(claim_text, full_text)
        self.assertIsNone(span)
        self.assertEqual(method, "not_multi_quote")

    def test_fragment_not_present_returns_none(self):
        full_text = "Intro. Something completely different. Outro."
        claim_text = "“First fragment missing” and “Second fragment missing”"
        span, method = runner.locate_multi_quote_span(claim_text, full_text)
        self.assertIsNone(span)
        self.assertEqual(method, "fragment_not_present")

    def test_fragments_crossing_paragraph_break_returns_none(self):
        full_text = (
            "First paragraph has the opening fragment here.\n\n"
            "Second paragraph has the closing fragment here."
        )
        claim_text = (
            "“First paragraph has the opening fragment here.” and "
            "“Second paragraph has the closing fragment here.”"
        )
        span, method = runner.locate_multi_quote_span(claim_text, full_text)
        self.assertIsNone(span)
        self.assertEqual(method, "span_crosses_paragraph")

    def test_span_too_long_returns_none(self):
        filler = "x" * 700
        full_text = f"“start fragment” {filler} “end fragment”"
        claim_text = "“start fragment” and “end fragment”"
        span, method = runner.locate_multi_quote_span(claim_text, full_text)
        self.assertIsNone(span)
        self.assertEqual(method, "span_too_long")


class TestLocateTargetMultiQuoteIntegration(unittest.TestCase):
    # 委任_36(§6-18): locate_targetへのlocate_multi_quote_span統合。
    def test_locate_target_prefers_multi_quote_span_over_single_sentence_match(self):
        full_text = (
            "Intro sentence. They could not tell if it was AI or a person. "
            "They enjoyed the convenience, but a human was on the other end. "
            "They did not realize it. Outro sentence."
        )
        claim_text = (
            "“They could not tell if it was AI or a person” and "
            "“They did not realize it.”"
        )
        target, method = runner.locate_target(claim_text, "", full_text)
        self.assertEqual(method, "multi_quote_span")
        self.assertIn("They did not realize it.", target)

    def test_rewrite_hint_quote_still_takes_priority_over_multi_quote_span(self):
        # 第一キー(rewrite_hintのexact substring)は従来通り維持される
        # (multi_quote_spanは第二キーとして追加されただけで優先順位を
        # 崩さない、既存TestLocateTarget.test_uses_rewrite_hint_quote_as_
        # first_keyと同一原則)。
        full_text = "Intro sentence. The exact target phrase appears here. Outro sentence."
        claim_text = "“fragment one unrelated” and “fragment two unrelated”"
        target, method = runner.locate_target(
            claim_text,
            'rewrite: replace "The exact target phrase appears here." per ledger',
            full_text,
        )
        self.assertEqual(target, "The exact target phrase appears here.")
        self.assertEqual(method, "rewrite_hint_quote")

    def test_reproduces_rep20_sample2_cycle2_fix(self):
        # rep20 sample2 cycle2で実測した非収束パターンの再現(委任_36
        # 根本原因): claim_textが'They could not tell...'と'They did not
        # realize it.'という記事中の非隣接2文を結合した合成claimであり、
        # 旧実装ではlocate_best_sentenceが前者1文しか捕捉できなかった。
        en_full_fragment = (
            "People asking Muse to call might think AI was calling. But sometimes, "
            "a human was speaking instead. If no one explained this clearly, users "
            "could not know. They could not tell if it was AI or a person. They "
            "enjoyed AI’s convenience, but a human was on the other end. They did "
            "not realize it. That was happening behind the scenes."
        )
        claim_text = (
            "“They could not tell if it was AI or a person” and "
            "“They did not realize it.”"
        )
        target, method = runner.locate_target(claim_text, "", en_full_fragment)
        self.assertEqual(method, "multi_quote_span")
        self.assertIn("They could not tell if it was AI or a person", target)
        self.assertIn("They did not realize it.", target)
        # 旧実装(locate_best_sentenceのみ)は'did not realize it'を含まない
        # 単一文しか返さなかった(回帰確認)。
        old_target, _ = runner.locate_best_sentence(claim_text, en_full_fragment)
        self.assertNotIn("did not realize it", old_target)


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

    def test_multiple_prior_records_same_fact_id_returns_most_recent(self):
        # 委任_24 A-2(§6-13): 同一fact_idのprior recordが複数cycleにまたがり
        # 複数件蓄積されている場合(各cycleごとに1件追記)、呼び出し側が
        # escalated_to_paragraphで「直近の試行状態」を判定できるよう、
        # 最も新しく追記された(=リスト末尾の)一致レコードを返す
        # (reversed走査、旧来のfirst-match=最も古い挙動からの変更)。
        dev = {"related_fact_id": "HF-009",
               "claim_in_article": "The fee plan left the stage, but the events quickly returned."}
        older = {"identity": "fact:HF-009", "fact_id": "HF-009",
                  "claim_text_norm": runner.normalize_claim_text(
                      "The fee plan left the stage, but the events quickly returned."),
                  "escalated_to_paragraph": False}
        newer = {"identity": "fact:HF-009", "fact_id": "HF-009",
                  "claim_text_norm": runner.normalize_claim_text(
                      "The fee plan left the stage, but the events quickly returned."),
                  "escalated_to_paragraph": True}
        match = runner.find_matching_prior_record(dev, [older, newer])
        self.assertIsNotNone(match)
        self.assertTrue(match["escalated_to_paragraph"])


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
        # 委任_16作業Cの代表ケースTrialで、RUBRIC_R4_HOOK_AWARE(Title/Hook/
        # 場面描写の演出許容原則を追記したrubric)がSafety-critical claim
        # (bgroup_B3)を誤降格させ、最小修正1回でも再現したため(§5 STOP
        # 条件該当)、実配線はRUBRIC_R3_TRIPLE_PRIMEへ復帰した(詳細は
        # run_stage2内のコメント・REPORT§17参照)。RUBRIC_R4_HOOK_AWARE
        # 自体は次回委任向けにコードとして保持する(削除しない)。
        # 委任_30 Part2(design書§0/§9-1)でbody rubricの既定を
        # `BODY_RUBRIC_DEFAULT`(モジュール定数、委任_31 Part1(b)でV5=
        # RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V5へ昇格、
        # `ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT=False`で旧来の
        # RUBRIC_R3_TRIPLE_PRIMEへ復帰可能)経由へ変更したため、run_stage2
        # 内の直接参照は`BODY_RUBRIC_DEFAULT`を確認する(モジュール定数
        # 自体の定義はTestMisconceptionPrincipleDefaultWiringで別途検証)。
        self.assertIn("BODY_RUBRIC_DEFAULT", src)
        self.assertNotIn("s2c.RUBRIC_R4_HOOK_AWARE,", src)
        self.assertNotIn("s2c.RUBRIC_R2,", src)
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_NATURAL_INTERPRETATION"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_PRIME"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_DOUBLE_PRIME"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R3_TRIPLE_PRIME"))
        self.assertTrue(hasattr(s2c, "RUBRIC_R4_HOOK_AWARE"))
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_NATURAL_INTERPRETATION)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_PRIME)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_DOUBLE_PRIME)
        self.assertIn("確認済みのFact同士", s2c.RUBRIC_R3_TRIPLE_PRIME)
        # R4はR3'''本文を丸ごと内包(既存iteration4/5/6較正の再現性維持)。
        self.assertIn(s2c.RUBRIC_R3_TRIPLE_PRIME, s2c.RUBRIC_R4_HOOK_AWARE)
        self.assertIn("Hook-aware原則", s2c.RUBRIC_R4_HOOK_AWARE)
        self.assertIn("section_type", s2c.RUBRIC_R4_HOOK_AWARE)

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


class TestHookParagraphBlockBoundary(unittest.TestCase):
    """委任_31 Part1(b)(design書§4-24): `_hook_paragraph_block`の
    regression test(¥0)。第2段落を無条件に含めず、(a)1文のみ・(b)数字を
    含まない場合のみ含める決定論ヒューリスティックを直接検証する。"""

    def test_neg1_style_closing_line_is_included(self):
        full_text = ("# Title\n\n"
                      "Ring, ring. A call seemed to come from an AI agent.\n\n"
                      "Meta had run a test that caused exactly this surprise.\n\n"
                      "The test used the phone feature of its AI agent, Muse.\n")
        result = runner._hook_paragraph_block(full_text)
        self.assertIn("Meta had run a test that caused exactly this surprise.", result)
        self.assertIn("Ring, ring.", result)
        self.assertNotIn("Muse", result)

    def test_multi_sentence_second_paragraph_is_excluded(self):
        # hormuz_run03_standard実例の構造と同種(複数文の本文段落)。
        full_text = ("# Title\n\nA plan appeared.\n\n"
                     "Trump said the fee would pay for safety. It would cover all cargo. "
                     "But details were missing.\n\n")
        result = runner._hook_paragraph_block(full_text)
        self.assertNotIn("Trump said", result)

    def test_single_sentence_with_digit_is_excluded(self):
        # neg3/bgroup_B3実例の構造と同種(1文でも具体的な数字/日付を含む)。
        full_text = "# Title\n\nA call came in.\n\nOn July 13, the plan appeared with a 20 percent fee.\n\n"
        result = runner._hook_paragraph_block(full_text)
        self.assertNotIn("July 13", result)

    def test_single_paragraph_article_returns_first_paragraph_only(self):
        full_text = "# Title\n\nJust one paragraph here.\n"
        self.assertEqual(runner._hook_paragraph_block(full_text), "Just one paragraph here.")


class TestDetectClaimSectionType(unittest.TestCase):
    # 委任_31 Part1(b)是正(design書§4-24)後の期待値へ更新。段落②
    # ("Meta ran a test...a report says.")は1文・数字なしの短い締め文
    # のため、旧来の"body"から"hook"へ変わる(意図的な仕様変更、新設
    # test_hook_second_paragraph_closing_line_detectedで確認)。genuine
    # bodyを確認するため、複数文・具体的な日付/数字を含む段落③を新設した。
    ARTICLE = (
        "# A Call That Surprised Everyone\n\n"
        "Ring, ring. A call seemed to come from an AI agent, but it was a person all along.\n\n"
        "Meta ran a test with trained contract workers on some calls, a report says.\n\n"
        "The test began on July 14. It used a calling feature inside the assistant, and some "
        "calls were handled by real people instead of AI, a company statement said.\n\n"
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

    def test_hook_second_paragraph_closing_line_detected(self):
        # 委任_31 Part1(b): 1文のみ・数字を含まない第2段落は、Hook導入文の
        # 締め文とみなしhookへ含める(neg1実例の構造と同一)。
        self.assertEqual(runner.detect_claim_section_type(
            "Meta ran a test with trained contract workers on some calls, a report says.",
            self.ARTICLE), "hook")

    def test_in_one_line_detected(self):
        self.assertEqual(runner.detect_claim_section_type(
            "A test used real people on some calls.", self.ARTICLE), "in_one_line")

    def test_body_detected(self):
        # 複数文・具体的日付(July 14)を含む段落③は、締め文の条件(1文・
        # 数字なし)を満たさないため引き続き"body"のまま(Safety回帰なしの
        # 確認、hormuz/meta_run03_standard/bgroup_B3/neg3実測と同種)。
        self.assertEqual(runner.detect_claim_section_type(
            "The test began on July 14. It used a calling feature inside the assistant, and "
            "some calls were handled by real people instead of AI, a company statement said.",
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


class TestJ1MinimalChangeLadderOrdering(unittest.TestCase):
    """委任_16 B-1(§2原因1是正): paired_rewrite(J-1)がsingle_text_rewriteと
    同じ①単語・接続詞(J1_MINIMAL_WORD)を先に試し、guardを満たしたら
    ③1文/④段落へ進まないことを、API呼び出しをmockして確認する(¥0)。"""

    def test_stops_at_level1_when_minimal_edit_resolves_it_both_languages(self):
        from unittest import mock

        en_full = ("# Title\n\nConcerns continued on July 14. So the flashy 20% plan left "
                   "the stage.\n\n## In one line\nA plan changed.\n")
        ja_full = ("# タイトル\n\n懸念は7月14日も続いた。そのため、派手な20%案は表舞台から消えた。"
                   "\n\n## 一言でまとめると\n案が変わった。\n")
        claim_rec = {
            "claim_text": "So the flashy 20% plan left the stage.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            # rewrite_hintへ逐語引用(JA)を含めることで、ja側のlocate_targetを
            # 第一キー(extract_quoted_fragment)経由で決定論的に一致させる
            # (実runのrewrite_hint[Stage2出力]の仕様どおり、テストの安定性のため)。
            "rewrite_hint": '"懸念は7月14日も続いた。そのため、派手な20%案は表舞台から消えた。"',
            "dev": {"issue": "wrong causal link"}, "origin": "ja_source",
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": en_full,
                   "source_article_text": ja_full}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_j1_e1_minimal_word"):
                return ('{"ja_revised": "懸念は7月14日も続いた。一方、派手な20%案は表舞台から消えた。", '
                        '"en_revised": "While the flashy 20% plan left the stage, concerns lingered."}')
            raise AssertionError(f"should not escalate past level 1, but called {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.paired_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, claim_rec)
        self.assertEqual(result["ladder_level_used"], "1_word_connective")
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["guard_ok"])
        self.assertIn("While the flashy 20% plan", result["updated_en_text"])

    def test_escalates_to_level3_when_level1_declines(self):
        from unittest import mock

        en_full = "# Title\n\nSome sentence with a problem in it.\n\n## In one line\nA plan changed.\n"
        ja_full = "# タイトル\n\n問題のある文がある。\n\n## 一言でまとめると\n案が変わった。\n"
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            # test1と同じ理由でja側の対象文を逐語引用で決定論的に固定する。
            "rewrite_hint": '"問題のある文がある。"', "dev": {"issue": "problem"}, "origin": "ja_source",
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": en_full,
                   "source_article_text": ja_full}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_j1_e1_minimal_word"):
                return '{"ja_revised": "", "en_revised": ""}'
            if label.endswith("_j1_paired_rewrite"):
                return ('{"ja_revised": "問題のない文がある。", '
                        '"en_revised": "Some sentence without the problem."}')
            raise AssertionError(f"unexpected escalation to {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.paired_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, claim_rec)
        self.assertEqual(result["ladder_level_used"], "3_sentence")
        self.assertEqual(calls, ["test_j1_e1_minimal_word", "test_j1_paired_rewrite"])


class TestStage2HookAwareSectionTypeWiring(unittest.TestCase):
    """委任_16 B-2(§2原因2是正): Stage2入力にsection_typeが付与され、
    RUBRIC_R4_HOOK_AWAREがTitle/Hook/場面描写の演出許容原則を持つことを
    確認する(¥0、API呼び出しなし)。Meta hook実例のsection_type判定自体は
    決定論(detect_claim_section_type)であり、ここでunittest化する。
    実際にLLMがQUALITY/ACCEPTABLEへ判定するかは代表ケースTrial(委任_16 C)
    で実測する(このunittestの対象外)。"""

    META_HOOK_TEXT = (
        "# When a Robot Voice Answered the Phone\n\n"
        "Ring, ring. A call seemed to come from an AI agent, and the person picking up "
        "the phone had to guess who was really on the line.\n\n"
        "## In one line\nMeta ran a test about AI phone calls.\n"
    )

    def test_meta_hook_claim_classified_as_hook_section(self):
        claim_text = ("Ring, ring. A call seemed to come from an AI agent, and the person "
                       "picking up the phone had to guess who was really on the line.")
        section_type = runner.detect_claim_section_type(claim_text, self.META_HOOK_TEXT)
        self.assertEqual(section_type, "hook")

    def test_run_stage2_passes_section_type_into_batch_prompt(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        claims = [{"claim_text": "x", "local_context": "y", "origin": None,
                   "related_fact_id": None, "section_type": "hook"}]
        blocks = []
        for i, c in enumerate(claims):
            blocks.append(
                f"[claim_index={i}]\nclaim: {c['claim_text']}\n"
                f"ローカル文脈(段落±1): {c['local_context']}\n"
                f"origin: {c.get('origin') or '(不明)'}\n"
                f"related_fact_id: {c.get('related_fact_id') or '(不明)'}\n"
                f"section_type(title/hook/in_one_line/body): {c.get('section_type') or 'body'}"
            )
        self.assertIn("section_type(title/hook/in_one_line/body): hook", "\n\n".join(blocks))
        # run_stage2自体もsection_typeをclaim_recordsへ付与する(post-hoc
        # downgrade[§6-4]・測定[§8-7]用に保持、ただしLLMプロンプトへは渡さない
        # ことを代表ケースTrialの是正として確認する、REPORT§17参照)。
        import inspect
        src = inspect.getsource(runner.run_stage2)
        self.assertIn('"section_type": section_type', src)
        self.assertIn("claim_records_for_stage2", src)
        self.assertIn('if k != "section_type"', src)
        # 委任_30 Part2(design書§0/§9-1): body rubric既定が`BODY_RUBRIC_
        # DEFAULT`経由へ変更されたため(TestRubricR3Wiring参照)、ここでは
        # 文字列自体ではなくその参照を確認する。
        self.assertIn("BODY_RUBRIC_DEFAULT", src)
        self.assertIn("Hook-aware原則", s2c.RUBRIC_R4_HOOK_AWARE)

    def test_rubric_r4_does_not_exempt_body_or_in_one_line_section_from_normal_rules(self):
        # 委任_16代表ケースTrial実測是正: 当初案(title/hook/in_one_line)は
        # Safety-critical claim(bgroup_B3、In one line欄)を誤降格させたため、
        # 適用対象をtitle/hookの2種のみへ限定した(in_one_line/bodyは対象外)。
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertIn("in_one_lineまたはbodyの場合は本項目を適用せず", s2c.RUBRIC_R4_HOOK_AWARE)
        self.assertIn("section_typeがtitle/hookであることを理由に", s2c.RUBRIC_R4_HOOK_AWARE)


class TestInOneLineTooLongDetection(unittest.TestCase):
    """委任_16 B-4: In one line長文化検出(§5-7/§8-7)のunittest(既存
    hook_shrinking/numbers_added_to_titleと並ぶ、+30%超の検出のみを
    直接対象とする追加ケース)。"""

    def test_in_one_line_length_increase_over_30_percent_detected(self):
        before = "# Title\n\nHook.\n\n## In one line\nA short plan changed today.\n"
        after = ("# Title\n\nHook.\n\n## In one line\nA short plan changed today after a long "
                 "series of unexpected concerns and additional background details were added.\n")
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["in_one_line_too_long"])
        self.assertTrue(result["section_role_violated"])

    def test_in_one_line_small_increase_not_flagged(self):
        before = "# Title\n\nHook.\n\n## In one line\nA short plan changed today.\n"
        after = "# Title\n\nHook.\n\n## In one line\nA short plan changed today, mostly.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertFalse(result["in_one_line_too_long"])


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


class TestHookOnlyStage2Separation(unittest.TestCase):
    """委任_17 A-4: Hook専用Stage2(title/hookに位置するclaimのみ別Prompt・
    別callで判定し、body/in_one_lineは既存Stage2[R3''']のまま)のルーティング
    ・fail-closed floor維持・prompt priming遮断をunittest化する(¥0、
    client.responses.createは呼ばず、s2c.run_stage2_batch_variant/
    s2h.run_stage2_hook_batchをmonkeypatchする。record_callも
    budget_state.jsonへの実書き込みを避けるためno-opへ差し替える)。"""

    NEG1_HOOK_TEXT = (
        "# When a Robot Voice Answered the Phone\n\n"
        "Ring, ring. A call seemed to come from an AI agent, and the person picking up "
        "the phone had to guess who was really on the line.\n\n"
        "## In one line\nMeta ran a test about AI phone calls.\n"
    )
    B3_BODY_TEXT = (
        "# Oil Prices Recover\n\n"
        "Traders watched the region closely as the week began.\n\n"
        "## In one line\n"
        "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on "
        "July 14, so the flashy 20% plan left the stage.\n"
    )

    @staticmethod
    def _base_state():
        return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}

    def test_neg1_hook_claim_routes_to_hook_stage2_and_quality_passes_without_rewrite(self):
        claim_text = ("Ring, ring. A call seemed to come from an AI agent, and the person "
                       "picking up the phone had to guess who was really on the line.")
        fixture = {"article_text": self.NEG1_HOOK_TEXT, "ledger_text": "(ledger)",
                   "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": None,
                   "dev": {}, "detected_by": "stage1_llm"}]

        def fake_hook_batch(client, ledger, source, title_hook_text, cl, model=None, **kwargs):
            self.assertEqual(len(cl), 1)
            self.assertIn("When a Robot Voice Answered the Phone", title_hook_text)
            return {"prompt_sha256": "h", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "QUALITY", "basis": "none",
                 "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "gpt-6-luna", "response_id": "r1", "usage": {},
                    "cost_jpy": 0.01, "elapsed_seconds": 0.01}

        mock_body_fn = mock.MagicMock()
        state = self._base_state()
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2h, "run_stage2_hook_batch", fake_hook_batch), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", mock_body_fn):
            out = runner.run_stage2(None, state, [0], call_log, "neg1_test", fixture, claims)

        mock_body_fn.assert_not_called()
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["section_type"], "hook")
        self.assertEqual(out[0]["stage2_route"], "hook")
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertIsNone(out[0]["floor_reason"])

    def test_b3_causal_claim_routes_to_body_stage2_not_hook_and_stays_blocking(self):
        claim_text = ("Concerns about US-Iran attacks, the sea blockade, and tanker safety "
                       "continued on July 14, so the flashy 20% plan left the stage.")
        fixture = {"article_text": self.B3_BODY_TEXT, "ledger_text": "(ledger)",
                   "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "ja_source", "related_fact_id": "HF-007",
                   "dev": {}, "detected_by": "stage1_llm"}]

        # bgroup_B3実例と同じく、In one line欄に集約されたclaimはsection_type
        # ="in_one_line"に分類される(委任_16でこの分類がHook-aware原則の
        # 誤降格を招いた対象そのもの)ことを先に確認する。
        section_type = runner.detect_claim_section_type(claim_text, self.B3_BODY_TEXT)
        self.assertEqual(section_type, "in_one_line")

        def fake_body_batch(client, ledger, source, cl, rubric_text, model=None, **kwargs):
            # 委任_30 Part2(design書§0/§9-1)でbody rubricの既定を
            # `RUBRIC_R3_TRIPLE_PRIME`からV4(重大誤解原則配線)へ昇格した
            # ため、ここではrubric_textが`runner.BODY_RUBRIC_DEFAULT`
            # (既定True時はV4、Falseなら従来のRUBRIC_R3_TRIPLE_PRIME)と
            # 一致することを確認する(本テストの目的=hook/body routingの
            # regressionであり、rubric本文自体の選択はTestMisconception
            # PrincipleDefaultWiringで別途検証する)。
            self.assertIs(rubric_text, runner.BODY_RUBRIC_DEFAULT)
            return {"prompt_sha256": "b", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "BLOCKING", "basis": "notes_for_writer",
                 "rewrite_kind": "delete", "rewrite_hint": "delete the causal clause"}]},
                    "model": "gpt-6-luna", "response_id": "r2", "usage": {},
                    "cost_jpy": 0.02, "elapsed_seconds": 0.02}

        mock_hook_fn = mock.MagicMock()
        state = self._base_state()
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake_body_batch), \
             mock.patch.object(runner.s2h, "run_stage2_hook_batch", mock_hook_fn):
            out = runner.run_stage2(None, state, [0], call_log, "b3_test", fixture, claims)

        mock_hook_fn.assert_not_called()
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["section_type"], "in_one_line")
        self.assertEqual(out[0]["stage2_route"], "body")
        self.assertEqual(out[0]["materiality"], "BLOCKING")

    def test_safety_changed_actor_floor_blocks_even_if_hook_stage2_says_quality(self):
        # deterministic floor/pre-checkはHook専用Stage2でも維持される
        # (委任文§3「Safety 12は改竄fixtureなのでfloorで止まる」)ことを
        # Hook専用Stage2がQUALITYと誤って判定した場合でも確認する。
        claim_text = "The company said its rival built the device."
        article_text = f"# T\n\n{claim_text}\n\n## In one line\nSummary.\n"
        fixture = {"article_text": article_text, "ledger_text": "(ledger)",
                   "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": "HF-001",
                   "dev": {"changed_actor": True}, "detected_by": "stage1_llm"}]

        def fake_hook_batch(client, ledger, source, title_hook_text, cl, model=None, **kwargs):
            return {"prompt_sha256": "h2", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "QUALITY", "basis": "none",
                 "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "gpt-6-luna", "response_id": "r3", "usage": {},
                    "cost_jpy": 0.01, "elapsed_seconds": 0.01}

        state = self._base_state()
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2h, "run_stage2_hook_batch", fake_hook_batch):
            out = runner.run_stage2(None, state, [0], call_log, "safety_test", fixture, claims)

        self.assertEqual(out[0]["stage2_route"], "hook")
        self.assertEqual(out[0]["llm_materiality"], "QUALITY")
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        self.assertTrue(out[0]["floor_reason"].startswith("deterministic_floor"))

    def test_hook_claim_with_invented_specifics_stays_blocking_when_hook_stage2_says_blocking(self):
        claim_text = "A secret new AI feature was launched by the company that week."
        article_text = f"# T\n\n{claim_text}\n\n## In one line\nSummary.\n"
        fixture = {"article_text": article_text, "ledger_text": "(ledger)",
                   "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": None,
                   "dev": {}, "detected_by": "stage1_llm"}]

        def fake_hook_batch(client, ledger, source, title_hook_text, cl, model=None, **kwargs):
            return {"prompt_sha256": "h3", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "BLOCKING", "basis": "unsupported_relationship",
                 "rewrite_kind": "delete", "rewrite_hint": "delete the invented feature claim"}]},
                    "model": "gpt-6-luna", "response_id": "r4", "usage": {},
                    "cost_jpy": 0.01, "elapsed_seconds": 0.01}

        state = self._base_state()
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2h, "run_stage2_hook_batch", fake_hook_batch):
            out = runner.run_stage2(None, state, [0], call_log, "hook_blocking_test", fixture, claims)

        self.assertEqual(out[0]["stage2_route"], "hook")
        self.assertEqual(out[0]["materiality"], "BLOCKING")


# ============================================================
# 委任_18(OPEN-233-SELF-RECOVERY-TRIAL-01委任_18)regression test。
# 2-1(precheck合成マーカー是正・target_not_locatable・degenerate guard)、
# 2-2(disclosure-gap downgrade)、2-3(b)(同一fact_id別箇所cycle緩和)、
# 2-4(局所QA fastpath条件判定)を対象とする(¥0、API呼び出しなし)。
# ============================================================
class TestResolvePrecheckTargetSentence(unittest.TestCase):
    """委任_18 2-1(a): precheckの合成マーカー(article_evidence)ではなく
    記事本文中の実文へclaim_textを解決できることを確認する。"""

    def test_number_mismatch_resolves_to_real_sentence_not_synthetic_marker(self):
        article = ("# Card Study\n\nResearchers studied more than 30 million credit card "
                    "payments last year.\n\nThey found a clear pattern.\n")
        finding = {"kind": "number_mismatch", "field": "F-002",
                    "article_evidence": "count values found in article not matching any ledger fact: [30000000.0]",
                    "foreign_values": [30000000.0]}
        sentence, method = runner.resolve_precheck_target_sentence(article, finding)
        self.assertIsNotNone(sentence)
        self.assertIn("30 million", sentence)
        self.assertEqual(method, "precheck_number_locate")
        # 合成マーカーそのものは記事本文に存在しないことの確認(前提の検証)。
        self.assertNotIn(finding["article_evidence"], article)

    def test_number_mismatch_not_locatable_when_value_not_in_any_sentence(self):
        article = "# T\n\nNothing numeric here at all.\n"
        finding = {"kind": "number_mismatch", "field": "F-002",
                    "article_evidence": "count values found in article not matching any ledger fact: [30000000.0]",
                    "foreign_values": [30000000.0]}
        sentence, method = runner.resolve_precheck_target_sentence(article, finding)
        self.assertIsNone(sentence)
        self.assertEqual(method, "not_locatable")

    def test_actor_missing_resolves_via_candidate_list(self):
        article = "# T\n\nSmithCo announced the rival device last week.\n"
        finding = {"kind": "actor_missing", "field": "F-001",
                    "article_evidence": ["SmithCo"]}
        sentence, method = runner.resolve_precheck_target_sentence(article, finding)
        self.assertIsNotNone(sentence)
        self.assertIn("SmithCo", sentence)
        self.assertEqual(method, "precheck_actor_locate")


class TestBuildPrecheckFloorClaimsLocatability(unittest.TestCase):
    def test_locatable_finding_uses_real_sentence_as_claim_text(self):
        article = "# T\n\nResearchers studied more than 30 million payments last year.\n"
        ledger = "[VERIFIED] fact_id: F-002 | claim: a study of card payments | numeric_value: 13 million"
        fixture = {"article_text": article, "ledger_text": ledger}
        with mock.patch.object(runner.precheck, "run_precheck", return_value=[{
                "field": "F-002", "kind": "number_mismatch", "ledger_value": "13 million",
                "article_evidence": "count values found in article not matching any ledger fact: [30000000.0]",
                "foreign_values": [30000000.0], "detected_by": "precheck"}]):
            claims = runner.build_precheck_floor_claims(fixture, set())
        self.assertEqual(len(claims), 1)
        self.assertTrue(claims[0]["precheck_target_locatable"])
        self.assertIn("30 million", claims[0]["claim_text"])
        self.assertNotIn("count values found in article", claims[0]["claim_text"])

    def test_unlocatable_finding_flags_precheck_target_locatable_false(self):
        article = "# T\n\nNothing numeric here.\n"
        fixture = {"article_text": article, "ledger_text": "(ledger)"}
        with mock.patch.object(runner.precheck, "run_precheck", return_value=[{
                "field": "F-002", "kind": "number_mismatch", "ledger_value": "13 million",
                "article_evidence": "count values found in article not matching any ledger fact: [30000000.0]",
                "foreign_values": [30000000.0], "detected_by": "precheck"}]):
            claims = runner.build_precheck_floor_claims(fixture, set())
        self.assertEqual(len(claims), 1)
        self.assertFalse(claims[0]["precheck_target_locatable"])


class TestTargetNotLocatableEarlyReturn(unittest.TestCase):
    """委任_18 2-1(b)(d): found=Falseの場合、⑥全体フォールバック(API call)
    を試みずtarget_not_locatable=Trueで即returnすることを確認する
    (client=Noneでも例外が起きなければAPI callが発生していない証拠)。"""

    def test_single_text_rewrite_returns_target_not_locatable_without_api_call(self):
        fixture = {"article_text": "# T\n\nSomething unrelated entirely.\n", "ledger_text": "(ledger)"}
        claim_rec = {"claim_text": "This exact sentence is nowhere in the article body text at all.",
                     "rewrite_kind": "replace_with_ledger_value", "materiality": "BLOCKING",
                     "basis": "x", "dev": {}, "rewrite_hint": ""}
        call_log = []
        res = runner.single_text_rewrite(None, None, [0], call_log, "lbl", fixture, "article_text", claim_rec)
        self.assertTrue(res["target_not_locatable"])
        self.assertFalse(res["guard_ok"])
        self.assertEqual(call_log, [])
        self.assertEqual(res["updated_text"], fixture["article_text"])

    def test_paired_rewrite_returns_target_not_locatable_when_both_sides_unlocatable(self):
        fixture = {"article_text": "# T\n\nSomething unrelated entirely.\n",
                    "source_article_text": "# T\n\n全く関係のない文章です。\n", "ledger_text": "(ledger)"}
        claim_rec = {"claim_text": "This exact sentence is nowhere in either article body text at all.",
                     "rewrite_kind": "replace_with_ledger_value", "materiality": "BLOCKING",
                     "basis": "x", "dev": {}, "rewrite_hint": ""}
        call_log = []
        res = runner.paired_rewrite(None, None, [0], call_log, "lbl", fixture, claim_rec)
        self.assertTrue(res["target_not_locatable"])
        self.assertFalse(res["guard_ok"])
        self.assertEqual(call_log, [])

    def test_paired_rewrite_partial_locate_delegates_to_single_text_rewrite(self):
        # 委任_30 Part3 FAIL是正(neg3_hormuz_prodrunner_b1b根本原因の
        # regression test、¥0): claim_text自体がJA文(origin=ja_source由来の
        # 実データで実際に観測された形、§27-5開示doc参照)で、JA側には
        # 存在する(exact_substring)がEN側には存在しない(EN側は既に別
        # cycleで解決済み等)場合、従来は0 callでladder6-disabled(method=
        # "+ladder6_disabled")へ落ちていた(EN側に対応する位置推定
        # fallbackが存在しないため、ja_located=True/en_located=Falseの
        # 非対称ケースはJA→EN双方向の既存fallback網でも救済されない)。
        # 本委任の是正後は、特定できたJA側のみ既存single_text_rewrite
        # (①〜④の非⑥ローカル編集)へ委譲し、EN側は変更せずguard_ok=Trueで
        # 解決することを確認する。
        from unittest import mock

        en_full = "# T\n\nSomething entirely different in English.\n\n## In one line\nSummary.\n"
        ja_full = "# タイトル\n\nこの主張文はJA本文にのみ存在します。\n\n## 一言でまとめると\nまとめ。\n"
        claim_rec = {
            "claim_text": "この主張文はJA本文にのみ存在します。",
            "rewrite_kind": "replace_with_ledger_value", "materiality": "BLOCKING", "basis": "ledger_fact",
            "rewrite_hint": "", "dev": {"issue": "stale duplicate"}, "origin": "ja_source",
        }
        fixture = {"ledger_text": "[VERIFIED] HF-999: ...", "article_text": en_full,
                   "source_article_text": ja_full}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            return "この主張文は修正されました。"

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.paired_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, claim_rec)
        self.assertTrue(result["guard_ok"])
        self.assertFalse(result["target_not_locatable"])
        self.assertTrue(result["method"].startswith("j1_single_side_ja("))
        self.assertIn("この主張文は修正されました。", result["updated_ja_text"])
        self.assertEqual(result["updated_en_text"], en_full, "EN側は未特定のため変更しないこと")
        self.assertTrue(len(calls) >= 1)

    def test_paired_rewrite_partial_locate_falls_through_to_stage4_when_single_side_also_fails(self):
        # 単体側への委譲自体が失敗(API失敗等)した場合は、従来どおり⑥を
        # 試みずmethodに"+ladder6_disabled"を含めてguard_ok=Falseを返す
        # こと(新設elif分岐が無限ループ・例外を起こさないこと)を確認する。
        from unittest import mock

        en_full = "# T\n\nSomething entirely different in English.\n\n## In one line\nSummary.\n"
        ja_full = "# タイトル\n\nこの主張文はJA本文にのみ存在します。\n\n## 一言でまとめると\nまとめ。\n"
        claim_rec = {
            "claim_text": "この主張文はJA本文にのみ存在します。",
            "rewrite_kind": "replace_with_ledger_value", "materiality": "BLOCKING", "basis": "ledger_fact",
            "rewrite_hint": "", "dev": {"issue": "stale duplicate"}, "origin": "ja_source",
        }
        fixture = {"ledger_text": "[VERIFIED] HF-999: ...", "article_text": en_full,
                   "source_article_text": ja_full}

        def fake_llm_declines(client, state, errs, log, label, dev_msg, prompt, model=None):
            return None  # API失敗を模す(全levelでapi_failureとなりguard_okが一度もTrueにならない)

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm_declines):
            result = runner.paired_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, claim_rec)
        self.assertFalse(result["guard_ok"])
        self.assertEqual(result["updated_en_text"], en_full)
        self.assertEqual(result["updated_ja_text"], ja_full)


class TestDegenerateRewriteGuard(unittest.TestCase):
    """委任_18 2-1(c)(disclosure §1-1-4是正): タイトル/hookの空文字・
    極端短縮(語数<3)を検出できることを確認する。"""

    def test_title_emptied_is_degenerate(self):
        before = "# The Same New York City Taxi Researchers Also Found Something\n\nHook para.\n"
        after = "# \n\nHook para.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["title_degenerate"])
        self.assertTrue(result["section_role_violated"])

    def test_title_shrunk_below_3_words_is_degenerate(self):
        before = "# The Same New York City Taxi Researchers Also Found Something\n\nHook para.\n"
        after = "# Taxi Study\n\nHook para.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["title_degenerate"])

    def test_title_unchanged_short_title_is_not_flagged(self):
        text = "# Taxi Study\n\nHook para.\n"
        result = runner.measure_section_role_violation(text, text)
        self.assertFalse(result["title_degenerate"])
        self.assertFalse(result["section_role_violated"])

    def test_hook_emptied_is_degenerate(self):
        before = "# T\n\nA long hook paragraph describing the scene in detail here.\n"
        after = "# T\n\n\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["hook_degenerate"])

    def test_title_changed_but_still_healthy_is_not_degenerate(self):
        before = "# The Old Title Here Now\n\nHook para.\n"
        after = "# A New But Still Healthy Title\n\nHook para.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertFalse(result["title_degenerate"])


class TestDegenerateRewriteHardBlockWiring(unittest.TestCase):
    """degenerate guardがrun_instanceのcycleループで無条件STAGE4へ
    配線されていることをソース検査で確認する(¥0)。"""

    def test_run_instance_source_contains_degenerate_hard_block(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("degenerate_rewrite_output", src)
        self.assertIn('final_section_role.get("title_degenerate")', src)
        self.assertIn('final_section_role.get("hook_degenerate")', src)

    def test_run_instance_source_contains_target_not_locatable_escalation(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('stage4_reason = "target_not_locatable"', src)
        self.assertIn("unlocatable_records", src)

    def test_run_instance_source_contains_same_fact_id_new_location_extension(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("same_fact_id_new_location", src)
        self.assertIn("current_fact_ids & prior_fact_ids", src)


class TestApplyDisclosureGapDowngrade(unittest.TestCase):
    """委任_18 2-2: MUSE-HC-012パターン(開示不備→気づけなかった、否定形の
    論理的帰結)のみを対象とした決定論downgradeを確認する。"""

    LEDGER = ("[VERIFIED] MUSE-HC-012: The AI test began without a clear disclosure to callers.\n"
              "  related_actors: Meta\n")

    def test_negative_disclosure_gap_inference_downgrades_to_quality(self):
        claim = "They enjoyed the ease of AI. But they did not know that a human was on the other end."
        dev = {"unsupported_new_claim": True, "changed_certainty": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "QUALITY")
        self.assertEqual(reason, "disclosure_gap_negative_inference_downgrade(委任_18 2-2)")

    def test_affirmative_claim_not_downgraded_direction_guard(self):
        # neg1型(肯定形の主観断定、"驚いた"/"realized"相当)は対象外(§1-2-5)。
        claim = "The caller was surprised to realize a human was on the other end."
        dev = {"unsupported_new_claim": True, "changed_certainty": True, "changed_fact": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_floor_already_triggered_is_not_touched(self):
        claim = "They did not know that a human was on the other end."
        dev = {"unsupported_new_claim": True, "changed_number": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, "deterministic_floor:changed_number", claim, self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_disqualifying_flag_present_blocks_downgrade(self):
        claim = "They did not know that a human was on the other end."
        dev = {"unsupported_new_claim": True, "changed_number": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_new_proper_noun_introduced_blocks_downgrade(self):
        claim = "They did not know that Jonathan Carter was on the other end."
        dev = {"unsupported_new_claim": True, "changed_certainty": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_non_blocking_input_passthrough(self):
        claim = "They did not know that a human was on the other end."
        dev = {"unsupported_new_claim": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "QUALITY", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "QUALITY")
        self.assertIsNone(reason)

    def test_safety_critical_style_claim_with_changed_number_never_downgrades(self):
        """Safety-critical claim(数値改竄+否定形が偶然含まれていても)は
        floorが対象外に含まれるためdowngradeされないことを確認する
        (mock、Safety-critical 10 claim・Safety 12のfloor不変を保証)。"""
        claim = "Researchers did not know that more than 30 million payments were studied."
        dev = {"unsupported_new_claim": True, "changed_number": True}
        materiality, reason = runner.apply_disclosure_gap_downgrade(
            "BLOCKING", dev, None, claim, self.LEDGER)
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)


class TestApplyDisclosureGapDowngradeWiredIntoStage2(unittest.TestCase):
    """run_stage2内でhook downgradeの直後にdisclosure-gap downgradeが
    呼ばれることをmock経由で確認する(body経路、floor不発火時のみ)。"""

    @staticmethod
    def _base_state():
        return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}

    def test_body_claim_muse_hc012_pattern_downgrades_via_run_stage2(self):
        claim_text = "They enjoyed the ease of AI. But they did not know that a human was on the other end."
        article_text = f"# T\n\nIntro hook.\n\n{claim_text}\n\n## In one line\nSummary.\n"
        ledger = TestApplyDisclosureGapDowngrade.LEDGER
        fixture = {"article_text": article_text, "ledger_text": ledger, "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": "MUSE-HC-012",
                   "dev": {"unsupported_new_claim": True, "changed_certainty": True},
                   "detected_by": "stage1_llm"}]

        def fake_body_batch(client, ledger_text, source, cl, rubric_text, model=None):
            return {"prompt_sha256": "d1", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "BLOCKING", "basis": "unsupported_relationship",
                 "rewrite_kind": "delete", "rewrite_hint": "x"}]},
                    "model": "gpt-6-luna", "response_id": "rd1", "usage": {},
                    "cost_jpy": 0.01, "elapsed_seconds": 0.01}

        state = self._base_state()
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake_body_batch):
            out = runner.run_stage2(None, state, [0], call_log, "disclosure_test", fixture, claims)

        self.assertEqual(out[0]["stage2_route"], "body")
        self.assertEqual(out[0]["llm_materiality"], "BLOCKING")
        self.assertEqual(out[0]["materiality"], "QUALITY")
        self.assertEqual(out[0]["floor_reason"], "disclosure_gap_negative_inference_downgrade(委任_18 2-2)")


class TestFullRecheckRequired(unittest.TestCase):
    """委任_18 2-4/委任_20 W3: 全文Recheckを残す条件(a)〜(h)の判定を確認
    する。委任_20 W3で(c)を「paired かつ(ladder≥④ or JAガード不通過)」へ
    縮小し、(g)(h)を新設した(Opus L2レビュー#4 Q1(b)推奨、前提: W1で
    JA fail-openガード/equivalence gatingを導入済み)。"""

    def test_no_escalation_condition_returns_false(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "neg2_meta_refresh_a2")
        self.assertFalse(required)
        self.assertEqual(reasons, [])

    def test_paragraph_level_requires_full_recheck(self):
        rewrite_records = [{"ladder_level_used": "4_paragraph", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "bgroup_B3")
        self.assertTrue(required)
        self.assertIn("paragraph_or_full_or_delete_rewrite", reasons)

    def test_multiple_claims_same_cycle_requires_full_recheck(self):
        rewrite_records = [
            {"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"},
            {"ladder_level_used": "3_sentence", "mechanism": "single_text_local(E-2)"},
        ]
        blocking_claims = [{"floor_reason": None}, {"floor_reason": None}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "bgroup_B4")
        self.assertTrue(required)
        self.assertIn("multiple_claims_rewritten_same_cycle", reasons)

    def test_paired_j1_high_ladder_requires_full_recheck(self):
        # 委任_20 W3: paired かつ ladder≥④(段落水準)は(a)からも捕捉される
        # ため、(c)理由も併記されfull recheckが要求される。
        rewrite_records = [{"ladder_level_used": "4_paragraph", "mechanism": "paired_ja_en(J-1)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "meta_run03_standard")
        self.assertTrue(required)
        self.assertIn("both_ja_en_changed(paired_j1)", reasons)
        self.assertIn("paragraph_or_full_or_delete_rewrite", reasons)

    def test_paired_j1_low_ladder_with_ja_guard_violation_requires_full_recheck(self):
        # 委任_20 W3: paired・ladder①(低水準)でも、JA fail-openガードが
        # 不通過(ja_guard_ok=False)ならfull recheckを維持する。
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "paired_ja_en(J-1)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "meta_run03_standard", ja_guard_ok=False)
        self.assertTrue(required)
        self.assertIn("both_ja_en_changed(paired_j1)", reasons)

    def test_paired_j1_low_ladder_with_ja_guard_ok_does_not_force_full_recheck(self):
        # 委任_20 W3(narrowing本体): paired・ladder①(低水準)・JAガード通過
        # (ja_guard_ok=True)なら、(c)単独では全文Recheckを要さない(他の
        # 条件[(a)〜(h)]に該当しない前提)。
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "paired_ja_en(J-1)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "meta_run03_standard", ja_guard_ok=True)
        self.assertFalse(required)
        self.assertEqual(reasons, [])

    def test_paired_j1_low_ladder_with_ja_guard_unknown_does_not_force_full_recheck(self):
        # ja_guard_ok=None(このcycleでJAガードを計算していない、例えば
        # 非paired文脈やJA本文自体が存在しない場合)は違反扱いにしない
        # (fail-openへ倒さない側だが、明示的な違反シグナルが無い限り
        # narrowingの効果を持たせる、既定値)。
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "paired_ja_en(J-1)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "meta_run03_standard")
        self.assertFalse(required)

    def test_short_section_claim_requires_full_recheck(self):
        # 委任_20 W3新設(g): title/hook/in_one_lineは局所QAのwindow概念が
        # 成立しないため全文Recheckを維持する。
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None, "section_type": "in_one_line"}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "neg3_hormuz_prodrunner_b1b")
        self.assertTrue(required)
        self.assertIn("short_section_no_window(title_hook_in_one_line)", reasons)

    def test_body_section_claim_does_not_trigger_short_section_condition(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None, "section_type": "body"}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "neg2_meta_refresh_a2")
        self.assertFalse(required)

    def test_ja_en_equivalence_non_pass_requires_full_recheck(self):
        # 委任_20 W3新設(h): ja_en_equivalence_verdictがPASS以外(FAIL/
        # REVIEW_REQUIRED)の場合、全文Recheckを維持する。
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "neg2_meta_refresh_a2", ja_equivalence_verdict="FAIL")
        self.assertTrue(required)
        self.assertIn("ja_en_equivalence_not_pass", reasons)

    def test_ja_en_equivalence_pass_does_not_trigger_condition_h(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "neg2_meta_refresh_a2", ja_equivalence_verdict="PASS")
        self.assertFalse(required)

    def test_deterministic_floor_claim_requires_full_recheck(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": "deterministic_floor:changed_number"}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "b_group_test")
        self.assertTrue(required)
        self.assertIn("deterministic_floor_claim", reasons)

    def test_safety_fixture_always_requires_full_recheck(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "safety_er009_changed_actor")
        self.assertTrue(required)
        self.assertIn("safety_fixture", reasons)


class TestFindSentenceContext(unittest.TestCase):
    def test_locates_before_and_after_context(self):
        text = "First sentence here. Second sentence here. Third sentence here."
        before, target, after = runner.find_sentence_context(text, "Second sentence here.")
        self.assertEqual(target, "Second sentence here.")
        self.assertEqual(before, "First sentence here.")
        self.assertEqual(after, "Third sentence here.")

    def test_returns_none_when_not_found(self):
        text = "First sentence here. Second sentence here."
        before, target, after = runner.find_sentence_context(text, "Not present anywhere.")
        self.assertIsNone(target)
        self.assertIsNone(before)
        self.assertIsNone(after)

    def test_empty_needle_returns_none(self):
        before, target, after = runner.find_sentence_context("Some text.", "")
        self.assertIsNone(target)


class TestLocalQaFastpathWiring(unittest.TestCase):
    """局所QA fastpathがrun_instanceのcycleループへ配線され、全文Recheckが
    局所QA成功時にスキップされる(run_recheckが呼ばれない)ことをソース検査
    +mockベースの動作確認で行う(¥0)。"""

    def test_run_instance_source_contains_local_qa_fastpath_wiring(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("run_local_qa_fastpath", src)
        self.assertIn("full_recheck_required(", src)
        self.assertIn('local_qa_outcome["success"]', src)

    def test_run_local_qa_fastpath_success_when_all_claims_resolved(self):
        fixture = {"ledger_text": "[VERIFIED] fact_id: F-1 | claim: x", "article_text": "irrelevant"}
        current_en_text = "Before ctx. The revised sentence is here. After ctx."
        blocking_claims = [{"dev": {"related_fact_id": "F-1", "issue": "issue text"},
                             "claim_text": "orig"}]
        before_after_pairs = [{"before": "orig sentence", "after": "The revised sentence is here."}]
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "run_local_qa", return_value={
                 "prior_issue_resolved": True, "new_deviation_in_revised_sentence": False,
                 "adjacent_sentence_affected": False, "_api_failure": False}):
            outcome = runner.run_local_qa_fastpath(
                None, None, [0], call_log, "lbl", fixture, current_en_text, blocking_claims, before_after_pairs)
        self.assertTrue(outcome["success"])

    def test_run_local_qa_fastpath_fails_when_new_deviation_detected(self):
        fixture = {"ledger_text": "[VERIFIED] fact_id: F-1 | claim: x", "article_text": "irrelevant"}
        current_en_text = "Before ctx. The revised sentence is here. After ctx."
        blocking_claims = [{"dev": {"related_fact_id": "F-1", "issue": "issue text"},
                             "claim_text": "orig"}]
        before_after_pairs = [{"before": "orig sentence", "after": "The revised sentence is here."}]
        call_log = []
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "run_local_qa", return_value={
                 "prior_issue_resolved": True, "new_deviation_in_revised_sentence": True,
                 "adjacent_sentence_affected": False, "_api_failure": False}):
            outcome = runner.run_local_qa_fastpath(
                None, None, [0], call_log, "lbl", fixture, current_en_text, blocking_claims, before_after_pairs)
        self.assertFalse(outcome["success"])

    def test_run_local_qa_fastpath_skips_when_after_fragment_unknown(self):
        fixture = {"ledger_text": "(ledger)", "article_text": "irrelevant"}
        blocking_claims = [{"dev": {"related_fact_id": "F-1", "issue": "issue"}, "claim_text": "orig"}]
        before_after_pairs = [{"before": "orig", "after": None}]
        call_log = []
        outcome = runner.run_local_qa_fastpath(
            None, None, [0], call_log, "lbl", fixture, "text", blocking_claims, before_after_pairs)
        self.assertFalse(outcome["success"])
        self.assertEqual(outcome["results"][0]["skipped_reason"], "after_fragment_unknown")
        self.assertEqual(call_log, [])


class TestBuildLedgerExcerpt(unittest.TestCase):
    def test_extracts_only_matching_fact(self):
        ledger = ("[VERIFIED] F-1: alpha claim.\n  numeric_value: 10%\n\n"
                  "[VERIFIED] F-2: beta claim.\n  numeric_value: 20%\n")
        excerpt = runner.build_ledger_excerpt(ledger, "F-1")
        self.assertIn("F-1", excerpt)
        self.assertIn("alpha claim", excerpt)
        self.assertNotIn("beta claim", excerpt)

    def test_missing_fact_id_falls_back_to_full_ledger(self):
        ledger = "[VERIFIED] F-1: alpha claim.\n  numeric_value: 10%\n"
        excerpt = runner.build_ledger_excerpt(ledger, "F-999")
        self.assertEqual(excerpt, ledger)

    def test_empty_fact_id_falls_back_to_full_ledger(self):
        ledger = "[VERIFIED] F-1: alpha claim.\n  numeric_value: 10%\n"
        excerpt = runner.build_ledger_excerpt(ledger, "")
        self.assertEqual(excerpt, ledger)


class TestFullRecheckRequiredRepeatFactId(unittest.TestCase):
    """委任_19 A-1新設(f): 過去cycleで一度でもBLOCKINGだったfact_idが
    このcycleにも含まれる場合、①水準の局所編集であっても全文Recheckを
    要することを確認する(hormuz_run03_standard rep9実測の再発防止)。"""

    def test_repeat_fact_id_requires_full_recheck_even_at_word_level(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None, "dev": {"related_fact_id": "HF-009"}}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "hormuz_run03_standard", frozenset({"HF-009"}))
        self.assertTrue(required)
        self.assertIn("same_fact_id_reappeared_across_cycles", reasons)

    def test_non_repeat_fact_id_with_no_other_condition_does_not_require_full_recheck(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None, "dev": {"related_fact_id": "HF-009"}}]
        required, reasons = runner.full_recheck_required(
            rewrite_records, blocking_claims, "hormuz_run03_standard", frozenset({"HF-999"}))
        self.assertFalse(required)
        self.assertEqual(reasons, [])

    def test_default_repeat_fact_ids_is_empty(self):
        rewrite_records = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2)"}]
        blocking_claims = [{"floor_reason": None, "dev": {"related_fact_id": "HF-009"}}]
        required, reasons = runner.full_recheck_required(rewrite_records, blocking_claims, "hormuz_run03_standard")
        self.assertFalse(required)


class TestFindSentenceContextFuzzyFallback(unittest.TestCase):
    """委任_19 A-1是正: rep9実測(REPORT§18)でlocal QA fastpath 3試行中2件が
    `revised_sentence_not_locatable_in_context`で失敗していた(exact
    substring不一致)ことを受け、SequenceMatcher近似fallbackを追加した。
    exactで見つかる場合の既存挙動は変えず、近似のみで見つかる/見つからない
    ケースを確認する。"""

    def test_exact_match_still_preferred(self):
        text = "First sentence here. Second sentence here. Third sentence here."
        before, target, after = runner.find_sentence_context(text, "Second sentence here.")
        self.assertEqual(target, "Second sentence here.")

    def test_near_match_with_whitespace_difference_found_via_fuzzy_fallback(self):
        text = "First sentence here. Also, some calls could  need   user information. Third sentence here."
        before, target, after = runner.find_sentence_context(
            text, "Also, some calls could need user information.")
        self.assertIsNotNone(target)
        self.assertIn("some calls could", target)
        self.assertEqual(before, "First sentence here.")
        self.assertEqual(after, "Third sentence here.")

    def test_dissimilar_needle_still_returns_none(self):
        text = "First sentence here. Second sentence here."
        before, target, after = runner.find_sentence_context(text, "Completely unrelated content about oil.")
        self.assertIsNone(target)


class TestEscalateToParagraphLadderSkip(unittest.TestCase):
    """委任_19 A-2(hormuz_run03_standard cycle枯渇是正)で導入し、委任_27
    Part1-1(design書§0-4/§5-11)で既定OFFへ変更した`escalate_to_paragraph`
    ladder skip機構のregression test(¥0)。**委任_27以降、既定
    (ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP=False)ではこの機構は発火
    しない**(各箇所は独立に初期単位から判断する、上位原則)。コード自体は
    削除していないため、flagを明示的にTrueへ戻すと旧来の挙動(①③飛ばし
    ④直行)に戻ることも確認する。"""

    def test_single_text_rewrite_does_not_skip_by_default_even_with_flag_set_on_claim(self):
        """claim_recに`escalate_to_paragraph=True`が付与されていても、
        ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIPが既定Falseのため①から
        試す(devにfloor flagが無いためclassify_problem_kindはunspecified
        =①開始)。"""
        from unittest import mock

        full_text = ("# Title\n\nSome sentence with a problem in it. Another sentence follows.\n\n"
                     "## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "problem"}, "escalate_to_paragraph": True,
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e1_minimal_word"):
                return "Some sentence without the problem. Another sentence follows."
            raise AssertionError(f"should not escalate past level 1, but called {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertEqual(result["ladder_level_used"], "1_word_connective")
        self.assertEqual(calls, ["test_e1_minimal_word"])

    def test_single_text_rewrite_skips_to_paragraph_level_when_flag_reenabled(self):
        """flagを明示的にTrueへ戻すと、旧来どおり①③を飛ばし④段落水準から
        直接試す(コード自体は壊れていない、再有効化はFable/ユーザー判断)。"""
        from unittest import mock

        full_text = ("# Title\n\nSome sentence with a problem in it. Another sentence follows.\n\n"
                     "## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "problem"}, "escalate_to_paragraph": True,
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e2_paragraph_rewrite"):
                return "Some sentence without the problem. Another sentence follows."
            raise AssertionError(f"should skip directly to paragraph level, but called {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm), \
                mock.patch.object(runner, "ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP", True):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertEqual(result["ladder_level_used"], "4_paragraph")
        self.assertEqual(calls, ["test_e2_paragraph_rewrite"])

    def test_single_text_rewrite_stops_at_ladder_exhausted_when_paragraph_level_guard_fails_and_level6_disabled(
            self):
        """委任_23 B-2: ⑥は既定OFF(ENABLE_LADDER_LEVEL_6_FULL_REWRITE=False)
        のため、①〜④全段でguardが失敗した場合は⑥のAPI callを試みず、
        ladder_exhausted_without_full_rewrite=Trueを返す(呼び出し側
        run_instanceがSTAGE4へ回す)。escalate_to_paragraph flagを明示的に
        再有効化した状態(④直行)で確認する。"""
        from unittest import mock

        full_text = ("# Title\n\nSome sentence with a problem in it. Another sentence follows.\n\n"
                     "## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "problem"}, "escalate_to_paragraph": True,
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e2_paragraph_rewrite"):
                # guard抵触(元claim文言がそのまま残る)を再現する。
                return "Some sentence with a problem in it. Another sentence follows, unchanged."
            raise AssertionError(f"⑥ disabled by default, should not call {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm), \
                mock.patch.object(runner, "ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP", True):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertIsNone(result["ladder_level_used"])
        self.assertFalse(result["guard_ok"])
        self.assertTrue(result["ladder_exhausted_without_full_rewrite"])
        self.assertEqual(calls, ["test_e2_paragraph_rewrite"])

    def test_single_text_rewrite_level6_still_works_when_feature_flag_reenabled(self):
        """委任_23 B-2: ⑥はコード削除せずfeature flagで残す。flagを明示的に
        Trueへ戻すと、iter7以前と同じ①〜⑥の挙動(⑥で解消)に戻ることを
        確認する(再有効化はユーザー判断だが、機構自体は壊れていない)。
        escalate_to_paragraph flagも明示的に再有効化した状態で確認する。"""
        from unittest import mock

        full_text = ("# Title\n\nSome sentence with a problem in it. Another sentence follows.\n\n"
                     "## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "problem"}, "escalate_to_paragraph": True,
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_e2_paragraph_rewrite"):
                return "Some sentence with a problem in it. Another sentence follows, unchanged."
            if label.endswith("_fulltext_fallback"):
                return "Some sentence without the problem. Another sentence follows."
            raise AssertionError(f"unexpected call to {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm), \
                mock.patch.object(runner, "ENABLE_LADDER_LEVEL_6_FULL_REWRITE", True), \
                mock.patch.object(runner, "ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP", True):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)
        self.assertEqual(result["ladder_level_used"], "6_full_article")
        self.assertEqual(calls, ["test_e2_paragraph_rewrite", "test_fulltext_fallback"])

    def test_paired_rewrite_skips_to_paragraph_level_when_flag_reenabled(self):
        from unittest import mock

        en_full = ("# Title\n\nSome sentence with a problem in it. Another sentence follows.\n\n"
                   "## In one line\nA plan changed.\n")
        ja_full = ("# タイトル\n\n問題のある文がある。もう一つの文が続く。\n\n"
                   "## 一言でまとめると\n案が変わった。\n")
        claim_rec = {
            "claim_text": "Some sentence with a problem in it.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": '"問題のある文がある。"', "dev": {"issue": "problem"}, "origin": "ja_source",
            "escalate_to_paragraph": True,
        }
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": en_full,
                   "source_article_text": ja_full}
        calls = []

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            if label.endswith("_j1_paired_rewrite_paragraph"):
                return ('{"ja_revised": "問題のない文がある。もう一つの文が続く。", '
                        '"en_revised": "Some sentence without the problem. Another sentence follows."}')
            raise AssertionError(f"should skip directly to paragraph level, but called {label}")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm), \
                mock.patch.object(runner, "ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP", True):
            result = runner.paired_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, claim_rec)
        self.assertEqual(result["ladder_level_used"], "4_paragraph")
        self.assertEqual(calls, ["test_j1_paired_rewrite_paragraph"])


class TestLadderExhaustedWithoutFullRewriteWiring(unittest.TestCase):
    """委任_23 B-2: run_instanceのメインループが、⑥ feature flag(既定OFF)
    によりladder_exhausted_without_full_rewriteが立ったclaimを、
    target_not_locatableと同じパターンで即座にSTAGE4_ESCALATIONへ回す
    ことをソース検査で確認する(¥0)。"""

    def test_run_instance_source_contains_ladder_exhausted_wiring(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("ladder_exhausted_records", src)
        self.assertIn('stage4_reason = "ladder_exhausted_without_full_rewrite"', src)

    def test_enable_ladder_level_6_full_rewrite_defaults_to_false(self):
        self.assertFalse(runner.ENABLE_LADDER_LEVEL_6_FULL_REWRITE)


class TestRepeatFactIdWiring(unittest.TestCase):
    """委任_19 A-2: run_instanceのメインループが同一fact_id再出現を検出し
    escalate_to_paragraphを付与すること、full_recheck_requiredへ
    repeat_fact_idsを渡すことをソース検査で確認する(¥0)。"""

    def test_run_instance_source_contains_escalation_wiring(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("escalate_to_paragraph", src)
        self.assertIn("repeat_fact_ids_for_recheck", src)
        # 委任_20 W3: full_recheck_required呼び出しへja_guard_ok/
        # ja_equivalence_verdictが追加された(引数の折返し位置が変わった
        # ため、呼び出し自体と新規引数名の存在を確認する形へ更新)。
        self.assertIn("full_recheck_required(\n            rewrite_records, blocking_claims, instance_id, "
                       "repeat_fact_ids_for_recheck,", src)
        self.assertIn("ja_guard_ok=", src)
        self.assertIn("ja_equivalence_verdict=", src)


class TestSameClaimReblockedLadderEscalationWiring(unittest.TestCase):
    """委任_24 A-2(§6-13): rep14で判明した第三要因(①水準のみのRewrite後の
    再発が、ラダー前進[§6-6 A-2]より先に§3-3安全網でSTAGE4化される)の
    是正を、run_instanceのメインループのソース検査で確認する(¥0)。
    ①・③水準までしか試していない再発はSTAGE4にせずescalate_to_paragraphを
    付与してループを継続し、④段落水準まで試行済みの再発のみ
    same_claim_fact_id_reblockedへ回ることを検証する。"""

    def test_run_instance_source_gates_reblock_on_escalated_to_paragraph(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("exhausted_matched_records", src)
        self.assertIn("escalatable_matched_records", src)
        self.assertIn('m.get("escalated_to_paragraph")', src)
        self.assertIn("ladder_exhausted_before_reblock", src)
        self.assertIn("same_claim_reblocked_escalated_to_paragraph", src)
        # same_claim_fact_id_reblockedは、exhausted_matched_records(=④段落
        # 水準まで試行済みの再発)のブロック内でのみSTAGE4理由として使われる
        # こと(旧来のmatched_records直後の無条件STAGE4ではないこと)を確認。
        exhausted_idx = src.index("if exhausted_matched_records:")
        reason_idx = src.index('stage4_reason = "same_claim_fact_id_reblocked"')
        escalatable_idx = src.index("if escalatable_matched_records:")
        self.assertLess(exhausted_idx, reason_idx)
        self.assertLess(reason_idx, escalatable_idx)

    def test_prior_blocking_records_persist_escalated_to_paragraph_flag(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('"escalated_to_paragraph": bool(c.get("escalate_to_paragraph"))', src)

    def test_find_matching_prior_record_source_uses_reversed_iteration(self):
        import inspect
        src = inspect.getsource(runner.find_matching_prior_record)
        self.assertIn("reversed(prior_records)", src)


# ============================================================
# 委任_20 W1(iii): JA fail-openガード(rep10 hormuz_run03_standard sample1
# cycle2の実データを再現用fixtureとして使用、
# `er052_output/open233_self_recovery_flow_runner_01_rep10/summary_rep10.json`
# L1091-1092のja_text_before_rewrite/ja_text_after_rewrite・L939の
# rewrite_hintから逐語で転記)。
# ============================================================
REP10_JA_TEXT_BEFORE_REWRITE = (
    "料金案は退場、原油高は居残り\n\n"
    "七月十三日、いきなり登場したのは、ホルムズ海峡の貨物に二割を求めるという料金案でした。\n\n"
    "トランプ氏が示した名目は、アメリカが海峡の安全を守る費用を返してもらうことです。"
    "対象は、海峡を通るすべての貨物。ところが、誰が集めるのか、誰が払うのか、"
    "どう計算するのかといった大事な部分は、まだ空欄でした。\n\n"
    "つまり、実際に料金を徴収し始めたわけではありません。舞台に登場したのは、"
    "完成した料金制度ではなく、二割という数字を掲げた提案でした。\n\n"
    "そして翌日、物語は急展開します。トランプ氏は、この二割の償還料案を取りやめ、"
    "湾岸諸国によるアメリカ向けの貿易や投資の案件に置き換えると発表しました。"
    "中東の指導者たちとの「非常に生産的な協議」に基づく決定だと説明しています。\n\n"
    "さらに記者団には、ホルムズ海峡を通る船に誰も料金を課すべきではない、"
    "料金という考え方自体を好まないとも話しました。二割案は、登場から約一日で"
    "舞台を降りたことになります。\n\n"
    "ここで原油市場にカメラを向けると、次の場面が始まります。\n\n"
    "料金案の撤回と置き換えが発表されたあと、ブレント原油先物は上げ幅を一時的に"
    "縮めました。これで値下がりの幕が開くのかと思ったところ、ほどなくして、"
    "発表前に近い高い水準へ戻りました。報道時点では約二点六パーセント高で、"
    "一バレル八十五ドルを超えていました。\n\n"
    "このとき確認できるのは、撤回の直後にBrent先物が下落したわけではない、"
    "ということです。同じ時間帯には、アメリカとイランの攻撃、海上封鎖、"
    "タンカーの安全への懸念が続いていました。\n\n"
    "料金案は消えました。けれど、海峡をめぐる緊張に関するニュースは、"
    "舞台に残ったままです。政治の発言が大きく変わっても、原油価格は一度揺れたあと、"
    "高い水準へ戻った。今回の面白さは、まるで一つの見出しだけでは、"
    "物語の結末まで決められなかったように見えるところです。"
)
REP10_JA_TEXT_AFTER_REWRITE = (
    "料金案は退場、原油高は居残り\n\n"
    "七月十三日、いきなり登場したのは、ホルムズ海峡の貨物に二割を求めるという料金案でした。\n\n"
    "トランプ氏が示した名目は、アメリカが海峡の安全を守る費用を返してもらうことです。"
    "対象は、海峡を通るすべての貨物。ところが、誰が集めるのか、誰が払うのか、"
    "どう計算するのかといった大事な部分は、まだ空欄でした。\n\n"
    "つまり、実際に料金を徴収し始めたわけではありません。舞台に登場したのは、"
    "完成した料金制度ではなく、二割という数字を掲げた提案でした。\n\n"
    "そして翌日、物語は急展開します。トランプ氏は、この二割の償還料案を取りやめ、"
    "湾岸諸国によるアメリカ向けの貿易や投資の案件に置き換えると発表しました。"
    "中東の指導者たちとの「非常に生産的な協議」に基づく決定だと説明しています。\n\n"
    "さらに記者団には、ホルムズ海峡を通る船に誰も料金を課すべきではない、"
    "料金という考え方自体を好まないとも話しました。二割案は、登場から約一日で"
    "舞台を降りたことになります。\n\n"
    "ここで原油市場にカメラを向けると、次の場面が始まります。\n\n"
    "料金案の撤回と置き換えが発表されたあと、ブレント原油先物は上げ幅を一時的に"
    "縮めました。これで値下がりの幕が開くのかと思ったところ、ほどなくして、"
    "発表前に近い高い水準へ戻りました。\n\n"
    "このとき確認できるのは、撤回の直後にBrent先物が下落したわけではない、"
    "ということです。同じ時間帯には、アメリカとイランの攻撃、海上封鎖、"
    "タンカーの安全への懸念が続いていました。\n\n"
    "料金案は消えました。けれど、海峡をめぐる緊張に関するニュースは、"
    "舞台に残ったままです。政治の発言が大きく変わっても、原油価格は一度揺れたあと、"
    "高い水準へ戻った。今回の面白さは、まるで一つの見出しだけでは、"
    "物語の結末まで決められなかったように見えるところです。"
)
REP10_REWRITE_HINT = (
    "「このとき確認できるのは、撤回の直後にBrent先物が下落したわけではない、"
    "ということです。」を、「撤回発表後、Brent先物は一時的に上げ幅を縮小したが、"
    "ほどなく発表前に近い高い水準へ戻った」と置き換えてください。参照Fact: HF-009。"
)


class TestJaFailOpenGuard(unittest.TestCase):
    """委任_20 W1(iii): rep10 hormuz_run03_standard sample1 cycle2の実データ
    (指摘JA文が一字一句残存したまま、別段落の"報道時点では約2.6%高..."が
    消失し`RESOLVED_REWRITE_THEN_DOWNGRADE`として誤って完了した事故)を
    ガードが実際に捕捉することを確認する(¥0、決定論)。"""

    def test_detects_rep10_hormuz_cycle2_defect(self):
        blocking_claims = [{
            "rewrite_hint": REP10_REWRITE_HINT,
            "dev": {"related_fact_id": "HF-009"},
        }]
        result = runner.ja_fail_open_guard(
            REP10_JA_TEXT_BEFORE_REWRITE, REP10_JA_TEXT_AFTER_REWRITE, blocking_claims)
        self.assertFalse(result["ok"])
        self.assertTrue(result["checked"])
        violation_types = {v["type"] for v in result["violations"]}
        self.assertIn("flagged_ja_sentence_unchanged", violation_types)
        self.assertIn("unexplained_ja_sentence_deletion", violation_types)
        deleted_sentences = [v["sentence"] for v in result["violations"]
                              if v["type"] == "unexplained_ja_sentence_deletion"]
        self.assertTrue(any("二点六パーセント" in s for s in deleted_sentences))

    def test_ok_when_ja_text_unchanged(self):
        blocking_claims = [{"rewrite_hint": REP10_REWRITE_HINT, "dev": {"related_fact_id": "HF-009"}}]
        result = runner.ja_fail_open_guard(
            REP10_JA_TEXT_BEFORE_REWRITE, REP10_JA_TEXT_BEFORE_REWRITE, blocking_claims)
        self.assertTrue(result["ok"])
        self.assertFalse(result["checked"])

    def test_ok_when_flagged_sentence_actually_rewritten_and_no_other_deletion(self):
        before = "First problem sentence. Unrelated second sentence."
        after = "First problem sentence, fixed correctly. Unrelated second sentence."
        blocking_claims = [{"rewrite_hint": '"First problem sentence." を修正してください。',
                             "dev": {"related_fact_id": "X-1"}}]
        result = runner.ja_fail_open_guard(before, after, blocking_claims)
        self.assertTrue(result["ok"])
        self.assertTrue(result["checked"])

    def test_no_extractable_quote_is_skipped_conservatively(self):
        before = "Some sentence here. Another one."
        after = "Some sentence here. Another one changed."
        blocking_claims = [{"rewrite_hint": "no quotes in this hint", "dev": {"related_fact_id": "X-1"}}]
        result = runner.ja_fail_open_guard(before, after, blocking_claims)
        self.assertTrue(result["ok"])
        self.assertFalse(result["checked"])


class TestExpandSameFactIdLocations(unittest.TestCase):
    """委任_20 W2: Stage1/Recheckのsame_fact_id_locationsを追加deviationへ
    展開する(¥0、決定論)。reuse fixture(フィールド無し)は安全側で
    従来動作のまま(何も追加しない)ことを確認する。"""

    def test_expands_verbatim_locations_found_in_article(self):
        article_text = "Title line here.\n\nBody sentence one. Another body sentence."
        deviations = [{
            "claim_in_article": "Body sentence one.", "severity": "MAJOR",
            "related_fact_id": "F-1",
            "same_fact_id_locations": ["Title line here."],
        }]
        out = runner.expand_same_fact_id_locations(deviations, article_text)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]["claim_in_article"], "Title line here.")
        self.assertTrue(out[1]["detected_by_enumeration"])
        self.assertEqual(out[1]["related_fact_id"], "F-1")

    def test_hallucinated_location_not_in_article_is_rejected(self):
        article_text = "Body sentence one."
        deviations = [{"claim_in_article": "Body sentence one.", "severity": "MAJOR",
                        "same_fact_id_locations": ["This text does not exist in the article."]}]
        out = runner.expand_same_fact_id_locations(deviations, article_text)
        self.assertEqual(len(out), 1)

    def test_missing_field_is_safe_fallback_noop(self):
        # reuse fixture(旧jsonにsame_fact_id_locations自体が無い)を模擬。
        article_text = "Body sentence one."
        deviations = [{"claim_in_article": "Body sentence one.", "severity": "MAJOR"}]
        out = runner.expand_same_fact_id_locations(deviations, article_text)
        self.assertEqual(out, deviations)

    def test_duplicate_location_not_added_twice(self):
        article_text = "Body sentence one. Body sentence one repeated elsewhere? No."
        deviations = [{
            "claim_in_article": "Body sentence one.", "severity": "MAJOR",
            "same_fact_id_locations": ["Body sentence one.", "Body sentence one."],
        }]
        out = runner.expand_same_fact_id_locations(deviations, article_text)
        self.assertEqual(len(out), 1)


HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE = (
    '# The Fee Plan Leaves, But High Oil Prices Stay\n\nOn July 13, a plan suddenly appeared. '
    'It would charge a 20 percent fee on cargo passing through the Strait of Hormuz.\n\n'
    'Trump said the fee would pay for the United States keeping the strait safe. It would cover '
    'all cargo passing through the strait. But important details were still missing. These '
    'included who would collect the fee, who would pay it, and how its amount would be '
    'decided.\n\nIn other words, no one had actually started collecting the fee. What appeared '
    'on stage was not a finished fee system. It was a proposal with the number 20 percent.\n\n'
    'Then, the next day, the story suddenly changed. Trump said he would drop the 20 percent fee '
    'plan. He would replace it with trade and investment deals between Gulf countries and the '
    'United States. He said this decision followed “very productive talks” with Middle '
    'Eastern leaders.\n\nHe also told reporters that no one should charge fees to ships passing '
    'through the Strait of Hormuz. He said he did not like the idea of fees. The 20 percent plan '
    'left the stage about one day after it appeared.\n\nNow, let us point the camera toward the '
    'oil market. The next scene begins.\n\nAfter the fee plan was withdrawn and replaced, Brent '
    'crude oil futures briefly lost some of their gains. Prices seemed ready to fall. But they '
    'soon returned to a high level near their earlier level. At the time of reporting, they were '
    'up about 2.6 percent, above 85 dollars a barrel.\n\nOil prices did not fall across the whole '
    'market after the plan was withdrawn. At the same time, attacks by the United States and Iran '
    'continued. So did a sea blockade and worries about tanker safety.\n\nThe fee plan '
    'disappeared. But news about tensions around the strait stayed on stage. Political statements '
    'changed greatly. Oil prices moved briefly, then returned to a high level. The interesting '
    'point this time was simple. One headline alone could not decide how the story would end.\n\n'
    '## In one line\nThe fee plan vanished, but oil prices stayed high as tensions around the '
    'Strait of Hormuz continued.'
)


class TestDeterministicSameFactIdLocationFallback(unittest.TestCase):
    """委任_23 A-2(b、REPORT§23 A): reuse fixture(`same_fact_id_locations`
    フィールドを持たない)向けの¥0決定論フォールバック。iter7実データ
    (`hormuz_run03_standard` instances_s2 cycle0、HF-009のbody claim)を
    fixtureとして使い、cycle1のfresh Recheck(LLMベース列挙)が実際に
    検出したin_one_line文を、cycle0の時点で候補化できることを確認する。"""

    CLAIM_TEXT = "Oil prices did not fall across the whole market after the plan was withdrawn."

    def test_finds_in_one_line_restatement_via_keyword_overlap(self):
        deviations = [{"claim_in_article": self.CLAIM_TEXT, "severity": "MAJOR",
                        "related_fact_id": "HF-009"}]
        out = runner.deterministic_same_fact_id_location_fallback(
            deviations, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        self.assertEqual(len(out), 1)
        locations = out[0]["same_fact_id_locations"]
        self.assertIn(
            "The fee plan vanished, but oil prices stayed high as tensions around the Strait of "
            "Hormuz continued.", locations)

    def test_does_not_flag_unrelated_sentence_with_two_shared_words(self):
        # "Prices seemed ready to fall." はclaimと{prices, fall}の2語のみを
        # 共有する(閾値3未満)ため候補化されない(過剰候補化防止の実測、
        # REPORT§23 A)。
        deviations = [{"claim_in_article": self.CLAIM_TEXT, "severity": "MAJOR"}]
        out = runner.deterministic_same_fact_id_location_fallback(
            deviations, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        locations = out[0]["same_fact_id_locations"]
        self.assertNotIn("Prices seemed ready to fall.", locations)
        self.assertNotIn("Trump said he would drop the 20 percent fee plan.", locations)

    def test_expand_same_fact_id_locations_adds_verbatim_independent_claims(self):
        # 本フォールバック+既存expand_same_fact_id_locationsを連結した
        # 実際のrun_instance配線と同じ経路で、独立claimへ展開されることを
        # 確認する(fail-closed: 逐語実在確認込み)。閾値3では、in_one_line
        # 文に加え、共有語3語("plan"/"oil"/"withdrawn")の本文文1件も
        # 候補化される(既知の限界、過剰候補化はStage2が独立にACCEPTABLE
        # 判定でscreenする設計、REPORT§23 A)。
        deviations = [{"claim_in_article": self.CLAIM_TEXT, "severity": "MAJOR",
                        "related_fact_id": "HF-009"}]
        enumerated = runner.deterministic_same_fact_id_location_fallback(
            deviations, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        out = runner.expand_same_fact_id_locations(
            enumerated, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        self.assertEqual(len(out), 3)
        claim_texts = {o["claim_in_article"] for o in out}
        self.assertIn(
            "The fee plan vanished, but oil prices stayed high as tensions around the Strait of "
            "Hormuz continued.", claim_texts)
        for o in out[1:]:
            self.assertEqual(o["related_fact_id"], "HF-009")
            self.assertTrue(o["detected_by_enumeration"])

    def test_existing_same_fact_id_locations_field_is_not_overwritten(self):
        # fresh instance(委任_20 W2のLLMベース列挙)は既にフィールドを
        # 持つため、本フォールバックはスキップし上書きしない。
        deviations = [{"claim_in_article": self.CLAIM_TEXT, "severity": "MAJOR",
                        "same_fact_id_locations": ["already enumerated by LLM"]}]
        out = runner.deterministic_same_fact_id_location_fallback(
            deviations, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        self.assertEqual(out[0]["same_fact_id_locations"], ["already enumerated by LLM"])

    def test_empty_claim_text_returns_no_locations(self):
        deviations = [{"claim_in_article": "", "severity": "MAJOR"}]
        out = runner.deterministic_same_fact_id_location_fallback(
            deviations, HORMUZ_RUN03_STANDARD_CYCLE0_EN_TEXT_BEFORE_REWRITE)
        self.assertEqual(out[0]["same_fact_id_locations"], [])

    def test_run_instance_source_wires_fallback_into_reuse_path(self):
        # 委任_23 A-2(b): reuse mode(stage1_mode=="reuse")の分岐内で本
        # フォールバックが呼ばれていることをソース検査で確認する(¥0)。
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("deterministic_same_fact_id_location_fallback", src)


class TestJaPendingDeviationSafetyNet(unittest.TestCase):
    """委任_20 W1(i): run_instanceのソースにJA未解消フラグ(ja_pending_
    deviation)とSTAGE4安全網(ja_deviation_unresolved)、JA recheck
    deviationsの次cycleへの合流が実装されていることを確認する(¥0)。"""

    def test_run_instance_source_contains_ja_pending_deviation_safety_net(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("ja_pending_deviation", src)
        self.assertIn("ja_deviation_unresolved", src)
        self.assertIn("ja_major_deviations", src)
        self.assertIn('d["origin"] = "ja_source"', src)


# ============================================================
# 委任_21 A-1: JA fail-openガードの言語判定是正(rep11実データを
# fixtureとして使用、`er052_output/open233_self_recovery_flow_runner_01_
# rep11/instances_s1/bgroup_B3.json` cycle1のja_text_before_rewrite/
# ja_text_after_rewrite(実際は英語)・stage2_results[0].rewrite_hintから
# 逐語で転記)。`bgroup_B3`はrep11で2/2 sampleとも本バグにより誤って
# STAGE4_ESCALATIONへ回った(KPI後退)。
# ============================================================
REP11_B3_SOURCE_ARTICLE_TEXT_BEFORE = '# 20% Withdrawn—but the Oil Chart Was Not Finished Yet\n\nThis news feels like a short play in three acts. Act One was “20%.” Act Two brought an unexpected turn. Act Three was an unexpected move in oil prices.\n\nThe curtain rose on July 13. At 10:16 a.m., Trump posted that the United States would seek a 20% charge on all cargo passing through the Strait of Hormuz. The aim was to recover the cost of US efforts to keep the strait safe.\n\nBut “20%” was not a finished system. The post did not say who would pay, how the money would be collected, or what legal basis would support it. For the moment, only a large number stood at center stage.\n\nThe number stayed at center stage for about a day. Then the story took a sharp turn.\n\n### The 20% plan changes overnight\n\nAbout 24 hours and 48 minutes later, at 11:04 a.m. on July 14, Trump said the 20% plan would be replaced by trade and investment projects between Gulf states and the US. He cited “very productive discussions” with Middle Eastern leaders. He also said no one should charge ships in the Strait, and that he disliked fees.\n\nThe change was sudden. But to read the oil move, the dates must be kept separate. On July 13, Brent rose 9.59% and settled at $83.30. Reuters linked that rise to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz.\n\n### The chart refuses to stay down\n\nOn July 14, after the withdrawal and replacement announcement, Brent crude futures briefly gave back some of their gains. Soon, they returned close to the high level before the announcement. At the time of reporting, Brent was up about 2.6%, above $85 a barrel. Its final settlement price was $84.73, up 1.7% from the day before.\n\n## In one line\n\nConcerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.'
REP11_B3_SOURCE_ARTICLE_TEXT_AFTER = '# 20% Withdrawn—but the Oil Chart Was Not Finished Yet\n\nThis news feels like a short play in three acts. Act One was “20%.” Act Two brought an unexpected turn. Act Three was an unexpected move in oil prices.\n\nThe curtain rose on July 13. At 10:16 a.m., Trump posted that the United States would seek a 20% charge on all cargo passing through the Strait of Hormuz. The aim was to recover the cost of US efforts to keep the strait safe.\n\nBut “20%” was not a finished system. The post did not say who would pay, how the money would be collected, or what legal basis would support it. For the moment, only a large number stood at center stage.\n\nThe number stayed at center stage for about a day. Then the story took a sharp turn.\n\n### The 20% plan changes overnight\n\nAbout 24 hours and 48 minutes later, at 11:04 a.m. on July 14, Trump said the 20% plan would be replaced by trade and investment projects between Gulf states and the US. He cited “very productive discussions” with Middle Eastern leaders. He also said no one should charge ships in the Strait, and that he disliked fees.\n\nThe change was sudden. But to read the oil move, the dates must be kept separate. On July 13, Brent rose 9.59% and settled at $83.30. Reuters linked that rise to concern about a US sea blockade of Iran, planned for the next day, and energy shipments through the Strait of Hormuz.\n\n### The chart refuses to stay down\n\nOn July 14, after the withdrawal and replacement announcement, Brent crude futures briefly gave back some of their gains. Soon, they returned close to the high level before the announcement. At the time of reporting, Brent was up about 2.6%, above $85 a barrel. Its final settlement price was $84.73, up 1.7% from the day before.\n\n## In one line\n\nConcerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% plan left the stage, but the chart only pulled back briefly before recovering: the policy turn and the oil chart’s “not over yet” movement happened on the same day.'
REP11_B3_REWRITE_HINT = '対象文: “Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy 20% plan left the stage”。「so」が懸念の継続を20％案の撤回理由として結び付けているため、その因果関係を削除し、懸念の継続と案の置換を別個の事実として記述してください。撤回・置換は中東指導者との協議に基づくとの説明に沿ってください(HF-007)。'


class TestJaFailOpenGuardLanguageAware(unittest.TestCase):
    """委任_21 A-1: rep11実データ(`bgroup_B3`、source_article_textが実際
    には英語)で、言語判定是正後はガードが誤発火しないことを確認する。
    比較対象として、rep10 hormuz実データ(真のJA、split_ja_sentences)は
    既存`TestJaFailOpenGuard`で発火することを既に確認済み(regressionなし)。"""

    def test_no_false_positive_on_english_source_article_text_b3_rep11(self):
        blocking_claims = [{"rewrite_hint": REP11_B3_REWRITE_HINT, "dev": {"related_fact_id": "HF-007"}}]
        result = runner.ja_fail_open_guard(
            REP11_B3_SOURCE_ARTICLE_TEXT_BEFORE, REP11_B3_SOURCE_ARTICLE_TEXT_AFTER, blocking_claims)
        self.assertTrue(result["ok"])
        self.assertFalse(result["indeterminate"])
        self.assertEqual(result["violations"], [])

    def test_still_detects_rep10_hormuz_defect_after_language_switch(self):
        # regression確認: 既存TestJaFailOpenGuard.test_detects_rep10_
        # hormuz_cycle2_defectと同一fixtureで、言語判定是正後も真のJA
        # テキストはsplit_ja_sentencesのまま使われ発火することを確認する。
        blocking_claims = [{"rewrite_hint": REP10_REWRITE_HINT, "dev": {"related_fact_id": "HF-009"}}]
        result = runner.ja_fail_open_guard(
            REP10_JA_TEXT_BEFORE_REWRITE, REP10_JA_TEXT_AFTER_REWRITE, blocking_claims)
        self.assertFalse(result["ok"])
        self.assertFalse(result["indeterminate"])

    def test_indeterminate_when_neither_splitter_can_split(self):
        # 句読点が実質存在しないtext(JA/EN判定を問わず1文以下にしか
        # 分割できない)の場合、違反判定はせず(ok=True)indeterminate=True
        # を返す(全文Recheック条件へ倒す、STAGE4直行にはしない)。
        before = "aaa bbb ccc ddd eee"
        after = "aaa bbb ccc ddd eee fff"
        blocking_claims = [{"rewrite_hint": '"aaa bbb ccc ddd eee" を修正してください。',
                             "dev": {"related_fact_id": "X-1"}}]
        result = runner.ja_fail_open_guard(before, after, blocking_claims)
        self.assertTrue(result["ok"])
        self.assertTrue(result["indeterminate"])


# ============================================================
# 委任_21 A-2: 局所QA locateバグ是正(rep11実データを fixtureとして使用、
# `er052_output/open233_self_recovery_flow_runner_01_rep11/instances_s1/
# meta_run03_standard.json` cycle1のen_text_after_rewriteから逐語で転記。
# after_fragment(needle)はrewrite_hint中の引用断片[2文]がrewrite_hint_
# quoteとして`target_sentence`に採用され、E1水準のRewrite後も2文のまま
# 返るため、旧実装ではどの単一文とも一致せず
# `revised_sentence_not_locatable_in_context`でskipしていた)。
# ============================================================
REP11_META_EN_TEXT_AFTER_REWRITE = '# Some AI Phone Calls Had Humans Behind the Scenes\n\nIt was a small surprise. A service let people ask AI to make phone calls. But humans made some of the calls behind the scenes. This was part of a test.\n\nThe main player was Muse, Meta’s AI assistant. Muse can call businesses and stores in the United States. It can book haircuts and check if items are in stock. It can also get price estimates from businesses. If AI can handle difficult calls, it seems very useful.\n\nIn some tests, trained human contract workers made the calls, not AI. They handled each conversation until it ended.\n\nThe problem was not that humans made the calls. The problem was telling users who was speaking.\n\nPeople asking Muse to call might think AI was calling. But sometimes, a human was speaking instead. If no one explained this clearly, users could not know. They could not tell if it was AI or a person. They enjoyed AI’s convenience, but a human was on the other end. They did not realize it. That was happening behind the scenes.\n\nAlso, some calls might need user information to continue. That information might accidentally be shared with contract workers at a call center. Meta employees pointed this out inside the company as a privacy concern.\n\nNews reports also cited one employee’s report. It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees. However, this is only one report. It would be wrong to say all contract workers did this.\n\nA Meta executive admitted the test began without a clear explanation. That was a mistake. The company also restored its human help feature to its earlier form, at least for now.\n\nThe real challenge for AI calls is not only how they talk. They must also be honest about who is on the other end. The more useful a service is, the less it should hide workers behind the scenes. The Muse case showed this simple but important point.\n\n## In one line\nSome calls through Meta’s AI assistant were actually handled by humans, but users were not properly told.'
REP11_META_AFTER_FRAGMENT = 'Also, some calls might need user information to continue. That information might accidentally be shared with contract workers at a call center.'


class TestFindSentenceContextMultiSentenceNeedle(unittest.TestCase):
    """委任_21 A-2: rep11実データ(`meta_run03_standard` sample1 cycle1)で
    局所QA fastpathが`revised_sentence_not_locatable_in_context`により
    毎回skipしていた実バグをfind_sentence_contextが是正後は解決すること
    を確認する。"""

    def test_locates_two_sentence_needle_from_rep11_meta_run03(self):
        before_ctx, located, after_ctx = runner.find_sentence_context(
            REP11_META_EN_TEXT_AFTER_REWRITE, REP11_META_AFTER_FRAGMENT)
        self.assertIsNotNone(located)
        self.assertEqual(located, REP11_META_AFTER_FRAGMENT)
        self.assertEqual(before_ctx, "That was happening behind the scenes.")
        self.assertEqual(after_ctx, "Meta employees pointed this out inside the company as a privacy concern.")

    def test_single_sentence_needle_still_works_unaffected(self):
        # 既存の単一文needleの経路(regression確認)。
        full_text = "First sentence here. Second sentence here. Third sentence here."
        before_ctx, located, after_ctx = runner.find_sentence_context(full_text, "Second sentence here.")
        self.assertEqual(located, "Second sentence here.")
        self.assertEqual(before_ctx, "First sentence here.")
        self.assertEqual(after_ctx, "Third sentence here.")

    def test_returns_none_when_multi_sentence_needle_not_present(self):
        full_text = "First sentence here. Second sentence here. Third sentence here."
        before_ctx, located, after_ctx = runner.find_sentence_context(
            full_text, "A completely different sentence. Another unrelated one.")
        self.assertIsNone(located)


# ============================================================
# 委任_22 A-1: JA/EN等価チェックgatingの言語判定是正。`REP11_B3_SOURCE_
# ARTICLE_TEXT_AFTER`(既存定数、上のTestJaFailOpenGuardLanguageAware
# セクションで定義済み)はrep12 `bgroup_B3` cycle1の`ja_text_after_rewrite`
# と逐語一致する(reuse fixtureのため同一instanceはrep11・rep12で同文言)。
# rep12実データでは、このcycleの全文Recheck・JA Recheckは双方とも
# `LEDGER_COMPLIANT`かつ`all_prior_issues_resolved=True`(=ja_ok本来True)
# だったが、`ja_en_equivalence_verdict=REVIEW_REQUIRED`の無条件gatingに
# より`ja_ok`がFalseへ強制され、次cycle(blocking_count=0)でも
# `ja_pending_deviation`が残り`STAGE4_ESCALATION(ja_deviation_unresolved)`
# へ2/2到達していた(`er052_output/open233_self_recovery_flow_runner_01_
# rep12/instances_s1/bgroup_B3.json`)。
# ============================================================
class TestResolveJaOkAfterEquivalenceGating(unittest.TestCase):
    def test_review_required_with_indeterminate_lang_does_not_block_rep12_b3(self):
        # rep12 bgroup_B3実データ: ja_ok本来True、verdict=REVIEW_REQUIRED、
        # JA側フィールドが実際には英語(indeterminate)。gatingで強制的に
        # Falseへ倒されない(=STAGE4直行を強制しない)ことを確認する。
        result = runner.resolve_ja_ok_after_equivalence_gating(
            True, "REVIEW_REQUIRED", REP11_B3_SOURCE_ARTICLE_TEXT_AFTER)
        self.assertTrue(result["ja_ok"])
        self.assertTrue(result["lang_indeterminate"])
        self.assertTrue(result["not_gated_indeterminate_lang"])
        self.assertFalse(result["blocked_by_equivalence"])

    def test_review_required_with_normal_ja_lang_and_confirmed_resolved_no_longer_gates(self):
        # 委任_23 A-2是正(REPORT§23 A、`hormuz_run03_standard` real_run
        # Escalation真因): 真のJAテキスト(rep10 hormuz実データ)でも、
        # ja_ok=True(全文RecheckがEN/JA双方の解消を既に確認済み)の場合は
        # equivalence REVIEW_REQUIREDだけでja_okを覆さない(旧挙動から変更、
        # rep10のFAIL実例はja_recheck自体が独立にLEDGER_DEVIATIONだった
        # ため本変更の影響を受けない、§6-7参照)。
        result = runner.resolve_ja_ok_after_equivalence_gating(
            True, "REVIEW_REQUIRED", REP10_JA_TEXT_AFTER_REWRITE)
        self.assertTrue(result["ja_ok"])
        self.assertFalse(result["lang_indeterminate"])
        self.assertFalse(result["blocked_by_equivalence"])
        self.assertFalse(result["not_gated_indeterminate_lang"])
        self.assertTrue(result["not_gated_already_confirmed_resolved"])

    def test_review_required_with_normal_ja_lang_and_unconfirmed_ja_ok_stays_false(self):
        # 委任_23 A-2: ja_ok=False(全文Recheckが既に未解消と判定)の場合は
        # gating自体がno-op(元々False)であり、この是正後も挙動は変わらない
        # (二重の安全網のうち、ja_recheck自体の判定は無変更のまま機能する)。
        result = runner.resolve_ja_ok_after_equivalence_gating(
            False, "REVIEW_REQUIRED", REP10_JA_TEXT_AFTER_REWRITE)
        self.assertFalse(result["ja_ok"])
        self.assertFalse(result["blocked_by_equivalence"])
        self.assertFalse(result["not_gated_already_confirmed_resolved"])

    def test_fail_verdict_always_blocks_even_with_indeterminate_lang(self):
        # FAIL(等価チェックが実際に不一致を検出)は、JA側言語判定に関わらず
        # 従来どおりja_okをFalseへ倒す(次段のRewriteへ、最終的にSTAGE4)。
        result = runner.resolve_ja_ok_after_equivalence_gating(
            True, "FAIL", REP11_B3_SOURCE_ARTICLE_TEXT_AFTER)
        self.assertFalse(result["ja_ok"])
        self.assertTrue(result["blocked_by_equivalence"])
        self.assertIsNone(result["lang_indeterminate"])

    def test_pass_verdict_does_not_change_ja_ok(self):
        result = runner.resolve_ja_ok_after_equivalence_gating(True, "PASS", REP10_JA_TEXT_AFTER_REWRITE)
        self.assertTrue(result["ja_ok"])
        self.assertFalse(result["blocked_by_equivalence"])
        self.assertFalse(result["not_gated_indeterminate_lang"])

    def test_none_verdict_does_not_change_ja_ok(self):
        result = runner.resolve_ja_ok_after_equivalence_gating(True, None, None)
        self.assertTrue(result["ja_ok"])
        self.assertFalse(result["blocked_by_equivalence"])

    def test_already_false_ja_ok_stays_false_and_not_double_flagged(self):
        # 全文Recheck自体が既にja_ok=Falseと判定していた場合(通常経路)、
        # gatingは追加で状態を変えない(blocked_by_equivalenceは新規に
        # このgatingがFalseへ倒した場合のみTrueにする、既に別理由でFalseの
        # 場合はフラグを立てない)。
        result = runner.resolve_ja_ok_after_equivalence_gating(
            False, "REVIEW_REQUIRED", REP10_JA_TEXT_AFTER_REWRITE)
        self.assertFalse(result["ja_ok"])
        self.assertFalse(result["blocked_by_equivalence"])


class TestClassifyProblemKind(unittest.TestCase):
    """委任_27 Part1-2: Stage1 deterministic floor flag(dev)から問題種類を
    分類するclassify_problem_kind()のregression test(¥0)。"""

    def test_no_flags_is_unspecified(self):
        self.assertEqual(runner.classify_problem_kind({}), "unspecified")
        self.assertEqual(runner.classify_problem_kind({"issue": "x"}), "unspecified")

    def test_changed_scope_is_term_scope(self):
        self.assertEqual(runner.classify_problem_kind({"changed_scope": True}), "term_scope")

    def test_changed_number_with_suppressed_reason_is_rounding(self):
        dev = {"changed_number": True, "changed_number_suppressed_reason": "natural_rounding(委任_14 B-1)"}
        self.assertEqual(runner.classify_problem_kind(dev), "rounding")

    def test_changed_number_without_suppression_is_not_rounding(self):
        # floorが維持されたままのchanged_number(自然な丸めと判定されな
        # かった場合)はterm_scope等の他カテゴリにも該当しないため
        # unspecified(既存の①開始挙動を維持、丸め専用分類はしない)。
        self.assertEqual(runner.classify_problem_kind({"changed_number": True}), "unspecified")

    def test_changed_causality_is_causality(self):
        self.assertEqual(runner.classify_problem_kind({"changed_causality": True}), "causality")

    def test_changed_actor_is_actor(self):
        self.assertEqual(runner.classify_problem_kind({"changed_actor": True}), "actor")

    def test_changed_time_is_time(self):
        self.assertEqual(runner.classify_problem_kind({"changed_time": True}), "time")

    def test_single_logic_flag_is_sentence_logic(self):
        self.assertEqual(runner.classify_problem_kind({"changed_negation": True}), "sentence_logic")
        self.assertEqual(runner.classify_problem_kind({"unsupported_new_claim": True}), "sentence_logic")

    def test_two_logic_flags_is_multi_sentence(self):
        self.assertEqual(
            runner.classify_problem_kind({"changed_negation": True, "changed_certainty": True}),
            "multi_sentence")

    def test_priority_scope_over_logic_flags(self):
        # changed_scopeが立っていれば、他のlogic flagが同時に立っていても
        # term_scopeを優先する(より限定的な初期単位を優先、§5-11)。
        dev = {"changed_scope": True, "changed_negation": True, "changed_certainty": True}
        self.assertEqual(runner.classify_problem_kind(dev), "term_scope")


class TestFilterLevelsByProblemKind(unittest.TestCase):
    """委任_27 Part1-2: 初期Rewrite単位の写像でlevelsを絞り込む
    filter_levels_by_problem_kind()のregression test(¥0)。"""

    def _levels(self):
        return [{"name": "1_word_connective"}, {"name": "3_sentence"}, {"name": "4_paragraph"}]

    def test_unspecified_keeps_all_levels(self):
        result = runner.filter_levels_by_problem_kind(self._levels(), {})
        self.assertEqual([lv["name"] for lv in result], ["1_word_connective", "3_sentence", "4_paragraph"])

    def test_actor_keeps_all_levels_starting_from_word(self):
        result = runner.filter_levels_by_problem_kind(self._levels(), {"changed_actor": True})
        self.assertEqual([lv["name"] for lv in result], ["1_word_connective", "3_sentence", "4_paragraph"])

    def test_sentence_logic_starts_at_level3(self):
        result = runner.filter_levels_by_problem_kind(self._levels(), {"changed_negation": True})
        self.assertEqual([lv["name"] for lv in result], ["3_sentence", "4_paragraph"])

    def test_multi_sentence_starts_at_level4(self):
        dev = {"changed_negation": True, "changed_comparison": True}
        result = runner.filter_levels_by_problem_kind(self._levels(), dev)
        self.assertEqual([lv["name"] for lv in result], ["4_paragraph"])

    def test_rounding_returns_empty(self):
        dev = {"changed_number": True, "changed_number_suppressed_reason": "natural_rounding"}
        result = runner.filter_levels_by_problem_kind(self._levels(), dev)
        self.assertEqual(result, [])


class TestActorRewriteGuard(unittest.TestCase):
    """委任_27 Part1-3: 主体置換ガードactor_rewrite_guard_ok()の
    regression test(¥0)。neg1 cycle2実データ(users→employees却下)を
    fixtureとして使う(docs/pm/open233_evidence_disclosure_neg1_neg3_
    hormuz_01.md §1、MUSE-HC-012)。"""

    def test_neg1_cycle2_users_to_employees_is_rejected(self):
        # 実データ(disclosure §1): EN Beforeは"users"/"user"、EN Afterは
        # "employees"。MUSE-HC-012のledger_textはJA本文のみで英語の
        # "employees"という語を含まない(実際のfixture、捏造ではない)。
        before = ("Here was the reveal. The test began without clearly telling users "
                  "that contract workers would make the calls.")
        after = ("Here was the reveal. The test began without clearly telling employees "
                 "that contract workers would make the calls.")
        ledger_text = ("[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、"
                       "適切な開示なしに契約スタッフが電話をかけるテストを開始したことを"
                       "「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。")
        self.assertFalse(runner.actor_rewrite_guard_ok(before, after, ledger_text))

    def test_no_new_actor_noun_is_always_ok(self):
        before = "Some users were not told."
        after = "Some users were not clearly told."
        self.assertTrue(runner.actor_rewrite_guard_ok(before, after, "[VERIFIED] X: ..."))

    def test_new_actor_noun_present_in_ledger_is_ok(self):
        before = "Some people were not told."
        after = "Some contractors were not told."
        ledger_text = "[VERIFIED] X: contractors handled the calls."
        self.assertTrue(runner.actor_rewrite_guard_ok(before, after, ledger_text))


class TestActorGuardAlwaysEvaluatedRegardlessOfProblemKind(unittest.TestCase):
    """委任_31 Part1(a)是正(design書§4-24): Trial C期待2の実データ
    (users→employees)が、`classify_problem_kind`の優先順位(term_scope>
    actor)によりproblem_kind="term_scope"に分類される場合でも、
    主体置換ガードが発火し却下されることを確認する(委任_30で発見した
    設計上の盲点のregression test、¥0、API呼び出しはmock)。"""

    def test_term_scope_and_actor_both_true_still_rejects_users_to_employees(self):
        full_text = ("# Title\n\nHere was the reveal. The test began without clearly telling "
                     "users that contract workers would make the calls.\n")
        ledger_text = ("[VERIFIED] MUSE-HC-012: MetaのSuperintelligence Labs部門の副社長は、"
                       "適切な開示なしに契約スタッフが電話をかけるテストを開始したことを"
                       "「ミス」だったと認め、機能を当面ロールバックしたと社内投稿で説明した。")
        claim_rec = {
            "claim_text": "The test began without clearly telling users that contract "
                           "workers would make the calls.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "",
            # changed_scope=True かつ changed_actor=True(委任_30 Trial C
            # 期待2の実データと同じ組み合わせ)。classify_problem_kindの
            # 優先順位により problem_kind="term_scope" になる(actorではない)。
            "dev": {"changed_scope": True, "changed_actor": True, "issue": "scope widened"},
        }
        self.assertEqual(
            runner.classify_problem_kind(claim_rec["dev"]), "term_scope",
            "前提: このdevの組み合わせはterm_scopeに分類される(盲点の再現条件)")
        fixture = {"ledger_text": ledger_text, "article_text": full_text}

        def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            # どの水準でも"users"を"employees"へ置換する応答を返す
            # (ledger_textに存在しない新しい主体語、却下されるべき)。
            return ("Here was the reveal. The test began without clearly telling employees "
                    "that contract workers would make the calls.")

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
            result = runner.single_text_rewrite(
                None, {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []},
                [], [], "test", fixture, "article_text", claim_rec)

        # 是正前(旧実装)は`problem_kind == "actor"`の場合のみガードを
        # 評価していたため、term_scope分類のこのclaimではガードが一度も
        # 発火せず"employees"への置換がそのまま通っていた(委任_30開示)。
        # 是正後は却下され、updated_textが変化しないまま終わることを確認する。
        self.assertFalse(result["guard_ok"])
        self.assertIn("actor_guard_rejected", result["method"])
        self.assertEqual(result["updated_text"], full_text)


class TestEscalateToParagraphDisabledByDefault(unittest.TestCase):
    """委任_27 Part1-1: escalate_to_paragraphのladder skipが既定で発火
    しないこと(ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP=False)を確認
    する(¥0、API呼び出しはmock)。"""

    def test_flag_defaults_to_false(self):
        self.assertFalse(runner.ENABLE_ESCALATE_TO_PARAGRAPH_LADDER_SKIP)

    def test_escalate_flag_on_claim_no_longer_skips_level1_and_3(self):
        full_text = ("# Title\n\nConcerns continued on July 14. So the flashy 20% plan left "
                     "the stage.\n\n## In one line\nA plan changed.\n")
        claim_rec = {
            "claim_text": "So the flashy 20% plan left the stage.",
            "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "ledger_conditions",
            "rewrite_hint": "", "dev": {"issue": "wrong causal link"},
            # 旧機構が有効だった場合はここでlevel1/3がskipされ、いきなり
            # level4(段落)が試される。既定OFFでは、levelは通常どおり
            # level1から試す(classify_problem_kindはdevにfloor flagが
            # 無いためunspecified=level1開始)。
            "escalate_to_paragraph": True,
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


class TestStage1FreshWithMisconceptionPrinciple(unittest.TestCase):
    """委任_28 Part0-1: Stage1(V4A)Trial harnessへの重大誤解原則配線の
    regression test(¥0、API呼び出しはmock)。既存`stage1_fresh()`は無変更で
    あること・新関数は`developer_message_override`を渡すことの両方を確認する。"""

    def test_stage1_fresh_unchanged_uses_no_override(self):
        captured = {}

        def fake_check(client, ledger, article, model, variant, include_related_fact_id=False,
                       source_article_text=None, developer_message_override=None):
            captured["override"] = developer_message_override
            return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []},
                    "usage": {"input_tokens": 1, "output_tokens": 1}, "prompt": "p"}

        fixture = {"ledger_text": "L", "article_text": "A"}
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        # 委任_28事故是正: runner.stage1_fresh()は既存どおりrecord_call→
        # save_budget_state(runner自身の固定BUDGET_STATE_PATH)を経由する
        # ため、このunittest自体が他delegation(rep15)の既存証跡を上書き
        # しないよう、save_budget_stateを必ずno-opへ差し替えて呼び出す。
        with mock.patch.object(runner.trial, "run_trial_deviation_check", side_effect=fake_check), \
             mock.patch.object(runner, "save_budget_state", lambda s: None):
            runner.stage1_fresh(None, state, [0], [], "label", fixture)
        self.assertIsNone(captured["override"])

    def test_new_function_passes_misconception_override(self):
        captured = {}

        def fake_check(client, ledger, article, model, variant, include_related_fact_id=False,
                       source_article_text=None, developer_message_override=None):
            captured["override"] = developer_message_override
            return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []},
                    "usage": {"input_tokens": 1, "output_tokens": 1}, "prompt": "p"}

        fixture = {"ledger_text": "L", "article_text": "A"}
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner.trial, "run_trial_deviation_check", side_effect=fake_check):
            result = runner.stage1_fresh_with_misconception_principle(
                None, state, [0], [], "label", fixture)
        self.assertEqual(captured["override"], runner.trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
        self.assertEqual(result["overall_status"], "LEDGER_COMPLIANT")


class TestHookRubricTextWiring(unittest.TestCase):
    """委任_28 Part0-1/0-3: `run_stage2_hook_batch`の`hook_rubric_text`
    引数配線と、`HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2`のtie-break
    明文化のregression test(¥0)。"""

    def test_default_uses_hook_rubric_unchanged(self):
        captured = {}

        class FakeResp:
            output_text = '{"judgments": []}'
            id = "r1"
            model = "gpt-6-luna"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    captured["prompt"] = kwargs["input"][1]["content"]
                    return FakeResp()

        s2h.run_stage2_hook_batch(FakeClient(), "(ledger)", None, "(hook)", [])
        self.assertIn(s2h.HOOK_RUBRIC.strip(), captured["prompt"])
        self.assertNotIn("tie-break", captured["prompt"])

    def test_override_uses_misconception_principle_v2(self):
        captured = {}

        class FakeResp:
            output_text = '{"judgments": []}'
            id = "r1"
            model = "gpt-6-luna"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    captured["prompt"] = kwargs["input"][1]["content"]
                    return FakeResp()

        s2h.run_stage2_hook_batch(FakeClient(), "(ledger)", None, "(hook)", [],
                                   hook_rubric_text=s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V2)
        self.assertIn("重大誤解原則", captured["prompt"])
        self.assertIn("tie-break", captured["prompt"])

    def test_hook_tiebreak_text_mentions_allow_and_block_criteria(self):
        self.assertIn("conversational restatement", s2h.HOOK_TIEBREAK_TEXT)
        self.assertIn("未確認の具体的な", s2h.HOOK_TIEBREAK_TEXT)


class TestSafetyCriticalSubIdsHormuzExclusion(unittest.TestCase):
    """委任_28 Part0-2: SAFETY_CRITICAL_SUB_IDSからhormuz-HF009を除外した
    ことのregression test(¥0)。"""

    def test_hormuz_hf009_excluded(self):
        self.assertNotIn("hormuz-HF009", r3d.SAFETY_CRITICAL_SUB_IDS)

    def test_other_eight_still_present(self):
        # 委任_29 Part1でA5-1もこのリストから除外されたため、期待集合を
        # 8件(A5-1除く)へ更新する(TestSafetyCriticalSubIdsA5_1Exclusion参照)。
        expected = {"A2A3-0", "A4-0", "A4-1", "A5-0", "Meta-1", "Meta-2", "B3", "B4-a"}
        self.assertEqual(set(r3d.SAFETY_CRITICAL_SUB_IDS), expected)


class TestSafetyCriticalSubIdsA5_1Exclusion(unittest.TestCase):
    """委任_29 Part1: SAFETY_CRITICAL_SUB_IDSからA5-1を除外し、
    CORRECT_LABEL_OVERRIDES_R3DPRIMEでQUALITYへ上書きしたことの
    regression test(¥0、Fableラベル判定の反映)。"""

    def test_a5_1_excluded_from_safety_critical(self):
        self.assertNotIn("A5-1", r3d.SAFETY_CRITICAL_SUB_IDS)

    def test_a5_1_correct_label_is_quality(self):
        self.assertEqual(r3d.CORRECT_LABEL_OVERRIDES_R3DPRIME.get("A5-1"), "QUALITY")

    def test_a5_0_still_safety_critical(self):
        # A5-0(同一グループの別claim)はSafety-critical扱いのまま。
        self.assertIn("A5-0", r3d.SAFETY_CRITICAL_SUB_IDS)


class TestStage1FreshWithMisconceptionPrincipleDoesNotTouchSharedBudgetFile(unittest.TestCase):
    """委任_28事故是正のregression test(¥0): `stage1_fresh_with_
    misconception_principle`が、実際にrunner自身の固定`BUDGET_STATE_
    PATH`ファイルへ一切書き込まないことを確認する(委任_28実測中に本関数
    経由でrep15の既存budget state証跡を一時的に上書きする事故が発生し、
    `git checkout`で復元した。再発防止として、本関数自体がファイル書き
    込みの副作用を持たない設計へ是正済みであることをファイルI/Oの有無で
    直接検証する)。"""

    def test_does_not_write_to_runner_budget_state_path(self):
        def fake_check(client, ledger, article, model, variant, include_related_fact_id=False,
                       source_article_text=None, developer_message_override=None):
            return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": []},
                    "usage": {"input_tokens": 1, "output_tokens": 1}, "prompt": "p"}

        fixture = {"ledger_text": "L", "article_text": "A"}
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        write_calls = []
        with mock.patch.object(runner.trial, "run_trial_deviation_check", side_effect=fake_check), \
             mock.patch.object(runner, "save_budget_state", side_effect=lambda s: write_calls.append(s)):
            result = runner.stage1_fresh_with_misconception_principle(
                None, state, [0], [], "label", fixture)
        self.assertEqual(write_calls, [], "stage1_fresh_with_misconception_principleはsave_budget_state"
                                           "(runner固定pathへの書き込み)を一切呼び出してはならない")
        self.assertEqual(result["overall_status"], "LEDGER_COMPLIANT")
        self.assertEqual(state["cumulative_calls"], 1)
        self.assertGreater(state["cumulative_jpy"], 0.0)


class TestMisconceptionPrincipleRubricV4(unittest.TestCase):
    """委任_29 Part1: RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V4
    (Meta-1/Meta-2のfalse downgrade是正)のregression test(¥0)。
    既存V3定数は変更していないことも併せて確認する。"""

    def test_v4_extends_v3_with_new_clarification_only(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4.startswith(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V3))
        self.assertIn("条件付きの可能性", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4)
        self.assertIn("certaintyの強化", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4)

    def test_v3_unchanged(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertIn("当事者関係(カウンターパート)の取り違え", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V3)
        self.assertNotIn("条件付きの可能性", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V3)

    def test_rubric_v4_combines_base_and_text(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V4.startswith(
                s2c.RUBRIC_R3_TRIPLE_PRIME))
        self.assertIn(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4,
                       s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V4)


class TestMisconceptionPrincipleRubricV5(unittest.TestCase):
    """委任_31 Part1(b)(design書§4-24): RUBRIC_R3_TRIPLE_PRIME_WITH_
    MISCONCEPTION_PRINCIPLE_V5(neg1の不要Rewrite是正、body rubric側の
    防御層)のregression test(¥0)。既存V4定数は変更していないことも
    併せて確認する。"""

    def test_v5_extends_v4_with_new_clarification_only(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5.startswith(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4))
        self.assertIn("受け手(読者・利用者)側の", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5)
        self.assertIn("新しい具体的Factの追加ではありません", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5)

    def test_v4_unchanged(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertIn("条件付きの可能性", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4)
        self.assertNotIn("受け手(読者・利用者)側の", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V4)

    def test_rubric_v5_combines_base_and_text(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V5.startswith(
                s2c.RUBRIC_R3_TRIPLE_PRIME))
        self.assertIn(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5,
                       s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V5)


class TestMisconceptionPrincipleRubricV6(unittest.TestCase):
    """委任_33(design書§4-25): RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_
    PRINCIPLE_V6(広いTrial iteration8で検出したB3[HF-007]/A2A3-0[HF-003]
    誤降格是正、許容/NG対比例示の追加)のregression test(¥0)。既存V5定数は
    変更していないことも併せて確認する。"""

    def test_v6_extends_v5_with_new_clarification_only(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6.startswith(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5))
        self.assertIn("自然な接続", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6)
        self.assertIn("支払義務者は未提示", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6)

    def test_v5_unchanged(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertIn("受け手(読者・利用者)側の", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5)
        self.assertNotIn("支払義務者は未提示", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V5)

    def test_rubric_v6_combines_base_and_text(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(
            s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V6.startswith(
                s2c.RUBRIC_R3_TRIPLE_PRIME))
        self.assertIn(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6,
                       s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V6)


class TestSafetyCriticalMisdowngradeDetection(unittest.TestCase):
    """委任_33(design書§8-x): `detect_safety_critical_misdowngrades`/
    `aggregate_measurements`の`silent_pass_candidate`自動検知のregression
    test(¥0、ネットワーク呼び出しなし、合成instance_resultsのみ使用)。
    旧実装は常に0を返す非稼働プレースホルダだった(委任_32 REPORT§30-3C)。"""

    def _fake_instance(self, instance_id, cycles):
        return {
            "instance_id": instance_id, "group": "test", "expected_group_label": "",
            "final_state": "RESOLVED_STAGE2_DOWNGRADE", "stage4_reason": None,
            "cycles": cycles, "stage1_call_used": False, "stage1_recall_miss_substituted": False,
            "s1u_screen_used": False, "s1u_additional_blocking_count": 0,
            "s1u_additional_block": False, "s1u_additional_block_label": None,
            "call_log": [], "total_cost_jpy": 0.0, "total_calls": 0, "elapsed_seconds": 0.0,
        }

    def test_detects_b3_misdowngrade(self):
        r = self._fake_instance("bgroup_B3", [{"stage2_results": [
            {"claim_text": "...so the flashy 20% plan left the stage...",
             "related_fact_id": "HF-007", "materiality": "QUALITY",
             "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        rows = runner.detect_safety_critical_misdowngrades([r])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sub_id"], "B3")
        self.assertEqual(rows[0]["instance_id"], "bgroup_B3")

    def test_detects_a2a3_0_misdowngrade(self):
        r = self._fake_instance("safety_A2A3", [{"stage2_results": [
            {"claim_text": "The idea was that those carrying the cargo would repay the money.",
             "related_fact_id": "HF-003", "materiality": "QUALITY",
             "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        rows = runner.detect_safety_critical_misdowngrades([r])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["sub_id"], "A2A3-0")

    def test_no_false_positive_when_blocking_maintained(self):
        r = self._fake_instance("bgroup_B3", [{"stage2_results": [
            {"claim_text": "...so the flashy 20% plan left the stage...",
             "related_fact_id": "HF-007", "materiality": "BLOCKING",
             "llm_materiality": "BLOCKING", "floor_reason": None},
        ]}])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([r]), [])

    def test_no_false_positive_for_unrelated_fact_id_same_instance(self):
        # safety_A5のA5-1(MUSE-HC-012、非Safety-critical)がA5-0と同じ
        # related_fact_idを共有するため、text_substringでの区別が必須
        # (混同するとA5-1の正当なQUALITY/ACCEPTABLEを誤検出する)。
        r = self._fake_instance("safety_A5", [{"stage2_results": [
            {"claim_text": "Meta executives admitted that starting the test "
                            "without a proper explanation was a mistake.",
             "related_fact_id": "MUSE-HC-012", "materiality": "QUALITY",
             "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([r]), [])

    def test_instance_not_in_defs_is_ignored(self):
        r = self._fake_instance("neg1_meta_b3prod_a2", [{"stage2_results": [
            {"claim_text": "irrelevant claim text", "related_fact_id": "HF-007",
             "materiality": "QUALITY", "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([r]), [])

    def test_aggregate_measurements_silent_pass_candidate_counts_distinct_claims(self):
        r1 = self._fake_instance("bgroup_B3", [{"stage2_results": [
            {"claim_text": "...so the flashy 20% plan left the stage...",
             "related_fact_id": "HF-007", "materiality": "QUALITY",
             "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        r2 = self._fake_instance("safety_A2A3", [{"stage2_results": [
            {"claim_text": "The idea was that those carrying the cargo would repay the money.",
             "related_fact_id": "HF-003", "materiality": "QUALITY",
             "llm_materiality": "QUALITY", "floor_reason": None},
        ]}])
        measurements = runner.aggregate_measurements([r1, r2])
        self.assertEqual(measurements["escalation_zero_breakdown"]["silent_pass_candidate"], 2)
        self.assertEqual(
            len(measurements["escalation_zero_breakdown"]["silent_pass_candidate_rows"]), 2)

    def test_aggregate_measurements_silent_pass_candidate_zero_when_safe(self):
        r1 = self._fake_instance("bgroup_B3", [{"stage2_results": [
            {"claim_text": "...so the flashy 20% plan left the stage...",
             "related_fact_id": "HF-007", "materiality": "BLOCKING",
             "llm_materiality": "BLOCKING", "floor_reason": None},
        ]}])
        measurements = runner.aggregate_measurements([r1])
        self.assertEqual(measurements["escalation_zero_breakdown"]["silent_pass_candidate"], 0)

    def test_iter8_real_data_detects_exactly_two_misdowngrades(self):
        # 委任_32実データ(er052_output/open233_self_recovery_flow_runner_01_
        # iter8/)に本関数を適用し、報告済みの2件(B3 2/2、A2A3-0 1/2)が
        # 自動検出されることを実データで確認する(¥0、新規API呼び出しなし)。
        base = "er052_output/open233_self_recovery_flow_runner_01_iter8"
        instance_results = []
        for sub in ("instances_s1", "instances_s2"):
            for iid in ("bgroup_B3", "safety_A2A3"):
                path = os.path.join(base, sub, f"{iid}.json")
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        instance_results.append(json.load(f))
        self.assertEqual(len(instance_results), 4)
        rows = runner.detect_safety_critical_misdowngrades(instance_results)
        distinct = {(row["instance_id"], row["sub_id"]) for row in rows}
        self.assertIn(("bgroup_B3", "B3"), distinct)
        self.assertIn(("safety_A2A3", "A2A3-0"), distinct)
        b3_rows = [row for row in rows if row["sub_id"] == "B3"]
        self.assertEqual(len(b3_rows), 2)  # sample1・sample2の両方(2/2)
        a2a3_rows = [row for row in rows if row["sub_id"] == "A2A3-0"]
        # sample2のcycle0内に同一claim(引用符付き/なし)が2回出現するため
        # raw行は2件(いずれもsample2由来、sample1は2件ともBLOCKINGで
        # 検出されない)。本番経路ではsample1/sample2は別々に
        # aggregate_measurements()へ渡される(本testのようにinstance_id
        # が同じ2サンプルを1リストへ混在させることはない)ため、報告済みの
        # 「1/2」はsample単位の集計で確認される(REPORT§30-3C)。
        self.assertEqual(len(a2a3_rows), 2)
        self.assertTrue(all(row["materiality"] == "QUALITY" for row in a2a3_rows))


class TestHookRubricV3(unittest.TestCase):
    """委任_29 Part2: HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V3
    (accept-1/accept-4のfalse block是正)のregression test(¥0)。"""

    def test_v3_extends_v2_with_new_clarification_only(self):
        self.assertTrue(
            s2h.HOOK_TIEBREAK_TEXT_V3.startswith(s2h.HOOK_TIEBREAK_TEXT))
        self.assertIn("自然な時間の流れ", s2h.HOOK_TIEBREAK_TEXT_V3)

    def test_v2_unchanged(self):
        self.assertNotIn("自然な時間の流れ", s2h.HOOK_TIEBREAK_TEXT)

    def test_rubric_v3_combines_base_and_text(self):
        self.assertTrue(
            s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V3.startswith(
                s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE))
        self.assertIn(s2h.HOOK_TIEBREAK_TEXT_V3, s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V3)


class TestMetaHookTallyScoringBugFix(unittest.TestCase):
    """委任_29 Part2: er052_open233_element_trial_meta_hook_01.tally_hook_rows()
    の符号反転バグ是正のregression test(¥0、本委任の初回実行で発覚)。
    旧実装は、ng群でBLOCKING(正しい)をfalse_passへ、accept/boundary群で
    非BLOCKING(正しい)をfalse_blockへ、それぞれ誤って計上していた。"""

    def _tally(self, accept_materiality_pairs, ng_materiality_pairs):
        import er052_open233_element_trial_meta_hook_01 as meta_hook

        # HOOK_CLAIMSの実claim群と同じ件数・group順を使い、n_runsぶんの
        # fake runを合成する(claim_indexはHOOK_CLAIMSの並び順と一致させる)。
        n_runs = max(c["n_runs"] for c in meta_hook.HOOK_CLAIMS)
        accept_idx = [i for i, c in enumerate(meta_hook.HOOK_CLAIMS) if c["group"] != "ng"]
        ng_idx = [i for i, c in enumerate(meta_hook.HOOK_CLAIMS) if c["group"] == "ng"]
        runs = []
        for run_idx in range(n_runs):
            judgments = []
            for pos, idx in enumerate(accept_idx):
                judgments.append({"claim_index": idx,
                                   "materiality": accept_materiality_pairs[pos % len(accept_materiality_pairs)],
                                   "basis": None})
            for pos, idx in enumerate(ng_idx):
                judgments.append({"claim_index": idx,
                                   "materiality": ng_materiality_pairs[pos % len(ng_materiality_pairs)],
                                   "basis": None})
            runs.append({"parsed": {"judgments": judgments}})
        return meta_hook.tally_hook_rows(runs)

    def test_all_correct_gives_zero_false_block_and_pass(self):
        # accept/boundary群が全てACCEPTABLE(正しい)、ng群が全てBLOCKING
        # (正しい)の場合、false_block/false_passは両方とも0でなければ
        # ならない(旧バグでは逆に非ゼロになっていた)。
        rows = self._tally(["ACCEPTABLE"], ["BLOCKING"])
        self.assertEqual(sum(r["false_block_count"] for r in rows), 0)
        self.assertEqual(sum(r["false_pass_count"] for r in rows), 0)

    def test_all_wrong_gives_nonzero_false_block_and_pass(self):
        # accept/boundary群が全てBLOCKING(誤り)、ng群が全てACCEPTABLE
        # (誤り)の場合、false_block/false_passは両方とも観測件数
        # (claimごとのn_runs合計)と一致する。
        import er052_open233_element_trial_meta_hook_01 as meta_hook
        rows = self._tally(["BLOCKING"], ["ACCEPTABLE"])
        n_accept_runs = sum(c["n_runs"] for c in meta_hook.HOOK_CLAIMS if c["group"] != "ng")
        n_ng_runs = sum(c["n_runs"] for c in meta_hook.HOOK_CLAIMS if c["group"] == "ng")
        self.assertEqual(sum(r["false_block_count"] for r in rows), n_accept_runs)
        self.assertEqual(sum(r["false_pass_count"] for r in rows), n_ng_runs)


class TestMisconceptionPrincipleDefaultWiring(unittest.TestCase):
    """委任_30 Part2(design書§0/§9-1「既定構成の確定」): 重大誤解原則V4を
    Stage1/Stage2(body)/Hook専用Stage2の既定経路へ配線したことの
    regression test(¥0、ネットワーク呼び出しなし)。"""

    def test_enable_flag_defaults_true(self):
        self.assertTrue(runner.ENABLE_MISCONCEPTION_PRINCIPLE_DEFAULT)

    def test_body_rubric_default_is_v6_when_enabled(self):
        # 委任_33(design書§4-25)でV5からV6へ昇格(広いTrial iteration8で
        # 検出したB3/A2A3-0誤降格の是正、rep18でSafety-critical 8claim/
        # Hormuz許容5・NG5/bgroup_B3・safety_A2A3のfull flow再確認済み)。
        self.assertEqual(runner.BODY_RUBRIC_DEFAULT,
                          s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V6)

    def test_hook_rubric_default_is_v4_when_enabled(self):
        self.assertEqual(runner.HOOK_RUBRIC_DEFAULT,
                          s2h.HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V4)

    def test_stage1_fresh_with_enumeration_default_developer_message_unchanged(self):
        # 既存呼び出し元(developer_message省略時)はvfl01既定のまま
        # (後方互換、既存iteration/rep証跡の再現性維持)。
        import inspect
        sig = inspect.signature(runner.stage1_fresh_with_enumeration)
        default = sig.parameters["developer_message"].default
        import er003_v1_en_direct_vfl_01_generate as vfl01
        self.assertEqual(default, vfl01.DEVIATION_DEVELOPER_MESSAGE)

    def test_stage1_fresh_with_enumeration_accepts_misconception_developer_message(self):
        captured = {}

        class FakeResp:
            output_text = '{"deviations": []}'
            id = "r1"
            model = "gpt-6-luna"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    captured["developer"] = kwargs["input"][0]["content"]
                    return FakeResp()

        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "check_budget", lambda s: None), \
             mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2p, "_extract_usage", lambda r: {}), \
             mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 0.0):
            runner.stage1_fresh_with_enumeration(
                FakeClient(), state, [0], [], "label", {"ledger_text": "(l)", "article_text": "(a)"},
                developer_message=trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)
        self.assertIn("重大誤解原則", captured["developer"])

    def test_run_stage2_body_group_uses_body_rubric_default(self):
        captured = {}

        class FakeResp:
            output_text = '{"judgments": []}'
            id = "r1"
            model = "gpt-6-luna"

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    captured["prompt"] = kwargs["input"][1]["content"]
                    return FakeResp()

        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": "(ledger)", "article_text": "Some body paragraph claim here.",
                   "source_article_text": None}
        claims = [{"claim_text": "Some body paragraph claim here.", "origin": "translation",
                   "related_fact_id": "X-1", "dev": {}}]
        with mock.patch.object(runner, "check_budget", lambda s: None), \
             mock.patch.object(runner, "record_call", lambda *a, **k: None):
            runner.run_stage2(FakeClient(), state, [0], [], "label", fixture, claims)
        self.assertIn("重大誤解原則", captured["prompt"])

    def test_run_instance_passes_misconception_principle_flag_to_stage1(self):
        # run_instance(fresh mode, use_enumeration_stage1既定True)が
        # misconception principle配線版developer_messageを使うことを、
        # stage1_fresh_with_enumerationへのcall引数で確認する(¥0、APIは
        # fakeで代替)。
        captured = {}

        def fake_stage1(client, state, consecutive_errors, call_log, label, fixture,
                         developer_message=None):
            captured["developer_message"] = developer_message
            return {"overall_status": "ACCEPTABLE_LLM", "deviations": []}

        inst = {
            "instance_id": "unit_test_instance", "group": "unit", "expected_group_label": "unit",
            "stage1_mode": "fresh",
            "fixture": {"ledger_text": "(l)", "article_text": "(a)", "source_article_text": None},
        }
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        # 委任_30(事故是正): run_instance()は末尾でsave_json()を呼び、
        # runner.OUT_DIR(固定path、過去delegationの既存証跡ディレクトリを
        # 指す)へ実ファイル書き込みを行う副作用を持つ。本委任の最初の実装で
        # この副作用を遮断し忘れ、rep15既存ディレクトリへunit_test_instance
        # .jsonを誤って書き込む事故が実際に発生した(直後に削除・復元済み)。
        # 以後、runner.save_jsonを必ずmockしてファイルI/Oを遮断する。
        with mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1), \
             mock.patch.object(runner, "save_json", lambda *a, **k: None):
            runner.run_instance(object(), state, [0], inst, stage1_cache={})
        self.assertEqual(captured["developer_message"],
                          trial.V4A_DEVELOPER_MSG_WITH_MISCONCEPTION_PRINCIPLE)

    def test_run_instance_use_misconception_principle_false_restores_old_developer_message(self):
        captured = {}

        def fake_stage1(client, state, consecutive_errors, call_log, label, fixture,
                         developer_message=None):
            captured["developer_message"] = developer_message
            return {"overall_status": "ACCEPTABLE_LLM", "deviations": []}

        import er003_v1_en_direct_vfl_01_generate as vfl01
        inst = {
            "instance_id": "unit_test_instance2", "group": "unit", "expected_group_label": "unit",
            "stage1_mode": "fresh",
            "fixture": {"ledger_text": "(l)", "article_text": "(a)", "source_article_text": None},
        }
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1), \
             mock.patch.object(runner, "save_json", lambda *a, **k: None):
            runner.run_instance(object(), state, [0], inst, stage1_cache={},
                                 use_misconception_principle=False)
        self.assertEqual(captured["developer_message"], vfl01.DEVIATION_DEVELOPER_MESSAGE)


class TestFloorFactIdBroadcastFix35(unittest.TestCase):
    """委任_35(design書§6-16、OPEN-233-SELF-RECOVERY-TRIAL-01 REPORT§32-3の
    追加原因(d)是正): deterministic floorは、Stage1が違反を体現する当該
    claim文に直接付与したflagにのみ適用し、`expand_same_fact_id_locations`
    (委任_20 W2)が同一related_fact_idの他claimへ複製したflag
    (detected_by_enumeration=True)には適用しない。rep19実測
    (`er052_output/open233_self_recovery_flow_runner_01_rep19/instances_s1/
    meta_run03_standard.json`cycle1)の実データdevをそのまま使う。"""

    # claim#2(原本、非enum): 「It said human staff made inappropriate
    # comments about race during calls. These calls were about trying to
    # lower internet or cable fees.」。違反を体現する当該claim文自体。
    VIOLATION_DEV = {
        "claim_in_article": "“It said human staff made inappropriate comments about race during calls. "
                             "These calls were about trying to lower internet or cable fees.”",
        "severity": "MAJOR", "changed_fact": True, "changed_scope": True, "changed_number": True,
        "changed_actor": False, "changed_negation": False, "changed_comparison": False, "changed_time": False,
        "unsupported_new_claim": True, "related_fact_id": "MUSE-HC-011",
        "same_fact_id_locations": [
            "News reports also cited one employee’s report.",
            "However, this is only one report. It would be wrong to say all contract workers did this.",
        ],
    }

    # claim#5(expand_same_fact_id_locationsによる複製、enum=True):
    # 「News reports also cited one employee's report.」。文面自体は単数
    # ("one")で正確であり、Stage2 LLM自身もACCEPTABLEと判定した
    # (rep19実測)が、floor波及でBLOCKINGへ強制されていた。
    BROADCAST_DEV = {
        **{k: v for k, v in VIOLATION_DEV.items() if k != "claim_in_article"},
        "claim_in_article": "News reports also cited one employee’s report.",
        "detected_by_enumeration": True,
        "enumeration_source_claim": VIOLATION_DEV["claim_in_article"],
    }

    def test_violation_claim_itself_still_forced_blocking_by_floor(self):
        # 違反を体現する当該claim文は、Safety側安全装置として引き続き
        # floorでBLOCKING(fail-closed維持、非回帰)。
        materiality, reason = runner.apply_floor("QUALITY", self.VIOLATION_DEV, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")
        self.assertEqual(reason, "deterministic_floor:changed_number")

    def test_broadcast_claim_not_forced_blocking_when_llm_says_acceptable(self):
        # 複製claim(detected_by_enumeration=True)は、Stage2 LLMが独立に
        # ACCEPTABLEと判定した場合、floorで強制BLOCKINGへ波及しない
        # (rep19実測のclaim#5誤分類の是正)。
        materiality, reason = runner.apply_floor("ACCEPTABLE", self.BROADCAST_DEV, "stage1_llm")
        self.assertEqual(materiality, "ACCEPTABLE")
        self.assertIsNone(reason)

    def test_broadcast_claim_still_blocking_if_llm_independently_says_so(self):
        # floorが波及しなくなっても、Stage2 LLMが複製claim自体を独立に
        # BLOCKINGと判定した場合はBLOCKINGのまま(fail-closedが失われて
        # いないことの確認、floor forcingを外しただけでllm判定は無変更)。
        materiality, reason = runner.apply_floor("BLOCKING", self.BROADCAST_DEV, "stage1_llm")
        self.assertEqual(materiality, "BLOCKING")
        self.assertIsNone(reason)

    def test_precheck_floor_unaffected_by_enumeration_flag(self):
        # precheck floor(detected_by=="precheck")はdetected_by_enumeration
        # の値に関わらず常にBLOCKING(既存のprecheck fail-closedは変更なし)。
        dev = dict(self.BROADCAST_DEV)
        materiality, reason = runner.apply_floor("ACCEPTABLE", dev, "precheck")
        self.assertEqual(materiality, "BLOCKING")
        self.assertEqual(reason, "precheck_floor")

    def test_floor_cited_variant_also_skips_broadcast_claim(self):
        ledger = "[VERIFIED] MUSE-HC-011: a contract worker reported one incident.\n"
        materiality, reason = runner.apply_floor_cited("ACCEPTABLE", self.BROADCAST_DEV, "stage1_llm", ledger)
        self.assertEqual(materiality, "ACCEPTABLE")
        self.assertIsNone(reason)


class TestRecheckFactIdEnumerationOnceOnly35(unittest.TestCase):
    """委任_35(design書§6-16): same_fact_id_locations列挙は初回Stage1
    検出時のみ行い、run_recheck()呼び出し(cycle番号に関わらず)では既定で
    再列挙しない(enable_fact_id_enumeration既定False)。"""

    def test_default_prompt_omits_enumeration_instruction(self):
        captured = {}

        class _FakeResp:
            output_text = json.dumps({
                "overall_status": "LEDGER_COMPLIANT", "deviations": [],
                "prior_issues_resolved": [{"index": 0, "resolved": True, "explanation": "fixed"}],
            })

        class _FakeResponses:
            def create(self, **kwargs):
                captured["prompt"] = kwargs["input"][1]["content"]
                return _FakeResp()

        class _FakeClient:
            responses = _FakeResponses()

        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": "[VERIFIED] HF-001: x\n", "source_article_text": None}
        runner.run_recheck(_FakeClient(), state, [0], [], "test_recheck", fixture,
                            "Some article text.", [{"fact_id": "HF-001", "claim_in_article": "x",
                                                     "issue": "i", "explanation": "e"}])
        self.assertNotIn("same_fact_id_locations", captured["prompt"])

    def test_default_does_not_expand_deviations(self):
        dev_with_locations = {
            "claim_in_article": "A claim.", "severity": "MAJOR", "related_fact_id": "HF-001",
            "same_fact_id_locations": ["Another sentence stating the same fact."],
        }
        article_text = "A claim. Another sentence stating the same fact."

        class _FakeResp:
            output_text = json.dumps({
                "overall_status": "LEDGER_DEVIATION", "deviations": [dev_with_locations],
                "prior_issues_resolved": [{"index": 0, "resolved": False, "explanation": "still there"}],
            })

        class _FakeResponses:
            def create(self, **kwargs):
                return _FakeResp()

        class _FakeClient:
            responses = _FakeResponses()

        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": "[VERIFIED] HF-001: x\n", "source_article_text": None}
        result = runner.run_recheck(_FakeClient(), state, [0], [], "test_recheck", fixture, article_text,
                                     [{"fact_id": "HF-001", "claim_in_article": "A claim.",
                                       "issue": "i", "explanation": "e"}])
        self.assertEqual(len(result["deviations"]), 1)
        self.assertFalse(any(d.get("detected_by_enumeration") for d in result["deviations"]))

    def test_explicit_true_restores_old_enumeration_behavior(self):
        dev_with_locations = {
            "claim_in_article": "A claim.", "severity": "MAJOR", "related_fact_id": "HF-001",
            "same_fact_id_locations": ["Another sentence stating the same fact."],
        }
        article_text = "A claim. Another sentence stating the same fact."

        class _FakeResp:
            output_text = json.dumps({
                "overall_status": "LEDGER_DEVIATION", "deviations": [dev_with_locations],
                "prior_issues_resolved": [{"index": 0, "resolved": False, "explanation": "still there"}],
            })

        class _FakeResponses:
            def create(self, **kwargs):
                return _FakeResp()

        class _FakeClient:
            responses = _FakeResponses()

        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": "[VERIFIED] HF-001: x\n", "source_article_text": None}
        result = runner.run_recheck(_FakeClient(), state, [0], [], "test_recheck", fixture, article_text,
                                     [{"fact_id": "HF-001", "claim_in_article": "A claim.",
                                       "issue": "i", "explanation": "e"}],
                                     enable_fact_id_enumeration=True)
        self.assertEqual(len(result["deviations"]), 2)
        self.assertTrue(any(d.get("detected_by_enumeration") for d in result["deviations"]))


class TestInOneLineHeadingDegenerateGuard35(unittest.TestCase):
    """委任_35(design書§6-16): 「## In one line」見出し自体の削除・消失を
    Rewrite失敗(iol_degenerate)として検出する(rep19実測cycle3、見出し行
    ごと消失した事例、REPORT§32参照)。"""

    def test_in_one_line_heading_removed_is_degenerate(self):
        before = "# T\n\nHook para.\n\n## In one line\nSome calls were handled by humans.\n"
        after = "# T\n\nHook para.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertTrue(result["iol_degenerate"])
        self.assertTrue(result["section_role_violated"])
        self.assertIn("in_one_line_degenerate", result["reasons"])

    def test_in_one_line_heading_unchanged_is_not_degenerate(self):
        text = "# T\n\nHook para.\n\n## In one line\nSome calls were handled by humans.\n"
        result = runner.measure_section_role_violation(text, text)
        self.assertFalse(result["iol_degenerate"])
        self.assertFalse(result["section_role_violated"])

    def test_in_one_line_text_changed_but_heading_kept_is_not_degenerate(self):
        before = "# T\n\nHook para.\n\n## In one line\nOld summary sentence.\n"
        after = "# T\n\nHook para.\n\n## In one line\nNew summary sentence here now.\n"
        result = runner.measure_section_role_violation(before, after)
        self.assertFalse(result["iol_degenerate"])

    def test_run_instance_source_contains_iol_degenerate_hard_block(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('final_section_role.get("iol_degenerate")', src)


if __name__ == "__main__":
    unittest.main()
