# ============================================================
# er029_key_phrase_db_hybrid_trial_04_test.py
# KEY-PHRASE-DB-HYBRID-TRIAL-04
# ============================================================
# 実行: .venv/Scripts/python.exe -m unittest er029_key_phrase_db_hybrid_trial_04_test -v
# ============================================================

from __future__ import annotations

import os
import unittest

import er023_key_phrase_db_ingest as ing
import er028_key_phrase_db_hybrid_trial_03_run as base
import er029_key_phrase_db_hybrid_trial_04_run as run4
import er029_key_phrase_db_hybrid_trial_04_stage1 as s1v4


class FixASentenceSegmentationQuoteAwareTests(unittest.TestCase):
    """Fix A: 終端句読点の直後に閉じ引用符が続く会話文境界を正しく分割
    できること(twins_a2実データ由来のfixture、Trial-03 REPORT §15-3で
    発見したINVALID原因の再現・修正確認)。"""

    def test_consecutive_quoted_utterances_split_into_separate_units(self):
        text = ('"Today is your audition," Echo said. "You asked me to wake you." '
                '"I did not." "You did not remember asking." Mara sat up. '
                'For ten years, she had given Echo almost everything.')
        units = s1v4.build_sentence_units_v4(text)
        raw_texts = [u["raw_text"] for u in units]
        self.assertIn("You asked me to wake you", raw_texts)
        self.assertIn("I did not", raw_texts)
        self.assertIn("You did not remember asking", raw_texts)
        self.assertIn("Mara sat up", raw_texts)
        # 旧regex(引用符非対応)が作っていた結合ブロックが残っていないこと
        merged_blob = "You asked me to wake you." + " " + '"I did not.'
        self.assertNotIn(merged_blob, raw_texts)

    def test_no_leading_or_trailing_bare_quote_left_in_unit(self):
        text = '"Echo?" she said. "It comes from your memories," Echo said.'
        units = s1v4.build_sentence_units_v4(text)
        for u in units:
            self.assertFalse(u["raw_text"].startswith('"'))
            self.assertFalse(u["raw_text"].endswith('"'))

    def test_ordinary_declarative_sentences_unaffected(self):
        text = "The chart pulled back, but only briefly. It recovered later."
        units = s1v4.build_sentence_units_v4(text)
        raw_texts = [u["raw_text"] for u in units]
        self.assertIn("The chart pulled back, but only briefly", raw_texts)
        self.assertIn("It recovered later", raw_texts)

    def test_heading_does_not_merge_into_next_sentence_raw_text(self):
        text = "## Big News Today\n\nSomething happened here."
        units = s1v4.build_sentence_units_v4(text)
        self.assertEqual(len(units), 2)
        self.assertEqual(units[0]["raw_text"], "Big News Today")

    def test_mid_sentence_attribution_not_split(self):
        # 文中の帰属句("X," she said, "Y")は1文のまま(コンマでは分割しない)
        text = '"Echo," she said, "start the first note." Her fingers began to move.'
        units = s1v4.build_sentence_units_v4(text)
        raw_texts = [u["raw_text"] for u in units]
        self.assertTrue(any("Echo" in t and "start the first note" in t for t in raw_texts))


class FixBRareSingleWordCandidateTests(unittest.TestCase):
    """Fix B: CEFR-J/NGSL外・1-tokenの重要語(grogginess/self-awakening)が
    候補化されること(positive)、固有名詞・会話タグ・一般語・非ASCII文字
    起因のトークナイザ破損断片("minaudi")はノイズとして抑制されること
    (negative)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_grogginess_and_self_awakening_selected_as_candidates(self):
        text = ("Researchers also study a related ability called self-awakening: "
                "waking near a planned time without an outside signal. "
                "Waking from deep sleep is linked with stronger grogginess "
                "than waking from lighter sleep.")
        units = s1v4.build_sentence_units_v4(text)
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertIn("grogginess", keys)
        self.assertIn("self-awakening", keys)

    def test_proper_noun_dialogue_tag_excluded_no_lowercase_occurrence(self):
        # "Echo"は常に大文字始まりで出現する(会話タグ、固有名詞)ため対象外
        text = '"Echo," she said. Echo knew the songs she played.'
        units = s1v4.build_sentence_units_v4(text)
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertNotIn("echo", keys)

    def test_closed_class_and_short_words_excluded(self):
        text = "The cat sat on the mat and the dog ran to it."
        units = s1v4.build_sentence_units_v4(text)
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertEqual(keys, set())

    def test_frequency_unknown_candidate_dropped_without_wiktionary_confirmation(self):
        # "minaudi"相当(非ASCII文字混じり語がASCII限定トークナイザで壊れた
        # 断片を模したfixture、wordfreq頻度データが皆無=reason
        # "frequency_unknown"、Wiktionary未確認なら除外されること)。
        units = [{"tokens": ["a", "minaudi", "bag"], "raw_text": "a minaudi bag"}]
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        reasons = {k: r for k, e, r in selected}
        self.assertEqual(reasons.get("minaudi"), "frequency_unknown")
        built = s1v4.build_rare_single_word_evidences(selected, {"minaudi": False})
        self.assertNotIn("minaudi", [ev["canonical_form"] for ev in built["evidences"]])
        self.assertIn("minaudi", built["dropped_unconfirmed_frequency_unknown"])

    def test_frequency_unknown_candidate_kept_when_wiktionary_confirms(self):
        units = [{"tokens": ["a", "minaudi", "bag"], "raw_text": "a minaudi bag"}]
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        built = s1v4.build_rare_single_word_evidences(selected, {"minaudi": True})
        self.assertIn("minaudi", [ev["canonical_form"] for ev in built["evidences"]])

    def test_morphology_reason_candidate_kept_regardless_of_wiktionary_result(self):
        units = [{"tokens": ["the", "self-awakening", "process"], "raw_text": "the self-awakening process"}]
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        built = s1v4.build_rare_single_word_evidences(selected, {"self-awakening": False})
        self.assertIn("self-awakening", [ev["canonical_form"] for ev in built["evidences"]])

    def test_db_matched_words_not_selected(self):
        # CEFR-J/NGSLに既に一致する語("important"等)は対象外
        text = "This is an important discovery about important things."
        units = s1v4.build_sentence_units_v4(text)
        selected = s1v4.select_rare_single_word_candidates(units, self.dbs, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertNotIn("important", keys)


class Stage1V4IntegrationTests(unittest.TestCase):
    """run_stage1_for_article_v4がer028(v3)の既存挙動(bug A/B/C修正済み
    のexclusion判定・shortlist組み立て)を壊していないことの回帰。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_run_stage1_for_article_v4_is_deterministic(self):
        text = "Meta has pulled back the human concierge feature. Before AI speaks for us, we need to know."
        r1 = s1v4.run_stage1_for_article_v4(text, self.dbs)
        r2 = s1v4.run_stage1_for_article_v4(text, self.dbs)
        self.assertEqual([c["canonical_form"] for c in r1["phrase_survivors"]],
                         [c["canonical_form"] for c in r2["phrase_survivors"]])

    def test_bug_a_discontinuous_phrasal_verb_still_excluded_in_v4(self):
        text = "The worker was pushing large bags out of the truck."
        r = s1v4.run_stage1_for_article_v4(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["phrase_survivors"]}
        self.assertNotIn("bags out", canonicals)

    def test_bug_c_possessive_noise_stripped_in_v4(self):
        text = "The user's plan changed after the meeting."
        r = s1v4.run_stage1_for_article_v4(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["word_survivors"]}
        self.assertNotIn("user's", canonicals)


class NoFullArticleBodyInPromptV4Tests(unittest.TestCase):
    """article全文がLLM inputへ入っていないことの構造的assert(Fix A/B
    追加後も維持されていること)。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_lightweight_prompt_v4_does_not_contain_full_article_body(self):
        path = "er019_output/family_x_b3_production_wiring_01/run_01/a2/article.md"
        if not os.path.exists(path):
            self.skipTest("article fixture not present")
        article_text = open(path, encoding="utf-8").read()
        title = base.extract_article_title(article_text)
        s1r = run4.run_stage1_and_shortlist_v4(article_text, self.dbs, title)
        static_instructions = base.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())
        message = run4.build_lightweight_user_message_v4(
            title, s1r["shortlist_info"], s1r["shortlist_info"]["sentence_reference"], static_instructions)
        base.assert_no_full_article_body(message, article_text)
        self.assertLess(len(message), len(article_text) + 6000)

    def test_lightweight_prompt_v4_does_not_contain_full_article_body_dialogue_heavy(self):
        path = "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt"
        if not os.path.exists(path):
            self.skipTest("article fixture not present")
        article_text = open(path, encoding="utf-8").read()
        s1r = run4.run_stage1_and_shortlist_v4(article_text, self.dbs, "Digital Twins")
        static_instructions = base.extract_static_instructions(
            __import__("er003_b1_p2_keywords").load_prompt_template())
        message = run4.build_lightweight_user_message_v4(
            "Digital Twins", s1r["shortlist_info"], s1r["shortlist_info"]["sentence_reference"],
            static_instructions)
        base.assert_no_full_article_body(message, article_text)


class TwinsA2SourceSentenceStructuralFixtureTests(unittest.TestCase):
    """Trial-03 REPORT §15-3で発見したtwins_a2 INVALID原因(source_sentence
    がB2本文に存在しない)の元となったsentence unitが、Fix A適用後は
    validatorのsubstring照合方式(空白正規化・小文字化のみ)と整合する
    クリーンな文字列になっていることの確認。"""

    def test_sat_up_sentence_is_clean_substring_of_article(self):
        path = "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt"
        if not os.path.exists(path):
            self.skipTest("article fixture not present")
        article_text = open(path, encoding="utf-8").read()
        units = s1v4.build_sentence_units_v4(article_text)
        raw_texts = [u["raw_text"] for u in units]
        self.assertIn("Mara sat up", raw_texts)
        self.assertIn("You asked me to wake you", raw_texts)
        # 修正前の結合ブロック(4発話が1個のunitへ結合)が残っていないこと
        self.assertFalse(any(t.count('"') >= 2 and "sat up" in t for t in raw_texts))


if __name__ == "__main__":
    unittest.main()
