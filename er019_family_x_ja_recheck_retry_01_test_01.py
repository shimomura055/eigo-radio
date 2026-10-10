# ============================================================
# er019_family_x_ja_recheck_retry_01_test_01.py
# FAMILY-X-REFRESH-E2E-PRODUCTION-WIRING-01(W6) -> RISK-FLAGGER-PRODUCTION-WIRING-01 C2で無効化
# ============================================================
# 【無効化(legacy)】2026-10-10 C2: ja_source MAJOR(JARecheckRequiredError)発生時の暫定対応「案B」
# (English側Deviation CheckがJA R2由来MAJORを検出した場合のJA 1回再生成+Advanced/Standard再実行)は、
# 旧Fact Checker全面撤去(ユーザー決定2026-10-08/RISK-FLAGGER-PRODUCTION-WIRING-01、案P物理削除)で
# 実装ごと削除された。本ファイルの旧testは削除済みの機構を前提としていたため、撤去の事実を固定する
# testのみ残す(旧挙動の再現は C2適用前の commit f71dbb41 の worktree で行う)。
# 実行方法: .venv/Scripts/python.exe -m pytest er019_family_x_ja_recheck_retry_01_test_01.py -q
# ============================================================
from __future__ import annotations

import inspect
import unittest

import er012_e_family_entertainment_two_level_runner_01 as runner
import er019_family_x_ja_writer_o_r1_r2_01 as jaw


class JaRecheckPlanBRemovedTests(unittest.TestCase):
    def test_ja_recheck_symbols_removed_from_efam(self):
        for name in ("JARecheckRequiredError", "_major_deviations", "_must_fix_from_deviations",
                     "open243_m1_enabled", "open243_m1_summary_only_retry", "open243_majors_only_in_summary",
                     "open243_g3_record_translation_minor", "_open243_iol"):
            self.assertFalse(hasattr(runner, name), name)

    def test_run_writer_stage_has_no_plan_b_arguments(self):
        params = list(inspect.signature(runner.run_writer_stage).parameters)
        self.assertEqual(params, ["client", "theme", "ja_text", "ledger_text", "budget_jpy", "only"])

    def test_jaw_has_no_original_must_fix_or_full_ledger_arguments(self):
        params = list(inspect.signature(jaw.run_ja_writer_o_r1_r2).parameters)
        self.assertEqual(params, ["client", "storyline_line", "selected_fact_brief_text"])

    def test_no_ja_recheck_artifacts_written_by_efam_source(self):
        src = inspect.getsource(runner)
        for token in ("ja_recheck", "JA_RECHECK_REQUIRED", "pre_recheck_sha256"):
            self.assertNotIn(token, src, token)


if __name__ == "__main__":
    unittest.main()
