# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 / PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03: Part 2(文法)のX/Z runner配線の統合test(API 0)。
LLMはすべてmock(er120_part2_mock_01)、実API到達はnetblock harness(sitecustomize)で0を証明する(別途、実行時ログで確認)。
対象: 待機は1回(統合依頼書+rc=4/FamilyZKpReviewPending)・確定前はStep B 0 call・再開でStep A''を再実行しない・再実行はAPI 0・
      失敗はrc=3/STOP+案内1つ・事後Review(確定の変更)は再finalizeを要求・使う側の入口はfail-closed・Advancedだけに載る・0件固定文面。
実行: PYTHONPATH=netblock_harness_01 .venv/Scripts/python.exe -m pytest er120_part2_wiring_integration_test_01.py -q"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import io
import json
import os
import shutil
import sys
import unittest
from unittest import mock

import er019_family_x_audio_production_runner_01 as xr
import er026_family_z_fiction_production_runner_01 as r
import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g2
import er120_part2_mock_01 as pm
import er120_part2_wiring_01 as p2w
import er119_z_wiring_test_01 as zw
import er003_kp_general_explanation_01_runner_integration_test_01 as ri
from er119_test_support_01 import jl, rd

BAD_EXPLAIN = lambda prompt: ("壊れた出力(ITEM区切りなし)", pm.MODEL, {"input_tokens": 1, "output_tokens": 1, "cached_input_tokens": 0}, "bad")  # noqa: E731


def _decide_top1(study_dir, by="human"):
    return gr.op_decide(study_dir, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(study_dir)["candidates_sha256"], by=by)


# ============================================================
# Z
# ============================================================
class ZPart2Integration(zw.ZBase):
    def _select_kp(self):
        for lv in ("b1b", "a2"):
            rv.op_select(self.src[lv], kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if lv == "b1b" else None), by="human")

    def _pend(self):
        with self.assertRaises(r.FamilyZKpReviewPending) as cm:
            zw._quiet(r.run_stage, self.ctx, "kp")
        return cm.exception

    def _finish(self):
        self._select_kp()
        _decide_top1(r._part2_dir(self.ctx))
        zw._quiet(r.run_stage, self.ctx, "kp")

    def test_wait_is_one_unified_request_and_no_stepb_or_part1(self):
        exc = self._pend()
        kinds = [p.get("kind") for p in exc.pending]
        self.assertEqual(kinds.count("grammar"), 1)
        self.assertEqual(self.extract_calls(), 1)          # Step A''は確認前に1回
        self.assertEqual(self.explain_calls(), 0)          # Step Bは確認前に呼ばない
        self.assertEqual(self._kind_calls("kp_part1"), 0)  # Part 1も確認前に呼ばない
        import er119_kp_wiring_01 as kpw   # runner main()が出すbanner(統合依頼書も書く)
        banner = kpw.pending_banner(exc.pending, restart_command="py x --stage kp", run_dir=self.ctx.out_dir)
        self.assertEqual(banner.count(rv.PENDING_MARKER), 1)                  # 待機表示は1回
        self.assertTrue(os.path.exists(f"{self.ctx.out_dir}/review_request.md"))
        txt = rd(f"{self.ctx.out_dir}/review_request.md")
        self.assertIn("文法", txt)
        self.assertIn("KP", txt)
        self.assertFalse(os.path.exists(f"{r._part2_dir(self.ctx)}/{g2.RESULT_FILENAME}"))
        # 再実行(待機中)はAPI 0
        n = (self.extract_calls(), self.kp_calls())
        self._pend()
        self.assertEqual((self.extract_calls(), self.kp_calls()), n)

    def test_resume_runs_stepb_once_and_reuse_is_api0(self):
        self._pend()
        self._finish()
        self.assertEqual(self.extract_calls(), 1)          # 再開でStep A''を再実行しない
        self.assertEqual(self.explain_calls(), 1)
        self.assertTrue(os.path.exists(f"{r._part2_dir(self.ctx)}/{g2.RESULT_FILENAME}"))
        prov = r._prov(self.ctx)
        self.assertIsNotNone(prov.stage_entry("part2_b1b"))
        self.assertIsNotNone(prov.stage_entry("part2_cand_b1b"))
        zw._quiet(r.run_stage, self.ctx, "kp")             # 再実行
        self.assertEqual((self.extract_calls(), self.explain_calls()), (1, 1))

    def test_stepb_failure_stops_with_single_next_command_then_recovers_without_reextract(self):
        self._pend()
        self._select_kp()
        _decide_top1(r._part2_dir(self.ctx))
        good = self.ctx.hooks["part2_explain_call_fn"]
        self.ctx.hooks["part2_explain_call_fn"] = BAD_EXPLAIN
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            zw._quiet(r.run_stage, self.ctx, "kp")
        msg = str(cm.exception)
        self.assertEqual(msg.count("--regenerate-stage part2_b1b"), 1, msg)   # 案内は1つだけ
        self.assertTrue(os.path.exists(f"{r._part2_dir(self.ctx)}/{g2.FAILED_FILENAME}"))
        self.assertFalse(os.path.exists(f"{r._part2_dir(self.ctx)}/{g2.RESULT_FILENAME}"))   # 空欄/部分成果物で続行しない
        self.ctx.hooks["part2_explain_call_fn"] = good
        self.ctx.regenerate_stage = "part2_b1b"
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.ctx.regenerate_stage = None
        self.assertEqual(self.extract_calls(), 1)          # 回復でも再抽出しない
        self.assertTrue(os.path.exists(f"{r._part2_dir(self.ctx)}/{g2.RESULT_FILENAME}"))

    def test_posthoc_selection_change_requires_refinalize_without_reextract(self):
        self._pend()
        self._finish()
        sd = r._part2_dir(self.ctx)
        sig0 = gr.load_review(sd)["selection_signature"]
        doc = gr.load_candidates(sd)
        self.assertGreaterEqual(len(doc["candidates"]), 2)
        gr.op_decide(sd, choice="top2", reason="事後Review: 別の構文を採る", candidates_sha256=doc["candidates_sha256"], by="human")
        self.assertNotEqual(gr.load_review(sd)["selection_signature"], sig0)
        with self.assertRaises(Exception) as cm:
            zw._quiet(r.run_stage, self.ctx, "kp")
        self.assertIn("--regenerate-stage part2_b1b", str(cm.exception))
        self.ctx.regenerate_stage = "part2_b1b"
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.ctx.regenerate_stage = None
        self.assertEqual((self.extract_calls(), self.explain_calls()), (1, 2))
        self.assertEqual(jl(f"{sd}/{g2.RESULT_FILENAME}")["selection"]["candidate_id"], doc["candidates"][1]["candidate_id"])

    def test_consumer_entries_fail_closed(self):
        self._pend()
        with self.assertRaises((r.FamilyZKpReviewPending, r.FamilyZE2EStop)):
            r.load_level_inputs(self.ctx, "b1b")             # 未確定のままTTS入力へ進めない
        self._finish()
        r.load_level_inputs(self.ctx, "b1b")                 # 確定後は通る
        r.load_level_inputs(self.ctx, "a2")                  # Standardは対象外
        res = f"{r._part2_dir(self.ctx)}/{g2.RESULT_FILENAME}"
        good = rd(res)
        os.remove(res)
        with self.assertRaises((r.FamilyZE2EStop, g2.Part2Error)):
            r.load_level_inputs(self.ctx, "b1b")             # 結果欠落でSTOP(M-2)
        d = json.loads(good)
        d["selection"]["sentence"] = d["selection"]["sentence"] + " x"
        with open(res, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False))
        with self.assertRaises((r.FamilyZE2EStop, g2.Part2Error)):
            r.load_level_inputs(self.ctx, "b1b")             # 改変/古い結果でSTOP

    def _run_rest(self):
        rest = [s for s in r.E2E_STAGES if s not in zw.PRE and s not in ("kp", "page_verify")]
        zw._quiet(r.run_stages, self.ctx, rest)

    def test_pages_show_part2_after_part1_in_advanced_only_and_page_verify_checks_it(self):
        self._pend()
        self._finish()
        self._run_rest()
        index = rd(f"{self.ctx.pages_dir}/index.html")
        std = rd(f"{self.ctx.pages_dir}/standard.html")
        self.assertEqual(index.count("<section class='study'>"), 2)
        self.assertLess(index.index("Vocabulary &amp; Expressions"), index.index("Grammar &amp; Sentence Structure"))   # Part 1の直後
        self.assertLess(index.index("id='adv'"), index.index("Grammar &amp; Sentence Structure"))                   # Advancedの節
        self.assertNotIn("Grammar &amp; Sentence Structure", std)                                                  # Standardには出さない
        zw._quiet(r.run_stages, self.ctx, ["page_verify"])
        self.assertTrue(jl(f"{self.ctx.out_dir}/page_verify_local.json")["part2_verified"])
        # R-3: ページを改変すると不一致でSTOP
        with open(f"{self.ctx.pages_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(index.replace("Grammar &amp; Sentence Structure", "Grammar &amp; Something Else"))
        with self.assertRaises(Exception):
            zw._quiet(r.run_stages, self.ctx, ["page_verify"])

    def test_omit_renders_fixed_zero_text_and_is_not_counted_as_reviewed(self):
        self._pend()
        self._select_kp()
        sd = r._part2_dir(self.ctx)
        gr.op_decide(sd, choice="omit", reason="今回は解説を出さない", candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.assertEqual(self.explain_calls(), 0)          # 0件確定はStep Bを呼ばない
        self._run_rest()
        index = rd(f"{self.ctx.pages_dir}/index.html")
        self.assertIn(g2.ZERO_P2.replace("&", "&amp;"), index)

    def test_declared_absence_auto_adopts_top1_and_is_labelled_unreviewed(self):
        self.declare()
        zw._quiet(r.run_stage, self.ctx, "kp")
        sd = r._part2_dir(self.ctx)
        self.assertEqual(gr.load_review(sd)["status"], rv.ST_AUTO)          # UNREVIEWED_AUTO_ADOPTED(レビュー済みに数えない)
        self.assertEqual((self.extract_calls(), self.explain_calls()), (1, 1))


# ============================================================
# X
# ============================================================
class XPart2Integration(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)
        ri.isolate_part2(self)
        ri.no_decision_record(self)
        pm.CALLS.clear()
        self.work, self.src, self.out = ri._x_setup()
        os.remove(rv.declarations_path(self.out))          # 宣言なし=待機が既定
        self.addCleanup(shutil.rmtree, self.work, True)
        self.addCleanup(shutil.rmtree, self.out, True)
        self.sd = f"{self.out}/b1b/study_text"

    def _main(self, stage, *, client=None, extra=()):
        os.chdir(self.work)
        argv = ["x", "--slug", "t", "--run", "r", "--out-dir", self.out, "--stage", stage, "--level", "b1b", *extra]
        tts, asm = mock.Mock(), mock.Mock()
        patches = [mock.patch.object(sys, "argv", argv),
                   mock.patch.object(xr, "generate_family_x_b1_segments", tts),
                   mock.patch.object(xr, "stage_assemble_family_x_b1", asm),
                   mock.patch.object(xr, "assert_production_tts_backend"),
                   mock.patch.object(xr, "ensure_rf_record"),
                   mock.patch.object(xr, "assert_budget_ok"),
                   mock.patch.object(xr, "compute_cost_jpy_so_far", return_value=(0.0, {})),
                   mock.patch.object(ri._kpw, "run_kp_with_review", side_effect=ri._kp_writer(self.out)),
                   mock.patch.object(xr.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}),
                   mock.patch.object(xr, "run_family_x_b1_scaffold", return_value={}),
                   mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", return_value=client)]
        rc, buf = None, io.StringIO()
        with contextlib.ExitStack() as es:
            for p in patches:
                es.enter_context(p)
            es.enter_context(contextlib.redirect_stdout(buf))
            try:
                xr.main()
            except SystemExit as e:
                rc = e.code
        return rc, tts, asm, buf.getvalue()

    def test_wait_once_with_unified_request_and_no_stepb_or_part1(self):
        client = ri.FakeClient()
        rc, tts, asm, log = self._main("scaffold", client=client)
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        self.assertEqual(log.count(rv.PENDING_MARKER), 1)    # 待機表示は1回
        self.assertEqual(pm.CALLS, ["extract"])               # Step A''のみ
        self.assertEqual(client.calls, [])                    # Part 1も0
        self.assertTrue(os.path.exists(f"{self.out}/review_request.md"))
        self.assertFalse(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))
        tts.assert_not_called()
        # 待機中の再実行はAPI 0
        rc, *_ = self._main("scaffold", client=client)
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        self.assertEqual(pm.CALLS, ["extract"])

    def test_resume_runs_part1_and_stepb_once_then_reuse_is_api0(self):
        self._main("scaffold", client=ri.FakeClient())
        _decide_top1(self.sd)
        client = ri.FakeClient()
        rc, tts, asm, log = self._main("scaffold", client=client)
        self.assertIsNone(rc, log)
        self.assertEqual(pm.CALLS, ["extract", "explain"])   # Step A''は再実行しない
        self.assertEqual(len(client.calls), 2)                # Part 1: 解説1+訳1
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))
        again = ri.FakeClient()
        rc, *_ = self._main("scaffold", client=again)
        self.assertIsNone(rc)
        self.assertEqual(pm.CALLS, ["extract", "explain"])
        self.assertEqual(again.calls, [])

    def test_stepb_failure_is_rc3_with_failed_record_and_blocks_tts(self):
        self._main("scaffold", client=ri.FakeClient())
        _decide_top1(self.sd)
        with mock.patch.object(pm, "mock_explain_call_fn", BAD_EXPLAIN):
            rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient())
        self.assertEqual(rc, 3, log)
        self.assertIn("--stage study_text", log)
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.FAILED_FILENAME}"))
        tts.assert_not_called()
        rc, tts, asm, log = self._main("tts", client=ri.FakeClient())
        self.assertIn(rc, (3, 4))
        tts.assert_not_called()
        # 回復: --stage study_text(Part 2だけ。再抽出なし)
        rc, tts, asm, log = self._main("study_text", client=ri.FakeClient())
        self.assertIsNone(rc, log)
        self.assertEqual(pm.CALLS.count("extract"), 1)
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))

    def test_tts_and_assemble_entrances_wait_while_unconfirmed(self):
        self._main("scaffold", client=ri.FakeClient())
        for stage in ("tts", "assemble"):
            rc, tts, asm, log = self._main(stage, client=ri.FakeClient())
            self.assertIn(rc, (3, 4), stage)
            tts.assert_not_called()
            asm.assert_not_called()

    def test_player_shows_part2_after_part1_in_advanced_only_and_blocks_on_tamper(self):
        ri.decision_record(self, "T2")
        self._main("scaffold", client=ri.FakeClient())
        _decide_top1(self.sd)
        rc, *_ = self._main("scaffold", client=ri.FakeClient())
        self.assertIsNone(rc)
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, tts, asm, log = self._main("player", client=ri.FakeClient())
        self.assertIsNone(rc, log)
        page = rd(f"{self.out}/player.html")
        self.assertEqual(page.count("<section class='study'>"), 2)
        gp = page.index("Grammar &amp; Sentence Structure")
        self.assertLess(page.index("Vocabulary &amp; Expressions"), gp)
        self.assertLess(page.index("Advanced(B1)"), gp)
        self.assertLess(gp, page.index("Standard(A2)"))                    # Standardの節には出さない
        # 確定結果を改変するとplayerの入口が止まる(M-2)
        res = f"{self.sd}/{g2.RESULT_FILENAME}"
        d = json.loads(rd(res))
        d["selection"]["sentence"] = d["selection"]["sentence"] + " x"
        with open(res, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False))
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, *_ = self._main("player", client=ri.FakeClient())
        self.assertEqual(rc, 3)

    def test_public_builder_requires_confirmation_and_renders_part2_after_part1(self):
        ri.decision_record(self, "T2")
        self._main("scaffold", client=ri.FakeClient())
        article = rd(f"{self.src}/b1b/article.md")
        with self.assertRaises(p2w.Part2NotConfirmed):
            p2w.public_study_html(self.out, article)
        _decide_top1(self.sd)
        rc, *_ = self._main("scaffold", client=ri.FakeClient())
        self.assertIsNone(rc)
        html_text = p2w.public_study_html(self.out, article)
        self.assertEqual(html_text.count("<section class='study'>"), 2)
        self.assertLess(html_text.index("Vocabulary &amp; Expressions"), html_text.index("Grammar &amp; Sentence Structure"))
        os.remove(f"{self.sd}/{g2.RESULT_FILENAME}")
        with self.assertRaises(g2.Part2Error):
            p2w.public_study_html(self.out, article)


if __name__ == "__main__":
    unittest.main()
