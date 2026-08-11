# ============================================================
# er003_v1_a2_audio_ab_01_generate.py
# ER-003-A2-AUDIO-AB-01: A02完成候補 A/B比較(従来速度 vs 約135 WPM)
# ============================================================
# A版: 速度指定なし(既存の自然なTTS読み上げ方式)。Full Story Part1/2・
#   Point One/Two はer003_v1_a2_audio_01_generate.py(audio01)の既存承認
#   音声をそのまま再利用する(速度は変更しないため再生成不要)。
#   In One Lineのみ、見出しテキストを実際に含める修正
#   (ER-003-CROSSLEVEL-AUDIO-04で検証済み)を反映して新規生成する。
# B版: 英語ニュースナレーション(Full Story Part1/2・Point One/Two・
#   In One Line)のみ約135 WPM目安で新規生成。Full Story Part1は元々
#   134.91 WPMと目標付近のため無変更で流用する。
# 両版共通: Key Phrase 5件へ「意味+語末音素+phrase一体感」の統合発音
#   方式(ER-003-CROSSLEVEL-AUDIO-04で試作済み)を適用(feedは既承認版を
#   維持、他4件は新規生成)。Point One→Two・In One Line→Outroポーズを
#   0.8秒へ、Outroをさらに追加減衰(v3)する。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_a2_article as a2
import er003_b1_p9a_audio as p9a
import er003_v1_a2_audio_01_generate as audio01
import er003_v1_a2_audio_02_generate as audio02
import er003_v1_repro01_main_generate as repro01

ARTICLE_ID = "A02"
OUT_DIR = "er003_output/a2_audio_ab_01/A02"

SR = p9a.TARGET_SAMPLE_RATE

# Cross-level定数の再利用(新しい数値は設計しない)
POINT_EXPLANATION_PAUSE_SECONDS = audio02.POINT_EXPLANATION_PAUSE_SECONDS  # 0.7
OUTRO_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR  # v2で確定した1段目(約0.6903)
OUTRO_FURTHER_EXTRA_GAIN_LINEAR = audio02.OUTRO_EXTRA_GAIN_LINEAR  # v3: 同じ係数をもう一段(AUDIO-03/04で試作済み)
POINT1_TO_POINT2_PAUSE_SECONDS = 0.8  # 新規(0.5秒から変更)
IN_ONE_LINE_TO_OUTRO_PAUSE_SECONDS = 0.8  # 新規(0.5秒から変更)

# Key Phrase(A02、方式は既存のまま。使用形は無変更、発音instructionのみ更新)
KEY_PHRASES = repro01.A02_KEY_PHRASES

KEY_PHRASE_AUDIO_PATHS = {
    "One": f"{OUT_DIR}/key_phrase_components/opt_out_unified.wav",
    "Two": f"{OUT_DIR}/key_phrase_components/covered_apps_unified.wav",
    "Three": f"{OUT_DIR}/key_phrase_components/urge_to_watch_unified_r1.wav",
    # feedはCROSSLEVEL-AUDIO-01/02でユーザー承認済みのtrial版を維持(後退させない)
    "Four": f"{audio02.OUT_DIR}/narration/key_phrase_4_feed_trial.wav",
    "Five": f"{OUT_DIR}/key_phrase_components/digital_switch_off_period_unified.wav",
}


def load_all_sources(variant: str) -> dict:
    """variant: 'A'(速度指定なし) または 'B'(約135 WPM)。
    Preview/Comment/Key Phrase/Full Story Part1は両版共通(既存承認音声を
    再利用)。Full Story Part2・Point One・Point Two・In One Lineのみ
    variantごとに異なる音声を読み込む。"""
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(f"{audio02.OUT_DIR}/narration/preview_v2.wav")
    assert preview_sr == common.SAMPLE_RATE

    narration = {}
    for name in repro01.SERVICE_LEVEL_NARRATION_NAMES:
        mono, sr, _, _ = common.read_wav_float(f"{repro01.A01_NARRATION_DIR}/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono
    for name in ("topic_intro", "japanese_title", "meaning_1", "meaning_2", "meaning_3", "meaning_4", "meaning_5"):
        mono, sr, _, _ = common.read_wav_float(f"{repro01.OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    key_phrase_components = {}
    for kp in KEY_PHRASES:
        mono, sr, _, _ = common.read_wav_float(KEY_PHRASE_AUDIO_PATHS[kp["number"]])
        key_phrase_components[kp["number"]] = p9a.p7c.tight_speech_only(mono, sr)

    a2_segments = {}
    # Comment1-3(既存)/Comment4(v2)/Full Story Part1: 両版共通、無変更
    for name in ("comment_1", "comment_2", "comment_3"):
        mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        a2_segments[name] = mono
    mono, sr, _, _ = common.read_wav_float(f"{audio02.OUT_DIR}/narration/comment_4_v2.wav")
    assert sr == common.SAMPLE_RATE
    a2_segments["comment_4"] = mono
    mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/full_story_part1.wav")
    assert sr == common.SAMPLE_RATE
    a2_segments["full_story_part1"] = mono

    if variant == "A":
        mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/full_story_part2.wav")
        a2_segments["full_story_part2"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/point_one.wav")
        a2_segments["point_one"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{audio01.OUT_DIR}/narration/point_two.wav")
        a2_segments["point_two"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/in_one_line_A.wav")
        a2_segments["in_one_line"] = mono
    elif variant == "B":
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/full_story_part2_B.wav")
        a2_segments["full_story_part2"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/point_one_B.wav")
        a2_segments["point_one"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/point_two_B.wav")
        a2_segments["point_two"] = mono
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/in_one_line_B.wav")
        a2_segments["in_one_line"] = mono
    else:
        raise ValueError(f"unknown variant: {variant}")

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "narration": narration,
        "key_phrase_components": key_phrase_components,
        "a2_segments": a2_segments,
    }


def apply_gain_and_convert(sources: dict) -> dict:
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

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(A02 v2で承認済みPreview音声を保持)"}
    result["gain_report"] = gain_report
    return result


def build_key_phrase_blocks(parts: dict) -> list:
    blocks = []
    for kp in KEY_PHRASES:
        num_key = f"num_{kp['number'].lower()}"
        meaning_key = f"meaning_{KEY_PHRASES.index(kp) + 1}"
        block = p9a.build_key_phrase_block(
            parts[num_key], parts["key_phrase_components"][kp["number"]], parts[meaning_key], SR)
        blocks.append(block)
    return blocks


def build_pieces_with_timeline(parts: dict) -> list:
    key_phrase_blocks = build_key_phrase_blocks(parts)
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
        ("pause_0.7_point_explanation", p9a.silence_stereo(POINT_EXPLANATION_PAUSE_SECONDS)),
        ("Preview", parts["preview"]),
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
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("Point One", a2["point_one"]),
        ("pause_0.8_point1_to_point2", p9a.silence_stereo(POINT1_TO_POINT2_PAUSE_SECONDS)),
        ("Point Two", a2["point_two"]),
        ("pause_1.0_en_to_ja", p9a.silence_stereo(1.0)),
        ("Comment 4", a2["comment_4"]),
        ("pause_0.8_ja_to_en", p9a.silence_stereo(0.8)),
        ("In One Line", a2["in_one_line"]),
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


def stage_assemble(variant: str) -> dict:
    os.makedirs(f"{OUT_DIR}/assembled", exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)
    sources = load_all_sources(variant)
    parts = apply_gain_and_convert(sources)
    result = assemble_with_timeline(parts)
    assembled = result["assembled"]

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A2_A02_{variant}.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report_{variant}.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/timeline_{variant}.json", "w", encoding="utf-8") as f:
        json.dump(result["timeline"], f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": result["total_duration_seconds"],
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "timeline": result["timeline"],
    }


if __name__ == "__main__":
    for v in ("A", "B"):
        r = stage_assemble(v)
        print(v, r["status"], "duration:", r["duration_seconds"], "peak:", r["peak"], "clipping:", r["clipping_detected"])
