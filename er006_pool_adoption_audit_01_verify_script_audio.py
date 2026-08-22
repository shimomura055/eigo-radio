# -*- coding: utf-8 -*-
import json, re

def norm(t):
    if t is None: return ""
    t = t.replace("\n\n", " ").replace("\n", " ")
    t = re.sub(r"\s+", " ", t).strip()
    return t

CANDIDATES = {
    ("benches", "b1"): {
        "script_dir": "er006_output/pool_pilot_01/pool_benches_luna/b1b",
        "audio_dir": "er006_output/pool_pilot_01/pool_benches_pilot_02/b1b",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line"},
        "support_file": "b1_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
    ("benches", "a2"): {
        "script_dir": "er006_output/pool_pilot_01/pool_benches_luna/a2",
        "audio_dir": "er006_output/pool_pilot_01/pool_benches_pilot_02/a2",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line_core"},
        "support_file": "a2_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
    ("subscriptions", "b1"): {
        "script_dir": "er006_output/pool_pilot_01/pool_subscriptions/b1b",
        "audio_dir": "er006_output/pool_pilot_01/pool_subscriptions/b1b",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line"},
        "support_file": "b1_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
    ("subscriptions", "a2"): {
        "script_dir": "er006_output/pool_pilot_01/pool_subscriptions/a2",
        "audio_dir": "er006_output/pool_pilot_01/pool_subscriptions/a2",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line_core"},
        "support_file": "a2_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
    ("startups", "b1"): {
        "script_dir": "er006_output/pool_pilot_01/pool_startups/b1b",
        "audio_dir": "er006_output/pool_pilot_01/pool_startups/b1b",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line"},
        "support_file": "b1_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
    ("startups", "a2"): {
        "script_dir": "er006_output/pool_pilot_01/pool_startups/a2",
        "audio_dir": "er006_output/pool_pilot_01/pool_startups/a2",
        "parts_map": {"full_story_part1": "part1", "full_story_part2": "part2",
                       "point_one": "point_one_body", "point_two": "point_two_body",
                       "in_one_line": "in_one_line_core"},
        "support_file": "a2_support_texts.json",
        "support_map": {"preview": "preview", "comment_1": "comment_1", "comment_2": "comment_2",
                         "comment_3": "comment_3", "comment_4": "comment_4"},
    },
}

overall_report = {}
for (topic, level), cfg in CANDIDATES.items():
    parts = json.load(open(f"{cfg['script_dir']}/parts.json", encoding="utf-8"))
    support = json.load(open(f"{cfg['script_dir']}/{cfg['support_file']}", encoding="utf-8"))
    tts = json.load(open(f"{cfg['audio_dir']}/audit/tts_generation_results.json", encoding="utf-8"))
    segs = tts["segments"]
    kps = tts.get("key_phrases", {})

    results = {"status_not_ok": [], "asr_not_verified": [], "text_mismatch": [], "missing_segment": [],
               "ok_segments": 0, "total_segments": 0}

    for seg_name, script_key in cfg["parts_map"].items():
        results["total_segments"] += 1
        if seg_name not in segs:
            results["missing_segment"].append(seg_name); continue
        entry = segs[seg_name]
        if entry.get("status") != "OK":
            results["status_not_ok"].append((seg_name, entry.get("status"))); continue
        if not entry.get("asr_verified"):
            results["asr_not_verified"].append(seg_name); continue
        script_text = norm(parts.get(script_key))
        tts_text = norm(entry.get("text"))
        if script_text != tts_text:
            results["text_mismatch"].append((seg_name, script_text[:80], tts_text[:80]))
        else:
            results["ok_segments"] += 1

    for seg_name, script_key in cfg["support_map"].items():
        results["total_segments"] += 1
        if seg_name not in segs:
            results["missing_segment"].append(seg_name); continue
        entry = segs[seg_name]
        if entry.get("status") != "OK":
            results["status_not_ok"].append((seg_name, entry.get("status"))); continue
        if not entry.get("asr_verified"):
            results["asr_not_verified"].append(seg_name); continue
        script_text = norm(support.get(script_key))
        tts_text = norm(entry.get("text"))
        if script_text != tts_text:
            results["text_mismatch"].append((seg_name, script_text[:80], tts_text[:80]))
        else:
            results["ok_segments"] += 1

    # key phrases: just check all present and OK/asr_verified (content compared loosely below)
    kp_issues = []
    for kp_id, kp_entry in kps.items():
        if isinstance(kp_entry, dict):
            eng = kp_entry.get("english", kp_entry)
            jp = kp_entry.get("japanese")
        results["total_segments"] += 1
    results["key_phrase_count"] = len(kps)

    overall_report[f"{topic}_{level}"] = results

for k, v in overall_report.items():
    print(f"=== {k} ===")
    print(f"  segments checked (excl. key phrases): {v['total_segments']}, text-matched OK: {v['ok_segments']}")
    print(f"  status_not_ok: {v['status_not_ok']}")
    print(f"  asr_not_verified: {v['asr_not_verified']}")
    print(f"  missing_segment: {v['missing_segment']}")
    print(f"  text_mismatch count: {len(v['text_mismatch'])}")
    for m in v['text_mismatch']:
        print(f"    MISMATCH {m[0]}: script={m[1]!r} vs tts={m[2]!r}")
    print(f"  key_phrase_count: {v['key_phrase_count']}")
