"""Implementer Launcher read-only dry-run(AUTO-001-06-01)。

`agent:working`ラベルが付与されたIssueについて、Implementer(将来のClaude
Code起動等)を実際に起動してよいかをread-onlyで判定し、契約正常な場合に
Implementerへ渡す決定的なtask bundle(JSON)を生成する。

このモジュール自身はGitHub APIへのHTTPリクエストを一切行わない。実際のHTTP
呼び出しはworkflow側のcurlステップが担い、レスポンス(JSON本文)は一時ファイル
経由でこのモジュールへ渡される。Issue本文・タイトル等の未信頼フィールドを
shell環境変数・command substitution・GITHUB_OUTPUT・Job Summaryへ流さない
設計方針は、既存のController App writer群(scripts.controller_label_writer /
scripts.controller_block_writer)と同一である。

既存モジュールの再利用方針(重複実装しない):

* `scripts.issue_agent_planner`の`AGENT_READY_LABEL` / `AGENT_WORKING_LABEL`
  / `AGENT_BLOCKED_LABEL` / `KNOWN_STATE_LABELS` / `CONFLICTING_STATE_LABELS`
  / `_sanitize_validation_errors()`をそのまま再利用する(`controller_block_writer`
  が同じ関数を再利用している既存の前例に倣う)。
* `scripts.issue_preflight_validator`の`validate_issue_body()` /
  `ValidationStatus` / `extract_task_fields()`をそのまま使う。Launcher独自の
  第二のpreflight validatorやIssue本文パーサーは実装しない。

このモジュールは、Claude Code・Implementer App・GitHub Appのいずれも起動・
接続しない。GitHubへの書き込み(ラベル変更・コメント投稿・Issue編集・branch
作成・commit・push・PR作成)は一切行わない。重複起動判定(WOULD_BLOCK_DUPLICATE)
は、branch命名・PR紐付け・実装開始markerの契約が未確定なため、v1では
到達不能な予約値として定義するに留める(推測で実装しない)。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from scripts.issue_agent_planner import (
    AGENT_BLOCKED_LABEL,
    AGENT_READY_LABEL,
    AGENT_WORKING_LABEL,
    CONFLICTING_STATE_LABELS,
    _sanitize_validation_errors,
)
from scripts.issue_preflight_validator import (
    AcceptanceCriterionField,
    ExtractedTaskFields,
    ValidationStatus,
    extract_task_fields,
    validate_issue_body,
)

__all__ = [
    "TASK_BUNDLE_SCHEMA_VERSION",
    "TriggerType",
    "Decision",
    "ReasonCode",
    "IssueSnapshot",
    "LauncherInput",
    "LauncherClassification",
    "ConsistencyCheckResult",
    "parse_positive_integer_strict",
    "parse_issue_snapshot",
    "classify",
    "check_source_unchanged",
    "build_task_bundle",
    "canonical_json_bytes",
    "main",
]


# ---------------------------------------------------------------------------
# decision / reason code契約
# ---------------------------------------------------------------------------

class TriggerType(str, Enum):
    ISSUES_LABELED = "issues:labeled"
    WORKFLOW_DISPATCH = "workflow_dispatch"


class Decision(str, Enum):
    WOULD_LAUNCH = "WOULD_LAUNCH"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    WOULD_BLOCK_STATE = "WOULD_BLOCK_STATE"
    WOULD_BLOCK_CONTRACT = "WOULD_BLOCK_CONTRACT"
    # AUTO-001-06-01: enum/出力契約上の予約値。branch命名・PR紐付け・実装
    # 開始markerの契約が未確定なため、v1のロジックからは一切到達しない。
    WOULD_BLOCK_DUPLICATE = "WOULD_BLOCK_DUPLICATE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ReasonCode(str, Enum):
    TARGET_IS_PULL_REQUEST = "TARGET_IS_PULL_REQUEST"
    LABEL_NOT_AGENT_WORKING = "LABEL_NOT_AGENT_WORKING"
    ISSUE_CLOSED = "ISSUE_CLOSED"
    AGENT_WORKING_LABEL_MISSING = "AGENT_WORKING_LABEL_MISSING"
    AGENT_READY_STILL_PRESENT = "AGENT_READY_STILL_PRESENT"
    AGENT_BLOCKED_PRESENT = "AGENT_BLOCKED_PRESENT"
    STATE_LABEL_CONFLICT = "STATE_LABEL_CONFLICT"
    PREFLIGHT_CONTRACT_VIOLATION = "PREFLIGHT_CONTRACT_VIOLATION"
    PREFLIGHT_VALIDATOR_INTERNAL_ERROR = "PREFLIGHT_VALIDATOR_INTERNAL_ERROR"
    TASK_FIELD_EXTRACTION_FAILED = "TASK_FIELD_EXTRACTION_FAILED"
    LAUNCH_READY = "LAUNCH_READY"
    SOURCE_CHANGED_BEFORE_OUTPUT = "SOURCE_CHANGED_BEFORE_OUTPUT"
    INVALID_ISSUE_NUMBER = "INVALID_ISSUE_NUMBER"
    RESPONSE_VALIDATION_FAILED = "RESPONSE_VALIDATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


TASK_BUNDLE_SCHEMA_VERSION = "AUTO-001-TASK-BUNDLE-V1"


# ---------------------------------------------------------------------------
# workflow_dispatch issue_number検証(fail-closed)
#
# AUTO-001-05-03-03C-R5で確立したpositive integer検証パターン
# (`^[1-9][0-9]*$`)をそのまま踏襲する。空文字列・0・負数・小数・数字以外・
# 先頭ゼロをすべて拒否する。
# ---------------------------------------------------------------------------

_POSITIVE_INTEGER_RE = re.compile(r"^[1-9][0-9]*$")


def parse_positive_integer_strict(value: str) -> Optional[int]:
    if not isinstance(value, str):
        return None
    if not _POSITIVE_INTEGER_RE.match(value):
        return None
    return int(value)


# ---------------------------------------------------------------------------
# GitHub Issue APIレスポンスの正規化(GET /repos/{owner}/{repo}/issues/{n})
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IssueSnapshot:
    """`GET /repos/{owner}/{repo}/issues/{number}`のレスポンスから抽出した、
    判定に必要な最小限のフィールド。初回取得・再取得のどちらにも使う共通形状。
    """

    issue_number: int
    is_open: bool
    is_pull_request: bool
    current_labels: tuple[str, ...]
    issue_body: str
    updated_at: str
    title: str
    html_url: str

    @property
    def body_sha256(self) -> str:
        return hashlib.sha256(self.issue_body.encode("utf-8")).hexdigest()


def parse_issue_snapshot(raw: Any) -> Optional[IssueSnapshot]:
    """Issue取得APIレスポンスの形状を検証し、`IssueSnapshot`へ変換する。
    形状が不正な場合は例外を送出せず`None`を返す。
    """
    if not isinstance(raw, dict):
        return None

    number = raw.get("number")
    if isinstance(number, bool) or not isinstance(number, int):
        return None

    state = raw.get("state")
    if state not in ("open", "closed"):
        return None

    labels_raw = raw.get("labels")
    if not isinstance(labels_raw, list):
        return None
    names: list[str] = []
    for entry in labels_raw:
        if not isinstance(entry, dict):
            return None
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            return None
        names.append(name)

    body = raw.get("body")
    if body is None:
        body = ""
    if not isinstance(body, str):
        return None

    updated_at = raw.get("updated_at")
    if not isinstance(updated_at, str) or not updated_at:
        return None

    title = raw.get("title")
    if not isinstance(title, str):
        return None

    html_url = raw.get("html_url")
    if not isinstance(html_url, str) or not html_url:
        return None

    is_pull_request = raw.get("pull_request") is not None

    return IssueSnapshot(
        issue_number=number,
        is_open=(state == "open"),
        is_pull_request=is_pull_request,
        current_labels=tuple(names),
        issue_body=body,
        updated_at=updated_at,
        title=title,
        html_url=html_url,
    )


# ---------------------------------------------------------------------------
# 判定契約
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LauncherInput:
    trigger: str  # TriggerType.value
    added_label: Optional[str]  # issues:labeledで付与されたラベル名。workflow_dispatchではNone。
    snapshot: IssueSnapshot


@dataclass(frozen=True)
class LauncherClassification:
    decision: Decision
    reason_code: ReasonCode
    errors: tuple[dict[str, Optional[str]], ...] = ()
    fields: Optional[ExtractedTaskFields] = None

    def to_machine_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason_code": self.reason_code.value,
            "errors": list(self.errors),
        }

    def to_line(self) -> str:
        """既存のController App writer群と同じ、grep -oPで抽出しやすい
        `KEY=value`空白区切り形式(固定語彙・数値だけ、Issue本文等の未信頼
        フィールドは含めない)。"""
        return f"DECISION={self.decision.value} REASON_CODE={self.reason_code.value} ERROR_COUNT={len(self.errors)}"


def _outcome(
    decision: Decision, reason_code: ReasonCode, *,
    errors: tuple[dict[str, Optional[str]], ...] = (),
    fields: Optional[ExtractedTaskFields] = None,
) -> LauncherClassification:
    return LauncherClassification(decision=decision, reason_code=reason_code, errors=errors, fields=fields)


def _classify_inner(input_: LauncherInput) -> LauncherClassification:
    if not isinstance(input_, LauncherInput):
        raise TypeError(f"classify()にはLauncherInputを渡してください: got {type(input_).__name__}")

    snapshot = input_.snapshot

    # 1〜2. 入力/対象種別・適用対象の検査
    if snapshot.is_pull_request:
        return _outcome(Decision.NOT_APPLICABLE, ReasonCode.TARGET_IS_PULL_REQUEST)

    if input_.trigger == TriggerType.ISSUES_LABELED.value:
        if input_.added_label != AGENT_WORKING_LABEL:
            return _outcome(Decision.NOT_APPLICABLE, ReasonCode.LABEL_NOT_AGENT_WORKING)
    elif input_.trigger == TriggerType.WORKFLOW_DISPATCH.value:
        pass
    else:
        raise ValueError("未知のtriggerです。")

    # 3. Issue状態の検査
    if not snapshot.is_open:
        return _outcome(Decision.NOT_APPLICABLE, ReasonCode.ISSUE_CLOSED)

    labels = set(snapshot.current_labels)
    if AGENT_WORKING_LABEL not in labels:
        return _outcome(Decision.WOULD_BLOCK_STATE, ReasonCode.AGENT_WORKING_LABEL_MISSING)
    if AGENT_READY_LABEL in labels:
        return _outcome(Decision.WOULD_BLOCK_STATE, ReasonCode.AGENT_READY_STILL_PRESENT)
    if AGENT_BLOCKED_LABEL in labels:
        return _outcome(Decision.WOULD_BLOCK_STATE, ReasonCode.AGENT_BLOCKED_PRESENT)
    other_conflicts = (labels & CONFLICTING_STATE_LABELS) - {AGENT_WORKING_LABEL}
    if other_conflicts:
        return _outcome(Decision.WOULD_BLOCK_STATE, ReasonCode.STATE_LABEL_CONFLICT)

    # 4. Issue契約の検査(既存preflight validatorのみを使う。第二validatorは作らない)
    validation = validate_issue_body(snapshot.issue_body)

    if validation.status is ValidationStatus.INTERNAL_ERROR:
        return _outcome(Decision.INTERNAL_ERROR, ReasonCode.PREFLIGHT_VALIDATOR_INTERNAL_ERROR)

    if validation.status is ValidationStatus.CONTRACT_VIOLATION:
        sanitized = tuple(_sanitize_validation_errors(validation.errors))
        return _outcome(Decision.WOULD_BLOCK_CONTRACT, ReasonCode.PREFLIGHT_CONTRACT_VIOLATION, errors=sanitized)

    # validation.status is PASS
    fields = extract_task_fields(snapshot.issue_body)
    if fields is None:
        # 契約上ここには到達しないはずだが(PASS済みは常に抽出できる)、
        # 防御的にfail-closedとする。
        return _outcome(Decision.INTERNAL_ERROR, ReasonCode.TASK_FIELD_EXTRACTION_FAILED)

    return _outcome(Decision.WOULD_LAUNCH, ReasonCode.LAUNCH_READY, fields=fields)


def classify(input_: LauncherInput) -> LauncherClassification:
    """`LauncherInput`から、Implementer起動可否のdry-run上の判定を計算する。

    GitHub API・Anthropic API・OpenAI API・その他の外部通信は一切行わない。
    どのような入力に対しても例外を送出せず、想定外の内部エラーは
    Decision.INTERNAL_ERROR として結果に包んで返す。
    """
    try:
        return _classify_inner(input_)
    except Exception as exc:  # noqa: BLE001 - 内部エラーとして状態化するために意図的に広く捕捉する
        return _outcome(
            Decision.INTERNAL_ERROR, ReasonCode.INTERNAL_ERROR,
            errors=({"code": "INTERNAL_ERROR", "section": None,
                     "message": f"launcher内部で予期しない例外が発生しました({type(exc).__name__})。"},),
        )


# ---------------------------------------------------------------------------
# 再取得整合性検査(task bundle出力確定前)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConsistencyCheckResult:
    ok: bool
    reason_code: Optional[ReasonCode]
    changed_fields: tuple[str, ...] = ()

    def to_line(self) -> str:
        parts = [f"OK={'true' if self.ok else 'false'}"]
        parts.append(f"REASON_CODE={self.reason_code.value if self.reason_code else 'NONE'}")
        parts.append(f"CHANGED_FIELDS={','.join(self.changed_fields) if self.changed_fields else 'NONE'}")
        return " ".join(parts)


def check_source_unchanged(before: IssueSnapshot, after: IssueSnapshot) -> ConsistencyCheckResult:
    """task bundle出力確定直前に再取得したIssueが、判定時点の取得結果と
    一致しているかを比較する。number・state・labels・updated_at・body
    sha256のいずれかが変化していれば、`SOURCE_CHANGED_BEFORE_OUTPUT`と
    する(古いtask bundleを発行しない)。
    """
    changed: list[str] = []
    if before.issue_number != after.issue_number:
        changed.append("issue_number")
    if before.is_open != after.is_open:
        changed.append("state")
    if frozenset(before.current_labels) != frozenset(after.current_labels):
        changed.append("labels")
    if before.updated_at != after.updated_at:
        changed.append("updated_at")
    if before.body_sha256 != after.body_sha256:
        changed.append("body_sha256")

    if changed:
        return ConsistencyCheckResult(False, ReasonCode.SOURCE_CHANGED_BEFORE_OUTPUT, tuple(changed))
    return ConsistencyCheckResult(True, None, ())


# ---------------------------------------------------------------------------
# task bundle生成(決定的なJSON)
# ---------------------------------------------------------------------------

def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    """task bundleを、常にbyte単位で同一になる形式でシリアライズする
    (キー順序・separatorsを固定し、生成時刻・run ID等の非決定値は
    呼び出し側が一切含めないことを前提とする)。
    """
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def build_task_bundle(
    *,
    repository: str,
    snapshot: IssueSnapshot,
    fields: ExtractedTaskFields,
    generated_from_main_sha: str,
    launcher_decision: str,
    launcher_reason_code: str,
) -> dict[str, Any]:
    """決定的なtask bundle(dict)を組み立てる。生成時刻・run ID・ランダム値は
    一切含めない。ラベル配列は昇順ソートで決定的な順序へ正規化する。
    """
    return {
        "schema_version": TASK_BUNDLE_SCHEMA_VERSION,
        "source": {
            "repository": repository,
            "issue_number": snapshot.issue_number,
            "issue_url": snapshot.html_url,
            "issue_title": snapshot.title,
            "issue_state": "open" if snapshot.is_open else "closed",
            "issue_updated_at": snapshot.updated_at,
            "issue_body_sha256": snapshot.body_sha256,
            "labels": sorted(snapshot.current_labels),
        },
        "task": fields.to_dict(),
        "generated_from_main_sha": generated_from_main_sha,
        "launcher_decision": launcher_decision,
        "launcher_reason_code": launcher_reason_code,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_json_file(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_event_payload(path: str) -> dict:
    raw = _load_json_file(path)
    if not isinstance(raw, dict):
        raise ValueError("event payloadがオブジェクトではありません。")
    return raw


def _cmd_classify(args: argparse.Namespace) -> int:
    try:
        issue_raw = _load_json_file(args.issue_response_file)
        snapshot = parse_issue_snapshot(issue_raw)
        if snapshot is None:
            raise ValueError("issue-response-fileの形状が不正です。")

        if args.expected_issue_number is not None and snapshot.issue_number != args.expected_issue_number:
            raise ValueError("取得したIssue番号がexpected-issue-numberと一致しません。")

        added_label: Optional[str] = None
        if args.trigger == TriggerType.ISSUES_LABELED.value:
            event_payload = _load_event_payload(args.event_json_path)
            label_obj = event_payload.get("label")
            if not isinstance(label_obj, dict) or not isinstance(label_obj.get("name"), str):
                raise ValueError("labeledイベントにlabel.nameがありません。")
            added_label = label_obj["name"]

        launcher_input = LauncherInput(trigger=args.trigger, added_label=added_label, snapshot=snapshot)
        outcome = classify(launcher_input)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        # exc自体のstr()/repr()は埋め込まない(入力ファイルの内容の断片を
        # 含み得るため)。例外の型名だけを安全な情報として使う。
        outcome = _outcome(
            Decision.INTERNAL_ERROR, ReasonCode.RESPONSE_VALIDATION_FAILED,
            errors=({"code": "INTERNAL_ERROR", "section": None,
                     "message": f"classify入力の準備に失敗しました({type(exc).__name__})。"},),
        )

    machine_dict = outcome.to_machine_dict()
    print(outcome.to_line())
    # errorsはsanitize済み(validate_issue_bodyのerrorsをclassify()内部で
    # _sanitize_validation_errors()に通した後の固定安全文言)であり、Issue
    # 本文由来の引用を含まないため、ログへ出力してよい。
    print(json.dumps(machine_dict, ensure_ascii=False))

    if args.machine_json_path:
        Path(args.machine_json_path).write_text(
            json.dumps(machine_dict, ensure_ascii=False, indent=2), encoding="utf-8",
        )
    if args.fields_json_path:
        if outcome.decision is Decision.WOULD_LAUNCH and outcome.fields is not None:
            Path(args.fields_json_path).write_text(
                json.dumps(outcome.fields.to_dict(), ensure_ascii=False), encoding="utf-8",
            )

    return 0 if outcome.decision is not Decision.INTERNAL_ERROR else 1


def _cmd_check_recheck(args: argparse.Namespace) -> int:
    try:
        before_raw = _load_json_file(args.before_response_file)
        after_raw = _load_json_file(args.after_response_file)
        before = parse_issue_snapshot(before_raw)
        after = parse_issue_snapshot(after_raw)
        if before is None or after is None:
            result = ConsistencyCheckResult(False, ReasonCode.RESPONSE_VALIDATION_FAILED)
        else:
            result = check_source_unchanged(before, after)
    except (OSError, json.JSONDecodeError):
        result = ConsistencyCheckResult(False, ReasonCode.INTERNAL_ERROR)

    print(result.to_line())
    return 0 if result.ok else 1


def _cmd_build_bundle(args: argparse.Namespace) -> int:
    try:
        after_raw = _load_json_file(args.after_response_file)
        snapshot = parse_issue_snapshot(after_raw)
        fields_raw = _load_json_file(args.fields_json_path)
        if snapshot is None or not isinstance(fields_raw, dict):
            print("OK=false REASON_CODE=RESPONSE_VALIDATION_FAILED")
            return 1

        acceptance_criteria = fields_raw.get("acceptance_criteria")
        if not isinstance(acceptance_criteria, list):
            print("OK=false REASON_CODE=RESPONSE_VALIDATION_FAILED")
            return 1

        fields = ExtractedTaskFields(
            management_id=fields_raw["management_id"],
            current_problem=fields_raw["current_problem"],
            cause_hypotheses=fields_raw["cause_hypotheses"],
            purpose=fields_raw["purpose"],
            expected_behavior=fields_raw["expected_behavior"],
            non_goals=fields_raw["non_goals"],
            acceptance_criteria=tuple(
                AcceptanceCriterionField(id=ac["id"], description=ac["description"])
                for ac in acceptance_criteria
            ),
            test_perspectives=tuple(fields_raw["test_perspectives"]),
            risks=tuple(fields_raw["risks"]),
            human_confirmation_items=fields_raw["human_confirmation_items"],
            change_classification=dict(fields_raw["change_classification"]),
            reference_materials=fields_raw["reference_materials"],
        )

        bundle = build_task_bundle(
            repository=args.repository,
            snapshot=snapshot,
            fields=fields,
            generated_from_main_sha=args.generated_from_main_sha,
            launcher_decision=args.launcher_decision,
            launcher_reason_code=args.launcher_reason_code,
        )
        Path(args.output_path).write_bytes(canonical_json_bytes(bundle))
        digest = hashlib.sha256(canonical_json_bytes(bundle)).hexdigest()
        print(f"OK=true REASON_CODE=NONE BUNDLE_SHA256={digest}")
        return 0
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        print("OK=false REASON_CODE=INTERNAL_ERROR")
        return 1


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUTO-001-06-01 Implementer Launcher read-only dry-run CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate_num = sub.add_parser(
        "validate-issue-number",
        help="workflow_dispatch issue_number入力のfail-closed検証(正の整数のみ許可)",
    )
    p_validate_num.add_argument("value")

    p_classify = sub.add_parser("classify", help="起動可否のdecision判定")
    p_classify.add_argument("--trigger", required=True, choices=[t.value for t in TriggerType])
    p_classify.add_argument("--issue-response-file", required=True)
    p_classify.add_argument("--event-json-path", default=None)
    p_classify.add_argument("--expected-issue-number", type=int, default=None)
    p_classify.add_argument("--machine-json-path", default=None)
    p_classify.add_argument("--fields-json-path", default=None)

    p_recheck = sub.add_parser("check-recheck", help="出力確定前の再取得整合性検査")
    p_recheck.add_argument("--before-response-file", required=True)
    p_recheck.add_argument("--after-response-file", required=True)

    p_bundle = sub.add_parser("build-bundle", help="決定的なtask bundle JSONを生成")
    p_bundle.add_argument("--after-response-file", required=True)
    p_bundle.add_argument("--fields-json-path", required=True)
    p_bundle.add_argument("--repository", required=True)
    p_bundle.add_argument("--generated-from-main-sha", required=True)
    p_bundle.add_argument("--launcher-decision", required=True)
    p_bundle.add_argument("--launcher-reason-code", required=True)
    p_bundle.add_argument("--output-path", required=True)

    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    if args.command == "validate-issue-number":
        if parse_positive_integer_strict(args.value) is None:
            print(f"OK=false REASON_CODE={ReasonCode.INVALID_ISSUE_NUMBER.value}")
            return 1
        print("OK=true REASON_CODE=NONE")
        return 0
    if args.command == "classify":
        return _cmd_classify(args)
    if args.command == "check-recheck":
        return _cmd_check_recheck(args)
    if args.command == "build-bundle":
        return _cmd_build_bundle(args)
    return 2  # pragma: no cover - argparseがrequired=Trueで防ぐ


if __name__ == "__main__":
    raise SystemExit(main())
