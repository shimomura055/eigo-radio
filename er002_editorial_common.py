# ============================================================
# er002_editorial_common.py
# ER-002-v1.1A: 固定記事(A01・A02)向け編集工程の共通基盤
# ============================================================
# 「編集アングル生成→評価・選定→Editorial Brief→検品→台本生成→編集品質
# 検品」という新工程を、記事採用基準(トピック選定)とは完全に分離した
# モジュールとして実装する。
#
# モデルの責務分離(ER-002-v1.1A-I1の指示どおり):
#   編集アングル生成: 既存OpenAI台本生成モデル(er002_script_adapter.MODEL_WRITE)
#   台本生成:        既存OpenAI台本生成モデル(同上)
#   アングル評価:     既存Gemini QAモデル(er002_common.QA_MODEL_NAME)
#   Editorial Brief検品: 既存Gemini QAモデル(同上)
#   台本編集品質検品:  既存Gemini QAモデル(同上)
# 生成と評価は必ず別のAPI応答(別呼び出し)で行い、同一呼び出し内で
# 自己採点させない。
#
# このモジュールは実APIを一切呼び出さない(呼び出し関数は引数として
# 注入される。ER-002-v1.1A-I1ではモックのみで検証する)。

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

import er002_common as common

# ============================================================
# ブロック1: モデル責務(定数として明示)
# ============================================================
ANGLE_GENERATION_MODEL_ROLE = "openai_script_model"
ANGLE_EVALUATION_MODEL_ROLE = "gemini_qa_model"
BRIEF_INSPECTION_MODEL_ROLE = "gemini_qa_model"
SCRIPT_GENERATION_MODEL_ROLE = "openai_script_model"
EDITORIAL_QUALITY_MODEL_ROLE = "gemini_qa_model"


def sha256_text(text: str) -> str:
    return common.sha256_text(text)


def sha256_json(obj: Any) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


# ============================================================
# ブロック2: 事実ID(raw_facts.jsonのverified_factsへ安定IDを付与)
# ============================================================
def assign_fact_ids(verified_facts: list[str]) -> dict[str, str]:
    """{"F01": fact_text, "F02": fact_text, ...} を返す。verified_factsの
    並び順に基づく安定ID(general_knowledge_contextにはIDを振らない。
    v1.1Aでは新しい具体的事実主張の根拠として使わないため)。"""
    return {f"F{i + 1:02d}": fact for i, fact in enumerate(verified_facts)}


def validate_fact_id_refs(fact_ids: list, valid_ids: set, *, allow_empty: bool, context: str) -> list[str]:
    """不正なfact_id参照のエラーメッセージ一覧を返す(例外は投げない)。"""
    errors = []
    if not fact_ids:
        if not allow_empty:
            errors.append(f"{context}: fact_idsが空です")
        return errors
    for fid in fact_ids:
        if fid not in valid_ids:
            errors.append(f"{context}: 存在しないfact_id '{fid}' が参照されています")
    return errors


# ============================================================
# ブロック3: 編集アングル候補スキーマ
# ============================================================
OPENING_MODES = ["verified_event", "hypothetical", "direct_question", "contrast"]

EDITORIAL_ROLE_VOCAB = [
    "cause_explanation",
    "consequence_or_stakes",
    "counterpoint_or_tension",
    "human_or_concrete_detail",
    "context_or_comparison",
    "mechanism_or_process",
]

# openingが具体的事実の裏付けを必須としないモード
# (hypotheticalは定義上verified事実そのものではない。direct_questionは
# 問いかけであり単独の事実主張ではないため、空でも許容する)
OPENING_MODES_ALLOWING_EMPTY_FACT_IDS = ("hypothetical", "direct_question")


@dataclass
class EditorialAngleCandidate:
    angle_id: str
    article_id: str
    listener_relevance: str
    central_tension_or_question: str
    concrete_opening: str
    opening_mode: str
    non_obvious_takeaway: str
    point_one_editorial_role: str
    point_one_core_claim: str
    point_two_editorial_role: str
    point_two_core_claim: str
    listener_payoff: str
    in_one_line_target: str
    opening_fact_ids: list = field(default_factory=list)
    hypothetical_disclosure_required: bool = False
    point_one_fact_ids: list = field(default_factory=list)
    point_two_fact_ids: list = field(default_factory=list)
    fact_support_map: list = field(default_factory=list)  # [{"fact_id": "F01", "used_for": "..."}]
    unsupported_assumptions: list = field(default_factory=list)
    generated_at: Optional[str] = None


def validate_candidate_structure(candidate: dict, valid_fact_ids: set) -> list[str]:
    """1案の構造的妥当性を検証する(fact ID参照・opening根拠・役割/主張の
    重複)。評価LLMの判定とは独立に、コードだけで機械的に判定できる項目。"""
    errors = []

    opening_mode = candidate.get("opening_mode")
    if opening_mode not in OPENING_MODES:
        errors.append(f"不正なopening_mode: {opening_mode!r}")

    role1 = candidate.get("point_one_editorial_role")
    role2 = candidate.get("point_two_editorial_role")
    if role1 not in EDITORIAL_ROLE_VOCAB:
        errors.append(f"不正なpoint_one_editorial_role: {role1!r}")
    if role2 not in EDITORIAL_ROLE_VOCAB:
        errors.append(f"不正なpoint_two_editorial_role: {role2!r}")

    allow_empty_opening = opening_mode in OPENING_MODES_ALLOWING_EMPTY_FACT_IDS
    errors += validate_fact_id_refs(
        candidate.get("opening_fact_ids", []), valid_fact_ids,
        allow_empty=allow_empty_opening, context="opening_fact_ids")
    errors += validate_fact_id_refs(
        candidate.get("point_one_fact_ids", []), valid_fact_ids,
        allow_empty=False, context="point_one_fact_ids")
    errors += validate_fact_id_refs(
        candidate.get("point_two_fact_ids", []), valid_fact_ids,
        allow_empty=False, context="point_two_fact_ids")

    fact_support_map = candidate.get("fact_support_map", [])
    if not fact_support_map:
        errors.append("fact_support_mapが空です")
    for entry in fact_support_map:
        fid = entry.get("fact_id") if isinstance(entry, dict) else None
        if fid not in valid_fact_ids:
            errors.append(f"fact_support_map: 存在しないfact_id {fid!r}")

    if opening_mode == "hypothetical" and not candidate.get("hypothetical_disclosure_required"):
        errors.append("opening_mode=hypotheticalの場合、hypothetical_disclosure_requiredはTrue必須です")

    # 役割enumが異なるだけでは不十分。core_claimも実質的に異なる必要がある
    # (「実質的」の完全な意味判定はLLM評価に委ねるが、明白な完全一致は
    # ここで機械的に弾く)。
    if role1 is not None and role1 == role2:
        errors.append("point_one_editorial_roleとpoint_two_editorial_roleが同一です")
    claim1 = (candidate.get("point_one_core_claim") or "").strip().lower()
    claim2 = (candidate.get("point_two_core_claim") or "").strip().lower()
    if claim1 and claim1 == claim2:
        errors.append("point_one_core_claimとpoint_two_core_claimが同一です")

    return errors


def rule_based_diversity_prescreen(candidates: list[dict]) -> list[str]:
    """3案の明白な重複(完全一致)だけを検出する診断的な早期棄却チェック。
    これに通っても意味的な多様性を保証しない。実質的な多様性判定は
    アングル評価(LLM)で別途行う(ルールベース検査でLLM検品を省略しない
    という方針を、アングル多様性判定にも一貫して適用する)。"""
    errors = []

    tensions = [str(c.get("central_tension_or_question", "")).strip().lower() for c in candidates]
    if len(set(tensions)) < len(tensions):
        errors.append("central_tension_or_questionが完全一致する案があります")

    role_combos = [
        (c.get("point_one_editorial_role"), c.get("point_two_editorial_role")) for c in candidates
    ]
    if len(set(role_combos)) < len(role_combos):
        errors.append("Pointの役割組み合わせが完全一致する案があります")

    takeaways = [str(c.get("non_obvious_takeaway", "")).strip().lower() for c in candidates]
    if len(set(takeaways)) < len(takeaways):
        errors.append("non_obvious_takeawayが完全一致する案があります")

    return errors


# ============================================================
# ブロック4: アングル評価(Gemini QAモデル、生成とは別呼び出し)
# ============================================================
ANGLE_SCORING_FIELDS = [
    "concreteness",
    "article_specificity",
    "non_obviousness",
    "listener_relevance_score",
    "point_role_distinctness",
    "fact_groundedness",
    "word_budget_feasibility",
]

ANGLE_PROVISIONAL_PASS_THRESHOLDS = {
    "article_specificity": 3,
    "non_obviousness": 3,
    "listener_relevance_score": 3,
    "point_role_distinctness": 4,
    "fact_groundedness": 5,
    "word_budget_feasibility": 3,
}
ANGLE_TOTAL_SCORE_MIN = 24

ANGLE_RANK_TIEBREAK_ORDER = [
    "non_obviousness", "listener_relevance_score", "point_role_distinctness",
    "concreteness", "article_specificity", "fact_groundedness", "word_budget_feasibility",
]

ANGLE_EVALUATION_PROMPT_TEMPLATE = """You are an independent editorial evaluator. You did NOT write the following 3 editorial angle candidates - your job is only to score and rank them. Do not soften scores out of politeness; a generic or redundant angle must score low.

CANDIDATES:
{candidates_block}

VALID FACT IDS: {valid_fact_ids}

First, assess DIVERSITY across all 3 candidates as a group: are they genuinely different angles, or is one (or more) essentially the same angle reworded in different language? Consider central_tension_or_question, the (point_one_editorial_role, point_two_editorial_role) combination, and non_obvious_takeaway.

Then, for EACH candidate independently, score 1-5 on these exact 7 criteria, and give a short evidence string for EVERY score (evidence is mandatory - a missing evidence string makes your response unusable):
1. concreteness
2. article_specificity (a generic angle that could apply to almost any story must score low)
3. non_obviousness
4. listener_relevance_score
5. point_role_distinctness (do the two points genuinely do different jobs?)
6. fact_groundedness (5 only if every claim traces to a valid fact ID; lower otherwise)
7. word_budget_feasibility (can this be told well in 380-420 English words?)

Also report for each candidate:
- unsupported_assumptions_detected: true if the candidate relies on any claim not directly supported by the valid fact IDs
- fact_id_reference_valid: true only if every fact ID referenced by the candidate is in the VALID FACT IDS list above
- forced_disqualification_reasons: list any other reason this candidate should be automatically disqualified (empty list if none)

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "diversity_passed": true,
  "diversity_evidence": "brief explanation",
  "candidates": {{
    "angle_1": {{
      "scores": {{"concreteness": 4, "article_specificity": 4, "non_obviousness": 4, "listener_relevance_score": 4, "point_role_distinctness": 4, "fact_groundedness": 5, "word_budget_feasibility": 4}},
      "evidence": {{"concreteness": "...", "article_specificity": "...", "non_obviousness": "...", "listener_relevance_score": "...", "point_role_distinctness": "...", "fact_groundedness": "...", "word_budget_feasibility": "..."}},
      "unsupported_assumptions_detected": false,
      "fact_id_reference_valid": true,
      "forced_disqualification_reasons": []
    }},
    "angle_2": {{ ... same shape ... }},
    "angle_3": {{ ... same shape ... }}
  }}
}}"""


def build_angle_evaluation_prompt(candidates: list[dict], valid_fact_ids: set) -> str:
    candidates_block = json.dumps(candidates, ensure_ascii=False, indent=2)
    return ANGLE_EVALUATION_PROMPT_TEMPLATE.format(
        candidates_block=candidates_block, valid_fact_ids=sorted(valid_fact_ids),
    )


class AngleEvaluationInconclusive(Exception):
    """評価応答の解析不能・必須項目欠落・evidence欠落を表す(fail-closed)。"""


def _require_evidence(evidence: Any, fields: list[str], where: str) -> None:
    if not isinstance(evidence, dict):
        raise AngleEvaluationInconclusive(f"{where}: evidenceがオブジェクトではありません")
    missing = [f for f in fields if not evidence.get(f)]
    if missing:
        raise AngleEvaluationInconclusive(f"{where}: evidence欠落 {missing}")


@dataclass
class AngleCandidateEvaluation:
    angle_id: str
    scores: dict
    evidence: dict
    total_score: int
    eligible: bool
    disqualification_reasons: list
    structural_errors: list


@dataclass
class AngleSelectionResult:
    status: str  # "selected" / "all_disqualified" / "diversity_failed" / "inconclusive"
    selected_angle_id: Optional[str] = None
    ranking: list = field(default_factory=list)  # 適格候補のangle_id、順位順
    per_candidate: dict = field(default_factory=dict)  # angle_id -> AngleCandidateEvaluation
    diversity_passed: Optional[bool] = None
    reason: Optional[str] = None


def classify_angle_evaluation(
    raw_result: dict,
    candidates: list[dict],
    valid_fact_ids: set,
) -> AngleSelectionResult:
    """アングル評価(Gemini QA)の生応答を解析し、多様性判定・各案の暫定合否・
    順位付けまでを行う。evidence欠落・応答不備はAngleEvaluationInconclusive
    として送出し、呼び出し側はfail-closedで扱う(再評価対象)。"""
    if not isinstance(raw_result, dict):
        raise AngleEvaluationInconclusive("評価応答がJSONオブジェクトではありません")

    diversity_passed = raw_result.get("diversity_passed")
    if not isinstance(diversity_passed, bool):
        raise AngleEvaluationInconclusive("diversity_passedが真偽値で返っていません")
    if not raw_result.get("diversity_evidence"):
        raise AngleEvaluationInconclusive("diversity_evidenceが欠落しています")

    candidates_result = raw_result.get("candidates")
    if not isinstance(candidates_result, dict):
        raise AngleEvaluationInconclusive("candidatesが返っていません")

    # ルールベース早期棄却(完全一致)も加味する。診断結果を握りつぶさない。
    prescreen_errors = rule_based_diversity_prescreen(candidates)

    if not diversity_passed or prescreen_errors:
        return AngleSelectionResult(
            status="diversity_failed", diversity_passed=False,
            reason="; ".join([raw_result.get("diversity_evidence", "")] + prescreen_errors),
        )

    per_candidate = {}
    for c in candidates:
        cid = c["angle_id"]
        entry = candidates_result.get(cid)
        if not isinstance(entry, dict):
            raise AngleEvaluationInconclusive(f"{cid}の評価が見つかりません")

        scores = entry.get("scores")
        if not isinstance(scores, dict):
            raise AngleEvaluationInconclusive(f"{cid}: scoresが不正です")
        missing_scores = [f for f in ANGLE_SCORING_FIELDS if f not in scores]
        if missing_scores:
            raise AngleEvaluationInconclusive(f"{cid}: scores欠落 {missing_scores}")

        _require_evidence(entry.get("evidence"), ANGLE_SCORING_FIELDS, cid)

        total = sum(scores[f] for f in ANGLE_SCORING_FIELDS)
        reasons = []
        for field_name, threshold in ANGLE_PROVISIONAL_PASS_THRESHOLDS.items():
            if scores[field_name] < threshold:
                reasons.append(f"{field_name}<{threshold}")
        if total < ANGLE_TOTAL_SCORE_MIN:
            reasons.append(f"total<{ANGLE_TOTAL_SCORE_MIN}")
        if entry.get("unsupported_assumptions_detected"):
            reasons.append("unsupported_assumptions_detected")
        if not entry.get("fact_id_reference_valid", False):
            reasons.append("fact_id_reference_invalid")
        reasons += list(entry.get("forced_disqualification_reasons", []))

        structural_errors = validate_candidate_structure(c, valid_fact_ids)
        if structural_errors:
            reasons += structural_errors

        per_candidate[cid] = AngleCandidateEvaluation(
            angle_id=cid, scores=scores, evidence=entry["evidence"], total_score=total,
            eligible=(len(reasons) == 0), disqualification_reasons=reasons,
            structural_errors=structural_errors,
        )

    eligible_ids = [cid for cid, ev in per_candidate.items() if ev.eligible]
    if not eligible_ids:
        return AngleSelectionResult(
            status="all_disqualified", diversity_passed=True, per_candidate=per_candidate,
            reason="適格な案がありません",
        )

    def sort_key(cid):
        ev = per_candidate[cid]
        return tuple([-ev.total_score] + [-ev.scores[f] for f in ANGLE_RANK_TIEBREAK_ORDER])

    ranking = sorted(eligible_ids, key=sort_key)
    return AngleSelectionResult(
        status="selected", selected_angle_id=ranking[0], ranking=ranking,
        per_candidate=per_candidate, diversity_passed=True,
    )


# ============================================================
# ブロック5: Editorial Brief
# ============================================================
EDITORIAL_BRIEF_FIELDS = [
    "central_tension_or_question", "opening_mode", "concrete_opening", "opening_fact_ids",
    "hypothetical_disclosure_required", "point_one_editorial_role", "point_one_core_claim",
    "point_one_fact_ids", "point_two_editorial_role", "point_two_core_claim", "point_two_fact_ids",
    "non_obvious_takeaway", "listener_payoff", "in_one_line_target", "fact_support_map",
]


def build_editorial_brief(candidate: dict) -> dict:
    """選定されたアングルからEditorial Briefを構築する(必要フィールドだけを
    固定して切り出す)。"""
    return {k: candidate[k] for k in EDITORIAL_BRIEF_FIELDS}


BRIEF_INSPECTION_PROMPT_TEMPLATE = """You are inspecting an EDITORIAL BRIEF that was already selected by a separate scoring process. You did NOT select it - your job is only to independently re-verify it before it is frozen and passed to script generation.

EDITORIAL BRIEF:
{brief_block}

VALID FACT IDS: {valid_fact_ids}

Check independently:
1. schema_valid: does the brief contain all required fields with plausible, non-empty values?
2. fact_ids_valid: does every fact ID referenced anywhere in the brief (opening_fact_ids, point_one_fact_ids, point_two_fact_ids, fact_support_map) appear in VALID FACT IDS, with none empty where a concrete claim is being made?
3. roles_distinct: are point_one_editorial_role and point_two_editorial_role different values?
4. claims_distinct: are point_one_core_claim and point_two_core_claim substantively different claims (not the same idea reworded)?

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "schema_valid": true,
  "fact_ids_valid": true,
  "roles_distinct": true,
  "claims_distinct": true,
  "overall_status": "pass",
  "evidence": "brief explanation of your checks"
}}"""


def build_brief_inspection_prompt(brief: dict, valid_fact_ids: set) -> str:
    """valid_fact_idsは記事全体の事実ID全集合(assign_fact_idsの出力キー)を
    渡すこと。brief自身が参照しているIDだけを基準にすると、参照先が
    存在するかどうかの判定が自明になってしまい検品の意味がなくなるため。"""
    brief_block = json.dumps(brief, ensure_ascii=False, indent=2)
    return BRIEF_INSPECTION_PROMPT_TEMPLATE.format(
        brief_block=brief_block, valid_fact_ids=sorted(valid_fact_ids),
    )


class BriefInspectionInconclusive(Exception):
    pass


def classify_brief_inspection(raw_result: dict, brief: dict, valid_fact_ids: set) -> dict:
    """Editorial Brief検品(Gemini QA、アングル評価とは別呼び出し)の応答を
    解析する。スキーマ・事実参照・役割/主張の相違を再確認する独立ゲート。"""
    if not isinstance(raw_result, dict):
        raise BriefInspectionInconclusive("Brief検品応答がJSONオブジェクトではありません")

    required = ["schema_valid", "fact_ids_valid", "roles_distinct", "claims_distinct", "overall_status", "evidence"]
    missing = [k for k in required if k not in raw_result]
    if missing:
        raise BriefInspectionInconclusive(f"Brief検品応答に必須フィールドが欠落: {missing}")
    if not raw_result.get("evidence"):
        raise BriefInspectionInconclusive("Brief検品応答にevidenceがありません")

    # コード側でも独立に再検証する(LLM任せにしない)
    structural_errors = validate_candidate_structure(
        {**brief, "angle_id": "brief", "article_id": ""}, valid_fact_ids)

    llm_passed = (
        raw_result.get("schema_valid") is True
        and raw_result.get("fact_ids_valid") is True
        and raw_result.get("roles_distinct") is True
        and raw_result.get("claims_distinct") is True
        and raw_result.get("overall_status") == "pass"
    )
    passed = llm_passed and not structural_errors

    return {
        "passed": passed,
        "llm_result": raw_result,
        "structural_errors": structural_errors,
    }


# ============================================================
# ブロック6: 編集品質検品(全台本に必須。ER-002-v1.1A-I1の指示どおり)
# ============================================================
EDITORIAL_QUALITY_REQUIRED_FIELDS = [
    "brief_alignment", "opening_is_specific", "opening_is_grounded", "hypothetical_is_disclosed",
    "central_tension_present", "point_one_role_fulfilled", "point_two_role_fulfilled",
    "point_claims_are_distinct", "point_redundancy_detected", "narrative_coherence_present",
    "fact_enumeration_dominates", "non_obvious_takeaway_landed", "listener_payoff_present",
    "ungrounded_claims", "claim_strength_changed", "overstatement_or_dramatization",
    "overall_status", "evidence",
]

MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS = 2  # 1回目+解析不能時のみ1回再評価

EDITORIAL_QUALITY_PROMPT_TEMPLATE = """You are checking a finished script against the EDITORIAL BRIEF it was supposed to follow, and against the CLAIM STRENGTH ESCALATION categories below. You did not write the script or the brief.

EDITORIAL BRIEF:
{brief_block}

SCRIPT TEXT:
{script_text}

CLAIM STRENGTH ESCALATION CATEGORIES (flag any place the script states something MORE strongly than the brief/facts support, in any of these directions): {escalation_categories}

Check all of the following and answer each with true/false (or, for hypothetical_is_disclosed, null if the brief's opening_mode was not "hypothetical"):
- brief_alignment: does the script follow the brief's central_tension_or_question, opening, and both point roles/claims?
- opening_is_specific: is the opening a concrete moment/question, not a generic topic summary?
- opening_is_grounded: is the opening's factual content consistent with the brief's opening_fact_ids (or, if hypothetical, clearly marked as such)?
- hypothetical_is_disclosed: if opening_mode is "hypothetical", does the script clearly signal this to the listener? (null if not applicable)
- central_tension_present: does the script maintain the central tension/question as a throughline?
- point_one_role_fulfilled / point_two_role_fulfilled: does each point actually do its assigned editorial job?
- point_claims_are_distinct: are the two points' core claims substantively different (not overlapping/redundant)?
- point_redundancy_detected: true if Point One and Point Two restate the same idea
- narrative_coherence_present: does the script build a throughline/cause-effect narrative rather than a flat list of facts?
- fact_enumeration_dominates: true if the script reads mainly as a sequence of disconnected facts
- non_obvious_takeaway_landed: does the ending deliver the brief's non_obvious_takeaway?
- listener_payoff_present: does the listener clearly get something (insight/reframing) by the end?
- ungrounded_claims: list any claim, number, quote, psychological state, or scene NOT supported by the brief's cited facts (empty list if none)
- claim_strength_changed: list any escalation matching the categories above, each as {{"category": "...", "original": "...", "escalated_to": "..."}} (empty list if none)
- overstatement_or_dramatization: true if the script uses emotionally exaggerated language not warranted by the facts

overall_status: "pass" only if brief_alignment is true, no redundancy/enumeration/overstatement/ungrounded-claims/escalation issues were found, and both points fulfill their roles. Otherwise "fail".

evidence is MANDATORY: give a short justification (a dict or string) referencing the specific parts of the script that led to your judgments. Do not return this field empty.

Return ONLY valid JSON, no other text, in exactly this shape:
{{
  "brief_alignment": true, "opening_is_specific": true, "opening_is_grounded": true,
  "hypothetical_is_disclosed": null, "central_tension_present": true,
  "point_one_role_fulfilled": true, "point_two_role_fulfilled": true,
  "point_claims_are_distinct": true, "point_redundancy_detected": false,
  "narrative_coherence_present": true, "fact_enumeration_dominates": false,
  "non_obvious_takeaway_landed": true, "listener_payoff_present": true,
  "ungrounded_claims": [], "claim_strength_changed": [], "overstatement_or_dramatization": false,
  "overall_status": "pass", "evidence": "brief explanation"
}}"""


def build_editorial_quality_prompt(script: dict, brief: dict) -> str:
    plan = common.build_narration_plan(script)
    escalation_categories = [
        f"{e['from_label']} -> {e['to_label']}" for e in CLAIM_STRENGTH_ESCALATION_TAXONOMY
    ]
    return EDITORIAL_QUALITY_PROMPT_TEMPLATE.format(
        brief_block=json.dumps(brief, ensure_ascii=False, indent=2),
        script_text=plan.full_text,
        escalation_categories=escalation_categories,
    )


class EditorialQualityParseError(Exception):
    pass


def validate_editorial_quality_fields(parsed: dict) -> dict:
    """必須フィールド欠落はfail-closed対象として扱う(technical QAの
    parse_qa_jsonと同じ考え方)。呼び出し側で既にJSON解析済みのdictを渡す。"""
    missing = [f for f in EDITORIAL_QUALITY_REQUIRED_FIELDS if f not in parsed]
    if missing:
        raise EditorialQualityParseError(f"編集品質検品応答に必須フィールドが欠落: {missing}")
    if not parsed.get("evidence"):
        raise EditorialQualityParseError("編集品質検品応答にevidenceがありません")
    return parsed


def parse_editorial_quality_response(raw_text: Optional[str]) -> dict:
    """生テキストから解析する版(単体テスト・直接利用向け)。
    QAParseErrorはそのまま伝播させる。"""
    return validate_editorial_quality_fields(common.parse_qa_json(raw_text))


def classify_editorial_quality(result: dict) -> dict:
    """overall_status=="pass"かつ危険フラグが立っていないことを要求する。
    ここに到達している時点でparse_editorial_quality_responseは通過済み
    (必須フィールド・evidenceは存在する)。"""
    danger_flags = {
        "point_redundancy_detected": result.get("point_redundancy_detected") is True,
        "fact_enumeration_dominates": result.get("fact_enumeration_dominates") is True,
        "overstatement_or_dramatization": result.get("overstatement_or_dramatization") is True,
        "ungrounded_claims_present": bool(result.get("ungrounded_claims")),
        "claim_strength_changed_present": bool(result.get("claim_strength_changed")),
    }
    required_true = {
        "brief_alignment": result.get("brief_alignment") is True,
        "opening_is_specific": result.get("opening_is_specific") is True,
        "opening_is_grounded": result.get("opening_is_grounded") is True,
        "central_tension_present": result.get("central_tension_present") is True,
        "point_one_role_fulfilled": result.get("point_one_role_fulfilled") is True,
        "point_two_role_fulfilled": result.get("point_two_role_fulfilled") is True,
        "point_claims_are_distinct": result.get("point_claims_are_distinct") is True,
        "narrative_coherence_present": result.get("narrative_coherence_present") is True,
        "non_obvious_takeaway_landed": result.get("non_obvious_takeaway_landed") is True,
        "listener_payoff_present": result.get("listener_payoff_present") is True,
    }
    # hypothetical_is_disclosedは、opening_mode!=hypotheticalの場合はnull(該当なし)を許容
    hyp = result.get("hypothetical_is_disclosed")
    hypothetical_ok = hyp is True or hyp is None

    reasons = [k for k, v in required_true.items() if not v]
    reasons += [k for k, v in danger_flags.items() if v]
    if not hypothetical_ok:
        reasons.append("hypothetical_is_disclosed_false")

    passed = (result.get("overall_status") == "pass") and not reasons
    return {"passed": passed, "reasons": reasons, "raw": result}


@dataclass
class EditorialQualityAttemptRecord:
    attempt_number: int
    outcome: str  # "passed" / "conclusive_fail" / "inconclusive"
    reasons: list
    api_retry_count: int = 0


@dataclass
class EditorialQualityOutcome:
    final_outcome: str  # "passed" / "conclusive_fail" / "inconclusive"
    reasons: list
    attempts: list  # list[EditorialQualityAttemptRecord]
    total_api_retry_count: int = 0


def evaluate_editorial_quality(
    prompt: str,
    qa_call_fn: Callable[[str], str],
    max_eval_attempts: int = MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS,
    max_api_retry: int = common.MAX_QA_API_RETRY,
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> EditorialQualityOutcome:
    """evaluate_qa_for_audio(er002_common.py)と同じ状態遷移: 解析不能・
    必須フィールド欠落は"inconclusive"として同じ台本を再評価する
    (最大max_eval_attempts回)。有効な形式で不合格を検出できたら
    "conclusive_fail"とし、再評価せず呼び出し元(次の台本生成)へ返す。"""
    attempts: list[EditorialQualityAttemptRecord] = []
    total_api_retry = 0

    for attempt in range(1, max_eval_attempts + 1):
        outcome = common.call_qa_with_retry(
            lambda p, _wav: qa_call_fn(p), prompt, b"", max_retry=max_api_retry, sleep_fn=sleep_fn)
        total_api_retry += outcome.api_retry_count

        if outcome.parse_failed or outcome.raw_result is None:
            attempts.append(EditorialQualityAttemptRecord(
                attempt_number=attempt, outcome="inconclusive",
                reasons=["qa_unavailable_or_unparseable"], api_retry_count=outcome.api_retry_count,
            ))
            continue

        try:
            parsed = validate_editorial_quality_fields(outcome.raw_result)
        except EditorialQualityParseError as e:
            attempts.append(EditorialQualityAttemptRecord(
                attempt_number=attempt, outcome="inconclusive",
                reasons=[str(e)], api_retry_count=outcome.api_retry_count,
            ))
            continue

        classified = classify_editorial_quality(parsed)
        if classified["passed"]:
            attempts.append(EditorialQualityAttemptRecord(
                attempt_number=attempt, outcome="passed", reasons=[],
                api_retry_count=outcome.api_retry_count,
            ))
            return EditorialQualityOutcome(
                final_outcome="passed", reasons=[], attempts=attempts,
                total_api_retry_count=total_api_retry,
            )
        else:
            # 有効な形式で不合格を検出できた=確定的な不合格。再評価しない。
            attempts.append(EditorialQualityAttemptRecord(
                attempt_number=attempt, outcome="conclusive_fail", reasons=classified["reasons"],
                api_retry_count=outcome.api_retry_count,
            ))
            return EditorialQualityOutcome(
                final_outcome="conclusive_fail", reasons=classified["reasons"], attempts=attempts,
                total_api_retry_count=total_api_retry,
            )

    return EditorialQualityOutcome(
        final_outcome="inconclusive", reasons=["editorial_quality_inconclusive_after_max_attempts"],
        attempts=attempts, total_api_retry_count=total_api_retry,
    )


# ============================================================
# ブロック7: 主張強度エスカレーション(全記事共通スキーマ。A02専用語を
# プロダクションコードへハードコードしない)
# ============================================================
CLAIM_STRENGTH_ESCALATION_TAXONOMY = [
    {
        "category": "certainty_status",
        "from_label": "proposed_or_planned",
        "to_label": "decided_or_finalized",
        "from_terms": ["proposed", "planned", "under consideration", "would"],
        "to_terms": ["decided", "finalized", "confirmed policy", "has been approved"],
    },
    {
        "category": "obligation_scope",
        "from_label": "default_or_optional",
        "to_label": "mandatory",
        "from_terms": ["default", "optional", "can be turned off", "can override", "opt out"],
        "to_terms": ["mandatory", "required", "forced", "compulsory", "cannot be turned off"],
    },
    {
        "category": "coverage_scope",
        "from_label": "partial_or_limited",
        "to_label": "total",
        "from_terms": ["partial", "limited", "some accounts", "certain features"],
        "to_terms": ["total", "complete", "entire", "全面", "all accounts", "every feature"],
    },
    {
        "category": "modal_certainty",
        "from_label": "may_or_could",
        "to_label": "will",
        "from_terms": ["may", "could", "might"],
        "to_terms": ["will", "shall", "is going to", "is certain to"],
    },
    {
        "category": "quantifier_scope",
        "from_label": "some",
        "to_label": "all",
        "from_terms": ["some", "a few", "several", "part of"],
        "to_terms": ["all", "every", "entirely", "everyone"],
    },
    {
        "category": "causal_strength",
        "from_label": "concern_or_correlation",
        "to_label": "proven_causation",
        "from_terms": ["concern", "correlation", "associated with", "linked to", "may help"],
        "to_terms": ["proven", "causes", "confirmed to cause", "guarantees"],
    },
]
CLAIM_STRENGTH_TAXONOMY_VERSION = "er002-claim-strength-taxonomy-v1"


def detect_claim_strength_escalation_heuristic(facts_text: str, script_text: str) -> list[dict]:
    """ルールベースの診断専用ヒューリスティック。CLAIM_STRENGTH_ESCALATION_
    TAXONOMYの各カテゴリについて、事実側がfrom_termsの語彙で書かれている
    のに台本側にto_termsの語彙が出現する場合を検出する。

    これは診断情報としてのみ使用し、この結果が「問題なし」であることを
    理由に編集品質検品(LLM)を省略してはならない(その判断は呼び出し側の
    設計で保証する)。誤検出・見逃しがあり得る簡易実装であり、確定判定は
    常にevaluate_editorial_qualityのLLM検品(claim_strength_changed)に委ねる。"""
    facts_lower = facts_text.lower()
    script_lower = script_text.lower()
    findings = []
    for entry in CLAIM_STRENGTH_ESCALATION_TAXONOMY:
        facts_has_from = any(t in facts_lower for t in entry["from_terms"])
        facts_has_to = any(t in facts_lower for t in entry["to_terms"])
        script_has_to = any(t in script_lower for t in entry["to_terms"])
        if facts_has_from and not facts_has_to and script_has_to:
            findings.append({
                "category": entry["category"],
                "from_label": entry["from_label"],
                "to_label": entry["to_label"],
                "note": "diagnostic heuristic match only, not a confirmed detection",
            })
    return findings


# ============================================================
# ブロック8: 汎用APIリトライ(コンテンツ試行回数とは別カウント)
# ============================================================
def call_with_retry(fn: Callable[[], Any], max_retry: int, sleep_fn: Optional[Callable[[float], None]] = None):
    """引数なしの呼び出し可能オブジェクトfnを実行し、例外時はmax_retry回まで
    再試行する(API通信障害用。コンテンツ・評価の試行回数カウントとは別枠)。
    戻り値: (結果, api_retry_count, ok, last_error)"""
    last_error = None
    for attempt in range(max_retry + 1):
        try:
            return fn(), attempt, True, None
        except Exception as e:
            last_error = str(e)
            if sleep_fn:
                sleep_fn(2)
    return None, max_retry, False, last_error
