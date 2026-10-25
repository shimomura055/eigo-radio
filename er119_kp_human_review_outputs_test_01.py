# -*- coding: utf-8 -*-
"""KP Human Review: 検証5(verify_selection_matches_outputs)・公開版記録(R-5)の単体test。API 0。
実行: .venv\\Scripts\\python.exe -W error -m unittest er119_kp_human_review_outputs_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import unittest

import er119_kp_human_review_01 as rv
from er119_test_support_01 import Env, KpTestCase, jd, jl, wr


class TestVerifyOutputs(KpTestCase):
    def _final(self, **kw):
        env = Env(self.tmp, **kw)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.declare()
        self.assertEqual(self.ensure(env)["state"], "FINALIZED")
        return env

    def _write_outputs(self, kp_forms=None, vocab_forms=None):
        kp = jl(f"{self.kp_dir}/keywords_canonicalized.json")["items"]
        kp_forms = kp_forms or [it["used_form"] for it in sorted(kp, key=lambda x: x["rank"])]
        vocab_forms = vocab_forms or [it["used_form"] for it in rv.part1_items(self.kp_dir)]
        tts = os.path.join(self.tmp, "tts_results.json")
        jd(tts, {"key_phrases": {str(i): {"english": {"text": f}} for i, f in enumerate(kp_forms, 1)}})
        st = os.path.join(self.tmp, "study.json")
        jd(st, {"rows": [{"english_expression": f} for f in vocab_forms]})
        page = os.path.join(self.tmp, "page.html")
        wr(page, "<html>" + " ".join(f"<li>{f}</li>" for f in kp_forms) + "</html>")
        vpage = os.path.join(self.tmp, "vocab.html")
        wr(vpage, "<html>" + " ".join(f"<li>{f}</li>" for f in vocab_forms) + "</html>")
        return tts, st, page, vpage

    def test_consistent_outputs_pass(self):
        self._final()
        tts, st, page, vpage = self._write_outputs()
        rep = rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts, study_text_json=st,
                                                  page_paths=[page], vocab_page_paths=[vpage])
        self.assertTrue(rep["ok"])
        self.assertEqual(len(rep["kp"]), 3)
        self.assertEqual(len(rep["vocab"]), 5)

    def test_tts_text_mismatch_is_detected(self):
        self._final()
        tts, st, page, vpage = self._write_outputs(kp_forms=["other one", "other two", "other three"])
        with self.assertRaises(rv.KpReviewInconsistent) as e:
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)
        self.assertIn("TTSのKP英語text", str(e.exception))

    def test_study_text_and_page_mismatch_are_detected(self):
        self._final()
        tts, st, page, vpage = self._write_outputs(vocab_forms=["a", "b", "c", "d", "e"])
        with self.assertRaises(rv.KpReviewInconsistent) as e:
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", study_text_json=st)
        self.assertIn("Part 1", str(e.exception))
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", vocab_page_paths=[vpage])
        wr(page, "<html>nothing</html>")
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", page_paths=[page])

    def test_master_store_reused_tts_record_uses_canonical_text(self):
        """実run(KP-GRAMMAR-HR-PRODUCTION-01 R1)で判明: Master Store再利用のKP英語recordは`text`が無く`canonical_text`だけを持つ。"""
        self._final()
        tts, st, page, vpage = self._write_outputs()
        d = json.load(open(tts, encoding="utf-8"))
        for k, v in d["key_phrases"].items():
            v["english"] = {"status": "OK", "reused": True, "canonical_text": v["english"]["text"]}
        jd(tts, d)
        rep = rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)
        self.assertTrue(rep["ok"])
        d["key_phrases"]["2"]["english"]["canonical_text"] = "different phrase"
        jd(tts, d)
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)
        d["key_phrases"]["2"]["english"].pop("canonical_text")   # text/canonical_textとも無い=不一致(fail-closed)
        jd(tts, d)
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.verify_selection_matches_outputs(self.kp_dir, level="b1b", tts_results_path=tts)

    def test_legacy_run_is_out_of_scope(self):
        os.makedirs(self.kp_dir)
        self.assertEqual(rv.verify_selection_matches_outputs(self.kp_dir, level="b1b"), {"legacy": True, "ok": True})


class TestMarkPublished(KpTestCase):
    def test_mark_published_records_signature_and_later_review_does_not_auto_replace(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.declare()
        self.assertEqual(self.ensure(env)["state"], "FINALIZED")
        self.assertFalse(rv.published_diff(self.kp_dir)["differs"])
        rv.op_mark_published(self.kp_dir, by="ops")
        sig = rv.load_review(self.kp_dir)["selection_signature"]
        self.assertEqual(rv.published_diff(self.kp_dir)["published"], sig)
        self.assertFalse(rv.published_diff(self.kp_dir)["differs"])
        # 事後Review(AUTO->REVIEWED、別の選定): 確定版は変わるが公開版は自動では差し替わらない(差だけ表示)
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 4], vocab_ranks=[1, 2, 4, 5, 6], by="human")
        d = rv.published_diff(self.kp_dir)
        self.assertTrue(d["differs"])
        self.assertEqual(d["published"], sig)
        self.assertIn("自動では差し替えません", d["note"])

    def test_mark_published_requires_confirmed_and_by(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.assertEqual(self.ensure(env)["state"], "PENDING")
        with self.assertRaises(rv.KpReviewError):
            rv.op_mark_published(self.kp_dir, by="ops")
        with self.assertRaises(rv.KpReviewError):
            rv.op_mark_published(self.kp_dir, by="")


if __name__ == "__main__":
    unittest.main()
