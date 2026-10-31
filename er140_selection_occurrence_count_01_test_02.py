# -*- coding: utf-8 -*-
"""er140_selection_occurrence_count_01 の Opus必須M1-M3・推奨の単体test(API 0・一時ディレクトリ以外へ書かない)。
SELECTION-UI-OCCURRENCE-COUNT-01 委任_02。M1=除外表(build->building等)・M2=前置詞兼用の不変化詞・M3=先頭be/have/do・縮約's・sb/sth・人名スロット・S/U和集合・
er105活用表snapshot・a2日本語本文・行単位unit(loader)・export自己検査用の厳密一致件数。
実行: .venv\\Scripts\\python.exe er140_selection_occurrence_count_01_test_02.py
"""
import hashlib
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import er140_selection_occurrence_count_01 as oc  # noqa: E402
import er140_selection_occurrence_sections_01 as sl  # noqa: E402


def cnt(text, term, sel=None, sec="story"):
    """textを1区分として数え、(確定件数, 保留件数)を返す。"""
    o = oc.count_entry({sec: [text]}, term, sel)
    return o["counts"].get(sec, 0), o.get("uncertain", {}).get(sec, 0)


class M1ExclusionTables(unittest.TestCase):
    """Opus M1: 前方活用生成に er105 の除外表を適用。1語Wordでは該当形を保留(確定にしない)。"""

    def test_build_building_is_uncertain(self):
        self.assertEqual(cnt("The building was tall. They build fast. It was built.", "build"), (2, 1))

    def test_lie_lay_is_uncertain(self):
        self.assertEqual(cnt("She lay down. He lies. It has lain there.", "lie"), (2, 1))

    def test_good_goods_is_uncertain(self):
        self.assertEqual(cnt("The goods arrived. A good idea.", "good"), (1, 1))

    def test_past_that_is_another_word_is_uncertain_for_single_word(self):
        self.assertEqual(cnt("I saw it. We see it.", "see"), (1, 1))

    def test_phrasal_verb_left_out_stays_confirmed(self):
        # 複数語の句動詞は不変化詞が用法を決める。left out <- leave out は確定のまま
        self.assertEqual(cnt("He left out the part. She leaves out data.", "leave out"), (2, 0))

    def test_phrase_plural_exclude_and_completion_exclude_are_uncertain(self):
        self.assertEqual(cnt("It is for goods. It is for good.", "for good"), (1, 1))
        self.assertEqual(cnt("They lay down. They lie down. They lain down.", "lie down"), (2, 1))

    def test_exact_selection_surface_is_always_confirmed(self):
        # 選定表層(S)そのものは除外表に該当しても確定(実表現の完全一致=下限保証)
        self.assertEqual(cnt("The building is old.", "building"), (1, 0))
        self.assertEqual(cnt("The goods arrived.", "goods"), (1, 0))
        self.assertEqual(cnt("They lay down.", "lay down"), (1, 0))


class M2PrepositionalParticles(unittest.TestCase):
    """Opus M2: 前置詞兼用の不変化詞の分離形は、直後が句読点・文末以外なら保留。"""

    def test_put_it_in_boxes_is_uncertain(self):
        self.assertEqual(cnt("Put it in boxes.", "put in"), (0, 1))

    def test_put_it_in_at_clause_end_is_confirmed(self):
        self.assertEqual(cnt("Put it in. Put it in, then. Put it in", "put in"), (3, 0))

    def test_over_through_around_along_down_up_off(self):
        for p in ("over", "through", "around", "along", "down", "up", "off", "on"):
            self.assertEqual(cnt("Put it %s the table." % p, "put " + p), (0, 1), p)
            self.assertEqual(cnt("Put it %s." % p, "put " + p), (1, 0), p)

    def test_non_prepositional_particle_unaffected(self):
        self.assertEqual(cnt("Put it away tonight.", "put away"), (1, 0))
        self.assertEqual(cnt("Put it back soon.", "put back"), (1, 0))

    def test_longer_pattern_is_disambiguated_by_itself(self):
        self.assertEqual(cnt("Put it on hold today.", "put on hold"), (1, 0))


class M3FunctionVerbHead(unittest.TestCase):
    """Opus M3: 先頭の be/have/do を活用対象にする。"""

    def test_be_forms(self):
        self.assertEqual(cnt("It was in the way. They are in the way. He is in the way.", "be in the way"), (3, 0))

    def test_have_do_forms(self):
        self.assertEqual(cnt("She had a look. He has a look.", "have a look"), (2, 0))
        self.assertEqual(cnt("They did away with it. He does away with it.", "do away with"), (2, 0))

    def test_junk_forms_are_not_generated(self):
        self.assertEqual(cnt("I have a bed. It beds down.", "be down"), (0, 0))      # bed / beds を be の活用形にしない
        self.assertEqual(oc.inflect_forms("be"), {"be", "is", "are", "was", "were", "been", "being", "am"})

    def test_to_be(self):
        self.assertEqual(cnt("It seems to be in the way. He seemed to have a look.", "to be in the way"), (1, 0))

    def test_function_verbs_not_inflected_in_the_middle(self):
        self.assertEqual(cnt("It is a good thing.", "make a good thing"), (0, 0))


class ContractionExclusion(unittest.TestCase):
    """推奨: 's 縮約(let's / it's)は同一語として数えない。所有格は数える。"""

    def test_lets_and_its_are_not_let_or_it(self):
        self.assertEqual(cnt("Let's go. It's fine. That's all. He let it go.", "let"), (1, 0))
        self.assertEqual(cnt("It's fine. It was it.", "it"), (2, 0))

    def test_possessive_still_counts(self):
        self.assertEqual(cnt("The campaign's message. The team's goal.", "team"), (1, 0))
        self.assertEqual(cnt("The campaign's message.", "campaign"), (1, 0))


class JapaneseBodyAndStandard(unittest.TestCase):
    """推奨: a2(Standard)のPreview/Commentは日本語本文。英語tokenを含まず自然に0。縮約記号を含む日本語混在文も誤カウントしない。"""

    def test_japanese_comment_with_embedded_english(self):
        o = oc.count_entry({"story": ["He put it away."], "comment": ["「put away」は「片付ける」という意味です。今日は let's 復習しましょう。"], "preview": ["この記事では片付けを学びます。"],
                            "oneline": [], "title": ["A Title"]}, "put away")
        self.assertEqual(o["counts"]["story"], 1)
        self.assertEqual(o["counts"]["comment"], 1)      # 日本語文中の英語表現そのものは数える(回数は本文区分の出現)
        self.assertEqual(o["counts"]["preview"], 0)
        o2 = oc.count_entry({"story": ["Let's go."], "comment": ["今日は let's 復習しましょう。"], "preview": [], "oneline": [], "title": [""]}, "let")
        self.assertEqual(o2["total"], 0)


class SlotAliasesAndNames(unittest.TestCase):
    def test_sb_sth_aliases(self):
        self.assertEqual(cnt("He gave it up. She gives this up.", "give sth up"), (2, 0))
        self.assertEqual(cnt("They pulled him under. We pull her under.", "pull sb under"), (2, 0))
        self.assertEqual(cnt("She lost her trust in him.", "lose sb's trust in sb"), (1, 0))

    def test_person_name_slot_is_uncertain(self):
        self.assertEqual(cnt("They pulled Tom under. They pulled him under.", "pull someone under"), (1, 1))

    def test_lowercase_noun_not_treated_as_name(self):
        self.assertEqual(cnt("They pulled boats under.", "pull someone under"), (0, 0))


class UnionOfGeneralizedAndSurface(unittest.TestCase):
    """推奨: 活用・スロット展開は一般化形Uと実表現Sの両方から作り、和集合にする。"""

    def test_surface_inflection_expands_too(self):
        self.assertEqual(cnt("We heard it out. They hear it out. We heard him out.", "hear someone out", "hear it out"), (3, 0))

    def test_surface_variants(self):
        self.assertEqual(cnt("We turned it around. We turn it around.", "turn something around", "turned it around"), (2, 0))


class Er105Snapshot(unittest.TestCase):
    """er105の活用表・除外表の内容が変わったら落ちる(集計規則の再確認の合図。RULES_01.md の例と出現回数への影響を見直す)。"""

    SNAPSHOT = "501e9a186a0bfdfb5ef322239b91af9830ed233d49255c4dfc2b8b77d4d5f6f4"

    def test_er105_tables_snapshot(self):
        import er105_kp_fulltext_selector_01 as s
        d = {"plural_exclude": sorted(s._PLURAL_EXCLUDE), "participial": sorted(s._PARTICIPIAL_ADJ_EXCLUDE), "past_also": sorted(s.PAST_ALSO_OTHER_WORD),
             "completion": sorted(s.COMPLETION_EXCLUDE), "irr": sorted((k, v[0], v[1]) for k, v in s.IRR.items()), "irr_plural": sorted(s._IRREGULAR_PLURAL.items())}
        got = hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()
        self.assertEqual(got, self.SNAPSHOT, "er105の活用表/除外表が変わりました。RULES_01.md・M1の保留対象を再確認してから SNAPSHOT を更新してください")

    def test_forward_forms_of_sample_lemmas(self):
        self.assertEqual(oc.inflect_forms("build"), {"build", "builds", "building", "built"})
        self.assertEqual(oc.inflect_forms("leave"), {"leave", "leaves", "leaving", "left"})
        self.assertEqual(oc.inflect_forms("lie"), {"lie", "lies", "lying", "lay", "lain"})
        self.assertEqual(oc.risky_forms("build", 1), {"building"})
        self.assertEqual(oc.risky_forms("leave", 1), {"left"})
        self.assertEqual(oc.risky_forms("leave", 2), set())
        self.assertEqual(oc.risky_forms("lie", 2), {"lay"})
        self.assertEqual(oc.risky_forms("good", 2), {"goods"})


class SelfCheckExactCount(unittest.TestCase):
    def test_exact_selection_count_matches_old_definition(self):
        secs = {"story": ["The campaign's message. A campaign works."], "oneline": ["Campaign."], "title": ["Campaign Day"], "comment": None}
        self.assertEqual(oc.exact_selection_count(secs, "campaign"), 4)

    def test_exact_selection_count_none_when_section_missing(self):
        self.assertIsNone(oc.exact_selection_count({"story": ["x"], "oneline": None, "title": ["y"]}, "x"))

    def test_exact_count_excludes_inflection(self):
        self.assertEqual(oc.exact_selection_count({"story": ["He left out it. He leaves out it."], "oneline": [], "title": []}, "leave out"), 0)


class SectionLoaders(unittest.TestCase):
    def _write(self, root, rel, text):
        p = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)

    def test_units_split_at_newlines_not_joined(self):
        self.assertEqual(sl.units("Lead line without period\nwhen I came.\n\nSecond   para."), ["Lead line without period", "when I came.", "Second para."])

    def test_y_heading_and_first_line_do_not_form_a_phrase(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, "out/translate/b1b.md", "# Title Here\n\nSpeaker One\nlead the way home. Next.\n")
            self._write(td, "out/support/b1b_support.json", json.dumps({"preview": "pre", "comments": {"1": "c1"}}))
            cand = os.path.join(td, "out", "key_phrases", "b1b", "kp_candidates.json").replace("\\", "/")
            sec, src = sl.load_sections("Y", cand, "b1b")
            self.assertEqual(sec["story"], ["Speaker One", "lead the way home. Next."])
            self.assertEqual(oc.count_entry(sec, "one lead")["total"], 0)      # 見出し行の末尾語+本文先頭語の連結一致なし
            self.assertEqual(sec["title"], ["Title Here"])
            self.assertEqual(sec["oneline"], [])
            self.assertEqual(sec["comment"], ["c1"])

    def test_x_loader_and_unavailable(self):
        with tempfile.TemporaryDirectory() as td:
            self._write(td, "run/b1b/parts.json", json.dumps({"title": "T", "part1": "A one.\n\nB two.", "part2": "C.", "part3": "", "in_one_line": "Short."}))
            cand = os.path.join(td, "run", "b1b", "key_phrases", "kp_candidates.json").replace("\\", "/")
            sec, src = sl.load_sections("X", cand, "b1b")
            self.assertEqual(sec["story"], ["A one.", "B two.", "C."])
            self.assertEqual(sec["oneline"], ["Short."])
            self.assertIsNone(sec["comment"])
            self.assertIsNone(sec["preview"])
            meta = sl.sections_meta(sec, src, td)
            self.assertEqual(meta["unavailable"], ["comment", "preview"])
            self.assertEqual(meta["sections"]["story"]["units"], 3)

    def test_nothing_found_is_all_unavailable(self):
        with tempfile.TemporaryDirectory() as td:
            cand = os.path.join(td, "none", "b1b", "key_phrases", "kp_candidates.json").replace("\\", "/")
            sec, src = sl.load_sections("Z", cand, "b1b")
            self.assertTrue(all(v is None for v in sec.values()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
