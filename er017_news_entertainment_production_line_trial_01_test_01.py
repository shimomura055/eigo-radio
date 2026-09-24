# ============================================================
# er017_news_entertainment_production_line_trial_01_test_01.py
# NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01 Phase B
# ============================================================
# 回帰テスト。run_project_regression.py(er0*_test_*.py自動探索)対象。
# API呼び出し(Web検索・LLM)は一切行わない(¥0)。er017本体・Production
# primitiveのimportのみで完結する静的検証。
from __future__ import annotations

import json
import os
import unittest

import er017_news_entertainment_production_line_trial_01 as mod


class NoStage3CodePathTest(unittest.TestCase):
    def test_allowed_stages_is_0_1_2_only(self):
        self.assertEqual(mod.ALLOWED_STAGES, (0, 1, 2))
        self.assertNotIn(3, mod.ALLOWED_STAGES)

    def test_stage_files_has_no_stage3_entry(self):
        self.assertNotIn(3, mod.STAGE_FILES)
        self.assertNotIn(3, mod.STAGE_LABELS)
        self.assertNotIn(3, mod.STAGE_USER_TEXT)

    def test_step_write_rejects_stage3(self):
        # step_write自体は冒頭でALLOWED_STAGES外のstageをValueErrorにする
        # (API呼び出し前に弾く)。out_dirはダミーで良い(到達しない)。
        with self.assertRaises(ValueError):
            mod.step_write("dummy_out_dir_never_created", [3])

    def test_stage_files_dict_has_exactly_three_entries_0_1_2(self):
        # STAGE_FILES/STAGE_LABELSがstage 0/1/2の3件のみで構成されている
        # こと(stage3の辞書エントリが追加されていないこと)を、リテラル
        # 文字列一致ではなく辞書の内容そのもので検証する(コメント中の
        # 他ファイル名[例: er011_news_stage3_new_theme_ledger_trial_09.py]
        # への言及と誤検知しないため)。
        self.assertEqual(set(mod.STAGE_FILES.keys()), {0, 1, 2})
        self.assertEqual(set(mod.STAGE_LABELS.keys()), {0, 1, 2})


class PromptDoesNotContainNewsEditorialInstructionTest(unittest.TestCase):
    FORBIDDEN_STRINGS = ["B1_B_DIRECT_INSTRUCTION", "COMMON_BLOCK_TEMPLATE"]

    def test_entertainment_prompt_lines_clean(self):
        combined = "\n".join(mod.ENTERTAINMENT_PROMPT_LINES)
        for s in self.FORBIDDEN_STRINGS:
            self.assertNotIn(s, combined)

    def test_contract_lines_clean(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        for s in self.FORBIDDEN_STRINGS:
            self.assertNotIn(s, combined)

    def test_rendered_stage0_template_clean(self):
        rendered = mod.STAGE0_USER_TEMPLATE.format(ledger_text="[DUMMY LEDGER TEXT FOR TEST]")
        for s in self.FORBIDDEN_STRINGS:
            self.assertNotIn(s, rendered)

    def test_revision_contract_line_clean(self):
        for s in self.FORBIDDEN_STRINGS:
            self.assertNotIn(s, mod.REVISION_CONTRACT_LINE)

    def test_developer_message_clean(self):
        for s in self.FORBIDDEN_STRINGS:
            self.assertNotIn(s, mod.DEVELOPER_MESSAGE)


class ContractMatchesPhaseAConfirmedContractTest(unittest.TestCase):
    """Phase A recon(NEWS-ENTERTAINMENT-PRODUCTION-LINE-TRIAL-01_REPORT.md
    §A「前提」節、L17-28)で確定したheading表記・Length Targetと一致するか。"""

    def test_length_soft_range_280_420_present(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        self.assertIn("280", combined)
        self.assertIn("420", combined)

    def test_title_heading_marker_present(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        self.assertIn('"# "', combined)

    def test_exactly_two_h3_subsections_required(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        self.assertIn('"### "', combined)
        self.assertIn("exactly two", combined)
        self.assertIn("30", combined)
        self.assertIn("60", combined)

    def test_in_one_line_exact_heading_string_required(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        self.assertIn('"## In one line"', combined)

    def test_point_one_two_labels_forbidden_by_contract(self):
        combined = "\n".join(mod.CONTRACT_LINES)
        self.assertIn("do not use labels like", combined)

    def test_revision_contract_line_preserves_same_structure(self):
        self.assertIn('"# "', mod.REVISION_CONTRACT_LINE)
        self.assertIn('"### "', mod.REVISION_CONTRACT_LINE)
        self.assertIn('"## In one line"', mod.REVISION_CONTRACT_LINE)
        self.assertIn("do not add or remove sections", mod.REVISION_CONTRACT_LINE)


class ProductionCodeSha256ConsistencyTest(unittest.TestCase):
    """production_code_sha256.json(実走時にer017本体が生成する、pre_*/post_*
    の各snapshotタグ)を読み、同一ファイルのhash値が全snapshotを通じて
    一貫しているか(=Production codeが実走中に一切変更されていないか)を
    検証する。実走前(snapshotファイル未生成)の場合はskipする(¥0、
    API呼び出しなし、既存artifactの読み取りのみ)。"""

    def test_hash_stable_across_all_recorded_snapshots(self):
        candidates = [
            "er017_output/news_entertainment_production_line_trial_01/production_code_sha256.json",
        ]
        path = next((p for p in candidates if os.path.exists(p)), None)
        if path is None:
            self.skipTest("production_code_sha256.jsonが未生成です(先にer017本体のstepを実行してください)")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertGreaterEqual(len(data), 2, "snapshotが2つ未満では前後比較になりません")
        per_file = {}
        for tag, filehashes in data.items():
            for fname, h in filehashes.items():
                per_file.setdefault(fname, set()).add(h)
        for fname, hashes in per_file.items():
            self.assertEqual(len(hashes), 1,
                              f"{fname} のsha256が実走中に変化しています(値={hashes})。"
                              "Production codeを変更していないか確認してください。")

    def test_all_production_files_listed_are_tracked(self):
        for f in mod.PRODUCTION_FILES:
            self.assertTrue(os.path.exists(f), f"Production file not found: {f}")


class ThemeIsolationTest(unittest.TestCase):
    def test_theme_id_is_trial_specific_not_production_theme_name(self):
        # 既存Production themeと衝突しない、Trial専用の名前であることの
        # 最低限の静的確認(完全な一意性はfilesystem上の分離で保証する)。
        self.assertIn("trial", mod.THEME_ID)
        self.assertNotEqual(mod.THEME_ID, "hanshin")
        self.assertNotEqual(mod.THEME_ID, "health")
        self.assertNotEqual(mod.THEME_ID, "household")


if __name__ == "__main__":
    unittest.main()
