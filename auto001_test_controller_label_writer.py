"""scripts/controller_label_writer.py (AUTO-001-05-03-03A) の単体テスト。

外部API・外部ネットワーク・実際のGitHub App credentialは一切使わない。
純粋関数群の決定論的な判定、CLIの入出力、workflow YAML
(.github/workflows/auto001-controller-write-check.yml)の静的検査、そして
GitHub Actions既定の厳格shell(`bash --noprofile --norc -eo pipefail`)で
実stepスクリプトを抽出実行するsubprocessテストを対象とする。

curlのbash関数スタブ・workflow抽出ヘルパーは、既存の
auto001_test_controller_token_check.pyのものをそのまま再利用し、
別の定義を重複実装しない。
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
    _run_bash_script_strict,
)
from auto001_test_issue_preflight_validator import build_body
from scripts.controller_label_writer import (
    CheckOutcome,
    PreconditionState,
    ReasonCode,
    check_add_label_http_status,
    check_planner_plan_matches_expected,
    check_remove_label_http_status,
    check_repository_label_exists,
    check_state_unchanged_before_write,
    classify_precondition_state,
    evaluate_final_state,
    extract_label_names_from_issue_response,
    main as cli_main,
    verify_label_present_after_add,
)

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto001-controller-write-check.yml"
TEST_ISSUE_NUMBER = "5"


def _issue_response(labels: list[str]) -> dict:
    return {
        "number": int(TEST_ISSUE_NUMBER),
        "state": "open",
        "labels": [{"name": name} for name in labels],
    }


def _write_json(tmpdir: Path, name: str, data) -> str:
    path = tmpdir / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


# ---------------------------------------------------------------------------
# extract_label_names_from_issue_response
# ---------------------------------------------------------------------------

class ExtractLabelNamesTests(unittest.TestCase):

    def test_extracts_names_in_order(self):
        raw = _issue_response(["agent:ready", "priority:high"])
        self.assertEqual(
            extract_label_names_from_issue_response(raw), ["agent:ready", "priority:high"]
        )

    def test_not_a_dict_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response([1, 2, 3]))

    def test_missing_labels_key_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response({"number": 5}))

    def test_labels_not_a_list_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response({"labels": "oops"}))

    def test_label_entry_not_a_dict_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response({"labels": ["oops"]}))

    def test_label_entry_missing_name_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response({"labels": [{}]}))

    def test_label_entry_empty_name_returns_none(self):
        self.assertIsNone(extract_label_names_from_issue_response({"labels": [{"name": ""}]}))


# ---------------------------------------------------------------------------
# classify_precondition_state (final-state no-op / partial state)
# ---------------------------------------------------------------------------

class ClassifyPreconditionStateTests(unittest.TestCase):

    def test_ready_only_needs_write(self):
        self.assertEqual(
            classify_precondition_state(["agent:ready"]), PreconditionState.NEEDS_WRITE
        )

    def test_working_only_already_applied(self):
        self.assertEqual(
            classify_precondition_state(["agent:working"]), PreconditionState.ALREADY_APPLIED
        )

    def test_ready_and_working_partial_state(self):
        self.assertEqual(
            classify_precondition_state(["agent:ready", "agent:working"]),
            PreconditionState.PARTIAL_STATE_DETECTED,
        )

    def test_no_state_labels_needs_write(self):
        self.assertEqual(classify_precondition_state([]), PreconditionState.NEEDS_WRITE)
        self.assertEqual(
            classify_precondition_state(["priority:high"]), PreconditionState.NEEDS_WRITE
        )

    def test_working_with_other_conflict_needs_write_not_noop(self):
        # working+blockedのような想定外の組み合わせは「既に完了済み」とは
        # みなさず、後段のplanner一致判定へ委ねる(NEEDS_WRITE)。
        self.assertEqual(
            classify_precondition_state(["agent:working", "agent:blocked"]),
            PreconditionState.NEEDS_WRITE,
        )

    def test_ready_with_other_conflict_needs_write(self):
        self.assertEqual(
            classify_precondition_state(["agent:ready", "agent:blocked"]),
            PreconditionState.NEEDS_WRITE,
        )

    def test_unrelated_labels_do_not_affect_classification(self):
        self.assertEqual(
            classify_precondition_state(["agent:working", "priority:high", "good-first-issue"]),
            PreconditionState.ALREADY_APPLIED,
        )


# ---------------------------------------------------------------------------
# check_planner_plan_matches_expected
# ---------------------------------------------------------------------------

def _planner_dict(**overrides) -> dict:
    base = {
        "decision": "WOULD_START",
        "applicable": True,
        "planned_remove_labels": ["agent:ready"],
        "planned_add_labels": ["agent:working"],
        "planned_comment": None,
    }
    base.update(overrides)
    return base


class CheckPlannerPlanMatchesExpectedTests(unittest.TestCase):

    def test_exact_match_passes(self):
        outcome = check_planner_plan_matches_expected(_planner_dict())
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)

    def test_not_applicable_rejected(self):
        outcome = check_planner_plan_matches_expected(_planner_dict(decision="NOT_APPLICABLE"))
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_would_block_state_rejected(self):
        outcome = check_planner_plan_matches_expected(_planner_dict(decision="WOULD_BLOCK_STATE"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_would_block_preflight_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(decision="WOULD_BLOCK_PREFLIGHT")
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_internal_error_rejected(self):
        outcome = check_planner_plan_matches_expected(_planner_dict(decision="INTERNAL_ERROR"))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_applicable_false_rejected(self):
        outcome = check_planner_plan_matches_expected(_planner_dict(applicable=False))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_extra_remove_label_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_remove_labels=["agent:ready", "priority:high"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_extra_add_label_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_add_labels=["agent:working", "agent:blocked"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_wrong_remove_label_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_remove_labels=["agent:blocked"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_duplicate_add_label_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_add_labels=["agent:working", "agent:working"])
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_empty_remove_list_rejected(self):
        outcome = check_planner_plan_matches_expected(_planner_dict(planned_remove_labels=[]))
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_planned_comment_present_rejected(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_comment="何らかのコメント予定")
        )
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PLAN_REJECTED)

    def test_not_a_dict_is_response_validation_failed(self):
        outcome = check_planner_plan_matches_expected(["not", "a", "dict"])
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_planned_remove_not_a_list_is_response_validation_failed(self):
        outcome = check_planner_plan_matches_expected(
            _planner_dict(planned_remove_labels="agent:ready")
        )
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)


# ---------------------------------------------------------------------------
# check_state_unchanged_before_write
# ---------------------------------------------------------------------------

class CheckStateUnchangedBeforeWriteTests(unittest.TestCase):

    def test_identical_state_labels_pass(self):
        outcome = check_state_unchanged_before_write(
            ["agent:ready", "priority:high"], ["agent:ready", "other-unrelated"]
        )
        self.assertTrue(outcome.ok)

    def test_state_label_changed_fails(self):
        outcome = check_state_unchanged_before_write(["agent:ready"], ["agent:blocked"])
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.STATE_CHANGED_BEFORE_WRITE)

    def test_state_label_added_fails(self):
        outcome = check_state_unchanged_before_write(
            ["agent:ready"], ["agent:ready", "agent:blocked"]
        )
        self.assertFalse(outcome.ok)

    def test_unrelated_label_change_does_not_affect_result(self):
        outcome = check_state_unchanged_before_write(
            ["agent:ready", "foo"], ["agent:ready", "bar"]
        )
        self.assertTrue(outcome.ok)


# ---------------------------------------------------------------------------
# check_repository_label_exists
# ---------------------------------------------------------------------------

class CheckRepositoryLabelExistsTests(unittest.TestCase):

    def test_200_passes(self):
        self.assertTrue(check_repository_label_exists(200).ok)

    def test_404_is_target_label_missing(self):
        outcome = check_repository_label_exists(404)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.TARGET_LABEL_MISSING)

    def test_other_status_is_internal_error(self):
        outcome = check_repository_label_exists(500)
        self.assertEqual(outcome.reason_code, ReasonCode.INTERNAL_ERROR)


# ---------------------------------------------------------------------------
# writer: add / verify / remove / final
# ---------------------------------------------------------------------------

class CheckAddLabelHttpStatusTests(unittest.TestCase):

    def test_200_passes(self):
        self.assertTrue(check_add_label_http_status(200).ok)

    def test_201_passes(self):
        self.assertTrue(check_add_label_http_status(201).ok)

    def test_404_fails(self):
        outcome = check_add_label_http_status(404)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_ADD_FAILED)

    def test_403_fails(self):
        self.assertEqual(check_add_label_http_status(403).reason_code, ReasonCode.WRITE_ADD_FAILED)


class VerifyLabelPresentAfterAddTests(unittest.TestCase):

    def test_working_present_passes(self):
        self.assertTrue(verify_label_present_after_add(["agent:ready", "agent:working"]).ok)

    def test_working_absent_fails(self):
        outcome = verify_label_present_after_add(["agent:ready"])
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_VERIFICATION_FAILED)


class CheckRemoveLabelHttpStatusTests(unittest.TestCase):

    def test_200_passes(self):
        self.assertTrue(check_remove_label_http_status(200).ok)

    def test_404_passes_defers_to_final_state(self):
        # 対象ラベルが既に存在しない(404)場合、ここでは即失敗にしない。
        self.assertTrue(check_remove_label_http_status(404).ok)

    def test_403_fails(self):
        outcome = check_remove_label_http_status(403)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL)

    def test_500_fails(self):
        self.assertEqual(check_remove_label_http_status(500).reason_code, ReasonCode.WRITE_PARTIAL)


class EvaluateFinalStateTests(unittest.TestCase):

    def test_full_success(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready", "priority:high"],
            after_labels=["agent:working", "priority:high"],
        )
        self.assertTrue(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_SUCCEEDED)
        self.assertEqual(outcome.detail["WORKING_PRESENT"], "true")
        self.assertEqual(outcome.detail["READY_PRESENT"], "false")
        self.assertEqual(outcome.detail["UNRELATED_PRESERVED"], "true")

    def test_remove_404_but_final_state_correct_is_success(self):
        # writerテスト: remove 404後、再取得してfinal状態なら成功扱い可能。
        # (check_remove_label_http_status(404)がokを返すことに加え、
        # evaluate_final_stateが最終状態だけで独立に判定することを確認する)
        outcome = evaluate_final_state(
            before_labels=["agent:ready"], after_labels=["agent:working"]
        )
        self.assertTrue(outcome.ok)

    def test_ready_still_present_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready"], after_labels=["agent:ready", "agent:working"]
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL)

    def test_working_missing_is_partial(self):
        outcome = evaluate_final_state(before_labels=["agent:ready"], after_labels=[])
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.WRITE_PARTIAL)

    def test_other_conflict_present_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready"], after_labels=["agent:working", "agent:blocked"]
        )
        self.assertFalse(outcome.ok)

    def test_unrelated_label_lost_is_partial(self):
        outcome = evaluate_final_state(
            before_labels=["agent:ready", "priority:high"], after_labels=["agent:working"]
        )
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.detail["UNRELATED_PRESERVED"], "false")

    def test_new_unrelated_label_does_not_block_success(self):
        # 実行前に存在しなかった無関係ラベルが増える分には成功条件を妨げない。
        outcome = evaluate_final_state(
            before_labels=["agent:ready"], after_labels=["agent:working", "new-label"]
        )
        self.assertTrue(outcome.ok)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):

    def _run_cli(self, argv: list[str]) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = cli_main(argv)
        return exit_code, buf.getvalue().strip()

    def test_classify_precondition_needs_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "issue.json", _issue_response(["agent:ready"]))
            code, out = self._run_cli(["classify-precondition", "--response-file", path])
        self.assertEqual(code, 0)
        self.assertIn("PRECONDITION_STATE=NEEDS_WRITE", out)

    def test_classify_precondition_already_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "issue.json", _issue_response(["agent:working"]))
            code, out = self._run_cli(["classify-precondition", "--response-file", path])
        self.assertEqual(code, 0)
        self.assertIn("REASON_CODE=NOOP_ALREADY_APPLIED", out)

    def test_classify_precondition_partial_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(
                Path(tmp), "issue.json", _issue_response(["agent:ready", "agent:working"])
            )
            code, out = self._run_cli(["classify-precondition", "--response-file", path])
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=WRITE_PARTIAL_STATE_DETECTED", out)

    def test_classify_precondition_malformed_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "issue.json", {"labels": "oops"})
            code, out = self._run_cli(["classify-precondition", "--response-file", path])
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=RESPONSE_VALIDATION_FAILED", out)

    def test_check_plan_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "planner.json", _planner_dict())
            code, out = self._run_cli(["check-plan", "--planner-json-path", path])
        self.assertEqual(code, 0)
        self.assertIn("REASON_CODE=NONE", out)

    def test_check_plan_reject(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "planner.json", _planner_dict(decision="NOT_APPLICABLE"))
            code, out = self._run_cli(["check-plan", "--planner-json-path", path])
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=WRITE_PLAN_REJECTED", out)

    def test_check_plan_missing_file_is_internal_error(self):
        code, out = self._run_cli(["check-plan", "--planner-json-path", "/nonexistent.json"])
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=INTERNAL_ERROR", out)

    def test_check_repo_label_status(self):
        code, out = self._run_cli(["check-repo-label-status", "--http-status", "404"])
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=TARGET_LABEL_MISSING", out)

    def test_check_state_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            before = _write_json(tmpdir, "before.json", _issue_response(["agent:ready"]))
            current = _write_json(tmpdir, "current.json", _issue_response(["agent:blocked"]))
            code, out = self._run_cli(
                ["check-state-unchanged", "--before-response-file", before,
                 "--current-response-file", current]
            )
        self.assertEqual(code, 1)
        self.assertIn("REASON_CODE=STATE_CHANGED_BEFORE_WRITE", out)

    def test_check_add_http_status(self):
        code, out = self._run_cli(["check-add-http-status", "--http-status", "200"])
        self.assertEqual(code, 0)

    def test_verify_working_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = _write_json(Path(tmp), "issue.json", _issue_response(["agent:working"]))
            code, out = self._run_cli(["verify-working-present", "--response-file", path])
        self.assertEqual(code, 0)

    def test_check_remove_http_status(self):
        code, out = self._run_cli(["check-remove-http-status", "--http-status", "404"])
        self.assertEqual(code, 0)

    def test_evaluate_final_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            before = _write_json(tmpdir, "before.json", _issue_response(["agent:ready", "x"]))
            after = _write_json(tmpdir, "after.json", _issue_response(["agent:working", "x"]))
            code, out = self._run_cli(
                ["evaluate-final-state", "--before-response-file", before,
                 "--after-response-file", after]
            )
        self.assertEqual(code, 0)
        self.assertIn("REASON_CODE=WRITE_SUCCEEDED", out)

    def test_issue_title_and_body_never_appear_in_cli_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            raw = _issue_response(["agent:ready"])
            raw["title"] = "SECRET-TITLE-MARKER"
            raw["body"] = "SECRET-BODY-MARKER"
            path = _write_json(Path(tmp), "issue.json", raw)
            code, out = self._run_cli(["classify-precondition", "--response-file", path])
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
        m = re.search(r"^permissions:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        block = m.group(1)
        entries = dict(line.strip().split(":", 1) for line in block.splitlines())
        entries = {k.strip(): v.strip() for k, v in entries.items()}
        self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_no_write_permissions_anywhere(self):
        # GITHUB_TOKEN用のpermissions:ブロックだけを対象とする
        # (App token用の"permission-issues: write"は許可された別concern)。
        for section in ("^permissions:\n((?:  .+\n)+)", "^    permissions:\n((?:      .+\n)+)"):
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
        self.assertEqual(len(occurrences), 2, "app write tokenの参照箇所が想定と異なります")

    def test_write_endpoints_are_exactly_the_allowlisted_two(self):
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
        self.assertEqual(self.text.count("-X POST"), 1)
        self.assertEqual(self.text.count("-X DELETE"), 1)
        self.assertNotIn("-X PUT", self.text)
        self.assertNotIn("-X PATCH", self.text)

    def test_no_comments_api(self):
        self.assertNotIn("/comments", self.text)

    def test_no_repository_label_mutation_api(self):
        # repository labelへのGETは許可するが、POST/PUT/DELETEでの変更は禁止する。
        lower = self.text.lower()
        self.assertIn('/repos/${{ github.repository }}/labels/agent%3aworking"', lower)
        self.assertNotIn('-x post \\\n            -h "authorization: token ${gh_read_token}"', lower)

    def test_no_issue_edit_or_close_apis(self):
        lower = self.text.lower()
        for forbidden in (
            "gh issue edit", "gh issue close", "gh issue comment", "gh label",
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
        for forbidden in ("cat issue_", "cat planner_result.json"):
            self.assertNotIn(forbidden, self.text)

    def test_no_issue_body_or_title_expression(self):
        self.assertNotIn("issue.body", self.text)
        self.assertNotIn("issue.title", self.text)

    def test_calls_controller_label_writer_module(self):
        self.assertIn("scripts.controller_label_writer", self.text)

    def test_reuses_existing_planner_module(self):
        self.assertIn("scripts.issue_agent_planner", self.text)

    def test_reuses_existing_config_check_module(self):
        self.assertIn("scripts.controller_token_check check-config", self.text)

    def test_snapshot_files_cleaned_up_in_summary_step(self):
        self.assertIn("rm -f issue_snapshot.json", self.text)

    def test_downstream_steps_gated_on_needs_write(self):
        # check_plan・check_repo_label・check_state_unchanged・app_write_token・
        # add_and_verify・remove_label・evaluate_finalの7step。
        self.assertEqual(
            self.text.count("if: steps.precondition.outputs.state == 'NEEDS_WRITE'"), 7
        )

    def test_no_automatic_retry_loop(self):
        # このStageでは自動retryを実装しない設計判断(冪等性検証の複雑化を避ける)。
        lower = self.text.lower()
        for forbidden in ("for i in 1 2 3", "retry", "until curl", "while true"):
            self.assertNotIn(forbidden, lower)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-03A: GitHub Actions既定shell(`bash --noprofile --norc
# -eo pipefail`)のfail-fast挙動を模したsubprocessテスト。workflow YAMLから
# 各stepの実スクリプトを抽出して実行することで、非ゼロ終了時でも
# reason_codeがGITHUB_OUTPUTへ保存されることを検証する(AUTO-001-05-03-02-R1
# で学んだ教訓をこのStageの実装時点から適用済みであることの回帰確認)。
#
# `curl`はbash関数として差し替え、実ネットワーク接続は一切行わない。
# credential(実際のGitHub App秘密鍵・token等)は一切使用せず、ダミー文字列
# だけを使う。相対パスのfixtureファイル(issue_snapshot.json等)を扱うstepは、
# 実際のrepository直下を汚さないよう、専用の一時ディレクトリをcwdとして
# 実行し、`python -m scripts.X`のモジュール解決はPYTHONPATH経由で行う。
# ---------------------------------------------------------------------------

_STEP_SUBSTITUTIONS = {
    "${{ github.repository }}": EXPECTED_FULL_NAME,
    "${{ inputs.issue_number }}": TEST_ISSUE_NUMBER,
}

VALID_ISSUE_BODY = build_body()


def _run_bash_script_in_dir(script: str, env: dict, cwd: Path) -> subprocess.CompletedProcess:
    """`_run_bash_script_strict`と同様だが、cwdを任意のディレクトリへ指定できる。
    相対パスのfixtureファイルを読み書きするstepを、実際のrepository直下を
    汚さずに隔離実行するために使う。`python -m scripts.X`のモジュール解決は
    cwdではなくPYTHONPATH経由で行う(呼び出し側がenv["PYTHONPATH"]を設定する)。
    """
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


def _fake_curl_by_method(*, default: dict, post: dict | None = None) -> str:
    """HTTP methodごとに異なる終了コード・HTTPステータス・本文を返せる
    `curl`のbash関数。add_and_verifyステップ(POST → GETの2回curlを呼ぶ)専用。
    """
    post = post or default
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
        '  if [ "$method" = "POST" ]; then\n'
        f"    body={_bash_single_quote(post['body'])}\n"
        f"    http_code={_bash_single_quote(post['http_code'])}\n"
        f"    exit_code={int(post['exit_code'])}\n"
        "  else\n"
        f"    body={_bash_single_quote(default['body'])}\n"
        f"    http_code={_bash_single_quote(default['http_code'])}\n"
        f"    exit_code={int(default['exit_code'])}\n"
        "  fi\n"
        '  if [ -n "$out_file" ]; then printf \'%s\' "$body" > "$out_file"; fi\n'
        "  printf '%s' \"$http_code\"\n"
        '  return "$exit_code"\n'
        "}\n"
    )


class PreconditionSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "precondition",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(self, *, curl_exit_code: int, curl_http_code: str, curl_body: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            combined = _fake_curl_function(
                exit_code=curl_exit_code, http_code=curl_http_code, body=curl_body
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_api_failure_is_internal_error(self):
        result, outputs = self._run(curl_exit_code=7, curl_http_code="000", curl_body="")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")

    def test_ready_only_needs_write(self):
        body = json.dumps(_issue_response(["agent:ready"]))
        result, outputs = self._run(curl_exit_code=0, curl_http_code="200", curl_body=body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("state"), "NEEDS_WRITE")
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_working_only_is_noop(self):
        body = json.dumps(_issue_response(["agent:working"]))
        result, outputs = self._run(curl_exit_code=0, curl_http_code="200", curl_body=body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("state"), "ALREADY_APPLIED")
        self.assertEqual(outputs.get("reason_code"), "NOOP_ALREADY_APPLIED")

    def test_ready_and_working_is_partial_state(self):
        body = json.dumps(_issue_response(["agent:ready", "agent:working"]))
        result, outputs = self._run(curl_exit_code=0, curl_http_code="200", curl_body=body)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL_STATE_DETECTED")

    def test_malformed_json_is_internal_error(self):
        result, outputs = self._run(
            curl_exit_code=0, curl_http_code="200", curl_body="{not valid json"
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")

    def test_read_token_and_body_never_leak(self):
        raw = _issue_response(["agent:ready"])
        raw["title"] = "SECRET-TITLE-MARKER"
        raw["body"] = "SECRET-BODY-MARKER"
        result, _outputs = self._run(
            curl_exit_code=0, curl_http_code="200", curl_body=json.dumps(raw)
        )
        self.assertNotIn("dummy-read-token", result.stdout)
        self.assertNotIn("SECRET-TITLE-MARKER", result.stdout)
        self.assertNotIn("SECRET-BODY-MARKER", result.stdout)


class CheckPlanSubprocessTests(unittest.TestCase):
    """既存plannerとの厳密一致判定をsubprocess実行する(curlは使わない)。"""

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "check_plan",
        )

    def _run(self, *, issue_labels: list[str], issue_body: str = ""):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            event_path = tmpdir / "event.json"
            event_path.write_text("{}", encoding="utf-8")
            env["GITHUB_EVENT_PATH"] = str(event_path)
            issue_snapshot = _issue_response(issue_labels)
            issue_snapshot["body"] = issue_body
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(issue_snapshot, ensure_ascii=False), encoding="utf-8"
            )
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_ready_with_valid_preflight_body_passes(self):
        result, outputs = self._run(issue_labels=["agent:ready"], issue_body=VALID_ISSUE_BODY)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_missing_ready_label_is_rejected(self):
        result, outputs = self._run(issue_labels=[], issue_body=VALID_ISSUE_BODY)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PLAN_REJECTED")

    def test_preflight_violation_is_rejected(self):
        result, outputs = self._run(issue_labels=["agent:ready"], issue_body="不十分な本文")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PLAN_REJECTED")

    def test_conflicting_state_label_is_rejected(self):
        result, outputs = self._run(
            issue_labels=["agent:ready", "agent:blocked"], issue_body=VALID_ISSUE_BODY
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PLAN_REJECTED")

    def test_issue_body_never_leaks_into_output(self):
        secret_body = build_body(content={"現在の問題": "SECRET-PROBLEM-MARKER"})
        result, _outputs = self._run(issue_labels=["agent:ready"], issue_body=secret_body)
        self.assertNotIn("SECRET-PROBLEM-MARKER", result.stdout)


class CheckRepoLabelSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "check_repo_label",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(self, *, curl_exit_code: int, curl_http_code: str):
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
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_label_missing_fails(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="404")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "TARGET_LABEL_MISSING")

    def test_network_failure_is_internal_error(self):
        result, outputs = self._run(curl_exit_code=7, curl_http_code="000")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")


class CheckStateUnchangedSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "check_state_unchanged",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(self, *, before_labels: list[str], curl_exit_code: int, curl_http_code: str, curl_body: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(_issue_response(before_labels)), encoding="utf-8"
            )
            combined = _fake_curl_function(
                exit_code=curl_exit_code, http_code=curl_http_code, body=curl_body
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_unchanged_state_passes(self):
        body = json.dumps(_issue_response(["agent:ready"]))
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=0, curl_http_code="200", curl_body=body
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_changed_state_fails(self):
        body = json.dumps(_issue_response(["agent:blocked"]))
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=0, curl_http_code="200", curl_body=body
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "STATE_CHANGED_BEFORE_WRITE")

    def test_api_failure_is_internal_error(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=7, curl_http_code="000", curl_body=""
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "INTERNAL_ERROR")


class AddAndVerifySubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "add_and_verify",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(
        self, *, post_exit_code: int = 0, post_http_code: str = "200",
        get_exit_code: int = 0, get_http_code: str = "200", get_body: str = "",
    ):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["APP_TOKEN"] = "dummy-app-write-token"
            env["GH_READ_TOKEN"] = "dummy-read-token"
            fake_curl = _fake_curl_by_method(
                default={"exit_code": get_exit_code, "http_code": get_http_code, "body": get_body},
                post={"exit_code": post_exit_code, "http_code": post_http_code, "body": ""},
            )
            combined = fake_curl + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_add_then_verify_success(self):
        get_body = json.dumps(_issue_response(["agent:ready", "agent:working"]))
        result, outputs = self._run(post_http_code="200", get_http_code="200", get_body=get_body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_add_http_failure(self):
        result, outputs = self._run(post_http_code="404")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_ADD_FAILED")

    def test_add_succeeds_but_refetch_network_fails(self):
        result, outputs = self._run(post_http_code="200", get_exit_code=7, get_http_code="000")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_VERIFICATION_FAILED")

    def test_add_succeeds_but_working_absent_after_refetch(self):
        get_body = json.dumps(_issue_response(["agent:ready"]))
        result, outputs = self._run(post_http_code="200", get_http_code="200", get_body=get_body)
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_VERIFICATION_FAILED")

    def test_app_token_never_appears_in_output(self):
        get_body = json.dumps(_issue_response(["agent:working"]))
        result, _outputs = self._run(post_http_code="200", get_http_code="200", get_body=get_body)
        self.assertNotIn("dummy-app-write-token", result.stdout)
        self.assertNotIn("dummy-app-write-token", result.stderr)


class RemoveLabelSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "remove_label",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(self, *, curl_exit_code: int, curl_http_code: str):
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
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_404_passes(self):
        # idempotency: 対象ラベルが既に存在しない場合でも即失敗にしない。
        result, outputs = self._run(curl_exit_code=0, curl_http_code="404")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_403_is_write_partial(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="403")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")

    def test_network_failure_is_write_partial(self):
        result, outputs = self._run(curl_exit_code=7, curl_http_code="000")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")

    def test_app_token_never_appears_in_output(self):
        result, _outputs = self._run(curl_exit_code=0, curl_http_code="200")
        self.assertNotIn("dummy-app-write-token", result.stdout)
        self.assertNotIn("dummy-app-write-token", result.stderr)


class EvaluateFinalSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "evaluate_final",
            substitutions=_STEP_SUBSTITUTIONS,
        )

    def _run(self, *, before_labels: list[str], curl_exit_code: int, curl_http_code: str, curl_body: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            (tmpdir / "issue_pre_write.json").write_text(
                json.dumps(_issue_response(before_labels)), encoding="utf-8"
            )
            combined = _fake_curl_function(
                exit_code=curl_exit_code, http_code=curl_http_code, body=curl_body
            ) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_success_final_state(self):
        body = json.dumps(_issue_response(["agent:working"]))
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=0, curl_http_code="200", curl_body=body
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_SUCCEEDED")
        self.assertEqual(outputs.get("working_present"), "true")
        self.assertEqual(outputs.get("ready_present"), "false")

    def test_partial_final_state(self):
        body = json.dumps(_issue_response(["agent:ready", "agent:working"]))
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=0, curl_http_code="200", curl_body=body
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")

    def test_unrelated_label_lost_is_partial(self):
        body = json.dumps(_issue_response(["agent:working"]))
        result, outputs = self._run(
            before_labels=["agent:ready", "priority:high"],
            curl_exit_code=0, curl_http_code="200", curl_body=body,
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("unrelated_preserved"), "false")

    def test_final_fetch_failure_is_write_partial(self):
        result, outputs = self._run(
            before_labels=["agent:ready"], curl_exit_code=7, curl_http_code="000", curl_body=""
        )
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "WRITE_PARTIAL")


if __name__ == "__main__":
    unittest.main()
