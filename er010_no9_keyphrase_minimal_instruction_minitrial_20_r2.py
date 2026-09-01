# ============================================================
# er010_no9_keyphrase_minimal_instruction_minitrial_20_r2.py
# ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-MINI-TRIAL-20-R2
# ============================================================
# OPEN-103のMini-Trial(R2)専用モジュール。No.9 A2の正式Production Key
# Phrase 5件(pool_n9_tip_screens/a2)を対象に、Minimal instructionで
# 各語まず1回生成し、ASR/Validator NGの語だけ最大2回までretry(各語
# 最大3attempt)する隔離実装。
#
# Production経路(er003_v1_repro01_main_generate.py::
# generate_key_phrase_component_verified、review_lock guarded)は一切
# 呼び出さない。TTSモデル・voice・trim margin・duration anomaly検知・
# ASR Validator(secondary_asr cascade)・disfluency gateは、すべて
# Productionが実際に使っているのと同一の関数をそのまま再利用し、
# style instructionだけをMinimal Trial版に差し替える。review_lockの
# guarded_generate/guarded_generate_with_language_argデコレータが付いた
# 関数(generate_narration_snippet_verified_strict等)は一切呼ばないため、
# Production retry count/review lockには一切触れない。
#
# Minimal instruction文言は前回Trial(ER-010-NO9-KEYPHRASE-MINIMAL-
# INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19)のMINIMAL_INSTRUCTION_
# TRIAL_PREFIX_V2をそのまま踏襲する(無変更)。設計根拠は同ファイル
# (er010_no9_keyphrase_minimal_instruction_trial_19.py)のコメント参照:
#   - ベースの最小限instructionはProduction fallback承認済みの
#     repro01.MINIMAL_INSTRUCTION_PREFIXを踏襲
#   - 語末音素保持の一文は、既にTrial実績のある
#     er003_v1_a2_audio_02_generate.TRIAL_CLARITY_INSTRUCTION_PREFIXの
#     文言をそのまま再利用
#   - phrase一体感の一文は、CURRENT_SPEC.md「Key Phrase発音品質(3条件)」
#     DECIDED仕様の(3)を文章化した新規の一文

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

OUT_DIR = "er010_output/no9_keyphrase_minimal_instruction_minitrial_20_r2"
AUDIO_DIR = f"{OUT_DIR}/audio"
QUARANTINE_DIR = f"{OUT_DIR}/quarantine"
COST_LOG_PATH = f"{OUT_DIR}/cost_log_trial.jsonl"

MAX_ATTEMPTS_PER_KEY_PHRASE = 3

# 前回Trial(19)からの無変更引き継ぎ。
MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2 = (
    "Speak the following short phrase aloud naturally and clearly, in a warm podcast "
    "announcer voice, exactly once. Say only this phrase — do not add explanations, "
    "examples, introductions, or any other commentary, and do not add, omit, or change "
    "any words. Say it as one natural phrase, not as separate words read one at a time. "
    "Make sure the very last sound of the phrase is actually spoken, not trailed off into "
    "silence, and do not over-emphasize or exaggerate any single sound.\n\n"
)

KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS = repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS

# No.9 A2正式Production Key Phrase 5件(er006_output/pool_pilot_01/
# pool_n9_tip_screens/a2/key_phrases/keywords_canonicalized.jsonから
# そのまま取得。テキストを書き換えない)。
NO9_A2_KEY_PHRASES = [
    {"rank": 1, "key_phrase": "guilt tipping", "japanese_gloss": "罪悪感からするチップ",
     "production_segment": "kp1_en", "production_status": "OK(reused, master_audio_store)"},
    {"rank": 2, "key_phrase": "default", "japanese_gloss": "初期設定の選択肢",
     "production_segment": "kp2_en", "production_status": "HUMAN_REVIEW_REQUIRED(3回とも duration anomaly)"},
    {"rank": 3, "key_phrase": "push back", "japanese_gloss": "反発する、抵抗する",
     "production_segment": "kp3_en", "production_status": "OK(reused, master_audio_store)"},
    {"rank": 4, "key_phrase": "a catch", "japanese_gloss": "落とし穴、ただし書き",
     "production_segment": "kp4_en", "production_status": "OK(reused, master_audio_store)"},
    {"rank": 5, "key_phrase": "starting point", "japanese_gloss": "判断の出発点、基準",
     "production_segment": "kp5_en", "production_status": "OK(reused, master_audio_store)"},
]


def _run_one_attempt(text: str, out_name: str, attempt: int, classification_history: list) -> dict:
    """Production同一のTTS呼び出し・trim・duration anomaly検知・ASR
    Validator(secondary_asr cascade)・disfluency gateを、Minimal
    instructionで1回だけ実行する。review_lockには一切触れない。"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}_attempt{attempt}.wav"

    prompt = p4c.build_tts_prompt(text, MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2)
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"attempt": attempt, "status": "STOPPED", "verified": False, "stop_retrying": False,
                "reason": f"TTS技術的失敗: {err}", "audio_path": None, "is_quarantine": False}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"attempt": attempt, "status": "STOPPED", "verified": False, "stop_retrying": False,
                "reason": "発話区間を検出できませんでした", "audio_path": None, "is_quarantine": False}

    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        # Production(er003_b1_p9a_audio.generate_narration_snippet等)は
        # ここでSTOPPEDを返し音声を一切保存しないが、Trial診断・ユーザー
        # 試聴のためquarantine専用pathへ生波形を保存する(Production正式
        # quarantine仕様の新設ではなく、このTrialモジュール内限定の措置)。
        q_path = f"{QUARANTINE_DIR}/{out_name}_attempt{attempt}_anomaly.wav"
        common.write_wav_float(q_path, samples_raw, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(q_path, language="en-US")
        return {
            "attempt": attempt, "status": "STOPPED", "verified": False, "stop_retrying": False,
            "reason": anomaly["reason"], "duration_anomaly": anomaly,
            "raw_duration_seconds": trim_info["raw_duration_seconds"],
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
        "attempt": attempt, "status": "OK", "verified": verified, "stop_retrying": stop_retrying,
        "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "raw_duration_seconds": trim_info["raw_duration_seconds"],
        "duration_anomaly": anomaly, "clipping_detected": metrics["clipping_detected"],
        "asr_text": asr_text, "asr_error": asr_err, "length_ok": length_ok,
        "audio_classification": cls.classification, "classification_reason": cls.reason,
        "disfluency_checked": gate["disfluency_checked"], "disfluency_evidence": gate.get("disfluency_evidence"),
        "audio_path": out_path, "is_quarantine": False,
        "call_count": 1 + retries, "retry_count": retries,
        "sha256": p8a.sha256_file(out_path),
    }


def generate_key_phrase_minimal_minitrial_bounded(text: str, out_name: str,
                                                    max_attempts: int = MAX_ATTEMPTS_PER_KEY_PHRASE) -> dict:
    classification_history: list = []
    attempts = []
    final_status = None
    for attempt in range(1, max_attempts + 1):
        rec = _run_one_attempt(text, out_name, attempt, classification_history)
        attempts.append(rec)
        if rec["verified"]:
            final_status = f"PASS_ON_ATTEMPT_{attempt}"
            break
        if rec.get("stop_retrying"):
            final_status = f"STOPPED_UNCERTAIN_ATTEMPT_{attempt}"
            break
    else:
        final_status = f"FAIL_AFTER_{max_attempts}_ATTEMPTS"

    return {
        "key_phrase": text, "out_name": out_name, "final_status": final_status,
        "attempts": attempts, "total_actual_calls": len(attempts),
    }


def run_minitrial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    cl.init_logger(COST_LOG_PATH)
    results = {}
    with cl.logging_context("no9_keyphrase_minimal_minitrial_20_r2", "keyphrase_minimal_minitrial"):
        for kp in NO9_A2_KEY_PHRASES:
            text = kp["key_phrase"]
            out_name = f"kp{kp['rank']}_{text.replace(' ', '_')}"
            result = generate_key_phrase_minimal_minitrial_bounded(text, out_name)
            result["rank"] = kp["rank"]
            result["japanese_gloss"] = kp["japanese_gloss"]
            result["production_segment"] = kp["production_segment"]
            result["production_status"] = kp["production_status"]
            results[text] = result

    with open(f"{OUT_DIR}/minitrial_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "instruction_prefix": MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2,
            "trim_safety_margin_seconds": KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS,
            "max_attempts_per_key_phrase": MAX_ATTEMPTS_PER_KEY_PHRASE,
            "results": results,
        }, f, ensure_ascii=False, indent=2, default=str)

    return results


if __name__ == "__main__":
    r = run_minitrial()
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
