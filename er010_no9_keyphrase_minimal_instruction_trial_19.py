# ============================================================
# er010_no9_keyphrase_minimal_instruction_trial_19.py
# ER-010-NO9-KEYPHRASE-MINIMAL-INSTRUCTION-TRIAL-AND-RETRY-ACCOUNTING-FIX-19
# ============================================================
# OPEN-103のMinimal instruction Trial専用モジュール。Production経路
# (er003_v1_repro01_main_generate.py::generate_key_phrase_component_verified、
# review_lock guarded)は一切呼び出さない。声・モデル・trim margin・
# duration anomaly検知ロジックはProductionと同一のものを再利用し、
# instruction文言だけをTrial版に差し替えて比較する隔離実装。
#
# Trial instructionの設計根拠(CURRENT_SPEC.md「Key Phrase発音品質
# (3条件)」DECIDED、2026-08-12、ER-003-CROSSLEVEL-AUDIO-04):
#   (1) Meaning/contextual prosody — 単語単位のTrialでは記事文脈を
#       持たないため、汎用instructionとしては対応しない(既知の制約、
#       完了報告で明記する)。
#   (2) Phoneme integrity(語末音素保持) — 既にTrial実績のある
#       er003_v1_a2_audio_02_generate.TRIAL_CLARITY_INSTRUCTION_PREFIXの
#       文言("make sure the very last sound of the phrase is actually
#       spoken, not trailed off into silence"/ "do not over-emphasize or
#       exaggerate any single sound")をそのまま再利用する。
#   (3) Phrase grouping(単語ごとに分断しない) — CURRENT_SPEC定義を
#       文章化した新規の一文("Say it as one natural phrase, not as
#       separate words read one at a time.")を追加する。
# ベースの「最小限であること」自体は、既にProduction fallbackとして
# 承認済みのrepro01.MINIMAL_INSTRUCTION_PREFIXの文言をそのまま踏襲する。
# "Say it only once" / "do not add explanations, examples, introductions,
# or commentary"は、タスク仕様§5が候補として明示した文言をそのまま採用
# した(hallucination/instruction leak対策、未承認の発音ルールではない)。

from __future__ import annotations

import json
import os

import er002_common as common
import er003_audio_tts_asr_safety as safety
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p8a_audio as p8a
import er003_b1_p9a_audio as p9a
import er003_v1_repro01_main_generate as repro01
import er006_asr_provider_routing_01 as routing

OUT_DIR = "er010_output/no9_keyphrase_minimal_instruction_trial_19"
AUDIO_DIR = f"{OUT_DIR}/audio"
QUARANTINE_DIR = f"{OUT_DIR}/quarantine"

MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2 = (
    "Speak the following short phrase aloud naturally and clearly, in a warm podcast "
    "announcer voice, exactly once. Say only this phrase — do not add explanations, "
    "examples, introductions, or any other commentary, and do not add, omit, or change "
    "any words. Say it as one natural phrase, not as separate words read one at a time. "
    "Make sure the very last sound of the phrase is actually spoken, not trailed off into "
    "silence, and do not over-emphasize or exaggerate any single sound.\n\n"
)

# Key Phrase生成専用のhead safety margin(ER-003-N3-ROOT-FIX-01と同じ値、
# Production standard/fallback両経路と揃える)。
TRIAL_TRIM_SAFETY_MARGIN_SECONDS = repro01.KEY_PHRASE_TRIM_SAFETY_MARGIN_SECONDS


def generate_key_phrase_minimal_trial(text: str, out_name: str) -> dict:
    """Production review lockを経由しない、隔離Trial専用の単発生成
    (retry・review lockの状態は変更しない)。異常音声もquarantineへ保存する。"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    out_path = f"{AUDIO_DIR}/{out_name}.wav"

    prompt = p4c.build_tts_prompt(text, MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2)
    call_fn = p9a._make_english_call_fn()
    pcm, retries, ok, err = common._call_tts_with_retry(
        call_fn, prompt, max_retry=p9a.MAX_TTS_TECHNICAL_RETRY, sleep_fn=None)
    if not ok:
        return {"status": "STOPPED", "reason": f"TTS失敗: {err}", "text": text,
                "instruction": "minimal_trial_v2"}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIAL_TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"status": "STOPPED", "reason": "発話区間を検出できませんでした", "text": text,
                "instruction": "minimal_trial_v2"}

    # Production同様、ASR実行前にduration anomalyを検知する(同一ロジック・
    # 同一閾値をそのまま再利用し、比較可能性を保つ)。
    anomaly = safety.detect_duration_anomaly(trim_info["raw_duration_seconds"], text, "en")
    if anomaly["is_anomaly"]:
        # Production(er003_b1_p9a_audio.generate_narration_snippet等)は
        # 異常検知時に音声を一切保存しないが、Trial診断のためここでは
        # quarantine専用pathへ生波形を保存する(Production正式quarantine
        # 仕様の新設ではなく、このTrialモジュール内限定の一時措置)。
        q_path = f"{QUARANTINE_DIR}/{out_name}_anomaly.wav"
        common.write_wav_float(q_path, samples_raw, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(q_path, language="en-US")
        return {
            "status": "STOPPED", "text": text, "instruction": "minimal_trial_v2",
            "reason": anomaly["reason"], "duration_anomaly": anomaly,
            "quarantine_path": q_path, "quarantine_asr_text": asr_text, "quarantine_asr_error": asr_err,
            "raw_duration_seconds": trim_info["raw_duration_seconds"],
            "call_count": 1 + retries, "retry_count": retries,
        }

    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
    asr_text, asr_err = routing.transcribe(out_path, language="en-US")
    max_len = len(text) + 10
    length_ok = asr_text is not None and len(asr_text) <= max_len
    return {
        "status": "OK", "text": text, "path": out_path, "instruction": "minimal_trial_v2",
        "model": p9a.ENGLISH_MODEL_NAME, "voice": p9a.VOICE_NAME,
        "call_count": 1 + retries, "retry_count": retries,
        "sha256": p8a.sha256_file(out_path),
        "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        "raw_duration_seconds": trim_info["raw_duration_seconds"],
        "duration_anomaly": anomaly,
        "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
        "asr_text": asr_text, "asr_error": asr_err, "asr_length_ok": length_ok,
        "asr_exact_match": (asr_text or "").strip().rstrip(".").lower() == text.strip().lower(),
    }


def run_trial() -> dict:
    os.makedirs(OUT_DIR, exist_ok=True)
    targets = [
        ("default", "kp_default_no9_a2"),
        ("opt out", "kp_opt_out_a02_repro"),
    ]
    results = {}
    for text, name in targets:
        results[text] = generate_key_phrase_minimal_trial(text, name)

    with open(f"{OUT_DIR}/trial_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "instruction_prefix": MINIMAL_INSTRUCTION_TRIAL_PREFIX_V2,
            "trim_safety_margin_seconds": TRIAL_TRIM_SAFETY_MARGIN_SECONDS,
            "results": results,
        }, f, ensure_ascii=False, indent=2, default=str)

    return results


if __name__ == "__main__":
    r = run_trial()
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
