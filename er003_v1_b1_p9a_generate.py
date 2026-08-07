# ============================================================
# er003_v1_b1_p9a_generate.py
# ER-003-B1-P9A: 「English Your Way」Podcast完成版組み立て
# ============================================================
# Preview(P7C)・本編(P8A)は無変更のまま再利用。番組名・記事タイトル
# (英語+日本語)・セクション案内2件のみ新規生成済み(narration/配下)。
# Intro/notification/outroは外部mp3をそのまま使用(内容・速度・ピッチは
# 変えず、48000Hz/stereoへリサンプリングのみ)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1_p9a_generate.py

from __future__ import annotations

import json

import numpy as np

import er002_common as common
import er003_b1_p9a_audio as p9a

OUT_DIR = "er003_output/b1_p9a/A01"
SR = p9a.TARGET_SAMPLE_RATE


def load_all_sources() -> dict:
    intro = p9a.load_and_resample_to_target(p9a.INTRO_MP3_PATH)
    notification = p9a.load_and_resample_to_target(p9a.NOTIFICATION_MP3_PATH)
    outro = p9a.load_and_resample_to_target(p9a.OUTRO_MP3_PATH)

    preview_mono, preview_sr, _, _ = common.read_wav_float(p9a.PREVIEW_PATH)
    body_mono, body_sr, _, _ = common.read_wav_float(p9a.BODY_PATH)
    assert preview_sr == common.SAMPLE_RATE and body_sr == common.SAMPLE_RATE

    narration = {}
    for name in ("podcast_name", "english_title", "japanese_title", "preview_intro", "full_story_intro"):
        mono, sr, _, _ = common.read_wav_float(f"{OUT_DIR}/narration/{name}.wav")
        assert sr == common.SAMPLE_RATE
        narration[name] = mono

    return {
        "intro": intro, "notification": notification, "outro": outro,
        "preview_mono": preview_mono, "body_mono": body_mono, "narration": narration,
    }


def apply_gain_and_convert(sources: dict) -> dict:
    """PreviewとBody(本編)は無加工のまま基準とする。それ以外
    (Intro/notification/outro/新規ナレーション5点)だけ、Preview・Bodyの
    平均RMSへ近づけるスカラーgainを掛けてから48kHz/stereoへ変換する
    (Dynamics3等の圧縮は使わない、内容・速度・ピッチは変えない)。"""
    target_rms = (p9a.rms(sources["preview_mono"]) + p9a.rms(sources["body_mono"])) / 2

    gain_report = {}

    def to_stereo_gain_applied(mono_24k, label):
        gain = p9a.compute_gain_for_target_rms(mono_24k, target_rms)
        gained = mono_24k * gain
        stereo = p9a.mono_24k_to_stereo_target(gained)
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(mono_24k), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return stereo

    def apply_gain_to_stereo(stereo_data, label):
        gain = p9a.compute_gain_for_target_rms(stereo_data, target_rms)
        gained = stereo_data * gain
        gain_report[label] = {"gain": round(float(gain), 4), "rms_before": round(p9a.rms(stereo_data), 5),
                               "rms_after": round(p9a.rms(gained), 5), "peak_after": round(p9a.peak(gained), 5)}
        return gained

    result = {"target_rms": round(target_rms, 5)}
    result["intro"] = apply_gain_to_stereo(sources["intro"]["samples"], "intro")
    result["notification"] = apply_gain_to_stereo(sources["notification"]["samples"], "notification")
    result["outro"] = apply_gain_to_stereo(sources["outro"]["samples"], "outro")
    result["preview"] = p9a.mono_24k_to_stereo_target(sources["preview_mono"])  # 無加工
    result["body"] = p9a.mono_24k_to_stereo_target(sources["body_mono"])  # 無加工
    for name, mono in sources["narration"].items():
        result[name] = to_stereo_gain_applied(mono, name)

    gain_report["preview"] = {"gain": 1.0, "note": "無加工(既存承認済み音声を保持)"}
    gain_report["body"] = {"gain": 1.0, "note": "無加工(既存承認済み音声を保持)"}
    result["gain_report"] = gain_report
    return result


def assemble(parts: dict) -> "np.ndarray":
    pieces = [
        parts["intro"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_INTRO_SECONDS),
        parts["podcast_name"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_PODCAST_NAME_SECONDS),
        parts["english_title"],
        p9a.silence_stereo(p9a.PAUSE_BETWEEN_TITLES_SECONDS),
        parts["japanese_title"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_JAPANESE_TITLE_SECONDS),
        parts["notification"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_NOTIFICATION_SECONDS),
        parts["preview_intro"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_PREVIEW_INTRO_SECONDS),
        parts["preview"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_PREVIEW_SECONDS),
        parts["notification"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_NOTIFICATION_SECONDS),
        parts["full_story_intro"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_FULL_STORY_INTRO_SECONDS),
        parts["body"],
        p9a.silence_stereo(p9a.PAUSE_AFTER_FULL_STORY_SECONDS),
        parts["outro"],
    ]
    return np.ascontiguousarray(np.concatenate(pieces, axis=0))


def run() -> dict:
    sources = load_all_sources()
    parts = apply_gain_and_convert(sources)
    assembled = assemble(parts)

    out_path = f"{OUT_DIR}/assembled/English_Your_Way_A01.wav"
    common.write_wav_float(out_path, assembled, SR, 2)
    metrics = common.measure_metrics(assembled[:, 0], SR)

    with open(f"{OUT_DIR}/audit/gain_report.json", "w", encoding="utf-8") as f:
        json.dump(parts["gain_report"], f, ensure_ascii=False, indent=2)
    with open(f"{OUT_DIR}/audit/target_rms.json", "w", encoding="utf-8") as f:
        json.dump({"target_rms": parts["target_rms"]}, f, ensure_ascii=False, indent=2)

    return {
        "status": "OK", "out_path": out_path, "duration_seconds": round(len(assembled) / SR, 4),
        "clipping_detected": metrics["clipping_detected"], "peak": round(p9a.peak(assembled), 5),
        "sample_rate": SR, "channels": 2, "gain_report": parts["gain_report"],
    }


if __name__ == "__main__":
    result = run()
    print("status:", result["status"])
    print("out_path:", result["out_path"])
    print("duration_seconds:", result["duration_seconds"])
    print("clipping_detected:", result["clipping_detected"])
    print("peak:", result["peak"])
