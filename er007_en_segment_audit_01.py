# ============================================================
# er007_en_segment_audit_01.py
# ER-007-EN-ASR-EFFECTIVENESS-AUDIT-01 Part 3 & 8: No.1-6のEnglish TTS
# segment構造・長さ分布、および実Production ASR validation logの再解析。
# 新規TTS/ASRは呼ばない(既存tts_generation_results.jsonの再解析のみ)。
# ============================================================
import json
import re

TOPIC_DIRS = {
    "No.1 pool_benches_luna": "er006_output/pool_pilot_01/pool_benches_luna",
    "No.2 pool_subscriptions": "er006_output/pool_pilot_01/pool_subscriptions",
    "No.3 pool_startups": "er006_output/pool_pilot_01/pool_startups",
    "No.4 pool_n4_supermarket": "er006_output/pool_pilot_01/pool_n4_supermarket",
    "No.5 pool_n5_cafes": "er006_output/pool_pilot_01/pool_n5_cafes",
    "No.6 pool_n6_delivery": "er006_output/pool_pilot_01/pool_n6_delivery",
}

# B1: 英語=topic_intro, preview, comment_1-4, point_one_heading/two_heading,
#     full_story_part1/2, point_one/two, in_one_line, kp{n}_english
# A2: 英語=topic_intro, point_one_heading/two_heading, full_story_part1/2,
#     point_one/two, in_one_line, kp{n}_english (japanese_title/preview/
#     comment/meaningは日本語、前タスクで既に集計済み)
B1_EN_STATIC = {"topic_intro", "preview", "comment_1", "comment_2", "comment_3", "comment_4",
                 "point_one_heading", "point_two_heading", "full_story_part1", "full_story_part2",
                 "point_one", "point_two", "in_one_line"}
A2_EN_STATIC = {"topic_intro", "point_one_heading", "point_two_heading",
                 "full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line"}
KP_EN_PATTERN = re.compile(r"^kp\d+$")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def word_count(text):
    return len(re.findall(r"[A-Za-z][A-Za-z'-]*", text))


def bucket_words(n):
    if n <= 20:
        return "<=20"
    if n <= 40:
        return "21-40"
    if n <= 60:
        return "41-60"
    if n <= 100:
        return "61-100"
    return ">100"


def collect_en_segments(topic_label, out_dir):
    found = []
    for level_dir, level_label, static_set in (("b1b", "B1", B1_EN_STATIC), ("a2", "A2", A2_EN_STATIC)):
        path = f"{out_dir}/{level_dir}/audit/tts_generation_results.json"
        data = load_json(path)
        if data is None:
            continue
        segs = data.get("segments", {})
        kps = data.get("key_phrases", {})
        for seg_name, seg in segs.items():
            if seg_name in static_set:
                text = seg.get("canonical_text") or seg.get("text") or ""
                if text:
                    found.append((topic_label, level_label, seg_name, word_count(text), len(text), text))
        for rank, kp in kps.items():
            en = kp.get("english")
            if en:
                text = en.get("canonical_text") or ""
                if text:
                    found.append((topic_label, level_label, f"kp{rank}_english", word_count(text), len(text), text))
    return found


# ------------------------------------------------------------
# Part 8: 実Production ASR validation logの集計(status/classification別)
# ------------------------------------------------------------
def collect_attempt_classifications(topic_label, out_dir):
    """各levelの各segmentについて、最終的なstatusとattempts_logの
    classification推移を集計する(全attempt、全segment)。"""
    records = []
    for level_dir, level_label in (("b1b", "B1"), ("a2", "A2")):
        path = f"{out_dir}/{level_dir}/audit/tts_generation_results.json"
        data = load_json(path)
        if data is None:
            continue
        segs = data.get("segments", {})
        for seg_name, seg in segs.items():
            final_status = seg.get("status")
            attempt_lists = []
            if "attempts_log" in seg:
                attempt_lists.append(seg["attempts_log"])
            if "standard_attempts_log" in seg:
                attempt_lists.append(seg["standard_attempts_log"])
            if "fallback_attempts_log" in seg:
                attempt_lists.append(seg["fallback_attempts_log"])
            all_attempts = [a for lst in attempt_lists for a in lst]
            for att in all_attempts:
                cls = att.get("audio_classification")
                if cls:
                    records.append({
                        "topic": topic_label, "level": level_label, "segment": seg_name,
                        "attempt": att.get("attempt"), "classification": cls,
                        "verified": att.get("verified"), "final_status": final_status,
                    })
    return records


if __name__ == "__main__":
    print("=" * 70)
    print("Part 3: No.1-6 English segment長分布")
    print("=" * 70)
    all_segments = []
    for topic_label, out_dir in TOPIC_DIRS.items():
        segs = collect_en_segments(topic_label, out_dir)
        all_segments.extend(segs)
        print(f"{topic_label}: {len(segs)} EN segments found")

    buckets = {"<=20": 0, "21-40": 0, "41-60": 0, "61-100": 0, ">100": 0}
    for _, _, _, wc, _, _ in all_segments:
        buckets[bucket_words(wc)] += 1
    total = len(all_segments)
    print(f"\nTOTAL EN segments across No.1-6: {total}")
    for b, count in buckets.items():
        pct = 100 * count / total if total else 0
        print(f"  {b} words: {count} ({pct:.1f}%)")

    # Full Story Part1/2の代表値(長いsegmentの実例)
    print("\n代表的なlong segment(Full Story Part1/2)の実測:")
    for t, l, s, wc, cl, txt in all_segments:
        if s in ("full_story_part1", "full_story_part2"):
            print(f"  {t}/{l}/{s}: {wc} words, {cl} chars")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/en_segment_length_audit.json", "w", encoding="utf-8") as f:
        json.dump({
            "segments": [{"topic": t, "level": l, "segment": s, "word_count": wc, "char_len": cl}
                         for t, l, s, wc, cl, txt in all_segments],
            "buckets": buckets, "total": total,
        }, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print("Part 8: 実Production ASR validation logの再解析(No.1-6)")
    print("=" * 70)
    all_records = []
    for topic_label, out_dir in TOPIC_DIRS.items():
        recs = collect_attempt_classifications(topic_label, out_dir)
        all_records.extend(recs)

    from collections import Counter
    cls_counter = Counter(r["classification"] for r in all_records)
    total_attempts = len(all_records)
    print(f"\nTotal English ASR-validated attempts across No.1-6: {total_attempts}")
    for cls, count in cls_counter.most_common():
        pct = 100 * count / total_attempts if total_attempts else 0
        print(f"  {cls}: {count} ({pct:.1f}%)")

    verified_count = sum(1 for r in all_records if r["verified"])
    print(f"\nverified=True attempts: {verified_count}/{total_attempts} ({100*verified_count/total_attempts:.1f}%)")

    # segment単位でretry発生数(attempt>1が存在したsegment)を数える
    from collections import defaultdict
    seg_attempts = defaultdict(list)
    for r in all_records:
        seg_attempts[(r["topic"], r["level"], r["segment"])].append(r)
    retried_segments = sum(1 for k, v in seg_attempts.items() if len(v) > 1)
    total_segments_with_attempts = len(seg_attempts)
    print(f"\nSegments with retry (>1 attempt): {retried_segments}/{total_segments_with_attempts}")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/en_production_log_audit.json", "w", encoding="utf-8") as f:
        json.dump({
            "records": all_records, "classification_counts": dict(cls_counter),
            "total_attempts": total_attempts, "verified_count": verified_count,
            "retried_segments": retried_segments, "total_segments": total_segments_with_attempts,
        }, f, ensure_ascii=False, indent=2)
    print("\nEN_SEGMENT_AUDIT_DONE")
