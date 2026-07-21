# ============================================================
# er003_test_p2j_investigate.py
# ER-003-P2J: テスト件数差異の調査・回帰テスト証跡の正式化のテスト
# ============================================================
# 調査スクリプト(er003_v1_p2j_investigate.py)の決定的な集計ロジックが
# 正しいこと、および保存済み成果物(inventory/current_test_run)が現在の
# 実測値と一致することを検証する。API呼び出しは一切行わない。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_p2j_investigate -v

import glob
import json
import unittest

import er003_v1_p2j_investigate as inv_mod


class ModuleListTests(unittest.TestCase):

    def test_p2h_command_modules_has_21_entries(self):
        self.assertEqual(len(inv_mod.P2H_COMMAND_MODULES), 21)

    def test_p2h_command_modules_are_10_er002_plus_11_er003(self):
        er002 = [m for m in inv_mod.P2H_COMMAND_MODULES if m.startswith("er002_test_")]
        er003 = [m for m in inv_mod.P2H_COMMAND_MODULES if m.startswith("er003_test_")]
        self.assertEqual(len(er002), 10)
        self.assertEqual(len(er003), 11)

    def test_p2h_command_modules_exclude_p2i_production(self):
        self.assertNotIn("er003_test_p2i_production", inv_mod.P2H_COMMAND_MODULES)

    def test_p2h_command_modules_all_exist_as_files_now(self):
        for mod in inv_mod.P2H_COMMAND_MODULES:
            self.assertTrue(glob.glob(f"{mod}.py"), msg=mod)


class CollectionCountTests(unittest.TestCase):
    """unittest.TestLoaderによる収集件数(collected)が、実行結果の
    passed件数と一致することを保証する(collectとexecuteの取り違えを
    防ぐ)。"""

    def test_er002_only_pattern_collects_438(self):
        """er002側はP2H以降ファイル数が変化していない固定値として検証する。"""
        self.assertEqual(inv_mod.collect_count("er002_test_*.py"), 438)

    def test_er003_only_pattern_at_least_p2i_era_count(self):
        """er003側は本テストファイル自身を含むため増え続ける。P2I時点の
        660件を下回らないことのみを固定的に検証する(自己参照による
        数値の陳腐化を避ける)。"""
        self.assertGreaterEqual(inv_mod.collect_count("er003_test_*.py"), inv_mod.P2I_REPORTED_COUNT)

    def test_combined_equals_sum_of_er002_and_er003(self):
        er002 = inv_mod.collect_count("er002_test_*.py")
        er003 = inv_mod.collect_count("er003_test_*.py")
        combined = inv_mod.collect_count("er0*_test_*.py")
        self.assertEqual(combined, er002 + er003)

    def test_combined_pattern_does_not_match_non_er00_test_files(self):
        """test_api.py/generate_test.py/tts_test.py等は対象外であることの確認。"""
        matched = set(glob.glob("er0*_test_*.py"))
        self.assertNotIn("test_api.py", matched)
        self.assertNotIn("generate_test.py", matched)
        self.assertNotIn("tts_test.py", matched)
        self.assertNotIn("tts_style_test.py", matched)


class PerFileCountsTests(unittest.TestCase):

    def test_per_file_counts_sum_matches_pattern_discovery(self):
        counts = inv_mod.per_file_counts(["er002_test_*.py", "er003_test_*.py"])
        self.assertEqual(sum(counts.values()), inv_mod.collect_count("er0*_test_*.py"))

    def test_p2i_production_present_in_er003_counts(self):
        counts = inv_mod.per_file_counts(["er003_test_*.py"])
        self.assertIn("er003_test_p2i_production", counts)
        self.assertEqual(counts["er003_test_p2i_production"], 66)


class ReconciliationArithmeticTests(unittest.TestCase):
    """P2H(1032)とP2I(660)の差異が、er002スコープの欠落とP2Iの新規テスト
    増分だけで完全に説明できることを検証する(推測ではなく実測値のみで
    構成する)。"""

    @classmethod
    def setUpClass(cls):
        cls.inventory = inv_mod.build_inventory()

    def test_p2h_reported_count_matches_er002_plus_er003_at_that_time(self):
        detail = self.inventory["detail"]
        self.assertEqual(detail["er002_total_now"] + detail["er003_total_at_p2h_era"],
                         inv_mod.P2H_REPORTED_COUNT)

    def test_p2i_reported_count_matches_er003_at_p2i_era(self):
        """P2Iが報告した660は、P2I完了時点(commit eca3198)に存在した
        12ファイルの合計であり、その後P2J自身が追加するファイルを
        含めても値が変わらないことを確認する(過去時点のスコープは
        固定リストで再現しているため)。"""
        detail = self.inventory["detail"]
        self.assertEqual(detail["er003_total_at_p2i_era"], inv_mod.P2I_REPORTED_COUNT)

    def test_delta_fully_explained_by_scope_and_new_tests(self):
        arithmetic = self.inventory["detail"]["reconciliation_arithmetic"]
        self.assertTrue(arithmetic["net_check"])
        delta = arithmetic["delta_explained_by_missing_er002_scope"] + arithmetic["delta_explained_by_new_p2i_tests"]
        self.assertEqual(delta, arithmetic["delta_660_minus_1032"])

    def test_classification_is_different_test_scope(self):
        self.assertIn("DIFFERENT_TEST_SCOPE", self.inventory["classification"])

    def test_verdict_is_pass(self):
        self.assertEqual(self.inventory["p2i_final_test_verdict"], "PASS")

    def test_no_tests_missing_or_uncollected(self):
        """TESTS_MISSING_OR_NOT_COLLECTEDに該当しないことの確認
        (collected件数がpassed件数と一致し、failed/skippedが0)。"""
        current = self.inventory["current_head"]
        self.assertEqual(current["collected"], current["passed"])
        self.assertEqual(current["failed"], 0)
        self.assertEqual(current["skipped"], 0)


class SavedArtifactConsistencyTests(unittest.TestCase):
    """保存済みJSON成果物が、現在の実測値と一致することを検証する
    (ドリフト検出)。"""

    def test_inventory_json_matches_freshly_built_inventory(self):
        fresh = inv_mod.build_inventory()
        with open("er003_output/p2j/ER-003-P2J_test_inventory.json", encoding="utf-8") as f:
            saved = json.load(f)
        # evidenceのcommit hash等、実行のたびに変わり得ない項目のみ比較する
        self.assertEqual(fresh["p2h"]["collected"], saved["p2h"]["collected"])
        self.assertEqual(fresh["p2i"]["collected"], saved["p2i"]["collected"])
        self.assertEqual(fresh["current_head"]["collected"], saved["current_head"]["collected"])
        self.assertEqual(fresh["classification"], saved["classification"])
        self.assertEqual(fresh["p2i_final_test_verdict"], saved["p2i_final_test_verdict"])

    def test_current_run_json_matches_fresh_build(self):
        fresh_inv = inv_mod.build_inventory()
        fresh_run = inv_mod.build_current_run_record(fresh_inv)
        with open("er003_output/p2j/ER-003-P2J_current_test_run.json", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(fresh_run["collected"], saved["collected"])
        self.assertEqual(fresh_run["passed"], saved["passed"])
        self.assertEqual(fresh_run["p2i_targeted_collected"], saved["p2i_targeted_collected"])

    def test_saved_current_run_shows_zero_failures(self):
        with open("er003_output/p2j/ER-003-P2J_current_test_run.json", encoding="utf-8") as f:
            saved = json.load(f)
        self.assertEqual(saved["failed"], 0)
        self.assertEqual(saved["skipped"], 0)


if __name__ == "__main__":
    unittest.main()
