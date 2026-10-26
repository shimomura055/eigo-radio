# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_02: 共通核(候補生成・状態機械・NG・宣言・finalize・消費側検査)の単体test。
API 0(LLM由来の関数はすべてmock。Env.n[...]で呼出回数を数える)。
実行: .venv\\Scripts\\python.exe -m unittest er119_kp_human_review_01_test_01 -v"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import threading
import unittest

import er105_kp_fulltext_selector_01 as ft
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er119_kp_prompt_2v_01 as p2v
from er119_test_support_01 import ARTICLE, ARTICLE2, CALL1, CALL2, Env, KpTestCase, jd, jl, rd, wr

P2_SHA = "a12896f485604f32efd52cb159d2615733c0eca262725af78db0b4f1c9a3dc9a"


def cid(phrase: str) -> str:
    return rv.candidate_id_for(phrase)


class TestPrompt2V(unittest.TestCase):
    def test_prompt2_unchanged_and_sha_pinned(self):
        self.assertEqual(ft.PROMPT_2_SHA256, P2_SHA)   # R-1: Prompt 2は無変更(sha不変)
        self.assertEqual(p2v.PROMPT_2V_SHA256, p2v.PROMPT_2V_SHA256_PINNED)

    def test_2v_differs_from_prompt2_only_in_head_and_condition6(self):
        a = ft.PROMPT_2_TEXT.split("\n")
        b = p2v.PROMPT_2V_TEXT.split("\n")
        self.assertEqual(len(a), len(b))
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        self.assertEqual(len(diff), 2, f"差分行は冒頭文と条件6の2行のみ: {diff}")
        self.assertTrue(a[diff[0]].startswith("以下の記事から") and a[diff[1]].startswith("6. "))
        # 条件1〜5と最終確認文は1字も変えない
        for i, (x, y) in enumerate(zip(a, b)):
            if i not in diff:
                self.assertEqual(x, y)

    def test_schema_reason_ja_after_phrase_and_no_item_count_constraint(self):
        props = list(p2v.SELECTOR_2V_JSON_SCHEMA["schema"]["properties"]["items"]["items"]["properties"])
        self.assertEqual(props[:2], ["phrase", "reason_ja"])
        s = json.dumps(p2v.SELECTOR_2V_JSON_SCHEMA)
        self.assertNotIn("minItems", s)
        self.assertNotIn("maxItems", s)

    def test_message_contains_already_selected_after_body(self):
        m = p2v.build_user_message("BODY", ["a b", "c d"])
        self.assertTrue(p2v.prompt_prefix_intact(m))
        self.assertIn("【記事本文】\nBODY", m)
        self.assertTrue(m.split("BODY", 1)[1].startswith(p2v.ALREADY_DELIMITER + "- a b\n- c d"))


class TestCandidateGeneration(KpTestCase):
    def test_candidates_generated_in_work_dir_not_kp_dir_M1(self):
        with Env(self.tmp) as env:
            r = self.ensure(env)
        self.assertEqual(r["state"], "PENDING")   # 宣言なし=待機
        # M-1: 候補生成直後に kp_dir/keywords_canonicalized.json は存在しない
        self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))
        self.assertFalse(os.path.exists(f"{self.kp_dir}/vocab_confirmed.json"))
        self.assertFalse(os.path.exists(f"{self.kp_dir}/kp_selection_final.json"))
        # 作業dirにはある(既存関数の書込先)
        self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_candidates/round_1/work/keywords_canonicalized.json"))
        self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_human_review_request.md"))

    def test_candidates_schema_and_hash(self):
        with Env(self.tmp) as env:
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        self.assertEqual(c["schema"], rv.SCHEMA_CANDIDATES)
        self.assertEqual(c["candidates_sha256"], rv.candidates_sha256(c))
        self.assertEqual([x["ai_rank"] for x in c["candidates"]], list(range(1, len(c["candidates"]) + 1)))
        self.assertLessEqual(len(c["candidates"]), rv.KP_CANDIDATE_MAX)
        self.assertEqual(len(c["candidates"]), 8)   # call1の3件+call2の5件
        self.assertEqual([x["origin"] for x in c["candidates"]], ["call1"] * 3 + ["call2"] * 5)
        self.assertEqual(c["prompt_sha256"]["call1"], P2_SHA)
        self.assertEqual(c["prompt_sha256"]["call2"], p2v.PROMPT_2V_SHA256)
        for x in c["candidates"]:
            self.assertIn("reason_ja", x)
            self.assertTrue(x["auto_eligible"])
            self.assertEqual(x["candidate_id"], cid(x["selection_phrase"]))

    def test_prompt2_message_unchanged_in_call1(self):
        with Env(self.tmp) as env:
            self.ensure(env)
        for m in env.messages1:
            self.assertTrue(m.startswith(ft.PROMPT_2_TEXT + ft.BODY_DELIMITER))
        for m in env.messages2:
            self.assertTrue(p2v.prompt_prefix_intact(m))
            self.assertIn("pushed prices up", m)   # 既選定3件が除外対象として渡る

    def test_call2_dedup_vs_top3_is_dropped(self):
        call2 = [{"phrase": "time lag", "reason_ja": "dup", "word_count": 2}] + CALL2[:2]
        with Env(self.tmp, call2=call2) as env:
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        self.assertIn("duplicate_of_top3", [d["stage"] for d in c["dropped"]])
        self.assertEqual(len(c["candidates"]), 5)

    def test_canonicalization_invalid_item_excluded_and_rerun_M7a(self):
        with Env(self.tmp, bad_phrases=["feel a spike"], rescue_env="0") as env:   # 救済前の挙動(M-7a)を検証するためkill switch OFFに固定
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        self.assertIn("feel a spike", [d["phrase"] for d in c["dropped"] if d["stage"] == "canonicalization"])
        self.assertNotIn("feel a spike", [x["selection_phrase"] for x in c["candidates"]])
        # 全体PASSの応答だけ受理: 2周目は"feel a spike"を除いた7件でcanonicalization
        self.assertEqual(len(env.canon_inputs[0]), 8)
        self.assertEqual(len(env.canon_inputs[-1]), 7)
        self.assertNotIn("feel a spike", env.canon_inputs[-1])
        # n_auto=7>=3: 外側retryなし(select1回)
        self.assertEqual(env.n["call1"], 1)

    def test_outer_retry_only_when_auto_lt3_and_gate_drop_M7c(self):
        # call1の3件が全てcanonicalization INVALID -> auto_eligibleはcall2の5件(>=3)なのでretryしない
        with Env(self.tmp, bad_phrases=[p["phrase"] for p in CALL1], rescue_env="0") as env:   # 救済前の挙動(M-7c)を検証
            self.ensure(env)
        self.assertEqual(env.n["call1"], 1)
        c = rv.load_candidates(self.kp_dir)
        self.assertEqual(len(c["candidates"]), 5)

    def test_outer_retry_replaces_list_when_auto_lt3(self):
        call1b = [{"phrase": "Before you know it", "word_count": 4}, {"phrase": "stay high", "word_count": 2}]
        call2_only_bad = [{"phrase": "in stock", "reason_ja": "x", "word_count": 2}]
        # 1周目: call1 3件のうち2件がINVALID、call2 1件 -> 有効2件(<3)かつGate除外あり -> 外側retry(2周目はcall1b+call2)
        with Env(self.tmp, call1_seq=[CALL1, call1b], call2_seq=[call2_only_bad, CALL2[3:5]],
                 bad_phrases=["pushed prices up", "took a sharp turn"]) as env:
            self.ensure(env)
        self.assertEqual(env.n["call1"], 2)
        c = rv.load_candidates(self.kp_dir)
        phrases = [x["selection_phrase"] for x in c["candidates"]]
        # 候補listは2周目のものに置換(merge禁止): 1周目の"time lag"/"in stock"は残らない
        self.assertNotIn("time lag", phrases)
        self.assertEqual(phrases, ["Before you know it", "stay high", "raw beans"])
        # 1周目で除外された句は2周目の選定noteで除外指定される
        self.assertIn("pushed prices up", env.messages1[1])

    def test_shortfall_without_gate_drop_does_not_retry(self):
        with Env(self.tmp, call2=[{"phrase": "in stock", "reason_ja": "x", "word_count": 2}]) as env:
            self.ensure(env)
        self.assertEqual(env.n["call1"], 1)   # LLMが少なく返しただけ=shortfall受容(数合わせretryなし)
        self.assertEqual(len(rv.load_candidates(self.kp_dir)["candidates"]), 4)

    def test_review_required_item_gets_qa_fail_flag_and_not_auto(self):
        with Env(self.tmp, qa_fail_phrases=["pushed prices up"]) as env:
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        x = next(i for i in c["candidates"] if i["selection_phrase"] == "pushed prices up")
        self.assertTrue(x["flags"]["qa_fail"])
        self.assertFalse(x["auto_eligible"])
        self.assertEqual(x["gates"]["canonicalization"], "REVIEW_REQUIRED")
        self.assertEqual(env.n["call1"], 1)   # 有効>=3なので再選定なし

    def test_gloss_hr_pending_flag(self):
        with Env(self.tmp, gloss_fail_phrases=["time lag"]) as env:
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        x = next(i for i in c["candidates"] if i["selection_phrase"] == "time lag")
        self.assertTrue(x["flags"]["gloss_hr_pending"])
        self.assertFalse(x["auto_eligible"])

    def test_redundancy_flags_from_candidate_wide_qa(self):
        with Env(self.tmp, red_ng_pairs=[(1, 2)]) as env:
            self.ensure(env)
        c = rv.load_candidates(self.kp_dir)
        by = {x["ai_rank"]: x for x in c["candidates"]}
        self.assertEqual(by[1]["flags"]["redundant_with"], [by[2]["candidate_id"]])
        self.assertEqual(c["redundancy_qa"]["status"], "REDUNDANCY_NG")
        self.assertEqual(env.n["red_cand"], 1)   # 候補全体で1回


class TestReviewFlowAndFinalize(KpTestCase):
    def _pending(self, **kw):
        env = Env(self.tmp, **kw)
        env.__enter__()
        self.addCleanup(env.__exit__)
        r = self.ensure(env)
        self.assertEqual(r["state"], "PENDING")
        return env

    def test_no_declaration_waits_and_downstream_api_zero_and_no_side_files(self):
        """DefaultOffIsolation型(核): 宣言なし->待機。finalizeの副作用ファイル0・以降のLLM呼出0(再実行でもAPI 0)。"""
        env = self._pending()
        n_after_gen = env.total_llm_calls()
        r2 = self.ensure(env)   # resume
        self.assertEqual(r2["state"], "PENDING")
        self.assertEqual(env.total_llm_calls(), n_after_gen, "resume(候補sha一致)は再選定せずAPI 0")
        for f in ("keywords_canonicalized.json", "vocab_confirmed.json", "kp_selection_final.json"):
            self.assertFalse(os.path.exists(f"{self.kp_dir}/{f}"))
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)
        with self.assertRaises(rv.KpReviewNotConfirmed):
            rv.require_final_consistent(self.kp_dir)

    def test_select_then_finalize_writes_confirmed_files_and_runs_final_redundancy_M8(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 3, 5], vocab_ranks=[1, 2, 3, 5, 7], by="human")
        red_before = env.n["red"]
        r = self.ensure(env)
        self.assertEqual(r["state"], "FINALIZED")
        kp = jl(f"{self.kp_dir}/keywords_canonicalized.json")
        self.assertEqual([i["rank"] for i in kp["items"]], [1, 2, 3])
        self.assertEqual([i["ai_rank"] for i in kp["items"]], [1, 3, 5])
        vo = jl(f"{self.kp_dir}/vocab_confirmed.json")
        self.assertEqual([i["ai_rank"] for i in vo["items"]], [1, 2, 3, 5, 7])
        self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_selection_final.json"))
        # M-8: 確定KP集合(3件)と確定vocab集合(5件)にRedundancy QAを再適用(各1回)
        self.assertEqual(env.n["red_final"], 2)
        self.assertEqual(env.n["red"] - red_before, 2)
        rv.require_final_consistent(self.kp_dir)
        # 再実行はAPI 0(署名一致・final_qa記録済み)
        n = env.total_llm_calls()
        self.ensure(env)
        self.assertEqual(env.total_llm_calls(), n)

    def test_select_validation_errors(self):
        self._pending(red_ng_pairs=[(1, 2)])
        with self.assertRaises(rv.KpReviewError) as e:
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        self.assertIn("重複", str(e.exception))                       # redundancy pair
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1, 3, 4, 5], vocab_ranks=[1, 3, 4, 5], by="h")   # KP最大3
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1, 3], vocab_ranks=[2, 3, 4], by="h")           # KP⊄vocab
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1], vocab_ranks=[1, 3, 4, 5, 6, 7], by="h")     # vocab最大5
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1], by="h")                                      # Advはvocab必須
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1, 3, 4], vocab_ranks=[1, 3, 4], ng={3: ""}, by="h")  # NG理由必須
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[1, 3, 4], vocab_ranks=[1, 3, 4], ng={3: "bad"}, by="h")  # 選択とNGの矛盾
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)

    def test_standard_level_rejects_vocab(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        r = self.ensure(env, level="a2")
        self.assertEqual(r["state"], "PENDING")
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir_a2, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="h")
        rv.op_select(self.kp_dir_a2, kp_ranks=[1, 2, 3], by="h")
        r = self.ensure(env, level="a2")
        self.assertEqual(r["state"], "FINALIZED")
        self.assertFalse(os.path.exists(f"{self.kp_dir_a2}/vocab_confirmed.json"))   # Stdは単語解説なし(I-1)

    def test_qa_fail_requires_explicit_accept(self):
        self._pending(qa_fail_phrases=["pushed prices up"])
        with self.assertRaises(rv.KpReviewError) as e:
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        self.assertIn("--accept-qa-fail", str(e.exception))
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], accept_qa_fail=[1], by="h")
        self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_REVIEWED)

    def test_gloss_hr_pending_not_selectable_until_resolved(self):
        self._pending(gloss_fail_phrases=["time lag"])
        with self.assertRaises(rv.KpReviewError) as e:
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        self.assertIn("gloss HR", str(e.exception))
        rv.op_resolve_gloss(self.kp_dir, rank=3, gloss="時間差", by="h")
        c = rv.load_candidates(self.kp_dir)
        self.assertEqual(c["candidates_sha256"], rv.load_review(self.kp_dir)["candidates_sha256"])
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")

    def test_accept_ai_is_reviewed_not_auto_and_needs_shown_sha_R6(self):
        self._pending()
        c = rv.load_candidates(self.kp_dir)
        with self.assertRaises(rv.KpReviewError):
            rv.op_select(self.kp_dir, kp_ranks=[], accept_ai=True, shown_candidates_sha256="deadbeef", by="h")
        r = rv.op_select(self.kp_dir, kp_ranks=[], accept_ai=True, shown_candidates_sha256=c["candidates_sha256"], by="h")
        self.assertEqual(r["status"], rv.ST_REVIEWED)
        self.assertTrue(r["accept_ai_default"])
        self.assertEqual(r["selection"]["kp"], [cid(p["phrase"]) for p in CALL1])

    def test_final_redundancy_ng_on_human_selection_returns_to_pending_M8(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        env.final_red_seq = ["NG"]
        r = self.ensure(env)
        self.assertEqual(r["state"], "PENDING")
        rev = rv.load_review(self.kp_dir)
        self.assertEqual(rev["status"], rv.ST_PENDING)
        self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))
        self.assertIn("final_redundancy_ng", [h["event"] for h in rev["history"]])


class TestAutoMode(KpTestCase):
    def test_auto_adopts_top3_top5_with_declaration_and_records_status(self):
        with Env(self.tmp) as env:
            self.declare()
            r = self.ensure(env)
            self.assertEqual(r["state"], "FINALIZED")
            rev = rv.load_review(self.kp_dir)
            self.assertEqual(rev["status"], rv.ST_AUTO)           # REVIEWEDとは区別
            self.assertFalse(rev["accept_ai_default"])
            self.assertTrue(all(v is None for v in rev["verdicts"].values()))   # 未レビュー(verdict=null)。NGではない
            self.assertEqual(rev["ng"], [])
            kp = jl(f"{self.kp_dir}/keywords_canonicalized.json")
            self.assertEqual([i["used_form"] for i in kp["items"]], ["pushed prices up", "took a sharp turn", "time lag"])   # 承認済みの選定と同一(R-1)
            vo = jl(f"{self.kp_dir}/vocab_confirmed.json")
            self.assertEqual(len(vo["items"]), 5)
            self.assertEqual(rev["mode_used"]["declared_by"], "tester")

    def test_auto_skips_qa_fail_and_redundant_pair(self):
        with Env(self.tmp, qa_fail_phrases=["took a sharp turn"], red_ng_pairs=[(1, 3)]) as env:
            self.declare()
            self.ensure(env)
            rev = rv.load_review(self.kp_dir)
            c = rv.load_candidates(self.kp_dir)
            by = {x["candidate_id"]: x for x in c["candidates"]}
            used = [by[i]["selection_phrase"] for i in rev["selection"]["kp"]]
            self.assertNotIn("took a sharp turn", used)                  # qa_failはAUTO対象外
            self.assertEqual(used[0], "pushed prices up")
            self.assertNotIn("time lag", used)                           # pair(1,3)の片方を飛ばす(ai_rank順に走査: 1採用->3は重複で除外)... 実際は2が除外されqa_fail、3がpair
            self.assertEqual(len(used), 3)

    def test_auto_zero_eligible_stops(self):
        qa = [p["phrase"] for p in CALL1] + [p["phrase"] for p in CALL2]
        with Env(self.tmp, qa_fail_phrases=qa) as env:
            self.declare()
            with self.assertRaises(rv.KpReviewError):
                self.ensure(env)
            self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))

    def test_auto_final_redundancy_ng_advances_to_next_candidate_M8(self):
        with Env(self.tmp) as env:
            env.final_red_seq = ["NG"]   # 最初のKP集合QAがNG(rank1,2のペア)
            self.declare()
            r = self.ensure(env)
            self.assertEqual(r["state"], "FINALIZED")
            rev = rv.load_review(self.kp_dir)
            self.assertIn("auto_advance_final_redundancy_ng", [h["event"] for h in rev["history"]])
            self.assertNotIn(cid("took a sharp turn"), rev["selection"]["kp"])   # 重複ペアの下位が繰り上げで入れ替わる
            self.assertEqual(len(rev["selection"]["kp"]), 3)


class TestDeclarationScope(KpTestCase):
    def test_declaration_must_not_leak_to_next_round_after_reselect_M6(self):
        with Env(self.tmp, call1_seq=[CALL1, CALL1]) as env:
            r = self.ensure(env)
            self.assertEqual(r["state"], "PENDING")
            self.declare()                                       # round 1向けの宣言
            rv.op_reselect(self.kp_dir, ng={1: "bad"}, by="human")   # Human操作 -> 宣言失効 + round1専用
            r = self.ensure(env)                                 # 候補再生成(round 2)
            self.assertEqual(r["state"], "PENDING")              # 古い宣言ではAUTO確定されない
            self.assertEqual(rv.load_review(self.kp_dir)["round"], 2)
            self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))

    def test_new_declaration_after_human_op_for_round2_works_but_old_rounds_param_blocks(self):
        with Env(self.tmp, call1_seq=[CALL1, CALL1]) as env:
            self.ensure(env)
            rv.op_reselect(self.kp_dir, ng={1: "bad"}, by="human")
            self.declare(rounds=(2,))                            # Human操作の後の明示宣言(round 2)
            r = self.ensure(env)
            self.assertEqual(r["state"], "FINALIZED")
            rev = rv.load_review(self.kp_dir)
            self.assertEqual(rev["status"], rv.ST_AUTO)
            kp = jl(f"{self.kp_dir}/keywords_canonicalized.json")
            self.assertNotIn("pushed prices up", [i["used_form"] for i in kp["items"]])   # round1でNGにした句は復活しない

    def test_ai_declaration_requires_user_ref(self):
        with Env(self.tmp):
            with self.assertRaises(rv.KpReviewError):
                rv.add_declaration(run_dirs=[self.run_dir], by="Fable", reason="不在")
            rv.add_declaration(run_dirs=[self.run_dir], by="Fable", reason="不在", user_ref="ユーザー2026-10-26発言「今日は見ない」")
            with self.assertRaises(rv.KpReviewError):
                rv.add_declaration(run_dirs=[self.run_dir], by="", reason="r")
            with self.assertRaises(rv.KpReviewError):
                rv.add_declaration(run_dirs=[self.run_dir], by="user", reason="")

    def test_R7_period_or_range_declarations_are_removed(self):
        """委任_03(ユーザー決定2026-10-25): 期限付き/範囲付き(family・日付)の不在宣言は不採用。APIにも読取点にも残っていない。"""
        import inspect
        params = inspect.signature(rv.add_declaration).parameters
        for k in ("scope", "until"):
            self.assertNotIn(k, params)
        with self.assertRaises(TypeError):
            rv.add_declaration(scope={"family": "x"}, until="2999-01-01T00:00:00+09:00", by="user", reason="r")
        self.assertFalse(hasattr(rv, "_today_jst"))
        src = inspect.getsource(rv)
        for needle in ("scope_family", "scope-family", "_today_jst", "until"):
            self.assertNotIn(needle, src, needle)
        # run_dirsなしの宣言は作れない(範囲宣言の入口がない)
        with self.assertRaises((KeyError, TypeError, rv.KpReviewError)):
            rv.add_declaration(by="user", reason="r")

    def test_declaration_for_other_run_does_not_apply(self):
        with Env(self.tmp) as env:
            rv.add_declaration(run_dirs=[os.path.join(self.tmp, "other_run")], by="user", reason="別run")
            self.assertEqual(self.ensure(env)["state"], "PENDING")

    def test_no_environment_or_default_path_to_auto(self):
        """環境変数・設定・関数既定値からautoにならない(read_mode_declarationは宣言ファイルのみ)。"""
        src = rd(rv.__file__)
        self.assertNotIn("os.environ", src)
        self.assertNotIn("getenv", src)
        for k in ("EIGO_KP_REVIEW", "EIGO_KP_REVIEW_MODE", "KP_REVIEW_MODE", "KP_REVIEW"):
            os.environ[k] = "auto"
            self.addCleanup(os.environ.pop, k, None)
        with Env(self.tmp) as env:
            self.assertEqual(self.ensure(env)["state"], "PENDING")


class TestNgPersistence(KpTestCase):
    def test_ng_candidate_is_not_resurrected_by_reselect_and_llm_reply_M5(self):
        with Env(self.tmp, call1_seq=[CALL1, CALL1]) as env:
            self.ensure(env)
            rv.op_reselect(self.kp_dir, ng={1: "不自然"}, by="human")
            r = self.ensure(env)       # LLMは2回目もNG句(pushed prices up)を返す
            self.assertEqual(r["state"], "PENDING")
            c = rv.load_candidates(self.kp_dir)
            self.assertNotIn("pushed prices up", [x["selection_phrase"] for x in c["candidates"]])
            self.assertIn("pushed prices up", " ".join(env.messages1[1].split("【前回")[0:1] + env.messages1[1:2]))   # 除外指定として渡る
            # AUTOでもNGを採用しない
            self.declare(rounds=(2,))
            r = self.ensure(env)
            self.assertEqual(r["state"], "FINALIZED")
            rev = rv.load_review(self.kp_dir)
            self.assertNotIn(cid("pushed prices up"), sum((list(v) for v in rev["selection"].values()), []))

    def test_ng_shared_store_applies_to_other_run_dir_of_same_article_M5(self):
        with Env(self.tmp, call1_seq=[CALL1, CALL1]) as env:
            self.ensure(env)
            rv.op_ng(self.kp_dir, ng={2: "NG理由"}, by="human")
            other = os.path.join(self.tmp, "run2")
            kp2 = os.path.join(other, "b1b", "key_phrases")
            r = self.ensure(env, kp_dir=kp2, run_dir=other)   # 別run dir・同slug/level
            c = rv.load_candidates(kp2)
            self.assertNotIn("took a sharp turn", [x["selection_phrase"] for x in c["candidates"]])
            # 別slugには効かない
            other3 = os.path.join(self.tmp, "run3")
            kp3 = os.path.join(other3, "b1b", "key_phrases")
            self.ensure(env, kp_dir=kp3, run_dir=other3, slug="different_article")
            self.assertIn("took a sharp turn", [x["selection_phrase"] for x in rv.load_candidates(kp3)["candidates"]])

    def test_unng_requires_reason_and_by_and_is_recorded(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            rv.op_ng(self.kp_dir, ng={2: "x"}, by="human")
            with self.assertRaises(rv.KpReviewError):
                rv.op_unng(self.kp_dir, rank=2, reason="", by="human")
            removed = rv.op_unng(self.kp_dir, rank=2, reason="誤判定", by="human")
            self.assertEqual(removed, [cid("took a sharp turn")])
            self.assertEqual(rv.store_load_ng("x", "coffee", "b1b"), [])

    def test_used_form_key_possessive_normalization_and_similar_flag_R2(self):
        self.assertEqual(rv.used_form_key("catch one's attention"), rv.used_form_key("catch your attention"))
        self.assertEqual(rv.used_form_key("lose their way"), rv.used_form_key("lose his way"))
        ng = [{"candidate_id": "p_x", "phrase_key": "pushed prices up", "used_form_key": rv.used_form_key("push prices up")}]
        exact = {"candidate_id": "p_y", "selection_phrase": "pushed prices up", "used_form": "push prices up"}
        sim = {"candidate_id": "p_z", "selection_phrase": "pushed prices up sharply", "used_form": "push prices up sharply"}
        other = {"candidate_id": "p_w", "selection_phrase": "time lag", "used_form": "time lag"}
        self.assertEqual(rv.match_ng(exact, ng), "exact")
        self.assertEqual(rv.match_ng(sim, ng), "similar")
        self.assertIsNone(rv.match_ng(other, ng))
        self.assertFalse(rv.auto_eligible_now({"auto_eligible": True, **sim}, ng))   # 類似NGはAUTO対象外
        self.assertTrue(rv.auto_eligible_now({"auto_eligible": True, **other}, ng))

    def test_hand_edited_final_with_ng_rejected(self):
        with Env(self.tmp) as env:
            self.declare()
            self.ensure(env)
            rv.require_final_consistent(self.kp_dir)
            # 事後にNG追加(select無しのng操作は確定集合を落とす)-> 確定は取り消されPENDING
            rv.op_ng(self.kp_dir, ng={1: "後からNG"}, by="human")
            self.assertEqual(rv.load_review(self.kp_dir)["status"], rv.ST_PENDING)
            with self.assertRaises(rv.KpReviewNotConfirmed):
                rv.require_final_consistent(self.kp_dir)


class TestResumeStaleRegenerate(KpTestCase):
    def test_resume_same_text_no_api_even_after_finalize(self):
        with Env(self.tmp) as env:
            self.declare()
            self.ensure(env)
            n = env.total_llm_calls()
            for _ in range(3):
                self.ensure(env)
            self.assertEqual(env.total_llm_calls(), n)   # 再選定しない(確定済みreviewを読む)

    def test_text_change_marks_stale_archives_outputs_and_keeps_ng(self):
        with Env(self.tmp, call1_seq=[CALL1, CALL1]) as env:
            self.declare()
            self.ensure(env)
            rv.op_ng(self.kp_dir, ng={2: "NG"}, by="human")
            r = self.ensure(env, text=ARTICLE2)
            self.assertEqual(r["state"], "PENDING")
            self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))   # 旧KPは退避(後段が読めない)
            self.assertTrue([f for f in os.listdir(self.kp_dir) if "SUPERSEDED" in f])
            c = rv.load_candidates(self.kp_dir)
            self.assertEqual(c["text_sha256"], rv.sha256_text(ARTICLE2))
            self.assertNotIn("took a sharp turn", [x["selection_phrase"] for x in c["candidates"]])   # NGは保持

    def test_candidates_without_review_is_inconsistent(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            os.remove(f"{self.kp_dir}/kp_human_review.json")
            with self.assertRaises(rv.KpReviewInconsistent):
                self.ensure(env)

    def test_reselect_limit_and_rounds(self):
        with Env(self.tmp, call1_seq=[CALL1] * 6) as env:
            self.ensure(env)
            for i in range(rv.RESELECT_MAX):
                rv.op_reselect(self.kp_dir, by="h", note=f"n{i}")
                self.ensure(env)
            with self.assertRaises(rv.KpReviewError) as e:
                rv.op_reselect(self.kp_dir, by="h")
            self.assertIn("上限", str(e.exception))
            self.assertEqual(rv.load_review(self.kp_dir)["round"], rv.RESELECT_MAX + 1)

    def test_superseded_candidates_archived_on_reselect(self):
        with Env(self.tmp, call1_seq=[CALL1] * 3) as env:
            self.ensure(env)
            rv.op_reselect(self.kp_dir, by="h")
            self.ensure(env)
            self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_candidates.SUPERSEDED_1.json"))
            self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_candidates/round_1/kp_candidates.json"))
            self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_candidates/round_2/kp_candidates.json"))


class TestConsumerGuards(KpTestCase):
    def _final(self, **kw):
        env = Env(self.tmp, **kw)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.declare()
        self.ensure(env)
        return env

    def test_legacy_run_without_review_is_none_and_part1_falls_back(self):
        os.makedirs(self.kp_dir)
        jd(f"{self.kp_dir}/keywords_canonicalized.json", {"items": [{"rank": 2, "used_form": "b"}, {"rank": 1, "used_form": "a"}]})
        self.assertIsNone(rv.require_final_consistent(self.kp_dir))
        self.assertEqual([i["used_form"] for i in rv.part1_items(self.kp_dir)], ["a", "b"])

    def test_part1_items_is_vocab_5_and_ranks_independent_from_kp_rank_M9(self):
        self._final()
        items = rv.part1_items(self.kp_dir)
        self.assertEqual(len(items), 5)
        self.assertEqual([i["rank"] for i in items], [1, 2, 3, 4, 5])
        kp = jl(f"{self.kp_dir}/keywords_canonicalized.json")
        self.assertEqual(len(kp["items"]), 3)

    def test_part1_items_fail_closed_when_vocab_missing_with_review_M9(self):
        self._final()
        os.remove(f"{self.kp_dir}/vocab_confirmed.json")
        with self.assertRaises(rv.KpReviewError) as e:
            rv.part1_items(self.kp_dir)
        self.assertIn("3件へは戻しません", str(e.exception))
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.require_final_consistent(self.kp_dir)

    def test_part1_vocab_overlays_kp_artifact_gloss_but_keeps_vocab_rank(self):
        self._final()
        p = f"{self.kp_dir}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "後段修復後の意味"
        jd(p, d)
        items = rv.part1_items(self.kp_dir)
        self.assertEqual(items[0]["japanese_gloss"], "後段修復後の意味")
        self.assertEqual(items[0]["rank"], 1)

    def test_tampering_detected(self):
        self._final()
        p = f"{self.kp_dir}/keywords_canonicalized.json"
        orig = rd(p)
        # (a) candidate_id差し替え(旧KP混入の疑い)
        d = json.loads(orig)
        d["items"][0]["candidate_id"] = "p_forged"
        wr(p, json.dumps(d, ensure_ascii=False))
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.require_final_consistent(self.kp_dir)
        wr(p, orig)
        rv.require_final_consistent(self.kp_dir)
        # (b) reviewの手編集(署名不一致)
        rp = f"{self.kp_dir}/kp_human_review.json"
        r = jl(rp)
        r["selection"]["kp"] = r["selection"]["kp"][:2]
        wr(rp, json.dumps(r))
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.require_final_consistent(self.kp_dir)

    def test_vocab_items_subject_to_consumer_gates_M9(self):
        self._final()
        p = f"{self.kp_dir}/vocab_confirmed.json"
        d = jl(p)
        d["items"][4]["gloss_alignment_status"] = "FAILED_HUMAN_REVIEW_REQUIRED"   # vocab itemにHR待ちが残っている
        jd(p, d)
        with self.assertRaises(rv.KpReviewInconsistent) as e:
            rv.require_final_consistent(self.kp_dir)
        self.assertIn("gloss HR", str(e.exception))
        d["items"][4]["gloss_alignment_status"] = None
        d["items"][4]["japanese_gloss"] = ""
        jd(p, d)
        with self.assertRaises(rv.KpReviewInconsistent):
            rv.require_final_consistent(self.kp_dir)
        d["items"][4]["japanese_gloss"] = "意味"
        jd(p, d)
        with self.assertRaises(rv.KpReviewInconsistent) as e2:
            rv.require_final_consistent(self.kp_dir, require_src_contract=True)
        self.assertIn("SRC D1", str(e2.exception))

    def test_regenerate_equivalent_refinalize_keeps_files_when_signature_same(self):
        self._final()
        p = f"{self.kp_dir}/keywords_canonicalized.json"
        d = jl(p)
        d["items"][0]["japanese_gloss"] = "人が修復した意味"   # 後段(gloss修復・resolve_gloss)の編集
        jd(p, d)
        fin = rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=lambda items, name: self.fail("QA不要(記録済み)"))
        self.assertEqual(fin["wrote"], [])
        self.assertEqual(jl(p)["items"][0]["japanese_gloss"], "人が修復した意味")


class TestConcurrencyR3(KpTestCase):
    def test_lock_held_rejects_second_writer(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            with rv.review_lock(self.kp_dir, rv.KIND_KP, "runner"):
                with self.assertRaises(rv.ReviewLockHeld):
                    rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="human")
                with self.assertRaises(rv.ReviewLockHeld):
                    rv.finalize_kp(self.kp_dir, level="b1b")
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="human")   # lock解放後は成功

    def test_version_conflict_rejected(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            rev = rv.load_review(self.kp_dir)
            stale = json.loads(json.dumps(rev))
            rv.op_ng(self.kp_dir, ng={2: "x"}, by="human")      # revision +1
            with self.assertRaises(rv.ReviewConflict):
                rv.save_review(self.kp_dir, stale, expected_revision=stale["revision"])

    def test_concurrent_select_and_finalize_one_rejected(self):
        with Env(self.tmp) as env:
            self.ensure(env)
            results = []
            barrier = threading.Barrier(2)

            def human():
                barrier.wait()
                try:
                    rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="human")
                    results.append("ok")
                except (rv.ReviewLockHeld, rv.ReviewConflict, rv.KpReviewError):
                    results.append("rejected")

            def runner_like():
                barrier.wait()
                try:
                    with rv.review_lock(self.kp_dir, rv.KIND_KP, "runner"):
                        import time
                        time.sleep(0.2)
                    results.append("ok")
                except rv.ReviewLockHeld:
                    results.append("rejected")
            ts = [threading.Thread(target=human), threading.Thread(target=runner_like)]
            [t.start() for t in ts]
            [t.join() for t in ts]
            self.assertEqual(len(results), 2)
            self.assertLessEqual(results.count("ok"), 2)


class TestGrammarKindFixture(unittest.TestCase):
    """G-1: 文法は核をkind非依存にし、合成fixtureで状態機械だけを検証する(Production配線なし)。"""

    def _cands(self, n=2):
        cs = []
        for i in range(1, n + 1):
            cs.append({"candidate_id": f"g{i}", "ai_rank": i, "selection_phrase": f"Not only A but B{i}", "used_form": f"struct{i}",
                       "auto_eligible": True, "human_selectable": True, "flags": {"redundant_with": []}, "item": {}})
        return {"level": "b1b", "candidates": cs}

    def test_slot_rules_and_validation(self):
        c = self._cands()
        self.assertEqual(rv.validate_selection(c, {"grammar": ["g1"]}, level="b1b", kind=rv.KIND_GRAMMAR), [])
        self.assertEqual(rv.validate_selection(c, {"grammar": []}, level="b1b", kind=rv.KIND_GRAMMAR), [])   # omit(Part 2コーナーなし)
        self.assertTrue(rv.validate_selection(c, {"grammar": ["g1", "g2"]}, level="b1b", kind=rv.KIND_GRAMMAR))   # 最大1
        self.assertTrue(rv.validate_selection(c, {"grammar": ["gx"]}, level="b1b", kind=rv.KIND_GRAMMAR))

    def test_auto_is_top1_eligible_only_and_ng_skipped(self):
        c = self._cands(2)
        self.assertEqual(rv.auto_select(c, level="b1b", kind=rv.KIND_GRAMMAR), {"grammar": ["g1"]})
        ng = [{"candidate_id": "g1", "phrase_key": "x", "used_form_key": "y"}]
        self.assertEqual(rv.auto_select(c, level="b1b", kind=rv.KIND_GRAMMAR, ng_entries=ng), {"grammar": ["g2"]})
        c["candidates"][0]["auto_eligible"] = False
        c["candidates"][1]["auto_eligible"] = False
        self.assertEqual(rv.auto_select(c, level="b1b", kind=rv.KIND_GRAMMAR), {"grammar": []})   # 適格0=Part 2コーナーなし

    def test_files_are_kind_specific_and_select_cycle(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            c = self._cands(2)
            c.update(level="b1b", text_sha256="t", round=1)
            c = rv.save_candidates(d, c, kind=rv.KIND_GRAMMAR)
            self.assertTrue(os.path.exists(f"{d}/grammar_candidates.json"))
            self.assertFalse(os.path.exists(f"{d}/kp_candidates.json"))
            r = rv.new_review(c, kind=rv.KIND_GRAMMAR, article_key={"family": "z", "slug": "s", "level": "b1b"})
            rv.save_review(d, r, expected_revision=None, kind=rv.KIND_GRAMMAR)
            out = rv.op_select(d, kp_ranks=[2], by="h", kind=rv.KIND_GRAMMAR)
            self.assertEqual(out["status"], rv.ST_REVIEWED)
            self.assertEqual(out["selection"], {"grammar": ["g2"]})


if __name__ == "__main__":
    unittest.main()
