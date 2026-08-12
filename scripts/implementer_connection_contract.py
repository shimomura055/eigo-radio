"""AUTO-001-06-02-02: 半自動Implementer(MVP-1.5)接続契約。

task bundle(AUTO-001-TASK-BUNDLE-V1、scripts.implementer_launcher)を人間経由で
Claude Codeへ渡し、Claude Codeが「入力検査+実装計画」だけを返す半自動MVP-1.5の
ための、2つの新しいJSON契約(execution envelope / plan result)と、それらを
検証するための手書きバリデータを提供する。

このモジュールはscripts.implementer_launcherを一切import/変更しない
(役割分担: Launcherはtask bundleの生成、本モジュールはtask bundle受け渡し後の
envelope/plan result契約を担当する)。task bundle自体のフィールド・決定性・
schema versionはこのモジュールの検証対象としてのみ参照する。

このモジュールはClaude Codeを起動しない。GitHubへの読み書きを一切行わない。
ファイル・git操作は一切行わない(検証対象のdictを受け取り、結果を返すだけ)。

JSON Schemaの全機能を実装するものではない(正式なJSON Schemaライブラリ
(`jsonschema`等)は`requirements-ci.txt`に存在せず、本タスクでも追加しない)。
実装しているのは、`docs/automation/schemas/implementer_execution_envelope.
schema.json`および`implementer_plan_result.schema.json`が実際に使用している
サブセットだけである: required / type / enum・const / pattern / minimum・
maximum / minLength / minItems / uniqueItems / additionalProperties(全field
required構成のため「未知fieldの拒否」として実装) / cross-field / RFC3339 UTC
(Z終端のみ)。対応していない主なJSON Schema機能: `$ref`、`oneOf`/`anyOf`、
`patternProperties`、`prefixItems`、`contains`、`format`の一般的なvalidation
(date-time以外)、数値の`multipleOf`、文字列の`maxLength`。
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatchcase
from typing import Any, Optional

__all__ = [
    "EXECUTION_ENVELOPE_SCHEMA_VERSION",
    "PLAN_RESULT_SCHEMA_VERSION",
    "TASK_BUNDLE_SCHEMA_VERSION_CONST",
    "PROHIBITED_OPERATIONS",
    "CHANGED_FILE_CHANGE_TYPES",
    "SERVICE_SPEC_IMPACT_VALUES",
    "ConnectionDecision",
    "ValidationResult",
    "build_logical_task_key",
    "validate_envelope",
    "validate_plan_result",
]


# ---------------------------------------------------------------------------
# 固定契約値
# ---------------------------------------------------------------------------

EXECUTION_ENVELOPE_SCHEMA_VERSION = "1.0.0"
PLAN_RESULT_SCHEMA_VERSION = "1.0.0"

# scripts.implementer_launcher.TASK_BUNDLE_SCHEMA_VERSIONと同じ値。
# importで結合させず、テスト側(auto001_test_implementer_connection_contract.py)
# で両者が一致することを検証する(本モジュールをLauncherから独立させるため)。
TASK_BUNDLE_SCHEMA_VERSION_CONST = "AUTO-001-TASK-BUNDLE-V1"

TASK_BUNDLE_FILE_CONST = "task_bundle.json"
STOP_POINT_CONST = "PLAN_ONLY"
EXPECTED_OUTPUT_CONST = "PLAN_RESULT_JSON"

# 辞書順(Pythonの文字列比較順)で固定。envelope.prohibited_operationsは、
# この集合の部分集合を、この順序(辞書順)で列挙することを要求する。
PROHIBITED_OPERATIONS = (
    "AMEND",
    "BRANCH_CREATE",
    "BRANCH_DELETE",
    "COMMENT_WRITE",
    "CREDENTIAL_MODIFICATION",
    "FILE_WRITE",
    "FORCE_PUSH",
    "GIT_COMMIT",
    "GIT_PUSH",
    "GIT_STAGE",
    "ISSUE_WRITE",
    "LABEL_WRITE",
    "MAIN_DIRECT_CHANGE",
    "MERGE",
    "PR_CREATE",
    "REBASE",
    "SECRET_ACCESS",
    "WORKFLOW_DISPATCH",
    "WORKTREE_CREATE",
    "WORKTREE_DELETE",
)
_PROHIBITED_OPERATIONS_SET = frozenset(PROHIBITED_OPERATIONS)

# claude_implementation_report.schema.json の changed_files と型を一致させる。
CHANGED_FILE_CHANGE_TYPES = ("added", "modified", "deleted", "renamed")
SERVICE_SPEC_IMPACT_VALUES = ("NONE", "POSSIBLE", "YES", "UNKNOWN")

_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX40_RE = re.compile(r"^[0-9a-f]{40}$")
_REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
_EXECUTION_ID_RE = re.compile(r"^exec_([0-9a-f]{12})_a([1-9][0-9]*)_([A-Za-z0-9]{8,32})$")
# RFC3339のうち、UTC(Z終端)かつ小数秒任意という限定サブセットのみを受理する。
_RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

_TIMEOUT_SECONDS_MIN = 1
_TIMEOUT_SECONDS_MAX = 86400


# ---------------------------------------------------------------------------
# decision / validation result契約
# ---------------------------------------------------------------------------

class ConnectionDecision(str, Enum):
    """接続層のdecision。LauncherのDecision(WOULD_LAUNCH等)、レビューの
    overall_verdict(PASS等)とは別語彙であり、文字列も意味も重複しない。

    AUTO-001-06-02-01の監査ではREJECTED_DUPLICATEも候補として提示したが、
    AUTO-001-06-02-02の実装指示により、v1では予約値としても追加しない
    (Launcherの WOULD_BLOCK_DUPLICATE とは異なる方針)。
    """

    ACCEPTED = "ACCEPTED"
    REJECTED_SCHEMA = "REJECTED_SCHEMA"
    REJECTED_HASH = "REJECTED_HASH"
    REJECTED_SOURCE = "REJECTED_SOURCE"
    REJECTED_POLICY = "REJECTED_POLICY"


@dataclass(frozen=True)
class ValidationResult:
    """envelope/plan resultの検証結果。拒否系はこの型でだけ表現し、
    plan result自体を拒否系の形へ加工することはしない。
    """

    valid: bool
    connection_decision: str
    error_codes: tuple[str, ...]
    error_messages: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "connection_decision": self.connection_decision,
            "error_codes": list(self.error_codes),
            "error_messages": list(self.error_messages),
        }


def _accepted() -> ValidationResult:
    return ValidationResult(
        valid=True,
        connection_decision=ConnectionDecision.ACCEPTED.value,
        error_codes=(),
        error_messages=(),
    )


def _rejected(decision: ConnectionDecision, errors: list[tuple[str, str]]) -> ValidationResult:
    return ValidationResult(
        valid=False,
        connection_decision=decision.value,
        error_codes=tuple(code for code, _ in errors),
        error_messages=tuple(message for _, message in errors),
    )


# ---------------------------------------------------------------------------
# logical_task_key
# ---------------------------------------------------------------------------

def _canonical_json_bytes(payload: Any) -> bytes:
    """scripts.implementer_launcher.canonical_json_bytes()と同一の直列化規則
    (ensure_ascii=False, sort_keys=True, separators=(",", ":")、UTF-8、末尾
    改行なし)を、list入力にもそのまま使える形でこのモジュール内に複製する。
    Launcher本体をimportせず、このモジュールを独立させるための意図的な複製
    (4行のみ)であり、両者が同一規則であることはテストで確認する。
    """
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def build_logical_task_key(
    *, repository: str, issue_number: int, management_id: str, task_bundle_sha256: str,
) -> str:
    """repository, issue_number, management_id, task_bundle_sha256から、
    決定的なlogical_task_key(sha256 hex, 64桁小文字)を生成する。
    """
    payload = [repository, issue_number, management_id, task_bundle_sha256]
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


# ---------------------------------------------------------------------------
# 汎用フィールドチェックヘルパ(手書きJSON Schemaサブセット)
# ---------------------------------------------------------------------------

def _check_required_and_unknown(
    data: dict[str, Any], required_fields: tuple[str, ...], errors: list[tuple[str, str]],
) -> None:
    for field in required_fields:
        if field not in data:
            errors.append(("SCHEMA_REQUIRED_FIELD_MISSING", f"必須field '{field}' がありません。"))
    unknown = sorted(set(data.keys()) - set(required_fields))
    for field in unknown:
        errors.append(("SCHEMA_UNKNOWN_FIELD", f"未知のfield '{field}' が含まれています(additionalProperties: false)。"))


def _check_string(
    data: dict[str, Any], field: str, errors: list[tuple[str, str]],
    *, pattern: Optional[re.Pattern[str]] = None, const: Optional[str] = None,
    enum: Optional[tuple[str, ...]] = None, min_length: Optional[int] = None,
) -> Optional[str]:
    if field not in data:
        return None
    value = data[field]
    if not isinstance(value, str):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"'{field}' はstring型である必要があります。"))
        return None
    if const is not None and value != const:
        errors.append(("SCHEMA_CONST_MISMATCH", f"'{field}' は固定値 '{const}' である必要があります(実際: '{value}')。"))
        return None
    if enum is not None and value not in enum:
        errors.append(("SCHEMA_ENUM_MISMATCH", f"'{field}' は許可された値ではありません(実際: '{value}')。"))
        return None
    if min_length is not None and len(value) < min_length:
        errors.append(("SCHEMA_MIN_LENGTH_VIOLATION", f"'{field}' はminLength {min_length} 以上である必要があります。"))
        return None
    if pattern is not None and not pattern.match(value):
        errors.append(("SCHEMA_PATTERN_MISMATCH", f"'{field}' の形式が不正です(実際: '{value}')。"))
        return None
    return value


def _check_integer(
    data: dict[str, Any], field: str, errors: list[tuple[str, str]],
    *, minimum: Optional[int] = None, maximum: Optional[int] = None,
) -> Optional[int]:
    if field not in data:
        return None
    value = data[field]
    # bool は int のサブクラスのため明示的に除外する。
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"'{field}' はinteger型である必要があります。"))
        return None
    if minimum is not None and value < minimum:
        errors.append(("SCHEMA_MINIMUM_VIOLATION", f"'{field}' はminimum {minimum} 以上である必要があります(実際: {value})。"))
        return None
    if maximum is not None and value > maximum:
        errors.append(("SCHEMA_MAXIMUM_VIOLATION", f"'{field}' はmaximum {maximum} 以下である必要があります(実際: {value})。"))
        return None
    return value


def _check_bool_const(
    data: dict[str, Any], field: str, const: bool, errors: list[tuple[str, str]],
) -> None:
    if field not in data:
        return
    value = data[field]
    if not isinstance(value, bool) or value is not const:
        errors.append(("SCHEMA_CONST_MISMATCH", f"'{field}' は固定値 {const} である必要があります。"))


def _check_string_array(
    data: dict[str, Any], field: str, errors: list[tuple[str, str]],
    *, min_items: Optional[int] = None, unique: bool = False,
) -> Optional[list[str]]:
    if field not in data:
        return None
    value = data[field]
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"'{field}' はstringのarrayである必要があります。"))
        return None
    if min_items is not None and len(value) < min_items:
        errors.append(("SCHEMA_MIN_ITEMS_VIOLATION", f"'{field}' はminItems {min_items} 以上である必要があります。"))
        return None
    if unique and len(set(value)) != len(value):
        errors.append(("SCHEMA_UNIQUE_ITEMS_VIOLATION", f"'{field}' に重複した要素があります(uniqueItems: true)。"))
        return None
    return value


# ---------------------------------------------------------------------------
# execution envelope
# ---------------------------------------------------------------------------

_ENVELOPE_REQUIRED_FIELDS = (
    "schema_version",
    "logical_task_key",
    "execution_id",
    "attempt",
    "repository",
    "base_sha",
    "issue_number",
    "management_id",
    "task_bundle_schema_version",
    "task_bundle_sha256",
    "task_bundle_file",
    "prohibited_paths",
    "prohibited_operations",
    "timeout_seconds",
    "stop_point",
    "expected_output",
    "human_approval_required",
)


def _validate_envelope_schema(envelope: Any) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    if not isinstance(envelope, dict):
        return [("SCHEMA_TYPE_MISMATCH", "envelopeはobjectである必要があります。")]

    _check_required_and_unknown(envelope, _ENVELOPE_REQUIRED_FIELDS, errors)

    _check_string(envelope, "schema_version", errors, pattern=_SEMVER_RE)
    logical_task_key = _check_string(envelope, "logical_task_key", errors, pattern=_HEX64_RE)
    execution_id = _check_string(envelope, "execution_id", errors, pattern=_EXECUTION_ID_RE)
    attempt = _check_integer(envelope, "attempt", errors, minimum=1)
    _check_string(envelope, "repository", errors, pattern=_REPOSITORY_RE)
    _check_string(envelope, "base_sha", errors, pattern=_HEX40_RE)
    _check_integer(envelope, "issue_number", errors, minimum=1)
    _check_string(envelope, "management_id", errors, min_length=1)
    _check_string(envelope, "task_bundle_schema_version", errors, const=TASK_BUNDLE_SCHEMA_VERSION_CONST)
    _check_string(envelope, "task_bundle_sha256", errors, pattern=_HEX64_RE)
    _check_string(envelope, "task_bundle_file", errors, const=TASK_BUNDLE_FILE_CONST)

    prohibited_paths = _check_string_array(envelope, "prohibited_paths", errors, min_items=1, unique=True)

    prohibited_operations = envelope.get("prohibited_operations")
    if "prohibited_operations" in envelope:
        if not isinstance(prohibited_operations, list) or not all(
            isinstance(item, str) for item in prohibited_operations
        ):
            errors.append(("SCHEMA_TYPE_MISMATCH", "'prohibited_operations' はstringのarrayである必要があります。"))
        elif len(prohibited_operations) < 1:
            errors.append(("SCHEMA_MIN_ITEMS_VIOLATION", "'prohibited_operations' はminItems 1以上である必要があります。"))
        elif len(set(prohibited_operations)) != len(prohibited_operations):
            errors.append(("SCHEMA_UNIQUE_ITEMS_VIOLATION", "'prohibited_operations' に重複した要素があります。"))
        else:
            unknown_ops = sorted(set(prohibited_operations) - _PROHIBITED_OPERATIONS_SET)
            if unknown_ops:
                errors.append(("SCHEMA_ENUM_MISMATCH", f"'prohibited_operations' に未知の値があります: {unknown_ops}。"))
            elif list(prohibited_operations) != sorted(prohibited_operations):
                errors.append(("SCHEMA_OPERATIONS_ORDER_VIOLATION", "'prohibited_operations' は辞書順で並んでいる必要があります。"))

    _check_integer(envelope, "timeout_seconds", errors, minimum=_TIMEOUT_SECONDS_MIN, maximum=_TIMEOUT_SECONDS_MAX)
    _check_string(envelope, "stop_point", errors, const=STOP_POINT_CONST)
    _check_string(envelope, "expected_output", errors, const=EXPECTED_OUTPUT_CONST)
    _check_bool_const(envelope, "human_approval_required", True, errors)

    # cross-field(envelope自身の内部整合性): execution_idの構造がlogical_task_key
    # /attemptと矛盾していないか。形式自体が不正な場合は既にerrorsへ積まれて
    # いるため、ここでは形式が有効だった場合のみ追加検査する。
    if execution_id is not None and logical_task_key is not None:
        match = _EXECUTION_ID_RE.match(execution_id)
        assert match is not None  # _check_stringのpatternで既に確認済み
        key_prefix, attempt_in_id, _suffix = match.groups()
        if key_prefix != logical_task_key[:12]:
            errors.append((
                "SCHEMA_EXECUTION_ID_LOGICAL_KEY_MISMATCH",
                "execution_idの先頭12文字がlogical_task_keyの先頭12文字と一致しません。",
            ))
        if attempt is not None and int(attempt_in_id) != attempt:
            errors.append((
                "SCHEMA_EXECUTION_ID_ATTEMPT_MISMATCH",
                "execution_idに埋め込まれたattempt番号がattempt fieldと一致しません。",
            ))

    return errors


def _check_envelope_source(envelope: dict[str, Any], task_bundle: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    try:
        bundle_source = task_bundle["source"]
        bundle_task = task_bundle["task"]
        bundle_schema_version = task_bundle["schema_version"]
    except (KeyError, TypeError):
        return [("SOURCE_TASK_BUNDLE_SHAPE_INVALID", "task bundleの形状が不正です(source/task/schema_versionが取得できません)。")]

    if envelope.get("repository") != bundle_source.get("repository"):
        errors.append(("SOURCE_REPOSITORY_MISMATCH", "envelope.repositoryがtask bundle.source.repositoryと一致しません。"))
    if envelope.get("issue_number") != bundle_source.get("issue_number"):
        errors.append(("SOURCE_ISSUE_NUMBER_MISMATCH", "envelope.issue_numberがtask bundle.source.issue_numberと一致しません。"))
    if envelope.get("management_id") != bundle_task.get("management_id"):
        errors.append(("SOURCE_MANAGEMENT_ID_MISMATCH", "envelope.management_idがtask bundle.task.management_idと一致しません。"))
    if envelope.get("task_bundle_schema_version") != bundle_schema_version:
        errors.append(("SOURCE_SCHEMA_VERSION_MISMATCH", "envelope.task_bundle_schema_versionがtask bundle.schema_versionと一致しません。"))

    if not errors:
        expected_key = build_logical_task_key(
            repository=bundle_source.get("repository"),
            issue_number=bundle_source.get("issue_number"),
            management_id=bundle_task.get("management_id"),
            task_bundle_sha256=envelope.get("task_bundle_sha256"),
        )
        if envelope.get("logical_task_key") != expected_key:
            errors.append((
                "SOURCE_LOGICAL_TASK_KEY_MISMATCH",
                "envelope.logical_task_keyが、実際のtask bundle内容から再計算した値と一致しません。",
            ))
    return errors


def _check_envelope_hash(
    envelope: dict[str, Any], task_bundle_raw_bytes: bytes, task_bundle: dict[str, Any],
) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    actual_sha256 = hashlib.sha256(task_bundle_raw_bytes).hexdigest()
    if envelope.get("task_bundle_sha256") != actual_sha256:
        errors.append((
            "HASH_TASK_BUNDLE_BYTES_MISMATCH",
            "envelope.task_bundle_sha256が、実際のtask bundleファイルのbyte列から計算したSHA-256と一致しません。",
        ))
    return errors


def validate_envelope(
    envelope: Any, *, task_bundle_raw_bytes: bytes, task_bundle: Any,
) -> ValidationResult:
    """execution envelopeを、(1)単体schema、(2)task bundleとのsource一致、
    (3)task bundleとのhash一致、の順にfail-closedで検証する。

    優先順位: SCHEMA > SOURCE > HASH。envelope自体が自己矛盾している場合は
    task bundleとの突き合わせを行わない(先に直しようがないため)。
    """
    schema_errors = _validate_envelope_schema(envelope)
    if schema_errors:
        return _rejected(ConnectionDecision.REJECTED_SCHEMA, schema_errors)

    if not isinstance(task_bundle, dict):
        return _rejected(
            ConnectionDecision.REJECTED_SOURCE,
            [("SOURCE_TASK_BUNDLE_SHAPE_INVALID", "task bundleがobjectではありません。")],
        )

    source_errors = _check_envelope_source(envelope, task_bundle)
    if source_errors:
        return _rejected(ConnectionDecision.REJECTED_SOURCE, source_errors)

    hash_errors = _check_envelope_hash(envelope, task_bundle_raw_bytes, task_bundle)
    if hash_errors:
        return _rejected(ConnectionDecision.REJECTED_HASH, hash_errors)

    return _accepted()


# ---------------------------------------------------------------------------
# plan result
# ---------------------------------------------------------------------------

_PLAN_RESULT_REQUIRED_FIELDS = (
    "schema_version",
    "execution_id",
    "attempt",
    "logical_task_key",
    "management_id",
    "input_task_bundle_sha256",
    "input_base_sha",
    "connection_decision",
    "execution_status",
    "next_action",
    "summary",
    "current_problem_understanding",
    "implementation_plan",
    "proposed_changed_files",
    "proposed_test_plan",
    "prohibited_change_detected",
    "missing_information",
    "unresolved_items",
    "risks",
    "human_confirmation_items",
    "generated_at",
    "self_reported",
)


def _validate_changed_file_entry(entry: Any, index: int, errors: list[tuple[str, str]]) -> Optional[str]:
    if not isinstance(entry, dict):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"proposed_changed_files[{index}] はobjectである必要があります。"))
        return None
    required = ("path", "change_type", "purpose", "service_spec_impact")
    for field in required:
        if field not in entry:
            errors.append(("SCHEMA_REQUIRED_FIELD_MISSING", f"proposed_changed_files[{index}].{field} がありません。"))
    unknown = sorted(set(entry.keys()) - set(required))
    for field in unknown:
        errors.append(("SCHEMA_UNKNOWN_FIELD", f"proposed_changed_files[{index}] に未知のfield '{field}' があります。"))

    path = entry.get("path")
    if "path" in entry and (not isinstance(path, str) or len(path) < 1):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"proposed_changed_files[{index}].path はnon-empty stringである必要があります。"))
        path = None
    change_type = entry.get("change_type")
    if "change_type" in entry and change_type not in CHANGED_FILE_CHANGE_TYPES:
        errors.append(("SCHEMA_ENUM_MISMATCH", f"proposed_changed_files[{index}].change_type が不正です。"))
    purpose = entry.get("purpose")
    if "purpose" in entry and (not isinstance(purpose, str) or len(purpose) < 1):
        errors.append(("SCHEMA_TYPE_MISMATCH", f"proposed_changed_files[{index}].purpose はnon-empty stringである必要があります。"))
    impact = entry.get("service_spec_impact")
    if "service_spec_impact" in entry and impact not in SERVICE_SPEC_IMPACT_VALUES:
        errors.append(("SCHEMA_ENUM_MISMATCH", f"proposed_changed_files[{index}].service_spec_impact が不正です。"))

    return path


def _validate_plan_result_schema(plan_result: Any) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    if not isinstance(plan_result, dict):
        return [("SCHEMA_TYPE_MISMATCH", "plan resultはobjectである必要があります。")]

    _check_required_and_unknown(plan_result, _PLAN_RESULT_REQUIRED_FIELDS, errors)

    _check_string(plan_result, "schema_version", errors, pattern=_SEMVER_RE)
    _check_string(plan_result, "execution_id", errors, pattern=_EXECUTION_ID_RE)
    _check_integer(plan_result, "attempt", errors, minimum=1)
    _check_string(plan_result, "logical_task_key", errors, pattern=_HEX64_RE)
    _check_string(plan_result, "management_id", errors, min_length=1)
    _check_string(plan_result, "input_task_bundle_sha256", errors, pattern=_HEX64_RE)
    _check_string(plan_result, "input_base_sha", errors, pattern=_HEX40_RE)
    _check_string(plan_result, "connection_decision", errors, const=ConnectionDecision.ACCEPTED.value)
    _check_string(plan_result, "execution_status", errors, const="PLAN_COMPLETED")
    _check_string(plan_result, "next_action", errors, const="HUMAN_APPROVAL_REQUIRED")
    _check_string(plan_result, "summary", errors, min_length=1)
    _check_string(plan_result, "current_problem_understanding", errors, min_length=1)

    implementation_plan = _check_string_array(plan_result, "implementation_plan", errors, min_items=1)

    if "proposed_changed_files" in plan_result:
        changed_files = plan_result["proposed_changed_files"]
        if not isinstance(changed_files, list):
            errors.append(("SCHEMA_TYPE_MISMATCH", "'proposed_changed_files' はarrayである必要があります。"))
        else:
            paths: list[str] = []
            for index, entry in enumerate(changed_files):
                path = _validate_changed_file_entry(entry, index, errors)
                if path is not None:
                    paths.append(path)
            if len(set(paths)) != len(paths):
                errors.append(("SCHEMA_CHANGED_FILES_DUPLICATE_PATH", "'proposed_changed_files' 内にpathの重複があります。"))

    _check_string_array(plan_result, "proposed_test_plan", errors, min_items=1)
    _check_bool_const(plan_result, "prohibited_change_detected", False, errors)
    _check_string_array(plan_result, "missing_information", errors)
    _check_string_array(plan_result, "unresolved_items", errors)
    _check_string_array(plan_result, "risks", errors)
    _check_string_array(plan_result, "human_confirmation_items", errors)
    _check_string(plan_result, "generated_at", errors, pattern=_RFC3339_UTC_RE)
    _check_bool_const(plan_result, "self_reported", True, errors)

    return errors


def _check_plan_result_source(plan_result: dict[str, Any], envelope: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    if plan_result.get("execution_id") != envelope.get("execution_id"):
        errors.append(("SOURCE_EXECUTION_ID_MISMATCH", "plan_result.execution_idがenvelope.execution_idと一致しません。"))
    if plan_result.get("attempt") != envelope.get("attempt"):
        errors.append(("SOURCE_ATTEMPT_MISMATCH", "plan_result.attemptがenvelope.attemptと一致しません。"))
    if plan_result.get("logical_task_key") != envelope.get("logical_task_key"):
        errors.append(("SOURCE_LOGICAL_TASK_KEY_MISMATCH", "plan_result.logical_task_keyがenvelope.logical_task_keyと一致しません。"))
    if plan_result.get("management_id") != envelope.get("management_id"):
        errors.append(("SOURCE_MANAGEMENT_ID_MISMATCH", "plan_result.management_idがenvelope.management_idと一致しません。"))
    return errors


def _check_plan_result_hash(plan_result: dict[str, Any], envelope: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    if plan_result.get("input_task_bundle_sha256") != envelope.get("task_bundle_sha256"):
        errors.append(("HASH_TASK_BUNDLE_ECHO_MISMATCH", "plan_result.input_task_bundle_sha256がenvelope.task_bundle_sha256と一致しません。"))
    if plan_result.get("input_base_sha") != envelope.get("base_sha"):
        errors.append(("HASH_BASE_SHA_ECHO_MISMATCH", "plan_result.input_base_shaがenvelope.base_shaと一致しません。"))
    return errors


def _normalize_path_separators(path: str) -> str:
    return path.replace("\\", "/")


def _has_path_traversal(normalized_path: str) -> bool:
    return ".." in normalized_path.split("/")


def _check_policy(plan_result: dict[str, Any], envelope: dict[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    prohibited_paths = envelope.get("prohibited_paths")
    if not isinstance(prohibited_paths, list):
        return errors
    normalized_patterns = [_normalize_path_separators(p) for p in prohibited_paths]

    changed_files = plan_result.get("proposed_changed_files")
    if not isinstance(changed_files, list):
        return errors

    for entry in changed_files:
        if not isinstance(entry, dict):
            continue
        raw_path = entry.get("path")
        if not isinstance(raw_path, str):
            continue
        normalized_path = _normalize_path_separators(raw_path)

        if _has_path_traversal(normalized_path):
            errors.append((
                "POLICY_PATH_TRAVERSAL",
                f"proposed_changed_files.path '{raw_path}' にパストラバーサル('..')が含まれています。",
            ))
            continue

        for pattern in normalized_patterns:
            if fnmatchcase(normalized_path, pattern):
                errors.append((
                    "POLICY_PROHIBITED_PATH_MATCH",
                    f"proposed_changed_files.path '{raw_path}' がprohibited_pathsのパターン '{pattern}' に一致します。",
                ))
                break

    return errors


def validate_plan_result(plan_result: Any, *, envelope: Any) -> ValidationResult:
    """plan resultを、(1)単体schema、(2)envelopeとのsource一致、(3)envelope
    とのhash一致(echo検査)、(4)prohibited_pathsに基づくpolicy検査、の順に
    fail-closedで検証する。優先順位: SCHEMA > SOURCE > HASH > POLICY。
    """
    schema_errors = _validate_plan_result_schema(plan_result)
    if schema_errors:
        return _rejected(ConnectionDecision.REJECTED_SCHEMA, schema_errors)

    if not isinstance(envelope, dict):
        return _rejected(
            ConnectionDecision.REJECTED_SOURCE,
            [("SOURCE_ENVELOPE_SHAPE_INVALID", "envelopeがobjectではありません。")],
        )

    source_errors = _check_plan_result_source(plan_result, envelope)
    if source_errors:
        return _rejected(ConnectionDecision.REJECTED_SOURCE, source_errors)

    hash_errors = _check_plan_result_hash(plan_result, envelope)
    if hash_errors:
        return _rejected(ConnectionDecision.REJECTED_HASH, hash_errors)

    policy_errors = _check_policy(plan_result, envelope)
    if policy_errors:
        return _rejected(ConnectionDecision.REJECTED_POLICY, policy_errors)

    return _accepted()
