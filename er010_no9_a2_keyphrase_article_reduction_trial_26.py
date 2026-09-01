# ============================================================
# er010_no9_a2_keyphrase_article_reduction_trial_26.py
# ER-010-NO9-A2-KEYPHRASE-ARTICLE-REDUCTION-DIAGNOSTIC-AND-TRIAL-26
# ============================================================
# ユーザー試聴フィードバック: No.9 A2 Key Phrase「a catch」で冠詞
# "a"が独立した強勢語のように強く・長く発音されている("アー キャッチ")。
#
# 現行Production Key Phrase Minimal instruction(er003_v1_repro01_
# main_generate.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX)には、function
# word(冠詞等)を弱く・短く読むという原則が存在しない(CURRENT_SPEC.md・
# DECISION_LOG.md監査で確認、article reductionへの言及は見つからず)。
# したがってこれは既存仕様の実装漏れではなく、新しいpronunciation
# safeguard候補として扱う。
#
# 本Trialは対象を"a catch"のみに隔離し、Production本番pathを一切
# 変更しない。既存Minimal instructionの文言は一切削除・変更せず、
# 末尾にfunction-word reduction原則を追加するだけ(ENGLISH_LOCK
# suffixと同じAND方式)。article/function wordという一般原則として
# 設計し、"a catch"や"a"という文字列だけへの特殊処理にはしない。
#
# Production経路(review_lock guarded)は一切呼ばない。TTSモデル・
# voice・trim margin・duration anomaly検知・ASR Validator(secondary_asr
# cascade)・disfluency gateは、Production実装をそのまま再利用し、
# style instructionだけを差し替える(Trial 21と同じ設計方針)。

from __future__ import annotations

import json
import os

import numpy as np

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er006_pronunciation_ledger_01 as pronun_ledger
import er006_secondary_asr_01 as secondary_asr
import er008_disfluency_qa_18 as dq18
import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er010_output/no9_a2_keyphrase_article_reduction_trial_26"
AUDIO_DIR = f"{OUT_DIR}/audio"
QUARANTINE_DIR = f"{OUT_DIR}/quarantine"
COST_LOG_PATH = f"{OUT_DIR}/cost_log_trial.jsonl"

TARGET_KEY_PHRASE = "a catch"
TARGET_JAPANESE_GLOSS = "落とし穴、ただし書き"

MAX_TRIAL_ATTEMPTS = 3  # 1回目を実施し、NG/異常時のみ最大2回追加(合計3)

CURRENT_PRODUCTION_INSTRUCTION = repro01.KEY_PHRASE_MINIMAL_INSTRUCTION_PREFIX

# 既存Minimal instructionの文言は一切変更せず、末尾に一般原則として
# function-word reduction指示を追加するだけ(ENGLISH_LOCK_SUFFIXと同じ
# AND方式)。「a catch」や「a」という文字列への特殊処理ではなく、
# article/function word全般への一般原則として記述する。
FUNCTION_WORD_REDUCTION_SUFFIX = (
    "In natural spoken English, short function words such as articles "
    "(\"a\", \"an\", \"the\") are usually spoken briefly and without stress, "
    "connecting smoothly into the word that follows, while the main content "
    "word carries the natural stress of the phrase. If the phrase contains "
    "such a function word, keep it light and unstressed, and let it flow "
    "naturally into the following word, rather than pronouncing it as its "
    "own separate, stressed beat. Do not omit or drop the function word — "
    "only make it light and unstressed, not silent, and do not let this "
    "affect how clearly the rest of the phrase is spoken.\n\n"
)
TRIAL_INSTRUCTION = CURRENT_PRODUCTION_INSTRUCTION + FUNCTION_WORD_REDUCTION_SUFFIX

KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS


def _measure_word_envelope(path: str) -> dict:
    """簡易envelope解析(10ms窓RMS、閾値=peakの8%)。formal な音響解析
    ではなく、articleとcontent wordのduration/energyバランスを客観的に
    比較するための補助情報(spec section 11「過度な音響解析は不要」)。"""
    samples, sr, channels, _nframes = common.read_wav_float(path)
    if channels > 1:
        samples = samples.reshape(-1, channels)
        samples = samples[:, 0]
    win = max(1, int(sr * 0.01))
    n_win = len(samples) // win
    if n_win == 0:
        return {"runs": [], "note": "音声が短すぎてenvelope解析不可"}
    env = np.array([np.sqrt(np.mean(samples[i * win:(i + 1) * win] ** 2)) for i in range(n_win)])
    peak = float(env.max()) if len(env) else 0.0
    if peak <= 0:
        return {"runs": [], "note": "無音"}
    thresh = peak * 0.08
    speech = env > thresh
    runs = []
    in_run = False
    start = 0
    for i, s in enumerate(speech):
        if s and not in_run:
            start = i
            in_run = True
        if not s and in_run:
            runs.append((start, i))
            in_run = False
    if in_run:
        runs.append((start, len(speech)))
    run_info = []
    for r in runs:
        seg = env[r[0]:r[1]]
        run_info.append({
            "start_seconds": round(r[0] * 0.01, 3), "end_seconds": round(r[1] * 0.01, 3),
            "duration_seconds": round((r[1] - r[0]) * 0.01, 3),
            "peak_rms": round(float(seg.max()), 4), "mean_rms": round(float(seg.mean()), 4),
        })
    return {"runs": run_info, "peak_rms_overall": round(peak, 4), "num_runs": len(run_info)}


def _run_one_attempt(text: str, out_name: str, attempt_no: int,
                      instruction: str, classification_history: list) -> dict:
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}.wav"

    prompt = p4c.build_tts_prompt(text, instruction)
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"attempt": attempt_no, "status": "STOPPED", "verified": False, "stop_retrying": False,
                "reason": f"TTS技術的失敗: {err}", "instruction_full_text": instruction,
                "audio_path": None, "is_quarantine": False}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"attempt": attempt_no, "status": "STOPPED", "verified": False, "stop_retrying": False,
                "reason": "発話区間を検出できませんでした", "instruction_full_text": instruction,
                "audio_path": None, "is_quarantine": False}

    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        q_path = f"{QUARANTINE_DIR}/{out_name}_anomaly.wav"
        common.write_wav_float(q_path, samples_raw, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(q_path, language="en-US")
        return {
            "attempt": attempt_no, "status": "STOPPED", "verified": False, "stop_retrying": False,
            "reason": anomaly["reason"], "duration_anomaly": anomaly,
            "raw_duration_seconds": trim_info["raw_duration_seconds"], "instruction_full_text": instruction,
            "audio_path": q_path, "is_quarantine": True, "asr_text": asr_text, "asr_error": asr_err,
            "call_count": 1 + retries, "retry_count": retries,
        }

    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    asr_text, asr_err = routing.transcribe(out_path, language="en-US")
    max_len = len(text) + 10
    length_ok = asr_text is not None and len(asr_text) <= max_len

    ledger_phrases = [h["canonical_spelling"] for h in pronun_ledger.get_hint_for_text(text, min_confidence="low")]
    verified_content, stop_retrying, cls = secondary_asr.evaluate_attempt_with_cascade(
        text, asr_text, classification_history, out_path, language="en-US",
        ledger_phrases=ledger_phrases, cascade_enabled=secondary_asr.FEATURE_FLAG_SECONDARY_ASR_ENABLED)
    verified = verified_content and length_ok
    gate = dq18.apply_disfluency_gate(verified, out_path, language="en", enabled=True)
    verified = gate["verified"]
    classification_history.append(cls)

    envelope = _measure_word_envelope(out_path)

    return {
        "attempt": attempt_no, "status": "OK", "verified": verified, "stop_retrying": stop_retrying,
        "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "raw_duration_seconds": trim_info["raw_duration_seconds"],
        "duration_anomaly": anomaly, "clipping_detected": metrics["clipping_detected"],
        "asr_text": asr_text, "asr_error": asr_err, "length_ok": length_ok,
        "audio_classification": cls.classification, "classification_reason": cls.reason,
        "disfluency_checked": gate["disfluency_checked"], "disfluency_evidence": gate.get("disfluency_evidence"),
        "instruction_full_text": instruction, "audio_path": out_path, "is_quarantine": False,
        "call_count": 1 + retries, "retry_count": retries, "sha256": p8a.sha256_file(out_path),
        "envelope_analysis": envelope,
    }


def run_trial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.init_logger(COST_LOG_PATH)
    text = TARGET_KEY_PHRASE
    classification_history: list = []
    attempts = []
    final_status = None

    current_production_path = (
        "er006_output/pool_pilot_01/pool_n9_tip_screens/a2/narration/kp4_en.wav")
    current_production_envelope = (
        _measure_word_envelope(current_production_path)
        if os.path.exists(current_production_path) else None)

    with cl.logging_context("no9_a2_keyphrase_article_reduction_trial_26", "keyphrase_article_reduction_trial"):
        for n in range(1, MAX_TRIAL_ATTEMPTS + 1):
            out_name = f"a_catch_functionword_attempt{n}"
            rec = _run_one_attempt(text, out_name, n, TRIAL_INSTRUCTION, classification_history)
            attempts.append(rec)
            if rec["verified"]:
                final_status = f"PASS_ON_ATTEMPT_{n}"
                break
            if rec.get("stop_retrying"):
                final_status = f"STOPPED_UNCERTAIN_ATTEMPT_{n}"
                break
        else:
            final_status = f"FAIL_AFTER_{MAX_TRIAL_ATTEMPTS}_ATTEMPTS"

    result = {
        "key_phrase": text,
        "japanese_gloss": TARGET_JAPANESE_GLOSS,
        "current_production_instruction_full_text": CURRENT_PRODUCTION_INSTRUCTION,
        "trial_instruction_full_text": TRIAL_INSTRUCTION,
        "function_word_reduction_suffix_added": FUNCTION_WORD_REDUCTION_SUFFIX,
        "current_production_audio_path": current_production_path,
        "current_production_envelope_analysis": current_production_envelope,
        "final_status": final_status,
        "total_actual_calls": len(attempts),
        "attempts": attempts,
    }

    with open(f"{OUT_DIR}/trial26_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    run_trial()
