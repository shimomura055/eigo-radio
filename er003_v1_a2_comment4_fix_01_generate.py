# ============================================================
# er003_v1_a2_comment4_fix_01_generate.py
# ER-003-A2-COMMENT4-INONELINE-FIX-01: A2 Comment 4文言修正
# ============================================================
# Comment 4末尾の「一文で確認しましょう」が、実際は2文であるIn One Line
# の内容と一致していなかったため、文数を断定しない文言へ差し替える。
# canonical textはsupport_texts_ja.json側で既に更新済み(このscriptは
# TTS生成のみを担当)。Comment 4以外のsegmentは一切変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_a2_comment4_fix_01_generate.py

from __future__ import annotations

import json
import os

import er003_audio_tts_asr_safety as safety
import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2gen

OUT_DIR = a2gen.OUT_DIR
NARRATION_DIR = f"{OUT_DIR}/narration"

NEW_COMMENT_4_TEXT = a2gen.A2_SUPPORT_JA["comment_4"]
EXPECTED_SUBSTRING = "まとめて確認"


def main():
    os.makedirs(NARRATION_DIR, exist_ok=True)
    os.makedirs(f"{OUT_DIR}/audit", exist_ok=True)

    tts_input = safety.to_tts_safe_japanese_fraction_reading(NEW_COMMENT_4_TEXT)
    print(f"[A2-COMMENT4-FIX] canonical={NEW_COMMENT_4_TEXT!r}")
    print(f"[A2-COMMENT4-FIX] tts_input={tts_input!r} (changed={tts_input != NEW_COMMENT_4_TEXT})")

    out_path = f"{NARRATION_DIR}/comment_4.wav"
    r = c.generate_narration_snippet_verified_strict(
        tts_input, "ja", out_path, EXPECTED_SUBSTRING, max_attempts=6, max_extra_chars=40)
    r["canonical_text"] = NEW_COMMENT_4_TEXT
    r["tts_input_text_after_reading_safety"] = tts_input
    r["reading_safety_changed_text"] = (tts_input != NEW_COMMENT_4_TEXT)
    print("[A2-COMMENT4-FIX] status:", r.get("status"))

    with open(f"{OUT_DIR}/audit/comment4_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2, default=str)

    print("[A2-COMMENT4-FIX] 完了。")


if __name__ == "__main__":
    main()
