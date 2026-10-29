# -*- coding: utf-8 -*-
"""KP Human Review CLI(er119_kp_human_review_cli_01)の単体test。API 0。
実行: .venv\\Scripts\\python.exe -W error -m unittest er119_kp_human_review_cli_01_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import argparse
import contextlib
import io
import json
import os
import unittest

import er119_kp_human_review_01 as rv
import er119_kp_human_review_cli_01 as cli
from er119_test_support_01 import CALL1, Env, KpTestCase, jd, jl, make_legacy_flagged, rd


def run_cli(args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = cli.run(args)
    return rc, out.getvalue(), err.getvalue()


class TestCli(KpTestCase):
    def _gen(self, **kw):
        env = Env(self.tmp, **kw)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.assertEqual(self.ensure(env)["state"], "PENDING")
        return env

    def test_status_lists_pending_levels(self):
        self._gen()
        rc, out, _ = run_cli(["status", "--run", self.run_dir])
        self.assertEqual(rc, 0)
        d = json.loads(out)
        self.assertEqual(d["pending"], ["b1b"])
        self.assertEqual(d["levels"][0]["status"], rv.ST_PENDING)

    def test_show_prints_candidate_table_and_commands(self):
        self._gen()
        rc, out, _ = run_cli(["show", "--run", self.run_dir, "--level", "b1b"])
        self.assertEqual(rc, 0)
        self.assertIn("| 番号 |", out)
        self.assertIn("pushed prices up", out)
        self.assertIn("declare-absent", out)
        self.assertIn("select --run", out)
        md = rd(f"{self.kp_dir}/kp_human_review_request.md")
        self.assertIn("再開", md)

    def test_select_and_json_input(self):
        self._gen()
        rc, out, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--kp", "1,2,3", "--vocab", "1,2,3,4,5", "--ng", "6:不要", "--by", "tester"])
        self.assertEqual(rc, 0, err)
        r = rv.load_review(self.kp_dir)
        self.assertEqual(r["status"], rv.ST_REVIEWED)
        self.assertEqual(r["verdicts"][rv.candidate_id_for("insiders")], "NG")
        self.assertEqual(r["verdicts"][rv.candidate_id_for("blends")], "NOT_SELECTED")   # 見たが選ばなかった=NGではない
        self.assertEqual(r["verdicts"][rv.candidate_id_for("pushed prices up")], "SELECTED_KP")
        self.assertEqual(r["verdicts"][rv.candidate_id_for("spike")], "SELECTED_VOCAB")
        # --from-json
        jd(os.path.join(self.tmp, "sel.json"), {"kp": [1, 2, 3], "vocab": [1, 2, 3, 4], "by": "tester2"})
        rc, out, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--from-json", os.path.join(self.tmp, "sel.json")])
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(rv.load_review(self.kp_dir)["selection"]["vocab"]), 4)

    def test_refusals_return_rc2_and_do_not_change_state(self):
        self._gen()
        before = jl(f"{self.kp_dir}/kp_human_review.json")
        rc, _, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--kp", "1,2,3,4", "--vocab", "1,2,3,4", "--by", "t"])
        self.assertEqual(rc, 2)
        self.assertIn("REFUSED", err)
        rc, _, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--kp", "1,2,3", "--vocab", "1,2,3"])   # --by無し
        self.assertEqual(rc, 2)
        rc, _, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--kp", "1", "--vocab", "1", "--ng", "2", "--by", "t"])   # NG理由なし
        self.assertEqual(rc, 2)
        self.assertEqual(jl(f"{self.kp_dir}/kp_human_review.json"), before)

    def test_accept_ai_requires_displayed_sha(self):
        self._gen()
        rc, _, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--accept-ai", "--by", "t"])
        self.assertEqual(rc, 2)
        sha = rv.load_candidates(self.kp_dir)["candidates_sha256"]
        rc, out, err = run_cli(["select", "--run", self.run_dir, "--level", "b1b", "--accept-ai", "--candidates-sha", sha, "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertTrue(rv.load_review(self.kp_dir)["accept_ai_default"])

    def test_reselect_and_ng_and_unng(self):
        self._gen(call1_seq=[CALL1, CALL1])
        rc, out, err = run_cli(["reselect", "--run", self.run_dir, "--level", "b1b", "--ng", "1:不自然", "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertIn("RESTART_STORM", out)
        r = rv.load_review(self.kp_dir)
        self.assertEqual(r["status"], rv.ST_RESELECT)
        self.assertEqual(r["reselect_count"], 1)
        self.assertEqual(len(rv.store_load_ng("x", "coffee", "b1b")), 1)
        rc, out, err = run_cli(["unng", "--run", self.run_dir, "--level", "b1b", "--phrase", "pushed prices up", "--reason", "誤判定", "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(rv.store_load_ng("x", "coffee", "b1b"), [])

    def test_declare_absent_runs_and_ai_requires_user_ref(self):
        rc, out, err = run_cli(["declare-absent", "--runs", self.run_dir, "--reason", "不在", "--by", "Fable"])
        self.assertEqual(rc, 2)
        self.assertIn("user-ref", err)
        rc, out, err = run_cli(["declare-absent", "--runs", self.run_dir, "--reason", "不在", "--by", "Fable", "--user-ref", "ユーザー発言2026-10-26"])
        self.assertEqual(rc, 0, err)
        d = jl(os.path.join(self.run_dir, "kp_review_mode.json"))
        self.assertEqual(d["declarations"][0]["rounds"], [1])
        self.assertEqual(d["declarations"][0]["source"], "declare_absent_cli")
        # 委任_03(R-7撤去): 範囲/期限の宣言引数はCLIに存在しない(argparseが拒否。宣言ファイルも増えない)
        before = open(os.path.join(self.run_dir, "kp_review_mode.json"), encoding="utf-8").read()
        for bad in (["--scope-family", "x"], ["--scope-date", "2026-10-26"], ["--until", "2999-01-01T00:00:00+09:00"]):
            with self.assertRaises((SystemExit, argparse.ArgumentError)):
                run_cli(["declare-absent", "--runs", self.run_dir, *bad, "--reason", "r", "--by", "user"])
        with self.assertRaises((SystemExit, argparse.ArgumentError)):   # runs必須
            run_cli(["declare-absent", "--reason", "r", "--by", "user"])
        self.assertEqual(before, open(os.path.join(self.run_dir, "kp_review_mode.json"), encoding="utf-8").read())

    def test_declare_then_run_auto_then_status(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        rc, *_ = run_cli(["declare-absent", "--runs", self.run_dir, "--reason", "不在", "--by", "user"])
        self.assertEqual(rc, 0)
        self.assertEqual(self.ensure(env)["state"], "FINALIZED")
        rc, out, _ = run_cli(["status", "--run", self.run_dir])
        self.assertEqual(json.loads(out)["levels"][0]["status"], rv.ST_AUTO)

    def test_resolve_gloss_cli(self):
        """旧doc(仕様①より前に gloss HR待ちが旗付きで保存された候補doc)のresolve-gloss救済は残置。新docではHR待ち候補は提示されない(除外+補完)。"""
        self._gen()
        make_legacy_flagged(self.kp_dir, [3], gloss_hr=[3])
        rc, out, err = run_cli(["resolve-gloss", "--run", self.run_dir, "--level", "b1b", "--rank", "3", "--gloss", "時間差", "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertFalse(rv.load_candidates(self.kp_dir)["candidates"][2]["flags"]["gloss_hr_pending"])


if __name__ == "__main__":
    unittest.main()
