# ============================================================
# er002_v1_2m_freeze.py
# ER-002-v1.2M-JA: 阪神日本語マスター模倣方式の条件凍結
# ============================================================
# ER-002-v1.0(er002_v1_freeze.py)・v1.1A(er002_v1_1a_freeze.py)・
# v1.1B(er002_v1_1b_freeze.py)は変更・上書きしない。v1.2Mはルール・
# スコア・Editorial Briefによる編集工程を使わない別方式のため、独立した
# 凍結ファイルとしてここに保存する。
#
# このモジュールは実APIを一切呼び出さない(ハッシュ計算のみ)。

from __future__ import annotations

import json
from datetime import datetime, timezone

import er002_common as common
import er002_ja_master_imitation as jami

EXPERIMENT_VERSION = jami.EXPERIMENT_VERSION  # "ER-002-v1.2M-JA"
BASE_EXPERIMENT_VERSION = jami.BASE_EXPERIMENT_VERSION  # "ER-002-v1.1B"(比較対象。ルール中心工程はここで終了)


def sha256_text(text: str) -> str:
    return jami.sha256_text(text)


def sha256_json(obj) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


def _freeze_masters() -> dict:
    with open(jami.MASTERS_SHA256_PATH, encoding="utf-8") as f:
        masters_sha256 = json.load(f)
    return masters_sha256


def _freeze_generation_prompt() -> dict:
    return {
        "version": jami.PROMPT_VERSION,
        "template_sha256": sha256_text(jami.MINIMAL_JA_GENERATION_PROMPT_TEMPLATE),
        "evaluation_reasons": jami.EVALUATION_REASONS,
        "evaluation_reasons_sha256": sha256_json(jami.EVALUATION_REASONS),
        "json_shape_fallback_instruction_sha256": sha256_text(jami.MINIMAL_JSON_SHAPE_FALLBACK_INSTRUCTION),
        "note": (
            "過去6トピック一覧・過去記事本文はプロンプトへ含めない。依頼文全文からの"
            "動的抽出も行わず、評価理由は固定文言として凍結する。"
        ),
    }


def _freeze_structured_output_schema() -> dict:
    return {
        "schema": jami.JA_ARTICLE_JSON_SCHEMA,
        "sha256": sha256_json(jami.JA_ARTICLE_JSON_SCHEMA),
        "required_fields": jami.REQUIRED_ARTICLE_FIELDS,
    }


def _freeze_fact_qa() -> dict:
    return {
        "version": jami.MINIMAL_FACT_QA_PROMPT_VERSION,
        "template_sha256": sha256_text(jami.MINIMAL_FACT_QA_PROMPT_TEMPLATE),
        "required_fields": jami.MINIMAL_FACT_QA_REQUIRED_FIELDS,
        "required_fields_sha256": sha256_json(jami.MINIMAL_FACT_QA_REQUIRED_FIELDS),
        "judged_only": ["contradicts_verified_facts", "unsupported_specific_claims"],
        "never_judges": [
            "面白さ", "勢い", "アングルの良し悪し", "Pointの価値",
            "In One Lineの印象", "narrative coherence", "listener payoff", "続きを聞きたいか",
        ],
    }


def _freeze_verdict_rules() -> dict:
    rules = {
        "PASS": "明確な事実矛盾なし かつ 未確認の具体的主張なし",
        "REVIEW_REQUIRED": "確認済み事実に見当たらない具体的主張がある(明確な矛盾とまでは断定できない)",
        "FAIL": "確認済み事実と明確に矛盾する",
        "on_review_required_or_fail": "再生成しない(記録のみ)",
    }
    return {"rules": rules, "sha256": sha256_json(rules)}


def _freeze_model_config() -> dict:
    import er002_script_adapter as script_adapter
    return {
        "generation_model_ref": "er002_script_adapter.MODEL_WRITE",
        "generation_model_value": script_adapter.MODEL_WRITE,
        "fact_qa_model_ref": "er002_common.QA_MODEL_NAME",
        "fact_qa_model_value": common.QA_MODEL_NAME,
        "note": "モデル名は既存定義を参照するのみで、このファイルへ重複してハードコードしない(値は記録用の参照コピー)。temperature等は既存アダプターのデフォルトを使用し、新規パラメータを追加しない。",
    }


def _freeze_retry_rules() -> dict:
    conditions = {
        "content_generation_attempts_per_article": 1,
        "max_generation_api_retry": jami.MAX_GENERATION_API_RETRY,
        "max_generation_parse_retry": jami.MAX_GENERATION_PARSE_RETRY,
        "max_fact_qa_eval_attempts": jami.MAX_FACT_QA_EVAL_ATTEMPTS,
        "max_fact_qa_api_retry": common.MAX_QA_API_RETRY,
        "regeneration_on_content_dissatisfaction": False,
        "regeneration_on_review_required_or_fail": False,
    }
    return {"conditions": conditions, "sha256": sha256_json(conditions)}


TARGET_ARTICLES = [
    {"article_id": "A01", "topic": "World Cup semifinal"},
    {"article_id": "A02", "topic": "UK nighttime social-media setting"},
    {"article_id": "ADD01", "topic": "Tokuryu case broker"},
    {"article_id": "ADD02", "topic": "Imperial House Law reform"},
    {"article_id": "ADD03", "topic": "Strait of Hormuz 20% charge withdrawal"},
    {"article_id": "ADD04", "topic": "Akutagawa and Naoki prizes"},
    {"article_id": "ADD05", "topic": "Elder-to-elder caregiving"},
]

EXCLUDED_STAGES = [
    "editorial_angle_generation", "editorial_angle_scoring", "editorial_brief",
    "editorial_role_enum", "editorial_quality_llm_gate", "narrative_quality_auto_pass_fail",
    "multi_script_auto_selection", "content_dissatisfaction_regeneration",
    "web_search", "topic_retrieval", "fact_registry_auto_collection",
    "pdf_fact_extraction", "approved_article_fact_extraction", "tts", "audio_qa", "dynamics3",
]

CHARACTER_COUNT_POLICY = {
    "used_as_pass_fail_gate": False,
    "recorded_fields": ["total_characters", "characters_excluding_whitespace_and_markdown", "ratio_to_master"],
}


def _freeze_target_articles_and_scope() -> dict:
    return {
        "target_articles": TARGET_ARTICLES,
        "target_articles_sha256": sha256_json(TARGET_ARTICLES),
        "excluded_stages": EXCLUDED_STAGES,
        "excluded_stages_sha256": sha256_json(EXCLUDED_STAGES),
        "character_count_policy": CHARACTER_COUNT_POLICY,
    }


def _freeze_benchmark() -> dict:
    with open("er002_v1_2m_benchmarks/benchmark_source_status.json", encoding="utf-8") as f:
        source_status = json.load(f)
    with open("er002_v1_2m_benchmarks/benchmark_positioning.json", encoding="utf-8") as f:
        positioning = json.load(f)
    return {
        "source_status": source_status,
        "positioning": positioning,
    }


def build_frozen_conditions() -> dict:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "base_experiment_version": BASE_EXPERIMENT_VERSION,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "note": (
            "ER-002-v1.0・v1.1A・v1.1Bの凍結条件・コード・実行成果物は変更していない。"
            "ここにはv1.2M-JA(ルール中心編集工程を使わない最小指示型生成方式)の"
            "条件のみを記録する。"
        ),
        "masters": _freeze_masters(),
        "generation_prompt": _freeze_generation_prompt(),
        "structured_output_schema": _freeze_structured_output_schema(),
        "fact_qa": _freeze_fact_qa(),
        "verdict_rules": _freeze_verdict_rules(),
        "model_config": _freeze_model_config(),
        "retry_rules": _freeze_retry_rules(),
        "target_articles_and_scope": _freeze_target_articles_and_scope(),
        "benchmark": _freeze_benchmark(),
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
