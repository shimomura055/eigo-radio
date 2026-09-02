# ============================================================
# er011_no18_open110_survey_diagnostic_04.py
# ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04 §2/§3: "survey"->"surveys" 診断
# ============================================================
# Productionとは完全に分離したDiagnostic Trial。No.18 B1のcomment_3原稿は
# 一切変更しない。comment_3のTTS読み上げで"survey"(単数、原稿通り)が
# ASRで"surveys"(複数、存在しない語尾追加)になる現象について、原因候補
# (後続語頭の/s/取り込み、grammatical parallelism補正、ASR側の誤認等)を
# 切り分けるための再現条件を診断する。ここで得られた知見からProductionへ
# 新しい仕様・言い換え・Validator変更を加えることは、このTrial単体では
# 行わない(方針判断はユーザーへ委ねる)。
#
# 使用model/voice/TTS instructionは、実際にcomment_3を生成したのと同一
# (voice01.generate_charon_english()が使う値: voice=Charon、
# style_prefix_override=B1_PREVIEW_STYLE_PREFIX_CALM)をそのまま踏襲する。

from __future__ import annotations

import json
import os
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_voice01_generate as voice01
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing

OUT_DIR = "er011_output/open110_survey_diagnostic_04"
NARRATION_DIR = f"{OUT_DIR}/narration"
os.makedirs(NARRATION_DIR, exist_ok=True)

VOICE_NAME = voice01.CHARON
STYLE_PREFIX = tts_gen.B1_PREVIEW_STYLE_PREFIX_CALM  # 実際にcomment_3が使ったinstruction(無変更)
TRIM_SAFETY_MARGIN_SECONDS = voice01.SAFETY_MARGIN

ATTEMPTS_PER_CONDITION = 3

ORIGINAL_COMMENT3_TEXT = (
    "This story is not only about choosing to check a phone. The studies and the survey suggest "
    "that a phone can affect people even when they do not check it. Now, let's look more closely "
    "at what may be happening in these situations.")

CONDITIONS = [
    # cond1: 実際のcomment_3全文をそのまま再現条件として使う(baseline再現率確認)。
    ("cond1_full_original", ORIGINAL_COMMENT3_TEXT),
    # cond2: "survey"を短文で"suggest"(/s/始まり)の直前に置く。文脈を削って
    # 後続/s/との隣接だけを残す。
    ("cond2_survey_before_s_initial_word_short", "The survey suggests useful information for parents."),
    # cond3: "survey"の直後を非歯擦音(母音始まり)の語に変える。後続/s/依存かどうかの対照条件。
    ("cond3_survey_before_non_sibilant_word", "The survey indicates useful information for parents."),
    # cond4: 元の語順を変え、"survey"を"suggest"の直前から外す
    # (grammatical parallelism仮説と/s/隣接仮説を切り分ける)。
    ("cond4_survey_reordered_away_from_suggest",
     "The survey and the studies suggest that a phone can affect people even when they do not check it."),
    # cond5: "survey"を単独の名詞句として発話させる(最小文脈)。
    ("cond5_survey_isolated_minimal", "The survey was clear."),
]


def classify_survey_pluralization(asr_text: str | None) -> str:
    if asr_text is None:
        return "NO_ASR"
    lowered = asr_text.lower()
    if "surveys" in lowered:
        return "PLURALIZED_SURVEYS"
    if "survey" in lowered:
        return "CORRECT_SURVEY_SINGULAR"
    return "OTHER_MISMATCH"


def _make_call_fn(out_path: str):
    import er006_batch_tts_wiring_01 as batch_wiring
    return batch_wiring.make_batch_tts_call_fn(p9a.ENGLISH_MODEL_NAME, VOICE_NAME, output_path=out_path)


def run_raw_attempt(condition_id: str, text: str, attempt: int) -> dict:
    out_path = f"{NARRATION_DIR}/{condition_id}_attempt{attempt}.wav"
    call_fn = _make_call_fn(out_path)
    prompt = p4c.build_tts_prompt(text, STYLE_PREFIX)

    t0 = time.time()
    with cl.logging_context("open110_survey_diagnostic_04", f"survey_diag_{condition_id}"), \
         cl.segment_context(f"{condition_id}_attempt{attempt}"):
        pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
    elapsed = round(time.time() - t0, 2)

    if not ok:
        return {"condition_id": condition_id, "attempt": attempt, "input_text": text, "voice": VOICE_NAME,
                "tts_instruction": STYLE_PREFIX, "status": "TTS_CALL_FAILED", "error": err,
                "elapsed_seconds": elapsed}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"condition_id": condition_id, "attempt": attempt, "input_text": text, "voice": VOICE_NAME,
                "tts_instruction": STYLE_PREFIX, "status": "SPEECH_BOUNDS_NOT_FOUND", "elapsed_seconds": elapsed}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    duration_seconds = round(len(trimmed) / common.SAMPLE_RATE, 3)

    asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
    classification = classify_survey_pluralization(asr_text)

    return {
        "condition_id": condition_id, "attempt": attempt, "input_text": text, "voice": VOICE_NAME,
        "tts_instruction": STYLE_PREFIX, "audio_path": out_path, "duration_seconds": duration_seconds,
        "asr_text": asr_text, "asr_error": asr_err, "survey_pluralization_classification": classification,
        "elapsed_seconds": elapsed, "status": "GENERATED",
    }


def main():
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    results = {}
    for condition_id, text in CONDITIONS:
        attempts = []
        for attempt in range(1, ATTEMPTS_PER_CONDITION + 1):
            print(f"[OPEN-110][survey diagnostic][{condition_id}] attempt {attempt}/{ATTEMPTS_PER_CONDITION}: {text!r}")
            r = run_raw_attempt(condition_id, text, attempt)
            print(f"  -> status={r.get('status')} asr={r.get('asr_text')!r} "
                  f"classification={r.get('survey_pluralization_classification')}")
            attempts.append(r)
        results[condition_id] = {"input_text": text, "attempts": attempts}
        with open(f"{OUT_DIR}/survey_diagnostic_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    summary = {}
    for condition_id, data in results.items():
        classes = [a.get("survey_pluralization_classification") for a in data["attempts"]]
        summary[condition_id] = {"input_text": data["input_text"], "classifications": classes,
                                  "pluralized_count": classes.count("PLURALIZED_SURVEYS")}
    with open(f"{OUT_DIR}/survey_diagnostic_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("[OPEN-110][survey diagnostic] summary:")
    for condition_id, s in summary.items():
        print(f"  {condition_id}: {s['classifications']} (pluralized {s['pluralized_count']}/{ATTEMPTS_PER_CONDITION})")


if __name__ == "__main__":
    main()
