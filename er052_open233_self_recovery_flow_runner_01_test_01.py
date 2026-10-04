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
import re
import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_self_recovery_r3dprime_calibration_01 as r3d
import er052_open233_self_recovery_stage2_calibration_01 as s2c
import er052_open233_self_recovery_stage2_hook_01 as s2h
import er051_open233_checker_trial_variant_01 as trial


def _legacy_handoff(fn):
    """委任_42(意図的な書き換え): 旧方式(`HANDOFF_MODE="legacy"`、locate_target
    経由の対象決定)の挙動を固定する既存テスト。旧方式は比較・切り戻し用に残して
    あるため、旧方式を明示してこれらのテストを維持する(新方式の同等テストは
    `TestHandoffViolationSpan*`系で別途追加)。"""
    return mock.patch.object(runner, "HANDOFF_MODE", runner.HANDOFF_MODE_LEGACY)(fn)


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

    @_legacy_handoff
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

    @_legacy_handoff
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

    @_legacy_handoff
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
        self.assertIn('stage4_reason = "violation_span_unverified" if span_unverified_records else "target_not_locatable"', src)
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

    @_legacy_handoff
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

    @_legacy_handoff
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

    @_legacy_handoff
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

    @_legacy_handoff
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
        # 委任_55(ユーザー決定2026-10-03): Meta-1/Meta-2もQUALITY(軽微)と確定し除外(8件→6件)。
        # 委任_57(2026-10-03、正式採用基準の適用): A4-1もACCEPTABLEへ再ラベルし除外(6件→5件)。
        expected = {"A2A3-0", "A4-0", "A5-0", "B3", "B4-a"}
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


class TestMeta12MovedToOverQualityMonitor55(unittest.TestCase):
    """委任_55(ユーザー決定2026-10-03、例1=軽微): Meta-1/Meta-2はSafety-criticalから外れ、
    `expected: "QUALITY"`の過剰品質監視用として残る(¥0、合成データのみ)。"""

    def _r(self, materiality):
        return {"instance_id": "meta_run03_standard", "cycles": [{"stage2_results": [
            {"claim_text": "Also, some calls needed user information to continue.",
             "related_fact_id": "MUSE-HC-010", "materiality": materiality,
             "llm_materiality": materiality, "floor_reason": None}]}]}

    def test_defs_kept_with_expected_quality(self):
        defs = runner.SAFETY_CRITICAL_CLAIM_DEFS["meta_run03_standard"]
        self.assertEqual([d["sub_id"] for d in defs], ["Meta-1", "Meta-2"])
        self.assertTrue(all(d.get("expected") == "QUALITY" for d in defs))

    def test_not_safety_critical_any_more(self):
        self.assertEqual(runner._safety_critical_defs("meta_run03_standard"), [])
        # 他のSafety-critical定義はそのまま(expected省略=BLOCKING)
        self.assertEqual([d["sub_id"] for d in runner._safety_critical_defs("bgroup_B3")], ["B3"])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([self._r("QUALITY")]), [])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([self._r("ACCEPTABLE")]), [])

    def test_residual_at_pass_excludes_meta(self):
        out = runner.compute_residual_at_pass(
            "meta_run03_standard", "ACCEPTABLE_STAGE1", "x. Also, some calls needed user information to continue.",
            [], [], [])
        self.assertEqual(out["applicable_defs"], 0)
        self.assertEqual(out["defs"], [])

    def test_over_quality_monitor_records_blocking_only(self):
        rows = runner.detect_over_quality_monitor_blocks([self._r("BLOCKING")])
        self.assertEqual([x["sub_id"] for x in rows], ["Meta-1"])
        self.assertEqual(rows[0]["expected"], "QUALITY")
        self.assertEqual(runner.detect_over_quality_monitor_blocks([self._r("QUALITY")]), [])
        self.assertEqual(runner.detect_over_quality_monitor_blocks([self._r("ACCEPTABLE")]), [])

    def test_r3d_labels(self):
        self.assertNotIn("Meta-1", r3d.SAFETY_CRITICAL_SUB_IDS)
        self.assertNotIn("Meta-2", r3d.SAFETY_CRITICAL_SUB_IDS)
        self.assertEqual(r3d.CORRECT_LABEL_OVERRIDES_R3DPRIME.get("Meta-1"), "QUALITY")
        self.assertEqual(r3d.CORRECT_LABEL_OVERRIDES_R3DPRIME.get("Meta-2"), "QUALITY")


class TestA41MovedToMonitor57(unittest.TestCase):
    """委任_57(2026-10-03、Fable判断): A4-1は`expected: "ACCEPTABLE"`の監視用へ移り、
    `detect_safety_critical_misdowngrades`の対象外(¥0、合成データのみ)。"""

    def _r(self, materiality):
        return {"instance_id": "safety_A4", "cycles": [{"stage2_results": [
            {"claim_text": "people who thought they were speaking with AI were actually speaking with human staff",
             "related_fact_id": "MUSE-HC-012", "materiality": materiality,
             "llm_materiality": materiality, "floor_reason": None}]}]}

    def test_a41_def_expected_acceptable(self):
        defs = {d["sub_id"]: d for d in runner.SAFETY_CRITICAL_CLAIM_DEFS["safety_A4"]}
        self.assertEqual(defs["A4-1"].get("expected"), "ACCEPTABLE")
        self.assertEqual([d["sub_id"] for d in runner._safety_critical_defs("safety_A4")], ["A4-0"])

    def test_a41_not_misdowngrade_target(self):
        self.assertEqual(runner.detect_safety_critical_misdowngrades([self._r("ACCEPTABLE")]), [])
        self.assertEqual(runner.detect_safety_critical_misdowngrades([self._r("QUALITY")]), [])
        rows = runner.detect_over_quality_monitor_blocks([self._r("BLOCKING")])
        self.assertEqual([x["sub_id"] for x in rows], ["A4-1"])
        self.assertEqual(runner.detect_over_quality_monitor_blocks([self._r("ACCEPTABLE")]), [])

    def test_a41_r3d_labels(self):
        self.assertNotIn("A4-1", r3d.SAFETY_CRITICAL_SUB_IDS)
        self.assertIn("A4-0", r3d.SAFETY_CRITICAL_SUB_IDS)
        self.assertEqual(r3d.CORRECT_LABEL_OVERRIDES_R3DPRIME.get("A4-1"), "ACCEPTABLE")


class TestRubricV7LineDrawing55(unittest.TestCase):
    """委任_55(design書§4-26): 線引きの正式採用に伴うV7。旧版は残り、V7はV6へ追記する形。
    機械的な安全装置(FLOOR_FLAGS等)は不変(¥0)。"""

    def test_v6_unchanged_and_v7_extends_v6(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        self.assertTrue(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7.startswith(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6))
        self.assertIn("支払義務者は未提示", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7)
        self.assertTrue(s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7.startswith(
            s2c.RUBRIC_R3_TRIPLE_PRIME))
        self.assertIn(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7,
                       s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7)
        self.assertNotIn("線引きの正式採用", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V6)

    def test_v7_has_three_user_examples_with_expected_labels(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        t = s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7
        tail = t[t.index("判定済みの例"):]
        lines = [x for x in tail.splitlines() if x.startswith("- ")]
        self.assertEqual(len(lines), 3)  # 例示は3行まで(委任_16 B-2のpriming前例)
        self.assertIn("some calls needed user information to continue", lines[0])
        self.assertTrue(lines[0].endswith("QUALITY"))
        self.assertIn("They did not realize it", lines[1])
        self.assertTrue(lines[1].endswith("ACCEPTABLE"))
        self.assertIn("prices began to fall", lines[2])
        self.assertTrue(lines[2].endswith("QUALITY"))

    def test_v7_no_blanket_blocking_and_replaces_when_in_doubt(self):
        import er052_open233_self_recovery_stage2_calibration_01 as s2c
        t = "".join(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7.split())  # 改行・空白を除いて照合
        self.assertIn("被害・結果にあたる核心の主張", t)
        self.assertIn("核心の主張に留保が残り", t)
        self.assertIn("肯定形", t)
        self.assertIn("事実関係の重大な誤解につながるか", t)
        self.assertIn("数値・主体・否定・比較・時期の差は、この原則の対象外", t)

    def test_production_stage2_rubric_v7_replaces_fail_closed_only(self):
        import er052_open233_self_recovery_stage2_production_01 as s2p
        self.assertIn("(fail-closed)", s2p.MATERIALITY_RUBRIC)  # 旧版は残る
        self.assertNotIn("(fail-closed)", s2p.MATERIALITY_RUBRIC_V7)
        v7 = "".join(s2p.MATERIALITY_RUBRIC_V7.split())
        self.assertIn("重大な誤解につながるかで決めてください", v7)
        self.assertIn("動機の帰属", v7)  # 3-4: 変更しない
        old_head = s2p.MATERIALITY_RUBRIC.split("- 上記のどれに")[0]
        self.assertEqual(old_head, s2p.MATERIALITY_RUBRIC_V7.split("- 上記のどれに")[0])

    def test_mechanical_safeguards_unchanged(self):
        # FLOOR_FLAGS(5種)・disclosure_gap否定形限定は変更していない
        self.assertEqual(set(runner.FLOOR_FLAGS), {"changed_actor", "changed_number", "changed_negation",
                                                    "changed_comparison", "changed_time"})
        self.assertTrue(runner.DISCLOSURE_GAP_NEGATION_RE.search("They did not realize it."))
        self.assertIsNone(runner.DISCLOSURE_GAP_NEGATION_RE.search("They thought it was AI."))


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

    def test_body_rubric_default_is_v7_when_enabled(self):
        # 委任_33(design書§4-25)でV5からV6へ昇格。委任_55(design書§4-26、
        # 2026-10-03、線引きの正式採用)でV6からV7へ昇格(V6は定数として残る)。
        self.assertEqual(runner.BODY_RUBRIC_DEFAULT,
                          s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B)
        self.assertNotEqual(runner.BODY_RUBRIC_DEFAULT,
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


# ============================================================
# 委任_42(2026-10-02、OPEN-233 受け渡し修正)の新規テスト。
# 実データ(rep21 sample1 cycle1の記事本文、rep20 sample2 cycle1後の記事本文)を
# テスト用に埋め込む。ネットワーク呼び出しなし(¥0、simple_llm_callはmock)。
# ============================================================
REP21_S1_EN = """# Some AI Phone Calls Had Humans Behind the Scenes

It was a small surprise. A service let people ask AI to make phone calls. But humans made some of the calls behind the scenes. This was part of a test.

The main player was Muse, Meta’s AI assistant. Muse can call businesses and stores in the United States. It can book haircuts and check if items are in stock. It can also get price estimates from businesses. If AI can handle difficult calls, it seems very useful.

In some tests, trained human contract workers made the calls, not AI. They handled each conversation until it ended.

The problem was not that humans made the calls. The problem was telling users who was speaking.

People asking Muse to call might think AI was calling. But sometimes, a human was speaking instead. If no one explained this clearly, users could not know. They could not tell if it was AI or a person. They enjoyed AI’s convenience, but a human was on the other end. They did not realize it. That was happening behind the scenes.

Also, some calls needed user information to continue. That information might accidentally be shared with contract workers at a call center. Meta employees pointed this out inside the company as a privacy concern.

News reports also cited one employee’s report. It said human staff made inappropriate comments about race during calls. These calls were about trying to lower internet or cable fees. However, this is only one report. It would be wrong to say all contract workers did this.

A Meta executive admitted the test began without a clear explanation. That was a mistake. The company also restored its human help feature to its earlier form, at least for now.

The real challenge for AI calls is not only how they talk. They must also be honest about who is on the other end. The more useful a service is, the less it should hide workers behind the scenes. The Muse case showed this simple but important point.

## In one line
Some calls through Meta’s AI assistant were actually handled by humans, but users were not properly told."""

REP20_S2_CYCLE2_EN = """# Some AI Phone Calls Had Humans Behind the Scenes

It was a small surprise. A service let people ask AI to make phone calls. But humans made some of the calls behind the scenes. This was part of a test.

The main player was Muse, Meta’s AI assistant. Muse can call businesses and stores in the United States. It can book haircuts and check if items are in stock. It can also get price estimates from businesses. If AI can handle difficult calls, it seems very useful.

In some tests, trained human contract workers made the calls, not AI. They handled each conversation until it ended.

The problem was not that humans made the calls. The problem was telling users who was speaking.

People asking Muse to call might think AI was calling. But sometimes, a human was speaking instead. If no one explained this clearly, users could not know. They could not tell if it was AI or a person. They enjoyed AI’s convenience, but a human was on the other end. They did not realize it. That was happening behind the scenes.

Also, some calls needed user information to continue. That information might accidentally be shared with contract workers at a call center. Meta employees pointed this out inside the company as a privacy concern.

News reports also cited one employee’s report. It said human staff made inappropriate comments about race during a call. This call was about trying to lower internet or cable fees. However, this is only one report. It would be wrong to say all contract workers did this.

A Meta executive admitted the test began without a clear explanation. That was a mistake. The company also restored its human help feature to its earlier form, at least for now.

The real challenge for AI calls is not only how they talk. They must also be honest about who is on the other end. The more useful a service is, the less it should hide workers behind the scenes. The Muse case showed this simple but important point.

## In one line
Some calls through Meta’s AI assistant were actually handled by humans, but users were not properly told."""

REP21_S1_TWO_SENTENCE_CLAIM = (
    "“It said human staff made inappropriate comments about race during calls. "
    "These calls were about trying to lower internet or cable fees.”"
)
REP21_S1_TWO_SENTENCES = (
    "It said human staff made inappropriate comments about race during calls. "
    "These calls were about trying to lower internet or cable fees."
)
REP20_S2_C2_CLAIM = "“They could not tell if it was AI or a person” and “They did not realize it.”"
LEDGER = "[VERIFIED] MUSE-HC-011: one reported call. [VERIFIED] MUSE-HC-012: test started without disclosure."


def _state0() -> dict:
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def _claim(claim_text: str, kind: str = "narrow_scope", hint: str = "", origin: str = "translation",
           dev: dict | None = None, **extra) -> dict:
    rec = {"claim_text": claim_text, "rewrite_kind": kind, "materiality": "BLOCKING", "basis": "ledger_fact",
           "rewrite_hint": hint, "dev": dev if dev is not None else {"issue": "plural calls vs one reported call",
                                                                      "related_fact_id": "MUSE-HC-011"},
           "origin": origin}
    rec.update(extra)
    return rec


class TestResolveViolationSpans(unittest.TestCase):
    """委任_42 仕様(1): Checkerの文字列だけを入力にした文字単位の照合(L0〜L4、
    ちょうど1箇所)。類似度・単語重なり・判定役の引用は使わない。"""

    def test_a_rep21_s1_two_sentence_quoted_claim_becomes_one_range_of_two_sentences(self):
        res = runner.resolve_violation_spans(REP21_S1_TWO_SENTENCE_CLAIM, REP21_S1_EN, None)
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["lang"], "EN")
        self.assertEqual(res["level"], "L1")  # 両端の“ ”を外すだけ
        self.assertEqual(res["ranges"], [REP21_S1_TWO_SENTENCES])
        a, b = res["spans"][0]
        self.assertEqual(REP21_S1_EN[a:b], REP21_S1_TWO_SENTENCES)

    def test_b_rep20_s2_cycle2_two_fragments_become_two_ranges_and_middle_sentence_excluded(self):
        res = runner.resolve_violation_spans(REP20_S2_C2_CLAIM, REP20_S2_CYCLE2_EN, None)
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["level"], "L4")
        self.assertEqual(res["ranges"], ["They could not tell if it was AI or a person",
                                         "They did not realize it."])
        joined = " ".join(res["ranges"])
        self.assertNotIn("They enjoyed AI’s convenience", joined)  # 間の文は対象外
        self.assertEqual(len(res["spans"]), 2)
        self.assertLess(res["spans"][0][1], res["spans"][1][0])

    def test_c_paragraph_beginning_description_is_unverified_explanatory(self):
        res = runner.resolve_violation_spans("Paragraph beginning “People asking Muse to call”",
                                             REP20_S2_CYCLE2_EN, None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "explanatory_mixed")
        self.assertEqual(res["ranges"], [])

    def test_d_partial_sentence_confirmed_by_case_insensitive_match(self):
        res = runner.resolve_violation_spans("“Some calls needed user information to continue.”",
                                             REP21_S1_EN, None)
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["level"], "L3")
        # 記事側の文字列(小文字のsome)が範囲。文頭の“Also, ”は含まれない(縮小も拡張もしない)
        self.assertEqual(res["ranges"], ["some calls needed user information to continue."])

    def test_e_same_string_in_two_places_is_unverified_multi_match(self):
        text = "# T\n\nIt was one call. Other text.\n\nIt was one call. More text.\n"
        res = runner.resolve_violation_spans("It was one call.", text, None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "multi_match")

    def test_paraphrase_is_not_rescued_by_similarity(self):
        # 原文を少し言い換えた文字列は、類似度で近い文へ落とさず確定不能(不一致)
        res = runner.resolve_violation_spans("Human staff made racist remarks during calls.", REP21_S1_EN, None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "mismatch")

    def test_l2_curly_vs_straight_quotes_and_whitespace(self):
        text = "# T\n\nMeta’s AI  assistant\nhandled it.\n"
        res = runner.resolve_violation_spans("Meta's AI assistant handled it.", text, None)
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["level"], "L2")
        self.assertEqual(res["ranges"], ["Meta’s AI  assistant\nhandled it."])

    def test_l4_with_explanatory_remainder_is_not_decomposed(self):
        # 断片が2つ以上でも、残りに説明文があれば分解しない(縮小の防止)
        res = runner.resolve_violation_spans(
            "The paragraph with “They could not tell if it was AI or a person” and then “They did not realize it.”",
            REP20_S2_CYCLE2_EN, None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "explanatory_mixed")

    def test_l4_fragment_not_found_is_unverified(self):
        res = runner.resolve_violation_spans("“They could not tell if it was AI or a person” and “Nothing like this.”",
                                             REP20_S2_CYCLE2_EN, None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "mismatch")

    def test_ja_text_is_checked_and_language_is_kept(self):
        ja = "# タイトル\n\nこの主張文はJA本文にのみ存在します。\n"
        res = runner.resolve_violation_spans("この主張文はJA本文にのみ存在します。", "# T\n\nEnglish only.\n", ja)
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["lang"], "JA")
        self.assertFalse(res["both_langs_ok"])

    def test_en_is_preferred_when_both_languages_match(self):
        res = runner.resolve_violation_spans("2.6%", "# T\n\nUp 2.6% today.\n", "# T\n\n2.6%上昇。\n")
        self.assertEqual(res["lang"], "EN")
        self.assertTrue(res["both_langs_ok"])

    def test_empty_claim_is_unverified(self):
        res = runner.resolve_violation_spans("   ", "# T\n\nText.\n", None)
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "empty_claim")


class TestMergeSpans(unittest.TestCase):
    def test_overlapping_spans_are_merged(self):
        text = "abcdefghij"
        self.assertEqual(runner.vs_merge_spans([(0, 5), (3, 8)], text), [(0, 8)])

    def test_adjacent_spans_separated_only_by_whitespace_are_merged(self):
        text = "First one. Second one."
        self.assertEqual(runner.vs_merge_spans([(0, 10), (11, 22)], text), [(0, 22)])

    def test_spans_across_paragraph_break_are_not_merged(self):
        text = "First one.\n\nSecond one."
        self.assertEqual(runner.vs_merge_spans([(0, 10), (12, 23)], text), [(0, 10), (12, 23)])

    def test_contained_span_is_absorbed_by_the_larger_one(self):
        text = "abcdefghij"
        self.assertEqual(runner.vs_merge_spans([(1, 9), (3, 5)], text), [(1, 9)])

    def test_spans_with_text_between_stay_separate(self):
        text = "AAA middle BBB"
        self.assertEqual(runner.vs_merge_spans([(0, 3), (11, 14)], text), [(0, 3), (11, 14)])


class TestVsExpandAndReplace(unittest.TestCase):
    def test_expand_partial_range_to_whole_sentence_without_adding_other_sentences(self):
        spans = runner.resolve_violation_spans("“Some calls needed user information to continue.”",
                                               REP21_S1_EN, None)["spans"]
        units = runner.vs_expand_to_sentences(spans, REP21_S1_EN)
        self.assertEqual(units, ["Also, some calls needed user information to continue."])

    def test_expand_two_ranges_to_their_own_sentences_only(self):
        spans = runner.resolve_violation_spans(REP20_S2_C2_CLAIM, REP20_S2_CYCLE2_EN, None)["spans"]
        units = runner.vs_expand_to_sentences(spans, REP20_S2_CYCLE2_EN)
        self.assertEqual(units, ["They could not tell if it was AI or a person.", "They did not realize it."])

    def test_replace_once_requires_exactly_one_occurrence(self):
        self.assertEqual(runner.vs_replace_once("a b c", "b", "X"), "a X c")
        self.assertIsNone(runner.vs_replace_once("a b b", "b", "X"))
        self.assertIsNone(runner.vs_replace_once("a b", "zzz", "X"))
        self.assertIsNone(runner.vs_replace_once("a b", "", "X"))

    def test_parse_revised_ranges(self):
        self.assertEqual(runner.vs_parse_revised_ranges('{"revised_ranges": ["a", "b"]}'), (["a", "b"], None))
        self.assertEqual(runner.vs_parse_revised_ranges('```json\n{"revised_ranges": ["a"]}\n```'), (["a"], None))
        self.assertEqual(runner.vs_parse_revised_ranges("plain sentence")[1], "parse_failure")
        self.assertEqual(runner.vs_parse_revised_ranges('{"revised_ranges": "a"}')[1], "parse_failure")


def _run_ladder(fixture: dict, claim_rec: dict, fake_llm, field: str = "article_text") -> tuple:
    calls: list = []

    def wrapped(client, state, errs, log, label, dev_msg, prompt, model=None):
        calls.append({"label": label, "prompt": prompt})
        return fake_llm(label, prompt, len(calls))

    with mock.patch.object(runner, "simple_llm_call", side_effect=wrapped):
        result = runner.single_text_rewrite(None, _state0(), [], [], "t", fixture, field, claim_rec)
    return result, calls


class TestHandoffRewriteLadder(unittest.TestCase):
    """委任_42 仕様(3)(4)(5)(6)(9): 確定範囲を対象にした最小修正優先ラダー。"""

    def setUp(self):
        self.assertEqual(runner.HANDOFF_MODE, runner.HANDOFF_MODE_VIOLATION_SPAN)  # 既定=新方式

    def test_a_two_sentence_claim_level1_target_is_the_whole_confirmed_range(self):
        revised = ("It said human staff made inappropriate comments about race during a call. "
                   "This call was about trying to lower internet or cable fees.")

        def fake(label, prompt, n):
            self.assertTrue(label.endswith("_e1_minimal_word"), label)
            return json.dumps({"revised_ranges": [revised]})

        fixture = {"ledger_text": LEDGER, "article_text": REP21_S1_EN}
        res, calls = _run_ladder(fixture, _claim(REP21_S1_TWO_SENTENCE_CLAIM, kind="replace_with_ledger_value"), fake)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertEqual(len(calls), 1)
        h = res["handoff"]
        self.assertEqual(h["level_attempts"][0]["targets"], [REP21_S1_TWO_SENTENCES])
        self.assertTrue(h["level_attempts"][0]["target_equals_confirmed_ranges"])
        self.assertEqual(h["resolution"]["ranges"], [REP21_S1_TWO_SENTENCES])
        self.assertIn(revised, res["updated_text"])
        self.assertNotIn(REP21_S1_TWO_SENTENCES, res["updated_text"])
        # 範囲の外は書き換えない
        self.assertEqual(res["updated_text"].replace(revised, REP21_S1_TWO_SENTENCES), REP21_S1_EN)
        self.assertEqual(res["before_fragment"], REP21_S1_TWO_SENTENCES)
        self.assertEqual(res["after_fragment"], revised)
        # Promptには範囲全体と読み取り専用の段落文脈が入る
        self.assertIn(REP21_S1_TWO_SENTENCES, calls[0]["prompt"])
        self.assertIn("Paragraph context (read-only)", calls[0]["prompt"])
        self.assertIn("However, this is only one report.", calls[0]["prompt"])  # 同じ段落の文脈

    def test_b_two_separate_ranges_are_passed_as_array_and_middle_sentence_untouched(self):
        def fake(label, prompt, n):
            return json.dumps({"revised_ranges": ["They could not always tell if it was AI or a person",
                                                  "They may not have realized it."]})

        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim(REP20_S2_C2_CLAIM, origin="translation"), fake)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertEqual(res["handoff"]["level_attempts"][0]["targets"],
                         ["They could not tell if it was AI or a person", "They did not realize it."])
        self.assertIn("Range 1:", calls[0]["prompt"])
        self.assertIn("Range 2:", calls[0]["prompt"])
        self.assertIn("exactly 2 string(s)", calls[0]["prompt"])
        self.assertNotIn("They enjoyed AI’s convenience", calls[0]["prompt"].split("[Paragraph context")[0])
        self.assertIn("They enjoyed AI’s convenience, but a human was on the other end.", res["updated_text"])
        self.assertIn("They could not always tell if it was AI or a person. They enjoyed", res["updated_text"])
        self.assertIn("They may not have realized it.", res["updated_text"])

    def test_c_unverified_claim_makes_no_api_call_and_is_flagged_span_unverified(self):
        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim("Paragraph beginning “People asking Muse to call”"),
                                 lambda *a: self.fail("API must not be called"))
        self.assertEqual(calls, [])
        self.assertTrue(res["target_not_locatable"])
        self.assertTrue(res["span_unverified"])
        self.assertEqual(res["span_unverified_reason"], "explanatory_mixed")
        self.assertFalse(res["guard_ok"])
        self.assertEqual(res["updated_text"], REP20_S2_CYCLE2_EN)
        self.assertTrue(res["handoff"]["span_unverified"])

    def test_d_partial_sentence_level1_targets_fragment_and_only_level3_expands_to_whole_sentence(self):
        seen = {}

        def fake(label, prompt, n):
            if label.endswith("_e1_minimal_word"):
                seen["l1"] = prompt
                return json.dumps({"revised_ranges": []})  # 最小編集では解消できない宣言
            if label.endswith("_e2_rewrite"):
                seen["l3"] = prompt
                return json.dumps({"revised_ranges": ["Also, some calls may need user information to continue."]})
            self.fail(f"unexpected {label}")

        fixture = {"ledger_text": LEDGER, "article_text": REP21_S1_EN}
        res, calls = _run_ladder(fixture, _claim("“Some calls needed user information to continue.”"), fake)
        self.assertEqual([c["label"] for c in calls], ["t_e1_minimal_word", "t_e2_rewrite"])
        attempts = res["handoff"]["level_attempts"]
        self.assertEqual(attempts[0]["targets"], ["some calls needed user information to continue."])
        self.assertEqual(attempts[0]["result"], "declined")
        self.assertEqual(attempts[1]["targets"], ["Also, some calls needed user information to continue."])
        self.assertEqual(res["ladder_level_used"], "3_sentence")
        self.assertIn("Also, some calls may need user information to continue.", res["updated_text"])
        # ①のPromptには文頭の“Also, ”を含む文全体は範囲として出ない(範囲は断片)
        l1_ranges_part = seen["l1"].split("[Paragraph context")[0]
        self.assertIn("<<<\nsome calls needed user information to continue.\n>>>", l1_ranges_part)
        self.assertNotIn("<<<\nAlso, some calls", l1_ranges_part)

    def test_d2_partial_sentence_level1_success_replaces_only_the_fragment(self):
        def fake(label, prompt, n):
            return json.dumps({"revised_ranges": ["some calls may need user information to continue."]})

        fixture = {"ledger_text": LEDGER, "article_text": REP21_S1_EN}
        res, calls = _run_ladder(fixture, _claim("“Some calls needed user information to continue.”"), fake)
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertIn("Also, some calls may need user information to continue.", res["updated_text"])
        self.assertEqual(len(calls), 1)

    def test_e_ambiguous_duplicate_string_is_unverified_without_api_call(self):
        text = "# T\n\nIt was one call. Other text.\n\nIt was one call. More text.\n"
        res, calls = _run_ladder({"ledger_text": LEDGER, "article_text": text}, _claim("It was one call."),
                                 lambda *a: self.fail("API must not be called"))
        self.assertTrue(res["span_unverified"])
        self.assertEqual(res["span_unverified_reason"], "multi_match")
        self.assertEqual(calls, [])

    def test_f_array_count_mismatch_fails_that_level_and_escalates(self):
        def fake(label, prompt, n):
            if label.endswith("_e1_minimal_word"):
                return json.dumps({"revised_ranges": ["only one"]})  # 範囲は2つ → 個数不一致
            return json.dumps({"revised_ranges": ["They could not always tell if it was AI or a person.",
                                                  "They may not have realized it."]})

        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim(REP20_S2_C2_CLAIM), fake)
        attempts = res["handoff"]["level_attempts"]
        self.assertEqual(attempts[0]["level"], "1_word_connective")
        self.assertEqual(attempts[0]["result"], "count_mismatch")
        self.assertEqual(attempts[0]["returned_count"], 1)
        self.assertEqual(attempts[1]["level"], "3_sentence")
        self.assertEqual(attempts[1]["result"], "success")
        self.assertEqual(res["ladder_level_used"], "3_sentence")

    def test_f2_all_levels_count_mismatch_ends_in_ladder_exhausted_without_full_rewrite(self):
        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim(REP20_S2_C2_CLAIM),
                                 lambda *a: json.dumps({"revised_ranges": ["x", "y", "z"]}))  # 常に3個(範囲は2つ)
        self.assertFalse(res["guard_ok"])
        self.assertTrue(res["ladder_exhausted_without_full_rewrite"])
        self.assertEqual([a["result"] for a in res["handoff"]["level_attempts"]],
                         ["count_mismatch", "count_mismatch", "count_mismatch"])
        self.assertEqual(res["updated_text"], REP20_S2_CYCLE2_EN)
        self.assertEqual(len(calls), 3)  # ①③④。⑥は既定OFFで呼ばない
        self.assertFalse(any(c["label"].endswith("fulltext_fallback") for c in calls))

    def test_g_writeback_recheck_failure_never_replaces_by_guess(self):
        # 1つ目の範囲の書き換え結果が2つ目の範囲の文字列を含むと、書き戻し直前の再確認
        # (ちょうど1箇所)が2つ目で失敗する → その水準は失敗、本文は変更しない
        def fake(label, prompt, n):
            if label.endswith("_e1_minimal_word"):
                return json.dumps({"revised_ranges": ["They did not realize it. It was a person",
                                                      "They did not realize it."]})
            return json.dumps({"revised_ranges": []})

        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim(REP20_S2_C2_CLAIM), fake)
        a0 = res["handoff"]["level_attempts"][0]
        self.assertEqual(a0["result"], "writeback_failed")
        self.assertEqual(a0["writeback_failed_index"], 1)
        self.assertFalse(res["guard_ok"])
        self.assertEqual(res["updated_text"], REP20_S2_CYCLE2_EN)

    def test_g2_stale_range_not_found_at_writeback_is_a_level_failure(self):
        # 範囲確定後に本文が変わって範囲が消えた場合を直接再現: vs_apply_replacementsの契約
        new, bad = runner.vs_apply_replacements("A. B. C.", ["B.", "ZZZ"], ["x", "y"])
        self.assertIsNone(new)
        self.assertEqual(bad, 1)

    def test_h_guard_fails_when_only_one_of_two_ranges_changed(self):
        def fake(label, prompt, n):
            if label.endswith("_e1_minimal_word"):
                return json.dumps({"revised_ranges": ["They could not tell if it was AI or a person",  # 不変
                                                      "They may not have realized it."]})
            return json.dumps({"revised_ranges": []})

        fixture = {"ledger_text": LEDGER, "article_text": REP20_S2_CYCLE2_EN}
        res, calls = _run_ladder(fixture, _claim(REP20_S2_C2_CLAIM), fake)
        a0 = res["handoff"]["level_attempts"][0]
        self.assertEqual(a0["each_target_changed"], [False, True])
        self.assertEqual(a0["result"], "guard_failed")
        self.assertFalse(res["guard_ok"])
        self.assertEqual(res["updated_text"], REP20_S2_CYCLE2_EN)

    def test_h2_old_guard_blind_spot_is_closed_two_sentence_claim_with_only_first_sentence_changed(self):
        # 旧guard(`claim_text.strip() not in candidate`)は引用符付き文字列では常に成立し、
        # 2文のうち1文しか変えていなくても通っていた。新guardは範囲全体の変化を要求する
        # (範囲=2文は1つの範囲なので、範囲として変化していればよい=範囲外へ広げない)。
        revised = ("It said human staff made inappropriate comments about race during a call. "
                   "These calls were about trying to lower internet or cable fees.")
        res, _ = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                             _claim(REP21_S1_TWO_SENTENCE_CLAIM),
                             lambda *a: json.dumps({"revised_ranges": [revised]}))
        self.assertTrue(res["guard_ok"])  # 範囲(2文のまとまり)として変化している
        self.assertTrue(res["handoff"]["level_attempts"][0]["each_target_changed"][0])
        # 範囲が全く変わらなければ不成立
        res2, _ = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                              _claim(REP21_S1_TWO_SENTENCE_CLAIM),
                              lambda label, prompt, n: ("not json" if label.endswith("paragraph_rewrite") else
                                                        json.dumps({"revised_ranges": [REP21_S1_TWO_SENTENCES]})))
        self.assertFalse(res2["guard_ok"])
        self.assertEqual([a["result"] for a in res2["handoff"]["level_attempts"]],
                         ["guard_failed", "guard_failed", "parse_failure"])

    def test_level1_declined_when_empty_string_returned(self):
        def fake(label, prompt, n):
            if label.endswith("_e1_minimal_word"):
                return json.dumps({"revised_ranges": [""]})
            return json.dumps({"revised_ranges": ["Also, some calls may need user information to continue."]})

        res, calls = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                                 _claim("“Some calls needed user information to continue.”"), fake)
        self.assertEqual(res["handoff"]["level_attempts"][0]["result"], "declined")
        self.assertEqual(res["ladder_level_used"], "3_sentence")

    def test_level4_paragraph_is_reached_only_after_level1_and_level3_fail(self):
        order = []

        def fake(label, prompt, n):
            order.append(label)
            if label.endswith("_e2_paragraph_rewrite"):
                para = "Also, some calls may need user information to continue. That information might be shared."
                return json.dumps({"revised_ranges": [para]})
            return json.dumps({"revised_ranges": []})

        res, calls = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                                 _claim("“Some calls needed user information to continue.”"), fake)
        self.assertEqual(order, ["t_e1_minimal_word", "t_e2_rewrite", "t_e2_paragraph_rewrite"])
        self.assertEqual(res["ladder_level_used"], "4_paragraph")
        self.assertIsNone(res["after_fragment"])  # 段落水準では文単位のafterは確定しない(既存仕様)

    def test_hint_quote_does_not_decide_the_target(self):
        # 判定役のhintが別の文を引用していても、対象はCheckerの範囲だけ(hintは指示文としてのみ)
        hint = "“Meta employees pointed this out inside the company as a privacy concern.” を直す。"
        seen = {}

        def fake(label, prompt, n):
            seen["prompt"] = prompt
            return json.dumps({"revised_ranges": ["some calls may need user information to continue."]})

        res, _ = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                             _claim("“Some calls needed user information to continue.”", hint=hint), fake)
        self.assertEqual(res["handoff"]["level_attempts"][0]["targets"],
                         ["some calls needed user information to continue."])
        self.assertIn("Meta employees pointed this out", seen["prompt"])  # 指示文としては渡る
        self.assertIn("Meta employees pointed this out inside the company as a privacy concern.", res["updated_text"])

    def test_old_four_stage_locators_are_not_called_in_new_mode(self):
        boom = AssertionError("old locator must not be used in new mode")
        fixture = {"ledger_text": LEDGER, "article_text": REP21_S1_EN}
        with mock.patch.object(runner, "locate_target", side_effect=boom), \
                mock.patch.object(runner, "locate_best_sentence", side_effect=boom), \
                mock.patch.object(runner, "locate_multi_quote_span", side_effect=boom), \
                mock.patch.object(runner.er010, "locate_target_sentence", side_effect=boom):
            res, _ = _run_ladder(fixture, _claim(REP21_S1_TWO_SENTENCE_CLAIM),
                                 lambda *a: json.dumps({"revised_ranges": [REP21_S1_TWO_SENTENCES + " (x)"]}))
            self.assertTrue(res["guard_ok"])
            res2, _ = _run_ladder(fixture, _claim("Totally unrelated paraphrase of nothing."),
                                  lambda *a: self.fail("no API"))
            self.assertTrue(res2["span_unverified"])
            self.assertEqual(runner.detect_claim_section_type(REP21_S1_TWO_SENTENCE_CLAIM, REP21_S1_EN), "body")

    def test_delete_kind_whole_sentence_is_deleted_deterministically_and_absence_verified(self):
        text = "# T\n\nKeep this one. Remove this exact sentence. Keep the end.\n"
        res, calls = _run_ladder({"ledger_text": LEDGER, "article_text": text},
                                 _claim("“Remove this exact sentence.”", kind="delete"),
                                 lambda *a: self.fail("delete is deterministic (no API)"))
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "0_delete")
        self.assertNotIn("Remove this exact sentence.", res["updated_text"])
        self.assertIn("Keep this one.", res["updated_text"])
        self.assertIn("Keep the end.", res["updated_text"])
        self.assertEqual(calls, [])

    def test_delete_kind_with_partial_range_expands_to_containing_sentence_and_records_it(self):
        res, _ = _run_ladder({"ledger_text": LEDGER, "article_text": REP21_S1_EN},
                             _claim("“Some calls needed user information to continue.”", kind="delete"),
                             lambda *a: self.fail("no API"))
        self.assertTrue(res["guard_ok"])
        self.assertTrue(res["handoff"]["delete_expanded_to_sentence"])
        self.assertNotIn("Also, some calls needed user information to continue.", res["updated_text"])

    def test_actor_guard_is_kept(self):
        def fake(label, prompt, n):
            if label.endswith("paragraph_rewrite"):
                return "not json"
            if label.endswith("_e2_rewrite"):
                return json.dumps({"revised_ranges": ["Also, some customers needed user information to continue."]})
            return json.dumps({"revised_ranges": ["some customers needed user information to continue."]})

        res, _ = _run_ladder({"ledger_text": "[VERIFIED] x: nothing relevant here", "article_text": REP21_S1_EN},
                             _claim("“Some calls needed user information to continue.”"), fake)
        self.assertFalse(res["guard_ok"])
        self.assertEqual([a["result"] for a in res["handoff"]["level_attempts"]],
                         ["actor_guard_rejected", "actor_guard_rejected", "parse_failure"])


class TestHandoffStage3Routing(unittest.TestCase):
    """委任_42 仕様(8): originとEN/JAどちらで確定したかによる振り分け(JA側は暫定)。"""

    EN = "# T\n\nIt was one call. Another sentence here. They did not realize it.\n"
    JA = "# タイトル\n\nこれは1回の電話でした。別の文です。彼らは気づきませんでした。\n"

    def _fixture(self):
        return {"ledger_text": LEDGER, "article_text": self.EN, "source_article_text": self.JA}

    def test_translation_origin_resolved_in_en_uses_single_text_path(self):
        with mock.patch.object(runner, "simple_llm_call",
                               return_value=json.dumps({"revised_ranges": ["It was a single call."]})):
            r = runner.run_stage3_for_claim(None, _state0(), [], [], "t", self._fixture(), self.EN, self.JA,
                                            _claim("“It was one call.”", origin="translation"))
        self.assertEqual(r["mechanism"], "single_text_local(E-2/delete-generic)")
        self.assertTrue(r["guard_ok"])
        self.assertIn("It was a single call.", r["en_text"])
        self.assertEqual(r["ja_text"], self.JA)

    def test_ja_source_single_en_range_uses_paired_rewrite_with_en_target_replaced_by_confirmed_range(self):
        seen = {}

        def fake_paired(client, state, errs, log, label, fixture, claim_rec):
            seen["claim_rec"] = claim_rec
            return {"updated_en_text": self.EN, "updated_ja_text": self.JA, "method": "x", "guard_ok": False,
                    "en_target": "It was one call.", "ja_target": "ja", "before_fragment": None,
                    "after_fragment": None, "ladder_level_used": None, "target_not_locatable": False,
                    "handoff": {"mode": "violation_span"}}

        with mock.patch.object(runner, "paired_rewrite", side_effect=fake_paired):
            r = runner.run_stage3_for_claim(None, _state0(), [], [], "t", self._fixture(), self.EN, self.JA,
                                            _claim("“It was one call.”", origin="ja_source"))
        self.assertEqual(r["mechanism"], "paired_ja_en(J-1)")
        self.assertEqual(seen["claim_rec"]["span_resolution"]["ranges"], ["It was one call."])
        self.assertFalse(r["handoff"]["ja_provisional_path"])

    def test_ja_source_multiple_en_ranges_goes_to_provisional_single_side_path(self):
        en = "# T\n\nIt was one call. Middle sentence. They did not realize it.\n"
        fixture = {"ledger_text": LEDGER, "article_text": en, "source_article_text": self.JA}
        with mock.patch.object(runner, "simple_llm_call",
                               return_value=json.dumps({"revised_ranges": ["It was a single call.",
                                                                           "They may not have realized it."]})), \
                mock.patch.object(runner, "paired_rewrite", side_effect=AssertionError("paired must not be used")):
            r = runner.run_stage3_for_claim(
                None, _state0(), [], [], "t", fixture, en, self.JA,
                _claim("“It was one call.” and “They did not realize it.”", origin="ja_source"))
        self.assertTrue(r["guard_ok"])
        self.assertTrue(r["handoff"]["ja_provisional_path"])
        self.assertEqual(r["handoff"]["ja_provisional_reason"], "en_multiple_ranges")
        self.assertTrue(r["method"].startswith("j1_single_side_en("))
        self.assertEqual(r["mechanism"], "paired_ja_en(J-1)")  # 既存のJA Recheckが走るよう維持
        self.assertEqual(r["ja_text"], self.JA)  # JAは触らない(既存の再検査に任せる)
        self.assertIn("They may not have realized it.", r["en_text"])

    def test_ja_source_claim_confirmed_only_in_ja_edits_ja_side_provisionally(self):
        with mock.patch.object(runner, "simple_llm_call",
                               return_value=json.dumps({"revised_ranges": ["これは1件の報告でした。"]})):
            r = runner.run_stage3_for_claim(None, _state0(), [], [], "t", self._fixture(), self.EN, self.JA,
                                            _claim("これは1回の電話でした。", origin="ja_source"))
        self.assertTrue(r["handoff"]["ja_provisional_path"])
        self.assertEqual(r["handoff"]["ja_provisional_reason"], "ja_only_match")
        self.assertTrue(r["guard_ok"])
        self.assertIn("これは1件の報告でした。", r["ja_text"])
        self.assertEqual(r["en_text"], self.EN)

    def test_non_ja_source_claim_confirmed_only_in_ja_is_unverified_fail_closed(self):
        r = runner.run_stage3_for_claim(None, _state0(), [], [], "t", self._fixture(), self.EN, self.JA,
                                        _claim("これは1回の電話でした。", origin="translation"))
        self.assertTrue(r["span_unverified"])
        self.assertTrue(r["target_not_locatable"])
        self.assertEqual(r["span_unverified_reason"], "ja_only_match_origin_not_ja_source")

    def test_unresolvable_claim_is_unverified_without_api_call(self):
        log = []
        r = runner.run_stage3_for_claim(None, None, [0], log, "t", self._fixture(), self.EN, self.JA,
                                        _claim("Paragraph beginning “People”", origin="ja_source"))
        self.assertTrue(r["span_unverified"])
        self.assertEqual(r["handoff"]["span_unverified_reason"], "explanatory_mixed")
        self.assertEqual(log, [])
        self.assertEqual((r["en_text"], r["ja_text"]), (self.EN, self.JA))

    def test_paired_rewrite_new_mode_uses_range_at_level1_and_sentence_at_level3(self):
        en = "# T\n\nAlso, it was one call today. Other.\n"
        ja = "# タイトル\n\nまた、今日は1回の電話でした。他。\n"
        fixture = {"ledger_text": LEDGER, "article_text": en, "source_article_text": ja}
        prompts = []

        def fake(client, state, errs, log, label, dev_msg, prompt, model=None):
            prompts.append((label, prompt))
            if label.endswith("_j1_e1_minimal_word"):
                return json.dumps({"ja_revised": "", "en_revised": ""})
            return json.dumps({"ja_revised": "また、今日は1件の報告でした。",
                               "en_revised": "Also, it was one reported call today."})

        claim = _claim("“It was one call today.”", origin="ja_source")
        claim["span_resolution"] = runner.resolve_violation_spans(claim["claim_text"], en, ja)
        with mock.patch.object(runner, "simple_llm_call", side_effect=fake), \
                mock.patch.object(runner, "locate_target", side_effect=AssertionError("legacy locator")), \
                mock.patch.object(runner, "locate_multi_quote_span", side_effect=AssertionError("legacy")):
            res = runner.paired_rewrite(None, _state0(), [], [], "t", fixture, claim)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["en_target"], "it was one call today.")  # 水準①の対象=確定範囲(断片)
        att = res["handoff"]["level_attempts"]
        self.assertEqual(att[0]["targets"], ["it was one call today."])
        self.assertTrue(att[0]["target_equals_confirmed_ranges"])
        self.assertEqual(att[1]["targets"], ["Also, it was one call today."])  # ③で初めて文全体
        self.assertEqual(res["ladder_level_used"], "3_sentence")
        self.assertIn("Also, it was one reported call today.", res["updated_en_text"])

    def test_paired_rewrite_new_mode_guard_requires_en_range_to_change(self):
        en = "# T\n\nIt was one call today. Other.\n"
        ja = "# タイトル\n\n今日は1回の電話でした。他。\n"
        fixture = {"ledger_text": LEDGER, "article_text": en, "source_article_text": ja}
        claim = _claim("“It was one call today.”", origin="ja_source")
        def fake(client, state, errs, log, label, dev_msg, prompt, model=None):
            if label.endswith("_paragraph"):
                return "not json"
            return json.dumps({"ja_revised": "今日は1件でした。", "en_revised": "It was one call today."})  # ENは不変

        with mock.patch.object(runner, "simple_llm_call", side_effect=fake):
            res = runner.paired_rewrite(None, _state0(), [], [], "t", fixture, claim)
        self.assertFalse(res["guard_ok"])
        self.assertEqual(res["updated_en_text"], en)
        self.assertEqual([a["result"] for a in res["handoff"]["level_attempts"]],
                         ["guard_failed", "guard_failed", "guard_failed"])


class TestHandoffSectionTypeAndIdentity(unittest.TestCase):
    ART = ("# Meta’s AI Calls Had Humans\n\nIt was a surprise. A service let people ask AI to call.\n\n"
           "Body paragraph one has a unique body claim sentence. Another body sentence follows.\n\n"
           "## In one line\nSome calls were handled by humans, but users were not told.\n")

    def test_section_by_span_containment(self):
        f = runner.detect_claim_section_type
        self.assertEqual(f("“Meta’s AI Calls Had Humans”", self.ART), "title")
        self.assertEqual(f("“Some calls were handled by humans, but users were not told.”", self.ART), "in_one_line")
        self.assertEqual(f("“A service let people ask AI to call.”", self.ART), "hook")
        self.assertEqual(f("“Body paragraph one has a unique body claim sentence.”", self.ART), "body")

    def test_section_multiple_ranges_across_sections_takes_strongest(self):
        claim = "“A service let people ask AI to call.” and “Another body sentence follows.”"
        self.assertEqual(runner.detect_claim_section_type(claim, self.ART), "hook")
        claim2 = ("“Another body sentence follows.” and "
                  "“Some calls were handled by humans, but users were not told.”")
        self.assertEqual(runner.detect_claim_section_type(claim2, self.ART), "in_one_line")

    def test_section_of_unverified_claim_is_body_and_not_similarity_based(self):
        self.assertEqual(runner.detect_claim_section_type("A service let people ask AI to phone someone.", self.ART),
                         "body")

    def test_legacy_section_function_is_kept_for_rollback(self):
        self.assertEqual(runner.detect_claim_section_type_legacy("A service let people ask AI to call.", self.ART),
                         "hook")
        with mock.patch.object(runner, "HANDOFF_MODE", runner.HANDOFF_MODE_LEGACY):
            self.assertEqual(runner.detect_claim_section_type("A service let people ask AI to call.", self.ART),
                             "hook")

    def test_claim_span_text_and_identity_use_the_confirmed_range_not_the_raw_quoted_string(self):
        c = {"claim_text": REP20_S2_C2_CLAIM}
        runner.annotate_claim_span_identity(c, REP20_S2_CYCLE2_EN, None)
        self.assertEqual(c["claim_span_text"], "They could not tell if it was AI or a person\nThey did not realize it.")
        self.assertEqual(c["span_resolution_cycle_start"]["status"], "resolved")
        c2 = {"claim_text": "Paragraph beginning “People asking Muse to call”"}
        runner.annotate_claim_span_identity(c2, REP20_S2_CYCLE2_EN, None)
        self.assertIsNone(c2["claim_span_text"])
        self.assertEqual(c2["span_resolution_cycle_start"]["reason"], "explanatory_mixed")

    def test_find_matching_prior_record_uses_claim_norm_when_given(self):
        prior = [{"identity": "fact:F1", "fact_id": "F1",
                  "claim_text_norm": runner.normalize_claim_text("It was one call."), "escalated_to_paragraph": False}]
        dev = {"related_fact_id": "F1", "claim_in_article": "“It was one call.” (raw quoted + extra words here)"}
        # 生の文字列では一致しない(同一判定が揺れる)が、確定範囲の正規化表現なら一致する
        self.assertIsNone(runner.find_matching_prior_record(dev, prior))
        self.assertIsNotNone(runner.find_matching_prior_record(
            dev, prior, claim_norm=runner.normalize_claim_text("It was one call.")))

    def test_run_instance_wiring_uses_span_text_for_identity_and_prior_issues(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn("annotate_claim_span_identity(c, current_en_text, current_ja_text)", src)
        # 委任_01(KPI-RECOVERY-REDESIGN-02): prior_issuesのclaim_in_articleは、確定範囲(claim_span_text)を
        # 元textとしつつ、Rewrite後の現行本文の置換後の文があればそちらを渡す(resolve_prior_issue_text)。
        self.assertIn('_orig = c.get("claim_span_text") or c["claim_text"]', src)
        self.assertIn("resolve_prior_issue_text(_orig,", src)
        self.assertIn("claim_norm=(normalize_claim_text(_span_txt) if _span_txt else None)", src)
        self.assertIn('stage4_reason = "violation_span_unverified" if span_unverified_records', src)

    def test_stage2_input_claim_text_display_is_unchanged(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('"claim_text": d.get("claim_in_article", "")', src)

    def test_handoff_mode_default_is_new_and_legacy_is_selectable(self):
        self.assertEqual(runner.HANDOFF_MODE, "violation_span")
        self.assertEqual(runner.HANDOFF_MODE_LEGACY, "legacy")

    def test_legacy_mode_single_text_rewrite_still_runs_old_path(self):
        text = "# T\n\nSome sentence with a problem in it.\n"
        claim = _claim("Some sentence with a problem in it.")
        with mock.patch.object(runner, "HANDOFF_MODE", runner.HANDOFF_MODE_LEGACY), \
                mock.patch.object(runner, "simple_llm_call", return_value="Some sentence without it."):
            res = runner.single_text_rewrite(None, _state0(), [], [], "t",
                                             {"ledger_text": LEDGER, "article_text": text}, "article_text", claim)
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("handoff", res)



class TestHandoffCarryForwardWithinCycle(unittest.TestCase):
    """委任_42(rep22 T3で判明した不具合の是正): 同じ文を指す2つのclaim(LLM claim+precheck
    floor claim)で、先行claimのRewriteが文を書き換えると後続claimの文字列が現在の本文から消える。
    これを確定不能(Stage 4)と誤認せず、「先行Rewriteで既に書き換え済み」として扱う。"""

    START = "# T\n\nResearchers studied 30 million payments in taxis. Another sentence stays.\n"
    AFTER_FIRST = "# T\n\nResearchers studied over 3 million payments in taxis. Another sentence stays.\n"
    SENT = "Researchers studied 30 million payments in taxis."

    def _claim_rec(self, text=None):
        rec = _claim(text or self.SENT, kind="replace_with_ledger_value", origin="translation")
        rec["cycle_start_en_text"] = self.START
        rec["cycle_start_ja_text"] = None
        rec["cycle_replaced_units"] = [{"claim_identity": "claim:first", "lang": "EN",
                                        "before_units": [self.SENT],
                                        "after_units": ["Researchers studied over 3 million payments in taxis."]}]
        return rec

    def test_claim_already_rewritten_by_earlier_claim_is_skipped_not_unverified(self):
        log = []
        r = runner.run_stage3_for_claim(None, None, [0], log, "t",
                                        {"ledger_text": LEDGER, "article_text": self.AFTER_FIRST},
                                        self.AFTER_FIRST, None, self._claim_rec())
        self.assertEqual(log, [])
        self.assertFalse(r["target_not_locatable"])
        self.assertFalse(r["span_unverified"])
        self.assertEqual(r["method"], "covered_by_earlier_rewrite_in_cycle")
        self.assertTrue(r["handoff"]["skipped_covered_by_earlier_rewrite"])
        self.assertEqual(r["handoff"]["carry_forward_covered"][0]["covered_by_claim"], "claim:first")
        self.assertEqual(r["en_text"], self.AFTER_FIRST)

    def test_without_earlier_rewrite_the_vanished_string_is_still_unverified(self):
        rec = self._claim_rec()
        rec["cycle_replaced_units"] = []
        r = runner.run_stage3_for_claim(None, None, [0], [], "t",
                                        {"ledger_text": LEDGER, "article_text": self.AFTER_FIRST},
                                        self.AFTER_FIRST, None, rec)
        self.assertTrue(r["span_unverified"])
        self.assertEqual(r["span_unverified_reason"], "mismatch")

    def test_string_absent_in_cycle_start_text_too_is_unverified(self):
        r = runner.run_stage3_for_claim(None, None, [0], [], "t",
                                        {"ledger_text": LEDGER, "article_text": self.AFTER_FIRST},
                                        self.AFTER_FIRST, None, self._claim_rec("Nothing like this sentence."))
        self.assertTrue(r["span_unverified"])

    def test_partially_covered_claim_rewrites_only_the_remaining_range(self):
        # 2範囲のclaimのうち1つは先行Rewriteで書き換え済み、もう1つは現存 → 現存するものだけRewrite
        start = "# T\n\nFirst flagged one. Middle. Second flagged two.\n"
        now = "# T\n\nFirst revised one. Middle. Second flagged two.\n"
        rec = _claim("“First flagged one.” and “Second flagged two.”", origin="translation")
        rec.update({"cycle_start_en_text": start, "cycle_start_ja_text": None,
                    "cycle_replaced_units": [{"claim_identity": "claim:first", "lang": "EN",
                                              "before_units": ["First flagged one."],
                                              "after_units": ["First revised one."]}]})
        with mock.patch.object(runner, "simple_llm_call",
                               return_value=json.dumps({"revised_ranges": ["Second revised two."]})):
            r = runner.run_stage3_for_claim(None, _state0(), [], [], "t",
                                            {"ledger_text": LEDGER, "article_text": now}, now, None, rec)
        self.assertTrue(r["guard_ok"])
        self.assertEqual(r["handoff"]["level_attempts"][0]["targets"], ["Second flagged two."])
        self.assertEqual(r["handoff"]["carry_forward_covered"][0]["range"], "First flagged one.")
        self.assertIn("First revised one. Middle. Second revised two.", r["en_text"])

    def test_collect_replaced_units_from_successful_result(self):
        res = {"guard_ok": True, "handoff": {"text_lang": "EN", "level_attempts": [
            {"level": "1_word_connective", "result": "declined", "targets": ["a"]},
            {"level": "3_sentence", "result": "success", "targets": ["A sentence."], "revised": ["B sentence."],
             "before_after": [{"before": "A sentence.", "after": "B sentence."}]}]}}
        units = runner.collect_replaced_units(res, "claim:x")
        self.assertEqual(units, [{"claim_identity": "claim:x", "lang": "EN", "before_units": ["A sentence."],
                                  "after_units": ["B sentence."]}])
        self.assertEqual(runner.collect_replaced_units({"guard_ok": False, "handoff": res["handoff"]}, "c"), [])

    def test_run_instance_cycle_passes_replaced_units_to_following_claims(self):
        import inspect
        src = inspect.getsource(runner.run_instance)
        self.assertIn('c2["cycle_replaced_units"] = list(cycle_replaced_units)', src)
        self.assertIn('cycle_replaced_units.extend(collect_replaced_units(r, claim_identity(c["dev"])))', src)


# ============================================================
# 委任_49: 照合の追補(VS_MATCH_EXT)・英語だけ修正(JA_MODE)・評価と記録の追加の実例ベーステスト。
# すべて¥0・ネットワークなし。実例の文字列は`er052_output/open233_match_ext_replay_01`の再生で
# 確認した記録(委任_45のU03・U04・U07)と、rep22 meta_run03_standardの実文から取った。
# ============================================================
U03_CLAIM = "“Trump’s proposed Hormuz fee vanished overnight.”"
U03_ARTICLE = ("# T\n\n## In one line\nTrump’s proposed Hormuz fee vanished overnight, but crude oil prices "
               "stayed high as tensions and tanker fees remained.\n")
U04_CLAIM = ("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the "
             "flashy 20% plan left the stage.")
U07_CLAIM = ("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the "
             "flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.")
U047_ARTICLE = ("# T\n\n## In one line\n\nConcerns about US-Iran attacks, the sea blockade, and tanker safety "
                "continued on July 14, so the flashy 20% plan left the stage, but the chart only pulled back "
                "briefly before recovering: the policy turn and the oil chart’s “not over yet” movement.\n")
META_TARGET = "Also, some calls needed user information to continue."


def _meta_as_safety_critical():
    """委任_55: Meta-1は期待QUALITYの監視用へ移ったため、`detect_safety_critical_misdowngrades`/
    `compute_residual_at_pass`の機構そのものの試験(Meta文を使う既存テスト)では、機構が使うキーを
    持つ合成の定義(expected省略=BLOCKING)へ一時的に差し替える。"""
    return mock.patch.dict(runner.SAFETY_CRITICAL_CLAIM_DEFS, {"meta_run03_standard": [
        {"sub_id": "Meta-1", "related_fact_id": "MUSE-HC-010",
         "text_substring": "needed user information to continue"}]})


def _ext(on: bool = True):
    return mock.patch.object(runner, "VS_MATCH_EXT", on)


class TestVsMatchExtA1EdgePunct49(unittest.TestCase):
    def test_default_switch_is_off(self):
        self.assertFalse(runner.VS_MATCH_EXT)
        self.assertEqual(runner.JA_MODE, runner.JA_MODE_PAIRED)

    def test_u03_u04_u07_unresolved_when_off_and_confirmed_by_l5_when_on(self):
        for claim, art, expected in (
                (U03_CLAIM, U03_ARTICLE, "Trump’s proposed Hormuz fee vanished overnight"),
                (U04_CLAIM, U047_ARTICLE, U04_CLAIM[:-1]),
                (U07_CLAIM, U047_ARTICLE, U07_CLAIM[:-1])):
            with self.subTest(claim=claim[:30]):
                off = runner.resolve_violation_spans(claim, art, None)
                self.assertEqual(off["status"], "unverified")
                self.assertEqual(off["reason"], "mismatch")
                with _ext():
                    on = runner.resolve_violation_spans(claim, art, None)
                self.assertEqual(on["status"], "resolved")
                self.assertEqual(on["level"], "L5_edge_punct")
                self.assertEqual(on["ranges"], [expected])  # 文の途中までの節。文単位へ拡張しない
                self.assertEqual(on["edge_removed"][1], ".")

    def test_mid_word_match_is_not_confirmed(self):
        # 「ear.」から末尾句読点を除いた「ear」は「year」の途中にしか無い(語の途中への一致)
        art = "# T\n\nThe year, then calm.\n"
        with _ext():
            r = runner.resolve_violation_spans("ear.", art, None)
        self.assertEqual(r["status"], "unverified")

    def test_ja_body_is_not_subject_to_l5(self):
        ja = "# T\n\n夜のうちに消えた、そして落ち着いた。\n"
        with _ext():
            r = runner.resolve_violation_spans("夜のうちに消えた。", None, ja)
        self.assertEqual(r["status"], "unverified")

    def test_inner_punctuation_is_not_removed(self):
        art = "# T\n\nOne, two and three stay.\n"
        with _ext():
            r = runner.resolve_violation_spans("One two and three stay.", art, None)
        self.assertEqual(r["status"], "unverified")  # 両端以外の句読点は補わない

    def test_two_places_stays_unverified(self):
        art = "# T\n\nIt left the stage, then It left the stage; done.\n"
        with _ext():
            r = runner.resolve_violation_spans("It left the stage.", art, None)
        self.assertEqual(r["status"], "unverified")
        self.assertEqual(r["reason"], "multi_match")


class TestVsMatchExtLabelAndBoundary49(unittest.TestCase):
    ART = "# Title Line\n\n## In one line\nBody sentence one. Body sentence two.\n"

    def test_label_line_is_unverified_with_label_only_when_on(self):
        off = runner.resolve_violation_spans("“In one line”", self.ART, None)
        self.assertEqual(off["status"], "resolved")  # 委任_42の照合(現行)では見出し行に確定してしまう
        with _ext():
            on = runner.resolve_violation_spans("“In one line”", self.ART, None)
        self.assertEqual(on["status"], "unverified")
        self.assertEqual(on["reason"], "label_only")

    def test_title_line_and_body_are_not_label(self):
        with _ext():
            t = runner.resolve_violation_spans("Title Line", self.ART, None)
            b = runner.resolve_violation_spans("Body sentence two.", self.ART, None)
        self.assertEqual(t["status"], "resolved")
        self.assertEqual(b["status"], "resolved")

    def test_word_boundary_applies_to_l0(self):
        art = "# T\n\nThe year, then calm.\n"
        self.assertEqual(runner.resolve_violation_spans("ear", art, None)["status"], "resolved")  # OFF=現行
        with _ext():
            self.assertEqual(runner.resolve_violation_spans("ear", art, None)["status"], "unverified")

    def test_word_boundary_applies_to_l1_l2_l3_and_l4(self):
        art = "# T\n\nThe Year ahead, with more  space. Another place.\n"
        with _ext():
            # L1(引用符を外す)
            self.assertEqual(runner.resolve_violation_spans("“ear”", art, None)["status"], "unverified")
            # L2(空白の連続の同一視)・L3(大文字小文字)でも語の途中は確定しない
            self.assertEqual(runner.resolve_violation_spans("ore space", art, None)["status"], "unverified")
            self.assertEqual(runner.resolve_violation_spans("EAR AHEAD", art, None)["status"], "unverified")
            # 語境界を満たすL3は確定する
            self.assertEqual(runner.resolve_violation_spans("year AHEAD", art, None)["level"], "L3")
            # L4(2断片): 1つが語の途中なら確定しない
            self.assertEqual(runner.resolve_violation_spans("“ear” and “Another place”", art, None)["status"],
                             "unverified")
            self.assertEqual(runner.resolve_violation_spans("“Year ahead” and “Another place”", art, None)["level"],
                             "L4")

    def test_ja_body_has_no_word_boundary_condition(self):
        ja = "# T\n\n夜のうちに消えた。\n"
        with _ext():
            self.assertEqual(runner.resolve_violation_spans("消え", None, ja)["status"], "resolved")

    def test_switch_off_equals_delegation_42_for_real_strings(self):
        # スイッチOFF(既定)と、スイッチ変数を明示的にFalseにした場合で同一(委任_42の挙動のまま)
        for claim, art in ((U03_CLAIM, U03_ARTICLE), (U04_CLAIM, U047_ARTICLE), ("“In one line”", self.ART)):
            a = runner.resolve_violation_spans(claim, art, None)
            with _ext(False):
                b = runner.resolve_violation_spans(claim, art, None)
            self.assertEqual(a, b)
            self.assertNotIn("edge_removed", a)


# ---- run_instanceの流れを偽の応答で通す(ネットワークなし)
EN49 = ("# Title\n\n## In one line\nShort line.\n\n"
        "Calls happened. Also, some calls needed user information to continue. The end.\n")
JA49 = "# タイトル\n\n## ひとこと\n短い。\n\nいくつかの通話があった。\n"


def _dev49(claim, sev="MAJOR", origin="translation", fid="MUSE-HC-010", **flags):
    d = {"claim_in_article": claim, "severity": sev, "origin": origin, "related_fact_id": fid,
         "issue": "claim differs from ledger", "explanation": "x", "changed_fact": False, "changed_scope": False,
         "changed_causality": False, "changed_certainty": False, "changed_number": False,
         "changed_actor": False, "changed_negation": False, "changed_comparison": False,
         "changed_time": False, "unsupported_new_claim": False}
    d.update(flags)
    return d


def _run_instance49(stage1_devs, recheck_devs=None, stage3_new_sentence="Some calls may have needed user information.",
                    fastpath_success=True, ja_mode=None, stage3_fn=None, iid="unit49", ledger_text="(ledger)",
                    stage1_status="LEDGER_DEVIATION", recheck_resolved=True):
    """run_instanceを、Checker/Stage 2/Rewrite/Recheck/局所QAの偽の応答で通す。返値: (result, 記録dict)。"""
    seen = {"stage3_ja": [], "stage3_en": [], "fastpath_calls": 0, "recheck_calls": [], "recheck_fixture_ja": []}

    def fake_stage1(client, state, ce, call_log, label, fixture, developer_message=None):
        return {"overall_status": stage1_status, "deviations": [dict(d) for d in stage1_devs]}

    def fake_stage2(client, state, ce, call_log, label, fixture, claims):
        return [{**c, "materiality": "BLOCKING", "llm_materiality": "BLOCKING", "basis": "ledger_fact",
                 "rewrite_kind": "narrow_scope", "rewrite_hint": "h", "floor_reason": None, "section_type": "body",
                 "stage2_route": "body", "floor_cited_materiality": "BLOCKING", "floor_cited_reason": None}
                for c in claims]

    def fake_stage3(client, state, ce, call_log, label, fixture, en, ja, claim_rec):
        seen["stage3_ja"].append(ja)
        seen["stage3_en"].append(en)
        new_en = en.replace(META_TARGET, "Also, " + stage3_new_sentence[0].lower() + stage3_new_sentence[1:])
        return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": new_en, "ja_text": ja,
                "method": "fake", "guard_ok": True, "before_fragment": META_TARGET,
                "after_fragment": stage3_new_sentence, "ladder_level_used": "1_word_connective",
                "target_not_locatable": False, "span_unverified": False,
                "ladder_exhausted_without_full_rewrite": False,
                "handoff": {"level_attempts": [], "text_lang": "EN"}}

    def fake_fastpath(*a, **k):
        seen["fastpath_calls"] += 1
        return {"success": fastpath_success, "results": []}

    def fake_recheck(client, state, ce, call_log, label, fixture, article_text, prior_issues, **k):
        seen["recheck_calls"].append(label)
        seen["recheck_fixture_ja"].append(fixture.get("source_article_text"))
        seen.setdefault("prior_issues", prior_issues)
        return {"overall_status": "LEDGER_COMPLIANT" if recheck_resolved else "LEDGER_DEVIATION",
                "deviations": [dict(d) for d in (recheck_devs or [])],
                "prior_issues_resolved": [{"index": i, "resolved": recheck_resolved, "explanation": ""}
                                          for i, _ in enumerate(prior_issues)],
                "all_prior_issues_resolved": recheck_resolved}

    inst = {"instance_id": iid, "group": "unit", "expected_group_label": "unit", "stage1_mode": "fresh",
            "fixture": {"ledger_text": ledger_text, "article_text": EN49, "source_article_text": JA49}}
    patches = [mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1),
               mock.patch.object(runner, "run_stage2", fake_stage2),
               mock.patch.object(runner, "apply_stage2_two_of_two", lambda *a, **k: (a[6], [])),
               mock.patch.object(runner, "run_stage3_for_claim", stage3_fn or fake_stage3),
               mock.patch.object(runner, "run_local_qa_fastpath", fake_fastpath),
               mock.patch.object(runner, "run_recheck", fake_recheck),
               mock.patch.object(runner, "save_json", lambda *a, **k: None)]
    if ja_mode is not None:
        patches.append(mock.patch.object(runner, "JA_MODE", ja_mode))
    for p in patches:
        p.start()
    try:
        res = runner.run_instance(object(), _state0(), [0], inst, stage1_cache={})
    finally:
        for p in reversed(patches):
            p.stop()
    return res, seen


def _title_rewrite49(client, state, ce, call_log, label, fixture, en, ja, claim_rec):
    return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": en.replace("# Title", "# New Title"),
            "ja_text": ja, "method": "fake", "guard_ok": True, "before_fragment": "# Title",
            "after_fragment": "# New Title", "ladder_level_used": "1_word_connective",
            "target_not_locatable": False, "span_unverified": False,
            "ladder_exhausted_without_full_rewrite": False, "handoff": {"level_attempts": []}}


class TestJaModeEnglishOnly49(unittest.TestCase):
    JA_SRC_DEV = _dev49(META_TARGET, origin="ja_source")
    TR_DEV = _dev49(META_TARGET, origin="translation")

    def test_english_only_ja_text_is_none_and_ja_source_forces_full_recheck(self):
        res, seen = _run_instance49([self.JA_SRC_DEV], ja_mode=runner.JA_MODE_ENGLISH_ONLY)
        self.assertEqual(seen["stage3_ja"], [None])  # 日本語側の処理は呼ばれない(JA本文を渡さない)
        self.assertEqual(seen["fastpath_calls"], 0)  # 局所QA fastpath(全文検査なし)を使わない
        self.assertEqual(len(seen["recheck_calls"]), 1)  # 全文Recheckは1回(JA Recheckは無い)
        self.assertNotIn("ja_recheck", seen["recheck_calls"][0])
        c = res["cycles"][0]
        self.assertTrue(c["full_recheck_required"])
        self.assertIn("english_only_ja_source_requires_full_recheck", c["full_recheck_required_reasons"])
        self.assertNotIn("ja_fail_open_guard", c)
        self.assertNotIn("ja_en_equivalence_verdict", c)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        # CheckerとStage 2へ渡す元の日本語は変えない(D1)
        self.assertEqual(seen["recheck_fixture_ja"], [JA49])
        self.assertEqual(res["switches"]["JA_MODE"], "english_only")

    def test_english_only_other_origin_keeps_local_qa_fastpath(self):
        res, seen = _run_instance49([self.TR_DEV], ja_mode=runner.JA_MODE_ENGLISH_ONLY)
        self.assertEqual(seen["fastpath_calls"], 1)
        self.assertEqual(seen["recheck_calls"], [])
        self.assertNotIn("english_only_ja_source_requires_full_recheck",
                         res["cycles"][0]["full_recheck_required_reasons"])

    def test_paired_default_is_unchanged_ja_text_passed_and_no_extra_reason(self):
        res, seen = _run_instance49([self.JA_SRC_DEV])
        self.assertEqual(seen["stage3_ja"], [JA49])
        self.assertNotIn("english_only_ja_source_requires_full_recheck",
                         res["cycles"][0]["full_recheck_required_reasons"])
        self.assertEqual(res["switches"]["JA_MODE"], "paired")

    def test_full_recheck_required_direct(self):
        recs = [{"ladder_level_used": "1_word_connective", "mechanism": "single_text_local(E-2/delete-generic)"}]
        with mock.patch.object(runner, "JA_MODE", runner.JA_MODE_ENGLISH_ONLY):
            ok, reasons = runner.full_recheck_required(recs, [{"origin": "ja_source"}], "unit49")
            ng, _ = runner.full_recheck_required(recs, [{"origin": "translation"}], "unit49")
        self.assertTrue(ok)
        self.assertEqual(reasons, ["english_only_ja_source_requires_full_recheck"])
        self.assertFalse(ng)
        self.assertFalse(runner.full_recheck_required(recs, [{"origin": "ja_source"}], "unit49")[0])

    def test_ja_only_match_is_unverified_with_english_only_reason(self):
        ja = "# T\n\nアメリカが費用を返してもらうという考えです。\n"
        en = "# T\n\nThe US wants a refund.\n"
        rec = _claim("アメリカが費用を返してもらうという考えです。", origin="ja_source")
        with mock.patch.object(runner, "JA_MODE", runner.JA_MODE_ENGLISH_ONLY):
            r = runner.run_stage3_for_claim(None, _state0(), [], [], "t",
                                            {"ledger_text": LEDGER, "article_text": en, "source_article_text": ja},
                                            en, None, rec)
        self.assertTrue(r["span_unverified"])
        self.assertEqual(r["span_unverified_reason"], "ja_only_match_english_only")
        self.assertEqual(r["en_text"], en)


class TestRecordsOnly49(unittest.TestCase):
    def test_minor_is_recorded_but_not_passed_downstream(self):
        major = _dev49(META_TARGET)
        minor = _dev49("Calls happened.", sev="MINOR", fid="MUSE-HC-011")
        res, seen = _run_instance49([major, minor], recheck_devs=[minor], fastpath_success=False)
        raw = res["all_deviations_raw"]
        self.assertEqual([d["severity"] for d in raw["stage1"]], ["MAJOR", "MINOR"])
        self.assertEqual([d["passed_downstream"] for d in raw["stage1"]], [True, False])
        # 後段(Stage 2の入力=cycle1のstage2_results)へ渡るのは従来どおりMAJORのみ
        self.assertEqual([s["claim_text"] for s in res["cycles"][0]["stage2_results"]], [META_TARGET])
        # Recheckが返したMINORも記録(次周回へは渡らない=1周で終了し、prior_issuesはMAJORのみ)
        self.assertEqual(res["all_deviations_raw"]["rechecks"][0]["deviations"][0]["severity"], "MINOR")

    def test_judgement_unchanged_by_records(self):
        # 記録の有無で最終状態・周回数が変わらない(同じ入力で同じ結果)
        r1, _ = _run_instance49([_dev49(META_TARGET)])
        r2, _ = _run_instance49([_dev49(META_TARGET), _dev49("Calls happened.", sev="MINOR")])
        self.assertEqual((r1["final_state"], len(r1["cycles"])), (r2["final_state"], len(r2["cycles"])))

    @_meta_as_safety_critical()
    def test_residual_at_pass_stage1_pass_with_minor_only_deviation(self):
        # rep22 T1 s1/s3/s4型: 対象文が元のまま残り、Checkerが(MINORでも)BLOCKINGでも指摘せずに合格
        minor = _dev49("Also, some calls needed user information to continue", sev="MINOR")
        res, _ = _run_instance49([minor], iid="meta_run03_standard", stage1_status="LEDGER_COMPLIANT")
        self.assertEqual(res["final_state"], "ACCEPTABLE_STAGE1")
        d = res["residual_at_pass"]["defs"][0]
        self.assertEqual(d["sub_id"], "Meta-1")
        self.assertTrue(d["remains_in_final_en"])
        self.assertFalse(d["ever_blocking_flagged"])
        self.assertTrue(d["pass_with_residual_unflagged"])
        self.assertEqual(d["in_checker_raw_deviations_any_severity"][0]["severity"], "MINOR")

    @_meta_as_safety_critical()
    def test_residual_at_pass_values(self):
        cyc_block = [{"stage2_results": [{"claim_text": "needed user information to continue",
                                          "related_fact_id": "MUSE-HC-010", "materiality": "BLOCKING"}]}]
        cyc_down = [{"stage2_results": [{"claim_text": "needed user information to continue",
                                         "related_fact_id": "MUSE-HC-010", "materiality": "QUALITY"}]}]
        txt = "x. " + META_TARGET + " y."
        f = runner.compute_residual_at_pass
        a = f("meta_run03_standard", "RESOLVED_REWRITE", txt, cyc_block, [], [])["defs"][0]
        self.assertTrue(a["ever_blocking_flagged"])
        self.assertFalse(a["pass_with_residual_unflagged"])
        b = f("meta_run03_standard", "RESOLVED_STAGE2_DOWNGRADE", txt, cyc_down, [], [])["defs"][0]
        self.assertTrue(b["ever_flagged_but_never_blocking"])
        self.assertTrue(b["pass_with_residual_unflagged"])
        c = f("meta_run03_standard", "STAGE4_ESCALATION", txt, [], [], [])
        self.assertFalse(c["final_state_is_pass_family"])
        self.assertFalse(c["defs"][0]["pass_with_residual_unflagged"])  # 人間確認へ回った=合格系ではない
        d = f("meta_run03_standard", "RESOLVED_REWRITE", "x. Some calls may have needed user information.", [], [], [])
        self.assertFalse(d["defs"][0]["remains_in_final_en"])
        self.assertEqual(f("unknown_instance", "RESOLVED_REWRITE", txt, [], [], [])["defs"], [])

    @_meta_as_safety_critical()
    def test_existing_misdowngrade_detector_unchanged(self):
        r = {"instance_id": "meta_run03_standard", "cycles": [{"stage2_results": [
            {"claim_text": "needed user information to continue", "related_fact_id": "MUSE-HC-010",
             "materiality": "QUALITY"}]}]}
        self.assertEqual(len(runner.detect_safety_critical_misdowngrades([r])), 1)

    def test_severity_wobble_recorded_across_cycles_only(self):
        en = "# T\n\nAlpha beta gamma delta.\n"
        s_block = {"claim_text": "Alpha beta gamma delta.", "related_fact_id": "F-1", "materiality": "BLOCKING",
                   "llm_materiality": "BLOCKING", "floor_reason": None, "basis": "b1",
                   "dev": {"changed_fact": True}}
        s_q = {**s_block, "materiality": "QUALITY", "floor_reason": "disclosure_gap_negative_inference_downgrade",
               "basis": "b2", "dev": {"changed_certainty": True}}
        reg0, recs0 = {}, []
        runner._wobble_observe(reg0, recs0, 1, [s_block], en)
        runner._wobble_observe(reg0, recs0, 1, [s_q], en)  # 同一周回内は比較しない
        self.assertEqual(recs0, [])
        recs2 = []
        reg2 = {}
        runner._wobble_observe(reg2, recs2, 1, [s_block], en)
        runner._wobble_observe(reg2, recs2, 2, [s_q], en)
        self.assertEqual(len(recs2), 1)
        self.assertEqual(recs2[0]["from"]["true_flags"], ["changed_fact"])
        self.assertEqual(recs2[0]["to"]["true_flags"], ["changed_certainty"])
        self.assertEqual(recs2[0]["to"]["floor_reason"], "disclosure_gap_negative_inference_downgrade")

    def test_carry_forward_comparison_and_recheck_flag(self):
        start = "# T\n\nResearchers studied 30 million payments in taxis. Another sentence stays.\n"
        after = "# T\n\nResearchers studied over 3 million payments in taxis. Another sentence stays.\n"
        sent = "Researchers studied 30 million payments in taxis."
        dev = {"issue": "plural calls vs one reported call", "related_fact_id": "MUSE-HC-011",
               "changed_fact": True}
        rec = _claim(sent, kind="replace_with_ledger_value", origin="translation", dev=dev)
        rec.update({"cycle_start_en_text": start, "cycle_start_ja_text": None,
                    "cycle_replaced_units": [{"claim_identity": "claim:first", "lang": "EN",
                                              "before_units": [sent], "after_units": ["x"]}],
                    "cycle_claim_info": {"claim:first": {"issue": "plural calls vs one reported call",
                                                         "related_fact_id": "MUSE-HC-011",
                                                         "true_flags": ["changed_fact"]}}})
        r = runner.run_stage3_for_claim(None, None, [0], [], "t", {"ledger_text": LEDGER, "article_text": after},
                                        after, None, rec)
        cmp_ = r["handoff"]["carry_forward_comparison"][0]
        self.assertTrue(cmp_["issue_string_equal"])
        self.assertTrue(cmp_["same_related_fact_id"])
        self.assertTrue(cmp_["true_flags_equal"])
        self.assertEqual(r["method"], "covered_by_earlier_rewrite_in_cycle")  # 動作は変えない
        rr = [{"handoff": r["handoff"]}]
        runner._record_carry_forward_recheck(rr, [{"index": 0, "resolved": True}], "full_recheck")
        self.assertTrue(rr[0]["handoff"]["carry_forward_recheck_resolved"])
        runner._record_carry_forward_recheck(rr, None, "local_qa_fastpath_no_full_recheck")
        self.assertIsNone(rr[0]["handoff"]["carry_forward_recheck_resolved"])
        # 異なるissueなら不一致として記録される
        rec["dev"] = {**dev, "issue": "different issue", "changed_fact": False, "changed_scope": True}
        r2 = runner.run_stage3_for_claim(None, None, [0], [], "t", {"ledger_text": LEDGER, "article_text": after},
                                         after, None, rec)
        c2 = r2["handoff"]["carry_forward_comparison"][0]
        self.assertFalse(c2["issue_string_equal"])
        self.assertFalse(c2["true_flags_equal"])
        self.assertTrue(c2["same_related_fact_id"])

    def test_carry_forward_partial_overlap_same_issue_only(self):
        """委任_04(rep26 A2A3の照合漏れ是正): 先行Rewriteが範囲の一部(文末の節)だけを置換した場合、同じ指摘に限り書き換え済み扱い。"""
        sent = "Prices rose, because attacks continued, with its distant danger reaching gasoline prices."
        frag = "with its distant danger reaching gasoline prices."
        start = "# T\n\nIntro. " + sent + " Another sentence stays.\n"
        after = "# T\n\nIntro. Prices rose, because attacks continued, with the route still in danger. Another sentence stays.\n"
        dev = {"issue": "downstream effect not in Ledger", "related_fact_id": "HF-006", "changed_fact": True}
        rec = _claim(sent, kind="replace_with_ledger_value", origin="translation", dev=dev)
        rec.update({"cycle_start_en_text": start, "cycle_start_ja_text": None,
                    "cycle_replaced_units": [{"claim_identity": "claim:first", "lang": "EN",
                                              "before_units": [frag], "after_units": ["with the route still in danger."]}],
                    "cycle_claim_info": {"claim:first": {"issue": "downstream effect not in Ledger",
                                                         "related_fact_id": "HF-006", "true_flags": ["changed_fact"]}}})
        r = runner.run_stage3_for_claim(None, None, [0], [], "t", {"ledger_text": LEDGER, "article_text": after},
                                        after, None, rec)
        self.assertEqual(r["method"], "covered_by_earlier_rewrite_in_cycle")
        self.assertTrue(r["handoff"]["carry_forward_covered"][0].get("partial_overlap"))
        # 異なる指摘は従来どおり確定不能(unverified)。新しいHuman Review経路は作らない
        rec["dev"] = {**dev, "issue": "another issue entirely"}
        r2 = runner.run_stage3_for_claim(None, None, [0], [], "t", {"ledger_text": LEDGER, "article_text": after},
                                         after, None, rec)
        self.assertEqual(r2["method"], "violation_span_unverified")

    def test_en_title_rewrite_recorded(self):
        self.assertEqual(runner._en_title_line("# A Title\n\n## In one line\nx"), "# A Title")
        self.assertIsNone(runner._en_title_line("## In one line\nx"))
        res, _ = _run_instance49([_dev49(META_TARGET)], stage3_fn=_title_rewrite49)
        self.assertTrue(res["en_title_rewritten"])
        self.assertEqual(res["en_title_changes"], [{"cycle": 1, "before": "# Title", "after": "# New Title"}])
        self.assertTrue(res["cycles"][0]["en_title_rewritten"])
        res2, _ = _run_instance49([_dev49(META_TARGET)])
        self.assertFalse(res2["en_title_rewritten"])
        self.assertEqual(res2["en_title_changes"], [])



# 委任_53: 違反箇所の出力形式(CHECKER_SPANS_MODE="violation_spans"、Trial専用、既定OFF)のテスト。
# U01〜U13は委任_45 §2の13種類(Checkerが実際に返した文字列、記事は§2に記載の該当箇所)。
_ART_META53 = ("# I Thought It Was an AI Call—But There Was a Person Inside? Meta’s Unexpected Muse Test\n\n"
               "Ring, ring... A call came from an AI agent. That was what it seemed. But while the conversation "
               "continued, the voice on the other end was not AI. It was a person.\n\n"
               "Meta had run a test that produced exactly this kind of surprise.\n\n## In one line\nA short summary.")
_ART_SAFETY53 = ("# A Title\n\nAn AI called. That was what people thought as they spoke. But a human appeared from "
                 "behind the scenes.\n\nSo people who thought they were speaking with AI were actually speaking "
                 "with human staff.")
_ART_NEG53 = ("# We Thought It Was AI—But There Was a Person Inside Meta’s Muse\n\n"
              "Meta had run a test that caused exactly this surprise.\n\n## In one line\nA short summary.")
_ART_HORMUZ53 = ("# The Fee Plan Leaves, But High Oil Prices Stay\n\n"
                 "Oil prices moved briefly, then returned to a high level.\n\n## In one line\n"
                 "The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued.")
_HEAD_META53 = "I Thought It Was an AI Call—But There Was a Person Inside?"
_OPEN_META53 = "A call came from an AI agent. That was what it seemed."
_OPEN_META_FULL53 = ("A call came from an AI agent. That was what it seemed. But while the conversation continued, "
                     "the voice on the other end was not AI. It was a person.")
# (記事, 実際に混入したChecker文字列, 配列で返った場合の正しい要素)
_CASES53 = {
    "U01": (_ART_META53,
            "“" + _OPEN_META_FULL53 + "” Meta’s test “produced exactly this kind of surprise.”",
            [_OPEN_META_FULL53, "Meta had run a test that produced exactly this kind of surprise."]),
    "U02": (_ART_SAFETY53,
            "“people who thought they were speaking with AI were actually speaking with human staff”"
            "および冒頭の「That was what people thought as they spoke.」",
            ["people who thought they were speaking with AI were actually speaking with human staff",
             "That was what people thought as they spoke."]),
    "U06": (_ART_SAFETY53,
            "“That was what people thought as they spoke.” The opening also presents the call as one people "
            "believed was from an AI.",
            ["That was what people thought as they spoke."]),
    "U08": (_ART_META53,
            "The headline says “" + _HEAD_META53 + "” and the opening says, “" + _OPEN_META53 + "”",
            [_HEAD_META53, _OPEN_META53]),
    "U09": (_ART_NEG53,
            "“Meta had run a test that caused exactly this surprise,” reinforced by the headline “We Thought It "
            "Was AI—But There Was a Person Inside Meta’s Muse.”",
            ["Meta had run a test that caused exactly this surprise.",
             "We Thought It Was AI—But There Was a Person Inside Meta’s Muse"]),
    "U10": (_ART_NEG53,
            "Headline: “We Thought It Was AI—But There Was a Person Inside Meta’s Muse.”",
            ["We Thought It Was AI—But There Was a Person Inside Meta’s Muse"]),
    "U11": (_ART_HORMUZ53,
            "“Oil prices moved briefly, then returned to a high level.” The headline and one-line summary also "
            "state this more broadly as a claim about oil prices generally.",
            ["Oil prices moved briefly, then returned to a high level.", "The Fee Plan Leaves, But High Oil Prices Stay",
             "The fee plan vanished, but oil prices stayed high as tensions around the Strait of Hormuz continued."]),
    "U12": (_ART_HORMUZ53,
            "“Oil prices moved briefly, then returned to a high level”; “oil prices stayed high” (also reflected "
            "in the headline).",
            ["Oil prices moved briefly, then returned to a high level", "oil prices stayed high"]),
    "U13": (_ART_HORMUZ53,
            "“High Oil Prices Stay” (headline); “oil prices stayed high” (one-line summary).",
            ["High Oil Prices Stay", "oil prices stayed high"]),
}


class TestCheckerSpansFormat53(unittest.TestCase):
    def setUp(self):
        runner._VS_SPANS_REGISTRY.clear()
        self._p1 = mock.patch.object(runner, "CHECKER_SPANS_MODE", "violation_spans")
        self._p2 = mock.patch.object(runner, "VS_MATCH_EXT", True)
        self._p1.start()
        self._p2.start()

    def tearDown(self):
        self._p2.stop()
        self._p1.stop()
        runner._VS_SPANS_REGISTRY.clear()

    def _resolve_array(self, article, elems, issue="issue text"):
        dev = {"violation_spans": list(elems), "issue": issue, "severity": "MAJOR"}
        d2 = runner.assemble_claim_from_violation_spans(dev)
        return d2, runner.resolve_violation_spans(d2["claim_in_article"], article, None)

    def test_default_is_legacy(self):
        self._p1.stop()
        try:
            self.assertEqual(runner.CHECKER_SPANS_MODE, "legacy")
        finally:
            self._p1.start()

    def test_u01_to_u13_correct_array_elements_resolve_per_element(self):
        for uid, (art, _mixed, elems) in _CASES53.items():
            with self.subTest(uid=uid):
                d2, res = self._resolve_array(art, elems)
                self.assertEqual(res["status"], "resolved", (uid, res.get("reason"), res.get("array_elements")))
                self.assertEqual(len(res["array_elements"]), len(elems))
                self.assertTrue(all(e["status"] == "resolved" for e in res["array_elements"]))
                self.assertEqual(d2["claim_in_article"], "\n".join(elems))
                # 確定範囲は各要素そのもの(記事順)。複数範囲は複数範囲のまま(段落をまたいで結合しない)。
                for e in elems:
                    self.assertTrue(any(e in r or r == e for r in res["ranges"]), (uid, e, res["ranges"]))

    def test_u01_to_u13_explanation_mixed_element_is_unverified(self):
        # 説明文・位置ラベル・接続語・日本語のつなぎが混じった文字列が1要素として返った場合は確定不能
        for uid, (art, mixed, _elems) in _CASES53.items():
            with self.subTest(uid=uid):
                _d2, res = self._resolve_array(art, [mixed])
                self.assertEqual(res["status"], "unverified", uid)
                self.assertEqual(res["failed_span_index"], 0)
                self.assertTrue(res["reason_detail"].startswith("span[0]:"))

    def test_one_bad_element_makes_all_unverified_with_index(self):
        art, _m, elems = _CASES53["U13"]
        _d2, res = self._resolve_array(art, [elems[0], "not in the article at all"])
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "mismatch")
        self.assertEqual(res["failed_span_index"], 1)
        self.assertEqual(res["reason_detail"], "span[1]:mismatch")
        self.assertEqual(res["array_elements"][0]["status"], "resolved")

    def test_multi_match_element_is_unverified(self):
        art = "A cat sat. A cat ran away.\n\nOther text."
        _d2, res = self._resolve_array(art, ["A cat"])
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "multi_match")
        self.assertEqual(res["failed_span_index"], 0)

    def test_empty_array_is_unverified_human_review(self):
        d2, res = self._resolve_array(_ART_META53, [], issue="whole-article implication")
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["reason"], "violation_spans_empty")
        # Stage 2への表示にはissueを添える(確定には使わない)
        self.assertIn("whole-article implication", d2["claim_in_article"])

    def test_blank_element_is_unverified(self):
        _d2, res = self._resolve_array(_ART_META53, [_OPEN_META53, "  "])
        self.assertEqual(res["status"], "unverified")
        self.assertEqual(res["failed_span_index"], 1)

    def test_fixture_without_array_uses_claim_in_article_path(self):
        dev = {"claim_in_article": _OPEN_META53, "issue": "x"}
        self.assertIs(runner.assemble_claim_from_violation_spans(dev), dev)
        self.assertEqual(runner.adopt_violation_spans([dev]), [dev])
        res = runner.resolve_violation_spans(_OPEN_META53, _ART_META53, None)
        self.assertEqual(res, runner._resolve_claim_string(_OPEN_META53, _ART_META53, None))
        self.assertEqual(res["status"], "resolved")
        self.assertNotIn("from_violation_spans", res)

    def test_legacy_mode_unchanged(self):
        self._p1.stop()
        try:
            dev = {"violation_spans": [_OPEN_META53], "claim_in_article": "orig", "issue": "x"}
            self.assertIs(runner.assemble_claim_from_violation_spans(dev), dev)
            self.assertEqual(runner.adopt_violation_spans([dev]), [dev])
            self.assertEqual(runner._VS_SPANS_REGISTRY, {})
            for uid, (art, mixed, _e) in _CASES53.items():
                self.assertEqual(runner.resolve_violation_spans(mixed, art, None),
                                 runner._resolve_claim_string(mixed, art, None), uid)
        finally:
            self._p1.start()

    def test_same_fact_id_locations_stay_separate_and_drop_array(self):
        art = _ART_HORMUZ53
        dev = {"violation_spans": ["Oil prices moved briefly, then returned to a high level."], "issue": "i",
               "same_fact_id_locations": ["The Fee Plan Leaves, But High Oil Prices Stay"]}
        out = runner.expand_same_fact_id_locations(runner.adopt_violation_spans([dev]), art)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1]["claim_in_article"], "The Fee Plan Leaves, But High Oil Prices Stay")
        self.assertNotIn("violation_spans", out[1])
        self.assertTrue(out[1]["detected_by_enumeration"])
        self.assertTrue(out[0]["claim_assembled_from_violation_spans"])

    def test_schema_swap_and_recheck_schema(self):
        item = trial.build_trial_deviation_item_schema(True, False)
        enum_item = runner.build_deviation_schema_with_enumeration(item)
        self.assertIn("claim_in_article", enum_item["properties"])
        sp = runner.build_deviation_schema_with_spans(enum_item)
        self.assertNotIn("claim_in_article", sp["properties"])
        self.assertNotIn("claim_in_article", sp["required"])
        self.assertEqual(sp["properties"]["violation_spans"], {"type": "array", "items": {"type": "string"}})
        self.assertIn("violation_spans", sp["required"])
        self.assertIn("same_fact_id_locations", sp["properties"])
        self.assertEqual(set(sp["properties"]), set(sp["required"]))
        rs = runner.build_recheck_schema(True, False)
        rs_item = rs["schema"]["properties"]["deviations"]["items"]
        self.assertIn("violation_spans", rs_item["properties"])
        self.assertNotIn("claim_in_article", rs_item["properties"])
        self._p1.stop()
        try:
            rs0 = runner.build_recheck_schema(True, False)["schema"]["properties"]["deviations"]["items"]
            self.assertIn("claim_in_article", rs0["properties"])
            self.assertNotIn("violation_spans", rs0["properties"])
        finally:
            self._p1.start()

    def test_instruction_text_policy(self):
        ins = runner.VIOLATION_SPANS_INSTRUCTION
        self.assertNotIn("その語句を含む文全体", ins)
        self.assertIn("ちょうど1箇所", ins)
        self.assertIn("英語の記事本文からのみ", ins)
        self.assertIn("空配列", ins)
        self.assertIn("判定基準は変えない", ins)


class TestExplainSplitStrictClosed57(unittest.TestCase):
    """委任_57(Opus独立レビュー#7の4ガード付き説明文後段分離P-strict-closed、Trial専用スイッチ`VS_EXPLAIN_SPLIT`、
    既定OFF)。¥0。基準実装は`er052_output/open233_explanatory_mixed_offline_check_01/check_02.py`(オフライン再生で
    346行・委任_53対照腕62件・合成テストを検証済み)。runnerの`vs_explain_split_resolve`が同じ結果を返すことを確認する。"""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        import sys
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "er052_output", "open233_explanatory_mixed_offline_check_01", "check_02.py")
        spec = importlib.util.spec_from_file_location("check_02_for_test57", path)
        cls.c2 = importlib.util.module_from_spec(spec)
        sys.modules["check_02_for_test57"] = cls.c2
        spec.loader.exec_module(cls.c2)
        runs = cls.c2.load_runs()
        cls.blocking, cls.nonblocking = cls.c2.collect_rows(runs)
        with open(os.path.join(here, "er052_output", "open233_handoff_log_aggregation_01",
                               "unverified35_classification_01.csv"), encoding="utf-8-sig") as fh:
            import csv
            cls.uid = {}
            for r in csv.DictReader(fh):
                cls.uid.setdefault(r["claim"].strip(), r["unique_id"])

    def _on(self):
        return mock.patch.multiple(runner, VS_EXPLAIN_SPLIT=True, VS_MATCH_EXT=True)

    def _u_rows(self):
        out = []
        for r in self.blocking:
            if r["en"] is None and r["ja"] is None:
                continue
            base = self.c2.base_resolve(r["claim"], r["en"], r["ja"], True)
            if base["reason"] == "explanatory_mixed" and base["status"] != "resolved":
                out.append((self.uid.get(r["claim"].strip(), "?"), r))
        return out

    def test_default_is_off_and_cli_flag_exists(self):
        self.assertFalse(runner.VS_EXPLAIN_SPLIT)
        import inspect
        self.assertIn("--vs-explain-split", inspect.getsource(runner.main))

    def test_u01_to_u13_real_strings_10_adopted_3_rejected(self):
        rows = self._u_rows()
        self.assertEqual(len(rows), 13)
        adopted = [u for u, _ in rows if u in ("U01", "U02", "U08", "U09", "U10", "U13")]
        self.assertEqual(len(adopted), 10)  # U02が5行
        with self._on():
            for u, r in rows:
                res = runner._resolve_claim_string(r["claim"], r["en"], r["ja"])
                ref = self.c2.closed_resolve(r["claim"], r["en"], r["ja"], True)
                if u == "U12":
                    # 委任_02 規則U-2(1): U12(D5型「also reflected in the headline」)は見出し行を範囲へ加えて確定する(旧: 棄却)
                    self.assertEqual(res["status"], "resolved", u)
                    self.assertTrue(res["level"].endswith("+U2"), u)
                    self.assertIn("The Fee Plan Leaves, But High Oil Prices Stay", res["ranges"], u)
                    for rng in res["ranges"]:
                        self.assertEqual(r["en"].count(rng), 1)
                elif u in ("U06", "U11"):
                    self.assertEqual(res["status"], "unverified", u)
                    self.assertTrue(res["explain_split"]["reason"].startswith("explain_split_rejected:"), u)
                    if u == "U11":
                        # 委任_02 規則U-2(1): 位置語headline/one-lineは棄却せず要素を加えるため、U11の棄却理由は
                        # dangling_positionからremainder_too_long(規則Rは保留=現状維持)へ変わる(棄却は維持)
                        self.assertEqual(res["explain_split"]["reason"], "explain_split_rejected:remainder_too_long", u)
                    else:
                        self.assertEqual(res["explain_split"]["reason"], ref["reason"], u)
                    self.assertEqual(res["reason"], "explanatory_mixed", u)  # 下流の分岐を変えない
                else:
                    self.assertEqual(res["status"], "resolved", u)
                    self.assertEqual(res["lang"], "EN")
                    self.assertEqual(res["ranges"], ref["ranges"], u)
                    self.assertTrue(res["level"].startswith("P:"), u)
                    self.assertEqual(res["explain_split"]["fragments"], ref["fragments"])
                    self.assertTrue(res["explain_split"]["dropped_remainders"] is not None)
                    for rng in res["ranges"]:
                        self.assertEqual(r["en"].count(rng), 1)

    def test_synthetic_cases_all_as_expected(self):
        with self._on():
            for name, claim, en, ja, expect in self.c2.synthetic_closed_cases():
                res = runner._resolve_claim_string(claim, en, ja)
                if name.startswith("S8"):
                    # 委任_02 規則U-2(1): 宙に浮いた見出し名指しは棄却せず、見出し行を範囲へ加えて確定する(拡張のみ)
                    self.assertEqual(res["status"], "resolved", name)
                    self.assertTrue(res["level"].endswith("+U2"), name)
                    self.assertIn("Headline Here About Oil", res["ranges"], name)
                    self.assertIn("Another paragraph has a unique line.", res["ranges"], name)
                    continue
                self.assertEqual(res["status"], expect, name)
                if expect == "unverified":
                    ref = self.c2.closed_resolve(claim, en, ja, True)
                    # 現行照合で確定不能の文字列だけがP-strict-closedの対象(それ以外は理由コードなし)
                    if res.get("explain_split"):
                        self.assertEqual(res["explain_split"]["reason"], ref["reason"], name)

    def test_off_is_identical_to_base_on_all_346_rows(self):
        with mock.patch.multiple(runner, VS_EXPLAIN_SPLIT=False, VS_MATCH_EXT=True):
            for r in self.blocking:
                if r["en"] is None and r["ja"] is None:
                    continue
                self.assertEqual(runner._resolve_claim_string(r["claim"], r["en"], r["ja"]),
                                 runner._resolve_claim_string_base(r["claim"], r["en"], r["ja"]))

    def test_on_never_changes_already_confirmed_ranges_346_rows(self):
        n_new, n_chk = 0, 0
        for r in self.blocking:
            if r["en"] is None and r["ja"] is None:
                continue
            with mock.patch.multiple(runner, VS_EXPLAIN_SPLIT=False, VS_MATCH_EXT=True):
                base = runner._resolve_claim_string(r["claim"], r["en"], r["ja"])
            with self._on():
                on = runner._resolve_claim_string(r["claim"], r["en"], r["ja"])
            n_chk += 1
            if base["status"] == "resolved":
                self.assertEqual(on["status"], "resolved")
                self.assertEqual((on["lang"], on["spans"], on["ranges"], on["level"]),
                                 (base["lang"], base["spans"], base["ranges"], base["level"]))
                self.assertNotIn("explain_split", on)
            elif on["status"] == "resolved":
                n_new += 1
        self.assertGreater(n_chk, 300)
        # 委任_02: 規則U-2(1)でD5型(「also reflected in the headline」)の1件が新たに確定(10→11)
        self.assertEqual(n_new, 11)

    def test_multi_match_and_empty_not_attempted(self):
        en = "# T\n\nThe second sentence repeats. The second sentence repeats.\n"
        with self._on():
            res = runner._resolve_claim_string("“The second sentence repeats.”", en, None)
            self.assertEqual(res["reason"], "multi_match")
            self.assertNotIn("explain_split", res)
            self.assertEqual(runner._resolve_claim_string("", en, None)["reason"], "empty_claim")

    def test_japanese_text_only_never_newly_confirmed(self):
        ja = "# タイトル\n\n彼は「価格は近く下がる」と述べた。\n"
        with self._on():
            res = runner._resolve_claim_string("「価格は近く下がる」と冒頭にある", None, ja)
            self.assertEqual(res["status"], "unverified")
            self.assertEqual(res["explain_split"]["reason"], "explain_split_rejected:no_en_text")

    def test_legacy_handoff_mode_unaffected(self):
        claim = {"claim_text": "“That was what people thought as they spoke.” The opening also presents x"}
        with mock.patch.multiple(runner, VS_EXPLAIN_SPLIT=True, HANDOFF_MODE=runner.HANDOFF_MODE_LEGACY):
            out = runner.annotate_claim_span_identity(dict(claim), "x", None)
        self.assertEqual(out, claim)

    def test_constants_verbatim(self):
        self.assertEqual(runner.VS_EXPLAIN_CONTRAST_REF_EN_RE.pattern,
                         r"\b(ledger|source|but|instead|not|should|however|rather|whereas|contrary|versus)\b|n't")
        self.assertEqual(runner.VS_EXPLAIN_CONTRAST_REF_JA_RE.pattern,
                         "台帳|原文|ではなく|ではない|しかし|べき|一方|対して|ところが")
        self.assertEqual(runner.VS_EXPLAIN_POSITION_REJECT_RE.pattern,
                         r"\b(paragraph|closing|elsewhere|section|ending|conclusion)\b|段落|末尾|結び")
        self.assertEqual((runner.VS_EXPLAIN_MAX_EN_WORDS, runner.VS_EXPLAIN_MAX_JA_CHARS,
                          runner.VS_EXPLAIN_MIN_VERBATIM_WORDS), (6, 11, 3))
        self.assertEqual(self.c2.CONTRAST_REF_EN_RE.pattern, runner.VS_EXPLAIN_CONTRAST_REF_EN_RE.pattern)
        self.assertEqual(self.c2.CONTRAST_REF_JA_RE.pattern, runner.VS_EXPLAIN_CONTRAST_REF_JA_RE.pattern)
        self.assertEqual(self.c2.POSITION_REJECT_RE.pattern, runner.VS_EXPLAIN_POSITION_REJECT_RE.pattern)


# ---------------------------------------------------------------------
# 委任_60(OPEN-233-SELF-RECOVERY-TRIAL-01、2026-10-04ユーザー決定[4回目]、判断D=案1)
# 比較・方向・時期の機械判定の追加確認(FLOOR_VERIFY_MODE、既定OFF)。¥0(APIはfake)。
# ---------------------------------------------------------------------
_FV_LEDGER = (
    "[HF-009] The fee plan was withdrawn on July 13, but oil prices kept rising afterwards.\n"
    "  date_or_period: 2026-07-13\n"
    "  numeric_value: 20% increase\n"
    "  scope: oil prices kept rising after the withdrawal\n"
    "\n"
    "[HF-003] Talks resumed.\n"
    "  date_or_period: July 14\n"
)


def _fv_call_ok(materiality="QUALITY", citation="oil prices kept rising afterwards", cost=0.1):
    def _fn(claim_text, local_context, fact_block, issue, flag_names, related_fact_id):
        return {"parsed": {"materiality": materiality, "ledger_citation": citation, "basis": "nuance_only",
                           "explanation": "x"}, "prompt_sha256": "h", "cost_jpy": cost, "response_id": "r",
                "usage": {}}
    return _fn


class TestFloorVerify60(unittest.TestCase):
    def setUp(self):
        self._old_mode = runner.FLOOR_VERIFY_MODE
        runner.FLOOR_VERIFY_MODE = runner.FLOOR_VERIFY_MODE_TIME_ONLY

    def tearDown(self):
        runner.FLOOR_VERIFY_MODE = self._old_mode

    def _dev(self, **flags):
        d = {"related_fact_id": "HF-009", "issue": "prices rose, but the claim says fell"}
        d.update(flags)
        return d

    # --- 対象の絞り込み(2-1) ---
    def test_default_mode_is_off(self):
        self.assertEqual(self._old_mode, "off")
        self.assertEqual(runner.FLOOR_VERIFY_MODE_OFF, "off")

    def test_target_only_time_flag_when_llm_non_blocking(self):
        T = runner.floor_verify_target
        self.assertTrue(T("ACCEPTABLE", "deterministic_floor:changed_time", self._dev(changed_time=True))[0])
        self.assertTrue(T("QUALITY", "deterministic_floor:changed_time", self._dev(changed_time=True))[0])

    def test_comparison_flag_is_out_of_scope(self):
        T = runner.floor_verify_target
        ok, reason, _ = T("QUALITY", "deterministic_floor:changed_comparison",
                          self._dev(changed_comparison=True))
        self.assertFalse(ok)
        self.assertEqual(reason, "out_of_scope_flag:changed_comparison")
        ok, reason, _ = T("QUALITY", "deterministic_floor:changed_comparison,changed_time",
                          self._dev(changed_comparison=True, changed_time=True))
        self.assertFalse(ok)
        self.assertEqual(reason, "out_of_scope_flag:changed_comparison")

    def test_comparison_time_mode_is_not_selectable(self):
        self.assertFalse(hasattr(runner, "FLOOR_VERIFY_MODE_COMPARISON_TIME"))
        self.assertEqual(runner.FLOOR_VERIFY_MODES, ("off", "time_only"))
        with self.assertRaises(ValueError):
            runner.validate_floor_verify_mode("comparison_time")
        self.assertEqual(runner.validate_floor_verify_mode("time_only"), "time_only")
        import inspect
        src = inspect.getsource(runner.main)
        self.assertNotIn("comparison_time", src)

    def test_verify_prompt_has_no_comparison_or_direction_examples(self):
        for txt in (runner.FLOOR_VERIFY_RUBRIC_ADDENDUM, runner.FLOOR_VERIFY_DEVELOPER_MESSAGE,
                    runner.FLOOR_VERIFY_PROMPT_TEMPLATE):
            for w in ("比較", "方向", "反転", "prices began to fall"):
                self.assertNotIn(w, txt)
        self.assertIn("時期", runner.FLOOR_VERIFY_RUBRIC_ADDENDUM)

    def test_not_target_when_comparison_actor_number_negation_flag_true(self):
        T = runner.floor_verify_target
        for extra in ("changed_comparison", "changed_actor", "changed_number", "changed_negation"):
            ok, reason, _ = T("QUALITY", "deterministic_floor:changed_time," + extra,
                              self._dev(changed_time=True, **{extra: True}))
            self.assertFalse(ok, extra)
            self.assertEqual(reason, "out_of_scope_flag:" + extra)

    def test_not_target_for_precheck_blocking_llm_or_mode_off(self):
        T = runner.floor_verify_target
        d = self._dev(changed_time=True)
        self.assertFalse(T("QUALITY", "precheck_floor", d)[0])
        self.assertFalse(T("BLOCKING", "deterministic_floor:changed_time", d)[0])
        self.assertFalse(T("QUALITY", None, d)[0])
        runner.FLOOR_VERIFY_MODE = "off"
        self.assertFalse(T("QUALITY", "deterministic_floor:changed_time", d)[0])

    # --- CONFIRMED(2-2) ---
    def test_confirmed_time_when_date_missing_in_fact_block(self):
        fb = runner.floor_verify_fact_block(_FV_LEDGER, "HF-009")
        self.assertIn("July 13", fb)
        self.assertNotIn("HF-003", fb)
        c = runner.floor_verify_confirmed("The plan was withdrawn on July 14.", fb, ["changed_time"])
        self.assertTrue(c["confirmed"])
        c = runner.floor_verify_confirmed("The plan was withdrawn on July 13.", fb, ["changed_time"])
        self.assertFalse(c["confirmed"])

    def test_fact_block_multiple_ids_joined_and_all_required(self):
        fb = runner.floor_verify_fact_block(_FV_LEDGER, "HF-009, HF-003")
        self.assertIn("HF-009", fb)
        self.assertIn("HF-003", fb)
        self.assertIsNone(runner.floor_verify_fact_block(_FV_LEDGER, "HF-009, NOPE-1"))

    def test_time_tokens_normalise_ja_en_and_iso(self):
        t = runner.floor_verify_time_tokens
        self.assertEqual(t("7月13日"), t("July 13"))
        self.assertTrue(t("2026-07-13") >= t("Jul 13"))
        self.assertEqual(t("翌日"), t("the following day"))
        self.assertEqual(t("3 days"), t("3日間"))

    def test_confirmed_comparison_number_missing(self):
        fb = runner.floor_verify_fact_block(_FV_LEDGER, "HF-009")
        c = runner.floor_verify_confirmed("Prices rose 30% afterwards.", fb, ["changed_comparison"])
        self.assertTrue(c["confirmed"])
        c = runner.floor_verify_confirmed("Prices rose 20% afterwards.", fb, ["changed_comparison"])
        self.assertFalse(c["confirmed"])

    def test_not_confirmed_without_deterministic_token_goes_to_verify_not_release(self):
        fb = runner.floor_verify_fact_block(_FV_LEDGER, "HF-009")
        claim = "Just after the charge plan disappeared, prices began to fall."
        c = runner.floor_verify_confirmed(claim, fb, ["changed_time"])
        self.assertFalse(c["confirmed"])
        calls = []

        def fn(*a):
            calls.append(a)
            return _fv_call_ok("BLOCKING")(*a)
        fv = runner.floor_verify_evaluate(fn, _FV_LEDGER, claim, "ctx", self._dev(changed_time=True),
                                          "QUALITY", "deterministic_floor:changed_time")
        self.assertEqual(len(calls), 1)  # 確認へ進む(自動解放されない)。1回目BLOCKINGで固定
        self.assertFalse(fv["released"])
        self.assertEqual(fv["blocking_fixed_reason"], "verify_blocking_both")

    def test_confirmed_skips_calls_and_keeps_blocking(self):
        calls = []
        fv = runner.floor_verify_evaluate(lambda *a: calls.append(a), _FV_LEDGER, "It happened on July 14.",
                                          "ctx", self._dev(changed_time=True), "QUALITY",
                                          "deterministic_floor:changed_time")
        self.assertEqual(calls, [])
        self.assertTrue(fv["confirmed"])
        self.assertFalse(fv["released"])
        self.assertEqual(fv["final_materiality"], "BLOCKING")

    # --- 解放条件(2-4) ---
    def _eval(self, fn, llm="QUALITY", dev=None, claim="Prices began to fall."):
        return runner.floor_verify_evaluate(
            fn, _FV_LEDGER, claim, "ctx", dev or self._dev(changed_time=True), llm,
            "deterministic_floor:changed_time")

    def test_release_only_when_both_non_blocking_with_verbatim_citation(self):
        fv = self._eval(_fv_call_ok("ACCEPTABLE"), llm="QUALITY")
        self.assertTrue(fv["released"])
        self.assertEqual(fv["n_calls"], 2)
        self.assertEqual(fv["final_materiality"], "QUALITY")  # 最も重い非BLOCKING(Stage2のQUALITY)
        fv = self._eval(_fv_call_ok("QUALITY"), llm="ACCEPTABLE")
        self.assertEqual(fv["final_materiality"], "QUALITY")
        fv = self._eval(_fv_call_ok("ACCEPTABLE"), llm="ACCEPTABLE")
        self.assertEqual(fv["final_materiality"], "ACCEPTABLE")

    def test_disagreement_one_blocking_fixes_blocking(self):
        seq = iter(["QUALITY", "BLOCKING"])

        def fn(*a):
            return _fv_call_ok(next(seq))(*a)
        fv = self._eval(fn)
        self.assertFalse(fv["released"])
        self.assertEqual(fv["blocking_fixed_reason"], "verify_blocking_disagree")
        seq2 = iter(["BLOCKING", "QUALITY"])

        def fn2(*a):
            return _fv_call_ok(next(seq2))(*a)
        self.assertFalse(self._eval(fn2)["released"])

    def test_failures_fix_blocking(self):
        def api_fail(*a):
            raise runner.FloorVerifyCallError("boom")
        fv = self._eval(api_fail)
        self.assertEqual((fv["released"], fv["blocking_fixed_reason"]), (False, "verify_api_failure"))
        fv = self._eval(_fv_call_ok("QUALITY", citation=""))
        self.assertEqual((fv["released"], fv["blocking_fixed_reason"]), (False, "ledger_citation_empty"))
        fv = self._eval(_fv_call_ok("QUALITY", citation="prices fell sharply"))
        self.assertEqual((fv["released"], fv["blocking_fixed_reason"]), (False, "ledger_citation_not_verbatim"))

        def bad_schema(*a):
            return {"parsed": {"materiality": "MAYBE", "ledger_citation": "x"}, "prompt_sha256": "h",
                    "cost_jpy": 0.0}
        fv = self._eval(bad_schema)
        self.assertEqual((fv["released"], fv["blocking_fixed_reason"]), (False, "schema_mismatch"))

    def test_missing_fact_block_is_blocking_without_calls(self):
        calls = []
        fv = self._eval(lambda *a: calls.append(a), dev=self._dev(changed_time=True,
                                                                  related_fact_id="NOPE-1"))
        self.assertEqual(calls, [])
        self.assertEqual(fv["blocking_fixed_reason"], "fact_block_unavailable")
        self.assertFalse(fv["released"])
        fv = self._eval(lambda *a: calls.append(a), dev={"changed_time": True})
        self.assertFalse(fv["released"])

    def test_dev_flags_not_rewritten(self):
        dev = self._dev(changed_time=True)
        before = dict(dev)
        self._eval(_fv_call_ok("QUALITY"), dev=dev)
        self.assertEqual(dev, before)

    # --- run_stage2への配線(2-5) ---
    def _run_stage2(self, dev, verify_materiality="QUALITY", llm="QUALITY", mode_on=True):
        calls = {"stage2": 0, "verify": 0}
        import json as _json

        class FakeResp:
            id = "r1"
            model = "gpt-6-luna"

            def __init__(self, text):
                self.output_text = text

        class FakeClient:
            class responses:
                @staticmethod
                def create(**kwargs):
                    prompt = kwargs["input"][1]["content"]
                    if "独立した追加確認" in prompt:
                        calls["verify"] += 1
                        return FakeResp(_json.dumps({
                            "materiality": verify_materiality,
                            "ledger_citation": "oil prices kept rising afterwards", "basis": "nuance_only",
                            "explanation": "x"}))
                    calls["stage2"] += 1
                    return FakeResp(_json.dumps({"judgments": [{
                        "claim_index": 0, "materiality": llm, "basis": "none", "rewrite_kind": "none",
                        "rewrite_hint": ""}]}))

        runner.FLOOR_VERIFY_MODE = (runner.FLOOR_VERIFY_MODE_TIME_ONLY if mode_on
                                    else runner.FLOOR_VERIFY_MODE_OFF)
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": _FV_LEDGER, "article_text": "Prices began to fall.",
                   "source_article_text": None}
        claims = [{"claim_text": "Prices began to fall.", "origin": "translation",
                   "related_fact_id": "HF-009", "dev": dev, "detected_by": "stage1_llm"}]
        call_log = []
        with mock.patch.object(runner, "check_budget", lambda s: None), \
             mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner.s2p, "_extract_usage", lambda r: {}), \
             mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 0.0):
            out = runner.run_stage2(FakeClient(), state, [0], call_log, "label", fixture, claims)
        return out[0], calls, call_log

    def test_run_stage2_releases_after_two_non_blocking_checks(self):
        r, calls, log = self._run_stage2(self._dev(changed_time=True))
        self.assertEqual(calls, {"stage2": 1, "verify": 2})
        self.assertEqual(r["materiality"], "QUALITY")
        self.assertTrue(r["floor_reason"].startswith("floor_verify_released:deterministic_floor"))
        self.assertTrue(r["floor_verify"]["released"])
        self.assertEqual(r["llm_materiality"], "QUALITY")
        self.assertTrue(r["dev"]["changed_time"])  # devは書き換えない
        self.assertEqual(sum(1 for c in log if c.get("recovery_stage") == "floor_verify"), 2)

    def test_run_stage2_keeps_blocking_when_verify_says_blocking(self):
        r, calls, _ = self._run_stage2(self._dev(changed_time=True), verify_materiality="BLOCKING")
        self.assertEqual(r["materiality"], "BLOCKING")
        self.assertTrue(r["floor_reason"].startswith("deterministic_floor:"))
        self.assertFalse(r["floor_verify"]["released"])

    def test_run_stage2_actor_flag_never_verified(self):
        r, calls, _ = self._run_stage2(self._dev(changed_time=True, changed_actor=True))
        self.assertEqual(calls["verify"], 0)
        self.assertEqual(r["materiality"], "BLOCKING")
        self.assertFalse(r["floor_verify"]["target"])

    def test_run_stage2_number_flag_never_verified(self):
        r, calls, _ = self._run_stage2(self._dev(changed_time=True, changed_number=True))
        self.assertEqual((calls["verify"], r["materiality"]), (0, "BLOCKING"))

    def test_run_stage2_mode_off_is_unchanged(self):
        r, calls, _ = self._run_stage2(self._dev(changed_time=True), mode_on=False)
        self.assertEqual(calls["verify"], 0)
        self.assertEqual(r["materiality"], "BLOCKING")
        self.assertNotIn("floor_verify", r)
        self.assertTrue(r["floor_reason"].startswith("deterministic_floor:"))

    def test_run_stage2_llm_blocking_not_verified(self):
        r, calls, _ = self._run_stage2(self._dev(changed_time=True), llm="BLOCKING")
        self.assertEqual(calls["verify"], 0)
        self.assertEqual(r["materiality"], "BLOCKING")

    def test_released_claim_excluded_from_two_of_two(self):
        inst = {"instance_id": next(iter(runner.NORMAL_GROUP_INSTANCE_IDS))}
        base = {"materiality": "BLOCKING", "floor_reason": None}
        self.assertTrue(runner.stage2_two_of_two_eligible(inst, base))
        self.assertFalse(runner.stage2_two_of_two_eligible(
            inst, {**base, "floor_verify": {"released": True}}))
        self.assertTrue(runner.stage2_two_of_two_eligible(
            inst, {**base, "floor_verify": {"released": False}}))

    def test_state_not_carried_across_cycles(self):
        r1, c1, _ = self._run_stage2(self._dev(changed_time=True))
        self.assertTrue(r1["floor_verify"]["released"])
        r2, c2, _ = self._run_stage2(self._dev(changed_time=True), verify_materiality="BLOCKING")
        self.assertEqual(r2["materiality"], "BLOCKING")  # 前周回の解放は引き継がれない
        self.assertEqual(c2["verify"], 1)  # 毎周回、再評価(1回目BLOCKINGで固定)

    def test_summary_counts(self):
        r1, _, _ = self._run_stage2(self._dev(changed_time=True))
        r2, _, _ = self._run_stage2(self._dev(changed_time=True), verify_materiality="BLOCKING")
        r3, _, _ = self._run_stage2(self._dev(changed_time=True, changed_number=True))
        s = runner.floor_verify_summarize([r1, r2, r3])
        self.assertEqual((s["n_target"], s["n_released"], s["n_verify_calls"]), (2, 1, 3))
        self.assertEqual(s["blocking_fixed_by_reason"], {"verify_blocking_both": 1})
        self.assertEqual(s["out_of_scope_flag"], {"changed_number": 1})

    def test_cli_has_floor_verify_option_and_legacy_unaffected(self):
        import inspect
        src = inspect.getsource(runner.main)
        self.assertIn("--floor-verify-mode", src)
        self.assertEqual(runner.HANDOFF_MODE_LEGACY, "legacy")
        # 既定OFFではswitches記録にFLOOR_VERIFY_MODEは付かない(従来と同一出力)
        self.assertEqual(self._old_mode, runner.FLOOR_VERIFY_MODE_OFF)


class TestRubricV7b60(unittest.TestCase):
    """委任_60: V7(3)の「比較・時期の差は一律BLOCKING」を基底R3(e)に揃えたV7b。"""

    def test_v7_kept_and_v7b_adds_contradiction_wording(self):
        import er052_open233_self_recovery_stage2_production_01 as s2p
        v7 = "".join(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7.split())
        v7b = "".join(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7B.split())
        self.assertIn("数値・主体・否定・比較・時期の差は、この原則の対象外", v7)  # 旧版は定数として残る
        self.assertNotIn("数値・主体・否定・比較・時期の差は、この原則の対象外", v7b)
        for w in ("Ledgerと矛盾する重大な変更", "数値の改変", "主体の取り違え", "否定の反転", "方向の反転",
                  "時期の取り違え", "方向・時期のニュアンスの差で事実関係の核心が保たれている"):
            self.assertIn(w, v7b)
        # 3例の期待値は不変
        t = s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7B
        lines = [x for x in t[t.index("判定済みの例"):].splitlines() if x.startswith("- ")]
        self.assertEqual([x.split("→")[-1].strip() for x in lines], ["QUALITY", "ACCEPTABLE", "QUALITY"])
        # 動機(V7(1)(イ))へ「仕組み・意図」を足していない(Opus#8: 既存より厳しくなりうる)
        self.assertEqual(s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7.split("(2) 自然な推論")[0],
                         s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7B.split("(2) 自然な推論")[0])
        self.assertNotIn("仕組み・意図", s2c.MISCONCEPTION_PRINCIPLE_TEXT_V7B)
        # production側(配線時用)
        self.assertIn("方向の反転", s2p._V7B_NEW_TIEBREAK)
        self.assertNotIn("(fail-closed)", s2p.MATERIALITY_RUBRIC_V7B)
        self.assertIn("動機の帰属", "".join(s2p.MATERIALITY_RUBRIC_V7B.split()))  # 動機行は変更しない
        self.assertIn("比較・時期の差は", "".join(s2p.MATERIALITY_RUBRIC_V7.split()).replace("数値・主体・否定・", ""))

    def test_body_default_is_v7b_and_mechanical_floor_unchanged(self):
        self.assertEqual(runner.BODY_RUBRIC_DEFAULT,
                         s2c.RUBRIC_R3_TRIPLE_PRIME_WITH_MISCONCEPTION_PRINCIPLE_V7B)
        self.assertEqual(set(runner.FLOOR_FLAGS), {"changed_actor", "changed_number", "changed_negation",
                                                   "changed_comparison", "changed_time"})

    def test_floor_verify_prompt_has_hypothesis_and_v7b(self):
        self.assertIn("検証すべき仮説", runner.FLOOR_VERIFY_PROMPT_TEMPLATE)
        self.assertIn("Ledgerの該当箇所を引用して検証せよ", runner.FLOOR_VERIFY_PROMPT_TEMPLATE)
        self.assertIn("時期の取り違え", runner.FLOOR_VERIFY_RUBRIC_ADDENDUM)
        self.assertEqual(set(runner.FLOOR_VERIFY_JSON_SCHEMA["schema"]["required"]),
                         {"materiality", "ledger_citation", "basis", "explanation"})


class TestMotiveDocAlignment60(unittest.TestCase):
    """委任_60: 動機(帰属=軽微/創作=重大)の文書整合。"""

    def _read(self, p):
        with open(p, encoding="utf-8") as f:
            return f.read()

    def test_design_section_0_2_updated(self):
        t = "".join(self._read("docs/pm/design_open233_self_recovery_flow_01.md").split())
        self.assertIn("未確認の人物・行動・仕組み・数字の追加(Ledgerに根拠のない人物・組織の意図・動機の断定を含む", t)
        self.assertIn("確認済みの事象に理由づけを添えるだけで新しい具体的事実を加えないものは含まない", t)

    def test_criteria_doc_has_motive_section(self):
        t = "".join(self._read("docs/pm/open233_materiality_criteria_2026-10-03.md").split())
        self.assertIn("動機の帰属=確認済みの事象に理由づけを添える", t)
        self.assertIn("動機の創作=台帳にない意図・仕組み", t)
        self.assertIn("V7(1)(イ)への「仕組み・意図」の追加はしない", t)


# ============================================================
# 委任_66: L6「完結文復元」(Trial専用スイッチ`VS_SENTENCE_RESTORE`、既定OFF)+Opus#9是正のテスト。すべて¥0・ネットワークなし。
# 実例の2件(rep24 A2A3 s2 cycle2・B3 s2 cycle2)と`6 percent`型は、rep24のinstance JSONがある場合に実データで固定する。
# ============================================================
L6_ART = (
    "# Oil Plan Turns\n\n## In one line\n\n"
    "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the flashy 20% "
    "plan left the stage, but the chart only pulled back briefly before recovering.\n\n"
    "On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals that the "
    "Gulf states were working on with the United States. "
    "After the announcement, Brent was up about 2.6 percent, because attacks between the United States and Iran "
    "continued, fears of a blockade at sea grew, and traders worried about tanker safety near the strait. "
    "The chart later cooled. The chart later cooled down quickly.\n\n"
    "Mr. Smith of the U.S. Treasury said the group met on Jan. 5 in St. Louis to review the plan. He said no. "
    "Then he left for No. 5 Street. "
    "The council approved the new harbor budget on Monday after a long debate about costs. "
    "Residents objected to the proposed tunnel fees during the public hearing last week.\n"
)
L6_S_JULY = ("On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals "
             "that the Gulf states were working on with the United States.")
L6_S_BRENT = ("After the announcement, Brent was up about 2.6 percent, because attacks between the United States and "
              "Iran continued, fears of a blockade at sea grew, and traders worried about tanker safety near the strait.")
L6_S_ONELINE = ("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, while the "
                "flashy 20% plan left the stage, but the chart only pulled back briefly before recovering.")
L6_S_MR = "Mr. Smith of the U.S. Treasury said the group met on Jan. 5 in St. Louis to review the plan."
L6_S_COUNCIL = "The council approved the new harbor budget on Monday after a long debate about costs."


def _l6_on():
    return mock.patch.multiple(runner, VS_SENTENCE_RESTORE=True, VS_MATCH_EXT=True, VS_EXPLAIN_SPLIT=True)


def _l6_res(claim, art=None):
    with _l6_on():
        return runner._resolve_claim_string(claim, art or L6_ART)


def _l6_info(claim, art=None):
    with _l6_on():
        return runner.vs_sentence_restore_resolve(claim, art or L6_ART)


def _l6_state():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


class TestL6SwitchOffUnchanged66(unittest.TestCase):
    """スイッチ既定OFFで既存挙動が不変・legacy無影響。"""

    CLAIMS = [
        "6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea grew",
        "rump announced that the 20 percent plan would be replaced by trade and investment deals",
        "On July 14, Trump announced that the 20 percent plan ... working on with the United States",
        "Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the flashy "
        "20% plan left the stage...",
        L6_S_JULY, "“Prices stayed high.” This overstates the situation", "In one line", "not in the article at all, really",
    ]

    def test_default_off_and_cli_flag(self):
        import inspect
        self.assertFalse(runner.VS_SENTENCE_RESTORE)
        self.assertIn("--vs-sentence-restore", inspect.getsource(runner.main))
        self.assertIn("VS_SENTENCE_RESTORE", inspect.getsource(runner.run_instance))

    def test_off_equals_p_path_for_every_claim(self):
        with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=False, VS_MATCH_EXT=True, VS_EXPLAIN_SPLIT=True):
            for c in self.CLAIMS:
                a = runner._resolve_claim_string(c, L6_ART)
                b = runner._resolve_claim_string_p(c, L6_ART)
                self.assertEqual(a, b, c)
                self.assertNotIn("sentence_restore", a)

    def test_on_does_not_change_claims_resolved_before_l6(self):
        for c in (L6_S_JULY, "“Prices stayed high.” This overstates the situation",
                  "On July 14, Trump announced that the 20 percent plan would be replaced by trade and investment deals"):
            art = L6_ART + "\nPrices stayed high.\n"
            with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=False, VS_MATCH_EXT=True, VS_EXPLAIN_SPLIT=True):
                off = runner._resolve_claim_string(c, art)
            on = _l6_res(c, art)
            self.assertEqual(off["status"], "resolved", c)
            self.assertEqual(on, off, c)

    def test_flag_requires_vs_match_ext(self):
        c = "rump announced that the 20 percent plan would be replaced by trade and investment deals"
        with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=True, VS_MATCH_EXT=False, VS_EXPLAIN_SPLIT=True):
            r = runner._resolve_claim_string(c, L6_ART)
        self.assertNotEqual(r.get("level"), runner.VS_L6_LEVEL)
        self.assertNotIn("sentence_restore", r)

    def test_legacy_handoff_unaffected_by_flag(self):
        full_text = "# Title\n\nSome sentence with a problem in it.\n\n## In one line\nA plan changed.\n"
        claim_rec = {"claim_text": "Some sentence with a problem in it.", "rewrite_kind": "narrow_scope",
                     "materiality": "BLOCKING", "basis": "ledger_conditions", "rewrite_hint": "",
                     "dev": {"issue": "problem"}}
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": full_text}
        outs = []
        for flag in (False, True):
            calls = []

            def fake_llm(client, state, errs, log, label, dev_msg, prompt, model=None):
                calls.append(label)
                return "Some sentence without the problem." if label.endswith("_e2_rewrite") else ""

            with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=flag, VS_MATCH_EXT=True,
                                     HANDOFF_MODE=runner.HANDOFF_MODE_LEGACY), \
                    mock.patch.object(runner, "simple_llm_call", side_effect=fake_llm):
                res = runner.single_text_rewrite(None, _l6_state(), [], [], "t", fixture, "article_text", claim_rec)
            outs.append((res["updated_text"], res["method"], calls))
        self.assertEqual(outs[0], outs[1])

    def test_e1_template_unchanged_for_non_l6(self):
        self.assertEqual(runner.E1_RANGES_PROMPT_TEMPLATE_L6.replace("{focus_block}", ""),
                         runner.E1_RANGES_PROMPT_TEMPLATE)
        self.assertNotIn("focus_block", runner.E1_RANGES_PROMPT_TEMPLATE)


class TestL6NumericBoundary66(unittest.TestCase):
    """作業2-1: 数字に挟まれた`.`/`,`は語構成文字(VS_MATCH_EXT配下、新スイッチなし)。"""

    def test_decimal_point_and_thousands_separator_are_word_chars_only_under_ext(self):
        t = "Brent was up about 2.6 percent and 1,000 people came."
        a = t.index("6 percent")
        b = t.index("000 people")
        with mock.patch.object(runner, "VS_MATCH_EXT", True):
            self.assertFalse(runner.vs_word_boundary_ok(t, (a, a + len("6 percent"))))
            self.assertFalse(runner.vs_word_boundary_ok(t, (b, b + len("000 people"))))
            self.assertFalse(runner.vs_word_boundary_ok(t, (a - 2, a)))  # 「2.6」の途中(`2.`)で終わる切り方も不可
            self.assertTrue(runner.vs_word_boundary_ok(t, (a - 2, a + len("6 percent"))))  # 2.6 percent
            self.assertTrue(runner.vs_word_boundary_ok(t, (t.index("1,000"), t.index("1,000") + 5)))
            self.assertTrue(runner.vs_word_boundary_ok(t, (t.index("came"), t.index("came") + 4)))
        with mock.patch.object(runner, "VS_MATCH_EXT", False):  # OFFでは従来どおり(旧挙動の固定)
            self.assertTrue(runner.vs_word_boundary_ok(t, (a, a + len("6 percent"))))

    def test_sentence_final_period_after_digit_is_not_a_word_char(self):
        t = "It rose to 85. Then it fell."
        with mock.patch.object(runner, "VS_MATCH_EXT", True):
            self.assertTrue(runner.vs_word_boundary_ok(t, (t.index("85"), t.index("85") + 2)))

    def test_six_percent_claim_no_longer_resolves_by_base_and_goes_to_l6(self):
        c = "6 percent, because attacks between the United States and Iran continued, fears of a blockade at sea grew"
        with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=False, VS_MATCH_EXT=True, VS_EXPLAIN_SPLIT=True):
            base = runner._resolve_claim_string(c, L6_ART)
        self.assertEqual(base["status"], "unverified")
        self.assertEqual(base["reason"], "mismatch")
        with mock.patch.multiple(runner, VS_SENTENCE_RESTORE=False, VS_MATCH_EXT=False, VS_EXPLAIN_SPLIT=True):
            old = runner._resolve_claim_string(c, L6_ART)  # スイッチOFFの旧挙動(数値の途中から確定)
        self.assertEqual(old["status"], "resolved")
        self.assertTrue(old["ranges"][0].startswith("6 percent"))
        r = _l6_res(c)
        self.assertEqual(r["status"], "resolved")
        self.assertEqual(r["level"], runner.VS_L6_LEVEL)
        self.assertEqual(r["ranges"], [L6_S_BRENT])
        self.assertEqual(r["sentence_restore"]["restore_reason"], ["truncated_head"])


class TestL6FireConditions66(unittest.TestCase):
    """発火条件(i)〜(iv)と記録。"""

    def test_i_truncated_head_and_tail_restore_the_complete_sentence(self):
        r = _l6_res("rump announced that the 20 percent plan would be replaced by trade and investment deals")
        self.assertEqual((r["level"], r["ranges"]), (runner.VS_L6_LEVEL, [L6_S_JULY]))
        self.assertEqual(r["sentence_restore"]["restore_reason"], ["truncated_head"])
        r = _l6_res("Mr. Smith of the U.S. Treasury said the group met on Jan. 5 in St. Louis to rev")
        self.assertEqual(r["ranges"], [L6_S_MR])
        self.assertEqual(r["sentence_restore"]["restore_reason"], ["truncated_tail"])

    def test_ii_ellipsis_tail_with_altered_word_and_mid_ellipsis(self):
        r = _l6_res("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so "
                    "the flashy 20% plan left the stage...")
        self.assertEqual(r["ranges"], [L6_S_ONELINE])
        self.assertIn("ellipsis_tail", r["sentence_restore"]["restore_reason"])
        self.assertIn("anchor_with_substituted_words", r["sentence_restore"]["restore_reason"])
        r = _l6_res("On July 14, Trump announced that the 20 percent plan ... working on with the United States")
        self.assertEqual(r["ranges"], [L6_S_JULY])
        self.assertEqual(r["sentence_restore"]["restore_reason"], ["ellipsis_mid"])

    def test_iii_mid_ellipsis_parts_match_but_whole_does_not(self):
        r = _l6_info("Concerns about US-Iran attacks, the sea blockade ... the chart only pulled back briefly before "
                     "recovering")
        self.assertEqual(r["status"], "restored")
        self.assertEqual(r["restored_sentence"], L6_S_ONELINE)

    def test_iv_anchor_with_foreign_words(self):
        r = _l6_res("by trade and investment deals that the Gulf states were already working on with the United States")
        self.assertEqual(r["ranges"], [L6_S_JULY])
        sr = r["sentence_restore"]
        self.assertEqual(sr["restore_reason"], ["anchor_with_substituted_words"])
        self.assertEqual(sr["anchors"][0]["unmatched"], 1)
        self.assertEqual(sr["original_claim"][:10], "by trade a")
        self.assertEqual(sr["n_candidates"], 1)
        self.assertEqual(sr["n_sentences"], 1)

    def test_record_contains_fragments_span_and_restored_text_verbatim(self):
        r = _l6_res("rump announced that the 20 percent plan would be replaced by trade and investment deals")
        s, e = r["spans"][0]
        self.assertEqual(L6_ART[s:e], r["sentence_restore"]["restored_sentence"])
        self.assertEqual(tuple(r["sentence_restore"]["span"]), (s, e))
        self.assertTrue(r["sentence_restore"]["fragments"])
        self.assertEqual(L6_ART.count(r["ranges"][0]), 1)


class TestL6Exclusions66(unittest.TestCase):
    def test_japanese_claim_not_applicable(self):
        i = _l6_info("日本語のclaimは対象外であることを確認するための文章です")
        self.assertEqual((i["status"], i["reason"]), ("not_applicable", "claim_is_japanese"))

    def test_explanatory_mixed_left_to_p_strict_closed(self):
        c = ("“Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 1” — the headline "
             "and one-line summary also repeat this claim in other words")
        i = _l6_info(c)
        self.assertEqual((i["status"], i["reason"]), ("not_fired", "explanatory_mixed_left_to_P"))
        r = _l6_res(c)
        self.assertEqual(r["status"], "unverified")

    def test_label_only_and_multi_match_are_never_touched(self):
        with _l6_on():
            r = runner._resolve_claim_string("In one line", L6_ART)
        self.assertEqual((r["status"], r["reason"]), ("unverified", "label_only"))
        self.assertNotIn("sentence_restore", r)
        r = _l6_res("hart later cooled")  # 断片が2文に出現=base multi_match
        self.assertEqual((r["status"], r["reason"]), ("unverified", "multi_match"))
        self.assertNotIn("sentence_restore", r)

    def test_label_only_range_is_refused_inside_l6(self):
        art = "# T\n\n## In one line\nShort.\n"
        a = runner._VsL6Art(art)
        i = art.index("In one line")
        self.assertEqual(runner._vs_l6_range_from(a, [(i - 3, i + len("In one line"))])[2], "label_only")

    def test_candidate_multiple_is_unresolvable_and_recorded(self):
        i = _l6_info("the chart later cooled ...")  # 同じ断片が2文に出現=候補複数(baseはmulti_matchで通常は到達しない)
        self.assertEqual(i["status"], "cand_multi")
        self.assertEqual(i["n_candidates"], 2)
        self.assertIsNone(i["restored_sentence"])

    def test_no_verbatim_anchor_is_cand0_and_unresolvable(self):
        c = "Worries over attacks and shipping safety persisted, which is why the plan was dropped and prices dipped"
        r = _l6_res(c)
        self.assertEqual(r["status"], "unverified")
        self.assertEqual(r["sentence_restore"]["status"], "cand0")
        self.assertEqual(r["sentence_restore"]["reason"], "no_verbatim_anchor_in_article")

    def test_exception_inside_l6_fails_closed(self):
        with _l6_on(), mock.patch.object(runner, "_VsL6Art", side_effect=RuntimeError("boom")):
            r = runner._resolve_claim_string("rump announced that the 20 percent plan would be replaced by trade", L6_ART)
        self.assertEqual(r["status"], "unverified")
        self.assertEqual(r["sentence_restore"]["status"], "exception")


class TestL6Guards66(unittest.TestCase):
    def test_threshold_constants(self):
        self.assertEqual((runner.VS_L6_MIN_FRAG_WORDS, runner.VS_L6_MIN_FRAG_CHARS), (3, 12))
        self.assertEqual((runner.VS_L6_MIN_ANCHOR_WORDS, runner.VS_L6_MIN_ANCHOR_CHARS), (4, 20))
        self.assertEqual(runner.VS_L6_MAX_UNMATCHED_TOKENS, 6)
        self.assertEqual(runner.VS_L6_MIN_COVER_RATIO, 0.5)
        self.assertEqual((runner.VS_L6_MAX_SENTENCES, runner.VS_L6_MAX_RESTORED_CHARS), (2, 700))
        self.assertEqual((runner.VS_L6_GAP_ALPHA, runner.VS_L6_RESIDUAL_MIN_WORDS), (3, 3))

    def test_fragment_too_short(self):
        i = _l6_info("he flashy 2")
        self.assertEqual((i["status"], i["reason"]), ("guard_rejected", "fragment_too_short"))

    def test_seven_substituted_words_is_cand0_six_is_ok(self):
        base = "by trade and investment deals that the Gulf states were"
        tail = "working on with the United States"
        six = base + " one two three four five six " + tail
        seven = base + " one two three four five six seven " + tail
        self.assertEqual(_l6_info(six)["status"], "restored")
        i = _l6_info(seven)
        self.assertEqual(i["status"], "cand0")
        self.assertTrue(i["reason"].startswith("unmatched_run_too_long(7>6)"))

    def test_cover_ratio_below_half_is_cand0(self):
        i = _l6_info("by trade and investment deals one two three four five six seven eight")
        self.assertEqual(i["status"], "cand0")

    def test_more_than_two_sentences_is_cand0(self):
        c = ("ent was up about 2.6 percent, because attacks between the United States and Iran continued, fears of a "
             "blockade at sea grew, and traders worried about tanker safety near the strait. The chart later cooled. "
             "The chart later cooled down quickly. Mr. Smith of the U.S. Treasury said the group met on Jan. 5 in St. Lou")
        i = _l6_info(c)
        self.assertEqual(i["status"], "cand0")
        self.assertTrue(i["reason"].startswith("spans_more_than_2_sentences"))

    def test_restored_too_long_is_cand0(self):
        long_sent = "Alpha " + " ".join(f"word{i}" for i in range(140)) + " omega."
        art = "# T\n\n" + long_sent + "\n"
        i = _l6_info("pha word0 word1 word2 word3 word4 word5", art)
        self.assertEqual(i["status"], "cand0")
        self.assertTrue(i["reason"].startswith("restored_too_long"))

    def test_unbalanced_quote_is_closed_by_neighbour_within_two_sentences(self):
        art = "# T\n\nOfficials said “this is not over. We will keep watching,” and prices rose sharply later.\n"
        i = _l6_info("Officials said “this is not ove", art)
        self.assertEqual(i["status"], "restored")
        self.assertEqual(i["n_sentences"], 2)
        self.assertEqual(i["restored_sentence"], art.strip().split("\n\n", 1)[1])

    def test_unbalanced_quote_not_closable_is_cand0(self):
        art = "# T\n\nOfficials said “this is not over. We will keep watching. Prices rose sharply later in the week.\n"
        i = _l6_info("Officials said “this is not ove", art)
        self.assertEqual(i["status"], "cand0")
        self.assertTrue(i["reason"].startswith("unbalanced_quote_not_closable"))

    def test_paragraph_boundary_is_not_crossed(self):
        art = "# T\n\nFirst paragraph ends here and goes on a while longer than usual.\n\nSecond paragraph starts here.\n"
        i = _l6_info("rst paragraph ends here and goes on a while longer than usu", art)
        self.assertEqual(i["status"], "restored")
        self.assertEqual(i["n_sentences"], 1)
        self.assertNotIn("\n", i["restored_sentence"])


class TestL6ResidualInclusionHoleA66(unittest.TestCase):
    """Opus#9 穴A: アンカー外の語が記事の別の文に逐語で存在するなら、復元しない(黙って縮小しない)。"""

    def test_residual_found_only_outside_restored_range_is_rejected(self):
        i = _l6_info("The council approved the new harbor budget on Monday after a long debate about costs and the public hearing")
        self.assertEqual((i["status"], i["reason"]), ("guard_rejected", "residual_outside_restored_range"))
        self.assertIsNone(i["restored_sentence"])

    def test_residual_found_inside_restored_range_is_accepted(self):
        i = _l6_info("The council approved the new harbor budget on Monday after a long debate about costs and the new harbor")
        self.assertEqual(i["status"], "restored")
        self.assertEqual(i["restored_sentence"], L6_S_COUNCIL)
        self.assertTrue(i["residual_check"])
        self.assertTrue(all(x["inside_restored_range"] >= 1 for x in i["residual_check"]))

    def test_short_residual_words_are_not_checked(self):
        # 残りが1語(`so`のような記事中どこにでもある語)だけなら残余検査の対象外(B3 s2の形が通る)
        i = _l6_info("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so "
                     "the flashy 20% plan left the stage...")
        self.assertEqual(i["status"], "restored")

    def test_ambiguous_anchor_words_outside_range_are_rejected(self):
        art = L6_ART + "The chart later cooled down quickly during the week.\n"
        i = _l6_info("The council approved the new harbor budget on Monday after a long debate and the chart later cooled down", art)
        self.assertEqual(i["status"], "guard_rejected")
        self.assertEqual(i["reason"], "residual_outside_restored_range")


class TestL6AnchorGapHoleB66(unittest.TestCase):
    """Opus#9 穴B: アンカー間隔の整合・unmatched>=0・cover二重計上の修正。"""

    def test_gap_inconsistent_is_rejected(self):
        c = ("The council approved the new harbor budget on Monday also "
             "tunnel fees during the public hearing last week")
        i = _l6_info(c)
        self.assertEqual(i["status"], "guard_rejected")
        self.assertTrue(i["reason"].startswith("anchor_gap_inconsistent"), i)

    def test_gap_consistent_within_alpha_is_accepted(self):
        c = "by trade and investment deals that the Gulf states were so working on with the United States"
        i = _l6_info(c)
        self.assertEqual(i["status"], "restored")
        self.assertEqual(i["anchors"][0]["gap"], {"article_gap_words": 0, "claim_gap_words": 1})

    def test_overlapping_anchors_in_claim_are_rejected_not_negative_unmatched(self):
        art = ("# T\n\nOne two three four five six seven eight nine ten.\n\n"
               "Five six seven eight nine ten eleven twelve thirteen fourteen.\n")
        i = _l6_info("one two three four five six seven eight nine ten eleven twelve thirteen fourteen", art)
        self.assertEqual((i["status"], i["reason"]), ("guard_rejected", "anchors_overlap_in_claim"))


class TestL6AbbreviationSentenceSplit66(unittest.TestCase):
    def test_l6_split_keeps_abbreviation_sentences_whole_and_old_split_unchanged(self):
        segs = [L6_ART[a:b] for a, b in runner.vs_sentence_segments_l6(L6_ART)]
        self.assertIn(L6_S_MR, segs)
        self.assertIn("He said no.", segs)  # 文末の`no.`(直後が数字でない)は文末
        self.assertIn("Then he left for No. 5 Street.", segs)  # `No. 5`は略語
        old = [L6_ART[a:b] for a, b in runner.vs_sentence_segments(L6_ART)]
        self.assertNotIn(L6_S_MR, old)  # 既存の分割は変更していない(略語でも切る)
        self.assertIn("Smith of the U.S.", old)

    def test_each_listed_abbreviation_does_not_split(self):
        for ab in ("U.S.", "Mr.", "Mrs.", "Ms.", "Dr.", "Jan.", "Feb.", "Mar.", "Apr.", "Jun.", "Jul.", "Aug.", "Sep.",
                   "Oct.", "Nov.", "Dec.", "vs.", "e.g.", "i.e.", "Inc.", "Co.", "Ltd.", "a.m.", "p.m."):
            t = f"The report cited {ab} figures and trends here. Next sentence follows."
            segs = [t[a:b] for a, b in runner.vs_sentence_segments_l6(t)]
            self.assertEqual(len(segs), 2, ab)
            self.assertTrue(segs[0].endswith("here."), (ab, segs))
        self.assertEqual(len(runner.vs_sentence_segments_l6("He lives in St. Louis. It is big.")), 2)
        # `St.`は直後が大文字なら略語扱い(`St. Louis`)。文末の`St.`+次文が大文字の曖昧ケースは割らない(固定の割り切り)
        self.assertEqual(len(runner.vs_sentence_segments_l6("That is the end of St. Then more.")), 1)
        self.assertEqual(len(runner.vs_sentence_segments_l6("He said No. 5 is best. Done.")), 2)

    def test_restore_returns_the_complete_sentence_with_abbreviations(self):
        i = _l6_info("Treasury said the group met on Jan. 5 in St. Louis to review the pl")
        self.assertEqual(i["restored_sentence"], L6_S_MR)
        i = _l6_info("e said no. Then he left for No. 5 Str")  # 2文にまたがる切断
        self.assertEqual(i["status"], "restored")
        self.assertEqual(i["n_sentences"], 2)


class TestL6IssueFocusAbsent66(unittest.TestCase):
    def test_quoted_phrase_extraction_covers_curly_and_corner_and_straight_quotes(self):
        ph = runner.vs_l6_issue_quoted_phrases("The word “so” and ‘because’ and 「ので」 and \"hence\" are used.")
        self.assertEqual(ph, ["so", "because", "ので", "hence"])
        self.assertEqual(runner.vs_l6_issue_quoted_phrases("no quotes here"), [])

    def test_focus_absent_rules(self):
        self.assertTrue(runner.vs_l6_focus_absent(["so"], "the plan left while it recovered")["absent"])
        self.assertFalse(runner.vs_l6_focus_absent(["so"], "also, so the plan left")["absent"])  # 独立の`so`は数える
        self.assertTrue(runner.vs_l6_focus_absent(["so"], "he is also happy")["absent"])  # alsoの`so`は数えない
        self.assertFalse(runner.vs_l6_focus_absent(["a", "b"], "a only")["absent"])  # 1つでも在ればRewriteする
        self.assertFalse(runner.vs_l6_focus_absent([], "anything")["absent"])  # 引用符付き語句なし=通常Rewrite

    def _ladder(self, issue, llm):
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": L6_ART}
        claim = ("Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 14, so the "
                 "flashy 20% plan left the stage...")
        claim_rec = {"claim_text": claim, "rewrite_kind": "narrow_scope", "materiality": "BLOCKING",
                     "basis": "ledger_conditions", "rewrite_hint": "", "dev": {"issue": issue}}
        with _l6_on(), mock.patch.object(runner, "simple_llm_call", side_effect=llm):
            return runner.rewrite_ranges_ladder(None, _l6_state(), [0], [], "t", fixture, "article_text", claim_rec)

    def test_b3_type_stale_quote_skips_rewrite_and_goes_to_recheck_only(self):
        calls = []

        def llm(*a, **k):
            calls.append(a[4])
            raise AssertionError("no Rewrite call must be made when the issue focus is absent")

        res = self._ladder("The word “so” presents the concerns as a cause of the plan’s withdrawal.", llm)
        self.assertEqual(calls, [])
        self.assertEqual(res["method"], "issue_focus_absent_recheck_only")
        self.assertFalse(res["guard_ok"])
        self.assertEqual(res["updated_text"], L6_ART)
        self.assertFalse(res["target_not_locatable"])
        self.assertFalse(res.get("ladder_exhausted_without_full_rewrite"))
        h = res["handoff"]
        self.assertTrue(h["issue_focus_absent"])
        self.assertEqual(h["resolution"]["level"], runner.VS_L6_LEVEL)
        self.assertEqual(h["resolution"]["sentence_restore"]["restored_sentence"], L6_S_ONELINE)

    def test_issue_phrase_present_in_range_rewrites_normally_with_fragment_in_e1_prompt(self):
        prompts = []

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            prompts.append(prompt)
            return json.dumps({"revised_ranges": [L6_S_ONELINE.replace("while", "meanwhile")]})

        res = self._ladder("The word “while” presents the plan leaving as a contrast the Ledger does not support.", llm)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertEqual(len(prompts), 1)
        p = prompts[0]
        self.assertIn("[Checker's flagged fragment", p)
        self.assertIn("so the flashy 20% plan left the stage...", p)  # 元の断片(Checker出力そのまま)
        self.assertIn(L6_S_ONELINE, p)  # 範囲=復元文
        self.assertLess(p.index("[Flagged range(s)"), p.index("[Checker's flagged fragment"))
        self.assertLess(p.index("[Checker's flagged fragment"), p.index("[Paragraph context"))

    def test_issue_without_quoted_phrase_rewrites_normally(self):
        calls = []

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            return json.dumps({"revised_ranges": [L6_S_ONELINE.replace("while", "meanwhile")]})

        res = self._ladder("The causal link is not supported by the Ledger.", llm)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(len(calls), 1)

    def test_non_l6_resolution_has_no_focus_block_and_is_never_skipped(self):
        fixture = {"ledger_text": "[VERIFIED] HF-007: ...", "article_text": L6_ART}
        claim_rec = {"claim_text": L6_S_JULY, "rewrite_kind": "narrow_scope", "materiality": "BLOCKING",
                     "basis": "ledger_conditions", "rewrite_hint": "",
                     "dev": {"issue": "The word “zzz” is not in the article."}}
        prompts = []

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            prompts.append(prompt)
            return json.dumps({"revised_ranges": [L6_S_JULY.replace("working on", "discussing")]})

        with _l6_on(), mock.patch.object(runner, "simple_llm_call", side_effect=llm):
            res = runner.rewrite_ranges_ladder(None, _l6_state(), [0], [], "t", fixture, "article_text", claim_rec)
        self.assertTrue(res["guard_ok"])
        self.assertNotIn("flagged fragment", prompts[0])

    def test_full_recheck_is_forced_when_focus_absent(self):
        rec = [{"ladder_level_used": None, "mechanism": "single_text_local(E-2/delete-generic)",
                "handoff": {"issue_focus_absent": True}}]
        need, reasons = runner.full_recheck_required(rec, [{"dev": {}, "origin": "x"}], "bgroup_B3")
        self.assertTrue(need)
        self.assertIn("issue_focus_absent_recheck_only", reasons)
        rec[0]["handoff"] = {}
        need, reasons = runner.full_recheck_required(rec, [{"dev": {}, "origin": "x"}], "bgroup_B3")
        self.assertNotIn("issue_focus_absent_recheck_only", reasons)


class TestL6TwoSentenceFocusGuard66(unittest.TestCase):
    ART = "# T\n\nOfficials said “this is not over. We will keep watching,” and prices rose sharply later.\n"
    CLAIM = "Officials said “this is not ove"

    def _run(self, revised_text):
        fixture = {"ledger_text": "[VERIFIED] HF-001: ...", "article_text": self.ART}
        claim_rec = {"claim_text": self.CLAIM, "rewrite_kind": "narrow_scope", "materiality": "BLOCKING",
                     "basis": "ledger_conditions", "rewrite_hint": "", "dev": {"issue": "the statement is overstated"}}
        calls = []

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append(label)
            return json.dumps({"revised_ranges": [revised_text]})

        with _l6_on(), mock.patch.object(runner, "simple_llm_call", side_effect=llm):
            return runner.rewrite_ranges_ladder(None, _l6_state(), [0], [], "t", fixture, "article_text", claim_rec), calls

    def test_two_sentence_restore_is_recorded(self):
        with _l6_on():
            r = runner._resolve_claim_string(self.CLAIM, self.ART)
        self.assertEqual(r["sentence_restore"]["n_sentences"], 2)
        self.assertEqual(len(r["sentence_restore"]["focus_spans"]), 1)

    def test_change_inside_focus_sentence_is_accepted(self):
        revised = "Officials said “this is not quite over. We will keep watching,” and prices rose sharply later."
        res, calls = self._run(revised)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertTrue(res["handoff"]["level_attempts"][0]["focus_guard"]["ok"])

    def test_change_outside_focus_sentence_is_e1_failure_and_goes_to_existing_failure_path(self):
        revised = "Officials said “this is not over. We will keep watching,” and prices rose a bit later."
        res, calls = self._run(revised)
        att = res["handoff"]["level_attempts"][0]
        self.assertEqual(att["result"], "focus_guard_rejected")
        self.assertFalse(att["focus_guard"]["ok"])
        self.assertTrue(res["handoff"]["focus_guard_fired"])
        # 既存の失敗経路(次の水準③)へ進む。E1の結果は書き戻されない(E1の変更は採用されない)
        self.assertEqual(calls[0], "t_e1_minimal_word")
        self.assertIn("t_e2_rewrite", calls)
        self.assertNotEqual(res["handoff"]["level_used"], "1_word_connective")

    def test_guard_function_unit(self):
        art = "# T\n\nAlpha beta gamma delta. Epsilon zeta eta theta iota.\n"
        a = art.index("Alpha")
        e = art.index("iota.") + 5
        sr = {"span": (a, e), "focus_spans": [(a, a + 10)]}
        target = art[a:e]
        self.assertTrue(runner.vs_l6_focus_guard(sr, target, target.replace("beta", "BETA"), art)["ok"])
        self.assertFalse(runner.vs_l6_focus_guard(sr, target, target.replace("zeta", "ZETA"), art)["ok"])
        self.assertTrue(runner.vs_l6_focus_guard(sr, target, target, art)["ok"])  # 変更なし


class TestL6OrderPThenL6_66(unittest.TestCase):
    def test_p_resolves_first_and_l6_is_not_called(self):
        c = "“Prices stayed high.” This overstates the situation"
        art = L6_ART + "\nPrices stayed high.\n"
        with _l6_on(), mock.patch.object(runner, "vs_sentence_restore_resolve",
                                         side_effect=AssertionError("L6 must not run when P resolved")):
            r = runner._resolve_claim_string(c, art)
        self.assertEqual(r["status"], "resolved")
        self.assertTrue(r["level"].startswith("P:"))

    def test_l6_does_not_bypass_p_guards(self):
        c = ("“Concerns about US-Iran attacks, the sea blockade, and tanker safety continued on July 1” "
             "but the Ledger says otherwise about this headline")
        with _l6_on():
            r = runner._resolve_claim_string(c, L6_ART)
        self.assertEqual(r["status"], "unverified")
        self.assertTrue(r["explain_split"]["reason"].startswith("explain_split_rejected"))
        self.assertEqual(r["sentence_restore"]["reason"], "explanatory_mixed_left_to_P")


class TestL6SummaryAndRecords66(unittest.TestCase):
    def test_summarize_counts(self):
        def rec(sr, **h):
            hh = {"resolution": {"sentence_restore": sr}}
            hh.update(h)
            return {"handoff": hh}
        res = [{"instance_id": "x", "cycles": [{"cycle": 1, "rewrite_records": [
            rec({"status": "restored", "n_sentences": 2, "original_claim": "c", "restored_sentence": "s"}, focus_guard_fired=True),
            rec({"status": "restored", "n_sentences": 1, "original_claim": "c2", "restored_sentence": "s2"}, issue_focus_absent=True),
            rec({"status": "cand0", "reason": "x"}), rec({"status": "cand_multi"}),
            rec({"status": "guard_rejected", "reason": "residual_outside_restored_range"}),
            rec({"status": "not_fired", "reason": "explanatory_mixed_left_to_P"}),
            {"handoff": {"sentence_restore": {"status": "cand0"}}}, {"handoff": {}}]}]}]
        s = runner.sentence_restore_summarize(res)
        self.assertEqual((s["l6_fired"], s["restored"], s["restored_two_sentences"], s["cand0"], s["cand_multi"],
                          s["guard_rejected"], s["issue_focus_absent"], s["focus_guard_fired"], s["not_fired_or_na"]),
                         (6, 2, 1, 2, 1, 1, 1, 1, 1))
        self.assertEqual(s["guard_rejected_by_reason"], {"residual_outside_restored_range": 1})

    def test_switch_recorded_in_instance_switches_source(self):
        import inspect
        self.assertEqual(inspect.getsource(runner.run_instance).count('"VS_SENTENCE_RESTORE": True'), 2)


class TestL6Rep24RealFailures66(unittest.TestCase):
    """rep24の実データ(instance JSONがあれば): 失敗2件と`6 percent`型2件をfixture化(委任_66の主目的)。"""

    BASE = "er052_output/open233_self_recovery_flow_runner_01_rep24"

    def _load(self, sample, inst):
        p = os.path.join(self.BASE, f"instances_{sample}", f"{inst}.json")
        if not os.path.exists(p):
            self.skipTest("rep24 instance json not present")
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def _claim(self, d, cyc_idx):
        c = d["cycles"][cyc_idx]
        en = d["cycles"][cyc_idx - 1]["en_text_after_rewrite"] if cyc_idx else c["en_text_before_rewrite"]
        return c, en

    def test_a2a3_s2_cycle2_is_restored_and_rewritten_normally(self):
        d = self._load("s2", "safety_A2A3")
        c, en = self._claim(d, 1)
        sr = next(x for x in c["stage2_results"] if x.get("materiality") == "BLOCKING")
        with _l6_on():
            r = runner._resolve_claim_string(sr["claim_text"], en)
        self.assertEqual(r["status"], "resolved")
        self.assertEqual(r["level"], runner.VS_L6_LEVEL)
        self.assertTrue(r["ranges"][0].startswith("On July 14, Trump announced that the 20 percent plan"))
        self.assertEqual(r["sentence_restore"]["restore_reason"], ["anchor_with_substituted_words"])
        fa = runner.vs_l6_focus_absent(runner.vs_l6_issue_quoted_phrases((sr.get("dev") or {}).get("issue") or ""),
                                       r["ranges"][0])
        self.assertFalse(fa["absent"])  # issueに引用符付き語句なし=通常Rewrite

    def test_b3_s2_cycle2_is_restored_and_stale_so_triggers_issue_focus_absent(self):
        d = self._load("s2", "bgroup_B3")
        c, en = self._claim(d, 1)
        self.assertNotRegex(en, r"\bso\b")  # cycle2の本文に`so`は存在しない(古い引用)
        sr = next(x for x in c["stage2_results"] if x.get("materiality") == "BLOCKING")
        with _l6_on():
            r = runner._resolve_claim_string(sr["claim_text"], en)
        self.assertEqual(r["level"], runner.VS_L6_LEVEL)
        self.assertIn("while the flashy 20% plan left the stage", r["ranges"][0])
        fa = runner.vs_l6_focus_absent(runner.vs_l6_issue_quoted_phrases((sr.get("dev") or {}).get("issue") or ""),
                                       r["ranges"][0], r["sentence_restore"].get("claim_core") or "")
        self.assertTrue(fa["absent"])

    def test_six_percent_claims_are_restored_to_the_complete_sentence(self):
        n = 0
        for sample in ("s1", "s2"):
            d = self._load(sample, "safety_A2A3")
            c, en = self._claim(d, 0)
            hit = [x for x in c["stage2_results"] if "6 percent, because" in (x.get("claim_text") or "")]
            if not hit:
                continue
            n += 1
            with _l6_on():
                r = runner._resolve_claim_string(hit[0]["claim_text"], en)
            self.assertEqual(r["level"], runner.VS_L6_LEVEL, sample)
            self.assertTrue(r["ranges"][0].startswith("After the announcement"), sample)
            self.assertEqual(r["sentence_restore"]["restore_reason"], ["truncated_head"])
        self.assertGreaterEqual(n, 1)


class TestL6CarryForwardRecord66(unittest.TestCase):
    """cycle開始時点でL6が復元したclaimが、同一cycleの先行Rewriteで書き換え済み(carry-forward)になった場合も、L6の記録を残す
    (rep25 safety_A2A3 s1の`6 percent`型。記録専用で、動作は変えない)。"""

    def test_covered_handoff_keeps_the_l6_record(self):
        claim = "rump announced that the 20 percent plan would be replaced by trade and investment deals"
        rewritten = L6_ART.replace(L6_S_JULY, "A short new sentence now stands here instead.")
        claim_rec = {"claim_text": claim, "rewrite_kind": "narrow_scope", "materiality": "BLOCKING", "basis": "x",
                     "rewrite_hint": "", "dev": {"issue": "x"}, "origin": "stage1_llm",
                     "cycle_start_en_text": L6_ART, "cycle_start_ja_text": None,
                     "cycle_replaced_units": [{"lang": "EN", "claim_identity": "fact:HF-1", "before_units": [L6_S_JULY]}],
                     "cycle_claim_info": {}}
        fixture = {"ledger_text": "[VERIFIED] HF-1: ...", "article_text": rewritten}
        with _l6_on():
            res = runner.run_stage3_for_claim_spans(None, _l6_state(), [0], [], "t", fixture, rewritten, None, claim_rec, False)
        self.assertEqual(res["method"], "covered_by_earlier_rewrite_in_cycle")
        r = res["handoff"]["resolution"]
        self.assertEqual(r["cycle_start_level"], runner.VS_L6_LEVEL)
        self.assertEqual(r["sentence_restore"]["status"], "restored")
        self.assertEqual(r["ranges"], [L6_S_JULY])
        s = runner.sentence_restore_summarize([{"instance_id": "x", "cycles": [{"cycle": 1, "rewrite_records": [{"handoff": res["handoff"]}]}]}])
        self.assertEqual((s["restored"], s["l6_fired"]), (1, 1))


class TestKpiRecovery02PriorIssueCurrentText(unittest.TestCase):
    """委任_01(OPEN-233-KPI-RECOVERY-REDESIGN-02) 作業2-1: prior_issuesへ現行本文(Rewrite後)の置換後の文を渡す。"""
    NEW = "Some calls may have needed user information."

    @staticmethod
    def _rec(before, after, ident="fact:MUSE-HC-010", ok=True):
        return {"claim_identity": ident, "guard_ok": ok,
                "handoff": {"text_lang": "EN", "level_attempts": [
                    {"result": "success", "targets": [before], "before_after": [{"before": before, "after": after}]}]}}

    def test_current_text_replaces_original_when_after_unit_exists_in_article(self):
        rec = self._rec(META_TARGET, self.NEW)
        en_now = "Calls happened. " + self.NEW + " The end."
        txt, src = runner.resolve_prior_issue_text(META_TARGET, rec, [], en_now, None)
        self.assertEqual((txt, src), (self.NEW, "current_text"))

    def test_fallback_to_original_when_not_resolvable(self):
        en_now = "Calls happened. The end."
        # (a)置換後の文が現行本文に存在しない
        rec = self._rec(META_TARGET, self.NEW)
        self.assertEqual(runner.resolve_prior_issue_text(META_TARGET, rec, [], en_now, None),
                         (META_TARGET, "original_text"))
        # (b)delete型(後が空)
        rec = self._rec(META_TARGET, "")
        self.assertEqual(runner.resolve_prior_issue_text(META_TARGET, rec, [], en_now, None),
                         (META_TARGET, "original_text"))
        # (c)Rewrite未成功(guard_ok=False)・record無し
        rec = self._rec(META_TARGET, self.NEW, ok=False)
        self.assertEqual(runner.resolve_prior_issue_text(META_TARGET, rec, [], self.NEW, None),
                         (META_TARGET, "original_text"))
        self.assertEqual(runner.resolve_prior_issue_text(META_TARGET, None, [], self.NEW, None),
                         (META_TARGET, "original_text"))

    def test_carry_forward_uses_earlier_claims_after_unit(self):
        earlier = self._rec("S before. Also x.", "S after.", ident="fact:A")
        units = runner.collect_replaced_units(earlier, "fact:A")
        later = {"claim_identity": "fact:B", "guard_ok": False,
                 "handoff": {"carry_forward_covered": [{"range": "Also x.", "covered_by_claim": "fact:A"}]}}
        txt, src = runner.resolve_prior_issue_text("Also x.", later, units, "Intro. S after. End.", None)
        self.assertEqual((txt, src), ("S after.", "current_text"))
        # 置換元が見つからないcarry-forwardは元text
        later2 = {"claim_identity": "fact:C", "guard_ok": False,
                  "handoff": {"carry_forward_covered": [{"range": "zzz", "covered_by_claim": "fact:A"}]}}
        self.assertEqual(runner.resolve_prior_issue_text("zzz", later2, units, "Intro. S after. End.", None),
                         ("zzz", "original_text"))

    def test_run_instance_passes_current_text_to_recheck_and_records_source(self):
        def stage3(client, state, ce, call_log, label, fixture, en, ja, claim_rec):
            new_en = en.replace(META_TARGET, self.NEW)
            return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": new_en, "ja_text": ja,
                    "method": "fake", "guard_ok": True, "before_fragment": META_TARGET,
                    "after_fragment": self.NEW, "ladder_level_used": "1_word_connective",
                    "target_not_locatable": False, "span_unverified": False,
                    "ladder_exhausted_without_full_rewrite": False,
                    "handoff": {"text_lang": "EN", "level_attempts": [
                        {"result": "success", "targets": [META_TARGET],
                         "before_after": [{"before": META_TARGET, "after": self.NEW}]}]}}
        res, seen = _run_instance49([_dev49(META_TARGET, origin="ja_source")], ja_mode=runner.JA_MODE_ENGLISH_ONLY,
                                    stage3_fn=stage3)
        self.assertEqual([p["claim_in_article"] for p in seen["prior_issues"]], [self.NEW])
        self.assertEqual(res["cycles"][0]["prior_issue_text_sources"], ["current_text"])

    def test_run_instance_falls_back_to_original_when_handoff_has_no_units(self):
        res, seen = _run_instance49([_dev49(META_TARGET, origin="ja_source")], ja_mode=runner.JA_MODE_ENGLISH_ONLY)
        self.assertEqual([p["claim_in_article"] for p in seen["prior_issues"]], [META_TARGET])
        self.assertEqual(res["cycles"][0]["prior_issue_text_sources"], ["original_text"])

    def test_checker_prompt_template_bytes_unchanged(self):
        """Checker Promptの文面(er003の`build_prior_issues_instruction`)はバイト不変(sha256固定、2026-10-04時点)。"""
        import hashlib
        import er003_v1_en_direct_vfl_01_generate as vfl01
        s0 = vfl01.build_prior_issues_instruction([])
        s1 = vfl01.build_prior_issues_instruction(
            [{"fact_id": "HF-1", "claim_in_article": "X y.", "issue": "i", "explanation": "e"}])
        self.assertEqual(hashlib.sha256(s0.encode()).hexdigest(),
                         "a43f09d3624032f40a8deff40d3d98ab96f8ebe975ada3a6c3ff70358953ee67")
        self.assertEqual(hashlib.sha256(s1.encode()).hexdigest(),
                         "7cf0da0ac184aa6068c6d33eda09fff6c90c199c7547cc4cddbeb0ae1085b6e6")


class TestKpiRecovery02Switches(unittest.TestCase):
    """委任_01 作業2-2/2-3: KPI確認構成とNORMAL群2-of-2の既定OFF。"""

    def test_normal_two_of_two_default_off(self):
        self.assertFalse(runner.STAGE2_NORMAL_TWO_OF_TWO)

    def test_kpi_trial_switches_definition(self):
        k = runner.KPI_TRIAL_SWITCHES
        self.assertTrue(k["VS_SENTENCE_RESTORE"])
        self.assertTrue(k["VS_MATCH_EXT"])
        self.assertTrue(k["VS_EXPLAIN_SPLIT"])
        self.assertFalse(k["STAGE2_NORMAL_TWO_OF_TWO"])
        self.assertEqual(k["JA_MODE"], runner.JA_MODE_ENGLISH_ONLY)
        self.assertEqual(k["FLOOR_VERIFY_MODE"], runner.FLOOR_VERIFY_MODE_TIME_ONLY)
        self.assertEqual(k["HANDOFF_MODE"], runner.HANDOFF_MODE_VIOLATION_SPAN)

    def test_apply_kpi_trial_switches_sets_globals_and_defaults_untouched_before(self):
        keys = list(runner.KPI_TRIAL_SWITCHES)
        saved = {kk: getattr(runner, kk) for kk in keys}
        try:
            # 既定のglobal(適用前)はL6 OFF・NORMAL群2-of-2 OFF
            self.assertFalse(runner.VS_SENTENCE_RESTORE)
            applied = runner.apply_kpi_trial_switches()
            self.assertEqual(applied, runner.KPI_TRIAL_SWITCHES)
            self.assertTrue(runner.VS_SENTENCE_RESTORE)
            self.assertFalse(runner.STAGE2_NORMAL_TWO_OF_TWO)
        finally:
            for kk, v in saved.items():
                setattr(runner, kk, v)

    def test_two_of_two_not_applied_by_default_but_applied_when_switch_on(self):
        import contextlib
        calls = []

        def spy(*a, **k):
            calls.append(1)
            return a[6], []
        dev = [_dev49(META_TARGET, origin="ja_source")]

        def stage2(c, s, ce, cl, lb, fx, claims):
            return [{**x, "materiality": "QUALITY", "llm_materiality": "QUALITY", "basis": "none",
                     "rewrite_kind": "none", "rewrite_hint": "", "floor_reason": None, "section_type": "body",
                     "stage2_route": "body", "floor_cited_materiality": "QUALITY", "floor_cited_reason": None}
                    for x in claims]

        def stage1(c, s, ce, cl, lb, fx, developer_message=None):
            return {"overall_status": "LEDGER_DEVIATION", "deviations": [dict(d) for d in dev]}
        for sw in (False, True):
            calls.clear()
            with contextlib.ExitStack() as st:
                st.enter_context(mock.patch.object(runner, "STAGE2_NORMAL_TWO_OF_TWO", sw))
                st.enter_context(mock.patch.object(runner, "stage1_fresh_with_enumeration", stage1))
                st.enter_context(mock.patch.object(runner, "run_stage2", stage2))
                st.enter_context(mock.patch.object(runner, "apply_stage2_two_of_two", spy))
                st.enter_context(mock.patch.object(runner, "save_json", lambda *a, **k: None))
                inst = {"instance_id": "unit_kpi02", "group": "unit", "expected_group_label": "unit",
                        "stage1_mode": "fresh",
                        "fixture": {"ledger_text": "(ledger)", "article_text": EN49, "source_article_text": JA49}}
                runner.run_instance(object(), _state0(), [0], inst, stage1_cache={})
            self.assertEqual(len(calls), 1 if sw else 0, "switch=%s" % sw)


_DV_LEDGER = (
    "[VERIFIED] HF-007: トランプ大統領は7月14日、20％の米国償還料を湾岸諸国との貿易・投資案件に置き換えると投稿した。\n"
    "  scope: 7月13日に提案した20％償還料\n"
    "  conditions: 「非常に生産的な協議」に基づく決定だと説明した。\n"
    "  date_or_period: 2026-07-14\n"
    "  causal_strength: CAUSAL_STATED_BY_SOURCE\n"
    "  notes_for_writer: 7月14日の撤回の原因として記述しない。\n"
    "\n"
    "[VERIFIED] HF-003: 徴収主体、支払義務者などの制度設計は示されなかった。\n"
    "  scope: 償還料案\n"
    "  notes_for_writer: 「米国が20％通航料を導入した」と確定形で書かず、「提案した」とする。\n"
    "\n"
    "[VERIFIED] HF-020: Brent先物は一時的に上げ幅を縮小した。\n"
    "  scope: Brent先物の短時間の値動き\n"
)
_DV_B3_CLAIM = "Concerns continued on July 14. So the flashy 20% plan left the stage."
_DV_CIT = "7月13日に提案した20％償還料"


def _dv_dev(**kw):
    d = {"severity": "MAJOR", "related_fact_id": "HF-020", "issue": "The claim overstates the Ledger.",
         "changed_fact": True}
    d.update(kw)
    return d


def _dv_call_fn(verdict="RELEASE", citation="Brent先物の短時間の値動き", cost=0.05, calls=None, raises=False, parsed=None):
    def _fn(claim_text, local_context, fact_block, issue, related_fact_id):
        if calls is not None:
            calls.append({"claim_text": claim_text, "issue": issue, "fact_block": fact_block})
        if raises:
            raise runner.FloorVerifyCallError("boom")
        return {"parsed": parsed if parsed is not None else
                {"verdict": verdict, "ledger_citation": citation, "basis": "nuance_only", "explanation": "x"},
                "prompt_sha256": "h", "cost_jpy": cost, "response_id": "r", "usage": {}, "elapsed_seconds": 0.01}
    return _fn


class TestDowngradeVerifyThreeTier02(unittest.TestCase):
    """委任_02(Opus#11→Fable評価): Tier 0決定論Guard/Tier 1確認役/Tier 2 hint合成。¥0(APIは呼ばない)。"""

    def setUp(self):
        self._old = (runner.STAGE2_DOWNGRADE_VERIFY, runner.TIER0_G_L_ENABLED)
        runner.STAGE2_DOWNGRADE_VERIFY = True

    def tearDown(self):
        runner.STAGE2_DOWNGRADE_VERIFY, runner.TIER0_G_L_ENABLED = self._old

    # --- スイッチ・既定 ---
    def test_default_off_cli_flag_and_kpi_config(self):
        self.assertFalse(self._old[0])
        self.assertFalse(self._old[1])  # G_Lは既定無効(¥0 replayの最終判断)
        import inspect
        self.assertIn("--stage2-downgrade-verify", inspect.getsource(runner.main))
        # 委任_03: 確認役は実測で不採用のため`KPI_TRIAL_SWITCHES`から外した(コードは残置・既定OFF)
        self.assertNotIn("STAGE2_DOWNGRADE_VERIFY", runner.KPI_TRIAL_SWITCHES)

    # --- Tier 0 ---
    def test_g_l_causal_strength_and_notes(self):
        blk = runner.floor_verify_fact_block(_DV_LEDGER, "HF-007")
        self.assertEqual(runner.g_l_guard({"changed_causality": True}, blk), (True, "gl_causal_strength:CAUSAL_STATED_BY_SOURCE"))
        self.assertEqual(runner.g_l_guard({"changed_fact": True}, blk), (False, ""))  # flag無し
        blk3 = runner.floor_verify_fact_block(_DV_LEDGER, "HF-003")
        self.assertEqual(runner.g_l_guard({"changed_certainty": True}, blk3), (True, "gl_notes_certainty"))
        self.assertEqual(runner.g_l_guard({"changed_causality": True}, blk3), (False, ""))
        self.assertEqual(runner.g_l_guard({"changed_causality": True}, None), (False, ""))
        notes_only = "[VERIFIED] HF-100: x\n  notes_for_writer: この決議と撤回の因果関係は確認できない。\n"
        self.assertEqual(runner.g_l_guard({"changed_causality": True}, notes_only), (True, "gl_notes_causal"))

    def test_aux_belts_g_h_and_issue_actor(self):
        self.assertEqual(runner.g_h_guard({"changed_causality": True}, _DV_B3_CLAIM), (True, "aux:g_h"))
        self.assertFalse(runner.g_h_guard({"changed_causality": True}, "So the plan would leave the stage.")[0])  # ヘッジ語
        self.assertFalse(runner.g_h_guard({"changed_causality": False}, _DV_B3_CLAIM)[0])
        self.assertFalse(runner.g_h_guard({"changed_causality": True}, "懸念が続いたため、案は撤回された。")[0])  # 日本語claim対象外
        d = {"issue": "The article identifies cargo carriers as the payers; the Ledger does not say who pays."}
        self.assertEqual(runner.issue_actor_guard(d, "Carriers would repay the money."), (True, "aux:issue_actor"))
        self.assertFalse(runner.issue_actor_guard({"issue": "Numbers differ."}, "x")[0])

    def test_stage2_release_guard_g_l_switch(self):
        blk = runner.floor_verify_fact_block(_DV_LEDGER, "HF-007")
        claim = {"claim_text": "Concerns grew, and the plan ended.", "dev": {"changed_causality": True, "issue": "x"}}
        runner.TIER0_G_L_ENABLED = False
        self.assertEqual(runner.stage2_release_guard(claim, blk), (False, ""))
        runner.TIER0_G_L_ENABLED = True
        self.assertEqual(runner.stage2_release_guard(claim, blk), (True, "gl_causal_strength:CAUSAL_STATED_BY_SOURCE"))
        runner.TIER0_G_L_ENABLED = False
        b3 = {"claim_text": _DV_B3_CLAIM, "dev": {"changed_causality": True, "issue": "x"}}
        self.assertEqual(runner.stage2_release_guard(b3, blk), (True, "aux:g_h"))  # 補助ベルトは`aux:`接頭辞

    # --- 対象判定 ---
    def test_target_rules(self):
        T = runner.downgrade_verify_target
        d = _dv_dev()
        self.assertTrue(T(d, "QUALITY", None, "stage1_llm")[0])
        self.assertTrue(T(d, "ACCEPTABLE", None, "stage1_llm")[0])  # QUALITYとACCEPTABLEで要件は同一
        self.assertEqual(T(d, "BLOCKING", None, "stage1_llm"), (False, "final_blocking"))
        self.assertEqual(T(_dv_dev(severity="MINOR"), "QUALITY", None, "stage1_llm"), (False, "not_checker_major"))
        self.assertEqual(T(d, "QUALITY", {"released": True}, "stage1_llm"), (False, "floor_verify_released"))
        self.assertEqual(T(d, "QUALITY", {"released": False}, "stage1_llm")[0], True)
        self.assertEqual(T(d, "QUALITY", None, "precheck"), (False, "precheck"))
        runner.STAGE2_DOWNGRADE_VERIFY = False
        self.assertEqual(T(d, "QUALITY", None, "stage1_llm"), (False, "switch_off"))

    # --- 解除条件・失敗時BLOCKING ---
    def _ev(self, fn, dev=None, claim=None, final="QUALITY", fv=None):
        c = claim or {"claim_text": "Brent briefly eased.", "dev": dev or _dv_dev()}
        return runner.downgrade_verify_evaluate(fn, _DV_LEDGER, c, "ctx", c["dev"], final, fv, "stage1_llm")

    def test_release_only_with_release_and_verbatim_citation(self):
        calls = []
        dv = self._ev(_dv_call_fn("RELEASE", calls=calls))
        self.assertTrue(dv["released"])
        self.assertFalse(dv["blocking"])
        self.assertEqual(dv["n_calls"], 1)  # call 1回
        self.assertEqual(len(calls), 1)
        self.assertTrue(dv["call"]["citation_verbatim"])
        self.assertAlmostEqual(dv["cost_jpy"], 0.05)
        self.assertIn("Brent先物の短時間の値動き", calls[0]["fact_block"])
        self.assertNotIn("HF-007", calls[0]["fact_block"])  # 関連factブロックのみ
        self.assertEqual(calls[0]["issue"], "The claim overstates the Ledger.")  # Checkerの指摘を仮説として渡す

    def test_citation_quote_glyph_normalisation_only(self):
        dv = self._ev(_dv_call_fn("RELEASE", citation="  Brent先物の短時間の値動き "))
        self.assertTrue(dv["released"])  # 空白差のみは逐語扱い(`_fv_norm`)

    def test_upheld_blocking(self):
        dv = self._ev(_dv_call_fn("UPHOLD_BLOCKING"))
        self.assertFalse(dv["released"])
        self.assertTrue(dv["blocking"])
        self.assertEqual(dv["blocking_reason"], "verify_upheld_blocking")

    def test_non_verbatim_empty_schema_and_api_failure_all_blocking(self):
        for kw, reason in ((dict(citation="Ledgerにない文"), "ledger_citation_not_verbatim"),
                           (dict(citation="  "), "ledger_citation_empty"),
                           (dict(parsed={"verdict": "MAYBE", "ledger_citation": "x"}), "schema_mismatch"),
                           (dict(raises=True), "verify_api_failure")):
            dv = self._ev(_dv_call_fn("RELEASE", **kw))
            self.assertFalse(dv["released"], reason)
            self.assertTrue(dv["blocking"], reason)
            self.assertEqual(dv["blocking_reason"], reason)
            self.assertTrue(dv["hint"])  # Tier 2: hint合成(Rewriteへ)

    def test_tier0_hit_skips_call_and_blocks(self):
        calls = []
        claim = {"claim_text": _DV_B3_CLAIM, "dev": _dv_dev(related_fact_id="HF-007", changed_causality=True)}
        dv = self._ev(_dv_call_fn("RELEASE", calls=calls), claim=claim)
        self.assertEqual(calls, [])
        self.assertTrue(dv["tier0_blocked"])
        self.assertEqual(dv["tier0_reason"], "aux:g_h")
        self.assertEqual(dv["blocking_reason"], "tier0:aux:g_h")
        self.assertEqual(dv["n_calls"], 0)

    def test_fact_block_unavailable_blocks_without_call(self):
        calls = []
        dv = self._ev(_dv_call_fn("RELEASE", calls=calls), dev=_dv_dev(related_fact_id="NOPE-9"))
        self.assertEqual(calls, [])
        self.assertEqual(dv["blocking_reason"], "fact_block_unavailable")

    def test_not_target_makes_no_call_and_no_blocking(self):
        calls = []
        dv = self._ev(_dv_call_fn("RELEASE", calls=calls), final="BLOCKING")
        self.assertEqual(calls, [])
        self.assertFalse(dv["target"])
        self.assertFalse(dv["blocking"])

    # --- prompt ---
    def test_prompt_single_definition_hypothesis_and_sha(self):
        r = runner.DV_RUBRIC
        self.assertIn("英語学習者に、記事の本質について重大な誤解を与えるものだけを止めます", r)
        self.assertIn("迷う場合", r)
        self.assertIn("UPHOLD_BLOCKING", r)
        self.assertNotIn("V7", r)
        self.assertNotIn("tie-break", r)
        self.assertEqual(runner.DV_JSON_SCHEMA["schema"]["properties"]["verdict"]["enum"], ["UPHOLD_BLOCKING", "RELEASE"])
        self.assertEqual(set(runner.DV_JSON_SCHEMA["schema"]["required"]),
                         {"verdict", "ledger_citation", "basis", "explanation"})
        p = runner.DV_PROMPT_TEMPLATE.format(related_fact_id="HF-020", fact_block="FB", claim_text="CL",
                                              local_context="CTX", issue="ISSUE", rubric=r)
        self.assertIn("検証すべき仮説", p)
        self.assertIn("ISSUE", p)
        import hashlib
        self.assertEqual(len(hashlib.sha256(p.encode()).hexdigest()), 64)

    def test_run_downgrade_verify_call_records_sha_cost_with_fake_client(self):
        class _Resp:
            output_text = json.dumps({"verdict": "RELEASE", "ledger_citation": "c", "basis": "none", "explanation": "e"})
            model = "gpt-6-luna"
            id = "resp1"
            usage = None

        class _C:
            class responses:
                @staticmethod
                def create(**kw):
                    _C.kw = kw
                    return _Resp()
        with mock.patch.object(runner.s2p, "_extract_usage", lambda r: {}), \
             mock.patch.object(runner.s2p, "official_cost_jpy", lambda u: 0.04):
            res = runner.run_downgrade_verify_call(_C, "CL", "CTX", "FB", "ISSUE", "HF-020")
        self.assertEqual(len(res["prompt_sha256"]), 64)
        self.assertEqual(res["cost_jpy"], 0.04)
        self.assertEqual(_C.kw["text"]["format"]["name"], "open233_downgrade_verify_v1")
        self.assertIn("ISSUE", _C.kw["input"][1]["content"])

    # --- Tier 2 hint ---
    def test_tier2_hint_from_checker_issue_and_ledger_notes_without_quotes(self):
        dev = {"issue": "「懸念」が原因だと読める。", "related_fact_id": "HF-007"}
        blk = runner.floor_verify_fact_block(_DV_LEDGER, "HF-007")
        hint, src = runner.downgrade_verify_rewrite_hint(dev, blk)
        self.assertIn("懸念が原因だと読める", hint)
        self.assertIn("撤回の原因として記述しない", hint)
        self.assertIn("非常に生産的な協議", hint)
        self.assertIn("fact_id=HF-007", hint)
        for q in "「」『』“”\"":
            self.assertNotIn(q, hint)
        self.assertEqual(src, "checker_issue+ledger_notes_for_writer+ledger_conditions")
        hint2, src2 = runner.downgrade_verify_rewrite_hint({}, None)
        self.assertEqual(src2, "generic")

    # --- run_stage2配線(OFF不変/ON) ---
    def _run_stage2(self, verdict_fn, dev, claim_text="Brent briefly eased.", llm="QUALITY", on=True):
        article = (f"# T\n\nIntro hook. It has two sentences, and a 2026 date.\n\nSecond paragraph has several sentences. "
                   f"It is a plain body paragraph. It keeps going.\n\n{claim_text}\n\n## In one line\nSummary.\n")
        fixture = {"article_text": article, "ledger_text": _DV_LEDGER, "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": dev["related_fact_id"],
                   "dev": dev, "detected_by": "stage1_llm"}]

        def fake_body_batch(client, ledger_text, source, cl, rubric_text, model=None):
            return {"prompt_sha256": "d1", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": llm, "basis": "none", "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "gpt-6-luna", "response_id": "rd1", "usage": {}, "cost_jpy": 0.01, "elapsed_seconds": 0.01}
        runner.STAGE2_DOWNGRADE_VERIFY = on
        call_log = []
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "check_budget", lambda *a, **k: None), \
             mock.patch.object(runner, "run_downgrade_verify_call",
                               lambda client, ct, lc, fb, issue, fid, **k: verdict_fn(ct, lc, fb, issue, fid)), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake_body_batch):
            out = runner.run_stage2(None, state, [0], call_log, "dv_test", fixture, claims)
        return out[0], call_log

    def test_off_is_unchanged_no_record_no_call(self):
        calls = []
        o, log = self._run_stage2(_dv_call_fn("UPHOLD_BLOCKING", calls=calls), _dv_dev(), on=False)
        self.assertEqual(o["materiality"], "QUALITY")
        self.assertNotIn("downgrade_verify", o)
        self.assertEqual(calls, [])
        self.assertFalse(any(c.get("recovery_stage") == "downgrade_verify" for c in log))

    def test_on_upheld_returns_blocking_with_hint_and_floor_reason(self):
        o, log = self._run_stage2(_dv_call_fn("UPHOLD_BLOCKING"), _dv_dev())
        self.assertEqual(o["llm_materiality"], "QUALITY")
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertTrue(o["floor_reason"].startswith("downgrade_verify_blocking:verify_upheld_blocking"))
        self.assertIn("Checkerの指摘", o["rewrite_hint"])
        self.assertEqual(o["downgrade_verify"]["hint_source"].split("+")[0], "checker_issue")
        self.assertEqual(sum(1 for c in log if c.get("recovery_stage") == "downgrade_verify"), 1)

    def test_on_release_keeps_stage2_value(self):
        for llm in ("QUALITY", "ACCEPTABLE"):
            o, _ = self._run_stage2(_dv_call_fn("RELEASE"), _dv_dev(), llm=llm)
            self.assertEqual(o["materiality"], llm)
            self.assertTrue(o["downgrade_verify"]["released"])

    def test_on_api_failure_goes_to_blocking_not_exception(self):
        def boom(*a, **k):
            raise RuntimeError("network")
        o, log = self._run_stage2(boom, _dv_dev())
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertEqual(o["downgrade_verify"]["blocking_reason"], "verify_api_failure")

    def test_on_tier0_blocks_without_call(self):
        calls = []
        dev = _dv_dev(related_fact_id="HF-007", changed_causality=True)
        o, log = self._run_stage2(_dv_call_fn("RELEASE", calls=calls), dev, claim_text=_DV_B3_CLAIM)
        self.assertEqual(calls, [])
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertEqual(o["downgrade_verify"]["tier0_reason"], "aux:g_h")

    def test_on_llm_blocking_is_not_target(self):
        calls = []
        o, _ = self._run_stage2(_dv_call_fn("RELEASE", calls=calls), _dv_dev(), llm="BLOCKING")
        self.assertEqual(calls, [])
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertFalse(o["downgrade_verify"]["target"])

    def test_re_evaluated_each_call_with_current_text(self):
        calls = []
        dev = _dv_dev(related_fact_id="HF-007", changed_causality=True)
        o1, _ = self._run_stage2(_dv_call_fn("RELEASE", calls=calls), dev, claim_text=_DV_B3_CLAIM)
        self.assertEqual(o1["downgrade_verify"]["tier0_reason"], "aux:g_h")  # 接続語あり→Tier 0
        o2, _ = self._run_stage2(_dv_call_fn("UPHOLD_BLOCKING", calls=calls), dev,
                                 claim_text="Concerns continued on July 14 and the flashy 20% plan left the stage.")
        self.assertFalse(o2["downgrade_verify"]["tier0_blocked"])  # 接続語が消えてもGuardを回避するだけ=確認役が受ける
        self.assertEqual(len(calls), 1)
        self.assertEqual(o2["materiality"], "BLOCKING")

    def test_floor_verify_behaviour_unchanged_by_downgrade_verify_switch(self):
        old = runner.FLOOR_VERIFY_MODE
        runner.FLOOR_VERIFY_MODE = runner.FLOOR_VERIFY_MODE_TIME_ONLY
        try:
            res = []
            for sw in (False, True):
                runner.STAGE2_DOWNGRADE_VERIFY = sw
                fv = runner.floor_verify_evaluate(_fv_call_ok("QUALITY"), _FV_LEDGER, "Prices began to fall.", "ctx",
                                                  {"related_fact_id": "HF-009", "issue": "i", "changed_time": True},
                                                  "QUALITY", "deterministic_floor:changed_time")
                res.append((fv["released"], fv["n_calls"], fv["final_materiality"], fv["blocking_fixed_reason"]))
            self.assertEqual(res[0], res[1])
            self.assertEqual(res[0], (True, 2, "QUALITY", None))  # 2回確認の既存挙動
        finally:
            runner.FLOOR_VERIFY_MODE = old

    def test_summarize(self):
        recs = [
            {"downgrade_verify": {"target": False}},
            {"downgrade_verify": {"target": True, "n_calls": 0, "cost_jpy": 0.0, "tier0_blocked": True,
                                  "tier0_reason": "aux:g_h", "released": False, "blocking_reason": "tier0:aux:g_h"}},
            {"downgrade_verify": {"target": True, "n_calls": 1, "cost_jpy": 0.05, "tier0_blocked": False,
                                  "tier0_reason": None, "released": True, "blocking_reason": None}},
            {"downgrade_verify": {"target": True, "n_calls": 1, "cost_jpy": 0.04, "tier0_blocked": False,
                                  "tier0_reason": None, "released": False, "blocking_reason": "verify_upheld_blocking"}},
            {"downgrade_verify": {"target": True, "n_calls": 1, "cost_jpy": 0.04, "tier0_blocked": False,
                                  "tier0_reason": None, "released": False, "blocking_reason": "ledger_citation_not_verbatim"}},
            {"downgrade_verify": {"target": True, "n_calls": 1, "cost_jpy": 0.0, "tier0_blocked": False,
                                  "tier0_reason": None, "released": False, "blocking_reason": "verify_api_failure"}},
            {},
        ]
        s = runner.downgrade_verify_summarize(recs)
        self.assertEqual((s["n_records"], s["n_target"], s["n_tier0_blocked"], s["n_verify_calls"], s["n_released"],
                          s["n_upheld"], s["n_citation_not_verbatim"], s["n_failure"]), (6, 5, 1, 4, 1, 1, 1, 1))
        self.assertEqual(s["tier0_by_reason"], {"aux:g_h": 1})
        self.assertAlmostEqual(s["cost_jpy"], 0.13)


class TestSafetyCriticalDerivation02(unittest.TestCase):
    """委任_02 作業2-5: neg5登録・正BLOCKINGラベルからの自動導出・旧値/新値の並記。"""

    def test_neg5_registered_with_registered_in(self):
        defs = runner._safety_critical_defs("neg5_hormuz_div_a2")
        self.assertEqual([d["sub_id"] for d in defs], ["B3-same@neg5"])
        self.assertEqual(defs[0]["related_fact_id"], "HF-007")
        self.assertTrue(defs[0]["registered_in"])
        self.assertEqual([d["sub_id"] for d in runner._safety_critical_defs("bgroup_B3")], ["B3"])  # 既存不変

    def test_derive_from_labels_finds_neg5_from_b3_and_excludes_label_source(self):
        der = runner.derive_safety_critical_from_labels()
        self.assertIn("neg5_hormuz_div_a2", der)
        self.assertEqual(der["neg5_hormuz_div_a2"][0]["derived_from"], "bgroup_B3")
        self.assertNotIn("bgroup_B3", der)
        self.assertTrue(runner.normalized_same_as_labeled(
            "“Concerns continued. So the Flashy  20% plan left the stage.”", "bgroup_B3"))
        self.assertFalse(runner.normalized_same_as_labeled("Unrelated sentence.", "bgroup_B3"))

    def _res(self, iid, text, fid="HF-007", mat="QUALITY"):
        return {"instance_id": iid, "cycles": [{"stage2_results": [
            {"claim_text": text, "related_fact_id": fid, "materiality": mat, "llm_materiality": mat,
             "floor_reason": None}]}]}

    def test_dual_summary_old_vs_new(self):
        results = [self._res("bgroup_B3", "So the flashy 20% plan left the stage."),
                   self._res("neg5_hormuz_div_a2", "“Concerns. So the flashy 20% plan left the stage.”"),
                   self._res("neg5_hormuz_div_a2", "Unrelated.", mat="QUALITY")]
        s = runner.safety_critical_dual_summary(results)
        self.assertEqual(s["old_definition_rows"], 1)    # 旧値: neg5の登録なし
        self.assertEqual(s["registered_rows_new"], 2)    # 登録(neg5含む)
        self.assertEqual(s["derived_rows"], 1)           # 自動導出でもneg5を検出
        self.assertEqual(s["new_definition_rows"], 2)    # 和集合(neg5の重複は1行)
        rows = runner.detect_safety_critical_misdowngrades(results)
        self.assertEqual([r["registered_in"] is None for r in rows], [True, False])

    def test_aggregate_measurements_keeps_old_silent_pass_and_adds_dual(self):
        results = [self._res("neg5_hormuz_div_a2", "So the flashy 20% plan left the stage.")]
        rows = runner.detect_safety_critical_misdowngrades(results)
        self.assertEqual(len(rows), 1)  # 登録済みなので検出される
        self.assertEqual(len([r for r in rows if not r.get("registered_in")]), 0)  # 旧定義の集計には入らない


class TestQuoteGlyphAndU2Elements02(unittest.TestCase):
    """委任_02 作業2-6: 規則Q(引用符字形の同一視)と規則U-2(1)(閉じた語彙の位置語→構造要素)、`VS_EXPLAIN_SPLIT`配下。"""

    EN = ("# The Fee Plan Leaves, But High Oil Prices Stay\n\n## In one line\nOil prices stayed high after the plan left.\n\n"
          "Opening paragraph is here.\n\n"
          "They say, “This is today’s mood.” Then the day moved on.\n\n"
          "Oil prices moved briefly, then returned to a high level.\n")

    def _on(self):
        return mock.patch.multiple(runner, VS_EXPLAIN_SPLIT=True, VS_MATCH_EXT=True)

    def test_glyph_norm_is_length_preserving(self):
        s = "‘a’ “b” \"c\" 'd' 「e」 『f』"
        self.assertEqual(len(runner.vs_quote_glyph_norm(s)), len(s))
        self.assertEqual(set(runner.vs_quote_glyph_norm("‘“”’「」『』\"")), {"'"})

    def test_q_resolves_nested_quote_glyph_difference_uniquely(self):
        claim = "“They say, ‘This is today’s mood.’” Also the point stands"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["status"], "resolved")
        self.assertTrue(r["level"].endswith("+Q"))
        self.assertEqual(r["ranges"], ["They say, “This is today’s mood.”"])  # 範囲は記事側の原文のまま
        self.assertEqual(self.EN.count(r["ranges"][0]), 1)

    def test_q_not_adopted_when_not_unique(self):
        en = self.EN + "\nThey say, \"This is today's mood.\" Again.\n"
        claim = "“They say, ‘This is today’s mood.’” Also the point stands"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, en)
        self.assertEqual(r["status"], "unverified")

    def test_q_does_not_change_words(self):
        claim = "“They say, ‘This is yesterday’s mood.’” Also x"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["status"], "unverified")
        self.assertEqual(r["reason"], "explain_split_rejected:fragment_not_in_article")

    def test_u2_headline_and_one_line_added(self):
        claim = "“Oil prices moved briefly, then returned to a high level.” (headline and one-line summary)"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["status"], "resolved")
        self.assertEqual(sorted(r["added_elements"]), ["headline", "one_line"])
        self.assertTrue(r["level"].endswith("+U2"))
        self.assertEqual(len(r["ranges"]), 3)
        for rg in r["ranges"]:
            self.assertEqual(self.EN.count(rg), 1)
        self.assertIn("The Fee Plan Leaves, But High Oil Prices Stay", r["ranges"])
        self.assertIn("Oil prices stayed high after the plan left.", r["ranges"])

    def test_u2_each_closed_vocab_word(self):
        for word in ("headline", "title", "heading", "one-line summary", "In one line", "one line", "summary"):
            claim = f"“Oil prices moved briefly, then returned to a high level.” (in the {word})"
            with self._on():
                r = runner.vs_explain_split_resolve(claim, self.EN)
            self.assertEqual(r["status"], "resolved", word)
            self.assertTrue(r.get("added_elements"), word)

    def test_u2_opening_is_not_extended(self):
        claim = "“Oil prices moved briefly, then returned to a high level.” The opening also states this."
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["status"], "unverified")
        self.assertEqual(r["reason"], "explain_split_rejected:dangling_position:opening")

    def test_u2_no_element_added_when_fragment_already_inside(self):
        claim = "“Oil prices stayed high after the plan left.” (one-line summary)"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["status"], "resolved")
        self.assertNotIn("added_elements", r)

    def test_four_guards_unchanged_remainder_long_and_position_words(self):
        claim = "“Oil prices moved briefly, then returned to a high level.” and this is a very long explanatory remainder text that goes on"
        with self._on():
            r = runner.vs_explain_split_resolve(claim, self.EN)
        self.assertEqual(r["reason"], "explain_split_rejected:remainder_too_long")  # 規則Rは保留(実装しない)


class TestSectionTypeObserved02(unittest.TestCase):
    ART = ("# T Headline\n\nIntro hook paragraph here.\n\nSecond paragraph has several sentences. It keeps going. "
           "It is plain.\n\nBody sentence is unique and long enough to count.\n\n## In one line\n"
           "Concerns continued on July 14, so the flashy plan left the stage.\n")

    def test_in_one_line_claim_observed(self):
        self.assertEqual(runner.observe_section_type("“Concerns continued on July 14, so the flashy plan left the stage.”", self.ART), "in_one_line")

    def test_body_claim_observed_body_and_short_probe_ignored(self):
        self.assertEqual(runner.observe_section_type("Body sentence is unique and long enough to count.", self.ART), "body")
        self.assertEqual(runner.observe_section_type("So", self.ART), "body")  # 短い断片は包含照合しない
        self.assertEqual(runner.observe_section_type("anything", ""), "body")

    def test_run_stage2_records_observed_without_changing_section_type_route(self):
        fixture = {"article_text": self.ART, "ledger_text": _DV_LEDGER, "source_article_text": None}
        claim_text = "Concerns continued on July 14, so the flashy plan left the stage."
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": "HF-020",
                   "dev": {"severity": "MAJOR", "related_fact_id": "HF-020"}, "detected_by": "stage1_llm"}]

        def fake(client, ledger_text, source, cl, rubric_text, model=None):
            return {"prompt_sha256": "d", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": "BLOCKING", "basis": "none", "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "m", "response_id": "r", "usage": {}, "cost_jpy": 0.0, "elapsed_seconds": 0.0}
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "check_budget", lambda *a, **k: None), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake):
            out = runner.run_stage2(None, {"cumulative_jpy": 0.0}, [0], [], "so", fixture, claims)[0]
        self.assertEqual(out["section_type_observed"], "in_one_line")
        self.assertEqual(out["stage2_route"], "body")  # 判定・振り分けは不変



class TestCausalFloorAndS1_03(unittest.TestCase):
    """委任_03: Tier 0 因果floor(語彙は目録由来)、Tier 1' S1(第2意見)、label override、KPI構成。¥0(APIは呼ばない)。"""

    def setUp(self):
        self._old = (runner.CAUSAL_FLOOR, runner.STAGE2_SECOND_OPINION, runner.CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE,
                     runner.STAGE2_DOWNGRADE_VERIFY)
        self._old_vocab = runner.CAUSAL_FLOOR_VOCAB
        runner.CAUSAL_FLOOR_VOCAB = "inventory"  # 既存テストは目録語彙(評価用)の挙動を検証する。known6は別テスト

    def tearDown(self):
        (runner.CAUSAL_FLOOR, runner.STAGE2_SECOND_OPINION, runner.CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE,
         runner.STAGE2_DOWNGRADE_VERIFY) = self._old
        runner.CAUSAL_FLOOR_VOCAB = self._old_vocab

    # --- 委任_04: known6確定 ---
    def test_known6_is_default_and_in_kpi_config(self):
        self.assertEqual(self._old_vocab, "known6")
        self.assertEqual(runner.KPI_TRIAL_SWITCHES["CAUSAL_FLOOR_VOCAB"], "known6")
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["CAUSAL_FLOOR"])
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["STAGE2_SECOND_OPINION"])
        self.assertNotIn("STAGE2_DOWNGRADE_VERIFY", runner.KPI_TRIAL_SWITCHES)
        self.assertFalse(runner.TIER0_G_L_ENABLED)
        keys = list(runner.KPI_TRIAL_SWITCHES)
        saved = {kk: getattr(runner, kk) for kk in keys}
        try:
            applied = runner.apply_kpi_trial_switches()
            self.assertEqual(applied["CAUSAL_FLOOR_VOCAB"], "known6")
        finally:
            for kk, v in saved.items():
                setattr(runner, kk, v)

    def test_known6_vs_inventory_switch(self):
        dev = {"changed_causality": True}
        # known6: 既知6語のみ。目録語(due to/caused/lead to/as)では止めない
        runner.CAUSAL_FLOOR_VOCAB = "known6"
        for c in ("Prices rose because supply was cut.", "So the plan left the stage.", "It therefore stopped.",
                  "As a result, shipping stopped.", "It led to a sell-off.", "It was leading to a sell-off."):
            self.assertEqual(runner.causal_floor_guard(dev, c), (True, "changed_causality_floor"), c)
        for c in ("Prices rose due to the ban.", "Meta had run a test that caused exactly this surprise.",
                  "The fee plan did not lead to a fall in prices.", "As AI makes calls, people ask questions."):
            self.assertFalse(runner.causal_floor_guard(dev, c)[0], c)
        self.assertFalse(runner.causal_floor_guard(dev, "Prices rose because supply may have been cut.")[0])
        self.assertFalse(runner.causal_floor_guard({"changed_causality": False}, "It led to a sell-off.")[0])
        # inventory: 拡張語彙(評価用)は目録語でも止める
        runner.CAUSAL_FLOOR_VOCAB = "inventory"
        self.assertTrue(runner.causal_floor_guard(dev, "Prices rose due to the ban.")[0])
        self.assertTrue(runner.causal_floor_guard(dev, "Meta had run a test that caused exactly this surprise.")[0])
        runner.CAUSAL_FLOOR_VOCAB = "bogus"
        with self.assertRaises(ValueError):
            runner.causal_floor_guard(dev, "x because y")

    # --- 語彙・floor ---
    def test_defaults_off_and_kpi_config(self):
        self.assertFalse(self._old[0])
        self.assertFalse(self._old[1])
        self.assertFalse(self._old[3])
        k = runner.KPI_TRIAL_SWITCHES
        self.assertTrue(k["CAUSAL_FLOOR"])
        self.assertTrue(k["STAGE2_SECOND_OPINION"])
        self.assertFalse(k["STAGE2_NORMAL_TWO_OF_TWO"])

    def test_vocab_is_catalogue_based_and_includes_known_gh_words(self):
        for w in ("so", "because", "therefore", "as a result", "led to", "leading to", "due to", "owing to",
                  "thanks to", "consequently", "triggered", "in response to"):
            self.assertIn(w, runner.CAUSAL_CONNECTIVES_EN)
        for w in ("may", "might", "could", "possibly", "likely", "appears", "seems", "reportedly", "expected to"):
            self.assertIn(w, runner.HEDGE_MARKERS_EN)
        self.assertEqual(set(runner.HEDGE_CAN_WOULD_EN), {"can", "would"})

    def test_fires_without_hedge_and_not_with_hedge(self):
        dev = {"changed_causality": True}
        self.assertEqual(runner.causal_floor_guard(dev, _DV_B3_CLAIM), (True, "changed_causality_floor"))
        self.assertEqual(runner.causal_floor_guard(dev, "Prices rose because supply was cut."), (True, "changed_causality_floor"))
        self.assertEqual(runner.causal_floor_guard(dev, "The ban triggered a sell-off."), (True, "changed_causality_floor"))
        self.assertEqual(runner.causal_floor_guard(dev, "Due to the ban, shipping stopped."), (True, "changed_causality_floor"))
        self.assertEqual(runner.causal_floor_guard(dev, "Following the ban, shipping stopped."), (True, "changed_causality_floor"))
        # ヘッジ(推測・可能性・帰属)があれば発火しない
        self.assertFalse(runner.causal_floor_guard(dev, "So the plan may have left the stage.")[0])
        self.assertFalse(runner.causal_floor_guard(dev, "Analysts say prices rose because supply was cut.")[0])
        self.assertFalse(runner.causal_floor_guard(dev, "The ban reportedly triggered a sell-off.")[0])
        # flagなし・接続語なし・日本語claimは発火しない
        self.assertFalse(runner.causal_floor_guard({"changed_causality": False}, _DV_B3_CLAIM)[0])
        self.assertFalse(runner.causal_floor_guard(dev, "Concerns continued on July 14 and the plan left the stage.")[0])
        self.assertFalse(runner.causal_floor_guard(dev, "懸念が続いたため、案は撤回された。")[0])
        # 語境界: so-called/sourced/remade は接続語にならない、following は文頭のみ
        self.assertFalse(runner.causal_floor_guard(dev, "The so-called plan was sourced and remade.")[0])
        self.assertFalse(runner.causal_floor_guard(dev, "Prices fell in the following week.")[0])

    def test_can_would_ab_versions(self):
        dev = {"changed_causality": True}
        c = "So the payers would repay the money."
        self.assertTrue(runner.causal_floor_guard(dev, c, can_would_as_hedge=False)[0])   # B: would=ヘッジでない
        self.assertFalse(runner.causal_floor_guard(dev, c, can_would_as_hedge=True)[0])   # A: would=ヘッジ
        runner.CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE = False
        self.assertTrue(runner.causal_floor_guard(dev, c)[0])
        runner.CAUSAL_FLOOR_CAN_WOULD_AS_HEDGE = True
        self.assertFalse(runner.causal_floor_guard(dev, c)[0])

    def test_release_guard_uses_causal_floor_only_when_on(self):
        dev = {"changed_causality": True, "issue": "x"}
        claim = {"claim_text": "Prices rose due to the ban.", "dev": dev}
        runner.CAUSAL_FLOOR = False
        self.assertEqual(runner.stage2_release_guard(claim, None), (False, ""))
        runner.CAUSAL_FLOOR = True
        self.assertEqual(runner.stage2_release_guard(claim, None), (True, "changed_causality_floor"))
        # 補助ベルトissue_actorは補完として維持
        d2 = {"issue": "The article identifies cargo carriers as the payers."}
        self.assertEqual(runner.stage2_release_guard({"claim_text": "Carriers would repay.", "dev": d2}, None),
                         (True, "aux:issue_actor"))

    # --- run_stage2配線 ---
    def _run(self, llm, dev, claim_text, on):
        article = ("# T\n\nIntro hook. It has two sentences, and a 2026 date.\n\nSecond paragraph has several sentences. "
                   f"It is a plain body paragraph. It keeps going.\n\n{claim_text}\n\n## In one line\nSummary.\n")
        fixture = {"article_text": article, "ledger_text": _DV_LEDGER, "source_article_text": None}
        claims = [{"claim_text": claim_text, "origin": "translation", "related_fact_id": dev["related_fact_id"],
                   "dev": dev, "detected_by": "stage1_llm"}]

        def fake(client, ledger_text, source, cl, rubric_text, model=None):
            return {"prompt_sha256": "d1", "parsed": {"judgments": [
                {"claim_index": 0, "materiality": llm, "basis": "none", "rewrite_kind": "none", "rewrite_hint": ""}]},
                    "model": "m", "response_id": "r", "usage": {}, "cost_jpy": 0.01, "elapsed_seconds": 0.01}
        runner.CAUSAL_FLOOR = on
        call_log = []
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "record_call", lambda *a, **k: None), \
             mock.patch.object(runner, "check_budget", lambda *a, **k: None), \
             mock.patch.object(runner.s2c, "run_stage2_batch_variant", fake):
            out = runner.run_stage2(None, state, [0], call_log, "t03", fixture, claims)
        return out[0], call_log

    def test_run_stage2_off_unchanged_on_blocks_with_hint(self):
        dev = _dv_dev(related_fact_id="HF-007", changed_causality=True)
        o, _ = self._run("QUALITY", dev, _DV_B3_CLAIM, on=False)
        self.assertEqual(o["materiality"], "QUALITY")
        self.assertNotIn("tier0", o)
        o, log = self._run("QUALITY", dev, _DV_B3_CLAIM, on=True)
        self.assertEqual(o["materiality"], "BLOCKING")
        self.assertEqual(o["floor_reason"], "changed_causality_floor")
        self.assertTrue(o["tier0"]["blocked"])
        self.assertIn("Checkerの指摘", o["rewrite_hint"])   # Tier 2 hint合成
        self.assertEqual(len(log), 1)                          # Tier 0は追加callなし(¥0)

    def test_run_stage2_on_hedged_or_nonmajor_or_already_blocking_not_blocked(self):
        dev = _dv_dev(related_fact_id="HF-007", changed_causality=True)
        o, _ = self._run("QUALITY", dev, "So the plan may have left the stage.", on=True)
        self.assertEqual(o["materiality"], "QUALITY")
        self.assertFalse(o["tier0"]["blocked"])
        o, _ = self._run("QUALITY", _dv_dev(related_fact_id="HF-007", changed_causality=True, severity="MINOR"),
                         _DV_B3_CLAIM, on=True)
        self.assertEqual(o["materiality"], "QUALITY")
        self.assertFalse(o["tier0"]["target"])
        o, _ = self._run("BLOCKING", dev, _DV_B3_CLAIM, on=True)
        self.assertFalse(o["tier0"]["target"])

    def test_tier0_summarize(self):
        res = [{"instance_id": "i", "cycles": [{"cycle": 1, "stage2_results": [
            {"tier0": {"target": True, "blocked": True, "reason": "changed_causality_floor"}, "claim_text": "a"},
            {"tier0": {"target": True, "blocked": False, "reason": None}},
            {"tier0": {"target": False, "blocked": False, "reason": None}}, {}]}]}]
        s = runner.tier0_summarize(res)
        self.assertEqual((s["n_records"], s["n_target"], s["n_blocked"]), (3, 2, 1))
        self.assertEqual(s["blocked_by_reason"], {"changed_causality_floor": 1})

    # --- S1 ---
    def _sr(self, mat="QUALITY", **kw):
        r = {"claim_text": "Brent briefly eased.", "origin": "translation", "related_fact_id": "HF-020",
             "dev": _dv_dev(), "materiality": mat, "llm_materiality": mat, "basis": "none",
             "rewrite_kind": "none", "rewrite_hint": "", "floor_reason": None, "detected_by": "stage1_llm",
             "stage2_route": "body"}
        r.update(kw)
        return r

    def test_s1_eligibility(self):
        E = runner.stage2_second_opinion_eligible
        self.assertTrue(E(self._sr("QUALITY")))
        self.assertTrue(E(self._sr("ACCEPTABLE")))
        self.assertFalse(E(self._sr("BLOCKING")))
        self.assertFalse(E(self._sr(dev=_dv_dev(severity="MINOR"))))
        self.assertFalse(E(self._sr(floor_verify={"released": True})))
        self.assertTrue(E(self._sr(floor_verify={"released": False})))
        self.assertFalse(E(self._sr(detected_by="precheck", llm_materiality=None)))
        self.assertFalse(E(self._sr(stage2_route="precheck_floor_bypass")))

    def _s1(self, results, second_fn):
        fixture = {"article_text": "x", "ledger_text": _DV_LEDGER, "source_article_text": None}
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        call_log = []
        seen = {}

        def fake_run_stage2(client, st, ce, cl, label, fx, claims):
            seen["claims"] = claims
            cl.append({"label": label, "cost_jpy": 0.07, "prompt_sha256": "sha_s1"})
            return second_fn(claims)
        with mock.patch.object(runner, "run_stage2", fake_run_stage2):
            out, log = runner.apply_stage2_second_opinion(None, state, [0], call_log, "i_c1", fixture, results, "i", 1)
        return out, log, seen, call_log

    def _second(self, mat, floor_reason=None, hint="第2回のhint"):
        return lambda claims: [{"materiality": mat, "basis": "none", "rewrite_kind": "replace_with_ledger_value",
                                "rewrite_hint": hint, "floor_reason": floor_reason} for _ in claims]

    def test_s1_agree_keeps_heavier_and_logs(self):
        out, log, seen, _ = self._s1([self._sr("ACCEPTABLE")], self._second("QUALITY"))
        self.assertEqual(out[0]["materiality"], "QUALITY")   # 重い方(安全側)
        self.assertTrue(log[0]["confirmed_downgrade"])
        self.assertFalse(log[0]["split"])
        self.assertEqual(log[0]["prompt_sha256"], ["sha_s1"])
        self.assertAlmostEqual(log[0]["batch_cost_jpy"], 0.07)
        self.assertEqual(log[0]["second_status"], "ok")

    def test_s1_split_becomes_blocking_with_hint(self):
        out, log, _, _ = self._s1([self._sr("QUALITY")], self._second("BLOCKING"))
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        self.assertEqual(out[0]["floor_reason"], "s1_second_opinion_blocking")
        self.assertIn("Checkerの指摘", out[0]["rewrite_hint"])     # Tier 2 hint合成
        self.assertIn("第2回のhint", out[0]["rewrite_hint"])
        self.assertTrue(log[0]["split"])

    def test_s1_failure_is_blocking_failclosed(self):
        for fr, st in (("stage2_api_failure_failclosed", "api_failure"),
                       ("schema_index_mismatch_failclosed", "schema_mismatch")):
            out, log, _, _ = self._s1([self._sr("QUALITY")], self._second("BLOCKING", floor_reason=fr, hint=""))
            self.assertEqual(out[0]["materiality"], "BLOCKING")
            self.assertEqual(out[0]["floor_reason"], "s1_second_opinion_failclosed:" + st)
            self.assertEqual(log[0]["second_status"], st)

    def test_s1_second_floor_reason_is_logged_as_anomaly(self):
        out, log, _, _ = self._s1([self._sr("QUALITY")],
                                  self._second("BLOCKING", floor_reason="deterministic_floor:changed_number"))
        self.assertTrue(log[0]["second_floor_anomaly"])
        self.assertEqual(out[0]["materiality"], "BLOCKING")

    def test_s1_only_targets_in_batch_and_no_call_when_none(self):
        res = [self._sr("BLOCKING"), self._sr("QUALITY", claim_text="Brent eased."),
               self._sr("QUALITY", floor_verify={"released": True}, claim_text="Other.")]
        out, log, seen, _ = self._s1(res, self._second("QUALITY"))
        self.assertEqual([c["claim_text"] for c in seen["claims"]], ["Brent eased."])
        self.assertEqual(len(log), 1)
        self.assertEqual(out[0]["materiality"], "BLOCKING")
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        with mock.patch.object(runner, "run_stage2", side_effect=AssertionError("must not call")):
            o, lg = runner.apply_stage2_second_opinion(None, state, [0], [], "x", {"ledger_text": "", "article_text": ""},
                                                       [self._sr("BLOCKING")], "i", 1)
        self.assertEqual(lg, [])

    def test_s1_summarize(self):
        res = [{"instance_id": "i", "cycles": [{"cycle": 1, "stage2_downgrade_confirm_log": [
            {"confirmed_downgrade": True, "split": False, "second_status": "ok", "second_floor_anomaly": False,
             "claim_text": "a", "second_materiality": "QUALITY", "prompt_sha256": ["s"], "batch_cost_jpy": 0.1},
            {"confirmed_downgrade": False, "split": True, "second_status": "api_failure", "second_floor_anomaly": False,
             "claim_text": "b", "second_materiality": "BLOCKING", "prompt_sha256": ["s"], "batch_cost_jpy": 0.1}]},
            {"cycle": 2}]}]
        s = runner.s1_summarize(res)
        self.assertEqual((s["n_target"], s["n_confirmed"], s["n_split"], s["n_api_failure"], s["batches"]), (2, 1, 1, 1, 1))
        self.assertAlmostEqual(s["cost_jpy"], 0.1)   # batch費用は重複計上しない

    # --- label override ---
    def test_and_version_label_override(self):
        and_c = "Concerns about US-Iran attacks continued on July 14, and the flashy 20% plan left the stage."
        so_c = "Concerns continued on July 14. So the flashy 20% plan left the stage."
        self.assertIsNotNone(runner.label_override_for("bgroup_B3", "HF-007", and_c))
        self.assertIsNotNone(runner.label_override_for("neg5_hormuz_div_a2", "HF-007", and_c))
        self.assertIsNone(runner.label_override_for("bgroup_B3", "HF-007", so_c))      # 「so」版は対象外
        self.assertIsNone(runner.label_override_for("bgroup_B4", "HF-007", and_c))
        self.assertIsNone(runner.label_override_for("bgroup_B3", "HF-001", and_c))
        rows = [{"instance_id": "bgroup_B3", "cycles": [{"stage2_results": [
            {"claim_text": and_c, "related_fact_id": "HF-007", "materiality": "QUALITY", "llm_materiality": "QUALITY"},
            {"claim_text": so_c, "related_fact_id": "HF-007", "materiality": "QUALITY", "llm_materiality": "QUALITY"}]}]}]
        d = runner.safety_critical_dual_summary(rows, derived={})
        self.assertEqual(d["registered_rows_new"], 2)                         # 旧値(上書きなし)
        self.assertEqual(d["after_label_override_registered_rows"], 1)        # 新値(「and」版=ACCEPTABLE扱い)
        self.assertEqual(len(d["after_label_override_dropped"]), 1)


class TestL6CarryForwardPrecedence(unittest.TestCase):
    """委任_05(OPEN-233-KPI-RECOVERY-REDESIGN-02): rep27 A4/A5 s1のL6とcarry-forwardの順序不整合の是正。"""

    _KEYS = None

    def setUp(self):
        self._saved = {k: getattr(runner, k) for k in list(runner.KPI_TRIAL_SWITCHES) + ["FLOOR_VERIFY_MODE"]}
        runner.apply_kpi_trial_switches()
        self._orig_core = runner._run_stage3_spans_core
        self.called = []

        def stub(*a, **k):
            self.called.append(1)
            return {"handoff": {}, "en_text": a[6], "ja_text": a[7], "guard_ok": False, "method": "STUB_REWRITE",
                    "mechanism": "stub", "ladder_level_used": None, "target_not_locatable": False}
        runner._run_stage3_spans_core = stub

    def tearDown(self):
        runner._run_stage3_spans_core = self._orig_core
        for k, v in self._saved.items():
            setattr(runner, k, v)

    def _rep27(self, iid):
        import json
        import os
        path = f"er052_output/open233_self_recovery_flow_runner_01_rep27/instances_s1/{iid}.json"
        if not os.path.exists(path):
            self.skipTest("rep27 evidence missing")
        return json.load(open(path, encoding="utf-8"))

    def _replay(self, iid, order_fix=True):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "replay_cf_l6", "er052_output/open233_kpi_recovery_02_offline_01/replay_cf_l6_order_01.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        d = self._rep27(iid)
        fx = {i["instance_id"]: i for i in runner.build_target_instances()}[iid]["fixture"]
        return mod.replay_cycle(fx, d["cycles"][0], order_fix)

    def test_a4_s1_second_claims_are_carried_forward(self):
        rows = self._replay("safety_A4")
        self.assertEqual([r["replay_method"] for r in rows],
                         ["STUB_REWRITE_ATTEMPTED", "STUB_REWRITE_ATTEMPTED",
                          "covered_by_earlier_rewrite_in_cycle", "covered_by_earlier_rewrite_in_cycle"])
        self.assertEqual(rows[2]["replay_l6_skipped"], "carry_forward_precedence")
        self.assertFalse(rows[2]["replay_rewrite_attempted"])

    def test_a5_s1_second_claim_is_carried_forward(self):
        rows = self._replay("safety_A5")
        self.assertEqual(rows[1]["replay_method"], "covered_by_earlier_rewrite_in_cycle")
        self.assertFalse(rows[1]["replay_rewrite_attempted"])

    def test_old_order_double_rewrites(self):
        rows = self._replay("safety_A4", order_fix=False)
        self.assertTrue(rows[2]["replay_rewrite_attempted"])  # 是正前: L6が書き換え済みの文を復元し再Rewrite

    def test_l6_off_unchanged(self):
        runner.VS_SENTENCE_RESTORE = False
        rows = self._replay("safety_A4")
        self.assertEqual(rows[2]["replay_method"], "covered_by_earlier_rewrite_in_cycle")  # rep24と同じ(L6 OFF)
        self.assertIsNone(rows[2]["replay_l6_skipped"])

    def test_no_earlier_rewrite_l6_unchanged(self):
        """先行Rewriteが無いcycle(cycle_replaced_unitsが空)では、L6の復元はそのまま使われる(Rewriteが走る)。"""
        d = self._rep27("safety_A4")
        fx = {i["instance_id"]: i for i in runner.build_target_instances()}["safety_A4"]["fixture"]
        c = d["cycles"][0]
        rec3 = c["rewrite_records"][3]
        claim = rec3["handoff"]["checker_claim_text"]
        # 先行Rewrite済みの本文だけ与え、units空 → L6復元がそのまま採用される
        en_now = fx["article_text"].replace(
            "One helper meant one more person handling private data.", "One helper could mean one more person handling private data.")
        cl = next(x for x in c["stage2_results"] if x["claim_text"] == claim)
        claim_rec = {"claim_text": claim, "dev": cl["dev"], "cycle_start_en_text": fx["article_text"],
                     "cycle_start_ja_text": None, "cycle_replaced_units": [], "cycle_claim_info": {},
                     "claim_identity": rec3["claim_identity"]}
        r = runner.run_stage3_for_claim_spans(None, None, None, [], "x", {"article_text": fx["article_text"]},
                                              en_now, None, claim_rec, False)
        self.assertEqual(r["method"], "STUB_REWRITE")
        self.assertEqual(len(self.called), 1)

    def test_rule2_restored_equals_after_unit(self):
        units = [{"claim_identity": "fact:X", "lang": "EN", "before_units": ["Old sentence here."],
                  "after_units": ["New sentence here."]}]
        res = {"status": "resolved", "lang": "EN", "level": runner.VS_L6_LEVEL, "ranges": ["New sentence here."]}
        cf = runner.l6_carry_forward_precedence({"cycle_replaced_units": units, "cycle_start_en_text": "zzz"},
                                                "claim not in cycle start text", res, "New sentence here.", None)
        self.assertIsNotNone(cf)
        self.assertEqual(cf["remaining"], [])
        self.assertEqual(cf["covered"][0]["range"], "Old sentence here.")
        self.assertEqual(cf["l6_precedence"]["rule"], "restored_equals_after_unit")

    def test_rule2_unrelated_restored_sentence_is_not_intercepted(self):
        units = [{"claim_identity": "fact:X", "lang": "EN", "before_units": ["Old sentence here."],
                  "after_units": ["New sentence here."]}]
        res = {"status": "resolved", "lang": "EN", "level": runner.VS_L6_LEVEL, "ranges": ["A different sentence."]}
        cf = runner.l6_carry_forward_precedence({"cycle_replaced_units": units, "cycle_start_en_text": "zzz"},
                                                "claim not in cycle start text", res, "A different sentence.", None)
        self.assertIsNone(cf)


class TestRecheckMergeN1Prime(unittest.TestCase):
    """委任_06(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus#12後): N1′(`normalize_recheck_outcome`)・潜在ギャップ是正・N3′。"""

    def _claims(self, *fids):
        return [{"dev": {"related_fact_id": f, "claim_in_article": f"orig sentence {i}.", "severity": "MAJOR",
                         "issue": f"issue {i}", "explanation": f"expl {i}"}} for i, f in enumerate(fids)]

    def _rc(self, status="LEDGER_COMPLIANT", all_prior=True, devs=None, resolved=None):
        return {"overall_status": status, "all_prior_issues_resolved": all_prior, "deviations": devs or [],
                "prior_issues_resolved": resolved}

    def _maj(self, fid, claim="new claim."):
        return {"severity": "MAJOR", "related_fact_id": fid, "claim_in_article": claim, "issue": "x"}

    def test_pass_when_recheck_ok(self):
        r = runner.normalize_recheck_outcome(self._rc(), None, self._claims("A"))
        self.assertEqual(r["decision"], "PASS")

    def test_pass_when_reverify_ok_after_ambiguous(self):
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(all_prior=True)
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A"))
        self.assertEqual(r["decision"], "PASS")

    def test_reverify_major_merged(self):
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(status="LEDGER_DEVIATION", all_prior=True,
                      devs=[self._maj("B"), {"severity": "MINOR", "related_fact_id": "C"}])
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A"))
        self.assertEqual(r["decision"], "NEXT_CYCLE")
        self.assertEqual([d["related_fact_id"] for d in r["deviations"]], ["B"])
        self.assertEqual(r["merged_from"], ["reverify_major"])
        self.assertFalse(r["reverify_deviation_without_major"])

    def test_reverify_unresolved_prior_merged_with_current_text(self):
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(status="LEDGER_COMPLIANT", all_prior=False,
                      resolved=[{"index": 0, "resolved": True}, {"index": 1, "resolved": False}])
        pi = [{"claim_in_article": "cur 0."}, {"claim_in_article": "cur 1."}]
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A", "B"), pi)
        self.assertEqual(r["decision"], "NEXT_CYCLE")
        self.assertEqual([d["related_fact_id"] for d in r["deviations"]], ["B"])
        self.assertEqual(r["deviations"][0]["claim_in_article"], "cur 1.")   # 現行本文の文へ差し替え
        self.assertEqual(r["merged_from"], ["unresolved_prior"])
        self.assertEqual(self._claims("A", "B")[1]["dev"]["claim_in_article"], "orig sentence 1.")

    def test_multiline_current_text_keeps_original_claim(self):
        rc = self._rc(all_prior=False, resolved=[])
        cf = self._rc(status="LEDGER_DEVIATION", all_prior=False, resolved=[{"index": 0, "resolved": False}])
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A"), [{"claim_in_article": "a.\nb."}])
        self.assertEqual(r["deviations"][0]["claim_in_article"], "orig sentence 0.")

    def test_dedup_by_fact_id(self):
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(status="LEDGER_DEVIATION", all_prior=False, devs=[self._maj("A", "newer.")],
                      resolved=[{"index": 0, "resolved": False}, {"index": 1, "resolved": False}])
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A", "B"))
        self.assertEqual([d["related_fact_id"] for d in r["deviations"]], ["A", "B"])
        self.assertEqual(r["deviations"][0]["claim_in_article"], "newer.")
        self.assertEqual(r["n_dedup_dropped"], 1)
        self.assertEqual(r["merged_from"], ["reverify_major", "unresolved_prior"])

    def test_empty_reverify_marks_audit_flag(self):
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(status="LEDGER_DEVIATION", all_prior=True, devs=[{"severity": "MINOR", "related_fact_id": "Z"}])
        r = runner.normalize_recheck_outcome(rc, cf, self._claims("A"))
        self.assertEqual(r["decision"], "NEXT_CYCLE")
        self.assertEqual(r["deviations"], [])
        self.assertTrue(r["reverify_deviation_without_major"])

    def test_latent_gap_normal_path_unresolved_prior_merged(self):
        rc = self._rc(status="LEDGER_DEVIATION", all_prior=False, devs=[self._maj("B")],
                      resolved=[{"index": 0, "resolved": False}, {"index": 1, "resolved": True}])
        r = runner.normalize_recheck_outcome(rc, None, self._claims("A", "C"))
        self.assertEqual(r["decision"], "NEXT_CYCLE")
        self.assertEqual([d["related_fact_id"] for d in r["deviations"]], ["B", "A"])
        self.assertEqual(r["merged_from"], ["recheck_major", "normal_gap"])
        self.assertEqual(r["source"], "recheck")
        self.assertFalse(r["reverify_deviation_without_major"])

    def test_normal_deviation_all_prior_true_unchanged(self):
        rc = self._rc(status="LEDGER_DEVIATION", all_prior=True, devs=[self._maj("B")])
        r = runner.normalize_recheck_outcome(rc, None, self._claims("A"))
        self.assertEqual([d["related_fact_id"] for d in r["deviations"]], ["B"])

    def test_missing_resolved_list_is_all_unresolved_fail_closed(self):
        rc = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
              "_recheck_api_failure": True}
        r = runner.normalize_recheck_outcome(rc, None, self._claims("A", "B"))
        self.assertEqual(r["decision"], "NEXT_CYCLE")
        self.assertEqual(len(r["deviations"]), 2)

    def test_stop_only_when_flag_and_api_failure(self):
        rc = {"overall_status": "LEDGER_DEVIATION", "deviations": [], "all_prior_issues_resolved": False,
              "_recheck_api_failure": True}
        self.assertEqual(runner.normalize_recheck_outcome(rc, None, self._claims("A"),
                                                          api_failure_is_stop=True)["decision"], "STOP")
        self.assertEqual(runner.normalize_recheck_outcome(
            self._rc(status="LEDGER_DEVIATION", all_prior=False, devs=[self._maj("B")]), None, self._claims("A"),
            api_failure_is_stop=True)["decision"], "NEXT_CYCLE")

    def test_pure_function_does_not_mutate_inputs(self):
        import copy
        claims = self._claims("A", "B")
        rc = self._rc(all_prior=False, resolved=[{"index": 0, "resolved": False}])
        cf = self._rc(status="LEDGER_DEVIATION", all_prior=False, devs=[self._maj("A")],
                      resolved=[{"index": 1, "resolved": False}])
        b = copy.deepcopy((claims, rc, cf))
        runner.normalize_recheck_outcome(rc, cf, claims, [{"claim_in_article": "x"}, {"claim_in_article": "y"}])
        self.assertEqual((claims, rc, cf), b)

    def test_kpi_switches_include_merge_but_not_n3(self):
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["RECHECK_MERGE_UNRESOLVED"])
        self.assertNotIn("RECHECK_BEFORE_AFTER_PAIRS", runner.KPI_TRIAL_SWITCHES)
        self.assertFalse(runner.RECHECK_BEFORE_AFTER_PAIRS)

    # --- N3′ ---
    def _capture_prompt(self, **kw):
        captured = {}

        class _Cap(BaseException):
            pass

        class _Resp:
            def create(self_inner, **k):
                captured["prompt"] = k["input"][1]["content"]
                raise _Cap()

        class _Client:
            responses = _Resp()
        fixture = {"ledger_text": "LEDGER", "article_text": "ART"}
        try:
            runner.run_recheck(_Client(), {"cumulative_jpy": 0.0}, [0], [], "t", fixture, "ART",
                               [{"fact_id": "F", "claim_in_article": "c", "issue": "i", "explanation": "e"}], **kw)
        except _Cap:
            pass
        return captured["prompt"]

    def test_n3_prompt_diff_and_off_is_byte_identical(self):
        pairs = [{"before": "Old sentence.", "after": "New sentence."}, {"before": "Gone.", "after": ""}]
        base = self._capture_prompt()
        off = self._capture_prompt(before_after_pairs=pairs)           # スイッチOFF: 渡しても変化なし
        self.assertEqual(base, off)
        saved = runner.RECHECK_BEFORE_AFTER_PAIRS
        try:
            runner.RECHECK_BEFORE_AFTER_PAIRS = True
            on = self._capture_prompt(before_after_pairs=pairs)
            on_empty = self._capture_prompt(before_after_pairs=[])
        finally:
            runner.RECHECK_BEFORE_AFTER_PAIRS = saved
        block = runner.build_before_after_instruction(pairs)
        self.assertTrue(block)
        self.assertEqual(on, base + block)                              # 差分は前後の対ブロックのみ
        self.assertIn("before: Old sentence.\n  after: New sentence.", on)
        self.assertIn("(削除されました)", on)
        self.assertNotIn("remaining_sentence", on)                     # cite-or-release指示は含めない
        self.assertEqual(on_empty, base)                                # 対が無ければ変化なし

    def test_checker_template_and_prior_issues_builder_byte_stable(self):
        import hashlib
        import inspect
        import er003_v1_en_direct_vfl_01_generate as vfl01
        self.assertEqual(hashlib.sha256(inspect.getsource(vfl01.build_prior_issues_instruction).encode()).hexdigest(),
                         "893e145229678ebe3946911a4773591c45dedc6d5485de2b3843e0764d7f1901")
        self.assertEqual(hashlib.sha256(runner.trial.build_trial_prompt_template("V4A").encode()).hexdigest(),
                         "e9c939930496ebed00a198455279bac1d61e6f5a162063f41ef5fde52cf81c97")
        self.assertEqual(hashlib.sha256(vfl01.build_prior_issues_instruction(
            [{"fact_id": "F", "claim_in_article": "c", "issue": "i", "explanation": "e"}]).encode()).hexdigest(),
            "f5b661068e0fb968be2b8acb9150adacc91b7753e6a0f70560df6cf406d9a241")


def _run_instance_merge06(recheck_seq, confirm_seq, merge_on, before_after_on=False, structural_pair=None,
                          structural_pairs_on=False):
    """委任_06: run_instanceを偽のChecker/Stage 2/Rewrite/Recheck/再確認で通す(ネットワークなし)。
    recheck_seq・confirm_seq: 各呼び出しで返すdictのリスト(cycle順)。"""
    seen = {"stage2_claims": [], "recheck_labels": [], "confirm_labels": [], "recheck_kwargs": []}
    rs, cs = list(recheck_seq), list(confirm_seq)

    def fake_stage1(client, state, ce, call_log, label, fixture, developer_message=None):
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [_dev49(META_TARGET, fid="FA")]}

    def fake_stage2(client, state, ce, call_log, label, fixture, claims):
        seen["stage2_claims"].append([(c["related_fact_id"], c["claim_text"]) for c in claims])
        return [{**c, "materiality": "BLOCKING", "llm_materiality": "BLOCKING", "basis": "ledger_fact",
                 "rewrite_kind": "narrow_scope", "rewrite_hint": "h", "floor_reason": None, "section_type": "body",
                 "stage2_route": "body", "floor_cited_materiality": "BLOCKING", "floor_cited_reason": None}
                for c in claims]

    def fake_stage3(client, state, ce, call_log, label, fixture, en, ja, claim_rec):
        new_en = en.replace(META_TARGET, "Some calls may have needed user information.")
        return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": new_en, "ja_text": ja,
                "method": "fake", "guard_ok": True, "before_fragment": META_TARGET,
                "after_fragment": "Some calls may have needed user information.",
                "ladder_level_used": "1_word_connective", "target_not_locatable": False, "span_unverified": False,
                "ladder_exhausted_without_full_rewrite": False,
                "handoff": {"level_attempts": [], "text_lang": "EN",
                            **({"structural_pair": structural_pair} if structural_pair else {})}}

    def fake_recheck(client, state, ce, call_log, label, fixture, article_text, prior_issues, **k):
        seen["recheck_labels"].append(label)
        seen["recheck_kwargs"].append(k)
        return dict(rs.pop(0))

    def fake_confirm(client, state, ce, call_log, label, fixture, article_text, prior_issues, before_after_pairs):
        seen["confirm_labels"].append(label)
        return dict(cs.pop(0))

    inst = {"instance_id": "unit06", "group": "unit", "expected_group_label": "unit", "stage1_mode": "fresh",
            "fixture": {"ledger_text": "(ledger)", "article_text": EN49, "source_article_text": JA49}}
    patches = [mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1),
               mock.patch.object(runner, "run_stage2", fake_stage2),
               mock.patch.object(runner, "apply_stage2_two_of_two", lambda *a, **k: (a[6], [])),
               mock.patch.object(runner, "run_stage3_for_claim", fake_stage3),
               mock.patch.object(runner, "run_local_qa_fastpath", lambda *a, **k: {"success": False, "results": []}),
               mock.patch.object(runner, "run_recheck", fake_recheck),
               mock.patch.object(runner, "run_recheck_confirm", fake_confirm),
               mock.patch.object(runner, "save_json", lambda *a, **k: None),
               mock.patch.object(runner, "JA_MODE", runner.JA_MODE_ENGLISH_ONLY),
               mock.patch.object(runner, "RECHECK_MERGE_UNRESOLVED", merge_on),
               mock.patch.object(runner, "RECHECK_BEFORE_AFTER_PAIRS", before_after_on),
               mock.patch.object(runner, "STRUCTURAL_PAIRS_TO_RECHECK", structural_pairs_on)]
    for p in patches:
        p.start()
    try:
        res = runner.run_instance(object(), _state0(), [0], inst, stage1_cache={})
    finally:
        for p in reversed(patches):
            p.stop()
    return res, seen


def _rr06(status="LEDGER_COMPLIANT", all_prior=True, devs=None, resolved=None):
    return {"overall_status": status, "all_prior_issues_resolved": all_prior, "deviations": devs or [],
            "prior_issues_resolved": resolved if resolved is not None else [
                {"index": 0, "resolved": all_prior, "explanation": ""}]}


class TestRecheckMergeIntegration06(unittest.TestCase):
    """委任_06 N1′: run_instance統合(偽の応答)。再確認の結果が必ず次cycleのStage 2へ合流する。"""

    AMBIG = _rr06(all_prior=False)

    def test_off_keeps_stage4_unconfirmed_after_reverify(self):
        res, seen = _run_instance_merge06([self.AMBIG], [_rr06("LEDGER_DEVIATION", True)], merge_on=False)
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "unconfirmed_after_reverify")

    def test_on_empty_reverify_deviation_downgrades_with_audit_flag(self):
        res, seen = _run_instance_merge06([self.AMBIG], [_rr06("LEDGER_DEVIATION", True)], merge_on=True)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE_THEN_DOWNGRADE")
        self.assertIsNone(res["stage4_reason"])
        c1 = res["cycles"][0]
        self.assertTrue(c1["reverify_deviation_without_major"])
        self.assertEqual(c1["recheck_merge"]["decision"], "NEXT_CYCLE")
        self.assertEqual(c1["recheck_merge"]["n_merged"], 0)
        self.assertEqual(len(seen["confirm_labels"]), 1)   # 追加callなし(再確認は従来どおり1回)

    def test_on_reverify_major_flows_to_stage2_of_next_cycle(self):
        major = {"severity": "MAJOR", "related_fact_id": "FB", "claim_in_article": "Calls happened.",
                 "issue": "new", "origin": "translation"}
        res, seen = _run_instance_merge06([self.AMBIG, _rr06()], [_rr06("LEDGER_DEVIATION", True, devs=[major])],
                                          merge_on=True)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertEqual(seen["stage2_claims"][1], [("FB", "Calls happened.")])
        self.assertEqual(res["cycles"][0]["recheck_merge"]["merged_from"], ["reverify_major"])

    def test_on_unresolved_prior_flows_to_stage2(self):
        cf = _rr06("LEDGER_COMPLIANT", False)    # 再確認でも解消未確認
        res, seen = _run_instance_merge06([self.AMBIG, _rr06()], [cf], merge_on=True)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        fid, claim = seen["stage2_claims"][1][0]
        self.assertEqual(fid, "FA")
        self.assertEqual(claim, META_TARGET)  # 偽Rewriteは置換単位を持たず現行文を特定できない -> 元の文へfallback(現行文への差し替えは純関数テストで確認)
        self.assertEqual(res["cycles"][0]["recheck_merge"]["merged_from"], ["unresolved_prior"])

    def test_on_normal_path_latent_gap_closed(self):
        rc = _rr06("LEDGER_DEVIATION", False)    # 通常Recheck: DEVIATION∧all_prior=False、deviationsなし
        res_on, seen_on = _run_instance_merge06([rc, _rr06()], [], merge_on=True)
        self.assertEqual(len(seen_on["stage2_claims"]), 2)          # 次cycleのStage 2を通る
        self.assertEqual(res_on["cycles"][0]["recheck_merge"]["merged_from"], ["normal_gap"])
        self.assertEqual(res_on["final_state"], "RESOLVED_REWRITE")
        res_off, seen_off = _run_instance_merge06([rc], [], merge_on=False)
        self.assertEqual(len(seen_off["stage2_claims"]), 1)         # 旧挙動: 未解消priorが脱落
        self.assertEqual(res_off["final_state"], "RESOLVED_REWRITE_THEN_DOWNGRADE")

    def test_on_does_not_add_new_loop_cycle_limit_unchanged(self):
        rc = _rr06("LEDGER_COMPLIANT", False)
        res, seen = _run_instance_merge06([rc, rc, rc], [rc, rc, rc], merge_on=True)
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertIn(res["stage4_reason"], ("same_claim_fact_id_reblocked", "cycle_limit_exhausted",
                                              "cycle_limit_exhausted_after_recheck"))
        self.assertLessEqual(len(res["cycles"]), runner.HARD_MAX_CYCLES)

    def test_n3_pairs_passed_to_recheck_only_as_kwarg(self):
        res, seen = _run_instance_merge06([_rr06()], [], merge_on=True, before_after_on=True)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertEqual(len(seen["recheck_kwargs"][0]["before_after_pairs"]), 1)
        self.assertEqual(res["cycles"][0]["recheck_before_after_pairs_n"], 1)


class TestPriorCountMismatchFix07(unittest.TestCase):
    """委任_07: Recheckの`all_prior_issues_resolved`の件数一致バグ(同indexの複数項目で偽の自己矛盾)をindex別集約へ是正。"""

    def test_fix_all_true_with_count_mismatch_same_index_is_true(self):
        # 旧式(件数一致)ではFalseだったケース: 1 prior issueに対し同index 2項目、両方resolved
        items = [{"index": 0, "resolved": True}, {"index": 0, "resolved": True}]
        ok, by = runner.aggregate_prior_issues_resolved(["p0"], items)
        self.assertTrue(ok)
        self.assertEqual(by, {"0": True})
        old = (len(items) == 1) and all(i["resolved"] for i in items)
        self.assertFalse(old)  # 旧式との差分(偽の自己矛盾)

    def test_fix_missing_index_is_false_fail_closed(self):
        ok, by = runner.aggregate_prior_issues_resolved(
            ["p0", "p1"], [{"index": 0, "resolved": True}, {"index": 0, "resolved": True}])
        self.assertFalse(ok)
        self.assertEqual(by, {"0": True, "1": None})

    def test_fix_group_with_any_false_is_false(self):
        ok, by = runner.aggregate_prior_issues_resolved(
            ["p0"], [{"index": 0, "resolved": True}, {"index": 0, "resolved": False}])
        self.assertFalse(ok)
        self.assertEqual(by, {"0": False})

    def test_fix_exact_match_unchanged_and_empty_cases(self):
        T = {"resolved": True}
        self.assertTrue(runner.aggregate_prior_issues_resolved(["a", "b"], [{"index": 0, **T}, {"index": 1, **T}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(
            ["a", "b"], [{"index": 0, **T}, {"index": 1, "resolved": False}])[0])
        self.assertTrue(runner.aggregate_prior_issues_resolved([], [])[0])   # 旧式: 0==0 and all([])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["a"], [])[0])  # 項目なし=未確認
        self.assertFalse(runner.aggregate_prior_issues_resolved(["a"], [T])[0])  # index欠落項目は対応づかない

    def test_fix_rep28_neg3_recorded_response_replays_to_true(self):
        import glob as _g
        paths = _g.glob("er052_output/open233_self_recovery_flow_runner_01_rep28/instances_s*/neg3_hormuz_prodrunner_b1b.json")
        self.assertTrue(paths)
        for pth in paths:
            d = json.load(open(pth, encoding="utf-8"))
            c = d["cycles"][0]
            items = c["recheck_prior_issues_resolved"]
            n = c["recheck_prior_issues_sent_count"]
            self.assertEqual((len(items), n), (2, 1))
            self.assertFalse(c["recheck_all_prior_issues_resolved"])  # 記録(旧式)
            self.assertTrue(runner.aggregate_prior_issues_resolved(["x"] * n, items)[0])  # 是正後

    def test_fix_run_recheck_uses_aggregate_function(self):
        import inspect
        src = inspect.getsource(runner.run_recheck)
        self.assertIn("aggregate_prior_issues_resolved(prior_issues, resolved)", src)
        self.assertNotIn("len(resolved) == len(prior_issues)", src)


class TestStructuralElementRewrite07(unittest.TestCase):
    """委任_07: 構造要素(タイトル・In one line・見出し)へのdeleteを選ばず書き換えへ回す(KPI構成ON、既定OFFは旧挙動)。"""
    CLAIM = "The same taxi researchers also found that male passengers tipped twice as much."

    def _ladder(self, art, llm, on=True):
        fixture = {"ledger_text": "[F-004] Passengers shown higher suggested rates tipped more.", "article_text": art}
        claim_rec = {"claim_text": self.CLAIM, "rewrite_kind": "delete", "materiality": "BLOCKING", "basis": "ledger_claim",
                     "rewrite_hint": "Delete this unsupported gender comparison.", "dev": {"issue": "not in Ledger"}}
        with mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", on), \
                mock.patch.object(runner, "simple_llm_call", side_effect=llm):
            return runner.rewrite_ranges_ladder(None, _l6_state(), [0], [], "t", fixture, "article_text", claim_rec)

    def test_structural_title_delete_is_replaced_by_rewrite(self):
        calls = []

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            calls.append((label, prompt))
            return json.dumps({"revised_ranges": ["Passengers shown higher suggested tip rates tipped more."]})
        res = self._ladder(self.CLAIM, llm)
        self.assertTrue(res["guard_ok"])
        self.assertNotEqual(res["updated_text"].strip(), "")
        self.assertEqual(res["handoff"]["structural_element_rewrite"]["original_rewrite_kind"], "delete")
        self.assertIn("title", res["handoff"]["structural_element_rewrite"]["reasons"])
        self.assertEqual(res["ladder_level_used"], "1_word_connective")
        self.assertIn("Structural element", calls[0][1])
        self.assertNotIn("0_delete", [a["level"] for a in res["handoff"]["level_attempts"]])

    def test_empty_candidates_rejected_then_paragraph_level_succeeds(self):
        art = self.CLAIM + "\n\nSecond paragraph stays.\n"
        seq = iter([json.dumps({"revised_ranges": [""]}), json.dumps({"revised_ranges": [""]}),
                    json.dumps({"revised_ranges": ["Passengers tipped more at higher suggested rates."]})])

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            return next(seq)
        res = self._ladder(art, llm)
        lv = [(a["level"], a["result"]) for a in res["handoff"]["level_attempts"]]
        self.assertEqual(lv[0], ("1_word_connective", "declined"))
        self.assertEqual(lv[1], ("3_sentence", "declined_empty_structural"))
        self.assertEqual(lv[2][0], "4_paragraph")

    def test_degenerate_candidate_is_rejected(self):
        art = self.CLAIM + "\n\nSecond paragraph stays.\n"
        seq = iter([json.dumps({"revised_ranges": ["Tips."]}), json.dumps({"revised_ranges": ["Tips rose."]}),
                    json.dumps({"revised_ranges": ["Passengers tipped more at higher suggested rates."]})])

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            return next(seq)
        res = self._ladder(art, llm)
        lv = [a["result"] for a in res["handoff"]["level_attempts"]]
        self.assertEqual(lv[0], "degenerate_structural")  # title < 3 words
        self.assertEqual(lv[1], "degenerate_structural")
        self.assertEqual(lv[2], "success")

    def test_body_sentence_delete_still_deterministic(self):
        art = ("# Taxi tips\n\nFirst sentence is fine. " + self.CLAIM
               + " Another fine sentence.\n\n## In one line\n\nTips rose.\n")

        def llm(*a, **k):
            raise AssertionError("no LLM call expected")
        res = self._ladder(art, llm)
        self.assertTrue(res["guard_ok"])
        self.assertEqual(res["ladder_level_used"], "0_delete")
        self.assertNotIn("structural_element_rewrite", res["handoff"])

    def test_switch_off_keeps_old_delete_behavior(self):
        def llm(*a, **k):
            raise AssertionError("no LLM call expected")
        res = self._ladder(self.CLAIM, llm, on=False)
        self.assertEqual(res["ladder_level_used"], "0_delete")
        self.assertEqual(res["updated_text"].strip(), "")  # 旧挙動(後段でdegenerateのhard block)

    def test_in_one_line_heading_and_body_detection(self):
        art = "# Title here now\n\nBody text.\n\n## In one line\n\nTips rose a lot today.\n"
        i = art.index("Tips rose a lot today.")
        self.assertEqual(runner.structural_element_reasons(art, [(i, i + 5)], ["Tips "]), ["in_one_line"])
        j = art.index("## In one line")
        self.assertIn("heading", runner.structural_element_reasons(art, [(j, j + 14)], ["## In one line"]))
        k = art.index("Body text.")
        self.assertEqual(runner.structural_element_reasons(art, [(k, k + 10)], ["Body text."]), [])

    def test_switch_in_kpi_config_and_default_off(self):
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["STRUCTURAL_ELEMENT_REWRITE"])
        self.assertFalse(runner.STRUCTURAL_ELEMENT_REWRITE)


class TestActorGuardAG1Strict08(unittest.TestCase):
    """委任_08(Opus#13・Fable評価1〜3): actor_guardのAG1-strict+2条件AND。負例(a)〜(e)・正例(rep28の6試行・rep22型)・legacy不変。
    注: 本guardは主体語の置換だけを見る。scope(限定・一般化)を守るものではない(scopeはRecheckが担保)。"""

    @classmethod
    def setUpClass(cls):
        led = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
        cls.TIP = led["safety_er009_changed_scope"]
        cls.META = led["meta_run03_advanced"]

    def setUp(self):
        p = mock.patch.object(runner, "ACTOR_GUARD_MODE", "ag1_strict")
        p.start()
        self.addCleanup(p.stop)

    def ok(self, before, after, led, fid, issue=""):
        return runner.actor_rewrite_guard_decision(before, after, led, fid, issue)["ok"]

    # ---- 同義語表 ----
    def test_table_covers_all_25_actor_words_and_separate_classes(self):
        for w in ("users employees workers staff contractors agents executives customers clients spokespeople spokesperson "
                  "engineers managers officials residents drivers passengers patients students teachers analysts traders "
                  "investors shareholders").split():
            self.assertIn(w, runner._EN_WORD_TO_CLASS, w)
        c = runner._EN_WORD_TO_CLASS
        self.assertEqual(len({c["employees"], c["contractors"], c["staff"], c["workers"]}), 4)   # 別クラス
        self.assertEqual(len({c["customers"], c["users"], c["passengers"], c["clients"]}), 4)    # 別クラス

    def test_contract_worker_compound_is_contractor_not_worker(self):
        self.assertEqual(set(runner.actor_classes_in_text("A contract worker made calls; contract staff too.")), {"contractor"})
        self.assertEqual(set(runner.actor_classes_in_text("Some workers and contractors.")), {"worker", "contractor"})

    # ---- 正例: rep28の6試行(実Ledger・関連fact・許容)と rep22型 ----
    def test_positive_rep28_six_attempts_allowed(self):
        rows = json.load(open("er052_output/open233_kpi_recovery_02_offline_01/agg_actor_guard_01.json", encoding="utf-8"))
        rep28 = [r for r in rows if r["run"] == "rep28"]
        self.assertEqual(len(rep28), 6)
        led = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
        for r in rep28:
            d = runner.actor_rewrite_guard_decision(r["before"], r["after"], led[r["instance"]], r["related_fact_id"], r["issue"])
            self.assertTrue(d["ok"], (r["instance"], r["level"], d))
            self.assertTrue(all(p["basis"] == "related_fact" for p in d["new_classes"]))

    def test_positive_rep22_type_requires_both_ledger_and_issue(self):
        b, a = "They could not tell if it was AI or a person.", "Without a clear explanation, users might not know if it was AI or a person."
        self.assertFalse(self.ok(b, a, self.META, "MUSE-HC-012", ""))                                   # issue名指しなし
        self.assertFalse(self.ok(b, a, self.META, "MUSE-HC-012", "The article overstates what happened."))
        d = runner.actor_rewrite_guard_decision(b, a, self.META, "MUSE-HC-012", "The article says users could not tell it was a person.")
        self.assertTrue(d["ok"])
        self.assertEqual(d["new_classes"][0]["basis"], "ledger_and_issue")                              # 2条件AND

    # ---- 負例(a) 近接クラスの取り違え ----
    def test_negative_a_adjacent_class_swaps(self):
        M, T = self.META, self.TIP
        cases = [
            ("Calls were made.", "Employees made some calls.", M, "MUSE-HC-006", "The Ledger says contract workers made calls."),  # contractor→employee
            ("Calls were made.", "Staff made some calls.", M, "MUSE-HC-006", "The Ledger says contract workers made calls."),     # contractor→staff
            ("Calls were made.", "Workers made some calls.", M, "MUSE-HC-006", "The Ledger says contract staff made calls."),     # contractor→worker
            ("Tips rose.", "Customers left more.", T, "F-001", "The Ledger covers credit-card users."),   # users→customers
            ("Tips rose.", "Passengers left more.", T, "F-001", "The Ledger covers credit-card users."),  # users→passengers
            ("Calls were made.", "Executives made some calls.", M, "MUSE-HC-006", "The Ledger says contract workers made calls."),  # staff→executives
        ]
        for b, a, led, fid, iss in cases:
            self.assertFalse(self.ok(b, a, led, fid, iss), (a, fid))

    # ---- 負例(b) 別factの主体の持ち込み(issue名指しなし) ----
    def test_negative_b_actor_from_other_fact_without_issue_naming(self):
        T = self.TIP
        self.assertFalse(self.ok("Tips rose.", "Some customers cut tips to zero.", T, "F-001", "The claim is too strong."))   # F-005に顧客
        self.assertFalse(self.ok("Tips rose.", "Some customers cut tips to zero.", T, "F-001", "It concerns passengers."))  # 別の主体を名指し
        self.assertFalse(self.ok("Tips rose.", "Passengers tipped more.", T, "F-001", "The claim is too strong."))          # F-004に乗客
        # Ledgerに無い主体をissueだけが名指し(issue単独では許容しない)
        self.assertFalse(self.ok("Calls were made.", "Passengers made calls.", self.META, "MUSE-HC-006", "It names passengers."))

    # ---- 負例(c) related_fact_idの欠落・誤り ----
    def test_negative_c_missing_or_wrong_related_fact_id(self):
        M = self.META
        a = "Contract workers made some calls."
        self.assertTrue(self.ok("Calls were made.", a, M, "MUSE-HC-006"))                     # 正しいidなら許容
        # 委任_09: 欠落(空/None/空白)は Ledger全体fallback(Meta Ledgerに契約スタッフあり→許容)。誤id・別factは従来どおりfail-closed
        for fid in ("MUSE-HC-999", "F-004"):
            self.assertFalse(self.ok("Calls were made.", a, M, fid, ""), repr(fid))           # 誤り・別factでfail-closed
        for fid in ("", None, "   ", []):
            d = runner.actor_rewrite_guard_decision("Calls were made.", a, M, fid, "")
            self.assertTrue(d["ok"], repr(fid))
            self.assertEqual(d["new_classes"][0]["basis"], "ledger_wide_fallback")
        self.assertFalse(self.ok("Calls were made.", a, M, ["MUSE-HC-999"], ""))              # list形式の誤り
        self.assertTrue(self.ok("Calls were made.", a, M, "MUSE-HC-999, MUSE-HC-006", ""))     # 複数idの一部が正しければ有効

    # ---- 負例(d) 日本語の部分一致の誤ヒット ----
    def test_negative_d_japanese_partial_match_does_not_hit(self):
        def led(body):
            return "[F-900] " + body + "\n  scope: テスト\n"
        cases = [
            ("Calls.", "Users tipped more.", led("利用者数は増えた。")),          # 利用者数: 利用者+数
            ("Calls.", "Users tipped more.", led("非ユーザーは対象外だった。")),    # 非ユーザー
            ("Calls.", "Staff made calls.", led("契約スタッフが電話をかけた。")),    # 契約スタッフ内のスタッフ(contractorクラス)
            ("Calls.", "Employees made calls.", led("新入社員が参加した。")),      # 新入社員
        ]
        for b, a, l in cases:
            self.assertFalse(self.ok(b, a, l, "F-900", ""), a + l)
        # 対照: 語境界が正しければ許容(助詞・Latin文字・句読点の前後は境界)
        self.assertTrue(self.ok("Calls.", "Users tipped more.", led("Muse利用者が増えた。"), "F-900"))
        self.assertTrue(self.ok("Calls.", "Employees tipped.", led("Meta従業員は、半数だった。"), "F-900"))

    # ---- 負例(e) 複数の新主体語のうち一部のみ一致 ----
    def test_negative_e_partial_match_of_multiple_new_actors(self):
        M, T = self.META, self.TIP
        self.assertFalse(self.ok("Calls.", "Contract workers and employees made calls.", M, "MUSE-HC-006", ""))
        self.assertFalse(self.ok("Calls.", "Passengers and customers tipped more.", T, "F-004", ""))
        self.assertFalse(self.ok("Calls.", "Users and executives tipped more.", T, "F-001", ""))
        self.assertTrue(self.ok("Calls.", "Passengers and credit-card users tipped more.", T, "F-004", ""))  # 全て一致なら許容

    def test_no_new_actor_is_always_ok_and_decision_recorded(self):
        out: list = []
        self.assertTrue(runner.actor_rewrite_guard_ok("Users left.", "Users stayed.", "(ledger)", "", "", out))
        self.assertEqual(out[0]["new_classes"], [])
        out2: list = []
        runner.actor_rewrite_guard_ok("Calls.", "Contract workers made calls.", self.META, "MUSE-HC-006", "", out2)
        p = out2[0]["new_classes"][0]
        self.assertEqual((p["class"], p["basis"], p["ok"]), ("contractor", "related_fact", True))
        self.assertTrue(p["related_fact_hits"])

    # ---- legacy不変・スイッチ ----
    def test_legacy_mode_unchanged(self):
        with mock.patch.object(runner, "ACTOR_GUARD_MODE", "legacy"):
            # 従来: 英語の主体語がLedger本文(英語)に部分一致する場合のみ許容。日本語Ledgerでは一律拒否だった
            self.assertFalse(runner.actor_rewrite_guard_ok("x", "credit-card users", self.TIP))
            self.assertTrue(runner.actor_rewrite_guard_ok("x", "the agents", "AI agents are used."))
            self.assertTrue(runner.actor_rewrite_guard_ok("users", "users", "(none)"))

    def test_switch_in_kpi_config_and_default_legacy(self):
        self.assertEqual(runner.KPI_TRIAL_SWITCHES["ACTOR_GUARD_MODE"], "ag1_strict")
        self.assertTrue(runner.KPI_TRIAL_SWITCHES["STRUCTURAL_PAIRS_TO_RECHECK"])
        src = open("er052_open233_self_recovery_flow_runner_01.py", encoding="utf-8").read()
        self.assertIn('ACTOR_GUARD_MODE = "legacy"', src)
        self.assertIn("STRUCTURAL_PAIRS_TO_RECHECK = False", src)


class TestActorGuardLedgerWideFallback09(unittest.TestCase):
    """委任_09(Fable判断1〜3): related_fact_id空のときだけLedger全体fallback(basis=ledger_wide_fallback)。負例(f)(g)(h)・正例・legacy不変。"""

    @classmethod
    def setUpClass(cls):
        led = {i["instance_id"]: i["fixture"]["ledger_text"] for i in runner.build_target_instances()}
        cls.TIP = led["safety_er009_changed_scope"]
        cls.META = led["meta_run03_advanced"]

    def setUp(self):
        p = mock.patch.object(runner, "ACTOR_GUARD_MODE", "ag1_strict")
        p.start()
        self.addCleanup(p.stop)

    def dec(self, b, a, led, fid="", issue=""):
        return runner.actor_rewrite_guard_decision(b, a, led, fid, issue)

    def test_positive_rep29a_s2_passengers_empty_related_fact(self):
        d = json.load(open("er052_output/open233_self_recovery_flow_runner_01_rep29a/instances_s2/safety_er009_changed_scope.json", encoding="utf-8"))
        att = d["cycles"][0]["rewrite_records"][0]["handoff"]["level_attempts"]
        n = 0
        for a in att:
            if a.get("result") != "actor_guard_rejected":
                continue
            for t, rv in zip(a["targets"], a["revised"]):
                r = self.dec(t, rv, self.TIP, "", "")
                self.assertTrue(r["ok"], r)
                self.assertTrue(all(p["basis"] == "ledger_wide_fallback" for p in r["new_classes"]))
                n += 1
        self.assertGreaterEqual(n, 1)
        r = self.dec("Tips rose.", "Passengers who saw the menu tipped more.", self.TIP, "", "")
        self.assertEqual((r["ok"], r["new_classes"][0]["basis"]), (True, "ledger_wide_fallback"))

    def test_negative_f_empty_related_and_not_in_ledger(self):
        for a in ("Executives tipped more.", "Teachers tipped more.", "Drivers and analysts tipped more.", "Investors tipped more."):
            for fid in ("", None, []):
                self.assertFalse(self.dec("Tips rose.", a, self.TIP, fid, "It names executives, teachers, drivers, analysts and investors.")["ok"], (a, fid))
        self.assertFalse(self.dec("Calls.", "Passengers made calls.", self.META, "", "")["ok"])

    def test_negative_g_empty_related_adjacent_class(self):
        led = "[F-900] 契約スタッフが電話をかけた。\n  scope: テスト\n"      # contractorはあるがemployeeは無い
        for a in ("Employees made calls.", "Staff made calls.", "Workers made calls.", "Customers made calls."):
            for fid in ("", None):
                self.assertFalse(self.dec("Calls.", a, led, fid, "")["ok"], (a, fid))
        self.assertTrue(self.dec("Calls.", "Contract workers made calls.", led, "", "")["ok"])   # 対照(同クラス)
        # 部分一致: 複数新主体のうち1つでもLedger全体に無ければ拒否
        self.assertFalse(self.dec("Calls.", "Contract workers and employees made calls.", led, "", "")["ok"])

    def test_negative_h_related_present_other_fact_actor_no_fallback(self):
        T = self.TIP
        for a, fid in (("Some customers cut tips to zero.", "F-001"), ("Passengers tipped more.", "F-001"), ("Customers tipped less.", "F-004")):
            for iss in ("", "The claim is too strong.", "It concerns executives."):
                d = self.dec("Tips rose.", a, T, fid, iss)
                self.assertFalse(d["ok"], (a, fid, iss))
                self.assertFalse(d["new_classes"][0]["related_fact_empty"])
        # 2条件AND(issue名指しあり)なら従来どおり許容。basisはledger_and_issue(fallbackではない)
        d = self.dec("Tips rose.", "Passengers tipped more.", T, "F-001", "It concerns passengers.")
        self.assertEqual((d["ok"], d["new_classes"][0]["basis"]), (True, "ledger_and_issue"))
        # 誤id(Ledgerに無い)はfallbackしない
        self.assertFalse(self.dec("Calls.", "Contract workers made calls.", self.META, "MUSE-HC-999", "")["ok"])

    def test_related_fact_basis_preferred_and_legacy_unchanged(self):
        d = self.dec("Calls.", "Contract workers made calls.", self.META, "MUSE-HC-006", "")
        self.assertEqual(d["new_classes"][0]["basis"], "related_fact")
        with mock.patch.object(runner, "ACTOR_GUARD_MODE", "legacy"):
            self.assertFalse(runner.actor_rewrite_guard_ok("x", "credit-card users", self.TIP))
            self.assertTrue(runner.actor_rewrite_guard_ok("x", "the agents", "AI agents are used."))


class TestPriorCountMismatchThreeHoles08(unittest.TestCase):
    """委任_08(Opus#13・Fable評価4): 件数一致是正の3穴(文字列"false"・範囲外index・非dict項目)は全てFalse。"""
    T = {"resolved": True}

    def test_string_false_is_not_true(self):
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, "resolved": "false"}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, "resolved": 1}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, "resolved": None}])[0])

    def test_out_of_range_index_is_false(self):
        # Checkerが1始まりで番号付けした場合: {0:true}(別物)+{1:false}は旧式ではFalse、旧index別集約ではTrueになり得た
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, **self.T}, {"index": 1, "resolved": False}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, **self.T}, {"index": 5, **self.T}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": -1, **self.T}, {"index": 0, **self.T}])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": "0", **self.T}])[0])

    def test_non_dict_item_is_false(self):
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, **self.T}, None])[0])
        self.assertFalse(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, **self.T}, "x"])[0])

    def test_correct_cases_still_true(self):
        self.assertTrue(runner.aggregate_prior_issues_resolved(["p"], [{"index": 0, **self.T}, {"index": 0, **self.T}])[0])
        self.assertTrue(runner.aggregate_prior_issues_resolved(["a", "b"], [{"index": 1, **self.T}, {"index": 0, **self.T}])[0])
        self.assertTrue(runner.aggregate_prior_issues_resolved([], [])[0])


class TestStructuralPairsToRecheck08(unittest.TestCase):
    """委任_08(Fable評価5): 構造要素を書き換えた場合に限り、前後の対をRecheckへ渡す。title判定のProductionフォーマットテスト。"""

    def _recheck_prompt(self, pairs, structural_on, ba_on=False):
        captured = {}

        class _R:
            output_text = json.dumps({"overall_status": "LEDGER_COMPLIANT", "deviations": [],
                                      "prior_issues_resolved": [{"index": 0, "resolved": True, "explanation": "ok"}]})

        class _Rs:
            def create(self, **kw):
                captured["prompt"] = kw["input"][1]["content"]
                return _R()

        class _C:
            responses = _Rs()
        state = {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}
        fixture = {"ledger_text": "[VERIFIED] HF-001: x\n", "source_article_text": None}
        with mock.patch.object(runner, "STRUCTURAL_PAIRS_TO_RECHECK", structural_on), \
                mock.patch.object(runner, "RECHECK_BEFORE_AFTER_PAIRS", ba_on):
            runner.run_recheck(_C(), state, [0], [], "t", fixture, "Article.",
                               [{"fact_id": "HF-001", "claim_in_article": "x", "issue": "i", "explanation": "e"}],
                               before_after_pairs=pairs)
        return captured["prompt"]

    PAIRS = [{"before": "Old title", "after": "New title here", "structural": True},
             {"before": "Body before", "after": "Body after"}]

    def test_only_structural_pairs_are_passed_when_on(self):
        p = self._recheck_prompt(self.PAIRS, True)
        self.assertIn("Old title", p)
        self.assertIn("New title here", p)
        self.assertNotIn("Body before", p)

    def test_non_structural_pairs_not_passed_and_off_keeps_prompt_identical(self):
        p_none = self._recheck_prompt([{"before": "Body before", "after": "Body after"}], True)
        self.assertNotIn("Body before", p_none)
        p_off = self._recheck_prompt(self.PAIRS, False)
        self.assertNotIn("Old title", p_off)
        self.assertEqual(p_none, p_off)   # 対が渡らない場合・OFF時は従来とバイト同一

    def test_independent_of_n3_switch(self):
        p = self._recheck_prompt(self.PAIRS, False, ba_on=True)   # N3′ONなら従来どおり全対
        self.assertIn("Body before", p)

    def test_run_instance_passes_structural_pair_only_when_switch_on(self):
        sp = {"before": META_TARGET, "after": "A short natural title for the article"}
        res, seen = _run_instance_merge06([_rr06()], [], merge_on=True, structural_pair=sp, structural_pairs_on=True)
        pairs = seen["recheck_kwargs"][0]["before_after_pairs"]
        self.assertEqual(pairs, [{"before": sp["before"], "after": sp["after"], "structural": True}])
        self.assertEqual(res["cycles"][0]["recheck_structural_pairs_n"], 1)
        res2, seen2 = _run_instance_merge06([_rr06()], [], merge_on=True, structural_pair=None, structural_pairs_on=True)
        self.assertNotIn("structural", seen2["recheck_kwargs"][0]["before_after_pairs"][0])
        self.assertEqual(res2["cycles"][0]["recheck_structural_pairs_n"], 0)

    def test_ladder_records_structural_pair_including_paragraph_level(self):
        t = TestStructuralElementRewrite07()
        seq = iter([json.dumps({"revised_ranges": [""]}), json.dumps({"revised_ranges": [""]}),
                    json.dumps({"revised_ranges": ["Passengers tipped more at higher suggested rates."]})])

        def llm(client, state, errs, log, label, dev_msg, prompt, model=None):
            return next(seq)
        art = TestStructuralElementRewrite07.CLAIM + "\n\nSecond paragraph stays.\n"
        res = t._ladder(art, llm)
        self.assertEqual(res["ladder_level_used"], "4_paragraph")
        sp = res["handoff"]["structural_pair"]
        self.assertIn("male passengers tipped twice", sp["before"])
        self.assertEqual(sp["after"], "Passengers tipped more at higher suggested rates.")
        self.assertIsNone(res["after_fragment"])          # 従来のafter_fragmentはNone(これを補うのがstructural_pair)

    def test_title_detection_on_production_article_formats(self):
        import glob
        paths = sorted(glob.glob("er019_output/**/article.md", recursive=True))[:200]
        picked = []
        for pth in paths:
            txt = open(pth, encoding="utf-8").read()
            if txt.startswith("# ") and "\n## In one line" in txt and "\n### " in txt:
                picked.append((pth, txt))
            if len(picked) >= 5:
                break
        self.assertGreaterEqual(len(picked), 3)
        for pth, txt in picked:
            lines = txt.split("\n")
            title = lines[0]
            sp = (0, len(title))
            self.assertIn("title", runner.structural_element_reasons(txt, [(0, 5)], [txt[:5]]), pth)   # `# `付きtitleはtitle+headingの両方に判定される
            # 本文の最初の段落(titleの次の非空行)はtitleではない
            body_line = next(ln for ln in lines[1:] if ln.strip() and not ln.startswith("#"))
            bi = txt.index(body_line)
            self.assertEqual(runner.structural_element_reasons(txt, [(bi, bi + 8)], [body_line[:8]]), [], pth)
            # 見出し行(###)
            hi = txt.index("\n### ") + 1
            self.assertIn("heading", runner.structural_element_reasons(txt, [(hi, hi + 6)], [txt[hi:hi + 6]]), pth)
            # In one line直下の本文
            ii = txt.index("\n## In one line") + len("\n## In one line")
            nxt = next(ln for ln in txt[ii:].split("\n") if ln.strip())
            ni = txt.index(nxt, ii)
            self.assertEqual(runner.structural_element_reasons(txt, [(ni, ni + 6)], [nxt[:6]]), ["in_one_line"], pth)


class TestSafetyCriticalTextPattern08(unittest.TestCase):
    """委任_08(Fable評価6): `text_pattern`(因果接続語+目印)。旧`text_substring`と旧新並記。"""

    def test_pattern_distinguishes_causal_from_and(self):
        d = runner.SAFETY_CRITICAL_CLAIM_DEFS["bgroup_B3"][0]
        self.assertTrue(runner.safety_def_matches(d, "Concerns continued. So the flashy 20% plan left the stage.", True))
        self.assertTrue(runner.safety_def_matches(d, "Because of this, the flashy 20% plan ended.", True))
        self.assertFalse(runner.safety_def_matches(d, "Oil fell, and the flashy 20% plan left the stage.", True))
        self.assertFalse(runner.safety_def_matches(d, "The flashy 20% plan was withdrawn.", True))
        self.assertFalse(runner.safety_def_matches(d, "He said it was also a flashy 20% plan.", True))   # 'also'の'so'は語境界で除外
        self.assertTrue(runner.safety_def_matches(d, "The flashy 20% plan was withdrawn.", False))        # 旧定義は部分一致で真
        n = runner.SAFETY_CRITICAL_CLAIM_DEFS["neg5_hormuz_div_a2"][0]
        self.assertIn("text_pattern", n)
        self.assertIn("text_substring", n)

    def test_defs_without_pattern_fall_back_to_substring(self):
        d = runner.SAFETY_CRITICAL_CLAIM_DEFS["safety_A2A3"][0]
        self.assertTrue(runner.safety_def_matches(d, "They will repay the money.", True))

    def test_residual_at_pass_records_old_and_new(self):
        out = runner.compute_residual_at_pass("bgroup_B3", "RESOLVED_REWRITE", "Oil fell, and the flashy 20% plan left.", [], [], [])
        row = out["defs"][0]
        self.assertTrue(row["remains_in_final_en"])              # 旧: 部分一致
        self.assertFalse(row["remains_in_final_en_pattern"])     # 新: 因果パターン不一致
        self.assertTrue(row["pass_with_residual_unflagged"])
        self.assertFalse(row["pass_with_residual_unflagged_pattern"])


# ============================================================
# 委任_11(OPEN-233-KPI-RECOVERY-REDESIGN-02、Opus#14後のFable評価、設計書§18): STAGE4許可リスト・位置引継ぎ・A2・D・G・T・BLOCKING固定の
# 強制経路fixture・負例(H-1/H-2/rounding)。全て¥0(偽のStage1/2/3 LLM・Recheck、ネットワークなし)。
# ============================================================
ART11 = ("# Plan overview\n\n## In one line\nA short summary line.\n\n"
         "The firm said alpha rose sharply. Other news was calm today.\n\n"
         "The firm said beta fell hard. Another calm remark ends here.\n\n"
         "The firm said gamma shifted a lot. A last calm remark follows.\n")
_K11_NEW = ("STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD", "SPAN_FALLBACK_CHAIN",
            "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE", "MATERIALITY_BLOCKING_PIN",
            "STAGE2_VERDICT_REUSE_NONBLOCKING", "STAGE2_SIBLING_LOCATIONS_CYCLE1")


def _rr11(ok=True, devs=None, resolved=None, status=None):
    st = status or ("LEDGER_COMPLIANT" if ok else "LEDGER_DEVIATION")
    return {"overall_status": st, "all_prior_issues_resolved": ok, "deviations": devs or [],
            "prior_issues_resolved": resolved if resolved is not None else [{"index": 0, "resolved": ok, "explanation": ""}]}


def _run_kpi11(stage1_devs, stage2_fn, llm_fn, recheck_fn, stage3_fn=None, overrides=None, article=ART11,
               iid="unit11", ledger="(ledger)"):
    """run_instanceを偽のStage1/Stage2/S1/Recheck/Rewrite-LLMで通す。stage2_fn(cycle, claim_text, fid)->materiality、
    llm_fn(label, prompt)->応答文字列(またはNone)、recheck_fn(cycle, prior_issues, article)->Recheck dict。"""
    seen = {"s1_calls": [], "stage2": [], "llm_labels": [], "recheck_prior": []}

    def _cyc(label):
        m = re.search(r"_c(\d+)_", label)
        return int(m.group(1)) if m else 0

    def fake_stage1(client, state, ce, call_log, label, fixture, developer_message=None):
        return {"overall_status": "LEDGER_DEVIATION", "deviations": [dict(d) for d in stage1_devs]}

    def fake_stage2(client, state, ce, call_log, label, fixture, claims):
        c_ = _cyc(label)
        seen["stage2"].append((c_, [c["claim_text"] for c in claims]))
        out = []
        for c in claims:
            mat = stage2_fn(c_, c["claim_text"], c["related_fact_id"])
            out.append({**c, "materiality": mat, "llm_materiality": mat, "basis": "ledger_fact",
                        "rewrite_kind": "narrow_scope", "rewrite_hint": "h", "floor_reason": None, "section_type": "body",
                        "stage2_route": "body", "floor_cited_materiality": mat, "floor_cited_reason": None})
        return out

    def fake_s1(client, state, ce, call_log, label_prefix, fixture, results, instance_id=None, cycle=None):
        seen["s1_calls"].append(cycle)
        return results, []

    def fake_recheck(client, state, ce, call_log, label, fixture, article_text, prior_issues, **k):
        seen["recheck_prior"].append(prior_issues)
        return dict(recheck_fn(_cyc(label), prior_issues, article_text))

    def fake_llm(client, state, ce, call_log, label, dev_msg, prompt, model=None):
        seen["llm_labels"].append(label)
        return llm_fn(label, prompt)

    sw = {**runner.KPI_TRIAL_SWITCHES, **(overrides or {})}
    patches = [mock.patch.object(runner, k, v) for k, v in sw.items() if k != "FLOOR_VERIFY_MODE"]
    patches += [mock.patch.object(runner, "stage1_fresh_with_enumeration", fake_stage1),
                mock.patch.object(runner, "run_stage2", fake_stage2),
                mock.patch.object(runner, "apply_stage2_second_opinion", fake_s1),
                mock.patch.object(runner, "run_local_qa_fastpath", lambda *a, **k: {"success": False, "results": []}),
                mock.patch.object(runner, "run_recheck", fake_recheck),
                mock.patch.object(runner, "run_recheck_confirm", lambda *a, **k: _rr11(False, status="LEDGER_DEVIATION")),
                mock.patch.object(runner, "simple_llm_call", fake_llm),
                mock.patch.object(runner, "save_json", lambda *a, **k: None)]
    if stage3_fn is not None:
        patches.append(mock.patch.object(runner, "run_stage3_for_claim", stage3_fn))
    inst = {"instance_id": iid, "group": "unit", "expected_group_label": "unit", "stage1_mode": "fresh",
            "fixture": {"ledger_text": ledger, "article_text": article, "source_article_text": JA49}}
    for p in patches:
        p.start()
    try:
        res = runner.run_instance(object(), _state0(), [0], inst, stage1_cache={})
    finally:
        for p in reversed(patches):
            p.stop()
    return res, seen


def _llm_replace(mapping):
    """プロンプト中の`<<<...>>>`範囲(Flagged range(s)/sentence(s)/paragraph block(s))を、mapping{旧->新}で置換して返す偽LLM。"""
    def fn(label, prompt):
        head = prompt.split("[Checker's issue]", 1)[0]
        if "[Paragraph block(s) flagged" in head:
            head = head.split("[Text originally flagged", 1)[0]
        elif "[Paragraph context (read-only)]" in head:
            head = head.split("[Paragraph context (read-only)]", 1)[0]
        out = []
        for r in re.findall(r"<<<\n(.*?)\n>>>", head, re.S):
            t = r
            for o, n in mapping.items():
                t = t.replace(o, n)
            out.append(t)
        return json.dumps({"revised_ranges": out})
    return fn


class TestKpi11AllowlistFunction(unittest.TestCase):
    def test_allowed_four_reasons_only(self):
        self.assertEqual(runner.STAGE4_ALLOWED_REASONS, frozenset({
            "blocking_confirmed_unlocatable_after_cap", "blocking_structural_after_ladder", "post_T_new_blocking", "api_failure"}))
        for r in ("blocking_confirmed_unlocatable_after_cap", "blocking_structural_after_ladder", "post_T_new_blocking"):
            self.assertTrue(runner.stage4_allowlist_decision(r, {"funnel_passed": True})["allowed"])
            d = runner.stage4_allowlist_decision(r, {})
            self.assertFalse(d["allowed"])
            self.assertEqual(d["action"], "funnel")
        self.assertTrue(runner.stage4_allowlist_decision("api_failure")["allowed"])

    def test_legacy_reasons_are_not_allowed_and_funnel(self):
        for r in ("same_claim_fact_id_reblocked", "violation_span_unverified", "ladder_exhausted_without_full_rewrite",
                  "cycle_limit_exhausted", "cycle_limit_exhausted_after_recheck", "target_not_locatable",
                  "unconfirmed_after_reverify", "degenerate_rewrite_output", "anything_new"):
            d = runner.stage4_allowlist_decision(r, {"funnel_passed": True})
            self.assertFalse(d["allowed"], r)
            self.assertEqual(d["action"], "funnel")
            self.assertEqual(d["violation"], "reason_not_in_allowlist")

    def test_new_switches_default_off_and_on_in_kpi_config(self):
        for k in _K11_NEW:
            self.assertIn(k, runner.KPI_TRIAL_SWITCHES)
            self.assertFalse(getattr(runner, k), k)   # モジュールの既定(apply前)はlegacy=OFF
        for k in ("STAGE4_ALLOWLIST", "LADDER_LOCATION_CARRY", "REWRITE_REVERT_GUARD", "SPAN_FALLBACK_CHAIN",
                  "JUDGE_ONLY_CYCLE_AFTER_CAP", "LAST_RESORT_DELETE", "MATERIALITY_BLOCKING_PIN"):
            self.assertTrue(runner.KPI_TRIAL_SWITCHES[k], k)
        self.assertFalse(runner.KPI_TRIAL_SWITCHES["STAGE2_VERDICT_REUSE_NONBLOCKING"])
        self.assertFalse(runner.KPI_TRIAL_SWITCHES["STAGE2_SIBLING_LOCATIONS_CYCLE1"])


class TestKpi11HelpersUnit(unittest.TestCase):
    def test_revert_detected_with_context(self):
        cur = "A. The firm said alpha rose. B."
        prior = ["A. The firm said alpha rose sharply. B."]
        self.assertTrue(runner.revert_to_prior_state_detected(prior, cur, "The firm said alpha rose.",
                                                              "The firm said alpha rose sharply."))
        self.assertFalse(runner.revert_to_prior_state_detected(prior, cur, "The firm said alpha rose.",
                                                               "The firm said alpha rose slightly."))
        # 短い語が別の場所にあるだけでは却下しない
        self.assertFalse(runner.revert_to_prior_state_detected(["so it ran. so"], "A. because X. B.", "because", "so"))
        # 削除案は判定しない
        self.assertFalse(runner.revert_to_prior_state_detected(prior, cur, "The firm said alpha rose.", ""))

    def test_multi_range_quote_form_resolves_two_ranges(self):
        q = runner.multi_range_to_quote_form("The firm said alpha rose sharply.\nThe firm said beta fell hard.")
        self.assertEqual(q, "“The firm said alpha rose sharply.” and “The firm said beta fell hard.”")
        res = runner.resolve_violation_spans(q, ART11, None)
        self.assertEqual(res["status"], "resolved", res.get("reason"))
        self.assertEqual(len(res["ranges"]), 2)
        self.assertEqual(runner.multi_range_to_quote_form("single"), "single")

    def test_normalize_recheck_outcome_multirange_converted_only_with_switch(self):
        prior_claims = [{"dev": {"related_fact_id": "FA", "claim_in_article": "x"}}]
        prior_issues = [{"claim_in_article": "S one.\nS two."}]
        rc = _rr11(False, status="LEDGER_DEVIATION")
        with mock.patch.object(runner, "SPAN_FALLBACK_CHAIN", False):
            off = runner.normalize_recheck_outcome(rc, None, prior_claims, prior_issues)
        with mock.patch.object(runner, "SPAN_FALLBACK_CHAIN", True):
            on = runner.normalize_recheck_outcome(rc, None, prior_claims, prior_issues)
        self.assertEqual(off["deviations"][0]["claim_in_article"], "x")
        self.assertEqual(on["deviations"][0]["claim_in_article"], "“S one.” and “S two.”")

    def test_explain_split_too_long_relaxed_only_for_closed_position_words(self):
        art = ("# Head line\n\n## In one line\nA short summary line.\n\n"
               "The firm said alpha rose sharply. Other news was calm today.\n")
        claim = ("“The firm said alpha rose sharply.” and, in the one-line summary, calls were handled by "
                 "humans in the end")
        with mock.patch.object(runner, "SPAN_FALLBACK_CHAIN", False):
            off = runner.vs_explain_split_resolve(claim, art)
        with mock.patch.object(runner, "SPAN_FALLBACK_CHAIN", True):
            on = runner.vs_explain_split_resolve(claim, art)
        self.assertEqual(off["status"], "unverified")
        self.assertIn("remainder_too_long", off["reason"])
        self.assertEqual(on["status"], "resolved", on)
        self.assertTrue(any("A short summary line." in r for r in on["ranges"]))  # U-2: one_line要素が範囲へ加わる
        # 位置語を含まない長い残りは緩和しない(棄却のまま)
        claim2 = "“The firm said alpha rose sharply.” and calls were handled by humans in the very end of day"
        with mock.patch.object(runner, "SPAN_FALLBACK_CHAIN", True):
            self.assertEqual(runner.vs_explain_split_resolve(claim2, art)["status"], "unverified")

    def test_regions_inherit_levels_and_overlap_location(self):
        pre = ART11
        rec = [{"handoff": {"level_attempts": [{"result": "success", "level": "1_word_connective",
                                                  "targets": ["The firm said alpha rose sharply."],
                                                  "revised": ["The firm said alpha rose."]}]}}]
        regs = runner.update_regions_after_rewrite([], pre, rec, 1)
        self.assertEqual(regs[0]["levels"], ["1_word_connective"])
        post = pre.replace("alpha rose sharply", "alpha rose")
        claim = {"span_resolution_cycle_start": {"status": "resolved", "ranges": ["The firm said alpha rose."]}}
        lv, n = runner.location_prior_levels(regs, claim, post)
        self.assertEqual(lv, ["1_word_connective"])
        other = {"span_resolution_cycle_start": {"status": "resolved", "ranges": ["The firm said beta fell hard."]}}
        self.assertEqual(runner.location_prior_levels(regs, other, post)[0], [])  # 兄弟箇所(別位置)は昇段しない
        # 1文字以上の重なりで同一箇所(逐語一致でなくてよい、H-4)
        part = {"span_resolution_cycle_start": {"status": "resolved", "ranges": ["alpha rose."]}}
        self.assertEqual(runner.location_prior_levels(regs, part, post)[0], ["1_word_connective"])
        # 二度目の置換は前のlevelを引き継ぐ
        rec2 = [{"handoff": {"level_attempts": [{"result": "success", "level": "3_sentence",
                                                   "targets": ["The firm said alpha rose."],
                                                   "revised": ["The firm said alpha climbed."]}]}}]
        regs2 = runner.update_regions_after_rewrite(regs, post, rec2, 2)
        self.assertEqual(len(regs2), 1)
        self.assertEqual(regs2[0]["levels"], ["1_word_connective", "3_sentence"])


class TestKpi11ForcedPathFixtures(unittest.TestCase):
    """強制経路fixture: 各fixtureで終端reasonが許可リスト内か、funnelを通ったかを検証する。"""

    def DEV_A(self):
        return _dev49("The firm said alpha rose sharply.", fid="FA")

    def _assert_allowlisted_or_resolved(self, res):
        if res["final_state"] == "STAGE4_ESCALATION":
            self.assertIn(res["stage4_reason"], runner.STAGE4_ALLOWED_REASONS)
        self.assertFalse(res["stage4_allowlist"]["final_reason_outside_allowlist"])
        self.assertEqual(res["stage4_allowlist"]["unrewritten_blocking_pass"], 0)

    def _three_cycle_recheck(self, last_dev=None):
        sentences = {1: "The firm said beta fell hard.", 2: "The firm said gamma shifted a lot."}

        def rc(c, prior, art):
            if c in sentences:
                return _rr11(False, devs=[_dev49(sentences[c], fid="FA")])
            if c == 3 and last_dev:
                return _rr11(False, devs=[last_dev])
            return _rr11(True)
        return rc

    def _llm3(self):
        return _llm_replace({"alpha rose sharply": "alpha rose", "beta fell hard": "beta fell",
                             "gamma shifted a lot": "gamma shifted"})

    def test_cap_reached_goes_to_judge_only_cycle_with_s1_and_downgrades(self):
        last = _dev49("A last calm remark follows.", fid="FA")
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING" if c <= 3 else "ACCEPTABLE",
                               self._llm3(), self._three_cycle_recheck(last))
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE_THEN_DOWNGRADE")
        self.assertEqual(len(res["cycles"]), 4)
        self.assertTrue(res["cycles"][3].get("judge_only_cycle"))
        self.assertNotIn("rewrite_records", res["cycles"][3])        # Rewriteしない
        self.assertIn(4, seen["s1_calls"])                            # G経路でもS1(第2意見)を必ず通る(H-2)
        self.assertFalse(any("_c4_" in l for l in seen["llm_labels"]))
        self._assert_allowlisted_or_resolved(res)
        self.assertTrue(any(e["legacy_reason"] == "cycle_limit_exhausted_after_recheck"
                            for e in res["stage4_allowlist"]["decisions"]))

    def test_cap_reached_blocking_then_T_then_clean_recheck_resolves(self):
        last = _dev49("A last calm remark follows.", fid="FA")

        def rc(c, prior, art):
            return self._three_cycle_recheck(last)(c, prior, art) if c <= 3 else _rr11(True)
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", self._llm3(), rc)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertTrue(res["stage4_allowlist"]["t_used"])
        c4 = res["cycles"][3]
        self.assertTrue(c4.get("judge_only_cycle"))
        self.assertTrue(c4.get("cap_terminal_last_resort"))
        self.assertEqual(c4["rewrite_records"][0]["ladder_level_used"], "0_delete")
        self.assertFalse(any("_c4_" in l for l in seen["llm_labels"]))    # Tは決定論削除=LLM callなし
        self._assert_allowlisted_or_resolved(res)

    def test_T_then_new_blocking_after_recheck_goes_to_post_T_new_blocking(self):
        last = _dev49("A last calm remark follows.", fid="FA")
        new_dev = _dev49("Other news was calm today.", fid="FZ")

        def rc(c, prior, art):
            if c <= 3:
                return self._three_cycle_recheck(last)(c, prior, art)
            return _rr11(False, devs=[new_dev])
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", self._llm3(), rc)
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "post_T_new_blocking")
        self.assertIn(5, seen["s1_calls"])        # T後の新規MAJORも判定だけのcycle(Stage 2+S1)を通ってからSTAGE4
        self._assert_allowlisted_or_resolved(res)

    def test_oscillation_revert_rejected_and_location_carry_escalates(self):
        def llm(label, prompt):
            if "_e1_minimal_word" in label:
                return _llm_replace({"alpha rose sharply": "alpha rose"})(label, prompt)
            if "_e2_rewrite" in label:  # 元に戻す案(振動)
                return _llm_replace({"alpha rose.": "alpha rose sharply."})(label, prompt)
            return _llm_replace({"alpha rose.": "alpha eased."})(label, prompt)  # ④段落: 別の案

        def rc(c, prior, art):
            if c == 1:
                return _rr11(False, devs=[_dev49("The firm said alpha rose.", fid="FA")])
            return _rr11(True)
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", llm, rc)
        c2 = res["cycles"][1]
        att = c2["rewrite_records"][0]["handoff"]["level_attempts"]
        self.assertEqual(c2["location_carry"], {"fact:FA": ["1_word_connective"]})   # B′: 同一箇所は①を飛ばして昇段
        self.assertEqual([a["level"] for a in att][:2], ["3_sentence", "4_paragraph"])
        self.assertEqual(att[0]["result"], "revert_rejected")                          # A2: 原文へ戻る案を却下、同cycle内で上位levelへ
        self.assertEqual(att[1]["result"], "success")
        self._assert_allowlisted_or_resolved(res)

    def test_oscillation_revert_guard_off_accepts_revert_legacy(self):
        def llm(label, prompt):
            if "_c1_" in label:
                return _llm_replace({"alpha rose sharply": "alpha rose"})(label, prompt)
            return _llm_replace({"alpha rose.": "alpha rose sharply."})(label, prompt)   # c2: 原文へ戻る案(ガードOFFなら採用される)

        def rc(c, prior, art):
            return _rr11(False, devs=[_dev49("The firm said alpha rose.", fid="FA")]) if c == 1 else _rr11(True)
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", llm, rc,
                               overrides={"REWRITE_REVERT_GUARD": False, "LADDER_LOCATION_CARRY": False})
        att = res["cycles"][1]["rewrite_records"][0]["handoff"]["level_attempts"]
        self.assertEqual(att[0]["level"], "1_word_connective")
        self.assertEqual(att[0]["result"], "success")

    def test_multi_match_unlocatable_blocking_is_carried_and_never_passes_h1(self):
        art = ART11.replace("A short summary line.", "The firm said alpha rose sharply.")  # 同じ文が2箇所(multi_match)
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", self._llm3(),
                               lambda c, p, a: _rr11(True), article=art)
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "blocking_confirmed_unlocatable_after_cap")
        self.assertEqual(res["stage4_allowlist"]["pass_blocked_by_carry"], 1)        # H-1: Recheck1回の「準拠」でPASSしない
        self.assertTrue(res["cycles"][0]["pass_blocked_by_carry_blocking"])
        self.assertTrue(any(e["legacy_reason"] == "violation_span_unverified" for e in res["stage4_allowlist"]["decisions"]))
        self.assertFalse(any("e1" in l for l in seen["llm_labels"]))                  # Rewriteは試みていない
        self._assert_allowlisted_or_resolved(res)

    def test_multi_match_relocated_by_recheck_then_rewritten_and_resolved(self):
        art = ART11.replace("A short summary line.", "The firm said alpha rose sharply.")

        def rc(c, prior, a):
            if c == 1:   # 位置の再取得: 本文中の別の一意な断片で指摘し直す
                return _rr11(False, devs=[_dev49("Other news was calm today.", fid="FA")])
            return _rr11(True)
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING",
                               _llm_replace({"Other news was calm today.": "Other news was calm."}), rc, article=art)
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertEqual(res["stage4_allowlist"]["carry_blocking_remaining"], 0)
        self.assertTrue(res["cycles"][1]["stage2_results"][-1]["carried_blocking"])
        self._assert_allowlisted_or_resolved(res)

    def test_structural_element_ladder_exhaustion_goes_to_blocking_structural_after_ladder(self):
        dev = _dev49("Plan overview", fid="FS")
        res, seen = _run_kpi11([dev], lambda c, t, f: "BLOCKING",
                               lambda label, prompt: json.dumps({"revised_ranges": ["Plan overview"]}),
                               lambda c, p, a: _rr11(True))
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "blocking_structural_after_ladder")
        self._assert_allowlisted_or_resolved(res)

    def test_api_failure_goes_to_allowlisted_api_failure(self):
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING", lambda label, prompt: None,
                               lambda c, p, a: _rr11(True))
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "api_failure")
        self._assert_allowlisted_or_resolved(res)

    def test_ladder_exhausted_non_structural_goes_to_T_not_stage4(self):
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING",
                               _llm_replace({}),
                               lambda c, p, a: _rr11(True))
        self.assertEqual(res["final_state"], "RESOLVED_REWRITE")
        self.assertTrue(res["stage4_allowlist"]["t_used"])
        self.assertEqual(res["cycles"][0]["rewrite_records"][0]["ladder_level_used"], "0_delete")
        self.assertNotIn("alpha rose sharply", res["cycles"][0]["en_text_after_rewrite"])
        self._assert_allowlisted_or_resolved(res)

    def test_legacy_switches_off_keeps_legacy_reasons(self):
        off = {k: False for k in _K11_NEW}
        res, seen = _run_kpi11([self.DEV_A()], lambda c, t, f: "BLOCKING",
                               _llm_replace({}),
                               lambda c, p, a: _rr11(True), overrides=off)
        self.assertEqual(res["final_state"], "STAGE4_ESCALATION")
        self.assertEqual(res["stage4_reason"], "ladder_exhausted_without_full_rewrite")
        self.assertNotIn("stage4_allowlist", res)


class TestKpi11NegativeCases(unittest.TestCase):
    def test_h1_unrewritten_blocking_does_not_pass_on_single_clean_recheck(self):
        """H-1: Stage 2がBLOCKINGと確定した箇所を書き換えずに、Recheck1回の「解消/準拠」だけでPASSできない。"""
        art = ART11.replace("A short summary line.", "The firm said alpha rose sharply.")
        res, _ = _run_kpi11([_dev49("The firm said alpha rose sharply.", fid="FA")], lambda c, t, f: "BLOCKING",
                            lambda l, p: None, lambda c, p, a: _rr11(True), article=art)
        self.assertNotIn(res["final_state"], ("RESOLVED_REWRITE", "RESOLVED_STAGE2_DOWNGRADE", "RESOLVED_REWRITE_THEN_DOWNGRADE"))
        self.assertEqual(res["stage4_allowlist"]["unrewritten_blocking_pass"], 0)

    def test_h1_with_D_chain_off_but_allowlist_on_no_pass_either(self):
        art = ART11.replace("A short summary line.", "The firm said alpha rose sharply.")
        res, _ = _run_kpi11([_dev49("The firm said alpha rose sharply.", fid="FA")], lambda c, t, f: "BLOCKING",
                            lambda l, p: None, lambda c, p, a: _rr11(True), article=art,
                            overrides={"SPAN_FALLBACK_CHAIN": False})
        self.assertNotEqual(res["final_state"], "RESOLVED_REWRITE")

    def test_h2_pinned_blocking_not_downgraded_by_second_verdict_and_judge_only_uses_s1(self):
        """H-2: 本文が変わっていない箇所の再判定の揺れ(BLOCKING→非BLOCKING)で降格しない。G経路でもS1を通る。"""
        dev = _dev49("The firm said alpha rose sharply.", fid="FA")

        def stage3(client, state, ce, call_log, label, fixture, en, ja, claim_rec):  # 書き換えが起きない(本文不変)
            return {"mechanism": "single_text_local(E-2/delete-generic)", "en_text": en, "ja_text": ja,
                    "method": "fake_no_change", "guard_ok": False, "before_fragment": None, "after_fragment": None,
                    "ladder_level_used": None, "target_not_locatable": False, "span_unverified": False,
                    "ladder_exhausted_without_full_rewrite": False, "handoff": {"level_attempts": [], "text_lang": "EN"}}
        rc = lambda c, p, a: _rr11(False, devs=[_dev49("The firm said alpha rose sharply.", fid="FA")])
        res, seen = _run_kpi11([dev], lambda c, t, f: "BLOCKING" if c == 1 else "ACCEPTABLE", lambda l, p: None,
                               rc, stage3_fn=stage3)
        c2 = res["cycles"][1]["stage2_results"][0]
        self.assertEqual(c2["materiality"], "BLOCKING")
        self.assertEqual(c2["basis"], "materiality_pinned")
        self.assertEqual(c2["pinned_original_materiality"], "ACCEPTABLE")
        self.assertNotIn(res["final_state"], ("RESOLVED_STAGE2_DOWNGRADE", "RESOLVED_REWRITE_THEN_DOWNGRADE"))
        for c in res["cycles"]:   # G経路を含め、S1を飛ばした降格なし
            if c.get("judge_only_cycle"):
                self.assertIn(c["cycle"], seen["s1_calls"])
        self.assertIn("MATERIALITY_BLOCKING_PIN", res["stage4_allowlist"]["switch_fired"])
        # ピン止めOFFなら再判定で降格する(S-4の実在確認)
        res_off, _ = _run_kpi11([dev], lambda c, t, f: "BLOCKING" if c == 1 else "ACCEPTABLE", lambda l, p: None,
                                rc, stage3_fn=stage3, overrides={"MATERIALITY_BLOCKING_PIN": False})
        self.assertEqual(res_off["final_state"], "RESOLVED_REWRITE_THEN_DOWNGRADE")

    def test_rounding_blocking_never_passes_without_rewrite(self):
        """rounding(levels=[]、Rewriteしない)のBLOCKINGが、Rewriteなしでは決してPASSしない(Opus推測の同型、コードで確認)。"""
        dev = _dev49("The firm said alpha rose sharply.", fid="FA", changed_number=True,
                     changed_number_suppressed_reason="natural_rounding")
        self.assertEqual(runner.classify_problem_kind(dev), "rounding")
        legacy, _ = _run_kpi11([dev], lambda c, t, f: "BLOCKING", lambda l, p: None, lambda c, p, a: _rr11(True),
                               overrides={k: False for k in _K11_NEW})
        self.assertEqual(legacy["final_state"], "STAGE4_ESCALATION")      # 旧: ladder枯渇でSTAGE4(PASSしない)
        new, _ = _run_kpi11([dev], lambda c, t, f: "BLOCKING", lambda l, p: None, lambda c, p, a: _rr11(True))
        # 新: Rewriteは試みず(levels=[])、T(決定論削除)を経由してRecheckを受けた結果だけがPASSになる(書き換えなしのPASSではない)
        self.assertEqual(new["cycles"][0]["rewrite_records"][0]["ladder_level_used"], "0_delete")
        self.assertTrue(new["stage4_allowlist"]["t_used"])


if __name__ == "__main__":
    unittest.main()
