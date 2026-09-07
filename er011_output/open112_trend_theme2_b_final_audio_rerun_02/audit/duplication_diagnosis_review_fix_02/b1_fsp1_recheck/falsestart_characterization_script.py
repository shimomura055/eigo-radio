# ============================================================
# falsestart_characterization_script.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 (B1 FSP1 追加特性解析)
# 管理ID: OPEN-112-THEME2-AUDIO-REVIEW-FIX-02(B1 FSP1解析タスク)
# ============================================================
# 目的: ユーザー試聴(2026-09-07)でB1 Full Story Part 1のnarration単体
# 冒頭0〜3秒に「As of Septem, As of September 2026...」という
# partial-word false start(語の途中で切れる短い言い直し)型の重複が
# 実在すると確定した一方、既存の全機械検知手法(全文一括ASR8回・
# windowed再ASR12回・faster-whisper逐語8件・spectral self-similarity・
# cross-correlation)がすべて陰性だった。本スクリプトはその理由を
# 特性解析として記録するための追加診断。
#
# 診断のみ。修正・再生成・Assembly変更・Validator変更は一切行わない。
# Production関数(er006_asr_provider_routing_01.transcribe、
# er003_b1_p4_audio.get_full_text_via_azure_stt_continuous、
# er008_disfluency_qa_18)は無変更のまま呼び出しのみ。Git操作は
# 本タスク側で別途明示ファイルのみstageする。

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "..", ".."))
for _d in [os.getcwd(), _REPO_ROOT]:
    if _d not in sys.path:
        sys.path.insert(0, _d)

import er006_asr_provider_routing_01 as asr_routing
import er008_disfluency_qa_18 as disfluency_qa
import er003_b1_p4_audio as p4

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
NARRATION_SOLO = os.path.join(OUT_DIR, "narration_solo_full.wav")

LOG: list = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


def load_wav(path):
    data, sr = sf.read(path, always_2d=False)
    return data, sr


def write_wav(path, data, sr):
    sf.write(path, data, sr, subtype="PCM_16")


def cut_seconds(data, sr, start_s, end_s):
    start_i = max(0, int(round(start_s * sr)))
    end_i = min(len(data), int(round(end_s * sr)))
    return data[start_i:end_i]


def to_mono(data):
    if data.ndim == 1:
        return data.astype(np.float64)
    return data.mean(axis=1).astype(np.float64)


# ------------------------------------------------------------
# 0. 追加clip切り出し(試聴用+解析用)
# ------------------------------------------------------------
def prepare_clips():
    data, sr = load_wav(NARRATION_SOLO)
    clips = {}
    windows = {
        "opening_0-3s": (0.0, 3.0),
        "opening_0-1.5s": (0.0, 1.5),
        "opening_1.2-3s": (1.2, 3.0),
        "frag_a_0-1.2s": (0.0, 1.2),
        "frag_b_1.2-2.6s": (1.2, 2.6),
        "opening_0-6s": (0.0, 6.0),
    }
    for key, (w0, w1) in windows.items():
        clip = cut_seconds(data, sr, w0, w1)
        path = os.path.join(OUT_DIR, f"falsestart_{key}.wav")
        write_wav(path, clip, sr)
        clips[key] = {"path": path, "start": w0, "end": w1, "sr": sr}
    return clips, data, sr


# ------------------------------------------------------------
# (a) faster-whisper word-level timestamps、複数decodingパラメータ
# ------------------------------------------------------------
def word_level_timestamps(wav_path, model_size="small", beam_size=5, temperature=0.0,
                           condition_on_previous_text=False, best_of=5):
    from faster_whisper import WhisperModel
    model = disfluency_qa._get_model(model_size)
    segments, info = model.transcribe(
        wav_path, word_timestamps=True, language="en",
        beam_size=beam_size, temperature=temperature, best_of=best_of,
        condition_on_previous_text=condition_on_previous_text, vad_filter=False)
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({"text": w.word, "start": round(w.start, 3),
                              "end": round(w.end, 3), "probability": round(w.probability, 3)})
    return words, {"beam_size": beam_size, "temperature": temperature, "best_of": best_of,
                    "condition_on_previous_text": condition_on_previous_text,
                    "language_probability": round(getattr(info, "language_probability", -1) or -1, 3)}


def run_word_timestamp_configs(clip_path, label):
    configs = [
        {"beam_size": 5, "temperature": 0.0},
        {"beam_size": 1, "temperature": 0.0},
        {"beam_size": 5, "temperature": 0.4},
    ]
    results = []
    for cfg in configs:
        t0 = time.time()
        words, meta = word_level_timestamps(clip_path, **cfg)
        dt = time.time() - t0
        text_join = " ".join(w["text"] for w in words).strip()
        results.append({
            "label": label, "config": meta, "elapsed_seconds": round(dt, 2),
            "word_count": len(words), "words": words, "text": text_join,
        })
        log(f"  [WordTS] {label} cfg={meta} -> words={len(words)} text={text_join!r}")
    return results


# ------------------------------------------------------------
# (b) RMS envelope + onset検出(冒頭0-6秒)
# ------------------------------------------------------------
def rms_envelope(mono, sr, frame_ms=20.0, hop_ms=5.0):
    frame_len = int(sr * frame_ms / 1000.0)
    hop_len = int(sr * hop_ms / 1000.0)
    n_frames = 1 + max(0, (len(mono) - frame_len) // hop_len)
    rms = np.zeros(n_frames)
    times = np.zeros(n_frames)
    for i in range(n_frames):
        start = i * hop_len
        frame = mono[start:start + frame_len]
        rms[i] = np.sqrt(np.mean(frame.astype(np.float64) ** 2)) if len(frame) else 0.0
        times[i] = start / sr
    return times, rms


def detect_onsets(times, rms, min_gap_s=0.15):
    if rms.max() <= 0:
        return []
    norm = rms / rms.max()
    diff = np.diff(norm, prepend=norm[0])
    diff[diff < 0] = 0.0
    # adaptive threshold: mean + 1.5*std of positive diffs
    pos = diff[diff > 0]
    thresh = (pos.mean() + 1.5 * pos.std()) if len(pos) else 0.05
    thresh = max(thresh, 0.03)
    onsets = []
    last_t = -999.0
    for i in range(1, len(diff) - 1):
        if diff[i] >= thresh and diff[i] >= diff[i - 1] and diff[i] >= diff[i + 1]:
            t = times[i]
            if t - last_t >= min_gap_s:
                onsets.append({"time": round(float(t), 3), "diff": round(float(diff[i]), 4),
                                "rms_norm": round(float(norm[i]), 4)})
                last_t = t
    return onsets


def run_rms_onset_analysis(mono, sr, label, t_end=6.0):
    seg = mono[:int(t_end * sr)]
    times, rms = rms_envelope(seg, sr)
    onsets = detect_onsets(times, rms)
    log(f"  [RMS/Onset] {label} onsets(<{t_end}s) = {onsets}")
    return {
        "label": label,
        "frame_ms": 20.0, "hop_ms": 5.0,
        "times": [round(float(t), 3) for t in times],
        "rms": [round(float(r), 5) for r in rms],
        "onsets": onsets,
    }


# ------------------------------------------------------------
# (c) 短run再走査(0.3-1.5秒run, 低閾値)
# ------------------------------------------------------------
def spectral_frames(mono, sr, frame_ms=25.0, hop_ms=5.0):
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
    return normed, hop_ms


def short_run_rescan(mono, sr, label, time_a_max=3.0, lag_min=0.3, lag_max=1.5,
                      thresholds=(0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9)):
    # メモリ/計算量削減のため、必要な区間(0〜time_a_max+lag_max+マージン)
    # のみを対象にする(全体sim matrixは不要、i0とi0+lagが収まる範囲だけ)。
    slice_end_s = time_a_max + lag_max + 0.5
    mono = mono[:int(slice_end_s * sr)]
    normed, hop_ms = spectral_frames(mono, sr, frame_ms=25.0, hop_ms=5.0)
    n = normed.shape[0]
    hop_s = hop_ms / 1000.0
    i_max = int(time_a_max / hop_s)
    lag_min_f = int(lag_min / hop_s)
    lag_max_f = int(lag_max / hop_s)

    sim = normed @ normed.T

    # best diagonal run at each threshold, scanning all (i, lag) with i<=i_max
    best_by_thresh = {}
    for thr in thresholds:
        best = {"run_length_seconds": 0.0, "time_a": None, "lag": None}
        for i0 in range(0, min(i_max, n)):
            for lag_f in range(lag_min_f, min(lag_max_f, n - i0) + 1):
                if lag_f <= 0:
                    continue
                # measure run starting at i0 with this lag
                k = 0
                while (i0 + k < n and i0 + k + lag_f < n and
                       sim[i0 + k, i0 + k + lag_f] >= thr):
                    k += 1
                run_s = k * hop_s
                if run_s > best["run_length_seconds"]:
                    best = {"run_length_seconds": round(run_s, 3),
                            "time_a": round(i0 * hop_s, 3),
                            "lag": round(lag_f * hop_s, 3),
                            "similarity_at_start": round(float(sim[i0, i0 + lag_f]), 4)}
        best_by_thresh[str(thr)] = best
        log(f"  [ShortRunRescan] {label} thresh={thr} -> {best}")
    return {"label": label, "hop_ms": hop_ms, "time_a_max": time_a_max,
            "lag_range": [lag_min, lag_max], "best_by_threshold": best_by_thresh}


# ------------------------------------------------------------
# (d) DTW: frag_a(0-1.2s "Septem"想定) vs frag_b(1.2-2.6s "September 2026"想定)
# ------------------------------------------------------------
def dtw_distance(feat_a, feat_b):
    """簡易DTW(cosine距離、対角/水平/垂直遷移)。標準ライブラリ不要の
    numpyのみ実装(追加依存を増やさない)。正規化distance(パス長で割った
    値)と最適パスを返す。"""
    na, nb = feat_a.shape[0], feat_b.shape[0]
    # cosine distance matrix (features already L2-normalized per frame)
    cost = 1.0 - (feat_a @ feat_b.T)
    D = np.full((na + 1, nb + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, na + 1):
        for j in range(1, nb + 1):
            c = cost[i - 1, j - 1]
            D[i, j] = c + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    # backtrack path length
    i, j = na, nb
    path_len = 0
    while i > 0 or j > 0:
        path_len += 1
        choices = []
        if i > 0 and j > 0:
            choices.append((D[i - 1, j - 1], i - 1, j - 1))
        if i > 0:
            choices.append((D[i - 1, j], i - 1, j))
        if j > 0:
            choices.append((D[i, j - 1], i, j - 1))
        choices.sort(key=lambda x: x[0])
        _, i, j = choices[0]
    total = D[na, nb]
    return float(total), float(total / max(path_len, 1)), path_len


def dtw_and_crosscorr_fragments(mono, sr, label):
    frag_a = mono[int(0.0 * sr):int(1.2 * sr)]
    frag_b = mono[int(1.2 * sr):int(2.6 * sr)]
    feat_a, hop_ms = spectral_frames(frag_a, sr, frame_ms=25.0, hop_ms=10.0)
    feat_b, _ = spectral_frames(frag_b, sr, frame_ms=25.0, hop_ms=10.0)
    total, normed, path_len = dtw_distance(feat_a, feat_b)

    # for comparison: DTW of frag_a against a random-ish later window (25-26.2s) as baseline "different speech"
    frag_c = mono[int(25.0 * sr):int(26.2 * sr)]
    feat_c, _ = spectral_frames(frag_c, sr, frame_ms=25.0, hop_ms=10.0)
    total_c, normed_c, path_len_c = dtw_distance(feat_a, feat_c)

    # cross-correlation frag_a against a sliding window across 0-4s (raw waveform)
    search = mono[0:int(4.0 * sr)]
    a = frag_a - frag_a.mean()
    norm_a = np.linalg.norm(a) + 1e-9
    # trivial自己一致(offset=0, frag_a自身)を除外するため、frag_a長の半分
    # 以上ずらした位置から探索する(真の反復候補のみを対象とする)。
    best = {"offset": None, "corr": -2.0}
    min_start = max(1, len(a) // 2)
    step = max(1, sr // 200)  # 5ms step
    for start in range(min_start, len(search) - len(a), step):
        b = search[start:start + len(a)]
        b0 = b - b.mean()
        norm_b = np.linalg.norm(b0) + 1e-9
        c = float(np.dot(a, b0) / (norm_a * norm_b))
        if c > best["corr"]:
            best = {"offset": round(start / sr, 3), "corr": round(c, 4)}

    result = {
        "label": label,
        "dtw_frag_a_vs_frag_b": {"total_cost": round(total, 3), "normalized_cost_per_frame": round(normed, 4),
                                  "path_length": path_len, "frag_a_window": "0.0-1.2s", "frag_b_window": "1.2-2.6s"},
        "dtw_frag_a_vs_baseline_25-26.2s": {"total_cost": round(total_c, 3),
                                             "normalized_cost_per_frame": round(normed_c, 4),
                                             "path_length": path_len_c},
        "crosscorr_frag_a_vs_0-4s_sliding": best,
    }
    log(f"  [DTW/CrossCorr] {label} -> {json.dumps(result, ensure_ascii=False)}")
    return result


# ------------------------------------------------------------
# (e) 0-3秒clipへの生ASR投入(Production Primary/Azure/faster-whisper)
# ------------------------------------------------------------
def run_asr_on_opening(clip_path, n_calls=3):
    results = {}

    # Production Primary ASR (OpenAI gpt-4o-mini-transcribe), no prompt
    no_prompt = []
    for i in range(n_calls):
        text, err = asr_routing.transcribe(clip_path, language="en", prompt=None)
        no_prompt.append({"call": i + 1, "text": text, "error": err})
        log(f"  [OpeningASR no-prompt {i+1}/{n_calls}] -> {text!r} err={err!r}")
    results["production_openai_no_prompt"] = no_prompt

    # Production Primary ASR, with verbatim-style prompt
    style_prompt = ("Transcribe verbatim, including any repeated words or phrases exactly "
                     "as spoken. Do not smooth out repetitions or false starts.")
    with_prompt = []
    for i in range(n_calls):
        text, err = asr_routing.transcribe(clip_path, language="en", prompt=style_prompt)
        with_prompt.append({"call": i + 1, "text": text, "error": err})
        log(f"  [OpeningASR with-prompt {i+1}/{n_calls}] -> {text!r} err={err!r}")
    results["production_openai_with_prompt"] = with_prompt

    # Azure raw (diagnostic only, not Production routing for English)
    azure_calls = []
    for i in range(2):
        try:
            text, err = p4.get_full_text_via_azure_stt_continuous(clip_path, language="en-US", timeout_seconds=30.0)
        except Exception as exc:
            text, err = None, f"exception: {exc}"
        azure_calls.append({"call": i + 1, "text": text, "error": err})
        log(f"  [OpeningASR Azure {i+1}/2] -> {text!r} err={err!r}")
    results["azure_raw"] = azure_calls

    # faster-whisper local verbatim (word-level, several configs) already covered
    # separately via run_word_timestamp_configs(clip_path=opening_0-3s)

    return results


def main():
    log("=== B1 FSP1 false-start特性解析 開始 ===")
    clips, full_data, sr = prepare_clips()
    mono_full = to_mono(full_data)

    log("\n--- (a) faster-whisper word-level timestamps (opening_0-6s) ---")
    word_ts_0_6 = run_word_timestamp_configs(clips["opening_0-6s"]["path"], "opening_0-6s")

    log("\n--- (a2) faster-whisper word-level timestamps (opening_0-3s) ---")
    word_ts_0_3 = run_word_timestamp_configs(clips["opening_0-3s"]["path"], "opening_0-3s")

    log("\n--- (b) RMS envelope + onset検出 (narration full, 0-6s) ---")
    rms_result = run_rms_onset_analysis(mono_full, sr, "narration_solo_full", t_end=6.0)

    log("\n--- (c) 短run再走査 (time_a<=3.0s, lag 0.3-1.5s, 複数閾値) ---")
    short_run_result = short_run_rescan(mono_full, sr, "narration_solo_full")

    log("\n--- (d) DTW + cross-correlation fragments ---")
    dtw_result = dtw_and_crosscorr_fragments(mono_full, sr, "narration_solo_full")

    log("\n--- (e) 0-3秒clip生ASR (Production/Azure) ---")
    asr_opening_result = run_asr_on_opening(clips["opening_0-3s"]["path"])

    out = {
        "clips": {k: {kk: vv for kk, vv in v.items() if kk != "sr"} for k, v in clips.items()},
        "word_timestamps_opening_0-6s": word_ts_0_6,
        "word_timestamps_opening_0-3s": word_ts_0_3,
        "rms_onset_analysis": rms_result,
        "short_run_rescan": short_run_result,
        "dtw_crosscorr": dtw_result,
        "asr_opening_0-3s": asr_opening_result,
    }
    out_path = os.path.join(OUT_DIR, "falsestart_characterization_evidence.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)

    log_path = os.path.join(OUT_DIR, "falsestart_characterization_log.txt")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))

    log("\n=== 完了 ===")
    log(f"evidence: {out_path}")


if __name__ == "__main__":
    main()
