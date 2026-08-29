# ============================================================
# er008_n8_cost_compute_pricing_fix_24_test_01.py
# ER-008-N8-FINAL-CLOSEOUT-24 Item 4 (cost正確性):
# er005_stage7_cost_compute.record_cost()が、record自身のmodel_idに
# 応じた単価(sol/luna等)で価格計算することを検証する(無料、API呼び出し
# 無し)。ER-24で発見したバグ: 修正前はopenai providerの全record
# (model_idに関わらず)を常にgpt-5.6-sol単価で計算していたため、実際には
# gpt-5.6-luna(sol比で入力1/25・出力1/25の単価)を使うWriter/Fact
# Checker/Deviation Check呼び出しのcostがおよそ25倍過大に計算されていた
# (No.8のwriter_a2実測で$1.6461[誤]->$0.2098[修正後]など)。
# ============================================================
import unittest

import er005_stage7_cost_compute as cc


class TestCostComputePricingFix24(unittest.TestCase):
    def test_luna_model_uses_luna_pricing_not_sol(self):
        record = {
            "provider": "openai", "success": True, "model_id": "gpt-5.6-luna",
            "input_tokens": 1_000_000, "output_tokens": 1_000_000, "cached_input_tokens": 0,
            "web_search_call_count": 0,
        }
        gen_cost, search_cost = cc.record_cost(record)
        # luna: $0.2/M入力 + $1.2/M出力 = $1.40(sol単価$5+$30=$35なら
        # 明らかな誤り)
        self.assertAlmostEqual(gen_cost, 0.2 + 1.2, places=6)
        self.assertEqual(search_cost, 0.0)

    def test_sol_model_pricing_unchanged_for_backward_compatibility(self):
        record = {
            "provider": "openai", "success": True, "model_id": "gpt-5.6-sol",
            "input_tokens": 1_000_000, "output_tokens": 1_000_000, "cached_input_tokens": 0,
            "web_search_call_count": 0,
        }
        gen_cost, search_cost = cc.record_cost(record)
        self.assertAlmostEqual(gen_cost, 5.0 + 30.0, places=6)

    def test_missing_model_id_falls_back_to_sol_for_legacy_records(self):
        # ER-005当時のrecordにはmodel_idが無いものがあるため、後方互換として
        # sol単価にfallbackすることを確認する。
        record = {
            "provider": "openai", "success": True,
            "input_tokens": 1_000_000, "output_tokens": 1_000_000, "cached_input_tokens": 0,
            "web_search_call_count": 0,
        }
        gen_cost, _ = cc.record_cost(record)
        self.assertAlmostEqual(gen_cost, 5.0 + 30.0, places=6)

    def test_web_search_tool_fee_is_model_independent(self):
        luna_record = {
            "provider": "openai", "success": True, "model_id": "gpt-5.6-luna",
            "input_tokens": 0, "output_tokens": 0, "cached_input_tokens": 0,
            "web_search_call_count": 8,
        }
        _, search_cost = cc.record_cost(luna_record)
        self.assertAlmostEqual(search_cost, 8 / 1000 * 10.0, places=6)


if __name__ == "__main__":
    unittest.main()
