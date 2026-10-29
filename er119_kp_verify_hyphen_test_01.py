# -*- coding: utf-8 -*-
"""KP確定とTTS記録のハイフン表記差(YSC03C)の回帰test。API 0。
実行: python -W error -m unittest er119_kp_verify_hyphen_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import unittest

import er119_kp_human_review_01 as rv
from er119_kp_human_review_outputs_test_01 import TestVerifyOutputs as _Base


class TestNorm(unittest.TestCase):
    def test_hyphen_space_case_equal(self):
        n = rv._kp_text_norm
        self.assertEqual(n("old-fashioned"), n("old fashioned"))
        self.assertEqual(n(" Old  Fashioned "), n("old-fashioned"))
        self.assertEqual(n("let go of"), n("let go of"))

    def test_different_words_differ(self):
        n = rv._kp_text_norm
        self.assertNotEqual(n("old-fashioned"), n("old fashion"))
        self.assertNotEqual(n("give up"), n("up give"))
        self.assertIsNone(n(None))


class TestVerifyHyphen(_Base):
    def test_hyphen_flip_passes(self):
        self._final()
        kp = rv._read_json(f"{self.kp_dir}/keywords_canonicalized.json")["items"]
        forms = [it["used_form"] for it in sorted(kp, key=lambda x: x["rank"])]
        flipped = [f.replace(" ", "-").upper() for f in forms]
        tts, st, page, vpage = self._write_outputs(kp_forms=flipped)
        # ページには確定表記を出す
        from er119_test_support_01 import wr
        wr(page, "<html>" + " ".join(f"<li>{f}</li>" for f in forms) + "</html>")
        rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)

    def test_word_missing_still_stops(self):
        self._final()
        kp = rv._read_json(f"{self.kp_dir}/keywords_canonicalized.json")["items"]
        forms = [it["used_form"] for it in sorted(kp, key=lambda x: x["rank"])]
        bad = [forms[0][:-1]] + forms[1:]
        tts, st, page, vpage = self._write_outputs(kp_forms=bad)
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)


if __name__ == "__main__":
    unittest.main()
