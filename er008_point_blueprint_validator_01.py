# ============================================================
# er008_point_blueprint_validator_01.py
# A2/B1 Point Structure Semantic Alignment: 決定論的Structural Validator
# ============================================================
# Shared Point Blueprint(er008_shared_point_blueprint_01.py)に対して、
# 実際にA2/B1 Writer・Support(Comment)が自己申告したfact_id利用状況
# (Writer/Comment出力末尾のfenced JSON block、extract_trailing_
# metadata_blockで抽出)を突き合わせ、構造的な不整合を検出する。
#
# 設計方針: 意味理解を必要とする新しいRuntime LLM Checkerは追加しない。
# ここでのcheckは全て、fact_idの集合演算・所属判定という決定論的な
# 処理のみで完結する(Blueprintの宣言と自己申告メタデータの突き合わせ)。
# 自己申告メタデータの正確性自体はWriter/Support LLM呼び出しの品質に
# 依存する(既知の限界、完了報告で開示する)。
from __future__ import annotations

from dataclasses import dataclass, field

from er008_shared_point_blueprint_01 import SharedPointBlueprint

VALID_SEVERITIES = ("FAIL", "PASS")


@dataclass
class Violation:
    check: str
    severity: str  # "FAIL"のみ(PASSはViolationを生成しない)
    message: str
    point_key: str = ""
    fact_ids: list = field(default_factory=list)


@dataclass
class ValidationResult:
    ok: bool
    violations: list = field(default_factory=list)

    def add(self, v: Violation) -> None:
        self.violations.append(v)
        self.ok = False


def _all_fact_ids(bp: SharedPointBlueprint) -> set:
    return (set(bp.point_1.common_fact_ids) | set(bp.point_1.optional_b1_fact_ids)
            | set(bp.point_2.common_fact_ids) | set(bp.point_2.optional_b1_fact_ids))


# ============================================================
# Check 0: Blueprintスキーマ自体の構造検証(必須項目・重複割り当て)
# ============================================================
def validate_blueprint_schema(bp: SharedPointBlueprint) -> ValidationResult:
    result = ValidationResult(ok=True)
    for label, p in (("point_1", bp.point_1), ("point_2", bp.point_2)):
        if not p.role or not p.role.strip():
            result.add(Violation("schema_required_field", "FAIL", f"{label}.roleが空です", label))
        if not p.common_claim or not p.common_claim.strip():
            result.add(Violation("schema_required_field", "FAIL", f"{label}.common_claimが空です", label))
        if not p.common_fact_ids:
            result.add(Violation("schema_required_field", "FAIL",
                                  f"{label}.common_fact_idsが空です(最低1件のcommon factが必要)", label))
        if not p.comment_anchor or not p.comment_anchor.strip():
            result.add(Violation("schema_required_field", "FAIL", f"{label}.comment_anchorが空です", label))

    # 同一fact_idが両方のPointへ重複して割り振られていないか
    p1_ids = set(bp.point_1.common_fact_ids) | set(bp.point_1.optional_b1_fact_ids)
    p2_ids = set(bp.point_2.common_fact_ids) | set(bp.point_2.optional_b1_fact_ids)
    overlap = p1_ids & p2_ids
    if overlap:
        result.add(Violation("schema_duplicate_fact_assignment", "FAIL",
                              f"同じfact_idがPoint One/Two両方に割り振られています: {sorted(overlap)}",
                              fact_ids=sorted(overlap)))

    # required_in_a2_fact_idsはcommon_fact_idsの部分集合であること
    for label, p in (("point_1", bp.point_1), ("point_2", bp.point_2)):
        extra = set(p.required_in_a2_fact_ids) - set(p.common_fact_ids)
        if extra:
            result.add(Violation("schema_required_in_a2_not_subset", "FAIL",
                                  f"{label}.required_in_a2_fact_idsにcommon_fact_idsに無いfact_idが"
                                  f"含まれています: {sorted(extra)}", label, sorted(extra)))
    return result


# ============================================================
# Check 1 + 2: A2/B1のfact利用申告をBlueprintの所属と突き合わせる
#   1. A2がoptional_b1_fact_idsを省略してもPASS(何もしない、正常系)
#   2. 同じfact_idをA2/B1で別Pointへ配置するとFAIL
# ============================================================
def check_fact_point_consistency(bp: SharedPointBlueprint,
                                  a2_usage: dict, b1_usage: dict) -> ValidationResult:
    """a2_usage/b1_usageは{"point_1_fact_ids_used": [...], "point_2_fact_ids_used": [...]}
    形式(Writer出力末尾のfenced JSON blockから抽出したものをそのまま渡す)。"""
    result = ValidationResult(ok=True)
    point_owner = {}
    for label, p in (("point_1", bp.point_1), ("point_2", bp.point_2)):
        for fid in set(p.common_fact_ids) | set(p.optional_b1_fact_ids):
            point_owner[fid] = label

    for level_name, usage in (("A2", a2_usage), ("B1", b1_usage)):
        if not usage:
            continue
        for used_point_key, used_ids in (("point_1", usage.get("point_1_fact_ids_used") or []),
                                          ("point_2", usage.get("point_2_fact_ids_used") or [])):
            for fid in used_ids:
                owner = point_owner.get(fid)
                if owner is None:
                    result.add(Violation(
                        "fact_id_not_in_blueprint", "FAIL",
                        f"{level_name}が使用したfact_id {fid!r} はBlueprintのどちらのPointにも"
                        f"登録されていません", used_point_key, [fid]))
                elif owner != used_point_key:
                    result.add(Violation(
                        "fact_moved_to_different_point", "FAIL",
                        f"{level_name}はfact_id {fid!r} を{used_point_key}で使用していますが、"
                        f"Blueprintでは{owner}に割り当てられています(Point間でFactが移動しています)",
                        used_point_key, [fid]))

    # A2/B1が同じfact_idを互いに違うPointで使っていないか(直接比較でも検出)
    def flat(usage: dict) -> dict:
        m = {}
        for pk in ("point_1", "point_2"):
            for fid in (usage or {}).get(f"{pk}_fact_ids_used") or []:
                m[fid] = pk
        return m

    a2_flat, b1_flat = flat(a2_usage), flat(b1_usage)
    for fid in set(a2_flat) & set(b1_flat):
        if a2_flat[fid] != b1_flat[fid]:
            result.add(Violation(
                "fact_point_mismatch_across_levels", "FAIL",
                f"fact_id {fid!r} がA2では{a2_flat[fid]}、B1では{b1_flat[fid]}として使用されています"
                f"(同じFactが別のPointへ配置されています)", fact_ids=[fid]))
    return result


# ============================================================
# Check: A2に必須のfactが欠落していないか(required_in_a2_fact_ids)
# ============================================================
def check_required_facts_present(bp: SharedPointBlueprint, a2_usage: dict) -> ValidationResult:
    result = ValidationResult(ok=True)
    if not a2_usage:
        return result  # 自己申告なし(旧来のBlueprint未使用呼び出し)は対象外、後方互換
    for label, p in (("point_1", bp.point_1), ("point_2", bp.point_2)):
        used = set((a2_usage.get(f"{label}_fact_ids_used")) or [])
        missing = set(p.required_in_a2_fact_ids) - used
        if missing:
            result.add(Violation(
                "required_a2_fact_missing", "FAIL",
                f"A2の{label}に必須指定されたfact_idが使用されていません: {sorted(missing)}",
                label, sorted(missing)))
    return result


def check_b1_covers_common_facts(bp: SharedPointBlueprint, b1_usage: dict) -> ValidationResult:
    """B1は難易度・長さの都合でfactを省略する理由がA2と違って無いため、
    common_fact_ids(両レベル共通、必ずこのPointで扱うべきfact)は全て
    含めることを期待する(Fact所属ルール5「A2は...省略してよい」の
    裏返し、B1には省略の許可を与えない)。A2の必須subsetだけでなく、
    common_fact_ids全体を対象にする点がcheck_required_facts_presentとの
    違い。"""
    result = ValidationResult(ok=True)
    if not b1_usage:
        return result
    for label, p in (("point_1", bp.point_1), ("point_2", bp.point_2)):
        used = set((b1_usage.get(f"{label}_fact_ids_used")) or [])
        missing = set(p.common_fact_ids) - used
        if missing:
            result.add(Violation(
                "b1_common_fact_missing", "FAIL",
                f"B1の{label}が、両レベル共通のはずのfact_idを使用していません: {sorted(missing)}"
                f"(common_claim「{p.common_claim}」を支える根拠が本文から欠落している可能性)",
                label, sorted(missing)))
    return result


# ============================================================
# Check 3 + 4: Comment(Support)のfact参照をcomment_anchorの範囲と
#   突き合わせる
#   3. Point 1 CommentがPoint 2のFactを参照するとFAIL
#   4. 共通CommentがB1-only Fact(optional_b1_fact_ids)を参照するとFAIL
# ============================================================
def check_comment_fact_reference(bp: SharedPointBlueprint, point_key: str,
                                  referenced_fact_ids: list) -> ValidationResult:
    """point_keyは、このCommentが「どのPointの直後に流れるか」を表す
    ("point_1"ならPoint One直後、"point_2"ならPoint Two直後)。"""
    result = ValidationResult(ok=True)
    if not referenced_fact_ids:
        return result

    this_point = bp.point_1 if point_key == "point_1" else bp.point_2
    other_point = bp.point_2 if point_key == "point_1" else bp.point_1

    safe_ids = set(this_point.common_fact_ids)  # comment_anchorはcommon_fact_idsの範囲のみを想定
    other_all_ids = set(other_point.common_fact_ids) | set(other_point.optional_b1_fact_ids)
    b1_only_ids = set(this_point.optional_b1_fact_ids)

    for fid in referenced_fact_ids:
        if fid in other_all_ids:
            result.add(Violation(
                "comment_references_other_point_fact", "FAIL",
                f"Comment({point_key}後)がまだ提示されていない{('Point Two' if point_key=='point_1' else 'Point One')}"
                f"のfact_id {fid!r} を参照しています(ネタバレ)", point_key, [fid]))
        elif fid in b1_only_ids:
            result.add(Violation(
                "comment_references_b1_only_fact", "FAIL",
                f"共通Comment({point_key}後)がB1のみのoptional fact_id {fid!r} を参照しています"
                f"(A2では提示されていない可能性が高い)", point_key, [fid]))
        elif fid not in safe_ids:
            result.add(Violation(
                "comment_references_unknown_fact", "FAIL",
                f"Comment({point_key}後)が参照したfact_id {fid!r} はBlueprintのcommon_fact_idsに"
                f"存在しません", point_key, [fid]))
    return result


# ============================================================
# 統合エントリポイント
# ============================================================
def validate_topic(bp: SharedPointBlueprint, *, a2_writer_usage: dict = None, b1_writer_usage: dict = None,
                    comment_after_point_1_refs: list = None, comment_after_point_2_refs: list = None) -> ValidationResult:
    """1 Topic分の全checkをまとめて実行する。引数がNone(自己申告データが
    無い)の項目はスキップされる(後方互換、Blueprint未使用の呼び出しに
    対して誤ってFAILを出さないため)。"""
    result = ValidationResult(ok=True)
    for sub in (
        validate_blueprint_schema(bp),
        check_fact_point_consistency(bp, a2_writer_usage or {}, b1_writer_usage or {}),
        check_required_facts_present(bp, a2_writer_usage or {}),
        check_b1_covers_common_facts(bp, b1_writer_usage or {}),
        check_comment_fact_reference(bp, "point_1", comment_after_point_1_refs or []),
        check_comment_fact_reference(bp, "point_2", comment_after_point_2_refs or []),
    ):
        result.violations.extend(sub.violations)
        result.ok = result.ok and sub.ok
    return result
