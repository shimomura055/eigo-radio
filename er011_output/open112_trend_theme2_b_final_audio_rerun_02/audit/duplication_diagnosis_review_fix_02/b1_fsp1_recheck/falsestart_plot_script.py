# ============================================================
# falsestart_plot_script.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 (B1 FSP1 追加特性解析、図生成)
# ============================================================
# falsestart_characterization_evidence.json の内容から、試聴用ページに
# 添付するエネルギー包絡図・自己相関(短run)ヒートマップ図をpngで生成する。
# 診断のみ、Production/Assembly/Validatorへの変更なし。

from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_PATH = os.path.join(OUT_DIR, "falsestart_characterization_evidence.json")


def plot_rms_envelope():
    d = json.load(open(EVIDENCE_PATH, encoding="utf-8"))
    r = d["rms_onset_analysis"]
    times = np.array(r["times"])
    rms = np.array(r["rms"])
    onsets = r["onsets"]

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(times, rms, color="#1f77b4", linewidth=1.2, label="RMS envelope (frame20ms/hop5ms)")
    for o in onsets:
        ax.axvline(o["time"], color="#d62728", alpha=0.35, linewidth=1.0)
    # 短run rescanで見つかった反復候補(time_a=0.24-0.26s, lag=0.965-0.97s)を明示
    src = d["short_run_rescan"]["best_by_threshold"]
    ta = src["0.6"]["time_a"]
    lag = src["0.6"]["lag"]
    run_len = src["0.6"]["run_length_seconds"]
    ax.axvspan(ta, ta + run_len, color="#2ca02c", alpha=0.20,
               label=f"repeat window A ({ta}-{round(ta+run_len,2)}s)")
    ax.axvspan(ta + lag, ta + lag + run_len, color="#ff7f0e", alpha=0.20,
               label=f"repeat window B ({round(ta+lag,2)}-{round(ta+lag+run_len,2)}s, lag={lag}s)")
    ax.set_xlim(0, 6.0)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("RMS (normalized frame energy)")
    ax.set_title("B1 FSP1 narration_solo_full.wav: opening 0-6s RMS envelope + onsets\n"
                 "(red lines = detected onsets, green/orange bands = short-run self-similarity "
                 "repeat candidate at lag≈0.97s)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    out_path = os.path.join(OUT_DIR, "falsestart_rms_envelope.png")
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"saved {out_path}")


def plot_similarity_heatmap():
    narration_path = os.path.join(OUT_DIR, "narration_solo_full.wav")
    data, sr = sf.read(narration_path, always_2d=False)
    mono = data.astype(np.float64) if data.ndim == 1 else data.mean(axis=1)
    slice_end_s = 5.0
    mono = mono[:int(slice_end_s * sr)]

    frame_ms, hop_ms = 25.0, 5.0
    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    window = np.hanning(frame_len)
    spec = np.zeros((n_frames, frame_len // 2 + 1))
    for i in range(n_frames):
        start = i * hop_len
        frame = mono[start:start + frame_len]
        if len(frame) < frame_len:
            frame = np.pad(frame, (0, frame_len - len(frame)))
        spec[i] = np.abs(np.fft.rfft(frame * window))
    logspec = np.log1p(spec)
    norms = np.linalg.norm(logspec, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = logspec / norms
    sim = normed @ normed.T

    t = np.arange(n_frames) * hop_ms / 1000.0
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(sim, origin="lower", extent=[t[0], t[-1], t[0], t[-1]],
                    cmap="viridis", vmin=0.0, vmax=1.0, aspect="equal")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("time (s)")
    ax.set_title("B1 FSP1 narration_solo_full.wav: 0-5s frame self-similarity matrix\n"
                 "(diagonal band off the main diagonal near lag≈0.97s = repeat candidate)")
    fig.colorbar(im, ax=ax, label="cosine similarity")
    # mark the identified diagonal band
    d = json.load(open(EVIDENCE_PATH, encoding="utf-8"))
    src = d["short_run_rescan"]["best_by_threshold"]["0.6"]
    ta = src["time_a"]
    lag = src["lag"]
    run_len = src["run_length_seconds"]
    ax.plot([ta, ta + run_len], [ta + lag, ta + lag + run_len], color="red", linewidth=2,
            label=f"identified repeat run ({run_len}s @ lag={lag}s)")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    out_path = os.path.join(OUT_DIR, "falsestart_similarity_heatmap.png")
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    print(f"saved {out_path}")


if __name__ == "__main__":
    plot_rms_envelope()
    plot_similarity_heatmap()
