# ============================================================
# er003_v1_b1_p2_generate.py
# ER-003-B1-P2: A01 B1 Key Words選定(Part A) + Listening Preview 3案(Part B)
# ============================================================
# Part Aが不合格(FAIL/TECHNICAL_GENERATION_FAILED)の場合、Part Bは
# 実行しない(勝手に別方式へ切り替えず停止して報告する)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p2_generate.py

from __future__ import annotations

import json
import os

import er003_b1_p2_keywords as bk
import er003_b1_p2_preview as bp
import er003_natural_source as natural_source

OUT_DIR = "er003_output/b1_p2/A01"
sha256_text = natural_source.sha256_text


def run_part_a(make_selector_factory=None) -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)

    b1_article = bk.load_b1_article()
    template = bk.load_prompt_template()
    user_message = bk.build_user_message(b1_article, template=template)
    with open(f"{OUT_DIR}/keywords_selector_prompt.txt", "w", encoding="utf-8") as f:
        f.write(user_message)

    if make_selector_factory is None:
        def make_selector_factory():
            return bk.make_selector_fn(user_message)

    parsed, status, attempts, model_id, response_id = bk.run_selection_gate(make_selector_factory, b1_article)

    last_attempt = attempts[-1] if attempts else None
    raw_text = last_attempt.get("raw_text") if last_attempt else None
    if raw_text:
        with open(f"{OUT_DIR}/keywords_selector_raw.md", "w", encoding="utf-8") as f:
            f.write(raw_text)

    runtime_metadata = {
        "article_id": bk.ARTICLE_ID,
        "strategy_id": bk.STRATEGY_ID,
        "source_level": bk.SOURCE_LEVEL,
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "model": bk.SELECTOR_MODEL,
        "reasoning_effort": bk.SELECTOR_REASONING_EFFORT,
        "developer_message": bk.SELECTOR_DEVELOPER_MESSAGE,
        "b1_article_path": bk.B1_ARTICLE_PATH,
        "b1_article_sha256": sha256_text(b1_article),
        "max_attempts": bk.MAX_SELECTOR_ATTEMPTS,
        "api_call_count": len(attempts),
        "auto_regeneration_count": 0,
        "final_status": status,
        "model_id": model_id,
        "response_id": response_id,
        "attempts_detail": [
            {k: v for k, v in a.items() if k != "raw_text"} for a in attempts
        ],
    }
    with open(f"{OUT_DIR}/keywords_runtime_metadata.json", "w", encoding="utf-8") as f:
        json.dump(runtime_metadata, f, ensure_ascii=False, indent=2)

    result = {"status": status, "parsed": parsed, "runtime_metadata": runtime_metadata}

    if status != "KEY_WORDS_STRUCTURE_PASS":
        return result

    selected_json = bk.build_selected_keywords_json(parsed)
    with open(f"{OUT_DIR}/keywords_selected.json", "w", encoding="utf-8") as f:
        json.dump(selected_json, f, ensure_ascii=False, indent=2)

    reading_copy = bk.build_selected_keywords_reading_copy(selected_json)
    with open(f"{OUT_DIR}/keywords_selected_for_review.md", "w", encoding="utf-8") as f:
        f.write(reading_copy)

    result["selected_json"] = selected_json
    return result


def run_part_b(selected_json: dict, make_preview_factory=None) -> dict:
    b1_article = bk.load_b1_article()
    template = bp.load_prompt_template()
    user_message = bp.build_preview_user_message(selected_json, b1_article, template=template)
    with open(f"{OUT_DIR}/listening_preview_prompt.md", "w", encoding="utf-8") as f:
        f.write(user_message)

    if make_preview_factory is None:
        def make_preview_factory():
            return bp.make_preview_fn(user_message)

    preview_fn = make_preview_factory()
    raw_text, model_id, response_id = preview_fn()

    with open(f"{OUT_DIR}/listening_preview_raw.md", "w", encoding="utf-8") as f:
        f.write(raw_text)

    parsed = bp.parse_preview_json(raw_text)
    selected_ranks = [item["rank"] for item in selected_json["items"]]
    machine_checks = bp.run_preview_machine_checks(parsed, selected_ranks, b1_article)

    candidates_md = bp.build_candidates_markdown(parsed)
    with open(f"{OUT_DIR}/listening_preview_candidates.md", "w", encoding="utf-8") as f:
        f.write(candidates_md)

    metrics = {
        "pattern_count": machine_checks["pattern_count"],
        "pattern_ids_present": machine_checks["pattern_ids_present"],
        "per_pattern_sentence_count": {
            pid: r["checks"]["sentence_count"] for pid, r in machine_checks["per_pattern"].items()
        },
        "per_pattern_char_count": {
            p["pattern_id"]: len(p["text"]) for p in parsed["patterns"]
        },
        "machine_checks_status": machine_checks["status"],
    }
    with open(f"{OUT_DIR}/listening_preview_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    metadata = {
        "record_status": "PROTOTYPE",
        "approval_status": "NOT_APPROVED",
        "model": bp.PREVIEW_MODEL,
        "reasoning_effort": bp.PREVIEW_REASONING_EFFORT,
        "developer_message": bp.PREVIEW_DEVELOPER_MESSAGE,
        "api_call_count": 1,
        "auto_regeneration_count": 0,
        "web_search_tool_used": preview_fn.uses_web_search_tool,
        "model_id": model_id,
        "model_field_matches_expected": model_id == bp.PREVIEW_MODEL,
        "response_id": response_id,
        "machine_checks": machine_checks,
    }
    with open(f"{OUT_DIR}/listening_preview_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return {"parsed": parsed, "machine_checks": machine_checks, "metadata": metadata}


if __name__ == "__main__":
    part_a = run_part_a()
    print(f"Part A status: {part_a['status']}")
    if part_a["status"] != "KEY_WORDS_STRUCTURE_PASS":
        print("Part A did not pass. Stopping before Part B (per spec, no auto-fallback).")
    else:
        for item in part_a["selected_json"]["items"]:
            print(f"  rank {item['rank']}: {item['canonical_english']!r}")
        part_b = run_part_b(part_a["selected_json"])
        print(f"Part B machine checks status: {part_b['machine_checks']['status']}")
