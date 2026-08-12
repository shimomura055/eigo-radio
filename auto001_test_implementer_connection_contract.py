"""scripts/implementer_connection_contract.py (AUTO-001-06-02-02) の単体テスト。

外部API・外部ネットワークは一切使わない。GitHub API・Claude Code/Implementerの
起動も行わない。すべてPythonのdict fixtureとファイルI/O(このリポジトリ内の
schema/example JSONの読み込みだけ)で完結する。
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from scripts.implementer_connection_contract import (
    PROHIBITED_OPERATIONS,
    TASK_BUNDLE_SCHEMA_VERSION_CONST,
    ConnectionDecision,
    ValidationResult,
    build_logical_task_key,
    validate_envelope,
    validate_plan_result,
)
from scripts.implementer_launcher import TASK_BUNDLE_SCHEMA_VERSION

REPO_ROOT = Path(__file__).resolve().parent
SCHEMAS_DIR = REPO_ROOT / "docs" / "automation" / "schemas"
EXAMPLES_DIR = REPO_ROOT / "docs" / "automation" / "examples"

REPOSITORY = "shimomura055/eigo-radio"
ISSUE_NUMBER = 999
MANAGEMENT_ID = "AUTO-999-DEMO01"
BASE_SHA = "012330a6c340bcd9ae30f006f2e51df44332bb81"


def _canonical_json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def build_task_bundle_fixture(
    *,
    repository: str = REPOSITORY,
    issue_number: int = ISSUE_NUMBER,
    management_id: str = MANAGEMENT_ID,
    schema_version: str = TASK_BUNDLE_SCHEMA_VERSION_CONST,
) -> dict:
    return {
        "generated_from_main_sha": BASE_SHA,
        "launcher_decision": "WOULD_LAUNCH",
        "launcher_reason_code": "LAUNCH_READY",
        "schema_version": schema_version,
        "source": {
            "issue_body_sha256": "0" * 64,
            "issue_number": issue_number,
            "issue_state": "open",
            "issue_title": "demo",
            "issue_updated_at": "2026-08-01T10:00:00Z",
            "issue_url": "https://github.com/shimomura055/eigo-radio/issues/999",
            "labels": ["agent:working"],
            "repository": repository,
        },
        "task": {
            "acceptance_criteria": [{"id": "AC-01", "description": "demo"}],
            "cause_hypotheses": "なし",
            "change_classification": {
                "サービス仕様変更": "なし",
                "リポジトリ運用仕様変更": "なし",
                "実装方法だけの変更": "いいえ",
            },
            "current_problem": "demo",
            "expected_behavior": "demo",
            "human_confirmation_items": "なし",
            "management_id": management_id,
            "non_goals": "demo",
            "purpose": "demo",
            "reference_materials": "なし",
            "risks": [],
            "test_perspectives": ["demo"],
        },
    }


def build_envelope_and_bundle(**overrides) -> tuple[dict, bytes, dict]:
    """有効なtask bundle + それに一致する有効なenvelopeの組を返す。
    overridesはenvelope側のfieldを個別に上書きするために使う。
    """
    task_bundle = build_task_bundle_fixture()
    tb_bytes = _canonical_json_bytes(task_bundle)
    task_bundle_sha256 = hashlib.sha256(tb_bytes).hexdigest()
    logical_task_key = build_logical_task_key(
        repository=REPOSITORY, issue_number=ISSUE_NUMBER,
        management_id=MANAGEMENT_ID, task_bundle_sha256=task_bundle_sha256,
    )
    execution_id = f"exec_{logical_task_key[:12]}_a1_testsuite01"
    envelope = {
        "schema_version": "1.0.0",
        "logical_task_key": logical_task_key,
        "execution_id": execution_id,
        "attempt": 1,
        "repository": REPOSITORY,
        "base_sha": BASE_SHA,
        "issue_number": ISSUE_NUMBER,
        "management_id": MANAGEMENT_ID,
        "task_bundle_schema_version": TASK_BUNDLE_SCHEMA_VERSION_CONST,
        "task_bundle_sha256": task_bundle_sha256,
        "task_bundle_file": "task_bundle.json",
        "prohibited_paths": [".github/**", "**/*secret*"],
        "prohibited_operations": list(PROHIBITED_OPERATIONS),
        "timeout_seconds": 3600,
        "stop_point": "PLAN_ONLY",
        "expected_output": "PLAN_RESULT_JSON",
        "human_approval_required": True,
    }
    envelope.update(overrides)
    return envelope, tb_bytes, task_bundle


def build_plan_result_for(envelope: dict, **overrides) -> dict:
    plan_result = {
        "schema_version": "1.0.0",
        "execution_id": envelope["execution_id"],
        "attempt": envelope["attempt"],
        "logical_task_key": envelope["logical_task_key"],
        "management_id": envelope["management_id"],
        "input_task_bundle_sha256": envelope["task_bundle_sha256"],
        "input_base_sha": envelope["base_sha"],
        "connection_decision": "ACCEPTED",
        "execution_status": "PLAN_COMPLETED",
        "next_action": "HUMAN_APPROVAL_REQUIRED",
        "summary": "demo summary",
        "current_problem_understanding": "demo understanding",
        "implementation_plan": ["step 1"],
        "proposed_changed_files": [
            {"path": "foo.py", "change_type": "modified", "purpose": "demo", "service_spec_impact": "NONE"},
        ],
        "proposed_test_plan": ["python -m unittest demo"],
        "prohibited_change_detected": False,
        "missing_information": [],
        "unresolved_items": [],
        "risks": [],
        "human_confirmation_items": [],
        "generated_at": "2026-08-01T12:00:00Z",
        "self_reported": True,
    }
    plan_result.update(overrides)
    return plan_result


class BuildLogicalTaskKeyTests(unittest.TestCase):
    def test_deterministic_same_input_same_output(self):
        a = build_logical_task_key(
            repository=REPOSITORY, issue_number=ISSUE_NUMBER,
            management_id=MANAGEMENT_ID, task_bundle_sha256="a" * 64,
        )
        b = build_logical_task_key(
            repository=REPOSITORY, issue_number=ISSUE_NUMBER,
            management_id=MANAGEMENT_ID, task_bundle_sha256="a" * 64,
        )
        self.assertEqual(a, b)

    def test_output_is_64_char_lowercase_hex(self):
        key = build_logical_task_key(
            repository=REPOSITORY, issue_number=ISSUE_NUMBER,
            management_id=MANAGEMENT_ID, task_bundle_sha256="a" * 64,
        )
        self.assertRegex(key, r"^[0-9a-f]{64}$")

    def test_different_repository_changes_key(self):
        a = build_logical_task_key(repository="x/y", issue_number=1, management_id="M", task_bundle_sha256="a" * 64)
        b = build_logical_task_key(repository="x/z", issue_number=1, management_id="M", task_bundle_sha256="a" * 64)
        self.assertNotEqual(a, b)

    def test_different_issue_number_changes_key(self):
        a = build_logical_task_key(repository="x/y", issue_number=1, management_id="M", task_bundle_sha256="a" * 64)
        b = build_logical_task_key(repository="x/y", issue_number=2, management_id="M", task_bundle_sha256="a" * 64)
        self.assertNotEqual(a, b)

    def test_different_management_id_changes_key(self):
        a = build_logical_task_key(repository="x/y", issue_number=1, management_id="M1", task_bundle_sha256="a" * 64)
        b = build_logical_task_key(repository="x/y", issue_number=1, management_id="M2", task_bundle_sha256="a" * 64)
        self.assertNotEqual(a, b)

    def test_different_task_bundle_sha256_changes_key(self):
        a = build_logical_task_key(repository="x/y", issue_number=1, management_id="M", task_bundle_sha256="a" * 64)
        b = build_logical_task_key(repository="x/y", issue_number=1, management_id="M", task_bundle_sha256="b" * 64)
        self.assertNotEqual(a, b)

    def test_matches_manual_canonical_json_sha256(self):
        payload = [REPOSITORY, ISSUE_NUMBER, MANAGEMENT_ID, "a" * 64]
        expected = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        actual = build_logical_task_key(
            repository=REPOSITORY, issue_number=ISSUE_NUMBER, management_id=MANAGEMENT_ID, task_bundle_sha256="a" * 64,
        )
        self.assertEqual(actual, expected)


class ValidateEnvelopeNormalTests(unittest.TestCase):
    def test_valid_envelope_is_accepted(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertTrue(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.ACCEPTED.value)
        self.assertEqual(result.error_codes, ())


class ValidateEnvelopeSchemaTests(unittest.TestCase):
    def _assert_rejected_schema(self, envelope, tb_bytes, task_bundle, expected_code=None):
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SCHEMA.value)
        if expected_code is not None:
            self.assertIn(expected_code, result.error_codes)
        return result

    def test_required_field_missing(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        del envelope["timeout_seconds"]
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_REQUIRED_FIELD_MISSING")

    def test_unknown_field_rejected(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        envelope["unexpected_field"] = "x"
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_UNKNOWN_FIELD")

    def test_schema_version_invalid(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(schema_version="v1")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_PATTERN_MISMATCH")

    def test_task_bundle_schema_version_const_violation(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(task_bundle_schema_version="OTHER-V2")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_CONST_MISMATCH")

    def test_task_bundle_hash_format_invalid(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(task_bundle_sha256="not-hex")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_PATTERN_MISMATCH")

    def test_repository_format_invalid(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(repository="not-a-repo")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_PATTERN_MISMATCH")

    def test_base_sha_format_invalid(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(base_sha="abc123")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_PATTERN_MISMATCH")

    def test_attempt_zero_rejected(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(attempt=0)
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_MINIMUM_VIOLATION")

    def test_execution_id_format_invalid(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(execution_id="not-a-valid-id")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_PATTERN_MISMATCH")

    def test_execution_id_key_prefix_mismatch(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        envelope["execution_id"] = "exec_" + ("0" * 12) + "_a1_testsuite01"
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_EXECUTION_ID_LOGICAL_KEY_MISMATCH")

    def test_execution_id_attempt_mismatch(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        prefix = envelope["logical_task_key"][:12]
        envelope["execution_id"] = f"exec_{prefix}_a2_testsuite01"
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_EXECUTION_ID_ATTEMPT_MISMATCH")

    def test_prohibited_operations_unknown_value(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(prohibited_operations=["NOT_A_REAL_OP"])
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_ENUM_MISMATCH")

    def test_prohibited_operations_duplicate(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(
            prohibited_operations=["AMEND", "AMEND"],
        )
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_UNIQUE_ITEMS_VIOLATION")

    def test_prohibited_operations_wrong_order(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(
            prohibited_operations=["MERGE", "AMEND"],
        )
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_OPERATIONS_ORDER_VIOLATION")

    def test_prohibited_paths_duplicate(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github/**", ".github/**"],
        )
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_UNIQUE_ITEMS_VIOLATION")

    def test_timeout_seconds_out_of_range(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(timeout_seconds=999999)
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_MAXIMUM_VIOLATION")

    def test_stop_point_const_violation(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(stop_point="AFTER_COMMIT_BEFORE_PUSH")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_CONST_MISMATCH")

    def test_expected_output_const_violation(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(expected_output="SOMETHING_ELSE")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_CONST_MISMATCH")

    def test_human_approval_required_const_violation(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(human_approval_required=False)
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_CONST_MISMATCH")

    def test_task_bundle_file_const_violation(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(task_bundle_file="bundle.json")
        self._assert_rejected_schema(envelope, tb_bytes, task_bundle, "SCHEMA_CONST_MISMATCH")

    def test_envelope_not_object_rejected(self):
        result = validate_envelope([], task_bundle_raw_bytes=b"{}", task_bundle={})
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SCHEMA.value)


class ValidateEnvelopeSourceAndHashTests(unittest.TestCase):
    def test_repository_mismatch_rejected_source(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(repository="someone/else")
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_REPOSITORY_MISMATCH", result.error_codes)

    def test_issue_number_mismatch_rejected_source(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(issue_number=1)
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_ISSUE_NUMBER_MISMATCH", result.error_codes)

    def test_management_id_mismatch_rejected_source(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(management_id="OTHER-ID")
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_MANAGEMENT_ID_MISMATCH", result.error_codes)

    def test_logical_task_key_mismatch_rejected_source(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        envelope["logical_task_key"] = "f" * 64
        # execution_idの先頭12文字は元のlogical_task_keyに基づいているため、
        # ここではenvelope自身の内部整合性(SCHEMA)は保ったまま、実bundleとの
        # 突き合わせ(SOURCE)だけを壊すために、execution_idも新しいkeyへ揃える。
        envelope["execution_id"] = f"exec_{'f' * 12}_a1_testsuite01"
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_LOGICAL_TASK_KEY_MISMATCH", result.error_codes)

    def test_task_bundle_real_byte_hash_mismatch_rejected_hash(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        tampered_bytes = tb_bytes + b" "  # 実ファイルのbyte列だけを変える
        result = validate_envelope(envelope, task_bundle_raw_bytes=tampered_bytes, task_bundle=task_bundle)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_HASH.value)
        self.assertIn("HASH_TASK_BUNDLE_BYTES_MISMATCH", result.error_codes)

    def test_schema_errors_take_priority_over_source_errors(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle(repository="someone/else")
        del envelope["timeout_seconds"]
        result = validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SCHEMA.value)


class ValidatePlanResultNormalTests(unittest.TestCase):
    def test_valid_plan_result_is_accepted(self):
        envelope, _tb_bytes, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertTrue(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.ACCEPTED.value)


class ValidatePlanResultSchemaTests(unittest.TestCase):
    def _assert_rejected_schema(self, plan_result, envelope, expected_code=None):
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SCHEMA.value)
        if expected_code is not None:
            self.assertIn(expected_code, result.error_codes)
        return result

    def test_unknown_field(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, extra_field="x")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_UNKNOWN_FIELD")

    def test_required_field_missing(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope)
        del plan_result["summary"]
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_REQUIRED_FIELD_MISSING")

    def test_implementation_plan_empty_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, implementation_plan=[])
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_MIN_ITEMS_VIOLATION")

    def test_proposed_test_plan_empty_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, proposed_test_plan=[])
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_MIN_ITEMS_VIOLATION")

    def test_changed_files_duplicate_path_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": "a.py", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
            {"path": "a.py", "change_type": "modified", "purpose": "y", "service_spec_impact": "NONE"},
        ])
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CHANGED_FILES_DUPLICATE_PATH")

    def test_prohibited_change_detected_true_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, prohibited_change_detected=True)
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CONST_MISMATCH")

    def test_generated_at_non_utc_offset_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, generated_at="2026-08-01T12:00:00+09:00")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_PATTERN_MISMATCH")

    def test_generated_at_missing_z_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, generated_at="2026-08-01T12:00:00")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_PATTERN_MISMATCH")

    def test_generated_at_with_fractional_seconds_accepted(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, generated_at="2026-08-01T12:00:00.123Z")
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertTrue(result.valid)

    def test_self_reported_false_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, self_reported=False)
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CONST_MISMATCH")

    def test_connection_decision_invalid_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, connection_decision="REJECTED_SCHEMA")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CONST_MISMATCH")

    def test_execution_status_invalid_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, execution_status="IMPLEMENTING")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CONST_MISMATCH")

    def test_next_action_invalid_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, next_action="NONE")
        self._assert_rejected_schema(plan_result, envelope, "SCHEMA_CONST_MISMATCH")

    def test_plan_result_not_object_rejected(self):
        result = validate_plan_result([], envelope={})
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SCHEMA.value)


class ValidatePlanResultSourceAndHashTests(unittest.TestCase):
    def test_execution_id_mismatch_rejected_source(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        prefix = envelope["logical_task_key"][:12]
        mismatched_execution_id = f"exec_{prefix}_a1_differentsuffix"
        self.assertNotEqual(mismatched_execution_id, envelope["execution_id"])
        plan_result = build_plan_result_for(envelope, execution_id=mismatched_execution_id)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_EXECUTION_ID_MISMATCH", result.error_codes)

    def test_attempt_mismatch_rejected_source(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, attempt=2)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_ATTEMPT_MISMATCH", result.error_codes)

    def test_logical_task_key_mismatch_rejected_source(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, logical_task_key="e" * 64)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_LOGICAL_TASK_KEY_MISMATCH", result.error_codes)

    def test_management_id_mismatch_rejected_source(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, management_id="OTHER-ID")
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)
        self.assertIn("SOURCE_MANAGEMENT_ID_MISMATCH", result.error_codes)

    def test_task_bundle_hash_echo_mismatch_rejected_hash(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, input_task_bundle_sha256="a" * 64)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_HASH.value)
        self.assertIn("HASH_TASK_BUNDLE_ECHO_MISMATCH", result.error_codes)

    def test_base_sha_echo_mismatch_rejected_hash(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope, input_base_sha="b" * 40)
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_HASH.value)
        self.assertIn("HASH_BASE_SHA_ECHO_MISMATCH", result.error_codes)

    def test_source_errors_take_priority_over_hash_errors(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(
            envelope, attempt=2, input_base_sha="b" * 40,
        )
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)


class ProhibitedPathPolicyTests(unittest.TestCase):
    def test_prohibited_path_match_rejected_policy(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github/**"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": ".github/workflows/ci-test.yml", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_POLICY.value)
        self.assertIn("POLICY_PROHIBITED_PATH_MATCH", result.error_codes)

    def test_windows_path_separator_normalized_still_matches(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github/**"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": ".github\\workflows\\ci-test.yml", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_POLICY.value)
        self.assertIn("POLICY_PROHIBITED_PATH_MATCH", result.error_codes)

    def test_windows_pattern_separator_normalized_still_matches(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github\\**"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": ".github/workflows/ci-test.yml", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_POLICY.value)

    def test_path_traversal_rejected_even_without_pattern_match(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=["**/*secret*"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": "../outside_repo/file.py", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertFalse(result.valid)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_POLICY.value)
        self.assertIn("POLICY_PATH_TRAVERSAL", result.error_codes)

    def test_path_traversal_with_backslash_rejected(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=["**/*secret*"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": "..\\outside_repo\\file.py", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_POLICY.value)
        self.assertIn("POLICY_PATH_TRAVERSAL", result.error_codes)

    def test_non_matching_path_is_accepted(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github/**", "**/*secret*"],
        )
        plan_result = build_plan_result_for(envelope, proposed_changed_files=[
            {"path": "scripts/demo.py", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
        ])
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertTrue(result.valid)

    def test_policy_checked_last_after_schema_source_hash(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle(
            prohibited_paths=[".github/**"],
        )
        plan_result = build_plan_result_for(
            envelope,
            attempt=2,  # SOURCE mismatch
            proposed_changed_files=[
                {"path": ".github/workflows/ci-test.yml", "change_type": "modified", "purpose": "x", "service_spec_impact": "NONE"},
            ],
        )
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(result.connection_decision, ConnectionDecision.REJECTED_SOURCE.value)


class ExampleFixtureTests(unittest.TestCase):
    """docs/automation/examples/配下の実ファイルが、実際にこのバリデータで
    ACCEPTEDとなることを確認する(fixtureとコードの乖離を防ぐ回帰テスト)。
    """

    def _load(self, path: Path) -> dict:
        with path.open(encoding="utf-8") as f:
            return json.load(f)

    def test_envelope_example_is_valid_shape(self):
        envelope = self._load(EXAMPLES_DIR / "implementer_execution_envelope.example.json")
        task_bundle = build_task_bundle_fixture(
            repository=envelope["repository"],
            issue_number=envelope["issue_number"],
            management_id=envelope["management_id"],
        )
        # exampleのtask_bundle_sha256/logical_task_keyは、生成時に使った実際の
        # task bundle byte列に基づく値であり、ここで再構築したfixtureの
        # byte列とは異なる可能性があるため、hash自体の一致は問わず、
        # schema面(必須field・型・enum/const・pattern)だけを厳密に検証する。
        from scripts.implementer_connection_contract import _validate_envelope_schema
        errors = _validate_envelope_schema(envelope)
        self.assertEqual(errors, [], errors)

    def test_plan_result_example_matches_envelope_example(self):
        envelope = self._load(EXAMPLES_DIR / "implementer_execution_envelope.example.json")
        plan_result = self._load(EXAMPLES_DIR / "implementer_plan_result.example.json")
        result = validate_plan_result(plan_result, envelope=envelope)
        self.assertTrue(result.valid, result.to_dict())
        self.assertEqual(result.connection_decision, ConnectionDecision.ACCEPTED.value)

    def test_envelope_example_matches_reconstructed_task_bundle_hash(self):
        # exampleのtask bundleはdocs/automation/AUTO-001-06-02-02_implementer_
        # connection_contract.md に記載の生成手順(demo task bundle)に基づく。
        # ここではenvelope/plan resultのlogical_task_key・execution_idの
        # 内部整合性(envelope自身のcross-field)だけを再確認する。
        envelope = self._load(EXAMPLES_DIR / "implementer_execution_envelope.example.json")
        recomputed = build_logical_task_key(
            repository=envelope["repository"],
            issue_number=envelope["issue_number"],
            management_id=envelope["management_id"],
            task_bundle_sha256=envelope["task_bundle_sha256"],
        )
        self.assertEqual(recomputed, envelope["logical_task_key"])
        self.assertEqual(envelope["execution_id"][5:17], envelope["logical_task_key"][:12])


class SchemaJsonFilesShapeTests(unittest.TestCase):
    """docs/automation/schemas/配下の新規schemaファイル自体の構造を検査する
    (JSON parse可能・requiredとPythonバリデータのrequiredフィールド一覧が
    一致すること)。
    """

    def test_envelope_schema_file_required_matches_python_validator(self):
        with (SCHEMAS_DIR / "implementer_execution_envelope.schema.json").open(encoding="utf-8") as f:
            schema = json.load(f)
        from scripts.implementer_connection_contract import _ENVELOPE_REQUIRED_FIELDS
        self.assertEqual(set(schema["required"]), set(_ENVELOPE_REQUIRED_FIELDS))
        self.assertEqual(schema["additionalProperties"], False)

    def test_plan_result_schema_file_required_matches_python_validator(self):
        with (SCHEMAS_DIR / "implementer_plan_result.schema.json").open(encoding="utf-8") as f:
            schema = json.load(f)
        from scripts.implementer_connection_contract import _PLAN_RESULT_REQUIRED_FIELDS
        self.assertEqual(set(schema["required"]), set(_PLAN_RESULT_REQUIRED_FIELDS))
        self.assertEqual(schema["additionalProperties"], False)


class ExistingSchemaUnchangedTests(unittest.TestCase):
    """claude_implementation_report.schema.json / openai_review_result.
    schema.jsonの必須fieldセット・重要な固定値が、本タスクの変更で壊れて
    いないことを確認する(既存fileへの編集は行っていないため、内容そのもの
    ではなく契約の形が保たれていることを確認する回帰テスト)。
    """

    def test_claude_implementation_report_schema_unchanged_shape(self):
        with (SCHEMAS_DIR / "claude_implementation_report.schema.json").open(encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema["additionalProperties"], False)
        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version", "self_reported", "management_id", "issue_number",
                "branch", "head_commit", "implementation_status", "summary",
                "changed_files", "acceptance_criteria", "tests_executed",
                "tests_not_executed", "assumed_working_not_verified",
                "human_confirmation_items", "risks", "incomplete_items",
                "external_api_calls", "git_state",
            },
        )
        self.assertEqual(schema["properties"]["self_reported"]["const"], True)

    def test_openai_review_result_schema_unchanged_shape(self):
        with (SCHEMAS_DIR / "openai_review_result.schema.json").open(encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(
            set(schema["required"]),
            {
                "schema_version", "management_id", "issue_number", "pr_number",
                "head_commit", "overall_verdict", "summary", "review_id",
                "reviewed_at", "acceptance_criteria", "test_evidence",
                "human_judgement_required", "flags_for_human",
            },
        )
        self.assertEqual(
            set(schema["properties"]["overall_verdict"]["enum"]),
            {"PASS", "CHANGES_REQUIRED", "HUMAN_REVIEW"},
        )


class LauncherNoDriftTests(unittest.TestCase):
    """本モジュールはscripts.implementer_launcherをimportしない設計だが、
    固定値(TASK_BUNDLE_SCHEMA_VERSION)が実際のLauncher側の値と一致し続ける
    ことをテストでだけ確認する(本番コード同士は疎結合のまま)。
    """

    def test_task_bundle_schema_version_const_matches_launcher(self):
        self.assertEqual(TASK_BUNDLE_SCHEMA_VERSION_CONST, TASK_BUNDLE_SCHEMA_VERSION)


class ValidationResultShapeTests(unittest.TestCase):
    def test_to_dict_shape(self):
        result = ValidationResult(
            valid=False, connection_decision="REJECTED_SCHEMA",
            error_codes=("X",), error_messages=("y",),
        )
        self.assertEqual(
            result.to_dict(),
            {"valid": False, "connection_decision": "REJECTED_SCHEMA", "error_codes": ["X"], "error_messages": ["y"]},
        )

    def test_connection_decision_enum_has_no_duplicate_reserved(self):
        values = {member.value for member in ConnectionDecision}
        self.assertEqual(
            values,
            {"ACCEPTED", "REJECTED_SCHEMA", "REJECTED_HASH", "REJECTED_SOURCE", "REJECTED_POLICY"},
        )
        self.assertNotIn("REJECTED_DUPLICATE", values)


class InputImmutabilityTests(unittest.TestCase):
    def test_validate_envelope_does_not_mutate_input(self):
        envelope, tb_bytes, task_bundle = build_envelope_and_bundle()
        envelope_copy = copy.deepcopy(envelope)
        task_bundle_copy = copy.deepcopy(task_bundle)
        validate_envelope(envelope, task_bundle_raw_bytes=tb_bytes, task_bundle=task_bundle)
        self.assertEqual(envelope, envelope_copy)
        self.assertEqual(task_bundle, task_bundle_copy)

    def test_validate_plan_result_does_not_mutate_input(self):
        envelope, _tb, _task_bundle = build_envelope_and_bundle()
        plan_result = build_plan_result_for(envelope)
        envelope_copy = copy.deepcopy(envelope)
        plan_result_copy = copy.deepcopy(plan_result)
        validate_plan_result(plan_result, envelope=envelope)
        self.assertEqual(envelope, envelope_copy)
        self.assertEqual(plan_result, plan_result_copy)


if __name__ == "__main__":
    unittest.main()
