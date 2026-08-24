# ============================================================
# er007_artifact_audio_prep_01.py
# Artifact埋め込み用に、既存WAV(24kHz)をbase64データURIへ変換する。
# サイズ制約(Artifact合計16MB)のため、埋め込み専用コピーとして
# 12kHzへダウンサンプルする(scipy.signal.resample、アンチエイリアス
# 済み)。本番出力(24kHz)のWAVファイル自体は一切変更しない。
# ============================================================
from __future__ import annotations

import base64
import io
import wave

import numpy as np
from scipy.signal import resample

TARGET_RATE = 12000


def wav_to_data_uri(path: str, target_rate: int = TARGET_RATE) -> str:
    with wave.open(path, "rb") as w:
        rate = w.getframerate()
        n = w.getnframes()
        raw = w.readframes(n)
        sampwidth = w.getsampwidth()
        channels = w.getnchannels()
    assert sampwidth == 2 and channels == 1, f"unexpected format: {path}"
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64)
    if rate != target_rate:
        n_target = int(round(len(samples) * target_rate / rate))
        resampled = resample(samples, n_target)
    else:
        resampled = samples
    resampled = np.clip(resampled, -32768, 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(target_rate)
        out.writeframes(resampled.tobytes())
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:audio/wav;base64,{b64}"


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        uri = wav_to_data_uri(p)
        print(f"{p}: {len(uri)} chars ({len(uri)/1024:.1f} KB)")
