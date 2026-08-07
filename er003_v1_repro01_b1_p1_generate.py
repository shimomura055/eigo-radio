# ============================================================
# er003_v1_repro01_b1_p1_generate.py
# ER-003-REPRO-01: SNS規制記事(A02) B1本文の初回プロトタイプ生成
# ============================================================
# er003_b1_article.py(A01専用、TOPIC_ID固定・テストで単一トピック運用を
# 明示的に保証している)は変更しない。同モジュール内の汎用関数
# (export_master_files/build_b1_user_message/make_b1_generator_fn/
# check_b1_structure/compute_b1_sentence_metrics/run_machine_checks)は
# いずれも引数だけで動作しモジュール定数に依存しないため、そのまま
# A02へ再利用する。パスの決定だけをこのスクリプト側でA02向けに行う
# (ER-003_PIPELINE_CROSS_CUTTING_RULESの「既存A01コードを記事固有値
# ごとコピーして増殖させない」に対応する最小限の分離)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_repro01_b1_p1_generate.py

from __future__ import annotations

import json
import os

import er003_b1_article as b1
import er003_ja_to_en_translation as er003

TOPIC_ID = "A02"
OUT_DIR = f"er003_output/b1_p1/{TOPIC_ID}"

JAPANESE_MASTER_PATH = er003.APPROVED_ARTICLE_SOURCE_PATHS[TOPIC_ID]
NATURAL_ENGLISH_SOURCE_PATH = f"er003_output/p1b/{TOPIC_ID}/natural_source_approved.md"


def load_japanese_master() -> str:
    with open(JAPANESE_MASTER_PATH, encoding="utf-8") as f:
        return f.read()


def load_natural_english_source() -> str:
    with open(NATURAL_ENGLISH_SOURCE_PATH, encoding="utf-8") as f:
        return f.read()


def run(make_generator_factory=None) -> dict:
    """make_generator_factoryを渡さない場合は実クライアントで実行する
    (実API・課金対象)。テスト・dry-runではfake clientを渡す。"""
    os.makedirs(OUT_DIR, exist_ok=True)

    ja = load_japanese_master()
    en = load_natural_english_source()
    en_sha256_before = b1.sha256_text(en)

    master_export = b1.export_master_files(OUT_DIR, japanese_master=ja, natural_english_source=en)

    template = b1.load_b1_prompt_template()
    user_message = b1.build_b1_user_message(en, template=template)
    with open(f"{OUT_DIR}/b1_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    if make_generator_factory is None:
        def make_generator_factory():
            return b1.make_b1_generator_fn(user_message)

    generator_fn = make_generator_factory()
    raw_text, model_id, response_id, search_usage, sources = generator_fn()

    with open(f"{OUT_DIR}/b1_article_raw.md", "w", encoding="utf-8") as f:
        f.write(raw_text)
    with open(f"{OUT_DIR}/b1_article_for_review.md", "w", encoding="utf-8") as f:
        f.write(raw_text)

    structure = b1.check_b1_structure(raw_text)
    metrics = b1.compute_b1_sentence_metrics(raw_text)
    machine_checks = b1.run_machine_checks(
        raw_text, structure, metrics, uses_web_search_tool=generator_fn.uses_web_search_tool)

    heading_count = len([1 for line in raw_text.splitlines() if line.lstrip().startswith("#")])

    b1_metrics = {
        "topic_id": TOPIC_ID,
        "total_word_count_including_headings": metrics["total_word_count_including_headings"],
        "total_word_count_body_only": metrics["total_word_count_body_only"],
        "total_sentence_count": metrics["total_sentence_count"],
        "avg_words_per_sentence": metrics["avg_words_per_sentence"],
        "avg_words_per_sentence_target": metrics["avg_words_per_sentence_target"],
        "avg_words_per_sentence_within_target": metrics["avg_words_per_sentence_within_target"],
        "longest_sentence_word_count": metrics["longest_sentence_word_count"],
        "max_sentence_word_count_ceiling": metrics["max_sentence_word_count_ceiling"],
        "sentences_over_24_word_count": metrics["sentences_over_24_word_count"],
        "sentences_over_24": metrics["sentences_over_24"],
        "estimated_reading_time_minutes": metrics["estimated_reading_time_minutes"],
        "heading_count": heading_count,
        "point_one_present": structure.get("point_one_heading") is not None,
        "point_two_present": structure.get("point_two_heading") is not None,
        "in_one_line_present": bool(structure.get("in_one_line_present")),
        "structure_status": structure["status"],
        "structure_reasons": structure["reasons"],
    }
    with open(f"{OUT_DIR}/b1_metrics.json", "w", encoding="utf-8") as f:
        json.dump(b1_metrics, f, ensure_ascii=False, indent=2)

    en_sha256_after = b1.sha256_text(load_natural_english_source())
    source_master_unchanged = en_sha256_before == en_sha256_after

    generation_metadata = {
        "experiment_version": "ER-003-REPRO-01",
        "topic_id": TOPIC_ID,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "model": b1.B1_MODEL,
        "reasoning_effort": b1.B1_REASONING_EFFORT,
        "developer_message": b1.B1_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "api_call_count": 1,
        "auto_regeneration_count": 0,
        "web_search_tool_used": generator_fn.uses_web_search_tool,
        "response_format_used": generator_fn.response_format_used,
        "actual_response_model_field": model_id,
        "model_field_matches_expected": model_id == b1.B1_MODEL,
        "response_id": response_id,
        "japanese_master_path": master_export["japanese_master"]["source_path"],
        "japanese_master_sha256": master_export["japanese_master"]["sha256"],
        "natural_english_source_path": master_export["natural_english_source"]["source_path"],
        "natural_english_source_sha256_before": en_sha256_before,
        "natural_english_source_sha256_after": en_sha256_after,
        "source_master_unchanged": source_master_unchanged,
        "b2_body_used_as_input": False,
        "machine_checks": machine_checks,
    }
    with open(f"{OUT_DIR}/generation_metadata.json", "w", encoding="utf-8") as f:
        json.dump(generation_metadata, f, ensure_ascii=False, indent=2)

    return {
        "raw_text": raw_text,
        "structure": structure,
        "metrics": b1_metrics,
        "machine_checks": machine_checks,
        "generation_metadata": generation_metadata,
    }


if __name__ == "__main__":
    result = run()
    print("done.")
    print(f"structure_status={result['structure']['status']}")
    print(f"machine_checks_status={result['machine_checks']['status']}")
    print(f"source_master_unchanged={result['generation_metadata']['source_master_unchanged']}")
