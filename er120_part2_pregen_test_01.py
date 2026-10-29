# -*- coding: utf-8 -*-
"""GRAMMAR-PREGEN-ALL-LEVELS-01 委任_02(F-8核): 文法解説の事前生成(全level共通の核)のtest。全てmock・API 0(実client生成はblock)。
対象: pregen stage / Step B呼出点の単一化 / legacy_postselect限定とINTEGRITY / Part 1訳との食い違いISSUEと了承 / level必須(b1bの暗黙既定値の撤去) /
      review v2(2026-10-27文法選定仕様: Top1/Top2のみ提示・原則1件・0件可・2件禁止・冪等) / result v2(1件はv1とバイト同一) / 3位以降は非表示・事前生成しない / 失敗再開 / Prompt sha不変 / 既定の待機(rc=4)維持 /
      節単位4者一致 / フォーム用データのfail-closed。
テスト計画: docs/research/GRAMMAR-PREGEN-ALL-LEVELS-01/TEST_PLAN_02.md
"""
import hashlib
import inspect
import json
import os
import re
import unittest
from unittest import mock

import er119_grammar_review_01 as gr
import er119_kp_human_review_01 as rv
import er119_test_support_01 as sup
import er120_part2_grammar_production_01 as g
import er120_part2_mock_01 as mk
import er120_part2_wiring_01 as p2w

ROOT = os.path.dirname(os.path.abspath(__file__))
PARAS = ["The old man walked slowly down the road. He was tired.",
         "It was a cold morning that day. Nobody spoke.",
         "Never had she seen such a thing before. Really.",
         "Under the bed lay a small box of letters.",
         "Nothing else happened that day at all."]
LABEL = "Test Story"
STEPA_SHA = "51912fe1e2428c347c09969f2f3e8831c73782d5669921e6508c15de8855e15c"   # 本委任前(HEAD)のsha。Prompt本文は無変更であること
STEPB_SHA = "59588b5961e88d1be052e9ae5045ed90ca243546d6996027b60336e3083b591c"
AUTO = {"mode": "auto", "declared_by": "tester", "declared_at": "2026-10-27T00:00:00+0900", "reason": "unit test", "source": "declare_absent_cli"}


class Ctr:
    def __init__(self, fn):
        self.fn, self.n, self.prompts = fn, 0, []

    def __call__(self, prompt):
        self.n += 1
        self.prompts.append(prompt)
        return self.fn(prompt)


def _usage():
    return {"input_tokens": 10, "output_tokens": 10}


def many_extract(n):
    """n個の適格候補(P1..Pn。各段落に1文)を返すStep A''のmock。"""
    def fn(prompt):
        feats = [{"para": f"P{i}", "sentence": f"Sentence number {i} was written here today.", "feature_class": "CLEFT", "front_kind": "", "misread_target": "SUBJECT",
                  "misread_quote": "Sentence", "misread_ja": "x", "omitted_words": "", "basic_only": False, "teaching_value": "HIGH", "teaching_value_ja": "読み方",
                  "construct_ja": f"構文{i}", "points_ja": ["p"], "context_ja": "ctx"} for i in range(1, n + 1)]
        return json.dumps({"features": feats, "no_feature_paras": []}, ensure_ascii=False), mk.MODEL, _usage(), "many"
    return fn


def zero_extract(prompt):
    return json.dumps({"features": [], "no_feature_paras": ["P1"]}), mk.MODEL, _usage(), "z"


class PCase(sup.KpTestCase):
    def setUp(self):
        super().setUp()
        self.sd = os.path.join(self.run_dir, "b1b", "study_text")
        self.sd_a2 = os.path.join(self.run_dir, "a2", "study_text")
        self.ex, self.xp = Ctr(mk.mock_extract_call_fn), Ctr(mk.mock_explain_call_fn)
        p = mock.patch("er003_v1_b1_scaffold_01_generate.get_client", side_effect=AssertionError("real client must not be created (API 0)"))
        p.start()
        self.addCleanup(p.stop)
        self.callers = []
        orig = g.generate_explanation

        def spy(*a, **k):
            self.callers.append(inspect.stack()[1].function)      # Step Bの呼出元(単一呼出点の証明)
            return orig(*a, **k)
        p2 = mock.patch.object(g, "generate_explanation", spy)
        p2.start()
        self.addCleanup(p2.stop)

    def ensure(self, level="b1b", sd=None, paras=PARAS, ex=None, slug="coffee", run_dir=None):
        sd = sd or (self.sd if level == "b1b" else self.sd_a2)
        return gr.ensure_grammar_review(sd, level=level, run_dir=run_dir or self.run_dir, family="x", slug=slug, paragraphs=paras, label=LABEL,
                                        extract_call_fn=ex or self.ex)

    def pregen(self, level="b1b", sd=None, xp=None, **kw):
        sd = sd or (self.sd if level == "b1b" else self.sd_a2)
        return p2w.pregen_stage(sd, level=level, next_command="rerun", explain_call_fn=xp or self.xp, **kw)

    def prepare(self, level="b1b", **kw):
        r = self.ensure(level=level, **kw)
        self.pregen(level=level, sd=kw.get("sd"))
        return r

    def decide(self, choice, sd=None, reason="理由あり", by="tester", **kw):
        sd = sd or self.sd
        doc = gr.load_candidates(sd)
        return gr.op_decide(sd, choice=choice, candidates_sha256=doc["candidates_sha256"], reason=reason, by=by, **kw)

    def final(self, level="b1b", sd=None, paras=PARAS, **kw):
        sd = sd or (self.sd if level == "b1b" else self.sd_a2)
        return p2w.finalize_stage(sd, level=level, paragraphs=paras, label=LABEL, **kw)

    def req(self, level="b1b", sd=None, paras=PARAS, **kw):
        sd = sd or (self.sd if level == "b1b" else self.sd_a2)
        return p2w.require_final(sd, paras, LABEL, level=level, next_command="x", **kw)

    def ids(self, sd=None):
        return [c["candidate_id"] for c in gr.load_candidates(sd or self.sd)["candidates"]]


class T1_DefaultWait(PCase):
    def test_default_is_wait_rc4_until_human_decides_and_pregen_precedes_the_wait(self):
        r = self.ensure()
        self.assertEqual((r["state"], r["review"]["schema"], r["review"]["status"]), ("PENDING", g.SCHEMA_REVIEW_V2, rv.ST_PENDING))
        self.assertEqual(self.xp.n, 0)                                                     # candidate_stageはStep Bを呼ばない
        self.assertIn("古い/未完成", open(gr.paths(self.sd)["request"], encoding="utf-8").read())    # 事前生成前の依頼書は『未完成』(解説なしで選ばせない)
        with self.assertRaises(rv.KpReviewError):                                          # 解説の事前生成なしでは決められない
            self.decide("top1")
        pre = self.pregen()
        self.assertEqual((len(pre["generated"]), self.xp.n, pre["confirmed"]), (2, 2, False))    # Top1/Top2の2候補分だけ(3位は生成しない)
        self.assertEqual(len(pre["skipped_over_cap"]), 1)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)                  # 自動確定しない
        with self.assertRaises(p2w.Part2NotConfirmed):                                     # 使う側は待機(rc=4)
            self.req()
        with self.assertRaises(g.Part2PendingReview):
            self.final()
        self.assertFalse(os.path.exists(p2w.RESULT_PATH(self.sd)))
        txt = open(gr.paths(self.sd)["request"], encoding="utf-8").read()
        cs = gr.load_candidates(self.sd)["candidates"]
        for c in cs[:2]:                                                                   # Top1/Top2の文法名+解説全文
            self.assertIn(c["construct_ja"], txt)
        self.assertNotIn(cs[2]["construct_ja"], txt)                                       # 3位以降は非表示
        self.assertIn("他1件は非表示", txt)
        self.assertIn("これはmockの日本語訳です", txt)
        self.assertNotIn("古い/未完成", txt)


class T2_StepBSingleCallSite(PCase):
    def test_step_b_only_from_pregen_and_counts_are_fixed(self):
        self.prepare()
        self.assertEqual(self.xp.n, 2)
        self.pregen()                                                                       # 再実行=API 0
        self.assertEqual(self.xp.n, 2)
        self.decide("pick", ids=[self.ids()[0]], accept_ai=True)
        out = self.final()
        self.req()
        self.final()
        self.assertEqual((self.xp.n, out["path"]), (2, "v2"))                              # finalize/require/再finalizeはLLM 0
        self.assertEqual(set(self.callers), {"pregen_explanations"})
        # 候補が変わっても(reselect)既存の同一候補は再生成しない: 確定前の別run
        sd2 = os.path.join(self.tmp, "run2", "b1b", "study_text")
        self.ensure(sd=sd2, run_dir=os.path.join(self.tmp, "run2"))
        n0 = self.xp.n
        self.pregen(sd=sd2)
        self.assertEqual(self.xp.n, n0 + 2)                                                 # 別studyは別途2(Top1/Top2。共有キャッシュは持たない)

    def test_static_single_call_site_and_finalize_has_no_llm_parameters(self):
        src = open(os.path.join(ROOT, "er120_part2_grammar_production_01.py"), encoding="utf-8").read()
        self.assertEqual(len(re.findall(r"generate_explanation\(", src)), 2)               # 定義 + pregen_explanations内の呼出1か所
        for name in ("er120_part2_wiring_01.py", "er119_grammar_review_01.py"):
            self.assertNotIn("generate_explanation(", open(os.path.join(ROOT, name), encoding="utf-8").read(), name)
        for fn in (p2w.finalize_stage, g.finalize_part2_v2):
            params = set(inspect.signature(fn).parameters)
            self.assertTrue(params.isdisjoint({"explain_call_fn", "client", "budget_guard", "extract_call_fn", "call_fn"}), fn.__name__)

    def test_finalize_without_pregen_fails_closed_without_api(self):
        self.ensure()
        rv.add_declaration(run_dirs=[self.run_dir], by="t", reason="r")
        self.assertEqual(self.ensure()["review"]["status"], rv.ST_AUTO)
        with self.assertRaises(g.Part2Stale):                                              # 事前生成物なし(v2成果物もなし)=黙って生成しない
            self.final()
        self.assertEqual(self.xp.n, 0)


class T3_LegacyAndIntegrity(PCase):
    def _make_v1(self, write_result=True):
        ex, xp = Ctr(mk.mock_extract_call_fn), Ctr(mk.mock_explain_call_fn)
        r = g.run_part2(PARAS, LABEL, level="b1b", mode=AUTO, extract_call_fn=ex, explain_call_fn=xp)       # 旧フロー(選定後にStep B)で作ったv1成果物
        self.assertEqual((r["review_record"]["schema"], r["result"]["schema"], xp.n), (g.SCHEMA_REVIEW, g.SCHEMA_RESULT, 1))
        gr.save_candidates_doc(self.sd, r["candidates"])
        rec = dict(r["review_record"], article_key={"family": "x", "slug": "coffee", "level": "b1b"}, round=1, decision=None)
        with rv.review_lock(self.sd, "grammar", "t"):
            rv.save_review(self.sd, rec, expected_revision=None, kind="grammar")
        if write_result:
            g.write_artifacts(self.sd, None, r["result"])
        return r

    def test_legacy_postselect_is_review_v1_and_result_v1_only_and_reuses_without_stepb(self):
        r = self._make_v1()
        out = self.final()
        self.assertEqual((out["path"], out["reused"], out["result"]["schema"]), ("legacy_v1", True, g.SCHEMA_RESULT))
        self.assertEqual(self.req()["schema"], g.SCHEMA_RESULT)
        self.assertEqual(self.xp.n, 0)
        p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x", md_path=os.path.join(self.sd, f"{g.PART2_FILE_STEM}.md"),
                           html_text=g.render_html_block(r["result"], include_css=False))

    def test_v1_confirmed_without_result_pregens_selected_id_only_as_stepB_generated(self):
        self._make_v1(write_result=False)
        with self.assertRaises(g.Part2Stale):                                              # 事前生成物なし=その場で生成しない(INTEGRITYではなくStale)
            self.final()
        self.assertNotIsInstance(self._exc(lambda: self.final()), g.Part2IntegrityError)
        pre = self.pregen()
        self.assertEqual((len(pre["generated"]), self.xp.n, pre["confirmed"]), (1, 1, True))   # 選定済みid(TOP1)だけ。未選択候補へ課金しない
        ex = gr.load_explanations(self.sd)
        self.assertEqual([i["source"] for i in ex["items"]], ["stepB_generated"])          # ユーザー未閲覧と明示
        out = self.final()
        self.assertEqual((out["path"], out["result"]["schema"], gr.load_review(self.sd)["schema"]), ("v2", g.SCHEMA_RESULT_V2, g.SCHEMA_REVIEW))   # v1 reviewは書換えない
        self.assertEqual(out["result"]["items"][0]["translation_source"], "stepB_generated")
        self.req()

    def test_unconfirmed_v1_review_is_upgraded_to_v2(self):
        r = self.ensure()
        v1 = dict(gr.load_review(self.sd), schema=g.SCHEMA_REVIEW)
        with rv.review_lock(self.sd, "grammar", "t"):
            gr._atomic_json(gr.paths(self.sd)["review"], v1)
        r2 = self.ensure()
        self.assertEqual((r2["state"], r2["review"]["schema"]), ("PENDING", g.SCHEMA_REVIEW_V2))
        self.assertTrue(any(h["event"] == "upgraded_v1_to_v2" for h in r2["review"]["history"]))

    def _exc(self, fn):
        try:
            fn()
        except Exception as e:   # noqa: BLE001
            return e

    def test_v2_artifacts_without_pregen_file_is_integrity_not_legacy_nor_regeneration(self):
        self.prepare()
        self.decide("pick", ids=[self.ids()[0]], accept_ai=True)
        self.final()
        os.remove(gr.paths(self.sd)["explanations"])                                       # copy-runでの欠落/手動削除
        n0 = self.xp.n
        for call in (self.final, self.req, lambda: p2w.verify_outputs(self.sd, PARAS, LABEL, level="b1b", next_command="x")):
            with self.assertRaises(g.Part2IntegrityError):
                call()
        self.assertEqual(self.xp.n, n0)                                                     # 再生成へ落ちない
        self.assertTrue(issubclass(g.Part2IntegrityError, g.Part2Stale))


class T5_TranslationIssue(PCase):
    def _auto_ready(self):
        self.ensure()
        rv.add_declaration(run_dirs=[self.run_dir], by="t", reason="r")
        self.ensure()
        self.pregen()
        return gr.load_candidates(self.sd)["candidates"][0]

    def test_pool_mismatch_is_issue_rc4_regardless_of_freeze_and_ack_resolves_it(self):
        c = self._auto_ready()
        pool = {c["sentence"]: "Part 1の別の訳です。"}
        with self.assertRaises(p2w.Part2NotConfirmed) as cm:
            self.final(ref_ja_pool=pool)
        self.assertIn("解消手段", str(cm.exception))
        self.assertTrue(os.path.exists(gr.paths(self.sd)["translation_issue"]))
        self.assertFalse(os.path.exists(p2w.RESULT_PATH(self.sd)))
        with self.assertRaises(rv.KpReviewError):                                           # --user-ref必須
            gr.op_accept_translation_diff(self.sd, ids=[c["candidate_id"]], by="u", user_ref="", reason="了承")
        with self.assertRaises(rv.KpReviewError):                                           # ISSUEに無いid
            gr.op_accept_translation_diff(self.sd, ids=["gxxxx"], by="u", user_ref="ユーザー発言", reason="了承")
        self.assertEqual(gr.op_accept_translation_diff(self.sd, ids=[c["candidate_id"]], by="u", user_ref="ユーザー発言「このまま」", reason="了承"), [c["candidate_id"]])
        self.assertEqual(gr.op_accept_translation_diff(self.sd, ids=[c["candidate_id"]], by="u", user_ref="ユーザー発言「このまま」", reason="了承"), [])   # 冪等
        out = self.final(ref_ja_pool=pool)                                                   # 了承後は進める(記録が残る)
        self.assertEqual(out["path"], "v2")
        self.req(ref_ja_pool=pool)
        with self.assertRaises(p2w.Part2NotConfirmed):                                      # Part 1訳が変わったら了承は効かない(shaに結びつく)
            self.req(ref_ja_pool={c["sentence"]: "さらに別の訳。"})

    def test_matching_translation_or_unrelated_pool_is_not_an_issue(self):
        c = self._auto_ready()
        same = {c["sentence"]: gr.load_explanations(self.sd)["items"][0]["translation_ja"]}
        self.final(ref_ja_pool=same)
        self.final(ref_ja_pool={"Totally different sentence.": "無関係"})
        self.assertEqual(g.translation_issues(self.final()["result"], None), [])

    def test_another_candidate_resolves_the_issue(self):
        self.prepare()                                                                      # 未確定+Top1/Top2の解説を事前生成済み
        ids = self.ids()
        c = gr.load_candidates(self.sd)["candidates"][0]
        pool = {c["sentence"]: "Part 1の別の訳です。"}
        self.decide("pick", ids=[ids[0]], accept_ai=True)
        with self.assertRaises(p2w.Part2NotConfirmed):
            self.final(ref_ja_pool=pool)
        rec = self.decide("pick", ids=[ids[1]])                                             # 事後Review: Top2(解説済み)を選び直す
        out = self.final(ref_ja_pool=pool)
        self.assertEqual((out["path"], out["result"]["items"][0]["selection"]["candidate_id"]), ("v2", rec["selection"]["candidate_ids"][0]))


class T6_LevelRequired(PCase):
    def test_level_is_a_required_argument_with_no_default(self):
        for fn in (gr.ensure_grammar_review, p2w.candidate_stage, p2w.pregen_stage, p2w.finalize_stage, p2w.require_final, p2w.verify_outputs, p2w.public_study_html,
                   p2w.form_grammar_bundle, p2w.form_grammar_items, p2w.cand_marker, g.resolve_candidates, g.extract_candidates, g.build_candidates_doc, g.run_part2,
                   g.finalize_part2, g.finalize_part2_v2, g.pregen_explanations):
            prm = inspect.signature(fn).parameters["level"]
            self.assertIs(prm.default, inspect.Parameter.empty, fn.__name__)
        for bad in (None, "", "B1B", "advanced", "std"):
            with self.assertRaises(g.Part2InputError):
                g.level_name(bad)

    def test_no_b1b_default_or_legacy_level_key_remains_in_new_code(self):
        for name in ("er120_part2_wiring_01.py", "er119_grammar_review_01.py"):
            s = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertNotIn("LEVEL_KEY", s, name)
            self.assertIsNone(re.search(r"\bg\.LEVEL\b|\bm\.LEVEL\b", s), name)                # v1読取専用の定数への新コード参照0
            import ast
            for node in ast.walk(ast.parse(s)):                                                   # 引数の既定値にb1bを置かない(呼出しの level="b1b" は可)
                if isinstance(node, ast.FunctionDef):
                    a = node.args
                    pairs = list(zip(a.args[len(a.args) - len(a.defaults):], a.defaults)) + [(k, d) for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None]
                    for arg, d in pairs:
                        self.assertFalse(arg.arg.startswith("level") and isinstance(d, ast.Constant) and d.value in ("b1b", "a2"), f"{name}:{node.name}")
            self.assertNotIn("discover_dirs(run)[0]", s, name)
        src = open(os.path.join(ROOT, "er120_part2_grammar_production_01.py"), encoding="utf-8").read()
        self.assertIsNone(re.search(r"\"level\":\s*LEVEL\b", src))                              # 結果/record/候補docのlevelをv1定数から決めない
        self.assertEqual(g.LEVEL, "Advanced")                                                   # v1読取専用として残置

    def test_doc_level_mismatch_is_fail_closed_and_discover_dirs_does_not_infer_from_path(self):
        self.ensure()
        with self.assertRaises(g.Part2Stale):                                               # 同じdirをa2として呼ぶ
            self.ensure(level="a2", sd=self.sd)
        with self.assertRaises(g.Part2Stale):
            p2w.pregen_stage(self.sd, level="a2", next_command="x", explain_call_fn=self.xp)
        os.makedirs(self.sd_a2)
        for f in os.listdir(self.sd):                                                       # Advancedの候補doc/reviewをa2のdirへ置いた(取り違え)
            p = os.path.join(self.sd, f)
            if os.path.isfile(p):
                with open(p, "rb") as src, open(os.path.join(self.sd_a2, f), "wb") as dst:
                    dst.write(src.read())
        with self.assertRaises(g.Part2Stale):
            gr.discover_dirs(self.run_dir, "a2")
        n = lambda xs: sorted(os.path.normpath(x) for x in xs)   # noqa: E731
        self.assertEqual(n(gr.discover_dirs(self.run_dir, "b1b")), n([self.sd]))
        self.assertEqual(n(gr.discover_dirs(self.run_dir)), n([self.sd, self.sd_a2]))   # level未指定=列挙のみ(status表示用)

    def test_study_dir_for_and_stage_names(self):
        self.assertEqual(p2w.study_dir_for("x", "o", "b1b"), "o/b1b/study_text")
        self.assertEqual(p2w.study_dir_for("x", "o", "a2"), "o/a2/study_text")
        self.assertEqual(p2w.study_dir_for("y", "o", "b1b"), "o/study_text")
        self.assertEqual(p2w.study_dir_for("z", "o", "a2"), "o/a2/study_text")
        self.assertEqual(p2w.stage_names("a2"), {"cand": "part2_cand_a2", "expl": "part2_expl_a2", "final": "part2_a2"})
        self.assertEqual(p2w.stage_names("b1b")["cand"], "part2_cand_b1b")                  # 旧stage名と同一(Y/Zの来歴互換)
        with self.assertRaises(g.Part2InputError):
            p2w.study_dir_for("a", "o", "b1b")


class T8_ReviewV2(PCase):
    def test_pick_rules_reason_limits_and_idempotent_form_selection(self):
        self.prepare()
        ids = self.ids()
        with self.assertRaises(g.Part2ReviewError):                                         # 理由なし(AI推奨のみ以外)
            self.decide("pick", ids=[ids[1]], reason="")
        with self.assertRaises(g.Part2ReviewError):                                         # 2件同時選択は禁止(Top1+Top2でも)
            self.decide("pick", ids=ids[:2], reason="2件")
        with self.assertRaises(g.Part2ReviewError):                                         # Top1/Top2以外(3位)は提示していない=選べない
            self.decide("pick", ids=[ids[2]], reason="3位")
        with self.assertRaises(g.Part2ReviewError):                                         # 重複
            self.decide("pick", ids=[ids[0], ids[0]])
        with self.assertRaises(g.Part2ReviewError):                                         # 候補外
            self.decide("pick", ids=["gxxxx"])
        with self.assertRaises(g.Part2ReviewError):                                         # accept_aiはTOP1のみのとき
            self.decide("pick", ids=[ids[0], ids[1]], accept_ai=True)
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)                  # 拒否時は状態不変
        rec = self.decide("pick", ids=[ids[0]], reason="", accept_ai=True)                  # AI推奨のみ=理由不要
        self.assertEqual((rec["schema"], rec["status"], rec["selection"]["choice"], rec["selection"]["candidate_ids"]), (g.SCHEMA_REVIEW_V2, rv.ST_REVIEWED, "pick", [ids[0]]))
        self.assertEqual(set(rec["decision"]["explanation_sha_by_id"]), set(ids[:2]))        # 提示したTop1/Top2の解説のid別sha
        self.assertEqual(rec["verdicts"], {ids[0]: "SELECTED", ids[1]: "NOT_SELECTED"})

    def test_same_single_pick_gives_same_signature_and_result_across_runs(self):
        sd2 = os.path.join(self.tmp, "run2", "b1b", "study_text")
        for sd, run in ((self.sd, self.run_dir), (sd2, os.path.join(self.tmp, "run2"))):
            self.ensure(sd=sd, run_dir=run)
            self.pregen(sd=sd)
        ids = self.ids()
        a = self.decide("pick", ids=[ids[1]], reason="Top2")
        b = self.decide("pick", sd=sd2, ids=[ids[1]], reason="Top2")
        self.assertEqual(a["selection"]["candidate_ids"], [ids[1]])
        self.assertEqual(a["selection_signature"], b["selection_signature"])
        ra, rb = self.final()["result"], self.final(sd=sd2)["result"]
        strip = lambda r: {k: v for k, v in r.items() if k not in ("generated_at", "audit", "reused_from_previous_run")}   # noqa: E731
        self.assertEqual(json.dumps(strip(ra), sort_keys=True), json.dumps(strip(rb), sort_keys=True))

    def test_form_selection_pick_omit_zero_idempotent_and_validation(self):
        self.prepare()
        ids = self.ids()
        with self.assertRaises(g.Part2ReviewError):
            gr.apply_form_selection(self.sd, ids=ids[:2], by="u", user_ref="ref")           # 2件同時選択は禁止
        with self.assertRaises(g.Part2ReviewError):
            gr.apply_form_selection(self.sd, ids=[ids[2]], by="u", user_ref="ref")          # Top1/Top2以外は選べない
        with self.assertRaises(g.Part2ReviewError):
            gr.apply_form_selection(self.sd, ids=["gxxxx"], by="u", user_ref="ref")
        with self.assertRaises(g.Part2ReviewError):
            gr.apply_form_selection(self.sd, ids=[ids[0]], by="u", user_ref="ref", candidates_sha256="0" * 64)
        r0 = gr.apply_form_selection(self.sd, ids=[], by="u", user_ref="ref")                 # 文法0件 -> 同じロック内でomit
        self.assertEqual((r0["status"], r0["selection"]["choice"], r0["selection"]["zero_reason"]), (rv.ST_REVIEWED, "omit", "form_submission_no_grammar"))
        r0b = gr.apply_form_selection(self.sd, ids=[], by="u", user_ref="ref")                # 冪等(版が進まない)
        self.assertEqual(r0b["revision"], r0["revision"])
        out = self.final()
        self.assertEqual((out["result"]["status"], out["result"]["zero_reason"], out["result"]["items"]), ("ZERO", "form_submission_no_grammar", []))
        self.assertEqual((g.render_markdown(out["result"]), g.render_html_block(out["result"])), ("", ""))   # 0件=コーナー全体を出さない(固定文面なし)
        self.req()
        r1 = gr.apply_form_selection(self.sd, ids=[ids[1]], by="u", user_ref="ref")         # 事後の選び直し(保護なし環境): pick 1件(Top2)
        self.assertEqual(r1["selection"]["candidate_ids"], [ids[1]])
        self.assertEqual(r1["decision"]["channel"], "form")
        self.assertEqual(gr.apply_form_selection(self.sd, ids=[ids[1]], by="u", user_ref="ref")["revision"], r1["revision"])
        self.assertEqual([i["selection"]["candidate_id"] for i in self.final()["result"]["items"]], [ids[1]])
        self.req()

    def test_form_selection_requires_complete_pregen(self):
        self.ensure()
        with self.assertRaises(rv.KpReviewError):
            gr.apply_form_selection(self.sd, ids=[], by="u", user_ref="ref")

    def test_auto_declaration_adopts_top1_only_and_pregens_top1_only(self):
        self.ensure()
        rv.add_declaration(run_dirs=[self.run_dir], by="t", reason="r")
        r = self.ensure()
        self.assertEqual((r["review"]["status"], r["review"]["selection"]["candidate_ids"]), (rv.ST_AUTO, [self.ids()[0]]))
        pre = self.pregen()
        self.assertEqual((len(pre["generated"]), self.xp.n, pre["confirmed"]), (1, 1, True))   # 任意最適化: TOP1だけ生成
        self.assertEqual([i["source"] for i in gr.load_explanations(self.sd)["items"]], ["stepB_generated"])
        out = self.final()
        self.assertEqual(len(out["result"]["items"]), 1)
        self.assertEqual(out["result"]["items"][0]["selection"]["source"], "auto_top1")
        s = g.summarize_review_statuses([gr.load_review(self.sd)])
        self.assertEqual((s["reviewed"], s["unreviewed_auto_adopted"]), (0, 1))

    def test_zero_candidates_confirm_without_waiting_and_empty_pregen_file_marks_pregen_done(self):
        r = self.ensure(ex=Ctr(zero_extract))
        self.assertEqual((r["state"], r["review"]["status"], r["review"]["schema"]), ("READY", rv.ST_NO_CANDIDATE, g.SCHEMA_REVIEW_V2))
        self.pregen()
        self.assertEqual(gr.load_explanations(self.sd)["items"], [])
        out = self.final()
        self.assertEqual((out["result"]["status"], out["result"]["zero_reason"], self.xp.n), ("ZERO", "no_candidate", 0))
        self.req()
        self.assertEqual(p2w.form_grammar_bundle(self.sd, level="b1b")["grammar_status"], "no_candidates_found")

    def test_selection_after_reselect_requires_fresh_pregen_and_marks_request_stale(self):
        self.prepare()
        self.assertNotIn("古い/未完成", open(gr.paths(self.sd)["request"], encoding="utf-8").read())
        rec = self.decide("reselect", reason="不自然")
        self.assertEqual(rec["status"], rv.ST_PENDING)
        self.assertIn("古い/未完成", open(gr.paths(self.sd)["request"], encoding="utf-8").read())   # 古い依頼書を残さない
        n0 = self.xp.n
        pre = self.pregen()                                                                    # 新しいTop1(旧3位)の1件だけ生成(旧Top1/Top2はNG)
        self.assertEqual((self.xp.n, len(pre["generated"])), (n0 + 1, 1))
        self.assertEqual(len(gr.load_explanations(self.sd)["items"]), 1)                       # NG済み候補の解説は捨てる
        self.assertNotIn("古い/未完成", open(gr.paths(self.sd)["request"], encoding="utf-8").read())
        self.decide("pick", ids=self.ids(), accept_ai=True)                                     # 新しいTOP1だけ


class T9_ResultV2(PCase):
    def test_two_item_pick_is_rejected_and_one_item_is_byte_identical_to_v1_rendering(self):
        self.prepare()
        ids = self.ids()                                                                      # rank順: P1(CLEFT), P2(SPEC), P3(INV)。提示=P1,P2のみ
        with self.assertRaises(g.Part2ReviewError):                                           # 2件同時選択は禁止
            self.decide("pick", ids=[ids[1], ids[0]], reason="2件")
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)
        # 1件: v1形のresultとバイト同一
        self.decide("pick", ids=[ids[0]], accept_ai=True)
        one = self.final()["result"]
        self.assertEqual(len(one["items"]), 1)
        it = one["items"][0]
        v1 = {"schema": g.SCHEMA_RESULT, "status": "SELECTED", "selection": it["selection"], "sections": it["sections"], "translation_ja": it["translation_ja"]}
        self.assertEqual(g.render_markdown(v1), g.render_markdown(one))
        self.assertEqual(g.render_html_block(v1), g.render_html_block(one))
        self.assertEqual(g.result_items(v1)[0]["selection"], it["selection"])                  # v1は書換えず正規化して読む
        self.req()

    def test_decision_explanation_sha_binds_the_displayed_explanation(self):
        self.prepare()
        self.decide("pick", ids=[self.ids()[0]], accept_ai=True)
        self.final()
        self.req()
        path = gr.paths(self.sd)["explanations"]
        ex = json.load(open(path, encoding="utf-8"))
        it = ex["items"][0]
        it["explanation_md"] = it["explanation_md"] + "\n(改変)"
        it["explanation_sha256"] = g.explanation_sha256(it["explanation_md"])
        ex["explanations_sha256"] = g.explanations_digest(ex["items"])
        gr._atomic_json(path, ex)                                                              # shaまで整合させた改変でも、確定時に見た解説(decision.sha)と一致しない
        with self.assertRaises(g.Part2Stale):
            self.req()
        with self.assertRaises(g.Part2Stale):
            self.final()

    def test_tampered_result_item_is_rejected(self):
        self.prepare()
        self.decide("pick", ids=[self.ids()[0]], accept_ai=True)
        res = self.final()["result"]
        bad = json.loads(json.dumps(res))
        bad["items"][0]["explanation_md"] += "x"
        gr._atomic_json(p2w.RESULT_PATH(self.sd), bad)
        with self.assertRaises(g.Part2Stale):
            self.req()
        bad2 = json.loads(json.dumps(res))
        bad2["items"].append(bad2["items"][0])
        gr._atomic_json(p2w.RESULT_PATH(self.sd), bad2)
        with self.assertRaises(g.Part2Stale):
            self.req()


class T10_CapAndFailure(PCase):
    def test_only_top2_are_pregenerated_presented_and_selectable(self):
        paras = [f"Sentence number {i} was written here today." for i in range(1, 11)]
        self.ensure(paras=paras, ex=Ctr(many_extract(10)))
        pre = self.pregen()
        self.assertEqual((len(pre["generated"]), self.xp.n, len(pre["skipped_over_cap"])), (g.PREGEN_MAX, 2, 8))   # Top1/Top2のみ課金(3位以降は生成しない)
        self.assertEqual((g.PREGEN_MAX, g.GRAMMAR_MAX, g.TOP_N), (2, 1, 2))
        txt = open(gr.paths(self.sd)["request"], encoding="utf-8").read()
        self.assertIn("他8件は非表示", txt)
        b = p2w.form_grammar_bundle(self.sd, level="b1b")
        self.assertEqual((len(b["items"]), b["n_not_generated"], b["grammar_status"]), (2, 8, "candidates_available"))
        self.assertEqual([i["ai_recommended"] for i in b["items"]], [True, False])
        self.assertEqual([i["rank"] for i in b["items"]], [1, 2])
        third = self.ids()[2]
        with self.assertRaises(g.Part2ReviewError):                                         # 提示していない候補は選べない
            self.decide("pick", ids=[third])
        with self.assertRaises(g.Part2ReviewError):                                         # Top1+Top2の2件同時も不可
            self.decide("pick", ids=[self.ids()[0], self.ids()[1]])
        self.assertEqual(gr.load_review(self.sd)["status"], rv.ST_PENDING)

    def test_one_candidate_presents_one_and_zero_candidates_presents_none_without_padding(self):
        paras = ["Sentence number 1 was written here today."]
        self.ensure(paras=paras, ex=Ctr(many_extract(1)))
        pre = self.pregen()
        self.assertEqual((len(pre["generated"]), self.xp.n, pre["skipped_over_cap"]), (1, 1, []))   # 数合わせの追加はしない
        self.assertEqual(len(p2w.form_grammar_bundle(self.sd, level="b1b")["items"]), 1)

    def test_failure_keeps_done_items_blocks_hr_and_form_and_resumes_only_missing(self):
        n = {"i": 0}

        def flaky(prompt):
            n["i"] += 1
            if n["i"] in (2, 3):                                                             # 2番目の候補が初回+技術retryで構造NG
                return "garbage", mk.MODEL, _usage(), "bad"
            return mk.mock_explain_call_fn(prompt)
        self.ensure()
        with self.assertRaises(g.Part2Error):
            self.pregen(xp=Ctr(flaky))
        fp = os.path.join(self.sd, g.FAILED_FILENAME)
        failed = json.load(open(fp, encoding="utf-8"))
        self.assertEqual((failed["stage"], failed["next_command"]), ("part2_expl_b1b", "rerun"))
        self.assertEqual(len(gr.load_explanations(self.sd)["items"]), 1)                    # 成功分は保持
        self.assertIn("古い/未完成", open(gr.paths(self.sd)["request"], encoding="utf-8").read())
        with self.assertRaises(g.Part2Stale):                                              # フォーム用データを出さない
            p2w.form_grammar_items(self.sd, level="b1b")
        with self.assertRaises(rv.KpReviewError):                                          # grammar-show / HR決定も出さない
            gr.render_request_md(gr.load_candidates(self.sd), gr.load_review(self.sd), run_hint=self.run_dir, study_dir=self.sd)
        with self.assertRaises(rv.KpReviewError):
            self.decide("top1")
        ok = Ctr(mk.mock_explain_call_fn)
        pre = self.pregen(xp=ok)                                                             # 再開: 未生成の1件だけ(Top1/Top2のうち失敗分)
        self.assertEqual((len(pre["generated"]), len(pre["reused"]), ok.n), (1, 1, 1))
        self.assertFalse(os.path.exists(fp))
        self.assertTrue(os.path.exists(fp.replace(".json", ".resolved.json")))
        self.assertEqual(len(p2w.form_grammar_items(self.sd, level="b1b")), 2)

    def test_budget_stop_before_api_keeps_partial_and_never_writes_incomplete_form_data(self):
        self.ensure()
        seen = []

        def guard(stage, est):
            seen.append(stage)
            if len(seen) > 1:
                raise RuntimeError("budget stop")
        with self.assertRaises(RuntimeError):
            p2w.pregen_stage(self.sd, level="b1b", next_command="x", explain_call_fn=self.xp, budget_guard=guard)
        self.assertEqual((self.xp.n, len(gr.load_explanations(self.sd)["items"])), (1, 1))
        with self.assertRaises(g.Part2Stale):
            p2w.form_grammar_items(self.sd, level="b1b")


class T12_PromptsUnchanged(PCase):
    def test_prompt_text_sha_and_approved_selection_constants_are_unchanged(self):
        self.assertEqual((g.STEPA_PROMPT_SHA256, g.STEPB_PROMPT_SHA256), (STEPA_SHA, STEPB_SHA))
        self.assertEqual(hashlib.sha256(g.STEPA_PROMPT.encode("utf-8")).hexdigest(), STEPA_SHA)
        self.assertEqual((g.TOP_N, g.PRIORITY, g.MAX_RESELECT, g.MAX_REEXTRACT), (2, ["INV", "CLEFT", "CMP", "FRONT", "HEAVY", "POSTMOD", "SPEC", "ELL", "APPOS"], 2, 1))
        c1, c2 = self.prepare(), None
        self.assertEqual(gr.load_candidates(self.sd)["candidates"][0]["candidate_id"], self.ids()[0])
        doc = gr.load_candidates(self.sd)
        self.assertEqual(doc["prompt_template_sha256"], STEPA_SHA)                              # 事前生成はPrompt/選定規則に触れない
        self.assertEqual(gr.load_explanations(self.sd)["stepb_prompt_sha256"], STEPB_SHA)
        self.assertEqual(self.xp.prompts[0].split("# 解説する英文")[0], g.STEPB_PROMPT.split("# 解説する英文")[0])
        self.assertNotIn("参考訳(別工程で確定済み)", self.xp.prompts[0])                         # 事前生成はref_ja=None(参考訳の行を渡さない)


class T14_FormData(PCase):
    def test_form_grammar_items_contract_and_fail_closed_on_mismatch(self):
        with self.assertRaises(g.Part2Stale):
            p2w.form_grammar_items(self.sd, level="b1b")                                       # 候補docなし
        self.prepare()
        b = p2w.form_grammar_bundle(self.sd, level="b1b")
        ex = {i["candidate_id"]: i for i in gr.load_explanations(self.sd)["items"]}
        self.assertEqual((b["grammar_status"], b["n_not_generated"], b["level"]), ("candidates_available", 1, "b1b"))
        self.assertEqual(len(b["items"]), 2)                                                # Top1/Top2のみ
        for it in b["items"]:
            e = ex[it["candidate_id"]]
            self.assertEqual((it["id"], it["title"], it["explanation_full"], it["explanation_status"], it["explanation_sha256"], it["level"]),
                             (it["candidate_id"], gr.load_candidates(self.sd)["candidates"][it["rank"] - 1]["construct_ja"], e["explanation_md"], "provided", e["explanation_sha256"], "Advanced"))
            self.assertEqual(it["example"], e["sentence"])
        # explanations_sha不一致 -> データを出さない
        path = gr.paths(self.sd)["explanations"]
        d = json.load(open(path, encoding="utf-8"))
        d["explanations_sha256"] = "0" * 64
        gr._atomic_json(path, d)
        with self.assertRaises(g.Part2Stale):
            p2w.form_grammar_items(self.sd, level="b1b")
        with self.assertRaises(rv.KpReviewError):
            gr.render_request_md(gr.load_candidates(self.sd), gr.load_review(self.sd), run_hint=self.run_dir, study_dir=self.sd)


class T18_StandardLevelAndSectionCheck(PCase):
    def test_standard_level_runs_the_same_core_in_its_own_dir_and_registry(self):
        paras2 = ["The short story begins here. It was a calm night.", "It was in March that the plan changed. People cheered.", "Nothing else happened that day."]
        r = self.prepare(level="a2", paras=paras2)
        self.assertEqual((r["doc"]["level"], r["review"]["level"], r["review"]["article_key"]["level"]), ("Standard", "Standard", "a2"))
        self.assertEqual(self.xp.n, min(g.PREGEN_MAX, len(r["doc"]["candidates"])))
        self.decide("pick", sd=self.sd_a2, ids=[self.ids(self.sd_a2)[0]], accept_ai=True)
        out = self.final(level="a2", paras=paras2)
        self.assertEqual((out["path"], out["result"]["level"]), ("v2", "Standard"))
        self.req(level="a2", paras=paras2)
        with self.assertRaises(g.Part2Stale):                                              # Advancedとして呼ぶと拒否(別levelの成果物)
            p2w.require_final(self.sd_a2, paras2, LABEL, level="b1b", next_command="x")
        self.assertEqual(sorted(rv.store_load_ng("x", "coffee", "a2", "grammar")), [])      # Stdの共有NG registryはAdvとは別key
        self.decide("reselect", sd=self.sd_a2, reason="x") if False else None

    def test_section_scoped_verification_catches_wrong_level_missing_and_duplicate_blocks(self):
        paras2 = ["The short story begins here. It was a calm night.", "It was in March that the plan changed. People cheered.", "Nothing else happened that day."]
        self.prepare()
        self.decide("pick", ids=[self.ids()[0]], accept_ai=True)
        adv = self.final()["result"]
        self.prepare(level="a2", paras=paras2)
        self.decide("pick", sd=self.sd_a2, ids=[self.ids(self.sd_a2)[0]], accept_ai=True)
        std = self.final(level="a2", paras=paras2)["result"]
        adv_blk, std_blk = g.render_html_block(adv, include_css=False), g.render_html_block(std, include_css=False)
        self.assertNotEqual(adv_blk, std_blk)
        md_adv, md_std = os.path.join(self.sd, f"{g.PART2_FILE_STEM}.md"), os.path.join(self.sd_a2, f"{g.PART2_FILE_STEM}.md")
        v = lambda level, sd, paras, md, html: p2w.verify_outputs(sd, paras, LABEL, level=level, next_command="x", md_path=md, html_text=html)   # noqa: E731
        v("b1b", self.sd, PARAS, md_adv, f"<div>{adv_blk}</div>")
        v("a2", self.sd_a2, paras2, md_std, f"<div>{std_blk}</div>")
        with self.assertRaises(g.Part2Stale):                                               # levelを取り違えたブロック(件数は1個でも)
            v("b1b", self.sd, PARAS, md_adv, f"<div>{std_blk}</div>")
        with self.assertRaises(g.Part2Stale):
            v("a2", self.sd_a2, paras2, md_std, f"<div>{adv_blk}</div>")
        with self.assertRaises(g.Part2Stale):                                               # 欠落
            v("a2", self.sd_a2, paras2, md_std, "<div>none</div>")
        with self.assertRaises(g.Part2Stale):                                               # 節に2個(ページ全体を渡した等)
            v("a2", self.sd_a2, paras2, md_std, f"<div>{std_blk}{adv_blk}</div>")
        self.assertEqual(g.count_grammar_blocks(f"{std_blk}{adv_blk}"), 2)


class T19_PublicBuilderAndKcpCompat(PCase):
    ARTICLE = "# Test Story\n\n" + "\n\n".join(PARAS) + "\n"

    def test_public_study_html_requires_level_and_renders_standard_without_part1(self):
        with self.assertRaises(TypeError):
            p2w.public_study_html(self.run_dir, self.ARTICLE)                                # levelは必須
        self.prepare(level="a2")
        with self.assertRaises(p2w.Part2NotConfirmed):                                       # 未確定=待機
            p2w.public_study_html(self.run_dir, self.ARTICLE, level="a2")
        self.decide("pick", sd=self.sd_a2, ids=[self.ids(self.sd_a2)[0]], accept_ai=True)
        self.final(level="a2")
        h = p2w.public_study_html(self.run_dir, self.ARTICLE, level="a2")
        self.assertEqual((g.count_grammar_blocks(h), "<style>" in h), (1, True))              # Stdは文法ブロックのみ(Part 1なし)=CSS付き
        with self.assertRaises((g.Part2Stale, rv.KpReviewError)):                            # Advanced側は未生成(Part 1/Part 2とも無い)=ページを作らない
            p2w.public_study_html(self.run_dir, self.ARTICLE, level="b1b")

    def _stub(self, frozen, v2=False):
        outer = self

        class StubCC:
            def __init__(self):
                self.frozen, self.verified, self.frozen_views = frozen, [], []

            def grammar_state(self, sd):
                return {"sidecar": {"items": [{"id": f["candidate_id"]} for f in self.frozen]}, "kp_dir": "kp", "level": "b1b", "rec": {}}

            def guard_grammar(self, sd, op, candidate_id=None):
                return None

            def load_frozen_grammar(self, sd):
                return self.frozen[0] if len(self.frozen) == 1 else None

            def freeze_from_sidecar(self, sd, cand):
                return None

            def freeze_part2_result(self, sd, view):
                self.frozen_views.append(view)

            def verify_part2(self, sd, view):
                self.verified.append(view)

            def pool_ref_ja_issue(self, *a, **k):
                return None
        stub = StubCC()
        if v2:
            stub.load_frozen_grammar_items = lambda sd: stub.frozen
            stub.verify_part2_items = lambda sd, res: stub.verified.append(res)
        p = mock.patch.object(rv, "_cc", return_value=stub)
        p.start()
        self.addCleanup(p.stop)
        return stub

    def _frozen_for(self, cid):
        c = next(c for c in gr.load_candidates(self.sd)["candidates"] if c["candidate_id"] == cid)
        md = mk.STEPB_MOCK.split("=====ITEM 1=====\n")[1].replace("これはmockの日本語訳です。", "フォームで見せた別の訳です。")
        tr = "フォームで見せた別の訳です。"
        return {"candidate_id": cid, "sentence": c["sentence"], "construct_ja": c["construct_ja"], "explanation_md": md.strip(), "sections": {}, "translation_ja": tr,
                "ref_ja_at_freeze": None, "source": "form_displayed", "frozen_sha256": g.frozen_sha_of(cid, c["sentence"], md.strip(), tr)}

    def test_frozen_value_wins_over_pregen_and_two_item_pick_is_rejected(self):
        self.prepare()
        ids = self.ids()
        self.decide("pick", ids=[ids[0]], accept_ai=True)
        stub = self._stub([self._frozen_for(ids[0])])
        n0 = self.xp.n
        pre = self.pregen()                                                                   # 凍結値のある候補は(確定済み)生成しない
        self.assertEqual((len(pre["generated"]), self.xp.n), (0, n0))
        res = self.final()["result"]
        it = res["items"][0]
        self.assertEqual((it["translation_source"], it["translation_ja"], it["frozen_source"]), ("frozen", "フォームで見せた別の訳です。", "form_displayed"))
        self.assertTrue(it["explain_signature"].startswith("frozen:"))
        self.req()
        self.assertTrue(stub.verified and stub.verified[-1]["status"] == "SELECTED")           # G4(KCP v1 API)へは単件viewで渡す
        # 凍結値と違う結果は拒否(凍結した解説全文が正)
        bad = json.loads(json.dumps(res))
        bad["items"][0]["explanation_md"] += "x"
        gr._atomic_json(p2w.RESULT_PATH(self.sd), bad)
        with self.assertRaises(g.Part2Stale):
            self.req()
        # 2件選定は(KCPの版に関係なく)reviewの段階で拒否される(2026-10-27文法選定仕様)
        with self.assertRaises(g.Part2ReviewError):
            self.decide("pick", ids=[ids[0], ids[1]], reason="2件")

    def test_kcp_v2_items_api_is_used_when_available(self):
        self.prepare()
        ids = self.ids()
        self.decide("pick", ids=[ids[1]], reason="Top2")
        stub = self._stub([self._frozen_for(ids[1])], v2=True)
        res = self.final()["result"]
        self.assertEqual([i["translation_source"] for i in res["items"]], ["frozen"])
        self.assertEqual([i["selection"]["candidate_id"] for i in res["items"]], [ids[1]])
        self.req()
        self.assertTrue(stub.verified)


class T20_StaticBoundaries(unittest.TestCase):
    def test_no_new_flag_and_no_env_reads_in_new_code(self):
        for name in ("er120_part2_grammar_production_01.py", "er120_part2_wiring_01.py", "er119_grammar_review_01.py"):
            s = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertNotIn("os.environ", s, name)
            self.assertNotIn("getenv", s, name)
            self.assertIsNone(re.search(r"PREGEN_ENABLED|GRAMMAR_PREGEN_FLAG|enable_pregen", s), name)   # 新flagを設けない(承認済みProduction仕様)


if __name__ == "__main__":
    unittest.main()
