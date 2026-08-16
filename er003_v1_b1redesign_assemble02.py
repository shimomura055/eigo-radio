# ============================================================
# er003_v1_b1redesign_assemble02.py
# ER-003-B1-REDESIGN-AUDIO-02: Point Cue再設計後のFull Audio再組み立て
# ============================================================
# 変更点(AUDIO-01のassembleから):
#   - "First point."/"Second point."を削除
#   - Point One/Two本文の前に、既存Notification + semantic heading
#     (Aoede)を配置(Notification専用の新規SFXは作らない)
#   - Comment 3を新しいBridge文言の音声に差し替え
#   - In One LineをCharon→Aoedeへ変更
# pause値は既存Shellで確立済みの定数のみを再利用し、新しい値は作らない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_assemble02.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_audio_03_generate as audio03
import er003_v1_b1redesign_audio_scaffold_generate as scaf

OUT_DIR = scaf.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"
SR = p9a.TARGET_SAMPLE_RATE

OUTRO_EXTRA_GAIN_LINEAR = audio03.OUTRO_EXTRA_GAIN_LINEAR
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio03.OUTRO_FURTHER_EXTRA_GAIN_LINEAR
# 既存Shellで確立済みのpause定数のみを再利用する(新規値は作らない)。
NOTIFICATION_ENTRY_PAUSE_SECONDS = 0.5   # 各Notification挿入直前(既存パターン)
NOTIFICATION_EXIT_PAUSE_SECONDS = 0.4    # 各Notification直後(既存パターン)
HEADING_TO_BODY_PAUSE_SECONDS = audio03.POINT_EXPLANATION_PAUSE_SECONDS  # 0.7秒(旧Point見出し→本文と同一用途)
AOEDE_TO_CHARON_PAUSE_SECONDS = audio03.COMMENT_EN_TO_JA_PAUSE_SECONDS
CHARON_TO_AOEDE_PAUSE_SECONDS = audio03.COMMENT_JA_TO_EN_PAUSE_SECONDS
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = audio03.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS

KP_CANONICALIZED_PATH = f"{OUT_DIR}/key_phrases/keywords_canonicalized.json"


def load_kp_items() -> list:
    with open(KP_CANONICALIZED_PATH, encoding="utf-8") as f:
        d = json.load(f)
    return sorted(d["items"], key=lambda it: it["rank"])


def load_all_sources() -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro", "topic_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    # semantic heading = Aoede(Listening Content側)なのでnarration(Charon)側ではなく
    # b1_segments側で読み込む(下記)。

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two"):
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    for name in ("comment_1", "comment_2", "comment_3", "comment_4"):
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/preview_charon.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["preview"] = mono
    # In One Line = Aoede(今回変更)
    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/in_one_line_aoede.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["in_one_line"] = mono
    # Point見出し = semantic heading(Aoede、今回新規)
    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/point_one_heading_semantic_aoede.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_one_heading"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/point_two_heading_semantic_aoede.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_two_heading"] = mono

    kp_items = load_kp_items()
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/kp{rank}_en.wav")
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{NARRATION_DIR}/kp{rank}_ja_charon.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def apply_gain_and_convert(sources: dict) -> dict:
    preview_mono = sources["b1_segments"]["preview"]
    full_story_part1_mono = sources["b1_segments"]["full_story_part1"]
    target_rms = (p9a.rms(preview_mono) + p9a.rms(full_story_part1_mono)) / 2
    gain_report = {"target_rms": round(target_rms, 5)}

    def gain_to_rms(data, target, label):
        gain = p9a.compute_gain_for_target_rms(data, target)
        gained = data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {}
    result["intro"] = gain_to_rms(sources["intro"]["samples"], target_rms, "intro")
    result["notification"] = gain_to_rms(sources["notification"]["samples"], target_rms, "notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_v2 = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    outro_v3 = outro_v2 * OUTRO_FURTHER_EXTRA_GAIN_LINEAR
    result["outro"] = outro_v3
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "rms_final": round(p9a.rms(outro_v3), 5), "peak_final": round(p9a.peak(outro_v3), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(preview_mono)
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(RMSアンカー)"}

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo, key_phrase_meaning_stereo = {}, {}
    for rank, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{rank}")
        key_phrase_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    for rank, mono in sources["key_phrase_meanings"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_ja_{rank}")
        key_phrase_meaning_stereo[rank] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo
    result["key_phrase_meanings"] = key_phrase_meaning_stereo

    b1_stereo = {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        gained = gain_to_rms(mono, target_rms, f"b1_{name}")
        b1_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    b1_stereo["preview"] = result["preview"]
    result["b1_segments"] = b1_stereo

    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for item in parts["kp_items"]:
        rank = item["rank"]
        num_key = num_names[rank - 1]
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts["key_phrase_meanings"][rank], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(parts: dict) -> list:
    key_phrase_blocks = build_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome (Charon)", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro (Charon)", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro (Charon)", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Preview (Charon)", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro (Charon)", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i}" for i in range(1, len(key_phrase_blocks) + 1))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 1 (Aoede)", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, new Bridge)", b1["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Notification 4 (Point One cue)", parts["notification"]),
        ("pause_0.4_notification_exit", p9a.silence_stereo(NOTIFICATION_EXIT_PAUSE_SECONDS)),
        ("Point One semantic heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS)),
        ("Point One (Aoede)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Notification 5 (Point Two cue)", parts["notification"]),
        ("pause_0.4_notification_exit", p9a.silence_stereo(NOTIFICATION_EXIT_PAUSE_SECONDS)),
        ("Point Two semantic heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS)),
        ("Point Two (Aoede)", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede, voice changed)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def assemble_with_timeline(parts: dict) -> dict:
    seq = build_pieces_with_timeline(parts)
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))

    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur

    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


def main():
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    print("[B1REDESIGN-ASSEMBLE02] 音源読み込み開始...")
    sources = load_all_sources()
    print("[B1REDESIGN-ASSEMBLE02] gain調整開始...")
    parts = apply_gain_and_convert(sources)
    print("[B1REDESIGN-ASSEMBLE02] assemble開始...")
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_B1B_IRAN01_v2.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report_v2.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/timeline_v2.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "article_id": "IRAN01_B1B_v2", "out_path": out_path,
        "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }
    with open(f"{OUT_DIR}/run_summary_assemble_v2.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[B1REDESIGN-ASSEMBLE02] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
