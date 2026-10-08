# ============================================================
# er006_model_routing_gpt6_wiring_test_01.py
# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase 2 (M2/M4/O1/O2) 回帰test
# ============================================================
# 全工程gpt-6-luna配線後の不変条件を固定する(API呼び出しなし)。
from __future__ import annotations

import json
import os
import tempfile
import unittest

import er002_topic_adapter as topic_adapter
import er003_v1_en_direct_vfl_01_generate as vfl01
import er006_model_routing_contract_01 as routing
import er006_research_coverage_gate_01 as gate
import er018_fiction_story_dna_e_axis_redesign_01 as e_axis
import er019_family_x_kp_explanation_01 as kp
import er026_family_z_fiction_production_runner_01 as fz

CONSTANTS = ["QUERY_PLANNER_MODEL", "TOPIC_SELECTOR_MODEL", "RESEARCH_MODEL", "WRITER_MODEL",
             "WRITER_FACT_CHECK_MODEL", "SUPPORT_MODEL", "SUPPORT_FACT_CHECK_MODEL"]


class RoutingConstantsTest(unittest.TestCase):
    def test_seven_constants_are_gpt6_luna(self):
        for n in CONSTANTS:
            self.assertEqual(getattr(routing, n), "gpt-6-luna", n)

    def test_process_map_openai_models_all_gpt6_luna(self):
        for k, v in routing.PROCESS_MODEL_MAP.items():
            if v.startswith("gpt-"):
                self.assertEqual(v, "gpt-6-luna", k)

    def test_old_model_rejected_without_override(self):
        with self.assertRaises(routing.ModelContractViolation):
            routing.require_model("B1_WRITER", "gpt-5.6-luna")
        self.assertEqual(routing.require_model_or_override(
            "B1_WRITER", "gpt-5.6-luna", override_reason="旧Trial再現"), "gpt-5.6-luna")


class HardcodeRemovalTest(unittest.TestCase):
    def test_kp_explanation_follows_support_model(self):
        self.assertEqual(kp.MODEL, routing.SUPPORT_MODEL)

    def test_deviation_default_follows_fact_check_model(self):
        import inspect
        self.assertEqual(vfl01.DEVIATION_MODEL, routing.WRITER_FACT_CHECK_MODEL)
        self.assertEqual(inspect.signature(vfl01.run_deviation_check).parameters["model"].default,
                         routing.WRITER_FACT_CHECK_MODEL)

    def test_deviation_rejects_unapproved_model_before_api(self):
        class Boom:
            def __getattr__(self, name):
                raise AssertionError("API clientに触れてはいけない(require_modelが先)")
        with self.assertRaises(routing.ModelContractViolation):
            vfl01.run_deviation_check(Boom(), "ledger", "article", model="gpt-5.6-luna")

    def test_topic_and_gate_follow_routing(self):
        self.assertEqual(topic_adapter.MODEL_SEARCH, routing.QUERY_PLANNER_MODEL)
        self.assertEqual(gate.GATE_MODEL, routing.RESEARCH_MODEL)


def _write_log(d, model, theme=None):
    p = os.path.join(d, "raw_usage_log.jsonl")
    rec = {"provider": "openai", "model_id": model, "success": True,
           "input_tokens": 1_000_000, "cached_input_tokens": 0, "output_tokens": 1_000_000}
    if theme:
        rec["theme"] = theme
    with open(p, "w", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return p


class FictionCostTest(unittest.TestCase):
    def test_e_axis_cost_default_is_routing_model(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write_log(d, routing.WRITER_MODEL)
            cost = e_axis.compute_cost_jpy(p)
            self.assertAlmostEqual(cost["total_usd"], 0.60, places=6)
            # 旧Trial再現(5.6明示)では6-luna recordは集計対象外
            old = e_axis.compute_cost_jpy(p, model="gpt-5.6-luna")
            self.assertEqual(old["total_usd"], 0.0)

    def test_fz_cost_nonzero_for_gpt6_luna_and_fail_closed_for_unknown(self):
        with tempfile.TemporaryDirectory() as d:
            p = _write_log(d, routing.WRITER_MODEL, theme=fz.THEME_TAG)
            cost = fz.compute_actual_cost_jpy(p)
            self.assertAlmostEqual(cost["total_usd"], 0.60, places=6)
            self.assertGreater(cost["total_jpy"], 0)
        with tempfile.TemporaryDirectory() as d:
            p = _write_log(d, "gpt-99-mystery", theme=fz.THEME_TAG)
            with self.assertRaises(routing.PricingNotFoundError):
                fz.compute_actual_cost_jpy(p)


if __name__ == "__main__":
    unittest.main()
