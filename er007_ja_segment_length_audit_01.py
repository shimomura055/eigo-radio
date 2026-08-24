# ============================================================
# er007_ja_segment_length_audit_01.py
# ER-007-EVIDENCE-WORDCOUNT-JA-ASR-EFFECTIVENESS-AUDIT-01 Part B-3:
# No.1-6 Production音声の日本語segment長分布を集計する(新規TTSなし、
# 既存tts_generation_results.jsonの再解析のみ)。
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

# B1: 日本語はKey Phrase glossのみ(kp{rank}_ja_charon)。他は全て英語。
# A2: 日本語はjapanese_title/preview/comment_1-4/meaning_{i}(Key Phrase gloss)。
B1_JA_SEGMENT_PATTERN = re.compile(r"^kp\d+_ja")  # kp{rank}_ja_charonまたはkp{rank}_japanese等のkey表記ゆれに対応
A2_JA_SEGMENT_NAMES_STATIC = {"japanese_title", "preview", "comment_1", "comment_2", "comment_3", "comment_4"}
A2_JA_SEGMENT_PATTERN = re.compile(r"^meaning_\d+$")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def bucket(n):
    if n <= 30:
        return "<=30"
    if n <= 60:
        return "31-60"
    if n <= 90:
        return "61-90"
    if n <= 120:
        return "91-120"
    return ">120"


def collect_ja_segments(topic_label, out_dir):
    found = []  # (topic, level, seg_name, char_len, canonical_text)
    for level_dir, level_label in (("b1b", "B1"), ("a2", "A2")):
        path = f"{out_dir}/{level_dir}/audit/tts_generation_results.json"
        data = load_json(path)
        if data is None:
            continue
        segs = data.get("segments", {})
        kps = data.get("key_phrases", {})

        if level_label == "B1":
            for seg_name, seg in segs.items():
                if B1_JA_SEGMENT_PATTERN.match(seg_name):
                    text = seg.get("canonical_text") or seg.get("text") or ""
                    found.append((topic_label, level_label, seg_name, len(text), text))
            for rank, kp in kps.items():
                ja = kp.get("japanese")
                if ja:
                    text = ja.get("canonical_text") or ""
                    if text:
                        found.append((topic_label, level_label, f"kp{rank}_ja_charon", len(text), text))
        else:  # A2
            for seg_name, seg in segs.items():
                if seg_name in A2_JA_SEGMENT_NAMES_STATIC:
                    text = seg.get("canonical_text") or seg.get("text") or ""
                    found.append((topic_label, level_label, seg_name, len(text), text))
            for rank, kp in kps.items():
                ja = kp.get("japanese_meaning") or kp.get("japanese")
                if ja:
                    text = ja.get("canonical_text") or ""
                    if text:
                        found.append((topic_label, level_label, f"meaning_kp{rank}", len(text), text))
    return found


if __name__ == "__main__":
    all_segments = []
    for topic_label, out_dir in TOPIC_DIRS.items():
        segs = collect_ja_segments(topic_label, out_dir)
        all_segments.extend(segs)
        print(f"{topic_label}: {len(segs)} JA segments found")

    buckets = {"<=30": 0, "31-60": 0, "61-90": 0, "91-120": 0, ">120": 0}
    for _, _, _, n, _ in all_segments:
        buckets[bucket(n)] += 1

    total = len(all_segments)
    print(f"\nTOTAL JA segments across No.1-6: {total}")
    for b, count in buckets.items():
        pct = 100 * count / total if total else 0
        print(f"  {b}: {count} ({pct:.1f}%)")

    short_pct = 100 * buckets["<=30"] / total if total else 0
    long_pct = 100 - short_pct
    print(f"\n<=30文字(厳密PHONETIC_MATCH対象になり得る): {buckets['<=30']}/{total} ({short_pct:.1f}%)")
    print(f">30文字(prefix substring+length onlyで、phonetic fallbackは事実上no-op): "
          f"{total - buckets['<=30']}/{total} ({long_pct:.1f}%)")

    with open("er006_output/pool_pilot_01/evidence_density_ab_01/ja_segment_length_audit.json", "w", encoding="utf-8") as f:
        json.dump({
            "segments": [{"topic": t, "level": l, "segment": s, "char_len": n, "text": txt}
                         for t, l, s, n, txt in all_segments],
            "buckets": buckets, "total": total,
        }, f, ensure_ascii=False, indent=2)
    print("\nJA_SEGMENT_LENGTH_AUDIT_DONE")
