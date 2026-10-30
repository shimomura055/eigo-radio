# -*- coding: utf-8 -*-
"""KP-DIFFICULTY-4LEVEL-DISPLAY-01 委任_01 test(API 0・mock)。難易度4段階は『Gateではなく参考情報』であること、全候補に付くこと、
fail-open(unknown)、除外ゼロ、フォームdata/確定recordへの透過、resume/再選定/補完での扱い、実API遮断を固定する。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import json
import os
import sys
import unittest

from er119_test_support_01 import ARTICLE, Env, KpTestCase, jl
import er119_kp_candidates_01 as kcand
import er119_kp_difficulty_01 as dg
import er105_kp_fulltext_selector_01 as ft
import er119_kp_human_review_01 as rv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools"))
import export_form_data_01 as xf  # noqa: E402


def _cands(n=3):
    return [{"candidate_id": f"c{i}", "used_form": f"expr {i}", "kind": "phrase", "japanese_gloss": "意味", "source_sentence": "A sentence."}
            for i in range(1, n + 1)]


def _resp(levels, ids=None):
    ids = ids or [f"c{i}" for i in range(1, len(levels) + 1)]
    return json.dumps({"items": [{"id": i, "level": lv, "reason_ja": "理由"} for i, lv in zip(ids, levels)]}, ensure_ascii=False)


def _caller(*responses):
    """call_fn差込み。responses=各attemptの返答(str=raw, Exception=raise)。"""
    state = {"i": 0, "msgs": []}

    def call_fn(msg):
        state["msgs"].append(msg)
        r = responses[min(state["i"], len(responses) - 1)]
        state["i"] += 1

        def fn():
            if isinstance(r, BaseException):
                raise r
            return r, "gpt-6-luna", f"resp{state['i']}"
        return fn
    call_fn.state = state
    return call_fn


class GradeUnitTest(unittest.TestCase):
    def test_four_levels_mapped_to_display_labels(self):
        cs = _cands(4)
        rec = dg.apply_to_candidates(cs, "a2", call_fn=_caller(_resp(["easy", "medium", "hard", "rare"])))
        self.assertEqual([c["difficulty"]["label_ja"] for c in cs], ["易", "中", "難", "激難(レア)"])
        self.assertEqual([c["difficulty"]["level"] for c in cs], ["easy", "medium", "hard", "rare"])
        self.assertEqual(rec["status"], "OK")
        self.assertEqual((rec["n_graded"], rec["n_unknown"]), (4, 0))
        self.assertEqual(rec["prompt_sha256"], dg.PROMPT_SHA256)

    def test_message_carries_level_and_all_items_and_prompt_prefix(self):
        cs = _cands(3)
        cf = _caller(_resp(["easy", "easy", "easy"]))
        dg.apply_to_candidates(cs, "b1b", call_fn=cf)
        msg = cf.state["msgs"][0]
        self.assertTrue(dg.prefix_intact(msg))
        self.assertIn("Advanced", msg)
        for c in cs:
            self.assertIn(f'"id": "{c["candidate_id"]}"', msg)

    def test_one_call_when_all_graded(self):
        cf = _caller(_resp(["easy"] * 3))
        dg.apply_to_candidates(_cands(3), "a2", call_fn=cf)
        self.assertEqual(len(cf.state["msgs"]), 1)

    def test_fail_open_when_api_fails_twice_all_unknown_and_nothing_removed(self):
        cs = _cands(3)
        before = json.loads(json.dumps(cs))
        cf = _caller(RuntimeError("boom"), RuntimeError("boom2"))
        rec = dg.apply_to_candidates(cs, "a2", call_fn=cf)
        self.assertEqual(len(cf.state["msgs"]), dg.MAX_ATTEMPTS)
        self.assertEqual(rec["status"], "FAILED_OPEN")
        self.assertEqual(len(cs), 3)
        for c, b in zip(cs, before):
            self.assertEqual(c["difficulty"]["level"], "unknown")
            self.assertEqual(c["difficulty"]["label_ja"], "未判定")
            self.assertEqual({k: v for k, v in c.items() if k != "difficulty"}, b)       # 既存fieldは無変更(追加のみ)

    def test_retry_then_success(self):
        cs = _cands(2)
        rec = dg.apply_to_candidates(cs, "a2", call_fn=_caller("not json", _resp(["hard", "easy"])))
        self.assertEqual([c["difficulty"]["level"] for c in cs], ["hard", "easy"])
        self.assertEqual(rec["status"], "OK")
        self.assertEqual(len(rec["attempts"]), 2)

    def test_partial_then_full(self):
        cs = _cands(3)
        rec = dg.apply_to_candidates(cs, "a2", call_fn=_caller(_resp(["easy", "hard"], ["c1", "c3"]), _resp(["easy", "medium", "hard"])))
        self.assertEqual([c["difficulty"]["level"] for c in cs], ["easy", "medium", "hard"])
        self.assertEqual(rec["status"], "OK")

    def test_partial_both_attempts_missing_item_is_unknown_only(self):
        cs = _cands(3)
        rec = dg.apply_to_candidates(cs, "a2", call_fn=_caller(_resp(["easy", "hard"], ["c1", "c3"])))
        self.assertEqual([c["difficulty"]["level"] for c in cs], ["easy", "unknown", "hard"])
        self.assertEqual(rec["status"], "PARTIAL")
        self.assertEqual((rec["n_graded"], rec["n_unknown"]), (2, 1))

    def test_invalid_level_and_unknown_id_and_duplicate_id(self):
        raw = json.dumps({"items": [{"id": "c1", "level": "impossible", "reason_ja": "x"}, {"id": "zz", "level": "easy", "reason_ja": "x"},
                                    {"id": "c2", "level": "hard", "reason_ja": "first"}, {"id": "c2", "level": "easy", "reason_ja": "dup"}]})
        cs = _cands(2)
        dg.apply_to_candidates(cs, "a2", call_fn=_caller(raw))
        self.assertEqual([c["difficulty"]["level"] for c in cs], ["unknown", "hard"])

    def test_empty_candidates_no_call(self):
        cf = _caller(_resp([]))
        rec = dg.apply_to_candidates([], "a2", call_fn=cf)
        self.assertEqual(len(cf.state["msgs"]), 0)
        self.assertEqual(rec["status"], "SKIPPED")

    def test_routing_violation_and_model_mismatch_and_stop_propagate(self):
        for exc in (ft.FulltextSelectionError("routing"), ft.ModelMismatchError("model"), KeyboardInterrupt()):
            with self.assertRaises(type(exc)):
                dg.apply_to_candidates(_cands(2), "a2", call_fn=_caller(exc))

    def test_real_maker_rejects_foreign_prompt_and_checks_model(self):
        real = dg._REAL_make_difficulty_fn
        with self.assertRaises(ft.FulltextSelectionError):
            real("not the difficulty prompt")

        class R:
            model, id, output_text = "other-model", "r1", "{}"

        class C:
            class responses:
                @staticmethod
                def create(**kw):
                    return R()
        fn = real(dg.build_message(_cands(1), "a2"), client=C(), model="gpt-6-luna")
        with self.assertRaises(ft.ModelMismatchError):
            fn()

    def test_real_maker_sends_schema_and_returns_model_and_response_id(self):
        sent = {}

        class R:
            model, id, output_text = "gpt-6-luna", "resp_x", _resp(["easy"])

        class C:
            class responses:
                @staticmethod
                def create(**kw):
                    sent.update(kw)
                    return R()
        raw, model, rid = dg._REAL_make_difficulty_fn(dg.build_message(_cands(1), "a2"), client=C(), model="gpt-6-luna")()
        self.assertEqual((model, rid), ("gpt-6-luna", "resp_x"))
        self.assertEqual(sent["text"]["format"]["name"], "kp_difficulty_grading")
        self.assertEqual(sent["text"]["format"]["schema"]["properties"]["items"]["items"]["properties"]["level"]["enum"], list(dg.LEVELS))

    def test_test_environment_blocks_real_api(self):
        with self.assertRaises(RuntimeError):
            dg.make_difficulty_fn(dg.build_message(_cands(1), "a2"))
        cs = _cands(2)
        rec = dg.apply_to_candidates(cs, "a2", process="A2_SUPPORT")      # 差込みなし=遮断stub→fail-open
        self.assertEqual(rec["status"], "FAILED_OPEN")
        self.assertTrue(all(c["difficulty"]["level"] == "unknown" for c in cs))


class GenerationWiringTest(KpTestCase):
    def _gen(self, env, level="b1b"):
        self.ensure(env, level=level)
        return rv.load_candidates(self.kp_dir if level == "b1b" else self.kp_dir_a2)

    def test_every_candidate_gets_difficulty_and_doc_has_audit_record(self):
        with Env(self.tmp) as env:
            env.difficulty_map = {"pushed prices up": "easy", "time lag": "hard", "spike": "rare"}
            doc = self._gen(env)
            self.assertEqual(env.n["difficulty"], 1)                                   # 1 generate = 1 call
            self.assertTrue(doc["candidates"])
            for c in doc["candidates"]:
                self.assertIn(c["difficulty"]["level"], dg.LEVELS)
                self.assertEqual(c["difficulty"]["source"], "llm")
            by = {c["used_form"]: c["difficulty"]["label_ja"] for c in doc["candidates"]}
            self.assertEqual(by.get("time lag"), "難")
            g = doc["difficulty_grading"]
            self.assertEqual((g["version"], g["prompt_sha256"], g["model_id"], g["status"]), (dg.DIFFICULTY_VERSION, dg.PROMPT_SHA256, "gpt-6-luna", "OK"))
            self.assertEqual(g["n_graded"], len(doc["candidates"]))

    def test_difficulty_never_excludes_or_reorders_candidates(self):
        """難易度はGateではない: 全部『易』でも一部『激難』でも判定失敗(unknown)でも、候補のid・順位・droppedは同一。"""
        import shutil
        all_easy = {p: "easy" for p in ("pushed prices up", "took a sharp turn", "time lag", "spike", "stock", "insiders", "blends", "increases")}
        runs = {}
        for name, dmap, fail in (("easy", all_easy, None), ("mixed", {"time lag": "rare", "spike": "hard"}, None), ("fail", {}, RuntimeError("x"))):
            shutil.rmtree(os.path.join(self.tmp, "run1"), ignore_errors=True)
            with Env(self.tmp) as env:
                env.difficulty_map, env.difficulty_fail = dmap, fail
                doc = self._gen(env)
            runs[name] = ([(c["candidate_id"], c["ai_rank"], c["used_form"], c["kind"], c["auto_eligible"]) for c in doc["candidates"]],
                          [(d["phrase"], d["stage"]) for d in doc["dropped"]])
        self.assertEqual(runs["easy"], runs["fail"])
        self.assertEqual(runs["easy"], runs["mixed"])
        self.assertTrue(runs["easy"][0])

    def test_failure_is_fail_open_unknown_and_candidates_still_presented(self):
        with Env(self.tmp) as env:
            env.difficulty_fail = RuntimeError("api down")
            doc = self._gen(env)
            self.assertTrue(doc["candidates"])
            self.assertTrue(all(c["difficulty"]["level"] == "unknown" for c in doc["candidates"]))
            self.assertEqual(doc["difficulty_grading"]["status"], "FAILED_OPEN")
            self.assertEqual(env.n["difficulty"], dg.MAX_ATTEMPTS)
            self.assertTrue(all(c["human_selectable"] for c in doc["candidates"]))

    def test_resume_does_not_regrade_and_keeps_saved_values(self):
        with Env(self.tmp) as env:
            env.difficulty_map = {"time lag": "hard"}
            doc1 = self._gen(env)
            n = env.total_llm_calls()
            doc2 = self._gen(env)                                                      # resume(候補sha一致)
            self.assertEqual(env.total_llm_calls(), n, "resumeはAPI 0(難易度も再判定しない)")
            self.assertEqual([c["difficulty"] for c in doc1["candidates"]], [c["difficulty"] for c in doc2["candidates"]])

    def test_graded_for_both_levels_standard_and_advanced(self):
        with Env(self.tmp) as env:
            a = self._gen(env, level="a2")
            b = self._gen(env, level="b1b")
            self.assertTrue(all("difficulty" in c for c in a["candidates"] + b["candidates"]))
            self.assertIn("Standard", env.difficulty_messages[0])
            self.assertIn("Advanced", env.difficulty_messages[1])

    def test_stop_check_runs_before_paid_difficulty_call(self):
        calls = []
        with Env(self.tmp) as env:
            import er119_kp_candidates_01 as k
            res = k.generate_candidates(ARTICLE, self.kp_dir, "aid", "B1", "b1b", 1, [], process="B1_SUPPORT",
                                        stop_check_fn=lambda tag: calls.append(tag))
            self.assertTrue(res["ok"])
        self.assertTrue(any(t.startswith("kp_difficulty:") for t in calls))
        self.assertEqual(calls[-1].split(":")[0], "kp_difficulty")

    def test_injected_difficulty_fn_is_used_and_can_not_remove_candidates(self):
        seen = {}

        def fake(cands, level, *, process=None):
            seen["n"] = len(cands)
            for c in cands:
                c["difficulty"] = {"level": "rare", "label_ja": "激難(レア)", "reason_ja": "t", "source": "llm"}
            return {"status": "OK"}
        with Env(self.tmp) as env:
            import er119_kp_candidates_01 as k
            res = k.generate_candidates(ARTICLE, self.kp_dir, "aid", "B1", "b1b", 1, [], process="B1_SUPPORT", difficulty_fn=fake)
            self.assertEqual(env.n["difficulty"], 0)
        self.assertEqual(seen["n"], len(res["doc"]["candidates"]))
        self.assertTrue(all(c["difficulty"]["level"] == "rare" for c in res["doc"]["candidates"]))


class BackfillDifficultyTest(KpTestCase):
    def test_backfilled_candidates_also_get_difficulty_in_the_same_single_call(self):
        """補完(backfill)で足された候補にも難易度が付く(付与位置=最終候補集合の1か所)。難易度call自体は1回のまま。"""
        from er119_kp_backfill_test_01 import BF_WORD, BF_WORD2
        from er119_test_support_01 import CALL2
        from unittest import mock
        bad = {"phrase": "xylophone", "reason_ja": "x", "word_count": 1}      # 本文に無い単語=validate除外 -> E=1 -> W5'補完
        with Env(self.tmp, rescue_env="0", call2_seq=[CALL2[:3] + [bad], [BF_WORD, BF_WORD2]]) as env, mock.patch.dict(os.environ, {"EIGO_KP_BACKFILL": "1"}):
            env.difficulty_map = {BF_WORD["phrase"]: "rare"}
            self.ensure(env)
            doc = rv.load_candidates(self.kp_dir)
        self.assertTrue(doc["backfill"]["triggered"])
        added = [c for c in doc["candidates"] if c["origin"] == "backfill"]
        self.assertTrue(added)
        self.assertEqual(env.n["difficulty"], 1)
        self.assertTrue(all(c["difficulty"]["source"] == "llm" for c in doc["candidates"]))
        self.assertIn("rare", [c["difficulty"]["level"] for c in added])


class ExportAndConfirmedTest(KpTestCase):
    def test_exporter_passes_difficulty_and_old_doc_is_unknown_not_graded(self):
        with Env(self.tmp) as env:
            env.difficulty_map = {"time lag": "hard"}
            self.ensure(env)
            doc = rv.load_candidates(self.kp_dir)
        out = xf.convert(doc, slug="s", level="b1b", name="n", family="x", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        ents = out["phrases"] + out["words"]
        self.assertEqual(len(ents), len(rv.presentable_candidates(doc)))
        for e in ents:
            self.assertIn(e["difficulty"]["level"], dg.LEVELS)
            self.assertIn(e["difficulty"]["label_ja"], ("易", "中", "難", "激難(レア)"))
        self.assertEqual({e["term"]: e["difficulty"]["label_ja"] for e in ents}["time lag"], "難")
        self.assertEqual(out["difficulty_grading"]["prompt_sha256"], dg.PROMPT_SHA256)
        old = json.loads(json.dumps(doc))
        for c in old["candidates"]:
            c.pop("difficulty", None)
        old.pop("difficulty_grading", None)
        old["candidates_sha256"] = rv.candidates_sha256(old)      # 旧docは自身のshaが整合している(難易度fieldを持たない版)
        o2 = xf.convert(old, slug="s", level="b1b", name="n", family="x", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        for e in o2["phrases"] + o2["words"]:
            self.assertEqual((e["difficulty"]["level"], e["difficulty"]["source"]), ("unknown", "not_graded"))
        self.assertEqual(len(o2["phrases"]) + len(o2["words"]), len(ents))               # 旧docでも候補は減らない
        self.assertIsNone(o2["difficulty_grading"])

    def test_difficulty_info_rejects_invalid_levels_as_unknown(self):
        self.assertEqual(xf.difficulty_info({"difficulty": {"level": "super"}})["level"], "unknown")
        self.assertEqual(xf.difficulty_info({"difficulty": {"level": "unknown", "source": "fail_open"}})["label_ja"], "未判定")
        self.assertEqual(xf.difficulty_info({"difficulty": {"level": "rare", "reason_ja": " x "}})["label_ja"], "激難(レア)")

    def test_confirmed_item_reference_keeps_difficulty_only_when_present(self):
        import er128_kp_confirmed_content_01 as cc
        base = {"candidate_id": "c1", "kind": "phrase", "reason_ja": "r", "ai_rank": 1,
                "item": {"used_form": "u", "display_phrase": "u", "key_phrase": "u", "japanese_gloss": "意味", "source_sentence_id": "s1"}}
        without = cc._item_from_cand(base, 1, "kp")
        self.assertNotIn("difficulty", without["reference"])
        with_d = cc._item_from_cand(dict(base, difficulty={"level": "hard", "label_ja": "難", "reason_ja": "x", "source": "llm"}), 1, "kp")
        self.assertEqual(with_d["reference"]["difficulty"]["label_ja"], "難")
        a = {k: v for k, v in with_d.items() if k != "reference"}
        b = {k: v for k, v in without.items() if k != "reference"}
        self.assertEqual(a, b)                                                            # reference以外(照合に使う項目)は不変


class PromptIntactTest(unittest.TestCase):
    def test_selection_prompts_unchanged_and_not_difficulty_aware(self):
        import er119_kp_p7w5_prompts_01 as p
        self.assertEqual(p.P7_SHA256, p.P7_SHA256_PINNED)
        self.assertEqual(p.W5P_SHA256, p.W5P_SHA256_PINNED)
        self.assertNotIn("difficulty", p.P7_TEXT.lower())

    def test_prompt_states_not_a_gate_and_four_levels(self):
        for w in ("easy", "medium", "hard", "rare", "合否を決めるものではなく"):
            self.assertIn(w, dg.PROMPT_TEXT)

    def test_user_example_expressions_are_not_in_prompt_anchors(self):
        """検証用にユーザー原文の例(rely on/make room for/narrow down)をPrompt内の目安へ入れない(過適合防止・委任_02の保留検証用)。"""
        for w in ("rely on", "make room for", "narrow down"):
            self.assertNotIn(w, dg.PROMPT_TEXT)


if __name__ == "__main__":
    unittest.main()
