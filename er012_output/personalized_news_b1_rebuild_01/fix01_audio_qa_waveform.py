# ============================================================
# er012_output/personalized_news_b1_rebuild_01/fix01_audio_qa_waveform.py
# 管理ID: USER-TEST-PERSONALIZED-NEWS-B1-REBUILD-01-FIX-01
# ============================================================
# 目的: 全TTS再生成後の機械的QA(委任文5節(b))。新Production仕様ではなく、
# 記事dir配下限定の監査スクリプト(既存Gate/Validatorを緩和・置換しない、
# 追加の目視確認材料を作るだけ)。各segment wav + assembled episode wavに
# 対して、click/pop候補(隣接サンプル振幅急変)・無音区間(>1.5秒)・
# segment境界前後50msのRMS急変・区間RMSの偏差(音量揺れ)を算出する。
from __future__ import annotations

import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath("."))
import er002_common as common

BASE_DIR = "er012_output/personalized_news_b1_rebuild_01/audio/b1_2v_fix01"
NARRATION_DIR = f"{BASE_DIR}/b1b/narration"
ASSEMBLED_DIR = f"{BASE_DIR}/b1b/assembled"
TIMELINE_PATH = f"{BASE_DIR}/b1b/audit/timeline.json"
OUT_PATH = f"{BASE_DIR}/b1b/audit_fix01/audio_qa.json"

CLICK_JUMP_THRESHOLD = 0.3       # (改訂前の素朴な閾値、下記CLICK_SMOOTHED_JUMP_THRESHOLDへ置換)
CLICK_SMOOTH_WINDOW_SAMPLES = 21  # 約0.875ms(24kHz)の移動平均で高域(摩擦音等)成分を抑制
CLICK_SMOOTHED_JUMP_THRESHOLD = 0.08  # 平滑化後の信号での隣接点ジャンプ閾値
# 改訂理由(実測): 素の隣接サンプル間ジャンプ(閾値0.3)は、24kHz音声の
# 摩擦音(s/f/th等、ナイキスト近傍の高域エネルギーを持つ)で日常的に0.3〜1.1を
# 超えるため(例: preview.wav idx=536409付近で-0.598→0.534→0.024→-0.520と
# サンプルごとに符号反転する自然な摩擦音波形を実測確認)、真のclick/pop
# (段差的な不連続、低域成分を含む)と摩擦音の高域振動を区別できず大量の
# false positiveを生む(実測: preview.wavだけで4966件)。21サンプル
# (≈0.875ms)移動平均で平滑化すると、同じpreview.wavの平滑化後の最大隣接差は
# 0.055まで低下し(閾値0.08で0件)、正常な摩擦音は平滑化により除去される一方、
# 真の段差的click/popは低域成分を含むため平滑化後も残る性質を利用する。
SILENCE_ABS_THRESHOLD = 0.003    # 無音とみなす絶対振幅しきい値(約-50dBFS)
SILENCE_MIN_SECONDS = 1.5
BOUNDARY_WINDOW_SECONDS = 0.05   # segment境界前後50ms
BOUNDARY_RMS_JUMP_RATIO = 3.0    # 境界前後RMS比がこれを超えたら急変として報告
VOLUME_WINDOW_SECONDS = 1.0
VOLUME_CV_WARN = 0.6             # 区間RMSの変動係数(std/mean)がこれを超えたら報告


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2))) if len(x) else 0.0


def detect_clicks(samples: np.ndarray, sr: int) -> list:
    """平滑化後隣接ジャンプ方式(上記CLICK_SMOOTHED_JUMP_THRESHOLD参照、
    実測により摩擦音の高域振動をfalse positiveとして誤検知しないよう改訂)。"""
    if len(samples) < CLICK_SMOOTH_WINDOW_SAMPLES + 2:
        return []
    kernel = np.ones(CLICK_SMOOTH_WINDOW_SAMPLES) / CLICK_SMOOTH_WINDOW_SAMPLES
    smoothed = np.convolve(samples, kernel, mode="same")
    diffs = np.abs(np.diff(smoothed))
    idx = np.where(diffs >= CLICK_SMOOTHED_JUMP_THRESHOLD)[0]
    return [{"sample_index": int(i), "time_seconds": round(i / sr, 4),
              "smoothed_jump": round(float(diffs[i]), 4)} for i in idx]


def detect_silence_regions(samples: np.ndarray, sr: int) -> list:
    if len(samples) == 0:
        return []
    is_silent = np.abs(samples) < SILENCE_ABS_THRESHOLD
    regions = []
    start = None
    for i, v in enumerate(is_silent):
        if v and start is None:
            start = i
        elif not v and start is not None:
            dur = (i - start) / sr
            if dur >= SILENCE_MIN_SECONDS:
                regions.append({"start_seconds": round(start / sr, 3), "end_seconds": round(i / sr, 3),
                                 "duration_seconds": round(dur, 3)})
            start = None
    if start is not None:
        dur = (len(samples) - start) / sr
        if dur >= SILENCE_MIN_SECONDS:
            regions.append({"start_seconds": round(start / sr, 3),
                             "end_seconds": round(len(samples) / sr, 3), "duration_seconds": round(dur, 3)})
    return regions


def volume_variation(samples: np.ndarray, sr: int) -> dict:
    win = int(VOLUME_WINDOW_SECONDS * sr)
    if win <= 0 or len(samples) < win:
        return {"windows": 0, "mean_rms": None, "std_rms": None, "cv": None, "flag": False}
    window_rms = [rms(samples[i:i + win]) for i in range(0, len(samples) - win, win)]
    nonzero = [r for r in window_rms if r > 1e-6]
    if not nonzero:
        return {"windows": len(window_rms), "mean_rms": 0.0, "std_rms": 0.0, "cv": None, "flag": False}
    mean_r = float(np.mean(nonzero))
    std_r = float(np.std(nonzero))
    cv = std_r / mean_r if mean_r > 0 else None
    return {"windows": len(window_rms), "mean_rms": round(mean_r, 5), "std_rms": round(std_r, 5),
            "cv": round(cv, 4) if cv is not None else None, "flag": bool(cv is not None and cv > VOLUME_CV_WARN)}


def analyze_one(wav_path: str) -> dict:
    samples, sr, channels, _ = common.read_wav_float(wav_path)
    if channels > 1:
        samples = samples.reshape(-1, channels)[:, 0]
    clicks = detect_clicks(samples, sr)
    silence = detect_silence_regions(samples, sr)
    volume = volume_variation(samples, sr)
    metrics = common.measure_metrics(samples, sr)
    return {
        "wav_path": wav_path, "sample_rate": sr, "duration_seconds": metrics["duration_seconds"],
        "peak_dbfs": metrics["peak_dbfs"], "clipping_detected": metrics["clipping_detected"],
        "click_pop_candidates": clicks, "click_pop_count": len(clicks),
        "silence_regions_over_1_5s": silence,
        "volume_variation": volume,
    }


def analyze_boundaries(assembled_path: str, timeline: list) -> list:
    samples, sr, channels, _ = common.read_wav_float(assembled_path)
    if channels > 1:
        samples = samples.reshape(-1, channels)[:, 0]
    win = int(BOUNDARY_WINDOW_SECONDS * sr)
    results = []
    cum = 0.0
    boundaries = []
    for entry in timeline:
        boundaries.append((entry["part"], cum))
        cum += entry["duration_seconds"]
    for i in range(1, len(boundaries)):
        name, t = boundaries[i]
        idx = int(t * sr)
        before = samples[max(0, idx - win):idx]
        after = samples[idx:idx + win]
        r_before, r_after = rms(before), rms(after)
        ratio = (max(r_before, r_after) / min(r_before, r_after)) if min(r_before, r_after) > 1e-6 else None
        flag = bool(ratio is not None and ratio > BOUNDARY_RMS_JUMP_RATIO)
        results.append({
            "boundary_before_part": boundaries[i - 1][0], "boundary_after_part": name,
            "time_seconds": round(t, 3), "rms_before": round(r_before, 5), "rms_after": round(r_after, 5),
            "ratio": round(ratio, 3) if ratio is not None else None, "flag": flag,
        })
    return results


def main() -> None:
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    segment_wavs = sorted(glob.glob(f"{NARRATION_DIR}/*.wav"))
    segment_results = {os.path.basename(p)[:-4]: analyze_one(p) for p in segment_wavs}

    assembled_wavs = glob.glob(f"{ASSEMBLED_DIR}/*.wav")
    assembled_results = {os.path.basename(p)[:-4]: analyze_one(p) for p in assembled_wavs}

    boundary_results = []
    if os.path.exists(TIMELINE_PATH) and assembled_wavs:
        with open(TIMELINE_PATH, encoding="utf-8") as f:
            timeline = json.load(f)
        boundary_results = analyze_boundaries(assembled_wavs[0], timeline)

    flagged_segments = {k: v for k, v in segment_results.items()
                         if v["click_pop_count"] > 0 or v["silence_regions_over_1_5s"]
                         or v["volume_variation"]["flag"] or v["clipping_detected"]}
    flagged_boundaries = [b for b in boundary_results if b["flag"]]

    summary = {
        "thresholds": {
            "click_jump_threshold": CLICK_JUMP_THRESHOLD, "silence_abs_threshold": SILENCE_ABS_THRESHOLD,
            "silence_min_seconds": SILENCE_MIN_SECONDS, "boundary_window_seconds": BOUNDARY_WINDOW_SECONDS,
            "boundary_rms_jump_ratio": BOUNDARY_RMS_JUMP_RATIO, "volume_window_seconds": VOLUME_WINDOW_SECONDS,
            "volume_cv_warn": VOLUME_CV_WARN,
        },
        "segment_count": len(segment_results),
        "flagged_segment_count": len(flagged_segments),
        "flagged_segments": list(flagged_segments.keys()),
        "flagged_boundary_count": len(flagged_boundaries),
        "flagged_boundaries": flagged_boundaries,
        "segments": segment_results,
        "assembled": assembled_results,
        "boundaries": boundary_results,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[FIX-01-AUDIO-QA] segments={len(segment_results)} flagged_segments={len(flagged_segments)} "
          f"flagged_boundaries={len(flagged_boundaries)} -> {OUT_PATH}")


if __name__ == "__main__":
    main()
