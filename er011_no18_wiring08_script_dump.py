from __future__ import annotations

import json

OUT_DIR = "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_level(level, order, has_japanese_title):
    results = load(f"{OUT_DIR}/{level}/audit/tts_generation_results.json")
    kp = load(f"{OUT_DIR}/{level}/key_phrases/keywords_canonicalized.json")
    segs = results["segments"]
    items = []
    for name, label in order:
        if name.startswith("kp"):
            continue
        seg = segs.get(name, {})
        text = seg.get("canonical_text") or seg.get("text") or ""
        items.append({"label": label, "text": text,
                       "classification": seg.get("audio_classification"),
                       "connected_speech_info": seg.get("connected_speech_info"),
                       "reading_resolver_info_present": seg.get("reading_resolver_info") is not None})
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    kp_out = []
    for it in kp_items:
        rank = it["rank"]
        used_form = it["used_form"]
        gloss = it["japanese_gloss"]
        kp_out.append({"rank": rank, "used_form": used_form, "gloss": gloss})
    return {"items": items, "key_phrases": kp_out}


B1_ORDER = [
    ("topic_intro", "Topic Intro"),
    ("preview", "Preview"),
    ("comment_1", "Comment 1"),
    ("full_story_part1", "Full Story Part 1"),
    ("comment_2", "Comment 2"),
    ("full_story_part2", "Full Story Part 2"),
    ("comment_3", "Comment 3"),
    ("point_one_heading", "Point One (heading)"),
    ("point_one", "Point One"),
    ("point_two_heading", "Point Two (heading)"),
    ("point_two", "Point Two"),
    ("comment_4", "Comment 4"),
    ("in_one_line", "In One Line"),
]

A2_ORDER = [
    ("topic_intro", "Topic Intro"),
    ("japanese_title", "Japanese Title"),
    ("preview", "Preview"),
    ("comment_1", "Comment 1"),
    ("full_story_part1", "Full Story Part 1"),
    ("comment_2", "Comment 2"),
    ("full_story_part2", "Full Story Part 2"),
    ("comment_3", "Comment 3"),
    ("point_one_heading", "Point One (heading)"),
    ("point_one", "Point One"),
    ("point_two_heading", "Point Two (heading)"),
    ("point_two", "Point Two"),
    ("comment_4", "Comment 4"),
    ("in_one_line", "In One Line"),
]

if __name__ == "__main__":
    out = {
        "b1b": build_level("b1b", B1_ORDER, False),
        "a2": build_level("a2", A2_ORDER, True),
    }
    with open(f"{OUT_DIR}/wiring08_script_dump.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("wrote", f"{OUT_DIR}/wiring08_script_dump.json")
