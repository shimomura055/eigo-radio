# ============================================================
# er008_n8_cost_jpy_reporting_25_test.py
# ER-008-N8-CLOSEOUT-GOVERNANCE-25 (4): 今後のcost報告を円ベースへ統一する
# ルール(1 USD = 160円)のSSOTがer005_stage7_cost_compute.pyへ正しく
# 追加されていることを確認するregression test。
# ============================================================
import unittest

import er005_stage7_cost_compute as cc


class UsdToJpyConversionTests(unittest.TestCase):
    def test_rate_is_160(self):
        self.assertEqual(cc.USD_TO_JPY, 160.0)

    def test_usd_to_jpy_basic_conversion(self):
        self.assertAlmostEqual(cc.usd_to_jpy(1.0), 160.0)
        self.assertAlmostEqual(cc.usd_to_jpy(0.005), 0.8)

    def test_usd_to_jpy_zero(self):
        self.assertEqual(cc.usd_to_jpy(0.0), 0.0)

    def test_rate_matches_existing_audio_cost_scripts(self):
        # er006_pool_pilot_01_cost_time_compute.py / compute_topic_cost.py が
        # 個別に使っていたレートと同一であることを固定する(表示の不整合防止)。
        import ast

        for path, var_name in [
            ("er006_pool_pilot_01_cost_time_compute.py", "USD_JPY"),
            ("compute_topic_cost.py", "USD_TO_JPY"),
        ]:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
            found = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == var_name:
                            found = ast.literal_eval(node.value)
            self.assertEqual(found, cc.USD_TO_JPY, f"{path}の{var_name}が{cc.USD_TO_JPY}と不一致")


if __name__ == "__main__":
    unittest.main()
