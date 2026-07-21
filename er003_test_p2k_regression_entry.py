# ============================================================
# er003_test_p2k_regression_entry.py
# ER-003-P2K: プロジェクト全体回帰テスト入口の一本化のテスト
# ============================================================
# 実API・Web検索は一切行わない。canonical entry point
# (run_project_regression.py)自身の探索・集計・終了コードロジックを、
# 隔離した一時ディレクトリのfixtureと実リポジトリの両方で検証する。
#
# 実行方法:
#   .venv/Scripts/python.exe -m unittest er003_test_p2k_regression_entry -v

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import run_project_regression as entry

REPO_ROOT = entry.resolve_repo_root()


def _purge_modules_imported_from(dir_path: Path) -> None:
    """unittest.TestLoader.discover()はモジュール名でsys.modulesへ
    キャッシュするため、異なる一時ディレクトリで同名のfixtureファイルを
    使うテストが連続すると、同一プロセス内で衝突しImportErrorになる。
    各テストの前後でそのディレクトリ由来のモジュールをsys.modulesから
    除去し、隔離する。"""
    dir_str = str(dir_path)
    for name in [n for n, m in list(sys.modules.items())
                if getattr(m, "__file__", None) and str(m.__file__).startswith(dir_str)]:
        del sys.modules[name]


def write_test_file(root: Path, filename: str, passing: bool = True, count: int = 2) -> None:
    body = "\n".join(
        f"    def test_case_{i}(self):\n        self.assertTrue({'True' if passing else 'False'})"
        for i in range(count)
    )
    content = f"import unittest\n\nclass FixtureTests(unittest.TestCase):\n{body}\n"
    (root / filename).write_text(content, encoding="utf-8")


class TempRepoTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.root = Path(self.tmp_dir)

    def tearDown(self):
        _purge_modules_imported_from(self.root)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class DiscoveryTests(TempRepoTestCase):

    def test_matches_er002_and_er003_prefixed_files(self):
        write_test_file(self.root, "er002_test_common.py")
        write_test_file(self.root, "er003_test_something.py")
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, self.root)
        self.assertEqual(files, ["er002_test_common.py", "er003_test_something.py"])

    def test_excludes_non_matching_files(self):
        write_test_file(self.root, "er002_test_common.py")
        (self.root / "test_api.py").write_text("import unittest\n", encoding="utf-8")
        (self.root / "generate_test.py").write_text("import unittest\n", encoding="utf-8")
        (self.root / "tts_test.py").write_text("import unittest\n", encoding="utf-8")
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, self.root)
        self.assertEqual(files, ["er002_test_common.py"])

    def test_newly_added_file_picked_up_without_code_changes(self):
        """手動module列挙が不要であることの直接検証: 新しいfileを追加
        しただけで、コード変更なしに探索対象へ含まれる。"""
        write_test_file(self.root, "er003_test_first.py")
        before = entry.discover_test_files(entry.DEFAULT_PATTERN, self.root)
        write_test_file(self.root, "er003_test_second.py")
        after = entry.discover_test_files(entry.DEFAULT_PATTERN, self.root)
        self.assertEqual(len(after), len(before) + 1)
        self.assertIn("er003_test_second.py", after)

    def test_zero_matching_files_returns_empty_list(self):
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, self.root)
        self.assertEqual(files, [])


class RunFunctionTests(TempRepoTestCase):

    def test_zero_collected_is_treated_as_failure(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code, summary = entry.run(root=self.root)
        self.assertEqual(exit_code, 1)
        self.assertIsNone(summary)
        self.assertIn("0 tests collected", stderr.getvalue())

    def test_all_passing_returns_zero(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=3)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code, summary = entry.run(root=self.root)
        self.assertEqual(exit_code, 0)
        self.assertTrue(summary["wasSuccessful"])
        self.assertEqual(summary["collected"], 3)
        self.assertEqual(summary["passed"], 3)
        self.assertEqual(summary["failed"], 0)

    def test_any_failure_returns_nonzero(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=2)
        write_test_file(self.root, "er003_test_bad.py", passing=False, count=1)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code, summary = entry.run(root=self.root)
        self.assertEqual(exit_code, 1)
        self.assertFalse(summary["wasSuccessful"])
        self.assertEqual(summary["collected"], 3)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["passed"], 2)

    def test_collected_and_passed_are_distinguished_on_success(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=5)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            _, summary = entry.run(root=self.root)
        self.assertIn("collected", summary)
        self.assertIn("passed", summary)
        self.assertEqual(summary["collected"], summary["passed"])

    def test_pattern_and_scope_are_printed(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=1)
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            entry.run(root=self.root)
        output = stdout.getvalue()
        self.assertIn("discovery pattern", output)
        self.assertIn(entry.DEFAULT_PATTERN, output)
        self.assertIn("repo root", output)


class MainCliTests(TempRepoTestCase):

    def test_json_summary_written_when_requested(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=2)
        original_root = entry.resolve_repo_root
        entry.resolve_repo_root = lambda: self.root
        try:
            summary_path = str(self.root / "summary.json")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = entry.main(["--json-summary", summary_path])
            self.assertEqual(exit_code, 0)
            with open(summary_path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["collected"], 2)
            self.assertTrue(data["wasSuccessful"])
        finally:
            entry.resolve_repo_root = original_root

    def test_custom_pattern_argument_is_respected(self):
        write_test_file(self.root, "er003_test_ok.py", passing=True, count=1)
        write_test_file(self.root, "other_prefix_test_ignored.py", passing=True, count=1)
        original_root = entry.resolve_repo_root
        entry.resolve_repo_root = lambda: self.root
        try:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = entry.main(["--pattern", "er003_test_*.py"])
            self.assertEqual(exit_code, 0)
            self.assertIn("er003_test_ok.py", stdout.getvalue())
            self.assertNotIn("other_prefix_test_ignored.py", stdout.getvalue())
        finally:
            entry.resolve_repo_root = original_root


class RepoRootResolutionTests(unittest.TestCase):

    def test_resolve_repo_root_points_to_actual_repo(self):
        root = entry.resolve_repo_root()
        self.assertTrue((root / "CLAUDE.md").exists())
        self.assertTrue((root / "run_project_regression.py").exists())

    def test_resolution_independent_of_current_working_directory(self):
        original_cwd = os.getcwd()
        tmp_dir = tempfile.mkdtemp()
        try:
            os.chdir(tmp_dir)
            root = entry.resolve_repo_root()
            self.assertEqual(root, REPO_ROOT)
        finally:
            os.chdir(original_cwd)
            shutil.rmtree(tmp_dir, ignore_errors=True)


class RealRepoIntegrationTests(unittest.TestCase):
    """実リポジトリに対する探索(実行はしない、収集のみ)を検証する。
    実行(run())はここでは行わない(プロジェクト全体を毎回二重に実行
    すると回帰実行コストが倍になるため、本ファイル自身が
    project-wide regressionの一部として実行される際にすでに検証されて
    いる)。"""

    def test_default_pattern_discovers_both_er002_and_er003_files(self):
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, REPO_ROOT)
        self.assertTrue(any(f.startswith("er002_test_") for f in files))
        self.assertTrue(any(f.startswith("er003_test_") for f in files))

    def test_default_pattern_excludes_legacy_manual_scripts(self):
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, REPO_ROOT)
        self.assertNotIn("test_api.py", files)
        self.assertNotIn("generate_test.py", files)
        self.assertNotIn("tts_test.py", files)
        self.assertNotIn("tts_style_test.py", files)

    def test_discovered_file_count_matches_glob_count(self):
        import glob
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, REPO_ROOT)
        self.assertEqual(len(files), len(glob.glob(entry.DEFAULT_PATTERN)))

    def test_this_file_itself_is_discovered(self):
        files = entry.discover_test_files(entry.DEFAULT_PATTERN, REPO_ROOT)
        self.assertIn("er003_test_p2k_regression_entry.py", files)

    def test_loader_collection_does_not_raise_for_real_repo(self):
        """実リポジトリ全体のcollectionが例外なく完了することを確認する
        (実行はしない、収集のみで高速)。"""
        loader = unittest.TestLoader()
        suite = loader.discover(str(REPO_ROOT), pattern=entry.DEFAULT_PATTERN)
        collected = entry.count_tests_in_suite(suite)
        self.assertGreater(collected, 1000)


if __name__ == "__main__":
    unittest.main()
