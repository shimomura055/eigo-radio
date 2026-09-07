# ============================================================
# er011_transcript_style_normalization_production_wiring_01_test_01.py
# OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-PRODUCTION-WIRING-01
# ============================================================
# 採用元: OPEN-123-TRANSCRIPT-STYLE-NORMALIZATION-TRIAL-01_REPORT.md §13
# (VALIDATED)。ユーザー正式決定(2026-09-07、APPROVED_FOR_PRODUCTION):
# 標準contraction展開(否定保持のみ)を英語ASR照合の共通正規化層として
# 採用、wanna系(方式iv)は不採用。
#
# 本テストは以下を確認する:
#   (1) 既知のfalse rejectパターン(否定保持contraction)が救済される。
#   (2) 否定反転(can/can't・will/won't)・動詞屈折(asked/asks)・
#       wanna系はいずれも非救済のまま(false accept 0)。
#   (3) 's/'d(is/has・would/had)のような曖昧なcontractionでも、誤った
#       解釈を選んだ場合は「展開後に両側が既存Validatorの基準でPASSと
#       判定された場合のみ採用」という設計により安全側(非救済)に倒れる
#       ことを構造的に確認する。
#   (4) 英語ASR照合の共通経路(classify_asr_match自体、およびKey Phrase
#       呼び出しパターン[enable_non_latin_cascade=True]を模したCascade
#       呼び出し)の両方で同じ挙動になる(=Key Phrase英語経路にも
#       共通適用されることの確認)。
#   (5) 日本語経路(er007_ja_secondary_asr_01/er007_ja_asr_validator_01)
#       が本モジュールを一切importしておらず、影響を受けないことを
#       ソースレベルで証明する。
from __future__ import annotations

import inspect
import unittest

import er006_preprod_hardening_01_validation as val
import er006_secondary_asr_01 as secondary_asr


class TranscriptStyleNormalizationRescueTests(unittest.TestCase):
    """(1) 否定保持contractionによる既知false rejectの救済。"""

    def test_do_not_dont_rescued(self):
        r = val.classify_asr_match(
            "The office manager does not answer emails during the weekend.",
            "The office manager doesn't answer emails during the weekend.")
        self.assertEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")
        self.assertTrue(r.should_pass)
        self.assertFalse(r.should_retry)

    def test_trial08_p3_point_two_all_3_attempts_rescued(self):
        """Trial-08 P3 point_two(3回STOPPED、do not/don'tのみが差分)の
        実データを再現し、修正後の分類本体で救済されることを確認する。"""
        canonical = ("Since working from home gave them a place of their own, "
                     "they do not need one fixed spot at the office.")
        asr_variants = [
            "Since working from home gave them a place of their own, they don’t need one fixed spot at the office.",
            "Since working from home gave them a place of their own, they don't need one fixed spot at the office.",
        ]
        for asr in asr_variants:
            r = val.classify_asr_match(canonical, asr)
            self.assertTrue(r.should_pass, msg=f"asr={asr!r} classification={r.classification}")
            self.assertEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_non_negation_contraction_rescued(self):
        r = val.classify_asr_match("We are checking again tomorrow.", "We're checking again tomorrow.")
        self.assertTrue(r.should_pass)
        self.assertEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_no_intervention_when_baseline_already_passes(self):
        """既にNORMALIZED_MATCH等でPASSしている場合、ラッパーは介入せず
        baselineの分類名をそのまま返す(余計な上書きをしない)。"""
        r = val.classify_asr_match("a wide-scale empirical study", "Wide-scale empirical study.")
        self.assertEqual(r.classification, "NORMALIZED_MATCH")

    def test_no_intervention_when_no_contraction_present(self):
        """contractionが元々どちらの側にも無ければ、展開しても何も変わらず
        baseline(TRUE_CONTENT_MISMATCH)がそのまま返る(無駄な再帰なし)。"""
        r = val.classify_asr_match(
            "Prices tend to increase after the trial period.",
            "Prices tend to decrease after the trial period.")
        self.assertFalse(r.should_pass)
        self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")


class TranscriptStyleNormalizationSafetyTests(unittest.TestCase):
    """(2)(3) false accept 0を構造的に確認する(否定反転・動詞屈折・
    wanna系・曖昧なcontractionの誤解釈)。"""

    def test_can_cant_negation_reversal_not_rescued(self):
        r = val.classify_asr_match(
            "You can access the file from any device.",
            "You can't access the file from any device.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_will_wont_negation_reversal_not_rescued(self):
        r = val.classify_asr_match("The store will open on Monday.", "The store won't open on Monday.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_asked_asks_verb_inflection_not_rescued(self):
        """動詞屈折(asked/asks)はcontraction展開の対象外の別failure mode
        であり、非救済のまま(OPEN-122で個別に発見済み、混同しないことの
        確認)。"""
        r = val.classify_asr_match(
            "She asked them to review the document before the meeting.",
            "She asks them to review the document before the meeting.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_wanna_not_rescued(self):
        """wanna系(方式iv)はユーザー決定により不採用。_ALL_STANDARD_
        CONTRACTIONSに含まれておらず、展開されないため非救済のまま。"""
        self.assertNotIn("wanna", val._ALL_STANDARD_CONTRACTIONS)
        self.assertNotIn("gonna", val._ALL_STANDARD_CONTRACTIONS)
        self.assertNotIn("gotta", val._ALL_STANDARD_CONTRACTIONS)
        r = val.classify_asr_match(
            "Don't you want to come with us?",
            "Don't you wanna come with us?")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_ambiguous_apostrophe_s_wrong_interpretation_stays_safe(self):
        """'s は "is" として展開されるが、実際には "has" の意味である
        canonical("It has been a long day.")の場合、展開後も一致しない
        ため非救済のまま(誤った解釈を選んでもfalse acceptにならない
        ことの構造的確認)。"""
        r = val.classify_asr_match("It has been a long day.", "It's been a long day.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_ambiguous_apostrophe_d_wrong_interpretation_stays_safe(self):
        """'d は "would" として展開されるが、実際には "had" の意味である
        canonicalの場合、展開後も一致しないため非救済のまま。"""
        r = val.classify_asr_match(
            "They had already left when we arrived.",
            "They'd already left when we arrived.")
        self.assertFalse(r.should_pass)
        self.assertNotEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_ambiguous_apostrophe_s_correct_interpretation_rescued(self):
        """'s が実際に"is"の意味である場合(想定通りの解釈)は救済される
        ことも合わせて確認する(安全設計が過剰に保守的すぎないことの
        確認)。"""
        r = val.classify_asr_match("It is a long day today.", "It's a long day today.")
        self.assertTrue(r.should_pass)
        self.assertEqual(r.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")


class TranscriptStyleNormalizationCommonPathTests(unittest.TestCase):
    """(4) 英語ASR照合の共通経路(classify_asr_match自体がevaluate_attempt/
    evaluate_attempt_with_cascade_detailの内部で使われる設計のため、
    Key Phrase呼び出しパターンでも自動的に同じ挙動になる)ことを確認する。
    新規opt-inフラグは追加していない(enable_non_latin_cascade=Trueのみ、
    Key Phrase呼び出しと同じkwargを使う)。"""

    def test_valid_classifications_includes_new_label(self):
        self.assertIn("TRANSCRIPT_STYLE_NORMALIZED_MATCH", val.VALID_CLASSIFICATIONS)

    def test_evaluate_attempt_rescues_without_wav_dependency(self):
        """evaluate_attempt()はclassify_asr_match()のみを呼び、wav_pathに
        一切依存しない(=Primary#1の時点で救済されればCascade層の追加
        ASR呼び出しは発生しない、コスト増なし)ことを確認する。"""
        verified, stop_retrying, cls = val.evaluate_attempt(
            "The team will not finish the project before the deadline.",
            "The team won't finish the project before the deadline.", [])
        self.assertTrue(verified)
        self.assertFalse(stop_retrying)
        self.assertEqual(cls.classification, "TRANSCRIPT_STYLE_NORMALIZED_MATCH")

    def test_key_phrase_style_cascade_call_rescues_contraction(self):
        """Key Phrase呼び出しと同じkwarg(enable_non_latin_cascade=True、
        他のopt-inフラグは渡さない)のCascade呼び出しでも救済されることを
        確認する(=英語Key Phrase経路にも共通適用される)。wav_pathは
        実在しないダミーだが、Primary#1で即PASSするためwavへのアクセスは
        発生しない(追加ASR呼び出し無し)。"""
        detail = secondary_asr.evaluate_attempt_with_cascade_detail(
            "The client cannot access the shared folder from home.",
            "The client can't access the shared folder from home.",
            prior_results=[], wav_path="__nonexistent_dummy_for_test__.wav",
            language="en-US", enable_non_latin_cascade=True)
        self.assertTrue(detail["verified"])
        self.assertEqual(detail["final_status"], "TRANSCRIPT_STYLE_NORMALIZED_MATCH")
        self.assertFalse(detail["cascade_invoked"])
        self.assertFalse(detail["human_review_required"])

    def test_key_phrase_style_cascade_call_does_not_rescue_negation_reversal(self):
        """同じKey Phrase呼び出しパターンで、否定反転(can/can't)は救済
        されないことも確認する(false accept 0を共通経路側でも確認)。
        末尾まで到達するとcascade_eligible判定はFalse(entity_like/
        homophone_candidateいずれでもない)のため、追加ASR呼び出しは
        発生せずTRUE_CONTENT_MISMATCHのまま即returnされる(wavアクセス
        なし)。"""
        detail = secondary_asr.evaluate_attempt_with_cascade_detail(
            "You can access the shared folder from any device.",
            "You can't access the shared folder from any device.",
            prior_results=[], wav_path="__nonexistent_dummy_for_test__.wav",
            language="en-US", enable_non_latin_cascade=True)
        self.assertFalse(detail["verified"])
        self.assertEqual(detail["final_status"], "TRUE_CONTENT_MISMATCH")


class TranscriptStyleNormalizationJapanesePathIndependenceTests(unittest.TestCase):
    """(5) 日本語経路(er007_*)が本層の影響を一切受けないことをソース
    レベルで証明する(OPEN-122のer011_connected_speech_equivalence_
    layer_production_wiring_01_test_01.pyと同じ設計パターン)。"""

    def test_japanese_secondary_asr_module_does_not_import_english_validator(self):
        import er007_ja_secondary_asr_01 as ja_secondary_asr
        src = inspect.getsource(ja_secondary_asr)
        self.assertNotIn("import er006_preprod_hardening_01_validation", src)
        self.assertNotIn("expand_standard_contractions", src)
        self.assertFalse(hasattr(ja_secondary_asr, "expand_standard_contractions"))
        self.assertNotIn("er006_preprod_hardening_01_validation", dir(ja_secondary_asr))

    def test_japanese_asr_validator_module_does_not_import_english_validator(self):
        """er007_ja_asr_validator_01.pyはコメント中で英語Validatorの
        モジュール名に言及している(設計思想の由来を説明するため)が、
        実際にはimportしておらず、本層の関数(expand_standard_
        contractions等)はモジュール名前空間に一切存在しない
        (importはコメントではなく実際のバインディングの有無で判定する)。"""
        import er007_ja_asr_validator_01 as ja_validator
        src = inspect.getsource(ja_validator)
        self.assertNotIn("import er006_preprod_hardening_01_validation", src)
        self.assertNotIn("expand_standard_contractions", src)
        self.assertFalse(hasattr(ja_validator, "expand_standard_contractions"))
        self.assertNotIn("er006_preprod_hardening_01_validation", dir(ja_validator))

    def test_english_validator_module_english_only_docstring_preserved(self):
        """er006_preprod_hardening_01_validation.pyのモジュールdocstring/
        header comment(「このvalidatorは英語専用」)が維持されていることを
        再確認する(このモジュール自体がen専用である前提が変わっていない
        ことの確認)。"""
        src = inspect.getsource(val)
        self.assertIn("英語専用", src)


if __name__ == "__main__":
    unittest.main()
