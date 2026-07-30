"""scripts/controller_token_check.py (AUTO-001-05-03-02) の単体テスト。

外部API・外部ネットワーク・実際のGitHub App credentialは一切使わない。
純粋関数(check_required_config / validate_repository_scope /
validate_issue_read)の決定論的な判定、CLIの入出力、そして対応する
workflow YAML(.github/workflows/auto001-controller-token-check.yml)の
静的検査を対象とする。
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

from scripts.controller_token_check import (
    CheckOutcome,
    ReasonCode,
    check_required_config,
    main as cli_main,
    validate_issue_read,
    validate_repository_scope,
)

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto001-controller-token-check.yml"
EXPECTED_FULL_NAME = "shimomura055/eigo-radio"


# ---------------------------------------------------------------------------
# check_required_config
# ---------------------------------------------------------------------------

class CheckRequiredConfigTests(unittest.TestCase):

    def test_both_present_passes(self):
        outcome = check_required_config(True, True)
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)

    def test_client_id_missing(self):
        outcome = check_required_config(False, True)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.CONFIG_CLIENT_ID_MISSING)

    def test_private_key_missing(self):
        outcome = check_required_config(True, False)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.CONFIG_PRIVATE_KEY_MISSING)

    def test_client_id_checked_before_private_key(self):
        # 両方欠落している場合、client-idの欠落を優先して報告する(判定順序の固定)。
        outcome = check_required_config(False, False)
        self.assertEqual(outcome.reason_code, ReasonCode.CONFIG_CLIENT_ID_MISSING)


# ---------------------------------------------------------------------------
# validate_repository_scope
# ---------------------------------------------------------------------------

class ValidateRepositoryScopeTests(unittest.TestCase):

    def test_exactly_one_matching_repository_passes(self):
        raw = {"total_count": 1, "repositories": [{"full_name": EXPECTED_FULL_NAME}]}
        outcome = validate_repository_scope(raw, EXPECTED_FULL_NAME)
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)
        self.assertEqual(outcome.detail["REPOSITORY_COUNT"], 1)
        self.assertEqual(outcome.detail["MATCHED"], "true")

    def test_zero_repositories_fails(self):
        raw = {"total_count": 0, "repositories": []}
        outcome = validate_repository_scope(raw, EXPECTED_FULL_NAME)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.REPOSITORY_SCOPE_MISMATCH)
        self.assertEqual(outcome.detail["REPOSITORY_COUNT"], 0)

    def test_multiple_repositories_fails(self):
        raw = {
            "total_count": 2,
            "repositories": [
                {"full_name": EXPECTED_FULL_NAME},
                {"full_name": "shimomura055/other-repo"},
            ],
        }
        outcome = validate_repository_scope(raw, EXPECTED_FULL_NAME)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.REPOSITORY_SCOPE_MISMATCH)
        self.assertEqual(outcome.detail["REPOSITORY_COUNT"], 2)

    def test_single_but_mismatched_repository_fails(self):
        raw = {"total_count": 1, "repositories": [{"full_name": "shimomura055/other-repo"}]}
        outcome = validate_repository_scope(raw, EXPECTED_FULL_NAME)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.REPOSITORY_SCOPE_MISMATCH)
        self.assertEqual(outcome.detail["MATCHED"], "false")

    def test_mismatch_detail_never_contains_other_repository_name(self):
        # 不一致の場合でも、実際のrepository名(他repository名を含み得る)を
        # detailへ含めてはならない(件数・真偽値だけを許可する)。
        raw = {"total_count": 1, "repositories": [{"full_name": "shimomura055/other-repo"}]}
        outcome = validate_repository_scope(raw, EXPECTED_FULL_NAME)
        rendered = json.dumps(outcome.detail)
        self.assertNotIn("other-repo", rendered)

    def test_response_not_a_dict_fails_validation(self):
        outcome = validate_repository_scope(["not", "a", "dict"], EXPECTED_FULL_NAME)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_missing_repositories_key_fails_validation(self):
        outcome = validate_repository_scope({"total_count": 1}, EXPECTED_FULL_NAME)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_repositories_not_a_list_fails_validation(self):
        outcome = validate_repository_scope({"repositories": "oops"}, EXPECTED_FULL_NAME)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_repository_entry_not_a_dict_fails_validation(self):
        outcome = validate_repository_scope({"repositories": ["oops"]}, EXPECTED_FULL_NAME)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_repository_entry_missing_full_name_fails_validation(self):
        outcome = validate_repository_scope({"repositories": [{}]}, EXPECTED_FULL_NAME)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_repository_entry_empty_full_name_fails_validation(self):
        outcome = validate_repository_scope({"repositories": [{"full_name": ""}]}, EXPECTED_FULL_NAME)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_empty_expected_full_name_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_repository_scope({"repositories": []}, "")


# ---------------------------------------------------------------------------
# validate_issue_read
# ---------------------------------------------------------------------------

class ValidateIssueReadTests(unittest.TestCase):

    def test_matching_issue_number_passes(self):
        outcome = validate_issue_read({"number": 42, "title": "ignored", "body": "ignored"}, 42)
        self.assertTrue(outcome.ok)
        self.assertIsNone(outcome.reason_code)
        self.assertEqual(outcome.detail["ISSUE_NUMBER_MATCHED"], "true")

    def test_mismatched_issue_number_fails(self):
        outcome = validate_issue_read({"number": 7}, 42)
        self.assertFalse(outcome.ok)
        self.assertEqual(outcome.reason_code, ReasonCode.ISSUE_READ_FAILED)

    def test_body_and_title_never_appear_in_detail(self):
        raw = {"number": 42, "title": "SECRET TITLE", "body": "SECRET BODY"}
        outcome = validate_issue_read(raw, 42)
        rendered = json.dumps(outcome.detail)
        self.assertNotIn("SECRET TITLE", rendered)
        self.assertNotIn("SECRET BODY", rendered)

    def test_response_not_a_dict_fails_validation(self):
        outcome = validate_issue_read([1, 2, 3], 42)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_missing_number_field_fails_validation(self):
        outcome = validate_issue_read({"title": "x"}, 42)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_non_integer_number_field_fails_validation(self):
        outcome = validate_issue_read({"number": "42"}, 42)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_boolean_number_field_fails_validation(self):
        # Pythonではbool is int-subclassのため明示的に弾く必要がある。
        outcome = validate_issue_read({"number": True}, 1)
        self.assertEqual(outcome.reason_code, ReasonCode.RESPONSE_VALIDATION_FAILED)

    def test_zero_expected_issue_number_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_issue_read({"number": 1}, 0)

    def test_negative_expected_issue_number_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_issue_read({"number": 1}, -1)

    def test_non_integer_expected_issue_number_raises_value_error(self):
        with self.assertRaises(ValueError):
            validate_issue_read({"number": 1}, "1")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# CheckOutcome.to_line
# ---------------------------------------------------------------------------

class CheckOutcomeToLineTests(unittest.TestCase):

    def test_pass_line_format(self):
        outcome = CheckOutcome(True, None, {})
        self.assertEqual(outcome.to_line(), "OK=true REASON_CODE=NONE")

    def test_fail_line_includes_sorted_detail_keys(self):
        outcome = CheckOutcome(False, ReasonCode.REPOSITORY_SCOPE_MISMATCH, {"B": 2, "A": 1})
        self.assertEqual(
            outcome.to_line(),
            "OK=false REASON_CODE=REPOSITORY_SCOPE_MISMATCH A=1 B=2",
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):

    def _run_cli(self, argv: list[str]) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exit_code = cli_main(argv)
        return exit_code, buf.getvalue().strip()

    def test_check_config_pass(self):
        exit_code, out = self._run_cli(
            ["check-config", "--client-id-present", "true", "--private-key-present", "true"]
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(out, "OK=true REASON_CODE=NONE")

    def test_check_config_fail(self):
        exit_code, out = self._run_cli(
            ["check-config", "--client-id-present", "false", "--private-key-present", "true"]
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("REASON_CODE=CONFIG_CLIENT_ID_MISSING", out)

    def test_check_config_rejects_non_boolean_literal(self):
        with self.assertRaises(SystemExit):
            self._run_cli(
                ["check-config", "--client-id-present", "yes", "--private-key-present", "true"]
            )

    def test_repo_scope_pass_via_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"repositories": [{"full_name": EXPECTED_FULL_NAME}]}, f)
            path = f.name
        try:
            exit_code, out = self._run_cli(
                ["repo-scope", "--response-file", path, "--expected-full-name", EXPECTED_FULL_NAME]
            )
        finally:
            Path(path).unlink()
        self.assertEqual(exit_code, 0)
        self.assertIn("REPOSITORY_COUNT=1", out)
        self.assertIn("MATCHED=true", out)

    def test_repo_scope_missing_file_is_internal_error(self):
        exit_code, out = self._run_cli(
            ["repo-scope", "--response-file", "/nonexistent/path.json", "--expected-full-name", EXPECTED_FULL_NAME]
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("REASON_CODE=INTERNAL_ERROR", out)

    def test_repo_scope_malformed_json_is_internal_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{not valid json")
            path = f.name
        try:
            exit_code, out = self._run_cli(
                ["repo-scope", "--response-file", path, "--expected-full-name", EXPECTED_FULL_NAME]
            )
        finally:
            Path(path).unlink()
        self.assertEqual(exit_code, 1)
        self.assertIn("REASON_CODE=INTERNAL_ERROR", out)

    def test_issue_read_pass_via_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"number": 42, "title": "unused", "body": "unused"}, f)
            path = f.name
        try:
            exit_code, out = self._run_cli(
                ["issue-read", "--response-file", path, "--expected-issue-number", "42"]
            )
        finally:
            Path(path).unlink()
        self.assertEqual(exit_code, 0)
        self.assertIn("ISSUE_NUMBER_MATCHED=true", out)
        self.assertNotIn("unused", out)

    def test_issue_read_negative_expected_number_is_internal_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"number": 1}, f)
            path = f.name
        try:
            exit_code, out = self._run_cli(
                ["issue-read", "--response-file", path, "--expected-issue-number", "-1"]
            )
        finally:
            Path(path).unlink()
        self.assertEqual(exit_code, 1)
        self.assertIn("REASON_CODE=INTERNAL_ERROR", out)


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
        self.assertIsNotNone(m, "onブロックが見つかりません")
        block = m.group(1)
        self.assertIn("workflow_dispatch:", block)
        for forbidden_trigger in ("push:", "pull_request:", "issues:", "schedule:", "issue_comment:"):
            self.assertNotIn(forbidden_trigger, block)

    def test_has_issue_number_input(self):
        self.assertIn("issue_number:", self.text)
        self.assertIn("required: true", self.text)

    def test_workflow_level_permissions_are_contents_read_only(self):
        m = re.search(r"^permissions:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m, "workflowレベルpermissionsブロックが見つかりません")
        block = m.group(1)
        entries = dict(line.strip().split(":", 1) for line in block.splitlines())
        entries = {k.strip(): v.strip() for k, v in entries.items()}
        self.assertEqual(entries, {"contents": "read"})

    def test_job_level_permissions_are_contents_read_only(self):
        m = re.search(r"^    permissions:\n((?:      .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m, "jobレベルpermissionsブロックが見つかりません")
        block = m.group(1)
        entries = dict(line.strip().split(":", 1) for line in block.splitlines())
        entries = {k.strip(): v.strip() for k, v in entries.items()}
        self.assertEqual(entries, {"contents": "read"})

    def test_no_write_permissions_anywhere(self):
        for forbidden in (
            "contents: write", "issues: write", "pull-requests: write",
            "actions: write", "workflows: write", "administration: write",
            "id-token: write",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_create_github_app_token_pinned_to_full_sha(self):
        m = re.search(
            r"uses: actions/create-github-app-token@([0-9a-f]+) # (v\S+)", self.text
        )
        self.assertIsNotNone(m, "create-github-app-tokenの参照が見つかりません")
        sha, tag = m.groups()
        self.assertEqual(len(sha), 40, "full-length commit SHAではありません")
        self.assertEqual(tag, "v3.2.0")

    def test_uses_client_id_and_repository_secret(self):
        self.assertIn("vars.AUTO001_CONTROLLER_APP_CLIENT_ID", self.text)
        self.assertIn("secrets.AUTO001_CONTROLLER_APP_PRIVATE_KEY", self.text)

    def test_permission_issues_restricted_to_read(self):
        self.assertIn("permission-issues: read", self.text)
        for forbidden_permission in (
            "permission-contents:", "permission-pull-requests:", "permission-actions:",
            "permission-administration:", "permission-workflows:",
        ):
            self.assertNotIn(forbidden_permission, self.text)

    def test_token_scoped_to_current_repository_only(self):
        self.assertIn("owner: ${{ github.repository_owner }}", self.text)
        self.assertIn("repositories: ${{ github.event.repository.name }}", self.text)

    def test_does_not_disable_token_revocation(self):
        self.assertNotIn("skip-token-revoke", self.text)

    def test_no_secrets_leaked_into_job_wide_env(self):
        # jobまたはworkflow直下のenv:ブロック(トップレベル)に secrets./tokenを含めない。
        # (各step個別のenv:ブロックへ限定して渡すことは許可される)
        self.assertNotIn("\nenv:\n  APP_TOKEN", self.text)

    def test_app_token_only_referenced_in_scope_and_issue_steps(self):
        occurrences = [
            i for i, line in enumerate(self.text.splitlines())
            if "steps.app_token.outputs.token" in line
        ]
        self.assertEqual(len(occurrences), 2, "app tokenの参照箇所が想定と異なります")

    def test_no_write_api_endpoints(self):
        lower = self.text.lower()
        for forbidden in (
            "-x post", "-x patch", "-x put", "-x delete",
            "--request post", "--request patch", "--request put", "--request delete",
            "gh issue edit", "gh issue comment", "gh issue close", "gh label",
            "gh pr create", "git push", "git commit",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_raw_response_body_printed(self):
        self.assertNotIn("cat $resp_file", self.text)
        self.assertNotIn("cat \"$resp_file\"", self.text)

    def test_no_issue_body_or_title_expression(self):
        self.assertNotIn("issue.body", self.text)
        self.assertNotIn("issue.title", self.text)

    def test_temp_response_files_are_cleaned_up(self):
        self.assertEqual(self.text.count("trap 'rm -f \"$resp_file\"' EXIT"), 2)

    def test_no_claude_or_llm_api_usage(self):
        lower = self.text.lower()
        for forbidden in (
            "uses: anthropics/", "uses: claude-code-", "anthropic_api_key",
            "openai_api_key", "claude-code-action", "claude-code-base-action",
        ):
            self.assertNotIn(forbidden, lower)

    def test_calls_controller_token_check_module_only(self):
        self.assertIn("scripts.controller_token_check", self.text)

    def test_config_check_guards_command_substitution_with_if(self):
        # AUTO-001-05-03-02-R1: GitHub Actionsの既定shellは最初からerrexit(-e)が
        # 有効なため、`line=$(...)`を素の代入文にすると、非ゼロ終了時に
        # `status=$?`取得前にstepが終了してしまう(run 30510639443で発生)。
        # `if line=$(...); then ... else ... fi`の形でのみ、コマンド置換の
        # 失敗をstep全体の即時終了から保護できる。
        self.assertIn(
            "if line=$(python -m scripts.controller_token_check check-config",
            self.text,
        )

    def test_config_check_reason_code_falls_back_to_internal_error(self):
        self.assertIn('reason_code="INTERNAL_ERROR"', self.text)

    def test_summary_distinguishes_token_generation_skipped_due_to_config_failure(self):
        # 設定検査失敗によりtoken生成がskippedになった場合、Job Summaryに
        # reason_code=NONEを表示しない(固定reason codeで区別する)。
        self.assertIn("TOKEN_GENERATION_SKIPPED_CONFIG_FAILURE", self.text)
        self.assertIn("CONFIG_OUTCOME: ${{ steps.config_check.outcome }}", self.text)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-02-R1: GitHub Actions既定shellのfail-fast挙動を模した
# subprocessテスト。workflow YAMLからconfig_checkステップの実スクリプトを
# 抽出し、`bash --noprofile --norc -eo pipefail`(GitHub Actionsの既定)で
# 実行することで、実際のrun 30510639443で発生した「非ゼロ終了時に
# reason_codeがGITHUB_OUTPUTへ保存されない」問題が再発しないことを検証する。
# credential(実際のGitHub App秘密鍵等)は一切使用せず、ダミー文字列だけを使う。
# ---------------------------------------------------------------------------

def _extract_step_run_lines(text: str, step_id: str) -> str:
    """`id: <step_id>`直後の`run: |`ブロックを、実ファイルからそのまま抽出する。
    抽出したテキストをテストで直接実行することで、workflow本体とテストの
    実装が乖離することを防ぐ。"""
    lines = text.splitlines()
    id_marker = f"id: {step_id}"
    start = next((i for i, line in enumerate(lines) if line.strip() == id_marker), None)
    if start is None:
        raise AssertionError(f"step id={step_id} が見つかりません")

    run_start = next(
        (i + 1 for i in range(start, len(lines)) if lines[i].strip() == "run: |"), None
    )
    if run_start is None:
        raise AssertionError(f"step id={step_id} のrun:ブロックが見つかりません")

    script_lines: list[str] = []
    for line in lines[run_start:]:
        if line.strip() == "":
            script_lines.append("")
            continue
        if not line.startswith(" " * 10):
            break
        script_lines.append(line[10:])
    return "\n".join(script_lines)


def _run_bash_script_strict(script: str, env: dict) -> subprocess.CompletedProcess:
    """GitHub Actionsの既定shell(`bash --noprofile --norc -eo pipefail {0}`)を
    模して、スクリプトを一時ファイル経由で実行する(改行はLFへ固定し、
    Windows上でのCRLF混入によるbashの誤動作を避ける)。"""
    with tempfile.NamedTemporaryFile(
        "w", suffix=".sh", delete=False, encoding="utf-8", newline="\n"
    ) as f:
        f.write(script)
        script_path = f.name
    try:
        return subprocess.run(
            ["bash", "--noprofile", "--norc", "-eo", "pipefail", script_path],
            cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=30,
        )
    finally:
        Path(script_path).unlink()


def _parse_github_output(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not path.exists():
        return result
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = value
    return result


class ConfigCheckFailFastSubprocessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.script = _extract_step_run_lines(
            WORKFLOW_PATH.read_text(encoding="utf-8"), "config_check"
        )

    def _run(self, *, client_id_value: str, private_key_value: str):
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "github_output.txt"
            output_path.write_text("", encoding="utf-8")
            env = dict(os.environ)
            env["CLIENT_ID_VALUE"] = client_id_value
            env["PRIVATE_KEY_VALUE"] = private_key_value
            env["GITHUB_OUTPUT"] = str(output_path)
            result = _run_bash_script_strict(self.script, env)
            outputs = _parse_github_output(output_path)
            return result, outputs

    def test_missing_client_id_saves_reason_code_and_fails(self):
        result, outputs = self._run(client_id_value="", private_key_value="dummy-private-key")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "CONFIG_CLIENT_ID_MISSING")

    def test_missing_private_key_saves_reason_code_and_fails(self):
        result, outputs = self._run(client_id_value="dummy-client-id", private_key_value="")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "CONFIG_PRIVATE_KEY_MISSING")

    def test_both_missing_reports_client_id_first(self):
        result, outputs = self._run(client_id_value="", private_key_value="")
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "CONFIG_CLIENT_ID_MISSING")

    def test_both_present_passes(self):
        result, outputs = self._run(
            client_id_value="dummy-client-id", private_key_value="dummy-private-key"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("reason_code"), "NONE")

    def test_credential_values_never_appear_in_stdout_or_stderr(self):
        result, _outputs = self._run(
            client_id_value="SECRET_CLIENT_ID_MARKER",
            private_key_value="SECRET_PRIVATE_KEY_MARKER",
        )
        self.assertNotIn("SECRET_CLIENT_ID_MARKER", result.stdout)
        self.assertNotIn("SECRET_CLIENT_ID_MARKER", result.stderr)
        self.assertNotIn("SECRET_PRIVATE_KEY_MARKER", result.stdout)
        self.assertNotIn("SECRET_PRIVATE_KEY_MARKER", result.stderr)

    def test_pre_fix_pattern_would_have_failed_this_regression_test(self):
        # 回帰防止用: R1修正前の実装(command substitutionをifで保護しない形)を
        # 同じ厳格shellで実行すると、run 30510639443で実際に発生した通り、
        # reason_codeがGITHUB_OUTPUTへ保存されないままstepが終了することを示す。
        # これにより、本テストクラスが単に無条件で成功するのではなく、
        # 実際に問題を検知できることを示す。
        broken_script = (
            "set -u\n"
            "client_id_present=false\n"
            "private_key_present=false\n"
            'if [ -n "${CLIENT_ID_VALUE:-}" ]; then client_id_present=true; fi\n'
            'if [ -n "${PRIVATE_KEY_VALUE:-}" ]; then private_key_present=true; fi\n'
            "unset CLIENT_ID_VALUE PRIVATE_KEY_VALUE\n"
            "line=$(python -m scripts.controller_token_check check-config "
            '--client-id-present "$client_id_present" '
            '--private-key-present "$private_key_present")\n'
            "status=$?\n"
            'echo "$line"\n'
            "reason_code=$(echo \"$line\" | grep -oP 'REASON_CODE=\\K\\S+')\n"
            'echo "reason_code=${reason_code}" >> "$GITHUB_OUTPUT"\n'
            'if [ "$status" -ne 0 ]; then\n'
            '  echo "::error::設定検査に失敗しました(reason_code=${reason_code})"\n'
            "  exit 1\n"
            "fi\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "github_output.txt"
            output_path.write_text("", encoding="utf-8")
            env = dict(os.environ)
            env["CLIENT_ID_VALUE"] = ""
            env["PRIVATE_KEY_VALUE"] = "dummy-private-key"
            env["GITHUB_OUTPUT"] = str(output_path)
            result = _run_bash_script_strict(broken_script, env)
            outputs = _parse_github_output(output_path)

        self.assertNotEqual(result.returncode, 0)
        # 修正前のパターンでは-eによる即時終了のためreason_codeが保存されない
        # (=このassertは「修正前なら失敗していたはずのテスト」であることを示す)。
        self.assertNotIn("reason_code", outputs)


if __name__ == "__main__":
    unittest.main()
