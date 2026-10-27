# -*- coding: utf-8 -*-
"""KP Human Review: Family Z runner(er026)配線の単体test。API 0(LLM由来の関数は全てmock、Redundancy QA/実clientは到達したら即失敗)。
実行: .venv\\Scripts\\python.exe -m unittest er119_z_wiring_test_01 -v
対象: 宣言なし=待機(両レベルの候補を生成してから1回だけ止まる)・再実行でAPI 0・M-2(gloss HR snapshotの署名)・M-3(a)(b)(c)・
      旧run互換・hooksでモードを渡せないこと・rc=4とstdoutマーカー・RESTART_STORM間隔(R-4)。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import er003_key_words_gloss_alignment as ga
import er011_key_phrase_set_redundancy_qa_01 as rq
import er026_family_z_fiction_production_runner_01 as r
import er062_family_z_structure_01 as st62
import er119_kp_human_review_01 as rv
from er119_test_support_01 import jd, jl, rd, wr

PRE = ["seed_check", "writer", "std_adjust", "plan", "support"]


def _quiet(fn, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*a, **k)


class ZBase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        stack = contextlib.ExitStack()
        # 実API到達は即失敗(Redundancy QA・client生成・Support・KP)
        for target in ("er003_v1_en_direct_vfl_01_generate.get_client", "er003_v1_n3_01_scaffold_generate.run_key_phrases",
                       "er011_key_phrase_set_redundancy_qa_01.make_redundancy_qa_fn", "er105_kp_fulltext_selector_01.make_selector_fn",
                       "er119_kp_prompt_2v_01.make_vocab_selector_fn", "er003_key_words_canonicalization.make_canonicalization_fn",
                       "er003_key_words_gloss_alignment.make_alignment_fn"):
            stack.enter_context(mock.patch(target, side_effect=AssertionError(f"REAL API PATH CALLED: {target}")))
        stack.enter_context(mock.patch.object(rv, "STORE_ROOT", os.path.join(self.tmp, "store")))
        self.addCleanup(stack.close)
        self.ctx = r.build_mock_context(self.tmp)
        # 既存mock E2E testのimportでbuild_mock_contextが宣言付きにwrapされていても、このtestは『宣言なし』から始める
        decl = rv.declarations_path(self.ctx.out_dir)
        if os.path.exists(decl):
            os.remove(decl)
        _quiet(r.run_stages, self.ctx, PRE)
        self.src = {lv: f"{self.ctx.out_dir}/key_phrases/{lv}" for lv in ("b1b", "a2")}
        self.assets = {lv: r._kp_assets_dir(self.ctx, lv) for lv in ("b1b", "a2")}

    def kp_calls(self):
        p = self.ctx.mock_api.path
        if not os.path.exists(p):
            return 0
        return sum(1 for line in rd(p).splitlines() if '"kind": "kp"' in line)

    def _kind_calls(self, kind):
        p = self.ctx.mock_api.path
        if not os.path.exists(p):
            return 0
        return sum(1 for line in rd(p).splitlines() if f'"kind": "{kind}"' in line)

    def extract_calls(self):
        return self._kind_calls("part2_extract")

    def explain_calls(self):
        return self._kind_calls("part2_explain")

    def declare(self):
        return rv.add_declaration(run_dirs=[self.ctx.out_dir], by="test-fixture", reason="Human不在(明示宣言)")


class TestZWait(ZBase):
    def test_no_declaration_generates_both_levels_then_raises_pending_once(self):
        n_before = len(rd(self.ctx.mock_api.path).splitlines())
        with self.assertRaises(r.FamilyZKpReviewPending) as cm:
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertEqual(sorted(p["level"] for p in cm.exception.pending if p.get("kind") != "grammar"), ["a2", "b1b"])   # 両レベルの候補を先に作ってからまとめて1回待機
        self.assertEqual([p["kind"] for p in cm.exception.pending if p.get("kind") == "grammar"], ["grammar", "grammar"])   # 全level化(委任_03): 文法(Part 2)はAdv/Stdの2件が同じ1回の待機に載る
        for lv in ("b1b", "a2"):
            self.assertEqual(rv.load_review(self.src[lv])["status"], rv.ST_PENDING)
            self.assertTrue(os.path.exists(rv.paths(self.src[lv])["request"]))
            for f in ("keywords_canonicalized.json", "vocab_confirmed.json", "kp_selection_final.json"):   # DefaultOffIsolation: 副作用ファイル0
                self.assertFalse(os.path.exists(f"{self.src[lv]}/{f}"), f"{lv}/{f}")
            self.assertFalse(os.path.exists(f"{self.assets[lv]}/keywords_canonicalized.json"))
        self.assertTrue(os.path.exists(f"{self.ctx.out_dir}/kp_review_pending.json"))
        self.assertEqual(self.kp_calls(), 2)
        # 有料の後続(Adv解説・Part 1・TTS)のmock API呼出は0: kp stage開始後に増えたcallは候補生成(kp)だけ
        after = [json.loads(l)["kind"] for l in rd(self.ctx.mock_api.path).splitlines()][n_before:]
        # 全level化(GRAMMAR-PREGEN-ALL-LEVELS-01): 文法の候補抽出(Step A'')と全候補の解説の事前生成(Step B)が待機の前に両levelで走る(確認時に解説全文を見せるため)
        self.assertEqual(set(after), {"kp", "part2_extract", "part2_explain"}, after)
        self.assertEqual(after.count("part2_extract"), 2)

    def test_rerun_while_pending_makes_no_new_generation_call(self):
        with self.assertRaises(r.FamilyZKpReviewPending):
            _quiet(r.run_stage, self.ctx, "kp")
        with self.assertRaises(r.FamilyZKpReviewPending):
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertEqual(self.kp_calls(), 2, "再実行(候補sha一致)は候補を再生成しない")

    def test_hooks_cannot_carry_the_mode(self):
        """ctx.hooks等からautoにできない: 宣言ファイルだけが単一読取点。hooksに"kp_review":"auto"等を入れても待機のまま。"""
        self.ctx.hooks["kp_review"] = "auto"
        self.ctx.hooks["kp_review_mode"] = {"mode": "auto"}
        self.ctx.hooks["auto"] = True
        with self.assertRaises(r.FamilyZKpReviewPending):
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertFalse(os.path.exists(rv.declarations_path(self.ctx.out_dir)))

    def test_declaration_progresses_and_records_unreviewed_auto(self):
        self.declare()
        res = _quiet(r.run_stage, self.ctx, "kp")
        self.assertIn("b1b", res.get("kp_review", res) if isinstance(res, dict) else res)
        for lv in ("b1b", "a2"):
            self.assertEqual(rv.load_review(self.src[lv])["status"], rv.ST_AUTO)
            self.assertEqual(rv.require_final_consistent(self.src[lv], level=lv, require_src_contract=True)["status"], rv.ST_AUTO)
            self.assertTrue(os.path.exists(f"{self.assets[lv]}/keywords_canonicalized.json"))

    def test_select_resumes_without_new_generation(self):
        with self.assertRaises(r.FamilyZKpReviewPending):
            _quiet(r.run_stage, self.ctx, "kp")
        for lv in ("b1b", "a2"):
            rv.op_select(self.src[lv], kp_ranks=[1, 2, 3], vocab_ranks=([1, 2, 3, 4, 5] if lv == "b1b" else None), by="human")
        import er119_grammar_review_01 as gr   # 委任_03: 文法(Part 2)の確認も同じ待機点
        n_expl = self.explain_calls()
        self.assertGreater(n_expl, 0)                # 事前生成は待機の前に済んでいる(両level分)
        for glv in ("b1b", "a2"):
            sd = r._part2_dir(self.ctx, glv)
            gr.op_decide(sd, choice="top1", accept_ai=True, candidates_sha256=gr.load_candidates(sd)["candidates_sha256"], by="human")
        _quiet(r.run_stage, self.ctx, "kp")
        self.assertEqual(self.kp_calls(), 2)
        self.assertEqual(self.extract_calls(), 2)    # 再開でStep A''を呼び直さない(両levelで1回ずつ)
        self.assertEqual(self.explain_calls(), n_expl)   # 確定後のfinalizeはLLM 0(事前生成の再利用)
        for lv in ("b1b", "a2"):
            self.assertEqual(rv.load_review(self.src[lv])["status"], rv.ST_REVIEWED)


class TestZConfirmationRebindD1(ZBase):
    """KCP3所見D1(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03): 自動採用runへ後からユーザー確定を入れてKP review署名が変わっても、kp_<lv>来歴の親sha不一致STOPにならず
    API 0で再バインドされる(TTS等の子孫はstale化しない)。本文が変わった場合は従来どおりSTOP。"""

    def _auto(self):
        self.declare()
        _quiet(r.run_stage, self.ctx, "kp")

    def _auto_ranks(self, lv):
        fin = jl(f"{self.src[lv]}/kp_selection_final.json")
        return fin

    def test_user_confirmation_after_auto_adoption_rebinds_without_stop_or_api(self):
        self._auto()
        prov0 = r._prov(self.ctx)
        e0 = dict(prov0.stage_entry("kp_b1b"))
        n_calls = (self.kp_calls(), self.extract_calls(), self.explain_calls())
        rev = rv.load_review(self.src["b1b"])
        self.assertEqual(rev["status"], rv.ST_AUTO)
        # 自動採用と同じ集合をHumanが後から確定する(フォーム/HRの確定相当)。署名が変わる
        doc = rv.load_candidates(self.src["b1b"])
        rank_of = {c["candidate_id"]: c["ai_rank"] for c in doc["candidates"]}
        sel = rev["selection"]
        rv.op_select(self.src["b1b"], kp_ranks=[rank_of[i] for i in sel["kp"]], vocab_ranks=[rank_of[i] for i in sel["vocab"]], by="human")
        self.assertEqual(rv.load_review(self.src["b1b"])["status"], rv.ST_REVIEWED)
        _quiet(r.run_stage, self.ctx, "kp")        # 以前は kp_b1b の親sha不一致STOP
        e1 = r._prov(self.ctx).stage_entry("kp_b1b")
        self.assertNotEqual(e1["input_sha256"], e0["input_sha256"])
        self.assertEqual(e1["output_sha256"], e0["output_sha256"])                      # 出力は不変(再生成していない)
        self.assertEqual(len(e1["rebinds"]), 1)
        self.assertEqual(e1["rebinds"][0]["reason"], "confirmation_signature_changed")
        self.assertEqual(e1["rebinds"][0]["api_calls"], 0)
        self.assertEqual((self.kp_calls(), self.extract_calls(), self.explain_calls()), n_calls)   # API 0
        self.assertNotIn("kp_b1b", r._prov(self.ctx).data["downstream_stale"])
        for d in ("tts_b1b", "kp_expl_b1b"):
            self.assertNotIn(d, r._prov(self.ctx).data["downstream_stale"])             # 子孫はstale化しない(TTS再生成コストに波及しない)
        _quiet(r.run_stage, self.ctx, "kp")        # 再実行もAPI 0・再バインド履歴は増えない
        self.assertEqual(len(r._prov(self.ctx).stage_entry("kp_b1b")["rebinds"]), 1)

    def test_text_change_still_stops_and_helper_refuses_other_input_changes(self):
        self._auto()
        w62 = r._m().w62
        prov = r._prov(self.ctx)
        entry = prov.stage_entry("kp_b1b")
        # 旧署名で再計算した入力shaがentryと一致しない(=署名以外の入力が変わった)場合は付け替えない
        self.assertIsNone(w62.rebind_confirmation_input(prov, "kp_b1b", expected_old_input_sha="0" * 64, new_input_sha="1" * 64, new_signature="s"))
        self.assertEqual(prov.stage_entry("kp_b1b")["input_sha256"], entry["input_sha256"])
        # staleなstageは付け替えない
        prov.data["downstream_stale"].append("kp_b1b")
        self.assertIsNone(w62.rebind_confirmation_input(prov, "kp_b1b", expected_old_input_sha=entry["input_sha256"], new_input_sha="1" * 64, new_signature="s"))
        prov.data["downstream_stale"].remove("kp_b1b")
        # 本文を変えると従来どおり親sha不一致STOP
        p = r._level_text_path(self.ctx, "b1b")
        with open(p, "a", encoding="utf-8") as f:
            f.write("\n\nA changed paragraph appears.\n")
        with self.assertRaises(Exception) as cm:
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertNotIn("rebinds", r._prov(self.ctx).stage_entry("kp_b1b") or {})


class TestZSignatureAndConsumers(ZBase):
    def _auto(self):
        self.declare()
        _quiet(r.run_stage, self.ctx, "kp")

    def test_part1_items_follow_vocab_confirmed_five(self):
        self._auto()
        items = r._part1_items_b1b(self.ctx)
        self.assertEqual(len(items), 5)
        self.assertEqual([i["rank"] for i in items], [1, 2, 3, 4, 5])
        os.remove(f"{self.src['b1b']}/vocab_confirmed.json")
        with self.assertRaises(r.FamilyZE2EStop):
            r._part1_items_b1b(self.ctx)   # 3件へ黙って戻らない(fail-closed)

    def test_consumer_entry_refuses_stale_assets_and_unconfirmed(self):
        self._auto()
        r._assert_kp_review_consistent(self.ctx, "b1b", "test")   # 整合: OK
        p = f"{self.assets['b1b']}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["candidate_id"] = "p_stale"
        jd(p, d)
        with self.assertRaises(r.FamilyZE2EStop) as cm:
            r._assert_kp_review_consistent(self.ctx, "b1b", "test")
        self.assertIn("KP_ASSETS_STALE", str(cm.exception))

    def test_unconfirmed_review_is_pending_for_consumers(self):
        with self.assertRaises(r.FamilyZKpReviewPending):
            _quiet(r.run_stage, self.ctx, "kp")
        with self.assertRaises(r.FamilyZKpReviewPending):
            r._assert_kp_review_consistent(self.ctx, "b1b", "load_level_inputs")

    def test_M3a_stage_input_sha_changes_with_selection_signature(self):
        self._auto()
        prov = jl(f"{self.ctx.out_dir}/provenance.json") if os.path.exists(f"{self.ctx.out_dir}/provenance.json") else None
        sig0 = r._review_signature(self.ctx, "b1b")
        self.assertTrue(sig0)
        rv.op_reselect(self.src["b1b"], ng={}, note="n", by="human")
        self.assertEqual(rv.load_review(self.src["b1b"])["status"], rv.ST_RESELECT)
        # 再選定要求後は『確定署名なし』=消費者は止まる(旧署名のままstageを再利用しない)
        with self.assertRaises(r.FamilyZKpReviewPending):
            r._assert_kp_review_consistent(self.ctx, "b1b", "after-reselect")

    def test_M2_gloss_hr_snapshot_is_invalidated_when_signature_differs(self):
        self._auto()
        snap = f"{self.src['b1b']}/{rv.GLOSS_HR_SNAPSHOT}"
        wr(snap, json.dumps({"selection_signature": "OLD", "article_sha": "x"}))
        out = rv.invalidate_gloss_snapshot(self.src["b1b"])
        self.assertTrue(out)
        self.assertFalse(os.path.exists(snap))   # 旧snapshotはINVALIDATEDとして退避(再利用されない)
        self.assertTrue(any("INVALIDATED" in n for n in os.listdir(self.src["b1b"])))


class TestZPostHocReviewAndRegenerate(ZBase):
    """M-3(a)(b): 確定署名が来歴のinput_shaに入る/事後Reviewで確定が変わったら親sha不一致でSTOP(旧resultを黙って再利用しない)/
    `--regenerate-stage kp_<lv>`=現在のreviewからの再finalize(再選定なし)+子孫stale化。"""

    def _text(self, lv):
        return r.canonical_article_text(r._m().w62.rd(r._level_text_path(self.ctx, lv)))

    def test_M3a_input_sha_includes_signature_and_M3b_regenerate_is_refinalize(self):
        self.declare()
        _quiet(r.run_stage, self.ctx, "kp")
        prov = r._prov(self.ctx)
        sig0 = rv.load_review(self.src["b1b"])["selection_signature"]
        self.assertEqual(prov.stage_entry("kp_b1b")["input_sha256"], r._sha(f"{self._text('b1b')}|{sig0}"))
        n = self.kp_calls()
        # 事後Review(AUTO -> REVIEWED、別の選定)。確定署名が変わる
        rv.op_select(self.src["b1b"], kp_ranks=[1, 2, 4], vocab_ranks=[1, 2, 4, 5, 6], by="human")
        # 確定(finalize)は消費者入口が行う前なので、いったんkp stageを再実行するとreview側の確定→来歴の親sha不一致でSTOP
        with self.assertRaises(Exception) as cm:
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertIn("kp_b1b: 親sha不一致", str(cm.exception))
        # 明示regenerate: 再選定せず現在のreviewからfinalize。新署名が来歴に入る。KP表現が変わるので子孫(解説・Part 1)は
        # 既存の2段再生成手順(kp_expl_b1b -> kp_part1_b1b)で止まる(既存仕様。委任_14 Opus必須9)
        self.ctx.regenerate_stage = "kp_b1b"
        with self.assertRaises(Exception) as cm2:
            _quiet(r.run_stage, self.ctx, "kp")
        self.assertIn("kp_expl_b1b", str(cm2.exception))
        for step in ("kp_expl_b1b", "kp_part1_b1b", "kp_part1_ja_b1b"):
            self.ctx.regenerate_stage = step
            try:
                _quiet(r.run_stage, self.ctx, "kp")
                break
            except Exception as e:   # noqa: BLE001  次の子孫で止まる(想定どおり)
                self.assertIn("親sha不一致", str(e))
        self.ctx.regenerate_stage = None
        sig1 = rv.load_review(self.src["b1b"])["selection_signature"]
        self.assertNotEqual(sig0, sig1)
        self.assertEqual(r._prov(self.ctx).stage_entry("kp_b1b")["input_sha256"], r._sha(f"{self._text('b1b')}|{sig1}"))
        self.assertEqual(self.kp_calls(), n, "regenerateは再選定(候補生成)をしない")
        got = sorted(it["candidate_id"] for it in jl(f"{self.assets['b1b']}/keywords_canonicalized.json")["items"])
        self.assertEqual(got, sorted(rv.sel_ids(rv.load_review(self.src["b1b"])["selection"], "kp")))


class TestZLegacyRun(ZBase):
    def test_legacy_run_without_review_is_reused_without_selection(self):
        """review無し・KP結果とprovenance entryがある旧runは従来どおり再利用(再選定しない・待機しない)。"""
        self.declare()
        _quiet(r.run_stage, self.ctx, "kp")
        n = self.kp_calls()
        # 旧run化: review/候補ファイルを削除(旧run=review導入前に作られたrun)
        for lv in ("b1b", "a2"):
            for f in (rv.paths(self.src[lv])["review"], rv.paths(self.src[lv])["candidates"]):
                if os.path.exists(f):
                    os.remove(f)
        self.assertTrue(r._kp_legacy_run(self.ctx, "b1b", r._prov(self.ctx)))
        self.assertIsNone(rv.require_final_consistent(self.src["b1b"]))
        self.assertEqual(self.kp_calls(), n)


class TestZMainExitCode(unittest.TestCase):
    def test_main_returns_4_with_marker_when_pending(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        argv = ["--mode", "mock", "--story", "melos", "--run", "t119", "--stage", "all", "--stages", ",".join(PRE + ["kp"])]
        stack = contextlib.ExitStack()
        for target in ("er003_v1_en_direct_vfl_01_generate.get_client", "er011_key_phrase_set_redundancy_qa_01.make_redundancy_qa_fn"):
            stack.enter_context(mock.patch(target, side_effect=AssertionError(f"REAL API PATH CALLED: {target}")))
        stack.enter_context(mock.patch.object(rv, "STORE_ROOT", os.path.join(tmp, "store")))
        stack.enter_context(mock.patch.object(r, "E2E_RUN_ROOT", tmp))
        shutil.copytree("er026_output/family_z_production_e2e_01/melos/seed", f"{tmp}/melos/seed")   # Seed(不変・読取専用)の写し
        self.addCleanup(stack.close)
        orig = r.build_mock_context

        def no_decl(*a, **k):
            ctx = orig(*a, **k)
            p = rv.declarations_path(ctx.out_dir)
            if os.path.exists(p):
                os.remove(p)
            return ctx
        stack.enter_context(mock.patch.object(r, "build_mock_context", no_decl))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = r.main(argv)
        self.assertEqual(rc, 4)
        self.assertIn(rv.PENDING_MARKER, buf.getvalue())
        self.assertIn("再開コマンド", buf.getvalue())


class TestRestartStormInterval(unittest.TestCase):
    """R-4: 安全機構(5分間に3回起動でRESTART_STORM)は変更しない。運用で『rc=4後のselect/reselect→再起動』の間隔を守る根拠をtestで固定する。"""

    def test_three_launches_within_window_triggers_storm_and_spacing_avoids_it(self):
        d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d1, True)
        self.addCleanup(shutil.rmtree, d2, True)
        t0 = 1_000_000.0
        st62.record_launch_and_check_storm(d1, ["a"], now=t0)
        st62.record_launch_and_check_storm(d1, ["a"], now=t0 + 100)
        with self.assertRaises(st62.FamilyZStopSentinel):
            st62.record_launch_and_check_storm(d1, ["a"], now=t0 + 200)   # 3回目が5分以内=自動STOP
        self.assertTrue(os.path.exists(f"{d1}/STOP"))
        # 1回目と3回目を窓(300秒)より離せば発動しない: 待機(rc=4)→select→再開 を『2回目』で行い、reselectの再起動は窓外で行う
        st62.record_launch_and_check_storm(d2, ["a"], now=t0)
        st62.record_launch_and_check_storm(d2, ["a"], now=t0 + 100)
        out = st62.record_launch_and_check_storm(d2, ["a"], now=t0 + 301)
        self.assertEqual(out["launches_in_window"], 2)
        self.assertFalse(os.path.exists(f"{d2}/STOP"))


if __name__ == "__main__":
    unittest.main()
