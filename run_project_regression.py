# ============================================================
# run_project_regression.py
# ER-003-P2K: プロジェクト全体回帰テスト入口の一本化
# ============================================================
# ER-002・ER-003の回帰テストスイート全体を自動探索して実行する、唯一の
# 正式な「project-wide regression」入口。
#
# ER-003-P2Jで、テスト件数の食い違い(P2H 1032件 vs P2I 660件)の原因が
# DIFFERENT_TEST_SCOPEだったと判明した。P2Hは手動でtest module名を21個
# 列挙するcommandを使い、P2Iはer003_test_*.pyだけをglob探索するcommand
# を使っていたため、対象範囲が食い違っていた。本スクリプトはこの再発を
# 防ぐため、手動module列挙を正式手順から外し、単一のglob patternによる
# 自動探索だけを「プロジェクト全体回帰テスト」の正式手段とする。
#
# 対象範囲(scope): er002_test_*.py + er003_test_*.py (pattern: er0*_test_*.py)
# ER-001には現時点でunittest形式の回帰テストが存在しない(調査済み、
# ER-003-P2K完了報告に記録)。将来ER-001向けのer001_test_*.pyが追加
# されれば、本patternへ含めるかは別途判断する。
#
# 使い方:
#   python run_project_regression.py
#   python run_project_regression.py --json-summary path/to/summary.json
#
# 終了コード:
#   0: 全件成功
#   1: 収集0件、またはtest失敗/エラーがある場合
#
# どのカレントディレクトリから実行してもrepository rootを自動解決する
# (このファイル自身の場所を基準にするため、root以外から呼び出しても
# 対象範囲は変わらない)。

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path

DEFAULT_PATTERN = "er0*_test_*.py"


def resolve_repo_root() -> Path:
    return Path(__file__).resolve().parent


def discover_test_files(pattern: str, root: Path) -> list:
    return sorted(str(p.relative_to(root)) for p in root.glob(pattern))


def count_tests_in_suite(suite) -> int:
    count = 0
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            count += count_tests_in_suite(t)
        else:
            count += 1
    return count


def build_summary(pattern: str, files: list, collected: int, result: "unittest.TestResult") -> dict:
    return {
        "pattern": pattern,
        "test_files": files,
        "test_file_count": len(files),
        "collected": collected,
        "passed": result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        "failed": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "wasSuccessful": result.wasSuccessful(),
    }


def run(pattern: str = DEFAULT_PATTERN, verbosity: int = 1, root: Path = None) -> tuple:
    """探索・実行を行い、(exit_code, summary_dict または None)を返す。
    収集0件の場合はtestを実行せずexit_code=1・summary=Noneを返す。"""
    root = root if root is not None else resolve_repo_root()
    files = discover_test_files(pattern, root)

    print(f"[run_project_regression] repo root: {root}")
    print(f"[run_project_regression] discovery pattern: {pattern}")
    print(f"[run_project_regression] discovered {len(files)} test file(s):")
    for f in files:
        print(f"  - {f}")

    loader = unittest.TestLoader()
    suite = loader.discover(str(root), pattern=pattern)
    collected = count_tests_in_suite(suite)

    if collected == 0:
        print("[run_project_regression] FAILED: 0 tests collected", file=sys.stderr)
        return 1, None

    print(f"[run_project_regression] collected {collected} test(s)")

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    summary = build_summary(pattern, files, collected, result)

    print(f"[run_project_regression] collected={summary['collected']} passed={summary['passed']} "
          f"failed={summary['failed']} errors={summary['errors']} skipped={summary['skipped']}")

    return (0 if result.wasSuccessful() else 1), summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="ER-002+ER-003 project-wide regression test canonical entry point")
    parser.add_argument("--pattern", default=DEFAULT_PATTERN,
                        help=f"glob pattern for test discovery (default: {DEFAULT_PATTERN})")
    parser.add_argument("-v", "--verbosity", type=int, default=1)
    parser.add_argument("--json-summary", default=None,
                        help="collected/passed/failed/skippedをJSONへ保存するpath(省略可)")
    args = parser.parse_args(argv)

    exit_code, summary = run(pattern=args.pattern, verbosity=args.verbosity)

    if args.json_summary and summary is not None:
        with open(args.json_summary, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"[run_project_regression] summary written: {args.json_summary}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
