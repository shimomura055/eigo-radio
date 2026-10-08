# ============================================================
# er006_model_routing_pricing_coverage_test_01.py
# PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01 Phase 1 (Opus条件C M1)
# ============================================================
# 静的test: PROCESS_MODEL_MAPに現れる全OpenAI modelが
# pricing_snapshot.jsonにinput/cached_input/output単価を持つこと。
# および予算ガード/コスト関数が単価未登録で0円扱いにせず例外
# (PricingNotFoundError)を送出すること(fail-closed)。
from __future__ import annotations

import json
import unittest

import er006_model_routing_contract_01 as routing
import er012_e_family_entertainment_two_level_runner_01 as efam
import er003_v1_n3_01_advanced_adaptation_generate as adv_gen
import er003_v1_n3_01_standard_a2_generate as std_gen

SNAPSHOT = "er005_output/cost_baseline_01/pricing_snapshot.json"


def _openai_models():
    return sorted({m for m in routing.PROCESS_MODEL_MAP.values() if m.startswith("gpt-")})


class PricingCoverageTest(unittest.TestCase):
    def test_all_routed_openai_models_have_prices(self):
        with open(SNAPSHOT, encoding="utf-8") as f:
            prices = json.load(f)["prices"]
        models = _openai_models()
        self.assertTrue(models)
        for model in models:
            for meter in ("input_tokens", "cached_input_tokens", "output_tokens"):
                hits = [p for p in prices if p["provider"] == "openai" and p["model"] == model
                        and p["meter"] == meter and p.get("tier", "Standard") == "Standard"]
                self.assertEqual(len(hits), 1, f"{model}/{meter} 単価が登録されていない/重複")
                self.assertGreater(hits[0]["price"], 0)

    def test_every_routing_constant_model_has_prices(self):
        names = ["QUERY_PLANNER_MODEL", "TOPIC_SELECTOR_MODEL", "RESEARCH_MODEL", "WRITER_MODEL",
                 "WRITER_FACT_CHECK_MODEL", "SUPPORT_MODEL", "SUPPORT_FACT_CHECK_MODEL"]
        price = efam._load_pricing()
        for n in names:
            model = getattr(routing, n)
            for meter in ("input_tokens", "output_tokens"):
                self.assertGreater(price("openai", model, meter), 0, f"{n}={model}")

    def test_gpt6_luna_prices(self):
        price = efam._load_pricing()
        self.assertEqual(price("openai", "gpt-6-luna", "input_tokens"), 0.10)
        self.assertEqual(price("openai", "gpt-6-luna", "cached_input_tokens"), 0.01)
        self.assertEqual(price("openai", "gpt-6-luna", "output_tokens"), 0.50)
        self.assertEqual(price("openai", "gpt-6-luna", "cache_write_input_tokens"), 0.125)


class FailClosedTest(unittest.TestCase):
    def test_efam_price_unknown_model_raises(self):
        price = efam._load_pricing()
        with self.assertRaises(routing.PricingNotFoundError) as cm:
            price("openai", "gpt-99-mystery", "input_tokens")
        self.assertIn("gpt-99-mystery", str(cm.exception))

    def test_efam_cost_so_far_unknown_model_raises(self):
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "raw_usage_log.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"provider": "openai", "model_id": "gpt-99-mystery",
                                    "input_tokens": 10, "output_tokens": 10}) + "\n")
            with self.assertRaises(routing.PricingNotFoundError):
                efam.compute_cost_jpy_so_far(p)

    def test_gen_compute_cost_unknown_model_raises(self):
        for mod in (adv_gen, std_gen):
            price_fn = mod._load_pricing()
            with self.assertRaises(routing.PricingNotFoundError) as cm:
                mod._compute_cost_jpy(price_fn, "gpt-99-mystery", 100, 0, 100)
            self.assertIn("gpt-99-mystery", str(cm.exception))

    def test_known_model_cost_positive(self):
        for mod in (adv_gen, std_gen):
            price_fn = mod._load_pricing()
            usd, jpy = mod._compute_cost_jpy(price_fn, "gpt-6-luna", 1_000_000, 0, 1_000_000)
            self.assertAlmostEqual(usd, 0.60, places=6)
            self.assertGreater(jpy, 0)


if __name__ == "__main__":
    unittest.main()
