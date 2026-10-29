# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C Track D: ニュアンス解説のrunner配線(N0/N1/finalize・resume/retry/regeneration・LEGACY・CLI)のtest。全てmock・API 0。

対象(ユーザー正式決定2026-10-29 §2A・§2B・§2D・§2E、Opus M-1/M-2/M-3/M-4/R-3/R-4/R-5/R-7、WIRING_DESIGN_01 §8/§9):
  N0=新規KP review作成時だけspec発行(既存run=LEGACY=生成0・待機0・表示0・ファイルも作らない) / N1=KP候補生成後・HR提示前・resumeはAPI 0 /
  確定済みの採否はsidecarから決定論で導出(再生成・resume・regeneration・再起動で不変、LLM 0) / 不採用後に代替候補を補充しない /
  0件・不採用でコーナーが空枠含めて出ない / 技術失敗(API障害)は非ブロッキング / 未確定でページ入口=rc=4(Part2NotConfirmed) / 本文と確定の不整合=STOP /
  CLI nuance-show・nuance-select がV3フォーム経路と同じsidecarを作る / X・Y・Zの3 runnerが同一契約(共通関数 er134.n1_stage・er120_part2_wiring.finalize_nuance)を呼ぶ。
実行: .venv/Scripts/python.exe -m pytest er134_nuance_runner_wiring_test_01.py -q
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import io
import json
import os
import re
import shutil
import unittest
from unittest import mock

import er019_family_x_audio_production_runner_01 as X
import er026_family_z_fiction_production_runner_01 as Z
import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er119_kp_human_review_cli_01 as cli
import er119_kp_wiring_01 as kw
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
import er121_family_y_runner_01 as Y
import er128_kp_confirmed_content_01 as cc
import er134_nuance_explanation_01 as nx
import er134_nuance_explanation_01_test_01 as nt
from er119_test_support_01 import Env, jl, jd, rd, wr
from er128_kp_confirmed_content_grammar_v2_test_01 import PARAS, LABEL
from er128_nuance_hr_test_01 import NBase, QUOTE

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC_FILES = ("nuance_spec.json", "nuance_candidate.json", "nuance_failed.json", "nuance_result.json", "confirmed_nuance.json", "nuance_human_review_request.md")


class WBase(NBase):
    def setUp(self):
        super().setUp()
        self.n_calls = 0

    def ready(self, env, level="b1b"):
        """KP候補+review(PENDING)+文法Top1/Top2事前生成まで(runnerがN1を呼ぶ時点)。"""
        cands = self._gen(env, level=level)
        sd = self.prep_grammar(level)
        return sd, cands

    def mk_inputs(self, sd, level="b1b"):
        cands, review = rv.load_candidates(self.kpd(level)), rv.load_review(self.kpd(level))
        return nx.build_inputs(family="x", article_id="a", title=LABEL, level=level, paragraphs=PARAS, kp_cands=cands, grammar_items=nx.grammar_items_of(sd),
                               std_part1=bool(review.get("std_part1", True)))

    def n1(self, sd, level="b1b", *, review_existed=False, gen=None, judge=None, same=(), **kw_):
        inp = self.mk_inputs(sd, level)
        gen = gen or nt.Fn(nt.gen_json(expression="nobody vs no one", quote=QUOTE))
        judge = judge or nt.Fn(nt.judge_json(inp, same=same))
        res = nx.n1_stage(family="x", run_dir=self.run_dir, kp_dir=self.kpd(level), study_dir=sd, level=level, article_id="a", title=LABEL, paragraphs=PARAS,
                          review_existed=review_existed, call_fn=gen, judge_fn=judge, **kw_)
        return res, gen, judge

    def fin(self, sd, level="b1b"):
        return nx.finalize_stage(sd, PARAS, level=level, kp_dir=self.kpd(level), run_hint=self.run_dir)

    def page(self, sd, level="b1b"):
        res = p2w.finalize_nuance(sd, PARAS, level=level, kp_dir=self.kpd(level), run_hint=self.run_dir, next_command="rerun")
        return p2w.compose_page_html("", {"status": "NO_CANDIDATES"}, nuance=res), res

    def form_confirm(self, sd, decision):
        cands = rv.load_candidates(self.kp_dir)
        doc = jl(os.path.join(sd, "nuance_candidate.json"))
        nz = self.nz(doc, decision) if decision else None
        return self.confirm(self.payload_with(cands, nz)), doc


def assert_no_corner(tc, html):
    tc.assertNotIn(g.NUANCE_HEADING, html)
    tc.assertEqual(g.count_nuance_blocks(html), 0)
    tc.assertEqual(g.count_empty_study_sections(html), 0)


# ============================================================
# T1 N0(spec発行)+N1(候補生成)
# ============================================================
class T1_N0N1(WBase):
    def test_new_review_issues_spec_generates_once_and_resume_is_api_zero(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            r1, gen, judge = self.n1(sd, review_existed=False)
            self.assertEqual((r1["state"], r1["status"]), ("SPEC_ISSUED", "CANDIDATE"))
            self.assertEqual((gen.n, judge.n), (1, 1))                                    # 生成1+独立判定1
            self.assertTrue(os.path.exists(os.path.join(sd, "nuance_spec.json")))
            self.assertEqual(r1["pending"]["kind"], "nuance")
            self.assertIn(g.NUANCE_HEADING.replace("解説", ""), "ニュアンス")
            self.assertIn("nobody vs no one", rd(r1["pending"]["request_md"]))           # 依頼書に候補全文(統合依頼書に連結される)
            self.assertIn("nuance-select", rd(r1["pending"]["request_md"]))               # フォームを使わない面の案内
            gen2 = nt.Fn(nt.gen_json())
            r2, gen2, judge2 = self.n1(sd, review_existed=True, gen=gen2, judge=nt.Fn("x"))   # resume(KP reviewは既存)
            self.assertEqual((r2["reused"], r2["api_calls"], gen2.n, judge2.n), (True, 0, 0, 0))
            self.assertEqual(r2["status"], "CANDIDATE")
            self.assertIsNotNone(r2["pending"])                                           # HR未確定の間は待機itemを返し続ける

    def test_existing_review_without_spec_is_legacy_zero_everything(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            before = sorted(os.listdir(sd))
            gen, judge = nt.Fn("boom"), nt.Fn("boom")
            r, gen, judge = self.n1(sd, review_existed=True, gen=gen, judge=judge)        # 既存run(KP reviewは前から有る)=遡及なし
            self.assertEqual((r["state"], r["status"], r["api_calls"], r["pending"]), (nx.ST_LEGACY, None, 0, None))
            self.assertEqual((gen.n, judge.n), (0, 0))
            self.assertEqual(sorted(os.listdir(sd)), before)                               # ファイルも作らない
            self.assertTrue(all(not os.path.exists(os.path.join(sd, f)) for f in SPEC_FILES))
            self.assertIsNone(self.fin(sd))                                                # finalize=None(従来出力と同一)
            html, res = self.page(sd)
            self.assertIsNone(res)
            assert_no_corner(self, html)
            self.assertFalse(os.path.exists(os.path.join(sd, "nuance_result.json")))

    def test_no_kp_candidates_skips_without_spec(self):
        sd = os.path.join(self.run_dir, "b1b", "study_text")
        r = nx.n1_stage(family="x", run_dir=self.run_dir, kp_dir=self.kp_dir, study_dir=sd, level="b1b", article_id="a", title=LABEL, paragraphs=PARAS,
                        review_existed=False, call_fn=nt.Fn("x"), judge_fn=nt.Fn("x"))
        self.assertEqual((r["state"], r["api_calls"]), ("SKIPPED", 0))
        self.assertFalse(os.path.exists(os.path.join(sd, "nuance_spec.json")))

    def test_confirmed_decision_blocks_regeneration_even_if_everything_else_changes(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "adopt")
            boom = nt.Fn(exc=RuntimeError("must not call"))
            r, gen, judge = self.n1(sd, review_existed=True, gen=boom, judge=boom)
            self.assertEqual((r["state"], r["api_calls"], boom.n, r["pending"]), ("CONFIRMED", 0, 0, None))

    def test_auto_adopted_review_generates_nothing_and_finalizes_none(self):
        with Env(self.tmp) as env:
            self.confirm_auto(env)                                                         # 不在宣言=人間の採否が無い
            sd = self.prep_grammar("b1b")
            r, gen, judge = self.n1(sd, review_existed=False)
            self.assertEqual((r["status"], r["api_calls"], gen.n), (nx.ST_NO_CANDIDATE, 0, 0))
            self.assertEqual(jl(os.path.join(sd, "nuance_candidate.json"))["no_candidate_reason"], nx.R_AUTO_ADOPTED)
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_NONE)
            assert_no_corner(self, html)

    def test_technical_failure_is_non_blocking_and_page_completes_without_corner(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            r, gen, judge = self.n1(sd, review_existed=False, gen=nt.Fn(exc=ConnectionError("API down")), judge=nt.Fn("x"))   # 生成API失敗
            self.assertEqual((r["state"], r["status"], r["pending"]), ("SPEC_ISSUED", nx.ST_FAILED_TECHNICAL, None))          # 例外にならず、HR待機も作らない
            self.assertTrue(os.path.exists(os.path.join(sd, "nuance_failed.json")))
            html, res = self.page(sd)                                                      # ページ生成が止まらず『ニュアンス無し』で完結
            self.assertEqual((res["status"], res["reason"]), (nx.ST_RESULT_NONE, "failed_technical:api_error"))
            assert_no_corner(self, html)

    def test_stop_class_exceptions_propagate_not_swallowed(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            bad_model = nt.Fn(nt.gen_json(), model="gpt-other")
            with self.assertRaises(nx.NuanceModelContractError):                          # 応答model不一致=fallbackせずSTOP
                self.n1(sd, review_existed=False, gen=bad_model)

            def stop_guard(process, prompt, attempt):
                raise KeyboardInterrupt("budget/STOP")
            with self.assertRaises(KeyboardInterrupt):
                self.n1(sd, review_existed=False, budget_guard=stop_guard)


# ============================================================
# T2 finalize(ページ入口)と表示/非表示(採用1件・不採用・0件・技術失敗)
# ============================================================
class T2_FinalizeAndDisplay(WBase):
    def test_adopted_shows_one_corner_and_result_is_idempotent(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "adopt")
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_ADOPTED)
            self.assertEqual(g.count_nuance_blocks(html), 1)
            self.assertIn("nobody vs no one", html)
            self.assertEqual(g.count_empty_study_sections(html), 0)
            b1 = open(os.path.join(sd, "nuance_result.json"), "rb").read()
            for _ in range(2):                                                             # 再実行(resume/ページ再構築)で同一バイト
                html2, res2 = self.page(sd)
                self.assertEqual(html2, html)
            self.assertEqual(open(os.path.join(sd, "nuance_result.json"), "rb").read(), b1)
            self.assertEqual(p2w.expected_block_counts(sd, level="b1b")["nuance_blocks"], 1)

    def test_rejected_shows_no_corner_and_no_replacement_is_generated(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "reject")
            html, res = self.page(sd)
            self.assertEqual((res["status"], res["reason"]), (nx.ST_RESULT_REJECTED, "human_rejected"))
            assert_no_corner(self, html)
            self.assertNotIn("candidate", res)                                            # 不採用の本文は結果に載せない
            boom = nt.Fn(exc=RuntimeError("must not call"))
            r, g_, j_ = self.n1(sd, review_existed=True, gen=boom, judge=boom)             # resume/再起動しても代替候補を作らない(A-7)
            self.assertEqual((boom.n, r["api_calls"]), (0, 0))
            html3, res3 = self.page(sd)
            self.assertEqual(res3["status"], nx.ST_RESULT_REJECTED)
            assert_no_corner(self, html3)

    def test_zero_candidates_no_corner_after_human_confirms_without_nuance(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            r, gen, judge = self.n1(sd, review_existed=False, gen=nt.Fn(nt.gen_json(candidate=False)))
            self.assertEqual((r["status"], r["pending"]), (nx.ST_NO_CANDIDATE, None))     # 本物の0件(技術失敗と区別)
            self.assertEqual(judge.n, 0)                                                   # 候補なしなら判定callを省く
            self.form_confirm(sd, None)                                                    # フォームはnuance無しで送信(候補なし)
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_NONE)
            assert_no_corner(self, html)
            self.assertEqual(p2w.expected_block_counts(sd, level="b1b")["nuance_blocks"], 0)

    def test_undecided_candidate_at_page_entry_is_rc4_pending_not_silent_reject(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            with self.assertRaises(p2w.Part2NotConfirmed) as cm:                           # R-4: ISSUE rc=4
                self.page(sd)
            e = cm.exception
            self.assertEqual(e.pending[0]["kind"], "nuance")
            self.assertIsInstance(e, g.Part2Stale)                                         # 前進不可としてfail-closedにもなる
            self.assertFalse(os.path.exists(os.path.join(sd, "nuance_result.json")))      # 結果を書かない
            banner = kw.pending_banner(e.pending, restart_command="rerun", run_dir=self.run_dir)
            self.assertIn("ニュアンス解説", banner)
            self.assertIn("nobody vs no one", rd(os.path.join(self.run_dir, kw.UNIFIED_REQUEST)))   # 統合依頼書に候補全文が載る(待機は1回)

    def test_missing_or_stale_candidate_doc_with_spec_is_rc4(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            nx.ensure_spec(sd, level="b1b", new_review=True)                               # spec有・候補doc無し(N1未実行)
            with self.assertRaises(p2w.Part2NotConfirmed):
                self.page(sd)
            self.n1(sd, review_existed=True)
            nd = jl(os.path.join(sd, "nuance_candidate.json"))
            nd["text_sha256"] = "0" * 64                                                   # 本文が変わった後の古い候補doc
            jd(os.path.join(sd, "nuance_candidate.json"), nd)
            with self.assertRaises(p2w.Part2NotConfirmed):
                self.page(sd)

    def test_adopted_but_quote_vanished_from_new_text_is_stop_not_silent_drop(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "adopt")
            changed = [p.replace("Nobody spoke.", "Silence fell.") for p in PARAS]
            with self.assertRaises(g.Part2Stale) as cm:
                p2w.finalize_nuance(sd, changed, level="b1b", kp_dir=self.kp_dir, run_hint=self.run_dir, next_command="rerun")
            self.assertNotIsInstance(cm.exception, p2w.Part2NotConfirmed)                  # 待機ではなくSTOP。人間の採用を黙って捨てない(R-4)
            self.assertIn("revoke", str(cm.exception))

    def test_tampered_sidecar_candidate_is_integrity_stop(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "adopt")
            p = os.path.join(sd, cc.FILE_NUANCE)
            s = jl(p)
            s["candidate"]["explanation_ja"] = "改ざん"
            jd(p, s)
            with self.assertRaises(Exception) as cm:
                self.page(sd)
            self.assertIn("Integrity", type(cm.exception).__name__ + str(cm.exception))   # sidecar sha不一致=INTEGRITY(表示しない)

    def test_nuance_result_status_never_displays_unless_adopted(self):
        for st in ("REJECTED", "NONE", "FAILED_TECHNICAL", "SUPPRESSED", "LEGACY", None):
            res = {"status": st, "candidate": {k: "x" for k in g.NUANCE_REQUIRED_FIELDS}}
            self.assertEqual(g.render_nuance_html_block(res), "", st)


# ============================================================
# T3 重複判定(KP/Word=NG、文法=警告)
# ============================================================
class T3_Overlap(WBase):
    def test_kp_word_overlap_is_discarded_before_hr_and_not_replaced(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            inp = self.mk_inputs(sd)
            prov_text = inp["provisional"][0]["used_form"]
            r, gen, judge = self.n1(sd, review_existed=False, same=(prov_text,))
            self.assertEqual((r["status"], r["pending"]), (nx.ST_NO_CANDIDATE, None))     # HR提示前に破棄(人間に重複候補を見せない)
            doc = jl(os.path.join(sd, "nuance_candidate.json"))
            self.assertEqual(doc["no_candidate_reason"], nx.R_OVERLAP_NG)
            self.assertEqual(gen.n, 1)                                                     # 次点の再生成・自動補充をしない
            self.assertIn("rejected_candidate_audit", doc)
            self.form_confirm(sd, None)
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_NONE)
            assert_no_corner(self, html)

    def test_pool_conflict_chosen_at_hr_blocks_adoption_but_reject_is_accepted(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            inp = self.mk_inputs(sd)
            pool_only = next(e for e in inp["pool"] if not e["provisional"])
            self.n1(sd, review_existed=False, same=(pool_only["used_form"],))
            doc = jl(os.path.join(sd, "nuance_candidate.json"))
            self.assertIn(pool_only["id"], doc["candidate"]["pool_conflicts"])
            by_id = {c["candidate_id"]: c["ai_rank"] for c in cands["candidates"]}
            ranks = (by_id[pool_only["id"]],) + tuple(r for r in (1, 2, 3, 4, 5) if r != by_id[pool_only["id"]])[:2]
            pl = self._payload(cands, cat1=list(ranks), cat2=[], grammar=self.gram(pick=(0,)))
            pl["selection"]["nuance"] = self.nz(doc, "adopt")
            pl["schema_minor"] = 2
            with self.assertRaises(rv.ConfirmedContentIssue):                              # 重複するKP/Wordを選んだままの採用=NG(最終確認)
                self.confirm(pl)
            self.assertIsNone(self.rec())
            pl["selection"]["nuance"] = self.nz(doc, "reject")
            self.confirm(pl, "p2.json")                                                    # 不採用は常に受理
            self.assertEqual(self.rec()["nuance"]["decision"], "rejected")

    def test_grammar_overlap_is_warning_only_and_adoption_proceeds(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            gram_id = self.mk_inputs(sd)["grammar"][0]["id"]
            inp = self.mk_inputs(sd)
            judge = nt.Fn(nt.judge_json(inp, same=(inp["grammar"][0]["title"],)))
            r, gen, judge = self.n1(sd, review_existed=False, judge=judge)
            doc = jl(os.path.join(sd, "nuance_candidate.json"))
            self.assertEqual(doc["status"], "CANDIDATE")
            self.assertIn(gram_id, doc["candidate"]["grammar_conflicts"])                  # 警告(文法はHRで選ぶ前の提示中候補。ハードNGにしない=R-1)
            self.form_confirm(sd, "adopt")
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_ADOPTED)
            self.assertEqual(g.count_nuance_blocks(html), 1)


# ============================================================
# T4 CLI nuance-show / nuance-select / nuance-retry(フォーム経路と同じ結果)
# ============================================================
class T4_Cli(WBase):
    def run_cli(self, *argv):
        buf, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            rc = cli.run(list(argv))
        return rc, buf.getvalue(), err.getvalue()

    def kp_first_then_nuance(self, env):
        """KPをnuanceマーク発行前にフォーム確定(KP先行確定)→その後spec発行+候補生成。CLIで後付けできる状態。"""
        cands = self._gen(env)
        sd = self.prep_grammar()
        self.confirm(self.payload_with(cands, None))                                       # LEGACY時点の確定(nuance無し)
        self.n1(sd, review_existed=False)                                                  # spec発行+候補生成(KP確定は保持)
        return sd, cands

    def test_show_select_adopt_idempotent_and_locked(self):
        with Env(self.tmp) as env:
            sd, cands = self.kp_first_then_nuance(env)
            rc, out, err = self.run_cli("nuance-show", "--run", self.run_dir, "--level", "b1b")
            self.assertEqual(rc, 0)
            show = json.loads(out)
            sha = show["candidate"]["candidate_sha256"]
            self.assertEqual((show["candidate_status"], show["decision"]), ("CANDIDATE", None))
            rc, out, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 0, err)
            self.assertEqual(json.loads(out)["nuance"], "adopted")
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_ADOPTED)
            self.assertEqual(g.count_nuance_blocks(html), 1)
            rc, out, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual((rc, json.loads(out)["unchanged"]), (0, True))              # 冪等
            rc, out, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "reject", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 2)                                                        # 確定後の変更は拒否(revoke経由のみ)
            self.assertEqual(self.page(sd)[1]["status"], nx.ST_RESULT_ADOPTED)

    def test_select_reject_and_stale_sha_and_missing_user_ref_are_refused(self):
        with Env(self.tmp) as env:
            sd, cands = self.kp_first_then_nuance(env)
            sha = jl(os.path.join(sd, "nuance_candidate.json"))["candidate"]["candidate_sha256"]
            rc, _, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", "0" * 64, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 2)                                                        # 古い候補への操作を拒否(ISSUE)
            self.assertIsNone(cc.nuance_state(sd))
            rc, _, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", sha, "--by", "human", "--user-ref", "/no/such/file")
            self.assertEqual(rc, 2)
            self.assertIsNone(cc.nuance_state(sd))
            rc, out, _ = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "reject", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 0)
            html, res = self.page(sd)
            self.assertEqual(res["status"], nx.ST_RESULT_REJECTED)
            assert_no_corner(self, html)

    def test_select_requires_live_kp_record_and_spec(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)                                              # KP未確定
            sha = jl(os.path.join(sd, "nuance_candidate.json"))["candidate"]["candidate_sha256"]
            rc, _, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 2)
            self.assertIn("KP確定レコード", err)
        # specの無い(LEGACY)runでは使えない
        legacy_run = os.path.join(self.tmp, "legacy")
        os.makedirs(os.path.join(legacy_run, "b1b", "study_text"), exist_ok=True)
        rc, _, err = self.run_cli("nuance-show", "--run", legacy_run, "--level", "b1b")
        self.assertEqual(rc, 2)

    def test_cli_route_and_form_route_make_the_same_sidecar(self):
        keys = ("schema", "level", "decision", "nuance_id", "candidate_sha256", "candidate", "confirmed_against", "pool_identity_sha", "nuance_doc_status",
                "no_candidate_reason", "kp_dir_rel", "content_sha256", "text_sha256_at_confirm")
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)
            self.form_confirm(sd, "adopt")
            via_form = {k: jl(os.path.join(sd, cc.FILE_NUANCE)).get(k) for k in keys}
            res_form = jl(os.path.join(sd, "nuance_result.json")) if os.path.exists(os.path.join(sd, "nuance_result.json")) else self.page(sd)[1]
        shutil.rmtree(self.run_dir)                                                        # 同じ入力で最初からやり直し(mockは決定論)
        with Env(self.tmp) as env:
            sd, cands = self.kp_first_then_nuance(env)
            sha = jl(os.path.join(sd, "nuance_candidate.json"))["candidate"]["candidate_sha256"]
            rc, _, err = self.run_cli("nuance-select", "--run", self.run_dir, "--level", "b1b", "--choice", "adopt", "--candidates-sha", sha, "--by", "human", "--user-ref", self.uref)
            self.assertEqual(rc, 0, err)
            via_cli = {k: jl(os.path.join(sd, cc.FILE_NUANCE)).get(k) for k in keys}
            res_cli = self.page(sd)[1]
        self.assertEqual(via_cli, via_form)                                                # sidecarの確定内容が同一
        for k in ("status", "candidate", "candidate_sha256", "final_overlap_check"):
            self.assertEqual(res_cli[k], res_form[k], k)                                   # 表示用の確定結果も同一

    def test_retry_only_for_technical_failure_never_replaces_a_valid_candidate(self):
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False)                                              # 有効な候補
            rc, _, err = self.run_cli("nuance-retry", "--run", self.run_dir, "--level", "b1b", "--by", "human")
            self.assertEqual(rc, 2)                                                        # 代替候補の探し直しは拒否(A-7)
            self.assertTrue(os.path.exists(os.path.join(sd, "nuance_candidate.json")))
        shutil.rmtree(self.run_dir)
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.n1(sd, review_existed=False, gen=nt.Fn(exc=ConnectionError("down")), judge=nt.Fn("x"))
            rc, out, err = self.run_cli("nuance-retry", "--run", self.run_dir, "--level", "b1b", "--by", "human")
            self.assertEqual(rc, 0, err)
            self.assertFalse(os.path.exists(os.path.join(sd, "nuance_candidate.json")))
            self.assertTrue([f for f in os.listdir(sd) if f.startswith("nuance_candidate.REGEN_")])   # 退避(削除しない)
            r, gen, judge = self.n1(sd, review_existed=True)                               # 次回の制作コマンドで再試行
            self.assertEqual(r["status"], "CANDIDATE")


# ============================================================
# T5 runner(X/Y/Z)の同一契約
# ============================================================
class FakeCtx:
    def __init__(self, out_dir, mode="real", hooks=None):
        self.out_dir, self.slug, self.mode, self.hooks = out_dir, "coffee", mode, hooks or {}
        self.llm_client = None
        self.budget = None
        self.regenerate_stage = None
        self.stops = []

    @contextlib.contextmanager
    def stage_context(self, name):
        self.stops.append(name)
        yield


class T5_RunnerContract(WBase):
    def x_source(self):
        src = os.path.join(self.tmp, "src", "coffee", "run1")
        for lv in ("b1b", "a2"):
            os.makedirs(os.path.join(src, lv), exist_ok=True)
            wr(os.path.join(src, lv, "article.md"), f"# {LABEL}\n\n" + "\n\n".join(PARAS) + "\n")
        return src

    def test_x_helpers_issue_spec_only_on_new_review_and_finalize_at_player(self):
        src = self.x_source()
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            self.assertEqual(os.path.normpath(sd), os.path.normpath(X._part2_study_dir(self.run_dir, "b1b")))                # Xのstudy dir/kp dirの規約が共通関数と一致
            inp = self.mk_inputs(sd)
            gen, judge = nt.Fn(nt.gen_json(expression="nobody vs no one", quote=QUOTE)), nt.Fn(nt.judge_json(inp))
            legacy = X.run_nuance_candidates_x(None, src, self.run_dir, level="b1b", review_existed=True, call_fn=gen, judge_fn=judge)
            self.assertEqual((legacy["state"], gen.n), (nx.ST_LEGACY, 0))                  # 既存KP review=LEGACY=生成0
            self.assertIsNone(X.finalize_nuance_x(src, self.run_dir, level="b1b"))
            r = X.run_nuance_candidates_x(None, src, self.run_dir, level="b1b", review_existed=False, call_fn=gen, judge_fn=judge)
            self.assertEqual((r["state"], r["status"], gen.n), ("SPEC_ISSUED", "CANDIDATE", 1))
            with self.assertRaises(p2w.Part2NotConfirmed):
                X.finalize_nuance_x(src, self.run_dir, level="b1b")
            self.form_confirm(sd, "adopt")
            nz = X.finalize_nuance_x(src, self.run_dir, level="b1b")
            self.assertEqual(nz["status"], nx.ST_RESULT_ADOPTED)

    def test_y_and_z_steps_are_noop_in_mock_without_hooks_and_legacy_for_existing_review(self):
        for mod, family in ((Y, "y"), (Z, "z")):
            ctx = FakeCtx(os.path.join(self.tmp, f"{family}_o"), mode="dry-run")
            with mock.patch.object(mod, "_part2_inputs", lambda ctx_, lv: (PARAS, LABEL)):
                r = mod._nuance_cand_step(ctx, "b1b", True)
            self.assertEqual((r["state"], r["api_calls"], r["pending"]), ("SKIPPED_NO_HOOK", 0, None), family)   # mock/dry-runは実APIへ出さない(specも作らない)

    def test_y_and_z_wrappers_map_errors_to_each_runners_stop_and_pending_types(self):
        sd_for = {}
        with Env(self.tmp) as env:
            for mod, family, pend_cls, stop_cls in ((Y, "y", Y.YKpReviewPending, Y.YE2EStop), (Z, "z", Z.FamilyZKpReviewPending, Z.FamilyZE2EStop)):
                out = os.path.join(self.tmp, f"{family}_out")
                kp_dir = f"{out}/key_phrases/b1b"
                self.ensure(env, kp_dir=kp_dir, run_dir=out, family=family)
                sd = p2w.study_dir_for(family, out, "b1b")
                ctx = FakeCtx(out, mode="real", hooks={})
                with mock.patch.object(mod, "_part2_inputs", lambda ctx_, lv: (PARAS, LABEL)):
                    self.assertIsNone(mod._assert_nuance_final(ctx, "stage_pages", "b1b"))      # LEGACY(spec無し)=None=従来出力と同一
                    nx.ensure_spec(sd, level="b1b", new_review=True)
                    with self.assertRaises(pend_cls) as cm:                                      # spec有・候補doc無し=rc=4待機
                        mod._assert_nuance_final(ctx, "stage_pages", "b1b")
                    self.assertEqual(cm.exception.pending[0]["kind"], "nuance", family)
                self.assertTrue(issubclass(pend_cls, stop_cls))

    def test_all_three_runners_use_the_common_functions_and_no_unfinalized_read(self):
        srcs = {n: open(os.path.join(ROOT, n), encoding="utf-8").read() for n in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py",
                                                                                  "er026_family_z_fiction_production_runner_01.py")}
        for n, s in srcs.items():
            self.assertIn("n1_stage(", s, n)                                               # N0+N1は共通関数
            self.assertIn("finalize_nuance(", s, n)                                        # ページ入口の確定は共通関数
            self.assertNotIn("nuance=_p2w().nuance_for_display(", s, n)                    # 確定前のファイル読取でcomposeしない(R-3)
            self.assertIsNone(re.search(r"compose_page_html\([^\n]*nuance=None", s), n)    # 渡し漏れ(None固定)がない
        for n, s in srcs.items():
            self.assertIsNone(re.search(r"(?m)^\s*(import|from)\s+\S*(run_trial|FAMILY[-_]Z[-_]STUDY[-_]TEXT[-_]TRIAL)", s), n)   # Dangling Reference(Trial経路のimport)なし
        # X公開ページ(listening page)もpublic_study_html経由=finalize入り
        self.assertIn("finalize_nuance(", open(os.path.join(ROOT, "er120_part2_wiring_01.py"), encoding="utf-8").read())

    def test_er128_and_exporter_use_er134_public_wrappers_only(self):
        for n in ("er128_kp_confirmed_content_01.py", "er120_part2_wiring_01.py", "docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py"):
            s = open(os.path.join(ROOT, n), encoding="utf-8").read()
            self.assertNotIn("nx._pool_entry", s, n)
            self.assertNotIn("_pool_entry(", s, n)
        self.assertEqual(cc.nuance_pool_identity_sha(rv.load_candidates(self.kp_dir) or {"candidates": []}), nx.pool_identity_sha_of({"candidates": []}))

    def test_default_off_isolation_no_spec_means_no_calls_no_files_no_display(self):
        """LEGACY不変(DefaultOffIsolation型): specが無いrunはN1もfinalizeも何もしない(API 0・出力不変・副作用ファイル0)。flag/env/modeでONにする経路がない。"""
        with Env(self.tmp) as env:
            sd, cands = self.ready(env)
            before = sorted(os.listdir(sd))
            boom = nt.Fn(exc=AssertionError("API must not be called"))
            r, _, _ = self.n1(sd, review_existed=True, gen=boom, judge=boom)
            self.assertEqual((r["state"], boom.n), (nx.ST_LEGACY, 0))
            self.assertIsNone(self.fin(sd))
            self.assertEqual(sorted(os.listdir(sd)), before)
        s = open(os.path.join(ROOT, "er134_nuance_explanation_01.py"), encoding="utf-8").read()
        self.assertNotIn("os.environ", s)
        self.assertNotIn("getenv", s)


if __name__ == "__main__":
    unittest.main()
