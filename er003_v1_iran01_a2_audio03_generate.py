# ============================================================
# er003_v1_iran01_a2_audio03_generate.py
# ER-003-A2-POINT-HEADING-AUDIO-01: A2 Point One/Two semantic heading追加
# ============================================================
# v2(Point専用Notification導入)から変更するのは以下の2点のみ:
#   - Point Notification直後に、新規TTS生成したsemantic heading
#     (Aoede)を挿入する(記事データには存在したが、これまで一度も
#     音声化されていなかった)。
#   - Point Notification直後のpause(0.4秒)を除去する。理由はB1と
#     同様(Notification音源自体に長いtrailing無音があるため)だが、
#     A2固有に音源の実測(-40dB基準で末尾約1.1秒が無音)で確認した
#     うえでの判断であり、B1の設定を機械的にコピーしたものではない。
#     heading→body間のpauseは、A2に既存の
#     POINT_EXPLANATION_PAUSE_SECONDS(0.7秒、Point explanation
#     ナレーションで既に使用中の値)をそのまま再利用する(新規値なし)。
# Comment 3/4の文言・Point One/Two本文・Voice(単一Aoede)・
# Key Phrase選定・その他の順序/pauseはすべてv2から無変更で再利用する。
# Point One/Two spoken label(番号)は追加しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_a2_audio03_generate.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2gen

ARTICLE_ID = "IRAN01_A2_v3"
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


def stage_assemble_v3(config: dict) -> dict:
    os.makedirs(f"{config['out_dir']}/assembled", exist_ok=True)
    os.makedirs(f"{config['out_dir']}/audit", exist_ok=True)
    sources = load_all_sources_local(config)
    parts = apply_gain_and_convert_local(sources)
    result = assemble_with_timeline_local(config, parts)
    assembled = result["assembled"]

    out_path = f"{config['out_dir']}/assembled/English_Your_Way_A2_IRAN01_v3.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{config['out_dir']}/audit/gain_report_v3.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{config['out_dir']}/audit/timeline_v3.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    # Transcript / Audio整合性監査(ER-003-A2-POINT-HEADING-AUDIO-01 §14):
    # 新規追加した2件のheadingについて、TTS音声ファイルの存在と、
    # assembly timeline上への実在を、この場で明示的にassertする。
    spoken_names = {p["part"] for p in result["timeline"]}
    for label in ("Point One semantic heading", "Point Two semantic heading"):
        assert label in spoken_names, f"heading '{label}' がtimelineに存在しません"
    for name in ("point_one_heading", "point_two_heading"):
        path = f"{NARRATION_DIR}/{name}.wav"
        assert os.path.exists(path), f"heading音声ファイルが存在しません: {path}"
    audit_entries = [
        {"label": "Point One semantic heading", "text": a2gen.A2_PARTS["point_one_heading"] + ".",
         "wav_path": f"{NARRATION_DIR}/point_one_heading.wav", "in_timeline": True},
        {"label": "Point Two semantic heading", "text": a2gen.A2_PARTS["point_two_heading"] + ".",
         "wav_path": f"{NARRATION_DIR}/point_two_heading.wav", "in_timeline": True},
    ]
    with open(f"{config['out_dir']}/audit/transcript_audio_consistency_v3.json", "w", encoding="utf-8") as f:
        json.dump(audit_entries, f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }


def main():
    r3 = stage_assemble_v3(CONFIG)
    print(f"[{ARTICLE_ID}] stage_assemble status:", r3["status"], "duration:", r3["duration_seconds"],
          "peak:", r3["peak"], "clipping:", r3["clipping_detected"])

    summary = {"status": "OK", "article_id": ARTICLE_ID, "assemble": r3,
               "point_notification_source": POINT_NOTIFICATION_MP3_PATH,
               "change_from_v2": "Point One/Two semantic heading新規追加、Notification直後pause除去"}
    with open(f"{a2gen.OUT_DIR}/run_summary_audio_v3.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[{ARTICLE_ID}] 完了。")


if __name__ == "__main__":
    main()
