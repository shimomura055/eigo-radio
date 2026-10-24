# -*- coding: utf-8 -*-
"""KP-CANON-REVIEW-REQUIRED-FIX-01(OPEN-504、2026-10-25)のtest。API 0(fake client)。
承認済み3状態モデル(CURRENT_SPEC:1964「REVIEW_REQUIREDは自動採用しない・人間確認後に採用可」)への整合是正:
X/Z共通の外側retryでREVIEW_REQUIRED -> 除外語付き再選定 -> PASSなら採用 / 上限到達 -> OUTER_RETRY_EXHAUSTED(HR停止)。
実行: py -m unittest er003_test_kp_review_required_retry_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import glob
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er003_key_words_gloss_alignment as ga
import er003_v1_n3_01_scaffold_generate as sc
import er011_key_phrase_set_redundancy_qa_01 as rq
import er105_kp_fulltext_selector_01 as ft
import er019_family_x_audio_production_runner_01 as xr
import er062_family_z_writer_01 as w62
from er003_test_kp_fulltext_wiring_01 import (ARTICLE, _Patched, fake_canon_factory, fake_gloss_factory, fake_red_factory,
                                              selector_seq)

A = [{"phrase": "pushed prices up", "word_count": 3}, {"phrase": "time lag", "word_count": 2}]
B = [{"phrase": "took a sharp turn", "word_count": 4}, {"phrase": "time lag", "word_count": 2}]
QA_FAIL_FIELD = "qa_listening_blocker_value_preserved"


def canon_review_required(bad_key_phrases):
    """key_phraseが bad_key_phrases に含まれるitemのQAを1項目FAILにする(構造は合格=REVIEW_REQUIRED)。"""
    base = fake_canon_factory()

    def factory(um, **kw):
        inner = base(um, **kw)

        def fn():
            raw, m, r = inner()
            doc = json.loads(raw)
            for row in doc["items"]:
                if bad_key_phrases is None or row["key_phrase"] in bad_key_phrases:
                    row[QA_FAIL_FIELD] = "FAIL"
            return json.dumps(doc, ensure_ascii=False), m, r
        return fn
    return factory


class _Base(_Patched):
    def _run(self, seq, canon_factory, runner="shared", sub="kp"):
        mk, st = selector_seq(seq)
        d = os.path.join(self.tmp, sub)
        with mock.patch.object(ft, "make_selector_fn", lambda msg, **kw: mk(msg)), \
                mock.patch.object(kc, "make_canonicalization_fn", canon_factory), \
                mock.patch.object(ga, "make_alignment_fn", fake_gloss_factory()), \
                mock.patch.object(rq, "make_redundancy_qa_fn", fake_red_factory([])), \
                mock.patch("time.sleep", lambda s: None):
            if runner == "shared":   # X: sc.run_key_phrases(kp_backend=fulltext_p2)
                res = sc.run_key_phrases(ARTICLE, d, "aid", "B1", process="B1_SUPPORT", kp_backend="fulltext_p2", stop_run_dir=self.tmp)
            else:                    # Z: w62の薄いdelegate(Z Production既定のkp_fn)
                os.makedirs(d, exist_ok=True)
                res = w62.run_kp_with_outer_retry_fulltext(ARTICLE, d, "aid", "B1", process="B1_SUPPORT")
        return d, res, st


class TestReviewRequiredRetry(_Base):
    def test_fake_really_yields_review_required(self):
        items = [{"rank": 1, "display_phrase": "pushed prices up", "source_span": "pushed prices up", "source_sentence": "s"}]
        row = {"rank": 1, "key_phrase": "pushed prices up", "changed_from_display_phrase": False,
               "normalization_reason": "none", "reasoning": "r", **{f: "PASS" for f in kc.QA_FIELDS}}
        row[QA_FAIL_FIELD] = "FAIL"
        self.assertEqual(kc.validate_canonicalization_response({"items": [row]}, items)["status"], "CANONICALIZATION_REVIEW_REQUIRED")

    def _check_retry_then_pass(self, runner):
        d, res, st = self._run([A, B], canon_review_required({"pushed prices up"}), runner=runner)
        self.assertNotIn("status", res, res.get("status"))
        self.assertEqual(res["canonicalization"]["status"], "CANONICALIZATION_PASS")
        log = res["outer_retry_log"]
        self.assertEqual(len(log), 2)
        self.assertEqual(log[0]["canonicalization_status"], "CANONICALIZATION_REVIEW_REQUIRED")
        self.assertEqual(log[0]["excluded_phrases_added"], ["pushed prices up"])
        self.assertEqual(log[0]["review_required_ranks"], [1])
        self.assertEqual(log[1]["canonicalization_status"], "CANONICALIZATION_PASS")
        body = st["messages"][1].split(ft.BODY_DELIMITER, 1)[1]
        self.assertIn("「pushed prices up」", body)
        self.assertIn(QA_FAIL_FIELD, body)
        doc = json.load(open(f"{d}/keywords_canonicalized.json", encoding="utf-8"))
        self.assertEqual([it["display_phrase"] for it in doc["items"]], ["took a sharp turn", "time lag"])
        self.assertTrue(glob.glob(f"{d}/keywords_canonicalized.STALE_attempt1.json"))
        self.assertTrue(os.path.exists(f"{d}/outer_retry/attempt_1/keywords_canonicalized.json"))   # 証跡は保持

    def test_x_path_review_required_then_pass_adopts_only_pass(self):
        self._check_retry_then_pass("shared")

    def test_z_path_review_required_then_pass_adopts_only_pass(self):
        self._check_retry_then_pass("z")

    def _check_exhausted(self, runner):
        # 全attemptで全itemがQA FAIL(再選定でも解消しない) -> 通算max_outer回で停止。KPを採用しない
        d, res, st = self._run([A, B, [{"phrase": "set is set", "word_count": 3}]], canon_review_required(None), runner=runner)
        self.assertEqual(res.get("status"), "OUTER_RETRY_EXHAUSTED")
        self.assertFalse(os.path.exists(f"{d}/keywords_canonicalized.json"), "最終失敗でKPが本名で残らない")
        self.assertTrue(glob.glob(f"{d}/keywords_canonicalized.STALE_attempt*.json"))
        self.assertEqual(len(res["outer_retry_log"]), sc.KP_OUTER_RETRY_MAX)
        self.assertEqual(res["outer_retry_log"][0]["canonicalization_status"], "CANONICALIZATION_REVIEW_REQUIRED")
        return res

    def test_x_path_exhausted_stops_x_stage(self):
        res = self._check_exhausted("shared")
        self.assertEqual(xr.kp_stage_failure_status(res), "KP_STAGE_FAILED(OUTER_RETRY_EXHAUSTED)")

    def test_z_path_exhausted(self):
        res = self._check_exhausted("z")
        self.assertEqual(res["status"], "OUTER_RETRY_EXHAUSTED")

    def test_pass_first_try_unchanged(self):
        d, res, _ = self._run([A], fake_canon_factory())
        self.assertNotIn("status", res)
        self.assertEqual(len(res["outer_retry_log"]), 1)
        self.assertNotIn("review_required_ranks", res["outer_retry_log"][0])
        self.assertTrue(os.path.exists(f"{d}/keywords_canonicalized.json"))


class TestStageLevelNeverAdoptsReviewRequired(unittest.TestCase):
    """多層防御: 外側retryを経ない結果(保存結果の再利用/hook)がREVIEW_REQUIREDでも、X/Z stageは採用しない。"""

    def test_x_stage_gate(self):
        self.assertEqual(xr.KP_STAGE_PASS_CANON_STATUSES, ("CANONICALIZATION_PASS",))
        self.assertEqual(xr.kp_stage_failure_status({"selection": {}, "canonicalization": {"status": "CANONICALIZATION_REVIEW_REQUIRED"}}),
                         "KP_STAGE_FAILED(CANONICALIZATION_REVIEW_REQUIRED)")
        self.assertIsNone(xr.kp_stage_failure_status({"selection": {}, "canonicalization": {"status": "CANONICALIZATION_PASS"}}))

    def test_z_stage_gate_raises_stop(self):
        import er026_family_z_fiction_production_runner_01 as r
        tmp = tempfile.mkdtemp()
        ctx = r.build_mock_context(tmp)
        with contextlib.redirect_stdout(io.StringIO()):
            r.run_stages(ctx, ["seed_check", "writer", "std_adjust", "plan", "support"])
        rr = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"},
              "canonicalization": {"status": "CANONICALIZATION_REVIEW_REQUIRED", "merged": {"items": []}},
              "redundancy_qa": {"status": "REDUNDANCY_OK"}, "redundancy_retry_log": []}
        ctx.hooks["kp_fn"] = lambda *a, **k: rr
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(r.FamilyZE2EStop) as cm:
            r.run_stage(ctx, "kp")
        self.assertIn("FAMILY_Z_KP_NOT_PASSED", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
