# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 委任_02 Regression test (API不使用、¥0)
# 実行: .venv\Scripts\python.exe -m unittest er066_ja_asr_orthographic_equivalence_01_test_02 -v
import unittest

import er007_ja_asr_validator_01 as javal
import er066_ja_asr_orthographic_equivalence_01_cases as cases1
import er066_ja_asr_orthographic_equivalence_01_cases_02 as cases2
import er066_ja_asr_orthographic_equivalence_01_trial as trial

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False  # LLM/API呼出を完全に無効化


class TestSpanGrammar(unittest.TestCase):
    def test_man_alone_is_not_zero(self):
        self.assertIsNone(trial._to_value("万"))
        self.assertEqual(trial.find_spans("万円です"), [])
        self.assertEqual(trial._to_value("一万"), "10000")

    def test_invalid_kanji_grammar(self):
        for bad in ("万千", "十千", "百千"):
            self.assertIsNone(trial._to_value(bad), bad)
        self.assertEqual(trial._to_value("三万五千"), "35000")

    def test_digit_grouping_only_three_digit(self):
        self.assertEqual(trial._to_value("1,000"), "1000")
        self.assertEqual(trial._to_value("12,345"), "12345")
        self.assertEqual([s.value for s in trial.find_spans("1,000円")], ["1000"])
        # 全角「，」はNFKCで「,」になる: 3桁区切りでなければスパンにならない(34日と読まない)
        for t in ("3，4日", "3,4日", "3,45日"):
            self.assertEqual([s.value for s in trial.find_spans(t) if s.value == "34"], [], t)
            self.assertNotIn("34", [s.value for s in trial.find_spans(t)], t)

    def test_man_prefix_blocks_partial_span(self):
        self.assertEqual(trial.find_spans("3万5千円"), [])


class TestReadingTableFixes(unittest.TestCase):
    def test_six_age_week_no_sokuon(self):
        self.assertIn("ろくさい", trial._cands(6, "age"))
        self.assertNotIn("ろっさい", trial._cands(6, "age"))
        self.assertIn("ろくしゅうかん", trial._cands(6, "week"))
        self.assertNotIn("ろっしゅうかん", trial._cands(6, "week"))
        self.assertIn("いっさい", trial._cands(1, "age"))
        self.assertIn("いっしゅうかん", trial._cands(1, "week"))
        self.assertIn("ろっかい", trial._cands(6, "kai"))

    def test_thousand_hon_minute(self):
        self.assertIn("せんぼん", trial._cands(1000, "hon"))
        self.assertIn("さんぜんぼん", trial._cands(3000, "hon"))


class TestAmbiguousExtended(unittest.TestCase):
    def test_new_ambiguous(self):
        for c, a in cases2.AMBIGUITY_NO_RESCUE:
            r = trial.trial_judge(c, a)
            self.assertEqual(r.verdict, "AMBIGUOUS_NO_RESCUE", (c, a, r.verdict))

    def test_compound_numbers_not_ambiguous(self):
        # 十一時・二十一時・三十一月は『一時』『一月』を含むが曖昧語ではない
        self.assertFalse(trial.has_ambiguous("十一時に会う"))
        self.assertFalse(trial.has_ambiguous("二十一時"))


class TestStages(unittest.TestCase):
    def test_stage1_notation(self):
        r = trial.trial_judge("英国政府が10代の若者", "英国政府が十代の若者")
        self.assertEqual((r.verdict, r.stage), ("TRIAL_NOTATION_MATCH", "S1"))

    def test_stage1_prime_rescues_with_concurrent_diffs(self):
        # Melos A2型: 同文に あと/後、つけ/付け が併発。Stage1(表記のみ)は不可、Stage1'で救済
        c = "王は三日目の日没までに戻るよう条件をつけます。メロスは式のあと、三日目の夜明け前に町へ向かいます。"
        a = "王は3日目の日没までに戻るよう条件を付けます。メロスは式の後、3日目の夜明け前に町へ向かいます。"
        r = trial.trial_judge(c, a)
        self.assertEqual((r.verdict, r.stage), ("TRIAL_NOTATION_MATCH", "S1P"))
        self.assertFalse(r.rescued_at("S1"))
        self.assertTrue(r.rescued_at("S1P"))
        # 20%: あと/後併発
        r = trial.trial_judge("まず20％という計画が発表されたあと、決まっていなかった", "まず20パーセントという計画が発表された後、決まっていなかった")
        self.assertEqual(r.stage, "S1P")

    def test_stage1_prime_does_not_use_reading_table(self):
        # 読み(かな)で書かれたASRはStage1'では救済できずStage2へ
        r = trial.trial_judge("10分待つ", "じゅっぷん待つ")
        self.assertEqual(r.stage, "S2")

    def test_stage1_prime_requires_ordered_signature_equality(self):
        r = trial.trial_judge("二泊三日の旅", "三泊二日の旅")
        self.assertFalse(r.would_pass)

    def test_stage1_prime_exception_falls_back(self):
        orig = trial.opaque_form
        try:
            def boom(_):
                raise RuntimeError("x")
            trial.opaque_form = boom
            r = trial.trial_judge("王は三日目の日没、条件をつけます", "王は3日目の日没、条件を付けます")
            self.assertFalse(r.rescued_at("S1P"))  # 例外->救済せず(Stage2へ進み、読み展開で救済は別段階)
            self.assertNotEqual(r.stage, "S1P")
        finally:
            trial.opaque_form = orig

    def test_stage_cumulative_columns(self):
        r = trial.trial_judge("三日間", "3日間")
        self.assertTrue(all(r.rescued_at(s) for s in ("S1", "S1P", "S2")))
        r = trial.trial_judge("20歳になった", "はたちになった")
        self.assertEqual((r.verdict, r.stage), ("TRIAL_READING_MATCH", "S2"))
        self.assertTrue(r.rescued_at("S2") and not r.rescued_at("S1P"))


class TestCandidateEGuardFix(unittest.TestCase):
    def test_kana_side_not_vetoed_by_span_count_difference(self):
        # 旧実装: 片側にスパンがないだけで署名が『異なる』扱いになり取消。新: 読み展開で比較(正しい読みなら取消さない)
        self.assertFalse(trial.candidate_e_veto("三日間のあと", "みっかかんの後"))
        self.assertFalse(trial.candidate_e_veto("みっかかんの後", "三日間のあと"))
        self.assertFalse(trial.candidate_e_veto("三日坊主", "みっかぼうず"))

    def test_kana_side_wrong_reading_is_vetoed(self):
        self.assertTrue(trial.candidate_e_veto("三日間", "さんにち間"))
        self.assertTrue(trial.candidate_e_veto("三日坊主", "さんにちぼうず"))

    def test_both_side_signature_diff_vetoed(self):
        self.assertTrue(trial.candidate_e_veto("三日間", "三日目"))
        self.assertTrue(trial.candidate_e_veto("3日間", "3日目"))

    def test_homophone_signature_not_vetoed(self):
        self.assertFalse(trial.candidate_e_veto("一回に2点", "1階に2点"))

    def test_no_span_not_vetoed(self):
        self.assertFalse(trial.candidate_e_veto("落とし穴", "おとしあな"))

    def test_judge_level(self):
        self.assertEqual(trial.trial_judge("三日間", "三日目").verdict, "VETO_PROD_PASS")
        self.assertEqual(trial.trial_judge("三日間", "さんにち間").verdict, "VETO_PROD_PASS")
        self.assertEqual(trial.trial_judge("三日間", "みっか間").verdict, "PRODUCTION_PASS")

    def test_via_candidate_e_is_string_match_in_trial(self):
        # Trialは reason 文字列一致。Production実装では構造化フィールドを使う(docstringに明記)
        self.assertIn("構造化", trial.via_candidate_e.__doc__)


class TestWarningFlag(unittest.TestCase):
    def test_irregular_signatures(self):
        for v, k in (("3", "day"), ("3", "day_span"), ("1", "day"), ("14", "day"), ("20", "day"), ("24", "day"), ("1", "person"),
                     ("2", "person"), ("20", "age"), ("5", "tsu"), ("4", "month"), ("7", "hour")):
            self.assertTrue(trial.is_irregular_sig(v, k), (v, k))
        for v, k in (("3", "person"), ("100", "yen"), ("10", "gen"), ("20", "percent"), ("30", "age"), ("2", "month")):
            self.assertFalse(trial.is_irregular_sig(v, k), (v, k))

    def test_rescue_with_warning(self):
        self.assertTrue(trial.trial_judge("三日間", "3日間").warning)
        self.assertFalse(trial.trial_judge("10代の若者", "十代の若者").warning)
        self.assertFalse(trial.trial_judge("Production通過", "Production通過").warning)


class TestPositive02(unittest.TestCase):
    def test_all_pass(self):
        for c, a, k in cases2.POSITIVE_02:
            r = trial.trial_judge(c, a)
            self.assertTrue(r.would_pass, (c, a, k, r.verdict, r.detail))

    def test_v1_positive_still_pass(self):
        for c, a, k in cases1.POSITIVE:
            self.assertTrue(trial.trial_judge(c, a).would_pass, (c, a, k))


class TestAdversarial02(unittest.TestCase):
    def test_counts(self):
        self.assertGreaterEqual(len(cases1.NEGATIVE) + len(cases2.NEGATIVE_02), 70)

    def test_no_false_pass_v2(self):
        for c, a, k in cases2.NEGATIVE_02:
            r = trial.trial_judge(c, a)
            self.assertFalse(r.would_pass, (c, a, k, r.verdict))
            self.assertFalse(r.rescued, (c, a, k))

    def test_no_false_pass_v1_still(self):
        for c, a, k in cases1.NEGATIVE:
            self.assertFalse(trial.trial_judge(c, a).would_pass, (c, a, k))

    def test_stage_columns_no_false_pass(self):
        for c, a, k in cases1.NEGATIVE + cases2.NEGATIVE_02:
            r = trial.trial_judge(c, a)
            for s in ("S1", "S1P", "S2"):
                self.assertFalse(r.rescued_at(s), (c, a, k, s))


class TestExistingProductionDefectCharacterization(unittest.TestCase):
    """既存Production(normalize_ja)が〜/、を除去した直後に文字列一致でNORMALIZED_MATCHを返す不具合候補の特性化。
    Productionは本タスクで無変更。これらが将来修正されFalseに変わった場合は本testを更新する(OPEN-334)。"""

    def test_prod_passes_range_and_enumeration(self):
        for c, a, k in cases2.PRODBUG:
            r = javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)
            self.assertTrue(r.should_pass, (c, a, k, r.classification))

    def test_trial_adds_nothing_on_these(self):
        for c, a, k in cases2.PRODBUG:
            self.assertFalse(trial.trial_judge(c, a).rescued, (c, a, k))


if __name__ == "__main__":
    unittest.main()
