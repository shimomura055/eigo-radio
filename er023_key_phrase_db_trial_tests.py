# ============================================================
# er023_key_phrase_db_trial_tests.py
# KEY-PHRASE-DB-BASED-SELECTION-TRIAL-01
# 最低限のunit test: 抽出(tokenize/n-gram)・照合(DB match)・
# 別集計(word/phrase group separation)の決定論性を検証する。
# 実行: .venv/Scripts/python.exe -m pytest er023_key_phrase_db_trial_tests.py -v
# (pytestが無い環境向けにunittestでも直接実行可能にする)
# ============================================================

from __future__ import annotations

import unittest

import er023_key_phrase_db_extraction as ext
import er023_key_phrase_db_ingest as ing


class TokenizeDeterminismTests(unittest.TestCase):
    def test_tokenize_strips_markdown_and_is_deterministic(self):
        text = "# Title\n\nThis is a **test** sentence. Another one!\n"
        t1 = ext.tokenize(text)
        t2 = ext.tokenize(text)
        self.assertEqual(t1, t2)
        self.assertIn("Title", t1)
        self.assertIn("test", t1)
        self.assertNotIn("#", "".join(t1))

    def test_tokenize_sentences_does_not_cross_sentence_boundary(self):
        text = "The cat ran fast. The dog slept well."
        sentences = ext.tokenize_sentences(text)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], ["The", "cat", "ran", "fast"])
        self.assertEqual(sentences[1], ["The", "dog", "slept", "well"])

    def test_generate_ngrams_sentence_aware_never_crosses_boundary(self):
        sentences = [["a", "b", "c"], ["d", "e"]]
        ngrams = ext.generate_ngrams(sentences, min_n=1, max_n=5)
        surface_forms = {ng["surface_form"] for ng in ngrams}
        # "c d"のように文をまたぐ2-gramは生成されないこと
        self.assertNotIn("c d", surface_forms)
        self.assertIn("a b", surface_forms)
        self.assertIn("d e", surface_forms)
        # 5-gramは各文の長さ(3,2)を超えるため生成されない
        self.assertFalse(any(ng["n"] == 5 for ng in ngrams))

    def test_generate_ngrams_count_matches_expected_formula(self):
        sentences = [["a", "b", "c", "d"]]
        ngrams = ext.generate_ngrams(sentences, min_n=1, max_n=5)
        # n=1:4, n=2:3, n=3:2, n=4:1, n=5:0(文長4より長いため生成不可)
        counts = {}
        for ng in ngrams:
            counts[ng["n"]] = counts.get(ng["n"], 0) + 1
        self.assertEqual(counts, {1: 4, 2: 3, 3: 2, 4: 1})

    def test_generate_ngrams_flat_list_backward_compatible(self):
        # 後方互換: フラットな1次元リストを渡した場合は旧動作(境界なし)
        ngrams = ext.generate_ngrams(["a", "b", "c"], min_n=1, max_n=2)
        surface_forms = {ng["surface_form"] for ng in ngrams}
        self.assertIn("a b", surface_forms)
        self.assertIn("b c", surface_forms)


class DbMatchDeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_word_lemma_match_is_deterministic(self):
        ngram = {"n": 1, "start": 0, "surface_tokens": ["running"], "surface_form": "running"}
        r1 = ext.match_candidate_against_group1(ngram, self.dbs)
        r2 = ext.match_candidate_against_group1(ngram, self.dbs)
        self.assertEqual(r1, r2)
        self.assertGreaterEqual(r1["db_match_count"], 1)

    def test_known_phrasal_verb_matches_wiktionary(self):
        ngram = {"n": 2, "start": 0, "surface_tokens": ["give", "back"], "surface_form": "give back"}
        r = ext.match_candidate_against_group1(ngram, self.dbs)
        self.assertIn("wiktionary", r["matched_dbs"])
        self.assertIn("phrasal_verb", r["db_categories"])

    def test_single_word_wiktionary_idiom_category_does_not_become_phrase_unit_type(self):
        """1語の候補が偶然Wiktionaryのidiomsカテゴリに属していても、
        unit_typeはwordのままであること(2026-09-27の実データ確認: 'oil'/
        'story'/'would'が単語ページのままidiomsカテゴリに属していた
        観測に基づく回帰テスト)。"""
        ngram = {"n": 1, "start": 0, "surface_tokens": ["oil"], "surface_form": "oil"}
        r = ext.match_candidate_against_group1(ngram, self.dbs)
        self.assertEqual(r["unit_type"], "word")

    def test_closed_class_function_word_is_rule_excluded(self):
        ngram = {"n": 1, "start": 0, "surface_tokens": ["the"], "surface_form": "the"}
        evidence = ext.build_evidence(ngram, self.dbs)
        gate = ext.apply_exclusion_gate(evidence, [], {})
        self.assertTrue(gate["too_easy_or_common"]["rule_determined"])
        self.assertTrue(gate["too_easy_or_common"]["value"])

    def test_content_word_gate_is_not_rule_determined(self):
        """CEFR levelを主軸にしない(除外Gateの主軸には使わない)ため、
        内容語の「簡単すぎ」判定は規則で判定できない(人間判断が必要)
        ことを確認する回帰テスト。"""
        ngram = {"n": 1, "start": 0, "surface_tokens": ["important"], "surface_form": "important"}
        evidence = ext.build_evidence(ngram, self.dbs)
        gate = ext.apply_exclusion_gate(evidence, [], {})
        self.assertFalse(gate["too_easy_or_common"]["rule_determined"])


class WordPhraseSeparateTallyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbs = ing.load_all_group1_dbs()

    def test_word_and_phrase_groups_do_not_mix_in_ranking(self):
        """Fableレビュー論点2: 複数DB一致数でword群がphrase群を押し出さない
        よう、word/phrase各群内でのみソートすること(グローバルにdb_match_
        countでマージしないこと)を検証する。"""
        candidates = [
            {"canonical_form": "the", "unit_type": "word", "db_match_count": 3},
            {"canonical_form": "give back", "unit_type": "phrasal_verb", "db_match_count": 1},
            {"canonical_form": "cat", "unit_type": "word", "db_match_count": 2},
        ]
        word_group = sorted([c for c in candidates if c["unit_type"] == "word"],
                            key=lambda c: (-c["db_match_count"], c["canonical_form"]))
        phrase_group = sorted([c for c in candidates if c["unit_type"] != "word"],
                              key=lambda c: (-c["db_match_count"], c["canonical_form"]))
        # phrase_groupの"give back"(db_match_count=1)がword_groupの
        # 高db_match_count候補によって群外へ押し出されていないこと
        self.assertEqual(len(phrase_group), 1)
        self.assertEqual(phrase_group[0]["canonical_form"], "give back")
        self.assertEqual(word_group[0]["canonical_form"], "the")  # word群内では3が最上位のまま


class DedupeDeterminismTests(unittest.TestCase):
    def test_dedupe_keeps_highest_db_match_count(self):
        evidences = [
            {"canonical_form": "test", "unit_type": "word", "db_match_count": 1, "n": 1},
            {"canonical_form": "test", "unit_type": "word", "db_match_count": 2, "n": 1},
        ]
        deduped = ext.dedupe_candidates_by_canonical_form(evidences)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["db_match_count"], 2)

    def test_dedupe_prefers_smaller_n_on_tie(self):
        evidences = [
            {"canonical_form": "x", "unit_type": "phrase", "db_match_count": 1, "n": 3},
            {"canonical_form": "x", "unit_type": "phrase", "db_match_count": 1, "n": 2},
        ]
        deduped = ext.dedupe_candidates_by_canonical_form(evidences)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["n"], 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
