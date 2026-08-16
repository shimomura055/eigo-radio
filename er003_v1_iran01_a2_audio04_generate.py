# ============================================================
# er003_v1_iran01_a2_audio04_generate.py
# ER-003-A2-COMMENT4-INONELINE-FIX-01: A2 Comment 4文言修正の再組み立て
# ============================================================
# v3(Point One/Two semantic heading追加)から変更するのはComment 4の
# 音声のみ。「一文で確認しましょう」(実際のIn One Lineは2文のため
# 内容と不一致)を「まとめて確認しましょう」へ差し替えた新TTS
# (er003_v1_a2_comment4_fix_01_generate.pyで生成済み、
# narration/comment_4.wavを上書き)を再読み込みして組み立てるのみで、
# timeline構成・pause・その他segmentはv3から一切変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_a2_audio04_generate.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2gen

ARTICLE_ID = "IRAN01_A2_v4"
CONFIG = dict(a2gen.CONFIG, article_id=ARTICLE_ID)
OUT_DIR = a2gen.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"
SR = c.SR

POINT_NOTIFICATION_MP3_PATH = "C:/Users/tensh/eigo-radio/notification/universfield-new-notification-07-210334.mp3"

# 既存Shellで確立済みのpause定数のみ再利用(新規値は作らない)。
NOTIFICATION_ENTRY_PAUSE_SECONDS = 0.5
HEADING_TO_BODY_PAUSE_SECONDS = c.POINT_EXPLANATION_PAUSE_SECONDS  # 0.7秒、A2既存のPoint explanation用値を再利用


def load_all_sources_local(config: dict) -> dict:
    base = a2gen.load_all_sources_local(config)
    base["point_notification"] = p9a.load_and_resample_to_target(POINT_NOTIFICATION_MP3_PATH)

    for name in ("point_one_heading", "point_two_heading"):
        path = f"{NARRATION_DIR}/{name}.wav"
        assert os.path.exists(path), f"heading音声が見つかりません: {path}"
        mono, sr, _, _ = common.read_wav_float(path)
        assert sr == common.SAMPLE_RATE
        base["a2_segments"][name] = mono

    return base


def apply_gain_and_convert_local(sources: dict) -> dict:
    parts = c.apply_gain_and_convert(sources)
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
    gain = p9a.compute_gain_for_target_rms(sources["point_notification"]["samples"], target_rms)
    gained = sources["point_notification"]["samples"] * gain
    parts["point_notification"] = gained
    parts["gain_report"]["point_notification"] = {
        "gain": round(float(gain), 4), "rms_before": round(p9a.rms(sources["point_notification"]["samples"]), 5),
        "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5),
    }
    return parts


def build_pieces_with_timeline_local(config: dict, parts: dict) -> list:
    key_phrase_blocks = c.build_key_phrase_blocks(config, parts)
    a2 = parts["a2_segments"]

    seq = [
        ("Intro", parts["intro"]),
        ("Welcome", parts["welcome"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Topic intro", parts["topic_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Japanese title", parts["japanese_title"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 1", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Preview intro", parts["preview_intro"]),
        ("pause_0.65", p9a.silence_stereo(0.65)),
        ("Point explanation", parts["point_explanation"]),
        ("pause_0.7_point_explanation", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", parts["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = tuple(f"Key Phrase {i + 1}" for i in range(len(key_phrase_blocks)))
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 1", a2["comment_1"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 1", a2["full_story_part1"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 2", a2["comment_2"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Full Story Part 2", a2["full_story_part2"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 3", a2["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", parts["point_notification"]),
        ("Point One semantic heading", a2["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS)),
        ("Point One", a2["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading", a2["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Outro", parts["outro"]),
    ]
    return seq


def assemble_with_timeline_local(config: dict, parts: dict) -> dict:
    seq = build_pieces_with_timeline_local(config, parts)
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))

    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur

    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


def stage_assemble_v4(config: dict) -> dict:
    os.makedirs(f"{config['out_dir']}/assembled", exist_ok=True)
    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    sources = load_all_sources_local(config)
    parts = apply_gain_and_convert_local(sources)
    result = assemble_with_timeline_local(config, parts)
    assembled = result["assembled"]

    out_path = f"{config['out_dir']}/assembled/English_Your_Way_A2_IRAN01_v4.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{config['out_dir']}/audit/gain_report_v4.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{config['out_dir']}/audit/timeline_v4.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    # Transcript / Audio整合性監査(継続、ER-003-A2-POINT-HEADING-AUDIO-01
    # §14の考え方をComment 4にも適用): 新しいComment 4文言がcanonical・
    # TTS入力・timeline上のすべてで一致していることをここで明示的に確認する。
    spoken_names = {p["part"] for p in result["timeline"]}
    assert "Comment 4" in spoken_names, "Comment 4がtimelineに存在しません"
    assert os.path.exists(f"{NARRATION_DIR}/comment_4.wav"), "comment_4.wavが存在しません"
    assert "一文で" not in a2gen.A2_SUPPORT_JA["comment_4"], "旧文言(一文で)がcanonical textに残っています"
    audit_entries = [
        {"label": "Comment 4", "text": a2gen.A2_SUPPORT_JA["comment_4"],
         "wav_path": f"{NARRATION_DIR}/comment_4.wav", "in_timeline": True,
         "old_text_absent": "一文で" not in a2gen.A2_SUPPORT_JA["comment_4"]},
    ]
    with open(f"{config['out_dir']}/audit/transcript_audio_consistency_v4.json", "w", encoding="utf-8") as f:
        json.dump(audit_entries, f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }


def main():
    r3 = stage_assemble_v4(CONFIG)
    print(f"[{ARTICLE_ID}] stage_assemble status:", r3["status"], "duration:", r3["duration_seconds"],
          "peak:", r3["peak"], "clipping:", r3["clipping_detected"])

    summary = {"status": "OK", "article_id": ARTICLE_ID, "assemble": r3,
               "point_notification_source": POINT_NOTIFICATION_MP3_PATH,
               "change_from_v3": "Comment 4文言修正(一文で確認しましょう→まとめて確認しましょう)のみ"}
    with open(f"{a2gen.OUT_DIR}/run_summary_audio_v4.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{ARTICLE_ID}] 完了。")


if __name__ == "__main__":
    main()
