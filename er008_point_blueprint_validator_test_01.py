# ============================================================
# er008_point_blueprint_validator_test_01.py
# A2/B1 Point Structure Semantic Alignment: 決定論的Structural Validatorの
# 受入条件Fixture(タスク仕様「Regression/品質条件」記載の6項目を含む)。
# API呼び出しは一切行わない(純粋なデータ構造の突き合わせのみ)。
# ============================================================
from __future__ import annotations

import unittest

from er008_shared_point_blueprint_01 import (
    SharedPointBlueprint, PointBlueprint, extract_trailing_metadata_block,
)
from er008_point_blueprint_validator_01 import (
    validate_blueprint_schema, check_fact_point_consistency, check_required_facts_present,
    check_b1_covers_common_facts, check_comment_fact_reference, validate_topic,
)


def make_blueprint() -> SharedPointBlueprint:
    return SharedPointBlueprint(
        topic_id="TEST-TOPIC",
        point_1=PointBlueprint(
            role="研究の分類・方法を示す",
            common_claim="研究は場を複数の型に分類した",
            common_fact_ids=["FACT-001", "FACT-002"],
            optional_b1_fact_ids=["FACT-003"],
            required_in_a2_fact_ids=["FACT-001"],
            comment_anchor="研究がいくつかの型を報告したことに注目してください。",
            prohibited_reference_fact_ids=["FACT-011", "FACT-012"],
        ),
        point_2=PointBlueprint(
            role="実際の事業者の対応例を示す",
            common_claim="ある事業者は利用制限を導入した",
            common_fact_ids=["FACT-011", "FACT-012"],
            optional_b1_fact_ids=["FACT-013"],
            required_in_a2_fact_ids=[],
            comment_anchor="ある事業者が利用制限を導入したことが分かりました。",
            prohibited_reference_fact_ids=[],
        ),
        point_transition="研究結果 -> 実際の事業者の対応",
    )


class BlueprintSchemaTests(unittest.TestCase):
    def test_valid_blueprint_passes_schema(self):
        bp = make_blueprint()
        result = validate_blueprint_schema(bp)
        self.assertTrue(result.ok, msg=result.violations)

    def test_duplicate_fact_assignment_fails_schema(self):
        bp = make_blueprint()
        bp.point_2.common_fact_ids.append("FACT-001")  # point_1にもある
        result = validate_blueprint_schema(bp)
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "schema_duplicate_fact_assignment" for v in result.violations))

    def test_empty_common_claim_fails_schema(self):
        bp = make_blueprint()
        bp.point_1.common_claim = ""
        result = validate_blueprint_schema(bp)
        self.assertFalse(result.ok)

    def test_required_in_a2_not_subset_fails_schema(self):
        bp = make_blueprint()
        bp.point_1.required_in_a2_fact_ids = ["FACT-999"]  # common_fact_idsに無い
        result = validate_blueprint_schema(bp)
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "schema_required_in_a2_not_subset" for v in result.violations))


class RequiredFixtureTests(unittest.TestCase):
    """タスク仕様「Regression/品質条件」に明記された6件のFixture。"""

    def test_1_a2_omits_optional_b1_fact_and_passes(self):
        bp = make_blueprint()
        a2_usage = {"point_1_fact_ids_used": ["FACT-001"],  # FACT-002/003は省略
                    "point_2_fact_ids_used": ["FACT-011"]}
        b1_usage = {"point_1_fact_ids_used": ["FACT-001", "FACT-002", "FACT-003"],
                    "point_2_fact_ids_used": ["FACT-011", "FACT-012", "FACT-013"]}
        result = check_fact_point_consistency(bp, a2_usage, b1_usage)
        self.assertTrue(result.ok, msg=result.violations)
        req_result = check_required_facts_present(bp, a2_usage)
        self.assertTrue(req_result.ok, msg=req_result.violations)

    def test_2_same_fact_different_point_across_levels_fails(self):
        bp = make_blueprint()
        a2_usage = {"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]}
        # B1がFACT-011(本来point_2)をpoint_1で使ってしまったケース
        b1_usage = {"point_1_fact_ids_used": ["FACT-001", "FACT-011"], "point_2_fact_ids_used": ["FACT-012"]}
        result = check_fact_point_consistency(bp, a2_usage, b1_usage)
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "fact_moved_to_different_point" for v in result.violations))

    def test_3_point_1_comment_referencing_point_2_fact_fails(self):
        bp = make_blueprint()
        # Point One後のCommentが、まだ聞いていないPoint TwoのFACT-011を参照
        result = check_comment_fact_reference(bp, "point_1", ["FACT-011"])
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "comment_references_other_point_fact" for v in result.violations))

    def test_4_shared_comment_referencing_b1_only_fact_fails(self):
        bp = make_blueprint()
        # Point One後の共通CommentがB1限定のFACT-003を参照
        result = check_comment_fact_reference(bp, "point_1", ["FACT-003"])
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "comment_references_b1_only_fact" for v in result.violations))

    def test_5_b1_extra_evidence_within_same_point_passes(self):
        bp = make_blueprint()
        a2_usage = {"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]}
        # B1が同じPoint 1内でoptional fact(FACT-003)も追加evidenceとして使う
        b1_usage = {"point_1_fact_ids_used": ["FACT-001", "FACT-002", "FACT-003"],
                    "point_2_fact_ids_used": ["FACT-011", "FACT-012", "FACT-013"]}
        result = check_fact_point_consistency(bp, a2_usage, b1_usage)
        self.assertTrue(result.ok, msg=result.violations)

    def test_6_unequal_point_word_counts_are_not_checked_and_pass(self):
        # WordCount自体はValidatorが一切見ていないことを、意図的に極端に
        # 不均等なcomment_anchor長で確認する(語数を理由にFAILしない)。
        bp = make_blueprint()
        bp.point_1.comment_anchor = "短い。"
        bp.point_2.comment_anchor = "非常に長い説明を意図的にここへ書きます。" * 20
        result = validate_blueprint_schema(bp)
        self.assertTrue(result.ok, msg=result.violations)
        a2_usage = {"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]}
        b1_usage = {"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]}
        result2 = check_fact_point_consistency(bp, a2_usage, b1_usage)
        self.assertTrue(result2.ok, msg=result2.violations)


class B1CommonFactCoverageTests(unittest.TestCase):
    """B1はA2と違い難易度・長さの都合による省略理由が無いため、
    common_fact_idsを欠くとFAILする(No.5相当: B1がPoint Twoで共通factを
    使わず、B1限定factだけで本文を組み立ててしまったケース)。"""

    def test_b1_missing_common_fact_fails(self):
        bp = make_blueprint()
        b1_usage = {"point_1_fact_ids_used": ["FACT-001", "FACT-002"],
                    "point_2_fact_ids_used": ["FACT-013"]}  # FACT-011/012(common)を使っていない
        result = check_b1_covers_common_facts(bp, b1_usage)
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "b1_common_fact_missing" for v in result.violations))

    def test_b1_covering_all_common_facts_passes(self):
        bp = make_blueprint()
        b1_usage = {"point_1_fact_ids_used": ["FACT-001", "FACT-002", "FACT-003"],
                    "point_2_fact_ids_used": ["FACT-011", "FACT-012", "FACT-013"]}
        result = check_b1_covers_common_facts(bp, b1_usage)
        self.assertTrue(result.ok, msg=result.violations)


class TrailingMetadataBlockTests(unittest.TestCase):
    def test_extracts_and_strips_trailing_json_block(self):
        text = ('# Title\n\nBody text here.\n\n## In one line...\nA short closing line.\n\n'
                '```json\n{"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]}\n```')
        clean, parsed = extract_trailing_metadata_block(text)
        self.assertEqual(parsed, {"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]})
        self.assertNotIn("```json", clean)
        self.assertTrue(clean.endswith("A short closing line."))

    def test_no_trailing_block_returns_none_unchanged(self):
        text = "# Title\n\nBody text with no metadata block.\n\n## In one line...\nClosing."
        clean, parsed = extract_trailing_metadata_block(text)
        self.assertIsNone(parsed)
        self.assertEqual(clean, text)

    def test_malformed_trailing_json_returns_none_unchanged(self):
        text = "# Title\n\nBody.\n\n```json\n{not valid json\n```"
        clean, parsed = extract_trailing_metadata_block(text)
        self.assertIsNone(parsed)
        self.assertEqual(clean, text)


class IntegratedValidateTopicTests(unittest.TestCase):
    def test_all_checks_pass_for_compliant_topic(self):
        bp = make_blueprint()
        result = validate_topic(
            bp,
            a2_writer_usage={"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]},
            b1_writer_usage={"point_1_fact_ids_used": ["FACT-001", "FACT-002", "FACT-003"],
                              "point_2_fact_ids_used": ["FACT-011", "FACT-012", "FACT-013"]},
            comment_after_point_1_refs=["FACT-001"],
            comment_after_point_2_refs=["FACT-011"],
        )
        self.assertTrue(result.ok, msg=result.violations)

    def test_no5_style_violation_detected(self):
        """ER-008 No.5相当: 共通CommentがB1限定Factを参照してしまうケース。"""
        bp = make_blueprint()
        result = validate_topic(
            bp,
            a2_writer_usage={"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]},
            b1_writer_usage={"point_1_fact_ids_used": ["FACT-001", "FACT-002", "FACT-003"],
                              "point_2_fact_ids_used": ["FACT-011", "FACT-012", "FACT-013"]},
            comment_after_point_2_refs=["FACT-013"],  # B1限定factを共通Commentが参照
        )
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "comment_references_b1_only_fact" for v in result.violations))

    def test_no6_style_violation_detected(self):
        """ER-008 No.6相当: A2とB1でFactのPoint所属が入れ替わるケース。"""
        bp = make_blueprint()
        result = validate_topic(
            bp,
            a2_writer_usage={"point_1_fact_ids_used": ["FACT-011"], "point_2_fact_ids_used": ["FACT-001"]},
            b1_writer_usage={"point_1_fact_ids_used": ["FACT-001"], "point_2_fact_ids_used": ["FACT-011"]},
        )
        self.assertFalse(result.ok)
        self.assertTrue(any(v.check == "fact_point_mismatch_across_levels" for v in result.violations))


if __name__ == "__main__":
    unittest.main()
