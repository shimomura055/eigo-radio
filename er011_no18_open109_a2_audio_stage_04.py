# ============================================================
# er011_no18_open109_a2_audio_stage_04.py
# ER-011-NO18-OPEN109-110-FINAL-CLOSEOUT-04
# ============================================================
# OPEN-109(A2記事のLedger精密化反映)完了後、A2のみのAudio Stage(同期TTS)
# を正式Production経路で実行する。新article.mdは旧article.mdと大きく異なる
# ため(Writer再生成は非決定的、タイトル・構成とも変化)、旧A2完成音声は
# 一切流用しない(全segment再生成)。Master Audio Store(Welcome/Outro/Key
# Phrase英語Component等、canonical text hashキー)による既存の安全な再利用
# 機構はそのまま働く(無条件流用ではなく、内容一致時のみ機械的に再利用される
# 既存仕様、ここでの変更なし)。B1側は今回対象外(comment_2/3のscoped retry
# と同時並行のため、b1b配下のファイルには一切書き込まない)。

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


def run_a2_audio_stage() -> dict:
    tts_gen.JAPANESE_TITLES.update({THEME_ID: JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    enable_sync_tts_mode()
    try:
        t0 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_open109_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2"] = round(time.time() - t0, 2)
    finally:
        disable_sync_tts_mode()

    t1 = time.time()
    with cl.logging_context(THEME_ID, "assemble_a2_open109"):
        a2_assemble_summary = asm.stage_assemble_a2(theme)
    timing["assemble_a2"] = round(time.time() - t1, 2)

    with open(f"{OUT_DIR}/audio_timing_open109_04.json", "w", encoding="utf-8") as f:
        json.dump(timing, f, ensure_ascii=False, indent=2)
    print(f"[{THEME_ID}] A2 Audio完了(同期TTS、OPEN-109 Ledger精密化後article)。timing={timing}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    return {"a2_tts": a2_tts_summary, "a2_assemble": a2_assemble_summary, "timing": timing}


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log_open109_a2_audio.jsonl")
    run_a2_audio_stage()
