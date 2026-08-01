"""scripts/issue_preflight_validator.py (AUTO-001-05-01) の単体テスト。

外部API・外部ネットワークは一切使わない。文字列fixtureだけで、正常系・
マーカー異常・見出し異常・項目内容異常・管理ID異常・受入条件異常・
複合異常・安全性/再現性を検証する。
"""

from __future__ import annotations

import socket
import unittest
from pathlib import Path

from scripts.issue_preflight_validator import (
    CANONICAL_HEADINGS,
    END_MARKER,
    NONE_ALLOWED_HEADINGS,
    REQUIRED_SUBSTANTIVE_HEADINGS,
    START_MARKER,
    ValidationStatus,
    extract_task_fields,
    validate_issue_body,
)

REPO_ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "agent_task.md"

STRUCTURAL_ERROR_CODES = {
    "MARKER_START_MISSING", "MARKER_END_MISSING",
    "MARKER_START_DUPLICATE", "MARKER_END_DUPLICATE", "MARKER_ORDER_INVALID",
    "MISSING_HEADING", "DUPLICATE_HEADING", "HEADING_ORDER_INVALID",
}

DEFAULT_CONTENT = {
    "管理ID": "AUTO-001-05-01",
    "現在の問題": "既存のvalidatorが存在せず、契約違反を機械的に検知できない。",
    "原因に関する仮説": "なし",
    "目的": "preflight validatorを実装する。",
    "期待動作・決定事項": "Issue本文を判定できるようにする。",
    "非対象範囲": "Claude Code接続は対象外。",
    "受入条件": "- [ ] AC-01: 正常な本文でvalidationが成功する\n- [ ] AC-02: 異常な本文でvalidationが失敗する",
    "テスト観点": "正常系と異常系の両方を自動テストで確認する。",
    "リスク": "なし",
    "人間確認事項": "なし",
    "変更区分": "- サービス仕様変更：なし\n- リポジトリ運用仕様変更：あり\n- 実装方法だけの変更：いいえ",
    "参考資料": "なし",
}


def build_body(
    content: dict[str, str] | None = None,
    order: list[str] | None = None,
    drop: set[str] | None = None,
    start_marker: str | None = START_MARKER,
    end_marker: str | None = END_MARKER,
    extra_start_markers: int = 0,
    extra_end_markers: int = 0,
    prefix: str = "",
    suffix: str = "",
) -> str:
    merged = {**DEFAULT_CONTENT, **(content or {})}
    heading_order = list(order) if order is not None else list(CANONICAL_HEADINGS)
    if drop:
        heading_order = [h for h in heading_order if h not in drop]

    parts: list[str] = [prefix] if prefix else []
    if start_marker is not None:
        parts.append(start_marker)
    for _ in range(extra_start_markers):
        parts.append(START_MARKER)
    parts.append("")
    for h in heading_order:
        parts.append(f"## {h}")
        parts.append("")
        parts.append(merged.get(h, DEFAULT_CONTENT.get(h, "")))
        parts.append("")
    if end_marker is not None:
        parts.append(end_marker)
    for _ in range(extra_end_markers):
        parts.append(END_MARKER)
    if suffix:
        parts.append(suffix)
    return "\n".join(parts)


def error_codes(result) -> list[str]:
    return [e.code for e in result.errors]


class ContractConstantsTests(unittest.TestCase):

    def test_12_canonical_headings(self):
        self.assertEqual(len(CANONICAL_HEADINGS), 12)
        self.assertEqual(len(set(CANONICAL_HEADINGS)), 12)

    def test_required_and_none_allowed_partition_all_headings(self):
        self.assertEqual(REQUIRED_SUBSTANTIVE_HEADINGS | NONE_ALLOWED_HEADINGS, set(CANONICAL_HEADINGS))
        self.assertTrue(REQUIRED_SUBSTANTIVE_HEADINGS.isdisjoint(NONE_ALLOWED_HEADINGS))
        self.assertEqual(len(REQUIRED_SUBSTANTIVE_HEADINGS), 8)
        self.assertEqual(len(NONE_ALLOWED_HEADINGS), 4)


class RealTemplateStructuralSyncTests(unittest.TestCase):
    """テンプレート実体とvalidatorの定数が一致し続けることを保証する
    (risk2: テンプレートとvalidatorの二重管理を防ぐ回帰テスト)。
    テンプレート本体は空欄のままなのでMISSING_REQUIRED_CONTENT等の内容系
    エラーは出るが、マーカー・見出し構造に関するエラーは出てはならない。
    """

    def test_real_template_has_no_structural_errors(self):
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        result = validate_issue_body(text)
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        codes = set(error_codes(result))
        unexpected = codes & STRUCTURAL_ERROR_CODES
        self.assertEqual(unexpected, set(), msg=f"テンプレートの構造がvalidatorの契約とずれています: {unexpected}")

    def test_real_template_flags_empty_required_sections(self):
        # AUTO-001-05-01-R1: 「変更区分」の固定ラベルだけの未記入状態も
        # 実際に不合格として検知されることを、実テンプレートに対して
        # 直接検証する(AC-R1-06)。「受入条件」は説明欠落の別コードで
        # 報告されるため対象外とする。
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        result = validate_issue_body(text)
        flagged_sections = {e.section for e in result.errors if e.code == "MISSING_REQUIRED_CONTENT"}
        expected = REQUIRED_SUBSTANTIVE_HEADINGS - {"受入条件"}
        self.assertTrue(expected.issubset(flagged_sections), msg=flagged_sections)


# ---------------------------------------------------------------------------
# 10.1 正常系
# ---------------------------------------------------------------------------

class NormalCaseTests(unittest.TestCase):

    def test_all_12_headings_correct_order_passes(self):
        result = validate_issue_body(build_body())
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)
        self.assertEqual(result.errors, [])

    def test_optional_sections_all_none_passes(self):
        content = {h: "なし" for h in NONE_ALLOWED_HEADINGS}
        result = validate_issue_body(build_body(content=content))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_simple_valid_management_id(self):
        result = validate_issue_body(build_body(content={"管理ID": "ER-003"}))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_management_id_with_suffix(self):
        for mid in ("AUTO-001-05-01", "AUTO-001-04D-R2", "ER-003-B1-P4C"):
            with self.subTest(mid=mid):
                result = validate_issue_body(build_body(content={"管理ID": mid}))
                self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_single_acceptance_criterion(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-01: 単一条件の説明"}))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_multiple_acceptance_criteria(self):
        ac = "\n".join(f"- [ ] AC-{i:02d}: 条件{i}の説明" for i in range(1, 6))
        result = validate_issue_body(build_body(content={"受入条件": ac}))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_lf_only_body_passes(self):
        text = build_body()
        self.assertNotIn("\r", text)
        result = validate_issue_body(text)
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_crlf_body_passes(self):
        text = build_body().replace("\n", "\r\n")
        result = validate_issue_body(text)
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_mixed_crlf_lf_passes(self):
        text = build_body()
        lines = text.split("\n")
        mixed = "\n".join(lines[:5]) + "\r\n" + "\n".join(lines[5:])
        result = validate_issue_body(mixed)
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_utf8_japanese_content_passes(self):
        result = validate_issue_body(build_body(content={
            "現在の問題": "日本語の本文でも正しく判定できることを確認する。全角記号、句読点、絵文字以外の日本語文字を含む。",
        }))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)


# ---------------------------------------------------------------------------
# 10.2 マーカー異常
# ---------------------------------------------------------------------------

class MarkerErrorTests(unittest.TestCase):

    def test_missing_start_marker(self):
        result = validate_issue_body(build_body(start_marker=None))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("MARKER_START_MISSING", error_codes(result))

    def test_missing_end_marker(self):
        result = validate_issue_body(build_body(end_marker=None))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("MARKER_END_MISSING", error_codes(result))

    def test_duplicate_start_marker(self):
        result = validate_issue_body(build_body(extra_start_markers=1))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("MARKER_START_DUPLICATE", error_codes(result))

    def test_duplicate_end_marker(self):
        result = validate_issue_body(build_body(extra_end_markers=1))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("MARKER_END_DUPLICATE", error_codes(result))

    def test_start_end_reversed(self):
        text = f"{END_MARKER}\n\n## 管理ID\n\nAUTO-001-05-01\n\n{START_MARKER}\n"
        result = validate_issue_body(text)
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("MARKER_ORDER_INVALID", error_codes(result))

    def test_marker_text_inside_fenced_code_block_not_recognized(self):
        body = build_body()
        body = body.replace(
            "## 参考資料\n\nなし\n",
            "## 参考資料\n\n```text\n" + START_MARKER + "\n" + END_MARKER + "\n```\nなし\n",
        )
        result = validate_issue_body(body)
        # フェンス内のマーカーは無視され、外側の本物のマーカーだけが有効と判定される
        self.assertNotIn("MARKER_START_DUPLICATE", error_codes(result))
        self.assertNotIn("MARKER_END_DUPLICATE", error_codes(result))


# ---------------------------------------------------------------------------
# 10.3 見出し異常
# ---------------------------------------------------------------------------

class HeadingErrorTests(unittest.TestCase):

    def test_each_heading_missing_individually(self):
        for heading in CANONICAL_HEADINGS:
            with self.subTest(heading=heading):
                result = validate_issue_body(build_body(drop={heading}))
                self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
                missing = [e for e in result.errors if e.code == "MISSING_HEADING" and e.section == heading]
                self.assertEqual(len(missing), 1)

    def test_duplicate_heading(self):
        order = list(CANONICAL_HEADINGS) + ["目的"]
        result = validate_issue_body(build_body(order=order))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        dup = [e for e in result.errors if e.code == "DUPLICATE_HEADING" and e.section == "目的"]
        self.assertEqual(len(dup), 1)

    def test_adjacent_heading_order_swapped(self):
        order = list(CANONICAL_HEADINGS)
        i = order.index("目的")
        order[i], order[i + 1] = order[i + 1], order[i]
        result = validate_issue_body(build_body(order=order))
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIn("HEADING_ORDER_INVALID", error_codes(result))

    def test_similar_heading_name_not_recognized_as_canonical(self):
        body = build_body(drop={"目的"})
        body = body.replace("## 期待動作・決定事項", "## 目的について\n\n本来の目的ではない類似見出し。\n\n## 期待動作・決定事項")
        result = validate_issue_body(body)
        self.assertIn("MISSING_HEADING", error_codes(result))
        missing_purpose = [e for e in result.errors if e.code == "MISSING_HEADING" and e.section == "目的"]
        self.assertEqual(len(missing_purpose), 1)

    def test_heading_only_inside_html_comment_not_recognized(self):
        body = build_body(drop={"参考資料"})
        body = body.replace(
            f"\n{END_MARKER}",
            "\n<!--\n## 参考資料\n\nコメント内の偽見出し\n-->\n" + END_MARKER,
        )
        result = validate_issue_body(body)
        self.assertIn("MISSING_HEADING", error_codes(result))
        missing_ref = [e for e in result.errors if e.code == "MISSING_HEADING" and e.section == "参考資料"]
        self.assertEqual(len(missing_ref), 1)

    def test_heading_only_inside_fenced_code_block_not_recognized(self):
        body = build_body(drop={"参考資料"})
        body = body.replace(
            f"\n{END_MARKER}",
            "\n```markdown\n## 参考資料\n\nコードブロック内の偽見出し\n```\n" + END_MARKER,
        )
        result = validate_issue_body(body)
        self.assertIn("MISSING_HEADING", error_codes(result))
        missing_ref = [e for e in result.errors if e.code == "MISSING_HEADING" and e.section == "参考資料"]
        self.assertEqual(len(missing_ref), 1)


# ---------------------------------------------------------------------------
# 10.4 項目内容異常
# ---------------------------------------------------------------------------

class SectionContentErrorTests(unittest.TestCase):

    def test_required_section_completely_empty(self):
        result = validate_issue_body(build_body(content={"目的": ""}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_required_section_whitespace_only(self):
        result = validate_issue_body(build_body(content={"目的": "   　  "}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_required_section_newline_only(self):
        result = validate_issue_body(build_body(content={"目的": "\n\n\n"}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_required_section_html_comment_only(self):
        result = validate_issue_body(build_body(content={"目的": "<!-- TODO: 後で書く -->"}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_required_section_markdown_decoration_only(self):
        result = validate_issue_body(build_body(content={"目的": "- \n* \n# \n---"}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_required_section_bare_none_is_invalid(self):
        result = validate_issue_body(build_body(content={"目的": "なし"}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "目的"), [(e.code, e.section) for e in result.errors])

    def test_optional_section_empty_is_invalid(self):
        result = validate_issue_body(build_body(content={"リスク": ""}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "リスク"), [(e.code, e.section) for e in result.errors])

    def test_optional_section_none_is_valid(self):
        result = validate_issue_body(build_body(content={"リスク": "なし"}))
        self.assertNotIn("リスク", [e.section for e in result.errors])

    def test_optional_section_html_comment_only_is_invalid(self):
        result = validate_issue_body(build_body(content={"リスク": "<!-- 後で書く -->"}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "リスク"), [(e.code, e.section) for e in result.errors])


# ---------------------------------------------------------------------------
# 10.5 管理ID異常
# ---------------------------------------------------------------------------

class ManagementIdErrorTests(unittest.TestCase):

    def test_lowercase_invalid(self):
        result = validate_issue_body(build_body(content={"管理ID": "auto-001"}))
        self.assertIn("INVALID_MANAGEMENT_ID", error_codes(result))

    def test_too_few_digits_invalid(self):
        result = validate_issue_body(build_body(content={"管理ID": "AUTO-01"}))
        self.assertIn("INVALID_MANAGEMENT_ID", error_codes(result))

    def test_missing_separator_invalid(self):
        result = validate_issue_body(build_body(content={"管理ID": "AUTO001"}))
        self.assertIn("INVALID_MANAGEMENT_ID", error_codes(result))

    def test_invalid_symbol_invalid(self):
        result = validate_issue_body(build_body(content={"管理ID": "AUTO-001-05_01"}))
        self.assertIn("INVALID_MANAGEMENT_ID", error_codes(result))

    def test_id_surrounded_by_prose_still_recognized(self):
        result = validate_issue_body(build_body(content={"管理ID": "本タスクの管理IDは AUTO-001-05-01 です。"}))
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)

    def test_multiple_ids_ambiguous(self):
        result = validate_issue_body(build_body(content={"管理ID": "AUTO-001-05-01 または AUTO-001-05-02 のいずれか"}))
        self.assertIn("AMBIGUOUS_MANAGEMENT_ID", error_codes(result))


# ---------------------------------------------------------------------------
# 10.6 受入条件異常
# ---------------------------------------------------------------------------

class AcceptanceCriteriaErrorTests(unittest.TestCase):

    def test_zero_acceptance_criteria(self):
        result = validate_issue_body(build_body(content={"受入条件": "特に条件はまだ整理していない。"}))
        self.assertIn("ACCEPTANCE_CRITERIA_MISSING", error_codes(result))

    def test_starts_from_ac02(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-02: 2番目から始まる"}))
        self.assertIn("ACCEPTANCE_CRITERION_SEQUENCE_INVALID", error_codes(result))

    def test_single_digit_id(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-1: 1桁のID"}))
        self.assertIn("ACCEPTANCE_CRITERION_FORMAT", error_codes(result))

    def test_triple_digit_id(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-001: 3桁のID"}))
        self.assertIn("ACCEPTANCE_CRITERION_FORMAT", error_codes(result))

    def test_duplicate_id(self):
        ac = "- [ ] AC-01: 1件目\n- [ ] AC-01: 重複した1件目"
        result = validate_issue_body(build_body(content={"受入条件": ac}))
        self.assertIn("ACCEPTANCE_CRITERION_DUPLICATE_ID", error_codes(result))

    def test_missing_number_in_sequence(self):
        ac = "- [ ] AC-01: 1件目\n- [ ] AC-03: 欠番の次"
        result = validate_issue_body(build_body(content={"受入条件": ac}))
        self.assertIn("ACCEPTANCE_CRITERION_SEQUENCE_INVALID", error_codes(result))

    def test_reversed_order(self):
        ac = "- [ ] AC-02: 先に書かれた2件目\n- [ ] AC-01: 後に書かれた1件目"
        result = validate_issue_body(build_body(content={"受入条件": ac}))
        self.assertIn("ACCEPTANCE_CRITERION_SEQUENCE_INVALID", error_codes(result))

    def test_missing_checkbox(self):
        result = validate_issue_body(build_body(content={"受入条件": "AC-01: チェックボックスが無い"}))
        self.assertIn("ACCEPTANCE_CRITERION_FORMAT", error_codes(result))

    def test_missing_colon(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-01 コロンが無い"}))
        self.assertIn("ACCEPTANCE_CRITERION_FORMAT", error_codes(result))

    def test_missing_description(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-01:"}))
        self.assertIn("ACCEPTANCE_CRITERION_DESCRIPTION_MISSING", error_codes(result))

    def test_description_html_comment_only(self):
        result = validate_issue_body(build_body(content={"受入条件": "- [ ] AC-01: <!-- 後で書く -->"}))
        self.assertIn("ACCEPTANCE_CRITERION_DESCRIPTION_MISSING", error_codes(result))


# ---------------------------------------------------------------------------
# AUTO-001-05-01-R1: 「変更区分」の固定ラベルと実質的な値の区別
# ---------------------------------------------------------------------------

class ChangeScopeTests(unittest.TestCase):

    def test_labels_only_is_invalid(self):
        content = "- サービス仕様変更：\n- リポジトリ運用仕様変更：\n- 実装方法だけの変更："
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_labels_and_html_comment_only_is_invalid(self):
        content = (
            "- サービス仕様変更：<!-- 記入してください -->\n"
            "- リポジトリ運用仕様変更：<!-- 記入してください -->\n"
            "- 実装方法だけの変更：<!-- 記入してください -->"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_labels_and_whitespace_only_is_invalid(self):
        content = "- サービス仕様変更：   \n- リポジトリ運用仕様変更：\n- 実装方法だけの変更："
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_all_none_is_invalid(self):
        content = "- サービス仕様変更：なし\n- リポジトリ運用仕様変更：なし\n- 実装方法だけの変更：なし"
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_single_category_with_content_is_valid(self):
        content = "- サービス仕様変更：なし\n- リポジトリ運用仕様変更：なし\n- 実装方法だけの変更：validatorを新規実装する"
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertNotIn("変更区分", [e.section for e in result.errors])

    def test_one_applicable_rest_none_is_valid(self):
        content = (
            "- サービス仕様変更：なし\n"
            "- リポジトリ運用仕様変更：該当。Issue本文の機械判定契約を追加する\n"
            "- 実装方法だけの変更：なし"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertNotIn("変更区分", [e.section for e in result.errors])

    def test_multiple_categories_with_content_is_valid(self):
        content = (
            "- サービス仕様変更：なし\n"
            "- リポジトリ運用仕様変更：該当。Issue本文の機械判定契約を追加する\n"
            "- 実装方法だけの変更：validatorを新規実装する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertNotIn("変更区分", [e.section for e in result.errors])

    def test_labels_only_crlf_is_invalid(self):
        content = "- サービス仕様変更：\n- リポジトリ運用仕様変更：\n- 実装方法だけの変更："
        text = build_body(content={"変更区分": content}).replace("\n", "\r\n")
        result = validate_issue_body(text)
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_default_valid_body_change_scope_still_passes(self):
        # 既存のDEFAULT_CONTENT(サービス仕様変更：なし/リポジトリ運用仕様変更：あり/
        # 実装方法だけの変更：いいえ)は、この修正後も引き続き合格すること。
        result = validate_issue_body(build_body())
        self.assertEqual(result.status, ValidationStatus.PASS, msg=result.errors)


class ChangeScopeFreeformFallbackTests(unittest.TestCase):
    """AUTO-001-05-01-R2: 固定3区分に属さない自由記述を合格材料にしないことの検証。"""

    def test_empty_labels_with_unrelated_freeform_text_is_invalid(self):
        content = (
            "- サービス仕様変更：\n"
            "- リポジトリ運用仕様変更：\n"
            "- 実装方法だけの変更：\n"
            "\n"
            "あとで検討する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_all_none_with_unrelated_freeform_text_is_invalid(self):
        content = (
            "- サービス仕様変更：なし\n"
            "- リポジトリ運用仕様変更：なし\n"
            "- 実装方法だけの変更：なし\n"
            "\n"
            "補足があります"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_unknown_custom_label_with_value_is_invalid(self):
        content = (
            "- サービス仕様変更：\n"
            "- リポジトリ運用仕様変更：\n"
            "- 実装方法だけの変更：\n"
            "- その他の変更：何かを変更する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_same_line_value_on_formal_label_is_valid(self):
        content = (
            "- サービス仕様変更：なし\n"
            "- リポジトリ運用仕様変更：Issue本文の検証契約を追加する\n"
            "- 実装方法だけの変更：validatorを追加する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertNotIn("変更区分", [e.section for e in result.errors])

    def test_indented_continuation_lines_attached_to_formal_label_is_valid(self):
        content = (
            "- サービス仕様変更：なし\n"
            "- リポジトリ運用仕様変更：\n"
            "  Issue本文の検証契約を追加する。\n"
            "  不正なIssueではClaudeを起動しない。\n"
            "- 実装方法だけの変更：validatorを追加する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertNotIn("変更区分", [e.section for e in result.errors])

    def test_non_indented_line_immediately_after_labels_not_counted(self):
        # 空行を挟まなくても、非インデント行はどの区分の継続行にもならない
        content = (
            "- サービス仕様変更：\n"
            "- リポジトリ運用仕様変更：\n"
            "- 実装方法だけの変更：\n"
            "あとで検討する"
        )
        result = validate_issue_body(build_body(content={"変更区分": content}))
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])

    def test_empty_labels_with_unrelated_freeform_text_crlf_is_invalid(self):
        content = (
            "- サービス仕様変更：\n"
            "- リポジトリ運用仕様変更：\n"
            "- 実装方法だけの変更：\n"
            "\n"
            "あとで検討する"
        )
        text = build_body(content={"変更区分": content}).replace("\n", "\r\n")
        result = validate_issue_body(text)
        self.assertIn(("MISSING_REQUIRED_CONTENT", "変更区分"), [(e.code, e.section) for e in result.errors])


class ChangeScopeRealTemplateSyncTests(unittest.TestCase):
    """実テンプレートの固定ラベル表記とvalidatorの定数が一致し続けることを保証する。"""

    def test_real_template_change_scope_labels_match_constants(self):
        from scripts.issue_preflight_validator import CHANGE_SCOPE_LABELS

        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        for label in CHANGE_SCOPE_LABELS:
            self.assertIn(f"- {label}：", text, msg=f"テンプレートに固定ラベル「{label}：」が見つかりません")


# ---------------------------------------------------------------------------
# 10.7 複合異常
# ---------------------------------------------------------------------------

class CompoundErrorTests(unittest.TestCase):

    def test_multiple_independent_violations_all_listed(self):
        body = build_body(
            drop={"参考資料"},
            content={
                "目的": "",
                "管理ID": "auto-001",
                "受入条件": "- [ ] AC-01: 1件目\n- [ ] AC-01: 重複",
            },
        )
        result = validate_issue_body(body)
        self.assertEqual(result.status, ValidationStatus.CONTRACT_VIOLATION)
        codes = set(error_codes(result))
        self.assertIn("MISSING_HEADING", codes)
        self.assertIn("MISSING_REQUIRED_CONTENT", codes)
        self.assertIn("INVALID_MANAGEMENT_ID", codes)
        self.assertIn("ACCEPTANCE_CRITERION_DUPLICATE_ID", codes)
        self.assertGreaterEqual(len(result.errors), 4)


# ---------------------------------------------------------------------------
# 10.8 安全性・再現性
# ---------------------------------------------------------------------------

class SafetyAndReproducibilityTests(unittest.TestCase):

    def test_does_not_mutate_input_string(self):
        text = build_body()
        original = str(text)
        validate_issue_body(text)
        self.assertEqual(text, original)

    def test_does_not_touch_filesystem_tracked_files(self):
        before = TEMPLATE_PATH.read_bytes()
        validate_issue_body(build_body())
        validate_issue_body(TEMPLATE_PATH.read_text(encoding="utf-8"))
        after = TEMPLATE_PATH.read_bytes()
        self.assertEqual(before, after)

    def test_does_not_attempt_network_connection(self):
        attempted = {"flag": False}
        original_connect = socket.socket.connect

        def _blocked_connect(self, *args, **kwargs):
            attempted["flag"] = True
            raise AssertionError("validator attempted a network connection")

        socket.socket.connect = _blocked_connect
        try:
            validate_issue_body(build_body())
            validate_issue_body(build_body(content={"目的": ""}))
        finally:
            socket.socket.connect = original_connect
        self.assertFalse(attempted["flag"])

    def test_result_independent_of_local_artifacts_presence(self):
        # validatorは文字列だけを見て判定し、Git管理外の成果物の有無に依存しない
        result_a = validate_issue_body(build_body())
        result_b = validate_issue_body(build_body())
        self.assertEqual(result_a.to_machine_dict(), result_b.to_machine_dict())

    def test_result_independent_of_call_order(self):
        bodies = [build_body(), build_body(content={"目的": ""}), build_body(drop={"参考資料"})]
        first_pass = [validate_issue_body(b).to_machine_dict() for b in bodies]
        second_pass = [validate_issue_body(b).to_machine_dict() for b in reversed(bodies)]
        self.assertEqual(first_pass, list(reversed(second_pass)))

    def test_very_long_body_does_not_crash(self):
        long_content = "非常に長い本文のテスト。" * 5000
        result = validate_issue_body(build_body(content={"参考資料": long_content}))
        self.assertIn(result.status, (ValidationStatus.PASS, ValidationStatus.CONTRACT_VIOLATION))

    def test_non_string_input_yields_internal_error_not_exception(self):
        result = validate_issue_body(None)  # type: ignore[arg-type]
        self.assertEqual(result.status, ValidationStatus.INTERNAL_ERROR)
        self.assertTrue(result.errors)


# ---------------------------------------------------------------------------
# 機械向け/人間向け出力・状態区分
# ---------------------------------------------------------------------------

class OutputContractTests(unittest.TestCase):

    def test_machine_dict_shape_on_pass(self):
        result = validate_issue_body(build_body())
        d = result.to_machine_dict()
        self.assertEqual(d["valid"], True)
        self.assertEqual(d["status"], "PASS")
        self.assertEqual(d["errors"], [])

    def test_machine_dict_shape_on_violation(self):
        result = validate_issue_body(build_body(content={"目的": ""}))
        d = result.to_machine_dict()
        self.assertEqual(d["valid"], False)
        self.assertEqual(d["status"], "CONTRACT_VIOLATION")
        self.assertGreater(len(d["errors"]), 0)
        for err in d["errors"]:
            self.assertIn("code", err)
            self.assertIn("section", err)
            self.assertIn("message", err)

    def test_human_text_is_not_a_python_traceback(self):
        result = validate_issue_body(None)  # type: ignore[arg-type]
        human = result.to_human_text()
        self.assertNotIn("Traceback (most recent call last)", human)

    def test_human_text_lists_all_violations(self):
        body = build_body(content={"目的": "", "管理ID": "auto-001"})
        result = validate_issue_body(body)
        human = result.to_human_text()
        self.assertIn("目的", human)
        self.assertIn("管理ID", human)

    def test_three_status_values_are_distinct(self):
        pass_result = validate_issue_body(build_body())
        violation_result = validate_issue_body(build_body(content={"目的": ""}))
        error_result = validate_issue_body(None)  # type: ignore[arg-type]
        statuses = {pass_result.status, violation_result.status, error_result.status}
        self.assertEqual(statuses, {ValidationStatus.PASS, ValidationStatus.CONTRACT_VIOLATION, ValidationStatus.INTERNAL_ERROR})


# ---------------------------------------------------------------------------
# AUTO-001-06-01: extract_task_fields() (Launcher向けpublic抽出API)
# ---------------------------------------------------------------------------

class ExtractTaskFieldsTests(unittest.TestCase):

    def test_pass_body_returns_all_fields(self):
        body = build_body()
        fields = extract_task_fields(body)
        self.assertIsNotNone(fields)
        d = fields.to_dict()
        self.assertEqual(d["management_id"], DEFAULT_CONTENT["管理ID"])
        self.assertEqual(d["purpose"], DEFAULT_CONTENT["目的"])
        self.assertEqual(d["expected_behavior"], DEFAULT_CONTENT["期待動作・決定事項"])
        self.assertEqual(d["non_goals"], DEFAULT_CONTENT["非対象範囲"])
        self.assertEqual(d["test_perspectives"], [DEFAULT_CONTENT["テスト観点"]])
        self.assertEqual(d["current_problem"], DEFAULT_CONTENT["現在の問題"])
        self.assertEqual(d["cause_hypotheses"], DEFAULT_CONTENT["原因に関する仮説"])
        self.assertEqual(d["risks"], [DEFAULT_CONTENT["リスク"]])
        self.assertEqual(d["human_confirmation_items"], DEFAULT_CONTENT["人間確認事項"])
        self.assertEqual(d["reference_materials"], DEFAULT_CONTENT["参考資料"])

    def test_contract_violation_body_returns_none(self):
        body = build_body(content={"目的": ""})
        self.assertEqual(validate_issue_body(body).status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIsNone(extract_task_fields(body))

    def test_internal_error_input_returns_none(self):
        self.assertIsNone(extract_task_fields(None))  # type: ignore[arg-type]

    def test_acceptance_criteria_preserve_order_and_structure(self):
        body = build_body(content={
            "受入条件": "- [ ] AC-01: 一つ目\n- [ ] AC-02: 二つ目\n- [ ] AC-03: 三つ目",
        })
        fields = extract_task_fields(body)
        self.assertIsNotNone(fields)
        ac_dicts = [ac.to_dict() for ac in fields.acceptance_criteria]
        self.assertEqual(ac_dicts, [
            {"id": "AC-01", "description": "一つ目"},
            {"id": "AC-02", "description": "二つ目"},
            {"id": "AC-03", "description": "三つ目"},
        ])

    def test_change_classification_has_exactly_the_three_fixed_labels(self):
        fields = extract_task_fields(build_body())
        self.assertIsNotNone(fields)
        self.assertEqual(
            set(fields.change_classification.keys()),
            {"サービス仕様変更", "リポジトリ運用仕様変更", "実装方法だけの変更"},
        )

    def test_change_classification_values_extracted(self):
        fields = extract_task_fields(build_body())
        self.assertIsNotNone(fields)
        self.assertEqual(fields.change_classification["リポジトリ運用仕様変更"], "あり")
        self.assertEqual(fields.change_classification["実装方法だけの変更"], "いいえ")

    def test_html_comment_only_optional_section_is_empty_string(self):
        body = build_body(content={"人間確認事項": "<!-- 内部メモ -->なし"})
        fields = extract_task_fields(body)
        self.assertIsNotNone(fields)
        self.assertEqual(fields.human_confirmation_items, "なし")

    def test_risks_and_test_perspectives_are_line_arrays(self):
        body = build_body(content={
            "リスク": "1件目のリスク\n2件目のリスク",
            "テスト観点": "観点A\n観点B\n観点C",
        })
        fields = extract_task_fields(body)
        self.assertIsNotNone(fields)
        self.assertEqual(fields.risks, ("1件目のリスク", "2件目のリスク"))
        self.assertEqual(fields.test_perspectives, ("観点A", "観点B", "観点C"))

    def test_single_line_risk_is_a_one_element_array(self):
        fields = extract_task_fields(build_body())
        self.assertIsNotNone(fields)
        self.assertEqual(fields.risks, ("なし",))

    def test_ambiguous_management_id_body_is_contract_violation_and_returns_none(self):
        body = build_body(content={"管理ID": "AUTO-001-05-01 AUTO-001-05-02"})
        self.assertEqual(validate_issue_body(body).status, ValidationStatus.CONTRACT_VIOLATION)
        self.assertIsNone(extract_task_fields(body))

    def test_deterministic_across_calls(self):
        body = build_body()
        first = extract_task_fields(body).to_dict()
        second = extract_task_fields(body).to_dict()
        self.assertEqual(first, second)

    def test_does_not_mutate_input_string(self):
        body = build_body()
        original = str(body)
        extract_task_fields(body)
        self.assertEqual(body, original)

    def test_existing_validate_issue_body_unaffected_by_new_api(self):
        # extract_task_fields()の追加が、既存のvalidate_issue_body()の
        # 判定結果に一切影響しないことを確認する(公開契約の非破壊)。
        body = build_body(content={"目的": ""})
        before = validate_issue_body(body)
        extract_task_fields(body)
        after = validate_issue_body(body)
        self.assertEqual(before.status, after.status)
        self.assertEqual(
            [e.to_dict() for e in before.errors], [e.to_dict() for e in after.errors],
        )


if __name__ == "__main__":
    unittest.main()
