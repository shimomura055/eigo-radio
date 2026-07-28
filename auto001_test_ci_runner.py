"""scripts/run_ci_tests.py (AUTO-001 CIテストrunner)自身の単体テスト。

実際の外部API・外部ネットワークは一切使わない。固定のtempdir上に最小限の
偽repository(fixture manifestとfixture testファイル)を作り、runnerの
manifest検証・ファイル分類・テストID収集・除外計算・実行結果を検証する。
"""

from __future__ import annotations

import json
import os
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts import run_ci_tests as rct  # noqa: E402


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _minimal_manifest(include=None, exclude=None, excluded_test_ids=None) -> dict:
    return {
        "schema_version": "1.0",
        "include": include if include is not None else [],
        "exclude": exclude if exclude is not None else [],
        "excluded_test_ids": excluded_test_ids if excluded_test_ids is not None else [],
    }


PASS_TEST_SRC = """
import unittest

class SampleTests(unittest.TestCase):
    def test_ok_one(self):
        self.assertTrue(True)

    def test_ok_two(self):
        self.assertEqual(1 + 1, 2)
"""

FAIL_TEST_SRC = """
import unittest

class SampleFailTests(unittest.TestCase):
    def test_fails(self):
        self.assertTrue(False)
"""

POISON_SRC = """
raise RuntimeError("このファイルはimportされてはならない(exclude対象)")
"""

NETWORK_ATTEMPT_SRC = """
import socket
import unittest

class NetworkTests(unittest.TestCase):
    def test_tries_to_connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("example.com", 80))
"""


class ManifestValidationTests(unittest.TestCase):
    def test_valid_manifest_passes(self):
        manifest = _minimal_manifest(
            include=[{"path": "a_test.py", "reason": "r"}],
            excluded_test_ids=[{
                "test_id": "a_test.T.test_x",
                "reason": "r",
                "exclusion_type": "OTHER",
                "platform": "ALL",
                "duration": "PERMANENT",
                "follow_up_id": "X-1",
                "release_condition": "c",
            }],
        )
        rct.validate_manifest_structure(manifest)  # raiseしなければOK

    def test_missing_top_level_key_raises(self):
        manifest = _minimal_manifest()
        del manifest["exclude"]
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)

    def test_missing_file_entry_reason_raises(self):
        manifest = _minimal_manifest(include=[{"path": "a_test.py"}])
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)

    def test_missing_excluded_id_field_raises(self):
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": "a_test.T.test_x", "reason": "r",
            "exclusion_type": "OTHER", "platform": "ALL", "duration": "PERMANENT",
            # follow_up_id, release_condition missing
        }])
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)

    def test_invalid_exclusion_type_raises(self):
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": "a_test.T.test_x", "reason": "r",
            "exclusion_type": "NOT_A_REAL_TYPE", "platform": "ALL", "duration": "PERMANENT",
            "follow_up_id": "X-1", "release_condition": "c",
        }])
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)

    def test_invalid_duration_raises(self):
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": "a_test.T.test_x", "reason": "r",
            "exclusion_type": "OTHER", "platform": "ALL", "duration": "SOMETIMES",
            "follow_up_id": "X-1", "release_condition": "c",
        }])
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)

    def test_duplicate_excluded_test_id_raises(self):
        entry = {
            "test_id": "a_test.T.test_x", "reason": "r",
            "exclusion_type": "OTHER", "platform": "ALL", "duration": "PERMANENT",
            "follow_up_id": "X-1", "release_condition": "c",
        }
        manifest = _minimal_manifest(excluded_test_ids=[dict(entry), dict(entry)])
        with self.assertRaises(rct.ManifestError):
            rct.validate_manifest_structure(manifest)


class ClassifyFilesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_include_exclude_overlap_raises(self):
        _write(self.root / "dup_test.py", PASS_TEST_SRC)
        manifest = _minimal_manifest(
            include=[{"path": "dup_test.py", "reason": "r"}],
            exclude=[{"path": "dup_test.py", "reason": "r"}],
        )
        with self.assertRaises(rct.ManifestError):
            rct.classify_files(manifest, ["dup_test.py"], self.root)

    def test_nonexistent_file_registration_raises(self):
        manifest = _minimal_manifest(include=[{"path": "ghost_test.py", "reason": "r"}])
        with self.assertRaises(rct.ManifestError):
            rct.classify_files(manifest, [], self.root)

    def test_unclassified_candidate_raises(self):
        _write(self.root / "unknown_test.py", PASS_TEST_SRC)
        manifest = _minimal_manifest()
        with self.assertRaises(rct.ManifestError):
            rct.classify_files(manifest, ["unknown_test.py"], self.root)

    def test_happy_path_classification(self):
        _write(self.root / "good_test.py", PASS_TEST_SRC)
        _write(self.root / "danger_test.py", POISON_SRC)
        manifest = _minimal_manifest(
            include=[{"path": "good_test.py", "reason": "r"}],
            exclude=[{"path": "danger_test.py", "reason": "r"}],
        )
        include_paths, exclude_paths = rct.classify_files(
            manifest, ["good_test.py", "danger_test.py"], self.root
        )
        self.assertEqual(include_paths, ["good_test.py"])
        self.assertEqual(exclude_paths, ["danger_test.py"])


class DiscoverCandidateFilesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_discovers_files_with_test_substring(self):
        _write(self.root / "foo_test_bar.py", PASS_TEST_SRC)
        _write(self.root / "not_matching.py", PASS_TEST_SRC)
        candidates = rct.discover_candidate_files(self.root)
        self.assertIn("foo_test_bar.py", candidates)
        self.assertNotIn("not_matching.py", candidates)

    def test_does_not_recurse_into_subdirectories(self):
        sub = self.root / "sub"
        sub.mkdir()
        _write(sub / "nested_test.py", PASS_TEST_SRC)
        candidates = rct.discover_candidate_files(self.root)
        self.assertEqual(candidates, [])


class CollectAndExcludeTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self._orig_sys_path = list(sys.path)
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), self._orig_sys_path))
        self._orig_modules = set(sys.modules)
        self.addCleanup(self._purge_modules)

    def _purge_modules(self):
        for name in list(sys.modules):
            if name not in self._orig_modules:
                del sys.modules[name]

    def test_excluded_file_is_never_imported(self):
        _write(self.root / "collect_good_test.py", PASS_TEST_SRC)
        _write(self.root / "collect_danger_test.py", POISON_SRC)
        # collect_test_idsにはincludeファイルだけを渡す。excludeファイルには一切触れない。
        ids = rct.collect_test_ids(self.root, ["collect_good_test.py"])
        self.assertEqual(len(ids), 2)
        self.assertNotIn("collect_danger_test", sys.modules)

    def test_compute_exclusions_removes_all_platform_id(self):
        _write(self.root / "excl_a_test.py", PASS_TEST_SRC)
        ids = rct.collect_test_ids(self.root, ["excl_a_test.py"])
        target = "excl_a_test.SampleTests.test_ok_one"
        self.assertIn(target, ids)
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": target, "reason": "r", "exclusion_type": "OTHER",
            "platform": "ALL", "duration": "PERMANENT",
            "follow_up_id": "X-1", "release_condition": "c",
        }])
        always_excl, plat_excl = rct.compute_exclusions(manifest, ids, "win32")
        self.assertIn(target, always_excl)
        self.assertEqual(plat_excl, {})
        # 同じファイル内の他テストは除外対象に含まれない
        self.assertNotIn("excl_a_test.SampleTests.test_ok_two", always_excl)

    def test_compute_exclusions_platform_specific_applies_only_on_matching_platform(self):
        _write(self.root / "excl_b_test.py", PASS_TEST_SRC)
        ids = rct.collect_test_ids(self.root, ["excl_b_test.py"])
        target = "excl_b_test.SampleTests.test_ok_one"
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": target, "reason": "r", "exclusion_type": "PLATFORM_NEWLINE_DIFFERENCE",
            "platform": "win32", "duration": "TEMPORARY",
            "follow_up_id": "X-2", "release_condition": "c",
        }])
        always_win, plat_win = rct.compute_exclusions(manifest, ids, "win32")
        self.assertEqual(always_win, {})
        self.assertIn(target, plat_win)

        always_linux, plat_linux = rct.compute_exclusions(manifest, ids, "linux")
        self.assertEqual(always_linux, {})
        self.assertEqual(plat_linux, {})  # Windows限定除外はLinuxでは適用されない

    def test_compute_exclusions_nonexistent_test_id_raises(self):
        _write(self.root / "excl_c_test.py", PASS_TEST_SRC)
        ids = rct.collect_test_ids(self.root, ["excl_c_test.py"])
        manifest = _minimal_manifest(excluded_test_ids=[{
            "test_id": "excl_c_test.SampleTests.test_does_not_exist",
            "reason": "r", "exclusion_type": "OTHER", "platform": "ALL",
            "duration": "PERMANENT", "follow_up_id": "X-3", "release_condition": "c",
        }])
        with self.assertRaises(rct.ManifestError):
            rct.compute_exclusions(manifest, ids, "win32")


class NetworkBlockTests(unittest.TestCase):
    def setUp(self):
        self._orig_connect = socket.socket.connect
        self._orig_connect_ex = socket.socket.connect_ex
        self._orig_create_connection = socket.create_connection
        rct._network_block_triggered = False
        self.addCleanup(self._restore)

    def _restore(self):
        socket.socket.connect = self._orig_connect
        socket.socket.connect_ex = self._orig_connect_ex
        socket.create_connection = self._orig_create_connection
        rct._network_block_triggered = False

    def test_connect_is_blocked_after_install(self):
        rct.install_network_block()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with self.assertRaises(rct.NetworkAccessBlockedError):
            s.connect(("example.com", 80))
        self.assertTrue(rct.network_block_triggered())


class ChildEnvTests(unittest.TestCase):
    def test_dummy_key_present_only_in_returned_dict(self):
        before = dict(os.environ)
        env = rct.build_child_env()
        self.assertEqual(env.get("OPENAI_API_KEY"), rct.DUMMY_OPENAI_API_KEY)
        # 親プロセスのos.environは一切変更されていない(呼び出し前後で完全に同一)
        self.assertEqual(dict(os.environ), before)

    def test_dummy_key_overrides_any_real_key_without_mutating_parent(self):
        # 呼び出し元プロセスに本物らしきキーが既に設定されていても、
        # build_child_envが返す辞書ではダミー値へ上書きされ、かつ
        # 呼び出し元プロセスのos.environ自体は変更されないことを確認する。
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "sk-not-a-real-key-but-looks-real"}):
            before = dict(os.environ)
            env = rct.build_child_env()
            self.assertEqual(env.get("OPENAI_API_KEY"), rct.DUMMY_OPENAI_API_KEY)
            self.assertEqual(dict(os.environ), before)
            self.assertEqual(os.environ["OPENAI_API_KEY"], "sk-not-a-real-key-but-looks-real")


class EndToEndTests(unittest.TestCase):
    """main()を通した終了コードの検証。実際にworker subprocessを起動する。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _write_manifest(self, manifest: dict) -> None:
        _write(self.root / rct.MANIFEST_FILENAME, json.dumps(manifest, ensure_ascii=False))

    def test_all_pass_returns_exit_0(self):
        _write(self.root / "e2e_pass_test.py", PASS_TEST_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_pass_test.py", "reason": "r"}]
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertEqual(code, 0)

    def test_failure_returns_nonzero(self):
        _write(self.root / "e2e_fail_test.py", FAIL_TEST_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_fail_test.py", "reason": "r"}]
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertNotEqual(code, 0)

    def test_excluded_id_not_run_and_remaining_tests_still_pass(self):
        _write(self.root / "e2e_mixed_test.py", PASS_TEST_SRC + "\n" + FAIL_TEST_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_mixed_test.py", "reason": "r"}],
            excluded_test_ids=[{
                "test_id": "e2e_mixed_test.SampleFailTests.test_fails",
                "reason": "既知の失敗を除外", "exclusion_type": "OTHER",
                "platform": "ALL", "duration": "PERMANENT",
                "follow_up_id": "X-4", "release_condition": "c",
            }],
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertEqual(code, 0)  # 失敗するテストを除外したので全体は成功扱い

    def test_uncollectable_excluded_id_fails_before_running(self):
        _write(self.root / "e2e_uncoll_test.py", PASS_TEST_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_uncoll_test.py", "reason": "r"}],
            excluded_test_ids=[{
                "test_id": "e2e_uncoll_test.SampleTests.test_does_not_exist",
                "reason": "r", "exclusion_type": "OTHER", "platform": "ALL",
                "duration": "PERMANENT", "follow_up_id": "X-5", "release_condition": "c",
            }],
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertNotEqual(code, 0)

    def test_duplicate_exclusion_registration_fails(self):
        _write(self.root / "e2e_dup_test.py", PASS_TEST_SRC)
        entry = {
            "test_id": "e2e_dup_test.SampleTests.test_ok_one",
            "reason": "r", "exclusion_type": "OTHER", "platform": "ALL",
            "duration": "PERMANENT", "follow_up_id": "X-6", "release_condition": "c",
        }
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_dup_test.py", "reason": "r"}],
            excluded_test_ids=[dict(entry), dict(entry)],
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertNotEqual(code, 0)

    def test_network_attempt_causes_failure(self):
        _write(self.root / "e2e_net_test.py", NETWORK_ATTEMPT_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_net_test.py", "reason": "r"}]
        ))
        code = rct.main(argv=[], root_override=self.root)
        self.assertNotEqual(code, 0)

    def test_windows_only_exclusion_end_to_end(self):
        _write(self.root / "e2e_plat_test.py", PASS_TEST_SRC)
        self._write_manifest(_minimal_manifest(
            include=[{"path": "e2e_plat_test.py", "reason": "r"}],
            excluded_test_ids=[{
                "test_id": "e2e_plat_test.SampleTests.test_ok_one",
                "reason": "r", "exclusion_type": "PLATFORM_NEWLINE_DIFFERENCE",
                "platform": "this-platform-does-not-exist",
                "duration": "TEMPORARY", "follow_up_id": "X-7", "release_condition": "c",
            }],
        ))
        # 現在のプラットフォームには一致しないplatform指定なので、除外されず実行され、成功する
        code = rct.main(argv=[], root_override=self.root)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
