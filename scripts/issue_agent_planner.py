"""Issueラベルtriggerに対する状態遷移planner(AUTO-001-05-02A)。

`agent:ready`ラベルイベント(またはworkflow_dispatchによる手動dry-run)を、
GitHub API・Anthropic API・その他の外部通信を一切呼び出さずに、正規化済みの
入力データだけから決定論的に判定するread-only dry-run基盤。

設計上の責務分離:

* `PlannerInput` / `plan()` -- GitHubのイベントpayload形状に依存しない、
  純粋で決定論的な状態遷移の核。外部I/Oを一切行わない。
* `normalize_github_event()` -- GitHub Actionsのevent payload(および
  workflow_dispatch用に別途取得したIssue情報)を`PlannerInput`へ変換する。
  ここで想定外・不足したデータを検出し、`PlannerInputError`を送出する。
* CLI (`main()`) -- ファイルパス経由でJSONを読み込み、上記2つを呼び出して
  結果を出力する。Issue本文はJSONの1フィールドとしてのみ扱われ、shell
  コマンドへ埋め込まれることはない。

このモジュール自体はGitHubへの書き込み(ラベル変更・コメント投稿・Issue編集・
branch作成・commit・push・PR作成)を一切行わない。

AUTO-001-05-02A-R1: Issue本文・タイトル・管理ID欄・受入条件欄は未信頼入力として
扱う。preflight validator(scripts/issue_preflight_validator.py)自身のエラー
メッセージは、契約違反の種類によっては入力値の一部を短く引用することがあるが
(既存validatorの公開契約は変更しない)、planner側の出力(stdout・機械向け
JSON・Job Summary・投稿予定コメント概要)には、その引用を一切含めない。
`_sanitize_validation_errors()`が、validatorのエラーコードごとに固定された
安全な文言へ変換したうえでのみ、結果へ含める。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from scripts.issue_preflight_validator import CANONICAL_HEADINGS, ValidationStatus, validate_issue_body

# ---------------------------------------------------------------------------
# 既知の状態ラベル(source of truth)
# ---------------------------------------------------------------------------

AGENT_READY_LABEL = "agent:ready"
AGENT_WORKING_LABEL = "agent:working"
AGENT_BLOCKED_LABEL = "agent:blocked"

KNOWN_STATE_LABELS: tuple[str, ...] = (
    "agent:ready",
    "agent:working",
    "agent:review",
    "agent:changes-required",
    "human:review-required",
    "human:approved",
    "agent:blocked",
    "agent:failed",
)

# agent:ready以外の既知状態ラベル。1件でも現在ラベルに含まれていれば競合とみなす。
CONFLICTING_STATE_LABELS = frozenset(KNOWN_STATE_LABELS) - {AGENT_READY_LABEL}


class TriggerType(str, Enum):
    ISSUES_LABELED = "issues:labeled"
    WORKFLOW_DISPATCH = "workflow_dispatch"


class Decision(str, Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    WOULD_START = "WOULD_START"
    WOULD_BLOCK_PREFLIGHT = "WOULD_BLOCK_PREFLIGHT"
    WOULD_BLOCK_STATE = "WOULD_BLOCK_STATE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class PlannerInputError(Exception):
    """正規化(normalize_github_event)に失敗した場合に送出する。呼び出し側はINTERNAL_ERRORとして扱う。"""


# ---------------------------------------------------------------------------
# preflightエラーの安全化(AUTO-001-05-02A-R1)
#
# validatorのエラーコードごとに固定された安全な文言だけをplanner出力へ含める。
# Issue本文由来の値(管理ID欄の実際の値、受入条件の実際の説明文、行内容の
# 引用等)は、validatorのエラーメッセージに含まれていてもここで完全に破棄する。
# 未知のエラーコード(将来validator側に追加された場合)も、汎用の安全な
# 文言へfallbackし、決して元のmessageをそのまま通過させない。
# ---------------------------------------------------------------------------

_SAFE_PREFLIGHT_ERROR_MESSAGES: dict[str, str] = {
    "MARKER_START_MISSING": "開始マーカー(AGENT_TASK_SPEC_START)が見つかりません。",
    "MARKER_START_DUPLICATE": "開始マーカーが複数回出現しています。1件だけにしてください。",
    "MARKER_END_MISSING": "終了マーカー(AGENT_TASK_SPEC_END)が見つかりません。",
    "MARKER_END_DUPLICATE": "終了マーカーが複数回出現しています。1件だけにしてください。",
    "MARKER_ORDER_INVALID": "終了マーカーが開始マーカーより前(または同じ位置)にあります。",
    "MISSING_HEADING": "必須の見出しが見つかりません。正式な12見出しを過不足なく記載してください。",
    "DUPLICATE_HEADING": "見出しが重複しています。各見出しは1回だけにしてください。",
    "HEADING_ORDER_INVALID": "見出しの順序が正式な順序と一致していません。",
    "MISSING_REQUIRED_CONTENT": (
        "必須セクションに実質的な内容が記載されていません"
        "(「なし」を許容しないセクションは実質的な内容が必須です)。"
    ),
    "INVALID_MANAGEMENT_ID": "管理IDを、指定された形式(例: AUTO-001-05-01)で1件だけ記載してください。",
    "AMBIGUOUS_MANAGEMENT_ID": "管理IDらしき記載が複数あり一意に判定できません。指定された形式で1件だけ記載してください。",
    "ACCEPTANCE_CRITERIA_MISSING": "受入条件が1件も見つかりません。`- [ ] AC-01: 説明`の形式で記載してください。",
    "ACCEPTANCE_CRITERION_FORMAT": "受入条件の記載形式が`- [ ] AC-01: 説明`と一致していません。",
    "ACCEPTANCE_CRITERION_DESCRIPTION_MISSING": "受入条件に実質的な説明が記載されていません。",
    "ACCEPTANCE_CRITERION_DUPLICATE_ID": "受入条件IDが重複しています。各IDは1件だけにしてください。",
    "ACCEPTANCE_CRITERION_SEQUENCE_INVALID": "受入条件IDはAC-01から1ずつの連番にしてください。",
    "INTERNAL_ERROR": "preflight validator自体が内部エラーを検出しました。",
}

_GENERIC_PREFLIGHT_FALLBACK_MESSAGE = "preflight契約違反が検出されました(詳細はこのdry-run出力には含まれません)。"

_CANONICAL_SECTION_NAMES = frozenset(CANONICAL_HEADINGS)


def _sanitize_validation_errors(errors) -> list[dict[str, Optional[str]]]:
    """validatorのValidationErrorの列を、Issue本文由来の値を一切含まない
    固定文言のdict列へ変換する。code・section(既知の見出し名の固定語彙のみ)
    だけは元の値を保持し、messageは常にこのモジュール内の固定文言に置き換える。
    """
    sanitized: list[dict[str, Optional[str]]] = []
    for e in errors:
        section = e.section if e.section in _CANONICAL_SECTION_NAMES else None
        sanitized.append({
            "code": e.code,
            "section": section,
            "message": _SAFE_PREFLIGHT_ERROR_MESSAGES.get(e.code, _GENERIC_PREFLIGHT_FALLBACK_MESSAGE),
        })
    return sanitized


# ---------------------------------------------------------------------------
# planner入力契約
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlannerInput:
    """GitHubのevent payload形状に依存しない、正規化済みのplanner入力。"""

    issue_number: int
    is_open: bool
    is_pull_request: bool
    trigger: str  # TriggerType.value
    added_label: Optional[str]  # issues:labeledイベントで付与されたラベル名。workflow_dispatchではNone。
    current_labels: tuple[str, ...]
    issue_body: str


# ---------------------------------------------------------------------------
# planner出力契約
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlannerResult:
    issue_number: Optional[int]
    decision: Decision
    applicable: bool
    preflight_valid: Optional[bool]
    current_labels: tuple[str, ...]
    planned_remove_labels: tuple[str, ...]
    planned_add_labels: tuple[str, ...]
    planned_comment: Optional[str]
    errors: list[dict] = field(default_factory=list)
    reason: str = ""

    def to_machine_dict(self) -> dict[str, Any]:
        return {
            "issue_number": self.issue_number,
            "decision": self.decision.value,
            "applicable": self.applicable,
            "preflight_valid": self.preflight_valid,
            "current_labels": list(self.current_labels),
            "planned_remove_labels": list(self.planned_remove_labels),
            "planned_add_labels": list(self.planned_add_labels),
            "planned_comment": self.planned_comment,
            "errors": list(self.errors),
            "reason": self.reason,
        }

    def to_human_text(self) -> str:
        lines = [
            f"[dry-run] Issue #{self.issue_number}",
            f"判定(decision): {self.decision.value}",
            f"判定理由コード: {self.reason}",
            f"対象内(applicable): {self.applicable}",
            f"現在の状態ラベル: {list(self.current_labels)}",
        ]
        if self.preflight_valid is None:
            lines.append("preflight判定: 未評価")
        else:
            lines.append(f"preflight合否: {'合格' if self.preflight_valid else '不合格'}")
        lines.append(
            f"本番で行う予定のラベル変更: 削除={list(self.planned_remove_labels)} "
            f"追加={list(self.planned_add_labels)}"
        )
        if self.planned_comment:
            lines.append(f"本番で投稿する予定のコメント: あり(契約違反{len(self.errors)}件の概要)")
        else:
            lines.append("本番で投稿する予定のコメント: なし")
        if self.decision is Decision.INTERNAL_ERROR and self.errors:
            for e in self.errors:
                lines.append(f"  内部エラー詳細: {e.get('message', e)}")
        lines.append("read-only dry-run: GitHub上のIssue・ラベル・コメント・branch・commit・PRは実際には変更していません。")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 決定論的コア: plan()
# ---------------------------------------------------------------------------

def _result(
    input_: Any,
    decision: Decision,
    *,
    applicable: bool,
    preflight_valid: Optional[bool] = None,
    planned_remove: tuple[str, ...] = (),
    planned_add: tuple[str, ...] = (),
    planned_comment: Optional[str] = None,
    errors: Optional[list[dict]] = None,
    reason: str,
) -> PlannerResult:
    current_labels = tuple(getattr(input_, "current_labels", ()) or ())
    return PlannerResult(
        issue_number=getattr(input_, "issue_number", None),
        decision=decision,
        applicable=applicable,
        preflight_valid=preflight_valid,
        current_labels=current_labels,
        planned_remove_labels=tuple(planned_remove),
        planned_add_labels=tuple(planned_add),
        planned_comment=planned_comment,
        errors=errors or [],
        reason=reason,
    )


def _build_preflight_violation_comment(sanitized_errors: list[dict[str, Optional[str]]]) -> str:
    """安全化済みのエラー(_sanitize_validation_errorsの出力)だけからコメント概要を組み立てる。
    validatorの元のto_human_text()は(Issue本文由来の引用を含み得るため)使わない。
    """
    lines = [
        "[dry-run] preflight不合格時にIssueへ投稿予定のコメント概要です。"
        "このStageでは実際には投稿していません。",
        "",
        f"不合格: {len(sanitized_errors)}件の契約違反が見つかりました。",
    ]
    for i, e in enumerate(sanitized_errors, start=1):
        where = f"[{e['section']}] " if e.get("section") else ""
        lines.append(f"  {i}. {where}{e['message']} (code={e['code']})")
    return "\n".join(lines)


def _plan_inner(input_: PlannerInput) -> PlannerResult:
    if not isinstance(input_, PlannerInput):
        raise TypeError(f"plan()にはPlannerInputを渡してください: got {type(input_).__name__}")

    # 1. Pull Requestは対象外(triggerに関わらず)
    if input_.is_pull_request:
        return _result(input_, Decision.NOT_APPLICABLE, applicable=False, reason="target_is_pull_request")

    # 2. trigger種別ごとの適用可否
    if input_.trigger == TriggerType.ISSUES_LABELED.value:
        if input_.added_label != AGENT_READY_LABEL:
            return _result(input_, Decision.NOT_APPLICABLE, applicable=False, reason="label_not_agent_ready")
    elif input_.trigger == TriggerType.WORKFLOW_DISPATCH.value:
        pass
    else:
        raise ValueError("未知のtriggerです。")

    # 3. 状態異常(安全側で開始不可)
    if not input_.is_open:
        return _result(input_, Decision.WOULD_BLOCK_STATE, applicable=True, reason="issue_closed")

    if AGENT_READY_LABEL not in input_.current_labels:
        return _result(input_, Decision.WOULD_BLOCK_STATE, applicable=True, reason="agent_ready_label_missing")

    conflicts = sorted(set(input_.current_labels) & CONFLICTING_STATE_LABELS)
    if conflicts:
        return _result(
            input_, Decision.WOULD_BLOCK_STATE, applicable=True,
            reason="conflicting_state_label",
            errors=[{"code": "CONFLICTING_STATE_LABEL", "message": f"競合する状態ラベルが既に存在します: {conflicts}"}],
        )

    # 4. preflight validation
    validation = validate_issue_body(input_.issue_body)

    if validation.status is ValidationStatus.PASS:
        return _result(
            input_, Decision.WOULD_START, applicable=True, preflight_valid=True,
            planned_remove=(AGENT_READY_LABEL,), planned_add=(AGENT_WORKING_LABEL,),
            reason="preflight_pass",
        )

    if validation.status is ValidationStatus.CONTRACT_VIOLATION:
        sanitized_errors = _sanitize_validation_errors(validation.errors)
        return _result(
            input_, Decision.WOULD_BLOCK_PREFLIGHT, applicable=True, preflight_valid=False,
            planned_remove=(AGENT_READY_LABEL,), planned_add=(AGENT_BLOCKED_LABEL,),
            planned_comment=_build_preflight_violation_comment(sanitized_errors),
            errors=sanitized_errors,
            reason="preflight_contract_violation",
        )

    # validation.status is ValidationStatus.INTERNAL_ERROR -- 契約違反ではなく
    # validator自体の故障。plannerとしても内部エラーとして区別する(risk4)。
    return _result(
        input_, Decision.INTERNAL_ERROR, applicable=True, preflight_valid=None,
        errors=_sanitize_validation_errors(validation.errors),
        reason="preflight_validator_internal_error",
    )


def plan(input_: PlannerInput) -> PlannerResult:
    """`PlannerInput`から、dry-run上の状態遷移決定を計算する。

    GitHub API・Anthropic API・OpenAI API・その他の外部通信は一切行わない。
    どのような入力に対しても例外を送出せず、想定外の内部エラーは
    Decision.INTERNAL_ERROR として結果に包んで返す。
    """
    try:
        return _plan_inner(input_)
    except Exception as exc:  # noqa: BLE001 - 内部エラーとして状態化するために意図的に広く捕捉する
        # 例外のstr()/repr()は埋め込まない(入力由来の値を含み得るため)。
        # 例外の型名だけは、planner自身のコードから決まる安全な情報である。
        return _result(
            input_, Decision.INTERNAL_ERROR, applicable=False,
            errors=[{
                "code": "INTERNAL_ERROR",
                "message": f"planner内部で予期しない例外が発生しました({type(exc).__name__})。",
            }],
            reason="internal_exception",
        )


# ---------------------------------------------------------------------------
# GitHub event payload -> PlannerInput への正規化
# ---------------------------------------------------------------------------

def _require_dict(value: Any, what: str) -> dict:
    if not isinstance(value, dict):
        raise PlannerInputError(f"{what}がオブジェクトではありません: {type(value).__name__}")
    return value


def _extract_issue_number(issue_obj: dict) -> int:
    number = issue_obj.get("number")
    if isinstance(number, bool) or not isinstance(number, int):
        raise PlannerInputError("issue.numberが整数ではありません。")
    return number


def _extract_is_open(issue_obj: dict) -> bool:
    state = issue_obj.get("state")
    if state not in ("open", "closed"):
        raise PlannerInputError("issue.stateがopen/closedのいずれでもありません。")
    return state == "open"


def _extract_current_labels(issue_obj: dict) -> tuple[str, ...]:
    labels_raw = issue_obj.get("labels")
    if not isinstance(labels_raw, list):
        raise PlannerInputError("issue.labelsがリストではありません。")
    names: list[str] = []
    for entry in labels_raw:
        if isinstance(entry, dict) and isinstance(entry.get("name"), str):
            names.append(entry["name"])
        elif isinstance(entry, str):
            names.append(entry)
        else:
            raise PlannerInputError("issue.labelsの要素形式が不正です。")
    return tuple(names)


def _extract_body(issue_obj: dict) -> str:
    body = issue_obj.get("body")
    if body is None:
        return ""
    if not isinstance(body, str):
        raise PlannerInputError(f"issue.bodyが文字列ではありません: {type(body).__name__}")
    return body


def normalize_github_event(
    *,
    trigger: str,
    event_payload: dict,
    issue_payload: Optional[dict] = None,
) -> PlannerInput:
    """GitHub Actionsのevent payloadを`PlannerInput`へ正規化する。

    trigger == "issues:labeled" の場合、`event_payload`はGitHubの`issues`
    イベントpayloadそのもの("action" / "issue" / "label"を含む)を想定する。

    trigger == "workflow_dispatch" の場合、`event_payload`はworkflow_dispatch
    イベントpayload、`issue_payload`は別途(read-only API呼び出しで)取得した
    対象Issueのオブジェクトを想定する。

    想定外・不足したデータがあれば`PlannerInputError`を送出する
    (呼び出し側はDecision.INTERNAL_ERRORとして扱うこと)。
    """
    event_payload = _require_dict(event_payload, "event_payload")

    if trigger == TriggerType.ISSUES_LABELED.value:
        action = event_payload.get("action")
        if action != "labeled":
            raise PlannerInputError("issues:labeled triggerなのに想定外のactionです。")
        label_obj = event_payload.get("label")
        if not isinstance(label_obj, dict) or not isinstance(label_obj.get("name"), str):
            raise PlannerInputError("labeledイベントにlabel.nameがありません。")
        added_label = label_obj["name"]
        issue_obj = _require_dict(event_payload.get("issue"), "event_payload.issue")
    elif trigger == TriggerType.WORKFLOW_DISPATCH.value:
        added_label = None
        issue_obj = _require_dict(issue_payload, "issue_payload")
    else:
        raise PlannerInputError("未知のtriggerです。")

    issue_number = _extract_issue_number(issue_obj)
    is_open = _extract_is_open(issue_obj)
    is_pull_request = issue_obj.get("pull_request") is not None
    current_labels = _extract_current_labels(issue_obj)
    body = _extract_body(issue_obj)

    return PlannerInput(
        issue_number=issue_number,
        is_open=is_open,
        is_pull_request=is_pull_request,
        trigger=trigger,
        added_label=added_label,
        current_labels=current_labels,
        issue_body=body,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_json_file(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _internal_error_result(message: str) -> PlannerResult:
    return PlannerResult(
        issue_number=None,
        decision=Decision.INTERNAL_ERROR,
        applicable=False,
        preflight_valid=None,
        current_labels=(),
        planned_remove_labels=(),
        planned_add_labels=(),
        planned_comment=None,
        errors=[{"code": "INTERNAL_ERROR", "message": message}],
        reason="cli_setup_error",
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="AUTO-001 Issue agent planner read-only dry-run CLI")
    parser.add_argument("--trigger", required=True, choices=[t.value for t in TriggerType])
    parser.add_argument("--event-json-path", required=True, help="GitHub event payload JSONファイルのパス")
    parser.add_argument("--issue-json-path", default=None, help="workflow_dispatch時のIssue情報JSONファイルのパス")
    parser.add_argument("--machine-json-path", default=None, help="機械可読な結果JSONの出力先パス")
    parser.add_argument("--summary-path", default=None, help="人間向けサマリの出力先パス(例: $GITHUB_STEP_SUMMARY)")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    try:
        event_payload = _load_json_file(args.event_json_path)
        issue_payload = _load_json_file(args.issue_json_path) if args.issue_json_path else None
        planner_input = normalize_github_event(
            trigger=args.trigger, event_payload=event_payload, issue_payload=issue_payload,
        )
        result = plan(planner_input)
    except (OSError, json.JSONDecodeError, PlannerInputError) as exc:
        # exc自体のstr()/repr()は埋め込まない(入力ファイルの内容の断片を含み得るため)。
        result = _internal_error_result(f"planner入力の準備に失敗しました({type(exc).__name__})。")

    machine_dict = result.to_machine_dict()
    human_text = result.to_human_text()

    print(human_text)
    print(json.dumps(machine_dict, ensure_ascii=False, indent=2))

    if args.machine_json_path:
        Path(args.machine_json_path).write_text(
            json.dumps(machine_dict, ensure_ascii=False, indent=2), encoding="utf-8",
        )
    if args.summary_path:
        with open(args.summary_path, "a", encoding="utf-8") as f:
            f.write("## AUTO-001 agent planner dry-run結果\n\n")
            f.write("**read-only dry-run: GitHub上への実際の変更は行っていません。**\n\n")
            f.write("```\n")
            f.write(human_text)
            f.write("\n```\n")

    return 0 if result.decision is not Decision.INTERNAL_ERROR else 2


if __name__ == "__main__":
    raise SystemExit(main())
