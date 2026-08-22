# -*- coding: utf-8 -*-
import json

TARGETS = {
    ("benches", "b1"): ("er006_output/pool_pilot_01/pool_benches_pilot_02/b1b/audit/tts_generation_results.json",
                          "er006_output/pool_pilot_01/pool_benches_luna/b1b/parts.json",
                          "er006_output/pool_pilot_01/pool_benches_luna/b1b/b1_support_texts.json",
                          ["point_one", "comment_3"]),
    ("benches", "a2"): ("er006_output/pool_pilot_01/pool_benches_pilot_02/a2/audit/tts_generation_results.json",
                          "er006_output/pool_pilot_01/pool_benches_luna/a2/parts.json",
                          "er006_output/pool_pilot_01/pool_benches_luna/a2/a2_support_texts.json",
                          ["full_story_part1"]),
    ("subscriptions", "b1"): ("er006_output/pool_pilot_01/pool_subscriptions/b1b/audit/tts_generation_results.json",
                          "er006_output/pool_pilot_01/pool_subscriptions/b1b/parts.json",
                          "er006_output/pool_pilot_01/pool_subscriptions/b1b/b1_support_texts.json",
                          ["comment_2"]),
    ("subscriptions", "a2"): ("er006_output/pool_pilot_01/pool_subscriptions/a2/audit/tts_generation_results.json",
                          "er006_output/pool_pilot_01/pool_subscriptions/a2/parts.json",
                          "er006_output/pool_pilot_01/pool_subscriptions/a2/a2_support_texts.json",
                          ["full_story_part2"]),
    ("startups", "a2"): ("er006_output/pool_pilot_01/pool_startups/a2/audit/tts_generation_results.json",
                          "er006_output/pool_pilot_01/pool_startups/a2/parts.json",
                          "er006_output/pool_pilot_01/pool_startups/a2/a2_support_texts.json",
                          ["full_story_part1"]),
}

for (topic, level), (ttsfile, partsfile, supportfile, segnames) in TARGETS.items():
    d = json.load(open(ttsfile, encoding="utf-8"))
    for seg in segnames:
        entry = d["segments"][seg]
        print(f"=== {topic}/{level}/{seg} ===")
        print("top-level status:", entry.get("status"), "| reason:", entry.get("reason"))
        log = entry.get("attempts_log") or entry.get("standard_attempts_log") or []
        if log:
            last = log[-1]
            print("last attempt:", {k: v for k, v in last.items() if k not in ("trim_info",)})
        print()
