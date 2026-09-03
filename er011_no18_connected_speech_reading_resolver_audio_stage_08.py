# ============================================================
# er011_no18_connected_speech_reading_resolver_audio_stage_08.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# ============================================================
# No.18(pool_n18_notifications_specfix_v2)のA2/B1 Audio Stageを、
# OPEN-107撤去+B1 Connected Speech Validator+A2 Reading ResolverをProduction
# 配線した後の正式Production経路で通し直す(§7)。既存の確定済み記事・
# Support・Key Phraseは再利用し(§6、Writer再生成はしない)、Audio
# Validation(TTS/ASR/Validator/retry/Gate/Assembly)だけを正式経路で
# 再実行する。既存完成segmentの単純コピーはしない(全segment再生成)。

from __future__ import annotations

import json
import time

import er003_v1_n3_01_assemble as asm
import er003_v1_n3_01_tts_generate as tts_gen
import er005_cost_logger as cl
import er011_no18_discovery_why_full_production_run_01 as no18_orig
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
JAPANESE_TITLE_JA = driver.JAPANESE_TITLE_JA

enable_sync_tts_mode = no18_orig.enable_sync_tts_mode
disable_sync_tts_mode = no18_orig.disable_sync_tts_mode


def run_audio_stage() -> dict:
    tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    enable_sync_tts_mode()
    try:
        t0 = time.time()
        with cl.logging_context(THEME_ID, "tts_b1_wiring08_sync"):
            b1_tts_summary = tts_gen.generate_b1_segments(theme)
        timing["tts_b1"] = round(time.time() - t0, 2)

        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_wiring08_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2"] = round(time.time() - t1, 2)
    finally:
        disable_sync_tts_mode()

    t2 = time.time()
    with cl.logging_context(THEME_ID, "assemble_b1_wiring08"):
        b1_assemble_summary = asm.stage_assemble_b1(theme)
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    with cl.logging_context(THEME_ID, "assemble_a2_wiring08"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing_wiring08.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] Audio完了(同期TTS、Connected Speech Validator+Reading Resolver配線後)。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
            "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log_wiring08_audio.jsonl")
    run_audio_stage()
