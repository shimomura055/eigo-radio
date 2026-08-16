# ============================================================
# er003_v1_b1redesign_audio_fix.py
# ER-003-B1-REDESIGN-AUDIO-01: num_one〜five / preview / point_two 個別修正
# ============================================================
# num_one〜five: 既知の数詞→数字ASR正規化パターン(VOICE-01で確立済みの
# 数詞/数字等価判定を再利用)。
# preview: writerが生成したSupport textにカーブアポストロフィ(’)が
# 含まれており、ASR側の直立アポストロフィ(')と_extract_wordsの
# トークン化が食い違って誤ってFAILしていた。TTS入力のみアポストロフィを
# 正規化する(表示用テキストは変更しない)。
# point_two: 既知の"one-fifth"→ASR"1/5"分数表記正規化パターン(IRAN01
# B1 point_twoで確立済みのnormalize_fraction_wordsを再利用)。
#
# 実行方法:
#   .venv/Scripts/python.exe er003_v1_b1redesign_audio_fix.py

from __future__ import annotations

import json

import er003_v1_b1redesign_audio_generate as b1a
import er003_v1_b1redesign_audio_scaffold_generate as scaf
import er003_v1_iran01_b1_audio_fix as iran01_fix
import er003_v1_sing01_voice01_labels_fix as labels_fix

NARRATION_DIR = b1a.NARRATION_DIR
NUMBER_WORDS = {"num_one": "One.", "num_two": "Two.", "num_three": "Three.",
                "num_four": "Four.", "num_five": "Five."}


def main():
    results = {}

    for name, text in NUMBER_WORDS.items():
        print(f"[B1REDESIGN-FIX] {name}再生成(Charon、数詞/数字等価判定): {text!r}...")
        r = labels_fix.generate_label(text, f"{NARRATION_DIR}/{name}_charon.wav")
        results[name] = r
        print(f"[B1REDESIGN-FIX] {name}: status={r.get('status')}")

    with open(f"{scaf.OUT_DIR}/support_texts.json", encoding="utf-8") as f:
        support_texts = json.load(f)
    preview_text_normalized = support_texts["preview"].replace("’", "'")
    print(f"[B1REDESIGN-FIX] preview再生成(Charon、カーブアポストロフィ正規化)...")
    print(f"    表示用canonical: {support_texts['preview'][:40]!r}...")
    print(f"    TTS input(直立アポストロフィへ正規化): {preview_text_normalized[:40]!r}...")
    from er003_v1_sing01_voice01_generate import generate_charon_english
    r = generate_charon_english(preview_text_normalized, f"{NARRATION_DIR}/preview_charon.wav")
    results["preview"] = r
    print(f"[B1REDESIGN-FIX] preview: status={r.get('status')}")

    with open(f"{scaf.OUT_DIR}/audit/text_identity.json", encoding="utf-8") as f:
        parts = json.load(f)["parts"]
    print("[B1REDESIGN-FIX] point_two再生成(Aoede、分数正規化対応)...")
    r = iran01_fix.generate_point_two_wide_margin(parts["point_two_body"], f"{NARRATION_DIR}/point_two.wav")
    results["point_two"] = r
    print(f"[B1REDESIGN-FIX] point_two: status={r.get('status')}")

    with open(f"{scaf.OUT_DIR}/audit/audio_fix_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)

    with open(f"{scaf.OUT_DIR}/audit/segment_generation_results.json", encoding="utf-8") as f:
        all_results = json.load(f)
    for name, r in results.items():
        if r.get("status") == "OK":
            all_results[name] = r
    with open(f"{scaf.OUT_DIR}/audit/segment_generation_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    failed = [k for k, v in results.items() if v.get("status") != "OK"]
    print("完了。失敗:" if failed else "完了。全件成功。", failed if failed else "")


if __name__ == "__main__":
    main()
