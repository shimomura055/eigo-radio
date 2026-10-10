# -*- coding: utf-8 -*-
"""OPEN-243-TRANSLATION-NG-ANALYSIS-01 委任_03 M1-M3 Trialフラグの単体テスト(API呼び出しなし、¥0)。

確認すること: (1) フラグ未設定なら従来のprompt/挙動と完全に同一、(2) フラグONで意図した差分だけが出る、
(3) 承認済みChecker構成 OPEN233_APPROVED_FLOW_SWITCHES の値が変わっていない。
"""
import copy
import os
import unittest
from unittest import mock

import er003_v1_en_direct_vfl_01_generate as vfl01
import er003_v1_n3_01_advanced_adaptation_generate as adv
import er012_e_family_entertainment_two_level_runner_01 as runner
import er052_open233_self_recovery_flow_runner_01 as chk
import er052_open233_stage1_reclassify_01 as reclf


class M1Tests(unittest.TestCase):
    def test_prompt_unchanged_without_args(self):
        old = adv.FAMILY_X_IN_ONE_LINE_INSTRUCTION_TEMPLATE.format(article_text="# T\n\nB")
        self.assertEqual(adv.build_family_x_in_one_line_prompt("T", "B"), old)

    def test_prompt_with_ja_ledger_mustfix(self):
        p = adv.build_family_x_in_one_line_prompt("T", "B", ja_text="日本語", ledger_text="LEDGER",
                                                  must_fix=[{"fact_id": "F1", "claim_in_article": "c", "issue": "i", "explanation": "e"}])
        self.assertIn("[Japanese source article]\n日本語", p)
        self.assertIn("[Verified Fact Ledger]\nLEDGER", p)
        self.assertIn("Fact ID: F1", p)
        self.assertIn("Keep who did what to whom", p)

    def test_env_flag_default_off(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPEN243_M1", None)
            self.assertFalse(adv.open243_m1_enabled())
            os.environ["OPEN243_M1"] = "1"
            self.assertTrue(adv.open243_m1_enabled())

    @unittest.skip("LEGACY(RISK-FLAGGER-PRODUCTION-WIRING-01 C2, 2026-10-10): 対象関数は旧Fact Checker撤去(案P)でer012_eから物理削除された。再現はC2適用前commit f71dbb41のworktreeで行う。")
    def test_majors_only_in_summary(self):
        body = "Meta tested a feature. Contract workers made calls."
        summ = "Meta paused a calling feature after contract workers made calls without informing users."
        ok = [{"claim_in_article": "Meta paused a calling feature after contract workers made calls without informing users."}]
        self.assertTrue(runner.open243_majors_only_in_summary(ok, summ, body))
        lab = [{"claim_in_article": "In one line: “Meta paused a calling feature after contract workers made calls”"}]
        self.assertTrue(runner.open243_majors_only_in_summary(lab, summ, body))
        in_body = [{"claim_in_article": "Contract workers made calls."}]
        self.assertFalse(runner.open243_majors_only_in_summary(in_body, summ, body))
        short = [{"claim_in_article": "calls"}]
        self.assertFalse(runner.open243_majors_only_in_summary(short, summ, body))
        self.assertFalse(runner.open243_majors_only_in_summary([], summ, body))

    @unittest.skip("LEGACY(RISK-FLAGGER-PRODUCTION-WIRING-01 C2, 2026-10-10): 対象関数は旧Fact Checker撤去(案P)でer012_eから物理削除された。再現はC2適用前commit f71dbb41のworktreeで行う。")
    def test_summary_only_retry_success_and_failure(self):
        def fake_iol(client, title, body, **kw):
            return {"text": "S-new", "model": "m", "usage": {}}

        def comp(text, prior):
            return {"parsed": {"overall_status": "LEDGER_COMPLIANT", "deviations": [], "all_prior_issues_resolved": True}}

        def still_major(text, prior):
            return {"parsed": {"overall_status": "LEDGER_DEVIATION", "all_prior_issues_resolved": False,
                               "deviations": [{"severity": "MAJOR", "claim_in_article": "S-new sentence here", "issue": "i",
                                               "explanation": "e", "related_fact_id": "F1", "origin": "translation"}]}}

        with mock.patch.object(adv, "generate_family_x_in_one_line", side_effect=fake_iol) as g:
            r = runner.open243_m1_summary_only_retry(None, ledger_text="L", ja_text="J", title="T", body="B",
                                                     must_fix=[{"fact_id": "F1"}], dev_check_fn=comp)
            self.assertTrue(r["success"])
            self.assertEqual(g.call_count, 1)
            self.assertIn("## In one line\nS-new", r["final_text"])
        with mock.patch.object(adv, "generate_family_x_in_one_line", side_effect=fake_iol) as g:
            r = runner.open243_m1_summary_only_retry(None, ledger_text="L", ja_text="J", title="T", body="B",
                                                     must_fix=[{"fact_id": "F1"}], dev_check_fn=still_major, max_attempts=2)
            self.assertFalse(r["success"])
            self.assertEqual(g.call_count, 2)  # 最大2回
            self.assertEqual(r["reason"], "unresolved_after_max_attempts")

    @unittest.skip("LEGACY(RISK-FLAGGER-PRODUCTION-WIRING-01 C2, 2026-10-10): 対象関数は旧Fact Checker撤去(案P)でer012_eから物理削除された。再現はC2適用前commit f71dbb41のworktreeで行う。")
    def test_g3_translation_minor_gated_by_env(self):
        dev = {"parsed": {"deviations": [{"severity": "MINOR", "origin": "translation", "claim_in_article": "c",
                                          "changed_number": True}]}}
        os.environ.pop("OPEN243_G3_TELEMETRY_PATH", None)
        self.assertEqual(runner.open243_g3_record_translation_minor(dev, stage="s", out_dir="o"), 0)


class M2Tests(unittest.TestCase):
    def test_off_prompt_unchanged(self):
        self.assertIn("changed_actor: 発言主体・調査主体をLedgerと異なる人物・組織にすり替えている", vfl01.DEVIATION_PROMPT_TEMPLATE)
        os.environ.pop("OPEN243_M2", None)
        self.assertFalse(vfl01.open243_m2_enabled())

    def test_on_prompt_changes_only_description(self):
        new = vfl01.apply_open243_m2_to_prompt_template(vfl01.DEVIATION_PROMPT_TEMPLATE)
        self.assertIn("依頼主体", new)
        self.assertIn("受動化", new)
        self.assertIn("主語省略", new)
        self.assertIn("Brent", new)
        # severity規則(判定ルール節)と10フラグの並びは不変
        self.assertEqual(new.split("【判定ルール】")[1], vfl01.DEVIATION_PROMPT_TEMPLATE.split("【判定ルール】")[1])
        for k in vfl01.DEVIATION_FLAG_KEYS:
            self.assertIn(f"- {k}:", new)
        # hook-aware版にも同じ差し替えが効く
        vfl01.apply_open243_m2_to_prompt_template(vfl01.HOOK_AWARE_DEVIATION_PROMPT_TEMPLATE)

    def test_origin_template_has_source_placeholder(self):
        self.assertIn("{source_article_text}", vfl01.ORIGIN_INSTRUCTION_TEMPLATE_M2)
        vfl01.ORIGIN_INSTRUCTION_TEMPLATE_M2.format(source_article_text="x")


class M3Tests(unittest.TestCase):
    def _cands(self):
        base = {"unit_ids": ["S1"], "routes": ["r3"], "sub_reasons": ["model"], "sources": ["model_r3"], "issues": [],
                "related_fact_ids": ["F1"], "claim_text": "Meta was asked to negotiate bills."}
        a = dict(base, flags={"changed_actor": True, "changed_number": False})
        b = dict(base, unit_ids=["S2"], claim_text="Another claim.", flags={"changed_actor": False, "changed_number": True})
        return [a, b]

    def test_default_off_no_protection(self):
        os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)
        items, prot = reclf.claims_for_candidates(self._cands())
        self.assertEqual(len(items), 2)
        self.assertEqual(prot, set())

    def test_protect_changed_actor(self):
        os.environ["OPEN233_RECLASSIFY_PROTECT_FLAGS"] = "changed_actor"
        try:
            items, prot = reclf.claims_for_candidates(self._cands())
            self.assertEqual(prot, {"S1"})
            self.assertEqual([x["key"] for x in items], ["S2"])
        finally:
            os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)

    def test_unknown_flag_raises(self):
        os.environ["OPEN233_RECLASSIFY_PROTECT_FLAGS"] = "changed_bogus"
        try:
            with self.assertRaises(ValueError):
                reclf.protect_flags_from_env()
        finally:
            os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)

    def test_reclassify_keeps_protected_candidate(self):
        os.environ["OPEN233_RECLASSIFY_PROTECT_FLAGS"] = "changed_actor"
        try:
            calls = []

            def call_fn(label, dev, prompt, schema):
                calls.append(prompt)
                return {"results": [{"cid": "C1", "verdict": "SUPPORTED", "fact_tags": ["none"], "actor_match": "match",
                                     "counterpart_match": "n_a", "scope_match": "n_a", "qualifier_match": "n_a", "reason": "r"}]}, {"cost_jpy": 0.0}

            kept, info = reclf.reclassify_candidates({"ledger_text": "L", "article_text": "A"}, self._cands(), call_fn)
            keys = [reclf.ckey(c) for c in kept]
            self.assertIn("S1", keys)         # 保護: 除外されない
            self.assertNotIn("S2", keys)      # 保護なし: SUPPORTEDで除外
            self.assertEqual(info["n_protected_by_flags"], 1)
            self.assertNotIn("Meta was asked", calls[0])  # 保護された候補は再分類promptに載らない
        finally:
            os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)


class G3TelemetryTests(unittest.TestCase):
    @unittest.skip("LEGACY(RISK-FLAGGER-PRODUCTION-WIRING-01 C2, 2026-10-10): 対象関数は旧Fact Checker撤去(案P)でer012_eから物理削除された。再現はC2適用前commit f71dbb41のworktreeで行う。")
    def test_translation_minor_written_when_path_set(self):
        import json
        import tempfile
        d = tempfile.mkdtemp()
        path = os.path.join(d, "t.jsonl")
        dev = {"parsed": {"deviations": [
            {"severity": "MINOR", "origin": "translation", "claim_in_article": "c1", "changed_number": True, "issue": "i"},
            {"severity": "MINOR", "origin": "ja_source", "claim_in_article": "c2"},
            {"severity": "MAJOR", "origin": "translation", "claim_in_article": "c3"}]}}
        with mock.patch.dict(os.environ, {"OPEN243_G3_TELEMETRY_PATH": path}):
            self.assertEqual(runner.open243_g3_record_translation_minor(dev, stage="s", out_dir="o"), 1)
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["claim_in_article"], "c1")
        self.assertEqual(rows[0]["flags"], ["changed_number"])

    def test_reclassify_excluded_flagged_written_when_path_set(self):
        import json
        import tempfile
        d = tempfile.mkdtemp()
        path = os.path.join(d, "t.jsonl")
        base = {"unit_ids": ["S2"], "routes": ["r3"], "sub_reasons": ["model"], "sources": ["model_r3"], "issues": [],
                "related_fact_ids": ["F1"], "claim_text": "Another claim.", "flags": {"changed_number": True}}

        def call_fn(label, dev, prompt, schema):
            return {"results": [{"cid": "C1", "verdict": "SUPPORTED", "fact_tags": ["none"], "actor_match": "n_a",
                                 "counterpart_match": "n_a", "scope_match": "n_a", "qualifier_match": "n_a", "reason": "r"}]}, {"cost_jpy": 0.0}

        env = {"OPEN243_G3_TELEMETRY_PATH": path}
        with mock.patch.dict(os.environ, env):
            os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)
            kept, info = reclf.reclassify_candidates({"ledger_text": "L", "article_text": "A"}, [base], call_fn)
        self.assertEqual(kept, [])
        self.assertEqual(info["g3_n_excluded_flagged"], 1)
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        self.assertEqual(rows[0]["flags"], ["changed_number"])
        # パス未設定ならinfoにG3キーは増えない(従来と同一のキー集合)
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("OPEN243_G3_TELEMETRY_PATH", None)
            os.environ.pop("OPEN233_RECLASSIFY_PROTECT_FLAGS", None)
            _, info2 = reclf.reclassify_candidates({"ledger_text": "L", "article_text": "A"}, [dict(base)], call_fn)
        self.assertNotIn("g3_n_excluded_flagged", info2)
        self.assertNotIn("n_protected_by_flags", info2)


class ApprovedConfigUnchanged(unittest.TestCase):
    def test_approved_switches_values(self):
        s = chk.OPEN233_APPROVED_FLOW_SWITCHES
        self.assertEqual(s["FLOOR_MODE"], "number_only")
        self.assertTrue(s["STAGE1_RECLASSIFY"])
        self.assertEqual(s["PRECHECK_MODE"], "number_only")
        self.assertNotIn("OPEN233_RECLASSIFY_PROTECT_FLAGS", s)
        self.assertFalse(any("PROTECT" in k for k in s))


if __name__ == "__main__":
    unittest.main()
