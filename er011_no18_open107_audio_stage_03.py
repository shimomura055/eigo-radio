# ============================================================
# er011_no18_open107_audio_stage_03.py
# ER-011-NO18-OPEN107-PRODUCTION-WIRING-AND-FINAL-AUDIO-03
# ============================================================
# No.18(pool_n18_notifications_specfix_v2)のA2/B1 Audio Stageを正式
# Production経路で実行する。er011_no18_discovery_why_full_production_run_01.
# run_audio_stage()と同じ構造(同期TTS切替 -> B1/A2 TTS -> B1/A2 Assembly)を
# 再利用し、THEME_ID/OUT_DIRだけをspecfix_v2版へ差し替える(パイプライン自体は
# 変更しない)。B1のFull Story/Point本文/In One Line生成には、
# er011_ending_clarity_fallback_01経由でEnding-Clarity fallbackが今回配線
# 済み(er003_v1_n3_01_tts_generate.generate_b1_segments内)。

from __future__ import annotations

import json
import time

import er005_cost_logger as cl
import er011_no18_discovery_why_full_production_run_01 as no18_orig
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR
JAPANESE_TITLE_JA = driver.JAPANESE_TITLE_JA

enable_sync_tts_mode = no18_orig.enable_sync_tts_mode
disable_sync_tts_mode = no18_orig.disable_sync_tts_mode


def run_audio_stage() -> dict:
    import er003_v1_n3_01_assemble as asm
    import er003_v1_n3_01_tts_generate as tts_gen

    tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    enable_sync_tts_mode()
    try:
        t0 = time.time()
        with cl.logging_context(THEME_ID, "tts_b1_sync"):
            b1_tts_summary = tts_gen.generate_b1_segments(theme)
        timing["tts_b1"] = round(time.time() - t0, 2)

        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2"] = round(time.time() - t1, 2)
    finally:
        disable_sync_tts_mode()

    t2 = time.time()
    with cl.logging_context(THEME_ID, "assemble_b1"):
        b1_assemble_summary = asm.stage_assemble_b1(theme)
    timing["assemble_b1"] = round(time.time() - t2, 2)

    t3 = time.time()
    with cl.logging_context(THEME_ID, "assemble_a2"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    with open(f"{OUT_DIR}/audio_timing_open107_03.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] Audio完了(同期TTS)。timing={timing}")
    print(f"  B1 TTS: {b1_tts_summary['segment_status']}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  B1 Assemble: {b1_assemble_summary}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"b1_tts": b1_tts_summary, "a2_tts": a2_tts_summary,
            "b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log_open107_audio.jsonl")
    run_audio_stage()
