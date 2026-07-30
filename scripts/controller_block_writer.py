"""Controller Appによる、正確に1件の状態ラベル遷移(agent:ready -> agent:blocked)
と、それに付随する管理コメント(managed comment)の安全な作成・更新を実行する
ための判定・検証ロジック(AUTO-001-05-03-03B)。

このモジュール自身はGitHub APIへのHTTPリクエストを一切行わない。実際のHTTP
呼び出しはworkflow側のcurlステップが担い、レスポンス(HTTP status・JSON本文)は
一時ファイル・CLI引数経由でこのモジュールへ渡される。

既存モジュールの再利用方針(重複実装しない):

* `scripts.issue_agent_planner` の `AGENT_READY_LABEL` / `AGENT_BLOCKED_LABEL` /
  `CONFLICTING_STATE_LABELS` をそのまま使う。
* `scripts.issue_agent_planner._sanitize_validation_errors()` を再利用し、
  preflight validatorの生メッセージ(Issue本文由来の断片を含み得る)を、
  固定安全文言へ変換するロジックを重複実装しない。`issue_agent_planner.py`
  自体は変更しない(既存のdry-run workflow・テストへの影響を避けるため)。
* `scripts.controller_label_writer` の `check_repository_label_exists` /
  `check_state_unchanged_before_write` / `extract_label_names_from_issue_response`
  をそのまま使う(repository label前提確認・状態ラベル変化検知・ラベル抽出は
  ラベル名に依存しない汎用ロジックのため)。

managed commentの本文は、plannerのdry-run専用文言(`planned_comment`)を一切
使わず、`scripts.issue_preflight_validator.validate_issue_body()` を直接
呼び出して得た、サニタイズ済みerrors(code/section/messageの構造化データ、
Issue本文の生の引用を含まない)だけから決定的に組み立てる。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Sequence

from scripts.controller_label_writer import (
    check_repository_label_exists,
    check_state_unchanged_before_write,
    extract_label_names_from_issue_response,
)
from scripts.issue_agent_planner import (
    AGENT_BLOCKED_LABEL,
    AGENT_READY_LABEL,
    CONFLICTING_STATE_LABELS,
    _sanitize_validation_errors,
)
from scripts.issue_preflight_validator import ValidationStatus, validate_issue_body

__all__ = [
    "ReasonCode",
    "CheckOutcome",
    "MANAGED_COMMENT_MARKER",
    "MANAGED_COMMENT_AUTHOR_LOGIN",
    "compute_current_preflight_result",
    "compute_comment_fingerprint",
    "build_canonical_block_comment",
    "extract_comment_fingerprint",
    "extract_comments_from_response",
    "classify_managed_comments",
    "classify_precondition",
    "check_block_plan_matches_expected",
    "check_errors_match_current",
    "check_add_blocked_http_status",
    "verify_blocked_present_after_add",
    "check_comment_create_http_status",
    "check_comment_update_http_status",
    "verify_managed_comment_after_write",
    "evaluate_final_state",
    # 汎用ロジックの再エクスポート(workflow/テストの参照経路を一本化するため)
    "check_repository_label_exists",
    "check_state_unchanged_before_write",
    "extract_label_names_from_issue_response",
    "main",
]


class ReasonCode(str, Enum):
    WRITE_PLAN_REJECTED = "WRITE_PLAN_REJECTED"
    NOOP_ALREADY_APPLIED = "NOOP_ALREADY_APPLIED"
    COMMENT_UPDATE_REQUIRED = "COMMENT_UPDATE_REQUIRED"
    WRITE_PARTIAL_STATE_DETECTED = "WRITE_PARTIAL_STATE_DETECTED"
    TARGET_LABEL_MISSING = "TARGET_LABEL_MISSING"
    STATE_CHANGED_BEFORE_WRITE = "STATE_CHANGED_BEFORE_WRITE"
    AUTH_TOKEN_FAILED = "AUTH_TOKEN_FAILED"
    WRITE_ADD_BLOCKED_FAILED = "WRITE_ADD_BLOCKED_FAILED"
    WRITE_VERIFICATION_FAILED = "WRITE_VERIFICATION_FAILED"
    COMMENT_CREATE_FAILED = "COMMENT_CREATE_FAILED"
    COMMENT_UPDATE_FAILED = "COMMENT_UPDATE_FAILED"
    COMMENT_VERIFICATION_FAILED = "COMMENT_VERIFICATION_FAILED"
    WRITE_PARTIAL = "WRITE_PARTIAL"
    MANAGED_COMMENT_DUPLICATE = "MANAGED_COMMENT_DUPLICATE"
    MANAGED_COMMENT_OWNERSHIP_MISMATCH = "MANAGED_COMMENT_OWNERSHIP_MISMATCH"
    WRITE_SUCCEEDED = "WRITE_SUCCEEDED"
    COMMENT_UPDATED = "COMMENT_UPDATED"
    PREFLIGHT_RESULT_MISMATCH = "PREFLIGHT_RESULT_MISMATCH"
    PREFLIGHT_NOW_PASSES = "PREFLIGHT_NOW_PASSES"
    RESPONSE_VALIDATION_FAILED = "RESPONSE_VALIDATION_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(frozen=True)
class CheckOutcome:
    """呼び出し側(workflow)が機械的に解釈できる最小限の結果。

    `detail`は固定語彙・数値・真偽値・comment IDだけで構成し、Issue本文・
    タイトル・コメント本文全体など未信頼入力の内容を一切含めない。
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
REQUIRED_PLANNED_ADD: tuple[str, ...] = (AGENT_BLOCKED_LABEL,)

MANAGED_COMMENT_MARKER = "<!-- AUTO-001:preflight-block:v1 -->"
MANAGED_COMMENT_AUTHOR_LOGIN = "eigo-radio-auto-controller[bot]"
MANAGED_COMMENT_HEADING = "## AUTO-001 preflight不合格"
MANAGED_COMMENT_DESCRIPTION = (
    "このIssueは自動処理のpreflight検査で契約違反が見つかったため、"
    "agent:blockedへ遷移しました。"
)
MANAGED_COMMENT_GUIDANCE = (
    "Issue本文を修正して契約(管理ID・受入条件など固定12見出し)を満たしたうえで、"
    "agent:readyラベルを再度付与してください。"
)

_FINGERPRINT_RE = re.compile(r"<!-- AUTO-001:fingerprint:([0-9a-f]{64}) -->")
_REQUIRED_ERROR_KEYS = frozenset({"code", "section", "message"})


# ---------------------------------------------------------------------------
# preflight再評価(plannerのplan()はagent:ready前提のため、blocked状態の
# Issueに対して独立に再評価するためにvalidatorを直接呼び出す)
# ---------------------------------------------------------------------------

def compute_current_preflight_result(issue_body: str) -> tuple[str, Optional[list[dict]]]:
    """現在のIssue本文をpreflight validatorへ直接かけ、(status, errors)を返す。

    status is one of "CONTRACT_VIOLATION" / "PASS" / "INTERNAL_ERROR"。
    errorsはstatus=="CONTRACT_VIOLATION"の場合だけサニタイズ済みリスト、
    それ以外はNone。

    "PASS"(errors 0件、本文が修正済み)と"INTERNAL_ERROR"(validator自体の
    故障)を区別することで、blocked状態のIssueに対して
    `PREFLIGHT_NOW_PASSES`(復帰は03Bの対象外、書き込みなしで安全終了)と
    真の内部エラーとを取り違えないようにする。
    """
    result = validate_issue_body(issue_body)
    if result.status is ValidationStatus.CONTRACT_VIOLATION:
        return "CONTRACT_VIOLATION", _sanitize_validation_errors(result.errors)
    if result.status is ValidationStatus.PASS:
        return "PASS", None
    return "INTERNAL_ERROR", None


def _is_valid_sanitized_error(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    if set(entry.keys()) != _REQUIRED_ERROR_KEYS:
        return False
    if not isinstance(entry.get("code"), str) or not entry["code"]:
        return False
    if not isinstance(entry.get("message"), str) or not entry["message"]:
        return False
    section = entry.get("section")
    if section is not None and not isinstance(section, str):
        return False
    return True


# ---------------------------------------------------------------------------
# managed comment: canonical本文・fingerprint
# ---------------------------------------------------------------------------

def _build_comment_preimage(errors: Sequence[dict]) -> str:
    lines = [
        MANAGED_COMMENT_MARKER,
        MANAGED_COMMENT_HEADING,
        MANAGED_COMMENT_DESCRIPTION,
        f"契約違反: {len(errors)}件",
    ]
    for i, e in enumerate(errors, start=1):
        where = f"[{e['section']}] " if e.get("section") else ""
        lines.append(f"{i}. {where}{e['message']} (code={e['code']})")
    lines.append(MANAGED_COMMENT_GUIDANCE)
    return "\n".join(lines)


def compute_comment_fingerprint(errors: Sequence[dict]) -> str:
    """errorsと固定文言(見出し・説明・案内)だけから決定的に導出するfingerprint
    (sha256)。固定文言が将来変更された場合も、その変更自体がfingerprintへ
    反映される(pre-imageに固定文言も含めるため)。
    """
    preimage = _build_comment_preimage(errors)
    return hashlib.sha256(preimage.encode("utf-8")).hexdigest()


def build_canonical_block_comment(errors: Sequence[dict]) -> str:
    """管理コメントのcanonical本文を、サニタイズ済みerrorsだけから決定的に
    組み立てる。Issue本文・タイトルなど未信頼入力は一切参照しない。
    """
    fingerprint = compute_comment_fingerprint(errors)
    lines = _build_comment_preimage(errors).split("\n")
    lines.insert(1, f"<!-- AUTO-001:fingerprint:{fingerprint} -->")
    return "\n".join(lines)


def extract_comment_fingerprint(body: str) -> Optional[str]:
    m = _FINGERPRINT_RE.search(body)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# コメントAPIレスポンスの解析
# ---------------------------------------------------------------------------

def extract_comments_from_response(raw: Any) -> Optional[list[dict]]:
    """`GET /issues/{number}/comments`のレスポンス(トップレベル配列)から、
    {id, body, author_login}だけを抽出する。形状不正時はNoneを返す。
    """
    if not isinstance(raw, list):
        return None
    comments: list[dict] = []
    for entry in raw:
        if not isinstance(entry, dict):
            return None
        comment_id = entry.get("id")
        body = entry.get("body")
        user = entry.get("user")
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            return None
        if not isinstance(body, str):
            return None
        if not isinstance(user, dict) or not isinstance(user.get("login"), str):
            return None
        comments.append({"id": comment_id, "body": body, "author_login": user["login"]})
    return comments


# ---------------------------------------------------------------------------
# managed comment状態分類
# ---------------------------------------------------------------------------

def classify_managed_comments(comments: Sequence[dict], expected_fingerprint: str) -> CheckOutcome:
    """固定markerを含むコメントを走査し、0件/1件一致/1件不一致/2件以上/
    author不一致を判定する。comment本文全体は結果へ含めない。
    """
    marker_hits = [c for c in comments if MANAGED_COMMENT_MARKER in c.get("body", "")]

    if not marker_hits:
        return CheckOutcome(True, None, {"MANAGED_COMMENT_STATE": "NONE", "MANAGED_COMMENT_COUNT": 0})

    if len(marker_hits) >= 2:
        return CheckOutcome(
            False, ReasonCode.MANAGED_COMMENT_DUPLICATE,
            {"MANAGED_COMMENT_STATE": "DUPLICATE", "MANAGED_COMMENT_COUNT": len(marker_hits)},
        )

    only = marker_hits[0]
    if only.get("author_login") != MANAGED_COMMENT_AUTHOR_LOGIN:
        return CheckOutcome(
            False, ReasonCode.MANAGED_COMMENT_OWNERSHIP_MISMATCH,
            {"MANAGED_COMMENT_STATE": "OWNERSHIP_MISMATCH", "MANAGED_COMMENT_COUNT": 1},
        )

    existing_fp = extract_comment_fingerprint(only.get("body", ""))
    if existing_fp == expected_fingerprint:
        return CheckOutcome(
            True, None,
            {"MANAGED_COMMENT_STATE": "MATCHES", "MANAGED_COMMENT_COUNT": 1, "COMMENT_ID": only["id"]},
        )
    return CheckOutcome(
        True, None,
        {"MANAGED_COMMENT_STATE": "STALE", "MANAGED_COMMENT_COUNT": 1, "COMMENT_ID": only["id"]},
    )


# ---------------------------------------------------------------------------
# 1. final-state no-op / comment-update-required / partial-state 判定
# ---------------------------------------------------------------------------

def classify_precondition(
    current_labels: Sequence[str],
    comments: Sequence[dict],
    current_status: str,
    current_errors: Optional[list[dict]],
) -> CheckOutcome:
    """`current_status`/`current_errors`は`compute_current_preflight_result()`
    の結果。

    * agent:ready と agent:blocked が両方存在する -> PARTIAL_STATE_DETECTED
    * agent:blocked が存在し、agent:ready が存在せず、他の競合ラベルも無い場合:
        - current_status=="PASS"(Issue本文が修正済みでerrors 0件)
          -> PREFLIGHT_NOW_PASSES(復帰は03Bの対象外。token生成・write一切
          なしで安全に終了する。既存のblockedラベル・commentは削除しない)
        - current_status!="CONTRACT_VIOLATION"(validator自体の内部エラー等)
          -> INTERNAL_ERROR
        - managed commentが0件 -> 想定外の部分状態としてPARTIAL_STATE_DETECTED
        - managed commentが1件かつcanonical一致 -> NOOP_ALREADY_APPLIED
        - managed commentが1件かつ不一致(古い) -> COMMENT_UPDATE_REQUIRED
        - managed commentが2件以上/author不一致 -> それぞれの固定reason code
    * それ以外(agent:readyのみを含む) -> NEEDS_WRITE
      (後段のplanner厳密一致判定・errors完全一致判定で、書き込み対象外なら
      安全に拒否される)
    """
    labels = set(current_labels)
    ready = AGENT_READY_LABEL in labels
    blocked = AGENT_BLOCKED_LABEL in labels
    other_conflicts = (labels & CONFLICTING_STATE_LABELS) - {AGENT_BLOCKED_LABEL}

    base_detail = {
        "READY_PRESENT": "true" if ready else "false",
        "BLOCKED_PRESENT": "true" if blocked else "false",
    }

    if ready and blocked:
        return CheckOutcome(
            False, ReasonCode.WRITE_PARTIAL_STATE_DETECTED,
            {**base_detail, "PRECONDITION_STATE": "PARTIAL_STATE_DETECTED"},
        )

    if blocked and not ready and not other_conflicts:
        if current_status == "PASS":
            return CheckOutcome(
                True, ReasonCode.PREFLIGHT_NOW_PASSES,
                {**base_detail, "PRECONDITION_STATE": "PREFLIGHT_NOW_PASSES"},
            )
        if current_status != "CONTRACT_VIOLATION" or current_errors is None:
            return CheckOutcome(
                False, ReasonCode.INTERNAL_ERROR, {**base_detail, "PRECONDITION_STATE": "NA"}
            )

        expected_fp = compute_comment_fingerprint(current_errors)
        comment_outcome = classify_managed_comments(comments, expected_fp)
        if not comment_outcome.ok:
            return CheckOutcome(
                comment_outcome.ok, comment_outcome.reason_code,
                {**base_detail, **comment_outcome.detail},
            )

        comment_state = comment_outcome.detail.get("MANAGED_COMMENT_STATE")
        comment_count = comment_outcome.detail.get("MANAGED_COMMENT_COUNT", 0)
        if comment_state == "NONE":
            return CheckOutcome(
                False, ReasonCode.WRITE_PARTIAL_STATE_DETECTED,
                {**base_detail, "PRECONDITION_STATE": "PARTIAL_STATE_DETECTED",
                 "MANAGED_COMMENT_COUNT": comment_count},
            )
        if comment_state == "MATCHES":
            return CheckOutcome(
                True, ReasonCode.NOOP_ALREADY_APPLIED,
                {**base_detail, "PRECONDITION_STATE": "ALREADY_APPLIED",
                 "MANAGED_COMMENT_COUNT": comment_count},
            )
        # STALE
        return CheckOutcome(
            True, ReasonCode.COMMENT_UPDATE_REQUIRED,
            {
                **base_detail,
                "PRECONDITION_STATE": "COMMENT_UPDATE_REQUIRED",
                "MANAGED_COMMENT_COUNT": comment_count,
                "COMMENT_ID": comment_outcome.detail.get("COMMENT_ID"),
            },
        )

    return CheckOutcome(True, None, {**base_detail, "PRECONDITION_STATE": "NEEDS_WRITE"})


# ---------------------------------------------------------------------------
# 2. planner契約の厳密一致判定(WOULD_BLOCK_PREFLIGHT専用)
# ---------------------------------------------------------------------------

def check_block_plan_matches_expected(planner_result: Any) -> CheckOutcome:
    """`scripts.issue_agent_planner.PlannerResult.to_machine_dict()`が、
    正確に次の1パターンに一致する場合だけpassとする:

        decision=WOULD_BLOCK_PREFLIGHT, applicable=true,
        planned_remove_labels=[agent:ready], planned_add_labels=[agent:blocked],
        errorsが1件以上かつ全要素が{code, section, message}のschemaに一致

    `planned_comment`(dry-run専用文言)の内容はここでは一切参照・使用しない。
    """
    if not isinstance(planner_result, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    decision = planner_result.get("decision")
    applicable = planner_result.get("applicable")
    planned_remove = planner_result.get("planned_remove_labels")
    planned_add = planner_result.get("planned_add_labels")
    errors = planner_result.get("errors")

    if not isinstance(planned_remove, list) or not isinstance(planned_add, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
    if not isinstance(errors, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    valid_errors = len(errors) >= 1 and all(_is_valid_sanitized_error(e) for e in errors)

    matches = (
        decision == "WOULD_BLOCK_PREFLIGHT"
        and applicable is True
        and tuple(planned_remove) == REQUIRED_PLANNED_REMOVE
        and tuple(planned_add) == REQUIRED_PLANNED_ADD
        and valid_errors
    )
    if matches:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_PLAN_REJECTED, {})


def check_errors_match_current(current_result: dict, planner_result: Any) -> CheckOutcome:
    """初回NEEDS_WRITE経路限定のwriter進行条件: `validate_issue_body()`を
    直接呼び出して得たerrors(`current_result`、`compute_current_preflight_result()`
    の"status"/"errors"を保持する辞書)と、plannerのmachine_dict.errorsが、
    要素数・順序・code/section/message・重複を含めて完全一致することを検証
    する。一致しない場合、App token生成・ラベルwrite・コメントwriteのいずれ
    も行わない(呼び出し側でこの関数の結果をgateとして使う)。
    """
    if not isinstance(current_result, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
    if not isinstance(planner_result, dict):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    planner_errors = planner_result.get("errors")
    if not isinstance(planner_errors, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    if current_result.get("status") != "CONTRACT_VIOLATION":
        return CheckOutcome(False, ReasonCode.PREFLIGHT_RESULT_MISMATCH, {})
    current_errors = current_result.get("errors")
    if not isinstance(current_errors, list):
        return CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})

    if list(current_errors) == list(planner_errors):
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.PREFLIGHT_RESULT_MISMATCH, {})


# ---------------------------------------------------------------------------
# 3. write API呼び出し結果の判定(HTTP statusだけによる一次判定)
# ---------------------------------------------------------------------------

def check_add_blocked_http_status(http_status: int) -> CheckOutcome:
    if 200 <= http_status < 300:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_ADD_BLOCKED_FAILED, {})


def verify_blocked_present_after_add(current_labels: Sequence[str]) -> CheckOutcome:
    if AGENT_BLOCKED_LABEL in set(current_labels):
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.WRITE_VERIFICATION_FAILED, {})


def check_comment_create_http_status(http_status: int) -> CheckOutcome:
    if 200 <= http_status < 300:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.COMMENT_CREATE_FAILED, {})


def check_comment_update_http_status(http_status: int) -> CheckOutcome:
    if 200 <= http_status < 300:
        return CheckOutcome(True, None, {})
    return CheckOutcome(False, ReasonCode.COMMENT_UPDATE_FAILED, {})


def verify_managed_comment_after_write(
    comments: Sequence[dict], expected_fingerprint: str
) -> CheckOutcome:
    """comment作成/更新後の再取得結果から、固定marker・author・fingerprintが
    厳密に一致する管理コメントが正確に1件だけ存在することを検証する。
    """
    outcome = classify_managed_comments(comments, expected_fingerprint)
    if not outcome.ok:
        return outcome
    if outcome.detail.get("MANAGED_COMMENT_STATE") == "MATCHES":
        return CheckOutcome(True, None, outcome.detail)
    return CheckOutcome(False, ReasonCode.COMMENT_VERIFICATION_FAILED, outcome.detail)


# ---------------------------------------------------------------------------
# 4. 最終状態評価
# ---------------------------------------------------------------------------

def evaluate_final_state(
    before_labels: Sequence[str],
    after_labels: Sequence[str],
    after_comments: Sequence[dict],
    expected_fingerprint: str,
    *,
    require_label_transition: bool,
) -> CheckOutcome:
    """最終状態評価。`require_label_transition=True`(NEEDS_WRITE経路)の場合は
    ラベル遷移(blockedあり・readyなし・他競合なし・無関係ラベル保持)まで検証
    する。`False`(COMMENT_UPDATE_REQUIRED経路)の場合はラベルが変化していない
    ことと、管理コメントの内容だけを検証する。
    """
    before_set = set(before_labels)
    after_set = set(after_labels)

    comment_outcome = classify_managed_comments(after_comments, expected_fingerprint)
    comment_ok = comment_outcome.ok and comment_outcome.detail.get("MANAGED_COMMENT_STATE") == "MATCHES"

    if require_label_transition:
        blocked_present = AGENT_BLOCKED_LABEL in after_set
        ready_present = AGENT_READY_LABEL in after_set
        other_conflicts = (after_set & CONFLICTING_STATE_LABELS) - {AGENT_BLOCKED_LABEL}
        before_unrelated = before_set - {AGENT_READY_LABEL, AGENT_BLOCKED_LABEL}
        after_unrelated = after_set - {AGENT_READY_LABEL, AGENT_BLOCKED_LABEL}
        unrelated_preserved = before_unrelated <= after_unrelated

        detail = {
            "BLOCKED_PRESENT": "true" if blocked_present else "false",
            "READY_PRESENT": "true" if ready_present else "false",
            "UNRELATED_PRESERVED": "true" if unrelated_preserved else "false",
            "COMMENT_OK": "true" if comment_ok else "false",
        }
        ok = (
            blocked_present and not ready_present and not other_conflicts
            and unrelated_preserved and comment_ok
        )
        if ok:
            return CheckOutcome(True, ReasonCode.WRITE_SUCCEEDED, detail)
        return CheckOutcome(False, ReasonCode.WRITE_PARTIAL, detail)

    unchanged = before_set == after_set
    detail = {
        "BLOCKED_PRESENT": "true" if AGENT_BLOCKED_LABEL in after_set else "false",
        "READY_PRESENT": "true" if AGENT_READY_LABEL in after_set else "false",
        "UNRELATED_PRESERVED": "true" if unchanged else "false",
        "COMMENT_OK": "true" if comment_ok else "false",
    }
    ok = unchanged and comment_ok
    if ok:
        return CheckOutcome(True, ReasonCode.COMMENT_UPDATED, detail)
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
    return extract_label_names_from_issue_response(_load_json_file(path))


def _comments_from_file_or_none(path: str) -> Optional[list[dict]]:
    return extract_comments_from_response(_load_json_file(path))


def _load_current_result(path: str) -> tuple[str, Optional[list[dict]]]:
    """`compute-current-errors`が書き出した{"status":.., "errors":..}形式を
    読み込む。"""
    raw = _load_json_file(path)
    if not isinstance(raw, dict) or "status" not in raw or "errors" not in raw:
        raise ValueError("current-errors-pathの内容が想定形式({status, errors})ではありません")
    status = raw["status"]
    errors = raw["errors"]
    if errors is not None and not isinstance(errors, list):
        raise ValueError("current-errors-pathのerrorsがリストまたはnullではありません")
    return status, errors


def _errors_only_or_none(path: str) -> Optional[list[dict]]:
    """書き込み系step(NEEDS_WRITE/COMMENT_UPDATE_REQUIRED経路、既に
    CONTRACT_VIOLATIONであることが上流で確定済み)から使う簡易アクセサ。"""
    _status, errors = _load_current_result(path)
    return errors


def _bool_arg(value: str) -> bool:
    if value not in ("true", "false"):
        raise argparse.ArgumentTypeError("true または false を指定してください")
    return value == "true"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="AUTO-001-05-03-03B Controller App blocked/comment writer 判定・検証ロジック"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_errors = sub.add_parser("compute-current-errors", help="現在の本文に対するpreflight再評価")
    p_errors.add_argument("--issue-response-file", required=True)
    p_errors.add_argument("--output-path", required=True)

    p_pre = sub.add_parser("classify-precondition", help="final-state no-op / comment-update / partial判定")
    p_pre.add_argument("--issue-response-file", required=True)
    p_pre.add_argument("--comments-response-file", required=True)
    p_pre.add_argument("--current-errors-path", required=True)

    p_plan = sub.add_parser("check-plan", help="planner契約の厳密一致判定(WOULD_BLOCK_PREFLIGHT)")
    p_plan.add_argument("--planner-json-path", required=True)

    p_errors_match = sub.add_parser(
        "check-errors-match",
        help="direct validator errorsとplanner machine_dict.errorsの完全一致判定(NEEDS_WRITE経路限定)",
    )
    p_errors_match.add_argument("--current-errors-path", required=True)
    p_errors_match.add_argument("--planner-json-path", required=True)

    p_comment_state = sub.add_parser("check-comment-state", help="managed commentの現在状態を判定")
    p_comment_state.add_argument("--comments-response-file", required=True)
    p_comment_state.add_argument("--current-errors-path", required=True)

    p_add_status = sub.add_parser("check-add-blocked-http-status")
    p_add_status.add_argument("--http-status", type=int, required=True)

    p_verify_add = sub.add_parser("verify-blocked-present")
    p_verify_add.add_argument("--response-file", required=True)

    p_comment_create_status = sub.add_parser("check-comment-create-http-status")
    p_comment_create_status.add_argument("--http-status", type=int, required=True)

    p_comment_update_status = sub.add_parser("check-comment-update-http-status")
    p_comment_update_status.add_argument("--http-status", type=int, required=True)

    p_verify_comment = sub.add_parser("verify-managed-comment")
    p_verify_comment.add_argument("--comments-response-file", required=True)
    p_verify_comment.add_argument("--current-errors-path", required=True)

    p_final = sub.add_parser("evaluate-final-state")
    p_final.add_argument("--before-response-file", required=True)
    p_final.add_argument("--after-response-file", required=True)
    p_final.add_argument("--after-comments-file", required=True)
    p_final.add_argument("--current-errors-path", required=True)
    p_final.add_argument("--require-label-transition", type=_bool_arg, required=True)

    p_render = sub.add_parser(
        "render-comment-body",
        help="POST/PATCH用のcanonical comment本文をJSONファイルへ書き出す(標準出力・Summaryへは出さない)",
    )
    p_render.add_argument("--current-errors-path", required=True)
    p_render.add_argument("--output-path", required=True)

    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    try:
        if args.command == "compute-current-errors":
            raw = _load_json_file(args.issue_response_file)
            body = raw.get("body") if isinstance(raw, dict) else None
            if not isinstance(body, str):
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                status, errors = compute_current_preflight_result(body)
                with open(args.output_path, "w", encoding="utf-8") as f:
                    json.dump({"status": status, "errors": errors}, f, ensure_ascii=False)
                if status == "INTERNAL_ERROR":
                    outcome = CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {"PREFLIGHT_STATUS": status})
                else:
                    outcome = CheckOutcome(True, None, {"PREFLIGHT_STATUS": status})

        elif args.command == "classify-precondition":
            labels = _labels_from_file_or_none(args.issue_response_file)
            comments = _comments_from_file_or_none(args.comments_response_file)
            if labels is None or comments is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                current_status, current_errors = _load_current_result(args.current_errors_path)
                outcome = classify_precondition(labels, comments, current_status, current_errors)

        elif args.command == "check-plan":
            planner_result = _load_json_file(args.planner_json_path)
            outcome = check_block_plan_matches_expected(planner_result)

        elif args.command == "check-errors-match":
            current_result = _load_json_file(args.current_errors_path)
            planner_result = _load_json_file(args.planner_json_path)
            outcome = check_errors_match_current(current_result, planner_result)

        elif args.command == "check-comment-state":
            comments = _comments_from_file_or_none(args.comments_response_file)
            if comments is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                current_errors = _errors_only_or_none(args.current_errors_path)
                if current_errors is None:
                    outcome = CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})
                else:
                    expected_fp = compute_comment_fingerprint(current_errors)
                    outcome = classify_managed_comments(comments, expected_fp)

        elif args.command == "check-add-blocked-http-status":
            outcome = check_add_blocked_http_status(args.http_status)

        elif args.command == "verify-blocked-present":
            labels = _labels_from_file_or_none(args.response_file)
            if labels is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                outcome = verify_blocked_present_after_add(labels)

        elif args.command == "check-comment-create-http-status":
            outcome = check_comment_create_http_status(args.http_status)

        elif args.command == "check-comment-update-http-status":
            outcome = check_comment_update_http_status(args.http_status)

        elif args.command == "verify-managed-comment":
            comments = _comments_from_file_or_none(args.comments_response_file)
            if comments is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                current_errors = _errors_only_or_none(args.current_errors_path)
                if current_errors is None:
                    outcome = CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})
                else:
                    expected_fp = compute_comment_fingerprint(current_errors)
                    outcome = verify_managed_comment_after_write(comments, expected_fp)

        elif args.command == "evaluate-final-state":
            before_labels = _labels_from_file_or_none(args.before_response_file)
            after_labels = _labels_from_file_or_none(args.after_response_file)
            after_comments = _comments_from_file_or_none(args.after_comments_file)
            if before_labels is None or after_labels is None or after_comments is None:
                outcome = CheckOutcome(False, ReasonCode.RESPONSE_VALIDATION_FAILED, {})
            else:
                current_errors = _errors_only_or_none(args.current_errors_path)
                if current_errors is None:
                    outcome = CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})
                else:
                    expected_fp = compute_comment_fingerprint(current_errors)
                    outcome = evaluate_final_state(
                        before_labels, after_labels, after_comments, expected_fp,
                        require_label_transition=args.require_label_transition,
                    )

        elif args.command == "render-comment-body":
            current_errors = _errors_only_or_none(args.current_errors_path)
            if current_errors is None:
                outcome = CheckOutcome(False, ReasonCode.INTERNAL_ERROR, {})
            else:
                body_text = build_canonical_block_comment(current_errors)
                with open(args.output_path, "w", encoding="utf-8") as f:
                    json.dump({"body": body_text}, f, ensure_ascii=False)
                outcome = CheckOutcome(True, None, {})

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
