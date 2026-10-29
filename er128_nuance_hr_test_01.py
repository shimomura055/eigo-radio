# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02B Track C: ニュアンス解説のHuman Review統合(フォームV3・照合コードAIF2・exporter・cmd_from_form・sidecar・N2検査)のtest。全てmock・API 0。

対象(ユーザー正式決定2026-10-29 §2A-3/4・§2B・§2D、Opus M-3/M-4/R-1/R-4/R-5/R-11、TEST_PLAN H-1〜H-14相当):
  採用/不採用/未回答(ISSUE)/候補なし/LEGACY(遡及なし)・古いフォーム(sha)・被覆欠落(M-4)・pool_conflicts・confirm-reviseで誤STALEにならない(M-3)・
  revoke後の再確定で旧採否を既定表示+旧sidecar退避(R-11)・--grammar-pendingと結合しない(R-1)・SUPPRESSED廃止(R-4)・AIF1バイト不変・AIF2の往復と改ざん検出・exporter・フォームJS。
実行: .venv/Scripts/python.exe -m pytest er128_nuance_hr_test_01.py -q
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import copy
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g
import er120_part2_wiring_01 as p2w
import er128_form_readable_restore_01 as R
import er128_kp_confirmed_content_01 as cc
import er134_nuance_explanation_01 as nx
import er134_nuance_explanation_01_test_01 as nt
from er119_test_support_01 import Env, jd, jl, rd, wr
from er128_kp_confirmed_content_grammar_v2_test_01 import GBase, PARAS, LABEL

ROOT = os.path.dirname(os.path.abspath(__file__))
FORM_LOGIC = os.path.join(ROOT, "user_test", "selection_form_v3", "form_logic.js")
HAVE_NODE = shutil.which("node") is not None
QUOTE = "Nobody spoke."


class NBase(GBase):
    """文法(Top1/Top2事前生成)+KP候補+ニュアンス候補doc(er134の実関数で生成。LLMはmock)を用意する。"""

    def nuance_doc(self, env, level="b1b", *, same=(), candidate=True, gen_expr="nobody vs no one", spec=True, prov_n=5):
        cands = self._gen(env, level=level)
        sd = self.prep_grammar(level)
        if spec:
            nx.ensure_spec(sd, level=level, new_review=True)
        by_rank = sorted(cands["candidates"], key=lambda c: c["ai_rank"])
        gitems = p2w.form_grammar_bundle(sd, level=level)["items"]
        inp = nx.build_inputs(family="X", article_id="coffee", title=LABEL, level=level, paragraphs=PARAS, kp_cands=cands, grammar_items=gitems,
                              provisional_ids=[c["candidate_id"] for c in by_rank[:prov_n]])
        same_ids = [c["candidate_id"] if isinstance(c, dict) else c for c in same]
        gen = nt.Fn(nt.gen_json(expression=gen_expr, quote=QUOTE, candidate=candidate))
        lab = {m["item_id"]: lid for lid, m in nx.labels_for(inp).items()}
        jdg = nt.Fn(nt.judge_json(inp, same=tuple(lab.get(i, i) for i in same_ids)))
        res = nx.candidate_stage(sd, inp, call_fn=gen, judge_fn=jdg)
        return sd, inp, res["doc"], cands

    def pool_rank(self, cands, rank):
        return next(c["candidate_id"] for c in cands["candidates"] if c["ai_rank"] == rank)

    def payload_with(self, cands, nuance=None, *, level="b1b", cat1=(1, 2, 3), cat2=(4, 5), grammar=None, **mods):
        pl = self._payload(cands, cat1=list(cat1), cat2=list(cat2), grammar=grammar if grammar is not None else self.gram(level=level, pick=(0,)), level=level, **mods)
        if nuance is not None:
            pl["selection"]["nuance"] = nuance
            pl["schema_minor"] = 2
        return pl

    def nz(self, doc, decision):
        c = doc["candidate"]
        return {"decision": decision, "candidate_sha256": c["candidate_sha256"], "id": cc.nuance_id_of(c)}

    def confirm(self, pl, name="payload.json", level="b1b", **kw):
        return cc.cmd_from_form(self.run_dir, level, self._write(pl, name), "human", self.uref, **kw)


class T1_AdoptRejectAndUnanswered(NBase):
    def test_adopt_writes_sidecar_record_mark_and_state_after_grammar_sidecar(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            self.assertEqual(doc["status"], "CANDIDATE")
            out = self.confirm(self.payload_with(cands, self.nz(doc, "adopt")))
            self.assertEqual(out["nuance"], "adopted")
            rec = self.rec()
            side = jl(os.path.join(sd, cc.FILE_NUANCE))
            self.assertEqual((side["schema"], side["decision"], side["level"], side["confirmation_id"]), (cc.SCHEMA_NUANCE, "adopted", "b1b", rec["confirmation_id"]))
            self.assertEqual(side["candidate"], doc["candidate"])                                      # 候補本文を逐語コピー(改変検出用)
            self.assertEqual(side["candidate_sha256"], doc["candidate"]["candidate_sha256"])
            self.assertEqual(rec["nuance"], {"path_rel": os.path.relpath(os.path.join(sd, cc.FILE_NUANCE), self.run_dir).replace(os.sep, "/"),
                                             "sidecar_sha256": side["sidecar_sha256"], "decision": "adopted", "level": "b1b", "schema": cc.SCHEMA_NUANCE})
            self.assertEqual(side["pool_identity_sha"], doc["kp_word_basis"]["pool_identity_sha"])
            self.assertEqual(sorted(side["confirmed_against"]["kp_word"]), sorted(i["candidate_id"] for i in rec["items"]))
            self.assertEqual(side["kp_dir_rel"], os.path.relpath(self.kp_dir, sd).replace(os.sep, "/"))   # 相対path(runごとコピーしても辿れる)
            st = cc.nuance_state(sd)
            self.assertEqual((st["sidecar"]["decision"], st["level"]), ("adopted", "b1b"))
            self.assertEqual(os.path.getmtime(os.path.join(sd, cc.FILE_GRAMMAR)) <= os.path.getmtime(os.path.join(sd, cc.FILE_NUANCE)), True)   # 文法sidecarの直後
            self.assertEqual(gr.load_review(sd)["status"], rv.ST_REVIEWED)                           # 文法の確定は従来どおり
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_REVIEWED)
            self.assertEqual(cc.cmd_status(self.run_dir)["levels"][0]["record"]["nuance"], "adopted")

    def test_reject_is_recorded_and_makes_no_replacement_call(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            before = open(os.path.join(sd, cc.FILE_NUANCE_CANDIDATE), "rb").read()
            out = self.confirm(self.payload_with(cands, self.nz(doc, "reject")))
            self.assertEqual(out["nuance"], "rejected")
            side = jl(os.path.join(sd, cc.FILE_NUANCE))
            self.assertEqual((side["decision"], side["candidate"]), ("rejected", doc["candidate"]))
            self.assertEqual(open(os.path.join(sd, cc.FILE_NUANCE_CANDIDATE), "rb").read(), before)   # 候補docは書換えない(次点の補充・再生成なし。A-7)
            self.assertEqual(self.rec()["nuance"]["decision"], "rejected")

    def test_unanswered_is_issue_and_saves_nothing(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            gram_before = rd(gr.paths(sd)["review"])
            with self.assertRaises(rv.ConfirmedContentIssue) as cm:
                self.confirm(self.payload_with(cands, None))                                           # 候補ありで採否なし=黙って不採用にしない
            self.assertIn("未回答", str(cm.exception) + rd(cc.paths_of(self.kp_dir)["issue_json"]))
            self.assertIsNone(self.rec())                                                              # 確定レコード無し
            self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_NUANCE)))                         # sidecar無し
            self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_GRAMMAR)))                        # 文法sidecarも書かない(全検証が先)
            self.assertEqual(rd(gr.paths(sd)["review"]), gram_before)                                  # 文法reviewも不変
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)
            self.assertEqual(os.path.exists(cc.paths_of(self.kp_dir)["issue_json"]), True)
            exc_code = rv.EXIT_CODE_PENDING
            self.assertEqual(exc_code, 4)

    def test_bad_decision_and_stale_form_are_issues(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            for bad in ({"decision": "maybe", "candidate_sha256": doc["candidate"]["candidate_sha256"]},
                        {"decision": "adopt", "candidate_sha256": "0" * 64},                              # 古いフォーム(別の候補を見て選んだ)
                        {"decision": "adopt", "candidate_sha256": doc["candidate"]["candidate_sha256"], "id": "nuance_other"}):
                with self.assertRaises(rv.ConfirmedContentIssue):
                    self.confirm(self.payload_with(cands, bad))
                self.assertIsNone(self.rec())
                self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_NUANCE)))

    def test_idempotent_same_payload_is_locked_after_confirm(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            pl = self.payload_with(cands, self.nz(doc, "adopt"))
            self.confirm(pl)
            side0 = rd(os.path.join(sd, cc.FILE_NUANCE))
            with self.assertRaises(rv.ConfirmedContentLocked):                                         # 確定後の別決定/再送は拒否(変更はrevoke経由のみ)
                self.confirm(self.payload_with(cands, self.nz(doc, "reject")), "p2.json")
            self.assertEqual(rd(os.path.join(sd, cc.FILE_NUANCE)), side0)
            with self.assertRaises(rv.ConfirmedContentLocked):
                cc.guard_nuance(sd, "--regenerate-stage nuance_cand_b1b")                              # 確定後の候補再生成は拒否(revoke必須)


class T2_CoverageAndConflicts(NBase):
    def test_m4_confirmed_id_not_in_against_is_issue_for_adopt_but_not_for_reject(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            cid = self.pool_rank(cands, 5)                                                              # ②で選ぶ項目
            cp = os.path.join(sd, cc.FILE_NUANCE_CANDIDATE)
            d = jl(cp)
            d["candidate"]["overlap_check"]["against"] = [a for a in d["candidate"]["overlap_check"]["against"] if a["item_id"] != cid]   # judgeから漏れたid
            jd(cp, d)
            with self.assertRaises(rv.ConfirmedContentIssue) as cm:
                self.confirm(self.payload_with(cands, self.nz(doc, "adopt")))
            self.assertIn("coverage", rd(cc.paths_of(self.kp_dir)["issue_json"]))
            self.assertIsNone(self.rec())
            self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_NUANCE)))
            out = self.confirm(self.payload_with(cands, self.nz(doc, "reject")), "p_rej.json")           # 不採用は人間判断を覆さず受理
            self.assertEqual(out["nuance"], "rejected")

    def test_pool_conflict_is_alarm_only_when_that_item_is_chosen_spec2(self):
        """仕様②(2026-10-29): 人間が選んだ②が候補の焦点と重複(pool_conflicts)しても確定は止めず、アラームを記録する。選ばなければアラーム0。"""
        with Env(self.tmp) as env:
            cands0 = self._gen(env)
            conflict = self.pool_rank(cands0, 7)                                                        # 暫定選定(rank1-5)ではないpool項目
            sd, inp, doc, cands = self.nuance_doc(env, same=(conflict,))
            self.assertEqual(doc["status"], "CANDIDATE")
            self.assertIn(conflict, doc["candidate"]["pool_conflicts"])
            out = self.confirm(self.payload_with(cands, self.nz(doc, "adopt"), cat2=(4, 7)))              # ②で選んでも確定する
            self.assertEqual(out["nuance"], "adopted")
            self.assertEqual([a["item_id"] for a in out["nuance_redundancy_alarms"]], [conflict])
            self.assertEqual(self.rec()["nuance"]["decision"], "adopted")
            side = jl(os.path.join(sd, cc.FILE_NUANCE))
            self.assertEqual([a["item_id"] for a in side["redundancy_alarms"]], [conflict])
            self.assertEqual(jl(os.path.join(sd, cc.FILE_NUANCE_ALARM))["alarm_count"], 1)
            self.assertFalse(os.path.exists(cc.paths_of(self.kp_dir)["issue_json"]))                      # ISSUE停止なし

    def test_redundancy_alarm_helper_is_deterministic_and_nonblocking_spec2(self):
        with Env(self.tmp) as env:
            cands0 = self._gen(env)
            conflict = self.pool_rank(cands0, 7)
            sd, inp, doc, cands = self.nuance_doc(env, same=(conflict,))
            alarms = cc.nuance_redundancy_alarms(doc["candidate"], [conflict, "x_not_judged"])
            self.assertEqual([(a["kind"], a["item_id"], a["blocking"]) for a in alarms], [("nuance_vs_kp_word", conflict, False), ("nuance_vs_kp_word_unjudged", "x_not_judged", False)])
            self.assertEqual(cc.nuance_redundancy_alarms(doc["candidate"], []), [])
            self.assertEqual(cc.nuance_redundancy_alarms(None, [conflict]), [])

    def test_grammar_conflict_is_a_warning_only_and_never_blocks(self):
        with Env(self.tmp) as env:
            sd0 = self.prep_grammar()
            gid = nx.build_inputs(family="X", article_id="coffee", title=LABEL, level="b1b", paragraphs=PARAS, kp_cands=self._gen(env),
                                  grammar_items=p2w.form_grammar_bundle(sd0, level="b1b")["items"])["grammar"][0]["id"]
            sd, inp, doc, cands = self.nuance_doc(env, same=(gid,))
            self.assertEqual(doc["candidate"]["grammar_conflicts"], [gid])
            self.assertEqual(doc["candidate"]["overlap_check"]["verdict"], "pass")                      # R-1: 文法はハードNGにしない
            self.confirm(self.payload_with(cands, self.nz(doc, "adopt"), grammar=self.gram(pick=(0,))))   # 文法を選んでも採用できる(警告のみ)
            self.assertEqual(self.rec()["nuance"]["decision"], "adopted")

    def test_pool_identity_change_after_hr_presentation_is_issue_but_translation_revise_is_not(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            pl = self.payload_with(cands, self.nz(doc, "adopt"))
            c2 = copy.deepcopy(cands)
            c2["candidates"][-1]["item"]["display_phrase"] = c2["candidates"][-1]["item"].get("display_phrase", "") + " X"   # 提示pool項目の英語が変わった(reselect等)
            rv.save_candidates(self.kp_dir, c2)
            with self.assertRaises(rv.ConfirmedContentIssue):
                self.confirm(dict(pl, article=dict(pl["article"], candidates_sha256=rv.load_candidates(self.kp_dir)["candidates_sha256"])))
            self.assertIsNone(self.rec())


class T3_NoCandidateLegacyAndAutoMark(NBase):
    def test_no_candidate_confirms_without_nuance_and_rejects_a_nuance_payload(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env, candidate=False)
            self.assertEqual(doc["status"], "NO_CANDIDATE")
            with self.assertRaises(rv.ConfirmedContentIssue):                                           # 候補が無いのに採否が送られた(古い/改変フォーム)
                self.confirm(self.payload_with(cands, {"decision": "adopt", "candidate_sha256": "0" * 64, "id": "x"}))
            self.assertIsNone(self.rec())
            self.confirm(self.payload_with(cands, None), "p_none.json")
            side = jl(os.path.join(sd, cc.FILE_NUANCE))
            self.assertEqual((side["decision"], side["candidate"], side["nuance_doc_status"]), ("none", None, "NO_CANDIDATE"))
            self.assertIsNotNone(side["nuance_doc_sha256"])                                              # 後から候補が現れても人間の判断なしに採用しないための基準

    def test_failed_technical_is_distinguished_and_nonblocking(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            sd = self.prep_grammar()
            nx.ensure_spec(sd, level="b1b", new_review=True)
            d = {"schema": nx.SCHEMA, "family": "X", "article_id": "coffee", "level": "Advanced", "level_key": "b1b", "candidate": None, "status": "FAILED_TECHNICAL",
                 "no_candidate_reason": "failed_technical:api_error", "failed_technical": {"kind": "api_error"}, "text_sha256": g.text_sha256(PARAS),
                 "kp_word_basis": {"candidates_sha256": cands["candidates_sha256"], "pool_identity_sha": cc.nuance_pool_identity_sha(cands)}}
            jd(os.path.join(sd, cc.FILE_NUANCE_CANDIDATE), d)
            b = p2w.form_nuance_bundle(sd, level="b1b", kp_cands=cands)
            self.assertFalse(b["nuance_spec"]["presented"])
            self.assertEqual(b["nuance_spec"]["candidate_status"], "FAILED_TECHNICAL")
            self.assertIn("技術失敗", b["nuance_note_ja"])                                               # R-5: 本物の0件と区別して表示
            self.assertIn("本物の0件ではありません", b["nuance_note_ja"])
            self.confirm(self.payload_with(cands, None))
            self.assertEqual(jl(os.path.join(sd, cc.FILE_NUANCE))["nuance_doc_status"], "FAILED_TECHNICAL")

    def test_legacy_without_spec_is_byte_for_byte_the_old_behaviour(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env, spec=False) if False else (None, None, None, None)
            cands = self._gen(env)
            sd = self.prep_grammar()
            self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_NUANCE_SPEC)))
            out = self.confirm(self.payload_with(cands, None))
            self.assertIsNone(out["nuance"])
            self.assertNotIn("nuance", self.rec())                                                       # 印を作らない(旧レコードのrecord_sha256・バイトを変えない)
            self.assertFalse(os.path.exists(os.path.join(sd, cc.FILE_NUANCE)))
            self.assertIsNone(cc.nuance_state(sd))

    def test_legacy_rejects_a_nuance_payload(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            self.prep_grammar()
            with self.assertRaises(cc.CliError):
                self.confirm(self.payload_with(cands, {"decision": "adopt", "candidate_sha256": "0" * 64, "id": "x"}))
            self.assertIsNone(self.rec())

    def test_spec_without_candidate_doc_is_issue_not_silent_none(self):
        with Env(self.tmp) as env:
            cands = self._gen(env)
            sd = self.prep_grammar()
            nx.ensure_spec(sd, level="b1b", new_review=True)
            with self.assertRaises(rv.ConfirmedContentIssue):
                self.confirm(self.payload_with(cands, None))
            self.assertIsNone(self.rec())


class T4_AfterConfirm(NBase):
    def test_m3_confirm_revise_keeps_the_decision_without_false_stale(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            self.confirm(self.payload_with(cands, self.nz(doc, "adopt")))
            side0 = rd(os.path.join(sd, cc.FILE_NUANCE))
            cid = self.rec()["items"][0]["candidate_id"]
            cc.cmd_revise(self.run_dir, "b1b", "human", self.uref, "訳の修正", [f"{cid}=修正した訳"])      # KP候補docを保存し直す(candidates_sha256が変わる)
            self.assertNotEqual(rv.load_candidates(self.kp_dir)["candidates_sha256"], cands["candidates_sha256"])
            self.assertEqual(cc.nuance_state(sd)["sidecar"]["decision"], "adopted")                       # 誤STALEにならない(confirmation_idで結合)
            self.assertEqual(rd(os.path.join(sd, cc.FILE_NUANCE)), side0)                                  # sidecarは不変
            self.assertEqual(self.rec()["nuance"]["decision"], "adopted")                                  # 新レコード版にも印を引き継ぐ
            self.assertEqual(cc.nuance_pool_identity_sha(rv.load_candidates(self.kp_dir)), doc["kp_word_basis"]["pool_identity_sha"])   # pool同一性は訳の修正で変わらない
            # 一方HR提示時の鮮度確認(exporter側)はcandidates_sha256で行う: 提示後に候補docが変わったフォームは作り直しを求める
            with self.assertRaises(g.Part2Stale):
                p2w.form_nuance_bundle(sd, level="b1b", kp_cands=rv.load_candidates(self.kp_dir))

    def test_sidecar_tamper_is_integrity_violation(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            self.confirm(self.payload_with(cands, self.nz(doc, "reject")))
            p = os.path.join(sd, cc.FILE_NUANCE)
            d = jl(p)
            d["decision"] = "adopted"
            jd(p, d)
            with self.assertRaises(rv.ConfirmedContentIntegrityViolation):
                cc.nuance_state(sd)

    def test_stale_or_rebind_requires_the_adopted_quote_in_the_new_text(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            self.confirm(self.payload_with(cands, self.nz(doc, "adopt")))
            rec = self.rec()
            self.assertEqual(cc._nuance_quotes(self.kp_dir, rec), [("nuance", QUOTE)])
            self.assertEqual(cc._nuance_quotes(self.kp_dir, dict(rec, nuance=dict(rec["nuance"], decision="rejected"))), [])   # 不採用は引用を縛らない

    def test_revoke_then_reconfirm_shows_previous_decision_and_archives_old_sidecar(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            self.confirm(self.payload_with(cands, self.nz(doc, "adopt")))
            cc.cmd_revoke(self.run_dir, "b1b", "human", self.uref, "選び直し")
            self.assertIsNone(cc.nuance_state(sd))                                                         # 取消済み=保護なし
            prev = cc.previous_nuance_decision(sd)
            self.assertEqual(prev["decision"], "adopted")
            self.assertEqual(prev["candidate_sha256"], doc["candidate"]["candidate_sha256"])
            # R-11: 再確定フォームのデータには旧採否が既定表示として載る(同じ候補のときだけ。明示送信は必須)
            cand_doc = rv.load_candidates(self.kp_dir)
            nd = jl(os.path.join(sd, cc.FILE_NUANCE_CANDIDATE))
            nd["kp_word_basis"]["candidates_sha256"] = cand_doc["candidates_sha256"]
            jd(os.path.join(sd, cc.FILE_NUANCE_CANDIDATE), nd)
            b = p2w.form_nuance_bundle(sd, level="b1b", kp_cands=cand_doc)
            self.assertEqual(b["nuance"]["previous_decision"], "adopt")
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")          # 選び直し(reviewをREVIEWEDへ戻す)
            self.confirm(self.payload_with(cand_doc, self.nz(doc, "reject")), "p_re.json")
            side = jl(os.path.join(sd, cc.FILE_NUANCE))
            self.assertEqual(side["decision"], "rejected")
            archived = [f for f in os.listdir(sd) if f.startswith("confirmed_nuance.RECONFIRM_SUPERSEDED")]
            self.assertEqual(len(archived), 1)                                                              # 旧sidecarは退避(削除しない)
            self.assertEqual(jl(os.path.join(sd, archived[0]))["decision"], "adopted")
            self.assertEqual(side["confirmation_id"], self.rec()["confirmation_id"])


class T5_GrammarPendingIndependence(NBase):
    def test_r1_nuance_confirms_with_grammar_pending_and_does_not_wait_for_grammar(self):
        with Env(self.tmp) as env:
            sd, inp, doc, cands = self.nuance_doc(env)
            out = self.confirm(self.payload_with(cands, self.nz(doc, "adopt")), grammar_pending=True)
            self.assertEqual(out["grammar_status"], cc.GRAMMAR_PENDING)
            self.assertEqual(out["nuance"], "adopted")                                                      # 文法の確定を待たずに確定(結合を外した=経路を1本減らした)
            self.assertEqual(self.rec()["nuance"]["decision"], "adopted")


class T6_StaticContracts(unittest.TestCase):
    def test_suppressed_is_abolished_and_no_automatic_override_exists(self):
        for n in ("er128_kp_confirmed_content_01.py", "er120_part2_wiring_01.py", "er120_part2_grammar_production_01.py", "er128_form_readable_restore_01.py"):
            s = open(os.path.join(ROOT, n), encoding="utf-8").read()
            self.assertIsNone(re.search(r"SUPPRESSED\s*=|['\"]SUPPRESSED['\"]", s), n)                           # R-4: 人間の採用を自動で覆さない(定数・状態値として存在しない)
        self.assertFalse(any(hasattr(cc, x) for x in ("nuance_suppress", "suppress_nuance")))

    def test_pool_ids_use_the_same_function_as_the_exporter(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp", os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py"))
        exp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(exp)
        cands = nt.kp_doc()
        cands["candidates_sha256"] = exp.doc_sha256(cands)
        out = exp.convert(cands, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        exp_ids = [e["id"] for e in out["phrases"]] + [e["id"] for e in out["words"]]
        self.assertEqual(sorted(cc.nuance_presented_ids(cands)), sorted(exp_ids))                          # M-4: exporterの提示集合と同一


# ============================================================
# フォームJS(node)とPython(復元ツール)の往復・AIF1バイト不変・改ざん検出
# ============================================================
import hashlib  # noqa: E402
import er128_form_readable_restore_test_01 as RT  # noqa: E402

NSHA = "a" * 64
NUANCE = {"id": "nuance_" + NSHA[:16], "candidate_sha256": NSHA, "expression": "nobody vs no one", "focus": "代名詞nobodyとno oneの使い分け",
          "explanation_ja": "nobodyもno oneも「誰も〜ない」だが、nobodyのほうが口語的で、no oneは書き言葉でやや改まる。",
          "quote_en": "Nobody spoke.", "quote_ja": "誰も話さなかった。", "pool_conflicts": ["p_0000000002"], "grammar_conflicts": [], "shared_terms": [], "overlap_summary_ja": "既存の選定と焦点が重ならない"}


def nuance_dataset(base, *, nuance=NUANCE, spec=True):
    d = copy.deepcopy(base)
    if spec:
        d["nuance_spec"] = {"version": "nuance_v1", "max_select": 1, "allow_zero": True, "presented": bool(nuance), "candidate_status": "CANDIDATE" if nuance else "NO_CANDIDATE"}
        if nuance:
            d["nuance"] = copy.deepcopy(nuance)
        else:
            d["nuance_note_ja"] = "ニュアンス解説の候補はありません"
    return d


def run_node(js, *args):
    return json.loads(subprocess.run(["node", "-e", js, FORM_LOGIC, *args], capture_output=True, check=True).stdout.decode("utf-8"))


@unittest.skipUnless(HAVE_NODE, "node が無い")
class T7_FormJsAndRestore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        base = RT.synth_datasets()["fixture_synth__a2"]
        cls.files = {}
        for key, d in (("adopt", nuance_dataset(base)), ("none", nuance_dataset(base, nuance=None)), ("legacy", nuance_dataset(base, spec=False))):
            stem = f"fixture_nuance_{key}__a2"
            dd = dict(d, slug=f"fixture_nuance_{key}")
            pth = os.path.join(cls.tmp, stem + ".json")
            with open(pth, "wb") as f:
                f.write((json.dumps(dd, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
            cls.files[key] = (stem, pth, dd)
        g = RT.R.grammar_presented(cls.files["adopt"][2])[0]
        cls.st = {"choices": {"run out of": 1, "give up": 2}, "grammar": {g["id"]: True}, "grammar_zero": False, "comment": "強調したい"}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def readable(self, key, **kw):
        stem, pth, d = self.files[key]
        return RT.R.build_readable(stem, d, dict(self.st, **kw), RT.d6_of_file(pth))

    def node_readable(self, key, st):
        stem, pth, d = self.files[key]
        raw = open(pth, "rb").read().replace(b"\r\n", b"\n")
        js = ("const FL=require(process.argv[1]);const d=JSON.parse(process.argv[2]);const st=JSON.parse(process.argv[3]);"
              "try{process.stdout.write(JSON.stringify({ok:FL.buildReadable(d,st,{stem:process.argv[4],file_sha256:process.argv[5]})}));}catch(e){process.stdout.write(JSON.stringify({err:String(e.message)}));}")
        return run_node(js, raw.decode("utf-8"), json.dumps(st, ensure_ascii=False), stem, hashlib.sha256(raw).hexdigest())

    def test_python_equals_node_readable_bytes_for_adopt_reject_none_and_legacy(self):
        for key, nz in (("adopt", "adopt"), ("adopt", "reject"), ("none", None), ("legacy", None)):
            st = dict(self.st, nuance=nz) if nz else dict(self.st)
            got = self.node_readable(key, st)
            self.assertEqual(got.get("ok"), self.readable(key, **({"nuance": nz} if nz else {})), (key, nz, got))

    def test_aif_versions_and_text_blocks(self):
        t = self.readable("adopt", nuance="adopt")
        self.assertIn("ニュアンス解説：採用", t)
        self.assertIn("【ニュアンス全文】", t)
        self.assertIn("本文の英文：Nobody spoke.", t)
        self.assertRegex(t, r"AIF2-fixture_nuance_adopt__a2-[0-9a-f]{6}-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{10}-[0-9a-f]{10}-[0-9a-f]{8}-[0-9a-f]{8}-[0-9a-f]{4}")
        self.assertIn("ニュアンス解説：不採用", self.readable("adopt", nuance="reject"))
        self.assertIn("ニュアンス解説：候補なし", self.readable("none"))
        self.assertRegex(self.readable("none"), r"AIF2-\S+-0-[0-9a-f]{4}")                                   # n8=0
        leg = self.readable("legacy")
        self.assertRegex(leg, r"AIF1-")
        self.assertNotIn("ニュアンス", leg)                                                                  # 仕様マークなし=従来出力(AIF1・ニュアンス行なし)
        self.assertNotEqual(self.readable("adopt", nuance="adopt"), self.readable("adopt", nuance="reject"))

    def test_undecided_is_refused_by_both_implementations(self):
        with self.assertRaises(Exception):
            self.readable("adopt")                                                                          # 候補あり・未回答
        got = self.node_readable("adopt", dict(self.st))
        self.assertIn("未決定", got.get("err", ""))

    def test_restore_roundtrip_matches_node_buildStructured(self):
        for key, nz in (("adopt", "adopt"), ("adopt", "reject"), ("none", None)):
            stem, pth, d = self.files[key]
            st = dict(self.st, nuance=nz) if nz else dict(self.st)
            payload, _ = RT.R.restore(self.readable(key, **({"nuance": nz} if nz else {})), self.tmp)
            exp = RT.node_expected([{"data": pth, "state": st}])[0]
            self.assertEqual(RT.diff_payload(payload, exp), [], (key, nz))
            self.assertEqual(payload["schema_minor"], 2)
            self.assertEqual(payload["restore_meta"]["code_version"], "AIF2")
            if nz:
                self.assertEqual(payload["selection"]["nuance"], {"decision": nz, "candidate_sha256": NSHA, "id": NUANCE["id"]})
            else:
                self.assertNotIn("nuance", payload["selection"])

    def test_legacy_roundtrip_has_no_nuance_keys_and_stays_aif1(self):
        payload, _ = RT.R.restore(self.readable("legacy"), self.tmp)
        self.assertEqual(payload["restore_meta"]["code_version"], "AIF1")
        self.assertEqual(payload["schema_minor"], 1)                                                       # 従来値のまま(2にならない)
        self.assertNotIn("nuance", payload["selection"])
        self.assertNotIn("nuance_status", payload)

    def refused(self, text, frag=None):
        with self.assertRaises(RT.R.RestoreError) as cm:
            RT.R.restore(text, self.tmp)
        if frag:
            self.assertIn(frag, str(cm.exception))

    def test_tampering_is_refused(self):
        t = self.readable("adopt", nuance="adopt")
        self.refused(t.replace("ニュアンス解説：採用", "ニュアンス解説：不採用"))                          # 採否の書換え(コードn8と不一致)
        self.refused(t.replace("Nobody spoke.", "Everybody spoke."))                                       # 本文の改変
        self.refused(t.replace("nobodyのほうが口語的で", "nobodyが"))                                      # 解説の改変/省略
        self.refused("\n".join(l for l in t.split("\n") if not l.startswith("ニュアンス解説") and "【ニュアンス" not in l and "本文の英文" not in l))   # ブロック削除
        self.refused(t.replace("AIF2-", "AIF1-"))                                                           # AIF1で提出(旧形式のコピー)
        self.refused(self.readable("legacy").replace("AIF1-", "AIF2-"))                                     # 仕様マークなしデータにAIF2

    def test_old_aif1_copy_of_nuance_data_is_refused_with_recheck_hint(self):
        stem, pth, d = self.files["adopt"]
        old_d = {k: v for k, v in d.items() if k not in ("nuance_spec", "nuance")}
        old = RT.R.build_readable(stem, old_d, self.st, RT.d6_of_file(pth))                                 # 仕様マーク前のデータで作ったコピー
        self.refused(old, frag="ニュアンス")

    def test_form_logic_blocking_helpers(self):
        js = ("const FL=require(process.argv[1]);const d=JSON.parse(process.argv[2]);"
              "process.stdout.write(JSON.stringify({u:FL.nuanceDecision(d,{}),b0:FL.nuanceBlocked(d,{}),a:FL.nuanceDecision(d,{nuance:'adopt'}),keys:Object.keys(FL).filter(k=>/nuance/i.test(k))}));")
        out = run_node(js, json.dumps(self.files["adopt"][2], ensure_ascii=False))
        self.assertEqual((out["u"], out["b0"], out["a"]), ("undecided", True, "adopt"))
        self.assertIn("nuanceBlocked", out["keys"])
        out2 = run_node("const FL=require(process.argv[1]);const d=JSON.parse(process.argv[2]);process.stdout.write(JSON.stringify([FL.nuanceDecision(d,{}),FL.nuanceBlocked(d,{})]));",
                        json.dumps(self.files["none"][2], ensure_ascii=False))
        self.assertEqual(out2, ["n/a", False])                                                              # 候補なしは回答不要

    def test_pool_conflict_is_alarm_only_and_never_blocks_in_form_logic_spec2(self):
        d = copy.deepcopy(self.files["adopt"][2])
        it = d["phrases"][1]
        d["nuance"]["pool_conflicts"] = [it.get("candidate_id") or it["id"]]
        js = ("const FL=require(process.argv[1]);const d=JSON.parse(process.argv[2]);const t=process.argv[3];"
              "const mk=(c,n)=>({choices:Object.fromEntries([[t,c]]),grammar:{},grammar_zero:false,comment:'',nuance:n});"
              "process.stdout.write(JSON.stringify([FL.nuanceConflicts(d,mk(1,'adopt')),FL.nuanceBlocked(d,mk(1,'adopt')),FL.nuanceBlocked(d,mk(1,'reject')),FL.nuanceBlocked(d,mk(3,'adopt'))]));")
        out = run_node(js, json.dumps(d, ensure_ascii=False), it["term"])
        self.assertEqual(out[0], [it["term"]])
        self.assertEqual(out[1:], [False, False, False])                                                    # 仕様②: 重複(採用+その項目を①②で選ぶ)はアラーム表示のみ=送信/コピーを止めない


class T8_ExporterKeys(unittest.TestCase):
    def setUp(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp2", os.path.join(ROOT, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py"))
        self.exp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.exp)
        self.cands = nt.kp_doc()
        self.cands["candidates_sha256"] = self.exp.doc_sha256(self.cands)

    def conv(self, bundle=None):
        return self.exp.convert(self.cands, slug="s", level="b1b", name="n", family="X", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="", nuance_bundle=bundle)

    def test_without_bundle_there_are_no_nuance_keys(self):
        a = self.conv(None)
        for k in ("nuance", "nuance_spec", "nuance_note_ja"):
            self.assertNotIn(k, a)

    def test_with_bundle_adds_spec_and_nuance_or_note_only(self):
        base = self.conv(None)
        spec = {"version": "nuance_v1", "max_select": 1, "allow_zero": True, "presented": True, "candidate_status": "CANDIDATE"}
        w = self.conv({"nuance_spec": spec, "nuance": NUANCE})
        self.assertEqual(w["nuance"], NUANCE)
        self.assertEqual(w["nuance_spec"], spec)
        self.assertEqual({k: v for k, v in w.items() if k not in ("nuance", "nuance_spec")}, base)         # 他のキーは不変
        n = self.conv({"nuance_spec": dict(spec, presented=False, candidate_status="NO_CANDIDATE"), "nuance_note_ja": "ニュアンス解説の候補はありません"})
        self.assertNotIn("nuance", n)
        self.assertEqual(n["nuance_note_ja"], "ニュアンス解説の候補はありません")


INDEX_HTML = os.path.join(ROOT, "user_test", "selection_form_v3", "index.html")


@unittest.skipUnless(HAVE_NODE, "node が無い")
class T9_FormHtmlUi(unittest.TestCase):
    """index.htmlのニュアンス欄: スクリプトの構文・仕様マークなしで非表示・採用/不採用ラジオの描画・未回答/重複でguardが止める(node上の最小DOM stub)。"""

    @classmethod
    def setUpClass(cls):
        cls.html = open(INDEX_HTML, encoding="utf-8").read()

    def test_static_elements_and_guard_present(self):
        h = self.html
        for needle in ('id="nuanceH"', 'id="nuanceNotice"', 'id="nuances"', "function renderNuance", "FL.nuanceDecision(D,get())==='undecided'", "FL.nuanceConflicts(d,st)", "data-nuance=\"adopt\"", "data-nuance=\"reject\""):
            self.assertIn(needle, h)
        self.assertLess(h.index('id="grammars"'), h.index('id="nuanceH"'))                                 # 文法の直後
        self.assertLess(h.index('id="nuanceH"'), h.index("自由コメント"))                                  # 自由コメントの前
        self.assertIn("renderNuance(d,st);", h)

    def test_inline_script_parses(self):
        body = re.findall(r"<script>(.*?)</script>", self.html, re.S)[-1]
        fd, p = tempfile.mkstemp(suffix=".js")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(body)
            r = subprocess.run(["node", "--check", p], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, r.stderr[-800:])
        finally:
            os.remove(p)

    def run_render(self, d, st):
        fn = re.search(r"function renderNuance\(d,st\)\{.*?\n\}\n", self.html, re.S).group(0)
        js = ("const FL=require(process.argv[1]);const d=JSON.parse(process.argv[2]);const st=JSON.parse(process.argv[3]);"
              "const els={};const $=id=>els[id]||(els[id]={hidden:false,textContent:'',innerHTML:''});"
              "const esc=s=>String(s).replace(/[&<>\"']/g,'_');const saved=[];"
              "const document={querySelectorAll:()=>({forEach:()=>{}})};const save=()=>{},render=()=>{};"
              + fn +
              "renderNuance(d,st);process.stdout.write(JSON.stringify({H:$('nuanceH').hidden,N:$('nuanceNotice').hidden,Nt:$('nuanceNotice').textContent,cnt:$('nuanceCount').textContent,B:$('nuances').innerHTML}));")
        return run_node(js, json.dumps(d, ensure_ascii=False), json.dumps(st, ensure_ascii=False))

    def test_hidden_without_spec_and_rendered_with_candidate(self):
        base = RT.synth_datasets()["fixture_synth__a2"]
        out = self.run_render(base, {})
        self.assertEqual((out["H"], out["N"], out["B"]), (True, True, ""))                                   # 仕様マークなし=従来の画面のまま
        d = nuance_dataset(base)
        out = self.run_render(d, {})
        self.assertFalse(out["H"])
        self.assertEqual(out["cnt"], "未決定")
        self.assertIn("未決定のままでは送信・コピーできません", out["Nt"])
        self.assertIn('data-nuance="adopt"', out["B"])
        self.assertIn('data-nuance="reject"', out["B"])
        self.assertIn("Nobody spoke.", out["B"])
        out = self.run_render(d, {"nuance": "adopt", "nuance_sha": NSHA})
        self.assertEqual(out["cnt"], "採用")
        self.assertIn("checked", out["B"])
        out = self.run_render(d, {"nuance": "adopt", "nuance_sha": "b" * 64})                               # 別の候補に対する旧回答は引き継がない
        self.assertEqual(out["cnt"], "未決定")

    def test_no_candidate_and_failed_technical_notes_are_shown_without_radios(self):
        base = RT.synth_datasets()["fixture_synth__a2"]
        d = nuance_dataset(base, nuance=None)
        d["nuance_note_ja"] = "ニュアンス解説の候補なし（技術失敗: api_error）。本物の0件ではありません。"
        out = self.run_render(d, {})
        self.assertEqual((out["cnt"], out["B"]), ("候補なし", ""))
        self.assertIn("技術失敗", out["Nt"])

    def test_previous_decision_is_default_shown_after_revoke(self):
        base = RT.synth_datasets()["fixture_synth__a2"]
        d = nuance_dataset(base, nuance=dict(NUANCE, previous_decision="adopt"))
        out = self.run_render(d, {})
        self.assertEqual(out["cnt"], "採用")
        self.assertIn("前回の確定は「採用」", out["Nt"])


if __name__ == "__main__":
    unittest.main()
