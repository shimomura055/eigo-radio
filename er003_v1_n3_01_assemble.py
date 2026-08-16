# ============================================================
# er003_v1_n3_01_assemble.py
# ER-003-A2-B1-N3-01: 3テーマ×2レベル Full Audio組み立て
# ============================================================
# B1: er003_v1_b1redesign_assemble04.py(v4、Point Notification直後
# pause除去済み)のtimeline構造をそのまま再利用する。
# A2: er003_v1_iran01_a2_audio04_generate.py(v4)のtimeline構造を
# そのまま再利用する。
# Shell共通のCharon文言(Welcome/Preview intro/Key phrases intro/
# Full story intro/num_one〜five)は、記事非依存の音声としてIRAN01の
# 既存ファイルをそのままコピーして再利用し、新規TTSは行わない
# (A2側はA01のservice-level共有ディレクトリを直接参照する、既存の
# A2アーキテクチャをそのまま踏襲)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_n3_01_assemble.py <theme_id>
#   (theme_idを省略すると3テーマ全部を実行)

from __future__ import annotations

import json
import os
import shutil
import sys

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_b1_scaffold_audio_03_generate as audio03
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_n3_01_articles_generate as gen

SR = p9a.TARGET_SAMPLE_RATE
POINT_NOTIFICATION_MP3_PATH = "C:/Users/tensh/eigo-radio/notification/universfield-new-notification-07-210334.mp3"

# B1既存のshared Charon shell音声(記事非依存、コピー元)
B1_SHARED_SOURCE_DIR = "er003_output/b1redesign_audio_01/IRAN01/narration"
B1_SHARED_NAMES = ("welcome_charon.wav", "preview_intro_charon.wav", "key_phrases_intro_charon.wav",
                    "full_story_intro_charon.wav", "num_one_charon.wav", "num_two_charon.wav",
                    "num_three_charon.wav", "num_four_charon.wav", "num_five_charon.wav")

# 既存Shellで確立済みのpause定数のみ再利用(新規値は作らない)。
NOTIFICATION_ENTRY_PAUSE_SECONDS = 0.5
HEADING_TO_BODY_PAUSE_SECONDS_B1 = audio03.POINT_EXPLANATION_PAUSE_SECONDS
AOEDE_TO_CHARON_PAUSE_SECONDS = audio03.COMMENT_EN_TO_JA_PAUSE_SECONDS
CHARON_TO_AOEDE_PAUSE_SECONDS = audio03.COMMENT_JA_TO_EN_PAUSE_SECONDS
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = audio03.IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS
OUTRO_EXTRA_GAIN_LINEAR = audio03.OUTRO_EXTRA_GAIN_LINEAR
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio03.OUTRO_FURTHER_EXTRA_GAIN_LINEAR


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def copy_b1_shared_assets(narration_dir: str) -> None:
    for name in B1_SHARED_NAMES:
        dst = f"{narration_dir}/{name}"
        if not os.path.exists(dst):
            shutil.copyfile(f"{B1_SHARED_SOURCE_DIR}/{name}", dst)


# ============================================================
# B1組み立て
# ============================================================
def load_b1_sources(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    narration_dir = f"{out_dir}/narration"
    copy_b1_shared_assets(narration_dir)

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    for name in ("welcome", "preview_intro", "key_phrases_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("num_one", "num_two", "num_three", "num_four", "num_five"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}_charon.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    # topic_introは記事固有(N3-01 TTS生成scriptがtopic_intro.wavという
    # ファイル名で新規生成済み)なので、共有Charon shellのコピー元とは
    # 別に、記事ごとのnarration_dirから直接読み込む。
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/topic_intro.wav")
    assert sr == common.SAMPLE_RATE
    narration["topic_intro"] = mono

    b1_segments = {}
    for name in ("full_story_part1", "full_story_part2", "point_one", "point_two"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "preview"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/in_one_line.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["in_one_line"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/point_one_heading.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_one_heading"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/point_two_heading.wav")
    assert sr == common.SAMPLE_RATE
    b1_segments["point_two_heading"] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    key_phrase_components, key_phrase_meanings = {}, {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_ja_charon.wav")
        key_phrase_meanings[rank] = mono

    return {"intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
            "narration": narration, "b1_segments": b1_segments,
            "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
            "kp_items": kp_items}


def apply_b1_gain(sources: dict) -> dict:
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
    result["point_notification"] = gain_to_rms(
        sources["point_notification"]["samples"], target_rms, "point_notification")

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


def build_b1_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for item in parts["kp_items"]:
        rank = item["rank"]
        num_key = num_names[rank - 1]
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts["key_phrase_meanings"][rank], SR)
        blocks.append(block)
    return blocks


def build_b1_timeline(parts: dict) -> list:
    key_phrase_blocks = build_b1_key_phrase_blocks(parts)
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
        ("Comment 3 (Charon, Bridge)", b1["comment_3"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point One cue)", parts["point_notification"]),
        ("Point One semantic heading (Aoede)", b1["point_one_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point One (Aoede)", b1["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading (Aoede)", b1["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(HEADING_TO_BODY_PAUSE_SECONDS_B1)),
        ("Point Two (Aoede)", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(AOEDE_TO_CHARON_PAUSE_SECONDS)),
        ("Comment 4 (Charon)", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(CHARON_TO_AOEDE_PAUSE_SECONDS)),
        ("In One Line (Aoede)", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro (Charon)", parts["outro"]),
    ]
    return seq


# ============================================================
# A2組み立て
# ============================================================
def load_a2_sources(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/a2"
    narration_dir = f"{out_dir}/narration"

    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    point_notification = p9a.load_and_resample_to_target(POINT_NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{narration_dir}/preview.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in c.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{c.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    kp = load_json(f"{out_dir}/key_phrases/keywords_canonicalized.json")
    kp_items = sorted(kp["items"], key=lambda it: it["rank"])
    for i in range(1, len(kp_items) + 1):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/meaning_{i}.wav")
        assert sr == common.SAMPLE_RATE
        narration[f"meaning_{i}"] = mono

    key_phrase_components = {}
    for item in kp_items:
        rank = item["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/kp{rank}_en.wav")
        key_phrase_components[rank] = p9a.p7c.tight_speech_only(mono, sr)

    a2_segments = {}
    for name in ("comment_1", "comment_2", "comment_3", "comment_4", "full_story_part1", "full_story_part2",
                  "point_one", "point_two", "point_one_heading", "point_two_heading", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{narration_dir}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono

    return {
        "intro": intro, "notification": notification, "point_notification": point_notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components, "a2_segments": a2_segments, "kp_items": kp_items,
    }


def apply_a2_gain(sources: dict) -> dict:
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["a2_segments"]["full_story_part1"])) / 2
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
    result["point_notification"] = gain_to_rms(
        sources["point_notification"]["samples"], target_rms, "point_notification")

    intro_final_rms = p9a.rms(result["intro"])
    outro_matched = sources["outro"]["samples"] * p9a.compute_gain_for_target_rms(
        sources["outro"]["samples"], intro_final_rms)
    outro_final = outro_matched * OUTRO_EXTRA_GAIN_LINEAR
    result["outro"] = outro_final
    gain_report["outro"] = {
        "matched_to": "intro_post_gain_rms", "intro_post_gain_rms": round(intro_final_rms, 5),
        "rms_after_match": round(p9a.rms(outro_matched), 5),
        "extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_final), 5), "peak_final": round(p9a.peak(outro_final), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])

    for name, mono in sources["narration"].items():
        gained = gain_to_rms(mono, target_rms, name)
        result[name] = p9a.mono_24k_to_stereo_target(gained)

    key_phrase_stereo = {}
    for number, mono in sources["key_phrase_components"].items():
        gained = gain_to_rms(mono, target_rms, f"key_phrase_en_{number}")
        key_phrase_stereo[number] = p9a.mono_24k_to_stereo_target(gained)
    result["key_phrase_components"] = key_phrase_stereo

    a2_stereo = {}
    for name, mono in sources["a2_segments"].items():
        gained = gain_to_rms(mono, target_rms, f"a2_{name}")
        a2_stereo[name] = p9a.mono_24k_to_stereo_target(gained)
    result["a2_segments"] = a2_stereo

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(新規Preview音声を保持)"}
    result["kp_items"] = sources["kp_items"]
    result["gain_report"] = gain_report
    return result


def build_a2_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for i, item in enumerate(parts["kp_items"]):
        rank = item["rank"]
        num_key = num_names[i]
        meaning_key = f"meaning_{i + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def build_a2_timeline(parts: dict) -> list:
    key_phrase_blocks = build_a2_key_phrase_blocks(parts)
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
        ("pause_0.7_heading_to_body", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Point One", a2["point_one"]),
        ("pause_0.5_notification_entry", p9a.silence_stereo(NOTIFICATION_ENTRY_PAUSE_SECONDS)),
        ("Point Notification (Point Two cue)", parts["point_notification"]),
        ("Point Two semantic heading", a2["point_two_heading"]),
        ("pause_0.7_heading_to_body", p9a.silence_stereo(c.POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Outro", parts["outro"]),
    ]
    return seq


# ============================================================
# 共通組み立てヘルパー
# ============================================================
def assemble_with_timeline(seq: list) -> dict:
    pieces = [samples for _, samples in seq]
    assembled = np.ascontiguousarray(np.concatenate(pieces, axis=0))
    timeline = []
    t = 0.0
    for name, samples in seq:
        dur = len(samples) / SR
        timeline.append({"part": name, "start_seconds": round(t, 3), "duration_seconds": round(dur, 3)})
        t += dur
    return {"assembled": assembled, "timeline": timeline, "total_duration_seconds": round(t, 3)}


def stage_assemble_b1(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/b1b"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_b1_sources(theme)
    parts = apply_b1_gain(sources)
    seq = build_b1_timeline(parts)
    result = assemble_with_timeline(seq)
    assembled = result["assembled"]

    out_path = f"{out_dir}/assembled/English_Your_Way_B1B_{theme['theme_id'].upper()}.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{out_dir}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }
    with open(f"{out_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-ASSEMBLE][{theme['theme_id']}/b1b] status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


def stage_assemble_a2(theme: dict) -> dict:
    out_dir = f"{theme['out_dir']}/a2"
    os.makedirs(f"{out_dir}/assembled", exist_ok=True)
    os.makedirs(f"{out_dir}/audit", exist_ok=True)
    sources = load_a2_sources(theme)
    parts = apply_a2_gain(sources)
    seq = build_a2_timeline(parts)
    result = assemble_with_timeline(seq)
    assembled = result["assembled"]

    out_path = f"{out_dir}/assembled/English_Your_Way_A2_{theme['theme_id'].upper()}.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{out_dir}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{out_dir}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2,
    }
    with open(f"{out_dir}/run_summary_assemble.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print(f"[N3-ASSEMBLE][{theme['theme_id']}/a2] status={summary['status']} "
          f"duration={summary['duration_seconds']} peak={summary['peak']} clipping={summary['clipping_detected']}")
    return summary


def run_theme(theme: dict) -> dict:
    b1_result = stage_assemble_b1(theme)
    a2_result = stage_assemble_a2(theme)
    return {"b1b": b1_result, "a2": a2_result}


def main():
    theme_ids = sys.argv[1:] or [t["theme_id"] for t in gen.THEMES]
    themes_by_id = {t["theme_id"]: t for t in gen.THEMES}
    for theme_id in theme_ids:
        run_theme(themes_by_id[theme_id])
    print("[N3-ASSEMBLE] 完了。")


if __name__ == "__main__":
    main()
