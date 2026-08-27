# ============================================================
# er010_entity_phonetic_corroboration_01_test_01.py
# ER-010-ENTITY-PHONETIC-CORROBORATION-01: Acceptance Tests
# ============================================================
# 対象: er006_preprod_hardening_01_validation.pyへ新設した
# soundex_en()/aggregate_entity_only_phonetic_corroboration()(固有名詞
# ASR表記揺れの軽量音韻類似度チェック)と、_convert_compound_ordinal_
# words()(複合序数の正規化バグ修正)。
from __future__ import annotations

import unittest

import er006_preprod_hardening_01_validation as v


class SoundexAndPhoneticPairTests(unittest.TestCase):
    """No.5 pool_n5_cafes full_story_part1/2の実データに基づく回帰確認。"""

    def test_1_no5_real_example_mimoun_variants_match(self):
        # 実際にNo.5で観測された、canonical "Mimoun" に対する複数の
        # 独立したTTS takeでの誤認識(Myman/Mamone/Mimmen)。
        for guess in ("myman", "mamone", "mimmen"):
            with self.subTest(guess=guess):
                self.assertTrue(v._phonetic_pair_ok("mimoun", guess, strict=False))

    def test_2_no5_real_example_gruen_variant_matches(self):
        self.assertTrue(v._phonetic_pair_ok("gruen", "grun", strict=True))

    def test_3_no5_real_example_ralf_ruller_variant_matches(self):
        self.assertTrue(v._span_phonetically_ok(["ralf", "ruller"], "ralph ruler", strict=False))

    def test_4_unrelated_content_words_do_not_match(self):
        # increase/decrease(対義語)、smith/jones(無関係な別人名)は
        # 音韻的にも一致してはならない。
        self.assertFalse(v._phonetic_pair_ok("increase", "decrease", strict=False))
        self.assertFalse(v._phonetic_pair_ok("smith", "jones", strict=False))
        self.assertFalse(v._phonetic_pair_ok("barn", "bar", strict=False))

    def test_5_word_count_mismatch_span_rejected(self):
        # "Neukölln"(1語) -> "new Cologne"(2語)のような、別の単語への
        # 丸ごと置換の疑いが強いケースは、語数不一致として常に拒否する。
        self.assertFalse(v._span_phonetically_ok(["neukolln"], "new cologne", strict=False))

    def test_6_single_occurrence_uses_strict_threshold(self):
        # 単発観測(裏付け無し)は、標準閾値では通っても厳格閾値では
        # 通らない場合がある(過度な自動採用を防ぐ)。
        self.assertTrue(v._phonetic_pair_ok("mimoun", "mamone", strict=False))
        # strict=Trueは長さ差<=1・類似度0.75以上を要求するため、"mimoun"/
        # "mamone"(類似度0.667)は厳格閾値では不採用になる。
        self.assertFalse(v._phonetic_pair_ok("mimoun", "mamone", strict=True))


class AggregateEntityOnlyPhoneticCorroborationTests(unittest.TestCase):
    """複数の独立したTTS take(asr_texts)を集約評価するメイン関数。"""

    CANONICAL = ("A 2021 qualitative study by L. Mimoun and A. Gruen, published in the "
                 "Journal of Service Research, examined this question.")

    def test_1_no5_real_two_takes_accept(self):
        # No.5実データ: 2つの独立したTTS takeで異なる誤認識が観測され、
        # かつ両方とも音韻的に妥当(このケースが本機構を作る発端になった)。
        asr_texts = [
            "A 2021 qualitative study by L. Myman and A. Grün, published in the "
            "Journal of Service Research, examined this question.",
            "A 2021 qualitative study by L. Mamone and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
        ]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertTrue(result["accept"], result["reason"])

    def test_2_single_take_with_clear_variant_is_accepted_if_not_strict_borderline(self):
        # 単発観測でも、厳格閾値を満たす程度に近い誤認識であれば採用される
        # (例: "Gruen"->"Grün"、発音区別符号のみの差に近い)。
        asr_texts = ["A 2021 qualitative study by L. Mimoun and A. Grün, published in the "
                     "Journal of Service Research, examined this question."]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertTrue(result["accept"], result["reason"])

    def test_3_single_take_with_weak_variant_is_rejected(self):
        # 単発観測かつ厳格閾値を満たさない誤認識(No.5実データの"mimmen"、
        # 類似度0.667)は、裏付けが無いため不採用のままHuman Reviewへ回る。
        asr_texts = ["A 2021 qualitative study by L. Mimmen and A. Gruen, published in the "
                     "Journal of Service Research, examined this question."]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertFalse(result["accept"])

    def test_4_consistent_alternate_name_is_rejected(self):
        # 同じ誤認識が繰り返し観測される場合(多様性の裏付けが無い)は、
        # 「別の実在する固有名詞として安定して聞こえている」可能性を
        # 排除できないため採用しない(Robert/Rupert型のリスク低減)。
        canonical = "The meeting was led by Robert, who chaired the committee."
        asr_texts = ["The meeting was led by Rupert, who chaired the committee."] * 3
        result = v.aggregate_entity_only_phonetic_corroboration(canonical, asr_texts)
        self.assertFalse(result["accept"])

    def test_5_non_entity_mismatch_take_is_skipped_not_vetoing(self):
        # No.5実データで実際に発生した状況の再現: 1つのtakeに無関係な
        # 内容語欠落("their"相当の脱落)がある場合、そのtake単体は判断
        # 材料から除外されるが、残る2つの独立したentity-only take(異なる
        # 誤認識"Myman"/"Mamone")の証拠は引き続き使われ、全体としては
        # 採用され得る(1回の無関係な不具合が対象entityの評価を無効化
        # しない)。
        asr_texts = [
            "A 2021 qualitative study by L. Myman and A. Grün, published in the "
            "Journal of Service Research, examined this question but not all of "
            "the finding.",  # "their"相当の欠落を模した非entity差(除外対象)
            "A 2021 qualitative study by L. Myman and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
            "A 2021 qualitative study by L. Mamone and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
        ]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertTrue(result["accept"], result["reason"])

    def test_5b_all_takes_non_entity_mismatch_rejects(self):
        # 全てのtakeが非entity差を含む場合、判断材料が無いため不採用。
        asr_texts = [
            "A 2021 qualitative study by L. Myman and A. Grün, published in the "
            "Journal of Service Research, examined this question but not all of "
            "the finding.",
            "A 2021 qualitative study by L. Mamone and A. Gruen, published in the "
            "Journal of Service Research, examined this question but not every angle.",
        ]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertFalse(result["accept"])

    def test_6_no_diffs_at_all_rejects_with_clear_reason(self):
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, [self.CANONICAL])
        self.assertFalse(result["accept"])

    def test_7_empty_input_rejects(self):
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, [])
        self.assertFalse(result["accept"])

    def test_8_no5_real_initial_merging_noise_does_not_block_other_evidence(self):
        # No.5実データで実際に発生した状況の再現: difflibの語境界の揺れに
        # より、"L. Mimoun"が、あるtakeでは"mimoun"単独のspanとして、
        # 別のtakeでは頭文字"L"を含む2語span("l mimoun"→ASR側は融合して
        # "elmi moon"のような無関係に見える2語)として検出されることが
        # ある。この頭文字融合ノイズが、他のtakeの明確な証拠
        # (mamoun/miman/mimon等)を巻き込んで全体を不採用にしないことを
        # 確認する。
        asr_texts = [
            "A 2021 qualitative study by Elmi Moon and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
            "A 2021 qualitative study by L. Mamoun and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
            "A 2021 qualitative study by L. Miman and A. Gruen, published in the "
            "Journal of Service Research, examined this question.",
        ]
        result = v.aggregate_entity_only_phonetic_corroboration(self.CANONICAL, asr_texts)
        self.assertTrue(result["accept"], result["reason"])


class CompoundOrdinalNormalizationTests(unittest.TestCase):
    """No.5 full_story_part2で発見した複合序数("twenty eighth"型)の
    正規化バグ修正。"""

    def test_1_space_separated_compound_ordinal(self):
        self.assertEqual(v.tokenize("April twenty eighth, 2026"), ["april", "28", "2026"])

    def test_2_hyphenated_compound_ordinal(self):
        self.assertEqual(v.tokenize("April twenty-eighth, 2026"), ["april", "28", "2026"])

    def test_3_digit_ordinal_unaffected(self):
        self.assertEqual(v.tokenize("April 28th, 2026"), ["april", "28", "2026"])

    def test_4_no5_real_case_matches_after_fix(self):
        canonical = ("In a report published by Coffee Intelligence on April twenty eighth, "
                     "2026, The Barn introduced a one-hour laptop limit.")
        asr_correct = ("In a report published by Coffee Intelligence on April 28th, 2026, "
                       "The Barn introduced a one-hour laptop limit.")
        asr_wrong = ("In a report published by Coffee Intelligence on April 26th, 2026, "
                     "The Barn introduced a one-hour laptop limit.")
        r_correct = v.classify_asr_match(canonical, asr_correct)
        r_wrong = v.classify_asr_match(canonical, asr_wrong)
        self.assertTrue(r_correct.should_pass, r_correct.reason)
        self.assertFalse(r_wrong.should_pass)
        self.assertEqual(r_wrong.protected.number_mismatches, [("28", "26")])

    def test_5_simple_ordinal_words_still_unaffected(self):
        # 既存の単純序数(tens語を伴わない)の挙動を壊していないことの確認。
        self.assertEqual(v.tokenize("the third meeting"), v.tokenize("the 3rd meeting"))
        self.assertEqual(v.tokenize("the twentieth century"), v.tokenize("the 20th century"))

    def test_6_bare_tens_cardinal_still_unaffected(self):
        # "twenty" 単独(序数語を伴わない)のcardinal変換は従来通り機能する。
        self.assertEqual(v.tokenize("twenty apples"), ["20", "apples"])

    def test_7_compound_cardinal_not_confused_with_ordinal(self):
        # "twenty eight"(cardinal、序数語ではない)は複合序数パターンに
        # マッチしない(ones語がordinal形"eighth"ではなく"eight"のため)。
        self.assertEqual(v.tokenize("twenty eight apples"), ["28", "apples"])


if __name__ == "__main__":
    unittest.main()
