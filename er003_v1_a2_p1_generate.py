# ============================================================
# er003_v1_a2_p1_generate.py
# ER-003-A2-01: A01/A02/ADD03のA2暫定仕様本文をまとめて生成
# ============================================================
# er003_a2_article.py(汎用)を再利用し、記事固有の値(パスのみ)を
# このスクリプト側で解決する(ER-003_PIPELINE_CROSS_CUTTING_RULESの
# 「既存コードを記事固有値ごとコピーして増殖させない」に対応)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_p1_generate.py

from __future__ import annotations

import json
import os

import er003_a2_article as a2
import er003_ja_to_en_translation as er003

TOPIC_IDS = ("A01", "A02", "ADD03")


def run_for_topic(topic_id: str) -> dict:
    out_dir = f"er003_output/a2_p1/{topic_id}"
    os.makedirs(out_dir, exist_ok=True)

    natural_source_path = f"er003_output/p1b/{topic_id}/natural_source_approved.md"
    with open(natural_source_path, encoding="utf-8") as f:
        en = f.read()
    en_sha256_before = a2.sha256_text(en)

    with open(f"{out_dir}/master_en_natural_source_approved.md", "w", encoding="utf-8") as f:
        f.write(en)

    template = a2.load_a2_prompt_template()
    user_message = a2.build_a2_user_message(en, template=template)
    with open(f"{out_dir}/a2_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    generator_fn = a2.make_a2_generator_fn(user_message)
    raw_text, model_id, response_id, search_usage, sources = generator_fn()

    with open(f"{out_dir}/a2_article_raw.md", "w", encoding="utf-8") as f:
        f.write(raw_text)

    structure = a2.check_a2_structure(raw_text)
    metrics = a2.compute_a2_sentence_metrics(raw_text)
    heuristics = a2.compute_a2_grammar_vocab_heuristics(raw_text)
    machine_checks = a2.run_machine_checks(
        raw_text, structure, metrics, uses_web_search_tool=generator_fn.uses_web_search_tool)

    heading_count = len([1 for line in raw_text.splitlines() if line.lstrip().startswith("#")])

    a2_metrics = {
        "topic_id": topic_id,
        "total_word_count_including_headings": metrics["total_word_count_including_headings"],
        "total_word_count_body_only": metrics["total_word_count_body_only"],
        "total_sentence_count": metrics["total_sentence_count"],
        "avg_words_per_sentence": metrics["avg_words_per_sentence"],
        "avg_words_per_sentence_target": metrics["avg_words_per_sentence_target"],
        "avg_words_per_sentence_within_target": metrics["avg_words_per_sentence_within_target"],
        "longest_sentence_word_count": metrics["longest_sentence_word_count"],
        "max_sentence_word_count_ceiling": metrics["max_sentence_word_count_ceiling"],
        "sentences_over_18_word_count": metrics["sentences_over_18_word_count"],
        "sentences_over_18": metrics["sentences_over_18"],
        "estimated_reading_time_minutes": metrics["estimated_reading_time_minutes"],
        "heading_count": heading_count,
        "point_one_present": structure.get("point_one_heading") is not None,
        "point_two_present": structure.get("point_two_heading") is not None,
        "in_one_line_present": bool(structure.get("in_one_line_present")),
        "structure_status": structure["status"],
        "structure_reasons": structure["reasons"],
        "grammar_vocab_heuristics": heuristics,
    }
    with open(f"{out_dir}/a2_metrics.json", "w", encoding="utf-8") as f:
        json.dump(a2_metrics, f, ensure_ascii=False, indent=2)

    en_sha256_after = a2.sha256_text(open(natural_source_path, encoding="utf-8").read())
    source_master_unchanged = en_sha256_before == en_sha256_after

    generation_metadata = {
        "experiment_version": "ER-003-A2-01",
        "topic_id": topic_id,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "spec_status": "UNDER_REVIEW (A2 provisional spec, not CURRENT_SPEC)",
        "model": a2.A2_MODEL,
        "reasoning_effort": a2.A2_REASONING_EFFORT,
        "developer_message": a2.A2_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "api_call_count": 1,
        "auto_regeneration_count": 0,
        "web_search_tool_used": generator_fn.uses_web_search_tool,
        "response_format_used": generator_fn.response_format_used,
        "actual_response_model_field": model_id,
        "model_field_matches_expected": model_id == a2.A2_MODEL,
        "response_id": response_id,
        "natural_english_source_path": natural_source_path,
        "natural_english_source_sha256_before": en_sha256_before,
        "natural_english_source_sha256_after": en_sha256_after,
        "source_master_unchanged": source_master_unchanged,
        "b1_body_used_as_input": False,
        "b2_body_used_as_input": False,
        "machine_checks": machine_checks,
    }
    with open(f"{out_dir}/generation_metadata.json", "w", encoding="utf-8") as f:
        json.dump(generation_metadata, f, ensure_ascii=False, indent=2)

    return {
        "topic_id": topic_id,
        "raw_text": raw_text,
        "structure": structure,
        "metrics": a2_metrics,
        "machine_checks": machine_checks,
        "generation_metadata": generation_metadata,
    }


def run_all() -> dict:
    results = {}
    for topic_id in TOPIC_IDS:
        print(f"=== generating A2 text for {topic_id} ===")
        results[topic_id] = run_for_topic(topic_id)
        print(f"  structure_status={results[topic_id]['structure']['status']}")
        print(f"  machine_checks_status={results[topic_id]['machine_checks']['status']}")
        print(f"  avg_words_per_sentence={results[topic_id]['metrics']['avg_words_per_sentence']}")
        print(f"  longest_sentence_word_count={results[topic_id]['metrics']['longest_sentence_word_count']}")
    return results


if __name__ == "__main__":
    run_all()
    print("done.")
