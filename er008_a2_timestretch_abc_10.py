# ============================================================
# er008_a2_timestretch_abc_10.py
# ER-008-A2-TIMESTRETCH-ABC-10:
# No.7 A2 Full Story Part 1の既存音声(新規TTS生成なし)に対し、FFmpegの
# pitch-preserving time-stretch(atempoフィルタ、WSOLA系アルゴリズム、
# 単純なsample-rate変更によるpitch低下ではない)で3%/6%/9%の減速を
# 適用し、0%(元音声)と合わせて4条件を比較する。VALIDATION_ONLY
# (Production Audio Pipelineへは配線しない)。
# ============================================================
from __future__ import annotations

import json
import os
import wave

import imageio_ffmpeg
import numpy as np

import er006_asr_provider_routing_01 as routing
import er006_preprod_hardening_01_validation as validator

SOURCE_WAV = "er006_output/pool_pilot_01/pool_n7_assigned_desks/a2/narration/full_story_part1.wav"
OUT_DIR = "er008_output/n7_a2_timestretch_abc_10"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

CANONICAL_TEXT = (
    "After the pandemic, many offices changed how people sit at work. Instead of giving each "
    "person a desk, they introduced hot-desking. A worker comes in, finds an empty desk, and "
    "uses it for the day. No personal desk is waiting. Now, some offices are changing again. "
    "Reports show some companies bringing back assigned desks for certain workers or teams. In "
    "this system, a person or team has a regular place."
)
WORD_COUNT = len(CANONICAL_TEXT.split())

CANDIDATES = {
    "A": {"slowdown_pct": 0, "label": "0% Original"},
    "B": {"slowdown_pct": 3, "label": "3% slower"},
    "C": {"slowdown_pct": 6, "label": "6% slower"},
    "D": {"slowdown_pct": 9, "label": "9% slower"},
}


def read_wav_info(path: str) -> dict:
    with wave.open(path, "rb") as w:
        return {
            "framerate": w.getframerate(), "channels": w.getnchannels(),
            "sampwidth": w.getsampwidth(), "nframes": w.getnframes(),
            "duration_seconds": round(w.getnframes() / w.getframerate(), 4),
        }


def apply_timestretch(src_path: str, dst_path: str, slowdown_pct: float) -> None:
    """slowdown_pct=0の場合はそのままコピー(FFmpeg再エンコードによる
    劣化を避ける)。それ以外はatempo=1/(1+slowdown_pct/100)で再生時間
    だけを伸ばす(pitch-preserving、単純なsample-rate変更[asetrate等]
    はPart Bで明示的に禁止されているため使わない)。"""
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    if slowdown_pct == 0:
        import shutil
        shutil.copyfile(src_path, dst_path)
        return
    tempo = 1.0 / (1.0 + slowdown_pct / 100.0)
    assert 0.5 <= tempo <= 100.0, f"atempoの有効範囲外: {tempo}"
    cmd = [
        FFMPEG, "-y", "-i", src_path,
        "-filter:a", f"atempo={tempo:.6f}",
        "-ar", "24000", "-ac", "1", "-sample_fmt", "s16",
        dst_path,
    ]
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (slowdown={slowdown_pct}%): {result.stderr[-2000:]}")


# ------------------------------------------------------------
# 簡易F0(基本周波数)推定: 自己相関法。pitch維持確認専用の軽量実装
# (librosa等の追加依存を増やさない、numpy/scipyのみで完結させる)。
# ------------------------------------------------------------
def _read_wav_float(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    return samples, sr


def _estimate_f0_autocorr(frame: np.ndarray, sr: int, fmin: float = 75.0, fmax: float = 400.0) -> float | None:
    frame = frame - frame.mean()
    if np.max(np.abs(frame)) < 0.01:
        return None  # 無音/ほぼ無音フレームは除外
    windowed = frame * np.hanning(len(frame))
    corr = np.correlate(windowed, windowed, mode="full")
    corr = corr[len(corr) // 2:]
    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)
    if max_lag >= len(corr):
        return None
    segment = corr[min_lag:max_lag]
    if len(segment) == 0 or corr[0] <= 0:
        return None
    peak_idx = int(np.argmax(segment))
    peak_val = segment[peak_idx]
    if peak_val / corr[0] < 0.3:
        return None  # 有声音らしい周期性が弱いフレームは信頼しない
    lag = min_lag + peak_idx
    return sr / lag


def estimate_median_f0(path: str, frame_ms: float = 40.0, hop_ms: float = 20.0) -> dict:
    samples, sr = _read_wav_float(path)
    frame_len = int(sr * frame_ms / 1000)
    hop_len = int(sr * hop_ms / 1000)
    f0s = []
    for start in range(0, len(samples) - frame_len, hop_len):
        frame = samples[start:start + frame_len]
        f0 = _estimate_f0_autocorr(frame, sr)
        if f0 is not None:
            f0s.append(f0)
    if not f0s:
        return {"median_f0_hz": None, "voiced_frame_count": 0}
    return {"median_f0_hz": round(float(np.median(f0s)), 2), "voiced_frame_count": len(f0s)}


def run_asr_check(path: str) -> dict:
    asr_text, err = routing.transcribe(path, language="en-US")
    if err:
        return {"asr_text": None, "error": err, "classification": "TTS_FAILURE"}
    result = validator.classify_asr_match(CANONICAL_TEXT, asr_text)
    return {"asr_text": asr_text, "error": None, "classification": result.classification,
            "should_pass": result.should_pass, "normalized_ratio": result.normalized_ratio}


def run_comparison() -> dict:
    source_info = read_wav_info(SOURCE_WAV)
    source_f0 = estimate_median_f0(SOURCE_WAV)
    print(f"[TS-10] source: {source_info} f0={source_f0}")

    results = {}
    for key, cfg in CANDIDATES.items():
        out_path = f"{OUT_DIR}/{key}/full_story_part1.wav"
        print(f"[TS-10][{key}] {cfg['label']} 処理開始...")
        apply_timestretch(SOURCE_WAV, out_path, cfg["slowdown_pct"])
        info = read_wav_info(out_path)
        f0 = estimate_median_f0(out_path)
        asr = run_asr_check(out_path)

        actual_duration_ratio = info["duration_seconds"] / source_info["duration_seconds"]
        actual_slowdown_pct = round((actual_duration_ratio - 1.0) * 100, 2)

        results[key] = {
            "label": cfg["label"], "target_slowdown_pct": cfg["slowdown_pct"],
            "duration_seconds": info["duration_seconds"],
            "actual_slowdown_pct": actual_slowdown_pct,
            "f0": f0,
            "f0_delta_hz": (round(f0["median_f0_hz"] - source_f0["median_f0_hz"], 2)
                            if f0.get("median_f0_hz") and source_f0.get("median_f0_hz") else None),
            "f0_delta_pct": (round((f0["median_f0_hz"] / source_f0["median_f0_hz"] - 1) * 100, 2)
                             if f0.get("median_f0_hz") and source_f0.get("median_f0_hz") else None),
            "asr": asr,
            "path": out_path,
        }
        print(f"[TS-10][{key}] duration={info['duration_seconds']}s actual_slowdown={actual_slowdown_pct}% "
              f"f0={f0.get('median_f0_hz')}Hz asr={asr['classification']}")

    return {"source": {**source_info, "path": SOURCE_WAV}, "source_f0": source_f0,
            "word_count": WORD_COUNT, "results": results}


if __name__ == "__main__":
    # 元音声のactive-speech duration(margin除いた実発話区間)をtts_
    # generation_results.jsonのtrim_infoから取得する(新規TTS生成をせず
    # 既存の記録値を再利用、Part C「TTS再生成は禁止」を遵守)。
    with open("er006_output/pool_pilot_01/pool_n7_assigned_desks/a2/audit/tts_generation_results.json",
              encoding="utf-8") as f:
        tts_results = json.load(f)
    trim_info = tts_results["segments"]["full_story_part1"]["trim_info"]
    source_active_speech = (trim_info["trimmed_duration_seconds"]
                             - trim_info["leading_margin_retained_seconds"]
                             - trim_info["trailing_margin_retained_seconds"])

    out = run_comparison()
    out["source"]["active_speech_duration"] = round(source_active_speech, 3)
    out["source"]["active_speech_wpm"] = round(WORD_COUNT / (source_active_speech / 60), 2)
    for key, r in out["results"].items():
        ratio = r["duration_seconds"] / out["source"]["duration_seconds"]
        r["active_speech_duration_seconds"] = round(source_active_speech * ratio, 3)
        r["active_speech_wpm"] = round(WORD_COUNT / (r["active_speech_duration_seconds"] / 60), 2)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(f"{OUT_DIR}/timestretch_comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print("[TS-10] 完了。結果を保存しました:", f"{OUT_DIR}/timestretch_comparison_results.json")
