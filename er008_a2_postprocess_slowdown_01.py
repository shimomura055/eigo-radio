# ============================================================
# er008_a2_postprocess_slowdown_01.py
# ER-008-A2-POSTPROCESS-SLOWDOWN-PROD-11:
# ER-008-A2-TIMESTRETCH-ABC-10でユーザー承認済みの「6%スローダウン」を
# Production A2音声パイプラインへ配線するための共通ユーティリティ。
# ============================================================
# 設計方針: A2英語spoken content(自然言語の「わずかに遅く」instruction、
# ER-008-EVIDENCE-COMPRESSION-PROD-AND-N7-AUDIO-06で導入)は、same-text
# A/B/C比較(ER-008-A2-SPEED-SAME-TEXT-ABC-09)で安定して機能しないことが
# 判明した。代わりに、TTSは通常ペース(B1と同じ英語style instruction)で
# 生成し、生成後にFFmpeg atempoフィルタ(pitch-preserving time-stretch、
# 実測でpitch変化-0.9%程度・ASR内容破損なしを確認済み)で機械的に6%
# 減速する方式へ切り替える。この方式のメリット(ユーザー承認時の指摘):
# 「Slow down処理をしていないオリジナル音声」がそのまま残るため、Middle
# 等で通常速度が必要な場合にTTS再生成なしで流用できる。
from __future__ import annotations

import subprocess
import wave

import imageio_ffmpeg

A2_SLOWDOWN_PERCENT = 6.0
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def read_wav_duration_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / w.getframerate()


def apply_a2_slowdown(src_path: str, dst_path: str, slowdown_pct: float = A2_SLOWDOWN_PERCENT) -> dict:
    """src_path(TTS生成直後の通常ペース音声)に対し、pitch-preservingな
    time-stretch(FFmpeg `atempo`フィルタ、WSOLA系。単純なsample-rate
    変更[pitchが下がる]は使わない)でslowdown_pct分だけ再生時間を伸ばし、
    dst_pathへ書き出す。ER-008-A2-TIMESTRETCH-ABC-10のNo.7実測(目標値と
    実測値の差0.05ポイント未満、pitch変化-0.9%程度)と同じ処理方式を
    そのまま再利用する(新規アルゴリズムの追加検証はしない)。"""
    tempo = 1.0 / (1.0 + slowdown_pct / 100.0)
    assert 0.5 <= tempo <= 100.0, f"atempoの有効範囲外: {tempo}"
    src_duration = read_wav_duration_seconds(src_path)
    cmd = [
        FFMPEG, "-y", "-i", src_path,
        "-filter:a", f"atempo={tempo:.6f}",
        "-ar", "24000", "-ac", "1", "-sample_fmt", "s16",
        dst_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg atempo failed (slowdown={slowdown_pct}%, src={src_path}): "
                            f"{result.stderr[-2000:]}")
    dst_duration = read_wav_duration_seconds(dst_path)
    actual_slowdown_pct = round((dst_duration / src_duration - 1.0) * 100, 3)
    return {
        "slowdown_pct_target": slowdown_pct, "slowdown_pct_actual": actual_slowdown_pct,
        "src_duration_seconds": round(src_duration, 3), "dst_duration_seconds": round(dst_duration, 3),
        "src_path": src_path, "dst_path": dst_path,
    }
