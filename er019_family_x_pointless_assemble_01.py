# ============================================================
# er019_family_x_pointless_assemble_01.py
# NEWS-FAMILY-X-POINTLESS-TRIAL-01 Phase B
# ============================================================
# Family X(Point構造廃止)向けB1 Assembly。Audio Validation Gate本体
# (asm.verify_episode_audio_validation_gate)・共通Assembly helper
# (asm.assemble_with_timeline / asm.apply_headroom_safety_valve)・
# pause定数・gain定数は、er003_v1_n3_01_assemble.py(asm)から無変更の
# まま読み取り専用でimportして再利用する(Point前提を持たない汎用部分
# のため。A-2確認済み)。timeline builder(build_b1_timeline)・
# source loader(load_b1_sources)・gain適用(apply_b1_gain)は、Point
# Notification効果音・Point見出し・Point本文・Key Phrase blockを含む
# Point前提の上位関数のため、この3つのみコピーして書き換える。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_assemble as asm

SR = asm.SR


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# B1組み立て(Family X: Key Phrase/Point系一切なし)
# ============================================================
def load_family_x_b1_sources(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    # 既存Audio Validation Gate本体を無変更のまま呼ぶ(A-2確認済み: segment名の
    # ハードコードは本関数自体には無く、DISFLUENCY_QA_MANDATORY_SEGMENTS_
    # BY_LEVEL["B1"]は生成したsegmentにのみ照合されるため、Family Xが生成
    # しないpoint_one_heading等は単に無視される。key_phrase_source_gateも
    # key_phrasesが空dictのためNOT_APPLICABLEになる)。
    asm.verify_episode_audio_validation_gate(out_dir, "B1")

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "full_story_part3",
                  "comment_1", "comment_2", "comment_3", "comment_4", "preview", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    return {"intro": intro, "notification": notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments}


def apply_family_x_b1_gain(sources: dict) -> dict:
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
    outro_v2 = outro_matched * asm.OUTRO_EXTRA_GAIN_LINEAR
    outro_v3 = outro_v2 * asm.OUTRO_FURTHER_EXTRA_GAIN_LINEAR
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

    b1_stereo = {}
    for name, mono in sources["b1_segments"].items():
        if name == "preview":
            continue
        gained = gain_to_rms(mono, target_rms, f"b1_{name}")
        b1_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    b1_stereo["preview"] = result["preview"]
    result["b1_segments"] = b1_stereo

    result["gain_report"] = gain_report
    return result


def build_family_x_b1_timeline(parts: dict) -> list:
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
        ("Full story intro (Charon)", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 1 (Charon)", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 1 (Aoede)", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 2 (Charon)", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 2 (Aoede)", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 3 (Charon, Bridge to Part 3)", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("Full Story Part 3 (Aoede)", b1["full_story_part3"]),
        ("pause_1.0", p9a.silence_stereo(asm.AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(asm.CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(asm.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


def stage_assemble_family_x_b1(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_family_x_b1_sources(theme)
    parts = apply_family_x_b1_gain(sources)
    seq = build_family_x_b1_timeline(parts)
    result = asm.assemble_with_timeline(seq)
    headroom = asm.apply_headroom_safety_valve(result["assembled"], seq)
    assembled = headroom["assembled"]

    out_path = f"{out_dir}/assembled/Family_X_Pointless_B1_{theme['theme_id'].upper()}.wav"

    with open(f"{out_dir}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/headroom_report.json", "w", encoding="utf-8") as f:
        json.dump(headroom["report"], f, ensure_ascii=False, indent=2)

    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "headroom_safety_valve": headroom["report"],
    }
    with open(f"{out_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[FAMILY-X-ASSEMBLE][{theme['theme_id']}/b1b] status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']} "
          f"headroom_applied={headroom['report']['applied']}")
    return summary
