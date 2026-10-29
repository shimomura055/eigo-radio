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
from er119_test_support_01 import legacy_unmarked_class  # noqa: E402  (旧マーク無し記事の再現。SLOT-23 委任_05M)

BAD_EXPLAIN = lambda prompt: ("壊れた出力(ITEM区切りなし)", pm.MODEL, {"input_tokens": 1, "output_tokens": 1, "cached_input_tokens": 0}, "bad")  # noqa: E731


def _decide_top1(study_dir, by="human"):
    return gr.op_decide(study_dir, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(study_dir)["candidates_sha256"], by=by)


def _accept_translation_issue(study_dir, by="human"):
    """Part 1訳とStep B訳の食い違いISSUE(O-1)を、ユーザー了承として記録する(実運用の解消手段(b)。mock訳は必ずPart 1訳と異なるため、X統合testで通す)。"""
    issue = json.loads(open(f"{study_dir}/grammar_translation_issue.json", encoding="utf-8").read())
    return gr.op_accept_translation_diff(study_dir, ids=[i["candidate_id"] for i in issue["issues"]], by=by, user_ref="test:了承", reason="test fixture(mock訳はPart 1訳と異なる)")


def _decide_pick(study_dir, ids_idx, by="human"):
    """pick(候補のrank順の位置を指定)。1件採用(Top1/Top2のどちらか)と、2件指定の拒否(文法選定仕様 2026-10-27: 原則1件・2件同時選択禁止)の両用。"""
    doc = gr.load_candidates(study_dir)
    ids = [doc["candidates"][i]["candidate_id"] for i in ids_idx]
    return gr.op_decide(study_dir, choice="pick", ids=ids, reason="pick(test)", candidates_sha256=doc["candidates_sha256"], by=by)


# ============================================================
# Z
# ============================================================
@legacy_unmarked_class
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
        for lv in ("b1b", "a2"):
            _decide_top1(r._part2_dir(self.ctx, lv))
        zw._quiet(r.run_stage, self.ctx, "kp")

    def test_wait_is_one_unified_request_with_pregen_before_wait_and_no_part1(self):
        exc = self._pend()
        kinds = [p.get("kind") for p in exc.pending]
        self.assertEqual(kinds.count("grammar"), 2)        # 全level化: Adv/Stdの文法が同じ1回の待機に載る
        self.assertEqual(self.extract_calls(), 2)          # Step A''は確認前に両levelで1回ずつ
        self.assertGreater(self.explain_calls(), 0)        # 全候補の解説は確認前に事前生成(解説全文を見せてから選ばせる)。Step Bの唯一の呼出点=pregen
        self.assertEqual(self._kind_calls("kp_part1"), 0)  # Part 1は確認前に呼ばない
        import er119_kp_wiring_01 as kpw   # runner main()が出すbanner(統合依頼書も書く)
        banner = kpw.pending_banner(exc.pending, restart_command="py x --stage kp", run_dir=self.ctx.out_dir)
        self.assertEqual(banner.count(rv.PENDING_MARKER), 1)                  # 待機表示は1回
        self.assertTrue(os.path.exists(f"{self.ctx.out_dir}/review_request.md"))
        txt = rd(f"{self.ctx.out_dir}/review_request.md")
        self.assertIn("文法", txt)
        self.assertIn("KP", txt)
        for lv in ("b1b", "a2"):
            self.assertFalse(os.path.exists(f"{r._part2_dir(self.ctx, lv)}/{g2.RESULT_FILENAME}"))
        # 再実行(待機中)はAPI 0(抽出も解説も再生成しない)
        n = (self.extract_calls(), self.explain_calls(), self.kp_calls())
        self._pend()
        self.assertEqual((self.extract_calls(), self.explain_calls(), self.kp_calls()), n)

    def test_resume_finalizes_both_levels_with_llm_zero_and_reuse_is_api0(self):
        self._pend()
        n_expl = self.explain_calls()
        self._finish()
        self.assertEqual(self.extract_calls(), 2)          # 再開でStep A''を再実行しない
        self.assertEqual(self.explain_calls(), n_expl)     # 確定後のfinalizeはLLM 0(事前生成の再利用)
        for lv in ("b1b", "a2"):
            self.assertTrue(os.path.exists(f"{r._part2_dir(self.ctx, lv)}/{g2.RESULT_FILENAME}"), lv)
        prov = r._prov(self.ctx)
        for name in ("part2_b1b", "part2_cand_b1b", "part2_a2", "part2_cand_a2"):
            self.assertIsNotNone(prov.stage_entry(name), name)
        zw._quiet(r.run_stage, self.ctx, "kp")             # 再実行
        self.assertEqual((self.extract_calls(), self.explain_calls()), (2, n_expl))

    def test_pregen_failure_stops_with_resume_command_then_recovers_without_reextract(self):
        good = self.ctx.hooks["part2_explain_call_fn"]
        self.ctx.hooks["part2_explain_call_fn"] = BAD_EXPLAIN
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            zw._quiet(r.run_stage, self.ctx, "kp")
        msg = str(cm.exception)
        self.assertEqual(msg.count("`--stage kp` を同じまま再実行"), 1, msg)         # 案内は1つだけ(--regenerate-stageを案内しない)
        self.assertNotIn("`--regenerate-stage part2", msg)
        sd = r._part2_dir(self.ctx, "b1b")
        self.assertTrue(os.path.exists(f"{sd}/{g2.FAILED_FILENAME}"))
        self.assertEqual(jl(f"{sd}/{g2.FAILED_FILENAME}")["stage"], "part2_expl_b1b")
        self.assertFalse(os.path.exists(f"{sd}/{g2.RESULT_FILENAME}"))             # 空欄/部分成果物で続行しない
        self.ctx.hooks["part2_explain_call_fn"] = good
        self._pend()                                                                # 回復: 同じコマンド(KP待機まで進む)
        self.assertEqual(self.extract_calls(), 2)                                   # 回復でも再抽出しない(Adv1+Std1)
        self.assertFalse(os.path.exists(f"{sd}/{g2.FAILED_FILENAME}"))
        self.assertTrue(os.path.exists(f"{sd}/{g2.FAILED_FILENAME.replace('.json', '.resolved.json')}"))

    def test_posthoc_selection_change_requires_refinalize_without_reextract_or_llm(self):
        self._pend()
        self._finish()
        n_expl = self.explain_calls()
        sd = r._part2_dir(self.ctx, "b1b")
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
        self.assertEqual((self.extract_calls(), self.explain_calls()), (2, n_expl))   # 事前生成済みの解説を使う=追加のLLM 0
        self.assertEqual([i["selection"]["candidate_id"] for i in g2.result_items(jl(f"{sd}/{g2.RESULT_FILENAME}"))], [doc["candidates"][1]["candidate_id"]])

    def test_consumer_entries_fail_closed(self):
        self._pend()
        with self.assertRaises((r.FamilyZKpReviewPending, r.FamilyZE2EStop)):
            r.load_level_inputs(self.ctx, "b1b")             # 未確定のままTTS入力へ進めない
        self._finish()
        r.load_level_inputs(self.ctx, "b1b")                 # 確定後は通る
        r.load_level_inputs(self.ctx, "a2")                  # Standardの文法はTTS/Gate/Assemblyの前提ではない(ページ専用)
        res = f"{r._part2_dir(self.ctx, 'b1b')}/{g2.RESULT_FILENAME}"
        good = rd(res)
        os.remove(res)
        with self.assertRaises((r.FamilyZE2EStop, g2.Part2Error)):
            r.load_level_inputs(self.ctx, "b1b")             # 結果欠落でSTOP(M-2)
        d = json.loads(good)
        it0 = d["items"][0]["selection"] if d.get("schema") == g2.SCHEMA_RESULT_V2 else d["selection"]
        it0["sentence"] = it0["sentence"] + " x"
        with open(res, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False))
        with self.assertRaises((r.FamilyZE2EStop, g2.Part2Error)):
            r.load_level_inputs(self.ctx, "b1b")             # 改変/古い結果でSTOP

    def _run_rest(self):
        rest = [s for s in r.E2E_STAGES if s not in zw.PRE and s not in ("kp", "page_verify")]
        zw._quiet(r.run_stages, self.ctx, rest)

    def _sections(self, index):
        advi, stdi = index.index("id='adv'"), index.index("id='std'")
        return (index[advi:stdi], index[stdi:]) if advi < stdi else (index[advi:], index[stdi:advi])

    def test_pages_show_part2_in_both_level_sections_and_page_verify_checks_each_section(self):
        self._pend()
        self._finish()
        self._run_rest()
        index = rd(f"{self.ctx.pages_dir}/index.html")
        marker = "Grammar &amp; Sentence Structure"
        self.assertEqual(index.count("<section class='study'>"), 3)        # Adv: Part 1+Part 2 / Std: Part 2
        self.assertEqual(index.count(marker), 2)
        sec_adv, sec_std = self._sections(index)
        self.assertEqual(sec_adv.count(marker), 1)
        self.assertEqual(sec_std.count(marker), 1)
        self.assertLess(sec_adv.index("Vocabulary &amp; Expressions"), sec_adv.index(marker))   # Advanced: Part 1の直後
        self.assertNotIn("Vocabulary", sec_std)                                                 # StandardにPart 1は無い
        for fn in ("standard.html", "advanced.html"):
            self.assertNotIn(marker, rd(f"{self.ctx.pages_dir}/{fn}"))                         # 開発確認用の個別ページには出さない
        r._verify_part2_outputs(self.ctx)
        pv = r._verify_part2_outputs(self.ctx)
        self.assertEqual((pv["b1b"]["part2_blocks"], pv["a2"]["part2_blocks"]), (1, 1))
        # R-3: ブロックの見出しを改変すると(節単位の)描画不一致でSTOP
        with open(f"{self.ctx.pages_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(index.replace(marker, "Grammar &amp; Something Else"))
        with self.assertRaises(Exception):
            r._verify_part2_outputs(self.ctx)

    def test_page_verify_detects_std_section_missing_or_swapped_block(self):
        self._pend()
        self._finish()
        self._run_rest()
        index = rd(f"{self.ctx.pages_dir}/index.html")
        sec_adv, sec_std = self._sections(index)
        # (a) Std節からPart 2ブロックだけ消す(欠落)
        a_at = sec_std.index("<section class='study'>")
        a_end = sec_std.index("</section>", a_at) + len("</section>")
        broken = index.replace(sec_std, sec_std[:a_at] + sec_std[a_end:])
        with open(f"{self.ctx.pages_dir}/index.html", "w", encoding="utf-8") as f:
            f.write(broken)
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            r._verify_part2_outputs(self.ctx)
        self.assertIn("FAMILY_Z_PART2_OUTPUT_MISMATCH", str(cm.exception))
        # (b) Std節とAdv節のPart 2ブロックを取り違える(levelを取り違えたブロック=描画不一致)
        def blk(sec):
            i = sec.index("Grammar &amp; Sentence Structure")
            st = sec.rindex("<section class='study'>", 0, i)
            return st, sec.index("</section>", i) + len("</section>")
        (as_, ae_), (ss_, se_) = blk(sec_adv), blk(sec_std)
        b_adv, b_std = sec_adv[as_:ae_], sec_std[ss_:se_]
        if b_adv != b_std:
            swapped = index.replace(b_adv, "@@ADV@@").replace(b_std, "@@STD@@").replace("@@ADV@@", b_std).replace("@@STD@@", b_adv)
            with open(f"{self.ctx.pages_dir}/index.html", "w", encoding="utf-8") as f:
                f.write(swapped)
            with self.assertRaises(r.FamilyZE2EStop):
                r._verify_part2_outputs(self.ctx)

    def test_omit_renders_no_grammar_corner_in_both_sections_and_is_not_counted_as_reviewed(self):
        self._pend()
        self._select_kp()
        n_expl = self.explain_calls()
        for lv in ("b1b", "a2"):
            sd = r._part2_dir(self.ctx, lv)
            gr.op_decide(sd, choice="omit", reason="今回は解説を出さない", candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")
        zw._quiet(r.run_stage, self.ctx, "kp")
        self.assertEqual(self.explain_calls(), n_expl)     # 0件確定はLLM 0
        self._run_rest()
        index = rd(f"{self.ctx.pages_dir}/index.html")
        self.assertNotIn("特に取り上げる難所", index)                          # 固定文面は撤去(ユーザー正式決定2026-10-29 §2C: 0件はコーナー全体を非表示)
        self.assertNotIn("Grammar &amp; Sentence Structure", index)          # 見出しも空枠も出さない
        self.assertEqual(index.count("<section class='study'>"), 1)         # Advanced の Part 1 のみ(Standard は学習ブロックなし)
        for lv in ("b1b", "a2"):
            self.assertFalse(os.path.exists(f"{r._part2_dir(self.ctx, lv)}/{g2.PART2_FILE_STEM}.md"), lv)   # 0件=mdも書かない
        pv = r._verify_part2_outputs(self.ctx)              # 0件確定も節単位検査を通る(期待ブロック数=0)
        self.assertEqual((pv["b1b"]["part2_blocks"], pv["a2"]["part2_blocks"]), (0, 0))

    def test_one_item_picked_from_top2_renders_one_block_and_two_picks_are_rejected(self):
        """文法選定仕様(2026-10-27): 2件同時選択は拒否され(状態は待機のまま)、Top2の1件採用が節に1ブロック載り節単位検査を通る。"""
        self._pend()
        self._select_kp()
        sd_b, sd_s = r._part2_dir(self.ctx, "b1b"), r._part2_dir(self.ctx, "a2")
        with self.assertRaises(g2.Part2ReviewError):          # 旧『2件採用』は拒否
            _decide_pick(sd_b, [1, 0])
        self.assertIn(gr.load_review(sd_b)["status"], rv.GRAMMAR_WAIT_STATUSES)   # 拒否は確定に影響しない(待機のまま)
        _decide_pick(sd_b, [1])             # Top2を1件だけ選ぶ
        _decide_top1(sd_s)
        zw._quiet(r.run_stage, self.ctx, "kp")
        self._run_rest()
        res = jl(f"{sd_b}/{g2.RESULT_FILENAME}")
        items = g2.result_items(res)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["selection"]["candidate_id"], gr.load_candidates(sd_b)["candidates"][1]["candidate_id"])
        index = rd(f"{self.ctx.pages_dir}/index.html")
        sec_adv, _ = self._sections(index)
        self.assertEqual(sec_adv.count("Grammar &amp; Sentence Structure"), 1)
        self.assertIn(items[0]["selection"]["sentence"].split(",")[0].replace("&", "&amp;").replace("'", "&#x27;")[:12], sec_adv)
        self.assertEqual(r._verify_part2_outputs(self.ctx)["b1b"]["part2_blocks"], 1)

    def test_declared_absence_auto_adopts_top1_and_is_labelled_unreviewed(self):
        self.declare()
        zw._quiet(r.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            sd = r._part2_dir(self.ctx, lv)
            self.assertEqual(gr.load_review(sd)["status"], rv.ST_AUTO)          # UNREVIEWED_AUTO_ADOPTED(レビュー済みに数えない)
        self.assertEqual((self.extract_calls(), self.explain_calls()), (2, 2))   # 自動採用はTOP1のみ生成(Adv1+Std1)

    def test_rejected_regenerate_of_confirmed_grammar_writes_no_failed_record_and_guides_revoke(self):
        """D4: 確定済み文法への --regenerate-stage part2_cand_<lv> は拒否される。part2_failed.jsonを書かず、次の一手は同じコマンドの繰り返しにならない(revoke案内)。"""
        self._pend()
        self._finish()
        import er128_kp_confirmed_content_01 as cc
        for lv in ("b1b", "a2"):
            sd = r._part2_dir(self.ctx, lv)
            # 確定レコード(sidecar)の作成は委任_04(from-form)の所有。ここでは『ユーザー確定済みの文法がある』状態だけを模擬し、
            # 拒否そのもの(er128.guard_grammar -> gr.ensure_grammar_review -> Part2Stale)は本物の経路を通す。
            state = {"sidecar": {"items": [{"id": "cand_confirmed"}]}, "level": lv, "kp_dir": self.src[lv]}
            self.ctx.regenerate_stage = f"part2_cand_{lv}"
            try:
                with mock.patch.object(cc, "grammar_state", return_value=state):
                    with self.assertRaises(r.FamilyZE2EStop) as cm:
                        zw._quiet(r.run_stage, self.ctx, "kp")
            finally:
                self.ctx.regenerate_stage = None
            msg = str(cm.exception)
            hint = msg.split("次の一手:")[-1]
            self.assertIn("CONFIRMED_CONTENT_LOCKED", msg)
            self.assertIn("revoke", hint)                                                   # 次の一手=確定の取消し(revoke)
            self.assertNotIn(f"--regenerate-stage part2_cand_{lv}", hint.replace("では変えられません", ""))   # 同じregenerateの繰り返しにしない
            self.assertFalse(os.path.exists(f"{sd}/{g2.FAILED_FILENAME}"), lv)               # 操作の拒否は失敗記録(part2_failed.json)を残さない
            self.assertTrue(os.path.exists(f"{sd}/{g2.RESULT_FILENAME}"), lv)                # 確定済みの成果物は無傷


# ============================================================
# X
# ============================================================
class XPart2Integration(unittest.TestCase):
    def setUp(self):
        self._cwd = os.getcwd()
        self.addCleanup(os.chdir, self._cwd)
        ri.isolate_part2(self, check_translation=True)
        ri.no_decision_record(self)
        pm.CALLS.clear()
        self.work, self.src, self.out = ri._x_setup()
        os.remove(rv.declarations_path(self.out))          # 宣言なし=待機が既定
        self.addCleanup(shutil.rmtree, self.work, True)
        self.addCleanup(shutil.rmtree, self.out, True)
        self.sd = f"{self.out}/b1b/study_text"
        self.sd_a2 = f"{self.out}/a2/study_text"

    def _main(self, stage, *, client=None, extra=(), level="b1b"):
        os.chdir(self.work)
        argv = ["x", "--slug", "t", "--run", "r", "--out-dir", self.out, "--stage", stage, "--level", level, *extra]
        tts, asm = mock.Mock(), mock.Mock()
        patches = [mock.patch.object(sys, "argv", argv),
                   mock.patch.object(xr, "generate_family_x_b1_segments", tts),
                   mock.patch.object(xr, "generate_family_x_a2_segments", tts),
                   mock.patch.object(xr, "stage_assemble_family_x_b1", asm),
                   mock.patch.object(xr, "stage_assemble_family_x_a2", asm),
                   mock.patch.object(xr, "run_family_x_a2_scaffold", return_value={}),
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

    def test_wait_once_with_unified_request_pregen_before_wait_and_no_part1(self):
        client = ri.FakeClient()
        rc, tts, asm, log = self._main("scaffold", client=client)
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        self.assertEqual(log.count(rv.PENDING_MARKER), 1)    # 待機表示は1回
        self.assertEqual(pm.CALLS[0], "extract")               # Step A''が先頭
        n_expl = pm.CALLS.count("explain")
        self.assertGreater(n_expl, 0)                          # 全候補の解説は待機の前に事前生成(解説全文を見せてから選ばせる)
        self.assertEqual(set(pm.CALLS), {"extract", "explain"})
        self.assertEqual(client.calls, [])                    # Part 1は確認前に0
        self.assertTrue(os.path.exists(f"{self.out}/review_request.md"))
        self.assertFalse(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))
        tts.assert_not_called()
        # 待機中の再実行はAPI 0
        before = list(pm.CALLS)
        rc, *_ = self._main("scaffold", client=client)
        self.assertEqual(rc, rv.EXIT_CODE_PENDING)
        self.assertEqual(pm.CALLS, before)

    def test_resume_runs_part1_once_and_finalize_is_llm_zero_then_reuse_is_api0(self):
        self._main("scaffold", client=ri.FakeClient())
        pend_calls = list(pm.CALLS)
        _decide_top1(self.sd)
        client = ri.FakeClient()
        rc, tts, asm, log = self._main("scaffold", client=client)
        # mock訳はPart 1訳と必ず異なる=食い違いISSUEは失敗(rc=3)ではなく待機(rc=4)。解消=ユーザー了承(実運用の手段(b))
        self.assertEqual(rc, rv.EXIT_CODE_PENDING, log)
        self.assertTrue(os.path.exists(f"{self.sd}/grammar_translation_issue.json"))
        self.assertFalse(os.path.exists(f"{self.sd}/{g2.FAILED_FILENAME}"))
        _accept_translation_issue(self.sd)
        client2 = ri.FakeClient()
        rc, tts, asm, log = self._main("scaffold", client=client2)
        self.assertIsNone(rc, log)
        self.assertEqual(pm.CALLS, pend_calls)               # Step A''は再実行せず、確定後のfinalizeはLLM 0
        self.assertEqual(len(client.calls) + len(client2.calls), 2)   # Part 1: 解説1+訳1(再開しても再生成しない)
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))
        again = ri.FakeClient()
        rc, *_ = self._main("scaffold", client=again)
        self.assertIsNone(rc)
        self.assertEqual(pm.CALLS, pend_calls)
        self.assertEqual(again.calls, [])

    def test_pregen_failure_is_rc3_with_failed_record_blocks_tts_and_recovers_via_scaffold_rerun(self):
        with mock.patch.object(pm, "mock_explain_call_fn", BAD_EXPLAIN):
            rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient())
        self.assertEqual(rc, 3, log)
        self.assertIn("同じ `--stage scaffold` コマンドを再実行", log)          # support/KP未発注の段階の失敗=scaffold再実行(study_textはKP未生成でPart 1に進めない)
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.FAILED_FILENAME}"))
        self.assertEqual(json.loads(rd(f"{self.sd}/{g2.FAILED_FILENAME}"))["stage"], "part2_expl_b1b")
        tts.assert_not_called()
        rc, tts, asm, log = self._main("tts", client=ri.FakeClient())
        self.assertIn(rc, (3, 4))
        tts.assert_not_called()
        # 回復: 同じscaffoldコマンドの再実行(再抽出なし・未生成分のみ生成)。確認待ち(rc=4)まで進む
        rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient())
        self.assertEqual(rc, rv.EXIT_CODE_PENDING, log)
        self.assertEqual(pm.CALLS.count("extract"), 1)
        self.assertFalse(os.path.exists(f"{self.sd}/{g2.FAILED_FILENAME}"))
        self.assertTrue(os.path.exists(f"{self.sd}/{g2.FAILED_FILENAME.replace('.json', '.resolved.json')}"))

    def test_tts_and_assemble_entrances_wait_while_unconfirmed(self):
        self._main("scaffold", client=ri.FakeClient())
        for stage in ("tts", "assemble"):
            rc, tts, asm, log = self._main(stage, client=ri.FakeClient())
            self.assertIn(rc, (3, 4), stage)
            tts.assert_not_called()
            asm.assert_not_called()

    # ---- 両level(Standard=a2 / Advanced=b1b)
    def _both_to_confirmed(self, decide_b1b=_decide_top1, decide_a2=_decide_top1):
        """両levelの待機(rc=4)->両levelの確定->Part 1訳との食い違い了承->scaffold完了(rc=None)まで進める。"""
        rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        self.assertEqual(rc, rv.EXIT_CODE_PENDING, log)
        self.assertEqual(log.count(rv.PENDING_MARKER), 1)                       # 待機表示は1回(両levelの文法を統合)
        decide_b1b(self.sd)
        decide_a2(self.sd_a2)
        rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        if rc == rv.EXIT_CODE_PENDING and os.path.exists(f"{self.sd}/grammar_translation_issue.json"):   # Part 1訳との食い違い(待機)
            _accept_translation_issue(self.sd)
            rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        self.assertIsNone(rc, log)

    def test_both_levels_pregen_before_wait_then_finalize_llm_zero_and_player_has_block_in_each_section(self):
        ri.decision_record(self, "T2")
        rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        self.assertEqual(rc, rv.EXIT_CODE_PENDING, log)
        self.assertEqual(pm.CALLS.count("extract"), 2)                          # Adv1+Std1
        n_expl = pm.CALLS.count("explain")
        self.assertGreater(n_expl, 0)
        self.assertFalse(os.path.exists(f"{self.sd}/{g2.RESULT_FILENAME}"))
        self.assertFalse(os.path.exists(f"{self.sd_a2}/{g2.RESULT_FILENAME}"))
        tts.assert_not_called()
        self._both_to_confirmed()
        self.assertEqual((pm.CALLS.count("extract"), pm.CALLS.count("explain")), (2, n_expl))   # 確定後のfinalizeはLLM 0
        for sd in (self.sd, self.sd_a2):
            self.assertTrue(os.path.exists(f"{sd}/{g2.RESULT_FILENAME}"), sd)
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, tts, asm, log = self._main("player", client=ri.FakeClient(), level="both")
        self.assertIsNone(rc, log)
        page = rd(f"{self.out}/player.html")
        marker = "Grammar &amp; Sentence Structure"
        self.assertEqual(page.count("<section class='study'>"), 3)               # Adv: Part 1+Part 2 / Std: Part 2
        sec_adv, sec_std = xr.player_level_section(page, "b1b"), xr.player_level_section(page, "a2")
        self.assertEqual((sec_adv.count(marker), sec_std.count(marker)), (1, 1))  # 各levelの節にちょうど1個
        self.assertLess(sec_adv.index("Vocabulary &amp; Expressions"), sec_adv.index(marker))   # Advanced: Part 1の直後
        self.assertNotIn("Vocabulary", sec_std)                                  # StandardにPart 1は無い
        # 確定結果を改変するとplayerの入口が止まる(M-2。Standardも)
        res = f"{self.sd_a2}/{g2.RESULT_FILENAME}"
        d = json.loads(rd(res))
        it0 = d["items"][0]["selection"] if d.get("schema") == g2.SCHEMA_RESULT_V2 else d["selection"]
        it0["sentence"] = it0["sentence"] + " x"
        with open(res, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False))
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, *_ = self._main("player", client=ri.FakeClient(), level="both")
        self.assertEqual(rc, 3)

    def test_both_levels_zero_candidate_path_renders_no_grammar_corner_in_each_section(self):
        ri.decision_record(self, "T2")
        omit = lambda sd: gr.op_decide(sd, choice="omit", reason="今回は解説を出さない", candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")   # noqa: E731
        self._both_to_confirmed(decide_b1b=omit, decide_a2=omit)
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, tts, asm, log = self._main("player", client=ri.FakeClient(), level="both")
        self.assertIsNone(rc, log)
        page = rd(f"{self.out}/player.html")
        self.assertNotIn("特に取り上げる難所", page)                              # 固定文面は撤去(0件=コーナー全体を非表示)
        self.assertNotIn("Grammar &amp; Sentence Structure", page)               # 見出し・空枠も出さない
        self.assertEqual(page.count("<section class='study'>"), 1)              # Advanced の Part 1 のみ
        self.assertNotIn("class='study'", xr.player_level_section(page, "a2"))

    def test_one_item_picked_in_standard_renders_in_one_block_and_two_picks_are_rejected(self):
        ri.decision_record(self, "T2")
        def decide_a2(sd):
            with self.assertRaises(g2.Part2ReviewError):      # Std側でも2件同時選択は拒否(旧『2件採用』)
                _decide_pick(sd, [1, 0])
            return _decide_pick(sd, [1])
        self._both_to_confirmed(decide_a2=decide_a2)
        res = json.loads(rd(f"{self.sd_a2}/{g2.RESULT_FILENAME}"))
        items = g2.result_items(res)
        self.assertEqual(len(items), 1)
        with mock.patch.object(xr, "derive_japanese_title", lambda sd: {"japanese_title": "T", "source": "test"}):
            rc, tts, asm, log = self._main("player", client=ri.FakeClient(), level="both")
        self.assertIsNone(rc, log)
        sec_std = xr.player_level_section(rd(f"{self.out}/player.html"), "a2")
        self.assertEqual(sec_std.count("Grammar &amp; Sentence Structure"), 1)

    def test_study_text_stage_accepts_standard_level_without_part1(self):
        """X `--stage study_text` のAdvanced限定parser.errorを撤去: --level a2 でもPart 2(候補->事前生成->待機->finalize)を通る。"""
        rc, tts, asm, log = self._main("study_text", client=ri.FakeClient(), level="a2")
        self.assertEqual(rc, rv.EXIT_CODE_PENDING, log)                          # 未確定=待機(Part 1は呼ばない)
        self.assertEqual(pm.CALLS.count("extract"), 1)
        _decide_top1(self.sd_a2)
        client = ri.FakeClient()
        rc, tts, asm, log = self._main("study_text", client=client, level="a2")
        self.assertIsNone(rc, log)
        self.assertEqual(client.calls, [])                                       # Standardには Part 1が無い
        self.assertTrue(os.path.exists(f"{self.sd_a2}/{g2.RESULT_FILENAME}"))
        self.assertEqual(pm.CALLS.count("extract"), 1)                           # 再抽出なし

    def test_public_builder_requires_confirmation_and_renders_both_levels(self):
        ri.decision_record(self, "T2")
        rc, *_ = self._main("scaffold", client=ri.FakeClient(), level="both")
        art_adv, art_std = rd(f"{self.src}/b1b/article.md"), rd(f"{self.src}/a2/article.md")
        for lv, art in (("b1b", art_adv), ("a2", art_std)):
            with self.assertRaises(p2w.Part2NotConfirmed):
                p2w.public_study_html(self.out, art, level=lv)
        self._both_to_confirmed_after_pending()
        html_adv = p2w.public_study_html(self.out, art_adv, level="b1b")
        self.assertEqual(html_adv.count("<section class='study'>"), 2)
        _pos = [html_adv.index(m) for m in ("Vocabulary &amp; Expressions", "Grammar &amp; Sentence Structure", "<h3>ニュアンス解説</h3>") if m in html_adv]
        self.assertEqual(_pos, sorted(_pos))   # Part 1 → 文法 → ニュアンス解説(存在するブロック同士の相対順。M-5)
        html_std = p2w.public_study_html(self.out, art_std, level="a2")
        self.assertEqual(html_std.count("<section class='study'>"), 1)           # Standardは Part 2だけ
        self.assertNotIn("Vocabulary", html_std)
        with self.assertRaises(TypeError):
            p2w.public_study_html(self.out, art_adv)                              # levelは必須(暗黙のAdvanced既定なし)
        os.remove(f"{self.sd_a2}/{g2.RESULT_FILENAME}")
        with self.assertRaises(g2.Part2Error):
            p2w.public_study_html(self.out, art_std, level="a2")

    def _both_to_confirmed_after_pending(self):
        _decide_top1(self.sd)
        _decide_top1(self.sd_a2)
        rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        if rc == rv.EXIT_CODE_PENDING and os.path.exists(f"{self.sd}/grammar_translation_issue.json"):
            _accept_translation_issue(self.sd)
            rc, tts, asm, log = self._main("scaffold", client=ri.FakeClient(), level="both")
        self.assertIsNone(rc, log)


if __name__ == "__main__":
    unittest.main()
