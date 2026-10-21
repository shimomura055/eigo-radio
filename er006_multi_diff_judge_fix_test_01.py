# ============================================================
# er006_multi_diff_judge_fix_test_01.py
# FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01 (API 0, 常にJPY0)
# ------------------------------------------------------------
# 既存承認仕様(分かち書き/ハイフン差の吸収・CMU同音等価・数値保護)が、同一音声内に複数差分が
# あるときも個々の差分へ適用されること、および本来NGの差分はNGを維持することを固定する。
# 実行: .venv/Scripts/python.exe -m unittest er006_multi_diff_judge_fix_test_01 -v
# ============================================================
from __future__ import annotations

import json
import os
import unittest

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as s2
import er021_en_asr_semantic_equivalence_production_01 as semantic_equivalence

_HERE = os.path.dirname(os.path.abspath(__file__))
_FX = os.path.join(_HERE, "docs", "research", "FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01", "fixtures_real_transcripts.json")


def judge(canon, asr, segment_id=None):
    """Production判定チェーンのoffline版: classify_asr_match + cascadeのCMU alternate層(M1/Azureは使わない)。
    戻り値=(ClassificationResult, effective_pass, label)。"""
    r = val.classify_asr_match(canon, asr, segment_id=segment_id)
    if r.should_pass:
        return r, True, r.classification
    lab = s2._step_alternate_pass(r)
    return r, lab is not None, (lab or r.classification)


class _NoTelemetry(unittest.TestCase):
    def setUp(self):
        self._orig = semantic_equivalence.append_telemetry_log
        semantic_equivalence.append_telemetry_log = lambda *a, **k: None

    def tearDown(self):
        semantic_equivalence.append_telemetry_log = self._orig


class RealByUsCase(_NoTelemetry):
    """必須再現: 記事B Advanced Full Story第1部attempt1の実canonical/実Primary転写(固定データ)。"""

    def setUp(self):
        super().setUp()
        self.fx = json.load(open(_FX, encoding="utf8"))["byus_part1_att1"]

    def test_real_part1_attempt1_passes_via_existing_homophone_layer(self):
        r, ok, lab = judge(self.fx["canonical"], self.fx["primary_asr"], self.fx["segment_id"])
        self.assertTrue(ok)
        self.assertEqual(lab, s2.HOMOPHONE_EQUIVALENT)
        self.assertEqual([(d["canonical"], d["asr"]) for d in r.protected.content_word_diffs], [("byus", "bias")])

    def test_real_part1_attempt1_recorded_old_label_was_true_content_mismatch(self):
        # 是正前のProduction実ログの記録(再現の出発点が実在したことの固定)。
        self.assertEqual(self.fx["recorded_primary_label"], "TRUE_CONTENT_MISMATCH")


class RequiredCases(_NoTelemetry):
    def test_a_byus_to_bias_alone_passes(self):
        _, ok, lab = judge("It is byUs. Go.", "It is Bias. Go.")
        self.assertTrue(ok)
        self.assertEqual(lab, s2.HOMOPHONE_EQUIVALENT)

    def test_b_byus_bias_plus_story_making_passes(self):
        r, ok, lab = judge("A stage of story-making. It is byUs.", "A stage of storymaking. It is Bias.")
        self.assertTrue(ok)
        self.assertEqual(lab, s2.HOMOPHONE_EQUIVALENT)

    def test_b2_storymaking_alone_still_normalized_match(self):
        r = val.classify_asr_match("A stage of story-making.", "A stage of storymaking.")
        self.assertEqual(r.classification, "NORMALIZED_MATCH")

    def test_c_two_works_to_20_works_stays_ng_even_with_allowed_diffs(self):
        for asr in ("They saw 20 works. A stage of storymaking. It is Bias.",
                    "They saw 20 works. A stage of story making. It is byUs."):
            r, ok, lab = judge("They saw two works. A stage of story-making. It is byUs.", asr)
            self.assertFalse(ok, asr)
            self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
            self.assertTrue(r.protected.number_mismatches)

    def test_d_different_pronunciation_substitution_stays_ng(self):
        for canon, asr in (("I use LINE Manga. A stage of story-making.", "I use Lion Manga. A stage of storymaking."),
                           ("I need a part. A stage of story-making. It is byUs.", "I need a tart. A stage of storymaking. It is Bias.")):
            r, ok, lab = judge(canon, asr)
            self.assertFalse(ok, asr)

    def test_d2_line_to_lion_with_byus_bias_stays_ng(self):
        r, ok, lab = judge("LINE says byUs is new. A stage of story-making.", "Lion says Bias is new. A stage of storymaking.")
        self.assertFalse(ok)

    def test_e_dropped_word_stays_ng(self):
        r, ok, lab = judge("A stage of story-making. It is byUs.", "A stage of making. It is Bias.")
        self.assertFalse(ok)
        self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
        r, ok, lab = judge("A stage of story-making. It is byUs. Works are here.", "A stage of storymaking. It is Bias. Are here.")
        self.assertFalse(ok)

    def test_f_buy_us_two_word_form_current_behaviour_recorded(self):
        # 拡張しない: "Buy Us"はCMU単語対単語の同音等価に該当せず従来どおりNG(multi-diffでも同じ)。
        r1, ok1, _ = judge("It is byUs. Go.", "It is Buy Us. Go.")
        r2, ok2, _ = judge("A stage of story-making. It is byUs.", "A stage of storymaking. It is Buy Us.")
        self.assertFalse(ok1)
        self.assertFalse(ok2)
        self.assertEqual(r1.classification, "TRUE_CONTENT_MISMATCH")
        self.assertEqual(r2.classification, "TRUE_CONTENT_MISMATCH")

    def test_g_family_z_real_segments_unchanged(self):
        fx = json.load(open(_FX, encoding="utf8"))["family_z"]
        # 旧判定関数(git HEAD版)で同一データを再判定した値を固定(golden: 新旧一致)
        expect = {"full_story_part1_c1": ("ASR_VALIDATION_UNCERTAIN", False),
                  "comment_1": ("ASR_VALIDATION_UNCERTAIN", False),
                  "preview": ("EXACT_MATCH", True)}
        for sid, (cls, sp) in expect.items():
            r = val.classify_asr_match(fx[sid]["canonical"], fx[sid]["asr_text"], segment_id=sid)
            self.assertEqual((r.classification, r.should_pass), (cls, sp), sid)


class SpanHelperBoundary(_NoTelemetry):
    """新しい許容規則を足していないこと(全文規則と同じ基準・数値/否定/脱落には不適用)。"""

    def test_helper_only_accepts_existing_despace_rules(self):
        f = val._is_compound_spacing_only_span
        self.assertTrue(f(["story", "making"], ["storymaking"]))
        self.assertTrue(f(["storymaking"], ["story", "making"]))
        self.assertTrue(f(["a", "wide", "scale"], ["widescale"]))  # 冠詞のみ除外する既存規則
        self.assertFalse(f(["story", "making"], ["story"]))  # 脱落
        self.assertFalse(f(["story"], []))
        self.assertFalse(f([], ["story"]))
        self.assertFalse(f(["line"], ["lion"]))
        self.assertFalse(f(["the", "story"], ["a", "tale"]))
        self.assertFalse(f(["to", "works"], ["20", "works"]))  # 数値を含むspanは対象外
        self.assertFalse(f(["not", "going"], ["notgoing"]))  # 否定語を含むspanは対象外
        self.assertFalse(f(["with"], ["without"]))  # 前置詞だけの除去は許さない

    def test_no_new_allowance_for_phonetic_neighbours(self):
        r, ok, _ = judge("It is byUs. Go.", "It is Bias, buys. Go.")
        self.assertFalse(ok)


class ContractUnchanged(_NoTelemetry):
    """戻り値契約(ClassificationResult fields / content_word_diffsのkey集合)が不変。"""

    def test_classification_result_contract(self):
        r = val.classify_asr_match("A stage of story-making. It is byUs.", "A stage of storymaking. It is Bias.")
        for f in ("classification", "normalized_ratio", "protected", "should_pass", "should_retry", "reason",
                  "connected_speech_info", "semantic_equivalence_info"):
            self.assertTrue(hasattr(r, f), f)
        for f in ("passed", "number_mismatches", "negation_mismatches", "content_word_diffs"):
            self.assertTrue(hasattr(r.protected, f), f)
        for d in r.protected.content_word_diffs:
            self.assertEqual(set(d), {"type", "canonical", "asr", "entity_like", "homophone_candidate", "entity_like_source"})
        self.assertEqual(r.classification, "ASR_VALIDATION_UNCERTAIN")
        self.assertFalse(r.should_pass)
        self.assertFalse(r.should_retry)

    def test_true_mismatch_keeps_retry_contract(self):
        r = val.classify_asr_match("We must increase it. A stage of story-making.", "We must decrease it. A stage of storymaking.")
        self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")
        self.assertTrue(r.should_retry)
        self.assertFalse(r.should_pass)


class XZSharedJudgePath(unittest.TestCase):
    """Family X(er003 repro01 / er019 runner)とFamily Z(er063 -> er012)が同一の判定関数を通ること。"""

    def test_x_and_z_modules_use_same_secondary_asr_and_validation(self):
        import er003_v1_repro01_main_generate as x_gen
        import er012_b_family_voices_production_01 as z_gen
        self.assertIs(x_gen.secondary_asr, s2)
        self.assertIs(z_gen.secondary_asr, s2)
        self.assertIs(s2.val, val)
        self.assertTrue(callable(s2.evaluate_attempt_with_cascade))

    def test_family_z_entry_points_to_er012(self):
        src = open(os.path.join(_HERE, "er063_family_z_audio_01.py"), encoding="utf8").read()
        self.assertIn("bvoices.generate_voice_body_wide_margin(", src)
        self.assertIn("import er012_b_family_voices_production_01 as bvoices", src)
        self.assertIn("import er003_v1_repro01_main_generate as repro01", src)

    def test_x_runner_uses_repro01(self):
        src = open(os.path.join(_HERE, "er019_family_x_audio_production_runner_01.py"), encoding="utf8").read()
        self.assertIn("import er003_v1_repro01_main_generate as repro01", src)
        self.assertIn("repro01.generate_narration_snippet_verified_strict(", src)


if __name__ == "__main__":
    unittest.main()
