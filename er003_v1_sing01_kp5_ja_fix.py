# ============================================================
# er003_v1_sing01_kp5_ja_fix.py
# ER-003-B1-NOVEL-AUDIO-01: Key Phrase 5 日本語meaning 個別再生成
# ============================================================
# japanese_gloss「～の可能性が高いと見る」の先頭「～」は、書き言葉の
# プレースホルダー記号であり発話対象ではない(TTSが省略/ASRが認識しない
# ため、substring検証が毎回不合格になっていた)。OPEN-28と同種の、
# ナレーション用テキストのみの個別対応。Canonicalization正式出力
# (keywords_canonicalized.json)自体は変更しない。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_sing01_kp5_ja_fix.py

from __future__ import annotations

import json

import er003_v1_repro01_main_generate as repro01

OUT_DIR = "er003_output/novel_audio_01/SING01"
NARRATION_DIR = f"{OUT_DIR}/narration"


def main():
    ja_gloss = "～の可能性が高いと見る"
    ja_tts_text = ja_gloss.lstrip("～~・")  # TTS入力・ASR期待値のみ、先頭のプレースホルダー記号を除去
    print(f"[KP5-JA-FIX] TTS入力: {ja_tts_text!r}(表示用japanese_glossは無変更: {ja_gloss!r})")

    ja_path = f"{NARRATION_DIR}/kp5_ja.wav"
    result = repro01.generate_narration_snippet_verified_strict(
        ja_tts_text, "ja", ja_path, ja_tts_text[:4])
    print(f"[KP5-JA-FIX] status={result.get('status')}")

    with open(f"{OUT_DIR}/audit/kp5_ja_fix_result.json", "w", encoding="utf-8") as f:
        json.dump({"original_japanese_gloss": ja_gloss, "tts_text_used": ja_tts_text, "result": result},
                   f, ensure_ascii=False, indent=2, default=str)

    if result.get("status") == "OK":
        with open("er003_output/novel_audio_01/SING01/audit/key_phrase_generation_results.json",
                   encoding="utf-8") as f:
            all_results = json.load(f)
        all_results["5"]["japanese"] = result
        all_results["5"]["japanese"]["tts_text_override"] = ja_tts_text
        with open("er003_output/novel_audio_01/SING01/audit/key_phrase_generation_results.json",
                   "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
        print("[KP5-JA-FIX] key_phrase_generation_results.json 更新済み")


if __name__ == "__main__":
    main()
