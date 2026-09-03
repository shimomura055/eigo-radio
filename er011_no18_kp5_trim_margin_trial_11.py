# ============================================================
# er011_no18_kp5_trim_margin_trial_11.py
# ER-011-NO18-A2-KP5-TRIM-MARGIN-03-TRIAL-11
# ============================================================
# No.18 A2 Key Phrase rank5「be powered off」の語末/f/が聞こえにくい
# 問題(DIAGNOSTIC-10で調査)について、Key Phrase専用のtrim safety
# margin(現行Production: KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS=0.20秒、
# er003_v1_repro01_main_generate.py)を0.30秒にした場合の比較試聴用
# 音声だけを1件生成するTrial。
#
# Productionの0.20秒は恒久変更しない(このファイルはProduction定数を
# 一切書き換えず、生成呼び出し側の引数としてのみ0.30を渡す)。text・
# TTS model・voice・Key Phrase Minimal instruction(final-sound
# safeguard・function-word reduction込み)・retry上限(Primary最大2回)・
# ASR Validator(secondary_asr cascade)・disfluency gateはすべて
# Production実装(er003_v1_repro01_main_generate.
# generate_narration_snippet_verified_strict)をそのまま再利用し、
# safety_margin_secondsだけを変えるTrial変数として隔離する。
#
# Production経路(review_lock guarded、generate_key_phrase_component_
# verified自体)は呼ばない。out_pathもProduction資産(a2/narration/
# kp5_en.wav)とは別のTrial専用パスにし、既存のProduction音声・
# tts_generation_results.json・Master Audio Storeには一切触れない。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p8a_audio as p8a
import er005_cost_logger as cl
import er008_disfluency_qa_18 as dq18
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er011_output/no18_kp5_trim_margin_trial_11"
AUDIO_DIR = f"{OUT_DIR}/audio"
COST_LOG_PATH = f"{OUT_DIR}/cost_log_trial.jsonl"

TARGET_TEXT = "be powered off"
PRODUCTION_MARGIN_SECONDS = repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS  # 0.20
TRIAL_MARGIN_SECONDS = 0.30

PRODUCTION_ASSET_PATH = (
    "er006_output/pool_pilot_01/pool_n18_notifications_specfix_v2/a2/narration/kp5_en.wav")

MAX_TRIAL_ATTEMPTS = repro01.KEY_PHRASE_MINIMAL_MAX_ATTEMPTS  # Production Primaryと同じ上限(2)


def _acoustic_off_tail_analysis(path: str) -> dict:
    """faster-whisper(ローカル、追加課金なし)の単語タイムスタンプで
    "off"トークンを特定し、その終端からfile末尾までを10ms窓でRMS・
    高域(>4kHz)スペクトル比を測定する(DIAGNOSTIC-10と同一手法)。"""
    words = dq18.transcribe_verbatim(path, language="en", model_size="small")
    samples, sr, channels, _n = common.read_wav_float(path)
    if channels > 1:
        samples = samples.reshape(-1, channels)[:, 0]
    total_dur = len(samples) / sr

    off_tok = None
    for w in words:
        t = w["text"].strip().lower().strip(".,;:!?")
        if t == "off":
            off_tok = w
            break

    out = {
        "file_duration_seconds": round(total_dur, 4),
        "words": [{"text": w["text"], "start": round(w["start"], 3), "end": round(w["end"], 3),
                   "prob": round(w["probability"], 4)} for w in words],
    }
    if off_tok is None:
        out["off_analysis"] = None
        return out

    start_s = max(0.0, off_tok["start"] - 0.03)
    end_s = total_dur
    i0, i1 = int(start_s * sr), int(end_s * sr)
    window = samples[i0:i1]
    win_len = int(sr * 10 / 1000)

    def rms(chunk):
        return float(np.sqrt(np.mean(chunk.astype(np.float64) ** 2))) if len(chunk) else 0.0

    def high_band_ratio(chunk, sr_, cutoff=4000):
        if len(chunk) < 8:
            return None
        spec = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1 / sr_)
        total = spec.sum() + 1e-12
        return float(spec[freqs > cutoff].sum() / total)

    rms_w, hb_w = [], []
    for p in range(0, len(window), win_len):
        chunk = window[p:p + win_len]
        rms_w.append(round(rms(chunk), 5))
        hb = high_band_ratio(chunk, sr)
        hb_w.append(round(hb, 4) if hb is not None else None)

    out["off_analysis"] = {
        "off_start": round(off_tok["start"], 4), "off_end": round(off_tok["end"], 4),
        "off_prob": round(off_tok["probability"], 4),
        "off_duration_ms": round((off_tok["end"] - off_tok["start"]) * 1000, 1),
        "file_end_minus_off_end_ms": round((total_dur - off_tok["end"]) * 1000, 1),
        "rms_10ms_windows": rms_w,
        "high_band_ratio_10ms_windows": hb_w,
        "peak_amplitude_in_window": round(float(np.max(np.abs(window))), 5) if len(window) else None,
    }
    return out


def run_trial() -> dict:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    cl.init_logger(COST_LOG_PATH)

    out_path = f"{AUDIO_DIR}/kp5_en_trial_margin030.wav"
    classification_history: list = []

    with cl.logging_context("no18_kp5_trim_margin_trial_11", "keyphrase_trim_margin_trial"):
        gen = repro01.generate_narration_snippet_verified_strict(
            TARGET_TEXT, "en", out_path, TARGET_TEXT,
            max_attempts=MAX_TRIAL_ATTEMPTS, max_extra_chars=10,
            safety_margin_seconds=TRIAL_MARGIN_SECONDS,
            style_prefix_override=repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX,
            disfluency_qa=True,
        )

    result = {
        "target_text": TARGET_TEXT,
        "production_margin_seconds": PRODUCTION_MARGIN_SECONDS,
        "trial_margin_seconds": TRIAL_MARGIN_SECONDS,
        "instruction_full_text": repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX,
        "production_asset_path": PRODUCTION_ASSET_PATH,
        "trial_asset_path": out_path,
        "generation_result": gen,
    }

    if gen.get("status") == "OK" and os.path.exists(out_path):
        result["trial_sha256"] = p8a.sha256_file(out_path)
        result["trial_acoustic_analysis"] = _acoustic_off_tail_analysis(out_path)
        if os.path.exists(PRODUCTION_ASSET_PATH):
            result["production_acoustic_analysis"] = _acoustic_off_tail_analysis(PRODUCTION_ASSET_PATH)

    with open(f"{OUT_DIR}/trial11_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    r = run_trial()
    print("status:", r["generation_result"].get("status"))
