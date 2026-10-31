# -*- coding: utf-8 -*-
"""SELECTION-UI-OCCURRENCE-COUNT-01 委任_01: 集計規則 occ-v1 の単体test(API 0・ファイル書込なし)。誤カウント防止(受入条件5)・分離句動詞・人称スロット・保留(uncertain)の挙動を固定する。
実行: .venv\\Scripts\\python.exe -m unittest docs/research/SELECTION-UI-OCCURRENCE-COUNT-01/tools/occurrence_count_01_test_01.py  (リポジトリroot=cwd)
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.getcwd())
import occurrence_count_01 as oc  # noqa: E402


def cnt(text, term, sel=None, sec="story"):
    """textを1区分として数え、(確定件数, 保留件数)を返す。"""
    o = oc.count_entry({sec: [text]}, term, sel)
    return o["counts"].get(sec, 0), o.get("uncertain", {}).get(sec, 0)


class SubstringAndBoundary(unittest.TestCase):
    def test_no_substring_match(self):
        self.assertEqual(cnt("He is within the wayside hut.", "in the way"), (0, 0))
        self.assertEqual(cnt("It gave me insight and sights.", "in sight"), (0, 0))
        self.assertEqual(cnt("Use the input away from here.", "put away"), (0, 0))
        self.assertEqual(cnt("The putaway process is slow.", "put away"), (0, 0))

    def test_hyphenated_word_is_one_token(self):
        self.assertEqual(cnt("A put-away shelf.", "put away"), (0, 0))
        self.assertEqual(cnt("An old-fashioned idea.", "old-fashioned"), (1, 0))
        self.assertEqual(cnt("An old fashioned idea.", "old-fashioned"), (0, 0))

    def test_different_phrases_are_not_confused(self):
        self.assertEqual(cnt("In a way, it works. By the way, hello.", "in the way"), (0, 0))

    def test_case_insensitive(self):
        self.assertEqual(cnt("Put Away the toys. PUT AWAY now.", "put away"), (2, 0))

    def test_no_match_across_punctuation_or_newline_or_sentence(self):
        self.assertEqual(cnt("He had to put, away the toys.", "put away"), (0, 0))
        self.assertEqual(cnt("Put. Away we go.", "put away"), (0, 0))
        o = oc.count_entry({"story": ["He wanted to put\naway the toys."]}, "put away")
        self.assertEqual(o["counts"]["story"], 0)
        self.assertEqual(cnt("He sat in—the way.", "in the way"), (0, 0))   # em dash

    def test_possessive_s_attaches_to_final_token_only(self):
        self.assertEqual(cnt("The campaign's message was clear.", "campaign"), (1, 0))
        self.assertEqual(cnt("The participant's own explanation.", "the participant's own explanation"), (1, 0))

    def test_two_occurrences_in_one_sentence(self):
        self.assertEqual(cnt("Clutter is clutter, and clutter is fine.", "clutter"), (3, 0))


class Inflection(unittest.TestCase):
    def test_regular_and_irregular(self):
        self.assertEqual(cnt("She puts away, he was putting away, they put away.", "put away"), (3, 0))
        self.assertEqual(cnt("It was left out. Leaving out is hard. She leaves out nothing. Leave out the noise.", "leave out"), (4, 0))

    def test_selection_surface_and_lemma_both_count(self):
        self.assertEqual(cnt("It applied to every household. It may apply to every household.", "apply to every household", "applied to every household"), (2, 0))

    def test_plural_last_token(self):
        self.assertEqual(cnt("Two supplements and one supplement.", "supplement"), (2, 0))

    def test_participial_adjective_not_reversed(self):
        # 'puzzling'(分詞形容詞)を puzzle(名詞) へ逆引きしない
        self.assertEqual(cnt("What a puzzle. It is puzzling.", "puzzling"), (1, 0))

    def test_reverse_lemma_is_uncertain_not_counted(self):
        # N5が基本形化していない活用済み語(bothered)の他活用形は保留(加算しない)
        self.assertEqual(cnt("It did not bother me. It bothered me.", "bothered"), (1, 1))

    def test_plural_exclude_not_reversed(self):
        self.assertEqual(cnt("The new idea. The news.", "news"), (1, 0))   # news -> new にしない


class SeparablePhrasalVerbs(unittest.TestCase):
    def test_pronoun_between_counts(self):
        self.assertEqual(cnt("Put it away. Put them away. Put this away.", "put away"), (3, 0))
        self.assertEqual(cnt("You can force it away.", "force away"), (1, 0))
        self.assertEqual(cnt("Leave it out.", "leave out"), (1, 0))

    def test_noun_phrase_between_is_uncertain(self):
        self.assertEqual(cnt("Put the books away.", "put away"), (0, 1))
        self.assertEqual(cnt("Leaving things out is fine.", "leave out"), (0, 1))

    def test_preposition_like_particle_after_pronoun_is_uncertain(self):
        self.assertEqual(cnt("Put it on the table.", "put on"), (0, 1))
        self.assertEqual(cnt("Put it on.", "put on"), (1, 0))

    def test_too_far_apart_not_matched(self):
        self.assertEqual(cnt("Put the old red books away.", "put away"), (0, 0))
        self.assertEqual(cnt("He put it on the table and walked away.", "put away"), (0, 0))

    def test_direct_adjacent_is_exact(self):
        self.assertEqual(cnt("Put away your phones.", "put away"), (1, 0))


class PersonSlots(unittest.TestCase):
    def test_closed_pronoun_set(self):
        self.assertEqual(cnt("She lost her trust in him. I lost my trust in you.", "lose one's trust in someone"), (2, 0))
        self.assertEqual(cnt("They pulled him under. He pulled me under.", "pull someone under"), (2, 0))
        self.assertEqual(cnt("It will give it up. Give this up.", "give something up"), (2, 0))

    def test_noun_phrase_slot_is_uncertain(self):
        self.assertEqual(cnt("They hold the whole team back.", "hold someone back"), (0, 1))

    def test_selection_surface_counts_even_with_np(self):
        self.assertEqual(cnt("I did not hold my son back.", "hold someone back", "hold my son back"), (1, 0))


class N5GeneralizedForms(unittest.TestCase):
    """N5(2026-10-30配線)は term=N5一般化形(例 hear someone out) / selection_phrase=本文実表現(例 hear it out) を残す。実表現の完全一致は常に確定(下限保証)。"""

    def test_n5_form_with_selection_anchor(self):
        text = "She wanted to hear it out. We heard him out. They hear the boy out."
        self.assertEqual(cnt(text, "hear someone out", "hear it out"), (2, 1))

    def test_n5_form_something_slot(self):
        self.assertEqual(cnt("Turn the usual steps around. Turn it around. Turned them around.", "turn something around", "turned the usual steps around"),
                         (2, 1))   # it/them = 確定(2)。"Turn the usual steps around" は名詞句スロット=保留(1)(実表現は過去形 turned のため exact ではない)


class DeterminerAndReference(unittest.TestCase):
    def test_a_that_this_but_not_the(self):
        self.assertEqual(cnt("We draw that line. They draw a line. Draw this line.", "draw a line"), (3, 0))
        self.assertEqual(cnt("Draw the line here.", "draw a line"), (0, 0))

    def test_contextual_determiner_removed_form(self):
        self.assertEqual(cnt("This is the sales pitch. A sales pitch is a pitch.", "sales pitch", "the sales pitch"), (2, 0))


class SectionsAndAvailability(unittest.TestCase):
    def test_sections_are_separate_and_title_excluded_from_total(self):
        secs = {"story": ["Clutter helps."], "comment": ["Is clutter bad?"], "preview": ["clutter", "clutter"], "oneline": [], "title": ["Clutter Trial"]}
        o = oc.count_entry(secs, "clutter")
        self.assertEqual(o["counts"], {"story": 1, "comment": 1, "preview": 2, "oneline": 0, "title": 1})
        self.assertEqual(o["total"], 4)

    def test_missing_section_is_unavailable_not_zero(self):
        o = oc.count_entry({"story": ["clutter"], "comment": None, "preview": None, "oneline": []}, "clutter")
        self.assertEqual(o["unavailable"], ["comment", "preview"])
        self.assertNotIn("comment", o["counts"])
        self.assertEqual(o["total"], 1)

    def test_japanese_text_has_no_english_tokens(self):
        self.assertEqual(cnt("この表現は「しまう」という意味です。", "put away"), (0, 0))

    def test_empty_term(self):
        self.assertEqual(cnt("anything", ""), (0, 0))

    def test_deterministic(self):
        t = "Put it away; put away; putting them away."
        a = oc.count_entry({"story": [t]}, "put away", with_hits=True)
        b = oc.count_entry({"story": [t]}, "put away", with_hits=True)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
