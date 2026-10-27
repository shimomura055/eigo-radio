# -*- coding: utf-8 -*-
"""GRAMMAR-PREGEN-ALL-LEVELS-01 委任_05A: KP先行確定モード(`confirm --from-form --grammar-pending`)と、文法だけの後追い確定(`confirm --grammar-from-form`)のtest。全てmock・API 0。
文法選定仕様(2026-10-27ユーザー正式決定): Top1/Top2のみ提示・原則1件・0件可・2件同時選択禁止。KP/KWは確定・保護し、文法は再選定待ち(=0件確定としない)。
対象: pending(KP保護が効く/文法は保護なし/文法reviewはPENDINGのまま/sidecarはstatus=pending) / pendingのままfinalizeは待機 / 後から1件 / 後から0件(omit) /
      冪等(同じ送信・別内容拒否) / 2件ISSUE / 提示範囲外ISSUE / KP区分の食い違い拒否 / CLI(--grammar-pending・--grammar-from-form) / study dir無しのpending。
設計: docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_02,DESIGN_03,IMPLEMENTATION_05A}.md。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import unittest

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
import er128_kp_confirmed_content_01 as cc
from er119_test_support_01 import Env, jl
from er128_kp_confirmed_content_grammar_v2_test_01 import GBase


class PBase(GBase):
    def kp_payload(self, env, grammar, level="b1b"):
        cands = rv.load_candidates(self.kpd(level)) or self._gen(env, level=level)
        cat2 = (4, 5) if level == "b1b" else ()
        return self._payload(cands, cat1=[1, 2, 3], cat2=list(cat2), grammar=grammar, level=level)

    def pending(self, env, grammar=None, level="b1b"):
        pl = self.kp_payload(env, grammar, level)
        return cc.cmd_from_form(self.run_dir, level, self._write(pl, f"pending_{level}.json"), "human", self.uref, grammar_pending=True)

    def later(self, env, grammar, level="b1b", with_kp=True):
        pl = self.kp_payload(env, grammar, level)
        if not with_kp:
            pl["selection"] = {"grammar": grammar}
        return cc.cmd_grammar_from_form(self.run_dir, level, self._write(pl, f"later_{level}.json"), "human", self.uref)


class T1_Pending(PBase):
    def test_pending_confirms_kp_and_keeps_grammar_unconfirmed_not_zero(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            old_two = self.gram(pick=(0, 1))                                  # 旧仕様で2件選んでいたpayload(grammar[]は使わず無視する)
            out = self.pending(env, old_two)
            self.assertEqual((out["grammar_status"], out["grammar_payload_ignored"], out["grammar"]), (cc.GRAMMAR_PENDING, 2, 0))
            self.assertIsNone(out["grammar_review"])
            rec = self.rec()
            self.assertEqual(rec["state"], cc.STATE_LIVE)
            self.assertEqual(len(rec["items"]), 5)                            # KP3+KW2=確定・保護
            self.assertEqual((rec["grammar"]["status"], rec["grammar"]["payload_grammar_ignored"]), (cc.GRAMMAR_PENDING, 2))
            side = jl(os.path.join(self.sd, cc.FILE_GRAMMAR))
            self.assertEqual((side["status"], side["items"]), ("pending", []))     # 0件確定と区別できる(status=pending)
            self.assertEqual(rec["grammar"]["sidecar_sha256"], side["sidecar_sha256"])
            self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)     # 文法reviewは触らない=再選定待ち
            self.assertIsNone(cc.grammar_state(self.sd))                           # 文法の保護はまだ無い(選べる)
            cc.guard_grammar(self.sd, "pick")                                       # 文法の選定操作は拒否されない
            with self.assertRaises(rv.ConfirmedContentLocked):                      # KP/KWは保護される
                cc.guard(self.kpd(), "select")
            self.assertEqual(cc._problems_self(rec), [])
            self.assertEqual(cc._grammar_problems(self.kpd(), "b1b", rec), [])

    def test_pending_without_grammar_study_dir_records_mark_only(self):
        with Env(self.tmp) as env:
            out = self.pending(env, None)
            self.assertFalse(os.path.exists(self.sd))
            rec = self.rec()
            self.assertEqual((rec["grammar"]["status"], rec["grammar"]["path_rel"]), (cc.GRAMMAR_PENDING, None))
            self.assertEqual(out["grammar_status"], cc.GRAMMAR_PENDING)
            self.assertEqual(cc._grammar_problems(self.kpd(), "b1b", rec), [])
            self.assertEqual(cc._grammar_sentences(self.kpd(), rec), [])
            with self.assertRaises(cc.CliError) as cm:                              # 文法候補が無いのに後追い確定はできない
                self.later(env, [])
            self.assertIn("次の一手", str(cm.exception))
            self.assertEqual(self.rec()["grammar"]["status"], cc.GRAMMAR_PENDING)

    def test_finalize_while_pending_waits_rc4_and_never_zero_confirms(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            with self.assertRaises(g.Part2PendingReview):                           # 文法は判断待ち(rc=4待機)。0件で最終確定しない
                self.finalize()
            with self.assertRaises(p2w.Part2NotConfirmed):
                p2w.require_final(self.sd, PARAS_, "Test Story", level="b1b", next_command="x")
            self.assertFalse(os.path.exists(p2w.RESULT_PATH(self.sd)))
            self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)
            self.assertEqual(rv.EXIT_CODE_PENDING, 4)


PARAS_ = ["The old man walked slowly down the road. He was tired.",
          "It was a cold morning that day. Nobody spoke.",
          "Never had she seen such a thing before. Really.",
          "Under the bed lay a small box of letters.",
          "Nothing else happened that day at all."]


class T2_LaterOne(PBase):
    def test_pending_then_one_grammar_confirms_grammar_only_and_kp_record_is_unchanged(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            before = self.rec()
            gm = self.gram(pick=(1,))                                         # Top2を選ぶ
            out = self.later(env, gm)
            self.assertEqual((out["grammar_status"], out["grammar"], out["unchanged"]), ("confirmed", 1, False))
            after = self.rec()
            for k in ("items", "content_sha256", "confirmation_id", "unconsumed", "comment", "user_note_sha256", "confirmed_by", "origin", "article"):
                self.assertEqual(after[k], before[k], k)                       # KPの確定内容は不変
            self.assertEqual(after["revision"], before["revision"] + 1)
            self.assertEqual(after["history"][-1]["event"], "grammar_confirmed")   # revisionに文法追加を記録
            self.assertEqual(after["history"][-1]["extra"]["grammar_ids"], [gm[0]["id"]])
            self.assertEqual(cc._problems_self(after), [])
            self.assertEqual((after["grammar"]["status"], after["grammar"]["count"]), ("confirmed", 1))
            side = jl(os.path.join(self.sd, cc.FILE_GRAMMAR))
            self.assertEqual((side["status"], [i["id"] for i in side["items"]], side["confirmed_after_pending"]), ("confirmed", [gm[0]["id"]], True))
            review = gr.load_review(self.sd)
            self.assertEqual((review["status"], review["selection"]["choice"], review["selection"]["candidate_ids"]), (rv.ST_REVIEWED, "pick", [gm[0]["id"]]))
            self.assertEqual(cc.grammar_state(self.sd)["level"], "b1b")           # これ以降は文法も保護される
            with self.assertRaises(rv.ConfirmedContentLocked):
                cc.guard_grammar(self.sd, "reselect")
            res = self.finalize()["result"]                                     # 確定した文法で最終確定(Step B 0 call)
            self.assertEqual(([i["selection"]["candidate_id"] for i in res["items"]], self.xp.n), ([gm[0]["id"]], 2))
            cc.verify_part2_items(self.sd, res)

    def test_later_is_idempotent_and_another_grammar_is_refused(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            gm = self.gram(pick=(0,))
            self.later(env, gm)
            rec1 = self.rec()
            rev_g = gr.load_review(self.sd)["revision"]
            out = self.later(env, gm)                                           # 同じ送信=冪等(何も変えない)
            self.assertTrue(out["unchanged"])
            self.assertEqual(self.rec(), rec1)
            self.assertEqual(gr.load_review(self.sd)["revision"], rev_g)
            with self.assertRaises(cc.CliError) as cm:                          # 別の文法・0件への変更は確定後不変
                self.later(env, self.gram(pick=(1,)))
            self.assertIn("確定後は変更できません", str(cm.exception))
            with self.assertRaises(cc.CliError):
                self.later(env, [])
            self.assertEqual(self.rec(), rec1)

    def test_later_two_grammar_or_third_ranked_is_issue_and_writes_nothing(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            before, rev_g = self.rec(), gr.load_review(self.sd)["revision"]
            with self.assertRaises(rv.ConfirmedContentIssue):                   # 2件同時選択は禁止
                self.later(env, self.gram(pick=(0, 1)))
            third = gr.load_candidates(self.sd)["candidates"][2]
            item = {"id": third["candidate_id"], "title": third["construct_ja"], "explanation_full": "【日本語訳】\nx", "explanation_status": "provided", "example": third["sentence"]}
            with self.assertRaises(rv.ConfirmedContentIssue):                   # Top1/Top2以外(3位)は提示していない
                self.later(env, [item])
            with self.assertRaises(rv.ConfirmedContentIssue):                   # 解説全文が事前生成物と違う
                self.later(env, [dict(self.gram(pick=(0,))[0], explanation_full="改変")])
            self.assertEqual(self.rec(), before)
            self.assertEqual(gr.load_review(self.sd)["revision"], rev_g)
            self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)

    def test_later_with_different_kp_groups_is_refused(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            cands = rv.load_candidates(self.kpd())
            pl = self._payload(cands, cat1=[1, 2, 4], cat2=[3, 5], grammar=self.gram(pick=(0,)))        # KP区分が確定済みと違う
            with self.assertRaises(cc.CliError) as cm:
                cc.cmd_grammar_from_form(self.run_dir, "b1b", self._write(pl, "diffkp.json"), "human", self.uref)
            self.assertIn("変更できません", str(cm.exception))
            self.assertEqual(self.rec()["grammar"]["status"], cc.GRAMMAR_PENDING)

    def test_later_requires_a_pending_record(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            with self.assertRaises(cc.CliError):                                # KP未確定
                self.later(env, self.gram(pick=(0,)))
            self._gen(env)
            self.form(env, self.gram(pick=(0,)))                                # 通常のfrom-form(文法込み)で確定
            with self.assertRaises(cc.CliError):                                # 別の文法を後から=確定後不変
                self.later(env, self.gram(pick=(1,)))
            self.assertTrue(self.later(env, self.gram(pick=(0,)))["unchanged"])    # 同じ内容は冪等


class T3_LaterZero(PBase):
    def test_pending_then_zero_omits_and_finalizes_zero(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.pending(env, None)
            out = self.later(env, [])
            self.assertEqual((out["grammar_status"], out["grammar"]), ("confirmed", 0))
            review = gr.load_review(self.sd)
            self.assertEqual((review["selection"]["choice"], review["selection"]["zero_reason"], review["selection"]["candidate_ids"]), ("omit", "form_submission_no_grammar", []))
            side = jl(os.path.join(self.sd, cc.FILE_GRAMMAR))
            self.assertEqual((side["status"], side["items"]), ("confirmed", []))   # 今度は『0件を確定した』
            res = self.finalize()["result"]
            self.assertEqual(res["status"], "ZERO")
            cc.verify_part2_items(self.sd, res)
            with self.assertRaises(cc.CliError):                                # 0件確定後に1件へは変更不可
                self.later(env, self.gram(pick=(0,)))


class T4_Cli(PBase):
    def test_cli_grammar_pending_then_grammar_from_form(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=self.gram(pick=(0, 1)))
            p = self._write(pl, "cli_pending.json")
            base = ["--run", self.run_dir, "--level", "b1b", "--by", "human", "--user-ref", self.uref]
            self.assertEqual(cc.run(["confirm", "--from-form", p, "--grammar-pending"] + base), 0)
            self.assertEqual(self.rec()["grammar"]["status"], cc.GRAMMAR_PENDING)
            self.assertEqual(cc.run(["confirm", "--grammar-pending", "--from-review"] + base), 2)         # --from-form 無しの--grammar-pendingは拒否
            pl2 = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=self.gram(pick=(1,)))
            p2 = self._write(pl2, "cli_later.json")
            self.assertEqual(cc.run(["confirm", "--grammar-from-form", p2] + base), 0)
            self.assertEqual((self.rec()["grammar"]["status"], self.rec()["grammar"]["count"]), ("confirmed", 1))
            self.assertEqual(cc.run(["confirm", "--grammar-from-form", p2] + base), 0)                      # 冪等
            pl3 = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=self.gram(pick=(0, 1)))
            self.assertEqual(cc.run(["confirm", "--grammar-from-form", self._write(pl3, "cli_two.json")] + base), 4)   # 2件はISSUE(rc=4。何も書かない)


if __name__ == "__main__":
    unittest.main()
