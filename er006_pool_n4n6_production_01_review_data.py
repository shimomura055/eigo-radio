# -*- coding: utf-8 -*-
import json

CONFIG = {
    "n4_supermarket": {
        "title_en": "The Supermarket Shuffle: Why Shelves Keep Moving",
        "title_ja": "スーパーの商品棚は、なぜ何度も場所が変わるのか",
        "no": 4,
        "b1": {"dir": "er006_output/pool_pilot_01/pool_n4_supermarket/b1b", "stopped": []},
        "a2": {"dir": "er006_output/pool_pilot_01/pool_n4_supermarket/a2", "stopped": ["comment_2"]},
    },
    "n5_cafes": {
        "title_en": "Cafes Are Rethinking the All-Day Customer",
        "title_ja": "カフェは「一日中居る客」をどう考え始めているのか",
        "no": 5,
        "b1": {"dir": "er006_output/pool_pilot_01/pool_n5_cafes/b1b", "stopped": ["full_story_part1", "full_story_part2"]},
        "a2": {"dir": "er006_output/pool_pilot_01/pool_n5_cafes/a2", "stopped": []},
    },
    "n6_delivery": {
        "title_en": "The Strange Pull of Delivery Tracking",
        "title_ja": "配送状況を何度も確認したくなる不思議",
        "no": 6,
        "b1": {"dir": "er006_output/pool_pilot_01/pool_n6_delivery/b1b", "stopped": ["full_story_part1"]},
        "a2": {"dir": "er006_output/pool_pilot_01/pool_n6_delivery/a2", "stopped": ["full_story_part1", "point_one"]},
    },
}

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

out = {}
for key, cfg in CONFIG.items():
    out[key] = {"title_en": cfg["title_en"], "title_ja": cfg["title_ja"], "no": cfg["no"], "levels": {}}
    for level in ("b1", "a2"):
        lvl_cfg = cfg[level]
        sdir = lvl_cfg["dir"]
        parts = load(f"{sdir}/parts.json")
        support_file = "b1_support_texts.json" if level == "b1" else "a2_support_texts.json"
        support = load(f"{sdir}/{support_file}")
        kp = load(f"{sdir}/key_phrases/keywords_canonicalized.json")
        key_phrases = [{"rank": it["rank"], "en": it["used_form"], "ja": it["japanese_gloss"]}
                       for it in sorted(kp["items"], key=lambda x: x["rank"])]
        out[key]["levels"][level] = {
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
            "wav_path": f"{sdir}/assembled/" + ("English_Your_Way_B1B_POOL_" if level=="b1" else "English_Your_Way_A2_POOL_") + key.upper() + ".wav",
        }

with open("er006_output/pool_pilot_01/adoption_audit_01/review_data_n4n6.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote review_data_n4n6.json")
import glob
for key in out:
    for level in ("b1","a2"):
        p = out[key]["levels"][level]["wav_path"]
        print(level, p, "exists" if __import__("os").path.exists(p) else "MISSING")
