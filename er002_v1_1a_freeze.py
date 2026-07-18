# ============================================================
# er002_v1_1a_freeze.py
# ER-002-v1.1A: 固定記事用編集工程の条件凍結
# ============================================================
# ER-002-v1.0(er002_v1_freeze.py)は変更・上書きしない。v1.1Aは比較実験
# として別ファイルに保存する。v1.0のトピック取得・台本生成条件等は
# そのまま参照し(重複定義しない)、v1.1Aで新規に追加した要素だけを
# ここで凍結する。
#
# このモジュールは実APIを一切呼び出さない(ハッシュ計算のみ)。

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import er002_editorial_angle_adapter as angle_adapter
import er002_editorial_common as ec
import er002_script_adapter as script_adapter
import er002_v1_freeze as v1_freeze

EXPERIMENT_VERSION = "ER-002-v1.1A"
BASE_EXPERIMENT_VERSION = "ER-002-v1.0"  # 比較対象。v1.0の凍結条件はv1_freeze側で管理


def sha256_text(text: str) -> str:
    return ec.sha256_text(text)


def sha256_json(obj) -> str:
    return ec.sha256_json(obj)


def _freeze_angle_generation_prompt() -> dict:
    return {
        "version": angle_adapter.PROMPT_VERSION,
        "model": angle_adapter.MODEL_NAME,
        "model_role": angle_adapter.MODEL_ROLE,
        "sha256": sha256_text(angle_adapter.ANGLE_GENERATION_PROMPT_TEMPLATE),
    }


def _freeze_angle_evaluation_prompt() -> dict:
    return {
        "version": "er002-angle-evaluation-v1",
        "model": "gemini-3-flash-preview (er002_common.QA_MODEL_NAME)",
        "model_role": ec.ANGLE_EVALUATION_MODEL_ROLE,
        "sha256": sha256_text(ec.ANGLE_EVALUATION_PROMPT_TEMPLATE),
        "scoring_fields": ec.ANGLE_SCORING_FIELDS,
        "pass_thresholds": {**ec.ANGLE_PROVISIONAL_PASS_THRESHOLDS, "total_score_min": ec.ANGLE_TOTAL_SCORE_MIN},
        "rank_tiebreak_order": ec.ANGLE_RANK_TIEBREAK_ORDER,
        "thresholds_sha256": sha256_json({
            **ec.ANGLE_PROVISIONAL_PASS_THRESHOLDS, "total_score_min": ec.ANGLE_TOTAL_SCORE_MIN,
            "tiebreak": ec.ANGLE_RANK_TIEBREAK_ORDER,
        }),
    }


def _freeze_brief_inspection_prompt() -> dict:
    return {
        "version": "er002-brief-inspection-v1",
        "model": "gemini-3-flash-preview (er002_common.QA_MODEL_NAME)",
        "model_role": ec.BRIEF_INSPECTION_MODEL_ROLE,
        "sha256": sha256_text(ec.BRIEF_INSPECTION_PROMPT_TEMPLATE),
        "brief_fields": ec.EDITORIAL_BRIEF_FIELDS,
        "brief_fields_sha256": sha256_json(ec.EDITORIAL_BRIEF_FIELDS),
    }


def _freeze_script_generation_prompt_v1_1a() -> dict:
    return {
        "version": script_adapter.PROMPT_VERSION_V1_1A,
        "model": script_adapter.MODEL_WRITE,
        "model_role": ec.SCRIPT_GENERATION_MODEL_ROLE,
        "sha256": sha256_text(script_adapter.COMMON_SCRIPT_PROMPT_TEMPLATE_V1_1A),
        "note": "v1(COMMON_SCRIPT_PROMPT_TEMPLATE, ER-002-v1.0)とは別バージョン。v1は変更していない。",
    }


def _freeze_editorial_quality_prompt() -> dict:
    return {
        "version": "er002-editorial-quality-v1",
        "model": "gemini-3-flash-preview (er002_common.QA_MODEL_NAME)",
        "model_role": ec.EDITORIAL_QUALITY_MODEL_ROLE,
        "sha256": sha256_text(ec.EDITORIAL_QUALITY_PROMPT_TEMPLATE),
        "required_fields": ec.EDITORIAL_QUALITY_REQUIRED_FIELDS,
        "required_fields_sha256": sha256_json(ec.EDITORIAL_QUALITY_REQUIRED_FIELDS),
        "max_eval_attempts": ec.MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS,
    }


def _freeze_claim_strength_taxonomy() -> dict:
    return {
        "version": ec.CLAIM_STRENGTH_TAXONOMY_VERSION,
        "taxonomy": ec.CLAIM_STRENGTH_ESCALATION_TAXONOMY,
        "sha256": sha256_json(ec.CLAIM_STRENGTH_ESCALATION_TAXONOMY),
        "note": (
            "全記事共通のスキーマ(分類taxonomy)。A02固有の禁止語をプロダクション"
            "コードへハードコードしていない。実際の検出はeditorial quality "
            "check(LLM)のclaim_strength_changedフィールドが担い、"
            "detect_claim_strength_escalation_heuristicは診断専用の補助。"
        ),
    }


def _freeze_schemas() -> dict:
    schema_fields = {
        "editorial_angle_candidate": [
            "angle_id", "article_id", "listener_relevance", "central_tension_or_question",
            "concrete_opening", "opening_mode", "opening_fact_ids", "hypothetical_disclosure_required",
            "non_obvious_takeaway", "point_one_editorial_role", "point_one_core_claim",
            "point_one_fact_ids", "point_two_editorial_role", "point_two_core_claim",
            "point_two_fact_ids", "listener_payoff", "in_one_line_target", "fact_support_map",
            "unsupported_assumptions", "generated_at",
        ],
        "editorial_role_vocab": ec.EDITORIAL_ROLE_VOCAB,
        "opening_modes": ec.OPENING_MODES,
        "editorial_brief_fields": ec.EDITORIAL_BRIEF_FIELDS,
        "editorial_quality_required_fields": ec.EDITORIAL_QUALITY_REQUIRED_FIELDS,
    }
    return {"fields": schema_fields, "sha256": sha256_json(schema_fields)}


def _freeze_retry_conditions() -> dict:
    import er002_editorial_runner as runner
    conditions = {
        "max_angle_content_attempts": runner.MAX_ANGLE_CONTENT_ATTEMPTS,
        "max_angle_generation_api_retry": runner.MAX_ANGLE_GENERATION_API_RETRY,
        "max_angle_evaluation_api_retry": runner.MAX_ANGLE_EVALUATION_API_RETRY,
        "max_script_content_attempts": runner.MAX_SCRIPT_CONTENT_ATTEMPTS,
        "max_editorial_quality_eval_attempts": ec.MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS,
    }
    return {"version": "er002-v1.1a-retry-v1", "conditions": conditions, "sha256": sha256_json(conditions)}


def build_frozen_conditions() -> dict:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "base_experiment_version": BASE_EXPERIMENT_VERSION,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "ER-002-v1.0の凍結条件(トピック取得・台本生成v1・TTS演技指示・QA/"
            "Dynamics3/語数/再試行/話者割当/A/B匿名化)は変更していない。ここには"
            "v1.1Aで新規追加した編集アングル工程の条件のみを記録する。"
        ),
        "angle_generation_prompt": _freeze_angle_generation_prompt(),
        "angle_evaluation_prompt": _freeze_angle_evaluation_prompt(),
        "brief_inspection_prompt": _freeze_brief_inspection_prompt(),
        "script_generation_prompt_v1_1a": _freeze_script_generation_prompt_v1_1a(),
        "editorial_quality_prompt": _freeze_editorial_quality_prompt(),
        "claim_strength_taxonomy": _freeze_claim_strength_taxonomy(),
        "schemas": _freeze_schemas(),
        "retry_conditions": _freeze_retry_conditions(),
    }


def save_frozen_conditions(path: str) -> dict:
    frozen = build_frozen_conditions()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(frozen, f, ensure_ascii=False, indent=2)
    return frozen


def frozen_conditions_overall_sha256() -> str:
    frozen = build_frozen_conditions()
    stable = {k: v for k, v in frozen.items() if k != "frozen_at"}
    return sha256_json(stable)


def verify_v1_0_untouched(v1_0_frozen_conditions_path: str, expected_sha256: str) -> bool:
    """v1.0の凍結ファイルが変更されていないことを確認する(ハッシュ比較)。"""
    with open(v1_0_frozen_conditions_path, "r", encoding="utf-8") as f:
        content = f.read()
    return hashlib.sha256(content.encode("utf-8")).hexdigest() == expected_sha256
