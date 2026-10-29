# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C: Z Production runner の実stage経路(mock・API 0)でのニュアンス解説の配線test。
Y版(er134_nuance_y_mock_e2e_test_01.py)と同じ契約を、Zの実コード(stage_kp -> N0/N1 -> rc=4 -> stage_pages -> _verify_part2_outputs)で確認する。runner本体は無変更でhooksだけ注入。
  新規run: spec発行・両levelでN1・KP/文法/ニュアンスが1回の待機・pages入口で未確定=rc=4・CLI確定(Adv採用/Std不採用)後にpages: 採用levelの節だけにコーナー・節単位一致 /
  resumeでAPI 0・同一HTML / 既存run(KP reviewが先)=LEGACY(生成0・副作用ファイル0・コーナー0) / AUTO採用=生成0 / 生成API失敗=非ブロッキング。
実行: .venv/Scripts/python.exe -m pytest er134_nuance_z_mock_e2e_test_01.py -q
(注: Zのmock E2Eは tracked seed file の改行コード[CRLF/LF]に依存する既存の環境差で失敗することがある=FAMILY_Z_SEED_SHA_MISMATCH。Windows worktreeでは seed を LF にしてから実行)"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import re
import unittest

import er026_family_z_fiction_production_runner_01 as r
import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er119_z_wiring_test_01 as zw
import er120_part2_grammar_production_01 as g
import er128_kp_confirmed_content_01 as cc
import er134_nuance_explanation_01 as nx
import er134_nuance_explanation_01_test_01 as nt
from er119_test_support_01 import jl, rd, wr

NUANCE_FILES = ("nuance_spec.json", "nuance_candidate.json", "nuance_failed.json", "nuance_result.json", "confirmed_nuance.json", "nuance_human_review_request.md")


class Hooks:
    def __init__(self, ctx):
        self.ctx, self.gen_n, self.judge_n = ctx, 0, 0

    def _sentence_in(self, prompt):
        for lv in ("b1b", "a2"):
            paras, _ = r._part2_inputs(self.ctx, lv)
            for p in paras:
                for s in nx._sents(p):
                    if 30 <= len(s) <= 140 and s in prompt:
                        return s
        raise AssertionError("promptに引用できる本文の文が見つかりません")

    def gen(self, prompt):
        self.gen_n += 1
        return nt.gen_json(expression="maybe vs perhaps", quote=self._sentence_in(prompt)), nt.MODEL, {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}, f"g{self.gen_n}"

    def judge(self, prompt):
        self.judge_n += 1
        ids = re.findall(r"(?m)^([KG]\d+)\. ", prompt)
        body = json.dumps({"items": [{"id": i, "same": False} for i in ids], "closest": {"id": ids[0], "why": "別焦点"}}, ensure_ascii=False)
        return body, nt.MODEL, {"input_tokens": 800, "output_tokens": 200, "cached_input_tokens": 0}, f"j{self.judge_n}"

    def install(self):
        self.ctx.hooks["nuance_call_fn"], self.ctx.hooks["nuance_judge_fn"] = self.gen, self.judge
        return self


class ZNuance(zw.ZBase):
    def setUp(self):
        super().setUp()
        self.uref = os.path.join(self.tmp, "user_ref.md")
        wr(self.uref, "ユーザー発言原文(test fixture)\n")

    def sd(self, lv):
        return r._part2_dir(self.ctx, lv)

    def pend(self):
        with self.assertRaises(r.FamilyZKpReviewPending) as cm:
            zw._quiet(r.run_stage, self.ctx, "kp")
        return cm.exception

    def human_all(self):
        for lv in ("b1b", "a2"):
            cands, review = rv.load_candidates(self.src[lv]), rv.load_review(self.src[lv])
            sel = rv.auto_select(cands, level=lv, kind=rv.KIND_KP, ng_entries=[], std_part1=bool(review.get("std_part1")))
            rank = {c["candidate_id"]: c["ai_rank"] for c in cands["candidates"]}
            rv.op_select(self.src[lv], kp_ranks=[rank[i] for i in sel["kp"]], vocab_ranks=([rank[i] for i in sel["vocab"]] if rv.vocab_enabled(lv, review) else None), by="human")
            sd = self.sd(lv)
            gr.op_decide(sd, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")

    def rest(self):
        zw._quiet(r.run_stages, self.ctx, [s for s in r.E2E_STAGES if s not in zw.PRE and s not in ("kp", "page_verify", "pages")])

    def sections(self, index):
        advi, stdi = index.index("id='adv'"), index.index("id='std'")
        return (index[advi:stdi], index[stdi:]) if advi < stdi else (index[advi:], index[stdi:advi])


class T1_HrPath(ZNuance):
    def test_new_run_wait_pages_rc4_cli_select_and_per_section_display(self):
        hk = Hooks(self.ctx).install()
        exc = self.pend()
        self.assertEqual(sorted(p.get("kind") or "kp" for p in exc.pending), ["grammar", "grammar", "kp", "kp", "nuance", "nuance"])   # KP・文法・ニュアンス解説が1回の待機
        for lv in ("b1b", "a2"):
            self.assertTrue(os.path.exists(f"{self.sd(lv)}/nuance_spec.json"), lv)
            doc = jl(f"{self.sd(lv)}/nuance_candidate.json")
            self.assertEqual((doc["status"], doc["candidate"]["overlap_check"]["verdict"]), ("CANDIDATE", "pass"))
        self.assertEqual((hk.gen_n, hk.judge_n), (2, 2))
        self.pend()
        self.assertEqual((hk.gen_n, hk.judge_n), (2, 2))                                  # 待機中の再起動はAPI 0
        self.human_all()
        zw._quiet(r.run_stage, self.ctx, "kp")                                            # 確定(ニュアンス未決定でもkpは進む)
        self.rest()
        with self.assertRaises(r.FamilyZKpReviewPending) as cm:                           # ページ入口: 未確定=rc=4
            zw._quiet(r.run_stage, self.ctx, "pages")
        self.assertEqual({p["kind"] for p in cm.exception.pending}, {"nuance"})
        self.assertFalse(os.path.exists(f"{self.ctx.pages_dir}/index.html"))
        shas = {lv: jl(f"{self.sd(lv)}/nuance_candidate.json")["candidate"]["candidate_sha256"] for lv in ("b1b", "a2")}
        self.assertEqual(cc.cmd_nuance_select(self.ctx.out_dir, "b1b", "adopt", shas["b1b"], "human", self.uref)["nuance"], "adopted")
        self.assertEqual(cc.cmd_nuance_select(self.ctx.out_dir, "a2", "reject", shas["a2"], "human", self.uref)["nuance"], "rejected")
        zw._quiet(r.run_stages, self.ctx, ["pages", "page_verify"])
        index = rd(f"{self.ctx.pages_dir}/index.html")
        sec_adv, sec_std = self.sections(index)
        self.assertEqual((g.count_nuance_blocks(sec_adv), g.count_nuance_blocks(sec_std)), (1, 0))   # 採用したAdvancedの節だけに1個。Standardは見出しも空枠も無い
        self.assertEqual(g.count_empty_study_sections(index), 0)
        pv = r._verify_part2_outputs(self.ctx)
        self.assertEqual((pv["b1b"]["nuance_blocks"], pv["a2"]["nuance_blocks"]), (1, 0))
        for fn in ("standard.html", "advanced.html"):
            self.assertNotIn(g.NUANCE_HEADING, rd(f"{self.ctx.pages_dir}/{fn}"))        # 開発確認用の個別ページには出さない
        self.assertEqual(jl(f"{self.sd('b1b')}/nuance_result.json")["status"], "ADOPTED")
        self.assertEqual(jl(f"{self.sd('a2')}/nuance_result.json")["status"], "REJECTED")
        # resume: 同一HTML・採否保持・API 0
        before = (hk.gen_n, hk.judge_n, open(f"{self.sd('b1b')}/nuance_result.json", "rb").read())
        zw._quiet(r.run_stages, self.ctx, ["kp", "pages", "page_verify"])
        self.assertEqual((hk.gen_n, hk.judge_n, open(f"{self.sd('b1b')}/nuance_result.json", "rb").read()), before)
        self.assertEqual(rd(f"{self.ctx.pages_dir}/index.html"), index)


class T2_LegacyAutoFailure(ZNuance):
    def test_existing_run_is_legacy_even_when_hooks_are_present(self):
        self.pend()                                                                       # hooks無し(mock)=N0/N1なし=従来のrun
        for lv in ("b1b", "a2"):
            self.assertFalse(any(os.path.exists(f"{self.sd(lv)}/{n}") for n in NUANCE_FILES))
        hk = Hooks(self.ctx).install()                                                    # 後からhooksが有っても、KP reviewは既存=遡及しない
        self.human_all()
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.rest()
        zw._quiet(r.run_stages, self.ctx, ["pages", "page_verify"])
        self.assertEqual((hk.gen_n, hk.judge_n), (0, 0))
        for lv in ("b1b", "a2"):
            self.assertFalse(any(os.path.exists(f"{self.sd(lv)}/{n}") for n in NUANCE_FILES), lv)
        index = rd(f"{self.ctx.pages_dir}/index.html")
        self.assertEqual(g.count_nuance_blocks(index), 0)
        self.assertNotIn(g.NUANCE_HEADING, index)

    def test_auto_adopted_run_generates_nothing_and_pages_complete_without_corner(self):
        hk = Hooks(self.ctx).install()
        self.declare()
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.rest()
        zw._quiet(r.run_stages, self.ctx, ["pages", "page_verify"])
        self.assertEqual(hk.gen_n, 0)
        for lv in ("b1b", "a2"):
            self.assertEqual(jl(f"{self.sd(lv)}/nuance_candidate.json")["no_candidate_reason"], nx.R_AUTO_ADOPTED)
            self.assertEqual(jl(f"{self.sd(lv)}/nuance_result.json")["status"], "NONE")
        index = rd(f"{self.ctx.pages_dir}/index.html")
        self.assertEqual(g.count_nuance_blocks(index), 0)
        self.assertEqual(g.count_empty_study_sections(index), 0)

    def test_generation_api_failure_is_non_blocking_and_pages_complete_without_corner(self):
        hk = Hooks(self.ctx)

        def down(prompt):
            hk.gen_n += 1
            raise ConnectionError("API down (test)")
        self.ctx.hooks["nuance_call_fn"], self.ctx.hooks["nuance_judge_fn"] = down, hk.judge
        exc = self.pend()
        self.assertEqual(sorted({p.get("kind") or "kp" for p in exc.pending}), ["grammar", "kp"])   # 技術失敗にはHR待機itemを作らない
        self.human_all()
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.rest()
        zw._quiet(r.run_stages, self.ctx, ["pages", "page_verify"])                      # ページ生成が止まらず『ニュアンス無し』で完結
        self.assertEqual(jl(f"{self.sd('b1b')}/nuance_result.json")["reason"], "failed_technical:api_error")
        self.assertEqual(g.count_nuance_blocks(rd(f"{self.ctx.pages_dir}/index.html")), 0)


if __name__ == "__main__":
    unittest.main()
