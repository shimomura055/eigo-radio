# -*- coding: utf-8 -*-
# OPEN-233-CHECKER-ACTION-POLICY-STAGE2-01 委任_01: W1(タイトル`# `記法保持)・W2(構造要素の前後対をRecheckへ)の単体テスト。
# 実データ=qvqc rep2(meta nb rep2)のcycle1タイトル書換え。ネットワークなし(¥0)。新挙動は環境変数スイッチ既定OFF。
from __future__ import annotations

import json
import os
import pathlib
import unittest
from unittest import mock

import er052_open233_self_recovery_flow_runner_01 as runner
import er052_open233_stage1_coverage_checker_01 as cov
from er052_open233_recheck_coverage_test_01 import FakeLLM, LEDGER

FX = pathlib.Path(__file__).parent / "er052_output" / "open233_stage2_01" / "precheck" / "fixtures"
BEFORE = (FX / "qvqc_rep2_before.md").read_text(encoding="utf-8")
ATT = json.loads((FX / "qvqc_rep2_cycle1_title_attempt.json").read_text(encoding="utf-8"))
TARGET, REVISED = ATT["targets"][0], ATT["revised"][0]
SW1, SW2 = "OPEN233_FIX_W1_TITLE_MARKUP", "OPEN233_FIX_W2_STRUCTURAL_RECHECK"


def _seg():
    return dict(segment_fn=runner.vs_sentence_segments_l6, initial_extra=runner.CAUSAL_SENTENCE_INITIAL_EN)


def _env(**kw):
    return mock.patch.dict(os.environ, kw, clear=False)


def _state():
    return {"cumulative_jpy": 0.0, "cumulative_calls": 0, "cumulative_errors": 0, "history": []}


def _ladder():
    claim_rec = {"claim_text": TARGET, "rewrite_kind": "delete", "materiality": "BLOCKING", "basis": "unsupported_relationship",
                 "rewrite_hint": "h", "dev": {"issue": "x"}}
    fixture = {"ledger_text": "[F-1] x", "article_text": BEFORE}
    with mock.patch.object(runner, "STRUCTURAL_ELEMENT_REWRITE", True), \
            mock.patch.object(runner, "simple_llm_call",
                              side_effect=lambda *a, **k: json.dumps({"revised_ranges": [REVISED]})):
        return runner.rewrite_ranges_ladder(None, _state(), [0], [], "t", fixture, "article_text", claim_rec)


class TestW1TitleMarkup(unittest.TestCase):
    def test_helper_restores_hash_prefix(self):
        out, fixed = runner.w1_preserve_title_markup([TARGET], [REVISED])
        self.assertEqual(out, ["# " + REVISED])
        self.assertEqual(fixed, [0])

    def test_helper_leaves_non_heading_and_already_marked(self):
        self.assertEqual(runner.w1_preserve_title_markup(["Plain."], ["Other."]), (["Other."], []))
        self.assertEqual(runner.w1_preserve_title_markup([TARGET], ["# " + REVISED])[1], [])

    def test_ladder_off_reproduces_current_behavior_title_becomes_hook_sentence(self):
        with _env(**{SW1: "0"}):
            res = _ladder()
        self.assertTrue(res["guard_ok"])
        self.assertIsNone(runner._en_title_line(res["updated_text"]))  # 現行=`# `が消える
        sp = cov.split_units(res["updated_text"], **_seg())
        self.assertNotIn("T", [u["id"] for u in sp["units"]])
        s11 = [u for u in sp["units"] if u["id"] == "S1.1"][0]
        self.assertTrue(s11["text"].startswith("Meta Tested"))  # タイトルがHook文S1.1として扱われる

    def test_ladder_on_keeps_title_as_title_unit(self):
        with _env(**{SW1: "1"}):
            res = _ladder()
        self.assertTrue(res["guard_ok"])
        self.assertEqual(runner._en_title_line(res["updated_text"]), "# " + REVISED)
        sp = cov.split_units(res["updated_text"], **_seg())
        t = [u for u in sp["units"] if u["id"] == "T"]
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0]["type"], "title")
        self.assertTrue(res["handoff"].get("w1_title_markup_restored"))

    def test_default_env_unset_is_off(self):
        env = {k: v for k, v in os.environ.items() if k != SW1}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(runner.stage2_fix_switch(SW1))


class TestW2StructuralRecheck(unittest.TestCase):
    PAIRS = [{"before": TARGET, "after": "# " + REVISED, "structural": True}]
    AFTER_W1ON = BEFORE.replace(TARGET, "# " + REVISED)
    AFTER_W1OFF = BEFORE.replace(TARGET, REVISED)

    def _run(self, after, pairs):
        llm = FakeLLM()
        res = cov.run_recheck_scope({"ledger_text": LEDGER, "article_text": after}, llm, BEFORE, [], structural_pairs=pairs, **_seg())
        return res, llm

    def test_off_prompt_has_no_pair_block_and_none_equals_empty(self):
        _, l0 = self._run(self.AFTER_W1ON, None)
        _, l1 = self._run(self.AFTER_W1ON, [])
        self.assertEqual([p for (_, p) in l0.calls], [p for (_, p) in l1.calls])
        self.assertTrue(all("書き換えられた構造要素" not in p for (_, p) in l0.calls))

    def test_on_title_pair_is_in_recheck_input(self):
        res, llm = self._run(self.AFTER_W1ON, self.PAIRS)
        for label, p in llm.calls:
            self.assertIn("書き換えられた構造要素", p)
            self.assertIn("before: " + TARGET, p)
            self.assertIn("after: # " + REVISED, p)
        self.assertIn("T", res["audit"]["scope_ids"])  # タイトル単位が判定対象

    def test_on_forces_after_unit_into_scope_even_when_unchanged_by_diff(self):
        # 差分上は変更なし(before==after)でも、前後対の後側と一致する単位はscopeへ入る
        res, _ = self._run(BEFORE, [{"before": "x y z", "after": TARGET, "structural": True}])
        self.assertIn("T", res["audit"]["scope_ids"])
        res0, _ = self._run(BEFORE, None)
        self.assertNotIn("T", res0["audit"]["scope_ids"])

    def test_runner_wrapper_passes_pairs_only_when_given(self):
        seen = {}

        def fake_scope(rf, call_fn, before_text, prior, **kw):
            seen.update(kw)
            return {"api_failure": False, "candidates": [], "prior_issues_resolved": [], "audit": {}}
        with mock.patch.object(runner.cov, "run_recheck_scope", fake_scope), \
                mock.patch.object(runner, "make_stage1_call_fn", lambda *a, **k: None), \
                mock.patch.object(runner, "make_reclassify_filter", lambda *a, **k: None):
            runner.run_recheck_coverage(None, {}, [0], [], "l", {"ledger_text": "", "article_text": "a"}, "a", [], "b")
            self.assertIsNone(seen["structural_pairs"])
            runner.run_recheck_coverage(None, {}, [0], [], "l", {"ledger_text": "", "article_text": "a"}, "a", [], "b",
                                        structural_pairs=self.PAIRS)
            self.assertEqual(seen["structural_pairs"], self.PAIRS)


class TestSaveR3SupportIds(unittest.TestCase):
    """作業5: OPEN233_SAVE_R3_SUPPORT_IDS(既定OFF)。OFFではauditにキーを作らない。"""
    AFTER = BEFORE.replace(TARGET, "# " + REVISED)

    def _scope(self):
        return cov.run_recheck_scope({"ledger_text": LEDGER, "article_text": self.AFTER}, FakeLLM(), BEFORE, [], **_seg())

    def test_off_has_no_support_ids_key(self):
        with _env(OPEN233_SAVE_R3_SUPPORT_IDS="0"):
            res = self._scope()
        self.assertNotIn("r3_support_fact_ids", res["audit"])

    def test_on_saves_support_ids_per_unit(self):
        with _env(OPEN233_SAVE_R3_SUPPORT_IDS="1"):
            res = self._scope()
        ids = res["audit"]["r3_support_fact_ids"]
        self.assertIn("T", ids)
        self.assertEqual(ids["T"], ["HF-001"])


if __name__ == "__main__":
    unittest.main()
