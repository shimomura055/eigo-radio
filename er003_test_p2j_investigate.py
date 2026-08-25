# ============================================================
# er003_test_p2j_investigate.py
# ER-003-P2J: テスト件数差異の調査・回帰テスト証跡の正式化のテスト
# ============================================================
# 調査スクリプト(er003_v1_p2j_investigate.py)の決定的な集計ロジックが
# 正しいことを検証する。API呼び出しは一切行わない。
#
# 責務分離(ER-003-P2Lで明確化):
#   - HistoricalRecordIntegrityTestsは、保存済みP2J成果物(過去時点の
#     スナップショット)の内部整合性だけを検証する。現在のlive実測値
#     とは一切比較しない(historical countとcurrent countの大小比較は
#     行わない)。保存された過去の数値(P2H:1032、P2I:660、
#     P2J current_head:1117)はfrozen定数として厳密一致で検証し、
#     現在の値へ書き換えることも想定しない。
#   - 現在の回帰品質(現在HEADで実際にテストが通るか)は、
#     run_project_regression.py(canonical entry point)の実行結果
#     だけが証跡になる。本テストファイルはそれを代替しない。
#   詳細はTESTING.mdの「Historical test evidence」/
#   「Current project-wide regression」を参照。
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

    def test_er003_only_pattern_still_includes_all_p2i_era_files(self):
        """er003側は本テストファイル自身を含むため件数は増え続ける。
        件数のしきい値比較(ER-003-P2Lで廃止対象と判定)ではなく、P2I
        完了時点に存在した各fileが今も個別に存在するかを直接確認する。
        これなら「重要なfileを消して無関係なfileを足す」ケースを
        件数だけでは見逃さない。"""
        files_now = set(glob.glob("er003_test_*.py"))
        for module in inv_mod.P2I_ERA_ER003_MODULES:
            self.assertIn(f"{module}.py", files_now, msg=module)

    def test_combined_equals_sum_of_er002_and_er003(self):
        """ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(2026-08-25)で、er007_ja_
        tts_retry_path_fix_test_01.pyが初めてer007プレフィックスの実
        unittest.TestCaseを追加し、「combinedはer002+er003の合計と一致
        する」というP2J investigation当時(er002/er003以外にtestを持つ
        prefixが存在しなかった時点)の前提が崩れた。er00N prefixが今後も
        増え続けることを前提に、実際に存在するprefix集合から動的に合計
        する形へ一般化する(er002+er003の2項決め打ちをやめる)。"""
        import re
        files = glob.glob("er0*_test_*.py")
        prefixes = sorted({m.group(1) for m in (re.match(r"(er0\d\d)_", f) for f in files) if m})
        sum_by_prefix = sum(inv_mod.collect_count(f"{p}_test_*.py") for p in prefixes)
        combined = inv_mod.collect_count("er0*_test_*.py")
        self.assertEqual(combined, sum_by_prefix)

    def test_combined_pattern_does_not_match_non_er00_test_files(self):
        """test_api.py/generate_test.py/tts_test.py等は対象外であることの確認。"""
        matched = set(glob.glob("er0*_test_*.py"))
        self.assertNotIn("test_api.py", matched)
        self.assertNotIn("generate_test.py", matched)
        self.assertNotIn("tts_test.py", matched)
        self.assertNotIn("tts_style_test.py", matched)


class PerFileCountsTests(unittest.TestCase):

    def test_per_file_counts_sum_matches_pattern_discovery(self):
        """test_combined_equals_sum_of_er002_and_er003と同じ理由
        (ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01)で、対象patternをer002/er003
        決め打ちから、実際に存在する全er0*_test_*.pyファイルへ一般化する。"""
        counts = inv_mod.per_file_counts(["er0*_test_*.py"])
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


class HistoricalRecordIntegrityTests(unittest.TestCase):
    """ER-003-P2L: P2J成果物(過去時点のスナップショット)の内部整合性
    だけを検証する。現在のlive実測値とは一切比較しない。

    保証すること: 必須セクション/フィールドの存在、値の型、commit hash
    形式、command/scopeの非空性、classification/verdictのenum妥当性、
    そして「保存された過去の数値が書き換えられていないこと」
    (immutability、frozen定数との厳密一致)。

    保証しないこと: 現在のtest件数が過去以上/以下/一致であること。
    現在の回帰品質はrun_project_regression.py(canonical entry)だけが
    証跡になる(TESTING.mdの「Historical test evidence」/
    「Current project-wide regression」の区別を参照)。"""

    @classmethod
    def setUpClass(cls):
        cls.inventory = inv_mod.load_saved_inventory()
        cls.current_run = inv_mod.load_saved_current_run()

    # --- 必須セクション/フィールドの存在 ---

    def test_inventory_has_required_top_level_sections(self):
        for key in ("p2h", "p2i", "current_head", "classification", "p2i_final_test_verdict", "detail"):
            self.assertIn(key, self.inventory, msg=key)

    def test_p2h_and_p2i_sections_are_not_confused(self):
        """p2hセクションにp2i固有の情報が、p2iセクションにp2h固有の情報が
        紛れ込んでいないことを、それぞれのcommit/scope文字列の内容から
        確認する。"""
        self.assertIn("70d8b0b", self.inventory["p2h"]["commit"])
        self.assertIn("eca3198", self.inventory["p2i"]["commit"])
        self.assertNotEqual(self.inventory["p2h"]["scope"], self.inventory["p2i"]["scope"])

    def test_current_run_has_required_fields(self):
        for key in ("commit", "canonical_collection_command", "canonical_test_command",
                   "collected", "passed", "failed", "skipped", "deselected",
                   "p2i_targeted_command", "p2i_targeted_collected", "p2i_targeted_passed"):
            self.assertIn(key, self.current_run, msg=key)

    # --- 構造/型/enum検証(validate_saved_inventory_schema) ---

    def test_saved_inventory_passes_schema_validation(self):
        result = inv_mod.validate_saved_inventory_schema(self.inventory)
        self.assertTrue(result["ok"], msg=result["reasons"])

    def test_schema_validation_rejects_missing_section(self):
        broken = {k: v for k, v in self.inventory.items() if k != "current_head"}
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])
        self.assertTrue(any("current_head" in r for r in result["reasons"]))

    def test_schema_validation_rejects_missing_field(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        del broken["p2h"]["collected"]
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])
        self.assertTrue(any("p2h.collected" in r for r in result["reasons"]))

    def test_schema_validation_rejects_negative_count(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["current_head"]["failed"] = -1
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])
        self.assertTrue(any("current_head.failed" in r for r in result["reasons"]))

    def test_schema_validation_rejects_non_int_count(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["p2i"]["collected"] = "660"
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])

    def test_schema_validation_rejects_malformed_commit_hash(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["p2h"]["commit"] = "not-a-hash!"
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])
        self.assertTrue(any("p2h.commit" in r for r in result["reasons"]))

    def test_schema_validation_rejects_empty_command(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["p2i"]["command"] = ""
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])

    def test_schema_validation_rejects_empty_scope(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["p2h"]["scope"] = "   "
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])

    def test_schema_validation_rejects_unknown_classification(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["classification"] = ["NOT_A_REAL_CLASSIFICATION"]
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])

    def test_schema_validation_rejects_unknown_verdict(self):
        import copy
        broken = copy.deepcopy(self.inventory)
        broken["p2i_final_test_verdict"] = "MAYBE"
        result = inv_mod.validate_saved_inventory_schema(broken)
        self.assertFalse(result["ok"])

    def test_schema_validation_raises_on_malformed_json_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{not valid json")
            path = f.name
        try:
            with self.assertRaises(json.JSONDecodeError):
                inv_mod.load_saved_inventory(path)
        finally:
            import os
            os.remove(path)

    # --- 分類・判定の妥当性(enumメンバーシップのみ、値の再計算はしない) ---

    def test_classification_is_within_enum(self):
        for c in self.inventory["classification"]:
            self.assertIn(c, inv_mod.CLASSIFICATION_ENUM)

    def test_classification_includes_different_test_scope(self):
        self.assertIn("DIFFERENT_TEST_SCOPE", self.inventory["classification"])

    def test_verdict_is_within_enum(self):
        self.assertIn(self.inventory["p2i_final_test_verdict"], inv_mod.VERDICT_ENUM)

    def test_verdict_is_pass(self):
        self.assertEqual(self.inventory["p2i_final_test_verdict"], "PASS")

    # --- immutability: 保存された過去の数値は凍結定数と厳密一致する
    #     (現在のlive件数とは一切比較しない) ---

    def test_p2h_collected_matches_frozen_historical_value(self):
        self.assertEqual(self.inventory["p2h"]["collected"], inv_mod.P2H_REPORTED_COUNT)

    def test_p2i_collected_matches_frozen_historical_value(self):
        self.assertEqual(self.inventory["p2i"]["collected"], inv_mod.P2I_REPORTED_COUNT)

    def test_current_head_collected_matches_frozen_p2j_snapshot(self):
        """current_headはP2J完了時点(commit eca3198直後)のスナップ
        ショットとして保存されたものであり、以後のステージ(P2K等)が
        テストを追加しても、この保存値自体は書き換えない。"""
        self.assertEqual(self.inventory["current_head"]["collected"], inv_mod.P2J_CURRENT_HEAD_REPORTED_COUNT)

    def test_current_run_collected_matches_frozen_p2j_snapshot(self):
        self.assertEqual(self.current_run["collected"], inv_mod.P2J_CURRENT_HEAD_REPORTED_COUNT)

    def test_p2i_targeted_collected_matches_frozen_value(self):
        """er003_test_p2i_production.py自体はP2I完了以降変更されて
        いないため、その項目数(66)は不変のはずである。"""
        self.assertEqual(self.current_run["p2i_targeted_collected"], 66)

    def test_saved_current_run_shows_zero_failures(self):
        self.assertEqual(self.current_run["failed"], 0)
        self.assertEqual(self.current_run["skipped"], 0)

    # --- 責務分離そのものの検証: このクラスはlive件数を一切参照しない ---

    def test_this_test_class_never_calls_build_inventory_or_collect_count(self):
        """履歴監査テストが、現在のlive件数を再計算する関数
        (build_inventory/collect_count/build_current_run_record)を
        一切呼んでいないことを、このクラス自身のソースコードから確認
        する(責務分離の構造的な保証)。このアサーション自身のメソッドは
        除外して調べる(禁止関数名を文字列として列挙しているため)。"""
        import inspect
        forbidden_calls = ("build_inventory(", "collect_count(", "build_current_run_record(")
        for name, method in inspect.getmembers(HistoricalRecordIntegrityTests, predicate=inspect.isfunction):
            if name == "test_this_test_class_never_calls_build_inventory_or_collect_count":
                continue
            method_source = inspect.getsource(method)
            for forbidden in forbidden_calls:
                self.assertNotIn(forbidden, method_source, msg=f"{name}: {forbidden}")


if __name__ == "__main__":
    unittest.main()
