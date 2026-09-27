# ============================================================
# er022_tts_gemini_3_8_flash_lite_ab_trial_01.py
# TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01
# ============================================================
# 性質: Trial限定(最大到達Status=VALIDATED、Production採用しない、
# Production挙動は無変更)。
#
# 目的: 既存完成記事「AIが採用を選ぶとき」Standard(A2)版
# (er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2/、
# PRODUCTION_WIRED済みcanonical)について、現行Production TTS
# (model=gemini-2.5-pro-preview-tts[英語]/gemini-3.1-flash-tts-preview[日本語])と
# Gemini 3.8 Flash-Lite TTS(model="gemini-3.8-flash-lite-tts"、
# client.models.list()の実結果から確認済み)を、英語ナレーション17
# segment(Key Phraseは今回のTrial対象外、スコープ縮小理由は
# REPORT §0参照)について純粋A/B比較する。
#
# 方式: 本文segmentの生成には、既存Production関数(retry/fallback/
# ASR validation/repetition QA/disfluency QA/6% slowdown post-process/
# review lock)を一切変更せずそのまま呼び出す。モデルIDだけを
# 差し替えるため、呼び出し直前にer003_b1_p9a_audio.ENGLISH_MODEL_NAME/
# JAPANESE_MODEL_NAMEをこのプロセス内でのみ一時的にmonkeypatchし
# (with文で必ず復元、Productionファイル自体は一切変更しない)、既存
# 関数群がこれらの属性をimport時ではなく呼び出し時に参照している
# ことを事前に確認済み(REPORT §3参照)。
#
# topic_intro(Charon)のみ、ER-002凍結仕様(er002_common.MODEL_NAME、
# 「変更しない」と明記)を経由する専用関数(voice01.generate_charon_
# english)を使っているため、上記monkeypatchの対象に含めない。代わりに
# 本ファイル内で、既存の共有primitive(common/p3u/p4c/routing/p7a)だけを
# 使った独立の最小生成関数を用意する(凍結仕様ファイルは一切触れない)。
#
# 出力先: er022_output/tts_gemini_3_8_flash_lite_ab_trial_01/ (専用、
# 既存記事artifactは無変更)。
# ============================================================
from __future__ import annotations

import contextlib
import json
import os
import time

import numpy as np

import er002_common as common
import er003_b1_p3u_audio as p3u
import er003_b1_p4c_audio as p4c
import er003_b1_p7a_audio as p7a
import er003_b1_p9a_audio as p9a
import er003_v1_n3_01_tts_generate as n3_tts
import er005_cost_logger as cl
import er006_asr_provider_routing_01 as routing
import er012_b_family_voices_a2_production_01 as a2prod
import er012_b_family_voices_production_01 as b1prod
import er012_b_voices_3v_a2_user_test_01 as v3

MODEL_B = "gemini-3.8-flash-lite-tts"
MODEL_A_ENGLISH = p9a.ENGLISH_MODEL_NAME  # "gemini-2.5-pro-preview-tts"(現行、参照用のみ)
MODEL_A_JAPANESE = p9a.JAPANESE_MODEL_NAME  # "gemini-3.1-flash-tts-preview"(現行、参照用のみ)

SOURCE_A_DIR = "er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/kp_fix_01/a2"
OUT_DIR = "er022_output/tts_gemini_3_8_flash_lite_ab_trial_01"
B_DIR = f"{OUT_DIR}/b"
NARR_DIR = f"{B_DIR}/narration"
AUDIT_DIR = f"{B_DIR}/audit"
COST_LOG_PATH = f"{AUDIT_DIR}/raw_usage_log.jsonl"

VOICE_A_3V, VOICE_B_3V, VOICE_C_3V = v3.VOICE_A_3V, v3.VOICE_B_3V, v3.VOICE_C_3V
JAPANESE_TITLE_3V = v3.JAPANESE_TITLE_3V
EXTRA_SEGMENT_NAME = b1prod.EXTRA_SEGMENT_NAME  # "tension_reflection"

# 本Trialで扱う17segment(既存Production driverのWEB_SEGMENT_NAMES+
# tension_reflectionと同一集合。Key Phrase[kp1-5 en/ja]は対象外、
# 理由はREPORT参照)。
SEGMENT_ORDER = [
    "topic_intro", "japanese_title", "preview", "comment_1",
    "full_story_part1", "full_story_part2", "comment_2",
    "point_one_heading", "point_one", "point_two_heading", "point_two",
    "point_three_heading", "point_three", "comment_3",
    EXTRA_SEGMENT_NAME, "comment_4", "in_one_line",
]


@contextlib.contextmanager
def model_b_override():
    """er003_b1_p9a_audio.ENGLISH_MODEL_NAME/JAPANESE_MODEL_NAMEを、この
    with블록の間だけMODEL_Bへ差し替える(プロセス内monkeypatch、ファイル
    自体は無変更)。既存Production関数はこれらの属性をp9a.XXX_MODEL_NAME
    という形で呼び出し時に参照しているため(モジュールimport時の値コピー
    ではない、er003_v1_repro01_main_generate.py/er012_b_family_voices_
    production_01.py本文で確認済み)、この差し替えだけでモデルを
    切り替えられる。"""
    orig_en, orig_ja = p9a.ENGLISH_MODEL_NAME, p9a.JAPANESE_MODEL_NAME
    p9a.ENGLISH_MODEL_NAME = MODEL_B
    p9a.JAPANESE_MODEL_NAME = MODEL_B
    try:
        yield
    finally:
        p9a.ENGLISH_MODEL_NAME = orig_en
        p9a.JAPANESE_MODEL_NAME = orig_ja


def generate_topic_intro_with_model(text: str, out_path: str, model_name: str,
                                     voice_name: str = "Charon", max_attempts: int = 3) -> dict:
    """topic_intro専用の独立実装。ER-002凍結仕様(common.MODEL_NAME)は
    一切参照・変更しない。既存の共有primitive(p4c.build_tts_prompt/
    p9a.ENGLISH_STYLE_PREFIX/common._call_tts_with_retry/
    p3u.trim_english_keyword_silence/routing.transcribe)だけを使う。"""
    prompt = p4c.build_tts_prompt(text, p9a.ENGLISH_STYLE_PREFIX)
    expected_substring = n3_tts.first_words(text, 3)
    attempts_log = []
    for attempt in range(1, max_attempts + 1):
        call_fn = p7a.make_tts_call_fn_for_model(model_name, voice_name)
        t0 = time.time()
        pcm, retries, ok, err = common._call_tts_with_retry(call_fn, prompt, max_retry=0, sleep_fn=None)
        elapsed = round(time.time() - t0, 3)
        if not ok:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": str(err), "elapsed_seconds": elapsed})
            continue
        samples_raw = common.pcm_bytes_to_float_mono(pcm)
        trimmed, trim_info = p3u.trim_english_keyword_silence(
            samples_raw, common.SAMPLE_RATE, safety_margin_seconds=p3u.EN_TRIM_SAFETY_MARGIN_SECONDS)
        if trimmed is None:
            attempts_log.append({"attempt": attempt, "status": "STOPPED", "reason": "発話区間を検出できませんでした",
                                  "elapsed_seconds": elapsed})
            continue
        common.write_wav_float(out_path, trimmed, common.SAMPLE_RATE, 1)
        asr_text, asr_err = routing.transcribe(out_path, "en-US")
        verified = asr_text is not None and expected_substring.lower() in asr_text.lower()
        metrics = common.measure_metrics(trimmed, common.SAMPLE_RATE)
        attempts_log.append({
            "attempt": attempt, "status": "OK", "asr_text": asr_text, "asr_error": asr_err,
            "verified": verified, "elapsed_seconds": elapsed,
            "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
        })
        if verified:
            return {
                "status": "OK", "text": text, "language": "en", "path": out_path,
                "model": model_name, "voice": voice_name, "call_count": attempt, "retry_count": attempt - 1,
                "duration_seconds": round(len(trimmed) / common.SAMPLE_RATE, 4),
                "trim_info": trim_info, "clipping_detected": metrics["clipping_detected"],
                "asr_verified": True, "asr_text": asr_text, "attempts_log": attempts_log,
                "instruction_type": "english_style_prefix",
            }
    return {"status": "ASR_VALIDATION_UNCERTAIN", "attempts_log": attempts_log, "text": text,
            "model": model_name, "voice": voice_name, "path": out_path}


def timed_call(name: str, fn, *args, **kwargs) -> tuple[dict, float]:
    t0 = time.time()
    with cl.segment_context(name):
        r = fn(*args, **kwargs)
    elapsed = round(time.time() - t0, 3)
    return r, elapsed


def run_generation() -> dict:
    os.makedirs(NARR_DIR, exist_ok=True)
    os.makedirs(AUDIT_DIR, exist_ok=True)
    os.environ["TTS_EXECUTION_MODE"] = "STANDARD"
    cl.install(COST_LOG_PATH)

    parts = json.load(open(f"{SOURCE_A_DIR}/parts.json", encoding="utf-8"))
    support = json.load(open(f"{SOURCE_A_DIR}/a2_support_texts.json", encoding="utf-8"))

    results: dict = {}
    timing: dict = {}

    # topic_intro(Charon、凍結仕様[common.MODEL_NAME]を経由しないため
    # monkeypatchブロックの外で個別実装を使う)
    topic_text = f"Today's topic is {parts['title']}."
    tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(topic_text))
    r, el = timed_call("topic_intro", generate_topic_intro_with_model,
                        tts_input, f"{NARR_DIR}/topic_intro.wav", MODEL_B, "Charon")
    r["canonical_text"] = topic_text
    results["topic_intro"] = r
    timing["topic_intro"] = el

    with model_b_override():
        r, el = timed_call("japanese_title", n3_tts.generate_a2_japanese_with_reading_safety,
                            JAPANESE_TITLE_3V, f"{NARR_DIR}/japanese_title.wav",
                            n3_tts.expected_substring_ja(JAPANESE_TITLE_3V), max_extra_chars=30)
        r["canonical_text"] = JAPANESE_TITLE_3V
        results["japanese_title"] = r
        timing["japanese_title"] = el

        for name in ("preview", "comment_1", "comment_2", "comment_3", "comment_4"):
            text = support[name]
            r, el = timed_call(name, n3_tts.generate_a2_japanese_with_reading_safety,
                                text, f"{NARR_DIR}/{name}.wav", n3_tts.expected_substring_ja(text))
            r["canonical_text"] = text
            results[name] = r
            timing[name] = el

        for name in ("point_one_heading", "point_two_heading", "point_three_heading"):
            text = parts[name]
            tts_input = n3_tts.tts_safe_number_words_en(n3_tts.tts_safe_en(text))
            r, el = timed_call(name, n3_tts.generate_a2_segment_with_slowdown,
                                tts_input, f"{NARR_DIR}/{name}.wav", n3_tts.first_words(text, 3),
                                max_extra_chars=20, style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                                disfluency_qa=True)
            r["canonical_text"] = text
            results[name] = r
            timing[name] = el

        for name, text, voice_name in (
            ("point_one", parts["point_one_body"], VOICE_A_3V),
            ("point_two", parts["point_two_body"], VOICE_B_3V),
            ("point_three", parts["point_three_body"], VOICE_C_3V),
        ):
            r, el = timed_call(name, a2prod.generate_voice_body_wide_margin_with_a2_slowdown,
                                name, n3_tts.tts_safe_news_en(text), f"{NARR_DIR}/{name}.wav", voice_name)
            r["canonical_text"] = text
            results[name] = r
            timing[name] = el

        for name, text in (
            ("full_story_part1", parts["part1"]), ("full_story_part2", parts["part2"]),
            (EXTRA_SEGMENT_NAME, parts["tension_body"]), ("in_one_line", parts["in_one_line"]),
        ):
            tts_input = n3_tts.tts_safe_news_en(text)
            r, el = timed_call(name, n3_tts.generate_a2_segment_with_slowdown,
                                tts_input, f"{NARR_DIR}/{name}.wav", n3_tts.first_words(text),
                                style_prefix_override=n3_tts.A2_ENGLISH_STYLE_PREFIX_SLOWER,
                                disfluency_qa=(name == "in_one_line"),
                                enable_connected_speech_equivalence_layer=(name in ("full_story_part1", "full_story_part2")),
                                enable_repetition_qa=(name in ("full_story_part1", "full_story_part2")))
            r["canonical_text"] = text
            results[name] = r
            timing[name] = el

    out = {"model_b": MODEL_B, "model_a_english": MODEL_A_ENGLISH, "model_a_japanese": MODEL_A_JAPANESE,
           "segments": results, "timing_seconds": timing}
    with open(f"{AUDIT_DIR}/tts_generation_results_b.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


if __name__ == "__main__":
    result = run_generation()
    ok = sum(1 for s in result["segments"].values() if s.get("status") == "OK")
    total = len(result["segments"])
    print(f"[TTS-GEMINI-3.8-FLASH-LITE-AB-TRIAL-01] 完了: OK={ok}/{total}")
    for name, s in result["segments"].items():
        print(f"  {name}: status={s.get('status')} retry={s.get('retry_count')} "
              f"duration={s.get('duration_seconds')} elapsed={result['timing_seconds'].get(name)}")
