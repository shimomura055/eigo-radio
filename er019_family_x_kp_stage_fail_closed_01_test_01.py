# ============================================================
# er019_family_x_kp_stage_fail_closed_01_test_01.py
# FAMILY-X-KP-STAGE-FAIL-CLOSED-FIX-01(KPMP-03 委任_03、2026-10-22)
# 実行: .venv/Scripts/python.exe -m unittest er019_family_x_kp_stage_fail_closed_01_test_01 -v
# API呼び出し0(sc.run_key_phrases等は全てmock)。費用0。
# 対象: Family X runnerのKP stageが、kp_statusがPASS系以外のとき停止し(Family Zと対称)、
#       旧attemptの keywords_canonicalized.json を後段(TTS/assembly)が使わないこと。
# ============================================================
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

import er003_v1_n3_01_scaffold_generate as sc
import er019_family_x_audio_production_runner_01 as runner

ARTICLE = "P1.\n\nP2.\n\nP3.\n\nP4.\n"
PASS = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_PASS"},
        "m2_fallback_events": []}
INVALID = {"selection": {"status": "KEY_WORDS_STRUCTURE_PASS"}, "canonicalization": {"status": "CANONICALIZATION_INVALID"},
           "m2_fallback_events": []}
_REPO = os.getcwd()


def _setup(stale=True):
    """tmp作業dir(cwd)にer019_output/t/r/a2/article.mdを置き、out_dirにsupport texts(+旧KP残骸)を置く。"""
    work, out = tempfile.mkdtemp(), tempfile.mkdtemp()
    src = f"{work}/er019_output/t/r"
    os.makedirs(f"{src}/a2")
    open(f"{src}/a2/article.md", "w", encoding="utf-8").write(ARTICLE)
    os.makedirs(f"{out}/a2/key_phrases")
    open(f"{out}/a2/a2_support_texts.json", "w").write("{}")
    if stale:   # 旧attemptの(Redundancy NG済み等の)KP残骸
        open(f"{out}/a2/key_phrases/keywords_canonicalized.json", "w").write('{"stale": true}')
    return work, src, out


def _scaffold(src, out, kp, scaffold_only="kp"):
    with mock.patch.object(sc, "run_key_phrases", return_value=kp), \
         mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}), \
         mock.patch.object(runner, "run_family_x_a2_scaffold", return_value={}), \
         contextlib.redirect_stdout(io.StringIO()):
        return runner.run_theme_scaffold(None, src, out, ["a2"], scaffold_only=scaffold_only)


class FailureStatusTests(unittest.TestCase):
    def test_pass_family_returns_none(self):
        self.assertIsNone(runner.kp_stage_failure_status(PASS))
        self.assertIsNone(runner.kp_stage_failure_status(
            {"selection": {}, "canonicalization": {"status": "CANONICALIZATION_REVIEW_REQUIRED"}}))
        # gloss HR(別key。canonicalizationはPASS)は従来のHR経路で扱い、ここでは止めない
        self.assertIsNone(runner.kp_stage_failure_status(
            {"selection": {}, "canonicalization": {"status": "CANONICALIZATION_PASS"}, "status": "GLOSS_ALIGNMENT_HUMAN_REVIEW"}))

    def test_blocking_cases(self):
        cases = [
            (INVALID, "KP_STAGE_FAILED(CANONICALIZATION_INVALID)"),
            ({"selection": {"status": "SELECTION_FAILED"}, "canonicalization": None}, "KP_STAGE_FAILED(SELECTION_FAILED)"),
            ({"selection": {}, "canonicalization": {"status": "CANONICALIZATION_PASS"}, "redundancy_qa": {"status": "REDUNDANCY_NG"},
              "status": "NG_REVIEW_REQUIRED"}, "KP_STAGE_FAILED(NG_REVIEW_REQUIRED)"),
            ({"selection": {}, "canonicalization": None, "status": "OUTER_RETRY_EXHAUSTED"},
             "KP_STAGE_FAILED(OUTER_RETRY_EXHAUSTED)"),   # KPFT 委任_02: 旧db_hybrid記事cap停止statusは撤去
        ]
        for kp, want in cases:
            self.assertEqual(runner.kp_stage_failure_status(kp), want)

    def test_same_pass_literals_as_family_z(self):
        src = open(os.path.join(_REPO, "er026_family_z_fiction_production_runner_01.py"), encoding="utf-8").read()
        for lit in runner.KP_STAGE_PASS_CANON_STATUSES + ("NG_REVIEW_REQUIRED", "OUTER_RETRY_EXHAUSTED"):
            self.assertIn(f'"{lit}"', src)


class ScaffoldStopTests(unittest.TestCase):
    def test_blocked_statuses_record_full_summary_marker_and_skip_remaining_levels(self):
        for kp in (INVALID,
                   {"selection": {"status": "SELECTION_FAILED"}, "canonicalization": None},
                   {"selection": {}, "canonicalization": {"status": "CANONICALIZATION_PASS"}, "status": "NG_REVIEW_REQUIRED"}):
            work, src, out = _setup(stale=False)
            os.makedirs(f"{src}/b1b")
            open(f"{src}/b1b/article.md", "w", encoding="utf-8").write(ARTICLE)
            with mock.patch.object(sc, "run_key_phrases", return_value=kp) as m,                  mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}),                  mock.patch.object(runner, "run_family_x_a2_scaffold", return_value={}),                  contextlib.redirect_stdout(io.StringIO()):
                res = runner.run_theme_scaffold(None, src, out, ["a2", "b1b"], scaffold_only="kp")
            self.assertEqual(m.call_count, 1)   # b1bのKPは呼ばない
            self.assertNotIn("b1b", res)
            self.assertTrue(res["a2"]["kp_stage_status"].startswith("KP_STAGE_FAILED("))
            self.assertIn("kp_run_status", res["a2"])   # 既存summary項目(OF-KGCPW-04/16)は欠落しない
            mk = json.load(open(f"{out}/a2/key_phrases/{runner.KP_STAGE_FAILED_MARKER}", encoding="utf-8"))
            self.assertTrue(mk["status"].startswith("KP_STAGE_FAILED("))
            s = json.load(open(f"{out}/scaffold_run_summary.json", encoding="utf-8"))
            self.assertEqual(s["a2"]["kp_stage_status"], mk["status"])

    def test_pass_continues_without_marker(self):
        work, src, out = _setup(stale=False)
        res = _scaffold(src, out, PASS)
        self.assertEqual(res["a2"]["key_phrases_status"], "CANONICALIZATION_PASS")
        self.assertFalse(os.path.exists(f"{out}/a2/key_phrases/{runner.KP_STAGE_FAILED_MARKER}"))


class DownstreamNotRunTests(unittest.TestCase):
    """main(): scaffoldがKP失敗で止まったとき rc=3・entry_pointにStatus・TTS/assembly未実行。
    markerが残る状態の後続--stage tts/assembleも、旧KP残骸があっても実行しない。"""

    def setUp(self):
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)

    def _main(self, work, out, stage, kp=None, extra=()):
        os.chdir(work)
        argv = ["x", "--slug", "t", "--run", "r", "--out-dir", out, "--stage", stage, "--level", "a2", *extra]
        tts, asm = mock.Mock(), mock.Mock()
        patches = [mock.patch.object(sys, "argv", argv),
                   mock.patch.object(runner, "generate_family_x_a2_segments", tts),
                   mock.patch.object(runner, "stage_assemble_family_x_a2", asm),
                   mock.patch.object(runner, "assert_production_tts_backend"),
                   mock.patch.object(runner, "ensure_rf_record"),
                   mock.patch.object(runner, "assert_budget_ok"),
                   mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(0.0, {})),
                   mock.patch.object(sc, "run_key_phrases", return_value=kp or PASS),
                   mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}),
                   mock.patch.object(runner, "run_family_x_a2_scaffold", return_value={}),
                   mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", return_value=None)]
        rc = None
        with contextlib.ExitStack() as es:
            for p in patches:
                es.enter_context(p)
            es.enter_context(contextlib.redirect_stdout(io.StringIO()))
            try:
                runner.main()
            except SystemExit as e:
                rc = e.code
        return rc, tts, asm

    def test_stage_all_stops_rc3_and_records_status(self):
        work, src, out = _setup(stale=True)
        rc, tts, asm = self._main(work, out, "all", INVALID, ("--allow-legacy-backend",))
        self.assertEqual(rc, 3)
        tts.assert_not_called()
        asm.assert_not_called()
        ep = json.load(open(f"{out}/entry_point.json", encoding="utf-8"))
        self.assertEqual(ep["kp_stage_status"], {"a2": "KP_STAGE_FAILED(CANONICALIZATION_INVALID)"})

    def test_later_stage_tts_assemble_refuse_with_marker_even_if_stale_kp_exists(self):
        work, src, out = _setup(stale=True)
        self._main(work, out, "all", INVALID)
        for stage in ("tts", "assemble"):
            rc, tts, asm = self._main(work, out, stage)
            self.assertEqual(rc, 3)
            tts.assert_not_called()
            asm.assert_not_called()

    def test_resume_scaffold_rerun_pass_clears_marker_and_continues(self):
        work, src, out = _setup(stale=True)
        self._main(work, out, "all", INVALID)
        self.assertTrue(os.path.exists(f"{out}/a2/key_phrases/{runner.KP_STAGE_FAILED_MARKER}"))
        rc, tts, asm = self._main(work, out, "scaffold", PASS)   # 同stage再実行(PASS)
        self.assertIsNone(rc)
        self.assertFalse(os.path.exists(f"{out}/a2/key_phrases/{runner.KP_STAGE_FAILED_MARKER}"))
        rc, tts, asm = self._main(work, out, "tts")               # 以後のttsは従来どおり進む
        self.assertIsNone(rc)
        tts.assert_called()


if __name__ == "__main__":
    unittest.main()
