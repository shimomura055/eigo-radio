# ============================================================
# er002_v1_freeze.py
# ER-002-S3-P0: 実験条件の凍結(ER-002-v1.0)
# ============================================================
# B1以降の本番6記事バッチを開始する前に、比較可能性を左右する条件
# (プロンプト・演技指示・QAスキーマ・Dynamics3・語数条件・再試行条件・
# 話者割当て・A/B匿名化処理)をバージョン番号とsha256ハッシュ付きで凍結する。
#
# QAプロンプトは記事ごとの期待テキスト(NarrationPlan)に応じて内容が変わる
# ため、プロンプト文字列そのものを直接凍結対象にはできない。代わりに、
# 「どの固定フィールドを要求するか」というスキーマ契約(JSON_SCHEMA_FIELDS)
# と、再現可能な固定サンプル台本から生成したプロンプトのハッシュの両方を
# 記録する(後者は同じ入力から常に同じ文字列が生成されることの確認用)。
#
# このモジュールは実APIを一切呼び出さない(ハッシュ計算のみ)。

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import er002_ab_anonymize as ab
import er002_common as common
import er002_s3_config as s3config
import er002_script_adapter as script_adapter
import er002_topic_adapter as topic_adapter

EXPERIMENT_VERSION = "ER-002-v1.0"

# QAプロンプトのハッシュを再現可能にするための固定サンプル台本
# (実記事の内容ではない。スキーマ契約を凍結するための固定入力)
_FREEZE_SAMPLE_SCRIPT = {
    "title": "Freeze Sample Title",
    "sections": [
        {"type": "body", "paragraphs": ["Sample body sentence one.", "Sample body sentence two."]},
        {
            "type": "section",
            "heading": "Today's Freeze Sample Points",
            "subsections": [
                {"heading": "First sample point", "paragraphs": ["First point detail."]},
                {"heading": "Second sample point", "paragraphs": ["Second point detail."]},
            ],
        },
        {"type": "section", "heading": "In One Line", "paragraphs": ["Sample closing sentence."]},
    ],
}

QA_JSON_SCHEMA_FIELDS_FROZEN = [
    "assessment_status", "inconclusive_reason",
    "element_counts",
    "body_dropped", "body_dropped_evidence",
    "body_duplicated", "body_duplicated_evidence",
    "unauthorized_paraphrase", "unauthorized_paraphrase_evidence",
    "section_order_changed", "observed_section_order",
    "extra_unscripted_speech", "extra_unscripted_speech_evidence",
    "notes",
]
QA_SCHEMA_VERSION = "er002-qa-schema-v2"  # v2: assessment_status/inconclusive_reason追加(S2-P0)

AB_ANONYMIZATION_VERSION = "er002-ab-anonymization-v2"  # v2: filename_mapping方式への修正(S2-C2/S3-P0)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(obj) -> str:
    return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


def _freeze_qa_prompts() -> dict:
    plan = common.build_narration_plan(_FREEZE_SAMPLE_SCRIPT)
    embedded_prompt = common.build_embedded_qa_prompt(plan)
    grounded_prompt = common.build_grounded_qa_prompt(plan)
    return {
        "version": QA_SCHEMA_VERSION,
        "schema_fields": QA_JSON_SCHEMA_FIELDS_FROZEN,
        "schema_fields_sha256": sha256_json(QA_JSON_SCHEMA_FIELDS_FROZEN),
        "sample_embedded_prompt_sha256": sha256_text(embedded_prompt),
        "sample_grounded_prompt_sha256": sha256_text(grounded_prompt),
        "sample_input_note": (
            "ハッシュは固定サンプル台本(_FREEZE_SAMPLE_SCRIPT、実記事ではない)から"
            "生成したプロンプトに対するもの。実記事ごとにプロンプト文字列自体は"
            "変化するが、スキーマ契約(schema_fields)とテンプレート構造は固定。"
        ),
    }


def _freeze_retry_conditions() -> dict:
    conditions = {
        "max_script_attempts": common.MAX_SCRIPT_ATTEMPTS,
        "max_tts_content_attempts": common.MAX_TTS_CONTENT_ATTEMPTS,
        "max_qa_evaluation_attempts": common.MAX_QA_EVALUATION_ATTEMPTS,
        "max_tts_api_retry": common.MAX_TTS_API_RETRY,
        "max_qa_api_retry": common.MAX_QA_API_RETRY,
    }
    return {"version": "er002-retry-v1", "conditions": conditions, "sha256": sha256_json(conditions)}


def _freeze_word_count_conditions() -> dict:
    conditions = {
        "target_min": common.WORD_COUNT_TARGET_MIN,
        "target_max": common.WORD_COUNT_TARGET_MAX,
        "accept_min": common.WORD_COUNT_ACCEPT_MIN,
        "accept_max": common.WORD_COUNT_ACCEPT_MAX,
        "duration_warn_min_seconds": common.DURATION_WARN_MIN_SECONDS,
        "duration_warn_max_seconds": common.DURATION_WARN_MAX_SECONDS,
    }
    return {"version": "er002-wordcount-v1", "conditions": conditions, "sha256": sha256_json(conditions)}


def _freeze_dynamics3() -> dict:
    return {
        "version": "er002-dynamics3-v1 (ER-001B-8で確定・不変)",
        "params": common.DYNAMICS3_PARAMS,
        "peak_ceiling_db": common.PEAK_CEILING_DB,
        "loudness_match_target_lu": common.LOUDNESS_MATCH_TARGET_LU,
        "sha256": sha256_json({
            "params": common.DYNAMICS3_PARAMS,
            "peak_ceiling_db": common.PEAK_CEILING_DB,
            "loudness_match_target_lu": common.LOUDNESS_MATCH_TARGET_LU,
        }),
    }


def _freeze_voice_assignment() -> dict:
    assignment = {a["article_id"]: a["voices"] for a in s3config.flatten_s3_batches()}
    return {"version": "er002-s3-voice-assignment-v1", "assignment": assignment, "sha256": sha256_json(assignment)}


def _freeze_ab_anonymization() -> dict:
    sample_filename = ab.anonymized_filename("SAMPLE_ARTICLE", 1)
    contract = {
        "version": AB_ANONYMIZATION_VERSION,
        "filename_pattern_sample": sample_filename,
        "mapping_keyed_by": "anonymized filename (not abstract sample_N label)",
        "consistency_enforced_by": "er002_ab_anonymize.validate_ab_bundle_filename_consistency",
    }
    return {**contract, "sha256": sha256_json(contract)}


def build_frozen_conditions() -> dict:
    return {
        "experiment_version": EXPERIMENT_VERSION,
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "topic_research_prompt": {
            "version": topic_adapter.PROMPT_VERSION,
            "sha256": topic_adapter.sha256_text(topic_adapter.TOPIC_RESEARCH_PROMPT_TEMPLATE),
        },
        "script_generation_prompt": {
            "version": script_adapter.PROMPT_VERSION,
            "sha256": script_adapter.sha256_text(script_adapter.COMMON_SCRIPT_PROMPT_TEMPLATE),
        },
        "tts_common_style_prefix": {
            "version": "er002-style-prefix-v1 (care point表現修正版、ER-002-S1)",
            "sha256": common.sha256_text(common.build_style_prefix()),
        },
        "qa_prompt_and_schema": _freeze_qa_prompts(),
        "dynamics3": _freeze_dynamics3(),
        "word_count_conditions": _freeze_word_count_conditions(),
        "retry_conditions": _freeze_retry_conditions(),
        "voice_assignment": _freeze_voice_assignment(),
        "ab_anonymization": _freeze_ab_anonymization(),
    }


def save_frozen_conditions(path: str) -> dict:
    frozen = build_frozen_conditions()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(frozen, f, ensure_ascii=False, indent=2)
    return frozen


def frozen_conditions_overall_sha256() -> str:
    """ER-002-v1.0の全条件をまとめた1個のハッシュ値。frozen_at(実行のたびに
    変わるタイムスタンプ)は対象から除外し、条件そのものだけで決定的になる
    ようにしている。再実行入力バンドルのfrozen_conditions_sha256と比較して、
    ER-002-v1.0以外の条件で保存されたバンドルを拒否するために使う。"""
    frozen = build_frozen_conditions()
    stable = {k: v for k, v in frozen.items() if k != "frozen_at"}
    return sha256_json(stable)
