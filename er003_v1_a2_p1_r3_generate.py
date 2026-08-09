# ============================================================
# er003_v1_a2_p1_r3_generate.py
# ER-003-A2-03: A01/A02/ADD03のA2改訂(リスニング向け言語簡略化)
# ============================================================
# prompt(a2_p1_r3_prompt_template.txt)だけを差し替えて再生成する。
# 生成後、正式CEFR-A2 wordlistが存在しないため、LLMによるsemantic QA
# (a2_vocab_qa_prompt_template.txt)を補助的に実行し、語彙を
# a2_common/beyond_a2_general/proper_noun/specialist_exception/uncertain
# へ分類する。1文1数字の確認は正規表現ベースで機械的に行う。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_p1_r3_generate.py

from __future__ import annotations

import json
import os

import er003_a2_article as a2

TOPIC_IDS = ("A01", "A02", "ADD03")
PROMPT_TEMPLATE_PATH = "er003_v1_translator_briefs/a2_p1_r3_prompt_template.txt"


def run_for_topic(topic_id: str) -> dict:
    out_dir = f"er003_output/a2_p1_r3/{topic_id}"
    os.makedirs(out_dir, exist_ok=True)

    natural_source_path = f"er003_output/p1b/{topic_id}/natural_source_approved.md"
    with open(natural_source_path, encoding="utf-8") as f:
        en = f.read()
    en_sha256_before = a2.sha256_text(en)

    with open(f"{out_dir}/master_en_natural_source_approved.md", "w", encoding="utf-8") as f:
        f.write(en)

    template = a2.load_a2_prompt_template(PROMPT_TEMPLATE_PATH)
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
    section_word_counts = a2.compute_section_word_counts(raw_text)
    number_report = a2.compute_number_per_sentence_report(raw_text)
    machine_checks = a2.run_machine_checks(
        raw_text, structure, metrics, uses_web_search_tool=generator_fn.uses_web_search_tool)

    # 語彙QA(LLM semantic QA、正式wordlist不在のため補助的に使用)
    vocab_qa_text = a2.article_text_for_vocab_qa(raw_text)
    vocab_qa_prompt = a2.build_a2_vocab_qa_prompt(vocab_qa_text)
    with open(f"{out_dir}/a2_vocab_qa_prompt.txt", "w", encoding="utf-8") as f:
        f.write(vocab_qa_prompt)
    vocab_qa_fn = a2.make_a2_vocab_qa_fn(vocab_qa_prompt)
    vocab_qa_raw, vocab_qa_model, vocab_qa_response_id = vocab_qa_fn()
    vocab_qa_result = a2.parse_and_validate_a2_vocab_qa_output(vocab_qa_raw)
    with open(f"{out_dir}/a2_vocab_qa_result.json", "w", encoding="utf-8") as f:
        json.dump(vocab_qa_result, f, ensure_ascii=False, indent=2)

    heading_count = len([1 for line in raw_text.splitlines() if line.lstrip().startswith("#")])

    a2_metrics = {
        "topic_id": topic_id,
        "revision": "r3",
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
        "section_word_counts": section_word_counts,
        "number_per_sentence_report": {
            "sentences_with_numbers": number_report["sentences_with_numbers"],
            "sentences_with_multiple_numbers": number_report["sentences_with_multiple_numbers"],
            "multi_number_sentence_detail": number_report["multi_number_sentence_detail"],
        },
        "vocab_qa": {
            "beyond_a2_general_count": len(vocab_qa_result["beyond_a2_general"]),
            "beyond_a2_general": vocab_qa_result["beyond_a2_general"],
            "proper_noun_count": len(vocab_qa_result["proper_nouns"]),
            "proper_nouns": vocab_qa_result["proper_nouns"],
            "specialist_exception_count": len(vocab_qa_result["specialist_exceptions"]),
            "specialist_exceptions": vocab_qa_result["specialist_exceptions"],
            "uncertain_count": len(vocab_qa_result["uncertain"]),
            "uncertain": vocab_qa_result["uncertain"],
            "a2_common_word_count": vocab_qa_result["a2_common_word_count"],
            "method_note": vocab_qa_result["method_note"],
            "qa_model": vocab_qa_model,
            "qa_response_id": vocab_qa_response_id,
        },
    }
    with open(f"{out_dir}/a2_metrics.json", "w", encoding="utf-8") as f:
        json.dump(a2_metrics, f, ensure_ascii=False, indent=2)

    en_sha256_after = a2.sha256_text(open(natural_source_path, encoding="utf-8").read())
    source_master_unchanged = en_sha256_before == en_sha256_after

    generation_metadata = {
        "experiment_version": "ER-003-A2-03",
        "topic_id": topic_id,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "spec_status": "PROTOTYPE / UNDER_REVIEW (A2 provisional spec r3, not CURRENT_SPEC)",
        "prompt_template_path": PROMPT_TEMPLATE_PATH,
        "model": a2.A2_MODEL,
        "reasoning_effort": a2.A2_REASONING_EFFORT,
        "developer_message": a2.A2_DEVELOPER_MESSAGE,
        "api_endpoint": "responses.create",
        "api_call_count": 2,
        "auto_regeneration_count": 0,
        "web_search_tool_used": generator_fn.uses_web_search_tool,
        "response_format_used": generator_fn.response_format_used,
        "actual_response_model_field": model_id,
        "model_field_matches_expected": model_id == a2.A2_MODEL,
        "response_id": response_id,
        "vocab_qa_model": vocab_qa_model,
        "vocab_qa_response_id": vocab_qa_response_id,
        "natural_english_source_path": natural_source_path,
        "natural_english_source_sha256_before": en_sha256_before,
        "natural_english_source_sha256_after": en_sha256_after,
        "source_master_unchanged": source_master_unchanged,
        "b1_body_used_as_input": False,
        "b2_body_used_as_input": False,
        "a2_r1_body_used_as_input": False,
        "a2_r2_body_used_as_input": False,
        "machine_checks": machine_checks,
        "vocab_wordlist_status": "NOT_FOUND_IN_REPOSITORY (confirmed via search; LLM semantic QA used as substitute per ER-003-A2-03 spec section 5)",
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
        "vocab_qa_result": vocab_qa_result,
        "number_report": number_report,
    }


def run_all() -> dict:
    results = {}
    for topic_id in TOPIC_IDS:
        print(f"=== generating A2-r3 text for {topic_id} ===")
        results[topic_id] = run_for_topic(topic_id)
        m = results[topic_id]["metrics"]
        vq = m["vocab_qa"]
        print(f"  structure_status={results[topic_id]['structure']['status']}")
        print(f"  avg={m['avg_words_per_sentence']} longest={m['longest_sentence_word_count']} "
              f"words={m['total_word_count_body_only']}")
        print(f"  FS_share={m['section_word_counts']['full_story_share_of_total']}")
        print(f"  beyond_a2_general_count={vq['beyond_a2_general_count']} "
              f"proper_nouns={vq['proper_noun_count']} specialist_exceptions={vq['specialist_exception_count']} "
              f"uncertain={vq['uncertain_count']}")
        print(f"  multi_number_sentences={m['number_per_sentence_report']['sentences_with_multiple_numbers']}")
    return results


if __name__ == "__main__":
    run_all()
    print("done.")
