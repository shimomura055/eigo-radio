# ============================================================
# er003_v1_iran01_a2_audio_fix.py
# ER-003-IRAN-A2-B1-01: A2 point_one/meaning_2/meaning_4 個別修正
# ============================================================
# point_one: 音声内容は正しいが、expected_substring "one-fifth" がASRの
# 分数正規化("1/5")と一致しなかっただけ。より安定した部分文字列で再検証。
# meaning_4: 同じ分数正規化("5分の1"→ASRは"1/5"と書き起こす)。音声内容は
# 正しいため、expected_substringのみ緩和する(本文テキストは変更しない、
# ADD03のBrent crude oil同種対応を踏襲)。
# meaning_2: japanese_gloss「～を…だと宣言する」の「～」「…」は文法上の
# プレースホルダーだが、TTSが記号をそのまま発話しようとして
# 「おおだ」「なになにをなにないだ」等の意味不明な音声になっていた
# (SING01 kp5「～」問題と同種)。TTS入力用テキストのみ自然な日本語
# 「何かを何かだと宣言する」に差し替える(japanese_gloss本体は変更しない)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_iran01_a2_audio_fix.py

from __future__ import annotations

import json

import er003_v1_crosslevel_audio_02_common as c
import er003_v1_iran01_a2_audio_generate as a2audio

OUT_DIR = a2audio.OUT_DIR
NARRATION_DIR = a2audio.NARRATION_DIR


def main():
    results = {}

    print("[IRAN01-A2-FIX] point_one 再検証(expected_substring変更)...")
    point_one_text = a2audio.A2_PARTS["point_one_body"]
    r = c.generate_english_segment_with_fallback(
        point_one_text, f"{NARRATION_DIR}/point_one.wav", "Iran and Oman", max_extra_chars=60)
    results["point_one"] = r
    print(f"[IRAN01-A2-FIX] point_one: status={r.get('status')}")

    print("[IRAN01-A2-FIX] meaning_4(5分の1)再検証(expected_substring緩和)...")
    r = c.generate_narration_snippet_verified_strict(
        "5分の1", "ja", f"{NARRATION_DIR}/meaning_4.wav", "1/5", max_attempts=6, max_extra_chars=40)
    results["meaning_4"] = r
    print(f"[IRAN01-A2-FIX] meaning_4: status={r.get('status')}")

    print("[IRAN01-A2-FIX] meaning_2(declare something to be)TTS入力を自然文へ差し替えて再生成...")
    r = c.generate_narration_snippet_verified_strict(
        "何かを何かだと宣言する", "ja", f"{NARRATION_DIR}/meaning_2.wav", "宣言する", max_attempts=6, max_extra_chars=40)
    results["meaning_2"] = r
    print(f"[IRAN01-A2-FIX] meaning_2: status={r.get('status')}")

    with open(f"{OUT_DIR}/audit/audio_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{OUT_DIR}/audit/text_segments_result.json", encoding="utf-8") as f:
        all_results = json.load(f)
    for name, r in results.items():
        if r.get("status") == "OK":
            all_results[name] = r
    with open(f"{OUT_DIR}/audit/text_segments_result.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
