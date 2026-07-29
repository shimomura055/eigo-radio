"""scripts/issue_agent_planner.py (AUTO-001-05-02A) の単体テスト。

外部API・外部ネットワークは一切使わない。plannerコア(plan)の決定論的な
状態遷移、GitHub event payloadの正規化(normalize_github_event)、CLI、
そしてワークフローYAMLの静的検査を対象とする。
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

from auto001_test_issue_preflight_validator import DEFAULT_CONTENT, build_body
from scripts.issue_agent_planner import (
    AGENT_BLOCKED_LABEL,
    AGENT_READY_LABEL,
    AGENT_WORKING_LABEL,
    CONFLICTING_STATE_LABELS,
    KNOWN_STATE_LABELS,
    Decision,
    PlannerInput,
    PlannerInputError,
    PlannerResult,
    TriggerType,
    main as planner_main,
    normalize_github_event,
    plan,
)
from scripts.issue_preflight_validator import validate_issue_body

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto001-agent-dryrun.yml"
PLANNER_SOURCE_PATH = REPO_ROOT / "scripts" / "issue_agent_planner.py"

VALID_BODY = build_body()


def make_input(**overrides) -> PlannerInput:
    defaults = dict(
        issue_number=1,
        is_open=True,
        is_pull_request=False,
        trigger=TriggerType.ISSUES_LABELED.value,
        added_label=AGENT_READY_LABEL,
        current_labels=(AGENT_READY_LABEL,),
        issue_body=VALID_BODY,
    )
    defaults.update(overrides)
    return PlannerInput(**defaults)


# ---------------------------------------------------------------------------
# 契約定数
# ---------------------------------------------------------------------------

class ContractConstantsTests(unittest.TestCase):

    def test_8_known_state_labels(self):
        self.assertEqual(len(KNOWN_STATE_LABELS), 8)
        self.assertEqual(len(set(KNOWN_STATE_LABELS)), 8)

    def test_conflicting_labels_excludes_agent_ready(self):
        self.assertNotIn(AGENT_READY_LABEL, CONFLICTING_STATE_LABELS)
        self.assertEqual(len(CONFLICTING_STATE_LABELS), 7)

    def test_trigger_type_values_are_exact(self):
        self.assertEqual(TriggerType.ISSUES_LABELED.value, "issues:labeled")
        self.assertEqual(TriggerType.WORKFLOW_DISPATCH.value, "workflow_dispatch")


# ---------------------------------------------------------------------------
# 16.1 trigger
# ---------------------------------------------------------------------------

class TriggerTests(unittest.TestCase):

    def test_labeled_agent_ready_is_evaluated(self):
        result = plan(make_input())
        self.assertEqual(result.decision, Decision.WOULD_START, msg=result.errors)
        self.assertTrue(result.applicable)

    def test_labeled_other_label_not_applicable(self):
        result = plan(make_input(added_label="bug"))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertFalse(result.applicable)
        self.assertEqual(result.reason, "label_not_agent_ready")

    def test_labeled_case_mismatch_not_applicable(self):
        result = plan(make_input(added_label="Agent:Ready"))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)

    def test_labeled_whitespace_variant_not_applicable(self):
        result = plan(make_input(added_label=" agent:ready "))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)

    def test_labeled_similar_name_not_applicable(self):
        result = plan(make_input(added_label="agent:ready2"))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)

    def test_workflow_dispatch_reaches_same_planner(self):
        result = plan(make_input(trigger=TriggerType.WORKFLOW_DISPATCH.value, added_label=None))
        self.assertEqual(result.decision, Decision.WOULD_START, msg=result.errors)

    def test_workflow_dispatch_ignores_added_label(self):
        # workflow_dispatchではadded_labelは意味を持たない(labeledイベント専用の入力)。
        a = plan(make_input(trigger=TriggerType.WORKFLOW_DISPATCH.value, added_label=None))
        b = plan(make_input(trigger=TriggerType.WORKFLOW_DISPATCH.value, added_label="irrelevant"))
        self.assertEqual(a.decision, b.decision)

    def test_unsupported_trigger_is_internal_error(self):
        result = plan(make_input(trigger="issues:opened"))
        self.assertEqual(result.decision, Decision.INTERNAL_ERROR)

    def test_normalize_missing_event_info_raises(self):
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload={"action": "labeled"})


# ---------------------------------------------------------------------------
# 16.2 正常系
# ---------------------------------------------------------------------------

class NormalCaseTests(unittest.TestCase):

    def test_would_start_on_open_issue_with_only_agent_ready(self):
        result = plan(make_input())
        self.assertEqual(result.decision, Decision.WOULD_START, msg=result.errors)

    def test_planned_remove_is_agent_ready(self):
        result = plan(make_input())
        self.assertEqual(result.planned_remove_labels, (AGENT_READY_LABEL,))

    def test_planned_add_is_agent_working(self):
        result = plan(make_input())
        self.assertEqual(result.planned_add_labels, (AGENT_WORKING_LABEL,))

    def test_preflight_valid_true(self):
        result = plan(make_input())
        self.assertTrue(result.preflight_valid)

    def test_no_errors_no_comment(self):
        result = plan(make_input())
        self.assertEqual(result.errors, [])
        self.assertIsNone(result.planned_comment)

    def test_machine_dict_has_required_keys(self):
        result = plan(make_input())
        d = result.to_machine_dict()
        for key in (
            "issue_number", "decision", "applicable", "preflight_valid",
            "current_labels", "planned_remove_labels", "planned_add_labels",
            "planned_comment", "errors",
        ):
            self.assertIn(key, d)


# ---------------------------------------------------------------------------
# 16.3 preflight不合格
# ---------------------------------------------------------------------------

class PreflightFailTests(unittest.TestCase):

    def test_missing_required_heading_blocks(self):
        body = build_body(drop={"目的"})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT)
        self.assertFalse(result.preflight_valid)
        codes = {e["code"] for e in result.errors}
        self.assertIn("MISSING_HEADING", codes)

    def test_empty_required_content_blocks(self):
        body = build_body(content={"目的": ""})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT)

    def test_invalid_management_id_blocks(self):
        body = build_body(content={"管理ID": "not-a-valid-id-format!!"})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT)
        codes = {e["code"] for e in result.errors}
        self.assertIn("INVALID_MANAGEMENT_ID", codes)

    def test_invalid_acceptance_criteria_blocks(self):
        body = build_body(content={"受入条件": "受入条件は特にありません"})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT)
        codes = {e["code"] for e in result.errors}
        self.assertIn("ACCEPTANCE_CRITERIA_MISSING", codes)

    def test_multiple_violations_all_included(self):
        body = build_body(drop={"目的", "非対象範囲", "リスク"})
        direct = validate_issue_body(body)
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT)
        self.assertEqual(len(result.errors), len(direct.errors))

    def test_planned_labels_on_block_preflight(self):
        body = build_body(drop={"目的"})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.planned_remove_labels, (AGENT_READY_LABEL,))
        self.assertEqual(result.planned_add_labels, (AGENT_BLOCKED_LABEL,))

    def test_planned_comment_present_on_block_preflight(self):
        body = build_body(drop={"目的"})
        result = plan(make_input(issue_body=body))
        self.assertIsNotNone(result.planned_comment)
        self.assertIn("dry-run", result.planned_comment)


# ---------------------------------------------------------------------------
# 16.4 状態異常
# ---------------------------------------------------------------------------

class StateAnomalyTests(unittest.TestCase):

    def test_closed_issue_blocks(self):
        result = plan(make_input(is_open=False))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason, "issue_closed")
        self.assertEqual(result.planned_remove_labels, ())
        self.assertEqual(result.planned_add_labels, ())

    def test_agent_working_conflict_blocks(self):
        result = plan(make_input(current_labels=(AGENT_READY_LABEL, "agent:working")))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason, "conflicting_state_label")

    def test_agent_blocked_conflict_blocks(self):
        result = plan(make_input(current_labels=(AGENT_READY_LABEL, "agent:blocked")))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)

    def test_agent_failed_conflict_blocks(self):
        result = plan(make_input(current_labels=(AGENT_READY_LABEL, "agent:failed")))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)

    def test_multiple_mutually_exclusive_labels_blocks(self):
        result = plan(make_input(
            current_labels=(AGENT_READY_LABEL, "agent:review", "human:approved"),
        ))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)

    def test_agent_ready_missing_from_current_labels_blocks(self):
        result = plan(make_input(current_labels=()))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason, "agent_ready_label_missing")

    def test_unknown_generic_labels_alone_still_blocks_missing_ready(self):
        result = plan(make_input(current_labels=("good-first-issue", "help-wanted")))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason, "agent_ready_label_missing")

    def test_unknown_generic_labels_alongside_agent_ready_do_not_block(self):
        result = plan(make_input(current_labels=(AGENT_READY_LABEL, "good-first-issue")))
        self.assertEqual(result.decision, Decision.WOULD_START, msg=result.errors)


# ---------------------------------------------------------------------------
# 16.5 Pull Request
# ---------------------------------------------------------------------------

class PullRequestTests(unittest.TestCase):

    def test_issue_form_is_evaluated(self):
        result = plan(make_input(is_pull_request=False))
        self.assertNotEqual(result.decision, Decision.NOT_APPLICABLE)

    def test_pull_request_form_not_applicable(self):
        result = plan(make_input(is_pull_request=True))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertEqual(result.reason, "target_is_pull_request")
        self.assertFalse(result.applicable)

    def test_pull_request_workflow_dispatch_not_applicable(self):
        result = plan(make_input(
            is_pull_request=True, trigger=TriggerType.WORKFLOW_DISPATCH.value, added_label=None,
        ))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)

    def test_pull_request_takes_precedence_over_wrong_label(self):
        # PR判定はラベル不一致より先に評価されるべき(どちらも安全にNOT_APPLICABLEになる)。
        result = plan(make_input(is_pull_request=True, added_label="bug"))
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertEqual(result.reason, "target_is_pull_request")


# ---------------------------------------------------------------------------
# 16.6 二重起動(plannerが検出できる部分)
# ---------------------------------------------------------------------------

class DoubleInvocationDetectionTests(unittest.TestCase):
    """concurrency group自体の生成はworkflow YAML側の責務であり、
    ここではworkflow静的検査(WorkflowStaticTests)で検証する。
    plannerが「既に作業中」という既存状態を検出できることを確認する。
    """

    def test_planner_detects_already_working_state(self):
        result = plan(make_input(current_labels=(AGENT_READY_LABEL, AGENT_WORKING_LABEL)))
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.planned_add_labels, ())


# ---------------------------------------------------------------------------
# 16.7 入力安全性
# ---------------------------------------------------------------------------

MALICIOUS_SNIPPETS = [
    "$(rm -rf /)",
    "`rm -rf /`",
    "${{ secrets.GITHUB_TOKEN }}",
    "$env:PATH; Remove-Item -Recurse -Force C:\\",
    "line1\nline2\nline3",
    "he said \"hello\" and 'goodbye'",
    "日本語とemoji😀とUnicode文字列",
    "```\ncode fence content\n```",
]


class InputSafetyTests(unittest.TestCase):

    def test_malicious_content_never_raises(self):
        for snippet in MALICIOUS_SNIPPETS:
            with self.subTest(snippet=snippet):
                body = build_body(content={"現在の問題": snippet})
                result = plan(make_input(issue_body=body))
                self.assertIsInstance(result, PlannerResult)
                self.assertNotEqual(result.decision, Decision.INTERNAL_ERROR, msg=result.errors)

    def test_malicious_content_in_management_id_handled_as_data(self):
        for snippet in MALICIOUS_SNIPPETS:
            with self.subTest(snippet=snippet):
                body = build_body(content={"管理ID": snippet})
                result = plan(make_input(issue_body=body))
                self.assertIsInstance(result, PlannerResult)
                self.assertIn(result.decision, (Decision.WOULD_BLOCK_PREFLIGHT, Decision.WOULD_START))

    def test_management_id_violation_never_echoes_raw_input(self):
        # AC-R1-07: 管理ID形式違反でも、入力された実際の値(またはそこから
        # 抽出された候補文字列)をplanner出力へ一切含めない。
        for snippet in MALICIOUS_SNIPPETS:
            with self.subTest(snippet=snippet):
                body = build_body(content={"管理ID": snippet})
                result = plan(make_input(issue_body=body))
                self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT, msg=result.errors)
                human = result.to_human_text()
                machine_text = json.dumps(result.to_machine_dict(), ensure_ascii=False)
                comment = result.planned_comment or ""
                for text in (human, machine_text, comment):
                    self.assertNotIn(snippet, text)
                for e in result.errors:
                    self.assertNotIn(snippet, e.get("message", ""))

    def test_acceptance_criteria_line_violation_never_echoes_raw_input(self):
        # AC-R1-07相当: 受入条件の形式違反行でも、記載された実際の行内容を
        # planner出力へ含めない。
        for snippet in MALICIOUS_SNIPPETS:
            with self.subTest(snippet=snippet):
                body = build_body(content={"受入条件": f"AC-01 {snippet}"})
                result = plan(make_input(issue_body=body))
                self.assertEqual(result.decision, Decision.WOULD_BLOCK_PREFLIGHT, msg=result.errors)
                human = result.to_human_text()
                machine_text = json.dumps(result.to_machine_dict(), ensure_ascii=False)
                for text in (human, machine_text):
                    self.assertNotIn(snippet, text)

    def test_malicious_labels_are_treated_as_opaque_strings(self):
        for snippet in MALICIOUS_SNIPPETS:
            with self.subTest(snippet=snippet):
                result = plan(make_input(current_labels=(AGENT_READY_LABEL, snippet)))
                self.assertIsInstance(result, PlannerResult)
                self.assertNotEqual(result.decision, Decision.INTERNAL_ERROR)

    def test_full_body_not_present_in_human_or_machine_output(self):
        marker = f"UNIQUE-BODY-MARKER-{uuid.uuid4().hex}"
        body = build_body(content={"現在の問題": f"{marker}\n" * 20})
        result = plan(make_input(issue_body=body))
        self.assertEqual(result.decision, Decision.WOULD_START, msg=result.errors)
        human = result.to_human_text()
        machine = json.dumps(result.to_machine_dict(), ensure_ascii=False)
        self.assertNotIn(marker, human)
        self.assertNotIn(marker, machine)

    def test_planner_source_has_no_dynamic_execution_of_input(self):
        source = PLANNER_SOURCE_PATH.read_text(encoding="utf-8")
        for forbidden in ("eval(", "exec(", "os.system(", "subprocess.", "shell=True"):
            self.assertNotIn(forbidden, source, msg=f"危険な呼び出しが含まれています: {forbidden}")

    def test_planner_source_has_no_network_calls(self):
        source = PLANNER_SOURCE_PATH.read_text(encoding="utf-8")
        for forbidden in ("import socket", "import requests", "import urllib", "import httpx", "requests.", "urlopen("):
            self.assertNotIn(forbidden, source, msg=f"外部通信の兆候が含まれています: {forbidden}")


# ---------------------------------------------------------------------------
# 16.8 再現性
# ---------------------------------------------------------------------------

class ReproducibilityTests(unittest.TestCase):

    def test_same_input_same_output(self):
        i = make_input()
        r1 = plan(i).to_machine_dict()
        r2 = plan(i).to_machine_dict()
        self.assertEqual(r1, r2)

    def test_label_order_independence_for_conflict_detection(self):
        a = plan(make_input(current_labels=(AGENT_READY_LABEL, "agent:working", "agent:blocked")))
        b = plan(make_input(current_labels=("agent:blocked", "agent:working", AGENT_READY_LABEL)))
        self.assertEqual(a.decision, b.decision)
        self.assertEqual(a.reason, b.reason)

    def test_label_order_independence_for_would_start(self):
        a = plan(make_input(current_labels=(AGENT_READY_LABEL, "good-first-issue")))
        b = plan(make_input(current_labels=("good-first-issue", AGENT_READY_LABEL)))
        self.assertEqual(a.decision, b.decision)
        self.assertEqual(a.decision, Decision.WOULD_START)

    def test_input_labels_not_mutated(self):
        labels = (AGENT_READY_LABEL, "agent:working")
        i = make_input(current_labels=labels)
        plan(i)
        self.assertEqual(i.current_labels, labels)

    def test_input_body_not_mutated(self):
        body = VALID_BODY
        i = make_input(issue_body=body)
        plan(i)
        self.assertEqual(i.issue_body, body)

    def test_repeated_calls_do_not_change_tracked_files(self):
        before = PLANNER_SOURCE_PATH.read_text(encoding="utf-8")
        for _ in range(3):
            plan(make_input())
        after = PLANNER_SOURCE_PATH.read_text(encoding="utf-8")
        self.assertEqual(before, after)


# ---------------------------------------------------------------------------
# normalize_github_event の異常系
# ---------------------------------------------------------------------------

class NormalizeErrorTests(unittest.TestCase):

    def _labeled_payload(self, **overrides):
        payload = {
            "action": "labeled",
            "label": {"name": AGENT_READY_LABEL},
            "issue": {
                "number": 1,
                "state": "open",
                "labels": [{"name": AGENT_READY_LABEL}],
                "body": VALID_BODY,
            },
        }
        payload.update(overrides)
        return payload

    def test_missing_issue_object_raises(self):
        payload = self._labeled_payload()
        del payload["issue"]
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_wrong_action_raises(self):
        payload = self._labeled_payload(action="unlabeled")
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_missing_label_name_raises(self):
        payload = self._labeled_payload(label={})
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_workflow_dispatch_missing_issue_payload_raises(self):
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="workflow_dispatch", event_payload={"inputs": {"issue_number": "1"}})

    def test_non_integer_issue_number_raises(self):
        payload = self._labeled_payload()
        payload["issue"]["number"] = "not-a-number"
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_invalid_state_raises(self):
        payload = self._labeled_payload()
        payload["issue"]["state"] = "archived"
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_labels_not_list_raises(self):
        payload = self._labeled_payload()
        payload["issue"]["labels"] = "agent:ready"
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_body_none_normalizes_to_empty_string(self):
        payload = self._labeled_payload()
        payload["issue"]["body"] = None
        normalized = normalize_github_event(trigger="issues:labeled", event_payload=payload)
        self.assertEqual(normalized.issue_body, "")

    def test_body_non_string_raises(self):
        payload = self._labeled_payload()
        payload["issue"]["body"] = 12345
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="issues:labeled", event_payload=payload)

    def test_unknown_trigger_raises(self):
        payload = self._labeled_payload()
        with self.assertRaises(PlannerInputError):
            normalize_github_event(trigger="pull_request:opened", event_payload=payload)

    def test_pull_request_detected_via_pull_request_key(self):
        payload = self._labeled_payload()
        payload["issue"]["pull_request"] = {"url": "https://example.invalid/not-fetched"}
        normalized = normalize_github_event(trigger="issues:labeled", event_payload=payload)
        self.assertTrue(normalized.is_pull_request)

    def test_workflow_dispatch_valid_issue_payload(self):
        event_payload = {"inputs": {"issue_number": "1"}}
        issue_payload = {
            "number": 1, "state": "open",
            "labels": [{"name": AGENT_READY_LABEL}], "body": VALID_BODY,
        }
        normalized = normalize_github_event(
            trigger="workflow_dispatch", event_payload=event_payload, issue_payload=issue_payload,
        )
        self.assertEqual(normalized.issue_number, 1)
        self.assertIsNone(normalized.added_label)


# ---------------------------------------------------------------------------
# plan()自体のINTERNAL_ERROR(内部エラーと契約違反の区別: risk4)
# ---------------------------------------------------------------------------

class InternalErrorTests(unittest.TestCase):

    def test_non_planner_input_returns_internal_error_without_raising(self):
        result = plan({"not": "a PlannerInput"})
        self.assertEqual(result.decision, Decision.INTERNAL_ERROR)

    def test_preflight_validator_internal_error_propagates_distinctly(self):
        # issue_bodyがstr以外の場合、validate_issue_body自身がINTERNAL_ERRORを返す。
        # これは契約違反(WOULD_BLOCK_PREFLIGHT)ではなく内部エラーとして区別されるべき。
        broken = PlannerInput(
            issue_number=1, is_open=True, is_pull_request=False,
            trigger=TriggerType.ISSUES_LABELED.value, added_label=AGENT_READY_LABEL,
            current_labels=(AGENT_READY_LABEL,), issue_body=12345,  # type: ignore[arg-type]
        )
        result = plan(broken)
        self.assertEqual(result.decision, Decision.INTERNAL_ERROR)
        self.assertEqual(result.reason, "preflight_validator_internal_error")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):

    def _write_json(self, tmpdir: Path, name: str, data: dict) -> str:
        path = tmpdir / name
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def test_labeled_event_exit_code_zero_on_would_start(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event = {
                "action": "labeled",
                "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 42, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": VALID_BODY,
                },
            }
            event_path = self._write_json(tmpdir, "event.json", event)
            machine_path = str(tmpdir / "result.json")
            summary_path = str(tmpdir / "summary.md")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "issues:labeled",
                    "--event-json-path", event_path,
                    "--machine-json-path", machine_path,
                    "--summary-path", summary_path,
                ])
            self.assertEqual(code, 0)
            result_data = json.loads(Path(machine_path).read_text(encoding="utf-8"))
            self.assertEqual(result_data["decision"], "WOULD_START")
            summary_text = Path(summary_path).read_text(encoding="utf-8")
            self.assertIn("read-only dry-run", summary_text)

    def test_malformed_event_json_is_internal_error_exit_code_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event_path = tmpdir / "event.json"
            event_path.write_text("{not valid json", encoding="utf-8")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "issues:labeled",
                    "--event-json-path", str(event_path),
                ])
            self.assertEqual(code, 2)

    def test_missing_event_file_is_internal_error(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = planner_main([
                "--trigger", "issues:labeled",
                "--event-json-path", "C:/does/not/exist/event.json",
            ])
        self.assertEqual(code, 2)

    def test_workflow_dispatch_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event_path = self._write_json(tmpdir, "event.json", {"inputs": {"issue_number": "7"}})
            issue_path = self._write_json(tmpdir, "issue.json", {
                "number": 7, "state": "open",
                "labels": [{"name": AGENT_READY_LABEL}], "body": VALID_BODY,
            })
            machine_path = str(tmpdir / "result.json")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "workflow_dispatch",
                    "--event-json-path", event_path,
                    "--issue-json-path", issue_path,
                    "--machine-json-path", machine_path,
                ])
            self.assertEqual(code, 0)
            result_data = json.loads(Path(machine_path).read_text(encoding="utf-8"))
            self.assertEqual(result_data["issue_number"], 7)
            self.assertEqual(result_data["decision"], "WOULD_START")

    def test_preflight_violation_via_cli_exit_code_zero(self):
        # AC-R1-01 / 7.1: preflight不合格でも、実際のCLI経路がexit code 0で終了し、
        # machine JSON・human outputの両方が生成されること。
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            body = build_body(drop={"目的"})
            event = {
                "action": "labeled",
                "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 10, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": body,
                },
            }
            event_path = self._write_json(tmpdir, "event.json", event)
            machine_path = str(tmpdir / "result.json")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "issues:labeled",
                    "--event-json-path", event_path,
                    "--machine-json-path", machine_path,
                ])
            self.assertEqual(code, 0)
            stdout_text = buf.getvalue()
            self.assertIn("WOULD_BLOCK_PREFLIGHT", stdout_text)  # human outputが生成されている
            result_data = json.loads(Path(machine_path).read_text(encoding="utf-8"))
            self.assertEqual(result_data["decision"], "WOULD_BLOCK_PREFLIGHT")
            self.assertTrue(Path(machine_path).exists())  # machine JSONが生成されている

    def test_internal_error_distinct_from_preflight_violation(self):
        # AC-R1-02 / 7.2: 内部エラー(bodyが文字列以外)は、実際のCLI経路で
        # 非ゼロ終了し、preflight不合格(exit code 0)とは区別されること。
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event = {
                "action": "labeled",
                "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 11, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": 12345,
                },
            }
            event_path = self._write_json(tmpdir, "event.json", event)

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "issues:labeled",
                    "--event-json-path", event_path,
                ])
            self.assertEqual(code, 2)
            self.assertNotEqual(code, 0)

    def test_marker_across_sections_not_leaked_via_stdout_machine_json_or_summary(self):
        # AC-R1-04 / AC-R1-05 / AC-R1-06 / 7.4: 一意マーカーを管理ID(不正形式)・
        # 現在の問題・受入条件・Markdown code block(参考資料)へ含めても、
        # stdout・machine JSON・Job Summaryファイルのいずれにも出現しないこと。
        marker = f"UNIQUE-CLI-MARKER-{uuid.uuid4().hex}"
        body = build_body(content={
            "管理ID": marker,
            "現在の問題": f"問題の説明。{marker}",
            "受入条件": f"- [ ] AC-01: {marker}を含む条件",
            "参考資料": f"```\n{marker}\n```",
        })
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event = {
                "action": "labeled",
                "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 55, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": body,
                },
            }
            event_path = self._write_json(tmpdir, "event.json", event)
            machine_path = str(tmpdir / "result.json")
            summary_path = str(tmpdir / "summary.md")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = planner_main([
                    "--trigger", "issues:labeled",
                    "--event-json-path", event_path,
                    "--machine-json-path", machine_path,
                    "--summary-path", summary_path,
                ])
            self.assertEqual(code, 0)
            stdout_text = buf.getvalue()
            machine_text = Path(machine_path).read_text(encoding="utf-8")
            summary_text = Path(summary_path).read_text(encoding="utf-8")

            result_data = json.loads(machine_text)
            self.assertEqual(result_data["decision"], "WOULD_BLOCK_PREFLIGHT", msg=result_data["errors"])

            self.assertNotIn(marker, stdout_text)
            self.assertNotIn(marker, machine_text)
            self.assertNotIn(marker, summary_text)


# ---------------------------------------------------------------------------
# AC-R1-03 / 7.3: workflowが実際に使うsubprocess起動形式
# (`python -m scripts.issue_agent_planner`)そのものの検証。
# CliTestsはmain()をプロセス内で直接呼ぶだけなので、パッケージimportや
# `-m`起動固有の問題(scripts/__init__.py欠落等)は別プロセスでしか検知できない。
# ---------------------------------------------------------------------------

class ModuleInvocationSubprocessTests(unittest.TestCase):

    def _run_module(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "scripts.issue_agent_planner", *args],
            cwd=str(REPO_ROOT), capture_output=True, text=True, timeout=30,
        )

    def test_normal_case_via_module_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event = {
                "action": "labeled", "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 21, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": VALID_BODY,
                },
            }
            event_path = tmpdir / "event.json"
            event_path.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            machine_path = tmpdir / "result.json"

            r = self._run_module([
                "--trigger", "issues:labeled",
                "--event-json-path", str(event_path),
                "--machine-json-path", str(machine_path),
            ])
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            data = json.loads(machine_path.read_text(encoding="utf-8"))
            self.assertEqual(data["decision"], "WOULD_START")

    def test_preflight_violation_via_module_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            body = build_body(drop={"目的"})
            event = {
                "action": "labeled", "label": {"name": AGENT_READY_LABEL},
                "issue": {
                    "number": 22, "state": "open",
                    "labels": [{"name": AGENT_READY_LABEL}], "body": body,
                },
            }
            event_path = tmpdir / "event.json"
            event_path.write_text(json.dumps(event, ensure_ascii=False), encoding="utf-8")
            machine_path = tmpdir / "result.json"

            r = self._run_module([
                "--trigger", "issues:labeled",
                "--event-json-path", str(event_path),
                "--machine-json-path", str(machine_path),
            ])
            self.assertEqual(r.returncode, 0, msg=r.stderr)
            data = json.loads(machine_path.read_text(encoding="utf-8"))
            self.assertEqual(data["decision"], "WOULD_BLOCK_PREFLIGHT")

    def test_malformed_json_via_module_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            event_path = tmpdir / "event.json"
            event_path.write_text("{not valid json", encoding="utf-8")

            r = self._run_module([
                "--trigger", "issues:labeled",
                "--event-json-path", str(event_path),
            ])
            self.assertEqual(r.returncode, 2, msg=r.stderr)

    def test_missing_input_file_via_module_invocation(self):
        r = self._run_module([
            "--trigger", "issues:labeled",
            "--event-json-path", "does/not/exist/event.json",
        ])
        self.assertEqual(r.returncode, 2, msg=r.stderr)


# ---------------------------------------------------------------------------
# 16.9 workflow静的検査
# ---------------------------------------------------------------------------

class WorkflowStaticTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_workflow_file_exists(self):
        self.assertTrue(WORKFLOW_PATH.exists())

    def test_permissions_block_is_exactly_contents_and_issues_read(self):
        m = re.search(r"^permissions:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m, "permissionsブロックが見つかりません")
        block = m.group(1)
        entries = dict(
            line.strip().split(":", 1)
            for line in block.splitlines()
        )
        entries = {k.strip(): v.strip() for k, v in entries.items()}
        self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_no_write_permissions_anywhere(self):
        for forbidden in (
            "contents: write", "issues: write", "pull-requests: write",
            "actions: write", "checks: write", "workflows: write",
            "administration: write", "id-token: write",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_no_secrets_referenced(self):
        self.assertNotIn("secrets.", self.text)

    def test_no_claude_or_llm_api_usage(self):
        # コメント本文で「Claude Code/Anthropic APIは起動しない」旨を説明することは許容する
        # (非対象範囲の明記)。ここで禁止するのは実際の呼び出し・action参照・APIキー環境変数。
        lower = self.text.lower()
        for forbidden in (
            "uses: anthropics/", "uses: claude-code-", "anthropic_api_key",
            "openai_api_key", "claude-code-action", "claude-code-base-action",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_label_or_comment_write_apis(self):
        lower = self.text.lower()
        for forbidden in (
            "issues/labels", "removelabel", "addlabels", "gh issue edit",
            "gh label", "issues/comments", "createcomment", "gh issue comment",
            "gh issue close", "gh issue lock",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_push_or_pr_creation(self):
        lower = self.text.lower()
        for forbidden in ("git push", "gh pr create", "create-pull-request", "git commit"):
            self.assertNotIn(forbidden, lower)

    def test_not_triggered_on_pull_request_event(self):
        self.assertNotIn("pull_request:", self.text)

    def test_triggered_on_issues_labeled(self):
        self.assertIn("issues:", self.text)
        self.assertIn("labeled", self.text)

    def test_has_workflow_dispatch_with_issue_number_input(self):
        self.assertIn("workflow_dispatch:", self.text)
        self.assertIn("issue_number:", self.text)

    def test_concurrency_group_present_and_per_issue(self):
        m = re.search(r"^concurrency:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m, "concurrencyブロックが見つかりません")
        block = m.group(1)
        self.assertIn("group:", block)
        self.assertIn("github.event.issue.number", block)
        self.assertIn("inputs.issue_number", block)

    def test_cancel_in_progress_is_false(self):
        self.assertIn("cancel-in-progress: false", self.text)

    def test_no_label_exact_match_logic_delegated_to_yaml_if(self):
        # ラベル名の完全一致判定はPython(planner)側の責務であり、
        # workflow YAMLのif条件でラベル名を直接比較・フィルタしてはならない。
        self.assertNotIn("github.event.label.name ==", self.text)
        self.assertNotIn("contains(github.event.label.name", self.text)

    def test_no_dispatch_of_claude_code_or_agents(self):
        lower = self.text.lower()
        for forbidden in ("actions/claude-code", "claude-code-base-action"):
            self.assertNotIn(forbidden, lower)

    def test_calls_planner_module_read_only(self):
        self.assertIn("scripts.issue_agent_planner", self.text)


# ---------------------------------------------------------------------------
# AUTO-001-05-02A-R1 7.5: Issue本文・タイトルがshellへ直接展開されないことの
# 専用回帰テスト。単純な"body"文字列の不在チェックだけに頼らず、禁止パターンを
# 個別に明示して検査する(AC-R1-08)。
# ---------------------------------------------------------------------------

class WorkflowShellSafetyTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_no_issue_body_expression(self):
        self.assertNotIn("github.event.issue.body", self.text)
        self.assertNotIn("${{ github.event.issue.body }}", self.text)

    def test_no_issue_title_expression(self):
        self.assertNotIn("github.event.issue.title", self.text)
        self.assertNotIn("${{ github.event.issue.title }}", self.text)

    def test_no_body_or_title_assigned_to_env_var(self):
        for line in self.text.splitlines():
            if re.match(r"^\s*\w+:\s*\$\{\{", line):
                self.assertNotIn("issue.body", line)
                self.assertNotIn("issue.title", line)

    def test_no_eval(self):
        self.assertNotIn("eval ", self.text)
        self.assertNotIn("eval(", self.text)
        self.assertNotIn("eval\t", self.text)

    def test_no_source_of_issue_derived_file(self):
        self.assertNotRegex(self.text, r"(?m)^\s*source\s+")
        self.assertNotIn("source issue_api.json", self.text)
        self.assertNotIn("source $GITHUB_EVENT_PATH", self.text)

    def test_body_string_not_present_anywhere_in_workflow(self):
        # Issue本文がshell scriptの生成材料・変数名・コメントいずれとしても
        # 使われていないことを、"body"という文字列自体の不在で確認する。
        self.assertNotIn("body", self.text.lower())

    def test_python_reads_event_and_issue_json_as_data_files(self):
        # $GITHUB_EVENT_PATH・issue_api.jsonは、いずれもPythonへファイルパス
        # として渡されるだけであり、shell内で内容を展開・実行しない。
        self.assertIn('--event-json-path "$GITHUB_EVENT_PATH"', self.text)
        self.assertIn("--issue-json-path issue_api.json", self.text)
        self.assertIn("> issue_api.json", self.text)  # ファイルへリダイレクトするだけ


# ---------------------------------------------------------------------------
# AUTO-001-05-02A-R1 7.6: `gh api`のread-only認証の静的検査(AC-R1-09, AC-R1-10)。
# ---------------------------------------------------------------------------

class GhApiReadOnlyAuthTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_gh_api_lines_never_specify_write_method(self):
        gh_api_lines = [line for line in self.text.splitlines() if "gh api" in line]
        self.assertTrue(gh_api_lines, "gh apiの呼び出しが見つかりません")
        for line in gh_api_lines:
            self.assertNotRegex(line, r"-X\s*(POST|PATCH|PUT|DELETE)")
            self.assertNotRegex(line, r"--method[= ]\s*(POST|PATCH|PUT|DELETE)")

    def test_no_write_http_methods_anywhere(self):
        for forbidden in (
            "-X POST", "-X PATCH", "-X PUT", "-X DELETE",
            "--method POST", "--method PATCH", "--method PUT", "--method DELETE",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_gh_token_explicitly_set_for_fetch_step(self):
        self.assertIn("GH_TOKEN: ${{ github.token }}", self.text)

    def test_token_value_never_echoed(self):
        for line in self.text.splitlines():
            lower = line.lower()
            if "echo" in lower:
                self.assertNotIn("gh_token", lower)
                self.assertNotIn("github.token", lower)

    def test_no_continue_on_error_masking_fetch_failure(self):
        self.assertNotIn("continue-on-error", self.text)

    def test_no_always_or_failure_override_on_dependent_steps(self):
        # 取得ステップが失敗した場合、後続ステップは(デフォルト挙動どおり)
        # 実行されないこと。always()/failure()での上書きがあると、
        # 取得失敗時にもplannerが実行され得てしまう。
        self.assertNotIn("always()", self.text)
        self.assertNotIn("failure()", self.text)


if __name__ == "__main__":
    unittest.main()
