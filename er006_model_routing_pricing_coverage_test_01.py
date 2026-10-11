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


    def test_gpt6_astra_prices_registered_standard_only(self):
        """FACTLOCK-ASTRA-E2E-TRIAL-01 委任_05(a): gpt-6-astra Standard単価(出典=pricing page 2026-10-08)。
        登録=採用ではない(routingのPROCESS_MODEL_MAPには割り当てない)。Batch/Flex単価は登録しない。"""
        price = efam._load_pricing()
        self.assertEqual(price("openai", "gpt-6-astra", "input_tokens"), 10.00)
        self.assertEqual(price("openai", "gpt-6-astra", "cached_input_tokens"), 1.00)
        self.assertEqual(price("openai", "gpt-6-astra", "output_tokens"), 50.00)
        self.assertEqual(price("openai", "gpt-6-astra", "cache_write_input_tokens"), 12.50)
        with open(SNAPSHOT, encoding="utf-8") as f:
            prices = json.load(f)["prices"]
        astra = [p for p in prices if p["model"] == "gpt-6-astra"]
        self.assertEqual({p["tier"] for p in astra}, {"Standard"})
        for p in astra:
            self.assertIn("161df7d8126a8287e0c0c4bc80950f977ab6b54a597d9bced35baeedbbb3a807", p["source_url"])
            self.assertIn("2026-10-08T16:38", p["source_url"])
            self.assertIn("platform.openai.com/docs/pricing", p["source_url"])
        # RISK-FLAGGER-PRODUCTION-WIRING-01 ユーザー決定2026-10-10: astraは FAMILY_X_FACTLOCK_REVISE のみに登録
        # SOL61 E案(2026-10-11): R1/R2はgpt-6.1-solへ移行。astraはroutingのどのキーにも割り当てない(単価登録は維持)。
        astra_keys = {k for k, v in routing.PROCESS_MODEL_MAP.items() if v == "gpt-6-astra"}
        self.assertEqual(astra_keys, set())

    def test_astra_pricing_not_found_error_resolved(self):
        """登録前は PricingNotFoundError だった astra の費用計算が、登録後は例外にならず正しい額になる。"""
        import os
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "raw_usage_log.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"provider": "openai", "model_id": "gpt-6-astra",
                                    "input_tokens": 1_000_000, "output_tokens": 1_000_000}) + "\n")
            jpy, _ = efam.compute_cost_jpy_so_far(p)
        self.assertAlmostEqual(jpy, (10.0 + 50.0) * efam.USD_JPY, places=4)
        for mod in (adv_gen, std_gen):
            usd, _jpy = mod._compute_cost_jpy(mod._load_pricing(), "gpt-6-astra", 1_000_000, 0, 1_000_000)
            self.assertAlmostEqual(usd, 60.0, places=6)



    def test_flagger_design_models_registered(self):
        """WRITER-DEV-RISK-FLAGGER-DESIGN-01 委任_01B: gpt-6.1-sol / deepseek-v4-pro 追加、gpt-5.6-sol を公式現行値へ更新(2026-10-09取得)。"""
        price = efam._load_pricing()
        self.assertEqual(price("openai", "gpt-6.1-sol", "input_tokens"), 2.00)
        self.assertEqual(price("openai", "gpt-6.1-sol", "cached_input_tokens"), 0.10)
        self.assertEqual(price("openai", "gpt-6.1-sol", "output_tokens"), 10.00)
        self.assertEqual(price("openai", "gpt-6.1-sol", "cache_write_input_tokens"), 2.50)
        self.assertEqual(price("openai", "gpt-5.6-sol", "input_tokens"), 4.00)
        self.assertEqual(price("openai", "gpt-5.6-sol", "cached_input_tokens"), 0.40)
        self.assertEqual(price("openai", "gpt-5.6-sol", "output_tokens"), 20.00)
        with open(SNAPSHOT, encoding="utf-8") as f:
            prices = json.load(f)["prices"]
        old = {p["meter"]: p["price_history"][0]["price"] for p in prices
               if p["model"] == "gpt-5.6-sol" and "price_history" in p}
        self.assertEqual(old, {"input_tokens": 5.0, "cached_input_tokens": 0.5, "output_tokens": 30.0})
        pro = {p["meter"]: p["price"] for p in prices if p["model"] == "deepseek-v4-pro" and p["tier"] == "Standard"}
        self.assertEqual(pro, {"cached_input_tokens": 0.044, "input_tokens": 1.32, "output_tokens": 3.96})
        off = {p["meter"]: p["price"] for p in prices if p["model"] == "deepseek-v4-pro" and p["tier"] != "Standard"}
        self.assertEqual(off, {"cached_input_tokens": 0.022, "input_tokens": 0.66, "output_tokens": 1.98})
        # SOL61 E案: gpt-6.1-solはFamily X日本語記事のB3/R0/R1/R2の3キーだけに割当(他キーへの混入禁止)
        sol_keys = {k for k, v in routing.PROCESS_MODEL_MAP.items() if v == "gpt-6.1-sol"}
        self.assertEqual(sol_keys, {"FAMILY_X_STORYLINE_B3", "FAMILY_X_FACTLOCK_R0", "FAMILY_X_FACTLOCK_REVISE"})
        self.assertNotIn("deepseek-v4-pro", set(routing.PROCESS_MODEL_MAP.values()))

    def test_deepseek_flash_prices_registered(self):
        """WRITER-EVAL-DUAL-LLM-METHOD-TRIAL-01 委任_04: DeepSeek公式単価(Standard=Peak、2026-10-09取得)。
        Off-peak割引は別tierで記録のみ。routingのPROCESS_MODEL_MAPには割り当てない。"""
        with open(SNAPSHOT, encoding="utf-8") as f:
            prices = json.load(f)["prices"]
        ds = [p for p in prices if p["provider"] == "deepseek" and p["model"] == "deepseek-v4-flash"]
        std = {p["meter"]: p["price"] for p in ds if p["tier"] == "Standard"}
        self.assertEqual(std, {"cached_input_tokens": 0.006, "input_tokens": 0.3, "output_tokens": 1.2})
        off = {p["meter"]: p["price"] for p in ds if p["tier"] != "Standard"}
        self.assertEqual(off, {"cached_input_tokens": 0.003, "input_tokens": 0.15, "output_tokens": 0.6})
        for p in ds:
            self.assertIn("api-docs.deepseek.com", p["source_url"])
        self.assertNotIn("deepseek-v4-flash", set(routing.PROCESS_MODEL_MAP.values()))


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
