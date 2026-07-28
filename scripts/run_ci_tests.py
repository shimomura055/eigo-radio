"""AUTO-001 CIテストrunner。

ci_test_manifest.json を読み込み、ファイル名に"test"を含むリポジトリルート直下の
.pyファイルが漏れなくinclude/excludeへ分類されていることを検証したうえで、
includeされたファイルからunittestのテストIDを収集し、manifestで個別に除外
指定されたテストID(常時除外・現在のプラットフォームでのみ除外)を取り除いた
残りだけを、実際のAPIキー・外部ネットワークを使わない子プロセスで実行する。

ER-003側の run_project_regression.py / TESTING.md はコピーしておらず独立実装
(AUTO-001-03A §12参照)。標準ライブラリのみで実装しており、shell=Trueは使わない。
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MANIFEST_FILENAME = "ci_test_manifest.json"
CANDIDATE_SUBSTRING = "test"
DUMMY_OPENAI_API_KEY = "ci-placeholder-not-a-real-key"
WORKER_FLAG = "--_worker"


class ManifestError(Exception):
    """manifestの検証、またはファイル分類の検証に失敗した場合に送出する。"""


class NetworkAccessBlockedError(RuntimeError):
    """CIテスト実行中に外部ネットワーク接続が試みられた場合に送出する。"""


# ---------------------------------------------------------------------------
# パス解決
# ---------------------------------------------------------------------------

def resolve_repo_root() -> Path:
    """このファイル自身の場所を基準にrepository rootを解決する(実行ディレクトリに非依存)。"""
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# manifest読み込み・検証
# ---------------------------------------------------------------------------

def load_manifest(root: Path) -> dict:
    path = root / MANIFEST_FILENAME
    if not path.exists():
        raise ManifestError(f"manifestが見つかりません: {path}")
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise ManifestError(f"manifestのJSON構文が不正です: {e}") from e


_REQUIRED_TOP_KEYS = ("schema_version", "include", "exclude", "excluded_test_ids")
_REQUIRED_FILE_ENTRY_KEYS = ("path", "reason")
_REQUIRED_EXCLUDED_ID_KEYS = (
    "test_id", "reason", "exclusion_type", "platform", "duration",
    "follow_up_id", "release_condition",
)
_VALID_EXCLUSION_TYPES = {"LOCAL_ARTIFACT_REQUIRED", "PLATFORM_NEWLINE_DIFFERENCE", "OTHER"}
_VALID_DURATIONS = {"PERMANENT", "TEMPORARY"}


def validate_manifest_structure(manifest: dict) -> None:
    for key in _REQUIRED_TOP_KEYS:
        if key not in manifest:
            raise ManifestError(f"manifestに必須キー'{key}'がありません")

    for section in ("include", "exclude"):
        entries = manifest[section]
        if not isinstance(entries, list):
            raise ManifestError(f"manifestの'{section}'はリストである必要があります")
        for entry in entries:
            for key in _REQUIRED_FILE_ENTRY_KEYS:
                if key not in entry:
                    raise ManifestError(f"manifestの'{section}'内のエントリに必須キー'{key}'がありません: {entry}")

    excluded_ids = manifest["excluded_test_ids"]
    if not isinstance(excluded_ids, list):
        raise ManifestError("manifestの'excluded_test_ids'はリストである必要があります")
    seen_ids = set()
    for entry in excluded_ids:
        for key in _REQUIRED_EXCLUDED_ID_KEYS:
            if key not in entry:
                raise ManifestError(f"manifestの'excluded_test_ids'内のエントリに必須キー'{key}'がありません: {entry}")
        tid = entry["test_id"]
        if tid in seen_ids:
            raise ManifestError(f"除外テストIDが重複して登録されています: {tid}")
        seen_ids.add(tid)
        if entry["exclusion_type"] not in _VALID_EXCLUSION_TYPES:
            raise ManifestError(
                f"未知のexclusion_typeです: {entry['exclusion_type']} (test_id={tid})"
            )
        if entry["duration"] not in _VALID_DURATIONS:
            raise ManifestError(f"未知のdurationです: {entry['duration']} (test_id={tid})")


# ---------------------------------------------------------------------------
# ファイル分類
# ---------------------------------------------------------------------------

def discover_candidate_files(root: Path) -> list[str]:
    """ファイル名(大文字小文字を区別しない)に'test'を含む、リポジトリルート直下の
    .pyファイルを全て列挙する(分類対象の母集合)。サブディレクトリは走査しない。"""
    candidates = [
        p.name for p in root.glob("*.py")
        if CANDIDATE_SUBSTRING in p.name.lower()
    ]
    return sorted(candidates)


def classify_files(manifest: dict, candidates: list[str], root: Path) -> tuple[list[str], list[str]]:
    """manifestのinclude/excludeとcandidatesを突き合わせ、(include_paths, exclude_paths)を返す。
    重複登録・未分類・存在しないファイルの登録があればManifestErrorを送出する。"""
    include_paths = [e["path"] for e in manifest["include"]]
    exclude_paths = [e["path"] for e in manifest["exclude"]]

    include_set = set(include_paths)
    exclude_set = set(exclude_paths)

    if len(include_paths) != len(include_set):
        raise ManifestError("manifestの'include'にファイルパスの重複登録があります")
    if len(exclude_paths) != len(exclude_set):
        raise ManifestError("manifestの'exclude'にファイルパスの重複登録があります")

    overlap = include_set & exclude_set
    if overlap:
        raise ManifestError(f"同じファイルがincludeとexcludeの両方に登録されています: {sorted(overlap)}")

    for p in include_set | exclude_set:
        if not (root / p).exists():
            raise ManifestError(f"manifestに存在しないファイルが登録されています: {p}")

    candidate_set = set(candidates)
    unclassified = sorted(candidate_set - include_set - exclude_set)
    if unclassified:
        raise ManifestError(
            "未分類のtest候補ファイルがあります(ci_test_manifest.jsonのinclude/excludeへ登録してください): "
            f"{unclassified}"
        )

    return sorted(include_set), sorted(exclude_set)


# ---------------------------------------------------------------------------
# テストID収集
# ---------------------------------------------------------------------------

def _walk_test_ids(suite) -> list[str]:
    ids = []
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            ids.extend(_walk_test_ids(item))
        else:
            ids.append(item.id())
    return ids


def collect_test_ids(root: Path, include_paths: list[str]) -> list[str]:
    """sys.pathへrootを追加したうえで、includeされた各ファイルのテストIDを収集する。"""
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    loader = unittest.TestLoader()
    all_ids: list[str] = []
    for path in include_paths:
        module_name = path[:-3]  # ".py"を除去
        suite = loader.loadTestsFromName(module_name)
        all_ids.extend(_walk_test_ids(suite))
    return all_ids


# ---------------------------------------------------------------------------
# 除外テストIDの計算
# ---------------------------------------------------------------------------

def compute_exclusions(
    manifest: dict, collected_ids: list[str], current_platform: str
) -> tuple[dict[str, dict], dict[str, dict]]:
    """excluded_test_idsを検証し、(常時除外辞書, 現在プラットフォームでの除外辞書)を返す。
    test_id -> manifestエントリ の辞書。存在しないテストIDの登録、重複登録はここでも検出する
    (validate_manifest_structureで重複は既に検出済みだが、収集結果との突き合わせはここで行う)。"""
    collected_set = set(collected_ids)
    always_excluded: dict[str, dict] = {}
    platform_excluded: dict[str, dict] = {}

    for entry in manifest["excluded_test_ids"]:
        tid = entry["test_id"]
        if tid not in collected_set:
            raise ManifestError(
                f"除外指定されたテストIDが収集結果に存在しません(存在しないテストIDが"
                f"登録されている可能性があります): {tid}"
            )
        platform = entry["platform"]
        if platform == "ALL":
            always_excluded[tid] = entry
        elif platform == current_platform:
            platform_excluded[tid] = entry
        # platformが"ALL"でも現在のplatformでもない場合、このプラットフォームでは除外しない

    return always_excluded, platform_excluded


# ---------------------------------------------------------------------------
# ネットワーク遮断(workerプロセス内でのみインストールする)
# ---------------------------------------------------------------------------

_network_block_triggered = False


def _blocked_call(*_args, **_kwargs):
    global _network_block_triggered
    _network_block_triggered = True
    raise NetworkAccessBlockedError("CIテスト実行中の外部ネットワーク接続はブロックされています")


def install_network_block() -> None:
    socket.socket.connect = _blocked_call
    socket.socket.connect_ex = _blocked_call
    socket.create_connection = _blocked_call


def network_block_triggered() -> bool:
    return _network_block_triggered


# ---------------------------------------------------------------------------
# worker(子プロセス)entry point: 実際にunittestを実行する
# ---------------------------------------------------------------------------

def run_worker(root: Path, test_ids: list[str]) -> dict:
    """ネットワーク遮断をインストールしたうえで、指定されたテストIDだけを実行し、結果を返す。"""
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    install_network_block()

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(test_ids)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return {
        "testsRun": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "wasSuccessful": result.wasSuccessful(),
        "network_blocked_triggered": network_block_triggered(),
    }


def _worker_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(WORKER_FLAG, action="store_true", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--test-ids-file", required=True)
    parser.add_argument("--result-file", required=True)
    args = parser.parse_args(argv)

    root = Path(args.root)
    with open(args.test_ids_file, encoding="utf-8") as f:
        test_ids = [line.strip() for line in f if line.strip()]

    summary = run_worker(root, test_ids)

    with open(args.result_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False)

    return 0 if summary["wasSuccessful"] else 1


# ---------------------------------------------------------------------------
# 親プロセス(orchestrator)entry point
# ---------------------------------------------------------------------------

def build_child_env() -> dict:
    """子プロセス専用の環境変数辞書を作る。親プロセスのos.environは一切変更しない。"""
    env = dict(os.environ)
    env["OPENAI_API_KEY"] = DUMMY_OPENAI_API_KEY
    return env


def launch_worker_subprocess(root: Path, test_ids: list[str]) -> dict:
    """子プロセスでテストを実行し、結果summary(dict)を返す。
    親プロセスのos.environ・ユーザー環境は変更しない(env引数だけに閉じる)。"""
    fd_ids, ids_path = tempfile.mkstemp(suffix=".txt", prefix="auto001_ci_ids_")
    fd_result, result_path = tempfile.mkstemp(suffix=".json", prefix="auto001_ci_result_")
    os.close(fd_ids)
    os.close(fd_result)
    try:
        with open(ids_path, "w", encoding="utf-8") as f:
            f.write("\n".join(test_ids))

        cmd = [
            sys.executable,
            str(Path(__file__).resolve()),
            WORKER_FLAG,
            "--root", str(root),
            "--test-ids-file", ids_path,
            "--result-file", result_path,
        ]
        subprocess.run(cmd, cwd=str(root), env=build_child_env(), check=False)

        with open(result_path, encoding="utf-8") as f:
            return json.load(f)
    finally:
        for p in (ids_path, result_path):
            try:
                os.remove(p)
            except OSError:
                pass


def main(argv: list[str] | None = None, root_override: Path | None = None) -> int:
    """root_overrideはテスト専用。通常実行時はNoneのままresolve_repo_root()を使う。"""
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == WORKER_FLAG:
        return _worker_main(argv)

    root = root_override if root_override is not None else resolve_repo_root()

    print(f"[run_ci_tests] repository root: {root}")

    try:
        manifest = load_manifest(root)
        validate_manifest_structure(manifest)
        candidates = discover_candidate_files(root)
        print(f"[run_ci_tests] test候補ファイル(ファイル名に'test'を含む): {len(candidates)}件")

        include_paths, exclude_paths = classify_files(manifest, candidates, root)
        print(f"[run_ci_tests] include: {len(include_paths)}件 / exclude: {len(exclude_paths)}件")

        collected_ids = collect_test_ids(root, include_paths)
        print(f"[run_ci_tests] 収集したテストメソッド数: {len(collected_ids)}")

        always_excluded, platform_excluded = compute_exclusions(
            manifest, collected_ids, sys.platform
        )
    except ManifestError as e:
        print(f"[run_ci_tests] FAILED (manifest検証エラー): {e}", file=sys.stderr)
        return 1

    excluded_ids = set(always_excluded) | set(platform_excluded)
    run_ids = [tid for tid in collected_ids if tid not in excluded_ids]

    print(f"[run_ci_tests] 現在のプラットフォーム: {sys.platform}")
    print(f"[run_ci_tests] 常時除外: {len(always_excluded)}件")
    for tid, entry in always_excluded.items():
        print(f"  - {tid}")
        print(f"      種別={entry['exclusion_type']} follow_up={entry['follow_up_id']} 理由={entry['reason']}")
    print(f"[run_ci_tests] このプラットフォームでのみ除外: {len(platform_excluded)}件")
    for tid, entry in platform_excluded.items():
        print(f"  - {tid}")
        print(f"      種別={entry['exclusion_type']} follow_up={entry['follow_up_id']} 理由={entry['reason']}")
    print(f"[run_ci_tests] 実行するテストメソッド数: {len(run_ids)}")

    if not run_ids:
        print("[run_ci_tests] FAILED: 実行対象のテストが0件です", file=sys.stderr)
        return 1

    summary = launch_worker_subprocess(root, run_ids)

    print("[run_ci_tests] ---- 結果 ----")
    print(f"  testsRun={summary['testsRun']} failures={summary['failures']} "
          f"errors={summary['errors']} skipped={summary['skipped']}")
    print(f"  外部ネットワーク接続の試行検出: {summary['network_blocked_triggered']}")
    print(f"  wasSuccessful={summary['wasSuccessful']}")

    return 0 if summary["wasSuccessful"] else 1


if __name__ == "__main__":
    sys.exit(main())
