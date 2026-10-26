# -*- coding: utf-8 -*-
r"""KP-PHRASE7-WORD5-PRODUCTION-01 委任_02: mock E2E(API 0、LLM由来の関数は全てmock。Opus R-5: 既存mock E2Eの候補生成mock[n_max=8]は12件を通らないため、
7+5のgeneratorを注入して候補12件→HR依頼書→確認/AUTO→finalize→下流整合を通す)。
  - X/Y/Z共通の1配線点(`er119_kp_wiring_01.run_kp_with_review`)を Std(a2)/Adv(b1b) x family(x/y/z) で通す(Zはsrc_fn/person_fnつき)
  - Family Xのrunner本体(`er019...main`)を実際に通す(宣言なし=rc4待機→選択→先へ進む)
  - Family Zのrunner(`er026`のkp stage)へ7+5のdocを注入して通す
実行: .venv\Scripts\python.exe -m unittest er119_kp_p7w5_e2e_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import unittest
from unittest import mock

import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er119_kp_p7w5_prompts_01 as p7w5
import er119_kp_wiring_01 as kw
import er119_x_wiring_test_01 as xw
import er119_z_wiring_test_01 as zw
from er119_test_support_01 import ARTICLE, Env, KpTestCase

PHRASES7 = ["time lag", "pushed prices up", "took a sharp turn", "Before you know it", "stay high", "Retail prices", "raw beans"]
WORDS5 = ["spike", "stock", "insiders", "blends", "increases"]
P7_ITEMS = [{"phrase": p, "reason_ja": f"理由{n}", "word_count": len(p.split())} for n, p in enumerate(PHRASES7, 1)]
W5_ITEMS = [{"phrase": w, "reason_ja": f"単語{n}", "word_count": 1} for n, w in enumerate(WORDS5, 1)]


def _invariants(tc, doc):
    c = doc["candidates"]
    ph = [x for x in c if x["kind"] == "phrase"]
    wd = [x for x in c if x["kind"] == "word"]
    tc.assertLessEqual(len(ph), 7)
    tc.assertLessEqual(len(wd), 5)
    tc.assertLessEqual(len(c), 12)
    for w in wd:
        for p in ph:
            tc.assertFalse(kcand._contains_any(w, p), (w["used_form"], p["used_form"]))


class TestSharedWiringAllFamiliesAndLevels(KpTestCase):
    def _run(self, family, level):
        text = ARTICLE
        kp_dir = self.kp_dir if level == "b1b" else self.kp_dir_a2
        run_dir = self.run_dir
        src_fn = kcand.make_z_src_fn(text, level) if family == "z" else None
        person_fn = (lambda merged: merged) if family == "z" else None
        with Env(self.tmp, call1=P7_ITEMS, call2=W5_ITEMS) as env:
            pend = kw.run_kp_with_review(text=text, kp_dir=kp_dir, run_dir=run_dir, family=family, slug="coffee", level=level, article_id=f"aid_{family}_{level}",
                                         stop_run_dir=run_dir, src_fn=src_fn, person_repair_fn=person_fn, run_hint=run_dir,
                                         redundancy_hook=lambda items, name: {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": None, "attempts_detail": []})
            self.assertEqual(pend["kp_review"]["state"], "PENDING")             # 宣言なし=待機(rc4)
            doc = rv.load_candidates(kp_dir)
            self.assertEqual(len(doc["candidates"]), 12)
            self.assertEqual((env.n["call1"], env.n["call2"]), (1, 1))
            self.assertEqual(doc["prompt_sha256"], {"call1": p7w5.P7_SHA256, "call2": p7w5.W5P_SHA256})
            _invariants(self, doc)
            with open(rv.paths(kp_dir)["request"], encoding="utf-8") as _f:
                md = _f.read()
            self.assertIn("pushed prices up", md)
            # Human選択(Std: KP3件 / Adv: KP3件+vocab5件)→再実行でfinalize
            rv.op_select(kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if level == "b1b" else None), by="human")
            n = env.total_llm_calls()
            res = kw.run_kp_with_review(text=text, kp_dir=kp_dir, run_dir=run_dir, family=family, slug="coffee", level=level, article_id=f"aid_{family}_{level}",
                                        stop_run_dir=run_dir, src_fn=src_fn, person_repair_fn=person_fn, run_hint=run_dir,
                                        redundancy_hook=lambda items, name: {"status": "REDUNDANCY_PASS", "duplicate_pairs": [], "model_id": None, "attempts_detail": []})
            self.assertEqual(res["kp_review"]["state"], "FINALIZED")
            self.assertEqual(env.n["call1"], 1)                                # finalizeで選定を再実行しない(候補生成は1回のみ)
        self.assertEqual(rv.require_final_consistent(kp_dir, level=level)["status"], rv.ST_REVIEWED)
        self.assertGreaterEqual(n, 0)

    def test_x_std(self):
        self._run("x", "a2")

    def test_x_adv(self):
        self._run("x", "b1b")

    def test_y_std(self):
        self._run("y", "a2")

    def test_y_adv(self):
        self._run("y", "b1b")

    def test_z_std(self):
        self._run("z", "a2")

    def test_z_adv(self):
        self._run("z", "b1b")


class TestXRunnerMain75(xw.XMainBase):
    """Family Xのrunner本体を実際に通す: 7+5(P7/W5')で12候補→宣言なしrc4待機→Human選択→再実行で先へ。"""

    def setUp(self):
        super().setUp()
        self.env.__exit__()
        self.env = Env(self.out, call1=P7_ITEMS, call2=W5_ITEMS)
        self.env.__enter__()
        self.addCleanup(self.env.__exit__)       # 差し替えたEnvのpatchを必ず戻す(漏れると他testのwrapperが差し替わったままになる)

    def test_runner_generates_12_candidates_waits_then_finalizes(self):
        rc, out = self.main("scaffold")
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        doc = rv.load_candidates(self.kp_dir)
        self.assertEqual(len(doc["candidates"]), 12)
        self.assertEqual([c["kind"] for c in doc["candidates"]].count("phrase"), 7)
        self.assertEqual([c["kind"] for c in doc["candidates"]].count("word"), 5)
        self.assertEqual((self.env.n["call1"], self.env.n["call2"]), (1, 1))     # 候補生成P7 1回 + W5' 1回のみ。TTS等は0
        self.tts.assert_not_called()
        _invariants(self, doc)
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=None, by="human")
        rc, out = self.main("scaffold")
        self.assertIsNone(rc)
        self.assertEqual(rv.require_final_consistent(self.kp_dir, level="a2")["status"], rv.ST_REVIEWED)


class TestZRunnerHook75(zw.ZBase):
    """Family Zのrunner(kp stage)へ7+5のdoc(フレーズ7+単語5)を注入して通す(mockの候補生成はn_max=8で12件を通らないため)。"""

    def _doc_for(self, lv):
        text = zw.r.canonical_article_text(zw.r._m().w62.rd(zw.r._level_text_path(self.ctx, lv)))
        spans = [s for s in zw.r._MOCK_KP_CANDIDATES if s in text]
        import re as _re
        span_tokens = {t.lower() for sp in spans for t in sp.split()}
        words = []
        for t in _re.findall(r"[A-Za-z]{5,}", text):
            if t.lower() not in span_tokens and t.lower() not in {w.lower() for w in words}:
                words.append(t)
        self.assertGreaterEqual(len(spans), 3)
        self.assertGreaterEqual(len(words), 3)
        items = []
        for i, s in enumerate(spans[:7] + words[:5], 1):
            items.append({"rank": i, "source_span": s, "source_sentence": s, "display_phrase": s, "key_phrase": s, "used_form": s,
                          "japanese_gloss": f"意味{i}", "fulltext_source_ref": "fulltext_exact_v1"})
        new, drop = kcand.make_z_src_fn(text, lv)(items)
        items = [new.get(x["rank"], x) for x in items if x["rank"] not in drop]
        return kcand.candidate_doc_from_items(items, lv, origin_split=min(7, len(spans)))

    def test_kp_stage_with_75_candidate_docs_waits_then_proceeds(self):
        docs = {lv: self._doc_for(lv) for lv in ("b1b", "a2")}
        self.ctx.hooks["kp_generate_fn"] = None

        def hook_for(lv):
            return lambda round_no, ng: {"ok": True, "doc": json.loads(json.dumps(docs[lv]))}
        # runnerはlevelごとにhookを引く: ctx.hooksは共通のため、呼出時のkp_dirで振り分けるadapterを注入する
        calls = []

        def gen(round_no, ng):
            calls.append(round_no)
            lv = "b1b" if len(calls) % 2 == 1 else "a2"
            return hook_for(lv)(round_no, ng)
        self.ctx.hooks["kp_generate_fn"] = gen
        with self.assertRaises(zw.r.FamilyZKpReviewPending):
            zw._quiet(zw.r.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            c = rv.load_candidates(self.src[lv])
            self.assertGreaterEqual(len(c["candidates"]), 6)
            self.assertLessEqual(len(c["candidates"]), 12)
            _invariants(self, c)
            self.assertIn("word", [x["kind"] for x in c["candidates"]])


if __name__ == "__main__":
    unittest.main()
