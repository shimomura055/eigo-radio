# ============================================================
# er011_open112_theme2_b1_fsp1_recheck_02.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 差し戻し1回目
# B1 Full Story Part 1「As of Septem, As of September 2026...」再検証
# ============================================================
# 目的: 前回(OPEN-112-THEME2-AUDIO-REVIEW-FIX-02サブタスクA)は
# B1 Full Story Part 1の重複を「現物で再現できず」と結論したが、
# 同レポート内でA2 Point Twoは全文一括ASRを8回かけても一度も検知
# できず、6〜22秒のwindowed再ASR+spectral self-similarityで初めて
# 確認できたと記録されている。B1にも同じ厳密な手法を適用したかが
# 不明なため、本スクリプトで同一手法をB1 Full Story Part 1へ適用する。
#
# 診断のみ(修正・再生成・Assembly変更は一切行わない、既存Gate/仕様は
# 不変)。Git操作なし(このタスクの管理範囲外)。

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er006_asr_provider_routing_01 as asr_routing
import er008_disfluency_qa_18 as disfluency_qa

RERUN02_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02"
TRIAL13_DIR = "er011_output/open112_trend_theme2_b_full_audio_trial_13"
OUT_DIR = f"{RERUN02_DIR}/audit/duplication_diagnosis_review_fix_02/b1_fsp1_recheck"

NARRATION_SOLO = f"{RERUN02_DIR}/b1b/narration/full_story_part1.wav"
TRIAL13_NARRATION = f"{TRIAL13_DIR}/b1b/narration/full_story_part1.wav"
ASSEMBLED_EPISODE = (f"{RERUN02_DIR}/b1b/assembled/"
                     "English_Your_Way_B1B_OPEN112_TREND_THEME2_B_FINAL_AUDIO_RERUN_02.wav")
TIMELINE_PATH = f"{RERUN02_DIR}/b1b/audit/timeline.json"

os.makedirs(OUT_DIR, exist_ok=True)

LOG: list = []


def log(msg):
    print(msg)
    LOG.append(msg)


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


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
# 1. timeline整合チェック
# ------------------------------------------------------------
def check_timeline():
    timeline = json.load(open(TIMELINE_PATH, encoding="utf-8"))
    names = [p["part"] for p in timeline]
    dup_names = [n for n in names if names.count(n) > 1]
    fsp1 = [p for p in timeline if p["part"] == "Full Story Part 1 (Aoede)"]
    total_end = timeline[-1]["start_seconds"] + timeline[-1]["duration_seconds"]
    result = {
        "piece_count": len(timeline),
        "duplicate_part_names": sorted(set(dup_names)),
        "full_story_part1_entries": fsp1,
        "computed_total_duration": round(total_end, 3),
    }
    return result, timeline


# ------------------------------------------------------------
# 2. 音声切り出し
# ------------------------------------------------------------
def prepare_clips(timeline):
    fsp1 = [p for p in timeline if p["part"] == "Full Story Part 1 (Aoede)"][0]
    seg_start = fsp1["start_seconds"]
    seg_dur = fsp1["duration_seconds"]
    seg_end = seg_start + seg_dur

    # (a) narration単体wav(rerun-02使用の実体、コピー)
    narr_data, narr_sr = load_wav(NARRATION_SOLO)
    narr_path = f"{OUT_DIR}/narration_solo_full.wav"
    write_wav(narr_path, narr_data, narr_sr)

    # (b) episode該当区間、前後3秒込み
    ep_data, ep_sr = load_wav(ASSEMBLED_EPISODE)
    pad = 3.0
    cut_start = max(0.0, seg_start - pad)
    cut_end = seg_end + pad
    ep_cut = cut_seconds(ep_data, ep_sr, cut_start, cut_end)
    ep_cut_path = f"{OUT_DIR}/episode_extract_padded3s.wav"
    write_wav(ep_cut_path, ep_cut, ep_sr)

    # segment自体(パディング無し)を episode から厳密に切り出したもの
    ep_exact = cut_seconds(ep_data, ep_sr, seg_start, seg_end)
    ep_exact_path = f"{OUT_DIR}/episode_extract_exact_segment.wav"
    write_wav(ep_exact_path, ep_exact, ep_sr)

    info = {
        "segment_start_seconds": seg_start,
        "segment_duration_seconds": seg_dur,
        "segment_end_seconds": seg_end,
        "episode_padded_cut_start_seconds": cut_start,
        "episode_padded_cut_end_seconds": cut_end,
        "episode_sample_rate": ep_sr,
        "narration_sample_rate": narr_sr,
        "narration_duration_seconds": len(narr_data) / narr_sr,
        "narration_solo_path": narr_path,
        "episode_padded_path": ep_cut_path,
        "episode_exact_path": ep_exact_path,
        "narration_solo_sha256": sha256_of(NARRATION_SOLO),
        "trial13_narration_sha256": sha256_of(TRIAL13_NARRATION),
        "sha256_match_trial13": sha256_of(NARRATION_SOLO) == sha256_of(TRIAL13_NARRATION),
    }

    # windowed clips (narration solo, offset 0 = segment start)
    windows = [(0.0, 6.0), (0.0, 10.0), (3.0, 12.0)]
    window_paths = {"narration_solo": {}, "episode_padded": {}}
    for (w0, w1) in windows:
        key = f"{w0:g}-{w1:g}s"
        clip = cut_seconds(narr_data, narr_sr, w0, w1)
        p = f"{OUT_DIR}/window_narration_{key}.wav"
        write_wav(p, clip, narr_sr)
        window_paths["narration_solo"][key] = p

        # episode_padded: segment starts at t=pad within the padded cut
        ep_clip = cut_seconds(ep_cut, ep_sr, pad + w0, pad + w1)
        p2 = f"{OUT_DIR}/window_episode_{key}.wav"
        write_wav(p2, ep_clip, ep_sr)
        window_paths["episode_padded"][key] = p2

    info["window_paths"] = window_paths
    return info


# ------------------------------------------------------------
# 3. Production Primary ASR (windowed + full, multi-call)
# ------------------------------------------------------------
def run_production_asr(paths_with_labels, n_calls=4, prompt=None):
    results = []
    for label, path in paths_with_labels:
        for i in range(n_calls):
            t0 = time.time()
            text, err = asr_routing.transcribe(path, language="en", prompt=prompt)
            dt = time.time() - t0
            results.append({
                "label": label, "path": path, "call_index": i + 1,
                "prompt_used": bool(prompt), "asr_text": text, "error": err,
                "elapsed_seconds": round(dt, 2),
            })
            shown = repr(text) if text else repr(err)
            log(f"  [ProdASR call {i+1}/{n_calls}] {label} prompt={bool(prompt)} -> {shown}")
    return results


# ------------------------------------------------------------
# 4. faster-whisper local verbatim
# ------------------------------------------------------------
def run_local_verbatim(paths_with_labels):
    results = []
    for label, path in paths_with_labels:
        t0 = time.time()
        evidence = disfluency_qa.check_segment_for_disfluency(path, language="en", model_size="small")
        dt = time.time() - t0
        evidence["label"] = label
        evidence["path"] = path
        evidence["elapsed_seconds"] = round(dt, 2)
        results.append(evidence)
        log(f"  [LocalVerbatim] {label} flagged={evidence['flagged']} "
            f"repeats={len(evidence['repeats'])} words={evidence['word_count']}")
    return results


# ------------------------------------------------------------
# 5. Spectral self-similarity (Point Twoで使用した手法と同一設計)
# ------------------------------------------------------------
def spectral_self_similarity(path, frame_ms=25.0, hop_ms=10.0, min_lag_s=1.0, top_k=5):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if mono.max() > 0:
        mono = mono / (np.abs(mono).max() + 1e-9)

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

    # log-magnitude + normalize each frame vector
    logspec = np.log1p(spec)
    norms = np.linalg.norm(logspec, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    normed = logspec / norms

    sim = normed @ normed.T  # cosine similarity matrix (n_frames x n_frames)

    min_lag_frames = int(min_lag_s * 1000.0 / hop_ms)
    n = sim.shape[0]
    candidates = []
    for i in range(n):
        for j in range(i + min_lag_frames, n):
            candidates.append((sim[i, j], i, j))
    candidates.sort(key=lambda x: -x[0])

    top = []
    seen_pairs = set()
    for score, i, j in candidates:
        key = (i // 20, j // 20)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        top.append({
            "similarity": round(float(score), 4),
            "time_a_seconds": round(i * hop_ms / 1000.0, 3),
            "time_b_seconds": round(j * hop_ms / 1000.0, 3),
            "lag_seconds": round((j - i) * hop_ms / 1000.0, 3),
        })
        if len(top) >= top_k:
            break

    # run-length estimate around the best match: how long does high similarity
    # persist along the diagonal offset (j - i fixed)?
    run_lengths = []
    for entry in top[:3]:
        i0 = int(round(entry["time_a_seconds"] * 1000.0 / hop_ms))
        lag = int(round(entry["lag_seconds"] * 1000.0 / hop_ms))
        threshold = 0.85
        # extend forward
        k = 0
        while (i0 + k < n and i0 + k + lag < n and
               sim[i0 + k, i0 + k + lag] >= threshold):
            k += 1
        run_len_s = round(k * hop_ms / 1000.0, 3)
        run_lengths.append(run_len_s)
    for idx, rl in enumerate(run_lengths):
        top[idx]["run_length_seconds_at_thresh_0.85"] = rl

    return {
        "path": path,
        "sample_rate": sr,
        "duration_seconds": round(len(mono) / sr, 3),
        "frame_ms": frame_ms, "hop_ms": hop_ms, "min_lag_seconds": min_lag_s,
        "top_matches": top,
    }


def cross_correlation_2_4_vs_4_8(path):
    data, sr = load_wav(path)
    mono = to_mono(data)
    seg_a = mono[int(2 * sr):int(4 * sr)]
    seg_b = mono[int(4 * sr):int(8 * sr)]
    if len(seg_a) == 0 or len(seg_b) == 0:
        return {"path": path, "error": "insufficient length for 2-4s/4-8s window"}
    a = seg_a - seg_a.mean()
    b = seg_b - seg_b.mean()
    corr = np.correlate(b, a, mode="valid")
    denom = (np.linalg.norm(a) * np.linalg.norm(seg_a[:len(a)]) + 1e-9)
    norm_a = np.linalg.norm(a) + 1e-9
    norm_b_running = np.sqrt(np.convolve(b ** 2, np.ones(len(a)), mode="valid")) + 1e-9
    normalized_corr = corr / (norm_a * norm_b_running)
    best_idx = int(np.argmax(np.abs(normalized_corr)))
    return {
        "path": path,
        "sample_rate": sr,
        "seg_a_window": "2.0-4.0s", "seg_b_window": "4.0-8.0s",
        "best_offset_within_b_seconds": round(best_idx / sr, 3),
        "max_normalized_correlation": round(float(normalized_corr[best_idx]), 4),
    }


def silence_positions(path, thresh_rms=0.01, frame_ms=50.0):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if np.abs(mono).max() > 0:
        mono = mono / np.abs(mono).max()
    frame_len = int(sr * frame_ms / 1000.0)
    n_frames = len(mono) // frame_len
    silent_regions = []
    in_silence = False
    region_start = None
    for i in range(n_frames):
        frame = mono[i * frame_len:(i + 1) * frame_len]
        rms = float(np.sqrt(np.mean(frame ** 2)))
        t = i * frame_len / sr
        if rms < thresh_rms:
            if not in_silence:
                in_silence = True
                region_start = t
        else:
            if in_silence:
                in_silence = False
                if t - region_start >= 0.15:
                    silent_regions.append({"start": round(region_start, 3), "end": round(t, 3)})
    return {"path": path, "silent_regions_ge_150ms": silent_regions}


def main():
    log("=== B1 Full Story Part 1 再検証 開始 ===")

    log("\n--- 1. timeline整合チェック ---")
    timeline_result, timeline = check_timeline()
    log(json.dumps(timeline_result, ensure_ascii=False, indent=2, default=str))

    log("\n--- 2. 音声切り出し ---")
    clip_info = prepare_clips(timeline)
    log(json.dumps({k: v for k, v in clip_info.items() if k != "window_paths"},
                    ensure_ascii=False, indent=2))

    all_targets = [
        ("narration_solo_full", clip_info["narration_solo_path"]),
        ("episode_exact_segment", clip_info["episode_exact_path"]),
    ]
    window_targets = []
    for src, wins in clip_info["window_paths"].items():
        for wkey, wpath in wins.items():
            window_targets.append((f"{src}_{wkey}", wpath))

    log("\n--- 3. Production Primary ASR (full file, 4回 x no-prompt) ---")
    prod_asr_full_noprompt = run_production_asr(all_targets, n_calls=4, prompt=None)

    log("\n--- 3b. Production Primary ASR (windowed clips, 各1回 x no-prompt) ---")
    prod_asr_windowed_noprompt = run_production_asr(window_targets, n_calls=1, prompt=None)

    log("\n--- 3c. Production Primary ASR (windowed clips, 各1回 x prompt有り) ---")
    style_prompt = ("Transcribe verbatim, including any repeated words or phrases exactly "
                     "as spoken. Do not smooth out repetitions or false starts.")
    prod_asr_windowed_prompt = run_production_asr(window_targets, n_calls=1, prompt=style_prompt)

    log("\n--- 4. faster-whisper local verbatim ---")
    local_verbatim_full = run_local_verbatim(all_targets)
    local_verbatim_windowed = run_local_verbatim(window_targets)

    log("\n--- 5. spectral self-similarity ---")
    spectral_results = {}
    for label, path in all_targets:
        log(f"  computing self-similarity for {label} ...")
        spectral_results[label] = spectral_self_similarity(path)
        log(json.dumps(spectral_results[label]["top_matches"], ensure_ascii=False, indent=2))

    log("\n--- 6. cross-correlation 2-4s vs 4-8s ---")
    crosscorr_results = {}
    for label, path in all_targets:
        crosscorr_results[label] = cross_correlation_2_4_vs_4_8(path)
        log(json.dumps(crosscorr_results[label], ensure_ascii=False, indent=2))

    log("\n--- 7. silence positions ---")
    silence_results = {}
    for label, path in all_targets:
        silence_results[label] = silence_positions(path)
        log(json.dumps(silence_results[label], ensure_ascii=False, indent=2))

    out = {
        "timeline_check": timeline_result,
        "clip_info": clip_info,
        "production_asr_full_noprompt_x4": prod_asr_full_noprompt,
        "production_asr_windowed_noprompt": prod_asr_windowed_noprompt,
        "production_asr_windowed_prompt": prod_asr_windowed_prompt,
        "local_verbatim_full": local_verbatim_full,
        "local_verbatim_windowed": local_verbatim_windowed,
        "spectral_self_similarity": spectral_results,
        "cross_correlation": crosscorr_results,
        "silence_positions": silence_results,
    }
    with open(f"{OUT_DIR}/recheck_raw_evidence.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/recheck_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))

    log("\n=== 完了 ===")
    log(f"raw evidence: {OUT_DIR}/recheck_raw_evidence.json")


if __name__ == "__main__":
    main()
