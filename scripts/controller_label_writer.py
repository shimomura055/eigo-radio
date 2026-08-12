"""Controller Appによる、正確に1件の状態ラベル遷移(agent:ready -> agent:working)
を安全に実行するための判定・検証ロジック(AUTO-001-05-03-03A)。

このモジュール自身はGitHub APIへのHTTPリクエストを一切行わない。実際のHTTP
呼び出しはworkflow側のcurlステップが担い、レスポンス(HTTP status・JSON本文)は
一時ファイル・CLI引数経由でこのモジュールへ渡される。

既存の`scripts.issue_agent_planner`が定義する状態ラベル(`AGENT_READY_LABEL`
`AGENT_WORKING_LABEL` `CONFLICTING_STATE_LABELS` `KNOWN_STATE_LABELS`)を
そのまま再利用し、別の定義を重複実装しない。plannerが算出した状態遷移計画
(`PlannerResult.to_machine_dict()`)が、次の1パターンに正確に一致する場合
だけwriteへ進める:

    decision=WOULD_START, applicable=true,
    planned_remove_labels=[agent:ready], planned_add_labels=[agent:working],
    planned_comment=なし

順序・重複・余分なラベル・余分なコメント計画を一切許容しない
(`check_planner_plan_matches_expected`)。

責務分離:

* `classify_precondition_state()` -- 現在のIssueラベルから、書き込みが
  そもそも必要か(NEEDS_WRITE)、既に完了済みか(ALREADY_APPLIED)、
  中間状態で危険か(PARTIAL_STATE_DETECTED)を判定する。
* `check_planner_plan_matches_expected()` -- plannerの計画が期待する
  1パターンに正確に一致するかだけを判定する。
* `check_state_unchanged_before_write()` -- planner評価時点と書き込み
  直前時点とで、状態ラベルの集合が変化していないかを判定する。
* `check_repository_label_exists()` / `check_add_label_http_status()` /
  `check_remove_label_http_status()` -- 各write APIのHTTP statusだけを
  入力とする、資格情報を一切含まない純粋判定。
* `verify_label_present_after_add()` / `evaluate_final_state()` --
  「HTTP statusだけで成功判定しない。GitHubから再取得した結果を根拠にする」
  という設計方針に基づき、再取得したIssueラベルの実態から判定する。
* CLI (`main()`) -- 上記をファイルパス/フラグ経由で呼び出し、固定語彙の
  1行だけを標準出力へ書く。raw例外メッセージやIssue本文・タイトルなどの
  未信頼フィールドは一切出力しない。
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Sequence

from scripts.issue_agent_planner import (
    AGENT_READY_LABEL,
    AGENT_WORKING_LABEL,
    CONFLICTING_STATE_LABELS,
    KNOWN_STATE_LABELS,
)


class ReasonCode(str, Enum):
    WRITE_PLAN_REJECTED = "WRITE_PLAN_REJECTED"
    NOOP_ALREADY_APPLIED = "NOOP_ALREADY_APPLIED"
    WRITE_PARTIAL_STATE_DETECTED = "WRITE_PARTIAL_STATE_DETECTED"
    TARGET_LABEL_MISSING = "TARGET_LABEL_MISSING"
    STATE_CHANGED_BEFORE_WRITE = "STATE_CHANGED_BEFORE_WRITE"
    AUTH_TOKEN_FAILED = "AUTH_TOKEN_FAILED"
    WRITE_ADD_FAILED = "WRITE_ADD_FAILED"
    WRITE_VERIFICATION_FAILED = "WRITE_VERIFICATION_FAILED"
    WRITE_PARTIAL = "WRITE_PARTIAL"
    WRITE_SUCCEEDED = "WRITE_SUCCEEDED"
    RESPONSE_VALIDATION_FAILED = "RESPONSE_VALIDATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class PreconditionState(str, Enum):
    NEEDS_WRITE = "NEEDS_WRITE"
    ALREADY_APPLIED = "ALREADY_APPLIED"
    PARTIAL_STATE_DETECTED = "PARTIAL_STATE_DETECTED"


@dataclass(frozen=True)
class CheckOutcome:
    """呼び出し側(workflow)が機械的に解釈できる最小限の結果。

    `detail`は固定語彙・数値・真偽値だけで構成し、Issue本文・タイトル・
    ラベルの自由記述値など未信頼入力の内容を一切含めない。
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


REQUIRED_PLANNED_REMOVE: tuple[str, ...] = (AGENT_READY_LABEL,)
REQUIRED_PLANNED_ADD: tuple[str, ...] = (AGENT_WORKING_LABEL,)


# ---------------------------------------------------------------------------
# Issue APIレスポンスからのラベル名抽出(GET /issues/{number}専用の形状)
# ---------------------------------------------------------------------------

def extract_label_names_from_issue_response(raw: Any) -> Optional[list[str]]:
    """`GET /repos/{owner}/{repo}/issues/{number}`のレスポンス形状から、
    ラベル名の列だけを抽出する。形状が不正な場合はNoneを返す(例外を送出しない)。
    """
    if not isinstance(raw, dict):
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
    return names


# ---------------------------------------------------------------------------
# 1. final-state no-op / partial state 判定
# ---------------------------------------------------------------------------

def classify_precondition_state(current_labels: Sequence[str]) -> PreconditionState:
    """現在のIssueラベルから、書き込みの要否を判定する。

    * agent:ready と agent:working が両方存在する -> PARTIAL_STATE_DETECTED
    * agent:working が存在し、agent:ready が存在せず、他の競合する状態
      ラベルも存在しない -> ALREADY_APPLIED(書き込み済みとみなす)
    * それ以外(状態ラベルなし、blocked等との競合を含む) -> NEEDS_WRITE
      (この後段のplanner一致判定で、書き込み対象外なら安全に拒否される)
    """
    labels = set(current_labels)
    ready = AGENT_READY_LABEL in labels
    working = AGENT_WORKING_LABEL in labels

    if ready and working:
        return PreconditionState.PARTIAL_STATE_DETECTED

    other_conflicts = (labels & CONFLICTING_STATE_LABELS) - {AGENT_WORKING_LABEL}
    if working and not ready and not other_conflicts:
        return PreconditionState.ALREADY_APPLIED

    return PreconditionState.NEEDS_WRITE


# ---------------------------------------------------------------------------
# 2. planner契約の厳密一致判定
# ---------------------------------------------------------------------------

def check_planner_plan_matches_expected(planner_result: Any) -> CheckOutcome:
    """`scripts.issue_agent_planner.PlannerResult.to_machine_dict()`が、
    正確に次の1パターンに一致する場合だけpassとする:

        decision=WOULD_START, applicable=true,
        planned_remove_labels=[agent:ready](順序・重複・要素数とも厳密一致)、
        planned_add_labels=[agent:working](同上)、planned_comment=なし
    """
    if not isinstance(planner_result, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    decision = planner_result.get("decision")
    applicable = planner_result.get("applicable")
    planned_remove = planner_result.get("planned_remove_labels")
    planned_add = planner_result.get("planned_add_labels")
    planned_comment = planner_result.get("planned_comment")

    if not isinstance(planned_remove, list) or not isinstance(planned_add, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    matches = (
        decision == "WOULD_START"
        and applicable is True
        and tuple(planned_remove) == REQUIRED_PLANNED_REMOVE
        and tuple(planned_add) == REQUIRED_PLANNED_ADD
        and not planned_comment
    )
    if matches:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_PLAN_REJECTED, {})


# ---------------------------------------------------------------------------
# 3. repository label前提(read-only)
# ---------------------------------------------------------------------------

def check_repository_label_exists(http_status: int) -> CheckOutcome:
    """`GET /repos/{owner}/{repo}/labels/{name}`のHTTP statusだけを判定する。"""
    if http_status == 200:
        return CheckOutcome(True, None, {})
    if http_status == 404:
        return CheckOutcome(False, ReasonCode.TARGET_LABEL_MISSING, {})
    return CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})


# ---------------------------------------------------------------------------
# 4. 書き込み直前確認
# ---------------------------------------------------------------------------

def check_state_unchanged_before_write(
    planner_time_labels: Sequence[str], current_labels: Sequence[str]
) -> CheckOutcome:
    """比較対象は、既存planner定義の状態ラベル集合(`KNOWN_STATE_LABELS`)
    との積集合だけとする(無関係ラベルの変化は書き込みを妨げない)。
    """
    known = frozenset(KNOWN_STATE_LABELS)
    before = frozenset(planner_time_labels) & known
    after = frozenset(current_labels) & known
    if before != after:
        return CheckOutcome(False, ReasonCode.STATE_CHANGED_BEFORE_WRITE, {})
    return CheckOutcome(True, None, {})


# ---------------------------------------------------------------------------
# 5. write API呼び出し結果の判定(HTTP statusだけによる一次判定)
# ---------------------------------------------------------------------------

def check_add_label_http_status(http_status: int) -> CheckOutcome:
    if 200 <= http_status < 300:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_ADD_FAILED, {})


def verify_label_present_after_add(current_labels: Sequence[str]) -> CheckOutcome:
    """add直後の再取得結果から、agent:workingが実際に存在するかを検証する
    (HTTP status 200を信頼せず、GitHubから再取得した実態を根拠にする)。
    """
    if AGENT_WORKING_LABEL in set(current_labels):
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_VERIFICATION_FAILED, {})


def check_remove_label_http_status(http_status: int) -> CheckOutcome:
    """404は「対象ラベルが既に存在しない」を意味しうるため、ここでは
    即座に失敗とはしない(最終状態の再取得・検証で判断する)。
    """
    if (200 <= http_status < 300) or http_status == 404:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_PARTIAL, {})


# ---------------------------------------------------------------------------
# 6. 最終状態評価
# ---------------------------------------------------------------------------

def evaluate_final_state(
    before_labels: Sequence[str], after_labels: Sequence[str]
) -> CheckOutcome:
    """成功条件: agent:workingあり、agent:readyなし、他の状態ラベル競合なし、
    実行前に存在した無関係ラベルが失われていない。HTTP statusではなく、
    再取得したラベルの実態だけを根拠にする。
    """
    before_set = set(before_labels)
    after_set = set(after_labels)

    working_present = AGENT_WORKING_LABEL in after_set
    ready_present = AGENT_READY_LABEL in after_set
    other_conflicts = (after_set & CONFLICTING_STATE_LABELS) - {AGENT_WORKING_LABEL}

    before_unrelated = before_set - {AGENT_READY_LABEL, AGENT_WORKING_LABEL}
    after_unrelated = after_set - {AGENT_READY_LABEL, AGENT_WORKING_LABEL}
    unrelated_preserved = before_unrelated <= after_unrelated

    detail = {
        "WORKING_PRESENT": "true" if working_present else "false",
        "READY_PRESENT": "true" if ready_present else "false",
        "UNRELATED_PRESERVED": "true" if unrelated_preserved else "false",
    }

    ok = working_present and not ready_present and not other_conflicts and unrelated_preserved
    if ok:
        return CheckOutcome(True, ReasonCode.WRITE_SUCCEEDED, detail)
    return CheckOutcome(False, ReasonCode.WRITE_PARTIAL, detail)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_json_file(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _internal_error() -> CheckOutcome:
    return CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})


def _labels_from_file_or_none(path: str) -> Optional[list[str]]:
    raw = _load_json_file(path)
    return extract_label_names_from_issue_response(raw)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUTO-001-05-03-03A Controller App label writer 判定・検証ロジック"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_pre = sub.add_parser("classify-precondition", help="final-state no-op / partial state 判定")
    p_pre.add_argument("--response-file", required=True)

    p_plan = sub.add_parser("check-plan", help="planner契約の厳密一致判定")
    p_plan.add_argument("--planner-json-path", required=True)

    p_label = sub.add_parser("check-repo-label-status", help="repository label前提の判定")
    p_label.add_argument("--http-status", type=int, required=True)

    p_state = sub.add_parser("check-state-unchanged", help="書き込み直前確認")
    p_state.add_argument("--before-response-file", required=True)
    p_state.add_argument("--current-response-file", required=True)

    p_add_status = sub.add_parser("check-add-http-status", help="add label APIのHTTP status判定")
    p_add_status.add_argument("--http-status", type=int, required=True)

    p_verify = sub.add_parser("verify-working-present", help="add直後の再取得検証")
    p_verify.add_argument("--response-file", required=True)

    p_remove_status = sub.add_parser("check-remove-http-status", help="remove label APIのHTTP status判定")
    p_remove_status.add_argument("--http-status", type=int, required=True)

    p_final = sub.add_parser("evaluate-final-state", help="最終状態評価")
    p_final.add_argument("--before-response-file", required=True)
    p_final.add_argument("--after-response-file", required=True)

    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    try:
        if args.command == "classify-precondition":
            names = _labels_from_file_or_none(args.response_file)
            if names is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                state = classify_precondition_state(names)
                names_set = set(names)
                base_detail = {
                    "PRECONDITION_STATE": state.value,
                    "READY_PRESENT": "true" if AGENT_READY_LABEL in names_set else "false",
                    "WORKING_PRESENT": "true" if AGENT_WORKING_LABEL in names_set else "false",
                }
                if state is PreconditionState.PARTIAL_STATE_DETECTED:
                    outcome = CheckOutcome(False, ReasonCode.WRITE_PARTIAL_STATE_DETECTED, base_detail)
                elif state is PreconditionState.ALREADY_APPLIED:
                    outcome = CheckOutcome(True, ReasonCode.NOOP_ALREADY_APPLIED, base_detail)
                else:
                    outcome = CheckOutcome(True, None, base_detail)

        elif args.command == "check-plan":
            planner_result = _load_json_file(args.planner_json_path)
            outcome = check_planner_plan_matches_expected(planner_result)

        elif args.command == "check-repo-label-status":
            outcome = check_repository_label_exists(args.http_status)

        elif args.command == "check-state-unchanged":
            before_names = _labels_from_file_or_none(args.before_response_file)
            current_names = _labels_from_file_or_none(args.current_response_file)
            if before_names is None or current_names is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                outcome = check_state_unchanged_before_write(before_names, current_names)

        elif args.command == "check-add-http-status":
            outcome = check_add_label_http_status(args.http_status)

        elif args.command == "verify-working-present":
            names = _labels_from_file_or_none(args.response_file)
            if names is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                outcome = verify_label_present_after_add(names)

        elif args.command == "check-remove-http-status":
            outcome = check_remove_label_http_status(args.http_status)

        elif args.command == "evaluate-final-state":
            before_names = _labels_from_file_or_none(args.before_response_file)
            after_names = _labels_from_file_or_none(args.after_response_file)
            if before_names is None or after_names is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                outcome = evaluate_final_state(before_names, after_names)

        else:  # pragma: no cover - argparseがrequired=Trueで防ぐ
            outcome = _internal_error()
    except (OSError, json.JSONDecodeError, ValueError):
        # exc自体のstr()/repr()は埋め込まない(レスポンスファイルの内容の
        # 断片やIssue本文由来の値を含み得るため)。
        outcome = _internal_error()

    print(outcome.to_line())
    return 0 if outcome.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
