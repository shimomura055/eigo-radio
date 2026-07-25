# ============================================================
# er003_b1_p3z_audio.py
# ER-003-B1-P3Z: 英語前後の間・9パターン比較
# ============================================================
# P3Yで生成済みの3つのcomponent(ja_before_marker.wav/
# en_shot_on_target_trimmed.wav/ja_after_marker.wav)を再利用し、新しい
# TTS生成・MFA再実行・原稿変更は一切行わない。英語前後の「実効的な間」
# (既存componentの自然な無音＋安全余白を含めた最終音声上の実測値)だけ
# を、3(英語前: 0.2/0.3/0.4秒)×3(英語後: 0.2/0.3/0.4秒)=9通りに
# 調整する。
#
# 設計方針: en_shot_on_target_trimmed.wavは、P3Uで既に安全余白(前後
# 各0.08秒)を意図して設定済みの成果物であるため、本ステージでは変更
# しない(固定)。目標の実効間隔は、ja_before_marker.wavの末尾無音
# (トリム)とja_after_marker.wavの先頭無音(パディング)だけを調整して
# 達成する。これにより、各境界の実測誤差は理論上0秒(許容誤差±0.03秒
# に対して十分に小さい)になる。
#
# 再利用するもの(再実装しない):
#   - er002_common.SAMPLE_RATE/read_wav_float/write_wav_float/
#     measure_metrics/apply_dynamics3_once
#   - er003_b1_p3u_audio.find_speech_bounds(無音検出条件、9パターン
#     全てで同一の条件を使う)

from __future__ import annotations

import numpy as np

import er003_b1_p3u_audio as p3u

ARTICLE_ID = "A01"

EXISTING_JA_BEFORE_PATH = "er003_output/b1_p3y/A01/components/ja_before_marker.wav"
EXISTING_EN_PATH = "er003_output/b1_p3y/A01/components/en_shot_on_target_trimmed.wav"
EXISTING_JA_AFTER_PATH = "er003_output/b1_p3y/A01/components/ja_after_marker.wav"

GAP_VALUES = (0.2, 0.3, 0.4)
GAP_TOLERANCE_SECONDS = 0.03

# 無音検出条件(p3u.find_speech_boundsと同一の既定値を9パターン全てで
# 使う: window_ms=20.0, silence_rms_threshold=0.02)。


def _gap_label(seconds: float) -> str:
    return f"{seconds:.1f}".replace(".", "p") + "s"


def build_patterns() -> list[dict]:
    patterns = []
    n = 1
    for before in GAP_VALUES:
        for after in GAP_VALUES:
            patterns.append({
                "no": f"{n:02d}",
                "gap_before_seconds": before,
                "gap_after_seconds": after,
                "filename": f"{n:02d}_A01_gap_before_{_gap_label(before)}_after_{_gap_label(after)}_dynamics3.wav",
            })
            n += 1
    return patterns


def measure_component_silence(samples: "np.ndarray", sample_rate: int) -> dict:
    """p3u.find_speech_boundsと同一の検出条件で、componentの先頭・末尾
    無音長(秒)を計測する。"""
    bounds = p3u.find_speech_bounds(samples, sample_rate)
    n = len(samples)
    if bounds is None:
        return {
            "speech_start_sample": None, "speech_end_sample": None,
            "leading_silence_seconds": None, "trailing_silence_seconds": None,
        }
    speech_start, speech_end = bounds
    return {
        "speech_start_sample": speech_start,
        "speech_end_sample": speech_end,
        "leading_silence_seconds": round(speech_start / sample_rate, 4),
        "trailing_silence_seconds": round((n - speech_end) / sample_rate, 4),
    }


def adjust_trailing_silence(
    samples: "np.ndarray",
    sample_rate: int,
    speech_end_sample: int,
    target_trailing_seconds: float,
) -> tuple["np.ndarray", dict]:
    """samplesの末尾無音を、speech_end_sample(発話終了位置、無音検出で
    特定済み)を基準に、target_trailing_secondsちょうどになるよう調整
    する(不足なら無音をpaddingで追加、超過ならtrimで除去)。発話部分
    (samples[:speech_end_sample])は一切変更しない。"""
    if target_trailing_seconds < 0:
        raise ValueError("target_trailing_secondsは0以上である必要があります")
    target_samples = int(round(target_trailing_seconds * sample_rate))
    speech_part = samples[:speech_end_sample]
    pad_or_trim_len = len(samples) - speech_end_sample
    if target_samples >= pad_or_trim_len:
        extra = np.zeros(target_samples - pad_or_trim_len, dtype=samples.dtype)
        result = np.concatenate([samples, extra])
    else:
        result = samples[:speech_end_sample + target_samples]
    achieved_trailing_seconds = (len(result) - speech_end_sample) / sample_rate
    return result, {
        "target_trailing_seconds": target_trailing_seconds,
        "achieved_trailing_seconds": round(achieved_trailing_seconds, 4),
        "speech_content_unchanged": bool(np.array_equal(result[:speech_end_sample], speech_part)),
    }


def adjust_leading_silence(
    samples: "np.ndarray",
    sample_rate: int,
    speech_start_sample: int,
    target_leading_seconds: float,
) -> tuple["np.ndarray", dict]:
    """samplesの先頭無音を、speech_start_sample(発話開始位置)を基準に、
    target_leading_secondsちょうどになるよう調整する。発話部分
    (samples[speech_start_sample:])は一切変更しない。"""
    if target_leading_seconds < 0:
        raise ValueError("target_leading_secondsは0以上である必要があります")
    target_samples = int(round(target_leading_seconds * sample_rate))
    speech_part = samples[speech_start_sample:]
    if target_samples >= speech_start_sample:
        extra = np.zeros(target_samples - speech_start_sample, dtype=samples.dtype)
        result = np.concatenate([extra, samples])
        new_speech_start = target_samples
    else:
        result = samples[speech_start_sample - target_samples:]
        new_speech_start = target_samples
    achieved_leading_seconds = new_speech_start / sample_rate
    return result, {
        "target_leading_seconds": target_leading_seconds,
        "achieved_leading_seconds": round(achieved_leading_seconds, 4),
        "speech_content_unchanged": bool(np.array_equal(result[new_speech_start:], speech_part)),
    }
