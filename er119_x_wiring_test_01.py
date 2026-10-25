# -*- coding: utf-8 -*-
"""KP Human Review: Family X runner(er019)配線の単体test。API 0(LLM由来の関数は全てmock、実TTS/実API呼出は0であることをcounterで確認)。
実行: .venv\\Scripts\\python.exe -m unittest er119_x_wiring_test_01 -v
対象: 宣言なし=待機(rc=4)・再実行でもAPI 0・M-4(support再生成なしの再開)・確定後に先へ進む・--kp-review auto(明示引数のみ)・
      未確定/不整合の消費者入口(rc=4/rc=3)・Part 1入力(vocab_confirmed.json)・旧run互換。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

import er003_key_words_gloss_alignment as ga
import er019_family_x_audio_production_runner_01 as runner
import er119_kp_human_review_01 as rv
from er119_test_support_01 import ARTICLE, Env, KpTestCase, jd, jl, wr


def _setup():
    """tmp作業dir(cwd)に er019_output/<slug>/<run>/a2/article.md、out_dirにa2_support_texts.jsonを置く。"""
    work, out = tempfile.mkdtemp(), tempfile.mkdtemp()
    src = f"{work}/er019_output/coffee/r"
    os.makedirs(f"{src}/a2")
    wr(f"{src}/a2/article.md", ARTICLE)
    os.makedirs(f"{out}/a2")
    wr(f"{out}/a2/a2_support_texts.json", "{}")
    import shutil
    repo = os.getcwd()
    for d in ("er003_v1_translator_briefs",):   # prompt templateは相対pathで読まれるため、tmp cwdへ読取専用の写しを置く
        if os.path.isdir(os.path.join(repo, d)):
            shutil.copytree(os.path.join(repo, d), os.path.join(work, d))
    return work, src, out


class XMainBase(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)
        self.work, self.src, self.out = _setup()
        self.addCleanup(lambda: __import__("shutil").rmtree(self.work, ignore_errors=True))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.out, ignore_errors=True))
        self.env = Env(self.out)
        self.env.__enter__()
        self.addCleanup(self.env.__exit__)
        self.tts, self.asm, self.scaf = mock.Mock(), mock.Mock(), mock.Mock(return_value={})
        self.kp_dir = f"{self.out}/a2/key_phrases"

    def main(self, stage, *extra):
        os.chdir(self.work)
        argv = ["x", "--slug", "coffee", "--run", "r", "--out-dir", self.out, "--stage", stage, "--level", "a2", *extra]
        patches = [mock.patch.object(sys, "argv", argv),
                   mock.patch.object(runner, "generate_family_x_a2_segments", self.tts),
                   mock.patch.object(runner, "stage_assemble_family_x_a2", self.asm),
                   mock.patch.object(runner, "assert_production_tts_backend"),
                   mock.patch.object(runner, "ensure_rf_record"),
                   mock.patch.object(runner, "assert_budget_ok"),
                   mock.patch.object(runner, "compute_cost_jpy_so_far", return_value=(0.0, {})),
                   mock.patch.object(runner.plan, "split_family_x_article_text_v2", return_value={"status": "OK", "paragraph_count": 4}),
                   mock.patch.object(runner, "run_family_x_a2_scaffold", self.scaf),
                   mock.patch("er003_v1_en_direct_vfl_01_generate.get_client", return_value=None)]
        rc, buf = None, io.StringIO()
        with contextlib.ExitStack() as es:
            for p in patches:
                es.enter_context(p)
            es.enter_context(contextlib.redirect_stdout(buf))
            try:
                runner.main()
            except SystemExit as e:
                rc = e.code
        return rc, buf.getvalue()


class TestXWaitAndResume(XMainBase):
    def test_no_declaration_waits_rc4_and_downstream_not_run(self):
        rc, out = self.main("scaffold")
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        self.assertEqual(rv.EXIT_CODE_PENDING, 4)
        self.assertIn(rv.PENDING_MARKER, out)
        self.assertIn("kp_human_review_request.md", out)
        self.tts.assert_not_called()
        self.asm.assert_not_called()
        for f in ("keywords_canonicalized.json", "vocab_confirmed.json", "kp_selection_final.json"):   # DefaultOffIsolation: 副作用ファイル0
            self.assertFalse(os.path.exists(f"{self.kp_dir}/{f}"), f)
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)
        # 候補生成の有料呼出(選定1/選定2-V/canon/gloss/QA)のみ。TTS等は0
        self.assertEqual(self.env.n["call1"], 1)
        self.assertEqual(self.env.n["call2"], 1)   # 追加候補(Prompt 2-V)の1 callまで。以降のTTS/後続は0

    def test_rerun_while_pending_makes_no_llm_call_and_does_not_regenerate_support_M4(self):
        self.main("scaffold")
        n = self.env.total_llm_calls()
        rc, out = self.main("scaffold")
        self.assertEqual(rc, 4)
        self.assertEqual(self.env.total_llm_calls(), n, "再実行(候補sha一致)は再選定せずAPI 0")
        self.assertEqual(self.scaf.call_count, 1, "M-4: 有効なreview/候補があればsupport(有料)を再生成しない")

    def test_select_then_rerun_finalizes_and_proceeds(self):
        self.main("scaffold")
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=None, by="human")
        n = self.env.total_llm_calls()
        rc, out = self.main("scaffold")
        self.assertIsNone(rc)
        self.assertTrue(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))
        self.assertEqual(rv.require_final_consistent(self.kp_dir, level="a2")["status"], rv.ST_REVIEWED)
        self.assertEqual(self.scaf.call_count, 1)
        # finalizeでの追加LLM呼出は確定集合のRedundancy QA(M-8)だけ。選定1/2-V/canonは再実行しない
        self.assertEqual(self.env.n["call1"], 1)
        self.assertEqual(self.env.n["canon"], 1)
        self.assertLessEqual(self.env.total_llm_calls() - n, 1)

    def test_kp_review_auto_arg_is_the_only_way_to_auto_adopt(self):
        rc, _ = self.main("scaffold", "--kp-review", "auto", "--kp-review-by", "user", "--kp-review-reason", "不在")
        self.assertIsNone(rc)
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_AUTO)
        decl = jl(os.path.join(self.out, "kp_review_mode.json"))["declarations"][0]
        self.assertEqual(decl["source"], "cli_runner_arg")

    def test_kp_review_auto_requires_by_and_reason(self):
        rc, _ = self.main("scaffold", "--kp-review", "auto")
        self.assertEqual(rc, 2)   # argparse error
        self.assertFalse(os.path.exists(f"{self.kp_dir}/kp_human_review.json"))
        self.assertFalse(os.path.exists(os.path.join(self.out, "kp_review_mode.json")))

    def test_ai_by_without_user_ref_is_rejected(self):
        try:
            rc, _ = self.main("scaffold", "--kp-review", "auto", "--kp-review-by", "Fable", "--kp-review-reason", "r")
        except rv.KpReviewError:
            rc = "raised"
        self.assertNotIn(rc, (None, 4))   # 宣言は拒否され、自動採用に進まない
        self.assertFalse(os.path.exists(os.path.join(self.out, "kp_review_mode.json")))

    def test_wait_arg_writes_no_declaration(self):
        rc, _ = self.main("scaffold", "--kp-review", "wait")
        self.assertEqual(rc, 4)
        self.assertFalse(os.path.exists(os.path.join(self.out, "kp_review_mode.json")))


class TestXConsumerEntryGate(XMainBase):
    def test_tts_stage_while_pending_refuses_with_rc4_and_no_tts(self):
        self.main("scaffold")
        rc, out = self.main("tts")
        self.assertEqual(rc, 4)
        self.assertIn(rv.PENDING_MARKER, out)
        self.tts.assert_not_called()

    def test_tts_stage_with_tampered_final_refuses_with_rc3(self):
        self.main("scaffold", "--kp-review", "auto", "--kp-review-by", "user", "--kp-review-reason", "r")
        p = f"{self.kp_dir}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["candidate_id"] = "p_tampered"
        jd(p, d)
        rc, out = self.main("tts")
        self.assertEqual(rc, 3)
        self.tts.assert_not_called()


class TestXLegacyRunCompat(XMainBase):
    def test_kp_already_generated_ignores_review_dir_but_counts_legacy_artifacts(self):
        self.main("scaffold")
        self.assertEqual(runner._kp_already_generated(self.kp_dir), [])   # review再開経路は『生成済み』ではない
        legacy = tempfile.mkdtemp()
        wr(os.path.join(legacy, "keywords_canonicalized.json"), "{}")
        self.assertEqual(len(runner._kp_already_generated(legacy)), 1)    # reviewの無い旧runは従来どおり1レベル1回


class TestXPart1Input(KpTestCase):
    def test_part1_items_follow_review_vocab_and_fail_closed(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        with self.assertRaises(RuntimeError):   # 候補すら無い(review無し・KP成果物無し)=従来どおりSTOP
            runner._part1_kp_items(self.run_dir)
        self.declare()
        self.assertEqual(self.ensure(env)["state"], "FINALIZED")
        items = runner._part1_kp_items(self.run_dir)
        self.assertEqual(len(items), 5)
        self.assertEqual([i["rank"] for i in items], [1, 2, 3, 4, 5])
        os.remove(f"{self.kp_dir}/vocab_confirmed.json")
        with self.assertRaises(rv.KpReviewInconsistent):
            runner._part1_kp_items(self.run_dir)

    def test_part1_pending_review_raises_not_confirmed(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.assertEqual(self.ensure(env)["state"], "PENDING")
        with self.assertRaises(rv.KpReviewNotConfirmed):
            runner._part1_kp_items(self.run_dir)


if __name__ == "__main__":
    unittest.main()
