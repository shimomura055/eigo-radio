# -*- coding: utf-8 -*-
"""er053_cost_aggregate_01 / pricing / routing追加分のtest(¥0)。
実行: .venv/Scripts/python.exe -m pytest er053_cost_aggregate_01_test_01.py -q
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest

import er006_model_routing_contract_01 as routing
import er019_family_x_entertainment_production_runner_01 as runner
import er053_cost_aggregate_01 as ca

HERE = os.path.dirname(os.path.abspath(__file__))


class AggTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ca_test_")
        self.p = os.path.join(self.d, "raw_usage_log.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def w(self, recs):
        open(self.p, "w", encoding="utf-8").write("".join(json.dumps(r) + "\n" for r in recs))

    def test_openai_only_equals_existing_function(self):
        self.w([{"provider": "openai", "model_id": "gpt-6-luna", "stage": "s1", "input_tokens": 1000, "output_tokens": 500},
                {"provider": "openai", "model_id": "gpt-6-astra", "stage": "s2", "input_tokens": 2000, "output_tokens": 800}])
        old = runner.compute_stage_cost_breakdown(self.p)
        new = ca.compute_stage_cost_breakdown_multi(self.p)
        self.assertEqual(old["by_stage_jpy"], new["by_stage_jpy"])
        self.assertEqual(old["total_jpy"], new["total_jpy"])

    def test_existing_function_still_ignores_gemini(self):
        self.w([{"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A3.b1b",
                 "input_tokens": 1000, "output_tokens": 200}])
        self.assertEqual(runner.compute_stage_cost_breakdown(self.p)["total_jpy"], 0.0)   # 既存関数は無変更

    def test_gemini_counted_with_level_model_condition(self):
        self.w([{"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A3.b1b",
                 "input_tokens": 1000, "output_tokens": 200, "success": True},
                {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A4.a2",
                 "input_tokens": 1000, "output_tokens": 200, "success": True},
                {"provider": "gemini", "model_id": "gemini-3.5-flash-lite", "stage": "risk_flag.gemini35fl.A4.a2", "success": False},
                {"provider": "openai", "model_id": "gpt-6-luna", "stage": "risk_flag.luna.A3.b1b", "input_tokens": 1000, "output_tokens": 200}])
        r = ca.compute_stage_cost_breakdown_multi(self.p)
        exp = (1000 * 0.30 + 200 * 2.50) / 1e6 * 160.0
        self.assertAlmostEqual(r["by_stage_jpy"]["risk_flag.gemini35fl.A3.b1b"], round(exp, 3), places=3)
        self.assertAlmostEqual(r["by_stage_jpy"]["risk_flag.gemini35fl.A4.a2"], round(exp, 3), places=3)
        self.assertIn("gemini", r["by_provider_jpy"])
        s = ca.rf_stage_summary(r["by_stage_jpy"])
        self.assertEqual(set(s), {"b1b", "a2"})
        self.assertEqual(set(s["b1b"]), {"gemini35fl", "luna"})
        self.assertEqual(set(s["a2"]["gemini35fl"]), {"A4"})

    def test_unregistered_gemini_model_fail_closed(self):
        self.w([{"provider": "gemini", "model_id": "gemini-nope", "stage": "x", "input_tokens": 1, "output_tokens": 1}])
        with self.assertRaises(routing.PricingNotFoundError):
            ca.compute_stage_cost_breakdown_multi(self.p)

    def test_missing_log(self):
        self.assertEqual(ca.compute_stage_cost_breakdown_multi(os.path.join(self.d, "none"))["total_jpy"], 0.0)


class PricingRoutingAdditionTests(unittest.TestCase):
    NEW_MODEL = "gemini-3.5-flash-lite"
    NEW_KEYS = {"FAMILY_X_RF_LUNA", "FAMILY_X_RF_GEMINI", "FAMILY_X_FACTLOCK_R0", "FAMILY_X_FACTLOCK_REVISE"}

    def test_pricing_addition_only_and_existing_entries_untouched(self):
        """git HEAD(C1適用前でもC1 commit後でも成立する形): gemini-3.5-flash-lite以外のエントリはHEADと完全一致、
        gemini-3.5-flash-lite は 3 meter(0.30/0.03/2.50)だけ追加されている。"""
        old = subprocess.run(["git", "show", "HEAD:er005_output/cost_baseline_01/pricing_snapshot.json"], cwd=HERE,
                             capture_output=True).stdout.decode("utf-8")
        old_prices = [p for p in json.loads(old)["prices"] if p["model"] != self.NEW_MODEL]
        new_all = json.load(open(os.path.join(HERE, "er005_output/cost_baseline_01/pricing_snapshot.json"), encoding="utf-8"))["prices"]

        def _strip_astra_note(ps):
            # C3-4(2026-10-10): gpt-6-astraのnote文言のみ更新(価格値・他キーは不変)。noteだけ比較から除く。
            return [{k: v for k, v in p.items() if not (p["model"] == "gpt-6-astra" and k == "note")} for p in ps]
        self.assertEqual(_strip_astra_note([p for p in new_all if p["model"] != self.NEW_MODEL]), _strip_astra_note(old_prices))
        added = [p for p in new_all if p["model"] == self.NEW_MODEL]
        self.assertEqual([(p["meter"], p["price"]) for p in added],
                         [("input_tokens", 0.3), ("cached_input_tokens", 0.03), ("output_tokens", 2.5)])

    def test_routing_addition_only(self):
        old_src = subprocess.run(["git", "show", "HEAD:er006_model_routing_contract_01.py"], cwd=HERE, capture_output=True).stdout.decode("utf-8")
        ns = {}
        exec(compile(old_src, "old_routing", "exec"), ns)
        old_map = {k: v for k, v in ns["PROCESS_MODEL_MAP"].items() if k not in self.NEW_KEYS}
        for k, v in old_map.items():
            self.assertEqual(routing.PROCESS_MODEL_MAP[k], v, k)               # 既存キー不変
        self.assertEqual(set(routing.PROCESS_MODEL_MAP) - set(old_map), self.NEW_KEYS)
        self.assertEqual(routing.PROCESS_PROVIDER_MAP, ns["PROCESS_PROVIDER_MAP"])

    def test_every_new_routing_model_has_pricing(self):
        import er053_risk_flagger_production_01 as rf
        for key, prov in (("FAMILY_X_RF_LUNA", "openai"), ("FAMILY_X_RF_GEMINI", "gemini"),
                          ("FAMILY_X_FACTLOCK_R0", "openai"), ("FAMILY_X_FACTLOCK_REVISE", "openai")):
            rf.load_prices(routing.PROCESS_MODEL_MAP[key], prov)

    def test_astra_price_values(self):
        import er053_risk_flagger_production_01 as rf
        pr = rf.load_prices(routing.PROCESS_MODEL_MAP["FAMILY_X_FACTLOCK_REVISE"], "openai")
        # SOL61 E案(2026-10-11): R1/R2はgpt-6.1-sol(2.00/10.00 USD/1M)。旧Astra(10/50)からの移行(単価値はsnapshot登録値、変更なし)
        self.assertEqual(routing.PROCESS_MODEL_MAP["FAMILY_X_FACTLOCK_REVISE"], "gpt-6.1-sol")
        self.assertEqual((pr["input_tokens"], pr["output_tokens"]), (2.0, 10.0))


if __name__ == "__main__":
    unittest.main()
