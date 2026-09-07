# ============================================================
# er011_open112_theme2_point_two_showed_show_diag_02.py
# OPEN-112-THEME2-AUDIO-REVIEW-FIX-02 サブタスクD
# A2 Point Two「showed -> show」ASR不一致の実体分類(A/B/C)診断
# ============================================================
# 目的: 2026-09-07に既にHUMAN_REVIEW_LOCKEDへ到達済みのA2 Point Two
# 再生成2attempt(rerun_02/a2/narration/attempts/point_two_attempt{1,2}_
# custom35d6860b.wav)で、Primary ASRが両attemptとも一貫して
# canonical "showed"をASR "show"と書き起こした事象について、
# (a)実音声で本当に語末/d/が脱落しているか、(b)ASR側の連結・弱化に
# よる誤認識かを、複数ASR経路+windowed再ASR+簡易音響分析で診断する。
#
# 診断のみ(TTS再生成・Assembly・仕様変更は一切行わない、既存Gate/
# 仕様は不変)。Git操作なし(このタスクの管理範囲外)。

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as disfluency_qa
import er011_b1_connected_speech_validator_01 as csv_validator

RERUN02_DIR = "er011_output/open112_trend_theme2_b_final_audio_rerun_02"
ATTEMPTS_DIR = f"{RERUN02_DIR}/a2/narration/attempts"
OUT_DIR = f"{RERUN02_DIR}/audit/point_two_showed_show_diag"

CANONICAL_TEXT = (
    "Young travelers are not one single market. Women aged 29 and under still "
    "showed strong interest in famous tourist places, at about 45%. Gourmet travel "
    "was even higher, at about 52%. This is not the same picture as the male interest "
    "in solo and hobby-based trips. The useful lesson is not that sightseeing is ending. "
    "Different young travelers may be looking for different kinds of value from the same holiday."
)

ATTEMPTS = {
    "attempt1": f"{ATTEMPTS_DIR}/point_two_attempt1_custom35d6860b.wav",
    "attempt2": f"{ATTEMPTS_DIR}/point_two_attempt2_custom35d6860b.wav",
}

os.makedirs(OUT_DIR, exist_ok=True)

LOG: list = []


def log(msg):
    print(msg)
    LOG.append(str(msg))


def sha256_of(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_wav(path):
    data, sr = sf.read(path, always_2d=False)
    return data, sr


def write_wav(path, data, sr):
    sf.write(path, data, sr, subtype="PCM_16")


def to_mono(data):
    if data.ndim == 1:
        return data.astype(np.float64)
    return data.mean(axis=1).astype(np.float64)


def cut_seconds(data, sr, start_s, end_s):
    start_i = max(0, int(round(start_s * sr)))
    end_i = min(len(data), int(round(end_s * sr)))
    return data[start_i:end_i]


# ------------------------------------------------------------
# 1. faster-whisper word-level timestamps (ローカル、無料)
#    "showed"/"show" と次語 "strong" の境界時刻を特定する
# ------------------------------------------------------------
def locate_word_window(path, target_words=("showed", "show"), context_word="strong",
                        pad_before=1.2, pad_after=1.8):
    words = disfluency_qa.transcribe_verbatim(path, language="en", model_size="small")
    norm = [disfluency_qa._normalize_token(w["text"]) for w in words]
    hit_idx = None
    for i, w in enumerate(norm):
        if w in target_words:
            # 次の1-2語以内に"strong"があるかで文脈確認
            nxt = norm[i + 1:i + 3]
            if context_word in nxt:
                hit_idx = i
                break
    if hit_idx is None:
        # フォールバック: target_wordsのみで探す(strongが別語に化けている場合)
        for i, w in enumerate(norm):
            if w in target_words:
                hit_idx = i
                break
    result = {
        "all_words": [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                       "probability": round(w["probability"], 4)} for w in words],
        "hit_index": hit_idx,
    }
    if hit_idx is not None:
        target_w = words[hit_idx]
        next_w = words[hit_idx + 1] if hit_idx + 1 < len(words) else None
        result["target_word"] = {"text": target_w["text"], "start": target_w["start"], "end": target_w["end"]}
        result["next_word"] = ({"text": next_w["text"], "start": next_w["start"], "end": next_w["end"]}
                                if next_w else None)
        win_start = max(0.0, target_w["start"] - pad_before)
        win_end = (next_w["end"] if next_w else target_w["end"]) + pad_after
        result["window_start_seconds"] = round(win_start, 3)
        result["window_end_seconds"] = round(win_end, 3)
    return result


# ------------------------------------------------------------
# 2. Production Primary ASR (windowed, prompt無し/有り)
# ------------------------------------------------------------
def run_production_asr(paths_with_labels, n_calls=1, prompt=None):
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
# 3. Secondary ASR (Azure)
# ------------------------------------------------------------
def run_secondary_asr(paths_with_labels):
    results = []
    for label, path in paths_with_labels:
        t0 = time.time()
        text, err = secondary_asr.get_full_text_via_azure_stt_with_phrase_list(
            path, language="en-US", phrases=["showed"])
        dt = time.time() - t0
        results.append({"label": label, "path": path, "asr_text": text, "error": err,
                         "elapsed_seconds": round(dt, 2)})
        shown = repr(text) if text else repr(err)
        log(f"  [SecondaryASR/Azure] {label} -> {shown}")
    return results


# ------------------------------------------------------------
# 4. faster-whisper local verbatim (windowed)
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
        log(f"  [LocalVerbatim] {label} -> {evidence['transcript']!r}")
    return results


# ------------------------------------------------------------
# 5. 簡易音響分析: "showed"末尾の閉鎖(closure)+破裂(burst)の
#    有無を、細かい時間分解能のRMSエンベロープ+高域エネルギー比で見る。
#    /d/があれば: 母音[ow]の後、短い低エネルギー区間(閉鎖)→短い
#    broadband transient(破裂、burst)→"strong"の/s/摩擦(高域エネルギー
#    持続)という並びが期待される。/d/が完全に脱落していれば、母音から
#    直接/s/摩擦へ連続的に立ち上がるはず(閉鎖区間が見えない)。
#    Agent自身は聴取できないため、ここでは物理量を記述するのみで
#    「発音ミスと断定」はしない(仕様どおり判定はユーザー試聴へ委ねる)。
# ------------------------------------------------------------
def fine_grained_energy_profile(path, start_s, end_s, frame_ms=8.0, hop_ms=2.0):
    data, sr = load_wav(path)
    mono = to_mono(data)
    if np.abs(mono).max() > 0:
        mono = mono / np.abs(mono).max()
    seg = cut_seconds(mono, sr, start_s, end_s)
    frame_len = max(1, int(sr * frame_ms / 1000.0))
    hop_len = max(1, int(sr * hop_ms / 1000.0))
    n_frames = 1 + max(0, (len(seg) - frame_len) // hop_len)
    profile = []
    for i in range(n_frames):
        s = i * hop_len
        frame = seg[s:s + frame_len]
        if len(frame) < frame_len:
            frame = np.pad(frame, (0, frame_len - len(frame)))
        rms = float(np.sqrt(np.mean(frame ** 2)))
        # 高域エネルギー比(/s/のような摩擦音は高域エネルギーが優勢になる)
        spec = np.abs(np.fft.rfft(frame * np.hanning(frame_len)))
        freqs = np.fft.rfftfreq(frame_len, d=1.0 / sr)
        total_e = float(np.sum(spec ** 2)) + 1e-12
        high_e = float(np.sum((spec[freqs >= 4000]) ** 2))
        high_ratio = high_e / total_e
        profile.append({
            "t_seconds": round(start_s + s / sr, 4),
            "rms": round(rms, 5),
            "high_freq_energy_ratio_ge_4kHz": round(high_ratio, 4),
        })
    # 低エネルギー(closure候補)区間を検出(rms < 0.06 かつ 50ms以上持続)
    closure_regions = []
    in_low = False
    region_start = None
    thresh = 0.06
    min_dur = 0.03  # 30ms以上を候補とする(closureは短いため)
    for p in profile:
        if p["rms"] < thresh:
            if not in_low:
                in_low = True
                region_start = p["t_seconds"]
        else:
            if in_low:
                in_low = False
                dur = p["t_seconds"] - region_start
                if dur >= min_dur:
                    closure_regions.append({"start": round(region_start, 4),
                                             "end": round(p["t_seconds"], 4),
                                             "duration": round(dur, 4)})
    return {
        "path": path, "window": [start_s, end_s], "sample_rate": sr,
        "frame_ms": frame_ms, "hop_ms": hop_ms,
        "profile": profile,
        "low_energy_candidate_regions_ge_30ms": closure_regions,
    }


def main():
    cl.init_logger(f"{OUT_DIR}/cost_log.jsonl")
    log("=== A2 Point Two 'showed -> show' 診断 開始 ===")
    log(f"canonical_text(raw TTS input, fix02_regeneration_log.json確認済み): {CANONICAL_TEXT[:140]}...")

    clip_info = {}
    all_targets = []
    window_targets = []

    for label, path in ATTEMPTS.items():
        if not os.path.exists(path):
            log(f"!! attempt wav not found: {path}")
            continue
        sha = sha256_of(path)
        data, sr = load_wav(path)
        dur = len(to_mono(data)) / sr
        log(f"\n--- {label}: {path} (sha256={sha[:16]}..., duration={dur:.3f}s, sr={sr}) ---")

        word_loc = locate_word_window(path)
        log(f"  word timestamps around target: hit_index={word_loc.get('hit_index')} "
            f"target_word={word_loc.get('target_word')} next_word={word_loc.get('next_word')}")

        clip_info[label] = {"path": path, "sha256": sha, "duration_seconds": round(dur, 3),
                             "sample_rate": sr, "word_localization": word_loc}
        all_targets.append((label, path))

        if word_loc.get("hit_index") is not None:
            w0 = word_loc["window_start_seconds"]
            w1 = word_loc["window_end_seconds"]
            win_path = f"{OUT_DIR}/{label}_window_{w0:.2f}-{w1:.2f}s.wav"
            win_clip = cut_seconds(to_mono(data), sr, w0, w1)
            write_wav(win_path, win_clip, sr)
            clip_info[label]["window_path"] = win_path
            clip_info[label]["window_start_seconds"] = w0
            clip_info[label]["window_end_seconds"] = w1
            window_targets.append((f"{label}_window", win_path))

    log("\n--- Production Primary ASR (full attempt clip, no prompt, 既存attempt json記録の確認+再現性チェック) ---")
    prod_asr_full_noprompt = run_production_asr(all_targets, n_calls=1, prompt=None)

    log("\n--- Production Primary ASR (windowed clip, no prompt) ---")
    prod_asr_windowed_noprompt = run_production_asr(window_targets, n_calls=1, prompt=None)

    log("\n--- Production Primary ASR (windowed clip, 中立promptあり[canonical answerを含まない]) ---")
    neutral_prompt = ("This is a short clip from an English podcast about travel trends. "
                       "Transcribe exactly what is spoken, including word endings.")
    prod_asr_windowed_prompt = run_production_asr(window_targets, n_calls=1, prompt=neutral_prompt)

    log("\n--- Secondary ASR (Azure, full clip + windowed clip) ---")
    secondary_full = run_secondary_asr(all_targets)
    secondary_windowed = run_secondary_asr(window_targets)

    log("\n--- faster-whisper local verbatim (独立した第3のASR、full + windowed) ---")
    local_full = run_local_verbatim(all_targets)
    local_windowed = run_local_verbatim(window_targets)

    log("\n--- 簡易音響分析(語境界の低エネルギー[closure候補]区間+高域エネルギー比) ---")
    acoustic_results = {}
    for label in ATTEMPTS:
        if label not in clip_info or "window_start_seconds" not in clip_info[label]:
            continue
        path = clip_info[label]["path"]
        tw = clip_info[label]["word_localization"]["target_word"]
        nw = clip_info[label]["word_localization"]["next_word"]
        # target_wordの終端0.3秒前からnext_wordの開始0.3秒後までを詳細分析
        a_start = max(0.0, tw["start"] - 0.15)
        a_end = (nw["start"] if nw else tw["end"]) + 0.35
        acoustic_results[label] = fine_grained_energy_profile(path, a_start, a_end)
        cregs = acoustic_results[label]["low_energy_candidate_regions_ge_30ms"]
        log(f"  [{label}] window=({a_start:.3f},{a_end:.3f}) low_energy_regions={cregs}")

    # ------------------------------------------------------------
    # Connected Speech Validator (既存Production関数、無変更)適用結果の
    # 再現(このcanonical/asr差分がPattern A/B/Cに該当するかどうか)
    # ------------------------------------------------------------
    log("\n--- Connected Speech Validator再現(既存関数、無変更呼び出し) ---")
    csv_result = csv_validator.classify_connected_speech(
        "still showed strong interest",
        "still show strong interest")
    log(json.dumps(csv_result, ensure_ascii=False, indent=2))

    out = {
        "canonical_text": CANONICAL_TEXT,
        "clip_info": clip_info,
        "production_asr_full_noprompt": prod_asr_full_noprompt,
        "production_asr_windowed_noprompt": prod_asr_windowed_noprompt,
        "production_asr_windowed_prompt": prod_asr_windowed_prompt,
        "secondary_asr_full": secondary_full,
        "secondary_asr_windowed": secondary_windowed,
        "local_verbatim_full": local_full,
        "local_verbatim_windowed": local_windowed,
        "acoustic_energy_profile": acoustic_results,
        "connected_speech_validator_replay": csv_result,
    }
    with open(f"{OUT_DIR}/diag_raw_evidence.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/diag_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(LOG))

    log("\n=== 完了 ===")
    log(f"raw evidence: {OUT_DIR}/diag_raw_evidence.json")


if __name__ == "__main__":
    main()
