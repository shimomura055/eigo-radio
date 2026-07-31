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


def _extract_job_block(text: str, job_key: str) -> str:
    """`  <job_key>:`行から、次の2-space indentのjob key行またはEOFまでの
    範囲を、そのままの行(2-space indent自身も含む)で返す。job単位の
    `uses:`/`with:`/`secrets:`/`permissions:`/`concurrency:`等を、他job分と
    混同せず個別に検査するための最小限のブロック抽出。YAML parserは使わず
    (実CIのrequirements-ci.txtにpyyaml依存が無いため)、既存の
    `_extract_step_names`と同じ行ベースの境界判定方式を用いる。"""
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
    return "\n".join(lines[start:end])


def _extract_mapping_block(block: str, key: str, *, indent: int) -> str | None:
    """`block`内の`<indent space>key:`行から、より深いindentが続く限りの
    行を連結して返す(単純な `key: value` 単一行mappingにも対応するため、
    値がインラインで同じ行にある場合はその行1行を返す)。"""
    lines = block.splitlines()
    marker_indent = " " * indent
    start = next(
        (i for i, line in enumerate(lines) if line == f"{marker_indent}{key}:"), None,
    )
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and (lines[end].startswith(marker_indent + "  ") or not lines[end].strip()):
        end += 1
    return "\n".join(lines[start:end])


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

    # -----------------------------------------------------------------
    # AUTO-001-05-03-03C-R2: writer_start/writer_blockはAUTO-001-05-03-03A/
    # 03Bをreusable workflowとして呼び出すだけであり、write本体(token生成・
    # write API呼び出し等)を一切複製しない。以下は、それらが統合workflow
    # ファイル自身には一切存在しないことを確認する(存在していればR2の
    # 目的である「大量複製の除去」が達成できていないことを意味する)。
    # -----------------------------------------------------------------

    def test_create_github_app_token_not_present_in_integrated_workflow(self):
        self.assertNotIn("create-github-app-token", self.text)

    def test_no_write_http_methods_in_integrated_workflow(self):
        for forbidden in ("-X POST", "-X DELETE", "-X PATCH", "-X PUT"):
            self.assertNotIn(forbidden, self.text)

    def test_no_secrets_inherit_anywhere(self):
        self.assertNotIn("secrets: inherit", self.text)

    def test_only_one_secret_name_referenced(self):
        referenced = set(re.findall(r"secrets\.(\w+)", self.text))
        self.assertEqual(referenced, {"AUTO001_CONTROLLER_APP_PRIVATE_KEY"})

    def test_client_id_variable_not_referenced_in_integrated_workflow(self):
        # client-idはrepository variableとして呼び出し先(03A/03B)で自動的に
        # 参照できるため、統合workflow側では一切参照しない。
        self.assertNotIn("AUTO001_CONTROLLER_APP_CLIENT_ID", self.text)

    def test_does_not_disable_token_revocation(self):
        self.assertNotIn("skip-token-revoke", self.text)

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

    def test_no_automatic_retry_or_rollback(self):
        lower = self.text.lower()
        for forbidden in ("for i in 1 2 3", "retry", "until curl", "while true"):
            self.assertNotIn(forbidden, lower)
        self.assertNotIn("rollback", lower)
        self.assertNotIn("compensat", lower)

    def test_no_raw_response_body_printed(self):
        for forbidden in ("cat issue_", "cat planner_result.json", "cat comments_"):
            self.assertNotIn(forbidden, self.text)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-03C-R2: writer_start/writer_blockが、実装本体を複製せず
# 03A/03Bをreusable workflowとして正しく呼び出していることの静的検査。
# ---------------------------------------------------------------------------

class ReusableWorkflowDelegationTests(unittest.TestCase):
    """YAML parserは使わず(実CIのrequirements-ci.txtにpyyaml依存が無いため)、
    既存の`_extract_step_names`と同じ行ベースのブロック抽出方式で検査する。"""

    @classmethod
    def setUpClass(cls):
        cls.integrated_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.write_check_text = WRITE_CHECK_PATH.read_text(encoding="utf-8")
        cls.block_check_text = BLOCK_CHECK_PATH.read_text(encoding="utf-8")

    @staticmethod
    def _on_block(text: str) -> str:
        m = re.search(r"^on:\n((?:.*\n)*?)(?=^permissions:)", text, flags=re.MULTILINE)
        assert m is not None, "on:ブロックが見つかりません"
        return m.group(1)

    def test_writer_start_uses_exactly_03a(self):
        block = _extract_job_block(self.integrated_text, "writer_start")
        self.assertIn(
            "\n    uses: ./.github/workflows/auto001-controller-write-check.yml\n", "\n" + block + "\n",
        )
        self.assertNotIn("\n    steps:\n", "\n" + block)

    def test_writer_block_uses_exactly_03b(self):
        block = _extract_job_block(self.integrated_text, "writer_block")
        self.assertIn(
            "\n    uses: ./.github/workflows/auto001-controller-block-check.yml\n", "\n" + block + "\n",
        )
        self.assertNotIn("\n    steps:\n", "\n" + block)

    def test_writer_jobs_pass_only_issue_number_and_contract_version(self):
        for job_key in ("writer_start", "writer_block"):
            block = _extract_job_block(self.integrated_text, job_key)
            with_block = _extract_mapping_block(block, "with", indent=4)
            self.assertIsNotNone(with_block, f"{job_key}にwith:が見つかりません")
            keys = re.findall(r"^      (\w+):", with_block, flags=re.MULTILINE)
            self.assertEqual(set(keys), {"issue_number", "contract_version"})
            self.assertIn("issue_number: ${{ needs.plan.outputs.issue_number }}", with_block)
            self.assertIn("contract_version: ${{ needs.plan.outputs.contract_version }}", with_block)

    def test_writer_jobs_pass_exactly_one_explicit_secret(self):
        for job_key in ("writer_start", "writer_block"):
            block = _extract_job_block(self.integrated_text, job_key)
            secrets_block = _extract_mapping_block(block, "secrets", indent=4)
            self.assertIsNotNone(secrets_block, f"{job_key}にsecrets:が見つかりません")
            keys = re.findall(r"^      (\w+):", secrets_block, flags=re.MULTILINE)
            self.assertEqual(keys, ["AUTO001_CONTROLLER_APP_PRIVATE_KEY"])
            self.assertIn(
                "AUTO001_CONTROLLER_APP_PRIVATE_KEY: ${{ secrets.AUTO001_CONTROLLER_APP_PRIVATE_KEY }}",
                secrets_block,
            )

    def test_writer_jobs_permissions_are_read_only(self):
        for job_key in ("writer_start", "writer_block"):
            block = _extract_job_block(self.integrated_text, job_key)
            perm_block = _extract_mapping_block(block, "permissions", indent=4)
            self.assertIsNotNone(perm_block, f"{job_key}にpermissions:が見つかりません")
            entries = dict(re.findall(r"^      (\w+): (\w+)$", perm_block, flags=re.MULTILINE))
            self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_writer_jobs_declare_no_own_concurrency_block(self):
        # 03A/03B自身のtop-level concurrencyブロックだけがnamespaceの
        # 唯一の定義元であることを保証するため、呼び出し側job(writer_start/
        # writer_block)にconcurrencyキー自体が無いことを確認する
        # (二重定義・namespace分岐を防ぐ)。
        for job_key in ("writer_start", "writer_block"):
            block = _extract_job_block(self.integrated_text, job_key)
            self.assertNotIn("\n    concurrency:", "\n" + block)

    def test_03a_declares_both_workflow_dispatch_and_workflow_call(self):
        on_block = self._on_block(self.write_check_text)
        self.assertIn("  workflow_dispatch:\n", on_block)
        self.assertIn("  workflow_call:\n", on_block)
        self.assertEqual(on_block.count("issue_number:"), 2)
        self.assertEqual(on_block.count("type: number"), 2)
        self.assertIn("contract_version:", on_block)
        self.assertIn("type: string", on_block)

    def test_03b_declares_both_workflow_dispatch_and_workflow_call(self):
        on_block = self._on_block(self.block_check_text)
        self.assertIn("  workflow_dispatch:\n", on_block)
        self.assertIn("  workflow_call:\n", on_block)
        self.assertEqual(on_block.count("issue_number:"), 2)
        self.assertEqual(on_block.count("type: number"), 2)
        self.assertIn("contract_version:", on_block)
        self.assertIn("type: string", on_block)

    def test_03a_workflow_call_declares_exactly_one_required_secret(self):
        on_block = self._on_block(self.write_check_text)
        self.assertEqual(on_block.count("AUTO001_CONTROLLER_APP_PRIVATE_KEY"), 1)
        m = re.search(
            r"    secrets:\n      AUTO001_CONTROLLER_APP_PRIVATE_KEY:\n(?:.*\n)*?        required: true\n",
            on_block,
        )
        self.assertIsNotNone(m)

    def test_03b_workflow_call_declares_exactly_one_required_secret(self):
        on_block = self._on_block(self.block_check_text)
        self.assertEqual(on_block.count("AUTO001_CONTROLLER_APP_PRIVATE_KEY"), 1)
        m = re.search(
            r"    secrets:\n      AUTO001_CONTROLLER_APP_PRIVATE_KEY:\n(?:.*\n)*?        required: true\n",
            on_block,
        )
        self.assertIsNotNone(m)

    def test_03a_and_03b_never_use_secrets_inherit(self):
        self.assertNotIn("secrets: inherit", self.write_check_text)
        self.assertNotIn("secrets: inherit", self.block_check_text)

    def test_client_id_var_referenced_but_not_passed_as_workflow_call_input(self):
        # vars(repository variable)はreusable workflow呼び出し時も自動的に
        # 参照できるため、workflow_call.inputsへ含める必要が無い。既存の
        # `vars.AUTO001_CONTROLLER_APP_CLIENT_ID`参照は03A/03B側に残り、
        # client_idという名前のinputは統合workflow側にもworkflow_call.inputs
        # にも一切登場しない。
        self.assertIn("vars.AUTO001_CONTROLLER_APP_CLIENT_ID", self.write_check_text)
        self.assertIn("vars.AUTO001_CONTROLLER_APP_CLIENT_ID", self.block_check_text)
        for on_block in (
            self._on_block(self.write_check_text), self._on_block(self.block_check_text),
        ):
            self.assertNotIn("client_id", on_block)
        self.assertNotIn("client_id", self.integrated_text)
        self.assertNotIn("client-id", self.integrated_text)


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
        # `plan:`job自身の本体だけを対象にする(ファイル先頭のheaderコメントは
        # 対象外)。
        plan_block = _extract_job_block(self.text, "plan")
        self.assertNotIn("issue_snapshot", plan_block)
        self.assertNotIn("comments_snapshot", plan_block)
        # errorsの中身(message全文)をGITHUB_OUTPUTへ書き出していないこと。
        # error_countとerror_fingerprint(sha256)だけが許可される。
        self.assertNotIn('errors[', plan_block)

    def test_plan_job_never_generates_app_token(self):
        plan_block = _extract_job_block(self.text, "plan")
        self.assertNotIn("create-github-app-token", plan_block)
        self.assertNotIn("AUTO001_CONTROLLER_APP_PRIVATE_KEY", plan_block)
        self.assertNotIn("AUTO001_CONTROLLER_APP_CLIENT_ID", plan_block)

    def test_no_job_in_integrated_workflow_generates_app_token_directly(self):
        # AUTO-001-05-03-03C-R2: token生成はAUTO-001-05-03-03A/03B
        # (auto001-controller-write-check.yml / auto001-controller-block-check.yml)
        # 側に1箇所ずつだけ実装されており、統合workflow自身(plan/writer_start/
        # writer_block)のいずれのjobにも直接のtoken生成stepは存在しない。
        self.assertNotIn("create-github-app-token", self.text)

    def test_called_writers_verify_contract_version_before_token_generation(self):
        # AUTO-001-05-03-03A/03B側で、contract_version確認stepが
        # token生成stepより前にあることを確認する(統合workflow経由での
        # 呼び出し時、token生成前に契約versionを確認するという契約境界)。
        for path, job_key in (
            (WRITE_CHECK_PATH, "write_check"), (BLOCK_CHECK_PATH, "block_check"),
        ):
            text = path.read_text(encoding="utf-8")
            names = _extract_step_names(text, job_key)
            verify_idx = names.index(
                "Verify contract_version (reusable call) or allow direct manual invocation",
            )
            token_idx = names.index("Generate Controller App write token")
            self.assertLess(verify_idx, token_idx)
            self.assertEqual(verify_idx, 0, "contract_version確認は先頭stepであるべき")


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

    def test_integrated_workflow_has_no_write_concurrency_group_of_its_own(self):
        # AUTO-001-05-03-03C-R2: writer_start/writer_blockはconcurrencyを
        # 自前で宣言しない(ReusableWorkflowDelegationTests参照)。統合
        # workflowファイル全体を見ても、`group: auto001-controller-write-`
        # というwrite namespace用のgroup定義行は一切登場しない(03A/03B側に
        # だけ1箇所ずつ定義され、それがwriter_start/writer_block呼び出し時にも
        # 評価されるため、統合workflow側で重複定義するとnamespace分岐のリスク
        # になる)。ファイル名自体に含まれる"auto001-controller-write-check.yml"
        # という文字列(`uses:`行やコメント中の言及)は許可対象であり、
        # 判定対象から除く。
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertNotIn("group: auto001-controller-write-", text)

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

    CONTRACT_STEP_NAME = "Verify contract_version (reusable call) or allow direct manual invocation"

    def test_03a_step_order_is_contract_version_then_validate_then_common_sequence(self):
        # AUTO-001-05-03-03C-R3: 先頭stepは常に評価対象(if:による無条件skip
        # は行わない。AUTO-001-05-03-03C-R2時点の`if: github.event_name ==
        # 'workflow_call'`は、called workflow内のgithub contextがcaller
        # workflowに関連付けられ`workflow_call`には決してならないという
        # 既知の問題があったため撤去した)。それ以降のstep順序・step名は
        # AUTO-001-05-03-03A時点から一切変更していない。
        names = _extract_step_names(
            WRITE_CHECK_PATH.read_text(encoding="utf-8"), "write_check",
        )
        self.assertEqual(
            names,
            [self.CONTRACT_STEP_NAME, "Checkout", "Set up Python 3.12", "Validate issue_number input format"]
            + self.COMMON_START_STEPS,
        )

    def test_03b_step_order_is_contract_version_then_validate_then_common_sequence(self):
        names = _extract_step_names(
            BLOCK_CHECK_PATH.read_text(encoding="utf-8"), "block_check",
        )
        self.assertEqual(
            names,
            [self.CONTRACT_STEP_NAME, "Checkout", "Set up Python 3.12", "Validate issue_number input format"]
            + self.COMMON_BLOCK_STEPS,
        )

    def test_03a_contract_version_step_has_no_event_name_gate(self):
        # AUTO-001-05-03-03C-R3: このstep自体には`if:`条件が無く、常に
        # 評価される(経路の分類はstep内部のshellロジックで行う)。
        text = WRITE_CHECK_PATH.read_text(encoding="utf-8")
        m = re.search(
            r"- name: " + re.escape(self.CONTRACT_STEP_NAME) + r"\n"
            r"        id: verify_contract_version\n"
            r"        env:\n",
            text,
        )
        self.assertIsNotNone(m)
        self.assertNotIn("if: github.event_name == 'workflow_call'", text)

    def test_03b_contract_version_step_has_no_event_name_gate(self):
        text = BLOCK_CHECK_PATH.read_text(encoding="utf-8")
        m = re.search(
            r"- name: " + re.escape(self.CONTRACT_STEP_NAME) + r"\n"
            r"        id: verify_contract_version\n"
            r"        env:\n",
            text,
        )
        self.assertIsNotNone(m)
        self.assertNotIn("if: github.event_name == 'workflow_call'", text)


# ---------------------------------------------------------------------------
# AUTO-001-05-03-03C-R2: called writer(03A/03B)がcontract version不一致で
# token生成前に停止することのsubprocess検証。
# ---------------------------------------------------------------------------

class CalledWriterContractVersionGateTests(unittest.TestCase):
    """AUTO-001-05-03-03C-R4: 空のcontract_versionを一切許可経路として
    扱わず、統合workflow用の固定sentinel("AUTO-001-05-03-03C-writer-v1")と
    各writer自身の直接手動実行用sentinel("...-03A-direct-v1" /
    "...-03B-direct-v1")の、既知の2種類だけを許可する。caller eventは、
    統合workflow自身が`issues:labeled`または`workflow_dispatch`のどちらで
    起動されたかを表す(called workflow内のgithub.event_nameがその値の
    まま伝播するため、これがテストのCALLER_EVENT_NAMEに相当する)。"""

    INTEGRATED = "AUTO-001-05-03-03C-writer-v1"
    DIRECT_A = "AUTO-001-05-03-03A-direct-v1"
    DIRECT_B = "AUTO-001-05-03-03B-direct-v1"
    UNKNOWN = "bogus-version"

    def _run(
        self, path: Path, *, caller_event_name: str, contract_version_value: str | None,
    ):
        script = _extract_step_run_lines(
            path.read_text(encoding="utf-8"), "verify_contract_version",
        )
        with tempfile.TemporaryDirectory() as tmp:
            env = _base_env(Path(tmp))
            env["CALLER_EVENT_NAME"] = caller_event_name
            if contract_version_value is not None:
                env["CONTRACT_VERSION_VALUE"] = contract_version_value
            else:
                env.pop("CONTRACT_VERSION_VALUE", None)
            return _run_bash_script_in_dir(script, env, Path(tmp))

    # -----------------------------------------------------------------
    # R4必須テスト1〜9(03A/03Bそれぞれの直接sentinelを使って両方に適用)。
    # -----------------------------------------------------------------

    def _assert_matrix(self, path: Path, *, own_direct: str):
        with self.subTest(case="1_integrated_version_issues"):
            proc = self._run(path, caller_event_name="issues", contract_version_value=self.INTEGRATED)
            self.assertEqual(proc.returncode, 0, proc.stderr)

        with self.subTest(case="2_integrated_version_workflow_dispatch"):
            proc = self._run(
                path, caller_event_name="workflow_dispatch", contract_version_value=self.INTEGRATED,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

        with self.subTest(case="3_direct_version_workflow_dispatch"):
            proc = self._run(
                path, caller_event_name="workflow_dispatch", contract_version_value=own_direct,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)

        with self.subTest(case="4_direct_version_issues"):
            proc = self._run(path, caller_event_name="issues", contract_version_value=own_direct)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("不正なイベント", proc.stdout + proc.stderr)

        with self.subTest(case="5_direct_version_unknown_event"):
            proc = self._run(path, caller_event_name="schedule", contract_version_value=own_direct)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("不正なイベント", proc.stdout + proc.stderr)

        with self.subTest(case="6_empty_workflow_dispatch"):
            proc = self._run(
                path, caller_event_name="workflow_dispatch", contract_version_value=None,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("契約versionが欠落", proc.stdout + proc.stderr)

        with self.subTest(case="7_empty_issues"):
            proc = self._run(path, caller_event_name="issues", contract_version_value=None)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("契約versionが欠落", proc.stdout + proc.stderr)

        with self.subTest(case="8_unknown_version_workflow_dispatch"):
            proc = self._run(
                path, caller_event_name="workflow_dispatch", contract_version_value=self.UNKNOWN,
            )
            self.assertEqual(proc.returncode, 1)
            self.assertIn("想定外です", proc.stdout + proc.stderr)

        with self.subTest(case="9_unknown_version_issues"):
            proc = self._run(path, caller_event_name="issues", contract_version_value=self.UNKNOWN)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("想定外です", proc.stdout + proc.stderr)

    def test_03a_gate_matrix(self):
        self._assert_matrix(WRITE_CHECK_PATH, own_direct=self.DIRECT_A)

    def test_03b_gate_matrix(self):
        self._assert_matrix(BLOCK_CHECK_PATH, own_direct=self.DIRECT_B)

    # -----------------------------------------------------------------
    # 10・11. 相手writerの直接sentinelを渡した場合はFailureになること
    # (03Aへ03B用sentinel、03Bへ03A用sentinel)。
    # -----------------------------------------------------------------

    def test_10_03b_direct_sentinel_rejected_by_03a(self):
        proc = self._run(
            WRITE_CHECK_PATH, caller_event_name="workflow_dispatch", contract_version_value=self.DIRECT_B,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("想定外です", proc.stdout + proc.stderr)

    def test_11_03a_direct_sentinel_rejected_by_03b(self):
        proc = self._run(
            BLOCK_CHECK_PATH, caller_event_name="workflow_dispatch", contract_version_value=self.DIRECT_A,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("想定外です", proc.stdout + proc.stderr)

    # -----------------------------------------------------------------
    # 13. private key・contract_version実値がログへ出力されないこと
    # -----------------------------------------------------------------

    def test_03a_failure_messages_never_echo_actual_contract_version_value(self):
        # 未知versionによるFailure(case 8/9)と、直接sentinelを不正なイベント
        # で使ったFailure(case 4/5)の両方で、渡された実値そのものが
        # ログへ出力されないことを確認する。
        for caller_event, cv in (
            ("issues", self.UNKNOWN), ("workflow_dispatch", self.UNKNOWN), ("issues", self.DIRECT_A),
        ):
            proc = self._run(WRITE_CHECK_PATH, caller_event_name=caller_event, contract_version_value=cv)
            self.assertNotIn(cv, proc.stdout + proc.stderr)

    def test_03b_failure_messages_never_echo_actual_contract_version_value(self):
        for caller_event, cv in (
            ("issues", self.UNKNOWN), ("workflow_dispatch", self.UNKNOWN), ("issues", self.DIRECT_B),
        ):
            proc = self._run(BLOCK_CHECK_PATH, caller_event_name=caller_event, contract_version_value=cv)
            self.assertNotIn(cv, proc.stdout + proc.stderr)

    # -----------------------------------------------------------------
    # 14. workflow_dispatchに正しいdefaultが設定されていること
    # -----------------------------------------------------------------

    def test_03a_workflow_dispatch_has_correct_default_sentinel(self):
        text = WRITE_CHECK_PATH.read_text(encoding="utf-8")
        m = re.search(
            r"contract_version:\n"
            r"        description: [^\n]+\n"
            r"        required: true\n"
            r"        type: string\n"
            r"        default: \"AUTO-001-05-03-03A-direct-v1\"\n",
            text,
        )
        self.assertIsNotNone(m)

    def test_03b_workflow_dispatch_has_correct_default_sentinel(self):
        text = BLOCK_CHECK_PATH.read_text(encoding="utf-8")
        m = re.search(
            r"contract_version:\n"
            r"        description: [^\n]+\n"
            r"        required: true\n"
            r"        type: string\n"
            r"        default: \"AUTO-001-05-03-03B-direct-v1\"\n",
            text,
        )
        self.assertIsNotNone(m)

    # -----------------------------------------------------------------
    # 15. 統合workflowが統合version(03A/03B自身の直接sentinelではない)
    # だけを渡すこと。
    # -----------------------------------------------------------------

    def test_integrated_workflow_never_passes_a_direct_sentinel(self):
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertNotIn(self.DIRECT_A, text)
        self.assertNotIn(self.DIRECT_B, text)
        self.assertIn(self.INTEGRATED, text)

    # -----------------------------------------------------------------
    # 8. すべてのFailureでApp token生成とwrite stepが到達不能であること。
    # この確認stepは常にjobの先頭step(WriteOrderRegressionTests側で
    # 順序確認済み)であり、GitHub Actionsの既定shell(-eo pipefail)の下で
    # このstepがexit 1すれば、`if:`条件を持たない後続step(Checkout等)を
    # 含め、job全体が直ちに失敗として停止し、以降のtoken生成stepを含む
    # 一切のstepへは到達しない。ここでは、このstepが実際にjobの唯一の
    # 先頭step(他のいかなるstepよりも前)であることを再確認し、その事実に
    # よってFailure時のtoken/write未到達が保証されることの根拠とする。
    # -----------------------------------------------------------------

    def test_03a_gate_is_the_single_first_step_before_any_write_capable_step(self):
        names = _extract_step_names(WRITE_CHECK_PATH.read_text(encoding="utf-8"), "write_check")
        self.assertEqual(names[0], "Verify contract_version (reusable call) or allow direct manual invocation")
        self.assertNotIn("Generate Controller App write token", names[:1])

    def test_03b_gate_is_the_single_first_step_before_any_write_capable_step(self):
        names = _extract_step_names(BLOCK_CHECK_PATH.read_text(encoding="utf-8"), "block_check")
        self.assertEqual(names[0], "Verify contract_version (reusable call) or allow direct manual invocation")
        self.assertNotIn("Generate Controller App write token", names[:1])

    def test_integrated_plan_job_contract_version_literal_matches_03a_03b_expectation(self):
        # plan jobが出力するcontract_versionの固定文字列が、03A/03Bが期待する
        # 固定文字列と一致していること(この値はGitHub Actions上の実際の
        # 値の受け渡しでは検証できないため、双方のソースの固定文字列リテラル
        # が一致していることを静的に確認する)。
        integrated_text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn(f'print("contract_version={self.INTEGRATED}")', integrated_text)
        for path in (WRITE_CHECK_PATH, BLOCK_CHECK_PATH):
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'integrated="{self.INTEGRATED}"', text)


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

    # -----------------------------------------------------------------
    # Success, write無し: plannerが「そもそも書き込みを意図しない」と
    # 判定した既知の状態(NOT_APPLICABLE / WOULD_BLOCK_STATE)。
    # -----------------------------------------------------------------

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

    # -----------------------------------------------------------------
    # Failure, write無し: plannerがWOULD_START/WOULD_BLOCK_PREFLIGHT
    # (=書き込みを意図)と判定したにもかかわらず、check-planによる
    # exact契約一致が取れない場合。NOT_APPLICABLE/WOULD_BLOCK_STATEとは
    # 異なり、これは異常事態であり成功扱いにしない(AUTO-001-05-03-03C-R1
    # 監査での修正: 修正前はここがwriter_action=NONEのままexit 0の
    # Successだった)。
    # -----------------------------------------------------------------

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

    def test_would_start_with_extra_planned_label_is_a_failure(self):
        # plannerが本来出さないはずの、余分なラベルを含む計画(改ざん・不具合
        # 想定)はcheck-planが厳密一致で拒否する。decision自体はWOULD_START
        # (=書き込み意図)のため、writer_action=NONEのまま黙ってSuccess終了
        # してはならず、stepをFailureにする。
        fixture = self._fixture(planned_add_labels=["agent:working", "extra:label"])
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")
        self.assertEqual(output.get("decision"), "WOULD_START")

    def test_would_block_preflight_with_zero_errors_is_a_failure(self):
        fixture = self._fixture(
            decision="WOULD_BLOCK_PREFLIGHT", preflight_valid=False,
            planned_add_labels=["agent:blocked"], errors=[],
            reason="preflight_contract_violation",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_unknown_decision_string_is_a_failure(self):
        fixture = self._fixture(decision="SOMETHING_ELSE")
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_would_block_preflight_missing_add_label_is_a_failure(self):
        # planned_add_labelsが空(=agent:blockedが計画されていない)WOULD_
        # BLOCK_PREFLIGHTも、check-planの厳密一致で拒否されFailureになる。
        fixture = self._fixture(
            decision="WOULD_BLOCK_PREFLIGHT", preflight_valid=False,
            planned_add_labels=[],
            errors=[{"code": "MISSING_HEADING", "section": None, "message": "x"}],
            reason="preflight_contract_violation",
        )
        proc, output = self._run(fixture)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertEqual(output.get("writer_action"), "NONE")

    def test_missing_planner_result_file_is_a_failure_with_no_output_written(self):
        # planner_result.json自体が存在しない(plannerの前段step失敗等)場合、
        # GITHUB_OUTPUTには何も書き込まれない(=needs.plan.outputs.*は空文字列
        # となり、writer jobのif条件は'START'/'BLOCK'いずれにも一致しない)。
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            script = _extract_step_run_lines(
                WORKFLOW_PATH.read_text(encoding="utf-8"), "classify",
            )
            env = _base_env(tmpdir)
            proc = _run_bash_script_in_dir(script, env, tmpdir)
            output = _parse_github_output(tmpdir / "github_output.txt")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(output, {})

    def test_malformed_planner_result_json_is_a_failure_with_no_output_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "planner_result.json").write_text("{not valid json", encoding="utf-8")
            script = _extract_step_run_lines(
                WORKFLOW_PATH.read_text(encoding="utf-8"), "classify",
            )
            env = _base_env(tmpdir)
            proc = _run_bash_script_in_dir(script, env, tmpdir)
            output = _parse_github_output(tmpdir / "github_output.txt")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(output, {})

    def test_planner_result_missing_required_key_is_a_failure_with_no_output_written(self):
        # decision等の必須キーが欠落したJSON(構造は正しいが不完全)も、
        # 読み込み・判定処理自体の失敗としてFailureになる。
        fixture = {"issue_number": 1}
        with tempfile.TemporaryDirectory() as tmp:
            proc = _run_classify_step(Path(tmp), fixture)
            output = _parse_github_output(Path(tmp) / "github_output.txt")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(output, {})


# ---------------------------------------------------------------------------
# Failure経路でtoken生成・write stepがSkippedとなることの証拠。
#
# writer_start/writer_blockはそれぞれ`if: needs.plan.outputs.writer_action
# == 'START'` / `== 'BLOCK'`でjob全体がgateされている
# (WorkflowStaticTests.test_writer_jobs_gated_on_exact_writer_actionで
# 確認済み)。ClassifyStepFixtureTestsの各Failureケースはいずれも
# writer_action="NONE"(または$GITHUB_OUTPUT自体が空)であり、'START'/'BLOCK'
# のどちらとも一致しないため、このgateによってjob自体が実行されない
# (Skipped)。job自体が実行されなければ、job内のController App token生成
# step・write stepも実行されない。このクラスは、その論理的連鎖の前提
# (gate文言の存在とFailureケースの出力値)を1箇所にまとめて再確認する。
# ---------------------------------------------------------------------------

class FailurePathSkipsTokenAndWriteTests(unittest.TestCase):

    def test_writer_job_gate_expressions_are_exact_string_equality(self):
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        self.assertIn("if: needs.plan.outputs.writer_action == 'START'", text)
        self.assertIn("if: needs.plan.outputs.writer_action == 'BLOCK'", text)
        # 'NONE'や空文字列と誤って一致するような緩い条件(!=禁止ラベル方式等)
        # ではないことを確認する。
        self.assertNotIn("writer_action != 'NONE'", text)

    def test_no_step_level_override_bypasses_the_job_level_gate(self):
        # job自体がgateされている以上、job内の個別stepに`if: always()`が
        # あってもjobそのものが起動しなければ実行されない。ただし「Publish
        # job summary」stepは、03A/03Bと同じく`if: always()`で常に実行され
        # Job Summaryを記録する設計であり、write APIやtoken生成を一切行わない
        # ためこれは許容する。ここではtoken生成step・write step側(summary
        # stepより前の部分)に、job-level gateを無視して単独実行され得る
        # ような`always()`が付いていないことだけを確認する。
        text = WORKFLOW_PATH.read_text(encoding="utf-8")
        writer_start_block = text.split("  writer_start:")[1].split("  writer_block:")[0]
        writer_block_block = text.split("  writer_block:")[1]
        for block in (writer_start_block, writer_block_block):
            pre_summary = block.split("- name: Publish job summary")[0]
            self.assertNotIn("if: always()", pre_summary)
            self.assertNotIn("if: failure()", pre_summary)

    def test_contract_mismatch_fixture_yields_writer_action_not_in_start_or_block(self):
        fixtures = [
            {
                "issue_number": 4, "decision": "WOULD_START", "applicable": True,
                "preflight_valid": True, "current_labels": ["agent:ready"],
                "planned_remove_labels": ["agent:ready"],
                "planned_add_labels": ["agent:working", "extra:label"],
                "planned_comment": None, "errors": [], "reason": "preflight_pass",
            },
            {
                "issue_number": 5, "decision": "WOULD_BLOCK_PREFLIGHT", "applicable": True,
                "preflight_valid": False, "current_labels": ["agent:ready"],
                "planned_remove_labels": ["agent:ready"], "planned_add_labels": ["agent:blocked"],
                "planned_comment": None, "errors": [], "reason": "preflight_contract_violation",
            },
            {
                "issue_number": 6, "decision": "INTERNAL_ERROR", "applicable": False,
                "preflight_valid": None, "current_labels": [],
                "planned_remove_labels": [], "planned_add_labels": [], "planned_comment": None,
                "errors": [{"code": "INTERNAL_ERROR", "section": None, "message": "x"}],
                "reason": "cli_setup_error",
            },
        ]
        for fixture in fixtures:
            with self.subTest(decision=fixture["decision"]):
                with tempfile.TemporaryDirectory() as tmp:
                    proc = _run_classify_step(Path(tmp), fixture)
                    output = _parse_github_output(Path(tmp) / "github_output.txt")
                self.assertEqual(proc.returncode, 1)
                self.assertNotIn(output.get("writer_action"), ("START", "BLOCK"))


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
