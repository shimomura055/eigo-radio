# ============================================================
# er032_key_phrase_db_hybrid_core_v2_trial_05_test.py
# KEY-PHRASE-DB-HYBRID-CORE-V2-TRIAL-05
# ============================================================
# 実行: .venv/Scripts/python.exe -m unittest er032_key_phrase_db_hybrid_core_v2_trial_05_test -v
# ============================================================

from __future__ import annotations

import os
import unittest

import er023_key_phrase_db_ingest as ing
import er032_key_phrase_db_hybrid_core_v2_trial_05_stage1 as s2


class V2WordBucketRankingTests(unittest.TestCase):
    """V2-1: lemma正規化後の頻度によるword bucket ranking改善。"""

    def test_loyalty_ranks_ahead_of_inflected_verb_forms(self):
        # Family Z Trial REPORT §4-2で発見した実データ相当の語群
        # (屈折形は本来の語族頻度より低いzipfを持つため、lemma正規化前は
        # loyaltyより「rare」に誤判定されていた)。
        inflected_forms = ["hurried", "executions", "whispered", "shouted",
                           "lowered", "smiled", "shaking", "demanded"]
        keys = ["loyalty"] + inflected_forms
        ranked = sorted(keys, key=s2._lemma_normalized_word_rarity_key)
        top5 = ranked[:5]
        self.assertIn("loyalty", top5,
                      f"loyaltyがlemma正規化後のword bucket上位5件から漏れている: {ranked}")

    def test_uninflected_word_unaffected(self):
        # 屈折形を持たない語(loyalty自身)は表層形のzipfのまま変わらない
        zf, key = s2._lemma_normalized_word_rarity_key("loyalty")
        self.assertEqual(key, "loyalty")
        self.assertGreater(zf, 0)

    def test_ied_past_tense_extra_lemma_rule(self):
        # 既存er015 lemma_candidates_v2は"-ied"→"-y"型(hurried→hurry)を
        # 生成できないため、本ファイル側で補う一般規則を確認する。
        self.assertIn("hurry", s2._extra_lemma_candidates_for_ranking("hurried"))
        self.assertIn("carry", s2._extra_lemma_candidates_for_ranking("carried"))


class V2PronounPlaceholderMultiwordTests(unittest.TestCase):
    """V2-2: 代名詞プレースホルダ置換による重要multiword lookup改善。"""

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_in_his_place_rescued_via_ones_place_idiom(self):
        # 実データ確認(Wiktionary idioms.jsonローカルdump): "one's place"が
        # `Category:English idioms`に存在する(in his/her place等の代表形)。
        ngram = {"n": 2, "surface_tokens": ["his", "place"], "surface_form": "his place", "start": 0}
        core = s2.match_candidate_with_pronoun_placeholder_rescue(ngram, self.dbs)
        self.assertTrue(core["pronoun_placeholder_rescue"])
        self.assertGreater(core["db_match_count"], 0)
        self.assertEqual(core["surface_form"], "his place")  # 表示は本文中の実際の表現のまま

    def test_placeholder_variants_cover_possessive_and_object_pronouns(self):
        variants = s2._pronoun_placeholder_variants(["her", "place"])
        self.assertIn("one's place", variants)
        self.assertIn("someone's place", variants)
        variants2 = s2._pronoun_placeholder_variants(["let", "me", "go"])
        self.assertIn("let one go", variants2)
        self.assertIn("let someone go", variants2)

    def test_no_rescue_when_no_pronoun_present(self):
        ngram = {"n": 2, "surface_tokens": ["brent", "crude"], "surface_form": "brent crude", "start": 0}
        core = s2.match_candidate_with_pronoun_placeholder_rescue(ngram, self.dbs)
        self.assertFalse(core["pronoun_placeholder_rescue"])

    def test_lookup_priority_puts_pronoun_slot_shapes_first(self):
        sentences = [["I", "will", "stay", "here", "in", "his", "place"],
                     ["The", "small", "boat", "broke", "against", "a", "rock"]]
        ordered = s2.select_unmatched_ngram_candidates_for_lookup_v2(sentences, set(), budget=60)
        # "in his"/"his place"(代名詞含む)が"small boat"のような形状より優先される
        idx_pronoun = next(i for i, s in enumerate(ordered) if "his" in s.lower().split())
        idx_plain = next(i for i, s in enumerate(ordered) if s.lower() == "small boat")
        self.assertLess(idx_pronoun, idx_plain)

    def test_lookup_priority_does_not_crowd_out_existing_good_candidate(self):
        # 実データ回帰(hormuz_a2): 初期案(前置詞・助詞で始まる/終わる候補を
        # 無制限に優先)は、既存の良い候補("Brent crude"、v1では528件中
        # 12位でbudget=60に楽に入っていた)をbudget外へ押し出す regression を
        # 起こしていた(2-3gram全体の過半数が前置詞形状のため)。予約枠を
        # 代名詞スロットのみ・小さく固定した本実装ではこれが起きないことを
        # 固定回帰化する。
        path = "er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/a2/article.md"
        if not os.path.exists(path):
            self.skipTest("hormuz article fixture not present")
        text = open(path, encoding="utf-8").read()
        units = s2.build_sentence_units(text)
        sentences = [u["tokens"] for u in units]
        ordered = s2.select_unmatched_ngram_candidates_for_lookup_v2(sentences, set(), budget=60)
        self.assertIn("brent crude", [s.lower() for s in ordered])


class V2ProperNounDialogueTagTests(unittest.TestCase):
    """V2-3: proper noun / dialogue tag除外の明示化。"""

    def test_echo_said_excluded_from_compound_noun_candidates(self):
        dbs = ing.load_all_group1_dbs()
        units = [
            {"tokens": ["Echo", "looked", "toward", "the", "city"], "raw_text": "x"},
            {"tokens": ["Then", "Echo", "said", "hello"], "raw_text": "x"},
            {"tokens": ["She", "walked", "with", "Echo", "again"], "raw_text": "x"},
            {"tokens": ["Echo", "said", "again", "softly"], "raw_text": "x"},
        ]
        signals = s2.compute_proper_noun_signals(units)
        self.assertTrue(s2.is_proper_noun_like("echo", signals))
        candidates = s2.find_repeated_compound_noun_candidates_v2(units, dbs, signals)
        canonicals = {c["canonical_form"] for c in candidates}
        self.assertNotIn("echo said", canonicals)

    def test_mark_lowercase_common_word_not_falsely_excluded(self):
        # "Mark"(固有名詞、会話タグに隣接)と"mark"(一般語、小文字出現あり)
        # が同一記事に混在する場合、一般語としてのfalse exclusionを避ける。
        units = [
            {"tokens": ["Mark", "said", "hello"], "raw_text": "x"},
            {"tokens": ["Then", "Mark", "walked", "away"], "raw_text": "x"},
            {"tokens": ["Later", "Mark", "smiled", "again"], "raw_text": "x"},
            {"tokens": ["There", "was", "a", "mark", "on", "the", "wall"], "raw_text": "x"},
        ]
        signals = s2.compute_proper_noun_signals(units)
        self.assertFalse(s2.is_proper_noun_like("mark", signals),
                         "小文字出現がある語(mark)を固有名詞として誤除外してはいけない")

    def test_recurring_capitalized_name_flagged_proper_noun(self):
        # 文頭以外での大文字始まり出現が2回以上・小文字出現なしの語は
        # 固有名詞として判定する(登場人物名の一般的性質)。
        units = [
            {"tokens": ["In", "a", "town", "Selinuntius", "lived"], "raw_text": "x"},
            {"tokens": ["His", "friend", "Selinuntius", "waited"], "raw_text": "x"},
        ]
        signals = s2.compute_proper_noun_signals(units)
        self.assertTrue(s2.is_proper_noun_like("selinuntius", signals))

    def test_single_occurrence_capitalized_quote_initial_word_not_flagged(self):
        # 引用符内発話冒頭の語("shouted, "Wait!"")が既存文分割の都合で
        # 「文頭以外」扱いになっても、記事中1回しか出現しないなら固有名詞
        # として誤判定しない(実データ発見、Melos"Wait")。
        units = [{"tokens": ["Then", "Melos", "shouted", "Wait"], "raw_text": "x"}]
        signals = s2.compute_proper_noun_signals(units)
        self.assertFalse(s2.is_proper_noun_like("wait", signals))

    def test_fix_b_rare_word_still_excludes_proper_noun_with_single_occurrence(self):
        # Fix B(1-gram, DB不一致専用経路)は既存v1のガード(小文字出現が
        # 一度もない語は対象外)を維持し、記事中1回しか出現しない固有名詞
        # (Dionysius等)も正しく除外できることを確認する。
        dbs = ing.load_all_group1_dbs()
        units = [{"tokens": ["The", "ruler", "Dionysius", "was", "afraid"], "raw_text": "x"}]
        signals = s2.compute_proper_noun_signals(units)
        selected = s2.select_rare_single_word_candidates_v2(units, dbs, signals, "", budget=15)
        keys = {k for k, e, r in selected}
        self.assertNotIn("dionysius", keys)

    def test_technical_compound_noun_preserved_when_no_dialogue_verb_present(self):
        # "brent crude"のような既存の真の技術複合語は、会話attribution動詞
        # を含まないため会話タグ形状ガードの対象外(既存の良い候補を保護)。
        dbs = ing.load_all_group1_dbs()
        units = [
            {"tokens": ["Brent", "crude", "rose", "today"], "raw_text": "x"},
            {"tokens": ["Traders", "watched", "Brent", "crude", "closely"], "raw_text": "x"},
        ]
        signals = s2.compute_proper_noun_signals(units)
        candidates = s2.find_repeated_compound_noun_candidates_v2(units, dbs, signals)
        canonicals = {c["canonical_form"] for c in candidates}
        self.assertIn("brent crude", canonicals)


class V2RealDataIntegrationTests(unittest.TestCase):
    """実データ(Melos、Family Z)でV2-1/V2-2/V2-3が組み合わさって機能する
    ことの統合確認(既存の真のphrase/idiomを壊していないことの回帰も
    兼ねる)。"""

    MELOS_PATH = "er026_output/family_z_production_e2e_01/melos/run_01/article.md"

    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_melos_loyalty_reaches_word_bucket_top6(self):
        # lemma正規化ランキング適用後、Melosの実データではloyalty(zipf
        # 4.17)がちょうど6番目に来る(whispered/ruler/punish/shouted/
        # hurriedの5語がlemma正規化後も[偏りではなく]genuineにloyaltyより
        # rareなため)。er032_runはこの境界ケースをbuild_shortlistの
        # word_min=6(既存の公開パラメータ)で救う(§run.py参照)。
        if not os.path.exists(self.MELOS_PATH):
            self.skipTest("Melos article fixture not present")
        text = open(self.MELOS_PATH, encoding="utf-8").read()
        st = s2.run_stage1_for_article_core_v2(text, self.dbs)
        top6 = [c["canonical_form"] for c in st["word_survivors"][:6]]
        self.assertIn("loyalty", top6)

    def test_melos_his_place_becomes_idiom_candidate(self):
        if not os.path.exists(self.MELOS_PATH):
            self.skipTest("Melos article fixture not present")
        text = open(self.MELOS_PATH, encoding="utf-8").read()
        st = s2.run_stage1_for_article_core_v2(text, self.dbs)
        canonicals = {c["canonical_form"]: c["unit_type"] for c in st["phrase_survivors"]}
        self.assertIn("his place", canonicals)
        self.assertEqual(canonicals["his place"], "idiom")

    def test_melos_proper_nouns_not_selected_as_stage1_candidates(self):
        if not os.path.exists(self.MELOS_PATH):
            self.skipTest("Melos article fixture not present")
        text = open(self.MELOS_PATH, encoding="utf-8").read()
        st = s2.run_stage1_for_article_core_v2(text, self.dbs)
        all_canonicals = ({c["canonical_form"] for c in st["word_survivors"]} |
                          {c["canonical_form"] for c in st["phrase_survivors"]} |
                          {c["canonical_form"] for c in st["important_noun_candidates"]})
        for name in ("melos", "dionysius", "selinuntius"):
            self.assertNotIn(name, all_canonicals)

    def test_twins_echo_said_not_in_important_noun_candidates(self):
        path = "er013_output/family_c_episode_trial_12/twins_a2/article_normalized.txt"
        if not os.path.exists(path):
            self.skipTest("twins article fixture not present")
        text = open(path, encoding="utf-8").read()
        st = s2.run_stage1_for_article_core_v2(text, self.dbs)
        canonicals = {c["canonical_form"] for c in st["important_noun_candidates"]}
        self.assertNotIn("echo said", canonicals)
        self.assertNotIn("mara said", canonicals)

    def test_run_stage1_for_article_core_v2_is_deterministic(self):
        text = "Meta has pulled back the human concierge feature. Before AI speaks for us, we need to know."
        r1 = s2.run_stage1_for_article_core_v2(text, self.dbs)
        r2 = s2.run_stage1_for_article_core_v2(text, self.dbs)
        self.assertEqual([c["canonical_form"] for c in r1["phrase_survivors"]],
                         [c["canonical_form"] for c in r2["phrase_survivors"]])

    def test_bug_a_discontinuous_phrasal_verb_still_excluded(self):
        text = "The worker was pushing large bags out of the truck."
        r = s2.run_stage1_for_article_core_v2(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["phrase_survivors"]}
        self.assertNotIn("bags out", canonicals)

    def test_bug_c_possessive_noise_stripped(self):
        text = "The user's plan changed after the meeting."
        r = s2.run_stage1_for_article_core_v2(text, self.dbs)
        canonicals = {c["canonical_form"] for c in r["word_survivors"]}
        self.assertNotIn("user's", canonicals)

    def test_melos_loyalty_and_his_place_in_actual_shortlist(self):
        # stage1のranking/matching改善だけでなく、er032_runのshortlist
        # 組み立て(word_min=6)まで通した実際のshortlistにloyalty/
        # his placeが含まれることの統合確認。
        if not os.path.exists(self.MELOS_PATH):
            self.skipTest("Melos article fixture not present")
        import er032_key_phrase_db_hybrid_core_v2_trial_05_run as r2
        text = open(self.MELOS_PATH, encoding="utf-8").read()
        s1r = r2.run_stage1_and_shortlist_core_v2(text, self.dbs, "The Three-Day Promise")
        canonicals = {c["canonical_form"] for c in s1r["shortlist_info"]["shortlist"]}
        self.assertIn("loyalty", canonicals)
        self.assertIn("his place", canonicals)


if __name__ == "__main__":
    unittest.main()
