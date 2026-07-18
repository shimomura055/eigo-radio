# ============================================================
# er002_v1_1b_freeze.py
# ER-002-v1.1B: 編集品質QAの事実入力契約修正(ER-002-v1.1B-I1)
# ============================================================
# ER-002-v1.1A(er002_v1_1a_freeze.py)は変更・上書きしない。v1.1Bは
# アングル生成・アングル評価・Editorial Briefスキーマ・Brief検品・
# 台本生成・モデル・再試行上限を一切変更せず、編集品質QAの
# 「入力ペイロード・プロンプト契約・応答スキーマ・応答整合性検証」のみを
# 修正した別バージョンとしてここに凍結する。
#
# 変更していない項目は、v1.1Aの凍結条件から継承ハッシュとして参照する
# (重複定義しない)。
#
# このモジュールは実APIを一切呼び出さない(ハッシュ計算のみ)。

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import er002_editorial_common as ec
import er002_v1_1a_freeze as v1_1a_freeze

EXPERIMENT_VERSION = "ER-002-v1.1B"
BASE_EXPERIMENT_VERSION = "ER-002-v1.1A"


def sha256_text(text: str) -> str:
    return ec.sha256_text(text)


def sha256_json(obj) -> str:
    return ec.sha256_json(obj)


def _freeze_editorial_quality_prompt_v1_1b() -> dict:
    return {
        "version": "er002-editorial-quality-v1.1b",
        "model": "gemini-3-flash-preview (er002_common.QA_MODEL_NAME, v1.1Aと同一)",
        "model_role": ec.EDITORIAL_QUALITY_MODEL_ROLE,
        "sha256": sha256_text(ec.EDITORIAL_QUALITY_PROMPT_TEMPLATE_V1_1B),
        "required_fields": ec.EDITORIAL_QUALITY_REQUIRED_FIELDS_V1_1B,
        "required_fields_sha256": sha256_json(ec.EDITORIAL_QUALITY_REQUIRED_FIELDS_V1_1B),
        "max_eval_attempts": ec.MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS,
        "note": (
            "v1.1A(er002-editorial-quality-v1)とは別バージョン。v1.1Aの"
            "EDITORIAL_QUALITY_PROMPT_TEMPLATE/EDITORIAL_QUALITY_REQUIRED_FIELDSは"
            "変更していない。max_eval_attemptsはv1.1Aと同一の値を維持する。"
        ),
    }


def _freeze_fact_registry_input_contract() -> dict:
    contract_bullets = [
        "VERIFIED FACT REGISTRY is the authoritative grounding source for all factual claims in the script.",
        "Editorial Brief fact IDs describe intended editorial use. They are not the complete list of facts allowed in the script.",
        "A claim must not be marked ungrounded merely because its supporting fact ID is absent from the Editorial Brief.",
        "Factual grounding and Editorial Brief alignment must be evaluated separately.",
        "A factually supported claim may still be misaligned with the Brief, but it is not ungrounded.",
    ]
    return {
        "version": "er002-quality-fact-input-contract-v1",
        "required_fields_per_fact": ["fact_id", "fact_text"],
        "full_source_article_text_included": False,
        "contract_bullets": contract_bullets,
        "contract_bullets_sha256": sha256_json(contract_bullets),
        "note": (
            "context_fact_idsは今回追加していない(ER-002-v1.1B-I1の指示どおり)。"
            "verified factsの原子化・再採番も行っていない(既存のF01..F05等の"
            "IDをそのまま使う)。"
        ),
    }


def _freeze_response_schema() -> dict:
    schema_fields = {
        "editorial_quality_required_fields_v1_1b": ec.EDITORIAL_QUALITY_REQUIRED_FIELDS_V1_1B,
        "claim_grounding_result_fields": ["claim_text", "claim_location", "verdict", "supporting_fact_ids", "rationale"],
        "claim_grounding_verdicts": list(ec.CLAIM_GROUNDING_VERDICTS),
        "brief_alignment_issue_fields": ["claim_or_passage", "issue", "rationale"],
        "grounding_status_values": list(ec.GROUNDING_STATUS_VALUES),
    }
    return {"fields": schema_fields, "sha256": sha256_json(schema_fields)}


def _freeze_consistency_rules() -> dict:
    rules = [
        "全claimがgroundedなのにfactual_grounding_statusがfail -> inconclusive",
        "factual_grounding_status=failなのに問題(ungrounded/ambiguous)となるclaimが一件もない -> inconclusive",
        "ungrounded_claimsとclaim_grounding_resultsのungrounded判定が一致しない -> inconclusive",
        "supporting_fact_idsに存在しないfact_idが含まれる -> inconclusive",
        "verdict=groundedなのにsupporting_fact_idsが空 -> inconclusive",
        "brief_alignment_status=passなのにbrief_alignment_issuesが空でない -> inconclusive",
        "brief_alignment_status=failなのにbrief_alignment_issuesもbrief_alignment=falseもない(factualとの混同疑い) -> inconclusive",
        "claim_grounding_results/brief_alignment_issuesの各要素にrationaleが欠落 -> inconclusive",
        "必須フィールド欠落(v1.1B拡張フィールド含む) -> inconclusive",
        "JSON解析不能 -> inconclusive(既存のcall_qa_with_retry/qa_unavailable_or_unparseableの扱いを維持)",
    ]
    return {
        "version": "er002-quality-consistency-rules-v1.1b",
        "rules": rules,
        "sha256": sha256_json(rules),
        "note": "inconclusiveの場合のみ、同じ台本を一度再評価する既存ルール(MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS)を維持する。",
    }


def _freeze_pass_conditions() -> dict:
    conditions = {
        "required_for_pass": [
            "factual_grounding_status == pass",
            "brief_alignment_status == pass",
            "ungrounded claim count == 0",
            "ambiguous claim count == 0",
            "既存の編集品質必須項目(EDITORIAL_QUALITY_REQUIRED_FIELDSのbool系10項目+危険フラグ)がすべて合格",
        ],
        "failure_classification_priority": [
            "factual_grounding_status != pass -> UNGROUNDED_CLAIMS_FAILURE",
            "factual_grounding_status == pass かつ brief_alignment_status != pass -> BRIEF_ALIGNMENT_FAILURE",
            "上記いずれでもない不合格 -> OTHER_EDITORIAL_QUALITY_FAILURE",
        ],
    }
    return {"conditions": conditions, "sha256": sha256_json(conditions)}


def _freeze_model_config() -> dict:
    import er002_common as common
    return {
        "qa_model_name": common.QA_MODEL_NAME,
        "max_qa_api_retry": common.MAX_QA_API_RETRY,
        "max_editorial_quality_eval_attempts": ec.MAX_EDITORIAL_QUALITY_EVAL_ATTEMPTS,
        "note": "v1.1Aから変更していない(モデル・temperature・再試行上限は据え置き)。",
    }


def _inherited_from_v1_1a() -> dict:
    """v1.1Aから変更していない項目は、ここでは再定義せずv1.1Aの凍結条件から
    継承ハッシュとして参照する(重複定義しない)。"""
    v1_1a_frozen = v1_1a_freeze.build_frozen_conditions()
    return {
        "angle_generation_prompt_sha256": v1_1a_frozen["angle_generation_prompt"]["sha256"],
        "angle_evaluation_prompt_sha256": v1_1a_frozen["angle_evaluation_prompt"]["sha256"],
        "brief_inspection_prompt_sha256": v1_1a_frozen["brief_inspection_prompt"]["sha256"],
        "script_generation_prompt_v1_1a_sha256": v1_1a_frozen["script_generation_prompt_v1_1a"]["sha256"],
        "claim_strength_taxonomy_sha256": v1_1a_frozen["claim_strength_taxonomy"]["sha256"],
        "editorial_brief_fields_sha256": sha256_json(ec.EDITORIAL_BRIEF_FIELDS),
        "angle_pass_thresholds_sha256": v1_1a_frozen["angle_evaluation_prompt"]["thresholds_sha256"],
        "retry_conditions_sha256": v1_1a_frozen["retry_conditions"]["sha256"],
        "note": (
            "この節はv1.1Aから一切変更していない項目のハッシュへの参照のみ。"
            "context_fact_idsは追加していないため、editorial_brief_fieldsは"
            "v1.1Aと同一である。"
        ),
    }


def build_frozen_conditions() -> dict:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "base_experiment_version": BASE_EXPERIMENT_VERSION,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "ER-002-v1.1Aの凍結条件・コード・実行成果物は変更していない。ここには"
            "v1.1Bで新規に変更した編集品質QAの入力ペイロード・プロンプト契約・"
            "応答スキーマ・応答整合性検証・合否条件のみを記録する。"
        ),
        "editorial_quality_prompt_v1_1b": _freeze_editorial_quality_prompt_v1_1b(),
        "fact_registry_input_contract": _freeze_fact_registry_input_contract(),
        "response_schema": _freeze_response_schema(),
        "consistency_rules": _freeze_consistency_rules(),
        "pass_conditions": _freeze_pass_conditions(),
        "model_config": _freeze_model_config(),
        "inherited_from_v1_1a": _inherited_from_v1_1a(),
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


def verify_v1_1a_untouched(v1_1a_frozen_conditions_path: str, expected_sha256: str) -> bool:
    """v1.1Aの凍結ファイルが変更されていないことを確認する(ハッシュ比較)。"""
    with open(v1_1a_frozen_conditions_path, "r", encoding="utf-8") as f:
        content = f.read()
    return hashlib.sha256(content.encode("utf-8")).hexdigest() == expected_sha256
