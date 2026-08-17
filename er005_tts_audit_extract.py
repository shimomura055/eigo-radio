# ER-005-TTS-CLEAN-COST-AUDIT-01: 既存ログからのsegment-level attempt抽出
from __future__ import annotations

import json

SEGMENT_ORDER_B1 = [
    "topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading",
    "full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line",
]
SEGMENT_ORDER_A2 = [
    "topic_intro", "japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
    "point_one_heading", "point_two_heading",
    "full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line",
]

SEGMENT_TYPE = {
    "topic_intro": "Preview",  # topic_introはPreview直前の短い導入。Previewカテゴリへ含める
    "japanese_title": "Preview",
    "preview": "Preview",
    "comment_1": "Comment", "comment_2": "Comment", "comment_3": "Comment", "comment_4": "Comment",
    "point_one_heading": "Heading", "point_two_heading": "Heading",
    "full_story_part1": "Full Story", "full_story_part2": "Full Story",
    "point_one": "Point Content", "point_two": "Point Content",
    "in_one_line": "In One Line",
}


def get_all_attempts(seg: dict) -> list[dict]:
    attempts = []
    if isinstance(seg.get("attempts_log"), list):
        attempts.extend(seg["attempts_log"])
    if isinstance(seg.get("standard_attempts_log"), list):
        attempts.extend(seg["standard_attempts_log"])
    if isinstance(seg.get("fallback_attempts_log"), list):
        attempts.extend(seg["fallback_attempts_log"])
    return attempts


def load_segments(theme: str, level: str) -> dict:
    path = f"er005_output/cost_baseline_01/{theme}/{level}/audit/tts_generation_results.json"
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    order = SEGMENT_ORDER_B1 if level == "b1b" else SEGMENT_ORDER_A2
    entries = []  # (segment_name, segment_type, attempt_count, attempts)
    for name in order:
        seg = d["segments"][name]
        attempts = get_all_attempts(seg)
        entries.append((name, SEGMENT_TYPE.get(name, "Other"), len(attempts), attempts, "main"))
    kp = d.get("key_phrases", {})
    for rank in sorted(kp.keys(), key=lambda x: int(x)):
        item = kp[rank]
        en = item.get("english", {})
        ja = item.get("japanese") or item.get("japanese_meaning") or {}
        en_attempts = get_all_attempts(en)
        ja_attempts = get_all_attempts(ja)
        entries.append((f"kp{rank}_en", "Key Phrase EN", len(en_attempts), en_attempts, "kp"))
        entries.append((f"kp{rank}_ja", "Key Phrase JA", len(ja_attempts), ja_attempts, "kp"))
    return entries


if __name__ == "__main__":
    for theme in ["akb48", "parenting"]:
        for level in ["b1b", "a2"]:
            entries = load_segments(theme, level)
            total = sum(e[2] for e in entries)
            print(f"{theme}/{level}: total_attempts={total}")
            for name, typ, count, attempts, kind in entries:
                print(f"  {name:20s} [{typ:14s}] attempts={count}")
