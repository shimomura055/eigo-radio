# ============================================================
# er003_v1_b1_scaffold_audio_02_generate.py
# ER-003-B1-SCAFFOLD-AUDIO-02: A02 B1 Supported Natural English 完成版Audio
# ============================================================
# ER-003-B1-SCAFFOLD-AUDIO-01で作った11コンテンツパートの音声(すべて
# ASR検証合格済み、無変更で再利用)を、A2の承認済みAudio Shell
# (Intro/Welcome/Topic Intro/Japanese Title/Notification x3/Preview
# Intro/Point解説/Key Phrases Intro/Full Story Intro/Outro、各種pause、
# Outro二段減衰)へ正しく組み込んで完成版候補をassembleする。
#
# Audio Shellの実装は、A02の最終承認済みscript
# er003_v1_a2_audio_ab_01_generate.py(variant B、DECISION_LOG.md
# 2026-08-12で採用確定)の build_pieces_with_timeline / apply_gain_
# and_convert をそのまま踏襲する(新しいpause秒数・gain方式は設計
# しない)。新しいのはB1コンテンツ側の音源差し替えのみ。
#
# 変更するもの(B1固有):
#   - Preview: 日本語 → 易しいSupport英語(AUDIO-01生成済み)
#   - Comment1-4: 日本語 → 易しいSupport英語(AUDIO-01生成済み)
#   - Full Story Part1/2・Point One/Two・In One Line: B2 V2と完全共通
#     (AUDIO-01生成済み、SHA256一致確認)
#   - Key Phrases: A2とは異なる5件(by default/curfew/cross the finish
#     line/pilot/personalised feeds)。A2のmeaning_1-5・key_phrase_
#     componentsは一切使わない(記事内容が異なるため無関係)
#
# 変更しないもの(A2 Shellから継承、無変更):
#   - Intro/Welcome/Topic Intro/Japanese Title/Notification/Preview
#     Intro/Point解説/Key Phrases Intro/Full Story Intro/Outro
#     (すべてA01/A02の既存承認済み音声をそのまま再利用)
#   - 各pause秒数、Key Phraseブロック内部構造、Outro二段減衰、
#     gain-matching方式
#
# Production本体(er003_v1_a2_audio_ab_01_generate.py等)は一切変更せず、
# この独立スクリプトから関数・定数を読み取り専用でimportするのみ。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_scaffold_audio_02_generate.py

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_02_generate as audio02
import er003_v1_b1_scaffold_01_generate as scaffold
import er003_v1_b1_scaffold_audio_01_generate as audio01b
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "A02"
OUT_DIR = "er003_output/b1_scaffold_audio_02/A02"
SR = p9a.TARGET_SAMPLE_RATE

# ------------------------------------------------------------
# Shell定数(A2最終承認script er003_v1_a2_audio_ab_01_generate.pyから
# 読み取り専用で継承。新しい値は作らない)
# ------------------------------------------------------------
POINT_EXPLANATION_PAUSE_SECONDS = audio02.POINT_EXPLANATION_PAUSE_SECONDS  # 0.7
OUTRO_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR  # v3: 同一係数をもう一段(A2と同じ)
POINT1_TO_POINT2_PAUSE_SECONDS = 0.8
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = 0.8
COMMENT_EN_TO_JA_PAUSE_SECONDS = 1.0  # 名称はA2由来(EN→JA)だが、B1ではEN→EN間に適用(H節で説明)
COMMENT_JA_TO_EN_PAUSE_SECONDS = 0.8  # 同上(EN→EN間)

# B1固有のKey Phrases(A2のA02_KEY_PHRASESとは異なる、AUDIO-01で確定した5件)
KEY_PHRASES = audio01b.KEY_PHRASES  # rank/used_form/japanese_gloss(/tts_text)

B1_NARRATION_DIR = "er003_output/b1_scaffold_audio_01/A02/narration"


def load_all_sources() -> dict:
    """Shell要素(Intro/Notification/Outro/Welcome/Topic Intro/Japanese
    Title/Preview Intro/Point解説/Key Phrases Intro/Full Story Intro/
    num_one〜five)はA01/A02の既存承認済み音声をそのまま読み込む。
    コンテンツ要素(Preview/Comment1-4/News5本/Key Phrase 5件)は
    ER-003-B1-SCAFFOLD-AUDIO-01で生成・ASR検証済みの音声をそのまま
    読み込む(再生成しない)。"""
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    narration = {}
    # article/level非依存のservice-level narration(A01の既存承認済み音声を再利用)
    for name in repro01.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{repro01.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    # article固有だがCEFRレベル非依存のnarration(A02の既存承認済み音声を再利用。
    # H節参照: topic_intro/japanese_titleの文言は旧B1本文のタイトルに基づくため、
    # 今回のB2 V2記事のタイトルとは字面が異なる。内容の矛盾ではないが、SoT不一致
    # として報告する)
    for name in ("topic_intro", "japanese_title"):
        mono, sr, _, _ = common.read_wav_float(f"{repro01.OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    # B1コンテンツ(AUDIO-01で生成・ASR検証済み、無変更で再利用)
    b1_segments = {}
    for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4",
                 "full_story_part1", "full_story_part2", "point_one", "point_two", "in_one_line"):
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        b1_segments[name] = mono

    key_phrase_components = {}
    key_phrase_meanings = {}
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR}/kp{rank}_en.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_components[rank] = mono
        mono, sr, _, _ = common.read_wav_float(f"{B1_NARRATION_DIR}/kp{rank}_ja.wav")
        assert sr == common.SAMPLE_RATE
        key_phrase_meanings[rank] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "narration": narration, "b1_segments": b1_segments,
        "key_phrase_components": key_phrase_components, "key_phrase_meanings": key_phrase_meanings,
    }


def apply_gain_and_convert(sources: dict) -> dict:
    """A2(er003_v1_a2_audio_ab_01_generate.apply_gain_and_convert)と同一の
    方式: target_rms = Preview と Full Story Part1 のRMS平均。Previewは
    無加工のアンカーとして扱う(A2と同じ設計判断)。Outroは post-gain
    Introへ一致させた上で、A2と同じ二段の心理音響ベース減衰を適用する。"""
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
        "v2_extra_gain_linear": round(float(OUTRO_EXTRA_GAIN_LINEAR), 4),
        "v3_further_extra_gain_linear": round(float(OUTRO_FURTHER_EXTRA_GAIN_LINEAR), 4),
        "combined_gain_linear_vs_intro": round(float(OUTRO_EXTRA_GAIN_LINEAR * OUTRO_FURTHER_EXTRA_GAIN_LINEAR), 4),
        "rms_final": round(p9a.rms(outro_v3), 5), "peak_final": round(p9a.peak(outro_v3), 5),
    }

    result["preview"] = p9a.mono_24k_to_stereo_target(preview_mono)
    gain_report["preview"] = {"gain": 1.0, "note": "無加工(A2のPreview扱いと同じくRMSアンカーとして使用)"}

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

    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    num_names = ["num_one", "num_two", "num_three", "num_four", "num_five"]
    blocks = []
    for kp in KEY_PHRASES:
        rank = kp["rank"]
        num_key = num_names[rank - 1]
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][rank], parts["key_phrase_meanings"][rank], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(parts: dict) -> list:
    """A2最終承認script(er003_v1_a2_audio_ab_01_generate.build_pieces_
    with_timeline)と同一の並び・pause値を使う。Comment区間の言語間pause
    (元はEN→JA/JA→EN)は、B1ではCommentも英語のためEN→EN間の遷移として
    そのまま適用する(H節で扱いを説明。新しいpauseは設計していない)。"""
    key_phrase_blocks = build_key_phrase_blocks(parts)
    b1 = parts["b1_segments"]

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
        ("pause_0.7_point_explanation", p9a.silence_stereo(POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", b1["preview"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
        ("Notification 2", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Key phrases intro", parts["key_phrases_intro"]),
        ("pause_0.5", p9a.silence_stereo(0.5)),
    ]
    kp_labels = ("Key Phrase 1", "Key Phrase 2", "Key Phrase 3", "Key Phrase 4", "Key Phrase 5")
    for label, block in zip(kp_labels, key_phrase_blocks):
        seq.append((label, block))

    seq += [
        ("Notification 3", parts["notification"]),
        ("pause_0.4", p9a.silence_stereo(0.4)),
        ("Full story intro", parts["full_story_intro"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 1", b1["comment_1"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Full Story Part 1", b1["full_story_part1"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 2", b1["comment_2"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Full Story Part 2", b1["full_story_part2"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 3", b1["comment_3"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("Point One", b1["point_one"]),
        ("pause_0.8_point1_to_point2", p9a.silence_stereo(POINT1_TO_POINT2_PAUSE_SECONDS)),
        ("Point Two", b1["point_two"]),
        ("pause_1.0", p9a.silence_stereo(COMMENT_EN_TO_JA_PAUSE_SECONDS)),
        ("Comment 4", b1["comment_4"]),
        ("pause_0.8", p9a.silence_stereo(COMMENT_JA_TO_EN_PAUSE_SECONDS)),
        ("In One Line", b1["in_one_line"]),
        ("pause_0.8_in_one_line_to_outro", p9a.silence_stereo(IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS)),
        ("Outro", parts["outro"]),
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


def verify_b2_text_sha() -> dict:
    import hashlib
    b2_text = scaffold.load_text(scaffold.B2_ARTICLE_PATH)
    sha = hashlib.sha256(b2_text.encode("utf-8")).hexdigest()
    expected = "e0d1c7f6d839ff83ed42bfe58fd1a4a79e3bb0284a6e082be79e71d0763611d7"
    return {"path": scaffold.B2_ARTICLE_PATH, "sha256": sha, "expected": expected, "match": sha == expected}


def main():
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    sha_check = verify_b2_text_sha()
    print("[B1-SHELL] B2本文SHA一致確認:", sha_check["match"])
    with open(f"{OUT_DIR}/audit/b2_text_sha_check.json", "w", encoding="utf-8") as f:
        json.dump(sha_check, f, ensure_ascii=False, indent=2)
    if not sha_check["match"]:
        print("[B1-SHELL] SHA不一致のため中断します。")
        return

    print("[B1-SHELL] 音源読み込み開始...")
    sources = load_all_sources()
    print("[B1-SHELL] gain調整開始...")
    parts = apply_gain_and_convert(sources)
    print("[B1-SHELL] assemble開始...")
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_B1_A02.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/timeline.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    summary = {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "b2_text_sha_match": sha_check["match"],
    }
    with open(f"{OUT_DIR}/run_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    print("[B1-SHELL] 完了。summary:", json.dumps(summary, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
