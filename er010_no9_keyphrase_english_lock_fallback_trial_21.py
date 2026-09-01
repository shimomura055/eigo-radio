# ============================================================
# er010_no9_keyphrase_english_lock_fallback_trial_21.py
# ER-010-NO9-KEYPHRASE-ENGLISH-LOCK-FALLBACK-TRIAL-21
# ============================================================
# OPEN-103のTrial 21専用モジュール。対象は"default"1語のみ。
#
# 量産候補retry仕様(今回はTrialのみ、Production未配線):
#   Minimal instruction        最大2 attempt
#     ↓ 2attemptともNG
#   Minimal + English language lock  最大2 attempt
#   合計最大4 TTS calls、PASSした時点で即終了。
#
# Minimal instruction本文はMini-Trial 20-R2(
# er010_no9_keyphrase_minimal_instruction_minitrial_20_r2.py::
# MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2)から一字一句変更せず踏襲する。
#
# English language lockは、Mini-Trial 20-R2で"default"がASR上
# 日本語カタカナ("デフォルト")・中国語("默认")として書き起こされた
# (=TTSが英語以外の言語として発話した可能性が高い)という実測結果を
# 受け、対象語を英語の単語として発話するよう明示する一文のみを追加する
# fallbackとして設計した。既存のfinal consonant/ending sound/自然さ/
# phrase一体感/1回のみ発話/commentary禁止といった既存pronunciation
# safeguardsは一切削除せず、English lockはAND(追加)として重ねる。
#
# Production経路(review_lock.guarded_generate系)は一切呼ばない。
# TTSモデル・voice・trim margin・duration anomaly検知・ASR Validator
# (secondary_asr cascade)・disfluency gateは、すべてProductionが実際に
# 使っているのと同一の関数をそのまま再利用し、style instructionだけを
# Minimal / Minimal+English-Lockに差し替える。review_lockのretry count/
# review lockには一切触れない。

from __future__ import annotations

import json
import os

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
import er010_no9_keyphrase_minimal_instruction_minitrial_20_r2 as minitrial20r2

OUT_DIR = "er010_output/no9_keyphrase_english_lock_fallback_trial_21"
AUDIO_DIR = f"{OUT_DIR}/audio"
QUARANTINE_DIR = f"{OUT_DIR}/quarantine"
COST_LOG_PATH = f"{OUT_DIR}/cost_log_trial.jsonl"

TARGET_KEY_PHRASE = "default"
TARGET_JAPANESE_GLOSS = "初期設定の選択肢"

MAX_MINIMAL_ATTEMPTS = 2
MAX_ENGLISH_LOCK_ATTEMPTS = 2

# Mini-Trial 20-R2から無変更で踏襲。
MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2 = minitrial20r2.MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2

# Minimal instructionの末尾に、英語の単語として発話することを明示する
# 一文のみを追加する。既存文言(explanation禁止/1回のみ/自然で明瞭/
# 語末音保持/phrase一体感)は一切変更せず、そのまま先頭に維持する。
ENGLISH_LANGUAGE_LOCK_SUFFIX = (
    "Pronounce the phrase specifically as an English word or phrase, "
    "using English pronunciation throughout — not as a Japanese, Chinese, "
    "or other non-English reading of it.\n\n"
)
ENGLISH_LOCK_INSTRUCTION = MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2 + ENGLISH_LANGUAGE_LOCK_SUFFIX

KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS


def _run_one_attempt(text: str, out_name: str, attempt_type: str, attempt_no: int,
                      instruction: str, classification_history: list) -> dict:
    """Production同一のTTS呼び出し・trim・duration anomaly検知・ASR
    Validator(secondary_asr cascade)・disfluency gateを、指定された
    instructionで1回だけ実行する。review_lockには一切触れない。"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}.wav"

    prompt = p4c.build_tts_prompt(text, instruction)
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"attempt_type": attempt_type, "attempt": attempt_no, "status": "STOPPED",
                "verified": False, "stop_retrying": False,
                "reason": f"TTS技術的失敗: {err}", "instruction_full_text": instruction,
                "audio_path": None, "is_quarantine": False}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"attempt_type": attempt_type, "attempt": attempt_no, "status": "STOPPED",
                "verified": False, "stop_retrying": False,
                "reason": "発話区間を検出できませんでした", "instruction_full_text": instruction,
                "audio_path": None, "is_quarantine": False}

    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        q_path = f"{QUARANTINE_DIR}/{out_name}_anomaly.wav"
        common.write_wav_float(q_path, samples_raw, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(q_path, language="en-US")
        return {
            "attempt_type": attempt_type, "attempt": attempt_no, "status": "STOPPED",
            "verified": False, "stop_retrying": False,
            "reason": anomaly["reason"], "duration_anomaly": anomaly,
            "raw_duration_seconds": trim_info["raw_duration_seconds"],
            "instruction_full_text": instruction,
            "audio_path": q_path, "is_quarantine": True,
            "asr_text": asr_text, "asr_error": asr_err,
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

    return {
        "attempt_type": attempt_type, "attempt": attempt_no, "status": "OK",
        "verified": verified, "stop_retrying": stop_retrying,
        "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "raw_duration_seconds": trim_info["raw_duration_seconds"],
        "duration_anomaly": anomaly, "clipping_detected": metrics["clipping_detected"],
        "asr_text": asr_text, "asr_error": asr_err, "length_ok": length_ok,
        "audio_classification": cls.classification, "classification_reason": cls.reason,
        "disfluency_checked": gate["disfluency_checked"], "disfluency_evidence": gate.get("disfluency_evidence"),
        "instruction_full_text": instruction,
        "audio_path": out_path, "is_quarantine": False,
        "call_count": 1 + retries, "retry_count": retries,
        "sha256": p8a.sha256_file(out_path),
    }


def run_english_lock_fallback_trial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.init_logger(COST_LOG_PATH)
    text = TARGET_KEY_PHRASE
    classification_history: list = []
    attempts = []
    final_status = None
    passed_attempt_type = None

    with cl.logging_context("no9_keyphrase_english_lock_fallback_trial_21", "keyphrase_english_lock_trial"):
        # Stage 1: Minimal instruction、最大2 attempt。
        for n in range(1, MAX_MINIMAL_ATTEMPTS + 1):
            out_name = f"default_minimal_attempt{n}"
            rec = _run_one_attempt(text, out_name, "MINIMAL", n,
                                    MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2, classification_history)
            attempts.append(rec)
            if rec["verified"]:
                final_status = f"PASS_ON_MINIMAL_ATTEMPT_{n}"
                passed_attempt_type = "MINIMAL"
                break
            if rec.get("stop_retrying"):
                final_status = f"STOPPED_UNCERTAIN_MINIMAL_ATTEMPT_{n}"
                break
        else:
            final_status = None  # Minimal 2回ともNG、Stage 2へ進む

        # Stage 2: Minimal + English language lock、Minimal 2attemptとも
        # NGだった場合のみ発火。最大2 attempt。
        if final_status is None:
            for n in range(1, MAX_ENGLISH_LOCK_ATTEMPTS + 1):
                out_name = f"default_englishlock_attempt{n}"
                rec = _run_one_attempt(text, out_name, "ENGLISH_LOCK", n,
                                        ENGLISH_LOCK_INSTRUCTION, classification_history)
                attempts.append(rec)
                if rec["verified"]:
                    final_status = f"PASS_ON_ENGLISH_LOCK_ATTEMPT_{n}"
                    passed_attempt_type = "ENGLISH_LOCK"
                    break
                if rec.get("stop_retrying"):
                    final_status = f"STOPPED_UNCERTAIN_ENGLISH_LOCK_ATTEMPT_{n}"
                    break
            else:
                final_status = "FAIL_AFTER_4_ATTEMPTS"

    result = {
        "key_phrase": text,
        "japanese_gloss": TARGET_JAPANESE_GLOSS,
        "minimal_instruction_full_text": MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2,
        "english_lock_instruction_full_text": ENGLISH_LOCK_INSTRUCTION,
        "final_status": final_status,
        "passed_attempt_type": passed_attempt_type,
        "total_actual_calls": len(attempts),
        "attempts": attempts,
    }

    with open(f"{OUT_DIR}/trial21_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    return result


if __name__ == "__main__":
    r = run_english_lock_fallback_trial()
    with open(f"{OUT_DIR}/trial21_results.json", "r", encoding="utf-8") as f:
        pass  # 既にJSON保存済み。Windows console cp932非対応文字を避けるためprintは省略。
