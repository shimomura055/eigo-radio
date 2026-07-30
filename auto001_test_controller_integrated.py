"""AUTO-001-05-03-03C 統合workflow
(.github/workflows/auto001-controller-integrated.yml)の単体・静的・
subprocessテスト。

このworkflowは、実証済みのread-only planner(scripts.issue_agent_planner)と
Controller App writer(scripts.controller_label_writer /
scripts.controller_block_writer)を、`issues:labeled`実イベントへ安全に統合
する。既存の03A(auto001-controller-write-check.yml)・03B
(auto001-controller-block-check.yml)・read-only dry-run
(auto001-agent-dryrun.yml)のロジック自体は一切変更しないため、それぞれの
既存テストスイートで既に検証済みの決定論的判定・HTTP status判定・comment契約
はここでは再検証しない。このファイルが対象とするのは統合部分だけである。

1. planジョブが`issues:labeled`のうち`agent:ready`だけをapplicableとし、
   working/blocked/無関係ラベルではwriteへ進まないこと(NOT_APPLICABLE/
   WOULD_BLOCK_STATEはwriter_action=NONEで成功終了する)。
2. planからwriterへ渡す値が、exact `WOULD_START`/`WOULD_BLOCK_PREFLIGHT`
   契約に正確に一致する場合だけwriter_actionを設定すること
   (契約不一致はController App token生成前にwriter_action=NONEで停止する)。
3. writer_start/writer_blockの書き込み順序が、03A/03Bのそれと(前置きの
   contract_version確認・issue_number入力検証の位置を除いて)完全一致する
   こと。
4. Controller App token生成(actions/create-github-app-token)がplanジョブ
   には一切現れず、writer_start/writer_blockにだけ現れること。
5. planジョブの`outputs:`がサニタイズ済みスカラーだけであること、writer側が
   `needs.plan.outputs.*`をその許可された名前だけで参照すること。
6. 03A/03Bとの共通concurrency namespaceを使うこと。

外部API・外部ネットワーク・実際のGitHub App credentialは一切使わない。
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

from auto001_test_controller_label_writer import _base_env, _run_bash_script_in_dir
from auto001_test_controller_token_check import (
    EXPECTED_FULL_NAME,
    _extract_step_run_lines,
    _parse_github_output,
)
from auto001_test_issue_preflight_validator import build_body
from scripts.issue_agent_planner import main as planner_main

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
WORKFLOW_PATH = WORKFLOWS_DIR / "auto001-controller-integrated.yml"
WRITE_CHECK_PATH = WORKFLOWS_DIR / "auto001-controller-write-check.yml"
BLOCK_CHECK_PATH = WORKFLOWS_DIR / "auto001-controller-block-check.yml"
DRYRUN_PATH = WORKFLOWS_DIR / "auto001-agent-dryrun.yml"

VALID_ISSUE_BODY = build_body()
INVALID_ISSUE_BODY = build_body(drop={"目的"})


def _write_json(tmpdir: Path, name: str, data) -> str:
    path = tmpdir / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _labeled_event(
    *,
    issue_number: int,
    label: str,
    current_labels: list[str],
    body: str = VALID_ISSUE_BODY,
    state: str = "open",
    is_pull_request: bool = False,
) -> dict:
    issue: dict = {
        "number": issue_number,
        "state": state,
        "labels": [{"name": n} for n in current_labels],
        "body": body,
    }
    if is_pull_request:
        issue["pull_request"] = {"url": "https://api.github.com/repos/x/y/pulls/1"}
    return {"action": "labeled", "label": {"name": label}, "issue": issue}


def _run_planner_like_plan_job(tmpdir: Path, event: dict) -> tuple[dict, int]:
    """planジョブの"Run planner (issues:labeled)"stepと同じCLI引数形状
    (--trigger issues:labeled)でscripts.issue_agent_planner.main()を
    in-process実行し、書き出されたplanner_result.json(machine_dict)を返す。
    """
    event_path = _write_json(tmpdir, "event.json", event)
    machine_path = str(tmpdir / "planner_result.json")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = planner_main([
            "--trigger", "issues:labeled",
            "--event-json-path", event_path,
            "--machine-json-path", machine_path,
        ])
    return json.loads(Path(machine_path).read_text(encoding="utf-8")), code


def _extract_step_names(text: str, job_key: str) -> list[str]:
    """`  <job_key>:`直後から、次の2-space indentのjob keyまたはEOFまでの
    範囲にある`      - name: ...`行を、出現順のリストとして抽出する。"""
    lines = text.splitlines()
    job_marker = f"  {job_key}:"
    start = next((i for i, line in enumerate(lines) if line == job_marker), None)
    if start is None:
        raise AssertionError(f"job {job_key} が見つかりません")
    end = next(
        (i for i in range(start + 1, len(lines))
         if re.match(r"^  \S+:", lines[i])),
        len(lines),
    )
    names = []
    for line in lines[start:end]:
        m = re.match(r"^      - name: (.+)$", line)
        if m:
            names.append(m.group(1))
    return names


def _run_classify_step(tmpdir: Path, planner_result: dict) -> "subprocess.CompletedProcess":
    (tmpdir / "planner_result.json").write_text(
        json.dumps(planner_result, ensure_ascii=False), encoding="utf-8",
    )
    script = _extract_step_run_lines(
        WORKFLOW_PATH.read_text(encoding="utf-8"), "classify",
    )
    env = _base_env(tmpdir)
    return _run_bash_script_in_dir(script, env, tmpdir)


# ---------------------------------------------------------------------------
# 静的構造テスト
# ---------------------------------------------------------------------------

class WorkflowStaticTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        self.assertTrue(WORKFLOW_PATH.exists())

    def test_triggers_are_issues_labeled_and_workflow_dispatch(self):
        m = re.search(r"^on:\n((?:  .+\n|\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        block = m.group(1)
        self.assertIn("issues:", block)
        self.assertIn("labeled", block)
        self.assertIn("workflow_dispatch:", block)
        for forbidden in ("push:", "pull_request:", "schedule:", "issue_comment:"):
            self.assertNotIn(forbidden, block)

    def test_top_level_permissions_are_read_only(self):
        m = re.search(r"^permissions:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        block = m.group(1)
        entries = {
            k.strip(): v.strip()
            for k, v in (line.strip().split(":", 1) for line in block.splitlines())
        }
        self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_no_write_permissions_anywhere(self):
        for m in re.finditer(r"^( *)permissions:\n((?:\1  .+\n)+)", self.text, flags=re.MULTILINE):
            block = m.group(2)
            for forbidden in (
                "contents: write", "issues: write", "pull-requests: write",
                "actions: write", "workflows: write", "administration: write",
                "id-token: write",
            ):
                self.assertNotIn(forbidden, block)

    def test_three_jobs_present(self):
        for job in ("plan:", "writer_start:", "writer_block:"):
            self.assertIn(f"\n  {job}\n", self.text)

    def test_writer_jobs_gated_on_exact_writer_action(self):
        self.assertIn("if: needs.plan.outputs.writer_action == 'START'", self.text)
        self.assertIn("if: needs.plan.outputs.writer_action == 'BLOCK'", self.text)

    def test_create_github_app_token_appears_exactly_twice_pinned(self):
        matches = re.findall(
            r"uses: actions/create-github-app-token@([0-9a-f]+) # (v\S+)", self.text,
        )
        self.assertEqual(len(matches), 2)
        for sha, tag in matches:
            self.assertEqual(len(sha), 40)
            self.assertEqual(tag, "v3.2.0")

    def test_app_token_permission_is_issues_write_only(self):
        self.assertEqual(self.text.count("permission-issues: write"), 2)
        for forbidden in (
            "permission-contents:", "permission-pull-requests:", "permission-actions:",
            "permission-administration:", "permission-workflows:", "permission-issues: read",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_token_scoped_to_current_repository_only(self):
        self.assertEqual(
            self.text.count("owner: ${{ github.repository_owner }}"), 2,
        )
        self.assertEqual(
            self.text.count("repositories: ${{ github.event.repository.name }}"), 2,
        )

    def test_does_not_disable_token_revocation(self):
        self.assertNotIn("skip-token-revoke", self.text)

    def test_app_token_not_in_job_wide_env(self):
        self.assertNotIn("\nenv:\n  APP_TOKEN", self.text)

    def test_no_issue_body_or_title_expression(self):
        self.assertNotIn("issue.body", self.text)
        self.assertNotIn("issue.title", self.text)

    def test_no_issue_edit_close_or_pr_apis(self):
        lower = self.text.lower()
        for forbidden in (
            "gh issue edit", "gh issue close", "gh label",
            "gh pr create", "git push", "git commit",
            "/assignees", "/milestones",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_claude_or_llm_api_usage(self):
        # workflowのコメントは「Claude Code/Anthropic API/OpenAI APIを起動
        # しない」という否定文で言及するため、bare文字列("claude"等)ではなく
        # 実際に起動・認証する具体的なactionやenv var名だけを禁止対象とする
        # (03A/03B/dry-run workflowの既存テストと同じ方針)。
        lower = self.text.lower()
        for forbidden in (
            "uses: anthropics/", "uses: claude-code-", "anthropic_api_key",
            "openai_api_key", "claude-code-action", "claude-code-base-action",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_comment_delete_api(self):
        # commentへのDELETEメソッドが一切登場しないことを確認する
        # (label削除のDELETEは許可対象。comments系URLに対するDELETEが無いことを
        # 個別に確認する)。
        for m in re.finditer(r"-X DELETE[\s\S]{0,400}?\"https://api\.github\.com[^\"]*\"", self.text):
            self.assertNotIn("/comments", m.group(0))

    def test_write_endpoints_allowlist(self):
        # label POST/DELETEはwriter_start/writer_blockそれぞれで1回ずつ(計2回)、
        # comments POST/PATCHはwriter_blockでのみ登場する。
        self.assertEqual(self.text.count("-X POST"), 3)  # label x2 + comment create x1
        self.assertEqual(self.text.count("-X DELETE"), 2)  # agent:ready remove x2
        self.assertEqual(self.text.count("-X PATCH"), 1)  # comment update x1
        self.assertNotIn("-X PUT", self.text)

    def test_no_automatic_retry_or_rollback(self):
        lower = self.text.lower()
        for forbidden in ("for i in 1 2 3", "retry", "until curl", "while true"):
            self.assertNotIn(forbidden, lower)
        # 部分失敗時に直前のadd/writeを取り消す「補償的DELETE/PATCH」が無いこと
        # (agent:ready削除・comment更新以外に、writeロールバック目的のAPI呼び出しは
        # 実装しない)。
        self.assertNotIn("rollback", lower)
        self.assertNotIn("compensat", lower)

    def test_no_raw_response_body_printed(self):
        for forbidden in ("cat issue_", "cat planner_result.json", "cat comments_"):
            self.assertNotIn(forbidden, self.text)


# ---------------------------------------------------------------------------
# plan job -> writer job境界: サニタイズ済みスカラーだけを渡すこと
# ---------------------------------------------------------------------------

class PlanWriterBoundaryTests(unittest.TestCase):

    ALLOWED_OUTPUT_KEYS = {
        "issue_number", "decision", "applicable", "reason_code", "writer_action",
        "planned_add_label", "planned_remove_label", "error_count",
        "error_fingerprint", "contract_version",
    }

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_plan_job_outputs_are_exactly_the_allowlist(self):
        # [^\n]を使い、DOTALLを有効にしても各行の`.+`が改行を越えて
        # ファイル末尾まで貪欲にマッチしないようにする。
        m = re.search(
            r"  plan:\n[\s\S]*?\n    outputs:\n((?:      [^\n]+\n)+)", self.text,
        )
        self.assertIsNotNone(m)
        block = m.group(1)
        keys = set(re.findall(r"^      (\w+):", block, flags=re.MULTILINE))
        self.assertEqual(keys, self.ALLOWED_OUTPUT_KEYS)

    def test_writer_jobs_only_reference_allowlisted_plan_outputs(self):
        referenced = set(re.findall(r"needs\.plan\.outputs\.(\w+)", self.text))
        self.assertTrue(referenced.issubset(self.ALLOWED_OUTPUT_KEYS))
        # writerが実際に参照している値であることも確認する(issue_number/
        # writer_action/contract_versionは書き込み判定・再取得に必須)。
        self.assertIn("issue_number", referenced)
        self.assertIn("writer_action", referenced)
        self.assertIn("contract_version", referenced)

    def test_plan_job_body_never_passes_raw_issue_or_errors_full_text(self):
        plan_block = self.text.split("  writer_start:")[0]
        self.assertNotIn("issue_snapshot", plan_block)
        self.assertNotIn("comments_snapshot", plan_block)
        # errorsの中身(message全文)をGITHUB_OUTPUTへ書き出していないこと。
        # error_countとerror_fingerprint(sha256)だけが許可される。
        self.assertNotIn('errors[', plan_block)

    def test_plan_job_never_generates_app_token(self):
        plan_block = self.text.split("  writer_start:")[0]
        self.assertNotIn("create-github-app-token", plan_block)
        self.assertNotIn("AUTO001_CONTROLLER_APP_PRIVATE_KEY", plan_block)
        self.assertNotIn("AUTO001_CONTROLLER_APP_CLIENT_ID", plan_block)

    def test_only_writer_jobs_generate_app_token(self):
        writer_start_block = self.text.split("  writer_start:")[1].split("  writer_block:")[0]
        writer_block_block = self.text.split("  writer_block:")[1]
        self.assertIn("create-github-app-token", writer_start_block)
        self.assertIn("create-github-app-token", writer_block_block)

    def test_writer_jobs_verify_contract_version_before_any_other_step(self):
        for job_key in ("writer_start", "writer_block"):
            names = _extract_step_names(self.text, job_key)
            self.assertEqual(names[0], "Verify plan/writer contract_version matches expected")
            # このstepより前にtoken生成やcurlが無いこと(tokenへ辿り着く前段の
            # 最初のgateであること)。
            job_marker = f"  {job_key}:"
            start = self.text.index(f"\n{job_marker}\n")
            first_step_idx = self.text.index("- name: Verify plan/writer contract_version", start)
            prelude = self.text[start:first_step_idx]
            self.assertNotIn("create-github-app-token", prelude)


# ---------------------------------------------------------------------------
# concurrency: 03A/03B/統合workflow(writer_start/writer_block)の
# 共通namespace
# ---------------------------------------------------------------------------

class ConcurrencyNamespaceTests(unittest.TestCase):

    GROUP_TEMPLATE_PREFIX = "auto001-controller-write-${{ github.repository }}-"

    def _group_line(self, text: str, *, occurrence: int = 0) -> str:
        matches = re.findall(r"group: (auto001-controller-write-.+)", text)
        return matches[occurrence]

    def test_write_check_03a_uses_shared_namespace(self):
        text = WRITE_CHECK_PATH.read_text(encoding="utf-8")
        group = self._group_line(text)
        self.assertTrue(group.startswith(self.GROUP_TEMPLATE_PREFIX))
        self.assertIn("${{ inputs.issue_number }}", group)

    def test_block_check_03b_uses_shared_namespace(self):
        text = BLOCK_CHECK_PATH.read_text(encoding="utf-8")
        group = self._group_line(text)
        self.assertTrue(group.startswith(self.GROUP_TEMPLATE_PREFIX))
        self.assertIn("${{ inputs.issue_number }}", group)

    def test_integrated_writer_jobs_use_shared_namespace(self):
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        groups = re.findall(r"group: (auto001-controller-write-\$\{\{.+\})", text)
        # writer_start, writer_blockの2箇所
        self.assertEqual(len(groups), 2)
        for group in groups:
            self.assertTrue(group.startswith(self.GROUP_TEMPLATE_PREFIX))
            self.assertIn("${{ needs.plan.outputs.issue_number }}", group)

    def test_cancel_in_progress_false_everywhere(self):
        for path in (WRITE_CHECK_PATH, BLOCK_CHECK_PATH, WORKFLOW_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertGreater(text.count("cancel-in-progress: false"), 0)
            self.assertNotIn("cancel-in-progress: true", text)


# ---------------------------------------------------------------------------
# 書き込み順序の03A/03Bとの一致(前置きstepを除く)
# ---------------------------------------------------------------------------

class WriteOrderRegressionTests(unittest.TestCase):

    # Checkout/Set up Pythonは、03A/03Bと統合workflowの両方で常に先頭2step
    # として存在するが、その直後に来るstep("Validate issue_number input
    # format"または"Verify plan/writer contract_version matches expected")
    # だけが異なるため、以降の共通部分だけをここに定義する。
    COMMON_START_STEPS = [
        "Verify required configuration is present",
        "Fetch current issue state and classify precondition",
        "Run planner and check exact write plan",
        "Verify repository has the agent:working label (read-only)",
        "Re-fetch issue immediately before write",
        "Generate Controller App write token",
        "Add agent:working label and verify",
        "Remove agent:ready label",
        "Evaluate final state",
        "Publish job summary (fixed non-secret fields only)",
    ]

    COMMON_BLOCK_STEPS = [
        "Verify required configuration is present",
        "Fetch issue and comments, classify precondition",
        "Run planner and check exact block plan",
        "Verify repository has the agent:blocked label (read-only)",
        "Re-fetch issue and comments immediately before write",
        "Generate Controller App write token",
        "Add agent:blocked label and verify",
        "Create or update managed comment and verify",
        "Remove agent:ready label",
        "Evaluate final state",
        "Publish job summary (fixed non-secret fields only)",
    ]

    def test_03a_step_order_is_validate_then_common_sequence(self):
        names = _extract_step_names(
            WRITE_CHECK_PATH.read_text(encoding="utf-8"), "write_check",
        )
        self.assertEqual(
            names,
            ["Checkout", "Set up Python 3.12", "Validate issue_number input format"]
            + self.COMMON_START_STEPS,
        )

    def test_03b_step_order_is_validate_then_common_sequence(self):
        names = _extract_step_names(
            BLOCK_CHECK_PATH.read_text(encoding="utf-8"), "block_check",
        )
        self.assertEqual(
            names,
            ["Checkout", "Set up Python 3.12", "Validate issue_number input format"]
            + self.COMMON_BLOCK_STEPS,
        )

    def test_writer_start_step_order_matches_03a_common_sequence(self):
        names = _extract_step_names(WORKFLOW_PATH.read_text(encoding="utf-8"), "writer_start")
        self.assertEqual(
            names,
            ["Verify plan/writer contract_version matches expected", "Checkout", "Set up Python 3.12"]
            + self.COMMON_START_STEPS,
        )

    def test_writer_block_step_order_matches_03b_common_sequence(self):
        names = _extract_step_names(WORKFLOW_PATH.read_text(encoding="utf-8"), "writer_block")
        self.assertEqual(
            names,
            ["Verify plan/writer contract_version matches expected", "Checkout", "Set up Python 3.12"]
            + self.COMMON_BLOCK_STEPS,
        )

    def test_writer_start_invokes_same_cli_subcommands_in_order_as_03a(self):
        pattern = re.compile(r"scripts\.controller_label_writer (\S+)")
        a_calls = pattern.findall(WRITE_CHECK_PATH.read_text(encoding="utf-8"))
        integrated_calls = pattern.findall(
            WORKFLOW_PATH.read_text(encoding="utf-8").split("  writer_start:")[1].split("  writer_block:")[0]
        )
        self.assertEqual(integrated_calls, a_calls)

    def test_writer_block_invokes_same_cli_subcommands_in_order_as_03b(self):
        pattern = re.compile(r"scripts\.controller_block_writer (\S+)")
        b_calls = pattern.findall(BLOCK_CHECK_PATH.read_text(encoding="utf-8"))
        integrated_calls = pattern.findall(
            WORKFLOW_PATH.read_text(encoding="utf-8").split("  writer_block:")[1]
        )
        self.assertEqual(integrated_calls, b_calls)


# ---------------------------------------------------------------------------
# 既存read-only dry-run workflowは変更しない(writerが接続されていないこと)
# ---------------------------------------------------------------------------

class DryRunWorkflowUntouchedTests(unittest.TestCase):

    def test_dryrun_workflow_still_read_only(self):
        text = DRYRUN_PATH.read_text(encoding="utf-8")
        self.assertNotIn("create-github-app-token", text)
        self.assertNotIn("-X POST", text)
        self.assertNotIn("-X DELETE", text)
        self.assertNotIn("-X PATCH", text)
        m = re.search(r"^permissions:\n((?:  .+\n)+)", text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        entries = {
            k.strip(): v.strip()
            for k, v in (line.strip().split(":", 1) for line in m.group(1).splitlines())
        }
        self.assertEqual(entries, {"contents": "read", "issues": "read"})


# ---------------------------------------------------------------------------
# classify step(plan -> writer gate)のsubprocess挙動テスト
# ---------------------------------------------------------------------------

class ClassifyStepFixtureTests(unittest.TestCase):
    """`Determine writer_action from planner result`stepを、実際のCLI
    (scripts.controller_label_writer/controller_block_writer のcheck-plan)
    を経由してsubprocess実行し、planner_result.jsonの各パターンに対する
    writer_action・exit codeを検証する。"""

    def _fixture(self, **overrides) -> dict:
        base = {
            "issue_number": 42,
            "decision": "WOULD_START",
            "applicable": True,
            "preflight_valid": True,
            "current_labels": ["agent:ready"],
            "planned_remove_labels": ["agent:ready"],
            "planned_add_labels": ["agent:working"],
            "planned_comment": None,
            "errors": [],
            "reason": "preflight_pass",
        }
        base.update(overrides)
        return base

    def _run(self, fixture: dict):
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_classify_step(Path(tmp), fixture)
            output = _parse_github_output(Path(tmp) / "github_output.txt")
            return proc, output

    def test_exact_would_start_yields_writer_action_start(self):
        proc, output = self._run(self._fixture())
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "START")
        self.assertEqual(output.get("decision"), "WOULD_START")
        self.assertEqual(output.get("planned_add_label"), "agent:working")
        self.assertEqual(output.get("planned_remove_label"), "agent:ready")

    def test_exact_would_block_preflight_yields_writer_action_block(self):
        fixture = self._fixture(
            decision="WOULD_BLOCK_PREFLIGHT",
            preflight_valid=False,
            planned_add_labels=["agent:blocked"],
            planned_comment="dry-run text",
            errors=[{"code": "MISSING_HEADING", "section": None, "message": "必須の見出しが見つかりません。"}],
            reason="preflight_contract_violation",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "BLOCK")
        self.assertEqual(output.get("error_count"), "1")
        self.assertNotEqual(output.get("error_fingerprint"), "NONE")

    def test_not_applicable_yields_writer_action_none_and_success(self):
        fixture = self._fixture(
            decision="NOT_APPLICABLE", applicable=False, preflight_valid=None,
            planned_remove_labels=[], planned_add_labels=[], reason="label_not_agent_ready",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_would_block_state_yields_writer_action_none_and_success(self):
        fixture = self._fixture(
            decision="WOULD_BLOCK_STATE", preflight_valid=None,
            planned_remove_labels=[], planned_add_labels=[], reason="issue_closed",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_internal_error_yields_writer_action_none_and_step_failure(self):
        fixture = self._fixture(
            decision="INTERNAL_ERROR", applicable=False, preflight_valid=None,
            planned_remove_labels=[], planned_add_labels=[],
            errors=[{"code": "INTERNAL_ERROR", "section": None, "message": "x"}],
            reason="cli_setup_error",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_would_start_with_extra_planned_label_is_rejected(self):
        # plannerが本来出さないはずの、余分なラベルを含む計画(改ざん・不具合
        # 想定)はcheck-planが厳密一致で拒否し、writer_actionはNONEのまま。
        fixture = self._fixture(planned_add_labels=["agent:working", "extra:label"])
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_would_block_preflight_with_zero_errors_is_rejected(self):
        fixture = self._fixture(
            decision="WOULD_BLOCK_PREFLIGHT", preflight_valid=False,
            planned_add_labels=["agent:blocked"], errors=[],
            reason="preflight_contract_violation",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_unknown_decision_string_is_rejected(self):
        fixture = self._fixture(decision="SOMETHING_ELSE")
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")


# ---------------------------------------------------------------------------
# event gate end-to-end(実plannerCLI + classify step)
# ---------------------------------------------------------------------------

class EventGateEndToEndTests(unittest.TestCase):
    """実際のscripts.issue_agent_planner.main()(plan jobの"Run planner
    (issues:labeled)"stepと同じ呼び出し)を経由し、その出力をclassify stepへ
    渡す完全なplan job相当のパイプラインをテストする。"""

    def _run(self, event: dict):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            planner_result, planner_code = _run_planner_like_plan_job(tmpdir, event)
            proc = _run_classify_step(tmpdir, planner_result)
            output = _parse_github_output(tmpdir / "github_output.txt")
            return planner_result, planner_code, proc, output

    def test_agent_ready_label_with_valid_body_starts(self):
        event = _labeled_event(
            issue_number=101, label="agent:ready",
            current_labels=["agent:ready"], body=VALID_ISSUE_BODY,
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "WOULD_START")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "START")
        self.assertEqual(output.get("issue_number"), "101")

    def test_agent_ready_label_with_invalid_body_blocks(self):
        event = _labeled_event(
            issue_number=102, label="agent:ready",
            current_labels=["agent:ready"], body=INVALID_ISSUE_BODY,
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "WOULD_BLOCK_PREFLIGHT")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "BLOCK")

    def test_agent_working_label_is_not_applicable(self):
        event = _labeled_event(
            issue_number=103, label="agent:working",
            current_labels=["agent:working"],
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "NOT_APPLICABLE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_agent_blocked_label_is_not_applicable(self):
        event = _labeled_event(
            issue_number=104, label="agent:blocked",
            current_labels=["agent:blocked"],
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "NOT_APPLICABLE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_unrelated_label_is_not_applicable(self):
        event = _labeled_event(
            issue_number=105, label="documentation",
            current_labels=["documentation"],
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "NOT_APPLICABLE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_agent_ready_on_closed_issue_blocks_state_not_write(self):
        event = _labeled_event(
            issue_number=106, label="agent:ready",
            current_labels=["agent:ready"], state="closed",
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "WOULD_BLOCK_STATE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_agent_ready_double_invocation_blocks_state_not_write(self):
        # agent:ready付与時点で既にagent:workingが付いている(二重起動)場合、
        # 競合状態ラベルとしてWOULD_BLOCK_STATEになり、writerは起動しない。
        event = _labeled_event(
            issue_number=107, label="agent:ready",
            current_labels=["agent:ready", "agent:working"],
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "WOULD_BLOCK_STATE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_pull_request_with_agent_ready_label_is_not_applicable(self):
        event = _labeled_event(
            issue_number=108, label="agent:ready",
            current_labels=["agent:ready"], is_pull_request=True,
        )
        planner_result, planner_code, proc, output = self._run(event)
        self.assertEqual(planner_result["decision"], "NOT_APPLICABLE")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")


if __name__ == "__main__":
    unittest.main()
