"""scripts/controller_block_writer.py (AUTO-001-05-03-03B) の単体テスト。

外部API・外部ネットワーク・実際のGitHub App credentialは一切使わない。
純粋関数群の決定論的な判定、CLIの入出力、workflow YAML
(.github/workflows/auto001-controller-block-check.yml)の静的検査、そして
GitHub Actions既定の厳格shell(`bash --noprofile --norc -eo pipefail`)で
実stepスクリプトを抽出実行するsubprocessテストを対象とする。

curlのbash関数スタブ・workflow抽出ヘルパー・build_body等は、既存の
auto001_test_controller_token_check.py / auto001_test_issue_preflight_validator.py
のものをそのまま再利用し、別の定義を重複実装しない。
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from auto001_test_controller_token_check import (
    EXPECTED_FULL_NAME,
    _bash_single_quote,
    _extract_step_run_lines,
    _fake_curl_function,
    _parse_github_output,
)
from auto001_test_issue_preflight_validator import build_body
from scripts.controller_block_writer import (
    CheckOutcome,
    MANAGED_COMMENT_AUTHOR_LOGIN,
    MANAGED_COMMENT_MARKER,
    ReasonCode,
    build_canonical_block_comment,
    check_add_blocked_http_status,
    check_block_plan_matches_expected,
    check_comment_create_http_status,
    check_comment_state_unchanged_before_write,
    check_comment_update_http_status,
    check_errors_match_current,
    classify_managed_comments,
    classify_precondition,
    compute_comment_fingerprint,
    compute_current_preflight_result,
    evaluate_final_state,
    extract_comment_fingerprint,
    extract_comments_from_response,
    main as cli_main,
    verify_blocked_present_after_add,
    verify_managed_comment_after_write,
)

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto001-controller-block-check.yml"
TEST_ISSUE_NUMBER = "6"


def _current_errors(body: str) -> Optional[list]:
    """テストのfixture構築専用: direct validatorのerrorsだけを取り出す
    (statusは通常CONTRACT_VIOLATIONを想定するfixtureでだけ使う)。"""
    return compute_current_preflight_result(body)[1]


def _write_current_errors_file(path: Path, issue_body: str) -> None:
    """`compute-current-errors`が書き出す{"status":.., "errors":..}形式を、
    実際にissue_bodyをvalidatorへかけた結果からそのまま再現して書き出す
    (workflow本体が使うファイル形式とテストのfixtureを一致させるため)。"""
    status, errors = compute_current_preflight_result(issue_body)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"status": status, "errors": errors}, f, ensure_ascii=False)

VALID_ISSUE_BODY = build_body()
INVALID_ISSUE_BODY = "不十分な本文"

SAMPLE_ERRORS = [
    {"code": "MISSING_HEADING", "section": None, "message": "見出しが不足しています。"},
    {"code": "ACCEPTANCE_CRITERIA_MISSING", "section": "受入条件", "message": "受入条件がありません。"},
]


def _issue_response(labels: list[str], *, body: str = "") -> dict:
    return {
        "number": int(TEST_ISSUE_NUMBER),
        "state": "open",
        "labels": [{"name": name} for name in labels],
        "body": body,
    }


def _comment(comment_id: int, body: str, author: str = MANAGED_COMMENT_AUTHOR_LOGIN) -> dict:
    """`extract_comments_from_response()`が返す正規化済みの形状
    ({id, body, author_login})。classify_managed_comments等、正規化後の
    データを受け取る関数への直接入力として使う。"""
    return {"id": comment_id, "body": body, "author_login": author}


def _raw_comment(comment_id: int, body: str, author: str = MANAGED_COMMENT_AUTHOR_LOGIN) -> dict:
    """`GET /issues/{n}/comments`の生レスポンス形状。
    extract_comments_from_response()自体のテスト専用。"""
    return {"id": comment_id, "body": body, "user": {"login": author}}


def _write_json(tmpdir: Path, name: str, data) -> str:
    path = tmpdir / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _planner_dict(**overrides) -> dict:
    base = {
        "decision": "WOULD_BLOCK_PREFLIGHT",
        "applicable": True,
        "planned_remove_labels": ["agent:ready"],
        "planned_add_labels": ["agent:blocked"],
        "errors": list(SAMPLE_ERRORS),
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# extract_comments_from_response
# ---------------------------------------------------------------------------

class ExtractCommentsFromResponseTests(unittest.TestCase):

    def test_extracts_id_body_author(self):
        raw = [_raw_comment(1, "hello", "someone")]
        self.assertEqual(
            extract_comments_from_response(raw),
            [{"id": 1, "body": "hello", "author_login": "someone"}],
        )

    def test_empty_array_is_empty_list(self):
        self.assertEqual(extract_comments_from_response([]), [])

    def test_not_a_list_returns_none(self):
        self.assertIsNone(extract_comments_from_response({"comments": []}))

    def test_entry_not_a_dict_returns_none(self):
        self.assertIsNone(extract_comments_from_response(["oops"]))

    def test_missing_user_returns_none(self):
        self.assertIsNone(extract_comments_from_response([{"id": 1, "body": "x"}]))

    def test_missing_body_returns_none(self):
        self.assertIsNone(extract_comments_from_response([{"id": 1, "user": {"login": "x"}}]))

    def test_non_integer_id_returns_none(self):
        self.assertIsNone(extract_comments_from_response([{"id": "1", "body": "x", "user": {"login": "y"}}]))


# ---------------------------------------------------------------------------
# compute_current_preflight_errors
# ---------------------------------------------------------------------------

class ComputeCurrentPreflightResultTests(unittest.TestCase):

    def test_valid_body_is_pass_with_no_errors(self):
        status, errors = compute_current_preflight_result(VALID_ISSUE_BODY)
        self.assertEqual(status, "PASS")
        self.assertIsNone(errors)

    def test_invalid_body_is_contract_violation_with_sanitized_errors(self):
        status, errors = compute_current_preflight_result(INVALID_ISSUE_BODY)
        self.assertEqual(status, "CONTRACT_VIOLATION")
        self.assertIsNotNone(errors)
        self.assertGreaterEqual(len(errors), 1)
        for e in errors:
            self.assertEqual(set(e.keys()), {"code", "section", "message"})

    def test_raw_input_never_appears_in_sanitized_message(self):
        marker = "UNIQUE-RAW-MARKER-XYZ"
        body = build_body(content={"管理ID": marker})
        _status, errors = compute_current_preflight_result(body)
        rendered = json.dumps(errors, ensure_ascii=False)
        self.assertNotIn(marker, rendered)


# ---------------------------------------------------------------------------
# canonical comment: build / fingerprint / determinism / no dry-run wording
# ---------------------------------------------------------------------------

class CanonicalCommentBuilderTests(unittest.TestCase):

    def test_contains_fixed_marker(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        self.assertIn(MANAGED_COMMENT_MARKER, body)

    def test_deterministic_body_and_fingerprint(self):
        body1 = build_canonical_block_comment(SAMPLE_ERRORS)
        body2 = build_canonical_block_comment(list(SAMPLE_ERRORS))
        self.assertEqual(body1, body2)
        self.assertEqual(
            compute_comment_fingerprint(SAMPLE_ERRORS),
            compute_comment_fingerprint(list(SAMPLE_ERRORS)),
        )

    def test_different_errors_produce_different_fingerprint(self):
        other_errors = [{"code": "OTHER", "section": None, "message": "別の違反。"}]
        self.assertNotEqual(
            compute_comment_fingerprint(SAMPLE_ERRORS),
            compute_comment_fingerprint(other_errors),
        )

    def test_extract_fingerprint_roundtrip(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        fp = extract_comment_fingerprint(body)
        self.assertEqual(fp, compute_comment_fingerprint(SAMPLE_ERRORS))

    def test_no_dry_run_wording_in_body(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        for forbidden in ("dry-run", "実際には投稿していません", "予定のコメント概要"):
            self.assertNotIn(forbidden, body)

    def test_raw_error_fields_only_used_no_unknown_fields_leak(self):
        errors = [{"code": "X", "section": "見出しA", "message": "メッセージA", "extra": "SHOULD-NOT-APPEAR"}]
        body = build_canonical_block_comment(errors)
        self.assertNotIn("SHOULD-NOT-APPEAR", body)

    def test_empty_errors_still_deterministic(self):
        body1 = build_canonical_block_comment([])
        body2 = build_canonical_block_comment([])
        self.assertEqual(body1, body2)


# ---------------------------------------------------------------------------
# classify_managed_comments
# ---------------------------------------------------------------------------

class ClassifyManagedCommentsTests(unittest.TestCase):

    def setUp(self):
        self.body = build_canonical_block_comment(SAMPLE_ERRORS)
        self.fp = compute_comment_fingerprint(SAMPLE_ERRORS)

    def test_zero_comments(self):
        outcome = classify_managed_comments([], self.fp)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "NONE")
        self.assertEqual(outcome.detail["MANAGED_COMMENT_COUNT"], 0)

    def test_one_matching(self):
        outcome = classify_managed_comments([_comment(1, self.body)], self.fp)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "MATCHES")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_one_stale(self):
        stale_body = self.body.replace(self.fp, "0" * 64)
        outcome = classify_managed_comments([_comment(1, stale_body)], self.fp)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "STALE")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_two_or_more_is_duplicate(self):
        outcome = classify_managed_comments(
            [_comment(1, self.body), _comment(2, self.body)], self.fp
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_DUPLICATE)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_COUNT"], 2)

    def test_wrong_author_is_ownership_mismatch(self):
        outcome = classify_managed_comments([_comment(1, self.body, "some-spoofer")], self.fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_OWNERSHIP_MISMATCH)

    def test_non_marker_comments_ignored(self):
        outcome = classify_managed_comments([_comment(1, "unrelated comment text")], self.fp)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "NONE")

    def test_marker_without_valid_fingerprint_is_stale(self):
        broken_body = MANAGED_COMMENT_MARKER + "\nno fingerprint line here"
        outcome = classify_managed_comments([_comment(1, broken_body)], self.fp)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "STALE")


# ---------------------------------------------------------------------------
# classify_precondition
# ---------------------------------------------------------------------------

class ClassifyPreconditionTests(unittest.TestCase):

    def setUp(self):
        self.body = build_canonical_block_comment(SAMPLE_ERRORS)

    def test_ready_only_needs_write(self):
        outcome = classify_precondition(["agent:ready"], [], "CONTRACT_VIOLATION", None)
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")

    def test_blocked_with_matching_comment_is_noop(self):
        comments = [_comment(1, self.body)]
        outcome = classify_precondition(["agent:blocked"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.NOOP_ALREADY_APPLIED)

    def test_blocked_with_stale_comment_needs_update(self):
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        stale_body = self.body.replace(fp, "0" * 64)
        comments = [_comment(1, stale_body)]
        outcome = classify_precondition(["agent:blocked"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_UPDATE_REQUIRED)
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_ready_and_blocked_is_partial_state(self):
        outcome = classify_precondition(
            ["agent:ready", "agent:blocked"], [], "CONTRACT_VIOLATION", SAMPLE_ERRORS
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL_STATE_DETECTED)

    def test_blocked_with_no_comment_is_partial_state(self):
        outcome = classify_precondition(["agent:blocked"], [], "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL_STATE_DETECTED)

    def test_blocked_with_conflicting_other_label_needs_write(self):
        outcome = classify_precondition(
            ["agent:blocked", "agent:review"], [], "CONTRACT_VIOLATION", SAMPLE_ERRORS
        )
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")

    def test_blocked_only_internal_error_status_is_internal_error(self):
        # validator自体が内部エラーの場合、fingerprint比較ができないため
        # 安全に停止する(PREFLIGHT_NOW_PASSESとは区別する)。
        outcome = classify_precondition(["agent:blocked"], [], "INTERNAL_ERROR", None)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.INTERNAL_ERROR)

    def test_blocked_only_pass_status_is_preflight_now_passes(self):
        # Issue本文が修正済みでerrors 0件(PASS)の場合、03Bは復帰処理を担当
        # しないため、token生成・write一切なしで安全に終了する。
        outcome = classify_precondition(["agent:blocked"], [], "PASS", None)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_NOW_PASSES)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "PREFLIGHT_NOW_PASSES")

    def test_preflight_now_passes_even_with_existing_matching_comment(self):
        # 本文修正後にblocked/commentが残っていても、03Bはそれらを自動削除
        # しない(このテストはclassify_precondition自体がPASSを最優先で
        # 判定し、comment状態を一切参照しないことを確認する)。
        comments = [_comment(1, self.body)]
        outcome = classify_precondition(["agent:blocked"], comments, "PASS", None)
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_NOW_PASSES)

    def test_duplicate_comment_propagates_even_for_blocked_state(self):
        comments = [_comment(1, self.body), _comment(2, self.body)]
        outcome = classify_precondition(["agent:blocked"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_DUPLICATE)

    def test_ownership_mismatch_propagates(self):
        comments = [_comment(1, self.body, "spoofer")]
        outcome = classify_precondition(["agent:blocked"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_OWNERSHIP_MISMATCH)

    def test_before_booleans_always_present(self):
        outcome = classify_precondition(["agent:ready"], [], "CONTRACT_VIOLATION", None)
        self.assertEqual(outcome.detail["READY_PRESENT"], "true")
        self.assertEqual(outcome.detail["BLOCKED_PRESENT"], "false")

    # -----------------------------------------------------------------
    # AUTO-001-05-03-03C-R6: readyのみ(blocked不在)経路でも、managed
    # comment状態を分類し、PRECONDITION_STATEはNEEDS_WRITEのまま維持しつつ
    # comment_actionを正しく導出する(Run 30676777164の誤検出の根本原因の
    # 単体テスト)。
    # -----------------------------------------------------------------

    def test_ready_only_with_no_comment_is_needs_write_with_create_action(self):
        outcome = classify_precondition(["agent:ready"], [], "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "NONE")
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "CREATE")

    def test_ready_only_with_matching_comment_is_needs_write_with_noop_action(self):
        # Run 30676777164の再現: agent:readyのみ・managed commentがcanonical
        # 一致(MATCHES)。修正前はこの分岐がcomment状態を一切見ずNEEDS_WRITEを
        # 返し、workflow側で「NEEDS_WRITE=comment無しのはず」という誤った
        # 前提によりSTATE_CHANGED_BEFORE_WRITEに誤検出されていた。
        comments = [_comment(1, self.body)]
        outcome = classify_precondition(["agent:ready"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "MATCHES")
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "NOOP")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_ready_only_with_stale_comment_is_needs_write_with_update_action(self):
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        stale_body = self.body.replace(fp, "0" * 64)
        comments = [_comment(1, stale_body)]
        outcome = classify_precondition(["agent:ready"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")
        self.assertEqual(outcome.detail["MANAGED_COMMENT_STATE"], "STALE")
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "UPDATE")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_ready_only_duplicate_comment_fails_closed(self):
        comments = [_comment(1, self.body), _comment(2, self.body)]
        outcome = classify_precondition(["agent:ready"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_DUPLICATE)

    def test_ready_only_ownership_mismatch_fails_closed(self):
        comments = [_comment(1, self.body, "some-spoofer")]
        outcome = classify_precondition(["agent:ready"], comments, "CONTRACT_VIOLATION", SAMPLE_ERRORS)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_OWNERSHIP_MISMATCH)

    def test_ready_only_without_current_errors_keeps_legacy_needs_write(self):
        # current_errorsが利用できない(現状の呼び出し元では起こらない)場合は
        # 従来通りmanaged comment状態を分類しない(既存のtest_ready_only_needs_write
        # と同じ契約を、他のcurrent_status値でも維持する)。
        outcome = classify_precondition(["agent:ready"], [_comment(1, self.body)], "PASS", None)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["PRECONDITION_STATE"], "NEEDS_WRITE")
        self.assertNotIn("MANAGED_COMMENT_STATE", outcome.detail)


# ---------------------------------------------------------------------------
# check_comment_state_unchanged_before_write (AUTO-001-05-03-03C-R6)
# ---------------------------------------------------------------------------

class CheckCommentStateUnchangedBeforeWriteTests(unittest.TestCase):
    """precondition時点の状態(state/count/comment_id)と、書き込み直前に
    再取得した状態を比較する純粋関数の単体テスト。真の状態変化(state・
    count・comment_idのいずれか)だけをSTATE_CHANGED_BEFORE_WRITEとして
    拒否し、それ以外は一致した状態から決定的にcomment_actionを導出する
    ことを検証する。
    """

    def setUp(self):
        self.body = build_canonical_block_comment(SAMPLE_ERRORS)
        self.fp = compute_comment_fingerprint(SAMPLE_ERRORS)

    def test_none_unchanged_yields_create(self):
        outcome = check_comment_state_unchanged_before_write("NONE", 0, None, [], self.fp)
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "CREATE")

    def test_matches_unchanged_yields_noop(self):
        outcome = check_comment_state_unchanged_before_write(
            "MATCHES", 1, 1, [_comment(1, self.body)], self.fp,
        )
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "NOOP")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_stale_unchanged_yields_update(self):
        stale_body = self.body.replace(self.fp, "0" * 64)
        outcome = check_comment_state_unchanged_before_write(
            "STALE", 1, 1, [_comment(1, stale_body)], self.fp,
        )
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.detail["COMMENT_ACTION"], "UPDATE")
        self.assertEqual(outcome.detail["COMMENT_ID"], 1)

    def test_none_to_matches_is_state_changed(self):
        outcome = check_comment_state_unchanged_before_write(
            "NONE", 0, None, [_comment(1, self.body)], self.fp,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.STATE_CHANGED_BEFORE_WRITE)

    def test_matches_to_none_is_state_changed(self):
        outcome = check_comment_state_unchanged_before_write("MATCHES", 1, 1, [], self.fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.STATE_CHANGED_BEFORE_WRITE)

    def test_matches_with_different_comment_id_is_state_changed(self):
        # state/countは一致(MATCHES, 1件)だがcomment_idが変化している
        # ケース(削除+再作成で同じcanonical本文の別commentに置き換わった等)。
        outcome = check_comment_state_unchanged_before_write(
            "MATCHES", 1, 1, [_comment(2, self.body)], self.fp,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.STATE_CHANGED_BEFORE_WRITE)

    def test_stale_to_matches_is_state_changed(self):
        outcome = check_comment_state_unchanged_before_write(
            "STALE", 1, 1, [_comment(1, self.body)], self.fp,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.STATE_CHANGED_BEFORE_WRITE)

    def test_duplicate_at_refetch_fails_regardless_of_precondition_state(self):
        comments = [_comment(1, self.body), _comment(2, self.body)]
        outcome = check_comment_state_unchanged_before_write("NONE", 0, None, comments, self.fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_DUPLICATE)

    def test_ownership_mismatch_at_refetch_fails_regardless_of_precondition_state(self):
        comments = [_comment(1, self.body, "some-spoofer")]
        outcome = check_comment_state_unchanged_before_write("NONE", 0, None, comments, self.fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_OWNERSHIP_MISMATCH)


# ---------------------------------------------------------------------------
# check_block_plan_matches_expected
# ---------------------------------------------------------------------------

class CheckBlockPlanMatchesExpectedTests(unittest.TestCase):

    def test_exact_match_passes(self):
        outcome = check_block_plan_matches_expected(_planner_dict())
        self.assertTrue(outcome.ok)

    def test_would_start_rejected(self):
        outcome = check_block_plan_matches_expected(_planner_dict(decision="WOULD_START"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_would_block_state_rejected(self):
        outcome = check_block_plan_matches_expected(_planner_dict(decision="WOULD_BLOCK_STATE"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_not_applicable_rejected(self):
        outcome = check_block_plan_matches_expected(_planner_dict(decision="NOT_APPLICABLE"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_internal_error_decision_rejected(self):
        outcome = check_block_plan_matches_expected(_planner_dict(decision="INTERNAL_ERROR"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_extra_remove_label_rejected(self):
        outcome = check_block_plan_matches_expected(
            _planner_dict(planned_remove_labels=["agent:ready", "priority:high"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_extra_add_label_rejected(self):
        outcome = check_block_plan_matches_expected(
            _planner_dict(planned_add_labels=["agent:blocked", "agent:review"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_empty_errors_rejected(self):
        outcome = check_block_plan_matches_expected(_planner_dict(errors=[]))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_malformed_error_schema_rejected(self):
        outcome = check_block_plan_matches_expected(
            _planner_dict(errors=[{"code": "X", "message": "y"}])  # sectionキー欠落
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_error_with_unknown_extra_field_rejected(self):
        outcome = check_block_plan_matches_expected(
            _planner_dict(errors=[{"code": "X", "section": None, "message": "y", "extra": "z"}])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_planned_comment_absence_does_not_matter(self):
        # planned_commentはdry-run専用文言であり、03Bのgateはこれを一切要求しない。
        d = _planner_dict()
        d["planned_comment"] = None
        outcome = check_block_plan_matches_expected(d)
        self.assertTrue(outcome.ok)

    def test_not_a_dict_is_response_validation_failed(self):
        outcome = check_block_plan_matches_expected(["not", "a", "dict"])
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)


# ---------------------------------------------------------------------------
# check_errors_match_current: NEEDS_WRITE経路のwriter進行条件
# ---------------------------------------------------------------------------

class CheckErrorsMatchCurrentTests(unittest.TestCase):

    def test_exact_match_passes(self):
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        planner_result = _planner_dict(errors=list(SAMPLE_ERRORS))
        outcome = check_errors_match_current(current_result, planner_result)
        self.assertTrue(outcome.ok)

    def test_element_count_mismatch_rejected(self):
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        planner_result = _planner_dict(errors=[SAMPLE_ERRORS[0]])
        outcome = check_errors_match_current(current_result, planner_result)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_order_mismatch_rejected(self):
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        planner_result = _planner_dict(errors=list(reversed(SAMPLE_ERRORS)))
        outcome = check_errors_match_current(current_result, planner_result)
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_code_mismatch_rejected(self):
        altered = [dict(SAMPLE_ERRORS[0], code="DIFFERENT_CODE"), SAMPLE_ERRORS[1]]
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        outcome = check_errors_match_current(current_result, _planner_dict(errors=altered))
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_section_mismatch_rejected(self):
        altered = [SAMPLE_ERRORS[0], dict(SAMPLE_ERRORS[1], section="別の見出し")]
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        outcome = check_errors_match_current(current_result, _planner_dict(errors=altered))
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_message_mismatch_rejected(self):
        altered = [SAMPLE_ERRORS[0], dict(SAMPLE_ERRORS[1], message="異なるメッセージ。")]
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        outcome = check_errors_match_current(current_result, _planner_dict(errors=altered))
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_duplicate_entry_mismatch_rejected(self):
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        duplicated = [SAMPLE_ERRORS[0], SAMPLE_ERRORS[0]]
        outcome = check_errors_match_current(current_result, _planner_dict(errors=duplicated))
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_current_status_not_contract_violation_rejected(self):
        current_result = {"status": "PASS", "errors": None}
        outcome = check_errors_match_current(current_result, _planner_dict())
        self.assertEqual(outcome.reason_code, ReasonCode.PREFLIGHT_RESULT_MISMATCH)

    def test_planner_errors_not_a_list_is_response_validation_failed(self):
        current_result = {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
        outcome = check_errors_match_current(current_result, _planner_dict(errors="not-a-list"))
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)


# ---------------------------------------------------------------------------
# writer: add / verify / comment create-update / remove / final
# ---------------------------------------------------------------------------

class CheckAddBlockedHttpStatusTests(unittest.TestCase):

    def test_200_passes(self):
        self.assertTrue(check_add_blocked_http_status(200).ok)

    def test_404_fails(self):
        outcome = check_add_blocked_http_status(404)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_ADD_BLOCKED_FAILED)


class VerifyBlockedPresentAfterAddTests(unittest.TestCase):

    def test_present_passes(self):
        self.assertTrue(verify_blocked_present_after_add(["agent:blocked"]).ok)

    def test_absent_fails(self):
        outcome = verify_blocked_present_after_add(["agent:ready"])
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_VERIFICATION_FAILED)


class CommentHttpStatusTests(unittest.TestCase):

    def test_create_200_passes(self):
        self.assertTrue(check_comment_create_http_status(200).ok)

    def test_create_403_fails(self):
        outcome = check_comment_create_http_status(403)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_CREATE_FAILED)

    def test_update_200_passes(self):
        self.assertTrue(check_comment_update_http_status(200).ok)

    def test_update_404_fails(self):
        outcome = check_comment_update_http_status(404)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_UPDATE_FAILED)


class VerifyManagedCommentAfterWriteTests(unittest.TestCase):

    def test_matches_passes(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        outcome = verify_managed_comment_after_write([_comment(1, body)], fp)
        self.assertTrue(outcome.ok)

    def test_stale_fails_verification(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        stale = body.replace(fp, "0" * 64)
        outcome = verify_managed_comment_after_write([_comment(1, stale)], fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_VERIFICATION_FAILED)

    def test_absent_fails_verification(self):
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        outcome = verify_managed_comment_after_write([], fp)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_VERIFICATION_FAILED)

    def test_duplicate_after_write_is_reported_as_duplicate(self):
        body = build_canonical_block_comment(SAMPLE_ERRORS)
        fp = compute_comment_fingerprint(SAMPLE_ERRORS)
        outcome = verify_managed_comment_after_write([_comment(1, body), _comment(2, body)], fp)
        self.assertEqual(outcome.reason_code, ReasonCode.MANAGED_COMMENT_DUPLICATE)


class EvaluateFinalStateTests(unittest.TestCase):

    def setUp(self):
        self.body = build_canonical_block_comment(SAMPLE_ERRORS)
        self.fp = compute_comment_fingerprint(SAMPLE_ERRORS)

    def test_needs_write_full_success(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready", "priority:high"],
            after_labels=["agent:blocked", "priority:high"],
            after_comments=[_comment(1, self.body)],
            expected_fingerprint=self.fp,
            require_label_transition=True,
        )
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_SUCCEEDED)
        self.assertEqual(outcome.detail["MANAGED_COMMENT_COUNT"], 1)

    def test_needs_write_ready_still_present_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready"],
            after_labels=["agent:ready", "agent:blocked"],
            after_comments=[_comment(1, self.body)],
            expected_fingerprint=self.fp,
            require_label_transition=True,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL)

    def test_needs_write_comment_mismatch_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready"],
            after_labels=["agent:blocked"],
            after_comments=[],
            expected_fingerprint=self.fp,
            require_label_transition=True,
        )
        self.assertFalse(outcome.ok)

    def test_needs_write_unrelated_label_lost_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready", "priority:high"],
            after_labels=["agent:blocked"],
            after_comments=[_comment(1, self.body)],
            expected_fingerprint=self.fp,
            require_label_transition=True,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.detail["UNRELATED_PRESERVED"], "false")

    def test_comment_update_required_success(self):
        outcome = evaluate_final_state(
            before_labels=["agent:blocked"],
            after_labels=["agent:blocked"],
            after_comments=[_comment(1, self.body)],
            expected_fingerprint=self.fp,
            require_label_transition=False,
        )
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.COMMENT_UPDATED)

    def test_comment_update_required_label_changed_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:blocked"],
            after_labels=["agent:blocked", "agent:ready"],
            after_comments=[_comment(1, self.body)],
            expected_fingerprint=self.fp,
            require_label_transition=False,
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL)

    def test_comment_update_required_comment_still_stale_is_partial(self):
        stale = self.body.replace(self.fp, "0" * 64)
        outcome = evaluate_final_state(
            before_labels=["agent:blocked"],
            after_labels=["agent:blocked"],
            after_comments=[_comment(1, stale)],
            expected_fingerprint=self.fp,
            require_label_transition=False,
        )
        self.assertFalse(outcome.ok)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-03C-R6: classify_precondition -> check_comment_state_
# unchanged_before_write -> evaluate_final_stateの純粋関数群を実際にその順
# で連結実行するend-to-endテスト。個々の関数は他クラスで単体検証済みのため、
# ここでは関数間の連結だけを対象とする。
# ---------------------------------------------------------------------------

class FullDecisionPipelineEndToEndTests(unittest.TestCase):

    def _pipeline(self, *, initial_comments, final_comments):
        errors = _current_errors(INVALID_ISSUE_BODY)
        fp = compute_comment_fingerprint(errors)

        pre = classify_precondition(["agent:ready"], initial_comments, "CONTRACT_VIOLATION", errors)
        self.assertTrue(pre.ok, pre.detail)
        self.assertEqual(pre.detail["PRECONDITION_STATE"], "NEEDS_WRITE")

        # 競合の無い正常系では、書き込み直前の再取得はprecondition時点と
        # 同じmanaged comment状態を返す。
        unchanged = check_comment_state_unchanged_before_write(
            pre.detail["MANAGED_COMMENT_STATE"], pre.detail["MANAGED_COMMENT_COUNT"],
            pre.detail.get("COMMENT_ID"), initial_comments, fp,
        )
        self.assertTrue(unchanged.ok, unchanged.detail)

        final = evaluate_final_state(
            before_labels=["agent:ready"], after_labels=["agent:blocked"],
            after_comments=final_comments, expected_fingerprint=fp,
            require_label_transition=True,
        )
        return pre, unchanged, final

    def test_e3_initial_create_path_reaches_write_succeeded(self):
        # E3: comment未作成の初回CREATE経路の回帰。
        errors = _current_errors(INVALID_ISSUE_BODY)
        _pre, unchanged, final = self._pipeline(
            initial_comments=[],
            final_comments=[_comment(1, build_canonical_block_comment(errors))],
        )
        self.assertEqual(unchanged.detail["COMMENT_ACTION"], "CREATE")
        self.assertTrue(final.ok, final.detail)
        self.assertEqual(final.reason_code, ReasonCode.WRITE_SUCCEEDED)

    def test_noop_path_reaches_write_succeeded_without_any_comment_change(self):
        # Run 30676777164の再発防止: agent:readyのみ・managed commentが既に
        # canonical一致(MATCHES)の場合でも、誤ってSTATE_CHANGED_BEFORE_WRITE
        # にならず、comment write APIを呼ばずにWRITE_SUCCEEDEDへ到達する。
        errors = _current_errors(INVALID_ISSUE_BODY)
        existing = [_comment(1, build_canonical_block_comment(errors))]
        _pre, unchanged, final = self._pipeline(initial_comments=existing, final_comments=existing)
        self.assertEqual(unchanged.detail["COMMENT_ACTION"], "NOOP")
        self.assertTrue(final.ok, final.detail)
        self.assertEqual(final.reason_code, ReasonCode.WRITE_SUCCEEDED)

    def test_stale_path_reaches_write_succeeded_after_update(self):
        errors = _current_errors(INVALID_ISSUE_BODY)
        fp = compute_comment_fingerprint(errors)
        stale_body = build_canonical_block_comment(errors).replace(fp, "0" * 64)
        _pre, unchanged, final = self._pipeline(
            initial_comments=[_comment(1, stale_body)],
            final_comments=[_comment(1, build_canonical_block_comment(errors))],
        )
        self.assertEqual(unchanged.detail["COMMENT_ACTION"], "UPDATE")
        self.assertTrue(final.ok, final.detail)
        self.assertEqual(final.reason_code, ReasonCode.WRITE_SUCCEEDED)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):

    def _run_cli(self, argv: list[str]) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = cli_main(argv)
        return exit_code, buf.getvalue().strip()

    def test_compute_current_errors_writes_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:ready"], body=INVALID_ISSUE_BODY))
            out_path = tmpdir / "out.json"
            code, out = self._run_cli([
                "compute-current-errors", "--issue-response-file", issue_path,
                "--output-path", str(out_path),
            ])
            self.assertEqual(code, 0)
            self.assertIn("PREFLIGHT_STATUS=CONTRACT_VIOLATION", out)
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "CONTRACT_VIOLATION")
            self.assertIsInstance(data["errors"], list)
            self.assertGreaterEqual(len(data["errors"]), 1)

    def test_compute_current_errors_valid_body_writes_pass_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:ready"], body=VALID_ISSUE_BODY))
            out_path = tmpdir / "out.json"
            code, out = self._run_cli([
                "compute-current-errors", "--issue-response-file", issue_path,
                "--output-path", str(out_path),
            ])
            self.assertEqual(code, 0)
            self.assertIn("PREFLIGHT_STATUS=PASS", out)
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(data["status"], "PASS")
            self.assertIsNone(data["errors"])

    def test_classify_precondition_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:ready"]))
            comments_path = _write_json(tmpdir, "comments.json", [])
            errors_path = _write_json(tmpdir, "errors.json", {"status": "PASS", "errors": None})
            code, out = self._run_cli([
                "classify-precondition",
                "--issue-response-file", issue_path,
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
            ])
            self.assertEqual(code, 0)
            self.assertIn("PRECONDITION_STATE=NEEDS_WRITE", out)

    def test_check_comment_state_unchanged_cli_matches_yields_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            body = build_canonical_block_comment(SAMPLE_ERRORS)
            comments_path = _write_json(
                tmpdir, "comments.json",
                [{"id": 7, "body": body, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}],
            )
            errors_path = _write_json(
                tmpdir, "errors.json", {"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS},
            )
            code, out = self._run_cli([
                "check-comment-state-unchanged",
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
                "--precondition-comment-state", "MATCHES",
                "--precondition-comment-count", "1",
                "--precondition-comment-id", "7",
            ])
            self.assertEqual(code, 0)
            self.assertIn("COMMENT_ACTION=NOOP", out)

    def test_check_comment_state_unchanged_cli_detects_state_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            comments_path = _write_json(tmpdir, "comments.json", [])
            errors_path = _write_json(
                tmpdir, "errors.json", {"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS},
            )
            code, out = self._run_cli([
                "check-comment-state-unchanged",
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
                "--precondition-comment-state", "MATCHES",
                "--precondition-comment-count", "1",
                "--precondition-comment-id", "7",
            ])
            self.assertEqual(code, 1)
            self.assertIn("REASON_CODE=STATE_CHANGED_BEFORE_WRITE", out)

    def test_check_comment_state_unchanged_cli_empty_precondition_id_means_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            comments_path = _write_json(tmpdir, "comments.json", [])
            errors_path = _write_json(
                tmpdir, "errors.json", {"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS},
            )
            code, out = self._run_cli([
                "check-comment-state-unchanged",
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
                "--precondition-comment-state", "NONE",
                "--precondition-comment-count", "0",
                "--precondition-comment-id", "",
            ])
            self.assertEqual(code, 0)
            self.assertIn("COMMENT_ACTION=CREATE", out)

    def test_check_plan_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "planner.json", _planner_dict())
            code, out = self._run_cli(["check-plan", "--planner-json-path", path])
            self.assertEqual(code, 0)

    def test_check_errors_match_cli_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            current_path = _write_json(
                tmpdir, "current.json", {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
            )
            planner_path = _write_json(tmpdir, "planner.json", _planner_dict(errors=list(SAMPLE_ERRORS)))
            code, out = self._run_cli([
                "check-errors-match",
                "--current-errors-path", current_path,
                "--planner-json-path", planner_path,
            ])
            self.assertEqual(code, 0)
            self.assertIn("REASON_CODE=NONE", out)

    def test_check_errors_match_cli_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            current_path = _write_json(
                tmpdir, "current.json", {"status": "CONTRACT_VIOLATION", "errors": list(SAMPLE_ERRORS)}
            )
            planner_path = _write_json(tmpdir, "planner.json", _planner_dict(errors=[SAMPLE_ERRORS[0]]))
            code, out = self._run_cli([
                "check-errors-match",
                "--current-errors-path", current_path,
                "--planner-json-path", planner_path,
            ])
            self.assertEqual(code, 1)
            self.assertIn("REASON_CODE=PREFLIGHT_RESULT_MISMATCH", out)

    def test_classify_precondition_preflight_now_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:blocked"]))
            comments_path = _write_json(tmpdir, "comments.json", [])
            errors_path = _write_json(tmpdir, "errors.json", {"status": "PASS", "errors": None})
            code, out = self._run_cli([
                "classify-precondition",
                "--issue-response-file", issue_path,
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
            ])
            self.assertEqual(code, 0)
            self.assertIn("REASON_CODE=PREFLIGHT_NOW_PASSES", out)

    def test_render_comment_body_never_prints_body(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            errors_path = _write_json(
                tmpdir, "errors.json", {"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS}
            )
            out_path = tmpdir / "body.json"
            code, out = self._run_cli([
                "render-comment-body", "--current-errors-path", errors_path,
                "--output-path", str(out_path),
            ])
            self.assertEqual(code, 0)
            self.assertNotIn("preflight", out)  # stdoutにはOK/REASON_CODEだけ
            written = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertIn("body", written)
            self.assertIn(MANAGED_COMMENT_MARKER, written["body"])

    def test_issue_title_and_body_never_appear_in_cli_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            raw = _issue_response(["agent:ready"])
            raw["title"] = "SECRET-TITLE-MARKER"
            raw["body"] = "SECRET-BODY-MARKER"
            issue_path = _write_json(tmpdir, "issue.json", raw)
            comments_path = _write_json(tmpdir, "comments.json", [])
            errors_path = _write_json(tmpdir, "errors.json", {"status": "PASS", "errors": None})
            code, out = self._run_cli([
                "classify-precondition",
                "--issue-response-file", issue_path,
                "--comments-response-file", comments_path,
                "--current-errors-path", errors_path,
            ])
            self.assertNotIn("SECRET-TITLE-MARKER", out)
            self.assertNotIn("SECRET-BODY-MARKER", out)


# ---------------------------------------------------------------------------
# workflow静的検査
# ---------------------------------------------------------------------------

class WorkflowStaticTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        self.assertTrue(WORKFLOW_PATH.exists())

    def test_only_trigger_is_workflow_dispatch(self):
        m = re.search(r"^on:\n((?:  .+\n|\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        block = m.group(1)
        self.assertIn("workflow_dispatch:", block)
        for forbidden in ("push:", "pull_request:", "issues:", "schedule:", "issue_comment:"):
            self.assertNotIn(forbidden, block)

    def test_github_token_permissions_are_read_only(self):
        for section in (r"^permissions:\n((?:  .+\n)+)", r"^    permissions:\n((?:      .+\n)+)"):
            m = re.search(section, self.text, flags=re.MULTILINE)
            self.assertIsNotNone(m)
            block = m.group(1)
            entries = dict(line.strip().split(":", 1) for line in block.splitlines())
            entries = {k.strip(): v.strip() for k, v in entries.items()}
            self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_no_write_permissions_anywhere(self):
        for section in (r"^permissions:\n((?:  .+\n)+)", r"^    permissions:\n((?:      .+\n)+)"):
            m = re.search(section, self.text, flags=re.MULTILINE)
            self.assertIsNotNone(m)
            block = m.group(1)
            for forbidden in (
                "contents: write", "issues: write", "pull-requests: write",
                "actions: write", "workflows: write", "administration: write",
                "id-token: write",
            ):
                self.assertNotIn(forbidden, block)

    def test_app_token_permission_is_issues_write_only(self):
        self.assertIn("permission-issues: write", self.text)
        for forbidden in (
            "permission-contents:", "permission-pull-requests:", "permission-actions:",
            "permission-administration:", "permission-workflows:", "permission-issues: read",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_create_github_app_token_pinned_to_full_sha(self):
        m = re.search(r"uses: actions/create-github-app-token@([0-9a-f]+) # (v\S+)", self.text)
        self.assertIsNotNone(m)
        sha, tag = m.groups()
        self.assertEqual(len(sha), 40)
        self.assertEqual(tag, "v3.2.0")
        self.assertEqual(sha, "bcd2ba49218906704ab6c1aa796996da409d3eb1")

    def test_token_scoped_to_current_repository_only(self):
        self.assertIn("owner: ${{ github.repository_owner }}", self.text)
        self.assertIn("repositories: ${{ github.event.repository.name }}", self.text)

    def test_does_not_disable_token_revocation(self):
        self.assertNotIn("skip-token-revoke", self.text)

    def test_app_token_not_in_job_wide_env(self):
        self.assertNotIn("\nenv:\n  APP_TOKEN", self.text)
        occurrences = [
            i for i, line in enumerate(self.text.splitlines())
            if "steps.app_write_token.outputs.token" in line
        ]
        self.assertEqual(len(occurrences), 3, "app write tokenの参照箇所が想定と異なります(add/comment/remove)")

    def test_write_endpoints_are_exactly_the_allowlisted_four(self):
        self.assertIn(
            '"https://api.github.com/repos/${{ github.repository }}/issues/'
            '${{ inputs.issue_number }}/labels"',
            self.text,
        )
        self.assertIn(
            '"https://api.github.com/repos/${{ github.repository }}/issues/'
            '${{ inputs.issue_number }}/labels/agent%3Aready"',
            self.text,
        )
        self.assertIn(
            '"https://api.github.com/repos/${{ github.repository }}/issues/'
            '${{ inputs.issue_number }}/comments"',
            self.text,
        )
        self.assertIn(
            '"https://api.github.com/repos/${{ github.repository }}/issues/comments/${comment_id}"',
            self.text,
        )
        self.assertEqual(self.text.count("-X POST"), 2)  # add label, create comment
        self.assertEqual(self.text.count("-X DELETE"), 1)  # remove ready
        self.assertEqual(self.text.count("-X PATCH"), 1)  # update comment
        self.assertNotIn("-X PUT", self.text)

    def test_no_repository_label_mutation_api(self):
        lower = self.text.lower()
        self.assertIn('/repos/${{ github.repository }}/labels/agent%3ablocked"', lower)

    def test_no_issue_edit_or_close_apis(self):
        lower = self.text.lower()
        for forbidden in (
            "gh issue edit", "gh issue close", "gh label",
            "gh pr create", "git push", "git commit",
            "/assignees", "/milestones",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_claude_or_llm_api_usage(self):
        lower = self.text.lower()
        for forbidden in (
            "uses: anthropics/", "uses: claude-code-", "anthropic_api_key",
            "openai_api_key", "claude-code-action", "claude-code-base-action",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_raw_response_body_printed(self):
        for forbidden in ("cat issue_", "cat comments_", "cat comment_body.json", "cat planner_result.json"):
            self.assertNotIn(forbidden, self.text)

    def test_no_issue_body_or_title_expression(self):
        self.assertNotIn("issue.body", self.text)
        self.assertNotIn("issue.title", self.text)

    def test_calls_controller_block_writer_module(self):
        self.assertIn("scripts.controller_block_writer", self.text)

    def test_calls_errors_match_gate_before_token_generation(self):
        # writer進行条件: direct validator errorsとplanner machine_dict.errors
        # の完全一致判定が、check_planステップ(app_write_token生成より前)で
        # 呼ばれていること。
        self.assertIn("scripts.controller_block_writer check-errors-match", self.text)
        errors_match_pos = self.text.index("scripts.controller_block_writer check-errors-match")
        token_gen_pos = self.text.index("Generate Controller App write token")
        self.assertLess(errors_match_pos, token_gen_pos)

    def test_reuses_existing_planner_module(self):
        self.assertIn("scripts.issue_agent_planner", self.text)

    def test_reuses_existing_label_writer_module(self):
        self.assertIn("scripts.controller_label_writer check-repo-label-status", self.text)
        self.assertIn("scripts.controller_label_writer check-state-unchanged", self.text)
        self.assertIn("scripts.controller_label_writer check-remove-http-status", self.text)

    def test_reuses_existing_config_check_module(self):
        self.assertIn("scripts.controller_token_check check-config", self.text)

    def test_snapshot_files_cleaned_up_in_summary_step(self):
        self.assertIn("rm -f issue_snapshot.json", self.text)
        self.assertIn("comment_body.json", self.text)

    def test_summary_step_runs_always(self):
        self.assertIn("if: always()", self.text)
        self.assertNotIn("continue-on-error", self.text)

    def test_add_and_remove_gated_to_needs_write_only(self):
        # agent:blocked追加・agent:ready削除は、NEEDS_WRITE経路だけで実行する
        # (COMMENT_UPDATE_REQUIRED経路ではラベルwriteを一切行わない)。
        m_add = re.search(
            r"- name: Add agent:blocked label and verify\n\s*id: add_and_verify\n\s*if: (.+)\n",
            self.text,
        )
        self.assertIsNotNone(m_add)
        self.assertEqual(m_add.group(1).strip(), "steps.precondition.outputs.state == 'NEEDS_WRITE'")

        m_remove = re.search(
            r"- name: Remove agent:ready label\n\s*id: remove_label\n\s*if: (.+)\n",
            self.text,
        )
        self.assertIsNotNone(m_remove)
        self.assertEqual(m_remove.group(1).strip(), "steps.precondition.outputs.state == 'NEEDS_WRITE'")

    def test_comment_step_gated_to_needs_write_or_comment_update(self):
        m = re.search(
            r"- name: Create or update managed comment and verify\n\s*id: comment_write\n\s*if: (.+)\n",
            self.text,
        )
        self.assertIsNotNone(m)
        self.assertIn("NEEDS_WRITE", m.group(1))
        self.assertIn("COMMENT_UPDATE_REQUIRED", m.group(1))

    def test_no_automatic_retry_loop(self):
        lower = self.text.lower()
        for forbidden in ("for i in 1 2 3", "retry", "until curl", "while true"):
            self.assertNotIn(forbidden, lower)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-03B: GitHub Actions既定shell(`bash --noprofile --norc
# -eo pipefail`)のfail-fast挙動を模したsubprocessテスト。workflow YAMLから
# 各stepの実スクリプトを抽出して実行することで、非ゼロ終了時でも
# reason_codeがGITHUB_OUTPUTへ保存されることを検証する。
#
# `curl`はbash関数として差し替え、実ネットワーク接続は一切行わない。
# credential(実際のGitHub App秘密鍵・token等)は一切使用せず、ダミー文字列
# だけを使う。相対パスのfixtureファイルを扱うstepは、実際のrepository直下
# を汚さないよう、専用の一時ディレクトリをcwdとして実行し、
# `python -m scripts.X`のモジュール解決はPYTHONPATH経由で行う。
# ---------------------------------------------------------------------------

_BASE_SUBSTITUTIONS = {
    "${{ github.repository }}": EXPECTED_FULL_NAME,
    "${{ inputs.issue_number }}": TEST_ISSUE_NUMBER,
}


def _run_bash_script_in_dir(script: str, env: dict, cwd: Path) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".sh", delete=False, encoding="utf-8", newline="\n"
    ) as f:
        f.write(script)
        script_path = f.name
    try:
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-eo", "pipefail", script_path],
            cwd=str(cwd), env=env, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
    finally:
        Path(script_path).unlink()


def _base_env(tmpdir: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT)
    # ネストしたpython呼び出し(scripts.issue_agent_planner等)のstdoutを常に
    # UTF-8で出力させる。Windowsではロケール既定(例: cp932)でエンコードされ、
    # 日本語を含む出力をUTF-8として復号する側(subprocess.run側)で
    # UnicodeDecodeErrorになることがあるため。
    env["PYTHONUTF8"] = "1"
    output_path = tmpdir / "github_output.txt"
    output_path.write_text("", encoding="utf-8")
    env["GITHUB_OUTPUT"] = str(output_path)
    return env


def _extract_block_step(step_id: str, extra_substitutions: dict[str, str] | None = None) -> str:
    subs = dict(_BASE_SUBSTITUTIONS)
    subs.update(extra_substitutions or {})
    return _extract_step_run_lines(WORKFLOW_PATH.read_text(encoding="utf-8"), step_id, substitutions=subs)


def _fake_curl_multi(*, default: dict, **method_configs: dict) -> str:
    """HTTP methodごとに異なる終了コード・HTTPステータス・本文を返せる
    `curl`のbash関数。method_configsのキーはHTTPメソッド名(POST/PATCH/
    DELETE等、大文字)。指定の無いmethodはdefaultを使う。"""
    lines = [
        "curl() {",
        '  local method="GET"',
        '  local out_file=""',
        '  local prev=""',
        '  for arg in "$@"; do',
        '    if [ "$prev" = "-X" ]; then method="$arg"; fi',
        '    if [ "$prev" = "-o" ]; then out_file="$arg"; fi',
        '    prev="$arg"',
        "  done",
        '  case "$method" in',
    ]
    for method, cfg in method_configs.items():
        lines.append(f"    {method})")
        lines.append(f"      body={_bash_single_quote(cfg['body'])}")
        lines.append(f"      http_code={_bash_single_quote(cfg['http_code'])}")
        lines.append(f"      exit_code={int(cfg['exit_code'])}")
        lines.append("      ;;")
    lines.append("    *)")
    lines.append(f"      body={_bash_single_quote(default['body'])}")
    lines.append(f"      http_code={_bash_single_quote(default['http_code'])}")
    lines.append(f"      exit_code={int(default['exit_code'])}")
    lines.append("      ;;")
    lines.append("  esac")
    lines.append("  if [ -n \"$out_file\" ]; then printf '%s' \"$body\" > \"$out_file\"; fi")
    lines.append("  printf '%s' \"$http_code\"")
    lines.append('  return "$exit_code"')
    lines.append("}")
    return "\n".join(lines) + "\n"


def _fake_curl_with_method_log(log_path: Path, *, get_body: str) -> str:
    """全HTTPメソッドを常にHTTP 200・`get_body`で成功させつつ、実際に呼ばれた
    メソッド名(POST/PATCH/GET等、`-X`未指定時はGET)を`log_path`へ1行ずつ
    追記する`curl`のbash関数スタブ。NOOP経路がPOST/PATCHを一切呼ばないことを、
    `--http-status`スタブの有無ではなく実際の呼び出し履歴から確認するために使う。
    """
    return (
        "curl() {\n"
        '  local method="GET"\n'
        '  local out_file=""\n'
        '  local prev=""\n'
        '  for arg in "$@"; do\n'
        '    if [ "$prev" = "-X" ]; then method="$arg"; fi\n'
        '    if [ "$prev" = "-o" ]; then out_file="$arg"; fi\n'
        '    prev="$arg"\n'
        "  done\n"
        f"  echo \"$method\" >> {_bash_single_quote(str(log_path))}\n"
        '  if [ -n "$out_file" ]; then\n'
        f"    printf '%s' {_bash_single_quote(get_body)} > \"$out_file\"\n"
        "  fi\n"
        "  printf '%s' 200\n"
        "  return 0\n"
        "}\n"
    )


class PreconditionSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_block_step("precondition")

    def _run(self, *, curl_exit_code, curl_http_code, issue_body_curl_body, comments_curl_body):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            # precondition callsは順にissue取得・comments取得の2回のGETを行う。
            # 呼び出し順で応答を変えたいので、出力ファイル名(-o)で判定する
            # スタブに差し替える。
            combined = _fake_curl_by_output_file(
                issue_body_curl_body, comments_curl_body, curl_exit_code, curl_http_code
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_ready_only_needs_write(self):
        issue_body = json.dumps(_issue_response(["agent:ready"], body=VALID_ISSUE_BODY))
        result, outputs = self._run(
            curl_exit_code=0, curl_http_code="200",
            issue_body_curl_body=issue_body, comments_curl_body="[]",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("state"), "NEEDS_WRITE")
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_blocked_with_matching_comment_is_noop(self):
        # commentのfingerprintは、実際にINVALID_ISSUE_BODYをvalidatorへ
        # かけたときのerrors(SAMPLE_ERRORSという無関係な固定値ではない)から
        # 計算しなければ、workflow側が再計算するfingerprintと一致しない。
        errors = _current_errors(INVALID_ISSUE_BODY)
        body_text = build_canonical_block_comment(errors)
        issue_body = json.dumps(_issue_response(["agent:blocked"], body=INVALID_ISSUE_BODY))
        comments_body = json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            curl_exit_code=0, curl_http_code="200",
            issue_body_curl_body=issue_body, comments_curl_body=comments_body,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NOOP_ALREADY_APPLIED")

    def test_ready_and_blocked_is_partial_state(self):
        issue_body = json.dumps(_issue_response(["agent:ready", "agent:blocked"], body=INVALID_ISSUE_BODY))
        result, outputs = self._run(
            curl_exit_code=0, curl_http_code="200",
            issue_body_curl_body=issue_body, comments_curl_body="[]",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL_STATE_DETECTED")

    def test_blocked_with_body_now_passing_is_preflight_now_passes(self):
        # Issue本文が修正されerrorsが0件になった場合。token生成なし・
        # blocked追加なし・コメント作成/更新なし・ready削除なしで、
        # 既存のblocked/commentも自動削除しない(03Bは復帰処理を担当しない)。
        issue_body = json.dumps(_issue_response(["agent:blocked"], body=VALID_ISSUE_BODY))
        result, outputs = self._run(
            curl_exit_code=0, curl_http_code="200",
            issue_body_curl_body=issue_body, comments_curl_body="[]",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "PREFLIGHT_NOW_PASSES")
        self.assertEqual(outputs.get("state"), "PREFLIGHT_NOW_PASSES")

    def test_api_failure_is_internal_error(self):
        result, outputs = self._run(
            curl_exit_code=7, curl_http_code="000",
            issue_body_curl_body="", comments_curl_body="",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")

    def test_issue_body_never_leaks(self):
        issue_body = json.dumps(_issue_response(["agent:ready"], body="SECRET-BODY-MARKER" + VALID_ISSUE_BODY))
        result, _outputs = self._run(
            curl_exit_code=0, curl_http_code="200",
            issue_body_curl_body=issue_body, comments_curl_body="[]",
        )
        self.assertNotIn("SECRET-BODY-MARKER", result.stdout)


def _fake_curl_by_output_file(issue_body: str, comments_body: str, exit_code: int, http_code: str) -> str:
    """`-o`引数のファイル名に'comments'を含むかどうかで、issue取得と
    comments取得のレスポンスを切り替える`curl`のbash関数スタブ。"""
    return (
        "curl() {\n"
        '  local out_file=""\n'
        '  local prev=""\n'
        '  for arg in "$@"; do\n'
        '    if [ "$prev" = "-o" ]; then out_file="$arg"; fi\n'
        '    prev="$arg"\n'
        "  done\n"
        '  case "$out_file" in\n'
        "    *comments*)\n"
        f"      body={_bash_single_quote(comments_body)}\n"
        "      ;;\n"
        "    *)\n"
        f"      body={_bash_single_quote(issue_body)}\n"
        "      ;;\n"
        "  esac\n"
        '  if [ -n "$out_file" ] && [ "$out_file" != "/dev/null" ]; then\n'
        '    printf \'%s\' "$body" > "$out_file"\n'
        "  fi\n"
        f"  printf '%s' {_bash_single_quote(http_code)}\n"
        f"  return {int(exit_code)}\n"
        "}\n"
    )


class CheckPlanSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_block_step("check_plan")

    def _run(self, *, issue_labels: list[str], issue_body: str, current_errors_override: dict | None = None):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            event_path = tmpdir / "event.json"
            event_path.write_text("{}", encoding="utf-8")
            env["GITHUB_EVENT_PATH"] = str(event_path)
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(_issue_response(issue_labels, body=issue_body), ensure_ascii=False),
                encoding="utf-8",
            )
            if current_errors_override is not None:
                with open(tmpdir / "current_errors.json", "w", encoding="utf-8") as f:
                    json.dump(current_errors_override, f, ensure_ascii=False)
            else:
                # precondition stepが実際に書き出すのと同じ内容(同一bodyを
                # direct validatorへかけた結果)を再現する。通常はplannerが
                # 独自に再計算するerrorsと一致する。
                _write_current_errors_file(tmpdir / "current_errors.json", issue_body)
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_ready_with_valid_violation_body_passes(self):
        result, outputs = self._run(issue_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_errors_mismatch_with_direct_validator_is_rejected(self):
        # direct validator(current_errors.json)とplannerが独自に再計算する
        # errorsが一致しない場合、writer進行条件を満たさずPREFLIGHT_RESULT_
        # MISMATCHとなり、token生成・write系stepへ進まない。
        mismatched = {
            "status": "CONTRACT_VIOLATION",
            "errors": [{"code": "FAKE_MISMATCHED_CODE", "section": None, "message": "テスト用の不一致データ。"}],
        }
        result, outputs = self._run(
            issue_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            current_errors_override=mismatched,
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "PREFLIGHT_RESULT_MISMATCH")

    def test_ready_with_valid_passing_body_is_rejected(self):
        # preflight合格(WOULD_START)はWOULD_BLOCK_PREFLIGHTではないため拒否する。
        result, outputs = self._run(issue_labels=["agent:ready"], issue_body=VALID_ISSUE_BODY)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PLAN_REJECTED")

    def test_missing_ready_label_is_rejected(self):
        result, outputs = self._run(issue_labels=[], issue_body=INVALID_ISSUE_BODY)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PLAN_REJECTED")

    def test_issue_body_never_leaks(self):
        body = build_body(content={"現在の問題": "SECRET-PROBLEM-MARKER"})
        result, _outputs = self._run(issue_labels=["agent:ready"], issue_body=body)
        self.assertNotIn("SECRET-PROBLEM-MARKER", result.stdout)


class CheckRepoLabelSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_block_step("check_repo_label")

    def _run(self, *, curl_exit_code, curl_http_code):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            combined = _fake_curl_function(
                exit_code=curl_exit_code, http_code=curl_http_code, body=""
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_label_exists_passes(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="200")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_label_missing_fails(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="404")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "TARGET_LABEL_MISSING")


class CheckStateUnchangedSubprocessTests(unittest.TestCase):
    """AUTO-001-05-03-03C-R6: 「Re-fetch issue and comments immediately before
    write」stepが、precondition時点のmanaged comment状態(state/count/
    comment_id)と書き込み直前の再取得結果を比較し、3つすべてが一致する場合
    だけcomment_actionを決定的に導出する(NONE->CREATE, MATCHES->NOOP,
    STALE->UPDATE)こと、およびいずれかが真に変化した場合だけ
    STATE_CHANGED_BEFORE_WRITEとすることを検証する。Run 30676777164の
    誤検出(agent:readyのみ・comment MATCHESという正常系をSTATE_CHANGED_
    BEFORE_WRITEと誤判定していた)の再発防止テストを兼ねる。
    """

    def _run(self, *, before_labels, issue_body, issue_curl_body, comments_curl_body,
              curl_exit_code=0, curl_http_code="200", precondition_state="NEEDS_WRITE",
              precondition_comment_state="NONE", precondition_comment_count="0",
              precondition_comment_id=""):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(_issue_response(before_labels, body=issue_body), ensure_ascii=False),
                encoding="utf-8",
            )
            _write_current_errors_file(tmpdir / "current_errors.json", issue_body)
            script = _extract_block_step(
                "check_state_unchanged",
                {
                    "${{ steps.precondition.outputs.state }}": precondition_state,
                    "${{ steps.precondition.outputs.comment_state }}": precondition_comment_state,
                    "${{ steps.precondition.outputs.comment_count }}": precondition_comment_count,
                    "${{ steps.precondition.outputs.comment_id }}": precondition_comment_id,
                },
            )
            combined = _fake_curl_by_output_file(
                issue_curl_body, comments_curl_body, curl_exit_code, curl_http_code
            ) + "\n" + script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    # -----------------------------------------------------------------
    # 必須テスト1〜3: precondition時点の状態と再取得結果が一致する場合、
    # その状態からcomment_actionを正しく導出する(readyのみ経路)。
    # -----------------------------------------------------------------

    def test_1_ready_only_none_to_none_passes_with_create_action(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body="[]",
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="NONE", precondition_comment_count="0", precondition_comment_id="",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("comment_action"), "CREATE")

    def test_2_ready_only_matches_to_matches_passes_with_noop_action(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 7, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="MATCHES", precondition_comment_count="1", precondition_comment_id="7",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("comment_action"), "NOOP")
        self.assertEqual(outputs.get("comment_id"), "7")

    def test_3_ready_only_stale_to_stale_passes_with_update_action(self):
        errors = _current_errors(INVALID_ISSUE_BODY)
        fp = compute_comment_fingerprint(errors)
        stale_body = build_canonical_block_comment(errors).replace(fp, "0" * 64)
        comments = json.dumps([{"id": 9, "body": stale_body, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="STALE", precondition_comment_count="1", precondition_comment_id="9",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("comment_action"), "UPDATE")
        self.assertEqual(outputs.get("comment_id"), "9")

    # -----------------------------------------------------------------
    # 既存回帰: blocked状態のcomment修復経路(COMMENT_UPDATE_REQUIRED)。
    # -----------------------------------------------------------------

    def test_comment_update_required_still_stale_passes_with_update_action(self):
        errors = _current_errors(INVALID_ISSUE_BODY)
        fp = compute_comment_fingerprint(errors)
        stale_body = build_canonical_block_comment(errors).replace(fp, "0" * 64)
        comments = json.dumps([{"id": 42, "body": stale_body, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:blocked"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:blocked"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="COMMENT_UPDATE_REQUIRED",
            precondition_comment_state="STALE", precondition_comment_count="1", precondition_comment_id="42",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("comment_action"), "UPDATE")
        self.assertEqual(outputs.get("comment_id"), "42")

    def test_needs_write_label_state_changed_fails(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:blocked"], body=INVALID_ISSUE_BODY)),
            comments_curl_body="[]",
            precondition_state="NEEDS_WRITE",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    # -----------------------------------------------------------------
    # 必須テスト9〜12: precondition時点の状態と再取得結果が食い違う場合
    # (真の状態変化)だけをSTATE_CHANGED_BEFORE_WRITEとして拒否する。
    # PRECONDITION_STATE(NEEDS_WRITE)という全体状態だけからは判定しない
    # ことの直接的な証拠(Run 30676777164の誤検出の再発防止)。
    # -----------------------------------------------------------------

    def test_9_none_to_matches_is_state_changed(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="NONE", precondition_comment_count="0", precondition_comment_id="",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    def test_10_matches_to_none_is_state_changed(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body="[]",
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="MATCHES", precondition_comment_count="1", precondition_comment_id="7",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    def test_11_matches_to_different_comment_id_is_state_changed(self):
        # 同じcanonical本文に一致する別のcomment(削除+再作成等)への
        # すり替わりは、MANAGED_COMMENT_STATEだけを見れば両方MATCHESの
        # ままだが、comment_idが変化しているため真の状態変化として拒否する
        # (state/countの一致だけでcomment_actionを決定してはならないことの
        # 直接的な証拠)。
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 99, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="MATCHES", precondition_comment_count="1", precondition_comment_id="7",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    def test_12_stale_to_matches_is_state_changed(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 9, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="STALE", precondition_comment_count="1", precondition_comment_id="9",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    # -----------------------------------------------------------------
    # 必須テスト13・14: 書き込み直前の再取得時点でmanaged commentが重複/
    # author不一致になっていた場合、precondition時点の状態によらず常に
    # Failureとする(自動修復しない)。
    # -----------------------------------------------------------------

    def test_13_duplicate_appearing_before_write_fails(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([
            {"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}},
            {"id": 2, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}},
        ])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="NONE", precondition_comment_count="0", precondition_comment_id="",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "MANAGED_COMMENT_DUPLICATE")

    def test_14_ownership_mismatch_appearing_before_write_fails(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 1, "body": body_text, "user": {"login": "some-spoofer"}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
            precondition_comment_state="NONE", precondition_comment_count="0", precondition_comment_id="",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "MANAGED_COMMENT_OWNERSHIP_MISMATCH")

    def test_api_failure_is_internal_error(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], issue_body=INVALID_ISSUE_BODY,
            issue_curl_body="", comments_curl_body="",
            curl_exit_code=7, curl_http_code="000",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")


class AddAndVerifySubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_block_step("add_and_verify")

    def _run(self, *, post_http_code="200", post_exit_code=0, get_http_code="200",
              get_exit_code=0, get_body=""):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["APP_TOKEN"] = "dummy-app-write-token"
            env["GH_READ_TOKEN"] = "dummy-read-token"
            fake_curl = _fake_curl_multi(
                default={"exit_code": get_exit_code, "http_code": get_http_code, "body": get_body},
                POST={"exit_code": post_exit_code, "http_code": post_http_code, "body": ""},
            )
            combined = fake_curl + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_add_then_verify_success(self):
        get_body = json.dumps(_issue_response(["agent:blocked"]))
        result, outputs = self._run(get_body=get_body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_add_http_failure(self):
        result, outputs = self._run(post_http_code="403")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_ADD_BLOCKED_FAILED")

    def test_add_succeeds_but_blocked_absent_after_refetch(self):
        get_body = json.dumps(_issue_response(["agent:ready"]))
        result, outputs = self._run(get_body=get_body)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_VERIFICATION_FAILED")

    def test_app_token_never_leaks(self):
        get_body = json.dumps(_issue_response(["agent:blocked"]))
        result, _outputs = self._run(get_body=get_body)
        self.assertNotIn("dummy-app-write-token", result.stdout)
        self.assertNotIn("dummy-app-write-token", result.stderr)


class CommentWriteSubprocessTests(unittest.TestCase):

    def _run(self, *, comment_action, comment_id="",
              write_http_code="200", write_exit_code=0,
              get_http_code="200", get_exit_code=0, get_body=""):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["APP_TOKEN"] = "dummy-app-write-token"
            env["GH_READ_TOKEN"] = "dummy-read-token"
            with open(tmpdir / "current_errors.json", "w", encoding="utf-8") as f:
                json.dump({"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS}, f, ensure_ascii=False)
            script = _extract_block_step("comment_write", {
                "${{ steps.check_state_unchanged.outputs.comment_action }}": comment_action,
                "${{ steps.check_state_unchanged.outputs.comment_id }}": comment_id,
            })
            write_method = "POST" if comment_action == "CREATE" else "PATCH"
            fake_curl = _fake_curl_multi(
                default={"exit_code": get_exit_code, "http_code": get_http_code, "body": get_body},
                **{write_method: {"exit_code": write_exit_code, "http_code": write_http_code, "body": ""}},
            )
            combined = fake_curl + "\n" + script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def _matching_comment_response(self) -> str:
        body_text = build_canonical_block_comment(SAMPLE_ERRORS)
        return json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])

    def test_create_then_verify_success(self):
        result, outputs = self._run(comment_action="CREATE", get_body=self._matching_comment_response())
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_update_then_verify_success(self):
        result, outputs = self._run(
            comment_action="UPDATE", comment_id="42", get_body=self._matching_comment_response()
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_create_http_failure(self):
        result, outputs = self._run(comment_action="CREATE", write_http_code="403")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "COMMENT_CREATE_FAILED")

    def test_update_http_failure(self):
        result, outputs = self._run(comment_action="UPDATE", comment_id="42", write_http_code="404")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "COMMENT_UPDATE_FAILED")

    def test_write_succeeds_but_verification_fails(self):
        result, outputs = self._run(comment_action="CREATE", get_body="[]")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "COMMENT_VERIFICATION_FAILED")

    def test_app_token_never_leaks(self):
        result, _outputs = self._run(comment_action="CREATE", get_body=self._matching_comment_response())
        self.assertNotIn("dummy-app-write-token", result.stdout)
        self.assertNotIn("dummy-app-write-token", result.stderr)

    def test_comment_body_never_printed(self):
        result, _outputs = self._run(comment_action="CREATE", get_body=self._matching_comment_response())
        self.assertNotIn(MANAGED_COMMENT_MARKER, result.stdout)

    def test_create_reports_write_api_executed(self):
        result, outputs = self._run(comment_action="CREATE", get_body=self._matching_comment_response())
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("write_api_outcome"), "EXECUTED")

    def test_update_reports_write_api_executed(self):
        result, outputs = self._run(
            comment_action="UPDATE", comment_id="42", get_body=self._matching_comment_response()
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("write_api_outcome"), "EXECUTED")

    # -----------------------------------------------------------------
    # 必須テスト4〜8: comment_action=NOOPの場合、comment write API
    # (POST/PATCHのどちらも)を一切呼ばず、最終comment確認(GET+検証)は
    # 省略しない。件数・comment IDは変化しない。
    # -----------------------------------------------------------------

    def _run_noop(self, *, comment_id="7", get_body):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            log_path = tmpdir / "curl_calls.log"
            env = _base_env(tmpdir)
            env["APP_TOKEN"] = "dummy-app-write-token"
            env["GH_READ_TOKEN"] = "dummy-read-token"
            with open(tmpdir / "current_errors.json", "w", encoding="utf-8") as f:
                json.dump({"status": "CONTRACT_VIOLATION", "errors": SAMPLE_ERRORS}, f, ensure_ascii=False)
            script = _extract_block_step("comment_write", {
                "${{ steps.check_state_unchanged.outputs.comment_action }}": "NOOP",
                "${{ steps.check_state_unchanged.outputs.comment_id }}": comment_id,
            })
            fake_curl = _fake_curl_with_method_log(log_path, get_body=get_body)
            combined = fake_curl + "\n" + script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            methods_called = log_path.read_text(encoding="utf-8").split() if log_path.exists() else []
            return result, outputs, methods_called

    def test_4_noop_never_calls_post(self):
        result, _outputs, methods_called = self._run_noop(
            comment_id="7", get_body=self._matching_comment_response(),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertNotIn("POST", methods_called)

    def test_5_noop_never_calls_patch(self):
        result, _outputs, methods_called = self._run_noop(
            comment_id="7", get_body=self._matching_comment_response(),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertNotIn("PATCH", methods_called)

    def test_noop_reports_write_api_skipped(self):
        result, outputs, _methods_called = self._run_noop(
            comment_id="7", get_body=self._matching_comment_response(),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")
        self.assertEqual(outputs.get("write_api_outcome"), "SKIPPED")

    def test_7_noop_final_comment_count_is_one(self):
        # _matching_comment_response()は正確に1件のcanonical一致commentを
        # 返す(verify-managed-commentがそれをMATCHESとして確認する)。
        result, outputs, _methods_called = self._run_noop(
            comment_id="7", get_body=self._matching_comment_response(),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_8_noop_keeps_same_comment_id(self):
        body_text = build_canonical_block_comment(SAMPLE_ERRORS)
        get_body = json.dumps([{"id": 7, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs, _methods_called = self._run_noop(comment_id="7", get_body=get_body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_noop_with_comment_now_missing_fails_final_verification(self):
        # NOOPの場合も最終comment確認を省略しない: 万一(直前確認と本stepの
        # 間で)commentが消えていた場合はCOMMENT_VERIFICATION_FAILEDとして
        # 検出できる。
        result, outputs, methods_called = self._run_noop(comment_id="7", get_body="[]")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "COMMENT_VERIFICATION_FAILED")
        self.assertNotIn("POST", methods_called)
        self.assertNotIn("PATCH", methods_called)


class RemoveLabelSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_block_step("remove_label")

    def _run(self, *, curl_exit_code, curl_http_code):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["APP_TOKEN"] = "dummy-app-write-token"
            combined = _fake_curl_function(
                exit_code=curl_exit_code, http_code=curl_http_code, body=""
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_200_passes(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="200")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_404_passes(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="404")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_403_is_write_partial(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="403")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")


class EvaluateFinalSubprocessTests(unittest.TestCase):

    def _run(self, *, before_labels, before_body, issue_curl_body, comments_curl_body,
              precondition_state="NEEDS_WRITE", curl_exit_code=0, curl_http_code="200"):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            (tmpdir / "issue_pre_write.json").write_text(
                json.dumps(_issue_response(before_labels, body=before_body), ensure_ascii=False),
                encoding="utf-8",
            )
            _write_current_errors_file(tmpdir / "current_errors.json", before_body)
            script = _extract_block_step(
                "evaluate_final",
                {"${{ steps.precondition.outputs.state }}": precondition_state},
            )
            combined = _fake_curl_by_output_file(
                issue_curl_body, comments_curl_body, curl_exit_code, curl_http_code
            ) + "\n" + script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_needs_write_success(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], before_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:blocked"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_SUCCEEDED")
        self.assertEqual(outputs.get("final_comment_count"), "1")

    def test_needs_write_partial_when_ready_remains(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:ready"], before_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:ready", "agent:blocked"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="NEEDS_WRITE",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")

    def test_comment_update_required_success(self):
        body_text = build_canonical_block_comment(_current_errors(INVALID_ISSUE_BODY))
        comments = json.dumps([{"id": 1, "body": body_text, "user": {"login": MANAGED_COMMENT_AUTHOR_LOGIN}}])
        result, outputs = self._run(
            before_labels=["agent:blocked"], before_body=INVALID_ISSUE_BODY,
            issue_curl_body=json.dumps(_issue_response(["agent:blocked"], body=INVALID_ISSUE_BODY)),
            comments_curl_body=comments,
            precondition_state="COMMENT_UPDATE_REQUIRED",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "COMMENT_UPDATED")

    def test_api_failure_is_write_partial(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], before_body=INVALID_ISSUE_BODY,
            issue_curl_body="", comments_curl_body="",
            precondition_state="NEEDS_WRITE",
            curl_exit_code=7, curl_http_code="000",
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")


_SUMMARY_ENV_KEYS = (
    "PRECONDITION_REASON", "PRECONDITION_STATE", "BEFORE_READY", "BEFORE_BLOCKED",
    "BEFORE_COMMENT_COUNT", "PLAN_REASON", "LABEL_REASON", "STATE_REASON",
    "COMMENT_ACTION", "COMMENT_WRITE_API", "TOKEN_OUTCOME", "ADD_REASON", "COMMENT_WRITE_REASON",
    "REMOVE_REASON", "FINAL_REASON", "FINAL_BLOCKED", "FINAL_READY",
    "FINAL_UNRELATED", "FINAL_COMMENT_OK", "FINAL_COMMENT_COUNT",
)


class SummarySubprocessTests(unittest.TestCase):
    """"Publish job summary" step(id: summary)の実end-to-end検証。upstream
    stepsの出力を模したenv変数を与え、GITHUB_STEP_SUMMARYへ正しいwrite
    outcomeが出力されること、このstep自体は与えたreason_codeの内容に
    関わらず常にexit 0で終了すること(if: always()の意図通り、summary
    step自身の実行結果が先行stepの失敗を上書きしない設計であることの
    傍証)を確認する。credential・raw入力は一切使用しない。
    """

    def setUp(self):
        self.script = _extract_block_step("summary")

    def _run(self, **env_overrides):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            for key in _SUMMARY_ENV_KEYS:
                env[key] = ""
            env.update(env_overrides)
            summary_path = tmpdir / "step_summary.md"
            summary_path.write_text("", encoding="utf-8")
            env["GITHUB_STEP_SUMMARY"] = str(summary_path)
            env["GITHUB_SERVER_URL"] = "https://github.com"
            env["GITHUB_REPOSITORY"] = EXPECTED_FULL_NAME
            env["GITHUB_RUN_ID"] = "12345"
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            summary_text = summary_path.read_text(encoding="utf-8")
            return result, summary_text

    def test_preflight_now_passes_shown_and_step_succeeds(self):
        # precondition stepがPREFLIGHT_NOW_PASSESで成功終了し、後続の
        # token生成・write系stepはすべてskipされた(outputsが空)状態を模す。
        result, summary_text = self._run(PRECONDITION_REASON="PREFLIGHT_NOW_PASSES")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("write outcome: PREFLIGHT_NOW_PASSES", summary_text)

    def test_preflight_result_mismatch_shown_and_step_succeeds(self):
        # precondition stepはNEEDS_WRITEで成功し、check_plan stepが
        # PREFLIGHT_RESULT_MISMATCHで失敗、後続はすべてskipされた状態を模す。
        result, summary_text = self._run(
            PRECONDITION_REASON="NONE", PLAN_REASON="PREFLIGHT_RESULT_MISMATCH",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("write outcome: PREFLIGHT_RESULT_MISMATCH", summary_text)
        # NONEやINTERNAL_ERRORへ置換されていないこと。
        self.assertNotIn("write outcome: NONE", summary_text)
        self.assertNotIn("write outcome: INTERNAL_ERROR", summary_text)

    def test_no_upstream_reason_falls_back_to_none(self):
        result, summary_text = self._run()
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("write outcome: NONE", summary_text)

    def test_summary_never_leaks_credentials_or_raw_input(self):
        result, summary_text = self._run(PRECONDITION_REASON="PREFLIGHT_NOW_PASSES")
        for forbidden in ("APP_TOKEN", "ghs_", "-----BEGIN", "Authorization"):
            self.assertNotIn(forbidden, summary_text)
            self.assertNotIn(forbidden, result.stdout)

    def test_noop_comment_action_and_skipped_write_api_shown(self):
        # AUTO-001-05-03-03C-R6: comment_action=NOOPおよびcomment write API
        # がSkippedであったことを、Summaryから明示的に確認できる。
        result, summary_text = self._run(
            PRECONDITION_REASON="NONE", COMMENT_ACTION="NOOP", COMMENT_WRITE_API="SKIPPED",
            FINAL_REASON="WRITE_SUCCEEDED", FINAL_COMMENT_OK="true", FINAL_COMMENT_COUNT="1",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("comment action: NOOP", summary_text)
        self.assertIn("comment write API: SKIPPED", summary_text)
        self.assertIn("managed comment件数(最終)=1", summary_text)

    def test_create_comment_action_and_executed_write_api_shown(self):
        result, summary_text = self._run(
            PRECONDITION_REASON="NONE", COMMENT_ACTION="CREATE", COMMENT_WRITE_API="EXECUTED",
            FINAL_REASON="WRITE_SUCCEEDED", FINAL_COMMENT_OK="true", FINAL_COMMENT_COUNT="1",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("comment action: CREATE", summary_text)
        self.assertIn("comment write API: EXECUTED", summary_text)


if __name__ == "__main__":
    unittest.main()
