# ============================================================
# er028_key_phrase_db_hybrid_trial_03_test.py
# KEY-PHRASE-DB-HYBRID-TRIAL-03
# ============================================================
# 実行: .venv/Scripts/python.exe -m unittest er028_key_phrase_db_hybrid_trial_03_test -v
# ============================================================

from __future__ import annotations

import os
import unittest

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing
import er027_key_phrase_db_hybrid_trial_02_stage1 as s1v2
import er028_key_phrase_db_hybrid_trial_03_run as run3
import er028_key_phrase_db_hybrid_trial_03_stage1 as s1v3


class BugAAdjectivePrecedesDiscontinuousPhrasalVerbTests(unittest.TestCase):
    """bug A: discontinuous phrasal verb false positive("large bags out"->
    "bags out"、"an unexpected move in oil prices"->"move in"、"a short
    play in three acts"->"play in")の一般化除外(positive)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_bags_out_excluded_after_adjective_large(self):
        sentence = ["pushing", "large", "bags", "out"]
        rule = s1v3.detect_context_mismatch_v3(
            ["bags", "out"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 2, self.dbs["cefr_j"])
        self.assertEqual(rule, "preceded_by_attributive_adjective_np_misparse")

    def test_move_in_excluded_after_adjective_unexpected(self):
        sentence = ["was", "an", "unexpected", "move", "in", "oil", "prices"]
        rule = s1v3.detect_context_mismatch_v3(
            ["move", "in"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertEqual(rule, "preceded_by_attributive_adjective_np_misparse")

    def test_play_in_excluded_after_adjective_short(self):
        sentence = ["like", "a", "short", "play", "in", "three", "acts"]
        rule = s1v3.detect_context_mismatch_v3(
            ["play", "in"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertEqual(rule, "preceded_by_attributive_adjective_np_misparse")


class BugANoOverExclusionRegressionTests(unittest.TestCase):
    """bug A修正が既存の良い候補(pull back/roll back/take over等)を
    壊さないことの回帰(negative、既存er027 KNOWN_GOOD_CANDIDATESの実際の
    前後文脈から抽出)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_pulled_back_after_noun_subject_not_excluded(self):
        sentence = ["but", "the", "chart", "pulled", "back", "only", "briefly"]
        rule = s1v3.detect_context_mismatch_v3(
            ["pulled", "back"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_rolled_back_after_auxiliary_been_not_excluded(self):
        sentence = ["feature", "has", "been", "rolled", "back", "for", "now"]
        rule = s1v3.detect_context_mismatch_v3(
            ["rolled", "back"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_standing_behind_after_auxiliary_was_not_excluded(self):
        sentence = ["a", "human", "was", "standing", "behind", "the", "sign"]
        rule = s1v3.detect_context_mismatch_v3(
            ["standing", "behind"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_take_over_after_noun_subject_not_excluded(self):
        sentence = ["having", "a", "person", "take", "over", "is", "not", "bad"]
        rule = s1v3.detect_context_mismatch_v3(
            ["take", "over"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_sits_on_after_predicative_only_adjective_alone_not_excluded(self):
        """"alone"は述語専用形容詞(predicative-only)であり、"size alone"の
        ようにfloating用法で使われるため、直後の動詞候補まで誤って
        excludeしてはならない(既存の良い候補"sits on"の回帰)。"""
        sentence = ["one", "size", "alone", "sits", "on", "the", "throne"]
        rule = s1v3.detect_context_mismatch_v3(
            ["sits", "on"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_speaks_for_after_unknown_proper_noun_not_excluded(self):
        sentence = ["before", "ai", "speaks", "for", "us"]
        rule = s1v3.detect_context_mismatch_v3(
            ["speaks", "for"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 2, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_stood_behind_after_noun_sense_human_not_excluded(self):
        """"human"はCEFR-Jで代表品詞が形容詞タグだが、"A human stood
        behind..."ではsubject名詞として使われている。過去形候補
        ("stood")は形態論上ほぼ確実に動詞であり、名詞句誤読の余地が
        ないため除外しない(実データregressionで発見、2026-09-27)。"""
        sentence = ["a", "human", "stood", "behind", "the", "sign"]
        rule = s1v3.detect_context_mismatch_v3(
            ["stood", "behind"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 2, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_pulled_back_after_adverb_sense_only_not_excluded(self):
        """"only"はCEFR-Jで代表品詞が形容詞タグだが、"the chart only
        pulled back briefly"では副詞として使われている。規則過去形
        ("-ed"語尾、"pulled")のため除外しない(実データregressionで
        発見、2026-09-27)。"""
        sentence = ["the", "chart", "only", "pulled", "back", "briefly"]
        rule = s1v3.detect_context_mismatch_v3(
            ["pulled", "back"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 3, self.dbs["cefr_j"])
        self.assertIsNone(rule)

    def test_existing_er027_rules_still_apply_unchanged(self):
        """既存6ルール(er027)がv3でも無変更のまま機能することを確認する。"""
        sentence = ["they", "are", "back", "in", "fashion"]
        rule = s1v3.detect_context_mismatch_v3(
            ["back", "in"], ext.UNIT_TYPE_PHRASAL_VERB, sentence, 2, self.dbs["cefr_j"])
        self.assertEqual(rule, "preceded_by_copula_ambiguous_particle")


class BugBWiktionaryMultiwordNounPhrasePlausibilityTests(unittest.TestCase):
    """bug B: even though/other side/other endのような function-word中心・
    conjunction/discourse系・generic fragmentが重要noun phraseバケットへ
    誤混入しないことの一般化修正(既存の品詞判定[_is_plausible_noun_
    component]を、Wiktionary multiword hitにも後付けで適用する)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def _hit(self, surface):
        return {
            "surface_form": surface, "canonical_form": surface.lower(), "n": len(surface.split()),
            "matched_dbs": ["wiktionary"], "db_match_count": 1,
            "db_categories": ["multiword_term"], "unit_type": ext.UNIT_TYPE_PHRASE,
            "cefr_level": None, "important_noun_phrase_candidate": True,
        }

    def test_even_though_demoted_from_important_noun_phrase(self):
        refined = s1v3.refine_multiword_hits_noun_phrase_flag([self._hit("even though")], self.dbs["cefr_j"])
        self.assertFalse(refined[0]["important_noun_phrase_candidate"])

    def test_other_side_demoted_from_important_noun_phrase(self):
        refined = s1v3.refine_multiword_hits_noun_phrase_flag([self._hit("other side")], self.dbs["cefr_j"])
        self.assertFalse(refined[0]["important_noun_phrase_candidate"])

    def test_other_end_demoted_from_important_noun_phrase(self):
        refined = s1v3.refine_multiword_hits_noun_phrase_flag([self._hit("other end")], self.dbs["cefr_j"])
        self.assertFalse(refined[0]["important_noun_phrase_candidate"])

    def test_call_center_stays_important_noun_phrase(self):
        """既存の良い重要名詞句候補(call center)を過剰に落とさないことの
        回帰(bug D「重要候補を落とす方向への過剰最適化禁止」対応)。"""
        refined = s1v3.refine_multiword_hits_noun_phrase_flag([self._hit("call center")], self.dbs["cefr_j"])
        self.assertTrue(refined[0]["important_noun_phrase_candidate"])

    def test_candidate_not_dropped_only_demoted(self):
        refined = s1v3.refine_multiword_hits_noun_phrase_flag([self._hit("even though")], self.dbs["cefr_j"])
        self.assertEqual(len(refined), 1)
        self.assertEqual(refined[0]["surface_form"], "even though")


class BugCPossessiveNoiseStrippingTests(unittest.TestCase):
    def _word(self, surface):
        return {"surface_form": surface, "canonical_form": surface.lower(), "n": 1,
                "unit_type": ext.UNIT_TYPE_WORD, "matched_dbs": ["cefr_j"], "db_match_count": 1,
                "db_categories": [], "cefr_level": "A2"}

    def test_users_possessive_stripped_to_user(self):
        cleaned = s1v3.strip_possessive_noise_from_word_survivors([self._word("user's")])
        self.assertEqual(cleaned[0]["canonical_form"], "user")
        self.assertTrue(cleaned[0]["possessive_noise_stripped"])

    def test_charts_possessive_stripped_to_chart(self):
        cleaned = s1v3.strip_possessive_noise_from_word_survivors([self._word("chart's")])
        self.assertEqual(cleaned[0]["canonical_form"], "chart")

    def test_seasons_possessive_stripped_to_season(self):
        cleaned = s1v3.strip_possessive_noise_from_word_survivors([self._word("season's")])
        self.assertEqual(cleaned[0]["canonical_form"], "season")

    def test_non_possessive_word_untouched(self):
        cleaned = s1v3.strip_possessive_noise_from_word_survivors([self._word("admits")])
        self.assertEqual(cleaned[0]["canonical_form"], "admits")
        self.assertNotIn("possessive_noise_stripped", cleaned[0])

    def test_dedupe_when_base_form_already_present(self):
        cleaned = s1v3.strip_possessive_noise_from_word_survivors(
            [self._word("chart"), self._word("chart's")])
        canonicals = [c["canonical_form"] for c in cleaned]
        self.assertEqual(canonicals, ["chart"])


class ImportantTermsPreservedRegressionTests(unittest.TestCase):
    """bug D: false positive削減のために重要候補(contract workers/sea
    blockade/Brent crude)を落とす方向へ過剰最適化していないことの回帰。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_contract_worker_survives_v3_stage1(self):
        text = ("The contract worker spoke to us. Another contract workers group joined "
                "the call later that day.")
        result = s1v3.run_stage1_for_article_v3(text, self.dbs)
        canonicals = {c["canonical_form"] for c in result["important_noun_candidates"]}
        self.assertTrue(any("contract worker" in c for c in canonicals))

    def test_sea_blockade_survives_v3_stage1(self):
        text = "A sea blockade began this week. The sea blockade has not ended yet."
        result = s1v3.run_stage1_for_article_v3(text, self.dbs)
        canonicals = {c["canonical_form"] for c in result["important_noun_candidates"]}
        self.assertIn("sea blockade", canonicals)


class SentenceUnitsAndContextTests(unittest.TestCase):
    def test_build_sentence_units_preserves_punctuation(self):
        text = "## A Heading\n\nThe chart pulled back, but only briefly. It recovered later."
        units = s1v3.build_sentence_units(text)
        joined_raw = " ".join(u["raw_text"] for u in units)
        self.assertIn("pulled back, but only briefly", joined_raw)

    def test_heading_does_not_merge_into_next_sentence_raw_text(self):
        text = "## Big News Today\n\nSomething happened here."
        units = s1v3.build_sentence_units(text)
        self.assertEqual(len(units), 2)
        self.assertEqual(units[0]["raw_text"], "Big News Today")

    def test_attach_compact_context_assigns_sentence_id_and_occurrence_count(self):
        units = [
            {"tokens": ["The", "chart", "pulled", "back"], "raw_text": "The chart pulled back"},
            {"tokens": ["It", "pulled", "back", "again"], "raw_text": "It pulled back again"},
        ]
        candidate = {"canonical_form": "pull back", "surface_form": "pulled back",
                     "observed_surface_variants": ["pulled back"], "unit_type": "phrasal_verb"}
        result = s1v3.attach_compact_context([candidate], units)
        enriched = result["shortlist"][0]
        self.assertEqual(enriched["occurrence_count_in_article"], 2)
        self.assertEqual(enriched["context_sentence_id"], "S1")
        self.assertIn("S1", result["sentence_reference"])
        self.assertEqual(result["sentence_reference"]["S1"], "The chart pulled back")


class NoFullArticleBodyInPromptTests(unittest.TestCase):
    """article全文がLLM inputへ入っていないことの構造的assert(連続100語
    一致が無いこと)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_lightweight_prompt_does_not_contain_full_article_body(self):
        path = "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md"
        if not os.path.exists(path):
            self.skipTest("article fixture not present")
        article_text = open(path, encoding="utf-8").read()
        s1r = run3.run_stage1_and_shortlist_v3(article_text, self.dbs)
        static_instructions = run3.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())
        title = run3.extract_article_title(article_text)
        message = run3.build_lightweight_user_message(
            title, s1r["shortlist_info"], s1r["shortlist_info"]["sentence_reference"], static_instructions)
        # 例外が飛ばないこと自体がassertion(飛べばAssertionError)
        run3.assert_no_full_article_body(message, article_text)
        self.assertLess(len(message), len(article_text) + 4000)

    def test_extract_static_instructions_removes_article_placeholder(self):
        template = "instructions here\n\n【B1 Article】\n{approved_b1_article}\n"
        result = run3.extract_static_instructions(template)
        self.assertNotIn("{approved_b1_article}", result)
        self.assertNotIn("【B1 Article】", result)
        self.assertIn("instructions here", result)


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_run_stage1_for_article_v3_is_deterministic(self):
        text = "Meta has pulled back the human concierge feature. Before AI speaks for us, we need to know."
        r1 = s1v3.run_stage1_for_article_v3(text, self.dbs)
        r2 = s1v3.run_stage1_for_article_v3(text, self.dbs)
        self.assertEqual([c["canonical_form"] for c in r1["phrase_survivors"]],
                         [c["canonical_form"] for c in r2["phrase_survivors"]])
        self.assertEqual([c["canonical_form"] for c in r1["word_survivors"]],
                         [c["canonical_form"] for c in r2["word_survivors"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
