# ============================================================
# er027_key_phrase_db_hybrid_trial_02_test.py
# KEY-PHRASE-DB-HYBRID-TRIAL-02
# ============================================================
# Stage 1(機械screening)のunit test。決定論性・不規則動詞正規化・
# 見出し連結artifact除外・品詞/文脈不一致の規則化可能な除外・
# near-duplicate整理・既存final candidate 30件への回帰安全性(誤って
# 除外していないこと)を検証する。
# 実行: .venv/Scripts/python.exe -m unittest er027_key_phrase_db_hybrid_trial_02_test -v
# ============================================================

from __future__ import annotations

import json
import os
import unittest

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1


class HeadingArtifactTests(unittest.TestCase):
    def test_heading_does_not_merge_with_next_paragraph(self):
        text = "## In one line\n\nIn 2026, the market changed.\n"
        sentences = s1.tokenize_sentences_heading_aware(text)
        surface_forms = set()
        for sent in sentences:
            ngrams = ext.generate_ngrams([sent], min_n=2, max_n=2)
            surface_forms.update(ng["surface_form"] for ng in ngrams)
        self.assertNotIn("line In", surface_forms)

    def test_heading_and_body_still_tokenized_independently(self):
        text = "## Big News Today\n\nSomething happened here.\n"
        sentences = s1.tokenize_sentences_heading_aware(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], ["Big", "News", "Today"])


class IrregularVerbRescueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_gave_back_is_rescued_as_give_back(self):
        ngram = {"n": 2, "start": 0, "surface_tokens": ["gave", "back"], "surface_form": "gave back"}
        core = ext.match_candidate_against_group1(ngram, self.dbs)
        self.assertEqual(core["db_match_count"], 0)  # 規則語尾ロジックでは検出できない(既知の検出漏れ)
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertTrue(rescued["irregular_verb_rescue"])
        self.assertGreater(rescued["db_match_count"], 0)
        self.assertIn("phrasal_verb", rescued["db_categories"])

    def test_went_on_is_rescued_as_go_on(self):
        ngram = {"n": 2, "start": 0, "surface_tokens": ["went", "on"], "surface_form": "went on"}
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertTrue(rescued["irregular_verb_rescue"])
        self.assertEqual(rescued["unit_type"], "phrasal_verb")

    def test_took_off_is_rescued_as_take_off(self):
        ngram = {"n": 2, "start": 0, "surface_tokens": ["took", "off"], "surface_form": "took off"}
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertTrue(rescued["irregular_verb_rescue"])

    def test_taken_back_is_rescued_as_take_back(self):
        ngram = {"n": 2, "start": 0, "surface_tokens": ["Taken", "Back"], "surface_form": "Taken Back"}
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertTrue(rescued["irregular_verb_rescue"])

    def test_already_matched_candidate_is_not_touched_by_rescue(self):
        """規則語尾で既に一致している候補は、rescueロジックで上書きしない
        (副作用の少なさを保証する回帰テスト)。"""
        ngram = {"n": 2, "start": 0, "surface_tokens": ["pulled", "back"], "surface_form": "pulled back"}
        core = ext.match_candidate_against_group1(ngram, self.dbs)
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertFalse(rescued["irregular_verb_rescue"])
        self.assertEqual(core["matched_dbs"], rescued["matched_dbs"])

    def test_made_through_is_not_falsely_rescued(self):
        """"made through"は"make through"としてDBに一致しない(既存REPORT
        §13.2で確認済みの非該当ケース)。誤ってrescueしないことを確認する。"""
        ngram = {"n": 2, "start": 0, "surface_tokens": ["made", "through"], "surface_form": "made through"}
        rescued = s1.match_candidate_with_irregular_rescue(ngram, self.dbs)
        self.assertFalse(rescued["irregular_verb_rescue"])
        self.assertEqual(rescued["db_match_count"], 0)


class ContextMismatchRuleTests(unittest.TestCase):
    def test_kind_of_excluded_after_what(self):
        sentence = ["What", "kind", "of", "bag", "is", "that"]
        rule = s1.detect_context_mismatch(["kind", "of"], "idiom", sentence, 1)
        self.assertEqual(rule, "preceded_by_determiner_immediate")

    def test_back_in_excluded_after_copula(self):
        sentence = ["they", "are", "back", "in", "fashion"]
        rule = s1.detect_context_mismatch(["back", "in"], "phrasal_verb", sentence, 2)
        self.assertEqual(rule, "preceded_by_copula_ambiguous_particle")

    def test_you_think_excluded_as_subject_pronoun_fragment(self):
        sentence = ["Do", "you", "think", "so"]
        rule = s1.detect_context_mismatch(["you", "think"], "idiom", sentence, 1)
        self.assertEqual(rule, "subject_pronoun_verb_fragment")

    def test_say_what_excluded_as_wh_complement(self):
        sentence = ["It", "did", "not", "say", "what", "law", "would", "support", "it"]
        rule = s1.detect_context_mismatch(["say", "what"], "idiom", sentence, 3)
        self.assertEqual(rule, "wh_complement_clause_continuation")

    def test_happened_on_excluded_as_temporal_pp(self):
        sentence = ["the", "movement", "happened", "on", "the", "same", "day"]
        rule = s1.detect_context_mismatch(["happened", "on"], "phrasal_verb", sentence, 2)
        self.assertEqual(rule, "temporal_prepositional_phrase")

    def test_sits_on_the_throne_is_not_excluded(self):
        """"sits on"(小物語彙trial final candidate)がR6(temporal_pp)で
        誤って除外されないことを確認する回帰テスト("throne"は時間表現
        ではない)。"""
        sentence = ["one", "size", "alone", "sits", "on", "the", "throne"]
        rule = s1.detect_context_mismatch(["sits", "on"], "phrasal_verb", sentence, 3)
        self.assertIsNone(rule)


class RegressionAgainstKnownGoodCandidatesTests(unittest.TestCase):
    """KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01の6本文final_selection.json
    (final_A、30件)を、本Trialの新しい除外ルール(context_mismatch)が
    誤って除外していないことを確認する回帰テスト。設計段階で
    "pulled back"/"rolled back"/"standing behind"/"take over"が広い
    windowルールにより誤って除外される問題が実際に発見されたため、
    このテストで再発を防ぐ。"""

    KNOWN_GOOD_CANDIDATES = {
        "meta_a2": ["pulled back", "take over", "stepped out", "call center", "speaks for"],
        "meta_b1b": ["rolled back", "turned out", "standing behind", "take over", "speaks for"],
        "hormuz_a2": ["brent crude", "center stage", "pulled back", "by trade", "passing through"],
        "hormuz_b1b": ["brent crude", "center stage", "pulled back", "by trade", "passing through"],
        "small_bag_a2": ["catch the eye", "taking over"],
        "small_bag_b1b": ["sits on", "all over"],
    }

    ARTICLE_PATHS = {
        "meta_a2": "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md",
        "meta_b1b": "er019_output/family_x_b3_production_wiring_01/run_01/b1b/article.md",
        "hormuz_a2": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md",
        "hormuz_b1b": "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md",
        "small_bag_a2": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/a2/article.md",
        "small_bag_b1b": "er019_output/family_x_b3_diversity_trial_01/small_bag/run_02/b1b/article.md",
    }

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_no_known_good_candidate_is_excluded_by_context_mismatch_rules(self):
        for article_key, path in self.ARTICLE_PATHS.items():
            if not os.path.exists(path):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            result = s1.run_stage1_for_article(text, self.dbs)
            excluded_canonicals = {c["canonical_form"] for c in result["context_mismatch_excluded"]}
            for known_good in self.KNOWN_GOOD_CANDIDATES.get(article_key, []):
                # brent crude/call centerのようなmultiword_term系はWiktionary
                # targeted lookup(別ステップ)で見つかるためstage1単体では
                # phrase_survivorsに現れない場合がある。ここでは
                # 「誤って除外していないこと」だけを厳密に確認する
                # (見つからないこと自体は別のstop条件チェックで扱う)。
                self.assertNotIn(known_good, excluded_canonicals,
                                 f"{article_key}: 既知の良い候補'{known_good}'が"
                                 "context_mismatch_excludedに含まれています(回帰)")


class DedupeAndRepeatedNounTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_merge_near_duplicates_keeps_higher_db_match_count(self):
        candidates = [
            {"canonical_form": "pulled back", "unit_type": "phrasal_verb", "db_match_count": 1, "n": 2},
            {"canonical_form": "pull back", "unit_type": "phrasal_verb", "db_match_count": 2, "n": 2},
        ]
        merged = s1.merge_near_duplicates(candidates)
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["db_match_count"], 2)
        self.assertIn("pulled back", merged[0]["observed_surface_variants"])

    def test_repeated_compound_noun_detects_contract_worker(self):
        sentences = [
            ["The", "contract", "worker", "spoke"],
            ["Another", "contract", "workers", "group", "joined"],
        ]
        results = s1.find_repeated_compound_noun_candidates(sentences, self.dbs, min_repetition=2)
        canonicals = {r["canonical_form"] for r in results}
        self.assertTrue(any("contract worker" in c for c in canonicals))

    def test_repeated_compound_noun_rejects_verb_adverb_artifact(self):
        """"clearly telling"のような副詞+動詞の定型artifactは、CEFR-Jの
        pos情報により重要名詞句候補から除外されることを確認する。"""
        sentences = [
            ["Meta", "is", "clearly", "telling", "users", "now"],
            ["It", "is", "clearly", "telling", "users", "again"],
        ]
        results = s1.find_repeated_compound_noun_candidates(sentences, self.dbs, min_repetition=2)
        canonicals = {r["canonical_form"] for r in results}
        self.assertNotIn("clearly telling", canonicals)

    def test_repeated_compound_noun_does_not_require_group1_db_membership(self):
        """"blockade"はgroup1 word DB(CEFR-J/NGSL)に存在しないが、wordfreq
        で実在語と判定できれば重要名詞句候補として拾えることを確認する
        (group1 DBの被覆範囲外を補う本機構の目的そのもの)。"""
        sentences = [
            ["a", "sea", "blockade", "began"],
            ["the", "sea", "blockade", "ended"],
        ]
        results = s1.find_repeated_compound_noun_candidates(sentences, self.dbs, min_repetition=2)
        canonicals = {r["canonical_form"] for r in results}
        self.assertIn("sea blockade", canonicals)


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_run_stage1_for_article_is_deterministic(self):
        text = "Meta has pulled back the human concierge feature. Before AI speaks for us, we need to know."
        r1 = s1.run_stage1_for_article(text, self.dbs)
        r2 = s1.run_stage1_for_article(text, self.dbs)
        self.assertEqual([c["canonical_form"] for c in r1["phrase_survivors"]],
                         [c["canonical_form"] for c in r2["phrase_survivors"]])
        self.assertEqual([c["canonical_form"] for c in r1["word_survivors"]],
                         [c["canonical_form"] for c in r2["word_survivors"]])

    def test_build_shortlist_respects_target_without_forcing_exact_count(self):
        stage1_result = {
            "phrase_survivors": [{"canonical_form": f"p{i}", "unit_type": "idiom"} for i in range(3)],
            "important_noun_candidates": [{"canonical_form": "sea blockade"}],
            "word_survivors": [{"canonical_form": f"w{i}"} for i in range(50)],
        }
        info = s1.build_shortlist(stage1_result, target_total=20, phrase_cap=15, word_min=5)
        self.assertEqual(info["phrase_included_count"], 3)
        self.assertEqual(info["important_noun_included_count"], 1)
        self.assertGreaterEqual(info["word_included_count"], 5)
        self.assertLessEqual(info["shortlist_total_count"], 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
