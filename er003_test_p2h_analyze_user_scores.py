# ============================================================
# er003_test_p2h_analyze_user_scores.py
# ER-003-P2H: P2Gユーザー評価の取込・ブラインド解除・L/P/U方式比較のテスト
# ============================================================
# 実API・Web検索は一切行わない。すべてローカルファイル/合成データのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_p2h_analyze_user_scores -v

import json
import os
import shutil
import tempfile
import unittest

import er003_p2h_analyze_user_scores as p2h

GOOD_TSV = "\n".join([
    "article\tset\trank\tdisplay_phrase\tja_gloss\trating",
] + [
    f"{a}\t{s}\t{r}\tphrase {a}{s}{r}\tグロス{a}{s}{r}\t〇"
    for a in p2h.ARTICLE_IDS for s in p2h.SET_LABELS for r in p2h.RANKS
])


def make_item(rank, display_phrase, source_span, source_sentence, ja_gloss):
    band = "TOP_5" if rank <= 5 else "RANK_6_TO_10"
    return {
        "rank": rank, "display_phrase": display_phrase, "source_span": source_span,
        "source_sentence": source_sentence, "ja_gloss": ja_gloss, "research_band": band,
    }


def make_selection(items):
    return {"items": items}


def make_form_qa_item(rank, verdict="PASS", notes=""):
    return {"rank": rank, "form_verdict": verdict, "minimal_unit": "PASS", "not_a_clause": "PASS",
            "canonical_form": "PASS", "source_fidelity": "PASS", "gloss_match": "PASS", "notes": notes}


class RatingConversionTests(unittest.TestCase):
    def test_maru_is_2(self):
        self.assertEqual(p2h.rating_to_score("〇"), 2)

    def test_sankaku_is_1(self):
        self.assertEqual(p2h.rating_to_score("△"), 1)

    def test_batsu_is_0(self):
        self.assertEqual(p2h.rating_to_score("×"), 0)

    def test_unknown_symbol_raises(self):
        with self.assertRaises(ValueError):
            p2h.rating_to_score("?")


class RawTsvValidationTests(unittest.TestCase):
    def test_90_rows_parsed_and_valid(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)
        self.assertEqual(len(rows), 90)
        result = p2h.validate_raw_rows(rows)
        self.assertTrue(result["ok"], msg=result["reasons"])

    def test_each_article_set_has_10_ranks(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)
        for a in p2h.ARTICLE_IDS:
            for s in p2h.SET_LABELS:
                ranks = sorted(r["rank"] for r in rows if r["article"] == a and r["set"] == s)
                self.assertEqual(ranks, list(range(1, 11)), msg=f"{a}/{s}")

    def test_rank_1_to_10_range(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)
        for r in rows:
            self.assertIn(r["rank"], p2h.RANKS)

    def test_duplicate_rank_detected(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)
        rows[1] = dict(rows[1])
        rows[1]["article"], rows[1]["set"], rows[1]["rank"] = rows[0]["article"], rows[0]["set"], rows[0]["rank"]
        result = p2h.validate_raw_rows(rows)
        self.assertFalse(result["ok"])
        self.assertTrue(any("重複キー" in r for r in result["reasons"]))

    def test_unknown_rating_symbol_rejected(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)
        rows[0] = dict(rows[0])
        rows[0]["rating"] = "?"
        result = p2h.validate_raw_rows(rows)
        self.assertFalse(result["ok"])
        self.assertTrue(any("unknown rating symbol" in r for r in result["reasons"]))

    def test_missing_row_detected(self):
        rows = p2h.parse_raw_tsv(GOOD_TSV)[:-1]
        result = p2h.validate_raw_rows(rows)
        self.assertFalse(result["ok"])
        self.assertTrue(any("90件でない" in r for r in result["reasons"]))
        self.assertTrue(any("欠落キー" in r for r in result["reasons"]))

    def test_add03_set_c_real_file_has_no_duplicate_ranks(self):
        # ユーザー提供の修正版TSV(rawファイル)がADD03 Set Cで重複rankを
        # 含まないことを確認する(元の画像に重複表示があった件の検証)。
        path = "er003_output/p2h/ER-003-P2H_user_scores_raw.tsv"
        if not os.path.exists(path):
            self.skipTest("raw TSVが見つかりません")
        with open(path, encoding="utf-8") as f:
            rows = p2h.parse_raw_tsv(f.read())
        add03_c_ranks = [r["rank"] for r in rows if r["article"] == "ADD03" and r["set"] == "C"]
        self.assertEqual(sorted(add03_c_ranks), list(range(1, 11)))
        self.assertEqual(len(add03_c_ranks), len(set(add03_c_ranks)))


class NormalizationTests(unittest.TestCase):
    def test_nfkc_normalization(self):
        self.assertEqual(p2h.normalize_text("ＡＢＣ"), "abc")

    def test_nbsp_normalized_to_space(self):
        self.assertEqual(p2h.normalize_text("take off"), "take off")

    def test_collapses_whitespace(self):
        self.assertEqual(p2h.normalize_text("take   off"), "take off")

    def test_case_insensitive(self):
        self.assertEqual(p2h.normalize_text("Take Off"), p2h.normalize_text("take off"))

    def test_typographic_apostrophe_normalized(self):
        self.assertEqual(p2h.normalize_text("don’t"), p2h.normalize_text("don't"))

    def test_exact_match_status(self):
        self.assertEqual(p2h.match_status("take off", "take off"), "EXACT_MATCH")

    def test_typo_match_status_for_even_soo(self):
        status = p2h.match_status("even soo", "even so")
        self.assertEqual(status, "LIKELY_TYPO_OR_MINOR_VARIANT")

    def test_typo_does_not_change_score(self):
        # match_statusはscore計算(rating_to_score)と独立している
        score = p2h.rating_to_score("×")
        status = p2h.match_status("even soo", "even so")
        self.assertEqual(score, 0)
        self.assertEqual(status, "LIKELY_TYPO_OR_MINOR_VARIANT")

    def test_very_different_text_differs(self):
        self.assertEqual(p2h.match_status("take off", "completely unrelated phrase"), "DIFFERS")


class ReconciliationTests(unittest.TestCase):
    """要求(section 6): mappingはファイルから読み推測しない。主キーは
    article_id+blind_set+rank。一致不能な行は停止する。"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.orig_root = p2h.P2G_ROOT
        p2h.P2G_ROOT = self.tmp_dir

        os.makedirs(f"{self.tmp_dir}/A01/L")
        os.makedirs(f"{self.tmp_dir}/A01/P")
        os.makedirs(f"{self.tmp_dir}/A01/U")

        mapping = {"Set A": "L", "Set B": "P", "Set C": "U"}
        with open(f"{self.tmp_dir}/A01/blind_mapping.json", "w", encoding="utf-8") as f:
            json.dump(mapping, f)

        items_l = [make_item(i, f"l-phrase-{i}", f"l-span-{i}", f"L sentence {i}.", f"Lグロス{i}")
                   for i in range(1, 11)]
        items_p = [make_item(i, f"p-phrase-{i}", f"p-span-{i}", f"P sentence {i}.", f"Pグロス{i}")
                   for i in range(1, 11)]
        items_u = [make_item(i, f"u-phrase-{i}", f"u-span-{i}", f"U sentence {i}.", f"Uグロス{i}")
                   for i in range(1, 11)]
        with open(f"{self.tmp_dir}/A01/L/key_words_selection.json", "w", encoding="utf-8") as f:
            json.dump(make_selection(items_l), f)
        with open(f"{self.tmp_dir}/A01/P/key_words_selection.json", "w", encoding="utf-8") as f:
            json.dump(make_selection(items_p), f)
        with open(f"{self.tmp_dir}/A01/U/key_words_selection.json", "w", encoding="utf-8") as f:
            json.dump(make_selection(items_u), f)

        form_qa = {"parsed_result": {"sets": [
            {"runtime_strategy_id": "L", "items": [make_form_qa_item(i) for i in range(1, 11)]},
            {"runtime_strategy_id": "P", "items": [make_form_qa_item(i) for i in range(1, 11)]},
            {"runtime_strategy_id": "U", "items": [make_form_qa_item(2, verdict="FAIL", notes="test fail")]
                + [make_form_qa_item(i) for i in range(1, 11) if i != 2]},
        ]}}
        with open(f"{self.tmp_dir}/A01/form_qa.json", "w", encoding="utf-8") as f:
            json.dump(form_qa, f)

    def tearDown(self):
        p2h.P2G_ROOT = self.orig_root
        shutil.rmtree(self.tmp_dir)

    def test_mapping_applied_from_file(self):
        rows = [{"article": "A01", "set": "B", "rank": 1, "display_phrase": "p-phrase-1",
                 "ja_gloss": "Pグロス1", "rating": "〇"}]
        normalized = p2h.reconcile_rows(rows)
        self.assertEqual(normalized[0]["strategy_id"], "P")

    def test_mapping_never_guessed_uses_file_content(self):
        # mapping fileを書き換えると結果も変わることを確認する(推測でない証拠)
        with open(f"{self.tmp_dir}/A01/blind_mapping.json", "w", encoding="utf-8") as f:
            json.dump({"Set A": "U", "Set B": "L", "Set C": "P"}, f)
        rows = [{"article": "A01", "set": "A", "rank": 1, "display_phrase": "u-phrase-1",
                 "ja_gloss": "Uグロス1", "rating": "〇"}]
        normalized = p2h.reconcile_rows(rows)
        self.assertEqual(normalized[0]["strategy_id"], "U")

    def test_canonical_fields_populated_from_p2g(self):
        rows = [{"article": "A01", "set": "A", "rank": 3, "display_phrase": "typo-phrase",
                 "ja_gloss": "違うグロス", "rating": "△"}]
        normalized = p2h.reconcile_rows(rows)
        row = normalized[0]
        self.assertEqual(row["canonical_phrase"], "l-phrase-3")
        self.assertEqual(row["source_span"], "l-span-3")
        self.assertEqual(row["source_sentence"], "L sentence 3.")
        self.assertEqual(row["research_band"], "TOP_5")
        self.assertEqual(row["score"], 1)

    def test_qa_verdict_attached(self):
        rows = [{"article": "A01", "set": "C", "rank": 2, "display_phrase": "u-phrase-2",
                 "ja_gloss": "Uグロス2", "rating": "〇"}]
        normalized = p2h.reconcile_rows(rows)
        self.assertEqual(normalized[0]["extraction_form_qa_verdict"], "FAIL")
        self.assertEqual(normalized[0]["extraction_form_qa_notes"], "test fail")

    def test_unmatched_rank_raises(self):
        rows = [{"article": "A01", "set": "A", "rank": 99, "display_phrase": "x", "ja_gloss": "y", "rating": "〇"}]
        with self.assertRaises(p2h.ReconciliationError):
            p2h.reconcile_rows(rows)

    def test_unmatched_set_label_raises(self):
        rows = [{"article": "A01", "set": "Z", "rank": 1, "display_phrase": "x", "ja_gloss": "y", "rating": "〇"}]
        with self.assertRaises(p2h.ReconciliationError):
            p2h.reconcile_rows(rows)

    def test_row_not_moved_to_different_rank_on_mismatch(self):
        # typoやgloss不一致があっても、rankの紐付け自体は変わらない
        rows = [{"article": "A01", "set": "A", "rank": 5, "display_phrase": "completely wrong text",
                 "ja_gloss": "全く違う", "rating": "〇"}]
        normalized = p2h.reconcile_rows(rows)
        self.assertEqual(normalized[0]["rank"], 5)
        self.assertEqual(normalized[0]["canonical_phrase"], "l-phrase-5")


class AggregationTests(unittest.TestCase):
    def _row(self, article_id, blind_set, strategy_id, rank, rating):
        band = "TOP_5" if rank <= 5 else "RANK_6_TO_10"
        return {
            "article_id": article_id, "blind_set": blind_set, "strategy_id": strategy_id, "rank": rank,
            "research_band": band, "rating_symbol": rating, "score": p2h.rating_to_score(rating),
            "extraction_form_qa_verdict": "PASS",
        }

    def _make_normalized(self, ratings_l, ratings_p, ratings_u, article_id="A01"):
        rows = []
        for strategy_id, ratings in (("L", ratings_l), ("P", ratings_p), ("U", ratings_u)):
            for rank, rating in enumerate(ratings, start=1):
                blind_set = {"L": "A", "P": "B", "U": "C"}[strategy_id]
                rows.append(self._row(article_id, blind_set, strategy_id, rank, rating))
        return rows

    def test_top5_rank6_10_total_scores(self):
        ratings = ["〇"] * 5 + ["×"] * 5  # top5=10, rank6-10=0, total=10
        normalized = self._make_normalized(ratings, ["△"] * 10, ["×"] * 10)
        agg = p2h.aggregate_by_article_strategy(normalized)
        stats = agg[("A01", "L")]
        self.assertEqual(stats["top5_score"], 10)
        self.assertEqual(stats["rank6_10_score"], 0)
        self.assertEqual(stats["total_score"], 10)

    def test_rating_counts(self):
        ratings = ["〇"] * 3 + ["△"] * 4 + ["×"] * 3
        normalized = self._make_normalized(ratings, ["×"] * 10, ["×"] * 10)
        agg = p2h.aggregate_by_article_strategy(normalized)
        counts = agg[("A01", "L")]["counts"]
        self.assertEqual(counts, {"〇": 3, "△": 4, "×": 3})

    def test_ranking_lift_positive_when_top5_better(self):
        ratings = ["〇"] * 5 + ["×"] * 5
        normalized = self._make_normalized(ratings, ["×"] * 10, ["×"] * 10)
        agg = p2h.aggregate_by_article_strategy(normalized)
        self.assertGreater(agg[("A01", "L")]["ranking_lift"], 0)

    def test_ranking_lift_negative_when_rank6_10_better(self):
        ratings = ["×"] * 5 + ["〇"] * 5
        normalized = self._make_normalized(ratings, ["×"] * 10, ["×"] * 10)
        agg = p2h.aggregate_by_article_strategy(normalized)
        self.assertLess(agg[("A01", "L")]["ranking_lift"], 0)

    def test_cross_article_totals_and_stats(self):
        normalized = []
        for article_id, ratings in (("A01", ["〇"] * 10), ("A02", ["△"] * 10), ("ADD03", ["×"] * 10)):
            normalized += self._make_normalized(ratings, ["×"] * 10, ["×"] * 10, article_id=article_id)
        art_strat = p2h.aggregate_by_article_strategy(normalized)
        cross = p2h.aggregate_strategy_cross_article(art_strat)
        self.assertEqual(cross["L"]["total_total"], 20 + 10 + 0)
        self.assertEqual(cross["L"]["min_total_per_article"], 0)
        self.assertEqual(cross["L"]["max_total_per_article"], 20)
        self.assertEqual(cross["L"]["median_total_per_article"], 10)

    def test_rank1_counts_and_ties(self):
        normalized = []
        for article_id in p2h.ARTICLE_IDS:
            normalized += self._make_normalized(["〇"] * 10, ["〇"] * 10, ["×"] * 10, article_id=article_id)
        art_strat = p2h.aggregate_by_article_strategy(normalized)
        rank1 = p2h.compute_rank1_counts(art_strat)
        self.assertEqual(len(rank1["tie_articles"]), 3)
        self.assertEqual(rank1["rank1_counts"]["L"], 3)
        self.assertEqual(rank1["rank1_counts"]["P"], 3)
        self.assertEqual(rank1["rank1_counts"]["U"], 0)

    def test_rank_position_averages(self):
        ratings = ["〇"] + ["×"] * 9
        normalized = self._make_normalized(ratings, ["×"] * 10, ["×"] * 10)
        rank_avg = p2h.compute_rank_position_averages(normalized)
        self.assertEqual(rank_avg["L"][1], 2.0)
        self.assertEqual(rank_avg["L"][2], 0.0)

    def test_pairwise_wins_and_diffs(self):
        normalized = []
        for article_id in p2h.ARTICLE_IDS:
            normalized += self._make_normalized(["〇"] * 10, ["×"] * 10, ["△"] * 10, article_id=article_id)
        art_strat = p2h.aggregate_by_article_strategy(normalized)
        pairwise = p2h.compute_pairwise(art_strat)
        self.assertEqual(pairwise["L_vs_P"]["wins"], {"L": 3, "P": 0, "ties": 0})
        self.assertEqual(pairwise["L_vs_P"]["total_diff_sum"], 60)


class PriorReconciliationTests(unittest.TestCase):
    def test_recalculates_and_computes_delta(self):
        art_set = {
            ("A01", "A"): {"total_score": 14}, ("A01", "B"): {"total_score": 9}, ("A01", "C"): {"total_score": 16},
            ("A02", "A"): {"total_score": 16}, ("A02", "B"): {"total_score": 16}, ("A02", "C"): {"total_score": 11},
            ("ADD03", "A"): {"total_score": 16}, ("ADD03", "B"): {"total_score": 13},
            ("ADD03", "C"): {"total_score": 16},
        }
        result = p2h.reconcile_prior_aggregate(art_set)
        self.assertEqual(result["A01"]["A"], {"prior": 13, "recalculated": 14, "delta": 1})
        self.assertEqual(result["A01"]["B"], {"prior": 13, "recalculated": 9, "delta": -4})


class QaFailExtractionTests(unittest.TestCase):
    def test_extracts_only_fail_rows(self):
        rows = [
            {"extraction_form_qa_verdict": "PASS"},
            {"extraction_form_qa_verdict": "FAIL"},
            {"extraction_form_qa_verdict": "PASS"},
        ]
        fails = p2h.extract_qa_fails(rows)
        self.assertEqual(len(fails), 1)


class RealDataIntegrationTests(unittest.TestCase):
    """実際に保存されたP2G成果物とP2H raw TSVを使った統合確認。
    ファイルが存在しない環境ではskipする。"""

    def setUp(self):
        self.raw_path = "er003_output/p2h/ER-003-P2H_user_scores_raw.tsv"
        if not os.path.exists(self.raw_path):
            self.skipTest("raw TSVが見つかりません")
        if not os.path.exists("er003_output/p2g/A01/blind_mapping.json"):
            self.skipTest("P2G成果物が見つかりません")

    def test_all_90_rows_reconcile_successfully(self):
        with open(self.raw_path, encoding="utf-8") as f:
            rows = p2h.parse_raw_tsv(f.read())
        validation = p2h.validate_raw_rows(rows)
        self.assertTrue(validation["ok"], msg=validation["reasons"])
        normalized = p2h.reconcile_rows(rows)
        self.assertEqual(len(normalized), 90)

    def test_known_two_qa_fails_are_found(self):
        with open(self.raw_path, encoding="utf-8") as f:
            rows = p2h.parse_raw_tsv(f.read())
        normalized = p2h.reconcile_rows(rows)
        fails = p2h.extract_qa_fails(normalized)
        self.assertEqual(len(fails), 2)


if __name__ == "__main__":
    unittest.main()
