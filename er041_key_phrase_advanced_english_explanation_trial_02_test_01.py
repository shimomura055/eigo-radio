# ============================================================
# er041_key_phrase_advanced_english_explanation_trial_02_test_01.py
# KEY-PHRASE-ADVANCED-ENGLISH-EXPLANATION-TRIAL-02: 単体test(費用ゼロ、
# API呼び出しは行わない)。プロジェクト規約に合わせunittest.TestCase形式
# で実装する(run_project_regression.py はunittest.TestLoader().discover()
# を使う)。
# ============================================================
from __future__ import annotations

import json
import os
import unittest

import er017_key_phrase_level_spec_trial_01 as prior_trial
import er041_key_phrase_advanced_english_explanation_trial_02 as trial

SUMMARY_PATH = "er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz/summary.json"
MATCH_RESULTS_PATH = ("er041_output/key_phrase_advanced_english_explanation_trial_02/hormuz/"
                       "match_results.json")
KEYWORDS_PATH = ("er019_output/family_x_audio_production_wiring_01/family_x_b3_diversity_trial_01/"
                  "hormuz__run_06_flashlite_full_kp/b1b/key_phrases/keywords_canonicalized.json")


class PriorSpecReuseTest(unittest.TestCase):
    """前回Trial(KEY-PHRASE-LEVEL-SPEC-TRIAL-01)のexplanation_en仕様文
    を逐語再利用していること、前回Prompt定数が無変更のままであることを
    検証する。"""

    def test_explanation_spec_sentence_is_substring_of_prior_prompt(self):
        self.assertIn(trial.EXPLANATION_EN_SPEC_SENTENCE, prior_trial.ADVANCED_USER_TEMPLATE)

    def test_prior_advanced_template_unchanged_marker(self):
        # 前回Promptの主要文言が変更されていないことの簡易マーカー
        # (本Trialは前回scriptを一切変更しないため、importした値がこの
        # 既知の部分文字列を含むことだけを確認する)。
        self.assertIn("CEFR B1", prior_trial.ADVANCED_USER_TEMPLATE)
        self.assertIn("Choose exactly 5 Key Phrases", prior_trial.ADVANCED_USER_TEMPLATE)

    def test_max_words_matches_prior_trial_observed_ceiling(self):
        # 前回実測(KEY-PHRASE-LEVEL-SPEC-TRIAL-01_REPORT.md §7.2、最大
        # 12語・目安15語以内)を踏襲した値であることを確認する。
        self.assertEqual(trial.MAX_WORDS, 15)


class NewFactDetectionTest(unittest.TestCase):
    """新規Fact混入検出ヘルパーの単体test(決定論、API不使用)。"""

    def test_no_new_fact_when_explanation_uses_only_known_words(self):
        phrase = "recover the cost"
        source_sentence = "The aim was to recover the cost of US efforts to keep the strait safe."
        explanation = "to get back the money spent on something"
        candidates = trial._new_fact_candidates(explanation, phrase, source_sentence)
        self.assertEqual(candidates, [])

    def test_flags_unrelated_proper_noun(self):
        phrase = "sea blockade"
        source_sentence = "Reuters linked that rise to concern about a US sea blockade of Iran."
        explanation = "the act of stopping ships near Japan from entering or leaving by sea"
        candidates = trial._new_fact_candidates(explanation, phrase, source_sentence)
        self.assertIn("Japan", candidates)

    def test_flags_unrelated_number(self):
        phrase = "give back"
        source_sentence = "Brent crude futures briefly gave back some of their gains."
        explanation = "to lose 50 percent of an earlier gain"
        candidates = trial._new_fact_candidates(explanation, phrase, source_sentence)
        self.assertIn("50", candidates)

    def test_does_not_flag_words_already_in_source_sentence(self):
        phrase = "sea blockade"
        source_sentence = "Reuters linked that rise to concern about a US sea blockade of Iran."
        explanation = "the act of a US sea blockade stopping ships from entering or leaving"
        candidates = trial._new_fact_candidates(explanation, phrase, source_sentence)
        self.assertEqual(candidates, [])


class ProductionIsolationTest(unittest.TestCase):
    """本Trial scriptが既存Production Key Phrase選定モジュール・
    Production Master Audio Storeをimportしていないことを検証する
    (text pipeline側。--audio側は別途er038を通じて隔離済み)。"""

    def test_does_not_import_production_key_phrase_selection_modules(self):
        # コメント内の言及(禁止事項の説明)は許容し、実際の import 文
        # ("import <module>" / "from <module> import")だけを検出する。
        with open("er041_key_phrase_advanced_english_explanation_trial_02.py", encoding="utf-8") as f:
            lines = f.readlines()
        forbidden = [
            "er003_v1_n3_01_scaffold_generate",
            "er003_b1_p2_keywords",
            "er003_key_words_canonicalization",
            "er003_key_words_production",
        ]
        import_lines = [ln for ln in lines
                         if (ln.strip().startswith("import ") or ln.strip().startswith("from "))]
        for name in forbidden:
            for ln in import_lines:
                self.assertNotIn(name, ln,
                                  f"Production Key Phrase選定モジュール({name})をimport文で参照しています: {ln!r}")

    def test_does_not_reference_production_master_store_path_in_import_or_assignment(self):
        with open("er041_key_phrase_advanced_english_explanation_trial_02.py", encoding="utf-8") as f:
            lines = f.readlines()
        code_lines = [ln for ln in lines if not ln.strip().startswith("#")]
        hits = [ln for ln in code_lines if "er006_output/master_audio_store_01" in ln]
        self.assertEqual(hits, [], f"Production Master Store pathがコード中に出現しています: {hits}")


@unittest.skipUnless(os.path.exists(SUMMARY_PATH), "実行済みsummary.jsonが無いため実測testをskip")
class ExecutedOutputTest(unittest.TestCase):
    """実際に実行したsummary.json/match_results.jsonに対する実測検証
    (Phrase同一性・語数上限)。"""

    @classmethod
    def setUpClass(cls):
        with open(SUMMARY_PATH, encoding="utf-8") as f:
            cls.summary = json.load(f)
        with open(MATCH_RESULTS_PATH, encoding="utf-8") as f:
            cls.match_results = json.load(f)
        with open(KEYWORDS_PATH, encoding="utf-8") as f:
            cls.source_items = json.load(f)["items"]

    def test_five_items(self):
        self.assertEqual(len(self.summary["items"]), 5)

    def test_phrase_identity_a_equals_b_and_equals_source(self):
        source_phrases = {it["rank"]: it["display_phrase"] for it in self.source_items}
        for row in self.summary["items"]:
            self.assertEqual(row["phrase"], source_phrases[row["rank"]],
                              "AとBのPhraseは、Hormuzの既存確定Phraseと完全一致している必要があります")

    def test_all_explanations_within_max_words(self):
        for row in self.match_results["rows"]:
            self.assertTrue(row["explanation_within_max_words"],
                             f"{row['phrase']!r} の解説が語数上限を超えています: "
                             f"{row['explanation_word_count']}")

    def test_no_new_fact_candidates_detected_in_actual_run(self):
        for row in self.match_results["rows"]:
            self.assertEqual(row.get("possible_new_fact_tokens"), [],
                              f"{row['phrase']!r} の解説に新規Fact候補が検出されました: "
                              f"{row.get('possible_new_fact_tokens')}")


if __name__ == "__main__":
    unittest.main()
