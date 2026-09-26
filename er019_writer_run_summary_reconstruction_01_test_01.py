# ============================================================
# er019_writer_run_summary_reconstruction_01_test_01.py
# NEWS-FAMILY-X-B3-FACT-SELECTION-PRODUCTION-WIRING-01(Fable差し戻し1回目、
# Gate 3 #13対応)
# ============================================================
# er019_writer_run_summary_reconstruction_01.pyの単体テスト。実API呼び出しは
# 一切行わない(合成raw_usage_log.jsonl + 合成監査ファイルのみを使う)。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er019_writer_run_summary_reconstruction_01_test_01 -v
# ============================================================
from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest

import er019_writer_run_summary_reconstruction_01 as recon


def _write_jsonl(path: str, records: list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _entry(stage: str, attempt_number: int, response_id: str, **extra) -> dict:
    base = {
        "provider": "openai", "api": "responses.create", "stage": stage,
        "model_id": "gpt-5.6-luna", "response_id": response_id,
        "attempt_number": attempt_number, "success": True,
        "elapsed_seconds": 10.0, "input_tokens": 1000, "output_tokens": 500,
        "cached_input_tokens": 0, "reasoning_tokens": 100,
    }
    base.update(extra)
    return base


class SelectInvocationGroupsTests(unittest.TestCase):
    def test_single_invocation_no_retry_groups_as_one_pair(self):
        entries = [
            _entry("advanced", 1, "resp_gen1"),
            _entry("advanced", 2, "resp_dev1"),
        ]
        groups = recon.select_invocation_groups(entries, "advanced")
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]), 2)

    def test_two_separate_process_invocations_split_on_attempt_number_reset(self):
        entries = [
            _entry("advanced", 1, "resp_gen1"),
            _entry("advanced", 2, "resp_dev1"),
            _entry("advanced", 1, "resp_gen2_rej"),
            _entry("advanced", 2, "resp_dev2_rej"),
            _entry("advanced", 3, "resp_gen2_final"),
            _entry("advanced", 4, "resp_dev2_final"),
        ]
        groups = recon.select_invocation_groups(entries, "advanced")
        self.assertEqual(len(groups), 2)
        self.assertEqual(len(groups[0]), 2)
        self.assertEqual(len(groups[1]), 4)

    def test_ignores_other_stage_tags(self):
        entries = [
            _entry("advanced", 1, "resp_a1"),
            _entry("advanced", 2, "resp_a2"),
            _entry("standard", 1, "resp_s1"),
            _entry("standard", 2, "resp_s2"),
        ]
        adv_groups = recon.select_invocation_groups(entries, "advanced")
        std_groups = recon.select_invocation_groups(entries, "standard")
        self.assertEqual(len(adv_groups), 1)
        self.assertEqual(len(std_groups), 1)


class ReconstructWriterRunSummaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.out_dir = os.path.join(self.tmp_dir, "run_01")
        os.makedirs(os.path.join(self.out_dir, "b1b", "audit"), exist_ok=True)
        os.makedirs(os.path.join(self.out_dir, "a2", "audit"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_common_fixtures(self, advanced_text="# Title\n\nBody.", standard_text="# Title\n\nSimple body."):
        with open(os.path.join(self.out_dir, "b1b", "article.md"), "w", encoding="utf-8") as f:
            f.write(advanced_text)
        with open(os.path.join(self.out_dir, "b1b", "audit", "deviation_check.json"), "w", encoding="utf-8") as f:
            json.dump({"deviations": [], "overall_status": "LEDGER_COMPLIANT"}, f)
        with open(os.path.join(self.out_dir, "a2", "article.md"), "w", encoding="utf-8") as f:
            f.write(standard_text)
        with open(os.path.join(self.out_dir, "a2", "audit", "deviation_check.json"), "w", encoding="utf-8") as f:
            json.dump({"deviations": [], "overall_status": "LEDGER_COMPLIANT"}, f)

    def test_reconstructs_both_stages_when_no_retry_occurred(self):
        self._write_common_fixtures()
        entries = [
            _entry("advanced", 1, "resp_adv_gen"),
            _entry("advanced", 2, "resp_adv_dev"),
            _entry("standard", 1, "resp_std_gen"),
            _entry("standard", 2, "resp_std_dev"),
        ]
        _write_jsonl(os.path.join(self.out_dir, "raw_usage_log.jsonl"), entries)

        result = recon.reconstruct_writer_run_summary(self.out_dir)

        self.assertIn("advanced", result)
        self.assertIn("standard", result)
        self.assertEqual(result["advanced"]["response_id"], "resp_adv_gen")
        self.assertFalse(result["advanced"]["retried_for_deviation"])
        self.assertEqual(result["standard"]["response_id"], "resp_std_gen")
        self.assertFalse(result["standard"]["retried_for_deviation"])
        self.assertEqual(result["advanced"]["deviation_overall_status"], "LEDGER_COMPLIANT")
        self.assertIn("checks", result["standard"])
        self.assertIn("_reconstruction_provenance", result)

    def test_reconstructs_final_accepted_call_when_deviation_retry_occurred(self):
        """Gate 3 #13の核心ケース: run_writer_stage()がMAJORで1回retryした
        (advancedが4 call: generate_rej -> deviation_rej -> generate_final ->
        deviation_final)場合、response_idは最終accepted(3番目)を使うこと。"""
        self._write_common_fixtures()
        entries = [
            _entry("advanced", 1, "resp_adv_gen_rejected"),
            _entry("advanced", 2, "resp_adv_dev_rejected"),
            _entry("advanced", 3, "resp_adv_gen_final"),
            _entry("advanced", 4, "resp_adv_dev_final"),
            _entry("standard", 1, "resp_std_gen"),
            _entry("standard", 2, "resp_std_dev"),
        ]
        _write_jsonl(os.path.join(self.out_dir, "raw_usage_log.jsonl"), entries)

        result = recon.reconstruct_writer_run_summary(self.out_dir)

        self.assertEqual(result["advanced"]["response_id"], "resp_adv_gen_final")
        self.assertTrue(result["advanced"]["retried_for_deviation"])
        self.assertNotEqual(result["advanced"]["response_id"], "resp_adv_gen_rejected")

    def test_takes_last_invocation_group_when_process_restarted_for_regenerate_stage(self):
        """--regenerate-stage advancedのように、別プロセスでadvancedだけ再実行
        された場合(attempt_numberがプロセス起動ごとに1へ戻る)、ディスク上の
        現物(article.md)と一致する最後のinvocationのresponse_idを使うこと。"""
        self._write_common_fixtures()
        entries = [
            # 1回目のプロセス実行(旧いadvanced、後で上書きされ現物ではない)
            _entry("advanced", 1, "resp_adv_gen_old"),
            _entry("advanced", 2, "resp_adv_dev_old"),
            # standardが後で失敗しSTOP(このentryは無視されて構わない)
            _entry("standard", 1, "resp_std_gen_failed_run"),
            _entry("standard", 2, "resp_std_dev_failed_major"),
            # 2回目のプロセス実行(--regenerate-stage advanced、現物と一致)
            _entry("advanced", 1, "resp_adv_gen_new"),
            _entry("advanced", 2, "resp_adv_dev_new"),
            # 3回目のプロセス実行(--regenerate-stage standard、現物と一致)
            _entry("standard", 1, "resp_std_gen_new"),
            _entry("standard", 2, "resp_std_dev_new"),
        ]
        _write_jsonl(os.path.join(self.out_dir, "raw_usage_log.jsonl"), entries)

        result = recon.reconstruct_writer_run_summary(self.out_dir)

        self.assertEqual(result["advanced"]["response_id"], "resp_adv_gen_new")
        self.assertEqual(result["standard"]["response_id"], "resp_std_gen_new")

    def test_ambiguous_entry_count_is_flagged_not_guessed(self):
        """generate/deviationの不変条件(2 or 4 call)が崩れる異常系
        (例: 3件)では、値を推測せずambiguous_stagesへ記録し、当該stageの
        キー自体は追加しないこと。"""
        self._write_common_fixtures()
        entries = [
            _entry("advanced", 1, "resp_a"),
            _entry("advanced", 2, "resp_b"),
            _entry("advanced", 3, "resp_c"),
            _entry("standard", 1, "resp_std_gen"),
            _entry("standard", 2, "resp_std_dev"),
        ]
        _write_jsonl(os.path.join(self.out_dir, "raw_usage_log.jsonl"), entries)

        result = recon.reconstruct_writer_run_summary(self.out_dir)

        self.assertNotIn("advanced", result)
        self.assertIn("advanced", result["_reconstruction_provenance"]["ambiguous_stages"])
        self.assertIn("standard", result)

    def test_save_reconstructed_summary_preserves_old_buggy_file_as_backup(self):
        """Gate 3 #13の核心要求: 旧(バグで壊れた)writer_run_summary.jsonを
        削除せず、backup_suffix付きファイルとして退避してから新しい内容で
        置き換えること。"""
        self._write_common_fixtures()
        entries = [
            _entry("advanced", 1, "resp_adv_gen"),
            _entry("advanced", 2, "resp_adv_dev"),
            _entry("standard", 1, "resp_std_gen"),
            _entry("standard", 2, "resp_std_dev"),
        ]
        _write_jsonl(os.path.join(self.out_dir, "raw_usage_log.jsonl"), entries)

        buggy_old_content = {"standard": {"response_id": "resp_std_gen"}}
        summary_path = os.path.join(self.out_dir, "writer_run_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(buggy_old_content, f)

        recon.save_reconstructed_summary(self.out_dir)

        backup_path = os.path.join(self.out_dir, "writer_run_summary_pre_gate3_fix_buggy_overwrite.json")
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, encoding="utf-8") as f:
            self.assertEqual(json.load(f), buggy_old_content)

        with open(summary_path, encoding="utf-8") as f:
            new_content = json.load(f)
        self.assertIn("advanced", new_content)
        self.assertIn("standard", new_content)


if __name__ == "__main__":
    unittest.main()
