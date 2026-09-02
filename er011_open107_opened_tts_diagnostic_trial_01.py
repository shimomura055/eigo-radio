# ============================================================
# er011_open107_opened_tts_diagnostic_trial_01.py
# ER-011-NO18-PRODUCTION-SPEC-IMPROVEMENT-01 §4: OPEN-107 "opened" TTS
# Diagnostic Trial
# ============================================================
# Productionとは完全に分離したDiagnostic Trial。No.18 B1のin_one_line原稿
# ("Your phone does not have to be opened to become part of the task.")は
# 一切変更しない。この一文のTTS読み上げで"opened"の"-ed"語尾が脱落し
# "open"になる(OPEN-107)現象について、Phase Aで再現条件・原因範囲を
# 診断し、Phase Bで回復策を評価する。ここで得られた知見からProductionへ
# 新しい仕様・例外処理を追加することは、このTrial単体では行わない
# (USER_DECISION_REQUIREDで停止し、ユーザーの判断を待つ)。
#
# 使用model/voice/TTS instruction/trim方式は、実際にNo.18 B1のin_one_line
# を生成したのと同一のもの(er003_v1_sing01_news_tail_fix.py::
# generate_news_narration_wide_margin()が使う値)をそのまま踏襲する
# (model=gemini-2.5-pro-preview-tts、voice=Aoede、ENGLISH_STYLE_PREFIX、
# trim safety margin=0.35秒)。Phase Aの条件1-7は、比較のため簡略化した
# 直接呼び出し(raw pipeline、同一のtrim/ASR手順を共有)で統一する。
# 条件8-9のみ、実際のProduction関数(generate_news_narration_wide_margin)
# をそのまま呼び出す(Production同一コード経路での再現性を確認するため)。

from __future__ import annotations

import json
import os
import sys
import time

# cp932コンソールでASRが非ASCII文字(誤認識でハングル等になる場合がある)を
# 返した際にprint()がクラッシュしないよう、標準出力をUTF-8+置換モードへ
# 切り替える(既知の再発パターン、他のscriptと同じ対処)。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as tts_gen
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing

OUT_DIR = "er011_output/open107_opened_tts_diagnostic_trial_01"
NARRATION_DIR = f"{OUT_DIR}/narration"
os.makedirs(NARRATION_DIR, exist_ok=True)

MODEL_NAME = p9a.ENGLISH_MODEL_NAME  # "gemini-2.5-pro-preview-tts"(実際にNo.18 B1 in_one_lineが使ったmodel)
VOICE_NAME = p9a.VOICE_NAME  # "Aoede"
STYLE_PREFIX = p9a.ENGLISH_STYLE_PREFIX  # 実際に使われたTTS instruction(無変更)
TRIM_SAFETY_MARGIN_SECONDS = 0.35  # news_tail_fix.LONG_FORM_TRIM_SAFETY_MARGIN_SECONDSと同一

ATTEMPTS_PER_CONDITION = 3  # 事前確定(既存Productionのcontent-attempt慣行[3回1セット]を踏襲、新規に発明した値ではない)

# No.18 B1のin_one_line原稿(実際のarticle/parts.jsonから取得、一切変更しない)
TARGET_SENTENCE = "Your phone does not have to be opened to become part of the task."
FOLLOWING_SENTENCE = (
    "In these studies, attention was pulled by the sound and affected by the silent device, "
    "which helps explain why ignoring a notification can feel harder than it looks.")
PRODUCTION_IN_ONE_LINE_FULL_TEXT = f"{TARGET_SENTENCE} {FOLLOWING_SENTENCE}"


def _make_call_fn():
    """実際にNo.18のTTS生成で使われたのと同一のsync呼び出し(client.models.
    generate_content()への直接blocking call)を、この診断Trial専用に
    再構築する(er003_b1_p7a_audio.make_tts_call_fn_for_modelをそのまま
    使う、新しいTTS実装は作らない)。"""
    import er003_b1_p7a_audio as p7a
    return p7a.make_tts_call_fn_for_model(MODEL_NAME, VOICE_NAME)


def classify_opened_pronunciation(asr_text: str | None) -> str:
    """OPEN-107固有の判定: ASRが"opened"(正しい)か"open"(誤り、-ed語尾
    脱落)かを分類する(このTrial専用の判定ロジック、Production側の
    汎用ASR cascadeとは別)。"""
    if asr_text is None:
        return "NO_ASR"
    lowered = asr_text.lower()
    if "opened" in lowered:
        return "CORRECT_OPENED"
    if "open" in lowered:
        return "MISPRONOUNCED_OPEN_MISSING_ED"
    return "OTHER_MISMATCH"


def run_raw_attempt(condition_id: str, text: str, attempt: int) -> dict:
    """Phase A条件1-7用の、簡略化した直接TTS呼び出し(1回のみ、Production
    のretry/fallbackカスケードは使わない、比較のため条件をraw pipelineで
    統一する)。"""
    out_path = f"{NARRATION_DIR}/{condition_id}_attempt{attempt}.wav"
    call_fn = _make_call_fn()
    prompt = p4c.build_tts_prompt(text, STYLE_PREFIX)

    t0 = time.time()
    with cl.logging_context("open107_diagnostic_trial", f"phaseA_{condition_id}"), \
         cl.segment_context(f"{condition_id}_attempt{attempt}"):
        pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
    elapsed = round(time.time() - t0, 2)

    if not ok:
        return {"condition_id": condition_id, "attempt": attempt, "input_text": text, "model": MODEL_NAME,
                "voice": VOICE_NAME, "tts_instruction": STYLE_PREFIX, "status": "TTS_CALL_FAILED",
                "error": err, "elapsed_seconds": elapsed}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {"condition_id": condition_id, "attempt": attempt, "input_text": text, "model": MODEL_NAME,
                "voice": VOICE_NAME, "tts_instruction": STYLE_PREFIX, "status": "SPEECH_BOUNDS_NOT_FOUND",
                "elapsed_seconds": elapsed}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    duration_seconds = round(len(trimmed) / common.SAMPLE_RATE, 3)

    asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
    classification = classify_opened_pronunciation(asr_text)

    return {
        "condition_id": condition_id, "attempt": attempt, "input_text": text, "model": MODEL_NAME,
        "voice": VOICE_NAME, "tts_instruction": STYLE_PREFIX, "audio_path": out_path,
        "duration_seconds": duration_seconds, "asr_text": asr_text, "asr_error": asr_err,
        "audio_validation_classification": classification, "elapsed_seconds": elapsed, "status": "GENERATED",
    }


# ============================================================
# Phase A: 原因範囲の診断(条件1-7はraw pipeline、条件8-9は実Production関数)
# ============================================================
PHASE_A_RAW_CONDITIONS = [
    ("cond1_word_opened", "opened"),
    ("cond2_phrase_be_opened", "be opened"),
    ("cond3_phrase_have_to_be_opened", "have to be opened"),
    ("cond4_phrase_does_not_have_to_be_opened", "does not have to be opened"),
    # 条件5(元の一文全体)と条件6(前後の文脈がない状態)は、この一文単独の
    # TTS呼び出しという点で構造的に同一のテストになるため、1つの実行に
    # 統合する(コスト・時間の無駄な重複を避けるための明示的な判断。結果は
    # 両方の観点[「一文全体」「文脈なし」]として報告する)。
    ("cond5_6_full_sentence_no_context", TARGET_SENTENCE),
    ("cond7_full_sentence_with_following_context", PRODUCTION_IN_ONE_LINE_FULL_TEXT),
]


def run_phase_a() -> dict:
    results = {"raw_conditions": {}, "production_function_conditions": {}}

    for condition_id, text in PHASE_A_RAW_CONDITIONS:
        attempts = []
        for attempt in range(1, ATTEMPTS_PER_CONDITION + 1):
            print(f"[OPEN-107][Phase A][{condition_id}] attempt {attempt}/{ATTEMPTS_PER_CONDITION}: {text!r}")
            r = run_raw_attempt(condition_id, text, attempt)
            print(f"  -> status={r.get('status')} asr={r.get('asr_text')!r} "
                  f"classification={r.get('audio_validation_classification')}")
            attempts.append(r)
        results["raw_conditions"][condition_id] = {"input_text": text, "attempts": attempts}
        with open(f"{OUT_DIR}/phase_a_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    # 条件8: 元の一文を単独segmentとして、実際のProduction関数
    # (generate_news_narration_wide_margin)で生成する(Production同一
    # コード経路での再現性を確認する。disfluency_qa=Trueはin_one_line
    # 生成時の実際の呼び出し設定に合わせる)。
    print("[OPEN-107][Phase A][cond8_isolated_segment_via_production_function] 実Production関数で単独生成...")
    t0 = time.time()
    with cl.logging_context("open107_diagnostic_trial", "phaseA_cond8_production_fn"), \
         cl.segment_context("cond8_isolated_segment"):
        cond8_result = news_tail_fix.generate_news_narration_wide_margin(
            tts_gen.tts_safe_news_en(TARGET_SENTENCE),
            f"{NARRATION_DIR}/cond8_isolated_segment.wav", disfluency_qa=True)
    elapsed = round(time.time() - t0, 2)
    results["production_function_conditions"]["cond8_isolated_segment_via_production_function"] = {
        "input_text": TARGET_SENTENCE, "result": cond8_result, "elapsed_seconds": elapsed,
        "audio_validation_classification": classify_opened_pronunciation(
            (cond8_result.get("asr_text") or cond8_result.get("classification", {}).get("asr_text"))),
    }
    print(f"  -> status={cond8_result.get('status')}")

    # 条件9: 長いin_one_line segment内(実際の2文)で生成した状態。これは
    # No.18本番実行で実際に3attempt連続でSTOPPEDした条件そのものであり、
    # 既に実データ(er006_output/pool_pilot_01/pool_n18_notifications/
    # b1b/audit/tts_generation_results.json)が存在するため、同一内容の
    # 呼び出しを新たな課金で繰り返さず、既存の実行結果を引用する
    # (再現性の追加確認が必要な場合はユーザー判断でこのTrialを再実行できる
    # よう、関数は用意しておく)。
    existing_path = "er006_output/pool_pilot_01/pool_n18_notifications/b1b/audit/tts_generation_results.json"
    cond9_entry = {"input_text": PRODUCTION_IN_ONE_LINE_FULL_TEXT, "source": "REUSED_FROM_ORIGINAL_PRODUCTION_RUN",
                    "reason": "同一内容の呼び出しを新たな課金で繰り返さないため、既存のNo.18本番実行(3attempt "
                              "連続STOPPED)の実データをそのまま引用する。"}
    if os.path.exists(existing_path):
        with open(existing_path, encoding="utf-8") as f:
            existing_data = json.load(f)
        cond9_entry["original_production_result"] = existing_data.get("segments", {}).get("in_one_line")
    results["production_function_conditions"]["cond9_long_in_one_line_segment_reused_from_production"] = cond9_entry

    with open(f"{OUT_DIR}/phase_a_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


# ============================================================
# Phase B: 回復策の評価(Phase Aで失敗が再現した条件[全文]を対象に、
# 3つの回復策を独立に検証する)
# ============================================================
CLEAR_ENDING_INSTRUCTION_SUFFIX = (
    " Pronounce every word ending clearly and completely, including grammatical suffixes such as "
    "the past participle \"-ed\" ending. Do not drop or shorten word endings, even in fast or "
    "casual speech.")


def run_recovery_split_and_rejoin() -> dict:
    """回復策1: segmentの短分割と再結合。"opened"を含む節を単独の短い
    TTS呼び出しへ分割し、残り部分と別々に生成する(結合自体はこのTrialの
    スコープ外、各chunkのASR結果だけを個別に評価する)。"""
    chunk_a = "Your phone does not have to be opened"
    chunk_b = "to become part of the task."
    attempts = []
    for attempt in range(1, ATTEMPTS_PER_CONDITION + 1):
        print(f"[OPEN-107][Phase B][split_and_rejoin] attempt {attempt}: chunk_a={chunk_a!r}")
        r = run_raw_attempt("phaseB_split_chunk_a", chunk_a, attempt)
        attempts.append(r)
    return {"strategy": "segment_split_and_rejoin", "chunk_a": chunk_a, "chunk_b": chunk_b, "attempts": attempts}


def run_recovery_clear_ending_instruction() -> dict:
    """回復策2: 語尾・文法要素を明瞭に読むTTS instructionを追加する
    (既存のSTYLE_PREFIXを削除・変更せず、AND方式で末尾へ追加する。
    Key Phraseのfunction-word reduction仕様[ER-010-27]と同じ設計方針)。"""
    text = TARGET_SENTENCE
    style_prefix = STYLE_PREFIX + CLEAR_ENDING_INSTRUCTION_SUFFIX
    attempts = []
    for attempt in range(1, ATTEMPTS_PER_CONDITION + 1):
        out_path = f"{NARRATION_DIR}/phaseB_clear_ending_attempt{attempt}.wav"
        call_fn = _make_call_fn()
        prompt = p4c.build_tts_prompt(text, style_prefix)
        print(f"[OPEN-107][Phase B][clear_ending_instruction] attempt {attempt}")
        t0 = time.time()
        with cl.logging_context("open107_diagnostic_trial", "phaseB_clear_ending"), \
             cl.segment_context(f"clear_ending_attempt{attempt}"):
            pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
        elapsed = round(time.time() - t0, 2)
        if not ok:
            attempts.append({"attempt": attempt, "status": "TTS_CALL_FAILED", "error": err})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIM_SAFETY_MARGIN_SECONDS)
        if trimmed is None:
            attempts.append({"attempt": attempt, "status": "SPEECH_BOUNDS_NOT_FOUND"})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
        attempts.append({
            "attempt": attempt, "status": "GENERATED", "audio_path": out_path, "asr_text": asr_text,
            "asr_error": asr_err, "audio_validation_classification": classify_opened_pronunciation(asr_text),
            "elapsed_seconds": elapsed,
        })
        print(f"  -> asr={asr_text!r} classification={attempts[-1]['audio_validation_classification']}")
    return {"strategy": "clear_ending_tts_instruction", "input_text": text,
            "tts_instruction": style_prefix, "attempts": attempts}


def run_recovery_voice_change() -> dict:
    """回復策3: voice変更(Aoede -> Charon、B1 Support/Navigatorで実際に
    使われている既存voiceへの一時的な切替。新しいvoiceは発明しない)。"""
    import er003_b1_p7a_audio as p7a
    text = TARGET_SENTENCE
    voice_name = "Charon"
    call_fn_factory = lambda: p7a.make_tts_call_fn_for_model(MODEL_NAME, voice_name)
    attempts = []
    for attempt in range(1, ATTEMPTS_PER_CONDITION + 1):
        out_path = f"{NARRATION_DIR}/phaseB_voice_charon_attempt{attempt}.wav"
        call_fn = call_fn_factory()
        prompt = p4c.build_tts_prompt(text, STYLE_PREFIX)
        print(f"[OPEN-107][Phase B][voice_change_charon] attempt {attempt}")
        t0 = time.time()
        with cl.logging_context("open107_diagnostic_trial", "phaseB_voice_change"), \
             cl.segment_context(f"voice_charon_attempt{attempt}"):
            pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
        elapsed = round(time.time() - t0, 2)
        if not ok:
            attempts.append({"attempt": attempt, "status": "TTS_CALL_FAILED", "error": err})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIM_SAFETY_MARGIN_SECONDS)
        if trimmed is None:
            attempts.append({"attempt": attempt, "status": "SPEECH_BOUNDS_NOT_FOUND"})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
        attempts.append({
            "attempt": attempt, "status": "GENERATED", "audio_path": out_path, "asr_text": asr_text,
            "asr_error": asr_err, "audio_validation_classification": classify_opened_pronunciation(asr_text),
            "elapsed_seconds": elapsed,
        })
        print(f"  -> asr={asr_text!r} classification={attempts[-1]['audio_validation_classification']}")
    return {"strategy": "voice_change_charon", "input_text": text, "voice": voice_name, "attempts": attempts}


def run_phase_b() -> dict:
    results = {
        "split_and_rejoin": run_recovery_split_and_rejoin(),
        "clear_ending_instruction": run_recovery_clear_ending_instruction(),
        "voice_change": run_recovery_voice_change(),
    }
    with open(f"{OUT_DIR}/phase_b_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return results


if __name__ == "__main__":
    import sys
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    if stage == "phase_a":
        run_phase_a()
    elif stage == "phase_b":
        run_phase_b()
    else:
        print("usage: er011_open107_opened_tts_diagnostic_trial_01.py [phase_a|phase_b]")
