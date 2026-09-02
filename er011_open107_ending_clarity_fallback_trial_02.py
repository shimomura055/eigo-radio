# ============================================================
# er011_open107_ending_clarity_fallback_trial_02.py
# ER-011-NO18-OPEN108-LEDGER-REFINE-AND-OPEN107-ENDING-FALLBACK-TRIAL-02 / Track B
# ============================================================
# OPEN-107の"opened"誤発音(-ed語尾脱落)について、通常TTS instructionを
# 常時複雑化せず、通常retryでもNGが続いたsegmentだけにEnding-Clarity
# instructionを追加するfallback候補案をTrialする。今回もProductionへの
# 正式採用は行わない(Ending-Clarity instructionはこのTrial実行中のみ、
# 一時的なmonkeypatchでer003_v1_sing01_news_tail_fixの実Production関数へ
# 適用する。er003_v1_sing01_news_tail_fix.py / er003_b1_p9a_audio.py
# 等のソースファイル自体は一切変更しない)。
#
# Ending-Clarity instructionの文言は、opened/-edへのhardcodeを避け、
# 「語尾・末尾音素を明瞭に保ちつつ、不自然な誇張やリズム破壊を禁止する」
# という一般化可能な形にした(ユーザー提示の意図例にほぼ準拠)。
#
# 条件・attempt回数は、前回のer011_open107_opened_tts_diagnostic_trial_01
# (Phase A/B)の実データをできる限り再利用し、新規課金は「Ending-Clarity
# instructionを使った新しい生成」にのみ限定する(無駄なAPI消費を避ける)。

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
import er003_b1_p7a_audio as p7a
import er003_b1_p9a_audio as p9a
import er003_v1_sing01_news_tail_fix as news_tail_fix
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as asr_routing
import er011_open107_opened_tts_diagnostic_trial_01 as diag01

OUT_DIR = "er011_output/open107_ending_clarity_fallback_trial_02"
NARRATION_DIR = f"{OUT_DIR}/narration"
os.makedirs(NARRATION_DIR, exist_ok=True)

MODEL_NAME = diag01.MODEL_NAME
VOICE_NAME = diag01.VOICE_NAME
NORMAL_STYLE_PREFIX = diag01.STYLE_PREFIX  # 既存Production instruction、無変更
TRIM_SAFETY_MARGIN_SECONDS = diag01.TRIM_SAFETY_MARGIN_SECONDS  # 0.35秒、既存Production long-formと同一

# Ending-Clarity fallback instruction(今回のTrial candidate)。既存instructionを
# 全面置換せず、末尾へAND方式で追加する。"opened"/"-ed"へのhardcodeを避け、
# 語尾・最終音素一般に適用可能な文言にし、過剰な強調を明示的に禁止する。
ENDING_CLARITY_SUFFIX = (
    " Pronounce grammatical endings and final sounds clearly enough to remain audible, "
    "without exaggerating them or disrupting the natural rhythm of the sentence.")
ENDING_CLARITY_STYLE_PREFIX = NORMAL_STYLE_PREFIX + ENDING_CLARITY_SUFFIX

TARGET_SENTENCE = diag01.TARGET_SENTENCE
FOLLOWING_SENTENCE = diag01.FOLLOWING_SENTENCE
PRODUCTION_IN_ONE_LINE_FULL_TEXT = diag01.PRODUCTION_IN_ONE_LINE_FULL_TEXT

classify_opened_pronunciation = diag01.classify_opened_pronunciation


def run_attempt(condition_id: str, text: str, attempt: int, style_prefix: str, instruction_label: str) -> dict:
    """diag01.run_raw_attemptと同じraw pipelineだが、style_prefixを外から
    指定できるよう一般化したもの(Normal/Ending-Clarityを同一条件で比較する
    ため)。"""
    out_path = f"{NARRATION_DIR}/{condition_id}_{instruction_label}_attempt{attempt}.wav"
    call_fn = p7a.make_tts_call_fn_for_model(MODEL_NAME, VOICE_NAME)
    prompt = p4c.build_tts_prompt(text, style_prefix)

    t0 = time.time()
    with cl.logging_context("open107_ending_clarity_trial", f"{condition_id}_{instruction_label}"), \
         cl.segment_context(f"{condition_id}_{instruction_label}_attempt{attempt}"):
        pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
    elapsed = round(time.time() - t0, 2)

    base = {"condition_id": condition_id, "instruction_label": instruction_label, "attempt": attempt,
            "input_text": text, "model": MODEL_NAME, "voice": VOICE_NAME, "tts_instruction": style_prefix}
    if not ok:
        return {**base, "status": "TTS_CALL_FAILED", "error": err, "elapsed_seconds": elapsed}

    samples_raw = common.pcm_bytes_to_float_mono(pcm)
    trimmed, trim_info = p3u.trim_english_keyword_silence(
        samples_raw, common.SAMPLE_RATE, safety_margin_seconds=TRIM_SAFETY_MARGIN_SECONDS)
    if trimmed is None:
        return {**base, "status": "SPEECH_BOUNDS_NOT_FOUND", "elapsed_seconds": elapsed}
    common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
    duration_seconds = round(len(trimmed) / common.SAMPLE_RATE, 3)

    asr_text, asr_err = asr_routing.transcribe(out_path, language="en-US")
    classification = classify_opened_pronunciation(asr_text)

    return {**base, "audio_path": out_path, "duration_seconds": duration_seconds, "asr_text": asr_text,
            "asr_error": asr_err, "audio_validation_classification": classification,
            "elapsed_seconds": elapsed, "status": "GENERATED"}


def _load_reused(condition_id: str) -> dict:
    """前回Trialの既存結果ファイルから、指定conditionのattempts(Normal)を
    そのまま引用する(同一内容の呼び出しを新たな課金で繰り返さないため)。"""
    with open("er011_output/open107_opened_tts_diagnostic_trial_01/phase_a_results.json", encoding="utf-8") as f:
        phase_a = json.load(f)
    with open("er011_output/open107_opened_tts_diagnostic_trial_01/phase_b_results.json", encoding="utf-8") as f:
        phase_b = json.load(f)
    return phase_a, phase_b


def build_condition_1_2_3(phase_a: dict) -> dict:
    """条件1-3(短句): Normalは前回Phase Aの結果をそのまま再利用(いずれも
    3/3 CORRECT_OPENED、天井効果のため再測定の価値が低い)。Ending-Clarityは
    自然さ確認のための最小限(各1回)のみ新規実行する。"""
    mapping = {
        "cond1_opened_alone": ("cond1_word_opened", "opened"),
        "cond2_be_opened": ("cond2_phrase_be_opened", "be opened"),
        "cond3_does_not_have_to_be_opened": ("cond4_phrase_does_not_have_to_be_opened", "does not have to be opened"),
    }
    results = {}
    for new_id, (old_id, text) in mapping.items():
        normal_attempts = phase_a["raw_conditions"][old_id]["attempts"]
        print(f"[OPEN-107][Ending-Clarity Trial][{new_id}] Ending-Clarity 1attempt: {text!r}")
        ec_attempt = run_attempt(new_id, text, 1, ENDING_CLARITY_STYLE_PREFIX, "ending_clarity")
        print(f"  -> status={ec_attempt.get('status')} asr={ec_attempt.get('asr_text')!r} "
              f"classification={ec_attempt.get('audio_validation_classification')}")
        results[new_id] = {
            "input_text": text,
            "normal": {"source": "REUSED_FROM_TRIAL_01_PHASE_A", "reused_from_condition": old_id,
                       "attempts": normal_attempts},
            "ending_clarity": {"source": "NEW", "attempts": [ec_attempt]},
        }
    return results


def build_condition_4_full_sentence(phase_a: dict) -> dict:
    """条件4(完全な一文、文脈なし): Normalは前回Phase Aのcond5_6を再利用
    (2/3 PASS)。Ending-Clarityは新しい文言で3回新規実行する(前回Phase Bの
    clear_ending_instructionは異なる文言[-ed明示]だったため、今回の一般化
    文言でこの条件は再検証する)。"""
    normal_attempts = phase_a["raw_conditions"]["cond5_6_full_sentence_no_context"]["attempts"]
    attempts = []
    for attempt in range(1, diag01.ATTEMPTS_PER_CONDITION + 1):
        print(f"[OPEN-107][Ending-Clarity Trial][cond4_full_sentence] Ending-Clarity attempt {attempt}")
        r = run_attempt("cond4_full_sentence", TARGET_SENTENCE, attempt, ENDING_CLARITY_STYLE_PREFIX, "ending_clarity")
        print(f"  -> status={r.get('status')} asr={r.get('asr_text')!r} "
              f"classification={r.get('audio_validation_classification')}")
        attempts.append(r)
    return {
        "input_text": TARGET_SENTENCE,
        "normal": {"source": "REUSED_FROM_TRIAL_01_PHASE_A", "reused_from_condition": "cond5_6_full_sentence_no_context",
                   "attempts": normal_attempts},
        "ending_clarity": {"source": "NEW", "attempts": attempts},
    }


def build_condition_5_full_sentence_with_context(phase_a: dict) -> dict:
    """条件5(完全な一文+周辺文脈、raw pipeline): Normalは前回Phase Aの
    cond7を再利用(2/3 PASS)。Ending-Clarityは新規3回実行する。"""
    normal_attempts = phase_a["raw_conditions"]["cond7_full_sentence_with_following_context"]["attempts"]
    attempts = []
    for attempt in range(1, diag01.ATTEMPTS_PER_CONDITION + 1):
        print(f"[OPEN-107][Ending-Clarity Trial][cond5_full_sentence_with_context] Ending-Clarity attempt {attempt}")
        r = run_attempt("cond5_full_sentence_with_context", PRODUCTION_IN_ONE_LINE_FULL_TEXT, attempt,
                         ENDING_CLARITY_STYLE_PREFIX, "ending_clarity")
        print(f"  -> status={r.get('status')} asr={r.get('asr_text')!r} "
              f"classification={r.get('audio_validation_classification')}")
        attempts.append(r)
    return {
        "input_text": PRODUCTION_IN_ONE_LINE_FULL_TEXT,
        "normal": {"source": "REUSED_FROM_TRIAL_01_PHASE_A", "reused_from_condition": "cond7_full_sentence_with_following_context",
                   "attempts": normal_attempts},
        "ending_clarity": {"source": "NEW", "attempts": attempts},
    }


PRODUCTION_EQUIVALENT_OUTER_REPEATS = 2


def build_condition_6_production_equivalent(phase_a: dict) -> dict:
    """条件6(Production実データ相当のsegment構成): Normalは前回Phase Aの
    cond9(実際のNo.18本番実行、Batch API + review_lock 3attempt cascade、
    3/3失敗)をそのまま引用する(同一内容の再実行は行わない)。
    Ending-Clarityは、実Production関数(news_tail_fix.
    generate_news_narration_wide_margin、disfluency_qa=True)をそのまま
    呼び出しつつ、そのプロセス内でのみp9a.ENGLISH_STYLE_PREFIXを一時的に
    Ending-Clarity版へmonkeypatchし、呼び出し後に必ず元へ戻す
    (ソースファイルへの恒久的な変更は一切行わない)。Production関数自体は
    内部で最大3回のASR検証retry cascadeを持つため、これを1セットとして
    2回(PRODUCTION_EQUIVALENT_OUTER_REPEATS)独立に実行する。"""
    normal_ref = phase_a["production_function_conditions"]["cond9_long_in_one_line_segment_reused_from_production"]

    outer_runs = []
    original_prefix = p9a.ENGLISH_STYLE_PREFIX
    for outer in range(1, PRODUCTION_EQUIVALENT_OUTER_REPEATS + 1):
        out_path = f"{NARRATION_DIR}/cond6_production_equivalent_ending_clarity_outer{outer}.wav"
        print(f"[OPEN-107][Ending-Clarity Trial][cond6_production_equivalent] "
              f"実Production関数(monkeypatch適用)outer run {outer}/{PRODUCTION_EQUIVALENT_OUTER_REPEATS}...")
        p9a.ENGLISH_STYLE_PREFIX = ENDING_CLARITY_STYLE_PREFIX
        try:
            t0 = time.time()
            with cl.logging_context("open107_ending_clarity_trial", "cond6_production_equivalent"), \
                 cl.segment_context(f"cond6_production_equivalent_outer{outer}"):
                result = news_tail_fix.generate_news_narration_wide_margin(
                    PRODUCTION_IN_ONE_LINE_FULL_TEXT, out_path, disfluency_qa=True)
            elapsed = round(time.time() - t0, 2)
        finally:
            p9a.ENGLISH_STYLE_PREFIX = original_prefix  # 恒久変更を残さないよう必ず復元

        asr_text = result.get("asr_text")
        outer_runs.append({
            "outer_attempt": outer, "result": result, "elapsed_seconds": elapsed,
            "audio_validation_classification": classify_opened_pronunciation(asr_text),
            "tts_instruction_used": ENDING_CLARITY_STYLE_PREFIX,
        })
        print(f"  -> status={result.get('status')} asr={asr_text!r} "
              f"classification={outer_runs[-1]['audio_validation_classification']}")
        with open(f"{OUT_DIR}/condition_6_partial.json", "w", encoding="utf-8") as f:
            json.dump(outer_runs, f, ensure_ascii=False, indent=2, default=str)

    return {
        "input_text": PRODUCTION_IN_ONE_LINE_FULL_TEXT,
        "normal": {"source": "REUSED_FROM_TRIAL_01_PHASE_A_COND9", "reused_from_condition":
                   "cond9_long_in_one_line_segment_reused_from_production", "reference": normal_ref},
        "ending_clarity": {"source": "NEW_VIA_MONKEYPATCHED_PRODUCTION_FUNCTION", "outer_runs": outer_runs,
                            "note": "p9a.ENGLISH_STYLE_PREFIXをこのTrial実行中のみ一時的に書き換え、"
                                     "呼び出し後に必ず元の値へ復元した。news_tail_fix.py等のソース"
                                     "ファイル自体は変更していない。"},
    }


def run_trial() -> dict:
    phase_a, phase_b = _load_reused("dummy")
    results = {
        "instruction_normal": NORMAL_STYLE_PREFIX,
        "instruction_ending_clarity": ENDING_CLARITY_STYLE_PREFIX,
        "conditions": {},
    }
    results["conditions"].update(build_condition_1_2_3(phase_a))
    with open(f"{OUT_DIR}/ending_clarity_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    results["conditions"]["cond4_full_sentence"] = build_condition_4_full_sentence(phase_a)
    with open(f"{OUT_DIR}/ending_clarity_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    results["conditions"]["cond5_full_sentence_with_context"] = build_condition_5_full_sentence_with_context(phase_a)
    with open(f"{OUT_DIR}/ending_clarity_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    results["conditions"]["cond6_production_equivalent"] = build_condition_6_production_equivalent(phase_a)
    with open(f"{OUT_DIR}/ending_clarity_trial_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    return results


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    run_trial()
    print("[OPEN-107][Ending-Clarity Trial] 完了。")
