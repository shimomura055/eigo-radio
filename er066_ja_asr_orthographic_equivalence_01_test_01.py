# JA-ASR-ORTHOGRAPHIC-EQUIVALENCE-COMPREHENSIVE-01 Regression test (API不使用、¥0)
# 実行: .venv\Scripts\python.exe -m unittest er066_ja_asr_orthographic_equivalence_01_test_01 -v
import glob
import re
import unittest

import er003_audio_tts_asr_safety as safety
import er007_ja_asr_validator_01 as javal
import er066_ja_asr_orthographic_equivalence_01_cases as cases
import er066_ja_asr_orthographic_equivalence_01_trial as trial

javal.FEATURE_FLAG_A2_READING_RESOLVER_ENABLED = False  # LLM/API呼出を完全に無効化


class TestExistingSpecClosedCounterList(unittest.TestCase):
    """既存承認仕様(閉じた助数詞リスト)の特性化テスト。Production無変更であることの回帰確認。"""

    PAIRS = [("二つ", "2つ"), ("二泊", "2泊"), ("三回", "3回"), ("五件", "5件"), ("三年", "3年"), ("三時間", "3時間"),
             ("三か月", "3か月"), ("三ヶ月", "3か月"), ("二週", "2週"), ("五歳", "5歳"), ("十件", "10件"),
             ("二十歳", "20歳"), ("百回", "100回"), ("1年間", "一年間"), ("二週間", "2週間")]

    def test_closed_list_all_pass_in_full_sentence(self):
        for c, a in self.PAIRS:
            for pre, post in (("", ""), ("彼は", "を待ちました。")):
                r = javal.classify_ja_asr_match(pre + c + post, pre + a + post, allow_reading_resolver=False)
                self.assertTrue(r.should_pass, (c, a, r.classification))

    def test_closed_list_declared_in_spec(self):
        self.assertEqual(safety._CLOSED_COUNTERS_JA, ("つ", "泊", "回", "件", "年", "時間", "か月", "週", "歳"))

    def test_nichi_ninn_still_excluded_in_production(self):
        # 日/人は意図的除外(三日坊主副作用)。Productionは本タスクで無変更=従来どおりMISMATCH(OPEN-319/287)
        for c, a in (("三日間", "3日間"), ("二人", "2人")):
            r = javal.classify_ja_asr_match(c, a, allow_reading_resolver=False)
            self.assertFalse(r.should_pass, (c, a))
            self.assertEqual(r.classification, "TRUE_CONTENT_MISMATCH")

    # TEST-HYGIENE-02(2026-10-22): 旧testは単純な部分文字列一致のため、Production側のコメント(移設元の記録:
    # er078_asr_value_guard_01.pyの「Production→Trial import禁止のため移設」説明)にも反応していた。
    # 禁止したいのは実際のimport文なので、import/from文のみを検出する。parity test(er078_asr_value_guard_01_test_01.py、
    # 設計どおり"test側のみがTrialをimport")はtest fileとして対象外。
    _IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+er066_ja_asr_orthographic", re.M)

    def test_production_does_not_import_trial(self):
        for p in glob.glob("er0*.py") + glob.glob("verify_*.py"):
            if "er066_" in p or re.search(r"_test_\d+\.py$", p):
                continue
            with open(p, encoding="utf-8", errors="ignore") as fh:
                txt = fh.read()
            self.assertIsNone(self._IMPORT_RE.search(txt), p)


class TestNumberReading(unittest.TestCase):
    def test_kana_int(self):
        for n, k in [(1, "いち"), (10, "じゅう"), (20, "にじゅう"), (100, "ひゃく"), (300, "さんびゃく"), (600, "ろっぴゃく"),
                     (1000, "せん"), (3000, "さんぜん"), (10000, "いちまん"), (35000, "さんまんごせん")]:
            self.assertEqual(trial.kana_int(n), k)

    def test_counter_readings(self):
        c = trial._cands
        self.assertIn("みっか", c(3, "day"))
        self.assertIn("みっかかん", c(3, "day_span"))
        self.assertIn("ふたり", c(2, "person"))
        self.assertIn("よにん", c(4, "person"))
        self.assertIn("じゅっぷん", c(10, "minute"))
        self.assertIn("さんぷん", c(3, "minute"))
        self.assertIn("さんぼん", c(3, "hon"))
        self.assertIn("ろっぽん", c(6, "hon"))
        self.assertIn("よじ", c(4, "hour"))
        self.assertIn("しがつ", c(4, "month"))
        self.assertIn("はたち", c(20, "age"))
        self.assertIn("さんがい", c(3, "floor"))
        self.assertIn("いっかい", c(1, "kai"))

    def test_value_parse(self):
        v = trial._to_value
        self.assertEqual(v("三十"), "30")
        self.assertEqual(v("百"), "100")
        self.assertEqual(v("一万"), "10000")
        self.assertEqual(v("1,000"), "1000")
        self.assertEqual(v("3万"), "30000")
        self.assertEqual(v("0.5"), "0.5")
        self.assertIsNone(v("〇"))


class TestPositive(unittest.TestCase):
    def test_all_positive_pass_after(self):
        for c, a, k in cases.POSITIVE:
            r = trial.trial_judge(c, a)
            self.assertTrue(r.would_pass, (c, a, k, r.verdict, r.detail))

    def test_at_least_one_rescue_beyond_production(self):
        self.assertTrue(any(trial.trial_judge(c, a).rescued for c, a, _ in cases.POSITIVE))


class TestAdversarialNoFalsePass(unittest.TestCase):
    def test_adversarial_count(self):
        self.assertGreaterEqual(len(cases.NEGATIVE), 20)

    def test_no_false_pass(self):
        for c, a, k in cases.NEGATIVE:
            r = trial.trial_judge(c, a)
            self.assertFalse(r.would_pass, (c, a, k, r.verdict))

    def test_trial_never_rescues_value_or_counter_difference(self):
        # Trial層が『新規に』救済してよいのは署名(値,助数詞)が一致する場合のみ
        for c, a, k in cases.NEGATIVE:
            r = trial.trial_judge(c, a)
            self.assertFalse(r.rescued, (c, a, k))

    def test_ambiguous_juubun_never_rescued(self):
        for c, a in (("十分待った", "10分待った"), ("10分待った", "十分待った"), ("十分に理解した", "10分に理解した")):
            self.assertEqual(trial.trial_judge(c, a).verdict, "AMBIGUOUS_NO_RESCUE")
        # 三十分は曖昧語ではない
        self.assertTrue(trial.trial_judge("三十分待った", "30分待った").would_pass)

    def test_negation_dropped_is_not_rescued(self):
        for c, a in (("三日間行かない", "3日間行く"), ("3日間ない", "三日間ある"), ("三人で来た", "3人で来なかった")):
            self.assertFalse(trial.trial_judge(c, a).would_pass)

    def test_unknown_counter_fails_safe(self):
        # 助数詞表に無い語は一切変換しない(従来どおりNG維持=救済しない)
        r = trial.trial_judge("三羽の鳥", "3羽の鳥")
        self.assertFalse(r.would_pass)

    def test_candidate_e_veto(self):
        # 現行Production(Candidate E)が『三日間=三日目』を通す型を、Trial層は取り消す
        pr = trial.prod_effective("三日間", "三日目")
        self.assertTrue(pr.should_pass)  # Productionの現状(誤PASS、OPEN候補として報告)
        self.assertEqual(trial.trial_judge("三日間", "三日目").verdict, "VETO_PROD_PASS")

    def test_pure_homophone_not_vetoed(self):
        # 一回/1階はともに「いっかい」で音声では区別不能 -> 既存PHONETIC_MATCH方針のまま
        self.assertEqual(trial.trial_judge("一回に2点", "1階に2点").verdict, "PRODUCTION_PASS")


class TestAdditive(unittest.TestCase):
    def test_production_pass_unchanged(self):
        for c, a in (("彼は二つを待ちました。", "彼は2つを待ちました。"), ("今日は晴れです。", "今日は晴れです"),
                     ("三日間の旅", "みっかかんの旅"), ("落とし穴", "おとしあな")):
            self.assertEqual(trial.trial_judge(c, a).verdict, "PRODUCTION_PASS")


if __name__ == "__main__":
    unittest.main()
