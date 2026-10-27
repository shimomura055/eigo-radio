# -*- coding: utf-8 -*-
"""GRAMMAR-PREGEN-ALL-LEVELS-01 委任_04(F-5/F-6): 確定内容保護(er128)への文法v2接続のtest。全てmock・API 0(実client生成はblock)。
対象: cmd_from_formの文法照合(id/title/解説全文バイト一致/件数<=2/重複・不一致=ISSUE rc=4で何も書かない)・0件=omit+文法なしの確定記録・2件の確定と凍結items[]・
      level別sidecar(Std/Adv)・level不一致fail-closed・事前生成不完全/失敗のfail-closed・呼出順(検証->KPロック->文法review->sidecar->KPレコード)と冪等・
      v1(sidecar/凍結)読取互換・G4(2件・ZERO矛盾・id集合)・guard_grammar複数id・revoke後の再確認で古い凍結を退避・b1b既定値/discover_dirs(run)[0]の撤去。
設計: docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/{SCHEMA_CONTRACT_01,IMPLEMENTATION_04}.md。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import inspect
import json
import os
import re
import unittest
from unittest import mock

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g
import er120_part2_mock_01 as mk
import er120_part2_wiring_01 as p2w
import er128_kp_confirmed_content_01 as cc
from er119_test_support_01 import Env, jd, jl, rd, wr
from er128_kp_confirmed_content_test_01 import FormHelpers

ROOT = os.path.dirname(os.path.abspath(__file__))
PARAS = ["The old man walked slowly down the road. He was tired.",
         "It was a cold morning that day. Nobody spoke.",
         "Never had she seen such a thing before. Really.",
         "Under the bed lay a small box of letters.",
         "Nothing else happened that day at all."]
LABEL = "Test Story"


class Ctr:
    def __init__(self, fn):
        self.fn, self.n = fn, 0

    def __call__(self, prompt):
        self.n += 1
        return self.fn(prompt)


class GBase(FormHelpers):
    def setUp(self):
        super().setUp()
        self.sd = os.path.join(self.run_dir, "b1b", "study_text")
        self.sd_a2 = os.path.join(self.run_dir, "a2", "study_text")
        self.xp = Ctr(mk.mock_explain_call_fn)
        p = mock.patch("er003_v1_b1_scaffold_01_generate.get_client", side_effect=AssertionError("real client must not be created (API 0)"))
        p.start()
        self.addCleanup(p.stop)

    def sdir(self, level):
        return self.sd if level == "b1b" else self.sd_a2

    def prep_grammar(self, level="b1b", pregen=True):
        sd = self.sdir(level)
        gr.ensure_grammar_review(sd, level=level, run_dir=self.run_dir, family="x", slug="coffee", paragraphs=PARAS, label=LABEL, extract_call_fn=mk.mock_extract_call_fn)
        if pregen:
            p2w.pregen_stage(sd, level=level, next_command="rerun", explain_call_fn=self.xp)
        return sd

    def gram(self, level="b1b", pick=(0, 1)):
        """フォームが出すgrammar[](form_grammar_bundleのitem。AI推奨=rank1が先頭)から pick の位置のものを {id,title,explanation_full,explanation_status,example} で返す。"""
        b = p2w.form_grammar_bundle(self.sdir(level), level=level)
        return [{k: b["items"][i][k] for k in ("id", "title", "explanation_full", "explanation_status", "example")} for i in pick]

    def cands(self, env, level="b1b"):
        return self._gen(env, level=level)

    def form(self, env, grammar, level="b1b", cat1=(1, 2, 3), cat2=None):
        cands = rv.load_candidates(self.kp_dir if level == "b1b" else self.kp_dir_a2) or self._gen(env, level=level)
        cat2 = (4, 5) if (cat2 is None and level == "b1b") else (cat2 or ())
        pl = self._payload(cands, cat1=list(cat1), cat2=list(cat2), grammar=grammar, level=level)
        return cc.cmd_from_form(self.run_dir, level, self._write(pl, f"payload_{level}.json"), "human", self.uref)

    def kpd(self, level="b1b"):
        return self.kp_dir if level == "b1b" else self.kp_dir_a2

    def finalize(self, level="b1b", **kw):
        return p2w.finalize_stage(self.sdir(level), level=level, paragraphs=PARAS, label=LABEL, **kw)


class T1_TwoGrammar(GBase):
    def test_two_grammar_confirm_writes_v2_sidecar_review_and_record(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            gm = self.gram(pick=(2, 0))                                         # クリック順(AI推奨が後)を逆にしても本文出現順へ正規化
            out = self.form(env, gm)
            self.assertEqual(out["grammar"], 2)
            rec = self.rec()
            self.assertEqual((rec["grammar"]["count"], rec["grammar"]["level"], rec["grammar"]["schema"]), (2, "b1b", cc.SCHEMA_GRAMMAR_V2))
            side = jl(os.path.join(self.sd, cc.FILE_GRAMMAR))
            self.assertEqual((side["schema"], side["level"], side["confirmation_id"]), (cc.SCHEMA_GRAMMAR_V2, "b1b", rec["confirmation_id"]))
            self.assertEqual([i["id"] for i in side["items"]], [x["id"] for x in gm])
            self.assertEqual(side["explanation_sha_by_id"], {i["id"]: i["explanation_sha256"] for i in side["items"]})
            self.assertTrue(all(i["explanation_status"] == "provided" and i["explanation_sha256"] for i in side["items"]))
            self.assertEqual(rec["grammar"]["sidecar_sha256"], side["sidecar_sha256"])
            review = gr.load_review(self.sd)
            self.assertEqual((review["status"], review["selection"]["choice"], review["decision"]["channel"]), (rv.ST_REVIEWED, "pick", "form"))
            self.assertEqual(sorted(review["selection"]["candidate_ids"]), sorted(x["id"] for x in gm))
            self.assertEqual(len(review["selection"]["candidate_ids"]), 2)
            self.assertEqual(set(review["decision"]["explanation_sha_by_id"]) >= {x["id"] for x in gm}, True)
            st = cc.grammar_state(self.sd)
            self.assertEqual(sorted(cc._side_ids(st)), sorted(x["id"] for x in gm))
            self.assertEqual(st["level"], "b1b")

    def test_finalize_freezes_two_items_without_step_b_and_g4_binds_both(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            n_before = self.xp.n
            self.form(env, self.gram(pick=(0, 1)))
            out = self.finalize()
            self.assertEqual(self.xp.n, n_before)                                # 確定後にStep Bは呼ばれない(事前生成物=フォームで見せた解説を使う)
            res = out["result"]
            self.assertEqual((res["schema"], res["status"], len(res["items"])), (g.SCHEMA_RESULT_V2, "SELECTED", 2))
            fzj = jl(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN))
            self.assertEqual((fzj["schema"], len(fzj["items"])), (cc.SCHEMA_GRAMMAR_FROZEN_V2, 2))
            self.assertTrue(all(i["source"] == "form_displayed" for i in fzj["items"]))
            self.assertEqual(sorted(i["candidate_id"] for i in fzj["items"]), sorted(i["selection"]["candidate_id"] for i in res["items"]))
            self.assertEqual([f["frozen_sha256"] for f in cc.load_frozen_grammar_items(self.sd)], [i["frozen_sha256"] for i in fzj["items"]])
            cc.verify_part2_items(self.sd, res)                                  # G4 PASS
            with self.assertRaises(rv.KpReviewError):                            # v1単一APIは2件で黙って先頭を返さない
                cc.load_frozen_grammar(self.sd)
            # 改変の検出(2件のどちらでも)
            for k in (0, 1):
                bad = json.loads(json.dumps(res))
                bad["items"][k]["explanation_md"] += "\n(改変)"
                with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                    cc.verify_part2_items(self.sd, bad)
            one = json.loads(json.dumps(res))
            one["items"] = one["items"][:1]
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):       # 確定2件が結果1件に減った
                cc.verify_part2_items(self.sd, one)
            zero = {"status": "ZERO", "items": []}
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):       # 確定した文法とZEROの矛盾
                cc.verify_part2_items(self.sd, zero)
            sw = json.loads(json.dumps(res))
            sw["items"][0]["selection"]["candidate_id"] = "g_other"
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                cc.verify_part2_items(self.sd, sw)
            # 凍結ファイルの書換え
            fzj["items"][1]["explanation_md"] = "書換え"
            jd(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN), fzj)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                cc.load_frozen_grammar_items(self.sd)

    def test_second_finalize_is_pure_reuse_and_wiring_uses_the_four_functions(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.form(env, self.gram(pick=(0, 1)))
            for fn in ("load_frozen_grammar_items", "freeze_from_sidecar_items", "freeze_part2_result_items", "verify_part2_items"):
                self.assertTrue(callable(getattr(cc, fn)), fn)
            self.finalize()
            before = rd(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN))
            self.finalize()
            self.assertEqual(rd(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN)), before)   # 凍結は上書きされない
            self.assertEqual(self.xp.n, 3)


class T2_ZeroGrammar(GBase):
    def test_zero_grammar_omits_and_records_no_grammar_confirmation(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            out = self.form(env, [])
            self.assertEqual((out["grammar"], out["grammar_review"]), (0, rv.ST_REVIEWED))
            review = gr.load_review(self.sd)
            self.assertEqual((review["selection"]["choice"], review["selection"]["zero_reason"], review["selection"]["candidate_ids"]), ("omit", "form_submission_no_grammar", []))
            self.assertEqual(review["decision"]["channel"], "form")
            rec = self.rec()
            self.assertEqual((rec["grammar"]["count"], jl(os.path.join(self.sd, cc.FILE_GRAMMAR))["items"]), (0, []))
            res = self.finalize()["result"]
            self.assertEqual(res["status"], "ZERO")                              # 文法なしの確定どおり(AUTO TOP1にならない)
            cc.verify_part2_items(self.sd, res)
            sel = json.loads(json.dumps(res))
            sel.update(status="SELECTED", items=[{"selection": {"candidate_id": "g1", "sentence": "x"}, "explanation_md": "e", "translation_ja": "t"}])
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):       # 文法なしを確定したのに文法が出た
                cc.verify_part2_items(self.sd, sel)
            for op in ("reselect", "reextract"):                                  # 文法なしの確定も保護される(revoke必須)
                with self.assertRaises(rv.ConfirmedContentLocked):
                    gr.op_decide(self.sd, choice=op, reason="x", candidates_sha256=gr.load_candidates(self.sd)["candidates_sha256"], by="human")

    def test_no_grammar_study_dir_and_zero_grammar_keeps_old_behaviour(self):
        with Env(self.tmp) as env:
            out = self.form(env, [])
            self.assertEqual((out["grammar"], out["grammar_review"]), (0, None))
            self.assertNotIn("grammar", self.rec())                              # 文法を見せていないフォーム: 文法の記録を作らない
            self.assertFalse(os.path.exists(self.sd))

    def test_nonzero_grammar_without_study_dir_is_refused(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=[{"id": "g1", "title": "x", "explanation_full": "y", "explanation_status": "provided"}])
            with self.assertRaises(cc.CliError) as cm:
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            self.assertIn("次の一手", str(cm.exception))
            self.assertIsNone(self.rec())
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)


class T3_IssueOnMismatch(GBase):
    def _nothing_written(self):
        self.assertIsNone(self.rec())
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)         # KP reviewも書いていない(検証は全てop_selectより前)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)             # 文法reviewも書いていない
        self.assertFalse(os.path.exists(os.path.join(self.sd, cc.FILE_GRAMMAR)))

    def _issue(self, grammar, needle):
        with Env(self.tmp) as env:
            with self.assertRaises(rv.ConfirmedContentIssue) as cm:
                self.form(env, grammar)
            self.assertIn("CONFIRMED_CONTENT_ISSUE", str(cm.exception))
            doc = jl(cc.paths_of(self.kp_dir)["issue_json"])
            self.assertEqual(doc["kind"], "CONFIRMED_CONTENT_ISSUE")
            self.assertTrue(any(needle in d["field"] for d in doc["diffs"]), doc["diffs"])
            self.assertTrue(doc["proposal"])                                       # 修正案(正しい値)を提示
            self._nothing_written()
            return doc

    def setUp(self):
        super().setUp()
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)

    def test_explanation_full_must_match_pregen_byte_for_byte(self):
        gm = self.gram(pick=(0,))
        gm[0]["explanation_full"] += " "                                          # 1文字の差
        self._issue(gm, "explanation_full")

    def test_title_mismatch(self):
        gm = self.gram(pick=(0,))
        gm[0]["title"] = "別の文法名"
        doc = self._issue(gm, "title")
        self.assertTrue(any("mock構文" in p for p in doc["proposal"]))

    def test_unknown_id_is_issue_not_guess_by_title(self):
        gm = self.gram(pick=(0,))
        gm[0]["id"] = "g_unknown"
        self._issue(gm, "id")

    def test_more_than_two_is_issue(self):
        self._issue(self.gram(pick=(0, 1, 2)), "count")

    def test_duplicate_id_is_issue(self):
        gm = self.gram(pick=(0,))
        self._issue(gm + gm, "duplicate")

    def test_explanation_status_must_be_provided(self):
        gm = self.gram(pick=(0,))
        gm[0]["explanation_status"] = "missing"
        self._issue(gm, "explanation_status")

    def test_payload_sha_and_example_when_present_must_match(self):
        gm = self.gram(pick=(0,))
        gm[0]["explanation_sha256"] = "0" * 64
        self._issue(gm, "explanation_sha256")
        gm = self.gram(pick=(0,))
        gm[0]["example"] = "Some other sentence."
        self._issue(gm, "example")

    def test_corrected_resend_after_issue_succeeds(self):
        gm = self.gram(pick=(0,))
        bad = [dict(gm[0], title="別の文法名")]
        with Env(self.tmp) as env:
            with self.assertRaises(rv.ConfirmedContentIssue):
                self.form(env, bad)
            out = self.form(env, gm)
            self.assertEqual(out["grammar"], 1)
            self.assertIsNotNone(self.rec())


class T4_FailClosed(GBase):
    def test_level_mismatch_of_candidate_doc_is_fail_closed(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            p = gr.paths(self.sd)["candidates"]
            d = jl(p)
            d["level"] = "Standard"                                               # b1b dirなのに候補docはStandard(pathから推定しない)
            jd(p, d)
            cands = rv.load_candidates(self.kp_dir)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=[])
            with self.assertRaises(cc.CliError) as cm:
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            self.assertIn("次の一手", str(cm.exception))
            self.assertIsNone(self.rec())
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)

    def test_incomplete_pregen_refuses_even_for_zero_grammar(self):
        with Env(self.tmp) as env:
            self.prep_grammar(pregen=False)
            self._gen(env)
            cands = rv.load_candidates(self.kp_dir)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=[])
            with self.assertRaises(cc.CliError) as cm:
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            self.assertIn("grammar-pregen", str(cm.exception))
            self.assertIsNone(self.rec())
            self.assertNotEqual(gr.load_review(self.sd)["status"], rv.ST_REVIEWED)

    def test_part2_failed_json_refuses(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            wr(os.path.join(self.sd, g.FAILED_FILENAME), json.dumps({"schema": "part2_failed_v1", "stage": "part2_expl_b1b", "error": "boom"}))
            gm = self.gram.__func__  # noqa: F841 (formは例外前にbundleを作れない: 同じfail-closedをexporter側でも確認)
            with self.assertRaises(g.Part2Stale):
                p2w.form_grammar_bundle(self.sd, level="b1b")
            cands = rv.load_candidates(self.kp_dir)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=[{"id": "g1", "title": "x", "explanation_full": "y", "explanation_status": "provided"}])
            with self.assertRaises(cc.CliError):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            self.assertIsNone(self.rec())

    def test_tampered_explanations_sha_refuses(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            gm = self.gram(pick=(0,))
            ep = gr.paths(self.sd)["explanations"] if "explanations" in gr.paths(self.sd) else os.path.join(self.sd, "grammar_explanations.json")
            d = jl(ep)
            d["items"][0]["explanation_md"] += "\n(改変)"
            jd(ep, d)
            cands = rv.load_candidates(self.kp_dir)
            pl = self._payload(cands, cat1=[1, 2, 3], cat2=[4, 5], grammar=gm)
            with self.assertRaises(cc.CliError):
                cc.cmd_from_form(self.run_dir, "b1b", self._write(pl), "human", self.uref)
            self.assertIsNone(self.rec())


class T5_OrderAndIdempotency(GBase):
    def test_call_order_validate_then_lock_then_grammar_sidecar_record(self):
        order = []
        orig_sel, orig_apply, orig_side, orig_save, orig_validate = rv.op_select, gr.apply_form_selection, cc._write_grammar_sidecar, cc.save_record, cc._validate_form_grammar
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            gm = self.gram(pick=(0, 1))
            with mock.patch.object(cc, "_validate_form_grammar", side_effect=lambda *a, **k: (order.append("validate"), orig_validate(*a, **k))[1]), \
                    mock.patch.object(rv, "op_select", side_effect=lambda *a, **k: (order.append("kp_select"), orig_sel(*a, **k))[1]), \
                    mock.patch.object(gr, "apply_form_selection", side_effect=lambda *a, **k: (order.append("grammar_review"), orig_apply(*a, **k))[1]), \
                    mock.patch.object(cc, "_write_grammar_sidecar", side_effect=lambda *a, **k: (order.append("sidecar"), orig_side(*a, **k))[1]), \
                    mock.patch.object(cc, "save_record", side_effect=lambda *a, **k: (order.append("record"), orig_save(*a, **k))[1]):
                self.form(env, gm)
        self.assertEqual(order, ["validate", "kp_select", "grammar_review", "sidecar", "record"])

    def test_crash_before_commit_then_resend_is_idempotent(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            gm = self.gram(pick=(0, 1))
            with mock.patch.object(cc, "save_record", side_effect=RuntimeError("simulated crash before commit")):
                with self.assertRaises(RuntimeError):
                    self.form(env, gm)
            self.assertIsNone(self.rec())                                          # 確定点(KPレコード)が無い=未確定
            rev1 = gr.load_review(self.sd)["revision"]
            self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_REVIEWED)
            out = self.form(env, gm)                                               # 同じ入力の再送
            self.assertEqual(out["grammar"], 2)
            self.assertEqual(gr.load_review(self.sd)["revision"], rev1)           # 文法reviewは変更されない(冪等)
            self.assertIsNotNone(self.rec())
            self.assertEqual(self.rec()["grammar"]["count"], 2)

    def test_grammar_apply_failure_writes_no_record(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self._gen(env)
            gm = self.gram(pick=(0,))
            with mock.patch.object(gr, "apply_form_selection", side_effect=g.Part2ReviewError("boom")):
                with self.assertRaises(cc.CliError) as cm:
                    self.form(env, gm)
            self.assertIn("再実行は安全", str(cm.exception))
            self.assertIsNone(self.rec())
            self.assertFalse(os.path.exists(os.path.join(self.sd, cc.FILE_GRAMMAR)))

    def test_resend_of_confirmed_form_is_locked_not_silently_duplicated(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            gm = self.gram(pick=(0,))
            self.form(env, gm)
            with self.assertRaises(rv.ConfirmedContentLocked):
                self.form(env, gm)


class T6_Levels(GBase):
    def test_std_level_has_its_own_sidecar_and_does_not_touch_adv(self):
        with Env(self.tmp) as env:
            self.prep_grammar("b1b")
            self.prep_grammar("a2")
            adv_before = gr.load_review(self.sd)["revision"]
            out = self.form(env, self.gram("a2", pick=(0, 1)), level="a2", cat1=(1, 2, 3), cat2=())
            self.assertEqual(out["grammar"], 2)
            rec = cc.load_record(self.kp_dir_a2)
            self.assertEqual((rec["grammar"]["level"], rec["grammar"]["path_rel"]), ("a2", "a2/study_text/confirmed_grammar.json"))
            self.assertEqual(jl(os.path.join(self.sd_a2, cc.FILE_GRAMMAR))["level"], "a2")
            self.assertFalse(os.path.exists(os.path.join(self.sd, cc.FILE_GRAMMAR)))      # Advのsidecarは作られない
            self.assertEqual(gr.load_review(self.sd)["revision"], adv_before)
            self.assertIsNone(cc.grammar_state(self.sd))
            st = cc.grammar_state(self.sd_a2)
            self.assertEqual(st["level"], "a2")
            res = self.finalize("a2")["result"]
            self.assertEqual(len(res["items"]), 2)
            cc.verify_part2_items(self.sd_a2, res)

    def test_sidecar_of_other_level_is_integrity(self):
        with Env(self.tmp) as env:
            self.prep_grammar("a2")
            self.form(env, self.gram("a2", pick=(0,)), level="a2", cat1=(1, 2, 3), cat2=())
            sp = os.path.join(self.sd_a2, cc.FILE_GRAMMAR)
            d = jl(sp)
            d["level"] = "b1b"
            d["sidecar_sha256"] = cc._jsha({k: v for k, v in d.items() if k != "sidecar_sha256"})
            jd(sp, d)
            rec = self.rec(self.kp_dir_a2)
            rec["grammar"]["sidecar_sha256"] = d["sidecar_sha256"]
            with rv.review_lock(self.kp_dir_a2, rv.KIND_KP, "t"):
                cc.save_record(self.kp_dir_a2, rec)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation) as cm:
                cc.grammar_state(self.sd_a2)
            self.assertIn("level", str(cm.exception))


class T7_V1Compat(GBase):
    def _to_v1(self, level="b1b"):
        """v2で確定したrunのsidecar/凍結をv1形式へ書き換えて(再署名)、v1読取互換を確認するfixture(1件確定)。"""
        sd = self.sdir(level)
        sp = os.path.join(sd, cc.FILE_GRAMMAR)
        d = jl(sp)
        v1 = {"schema": cc.SCHEMA_GRAMMAR, "confirmation_id": d["confirmation_id"], "items": [{k: i.get(k) for k in ("id", "title", "explanation_full", "explanation_status", "example")} for i in d["items"]],
              "kp_dir_rel": d["kp_dir_rel"]}
        v1["content_sha256"] = cc._jsha(v1["items"])
        v1["sidecar_sha256"] = cc._jsha({k: x for k, x in v1.items() if k != "sidecar_sha256"})
        jd(sp, v1)
        kd = self.kpd(level)
        rec = cc.load_record(kd)
        rec["grammar"] = {"path_rel": rec["grammar"]["path_rel"], "sidecar_sha256": v1["sidecar_sha256"], "count": 1, "explanation_source": ["form_displayed"]}
        with rv.review_lock(kd, rv.KIND_KP, "t"):
            cc.save_record(kd, rec)

    def test_v1_sidecar_and_v1_frozen_are_readable_and_verifiable(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.form(env, self.gram(pick=(0,)))
            self._to_v1()
            st = cc.grammar_state(self.sd)
            self.assertEqual(st["sidecar"]["schema"], cc.SCHEMA_GRAMMAR)
            self.assertEqual(st["level"], "b1b")                                     # levelは確定レコードの article.level(sidecar v1にlevelは無い)
            c = gr.load_candidates(self.sd)["candidates"]
            cid = cc._side_ids(st)[0]
            cand = next(x for x in c if x["candidate_id"] == cid)
            md = jl(os.path.join(self.sd, "grammar_explanations.json"))["items"][0]["explanation_md"]
            md = next(i for i in jl(os.path.join(self.sd, "grammar_explanations.json"))["items"] if i["candidate_id"] == cid)["explanation_md"]
            tr = cc.translation_from_explanation_full(md)
            fz1 = {"schema": cc.SCHEMA_GRAMMAR_FROZEN, "confirmation_id": self.rec()["confirmation_id"], "candidate_id": cid, "sentence": cand["sentence"], "construct_ja": cand["construct_ja"],
                   "explanation_md": md, "sections": {}, "translation_ja": tr, "ref_ja_at_freeze": None, "source": "form_displayed", "frozen_at": "x",
                   "frozen_sha256": cc.frozen_sha(cid, cand["sentence"], md, tr)}
            fz1["file_sha256"] = cc._jsha({k: v for k, v in fz1.items() if k != "file_sha256"})
            jd(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN), fz1)
            items = cc.load_frozen_grammar_items(self.sd)
            self.assertEqual([i["candidate_id"] for i in items], [cid])             # v1(単一)=長さ1として読む
            self.assertEqual(cc.load_frozen_grammar(self.sd)["frozen_sha256"], fz1["frozen_sha256"])
            self.assertEqual(jl(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN))["schema"], cc.SCHEMA_GRAMMAR_FROZEN)   # 読んでも書き換えない
            res = self.finalize()["result"]
            cc.verify_part2(self.sd, res)                                            # v1名のAPIでもv2結果を検査できる(1件)
            cc.verify_part2_items(self.sd, res)
            self.assertEqual(res["items"][0]["frozen_source"], "form_displayed")


class T7b_MalformedAndRebind(GBase):
    def test_malformed_sidecar_explanation_is_issue_not_regenerated(self):
        """v1/手編集由来で構造が不正な『フォームで見せた解説全文』は、Step Bで作り直さずISSUE(再確認)。凍結は作られない。"""
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.form(env, self.gram(pick=(0,)))
            sp = os.path.join(self.sd, cc.FILE_GRAMMAR)
            d = jl(sp)
            d["items"][0]["explanation_full"] = "見出しの無い解説全文"
            d["sidecar_sha256"] = cc._jsha({k: v for k, v in d.items() if k != "sidecar_sha256"})
            jd(sp, d)
            rec = self.rec()
            rec["grammar"]["sidecar_sha256"] = d["sidecar_sha256"]
            with rv.review_lock(self.kp_dir, rv.KIND_KP, "t"):
                cc.save_record(self.kp_dir, rec)
            n = self.xp.n
            cand = gr.load_candidates(self.sd)["candidates"]
            sel = [c for c in cand if c["candidate_id"] == d["items"][0]["id"]]
            with self.assertRaises(rv.ConfirmedContentIssue):
                cc.freeze_from_sidecar_items(self.sd, sel)
            self.assertFalse(os.path.exists(os.path.join(self.sd, cc.FILE_GRAMMAR_FROZEN)))
            self.assertEqual(self.xp.n, n)

    def test_text_change_rebind_checks_every_confirmed_grammar_sentence(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.form(env, self.gram(pick=(0, 1)))
            from er119_test_support_01 import ARTICLE
            new_text = ARTICLE + "\n\nAn extra closing paragraph is appended here."
            msg = cc.stale_or_rebind(self.kp_dir, new_text, "f" * 64)
            self.assertIsNotNone(msg)
            self.assertNotEqual(msg, "REBOUND")                                          # 確定した文法の英文が新本文に無い=黙って再バインドしない
            diffs = jl(cc.paths_of(self.kp_dir)["issue_json"])["diffs"]
            self.assertEqual(sorted(d["candidate_id"] for d in diffs if d["field"] == "grammar.sentence"), sorted(x["id"] for x in self.gram(pick=(0, 1))))
            self.assertEqual(self.rec()["state"], cc.STATE_LIVE)                         # 確定内容は変更しない


class T8_Reconfirm(GBase):
    def test_revoke_then_reconfirm_with_other_set_archives_stale_frozen(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            self.form(env, self.gram(pick=(0,)))
            self.finalize()
            old_conf = self.rec()["confirmation_id"]
            self.assertIsNotNone(cc.load_frozen_grammar_items(self.sd))
            cc.cmd_revoke(self.run_dir, "b1b", "human", self.uref, "選び直す")
            self.assertIsNone(cc.grammar_state(self.sd))                              # 取消後は保護なし
            out = self.form(env, self.gram(pick=(1, 2)))
            self.assertEqual(out["grammar"], 2)
            self.assertNotEqual(self.rec()["confirmation_id"], old_conf)
            fzs = [f for f in os.listdir(self.sd) if f.startswith("confirmed_grammar_frozen")]
            self.assertTrue(any("RECONFIRM_SUPERSEDED" in f for f in fzs), fzs)       # 古い凍結は退避(INTEGRITY化しない)
            self.assertNotIn(cc.FILE_GRAMMAR_FROZEN, fzs)
            res = self.finalize()["result"]
            self.assertEqual(sorted(i["selection"]["candidate_id"] for i in res["items"]),
                             sorted(x["id"] for x in self.gram(pick=(1, 2))))
            cc.verify_part2_items(self.sd, res)


class T9_GuardGrammar(GBase):
    def test_guard_requires_the_exact_confirmed_set(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            gm = self.gram(pick=(0, 1))
            self.form(env, gm)
            ids = [x["id"] for x in gm]
            cc.guard_grammar(self.sd, "x", candidate_ids=ids)                          # 同じ集合=許可
            cc.guard_grammar(self.sd, "x", candidate_ids=list(reversed(ids)))
            for bad in ([ids[0]], [ids[0], "g_other"], [], ids + ["g_other"]):
                with self.assertRaises(rv.ConfirmedContentLocked):
                    cc.guard_grammar(self.sd, "x", candidate_ids=bad)
            with self.assertRaises(rv.ConfirmedContentLocked):                         # 確定2件のうち1件だけを選ぶtop1は書換え
                cc.guard_grammar(self.sd, "x", candidate_id=ids[0])
            with self.assertRaises(rv.ConfirmedContentLocked):
                cc.guard_grammar(self.sd, "reselect")

    def test_decide_same_set_is_allowed_other_is_locked(self):
        with Env(self.tmp) as env:
            self.prep_grammar()
            gm = self.gram(pick=(0, 1))
            self.form(env, gm)
            sha = gr.load_candidates(self.sd)["candidates_sha256"]
            ids = [x["id"] for x in gm]
            gr.op_decide(self.sd, choice="pick", ids=ids, candidates_sha256=sha, reason="確定の反映", by="human")
            with self.assertRaises(rv.ConfirmedContentLocked):
                gr.op_decide(self.sd, choice="pick", ids=ids[:1], candidates_sha256=sha, reason="x", by="human")
            with self.assertRaises(rv.ConfirmedContentLocked):
                gr.op_decide(self.sd, choice="omit", reason="x", candidates_sha256=sha, by="human")


class T11_Cli(GBase):
    """grammar-* CLI(level必須・pick --ids・accept-translation・pregen)。pregenのStep Bは g._default_call_fn_factory をmockへ差替え(API 0)。"""

    def run_cli(self, argv):
        import contextlib
        import io
        import er119_kp_human_review_cli_01 as cli
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = cli.run(argv)
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue(), err.getvalue()

    def sha(self, level="b1b"):
        return gr.load_candidates(self.sdir(level))["candidates_sha256"]

    def test_level_is_required_for_every_grammar_command(self):
        self.prep_grammar()
        for cmd, extra in (("grammar-show", []), ("grammar-select", ["--choice", "omit", "--candidates-sha", "x", "--by", "t"]), ("grammar-ng", ["--rank", "1", "--reason", "r", "--by", "t"]),
                           ("grammar-unng", ["--sentence", "x", "--reason", "r", "--by", "t"]), ("grammar-pregen", []),
                           ("grammar-accept-translation", ["--candidate-id", "g1", "--user-ref", "x", "--by", "t"])):
            rc, out, err = self.run_cli([cmd, "--run", self.run_dir] + extra)
            self.assertEqual(rc, 2, cmd)
            self.assertIn("--level", err, cmd)                                           # argparse: --level必須(先頭dir/pathから推定しない)

    def test_show_and_select_target_the_given_level_only(self):
        self.prep_grammar("b1b")
        self.prep_grammar("a2")
        rc, out, err = self.run_cli(["grammar-show", "--run", self.run_dir, "--level", "a2"])
        self.assertEqual(rc, 0, err)
        self.assertIn("(Standard)", out)
        self.assertNotIn("(Advanced)", out)
        ids = [c["candidate_id"] for c in gr.load_candidates(self.sd_a2)["candidates"]]
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "a2", "--choice", "pick", "--ids", f"{ids[2]},{ids[0]}", "--reason", "2件選ぶ",
                                     "--candidates-sha", self.sha("a2"), "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(sorted(gr.load_review(self.sd_a2)["selection"]["candidate_ids"]), sorted([ids[0], ids[2]]))
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)              # Advは触られない

    def test_pick_requires_ids_and_ids_only_for_pick(self):
        self.prep_grammar()
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "pick", "--candidates-sha", self.sha(), "--by", "t"])
        self.assertEqual(rc, 2)
        self.assertIn("--ids", err)
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "top1", "--ids", "g1", "--candidates-sha", self.sha(), "--by", "t", "--accept-ai"])
        self.assertEqual(rc, 2)
        self.assertIn("--choice pick", err)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)

    def test_missing_level_dir_gives_next_step_and_never_falls_back_to_other_level(self):
        self.prep_grammar("b1b")
        rc, out, err = self.run_cli(["grammar-show", "--run", self.run_dir, "--level", "a2"])
        self.assertEqual(rc, 2)
        self.assertIn("次の一手", err)
        self.assertEqual(out, "")                                                         # b1bのデータを出さない

    def test_accept_translation_records_idempotently_and_requires_user_ref(self):
        self.prep_grammar()
        cid = gr.load_candidates(self.sd)["candidates"][0]["candidate_id"]
        sent = gr.load_candidates(self.sd)["candidates"][0]["sentence"]
        gr.op_decide(self.sd, choice="pick", ids=[cid], candidates_sha256=self.sha(), reason="x", by="human", accept_ai=True)
        with self.assertRaises(p2w.Part2NotConfirmed):                                    # Part 1訳との食い違い=ISSUE(rc=4)
            self.finalize(ref_ja_pool={sent: "Part 1の別訳です。"})
        args = ["grammar-accept-translation", "--run", self.run_dir, "--level", "b1b", "--candidate-id", cid, "--by", "human"]
        rc, out, err = self.run_cli(args + ["--user-ref", os.path.join(self.tmp, "nope.md")])
        self.assertEqual(rc, 2)
        self.assertIn("存在しません", err)
        uref = os.path.join(self.tmp, "user_ack.md")
        wr(uref, "ユーザー了承(test fixture)\n")
        rc, out, err = self.run_cli(args + ["--user-ref", uref])
        self.assertEqual(rc, 0, err)
        self.assertEqual(json.loads(out)["accepted_now"], [cid])
        rc, out, err = self.run_cli(args + ["--user-ref", uref])                          # 再送は冪等
        self.assertEqual(rc, 0, err)
        self.assertEqual((json.loads(out)["accepted_now"], json.loads(out)["already_recorded"]), ([], [cid]))
        self.assertEqual(len(gr.load_translation_acks(self.sd)[cid]), 1)
        self.assertEqual(self.finalize(ref_ja_pool={sent: "Part 1の別訳です。"})["status"], "SELECTED")   # 了承の記録で解消
        rc, out, err = self.run_cli(["grammar-accept-translation", "--run", self.run_dir, "--level", "b1b", "--candidate-id", "g_unknown", "--by", "human", "--user-ref", uref])
        self.assertEqual(rc, 2)

    def test_pregen_generates_missing_only_and_second_run_is_api_free(self):
        self.prep_grammar(pregen=False)
        mk.CALLS.clear()
        with mock.patch("er003_v1_b1_scaffold_01_generate.get_client", return_value=object()), mock.patch.object(g, "_default_call_fn_factory", mk.factory):
            rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b"])
            self.assertEqual(rc, 0, err)
            res = json.loads(out)
            self.assertEqual((len(res["generated"]), res["reused"], res["confirmed"]), (3, [], False))
            self.assertIn("grammar-show", res["next"])
            self.assertEqual(mk.CALLS.count("explain"), 3)
            rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b"])
            self.assertEqual(rc, 0, err)
            self.assertEqual((json.loads(out)["generated"], len(json.loads(out)["reused"])), ([], 3))
            self.assertEqual(mk.CALLS.count("explain"), 3)                                 # 再実行はAPI 0
        p2w.form_grammar_bundle(self.sd, level="b1b")                                     # 事前生成が揃えばフォームデータも出る

    def test_pregen_all_candidates_is_explicit_opt_in_for_auto_adopted_run(self):
        self.prep_grammar(pregen=False)
        rv.add_declaration(run_dirs=[self.run_dir], by="t", reason="r")
        gr.ensure_grammar_review(self.sd, level="b1b", run_dir=self.run_dir, family="x", slug="coffee", paragraphs=PARAS, label=LABEL, extract_call_fn=mk.mock_extract_call_fn)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_AUTO)
        mk.CALLS.clear()
        with mock.patch("er003_v1_b1_scaffold_01_generate.get_client", return_value=object()), mock.patch.object(g, "_default_call_fn_factory", mk.factory):
            rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b"])
            self.assertEqual((rc, mk.CALLS.count("explain"), json.loads(out)["confirmed"]), (0, 1, True))   # 既定=選定済み(TOP1)のみ
            rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b", "--all-candidates"])
            self.assertEqual((rc, mk.CALLS.count("explain")), (0, 3))                       # 明示opt-inで残りの候補
            self.assertIn("grammar-show", json.loads(out)["next"])

    def test_pregen_refuses_under_stop_and_ids_without_core_support(self):
        self.prep_grammar(pregen=False)
        mk.CALLS.clear()
        with mock.patch("er003_v1_b1_scaffold_01_generate.get_client", return_value=object()), mock.patch.object(g, "_default_call_fn_factory", mk.factory):
            wr(os.path.join(self.run_dir, "STOP"), "stop")                                   # 自runのSTOP
            rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b"])
            self.assertEqual(rc, 2)
            self.assertIn("STOP", err)
            os.remove(os.path.join(self.run_dir, "STOP"))
            if "ids" not in inspect.signature(p2w.pregen_stage).parameters:
                rc, out, err = self.run_cli(["grammar-pregen", "--run", self.run_dir, "--level", "b1b", "--ids", "g1"])
                self.assertEqual(rc, 2)
                self.assertIn("--ids に未対応", err)
        self.assertEqual(mk.CALLS, [])                                                      # どちらも有料呼出なし


class T13_Exporter(GBase):
    """フォームexporter(export_form_data_01 --grammar-study-dir): form_grammar_bundleを直接読み、不完全/失敗/不整合はデータを出さずrc=4(fail-closed)。"""

    def setUp(self):
        super().setUp()
        import importlib.util
        path = os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py")
        spec = importlib.util.spec_from_file_location("export_form_data_01_t", path)
        self.ex = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.ex)

    def export(self, level="b1b", extra=None, out=None):
        import contextlib
        import io
        with Env(self.tmp) as env:
            self._gen(env, level=level)
        cand = rv.paths(self.kpd(level))["candidates"]
        out = out or os.path.join(self.tmp, f"form_{level}.json")
        argv = ["--cand", cand, "--slug", "coffee", "--level", level, "--name", "Coffee", "--family", "X", "--out", out] + (extra or [])
        so, se = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
            try:
                rc = self.ex.main(argv)
            except SystemExit as e:
                rc = e.code
        return rc, out, so.getvalue(), se.getvalue()

    def test_study_dir_reads_bundle_directly_with_contract_keys(self):
        self.prep_grammar("a2")
        rc, out, so, se = self.export("a2", ["--grammar-study-dir", self.sd_a2])
        self.assertEqual(rc, 0, se)
        doc = jl(out)
        bundle = p2w.form_grammar_bundle(self.sd_a2, level="a2")
        self.assertEqual(doc["grammar_status"], "candidates_available")
        self.assertEqual([x["id"] for x in doc["grammar"]], [x["id"] for x in bundle["items"]])
        for e, b in zip(doc["grammar"], bundle["items"]):
            self.assertEqual((e["candidate_id"], e["title"], e["body"], e["explanation_full"], e["explanation_sha256"], e["level"], e["explanation_status"]),
                             (b["candidate_id"], b["title"], b["explanation_full"], b["explanation_full"], b["explanation_sha256"], "Standard", "provided"))
        self.assertEqual([e["ai_recommended"] for e in doc["grammar"]], [True, False, False])
        # フォーム確定側(cmd_from_form)と同じ契約: exporterが出したgrammar[]のid/title/explanation_fullでそのまま照合を通る
        with Env(self.tmp) as env:
            gm = [{k: e[k] for k in ("id", "title", "explanation_full", "explanation_status", "example")} for e in doc["grammar"][:2]]
            self.assertEqual(self.form(env, gm, level="a2", cat1=(1, 2, 3), cat2=())["grammar"], 2)

    def test_incomplete_pregen_writes_nothing_and_returns_4(self):
        self.prep_grammar("b1b", pregen=False)
        rc, out, so, se = self.export("b1b", ["--grammar-study-dir", self.sd])
        self.assertEqual(rc, 4)
        self.assertFalse(os.path.exists(out))                                            # データを出さない
        err = json.loads(se)
        self.assertEqual(err["status"], "GRAMMAR_NOT_READY")
        self.assertIn("grammar-pregen", err["next"])
        self.assertTrue(err["data_warnings"])
        self.assertNotIn("candidates_available", se)

    def test_failed_json_and_sha_tamper_return_4(self):
        self.prep_grammar("b1b")
        wr(os.path.join(self.sd, g.FAILED_FILENAME), json.dumps({"schema": "part2_failed_v1", "stage": "part2_expl_b1b", "error": "boom"}))
        rc, out, so, se = self.export("b1b", ["--grammar-study-dir", self.sd])
        self.assertEqual((rc, os.path.exists(out)), (4, False))
        os.remove(os.path.join(self.sd, g.FAILED_FILENAME))
        ep = os.path.join(self.sd, "grammar_explanations.json")
        d = jl(ep)
        d["items"][0]["explanation_md"] += "\n(改変)"
        jd(ep, d)
        rc, out, so, se = self.export("b1b", ["--grammar-study-dir", self.sd])
        self.assertEqual((rc, os.path.exists(out)), (4, False))

    def test_level_mismatch_and_double_source_are_refused(self):
        self.prep_grammar("b1b")
        rc, out, so, se = self.export("a2", ["--grammar-study-dir", self.sd])           # a2のフォームにb1bのstudy dirは渡せない
        self.assertEqual((rc, os.path.exists(out)), (4, False))
        bj = os.path.join(self.tmp, "bundle.json")
        jd(bj, p2w.form_grammar_bundle(self.sd, level="b1b"))
        rc, out, so, se = self.export("b1b", ["--grammar-study-dir", self.sd, "--grammar-bundle", bj])
        self.assertNotEqual(rc, 0)
        self.assertFalse(os.path.exists(out))

    def test_zero_candidates_is_no_candidates_found_not_available(self):
        gr.ensure_grammar_review(self.sd, level="b1b", run_dir=self.run_dir, family="x", slug="coffee", paragraphs=["Short."], label=LABEL, extract_call_fn=mk.mock_extract_call_fn)
        p2w.pregen_stage(self.sd, level="b1b", next_command="rerun", explain_call_fn=self.xp)
        rc, out, so, se = self.export("b1b", ["--grammar-study-dir", self.sd])
        self.assertEqual(rc, 0, se)
        doc = jl(out)
        self.assertEqual((doc["grammar_status"], doc["grammar"]), ("no_candidates_found", []))


class T10_Static(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "er128_kp_confirmed_content_01.py"), encoding="utf-8") as f:
            self.src = f.read()

    def test_no_implicit_b1b_default_and_no_discover_dirs_first(self):
        self.assertNotIn('or "b1b"', self.src)
        self.assertNotIn("discover_dirs(run)", self.src)
        self.assertFalse(re.search(r"discover_dirs\([^)]*\)\s*\[0\]", self.src))
        for m in re.finditer(r"discover_dirs\(([^)]*)\)", self.src):
            self.assertIn("level", m.group(1))

    def test_grammar_max_matches_core_and_four_contract_functions_exist(self):
        self.assertEqual(cc.GRAMMAR_MAX, g.GRAMMAR_MAX)
        for fn in ("load_frozen_grammar_items", "freeze_from_sidecar_items", "freeze_part2_result_items", "verify_part2_items"):
            self.assertTrue(inspect.isfunction(getattr(cc, fn)))
        self.assertEqual(list(inspect.signature(cc.freeze_from_sidecar_items).parameters), ["study_dir", "selected_candidates"])
        self.assertEqual(list(inspect.signature(cc.freeze_part2_result_items).parameters), ["study_dir", "result"])

    def test_frozen_sha_rule_equals_core(self):
        self.assertEqual(cc.frozen_sha("g1", "S", "E", "T"), g.frozen_sha_of("g1", "S", "E", "T"))

    def test_rec_level_is_required(self):
        for bad in ({}, {"article": {}}, {"article": {"level": "Advanced"}}):
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                cc._rec_level(bad)
        self.assertEqual(cc._rec_level({"article": {"level": "a2"}}), "a2")


if __name__ == "__main__":
    unittest.main()
