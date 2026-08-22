# -*- coding: utf-8 -*-
import json

CANDIDATES = {
    "benches": {
        "title_en": "Why Are More Cities Rethinking Public Benches?",
        "title_ja": "なぜ都市は公共ベンチを見直し始めているのか",
        "no": 1,
        "b1": {"script_dir": "er006_output/pool_pilot_01/pool_benches_luna/b1b",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_benches_b1b.mp3",
               "stopped": ["point_one", "comment_3"]},
        "a2": {"script_dir": "er006_output/pool_pilot_01/pool_benches_luna/a2",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_benches_a2.mp3",
               "stopped": ["full_story_part1"]},
    },
    "subscriptions": {
        "title_en": "Why Do Companies Make Subscriptions So Easy to Start—and Hard to Stop?",
        "title_ja": "なぜサブスクは始めるのは簡単で、やめるのは難しいのか",
        "no": 2,
        "b1": {"script_dir": "er006_output/pool_pilot_01/pool_subscriptions/b1b",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_subscriptions_b1b.mp3",
               "stopped": ["comment_2"]},
        "a2": {"script_dir": "er006_output/pool_pilot_01/pool_subscriptions/a2",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_subscriptions_a2.mp3",
               "stopped": ["full_story_part2"]},
    },
    "startups": {
        "title_en": "Why Do Some Startups Chase Growth Before Profit?",
        "title_ja": "なぜ一部のスタートアップは利益より先に成長を追うのか",
        "no": 3,
        "b1": {"script_dir": "er006_output/pool_pilot_01/pool_startups/b1b",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_startups_b1b.mp3",
               "stopped": []},
        "a2": {"script_dir": "er006_output/pool_pilot_01/pool_startups/a2",
               "audio_mp3": "er006_output/pool_pilot_01/human_review_mp3_candidates/pool_startups_a2.mp3",
               "stopped": ["full_story_part1"]},
    },
}

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

out = {}
for topic, cfg in CANDIDATES.items():
    out[topic] = {"title_en": cfg["title_en"], "title_ja": cfg["title_ja"], "no": cfg["no"], "levels": {}}
    for level in ("b1", "a2"):
        lvl_cfg = cfg[level]
        sdir = lvl_cfg["script_dir"]
        parts = load(f"{sdir}/parts.json")
        support_file = "b1_support_texts.json" if level == "b1" else "a2_support_texts.json"
        support = load(f"{sdir}/{support_file}")
        kp = load(f"{sdir}/key_phrases/keywords_canonicalized.json")
        key_phrases = [{"rank": it["rank"], "en": it["used_form"], "ja": it["japanese_gloss"]}
                       for it in sorted(kp["items"], key=lambda x: x["rank"])]
        out[topic]["levels"][level] = {
            "title": parts.get("title"),
            "preview": support.get("preview"),
            "key_phrases": key_phrases,
            "comment_1": support.get("comment_1"),
            "full_story_part1": parts.get("part1"),
            "comment_2": support.get("comment_2"),
            "full_story_part2": parts.get("part2"),
            "comment_3": support.get("comment_3"),
            "point_one_heading": parts.get("point_one_heading"),
            "point_one_body": parts.get("point_one_body"),
            "point_two_heading": parts.get("point_two_heading"),
            "point_two_body": parts.get("point_two_body"),
            "comment_4": support.get("comment_4"),
            "in_one_line": parts.get("in_one_line"),
            "stopped_segments": lvl_cfg["stopped"],
            "audio_mp3": lvl_cfg["audio_mp3"],
        }

with open("er006_output/pool_pilot_01/adoption_audit_01/review_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote er006_output/pool_pilot_01/adoption_audit_01/review_data.json")
for topic in out:
    for level in ("b1","a2"):
        d = out[topic]["levels"][level]
        missing = [k for k,v in d.items() if v is None and k not in ("stopped_segments","audio_mp3")]
        print(topic, level, "missing fields:", missing)
