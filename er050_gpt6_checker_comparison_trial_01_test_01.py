# -*- coding: utf-8 -*-
# ============================================================
# er050_gpt6_checker_comparison_trial_01_test_01.py
# GPT6-MODEL-COMPARISON-TRIAL-01 (Phase B, 委任_02) mock test
# ============================================================
# 実API呼び出しは行わない(client.responses.createをmockで差し替え)。
# 目的: (1) Prompt/Developer/schema sha256がPhase A記録と一致すること、
# (2) A/B/Meta fixtureのprompt逆展開がbyte単位で保存済みpromptを再現する
# こと、(3) fixture数がdesign書と一致すること(追加・削除がないこと)、
# (4) Guardrail(budget-jpy)が上限到達で以降のcallをskipすること、
# (5) 出力run jsonのschema、(6) post-hoc validation(MAJORかつ全flag false
# ならMINOR降格)がharness経由でも効くこと。
from __future__ import annotations

import json
import os
import shutil
import unittest
from types import SimpleNamespace
from unittest import mock

import er050_gpt6_checker_comparison_trial_01 as g6


class FixedConstantsTest(unittest.TestCase):
    def test_sha256_matches_phase_a(self):
        actual = g6.verify_fixed_constants()
        for k, v in actual.items():
            self.assertEqual(v, g6.PHASE_A_SHA256[k])


class FixtureExtractionTest(unittest.TestCase):
    def test_er009_fixture_count_is_nine(self):
        fx = g6.er009_fixtures()
        self.assertEqual(len(fx), 9)
        names = {f["expected_flag"] for f in fx}
        self.assertEqual(names, set(g6.er009t.FIXTURES.keys()))

    def test_step1_fixture_count(self):
        fx = g6.step1_fixtures()
        # 9 (ER-009-N1) + A2A3 + A4 + A5 = 12件(A1は再現不可のため対象外、design書明記どおり)
        self.assertEqual(len(fx), 12)
        ids = [f["id"] for f in fx]
        self.assertIn("A2A3", ids)
        self.assertIn("A4", ids)
        self.assertIn("A5", ids)
        self.assertNotIn("A1", ids)

    def test_step2_fixture_count(self):
        fx = g6.step2_fixtures()
        self.assertEqual(len(fx), 5)
        ids = {f["id"] for f in fx}
        self.assertEqual(ids, {"B1", "B2_hormuz", "B3", "B4", "Meta_run03_standard"})

    def test_step3_fixture_count(self):
        fx = g6.step3_fixtures()
        self.assertEqual(len(fx), 4)
        ids = {f["id"] for f in fx}
        self.assertEqual(ids, {
            "hormuz_run03_ja_original", "hormuz_run03_ja_r2",
            "hormuz_run03_advanced", "hormuz_run03_standard",
        })

    def test_audit_fixture_sha256_matches_design_doc(self):
        expected_sha = {
            "A2A3": "9e664e1ae373f629a58d283a5ad94334bbe76fe3dcf959a2c53f4b0b11d26877",
            "A4": "44fed56e96561ad5d5383805e00d3974340912e98bb97512d8a537a004e4f483",
            "B1": "e33d7fb09fdacfcfc931271ad4176f951ada0f1753fe20781ed4124b5faa51b2",
            "B2_hormuz": "0594e838284f32c2963d78b85000474451ac741a9cbcd06e03a7f773d04e97b1",
            "B3": "4bf6f67ce7d18ca1b79a40b28350e89126921e10d4a4cf7ba40c40cb530fe525",
            "B4": "bb21c160629c725afa3e82b58e8d1d1a32454ddb89a7e7d6e8a05f9dbf82f768",
            "Meta_run03_standard": "4016b8cb25a13dbc1809c0a147e7e992f64808ee0ff396189c0fa342a04e79a0",
        }
        fx_by_id = {f["id"]: f for f in g6.step1_fixtures() + g6.step2_fixtures()}
        for fid, sha in expected_sha.items():
            self.assertEqual(fx_by_id[fid]["source_sha256"], sha, f"{fid} sha256 mismatch")

    def test_reconstruction_matches_for_all_audit_fixtures(self):
        # load_audit_fixture内部で既にverify_reconstruction()がRuntimeErrorを
        # 投げる設計のため、ロード自体が例外なく通れば逆展開の正しさは保証されている。
        fixtures = g6.step1_fixtures() + g6.step2_fixtures() + g6.step3_fixtures()
        self.assertGreater(len(fixtures), 0)
        for f in fixtures:
            self.assertIsInstance(f["ledger_text"], str)
            self.assertIsInstance(f["article_text"], str)
            self.assertGreater(len(f["ledger_text"]), 0)
            self.assertGreater(len(f["article_text"]), 0)


class FixtureFilterTest(unittest.TestCase):
    def test_filter_by_id_returns_only_matching_fixture(self):
        fx = g6.step1_fixtures()
        filtered = g6.filter_fixtures_by_id(fx, "er009_changed_actor")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["id"], "er009_changed_actor")

    def test_filter_by_id_unknown_id_raises(self):
        fx = g6.step1_fixtures()
        with self.assertRaises(ValueError):
            g6.filter_fixtures_by_id(fx, "does_not_exist")

    def test_filter_by_id_preserves_multiple_order(self):
        fx = g6.step1_fixtures()
        filtered = g6.filter_fixtures_by_id(fx, "er009_changed_scope,er009_changed_actor")
        self.assertEqual([f["id"] for f in filtered], ["er009_changed_scope", "er009_changed_actor"])


def _make_fake_response(model_id, deviations, input_tokens=1000, output_tokens=200, cached=0):
    payload = {"deviations": deviations}
    usage = SimpleNamespace(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_tokens_details=SimpleNamespace(cached_tokens=cached),
        output_tokens_details=SimpleNamespace(reasoning_tokens=0),
    )
    return SimpleNamespace(
        output_text=json.dumps(payload), model=model_id, id=f"resp_fake_{model_id}", usage=usage,
    )


class GuardrailAndOutputTest(unittest.TestCase):
    def setUp(self):
        self.tmp_out = "er050_output/gpt6_checker_comparison_trial_01_TEST_TMP"
        g6.OUT_DIR = self.tmp_out
        g6.BUDGET_STATE_PATH = f"{self.tmp_out}/budget_state.json"
        if os.path.exists(self.tmp_out):
            shutil.rmtree(self.tmp_out)

    def tearDown(self):
        if os.path.exists(self.tmp_out):
            shutil.rmtree(self.tmp_out)

    def _fixture(self, name="dummy"):
        return {
            "id": name, "ledger_text": "[VERIFIED] F1: dummy fact.", "article_text": "Dummy article.",
            "source_article_text": None, "include_related_fact_id": False, "hook_aware": False,
            "gold_note": "test", "expected_flag": None, "baseline_parsed": None,
        }

    def test_post_hoc_downgrade_applied_via_harness(self):
        """MAJORだが全flag falseの応答は、run_deviation_check内部のpost-hoc処理で
        MINORへ自動降格される(harness経由でも効くことを確認、Validator自体は
        vfl01のものをそのまま使っているだけで複製していない)。"""
        deviations = [{
            "claim_in_article": "x", "issue": "y", "severity": "MAJOR",
            "changed_fact": False, "changed_scope": False, "changed_causality": False,
            "changed_certainty": False, "changed_number": False, "changed_actor": False,
            "changed_negation": False, "changed_comparison": False, "changed_time": False,
            "unsupported_new_claim": False, "explanation": "z",
        }]
        fake_client = mock.MagicMock()
        fake_client.responses.create.return_value = _make_fake_response("gpt-5.6-luna", deviations)
        # WIRING-01 Phase 2(O1): 旧5.6 harness検証中のみrequire_modelを素通し
        with mock.patch.object(g6.vfl01, "get_client", return_value=fake_client), \
                mock.patch.object(g6.vfl01.routing, "require_model", side_effect=lambda p, m: m):
            summary = g6.execute_step("step_test", [self._fixture()], ["gpt-5.6-luna"], budget_jpy=1000.0)
        run = summary["fixtures"][0]["runs"]["gpt-5.6-luna"][0]
        self.assertEqual(run["overall_status"], "LEDGER_COMPLIANT")
        self.assertTrue(run["deviations"][0]["auto_downgraded"])
        self.assertEqual(run["deviations"][0]["severity"], "MINOR")

    def test_guardrail_stops_when_budget_exceeded(self):
        """budget_jpyを極小に設定し、2回目以降のcallがskipされることを確認する。"""
        deviations = []
        fake_client = mock.MagicMock()
        # 1call目で高額usageを返し、即座に上限超過させる
        fake_client.responses.create.return_value = _make_fake_response(
            "gpt-6-luna", deviations, input_tokens=2_000_000, output_tokens=500_000,
        )
        fixtures = [self._fixture("f1"), self._fixture("f2")]
        with mock.patch.object(g6.vfl01, "get_client", return_value=fake_client):
            summary = g6.execute_step("step_test_budget", fixtures, ["gpt-6-luna"], budget_jpy=1.0)
        self.assertTrue(summary["stopped"])
        # f1は実行され(1回)、f2はskip
        f1_runs = summary["fixtures"][0]["runs"]["gpt-6-luna"]
        f2_runs = summary["fixtures"][1]["runs"]["gpt-6-luna"]
        self.assertNotIn("skipped", f1_runs[0])
        self.assertTrue(f2_runs[0].get("skipped"))

    def test_output_run_json_schema(self):
        deviations = [{
            "claim_in_article": "x", "issue": "y", "severity": "MINOR",
            "changed_fact": False, "changed_scope": False, "changed_causality": False,
            "changed_certainty": False, "changed_number": False, "changed_actor": False,
            "changed_negation": False, "changed_comparison": False, "changed_time": False,
            "unsupported_new_claim": False, "explanation": "z",
        }]
        fake_client = mock.MagicMock()
        fake_client.responses.create.return_value = _make_fake_response("gpt-6-luna", deviations)
        with mock.patch.object(g6.vfl01, "get_client", return_value=fake_client):
            g6.execute_step("step_test_schema", [self._fixture("f1")], ["gpt-6-luna"], budget_jpy=1000.0)
        run_path = f"{self.tmp_out}/step_test_schema/f1/gpt-6-luna/run_1.json"
        self.assertTrue(os.path.exists(run_path))
        with open(run_path, encoding="utf-8") as f:
            saved = json.load(f)
        for key in ("fixture_id", "model", "attempt", "prompt_sha256", "model_returned",
                    "usage", "elapsed_seconds", "raw_parsed", "parsed"):
            self.assertIn(key, saved)

    def test_model_is_only_varying_argument(self):
        """run_fixture_onceに渡すkwargsのうちmodel以外(prompt構成に影響する
        引数)がfixture定義由来で固定されており、モデル切替えループの中で
        書き換わらないことを確認する。"""
        fixture = self._fixture("f1")
        fake_client = mock.MagicMock()
        fake_client.responses.create.return_value = _make_fake_response("m", [])
        # WIRING-01 Phase 2(O1): run_deviation_checkが旧5.6を拒否するため、旧Trial harness検証中のみ素通し
        with mock.patch.object(g6.vfl01, "get_client", return_value=fake_client), \
                mock.patch.object(g6.vfl01.routing, "require_model", side_effect=lambda p, m: m):
            g6.run_fixture_once(fake_client, fixture, "gpt-5.6-luna")
            g6.run_fixture_once(fake_client, fixture, "gpt-6-luna")
        calls = fake_client.responses.create.call_args_list
        self.assertEqual(len(calls), 2)
        kwargs0, kwargs1 = calls[0].kwargs, calls[1].kwargs
        self.assertEqual(kwargs0["input"], kwargs1["input"])
        self.assertEqual(kwargs0["reasoning"], kwargs1["reasoning"])
        self.assertEqual(kwargs0["text"], kwargs1["text"])
        self.assertNotEqual(kwargs0["model"], kwargs1["model"])


if __name__ == "__main__":
    unittest.main()
