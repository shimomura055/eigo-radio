# -*- coding: utf-8 -*-
# ER-010-NO9-A2-KEYPHRASE-AUDIO-ISSUES-103-104-17: A2のみのProduction
# Audio再実行(記事再生成なし、B1再生成なし)。既存の正式entry point
# (er009_n1_production_integration_01.run_audio_stage)からA2部分のみを
# 呼び出す(B1呼び出しを含む同関数をそのまま使うとRESOLVED済みB1の
# 23segmentへ不要なTTS/ASR再実行が発生してしまうため)。
import json
import time
import sys

import er005_cost_logger as cl
import er009_n1_production_integration_01 as prod

THEME_ID = prod.THEME_ID
OUT_DIR = prod.OUT_DIR


def run_a2_only_audio_stage() -> dict:
    import er003_v1_n3_01_tts_generate as tts_gen
    import er003_v1_n3_01_assemble as asm

    tts_gen.JAPANESE_TITLES.update({THEME_ID: prod.JAPANESE_TITLE_JA})
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    timing = {}

    prod.enable_sync_tts_mode()
    try:
        t1 = time.time()
        with cl.logging_context(THEME_ID, "tts_a2_sync"):
            a2_tts_summary = tts_gen.generate_a2_segments(theme)
        timing["tts_a2"] = round(time.time() - t1, 2)
    finally:
        prod.disable_sync_tts_mode()

    t3 = time.time()
    try:
        with cl.logging_context(THEME_ID, "assemble_a2"):
            a2_assemble_summary = asm.stage_assemble_a2(theme)
        assemble_error = None
    except RuntimeError as e:
        a2_assemble_summary = None
        assemble_error = str(e)
    timing["assemble_a2"] = round(time.time() - t3, 2)

    print(f"[{THEME_ID}] A2 Audio再実行完了。timing={timing}")
    print(f"  A2 TTS: {a2_tts_summary['segment_status']}")
    print(f"  A2 kp_status: {a2_tts_summary.get('kp_status')}")
    print(f"  A2 Assemble: {a2_assemble_summary}")
    if assemble_error:
        print(f"  A2 Assemble ERROR: {assemble_error}")
    return {"a2_tts": a2_tts_summary, "a2_assemble": a2_assemble_summary,
            "assemble_error": assemble_error, "timing": timing}


if __name__ == "__main__":
    cl.install(f"{OUT_DIR}/raw_usage_log.jsonl")
    result = run_a2_only_audio_stage()
    with open("er010_output/no9_a2_keyphrase_audio_issues_103_104_17/a2_only_rerun_result.json",
              "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
