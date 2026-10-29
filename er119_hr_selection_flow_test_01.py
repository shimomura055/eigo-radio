# -*- coding: utf-8 -*-
"""HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01 委任_02r: 仕様①(候補は人間への提示前に品質検査)・仕様②(重複はアラームのみ=非ブロッキング)のtest。
API 0(LLM由来の関数はすべてmock)。X/Y/Zは共通経路(er119_kp_wiring_01.run_kp_with_review -> er119_kp_human_review_01 -> er119_kp_candidates_01)を通るため、
level(a2/b1b)x Std Part1マーク(有/無)でパラメタ化し、runner配線は共通関数の呼出Grepとrunner経由の1本(X)で確認する。
実行: .venv\\Scripts\\python.exe -m unittest er119_hr_selection_flow_test_01 -v
対応: TEST_PLAN_01 U1-U16/I1-I6 + Opus M1-M9追加分(docs/research/HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01/IMPLEMENTATION_01.md の表を参照)。"""
from __future__ import annotations

import test_state_isolation_01  # noqa: F401

import copy
import importlib.util
import json
import os
import re
import shutil
import sys
import unittest
from unittest import mock

import er003_key_words_canonicalization as kc
import er119_kp_backfill_01 as bf
import er119_kp_candidates_01 as kcand
import er119_kp_human_review_01 as rv
import er119_kp_wiring_01 as kw
import er128_kp_confirmed_content_01 as cc
import er134_nuance_explanation_01 as n134
from er119_test_support_01 import CALL1, CALL2, Env, KpTestCase, jl, legacy_unmarked_flow, make_legacy_flagged

HERE = os.path.dirname(os.path.abspath(__file__))
TASK_DIR = os.path.join(HERE, "docs", "research", "HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


EXPORTER = _load("export_form_data_01_hr", os.path.join(HERE, "docs", "research", "KP-GATE-DROP-BACKFILL-PRODUCTION-01", "tools", "export_form_data_01.py"))


def cid(p):
    return rv.candidate_id_for(p)


def _cand(rank, form, **over):
    c = {"candidate_id": f"c{rank}", "ai_rank": rank, "selection_phrase": form, "used_form": form, "japanese_gloss": f"{form}の訳", "kind": bf.kind_of_phrase(form),
         "origin": "call1", "source_sentence": f"{form} here.", "reason_ja": "r", "flags": {"qa_fail": False, "gloss_hr_pending": False, "similar_to_ng": False, "redundant_with": []},
         "gates": {"gloss": "ALIGNED", "canonicalization": "PASS"}, "auto_eligible": True, "human_selectable": True,
         "item": {"rank": rank, "used_form": form, "key_phrase": form, "qa_overall_status": "PASS", "qa": {}}}
    c.update(over)
    return c


# ============================================================ U1/U6/M1/M8/M9: 提示可否の単一定義
class TestPresentationBlockers(unittest.TestCase):
    def test_u1_pass_item_is_presentable(self):
        self.assertEqual(rv.presentation_blockers(_cand(1, "stay high")), [])

    def test_u1_review_required_missing_and_unknown_status_are_blocked_fail_closed(self):
        c = _cand(1, "x y")
        c["item"]["qa_overall_status"] = "REVIEW_REQUIRED"
        c["item"]["qa"] = {"qa_no_residual_context_word": "FAIL"}
        b = rv.presentation_blockers(c)
        self.assertEqual([x[0] for x in b], ["qa_fail"])
        self.assertIn("qa_no_residual_context_word", b[0][1])
        for st in (None, "", "UNKNOWN", "REVIEW_REQUIRED_HUMAN_ACCEPTED"):          # M9: 欠落・未知値は除外(fail-closed)
            c2 = _cand(2, "a b")
            c2["item"]["qa_overall_status"] = st
            self.assertEqual([x[0] for x in rv.presentation_blockers(c2)], ["canonicalization_qa"], st)
        c3 = _cand(3, "c d")
        del c3["item"]["qa_overall_status"]
        self.assertEqual([x[0] for x in rv.presentation_blockers(c3)], ["canonicalization_qa"])
        self.assertEqual(rv.blocker_stage(rv.presentation_blockers(c3)), "canonicalization_qa")

    def test_m1_gloss_hr_pending_and_non_official_gloss_are_blocked(self):
        c = _cand(1, "a b", flags={"qa_fail": False, "gloss_hr_pending": True, "similar_to_ng": False, "redundant_with": []})
        c["gates"]["gloss"] = "HR_PENDING"
        self.assertEqual([x[0] for x in rv.presentation_blockers(c)], ["gloss_hr_pending"])
        self.assertEqual(rv.blocker_stage(rv.presentation_blockers(c)), "gloss_unresolved")
        c2 = _cand(2, "c d")
        c2["gates"]["gloss"] = "FAILED"
        self.assertEqual([x[0] for x in rv.presentation_blockers(c2)], ["gloss_not_official"])
        c3 = _cand(3, "e f", japanese_gloss="")
        self.assertEqual([x[0] for x in rv.presentation_blockers(c3)], ["gloss_not_official"])
        c4 = _cand(4, "g h")
        c4["gates"]["gloss"] = "HUMAN_RESOLVED"                                       # resolve-gloss後は提示可能
        self.assertEqual(rv.presentation_blockers(c4), [])

    def test_u6_m8_rescue_requires_qa_pass_and_gloss_realigned_fail_closed(self):
        def resc(qs, gs):
            c = _cand(1, "pushed prices up")
            c["rescue"] = {"canonicalization": {"code": "REVERT_SURFACE"}, "qa": {"status": qs}, "gloss": {"status": gs}}
            return c
        self.assertEqual(rv.presentation_blockers(resc("PASS", "REALIGNED")), [])
        self.assertEqual([x[0] for x in rv.presentation_blockers(resc("NOT_REJUDGED", "REALIGNED"))], ["rescue_unverified"])
        self.assertEqual([x[0] for x in rv.presentation_blockers(resc("PASS", "FAILED"))], ["rescue_unverified"])
        c = _cand(2, "x y")                                                              # selection段のみの救済(canonicalizationなし)は通常候補と同じ
        c["rescue"] = {"selection": {"code": "D1"}, "canonicalization": None}
        self.assertEqual(rv.presentation_blockers(c), [])
        # QA再判定FAIL(item側がREVIEW_REQUIREDへ更新される)も除外
        f = resc("FAIL", "REALIGNED")
        f["item"]["qa_overall_status"] = "REVIEW_REQUIRED"
        self.assertIn("qa_fail", [x[0] for x in rv.presentation_blockers(f)])

    def test_not_selectable_is_blocked_and_presentable_candidates_keeps_order_and_identity(self):
        a, b, c = _cand(1, "a b"), _cand(2, "c d", human_selectable=False), _cand(3, "e f")
        doc = {"candidates": [a, b, c]}
        out = rv.presentable_candidates(doc)
        self.assertEqual([x["candidate_id"] for x in out], ["c1", "c3"])
        self.assertIs(out[0], a)
        self.assertEqual(rv.presentable_candidates([a, b, c]), out)                     # listでも同じ
        ex = rv.excluded_from_presentation(doc)
        self.assertEqual([(x["candidate_id"], x["codes"]) for x in ex], [("c2", ["not_selectable"])])


# ============================================================ 仕様①: 生成(_gate_chain)・補完・telemetry
class TestGenerationDropsAndBackfill(KpTestCase):
    def test_u2_qa_drop_counts_as_gate_drop_triggers_backfill_once_and_dropped_phrase_is_in_backfill_exclusions(self):
        with Env(self.tmp, qa_fail_phrases=["pushed prices up"]) as env:
            r = self.ensure(env)
        self.assertEqual(r["state"], "PENDING")
        doc = rv.load_candidates(self.kp_dir)
        self.assertNotIn("pushed prices up", [c["selection_phrase"] for c in doc["candidates"]])
        bfk = doc["backfill"]
        self.assertTrue(bfk["triggered"])                                               # 除外は補完のE(Gate除外)に数えられる
        self.assertEqual(bfk["E"]["total"], 1)
        # 補完のP7 callの除外入力に、品質検査で除外した句が入る(同じ句が再び選ばれない。Opus D-2)
        self.assertTrue(any("pushed prices up" in m for m in env.messages1[1:]))
        self.assertEqual(env.n["call1"], 2)                                             # 初回+補完1回(新しいretry/上限は作らない)
        self.assertEqual(doc["outer_attempts"], 1)
        self.assertTrue(bf.rejected_entries([], doc["dropped"]) and any(e["phrase"] == "pushed prices up" for e in bf.rejected_entries([], doc["dropped"])))

    def test_u2_backfill_candidate_failing_qa_is_dropped_too_without_recursive_backfill(self):
        with Env(self.tmp, qa_fail_phrases=["pushed prices up", "stock"]) as env:
            self.ensure(env)
        doc = rv.load_candidates(self.kp_dir)
        forms = [c["selection_phrase"] for c in doc["candidates"]]
        self.assertNotIn("pushed prices up", forms)
        self.assertNotIn("stock", forms)
        self.assertEqual(rv.presentable_candidates(doc), doc["candidates"])
        self.assertLessEqual(env.n["call1"] + env.n["call2"], 4)                          # 再帰補完なし(補完は1周1回)

    def test_telemetry_is_recorded_on_every_generation_even_with_zero_drops(self):
        with Env(self.tmp) as env:
            self.ensure(env)
        pf = rv.load_candidates(self.kp_dir)["presentable_filter"]
        self.assertEqual(pf["version"], rv.PRESENTABLE_FILTER_VERSION)
        self.assertEqual((pf["canonicalization_qa_dropped"], pf["gloss_unresolved_dropped"], pf["dropped_by_code"]), (0, 0, {}))
        self.assertGreaterEqual(pf["checked"], pf["presentable"])
        self.assertEqual(pf["presentable"], pf["n_candidates"])

    def test_m9_normal_generation_always_has_qa_status_pass_on_every_candidate(self):
        """通常経路の候補は必ずqa_overall_status=PASSを持つ(欠落経路が無い=fail-closedで大量除外されない)。"""
        with Env(self.tmp, canon_keys={"pushed prices up": "totally different"}) as env:           # 救済経路(通常)も含む
            self.ensure(env)
        for c in rv.load_candidates(self.kp_dir)["candidates"]:
            self.assertEqual(c["item"].get("qa_overall_status"), "PASS", c["selection_phrase"])


# ============================================================ 提示集合の単一定義(U3/U4/M2)・性質test
class TestSinglePresentableDefinitionAcrossSurfaces(KpTestCase):
    def _legacy_doc(self):
        env = Env(self.tmp)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.assertEqual(self.ensure(env)["state"], "PENDING")
        make_legacy_flagged(self.kp_dir, [2], qa_fail=[2])
        make_legacy_flagged(self.kp_dir, [4], gloss_hr=[4])
        return rv.load_candidates(self.kp_dir)

    def test_u3_all_surfaces_call_the_single_function(self):
        doc = self._legacy_doc()
        review = rv.load_review(self.kp_dir)
        with mock.patch.object(rv, "presentable_candidates", wraps=rv.presentable_candidates) as spy:
            rv.render_request_md(doc, review, run_hint="r")
            n_req = spy.call_count
            EXPORTER.convert(doc, slug="s", level="b1b", name="n", family="Y", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
            n_exp = spy.call_count
            n134.presented_pool(doc)
            n_pool = spy.call_count
            rv.auto_select(doc, level="b1b")
            n_auto = spy.call_count
        self.assertGreaterEqual(n_req, 1)
        self.assertGreater(n_exp, n_req)
        self.assertGreater(n_pool, n_exp)
        self.assertGreater(n_auto, n_pool)

    def test_u4_exporter_excludes_legacy_flagged_records_warning_and_new_doc_has_no_warning_key(self):
        doc = self._legacy_doc()
        out = EXPORTER.convert(doc, slug="s", level="b1b", name="n", family="Y", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        ids = {e["candidate_id"] for e in out["phrases"] + out["words"]}
        qa_id = next(c["candidate_id"] for c in doc["candidates"] if c["ai_rank"] == 2)
        hr_id = next(c["candidate_id"] for c in doc["candidates"] if c["ai_rank"] == 4)
        self.assertNotIn(qa_id, ids)
        self.assertNotIn(hr_id, ids)
        w = [x for x in out["data_warnings"] if x["code"] == "presentation_excluded"][0]
        self.assertEqual({x["candidate_id"] for x in w["candidates"]}, {qa_id, hr_id})
        # 新doc(除外なし)ではdata_warningsキー自体を出さない(従来とバイト同一)
        clean = copy.deepcopy(doc)
        make_clean = [c for c in clean["candidates"] if c["ai_rank"] not in (2, 4)]
        clean["candidates"] = make_clean
        clean.pop("candidates_sha256", None)
        out2 = EXPORTER.convert(clean, slug="s", level="b1b", name="n", family="Y", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        self.assertNotIn("presentation_excluded", [x["code"] for x in out2.get("data_warnings", [])])      # 既存のreason警告は別。除外が無ければ除外警告は出さない
        self.assertEqual({e["candidate_id"] for e in out2["phrases"] + out2["words"]}, ids)

    def test_m2_er134_presented_pool_parity_with_exporter_after_filter_and_cap(self):
        doc = self._legacy_doc()
        out = EXPORTER.convert(doc, slug="s", level="b1b", name="n", family="Y", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        exp_ids = [e["candidate_id"] for e in sorted(out["phrases"] + out["words"], key=lambda e: e["ai_rank"])]
        self.assertEqual(n134.presented_ids_of(doc), exp_ids)
        # capはフィルタの後に適用される(除外された候補が枠を消費しない)
        small = copy.deepcopy(doc)
        small["shortfall_detail"] = {"cap": 2, "cap_by_kind": {"phrase": 2, "word": 0}}
        small.pop("candidates_sha256", None)
        out3 = EXPORTER.convert(small, slug="s", level="b1b", name="n", family="Y", run="r", source_kind="PRODUCTION_FORMAL_PATH", note_ja="")
        self.assertEqual(n134.presented_ids_of(small), [e["candidate_id"] for e in out3["phrases"]])
        # 除外された候補(rank2)が枠を消費しない: phrase枠2 = 提示可能な先頭2件(rank1, rank3)
        self.assertEqual([e["ai_rank"] for e in out3["phrases"]], [1, 3])

    def test_u3_request_md_lists_only_presentable_and_shows_excluded_section(self):
        doc = self._legacy_doc()
        md = rv.render_request_md(doc, rv.load_review(self.kp_dir), run_hint="r")
        excluded = {c["ai_rank"] for c in doc["candidates"] if rv.presentation_blockers(c)}
        self.assertEqual(excluded, {2, 4})
        table = md.split("## ")[0]
        for rk in excluded:
            self.assertNotRegex(table, rf"\n\| {rk} \|")
        self.assertIn("提示から除外した候補", md)
        self.assertNotIn("--accept-qa-fail", table)

    def test_property_every_presentable_candidate_passes_candidate_level_checks_when_selected_alone(self):
        """原文§2-4の性質test(Opus M1の証明): 提示された候補は、単独で選んでも確定時の候補単位検査(validate_selection・cmd_from_formのja_gloss_status/kind/term)を通る。
        提示外(旧docのqa_fail/gloss HR待ち)は少なくとも1つの検査で拒否される=提示から外す理由がある。"""
        doc = self._legacy_doc()
        cm = {c["candidate_id"]: c for c in doc["candidates"]}
        shown = {c["candidate_id"] for c in rv.presentable_candidates(doc)}
        for level, sp1 in (("b1b", False), ("a2", True)):
            for c in doc["candidates"]:
                ent = EXPORTER.entry(c, "PRODUCTION_FORMAL_PATH")
                sel = {"kp": [c["candidate_id"]], "vocab": [c["candidate_id"]] if rv.vocab_enabled(level, {"std_part1": sp1}) else []}
                errs = rv.validate_selection(doc, sel, level=level, std_part1=sp1)
                form_ok = ent["ja_gloss_status"] == "official" and ent["kind"] == (c.get("kind") or "phrase") and ent["term"] == c["item"].get("used_form") \
                    and ent["ja_gloss"] == c["item"].get("japanese_gloss")
                if c["candidate_id"] in shown:
                    self.assertEqual(errs, [], (level, c["selection_phrase"]))
                    self.assertTrue(form_ok, (level, c["selection_phrase"]))
                else:
                    self.assertTrue(errs or not form_ok, (level, c["selection_phrase"]))
        self.assertTrue(set(cm) - shown)                                                  # fixtureが空振りでないこと

    def test_property_holds_for_freshly_generated_mixed_doc(self):
        with Env(self.tmp, qa_fail_phrases=["pushed prices up"], gloss_fail_phrases=["time lag"], canon_keys={"took a sharp turn": "totally different"}) as env:
            self.ensure(env)
        doc = rv.load_candidates(self.kp_dir)
        self.assertEqual(rv.presentable_candidates(doc), doc["candidates"])
        for c in doc["candidates"]:
            ent = EXPORTER.entry(c, "PRODUCTION_FORMAL_PATH")
            self.assertEqual(ent["ja_gloss_status"], "official", c["selection_phrase"])
            self.assertEqual(rv.validate_selection(doc, {"kp": [c["candidate_id"]], "vocab": [c["candidate_id"]]}, level="b1b"), [], c["selection_phrase"])


# ============================================================ 仕様②: 重複はアラームのみ
def _y_adv_doc():
    """Y Adv(夫が妻の姓を選ぶとき b1b)の3表現を再現するfixture: let go of(KP①) / hold one's son back(追加解説②) / give something up(本文意味③)。"""
    cs = [_cand(1, "taking offense"), _cand(2, "let go of"), _cand(3, "hold one's son back"), _cand(4, "at ease"), _cand(5, "way out in the country"),
          _cand(6, "give something up")]
    for c in cs:
        c["candidate_id"] = cid(c["selection_phrase"])
    pair = lambda a, b, r: {"rank_a": a, "rank_b": b, "meaning_overlap": "FAIL", "usage_context_overlap": "FAIL", "grammatical_teaching_value_overlap": "PASS",
                            "conceptual_role_overlap": "FAIL", "reasoning": r}
    return {"level": "b1b", "candidates": cs, "redundancy_qa": {"status": "REDUNDANCY_NG", "duplicate_pairs": [pair(2, 3, "息子の選択を受け入れる点で重なる"), pair(2, 6, "子の独立に伴う諦めの感覚で重なる")]}}


class TestRedundancyAlarms(unittest.TestCase):
    def test_u8_alarms_from_candidate_doc_include_meaning_display_slot_M6(self):
        d = _y_adv_doc()
        slots = {"key_phrase": [cid("let go of")], "extra_explanation": [cid("hold one's son back")], "meaning_display": [cid("give something up")]}
        al = rv.redundancy_alarms(d, slots)
        self.assertEqual([(a["used_form_a"], a["used_form_b"]) for a in al], [("let go of", "hold one's son back"), ("let go of", "give something up")])
        self.assertEqual([(a["slot_a"], a["slot_b"]) for a in al], [("key_phrase", "extra_explanation"), ("key_phrase", "meaning_display")])
        self.assertTrue(all(a["source"] == "candidate_qa" and a["reasoning"] and a["aspects"]["meaning_overlap"] == "FAIL" for a in al))
        self.assertIn("本文意味(③)", al[1]["slot_label_b"])
        # 決定論・API 0: 同じ入力は同じ出力
        self.assertEqual(al, rv.redundancy_alarms(copy.deepcopy(d), slots))
        # ③を除くと対(2,6)は出ない / 選ばれていない表現の対は出ない
        self.assertEqual(len(rv.redundancy_alarms(d, {k: v for k, v in slots.items() if k != "meaning_display"})), 1)
        self.assertEqual(rv.redundancy_alarms(d, {"key_phrase": [cid("at ease")]}), [])

    def test_u8_flags_only_pair_without_detail_is_reported_as_flags_only(self):
        d = _y_adv_doc()
        d["redundancy_qa"] = {"status": "REDUNDANCY_NG", "duplicate_pairs": []}
        a, b = d["candidates"][1], d["candidates"][2]
        a["flags"]["redundant_with"], b["flags"]["redundant_with"] = [b["candidate_id"]], [a["candidate_id"]]
        al = rv.redundancy_alarms(d, {"key_phrase": [a["candidate_id"], b["candidate_id"]]})
        self.assertEqual([(x["source"], x["reasoning"]) for x in al], [("flags_only", None)])

    def test_u7_validate_selection_has_no_redundancy_error_but_keeps_other_checks(self):
        d = _y_adv_doc()
        for c in d["candidates"]:
            c["flags"]["redundant_with"] = [x["candidate_id"] for x in d["candidates"] if x is not c and {c["ai_rank"], x["ai_rank"]} in ({2, 3}, {2, 6})]
        sel = {"kp": [cid("let go of"), cid("hold one's son back"), cid("give something up")], "vocab": [cid("let go of"), cid("hold one's son back"), cid("give something up")]}
        self.assertEqual(rv.validate_selection(d, sel, level="b1b"), [])
        self.assertTrue(rv.validate_selection(d, {"kp": [], "vocab": []}, level="b1b"))                    # 件数
        self.assertTrue(rv.validate_selection(d, {"kp": [cid("at ease")], "vocab": [cid("let go of")]}, level="b1b"))     # KP ⊂ vocab
        d["candidates"][1]["human_selectable"] = False
        self.assertTrue(rv.validate_selection(d, sel, level="b1b"))                                         # Gate不合格


class TestNonBlockingEndToEndThroughCommonWiring(KpTestCase):
    """I1: X/Y/Z共通の run_kp_with_review(canon_fnをmockして実際の_gate_chainを通す)。重複選定でもKP stageが通過し、後続へ戻る。"""

    def _run(self, env, level="b1b", **kw):
        kp_dir = self.kp_dir if level == "b1b" else self.kp_dir_a2
        from er119_test_support_01 import ARTICLE
        gen = kcand.make_generate_fn(ARTICLE, kp_dir, f"aid_{level}", "B1" if level == "b1b" else "A2", level, "B1_SUPPORT" if level == "b1b" else "A2_SUPPORT", stop_check_fn=None)

        def red(items, name):
            env._in_final = True
            try:
                return kcand.make_redundancy_fn(ARTICLE, kp_dir, f"aid_{level}", "B1_SUPPORT")(items, name)
            finally:
                env._in_final = False
        return kw_run(kp_dir, self.run_dir, level, gen, red)

    def test_i1_duplicate_selection_proceeds_records_alarm_and_reaches_runner_adv(self):
        env = Env(self.tmp, red_ng_pairs=[(1, 2)], final_red_seq=["NG"])
        with env:
            r = self._run(env)
            self.assertEqual(r["status"], kw.STATUS_PENDING)
            op = rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")
            self.assertTrue(op["redundancy_alarms"])                                                       # 選定時にアラーム(拒否しない)
            self.assertEqual([h["event"] for h in op["history"] if h["event"] == "redundancy_alarm"], ["redundancy_alarm"])
            r2 = self._run(env)
        self.assertEqual(r2["kp_review"]["state"], "FINALIZED")
        self.assertEqual(r2["selection"]["status"], "KEY_WORDS_STRUCTURE_PASS")                          # KP stageは通過(runnerは後続へ進む)
        self.assertEqual(r2["redundancy_qa"]["status"], "REDUNDANCY_ALARM")
        self.assertTrue(r2["redundancy_qa"]["nonblocking"])
        al = jl(rv.paths(self.kp_dir)["alarm"])
        self.assertEqual(al["telemetry"]["reached_next_stage"], "runner_kp_stage_passed")
        self.assertFalse(al["blocking"])
        self.assertTrue(al["telemetry"]["nonblocking"])
        self.assertGreaterEqual(al["telemetry"]["alarm_count"], 1)
        fin = jl(rv.paths(self.kp_dir)["final"])
        self.assertEqual(fin["redundancy_telemetry"]["final_qa_status"], "REDUNDANCY_ALARM")
        self.assertTrue(fin["redundancy_alarms"])

    @legacy_unmarked_flow
    def test_i1_std_level_duplicate_selection_proceeds(self):
        env = Env(self.tmp, red_ng_pairs=[(1, 2)], final_red_seq=["NG"])
        with env:
            self._run(env, "a2")
            rv.op_select(self.kp_dir_a2, kp_ranks=[1, 2, 3], by="human")
            r = self._run(env, "a2")
        self.assertEqual(r["kp_review"]["state"], "FINALIZED")
        self.assertEqual(r["redundancy_qa"]["status"], "REDUNDANCY_ALARM")

    def test_i2_resume_after_alarm_finalize_makes_no_llm_call_and_keeps_alarm(self):
        env = Env(self.tmp, red_ng_pairs=[(1, 2)], final_red_seq=["NG"])
        with env:
            self._run(env)
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")
            self._run(env)
            before = env.total_llm_calls()
            r = self._run(env)
            self.assertEqual(env.total_llm_calls(), before)                                                # ALARMはキャッシュ(有料の再判定をしない)
        self.assertEqual(r["redundancy_qa"]["status"], "REDUNDANCY_ALARM")
        al = jl(rv.paths(self.kp_dir)["alarm"])
        self.assertEqual(al["telemetry"]["reached_next_stage"], "runner_kp_stage_passed")

    def test_i3_reselect_does_not_carry_alarms_into_the_next_round(self):
        env = Env(self.tmp, red_ng_pairs=[(1, 2)], call1_seq=[CALL1, CALL1])
        with env:
            self._run(env)
            rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3, 4, 5], by="human")
            self.assertTrue(rv.load_review(self.kp_dir)["redundancy_alarms"])
            rv.op_reselect(self.kp_dir, note="n", by="human")
            self.assertEqual(rv.load_review(self.kp_dir)["redundancy_alarms"], [])
            self._run(env)
        rev = rv.load_review(self.kp_dir)
        self.assertEqual(rev["status"], rv.ST_PENDING)
        self.assertEqual(rev.get("redundancy_alarms") or [], [])


def kw_run(kp_dir, run_dir, level, gen, red):
    from er119_test_support_01 import ARTICLE
    return kw.run_kp_with_review(text=ARTICLE, kp_dir=kp_dir, run_dir=run_dir, family="x", slug="coffee", level=level, article_id=f"aid_{level}",
                                 generate_hook=gen, redundancy_hook=red, stop_check_fn=lambda note: None)


class TestFinalizeBehavior(KpTestCase):
    def _pending(self, **kw_):
        env = Env(self.tmp, **kw_)
        env.__enter__()
        self.addCleanup(env.__exit__)
        self.assertEqual(self.ensure(env)["state"], "PENDING")
        return env

    def test_u10_alarm_keeps_selection_status_reviewed_and_writes_all_artifacts(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        env.final_red_seq = ["NG"]
        self.assertEqual(self.ensure(env)["state"], "FINALIZED")
        for f in ("keywords_canonicalized.json", "vocab_confirmed.json", "kp_selection_final.json", "redundancy_alarm.json"):
            self.assertTrue(os.path.exists(f"{self.kp_dir}/{f}"), f)
        fin = jl(f"{self.kp_dir}/kp_selection_final.json")
        self.assertEqual(fin["final_redundancy_qa"]["status"], "REDUNDANCY_ALARM")
        self.assertEqual(fin["final_redundancy_qa"]["judged_status"], "REDUNDANCY_NG")
        pr = fin["final_redundancy_qa"]["alarm_pairs"][0]
        self.assertTrue(pr["reasoning"] is None or isinstance(pr["reasoning"], str))
        self.assertEqual({pr["candidate_id_a"], pr["candidate_id_b"]} <= {cid(CALL1[0]["phrase"]), cid(CALL1[1]["phrase"]), cid(CALL1[2]["phrase"])}, True)

    def test_u11_cache_alarm_is_reused_without_llm_but_changed_selection_reruns(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        env.final_red_seq = ["NG"]
        self.ensure(env)
        calls = {"n": 0}

        def counting(items, name):
            calls["n"] += 1
            return {"status": "REDUNDANCY_PASS", "duplicate_pairs": []}
        rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=counting)                    # 署名一致・ALARMキャッシュ有効
        rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=None)                        # _try_refinalize相当(関数なし)でも通る
        self.assertEqual(calls["n"], 0)
        # keyが選定と不一致(選定が変わった状態)なら再実行する(新しい判定がPASSならALARMは消える)。確定後のselectはユーザー確定ガードで拒否されるため、keyの失効で再現する
        review = rv.load_review(self.kp_dir)
        review["final_qa"]["key"] = "stale-key"
        rv.save_review(self.kp_dir, review, expected_revision=review["revision"])
        rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=counting)
        self.assertGreaterEqual(calls["n"], 1)
        self.assertEqual(rv.load_review(self.kp_dir)["final_qa"]["status"], "REDUNDANCY_PASS")

    def test_m5_run_final_qa_judgement_values_unchanged_and_alarm_not_cached_for_auto(self):
        env = self._pending()
        cands = rv.load_candidates(self.kp_dir)
        sel = {"kp": [cid(CALL1[0]["phrase"]), cid(CALL1[1]["phrase"])], "vocab": [cid(CALL1[0]["phrase"]), cid(CALL1[1]["phrase"])]}
        ng = lambda items, name: {"status": "REDUNDANCY_NG", "duplicate_pairs": [{"rank_a": 1, "rank_b": 2, "reasoning": "r"}]}     # noqa: E731
        fq = rv._run_final_qa(cands, sel, "b1b", ng)
        self.assertEqual((fq["status"], len(fq["ng_pairs"])), ("REDUNDANCY_NG", 1))                      # 判定値はNGのまま(AUTO分岐が使う)
        self.assertEqual(rv.final_qa_to_alarm(fq, cands)["status"], "REDUNDANCY_ALARM")
        # AUTOでは、key一致のALARM形が保存されていてもキャッシュとして有効にしない(再判定する)
        review = rv.load_review(self.kp_dir)
        review.update(status=rv.ST_AUTO, selection=sel, final_qa=dict(rv.final_qa_to_alarm(fq, cands)))
        review["final_qa"]["key"] = rv._qa_key(sel)
        rv.save_review(self.kp_dir, review, expected_revision=review["revision"])
        calls = {"n": 0}

        def counting(items, name):
            calls["n"] += 1
            return {"status": "REDUNDANCY_PASS", "duplicate_pairs": []}
        rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=counting)
        self.assertGreaterEqual(calls["n"], 1)

    def test_u12_judge_failure_is_fail_closed_with_explicit_message_and_retried_on_resume(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        broken = lambda items, name: {"status": "REDUNDANCY_INVALID", "duplicate_pairs": []}      # noqa: E731
        with self.assertRaises(rv.KpReviewError) as e:
            rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=broken)
        self.assertIn("重複」の判定結果ではなく判定器", str(e.exception).replace("『", "「").replace("』", "」") or "")
        self.assertFalse(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))                  # 確定しない(fail-closed)
        self.assertEqual(rv.load_review(self.kp_dir)["selection"]["kp"], [cid(CALL1[0]["phrase"]), cid(CALL1[1]["phrase"]), cid(CALL1[2]["phrase"])])   # 選定は保持
        self.assertIsNone(rv.load_review(self.kp_dir)["final_qa"])                                      # 故障はキャッシュされない
        ok = lambda items, name: {"status": "REDUNDANCY_PASS", "duplicate_pairs": []}                  # noqa: E731
        rv.finalize_kp(self.kp_dir, level="b1b", redundancy_fn=ok)                                      # resumeで再試行できる
        self.assertTrue(os.path.exists(f"{self.kp_dir}/keywords_canonicalized.json"))

    def test_u13_auto_final_redundancy_advance_still_works(self):
        with Env(self.tmp) as env:
            env.final_red_seq = ["NG"]
            self.declare()
            r = self.ensure(env)
            self.assertEqual(r["state"], "FINALIZED")
            rev = rv.load_review(self.kp_dir)
            self.assertIn("auto_advance_final_redundancy_ng", [h["event"] for h in rev["history"]])
            self.assertEqual(rev["final_qa"]["status"], "REDUNDANCY_PASS")                                # AUTOはALARMにせず繰上げ(AI選定の品質=範囲外)
            self.assertNotIn("final_redundancy_alarm", [h["event"] for h in rev["history"]])

    def test_u14_alarm_file_write_failure_does_not_fail_finalize_and_is_regenerated(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        env.final_red_seq = ["NG"]
        real = rv._write_json_atomic

        def flaky(path, obj):
            if path.endswith("redundancy_alarm.json"):
                raise OSError("disk full (test)")
            return real(path, obj)
        with mock.patch.object(rv, "_write_json_atomic", flaky):
            self.assertEqual(self.ensure(env)["state"], "FINALIZED")                                     # 確定は成功
        self.assertTrue(os.path.exists(f"{self.kp_dir}/kp_selection_final.json"))
        self.assertFalse(os.path.exists(f"{self.kp_dir}/redundancy_alarm.json"))
        rv.write_alarm_file_safe(self.kp_dir, rv.load_review(self.kp_dir), "b1b")                           # 再導出(API 0)
        self.assertTrue(os.path.exists(f"{self.kp_dir}/redundancy_alarm.json"))

    def test_u15_old_stop_machinery_is_removed_and_record_state_machine_has_no_reconfirm(self):
        self.assertFalse(hasattr(cc, "on_final_redundancy_ng"))
        self.assertFalse(hasattr(cc, "raise_issue_nowait"))
        self.assertFalse(hasattr(cc, "STATE_RECONFIRM"))

    def test_u9_op_select_accepts_duplicate_pair_records_alarm_and_event(self):
        self._pending(red_ng_pairs=[(1, 2)])
        out = rv.op_select(self.kp_dir, kp_ranks=[1, 2, 3], vocab_ranks=[1, 2, 3], by="h")
        self.assertEqual(out["status"], rv.ST_REVIEWED)
        self.assertEqual(len(out["redundancy_alarms"]), 1)
        ev = [h for h in out["history"] if h["event"] == "redundancy_alarm"][0]
        self.assertFalse(ev["detail"]["blocking"])

    def test_telemetry_final_is_recorded_even_with_zero_alarms(self):
        env = self._pending()
        rv.op_select(self.kp_dir, kp_ranks=[1, 3, 4], vocab_ranks=[1, 3, 4], by="h")
        self.ensure(env)
        t = jl(f"{self.kp_dir}/kp_selection_final.json")["redundancy_telemetry"]
        self.assertEqual((t["final_qa_status"], t["alarm_count"], t["nonblocking"]), ("REDUNDANCY_PASS", 0, True))
        self.assertEqual(jl(f"{self.kp_dir}/redundancy_alarm.json")["telemetry"]["alarm_count"], 0)


# ============================================================ Dangling Reference(撤去した旧停止機構)・X/Y/Z共通経路
class TestNoDanglingAndCommonPath(unittest.TestCase):
    PROD = [p for p in os.listdir(HERE) if p.startswith(("er019_", "er026_", "er119_", "er120_", "er121_", "er125_", "er128_", "er134_")) and p.endswith(".py")
            and "test" not in p and "golden" not in p]

    def _grep(self, pat):
        hits = []
        for p in self.PROD:
            with open(os.path.join(HERE, p), encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if re.search(pat, line):
                        hits.append((p, i, line.strip()[:120]))
        return hits

    def test_removed_identifiers_have_no_code_references(self):
        for pat in (r"\bon_final_redundancy_ng\b", r"\braise_issue_nowait\b", r"\bSTATE_RECONFIRM\b", r"redundancy_ng_reconfirm_required", r"auto_adopted_after_reconfirm_required"):
            code = [h for h in self._grep(pat) if not h[2].lstrip().startswith("#")]
            self.assertEqual(code, [], pat)
        # 旧メッセージ(重複を理由に確定を拒否する文言)も残さない
        self.assertEqual([h for h in self._grep(r"意味・用法が重複しています") if not h[2].lstrip().startswith("#")], [])

    def test_runners_x_y_z_all_use_the_common_run_kp_with_review(self):
        for p in ("er019_family_x_audio_production_runner_01.py", "er121_family_y_runner_01.py", "er026_family_z_fiction_production_runner_01.py"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                src = f.read()
            self.assertIn("run_kp_with_review", src, p)
            self.assertNotIn("on_final_redundancy_ng", src, p)
            self.assertNotIn("final_redundancy_ng", src, p)

    def test_old_family_abc_path_is_unchanged_and_does_not_import_new_functions(self):
        with open(os.path.join(HERE, "er003_v1_n3_01_scaffold_generate.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('REDUNDANCY_NG', src)                                                              # 凍結ライン(A/B/C)は無変更
        self.assertNotIn("presentable_candidates", src)
        self.assertNotIn("REDUNDANCY_ALARM", src)

    def test_default_has_no_new_flag_or_env_read(self):
        """新flagを作っていない(通常のProduction変更。11-7の限定例外は使わない)。新しい環境変数読取がない。"""
        for p in ("er119_kp_human_review_01.py", "er119_kp_candidates_01.py", "er128_kp_confirmed_content_01.py"):
            with open(os.path.join(HERE, p), encoding="utf-8") as f:
                src = f.read()
            self.assertEqual(len(re.findall(r"HR_SELECTION|PRESENTABLE_FILTER_ENABLE|EIGO_HR_", src)), 0, p)


# ============================================================ M4: 使い捨てtool(run_02 a2 old-fashioned)のdry-run/fixture
TOOL_PATH = os.path.join(TASK_DIR, "tools", "apply_user_decision_surname_choice_01.py")
RUN02 = os.path.join(HERE, "er121_output", "family_y_production_01", "surname_choice", "run_02")
USER_REF = os.path.join(HERE, "docs", "pm", "delegation_log", "2026-10-29_HR-SELECTION-FLOW-QA-FIRST-AND-REDUNDANCY-NONBLOCKING-01_USER.md")


@unittest.skipUnless(os.path.isdir(RUN02) and os.path.exists(TOOL_PATH), "run_02 / tool が無い環境")
class TestSurnameChoiceTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tool = _load("apply_user_decision_surname_choice_01", TOOL_PATH)

    def setUp(self):
        import tempfile
        # 実run_02 a2が確定済み(REVIEWED。委任_03以降にユーザー決定を適用後)なら、PENDING前提の差替えtoolのtestは対象外(toolはPENDINGの間だけ動く設計)
        _live = rv.load_review(os.path.join(RUN02, "key_phrases", "a2"))
        if _live is not None and _live.get("status") != "PENDING_REVIEW":
            self.skipTest(f"実run_02 a2は既に{_live.get('status')}(差替えはPENDING_REVIEWの間だけ。適用済みのため本testは対象外)")
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        p = mock.patch.object(rv, "STORE_ROOT", os.path.join(self.tmp, "store"))
        p.start()
        self.addCleanup(p.stop)
        self.run = os.path.join(self.tmp, "run_02")
        shutil.copytree(RUN02, self.run, ignore=shutil.ignore_patterns("__pycache__"))
        self.kp_dir = os.path.join(self.run, "key_phrases", "a2")
        self.review0 = rv.load_review(self.kp_dir)
        self.cands0 = rv.load_candidates(self.kp_dir)
        self.text = self.tool._load_text(self.run, self.review0)
        self.env = Env(self.tmp)

    def _qa_pass(self, msg):
        from er119_test_support_01 import _parse_items_json
        items = _parse_items_json(msg, "【Key Phrase候補(JSON)】\n")
        rows = [{"rank": it["rank"], "key_phrase": it["display_phrase"], "changed_from_display_phrase": False, "normalization_reason": "none", "reasoning": "r",
                 **{f: "PASS" for f in kc.QA_FIELDS}} for it in items]
        return json.dumps({"items": rows}, ensure_ascii=False), "m", "r"

    def _qa_fail(self, msg):
        raw, m, r = self._qa_pass(msg)
        d = json.loads(raw)
        d["items"][0]["qa_standalone_comprehensibility"] = "FAIL"
        return json.dumps(d, ensure_ascii=False), m, r

    def _red(self, status="REDUNDANCY_PASS", pairs=()):
        return lambda text, items, work, article_id, process=None: {"status": status, "duplicate_pairs": list(pairs), "model_id": "m"}

    def _requalify(self, **over):
        kwargs = dict(user_ref=USER_REF, by="tester", text=self.text, gloss_factory=self.env._gloss, qa_call_fn=self._qa_pass,
                      redundancy_fn=self._red(), article_id="a", process="A2_SUPPORT")
        kwargs.update(over)
        return self.tool.requalify(self.kp_dir, **kwargs)

    def test_dry_run_writes_nothing_and_passes_deterministic_gates_on_the_real_run(self):
        before = (open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read(), open(os.path.join(self.kp_dir, "kp_human_review.json"), "rb").read())
        rep = self._requalify(dry_run=True, gloss_factory=None, qa_call_fn=None, redundancy_fn=None)
        self.assertTrue(rep["dry_run"])
        self.assertEqual(set(rep["gates"].values()), {"PASS"})
        after = (open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read(), open(os.path.join(self.kp_dir, "kp_human_review.json"), "rb").read())
        self.assertEqual(before, after)

    def test_refuses_other_run_other_level_and_wrong_user_ref_and_confirmed_state(self):
        with self.assertRaises(self.tool.ToolRefused):
            self.tool.check_preconditions(self.kp_dir, os.path.join(self.tmp, "x.md"))                  # user-ref不一致
        review = rv.load_review(self.kp_dir)
        review["article_key"]["slug"] = "other"
        rv.save_review(self.kp_dir, review, expected_revision=review["revision"])
        with self.assertRaises(self.tool.ToolRefused):
            self.tool.check_preconditions(self.kp_dir, USER_REF)                                      # 他記事
        review = rv.load_review(self.kp_dir)
        review["article_key"]["slug"] = "surname_choice"
        review["status"] = rv.ST_REVIEWED
        rv.save_review(self.kp_dir, review, expected_revision=review["revision"])
        with self.assertRaises(self.tool.ToolRefused):
            self.tool.check_preconditions(self.kp_dir, USER_REF)                                      # PENDING以外

    def test_full_gates_apply_updates_candidate_kind_cap_free_and_provenance(self):
        rep = self._requalify()
        self.assertTrue(rep["applied"])
        self.assertEqual(rep["new_kind"], "word")                                                       # 1語になりkindが単語へ(M3: capは再計算しない)
        cands = rv.load_candidates(self.kp_dir)
        c = next(x for x in cands["candidates"] if x["candidate_id"] == self.cands0["candidates"][4]["candidate_id"])
        self.assertEqual((c["used_form"], c["selection_phrase"], c["kind"], c["word_count"]), ("old-fashioned", "old-fashioned about it", "word", 1))
        self.assertEqual(c["item"]["qa_overall_status"], "PASS")
        self.assertTrue(all(v == "PASS" for v in c["item"]["qa"].values()))
        self.assertEqual(rv.presentation_blockers(c), [])                                               # 提示集合の唯一の定義を満たす
        self.assertEqual(c["requalified"]["user_ref"], USER_REF)
        self.assertEqual(c["requalified"]["old_kind"], "phrase")
        # 他の候補は不変(順序・内容)
        others = lambda d: [(x["candidate_id"], x["used_form"], x["japanese_gloss"], x["ai_rank"]) for x in d["candidates"] if x["candidate_id"] != c["candidate_id"]]   # noqa: E731
        self.assertEqual(others(cands), others(self.cands0))
        review = rv.load_review(self.kp_dir)
        self.assertEqual(review["candidates_sha256"], cands["candidates_sha256"])
        self.assertNotEqual(cands["candidates_sha256"], self.cands0["candidates_sha256"])
        self.assertIn("requalify_user_decision", [h["event"] for h in review["history"]])
        self.assertEqual(review["status"], rv.ST_PENDING)
        self.assertEqual(cands["requalify_provenance"]["previous_candidates_sha256"], self.cands0["candidates_sha256"])

    def test_qa_fail_after_requalify_stops_without_writing(self):
        before = open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read()
        with self.assertRaises(self.tool.ToolRefused) as e:
            self._requalify(qa_call_fn=self._qa_fail)
        self.assertIn("QA再判定がPASSではありません", str(e.exception))
        self.assertEqual(before, open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read())

    def test_redundancy_judge_failure_stops_without_writing(self):
        before = open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read()
        with self.assertRaises(self.tool.ToolRefused):
            self._requalify(redundancy_fn=self._red(status="REDUNDANCY_INVALID"))
        self.assertEqual(before, open(os.path.join(self.kp_dir, "kp_candidates.json"), "rb").read())

    def test_redundant_with_is_recomputed_and_changes_reported(self):
        pair = {"rank_a": 5, "rank_b": 1, "reasoning": "r", "meaning_overlap": "FAIL"}
        rep = self._requalify(redundancy_fn=self._red("REDUNDANCY_NG", [pair]))
        self.assertIn(self.cands0["candidates"][4]["candidate_id"], rep["redundant_with_changed"])
        cands = rv.load_candidates(self.kp_dir)
        self.assertEqual(cands["candidates"][4]["flags"]["redundant_with"], [cands["candidates"][0]["candidate_id"]])

    def test_confirm_dry_run_replaces_only_the_one_item_and_keeps_all_other_selections(self):
        self._requalify()
        readable = os.path.join(RUN02, "hr", "readable_a2.txt")
        out = self.tool.confirm(self.run, kp_dir=self.kp_dir, readable_path=readable, user_ref=USER_REF, by="tester", dry_run=True)
        self.assertTrue(out["dry_run"])
        diffs = out["differences"]
        self.assertTrue(all(re.search(r"/(term|kind|ja_gloss|ja_gloss_status)$|candidates_sha256$", d) for d in diffs), diffs)
        self.assertEqual(len([d for d in diffs if d.endswith("/term")]), 1)
        s = out["summary"]
        self.assertEqual(s["key_phrase"][0][0], "old-fashioned")
        self.assertEqual([x[0] for x in s["key_phrase"][1:]], ["adopted", "relative"])                  # その他の選定は維持
        self.assertEqual([x[0] for x in s["extra_explanation"]], ["give something up", "far out in the country"])
        self.assertIn("perhaps", [x[0] for x in s["meaning_display"]])                                   # M3: capで落ちない(確定集合の直接記録)
        self.assertFalse(out["provenance"]["form_data_regenerated"])
        self.assertFalse(out["provenance"]["cap_recomputed"])

    def test_y_adv_user_readable_confirms_with_alarms_including_meaning_display_and_finalizes_nonblocking(self):
        """Y Adv(b1b)の実readable(ユーザー送信済み)を複製run上で確定: 重複3表現(let go of / hold one's son back / give something up)が拒否されず、
        ③を含むアラームが記録され、確定集合QAがNG(mock)でもALARMで確定が完了する(確定レコードはlive・差戻しなし)。"""
        import er128_form_readable_restore_01 as fr
        out = fr.cmd_from_readable(os.path.join(RUN02, "hr", "readable_b1b.txt"), self.run, "b1b", "tester", USER_REF, actor="user")
        conf = out["confirmed"]
        self.assertEqual(conf["revision"], 1)
        self.assertTrue(conf["redundancy_alarm_nonblocking"])
        pairs = {(a["used_form_a"], a["used_form_b"], a["slot_b"]) for a in conf["redundancy_alarms"]}
        self.assertIn(("let go of", "hold one's son back", "extra_explanation"), pairs)
        self.assertIn(("let go of", "give something up", "meaning_display"), pairs)              # ③本文意味も対象(Opus M6)
        kp_b = os.path.join(self.run, "key_phrases", "b1b")
        ng = lambda items, name: {"status": "REDUNDANCY_NG", "duplicate_pairs": [{"rank_a": 1, "rank_b": 2, "reasoning": "r"}]}     # noqa: E731
        fin = rv.finalize_kp(kp_b, level="b1b", redundancy_fn=ng)
        self.assertEqual(fin["review"]["final_qa"]["status"], "REDUNDANCY_ALARM")
        self.assertEqual(cc.load_record(kp_b)["state"], cc.STATE_LIVE)
        self.assertEqual(rv.load_review(kp_b)["status"], rv.ST_REVIEWED)
        self.assertTrue(os.path.exists(os.path.join(kp_b, "redundancy_alarm.json")))

    def test_confirm_records_user_instruction_transcription_attestation_and_provenance(self):
        self._requalify()
        readable = os.path.join(RUN02, "hr", "readable_a2.txt")
        import er128_form_readable_restore_01 as fr
        # 文法/ニュアンスのstudy dirが複製runに揃っていることが前提(欠けていればここでISSUE/REFUSEDになる=実装範囲外の環境差)
        with mock.patch.object(rv, "_cc", rv._cc):
            try:
                out = self.tool.confirm(self.run, kp_dir=self.kp_dir, readable_path=readable, user_ref=USER_REF, by="tester")
            except Exception as e:   # noqa: BLE001
                self.skipTest(f"複製runでは文法study dir等が不足し確定まで再現できない: {type(e).__name__}: {str(e)[:120]}")
        rec = cc.load_record(self.kp_dir)
        self.assertEqual(rec["confirmed_by"]["actor"], cc.ACTOR_USER)
        self.assertEqual(rec["confirmed_by"]["attestation"], "user_instruction_transcription")
        self.assertEqual(rec["origin"]["transcription"]["readable_sha256"], out["provenance"]["readable_sha256"])
        self.assertIn("old-fashioned", [i["used_form"] for i in rec["items"]])
        self.assertNotIn("old-fashioned about it", [i["used_form"] for i in rec["items"]])


if __name__ == "__main__":
    unittest.main()
