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
            [{"id": str(i), "rewritten_segment": c, "changed_span_before": "Some",
              "changed_span_after": "x", "rewrite_type": "single_word_swap", "rationale": ""}
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
                ok = m.validate_candidate_is_full_segment(d["canonical_text"], c["rewritten_segment"])
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


if __name__ == "__main__":
    unittest.main()
