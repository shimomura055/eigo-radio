# ============================================================
# er011_no18_connected_speech_reading_resolver_assemble_only_08.py
# ER-011-NO18-CONNECTED-SPEECH-READING-RESOLVER-PRODUCTION-WIRING-08
# ============================================================
# TTS Stage(er011_no18_connected_speech_reading_resolver_audio_stage_08.py
# の全segment run + er011_no18_connected_speech_reading_resolver_scoped_
# retry_08.pyのcomment_2/comment_3/comment_1 scoped retry)は完了済み。
# 既にOK/VALIDATED状態のsegmentを無駄に再生成しないよう、Assembly段階
# (Audio Validation Gate + timeline組み立て)だけを正式Production経路で
# 実行する。

from __future__ import annotations

import json

import er003_v1_n3_01_assemble as asm
import er011_no18_specfix_v2_production_run_01 as driver

THEME_ID = driver.THEME_ID
OUT_DIR = driver.OUT_DIR


def main():
    theme = {"theme_id": THEME_ID, "out_dir": OUT_DIR}
    b1_assemble_summary = asm.stage_assemble_b1(theme)
    print(f"[{THEME_ID}] B1 Assemble: {b1_assemble_summary}")
    a2_assemble_summary = asm.stage_assemble_a2(theme)
    print(f"[{THEME_ID}] A2 Assemble: {a2_assemble_summary}")
    with open(f"{OUT_DIR}/assemble_result_wiring08.json", "w", encoding="utf-8") as f:
        json.dump({"b1_assemble": b1_assemble_summary, "a2_assemble": a2_assemble_summary},
                   f, ensure_ascii=False, indent=2, default=str)


if __name__ == "__main__":
    main()
