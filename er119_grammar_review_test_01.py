# -*- coding: utf-8 -*-
"""KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01 委任_03 / PART2-GRAMMAR-PRODUCTION-WIRING-01 委任_03:
文法Human Review(er119共通核 kind="grammar" + er119_grammar_review_01 + er120_part2_wiring_01)の単体/統合test。全てmock・API 0。
LLM由来関数はer120_part2_mock_01(決定論)をcounterで包む。実client生成は禁止(blockして失敗させる)。
"""
import json
import os
import unittest
from unittest import mock

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er119_kp_human_review_cli_01 as cli
import er119_kp_wiring_01 as kpw
import er119_test_support_01 as sup
import er120_part2_grammar_production_01 as g
import er120_part2_mock_01 as mk
import er120_part2_wiring_01 as p2w

PARAS = ["The old man walked slowly down the road. He was tired.",
         "It was a cold morning that day. Nobody spoke.",
         "Never had she seen such a thing before. Really.",
         "Under the bed lay a small box of letters.",
         "Nothing else happened that day at all."]
LABEL = "Test Story"
ROOT = os.path.dirname(os.path.abspath(__file__))


class Ctr:
    def __init__(self, fn):
        self.fn, self.n, self.prompts = fn, 0, []

    def __call__(self, prompt):
        self.n += 1
        self.prompts.append(prompt)
        return self.fn(prompt)


def zero_extract(prompt):
    return json.dumps({"features": [], "no_feature_paras": ["P1", "P2", "P3", "P4", "P5"]}), mk.MODEL, {"input_tokens": 1, "output_tokens": 1}, "z"


class GrammarCase(sup.KpTestCase):
    def setUp(self):
        super().setUp()
        self.sd = os.path.join(self.run_dir, "b1b", "study_text")
        self.ex, self.xp = Ctr(mk.mock_extract_call_fn), Ctr(mk.mock_explain_call_fn)
        p = mock.patch("er003_v1_b1_scaffold_01_generate.get_client", side_effect=AssertionError("real client must not be created (API 0)"))
        p.start()
        self.addCleanup(p.stop)

    def ensure(self, run_dir=None, sd=None, slug="coffee", ex=None, **kw):
        return gr.ensure_grammar_review(sd or self.sd, level="b1b", run_dir=run_dir or self.run_dir, family="x", slug=slug, paragraphs=PARAS, label=LABEL,
                                        extract_call_fn=ex or self.ex, **kw)

    def pregen(self, sd=None):
        """GRAMMAR-PREGEN-ALL-LEVELS-01: Step Bの唯一の呼出点(事前生成stage)。未確定=全候補、確定済み=選定済みidだけ。再実行はAPI 0。"""
        return p2w.pregen_stage(sd or self.sd, level="b1b", next_command="x", explain_call_fn=self.xp)

    def decide(self, choice, reason="理由あり", by="tester", sha=None, **kw):
        doc = gr.load_candidates(self.sd)
        if choice in ("top1", "top2", "omit", "pick") and doc["candidates"] and gr.load_review(self.sd)["schema"] == g.SCHEMA_REVIEW_V2:
            self.pregen()                     # 全候補の解説を見てから決める(v2)
        return gr.op_decide(self.sd, choice=choice, candidates_sha256=sha or doc["candidates_sha256"], reason=reason, by=by, **kw)

    def final(self, **kw):
        if gr.load_review(self.sd)["status"] in rv.FORWARD_STATUSES_BY_KIND["grammar"]:
            self.pregen()                     # 確定済み=選定済みidだけ(未生成のときのみ。済みならAPI 0)。finalize自体はLLM 0
        return p2w.finalize_stage(self.sd, level="b1b", paragraphs=PARAS, label=LABEL, **kw)

    def declare(self, rounds=(1,), by="tester", user_ref=""):
        return rv.add_declaration(run_dirs=[self.run_dir], by=by, reason="test", rounds=list(rounds), user_ref=user_ref, source="declare_absent_cli")


class TestWaitAndAuto(GrammarCase):
    def test_default_is_wait_rc4_material_and_rerun_is_api0(self):
        r = self.ensure()
        self.assertEqual(r["state"], "PENDING")
        self.assertEqual(r["review"]["status"], rv.ST_PENDING)
        self.assertEqual(self.ex.n, 1)
        self.assertTrue(os.path.exists(gr.paths(self.sd)["request"]))
        r2 = self.ensure()                                   # 再開: Step A''を呼ばない(M-7)
        self.assertEqual((r2["state"], self.ex.n, self.xp.n), ("PENDING", 1, 0))
        with self.assertRaises(g.Part2PendingReview):        # 待機中はfinalizeに進めない・出力を書かない
            self.final()
        self.assertFalse(os.path.exists(p2w.RESULT_PATH(self.sd)))
        self.assertEqual(self.xp.n, 0)

    def test_explicit_declaration_auto_adopts_top1_and_is_not_counted_as_reviewed(self):
        self.ensure()
        self.declare()
        r = self.ensure()
        self.assertEqual((r["state"], r["review"]["status"]), ("READY", rv.ST_AUTO))
        self.assertEqual(r["review"]["mode_declaration"]["source"], "declare_absent_cli")
        self.assertEqual(self.ex.n, 1)
        out = self.final()
        self.assertEqual(out["result"]["selection"]["source"], "auto_top1")
        self.assertEqual(self.xp.n, 1)
        s = g.summarize_review_statuses([r["review"]])
        self.assertEqual((s["reviewed"], s["unreviewed_auto_adopted"], s["human_reviewed"]), (0, 1, 0))
        out2 = self.final()                                  # 再開: Step B 0 call
        self.assertEqual((out2["reused"], self.xp.n), (True, 1))

    def test_ai_declaration_needs_user_ref_and_other_run_or_round_does_not_apply(self):
        with self.assertRaises(rv.KpReviewError):
            self.declare(by="Fable")
        self.declare(by="Fable", user_ref="ユーザー原文「Humanなし経路の検証」")
        self.assertEqual(self.ensure()["review"]["status"], rv.ST_AUTO)
        # 別run dirの宣言は効かない
        other = os.path.join(self.tmp, "run2")
        rv.add_declaration(run_dirs=[other], by="t", reason="r")
        self.assertEqual(self.ensure(run_dir=os.path.join(self.tmp, "run3"), sd=os.path.join(self.tmp, "run3", "b1b", "study_text"))["state"], "PENDING")
        # round 2には効かない
        self.setUp()
        self.ensure()
        self.decide("reselect")
        self.declare(rounds=(1,))
        self.assertEqual(self.ensure()["state"], "PENDING")

    def test_declaration_before_human_op_is_invalidated(self):
        self.ensure()
        self.declare()
        self.decide("top1", accept_ai=True)                   # Human操作 -> 以前の宣言は失効(以後のround/reselect後に効かない)
        self.decide("reselect")
        self.assertEqual(self.ensure()["state"], "PENDING")

    def test_string_auto_and_mode_dict_from_outside_are_refused(self):
        r = self.ensure()
        for bad in ("auto", {"mode": "auto"}, {"mode": "auto", "declared_by": "x", "declared_at": "t", "reason": "r", "source": "runner_arg"}):
            with self.assertRaises(g.Part2ReviewError):
                g.select_from_candidates(r["doc"], None, bad)

    def test_declaration_dict_shape_is_what_er120_accepts(self):
        self.ensure()
        self.declare()
        d = rv.read_mode_declaration(self.run_dir, level="b1b", review=gr.load_review(self.sd), round_no=1, cands_sha=gr.load_candidates(self.sd)["candidates_sha256"])
        self.assertEqual(g.normalize_mode(d)[0], "auto")
        self.assertEqual(tuple(rv.DECLARATION_SOURCES), tuple(g.AUTO_DECLARATION_SOURCES))     # er119とer120のsource集合が一致


class TestNoCandidateAndExhausted(GrammarCase):
    def test_zero_candidates_confirm_without_waiting_as_no_candidate_unreviewed(self):
        r = self.ensure(ex=Ctr(zero_extract))
        self.assertEqual((r["state"], r["review"]["status"]), ("READY", rv.ST_NO_CANDIDATE))
        out = self.final()
        self.assertEqual((out["result"]["status"], out["result"]["zero_reason"]), ("ZERO", "no_candidate"))
        self.assertEqual(self.xp.n, 0)
        s = g.summarize_review_statuses([r["review"]])
        self.assertEqual((s["reviewed"], s["no_candidate_unreviewed"]), (0, 1))
        self.assertIn(g.ZERO_P2, g.render_markdown(out["result"]))                    # 0件固定文面ZERO_P2
        p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")

    def _exhaust_by_ng(self):
        self.ensure()
        for _ in range(3):
            gr.op_ng(self.sd, rank=1, reason="NG理由", by="tester")
        return gr.load_candidates(self.sd)

    def test_exhausted_waits_even_with_declaration_and_omit_gives_human_rejected_all(self):
        doc = self._exhaust_by_ng()
        self.assertTrue(doc["exhausted"])
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_RESELECT_EXHAUSTED)
        self.declare()
        r = self.ensure()
        self.assertEqual((r["state"], r["review"]["status"]), ("PENDING", rv.ST_RESELECT_EXHAUSTED))       # 自動ZEROにしない(M-5(c))
        self.assertEqual(g.review_request(doc)["choices"], ["omit", "reextract"])
        with self.assertRaises(g.Part2ReviewError):                                                         # 理由必須
            self.decide("omit", reason="")
        rec = self.decide("omit")
        self.assertEqual((rec["status"], rec["selection"]["zero_reason"]), (rv.ST_REVIEWED, "human_rejected_all"))
        out = self.final()
        self.assertEqual(out["result"]["zero_reason"], "human_rejected_all")
        p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")

    def test_reextract_calls_step_a_once_and_ng_are_not_resurrected(self):
        self._exhaust_by_ng()
        rec = self.decide("reextract")
        self.assertEqual(rec["status"], rv.ST_REEXTRACT_REQUESTED)
        with self.assertRaises(p2w.Part2NotConfirmed):                                                       # 再抽出待ちは下流fail-closed
            p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")
        n0 = self.ex.n
        r = self.ensure()                                                                                    # 次回起動: Step A'' 1 call
        self.assertEqual(self.ex.n, n0 + 1)
        self.assertEqual(r["doc"]["candidates"], [])
        self.assertTrue(r["doc"]["exhausted"])                                                               # 同じ候補はNGで戻らない
        self.assertEqual(r["doc"]["reextract_count"], 1)
        self.assertEqual(r["review"]["status"], rv.ST_RESELECT_EXHAUSTED)
        self.assertEqual(g.review_request(r["doc"])["choices"], ["omit"])                                    # 再抽出は最大1回
        self.assertEqual(self.ensure()["state"], "PENDING")
        self.assertEqual(self.ex.n, n0 + 1)


class TestHumanOps(GrammarCase):
    def test_top1_accept_ai_top2_requires_reason_and_stale_sha_refused(self):
        self.ensure()
        with self.assertRaises(g.Part2ReviewError):
            self.decide("top2", reason="")
        with self.assertRaises(g.Part2ReviewError):
            self.decide("top1", sha="0" * 64)
        with self.assertRaises(g.Part2ReviewError):
            self.decide("top2", accept_ai=True)
        with self.assertRaises(rv.KpReviewError):
            self.decide("top1", by="")
        rec = self.decide("top2")
        self.assertEqual((rec["status"], rec["selection"]["choice"], rec["decision"]["choice"]), (rv.ST_REVIEWED, "pick", "top2"))   # v2: 選択はpickに正規化、入力のtop2はdecisionに記録
        self.assertEqual(rec["verdicts"][g.candidate_id("P1", PARAS[0].split(". ")[0] + ".")], "NOT_SELECTED")
        out = self.final()
        self.assertEqual(out["result"]["selection"]["source"], "human_top2")
        res = p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")
        self.assertEqual([i["selection"]["candidate_id"] for i in res["items"]], rec["selection"]["candidate_ids"])   # v2結果はitems[]

    def test_post_hoc_review_makes_old_result_stale_and_stage_sha_changes(self):
        self.ensure()
        self.decide("top1", accept_ai=True)
        r1 = gr.load_review(self.sd)
        self.final()
        sha1 = g.final_stage_input_sha(PARAS, LABEL, r1)
        self.decide("top2")
        r2 = gr.load_review(self.sd)
        self.assertNotEqual(g.final_stage_input_sha(PARAS, LABEL, r2), sha1)                   # Z part2_b1bのinput_sha: 確定が変わると変わる
        with self.assertRaises(g.Part2Stale):                                                  # 旧結果(top1)は拒否
            p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")
        self.final()                                                                           # 再finalize(Step A''なし)
        self.assertEqual(self.ex.n, 1)
        p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")

    def test_reselect_registers_ng_in_shared_registry_and_copy_run_inherits(self):
        self.ensure()
        rec = self.decide("reselect", reason="TOP1もTOP2も不自然")
        self.assertEqual(rec["status"], rv.ST_PENDING)
        self.assertEqual(rec["reselect_count"], 1)
        doc = gr.load_candidates(self.sd)
        self.assertEqual(len(doc["candidates"]), 1)                                            # 次順位が新TOP1
        self.assertEqual(len(doc["ng"]), 2)
        reg = rv.store_load_ng("x", "coffee", "b1b", "grammar")
        self.assertEqual(len(reg), 2)
        self.assertEqual(rv.store_load_ng("x", "coffee", "b1b"), [])                           # KPのregistryとは別file
        self.assertEqual(rv.store_load_ng("x", "other", "b1b", "grammar"), [])                 # 別slugには効かない
        # copy-run(別run dir・同slug): 新規抽出でもNGがskipされる(R2の見立て)
        run2 = os.path.join(self.tmp, "run2")
        r2 = self.ensure(run_dir=run2, sd=os.path.join(run2, "b1b", "study_text"))
        sent_ng = {e["sentence"] for e in doc["ng"]}
        self.assertTrue(sent_ng.isdisjoint({c["sentence"] for c in r2["doc"]["candidates"]}))
        self.assertEqual(len(r2["doc"]["candidates"]), 1)
        self.assertEqual(len(r2["doc"]["filtered_by_ng"]), 2)
        # AUTOでもNGを採用しない
        rv.add_declaration(run_dirs=[run2], by="t", reason="r")
        r3 = self.ensure(run_dir=run2, sd=os.path.join(run2, "b1b", "study_text"))
        self.assertEqual(r3["review"]["status"], rv.ST_AUTO)
        self.assertNotIn(r3["doc"]["candidates"][0]["sentence"], sent_ng)

    def test_reselect_limit_two_and_reason_required(self):
        self.ensure()
        with self.assertRaises(g.Part2ReviewError):
            self.decide("reselect", reason="")
        self.decide("reselect")
        self.decide("reselect")                                                                # 2回目で候補が尽きる
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_RESELECT_EXHAUSTED)
        with self.assertRaises((g.Part2ReviewError, g.Part2Error)):
            self.decide("reselect")
        with self.assertRaises(g.Part2Error):                                                  # 再選定合計2回に達したので再抽出も不可
            self.decide("reextract")

    def test_ng_unng_records_and_unng_does_not_resurrect_in_current_list(self):
        self.ensure()
        c1 = gr.load_candidates(self.sd)["candidates"][0]
        gr.op_ng(self.sd, rank=1, reason="不自然", by="tester")
        self.assertEqual(len(gr.load_candidates(self.sd)["candidates"]), 2)
        with self.assertRaises(rv.KpReviewError):
            gr.op_unng(self.sd, sentence=c1["sentence"], reason="", by="tester")
        removed = gr.op_unng(self.sd, sentence=c1["sentence"], reason="誤NG", by="tester")
        self.assertEqual(removed, [c1["candidate_id"]])
        self.assertEqual(rv.store_load_ng("x", "coffee", "b1b", "grammar"), [])
        self.assertEqual(len(gr.load_candidates(self.sd)["candidates"]), 2)                    # 現在のlistには戻らない

    def test_concurrent_registry_write_is_refused_by_lock(self):
        with rv.store_lock("x", "coffee", "b1b", "grammar", "other"):
            with self.assertRaises(rv.ReviewLockHeld):
                rv.store_add_ng("x", "coffee", "b1b", {"candidate_id": "g1", "sentence": "s"}, "grammar")
        with rv.review_lock(self.sd, "grammar", "other"):
            self.ensure() if False else None
            with self.assertRaises(rv.ReviewLockHeld):
                with rv.review_lock(self.sd, "grammar", "me"):
                    pass

    def test_new_ng_in_registry_supersedes_confirmed_review(self):
        self.ensure()
        self.decide("top1", accept_ai=True)
        reg = gr.load_candidates(self.sd)["candidates"][0]
        rv.store_add_ng("x", "coffee", "b1b", dict(g.ng_entry_from_candidate(reg, reason="別runでNG", by="t"), sentence_key=g._norm_sentence(reg["sentence"])), "grammar")
        r = self.ensure()
        self.assertEqual((r["state"], r["review"]["status"]), ("PENDING", rv.ST_PENDING))      # 確定は古い候補docに対するものなので取り消し(新review)
        self.assertEqual(self.ex.n, 1)
        self.assertTrue(any(f.endswith(".json") and "SUPERSEDED" in f for f in os.listdir(self.sd)))


class TestSignatureAndConsumers(GrammarCase):
    def test_signature_single_source_core_and_er120(self):
        self.ensure()
        rec = self.decide("top1", accept_ai=True)
        self.assertEqual(rec["selection_signature"], g.grammar_selection_signature(rec))
        self.assertEqual(rv.selection_signature(rec), g.grammar_selection_signature(rec))
        self.assertEqual(os.path.normpath(rv.paths(self.sd, "grammar")["candidates"]), os.path.normpath(os.path.join(self.sd, g.CANDIDATES_FILENAME)))

    def test_wait_statuses_are_fail_closed_for_consumers(self):
        self.ensure()
        for st in rv.GRAMMAR_WAIT_STATUSES:
            r = gr.load_review(self.sd)
            r["status"] = st
            gr._atomic_json(gr.paths(self.sd)["review"], r)
            with self.assertRaises(g.Part2Stale):
                p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")
            with self.assertRaises(g.Part2PendingReview):
                self.final()
        self.assertEqual(set(rv.FORWARD_STATUSES_BY_KIND["grammar"]), set(g.ALLOWED_REVIEW_STATUSES))

    def test_hand_edited_review_or_candidates_is_detected(self):
        self.ensure()
        self.decide("top1", accept_ai=True)
        self.final()
        r = gr.load_review(self.sd)
        r["selection"]["candidate_ids"] = ["gxxxx"]
        gr._atomic_json(gr.paths(self.sd)["review"], r)
        with self.assertRaises(g.Part2Stale):
            p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")

    def test_missing_artifacts_fail_closed(self):
        with self.assertRaises(g.Part2Stale):
            p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")
        self.ensure()
        with self.assertRaises(p2w.Part2NotConfirmed):
            p2w.require_final(self.sd, PARAS, LABEL, level="b1b", next_command="x")

    def test_inconsistent_candidates_without_review_is_refused(self):
        self.ensure()
        os.remove(gr.paths(self.sd)["review"])
        with self.assertRaises(rv.KpReviewInconsistent):
            self.ensure()

    def test_verify_outputs_md_and_html(self):
        self.ensure()
        self.decide("top1", accept_ai=True)
        out = self.final()
        res = out["result"]
        md = os.path.join(self.sd, f"{g.PART2_FILE_STEM}.md")
        html_ok = p2w.compose_page_html("<section class='study'>P1</section>", res)
        p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x", md_path=md, html_text=html_ok)
        with self.assertRaises(g.Part2Stale):
            p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x", md_path=md, html_text="<html>none</html>")
        self.assertIn("<style>", p2w.compose_page_html("", res))                               # Part 1が空ならCSSを含める(R-1)
        self.assertNotIn("<style>", p2w.compose_page_html("<section>x</section>", res))


class TestUnifiedPending(GrammarCase):
    def test_kp_and_grammar_pending_make_one_request_and_one_banner(self):
        r = self.ensure()
        kp_req = os.path.join(self.run_dir, "b1b", "key_phrases", "kp_human_review_request.md")
        os.makedirs(os.path.dirname(kp_req), exist_ok=True)
        with open(kp_req, "w", encoding="utf-8") as f:
            f.write("# KP依頼 round 1\n本文KP\n")
        pend = [{"level": "b1b", "request_md": kp_req}, r["pending"]]
        banner = kpw.pending_banner(pend, restart_command="py runner --stage all", run_dir=self.run_dir)
        uni = os.path.join(self.run_dir, "review_request.md")
        self.assertTrue(os.path.exists(uni))
        txt = open(uni, encoding="utf-8").read()
        self.assertIn("# KP依頼 round 1", txt)
        self.assertIn("Part 2 文法解説 Human Review 依頼", txt)
        self.assertEqual(banner.count(rv.PENDING_MARKER), 1)
        self.assertEqual(banner.count("再開コマンド"), 1)
        self.assertIn("文法(Part 2) + KP", banner)


class TestCli(GrammarCase):
    def run_cli(self, argv):
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = cli.run(argv)
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue(), err.getvalue()

    def test_two_ids_pick_and_all_candidates_flag_are_refused_by_cli(self):
        self.ensure()
        self.pregen()
        sha = gr.load_candidates(self.sd)["candidates_sha256"]
        ids = [c["candidate_id"] for c in gr.load_candidates(self.sd)["candidates"]]
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "pick", "--ids", f"{ids[0]},{ids[1]}",
                                     "--candidates-sha", sha, "--reason", "2件", "--by", "t"])
        self.assertEqual(rc, 2)                                                                   # 2件同時選択は禁止
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "pick", "--ids", ids[2],
                                     "--candidates-sha", sha, "--reason", "3位", "--by", "t"])
        self.assertEqual(rc, 2)                                                                   # Top1/Top2以外は選べない
        with self.assertRaises(SystemExit):                                                       # 旧 --all-candidates は撤去(argparseが拒否)
            cli.run(["grammar-pregen", "--run", self.run_dir, "--level", "b1b", "--all-candidates"])

    def test_status_show_select_ng_unng_and_refusals(self):
        self.ensure()
        self.pregen()                                              # v2: 解説の事前生成が済んでから提示・選択できる
        rc, out, err = self.run_cli(["status", "--run", self.run_dir])
        self.assertEqual(rc, 0, err)
        j = json.loads(out)
        self.assertEqual([os.path.normpath(x) for x in j["grammar_pending"]], [os.path.normpath(self.sd)])
        rc, out, err = self.run_cli(["grammar-show", "--run", self.run_dir, "--level", "b1b"])
        self.assertEqual(rc, 0, err)
        self.assertIn("AI推奨(Top1)", out)                              # v2: Top1/Top2の文法名+解説全文を順位順に提示
        self.assertIn("Top2:", out)
        self.assertIn("他1件は非表示", out)                               # 3位以降は非表示(件数のみ)
        self.assertIn("学習ページに載る全文", out)
        sha = gr.load_candidates(self.sd)["candidates_sha256"]
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "top2", "--candidates-sha", sha, "--by", "t"])   # reason無し
        self.assertEqual(rc, 2)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)                     # 拒否時は状態不変
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "top1", "--accept-ai", "--candidates-sha", "0" * 64, "--by", "t"])
        self.assertEqual(rc, 2)
        rc, out, err = self.run_cli(["grammar-ng", "--run", self.run_dir, "--level", "b1b", "--rank", "1", "--reason", "x", "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.pregen()                                              # NG後の新候補一覧の解説を事前生成(再実行相当)
        sha = gr.load_candidates(self.sd)["candidates_sha256"]
        rc, out, err = self.run_cli(["grammar-select", "--run", self.run_dir, "--level", "b1b", "--choice", "top1", "--accept-ai", "--candidates-sha", sha, "--by", "t"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_REVIEWED)
        self.assertTrue(gr.load_review(self.sd)["accept_ai_default"])
        rc, out, err = self.run_cli(["grammar-unng", "--run", self.run_dir, "--level", "b1b", "--sentence", PARAS[0].split(". ")[0] + ".", "--reason", "誤NG", "--by", "t"])
        self.assertEqual(rc, 0, err)

    def test_r7_scoped_and_dated_declarations_are_gone(self):
        for argv in (["declare-absent", "--scope-family", "x", "--scope-date", "2099-01-01", "--reason", "r", "--by", "u"],
                     ["declare-absent", "--runs", self.run_dir, "--until", "2099-01-01T00:00:00+09:00", "--reason", "r", "--by", "u"]):
            rc, out, err = self.run_cli(argv)
            self.assertEqual(rc, 2, argv)
        rc, out, err = self.run_cli(["declare-absent", "--reason", "r", "--by", "u"])             # --runs必須
        self.assertEqual(rc, 2)
        import inspect
        params = set(inspect.signature(rv.add_declaration).parameters)
        self.assertTrue(params.isdisjoint({"scope", "until"}))
        src = open(os.path.join(ROOT, "er119_kp_human_review_01.py"), encoding="utf-8").read()
        for gone in ("scoped_declarations_dir", "_today_jst", "範囲宣言"):
            self.assertNotIn(gone, src.replace("範囲宣言は不採用", ""))
        self.assertEqual(sorted(os.listdir(os.path.join(self.tmp))), ["run1"] if os.path.isdir(os.path.join(self.tmp, "run1")) else sorted(os.listdir(self.tmp)))


class TestStaticBoundaries(unittest.TestCase):
    def _src(self, name):
        with open(os.path.join(ROOT, name), encoding="utf-8", errors="ignore") as f:
            return f.read()

    def test_runners_have_no_path_to_build_auto_mode_dict(self):
        """M-3: runner引数・hooks・環境変数からauto宣言dictを組み立てる経路をrunner側に作らない(宣言は read_mode_declaration[宣言ファイル]だけ)。"""
        for name in ("er019_family_x_audio_production_runner_01.py", "er026_family_z_fiction_production_runner_01.py", "er062_family_z_writer_01.py",
                     "er120_part2_wiring_01.py", "er119_grammar_review_01.py", "er119_kp_wiring_01.py"):
            s = self._src(name)
            for pat in ('"mode": "auto"', "'mode': 'auto'", 'mode="auto"', "mode='auto'", "normalize_mode("):
                self.assertNotIn(pat, s, f"{name}: {pat}")
            if name in ("er120_part2_wiring_01.py", "er119_grammar_review_01.py", "er119_kp_wiring_01.py"):
                for pat in ("os.environ", "getenv"):
                    self.assertNotIn(pat, s, f"{name}: {pat}")
            else:   # 既存runnerは他用途でenvironを使う。レビュー/宣言/Part 2に関するenv読取りが無いことだけを確認する
                import re
                self.assertIsNone(re.search(r"(environ|getenv)[^\n]*(KP_REVIEW|kp_review|REVIEW_MODE|GRAMMAR|PART2)", s, re.I), name)
        self.assertEqual(self._src("er119_grammar_review_01.py").count("decl = rv.read_mode_declaration("), 1)   # 文法側の読取点は共通核の単一関数だけ
        self.assertEqual(self._src("er119_kp_human_review_01.py").count("def read_mode_declaration("), 1)

    def test_public_builder_and_standard_never_call_part2(self):
        """R-2: Part 2の描画はcompose_page_html(=compose_study_html)だけ。Standard(a2)側の関数・ページからは呼ばない。"""
        x = self._src("er019_family_x_audio_production_runner_01.py")
        z = self._src("er026_family_z_fiction_production_runner_01.py")
        self.assertEqual(x.count("compose_page_html("), 1)
        self.assertEqual(z.count("compose_page_html("), 1)
        for s in (x, z):
            self.assertNotIn("render_html_block(_p2", s)
        for name, body_re in (("er019_family_x_audio_production_runner_01.py", "def generate_family_x_a2_segments"),
                              ("er019_family_x_audio_production_runner_01.py", "def stage_assemble_family_x_a2")):
            s = self._src(name)
            seg = s[s.index(body_re):s.index(body_re) + 6000]
            self.assertNotIn("part2", seg.lower().split("\ndef ")[0])

    def test_grammar_files_not_tracked_dirs(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "er119_output")), "テストが実リポジトリのstore(er119_output/)へ書いた")


if __name__ == "__main__":
    unittest.main()
