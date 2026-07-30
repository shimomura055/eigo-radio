"""Controller App installation tokenのread-only疎通チェック(AUTO-001-05-03-02)。

GitHub Actions上で、Controller GitHub App(`eigo-radio-auto-controller`)の
installation tokenを生成した後段の判定処理だけを、GitHub API・ネットワーク
アクセスを一切行わない決定論的な純粋関数として実装する。

このモジュール自身は次を一切行わない:

* installation tokenの生成(`actions/create-github-app-token`が担う)
* GitHub APIへのHTTPリクエスト送信(workflow側のcurlステップが担い、
  レスポンスは一時ファイル経由でこのモジュールへ渡される)
* private key・JWT・installation token・Authorization headerの読み取りや
  出力(このモジュールの入力・出力のいずれにも登場しない)

設計上の責務分離:

* `check_required_config()` -- Variable/Secretの「値」ではなく「存在有無の
  真偽値」だけを受け取り、欠落時の固定reason codeを返す。
* `validate_repository_scope()` -- `GET /installation/repositories`の
  レスポンス(パース済みJSON)を検証し、対象repositoryが厳密に1件かつ
  現在のrepositoryと一致するかどうかだけを判定する。repository名は
  一致した場合であっても人間向け出力へは含めない(呼び出し側の責務)。
* `validate_issue_read()` -- Issue read APIのレスポンス(パース済みJSON)
  から`number`フィールドだけを検証する。本文・タイトル・コメントなどの
  未信頼フィールドは一切参照しない。
* CLI (`main()`) -- 上記3つをファイルパス/フラグ経由で呼び出し、固定
  語彙の1行だけを標準出力へ書く。raw例外メッセージや入力値の断片は
  出力しない。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ReasonCode(str, Enum):
    CONFIG_CLIENT_ID_MISSING = "CONFIG_CLIENT_ID_MISSING"
    CONFIG_PRIVATE_KEY_MISSING = "CONFIG_PRIVATE_KEY_MISSING"
    TOKEN_GENERATION_FAILED = "TOKEN_GENERATION_FAILED"
    REPOSITORY_SCOPE_QUERY_FAILED = "REPOSITORY_SCOPE_QUERY_FAILED"
    REPOSITORY_SCOPE_MISMATCH = "REPOSITORY_SCOPE_MISMATCH"
    ISSUE_READ_FAILED = "ISSUE_READ_FAILED"
    RESPONSE_VALIDATION_FAILED = "RESPONSE_VALIDATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(frozen=True)
class CheckOutcome:
    """呼び出し側(workflow)が機械的に解釈できる最小限の結果。

    `detail`は固定語彙・数値・真偽値だけで構成し、未信頼入力の内容(repository
    名の一覧、Issue本文、raw JSONなど)を一切含めない。
    """

    ok: bool
    reason_code: Optional[ReasonCode]
    detail: dict[str, Any]

    def to_line(self) -> str:
        parts = [f"OK={'true' if self.ok else 'false'}"]
        parts.append(f"REASON_CODE={self.reason_code.value if self.reason_code else 'NONE'}")
        for key in sorted(self.detail):
            parts.append(f"{key}={self.detail[key]}")
        return " ".join(parts)


# ---------------------------------------------------------------------------
# 1. 必須Variable/Secretの存在検査
# ---------------------------------------------------------------------------

def check_required_config(client_id_present: bool, private_key_present: bool) -> CheckOutcome:
    """Variable/Secretの値そのものではなく、存在有無の真偽値だけを受け取る。

    呼び出し側(workflow)は、値の中身を一切このプロセスへ渡してはならない。
    """
    if not client_id_present:
        return CheckOutcome(False, ReasonCode.CONFIG_CLIENT_ID_MISSING, {})
    if not private_key_present:
        return CheckOutcome(False, ReasonCode.CONFIG_PRIVATE_KEY_MISSING, {})
    return CheckOutcome(True, None, {})


# ---------------------------------------------------------------------------
# 2. repositoryスコープ検証(GET /installation/repositories)
# ---------------------------------------------------------------------------

def validate_repository_scope(raw: Any, expected_full_name: str) -> CheckOutcome:
    """`GET /installation/repositories`のレスポンスを検証する。

    許可されるのは次の判定だけであり、repository名そのものは`detail`へ含めない。

    * repository件数(REPOSITORY_COUNT)
    * 期待するrepositoryと一致したか(MATCHED)
    """
    if not isinstance(expected_full_name, str) or not expected_full_name:
        raise ValueError("expected_full_nameは空でない文字列である必要があります")

    if not isinstance(raw, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    repositories = raw.get("repositories")
    if not isinstance(repositories, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    names: list[str] = []
    for entry in repositories:
        if not isinstance(entry, dict):
            return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
        full_name = entry.get("full_name")
        if not isinstance(full_name, str) or not full_name:
            return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
        names.append(full_name)

    count = len(names)
    if count != 1:
        return CheckOutcome(
            False, ReasonCode.REPOSITORY_SCOPE_MISMATCH,
            {"REPOSITORY_COUNT": count, "MATCHED": "false"},
        )

    matched = names[0] == expected_full_name
    if not matched:
        return CheckOutcome(
            False, ReasonCode.REPOSITORY_SCOPE_MISMATCH,
            {"REPOSITORY_COUNT": 1, "MATCHED": "false"},
        )

    return CheckOutcome(True, None, {"REPOSITORY_COUNT": 1, "MATCHED": "true"})


# ---------------------------------------------------------------------------
# 3. Issue read検証(GET /repos/{owner}/{repo}/issues/{number})
# ---------------------------------------------------------------------------

def validate_issue_read(raw: Any, expected_issue_number: int) -> CheckOutcome:
    """Issue read APIのレスポンスから`number`フィールドだけを検証する。

    本文(body)・タイトル(title)・コメントなど、未信頼な自由記述フィールドは
    一切参照・出力しない。
    """
    if not isinstance(expected_issue_number, int) or isinstance(expected_issue_number, bool):
        raise ValueError("expected_issue_numberは整数である必要があります")
    if expected_issue_number <= 0:
        raise ValueError("expected_issue_numberは正の整数である必要があります")

    if not isinstance(raw, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    number = raw.get("number")
    if not isinstance(number, int) or isinstance(number, bool):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    matched = number == expected_issue_number
    if not matched:
        return CheckOutcome(False, ReasonCode.ISSUE_READ_FAILED, {"ISSUE_NUMBER_MATCHED": "false"})

    return CheckOutcome(True, None, {"ISSUE_NUMBER_MATCHED": "true"})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _bool_arg(value: str) -> bool:
    if value not in ("true", "false"):
        raise argparse.ArgumentTypeError("true または false を指定してください")
    return value == "true"


def _load_json_file(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _internal_error() -> CheckOutcome:
    return CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUTO-001-05-03-02 Controller App token read-only疎通チェック(純粋処理部分)"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_config = sub.add_parser("check-config", help="必須Variable/Secretの存在検査")
    p_config.add_argument("--client-id-present", type=_bool_arg, required=True)
    p_config.add_argument("--private-key-present", type=_bool_arg, required=True)

    p_scope = sub.add_parser("repo-scope", help="repositoryスコープ検証")
    p_scope.add_argument("--response-file", required=True)
    p_scope.add_argument("--expected-full-name", required=True)

    p_issue = sub.add_parser("issue-read", help="Issue read検証")
    p_issue.add_argument("--response-file", required=True)
    p_issue.add_argument("--expected-issue-number", type=int, required=True)

    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    try:
        if args.command == "check-config":
            outcome = check_required_config(args.client_id_present, args.private_key_present)
        elif args.command == "repo-scope":
            raw = _load_json_file(args.response_file)
            outcome = validate_repository_scope(raw, args.expected_full_name)
        elif args.command == "issue-read":
            raw = _load_json_file(args.response_file)
            outcome = validate_issue_read(raw, args.expected_issue_number)
        else:  # pragma: no cover - argparseがrequired=Trueで防ぐ
            outcome = _internal_error()
    except (OSError, json.JSONDecodeError, ValueError):
        # exc自体のstr()/repr()は埋め込まない(レスポンスファイルの内容の
        # 断片を含み得るため)。
        outcome = _internal_error()

    print(outcome.to_line())
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
