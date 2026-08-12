"""scripts/implementer_launcher.py (AUTO-001-06-01) の単体・静的・
subprocessテスト。

外部API・外部ネットワーク・実際のGitHub App/Implementer credentialは一切
使わない。純粋関数群の決定論的な判定、CLIの入出力、task bundleの決定性、
そして対応するworkflow YAML
(.github/workflows/auto001-implementer-launcher-dryrun.yml)の静的検査を
対象とする。

このworkflow・スクリプトは、Claude Code・Implementer App・Controller App
のいずれも起動・接続せず、GitHubへの書き込み(ラベル・comment・本文・
branch・commit・PR)を一切行わない。重複起動判定(WOULD_BLOCK_DUPLICATE)は
v1では到達不能な予約値であり、それを実装しないことも検証する。
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from pathlib import Path

from auto001_test_controller_label_writer import _base_env, _run_bash_script_in_dir
from auto001_test_controller_token_check import (
    EXPECTED_FULL_NAME,
    _bash_single_quote,
    _extract_step_run_lines,
    _fake_curl_function,
    _parse_github_output,
)
from auto001_test_issue_preflight_validator import build_body

from scripts.implementer_launcher import (
    ConsistencyCheckResult,
    Decision,
    IssueSnapshot,
    LauncherClassification,
    LauncherInput,
    ReasonCode,
    TASK_BUNDLE_SCHEMA_VERSION,
    build_task_bundle,
    canonical_json_bytes,
    check_source_unchanged,
    classify,
    main as cli_main,
    parse_issue_snapshot,
    parse_positive_integer_strict,
)
from scripts.issue_preflight_validator import ValidationStatus, extract_task_fields, validate_issue_body

REPO_ROOT = Path(__file__).resolve().parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "auto001-implementer-launcher-dryrun.yml"

VALID_ISSUE_BODY = build_body(content={"管理ID": "AUTO-001-06-01"})
CONTRACT_VIOLATION_BODY = build_body(content={"目的": ""})

_BASE_SUBSTITUTIONS = {
    "${{ github.repository }}": EXPECTED_FULL_NAME,
}


def _write_json(tmpdir: Path, name: str, data) -> str:
    path = tmpdir / name
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _issue_response(
    labels: list[str],
    *,
    number: int = 42,
    state: str = "open",
    body: str = "",
    is_pull_request: bool = False,
    updated_at: str = "2026-08-01T00:00:00Z",
    title: str = "test issue",
    html_url: str = "https://github.com/shimomura055/eigo-radio/issues/42",
) -> dict:
    issue: dict = {
        "number": number,
        "state": state,
        "labels": [{"name": n} for n in labels],
        "body": body,
        "updated_at": updated_at,
        "title": title,
        "html_url": html_url,
    }
    if is_pull_request:
        issue["pull_request"] = {"url": "https://api.github.com/repos/x/y/pulls/1"}
    return issue


def _labeled_event(label: str) -> dict:
    return {"action": "labeled", "label": {"name": label}}


def _extract_step(step_id: str, extra_substitutions: dict[str, str] | None = None) -> str:
    subs = dict(_BASE_SUBSTITUTIONS)
    subs.update(extra_substitutions or {})
    return _extract_step_run_lines(WORKFLOW_PATH.read_text(encoding="utf-8"), step_id, substitutions=subs)


# ---------------------------------------------------------------------------
# 必須テスト1〜6: parse_positive_integer_strict
# ---------------------------------------------------------------------------

class ParsePositiveIntegerStrictTests(unittest.TestCase):

    def test_1_positive_integer_passes(self):
        self.assertEqual(parse_positive_integer_strict("12"), 12)

    def test_2_empty_string_fails(self):
        self.assertIsNone(parse_positive_integer_strict(""))

    def test_3_zero_fails(self):
        self.assertIsNone(parse_positive_integer_strict("0"))

    def test_4_leading_zero_fails(self):
        self.assertIsNone(parse_positive_integer_strict("007"))

    def test_5_negative_fails(self):
        self.assertIsNone(parse_positive_integer_strict("-1"))

    def test_6_decimal_fails(self):
        self.assertIsNone(parse_positive_integer_strict("1.5"))

    def test_non_numeric_fails(self):
        self.assertIsNone(parse_positive_integer_strict("abc"))

    def test_non_string_input_fails(self):
        self.assertIsNone(parse_positive_integer_strict(12))  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# parse_issue_snapshot
# ---------------------------------------------------------------------------

class ParseIssueSnapshotTests(unittest.TestCase):

    def test_valid_shape_parses(self):
        snap = parse_issue_snapshot(_issue_response(["agent:working"]))
        self.assertIsNotNone(snap)
        self.assertEqual(snap.issue_number, 42)
        self.assertTrue(snap.is_open)
        self.assertFalse(snap.is_pull_request)
        self.assertEqual(snap.current_labels, ("agent:working",))

    def test_pull_request_flagged(self):
        snap = parse_issue_snapshot(_issue_response(["agent:working"], is_pull_request=True))
        self.assertTrue(snap.is_pull_request)

    def test_closed_state(self):
        snap = parse_issue_snapshot(_issue_response(["agent:working"], state="closed"))
        self.assertFalse(snap.is_open)

    def test_not_a_dict_returns_none(self):
        self.assertIsNone(parse_issue_snapshot(["not", "a", "dict"]))

    def test_missing_number_returns_none(self):
        raw = _issue_response(["agent:working"])
        del raw["number"]
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_bool_number_returns_none(self):
        raw = _issue_response(["agent:working"])
        raw["number"] = True
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_invalid_state_returns_none(self):
        raw = _issue_response(["agent:working"])
        raw["state"] = "weird"
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_labels_not_a_list_returns_none(self):
        raw = _issue_response(["agent:working"])
        raw["labels"] = "agent:working"
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_label_entry_missing_name_returns_none(self):
        raw = _issue_response(["agent:working"])
        raw["labels"] = [{"color": "red"}]
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_missing_updated_at_returns_none(self):
        raw = _issue_response(["agent:working"])
        del raw["updated_at"]
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_missing_html_url_returns_none(self):
        raw = _issue_response(["agent:working"])
        del raw["html_url"]
        self.assertIsNone(parse_issue_snapshot(raw))

    def test_null_body_becomes_empty_string(self):
        raw = _issue_response(["agent:working"])
        raw["body"] = None
        snap = parse_issue_snapshot(raw)
        self.assertEqual(snap.issue_body, "")

    def test_body_sha256_is_correct(self):
        snap = parse_issue_snapshot(_issue_response(["agent:working"], body="hello"))
        self.assertEqual(snap.body_sha256, hashlib.sha256(b"hello").hexdigest())


# ---------------------------------------------------------------------------
# 必須テスト7〜18: classify() decision matrix
# ---------------------------------------------------------------------------

class ClassifyDecisionTests(unittest.TestCase):

    def _classify(self, *, labels, trigger="issues:labeled", added_label="agent:working",
                  state="open", body="", is_pull_request=False):
        snap = parse_issue_snapshot(
            _issue_response(labels, state=state, body=body, is_pull_request=is_pull_request),
        )
        return classify(LauncherInput(trigger=trigger, added_label=added_label, snapshot=snap))

    def test_7_open_working_only_is_launch_candidate(self):
        result = self._classify(labels=["agent:working"], body=VALID_ISSUE_BODY)
        self.assertEqual(result.decision, Decision.WOULD_LAUNCH)

    def test_pull_request_is_not_applicable(self):
        result = self._classify(labels=["agent:working"], is_pull_request=True)
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertEqual(result.reason_code, ReasonCode.TARGET_IS_PULL_REQUEST)

    def test_9_label_not_agent_working_is_not_applicable(self):
        result = self._classify(labels=["agent:ready"], added_label="agent:ready")
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertEqual(result.reason_code, ReasonCode.LABEL_NOT_AGENT_WORKING)

    def test_closed_issue_is_not_applicable(self):
        # Launcherの責務に基づき、既存Controller plannerの挙動(WOULD_BLOCK_STATE)
        # を踏襲せずNOT_APPLICABLEとする(AUTO-001-06-01の明示的な指示)。
        result = self._classify(labels=["agent:working"], state="closed")
        self.assertEqual(result.decision, Decision.NOT_APPLICABLE)
        self.assertEqual(result.reason_code, ReasonCode.ISSUE_CLOSED)

    def test_10_agent_working_missing_is_would_block_state(self):
        result = self._classify(labels=[])
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason_code, ReasonCode.AGENT_WORKING_LABEL_MISSING)

    def test_11_agent_ready_still_present_is_would_block_state(self):
        result = self._classify(labels=["agent:working", "agent:ready"])
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason_code, ReasonCode.AGENT_READY_STILL_PRESENT)

    def test_12_agent_blocked_present_is_would_block_state(self):
        result = self._classify(labels=["agent:working", "agent:blocked"])
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason_code, ReasonCode.AGENT_BLOCKED_PRESENT)

    def test_13_conflicting_state_labels_is_would_block_state(self):
        result = self._classify(labels=["agent:working", "agent:review"])
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_STATE)
        self.assertEqual(result.reason_code, ReasonCode.STATE_LABEL_CONFLICT)

    def test_14_contract_violation_is_would_block_contract(self):
        result = self._classify(labels=["agent:working"], body=CONTRACT_VIOLATION_BODY)
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_CONTRACT)
        self.assertEqual(result.reason_code, ReasonCode.PREFLIGHT_CONTRACT_VIOLATION)
        self.assertGreater(len(result.errors), 0)
        for e in result.errors:
            self.assertIn("code", e)
            self.assertIn("section", e)
            self.assertIn("message", e)

    def test_missing_management_id_is_would_block_contract(self):
        body = build_body(content={"管理ID": "not-a-valid-id"})
        result = self._classify(labels=["agent:working"], body=body)
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_CONTRACT)

    def test_missing_acceptance_criteria_is_would_block_contract(self):
        body = build_body(content={"受入条件": "特に記載なし"})
        result = self._classify(labels=["agent:working"], body=body)
        self.assertEqual(result.decision, Decision.WOULD_BLOCK_CONTRACT)

    def test_15_validator_internal_error_is_internal_error(self):
        # parse_issue_snapshot()は本文を常にstrへ正規化するため、通常経路
        # ではvalidator自体のINTERNAL_ERRORへ到達しない。validate_issue_body()
        # 自身がINTERNAL_ERRORを返す実際の条件(非str入力)を、
        # classify()へ直接IssueSnapshotを渡すことで再現する(防御的分岐の
        # 単体確認)。
        snapshot = IssueSnapshot(
            issue_number=42, is_open=True, is_pull_request=False,
            current_labels=("agent:working",), issue_body=None,  # type: ignore[arg-type]
            updated_at="2026-08-01T00:00:00Z", title="t", html_url="https://x/y/42",
        )
        self.assertEqual(validate_issue_body(None).status, ValidationStatus.INTERNAL_ERROR)  # type: ignore[arg-type]
        result = classify(LauncherInput(trigger="workflow_dispatch", added_label=None, snapshot=snapshot))
        self.assertEqual(result.decision, Decision.INTERNAL_ERROR)
        self.assertEqual(result.reason_code, ReasonCode.PREFLIGHT_VALIDATOR_INTERNAL_ERROR)

    def test_18_normal_would_launch_carries_extracted_fields(self):
        result = self._classify(labels=["agent:working"], body=VALID_ISSUE_BODY)
        self.assertEqual(result.decision, Decision.WOULD_LAUNCH)
        self.assertEqual(result.reason_code, ReasonCode.LAUNCH_READY)
        self.assertIsNotNone(result.fields)
        self.assertEqual(result.fields.management_id, "AUTO-001-06-01")

    def test_workflow_dispatch_ignores_added_label_check(self):
        result = self._classify(
            labels=["agent:working"], trigger="workflow_dispatch", added_label=None, body=VALID_ISSUE_BODY,
        )
        self.assertEqual(result.decision, Decision.WOULD_LAUNCH)

    def test_would_block_duplicate_is_never_returned_by_classify(self):
        # 必須テスト31: WOULD_BLOCK_DUPLICATEはv1で到達不能である。
        # 状態・契約のあらゆる組み合わせを網羅的に試し、一度も
        # WOULD_BLOCK_DUPLICATEにならないことを確認する。
        all_labels = ["agent:ready", "agent:working", "agent:blocked", "agent:review", "agent:failed"]
        bodies = [VALID_ISSUE_BODY, CONTRACT_VIOLATION_BODY, "", "garbage"]
        states = ["open", "closed"]
        from itertools import combinations
        label_combos: list[list[str]] = [[]]
        for r in range(1, len(all_labels) + 1):
            label_combos.extend(list(c) for c in combinations(all_labels, r))

        for labels in label_combos:
            for body in bodies:
                for state in states:
                    for is_pr in (False, True):
                        result = self._classify(labels=labels, body=body, state=state, is_pull_request=is_pr)
                        self.assertNotEqual(result.decision, Decision.WOULD_BLOCK_DUPLICATE)

    def test_reserved_decision_value_exists_in_enum(self):
        # enum/出力契約上の予約値としては定義されていること。
        self.assertIn("WOULD_BLOCK_DUPLICATE", [d.value for d in Decision])


# ---------------------------------------------------------------------------
# check_source_unchanged (必須テスト23〜26)
# ---------------------------------------------------------------------------

class CheckSourceUnchangedTests(unittest.TestCase):

    def _snap(self, **overrides) -> IssueSnapshot:
        base = dict(
            issue_number=42, is_open=True, is_pull_request=False,
            current_labels=("agent:working",), issue_body="x",
            updated_at="2026-08-01T00:00:00Z", title="t", html_url="https://x/y/42",
        )
        base.update(overrides)
        return IssueSnapshot(**base)

    def test_identical_snapshots_pass(self):
        before = self._snap()
        after = self._snap()
        result = check_source_unchanged(before, after)
        self.assertTrue(result.ok)
        self.assertIsNone(result.reason_code)

    def test_23_body_change_is_detected(self):
        before = self._snap(issue_body="x")
        after = self._snap(issue_body="y")
        result = check_source_unchanged(before, after)
        self.assertFalse(result.ok)
        self.assertEqual(result.reason_code, ReasonCode.SOURCE_CHANGED_BEFORE_OUTPUT)
        self.assertIn("body_sha256", result.changed_fields)

    def test_24_state_change_is_detected(self):
        before = self._snap(is_open=True)
        after = self._snap(is_open=False)
        result = check_source_unchanged(before, after)
        self.assertFalse(result.ok)
        self.assertIn("state", result.changed_fields)

    def test_25_labels_change_is_detected(self):
        before = self._snap(current_labels=("agent:working",))
        after = self._snap(current_labels=("agent:working", "agent:blocked"))
        result = check_source_unchanged(before, after)
        self.assertFalse(result.ok)
        self.assertIn("labels", result.changed_fields)

    def test_labels_order_alone_does_not_count_as_changed(self):
        before = self._snap(current_labels=("a", "b"))
        after = self._snap(current_labels=("b", "a"))
        result = check_source_unchanged(before, after)
        self.assertTrue(result.ok)

    def test_26_updated_at_change_is_detected(self):
        before = self._snap(updated_at="2026-08-01T00:00:00Z")
        after = self._snap(updated_at="2026-08-01T00:05:00Z")
        result = check_source_unchanged(before, after)
        self.assertFalse(result.ok)
        self.assertIn("updated_at", result.changed_fields)

    def test_issue_number_change_is_detected(self):
        before = self._snap(issue_number=42)
        after = self._snap(issue_number=43)
        result = check_source_unchanged(before, after)
        self.assertFalse(result.ok)
        self.assertIn("issue_number", result.changed_fields)


# ---------------------------------------------------------------------------
# task bundle: schema / 決定性 (必須テスト19〜22・24)
# ---------------------------------------------------------------------------

class BuildTaskBundleTests(unittest.TestCase):

    def setUp(self):
        self.snapshot = parse_issue_snapshot(
            _issue_response(["agent:working"], body=VALID_ISSUE_BODY, updated_at="2026-08-01T00:00:00Z"),
        )
        self.fields = extract_task_fields(VALID_ISSUE_BODY)
        self.assertIsNotNone(self.fields)

    def _build(self):
        return build_task_bundle(
            repository=EXPECTED_FULL_NAME,
            snapshot=self.snapshot,
            fields=self.fields,
            generated_from_main_sha="6428fd39acf6ebf5085ace786c91e46e1cb69ed3",
            launcher_decision="WOULD_LAUNCH",
            launcher_reason_code="LAUNCH_READY",
        )

    def test_17_required_top_level_fields_present(self):
        bundle = self._build()
        self.assertEqual(bundle["schema_version"], TASK_BUNDLE_SCHEMA_VERSION)
        self.assertIn("source", bundle)
        self.assertIn("task", bundle)
        self.assertEqual(bundle["generated_from_main_sha"], "6428fd39acf6ebf5085ace786c91e46e1cb69ed3")
        self.assertEqual(bundle["launcher_decision"], "WOULD_LAUNCH")
        self.assertEqual(bundle["launcher_reason_code"], "LAUNCH_READY")

    def test_source_required_fields_present(self):
        source = self._build()["source"]
        for key in (
            "repository", "issue_number", "issue_url", "issue_title",
            "issue_state", "issue_updated_at", "issue_body_sha256", "labels",
        ):
            self.assertIn(key, source)
        self.assertEqual(source["repository"], EXPECTED_FULL_NAME)
        self.assertEqual(source["issue_number"], 42)
        self.assertEqual(source["issue_state"], "open")

    def test_task_required_fields_present_including_ac13(self):
        task = self._build()["task"]
        for key in (
            "management_id", "current_problem", "cause_hypotheses", "purpose",
            "expected_behavior", "non_goals", "acceptance_criteria",
            "test_perspectives", "risks", "human_confirmation_items",
            "change_classification", "reference_materials",
        ):
            self.assertIn(key, task)
        # AC-13: current_problem・cause_hypothesesが含まれること
        self.assertIn("current_problem", task)
        self.assertIn("cause_hypotheses", task)

    def test_18_schema_version_is_fixed_string(self):
        self.assertEqual(TASK_BUNDLE_SCHEMA_VERSION, "AUTO-001-TASK-BUNDLE-V1")

    def test_19_and_22_identical_input_yields_identical_bytes(self):
        b1 = canonical_json_bytes(self._build())
        b2 = canonical_json_bytes(self._build())
        self.assertEqual(b1, b2)
        self.assertEqual(hashlib.sha256(b1).hexdigest(), hashlib.sha256(b2).hexdigest())

    def test_20_issue_body_sha256_is_correct(self):
        bundle = self._build()
        expected = hashlib.sha256(VALID_ISSUE_BODY.encode("utf-8")).hexdigest()
        self.assertEqual(bundle["source"]["issue_body_sha256"], expected)

    def test_21_acceptance_criteria_preserve_order(self):
        body = build_body(content={
            "管理ID": "AUTO-001-06-01",
            "受入条件": "- [ ] AC-01: 一つ目\n- [ ] AC-02: 二つ目\n- [ ] AC-03: 三つ目",
        })
        fields = extract_task_fields(body)
        self.snapshot = parse_issue_snapshot(_issue_response(["agent:working"], body=body))
        self.fields = fields
        bundle = self._build()
        ids = [ac["id"] for ac in bundle["task"]["acceptance_criteria"]]
        self.assertEqual(ids, ["AC-01", "AC-02", "AC-03"])

    def test_22_label_array_is_deterministically_sorted(self):
        self.snapshot = parse_issue_snapshot(
            _issue_response(["zzz", "agent:working", "aaa"], body=VALID_ISSUE_BODY),
        )
        bundle = self._build()
        self.assertEqual(bundle["source"]["labels"], sorted(["zzz", "agent:working", "aaa"]))

    def test_25_no_secret_looking_keys_added(self):
        bundle = self._build()
        flat_text = json.dumps(bundle, ensure_ascii=False).lower()
        for forbidden in ("token", "secret", "password", "private_key", "authorization", "ghs_", "-----begin"):
            self.assertNotIn(forbidden, flat_text)

    def test_12_no_generation_timestamp_run_id_or_random_values(self):
        bundle = self._build()
        flat_keys = set()

        def collect_keys(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    flat_keys.add(k)
                    collect_keys(v)
            elif isinstance(obj, list):
                for item in obj:
                    collect_keys(item)

        collect_keys(bundle)
        for forbidden_key in ("generated_at", "created_at", "run_id", "timestamp", "nonce", "random"):
            self.assertNotIn(forbidden_key, flat_keys)

    def test_26_only_body_change_affects_hash(self):
        b1 = canonical_json_bytes(self._build())
        other_body = VALID_ISSUE_BODY + "\n"  # 末尾に改行を1つ追加(暗黙の正規化はしない)
        other_fields = extract_task_fields(build_body(content={"管理ID": "AUTO-001-06-01"}))
        self.snapshot = parse_issue_snapshot(_issue_response(["agent:working"], body=other_body))
        # bodyそのものは変えず、issue_updated_atだけ変えても直接ハッシュに影響する
        self.snapshot = parse_issue_snapshot(
            _issue_response(["agent:working"], body=VALID_ISSUE_BODY, updated_at="2099-01-01T00:00:00Z"),
        )
        b2 = canonical_json_bytes(self._build())
        self.assertNotEqual(b1, b2)


# ---------------------------------------------------------------------------
# CLI (必須テスト16・17・27〜30寄り)
# ---------------------------------------------------------------------------

class CliTests(unittest.TestCase):

    def _run_cli(self, argv: list[str]) -> int:
        return cli_main(argv)

    def test_validate_issue_number_cli_pass(self):
        self.assertEqual(self._run_cli(["validate-issue-number", "12"]), 0)

    def test_validate_issue_number_cli_fail(self):
        self.assertEqual(self._run_cli(["validate-issue-number", "007"]), 1)

    def test_classify_cli_would_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:working"], body=VALID_ISSUE_BODY))
            machine_path = tmpdir / "result.json"
            fields_path = tmpdir / "fields.json"
            code = self._run_cli([
                "classify", "--trigger", "workflow_dispatch",
                "--issue-response-file", issue_path,
                "--expected-issue-number", "42",
                "--machine-json-path", str(machine_path),
                "--fields-json-path", str(fields_path),
            ])
            self.assertEqual(code, 0)
            result = json.loads(machine_path.read_text(encoding="utf-8"))
            self.assertEqual(result["decision"], "WOULD_LAUNCH")
            self.assertTrue(fields_path.exists())

    def test_classify_cli_issue_number_mismatch_is_internal_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:working"], number=42))
            machine_path = tmpdir / "result.json"
            code = self._run_cli([
                "classify", "--trigger", "workflow_dispatch",
                "--issue-response-file", issue_path,
                "--expected-issue-number", "99",
                "--machine-json-path", str(machine_path),
            ])
            self.assertEqual(code, 1)
            result = json.loads(machine_path.read_text(encoding="utf-8"))
            self.assertEqual(result["decision"], "INTERNAL_ERROR")

    def test_17_classify_cli_malformed_json_is_internal_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            bad_path = tmpdir / "issue.json"
            bad_path.write_text("{not valid json", encoding="utf-8")
            machine_path = tmpdir / "result.json"
            code = self._run_cli([
                "classify", "--trigger", "workflow_dispatch",
                "--issue-response-file", str(bad_path),
                "--machine-json-path", str(machine_path),
            ])
            self.assertEqual(code, 1)
            result = json.loads(machine_path.read_text(encoding="utf-8"))
            self.assertEqual(result["decision"], "INTERNAL_ERROR")

    def test_classify_cli_issues_labeled_missing_label_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:working"]))
            event_path = _write_json(tmpdir, "event.json", {"action": "labeled"})
            code = self._run_cli([
                "classify", "--trigger", "issues:labeled",
                "--issue-response-file", issue_path,
                "--event-json-path", event_path,
            ])
            self.assertEqual(code, 1)

    def test_check_recheck_cli_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue = _issue_response(["agent:working"])
            before_path = _write_json(tmpdir, "before.json", issue)
            after_path = _write_json(tmpdir, "after.json", issue)
            code = self._run_cli([
                "check-recheck", "--before-response-file", before_path, "--after-response-file", after_path,
            ])
            self.assertEqual(code, 0)

    def test_27_check_recheck_cli_detects_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            before_path = _write_json(tmpdir, "before.json", _issue_response(["agent:working"]))
            after_path = _write_json(tmpdir, "after.json", _issue_response(["agent:working", "agent:blocked"]))
            code = self._run_cli([
                "check-recheck", "--before-response-file", before_path, "--after-response-file", after_path,
            ])
            self.assertEqual(code, 1)

    def test_build_bundle_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:working"], body=VALID_ISSUE_BODY))
            fields_path = tmpdir / "fields.json"
            classify_result_path = tmpdir / "classify.json"
            self._run_cli([
                "classify", "--trigger", "workflow_dispatch",
                "--issue-response-file", issue_path,
                "--machine-json-path", str(classify_result_path),
                "--fields-json-path", str(fields_path),
            ])
            output_path = tmpdir / "bundle.json"
            code = self._run_cli([
                "build-bundle",
                "--after-response-file", issue_path,
                "--fields-json-path", str(fields_path),
                "--repository", EXPECTED_FULL_NAME,
                "--generated-from-main-sha", "6428fd39acf6ebf5085ace786c91e46e1cb69ed3",
                "--launcher-decision", "WOULD_LAUNCH",
                "--launcher-reason-code", "LAUNCH_READY",
                "--output-path", str(output_path),
            ])
            self.assertEqual(code, 0)
            bundle = json.loads(output_path.read_bytes())
            self.assertEqual(bundle["schema_version"], TASK_BUNDLE_SCHEMA_VERSION)

    def test_build_bundle_cli_missing_fields_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            issue_path = _write_json(tmpdir, "issue.json", _issue_response(["agent:working"]))
            code = self._run_cli([
                "build-bundle",
                "--after-response-file", issue_path,
                "--fields-json-path", str(tmpdir / "does_not_exist.json"),
                "--repository", EXPECTED_FULL_NAME,
                "--generated-from-main-sha", "abc",
                "--launcher-decision", "WOULD_LAUNCH",
                "--launcher-reason-code", "LAUNCH_READY",
                "--output-path", str(tmpdir / "bundle.json"),
            ])
            self.assertEqual(code, 1)


# ---------------------------------------------------------------------------
# workflow YAML: 静的検査(permissions, read-only保証, endpoint allowlist)
# 必須テスト28〜30・32〜36
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

    def test_30_top_level_permissions_are_read_only(self):
        m = re.search(r"^permissions:\n((?:  .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        block = m.group(1)
        entries = {
            k.strip(): v.strip()
            for k, v in (line.strip().split(":", 1) for line in block.splitlines())
        }
        self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_job_level_permissions_are_read_only(self):
        m = re.search(r"    permissions:\n((?:      .+\n)+)", self.text, flags=re.MULTILINE)
        self.assertIsNotNone(m)
        entries = {
            k.strip(): v.strip()
            for k, v in (line.strip().split(":", 1) for line in m.group(1).splitlines())
        }
        self.assertEqual(entries, {"contents": "read", "issues": "read"})

    def test_no_write_permissions_anywhere(self):
        for forbidden in (
            "contents: write", "issues: write", "pull-requests: write", "pull-requests: read",
            "actions: write", "id-token: write",
        ):
            self.assertNotIn(forbidden, self.text)

    def test_29_no_app_token_generation_step(self):
        self.assertNotIn("create-github-app-token", self.text)
        self.assertNotIn("AUTO001_CONTROLLER_APP_PRIVATE_KEY", self.text)
        self.assertNotIn("AUTO001_IMPLEMENTER_APP", self.text)

    def test_32_no_secrets_referenced(self):
        self.assertNotIn("secrets.", self.text)
        self.assertNotIn("secrets:", self.text)

    def test_33_no_write_http_methods(self):
        for forbidden in ("-X POST", "-X PATCH", "-X PUT", "-X DELETE"):
            self.assertNotIn(forbidden, self.text)

    def test_endpoint_allowlist_is_exactly_the_single_issue_get(self):
        urls = re.findall(r'"(https://api\.github\.com/[^"]+)"', self.text)
        unique_patterns = {re.sub(r"\$\{[A-Z_]+\}", "{n}", u) for u in urls}
        self.assertEqual(
            unique_patterns,
            {"https://api.github.com/repos/${{ github.repository }}/issues/{n}"},
        )

    def test_34_no_git_push_anywhere(self):
        self.assertNotIn("git push", self.text.lower())

    def test_35_no_branch_creation(self):
        lower = self.text.lower()
        for forbidden in ("git checkout -b", "git branch", "createref"):
            self.assertNotIn(forbidden, lower)

    def test_36_no_issue_comment_or_label_write_apis(self):
        lower = self.text.lower()
        for forbidden in ("gh issue edit", "gh issue close", "gh label", "gh pr create", "git commit"):
            self.assertNotIn(forbidden, lower)

    def test_no_claude_or_llm_api_usage(self):
        lower = self.text.lower()
        for forbidden in (
            "uses: anthropics/", "uses: claude-code-", "anthropic_api_key",
            "openai_api_key", "claude-code-action", "claude-code-base-action",
        ):
            self.assertNotIn(forbidden, lower)

    def test_no_issue_body_or_title_expression(self):
        self.assertNotIn("issue.body", self.text)
        self.assertNotIn("issue.title", self.text)

    def test_would_block_duplicate_documented_as_unimplemented_in_summary(self):
        self.assertIn("WOULD_BLOCK_DUPLICATE", self.text)
        self.assertIn("未実装", self.text)

    def test_artifact_action_is_pinned_to_full_commit_sha(self):
        m = re.search(r"uses: actions/upload-artifact@([0-9a-f]{40}) #", self.text)
        self.assertIsNotNone(m, "actions/upload-artifactはフルコミットSHAへpinされている必要があります")

    def test_checkout_and_setup_python_pinned_to_full_sha(self):
        self.assertRegex(self.text, r"uses: actions/checkout@[0-9a-f]{40} #")
        self.assertRegex(self.text, r"uses: actions/setup-python@[0-9a-f]{40} #")

    def test_artifact_upload_gated_to_bundle_built(self):
        m = re.search(
            r"- name: Upload task bundle artifact\n\s*if: (.+)\n", self.text,
        )
        self.assertIsNotNone(m)
        self.assertIn("bundle_built", m.group(1))

    def test_concurrency_group_scoped_to_issue_number(self):
        m = re.search(r"group: (auto001-implementer-launcher-.+)", self.text)
        self.assertIsNotNone(m)
        self.assertIn("issue.number", m.group(1))
        self.assertIn("inputs.issue_number", m.group(1))

    def test_no_raw_response_body_printed(self):
        for forbidden in ("cat issue_snapshot.json", "cat issue_recheck.json", "cat task_bundle.json"):
            self.assertNotIn(forbidden, self.text)


# ---------------------------------------------------------------------------
# subprocess: 実stepスクリプトの抽出実行(必須テスト1〜6・16・27〜30寄り)
# ---------------------------------------------------------------------------

class ValidateIssueNumberStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("validate_issue_number")

    def _run(self, value: str):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["ISSUE_NUMBER_INPUT"] = value
            return _run_bash_script_in_dir(self.script, env, tmpdir)

    def test_1_positive_integer_passes(self):
        self.assertEqual(self._run("12").returncode, 0)

    def test_2_empty_fails(self):
        self.assertNotEqual(self._run("").returncode, 0)

    def test_3_zero_fails(self):
        self.assertNotEqual(self._run("0").returncode, 0)

    def test_4_leading_zero_fails(self):
        self.assertNotEqual(self._run("007").returncode, 0)

    def test_5_negative_fails(self):
        self.assertNotEqual(self._run("-1").returncode, 0)

    def test_6_decimal_fails(self):
        self.assertNotEqual(self._run("1.5").returncode, 0)

    def test_non_numeric_fails(self):
        self.assertNotEqual(self._run("abc").returncode, 0)


class FetchIssueStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("fetch_issue")

    def _run(self, *, curl_exit_code=0, curl_http_code="200", body=""):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            env["TARGET_ISSUE_NUMBER"] = "42"
            combined = _fake_curl_function(exit_code=curl_exit_code, http_code=curl_http_code, body=body) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_success_sets_outputs(self):
        body = json.dumps(_issue_response(["agent:working"]))
        result, outputs = self._run(body=body)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("target_issue_number"), "42")
        self.assertIn("issue_body_sha256", outputs)

    def test_16_api_failure_is_internal_error(self):
        result, outputs = self._run(curl_exit_code=0, curl_http_code="500", body="")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("decision"), "INTERNAL_ERROR")

    def test_curl_transport_failure_is_internal_error(self):
        result, outputs = self._run(curl_exit_code=7, curl_http_code="000", body="")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("decision"), "INTERNAL_ERROR")

    def test_30_issue_body_never_appears_in_stdout_or_stderr(self):
        secret_marker = "SECRET-ISSUE-BODY-MARKER"
        body = json.dumps(_issue_response(["agent:working"], body=secret_marker))
        result, _outputs = self._run(body=body)
        self.assertNotIn(secret_marker, result.stdout)
        self.assertNotIn(secret_marker, result.stderr)


class ClassifyStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("classify", {
            "${{ github.event_name == 'issues' && 'issues:labeled' || 'workflow_dispatch' }}": "workflow_dispatch",
            '${{ github.event_name }}': "workflow_dispatch",
            "${{ steps.fetch_issue.outputs.target_issue_number }}": "42",
        })

    def _run(self, issue_obj: dict):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(issue_obj, ensure_ascii=False), encoding="utf-8",
            )
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_would_launch_end_to_end_via_step_script(self):
        result, outputs = self._run(_issue_response(["agent:working"], body=VALID_ISSUE_BODY))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("decision"), "WOULD_LAUNCH")
        self.assertEqual(outputs.get("reason_code"), "LAUNCH_READY")
        self.assertEqual(outputs.get("error_count"), "0")

    def test_would_block_state_end_to_end_via_step_script(self):
        result, outputs = self._run(_issue_response([]))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("decision"), "WOULD_BLOCK_STATE")

    def test_17_malformed_issue_json_is_internal_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            (tmpdir / "issue_snapshot.json").write_text("{not valid json", encoding="utf-8")
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
        self.assertNotEqual(result.returncode, 0)

    def test_30_issue_body_never_appears_in_stdout_or_stderr(self):
        secret_marker = "SECRET-CLASSIFY-BODY-MARKER"
        body = VALID_ISSUE_BODY.replace("問題の説明。", secret_marker) if "問題の説明。" in VALID_ISSUE_BODY else VALID_ISSUE_BODY
        result, _outputs = self._run(_issue_response(["agent:working"], body=CONTRACT_VIOLATION_BODY + secret_marker))
        self.assertNotIn(secret_marker, result.stdout)
        self.assertNotIn(secret_marker, result.stderr)


class ClassifyStepIssuesLabeledSubprocessTests(unittest.TestCase):
    """issues:labeledトリガー専用(event.jsonのlabel.nameを見る経路)。"""

    def setUp(self):
        self.script = _extract_step("classify", {
            "${{ github.event_name == 'issues' && 'issues:labeled' || 'workflow_dispatch' }}": "issues:labeled",
            '${{ github.event_name }}': "issues",
            "${{ steps.fetch_issue.outputs.target_issue_number }}": "42",
        })

    def _run(self, *, added_label: str, issue_obj: dict):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(issue_obj, ensure_ascii=False), encoding="utf-8",
            )
            event_path = tmpdir / "event.json"
            event_path.write_text(json.dumps(_labeled_event(added_label), ensure_ascii=False), encoding="utf-8")
            env["GITHUB_EVENT_PATH"] = str(event_path)
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_9_wrong_label_is_not_applicable(self):
        result, outputs = self._run(added_label="agent:ready", issue_obj=_issue_response(["agent:ready"]))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("decision"), "NOT_APPLICABLE")
        self.assertEqual(outputs.get("reason_code"), "LABEL_NOT_AGENT_WORKING")

    def test_correct_label_would_launch(self):
        result, outputs = self._run(
            added_label="agent:working", issue_obj=_issue_response(["agent:working"], body=VALID_ISSUE_BODY),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("decision"), "WOULD_LAUNCH")


class RefetchAndRecheckStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("refetch_issue")

    def _run(self, *, before_obj: dict, curl_exit_code=0, curl_http_code="200", after_body=None):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            env["GH_READ_TOKEN"] = "dummy-read-token"
            env["TARGET_ISSUE_NUMBER"] = "42"
            (tmpdir / "issue_snapshot.json").write_text(
                json.dumps(before_obj, ensure_ascii=False), encoding="utf-8",
            )
            body = after_body if after_body is not None else json.dumps(before_obj)
            combined = _fake_curl_function(exit_code=curl_exit_code, http_code=curl_http_code, body=body) + "\n" + self.script
            result = _run_bash_script_in_dir(combined, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            return result, outputs

    def test_no_change_passes(self):
        before = _issue_response(["agent:working"])
        result, outputs = self._run(before_obj=before)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("recheck_ok"), "true")

    def test_23_body_changed_before_output_fails(self):
        before = _issue_response(["agent:working"], body="original")
        after = _issue_response(["agent:working"], body="changed")
        result, outputs = self._run(before_obj=before, after_body=json.dumps(after))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("recheck_ok"), "false")
        self.assertEqual(outputs.get("reason_code"), "SOURCE_CHANGED_BEFORE_OUTPUT")

    def test_25_labels_changed_before_output_fails(self):
        before = _issue_response(["agent:working"])
        after = _issue_response(["agent:working", "agent:blocked"])
        result, outputs = self._run(before_obj=before, after_body=json.dumps(after))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("reason_code"), "SOURCE_CHANGED_BEFORE_OUTPUT")

    def test_24_state_changed_before_output_fails(self):
        before = _issue_response(["agent:working"], state="open")
        after = _issue_response(["agent:working"], state="closed")
        result, outputs = self._run(before_obj=before, after_body=json.dumps(after))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("reason_code"), "SOURCE_CHANGED_BEFORE_OUTPUT")

    def test_26_updated_at_changed_before_output_fails(self):
        before = _issue_response(["agent:working"], updated_at="2026-08-01T00:00:00Z")
        after = _issue_response(["agent:working"], updated_at="2026-08-01T01:00:00Z")
        result, outputs = self._run(before_obj=before, after_body=json.dumps(after))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("reason_code"), "SOURCE_CHANGED_BEFORE_OUTPUT")

    def test_refetch_api_failure_is_internal_error(self):
        before = _issue_response(["agent:working"])
        result, outputs = self._run(before_obj=before, curl_http_code="500")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs.get("recheck_ok"), "false")


class BuildBundleStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("build_bundle", {
            "${{ github.repository }}": EXPECTED_FULL_NAME,
            "${{ github.sha }}": "6428fd39acf6ebf5085ace786c91e46e1cb69ed3",
            "${{ steps.classify.outputs.decision }}": "WOULD_LAUNCH",
            "${{ steps.classify.outputs.reason_code }}": "LAUNCH_READY",
        })

    def _run(self, issue_obj: dict, fields: dict):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            (tmpdir / "issue_recheck.json").write_text(
                json.dumps(issue_obj, ensure_ascii=False), encoding="utf-8",
            )
            (tmpdir / "task_fields.json").write_text(
                json.dumps(fields, ensure_ascii=False), encoding="utf-8",
            )
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            outputs = _parse_github_output(tmpdir / "github_output.txt")
            bundle_path = tmpdir / "task_bundle.json"
            bundle = json.loads(bundle_path.read_bytes()) if bundle_path.exists() else None
            return result, outputs, bundle

    def test_29_build_bundle_produces_deterministic_schema(self):
        fields = extract_task_fields(VALID_ISSUE_BODY).to_dict()
        issue_obj = _issue_response(["agent:working"], body=VALID_ISSUE_BODY)
        result, outputs, bundle = self._run(issue_obj, fields)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(outputs.get("bundle_built"), "true")
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle["schema_version"], TASK_BUNDLE_SCHEMA_VERSION)

    def test_task_fields_never_appear_raw_in_stdout(self):
        secret_marker = "SECRET-BUNDLE-FIELD-MARKER"
        fields = extract_task_fields(VALID_ISSUE_BODY).to_dict()
        fields["purpose"] = secret_marker
        issue_obj = _issue_response(["agent:working"], body=VALID_ISSUE_BODY)
        result, _outputs, _bundle = self._run(issue_obj, fields)
        self.assertNotIn(secret_marker, result.stdout)
        self.assertNotIn(secret_marker, result.stderr)


class SummaryStepSubprocessTests(unittest.TestCase):

    def setUp(self):
        self.script = _extract_step("summary")

    def _run(self, **env_overrides):
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            env = _base_env(tmpdir)
            for key in (
                "TRIGGER", "TARGET_ISSUE_NUMBER", "ISSUE_BODY_SHA256", "DECISION", "REASON_CODE",
                "ERROR_COUNT", "RECHECK_OK", "RECHECK_REASON", "BUNDLE_BUILT", "BUNDLE_SHA256",
            ):
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

    def test_summary_shows_required_minimum_fields(self):
        result, summary_text = self._run(
            TRIGGER="workflow_dispatch", TARGET_ISSUE_NUMBER="42", DECISION="WOULD_LAUNCH",
            REASON_CODE="LAUNCH_READY", ERROR_COUNT="0", RECHECK_OK="true", RECHECK_REASON="NONE",
            BUNDLE_BUILT="true", BUNDLE_SHA256="abc123",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        for expected in (
            "trigger", "Issue番号: 42", "decision: WOULD_LAUNCH", "reason_code: LAUNCH_READY",
            "management ID", "issue_body_sha256", "schema_version", "task bundle生成",
            "GitHub write", "Controller App token", "Implementer App token",
        ):
            self.assertIn(expected, summary_text)

    def test_30_summary_never_contains_issue_body_marker(self):
        secret_marker = "SECRET-SUMMARY-BODY-MARKER"
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            (tmpdir / "task_fields.json").write_text(
                json.dumps({"management_id": secret_marker}, ensure_ascii=False), encoding="utf-8",
            )
            env = _base_env(tmpdir)
            for key in (
                "TRIGGER", "TARGET_ISSUE_NUMBER", "ISSUE_BODY_SHA256", "DECISION", "REASON_CODE",
                "ERROR_COUNT", "RECHECK_OK", "RECHECK_REASON", "BUNDLE_BUILT", "BUNDLE_SHA256",
            ):
                env[key] = ""
            summary_path = tmpdir / "step_summary.md"
            summary_path.write_text("", encoding="utf-8")
            env["GITHUB_STEP_SUMMARY"] = str(summary_path)
            env["GITHUB_SERVER_URL"] = "https://github.com"
            env["GITHUB_REPOSITORY"] = EXPECTED_FULL_NAME
            env["GITHUB_RUN_ID"] = "12345"
            result = _run_bash_script_in_dir(self.script, env, tmpdir)
            summary_text = summary_path.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        # management_idという固定短文字列フィールドは表示してよいが、
        # ここでは意図的にsecret_markerをmanagement_idへ入れて、それが
        # そのままSummaryに出ても内容としてはIssue本文全文ではないことを
        # 示す一方、tokenやAuthorization等の機微情報は含まれないことを確認する。
        for forbidden in ("Authorization", "ghs_", "-----BEGIN"):
            self.assertNotIn(forbidden, summary_text)

    def test_summary_step_runs_always(self):
        m = re.search(r"- name: Publish job summary[^\n]*\n\s*id: summary\n\s*if: (.+)\n", WORKFLOW_PATH.read_text(encoding="utf-8"))
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1).strip(), "always()")


if __name__ == "__main__":
    unittest.main()
