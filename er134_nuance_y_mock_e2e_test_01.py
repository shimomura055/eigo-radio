# -*- coding: utf-8 -*-
"""NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_02C: Y Production runner の実stage経路(mock・API 0・実client生成/network遮断)でのニュアンス解説の配線test。

`r.run_stages` の実コード(stage_kp -> N0/N1 -> HR待機rc=4 -> resume -> pages -> page_verify)を、nuance hooksだけ注入して通す(runner本体・共通関数は無変更)。
  * 新規run: KP review作成と同時にspec発行・両levelでN1(生成1+判定1)・待機itemがKP/文法と同じ統合待機(rc=4)に載る・resumeはAPI 0
  * HR未完了でpages=rc=4(ISSUE)・CLI nuance-select で Adv=採用/Std=不採用 を確定 -> pages: 採用levelの節だけにコーナー(1個)・page_verify節単位一致
  * ページ再構築(resume)で同一HTML・採否保持・hooks再呼出0
  * 既存run(KP reviewが先にある=LEGACY): hooksがあっても生成0・nuance関連ファイル0・コーナー0(遡及なし)
  * AUTO採用(不在宣言)run: 生成0・コーナー0・ページ完結
実行: .venv/Scripts/python.exe -m pytest er134_nuance_y_mock_e2e_test_01.py -q
"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import re
import shutil
import tempfile
import unittest

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er120_part2_grammar_production_01 as g
import er121_family_y_runner_01 as r
import er128_kp_confirmed_content_01 as cc
import er134_nuance_explanation_01 as nx
import er134_nuance_explanation_01_test_01 as nt
from er121_family_y_runner_01_test_01 import setUpModule, tearDownModule, _ctx, _quiet, _declare, _kinds, _calls  # noqa: F401  (遮断harness: 実client生成/networkを例外化)
from er119_test_support_01 import wr

NUANCE_FILES = ("nuance_spec.json", "nuance_candidate.json", "nuance_failed.json", "nuance_result.json", "confirmed_nuance.json", "nuance_human_review_request.md")


class Hooks:
    """mockのgenerate/judge hook。prompt中の本文から逐語の1文を引用し、判定は全件same=false。呼出回数を数える。"""

    def __init__(self, ctx):
        self.ctx = ctx
        self.gen_n = 0
        self.judge_n = 0

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
        q = self._sentence_in(prompt)
        return nt.gen_json(expression="maybe vs perhaps", quote=q), nt.MODEL, {"input_tokens": 1000, "output_tokens": 500, "cached_input_tokens": 0}, f"resp_g{self.gen_n}"

    def judge(self, prompt):
        self.judge_n += 1
        ids = re.findall(r"(?m)^([KG]\d+)\. ", prompt)
        body = json.dumps({"items": [{"id": i, "same": False} for i in ids], "closest": {"id": ids[0], "why": "別焦点"}}, ensure_ascii=False)
        return body, nt.MODEL, {"input_tokens": 800, "output_tokens": 200, "cached_input_tokens": 0}, f"resp_j{self.judge_n}"

    def install(self):
        self.ctx.hooks["nuance_call_fn"] = self.gen
        self.ctx.hooks["nuance_judge_fn"] = self.judge
        return self


class YBase(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="y_nuance_")
        self.addCleanup(shutil.rmtree, self.root, True)
        self.uref = os.path.join(self.root, "user_ref.md")
        os.makedirs(self.root, exist_ok=True)
        wr(self.uref, "ユーザー発言原文(test fixture)\n")

    def upto_support(self, ctx):
        with _quiet():
            r.run_stages(ctx, ["seed_check", "text", "translate", "support"])

    def sd(self, ctx, lv):
        return r._part2_dir(ctx, lv)

    def human_kp(self, ctx, lv):
        src = r._kp_src_dir(ctx, lv)
        cands, review = rv.load_candidates(src), rv.load_review(src)
        sel = rv.auto_select(cands, level=lv, kind=rv.KIND_KP, ng_entries=[], std_part1=bool(review.get("std_part1")))
        rank = {c["candidate_id"]: c["ai_rank"] for c in cands["candidates"]}
        rv.op_select(src, kp_ranks=[rank[i] for i in sel["kp"]], vocab_ranks=([rank[i] for i in sel["vocab"]] if rv.vocab_enabled(lv, review) else None), by="human")

    def decide_grammar(self, ctx, lv):
        sd = self.sd(ctx, lv)
        doc = gr.load_candidates(sd)
        gr.op_decide(sd, choice="top1", candidates_sha256=doc["candidates_sha256"], by="test-human", accept_ai=True)

    def index_html(self, ctx):
        with open(f"{ctx.out_dir}/pages/index.html", encoding="utf-8") as f:
            return f.read()


class T1_HrPath(YBase):
    def test_new_run_n0_n1_wait_resume_pages_rc4_cli_select_and_per_section_display(self):
        ctx = _ctx(self.root)
        hk = Hooks(ctx).install()
        self.upto_support(ctx)
        with self.assertRaises(r.YKpReviewPending) as cm:
            with _quiet():
                r.run_stages(ctx, ["kp"])
        kinds = sorted(p.get("kind") or "kp" for p in cm.exception.pending)
        self.assertEqual(kinds, ["grammar", "grammar", "kp", "kp", "nuance", "nuance"])           # KP・文法・ニュアンス解説が同じ待機点(rc=4は1回)
        for lv in ("b1b", "a2"):
            sd = self.sd(ctx, lv)
            self.assertTrue(os.path.exists(f"{sd}/nuance_spec.json"), lv)                          # N0: 新規KP reviewと同時に発行
            doc = json.load(open(f"{sd}/nuance_candidate.json", encoding="utf-8"))
            self.assertEqual((doc["status"], doc["level_key"]), ("CANDIDATE", lv))
            self.assertEqual(doc["candidate"]["overlap_check"]["verdict"], "pass")                 # HR提示前に重複判定済み(KP/Word)
        self.assertEqual((hk.gen_n, hk.judge_n), (2, 2))                                           # 両level: 生成1+独立判定1
        n_before = _calls(ctx)
        with self.assertRaises(r.YKpReviewPending):
            with _quiet():
                r.run_stages(ctx, ["kp"])                                                          # 待機中の再起動
        self.assertEqual((hk.gen_n, hk.judge_n), (2, 2))                                           # resumeはAPI 0(候補の再利用)
        self.assertEqual(_calls(ctx), n_before)
        # HR(KP・文法)を済ませる。ニュアンスは未決定のまま
        for lv in ("b1b", "a2"):
            self.human_kp(ctx, lv)
            self.decide_grammar(ctx, lv)
        with _quiet():
            r.run_stages(ctx, ["kp"])                                                              # KP/文法の確定。ニュアンス未決定でもkp stageは進む(TTSに音声は不要=R-3)
        self.assertEqual((hk.gen_n, hk.judge_n), (2, 2))
        with _quiet():
            r.run_stages(ctx, ["tts_b1b", "tts_a2", "gate", "assemble"])
        # ページ入口: 未確定=rc=4(ISSUE)。結果ファイルもページも作らない
        with self.assertRaises(r.YKpReviewPending) as cm2:
            with _quiet():
                r.run_stages(ctx, ["pages"])
        self.assertEqual({p["kind"] for p in cm2.exception.pending}, {"nuance"})
        self.assertFalse(os.path.exists(f"{ctx.out_dir}/pages/index.html"))
        self.assertFalse(os.path.exists(f"{self.sd(ctx, 'b1b')}/nuance_result.json"))
        # CLI: Advanced=採用 / Standard=不採用
        shas = {lv: json.load(open(f"{self.sd(ctx, lv)}/nuance_candidate.json", encoding="utf-8"))["candidate"]["candidate_sha256"] for lv in ("b1b", "a2")}
        out = cc.cmd_nuance_select(ctx.out_dir, "b1b", "adopt", shas["b1b"], "human", self.uref)
        self.assertEqual(out["nuance"], "adopted")
        out = cc.cmd_nuance_select(ctx.out_dir, "a2", "reject", shas["a2"], "human", self.uref)
        self.assertEqual(out["nuance"], "rejected")
        with _quiet():
            r.run_stages(ctx, ["pages", "page_verify"])
        html = self.index_html(ctx)
        self.assertEqual(g.count_nuance_blocks(html), 1)                                           # 採用したAdvancedの節だけに1個
        self.assertEqual(g.count_empty_study_sections(html), 0)
        pv = json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))
        self.assertTrue(pv["ok"])
        self.assertEqual({lv: pv["part2_verified"][lv]["nuance_blocks"] for lv in ("b1b", "a2")}, {"b1b": 1, "a2": 0})   # 節単位の一致(M-7)
        res_a = json.load(open(f"{self.sd(ctx, 'b1b')}/nuance_result.json", encoding="utf-8"))
        res_s = json.load(open(f"{self.sd(ctx, 'a2')}/nuance_result.json", encoding="utf-8"))
        self.assertEqual((res_a["status"], res_s["status"]), ("ADOPTED", "REJECTED"))
        self.assertIn(res_a["candidate"]["expression"], html)
        # resume(ページ再構築)で同一HTML・採否保持・API 0
        before_calls, before_bytes = (_calls(ctx), hk.gen_n, hk.judge_n), open(f"{self.sd(ctx, 'b1b')}/nuance_result.json", "rb").read()
        with _quiet():
            r.run_stages(ctx, ["kp", "pages", "page_verify"])
        self.assertEqual((_calls(ctx), hk.gen_n, hk.judge_n), before_calls)
        self.assertEqual(self.index_html(ctx), html)
        self.assertEqual(open(f"{self.sd(ctx, 'b1b')}/nuance_result.json", "rb").read(), before_bytes)


class T2_LegacyAndAuto(YBase):
    def test_existing_run_is_legacy_even_when_hooks_are_present(self):
        ctx = _ctx(self.root)
        self.upto_support(ctx)
        with self.assertRaises(r.YKpReviewPending):
            with _quiet():
                r.run_stages(ctx, ["kp"])                                                          # hooks無し(mock)=N0/N1は実行されない=従来のrun
        for lv in ("b1b", "a2"):
            self.assertFalse(any(os.path.exists(f"{self.sd(ctx, lv)}/{n}") for n in NUANCE_FILES))
        hk = Hooks(ctx).install()                                                                  # 後からhooksが有っても、KP reviewは既存=遡及しない
        for lv in ("b1b", "a2"):
            self.human_kp(ctx, lv)
            self.decide_grammar(ctx, lv)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        self.assertEqual((hk.gen_n, hk.judge_n), (0, 0))
        for lv in ("b1b", "a2"):
            self.assertFalse(any(os.path.exists(f"{self.sd(ctx, lv)}/{n}") for n in NUANCE_FILES), lv)   # 副作用ファイル0
        html = self.index_html(ctx)
        self.assertEqual(g.count_nuance_blocks(html), 0)
        self.assertNotIn(g.NUANCE_HEADING, html)
        self.assertTrue(json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))["ok"])

    def test_auto_adopted_run_generates_nothing_and_page_completes_without_corner(self):
        ctx = _ctx(self.root)
        hk = Hooks(ctx).install()
        self.upto_support(ctx)
        _declare(ctx)                                                                              # 不在宣言=人間の採否が無い
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])
        self.assertEqual(hk.gen_n, 0)                                                              # AUTO採用はニュアンスを生成しない(費用0)
        for lv in ("b1b", "a2"):
            doc = json.load(open(f"{self.sd(ctx, lv)}/nuance_candidate.json", encoding="utf-8"))
            self.assertEqual((doc["status"], doc["no_candidate_reason"]), ("NO_CANDIDATE", nx.R_AUTO_ADOPTED))
            self.assertEqual(json.load(open(f"{self.sd(ctx, lv)}/nuance_result.json", encoding="utf-8"))["status"], "NONE")
        html = self.index_html(ctx)
        self.assertEqual(g.count_nuance_blocks(html), 0)
        self.assertEqual(g.count_empty_study_sections(html), 0)
        pv = json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))
        self.assertTrue(pv["ok"])
        self.assertEqual({lv: pv["part2_verified"][lv]["nuance_blocks"] for lv in ("b1b", "a2")}, {"b1b": 0, "a2": 0})

    def test_generation_api_failure_is_non_blocking_and_pages_complete_without_corner(self):
        ctx = _ctx(self.root)
        hk = Hooks(ctx)

        def down(prompt):
            hk.gen_n += 1
            raise ConnectionError("API down (test)")
        ctx.hooks["nuance_call_fn"] = down
        ctx.hooks["nuance_judge_fn"] = hk.judge
        self.upto_support(ctx)
        with self.assertRaises(r.YKpReviewPending) as cm:
            with _quiet():
                r.run_stages(ctx, ["kp"])
        self.assertEqual(sorted({p.get("kind") or "kp" for p in cm.exception.pending}), ["grammar", "kp"])   # 候補なし(技術失敗)にはHR待機itemを作らない
        for lv in ("b1b", "a2"):
            self.assertEqual(json.load(open(f"{self.sd(ctx, lv)}/nuance_candidate.json", encoding="utf-8"))["status"], "FAILED_TECHNICAL")
            self.human_kp(ctx, lv)
            self.decide_grammar(ctx, lv)
        with _quiet():
            r.run_stages(ctx, ["kp", "tts_b1b", "tts_a2", "gate", "assemble", "pages", "page_verify"])   # ページ生成が止まらず『ニュアンス無し』で完結
        html = self.index_html(ctx)
        self.assertEqual(g.count_nuance_blocks(html), 0)
        self.assertEqual(json.load(open(f"{self.sd(ctx, 'b1b')}/nuance_result.json", encoding="utf-8"))["reason"], "failed_technical:api_error")
        self.assertTrue(json.load(open(f"{ctx.out_dir}/page_verify_local.json", encoding="utf-8"))["ok"])


if __name__ == "__main__":
    unittest.main()
