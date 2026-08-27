# -*- coding: utf-8 -*-
# ============================================================
# er009_pool_n5_a2_slowdown_01.py
# ============================================================
# No.5(pool_n5_cafes)のA2は既にAudio Validation Gate上クリーンだが、
# ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11の6% time-stretchが未適用
# (No.4と同じ状況)。台本は一切変更せず、A2英語7segment
# (point_one_heading/point_two_heading/full_story_part1/full_story_
# part2/point_one/point_two/in_one_line)だけを、既存の
# generate_a2_segment_with_slowdown()経由で再生成する(内容は変えない、
# 取り直しのみ)。No.4のer008_pool_n4_audio_qa_sync_01.pyと同じロジック。
from __future__ import annotations

import json

import er005_cost_logger as cl

cl.install("er006_output/pool_pilot_01/pool_n5_cafes/a2/audit/pool_n5_a2_slowdown_raw_usage_log.jsonl")

import er003_v1_n3_01_tts_generate as tg

OUT_DIR_A2 = "er006_output/pool_pilot_01/pool_n5_cafes/a2"
NARRATION_DIR = f"{OUT_DIR_A2}/narration"
RESULTS_PATH = f"{OUT_DIR_A2}/audit/tts_generation_results.json"


def run_headings(results, parts):
    for name in ("point_one_heading", "point_two_heading"):
        text = parts[name]
        tg.sc.assert_no_point_number_label(text, name)
        tts_input = tg.tts_safe_number_words_en(tg.tts_safe_en(text))
        print(f"[N5-A2-SLOWDOWN] {name} 再生成(6% slowdown経路)...")
        with cl.logging_context("pool_n5_cafes", "a2_slowdown"), cl.segment_context(name):
            r = tg.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", tg.first_words(text, 3), max_extra_chars=20,
                style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        r["canonical_text"] = text
        results["segments"][name] = r
        print(f"[N5-A2-SLOWDOWN] {name} status={r.get('status')}")


def run_bodies(results, parts):
    for name, text in (
        ("full_story_part1", parts["part1"]),
        ("full_story_part2", parts["part2"]),
        ("point_one", parts["point_one_body"]),
        ("point_two", parts["point_two_body"]),
        ("in_one_line", parts["in_one_line"]),
    ):
        if name in ("point_one", "point_two"):
            tg.sc.assert_no_point_number_label(text, name)
        sub = tg.first_words(text)
        tts_input = tg.tts_safe_news_en(text)
        print(f"[N5-A2-SLOWDOWN] {name} 再生成(6% slowdown経路)...")
        with cl.logging_context("pool_n5_cafes", "a2_slowdown"), cl.segment_context(name):
            r = tg.generate_a2_segment_with_slowdown(
                tts_input, f"{NARRATION_DIR}/{name}.wav", sub,
                style_prefix_override=tg.A2_ENGLISH_STYLE_PREFIX_SLOWER)
        r["canonical_text"] = text
        results["segments"][name] = r
        print(f"[N5-A2-SLOWDOWN] {name} status={r.get('status')}")


import sys


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    parts = tg.load_json(f"{OUT_DIR_A2}/parts.json")
    results = tg.load_json(RESULTS_PATH)

    if target in ("headings", "all"):
        run_headings(results, parts)
    if target in ("bodies", "all"):
        run_bodies(results, parts)

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    all_status = {k: v.get("status") for k, v in results["segments"].items()}
    print("[N5-A2-SLOWDOWN] segment_status:", json.dumps(all_status, ensure_ascii=False))


if __name__ == "__main__":
    main()
