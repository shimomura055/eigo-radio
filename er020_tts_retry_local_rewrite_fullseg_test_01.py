#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OPEN-256: validate_candidate_is_full_segment の位置非依存化テスト(offline、API 0)。"""
from __future__ import annotations

import glob
import json
import os
import unittest

import er020_tts_retry_local_rewrite_01 as m

META = ("Some Muse calls were handed over to human workers, but not all of them. "
        "Were people told when a worker took over, and what did Meta change after the test?")
TAIL = (" were handed over to human workers, but not all of them. "
        "Were people told when a worker took over, and what did Meta change after the test?")
META_CANDS = {
    1: "Certain Muse calls" + TAIL,
    2: "Some of the Muse calls" + TAIL,
    3: "Some of Muse's calls" + TAIL,
    4: "A number of Muse calls" + TAIL,
    5: "Some calls involving Muse" + TAIL,
}
META_SPANS = {
    1: ("Some", "Certain"),
    2: ("Some Muse calls were handed", "Some of the Muse calls were handed"),
    3: ("Some Muse calls were handed", "Some of Muse's calls were handed"),
    4: ("Some Muse calls were handed", "A number of Muse calls were handed"),
    5: ("Some Muse calls", "Some calls involving Muse"),
}


class MetaComment2Test(unittest.TestCase):
    def test_all_five_real_candidates_pass_fullness(self):
        # 候補3/5は意味保存Gateで別途不合格(全文性とは別)。全文性は全件PASS。
        for i, c in META_CANDS.items():
            self.assertTrue(m.validate_candidate_is_full_segment(META, c), i)

    def test_old_rule_would_have_rejected(self):
        self.assertNotEqual(META[:15].lower(), META_CANDS[1][:15].lower())

    def test_other_gates_still_decide(self):
        span = m.find_problem_span_token_range(META, "Muse")
        qa_keys = ("meaning_preserved", "role_preserved", "fact_non_contradiction",
                   "context_connection", "natural_english")
        recs = m.build_full_candidate_records(
            META,
            [{"id": str(i), "rewritten_segment": c, "changed_span_before": META_SPANS[i][0],
              "changed_span_after": META_SPANS[i][1], "rewrite_type": "single_word_swap", "rationale": ""}
             for i, c in META_CANDS.items()],
            [{"candidate_id": str(i),
              **{k: {"pass": (i not in (3, 5) or k != "meaning_preserved"), "reason": ""}
                 for k in qa_keys}}
             for i in META_CANDS],
            span)
        by = {r["id"]: r for r in recs}
        for i in ("1", "2", "4"):
            self.assertTrue(by[i]["is_full_segment_format_valid"], i)
            self.assertEqual(by[i]["full_segment_check"]["reason"], "FULL_SEGMENT_OK")
            self.assertTrue(by[i]["all_seven_gates_pass"], i)
        for i in ("3", "5"):  # 意味保存Gate不合格は維持
            self.assertFalse(by[i]["all_seven_gates_pass"], i)


class RejectionTest(unittest.TestCase):
    def check(self, cand, reason):
        d = m.diagnose_candidate_full_segment(META, cand)
        self.assertFalse(d["ok"], cand)
        self.assertEqual(d["reason"], reason, cand)
        self.assertFalse(m.validate_candidate_is_full_segment(META, cand))

    def test_replacement_phrase_only(self):
        self.check("manage some calls for Muse", "TOO_SHORT_FRAGMENT")
        self.check("Certain Muse calls", "TOO_SHORT_FRAGMENT")

    def test_substring_fragment(self):
        # 原文の部分文字列(置換句のみ返し)は明示的に拒否
        self.check("Some Muse calls were handed over to human workers, but not all of them.",
                   "FRAGMENT_SUBSTRING_OF_ORIGINAL")

    def test_truncated_midsentence(self):
        d = m.diagnose_candidate_full_segment(META, META[:-25])
        self.assertFalse(d["ok"])

    def test_truncated_with_terminal_but_half(self):
        c = "Certain Muse calls were handed over to human workers, but not all of them."
        self.check(c, "TOO_SHORT_FRAGMENT")

    def test_missing_terminal_punct_near_full_length(self):
        self.check(META[:-1], "FRAGMENT_SUBSTRING_OF_ORIGINAL")
        c = META_CANDS[1][:-1]  # 置換済み・長さ十分だが終端なし(不完全文)
        self.check(c, "TERMINAL_PUNCTUATION_MISMATCH")

    def test_unrelated_full_text(self):
        c = ("The central bank held interest rates steady on Tuesday, citing slowing "
             "inflation and a cautious outlook for the labor market this year.")
        d = m.diagnose_candidate_full_segment(META, c)
        self.assertFalse(d["ok"])
        self.assertEqual(d["reason"], "LOW_ORIGINAL_COVERAGE_OVER_MODIFIED_OR_UNRELATED")

    def test_over_modified(self):
        c = ("Several Muse calls got passed along to staff members, though certainly "
             "not every single one. Did users hear about it when an employee stepped in, "
             "and what did Meta alter once testing ended?")
        d = m.diagnose_candidate_full_segment(META, c)
        self.assertFalse(d["ok"])
        self.assertEqual(d["reason"], "LOW_ORIGINAL_COVERAGE_OVER_MODIFIED_OR_UNRELATED")

    def test_over_expanded(self):
        self.check(META_CANDS[1] + " " + META[:120], "TOO_LONG_OVER_EXPANDED")

    def test_empty(self):
        self.assertFalse(m.validate_candidate_is_full_segment(META, ""))
        self.assertFalse(m.validate_candidate_is_full_segment("", "abc."))


class PositionTest(unittest.TestCase):
    ORIG = "Some Muse calls were handed over to workers, but the plan stayed secret until Friday."
    POS = {
        "start": ("Some Muse calls", "Certain Muse calls"),
        "middle": ("the plan stayed", "the plan remained"),
        "end": ("until Friday.", "until Monday."),
    }

    def test_pass_each_position(self):
        for name, (a, b) in self.POS.items():
            cand = self.ORIG.replace(a, b)
            self.assertNotEqual(cand, self.ORIG)
            self.assertTrue(m.validate_candidate_is_full_segment(self.ORIG, cand), name)

    def test_reject_replacement_only_each_position(self):
        for name, (a, b) in self.POS.items():
            self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, b), name)

    def test_reject_truncation(self):
        full = self.ORIG.replace("the plan stayed", "the plan remained")
        self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, full[:len(full) // 2] + "."))
        self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, full[len(full) // 2:]))


class JapaneseTest(unittest.TestCase):
    ORIG = "メタは一部の通話を人間の作業員に引き継ぎましたが、すべてではありませんでした。テスト後に何を変えましたか。"

    def test_pass_head_change(self):
        cand = self.ORIG.replace("一部の通話", "いくつかの通話")
        self.assertTrue(m.validate_candidate_is_full_segment(self.ORIG, cand))

    def test_reject_fragment_and_no_terminal(self):
        self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, "いくつかの通話"))
        self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, self.ORIG[:-1]))
        self.assertFalse(m.validate_candidate_is_full_segment(self.ORIG, self.ORIG[:25] + "。"))

    def test_reject_unrelated(self):
        self.assertFalse(m.validate_candidate_is_full_segment(
            self.ORIG, "今日は天気が良いので、公園まで散歩に出かけて、友達とお昼ご飯を食べました。夕方に帰宅しました。"))


class RegressionCorpusTest(unittest.TestCase):
    """er011記録の実候補: 旧rule採択(True)は引き続きPASS、旧rule拒否(False)は
    全て実際に全文だった(文頭置換)ためPASSへ救済される(拒否側の緩和ではない)。"""

    def test_recorded_candidates(self):
        files = sorted(glob.glob(os.path.join(
            "er011_output", "local_rewrite_recovery", "**", "local_rewrite_recovery_*.json"),
            recursive=True))
        if not files:
            self.skipTest("er011 records not present")
        n_old_true = n_old_false = 0
        for f in files:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
            for c in d["candidates"]:
                ng = d.get("ng_span") or {}
                pr = (m.find_problem_span_token_range(d["canonical_text"], " ".join(ng.get("canonical_changed_words") or []))
                      if ng.get("found") else {"found": False})
                ngt = pr["canon_tokens"][pr["start"]:pr["end"]] if pr.get("found") else []
                ok = m.validate_candidate_is_full_segment(d["canonical_text"], c["rewritten_segment"],
                                                          ng_changed_tokens=ngt)
                old = c.get("is_full_segment_format_valid")
                if old is True:
                    n_old_true += 1
                    self.assertTrue(ok, (f, c["id"]))
                elif old is False:
                    n_old_false += 1
                    self.assertTrue(ok, (f, c["id"]))  # 実際は全文(置換句のみではない)
                # 置換句のみへ縮めた版は常に拒否
                self.assertFalse(m.validate_candidate_is_full_segment(
                    d["canonical_text"], c.get("changed_span_after") or "x"))
        self.assertGreaterEqual(n_old_true, 70)
        self.assertGreaterEqual(n_old_false, 14)


# ---- OPEN-256 Opusレビュー是正(2026-10-11) ----
def diag_span(orig, cand, before, after, ng=None):
    return m.diagnose_candidate_full_segment(orig, cand, changed_span_before=before,
                                             changed_span_after=after, check_span=True,
                                             ng_changed_tokens=ng or [])


class PrefixLabelRejectTest(unittest.TestCase):
    """推奨3: 前置き・ラベル・先頭引用符は拒否(除去して通さない)。"""

    def test_reject_preamble_label_quote(self):
        for cand in (
            "Here is the rewrite: " + META_CANDS[1],
            "Rewrite 1: " + META_CANDS[1],
            '"' + META_CANDS[1],
            "“" + META_CANDS[1],
            "(" + META_CANDS[1],
        ):
            d = diag_span(META, cand, "Some", "Certain")
            self.assertFalse(d["ok"], cand)
            self.assertIn(d["reason"], ("LEADING_QUOTE_OR_LABEL_ADDED", "TOO_LONG_OVER_EXPANDED",
                                         "SPAN_INCONSISTENT_UNDECLARED_CHANGE"), cand)

    def test_original_with_quote_is_not_penalized(self):
        orig = '"Some Muse calls were handed over to human workers," the report said.'
        cand = orig.replace("Some", "Certain")
        self.assertTrue(m.validate_candidate_is_full_segment(orig, cand))

    def test_label_reason_code_for_short_label(self):
        d = diag_span(META, "Note: " + META_CANDS[1], "Some", "Certain")
        self.assertEqual(d["reason"], "LEADING_QUOTE_OR_LABEL_ADDED")


class WindowInternalEditTest(unittest.TestCase):
    """必須是正1/2: Gate6窓内の事実句削除・数字脱落・申告外の追加を機械的に拒否。"""
    ORIG = ("In 2024, Muse calls were handed over to human workers, but not all of them "
            "were reviewed by staff before the test ended.")

    def test_fact_phrase_deletion_in_window_rejected(self):
        cand = "Muse calls were handed over to human workers, but not all of them were reviewed by staff before the test ended."
        d = diag_span(self.ORIG, cand, "Muse", "Muse")  # 申告は無変更なのに句が消えている
        self.assertFalse(d["ok"])
        self.assertIn(d["reason"], ("NUMERIC_TOKEN_LOST", "SPAN_INCONSISTENT_UNDECLARED_CHANGE",
                                         "FRAGMENT_SUBSTRING_OF_ORIGINAL"))

    def test_number_loss_rejected_even_if_span_declared(self):
        # ng spanは "muse"。数字2024はng span外なので脱落は拒否される。
        cand = "Certain calls were handed over to human workers, but not all of them were reviewed by staff before the test ended."
        d = diag_span(self.ORIG, cand, "In 2024, Muse calls", "Certain calls", ng=["muse"])
        self.assertFalse(d["ok"])
        self.assertEqual(d["reason"], "NUMERIC_TOKEN_LOST")

    def test_undeclared_added_words_rejected(self):
        cand = self.ORIG.replace("Muse calls", "Certain Muse calls") .replace("handed over", "quietly handed over")
        d = diag_span(self.ORIG, cand, "Muse calls", "Certain Muse calls", ng=["muse"])
        self.assertFalse(d["ok"])
        self.assertEqual(d["reason"], "SPAN_INCONSISTENT_UNDECLARED_CHANGE")

    def test_undeclared_fact_removal_rejected(self):
        cand = self.ORIG.replace(", but not all of them", "").replace("Muse calls", "Certain Muse calls")
        d = diag_span(self.ORIG, cand, "Muse calls", "Certain Muse calls", ng=["muse"])
        self.assertFalse(d["ok"])

    def test_missing_declared_span_rejected(self):
        d = diag_span(self.ORIG, self.ORIG.replace("Muse", "Certain"), "", "")
        self.assertEqual(d["reason"], "SPAN_BEFORE_NOT_DECLARED")

    def test_legit_declared_change_passes(self):
        cand = self.ORIG.replace("Muse calls", "Certain Muse calls")
        d = diag_span(self.ORIG, cand, "Muse calls", "Certain Muse calls", ng=["muse"])
        self.assertTrue(d["ok"], d)
        self.assertEqual(d["reason"], "FULL_SEGMENT_OK")

    def test_ng_span_number_excluded_from_preservation(self):
        orig = "At the time of reporting, Brent was up about 2.6%, above $85 a barrel. It settled higher."
        cand = orig.replace("$85", "eighty-five dollars")
        ng = ["85xdollarx"]
        self.assertTrue(m.check_numeric_preservation(orig, cand, ng)["ok"])
        # ng spanでなければ脱落は拒否
        self.assertFalse(m.check_numeric_preservation(orig, cand, [])["ok"])
        # ng span外の数字(2.6)脱落は拒否
        cand2 = cand.replace("2.6%", "a few percent")
        r = m.check_numeric_preservation(orig, cand2, ng)
        self.assertFalse(r["ok"])
        self.assertEqual(r["reason"], "NUMERIC_TOKEN_LOST")

    def test_numeric_preserved_multiset(self):
        orig = "It rose 5% on Monday and 5% on Tuesday, then 12 on Friday."
        self.assertTrue(m.check_numeric_preservation(orig, orig.replace("rose", "climbed"))["ok"])
        self.assertFalse(m.check_numeric_preservation(orig, orig.replace("and 5%", "and"))["ok"])  # 重複数字の片方脱落


class Fixture90Test(unittest.TestCase):
    """実記録90件の固定fixture: 新ルール(全文性+span整合+数値保持+ラベル拒否)で
    旧採択76件は全てPASS(誤拒否0)、救済対象14件のうち拒否は申告外変更の1件のみ
    (それも既にGate6不合格で選択には影響しない)。"""
    PATH = os.path.join("er053_output", "family_x_tts_asr_rootcause_01", "open256_fixture_90records_01.json")

    def test_no_false_rejection(self):
        if not os.path.exists(self.PATH):
            self.skipTest("fixture not present")
        rows = json.load(open(self.PATH, encoding="utf-8"))
        self.assertEqual(len(rows), 90)
        old_ok = [r for r in rows if r["old_prefix15_rule_pass"]]
        self.assertEqual(len(old_ok), 76)
        rejected = []
        for r in rows:
            d = diag_span(r["canonical_text"], r["rewritten_segment"], r["changed_span_before"],
                          r["changed_span_after"], r["ng_changed_tokens"])
            if not d["ok"]:
                rejected.append((r["file"], r["id"], d["reason"], r["old_prefix15_rule_pass"]))
        self.assertEqual([x for x in rejected if x[3]], [], "旧採択からの誤拒否")
        self.assertEqual(len(rejected), 1, rejected)
        self.assertEqual(rejected[0][2], "SPAN_INCONSISTENT_UNDECLARED_CHANGE")
        self.assertTrue(rejected[0][0].endswith("tts_gemini_3_8_flash_lite_ab_trial_01/b/local_rewrite_recovery_full_story_part1.json")
                        and rejected[0][1] == "5")


class DocNoteTest(unittest.TestCase):
    def test_english_only_noted(self):
        self.assertIn("日本語経路は未対応", m.diagnose_candidate_full_segment.__doc__)


if __name__ == "__main__":
    unittest.main()
